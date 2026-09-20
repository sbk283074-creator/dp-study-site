# Author style guide — READ BEFORE WRITING ANY CHAPTER

You are writing chapters of **C/C++ Mastery**, a self-contained teaching book that takes someone
who has never compiled anything to building (a) a C systems tool, (b) a real C++ web service and
(c) a complete C++ game.

Voice: a sharp, patient senior engineer sitting next to the learner. Direct. No filler, no
"Great question!", no emoji, no marketing language. Explain *why*, then show *how*.

This book is the **second track** of the CODE platform. The first track (`code/python/`) is the
reference for structure, tone and length. Read its `STYLE.md` and one chapter before starting.

## The one rule that matters most

**Every piece of code you teach must be compiled and run before it goes in.** A C++ book that
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
chapter: 7
part: 1
title: Pointers and Memory
summary: One or two sentences saying what the reader will be able to DO after this chapter.
minutes: 45
tags: [pointers, addresses, dereference, nullptr]
---
```

Part numbers:

```
0 = Start Here          1 = I · C Foundations        2 = II · C Advanced
3 = III · Project 1     4 = IV · Transition to C++   5 = V · Track A · C++ Web Service
6 = VI · Track B · C++ Game                          7 = VII · Appendices
```

## The fence contract

The fence info string carries a **language** and, optionally, a **directive**. The directive is
what makes the example verifiable. `code/cpp/tools/verify_examples.py` reads them.

| Fence | Meaning | What the harness does |
|---|---|---|
| ` ```cpp run ` | A **complete program**. | Compiles with `clang++ -std=c++17 -Wall -Wextra`, runs it, and compares stdout against the `text` fence that immediately follows (if there is one). |
| ` ```cpp run-san ` | A complete program that demonstrates **memory or UB behaviour**, and must run **clean**. | Same, plus `-fsanitize=address,undefined`. Use for anything about pointers, `new`/`delete` or out-of-bounds. |
| ` ```cpp run-san-catch ` | A program that **must be caught** by the sanitizer. | Requires a non-zero exit **or** a sanitizer report, and requires the `text` fence to appear inside that report. |
| ` ```cpp run-san-leak ` | A program that **must leak**. | Same, but leak detection does not exist on macOS — there it is reported **SKIPPED**, never "passed". |
| ` ```cpp compile ` | A complete program that must **build but not run** (needs input, opens a socket, is a header, …). | Compiles only. |
| ` ```cpp bad ` | **Intentionally wrong code.** | Asserts the compiler **rejects** it with a real `error:`. If it compiles, the harness fails — which means the "don't do this" example was not actually wrong. A following `text` fence is **verified**: the quoted words must appear in the real diagnostic, so you cannot paraphrase an error message. |
| ` ```cpp warn ` | Code the compiler **complains about but still builds** (`-Wformat`, `-Wunused-variable`, …). | Compiles with `-Wall -Wextra` and **no** `-Werror`, then requires the `text` fence to appear inside the diagnostic. Use this whenever the lesson is "`-Wall` catches it" rather than "it does not build". |
| ` ```cpp ` | A **fragment** (a signature, a struct body, two lines of a bigger idea). | Not compiled. **Use sparingly** — see below. |
| ` ```c run ` / ` ```c bad ` / … | The same directives for C. | Same, via the **C driver** (`clang`) with `-std=c17`. |
| ` ```bash ` / ` ```text ` / ` ```makefile ` | Commands and output. | Not compiled. `text` directly after a `run` block is read as its expected output. |

### What the toolchain can and cannot prove

Measured on Apple clang 21 (arm64 macOS). Do not assume these hold elsewhere; the harness
**probes** for leak detection rather than trusting the platform name.

| Capability | Status | Consequence for writing |
|---|---|---|
| ASan heap-buffer-overflow, use-after-free | works | Use `run-san-catch` freely. |
| **ASan leak detection** | **unavailable on macOS** | A leak demo is `run-san-leak`, which reports SKIPPED here. **Say so in prose**: tell the reader to run it on Linux or under `valgrind`. Never write "you will see this" about a leak report without naming the platform. |
| UBSan | works, but **the exit code stays 0** | A UB demo must be `run-san-catch`, never `run`. A plain `run` block with UB would pass on exit code alone. |
| `valgrind` | not installed | Do not make it the only suggested tool. |
| `cmake` | not installed | A CMake chapter cannot be machine-verified here — mark it `compile`-free and say so, or teach `make` first, which **is** verifiable. |
| `-Wimplicit-fallthrough` | **not** enabled by `-Wall -Wextra` on Apple clang | A switch fall-through cannot be a `warn` block — the harness would see silence and fail. Teach the *behaviour* with `run`, and mention the flag in prose. |
| Incompatible pointer types, `double *p = &x;` | **warning in C, error in C++** | The same "don't do this" example must be `warn` in a C chapter and `bad` in a C++ chapter. Measured, not guessed. |
| `sizeof` on an array *parameter* | warning `-Wsizeof-array-argument` | A `warn` block, never `run`: `run` builds with `-Werror`, so it would report "does not compile" instead of teaching the lesson. |
| `long double` | 8 bytes on arm64 macOS, 16 on x86-64 Linux | The sharpest reason never to print a size without naming the target. |
| SDL2 / Raylib / GLFW | not installed | Track B cannot be compiled here. Any code in those chapters must be labelled **not machine-verified** — the project's existing rule. |

**Never write a fragment when a program will do.** A fragment teaches the shape; a program teaches
the shape *and* proves it. If a concept needs three lines of context, write the complete program —
that is what the reader will actually type. Reserve bare ` ```cpp ` for things that genuinely
cannot stand alone, such as a header's contents or a function signature being discussed.

**Output fences must be exact.** If the program prints `size of int = 4`, the `text` fence must say
`size of int = 4` — same spacing, same case. The harness diffs them literally, because a reader
copying your code and getting different output is exactly the failure this book cannot afford.
When output is machine-dependent, say so in prose and mark the fence ` ```text ` with a note —
do not invent a number. **Prefer printing values the standard fixes** (`sizeof(int)` on the
target, `CHAR_BIT`) and **say the target** when it matters.

**Line numbers in errors are quoted from real runs.** If you show a compiler error, paste the one
you actually got, not a paraphrase. The `bad` directive exists to keep that honest.

## Required chapter skeleton

1. Opening paragraph — no heading. 3–5 sentences: what problem this chapter solves and why it
   matters in real code.
2. `##` sections teaching the material (use `###` for sub-topics). Order: concept → smallest
   working example → what changed → when you'd use it.
3. At least one `:::scenario` callout with a `:::solution` — a realistic workplace situation and
   how a C or C++ developer actually handles it.
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
- No `#include <bits/stdc++.h>` — it is a GCC-only header that does not exist on clang or MSVC, and
  teaching it produces code that fails on the reader's machine.

## Content rules for C and C++

- **Name the target.** Most of this book assumes `clang++`/`g++` on macOS or Linux with C++17 as
  the floor. Say when something is platform-specific. `sizeof(long)` is 8 on Linux and macOS but 8
  on 64-bit Windows *only* for `long long` — do not assert it without naming the platform.
- **Never teach undefined behaviour as if it worked.** Where a mistake is instructive, show it
  under `run-san` and show the sanitizer's verdict. "It happened to print 0 on my machine" is not
  a lesson; "the sanitizer catches it" is.
- **Prefer `std::` explicitly** in early chapters (`std::cout`, `std::string`). Introduce
  `using namespace std;` only to explain why you should not use it at file scope.
- **Memory is the whole point of this track.** Every allocation chapter must show the failure mode
  and the tool that catches it (ASan, UBSan, Valgrind, `-Wall -Wextra`).
- **Say what the compiler will say.** When a construct is rejected, quote the real diagnostic.
- Cross-reference chapters in prose ("we'll need this in Chapter 24 when we own memory through
  `std::unique_ptr`"). Do not link with URLs.
- Length: 1000–1800 words of prose plus code. Dense is fine; waffle is not.
- Never say "in this chapter we will learn". Just teach it.

## Definition of done for a chapter

1. Every `run` / `run-san` block compiles clean under `-Wall -Wextra` and its output matches the
   `text` fence.
2. Every `bad` block is rejected by the compiler.
3. `python3 tools/verify_examples.py <chapter-slug>` reports zero failures.
4. Front matter present with all six keys; part number matches the chapter's position.
5. One `:::scenario` + `:::solution`, one `:::pitfall`, `## Key takeaways`, `## Practice`,
   `## Solutions` all present.
