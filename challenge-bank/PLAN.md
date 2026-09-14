# IB Challenge Bank — Generation Plan

**Cohort: class of 2028 (final examination session May 2028).**
**Status: live. 224 questions across the four subjects, every priority-1 and priority-2 syllabus node
covered (166/166 nodes, 100%). The difficulty label is now a measured property rather than a declared
one: from 2026-09-13 every item must carry `difficulty_evidence`, and 60 of 224 do. The remaining 164 are
a published, ratcheting backlog — see `STANDARD.md` §2.2–§2.5 and `tools/difficulty_audit.py`. All 13
lever types are in use, and the Physics difficulty-5 share has been designed down from 62% to **49%**,
which brings every subject inside the 50% cap and clears the calibration debt. The only outstanding debt
is that no item claims difficulty 3, so the 3–5 scale still reads as two points.
The `topic` label is now a closed vocabulary per subject, enforced by `validate.py`, and is shown on every
question page and filterable on every subject page.**

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
- **Priority-3 ("stretch") tail:** optional deeper items beyond the must/should nodes — open when there is
  appetite; the four subjects are otherwise complete for priority-1 and priority-2 coverage.
- **Printables — DONE.** `site/papers/` holds a printable question paper and a matching answer booklet
  for each subject (8 files), regenerated by `build.py` on every build. The question paper prints no
  answers and no markscheme notes; the answer booklet carries the full answers. Current headers: maths
  97 questions / 1492 marks, physics 67 / 842, CS 34 / 553, BM SL 26 / 387 — all difficulty 4–5, May
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
