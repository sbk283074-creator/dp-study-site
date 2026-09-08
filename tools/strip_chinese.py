#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove all Chinese characters from the site's non-Chinese pages.

Rule: no Chinese characters anywhere on the site except inside the chinese/
section.  This script rewrites every `callout--vocab` block in every other
HTML file so that glossary entries become English-only, keeping any English
parentheticals that lived inside the original Chinese glosses (e.g. the
"vertical / horizontal" note attached to *asymptote*).

Run it once after a content sweep; it is idempotent.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Walk past everything that is not part of the rendered site, including the
# moved-in source platform under dp learning/ and its node_modules.
SKIP_DIR_NAMES = {
    "chinese",        # allowed to keep Chinese
    "assets",         # CSS / JS — no Chinese here
    ".workbuddy-ai",  # local memory
    "dp learning",    # the source platform the user moved in
    "node_modules",
    ".git",
}

CJK = re.compile(r"[\u4e00-\u9fff]")
# Drop CJK symbols/punctuation (U+3000-303F) and halfwidth/fullwidth forms
# (U+FF00-FFEF), plus the punctuation characters that show up as "glue"
# inside the Chinese glosses.
FW_DROP = re.compile(
    "["
    "\u3000-\u303f"          # CJK symbols & punctuation (、 。 「 」 etc)
    "\uff00-\uffef"          # fullwidth forms (／ ， ： ； （ ） ！ ？ etc)
    "\u2014\u2026\u00b7"     # em-dash, ellipsis, middot (used as glue)
    "]"
)

CALLOT = re.compile(
    r'(<div class="callout callout--vocab">\s*'
    r'<span class="callout__label">[^<]*</span>\s*'
    r"<p>)(.*?)(</p>\s*</div>)",
    re.DOTALL,
)

# Stricter CJK-only strip used as a safety net for prose, tables, quote blocks
# and other callouts that live OUTSIDE callout--vocab.  Keeps ordinary English
# punctuation (em-dash, ellipsis, middot) intact.
RESIDUAL_FW = re.compile(r"[\u3000-\u303f\uff00-\uffef]")


def clean_gloss(s: str) -> str:
    """Strip CJK + fullwidth glue from one gloss; keep English words."""
    s = CJK.sub("", s)
    s = FW_DROP.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def transform_paragraph(p: str) -> str:
    # 1) Chinese semicolon and middot -> English
    p = p.replace("\uff1b", "; ").replace("\u00b7", ";")
    # 2) " — gloss" up to the next ";" or "<" (or end of buffer)
    def repl(match):
        cleaned = clean_gloss(match.group(1))
        return " \u2014 " + cleaned if cleaned else ""
    p = re.sub(r" \u2014 ([^<;]*?)(?=; |<|$)", repl, p)
    # 3) safety net: anything still CJK / fullwidth must go
    p = CJK.sub("", p)
    p = FW_DROP.sub("", p)
    # 4) collapse empty separators left behind
    p = re.sub(r";\s*;\s*", ";", p)
    p = re.sub(r"(^|[\s]);\s*", r"\1", p)
    p = re.sub(r";\s*(?=<)", "", p)
    p = re.sub(r" {2,}", " ", p)
    return p


def process_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()
    new = CALLOT.sub(lambda m: m.group(1) + transform_paragraph(m.group(2)) + m.group(3), html)
    if new != html:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
        return True
    return False


def strip_residual_file(path: str) -> bool:
    """Second pass: any non-chinese HTML still containing CJK after the
    vocab callout has been cleaned gets a global character-level strip.

    Removes CJK ideographs and fullwidth punctuation, leaves em-dashes and
    other ASCII punctuation alone, and collapses stray double spaces.
    """
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()
    if not (CJK.search(html) or RESIDUAL_FW.search(html)):
        return False
    new = CJK.sub("", html)
    new = RESIDUAL_FW.sub("", new)
    new = re.sub(r" {2,}", " ", new)
    if new != html:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
        return True
    return False


def find_residual_Chinese():
    """List non-chinese HTML files that still contain CJK after processing."""
    bad = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                txt = fh.read()
            if CJK.search(txt):
                bad.append(p)
    return bad


def main():
    vocab_changed = []
    residual_changed = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(root, f)
            if process_file(p):
                vocab_changed.append(os.path.relpath(p, ROOT))
            if strip_residual_file(p):
                residual_changed.append(os.path.relpath(p, ROOT))

    print("vocab callouts cleaned: {}".format(len(vocab_changed)))
    print("residual CJK stripped:  {}".format(len(residual_changed)))
    for p in residual_changed:
        print("  " + p)

    residual = find_residual_Chinese()
    if residual:
        print("\nWARNING: {} non-chinese HTML files still contain CJK:".format(len(residual)))
        for p in residual:
            print("  " + os.path.relpath(p, ROOT))
        sys.exit(1)
    else:
        print("\nno residual CJK outside chinese/ \u2713")


if __name__ == "__main__":
    main()
