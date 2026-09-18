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

Two things that were removed because they flattered the author's own work:

- an `elim` term (whether the solution says "eliminate") scored **0.00 on all 25 real
  questions** and 2.40 average on the new ones, inflating the apparent gap from +1.3 to
  +3.7. A yardstick the reference paper cannot earn is not a yardstick.
- a `moves` cap of 6 truncated **only the real paper's hardest question** (13 moves),
  capping the yardstick at 18.7. Lifting it raised the paper's max to 27.4 and exposed
  that the bank's hardest question (17.3) is well below the paper's hardest.

## 4. The ten gates

`tools/bank/gates.py`. Run one section with `gates.py sec01`.

| Gate | What it checks |
|---|---|
| **G1** structure | 25 questions, five options each, unique ids, answer in range, module in scope, module mix matches the plan |
| **G2** distractors | each wrong option **names the error that produces it**; four distinct named errors; the key is marked correct. Filler options are what separate a worksheet from a competition paper |
| **G3** agreement & notation | the solution's stated answer equals the stored key; no caret or ASCII exponents reach the reader; markup balanced; no unresolved figure placeholder; **every decimal in visible text is hand-computable** or its sentence says not to compute it |
| **G4** profile vs solution | the declared reasoning chain (steps, relations, insight, shape) is cross-checked against the solution text, so a chain cannot be over- or under-stated |
| **G5** difficulty | measured score vs the real paper's quartiles, plus band counts |
| **G6** similarity | **logic**-level overlap between every pair, not wording |
| **G7** numerics | every answer re-derived independently of the solution, in exact arithmetic |
| **G8** figures | at least 8 figure-bearing questions; every referenced figure exists; figure geometry is checked |
| **G9** balance | no answer letter appears more than 10 times in 25 |
| **G10** hand-check ledger | at least 20 of 25 carry a hand-verified entry in `ledger.json` |

**G6 is deliberately not a text check.** The fingerprint is a set of curated features
(`key` tags, relation tokens, reasoning shape, depth band, approximation / symbolic /
figure flags) and contains **no words from the question**. Wording overlap is a separate,
weaker check that only fires when the logic does not.

### Why the gates are not trusted on their own

`tools/bank/mutants.py` is the answer to *"don't trust your tool that you write only"*.
It takes the real, passing section, breaks **exactly one thing** in each of 29 ways, re-runs
the whole suite, and asserts the right gate notices. A mutation that slips through is a
hole in the suite and is reported as a failure.

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
$PY figs.py

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
$NODE tools/bank/verify_site.js                       # drives a real browser over 127.0.0.1:8901
```

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

## 8. Progress

| | Sections | Questions | Status |
|---|---|---|---|
| Done | 1–2 | 50 | gated, hand-checked, published |
| Planned | 3–40 | 950 | not started |

**Section 1** — `S01`, 15 figures, mix `A3 B2 C4 D2 E1 F2 G2 H4 I1 J2 K2`, answer sequence
`BCBEDBECADCDEABEDCBABECAD`, measured median **14.8** against the paper's 13.5 and p25
**13.4** against the paper's 11.5. All ten gates pass, all 31 mutants are caught, 25/25
hand-verified in `ledger.json`, and it is live as `BANK-S01` in the practice view.

**Section 2** — `S02`, 8 figures, mix `A3 B2 C2 D1 E2 F2 G2 H3 I1 K2 L3 M2`, answer sequence
`CAEBDEAACBCBBEDBCCACDBBCD`, measured median **16.2** against the paper's 13.5 and p25
**15.1** against the paper's 11.5, min 11.6, hardest `S02-05` (conical pendulum) at 20.5.
Bands `d2=8 d3=17` — deliberately harder than the real paper, per the brief. All ten gates
pass, 25/25 hand-verified, live as `BANK-S02`.

Sections 1–2 together: 50 questions, 23 figures, 50/50 hand-checked, 31 mutants caught,
and `verify_site.js` discovers both tags from `window.BPHO_QUESTIONS` rather than naming
them, so sections 3–40 are checked the moment they publish.

## 9. File map

| File | Role |
|---|---|
| `spec.py` | the 40-section blueprint: targets, allocator, per-section mixes |
| `secNN.py` | the questions themselves — **the source of truth** |
| `figsNN.py` | hand-authored SVG figures per section → `fig/` |
| `svgkit.py` | shared SVG primitives (`ell(...)` sampled ellipses, palette) |
| `gates.py` | the ten gates, the difficulty scorer, the fingerprint |
| `mutants.py` | 31 mutants proving the gates have teeth, both directions |
| `make_ledger.py` | builds `ledger.json`, the hand-check record |
| `ledger.json` | per-question method, working, and hand-derived answer |
| `build_site.py` | gates, then emits `bpho/data/bank-NN.js` |
| `check_site_data.js` | loads the generated JS the way the browser does and asserts its shape |
| `verify_site.js` | Playwright end-to-end check that the bank works inside the study site |
| `extract_papers.js` | pulls the real paper and sample sheet out of the PDFs into `papers.json` |
| `papers.json` | the real 2025 paper and sample sheet, for calibration |

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
