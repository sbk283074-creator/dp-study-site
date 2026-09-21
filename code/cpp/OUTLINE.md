# C / C++ Mastery — the chapter outline

> **60 chapters (ch00–59).** ✅ = written and machine-verified · ★ = to write.
>
> Parts 0–IV keep the numbers the in-progress renumbering already gave them, so no written
> chapter moves. Parts V–VII are the build-out. The additions beyond Lucas's 57-chapter sketch
> are the *engineering* chapters (async I/O, sessions/auth, config/logging, end-to-end testing,
> packaging, security, design patterns) — the content that turns "knows C++" into "can ship a
> real project".

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
- ★ 08 Bits, Bytes, Endianness and Memory Layout — *what the bytes actually are*
- ★ 09 The Compile Pipeline, Linking and Build Systems — *preprocess → compile → assemble → link; Make and CMake*

## Part II · C Advanced — 10–16 (7)

- ✅ 10 Arrays and Strings
- ✅ 11 Structs, Enums and Unions
- ✅ 12 Dynamic Memory
- ✅ 13 Files and Streams
- ✅ 14 Headers and Multiple Files
- ★ 15 The Preprocessor — *macros, includes, conditionals, and why they are dangerous*
- ★ 16 Undefined Behaviour and Sanitizers — *the contract you must not break; ASan/UBSan/TSan*

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

## Part VII · Appendices — 55–59 (5)

- ★ 55 The Toolchain, Build and Debug Reference (compilers, CMake, gdb/lldb, sanitizers, Valgrind)
- ★ 56 Compile-time Programming and Metaprogramming (`constexpr`, `if constexpr`, `static_assert`)
- ★ 57 C/C++ Interop, Libraries and the Ecosystem (calling C, `extern "C"`, package managers, ABI)
- ★ 58 Design Patterns and Architecture in C++ (RAII idioms, pimpl, DI, SOLID)
- ★ 59 Where to Go Next

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

Optional further additions if wanted later (each needs a small renumber of 34–37): custom memory
allocators, a serialization/binary-protocol chapter, and a dedicated version-control/CI chapter.
