#!/usr/bin/env python3
"""Repair the two mechanical faults that LaTeX in JSON keeps causing.

    python3 tools/fix_json.py               # repair every data/*/*.json in place
    python3 tools/fix_json.py --dry-run     # report only

1. Doubles any backslash that does not start a valid JSON escape. LaTeX is full
   of `\\,` (thin space), `\\times`, `\\dfrac` — a single backslash is not a
   legal JSON escape for `,`, so the file fails to parse. This is the single
   most common reason a freshly written batch will not load.
2. Replaces HTML entities (`&ndash;`, `&mdash;`, `&lt;` …) with the literal
   Unicode character. build.py escapes `&`, so an entity renders as the visible
   text "&amp;ndash;" on the site.

Neither change alters rendered content: after doubling, `\\,` is again `\\,`
when parsed, and an en dash is an en dash either way.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

VALID_AFTER_BACKSLASH = set('"\\/bfnrtu')
ENTITY = re.compile(r"&([a-zA-Z]{2,10}|#\d{1,5}|#x[0-9a-fA-F]{1,5});")
NAMED = {
    "ndash": "\u2013", "mdash": "\u2014", "minus": "\u2212", "times": "\u00d7",
    "divide": "\u00f7", "lt": "<", "gt": ">", "amp": "&", "quot": '"',
    "apos": "'", "nbsp": " ", "deg": "\u00b0", "plusmn": "\u00b1",
    "alpha": "\u03b1", "beta": "\u03b2", "pi": "\u03c0", "theta": "\u03b8",
    "lambda": "\u03bb", "mu": "\u03bc", "sigma": "\u03c3", "omega": "\u03a9",
    "Delta": "\u0394", "Sigma": "\u03a3", "Omega": "\u03a9",
    "hellip": "\u2026", "prime": "\u2032", "Prime": "\u2033",
    "le": "\u2264", "ge": "\u2265", "ne": "\u2260", "approx": "\u2248",
    "sim": "\u223c", "infin": "\u221e", "sdot": "\u22c5",
    "euro": "\u20ac", "pound": "\u00a3", "yen": "\u00a5", "copy": "\u00a9",
}


def fix_escapes(s):
    out, i, n = [], 0, 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            if s[i + 1] in VALID_AFTER_BACKSLASH:
                out.append(s[i:i + 2])
                i += 2
                continue
            out.append("\\\\")
            n += 1
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out), n


def fix_entities(s):
    def repl(m):
        body = m.group(1)
        if body.startswith("#x"):
            return chr(int(body[2:], 16))
        if body.startswith("#"):
            return chr(int(body[1:]))
        return NAMED.get(body, m.group(0))
    s2 = ENTITY.sub(repl, s)
    return s2, len(ENTITY.findall(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    bad, changed = 0, 0
    for p in sorted(DATA.glob("*/*.json")):
        if p.name.startswith("_"):
            continue
        raw = p.read_text(encoding="utf-8")
        try:
            json.loads(raw)
        except Exception:
            bad += 1

        s, n_esc = fix_escapes(raw)
        s, n_ent = fix_entities(s)
        try:
            json.loads(s)
        except Exception as e:
            print("FAIL  %s still unparseable after repair: %s" % (p, e))
            bad += 1
            continue

        if n_esc or n_ent:
            changed += 1
            print("%s  %s  (+%d escapes, %d entities)" %
                  ("would fix" if args.dry_run else "fixed", p, n_esc, n_ent))
            if not args.dry_run:
                p.write_text(s, encoding="utf-8")
        else:
            print("clean  %s" % p)

    print("\n%d file(s) repaired, %d unparseable." % (changed, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
