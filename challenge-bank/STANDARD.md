# The Challenge Bank standard

This document pins down what a question **is** in this bank, and how a batch is produced. It exists
so that expansion is mechanical: write to this contract, run `python3 tools/ship.py`, and anything
that passes is publishable. Nothing here may be relaxed to make a question easier to write.

It does not shorten a question. The authoring cost per item is unchanged — a full answer, markscheme
and explanation has to be written either way. What it removes is the **re-reading** cost: the contract
is the checklist, the tools are the auditor, and a batch can be written and shipped without a separate
review pass over each item.

---

## 1. Scope

Four subjects, pinned to the guides a May 2028 candidate actually sits:

| Subject | Guide | Papers |
|---|---|---|
| Math AA HL | 2021 (runs to Nov 2028) | P1 120 min/110, no tech · P2 120 min/110, tech · P3 60 min/55, two extended problems |
| Physics HL | 2025 | P1 2 h/60 (1A 40 MCQ + 1B 20 data-based) · P2 2 h30/90 |
| Computer Science HL | 2027 (new Theme A/B) | P1 2 h/80 (Theme A + pre-seen case study) · P2 2 h/80 (Theme B) |
| Business Management SL | 2024 | P1 1 h30/30 (pre-released statement + unseen case) · P2 1 h30/40 (quantitative) |

Topic maps live in `tools/syllabus.json`, generated from the guide PDFs by `tools/extract_syllabus.py`.
**166 nodes**: Maths 83, Physics 24, CS 25, BM SL 34. The validator rejects any syllabus code that is
not in that map.

---

## 2. The quality contract

| Property | Rule | Enforced by |
|---|---|---|
| Originality | 5-gram Jaccard < 0.35 vs the 12,796-item external corpus | `similarity_check.py` (fail) |
| Internal originality | < 0.25 vs every other question **in this bank** | `similarity_check.py` (fail) |
| Not a reskin | No number-swap, name-swap, unit-swap, part-reordering or notation change of any existing question | `provenance.adaptation` (fail if borrowed without a note) |
| Difficulty | 3, 4 or 5. Nothing ships at 1–2 | `validate.py` (fail) |
| Marks floor | Maths 6 (P3: 12) · Physics 6 · CS 6 · BM SL 10 | `validate.py` (fail) |
| Part count | Maths ≥ 3 · Physics ≥ 3 · CS ≥ 2 · BM SL ≥ 3 | `validate.py` (fail) |
| Named lever | One specific mechanism in `challenge_mechanism`, ≥ 10 words | `validate.py` (fail) |
| Real markscheme | Maths/physics answers carry `(M1)(A1)(R1)(AG)` at each award | `validate.py` (fail if zero) |
| Command terms | Recognised IB terms; marks matched to the demand of the term | `validate.py` (warn) |
| Verification | Method named; arithmetic re-checked by machine where numbers exist | `validate.py` (fail if no method) |

### 2.1 Command term discipline

Only recognised IB command terms appear (`validate.py` holds the list; `recommend` is permitted for BM).
Two coherence rules, because mismatches are the clearest sign a question was not thought through:

- **Recall terms do not carry big marks.** `State`, `List`, `Define`, `Label`, `Identify`, `Write down`
  — 3 marks or fewer.
- **Evaluative terms do not carry one mark.** `Explain`, `Analyse`, `Compare`, `Discuss` need ≥ 2;
  `Evaluate`, `Justify`, `To what extent` need ≥ 3.
- Every **BM SL** item must contain at least one AO3/AO4 term (analyse / evaluate / discuss / justify /
  to what extent). A BM question that only describes is not an IB question.

---

## 3. Length contract — floors, not targets

Calibrated against the published corpus (now 52 items). These are **absolute floors**: a new question
may not be materially thinner than the thinnest existing one in its subject.

| Subject | `answer` | `markscheme_notes` | `explanation` | total context¹ |
|---|---|---|---|---|
| Math AA HL | 190 | 125 | 195 | 30 |
| Physics HL | 155 | 125 | 205 | 100 |
| Computer Science HL | 440 | 125 | 200 | 140 |
| Business Management SL | 345 | 155 | 220 | 160 |

¹ *Total context* = stem + stimulus + all part texts, counted together. The floor is per-subject because
a terse maths question is normal while a thin BM stimulus is not.

On top of the floors, each field is compared against the **running subject median** and warned below
80% of it. That is what stops a whole batch of technically-compliant but noticeably thin questions from
quietly lowering the bar.

Words are counted after stripping LaTeX commands and delimiters, so `$x^2$` counts as one word, not six.

---

## 4. Format contract

Full skeleton: **`data/_TEMPLATE.json`** (ignored by the tools because of the leading underscore).

- **Required fields:** `id, subject, level, syllabus_ref, topic, subtopic, paper, marks, difficulty,
  challenge_mechanism, command_terms, question, parts, answer, markscheme_notes, explanation,
  provenance, originality, verification, status`.
- **`parts[]`:** each has `label` (a, b, c…), `marks`, `command_term`, `text`, ≥ 8 words. Part marks must
  sum **exactly** to `marks`.
- **IDs:** `MATH-<ref>-NNN`, `PHYS-<theme>-NNN`, `CS-<topic>-NNN`, `BM-<unit>-NNN`.
- **Maths and physics:** LaTeX in `$…$` or `$$…$$`, delimiters paired.
- **CS:** fenced code blocks; SQL keywords upper case.
- **BM SL:** stimulus as `{title, body, table}`; every figure in the stimulus must be used by at least
  one part. **No HL-only content** — see §4.1.
- **No HTML entities** (`&ndash;` and similar). Use the literal character; the renderer escapes `&`.
  `tools/fix_json.py` converts them automatically.
- **LaTeX backslashes must be doubled** in JSON. `\,` (thin space) is the usual offender; `fix_json.py`
  repairs it.

### 4.1 Business Management SL boundary

HL-only, therefore never appears: **2.5** (culture), **2.7** (industrial relations), **3.6** (efficiency
ratios), **3.9** (budgets), **4.3** (sales forecasting), **4.6** (international marketing), **5.3**
(lean/quality), **5.6**, **5.7**, **5.8**, **5.9**. Toolkit is the **eight SL tools** only — no Gantt,
Porter's generic strategies, Hofstede, force field, critical path, contribution, or linear regression.

BM difficulty therefore cannot come from harder content. It comes from: messy or conflicting
quantitative data, stakeholder criteria that genuinely clash, a decision with no clean answer, and
cases where the obvious Toolkit tool is the wrong one.

### 4.2 Verification assertions

`verification.assertions` is a list of Python expressions that must all be true, e.g.

```json
"assertions": ["approx(0.5 * 42164, 21082, 1e-3)", "pct(6.5, 6.47)"]
```

They are evaluated by `validate.py` in a restricted namespace (`math`, plus `G`, `g`, `c`, `e_charge`,
and the helpers `approx(a, b, tol)` and `pct(a, b)`). **Mandatory for every new maths and physics
question** — it is the only mechanical check that the arithmetic in the answer is right. All 70 items
in the bank now carry them (680 assertions in total), including the CS and BM items, where the check
is optional but has already repaid the cost: backfilling the original BM items exposed a €24 slip in
an expected-value difference and a volume gap quoted against the wrong price pair.

---

## 5. How to author one

The order matters. Writing the question before knowing its lever produces a reskin.

1. **Pick the node.** `python3 tools/coverage.py --next 12` gives the highest-priority gaps.
2. **Choose the lever first.** Name the mechanism before writing anything. A lever is something the
   student must *notice, reject or invert* — not "it has several parts".
3. **Design the arc.** Parts interlock: the answer to (a) is needed for (b), and (c) is where the lever
   bites. The last part should be where the marks are.
4. **Give the data a reason.** Numbers are chosen so the arithmetic comes out clean *only if* the
   reasoning is right.
5. **Write the answer as a markscheme**, annotating every award at the point it is earned.
6. **Write `markscheme_notes`** — alternatives, condonations, follow-through, what forfeits a mark.
7. **Write `explanation`** — the insight, why it is hard, and the classic wrong turns.
8. **Add assertions** and a one-line `verification.method`.

### 5.1 Lever banks

Legitimate ways to make an item hard, by subject:

- **Maths:** implicit dependence (solve for a quantity that appears inside its own operator) · swap the
  dependent variable · a parameter that behaves one way for every value except one · a quantity the
  student must construct before it can be used · a result that looks like it needs a technique and does
  not, or the reverse.
- **Physics:** a constraint that binds only in combination · two effects that partially cancel · a
  quantity that is *not* set by the variable the student reaches for · a limit or approximation that must
  be derived, not quoted · recovering two unknowns from two aggregate readings.
- **CS:** quantify the cost of the wrong design at a stated scale · a case where the "better" structure
  degenerates · a correctness bug that survives the obvious test · a design that is right technically and
  wrong ethically · constraints that conflict, so the answer is a trade-off with numbers attached.
- **BM SL:** two indicators that move in opposite directions · criteria that cannot both be satisfied ·
  the correct tool is not the obvious tool · a decision where the quantitative answer and the
  stakeholder answer disagree.

### 5.2 Forbidden moves

Number-swap, name-swap, unit-swap, sign-flip, part-reordering, notation change, or "same question in a
different scenario" of any question in the bank, in `app.db`, or in `generated/*.json`. If a source
inspired the item, `provenance.inspired_by` names it and `provenance.adaptation` says what changed —
at least two of {context, structure, what is given vs what is asked, the reasoning chain}.

---

## 6. The pipeline

```
write data/<subject>/<file>.json      to this contract, from data/_TEMPLATE.json
python3 tools/ship.py                 the whole thing, stops on first failure
```

`ship.py` runs, in order:

| Stage | Command | Does |
|---|---|---|
| 1. repair | `tools/fix_json.py` | doubles stray backslashes, converts HTML entities |
| 2. build | `build.py` | renders `site/` from `data/` |
| 3. quality gate | `tools/validate.py` | §2, §3, §4. **This is the gate.** |
| 4. originality gate | `tools/similarity_check.py --write` | 12,796 external + all internal pairs |
| 5. rebuild | `build.py` | re-renders so similarity scores appear in the metadata |

Useful variants:

```
python3 tools/validate.py --strict              # warnings count as failures (new batches)
python3 tools/validate.py --subject "Physics HL"
python3 tools/validate.py --stats               # length distribution + subject medians
python3 tools/coverage.py --next 12             # the batch brief
python3 tools/ship.py --skip-similarity         # stage 4 costs ~1 min; skip while drafting
```

Exit codes are non-zero on failure at any stage, so a batch can be shipped without reading the output
unless something breaks.

---

## 7. Expansion protocol

1. **Brief:** `coverage.py --next N` returns the gap list, ordered by priority then subject. A batch
   takes its targets from the top of that list; it does not start from whatever topic is easiest.
2. **Batch size:** as many as can be written well in one pass, typically 4–8. One file per batch per
   subject, `data/<subject>/batchN.json`.
3. **Gate:** `python3 tools/ship.py`. New batches are additionally run with `validate.py --strict`.
4. **Status:** new items are `draft` until the gates pass, then `published`.
5. **Re-brief:** coverage is re-measured after every batch; the next brief comes from the new gaps.

Current state: 70 questions · **118 / 166 nodes covered (71%)**, and **every priority-1 node is done** —
Maths 32/32 (35/83 overall), Physics 24/24 (complete), CS 25/25 (complete), BM 34/34 (complete,
including all 8 Toolkit nodes). All 70 are `published`, `validate.py --strict` reports 0 failures and
0 warnings, and all 70 items carry `verification.assertions` (680 assertions in total).
