#!/usr/bin/env python3
"""Generate chapters/22-persistence-files-serialization-and-a-real-format.md.

    python3 tools/gen/22/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "22-persistence-files-serialization-and-a-real-format.md")

BLOCKS = {
    "escaping": gen.run("Escaping.java"),
    "roundtrip": gen.run_files(["Note.java", "RoundTrip.java"]),
    "serialblob": gen.run("SerialBlob.java"),
    "encoding": gen.run("Encoding.java"),
    "versioned": gen.run("Versioned.java"),
    "project": gen.run_files(["Main.java", "Note.java", "Vault.java"]),
    "drive": gen.sh("drive.sh", "run-project"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run_files(["Note.java", "Sol1.java"]),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 22
part: 3
title: Persistence — Files, Serialization and a Real Format
summary: Replace Quill's one-line-per-note format with one that can hold any text at all, decide what to do about character encodings and versions, and write the file so that a crash cannot leave it half-finished.
minutes: 60
tags: [persistence, file format, escaping, serialization, encoding, atomic writes]
---

Chapter 20 left Quill with a format that worked and could not hold a newline. Chapter 21 left it
refusing multi-line bodies rather than corrupting them, which was the right call and not a solution.
This chapter fixes the format properly. Along the way it answers three questions every program that
writes a file eventually has to answer — how do I represent text that contains my separator, what do I
do about character encoding, and how do I stop a crash from leaving the file unreadable — and it
answers a fourth that Java poses specifically: the language ships a serialization mechanism, and this
chapter explains why this project does not use it.

## A format has to be able to hold every body

The old rule was "a field may not contain a tab", and it had a hole the size of the user's clipboard.
The new rule is better: **a field may not contain a tab, because a tab in a field is written as the
two characters `\t`.** That is escaping, and it turns a restriction into a representation.

Four characters need it, and the fourth is the one people forget:

| character | written as | why |
|---|---|---|
| `\` | `\\` | or an escape could never be read back unambiguously |
| tab | `\t` | the field separator |
| newline | `\n` | the record separator |
| carriage return | `\r` | the other half of a line ending from Windows |

The backslash has to be escaped first, and *that* is the whole difficulty:

@@escaping@@

Two implementations, the same two inputs, and only one of them is correct.

`wrongOrder` replaces the newline first and the backslash second. On `two\nlines` it turns the newline
into a backslash and an `n` — and then doubles that backslash, because it has not finished escaping
yet. The stored form has two backslashes, and reading it back gives a literal `\n` **as two characters**
rather than a newline. `same=false`.

`rightOrder` escapes the backslash first, so when it later introduces a backslash as part of `\n`,
there is no second pass to double it. `same=true`.

Now look at the second field. `back\slash` has no newline in it, so **both implementations are
correct** — `same=true` twice. That is the trap in its purest form: an escape routine that is wrong
only for newlines passes every test written with backslashes, and the bug ships. This is why the test
suite in the next section is a list of awkward inputs rather than one comfortable example.

## The round-trip property is the test

"Every note survives being written and read" is a property, not an example, so it is tested as one:

@@roundtrip@@

Nine inputs, nine `ok`, and the list is chosen rather than typed at random. The empty string. A tab.
A newline. A lone backslash, which is the input that breaks a naive unescaper. The four characters
`already \n escaped`, which is what a user gets if they type the escape sequence literally — the
round trip must keep it as four characters and not turn it into a newline. `\r\n`. And a string with a
**trailing space**, which is the input that breaks a format that trims.

`round-tripped 9 of 9` is the claim, and it is worth noticing what it would take to falsify it: change
`escape` to use `wrongOrder` and the newline case reports `LOST`. The property test is not decoration;
it is the specification of the format, executable.

One detail in `Note` is easy to miss and produces a confusing error. The compact constructor is
declared `public`:

```java
public Note {
    if (id <= 0) {
        throw new IllegalArgumentException("id must be positive: " + id);
    }
}
```

A record's canonical constructor has the same access as the record, so for a `public record` it is
`public`. A compact constructor written without a modifier is package-private, which is *narrower*,
and javac rejects the whole file with `invalid canonical constructor in record Note`. If your record is
public, its compact constructor must say so too.

:::tip
Escape the backslash **first**, then everything else, and write one function that does both directions
next to each other. A format is a pair of functions, and the bug above is a bug about their order — it
is invisible if they live in different files.
:::

## Java will serialize your objects, and you should say no

Java has a built-in way to write an object to bytes: implement `java.io.Serializable` and hand the
object to an `ObjectOutputStream`. It works, and it is a trap.

@@serialblob@@

`round trip = true` — the mechanism does what it says. Now look at the other three lines.

The bytes start with `aced0005`. That is `STREAM_MAGIC` and `STREAM_VERSION`, and everything after it
is a binary encoding of the class structure, the field names and the values. **It is not text.** You
cannot read it, you cannot fix it with an editor, and `cat` on it is useless. The old format's
advantage was that a human could repair a vault with `vi`; this gives that up.

`names the class = true` is the second problem. The bytes contain the fully-qualified name of the class
that produced them, so the file is coupled to your code. Rename the class, move it to another package,
or change a field and the serialized form no longer matches — Java detects this with a computed
`serialVersionUID` and refuses to read the file with `InvalidClassException`. Your data's lifetime is
now the same as your class's lifetime, which is the opposite of what a persistence format is for.

The third problem is the reason to say no rather than "not yet". **Deserialization of untrusted bytes
is a well-known vulnerability class.** `ObjectInputStream` reconstructs arbitrary objects by running
their constructors and `readObject` methods, so reading a file an attacker can write is close to
executing code an attacker can write. Every security guide that mentions Java serialization says the
same thing: do not use it on data you did not produce.

So Quill writes text, and this chapter writes the escaping by hand. That is more code than
`implements Serializable` — about forty lines — and it buys a file that is readable, repairable,
portable and safe.

:::warning
`Serializable` is not wrong everywhere. It is a reasonable choice for a short-lived cache in a single
program, where the bytes never leave the machine and the class never changes. It is the wrong choice
for anything a user can edit, move between versions, or hand to you.
:::

## Encoding is not optional

A `String` is a sequence of `char` values. A file is a sequence of bytes. `StandardCharsets` is the
bridge, and the bridge is not the identity:

@@encoding@@

`café — 咖啡` is nine characters. In UTF-8 it is sixteen bytes, because `é` takes two and each of the
CJK characters takes three. In Latin-1 it is nine bytes — and `Latin-1 '?' = 3` says why: the em dash
and the two CJK characters **cannot be represented at all**, so `getBytes` replaced each with a
question mark. The bytes are the right length and the text is gone.

That is why `Latin-1 round trip = false` and `UTF-8 round trip = true`. Choosing the wrong charset does
not throw; it silently destroys the characters it cannot represent, and the only way to notice is to
read the data back and compare.

Which is why every file call in Quill names the charset explicitly:

```java
Files.writeString(file, note.render() + "\n", StandardCharsets.UTF_8,
        StandardOpenOption.CREATE, StandardOpenOption.APPEND);
```

`Files.writeString` and `Files.readString` default to UTF-8 and would have been fine without the
argument. The older `FileWriter` and `new PrintWriter(File)` default to **the platform default
charset**, which is UTF-8 on a modern macOS or Linux box and is not on a machine configured otherwise.
Code that relies on the default works on the machine it was written on and corrupts data elsewhere —
and that is the worst kind of bug, because it is invisible until it is expensive. **Name the charset
every time, even when the default happens to be what you want.** The argument is one identifier and it
removes an entire class of environment-dependent failure.

## A file needs a version

The format changed in this chapter, so there are now two kinds of `notes.tsv` in the world: the ones
Chapter 20 wrote, which have no header, and the ones this chapter writes, which do. A reader that
cannot tell them apart will either crash on the first or silently misread the second.

The fix is one line at the top of the file, and a refusal:

@@versioned@@

`-> 2 note(s)` for the current format, `-> unsupported version: quill-1` for a file from an older
build, and `-> not a quill file: no header line` for something that is not a vault at all.

The interesting decision is the middle one. `quill-1` is a format this program understands perfectly
well — the escaping is the only difference — and the honest options are to migrate it (Solution 4) or
to refuse it with a message. What is not an option is to guess. **A reader that tries the old format
when the new one fails is a reader that will one day write a file it cannot read back**, because it
will have interpreted some bytes as notes that were never notes.

The header also gives the format somewhere to grow. When Chapter 33 adds a field, the version becomes
`quill-3`, and every build that only understands `quill-2` says so in one sentence instead of
producing a vault with half the fields empty.

## Quill writes the new format

With escaping in place, the restriction from Chapter 21 can go. `Main` no longer counts body lines,
`Vault` writes the header, and `Note` escapes both fields:

@@project@@

The `add` method is four lines shorter than it was, because the refusal is gone:

```java
String body = String.join("\n", lines);
```

Joining the lines with a newline and storing that is now correct, because `render` escapes the newline
before it reaches the file. The multi-line body that Chapter 21 had to reject goes in:

@@drive@@

Read the three commands in order. `add` reports `19 character(s)` — that is `milk and eggs`, a newline,
and `bread`. `list` prints the note, and the body spans two lines because the newline came back as a
newline. Then `cat` shows the file itself, where the same body is one line containing the two
characters `\` and `n`.

That contrast is the whole idea. The file is line-oriented and always has been; the *fields* are
escaped so that a body can contain anything, and the escaping is what makes the two views agree.

:::scenario The backup that caught the file mid-write

Quill runs on a small server. A nightly job copies `vault/notes.tsv` to a backup directory. One morning
the vault is restored from a backup taken while `quill add` was running, and every note is gone — the
file is zero bytes. The backup job did nothing wrong: it read the file at a moment when the file
really was empty.

:::solution
`Files.writeString(path, text)` does not write the text and then replace the old content. It **truncates
the file to zero bytes first**, and then writes. Between those two moments the file exists and is
empty, and any reader — a backup job, a second copy of `quill`, a text editor — sees an empty vault.

The window is small and it is real, and the size of the window is not the point: the failure is not
proportional to the risk, because a backup that catches it preserves the empty state.

The fix is to never write the live file at all. Write the new content to a temporary file in the same
directory, then **move** it into place:

@@scenario@@

`mid-write, truncated : 0 bytes, 0 line(s)` is the state the in-place write passes through. The atomic
move has no such state: the live file is either the old content or the new content, and a reader that
opens it always gets one of the two. `temp file left behind : false` because a move does not leave a
copy.

`ATOMIC_MOVE` is the part that matters and it is worth knowing what it promises. It guarantees that the
rename is atomic **on the same filesystem**, so the temporary file must be created in the same
directory as the target — `resolveSibling` rather than `Files.createTempFile`, whose default directory
is somewhere else entirely.

The same reasoning applies to `Vault.append`. Appending is already atomic enough for a single writer,
because `O_APPEND` writes at the end and a reader sees either the line or not. What is not safe is
rewriting the whole file in place, which is what deleting a note will need in Chapter 23.
:::

## Solutions

### 1. The case Chapter 20 had to refuse

Chapter 20's `Note` rejected a tab in the title, and the scenario that motivated it was a title pasted
out of a spreadsheet. With escaping, the ban is unnecessary:

@@sol1@@

`round-tripped 4 of 4`, including `'Groceries\tand more'`, which is the exact input that Chapter 20's
constructor threw an exception on. The stored form shows why: the tab is two characters, `\` and `t`,
so it can no longer be confused with the separator.

This is the difference between validation and representation, and it is worth being able to say out
loud. Validation says *"this value is not allowed"*. Representation says *"this value is allowed and
here is how I write it down"*. A format that can represent everything needs less validation, and every
restriction it does not need is a restriction your users will eventually hit.

### 2. Create the header once, not every time

`Vault.append` needs a header on a new file and must not add a second one to an existing file:

@@sol2@@

`after the first call = 1 line(s)` and `after the second call = 1 line(s)`. The method is **idempotent**
— calling it twice has the same effect as calling it once — and that property is what makes it safe to
call at the top of `append` on every write rather than only on the first.

The check is on the *file*, not on a flag in memory, which is the part that matters. A `boolean
headerWritten` field would be true after a restart that found no file, and false after a restart that
found one. **Ask the file what it contains; do not remember.**

### 3. Replace the file, do not truncate it

The scenario's fix, as a reusable method:

@@sol3@@

`before = 27 bytes, 2 line(s)` and `after = 48 bytes, 3 line(s)`, and `temp = false`. The live file went
from the old content to the new content with no state in between, which is what `ATOMIC_MOVE` buys.

Note the shape: build the whole new content in memory first, write it once, move it once. That is
possible because a vault is small. A file too large to hold in memory needs a different strategy —
write the new file, then stream the unchanged parts across — but the principle is the same, and the
principle is *never modify the live file in place*.

### 4. Migrate, or refuse — but do not guess

A `quill-1` file has no header and no escaping, and both differences are mechanical:

@@sol4@@

The header is added and the ids are renumbered from 1. The `.replace("\\", "\\\\")` on each field is a
no-op for this input and is not optional in general: `quill-1` stored fields raw, so a title containing
a backslash would become ambiguous the moment the new unescaper saw it. **Migrating a format means
re-establishing every invariant the new format assumes**, and the ones that are invisible for your test
data are exactly the ones that will bite.

The migration is a one-way door, which is why it is a separate command rather than something `read`
does automatically. `quill migrate` rewrites the file and prints how many notes it converted; `read`
refuses anything that is not `quill-2`. An upgrade the user asked for is a migration. An upgrade that
happens because the reader guessed is a data loss waiting to be discovered.

## Key takeaways

- Escape the backslash **first**. An escaper that adds a backslash before the backslash pass will
  double the escape it just introduced, and it is correct for every input without a newline.
- A format is a pair of functions, `escape` and `unescape`, and the test for it is a round trip over
  awkward inputs: empty, the separator, the terminator, a lone backslash, and a trailing space.
- A `public record` needs a `public` compact constructor. Without the modifier it is package-private,
  which is narrower, and javac rejects the file with `invalid canonical constructor`.
- Java's built-in serialization writes binary that names your class, couples the data to the code's
  lifetime, and is unsafe on untrusted input. Write text instead.
- Always name the charset. `Files.writeString` defaults to UTF-8; `FileWriter` and `PrintWriter` default
  to the platform, which is a bug that only appears on someone else's machine.
- A charset that cannot represent a character replaces it silently. Read the data back and compare, or
  you will not know.
- Put a version in the file. Refuse a version you do not understand, or migrate it deliberately — never
  guess, because a guess writes a file you cannot read.
- `Files.writeString` truncates before it writes. A reader can catch the file at zero bytes. Write to a
  temporary file in the same directory and `ATOMIC_MOVE` it into place.
- A format that can represent everything needs less validation. Prefer representation to restriction.

## Practice

- [ ] Write `escape` and `unescape` for a comma-separated format and prove the round trip over ten
      awkward fields. Include a field that contains a comma, a quote, and the two characters `\n`.
- [ ] Change `Note` to escape the id field too, and explain what has to be true about the id for that
      change to be unnecessary.
- [ ] Make `Vault.append` write the header only when it creates the file, then make it crash between
      creating the file and writing the header, and show that `read` reports a clear error.
- [ ] Write `quill migrate` as a real command that reads a `quill-1` file, writes a `quill-2` file
      atomically, and prints the number of notes converted. It must refuse to run twice.
- [ ] Add a `size` field to `Note`, bump the header to `quill-3`, and write the migration from
      `quill-2`. Decide what `size` means for a note written before it existed.
- [ ] Take the `Scenario` and change `Files.move` to a plain copy followed by a delete. Find the window
      in which the live file is missing, and explain why the window is larger than the truncate window
      it replaced.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The same structure, with `,` `"` `\n` `\r` and `\` in the escape table. The field containing a
   quote is the one that catches people: if you escape with quotes, the escape character is the quote
   and you need `""` for a literal one, which is why CSV is harder than it looks. Escaping with a
   backslash and quoting only when the field contains a comma is what a real CSV writer does.
2. Escaping the id is unnecessary because `Integer.toString` produces only digits and a leading `-` —
   a set of characters that cannot contain a separator or a backslash. The rule is: escape a field when
   the set of strings it can hold includes the escape character or a separator. For a decimal integer
   that set is closed, so the escaping would be dead code.
3. `Files.createDirectories`, then `Files.createFile` (which fails if it exists), then write the header.
   Crashing between the two leaves an empty file, and `read`'s `lines.isEmpty()` branch returns no
   notes rather than an error — which is wrong, because an empty file is not a valid `quill-2` vault.
   The fix is to treat empty as an error too, or to write the header with `CREATE_NEW` in one call.
4. Read the header, check it is `quill-1`, convert in memory, `rewriteAtomically`, and print the count.
   It refuses to run twice by checking that the header is `quill-1` before doing anything, which is the
   same rule the reader uses: decide from the file, not from a flag.
5. `size` is the length of the body in characters. For a note written before the field existed there is
   no honest value, and the two options are to compute it from the body during the migration — which is
   correct and is what a migration should do — or to leave it `-1` and have every reader treat `-1` as
   "unknown". Computing it is better: the migration has the body, so the information is not lost.
6. A copy-then-delete has two windows: after the copy but before the delete, the live file still exists
   and is stale, and after the delete but before... nothing, because the copy already landed. The real
   problem is that the copy itself is not atomic, so a reader during the copy sees a partially written
   file — the same failure as truncation, with a longer window. `Files.move` on the same filesystem is
   a single rename, so there is no window at all.
"""

gen.write(TEMPLATE, BLOCKS)
