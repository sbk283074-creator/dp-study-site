# Difficulty audit — the bank against the real 2025 paper

Written 2026-09-19, after the feedback that *"the difficulty is really low"*.

The complaint was right, but not for the reason the summary statistics suggest. Measured
against the real paper, the bank's **median question is already harder** than the paper's.
What the bank does not have is a **top end**. It is a flat bank: every question is medium.
The real paper is a peaked paper: fifteen quick questions, then one monster.

---

## 1. The measurement

All numbers below come from the bank's own scorer (`gates.difficulty`), run over the real
paper's 25 questions in `papers.json` and over the bank's 125 questions. Figure-bearing
stems are expanded through `gates.expand_figs` first, exactly as `gate_section` does — the
scorer reads the **rendered** stem, and a `{{FIG:key}}` placeholder is not an `<svg>`.

| set | n | median | p25 | p75 | min | **max** | moves med | **moves max** | deep (≥9) |
|---|---|---|---|---|---|---|---|---|---|
| **R0-2025 (real)** | 25 | 13.50 | 11.50 | 15.50 | 8.30 | **27.40** | **3** | **13** | **1** |
| R0-SAMPLE | 12 | 14.80 | 13.60 | 15.10 | 10.80 | 19.40 | 4 | 6 | 0 |
| bank sec 1 | 25 | 14.80 | 13.40 | 16.10 | 11.00 | 17.30 | 4 | 5 | 0 |
| bank sec 2 | 25 | 16.20 | 15.10 | 16.80 | 11.60 | 20.50 | 5 | 6 | 0 |
| bank sec 3 | 25 | 15.20 | 14.20 | 16.20 | 11.60 | 18.30 | 5 | 6 | 0 |
| bank sec 4 | 25 | 14.60 | 12.60 | 16.20 | 11.60 | 19.30 | 4 | 6 | 0 |
| bank sec 5 | 25 | 14.20 | 12.60 | 15.20 | 7.70 | 16.70 | 5 | 5 | 0 |
| **bank, all** | **125** | **15.20** | 13.20 | 16.20 | 7.70 | **20.50** | **5** | **6** | **0** |

### The shape, which is the whole finding

```
moves      1    2    3    4    5    6    7 ... 13
R0-2025    #    #### ###############  ###  #          #      <- 15 at three, one at THIRTEEN
BANK            ###  ##########(51)####(47)####(18)          <- nothing above six
```

The paper's median question is **3** moves; the bank's is **5**. So the bank's typical
question already does more work than the paper's typical question — which is why the
median (15.20 vs 13.50) looks healthy and why the gate suite has been passing.

The paper's hardest question is **13** moves. The bank's hardest is **6**. The bank has
**zero** questions at 7 or above. That is the entire gap.

---

## 2. Why it happened — depth was never a gate

The ten gates check that a question is *well-formed*: correct structure, plausible
distractors, a profile that agrees with its solution, a declared band that matches its
measured band, no duplicated logic, a hand-checked key. **Not one of them ever asked
whether a question was hard.** `spec.SECTIONS` fixes the topic mix; nothing fixed the
depth. A section of twenty-five well-formed three-move questions passed every gate.

The scorer did measure chain length — `moves` — but it was only ever used to derive the
declared band (`diff`), and the bands are the *paper's* quartiles. The top band starts at
15.5, which a six-move question reaches comfortably. So the metric could see the ceiling
and nobody asked it to.

---

## 3. Length is not depth — read the two hardest questions

This is the finding that a metric alone would have missed.

**The bank's hardest question, S02-05 (20.50, moves 6).** A conical pendulum. The stem is
three lines; the solution is 2 917 characters. But the physics is **one idea**: resolve the
tension into vertical and horizontal components, divide to eliminate `T`, read off ω. Every
one of the six "steps" is a line of the same calculation. It is a standard textbook
exercise — the kind that appears in every A-level textbook — written up at length.

**The real paper's hardest question, R0-25 (27.40, moves 13).** A 3 × 3 grid of twelve
resistors; you must find the **median** of five different equivalent resistances
(PR, PS, PU, QS, QT). That requires:

1. spot that each of the five pairs lies on a symmetry axis;
2. fold by the vertical mirror `M` for QT — five resistors become ½ Ω;
3. recognise the folded bridge as **balanced**, delete the dead link, and get QT = 1 Ω;
4. fold again for QS — and here the fold is *not* enough, so solve a two-node network
   by node equations to get QS = 7/12 Ω;
5. fold **antisymmetrically** for PR — axis nodes all at V/2, solve for 5/4 Ω;
6. fold along the **diagonal** `D` for PU — a different symmetry — giving 3/2 Ω;
7. fold by `D` again for PS, giving 7/8 Ω;
8. order all five **by cross-multiplication, never decimals** (the paper is
   non-calculator), and pick the middle one.

Five independent network reductions, each with its own symmetry and its own method, then a
selection. That is a genuinely long chain, and it cannot be shortened by writing better
prose. R0-25's solution is 5 012 characters — long, but it is long because the work is long.

**The contrast in one line:** the bank writes ~2 800 characters for every question
regardless of how many ideas it contains. The paper writes 2 800 characters for a
three-move question and 5 000 for a thirteen-move one. Measured across the bank,
`corr(score, solution length) = +0.33` — length barely varies. Across the paper it is
`+0.85`, because the hard question is also the long one. **Uniformly thorough writing
masked uniformly shallow questions.**

---

## 4. Two secondary findings

### 4a. The non-calculator axes are under-used

Round 0 is a **non-calculator** paper. The two terms in the scorer that specifically encode
non-calculator skill are `approx` (a required approximation) and `symbolic` (a symbolic
answer). The real paper leans on both far more than the bank does:

| | approximation required | symbolic answer |
|---|---|---|
| **R0-2025** | **10 / 25 = 40 %** | **10 / 25 = 40 %** |
| bank (125) | **11 / 125 = 9 %** | 30 / 125 = 24 % |

Ten of the paper's twenty-five questions require an approximation or a symbolic result.
The bank requires an approximation in one question in eleven. This is a real gap in what
the bank trains, independent of chain length — and it is cheap to fix, because
approximation and symbolic reasoning are exactly what a no-calculator paper should test.

> **Status after the fix: still open.** The rebuilt sections were rebuilt for *depth*, not
> for this axis, and the approximation rate has not moved. See section 6a for the
> measured position and what is now enforced for the remaining sections.

### 4b. Figure inflation flatters the bank's median

`fig` is worth +1.00. The bank has figures on **58 / 125 (46 %)** of its questions; the
real paper has figures on **6 / 25 (24 %)**. The bank therefore collects a bonus on nearly
half its questions that the paper collects on a quarter. Subtracting the figure term, the
bank's median is about 14.2 against the paper's 13.5 — a much narrower margin than the
headline 15.20 vs 13.50 suggests.

**Consequence for the fix: depth must not be bought with figures.** A deep question that
reaches its score through a diagram has not become harder; it has become better
illustrated.

---

## 5. The fix, and how it is enforced

The correction is to give the bank a **top end** and to stop the non-calculator axes from
being decorative. Both become gates, so that a flat section fails the suite rather than
waiting for a reader to notice.

| gate | rule | why |
|---|---|---|
| **G5b deep tier** | every section contains ≥ **2** questions with `moves ≥ 9`, and the section's maximum score is ≥ **22.0** | mirrors the paper's outlier; 22.0 cannot be reached without a genuinely long chain |
| **G5c non-calculator coverage** | per section, **two** clauses: ≥ `noncalc_min` questions require an approximation *or* carry a symbolic answer, and ≥ `approx_min` of them require an **approximation** | the union alone is satisfiable with symbolic options; sections 6–40 are held to the paper's own 16 and 10 out of 25, sections 1–5 to the 6 and 1 they already meet |
| **G4 deep profile** | a question marked deep must declare ≥ 9 steps with ≥ 4 distinct relations, and its solution must actually contain ≥ 9 `Step N` markers and ≥ 9 formula blocks | makes the length claim checkable line by line; prose cannot earn it |

The **hand-check ledger** is the backstop. Every question is hand-worked and the ledger
records the method, the working and the letter. For a deep question the ledger entry must
show nine or more distinct relations — a human reading, not a regex.

### Target shape for a finished section of 25

| tier | count | moves | score |
|---|---|---|---|
| quick | ~8 | 2–3 | 8–12 |
| standard | ~10 | 4–5 | 13–16 |
| hard | ~5 | 6–8 | 17–21 |
| **deep** | **≥ 2** | **9–13** | **22–27** |

and, on top of that shape, the non-calculator axes: **≥ 16** questions carrying an
approximation or a symbolic answer, of which **≥ 10** require the approximation itself.

This is deliberately **harder than the real paper** at the top: the paper carries one deep
question, the bank will carry two or more. That matches the brief — *"the same or even
harder than the BPhO"* — and it is the right call for a drill bank, where the point is to
meet the hardest thing repeatedly rather than once.

---

## 6. Outcome, measured after the fix

The top-end finding — a flat bank measured against a peaked paper — is **closed**. The
first correction was applied to sections 4 and 5, which were the two that had already been
published with a weak ceiling, and the whole bank was then re-measured:

| | median | max | longest chain | questions scoring > 22 |
|---|---|---|---|---|
| **R0-2025** | 13.50 | **27.40** | **13 moves** | **1** |
| sec 1 | 15.20 | 26.90 | 10 | 2 |
| sec 2 | 16.60 | 23.20 | 10 | 2 |
| sec 3 | 15.80 | 24.30 | 10 | 3 |
| sec 4 | 15.20 | 24.20 | 10 | 2 |
| sec 5 | 14.20 | 25.40 | 10 | 2 |

Before the fix the bank's hardest question scored **20.50 at six moves**, and there were
**zero** questions above six moves in 125. Every section now carries at least two questions
whose chain is ten moves long, each of them hand-worked in `ledger.json` with its relations
enumerated, and each of them gated by G5b so that a section cannot drift back to flat.

The four questions that bought the ceiling, and what each one costs the candidate:

| question | module | moves | score | what makes it long |
|---|---|---|---|---|
| `S04-04` | H | 10 | 24.2 | five resistors, reduced in three stages, asking for the current in the *innermost* branch |
| `S04-15` | B | 10 | 24.2 | a bouncing ball: each bounce halves only the vertical velocity, so the flight times form a geometric series |
| `S05-06` | C | 10 | 25.4 | ramp → rough floor → perfectly inelastic collision → slide again, four regimes chained |
| `S05-22` | J | 10 | 24.2 | 500 W warming ice, melting it, then warming the water — three latent/sensible stages |

### 6a. The non-calculator axes, which the fix did not close

Measured on the same scorer, bank-wide, after the fix:

| | approximation required | symbolic answer | either | figures |
|---|---|---|---|---|
| **R0-2025** | **10 / 25 = 40 %** | **10 / 25 = 40 %** | **16 / 25 = 64 %** | 6 / 25 = 24 % |
| bank after the fix (125) | 12 / 125 = 10 % | 31 / 125 = 25 % | 41 / 125 = 33 % | 59 / 125 = 47 % |
| per section (approx / either) | S01 6/12 · S02 2/8 · S03 1/6 · S04 1/8 · S05 2/7 | | | |

Finding 4a is **not** closed, and the honest reading is that the approximation rate did not
move at all — the four rebuilt questions were rebuilt for depth. Two consequences follow,
and they are different in kind:

* **The standard is now enforced for what is left.** The floors live on `spec.SECTIONS`
  (`noncalc_min`, `approx_min`) and G5c reads them, so sections 6–40 are held to the paper's
  own profile — **16 and 10 out of 25** — rather than to a number invented for them.
  Sections 1–5 are grandfathered at the floors they actually meet (6 and 1): rewriting 125
  published questions is a different piece of work from getting the next 875 right, and
  doing the second while the first is tracked is strictly better than doing neither.
* **Sections 1–5 are an open item, not an implication.** They sit at 6–12 and 1–2 against
  a target of 16 and 10. Closing that means revisiting roughly sixty questions; it is listed
  as an open item in `BANK-PLAN.md` section 8 rather than left to be inferred from a table.

The gate has **two** clauses on purpose. The union can be satisfied entirely with symbolic
options, so an author could give every answer as a formula and never once require an
approximation — which is close to the shape the bank already had (33 % union, 10 %
approximation). `approx_min` is the clause that stops the axis being met on paper, and the
mutant that proves it strips the approximations while deliberately *leaving* the symbolic
options intact, so that the union clause still passes and the approximation clause is the
one that speaks.

### 6b. What the new gates cost to prove

Every gate added in this round has a mutant that fires it, and three of them needed more
than one attempt because a mutant caught by a *neighbouring* clause has demonstrated
nothing. The failures are recorded in `mutants.py` beside the mutants rather than here, but
the pattern is worth stating once:

* **Ordering decides observability.** G5c is reported after the top-quartile check and the
  band check. The first version of `difficulty.no_noncalculator_axis` stripped twelve
  questions and was caught by the top-quartile check; the second kept their old `diff` and
  was caught by the band check. Only the third — six approximation carriers plus two
  symbolic ones, with every touched `diff` re-declared from a fresh measurement — produced
  a `G5c` message.
* **A mutation's arithmetic must be done on measured flags, not on intent.** The third
  version still reported `MISSED`, because `S01-09` carries *both* axes: removing its
  approximation text left it a symbolic carrier that still counted. The count was seven,
  one over the minimum, and the gate stayed correctly silent.
* **A snapshot has to span everything the mutant can affect.** Adding the per-section
  floors made it possible for a mutant to change the *standard*. The runner now snapshots
  and restores `spec.SECTIONS` around each mutant — and the first version of that snapshot
  was attached to the mutation alone, so the floor was put back before the gate read it and
  the mutant reported `MISSED` for a mutation nobody ever saw.

The suite is now **39 mutants**, and `mutants.py` asserts that all 39 behave: every gate has
been shown to fail on demand, and the one content-correct mutant
(`structure.case_only_difference`) has been shown to keep it quiet.

---

## 7. Reproducing this audit

```sh
cd bpho/tools/bank
python - <<'EOF'
import gates, json, io, copy, os
data = json.load(io.open('papers.json', encoding='utf-8'))
ref = [q for q in data['questions'] if q['paper'] == 'R0-2025']
def show(name, qs):
    sc = sorted(gates.difficulty(q) for q in qs)
    mv = [gates.features(q)['moves'] for q in qs]
    print('%-10s med=%.2f max=%.2f moves med=%d max=%d' %
          (name, gates.median(sc), max(sc), gates.median(mv), max(mv)))
show('R0-2025', ref)
for n in range(1, 6):
    qs = gates.load_section(n).QUESTIONS
    ex = []
    for q in qs:
        q = copy.deepcopy(q); e = []
        q['stem'] = gates.expand_figs(q['stem'], 'fig', set(), e)
        ex.append(q)
    show('sec%02d' % n, ex)
EOF
```

**The trap this avoids:** importing a section and scoring it directly reports every
figure-bearing question 1.00 too low, because the stem still holds `{{FIG:key}}`. The
first pass of this audit did exactly that and produced a section 4 median of 13.6 against
the gate's 14.6. Expand the figures first, or the numbers will not reconcile with
`gates.py`.
