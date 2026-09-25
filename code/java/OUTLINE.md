# Java Mastery — the chapter outline

> **60 chapters (ch00–59).** ✅ = written and machine-verified · ★ = to write.
>
> Held to the same standard as `code/cpp/OUTLINE.md`. The existing 7-part structure in `parts.json`
> is kept exactly, and the written chapters keep their numbers, so nothing already published moves.
>
> The Java track starts from a stronger position than C/C++ did: `tools/verify_examples.py` is
> already in place and reports **334/334 blocks behaved as declared**, with `self-test PASSED`. Every
> ★ chapter below is expected to arrive with its own `tools/gen/<NN>/` generator, exactly as the
> C++ track does.
>
> Chapters 04–10 (Part I), 11–19 (all of Part II) and 20–24 (all of Part III) were each written with a
> `tools/gen/<NN>/` directory holding the Java sources and a `gen.py` that captures every transcript
> live. The harness is the arbiter: no output in a `text` fence was typed by hand.

## Part 0 · Start Here — 00–01 (2)

- ✅ 00 How to Use This Book
- ✅ 01 Your First Program

## Part I · Foundations — 02–10 (9)

- ✅ 02 Primitives and References
- ✅ 03 Strings
- ✅ 04 Operators, Casting and Integer Arithmetic — *overflow, integer division, `Math`, promotion*
- ✅ 05 Control Flow — *`if`, `switch` expressions, the three loops*
- ✅ 06 Methods, Overloading and the Call Stack
- ✅ 07 Arrays and the Enhanced `for`
- ✅ 08 Classes, Objects and Encapsulation
- ✅ 09 Inheritance, Interfaces and Polymorphism
- ✅ 10 `Object`: `equals`, `hashCode`, `toString` — *the contract every collection depends on*

## Part II · Leveling Up — 11–19 (9)

- ✅ 11 Generics and Type Erasure
- ✅ 12 The Collections Framework — *`List`, `Set`, `Map`, `Comparable`, `Comparator`*
- ✅ 13 Exceptions and `try`-with-resources
- ✅ 14 Lambdas, Functional Interfaces and Method References
- ✅ 15 Streams and `Optional`
- ✅ 16 Records, Enums and Sealed Types — *compact constructors, ordinal order, exhaustive switch*
- ✅ 17 I/O, NIO.2 and `Files` — *`Path` as a value, encodings, `walk` vs `list`, atomic writes*
- ✅ 18 Dates, Times, `BigDecimal` and Formatting — *`Period` vs `Duration`, zones, scale and rounding*
- ✅ 19 Testing with a Hand-Built Test Runner — *annotations, reflection, assertions, test doubles*

## Part III · Project 1 · Quill — 20–24 (5)

- ✅ 20 The Project — Quill, a Command-Line Vault — *exit codes as a contract, `Note` as a record, a
  sealed command hierarchy, an append-only vault, the CLI driven for real*
- ✅ 21 Reading and Parsing Input — *`readLine` vs `Scanner`, `null` vs `""`, `parseInt`'s real
  accept-set, CRLF, and `add` reading its body from standard input*
- ✅ 22 Persistence — Files, Serialization and a Real Format — *escaping and the backslash order,
  round-trip properties, why not `Serializable`, charsets, a file header, atomic replace*
- ✅ 23 A Command Layer and Argument Parsing — *parse into a value before executing anything, a sealed
  command hierarchy, `UsageException` and the retired exit code `3`, `--vault` and the `--` terminator*
- ✅ 24 Assembling Quill — *the six files and their one-way arrows, exit codes as the public interface,
  an end-to-end test table, why `main` cannot be tested, `jar --main-class`, a closed hierarchy*

## Part IV · Track A · Bulletin — 25–39 (15)

> The web service is built on `com.sun.net.httpserver` from the JDK, so **the whole track is
> verifiable offline with zero third-party jars** — no Maven Central, no Spring. That is the single
> biggest difference from a typical Java web tutorial, and it is what makes this track gate-able.

- ★ 25 How the Web Works — *TCP, HTTP, status codes, headers*
- ★ 26 The JDK HTTP Server — *`HttpServer`, handlers, the request/response model*
- ★ 27 Requests, Responses and Routing
- ★ 28 JSON — Parsing and Generating
- ★ 29 HTML Templates and Escaping — *and the XSS it prevents*
- ★ 30 Concurrency — Thread Pools and `ExecutorService`
- ★ 31 Threads, Locks and the Java Memory Model
- ★ 32 JDBC and a Real Database
- ★ 33 SQL, Transactions and Connection Pooling
- ★ 34 Sessions, Cookies and Authentication
- ★ 35 Configuration, Logging and Graceful Shutdown
- ★ 36 Testing the Service End to End — *unit, integration, and a real client*
- ★ 37 Build Tools — `javac`, `jar`, Maven and Gradle
- ★ 38 Packaging and Deployment — `jlink`, `jpackage`, containers
- ★ 39 **CAPSTONE A — Bulletin, the Complete Web Service**

## Part V · Track B · Ironhold — 40–54 (15)

> Swing and AWT are present, and the track renders into a `BufferedImage` so that output is
> checkable as **pixels**. Per `STYLE.md`: never assert on a `JFrame`. Chapter 53 turns that into a
> real property — the game gets deterministic, headless tests.

- ★ 40 The Game Loop and Rendering into a `BufferedImage`
- ★ 41 Sprites, Animation and Double Buffering
- ★ 42 Input, and the Swing Event Thread
- ★ 43 Collision Detection and Response
- ★ 44 Vectors and Physics
- ★ 45 Scenes, Game State and the State Machine
- ★ 46 Entities and Component Systems
- ★ 47 Tilemaps and Level Loading
- ★ 48 Cameras, Parallax and Lighting
- ★ 49 Pathfinding and Enemy AI
- ★ 50 Audio with `javax.sound`
- ★ 51 UI, Menus and Save Files
- ★ 52 Performance, Profiling and the JIT
- ★ 53 Deterministic Headless Tests for a Game
- ★ 54 **CAPSTONE B — Ironhold, the Complete Game**

## Part VI · Appendices & the Kotlin Extension — 55–59 (5)

- ★ 55 The JVM, Bytecode and the Toolchain Reference — *`javap`, class files, `-Xlint`, the module system*
- ★ 56 Garbage Collection and Memory in Practice
- ★ 57 Kotlin I — Kotlin for a Java Developer
- ★ 58 Kotlin II — Coroutines and Java Interop
- ★ 59 Where to Go Next

---

## Why this is the same standard as C++

The C++ outline's three claims were: **two capstones at Python's scale**, **systems depth Python has
no equivalent for**, and **engineering rather than language**. The Java plan answers each in JVM
terms.

- **Two capstones at Python's scale.** CAPSTONE A (39) and CAPSTONE B (54) are held to the ~100 KB
  bar set by `python/chapters/30-capstone-studyhub.md` and `36-polish-packaging-capstone.md`.
- **JVM depth that is specific to Java.** Type erasure (11), the memory model (31), bytecode and
  `javap` (55), and garbage collection (56) are the material that makes the rest debuggable rather
  than magic. They are the Java counterpart of the C++ track's memory-layout, link-step and
  preprocessor chapters.
- **Engineering, not just language.** Build tools (37), packaging and `jlink`/`jpackage` (38),
  end-to-end testing (36), profiling and the JIT (52), and deterministic headless tests (53).
  Python covers these in `ch11`/`ch22`/`ch29`; C++ covers them in `09`/`44`/`53`.

## Deliberate choices, and what is contested

Two decisions worth stating plainly, because a reader comparing this to a typical Java syllabus will
notice them.

1. **No Spring, and no Maven Central dependency in the web track.** Most Java web teaching starts
   with Spring Boot, which pulls a large dependency tree from the network. That would make the
   track unverifiable on a machine without network access and would put a framework between the
   reader and HTTP. The JDK's own `com.sun.net.httpserver` is used instead, so chapters 25–39 are
   gated exactly like the rest of the book. Spring is named in prose as the industry default, not
   taught as the foundation. This is a contested choice — a reader who wants a job in Java web
   development will eventually need Spring — so it is marked here rather than quietly omitted.
2. **Kotlin gets two chapters, not zero.** `languages.json` advertises the Java track as "Enterprise
   web and JVM games — with a Kotlin extension", and modern JVM work frequently mixes the two. The
   extension is kept to two chapters (57, 58) so it does not dilute the Java material, and it is
   placed in the appendices rather than as a second track.
3. **The database chapters build the engine.** There is no JDBC driver in the JDK, and this track
   takes no third-party jars, so chapters 32–33 implement a small in-memory engine behind the JDBC
   interfaces by hand rather than connecting to a real database. This is the same trade as the
   testing chapters, which build their own runner because JUnit is not installed. A reader who needs
   a real database will need a driver — SQLite, H2 and PostgreSQL are named in prose — but the lesson
   that matters most, that `?` placeholders are what prevent SQL injection, survives intact, and the
   whole thing stays verifiable offline. It is a contested choice, so it is stated rather than
   quietly worked around.

## Optional further additions if wanted later

Each would need a small renumber of Part VI: a dedicated **annotation processing / reflection**
chapter, a **Java modules (JPMS) in depth** chapter, and a **desktop UI with JavaFX** chapter if
JavaFX is ever installed on the build machine — it is not present today, so such a chapter could not
be machine-verified and would have to be labelled as such.
