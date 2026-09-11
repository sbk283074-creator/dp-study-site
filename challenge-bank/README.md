# IB Challenge Bank

A small, hard, **original** question bank for four IB subjects, pinned to the guides a **May 2028**
candidate actually sits. It is the deliberate opposite of the 9,969-question retrieval bank: instead of
covering everything shallowly, it covers the highest-value nodes with items that are difficult by
design and provably not copied.

**Line-up:** Mathematics AA HL · Physics HL · Computer Science HL · Business Management SL.

- Full design rationale and cohort pinning: [`PLAN.md`](PLAN.md)
- The authoring contract every item must satisfy: [`STANDARD.md`](STANDARD.md)

---

## Current state

| Subject | Guide in force | Questions | Nodes covered |
|---|---|---:|---:|
| Math AA HL | 2021 (runs to Nov 2028) | 20 | 35 / 83 (42%) |
| Physics HL | 2025 | 19 | 24 / 24 (100%) |
| Computer Science HL | 2027 (new Theme A/B) | 14 | 25 / 25 (100%) |
| Business Management SL | 2024 | 17 | 34 / 34 (100%) |
| **Total** | | **70** | **118 / 166 (71%)** |

**Every priority-1 ("must-cover") node is done** — Maths 32/32, Physics 24/24, CS 25/25 and BM 26/26,
plus all 8 BM Toolkit nodes. The 48 nodes still open are priority-2 ("should") maths topics, which the
brief orders after every must-cover node.

All 70 items are `published`, difficulty 4–5 (49 at difficulty 4, 21 at difficulty 5), and pass
`validate.py --strict` with **0 failures and 0 warnings**. The originality gate is clean: **0 items
above threshold**, highest external score 0.048 and highest internal score 0.026 (limits 0.35 / 0.25).

Every item carries a `verification.assertions` list — **680 machine-checked assertions** in total — so
the arithmetic in every answer is re-derived by the validator on each run, not merely asserted by the
author.

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
    similarity_check.py     the originality gate (12,796-item corpus + all internal pairs)
    coverage.py             the gap list that the next batch is drawn from
    fix_json.py             repairs stray backslashes and HTML entities
    ship.py                 runs the whole pipeline in one command
    extract_syllabus.py     rebuilds tools/syllabus.json from the guide PDFs
    syllabus.json           166 syllabus nodes, the validator's reference map
  site/                     generated output (committed, so it serves from Pages or file://)
    index.html              home: cohort note, difficulty legend, subject cards
    <subject>/index.html    topic list with filters (topic, paper, difficulty, command term)
    q/<id>.html             one page per question, with collapsed answer / markscheme / why-it's-hard
    papers/<subject>-paper.html     printable question paper (no answers printed)
    papers/<subject>-answers.html   matching answer booklet (answers + markscheme notes)
    assets/                 local CSS + JS; MathJax is loaded from CDN with a local fallback
  export/<subject>.json     the same questions in the shape backend/src/import.js accepts
```

`site/` is committed on purpose so the folder can be served straight from GitHub Pages or opened
from `file://`. Data is loaded as JS globals rather than via `fetch()`, because `fetch()` is blocked
on `file://`.

---

## Build

```bash
cd challenge-bank

python3 tools/ship.py                  # repair -> build -> validate -> originality -> rebuild
python3 tools/ship.py --skip-similarity  # skip the slow 12,796-item scan while drafting
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
python3 tools/similarity_check.py --write   # originality gate, record scores in data/
python3 tools/coverage.py --next 12     # the brief for the next batch
```

---

## How to author a batch

The order matters — writing the question before knowing its lever produces a reskin.

1. **Brief.** `python3 tools/coverage.py --next 12` returns the gap list. A batch takes its targets
   from the top of that list; it does not start from whatever topic is easiest.
2. **Choose the lever first.** Name the mechanism before writing anything. A lever is something the
   student must *notice, reject or invert* — not "it has several parts". See STANDARD.md §5.1.
3. **Design the arc.** Parts interlock: the answer to (a) is needed for (b), and (c) is where the
   lever bites.
4. **Write the answer as a markscheme**, annotating every award `(M1)(A1)(R1)(AG)` at the point it is
   earned.
5. **Write `markscheme_notes`** — alternatives, condonations, follow-through, what forfeits a mark.
6. **Write `explanation`** — the insight, why it is hard, and the classic wrong turns.
7. **Add assertions** and a one-line `verification.method`.
8. **Gate it.** New items are `draft` until the gates pass, then `published`.

One file per batch per subject: `data/<subject>/batchN.json`. Nothing ships at difficulty 1–2, nothing
ships below the mark floor, and nothing ships without a passing similarity score.

### The two gates

| Gate | Command | Rejects |
|---|---|---|
| Quality | `tools/validate.py --strict` | difficulty 1–2, below the marks floor, part marks that do not sum to `marks`, thin fields, missing markscheme annotations, failed assertions |
| Originality | `tools/similarity_check.py` | ≥ 0.35 vs the external corpus (same subject), ≥ 0.25 vs any other item in this bank |

The originality gate is measured, not asserted: `tools/similarity_check.py` scores every item against
9,969 past-paper items, 46 un-imported generated batches, and every other question in this bank, using
word-level 5-gram Jaccard over LaTeX-stripped text. Forbidden moves are number-swap, name-swap,
unit-swap, sign-flip, part-reordering and notation change — if a source inspired an item,
`provenance.inspired_by` names it and `provenance.adaptation` says what changed.

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
