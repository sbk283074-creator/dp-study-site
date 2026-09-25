#!/usr/bin/env python3
"""Generate chapters/17-io-nio2-and-files.md.

    python3 tools/gen/17/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "17-io-nio2-and-files.md")

BLOCKS = {
    "pathsdemo": gen.run("PathsDemo.java"),
    "readwrite": gen.run("ReadWrite.java"),
    "byteschars": gen.run("BytesVsChars.java"),
    "lines": gen.run("Lines.java"),
    "walk": gen.run("Walk.java"),
    "copymove": gen.run("CopyMove.java"),
    "attributes": gen.run("Attributes.java"),
    "badunhandled": gen.bad("BadUnhandled.java", "unreported exception IOException"),
    "throwmissing": gen.throw("ThrowMissing.java", "NoSuchFileException: nope.txt"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 17
part: 2
title: I/O, NIO.2 and Files
summary: Read and write real files with java.nio.file — knowing what a Path is, why bytes and characters differ, and what every one of these calls can throw.
minutes: 55
tags: [io, nio, files, paths, encoding, streams, try-with-resources]
---

Chapter 13 gave you `try`-with-resources and Chapter 15 gave you streams; both worked on data that
was already in memory. This chapter points them at the filesystem. The API is `java.nio.file`, and the
first thing to get straight is that it separates three ideas the older `java.io.File` ran together: a
`Path` is a *name*, a file is a *thing on disk*, and reading it is an *operation that can fail*. Nearly
every file-handling bug comes from treating those three as one.

## A `Path` is a value, not an open file

Creating a `Path` touches nothing. It parses a string, or joins components, and hands back an
immutable object you can inspect and combine.

@@pathsdemo@@

`Path.of("docs", "notes", "todo.txt")` joins three components with the platform separator, so the
same code produces `docs/notes/todo.txt` here and `docs\notes\todo.txt` on Windows. The printed path
is the one detail of this chapter that genuinely differs by platform, and it is why the rest of the
chapter prints relative names rather than absolute ones.

`getRoot()` is `null` and `isAbsolute()` is `false`, because this path is relative — relative to
whatever the process's working directory happens to be. That is the single most common source of
"I ran it and it worked, then the service did not": a relative path is resolved against a directory
that a command line and a service do not share. In real code, resolve a configured directory once and
build everything from it.

`normalize()` is pure text manipulation, and it is worth knowing exactly how dumb it is:
`a/b/../c` becomes `a/c` without ever asking the filesystem whether `a/b` exists. `relativize` is the
inverse operation — the path you would need to walk from one location to another — and it answers
`../../d`, again without touching disk.

:::note
`Path` and `File` are not alternatives you can mix freely. `Path` is the modern API and everything in
this chapter uses it; `File` survives because old code and a few library signatures still take one.
When you must cross over, `file.toPath()` and `path.toFile()` are the bridges.
:::

## Reading and writing text

For the common case — a whole small file, as text — there is one call in each direction.

@@readwrite@@

`Files.writeString` creates the file if it does not exist and **truncates it if it does**. The first
write produced `13` bytes for `"first\nsecond\n"`, and `Files.readString` gave back exactly what went
in.

The second call passes `StandardOpenOption.APPEND`, which is the only way to add to the end of a
file. Without it, `writeString` would have replaced the contents. That is the trap in this section:
a loop that calls `writeString` per line without `APPEND` leaves a file containing only its last line,
and nothing warns you. The transcript shows the file growing to `22` bytes and the three lines reading
back in order.

`Files.readAllLines` returns a `List<String>` with the line terminators removed, which is what you
want for a config file and is the wrong thing for a 2 GB log — see the last solution.

## Bytes and characters are not the same thing

A file on disk is bytes. A `String` in memory is UTF-16 code units. Something has to convert, and
that something is a charset.

@@byteschars@@

`café — 咖啡` is **9** characters in the heap and **16** bytes on disk. The two numbers differ because
the default charset for `Files.writeString` is UTF-8, and in UTF-8 `é` costs two bytes while each
CJK character costs three. `round trip = true` says the conversion was lossless in both directions.

The last two lines are the failure mode. Encoding the same string as ISO-8859-1 produces `9` bytes,
because that charset cannot represent `—` or the CJK characters at all and replaces each with a single
`?`. The round trip then reports `lossless = false` — the data is gone, and nothing threw.

:::danger
**Never rely on the platform default charset.** `Files.newBufferedReader(path)` and its relatives pick
one up from the environment, so the same program writes UTF-8 on one machine and CP1252 on another.
The default for the `Files` convenience methods is UTF-8 and has been since Java 18, but the
`InputStreamReader`/`OutputStreamWriter` family still uses the platform default. Pass
`StandardCharsets.UTF_8` explicitly, or use the `Files` methods that do it for you.
:::

## Reading a file a line at a time

@@lines@@

`readAllLines` and `lines` answer different questions. The first materialises the whole file as a
`List`; the second gives you a `Stream<String>` that reads as you consume it. Both produced `4` for
this four-line log, so the choice is about memory, not about output.

The `try`-with-resources around the stream is not decoration. A `Stream` from `Files.lines` holds an
open file handle, and it is `close()` — not garbage collection — that releases it. A program that
opens streams in a loop without closing them runs out of file descriptors. This is Chapter 13's rule
applied to Chapter 15's tool: **anything that holds a resource is a `try`-with-resources.**

The last block is the payoff. Splitting each line, taking the level field, `distinct` and `sorted`
gives the three levels in alphabetical order — a report built from a file in five lines, with no
accumulator and no manual parsing loop.

## Walking a tree

A directory listing is not recursive, and the difference between the two is a real bug source.

@@walk@@

`Files.walk` descends, and `Files.list` does not. The three `file =` lines are the recursive answer,
relativised against the root so the output does not depend on where the program ran. The two
`child =` lines are the shallow one: `notes` and `readme.md`, and nothing inside `notes`.

Two habits make this reliable. **Sort before printing** — `Files.walk` and `Files.list` make no
ordering promise, so an unsorted transcript is a test that passes on Tuesday. And **filter early**:
`Files::isRegularFile` removes the directories, which is almost always what a "count the files"
question means. `depth = 7` counts *every* entry including the root and the directories, which is why
it does not equal the three files.

## Copying, moving and deleting

@@copymove@@

`Files.copy` **refuses to overwrite**. The second attempt threw `FileAlreadyExistsException`, and that
is the safe default: a silent overwrite is how a backup destroys the thing it was backing up. Pass
`StandardCopyOption.REPLACE_EXISTING` when you mean it.

`Files.move` on the same filesystem is a rename, so it is atomic and cheap — which is what makes the
write-to-temp-then-rename pattern in the last solution correct. The two booleans show the move
completing: the source is gone and the destination exists.

`Files.delete` and `Files.deleteIfExists` differ in exactly one way, and the difference is a design
decision rather than a convenience. Deleting something that is not there is a `NoSuchFileException`
from `delete` and a no-op from `deleteIfExists`. Choose by asking what the absence *means*: if it
means your earlier code failed, you want the exception.

:::pitfall
**`delete` on a non-empty directory throws `DirectoryNotEmptyException`.** Neither `delete` nor
`deleteIfExists` is recursive, deliberately — a recursive delete is one of the few operations where a
mistyped variable silently removes a user's home directory. Walk the tree, delete leaves first, and
make sure the root you are deleting is the one you intended.
:::

## Asking about a file

@@attributes@@

These are all queries against the filesystem, not against the `Path` object — every one of them
performs a system call. `Files.exists` is the one to reach for rather than constructing the path and
hoping.

`Files.createDirectories` is idempotent: calling it on a directory that already exists is not an
error, unlike `createDirectory`, which throws `FileAlreadyExistsException`. That is why
`createDirectories` is the one to call at the top of a write, and why the last line of the transcript
is `true` rather than an exception.

`Files.size` returns bytes, and it is the size on disk at that moment. Do not cache it: another
process can change the file between the call and your use of the answer.

## Every one of these calls can fail

Everything in this chapter returns a value *or throws*, and the compiler tracks which.

@@badunhandled@@

`Files.readString` declares `throws IOException`, and Java's checked exceptions make that the caller's
problem. This is the contract from Chapter 13 doing real work: the compiler refuses the file, so you
cannot forget the failure path by accident. The usual fix is to declare `throws IOException` on
`main` while learning, and to handle it deliberately in production code.

The failure itself is worth seeing once.

@@throwmissing@@

`NoSuchFileException: nope.txt` — the message names the file, and the stack trace points at the exact
line. This is what the checked exception bought you: a specific, actionable failure instead of a
`null` that surfaces three methods later.

:::scenario The report that counted a third of the vault

A support engineer is asked how many files a vault holds and how much space they take. The script
lists the vault directory, filters to regular files, and reports the totals. The answer comes back as
one file.

:::solution
`Files.list` is not recursive. The vault has one file at the top level and five more inside
subdirectories, so a shallow listing sees `1` and the real answer is `6`.

The fix is `Files.walk`, which descends the whole tree, and the reason to be careful is that the bug
is invisible in the output: a count of `1` is a plausible number, and nothing about it looks wrong.
The honest version also says what it counted — `byExt` breaks the six down by extension, so a reader
can see that `md` files were found at all.

@@scenario@@

`shallow = 1` and `files = 6` are the same question answered two ways, and the gap is the bug. The
breakdown `{csv=2, md=3, txt=1}` is the evidence that the walk actually descended: those three
markdown files live two levels down, and a shallow listing could not have seen any of them.

The report also prints `dirs = 4` and `bytes = 29`. Counting directories separately matters because
`walk` returns them too — the filter is what turns "entries" into "files", and forgetting it is the
second way this report goes wrong.
:::

## Solutions

### 1. Turn a missing file into an empty result

@@sol1@@

`read` catches `NoSuchFileException` and returns `Optional.empty()`, which is the bridge from an
exception-based API to the `Optional` style of Chapter 15. `present = configured` and
`missing = (default)` are the two paths, and neither call site has a `try` in it.

The other `catch` matters as much as the first. `NoSuchFileException` is caught specifically; every
other `IOException` is wrapped in the JDK's own `UncheckedIOException` and rethrown. Catching
`IOException` broadly and returning `Optional.empty()` would turn a permission error, a full disk or
a corrupted filesystem into "no data" — which is the kind of silence that costs a day of debugging.

### 2. A per-file report, built from a sorted listing

@@sol2@@

`Files.list` is wrapped in a `try`-with-resources, materialised with `toList()`, and only then
iterated. That ordering is deliberate: it closes the directory handle before the loop does any work,
rather than holding it open for the whole report.

`Files.readAllLines(p).stream().mapToInt(...).sum()` is the counting idiom — one line per file, no
accumulator variable. The result goes into a `TreeMap` so `{a.txt=3, b.txt=4}` is sorted, and
`total = 7` is derived from the same map rather than counted a second time.

### 3. Write to a temporary file, then rename

@@sol3@@

This is the pattern to use for any file a reader might open while you are writing it. `createTempFile`
makes a uniquely named file in the *same directory* as the target — same directory so the move stays
on one filesystem and can be atomic — the content is written there, and `Files.move` with
`ATOMIC_MOVE` swaps it into place.

`files = [config.txt]` is the proof that nothing was left behind: the temporary file is gone, and the
target holds `v2`. The `finally` block deletes the temporary file even when the move failed, so a
crash mid-write cannot accumulate junk.

A reader either sees the old file or the new one. There is no state in which it sees half of either,
and that is the entire point of the extra two lines.

### 4. Read what you need, not the whole file

@@sol4@@

`readAllLines` and `lines()` give the same answers here — `line 0` first, `line 999` last, `1000`
lines — and they differ in what they hold. `readAllLines` built a `List` of a thousand `String`
objects; `Files.lines` read until the first line satisfied the question and stopped.

The file is `8890` bytes, which is small enough that either approach is fine. The reason to know the
difference is the file you will meet next week, where it is not. **Reach for `readAllLines` when you
need all the lines, and for `lines()` when you need an answer.** The stream version also composes
with everything Chapter 15 taught, which is how the log-level report above was built.

## Key takeaways

- A `Path` is an immutable name. Creating one touches nothing, and `normalize`/`relativize` are pure
  text operations that never consult the filesystem.
- A relative path is resolved against the process working directory, which a command line and a
  service do not share. Resolve once from a configured base and build the rest from it.
- `Files.writeString` truncates by default; pass `StandardOpenOption.APPEND` to add to a file.
- A file is bytes and a `String` is characters. `café — 咖啡` is 9 characters and 16 UTF-8 bytes, and
  encoding it as ISO-8859-1 loses data silently. Name the charset, or use the `Files` methods that
  default to UTF-8.
- `Files.readAllLines` materialises the file; `Files.lines` streams it and must be closed. Choose by
  whether you need all the lines or an answer.
- `Files.list` is shallow and `Files.walk` is recursive, and neither promises an order — sort before
  printing anything.
- `Files.copy` and `Files.createDirectory` refuse to overwrite an existing target;
  `Files.createDirectories` and `Files.deleteIfExists` are the idempotent versions.
- Deleting a non-empty directory throws. Neither delete method is recursive, deliberately.
- Every operation in this chapter can throw a checked `IOException`, so the compiler forces you to
  have a policy. Catch the specific exception you mean, and let the rest propagate.
- To write a file a reader may be watching, write a temporary file in the same directory and
  `Files.move` it into place with `ATOMIC_MOVE`.

## Practice

- [ ] Write a program that reads a text file and reports its line count, word count and byte count,
      then run it on a file containing a non-ASCII character and explain why the byte count is larger
      than the character count.
- [ ] Create a directory tree three levels deep, write one file in each level, then print every
      regular file as a path relative to the root — sorted.
- [ ] Take a program that writes a file with `Files.writeString` inside a loop and fix it so the file
      contains every line rather than the last one.
- [ ] Copy a file to a destination that already exists, catch the exception, then do it again with
      `REPLACE_EXISTING`. Say which behaviour you would want in a backup tool.
- [ ] Write a method that returns `Optional<String>` for a file's contents, returning empty only when
      the file does not exist, and rethrowing every other `IOException` as an unchecked exception.
- [ ] Rewrite a program that calls `Files.readAllLines` on a large file so that it uses `Files.lines`
      instead, and count how many lines it actually reads when the question can be answered early.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `Files.readAllLines(path)` for the line count, and the same list split on whitespace for the word
   count. The byte count comes from `Files.size(path)`, and it exceeds the character count because a
   non-ASCII character costs two or three bytes in UTF-8 while occupying one `char` in memory.
2. `Files.createDirectories(root.resolve("a/b/c"))` creates all three at once. Then
   `Files.walk(root).filter(Files::isRegularFile).map(root::relativize).map(Path::toString).sorted()`
   gives the listing — the `sorted` is what makes it reproducible.
3. The loop needs `StandardOpenOption.APPEND` on every call after the first, or `CREATE` plus `APPEND`
   throughout. The simplest fix is to build the whole string and write once, which also removes the
   partial-file window.
4. `Files.copy(src, dst)` throws `FileAlreadyExistsException`. A backup tool wants the *throwing*
   default for the destination it is about to overwrite, and `REPLACE_EXISTING` only for a
   destination it has already decided is disposable.
5. Catch `NoSuchFileException` and return `Optional.empty()`; catch `IOException` and throw
   `new UncheckedIOException(e)`. Returning empty for a permission failure would report "no file"
   for a file that is sitting right there.
6. With `Files.lines` and a short-circuiting terminal such as `findFirst` or `anyMatch`, the count is
   however many lines were needed to answer — often one. `readAllLines` always reads all of them.
"""

gen.write(TEMPLATE, BLOCKS)
