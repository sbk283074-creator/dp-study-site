#!/usr/bin/env python3
"""Audit content depth of every page in the site.

`wc -w` is WRONG for this site: Chinese pages have no spaces, so CJK text
is undercounted by an order of magnitude. This script counts:
  - English/Latin words  -> regex [A-Za-z][A-Za-z''-]+
  - CJK characters       -> regex [\\u4e00-\\u9fff]
and reports `score = words + cjk`. Markup, <script> and <style> are stripped.

Usage:
    python3 tools/audit_depth.py                # all pages, sorted thin-first
    python3 tools/audit_depth.py cs english     # only some subject dirs
    python3 tools/audit_depth.py --min 2500     # only flag pages under a floor
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {
    "tools", "assets", "_figures_export", "node_modules", "qbank",
    "dp learning", ".git", ".workbuddy-ai", "__pycache__", "figures",
}
SKIP_FILES = {"search-index.js"}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\u2019-]+")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


class TextExtractor(HTMLParser):
    """Collect visible text, skipping script/style content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def measure(path: Path) -> tuple[int, int, int]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    p = TextExtractor()
    p.feed(raw)
    text = "".join(p.parts)
    words = len(WORD_RE.findall(text))
    cjk = len(CJK_RE.findall(text))
    return words, cjk, words + cjk


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    floor = 0
    if "--min" in sys.argv:
        i = sys.argv.index("--min")
        if i + 1 < len(sys.argv):
            floor = int(sys.argv[i + 1])

    rows = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if set(rel.parts[:-1]) & SKIP_DIRS:
            continue
        if rel.name in SKIP_FILES:
            continue
        if args and rel.parts[0] not in args:
            continue
        words, cjk, score = measure(path)
        rows.append((score, words, cjk, str(rel)))

    rows.sort()
    width = max(len(r[3]) for r in rows)
    print(f"{'score':>7} {'words':>6} {'cjk':>6}  page")
    print("-" * (width + 26))
    flagged = 0
    for score, words, cjk, rel in rows:
        mark = " "
        if score < floor:
            mark = "!"
            flagged += 1
        print(f"{mark}{score:>6} {words:>6} {cjk:>6}  {rel}")
    print("-" * (width + 26))
    print(f"{len(rows)} pages   total score {sum(r[0] for r in rows):,}")
    if floor:
        print(f"{flagged} page(s) below the {floor} floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
