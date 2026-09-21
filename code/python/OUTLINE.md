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

## Part VIII · Algorithms & Complexity — 44–49 (6) ★

> Chapter 35 already implements A*. This part is what makes it possible to see that A* is graph
> search, and to choose a data structure on evidence rather than habit.

- ✅ 44 Complexity and the Cost Model — *Big-O, Θ and Ω, growth rates, amortised cost, the real
  constant factors of Python operations measured with `timeit`, and the difference between a
  benchmark and a guess*
- ★ 45 Core Data Structures — *dynamic arrays, linked lists, stacks, queues and `deque`, a hash
  table written by hand to see why `dict` is O(1), heaps and `heapq`, balanced trees vs `bisect`
  vs sorted list, tries; each one chosen for a stated cost*
- ★ 46 Sorting and Searching — *comparison sorts, why `sorted` is Timsort and stable, `key=` vs
  `cmp_to_key`, binary search and its off-by-one, `bisect` for insertion and rank*
- ★ 47 Graphs — *adjacency list vs matrix, BFS, DFS, topological sort and cycle detection,
  Dijkstra with a heap, and A\* (Chapter 35) as Dijkstra plus a heuristic*
- ★ 48 Recursion, Memoisation and Dynamic Programming — *the recursion tree, overlapping
  subproblems, `functools.lru_cache`, top-down vs bottom-up, edit distance, knapsack, and the
  recursion limit as a design constraint*
- ★ 49 A Method for Unseen Problems — *read the constraints first, derive a complexity budget,
  pick the structure, then the algorithm; worked interview-style problems from statement to
  proof of complexity, including the ones where the answer is "sort it first"*

## Part IX · Security — 50–53 (4) ★

> Chapters 18, 19, 27 and 28 already do the right things. This part is the framework that turns
> those habits into principles the reader can apply to code nobody has written yet.

- ★ 50 Thinking Like an Attacker — *assets, trust boundaries and threat modelling; the OWASP Top
  Ten mapped onto the specific Python code in this book; why "it is only internal" is not a
  control*
- ★ 51 Injection — *SQL injection and why parameterised queries work at the protocol level;
  command injection and `subprocess` without `shell=True`; template injection; `eval`/`exec` and
  `ast.literal_eval`; log injection*
- ★ 52 Untrusted Data — *`pickle`, `yaml.load`, XML entity expansion, zip/tar path traversal and
  the "zip slip" bug, `marshal`, size and depth limits, and schema validation as a boundary*
- ★ 53 Web Security — *XSS and the escaping contexts, CSRF and why `SameSite` is not enough, SSRF
  and allow-lists, open redirects, authentication vs authorization and the IDOR bug, session
  fixation, timing attacks on comparison, secret management, and dependency supply chain
  (`pip-audit`, pinning, reproducible installs)*

## Part X · Architecture & Patterns — 54–57 (4) ★

> Chapters 23 and 33 teach architecture by example. This part supplies the names, so the reader can
> read a codebase they did not write and can argue about a design instead of asserting it.

- ★ 54 Patterns You Will Actually Use — *strategy, observer, adapter, factory, composite, and the
  Python-specific twist: which of the GoF patterns are already built into the language*
- ★ 55 Dependency Injection and Inversion of Control — *constructor injection, seams via
  `Protocol`, why DI is about testing rather than about frameworks, and why FastAPI's `Depends` is
  dependency injection whether or not it is called that*
- ★ 56 Hexagonal Architecture — *ports and adapters, the dependency rule, repository and unit of
  work, the boundary that keeps SQLAlchemy out of the domain, and where FastAPI and Pygame each
  sit relative to it*
- ★ 57 Refactoring and When Not to Abstract — *code smells, the disciplined refactoring loop,
  premature abstraction and YAGNI, the strangler fig, and the cost of a layer you did not need*

## Part XI · Performance & Data at Scale — 58–61 (4) ★

- ★ 58 Measure First — *`cProfile`, `timeit`, `py-spy`, `tracemalloc` and flame graphs; finding the
  hot loop in a real program; why the bottleneck is never where you guessed*
- ★ 59 Caching — *in-process `lru_cache`, cache-aside vs write-through vs write-behind,
  invalidation as the hard part, TTLs, stampedes, and Redis as a shared cache*
- ★ 60 Databases at Scale — *indexes and reading a query plan, the isolation levels and the
  anomalies they prevent, connection pooling, async SQLAlchemy, and the N+1 problem revisited at
  a scale where it matters*
- ★ 61 Vectorising with NumPy and pandas — *arrays and broadcasting, vectorised vs looped code
  measured side by side, groupby and joins, and the cases where pandas is the wrong tool*

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
