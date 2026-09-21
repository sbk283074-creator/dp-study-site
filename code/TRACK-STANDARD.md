# The CODE track standard

Normative. Every language track in this platform is built to one of two bars: **`full`** or
**`mini`**. The bar is declared per language in `_build/languages.json` (`"kind": "full" | "mini"`)
and enforced by `_build/check-standard.py`.

The two bars are **different bars, not the same bar watered down.** A `mini` track is not a `full`
track with chapters missing; it is a different, deliberately bounded product — teach one language
to working competence, in one project, without the theory and architecture layers. It is never
graded against the `full` criteria.

This document exists because `DEPTH-AUDIT.md` measured two tracks that were *long* and *deep in
places* and still missing whole layers. Length was never the problem. Presence of the layers is.

---

## Part 1 · The `full` standard

### 1.1 Size

| Criterion | Requirement |
|---|---|
| Chapters | **55–70** (ch00–chNN, contiguous, no gaps) |
| Projects | **≥ 3** — one mid-book standalone project, plus two capstones |
| Capstones | **2**, each ≥ 8,000 words, each a complete buildable artifact |
| Median words per chapter | **≥ 2,400** |
| Teaching chapters below 1,500 words | **0** |

Length is a floor, not the goal — but a chapter under 1,500 words is a stub, not a lesson. The
floor does not apply to ch00, which has no topic to teach.

### 1.2 The six layers — the actual depth test

A `full` track must contain all six. This is the criterion the audit was really about: a track can
be 60 chapters of pure application and fail this.

| # | Layer | Minimum | What it is |
|---|---|---|---|
| 1 | **Language core + applied engineering** | — | The spine: syntax → idioms → real projects |
| 2 | **Internals** | **≥ 3 chapters** | How the runtime actually executes your code. Bytecode / VM / JIT / the link model / the object model / memory management. *The layer that turns API knowledge into language knowledge.* |
| 3 | **Cost theory** | **≥ 4 chapters** | Complexity, core data structures, sorting and searching, graphs, recursion/DP. *The layer that lets a reader choose on evidence rather than habit.* |
| 4 | **Security** | **≥ 2 chapters** | Threat modelling, injection, untrusted data, plus whatever the platform makes dangerous (web: XSS/CSRF/SSRF; systems: memory safety). |
| 5 | **Architecture** | **≥ 2 chapters** | Named patterns, dependency injection, boundaries (ports and adapters), and refactoring. *The layer that lets a reader discuss a codebase they did not write.* |
| 6 | **Performance & scale** | **≥ 2 chapters** | Measurement first, then caching and data-layer depth. |

Layers 2–6 are located by **part title** in the track's `OUTLINE.md`. A track that teaches
descriptors inside a chapter called "OOP II" does not satisfy layer 2 — the layer is a *part*, so
that a reader can find it and so that the outline states the intent.

### 1.3 Per-chapter depth

A book has four kinds of chapter, and grading all of them on the lesson template measures the
wrong artifact. The checker assigns a **role** and applies the matching template.

| Role | Assigned by | Graded on |
|---|---|---|
| `teaching` | default | the full template below |
| `project` | title matches `CAPSTONE` or `PROJECT:` | front matter, takeaways, **`## Milestone checklist`**, verified block, callouts closed. *Not* exercises — a build has milestones. |
| `appendix` | part title matches `Appendices` / `Where Next` | front matter, takeaways, verified block, callouts closed. Scenario and pitfall are lesson devices and do not apply to reference material. |
| `orientation` | part title matches `Start Here` (ch00) | front matter, takeaways, verified block, callouts closed. There is no topic to teach, so there is no lesson template to satisfy. |

The `teaching` template:

| Criterion | Requirement |
|---|---|
| Front matter | `chapter`, `part`, `title`, `summary`, `minutes`, `tags` — all present |
| `## Key takeaways` | **≥ 6** bullets |
| `## Practice` | **≥ 4** exercises |
| `## Solutions` | one `:::solution` per exercise |
| `:::scenario` + `:::solution` | **≥ 1** pair |
| Pitfall-family callout | **≥ 1** `:::pitfall`, `:::danger` or `:::warning` |
| Verified code | **≥ 1** block carrying a directive |
| Callouts | every opener has a closing marker somewhere after it |

The pitfall criterion accepts all three kinds because the house convention gives the strongest
mistakes `danger`. The criterion is "at least one callout naming a real mistake", not "the word
`pitfall` appears".

**Calibrated, not aspirational.** Run against the 77 chapters that already exist (40 Python, 33
C++, 4 Java), this template reports **0 false positives** — every criterion it flags is a real
gap. Getting there required five corrections, each of which was the criterion being wrong rather
than the content:

1. the word floor does not apply to ch00, and it belongs at 1,500 rather than 1,800 (a setup
   chapter at 1,758 words is covering its topic);
2. project chapters carry a Milestone checklist, not exercises;
3. appendix chapters (`Appendices`, `Where Next`) are reference material with no lesson devices;
4. orientation (ch00) has no topic to teach, so it is held only to front matter, takeaways and a
   verified block;
5. pitfall-family callouts count — the house convention gives the strongest mistakes `danger`.

A standard that flags conforming work trains people to ignore it, so every one of these was
resolved by fixing the criterion rather than the chapter. The only content change the calibration
forced was genuine: Python ch09 had no pitfall-family callout at all — it turned out to have one
under `:::danger`, so the criterion was wrong — while ch00 gained a sixth takeaway and a real
pitfall about resource-collecting, which is the failure mode that ends most self-taught attempts.

### 1.4 Verification

Not optional, and not satisfied by a harness that merely exists.

| Criterion | Requirement |
|---|---|
| Harness | `tools/verify_examples.py` present |
| Self-test | `--self-test` **PASSES**, with a `must_fail` fixture for every claimed check |
| Directive contract | `STYLE.md` documents every directive the harness honours |
| Failures | **0** across the whole track |
| Coverage | **every chapter** has ≥ 1 verified block |
| `text` fences | every attached `text` fence is a checked claim, not prose |

The self-test requirement is the load-bearing one. `DEPTH-AUDIT.md` records a case in this very
repo where a harness reported 70 failures and the truth was 3, because the harness was buggy. A
gate that cannot fail, or that has never been shown to fail, is not evidence.

### 1.5 Build

| Criterion | Requirement |
|---|---|
| Builds | `python3 _build/build.py <id>` succeeds |
| Idempotent | `_build/check-idempotent.sh` reports no change on a second build |
| Self-contained | the built book opens over `file://` with no network |

---

## Part 2 · The `mini` standard

A `mini` track is a **different product**: get a working developer of one language, through one
real project, in a compressed format. It is graded only against this section.

| Criterion | Requirement |
|---|---|
| Chapters | **12–22** |
| Projects | **exactly 1**, and it is a capstone (≥ 4,000 words) |
| Median words per chapter | **≥ 1,800** |
| Per-chapter depth | ≥ 4 Key takeaways · ≥ 3 exercises with solutions · ≥ 1 `:::pitfall` |
| Layers required | **1 (core), 6-lite (one performance chapter), and 4-lite (one security chapter)** |
| Layers explicitly **not** required | Internals, cost theory, architecture. Omitting them is the point of the format. |
| Verification | Same as `full`: harness, passing self-test, 0 failures, every chapter ≥ 1 verified block |

The `mini` bar is *stricter per chapter* than `full` on one axis: a `mini` chapter has less room to
be vague, so the exercise and pitfall minima are enforced at a higher rate relative to length.

A `mini` track must state its scope limit in `ch00` — what it deliberately does not cover — so the
omission is a decision rather than an oversight.

---

## Part 3 · Conformance

`_build/check-standard.py` measures each track against its declared `kind` and prints a per-criterion
verdict. Run it before a track is marked `live` in `languages.json`, and after any batch of chapter
work.

```sh
python3 _build/check-standard.py              # every track with a chapters/ dir
python3 _build/check-standard.py python cpp   # just these
python3 _build/check-standard.py --self-test  # prove the checker can fail
```

The checker is a gate, so it carries its own self-test and its own fixtures — a criterion it cannot
fail is not a criterion.

### Current conformance, 2026-09-21

Produced by `_build/check-standard.py --no-verify`. Every failure below is a real gap.

| Track | Kind | Chapters | Unmet | Verdict |
|---|---|---|---|---|
| `python` | full | 50 / 63 | 6 | **FAIL** — chapters 49–61 unwritten; 28 chapters still have no verified block; layers 4 (security), 5 (architecture), 6 (performance) absent |
| `cpp` | full | 35 / 67 | 9 | **FAIL** — chapters 31–33 unwritten; 0 capstones (45, 54 unwritten); 1 project of 3; layers 2–6 absent |
| `java` | full | 4 / 40 | 9 | **FAIL** — early build-out; median 2,306 words is under the 2,400 floor; layers absent |
| the other 11 | mixed | 0 | — | **not started** — build to this standard, not to a copy of Python |

What the checker *passes* is worth stating too, because it shows the existing tracks are not
broken: Python's median chapter is 3,917 words and C++'s is 4,211 (floor 2,400); Python has its
2 capstones and 3 projects; **every C++ chapter passes the per-chapter template**; and C++ has no
stub chapters. Python's remaining 28 per-chapter issues are all the same one — a chapter with no
verified block yet, which the harness build-out is clearing.

No track is conformant today. That is the honest state and the reason the standard exists: it
converts "is it deep enough?" from an opinion into a list of things to build.
