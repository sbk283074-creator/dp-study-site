# C / C++ Mastery — the chapter outline

> **67 chapters (ch00–66).** ✅ = written and machine-verified · ★ = to write.
>
> Parts 0–IV keep the numbers the in-progress renumbering already gave them, so no written
> chapter moves. Parts V–VII are the build-out. The additions beyond Lucas's 57-chapter sketch
> are the *engineering* chapters (async I/O, sessions/auth, config/logging, end-to-end testing,
> packaging, security, design patterns) — the content that turns "knows C++" into "can ship a
> real project".
>
> **Parts VIII–IX are new (2026-09-21), from `code/DEPTH-AUDIT.md`.** The audit found the same two
> holes here that it found in Python: **no theory of cost** (zero occurrences of Big-O, amortised
> cost, or any data structure not built in) and **no security layer** (zero of SSRF, path
> traversal, timing attacks, supply chain). C++ is the best language in the platform to teach
> algorithms — the reader can *measure* the constant factor and see the cache effect — and it is
> the language where security starts as memory safety. `59 Where to Go Next` becomes `66` so the
> book still ends with it.

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
- ★ 31 Operator Overloading and Iterators — *making your types feel built-in; writing iterators*
- ★ 32 Value Categories and Perfect Forwarding — *lvalues/rvalues, `std::move`, `std::forward`*
- ★ 33 C++20/23 — *concepts, ranges, `std::expected`, `std::span`, `format`*

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

## Part VI · Track B · C++ Game — 46–54 (9)

> SDL2 / Raylib / GLFW are **not installed here**; these chapters must be labelled *not machine-verified*.

- ★ 46 The Game Loop, Window and Input
- ★ 47 Sprites, Drawing and Animation
- ★ 48 Collision and Physics
- ★ 49 Game State, Scenes and Entities
- ★ 50 AI — Pathfinding and Enemy Behaviour
- ★ 51 Tilemaps, Cameras and Level Design
- ★ 52 Audio, UI and Polish
- ★ 53 Performance and Profiling (frame budget, cache, profilers)
- ★ 54 **CAPSTONE B — The Complete Game**

## Part VII · Appendices — 55–58 (4)

- ★ 55 The Toolchain, Build and Debug Reference (compilers, CMake, gdb/lldb, sanitizers, Valgrind)
- ★ 56 Compile-time Programming and Metaprogramming (`constexpr`, `if constexpr`, `static_assert`)
- ★ 57 C/C++ Interop, Libraries and the Ecosystem (calling C, `extern "C"`, package managers, ABI)
- ★ 58 Design Patterns and Architecture in C++ (RAII idioms, pimpl, DI, SOLID)

## Part VIII · Algorithms & Complexity — 59–63 (5) ★

> New. Chapter 35 of the Python track implements A* and chapter 29 uses `std::sort`; this part is
> what makes it possible to see that A* is graph search and to choose a container on evidence. C++
> is the right language for it because the reader can measure the constant factor, not just the
> exponent.

- ★ 59 Complexity and the Cost Model — *Big-O, Θ and Ω, growth rates, amortised cost, `std::chrono`
  benchmarking done properly, and the cache: why the same algorithm is an order of magnitude
  faster here than in Python, and when it is not*
- ★ 60 Core Data Structures — *`std::vector` growth and amortised push_back, linked lists and why
  they usually lose to vector, `deque`, hash tables by hand (chaining vs open addressing) and
  against `unordered_map`, binary heaps and `priority_queue`, balanced trees and `std::map` vs
  `unordered_map`, tries; each chosen for a stated cost*
- ★ 61 Sorting and Searching — *comparison sorts, introsort in `std::sort`, stability and
  `stable_sort`, partial sorting with `nth_element`, `lower_bound`/`upper_bound`, and the strict
  weak ordering bug that makes a comparator UB*
- ★ 62 Graphs — *adjacency list vs matrix and their cache behaviour, BFS, DFS, topological sort and
  cycle detection, Dijkstra with a `priority_queue`, and A\* as Dijkstra plus a heuristic*
- ★ 63 Recursion, Memoisation and Dynamic Programming — *the recursion tree, overlapping
  subproblems, memoisation with a map vs a vector, top-down vs bottom-up, edit distance, knapsack,
  and stack depth as a real constraint in C++*

## Part IX · Security and Hardening — 64–65 (2) ★

> New. Chapter 16 teaches UB as a correctness problem and chapter 39 teaches escaping; this part is
> where UB becomes an attack surface and escaping becomes one control among many.

- ★ 64 Memory Safety and Undefined Behaviour as a Security Problem — *buffer overflows and off-by-one,
  signed/unsigned integer overflow, use-after-free and double free, format string bugs, uninitialised
  reads, `std::span` and bounds-checked access, and how each one becomes an exploit rather than a
  crash*
- ★ 65 Hardening Real Programs — *parsing untrusted input safely, TOCTOU, path traversal, injection,
  constant-time comparison, what never to implement yourself (crypto), and the mitigations:
  `_FORTIFY_SOURCE`, stack canaries, ASLR, static analysis, and fuzzing with libFuzzer*

## Part X · Where Next — 66 (1)

- ★ 66 Where to Go Next — *moved from 59, rewritten to account for Parts VIII–IX*

---

## Why this is deep enough

- **Two capstones at Python's scale.** Python's capstones are ~100 KB each (StudyHub, Neon
  Dungeon). CAPSTONE A (45) and CAPSTONE B (54) are held to the same bar.
- **Systems depth Python has no equivalent for.** Memory layout (08), the link step (09), the
  preprocessor (15), UB and sanitizers (16), perfect forwarding (32) — the material that makes
  the rest debuggable rather than magic.
- **Modern C++ in full.** RAII → move semantics → smart pointers → templates → concepts/ranges →
  `expected` (22–33) is the actual arc a professional follows.
- **Engineering, not just language.** Build systems (09), end-to-end testing (44), profiling (53),
  packaging/ABI (57), architecture (58). Python covers these in `ch11`/`ch22`/`ch29`; the C++
  track now does too.
- **The two layers the depth audit found missing are now present** — a theory of cost (59–63) and
  security (64–65). `DEPTH-AUDIT.md` has the measurements that motivated them.

Optional further additions if wanted later (each needs a small renumber of 34–37): custom memory
allocators, a serialization/binary-protocol chapter, and a dedicated version-control/CI chapter.
