#!/usr/bin/env python3
"""Generate chapters/23-a-command-layer-and-argument-parsing.md.

    python3 tools/gen/23/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "23-a-command-layer-and-argument-parsing.md")

BLOCKS = {
    "parse": gen.run_files(["Commands.java", "ParseDemo.java"]),
    "dominated": gen.bad("Dominated.java",
                         "this case label is dominated by a preceding case label"),
    "warnserial": gen.warn("WarnSerial.java",
                           "has no definition of serialVersionUID"),
    "options": gen.run_files(["Options.java", "OptionsDemo.java"]),
    "project": gen.run_files(["Main.java", "Options.java", "Commands.java",
                              "Note.java", "Vault.java"]),
    "drive": gen.sh("drive.sh", "run-project"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 23
part: 3
title: A Command Layer and Argument Parsing
summary: Turn the strings a user typed into a value your program can switch on, so that every malformed command is rejected in one place and every valid one is handled somewhere the compiler can check.
minutes: 55
tags: [cli, argument parsing, sealed types, exceptions, design]
---

Chapter 20 sketched a sealed command hierarchy and then did not use it: `Main` switched on
`args[0]`, a `String`. This chapter makes the sketch real. The change is small in code and large in
consequence — arguments are parsed into a value *once*, before anything is executed, and from that
point the rest of the program works with a type that cannot be malformed. It is the difference between
a program that checks its input in five places and one that checks it in one.

## A string array is a poor thing to switch on

`String[] args` is what the JVM hands you, and it has no structure at all. `args[0]` might be a
command, might be an option, might be a typo. `args[1]` means a title for `add`, an id for `show`, and
nothing for `list`. Every one of those facts lives in the head of whoever wrote the dispatcher.

That is survivable for four commands. It stops being survivable the moment the rules are worth
writing down, because a `switch` on a `String` cannot express them:

- Nothing connects the label `"list"` to the fact that `list` takes no arguments.
- Nothing stops `args[1]` being read when `args.length` is 1.
- Nothing tells you, when you add a fifth command, that you forgot to handle it somewhere.

The fix is to spend the first few lines of the program turning the strings into a **value**, and then
never look at the strings again.

## Parse into a value, then act on the value

The command layer is a sealed interface with one record per command, and a `parse` that returns one of
them:

@@parse@@

Eleven inputs, and every one of them is answered. The first block is worth reading carefully because
it contains the whole design in miniature.

`parse` takes the array and returns a `Commands`. It does not execute anything, it does not print
anything, and it does not touch a file. `new Help()` for an empty array is a decision — a bare `quill`
is a request for help, not an error — and because it is a decision it is visible here rather than
buried in a branch.

Then the errors. `add` with no title, `show` with no id, `show seven`, `show 0`, and `frobnicate` all
produce a `UsageException` carrying a message a user can act on. `usage: show <id> needs an id` and
`usage: 'seven' is not an id` are different failures and they say so; `usage: ids start at 1, not 0` is
the range check from Chapter 22's format surfacing at the command line, where it belongs.

The `describe` method is the same exhaustive switch from Chapter 20, and it exists because a transcript
is easier to read than a `toString`. In the real program the second switch *executes*.

:::tip
Keep `parse` and the executor apart, and notice what each one is allowed to know. `parse` knows about
strings and about what a well-formed command looks like. The executor knows about vaults and notes and
streams. Neither knows what the other knows, and the seam between them is one method call.
:::

## The parse throws, and that is the design

`UsageException` extends `IllegalArgumentException`, and it is thrown rather than returned. That is a
choice worth defending, because returning `null` or an `Either` is fashionable.

A usage error is exceptional in the literal sense: it happens once, at startup, and it ends the
program. It is not a value the program goes on to compute with. Making it an exception means the happy
path — `parse`, then execute — reads as two statements with no error plumbing between them, and the
single `catch` in `Main` turns it into an exit code:

```java
try {
    invocation = Options.parse(args);
    command = Commands.parse(invocation.rest());
} catch (IllegalArgumentException e) {
    err.println("quill: " + e.getMessage());
    err.print(USAGE_TEXT);
    return USAGE;
}
```

The one thing that must not happen is for the exception to escape as a stack trace. A user who types
`quill show seven` should not see twenty lines of `at Main.run(Main.java:41)`. **Catch it at the
boundary, print the message, print the usage, return `2`.** The stack trace is for the developer; the
message is for the user; they are different audiences and the boundary is where you choose.

**This retires exit code `3`.** Chapters 20 to 22 returned `3` for `add` with no title and `2` for an
unknown command — two codes for two failures a user cannot tell apart, since both mean "the command
line was malformed" and both print the same usage text. Now that every malformed command goes through
one parser, there is one code for it, and it is `2`. A published contract that changes should say so
out loud: a script that tested for `3` will see `2` from this chapter on, and the exit-code table is
exactly where a reader would go looking for the difference.

## An arm that can never be reached is a compile error

The sealed hierarchy is not only a way to make the executor exhaustive. It also lets javac find arms
that are *dead*, which is the same guarantee from the other direction:

@@dominated@@

`case Shape any` matches every `Shape`, so the two arms after it can never run. javac says so:
`this case label is dominated by a preceding case label`. The file does not compile, and the reason is
worth pausing on — a type pattern for the sealed interface itself is a valid arm, and writing it first
silently disables everything below it.

In a `String` switch the equivalent mistake is unreachable in a different way: `case "list"` written
twice is a duplicate-label error, but a `default` placed first is perfectly legal and swallows
everything. The sealed version refuses the broad arm in front of the narrow ones, which is the more
useful check.

## A serializable exception wants a `serialVersionUID`

`UsageException` extends `IllegalArgumentException`, and `Throwable` implements `java.io.Serializable`.
That inheritance has a consequence that `-Xlint:all` will point out:

@@warnserial@@

`warning: [serial] serializable class UsageException has no definition of serialVersionUID`.

This is the one place in the book where the answer to a warning is *suppress it*, and it is worth
understanding why rather than reaching for the annotation out of habit. Java's serialization machinery
computes a version number for a class so that it can refuse to read bytes written by an incompatible
version. For a value type that gets persisted, that check is doing real work. For an exception that is
thrown, caught and discarded inside one process, nothing is ever serialized, so the number is dead
weight — and computing it costs a warning every time you add a method.

So the class says so:

```java
@SuppressWarnings("serial")
class UsageException extends IllegalArgumentException {
    UsageException(String message) {
        super(message);
    }
}
```

Note the shape of the argument, because it is the argument for every suppression. **You are not
silencing a warning; you are recording that the warning does not apply, at the one place a reader will
look.** A `@SuppressWarnings` on a method that swallows a real problem is a bug; this one is
documentation.

## Options come before the command

`--vault <dir>` has to be understood before the command is parsed, because it changes where the
command will look. That makes it a separate concern from `Commands.parse`, and it gets its own type:

@@options@@

The loop consumes options from the front and stops at the first thing that is not one. Four cases and
one subtlety:

- `list` — no options, so the whole array is the command.
- `--vault /tmp/notes list` — the option is consumed, `[list]` is what the command layer sees.
- `--vault` with nothing after it — an error naming the option, not a crash on an array index.
- `--` — the terminator. Everything after it is a command argument even if it starts with a dash,
  which is what `-- --vault list` demonstrates: `--vault` is now a *command name*, and the command
  layer will reject it as unknown.

The last one is the reason `--` exists at all. Without it, there is no way to pass a value that looks
like an option, and a program that cannot represent a valid input is a program with a hole in it. You
have used this every time you typed `git checkout -- .`.

## Quill parses, then executes

The project now has five files, and the arrows between them are worth following. `Main` owns the
streams and the exit codes. `Options` turns `args` into a home directory and a remainder. `Commands`
turns the remainder into a value. `Vault` owns the file. `Note` owns the format.

@@project@@

`run` is three phases in ten lines. Parse — and if that fails, report and return. Then construct the
vault from the parsed home directory. Then hand both the command and the vault to `execute`, whose
switch is the only place in the program that knows what a command *does*.

Look at how little `execute` needs. It takes a `Commands`, a `Vault` and the streams. It does not take
`args`, and it could not read them if it wanted to, because by the time it is called they have been
consumed. **That is the whole point of parsing into a value: the malformed inputs are gone.** There is
no `args.length >= 3` check inside `add`, because `Add` cannot be constructed without a title.

Running it exercises every arm of that switch:

@@drive@@

Two notes added, both listed, one shown, one deleted. Then the sixth command deletes note 1 a second
time and prints `quill: no note #1` with exit `5` — the code this chapter added for "you named
something that is not there". And the last line, `quill --vault other list`, prints `no notes yet`,
which is the option working: a different home directory is a different vault, and it is empty because
nothing has been added to it.

:::pitfall
**Parsing inside the executor is how the checks get duplicated.** The tempting version of `execute`
takes `String[] args` and does `Integer.parseInt(args[1])` in the `show` arm and again in the `delete`
arm — and now the range check, the error message and the exit code are written twice, and a third time
when `rename` arrives. The symptom is that `show abc` and `delete abc` report *slightly* different
errors, because they were written on different days. Parse once, in one place, into one type.
:::

:::scenario The delete that took two other notes with it

A teammate implements `quill delete <id>`. The implementation finds the line whose id matches, then
writes back everything **before** that line — a natural thing to reach for, because the file is
line-oriented and truncating is one call. A user deletes note 1 out of three and reports that notes 2
and 3 have vanished as well.

:::solution
The bug is not in the id matching. It is in the assumption that "remove an item from a sequence" means
"cut the sequence at that point". It means **keep everything that is not the item**, and those are the
same thing only when the item is last.

@@scenario@@

Deleting note 1 by truncation leaves 1 line — the header, and nothing else. Deleting it by filtering
leaves 3: the header and the two notes that were never the target. The second number is the correct
one and the difference is not subtle, which is exactly why it is worth a test rather than a reading.

Two things made this bug possible, and both are worth naming.

The first is that the vault is a *list of lines* rather than a list of notes. `Vault.delete` in this
chapter reads every note, builds a new list containing the ones whose id differs, and rewrites — so
"remove one" is expressed as "keep the others" and there is no index to get wrong.

The second is that the rewrite is atomic. `delete` is the first operation that has to replace the
whole file, and Chapter 22's `rewrite` writes to a temporary file and moves it into place, so a crash
halfway through leaves the old vault rather than a truncated one. **A destructive command is exactly
where the atomic-write discipline earns its keep**, and it is not a coincidence that the first
destructive command is the first one that needs it.
:::

## Solutions

### 1. Adding a command, and what it costs

`rename` is the sixth command. Here it is, fully wired, in a hierarchy of its own:

@@sol1@@

`6 permitted types, 6 arms, no default: one new case, one new arm`. That is the claim worth checking
against the alternative. In the `String`-switch version of Chapter 20, adding a command meant editing
the dispatcher and *remembering* to edit the help text, the `describe` method if there was one, and
any test that enumerated the commands. Here the compiler enumerates them for you: add `Rename` to the
`permits` clause and every switch over `Command` in the program stops compiling until it has an arm.

The cost is proportional to the case, not to the number of places that must be told about it. That is
the property to look for in a design, and it is the reason the sealed hierarchy is worth the extra
type rather than a `String` and a `default`.

### 2. "Not found" is an exit code, not an exception

`delete` on an id that is not there is not a bug in the program. It is an answer, and it needs a code:

@@sol2@@

`delete #2 -> exit 0, 2 left [1, 3]` and then `delete #2 -> exit 5, 2 left [1, 3]`. The second attempt
removed nothing and reported `5`, and the vault is unchanged either way.

The design question is whether that second attempt should be an error at all. Two defensible answers:
`5` says "the thing you named is not here", which lets a script tell a typo from a success; `0` says
"the note you asked to be gone is gone", which makes the operation idempotent and a retry safe. What is
not defensible is throwing an exception — nothing went wrong, the user asked about a note that does not
exist, and the program knows the answer.

This chapter chose `5`, and the choice is visible in the exit-code table rather than hidden in a
branch. Whichever you pick, write it down, because a script author will build on it.

### 3. The id is validated once

`show`, `delete` and `rename` all take an id, and all three go through one function:

@@sol3@@

Ten inputs, and the split between accepted and rejected is the useful part. `'3'`, `'007'` and `'+3'`
all become `3` — `Integer.parseInt` accepts a leading `+` and any number of leading zeros, so the three
spellings a user might type all work. `'0'` and `'-1'` parse fine and are then rejected by the range
check, with a message that names the rule. `' 3'` and `'3 '` are rejected by `parseInt` itself, because
it does not trim.

That last pair is the one to remember. A value that came from a text field or a copy-paste routinely
carries whitespace, and `parseInt` will not forgive it. Trim at the boundary where the string arrives,
not inside the parser — the parser is the wrong place to guess what the user meant.

One function, one message per failure, called from three commands. When the rules change — when ids
become `String` identifiers, say — there is one place to change them.

### 4. An unknown option is an error, not something to ignore

A parser that skips what it does not understand is worse than one that refuses, because the user gets
a program that silently did something other than what they asked:

@@sol4@@

Seven inputs and the two that matter are the failures. `-x list` reports `unknown option '-x'` rather
than treating `-x` as a command name and reporting `unknown command`. And `--vault=/tmp/n list` is
rejected, because this parser only understands the two-token form — `--vault` followed by its value.

That second one is a real limitation and it is stated rather than hidden. Many programs accept both
`--vault /tmp/n` and `--vault=/tmp/n`; supporting the second means checking for the `=` and splitting
on the first one, which is four lines. What must not happen is accepting `--vault=/tmp/n` and then
ignoring it, because the user's vault is now somewhere they did not choose.

`--help` being an unknown option is also deliberate. There is one spelling for a command in this
program — a word with no dashes — and adding a second one for `help` alone would mean every future
command has to decide whether it wants a `--` spelling too.

## Key takeaways

- Turn `String[] args` into a value **once**, before executing anything. After that, the rest of the
  program cannot see a malformed command.
- One record per command in a sealed interface, and `permits` listing all of them. The compiler then
  knows the complete set.
- Parse in one place and execute in another. `parse` knows strings; the executor knows vaults and
  streams. Neither needs the other's knowledge.
- A usage error is an exception thrown at startup and caught at the boundary. Catch it, print the
  message, print the usage, return `2` — never let a stack trace reach the user.
- A type pattern for the sealed interface itself, written before the specific arms, makes them
  unreachable: `this case label is dominated by a preceding case label`.
- `[serial]` fires on every class extending `Exception`. For an exception that is never serialized,
  `@SuppressWarnings("serial")` is documentation, not a silencing.
- Consume options from the front and stop at the first non-option. Support `--` so that a value which
  looks like an option can still be passed.
- An option you do not understand is an error. Silently ignoring it means the user gets a program that
  did something other than what they asked.
- "Not found" is an exit code, not an exception. Pick a number, write it in the table, and make the
  choice visible.
- Remove an item by keeping the ones that differ, never by truncating at its position.

## Practice

- [ ] Add a `count` command and add its arm to `execute`. Before you compile, predict which files
      change; then check. The answer should be two.
- [ ] Make `Commands.parse` reject a command that takes arguments when it is given extra ones —
      `quill list extra` should fail — and add the rows to a table that proves it.
- [ ] Implement `--vault=<dir>` as well as `--vault <dir>`, and decide what `--vault= list` should do.
- [ ] Change `delete` to exit `0` when the note was already gone, and write the two-command sequence
      that tells the two designs apart.
- [ ] Add a `search <word>` command that prints every note whose title or body contains the word, and
      make it exit `5` when nothing matches.
- [ ] Move the id parsing out of `Commands` into a `parseId` in its own class, then add a second caller
      that needs a different message. Decide whether the message belongs to the parser or the caller.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Two files: `Commands.java` gets a `record Count() implements Commands {}`, a `permits` entry, a
   `parse` arm and a `describe` arm; `Main.java` gets an `execute` arm. Nothing else changes, and if
   you predicted three you probably expected the help text to need editing — which it does, and which
   is the one thing the compiler cannot check. That is worth noticing: a `Usage` constant is prose, and
   prose is not type-checked.
2. `case "list" -> { if (args.length > 1) throw new UsageException("list takes no arguments"); yield
   new ListNotes(); }`. The table gains `{"list", "extra"}` expecting a usage error. The reason to do
   this is that a user who types `quill list extra` has almost certainly made a mistake, and the
   program should say so rather than ignore the extra word.
3. Check `args[i].startsWith("--vault=")` and take `substring(8)`. `--vault= list` should be an error:
   the value is empty, and an empty directory name is not a vault. The general rule is that an option
   which requires a value must reject an empty one, because the empty string is the value users get
   when a shell variable was unset.
4. `delete #2` then `delete #2`. With exit `5` on the second the script stops; with exit `0` it
   continues. If your scripts retry, choose `0`; if they distinguish a typo from a success, choose `5`.
   The sequence is the test either way.
5. `search` filters `vault.read()` on `note.title().contains(word) || note.body().contains(word)` and
   returns `NOT_FOUND` when the list is empty. Notice that this is the same "is empty a failure?" question
   as `show`, answered the same way for the same reason.
6. The message belongs to the caller, because the same failure is useful at different levels of detail:
   `Commands` wants `'seven' is not an id` for a user, and a test wants to know which of the two rules
   was broken. Have `parseId` throw a typed exception with a code, and let each caller format it — which
   is the same separation as `parse` versus `execute`.
"""

gen.write(TEMPLATE, BLOCKS)
