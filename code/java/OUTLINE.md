# Java Mastery — the chapter outline

> **61 chapters (ch00–60).** ✅ = written and machine-verified · ★ = to write.
>
> Held to the same standard as `code/cpp/OUTLINE.md`. The written chapters keep their numbers, so
> nothing already published moves.
>
> `tools/verify_examples.py` is in place and gates every block. Every ★ chapter arrives with its own
> `tools/gen/<NN>/` generator, driven by the shared `tools/gen/javagen.py`. The harness is the
> arbiter: no output in a `text` fence was typed by hand.

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

## Part IV · Track A · Bulletin, a Java Web Service — 25–33 (9) ✅ complete

> The web service is built on `com.sun.net.httpserver` from the JDK, so **the whole track is
> verifiable offline with zero third-party jars** — no Maven Central, no Spring. That is the single
> biggest difference from a typical Java web tutorial, and it is what makes this track gate-able.

- ✅ 25 How the Web Works
- ✅ 26 The JDK HTTP Server
- ✅ 27 Requests, Responses and Routing
- ✅ 28 JSON — Parsing and Generating
- ✅ 29 HTML Templates and Escaping
- ✅ 30 Concurrency — Thread Pools and `ExecutorService`
- ✅ 31 Threads, Locks and the Java Memory Model
- ✅ 32 JDBC and a Real Database — *a small engine behind the JDBC interfaces, because the JDK ships
  no driver and this book takes no jars*
- ✅ 33 SQL, Transactions and Connection Pooling

## Part V · Track A · Sessions, Security and Hardening — 34–35 (2) ✅ complete

- ✅ 34 Sessions, Cookies and Authentication
- ✅ 35 Configuration, Logging and Graceful Shutdown — *`--print-config`, redaction, shutdown hooks*

## Part VI · Track A · Build, Test and the Capstone — 36–39 (4)

- ✅ 36 Testing the Service End to End — *unit, integration, and a real client*
- ★ 37 Build Tools — `javac`, `jar`, Maven and Gradle
- ★ 38 Packaging and Deployment — `jlink`, `jpackage`, containers
- ★ 39 **CAPSTONE A — Bulletin, the Complete Web Service**

## Part VII · Track B · Ironhold — 40–48 (9)

> Swing and AWT are present, and the track renders into a `BufferedImage` so that output is
> checkable as **pixels**. Per `STYLE.md`: never assert on a `JFrame`. Every chapter drives the game
> headless and asserts on pixel values, so the whole track is deterministic and offline.

- ★ 40 The Game Loop and Rendering into a `BufferedImage`
- ★ 41 Sprites, Animation and Double Buffering
- ★ 42 Input, and the Swing Event Thread
- ★ 43 Collision Detection and Response
- ★ 44 Vectors and Physics
- ★ 45 Scenes, Game State and the State Machine
- ★ 46 Tilemaps, Entities and Level Loading
- ★ 47 Pathfinding and Enemy AI
- ★ 48 **CAPSTONE B — Ironhold, the Complete Game**

> Chapters dropped from the earlier, longer game plan and where their material went: cameras and
> parallax fold into 46, audio into 48, profiling and the JIT into Part X where it belongs, and the
> deterministic-headless-testing chapter is not a chapter at all any more — *every* chapter in this
> part is headless and deterministic.

## Part VIII · Inside the JVM — How the Runtime Actually Works — 49–51 (3)

- ★ 49 Bytecode, `javap` and the Toolchain Reference
- ★ 50 Garbage Collection and Memory in Practice
- ★ 51 Class Loading, Reflection and the JIT

## Part IX · Architecture, Patterns and Design — 52–53 (2)

- ★ 52 Design Patterns That Earn Their Keep in Java
- ★ 53 Architecture — Layers, Ports and the Shape of a Service

## Part X · Performance, Profiling and Scale — 54–55 (2)

- ★ 54 Allocation, Escape Analysis and the Cost of Boxing
- ★ 55 Concurrency at Scale — Virtual Threads, Backpressure and Load Shedding

## Part XI · Algorithms, Complexity and Data Structures — 56–59 (4)

- ★ 56 Complexity as a Measurement, Not a Guess
- ★ 57 The Collections You Already Use, Measured
- ★ 58 Sorting, Searching and Hashing in the Real World
- ★ 59 Graphs, Priority Queues and Pathfinding as Data Structures

## Part XII · Where Next — Kotlin and Beyond — 60 (1)

- ★ 60 Where Next — Kotlin for a Java Developer, and What to Read Afterwards

---

## Why this is the same standard as C++

- **Two capstones at Python's scale.** CAPSTONE A (39) and CAPSTONE B (48) are held to the ~100 KB
  bar set by `python/chapters/30-capstone-studyhub.md` and `36-polish-packaging-capstone.md`.
- **JVM depth that is specific to Java.** Type erasure (11), the memory model (31), bytecode and
  `javap` (49), garbage collection (50), class loading (51) and the JIT (51, 54) are the material
  that makes the rest debuggable rather than magic.
- **Engineering, not just language.** Build tools (37), packaging and `jlink`/`jpackage` (38),
  end-to-end testing (36), profiling and allocation (54), load shedding (55),
  architecture (52–53) and algorithms (56–59).

## Deliberate choices, and what is contested

1. **No Spring, and no Maven Central dependency in the web track.** The JDK's own
   `com.sun.net.httpserver` is used instead, so chapters 25–39 are gated exactly like the rest of
   the book. Spring is named in prose as the industry default, not taught as the foundation.
2. **Kotlin gets one chapter, not two.** The extension is kept to a single chapter (67) so it does
   not dilute the Java material, and it is placed last rather than as a second track.
3. **The database chapters build the engine.** There is no JDBC driver in the JDK, and this track
   takes no third-party jars, so chapters 32–33 implement a small in-memory engine behind the JDBC
   interfaces by hand. The lesson that matters most — that `?` placeholders are what prevent SQL
   injection — survives intact, and the whole thing stays verifiable offline.
4. **Parts are named so that the six layers in `TRACK-STANDARD.md` have a home.** The layer audit
   matches on the *part title*, not on chapter names, so `VIII · Inside the JVM — How the Runtime
   Actually Works` is internals, `XI · Algorithms, Complexity and Data Structures` is cost, and so
   on. Renaming a part silently re-scores the whole track, so part titles are load-bearing.

## Optional further additions if wanted later

A dedicated **Java modules (JPMS) in depth** chapter, and a **desktop UI with JavaFX** chapter if
JavaFX is ever installed on the build machine — it is not present today, so such a chapter could not
be machine-verified and would have to be labelled as such.
