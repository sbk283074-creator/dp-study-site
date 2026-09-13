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
| Originality | 5-gram Jaccard < 0.35 vs the 20,266-item external corpus | `similarity_check.py` (fail) |
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

Calibrated against the published corpus (now 164 items). These are **absolute floors**: a new question
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
question** — it is the only mechanical check that the arithmetic in the answer is right. All 164 items
in the bank now carry them (1652 assertions in total), including the CS and BM items, where the check
is optional but has already repaid the cost: backfilling the original BM items exposed a €24 slip in
an expected-value difference and a volume gap quoted against the wrong price pair.

### 4.3 Paper and question type

Topic coverage is complete: every question maps to a syllabus node and all 166 are covered. **Topic is
therefore no longer the axis a new batch should be planned on.** The live gaps are the paper a question
belongs to and the kind of question it is. Every new item must declare `question_type`, and
`validate.py` will reject a type that the declared paper does not contain.

| Subject | Paper | What that paper actually is |
|---|---|---|
| Physics HL | P1A | 40 multiple-choice, 1 mark each, 4 options, no negative marking |
| Physics HL | P1B | data-based: uncertainties, graphing, experimental critique (~20 marks) |
| Physics HL | P2 | short-answer and extended response, 90 marks, 2 h 30 |
| Maths AA HL | P1 / P2 | structured and extended response (P1 no GDC, P2 GDC), 110 marks each |
| Maths AA HL | P3 | HL-only inquiry/modelling, two extended problems, 55 marks, 1 h |
| CS HL | P1 / P2 | P1 structured; P2 case-study based, no code required |
| BM SL | P1 / P2 | P1 case study; P2 stimulus and data-response |

Physics has **no Paper 3** under the 2025 guide — the options were removed. Do not write one.

**MCQ rules.** Exactly four options labelled A–D, exactly one marked correct, one mark per question.
Every option, correct or not, needs a `rationale` of at least eight words that *names the error*: a
distractor with no stated purpose is noise, not a distractor. The four options should be the correct
route plus the three or four most predictable wrong ones — wrong part of a formula, an inverted ratio,
a unit slip, a quantity confused with its rate of change. An MCQ cluster is one bank item whose parts
are the individual questions; length floors scale with the cluster (45 words of answer per MCQ), so a
five-question cluster needs roughly 225 words of answer, not 45.

**Data-based rules.** Must carry a data table or a figure, and must exercise uncertainty, graphing or
experimental critique. Seed one genuine anomaly into the dataset and make the candidate find it, name a
plausible physical cause, and say what should have been done at the time — deleting a point after the
fact is not an answer. Generate the data in Python from the model, then round to the instrument
resolution, so the fit recovers the parameters you seeded.

**Solution skeleton.** Every new item carries `verification.solution_skeleton`: three to six short
steps naming the *method*, not the answer ("linearise by squaring and fit the gradient", not "find k").
This is what the originality gate compares — see §4.4. Make it specific to the physics or the
mathematics; two skeletons that both read "identify the model, solve, state the answer" will be
flagged as the same question, correctly.

### 4.4 Originality is about approach, not wording

Word-level n-gram overlap is the wrong measure and is no longer the one that matters. Two questions can
share almost no words and be the same question by method, and two can share nearly all their nouns and
be genuinely different. `similarity_check.py` therefore runs two gates:

- **lexical** (word 5-gram Jaccard; reject at 0.35 same subject, 0.25 within this bank) — catches
  copying;
- **approach** (structural match of the `solution_skeleton`; reject at **0.50**) — catches the same
  question wearing different words.

The approach gate is fuzzy at the token level: `expand`, `expands`, `expanding` and `expansion` land on
the same token, and stopwords are dropped, so a step described with a different part of speech still
matches. Calibration cases that the gate must get right:

| pair | lexical | approach | verdict |
|---|---|---|---|
| Maclaurin of e^(sin x) vs Taylor of e^(cos x) at 0 | 0.03 | 0.63 | same question — reject |
| flywheel by energy vs flywheel by angular impulse | 0.79 | 0.22 | different — allow |
| two half-life items, different wording | 0.00 | 0.66 | same question — reject |

The middle row is why the lexical gate alone is not enough: it would have rejected two questions that
have nothing in common but their subject matter. Only items that declare a skeleton take part in the
approach gate, so the pre-existing bank is unaffected.

**Practical consequence:** when planning a batch, check that no two items share a skeleton. Two
data-based Physics items both built on "linearise, fit, exclude the anomaly, evaluate" scored 0.31
against each other — under the threshold, but a warning that the next P1B items need deliberately
different treatments (residual analysis, log-log, area under a graph, comparison of two datasets).

### 4.5 Sourcing

Chinese material (高考压轴题, 强基计划 written tests, 数学/物理竞赛) is a good source of difficulty and
is encouraged. Adapt rather than translate: rebuild the context, convert to IB command terms and IB
mark-scheme conventions, enforce units and significant figures, and state the chain of reasoning the
markscheme will reward. Record what you borrowed in `provenance.resource_origin` and
`provenance.adaptation` — citing the origin is fine and useful. Difficulty must survive the adaptation;
if the hard step was an algebraic trick that IB does not examine, replace the trick rather than the
difficulty.

### 4.6 Approach ledger

The approach gate only knows about skeletons that exist. Keep this ledger current when adding a batch,
and read it before planning one — it is the only defence against a batch that passes the gate and is
still repetitive.

| paper / type | approaches already used | what to use next |
|---|---|---|
| Physics P1A | rigid-body rotation; induction; circuits; photons & photoelectric; **relativity (every distractor a Galilean answer)**; **Doppler (source-moves vs observer-moves pair on identical numbers)**; **fields (spurious algebraic root that fails the direction test)** | transverse waves; thermal physics; nuclear; a second relativity cluster on energy–momentum |
| Physics P1B | linearise T²–m then gradient; log–log for an exponent; trapezium integration of a tabulated non-linear force; form the invariant from each row and propagate uncertainty; **residual-pattern analysis + uncertainty budget (curvature is systematic)**; **reciprocal plot, intercept read as a zero error, two faults of different kinds**; **half-power width of a resonance curve → Q** | area under a graph; comparison of two datasets taken with different apparatus; log–log for a power law |
| Physics P2 | — | energy balance with an inverted parameter (done: greenhouse); selector-then-spectrometer chains; nuclear fuel-cycle arithmetic; rotational dynamics with a slipping constraint |
| Maths P3 | iterative root with a Pell invariant; difference-equation boundary-value problem; coupled ODE cascade; integral recurrence with a squeeze; generating-function counting; optimisation with a parameter range; binomial identities by coefficient extraction; exponential Diophantine by modular reduction; **inclusion–exclusion → recurrence → limit → rounding result (derangements)**; **roots of unity: factorise, cancel, substitute the excluded point** | Maclaurin solution of an ODE with no closed form; a graph-theoretic counting invariant; a probability problem whose answer is a named constant reached two ways |
| CS P1 (structured) | FDE cycle and CPU/GPU comparison; binary representation and overflow; scheduling; database design and SQL; NoSQL and warehousing; **cache hierarchy → Amdahl → clock scaling that fails**; **VLSM subnetting design with a boundary constraint**; **asymptotics vs constant factor, crossover computed** | translation (compiler vs interpreter, HL); ML preprocessing and validation; OOP design with multiple classes |
| CS P2 (case study) | binding-constraint architecture split; ADT selection against every operation; imbalanced-data metrics and governance; concurrency and deadlock; protocol design with a threat model; legacy-migration phasing; algorithmic fairness | distributed-system consistency; ML pipeline governance; a second security incident with a different failure class |
| BM P1 (case study) | ratio analysis → growth model choice; landed cost → working-capital and obsolescence effects | HR restructure with a motivation theory; market-entry with Ansoff plus STEEPLE |

Three rules keep the ledger honest. First, a new item in a row must differ from the entries already there
in *what the student has to decide*, not in the context it is dressed in. Second, the Physics P1B row
exists in its present form because the first two P1B items were both "linearise and fit"; if a row starts
to look like a list of the same verb, the next item has to change the verb. Third — and this is not
theoretical — backfilling skeletons onto the 164 legacy items immediately exposed
`MATH-AHL5.6-001`/`MATH-AHL5.8-001` at **0.467**, two "differentiate, set to zero, classify, evaluate"
questions on different functions that had been sitting in the bank as an apparent 0-failure state.
**Any legacy item without a skeleton is invisible to the approach gate.** Do not leave one that way.

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
| 4. originality gate | `tools/similarity_check.py --write` | 20,266 external + all internal pairs |
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

Current state: 164 questions · **166 / 166 nodes covered (100%)**, and **every priority-1 and
priority-2 node is done** — Maths 32/32 must + 51/51 should (83/83 overall), Physics 24/24 (complete),
CS 25/25 (complete), BM 26/26 must + 8/8 should (34/34 complete, including all 8 Toolkit nodes). All 164
are `published`, `validate.py --strict` reports 0 failures and 0 warnings, and all 164 items carry
`verification.assertions` (1652 assertions in total).
