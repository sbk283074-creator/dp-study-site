# IB Challenge Bank — Generation Plan

**Cohort: class of 2028 (final examination session May 2028).**
**Status: live. 62 questions across the four subjects, all published, all gates passing.**

New folder: `challenge-bank/` (inside `dp learning final/`). It holds the question data and a
standalone static website that collects and presents the questions.

Line-up: **Mathematics AA HL · Physics HL · Computer Science HL · Business Management SL.**

---

## 1. What we are building, and why it is not the existing bank

The existing question bank (`dp learning/ib-dp-platform/backend/data/app.db`, 9,969 questions) is a
**retrieval** corpus: real IB past papers plus topic extractions. It is good for practice and search.

This new bank serves the opposite purpose: a small, hard, **original** set of questions that force the
reasoning the real exams only occasionally demand. It is deliberately small and deliberately
uncomfortable.

| | Existing qbank | Challenge Bank (this project) |
|---|---|---|
| Provenance | Real IB papers + extractions | Original, or adapted from non-IB sources |
| Size | 9,969 | Tens per subject, grown slowly |
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
   against (a) all 9,969 rows of `app.db`, (b) the 2,827 un-imported items in
   `backend/generated/*.json`, (c) every previously published Challenge Bank question. Method:
   5-gram + token-set Jaccard/cosine over normalised text, per subject.
   **Reject if max similarity ≥ 0.35 within the same subject**, or ≥ 0.50 cross-subject. The nearest
   match id and score are stored in `originality`.
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
- **Batch 5+:** continue from `coverage.py --next`. Maths Topic 5 is still the largest hole
  (32/83 overall), with 3.9, 5.12 and 5.15 the next must-cover nodes, and Physics E.4/E.5
  (fission, fusion and stars) the only must-cover Physics nodes left. BM is 26/34: its remaining eight
  nodes are all priority-2 Toolkit tools (SWOT, Ansoff, STEEPLE, BCG, business plan, decision trees,
  descriptive statistics, circular business models), which the brief orders after every priority-1 node.
- **Printables:** assemble `site/papers/` (printable practice papers plus matching answer booklets)
  once a subject reaches roughly 20 items; at 13 per subject the bank is close but not there yet.

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
