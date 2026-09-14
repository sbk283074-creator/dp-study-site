#!/usr/bin/env python3
"""Normalise the `topic` label vocabulary (one-time, idempotent).

Before this ran, the same topic appeared under several labels:

  Computer Science HL
    "Theme A: Concepts of computer science"          17 items   <- canonical
    "Theme A: Computer fundamentals"                  1 item    <- A1 is a STRAND of Theme A
    "Theme A: Systems in organisations"               3 items   <- not in the 2027 guide at all
    "Theme B: Computational thinking and problem-solving"  6   <- canonical
    "Theme B: Computational thinking and programming"      5   <- B2 is a STRAND of Theme B

  Business Management SL
    "Unit 3: Finance and accounts"                    5 items   <- canonical
    "Topic 3: Finance and accounts"                   1 item    <- wrong prefix ("Topic" not "Unit")
    "Unit 5: Operations management"                   5 items   <- canonical
    "Units 3 and 5: Finance and accounts; Operations management"  1  <- two units in one label

The Computer Science names were checked against the IB DP Computer Science guide
for first assessment 2027, which defines exactly two themes -- "Concepts of
Computer Science" and "Computational Thinking and Problem Solving" -- with A1
(Computer Fundamentals) and B2 (Programming) as strands *inside* them. The
strand names had been promoted to theme labels, and one label ("Systems in
organisations") does not appear in the guide at all.

Only the `topic` field is touched. `subtopic` and `syllabus_ref` already carry
the fine-grained information, so nothing is lost. Running this twice is a no-op.

    python3 tools/normalise_topics.py --check   # report, change nothing
    python3 tools/normalise_topics.py --write   # apply
"""

import argparse
import glob
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RENAMES = {
    "Computer Science HL": {
        "Theme A: Computer fundamentals": "Theme A: Concepts of computer science",
        "Theme A: Systems in organisations": "Theme A: Concepts of computer science",
        "Theme B: Computational thinking and programming": "Theme B: Computational thinking and problem-solving",
    },
    "Business Management SL": {
        "Topic 3: Finance and accounts": "Unit 3: Finance and accounts",
        "Units 3 and 5: Finance and accounts; Operations management": "Unit 5: Operations management",
    },
}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="report only")
    g.add_argument("--write", action="store_true", help="apply the renames")
    args = ap.parse_args()

    changed = Counter()
    files = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "*", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        qs = doc.get("questions")
        if not isinstance(qs, list):
            continue
        touched = False
        for q in qs:
            table = RENAMES.get(q.get("subject") or "", {})
            old = q.get("topic")
            if old in table:
                new = table[old]
                changed["%s: %s  ->  %s" % (q["subject"], old, new)] += 1
                touched = True
                if args.write:
                    q["topic"] = new
        if touched:
            files += 1
            if args.write:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(doc, fh, ensure_ascii=False, indent=2)
                    fh.write("\n")

    if not changed:
        print("Nothing to normalise: every topic label is already canonical.")
        return 0
    print("%d item(s) affected across %d file(s):" % (sum(changed.values()), files))
    for k, n in sorted(changed.items()):
        print("  %2d  %s" % (n, k))
    print()
    print("Applied." if args.write else "Dry run -- nothing written. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
