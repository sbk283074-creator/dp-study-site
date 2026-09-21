# Depth audit — Python and C/C++ against a higher-level benchmark

Measured 2026-09-21. This answers one question: **is the content deep enough for a learner who is
going further than "can build things" — someone heading for university CS or serious engineering
work?**

Two things were measured, and neither is an impression:

1. **Structure** — every chapter's front matter, `##` headings, sub-heading count, Key takeaways
   count and Practice count, extracted from the 40 Python chapters and the 31 written C++ ones.
2. **Coverage** — a keyword sweep for the concepts a higher-level treatment must contain. A
   heading can promise depth a chapter does not deliver, so the sweep is the check on the claim.

The method has a known limit and it matters: **presence of a keyword is not depth, and absence is
much stronger evidence than presence.** So this audit only makes claims in the direction the
evidence supports. Every "absent" below is a zero count over the whole corpus, which is a fact.
Every "present" is a lead, not a verdict.

## The answer, up front

**The Python track is an excellent applied-engineering book and a weak theoretical one.** It is
not shallow — 4,310 words per chapter, 172,411 words, two 10,000-word capstones, and a genuine
arc from `print` to Docker. But it teaches *how to build* and almost never *why the machine
behaves the way it does* or *how to reason about cost*. Those are precisely the layers a
higher-level course adds, and they are missing.

The C++ track is deeper on systems and has the same two holes.

## The evidence

Keyword sweep over `code/python/chapters/` (40 files, 172k words). Counts are total occurrences.

| Concept a higher-level treatment must contain | Occurrences | Verdict |
|---|---|---|
| `Big-O` / `big-O` | **0** | **Absent** |
| `amortised` / `amortized` | **0** | **Absent** |
| `hash table` | **0** | **Absent** — `dict` is taught as a tool, never as a structure |
| `binary tree` / `heap` / `graph traversal` | **0** | **Absent** |
| `dynamic programming` | **0** | **Absent** |
| `metaclass` | **0** | **Absent** |
| `descriptor` | 3 | Named only |
| `__slots__` | **0** | **Absent** |
| `bytecode` / `dis.` | **0** | **Absent** — no CPython execution model |
| `reference count` / `garbage collect` | **0** | **Absent** — no memory model |
| `__getattr__` / `__getattribute__` | **0** | **Absent** |
| `Hypothesis` / `property-based` | **0** | **Absent** |
| `SSRF` / `path traversal` / `timing attack` / `supply chain` | **0** | **Absent** — no security layer |
| `SQL injection` | 1 | A single mention |
| `isolation level` | **0** | **Absent** |
| `complexity` | 2 | Named, never developed |
| `O(n` | 10 | Passim, in passing |
| `cProfile` / `profiling` | 11 / 5 | **Present** (ch11) |
| `GIL` | 15 | **Present** (ch21) |
| `closure` | 17 | **Present** (ch15) |
| `singledispatch` | 5 | **Present** (ch15) |
| `mock` / `flaky` | 8 / 18 | **Present** (ch11) |

The zero rows are not scattered gaps. They cluster into three absent layers:

**(1) There is no theory of cost.** Zero occurrences of Big-O, zero of amortised cost, zero of any
data structure that is not built in. `list`, `dict` and `set` are taught as convenient boxes with
no statement about what they cost, so a reader has no way to choose between them on anything but
habit. Chapter 35 implements A* for game AI — a genuinely good chapter — but A* is presented as a
game technique, not as an instance of graph search. The reader can use the algorithm and cannot
derive it, extend it, or recognise its cousins.

**(2) There is no interpreter.** Zero occurrences of bytecode, zero of reference counting or
garbage collection, zero of `__slots__`, zero of `__getattr__`, zero of metaclasses, and
`descriptor` appears three times without being explained. Chapter 12 teaches `@property`, chapter
13 teaches `dataclasses`, chapter 15 teaches `@classmethod` and decorators — and none of them says
that all four are the *same mechanism* (the descriptor protocol). So the reader learns five
features instead of one concept, and cannot write the sixth. This is the single largest depth gap:
it is the difference between knowing Python's API and knowing Python.

**(3) There is no security layer.** Chapter 18 says keep API keys out of git; chapter 27 hashes
passwords and issues tokens; chapter 28 mentions XSS and CSRF in a callout. That is good hygiene
taught in three places, not a security education. Zero occurrences of SSRF, path traversal, timing
attacks or supply chain. One mention of SQL injection — and chapter 19 *does* teach parameterised
queries correctly, so the reader is protected by imitation rather than by understanding. A learner
who goes on to write a service that accepts uploads, follows a URL, or deserialises data has been
given no framework for asking what can go wrong.

Two smaller holes: **no property-based testing** (ch11 stops at example-based pytest, so the reader
never meets the tool that finds the inputs they did not think of), and **no named architecture
vocabulary** (ch23 builds a layered CLI and ch33 a scene-stack game — both teach architecture by
example, neither names repository, unit of work, ports and adapters, or inversion of control, so
the reader cannot read or discuss an architecture they did not personally build).

## What the tracks get right, and should not lose

Worth stating, because an audit that only lists gaps invites cutting good material.

- **Python's applied depth beats most published books.** Chapter 20 (automation) runs 4,880 words;
  chapter 29 (deploy) covers health checks, request IDs, backups, rollback and a pre-launch
  checklist; chapter 19 covers the N+1 problem and Alembic. This is material people usually learn
  on the job, in a book.
- **Both tracks have a real project spine.** Python: TaskForge → StudyHub → Neon Dungeon. C++:
  `serve` → CAPSTONE A → CAPSTONE B. Theory chapters bolted onto a track with no project do not
  stick; these will.
- **Python's chapter structure is disciplined** — 8 takeaways, 5–6 exercises, and at least one
  `:::scenario`/`:::solution` per chapter, consistently across all 40. That uniformity is what
  makes a systematic expansion possible.
- **C++'s systems layer is genuinely deep** — memory layout (08), the link step (09), the
  preprocessor (15), UB and sanitizers (16), perfect forwarding (32). Python has no equivalent and
  should not try to grow one.

## The expansion plan

Both tracks get the same two new layers, sized to close the gaps above without diluting the
applied material. Full chapter lists are in each track's `OUTLINE.md`.

**Python: 40 → 63 chapters (+23).**

| New part | Chapters | Closes |
|---|---|---|
| VII · How Python Actually Works | 5 | The interpreter gap: bytecode, the object model, descriptors, metaclasses, memory |
| VIII · Algorithms & Complexity | 6 | The cost gap: complexity, core structures, sorting, graphs, DP, problem-solving method |
| IX · Security | 4 | The security gap: threat modelling, injection, untrusted data, web authz |
| X · Architecture & Patterns | 4 | The vocabulary gap: patterns, DI, hexagonal, refactoring |
| XI · Performance & Data at Scale | 3 | Caching, database depth, measurement |
| XII · Appendices | 1 | Version/packaging depth |

**C/C++: 60 → 67 chapters (+7).** Two new parts, because C++ already covers systems and
engineering:

| New part | Chapters | Closes |
|---|---|---|
| VIII · Algorithms & Complexity | 5 | The cost gap — and C++ is the right language for it: the reader can *measure* the constant factor and see the cache |
| IX · Security and Hardening | 2 | The security gap, in the language where it is a memory-safety problem first |

**Why these belong in a language book rather than a separate CS course.** The three gaps are not
neutral omissions — each one is a place where the existing material *stops just short of the
insight that would generalise it*. Chapter 35 has A*; one chapter of graph theory turns it from a
recipe into an application. Chapters 12/13/15 have `@property`, `dataclasses`, `@classmethod` and
decorators; one chapter of descriptors collapses five features into one idea. Chapter 19 has
parameterised queries; one chapter of injection turns a habit into a principle. Adding the layers
makes the existing chapters worth more, which is the argument for doing it inside the track.

## The standard this implies

The audit only covers two tracks. The remaining twelve languages need a bar to be built to, so the
criteria above are written down as `TRACK-STANDARD.md` — a `full` standard and a separate `mini`
one, since a compressed single-project track cannot carry six layers and should not pretend to.
`mini` tracks are explicitly held to a smaller bar rather than to a watered-down version of this
one.

## Method, so this can be re-run

- Structure: `parse_front` on the `---` block; `##` headings matched with `startswith("## ")` and
  not `"### "`; Key takeaways and Practice counted by their bullet prefixes inside the named
  section.
- Coverage: `grep -ric -- <term> chapters/` summed across files, over 40 Python chapters and 31
  C++ chapters. Multi-word terms are exact-substring, so `hash table` does not match `hash` or
  `table` separately; `O(n` is deliberately loose and is reported as passim rather than as
  evidence.
- C++ chapter counts and the written/planned split: `code/cpp/OUTLINE.md`.

**One caution, learned the hard way in this same session.** An earlier audit of this track
reported "70 transcripts fail" when the true number was 3, because the measuring harness was
buggy and a harness bug is indistinguishable from a content bug until you read a failure by hand.
The coverage counts above are `grep` over text, which has no such failure mode — but the
*interpretation* is still a judgement. A zero proves absence. A non-zero proves nothing except
that the word occurs, which is why every row above is labelled `Absent`, `Named only`, `Present`,
or `Passim` rather than graded.
