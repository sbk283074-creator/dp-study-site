#!/usr/bin/env python3
"""One-time migration: record `provenance.source_family` on every item.

    python3 tools/backfill_source_family.py            # dry run, prints the plan
    python3 tools/backfill_source_family.py --write    # apply

STANDARD.md 4.5 now requires `source_family`, and the existing bank could not
satisfy it because the field did not exist when the items were written. Only 6
of 172 items named any source at all, so "we draw on other syllabuses" was
untestable in either direction.

The rule reads ONLY `provenance.inspired_by` and `provenance.resource_origin`.

It deliberately does NOT read `provenance.adaptation`. That field says what was
changed, and routinely names other systems while doing so -- "this genre is
standard in A-level and first-year mechanics" is a statement about the genre,
not a claim that the item came from A-Level. Including it produced two false
positives on the first attempt (PHYS-A.4-001 and PHYS-D.4-001, both of which
record `inspired_by: original`). An item the rules cannot classify is reported
as UNRESOLVED and left alone rather than guessed at.
"""

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as V  # noqa: E402

# Families matched against `inspired_by` first and `resource_origin` second.
# Within a field the EARLIEST mention wins, because `inspired_by` names what
# inspired the item in order of prominence: "Chinese 高考/强基 genre" is a 高考
# problem that also appears in 强基 materials, not the reverse. Testing the
# families in a fixed order instead put four of the six mixed-genre items in
# the wrong bucket.
RULES = [
    ("china-qiangji",      ("强基",)),
    ("china-gaokao",       ("高考", "gaokao")),
    ("china-competition",  ("竞赛", "olympiad", "competition")),
    ("uk-further-maths",   ("further maths", "further mathematics")),
    ("uk-alevel",          ("a-level", "a level", "alevel")),
    ("us-ap",              ("advanced placement", "ap calculus", "ap physics", "ap computer")),
    ("singapore-alevel",   ("singapore",)),
]


def _first_hit(blob):
    """-> family, or None. The earliest-mentioned family in this text wins."""
    best = None
    for family, needles in RULES:
        for needle in needles:
            pos = blob.find(needle)
            if pos >= 0 and (best is None or pos < best[0]):
                best = (pos, family)
    return best[1] if best else None


def classify(q):
    """-> source_family, or None when the rules cannot decide."""
    prov = q.get("provenance") or {}
    for field in ("inspired_by", "resource_origin"):
        blob = str(prov.get(field) or "").strip().lower()
        if not blob:
            continue
        hit = _first_hit(blob)
        if hit:
            return hit
    if str(prov.get("inspired_by") or "").strip().lower().startswith("original"):
        return "original"
    return None


def with_family(prov, family):
    """Insert source_family after inspired_by, preserving key order."""
    out, placed = {}, False
    for k, v in prov.items():
        out[k] = v
        if k == "inspired_by":
            out["source_family"] = family
            placed = True
    if not placed:
        out = {"source_family": family}
        out.update(prov)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply (default is a dry run)")
    args = ap.parse_args()

    tally = collections.Counter()
    unresolved = []
    changed_files = 0

    for path in sorted(V.DATA.glob("*/*.json")):
        if path.name.startswith("_"):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for q in payload.get("questions", []):
            prov = q.get("provenance")
            if not isinstance(prov, dict):
                continue
            if str(prov.get("source_family") or "").strip():
                tally["already set"] += 1
                continue
            family = classify(q)
            if family is None:
                unresolved.append((q.get("id"), (prov.get("inspired_by") or "")[:70]))
                tally["UNRESOLVED"] += 1
                continue
            q["provenance"] = with_family(prov, family)
            tally[family] += 1
            changed = True

        if changed:
            changed_files += 1
            if args.write:
                # Same format as the existing files: 2-space indent, literal
                # UTF-8, trailing newline. Verified byte-identical on an
                # unchanged file before this was written.
                path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")

    print("%s\n" % ("APPLIED" if args.write else "DRY RUN -- nothing written"))
    for k, v in tally.most_common():
        print("  %-24s %d" % (k, v))
    if unresolved:
        print("\n  UNRESOLVED (%d) -- left untouched, needs a human:" % len(unresolved))
        for i, s in unresolved:
            print("    %-20s %s" % (i, s))
    print("\n  files %s: %d" % ("written" if args.write else "that would change", changed_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
