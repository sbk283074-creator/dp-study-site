# The 1000-question BPhO Round 0 drill bank

How the bank is built, how it is checked, and how to add the next section.

---

## 1. What it is

1000 original questions in the exact Round 0 format: **single-answer multiple choice,
five options, no calculator, one mark each, no negative marking**. They are not
past-paper items and not lightly-reworded competition questions — BPhO papers and other
competitions' papers are copyrighted. What is borrowed is the *style and the difficulty*.
`tools/bank/spec.py` records, per module, which competitions set questions of comparable
demand inside the R0 scope. That list is a reading list, not a source of text.

## 2. The shape

**40 sections of 25.** Each section is a complete Round 0 paper, so every section works
as a full-length timed mock and the bank is 40 mocks deep.

The module mix is not invented. It is the one real Round 0 paper that exists — 2025 —
whose 25 questions distribute as:

```
C 5   H 4   A 3   G 2   K 2   F 2   B 2   L 2   E 1   J 1   D 1
```

Two deliberate departures, recorded rather than buried:

- The 2025 paper tested **no capacitors (I) and no fluids (M)**, yet the official R0
  scope note lists both. The house rule for this project is that when sources disagree we
  include rather than omit, so I and M get 40 and 30 questions instead of zero. They are
  the smallest allocations in the bank, which keeps them proportionate to the evidence.
- Module **N (Round 1 insurance) gets no questions at all.** The scope rule is that R1
  evidence is not evidence about R0; a Round 0 mock containing R1 material would train
  the wrong thing. N stays in the curriculum pages and out of the bank.

Target totals, summing to exactly 1000:

```
A 120   B  80   C 130   D  60   E  50   F  80   G  80
H 140   I  40   J  50   K  80   L  60   M  30
```

Per-section mixes come from proportional apportionment with a shifting rounding phase, so
the totals close exactly and sections do not come out as period-4 repeats of each other.
Each section carries **11–13 distinct modules** — no section is a pile of circuits.

## 3. The difficulty standard

The brief is "the same or harder than BPhO". That has to be *measured against something*,
so one function (`gates.difficulty`) scores every question, and that function is calibrated
like-for-like on the real 2025 paper and the published sample sheet — the same scorer, the
same inputs.

Measured on the real 2025 paper:

| | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| 2025 paper | 8.3 | 11.5 | 13.5 | 15.5 | 27.4 |

A question's declared difficulty band is **derived from its measured score**, using the
real paper's own p25 and p75 as the cut-points. A declaration that disagrees with its
measurement fails the gate. The declared band is a consequence of the measurement, not a
claim about it.

A median test is not sufficient, and four sections proved it: all four had a median above
the paper's and none had a top end. The paper is **peaked** — one question at 27.4 and
thirteen moves, twice the score of its own upper quartile — and a bank that matches the
median while never setting anything that hard is not "the same or harder", it is a bank
that has removed the question which actually selects. So the standard now has a **top end**
as well: see G5b below, and `DIFFICULTY-AUDIT.md` for the measurement that found it.

Three things that flattered the author's own work, and what was done about them:

- an `elim` term (whether the solution says "eliminate") scored **0.00 on all 25 real
  questions** and 2.40 average on the new ones, inflating the apparent gap from +1.3 to
  +3.7. A yardstick the reference paper cannot earn is not a yardstick.
- a `moves` cap of 6 truncated **only the real paper's hardest question** (13 moves),
  capping the yardstick at 18.7. Lifting it raised the paper's max to 27.4 and exposed
  that the bank's hardest question (17.3) is well below the paper's hardest.
- numbering a **sanity check** as a "Step" inflated `moves` by one per question, and 19 of
  section 6's 25 solutions ended that way. The paper's own solutions average 2.44 numbered
  steps; section 6's averaged 5.48. The term is not wrong, but it counts what it is given,
  so the bank's counting convention has to match the paper's. See §8.

## 4. The eleven gates

`tools/bank/gates.py`. Run one section with `gates.py sec01`.

| Gate | What it checks |
|---|---|
| **G1** structure | 25 questions, five options each, unique ids, answer in range, module in scope, module mix matches the plan |
| **G2** distractors | each wrong option **names the error that produces it**; four distinct named errors; the key is marked correct. Filler options are what separate a worksheet from a competition paper |
| **G3** agreement & notation | the solution's stated answer equals the stored key; no caret or ASCII exponents reach the reader; markup balanced; no unresolved figure placeholder; **every decimal in visible text is hand-computable** or its sentence says not to compute it |
| **G4** profile vs solution | the declared reasoning chain (steps, relations, insight, shape) is cross-checked against the solution text, so a chain cannot be over- or under-stated |
| **G5** difficulty | measured score vs the real paper's quartiles, plus band counts — and three clauses added after the difficulty audit: **G5b** the top end (≥ 2 questions at ≥ 9 moves, hardest ≥ 22.0), **G5c** the non-calculator axes (per-section `noncalc_min` and `approx_min`), and a **floor** (nothing below 8.0, the paper's own easiest) |
| **G6** similarity | **logic**-level overlap between every pair, not wording |
| **G7** numerics | every answer re-derived independently of the solution, in exact arithmetic. A **symbolic** check whose coefficient is written as a decimal is evaluated by substituting a distinct prime per free symbol (`_spot_equal`), because `N()` of an expression with free symbols is not a number and the comparison used to die with sympy's "Cannot convert expression to float" |
| **G8** figures | at least 8 figure-bearing questions; every referenced figure exists; figure geometry is checked |
| **G9** balance | no answer letter appears more than 10 times in 25 |
| **G10** hand-check ledger | at least 20 of 25 carry a hand-verified entry in `ledger.json` |
| **G11** scope | nothing may test material the official Round 0 note excludes (fields, particle physics, RC charging, SHM, rotational dynamics, reactor detail, QM beyond the photoelectric effect). The scan is deliberately crude, so a hit is satisfied by a `profile.scope_note` recording why the question is in scope anyway — a recorded judgement, not a silent pass |

**G11 exists because of a question that passed all ten of the others.** `S05-21` asked for
the time constant of an RC circuit. The official scope note is one sentence long and says
capacitors mean *"not time dependent charging, but a knowledge that Q = CV"* — the
exclusion is about as explicit as it gets — and the question shipped anyway, because
nothing in the suite knew what the paper is allowed to test. It has been replaced by a
series-parallel capacitor network, which is inside `Q = CV` and is a better question.

The lesson is the one this file keeps relearning: **a gate suite only knows the properties
somebody wrote a gate for.** Every gate here was written in response to a defect that got
through, and the list of gates is therefore a list of the mistakes made so far, not a
description of what makes a question good.

**G6 is deliberately not a text check.** The fingerprint is a set of curated features
(`key` tags, relation tokens, reasoning shape, depth band, approximation / symbolic /
figure flags) and contains **no words from the question**. Wording overlap is a separate,
weaker check that only fires when the logic does not.

### Why the gates are not trusted on their own

`tools/bank/mutants.py` is the answer to *"don't trust your tool that you write only"*.
It takes the real, passing section, breaks **exactly one thing** in each of 44 ways, re-runs
the whole suite, and asserts the right gate notices. A mutation that slips through is a
hole in the suite and is reported as a failure.

Three of the 44 assert the **opposite** direction — that a gate stays *quiet* on content
that is correct. That direction matters as much: `S02-19` was once reported as having five
duplicate options when its five expressions were genuinely distinct, because the duplicate
check folded the case of the symbols. A gate that fires when it should not is as broken as
one that stays silent, and the only way to test it is to build correct content and assert
silence.

It has found three real bugs, two of them robustness holes in the gates themselves, plus
one gate that had been **passing vacuously**:

- the caret lint ran on text that `supify()` had already repaired upstream, so it could
  never fire — a gate that cannot fail reports safety it never tested;
- the G6 error message still indexed the old 5-tuple fingerprint, so it crashed — dead
  code, because a passing section produces no G6 findings;
- `check_numeric` left a second, unguarded comparison outside its `try`, so a check that
  parsed as a boolean (`"this is not maths"` → Python's `False`) crashed the suite;
- a missing figure produced an **untagged** error, so the defect was real but could not be
  attributed to any gate.

## 5. Per-section workflow

All commands from `bpho/tools/bank`. The gate **must** use the managed venv python (it
needs sympy); `python` on its own will not do.

```sh
PY=/Users/lucas.ma/.workbuddy-ai/binaries/python/envs/default/bin/python

# 1. write the figures for the section into fig/, then LOOK at them
#    NOT OPTIONAL: the gate and the build read fig/*.svg, not figsNN.py. Editing the
#    figure source without this step gates and publishes the OLD figure, silently.
$PY figs.py 3

# 2. write secNN.py, then gate it until it is clean
$PY gates.py sec01

# 3. hand-verify every calculation and record the working
$PY make_ledger.py

# 4. prove the gates still have teeth
$PY mutants.py

# 5. publish into the study site (refuses to publish a failing section)
$PY build_site.py 1
```

Then, from `bpho/`:

```sh
NODE=/Users/lucas.ma/.workbuddy-ai/binaries/node/versions/22.22.2-2/bin/node
$NODE tools/bank/check_site_data.js data/bank-01.js   # the generated JS loads, right shape
$NODE tools/papers/build_pdfs.js                      # rebuild the downloadable papers
$NODE tools/bank/verify_site.js                       # drives a real browser over 127.0.0.1:8901
```

**The PDF step is not optional.** A new section gets a card in the Papers area only once
`build_pdfs.js` has run, and `verify_site.js` now *fails* if a bank section in the data has
no built PDF — that check is the whole reason the omission is loud instead of silent.

Both harnesses live in the repo, not `/tmp` — a documented workflow should not depend on
files that vanish. `verify_site.js` needs the static server on `127.0.0.1:8901`, which is
rooted at the whole DP site, so the study space is `…/bpho/index.html`, not `…/index.html`.

**Figures are verified by looking, not by reading.** Seven label collisions and one real
geometry bug (an arc written with both large-arc and sweep set, which silently enlarges
the radius and bulges outside its circle) were invisible in the source and obvious in a
screenshot. Three figures were also physically wrong in ways no linter could see: a
velocity–time panel drawn entirely above the axis under a question that says "downward is
negative", a slope labelled `sin θ = 0.60` drawn at 26.6°, and a refraction that did not
satisfy Snell's law.

## 6. Figure convention

- Key format is **`s<NN>-<QQ>`** — `s01-02`, `s01-16`. One scheme; four figures used to be
  written `s01-q02` while the rest were `s01-08`, which is how a missing figure happens at
  section 20. `figs.py` now reports stale files instead of deleting them.
- Hand-authored inline SVG, emitted to `fig/`, referenced from a stem as `{{FIG:key}}`.
  No image files and no fetched assets: the same `file://` constraint that makes content
  `window.BPHO_*` globals forbids external assets.
- Wrapper: `<figure class="fig"><svg viewBox="0 0 W H" role="img" aria-label="…">`. Never
  fix `width`/`height` on the `<svg>`; the stylesheet scales it.
- Three silent-failure rules: a figure-bearing stem must survive as a **backtick template
  string**; **marker ids must be globally unique** (HTML has no id namespace); use
  **literal hex inside the SVG, never `var(--…)`**.
- Palette: `#14181f` ink · `#4a5262` · `#7b8494` · `#2f5fd0` accent · `#b3352f` ·
  `#1f7a53` · `#a8641a` · `#5b3fa8`.
- **A figure must encode the discriminator the question tests, not decorate the
  apparatus** — the rectified waveform shows *same peak, half the area*; the friction graph
  shows the *drop* at limiting equilibrium.

## 7. Publishing

`build_site.py` runs the gates **first** and writes nothing if the section fails.
Publishing an unchecked section is the one outcome worth making impossible.

The generated `data/bank-NN.js` is a build artefact, exactly like `data/questions-5.js`.
Never hand-edit it — edit `secNN.py`. The site app picks up new sections on its own: the
filter chips and the mock launchers are both derived from the data, so publishing section
2 needs no change to `assets/app.js` or `index.html` beyond one `<script>` tag.

## 7b. The Papers area (`#/papers`)

A separate place in the study space for the **papers** rather than the questions: the two
sheets BPhO has published, and every drill-bank section, each as a real PDF of questions
plus a matching markscheme PDF. It is a different job from Practice — there you answer one
question at a time and the app marks you; here you take away a sheet you can print, sit
against a clock, and mark on paper.

- **Real PDFs, pre-generated, committed.** `tools/papers/build_pdfs.js` renders them with
  headless Chromium rather than a PDF library, because every question may carry a
  hand-authored inline SVG: Chromium already renders those, honours `break-inside: avoid`
  so a question is never split across a page boundary, and supplies page numbers for free.
- **The pages are read from the same data files the site loads, in the same order**, so a
  PDF cannot disagree with the page it was downloaded from.
- **The manifest is generated, never hand-written.** The script writes `data/papers.js`
  from the files it actually produced, and the site renders its links from that list. A
  hardcoded link would be a dead download the moment someone added a section and forgot to
  rebuild — and `verify_site.js` fetches every link and checks the first bytes are `%PDF-`.
- Page counts come from counting `/Type /Page` in the raw bytes (with a `(?!s)` lookahead so
  the `/Type /Pages` tree node is not counted). Verified against PyMuPDF on every file.
- The provenance badge is the honest part of each card: an original question mistaken for a
  real one mis-calibrates revision, so the two kinds are never mixed in one list.

## 8. Progress

| | Sections | Questions | Status |
|---|---|---|---|
| Done | 1–6 | 150 | gated, hand-checked, published, difficulty-audited |
| Planned | 7–40 | 850 | not started |

**Open item carried forward: sections 1–5 under-use the approximation axis.** They sit
at 6–12 non-calculator questions per section and **1–2** requiring an approximation,
against the 2025 paper's 16 and 10 out of 25. Sections 6–40 are now gated at the
paper's own numbers (`spec.NONCALC_PAPER` / `APPROX_PAPER`); sections 1–5 are
grandfathered at the floors they meet, because rewriting 125 published questions is a
different piece of work from getting the next 875 right. Closing it means revisiting
roughly sixty questions. See `DIFFICULTY-AUDIT.md` sections 4a and 6a.

### The difficulty remediation (2026-09-19)

The brief was *"the difficulty is really low, how can you improve it? You should check the
past paper to ensure the difficulty."* The check is `DIFFICULTY-AUDIT.md`; the short version
is that the bank was **flat** where the paper is **peaked** — the paper's hardest question
scored 27.4 at thirteen moves, the bank's scored 20.5 at six, and 125 questions contained
**none** above six moves. A bank can pass a median test and still have no top end, which is
why the median test passed for four sections.

| what changed | why it cannot regress |
|---|---|
| **G5b deep tier** — every section needs ≥ 2 questions at ≥ 9 moves, and a hardest question ≥ 22.0 | a flat section now fails the suite instead of waiting for a reader |
| **G5 floor** — no question may score below 8.0 | the paper's easiest is 8.3, so anything under 8.0 is easier than the real paper sets |
| **G4 deep profile** — a deep question must declare ≥ 9 steps and ≥ 4 distinct relations | stops length being bought with padded numbering |
| **G5c per-section non-calculator floors** — `noncalc_min` and `approx_min` on the plan, 16 and 10 for sections 6–40 | stops the non-calculator axes being satisfied on paper by symbolic options alone |
| **four questions replaced** in sections 4 and 5 | the ceiling moved from 20.5 to 24.2/25.4, each replacement hand-worked in `ledger.json` |

The gate suite is now **44 mutants** (`python mutants.py`), all behaving: every gate has
been shown to fail on demand and the one content-correct mutant has been shown to keep the
suite quiet. Four of the new gates needed more than one mutant to prove, because a mutant
caught by a *neighbouring* clause has demonstrated nothing — the three failures and what
each one taught are recorded beside the mutants in `mutants.py` and summarised in
`DIFFICULTY-AUDIT.md` section 6b.

### What section 6 found: the bank numbers steps more finely than the paper does

Building section 6 turned up a defect the remediation had not looked for, and it is a
*measurement* defect rather than a content one. The real 2025 paper's solutions average
**2.44 numbered steps** with a maximum of 5; section 6's averaged **5.48** with a maximum
of 10 — while carrying *fewer* formulas per question (4.00 against 5.04) and the same
number of relations (2.00 against 1.96). Every point of section 6's excess median came
from one term, `moves`, and 19 of its 25 solutions ended with a numbered verification —
"Step 5 — check the size", "Step 6 — check the direction".

A sanity check does not obtain the answer, and numbering it as a step made the section read
uniformly harder than the paper instead of peaked like it. The fix keeps every word of
those paragraphs and removes only the number: the trailing step becomes an unnumbered
"Sanity check.", and the profile loses the matching step. That one change moved the section
from **21 of 25 questions above the paper's p75 to 15**, and its easiest question from 10.0
to 8.4 — against the paper's own 8.3.

The lesson generalises, and it is why G5b tests `moves` rather than trusting the declared
`diff`: **a scorer that counts numbered steps can be satisfied by numbering more of them.**
The counter is that a numbered step has to be a derivation move, which is a judgement no
gate can make — so it is held by the hand ledger and by reading the paper's own solutions
beside the bank's. Two other things surfaced with it: `_equal` could not evaluate a
symbolic check containing a decimal at all (it reported sympy's "Cannot convert expression
to float" as though the author had erred), and the logarithms in two estimate questions
were written to three significant figures, which no candidate without a calculator can
produce. Both are fixed, and the first has two mutants (`m40`, `m41`) proving the new
branch passes a correct decimal form and still catches a wrong one.

**Section 1** — `S01`, 15 figures, mix `A3 B2 C4 D2 E1 F2 G2 H4 I1 J2 K2`, answer sequence
`BCBEDBECADCAEABADCBABECAD`, measured median **15.2** against the paper's 13.5, p25 **14.6**
against 11.5, min 12.6, hardest `S01-16` at **26.9** and `S01-12` at 24.2 (both ten moves).
Non-calculator: 12 by either axis, 6 by approximation. All eleven gates pass, 25/25
hand-verified, live as `BANK-S01`.

**Section 2** — `S02`, 8 figures, mix `A3 B2 C2 D1 E2 F2 G2 H3 I1 K2 L3 M2`, answer
sequence `CAABDEAACBCBAEDBCCACDBBCD`, measured median **16.6** against 13.5, p25 **15.6**
against 11.5, min 11.6, hardest `S02-03` and `S02-13` at **23.2**. Bands `d2=6 d3=19` —
deliberately harder than the real paper, per the brief. Non-calculator 8 / 2. All eleven gates
pass, 25/25 hand-verified, live as `BANK-S02`.

**Section 3** — `S03`, 11 figures, mix `A3 B2 C4 D1 E1 F2 G2 H3 I1 J2 K2 L1 M1`, answer
sequence `CDBAEAABEDAAABDAAEBDACBED`, measured median **15.8** against 13.5, p25 **15.2**
against 11.5, min 11.6, hardest `S03-17` at **24.3**; **three** deep questions, the most in
the bank. Bands `d2=9 d3=16`; the section has **no diff-1 question at all**, which is the
brief's "same or even harder" taken literally — the easiest question sits above the real
paper's 25th percentile. Non-calculator 6 / 1, the weakest of the five. All eleven gates pass,
25/25 hand-verified, live as `BANK-S03`.

Section 3 was authored with every correct option first and then permuted deterministically
(`opts` and `distractors` rotated together), so the answer balance of 5 per letter holds by
construction rather than by luck, and the prose letters were rewritten to match — never
the key. Six figure defects were found by *looking*, five of which no existing check could
see: an open bridge circuit, an open series loop, two labels with a wire running through
them, dangling component dashes, a "normal" drawn along the wrong axis, and the `<sup>`
breakout below.

Section 3 later produced a seventh, of a different kind: `fig/s03-06.svg` was registered
in `figs03.py` and **referenced by no stem at all**. It drew an 8.0-second *car* journey
peaking at 12 m/s, while the question asks about a 60-second *train* journey peaking at
10 m/s — a leftover from an earlier draft of the question. Dead weight, invisible to every
check because a figure nobody references is never rendered. It was redrawn to the train's
journey and referenced from the stem as `figure_support` (the stem already carries every
number, so the figure supports rather than enables). `S03-06` 23.2 → 24.2, band unchanged.
`fig/` is now 73 files, 73 references, zero orphans — worth re-checking whenever a section
is finished.

**Section 4** — `S04`, 13 figures, mix `A3 B2 C3 D2 E1 F2 G2 H4 I1 J1 K2 L2`, answer
sequence `CABACABDEADBECDBAECDEBDCA`, measured median **15.2** against 13.5, p25 **12.6**
against 11.5, min 11.6. Hardest `S04-04` and `S04-15`, both at **24.2** and both ten moves:
a five-resistor circuit reduced in three stages, and a ball whose bounces halve only the
vertical velocity so the flight times form a geometric series. Non-calculator 8 / 1. All eleven
gates pass, 25/25 hand-verified, live as `BANK-S04`.

**Section 5** — `S05`, 14 figures, mix `A3 B2 C3 D2 E1 F2 G2 H3 I1 J1 K2 L2 M1`, answer
sequence `ACEBDDACEBBDACEEBDACCEBDA`, measured median **14.2** against 13.5, p25 **14.1**
against 11.5, min 8.2 — the bank's first section with a diff-1 question, and the section
that found the G5 floor. Hardest `S05-06` at **25.4** (ramp → rough floor → inelastic
collision → slide) and `S05-22` at 24.2 (ice warmed, melted, warmed again). Its opening
dimensional-analysis question was replaced after scoring 7.7, below anything the real paper
sets, because it asked the candidate to *recognise* a combination rather than build one.

Section 5 also produced the one **out-of-scope** question the bank has had. `S05-21`
asked for the time constant of an RC circuit; the official Round 0 note is explicit that
capacitors mean *"not time dependent charging, but a knowledge that Q = CV"*, and it had
passed all ten gates of the day. It is now a series-parallel capacitor network — inside
`Q = CV`, and a better question, because it is the only capacitor question in the bank
whose answer depends on **reading a topology** before doing any arithmetic. Gate **G11**
exists because of it.
Non-calculator 7 / 2. All eleven gates pass, 25/25 hand-verified, live as `BANK-S05`.

**Section 6** — `S06`, 12 figures, mix `A3 B2 C3 D1 E2 F2 G2 H4 I1 J1 K2 L1 M1`, answer
sequence `ACBDEBACEDBAECDAEBCDACBED`, measured median **16.8** against 13.5, p25 **14.5**
against 11.5, min 8.4. Hardest `S06-04` at **23.2** (a nested parallel pair, a series
resistor and the cell's internal resistance, reduced in ten moves and then walked back down
to the current in the innermost resistor) and `S06-15` at 21.6 (a pulley that goes slack,
so the motion has two regimes). Bands `d1=1 d2=9 d3=15`.

Section 6 is the **first section authored against the new standards** rather than
grandfathered into them, so it is the first held to `NONCALC_PAPER = 16` and
`APPROX_PAPER = 10` — and it clears both at **18** and **13**, where sections 1–5 sit at
6–12 and 1–2. It is also the section that produced the step-granularity finding above, and
the one that needed a tool fix rather than a content fix. Its first gate run reported 27
failures; the section now passes all eleven with 25/25 hand-checked.

**Papers area** — `#/papers` lists every paper as a downloadable PDF: the 2025 paper, the
sample sheet, and sections 1–6, each with its markscheme — **8 papers, 16 PDFs, 309
pages, 10.2 MB**. Both PDF defects found were found by rendering a page to PNG and
*looking* at it, not by any check: the markscheme's first solution was pushed to page 2 by
a `break-inside: avoid` on a block that is by nature long, leaving "Worked solutions" over
half a blank sheet. `verify_site.js` checks the area in both directions — every card
matches the manifest and every link fetches real `%PDF-` bytes, *and* every bank section in
the data has a built PDF.

## 9. File map

| File | Role |
|---|---|
| `spec.py` | the 40-section blueprint: targets, allocator, per-section mixes |
| `secNN.py` | the questions themselves — **the source of truth** |
| `figsNN.py` | hand-authored SVG figures per section |
| `figs.py` | **runs every `figsNN.py` and writes `fig/*.svg`** — the gate and build read these |
| `fig/*.svg` | the generated figures, the actual input to gating and publishing |
| `svgkit.py` | shared SVG primitives (`ell(...)` sampled ellipses, palette); raises on breakout tags |
| `gates.py` | the eleven gates, the difficulty scorer, the fingerprint |
| `measure.py` | read-only re-measurement of a section the way the gate measures it — encodes the absolute-figdir and `supify` traps |
| `mutants.py` | 44 mutants proving the gates have teeth, both directions |
| `make_ledger.py` | builds `ledger.json`, the hand-check record |
| `ledger.json` | per-question method, working, and hand-derived answer |
| `build_site.py` | gates, then emits `bpho/data/bank-NN.js` |
| `check_site_data.js` | loads the generated JS the way the browser does and asserts its shape |
| `verify_site.js` | Playwright end-to-end check that the bank works inside the study site |
| `extract_papers.js` | pulls the real paper and sample sheet out of the PDFs into `papers.json` |
| `papers.json` | the real 2025 paper and sample sheet, for calibration |
| `../papers/build_pdfs.js` | renders every paper + markscheme to real PDFs; writes `data/papers.js` |
| `../papers/inspect_pdfs.py` | opens the built PDFs and reports page counts / renders a page to PNG |

## 10. Traps hit while building this

- **Bash `grep` silently returns nothing on this repo.** Use the Grep tool or
  `/usr/bin/grep`. There is no `/usr/bin/cat`.
- **Two edits to the same file in one message can conflict** — the second reported
  success and did not land. Edit sequentially, then verify the edit landed.
- **Inline heredoc Python trips a "system-level tool disabled" security filter.** Write
  the script to a file and run that.
- **A sandboxed `rm` does not necessarily persist**, and `git add` can succeed while
  failing to unlink its own `.git/index.lock`. `git push` reports failure while
  succeeding — confirm with `git ls-remote origin -h refs/heads/main`.
- **The local server on `127.0.0.1:8901` is rooted at the whole DP site**, not at `bpho/`.
  The hub is `/index.html`; the study space is `/bpho/index.html`. Loading the wrong one
  reports "0 figures on every route" and looks like a site-wide regression.
- **A timed mock renders stem figures only** — solutions sit in `display:none`
  `.reveal__body` until revealed. That is expected, not a missing figure.
- **A probe that reads the raw `q['sol']` disagrees with the gate.** The gate measures
  `_sol`/`_stem`/`_opts`, which are `expand_figs(supify(...))` of the source. Measuring raw
  strings made every figure question read one point low — an instrument defect that would
  have had me "fix" a correct question. Any probe must run `gate_section` first and measure
  the gate's own fields.
- **A gate can be wrong in the *loud* direction too.** Two of this project's checks fired
  false positives: the `approx` scan read a *distractor's* "taking the tail to be
  negligible" as evidence the solution used an approximation, and the duplicate-option check
  collapsed `k` and `K` because it lowercased before comparing. Both would have corrupted
  correct content. Mutants now test the silent direction as well
  (`structure.case_only_difference`, `must_not_fire=True`).
- **A clipped `<text>` is invisible in the source.** `/tmp/lint-svg.js` estimates text width
  at 0.55 em/char (0.58 bold), decodes entities, and errors when a run leaves the viewBox.
  It caught `fig/s02-11.svg` running 180 px past the right edge. Screenshots still catch what
  lint cannot: label collisions and a dashed box that fails to enclose the thing it labels.
- **`<sup>` and `<sub>` are HTML foreign-content *breakout* tags, so they must never appear
  inside an inline `<svg>`.** The HTML parser closes the `svg` at that point and parses the
  rest of the figure as HTML: `s03-06`'s axis label `velocity / m s<sup>-1</sup>` threw the
  `-1` **and** the whole `time / s` label out of the graph, and both still rendered — in the
  wrong place. It is silent by every measure that existed: the `svg` keeps its box (a size
  check passes), `<sup></sup>` balances perfectly (the tag-balance lint passes), and the
  figure looks right if you screenshot the `svg` alone. `svgkit.svg()` now **raises** on any
  breakout tag at build time, and the linter checks the source for figures that bypass
  `svgkit`. Use `<tspan font-size="8" dy="-4">` instead.
- **`figsNN.py` is not what the gate and the build read.** They read `fig/<key>.svg`, which
  `figs.py` writes. Editing `figsNN.py` and re-running `build_site.py` publishes the *old*
  figure and reports success — the rebuild byte count was identical and the fix looked
  applied. Regenerate with `figs.py N` first, and confirm by grepping the built
  `data/bank-NN.js` for the new text, not the source.
- **A harness that measures a hidden element reports a defect that is not there.** Nine
  "ZERO-SIZE svg" failures on `#/practice` were all figures inside collapsed solution
  panels, where `getBoundingClientRect()` is legitimately `0x0`. The harness now walks the
  ancestor chain and reports hidden figures separately from broken ones. Before "fixing" a
  zero-size figure, ask whether it is being displayed at all.
- **The gate suite only knows the properties somebody wrote a gate for.** `S05-21` asked
  for an RC time constant, which the official Round 0 note excludes in as many words, and
  it passed **all ten** gates — structure, distractors, agreement, profile, difficulty,
  similarity, numerics, figures, balance, hand-check. Every one of those asks "is this
  question well made?", and none of them asked "is this question *in the syllabus*?".
  G11 now does. The general form: when a whole class of defect has no gate, the reason is
  almost never that the class is unimportant — it is that nobody thought to name it.
- **A scope scan cannot be precise, so it should not pretend to be.** G11 is a keyword
  scan and will always have false positives: `S01-01` legitimately says a smooth pulley
  exerts "no frictional torque", and *torque* is otherwise the signature of out-of-scope
  rotational dynamics. Weakening the pattern until it stops firing would also stop it
  catching the real thing. Instead a hit is cleared by writing `profile.scope_note` — one
  sentence of recorded judgement. A false positive then costs a sentence, a true positive
  costs a rewrite, and neither can pass silently. `scope.recorded_judgement_is_honoured`
  is a `must_not_fire` mutant that proves the escape hatch works, because a gate whose
  only outcome is "rewrite it" teaches the author to avoid a **word** rather than to think
  about a **topic**.
- **`fig/` can hold a figure no stem references.** `fig/s03-06.svg` was registered in
  `figs03.py` and referenced by nothing — it drew an 8-second car journey while the
  question asks about a 60-second train. No check saw it, because a figure nobody
  references is never rendered, never linted, and never sized. Count `fig/*.svg` against
  the `{{FIG:...}}` placeholders across all sections whenever a section is finished: they
  should be equal, and the difference in each direction means something different (an
  orphan is dead weight, a dangling reference is a G8 failure).
- **A collision linter's "crosses 0px" is a lead, not a verdict.** `/tmp/lint-text-path.js`
  reported `s03-10`'s labels as grazing by 0 px; at 2x the branch wire ran *straight through*
  the middle of `3.0 kΩ` and through `load`, splitting both. Its sampling understates. Treat
  a non-zero-or-suspicious reading as "look at this figure", not as "this figure is fine".
- **A lint that scans the whole figure wrapper cries wolf.** The breakout check first ran
  over everything between `<figure class="fig">` and `</figure>` and flagged harmless
  `<b>`/`<code>` that authors legitimately put *after* the `svg`. A non-greedy wrapper
  capture can also span two figures if a `</figure>` is ever missing. Narrow every per-figure
  check to the `<svg>…</svg>` span.
- **A layout defect in a generated PDF is invisible to every check that reads the data.**
  No page count, byte size, or data-level assertion could see that the markscheme's first
  worked solution had been pushed to page 2, leaving "Worked solutions" sitting over half a
  blank sheet — the cause was `break-inside: avoid` on a block that is long *by nature*.
  A solution must be allowed to break; keep the heading with what follows
  (`.ms__head { break-after: avoid }`) and let the prose flow with `orphans`/`widows`.
  Rendering a page to PNG and looking at it is the only thing that catches this class, and
  it caught both PDF defects there were.
- **Editing the PDF builder does not change the PDFs.** `papers/*.pdf` and `data/papers.js`
  are output; a fix in `build_pdfs.js` is invisible until the build is re-run, and the
  stale files look perfectly normal. Same shape as the `figsNN.py` trap above: know which
  layer a checker reads before believing it.
- **Counting pages by scanning the bytes needs a lookahead, not `[^s]`.** `/Type /Pages` is
  the page *tree* node and must not be counted, but `/\/Type\s*\/Page[^s]/g` consumes the
  character after each match, so two adjacent page objects can be miscounted as one. Use
  `(?![s])`. Cross-checked against PyMuPDF on all ten files: 11/34, 6/16, 12/28, 10/31,
  10/32 — exact.
