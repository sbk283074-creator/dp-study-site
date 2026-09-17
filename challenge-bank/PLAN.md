# IB Challenge Bank — Generation Plan

**Cohort: class of 2028 (final examination session May 2028).**
**Status: live. 325 questions across the four subjects, every priority-1 and priority-2 syllabus node
covered (166/166 nodes, 100%). The difficulty label is now a measured property rather than a declared
one: from 2026-09-13 every item must carry `difficulty_evidence`, and 240 of 325 do. The difficulty-5
backlog is **cleared** — no item claims difficulty 5 without evidence — and the 85 items that remain
unbacked are all difficulty-4 claims, a published, ratcheting backlog described in
`STANDARD.md` §2.2–§2.5 and measured by `tools/difficulty_audit.py`. All 13
lever types are in use, the largest share is 15%, and every subject is inside the 50% difficulty-5 cap
(Maths 45%, Physics 44%, CS 41%, BM 23%). Both calibration debts are cleared: R1 (no new Physics d5 while
the share was above the cap) and R2 (no item claimed difficulty 3 — the 3-5 scale had collapsed to two
points) were paid by Batches 21–23, and the backlog pass added a fifth difficulty-3 item. The audit prints
`calibration OK` and `--check --strict` exits 0.
The `topic` label is now a closed vocabulary per subject, enforced by `validate.py`, and is shown on every
question page and filterable on every subject page.**
**Figure coverage is now a first-class gate rather than a nice-to-have.** Batch 23 raised the share of
items that carry a self-authored graph to 75 of 301 = 25%; Batch 26 took it to 84 of 310 = 27.1%; Batch 27
to 89 of 315 = 28.3%; Batch 28 to 94 of 320 = 29.4%; Batch 29 takes it to **98 of 325 = 30.2%** and raises
the bank-wide ratchet `FIGURE_COVERAGE_FLOOR` from 0.29 to
**0.30** — the floor may rise and may
never fall, so a later batch cannot quietly spend the coverage. No subject prints a gap: Maths 18%,
Physics 39%, CS 48%, BM 21%, against a 15% target — but only **1 non-figure item of headroom** is left
(98/326 = 30.06% passes, 98/327 = 29.97% fails), so the ratchet now *forces* a batch to carry figures
rather than
merely encouraging it. Every figure is drawn by hand as a plain-Python SVG
string builder,
most of them inline in the batch generator that wrote the item and the named set in
`tools/make_figures.py`: no charting library, no plotting package, no
image model. `validate.py` rejects the fingerprints of all of them (`<canvas`, `plotly`, `matplotlib`,
`chart.js`, `highcharts`, `echarts`, `vega`, `bokeh`, `data:image/`), so "without other tools" is a
property the gate checks rather than a promise the prose makes.**
**The `section` label is a checked property too, as of 2026-09-16.** `SECTION_RULES` in `validate.py`
records the legal section set for every `(subject, paper)` — including the empty set, which is what makes
"this paper has no sections" enforceable — and `SECTION_THEME_RULES` records that CS P1 Section A is
theme A. Adding the rule exposed **60 items** (the bank then held 305) carrying a label their paper does
not have (47 Physics P2, 10 Maths P3, 3 CS P1); all 60 were cleared, and the 6 CS P1 theme-B items this
leaves without a home are the next CS batch's work order (`STANDARD.md` §7).

New folder: `challenge-bank/` (inside `dp learning final/`). It holds the question data and a
standalone static website that collects and presents the questions.

Line-up: **Mathematics AA HL · Physics HL · Computer Science HL · Business Management SL.**

---

## 1. What we are building, and why it is not the existing bank

The existing question bank (`dp learning/ib-dp-platform/backend/data/app.db`, 17,439 questions) is a
**retrieval** corpus: real IB past papers plus topic extractions. It is good for practice and search.

This new bank serves the opposite purpose: a small, hard, **original** set of questions that force the
reasoning the real exams only occasionally demand. It is deliberately small and deliberately
uncomfortable.

| | Existing qbank | Challenge Bank (this project) |
|---|---|---|
| Provenance | Real IB papers + extractions | Original, or adapted from non-IB sources |
| Size | 17,439 | Tens per subject, grown slowly |
| Difficulty | Whatever IB set | Minimum floor (§4) — easy items are rejected |
| Purpose | Coverage, retrieval, volume | Depth, transfer, non-routine reasoning |
| Reuse of figures | Scanned/IB figures | Only self-authored SVG / LaTeX / tables |

---

## 2. Scope — the four subjects

### 2.0 Cohort pinning: which syllabus is actually in force for May 2028

This matters, because three of the four subjects are mid-transition.

| Subject | Guide in force for the May 2028 session | Why |
|---|---|---|
| Mathematics AA HL | **2021 guide** (first assessment 2021) | The 2021 syllabus runs through **November 2028**. The revised guide is first teaching Aug 2027 / **first assessment May 2029** — one cohort after yours |
| Physics HL | **2025 guide** (first assessment 2025) | Current syllabus, no change before 2028 |
| Computer science HL | **2027 guide** (first assessment 2027) | May 2027 is the first session, so May 2028 is the **second** session of the new Theme A / Theme B syllabus |
| Business management **SL** | **2024 guide** (first assessment 2024) | Current syllabus, no change before 2028 |

Two consequences worth stating plainly:

- **Maths:** you sit the *old* maths syllabus. So the topics the 2029 revision deletes (financial
  applications, bivariate data, proof by counterexample, Euler's method) are still fully assessable for
  you. I will not avoid them — but I will not build a question whose whole difficulty rests on one of
  them, since they are on the way out.
- **Computer science:** you sit the *new* syllabus. The 1,107 CS questions already in the old bank are
  legacy (Topics 1–7 + options) and are **not** a valid model for what you will face. Everything CS here
  is written against Theme A / Theme B.

### 2.1 Mathematics AA HL — assessment shape (2021 guide)

| Paper | Time | Marks | Conditions | Weight |
|---|---|---|---|---|
| P1 | 120 min | 110 | **No technology**. Section A short-response, Section B extended-response | 30% |
| P2 | 120 min | 110 | Technology required. Section A short, Section B extended | 30% |
| P3 | 60 min | 55 | Technology required. **Two compulsory extended problem-solving questions** | 20% |
| IA | — | 20 | Mathematical exploration | 20% |

Sub-topic codes to tag against: T1 `SL 1.1–1.9 / AHL 1.10–1.16`; T2 `SL 2.1–2.11 / AHL 2.12–2.16`;
T3 `SL 3.1–3.8 / AHL 3.9–3.18`; T4 `SL 4.1–4.12 / AHL 4.13–4.14`; T5 `SL 5.1–5.11 / AHL 5.12–5.19`.

### 2.2 Physics HL — assessment shape (2025 guide)

| Paper | Time | Marks | Conditions | Weight |
|---|---|---|---|---|
| P1A | 2 h total | 40 | 40 MCQ on SL + AHL material, no penalty for wrong answers | 36% |
| P1B | (same sitting) | 20 | Data-based questions | (with P1A) |
| P2 | 2 h 30 min | 90 | Short-answer + extended-response, SL + AHL material | 44% |
| IA | 10 h | 24 | Scientific investigation | 20% |

Themes: **A** Space, time and motion (A.1–A.5) · **B** The particulate nature of matter (B.1–B.5) ·
**C** Wave behaviour (C.1–C.5) · **D** Fields (D.1–D.4) · **E** Nuclear and quantum physics (E.1–E.5).
Every question must state whether it is SL-core or AHL-only content, and must respect the Physics data
booklet constants and IB significant-figure/unit conventions.

### 2.3 Computer science HL — assessment shape (2027 guide)

| Paper | Time | Marks | Conditions | Weight |
|---|---|---|---|---|
| P1 | 2 h | 80 | Section A (56) extended response on Theme A, SL+HL; Section B (24) short + extended response on the **pre-seen case study** (4 challenge questions) | 40% |
| P2 | 2 h | 80 | Extended response on Theme B. Two questions shared with SL, incl. one **algorithmic-thinking question requiring no code**. Two versions: **Python** and **Java** | 40% |
| IA | 35 h | 30 | The computational solution | 20% |

Theme A: A1 computer fundamentals · A2 networks · A3 databases · A4 machine learning.
Theme B: B1 computational thinking · B2 programming · B3 OOP · B4 abstract data types.
HL-only: A1.4 translation, parts of A2, A3.4 alternative databases, A4.2/A4.3, B3.2 multiple classes.

Consequence for us: we must author **original case studies** (we cannot reuse IB's published ones), and
provide Python **and** Java variants for any P2 code question.

### 2.4 Business management SL — assessment shape (2024 guide)

| Paper | Time | Marks | Conditions | Weight |
|---|---|---|---|---|
| P1 | 1 h 30 | 30 | **Pre-released statement** (~200 words) + **unseen case study (800–1,000 words)**. Section A 20 marks (answer all), Section B 10 marks (1 of 2 extended response). Units 1–5 **excluding HL-only content**. 4-function calculator permitted, no formula sheet | 35% |
| P2 | 1 h 30 | 40 | Unseen **quantitative** stimulus. Section A 20 marks (answer all), Section B 20 marks (1 of 2: structured + extended response). **Formula sheet required**, 4-function calculator | 35% |
| IA | 20 h | 25 | Business research project (≤1,800 words) | 30% |

**There is no Paper 3 at SL.** All BM work here is P1-style or P2-style.

**SL content boundaries — a hard constraint.** Anything in this list is out of syllabus and must never
appear in a question, an answer, or a mark scheme:

| Unit | In syllabus for SL | HL-only (forbidden here) |
|---|---|---|
| 1 | 1.1–1.6 | 1.7 organizational planning tools |
| 2 | 2.1–2.4, 2.6 | 2.5 organizational (corporate) culture · 2.7 industrial/employee relations |
| 3 | 3.1–3.5, 3.7, 3.8 | 3.6 debt/equity and efficiency ratio analysis · 3.9 budgets |
| 4 | 4.1, 4.2, 4.4, 4.5 | 4.3 sales forecasting · 4.6 international marketing |
| 5 | 5.1, 5.2, 5.4, 5.5 | 5.3 lean production and quality · 5.6 production planning · 5.7 crisis management · 5.8 R&D · 5.9 management information systems |

**Toolkit: 8 tools only** — SWOT, Ansoff, STEEPLE, BCG, business plan, decision trees, descriptive
statistics, circular business models. (Force field analysis, Gantt charts, critical path analysis,
Hofstede's dimensions, Porter's generic strategies, contribution analysis and linear regression are
HL-only.) Concepts: change, creativity, ethics, sustainability.

**How BM SL gets hard, given the smaller syllabus.** It cannot come from harder content, so it has to
come from: messy or conflicting quantitative data; stakeholder criteria that genuinely clash; a
decision with no clean answer; a case where the obvious Toolkit tool is the wrong one. That is the
design brief for every BM item.

Consequence for us: BM questions cannot exist without stimuli. We must author **original pre-released
statements, unseen case studies (800–1,000 words) and quantitative stimuli**, with internally
consistent financial data.

---

## 3. Sources: what we may draw on, and how

### 3.1 Local resources — for **style calibration only**

`dp learning/` holds ~1,750 PDFs: 752 maths papers, 549 physics papers, 330 CS papers, 68 physics
topic booklets, 56 maths chapter-wise question banks with markschemes, plus Haese / Hodder / Pearson /
Oxford / Cambridge / Tsokos / IBID textbooks and workbooks, and the three subject guides.

These are used to **extract the grammar of an IB question** (command-term usage, mark:minute ratios,
part-lettering, marking annotations, phrasing) — **never** as a question source. Copying, or
"same question, new numbers", is prohibited (§5).

Caveat: the local CS papers are **legacy syllabus**. They are useful for markscheme *style* only; their
content is not a model for 2028.

### 3.2 External sources — allowed, with mandatory adaptation

| Subject | Permitted inspiration pools |
|---|---|
| Maths AA HL | STEP / MAT / TMUA / AEA; A-level Further Maths (Edexcel, MEI, OCR); AP Calculus BC free-response; BMO Round 1; JEE Advanced (selective); classic texts (Hardy, Polya) |
| Physics HL | BPhO / Physics Olympiad; Irodov; Morin; Kleppner & Kolenkow; University Physics / HRW (hard end-of-chapter problems); A-level Physics (harder structured/data questions); AP Physics C; real datasets (CERN, NASA, NOAA) for data-based P1B |
| CS HL | A-level Computer Science (OCR/AQA); AP CS A / CSP; USACO Bronze–Silver; Kattis / Codeforces *easy* problems; real system design write-ups; OWASP material for A2.4; SQL/relational-design exercises |
| BM SL | Real company reporting (annual reports, social enterprise impact reports); CIMA/ACCA-style quantitative analysis; case competitions; A-level Business / Economics data-response questions; HBS-style caselets (rewritten). Harder *concepts* from HL must not be imported — only harder *data and judgement* |

**Adaptation rule (mandatory).** A borrowed idea may only be used if **at least two** of the following
are changed: (a) real-world context, (b) question structure/part decomposition, (c) the quantity that
is given vs the quantity that is asked for, (d) the reasoning chain required. Then it must be
re-anchored to a specific IB syllabus bullet and rewritten in IB register. The `provenance` field
records what was borrowed and what was changed.

### 3.3 Never

- Verbatim IB past-paper stems, figures or markschemes (copyright + defeats the purpose).
- Verbatim textbook exercises.
- Any figure scanned or copied from a copyrighted source. All diagrams are authored as SVG or LaTeX.
- For BM SL: any HL-only topic or HL-only Toolkit tool, even as a distractor or in the mark scheme.

---

## 4. Quality bar: no short, no easy

### 4.1 Hard floors

| Subject | Minimum marks | Minimum structure |
|---|---|---|
| Maths AA HL | 6 (P1/P2), **12** (P3) | ≥3 interlocking parts; at least one `hence` / `show that` / proof or a modelling step |
| Physics HL | 6 (P2 / P1B) | ≥3 parts; must include quantitative work with units + SF, and one justification/evaluation |
| CS HL | 6 | ≥2 parts; P2 code questions must need an algorithm, not syntax recall; must state language and any prohibited built-ins |
| BM SL | 10 | Either a standalone 10-mark Section B extended response, or a 10+ mark structured cluster of ≥3 parts ending in an AO3 evaluation/decision. Must use ≥1 of the eight SL Toolkit tools (≥2 where the item is a P1 case-study or a P2 Section B response) and ≥1 concept lens |

### 4.2 Automatically rejected

- One-step substitution into a memorised formula.
- "State…" / "Define…" / "List two…" as the whole question.
- Recall-only MCQ.
- Plug-and-chug with a number change only.
- Any question whose difficulty rating would be 1 or 2.
- BM: a question whose difficulty depends on an HL-only topic (it would be out of syllabus, not hard).

### 4.3 Difficulty scale (only 3–5 accepted)

| Rating | Meaning | Target share |
|---|---|---|
| 3 | Harder than a standard exam part; 2–3 linked steps in a familiar setting | 40% |
| 4 | Non-routine: unfamiliar setting, or a step most candidates would not find | 40% |
| 5 | Olympiad / paper-3 grade: long chain, or a genuinely clever observation needed | 20% |

Physics and maths are weighted toward 4–5 (that is where you asked for the pressure). CS and BM SL sit
mostly at 3–4, with 5 reserved for genuinely long reasoning chains.

### 4.4 Challenge levers (each question must name the one it uses)

Novel scenario · multi-stage derivation · reverse/derive-the-parameter · data-vs-model discrepancy ·
uncertainty and error propagation · limiting-case / order-of-magnitude reasoning · assumption critique ·
cross-topic synthesis (e.g. fields + circular motion + energy) · constraint optimisation · proof then
apply · "hence" chain where each part unlocks the next · conflicting-criteria evaluation ·
design-a-decision-procedure · estimation with justified assumptions · algorithmic complexity trade-off.

Every question carries a one-line `challenge_mechanism`. If I cannot state it, the question is not hard
and gets discarded.

---

## 5. Originality protocol

1. **Design-first, never transform-first.** Start from a syllabus bullet + a chosen challenge lever +
   a fresh context. If I ever catch myself starting from an existing question and editing it, I stop
   and restart.
2. **Forbidden moves** (instant reject): change the numbers; change the names/units; reorder the parts;
   swap the graph/case but keep the stem; translate a real question into different notation;
   combine two real questions.
3. **Similarity gate (automated).** Script `tools/similarity_check.py` compares each new question
   against (a) all 17,439 rows of `app.db`, (b) the 2,827 un-imported items in
   `backend/generated/*.json`, (c) every previously published Challenge Bank question — **20,266 items
   in total**. Method: word-level 5-gram Jaccard over LaTeX-stripped text, plus an **approach gate**
   over the declared `solution_skeleton` (stemmed token overlap).
   **Reject if max similarity ≥ 0.35 within the same subject**, or ≥ 0.50 cross-subject, or ≥ 0.50 on
   the approach gate. The nearest match id and score are stored in `originality`.
4. **Web gate.** A distinctive phrase from the stem is searched verbatim. Any near-hit on a past
   paper, question-bank site or textbook solution → rewrite.
5. **Answer independence.** The worked answer must be derived from scratch and verified (§8), not
   compared against a known answer.
6. **Provenance is mandatory** even for fully original questions: `inspired_by` may be `"original"`;
   if it is anything else, `adaptation` must describe the structural change.

---

## 6. Data schema

One JSON file per subject per topic: `data/<subject>/<topic-slug>.json`, shaped as
`{ "questions": [ ... ] }`. Field set (extends, and stays compatible with, the existing `questions`
table):

```
id                  "MATH-AHL5.16-004" | "PHYS-D.3-002" | "CS-B4.1-007" | "BM-3.8-003"
subject             "Math AA HL" | "Physics HL" | "Computer Science HL" | "Business Management SL"
level               "HL" | "SL"
syllabus_ref        "AHL 5.16" | "D.3" | "B4.1.5" | "3.8 Investment appraisal"
topic / subtopic    human-readable topic and sub-topic
paper               "P1" | "P2" | "P3"        (BM: "P1" | "P2" only)
section             "A" | "B"   (CS/BM/P1A/P1B where relevant)
technology          "not allowed" | "required" | "permitted"      (maths/physics)
language            "python" | "java" | "pseudocode" | null      (CS)
marks               integer
difficulty          3 | 4 | 5
challenge_mechanism one line
command_terms       ["Hence", "Show that", ...]
stimulus            optional: authored case study / pre-released statement / data table / code listing
figure              optional: { "type": "svg" | "table" | "code", "content": "..." }
question            full stem, LaTeX for maths/physics, Markdown-lite elsewhere
parts               [ { "label": "a", "text": "...", "marks": 4, "command_term": "Determine" } ]
answer              full worked solution with IB marking annotations (M1)(A1)(R1)(AG)
markscheme_notes    alternative methods, condonations, what earns partial credit
explanation         the key insight, why it is hard, the classic wrong turn
tags                [ ... ]
provenance          { "inspired_by": "...", "adaptation": "...", "source_url": "...", "rights": "..." }
originality         { "checked_at": "...", "max_similarity": 0.21, "nearest_bank_id": "..." }
verification        { "method": "...", "checked_by": "...", "status": "pass" }
status              "draft" | "reviewed" | "published"
authored_by         "ai"
created_at / updated_at
```

All text in English (the house convention across the existing sites).

---

## 7. The website

New folder `challenge-bank/`, a static site with **no build framework** — same philosophy as the
existing `PYTHON/` micro-site: one Python script renders HTML from the JSON.

```
challenge-bank/
  PLAN.md
  README.md                 build + contribution notes
  build.py                  JSON -> static HTML (only script in the project)
  data/
    math-aa-hl/*.json
    physics-hl/*.json
    computer-science-hl/*.json
    business-management-sl/*.json
  site/                     generated output (committed, so it can be served from file:// or Pages)
    index.html              home: cohort note, difficulty legend, subject cards
    math-aa-hl/index.html   topic list + filters (topic, paper, difficulty, command term)
    physics-hl/index.html
    computer-science-hl/index.html
    business-management-sl/index.html
    q/<id>.html             one page per question: stimulus, question, then collapsed
                            "Reveal answer / markscheme / why it's hard"
    papers/*.html           assembled printable practice papers + matching answer booklets
    assets/                 local CSS + search JS (self-contained so it deploys anywhere)
```

Commands:

```
python3 build.py              # validate data/ and regenerate site/
python3 build.py --check      # validate only, write nothing
python3 tools/similarity_check.py           # originality gate, report only
python3 tools/similarity_check.py --write   # also record scores in data/
```

Design decisions:

- **Self-contained `assets/`** (CSS + JS + KaTeX/MathJax local-or-CDN) so the folder can be deployed
  standalone (GitHub Pages) or opened from `file://`. Data loads as JS globals, not `fetch()`, for the
  same reason the existing site does it — `fetch()` is blocked on `file://`.
- **Answer-hiding is first-class:** question page shows the question only; three separate toggles for
  *Answer*, *Markscheme notes*, *Why it's hard*. Printable versions put all answers in a separate
  booklet.
- **Every question shows its metadata** — syllabus ref, marks, difficulty, command terms, challenge
  lever, and its originality score. Nothing is anonymous.
- **Filter + full-text search** across the bank (small corpus, so a client-side index is fine).
- **Cross-nav** to the other four spaces (DP Learning, Question Bank, Python Mastery, Lit Lab) so it
  feels like one system, plus a link back from the main `index.html`.
- **Also emitted:** `challenge-bank/export/<subject>.json` in the shape `backend/src/import.js`
  accepts, so anything here can be pushed into the main bank later if you want it there.

---

## 8. Authoring workflow and gates

Per batch (one subject, one topic cluster):

1. **Calibrate** — read 10–15 real items from `app.db` on that topic; record command terms, marks per
   part, phrasing, marking-annotation conventions. Output: a short style note, not questions.
   (For CS, calibrate against the specimen/2027 material rather than the legacy papers.)
2. **Design** — pick syllabus bullets + challenge lever + fresh context. Write the *answer* first
   (this is what makes the question well-posed), then the stem.
3. **Author** — write question, stimulus, figure, markscheme, explanation, metadata.
4. **Verify**
   - Maths: recompute symbolically/numerically (sympy/mpmath), check domain/edge cases, confirm the
     P1 items are genuinely doable without a GDC and P2/P3 items use technology meaningfully.
   - Physics: dimensional analysis, recompute every number, check SF/units, confirm the constants used
     are in the 2025 data booklet, check the scenario is physically possible.
   - CS: actually run the Python and Java solutions; trace the pseudocode; confirm HL-only tagging.
   - BM SL: rebuild every figure in the stimulus in a spreadsheet-like check; confirm the case study is
     internally consistent; **sweep the whole item against the HL-only list in §2.4**; confirm the
     evaluation asks for a decision, not a description.
5. **Originality scan** — §5 gate. Fail → rewrite or drop.
6. **Difficulty audit** — if any part is trivial filler, either deepen it or remove it and reduce marks.
7. **Publish** — merge into `data/`, run `build.py`, smoke-test the generated pages.

Nothing ships at difficulty 1–2, nothing ships below the mark floor, nothing ships without a passing
similarity score, and no BM item ships containing HL-only content.

---

## 9. Milestones

- **Batch 0 (calibration, 4 questions) — DONE.** One per subject, all difficulty 4:
  `MATH-AHL5.18-001` (P1, 15 marks — constant-area tangent condition leading to a differential equation
  that only solves once x is treated as a function of y) · `PHYS-D.1-001` (P2, 15 marks — two-burn
  Hohmann transfer to geostationary orbit, ending in the launch lead-angle) · `CS-B4.1-001` (P2, 16 marks
  — the no-code algorithmic-thinking type: ADT choice quantified at 40 000 plates/day, two-finger merge,
  BST degeneration on sorted keys) · `BM-5.5-001` (P2, 15 marks — channel-mix campaign where break-even
  and margin of safety both worsen while expected profit improves).
  All four pass the originality gate at ≤ 0.017 against the 12,796-question corpus (threshold 0.35).
  These set the register; everything after this is measured against them.
- **Batch 1 (topic sweep) — DONE.** Four more per subject, so that every syllabus topic area now has at
  least one item. All 20 pass the originality gate (highest score 0.049 against the 12,796-question
  corpus). Maths: T1 roots of unity → exact trig values (P1, 14), T2 self-inverse rational family with a
  degenerate case (P1, 14), T3 skew lines → plane → shortest distance (P1, 14), T4 Bayes with an
  irrelevant stopping rule (P2, 16), T5 the constant-area DE. Physics: A.5 relativistic journey with
  implicit $\gamma$ (P2, 15), B.4 rectangular thermodynamic cycle vs Carnot (P2, 16), C.5 double Doppler
  shift with a derived small-speed approximation (P2, 15), D.1 Hohmann transfer, E.3 two-isotope mixture
  recovering initial activities (P2, 15). CS: A1 hardware/GPU/data-rate/compilation (P1, 16), A2 network
  sizing and segmentation (P1, 16), A3 3NF decomposition and SQL (P1, 16), A4 ML preprocessing and
  proxy bias (P1, 16), B4 ADTs and merge (P2, 16). BM SL: U1 legal form vs irreconcilable objectives
  (P1, 14), U2 flat structure and why a pay rise fails (P1, 14), U3 profitable but illiquid (P2, 14),
  U4 revenue-maximising vs contribution-maximising price (P2, 14), plus the channel-mix item.
- **Batch 2 — DONE.** Four more per subject (36 total), taking every subject to 9 items. CS reached
  24/25 nodes. All items pass the quality gate and the originality gate.
- **Batch 3 — DONE.** Four more per subject (52 total), 13 per subject. Maths: T1.10 the C(n,4)
  crossing-count bijection that fails on the regular hexagon (P2, 16, d5) · T1.11 partial fractions
  that do not telescope in the obvious form (P1, 14, d4) · T1.12 solving $z^{n}=\bar z$ and inverting
  the condition to $n\equiv5\pmod 6$ (P1, 16, d5) · T1.14 the condition for a real cubic to have a
  purely imaginary root (P2, 16, d4). Physics: A.2 the ball that rebounds to 7.89h (15, d5) · A.3 why
  the conveyor motor needs twice the expected power (16, d5) · B.1 recovering emissivity and specific
  heat from two vacuum-chamber readings (16, d4) · B.2 the one-layer atmosphere that always adds a
  factor $2^{1/4}$ (16, d4). CS: A3.1 a flat-file schema whose cascading delete destroys 240 000
  journey records a year (P1, 16, d4) · B2.1 the float money bug where forty £0.10 subtractions never
  reach £16.00 (P2, 16, d4) · B2.3 a nested loop that is $O(n)$ only while the data keeps moving
  (P2, 16, d5) · B2.5 streaming a 40 GB file through 8 GB of RAM in one pass (P2, 16, d4). BM:
  1.1 two ways to add value that rank the options in opposite orders (P1, 14, d4) · 3.1 a funding plan
  that balances on assumptions the bank has already refused (P2, 14, d4) · 5.1 a 20% productivity gain
  that makes each garment worth less (P2, 14, d4) · 5.2 a flow line that is cheaper per bench and
  dearer per year (P2, 15, d4).
  The whole bank is now **52 questions · 88/166 nodes covered (53%)**, with `validate.py --strict`
  reporting **0 failures and 0 warnings** and the originality gate clean at a highest external score
  of 0.049 and a highest internal score of 0.022.
- **Batch 4 — DONE.** Ten more items (62 total), drawn from the top of the gap list. Maths (5):
  1.15 an induction whose naive hypothesis is provably too weak, so the student must strengthen it to
  $S_n\le\frac32-\frac1n$ (15, d5) · 2.12+2.14 symmetry stated as $f(2+t)+f(2-t)=4$, i.e. oddness about
  $(2,2)$, with the coefficient pinned by a repeated root (15, d5) · 3.10+3.11 a compound-angle
  expansion that reproduces the double-angle factor and whose squaring invents two extraneous roots
  (15, d5) · 3.12+3.15 a scalar triple product of $k(k-1)$, so a zero determinant occurs at two values
  of $k$ for different reasons and can never settle the classification (16, d5) · 5.16+5.17 an implicit
  circle offset from both axes, where the $y$-axis area exists only after rejecting a branch (15, d4).
  Physics (4): C.1+C.2 coupled gliders in which the coupling spring never stretches, so the period is
  set by the wall springs alone and the stiffness cancels (16, d5) · C.4 touching a string at $3/8$ of
  its length forces the node condition $d=jL/n$, so the lowest note is the eighth harmonic, not the
  third (16, d5) · D.2+D.3 an undeflected reading that fixes only $E/B$, leaving the trajectory blind to
  a common rescaling (15, d5) · E.1+E.2 two stopping voltages, each one equation in two unknowns, where
  only their difference cancels the work function (16, d5). CS (1): B3.2 a superclass constructor that
  calls an overridden method, so the subclass field is read before assignment and the cached fee
  silently falls back to the class default — the bug survives every test its author wrote (16, d5).
  **CS is now complete at 25/25.**
  Whole bank: **62 questions · 105/166 nodes (63%)**, `validate.py --strict` clean at 0 failures and
  0 warnings, originality clean at 0.048 external / 0.022 internal.
- **Assertions backfilled across the whole bank — DONE.** All 62 items now carry
  `verification.assertions` (558 assertions). Making the machine check universal repaid its cost
  immediately by exposing three genuine defects that had survived review: `CS-B4.1-001` quoted the
  *average* comparison count (8×10⁸) where its own part asks for the worst case (1.6×10⁹) — the very
  error its explanation warns against; `BM-5.5-001` stated an expected-value gain of €17 040 where its
  own two EVs give €17 064; and `BM-4.5-001` illustrated the revenue/contribution conflict with a
  5 000-bottle gap taken from the wrong pair of prices. All three are corrected.
- **Batch 5 — DONE.** Eight more items (70 total), and with them **every priority-1 node in the bank is
  covered**. Maths (2): 3.9 the reciprocal ratios, where multiplying $\csc x-\cot x=1$ through by
  $\sin x$ is irreversible at the zero of $\sin x$ and so invents the root $x=0$, after which the
  reduced form in $\tan(x/2)$ gives $k=0$ no solution at all (15, d5) · 5.12+5.15 a piecewise function
  where continuity at each join forces one parameter relation and differentiability an independent
  slope relation, so a whole parameter family is continuous but **not** differentiable (15, d5).
  Physics (2): E.4 fission, where the energy per fission is fixed by the mass defect and so is *not*
  moved by enrichment or moderation — only the reaction rate is (16, d5) · E.5 fusion and stars, where
  the triple-alpha yield is a difference of *total* binding energies, so each per-nucleon figure must
  first be multiplied by its mass number (16, d5). BM (4, covering the eight Toolkit nodes 6.1–6.8):
  the factor management calls its leading strength is reclassified as a threat once STEEPLE is run
  (6.1+6.3, 15, d4) · BCG says harvest the cash cow while Ansoff makes the same product's market
  development the only low-risk growth, and the BCG label flips from cash cow to dog with the market
  definition (6.2+6.4, 15, d4) · a bimodal twelve-month trial gives an empirical probability of 5/12
  that replaces management's assumed 0.6 and reverses the expected-value ranking (6.6+6.7, 16, d5) ·
  a 3.8-year payback resting on twenty reuses per bottle against six achieved and a break-even of
  seven, setting the bank's payback rule against the founders' zero-waste goal (6.5+6.8, 15, d4).
  Whole bank: **70 questions · 118/166 nodes (71%)**, `validate.py --strict` clean, 680 machine-checked
  assertions. Physics, CS and BM are each at **100% of their must-cover nodes**; only maths priority-2
  topics remain.
- **Batch 6 — DONE.** Ten more items (80 total), the first batch drawn entirely from the priority-2
  maths tail. Maths Topic 1 (seven items): 1.1+1.5 a metallurgy sample whose mass is quoted in kilograms
  while the atomic mass is quoted in grams, so the ratio 60 and the atom count only agree after the
  mismatch is repaired and the factor of $10^3$ slip is asked for explicitly (15, d4) · 1.2+1.3 a
  recurrence whose successive differences are exactly geometric, so the general term must be built by
  summing them rather than from either standard formula (15, d4) · 1.4 an annuity in which the €900
  instalment overshoots, leaving 57 full payments and a final payment of €612.61 that has accrued one
  further month of interest (16, d5) · 1.6 the infinite-descent proof that $a^2+b^2=3c^2$ has no
  positive solution, contrasted with modulus 2 where the same congruence no longer forces both terms
  even (15, d5) · 1.7 a substitution whose quadratic has two roots, of which only the odd index of the
  cube root lets the negative one survive (15, d4) · 1.8 a geometric series whose data produce two
  legitimate roots for $r$, of which the convergence condition forbids $r=3/2$ (16, d5) · 1.9 a
  binomial whose consecutive-coefficient ratio equals one at an integer index, so the greatest
  coefficient $1001/16$ is attained twice (16, d5). Maths Topic 2 (four items): 2.1 a family of lines
  in which one parameter value makes the coefficient of $y$ vanish, so the usual gradient expression
  fails exactly at the member required, and the area condition collapses to $(4k+5)^2=0$ (15, d4) ·
  2.2+2.3 a composite function whose algebraic cancellation deletes one input, leaving one value
  missing from the range (15, d4) · 2.4+2.8 the reciprocal function, where taking $1/f$ swaps the zeros
  and the poles and the resulting inequality depends on which critical values are poles (16, d5).
  Whole bank: **80 questions · 132/166 nodes (79%)**, `validate.py --strict` clean, 819 machine-checked
  assertions.
- **Batch 7 — DONE.** Ten more items (90 total), finishing Topic 2 and opening Topic 3. Topic 2 (five
  items): 2.6 a quadratic whose leading coefficient carries the parameter, so the curve silently
  becomes a straight line at $m=1$ and the discriminant is $4(m+3)$ (16, d4) · 2.7 an inequality whose
  discriminant is $-8k-4$, so "positive for all $x$" needs the leading-coefficient condition and the
  discriminant condition to agree, and $k=-1$ degenerates to a linear case (16, d5) · 2.9 the
  exponential pair $3^x$ and $3^{-x}$ as reflections, plus the range $0<k<4$ that keeps both roots of
  $3^{2x}-4\cdot3^x+k=0$ positive (16, d4) · 2.10 the syllabus's own $e^{2x}-5e^x+4=0$, where the
  substitution forces both roots positive, the minimum is $-\frac94$ at $x=\ln\frac52$ and "no real
  solutions" means $k>\frac{25}{4}$ (16, d5) · 2.11 a horizontal stretch and translation that do not
  commute, so the translation is 6 units in one order and 3 in the other (16, d5). Topic 3 (five
  items): 3.1 collinear points in 3D with two points on the line exactly three units from the origin
  (16, d4) · 3.2+3.3 the **ambiguous case**, where $AB=6$, $BC=2\sqrt3$ and $\angle BAC=30^\circ$ admit
  two triangles with $CA=4\sqrt3$ or $2\sqrt3$ and areas $6\sqrt3$ or $3\sqrt3$ (16, d5) · 3.3 an area
  of 42 cm² that fixes $\sin Q=0.8$ but not the sign of $\cos Q$, giving $PR=2\sqrt{37}$ or $20$ and
  perimeters 34.2 or 42 (16, d5) · 3.4 a sector of perimeter 20 cm whose area $10r-r^2$ has two roots
  for a given area but only one admissible, because the other forces an angle beyond $2\pi$ (16, d4) ·
  3.5–3.8 the unit circle and Pythagorean identity, where two sign conditions pin the quadrant and the
  periodic count of solutions over $[0,10\pi)$ is required without ever recomputing the angle (15, d4).
  Whole bank: **90 questions · 145/166 nodes (87%)**, `validate.py --strict` clean, 961 machine-checked
  assertions.
- **Batch 8 — DONE.** Ten more items (100 total), completing the whole of Topic 4 (statistics and
  probability). 4.1 nine recorded masses where one value is an outlier: the mean sits at 12 above the
  median at 9, the $1.5\times$IQR fence is 19 and removing the 40 collapses the two averages together
  at 8.5 (16, d4) · 4.2 five classes of **unequal width**, so frequency density rather than frequency
  must be plotted and the tallest bar is not the densest class; the median must be interpolated to 7,
  with IQR 6 and $P_{90}=15$ (16, d4) · 4.3 two data sets sharing the mean 6 while their standard
  deviations are $\sqrt2$ and $2\sqrt2$, and a coding $w=1.5x-4$ that must be **inverted** rather than
  reapplied (16, d4) · 4.4 summary statistics giving $r=0.8$ and $r^2=0.64$, paired with the refusal to
  infer causation (16, d5) · 4.5 six equally likely pairs from $\{1,2,3,4\}$, where replacement rebuilds
  the sample space from 6 outcomes to 16 (16, d4) · 4.6 $P(H\cup G)=0.8$, $P(H\mid G)=\frac59$ and
  $P(G\mid H)=\frac5{12}$ show dependence, yet conditioning on the union instead gives $\frac5{16}$
  (16, d4) · 4.8 the binomial $n=8$, $p=0.3$ where "at least one" is a single complement rather than a
  nine-term sum and the trial count must be solved as an inequality, the smallest $n$ being 13 (16, d5) ·
  4.10 the two regression lines $y=-0.6+0.8x$ and $x=4.5+0.5y$, where rearranging the first to make $x$
  the subject yields the plausible but wrong $x=1.25y+0.75$ (16, d4) · 4.11 a weighted defective rate
  $P(D)=0.038$ with $P(B\mid D)=\frac{10}{19}$, and independence decided by comparing a conditional
  probability with an unconditional one (16, d5) · 4.12 z-values and the inverse normal, where the same
  $z=1.2816$ rescales from 165.379 at $\sigma=12$ to 169.223 at $\sigma=15$ (16, d4).
  Whole bank: **100 questions · 155/166 nodes (93%)**, `validate.py --strict` clean, 1053 machine-checked
  assertions.
- **Batch 9 — DONE.** Eleven more items (111 total), completing **Topic 5 (calculus)** and therefore
  every priority-2 node in the bank — the whole syllabus is now covered at 166/166 (100%). 5.1 the
  two-sided limit that vanishes because the one-sided limits disagree (RHL 2, LHL −2) (16, d4) · 5.2 the
  cubic whose derivative 3(x−3)(x+1) changes sign twice for a max at (−1,10) and a min at (3,−22)
  (16, d4) · 5.3 the derivative that keeps the negative power −6x⁻⁴, giving a fractional gradient 75.625
  at x=2 (16, d4) · 5.4 the tangent and normal to y=2x²−3/x, with a reciprocal derivative and a normal of
  gradient −1/7 (16, d4) · 5.5 rebuilding f from f′ and the single point f(1)=5, so the definite integral
  equals the net change 8 (16, d4) · 5.6 the product x⁴ln x whose stationary point is the irrational
  x=e⁻¹ᐟ (16, d5) · 5.7 the second derivative 12(x−1)(x−3) that changes sign at two points for two
  inflections (16, d4) · 5.8 the cubic (x−1)²(x+2) classified by the linear second derivative 6x
  (16, d4) · 5.9 the particle that stops twice and travels three equal legs for a total distance 12 m,
  not the net displacement 4 m (16, d5) · 5.10 the indefinite integral of a four-form mix whose
  antiderivative combines a logarithm with a cosine and is pinned to F(1)=7 (16, d5) · 5.11 the area
  between the parabola y=x²−4 and the line y=2x−1, equal to 32/3 with the right-hand part 9 (16, d5).
  Whole bank: **111 questions · 166/166 nodes (100%)**, `validate.py --strict` clean, 1108 machine-checked
  assertions, originality clean at 0.090 external / 0.042 internal.
- **Batch 10 — DONE (priority-3 stretch).** Three more items (114 total), the optional deeper/harder tail
  beyond the must/should nodes — the only AHL 5.x bullets with no *dedicated* question (5.12/5.16/5.17/5.18/5.19
  already had dedicated items, and 4.7/4.9 are cross-referenced). 5.13 l'Hopital's rule pushed past one pass
  (limits 1/3 and 1/6, plus the polynomial-vs-exponential 0) (16, d5) · 5.14 related rates on a 13 m sliding
  ladder solved by implicit differentiation, with the reversed part (given the rate, find the position) giving
  $x=2\sqrt{169/5}$ (16, d4) · 5.15 the derivative of $\arctan x$ derived by implicit differentiation of
  $x=\tan y$, then used for $\pi/4$ and $\pi/12$ (16, d4).
  Whole bank at that point: **114 questions · 166/166 nodes (100%)**.
- **Batches 11+ — DONE (paper and question-type expansion).** With all 166 syllabus nodes already
  covered, the remaining gap was the *paper* a question belongs to and the *kind* of question it is, so
  the bank was extended along that axis. 53 further items took the whole bank to **164**:
  - **Physics 19 → 46.** The P1A multiple-choice clusters (13 items, one mark per question) and the P1B
    data-based clusters (11 items), plus a P2 extended batch. The approaches used are listed in
    STANDARD.md §4.6 — for P1A, rigid-body rotation, induction, circuits, photons and the photoelectric
    effect, relativity, a source-moves/observer-moves Doppler pair, and a fields item with a spurious
    root that fails the direction test; for P1B, linearising then reading a gradient, a log–log
    exponent, trapezium integration of a tabulated force, residual-pattern analysis, a reciprocal plot
    whose intercept is a zero error, and the half-power width of a resonance curve.
  - **Computer Science 14 → 24.** P1 structured items (cache hierarchy → Amdahl → a clock-scaling step
    that fails; VLSM subnetting under a boundary constraint) and P2 case-study items (binding-constraint
    architecture split, ADT selection against every operation, imbalanced-data metrics, concurrency and
    deadlock, protocol design with a threat model, legacy-migration phasing).
  - **Maths 61 → 75.** The P3 inquiry set and further Paper 3 problem-solving items.
  - **Business Management SL 17 → 19.** P1 case studies, including an HR restructure and a market-entry
    decision using Ansoff with STEEPLE.
  Two tool changes shipped with this work: `validate.py` gained `question_type`, `PAPER_TYPES` and
  `TYPE_RULES` (a declared type is now checked against the paper that actually carries it), and
  `similarity_check.py` gained the approach gate over `solution_skeleton`.
  Whole bank: **164 questions · 166/166 nodes (100%)**, `validate.py --strict` clean at 0 failures and
  0 warnings, **1652** machine-checked assertions, originality clean at 0.090 external / 0.073 internal /
  0.356 approach.
- **Batch 12 — DONE (figures + the difficulty standard).** Eight figure-bearing items were added, one per
  figure file, taking the bank to **172** questions and **1762** assertions: an Argand locus, a normal
  distribution band, a velocity–time MCQ cluster, a spring-extension dataset with a seeded anomaly, a
  series circuit with internal resistance, a standing wave, an office network, and a BST operations
  figure. The same batch changed what a difficulty label *means*:
  - **`difficulty_evidence` is now required** — `{lever_type, naive_path, failure_point, wrong_answer}`,
    with `lever_type` drawn from a closed 13-term taxonomy. An unknown term is a failure, not a warning.
  - **The label must be earned by a 9-point rubric**, and difficulty 4 or above additionally requires all
    three evidence fields to be substantive and mutually distinct. The rubric was rewritten three times
    during the batch, each time because a test fired on correct work rather than on a defect.
  - **`tools/difficulty_audit.py` is a new pipeline stage** (stage 4, `--check`), because `validate.py`
    structurally cannot see that 46% of the bank claimed difficulty 5 while none claimed 3.
  - **`provenance.source_family` is now recorded** for all 172 items, from a closed 10-term list covering
    the IB, 高考, 强基, 竞赛, A-Level, Further Maths, AP and Singapore A-Level families, so that
    cross-syllabus sourcing is a recorded fact rather than a claim. Non-original families must also name
    `provenance.resource_origin`.
  - The eight items carrying evidence all score 9 of 9, so **no label had to be lowered**. One false
    `challenge_mechanism` was corrected: `MATH-AHL1.13-101` asserted a trap its own answer contradicts.
  - The bank's advertised `0 failures · 0 warnings [strict]` invariant is **deliberately broken** by this
    batch: the grandfathered items now warn (164 of them) instead of silently passing. The backlog is a
    published number that must fall, and no batch may add to it.
- **Batch 13 — DONE (cross-syllabus sourcing + the figure pipeline).** Six items took the bank to
  **178** questions, **1833** assertions and **32** figure-bearing items. The brief for this batch was
  explicit: keep the Batch 12 quality bar, take material from *other* syllabuses rather than inventing
  everything, and make some — not all — of the items graphic.
  - **Where the six come from.** Only one of the six is `original`; the other five are adaptations, and
    each names `provenance.resource_origin` and `provenance.adaptation`. `uk-further-maths` supplied the
    Maclaurin-recurrence item, `china-gaokao` supplied two (the root-interval width and the rod on
    rails), `china-competition` supplied the spool, and `uk-alevel` supplied two (translation strategies
    and the purchase-intent survey). In every case at least two of context, structure, given-vs-asked and
    reasoning chain were changed, so the difficulty is carried by the rewrite and not borrowed from a
    harder syllabus's content.
  - **The six items.** `MATH-P3-012` (P3, 14, d5, `decoy_technique`): $y' = 1 + xy$ is solved by a
    Maclaurin recurrence rather than by the integrating-factor routine the chapter teaches, and the two
    subseries have to be recognised separately — the even one is $e^{x^2/2}$ — before $f(1) = 3.059$ is
    reachable. `MATH-AHL2.12-101` (P1, 13, d4, `non_governing_variable`): the interval on which
    $x^3-3x+1 = k$ has three roots is widest at the *middle* level, $2\sqrt3$ at $k = 1$, not at the ends
    where the graph looks widest. `PHYS-A.4-103` (P2, 15, d5, `binding_constraint`): a spool pulled at
    the underside of the hub reverses its rolling direction at $\cos\theta = r/R$, and the constraint
    that actually binds is slipping at $T = 4.42$ N, not $\mu_s mg$. `PHYS-D.4-102` (P2, 15, d5,
    `non_governing_variable`): a rod on rails travels a distance proportional to $R$ while the charge
    that flows does not depend on $R$ at all, and the impulse route avoids integrating $I(t)$.
    `CS-A1.4-001` (P1, 16, d4, `wrong_design_cost`): the obvious comparison is $0.010$ ms against
    $0.050$ ms; the comparison that decides the question is their difference, $0.040$ ms, which puts the
    interpreter/compiler break-even at $N = 150$ and makes compiling roughly $120\times$ *slower* for a
    script run once. `BM-4.4-001` (P2, 15, d4, `non_obvious_tool`): a purchase-intent survey in which the
    headline rate falls from 29.5% to 25.5% even though every age band rose five points, so the rate has
    to be standardised before it is forecast — 270,000 buyers, not the director's 229,500.
  - **Three of the six are graphic, three are not**, which was the requirement. `tools/make_figures.py`
    gained three generators — `cubic_three_roots`, `spool_pull` and `jit_cost_curves` — and
    `data/_figures.json` now holds 11 SVGs. Authoring uses an `@@name@@` placeholder in
    `question.figure.content`, which is replaced by the generated SVG before the batch is validated, so
    the figure is data rather than a hand-edited blob.
  - **All six score 9 of 9** on the difficulty rubric, so no label had to be lowered, and the six add
    **71** machine-checked assertions. Originality is clean at 0.030 external / 0.025 internal / 0.127
    approach for the new items; the bank-wide maxima are unchanged at 0.090 / 0.073 / 0.356.
  - **One debt got slightly worse and it is recorded.** Physics HL moved from 62% to 63% of its items at
    difficulty 5, because two Physics items shipped and both genuinely earn d5. That is inside the 2-point
    regression slack, so `--check` still passes, but only **0.5 points of headroom remain** before it
    becomes a hard failure. The rule is now written down: the next Physics item may not claim difficulty 5
    until the share is back at or below 62%. The labels were left alone deliberately — lowering a label
    that the evidence supports would fix a statistic and break the standard.
- **Batch 14 — DONE (A-Level / AP / 高考, rewritten into IB form).** Six items took the bank to **184**
  questions and **1902** assertions. The brief was to mine three named syllabuses — A-Level, AP and
  高考 — for genuinely hard material and then convert it to IB style and IB testing method, not to
  translate the words and leave the question intact.
  - **What "IB form" was taken to mean, concretely.** Every item uses IB command terms drawn from the
    recognised list; every method mark is annotated `(M1)(A1)(R1)(AG)` at the point it is earned; every
    part carries an explicit condonation, follow-through and forfeiture rule in `markscheme_notes`;
    anchors are written as `Show that` so the answer is marked on the working and not on the result,
    which is the IB convention and not the A-Level, AP or 高考 one; and answers are given exact where the
    source would accept a decimal, or to three significant figures with units where IB requires it.
  - **The six items.** `MATH-AHL5.18-102` (P2, 16, d5, `derived_limit`, **us-ap**): the logistic equation
    arrives as the expanded polynomial $0.4P - 0.0002P^2$, so the carrying capacity must be recovered as
    the ratio $0.4/0.0002 = 2000$ before the model can be recognised at all; the time at which $P = 1000$
    turns out to be exactly the instant of maximum growth. `MATH-AHL5.16-102` (P3, 15, d5,
    `variable_swap`, **uk-alevel**): the reflection substitution $u = \pi/2 - x$ does not simplify the
    integrand, it swaps $\sin$ and $\cos$ and returns an integral of the same difficulty; adding the two
    gives $I = \pi/4$, the argument generalises to any positive continuous $f$, and a final part asks
    where the generalisation does *not* apply. `PHYS-A.1-103` (P2, 15, d4, `implicit_dependence`,
    **china-gaokao**): range of a projectile on an inclined plane; $\alpha$ and $\beta$ enter only through
    $2\alpha - \beta$, so the optimum is $\alpha = 45^\circ + \beta/2$, and using the flat-ground
    $45^\circ$ costs $6.3$ m out of $68.4$ m. `PHYS-A.4-104` (P2, 15, d4, `aggregate_recovery`,
    **us-ap**): an Atwood machine with a massive pulley, where the effective inertia $m_1 + m_2 + I/R^2$
    has a term that has the units of mass and is not a mass; inverting the formula shows that halving the
    acceleration needs $4.8$ times the moment of inertia, not twice. `CS-B2.4-002` (P1, 16, d4,
    `exceptional_parameter`, **us-ap**): an array-run method that is correct on ordinary tests and fails
    for exactly two classes of input, and where the plausible one-line repair fixes one class and not the
    other. `BM-3.5-002` (P2, 15, d4, `quant_vs_judgement`, **uk-alevel**): a ratio analysis in which ROCE
    and absolute profit improve while both margins and both liquidity ratios deteriorate, and where the
    expansion returns $25.6\\%$ against a current ROCE of $18.3\\%$ yet drops the acid test ratio to $0.41$ —
    the project is sound and the overdraft is not.
  - **Two structural decisions are worth recording.** First, both Physics items were written at
    **difficulty 4 with heavier `Show that` scaffolding**, deliberately. Batch 13 had pushed Physics to
    63% difficulty 5, and the rule written then was that the next Physics item might not claim 5. Rather
    than relabel an earned d5 — which fixes a statistic and breaks the standard — the new items were
    *designed* to be d4. It worked: **Physics fell from 63% to 61%, below the 62% baseline**, so the debt
    is being paid down the intended way. Second, six previously unused levers were brought in, taking the
    bank from **7 to 12 distinct levers of 13**, and dropping the largest share from 43% to 30%.
  - **Gates.** `validate.py` reports **0 failures** and the six add no new warnings (backlog steady at the
    164 grandfathered items). Originality is clean at 0.028 external / 0.012 internal / 0.147 approach for
    the new items, and the bank-wide maxima are unchanged at 0.090 / 0.073 / 0.356.
    `difficulty_audit.py --check` passes and `prove_difficulty_gates.py` holds all 10 cases.
  - **`us-ap` was previously unused** and is now represented by three items; `uk-alevel` by four and
    `china-gaokao` by seven.
- **Batch 15 — DONE (significant expansion: 18 items, 184 → 202).** The largest single batch so far,
  and the first deliberately planned as a volume expansion rather than a targeted top-up. Six Maths,
  five Physics, four Computer Science, three Business Management. Every item carries
  `difficulty_evidence`, `provenance` and machine-checked `verification.assertions`, so the batch
  raises the evidenced count from 20 to **38 of 202** while adding **186 assertions** (1902 → 2088).
  - **Two source families were used for the first time.** `singapore-alevel` (`MATH-AHL3.17-102`, a
    constrained-optimisation problem where the governing variable is the one the candidate is not asked
    about) and `china-qiangji` (`MATH-AHL5.11-102`, an improper integral whose singularity sits inside
    the interval, so the area is infinite despite the curve being positive and the limits looking
    finite). With these, seven of the ten families are represented and `original` has fallen to 166 of
    202.
  - **`partial_cancellation` — the last unused lever — is now in use twice.** `MATH-AHL5.19-102`
    (P3, 14, d5, uk-further-maths) and `BM-3.8-002` (P2, 16, d4, uk-alevel) both turn on a term that
    cancels from one comparison and not from another. In the BM item two machines carry an identical
    decommissioning charge and the obvious move is to cancel it; but one machine is replaced mid-period
    and decommissions twice, so **only the year-4 payment cancels** and the year-2 payment, worth
    £16,529 in present value, is the single term that decides the question — and it overturns a gap of
    £10,826. The final part asks for the charge at which the recommendation flips: **£13,100**.
    **All 13 lever types are now in use**, and the largest single share is down to 18% of evidenced
    items from 43% three batches ago.
  - **The Physics calibration debt was designed down again.** All five new Physics items were written
    at difficulty 4 from the outset rather than labelled down, continuing the Batch 14 mechanism. The
    Physics difficulty-5 share therefore falls **61% → 56% (33/59)** against a 50% cap and a 62%
    baseline. The rule that no new Physics item may claim difficulty 5 until the share reaches 50%
    still stands, and Batch 15 is the first batch in which that rule shaped the design.
  - **Three of the eighteen are graphic** (`improper_singularity`, `echo_doppler`, `bdp_window`), and
    `tools/make_figures.py` gained those three generators: `data/_figures.json` now holds 14 SVGs.
  - **Gates.** `validate.py` reports **0 failures** on 202 questions, and the eighteen add no new
    warnings beyond the expected "originality not yet scanned" (backlog steady at the 164 grandfathered
    items). Originality is clean — new items peak at 0.029 external / 0.038 internal / 0.294 approach
    — and the bank-wide maxima are unchanged at 0.090 / 0.073 / 0.356. `difficulty_audit.py --check`
    passes and `prove_difficulty_gates.py` holds all 10 cases.
- **Batch 16 — DONE (6 Maths P3 items, 202 → 208; plus the topic-label work).** Six Paper 3
  problem-solving items, every one adapted from a Chinese genre and rewritten into IB form: 极值点偏移
  (extremum-point shift), the series solution of an equation with no elementary solution, 概率递推
  (recursive probability), 计数递推 / 卡塔兰数 (counting by recurrence), 数列不等式放缩 (estimation of a
  series by comparison) and 解析几何定值 (invariance in analytic geometry). Evidenced count **38 → 44**;
  assertions **2088 → 2174**. Chinese sourcing rises from 14 to **20 items** (`china-gaokao` 10 → 14,
  `china-qiangji` 3 → 5).
  - **Every item was verified numerically before its prose was written, and two of my own designs were
    wrong.** The planned root-count for `x^2 e^-x = a` had missed the left branch (there is always a
    solution as x → -∞, so the answer is `a = 0 or a > 4e^-2`, not a tangency interval), and the coin
    item's crossover was checked rather than assumed. Six distinct levers are used, one per item, with no
    repeats: `implicit_dependence`, `decoy_technique`, `non_governing_variable`, `non_obvious_tool`,
    `binding_constraint`, `exceptional_parameter`.
  - **The calibration gate caught this batch, and the batch was changed rather than the gate.** Six new
    difficulty-5 items took Math AA HL to **51%** of items at difficulty 5, over the 50% cap — the exact
    "everything is a 5" defect §2.5 exists to prevent. All six scored 9/9 on the rubric, so the rubric
    alone would have allowed the label; the cap is a separate and deliberate constraint. On re-reading,
    `MATH-P3-015` (the coin item) is genuinely a 4: parts (a) and (b) *name the states*, so the derivation
    is forced and the rarity misconception cannot quietly survive — the item teaches rather than traps,
    and its `challenge_mechanism` now records that reasoning. Math AA HL sits at **49% (46/93)**.
  - **The topic label became a real label.** Every item already carried `topic`, but it was used only for
    search: it was never displayed, the subject index had no topic filter, and the same topic appeared
    under several names — Computer Science Theme A under *three* ("Concepts of computer science" 17,
    "Computer fundamentals" 1, "Systems in organisations" 3) and BM Unit 3 under two ("Unit 3:" and
    "Topic 3:"). The names were checked against the 2027 CS guide, which defines **exactly two** themes
    and places "Computer Fundamentals" (A1) and "Programming" (B2) *inside* them as strands. Eleven items
    were normalised by `tools/normalise_topics.py`; `validate.py` now holds a closed `TOPICS` vocabulary
    per subject and **fails** on an unknown label, proved non-vacuous on 12 cases including all five that
    were really in the bank. The topic now renders as a chip on every question page, appears in the
    metadata block and the global search index, and filters every subject page.
- **Batch 17 — DONE (8 Physics HL items, 208 → 216; and the Physics debt cleared).** Eight Paper 1/2/3
  Physics items spanning all five themes, every one at difficulty 4, on the explicit instruction to stop
  adding Physics d5 items until the share reached the 50% cap. Lever types are all distinct:
  `implicit_dependence`, `exceptional_parameter`, `decoy_technique`, `variable_swap`, `partial_cancellation`,
  `binding_constraint`, `derived_limit`, `seeded_anomaly`.
  - **Every number was recomputed from first principles before any prose was written.** A pulley with a
    non-negligible moment of inertia, ice that does not all melt, a rectangular pV cycle against a Carnot
    decoy, a point source with incoherent addition in dB, closed-pipe resonances where the end correction
    cancels, a charged drop with upward acceleration equal to g, a velocity selector, and a photoelectric
    data set with a seeded anomaly at 7.00×10¹⁴ Hz.
  - **The generator's self-check caught four false assertions and one silent data-loss bug.** Two of the
    assertions divided by `mg` twice and two had a malformed regression and a wrong-direction inequality;
    all four were fixed by re-expressing them. The data-loss bug was more serious: `item()`'s key list
    omitted `stimulus` and `figure`, so the data table for the photoelectric item was accepted as an
    argument and then silently dropped, and the item shipped as a `data_based` question with no data.
    `item()` now **raises** on any unknown keyword so this class of defect cannot recur.
  - **Outcome: Physics HL 56% → 49%.** The calibration gate reports no debt for any subject for the first
    time. The full pipeline passed including the originality scan: **0 items above threshold**, highest
    external 0.044, highest internal 0.073, highest approach 0.356.
- **Batch 18 — DONE (4 Maths, 2 CS, 2 BM; 216 → 224).** Weighted as asked — Physics and Maths are 12 of
  the 16 items across Batches 17 and 18, with CS and BM represented but not competing for attention.
  - **Maths ×4.** A telescoping sum whose cancellation skips a term (AHL 1.11), the root count of
    $x^3 - 3x + k$ and the strict range $-2 < k < 2$ (AHL 2.12), a screening test read by Bayes where a
    99%-sensitive test on a 1-in-1000 disease gives only 1.94% confidence (AHL 4.13), and
    $\int_0^{\pi/2}(1+\tan^n x)^{-1}dx = \pi/4$ for every $n$ by the reflection substitution, set as a
    Paper 3 problem-solving item at difficulty 5 (AHL 5.16).
  - **CS ×2.** An aggregate that silently excludes a row — `COUNT(*)` against `COUNT(unit_price)`, and
    `SUM/COUNT(*)` reporting 18.00 where `AVG` reports 21.00 — with the `WHERE`-before-`GROUP BY` trap on
    top. And a priority queue where the heap loses: under a stated counting model the crossover is at
    $k = 18.36$ extractions, so the unsorted array wins for any workload that drains fewer than nineteen
    of 1 024 items.
  - **BM ×2.** A ratio extract where paying a supplier in cash *raises* both liquidity ratios, and buying
    inventory on credit lowers the current ratio by the equal-amounts rule while dropping the acid test
    through 1.00 because its numerator cancels exactly. And a break-even at 12 500 units against a
    capacity of 10 000 — unreachable, with a negative margin of safety and three single-lever thresholds
    at £44.00, £160 000 and £20.00.
  - **The originality gate passed and the batch was still changed.** `MATH-AHL1.11-201` scored 0.185
    internal against a 0.25 limit — under the gate, but it used the *same general term* as the existing
    `MATH-AHL1.11-001` ($1/(n(n+1)(n+2))$) with near-identical parts (a) and (c). The threshold is a proxy
    for a judgement, and the judgement was that the bank should not hold the same question twice, so the
    item was rewritten around $1/(n(n+2))$, whose pieces cancel across a gap and leave two survivors at
    each end rather than one. Internal overlap fell **0.185 → 0.019**.
  - Evidenced count **52 → 60**; assertions **2265 → 2373**. Difficulty split 132 at d4, 92 at d5; every
    subject inside the 50% cap.
- **Batch 19 — DONE (5 Maths, 4 Physics, 3 CS, 2 BM; 224 → 238).** The stretch tail: volume added on top
  of a bank whose priority-1 and priority-2 nodes were already complete, so this batch competes only
  against its own quality bar. Every item is designed at difficulty 4–5 with a `difficulty_evidence`
  block, all four subjects sit inside the 50% cap, all 13 levers remain in use, and the originality gate
  is clean.
  - **Maths ×5.** A Maclaurin series solution of $y' = y^{2} - x$ whose inhomogeneous term first bites at
    $n = 1$, so the recurrence has to be started by hand (AHL 5.19, Paper 3, difficulty 5); three planes
    whose determinant vanishes at $k = 4$ and which meet in a *prism* rather than a sheaf, where the
    exceptional parameter produces inconsistency and not infinite solutions (AHL 3.18, difficulty 5);
    $9^{x} - k\cdot 3^{x} + (k+1) = 0$ read as a hidden quadratic whose number of roots is governed by the
    *product* of the roots rather than by the discriminant (AHL 2.10); $\int dx/(x^{2}+x+1)$, where the
    obvious substitution $u = x^{2}+x+1$ fails and the working one has to be built by completing the
    square (AHL 5.16); and a two-prize raffle whose values are recovered from $E(X)$ and $\operatorname{Var}(X)$,
    where the tempting symmetry assumption $a = b = 5$ fits the mean and gives the wrong variance
    (AHL 4.14).
  - **Physics ×4, all difficulty 4 by design** — the standing Physics difficulty-5 rule, so the d5 share
    falls again rather than rising. Two seeded-anomaly data-based items: a speed-of-sound measurement
    where the end correction is systematic rather than random, and an impulse obtained by integrating an
    $F$–$t$ record whose sampling interval changes mid-trace, so the constant-interval assumption
    overstates the impulse by 29%. Then a fission fuel-cycle chain in which the enrichment step *is* the
    arithmetic (377 kg of uranium consumed through 9.4 t of 4%-enriched fuel loaded to a coal comparison
    of $3.4 \times 10^{6}$ t), and a cyclotron whose exit energy is fixed by the flux density and the dee
    radius rather than by the accelerating voltage, so doubling the voltage halves the number of
    revolutions and leaves the energy exactly where it was.
  - **CS ×3.** A compiler-against-interpreter cost model on a daily batch workflow, where the per-run
    comparison is six to one in favour of the compiled form and the 720 ms one-off translation cost still
    reverses the verdict for the first 47 executions — crossover at $n = 48$; a hospital insider breach
    with no attacker and no vulnerability, where least privilege and the written guarantee that no
    clinician is blocked from a record in an emergency cannot both be met by one role per person
    (90 strict roles, 30 once the site is treated as a record attribute, plus a time-limited break-glass
    grant); and an OOP design where the obvious two-axis hierarchy is merely multiplicative — 19 classes
    in use, 24 in full — which composition keeps at 9.
  - **BM ×2.** A price cut that is revenue-positive and profit-negative: the elasticity really is elastic
    ($-1.33$) and revenue really does rise, but the £6 comes off the contribution of all 300 existing
    members and the 60 new ones do not cover it, so profit falls £120 and the membership needed to hold
    it (365) is five above the forecast. And a retention pay rise where the wrong comparison — the
    £300 000 recruitment bill *already being spent* against the £352 000 salary increase — makes the
    proposal look nearly self-financing, when the saving it actually buys is £150 000 and no achievable
    fall in turnover can cover the cost.
  - **The originality gate passed and the batch was still changed.** `PHYS-D.3-202` came back with an
    *approach* score of 0.416 against `PHYS-D.2-102`. That is under the 0.50 limit and therefore a pass,
    but the two items used the same apparatus (a velocity selector feeding a magnetic spectrometer) and
    near-identical solution skeletons, step for step. The threshold is a proxy for a judgement, and the
    judgement was that the bank should not hold the same question twice, so the item was rewritten around
    a cyclotron, where the exit energy is derived from the geometry instead of from the voltage. Its
    approach score fell **0.416 → 0.200**, and the top of the approach table is once again the
    `MATH-AHL1.11` pair at 0.366.
  - Evidenced count **60 → 74**; assertions **2373 → 2585**. Difficulty split 144 at d4, 94 at d5; every
    subject inside the 50% cap.
- **Batch 20 — DONE (6 Maths, 4 Physics, 3 CS, 1 BM; 238 → 252).** The hard half of the stretch tail, and
  the first batch written to the instruction *harder than before, especially in Maths, with a real logical
  point inside rather than more arithmetic*. Every item names a lever and the lever carries the
  difficulty; nothing was made longer to make it harder. Maths contributes 3 × d5 and 3 × d4, Physics
  2 × d5 and 2 × d4, CS 2 × d5 and 1 × d4, BM 1 × d5. Physics rises to **47%**, CS to **30%**, BM to
  **10%** — all inside the 50% cap, and the gate confirms no subject has regressed against the
  2026-09-13 baseline. Six hand-authored inline SVGs were added (three Maths, two Physics, one CS).
  A second BM item was written, passed every gate, and was then withdrawn: see the last bullet below.
  - **Maths ×6.** $\sin 2x = k\cos x$ on $[0, 2\pi]$, where the number of solutions is **5 at $k = 0$**,
    4 for $0 < |k| < 2$ and 2 for $|k| \ge 2$ — the exceptional parameter is the one value that makes
    $\cos x$ a *common* factor, so it destroys one of the roots it would otherwise leave (AHL 3.8, d5,
    `exceptional_parameter`); $\int_{-a}^{a}(x^{3} - a^{2}x)\,dx$, where the signed integral is exactly
    **zero for every $a$** while the geometric area between the curve and the axis is $a^{4}/2$, so the two
    readings of "area" disagree by the whole of it (AHL 5.11, d4, `partial_cancellation`); $\sum_{k=1}^{n}
    1/(1 - \omega^{k}) = (n-1)/2$ for an $n$-th root of unity, where every term has real part exactly
    $\tfrac12$ and the whole sum is recovered by pairing each term with its conjugate — the tool is complex
    conjugation applied to a real sum, which no amount of real manipulation suggests (AHL 1.13, d5,
    `non_obvious_tool`); a capped St Petersburg game where the uncapped expectation diverges because every
    term contributes exactly 1, and the cap at $2^{20}$ makes the expectation **21**, so a quantity that
    was infinite becomes a small integer (AHL 4.11, d5, `quant_vs_judgement`); $\int_{0}^{1} x^{-p}\,dx$,
    where the partial integral $(1 - \epsilon^{1-p})/(1-p)$ has a limit only for $p < 1$ and the naive
    antiderivative is applied at $p = 2$ to return 9, 99, 999 as $\epsilon$ falls (AHL 5.12, d4,
    `decoy_technique`); and $n! > 3^{n}$, which first holds at $N = 7$ because $6! = 720$ falls short of
    $729$ by exactly 9, so the induction step needs $k + 1 > 3$ and the base case cannot be guessed
    (AHL 1.15, d4, `implicit_dependence`).
  - **Physics ×4.** A series circuit containing an inductor, where the initial rate of rise is
    $\varepsilon/L = 48\ \mathrm{A\,s^{-1}}$ and contains **neither** resistance although both are in the
    diagram, while the final current and the time constant depend on the total including the coil's own
    8 Ω — so a candidate who treats the coil as ideal gets 0.300 A and 6.25 ms against the correct
    0.250 A and 5.21 ms (D.4, d5, `non_governing_variable`); a diffraction-grating record in which the
    36.1° line is present *at the correct angle* but carries only 2 of 100, the missing order being
    explained by $d/a = 2$ putting the single-slit envelope zero exactly on order 2, so the anomaly is
    invisible to anyone who checks only the angles (C.3, d5, `seeded_anomaly`, data-based with a figure);
    a potential divider asked to deliver 4.00 V into a load, which delivers 2.40 V and cannot be made to
    deliver 4.00 V for **any** finite $R_{2}$ because that would require the parallel combination to equal
    its own upper bound (B.5, d4, `wrong_design_cost`); and a hot-air balloon whose required internal
    temperature is 367 K, whose payload bound is $\rho_{\text{out}}V$, and for which a 3000 kg payload
    demands a *negative* density (B.3, d4, `derived_limit`).
  - **CS ×3.** A RAID 5 stripe of four data blocks and one parity block, where the parity is the XOR
    ($0x5A \oplus 0x3C \oplus 0xF0 \oplus 0x27 = 0xB1$), any one lost block is recoverable, and the
    tolerance is **one failure per stripe regardless of the stripe's width** — so widening a stripe
    raises capacity but not redundancy, which is the belief the item exists to break (A1.1, d5,
    `aggregate_recovery`, with a two-stripe figure); an ISBN-10 catalogue record holding the publisher's
    digits **interchanged** and accepted by a routine that sums the digits, where the digit sum is 27 in
    both orders and is therefore blind to every transposition, while the weighted total moves
    132 → 136 and the prime modulus 11 detects every interchange because the change is a product of two
    factors each smaller than 11 (A1.2, d5, `seeded_anomaly`); and a timetabling relation with
    $\{S,\mathrm{Sub}\} \to T$ and $T \to \mathrm{Sub}$ that is in **3NF but not BCNF**, whose natural
    decomposition is lossless but loses the dependency that made the pair a key, so no decomposition can
    be lossless, in BCNF and dependency-preserving at once (A3.2, d4, `binding_constraint`).
  - **BM ×1.** A four-stage flow line whose bottleneck is welding at 480 units a week against a demand of
    600, where a second machine at the assembly stage raises assembly's capacity to 1 200 and the line's
    output by **exactly zero**, while the same machine at welding closes the shortfall — and the choice
    between the 85 000-dollar machine at 326.92 a week and overtime at 360.00 a week turns on which cost is
    fixed and which is variable (5.2, d5, `binding_constraint`).
  - **The originality gate passed and the batch was still changed.** The first BM item of this batch
    computed the payback period, the average rate of return and the net present value of two mutually
    exclusive projects and then asked which to choose. It came back at internal 0.020 against a 0.25
    limit, a comfortable pass, and it was withdrawn anyway, because reading the same-node neighbour is the
    check the gate is only a proxy for. The neighbour is `BM-3.8-001`: payback, average rate of return and
    net present value on two mutually exclusive projects with a 400 000 outlay, a four-year life, no
    residual value and a 10 per cent cost of capital, whose own `challenge_mechanism` states that "the
    three appraisal methods rank the two projects differently". Four of those five parameters matched, and
    so did the recommendation part, so the new item was a second copy of an existing question rather than a
    harder one. It was withdrawn and Batch 20 ships one BM item: BM 3.8 is saturated by 001 and 002, and a
    third item on the node would have been padding. The batch is smaller for it and not weaker.
  - Evidenced count **74 → 88**; assertions **2585 → 2788**. Difficulty split 150 at d4, 102 at d5;
    every subject inside the 50% cap.
- **Batch 21 — DONE (1 Maths, 1 CS, 1 BM; 252 → 255).** The calibration batch, and the only batch in the
  plan written to close a rule rather than to add coverage. `STANDARD.md` §2.5 requires the bank to use
  the whole 3–5 range — *"a bank with 0% at difficulty 3 is, in effect, a two-point scale wearing three
  labels"* — and the audit had been printing R2, *no item claims difficulty 3*, on every run since the
  standard took force on 2026-09-13. Every item in this batch therefore claims difficulty 3, and each one
  earns it the same way: **one clean lever, everything else routine.** §2.3 exempts a difficulty-3 label
  from the three-field completeness floor, so the bar is a rubric score of 4/9 — but all three items score
  **9/9** anyway, because the evidence is written to the same standard as a difficulty-5 item.
  - **Maths ×1.** $2^{x} \ge x^{2}$, whose natural window $0 \le x \le 5$ shows exactly two intersections,
    both exact, at $x = 2$ and $x = 4$ — and it is their exactness that makes the window look complete.
    The solution set is $[r_{1}, 2] \cup [4, \infty)$ with $r_{1} = -0.7666646960$, a third intersection on
    the far side of the $y$-axis, where the exponential has flattened towards zero and the parabola has
    not. The lever is a single one: the **domain the search is carried out on**, not the algebra of the
    inequality, decides the answer (AHL 2.15, d3, `decoy_technique`, figure `b21-exp-vs-quad`).
  - **CS ×1.** A routing matrix at two scales. A dense two-dimensional array stores $n^{2}$ cells while the
    non-zeros grow only linearly, so the two costs diverge by a factor of the order: at the unit-test scale
    of 1 000 the array is 8.00 MB and allocates without complaint, while at the production scale of
    200 000 it is **320 GB** against **6.4 MB** held sparsely — a ratio of 50 000 in memory and 100 000 in
    time for one matrix-vector multiply (40.0 s against 0.40 ms). The density is 0.001% at both scales, so
    the test suite is exercising the one property that does not change (Theme B, B2.2, d3,
    `wrong_design_cost`, figure `b21-dense-vs-sparse`, with a stimulus table of the two scales).
  - **BM ×1.** Market share rising from 18% to 21% while every quantity it is supposed to stand for falls.
    The market contracted 20.0% while sales fell 6.67%, so the share gains 3.0 percentage points on 12 000
    *fewer* pots; unit contribution is unchanged at 9.00, total contribution falls 1 620 000 → 1 512 000,
    and operating profit goes from +60 000 to −138 000 once a 21.43% rise in marketing spend is taken into
    account. The lever is a single one: the **denominator moved**, so a relative gain is not an absolute
    one (Unit 4.1, d3, `non_governing_variable`).
  - **R2 is paid, and it took reading the branch to see why it was so cheap.** The audit's R2 rule is
    `if allc[3] < BASELINE["d3_count"]` → regression, `elif allc[3] == 0` → debt, with `d3_count`
    recorded as **0**. The count cannot fall below zero, so R2 can only ever fire as a debt, and a single
    item silences it. It is **bank-wide, not per subject** — which is why three subjects are enough to
    clear it, and why Physics deliberately contributes none. Physics is the one subject this batch leaves
    alone: every open Physics node already carries a trap *plus* a second demand, so a difficulty-3 item
    there would have been a difficulty-4 item relabelled, which is the exact failure §2.3 exists to
    prevent. `--check --strict` now exits 0 for the first time, and the outstanding-debts section has
    disappeared from the audit output.
  - **The rubric score cannot produce a difficulty-3 item, and this batch is the proof.** Measured across
    all 90 evidenced items that existed before this batch, **every one scores 9/9**, so
    `max_label_for(9)` = 5 is an upper bound and nothing more: `--id` prints *"permits at most difficulty
    5"* for a difficulty-3 item exactly as it does for a difficulty-5 one. A difficulty-3 claim therefore
    rests on the **number of ideas** in the item — one lever, everything else routine — and not on the
    score. Hollowing out an evidence field to drag the score down to 4 would make the claim *less*
    falsifiable, not more, so all three items carry full evidence. Recorded in the skill.
  - Evidenced count **88 → 91**; assertions **2788 → 2840**. Difficulty split now **3 at d3, 150 at d4,
    102 at d5**; every subject still inside the 50% cap.
- **Batch 22 — DONE (2 Maths, 2 Physics, 1 BM).** The figure-coverage batch. Standing
  instruction: *a percentage of questions must carry a graph, written without other tools.* Before this
  batch the bank held **45 of 255 = 18%** figure-bearing items and the distribution was lopsided — Physics
  and CS sat at 32% each, Maths at 8%, and **BM at zero**: 30 items, not one graph. Batch 22 adds five
  items, all five figure-bearing. Together with the two Physics waves that landed alongside it (22b below)
  the bank reaches **52 of 267 = 19%** (Maths 11 = 10%, Physics 27 = 32%, CS 13 = 32%, BM 1 = 3%), and
  `FIGURE_COVERAGE_FLOOR` rises 0.17 → 0.19 in the same change. All five are difficulty 5 except the BM
  item, which is difficulty 4; all five score **9/9** on the rubric.
  - **The two Physics items of this batch are filed as `physics-hl/batch22c.json`, not `batch22.json`, and
    that is a scar rather than a plan.** Two Physics writers were in flight at once and both targeted
    `physics-hl/batch22.json`; the pair was overwritten twice before it stuck. See the incident note at the
    end of this entry. The `c` suffix exists so that no writer's filename can collide with another's again.
  - **Maths ×2.** Both are designed so the **figure is the load-bearing part**, not decoration — in each
    the graph is what makes the wrong answer attractive.
    - `MATH-AHL5.8-201` (AHL 5.8, d5, Paper 3, `problem_solving`, 18 marks, `decoy_technique`,
      `uk-alevel`). The stimulus is the **graph of $f'(x) = (x-2)^{2}(4-x)$** and nothing else; the
      candidate must read stationary behaviour off the derivative rather than off $f$. At $x = 2$ the
      graph is flat and *does not cross*: $f'(1.9) = 0.021$ and $f'(2.1) = 0.019$, same sign, so $x = 2$ is
      a **stationary point of inflection**, not an extremum — and a plot that is read carelessly shows a
      turning point. At $x = 4$ the sign does change ($f'(3.9) = 0.361 \to f'(4.1) = -0.441$), so that one
      **is** a local maximum. $f''(x) = (x-2)(10-3x)$ confirms both. The second half turns on the
      difference between a signed integral and a geometric area: $f(4) = 475/12 \approx 39.58$,
      $f(5) = 36$, the signed integral over $[0,5]$ is $36$, and the **enclosed area is $259/6 \approx
      43.17$** — larger, because a lobe below the axis adds rather than cancels. Figure
      `derivative_cubic_graph`, sampled from the same `fp(x)` the markscheme integrates.
    - `MATH-AHL4.4-201` (AHL 4.4, d5, Paper 2 section B, `extended_response`, 12 marks,
      `seeded_anomaly`, `us-ap`). A ten-point bivariate stimulus table with **one influential point**
      ($y = 30$ against a body that runs $2 \ldots 18$). Over all ten points $S_{xx} = 82.5$,
      $S_{xy} = 206.5$, $m = 2.503$, $c = -1.467$, $r = 0.942$; drop the last point and $S_{xx} = 60$,
      $S_{xy} = 118$, $m = 1.967$, $c = 0.500$, $r = 0.996$. Both lines look respectable and both $r$ look
      strong, which is the trap: the *prediction* is what moves — at $x = 12$ the estimate goes from
      **24.1 to 28.6, +18.5%**. Figure `scatter_influential`, drawn from the same sums the markscheme uses.
  - **Physics ×2.** Both are the "right formula, wrong model" shape, and both use a graph to make the
    wrong model look sanctioned.
    - `PHYS-B.5-201` (B.5, d5, Paper 1 section B, `data_based`, 12 marks, `non_obvious_tool`,
      `uk-alevel`). A **filament-lamp characteristic** $I = 0.1403\,V^{0.526}$ plotted against a 6.0 V
      supply and a 12 Ω series resistor, i.e. the load line $I = (6.0 - V)/12$. The operating point is the
      intersection: **3.0 V, 0.250 A** (exact root $V = 2.999622$). The non-obvious tool is that the lamp's
      resistance *is not constant*: $R = 12\ \Omega$ at 3.0 V but $17\ \Omega$ at 6.0 V, so the tempting
      one-shot $I = 6.0/24$ gives **0.2093 A — 16.3% low** — and is self-contradictory besides, since it
      implies 0.2707 A at 3.488 V. Figure `lamp_characteristic` (curve + load line + the crossing marked).
    - `PHYS-D.1-201` (D.1, d5, Paper 2 section B, `structured`, 12 marks, `non_governing_variable`,
      `us-ap`). A **$g$-against-$r$ graph for a uniform planet** ($R = 3.0 \times 10^{6}$ m, surface
      $g_{s} = 3.6$ m s⁻²) whose defining feature is a **kink at the surface**: linear inside, inverse
      square outside. From the surface value $M = 4.86 \times 10^{23}$ kg, $V = 1.13 \times 10^{20}$ m³ and
      $\rho = 4295$ kg m⁻³ (cross-checked by the independent route $3g_{s}/4\pi GR$). The lever is that
      $r$ is *not* the governing variable inside the body: at $r = 1.5 \times 10^{6}$ m the field is
      **1.8 m s⁻²**, while the plausible-looking $GM/r^{2}$ gives **14.4 m s⁻² — eight times too big**,
      because that formula only holds for $r \ge R$. Figure `g_against_r_planet` (two regimes, kink marked).
  - **BM ×1.** `BM-3.7-201` (Unit 3.7, d4, Paper 2 section B, `structured`, 12 marks, `wrong_design_cost`,
    `original`). A six-month cash-flow forecast; closing balances $[8, 3, -9, -6, 3, 14]$; the trough is
    **−9 in month 3** and the limit is breached **4** times. The lever is that the obvious repair — re-time
    an inflow from month 4 into month 3 — moves the trough to −6 and the breach count to **1**: it
    *fails*. The reason is that **the month-4 closing balance is pinned at −6 by $12 + 68 - 86$ for every
    re-timing**, so shuffling receipts inside the window cannot fix a structural deficit. A 4 000 loan
    gives $[12, 7, -5, -2, 7, 18]$ — trough −5, exactly on the limit. Figure `cashflow_closing_balance`,
    the first figure ever to appear in a BM item.
  - **Hand-authored figures, and the gate that enforces it.** All five are plain-Python string builders
    appended to `tools/make_figures.py` and registered in its `FIGURES` dict: `derivative_cubic_graph`,
    `scatter_influential`, `lamp_characteristic`, `g_against_r_planet`, `cashflow_closing_balance`. They
    emit SVG from the same house primitives as the existing figures (`_svg`, `_t`, `_tsup`, `_tr`, `_l`,
    `_c`, `_p`, `_r`, `_poly`, `_arrow_defs`) and the same palette, and are exported through
    `data/_figures.json` before being inlined into the item JSON. **Two of them sample their own curve** —
    the derivative graph from `fp(x)`, the scatter from the very sums the markscheme quotes — so the
    picture and the markscheme cannot drift apart. Layout was checked programmatically before shipping: a
    bounds test caught two labels overrunning the frame and a collision test caught two overlapping
    labels; both were fixed.
  - Evidenced count **91 → 96**; assertions **2840 → 2909**.
- **Batch 22b — DONE (6 Physics, filed as `physics-hl/batch22.json`).** A parallel Physics wave that landed
  in the same window as Batch 22 and shares its figure goal. Six **difficulty-4 `structured`** items, one
  per node, and the design is visibly a *spread* rather than a theme:

  | id | node | lever | source family | marks | figure |
  |---|---|---|---|---|---|
  | `PHYS-A.2-301` | A.2 Space, time and motion | `non_obvious_tool` | `china-competition` | 14 | — |
  | `PHYS-B.3-301` | B.3 Particulate nature of matter | `aggregate_recovery` | `china-gaokao` | 14 | ✓ |
  | `PHYS-D.2-301` | D.2 Fields | `implicit_dependence` | `ib` | 15 | — |
  | `PHYS-D.4-301` | D.4 Fields | `wrong_design_cost` | `us-ap` | 15 | ✓ |
  | `PHYS-E.1-301` | E.1 Nuclear and quantum physics | `derived_limit` | `singapore-alevel` | 15 | — |
  | `PHYS-E.5-301` | E.5 Nuclear and quantum physics | `partial_cancellation` | `uk-alevel` | 15 | — |

  Six distinct **levers** from the 13-type taxonomy, six distinct **source families**, and four of the four
  examinable Themes — the wave is built to diversify rather than to drill one idea. All six carry full
  `difficulty_evidence` and score **9/9**. Two are figure-bearing, so the wave takes the figure count
  45 → 47. `PHYS-D.2-301` is the bank's first item sourced from `ib` itself.
- **Physics's first difficulty-3 item — DONE (1 Physics, `physics-hl/batch21.json`).** `PHYS-A.3-201`
  (Theme A, 13 marks, 5 parts, `decoy_technique`, `original`) closes the gap that the Batch 21 entry
  recorded in as many words: *"Physics still claims no difficulty-3 item; that is a design gap rather than
  a slot to fill."* It is the single-lever shape §2.3 asks for — one clean trap, everything else routine —
  and it still scores **9/9**.
  - **It shipped with a paper-type bug, and the gate caught it.** The item declared `paper: "P1"` with
    `question_type: "structured"`. Physics **P1 contains only `mcq` and `data_based`**; `structured` lives
    on P2. This is exactly what `PAPER_TYPES` in `validate.py` exists to reject, and it rejected it —
    `structured on Physics HL P1: that paper contains data_based/mcq`. Corrected to `paper: "P2"`, where
    `structured` is legal. The lesson is not "check the field" but "the paper a question *looks* like it
    belongs to is not the paper it is allowed on".
- **The clobber incident, recorded because it cost real work twice.** Two Physics writers were in flight at
  once and both wrote `data/physics-hl/batch22.json`. Batch 22's Physics pair was destroyed by the first
  writer; it was recovered from its generator, reinstated, and then destroyed **again** by the second
  writer before it finally settled. Nothing was lost in the end, but only because the generator survived
  and because the loss showed up as an arithmetic anomaly — the bank's item count moved by an amount that
  no single batch could explain, and the audit's per-subject Physics total did not match the sum of the
  files. Two rules came out of it, both now in the skill: **one wave, one filename** (a second pass gets
  `batchNb.json`, never a re-run over a filename another writer owns), and **check the count per subject
  after every write**, because a wrong total is the cheapest detector there is.
- **Batches 21–22 together — 255 → 277.** The figure ratchet was set in the same change:
  `FIGURE_COVERAGE_FLOOR` 0.17 → **0.19**, against a measured **52 / 277 = 19%**. Evidenced count
  **91 → 113**; assertions **2840 → 3144**. Difficulty split now **4 at d3, 163 at d4, 110 at d5**;
  every subject still inside the 50% cap (Maths 48%, Physics 44%, CS 31%, BM 10%). Bank totals:
  Maths 117 / 1773 marks, Physics 84 / 1060, CS 45 / 701, BM 31 / 462.
  - **A parallel session landed a CS and Maths wave in the same window.** Four CS items
    (`CS-A1.3-301`, `CS-A2.3-301`, `CS-A4.3-301`, `CS-B2.4-301`) and a further Maths wave arrived while
    these docs were being written, taking the bank 267 → 277. They are counted in every figure above. One
    of them (`MATH-AHL1.13-301`) briefly failed the gate — *difficulty 5 is not earned: the evidence
    scores 7/9, which permits at most 4* — and was corrected by its own author within minutes. Recorded
    here because the numbers in this document were re-derived three times in twenty minutes for the same
    release, and anyone comparing a count against an earlier revision should assume a second writer rather
    than a mistake.
  - **The ratchet, and why it is a gate and not a number.** `FIGURE_COVERAGE_FLOOR` was 0.17, set when the
    bank stood at 18%. The figure-bearing items added across these waves took the share to **19%**, so the
    floor moves to **0.19** in the same commit — a deliberately tight fit (52/267 = 19.5%), which is the
    point: the next batch has to carry its own weight. The rule is one-directional on purpose: coverage may
    rise and the floor follows it up, but a future batch cannot add non-figure items and let the percentage
    sag back — the audit fails instead. `FIGURE_SUBJECT_TARGET = 0.15` is the per-subject companion, and it
    is *reported* rather than enforced, which is the honest choice: Maths at 10% and BM at 3% are both
    still under it, and forcing them up would mean bolting graphs onto items that do not need one.
  - **Verification first, prose second.** Every number above was recomputed in Python *before* the prose
    was written: exact fractions plus 200 000-interval quadrature for the Maths area, bisection to 200
    iterations for the lamp operating point, two independent routes to the planet's density, and a
    re-chained cash-flow column for the BM repair. The BM verifier found a real bug on its first run — the
    "shifted" branch was reusing the original opening balances instead of re-chaining — and fixing it is
    what surfaced the stronger, correct result that month 4 is pinned.
- **Batch 22, second wave — 267 → 285.** Eighteen items landed in one sitting: eight Maths
  (`MATH-AHL2.13-301` oblique asymptote that the curve actually crosses, `MATH-4.10-301` the two
  regression lines of the same scatter, `MATH-AHL3.15-301` two flight paths that intersect without the
  aircraft colliding, `MATH-AHL3.10-301` the root a squared trig equation adds, `MATH-1.3-301` two
  sequences with the same first three terms, `MATH-AHL1.13-301` a sum of sines summed as a complex
  geometric series, `MATH-3.18-301` three planes that form a triangular prism, `MATH-5.9-301` two moving
  objects level at a repeated root), five Business Management (`BM-5.5-301` a contract that crosses the
  relevant range and destroys profit with positive contribution, `BM-4.4-301` a survey whose non-response
  flips the majority, `BM-6.7-301` a grouped table whose open-ended class makes the mean underivable,
  `BM-3.8-301` capital rationing in which the highest-NPV project is the wrong pick, `BM-5.2-301` the
  stage with the lowest stated capacity that is not the bottleneck) and five Computer Science
  (`CS-B2.4-301` recursion whose call count is 2F(n) − 1 while memoisation changes a different limit,
  `CS-A2.3-301` a DNS TTL judged against an arrival rate, `CS-A4.3-301` two confusion matrices that
  expose data leakage, `CS-A1.3-301` row-major against column-major traversal under thrashing,
  `CS-A3.2-301` an index that makes the slow operation a hundred times faster and the system 54% slower).
  - **Two gates bit, both on items in this wave.** `MATH-AHL1.13-301` failed *difficulty 5 is not
    earned: the evidence scores 7/9* because its heaviest part was part (a); the fix was to re-cut the
    marks (a: 4 → 3, d: 3 → 4) and expand the corresponding markscheme, not to weaken the evidence.
    `CS-A3.2-301` failed twice on vocabulary — a topic outside the CS closed list, and `structured` on
    Paper 2, which is a case-study paper — and both are the kind of error the validator exists to catch.
  - **The figure gap narrowed deliberately.** BM went from 1 to 5 figure-bearing items (3% → 14%)
    because four of the five new BM items carry an SVG built by the same plain-Python string builders,
    and both new Maths items carry one; bank-wide coverage rose 52 → 59 = **21%**, so
    `FIGURE_COVERAGE_FLOOR` moves to **0.20** in this commit. The per-subject companion stays *reported*,
    not enforced: Maths is still at 11% and forcing it to 15% would mean bolting graphs onto items that
    do not need one.
  - **One wave, one filename, kept.** The last CS item went to `batch23.json` rather than a re-run over
    `batch22.json`, which another writer owns in this window. The rule from the earlier incident holds:
    a second pass gets a new filename, and the per-subject total is checked after every write.
  - **Numbers after the wave.** 285 items — Maths 119 / 1803 marks, Physics 84 / 1060, CS 46 / 715,
    BM 36 / 532. Difficulty split **4 at d3, 164 at d4, 117 at d5**; every subject inside the 50% cap
    (Maths 49%, Physics 44%, CS 33%, BM 19%). Evidence present **121 / 285**; assertions **3271**.
- **Batch 23, the lean-devious wave — 285 → 301.** Sixteen items, and the point of the batch is the
  opposite of the batch before it: the median item in this bank is about fifteen marks and these are six
  marks in the sciences, ten or eleven in Business Management, with **every single one carrying an inline
  SVG figure**. Difficulty is compacted rather than spread — each item takes one turn in the reasoning
  and almost no arithmetic — and each of the sixteen was designed from a different lever, with the two
  thinnest levers in the bank (`variable_swap` at 3%, `quant_vs_judgement` at 4%) each given an item.
  - **Mathematics (6).** A decreasing bijection of $[0,\,6]$ onto itself whose graph therefore meets its
    own inverse at two points that are *not* on $y = x$ (`MATH-2.2-401`); a derivative graph whose area
    makes $f(7.5)$ exactly zero, so a crossing becomes a touching point and the root count drops by one
    (`MATH-5.8-401`); the closest point of a segment that is an *endpoint*, because the foot of the
    perpendicular falls outside it (`MATH-3.13-401`); the moment of a region recovered from its symmetry
    without ever knowing the function (`MATH-5.11-401`); a sideways parabola whose chord bounds a region
    needing one integral in $y$ and two in $x$, split at $x = 1$ (`MATH-AHL5.17-401`); and two unbounded
    tails drawn at the same scale, one enclosing exactly one unit of area and one enclosing none, decided
    entirely by whether the exponent exceeds $1$ (`MATH-5.11-402`).
  - **Physics (4).** A $p$–$V$ cycle whose path crosses itself, so the net work is the *difference* of
    the two lobe areas, $200 - 50 = 150\ \mathrm{J}$, and not their sum (`PHYS-B.4-401`); a ball that
    comes to rest in finite time after infinitely many bounces, the intervals forming a geometric series
    with ratio $0.8$ (`PHYS-A.1-401`); a string plucked at $\tfrac{L}{3}$ where every harmonic with a node
    at the plucking point cannot be excited at all (`PHYS-C.4-401`); and a ramp on which the required
    force peaks at an intermediate angle while the work needed falls steadily as the ramp steepens
    (`PHYS-A.3-401`).
  - **Computer Science (3).** A binary search defeated by one adjacent transposition: eleven of the twelve
    stored values are still found and only $13$ is lost, because the comparison that discards the half
    holding it reports a true value (`CS-B2.4-401`); six byte offsets with a stride of $16$ that all land
    in slot $0$ of a table of size $16$ at a load factor of $0.375$, while a table of size $17$ separates
    them perfectly at almost the same load factor (`CS-B2.2-401`); and a Euclidean loop needing twelve
    iterations on one three-digit pair and two on another, with the worst case below $1000$ derived from
    the Fibonacci recurrence as $14$, at $(987,\,610)$ (`CS-B2.4-402`).
  - **Business Management (3).** A six-month cash-flow forecast in which one $-8000$ outflow leaves five
    of six closing balances negative, the opening balance is not printed and has to be recovered from
    January, and the $15\,000$ peak breaches a $10\,000$ facility (`BM-3.7-401`); a firm whose market
    share rises in both regions and falls overall because the region where it is weak grew by 75% while
    the one where it is strong halved, and whose own volume fell from 290 to 258 units in a market of
    constant size (`BM-4.1-401`); and two liquidity ratios that both rise while the firm gives away two
    thirds of its cash and its working capital stays unchanged at £160\,000 (`BM-3.5-401`).
  - **The lever spread was chosen deliberately.** `variable_swap` and `quant_vs_judgement` were the two
    thinnest levers in the bank at the start of the wave; both gained an item, as did
    `partial_cancellation`, `aggregate_recovery`, `derived_limit` and `seeded_anomaly`. All thirteen
    levers remain in use and the largest share falls to 13%.
  - **The figure gap closed on its own.** Maths had been stuck at 11% against a 15% per-subject target
    since the standard took force; it stands at **15%** now, so the audit no longer prints a gap for any
    subject. Bank-wide coverage went **59 → 75 (21% → 25%)** and the ratchet moves
    `FIGURE_COVERAGE_FLOOR` **0.20 → 0.24**. All 16 new figures are built by plain Python string
    builders, so the validator's fingerprint check (`<canvas`, `plotly`, `matplotlib`, `chart.js`,
    `highcharts`, `echarts`, `vega`, `bokeh`, `data:image/`) stays satisfied by construction.
  - **Three gates bit, all fixed at the item.** `MATH-5.11-401` shipped a part whose command term was
    `Hence find`, which is not in the closed list — the text keeps the phrase, the term becomes `Hence`.
    `BM-3.7-401` and `BM-3.5-401` each carried a seven-step `solution_skeleton` against a three-to-six
    rule, and the fix merged steps rather than dropping them, so no reasoning left the markscheme.
  - **Numbers after the wave.** 301 items — Maths 125 / 1839 marks, Physics 88 / 1085, CS 49 / 734,
    BM 39 / 563; 4221 marks in all. Difficulty split **4 at d3, 171 at d4, 126 at d5**; every subject
    inside the 50% cap (Maths 48%, Physics 45%, CS 35%, BM 23%). Evidence present **137 / 301**, and
    `labels the evidence does not permit: 0`. Assertions **3447**.
- **Backlog pass — the difficulty-5 evidence debt is cleared (no change to the item count).** The 79 items
  that claimed difficulty 5 with no evidence were read one at a time and given a `difficulty_evidence`
  block: 36 Maths, 31 Physics, 10 CS, 2 BM. The headline number the audit publishes —
  `difficulty 5 with no evidence` — went **79 → 0**, and `labels the evidence does not permit` stayed at
  **0** throughout, which is the check that would have caught a correction that went the wrong way.
  Evidence coverage rose **137 → 216 of 301 (46% → 72%)** and the grandfathered backlog fell
  **164 → 85**; all 85 outstanding items are difficulty-3 or difficulty-4 claims.
  - **Five labels came down and none went up**, which is the outcome §4.7 asks for rather than a
    transcription. `MATH-P3-010` 5→4 — its heaviest part is the first (`5, 4, 4, 3`), so the arc test
    scores 0 and the item tops out at 7 of 9; `MATH-AHL5.9-001` 5→4; `MATH-AHL5.10-001` 5→3 — its own
    author note gives the trap as a sign slip on the cosine term, and a slip is not a lever;
    `MATH-AHL5.11-001` 5→4; `PHYS-E.2-101` 5→4 — the mechanism names units rather than an idea. The pass
    therefore widened the 3–5 range as well as shortening the top of it: difficulty-3 items went
    **4 → 5**, bank-wide d5 **42% → 40%**, Maths **48% → 45%**, Physics **45% → 44%**.
  - **The levers were spread, not piled up.** The largest single share stayed at **15%**
    (`non_governing_variable`, 33 of 216) while the evidenced set grew by 58%, so the backlog was not
    concentrated in the levers that were already busy. All 13 lever types remain in use.
  - **Two items are flagged rather than relabelled.** `MATH-AHL5.13-001` (repeated application of
    l'Hôpital) and `MATH-AHL4.11-001` (independence tested against the definition rather than by
    comparing the two conditional rates) keep difficulty 5 because the rubric permits it and their
    mechanisms name something to notice, but both sit near the bottom of the tier and are worth a second
    read before a later batch leans on them.
  - **This is not evidence that the bank got harder.** No question text, answer or mark allocation
    changed; the only edits are the 79 `difficulty_evidence` blocks and the five labels above.
- **Batch 25 — DONE (4 CS HL Paper 2 items, 301 → 305; and a structural error in the CS papers fixed).**
  The batch exists because of a defect found while answering a question about why Physics and CS have
  fewer items than Maths. The answer is that they do not, per syllabus node — Maths carries 125 items
  over **83** nodes while Physics carries 88 over **24** and CS 49 over **25**, so Physics is in fact the
  densest subject in the bank at 3.7 items per node against Maths's 1.5. What the question did expose was
  a paper-level hole that node coverage could not see.
  - **The CS Paper 2 table was wrong and the gate was blind to it.** `PAPER_TYPES` read
    `("Computer Science HL", "P2"): {"case_study"}`, contradicting both the guide and `STANDARD.md`
    §2.4, which states plainly that the case study lives on **P1 Section B** and that P2 is
    *entirely* extended-response. Seventeen CS items were declared `case_study` on P2 and the validator
    checked them against a table expecting exactly that, so the bank reported **0 failures** throughout.
    Correcting the table to P1 → `{structured, extended_response, case_study}` and P2 →
    `{extended_response}` turned `0 failures` into **17 failures with no data change at all** — the
    clearest possible demonstration that a gate encoding the same mistake as the data cannot detect it.
  - **The 17 items were re-filed by their own `topic` field.** Nine were Theme A, which the guide places
    on P1, and moved there (seven as Section B case studies, two as Section A extended response); eight
    were Theme B, which is P2's subject, and stayed on P2 with the type corrected to `extended_response`
    and the meaningless section label cleared. `paper` and `question_type` are the only fields changed.
  - **The consequence was that P2 had no items of its own type.** Before the fix, CS P2 held 17 items and
    **zero** extended-response — the 80-mark, 40%-of-grade component was effectively unmodelled while the
    audit reported 100% node coverage. Four new Theme B extended-response items fill it, on the three
    Theme B nodes that had no Paper 2 item at all (**B1.1**, **B2.2**, **B2.4**) plus B4.1. CS P2 now
    holds **12** items, CS stands at 53, and its figure share rises to **40% (21/53)**.
  - **The four items, all with a hand-authored SVG figure and all scoring 9/9 on the rubric.**
    `CS-P2B-001` (B1.1, d4, 16) single-machine scheduling where shortest-job-first — the rule the course
    teaches, and the right answer to a *different* objective — is the decoy: the booking order scores
    +2, shortest-job-first +3, and earliest-deadline-first **−1**, verified by enumerating all 24 orders
    and, after a fifth job is added, all 120. `CS-P2B-002` (B2.2, d4, 16) a triage queue where a binary
    heap and a sorted array **swap places** depending on the workload: the array wins a lookup-heavy
    workload by 9.3× and the heap wins an insertion-heavy one by 15.5×. `CS-P2B-003` (B2.4, d5, 15) a
    doubling array where the average of 0.999 copies per append is *correct* and still cannot answer the
    deadline question, because append 513 alone copies 512 elements. `CS-P2B-004` (B4.1, d4, 16) a cache
    that faults **more** when given more room — 9 misses at three pages rising to 10 at four, against
    10 falling to 8 for least-recently-used — which is why the eviction rule must be a function of the
    order the structure already maintains.
  - **Two of the four designs were wrong before they were written.** The verifier caught that the
    doubling item's prose would have claimed 2046 total copies and a worst append of 1024 (the truth is
    **1023** and **512**), and that the first greedy counterexample had **no counterexample in it** —
    earliest-finish and shortest-first both returned the same three intervals. Both were redesigned before
    a word of prose was written, which is the entire argument for verifying first.
  - **The figure ratchet moved with the coverage.** All four items carry a figure, so coverage rose
    75/301 = 25% → **79/305 = 26%** and `FIGURE_COVERAGE_FLOOR` was raised 0.24 → **0.25**. The headroom
    is unchanged at **11 non-figure items** (n = 316 passes, n = 317 fails), so the constraint on the next
    batch is as tight as it was.
  - **Numbers after the wave.** 305 items — Maths 125, Physics 88, CS 53, BM 39. Difficulty split
    **5 / 178 / 122**. Evidence present **220 / 305**, assertions **3491**, `difficulty 5 with no
    evidence` **0**, `labels the evidence does not permit` **0**. All 13 levers in use; largest share
    still 15%. `calibration OK`.
- **Housekeeping — the `section` field was never validated (2026-09-16).** The follow-up flagged when the
  CS Paper 2 table was fixed: three theme-B items were sitting in CS P1 Section A, which the guide
  reserves for theme A. Auditing the field properly found the same defect class at four times the size,
  because `section` is rendered to the student as a chip (`P1 · Section A`) and fed to the paper builder,
  and nothing checked it.
  - **60 of 305 items carried a label their paper does not have.** **47 Physics P2** and **10 Maths P3**
    items were split into sections those papers do not contain — the Physics 2025 guide says Paper 2 is
    "short-answer and extended-response questions" with no split named anywhere, and the Maths 2021 guide
    says Paper 3 is "two compulsory extended response problem-solving questions". **3 CS P1** items were
    theme B in Section A.
  - **Three things kept it invisible.** The label was plausible — "Physics P2 · Section B" reads like
    structure, and the pre-2025 syllabus *did* split P2 into sections, so it looked like history. It is
    not history: on Physics P2 the label separates nothing (A holds 4 structured + 2 extended-response,
    B holds 20 + 21) and all 57 items are `level: HL`, so it does not encode SL/AHL either. Half the
    field *was* right — Physics P1's A/B is the real 1A/1B booklet split and separates perfectly, 14 `mcq`
    on A against 17 `data_based` on B — which is worse than none of it, because a field correct in one
    subject invites the assumption it is correct everywhere. And the check has to be per-paper: "section
    must be A or B" passes all 60.
  - **`SECTION_RULES` now stores the legal set per `(subject, paper)`, empty set included** — the empty
    set is the whole point, since it is what makes "this paper has no sections" checkable. The legal sets
    were read off the guide PDFs, not inferred from the prose table in `STANDARD.md` §4.3, because prose
    and code drifting apart is exactly what the CS P2 bug was. `SECTION_THEME_RULES` holds the one
    content rule, CS P1 Section A ⇒ theme A.
  - **The 60 labels were cleared, not reassigned.** `tools/validate.py` went from `0 failures` to **60**
    with the gate added and back to **0** after the migration, which is a single-line deletion in each of
    23 files — **60 deletions, 0 insertions**, verified by `git diff --stat`, so there was no collateral
    reformatting. A byte-identity round-trip self-check runs before anything is written.
  - **What it leaves.** 6 CS P1 items are theme B with no case-study anchor and so fit neither section;
    the fix is a case-study anchor, which is content work and now the top of the next CS batch. 4 CS P1
    theme-A items sit in Section B with no stimulus. CS P1 Section B holds 25 of 41 items while the guide
    gives it 24 of 80 marks, so new CS P1 material should target Section A. Recorded in `STANDARD.md` §7.
- **Housekeeping — the same sweep applied to the other rendered fields (2026-09-16).** The `section` fix
  prompted a systematic audit of **every field `build.py` actually reads**, since the defect class is "a
  field the renderer prints and nothing validates". Four fields were rendered and unchecked:
  `technology`, `level`, `language`, `subtopic`.
  - **`technology` was wrong in 11 places and unnormalised everywhere.** It renders as a chip and had
    drifted into **six strings for three ideas** (`allowed` vs `permitted`; `not_allowed` vs
    `not allowed`, the first rendering with the underscore visible). Worse, the Maths 2021 guide says
    Paper 1 is "No technology allowed" while **Paper 2 and Paper 3 are "Technology required"**, and on
    Paper 2 students "must have access to a GDC at all times" — yet **3 P2 items and 8 P3 items said
    `not allowed`**, telling the student no calculator is permitted on the papers that mandate one. All
    eleven are "Show that"/"Prove" items, so the author meant "this question does not need the GDC"; the
    chip just carries no item-versus-paper qualifier. Fixed to `permitted` rather than `required`, because
    the paper permits the GDC and the question does not demand it.
  - **128 items touched, in one line each.** 108 `allowed` → `permitted`, 9 `not_allowed` →
    `not allowed`, 11 Maths P2/P3 `not allowed` → `permitted` — **128 insertions / 128 deletions across 46
    files**, verified with `git diff --stat`, so there was no collateral reformatting. `validate.py` went
    to **128 failures** with the gate added and back to **0** after the migration.
  - **`TECHNOLOGY_VALUES` closes the vocabulary; `TECHNOLOGY_RULES` encodes the per-paper policy.** The
    Physics guide's "The use of calculators is permitted" makes `not allowed` false on Physics P1/P2 too,
    so the rule is stated per paper rather than inferred from the majority value.
  - **CS and BM have no policy to enforce** — their guides say nothing about calculators — so those
    values stay author judgement. One open question is recorded rather than invented: **CS P1 is split 17
    `not allowed` against 15 `permitted` within one paper**, correlating with nothing (not question type,
    not `language`). Resolving it needs the CS specimen papers.
  - **`level` and `language` are closed while they are still free.** `level` is stated twice — derived
    from the subject slug and carried per item, with both printed — so `SUBJECT_LEVEL` requires them to
    agree; `language` is closed to `python / java / pseudocode / sql`. Both were already correct across
    all 305 items, which is the point: a rule added while it costs nothing is a rule a later batch cannot
    drift.
  - **`subtopic` was checked and deliberately left open.** All 305 items carry one and it is free text by
    design — it is the author's one-line summary of the item's idea, not a vocabulary — so gating it
    would be inventing a constraint the material does not have.
- **Batch 26 — DONE (5 items, 305 → 310; the CS P1 Section A gap closed and Physics E.2 deepened).**
  Two waves, two filenames, written to paths no earlier batch owned. The brief came from measuring the
  per-*paper* distribution rather than the node list, which is where the thinness actually was.
  - **CS HL Paper 1 Section A — 9 items → 12.** Three theme-A strands (**A1.1.6** cache hierarchy,
    **A1.2** number representation, **A1.3** scheduling) had **no Section A item at all**, and Section A
    holds 56 of the paper's 80 marks — so the component that carries the marks was the empty one.
    `CS-P1A-401` cache hierarchy and AMAT (d5, 14 marks, `non_governing_variable`), `CS-P1A-402` 8-bit
    two's-complement overflow (d5, 13 marks, `decoy_technique`), `CS-P1A-403` round-robin against FCFS
    (d4, 14 marks, `quant_vs_judgement`).
  - **Physics HL Paper 2 on E.2 — 1 item → 3.** E.2 was the bank's thinnest strand with a single item, so
    the gap was depth, not breadth (all 24 strands were already covered). `PHYS-E.2-401` de Broglie
    wavelength and electron diffraction (d5, 11 marks, `implicit_dependence`), `PHYS-E.2-402` photoelectric
    stopping potential for two metals (d4, 10 marks, `decoy_technique`). Both **omit `section` entirely**,
    because Physics P2 is one of the three papers with no sections — the shape `batch23.json` already had.
  - **Both waves carry hand-authored figures, and the ratchet was raised to follow them.** Five new SVGs,
    each generated from the same expression the markscheme uses: the cache pyramid with its hit rates and
    miss hand-off arrows, the two 8-bit frames with their sums and carry-outs, the process table plus
    round-robin Gantt chart, the diffraction tube with the ring drawn at $r = 2.95$ cm, and the two
    parallel $V_s$–$f$ lines. Coverage moved **79/305 = 26% → 84/310 = 27.1%** and
    `FIGURE_COVERAGE_FLOOR` went 0.25 → **0.27**. That leaves **1 non-figure item of headroom**
    (n = 311 passes, n = 312 fails), so the next batch cannot be plain text at all.
  - **A physics defect the gates could not have caught.** The first `PHYS-E.2-401` design used 150 V, which
    puts the first diffraction ring at $\theta \approx 28^\circ$ — far outside the small-angle regime the
    relation $r = 2L\lambda/d$ assumes, and far below any real electron-diffraction tube. Rebuilt at
    **3.00 kV**: $\lambda = 22.4$ pm, $\theta = 6.04^\circ$, $r = 2.95$ cm, with the inverse task (a
    2.50 cm ring) giving **4.17 kV**. Found by re-deriving the geometry before writing prose, not by a gate.
  - **The two traps were engineered to fail in both directions.** `CS-P1A-402`'s frames prove carry-out is
    *not* the overflow test: frame A has carry-out 1 with no overflow, frame B has carry-out 0 *with*
    overflow. `CS-P1A-401`'s naive path ($0.94 \times 3 + 0.06 \times 14 = 3.66$ ns) ignores RAM entirely
    and would turn the true 2.13× speed-up into a 3.28× one.
  - **All 49 planned assertions were run through `validate.py`'s own `evaluate()` before any prose was
    written** — 10/10, 12/12, 11/11, 8/8, 8/8, zero failures. `evaluate()` returns a `(bool, err)` tuple,
    so `if evaluate(a):` is always truthy; every result had to be unpacked.
  - **Numbers after the wave.** 310 items — Maths 125 / 1839 marks, Physics 90 / 1106, CS 56 / 838,
    BM 39 / 563. Difficulty split **5 / 180 / 125**, evidence **225 / 310**, assertions **3540**,
    figures **84 (78 svg / 4 code / 2 table)**. CS P1 now reads **Section A 12 / Section B 25 / 7
    unlabelled**. All five new items carry exactly one warning each — "originality not yet scanned" — and
    nothing else, so bank warnings moved 171 → 176 with no collateral. Similarity on the new items:
    external ≤ 0.054, internal ≤ 0.010, approach ≤ 0.220.
  - **A passing similarity gate is not a judgement.** The nearest approach neighbour (`PHYS-E.2-201`,
    0.220) was read rather than trusted: it is a `data_based` anomaly hunt using `seeded_anomaly`, against
    this batch's `structured` two-metal graph using `decoy_technique`. `CS-A1.3-001` (0.067 against
    `CS-P1A-403`) computes FCFS only and draws no chart. Both overlaps are the unavoidable
    "gradient + threshold" and "compare two schedulers" themes, not duplication.
- **Batch 27 — DONE (5 items, 310 → 315; the Maths figure share attacked where it was thinnest).**
  One wave, one filename (`data/math-aa-hl/figures-batch27.json`), written to an id space no batch had
  used (`-5xx`). The brief came from the **figure table** rather than the node list: node coverage has
  been 100% since 2026-09-11, so "which node is thin" was a dead end — the 125 Maths items already sat on
  **124 distinct `syllabus_ref` values**, so every node has its item and thinness was never a node
  problem. The real gap was **topics that have items but no figure at all**: tangents and normals
  (5 items, 0 figures), discrete random variables (8, 0), the binomial (5, 0), skew lines (2, 0), the
  unit circle (3, 1). Batch 27 takes the top of that list.
  - **The five items.** `MATH-AHL5.6-501` tangent and normal at a stationary point (P1 §B, d5, 13 marks,
    `exceptional_parameter`); `MATH-AHL4.7-501` expected value and variance read off a bar chart of
    counts (P2 §B, d4, 13 marks, `decoy_technique`); `MATH-AHL2.16-501` the graphs of $|f(x)|$,
    $f(|x|)$ and $1/f(x)$ (P1 §B, d5, 13 marks, `decoy_technique`); `MATH-AHL3.6-501` exact values from
    the unit circle (P1 §A, d4, 11 marks, `non_obvious_tool`); `MATH-AHL5.9-501` the open box whose
    optimum sits on the boundary (P2 §B, d5, 14 marks, `binding_constraint`). Three of the five are
    difficulty 5, which is what the standing rule asks of new Maths items; all three earn it with a lever
    rather than with length.
  - **Every item carries a hand-authored figure, and the ratchet was raised to follow them.** Five new
    SVGs, each built from the same expression the markscheme uses — the tangent line and its normal at
    the stationary point, the five-bar count chart, the three-panel $|f(x)|$ / $f(|x|)$ / $1/f(x)$
    sketch, the unit circle with both angles marked, and the net of the folded box. Coverage moved
    **84/310 = 27.1% → 89/315 = 28.3%** and `FIGURE_COVERAGE_FLOOR` went 0.27 → **0.28**. Maths — the
    thinnest subject in the bank — moved **15% → 18%** (19/125 → 24/130). **2 non-figure items of
    headroom** remain (n = 317 passes at 0.28, n = 318 fails), so a plain-text batch is still ruled out.
  - **Two of the five traps are built to fire from both sides.** `MATH-AHL4.7-501` draws the distribution
    as **counts from a sample of 14 trials** rather than as probabilities: reading the heights directly
    gives $E(X) = 28$ and a variance inflated by $14^2$, and both are self-consistent with the wrong
    normalisation, so nothing in the arithmetic flags the error — the only warning is that the heights
    sum to 14. `MATH-AHL5.9-501` is the mirror image: the differentiation is routine and the stationary
    point is found correctly, but the feasible interval closes before it, so the answer is the endpoint.
  - **All 60 assertions were checked numerically before any prose was written.** A standalone script
    verified $f(2) = -4$, $f'(2) = 0$ and $(x-2)^2(x+1) \equiv x^3 - 3x^2 + 4$; the heights 2, 3, 4, 3, 2
    with $E(X) = 2$, $E(X^2) = 39/7$ and $Var = 11/7$; $\cos(5\pi/6) = -\sqrt3/2$ with $PQ = \sqrt3$ by
    two routes and sector area $\pi/3$; and $V(2) = 128$, $dV/dx = 12(x-2)(x-6)$, $V''(2) = -48$ with
    $S = 144 - 4x^2$ strictly decreasing on the feasible interval.
  - **Two near-misses worth recording, because neither was a data defect.** `MATH-AHL4.7-501` first
    shipped an unpaired `$` from a literal `\\$` currency escape; the generator's own self-check caught
    it, which is the whole reason that script refuses to write on any mismatch. Separately, a coverage
    probe looked for `solution_skeleton` at the top level and reported 0 steps for the new items — the
    field is `verification.solution_skeleton`, and **all 315 items carry one**, so the approach gate had
    been running on them all along. A probe that looks in the wrong place reports a defect that does not
    exist; the fix was to the probe, not the data.
  - **Numbers after the wave.** 315 items — Maths 130 / 1903 marks, Physics 90 / 1106, CS 56 / 838,
    BM 39 / 563. Difficulty split **5 / 182 / 128**, evidence **230 / 315**, assertions **3600**,
    figures **89 (83 svg / 4 code / 2 table)**. Bank-wide difficulty-5 share 41%, difficulty-3 2%. All
    five new items are `ok` with **zero warnings**, so the bank total stayed at 176. Similarity on the
    new items: external ≤ 0.039, internal ≤ 0.042, approach ≤ 0.173.
  - **The originality pass is not idempotent across batches, and a diff on old files is expected.**
    Adding items can change which item is *nearest* to an existing one, so `similarity_check.py --write`
    rewrote `nearest_internal_id`, `max_internal_similarity`, `max_approach_similarity` and
    `nearest_approach_id` in **five older Maths files** (13 lines) with no data change to the items
    themselves. This is the gate working, not collateral damage — but a batch's diff is therefore not
    confined to the batch's own files, and a reviewer who expects otherwise will read a healthy diff as a
    mistake.
- **Batch 28 — DONE (5 items, 315 → 320; the CS P1 Section A gap closed by paper structure).** The brief
  was a structural one, not a subject-share one, and it came from the guide rather than from the coverage
  tool: `coverage.py --next 12` returned **0 gaps**, because every node was already covered, so node
  thinness was a dead end. CS HL Paper 1 is 2 h / 40% / **80 marks**, and the guide splits it into Section
  A at **56 marks** and Section B at 24. The bank held **12 of its 44 CS P1 items** in Section A. Attributing
  items to nodes by their id prefix showed why: five Theme A nodes — **A1.4, A2.4, A3.3, A3.4, A4.4** — had
  **no Section A item at all**, each already carrying an item on another paper or section. All five new
  items are Section A extended-response items on those five nodes, so Section A went **12 → 17 of 49** and
  the number of Theme A nodes represented in Section A went **7 → 12**.
  - **The guide was read for every node before anything was written**, because the brief bound the batch to
    in-syllabus content. A1.4.1 asks the candidate to *evaluate* interpreters and compilers and names
    bytecode interpreters and cross-platform development; A2.4.1 asks for the *effectiveness* of firewalls
    and names rules and the limitations of firewalls; A3.3.6 asks how transactions maintain integrity and
    names isolation; A3.4.2 names *append-only* and *time-variant* data; A4.4.1 names *consent* and
    *accountability*. Each item is built on its node's own bullet rather than beside it.
  - **Two of the five planned items were already owned by existing items, and were replaced.** A
    de-duplication sweep across all 315 items found that `CS-A3.3-201` (16 marks, COUNT(*) against
    COUNT(column), AVG, GROUP BY and HAVING over a NULL row) already covered the planned A3.3 item, and
    that **three** items already covered the planned A4.4 item — `CS-A4.3-301` (a 96% accuracy figure that
    is an artefact of a scan-level rather than patient-level split, which uses the same 77.5% the planned
    item was going to use), `CS-P2-007` (one 82% precision figure hiding two areas) and `CS-P2-003`
    (accuracy on imbalanced data). The slots moved to **A3.3.6 transactions** and **A4.4.1 consent
    withdrawal**, both of which nothing in the bank covered. The sweep also confirmed three planned items
    were clear: firewall rule shadowing (2 incidental matches bank-wide), append-only latest-snapshot reads
    (`CS-A3.4-001` mentions the term once, in passing, about key-value writes) and ACID/lost update (all
    matches incidental).
  - **The five items, all difficulty 5, one lever each, all figure-bearing.** `CS-A1.4-301` (13 marks,
    `derived_limit`): three translation strategies whose compiler-versus-interpreter crossover at N = 75 is
    never on the cheapest frontier, because the bytecode build costs 840 where the two that cross cost
    1500. `CS-A2.4-301` (12, `wrong_design_cost`): a four-rule packet filter in which rule 3 is unreachable
    for every flow, because rule 2's destination set contains rule 3's and sits above it. `CS-A3.3-301`
    (13, `seeded_anomaly`): two interleaved transfers where both read 500, both commit, and the committed
    balance is 550 instead of 650. `CS-A3.4-301` (13, `partial_cancellation`): an append-only load table
    whose two natural wrong totals err in opposite directions, 5600 (over by 2000) and 2600 (under by
    1000), against a correct 3600 which is neither of them nor their average of 4100. `CS-A4.4-301`
    (12, `implicit_dependence`): 900 withdrawn records, all 900 of them already used by one of two training
    runs, against a deletion that is 1.5% of the corpus and removes nothing from the model.
  - **Every number was verified before any prose was written**, through the gate's own `evaluate()`: 56
    assertions across the five items, plus ~60 numeric checks. The first run reported five failures, all of
    them faults of the *checker* rather than the data: the frontier enumeration compared `(cost, letter)`
    tuples, so it broke ties alphabetically and reported B cheapest through N = 20 and A cheapest from
    N = 240. Both are exact ties (B = C = 400 at 20; C = A = 2160 at 240), and the item now names them as
    ties, with the ranges running 0–19 for B, 21–239 for C and 241+ for A. A helper that silently resolves
    a tie invents a boundary that does not exist — the same class of error the item itself is about.
  - **Numbers after the wave.** 320 items — Maths 130 / 1903 marks, Physics 90 / 1106, **CS 61 / 901**,
    BM 39 / 563. Difficulty split **5 / 182 / 133**, evidence **235 / 320**, assertions **3656**, figures
    **94 (88 svg / 4 code / 2 table) = 29.4%**. Bank-wide difficulty-5 share 42%; CS rose 36% → **41%**,
    still inside the 50% cap. All five new items are `ok` with **zero warnings**, and the bank total stayed
    at **0 failures**. Similarity on the new items: external ≤ 0.003, internal ≤ 0.008, approach ≤ 0.191 —
    `CS-A1.4-301`'s nearest neighbour is `MATH-AHL3.3-001`, not `CS-A1.4-001`, which is the reframing
    working. `FIGURE_COVERAGE_FLOOR` went 0.28 → **0.29**, leaving **4** non-figure items of headroom.
  - **The audit's lever section now reads 13 of 13**, and the largest single share fell to **14%**
    (`non_governing_variable`, 34 of 235). The five levers used here are all distinct, so no share moved by
    more than a point.
- **Batch 29 — DONE (5 Physics HL Paper 1A MCQ clusters, 320 → 325).** The brief was a component of the
  paper rather than a node, because `coverage.py --next 12` returned **0 gaps** for the third wave running.
  Physics Paper 1 is 2 h and carries 60 of the 150 written marks — 40 for P1A (MCQ) and 20 for P1B
  (data-based) — but the bank held **14 MCQ clusters carrying 70 of its 1106 Physics marks, 6%**, against
  a 27% share of the written assessment. Worse, only **one** of those 14 carried a figure, so the component
  that is *most* graphic in the real paper was the least graphic in the bank. This wave adds five clusters,
  five marks each, one per theme, on the five Physics nodes that had no P1A cluster at all: **A.3, B.3,
  C.1, C.4, E.3** (D is the only theme whose every node already carried one).
  - **MCQ has its own length contract, and it is per question rather than per item.** `validate.py`
    measures an MCQ cluster against `per_part_answer` (45 words a question), `base_notes + per_part_notes`
    and `base_expl + per_part_expl`, and skips the subject-median test entirely — a five-mark cluster is
    judged as five one-mark questions, not as a 15-mark extended response. Without that the whole cluster
    would be failed by a median built from 15-mark items. Final counts: answer 269–385 words against a
    225 floor, notes 228–315 against 155, explanation 395–469 against 185, context 201–241 against 175.
  - **Every cluster was designed from a different lever, and the two thinnest levers in the bank were
    both used.** `MATH`-side shares at the start of the wave were `variable_swap` 5 and `quant_vs_judgement`
    10; this wave takes `variable_swap` to 6 with the closed-pipe/open-pipe reversal below. Physics gains
    five distinct levers — `non_governing_variable`, `derived_limit`, `decoy_technique`, `variable_swap`,
    `implicit_dependence` — and no share moves by more than a point. All 13 levers remain in use.
  - **`PHYS-A.3-501` (A.3 Work, energy and power, d4).** A force-distance graph that rises to 6.0 N,
  holds, and falls back to zero, against a constant 2.0 N of friction that the figure does not show. The
  lever is `non_governing_variable`: the greatest applied force does not decide where the kinetic energy
  peaks. Setting F(x) = 2.0 N on the falling branch, F = 16.0 − 2.0x, puts the peak at **x = 7.0 m** —
  two metres past the force maximum and one metre before the force vanishes. Five distractors are the
  exact results of five named errors: 48.0 J from peak-force-times-distance, 27.0 J from a missed
  triangle, 11.0 J by carrying that 27.0 J forward, 3.37/4.69 m s⁻¹ for displacement and distance
  interchanged, and 20.2 W from reusing the final speed in an instantaneous-power question.
  - **`PHYS-B.3-501` (B.3 Gas laws, d5).** A p–V diagram whose second change is a *straight line*. Because
    the isotherms of an ideal gas are rectangular hyperbolae, a straight segment must cut through a family
    of them and cross a maximum in its interior. Writing p = 4.0×10⁵ − 5.0×10⁷V gives
    pV = 4.0×10⁵V − 5.0×10⁷V², a downward parabola stationary at **V = 4.0×10⁻³ m³**, the midpoint, where
    pV = 800 against **600 at both labelled endpoints** — so the gas is a third hotter in the middle of the
    line than at either end and reaches **1200 K**. Deliberately, nothing here asks for work or energy:
    the area under a p–V graph is B.4, and the trap lives entirely in the state variables, which is what
    keeps the item inside its own node. The distractor 2700 K multiplies the greatest pressure by the
    greatest volume, a corner the gas never occupies.
  - **`PHYS-C.1-501` (C.1 Simple harmonic motion, d4).** A vertical mass-spring oscillator, where the
    equilibrium position is not the unstretched length. The lever is `decoy_technique` and both decoys are
    *correct physics*: the pendulum period 2π√(L/g) is a real formula and 1.42 s is a real number, but this
    oscillator's period is 2π√(m/k), which collapses to **2π√(e/g) = 1.00 s** once mg = ke is substituted —
    the mass cancels and the amplitude never appears. And 1.000 m is the correct greatest length for a mass
    released from the spring's natural length; this mass is released 0.050 m below equilibrium, so the
    longest length is **0.800 m**. A correct result from a different setup is the most convincing kind of
    wrong answer, which is why both are offered.
  - **`PHYS-C.4-501` (C.4 Standing waves and resonance, d5).** Two 0.850 m pipes, one stopped at one end,
    one open at both ends, and the same comparison asked twice with a different quantity held fixed. At
    equal length the stopped pipe is an octave lower — 100 Hz against 200 Hz. At equal pitch the stopped
    pipe is **half as long** — 0.850 m against **1.70 m**. The ranking reverses, so the distractor built for
    the second comparison (0.425 m) is exactly what a candidate who carries the first ordering across will
    choose. Alongside it, the harmonic number and the position in the list of resonances are made to
    diverge: the stopped pipe supports only odd harmonics, so the third *resonance* is 500 Hz while the third
    *harmonic* is 300 Hz, and 400 Hz is not a quiet resonance but no resonance at all.
  - **`PHYS-E.3-501` (E.3 Radioactive decay, d4).** This is the one item of the five with no figure, and the
    omission is deliberate: the natural figure here is a decay curve, and a decay curve drawn against a
    background line would print the answers to parts (c) and (d) straight onto the page. The lever is
    `implicit_dependence`. The exponential governs the activity and nothing else: 960 and 120 counts over
    120 s with a 4.0% detector give a corrected rate of 7.00 s⁻¹ and an activity of **175 Bq**, and the
    corrected rate really does quarter to 1.75 s⁻¹ in 24 h — but the recorded rate falls only from 8.00 to
    **2.75 s⁻¹**, a factor of **2.91**, because a constant background commutes with no fold-change. The
    same offset puts the halving of the recorded rate at **14.7 h** rather than 12 h: a term that does not
    decay can only delay a fall towards it. Every distractor is the number the exponential alone would give.
  - **Four figures, and a fifth item deliberately without one.** Physics MCQ figure share goes **1/14 to
    5/19** — the component where a figure is most obviously wanted was the one carrying almost none.
    All four are built by the same plain-Python string builders, so the validator's fingerprint check stays
    satisfied by construction, and all four were audited against the giveaway rule **as parsed text nodes**,
    not by reading the SVG: the force-distance graph prints no areas, the p–V diagram prints no pV products
    and no temperatures, the spring diagram stops at the equilibrium length and never shows the lowest
    point, and the pipes carry no standing-wave envelope. The rendered contact sheet then caught one real
    defect the text audit could not: the p–V y-axis label `p / 10⁵ Pa` overflowed the `viewBox` and was
    clipped to `› / 10⁵ Pa`, which is why it is now rotated.
  - **The answer key was distributed, and the defect it fixes was found in this bank's own MCQ.** Every
    cluster is authored with the correct option first, which is fine for one item and puts the key at A in
    **all fourteen** pre-existing MCQ clusters. The site renders the answer text but not the options, so a
    student working through the answer booklet would read the letter A twenty-five times in a row — the same
    class of defect the BPhO wave found, in a different bank. The spread is a fixed rotation applied in the
    assembler (**A6 B6 C7 D6** over the 25 questions), with a check that the letter stated in the answer
    matches the keyed option, and the option texts, rationales and arithmetic are untouched. Whether the
    existing fourteen should be redistributed too is a follow-up worth doing; it is noted in `STANDARD.md`.
  - **Two gates bit, both fixed at the item.** The `PHYS-B.3-501` distractor written as "0.2407 mol" was
    wrong physics, not wrong arithmetic: dividing by 900 K instead of 300 K gives **0.0267 mol** —
    a *smaller* answer, because a higher temperature means fewer moles for the same pV. 0.2407 mol is the
    result of carrying the *volume* of state B into the numerator instead, and both errors are now separate
    options with the rationales they deserve. The self-check caught it before the file was written, because
    every distractor is asserted in `verification.assertions`.
  - **Numbers after the wave.** 325 items — Maths 130 / 1903 marks, **Physics 95 / 1131**, CS 61 / 901,
    BM 39 / 563; 4498 marks in all. Difficulty split **5 / 185 / 135**; every subject inside the 50% cap
    (Maths 45%, Physics 44%, CS 41%, BM 23%). Evidence **240 / 325 (74%)**, `difficulty 5 with no evidence`
    **0**, `labels the evidence does not permit` **0**, assertions **3769**. Physics P1 goes 31 items / 301
    marks to **36 / 326**, and P1A from 14 clusters to 19.
  - **The ratchet moved to its tightest setting yet.** Coverage went **94/320 = 29.4% → 98/325 = 30.2%**, so
    `FIGURE_COVERAGE_FLOOR` moves **0.29 → 0.30**. That leaves **1 non-figure item of headroom** (98/326 =
    30.06% still passes, 98/327 = 29.97% fails) — the next batch carries a figure on almost every item or
    it does not ship. Similarity on the new items: external ≤ 0.018, internal ≤ 0.044, approach ≤ 0.160; the nearest
    external neighbour of the gas-laws item is `PH_HL_Option_B_HL-paper2_q14`, and of the decay item
    `PHYS_HL_P1_2004May_TZ2_q37`. Bank-wide maxima are unchanged at 0.090 external / 0.073 internal /
    0.366 approach.
- **Priority-3 ("stretch") tail:** optional deeper items beyond the must/should nodes — open when there is
  appetite; the four subjects are otherwise complete for priority-1 and priority-2 coverage.
- **Printables — DONE.** `site/papers/` holds a printable question paper and a matching answer booklet
  for each subject (8 files), regenerated by `build.py` on every build. The question paper prints no
  answers and no markscheme notes; the answer booklet carries the full answers. Current headers: maths
  130 questions / 1903 marks, physics 95 / 1131, CS 61 / 901, BM SL 39 / 563 — all difficulty 3–5, May
  2028 cohort.

Quality over quantity is explicit: a batch ships only when every item in it passes all gates. If that
means a batch of three, it ships three.

---

## 10. Decisions I need from you

1. **Volume target** per batch, and whether you want a target total per subject.
2. **Printable papers:** should I assemble timed papers (P1/P2/P3 style; BM P1/P2 only) once there is
   enough material, or keep it as a flat question collection?
3. **Linking:** add a card for this bank on the main `index.html` and in the nav of the other sites?
4. **The 2,827 un-imported generated questions** in `backend/generated/`: ignore them, or mine them for
   ideas (they would still have to be fully rewritten to meet §4/§5)?
5. **BM difficulty ceiling:** at SL, how hard do you want it — exam-grade hard (a 7 that requires real
   judgement), or stretched beyond anything the SL paper would actually ask?

CS syllabus version is no longer open: the 2027 guide is the one you sit, so Theme A/B it is.
