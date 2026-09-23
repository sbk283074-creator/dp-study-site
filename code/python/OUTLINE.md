# Python Mastery — the chapter outline

> **63 chapters (ch00–62).** ✅ = written and machine-verified · ★ = to write.
>
> Chapters 00–38 keep their numbers, so **no written chapter moves**. The 23 new chapters are
> inserted as Parts VII–XI and `39 What to Learn Next` becomes `62`, so the book still ends with it.
>
> The additions are the three layers `DEPTH-AUDIT.md` found missing: **how the interpreter works**
> (Part VII), **a theory of cost** (Part VIII), and **security** (Part IX), plus the architecture
> vocabulary and the performance/data material that a learner going further than "can build things"
> needs. They are placed *after* the applied tracks on purpose: by then the reader has used
> `@property`, `dataclasses`, `@classmethod` and A*, so Part VII can show that four things they
> already know are one mechanism, and Part VIII can show that a game technique is graph search.

## Part 0 · Start Here — 00 (1)

- ✅ 00 How to Use This Book

## Part I · Foundations — 01–07 (7)

- ✅ 01 Setting Up Your Python Workbench
- ✅ 02 Variables, Types & Expressions
- ✅ 03 Strings & Formatting
- ✅ 04 Control Flow
- ✅ 05 Functions
- ✅ 06 Lists, Tuples, Dicts & Sets
- ✅ 07 Loops, Comprehensions & Iteration Patterns

## Part II · Leveling Up — 08–17 (10)

- ✅ 08 Files, Paths & Persistence
- ✅ 09 Errors, Exceptions & Defensive Programming
- ✅ 10 Modules, Packages & Virtual Environments
- ✅ 11 Testing & Debugging
- ✅ 12 OOP I: Classes & Objects
- ✅ 13 OOP II: Inheritance, Composition & Dataclasses
- ✅ 14 Iterators, Generators & Context Managers
- ✅ 15 Decorators & Closures
- ✅ 16 Type Hints & Static Analysis
- ✅ 17 Regex, Dates & Numbers

## Part III · Real-World Python — 18–23 (6)

- ✅ 18 Talking to the World: HTTP, JSON & APIs
- ✅ 19 Working with Data: CSV, SQLite & SQLAlchemy
- ✅ 20 Automation & CLI Tools
- ✅ 21 Concurrency: Threads, Processes & async/await
- ✅ 22 Git, Code Quality & Packaging
- ✅ 23 **PROJECT: TaskForge** — a real CLI application

## Part IV · Track A · Full-Stack Web — 24–30 (7)

- ✅ 24 How the Web Works
- ✅ 25 HTML, CSS & JS for Python Developers
- ✅ 26 FastAPI I: Routing, Validation & Responses
- ✅ 27 FastAPI II: Database, Auth & Testing
- ✅ 28 Templates, HTMX & Real-Time
- ✅ 29 Deploy: Docker, CI & the Cloud
- ✅ 30 **CAPSTONE A: StudyHub** — a full-stack application

## Part V · Track B · Game Development — 31–36 (6)

- ✅ 31 Pygame I: Window, Game Loop & Drawing
- ✅ 32 Pygame II: Sprites, Input & Collisions
- ✅ 33 Game Architecture
- ✅ 34 Worlds: Tilemaps, Cameras & Procedural Generation
- ✅ 35 AI, Pathfinding & Enemy Behavior
- ✅ 36 Polish, Packaging & **CAPSTONE B** — Neon Dungeon

## Part VI · Appendices — 37–38 (2)

- ✅ 37 Real-World Scenarios & Solutions
- ✅ 38 Practice Problem Bank

## Part VII · How Python Actually Works — 39–43 (5) ★

> Placed here deliberately. Every chapter in this part takes features the reader has already used
> — `@property`, `dataclasses`, `@classmethod`, decorators, `__slots__`-free classes — and shows
> the single mechanism underneath them.

- ★ 39 From Source to Bytecode — *what actually runs when you press Enter: the AST, `compile()`,
  the `dis` module, the evaluation loop, `__pycache__`, and why `locals()` is slower than a dict*
- ★ 40 The Object Model — *every value is an object with identity, type and value: `__new__` vs
  `__init__`, the `__eq__`/`__hash__` contract, `__repr__`, `__bool__`, and the immutable/mutable
  split that everything else depends on*
- ★ 41 Memory: Reference Counting and the Cycle Collector — *`sys.getrefcount`, cycles and why they
  need a collector, `__slots__`, string interning, `weakref`, and what a leak looks like in Python*
- ★ 42 Descriptors — *the one mechanism behind bound methods, `@property`, `@classmethod`,
  `@staticmethod` and `functools.cached_property`; write your own and watch four features collapse*
- ★ 43 Metaclasses and Class Creation — *`type()` as a callable, `__init_subclass__`,
  `__set_name__`, `__prepare__`, a real metaclass (a registry and a validator), and the point at
  which the right answer is "do not"*

## Part VIII · Algorithms & Complexity — 44–49 (6) ✅

> Chapter 35 already implements A*. This part is what makes it possible to see that A* is graph
> search, and to choose a data structure on evidence rather than habit.

- ✅ 44 Complexity and the Cost Model — *Big-O, Θ and Ω, growth rates, amortised cost, the real
  constant factors of Python operations measured with `timeit`, and the difference between a
  benchmark and a guess*
- ✅ 45 Core Data Structures — *dynamic arrays, linked lists, stacks, queues and `deque`, a hash
  table written by hand to see why `dict` is O(1), heaps and `heapq`, balanced trees vs `bisect`
  vs sorted list, tries; each one chosen for a stated cost*
- ✅ 46 Sorting and Searching — *comparison sorts, why `sorted` is Timsort and stable, `key=` vs
  `cmp_to_key`, binary search and its off-by-one, `bisect` for insertion and rank*
- ✅ 47 Graphs — *adjacency list vs matrix, BFS, DFS, topological sort and cycle detection,
  Dijkstra with a heap, and A\* (Chapter 35) as Dijkstra plus a heuristic*
- ✅ 48 Recursion, Memoisation and Dynamic Programming — *the recursion tree, overlapping
  subproblems, `functools.lru_cache`, top-down vs bottom-up, edit distance, LCS, knapsack and
  pseudo-polynomial time, coin change, rolling rows, and the recursion limit as a design constraint*
- ✅ 49 A Method for Unseen Problems — *a repeatable procedure for a problem you have never seen:
  read the constraints as a complexity budget, pick the structure the budget allows, then prove the
  complexity by counting; worked end to end on one problem three ways (where the answer is unique but
  the witness is not), on fitting an exponent to timings, on the problems where the answer is "sort it
  first", the ones where a set is not enough, the sweep that is wrong rather than slow, and the ones
  where the budget says meet in the middle*

## Part IX · Security — 50–53 (4) ✅

> Chapters 18, 19, 27 and 28 already do the right things. This part is the framework that turns
> those habits into principles the reader can apply to code nobody has written yet.

- ✅ 50 Thinking Like an Attacker — *five counts and two assumptions: inventory the assets and the four
  controls over each, count trust boundaries rather than components, count inputs rather than
  endpoints, run STRIDE for completeness and see why it cannot rank, and hold the book against the
  OWASP Top Ten; then test the two assumptions every design quietly makes -- that "internal" means
  unreachable (nine of thirteen components were reachable before the SSRF existed) and that two
  defences multiply (independence predicted 4.6 inputs through, 14 got through)*
- ✅ 51 Injection — *the one mechanism behind six different bug classes: a value arrives where
  something parses it, and the parser cannot tell the value from the syntax it stands in. Why
  parameterised queries work at the protocol level (28 rows interpolated against 1 bound, and the one
  is the real name), and the slot where binding is not an option at all (`ORDER BY ?` sorts by a
  constant — the allow-list delivers all four orderings and accepts zero hostile values); command
  injection where the position decides rather than the payload (the same eight payloads run zero times
  in `argv[1]` and eight times in `argv[0]`, and `['sh','-c',f-string]` with `shell=False` runs all
  eight); template injection, where field access is enough (`{0.secret}` contains no call, no import
  and no name); `eval` against `ast.literal_eval` against a filter that ran 3 of 8 code strings;
  path traversal and the rule that the value you check must be the value you use (33.3% → 88.9% →
  100% as the check moves to the fixed point); eight sinks against seven encoders, where three of the
  six encoders that change anything make a sink **worse** than doing nothing; a blocklist scored
  against 7,680 generated strings; and log forging, where 24 of 84 lines are requests nobody made*
- ✅ 52 Untrusted Data — *the other half of injection: a value that is not parsed as syntax in a
  statement but reconstructed as an object, a path, a tree or a length. `pickle` as a program rather
  than a description (`__reduce__` returns a callable and its arguments — six payloads, six stdlib
  functions, six calls, and the stream needs no class of yours), the four operations that run it
  (`dumps`, `loads`, `copy.copy`, `copy.deepcopy`), and why JSON and `marshal` are not "safer pickle"
  but formats that cannot express the object; XML entity expansion measured at a factor of ten per
  line (125 bytes → 30 characters, 573 bytes → 3 billion); zip slip, where `zipfile` sanitises 0 of 6
  members and tarfile instead offers each member to a filter that refuses 0, 3 or 4 of 7 depending on
  which you name; schema validation as a boundary (presence alone accepted 7 hostile bodies of 12, and
  `True` is an `int` so only `type(x) is t` catches it); the allow-list that resolves the four types
  the application has where `getattr(builtins, ...)` resolves none of those and all three dangerous
  ones; and message framing, where trusting a declared length got 2 of 7 messages right before the
  reader died and misattributed every byte after it. Two blocks are about checks that measure the
  wrong quantity — a 4096-byte upload limit that passes all six documents while three of them expand
  past a hundred million characters. **`yaml.load` and `defusedxml` are not covered: PyYAML and
  defusedxml are not installed, and this track is stdlib-only.***
- ✅ 53 Web Security — *the same two mechanisms in the one place where you hold neither end: a
  browser, a session, and a set of services you did not write. Four rendering contexts against one
  escaper (8 of 24 renders broken raw, 2 of 24 after `html.escape`, and both survivors are the
  unquoted-attribute context, where the payload needs a space and a space is not one of the four
  characters an HTML escaper escapes); `SameSite` over eight request shapes (None sends on 8, Lax on
  3, Strict on 2, and Lax's single exception is a top-level navigation with a safe method, which is
  why state changes must not be GETs); four SSRF validators accepting 3, 3, 2 and 0 of fourteen
  hostile URLs, where the string checks remove classes of a different kind rather than being three
  attempts at one; three open-redirect checks accepting 4, 7 and 1 of nine, where the check that
  looks correct — `urlparse` netloc empty — accepts **more** than the check it replaced; IDOR as a
  route guard against a row scope (4 of 12 endpoint-and-caller pairs leak, one leaking endpoint's
  guard is correct, and one scope takes it to 0); session lifecycle over five attacks and four
  settings (5, 4, 3, 1, and the one that survives all four is a password change, which is not a
  session event at all), with a token table where every measurable generator is 1000 distinct out of
  1000 and two of them are reproduced in full by an attacker who never saw one; an early-exit
  comparison that recovered 27 of 28 bytes and misses the last one because there is no byte after it
  to differ at; three secret detectors finding 2, 3 and 5 of six credentials at a cost of 0, 1 and 3
  false alarms, where the keyword list held `api key` and not `key`; the dependency supply chain
  (125 resolutions → 27 → 25 → 1, where the last two rows are the same number and not the same
  thing, plus 4 of 6 install steps running package-authored code); and the logging category, where
  32 of 54 lines carry a credential and 6 of the 29 requests an incident would need produce no line
  at all. The scenario walks one password reset link and counts six mistakes in six different
  places.*

## Part X · Architecture & Patterns — 54–57 (4) ★

> Chapters 23 and 33 teach architecture by example. This part supplies the names, so the reader can
> read a codebase they did not write and can argue about a design instead of asserting it.

- ✅ 54 Patterns You Will Actually Use — *six shapes that get written again and again, each one
  measured against the thing it replaced, and several of the measurements coming out against the
  pattern. A five-method strategy written twice: the chain compares the method name 15 times to
  resolve 5 calls and the table once per call, which is the argument everybody makes and it is true —
  and the line count goes the other way, 24 lines of chain against 35 lines of table, with the table
  mentioning every name twice (once as a function, once as a key) where the chain mentions each once.
  What the table actually buys is in the third measurement: both refuse an unknown method, but the
  chain whose last branch is a default charges it the standard rate, so the request succeeds and the
  only signal is a plausible number. `functools.singledispatch` as the strategy pattern with the
  selection already written — 4 handlers, 9 values, 4 reaching the default, where `True` and a
  `Money` subclass both land on the `int` handler because the dispatch walks the mro, and where the
  second argument decides nothing at all. The observer pattern as a three-line loop: the version that
  does not isolate failures raised after 2 of 6 subscribers had run and lost the three after it, the
  isolating version ran 5 of 6 and returned the failure as data, and all 6 orderings of three folding
  subscribers leave a different value, so the order is part of the result and nothing in the pattern
  says what it is. An adapter measured as a count of places — 4 fields read in 4 places directly
  against 4 read in 1 behind a translation, indistinguishable under v1 and 4-of-4 versus 1-of-1
  missing under v2 — and the honest version of the argument, which is that with a single call site
  there is no difference at all. A factory registry: 5 handlers defined, 3 registered at import, 5
  after an import nobody wrote for that reason, and a `globals()` lookup resolving 6 of 8 requests
  where the registry resolved 5 — **not the same five**, since three of the names it answered for
  were not handlers and two of the registry's handlers were not module-level names. A composite of 12
  nodes (8 files, 4 directories, 3 implementations of the interface) where every query visits all 12,
  and a caching node that takes it to 13, 1, 1 — the pattern working exactly as advertised, and the
  node that has to be invalidated with no method in the interface for it. `@` as the decorator
  pattern: 5 things a function carries, a bare decorator losing 4 of them (the module survives by
  accident, because the decorator was defined in the same module), `functools.wraps` restoring 5, and
  a decorator factory being 3 nested functions. An interface check worth what it costs: 4 objects
  against 3 ways of naming the interface, where a plain `Protocol` raises `TypeError` for all 4, a
  `runtime_checkable` one accepts 4 of 4 — including an object whose method takes no arguments and
  one whose method name is bound to the number five — and an ABC accepts 1, having made every class
  that already satisfied it be edited to say so. And the chapter's own method turned on its own
  subject: 5 frames for one expression with 4 of them pure forwarding, and 5 layers each with exactly
  1 implementation, so every seam has one thing on each side. The pitfall is the case where the
  pattern does not pay — 4 classes, 6 defs and 33 lines against 0 classes, 1 function and 9 lines,
  both raising `KeyError` on an unknown channel. The scenario is a plugin host: 8 plugins, 4 of them
  broken in 4 different ways, and 5 hosts answering 4, 4, 4, 5 and 5 requests, where the last row
  answers no more than the one above it and differs only in finding the breakage before the first
  request.*
- ✅ 55 Dependency Injection and Inversion of Control — *what injection changes, counted rather than
  asserted, with several counts coming out against the practice. A ledger that builds its own
  database handle against one that takes it: both pass all 6 behaviours, and 0 of the 6 can be handed
  a stand-in under the first design against 6 of 6 under the second, decided by the one line that
  names the concrete type. A module-level handle over 3 behaviours in 3 orders, where all 3 change
  their result depending on what ran before them — and the first order is the one that passes, which
  is the order somebody would write them in. A `Protocol` seam with 3 implementations the consumer
  names 0 of, where 2 of the 3 return a value for every key and the third returns two and a `None`
  and the protocol said nothing about which is allowed. Inversion measured as the direction of the
  reference: **each design holds exactly 1 reference between the policy and the mechanism and they
  point in opposite directions**, so inversion is not a reduction in coupling — what changes is which
  module is on the receiving end, which is why the interface belongs to the consumer. Wiring and
  where a typo is found: 6 services, 6 dependencies and one undeclared name, where the hand-written
  root and the lazy container both get through 5 of 6 and the eager one constructs 0 of 6 — the
  container's gain is that the graph is data, and its cost is that `NameError` naming a thing becomes
  `KeyError` naming a string. A framework's `Depends` marker: 5 parameters across 4 handlers, 4
  marked, and the handler bodies name a provider in 0 of them. Lifetimes over 3 requests — 1, 3 and 6
  instances for singleton, per-request and transient — and a singleton that captured a per-request
  object handing 2 of the 3 requests the wrong session with nothing raising. A service locator that
  names 0 of 3 dependencies in the signature while one override reaches all 4 callers. The pitfall is
  the case where injection does not pay: a pure function behind an interface, adding 2 classes, 2
  functions and 10 lines for 1 implementation that no test needed to replace. The scenario is a
  checkout wired 3 ways — builds its own (0 of 3 tests run, 1 file names the vendor), takes one from
  every caller (3 of 3 tests, but 3 files name the vendor, which is where most refactors stop), and
  takes one wired in a composition root (3 of 3 tests and 1 file).*
- ✅ 56 Hexagonal Architecture — *ports and adapters, the dependency rule, repository and unit of
  work, the boundary that keeps the storage engine out of the domain, and where a web framework and
  a game loop each sit relative to it. Written and verified: 5/5 blocks.*
- ✅ 57 Refactoring and When Not to Abstract — *code smells, the disciplined refactoring loop,
  premature abstraction and YAGNI, the strangler fig, and the cost of a layer you did not need.
  Written and verified: 4/4 blocks.*

## Part XI · Performance & Data at Scale — 58–61 (4) ★

- ✅ 58 Measure First — *the one rule of the part, that a number you did not count is a guess, taught
  by counting rather than timing in all 15 blocks. Four phases of a report each looping exactly 400
  times, where the loop counts are identical and cannot rank them and the work counts say one phase
  does 99.8% of the work — a count of iterations counts how often code was reached, not what it did.
  A `cProfile` run where `normalise` is entered 3,000 times doing one thing and `count_words` 5 times
  doing 1,200, so the call-count ranking and the operation-count ranking disagree about which to look
  at first, because a profiler counts entries and cannot see the loop inside one. Three ways to find
  a duplicate at four sizes, where **doubling the input multiplies the work by 4.01, 2.28 and 2.00**,
  and the fitted exponents 2.00 / 1.19 / 1.00 are what name the shapes — with the note that counting
  the pass over neighbours and leaving the sort out makes the sort-based version report itself as
  linear. Three ways to total a column that all produce 897 while holding 557, 257 and 0 items in
  intermediates, and why `sys.getsizeof` is in the same category as a timing. Attribution: one
  function entered 8,600 times from 4 call sites, where two sites are 95% of the work and halving the
  function's cost removes 4,300 units while **deleting one duplicate pass removes 4,200** — the same
  size of win and only one of them is a deletion. Why one run is not a measurement: 5 candidates
  whose true costs differ by 20 units measured with a wobble of 60, where run 1 gets 1 of 5 positions
  right and 9 runs average 1.11, the median of the 9 gets 5 of 5 because a symmetric error cancels,
  and the count gets 5 of 5 on the first run and needs no repetition at all. A complexity class used
  for what it is actually for: 4 counts fitted to an exponent predicting a 5th size the program has
  not run, within 2.8%. The peak against the total: 5,000 rows read exactly once in all three designs,
  holding 5,000, 32 or 1 at once. And the order to fix things in: 6 fixes ranked by work removed
  against work removed per line changed, where the two orders disagree in 2 of 6 positions because a
  memo removes 3.0x the work of a set at 13.3x the lines. The pitfall is the benchmark that measures
  something else — 6 designs all declaring 50, of which 1 enters the function 50 times, 4 never enter
  it, and all 6 produce a number. The scenario is a 5-phase report where 2 phases are 99.7% of the
  work, both are one-line loops, and the 2 fixes a reader reaches for first are 0.1% each.*
- ✅ 59 Caching — *a cache is a copy of an answer, so it is a correctness decision before it is a
  performance one, and the chapter is arranged so the counts get harder as they go. The hit rate is a
  property of the caller: the same function behind the same cache gave 82.8% on one access pattern
  and 36.6% on another, because the misses are the number of distinct keys and nothing else (172
  against 634). Three places to put the write — cache-aside did 41 store reads, write-through 16 and
  write-behind 6 store writes against 40, and write-behind is the only one with a disagreement count
  above zero, 45 reads that got an answer the store did not have. **The precise invalidation is the
  wrong one**: dropping the three entries the key named left 10 reads stale because a derived value
  depended on the source without naming it, and dropping 1 entry instead left 14, so the policy that
  looks most careful is the worst. A TTL as two numbers at once — 5 ticks gave a staleness bound of 4
  and 80 loads, 100 ticks a bound of 99 and 4 loads, and the 100-tick setting left 14.8x as many stale
  reads from 20x fewer loads because the count depends on how the TTL falls against the source's change
  period. The stampede: 50 callers arriving together computed the same answer 50 times, and a hit rate
  computed afterwards does not show it. The key as the correctness of the cache — naming the item gave
  30 hits and 18 wrong answers, naming the type gave 39 hits and 36 wrong answers, and a key that is
  different on every call is a memory leak with a hit rate of zero (50 entries for 50 calls). Why the
  hit rate is not the metric: 90% over a two-unit call removed 180 units, 40% over a hundred-unit call
  removed 4,000. Every bounded eviction policy fails a scan — LRU 0, FIFO 0, random 7 hits out of 400,
  while not evicting got 200, so the spread across policies is 1.8 points and the spread from any
  policy to keeping everything is 48.2. Two levels multiply their miss rates, 260 store reads down to
  125. The pitfall is the key that is different every time — one of five designs answers the wrong
  question on half the calls while reporting nothing but hits. The scenario is a read-heavy service
  with four workers, where per-worker caches are worse than a shared one on both counts: 221 store
  reads with 199 stale reads against 95 and none, and publishing the invalidation to every worker is
  correct and costs 307.*
- ★ 60 Databases at Scale — *indexes and reading a query plan, the isolation levels and the
  anomalies they prevent, connection pooling, the N+1 problem revisited at a scale where it
  matters, and transactions under contention. **Re-scoped**: this track is stdlib-only, so the
  chapter builds its pool and its isolation demonstrations on `sqlite3` and threads rather than
  on SQLAlchemy, which is not installed and is not needed to make the counts.*
- ★ 61 Counting Instead of Vectorising — *the array and the column store, built from `array` and
  `collections` rather than from NumPy and pandas, which are not installed on this track; what a
  vectorised kernel saves measured as work removed rather than as elapsed time, groupby and join
  written as counts, and the cases where the array is the wrong tool*

## Part XII · Where Next — 62 (1)

- ★ 62 What to Learn Next — *moved from 39 and rewritten to account for Parts VII–XI: an honest
  inventory, one specialisation, one deep project, and a 30-day plan*

---

## Why this is deep enough

- **The three measured gaps are closed by name.** `DEPTH-AUDIT.md` found zero occurrences of Big-O,
  zero of bytecode, zero of reference counting, zero of descriptors-as-a-concept, zero of SSRF and
  friends. Parts VII, VIII and IX are those layers, and they are placed where they explain material
  the reader has already met.
- **Nothing already written is cut or renumbered.** 40 chapters keep their numbers and their text;
  the only file that moves is `39 → 62`.
- **Depth is added by collapsing features, not by adding more of them.** Part VII's five chapters
  replace "learn five more features" with "learn the one mechanism that produces five features you
  already use". That is what makes a book higher-level rather than longer.
- **Every new chapter is machine-verified.** The harness exists (58 blocks, 0 failures), the
  directive contract is in `STYLE.md`, and `text` fences are checked claims — so Part VIII's
  benchmarks and Part VII's `dis` output are captured from real runs, not written from memory.

## Order of work

1. **Part VII (39–43)** first. It explains the most existing material per chapter written, and the
   descriptor chapter is the single highest-value chapter in the whole expansion.
2. **Part VIII (44–49)** second — it is what a higher-level reader will notice missing fastest.
3. **Part IX (50–53)**, then **X (54–57)**, then **XI (58–61)**.
4. **Renumber 39 → 62** last, so the file move happens once.
5. Then the backlog: the 171 untagged programs with output fences that `AUDIT.md` sized.
