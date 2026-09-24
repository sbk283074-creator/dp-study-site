"""PLAN.md and README.md updates for Batch 33 (items 1 and 2)."""
import io, sys

EDITS = []

EDITS.append(("PLAN.md",
"""**Status: live. 339 questions across the four subjects""",
"""**Status: live. 341 questions across the four subjects"""))

EDITS.append(("PLAN.md",
"""one: from 2026-09-13 every item must carry `difficulty_evidence`, and 254 of 339 do.""",
"""one: from 2026-09-13 every item must carry `difficulty_evidence`, and 256 of 341 do."""))

EDITS.append(("PLAN.md",
"""cannot quietly spend the coverage. Batch 32 takes it to **112 of 339 = 33.0%**, and **the floor was left at
0.32 on purpose**: raising it to 0.33 would leave no headroom at all, and a ratchet with zero headroom
pressures a batch to bolt figures onto items that do not need one, which is the failure §0.1 now forbids.
No subject prints a gap: CS 52%, Physics 40%, Maths 23%, BM 21%, against a 15% target — and ten plain-text
items of headroom remain (112/349 = 32.09% passes, 112/350 = 32.00% fails), so the floor still binds without
dictating the shape of a wave.""",
"""cannot quietly spend the coverage. Batch 32 took it to 112 of 339 = 33.0% and Batch 33 to
**114 of 341 = 33.4%**, and **the floor has been left at 0.32 through both waves, deliberately**: raising
it to 0.33 would leave only four plain-text items of headroom, and a ratchet that tight would fail a wave
whose items genuinely do not need a drawing — which is the failure §0.1 forbids ("don't generate a graph
for generating a graph"). The floor is still nearly double where it started (0.17), so it binds; it just
does not dictate. No subject prints a gap: CS 52%, Physics 40%, Maths 23%, BM 21%, against a 15% target,
and fifteen plain-text items of headroom remain (114/356 = 32.02% passes, 114/357 = 31.93% fails)."""))

EDITS.append(("PLAN.md",
"""- **Priority-3 ("stretch") tail:** optional deeper items beyond the must/should nodes — open when there is""",
"""- **Batch 33 — DONE (2 items, 339 → 341; the first wave written entirely under §0).**
  - **The briefs came from three different gaps at once.** Physics Paper 1A's ledger row (§4.6) lists
    "thermal physics" among the approaches P1A has never used — its 19 clusters are rigid-body,
    circuits, photons, relativity, Doppler and fields. Maths node **1.15 (proof by induction)** carries
    five items and not one figure, and it is the only sub-topic in the bank whose natural statement is
    a drawing. And CS Paper 1 Section A still holds 245 of the paper's marks against Section B's 382,
    where the guide gives Section A 56 of 80 — so the next CS item must go there.
  - **`PHYS-B.4-601` (P1A, five MCQs, d4, `binding_constraint`)** is adapted from a named question in
    another system: the NEET-style "two identical samples of a gas expand, one isothermally and one
    adiabatically — in which is the work greater?", found by search on 2026-09-24 and recorded in
    `provenance` with what changed. The source asks one qualitative question; here the given is reduced
    to *only the isothermal path drawn*, so the candidate must construct the adiabatic from the
    constraint $Q = 0$, and the cluster then asks for four consequences of the one idea — the work
    ordering, the final pressures ($0.500$ against $2^{-5/3} = 0.315$), the energy bookkeeping, the
    final temperature ($201.6$ K) and the ratio $W_A / |\\Delta U_B| = 1.25$. **Difficulty 4, not 5, by
    design**: Maths now sits at 49% on the difficulty-5 cap and Physics at 44%, and §0.2's answer to a
    crowded cap is a harder idea told with more scaffolding, not a bigger number.
  - **`MATH-1.15-701` (P1 Section B, 14 marks, d5, `exceptional_parameter`)** asks for induction
    applied to the regions cut by $n$ lines in general position — where the inductive step is not
    algebra but a claim about how a new line is divided by its distinct intersection points. That is
    the whole item: parts (c) and (d) then drop general position one way and then the other, and the
    student in (d) argues that a triple point must cost more because it destroys two intersections
    where a parallel pair destroys one. It does not. **Both cost exactly one region** — eleven becomes
    ten either way — because the induction counts distinct points *on the line being added*, and a
    triple point collapses two of them onto one place on one line. The formula for the general case is
    therefore fragile in a specific, countable way: $R_n = \\frac{n^2+n+2}{2} - p - t$.
  - **Three defects were caught before shipping, and each one became a check.**
    (1) The `C_p` distractor was written as 1.62; the assertion list computed $1844 / 2461 = 0.75$ and
    failed the item. This is the same species of error Batch 30 found in a shipped markscheme — prose
    naming a distractor its own arithmetic does not produce — and it is the first time the gate caught
    it *during* authoring rather than after. (2) The lines figure had only five of its six crossings
    inside the frame while the stem claimed general position, so the drawing contradicted the
    question; it is now built by a search over slope and offset combinations that accepts a
    configuration only when all six intersections lie inside the box and are at least 45 px apart, and
    the chosen arrangement separates them by 48 px. (3) **The figure's caption stated the eleven
    regions that part (a) asks the candidate to count** — "they divide the plane into eleven parts,
    which the candidate is asked to count rather than to be told", a sentence that leaks the answer and
    then claims credit for not doing so. The leak lint had only ever looked at `<text>` nodes inside
    the SVG; it now checks the caption too, because a caption is part of the figure.
  - **Numbers after the wave.** 341 items — Maths 138 / 1967 marks, Physics 97 / 1149, CS 67 / 997,
    BM SL 39 / 563; 4676 marks. Difficulty 5 / 186 / 150. d5 shares: Maths **49%** (at the cap — the
    next Maths wave must be written at d4), Physics 44%, CS 46%, BM 23%. Evidence 256 / 341,
    `difficulty 5 with no evidence` **0**, `labels the evidence does not permit` **0**, all 13 levers in
    use. Assertions 3981. Figures 114 / 341 = 33%. Sourcing 126 items outside `original`, including the
    first `other`-family entry from the Indian systems. `validate.py` 0 failures / 179 warnings,
    `difficulty_audit --check` exit 0.
- **Priority-3 ("stretch") tail:** optional deeper items beyond the must/should nodes — open when there is"""))

EDITS.append(("README.md",
"""| Math AA HL | 2021 (runs to Nov 2028) | 137 | 83 / 83 (100%) |
| Physics HL | 2025 | 96 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 67 | 25 / 25 (100%) |
| Business Management SL | 2024 | 39 | 34 / 34 (100%) |
| **Total** | | **339** | **166 / 166 (100%)** |""",
"""| Math AA HL | 2021 (runs to Nov 2028) | 138 | 83 / 83 (100%) |
| Physics HL | 2025 | 97 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 67 | 25 / 25 (100%) |
| Business Management SL | 2024 | 39 | 34 / 34 (100%) |
| **Total** | | **341** | **166 / 166 (100%)** |"""))

EDITS.append(("README.md",
"""All 339 items are difficulty 3–5 (**5 at difficulty 3, 185 at difficulty 4, 149 at difficulty 5**), and
pass `validate.py`
with **0 failures**.""",
"""All 341 items are difficulty 3–5 (**5 at difficulty 3, 186 at difficulty 4, 150 at difficulty 5**), and
pass `validate.py`
with **0 failures**."""))

EDITS.append(("README.md",
"""| items with evidence for the label | **254 / 339** | 0 / 172 |""",
"""| items with evidence for the label | **256 / 341** | 0 / 172 |"""))

EDITS.append(("README.md",
"""Every item carries a `verification.assertions` list — **3957 machine-checked assertions** in total — so
the arithmetic in every answer is re-derived by the validator on each run, not merely asserted by the
author. **112 items are figure-bearing (33%)**, with the figure inlined into `question.figure` so a page
renders identically on `file://` and over HTTP.""",
"""Every item carries a `verification.assertions` list — **3981 machine-checked assertions** in total — so
the arithmetic in every answer is re-derived by the validator on each run, not merely asserted by the
author. **114 items are figure-bearing (33%)**, with the figure inlined into `question.figure` so a page
renders identically on `file://` and over HTTP."""))

EDITS.append(("README.md",
"""**Sourcing is recorded, not claimed.** 125 items are drawn from other syllabuses""",
"""**Sourcing is recorded, not claimed.** 126 items are drawn from other syllabuses"""))

failures, cache = [], {}
for path, old, new in EDITS:
    text = cache.get(path) or io.open(path, encoding="utf-8").read()
    n = text.count(old)
    if n != 1:
        failures.append("%s: anchor matched %d times -- %.70s" % (path, n, old.replace("\n", " ")))
        continue
    cache[path] = text.replace(old, new)
if failures:
    print("\n".join(failures))
    sys.exit("aborted, nothing written")
for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)
    print("updated", path)
