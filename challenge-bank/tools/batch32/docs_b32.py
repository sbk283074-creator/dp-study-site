"""Update PLAN.md and README.md for Batch 32.

Every replacement is asserted to match exactly once, because a doc edit that silently
misses is how the last three audits found stale numbers.
"""
import io, sys

EDITS = []

# ------------------------------------------------------------------ PLAN.md
EDITS.append(("PLAN.md",
"""**Status: live. 337 questions across the four subjects, every priority-1 and priority-2 syllabus node
covered (166/166 nodes, 100%). The difficulty label is now a measured property rather than a declared
one: from 2026-09-13 every item must carry `difficulty_evidence`, and 252 of 337 do.""",
"""**Status: live. 339 questions across the four subjects, every priority-1 and priority-2 syllabus node
covered (166/166 nodes, 100%). The difficulty label is now a measured property rather than a declared
one: from 2026-09-13 every item must carry `difficulty_evidence`, and 254 of 339 do."""))

EDITS.append(("PLAN.md",
"""**Figure coverage is now a first-class gate rather than a nice-to-have.** Batch 23 raised the share of
items that carry a self-authored graph to 75 of 301 = 25%; Batch 26 took it to 84 of 310 = 27.1%; Batch 27
to 89 of 315 = 28.3%; Batch 28 to 94 of 320 = 29.4%; Batch 29 to 98 of 325 = 30.2%; Batch 30 to
104 of 331 = 31.4%; Batch 31 takes it to
**110 of 337 = 32.6%** and raises
the bank-wide ratchet `FIGURE_COVERAGE_FLOOR` from 0.31 to
**0.32** — the floor may rise and may
never fall, so a later batch cannot quietly spend the coverage. No subject prints a gap: CS 52%,
Physics 39%, Maths 22%, BM 21%, against a 15% target — but only **6 non-figure items of headroom** are left
(110/343 = 32.07% passes, 110/344 = 31.98% fails), so the ratchet now *forces* a batch to carry figures
rather than
merely encouraging it.""",
"""**Figure coverage is now a first-class gate rather than a nice-to-have.** Batch 23 raised the share of
items that carry a self-authored graph to 75 of 301 = 25%; Batch 26 took it to 84 of 310 = 27.1%; Batch 27
to 89 of 315 = 28.3%; Batch 28 to 94 of 320 = 29.4%; Batch 29 to 98 of 325 = 30.2%; Batch 30 to
104 of 331 = 31.4%; Batch 31 took it to 110 of 337 = 32.6% and raised the bank-wide ratchet
`FIGURE_COVERAGE_FLOOR` from 0.31 to **0.32** — the floor may rise and may never fall, so a later batch
cannot quietly spend the coverage. Batch 32 takes it to **112 of 339 = 33.0%**, and **the floor was left at
0.32 on purpose**: raising it to 0.33 would leave no headroom at all, and a ratchet with zero headroom
pressures a batch to bolt figures onto items that do not need one, which is the failure §0.1 now forbids.
No subject prints a gap: CS 52%, Physics 40%, Maths 23%, BM 21%, against a 15% target — and ten plain-text
items of headroom remain (112/349 = 32.09% passes, 112/350 = 32.00% fails), so the floor still binds without
dictating the shape of a wave."""))

EDITS.append(("PLAN.md",
"""- **Priority-3 ("stretch") tail:** optional deeper items beyond the must/should nodes — open when there is""",
"""- **Batch 32 — DONE (2 items, 337 → 339; the first wave whose generator is in the repo).** A deliberately
  small wave, run to test the §0 rules end to end under a credit budget, and it is the first Challenge Bank
  wave whose authoring script is committed: `tools/batch32/` holds the two generators and the independent
  verification script, so the data can be regenerated and diffed instead of existing only as JSON. Until
  now every batch generator had been written to `/tmp` and lost, which meant the SVG builders behind 337
  items were unreproducible — the same trap `bpho/tools/` had already fixed for itself.
  - **The brief came from the component, and from the ledger's own "what to use next" column.** Physics
    Paper 1B holds 17 data-based items and every one of them treats a *single* dataset: linearise and fit,
    find the residual pattern, exclude the seeded anomaly, propagate the quadrature. `STANDARD.md` §4.6
    lists "comparison of two datasets taken with different apparatus" as an approach not yet used, so that
    is what `PHYS-B.5-601` (P1B, 13 marks, d5, `non_obvious_tool`) does. Two students fit $V = E - Ir$ to
    the same cell; student A's ammeter reads $+0.040$ A with no current and is never zeroed, and nobody is
    told. A's internal resistance comes out $2.40 \\pm 0.01\\ \\Omega$ — correct — while A's electromotive
    force comes out $1.60 \\pm 0.01$ V against B's $1.48 \\pm 0.02$ V. The resistances agree to **1.2**
    combined uncertainties and the EMFs disagree by **6.0**, and that asymmetry is the whole item: a
    constant offset in the independent variable slides a line along itself, cancelling in every
    $\\Delta V / \\Delta I'$, so it destroys the intercept and cannot touch the gradient. The candidate has
    to derive that, then invert it to measure the fault, $\\delta = \\Delta E / r = 0.049 \\pm 0.004$ A,
    test B's guess against the predicted shift $r\\delta = 0.096$ V versus an observed $0.117 \\pm 0.020$ V,
    and land on the split verdict — accept B's EMF, keep A's resistance. Rubric **9/9**; originality
    ext 0.022 / int 0.013 / appr 0.086.
  - **Every number in it is printed from a fit, not typed.** Both datasets were generated from the model
    with the seeded truth, the offset applied to the current actually plotted, reading noise added, and the
    values rounded to each instrument's stated resolution; ordinary least squares was then run on the
    *rounded* data with intercept and gradient uncertainties from the residual scatter, and the answer,
    the markscheme notes, the difficulty evidence and the 15 assertions are all interpolated from that fit.
    The three claims the item rests on were each checked against it before the item was written, which is
    the §0.5 rule in practice: a wrong markscheme is worse than none, because a student learns the wrong
    thing from it.
  - **The figure was linted, rendered, and found wanting twice.** The first render showed three defects no
    coordinate check could see: the legend ran off the right edge, the A and B line labels crowded
    together, and the vertical error bars — $\\pm 0.01$ V is about three pixels at this scale — were
    invisible, so the legend claimed an uncertainty the drawing did not show. All three were fixed (short
    legend, B moved below its own line, end caps on the vertical bars that widen the mark without
    lengthening it), and two of them became permanent checks in the generator's lint: a label's estimated
    width is now tested against the frame, and a label within 10 px of a data marker is a defect. The
    second render still showed B sitting on its own first marker; it moved again. **This is what §0.1
    means by "check it by yourself"** — the markup passing is not the figure being right.
  - **`MATH-P3-019` (P3, 14 marks, d5, `partial_cancellation`)** is the maths item, and it is the sample
    that was approved to build on: the lobes of $y = e^{-x} \\sin x$, where the convergent improper integral
    is $\\tfrac12$ and the total area is $0.545165$, so the technically flawless calculation is **8.28%**
    wrong and agrees with the answer to two significant figures. Rubric 9/9, originality ext 0.015 /
    int 0.010 / appr 0.150, every value cross-checked against Simpson quadrature on the raw integrand to
    about $2 \\times 10^{-15}$.
  - **Numbers after the wave.** 339 items — Maths 137 / 1953 marks, Physics 96 / 1144, CS 67 / 997,
    BM SL 39 / 563; 4657 marks in all. Difficulty 5 / 185 / 149 (d5 shares: Maths 48%, Physics 45%,
    CS 46%, BM 23% — all inside the 50% cap). Evidence 254 / 339, `difficulty 5 with no evidence` **0**,
    `labels the evidence does not permit` **0**. Assertions 3957. Figures 112 / 339 = 33% (Maths 31/137 =
    23%, Physics 38/96 = 40%, CS 35/67 = 52%, BM 8/39 = 21%). Cross-syllabus sourcing 125 items
    (`uk-alevel` 43). `validate.py` 0 failures / 175 warnings, `difficulty_audit --check` exit 0,
    `prove_difficulty_gates` 10/10, similarity 0 above threshold at ext 0.090 / int 0.073 / appr 0.366,
    coverage 166/166 nodes.
  - **What §0 was judged by eye rather than by a gate**, and is recorded here rather than claimed as
    enforced: that both figures are load-bearing rather than decorative; that the difficulty in each item
    is a decision and not arithmetic; and that the four parts of `PHYS-B.5-601` escalate. The first two
    have a review habit now (state it per item); the third does not — the arc test only forbids the
    heaviest part coming first, and nothing yet checks that the last part is the hardest.
- **Priority-3 ("stretch") tail:** optional deeper items beyond the must/should nodes — open when there is"""))

EDITS.append(("PLAN.md",
"""  136 questions / 1939 marks, physics 95 / 1131, CS 67 / 997, BM SL 39 / 563 — all difficulty 3–5, May
  2028 cohort.""",
"""  137 questions / 1953 marks, physics 96 / 1144, CS 67 / 997, BM SL 39 / 563 — all difficulty 3–5, May
  2028 cohort. Since 2026-09-23 the paper also prints the four options of every MCQ part: `build.py` had
  never rendered `parts[].options` anywhere, so 95 Physics P1A questions were unanswerable as printed."""))

# ---------------------------------------------------------------- README.md
EDITS.append(("README.md",
"""| Subject | Guide in force | Questions | Nodes covered |
|---|---|---:|---:|
| Math AA HL | 2021 (runs to Nov 2028) | 136 | 83 / 83 (100%) |
| Physics HL | 2025 | 95 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 67 | 25 / 25 (100%) |
| Business Management SL | 2024 | 39 | 34 / 34 (100%) |
| **Total** | | **337** | **166 / 166 (100%)** |""",
"""| Subject | Guide in force | Questions | Nodes covered |
|---|---|---:|---:|
| Math AA HL | 2021 (runs to Nov 2028) | 137 | 83 / 83 (100%) |
| Physics HL | 2025 | 96 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 67 | 25 / 25 (100%) |
| Business Management SL | 2024 | 39 | 34 / 34 (100%) |
| **Total** | | **339** | **166 / 166 (100%)** |"""))

EDITS.append(("README.md",
"""All 337 items are difficulty 3–5 (**5 at difficulty 3, 185 at difficulty 4, 147 at difficulty 5**), and
pass `validate.py`
with **0 failures**.""",
"""All 339 items are difficulty 3–5 (**5 at difficulty 3, 185 at difficulty 4, 149 at difficulty 5**), and
pass `validate.py`
with **0 failures**."""))

EDITS.append(("README.md",
"""Every item carries a `verification.assertions` list — **3918 machine-checked assertions** in total — so
the arithmetic in every answer is re-derived by the validator on each run, not merely asserted by the
author. **110 items are figure-bearing (33%)**, with the figure inlined into `question.figure` so a page
renders identically on `file://` and over HTTP.""",
"""Every item carries a `verification.assertions` list — **3957 machine-checked assertions** in total — so
the arithmetic in every answer is re-derived by the validator on each run, not merely asserted by the
author. **112 items are figure-bearing (33%)**, with the figure inlined into `question.figure` so a page
renders identically on `file://` and over HTTP."""))

EDITS.append(("README.md",
"""| items with evidence for the label | **252 / 337** | 0 / 172 |""",
"""| items with evidence for the label | **254 / 339** | 0 / 172 |"""))

EDITS.append(("README.md",
"""**Sourcing is recorded, not claimed.** 120 items are drawn from other syllabuses — 高考, 强基, 竞赛,
A-Level, Further Maths, AP, 新加坡 A-Level, four from IB itself, and six recorded as `other` — and each names""",
"""**Sourcing is recorded, not claimed.** 125 items are drawn from other syllabuses — 高考, 强基, 竞赛,
A-Level, Further Maths, AP, 新加坡 A-Level, four from IB itself, and six recorded as `other` — and each names"""))

failures = []
cache = {}
for path, old, new in EDITS:
    text = cache.get(path) or io.open(path, encoding="utf-8").read()
    n = text.count(old)
    if n != 1:
        failures.append("%s: anchor matched %d times -- %.60s" % (path, n, old.replace("\n", " ")))
        continue
    cache[path] = text.replace(old, new)

if failures:
    print("\n".join(failures))
    sys.exit("aborted, nothing written")

for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)
    print("updated", path)
