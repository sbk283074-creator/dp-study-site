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
not in that map, and separately rejects a non-empty `syllabus_ref` that yields no recognised code at all
— a malformed code must not pass on the strength of the code carried in `topic`.

---

## 2. The quality contract

| Property | Rule | Enforced by |
|---|---|---|
| Originality | 5-gram Jaccard < 0.35 vs the 20,266-item external corpus | `similarity_check.py` (fail) |
| Internal originality | < 0.25 vs every other question **in this bank** | `similarity_check.py` (fail) |
| Not a reskin | No number-swap, name-swap, unit-swap, part-reordering or notation change of any existing question | `provenance.adaptation` (fail if borrowed without a note) |
| Difficulty | 3, 4 or 5. Nothing ships at 1–2 | `validate.py` (fail) |
| **Difficulty is earned** | The label must be supported by `difficulty_evidence` and by the rubric score of §2.3. A label the evidence does not support is a failure | `validate.py` (fail) |
| **Calibration** | No subject may place more than 50% of its items at difficulty 5, and the bank must actually use the whole 3–5 range | `tools/difficulty_audit.py` (fail) |
| Marks floor | Maths 6 (P3: 12) · Physics 6 · CS 6 · BM SL 10 | `validate.py` (fail) |
| Part count | Maths ≥ 3 · Physics ≥ 3 · CS ≥ 2 · BM SL ≥ 3 | `validate.py` (fail) |
| Named lever | `difficulty_evidence.lever_type` from the closed taxonomy of §2.4, plus `challenge_mechanism` ≥ 10 words naming the specific mechanism | `validate.py` (fail) |
| **Sourcing recorded** | `provenance.source_family` from the closed list of §4.5 | `validate.py` (fail) |
| **Topic label** | `topic` from the closed per-subject vocabulary (`validate.py` holds `TOPICS`), named after the guide the subject is pinned to. A near-miss label silently splits one topic in two and makes the filter lie | `validate.py` (fail) |
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

### 2.2 Difficulty must be earned, not declared

The rule this replaces was `difficulty` ∈ {3,4,5} plus a `challenge_mechanism` of ≥ 10 words. That is a
slogan check: it verifies that a claim was **typed**, not that it is **true**. Measured on 2026-09-13 it
had produced exactly the failure you would predict — **46% of the bank (79/172) claimed difficulty 5**,
Physics HL claimed **62%**, and **not one item** claimed difficulty 3. A scale on which almost
everything sits at the top carries no information, and the words attached to it were unfalsifiable.

Difficulty is now a claim with four parts, written so that each can be **falsified**:

```json
"difficulty_evidence": {
  "lever_type": "binding_constraint",
  "naive_path": "what a well-prepared student does first, concretely enough to be tried",
  "failure_point": "the exact step where that path breaks, and why",
  "wrong_answer": "the plausible result the naive path produces"
}
```

These are not decoration. §2.3 turns them into checks that can **contradict** the claim. The purpose of
`naive_path` is that a reviewer can attempt it; the purpose of `wrong_answer` is that it commits to a
plausible outcome that differs from the right one, so that a reviewer can check the trap does not in fact
yield the answer. Prose that could be about any question in the subject fails all three.

### 2.3 The difficulty rubric

`validate.py` scores every item out of 9. Four of the five tests read the evidence, and are worth
nothing without it; one reads the item's structure and can be settled by arithmetic:

| # | Test | Pts | Why it is not gameable |
|---|---|---|---|
| 1 | `failure_point` ≥ 8 words, and not a paraphrase of `naive_path` | 2 | A trap that cannot be located separately from the path is not a trap |
| 2 | `wrong_answer` ≥ 8 words, and not a paraphrase of either of the other two fields | 2 | Three fields must be three distinct statements; reusing one is the tell |
| 3 | `naive_path` ≥ 8 words | 2 | The claim has to name an actual first move |
| 4 | The **heaviest part is not the first part** | 2 | Pure structure. "Long lead-in, trivial finish" is the commonest way a question is easier than it reads |
| 5 | Assertions per mark ≥ 0.5 | 1 | The numbers are machine-checked in proportion to the marks on offer |

**Difficulty 4 and above is a floor, not a sum.** A claim of difficulty 4 or more is a claim that the
item defeats a prepared student, and that claim is only complete if all three evidence fields do their
own job — the path, the break, and the outcome it yields. Tests 1–3 must therefore each score in full;
the total may not be reached by letting two strong fields carry a hollow one. The floor was added
because the sum alone did not hold: with `wrong_answer` reduced to a verbatim copy of `naive_path`, an
item still scored 7 of 9, which permitted difficulty 4. A difficulty-3 label is not subject to the
floor, because it claims a single clean lever rather than a complete defeat.

The thresholds were set **from the data, not chosen**. Assertion density 0.5 splits the bank (median
0.62) rather than passing everything. Four earlier tests were replaced or **withdrawn**, all for the
same reason: they did not measure difficulty.

- An earlier draft required ≥ 1 assertion per mark, and a fourth-or-later part. The first passed
  172/172; the second failed most of the bank. Neither measured anything, and both were replaced.
- A test failed any item whose `wrong_answer` reused a number from `answer`, on the reasoning that a
  trap which yields the right value is not a trap. `PHYS-A.1-102` disproved it: a 5-mark MCQ cluster's
  distractors are all readings of the same graph, so its trap values are necessarily also intermediates
  inside the worked answer. The overlap is now a warning that asks for confirmation by hand.
- A test required the final part to carry at least its equal share of the marks. It was **withdrawn**
  after the first eight items carrying real evidence were scored: three of them — `MATH-AHL4.9-101`,
  `CS-A2.2-101`, `CS-B4.1-101` — end on 3 marks against an average of 3.2 to 3.4, and in every one of
  them the short final part *is* the conceptual climax: the hash-table judgement, the "looks like a
  simplification and is not" redesign, the "judge the model rather than use it" question. The test
  measured mark distribution rather than difficulty, and it measured it anti-correlated — across the
  bank it flags 20% of the difficulty-5 items against 9% of the difficulty-4 items — so keeping it
  would have systematically penalised the hardest work. The shape signal is still reported, but it can
  no longer fail a run. The tenth point it carried went with it, which is why the maximum is 9.

**A check that fires on good work is worse than no check** — and it is the same failure mode as the
label inflation this section exists to fix.

The declared label must be **earned by the score**:

| `difficulty` | minimum score | what that means |
|---|---|---|
| 5 | 8 of 9 | every test passes, and the three evidence fields are complete and mutually distinct |
| 4 | 6 of 9 | the arc and the trap are both real, and the evidence is complete |
| 3 | 4 of 9 | a real challenge, but the lever is a single clean idea |

A question that scores 6 may not be labelled 5. **Lower the label, not the score.** If a question feels
like a 5 and scores 6, the honest reading is that the evidence has not been written down yet.

### 2.4 The lever taxonomy

`challenge_mechanism` states the lever in prose; `difficulty_evidence.lever_type` states it as a term
from a closed list. The term is what makes the bank's difficulty **countable** — so that "our questions
are varied and hard" becomes a number, and so that a bank quietly built on one trick is visible.

| `lever_type` | The student must… |
|---|---|
| `implicit_dependence` | solve for a quantity that appears inside its own operator, or construct a quantity before it can be used |
| `variable_swap` | exchange the dependent and independent variables |
| `exceptional_parameter` | notice a parameter behaves one way for every value except one, or that a family degenerates at one member |
| `decoy_technique` | see that a result looks like it needs a technique and does not, or the reverse |
| `binding_constraint` | find the constraint that binds only in combination, or the pair of constraints that cannot both hold |
| `partial_cancellation` | handle two effects that partially cancel |
| `non_governing_variable` | realise the quantity is *not* set by the variable they reach for |
| `derived_limit` | derive a limit or approximation instead of quoting it |
| `aggregate_recovery` | recover two unknowns from two aggregate readings |
| `wrong_design_cost` | quantify what the wrong design costs at a stated scale — covers the degenerate "better" structure and the bug that survives the obvious test |
| `quant_vs_judgement` | reconcile a quantitative answer with the stakeholder or ethical answer that disagrees with it |
| `non_obvious_tool` | use the correct tool when it is not the obvious one — covers opposing indicators and criteria that cannot both be satisfied |
| `seeded_anomaly` | find, explain and attribute a seeded anomaly in data |

An unknown term is a **failure, not a warning**. A lever outside the list is either a typo or a genuinely
new kind of difficulty, and both should stop the batch so the taxonomy is extended deliberately.

### 2.5 Calibration — the anti-inflation rule

A label is informative only if it discriminates. `tools/difficulty_audit.py` therefore enforces:

- **No subject may place more than 50% of its items at difficulty 5.** Above that the label is
  describing the bank's self-image rather than its questions.
- **The bank must use the whole 3–5 range.** A bank with 0% at difficulty 3 is, in effect, a two-point
  scale wearing three labels.
- **Coverage floor.** Every item must carry `difficulty_evidence`. The audit prints the exact backlog;
  items written before 2026-09-13 are grandfathered as warnings rather than failures, but the backlog is
  a measured number that must fall, and **no batch may add to it**.

Measured 2026-09-13, before this standard: difficulty 5 = 46% of the bank (Physics 62%), difficulty 3 =
0%, `difficulty_evidence` coverage = **0 / 172**. Those are the numbers this section exists to move, and
the audit reports them on every run so that they cannot quietly drift back.

### 2.6 The topic label is a label, not a comment

Every item carried a `topic` from the beginning, and it was 100% populated. It was still not a labelling
scheme, for three separate reasons, and all three had to be fixed before the label meant anything:

1. **It was invisible.** `topic` was concatenated into the search index and never rendered. A student
   browsing Mathematics had no way to see which items were Calculus and which were Number and algebra.
2. **There was no way to use it.** The subject index filtered by paper, difficulty and progress — not by
   topic. A label you cannot filter by is a label nobody can act on.
3. **The vocabulary had drifted.** The same topic appeared under several names, so even a filter would
   have split it. Measured on 2026-09-14, Computer Science Theme A was carrying **three** labels
   ("Concepts of computer science", 17 items; "Computer fundamentals", 1; "Systems in organisations", 3)
   and Theme B two; Business Management Unit 3 carried both "Unit 3: Finance and accounts" and
   "Topic 3: Finance and accounts", and one item carried two units in a single label.

The names are not a matter of taste: they are taken from the guide each subject is pinned to. The CS 2027
guide defines **exactly two** themes — "Concepts of Computer Science" and "Computational Thinking and
Problem Solving" — and places "Computer Fundamentals" (A1) and "Programming" (B2) *inside* them as
strands. Two of the three Theme A labels were strand names promoted to theme names; the third does not
appear in the guide at all.

The rule is therefore: `topic` must come from a closed per-subject vocabulary, and an unknown value is a
**failure, not a warning**, because the failure mode is silent — a near-miss label does not look wrong,
it just splits a topic in two. `tools/normalise_topics.py` records the migration that repaired the eleven
items affected, and `tools/validate.py` holds the vocabulary itself.

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
  challenge_mechanism, difficulty_evidence, command_terms, question, parts, answer, markscheme_notes,
  explanation, provenance, originality, verification, status`.
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
| Physics HL | P1A | 40 multiple-choice, **1 mark each**, 4 options, no negative marking (40 of P1's 60) |
| Physics HL | P1B | data-based questions, **20 marks** — the other half of P1 |
| Physics HL | P2 | short-answer and extended response, 90 marks, 2 h 30 |
| Maths AA HL | P1 | Section A short-response ≈55 + Section B extended-response ≈55 = 110 marks, **no GDC**, 2 h |
| Maths AA HL | P2 | same A/B shape, 110 marks, **GDC required**, 2 h |
| Maths AA HL | P3 | exactly **two** compulsory extended-response problem-solving questions, 55 marks, 1 h, GDC |
| CS HL | P1 | 80 marks: Section A **56** extended response (Theme A) + Section B **24** short *and* extended response (pre-seen case study) |
| CS HL | P2 | 80 marks, **all extended response**, Theme B only — no case study, no MCQ |
| BM SL | P1 | 30 marks: Section A **20** + Section B **10**, on an unseen 800–1 000-word case study |
| BM SL | P2 | 40 marks: Section A **20** (both sets of structured questions) + Section B **20** (one of two, extended response); **mostly quantitative**, stimulus carries charts/tables/infographics |

Physics has **no Paper 3** under the 2025 guide — the options were removed. Do not write one.
**CS has no MCQ paper and no Paper 3.** The case study lives in **P1 Section B**, not P2 — a CS item
declared `case_study` must be on P1, and a `structured` item on P2 is off-spec because P2 is entirely
extended-response. Two further CS rules from the guide: one P2 question is **algorithmic thinking with
no code to read or write**, and some questions **prohibit named built-ins** (`sort`, `pop`, `len`, `max`,
`min`) — a question that can be answered by `sorted()` is not testing the algorithm.

**Which papers have sections at all** — the legal sets, read off the guides rather than inferred from
the table above, and enforced by `SECTION_RULES` in `tools/validate.py`:

| Paper | Legal `section` | Where that comes from |
|---|---|---|
| Physics HL P1 | `A`, `B` | "Paper 1 is presented as two separate booklets" — 1A is 40 MCQ, 1B is data-based |
| Physics HL P2 | **none** | "short-answer and extended-response questions"; no split named anywhere in the guide |
| Maths AA HL P1, P2 | `A`, `B` | "Section A, short-response" / "Section B, extended-response" |
| Maths AA HL P3 | **none** | "two compulsory extended response problem-solving questions" |
| CS HL P1 | `A`, `B` | Section A 56 (theme A) + Section B 24 (pre-seen case study) |
| CS HL P2 | **none** | extended-response on theme B |
| BM SL P1, P2 | `A`, `B` | P1 20 + 10, P2 20 + 20 (no local guide; verified online) |

A section is only checked when one is present. How many items carry one is a coverage question, not an
error: **231 of the 331 items sit on a paper that has sections, and 221 of those carry a label** — the
10 that do not are 7 CS P1, 2 BM P1 and 1 BM P2. The remaining **100 items are on the three papers with
no sections at all** (Physics P2 59, Maths P3 29, CS P2 12), where a label is not merely missing but
impossible.

**The CS Paper 2 type table was wrong, and the gate could not see it (fixed 2026-09-16).** `PAPER_TYPES`
in `tools/validate.py` read `("Computer Science HL", "P2"): {"case_study"}`, which contradicts the
paragraph above and the guide. The consequence was not a warning but a blind spot: 17 CS items were
declared `paper: "P2", question_type: "case_study"`, the validator checked them against a table that
expected exactly that, and the bank reported **0 failures** the whole time. Nine of those items were
Theme A material, which the guide places on P1, and **not one item carried P2's only legal type** — so
the 80-mark, 40%-of-grade Paper 2 was effectively unmodelled while the gate said the corpus was clean.
The table now reads P1 → `{structured, extended_response, case_study}` and P2 → `{extended_response}`,
and the 17 items were moved to the paper their own `topic` field names. Two lessons, both general:

1. **A gate that encodes the same mistake as the data cannot detect it.** Correcting the table turned
   the bank from `0 failures` to `17 failures` with no data change at all. When a rule is written down
   in two places — prose and code — the prose is not a check on the code.
2. **Check that every legal paper/type pair actually has items.** Coverage was 100% by syllabus node
   throughout, which is exactly why nobody looked at the papers. Node coverage and paper coverage are
   different claims, and only the first was being measured.

**The `section` label was never checked either (fixed 2026-09-16).** `section` is rendered to the
student as a chip — `P1 · Section A` — and fed to the paper builder, so a wrong value is user-visible
guidance, not metadata. It was validated nowhere. Auditing it against the guides found **60 items** (of
the then-305) carrying a label their paper does not have: **47 Physics P2**, **10 Maths P3**, and
**3 CS P1** items whose theme is B while Section A is reserved for theme A. Three things kept it
invisible:

1. **The label was plausible.** "Physics P2 · Section B" reads like real structure, and the *pre-2025*
   syllabus did split P2 into short-answer and extended-response sections, so the label looked like
   history rather than error. It is not history either. On Physics P2 the label separates nothing:
   `section: A` holds 4 structured and 2 extended-response items and `section: B` holds 20 and 21, and
   all 57 items are `level: HL`, so it does not encode the SL/AHL split either. It correlates with
   nothing at all.
2. **Half the field was right, which is worse than none of it.** Physics P1's A/B *is* meaningful — the
   1A/1B booklet split — and it separates perfectly (14 `mcq` on A, 17 `data_based` on B). A field that
   is correct in one subject and noise in another invites the assumption that it is correct everywhere.
3. **The check has to be per-paper, not per-subject.** A rule reading "section must be `A` or `B`"
   passes every one of these 60 items. Only an empty legal set — "this paper has no sections" — catches
   them, which is why `SECTION_RULES` stores the empty set explicitly rather than omitting the key.

The 60 labels were **cleared, not reassigned**. For the Physics and Maths items the paper simply has no
sections, so there is nothing to reassign them to. For the three CS items, moving them to Section B
would trade a false claim for a different one: Section B is the pre-seen case study and these carry no
case-study anchor, so they belong in neither CS section. Clearing leaves a countable work order instead
of a quiet lie — see §7. `SECTION_RULES` stores the legal set per `(subject, paper)`, empty set
included, and `SECTION_THEME_RULES` stores the one content rule (CS P1 Section A is theme A).

**The `technology` field had the same problem, and 11 items stated the opposite of the paper's policy
(fixed 2026-09-16).** `technology` renders as a chip (`technology: not allowed`) and was validated
nowhere. It had drifted into **six strings for three ideas** — `allowed` and `permitted` are the same
thing, and `not_allowed` was a spelling variant that rendered with the underscore visible — and the
values contradicted the guides in eleven places:

| Paper | Guide | Items that said otherwise |
|---|---|---|
| Maths AA HL P1 | "No technology allowed" | — (all 61 correct) |
| Maths AA HL **P2** | **"Technology required"**; students "must have access to a GDC at all times" | **3** said `not allowed` |
| Maths AA HL **P3** | **"Technology required"** | **8** said `not allowed` |
| Physics HL P1, P2 | "The use of calculators is permitted" | — (all correct) |

The eleven were all "Show that" / "Prove" items, so the author's *intent* was legible — "this question
does not need the GDC" — but the chip carries no item-versus-paper qualifier, so on a paper the guide
says **requires** technology it read as a false instruction to the student. The field stays an
item-level judgement, which is why the fix is `permitted` rather than `required`: the paper permits the
GDC, and this question does not demand it. `TECHNOLOGY_VALUES` closes the vocabulary to
`not allowed / permitted / required / not applicable` and `TECHNOLOGY_RULES` records the per-paper
values that policy rules out. 128 items were touched — 108 `allowed` → `permitted`, 9 `not_allowed` →
`not allowed`, 11 Maths P2/P3 `not allowed` → `permitted` — as **128 insertions / 128 deletions across
46 files**, one line per item.

**The CS and BM guides say nothing about calculators**, so those papers have no policy to enforce and
their values stay an authoring judgement; the vocabulary still applies. That leaves one open question
worth recording rather than inventing an answer: **CS P1 is split 17 `not allowed` against 15
`permitted` within a single paper**, and the split correlates with nothing — not question type, not
`language`. Resolving it needs the CS specimen papers, not a rule this bank can derive.

**Two more rendered fields are now closed as well.** `level` is stated twice — `build.py` derives one
from the subject slug and prints the item's own `level` beside it — so `SUBJECT_LEVEL` requires them to
agree; and `language`, which renders as a bare chip, is closed to
`python / java / pseudocode / sql` (`LANGUAGE_VALUES`). Both were already correct across all 331 items,
which is the point: they are cheap checks added while they cost nothing, so a future batch cannot drift
them silently.

**MCQ rules.** Exactly four options labelled A–D, exactly one marked correct, one mark per question.
Every option, correct or not, needs a `rationale` of at least eight words that *names the error*: a
distractor with no stated purpose is noise, not a distractor. The four options should be the correct
route plus the three or four most predictable wrong ones — wrong part of a formula, an inverted ratio,
a unit slip, a quantity confused with its rate of change. An MCQ cluster is one bank item whose parts
are the individual questions; length floors scale with the cluster (45 words of answer per MCQ), so a
five-question cluster needs roughly 225 words of answer, not 45.

**The answer key must be spread, and this was a live defect in this bank.** Every MCQ cluster here was
authored with the correct option first, which is harmless for a single item and puts the key at A in
**all fourteen** pre-existing clusters. The site renders the answer text but not the options, so a
student working through the answer booklet reads the letter A twenty-five times in a row — the same class
of defect the BPhO wave found, in a different bank. From Batch 29 the assembler applies a fixed rotation
(**A6 B6 C7 D6** over its 25 questions) and asserts that the letter stated in the answer matches the
keyed option; the option texts, rationales and arithmetic are untouched, and the rotation is applied when
authoring rather than by reordering options in the JSON, which would silently invalidate the rationales.
**Redistributing the fourteen existing clusters is an open follow-up**, and it needs the same
letter-versus-key assertion before it ships.

**Data-based rules.** Must carry a data table or a figure, and must exercise uncertainty, graphing or
experimental critique. Seed one genuine anomaly into the dataset and make the candidate find it, name a
plausible physical cause, and say what should have been done at the time — deleting a point after the
fact is not an answer. Generate the data in Python from the model, then round to the instrument
resolution, so the fit recovers the parameters you seeded.

#### 4.3.1 A stated share of items must carry a graph — hand-authored, load-bearing

The guides say it outright. On every maths paper, "questions may be presented in the form of words,
symbols, **diagrams** or tables, or combinations of these"; marks are awarded for reasoning "supported by
working and/or explanations (in the form of, for example **diagrams, graphs** or calculations)". Physics
P1B *is* data-based. The BM paper 2 booklet carries "**charts, tables and infographics**". A bank of prose
questions is therefore not modelling the papers it claims to model, however good the prose is.

Three rules, all enforced:

1. **The figure is hand-authored vector markup**, written in code and inlined into the item JSON as
   `figure = {type:"svg", content, caption}`. **Never** a charting library (matplotlib, Chart.js, plotly,
   D3, vega) and **never** an image model. `validate.py` fails on the fingerprints of both —
   `<canvas`, `plotly`, `matplotlib`, `chart.js`, `highcharts`, `echarts`, `vega`, `bokeh`, `data:image/`
   — and on `<script>`. The reason is not purity: a figure that cannot be regenerated from the JSON alone
   breaks the property that the data is the source of truth.
2. **The figure must be load-bearing.** The question is not answerable without reading it. A decorative
   sketch that merely restates the stem is worse than no figure, because it inflates the count.
3. **The share is measured, and it ratchets.** `difficulty_audit.py` reports the figure share bank-wide and
   per subject, and fails the pipeline if the bank-wide share falls below `FIGURE_COVERAGE_FLOOR`. That
   floor **may rise and may never fall**, exactly like `EVIDENCE_COVERAGE_FLOOR`. The per-subject target is
   `FIGURE_SUBJECT_TARGET` (15%) and is reported as a *gap*, not a debt, so it stays visible without
   turning the pipeline red on a backlog being paid down.

The failure mode this rule exists to prevent is a bank that looks thorough and is not: at Batch 21 the
bank stood at **45/255 = 18%**, with **Maths at 8.3% (9/109)** and **BM at 0% (0/30)**. Maths and BM are
the two subjects with the widest gap between what the guide presents and what the bank contains. Batches
22 and 22b were written against that gap and moved it, and the figure work that followed kept moving it:
the bank now stands at **104/331 = 31%**, with **Maths at 22% (30/136)** — above the per-subject target —
**CS at 48% (29/61)**, **Physics at 39% (37/95)** and **BM at 21% (8/39)**, against 0%
for BM at Batch 21. `FIGURE_COVERAGE_FLOOR` was raised from 0.17 to **0.19** in the same change that
earned it and has since been raised seven times more, to **0.24**, then to **0.25** by Batch 25, then to
**0.27** by Batch 26, then to **0.28** by Batch 27, then to **0.29** by Batch 28, then to **0.30** by
Batch 29, then to **0.31** by Batch 30, which is the
ratchet working as designed: coverage
rose, and the floor followed it up so the gain cannot be spent later. Every subject now clears the 15%
per-subject target, so the audit prints no gap. That is the intended state — the gap visible until it is
closed, and then a floor that stops it reopening. The bank-wide floor has now become the binding
constraint rather than the per-subject one: **two non-figure items of headroom** remain, so the next
batch cannot be plain text at all.

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

### 4.5 Cross-syllabus sourcing

Difficulty does not have to be invented. Other systems examine the same mathematics and physics at
comparable or greater demand, and their hard questions are a legitimate source of *ideas*. Chinese
material (高考压轴题, 强基计划 written tests, 数学/物理竞赛) is already used, but the list is deliberately
wider than that: a bank fed from one system inherits that system's blind spots, and the same lever
appears over and over in the same accent.

Every item declares `provenance.source_family` from this closed list, and `difficulty_audit.py` reports
the mix — so "we draw on other syllabuses" is a measured fact rather than an intention. (Measured
2026-09-13: only **6 of 172** items name any source at all — the other 166 record `original` — so the
claim was untestable in either direction. Measured 2026-09-15, after the sourcing work: **60 of 255**.
Measured 2026-09-16, after Batches 22 and 22b: **70 of 267** — `uk-alevel` 21, `china-gaokao` 20,
`us-ap` 12, `uk-further-maths` 6, `china-qiangji` 6, `singapore-alevel` 2, `china-competition` 2,
`ib` 1.)

**Keeping the list fed is a standing duty, not a one-off.** A batch that sources nothing is not neutral —
it drifts back toward `original`, and `original` written by one author in one idiom is the fastest route
to a bank that is uniformly shaped. So every batch should carry at least one item whose idea came from
outside IB, and the search for material continues independently of any batch: new textbooks, other
systems' past papers, university-entrance tests and competition archives are all in scope. The rules do
not change — an idea may be borrowed, a question may not, and `provenance.adaptation` must name what
changed (§5.2). Prefer a source the bank has **not** used yet over a fifth item from one it has.

| `source_family` | What it is good for | What must change on adaptation |
|---|---|---|
| `original` | constructed from the guide's own bullets | nothing — this is the default |
| `ib` | other IB sessions, P3, specimen papers | the originality gate bites hardest here; rebuild, never reproduce |
| `china-gaokao` | 高考 including 压轴题: parameter discussion, multi-step algebra, hard inequalities, sequences | convert to IB command terms; keep the algebra inside AA HL content; add IB markscheme annotations and significant figures |
| `china-qiangji` | 强基计划 written tests: more abstract, more proof-like | keep the idea, rebuild at IB content level — these routinely exceed the guide |
| `china-competition` | 数学/物理竞赛 (联赛 and above) | the technique is usually outside IB. Use the *situation*, replace the trick |
| `uk-alevel` | A-Level Maths / Physics: long structured arcs, disciplined "show that" parts | check the data booklet — IB supplies fewer formulae than A-Level; physics sign and *g* conventions differ |
| `uk-further-maths` | Further Maths: matrices, complex numbers, polar form, differential equations | mostly *inside* AA HL — the single best source for P3 |
| `us-ap` | AP Calculus BC, Physics C, CS A, Micro/Macro: FRQ structure is close to IB extended response | Physics C uses calculus IB Physics HL does not — strip it; AP CS A is Java-specific, so keep the algorithmic reasoning and drop the language |
| `singapore-alevel` | H2: dense, rigorous, strong multi-part structure | heavy content overlap; check for topics outside the IB guide |
| `other` | any other system | say which, in `resource_origin` |

**Rights and originality.** Adapting an idea is legitimate; reproducing a question is not. Never copy a
question, diagram or dataset verbatim from any source. Record the origin in `provenance.resource_origin`,
name what inspired the item in `provenance.inspired_by`, and state in `provenance.adaptation` what
changed — at least two of {context, structure, what is given vs what is asked, the reasoning chain}
(§5.2). `provenance.rights` stays `original` for a rebuilt question.

**The rule that matters most: difficulty must survive the adaptation.** If the source's hard step was an
algebraic trick IB does not examine, replace the trick rather than the difficulty. A question that drops
its own lever while keeping the source's name is a reskin with a citation attached.

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
| CS P1 (case study, Section B) | binding-constraint architecture split; ADT selection against every operation; imbalanced-data metrics and governance; concurrency and deadlock; protocol design with a threat model; legacy-migration phasing; algorithmic fairness | distributed-system consistency; ML pipeline governance; a second security incident with a different failure class |
| CS P2 (extended response, Theme B) | **single-machine scheduling where the trained rule is the decoy**; **heap vs sorted array where the workload reverses the ranking**; **amortised doubling where the average is right and cannot answer the question**; **a cache that faults more when given more room** | graph traversal with a tie-break that changes the answer; string matching with overlapping occurrences; a compression scheme whose worst case is not its average case |
| BM P1 (case study) | ratio analysis → growth model choice; landed cost → working-capital and obsolescence effects | HR restructure with a motivation theory; market-entry with Ansoff plus STEEPLE |

Three rules keep the ledger honest. First, a new item in a row must differ from the entries already there
in *what the student has to decide*, not in the context it is dressed in. Second, the Physics P1B row
exists in its present form because the first two P1B items were both "linearise and fit"; if a row starts
to look like a list of the same verb, the next item has to change the verb. Third — and this is not
theoretical — backfilling skeletons onto the 164 legacy items immediately exposed
`MATH-AHL5.6-001`/`MATH-AHL5.8-001` at **0.467**, two "differentiate, set to zero, classify, evaluate"
questions on different functions that had been sitting in the bank as an apparent 0-failure state.
**Any legacy item without a skeleton is invisible to the approach gate.** Do not leave one that way.

### 4.7 Difficulty evidence — schema and migration state

```json
"difficulty_evidence": {
  "lever_type": "binding_constraint",
  "naive_path": "…",
  "failure_point": "…",
  "wrong_answer": "…"
}
```

`lever_type` comes from the closed taxonomy in §2.4; each of the three prose fields is ≥ 8 words;
`failure_point` must not restate `naive_path`; `wrong_answer` must differ from the answer. The rubric of
§2.3 then decides which label the item is allowed to carry.

**Migration state.** The field was introduced on 2026-09-13. Items written before it are grandfathered:
`validate.py` warns rather than fails, and `difficulty_audit.py` prints the backlog. Two consequences,
both deliberate:

- **The bank's advertised `0 failures · 0 warnings [strict]` invariant no longer holds in full.** That is
  the honest reading, not a regression: the difficulty label on the grandfathered items is currently
  unbacked, and the number is published rather than hidden behind a passing gate.
- **No new batch may add to the backlog.** An item written from 2026-09-13 onwards carries
  `difficulty_evidence`, or it does not ship.

The first eight items to carry evidence were the figure questions — one per figure-bearing file, chosen
because their answers are fully worked and the trap could be read out of the item rather than invented.
All eight score 9 of 9 and every label they carried was earned, so none had to be lowered; the audit's
`labels the evidence does not permit` count is the number to watch as the backlog is cleared. One of the
eight, `MATH-AHL1.13-101`, had a `challenge_mechanism` asserting a trap the item does not contain — it
claimed the second root of the quadratic sits on the opposite half-line, when both roots are positive and
the item's own answer says so. The mechanism was corrected to the real lever rather than the evidence
bent to match the false claim. **Where the prose and the answer disagree, the answer wins.**

**Do not mass-generate the prose.** Writing plausible `naive_path` / `failure_point` / `wrong_answer`
text for the remaining 85 items without reading each one reproduces precisely the failure this section
exists to fix. Clear the backlog subject by subject, reading the item, and **lower any label the evidence
does not support** rather than inventing evidence to protect the label. The 79-item pass described below
is the worked example: the five corrections are exactly the ones a transcription would have missed,
because a transcription cannot disagree with the label it is defending.

**The difficulty-5 backlog is cleared.** On 2026-09-16 the 79 items that claimed difficulty 5 with no
evidence — 36 Maths, 31 Physics, 10 CS, 2 BM — were read one at a time and given evidence. The headline
number is now **0**: no item in the bank claims difficulty 5 without a lever written down. 85 items still
carry no `difficulty_evidence`, all of them difficulty-3 or difficulty-4 claims, and they remain a
published backlog rather than a hidden one.

Reading the 79 produced **five label corrections, all downwards** — the outcome this section asks for,
not an accident:

| item | was | now | why the evidence does not permit 5 |
|---|---:|---:|---|
| `MATH-P3-010` | 5 | 4 | the heaviest part is the first (`5, 4, 4, 3`), so the arc test scores 0 and the item tops out at 7 of 9 |
| `MATH-AHL5.9-001` | 5 | 4 | one clean idea — split the journey at the rest times — rather than a complete defeat |
| `MATH-AHL5.10-001` | 5 | 3 | the author's own note gives the trap as a sign slip on the cosine term, and a slip is not a lever |
| `MATH-AHL5.11-001` | 5 | 4 | one clean idea — establish which curve is on top — on a flat four-part arc |
| `PHYS-E.2-101` | 5 | 4 | the mechanism names units rather than an idea |

`labels the evidence does not permit` stayed at **0** throughout, which is the check that would have
caught a correction that went the wrong way. One of the five landed at difficulty 3, so the pass widened
the 3–5 range rather than only shortening the top of it.

---

## 5. How to author one

The order matters. Writing the question before knowing its lever produces a reskin.

1. **Pick the node.** `python3 tools/coverage.py --next 12` gives the highest-priority gaps.
2. **Choose the lever first.** Name the mechanism before writing anything, and pick its `lever_type`
   from the taxonomy in §2.4 at the same time. A lever is something the student must *notice, reject or
   invert* — not "it has several parts".
3. **Write the difficulty evidence before the question.** `naive_path` is the first thing a prepared
   student tries; `failure_point` is the exact step where it breaks; `wrong_answer` is what that path
   yields instead. If you cannot state all three, you do not yet have a hard question — you have a long
   one, and the rubric will score it accordingly.
4. **Design the arc.** Parts interlock: the answer to (a) is needed for (b), and (c) is where the lever
   bites. The rubric checks that the heaviest part is not the first. It does **not** require the final
   part to be the heaviest — a short closing part that asks the candidate to judge rather than compute
   is one of the strongest ways to finish, and the audit reports the shape without scoring it.
5. **Give the data a reason.** Numbers are chosen so the arithmetic comes out clean *only if* the
   reasoning is right.
6. **Write the answer as a markscheme**, annotating every award at the point it is earned.
7. **Write `markscheme_notes`** — alternatives, condonations, follow-through, what forfeits a mark.
8. **Write `explanation`** — the insight, why it is hard, and the classic wrong turns.
9. **Add assertions** and a one-line `verification.method`.
10. **Score it before labelling it.** `python3 tools/difficulty_audit.py --id <ID>` prints the rubric
    score; set `difficulty` to the highest value that score permits (§2.3). Label inflation is the
    failure mode this bank has actually suffered, not a hypothetical one.

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
| 4. difficulty gate | `tools/difficulty_audit.py --check` | §2.2–§2.5: evidence coverage, the rubric, the lever taxonomy, the anti-inflation rule, the source-family mix |
| 5. originality gate | `tools/similarity_check.py --write` | 20,266 external + all internal pairs |
| 6. rebuild | `build.py` | re-renders so similarity scores appear in the metadata |

Stage 4 exists because stage 3 cannot see difficulty. Stage 3 checks that a claim was *made*; stage 4
checks whether the bank's claims, taken together, are *credible* — a bank where 46% of items claim
difficulty 5 and none claim 3 passes every per-item rule while telling the student nothing.

Stage 4 blocks on a **regression**, not on the backlog. The distinction matters: a gate that refuses to
let a batch ship until 164 unrelated items have been rewritten is a gate that gets switched off, and a
gate that is switched off is a slogan. So the calibration rules are enforced against the state measured
on 2026-09-13:

- **Regression — blocks.** Evidence coverage below the ratchet floor, a subject whose difficulty-5 share
  has *risen* above its recorded baseline, a `source_family` outside the list, a difficulty-3 count that
  has fallen. These mean the bank got worse, and that is always the batch's fault.
- **Debt — reported, does not block.** Physics HL at 62% difficulty 5, and no item claiming difficulty 3.
  Both are pre-existing, both are printed on every run with the baseline beside them, and both are paid
  down by backfilling evidence and re-labelling. `--check --strict` fails on the debt as well, which is
  the mode to use when asking "is this bank calibrated?" rather than "did this batch break anything?".

Useful variants:

```
python3 tools/validate.py --strict              # warnings count as failures (new batches)
python3 tools/validate.py --subject "Physics HL"
python3 tools/validate.py --stats               # length distribution + subject medians
python3 tools/difficulty_audit.py               # the difficulty report: distribution, levers, backlog
python3 tools/difficulty_audit.py --check       # exit non-zero only if the bank regressed
python3 tools/difficulty_audit.py --check --strict   # also fail on the outstanding debt
python3 tools/difficulty_audit.py --id MATH-AHL5.11-101   # score one item, to choose its label
python3 tools/prove_difficulty_gates.py         # regression test: prove the gates still bite
python3 tools/coverage.py --next 12             # the batch brief
python3 tools/ship.py --skip-similarity         # stage 5 costs ~1 min; skip while drafting
```

Exit codes are non-zero on failure at any stage, so a batch can be shipped without reading the output
unless something breaks.

`prove_difficulty_gates.py` is the guard on the guards. It injects one defect at a time into a real
item — an invented `lever_type`, a `wrong_answer` that restates `naive_path`, a difficulty 5 with no
evidence, a borrowed `source_family` with no origin — and fails if the gate lets any of them through.
It found a real hole on its first run, and it is the reason difficulty ≥ 4 is a completeness floor
rather than only a sum. Run it after any change to the rubric.

---

## 7. Expansion protocol

1. **Brief:** `coverage.py --next N` returns the gap list, ordered by priority then subject. A batch
   takes its targets from the top of that list; it does not start from whatever topic is easiest.
2. **Batch size:** as many as can be written well in one pass, typically 4–8. One file per batch per
   subject, `data/<subject>/batchN.json`.
3. **Gate:** `python3 tools/ship.py`. New batches are additionally run with `validate.py --strict`.
4. **Status:** new items are `draft` until the gates pass, then `published`.
5. **Re-brief:** coverage is re-measured after every batch; the next brief comes from the new gaps.

Current state: 331 questions · **166 / 166 nodes covered (100%)**, and **every priority-1 and
priority-2 node is done** — Maths 32/32 must + 51/51 should (83/83 overall), Physics 24/24 (complete),
CS 25/25 (complete), BM 26/26 must + 8/8 should (34/34 complete, including all 8 Toolkit nodes). All 331
carry `verification.assertions` (3828 assertions in total), `validate.py` reports 0 failures, and 246 of
the 331 carry a `difficulty_evidence` block — the other 85 are the grandfathered backlog described in
§4.7, which `--strict` reports as warnings and plain `--check` ignores unless the bank gets worse. **No
item claims difficulty 5 without evidence**; all 85 outstanding items are difficulty-4 claims.

**Node coverage is not paper coverage, and only the first was being measured.** The 100% above is true
and was true throughout the CS Paper 2 error described in §2.4: every CS node had an item, while the
80-mark Paper 2 component had none of its legal question type. When a coverage claim is quoted, say which
kind it is. The per-paper distribution is worth reading beside it — after Batch 29 it is Maths P1 64 /
P2 37 / P3 29, Physics P1A 19 clusters (95 questions) / P1B 17 / P2 59, CS P1 49 / P2 12, BM P1 10 / P2 29.
Batch 28 was aimed by exactly this paragraph: with node coverage at 100%, `coverage.py --next 12` reported
**0 gaps**, so the brief had to come from the paper structure instead. The guide gives CS HL Paper 1
Section A **56 of its 80 marks**, while the bank held 12 of its 44 CS P1 items there and five Theme A nodes
had no Section A item at all; the five new items fill those five, taking Section A to **17 of 49** and the
number of Theme A nodes represented in Section A from 7 to 12.

**The section audit left a bounded work order (§4.3).** Clearing the 60 false labels removed wrong claims
but did not supply right ones, and one group cannot be given a label without new content:

- **6 CS P1 items are theme B with no case-study anchor**, so they fit neither section: Section A is
  theme A, and Section B is the pre-seen case study. Three are now unlabelled — `CS-B2.2-401`,
  `CS-B2.4-401`, `CS-B2.4-402` — and three still claim Section B with no stimulus — `CS-B2.4-002`,
  `CS-B2.4-003`, `CS-B2.4-301`. The fix is content, not metadata: give each a case-study anchor and it
  becomes a legitimate Section B item. These six are the top of the next CS batch.
- **4 CS P1 theme-A items sit in Section B with no stimulus** — `CS-A1.2-002`, `CS-A1.3-301`,
  `CS-A2.3-002`, `CS-A2.3-301`. Section A is theme A and does not need a scenario, so these read as
  Section A items filed one section over.
- **`CS-B2.4-001`** is theme B, carries a stimulus, and has no section — the one item that can simply be
  labelled Section B.

CS P1 is also weighted the wrong way round against the real paper: Section B holds **25 of the 44 items**
while the guide gives it **24 of the 80 marks**. Section A is both the larger component and the thinner
one, so new CS P1 material should target it. Batch 26 took the first step — Section A went **9 → 12** —
but the weighting is still inverted, and the three theme-A strands it filled were the ones with no
Section A item at all.
