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

The twelve gates check that a question is *well-formed*: correct structure, plausible
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
| sec 5 | 15.20 | 25.40 | 10 | 2 |
| sec 6 | 16.80 | 23.20 | 10 | 2 |
| sec 7 | 13.60 | 24.60 | 9 | 2 |

Before the fix the bank's hardest question scored **20.50 at six moves**, and there were
**zero** questions above six moves in 125. Every section now carries at least two questions
whose chain is nine moves or longer, each of them hand-worked in `ledger.json` with its
relations enumerated, and each of them gated by G5b so that a section cannot drift back to
flat.

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
| bank with section 6 (150) | 25 / 150 = 17 % | 39 / 150 = 26 % | 59 / 150 = 39 % | 73 / 150 = 49 % |
| bank with section 7 (175) | 36 / 175 = 21 % | 47 / 175 = 27 % | 77 / 175 = 44 % | 86 / 175 = 49 % |
| per section (approx / either) | S01 6/12 · S02 2/8 · S03 1/6 · S04 1/8 · S05 2/7 · **S06 13/18** · **S07 11/17** | | | |

Section 6 is the first section written *to* the new floors rather than grandfathered into
them, and it clears both: **13 approximations against a floor of 10**, and **18 by either
axis against a floor of 16**. It moves the bank-wide approximation rate from 10 % to 17 %,
still well under the paper's 40 % — the remaining gap is entirely sections 1–5. Section 7
holds the same standard at **11 and 17**, and its own finding (6e) is that meeting the
floor required measuring the *rendered* text rather than trusting the declared flags.

Finding 4a is **not** closed, and the honest reading is that the approximation rate did not
move at all — the four rebuilt questions were rebuilt for depth. Two consequences follow,
and they are different in kind:

* **The standard is now enforced for what is left.** The floors live on `spec.SECTIONS`
  (`noncalc_min`, `approx_min`) and G5c reads them, so sections 6–40 are held to the paper's
  own profile — **16 and 10 out of 25** — rather than to a number invented for them.
  Sections 1–5 are grandfathered at the floors they actually meet (6 and 1): rewriting 125
  published questions is a different piece of work from getting the next 825 right, and
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

The suite is now **51 mutants**, and `mutants.py` asserts that all 51 behave: every gate has
been shown to fail on demand, and the six content-correct mutants
(`structure.case_only_difference`, `numerics.symbolic_check_with_decimal`,
`scope.recorded_judgement_is_honoured`, `render.plain_unicode_is_fine`,
`notation.single_token_radical_is_fine`, `notation.numeric_root_is_fine`) have been shown to
keep it quiet.

The last two were added for a tool fix rather than a gate, and they are the clearest
example of why one mutant per change is not enough. `_equal` routed any expression
containing a float to its numeric path, where `N()` of an expression that still has free
symbols is not a number — so a *symbolic* check whose coefficient was written as a decimal
died with sympy's "Cannot convert expression to float", reporting a tool defect as an
authoring error. The fix substitutes a distinct prime for each free symbol and compares
numerically. `m40` writes the same quantity as a decimal and as a fraction and asserts the
gate stays **silent**; `m41` writes the decimal six per cent out and asserts it **fires**.
Without `m41`, `m40` would be satisfied by a branch that returned `True` unconditionally,
and the fix would have traded a false failure for a false pass.

### 6c. A fourth finding, made while building section 6

Sections 1–5 were repaired against this audit. Section 6 was the first built against it, and
building it turned up a defect the audit had not looked for — in the bank's *convention*
rather than in its content.

The real 2025 paper's solutions average **2.44 numbered steps**, maximum 5 (its mean `moves`
is 3.36, because five of its solutions number nothing and fall back on their formula count).
Section 6's averaged **5.48 numbered steps**, maximum 10 — while carrying *fewer* formulas
per question (4.00 against 5.04) and the same number of relations (2.00 against 1.96). Since
`moves` is the dominant term in the scorer, that one difference accounted for the whole of
section 6's excess median, and it made the section read **uniformly** harder than the paper
instead of peaked like it: 21 of its 25 questions sat above the paper's p75, where the paper
has 6.

The cause was a habit, not a mistake in any single question: 19 of the 25 solutions ended
with a numbered verification — "Step 5 — check the size", "Step 6 — check the direction".
A sanity check does not obtain the answer. Demoting those steps to unnumbered prose, keeping
every word, moved the section to **15 of 25** above p75 and its easiest question from 10.0
to **8.4**, against the paper's own 8.3.

| | paper 2025 | section 6 before | section 6 after |
|---|---|---|---|
| mean `moves` | 3.36 | 5.48 | 4.72 |
| mean numbered steps | 2.44 | 5.48 | 4.72 |
| max numbered steps | 5 | 10 | 10 |
| mean formulas per question | 5.04 | 4.00 | 4.00 |
| questions above p75 | 6 | 21 | 15 |
| easiest question | 8.3 | 10.0 | 8.4 |

The general lesson is uncomfortable and worth writing down: **a scorer that counts numbered
steps can be satisfied by numbering more of them.** The audit's own instrument was
gameable by presentation, and nothing in the twelve gates could have caught it, because every
gate agreed with every other gate. What caught it was reading the paper's solutions beside
the bank's and comparing the *granularity* of the numbering — which is a judgement, not a
check, and is why G10's hand ledger and this document both exist.

---

## 6d. A fifth finding: a question that was hard, well-made, and out of syllabus

Not a difficulty finding, but it belongs here, because it is the same lesson from a
different direction: **the gate suite only knows the properties somebody wrote a gate
for.**

`S05-21` asked for the time constant of an RC charging circuit. The official Round 0
scope note is one sentence long and says capacitors mean *"not time dependent charging,
but a knowledge that Q = CV"* — an exclusion as explicit as a syllabus ever gets. The
question passed **all ten** gates. Structure, distractors, agreement, profile, measured
difficulty, logic similarity, independent numerics, figure geometry, letter balance and
the hand-check ledger all agreed it was a good question, and they were all right: it was
well made. It was simply about something the paper will never ask.

Every gate asks *"is this question well made?"*. None of them asked *"is this question
in the syllabus?"*, so a whole class of defect had no gate — not because the class was
unimportant, but because nobody had named it.

**The fix is two things.**

1. **G11, a scope gate.** A short list of phrases that can occur in an out-of-scope
   question and almost nowhere else (RC charging, SHM, electric / magnetic /
   gravitational fields, particle physics, rotational dynamics, reactor detail, QM
   beyond the photoelectric effect), scanned over every field a candidate reads.

2. **A recorded judgement instead of a silent pass.** A keyword scan cannot be precise.
   `S01-01` legitimately says a smooth pulley exerts "no frictional torque", and
   *torque* is otherwise the signature of out-of-scope rotational dynamics. Tightening
   the pattern until it stops firing would also stop it catching the real thing, so a
   hit is cleared by writing `profile.scope_note` — one sentence saying why the question
   is in scope anyway. `scope.recorded_judgement_is_honoured` is a `must_not_fire`
   mutant proving the hatch works, because a gate whose only outcome is "rewrite it"
   teaches the author to avoid a **word** rather than to think about a **topic**.

**The replacement.** `S05-21` is now a series-parallel capacitor network — two
capacitors in parallel, that pair in series with a third, across 12 V, and the question
is the p.d. across the single one. It is inside `Q = CV`, it scores 16.2 (band 3), and
it is a *better* question than the one it replaced: it is the only capacitor question in
the bank whose answer depends on **reading a topology** before any arithmetic starts.
The parallel pair adds, the series link does not, and the two rules pull in opposite
directions — which is exactly the kind of discriminator a multiple-choice paper can
test and a calculator cannot help with.

**The general form, worth carrying forward:** when a whole class of defect has no gate,
the reason is almost never that the class is unimportant. It is that nobody thought to
name it. Section 5's defect was found by asking a question the suite had never been
asked — *what is this paper allowed to test?* — and reading the answer off the official
note rather than off the bank.

---

## 6e. A sixth finding: the profile is a claim, the measurement is the fact

Building section 7 turned up a *measurement* subtlety that no gate had had to expose
before, because sections 6's numbers happened to agree with its declarations.

`difficulty()` scores `approx` and `symbolic` from **the rendered text** — what a
candidate sees — and not from the `profile` flags. The two can disagree, and when they do
the profile is the one that is wrong. Section 7's author declared **four** questions as
needing an approximation. Measured, the number was **six**, against a floor of ten.

The flags were not dishonest. Each of the four did need one. But six other questions also
used one — an order-of-magnitude estimate, a small-change expansion — without the author
noticing, because the flag was being written from memory of the *plan* rather than read
back off the *solution*. That is the same failure as the orphan figure and the
drawn-but-unlabelled angle: the artefact and the description of the artefact had drifted,
and only one of them is what the candidate meets.

**The consequence for how a section is written.** `measure.py` exists precisely so the
author can see the gate's numbers before the gate does, and the lesson of section 7 is to
use it *while* writing rather than after. The section was then rebuilt to the axis: 17 of
25 non-calculator and 11 requiring an approximation, against floors of 16 and 10, with
each approximation a real one — a small-change expansion, an order-of-magnitude estimate,
an interpolated graph reading, a gauge-offset argument. Section 7 measures median 13.6
against the paper's 13.5, p25 12.6 against 11.5, min 11.0, max 24.6 at nine moves.

**And a first: a recorded scope judgement nobody asked for.** G11 was built so that a
crude scan could be cleared by a written reason. `S07-19` — what fraction of a battery's
supplied energy is lost in the resistor while a capacitor charges — trips no marker, so
no judgement was demanded. It got one anyway, because it is a *charging* question and
"time dependent charging" is a phrase the official note uses. The exclusion is about the
time behaviour; the question is built so that `R` cancels and the trap is exactly the
candidate who looks for it. Writing the note costs a sentence and means the decision is
auditable; not writing it would have left a borderline call invisible, which is the state
`S05-21` shipped in. **A recorded judgement is worth having even when the gate is
silent** — the gate exists to force the *hard* cases into writing, not to define which
cases deserve thought.

---

## 6f. A seventh finding: text that could not be read

This one was not a difficulty finding and was not found by a check. It was found by
**looking at a screenshot of a figure** while verifying section 7 — and it had been live
on the site for four sections.

`assets/app.js` inserts most question fields as HTML (`q.q`, `opts`, `sol`, `trap`) but
**escapes two author-written ones**: `topic` and every `rel[i][1]` label. It has to
escape the label, because `data/priority.js` reuses it as a topic *name* and the topics
page escapes it there as well — so it cannot be HTML in either place.

Nineteen labels across sections 4, 6 and 7 had been written as HTML anyway. On the page
they read:

```
The maximum height of a projectile is u<sup>2</sup> sin<sup>2</sup>&#952; / 2g
```

— tags, entity and all, exactly as typed. A candidate sees that on the question page and,
as a topic name, on the topics page. Every gate passed them. The labels were well
written; they simply could not be read.

**The fix is the data, not the renderer.** Rendering `rel[1]` as HTML would fix the
question page and leave the topics page broken, so the labels were rewritten in plain
Unicode — `u² sin²θ / 2g` — which is the convention sections 1–3 and 5 had used all
along ("Energy stored in a spring is half the stiffness times the square of the
extension"). The whole site already writes `²`, `½`, `θ`, `√` and `≈` as characters.

**And a gate, G12.** In a field that will be escaped, `<`, `>` and `&` have no legitimate
use, so the check is deliberately blunt: markup in an escaped field fails. Two mutants
pin it — `render.markup_in_a_rel_label` must fire, and `render.plain_unicode_is_fine`
must stay **silent**, because a gate that fired on every non-ASCII character would forbid
the site's own typography. **The suite is 51 mutants.**

G12 earned its place again a day later. A mechanical sweep of the notation across all seven
sections rewrote the root symbol to its numeric reference everywhere — right for every
field the page injects as HTML, and wrong for `S07-12`'s first `rel` label, which is
escaped, so the candidate would have read `&#8730;(γP/ρ)` verbatim. G12 reported it inside
a minute. The full sweep is in **`NOTATION-AUDIT.md`**, and its §5 is the same lesson a
third time: the corpus runs **two** notation policies because it has **two** renderers, and
a find-and-replace that does not know which field it is in will always be wrong in one of
them.

The lesson is G11's lesson a second time, with a twist. G11 existed because a whole class
of defect — "is it in the syllabus?" — had no gate. G12 existed because a class of defect
had no gate for a reason nobody would have guessed: it was not about the *physics* at
all, but about **which of two renderers a field happens to pass through**. A question can
be correct, hard, original, in scope and beautifully written, and still be unreadable,
because the string it is written in is going to be escaped.

**The general form:** when a screenshot shows something a check cannot, that is not a gap
in the checks. It is evidence that the property being checked and the property that
matters are different properties.

---

## 7. Reproducing this audit

```sh
cd bpho/tools/bank
python measure.py paper     # the real 2025 paper, question by question
python measure.py all       # every section, summary
python measure.py 6         # one section, per-question breakdown
python gates.py all         # the twelve gates
python mutants.py           # proof the gates have teeth
```

`measure.py` exists because getting this measurement right is not obvious, and the two ways
to get it wrong are both silent:

* **The figure directory must be absolute** (`gates.HERE/fig`, not `"fig"`). A relative path
  resolves only if the working directory happens to be `tools/bank`; when it does not,
  `expand_figs` returns `<!-- MISSING FIGURE ... -->` rather than raising, every
  figure-bearing question loses its `fig` term, and the scores come out **1.00 too low**.
  That cost an hour in the section-6 session: six questions appeared to disagree with the
  gate by exactly 1.0 and the discrepancy looked like a scorer bug rather than a path bug.
* **The text must be `supify`-ed before scoring.** The `symbolic` flag and the formula count
  both read rendered text, so a helper that scores the raw source disagrees with the gate it
  is supposed to be checking.

The first pass of this audit made the first mistake, which is why it originally reported a
section 4 median of 13.6 against the gate's 14.6. If your numbers do not reconcile with
`gates.py`, check the path before you check the scorer.
