# -*- coding: utf-8 -*-
"""Measure a section the way `gate_section` measures it.  Read-only.

    python measure.py 6          one section, per-question breakdown
    python measure.py all        every section, summary only
    python measure.py paper      the real 2025 paper, for comparison

Why this exists rather than "just call `gates.difficulty`":

  * **The figure directory must be absolute.**  `gates.HERE/fig`, not `"fig"`.  A relative
    path only resolves if the working directory happens to be `tools/bank`, and when it
    does not, `expand_figs` returns `<!-- MISSING FIGURE ... -->` instead of raising.  Every
    figure-bearing question then loses its `fig` term and reads **1.00 too low**, silently.
    That cost an hour in the section-6 session: six questions appeared to disagree with the
    gate by exactly 1.0 and the discrepancy looked like a scorer bug.

  * **The text must be `supify`-ed before it is scored.**  The scorer's `symbolic` flag and
    the formula count both read the rendered text, not the source.  Scoring the raw source
    gives a different number, so the helper would disagree with the gate it is checking.

  * **`figdir` is shared state during a real gate run.**  `gate_section` threads one
    `marker_ids` set through every question, which is what catches two figures defining the
    same marker id.  For measurement that set is irrelevant, so a fresh one per call is
    fine -- but it is worth knowing why the helper's signature differs from the gate's.

This is the tool the audit's "Reproducing this audit" section refers to.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gates as G
from statistics import median

FIGDIR = os.path.join(G.HERE, "fig")


def measure(q, mids=None, errs=None):
    """(scorer_input, features, score) for one question, exactly as the gate sees it."""
    mids = set() if mids is None else mids
    errs = [] if errs is None else errs
    stem = G.expand_figs(G.supify(q["stem"]), FIGDIR, mids, errs)
    opts = [G.expand_figs(G.supify(o), FIGDIR, mids, errs) for o in q["opts"]]
    sol = G.expand_figs(G.supify(q["sol"]), FIGDIR, mids, errs)
    d = {"sol": sol, "q": stem, "opts": opts,
         "trap": q.get("trap", ""), "rel": q.get("rel", [])}
    return d, G.features(d), G.difficulty(d)


def measure_all(n, verbose=True):
    ref = G.baseline()["R0-2025"]
    qs = sorted(G.load_section(n).QUESTIONS, key=lambda d: d["n"])
    rows = [(q, ) + measure(q) for q in qs]
    sc = [r[3] for r in rows]
    fe = [r[2] for r in rows]

    if verbose:
        print("%-7s %5s %3s %3s %3s %3s %3s %3s %3s %6s %5s %5s %s" % (
            "id", "score", "mv", "st", "fm", "ap", "sy", "fg", "rl",
            "trapl", "band", "diff", "shape"))
        for q, _d, f, s in rows:
            b = G.band_of(s, ref)
            flag = "  <== declared diff disagrees" if b != q["diff"] else ""
            print("%-7s %5.1f %3d %3d %3d %3d %3d %3d %3d %6d %5d %5d %s%s" % (
                q["id"], s, f["moves"], f["n_steps"], f["n_formula"], int(f["approx"]),
                int(f["symbolic"]), int(f["fig"]), f["relmods"], f["trap_len"],
                b, q["diff"], (q.get("profile") or {}).get("shape", "?"), flag))

    plan = G.spec.SECTIONS[n - 1]
    nc = sum(1 for f in fe if f["approx"] or f["symbolic"])
    ao = sum(1 for f in fe if f["approx"])
    dist = {}
    for q, _d, _f, _s in rows:
        dist[q["diff"]] = dist.get(q["diff"], 0) + 1

    print("%-7s median %5.2f  p25 %5.2f  min %5.2f  max %5.2f   (paper %.2f / %.2f / %.2f / %.2f)"
          % ("S%02d" % n, median(sc), G.percentile(sc, 25), min(sc), max(sc),
             ref["median"], ref["p25"], ref["min"], ref["max"]))
    if verbose:
        print("        top-quartile %d/%d   deep(>=%d moves) %d/%d   longest %d"
              % (sum(1 for s in sc if s >= ref["p75"]), G.TOP_QUARTILE_MIN,
                 G.DEEP_MOVES, sum(1 for f in fe if f["moves"] >= G.DEEP_MOVES),
                 G.DEEP_MIN, max(f["moves"] for f in fe)))
        print("        non-calc %d/%d (floor %d)   approximation %d/%d (floor %d)"
              % (nc, len(qs), plan.get("noncalc_min"), ao, len(qs), plan.get("approx_min")))
        print("        declared bands %s" % dict(sorted(dist.items())))
    return {"median": median(sc), "p25": G.percentile(sc, 25), "min": min(sc),
            "max": max(sc), "noncalc": nc, "approx": ao, "bands": dist}


def cmd_paper():
    ref = G.baseline()["R0-2025"]
    print("%-10s %4s %8s %8s %8s %8s %8s" % ("paper", "n", "median", "p25", "p75", "min", "max"))
    for tag, b in sorted(G.baseline().items()):
        print("%-10s %4d %8.1f %8.1f %8.1f %8.1f %8.1f"
              % (tag, b["n"], b["median"], b["p25"], b["p75"], b["min"], b["max"]))
    print("\nthe 2025 paper, question by question:")
    data = json.load(open(os.path.join(G.HERE, "papers.json"), encoding="utf-8"))
    qs = [q for q in data["questions"] if q["paper"] == "R0-2025"]
    for q in sorted(qs, key=lambda q: -G.difficulty(q)):
        f = G.features(q)
        print("  %-8s %-2s  score %5.1f  moves %2d  steps %2d  formulas %2d  "
              "approx %d  sym %d  rel %d"
              % (q["id"], q["module"], G.difficulty(q), f["moves"], f["n_steps"],
                 f["n_formula"], f["approx"], f["symbolic"], f["relmods"]))
    print("\n  note the step counts: the paper numbers 2.44 steps on average and never more "
          "than 5,\n  so a section averaging far above that is numbering more finely than "
          "the paper does.")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "paper":
        cmd_paper()
        return 0
    if arg == "all":
        ns = sorted(int(f[3:5]) for f in os.listdir(G.HERE)
                    if f.startswith("sec") and f.endswith(".py") and f[3:5].isdigit())
        for n in ns:
            measure_all(n, verbose=False)
        return 0
    if arg.isdigit():
        measure_all(int(arg), verbose=True)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
