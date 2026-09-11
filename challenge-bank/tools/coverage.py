#!/usr/bin/env python3
"""Syllabus coverage report for the Challenge Bank.

    python3 tools/coverage.py                # full report
    python3 tools/coverage.py --next 12      # the next 12 nodes to write
    python3 tools/coverage.py --subject "Math AA HL"

Every question is mapped to the syllabus nodes its `syllabus_ref`, `subtopic`
and `topic` mention. Nodes come from tools/syllabus.json, which is generated
from the IB guide PDFs by tools/extract_syllabus.py.

`--next` is the batch brief: it prints the highest-priority nodes that have the
fewest questions, so a batch always attacks the real gaps rather than the
easiest topic to write.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SYLLABUS = json.loads((ROOT / "tools" / "syllabus.json").read_text(encoding="utf-8"))

CODE_PATTERNS = {
    "Math AA HL": re.compile(r"\b(?:SL|AHL)\s*(\d+\.\d+)\b"),
    "Physics HL": re.compile(r"\b([A-E]\.\d)\b"),
    "Computer Science HL": re.compile(r"\b([AB][1-4]\.\d+)\b"),
    "Business Management SL": re.compile(r"\b([1-6]\.\d+)\b"),
}

PRIORITY_LABEL = {1: "must", 2: "should", 3: "optional"}


def load_questions():
    rows = []
    for f in sorted(DATA.glob("*/*.json")):
        if f.name.startswith("_"):
            continue
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for q in payload.get("questions", []):
            rows.append(q)
    return rows


def codes_for(q):
    pat = CODE_PATTERNS.get(q.get("subject", ""))
    if not pat:
        return set()
    hay = " ".join(str(q.get(k, "")) for k in ("syllabus_ref", "subtopic", "topic"))
    return set(pat.findall(hay))


def build():
    counts = {}
    questions = load_questions()
    for subj, body in SYLLABUS["subjects"].items():
        counts[subj] = {code: [] for code in body["nodes"]}
    unmapped = []
    for q in questions:
        subj = q.get("subject")
        found = codes_for(q)
        if not found:
            unmapped.append(q.get("id"))
            continue
        for c in found:
            if subj in counts and c in counts[subj]:
                counts[subj][c].append(q.get("id"))
            else:
                unmapped.append("%s (%s)" % (q.get("id"), c))
    return counts, questions, unmapped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject")
    ap.add_argument("--next", type=int, metavar="N", help="print the next N nodes to write")
    ap.add_argument("--all-nodes", action="store_true", help="list covered nodes too")
    args = ap.parse_args()

    counts, questions, unmapped = build()
    subs = [args.subject] if args.subject else list(SYLLABUS["subjects"])
    total_nodes = total_covered = 0
    gaps = []

    for subj in subs:
        body = SYLLABUS["subjects"][subj]
        nodes = body["nodes"]
        covered = [c for c in nodes if counts[subj].get(c)]
        total_nodes += len(nodes)
        total_covered += len(covered)
        n_here = sum(1 for q in questions if q.get("subject") == subj)
        print("\n=== %s — %d questions · %d/%d nodes covered (%d%%) ==="
              % (subj, n_here, len(covered), len(nodes), 100 * len(covered) // len(nodes)))

        by_prio = {}
        for code, meta in nodes.items():
            by_prio.setdefault(meta["priority"], []).append(code)
        for prio in sorted(by_prio):
            codes = by_prio[prio]
            done = [c for c in codes if counts[subj].get(c)]
            print("  priority %d (%s): %d/%d covered"
                  % (prio, PRIORITY_LABEL.get(prio, "?"), len(done), len(codes)))
            missing = [c for c in codes if not counts[subj].get(c)]
            for c in missing:
                gaps.append((prio, subj, c, nodes[c]["title"]))
            if args.all_nodes:
                for c in codes:
                    ids = counts[subj].get(c) or []
                    print("      %-6s %-52s %s" % (c, nodes[c]["title"][:52],
                                                  ", ".join(ids) or "-"))

    gaps.sort(key=lambda x: (x[0], x[1]))
    print("\n=== gaps (%d uncovered nodes) ===" % len(gaps))
    if not gaps:
        print("  none — every node is covered.")
    if args.next:
        print("\n=== next %d to write ===" % args.next)
        for prio, subj, code, title in gaps[:args.next]:
            print("  [%s] %-24s %-6s %s" % (PRIORITY_LABEL.get(prio, "?"), subj, code, title))
    else:
        for prio, subj, code, title in gaps:
            print("  [%s] %-24s %-6s %s"
                  % (PRIORITY_LABEL.get(prio, "?"), subj, code, title[:56]))

    if unmapped:
        print("\nquestions with no usable syllabus code (%d): %s"
              % (len(unmapped), ", ".join(str(u) for u in unmapped[:12])))
    print("\nTOTAL: %d questions · %d/%d nodes covered (%d%%)"
          % (len(questions), total_covered, total_nodes,
             100 * total_covered // max(1, total_nodes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
