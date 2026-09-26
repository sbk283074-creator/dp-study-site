# C / C++ Mastery — the chapter outline

> **70 chapters (ch00–69).** ✅ = written and machine-verified · ★ = to write.
>
> Parts 0–V keep the numbers the in-progress renumbering already gave them, so no written
> chapter moves — everything written is ch00–ch41. Parts VI–XII are the build-out, and their
> numbers were settled on 2026-09-23 by the six-layer requirement, not by taste.
>
> **All six layers now have a home (2026-09-23).** `_build/check-standard.py` locates a layer by
> the **part title** in `parts.json`, and a track cannot conform unless each layer has a part to
> live in. Before this date the outline gave C++ a cost and a security part (from
> `code/DEPTH-AUDIT.md`) but **no internals, no architecture and no performance part** — so those
> three checks read 0 no matter how much of either subject the chapters taught. The three parts
> added to fix that are VII (`...Actually Works` → internals), VIII (`Design, Architecture and
> Patterns`) and X (`Performance, Profiling and Scale`); the appendices that used to be Part VII
> are dissolved into them, because a reference appendix is neither an internals nor an
> architecture layer. The Python track solved the same problem the same way (its Parts VII–XI).
>
> **The engineering chapters.** Beyond Lucas's 57-chapter sketch, the build-out carries async I/O,
> sessions/auth, config/logging, end-to-end testing, packaging, architecture, cost, performance
> and security — the content that turns "knows C++" into "can ship a real project". C++ is the
> best language in the platform to teach algorithms (the reader can *measure* the constant factor
> and watch the cache effect) and it is the language where security starts as memory safety.

## Part 0 · Start Here — 00–01 (2)

- ✅ 00 How to Use This Book
- ✅ 01 Your Workbench

## Part I · C Foundations — 02–09 (8)

- ✅ 02 Your First C Program
- ✅ 03 Types and Numbers
- ✅ 04 Operators and Expressions
- ✅ 05 Control Flow
- ✅ 06 Functions and the Stack
- ✅ 07 Pointers and Memory
- ✅ 08 Bits, Bytes, Endianness and Memory Layout — *what the bytes actually are*
- ✅ 09 The Compile Pipeline, Linking and Build Systems — *preprocess → compile → assemble → link; Make and CMake*

## Part II · C Advanced — 10–16 (7)

- ✅ 10 Arrays and Strings
- ✅ 11 Structs, Enums and Unions
- ✅ 12 Dynamic Memory
- ✅ 13 Files and Streams
- ✅ 14 Headers and Multiple Files
- ✅ 15 The Preprocessor — *macros, includes, conditionals, and why they are dangerous*
- ✅ 16 Undefined Behaviour and Sanitizers — *the contract you must not break; ASan/UBSan/TSan*

## Part III · Project 1 · A C Systems Tool — 17–21 (5)

- ✅ 17 The Project — a Static HTTP Server
- ✅ 18 Parsing Requests Safely
- ✅ 19 Building Responses
- ✅ 20 Sockets and the Server Loop
- ✅ 21 Assembling serve

## Part IV · Transition to Modern C++ — 22–33 (12)

- ✅ 22 Why C++
- ✅ 23 References, const, and Overloading
- ✅ 24 Classes and Encapsulation
- ✅ 25 Copying, Moving and the Rule of Five
- ✅ 26 Smart Pointers
- ✅ 27 Inheritance and Polymorphism
- ✅ 28 Templates
- ✅ 29 The Standard Library
- ✅ 30 Exceptions and Error Handling
- ✅ 31 Operator Overloading and Iterators — *making your types feel built-in; writing iterators* — 20/20 blocks
- ✅ 32 Value Categories and Perfect Forwarding — *lvalues/rvalues, `std::move`, `std::forward`* — 14/14 blocks
- ✅ 33 C++20/23 — *concepts, ranges, `std::expected`, `std::span`, `format`* — 15/15 blocks, `std: c++23`

## Part V · Track A · C++ Web Service — 34–45 (12)

- ✅ 34 Porting serve to C++
- ✅ 35 Requests, responses and a router
- ✅ 36 JSON by Hand
- ✅ 37 Persistence — Surviving a Restart
- ★ 38 SQLite — a Real Database (RAII wrapper over the C API)
- ★ 39 HTML Templates and Escaping (and the XSS it prevents)
- ★ 40 Concurrency — Serving Many Clients (threads, thread pool, mutexes)
- ★ 41 Async I/O — Non-blocking Sockets and the Event Loop (`select`/`poll`/`epoll`/`kqueue`)
- ★ 42 Sessions, Cookies and Authentication
- ★ 43 Configuration, Logging and Graceful Shutdown
- ★ 44 Testing the Service End to End (unit + integration + a real `curl` harness)
- ★ 45 **CAPSTONE A — The Complete Web Service** (routing + DB + templates + concurrency + auth, tested and deployed)

## Part VI · Track B · C++ Game — 46–53 (8)

> SDL2 / Raylib / GLFW are **not installed here**; these chapters must be labelled *not machine-verified*.
> What can still be verified is everything the game does not draw: the fixed-timestep accumulator,
> collision maths, the tilemap parser, A\* on a grid — each is a program with an output.

- ★ 46 The Game Loop, Window and Input
- ★ 47 Sprites, Drawing and Animation
- ★ 48 Collision and Physics
- ★ 49 Game State, Scenes and Entities
- ★ 50 AI — Pathfinding and Enemy Behaviour
- ★ 51 Tilemaps, Cameras and Level Design
- ★ 52 Audio, UI and Polish
- ★ 53 **CAPSTONE B — The Complete Game**

## Part VII · Inside C++ — How the Toolchain, Linker and Runtime Actually Works — 54–57 (4)

> The internals layer. The old appendices lived here as separate topics; this part names what they
> have in common — each one is *how the thing under you actually works*, so that a linker error, a
> 200 ms rebuild or a `vtable` crash stops being magic. Every chapter here is machine-verified
> with the room's own toolchain (`nm`, `otool`, `clang -E`, `gdb`/`lldb`, sanitizers).

- ★ 54 The Toolchain, Build and Debug Reference — *preprocess → compile → assemble → link made
  visible with `clang -E`/`-S`/`nm`, translation units and ODR, CMake properly, `gdb`/`lldb`,
  sanitizers, Valgrind, and `static_assert`*
- ★ 55 The Object Model, the ABI and the Linker — *object layout and padding, `vtable` and
  virtual dispatch cost, name mangling, calling conventions, `extern "C"`, what an ABI break is
  and why a header-only library is not immune*
- ★ 56 Compile-time Programming and Metaprogramming — *`constexpr` and `consteval`, `if constexpr`,
  variadic templates, fold expressions, concepts, SFINAE vs `requires`, and how to read the error
  wall*
- ★ 57 C/C++ Interop, Libraries and the Ecosystem — *calling C from C++, opaque handles, ownership
  across the boundary, ABI stability, package managers and vendoring*

## Part VIII · Design, Architecture and Patterns — 58–59 (2)

> The architecture layer. Chapter 24 taught encapsulation and chapter 26 RAII; this is what happens
> when the program is 50 000 lines instead of 500 and the boundaries are the deliverable.

- ★ 58 Design Patterns and Architecture in C++ — *RAII as the universal idiom, pimpl, factory,
  observer, strategy, dependency injection without a framework, and why C++ prefers value types to
  object hierarchies*
- ★ 59 Structuring and Evolving a Large Program — *layering and dependency direction, interfaces
  as seams for testing, keeping the build fast, versioning a public API, deprecation and
  backwards compatibility*

## Part IX · Algorithms & Complexity — 60–64 (5) ★

> The cost layer. Chapter 35 of the Python track implements A* and chapter 29 uses `std::sort`; this
> part is what makes it possible to see that A* is graph search and to choose a container on
> evidence. C++ is the right language for it because the reader can measure the constant factor,
> not just the exponent.

- ★ 60 Complexity and the Cost Model — *Big-O, Θ and Ω, growth rates, amortised cost, `std::chrono`
  benchmarking done properly, and the cache: why the same algorithm is an order of magnitude
  faster here than in Python, and when it is not*
- ★ 61 Core Data Structures — *`std::vector` growth and amortised push_back, linked lists and why
  they usually lose to vector, `deque`, hash tables by hand (chaining vs open addressing) and
  against `unordered_map`, binary heaps and `priority_queue`, balanced trees and `std::map` vs
  `unordered_map`, tries; each chosen for a stated cost*
- ★ 62 Sorting and Searching — *comparison sorts, introsort in `std::sort`, stability and
  `stable_sort`, partial sorting with `nth_element`, `lower_bound`/`upper_bound`, and the strict
  weak ordering bug that makes a comparator UB*
- ★ 63 Graphs — *adjacency list vs matrix and their cache behaviour, BFS, DFS, topological sort and
  cycle detection, Dijkstra with a `priority_queue`, and A\* as Dijkstra plus a heuristic*
- ★ 64 Recursion, Memoisation and Dynamic Programming — *the recursion tree, overlapping
  subproblems, memoisation with a map vs a vector, top-down vs bottom-up, edit distance, knapsack,
  and stack depth as a real constraint in C++*

## Part X · Performance, Profiling and Scale — 65–66 (2)

> The performance layer. "It is fast enough" is a measurement, not an opinion, and the tools that
> produce the measurement are the chapter.

- ★ 65 Performance and Profiling — *the frame budget and the request budget, the memory hierarchy
  and the cache, measure-don't-guess with `perf`/Instruments/`std::chrono`, branch prediction,
  aliasing, and the optimisations that are actually worth doing*
- ★ 66 Measuring and Scaling a Real Service — *load testing, throughput vs latency and why
  percentiles beat averages, back-pressure, when one thread is not enough and when it is,
  multi-process and `SO_REUSEPORT`, and profiling the capstone under load*

## Part XI · Security and Hardening — 67–68 (2)

> The security layer. Chapter 16 teaches UB as a correctness problem and chapter 39 teaches
> escaping; this part is where UB becomes an attack surface and escaping becomes one control among
> many.

- ★ 67 Memory Safety and Undefined Behaviour as a Security Problem — *buffer overflows and off-by-one,
  signed/unsigned integer overflow, use-after-free and double free, format string bugs, uninitialised
  reads, `std::span` and bounds-checked access, and how each one becomes an exploit rather than a
  crash*
- ★ 68 Hardening Real Programs — *parsing untrusted input safely, TOCTOU, path traversal, injection,
  constant-time comparison, what never to implement yourself (crypto), and the mitigations:
  `_FORTIFY_SOURCE`, stack canaries, ASLR, static analysis, and fuzzing with libFuzzer*

## Part XII · Where Next — 69 (1)

- ★ 69 Where to Go Next — *rewritten to account for Parts VII–XI*

---

## Why this is deep enough

- **Two capstones at Python's scale.** Python's capstones are ~100 KB each (StudyHub, Neon
  Dungeon). CAPSTONE A (45) and CAPSTONE B (53) are held to the same bar.
- **Systems depth Python has no equivalent for.** Memory layout (08), the link step (09), the
  preprocessor (15), UB and sanitizers (16), perfect forwarding (32) — the material that makes
  the rest debuggable rather than magic. In this outline that depth is no longer scattered: Part
  VII names it and finishes it.
- **Modern C++ in full.** RAII → move semantics → smart pointers → templates → concepts/ranges →
  `expected` (22–33) is the actual arc a professional follows.
- **Engineering, not just language.** Build systems (54), end-to-end testing (44), profiling (65),
  packaging/ABI (55, 57), architecture (58–59). Python covers these in `ch11`/`ch22`/`ch29`; the C++
  track now does too.
- **The six layers are parts, not intentions.** core (I–IV) · internals (VII) · cost (IX) ·
  performance (X) · architecture (VIII) · security (XI). This is the shape `check-standard.py`
  measures, and the reason Parts VI–XII were renumbered on 2026-09-23.

Optional further additions if wanted later (each needs a small renumber of 34–45): custom memory
allocators, a serialization/binary-protocol chapter, and a dedicated version-control/CI chapter.
