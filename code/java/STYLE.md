# Author style guide — READ BEFORE WRITING ANY CHAPTER

You are writing chapters of **Java Mastery**, a self-contained teaching book that takes someone who
has never compiled a Java program to building (a) a real command-line product, (b) a real web service
and (c) a complete game — all three with nothing but a JDK.

Voice: a sharp, patient senior engineer sitting next to the learner. Direct. No filler, no
"Great question!", no emoji, no marketing language. Explain *why*, then show *how*.

This book is the **third track** of the CODE platform. `code/python/` is the reference for structure,
tone and length; `code/cpp/` is the reference for a compiled language with a machine-checked fence
contract. Read both `STYLE.md` files and one chapter of each before starting.

## The one rule that matters most

**Every piece of code you teach must be compiled and run before it goes in.** A Java book that
teaches a snippet that does not build is worse than no book: the learner blames themselves, then
loses an hour, then trusts nothing else in the chapter. Wrong code in a textbook is a bug with a
human cost.

That rule is enforced mechanically, not by good intentions — see **The fence contract** below.
You do not get to decide that an example "obviously works".

## File format

Each chapter is one Markdown file in `chapters/`, named `NN-slug.md`.

Front matter (required, exact keys):

```
---
chapter: 2
part: 1
title: Primitives and References
summary: One or two sentences saying what the reader will be able to DO after this chapter.
minutes: 45
tags: [primitives, references, boxing, equality]
---
```

Part numbers:

```
0 = Start Here                    1 = I · Foundations
2 = II · Leveling Up              3 = III · Project 1 · Quill, a Command-Line Vault
4 = IV · Track A · Bulletin       5 = V · Track B · Ironhold
6 = VI · Appendices & Kotlin
```

## The fence contract

The fence info string carries a **language** and, optionally, a **directive**. The directive is what
makes the example verifiable. `code/java/tools/verify_examples.py` reads them.

| Fence | Meaning | What the harness does |
|---|---|---|
| ` ```java run ` | A **complete program**. | Writes it to a file named after its type, compiles with `javac -Xlint:all -Werror --release 21`, runs it, and compares stdout against the `text` fence that immediately follows (if there is one). |
| ` ```java run-files ` | A **multi-file listing**: several files in one block, each introduced by a `// ===== Foo.java =====` banner. | Writes every file, compiles them together, runs the class holding `main`. |
| ` ```java bad ` | **Intentionally wrong code.** | Asserts `javac` **rejects** it with a real `error:`. If it compiles, the harness fails — which means the "don't do this" example was not actually wrong. A following `text` fence is **verified**: the quoted words must appear in the real diagnostic, so you cannot paraphrase an error message. |
| ` ```java warn ` | Code the compiler **complains about but still builds**. | Compiles with `-Xlint:all` and **no** `-Werror`, then requires the `text` fence to appear in the diagnostic. Use this whenever the lesson is "the compiler warns you" rather than "it does not build". |
| ` ```java throw ` | A program that **must die** with a non-zero exit. | Compiles, then requires a non-zero exit **and** the `text` fence to appear in **stderr**. For the failures the *JVM* reports rather than the compiler: an uncaught `NullPointerException`, an `UnsupportedOperationException` from an immutable collection, a `ClassCastException` from an erased cast. |
| ` ```java compile ` | A complete program that must **build but not run** (opens a socket, needs input, is an interface, …). | Compiles only. |
| ` ```java ` | A **fragment** (a signature, a record body, two lines of a bigger idea). | Not compiled. **Use sparingly** — see below. |
| ` ```sh run ` | A **shell script**. | Runs with `sh` in an empty temp directory with the JDK on `PATH`, and compares stdout against the `text` fence that follows. Use it when the evidence is a *command* — a `curl` transcript, a `jar` transcript, a CLI driven with arguments, a `javac` error about **file names**. |
| ` ```sh run-project ` | A shell script that needs the chapter's project. | Same, but the directory is first seeded with the files of the most recent `-files` listing **in the same chapter**, and that listing is compiled into `out/`. |
| ` ```bash ` / ` ```text ` / ` ```java ` (bare) | Commands, output and fragments. | Not compiled. A shell fence with **no** directive is decoration, not a block: it is neither run nor counted as a fragment. `text` directly after a block is read as its expected output. |

Any directive may take a `-files` suffix: `run-files`, `bad-files`, `warn-files`, `throw-files`,
`compile-files`. The suffix changes only *how the block is built*, never what is asserted.

### A `text` fence belongs to the block directly above it

The parser attaches an expected output only when the `text` fence is the **next fence in the file**.
Blank lines are skipped; prose and other fences are not. So this is verified:

````
```java run
...
```

```text
the output
```
````

and this is **not**:

````
```java run
...
```

A paragraph explaining what you just saw.

```text
the output
```
````

In the second form the block reports `ran clean (no output fence to compare)` and the transcript is
unverified prose — while in the rendered book it looks exactly like a verified one. Nothing warns you.
This shipped once in the C++ track: a listing whose self-test transcript sat three paragraphs below
it, so 18 blocks read "all behaved as declared" with the chapter's most important transcript
unchecked. Write the output immediately under its block; put the discussion after it.

### Multi-file listings

A chapter about packages, interfaces or packaging cannot be verified by a single-file block. The
convention is a **banner** before each file, which is also a valid Java comment so the listing is
still exactly the code a reader would type:

    ```java run-files
    // ===== Note.java =====
    public record Note(String title, String body) {}

    // ===== Main.java =====
    public class Main { ... }
    ```

Rules for writing one:

- **Banners are listing separators, not file contents.** Say so in prose the first time a listing
  appears, because a `// ===== Makefile =====` line would be nonsense if pasted into one.
- Every file must be named. A `-files` block with no banner **fails** rather than being guessed at.
- **A public type's name must match its file name**, and the harness writes the file from the banner,
  not from the declaration. That means a listing with `// ===== Vault.java =====` above
  `public class Store` is a compile error — which is a lesson, not a bug, and worth teaching.
- All files are compiled together, so a missing definition is a **compiler** error, not a link error.
  Java has no separate link step; say so when you are contrasting with C++.

### Shell blocks

A quoted terminal transcript is a claim about what a command printed, and hand-copied transcripts are
wrong in exactly the way hand-copied anything is wrong. `sh run` exists so that transcripts are
checked like everything else.

Rules for writing one:

- **The script must be self-contained and stop what it starts.** A block that leaves a server
  listening will fail the *next* run for a reason unrelated to the code, and the harness kills it at
  `RUN_TIMEOUT` (20 s). Start background processes with `trap 'kill $pid' EXIT`, redirect their
  output to a file, and `wait` for them.
- **Do not print anything that is not stable.** An identity hash code (`[I@2a139a55`) changes between
  runs. So does the `Date:` header of an HTTP response, and so does a thread id. If a value is not
  reproducible, print something derived and stable instead — `xs.toString().startsWith("[I@")` is
  `true` forever — or teach it in prose with **no** output fence.
- **`sh run-project` seeds from the most recent `-files` listing in the same chapter**, so the block
  must come after the listing it uses.
- **Remember what the harness compares**: stdout only. `stderr` is invisible, so a transcript that
  shows a diagnostic must fold the streams (`2>&1`) inside the script. This is also how you verify a
  `javac` error whose text depends on a **file name**: the harness always names a program file after
  its type, so a file-name mismatch can only be shown from a shell block.

### Fragments and solutions are not verified, so you must verify them

A bare ` ```java ` fence is never compiled, and neither is anything inside a `:::solution` callout
unless it carries a directive. That is the largest unverified surface in a chapter, and the
`N/N blocks` line says nothing about it — a chapter can report every block green while a solution
teaches code that does not build.

Two habits, both cheap:

- **Apply every solution to a copy of the module and compile it.** Extract the code, patch it in with
  a script, build with the same flags, run it. In the C++ track this caught a suggested one-line patch
  that compiled, looked right, and silently corrupted valid input.
- **State the measurement next to the fragment.** If a solution's result was observed, put the
  observed values in the prose or a table. A table of measured inputs and outputs is honest evidence
  even when the code beside it is a fragment; a fragment with no evidence is a claim.

### Generate listings from the files, do not retype them

A multi-file listing is a copy of files that exist on disk. Retyping it invites a transcription error
that no gate will catch, because the harness compiles *the listing* — a typo that still compiles is a
silent divergence between what you verified and what you teach.

Write a small generator under `tools/gen/NN/` that reads the real files, compiles and runs the demos,
captures stdout, and splices both into the chapter. Two consequences worth having: the fences are
correct by construction, and re-running the generator after a code change updates the transcript
instead of leaving it stale.

## What the toolchain can and cannot prove

Measured on **Temurin JDK 21.0.12.1 (arm64 macOS)**. Do not assume these hold elsewhere; the harness
**probes** for the JDK rather than trusting a path, and reports `SKIPPED` (never "passed") when it
cannot run something.

| Capability | Status | Consequence for writing |
|---|---|---|
| `javac` / `java` / `jar` / `jwebserver` / `jlink` / `jpackage` | **present** | Packaging, HTTP and native images are all verifiable. Prefer the JDK's own `jar` over Maven for teaching. |
| Maven / Gradle | **not installed** | Never teach a `pom.xml` as the only way to build. Every project in this book builds with `javac` and ships as a JAR, so it is verifiable; mention Maven in prose as what industry adds. |
| `-Xlint:all -Werror` | works | The default for `run`. A `run` block with a raw type **fails**, so raw types belong in a `warn` block. |
| `javac -Werror` | **JDK 14+** | If you mention it, say which version got it. |
| `com.sun.net.httpserver` (module `jdk.httpserver`) | **present, no dependency** | Chapter 24 onward builds a real web service with zero third-party jars. This is the single biggest difference from a Spring tutorial, and it is why the track is verifiable offline. |
| `javax.swing` / `java.awt` | **present** | Track B renders into a `BufferedImage`, so its output is checkable as pixels. Never assert on a `JFrame`. |
| Headless rendering | `-Djava.awt.headless=true` works | `BufferedImage` + `Graphics2D` fill deterministically: a red 10×10 rect on white reads `ffff0000` at (0,0) and `ffffffff` at (20,15). Pixel assertions are stable; window assertions are not. |
| Uncaught exception | **exit code 1**, message on **stderr** | `throw` blocks. The message is precise: `Cannot invoke "String.length()" because "<local1>" is null`. Java 21's helpful NPE text is a feature worth teaching — but quote only the stable prefix, since `<local1>` depends on the source. |
| Public class / file name mismatch | **error**: `class Main is public, should be declared in a file named Main.java` | A file-name lesson can only be a `sh run` block — the harness always names a program file after its declared type. |
| Checked exception not handled | **error**: `unreported exception IOException; must be caught or declared to be thrown` | The canonical `bad` block for the exceptions chapter. |
| `o instanceof List<String>` | **error**: `Object cannot be safely cast to List<String>` | The cleanest proof that generics are erased. `List<String>` and `List<Integer>` share one runtime class (`true`, measured). |
| Raw type | **warning** `[rawtypes] found raw type: List` | A `warn` block, never `run`. |
| Unchecked cast | **warning** `[unchecked] unchecked cast` | A `warn` block. `@SuppressWarnings("unchecked")` silences it — show the annotation, then say what it actually promises. |
| `int instanceof Integer` | **error**: `unexpected type … required: reference, found: int` | A `bad` block. `var n = 10` makes `n` an `int`, not an `Integer`, and `instanceof` needs a reference type. |
| String interning | **measured** | `"ab" == "a" + "b"` is `true` (constant folding), `"ab" == new String("ab")` is `false`, `"ab" == "a".concat("b")` is `false`. This is why `==` on strings is a bug that sometimes works. |
| `Integer` cache | **measured**: 127 caches, 128 does not | `Integer p = 127, q = 127; p == q` is `true`; the same code with 128 is `false`. Always `.equals()`. |
| Integer overflow | **measured, silent** | `Integer.MAX_VALUE + 1` is `-2147483648` and `1_000_000 * 1_000_000` is `-727379968`. No exception, no warning — the sharpest argument for `Math.addExact`. |
| `int[]` `toString()` | **`[I@2a139a55` — unstable** | Never put an array's `toString()` in a `text` fence. Use `Arrays.toString`, or assert the prefix. |
| Identity hash codes, `Date:` headers, thread ids | **unstable** | Filter them out of any transcript before it becomes a fence. |
| Virtual threads (Java 21) | **present** | `Executors.newVirtualThreadPerTaskExecutor()` runs and is verifiable. Teach it, and say plainly that it is 21+. |
| Text blocks (`"""`) | **present** | Use them for embedded HTML and JSON rather than concatenated strings. |
| JUnit | **not installed** | Testing chapters build a tiny assertion harness by hand. That is honest here: it is verifiable, and it teaches what JUnit does. Say in prose what a real project would use. |
| JDBC drivers | **not installed** | The JDK ships `java.sql` (the API) and no driver, and this track takes no third-party jars. Database chapters build a small in-memory engine behind the JDBC interfaces by hand. That is verifiable offline, it teaches what a driver actually does, and the `?`-placeholder lesson — the one that prevents SQL injection — survives intact. Name SQLite, H2 and PostgreSQL in prose as what a real project would use. |
| JavaFX / LibGDX | **not installed** | Do not make them load-bearing. Track B uses Swing/AWT, which is in the JDK. |

**Never write a fragment when a program will do.** A fragment teaches the shape; a program teaches
the shape *and* proves it. Reserve bare ` ```java ` for things that genuinely cannot stand alone,
such as an interface's declaration or a signature being discussed.

**Output fences must be exact.** If the program prints `7 / 2     = 3`, the `text` fence must say
exactly that — same spacing, same case. The harness diffs them literally, because a reader copying
your code and getting different output is exactly the failure this book cannot afford. When output is
machine- or version-dependent, do not invent a number: print something the JDK fixes, or say the
target in prose.

**Line numbers and error text are quoted from real runs.** If you show a compiler error, paste the
one you actually got, not a paraphrase. The `bad` directive exists to keep that honest.

## Required chapter skeleton

1. Opening paragraph — no heading. 3–5 sentences: what problem this chapter solves and why it
   matters in real code.
2. `##` sections teaching the material (use `###` for sub-topics). Order: concept → smallest
   working example → what changed → when you'd use it.
3. At least one `:::scenario` callout with a `:::solution` — a realistic workplace situation and
   how a Java developer actually handles it.
4. At least one `:::pitfall` naming a mistake learners actually make.
5. `## Key takeaways` — 4–8 bullets, each a complete, checkable statement.
6. `## Practice` — 4–6 exercises as checkbox list items: `- [ ] Build a ...`
   Easiest → hardest. Doable with only what has been taught so far plus earlier chapters.
7. `## Solutions` — a `:::solution Exercise 1` block per exercise, with working code and 1–3
   sentences of reasoning. Solution code carries `run` too wherever it is a complete program.

## Markdown conventions the build script understands

- Headings: `##`, `###`, `####` only. Never `#` (the title comes from front matter).
- Callouts — title after the kind:

  `:::note This is the heading`
  body text, may contain code fences, lists, paragraphs
  `:::`

  Kinds: `note`, `tip`, `warning`, `danger`, `pitfall`, `scenario`, `solution`, `try`.
- Inline code with single backticks; bold with `**`; links as `[text](https://...)`.
- Tables with standard pipe syntax.
- Lists: `-` for bullets, `1.` for ordered. Indent 2 spaces for nesting.
- Do **not** use raw HTML, `<details>`, footnotes, or emoji.

## Content rules for Java

- **Target Java 21**, and say so. Every chapter is compiled with `--release 21`, so anything older
  than 21 is fair game and anything newer is not. Name the version when a feature needs one
  (records 16, sealed 17, virtual threads 21, pattern-matching `switch` 21).
- **Teach the JVM, not just the syntax.** The reader should know why `javac` produces `.class`
  files, what `java` does with them, and why the same file runs on another machine. That is this
  track's reason to exist next to Python's and C++'s.
- **No third-party dependencies anywhere in the book.** No Maven, no Spring, no JUnit, no JSON
  library. Every chapter — including the web service and the game — builds with the JDK alone, so
  every line is verifiable on the reader's machine and on this one. Mention the real-world library
  in prose when it matters, and say what it saves you.
- **Never teach `==` on objects as if it worked.** Where the mistake is instructive, show it under
  `run` with the measured `true`/`false`, then show `.equals()`. "It happened to work for 127" is
  not a lesson; "the cache makes small values alias and 128 breaks" is.
- **Checked exceptions are Java's signature feature** — teach them as a design decision, with the
  cost (signature pollution, `throws Exception`) stated honestly, not as gospel.
- **Cross-reference chapters in prose** ("we'll need this in Chapter 29 when the web app stores
  sessions"). Do not link with URLs.
- Length: 1000–1800 words of prose plus code. Dense is fine; waffle is not.
- Never say "in this chapter we will learn". Just teach it.

## Definition of done for a chapter

1. Every `run` block compiles clean under `-Xlint:all -Werror` and its output matches the `text`
   fence.
2. Every `bad` block is rejected by `javac`; every `warn` block produces the promised diagnostic;
   every `throw` block dies with the promised message.
3. `python3 tools/verify_examples.py <chapter-slug>` reports zero failures.
4. Front matter present with all six keys; part number matches the chapter's position.
5. One `:::scenario` + `:::solution`, one `:::pitfall`, `## Key takeaways`, `## Practice`,
   `## Solutions` all present.

Before publishing a batch, run `python3 tools/verify_examples.py --self-test`. It must print
`self-test PASSED`, which means `fixtures/good.md` still passes **and** `fixtures/bad.md` still fails
with exactly the expected number of failures. If the self-test fails, the harness has gone blind and
every chapter it has ever approved is suspect. When you add a new directive, add a `must_pass` case
to `good.md` and a `must_fail` case to `bad.md`, and bump `EXPECTED_BAD_FAILURES`.
