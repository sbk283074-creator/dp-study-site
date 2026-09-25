#!/usr/bin/env python3
"""Generate chapters/20-the-project-quill-a-command-line-vault.md.

    python3 tools/gen/20/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "20-the-project-quill-a-command-line-vault.md")

BLOCKS = {
    "skeleton": gen.run("Skeleton.java"),
    "note": gen.run_files(["Note.java", "NoteDemo.java"]),
    "commands": gen.run_files(["Commands.java", "CommandsDemo.java"]),
    "badswitch": gen.bad("BadSwitch.java",
                         "the switch expression does not cover all possible input values"),
    "vault": gen.run_files(["Note.java", "Vault.java", "VaultDemo.java"]),
    "project": gen.run_files(["Main.java", "Note.java", "Vault.java"]),
    "drive": gen.sh("drive.sh", "run-project"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 20
part: 3
title: The Project — Quill, a Command-Line Vault
summary: Start the project this part builds — a note vault driven from the command line — and settle its two contracts, the exit codes and the file format, before writing any of its features.
minutes: 55
tags: [cli, project, records, sealed types, exit codes, files]
---

Everything in Part II was a technique. This part is a program: **Quill**, a vault of short notes that
you drive from a terminal. It is small on purpose — four commands and one file — and it is the right
first project because everything it does is checkable. A command-line program reads arguments, writes
a file and prints text, and all three can be verified by a machine, which is why every transcript in
this part is a real one. By the end of Chapter 24 Quill will be a program you would not be embarrassed
to use. This chapter builds its skeleton and, more importantly, settles the two contracts that every
later chapter will have to honour.

## A program's exit code is part of its interface

A command-line program talks to the world in three ways: its arguments, its standard output, and its
**exit code**. The first two are visible when you run it by hand. The third is invisible, and that is
exactly why it is the one that gets neglected — and the one that a shell script depends on, because
`if quill list; then` is testing nothing else.

So the exit codes are decided first, before any feature exists, and they are written down as constants:

```text
0   success
2   unknown command
3   a required argument is missing
```

The numbers are not arbitrary. `0` for success is the one universal convention. `2` and `3` are above
`1` because `1` is reserved for "something went wrong that we did not anticipate" — a file that could
not be read, a disk that is full. A caller can then tell "you typed the command wrong" (my fault, do
not retry) from "the vault is unreadable" (not my fault, maybe retry) without parsing English.

@@skeleton@@

Read the shape of that `run` method, because it is the shape of the whole project.

It takes the arguments **and a `PrintStream`**. It does not touch `System.out`. That one decision is
what makes the contract testable: the demo `main` above hands `run` a `ByteArrayOutputStream` for each
invocation, which is why it can print `0 byte(s) written` for `list` without a single character
reaching the terminal. This is the dependency injection of Chapter 19 again, applied to output rather
than to a clock, and it will pay for itself every time a chapter needs to assert on what a command
printed.

The `switch` is an expression, so every arm has to produce a value and the compiler will not let one
fall through. `add` needs three arguments — the command, a title and a body — and the whole arm is the
ternary that checks it.

The measured table is the contract:

```text
(no arguments)                 exit 0, 172 byte(s) written
list                           exit 0,   0 byte(s) written
add                            exit 3,   0 byte(s) written
add Groceries milk and eggs    exit 0,   0 byte(s) written
frobnicate                     exit 2,   0 byte(s) written
```

The bare invocation writes 172 bytes — the help text — and exits **0**. That is a choice worth stating
plainly, because `git` does the opposite: running `git` with no arguments prints the usage and exits 1.
The argument for `0` is that the user asked for something reasonable and got it; nothing failed. The
argument for `1` is that a script which runs `quill` to check the tool exists should not see a success.
Pick one and write it down — what you must not do is leave it to whichever branch happens to be first.

:::warning
`System.exit` does not flush your output streams. A program that prints a result and then exits can
lose the last buffer, and the bug appears only when the output is large enough to fill it. Flush
before you exit, or avoid `System.exit` on the success path altogether. Quill does the second: `main`
returns normally when the code is `0`, and only calls `System.exit` when it must report a failure.
:::

## The unit of the vault is a record

A note has an id, a title and a body, and nothing else. Chapter 16 introduced records as classes the
compiler writes for you; here is one doing real work:

@@note@@

Two methods and one constant, and between them they define the file format. `render` turns a note into
a line; `parse` turns a line back into a note. **A format is the pair of them, and they are only
correct together.** Writing one without the other is how formats drift.

The interesting detail is the `3` in `line.split(SEP, 3)`. Without it, `split` would break the line
into as many pieces as there are tabs, and a note whose body contains a tab would come back in
fragments. The limit says *"split into at most three fields"*, so everything after the second tab is
the body — and the demo proves it:

```text
line        = 1\tGroceries\tmilk\teggs
round trip  = true
body        = milk\teggs
```

The body survived a tab. `round trip = true` means `parse(render(note)).equals(note)`, which is the
property that makes a format usable: what you write is what you read.

Now look at the second half of the same transcript, and watch the same format fail:

```text
title in    = A\tB
title out   = A
body out    = B\tx
```

A tab in the **title** does not survive, and the reason is that `split` works from the left. The first
field is the id, the second ends at the next tab — so `A` becomes the title, and the rest of what was
the title is now the head of the body. Nothing threw. Nothing warned. The note was silently rewritten.

That is not a bug in `parse`; `parse` did exactly what the format says. It is a hole in the format, and
it can only be closed by refusing the input — a title may not contain a tab, enforced where the note is
constructed. Chapter 16 showed where that goes (a compact constructor) and Chapter 22 will show what
happens when you decide instead to escape the separator rather than forbid it.

## A command is a sealed type, so the compiler can check the switch

The dispatcher in `Skeleton` switches on a `String`. That works, and it has a weakness: the compiler
knows nothing about the set of commands. Misspell `"lisst"` in a `case` label and you get a command
that can never be reached, with no complaint from anyone.

Chapter 16's sealed types fix exactly this. A command becomes a value, and the set of commands becomes
a closed hierarchy the compiler can see:

@@commands@@

`Commands` is sealed and `permits` exactly four records, so the compiler knows the complete list. The
`describe` switch has **no `default` arm**, and that is the point: javac can prove the arms cover every
permitted type, so it does not ask for one. A `default` here would not be defensive; it would throw
away the only guarantee the sealed keyword bought you.

The four lines of output are the proof that each command is a distinct value carrying its own data:

```text
Add          add "Groceries"
ListNotes    list
Show         show #7
Help         help
```

Note that `ListNotes` and `Help` are records with no components. They are still distinct types, which
is what lets them appear as separate arms — a fact an `enum` could not express, because `Add` carries a
title and a body while `Help` carries nothing.

## What the compiler does when you forget one

The guarantee is worth seeing fail, because the failure is the feature:

@@badswitch@@

`Shape` permits two records. The switch handles `Circle` and stops. javac refuses the file, and the
sentence it produces — **the switch expression does not cover all possible input values** — is the
entire reason to prefer a sealed hierarchy over a `String` and a `default`.

This is what Chapter 16 meant by closing a hierarchy. Adding a fifth command to Quill in Chapter 23
will break every switch that describes a command, at compile time, in the file that needs the new arm.
The alternative is a `default` arm that quietly does something wrong at runtime, and you find out from
a user.

:::pitfall
**A `default` arm in a switch over a sealed type is a silent downgrade.** It compiles, it looks
prudent, and it converts a compile error into a runtime surprise: add a permitted subtype and the new
case falls into `default` instead of stopping the build. If the switch is meant to be exhaustive, say
so by leaving the `default` out and let javac hold you to it.
:::

## The vault is a file, and the file is the state

There is no database in this project and no in-memory index. The state of a vault is one text file,
and every read goes to disk. That sounds slow and it is, by a few milliseconds; it is also the reason
the whole thing can be inspected, copied and repaired with `cat` and a text editor, which is worth far
more at this size.

@@vault@@

`read` is the only place that knows how to turn the file into notes, and it is careful about the two
cases that bite: the file may not exist yet, and it may contain a blank line. A missing file returns an
empty list rather than throwing, because "I have no notes" and "I have no vault" are the same thing to
a reader.

`append` uses `StandardOpenOption.APPEND`, so writing note number four hundred does not rewrite the
first three hundred and ninety-nine. It also calls `Files.createDirectories(home)` first, so the very
first `add` on a fresh machine creates `vault/` without a separate setup step.

The demo shows the file as it really is — tabs and all — and the count on disk:

```text
empty        = []
after two    = 2 note(s)
next id      = 3

notes.tsv, tabs shown as \t:
1\tGroceries\tmilk and eggs
2\tReading\tchapter 20

lines on disk= 2
```

`nextId` is the method to look at twice. It returns the **highest existing id plus one**, not the
number of notes plus one. Those agree until something is deleted, and then they disagree in the worst
possible way: after deleting a middle note, `size + 1` names a note that already exists. Solution 4
measures it.

## The three files, wired together

Here is the whole program as it stands. `Main.java` is the entry point, `Note.java` is the value and
`Vault.java` is the storage, and the arrows only point one way: `Main` knows about `Vault`, `Vault`
knows about `Note`, and `Note` knows about nothing.

@@project@@

Read the `main` method as three lines of policy. It resolves where the vault lives, it delegates every
decision to `run`, and it converts the returned code into a process exit. Everything interesting is in
`run`, which takes the home directory and both streams as parameters — so a test, or the next chapter,
can point it at a temporary directory and capture what it printed.

When this listing is compiled and run with no arguments it prints the help and exits 0, which is why
the transcript under it is the usage text and nothing else.

## Driving it

Arguments are the last piece, and the only honest way to show them is to run the program. The block
below compiles the listing above into `out/` and then calls it six times. The shell function folds the
error stream into the output with `2>&1` — without it, every diagnostic would be invisible here — and
prints `$?`, the exit code of the command that just ran:

@@drive@@

Six invocations, and the transcript is the specification:

- `list` on an empty vault prints `no notes yet` and exits `0`. An empty vault is not an error.
- Two `add` calls each print a confirmation naming the id they assigned, and `list` then shows both.
- `frobnicate` prints `quill: unknown command 'frobnicate'` and exits `2`.
- `add Untitled` prints the usage for that command and exits `3`.

That last line is the difference between a usable tool and an annoying one. `quill: missing argument;
usage: quill add <title> <body>` tells the user what was wrong *and* what to type instead. The
message is on the error stream, so a script that captures output does not have to filter it out.

:::scenario A note that came back with the wrong title

Quill is in use. A user copies a title out of a spreadsheet — the cell reads `Groceries` and a second
column, and what the clipboard actually contains is `Groceries\tand more`, because the spreadsheet puts
a tab between the columns. The note is added, and a week later the user reports that the vault has
split their note in two: the title is `Groceries` and the body begins `and more`.

:::solution
The format is `title` + tab + `body`, and the title arrived containing a tab. Everything downstream
behaved correctly: `render` wrote the tab, `parse` split on the first tab it found, and the title it
returned was genuinely the text before that tab.

The fix is not in `parse`. It is at the boundary, where the note is constructed, and it is the compact
constructor from Chapter 16:

@@scenario@@

The unguarded record demonstrates the corruption — the title read back is `Groceries` and the body
read back is `and more\tmilk` — and the guarded one refuses the same input with a message naming the
problem. The value of doing it in the constructor rather than in `main` is that there is no way to
build a bad note: every path that constructs one goes through the same check, including paths that do
not exist yet.

**The general rule: a format has a set of strings it can represent, and the strings it cannot represent
must be rejected where they enter the system, not discovered where they leave it.** The tab is this
format's example. Every format has one — a comma in a CSV field, a quote in a JSON string, a newline in
an HTTP header.
:::

## Solutions

### 1. The exit-code contract, written as a table

The contract in this chapter was three constants and a promise. A promise is not a test. Here it is as
data, checked by a loop:

@@sol1@@

`passed 8 of 8`. The value of writing it this way is that the contract is now *in* the test: eight
`Case` records, each with the arguments and the code the chapter claims. Adding a command to Quill
means adding its rows, and a row that disagrees with the implementation fails the build.

Note the last two rows. `add` with no title and `add` with a title but no body are both `MISSING_ARG`
— the argument count is checked once, not per-argument. And `--help`, which a user will certainly try,
is an unknown command, not help. If you want it to be help, that is a decision, and it belongs in this
table before it belongs in the code.

### 2. Reject the separator at the boundary

The scenario fixed the title. This is the same fix with the round-trip property made explicit, because
"the constructor rejects a tab" and "every note that exists survives a round trip" are different
claims:

@@sol2@@

`accepted 3 of 5` and `round-tripped losslessly 3 of 3`. The two rejected titles are the ones
containing a tab and a newline. The three accepted ones include the empty string and `Ünïcode`, and the
second number is the one that matters: **every note the constructor allowed came back identical.**

The empty string is accepted deliberately. It is not the same as a missing title — the command layer
decides that `quill add` with no title at all is a usage error, and the format layer decides that a
note may have an empty title. Two layers, two questions, and keeping them separate is what stops one
of them from making the other's decisions.

### 3. Adding a command proves the switch

Chapter 16 promised that a sealed hierarchy catches a missed case at compile time. Here is the promise
kept, with a `delete` command added to the four:

@@sol3@@

`5 permitted types, 5 arms, and no default arm`. The `describe` method grew by exactly one arm and
nothing else had to change, which is the property to look for in a design: the cost of a new case is
proportional to the case, not to the number of places that must be told about it.

The proof that the switch is exhaustive is the absence of `default`. Delete the `Command.Delete` arm
and the file stops compiling with the same diagnostic `BadSwitch.java` produced earlier in the
chapter. You do not have to trust that you remembered — javac tells you.

### 4. `max + 1`, not `size + 1`

This is the one that looks like a style preference and is not:

@@sol4@@

Three notes, then the middle one deleted. `max + 1` returns `4` both times, because the highest id in
the file is still `3`. `size + 1` returns `4` and then `3` — and `3` is already taken. The next `add`
would create a second note numbered 3, `list` would print two notes with the same id, and `show 3`
would have to pick one.

An id is an identifier, not an index. An index is a position in a sequence and it is expected to
change when the sequence changes; an identifier is a name and it must never be reused, or every
reference to it becomes ambiguous. The same reasoning is why databases have sequences that never go
backwards, and why deleting a row does not renumber the others.

## Key takeaways

- A command-line program's interface is its arguments, its output **and its exit code**. Decide the
  codes before the features, write them as constants, and let `0` mean success.
- Take the output stream as a parameter instead of using `System.out` directly. It costs one argument
  and makes every command testable.
- `System.exit` does not flush. Flush first, or stay off the success path.
- A file format is `render` and `parse` together. `split(SEP, 3)` keeps the body intact when it contains
  the separator; the same limit is what lets a separator in the *title* corrupt the note silently.
- A format's illegal inputs must be rejected where the value is constructed. The compact constructor is
  where that goes.
- A sealed hierarchy plus a switch with no `default` arm turns "did you handle every case?" into a
  compile error, with the message `the switch expression does not cover all possible input values`.
- A `default` arm over a sealed type throws that guarantee away. It is not defensive; it is a silent
  downgrade to a runtime bug.
- Append to a file with `StandardOpenOption.APPEND`. Rewriting the whole file to add one line is a
  correctness bug waiting for a crash, not just a performance one.
- An id is a name, not an index. Use the highest existing id plus one, never the count plus one —
  they differ the moment anything is deleted.

## Practice

- [ ] Add a `count` command that prints the number of notes and exits 0. Add its rows to the
      exit-code table from Solution 1 and check that the table still passes.
- [ ] Give `Note` a compact constructor that rejects a tab or newline in the title, then write a loop
      that tries twenty titles — including `""`, a title of only spaces, and one with an emoji — and
      reports how many were accepted and how many of those round-tripped.
- [ ] Change `nextId` to `size + 1` and write the sequence of commands that makes two notes share an
      id. Then change it back and show that the same sequence cannot.
- [ ] Add a `--vault <dir>` option that makes the vault live somewhere other than `./vault`. Prove
      that two vaults in two directories do not see each other's notes.
- [ ] Make `list` print a column-aligned table, then add a note whose title is longer than the column
      width and fix the output so it does not shift.
- [ ] Write a `show <id>` command that exits 4 when the id does not exist. Decide whether an empty
      vault should exit 4 or 0 for `show 1`, and write down why.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `case "count" -> { out.println(vault.read().size()); yield OK; }`. The table gains one row,
   `new Case(new String[] {"count"}, OK)`, and `passed 9 of 9` is the evidence. If you also add a row
   for a missing vault, you have discovered that `count` on an empty directory is not an error.
2. The constructor is the one from Solution 2. The interesting results are the edges: `""` and a title
   of only spaces are accepted, and the emoji is accepted because a tab is not a character class —
   the check is for two specific characters, not for "unusual" ones. A title of only spaces is
   arguably a mistake, but it is the *command layer's* mistake to catch, not the format's.
3. `add A`, `add B`, `add C`, delete `B`, then `add D`. With `size + 1` the new note is numbered 3,
   which `C` already has; `list` shows two notes numbered 3. With `max + 1` it is numbered 4. The
   sequence is the test — write it down before you change the code, or you will pick a sequence where
   the two happen to agree.
4. Parse the option before dispatching and pass the resolved `Path` into `run`, which already takes
   one. Two vaults in two directories are two `Vault` objects over two files; they cannot see each
   other because neither ever looks outside its own `home`. That is the whole benefit of `Vault` taking
   a `Path` rather than deciding for itself.
5. Compute the widest title first, then use `printf("%-" + width + "s", title)`. The trap is that a
   fixed width like `%-20s` does not truncate and does not push the next column along — it just butts
   the long value against whatever follows. Either measure the data or put the variable-length field
   last.
6. `show` reads the vault, finds the note with that id, and prints it; if there is none it writes
   `quill: no note #4` to the error stream and returns 4. For an empty vault the honest answer is 4:
   the user named a note that does not exist, and "the vault is empty" is the reason, not an excuse.
   Returning 0 would tell a script the note was found.
"""

gen.write(TEMPLATE, BLOCKS)
