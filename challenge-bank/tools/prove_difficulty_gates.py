#!/usr/bin/env python3
"""Prove the difficulty gates are not vacuous.

    python3 tools/prove_difficulty_gates.py

A gate that never fires is worse than no gate, because it advertises a guarantee
it does not provide. This is a regression test for §2.2-§2.5: it takes a real,
passing item, injects one specific defect at a time, and asserts that the gate
rejects it. Nothing is written to disk.

Two of these cases found real gaps when they were first run, which is the point:

  * A `wrong_answer` reduced to a verbatim copy of `naive_path` scored 7 of 9,
    and 7 permitted difficulty 4 -- so the label survived on a hollow field.
    That is why difficulty >= 4 is now a completeness floor and not only a sum.
  * The mark-distribution test was withdrawn after it fired on three of the
    eight items carrying real evidence. Its case is kept here as the control
    that the shape signal is reported but cannot fail a run.
"""
import copy
import glob
import json
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
CB = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import validate as V  # noqa: E402

BASE = "MATH-AHL1.13-101"   # a real item that passes today


def load_one(qid):
    for p in sorted(glob.glob(os.path.join(CB, "data", "*", "*.json"))):
        if os.path.basename(p).startswith("_"):
            continue
        for q in json.load(open(p, encoding="utf-8")).get("questions", []):
            if q.get("id") == qid:
                return copy.deepcopy(q)
    raise SystemExit("no item %s -- has the bank moved?" % qid)


CASES = []


def case(name, mutate, want_fail, want_warn_substr=None):
    CASES.append((name, mutate, want_fail, want_warn_substr))


def _set_ev(**kw):
    def m(q):
        q["difficulty_evidence"].update(kw)
    return m


def _set(**kw):
    def m(q):
        q.update(kw)
    return m


def _copy_naive_into(field):
    def m(q):
        q["difficulty_evidence"][field] = q["difficulty_evidence"]["naive_path"]
    return m


def _hollow(q):
    q["difficulty_evidence"] = {"lever_type": "decoy_technique",
                                "naive_path": "Read it off the diagram.",
                                "failure_point": "It is wrong.",
                                "wrong_answer": "Wrong."}


def _strip(created):
    def m(q):
        q.pop("difficulty_evidence", None)
        q["difficulty"] = 5
        q["created_at"] = created
    return m


def _bad_family(q):
    q.setdefault("provenance", {})["source_family"] = "made_up_family"


def _no_origin(q):
    prov = q.setdefault("provenance", {})
    prov["source_family"] = "china-gaokao"
    prov["resource_origin"] = None


# ---- lever taxonomy ------------------------------------------------------------
case("lever_type invented ('difficulty_by_vibes')",
     _set_ev(lever_type="difficulty_by_vibes"), True)

# ---- the three evidence fields must be three distinct statements ----------------
case("wrong_answer is naive_path written again",
     _copy_naive_into("wrong_answer"), True)
case("failure_point is naive_path written again",
     _copy_naive_into("failure_point"), True)
case("evidence too thin to score (three short fields)", _hollow, True)

# ---- the label must be earned ---------------------------------------------------
case("declares difficulty 5, evidence scores 9/9 -> allowed", _set(difficulty=5), False)
# Grandfathering is by date, not by wish: the same item fails if it is dated on
# or after the standard, and only warns if it predates it. Without the two cases
# taken together, "no new batch may add to the backlog" would not be enforced.
case("post-standard item (2026-09-13) with no evidence -> may not ship",
     _strip("2026-09-13"), True)
case("pre-standard item (2026-09-11) with no evidence -> grandfathered",
     _strip("2026-09-11"), False, want_warn_substr="no difficulty_evidence")

# ---- sourcing must be recorded and attributable --------------------------------
case("source_family outside the list", _bad_family, True)
case("source_family china-gaokao with no resource_origin", _no_origin, True)

# ---- control -------------------------------------------------------------------
case("CONTROL -- the real item, unmodified", lambda q: None, False)


def run():
    orig = load_one(BASE)
    print("=" * 78)
    print("NON-VACUITY PROOF  --  %d cases against %s" % (len(CASES), BASE))
    print("=" * 78)
    bad = 0
    for name, mutate, want_fail, want_warn in CASES:
        q = copy.deepcopy(orig)
        mutate(q)
        fail, warn = [], []
        V.check_difficulty(q, fail, warn)
        V.check_sourcing(q, fail, warn)
        got_fail = bool(fail)
        ok = (got_fail == want_fail)
        if want_warn and not any(want_warn in w for w in warn):
            ok = False
        bad += 0 if ok else 1
        print("\n%s %s" % ("PASS" if ok else "**FAIL**", name))
        print("   expected reject: %-5s  got reject: %s" % (want_fail, got_fail))
        for f in fail:
            print("     x %s" % f)
        for w in warn:
            print("     ! %s" % w)
    print("\n" + "=" * 78)
    print("all %d cases behaved as intended" % len(CASES) if not bad
          else "%d of %d cases MISBEHAVED -- the gate has a hole" % (bad, len(CASES)))
    print("=" * 78)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(run())
