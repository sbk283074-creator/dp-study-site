# IB Challenge Bank

A small, hard, **original** question bank for four IB subjects, pinned to the guides a **May 2028**
candidate actually sits. It is the deliberate opposite of the 17,439-question retrieval bank: instead of
covering everything shallowly, it covers the highest-value nodes with items that are difficult by
design and provably not copied.

**Line-up:** Mathematics AA HL · Physics HL · Computer Science HL · Business Management SL.

- Full design rationale and cohort pinning: [`PLAN.md`](PLAN.md)
- The authoring contract every item must satisfy: [`STANDARD.md`](STANDARD.md)

---

## Current state

| Subject | Guide in force | Questions | Nodes covered |
|---|---|---:|---:|
| Math AA HL | 2021 (runs to Nov 2028) | 139 | 83 / 83 (100%) |
| Physics HL | 2025 | 98 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 69 | 25 / 25 (100%) |
| Business Management SL | 2024 | 39 | 34 / 34 (100%) |
| **Total** | | **345** | **166 / 166 (100%)** |

**Every priority-1 ("must-cover") and priority-2 ("should-cover") node is done** — Maths 32/32 + 51/51,
Physics 24/24, CS 25/25, BM 26/26 + 8/8 Toolkit. The bank covers **all 166 syllabus nodes** across the
four subjects; the only remaining work is the optional priority-3 ("stretch") tail.

All 345 items are difficulty 3–5 (**5 at difficulty 3, 187 at difficulty 4, 153 at
difficulty 5**), and pass `validate.py`
with **0 failures**. The originality gate is clean: **0 items above threshold**, highest external score
0.090, highest internal score 0.073 and highest approach score 0.366 (limits 0.35 / 0.25 / 0.50). The
approach maximum is `MATH-AHL1.11-201` against `MATH-AHL1.11-001`, two items on the same node that share
the partial-fractions-then-telescoping method — the gate judges the method different enough, and the two
are different questions with different answers (¾ against ¼).

Every item carries a `verification.assertions` list — **4038 machine-checked assertions** in total — so
the arithmetic in every answer is re-derived by the validator on each run, not merely asserted by the
author. **116 items are figure-bearing (34%)**, with the figure inlined into `question.figure` so a page
renders identically on `file://` and over HTTP.

**The figures are hand-drawn, and the gate enforces it.** 104 of the 110 are raw SVG and the other six are
`<table>` and `<pre>` blocks, all of them emitted by a plain-Python string builder — some in
`tools/make_figures.py`, which writes the named set in
`data/_figures.json`, and the rest inline in the batch generator that authored the item — with no
charting library, no plotting package and no image model anywhere in the chain. That is not a style
preference: `validate.py` rejects the fingerprints of all of them
(`<canvas`, `plotly`, `matplotlib`, `chart.js`, `highcharts`, `echarts`, `vega`, `bokeh`, `data:image/`),
so an item cannot smuggle in a generated or rasterised picture. The newest figures go further and sample
their own curve from the same expression the markscheme integrates, so the picture and the answer cannot
drift apart: Batch 23's two unbounded tails are plotted from `1/x**2` and `1/sqrt(x)`, the very
integrands whose antiderivatives the answer evaluates.
Coverage is tracked as a **ratchet**: `difficulty_audit.py` holds a bank-wide floor
(`FIGURE_COVERAGE_FLOOR`, now **0.32**) that may rise but may never fall, so a later batch cannot add
text-only items and let the share sag back. Batch 26 raised it from 0.25 to 0.27; Batch 27 to 0.28;
Batch 28 to 0.29, because all five of its items carry a hand-authored figure, which moved coverage to
94/320 = 29.4%; Batch 29 to **0.30**, because four of its five do, which moved coverage to
98/325 = 30.2%; Batch 30 to **0.31**, because **all six** of its items do, which moved coverage to
104/331 = 31.4%; and Batch 31 to **0.32**, because **all six** of its items do again, which moved coverage
to 110/337 = 32.6%. That leaves
**6 non-figure items of headroom** (110/343 = 32.07% still passes; 110/344 = 31.98% fails), so a
plain-text batch is effectively ruled out — the ratchet has reached the point where it forces the issue
rather than merely encouraging it. Batches 27 and 28 were both aimed by reading the per-subject column
rather than the gap line, which never prints because no subject is below target. Batch 28 went further
and chose its five items by **paper structure**: CS P1 Section A carries 56 of that paper's 80 marks, but
it held only 12 of the bank's 44 CS P1 items, and five Theme A nodes — A1.4, A2.4, A3.3, A3.4 and A4.4 —
had no Section A item at all. Batch 28 fills exactly those five, taking Section A to **17 of 49**, the
number of Theme A nodes represented in Section A from 7 to 12, and CS's figure share from 43% to **48%**.
Batch 29 read the same column one level down and found the **component** rather than the subject: Physics
P1A held 14 MCQ clusters carrying 70 of the bank's 1131 Physics marks — 6% — and only **one** of those 14
carried a figure, so the most graphic component of the real paper was the least graphic in the bank. It
adds five five-mark clusters on the five Physics nodes that had no P1A item at all (A.3, B.3, C.1, C.4,
E.3), taking P1A from 14 clusters to 19 and the MCQ figure share from **1/14 to 5/19**. Batch 30 applied
the same test to Maths and found the sharpest version of it yet: **Section A is about half the marks of
both Paper 1 and Paper 2**, but the bank held only **5% of P1's marks and 6% of P2's** there, so Maths was
a bank of extended-response questions almost end to end. Its six items are short-response Section A
questions on nodes that had no figure, taking P1 Section A from 7 items to 10 (5% → 7% of P1's marks) and
P2 Section A from 2 to 5 (6% → 9%), and Maths's figure share from **18% to 22%**.
The per-subject companion
(`FIGURE_SUBJECT_TARGET = 0.15`) is *reported* rather than enforced, and no subject prints a gap:
**CS 48%, Physics 39%, Maths 22%, BM 21%**.

**Sourcing is recorded, not claimed.** 128 items are drawn from other syllabuses — 高考, 强基, 竞赛,
A-Level, Further Maths, AP, 新加坡 A-Level, four from IB itself, and six recorded as `other` — and each names
`provenance.resource_origin` and
`provenance.adaptation`.
Adaptation means at least two of context, structure, given-vs-asked and reasoning chain change, so the
difficulty is carried by the rewrite rather than borrowed from a harder syllabus's content.

### The difficulty label is measured, not declared

From 2026-09-13 every item must **earn** its difficulty label with a `difficulty_evidence` block naming
the lever, the first move a prepared student makes, the exact step where that move breaks, and the wrong
answer it yields instead. `tools/difficulty_audit.py` then checks the claims *together* — the thing
`validate.py` structurally cannot see.

What the audit reports today:

| | now | at the 2026-09-13 baseline |
|---|---|---|
| items with evidence for the label | **260 / 345** | 0 / 172 |
| difficulty 5 with no evidence | **0** | 79 |
| labels the evidence does not permit | **0** | — |
| items claiming difficulty 5 | 44% | 46% |
| items claiming difficulty 3 | **1%** | 0% |

The evidence row is now the story, and it is the intended one. What changed on 2026-09-13 is not the
distribution but the fact that the bank now *states its backlog as a number* instead of passing every
per-item rule while telling the student nothing. Evidence was then backfilled subject by subject, by
reading each item — **never mass-generated**, which would reproduce the exact defect. The whole
difficulty-5 backlog has since been cleared: **no item in the bank claims difficulty 5 without
evidence.** 85 items still carry no `difficulty_evidence` at all, but every one of them is a
difficulty-4 claim, so the audit reports them as a backlog rather than as an unbacked
top-tier label.

**Clearing it was not a transcription exercise.** The 79 items were read one at a time, and reading them
produced five label corrections in the direction §4.7 asks for — down, never up:

| item | was | now | why the evidence does not permit 5 |
|---|---:|---:|---|
| `MATH-P3-010` | 5 | 4 | the heaviest part is the first (`5, 4, 4, 3`), so the arc test scores 0 and the item tops out at 7/9 |
| `MATH-AHL5.9-001` | 5 | 4 | a single clean idea — split the journey at the rest times — rather than a complete defeat |
| `MATH-AHL5.10-001` | 5 | 3 | the author's own note gives the trap as a sign slip on the cosine term; a slip is not a lever (§5.2) |
| `MATH-AHL5.11-001` | 5 | 4 | a single clean idea — establish which curve is on top — and a flat four-part arc |
| `PHYS-E.2-101` | 5 | 4 | the mechanism names units rather than an idea: *"a student who knows the physics but loses the unit loses the mark"* |

Five corrections in total, all downwards, out of 79 items read — and the remaining 74 kept their label
because the mechanism named something the candidate has to *notice, reject or invert* rather than merely
get right. `labels the evidence does not permit` stayed at **0** throughout, which is the check that
would have caught a correction that went the wrong way.

**The 3–5 range is now in use.** R2 — *"no item claims difficulty 3 — the 3-5 scale has collapsed to two
points"* — was the last calibration debt, and it is paid: **five** items now claim difficulty 3 — Maths
(`MATH-AHL2.15-201` and, from the backlog pass, `MATH-AHL5.10-001`), CS (`CS-B2.2-201`), BM
(`BM-4.1-201`) and, since Batch 22b, Physics (`PHYS-A.3-201`). The audit prints `calibration OK` and `--check --strict`, which fails on a debt as well
as on a regression, exits 0 for the first time. **Physics's single difficulty-3 item is worth a note**,
because the batch that recorded the gap also argued it should stay open: *"every Physics node whose
natural idea is a single clean lever — orbital energy in D.1, the two-stage Doppler shift in C.5, the end
correction in C.4, the massive-pulley tensions in A.2/A.4, the Carnot comparison in B.4 — already carries
an item that uses it, so a Physics difficulty-3 item needs a new design rather than a slot filled."* The
item that closed it is on **A.3**, a node with no such incumbent, and it is a genuinely single-lever
question rather than a relabelled hard one — which is the distinction the earlier note was protecting.

**The rubric score is a documentation gate, not a difficulty meter, and this is worth knowing before
trying.** Measured across all 252 evidenced items: **232 score 9/9**, 19 score 8/9 and one scores 7/9 —
and 8 of 9 is already enough for the top label, so a score below 9 is not by itself a demotion. What the
score tests is whether the three evidence statements are present, long enough and mutually distinct, and
whether the arc and assertion-density tests hold; it does not measure how many *ideas* an item contains.
So a 9/9 item may honestly declare 3, and the five difficulty-3 items do. The only alternative would be
to hollow out an evidence field to drag the score down to 4–6, which would make the claim *less*
falsifiable, and §2.2 exists precisely to stop that. A difficulty-3 claim therefore rests on §2.3's own
test — "a single clean lever rather than a complete defeat" — and is written so that once the candidate
has seen the lever the rest is routine.

The Physics difficulty-5 share was the other breach, and it has been paid down the intended way — add d4
items rather than relabel earned d5 items. It stood at **62% at the baseline**, rose to **63%** in Batch
13 when two Physics items shipped at difficulty 5, fell to **61%** in Batch 14 when both new Physics
items were written at difficulty 4 with heavier `Show that` scaffolding, fell again to **56%** in Batch
15, and reached **49%** in Batch 17 when all eight new Physics items were designed at difficulty 4 from
the outset. **Physics HL is now inside the 50% cap and the debt is cleared**, and Batch 19's four Physics
items were again all written at difficulty 4, taking it down again to **46%**. The paydown was therefore
worked off rather than relabelled, and with Physics inside the cap the self-imposed rule lapsed: **Batch
20 adds two Physics items at difficulty 5 and two at difficulty 4, taking the share to 47%**, still
inside the cap and still below the 62% baseline. Batches 22 and 22b then added nine Physics items — six at
difficulty 4 and three at difficulty 5 — landing at **44%**; Batch 23 then added four Physics items, all at difficulty 4, for **45%**. The backlog pass then moved one further Physics item — `PHYS-E.2-101`, a photoelectric MCQ cluster whose own mechanism names units rather than an idea — from 5 down to 4, taking the share to **44%**. Batch 26 then added two Physics items — one at difficulty
5 and one at difficulty 4, both on the E.2 strand — leaving the share at
**44%**, unchanged to the nearest point because the batch added d4 and d5 in step. The calibration gate is checked against
the baseline on
every run, so a share that rose past 49% would stop the pipeline rather than pass quietly.

Batch 15 also closed the last gap in the lever taxonomy: **all 13 lever types are in use**, and the
largest single share is **15%** of evidenced items (`non_governing_variable`, 37 of 252), so the bank is
no longer one trick in different clothes. That share barely moved while the evidenced set grew from
**38 items to 252** — it was 18% of those 38, measured at the Batch 15 commit — which is the useful
reading: the backfill was spread across the taxonomy rather than concentrated in the levers that were
already busy. Batch 28 used five distinct levers (`derived_limit`, `wrong_design_cost`,
`seeded_anomaly`, `partial_cancellation`, `implicit_dependence`), one per item, so no share moved by
more than a point. Batch 29 used five more, again one per item, and took `variable_swap` — the thinnest
lever in the bank, at 5 items before the wave — to 6; here too no share moved by more than a point either
way. Batches 28 and 29 added no Maths items, and Batch 28 added no Physics items, so the Physics share
above is unchanged at 44%: Batch 29's three difficulty-4 and two difficulty-5 Physics items leave it
where it was. Batch 30 used six more, again one per item (`exceptional_parameter`, `aggregate_recovery`,
`decoy_technique`, `non_obvious_tool`, `non_governing_variable`, `implicit_dependence`), and its six
difficulty-5 Maths items moved the Maths share by three points, from 45% to 48% — still inside the 50%
cap, which the audit checks on every run, but the closest any subject has come to it.

`tools/prove_difficulty_gates.py` guards the gates themselves: it injects one defect at a time — an
invented `lever_type`, a `wrong_answer` that restates `naive_path`, a difficulty 5 with no evidence — and
fails if any of them gets through.

---

## Layout

```
challenge-bank/
  PLAN.md                   design document: scope, cohort pinning, sources, milestones
  STANDARD.md               the authoring contract (quality, length, format, pipeline)
  README.md                 this file — build + contribution notes
  build.py                  the only build script: data/*.json -> site/ and export/
  data/
    _TEMPLATE.json          the JSON skeleton (ignored by the tools: leading underscore)
    math-aa-hl/*.json       one file per batch, plus topic-specific single-item files
    physics-hl/*.json
    computer-science-hl/*.json
    business-management-sl/*.json
  tools/
    validate.py             the quality gate (difficulty, marks, parts, lengths, assertions)
    difficulty_audit.py     the calibration gate: does the label discriminate, and is it earned?
    prove_difficulty_gates.py  regression test for the gates themselves
    similarity_check.py     the originality gate (20,266-item corpus + all internal pairs)
    coverage.py             the gap list that the next batch is drawn from
    fix_json.py             repairs stray backslashes and HTML entities
    ship.py                 runs the whole pipeline in one command
    backfill_source_family.py  one-time migration recording provenance.source_family
    normalise_topics.py     one-time migration collapsing the drifted `topic` labels
    extract_syllabus.py     rebuilds tools/syllabus.json from the guide PDFs
    syllabus.json           166 syllabus nodes, the validator's reference map
  site/                     generated output (committed, so it serves from Pages or file://)
    index.html              home: cohort note, difficulty legend, subject cards
    <subject>/index.html    every question as a card, filterable by topic, paper, difficulty and progress
    q/<id>.html             one page per question, with collapsed answer / markscheme / why-it's-hard
    papers/<subject>-paper.html     printable question paper (no answers printed)
    papers/<subject>-answers.html   matching answer booklet (answers + markscheme notes)
    papers/builder.html     assemble a custom timed paper from any selection of items
    assets/                 local CSS + JS; MathJax is loaded from CDN with a local fallback
  export/<subject>.json     the same questions in the shape backend/src/import.js accepts
```

**MCQ options are printed on every surface.** The four choices of a Paper 1A cluster live in
`parts[].options`, and until 2026-09-23 `build.py` rendered them nowhere — a candidate reading the
printable Physics paper met "Which statement is correct?" with no statements, on 95 of the questions.
`options_html` now renders them in the question page, the custom builder and the paper, and
`options_scheme_html` renders them in the markscheme with the keyed option badged and each
distractor's `rationale` printed under it, because for an MCQ the per-option rationale *is* the
markscheme. The label printed is the stored `label`, never the list position, so the letter a student
reads is the letter `validate.py` checked.

`site/` is committed on purpose so the folder can be served straight from GitHub Pages or opened
from `file://`. Data is loaded as JS globals rather than via `fetch()`, because `fetch()` is blocked
on `file://`.

---

## Build

```bash
cd challenge-bank

python3 tools/ship.py                  # repair -> build -> validate -> originality -> rebuild
python3 tools/ship.py --skip-similarity  # skip the slow 20,266-item scan while drafting
```

`ship.py` stops at the first failing stage and exits non-zero, so it can be run at the end of every
batch without reading the output unless something breaks.

Useful single stages:

```bash
python3 build.py                        # regenerate site/ and export/ from data/
python3 build.py --check                # validate only, write nothing
python3 tools/validate.py               # the quality gate
python3 tools/validate.py --strict      # warnings count as failures (use for new batches)
python3 tools/validate.py --subject "Physics HL"
python3 tools/validate.py --stats       # length distribution + subject medians
python3 tools/difficulty_audit.py       # the difficulty report: distribution, levers, backlog
python3 tools/difficulty_audit.py --check   # exit non-zero only if the bank regressed
python3 tools/difficulty_audit.py --check --strict   # also fail on the outstanding debt
python3 tools/difficulty_audit.py --id MATH-AHL5.11-101   # score one item, to choose its label
python3 tools/prove_difficulty_gates.py # prove the gates still reject what they should
python3 tools/similarity_check.py --write   # originality gate, record scores in data/
python3 tools/coverage.py --next 12     # the brief for the next batch
```

---

## How to author a batch

The order matters — writing the question before knowing its lever produces a reskin.

1. **Brief.** `python3 tools/coverage.py --next 12` returns the gap list. A batch takes its targets
   from the top of that list; it does not start from whatever topic is easiest.
2. **Choose the lever first.** Name the mechanism before writing anything, and pick its `lever_type` from
   the taxonomy in STANDARD.md §2.4 at the same time. A lever is something the student must *notice,
   reject or invert* — not "it has several parts". See STANDARD.md §5.1.
3. **Write the difficulty evidence before the question.** `naive_path` is the first thing a prepared
   student tries; `failure_point` is the exact step where it breaks; `wrong_answer` is what that path
   yields instead. If you cannot state all three, you do not yet have a hard question — you have a long
   one, and the rubric will score it accordingly.
4. **Design the arc.** Parts interlock: the answer to (a) is needed for (b), and (c) is where the lever
   bites. The heaviest part must not be the first.
5. **Write the answer as a markscheme**, annotating every award `(M1)(A1)(R1)(AG)` at the point it is
   earned.
6. **Write `markscheme_notes`** — alternatives, condonations, follow-through, what forfeits a mark.
7. **Write `explanation`** — the insight, why it is hard, and the classic wrong turns.
8. **Add assertions** and a one-line `verification.method`.
9. **Record the sourcing.** `provenance.source_family` is one of the closed list in STANDARD.md §4.5; if
   it is anything other than `original`, `provenance.resource_origin` must name the source. Cross-syllabus
   material (A-Level, AP, 高考, 强基, 竞赛) is encouraged — but the difficulty must survive the adaptation,
   and difficulty is never borrowed from a harder syllabus's *content* that this one does not examine.
10. **Score it before labelling it.** `python3 tools/difficulty_audit.py --id <ID>` prints the rubric
    breakdown; label it no higher than the score permits, and never higher than 4 or 5 unless all three
    evidence fields are substantive and mutually distinct. **Lower the label, not the score.**
11. **Gate it.** New items are `draft` until the gates pass, then `published`.

One file per batch per subject: `data/<subject>/batchN.json`. Nothing ships at difficulty 1–2, nothing
ships below the mark floor, and nothing ships without a passing similarity score.

### The three gates

| Gate | Command | Rejects |
|---|---|---|
| Quality | `tools/validate.py --strict` | difficulty 1–2, below the marks floor, part marks that do not sum to `marks`, thin fields, missing markscheme annotations, failed assertions, an unearned difficulty label, a `lever_type` outside the taxonomy, an unrecorded or unattributable `source_family`, a `question_type` the declared paper does not contain, a `section` the declared paper does not have, a `technology` value the paper's own policy rules out, a `level` that disagrees with the subject, a `language` outside the closed set |
| Calibration | `tools/difficulty_audit.py --check` | a subject with > 50% of items at difficulty 5, a bank that never uses difficulty 3, evidence coverage below the ratchet floor |
| Originality | `tools/similarity_check.py` | ≥ 0.35 vs the external corpus (same subject), ≥ 0.25 vs any other item in this bank, ≥ 0.50 on the `solution_skeleton` approach gate |

The quality gate checks that a difficulty claim was *made*. The calibration gate checks whether the
bank's claims, taken together, are *credible* — a bank where 46% of items claim difficulty 5 and none
claim 3 passes every per-item rule while telling the student nothing.

The originality gate is measured, not asserted: `tools/similarity_check.py` scores every item against
the **20,266-item external corpus** (past-paper rows, un-imported generated batches and every other
question in this bank), using word-level 5-gram Jaccard over LaTeX-stripped text, and separately runs
an **approach gate** over the declared `solution_skeleton` (reject at 0.50). Forbidden moves are
number-swap, name-swap, unit-swap, sign-flip, part-reordering and notation change — if a source
inspired an item, `provenance.inspired_by` names it and `provenance.adaptation` says what changed.

---

## Notes

- **Cohort pinning is not optional.** Math AA HL sits the 2021 guide, Physics HL the 2025 guide, CS HL
  the 2027 guide (new Theme A/B — legacy CS papers are invalid), and BM SL the 2024 guide (no P3 at SL;
  a strict HL-only exclusion list applies, and only the eight SL Toolkit tools may be used).
- **BM SL difficulty cannot come from harder content.** It comes from messy or conflicting quantitative
  data, stakeholder criteria that genuinely clash, a decision with no clean answer, and cases where the
  obvious Toolkit tool is the wrong one.
- **No HL-only content in BM SL.** The exclusion list is in STANDARD.md §4.1 and is swept for by hand
  and recorded in each item's `verification.method`.
