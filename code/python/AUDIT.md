# Python track — audit against the C/C++ standard

Measured 2026-09-21 against `code/cpp/`, which is the reference standard for this platform.
Every number below was produced by a script run against the files in `chapters/`; nothing here
is an impression. Commands are reproducible from the descriptions given.

**Status: the check is complete and the edit has begun.** A harness now exists and passes its
self-test; 58 blocks are machine-verified and green; 11 genuine content defects were found and
fixed; 46 transcripts were promoted to gates. What remains is bulk conversion, and it is now
sized rather than guessed. See "Where this leaves the track".

## The headline

**The Python track had no verification infrastructure at all.** That is no longer true, and the
gap is now measurable in three numbers:

| | Python (before) | Python (now) | C / C++ |
|---|---|---|---|
| Verification harness | **none** | `tools/verify_examples.py` | `tools/verify_examples.py` |
| Harness self-test | n/a | **9 good / 9 caught, PASSED** | `self-test PASSED` |
| Fixtures pinning pass/fail | none | `fixtures/good.md`, `fixtures/bad.md` | same |
| Blocks machine-verified | **0** | **58** | **487** |
| Fences carrying a directive | **0** | 58 | 502 |
| `text` fences treated as claims | **0 of 263** | 0 of 263 | all attached ones |

The C++ track enforces its correctness mechanically, and its `STYLE.md` says why that matters:

> in the rendered book it looks exactly like a verified one. Nothing warns you.

The Python track had the same exposure: 263 `text` fences, every one an unchecked promise about
what a program prints, rendering identically to a checked one. The harness now exists so that
promises *can* be checked; converting the backlog is the next section.

`STYLE.md` has been given the directive contract the track was missing, including the two traps
that cost real defects in this pass (comments on output lines, and the REPL's double-`repr`).

## Two harness bugs found by measuring, not by reading

Both were found by running the harness over the corpus, and both would have caused me to "fix"
perfectly good book text. They are the reason the failure count moved from 70 to 3 without 60
chapter edits.

**1. `split_repl` destroyed continuation indentation.** It stripped the prompt with
`line[3:].lstrip()`. The real prompts are `>>> ` and `... ` — three characters *plus one space*
that belongs to the prompt. Everything after that space is the reader's indentation. Flattening
it turned every `for`, `if` and `def` in every transcript into an `IndentationError`. This alone
made 20 correct transcripts look like book defects. Fixed by stripping the prompt and **at most
one** space; pinned by `fixtures/good.md` and by a `must_fail` case that proves indentation is
still genuinely required.

**2. A compound statement needs the second Enter.** `codeop.compile_command(..., symbol="single")`
reports `for ch in "python":\n    print(ch)` as *incomplete* without a trailing newline, so the
console buffered it and the block appeared to print nothing. The harness now terminates each
entry the way a reader does. When the console is *still* waiting after a whole entry, the
transcript itself is truncated — it is missing its `...` lines — and that is now reported as the
specific defect it is rather than as an empty-output mismatch.

A third, smaller addition: a bare `...` line in a documented traceback now means "frames elided",
the convention every Python book uses, matched by `glob_lines_match`. It is narrow — it does
nothing unless the fence actually writes an elision, and a `must_fail` fixture pins that the
elision cannot swallow a wrong exception line.

## What the 96 untagged transcripts actually are

This is where the first reading of the data was wrong. "70 of 97 transcripts fail" suggested a
track full of bad transcripts. Classifying each failure by *cause* — harvesting bound names with
`ast`, per chapter, in document order — gives a different answer:

| Cause | Count | Is the book wrong? | Action |
|---|---|---|---|
| Passes as-is | 46 | No | **Tagged `repl`; now a gate** |
| Worked answer to an exercise | 33 | No — illustration | Leave untagged |
| Session fragment (name from an earlier fence) | 14 | No — harness limit | Needs session continuity |
| Environment-dependent | 3 | No | Leave untagged |
| Genuine content defect | 11 | **Yes** | **Fixed** |

The 33 "exercise answers" are mostly `38-practice-problems.md`, where a fence shows what
`fizzbuzz(15)[11:]` returns. `fizzbuzz` is the exercise the reader is about to write. That is
illustration, not a session, and tagging it `repl` would be a category error — the harness cannot
and should not replay it. The 14 session fragments are the same shape but recoverable: the name
*is* defined, just in a previous fence, and the harness starts a fresh console per fence.

## The 11 content defects, and how each was found

All were found by the harness on its first real application, and all are fixed and re-verified.

| File | What was wrong |
|---|---|
| `03-strings` | `f"{name!r}"` shown as `"'Ada\t'"`; the REPL reprs the *string* `!r` returned, so it prints `"'Ada\\t'"` |
| `03-strings` | `str + bytes` shown as `TypeError: can't concat str to bytes`; that is the Python 2 wording |
| `05-functions` | `sorted(names, key=lambda n: n[-1])` shown alphabetical; the key is the **last letter**, so `['ada', 'grace', 'alan']` |
| `06-collections` | `tasks.pop(0)` shown printing nothing; `pop` returns the item |
| `06-collections` ×3 | a comment trailing an **output** line — the REPL does not echo comments |
| `14-iterators` | `max()` on an empty sequence: message is `max() iterable argument is empty` |
| `15-decorators` | `sorted(..., key=lambda s: s[-1])` shown `['ccc', 'a', 'bb']`; correct is `['a', 'bb', 'ccc']` |
| `17-text-time-numbers` | `f"{0.1:.30f}"` shown to 33 decimal places; `.30f` gives 30 |
| `17-text-time-numbers` | `sum([0.1] * 10) == 1.0` shown `False` |
| `37-scenario-cookbook` | the same `sum([0.1] * 10)` claim |

The last two are the most interesting. Since **Python 3.12**, `sum()` adds floats with
compensated (Neumaier) summation, so `sum([0.1] * 10) == 1.0` is now `True` — it was `False`
through 3.11. `+` is still uncompensated, so `0.1 + 0.2 == 0.3` remains `False`. The claim was
not wrong when written; it aged. Chapter 17 now shows `True` *and* explains why relying on it is
a trap, which is a better lesson than the original line was. Chapter 37, where the point is
"use `Decimal` for money", now uses `0.1 * 3 == 0.3`, which is `False` on every version.

## Where this leaves the track

`python3 tools/verify_examples.py` — **all 58 blocks behaved as declared**, across all 40 chapters,
self-test green. That is the new floor. The remaining work, measured:

| Target | Count | Effort |
|---|---|---|
| Untagged programs **with** an output fence, parsing cleanly | **171** | Tag `run`; each will surface a real defect or pass. Highest value. |
| Untagged programs with no output fence, parsing cleanly | 675 | Tag `run` to assert they execute cleanly. Bulk, low risk. |
| Session fragments | 14 | Needs a `repl-session` continuity feature in the harness |
| Worked answers | 33 | Leave as illustration; consider a bare-fragment convention |
| Non-parsing, no output fence | 13 | Includes the 2 intentional conflict demos in `22-git-quality-packaging.md` and 2 hybrid fences |
| Environment-dependent | 3 | `import requests`; `import noisy` (needs a file seeded beside it); `sys.path` (machine-specific) |

The 171 are the reason the harness was worth building: each one converts a `text` fence from prose
into a checked claim. Extrapolating from this pass, roughly one in fifteen will be wrong — a
defect rate that had never been measured because nothing had ever run the code.

One feature gap worth naming: `import noisy` needs a file written beside the transcript before it
runs. The C++ harness has `-files` and `run-files` for exactly this; the Python harness does not
yet. Two other blocks are legitimately illustrative and should stay untagged: `import requests`
(needs a package and a network) and `for entry in sys.path` (prints a machine-specific list).

## Method, so this can be re-run

- Fence extraction: `tools/verify_examples.py::parse_chapter`. A fence closes on a line whose
  stripped form equals the opening backtick run, and a following `text` fence is consumed as the
  block's expected output.
- Classification of transcripts: for each failure, harvest names bound in *earlier* fences of the
  same chapter with `ast` (`Name`, `FunctionDef`, `ClassDef`, `Import`), then check whether the
  `NameError` name appears there. `seen` → session fragment; bound in the *same* fence →
  genuine defect; neither → worked answer.
- Sizes: `wc -c` / `wc -w` over `chapters/*.md`. Counts for the C++ column: the same fence scanner
  over `code/cpp/chapters/`, plus its `verify_examples.py` (no filter).

**Two cautions for anyone re-running this.**

First, an early pass reported "0 fences fail to parse", which was wrong: the block containing
`>>>>>>> add-units` starts with `>>>`, so a heuristic looking for `>>>` anywhere classified a
merge conflict as a REPL transcript and skipped the parse attempt. Anchor such a check to the
first non-blank line only.

Second, and more expensive: the first transcript survey reported 70 failures and the corrected
figure is 3. A harness bug is indistinguishable from a book bug until you read the failure by
hand. Both bugs above were found by inspecting a failure whose *diagnosis* was implausible — a
`for` loop that "prints nothing" — rather than by trusting the total. Any audit of this kind
should assert on a block it knows the answer for before trusting its own numbers.
