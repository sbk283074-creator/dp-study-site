#!/usr/bin/env python3
"""Difficulty audit for the Challenge Bank (STANDARD.md 2.2-2.5).

    python3 tools/difficulty_audit.py             # the report
    python3 tools/difficulty_audit.py --check     # exit 1 if calibration is breached
    python3 tools/difficulty_audit.py --backlog   # every item still missing evidence
    python3 tools/difficulty_audit.py --id MATH-AHL5.11-101

`validate.py` checks that each item *makes* a difficulty claim. This tool checks
whether the bank's claims, taken together, are *credible* -- a different
question, and the one that was going unanswered.

On 2026-09-13, before the standard existed, the bank passed every per-item rule
while 46% of its items claimed difficulty 5, Physics HL claimed 62%, no item
claimed 3, and not one item carried evidence for its label. Every per-item check
was green. The label simply did not mean anything.

Two of the three calibration rules are properties of the whole bank, which is
why this is a separate gate rather than another branch inside validate.py.
"""

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as V  # noqa: E402  (same directory, shares the rubric)

# Ratchet, not a target: coverage may not fall below this, and the standard
# requires it to rise. Raised when the backlog is cleared, never lowered.
EVIDENCE_COVERAGE_FLOOR = 8
MAX_D5_SHARE = 0.50
SUBJECT_ORDER = ["Math AA HL", "Physics HL", "Computer Science HL", "Business Management SL"]

# The state measured on 2026-09-13, when the standard took force.
#
# A gate that blocks on a known, published backlog gets switched off, and a gate
# that is switched off is a slogan. So the calibration rules are enforced against
# this baseline rather than against the target: the bank may not get *worse*, and
# the audit keeps printing the gap until it closes. R1 and R2 are debts -- real,
# measured, and reported on every run -- but only a regression stops the pipeline.
#
# A subject already above the 50% cap is held to its own recorded share until it
# comes down, so Physics at 62% is a debt, not a regression, but Physics at 70%
# is a regression.
BASELINE = {
    "measured": "2026-09-13",
    "subject_d5_share": {
        "Math AA HL": 0.47,
        "Physics HL": 0.62,
        "Computer Science HL": 0.38,
        "Business Management SL": 0.11,
    },
    "d3_count": 0,
    "evidence_coverage": 8,
}
# A subject may exceed the cap only up to this much over its own baseline before
# the increase counts as a regression rather than drift.
D5_REGRESSION_SLACK = 0.02


def evidence_of(q):
    ev = q.get("difficulty_evidence")
    return ev if isinstance(ev, dict) and ev else None


def bar(n, total, width=22):
    if not total:
        return ""
    filled = int(round(width * n / total))
    return "#" * filled + "." * (width - filled)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the bank has regressed against the 2026-09-13 baseline")
    ap.add_argument("--strict", action="store_true",
                    help="with --check, count the outstanding debts as failures too")
    ap.add_argument("--backlog", action="store_true",
                    help="list every item still missing difficulty_evidence")
    ap.add_argument("--id", help="print the rubric breakdown for a single item")
    args = ap.parse_args()

    items = [q for _f, q in V.load()]
    if not items:
        print("no items loaded")
        return 1

    if args.id:
        hit = [q for q in items if q.get("id") == args.id]
        if not hit:
            print("no item with id %r" % args.id)
            return 1
        q = hit[0]
        score, br, notes, info = V.difficulty_score(q)
        allowed = V.max_label_for(score)
        print("%s  %s  %s marks  declared difficulty %s"
              % (q.get("id"), q.get("subject"), q.get("marks"), q.get("difficulty")))
        print("  rubric score %d / %d  ->  permits at most difficulty %s"
              % (score, V.DIFFICULTY_MAX_SCORE, allowed if allowed else "none"))
        for k in ("failure_point", "wrong_answer", "naive_path", "arc", "assertions"):
            print("    %-14s %d" % (k, br.get(k, 0)))
        for n in notes:
            print("    ! %s" % n)
        for n in info:
            print("    i %s" % n)
        ev = evidence_of(q)
        print("  evidence: %s" % ("present" if ev else "MISSING -- the label is unbacked"))
        if ev:
            print("    lever_type: %s" % ev.get("lever_type"))
        return 0

    # ---------------------------------------------------------------- scale
    print("=" * 78)
    print("DIFFICULTY AUDIT  --  %d items" % len(items))
    print("=" * 78)

    by_subject = collections.defaultdict(list)
    for q in items:
        by_subject[q.get("subject", "?")].append(q)

    print("\n1. Does the label discriminate?\n")
    print("   %-24s %4s   %-24s %s" % ("subject", "n", "d3 / d4 / d5", "share claiming difficulty 5"))
    shares = {}
    for s in SUBJECT_ORDER + sorted(set(by_subject) - set(SUBJECT_ORDER)):
        qs = by_subject.get(s)
        if not qs:
            continue
        c = collections.Counter(q.get("difficulty") for q in qs)
        n = len(qs)
        share = c[5] / n
        shares[s] = share
        flag = ""
        if share > MAX_D5_SHARE:
            base = BASELINE["subject_d5_share"].get(s)
            flag = "  <- debt" if base is None or share <= base + D5_REGRESSION_SLACK else "  <- REGRESSION"
        print("   %-24s %4d   %2d / %2d / %2d %s %3.0f%%%s"
              % (s, n, c[3], c[4], c[5], bar(c[5], n), 100 * share, flag))

    allc = collections.Counter(q.get("difficulty") for q in items)
    n = len(items)
    d3_share = allc[3] / n
    d5_share = allc[5] / n
    print("\n   bank-wide: difficulty 5 = %.0f%%   difficulty 3 = %.0f%%" % (100 * d5_share, 100 * d3_share))

    regressions, debts = [], []
    for s, share in shares.items():
        if share <= MAX_D5_SHARE:
            continue
        base = BASELINE["subject_d5_share"].get(s)
        msg = "R1 %s puts %.0f%% of its items at difficulty 5 (cap %.0f%%)" % (
            s, 100 * share, 100 * MAX_D5_SHARE)
        if base is not None and share > base + D5_REGRESSION_SLACK:
            regressions.append(msg + "; baseline %s was %.0f%%" % (BASELINE["measured"], 100 * base))
        else:
            debts.append(msg + "; baseline %s was %s"
                         % (BASELINE["measured"],
                            "%.0f%%" % (100 * base) if base is not None else "not recorded"))
    if allc[3] < BASELINE["d3_count"]:
        regressions.append("R2 difficulty-3 count fell from %d to %d"
                           % (BASELINE["d3_count"], allc[3]))
    elif allc[3] == 0:
        debts.append("R2 no item claims difficulty 3 -- the 3-5 scale has collapsed to two points")

    # -------------------------------------------------------------- evidence
    with_ev = [q for q in items if evidence_of(q)]
    without = [q for q in items if not evidence_of(q)]
    unbacked5 = [q for q in without if q.get("difficulty") == 5]
    inflated = []
    for q in with_ev:
        score, _br, _n, _i = V.difficulty_score(q)
        allowed = V.max_label_for(score)
        if allowed is None or (isinstance(q.get("difficulty"), int) and q["difficulty"] > allowed):
            inflated.append((q, score, allowed))

    print("\n2. Is the label backed by evidence?\n")
    print("   evidence present : %d / %d  %s %.0f%%" % (len(with_ev), n, bar(len(with_ev), n), 100 * len(with_ev) / n))
    print("   backlog          : %d items (grandfathered; see STANDARD.md 4.7)" % len(without))
    print("   difficulty 5 with no evidence : %d  <-- the headline number" % len(unbacked5))
    print("   labels the evidence does not permit : %d" % len(inflated))
    for q, score, allowed in inflated[:10]:
        print("       %-20s claims %s, scores %d/%d (permits %s)"
              % (q.get("id"), q.get("difficulty"), score, V.DIFFICULTY_MAX_SCORE, allowed))

    if len(with_ev) < EVIDENCE_COVERAGE_FLOOR:
        regressions.append("R3 evidence coverage %d has fallen below the ratchet floor %d"
                           % (len(with_ev), EVIDENCE_COVERAGE_FLOOR))

    # ----------------------------------------------------- lever taxonomy
    print("\n3. Is the difficulty varied, or one trick in different clothes?\n")
    levers = collections.Counter(evidence_of(q).get("lever_type") for q in with_ev)
    if not levers:
        print("   no declared lever_type yet -- the taxonomy cannot be reported.")
        print("   (%d of %d items still need difficulty_evidence.)" % (len(without), n))
    else:
        for k, v in levers.most_common():
            print("   %-24s %3d  %s" % (k, v, bar(v, len(with_ev))))
        top = levers.most_common(1)[0]
        print("\n   distinct levers in use: %d of %d available" % (len(levers), len(V.LEVER_TYPES)))
        print("   largest share: %s at %.0f%% of evidenced items" % (top[0], 100 * top[1] / len(with_ev)))

    # ------------------------------------------------------------- sourcing
    print("\n4. Where does the difficulty come from?\n")
    fams = collections.Counter((q.get("provenance") or {}).get("source_family") or "(unrecorded)"
                               for q in items)
    for k, v in fams.most_common():
        print("   %-24s %3d  %s" % (k, v, bar(v, n)))
    unknown = [k for k in fams if k not in V.SOURCE_FAMILIES]
    if unknown:
        regressions.append("R4 source_family outside the list: %s" % ", ".join(map(str, unknown)))

    # -------------------------------------------------------------- backlog
    if args.backlog:
        print("\n5. Backlog -- items with no difficulty_evidence\n")
        for s in SUBJECT_ORDER:
            qs = [q for q in without if q.get("subject") == s]
            if qs:
                print("   %s (%d): %s" % (s, len(qs), ", ".join(q["id"] for q in qs)))

    print("\n" + "=" * 78)
    if debts:
        print("OUTSTANDING DEBTS (%d) -- measured, published, and being paid down:" % len(debts))
        for b in debts:
            print("  - " + b)
    if regressions:
        print("CALIBRATION REGRESSED (%d) -- the bank is worse than it was:" % len(regressions))
        for b in regressions:
            print("  x " + b)
    if not debts and not regressions:
        print("calibration OK -- every rule in STANDARD.md 2.5 holds")
    print("=" * 78)
    failed = bool(regressions) or (args.strict and bool(debts))
    return 1 if (args.check and failed) else 0


if __name__ == "__main__":
    sys.exit(main())
