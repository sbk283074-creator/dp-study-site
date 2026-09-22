---
chapter: 52
part: 9
title: Untrusted Data
summary: The other half of injection -- a value that is not parsed as syntax in a statement but reconstructed as an object, a path, a tree or a length. Eight blocks counting what each format lets its content decide, which defence actually bounds it, and the two checks that measure the wrong quantity.
minutes: 100
tags: [security, deserialisation, pickle, XML entities, zip slip, tarfile, schema validation, framing, size limits, allow-lists]
---

The previous chapter was about a value that arrives where something parses it. Every example there
had the same shape: a string goes into a statement, a command, a template or a log line, and the
parser reads part of it as syntax.

This chapter is about the same mistake in the places where the syntax is not text. A serialised
object is not a description of an object -- it is a program that builds one. An archive member is not
a file, it is a name and a path. An XML document is not a tree, it is a set of rules for producing
one. In each case the value you received is a *plan*, and the question is what the plan is allowed to
say.

The eight blocks count that. Two of them are about formats that can name a function. Two are about
formats that can name a path. Two are about checks that measure the wrong quantity, which is the
failure this chapter cares most about, because a check that is enforced and measuring the wrong thing
is harder to find than a check that is missing.

## A serialised object is a program

Start with the format that is explicit about it, because the documentation says so out loud and the
mechanism is visible once you look.

A pickled object has to be reconstructible by a process that has never seen the class. So the stream
cannot describe a memory layout; it has to carry instructions. For a class that defines `__reduce__`,
those instructions are a callable and the arguments to hand it, and `loads` is the thing that does
the calling.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 1 -- the payload names the function to call.

A serialised object is not a description of an object. It is a program that
builds one, and for the classes that define __reduce__ the program is written
in terms of a callable and its arguments. That is the whole design: pickling
has to be able to reconstruct an object whose class it cannot see, so the
stream carries instructions rather than a layout.

Six payloads. Each one is a tiny class whose __reduce__ returns a callable that
is a stdlib function and arguments that are constants. None of them does
anything visible, which is the point -- the question is not what these six do,
it is that loads() will call whatever the stream names.
"""
import json
import marshal
import operator
import os
import pickle


class Payload:
    """Stand-in for the object a stream would reconstruct."""

    def __init__(self, target, args):
        self.target = target
        self.args = args

    def __reduce__(self):
        return (self.target, self.args)


# label, the callable the stream names, its arguments
PAYLOADS = [
    ("len", (len, ("abcdef",))),
    ("str.upper", (str.upper, ("abc",))),
    ("sorted", (sorted, ([3, 1, 2],))),
    ("os.path.join", (os.path.join, ("/a", "b"))),
    ("max", (max, ([1, 9, 4],))),
    ("operator.add", (operator.add, (2, 3))),
]


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print("  what each stream names            a stdlib callable + constants")
    print()
    print(f"    {'callable':<16}{'pickle.loads':>13}{'json.dumps':>12}{'marshal':>10}")

    pickle_called = 0
    json_ok = 0
    marshal_ok = 0
    for label, (fn, args) in PAYLOADS:
        try:
            pickle.loads(pickle.dumps(Payload(fn, args)))
            pickle_called += 1
            pk = "called"
        except Exception as exc:                       # noqa: BLE001
            pk = type(exc).__name__

        try:
            json.dumps(Payload(fn, args))
            json_ok += 1
            js = "ok"
        except TypeError:
            js = "refused"

        try:
            marshal.dumps(Payload(fn, args))
            marshal_ok += 1
            ms = "ok"
        except ValueError:
            ms = "refused"

        print(f"    {label:<16}{pk:>13}{js:>12}{ms:>10}")

    print()
    print("  what the six calls returned, in order")
    returned = []
    for label, (fn, args) in PAYLOADS:
        returned.append(f"{label} -> {pickle.loads(pickle.dumps(Payload(fn, args)))!r}")
    for item in returned:
        print(f"    {item}")

    print()
    print(f"  pickle.loads called the named function  {pickle_called} of "
          f"{len(PAYLOADS)}")
    print(f"  json.dumps could express                {json_ok} of "
          f"{len(PAYLOADS)}")
    print(f"  marshal.dumps could express             {marshal_ok} of "
          f"{len(PAYLOADS)}")
    print()
    print("  none of the six is a class of yours, and none of them needed")
    print("  one. the stream carries the name of the function and the")
    print("  arguments to hand it, and loads() is the thing that does the")
    print("  calling.")
    print()
    print("  the last two columns are not safer versions of the first. they")
    print("  are formats that cannot express the object at all, which is a")
    print("  different property -- and it stops being available the moment")
    print("  you need the object back.")


if __name__ == "__main__":
    main()
```

```text
  payloads                             6
  what each stream names            a stdlib callable + constants

    callable         pickle.loads  json.dumps   marshal
    len                    called     refused   refused
    str.upper              called     refused   refused
    sorted                 called     refused   refused
    os.path.join           called     refused   refused
    max                    called     refused   refused
    operator.add           called     refused   refused

  what the six calls returned, in order
    len -> 6
    str.upper -> 'ABC'
    sorted -> [1, 2, 3]
    os.path.join -> '/a/b'
    max -> 9
    operator.add -> 5

  pickle.loads called the named function  6 of 6
  json.dumps could express                0 of 6
  marshal.dumps could express             0 of 6

  none of the six is a class of yours, and none of them needed
  one. the stream carries the name of the function and the
  arguments to hand it, and loads() is the thing that does the
  calling.

  the last two columns are not safer versions of the first. they
  are formats that cannot express the object at all, which is a
  different property -- and it stops being available the moment
  you need the object back.
```

Six payloads, each one a small class whose `__reduce__` returns a stdlib function and a constant.
`pickle.loads` called all six, and the values in the output are the ones those functions return:
`6`, `'ABC'`, `[1, 2, 3]`, `'/a/b'`, `9`, `5`.

None of the six is a class of yours and none of them needed one. That is the part to sit with. The
habit of thinking about deserialisation in terms of *your* classes -- which of my classes are safe to
unpickle -- has the question backwards. The stream does not need a class of yours. It needs a
callable that exists, and the standard library has thousands of those.

The last two columns are the ones that usually get quoted as the fix, and they deserve a careful
reading. `json.dumps` and `marshal.dumps` both refused all six, but not because they are safer: they
refused because they cannot express the object at all. That is a different property, and it stops
being available the moment you need the object back. "Use JSON instead of pickle" is good advice and
it is not a defence -- it is a change of requirement.

## Four operations that run the same method

If `__reduce__` were only reached by `loads`, the rule would be one line long. It is reached by four
operations, and only one of them is called deserialisation.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 2 -- four operations that run the same method.

If __reduce__ were only reached by loads(), the rule would be "never unpickle
untrusted data" and the chapter could stop. It is reached by four operations,
and only one of them is called deserialisation. This script counts the calls
for each one.
"""
import copy
import pickle


class Payload:
    def __init__(self, log):
        self.log = log

    def __reduce__(self):
        self.log.append("reduce")
        return (len, ("ab",))


OPERATIONS = [
    ("pickle.dumps", lambda p: pickle.dumps(p)),
    ("pickle.loads", lambda p: pickle.loads(pickle.dumps(p))),
    ("copy.copy", lambda p: copy.copy(p)),
    ("copy.deepcopy", lambda p: copy.deepcopy(p)),
]


def main():
    print(f"  operations tested                  {len(OPERATIONS):>3}")
    print("  the method                         Payload.__reduce__")
    print()
    print(f"    {'operation':<16}{'calls':>7}   result")

    called = 0
    for label, fn in OPERATIONS:
        log = []
        try:
            result = fn(Payload(log))
            # a written stream is bytes; report its size, not its contents
            shown = f"{len(result)} bytes" if isinstance(result, bytes) else repr(result)
        except Exception as exc:                       # noqa: BLE001
            shown = type(exc).__name__
        if log:
            called += 1
        print(f"    {label:<16}{len(log):>7}   {shown}")

    print()
    print(f"  operations that ran __reduce__     {called} of {len(OPERATIONS)}")
    print()
    print("  dumps runs it, which is the one place the callable is not")
    print("  invoked -- the tuple is being written down rather than used.")
    print("  loads runs it, which is the case the documentation warns about.")
    print()
    print("  copy and deepcopy run it too, and neither of them is called")
    print("  deserialisation. both take an object you already have, and an")
    print("  object you already have can be one that arrived from a stream.")
    print("  the boundary is not the function name. it is whether the object")
    print("  was ever under your control.")


if __name__ == "__main__":
    main()
```

```text
  operations tested                    4
  the method                         Payload.__reduce__

    operation         calls   result
    pickle.dumps          1   40 bytes
    pickle.loads          1   2
    copy.copy             1   2
    copy.deepcopy         1   2

  operations that ran __reduce__     4 of 4

  dumps runs it, which is the one place the callable is not
  invoked -- the tuple is being written down rather than used.
  loads runs it, which is the case the documentation warns about.

  copy and deepcopy run it too, and neither of them is called
  deserialisation. both take an object you already have, and an
  object you already have can be one that arrived from a stream.
  the boundary is not the function name. it is whether the object
  was ever under your control.
```

All four ran the method exactly once. `dumps` is the one place the callable is not invoked -- the
tuple is being written down rather than used, which is why the payload survives the round trip
intact. `loads` is the case the documentation warns about.

The two worth the paragraph are `copy.copy` and `copy.deepcopy`. Neither is called deserialisation,
and both take an object you already have. That is the trap: an object you already have can be one
that arrived from a stream, or one built from a request body, or one that a library handed you. The
boundary is not the function name. It is whether the object was ever under your control, and that
question has to be answered at the point where control changed rather than at the point where the
method runs.

## The document that expands

The next three formats cannot name a function. They can name a *size*, which is the other way a
document gets to choose how much work you do.

An XML document may declare its own entities, and an entity may be defined in terms of the ones
before it. Ten references to a three-character entity gives thirty characters. Define the next entity
as ten references to that one and it gives three hundred.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 3 -- the document that expands.

An XML document may declare its own entities, and an entity may be defined in
terms of the ones before it. Ten references to an entity of three characters
gives a thirty-character value; define the next entity as ten references to
that one and it gives three hundred. The document grows by one short line per
level. The value grows by a factor of ten.

The first five levels are parsed and measured. The rest is the same arithmetic,
and it is labelled as arithmetic rather than presented as a measurement,
because parsing level nine would need three gigabytes.
"""
import xml.etree.ElementTree as ET

BASE = "lol"
FACTOR = 10
MEASURED = 5
PROJECTED = 9
THRESHOLD = 1_000_000_000


def document(depth):
    lines = [f'<!ENTITY e0 "{BASE}">']
    for level in range(1, depth + 1):
        refs = "".join(f"&e{level - 1};" for _ in range(FACTOR))
        lines.append(f'<!ENTITY e{level} "{refs}">')
    return ('<?xml version="1.0"?>\n<!DOCTYPE r [\n' + "\n".join(lines) + "\n]>\n"
            f"<r>&e{depth};</r>")


def main():
    print(f"  base entity                        {BASE!r} ({len(BASE)} chars)")
    print(f"  references per level               {FACTOR}")
    print()
    print(f"    {'depth':>6}{'document bytes':>16}{'value chars':>15}{'growth':>9}")

    previous = len(BASE)
    measured = {}
    for depth in range(1, MEASURED + 1):
        doc = document(depth)
        try:
            root = ET.fromstring(doc)
            size = len(root.text or "")
        except ET.ParseError as exc:
            print(f"    {depth:>6}{len(doc):>16}{type(exc).__name__:>15}")
            break
        measured[depth] = size
        print(f"    {depth:>6}{len(doc):>16}{size:>15,}"
              f"{size / previous:>8.0f}x")
        previous = size

    print()
    print("  the same arithmetic, carried further")
    print(f"    {'depth':>6}{'document bytes':>16}{'value chars':>15}")
    for depth in range(MEASURED + 1, PROJECTED + 1):
        doc = document(depth)
        size = len(BASE) * FACTOR ** depth
        print(f"    {depth:>6}{len(doc):>16}{size:>15,}")

    smallest = next(d for d in range(1, 30)
                    if len(BASE) * FACTOR ** d >= THRESHOLD)
    doc = document(smallest)
    print()
    print(f"  a document of {len(doc)} bytes reaches "
          f"{len(BASE) * FACTOR ** smallest:,} characters")
    print(f"  at depth {smallest} -- the first level over "
          f"{THRESHOLD:,}.")
    print()
    print("  the reader that expands this is not broken. entity expansion is")
    print("  what the declaration is for. what the format does not have is a")
    print("  budget, and a parser cannot invent one, because it does not know")
    print("  how large a value the document was entitled to.")


if __name__ == "__main__":
    main()
```

```text
  base entity                        'lol' (3 chars)
  references per level               10

     depth  document bytes    value chars   growth
         1             125             30      10x
         2             181            300      10x
         3             237          3,000      10x
         4             293         30,000      10x
         5             349        300,000      10x

  the same arithmetic, carried further
     depth  document bytes    value chars
         6             405      3,000,000
         7             461     30,000,000
         8             517    300,000,000
         9             573  3,000,000,000

  a document of 573 bytes reaches 3,000,000,000 characters
  at depth 9 -- the first level over 1,000,000,000.

  the reader that expands this is not broken. entity expansion is
  what the declaration is for. what the format does not have is a
  budget, and a parser cannot invent one, because it does not know
  how large a value the document was entitled to.
```

The document grows by one short line per level, from 125 bytes to 349, and the value grows by a
factor of ten every time -- 30, 300, 3,000, 30,000, 300,000. The five rows are parsed and measured.

The projection underneath them is arithmetic, and it is labelled as arithmetic rather than presented
as a measurement, because the point is the arithmetic. A 573-byte document reaches three billion
characters. That is a factor of about five million, chosen by whoever wrote the file, and the file is
under six hundred bytes.

The reader that expands this is not broken. Entity expansion is what the declaration is for, and the
format is doing what it says. What the format does not have is a budget -- and a parser cannot invent
one, because it does not know how large a value the document was entitled to. That is why the limit
has to come from outside the parser, and why the next two blocks are about where outside is.

## The archive member that is a path

An archive is a list of names and the bytes to write at each one. If the writer chooses the names and
the reader writes them, the writer is choosing paths in your filesystem. This is the bug the industry
named zip slip, and the useful thing to know is that it has been fixed in one of the two modules and
not the other.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 4 -- the archive member that is a path.

An archive is a list of names and the bytes to write at each one. If the writer
chooses the names and the reader writes them, the writer is choosing paths in
your filesystem. Six member names, extracted one at a time into a directory,
and the question is where each one lands.

This measures zipfile, which sanitises. The next block measures tarfile, which
takes an argument.
"""
import os
import tempfile
import zipfile

# member name, what it is trying to be
MEMBERS = [
    ("../escape.txt", "one level up"),
    ("../../escape.txt", "two levels up"),
    ("a/../../escape.txt", "up through a subdirectory"),
    ("/abs/escape.txt", "an absolute path"),
    ("..\\escape.txt", "a backslash, on POSIX"),
    ("normal.txt", "an ordinary name"),
]


def main():
    print(f"  member names                       {len(MEMBERS):>3}")
    print()
    print(f"    {'member':<22}{'lands at':<26}{'outside?':>9}")

    escaped = 0
    renamed = 0
    for name, _intent in MEMBERS:
        with tempfile.TemporaryDirectory() as td:
            archive = os.path.join(td, "x.zip")
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr(name, "owned")

            dest = os.path.join(td, "out")
            os.makedirs(dest)
            with zipfile.ZipFile(archive) as zf:
                zf.extract(name, dest)

            real_dest = os.path.realpath(dest)
            real_archive = os.path.realpath(archive)
            landed = []
            outside = False
            for root, _dirs, files in os.walk(td):
                for f in files:
                    full = os.path.realpath(os.path.join(root, f))
                    if full == real_archive:
                        continue
                    # the test is on resolved paths, not on string prefixes:
                    # a name may contain ".." and still be inside
                    inside = full == real_dest or full.startswith(
                        real_dest + os.sep)
                    if not inside:
                        outside = True
                    landed.append(os.path.relpath(full, real_dest))

            if outside:
                escaped += 1
            if landed and sorted(landed)[0] != name:
                renamed += 1

            shown = ", ".join(sorted(landed)) if landed else "(nothing written)"
            print(f"    {name:<22}{shown:<26}"
                  f"{'YES' if outside else 'no':>9}")

    print()
    print(f"  members that escaped the destination   {escaped} of "
          f"{len(MEMBERS)}")
    print(f"  members that landed under a new name   {renamed} of "
          f"{len(MEMBERS)}")
    print()
    print("  zipfile.extract sanitises the name before it writes: it drops")
    print("  the path parts that would move the write, so nothing leaves the")
    print("  destination. that is a real fix and it has been in the standard")
    print("  library for a long time.")
    print()
    print("  read the second column anyway. four of the six landed somewhere")
    print("  other than where they asked to, and two of them created a")
    print("  directory the member never named -- the absolute path became a")
    print("  relative subdirectory called 'abs'. and the backslash survived")
    print("  as a literal character in a filename, which is not an escape on")
    print("  this platform and is an escape on another. a sanitiser removes")
    print("  the traversal; it does not promise that the name you get is the")
    print("  name you asked for.")


if __name__ == "__main__":
    main()
```

```text
  member names                         6

    member                lands at                   outside?
    ../escape.txt         escape.txt                       no
    ../../escape.txt      escape.txt                       no
    a/../../escape.txt    a/escape.txt                     no
    /abs/escape.txt       abs/escape.txt                   no
    ..\escape.txt         ..\escape.txt                    no
    normal.txt            normal.txt                       no

  members that escaped the destination   0 of 6
  members that landed under a new name   4 of 6

  zipfile.extract sanitises the name before it writes: it drops
  the path parts that would move the write, so nothing leaves the
  destination. that is a real fix and it has been in the standard
  library for a long time.

  read the second column anyway. four of the six landed somewhere
  other than where they asked to, and two of them created a
  directory the member never named -- the absolute path became a
  relative subdirectory called 'abs'. and the backslash survived
  as a literal character in a filename, which is not an escape on
  this platform and is an escape on another. a sanitiser removes
  the traversal; it does not promise that the name you get is the
  name you asked for.
```

Zero of the six members escaped. `zipfile.extract` sanitises the name before it writes, dropping the
path parts that would move the write, and it has done that for a long time.

Read the second column anyway, because "sanitised" is not the same as "unchanged". Four of the six
landed somewhere other than where they asked to. The absolute path did not escape -- it became a
relative subdirectory called `abs`, a directory the member never named. And the backslash survived as
a literal character in a filename, which is not an escape on this platform and is an escape on
another one.

So the sanitiser removes the traversal and makes no promise that the name you get is the name you
asked for. For a backup restore that is fine. For an import feature whose manifest is supposed to
describe what was unpacked, it is a correctness problem that happens to have been found by looking
for a security one.

## The format that asks you to choose

`tarfile` does not sanitise, and the reason is not an oversight. Tar has to be able to represent the
archives that already exist -- absolute paths, links that point out of the tree, device nodes -- and
refusing them would make the module unable to read its own format.

So `tarfile` asks. Each member is offered to a filter, and the filter returns a possibly-rewritten
member or raises.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 5 -- the archive format that asks you to choose.

zipfile sanitises member names on the way out and has done for a long time.
tarfile does not, because tar has to be able to represent the archives that
already exist -- absolute paths, links that point out of the tree, device nodes
-- and refusing them would make the module unable to read its own format.

So tarfile asks. Each member is offered to a filter, and the filter returns a
possibly-rewritten member or raises. Three filters ship with the module, and
this script runs the same seven members through all three.

The filters are called directly here rather than through extractall, so nothing
is written to the filesystem and the result is a property of the filter alone.
"""
import tarfile

DEST = "/srv/app/uploads"

# member name, mode, type
MEMBERS = [
    ("../escape.txt", 0o644, tarfile.REGTYPE),
    ("../../escape.txt", 0o644, tarfile.REGTYPE),
    ("a/../../escape.txt", 0o644, tarfile.REGTYPE),
    ("/abs/escape.txt", 0o644, tarfile.REGTYPE),
    ("normal.txt", 0o644, tarfile.REGTYPE),
    ("setuid", 0o4755, tarfile.REGTYPE),
    ("device", 0o644, tarfile.CHRTYPE),
]

FILTERS = [
    ("fully_trusted", tarfile.fully_trusted_filter),
    ("tar", tarfile.tar_filter),
    ("data", tarfile.data_filter),
]


def main():
    print(f"  members                            {len(MEMBERS):>3}")
    print(f"  destination                        {DEST}")
    print(f"  filters                            {len(FILTERS)}")
    print()
    print(f"    {'member':<20}{'fully_trusted':>15}{'tar':>10}{'data':>10}")

    rejected = {name: 0 for name, _ in FILTERS}
    rewritten = []
    survivors = []
    for mname, mode, mtype in MEMBERS:
        cells = []
        for fname, fn in FILTERS:
            member = tarfile.TarInfo(mname)
            member.mode, member.type = mode, mtype
            try:
                out = fn(member, DEST)
                cells.append("accepted")
                if out.name != mname:
                    rewritten.append((fname, mname, out.name))
                if fname == FILTERS[-1][0] and mname != "normal.txt":
                    survivors.append(mname)
            except tarfile.TarError:
                cells.append("rejected")
                rejected[fname] += 1
        print(f"    {mname:<20}{cells[0]:>15}{cells[1]:>10}{cells[2]:>10}")

    print()
    for name, _ in FILTERS:
        print(f"  {name:<14} rejected {rejected[name]:>2} of {len(MEMBERS)}")

    print()
    print("  members a filter accepted under a different name")
    for fname, was, now in rewritten:
        print(f"    {fname:<14} {was} -> {now}")
    if not rewritten:
        print("    (none)")

    print()
    print("  members the strictest filter still accepts, other than the")
    print("  ordinary one")
    for mname in survivors:
        print(f"    {mname}")

    print()
    print("  read the third column against the fourth. the two filters")
    print("  reject the same three traversals, and the difference between")
    print("  them is one member: the character device, which the strictest")
    print("  filter refuses because a device node is not a file you can")
    print("  write a payload into -- it is a handle to something else.")
    print()
    print("  two things neither filter does. the absolute path is not")
    print("  rejected, it is rewritten into a relative one, so the member")
    print("  lands somewhere -- just not where it asked. and the setuid")
    print("  member passes both, because a permission bit is not a path")
    print("  and neither filter is looking at permissions.")
    print()
    print("  the safe option is not the default. `extractall` without a")
    print("  filter uses fully_trusted, which is named for what it does,")
    print("  and the caller is the one who has to say otherwise.")


if __name__ == "__main__":
    main()
```

```text
  members                              7
  destination                        /srv/app/uploads
  filters                            3

    member                fully_trusted       tar      data
    ../escape.txt              accepted  rejected  rejected
    ../../escape.txt           accepted  rejected  rejected
    a/../../escape.txt         accepted  rejected  rejected
    /abs/escape.txt            accepted  accepted  accepted
    normal.txt                 accepted  accepted  accepted
    setuid                     accepted  accepted  accepted
    device                     accepted  accepted  rejected

  fully_trusted  rejected  0 of 7
  tar            rejected  3 of 7
  data           rejected  4 of 7

  members a filter accepted under a different name
    tar            /abs/escape.txt -> abs/escape.txt
    data           /abs/escape.txt -> abs/escape.txt

  members the strictest filter still accepts, other than the
  ordinary one
    /abs/escape.txt
    setuid

  read the third column against the fourth. the two filters
  reject the same three traversals, and the difference between
  them is one member: the character device, which the strictest
  filter refuses because a device node is not a file you can
  write a payload into -- it is a handle to something else.

  two things neither filter does. the absolute path is not
  rejected, it is rewritten into a relative one, so the member
  lands somewhere -- just not where it asked. and the setuid
  member passes both, because a permission bit is not a path
  and neither filter is looking at permissions.

  the safe option is not the default. `extractall` without a
  filter uses fully_trusted, which is named for what it does,
  and the caller is the one who has to say otherwise.
```

Three filters, and the progression is 0, 3, 4 out of seven. `fully_trusted` refuses nothing and is
named for what it does. `tar` refuses the three members that walk upward. `data` refuses those three
and one more: the character device, because a device node is not a file you can write a payload into
-- it is a handle to something else.

Two things neither filter does, and both are in the output. The absolute path is not rejected; it is
*rewritten*, so the member lands somewhere, just not where it asked. And the setuid member passes
both filters, because a permission bit is not a path and neither filter is looking at permissions.
That second one is not a bug in the filter. It is the edge of what a path filter can be asked to do.

The line that matters is the last one. The safe option is not the default: `extractall` with no
filter uses `fully_trusted`, and the caller is the one who has to say otherwise. A default that is
safe only when named is a default that gets used unnamed.

## Validation is a boundary, and a boundary has a shape

At this point the advice that replaces all the rest is "validate your input", and it is not wrong. It
is underspecified, because a validator is a predicate and the useful question about a predicate is
how many of the inputs you do not want it accepts.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 6 -- validation is a boundary, and a boundary has a shape.

"Validate your input" is the advice that replaces every other piece of advice in
this chapter, and it is not wrong. It is underspecified. A validator is a
predicate, and the useful question about a predicate is how many of the bodies
you do not want it accepts.

Twelve request bodies, three of which are legitimate. Three validators, each a
strict superset of the one above it, and the count of hostile bodies each one
lets through.
"""
REQUIRED = {"name": str, "age": int, "email": str}
MAX_LEN = {"name": 32, "email": 64}
ALLOWED = set(REQUIRED)

# label, body, is it legitimate
BODIES = [
    ("ada", {"name": "ada", "age": 36, "email": "ada@example.com"}, True),
    ("grace", {"name": "grace", "age": 45, "email": "grace@example.com"}, True),
    ("alan", {"name": "alan", "age": 41, "email": "alan@example.com"}, True),
    ("no name", {"age": 36, "email": "a@b.c"}, False),
    ("no age", {"name": "ada", "email": "a@b.c"}, False),
    ("name=5", {"name": 5, "age": 36, "email": "a@b.c"}, False),
    ("age='36'", {"name": "ada", "age": "36", "email": "a@b.c"}, False),
    ("age=True", {"name": "ada", "age": True, "email": "a@b.c"}, False),
    ("name 100 chars", {"name": "a" * 100, "age": 36, "email": "a@b.c"}, False),
    ("extra key", {"name": "ada", "age": 36, "email": "a@b.c", "role": "admin"}, False),
    ("age=-1", {"name": "ada", "age": -1, "email": "a@b.c"}, False),
    ("name=None", {"name": None, "age": 36, "email": "a@b.c"}, False),
]


def presence(body):
    return all(k in body for k in REQUIRED)


def with_types(body):
    if not presence(body):
        return False
    return all(isinstance(body[k], t) for k, t in REQUIRED.items())


def with_bounds(body):
    if not with_types(body):
        return False
    if set(body) - ALLOWED:                    # no keys you did not ask for
        return False
    if any(type(body[k]) is not t for k, t in REQUIRED.items()):
        return False                           # bool is an int; this is not
    if not all(len(body[k]) <= MAX_LEN[k] for k in MAX_LEN):
        return False
    return 0 <= body["age"] <= 150


VALIDATORS = [
    ("presence", presence),
    ("+ types", with_types),
    ("+ bounds", with_bounds),
]


def main():
    legit = sum(1 for _, _, ok in BODIES if ok)
    print(f"  bodies                             {len(BODIES):>3}")
    print(f"  legitimate                         {legit:>3}")
    print(f"  hostile                            {len(BODIES) - legit:>3}")
    print(f"  the strictest validator checks      keys, types, "
          f"{len(MAX_LEN)} length limits, 1 range")
    print()
    print(f"    {'body':<18}{'presence':>10}{'+ types':>9}{'+ bounds':>10}")

    accepted = {name: 0 for name, _ in VALIDATORS}
    hostile_accepted = {name: 0 for name, _ in VALIDATORS}
    for label, body, ok in BODIES:
        cells = []
        for name, fn in VALIDATORS:
            passed = fn(body)
            cells.append("pass" if passed else "reject")
            if passed:
                accepted[name] += 1
                if not ok:
                    hostile_accepted[name] += 1
        print(f"    {label:<18}{cells[0]:>10}{cells[1]:>9}{cells[2]:>10}")

    print()
    for name, _ in VALIDATORS:
        print(f"  {name:<12} accepts {accepted[name]:>2} of {len(BODIES)}"
              f"   ({hostile_accepted[name]} of them hostile)")

    print()
    print("  the strictest one accepts the three legitimate bodies and")
    print("  nothing else, which is what a boundary is supposed to do. the")
    print("  interesting column is the middle one.")
    print()
    print("  presence alone accepts seven hostile bodies, and the reason is")
    print("  not carelessness -- a body with every key present and the wrong")
    print("  type in each is a well-formed body. checking the types removes")
    print("  four of the seven and leaves one that no amount of isinstance")
    print("  will catch, because in Python `True` is an `int`.")
    print()
    print("  that is the shape of the problem. each validator is a strict")
    print("  superset of the last, and each one closes some of the gap. what")
    print("  none of them does is tell you how much gap is left, which is")
    print("  why the number is worth writing down next to the validator.")


if __name__ == "__main__":
    main()
```

```text
  bodies                              12
  legitimate                           3
  hostile                              9
  the strictest validator checks      keys, types, 2 length limits, 1 range

    body                presence  + types  + bounds
    ada                     pass     pass      pass
    grace                   pass     pass      pass
    alan                    pass     pass      pass
    no name               reject   reject    reject
    no age                reject   reject    reject
    name=5                  pass   reject    reject
    age='36'                pass   reject    reject
    age=True                pass     pass    reject
    name 100 chars          pass     pass    reject
    extra key               pass     pass    reject
    age=-1                  pass     pass    reject
    name=None               pass   reject    reject

  presence     accepts 10 of 12   (7 of them hostile)
  + types      accepts  7 of 12   (4 of them hostile)
  + bounds     accepts  3 of 12   (0 of them hostile)

  the strictest one accepts the three legitimate bodies and
  nothing else, which is what a boundary is supposed to do. the
  interesting column is the middle one.

  presence alone accepts seven hostile bodies, and the reason is
  not carelessness -- a body with every key present and the wrong
  type in each is a well-formed body. checking the types removes
  four of the seven and leaves one that no amount of isinstance
  will catch, because in Python `True` is an `int`.

  that is the shape of the problem. each validator is a strict
  superset of the last, and each one closes some of the gap. what
  none of them does is tell you how much gap is left, which is
  why the number is worth writing down next to the validator.
```

Twelve bodies, three legitimate. Presence alone accepted ten, seven of which were hostile -- and the
reason is not carelessness. A body with every key present and the wrong type in each is a well-formed
body; nothing about its shape is wrong.

Checking the types removed four of the seven and left one. That one is `age=True`, and no amount of
`isinstance` will catch it, because in Python `True` is an `int`. Only an exact-type comparison
catches it, and the third validator uses one.

The third column accepts the three legitimate bodies and nothing else, which is what a boundary is
supposed to do. But look at the shape of the progression rather than the endpoint: each validator is
a strict superset of the one above it, each one closes part of the gap, and none of them tells you
how much gap is left. That is why the number is worth writing down next to the validator -- not as
documentation, but because it is the only thing that will tell you when it changes.

## Reviving an object, the safe way

The goal that gets people to `pickle` in the first place is legitimate. A record in a stream names a
type, and something has to turn that record back into an object of that type. The unsafe way is to
let the record choose the type. The safe way is to let it name a type and then look that name up in a
dictionary you wrote.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 7 -- reviving an object, the safe way.

The goal that gets people to pickle is legitimate: a record in a stream names a
type, and something has to turn that record back into an object of that type.
The unsafe way to do it is to let the record choose the type. The safe way is to
let the record name a type and then look that name up in a dictionary you wrote.

Eight records. Four name a type the application has, three name a builtin
function, and one names something that does not exist. Two resolvers: an
allow-list, and the dynamic one that looks the name up in the builtins module.

Nothing hostile is called. The question is only whether the name resolves, which
is the step that decides whether it would be.
"""
import builtins
import json


class User:
    def __init__(self, name):
        self.name = name


class Note:
    def __init__(self, body):
        self.body = body


class Tag:
    def __init__(self, label):
        self.label = label


class Setting:
    def __init__(self, key):
        self.key = key


REGISTRY = {"User": User, "Note": Note, "Tag": Tag, "Setting": Setting}

RECORDS = [
    {"__type__": "User", "name": "ada"},
    {"__type__": "Note", "body": "milk"},
    {"__type__": "Tag", "label": "home"},
    {"__type__": "Setting", "key": "theme"},
    {"__type__": "eval", "expr": "1 + 1"},
    {"__type__": "open", "path": "/etc/hosts"},
    {"__type__": "exec", "code": "pass"},
    {"__type__": "Widget", "size": 3},
]


def build(record):
    """Construct from an allow-list. The name is a key, not a decision."""
    cls = REGISTRY.get(record["__type__"])
    if cls is None:
        raise KeyError(record["__type__"])
    return cls(**{k: v for k, v in record.items() if k != "__type__"})


def main():
    print(f"  records                            {len(RECORDS):>3}")
    print(f"  types in the allow-list            {len(REGISTRY):>3}")
    print()
    print(f"    {'type named':<14}{'allow-list':>13}{'getattr(builtins)':>20}")

    allow_resolved, dynamic_resolved, off_list = 0, 0, 0
    for record in RECORDS:
        name = record["__type__"]
        on_list = name in REGISTRY
        # resolution only: the question is whether the name is reachable,
        # not whether the call that follows it would have succeeded
        in_builtins = hasattr(builtins, name)
        if on_list:
            allow_resolved += 1
        if in_builtins:
            dynamic_resolved += 1
            if not on_list:
                off_list += 1
        print(f"    {name:<14}{'resolves' if on_list else 'no such name':>13}"
              f"{'RESOLVES' if in_builtins else 'no such name':>20}")

    built = sum(1 for r in RECORDS if r["__type__"] in REGISTRY
                and build(r) is not None)

    print()
    print(f"  allow-list resolves                 {allow_resolved:>3} of "
          f"{len(RECORDS)}   ({len(REGISTRY) - allow_resolved} not in the list)")
    print(f"  getattr(builtins, ...) resolves     {dynamic_resolved:>3} of "
          f"{len(RECORDS)}   ({off_list} of them not in the list)")
    print(f"  objects the allow-list built        {built:>3} of {len(RECORDS)}")

    print()
    print("  the allow-list resolves the four the application has and none")
    print("  of the others, so the names it can reach are the names you")
    print("  wrote down. it also builds all four, because a record whose")
    print("  fields match the constructor is a record the constructor can")
    print("  use.")
    print()
    print("  the dynamic resolver resolves none of the application's types")
    print("  -- none of them is a builtin -- and all three of the ones that")
    print("  are. it is worse than the allow-list in both directions at")
    print("  once, which is the usual shape of a resolver that trusts the")
    print("  input to name its own type. nothing hostile was called here;")
    print("  resolution is the step that decides whether it would be.")
    print()
    print("  this is the constructive half of the chapter. the record may")
    print("  carry a name; it may not carry a decision. the name is a key")
    print("  into a dictionary you wrote, which is the same fix as the sort")
    print("  key in the previous chapter.")


if __name__ == "__main__":
    main()
```

```text
  records                              8
  types in the allow-list              4

    type named       allow-list   getattr(builtins)
    User               resolves        no such name
    Note               resolves        no such name
    Tag                resolves        no such name
    Setting            resolves        no such name
    eval           no such name            RESOLVES
    open           no such name            RESOLVES
    exec           no such name            RESOLVES
    Widget         no such name        no such name

  allow-list resolves                   4 of 8   (0 not in the list)
  getattr(builtins, ...) resolves       3 of 8   (3 of them not in the list)
  objects the allow-list built          4 of 8

  the allow-list resolves the four the application has and none
  of the others, so the names it can reach are the names you
  wrote down. it also builds all four, because a record whose
  fields match the constructor is a record the constructor can
  use.

  the dynamic resolver resolves none of the application's types
  -- none of them is a builtin -- and all three of the ones that
  are. it is worse than the allow-list in both directions at
  once, which is the usual shape of a resolver that trusts the
  input to name its own type. nothing hostile was called here;
  resolution is the step that decides whether it would be.

  this is the constructive half of the chapter. the record may
  carry a name; it may not carry a decision. the name is a key
  into a dictionary you wrote, which is the same fix as the sort
  key in the previous chapter.
```

Eight records. The allow-list resolved the four the application has and none of the other four,
including the three that name a builtin. It also built all four, because a record whose fields match
the constructor is a record the constructor can use.

The dynamic resolver resolved none of the application's types -- none of them is a builtin -- and all
three of the ones that are. It is worse than the allow-list in both directions at once, which is the
usual shape of a resolver that trusts the input to name its own type.

Nothing hostile was called in that block, and the measurement is deliberately of resolution rather
than of invocation. Resolution is the step that decides whether it *would* be called, so it is the
step worth counting, and it is countable without doing anything dangerous.

## The length you were told

The last format cannot name a function and cannot name a path. It names a *length*, and the reader
uses that number to decide how many bytes belong to this message.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 8 -- the length you were told is not the length you get.

A stream of messages needs framing, and the cheap framing is to write the length
first. That puts a number from the sender into the reader's control flow: the
reader uses it to decide how many bytes belong to this message.

Seven messages. Four are honest, three declare a length that does not match the
bytes that follow, and one of those is honest-but-huge. Two readers: one that
believes the number, and one that reads to the delimiter and then checks the
number against what it actually got.
"""
LIMIT = 1024

# declared length, the bytes that actually follow
FRAMES = [
    (5, b"hello"),
    (2000, b"x" * 2000),
    (3, b"hello"),
    (9, b"hello"),
    (4, b"abcd"),
    (2, b"abcd"),
    (6, b"abcdef"),
]


def stream():
    return b"".join(f"{n}\n".encode() + body + b"\n" for n, body in FRAMES)


def read_trusting(data, frames):
    """Take the declared length as the number of bytes to read.

    Frames are appended as they are read, so a caller that catches the
    exception can still see how far this reader got before it died.
    """
    i = 0
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        body = data[i:i + declared]
        i += declared
        trailer = data[i:i + 1]
        i += 1
        frames.append((declared, body, trailer))


def read_bounded(data, limit):
    """Read to the delimiter, then check the declaration against it."""
    i = 0
    accepted, rejected = [], []
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        k = data.index(b"\n", i)
        body = data[i:k]
        i = k + 1
        if len(body) != declared:
            rejected.append((declared, len(body), "declared length"))
        elif declared > limit:
            rejected.append((declared, len(body), "over the limit"))
        else:
            accepted.append((declared, body))
    return accepted, rejected


def main():
    data = stream()
    print(f"  messages sent                      {len(FRAMES):>3}")
    print(f"  bytes on the wire                  {len(data):>3}")
    print(f"  declared length limit              {LIMIT:>3}")
    print()

    trusted = []
    stop = "-"
    try:
        read_trusting(data, trusted)
    except ValueError as exc:
        stop = f"ValueError: {exc}"

    accepted, rejected = read_bounded(data, LIMIT)

    print(f"    {'reader':<30}{'frames':>7}{'consistent':>12}"
          f"{'misaligned':>12}")
    good = sum(1 for _d, _b, trailer in trusted if trailer == b"\n")
    print(f"    {'trusts the declared length':<30}{len(trusted):>7}"
          f"{good:>12}{len(trusted) - good:>12}")
    print(f"    {'reads to the delimiter':<30}{len(accepted) + len(rejected):>7}"
          f"{len(accepted):>12}{0:>12}")

    print()
    print("  the reader that believes the number")
    for declared, body, trailer in trusted:
        mark = "consistent" if trailer == b"\n" else "MISALIGNED"
        print(f"    declared {declared:>5}  read {len(body):>5} bytes  "
              f"next byte {trailer!r:>6}  {mark}")
    print(f"    and then it stopped: {stop}")

    print()
    print("  the reader that reads to the delimiter")
    print(f"    accepted {len(accepted)} of {len(FRAMES)}")
    for declared, got, why in rejected:
        print(f"    rejected  declared {declared:>5}  got {got:>5} bytes"
              f"  {why}")

    print()
    print("  the first reader gets one message wrong and then cannot")
    print("  continue, because the bytes it did not read are now standing")
    print("  where a length is supposed to be. it read 'o' and tried to")
    print("  parse it as a number. that is the part worth carrying: a")
    print("  framing bug is not a wrong message, it is the end of the")
    print("  stream, and everything after the mistake is attributed to the")
    print("  wrong sender.")
    print()
    print("  the second reader never has that problem, because the")
    print("  delimiter decides where a message ends and the number is only")
    print("  ever a claim to be checked. it also gets the size limit for")
    print("  free, which the first reader has no way to apply: one")
    print("  consistent message of two thousand bytes is a perfectly")
    print("  well-formed frame, and it is still two thousand bytes.")


if __name__ == "__main__":
    main()
```

```text
  messages sent                        7
  bytes on the wire                  2053
  declared length limit              1024

    reader                         frames  consistent  misaligned
    trusts the declared length          3           2           1
    reads to the delimiter              7           3           0

  the reader that believes the number
    declared     5  read     5 bytes  next byte  b'\n'  consistent
    declared  2000  read  2000 bytes  next byte  b'\n'  consistent
    declared     3  read     3 bytes  next byte   b'l'  MISALIGNED
    and then it stopped: ValueError: invalid literal for int() with base 10: b'o'

  the reader that reads to the delimiter
    accepted 3 of 7
    rejected  declared  2000  got  2000 bytes  over the limit
    rejected  declared     3  got     5 bytes  declared length
    rejected  declared     9  got     5 bytes  declared length
    rejected  declared     2  got     4 bytes  declared length

  the first reader gets one message wrong and then cannot
  continue, because the bytes it did not read are now standing
  where a length is supposed to be. it read 'o' and tried to
  parse it as a number. that is the part worth carrying: a
  framing bug is not a wrong message, it is the end of the
  stream, and everything after the mistake is attributed to the
  wrong sender.

  the second reader never has that problem, because the
  delimiter decides where a message ends and the number is only
  ever a claim to be checked. it also gets the size limit for
  free, which the first reader has no way to apply: one
  consistent message of two thousand bytes is a perfectly
  well-formed frame, and it is still two thousand bytes.
```

Two readers, seven messages, four of them honest and three of them declaring a length that does not
match the bytes that follow.

The reader that trusts the number read three frames, got two of them right, and then died on
`ValueError` -- because it took three bytes of a five-byte message, left the remaining two standing
where the next length should be, and tried to parse the letter `o` as a number.

That is the part worth carrying, and it is not "one message was wrong". The bytes it did not read are
not lost. They are misattributed: everything downstream of this reader sees them as part of something
else, and every message after the mistake is attributed to the wrong sender. A framing bug is a
misattribution bug, and the second reader never has it, because the delimiter decides where a message
ends and the number is only ever a claim to be checked.

The second reader also gets the size limit for free. The 2000-byte message is a *perfectly
well-formed frame* -- declared length and actual length agree -- and it is still two thousand bytes.
The first reader has no way to apply a size limit at all, because it never looks at the actual length
of anything.

:::pitfall The limit is on the bytes you received

Everything so far has been about what a format can carry. This is about the check that is supposed to
bound the damage, and the mistake is not that the check is missing.

An upload endpoint with a four-kilobyte limit. Six documents, three ordinary and three with entity
declarations.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 9 -- the limit is on the bytes you received.

Everything so far has been about a format that can carry more than data. This
is about the check that is supposed to bound the damage, and the mistake is not
that the check is wrong. It is that the check is on a different quantity from
the one that costs.

An upload endpoint with a four-kilobyte limit. Six documents, three ordinary
and three with entity declarations. Every one of them is well under the limit,
and the number that matters is not on the same axis as the number being checked.

The expansion figures for the three large documents are arithmetic from the
factor measured in part 3, not measurements -- parsing the middle one would need
three gigabytes.
"""
import xml.etree.ElementTree as ET

LIMIT_BYTES = 4096
BUDGET_CHARS = 100_000_000
BASE = "lol"
FACTOR = 10
ANCHOR = 4          # the depth that is actually parsed, as a check on the factor


def entity_document(depth):
    lines = [f'<!ENTITY e0 "{BASE}">']
    for level in range(1, depth + 1):
        refs = "".join(f"&e{level - 1};" for _ in range(FACTOR))
        lines.append(f'<!ENTITY e{level} "{refs}">')
    return ('<?xml version="1.0"?>\n<!DOCTYPE r [\n' + "\n".join(lines) + "\n]>\n"
            f"<r>&e{depth};</r>")


def plain_document(title):
    return ('<?xml version="1.0"?>\n'
            f"<note><title>{title}</title><body>nothing here</body></note>")


def uploads():
    rows = [
        ("notes.xml", plain_document("notes"), None),
        ("export.xml", plain_document("export"), None),
        ("backup.xml", plain_document("backup"), None),
        ("config.xml", entity_document(8), 8),
        ("theme.xml", entity_document(9), 9),
        ("report.xml", entity_document(10), 10),
    ]
    return rows


def main():
    # one real parse, to check the factor the projections rest on
    anchor = entity_document(ANCHOR)
    anchor_chars = len(ET.fromstring(anchor).text or "")

    print(f"  upload limit                       {LIMIT_BYTES:>5} bytes")
    print(f"  processing budget                  {BUDGET_CHARS:,} characters")
    print(f"  factor per entity level            {FACTOR:>5}x")
    print(f"  checked by parsing depth {ANCHOR}        {anchor_chars:>5} characters")
    print()
    print(f"    {'file':<14}{'bytes':>7}{'under limit':>13}"
          f"{'chars after parse':>19}{'over budget':>13}")

    under = 0
    over = 0
    flagged = 0
    largest = 0
    for name, doc, depth in uploads():
        size = len(doc.encode())
        chars = (len(BASE) * FACTOR ** depth) if depth else len(doc)
        is_under = size <= LIMIT_BYTES
        is_over = chars > BUDGET_CHARS
        has_dtd = b"<!ENTITY" in doc.encode()
        under += is_under
        over += is_over
        flagged += has_dtd
        largest = max(largest, size)
        print(f"    {name:<14}{size:>7}{'yes' if is_under else 'no':>13}"
              f"{chars:>19,}{'yes' if is_over else 'no':>13}")

    print()
    print(f"  documents under the upload limit      {under:>2} of "
          f"{len(uploads())}")
    print(f"  documents over the processing budget  {over:>2} of "
          f"{len(uploads())}")
    print(f"  documents carrying a DTD              {flagged:>2} of "
          f"{len(uploads())}")

    print()
    print("  the endpoint is not missing a check. it has one, the check is")
    print("  enforced, and every document passes it honestly -- the largest")
    print(f"  of the six is {largest} bytes.")
    print()
    print("  the problem is that the check is on the bytes received and the")
    print("  cost is on the value produced, and the format lets those two")
    print("  numbers be different by a factor the sender chooses. a limit on")
    print("  one of them is not a limit on the other.")
    print()
    print("  the third count is the one that would have worked. refusing a")
    print("  document that declares its own entities catches all three, and")
    print("  it is a property of the document rather than of the value, so")
    print("  it can be decided before anything is expanded.")


if __name__ == "__main__":
    main()
```

```text
  upload limit                        4096 bytes
  processing budget                  100,000,000 characters
  factor per entity level               10x
  checked by parsing depth 4        30000 characters

    file            bytes  under limit  chars after parse  over budget
    notes.xml          80          yes                 80           no
    export.xml         81          yes                 81           no
    backup.xml         81          yes                 81           no
    config.xml        517          yes        300,000,000          yes
    theme.xml         573          yes      3,000,000,000          yes
    report.xml        631          yes     30,000,000,000          yes

  documents under the upload limit       6 of 6
  documents over the processing budget   3 of 6
  documents carrying a DTD               3 of 6

  the endpoint is not missing a check. it has one, the check is
  enforced, and every document passes it honestly -- the largest
  of the six is 631 bytes.

  the problem is that the check is on the bytes received and the
  cost is on the value produced, and the format lets those two
  numbers be different by a factor the sender chooses. a limit on
  one of them is not a limit on the other.

  the third count is the one that would have worked. refusing a
  document that declares its own entities catches all three, and
  it is a property of the document rather than of the value, so
  it can be decided before anything is expanded.
```

Every document passes the limit, and it passes honestly -- the largest of the six is 631 bytes. The
endpoint is not missing a check, the check is enforced, and the three documents that matter are three
of the smallest files in the table.

The problem is that the check is on the bytes received and the cost is on the value produced, and the
format lets those two numbers be different by a factor the sender chooses. Three of the six are over
a hundred-million-character budget. A limit on one of those quantities is not a limit on the other,
and no amount of care at the upload form closes the gap, because the upload form is not where the
value is produced.

The third count is the one that would have worked. Refusing a document that declares its own entities
catches all three, and it is a property of the *document* rather than of the value, so it can be
decided before anything is expanded. The rule to generalise: when a limit is on one quantity and the
cost is on another, the check has to move to something both of them are derived from.

:::

:::scenario The import feature that takes four formats

An import feature is where this chapter stops being theoretical, because it is the one feature whose
entire job is to accept a file from a user and act on what is inside it. This one accepts four
formats, and its validation is an extension check and a size check -- the two checks that are about
the file rather than about the content.

```python run
#!/usr/bin/env python3
"""Chapter 52 demo, part 10 -- the import feature that takes four formats.

An "import your data" feature is the place where this chapter stops being
theoretical, because it is the one feature whose entire job is to accept a file
from a user and act on what is inside it. This one accepts four formats, and the
validation is an extension check and a size check, which are the two checks that
are about the file rather than about the content.

Eight uploads, two per format. Each one is offered to the feature's validation
and then to three detectors, one per capability the chapter has been counting: a
member name that is a path, an opcode that names a callable, and a declaration
that expands.
"""
import io
import pickle
import pickletools
import tarfile
import xml.etree.ElementTree as ET

ALLOWED_EXT = {".json", ".xml", ".tar", ".pkl"}
MAX_BYTES = 64 * 1024


class Export:
    def __init__(self, rows):
        self.rows = rows


def json_upload():
    return [b'{"rows": [1, 2, 3]}', b'[{"id": 1}, {"id": 2}]']


def xml_upload():
    def doc(depth):
        lines = ['<!ENTITY e0 "lol">']
        for level in range(1, depth + 1):
            lines.append(f'<!ENTITY e{level} "'
                         + "".join(f"&e{level - 1};" for _ in range(10)) + '">')
        return ('<?xml version="1.0"?>\n<!DOCTYPE r [\n' + "\n".join(lines)
                + "\n]>\n" + f"<r>&e{depth};</r>")
    return [doc(3).encode(), doc(4).encode()]


def tar_upload():
    out = []
    for name in ("../rows.csv", "a/../../rows.csv"):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            data = b"1,2,3"
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        out.append(buf.getvalue())
    return out


def pickle_upload():
    return [pickle.dumps(Export([1, 2, 3])), pickle.dumps(Export([]))]


def carries_a_path(data, ext):
    if ext != ".tar":
        return False
    try:
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            return any(n.startswith("/") or ".." in n.split("/")
                       for n in tf.getnames())
    except tarfile.TarError:
        return False


def carries_a_callable(data, ext):
    if ext != ".pkl":
        return False
    try:
        return any(op.name in ("GLOBAL", "STACK_GLOBAL")
                   for op, _arg, _pos in pickletools.genops(data))
    except (ValueError, pickle.UnpicklingError):
        return False


def carries_an_expansion(data, ext):
    return ext == ".xml" and b"<!ENTITY" in data


def main():
    groups = [
        (".json", json_upload()),
        (".xml", xml_upload()),
        (".tar", tar_upload()),
        (".pkl", pickle_upload()),
    ]
    uploads = [(ext, data) for ext, datas in groups for data in datas]

    print(f"  formats accepted                   {len(groups):>3}")
    print(f"  uploads                            {len(uploads):>3}")
    print(f"  the feature's checks               extension, "
          f"{MAX_BYTES // 1024} KB")
    print()
    print(f"    {'upload':<12}{'bytes':>7}{'accepted':>10}{'path':>7}"
          f"{'callable':>10}{'expands':>9}")

    accepted = 0
    dangerous = 0
    for i, (ext, data) in enumerate(uploads, start=1):
        ok = ext in ALLOWED_EXT and len(data) <= MAX_BYTES
        path = carries_a_path(data, ext)
        call = carries_a_callable(data, ext)
        exp = carries_an_expansion(data, ext)
        accepted += ok
        if path or call or exp:
            dangerous += 1
        label = f"import-{i}{ext}"
        print(f"    {label:<12}{len(data):>7}{'yes' if ok else 'no':>10}"
              f"{'yes' if path else '-':>7}{'yes' if call else '-':>10}"
              f"{'yes' if exp else '-':>9}")

    print()
    print(f"  uploads the feature accepts         {accepted:>3} of "
          f"{len(uploads)}")
    print(f"  uploads whose content decides       {dangerous:>3} of "
          f"{len(uploads)}")
    biggest = max(len(d) for _e, d in uploads)
    print(f"  the largest upload                 {biggest:>3} bytes, "
          f"limit {MAX_BYTES}")

    print()
    print("  the extension check and the size check are correct and they")
    print("  pass every upload, because both of them are statements about the")
    print("  file and all three of the capabilities are statements about the")
    print("  content. a .tar well under the limit is still a well-formed tar")
    print("  that is well under the limit.")
    print()
    print("  the three detectors are not filters and they are not a")
    print("  sanitiser. each one asks a question the feature never asked: is")
    print("  any member name a path, does the pickle stream contain an opcode")
    print("  that names something, does the document declare its own")
    print("  entities. answering those three is the difference between a")
    print("  format that is accepted and a format that is understood.")
    print()
    print("  the fix is one reader per format, and none of the four uses the")
    print("  format's own constructor for the part that decides: json for the")
    print("  data, an allow-list for the type name, a member filter for the")
    print("  archive, and no entity declarations for the document.")


if __name__ == "__main__":
    main()
```

```text
  formats accepted                     4
  uploads                              8
  the feature's checks               extension, 64 KB

    upload        bytes  accepted   path  callable  expands
    import-1.json     19       yes      -         -        -
    import-2.json     22       yes      -         -        -
    import-3.xml    237       yes      -         -      yes
    import-4.xml    293       yes      -         -      yes
    import-5.tar  10240       yes    yes         -        -
    import-6.tar  10240       yes    yes         -        -
    import-7.pkl     58       yes      -       yes        -
    import-8.pkl     50       yes      -       yes        -

  uploads the feature accepts           8 of 8
  uploads whose content decides         6 of 8
  the largest upload                 10240 bytes, limit 65536

  the extension check and the size check are correct and they
  pass every upload, because both of them are statements about the
  file and all three of the capabilities are statements about the
  content. a .tar well under the limit is still a well-formed tar
  that is well under the limit.

  the three detectors are not filters and they are not a
  sanitiser. each one asks a question the feature never asked: is
  any member name a path, does the pickle stream contain an opcode
  that names something, does the document declare its own
  entities. answering those three is the difference between a
  format that is accepted and a format that is understood.

  the fix is one reader per format, and none of the four uses the
  format's own constructor for the part that decides: json for the
  data, an allow-list for the type name, a member filter for the
  archive, and no entity declarations for the document.
```

Eight uploads, two per format. All eight passed. Both checks are correct and both are enforced, and
the largest upload is 10240 bytes against a 65536-byte limit.

Six of the eight have content that decides something. Two XML documents declare entities, two tar
archives contain member names that are paths, and two pickle streams contain an opcode that names
something. The detectors are not filters and they are not a sanitiser. Each one asks a question the
feature never asked, and answering those three questions is the difference between a format that is
accepted and a format that is understood.

The fix is one reader per format, and the pattern is the same in all four. None of them uses the
format's own constructor for the part that decides: JSON for the data, an allow-list for the type
name, a member filter for the archive, and no entity declarations for the document. The extension
check stays. It is just no longer the thing standing between the upload and the work.

:::

## Key takeaways

- **A serialised object is a program, not a description.** `__reduce__` returns a callable and its
  arguments, and `loads` is the thing that calls it.
- **The stream does not need a class of yours.** Six payloads, six stdlib functions, six calls. "Which
  of my classes are safe to unpickle" has the question backwards.
- **JSON and `marshal` are not safer pickles.** They refused all six because they cannot express the
  object, which is a different property and one you lose the moment you need the object back.
- **Four operations run `__reduce__`.** `dumps`, `loads`, `copy.copy` and `copy.deepcopy`, and only
  the second is called deserialisation. The boundary is whether the object was ever under your
  control.
- **An XML document can choose its own size.** 125 bytes of document, 30 characters of value; 349
  bytes, 300,000 characters; 573 bytes, three billion. A factor of ten per line, chosen by the sender.
- **The parser cannot bound this, because it does not know the intended size.** The limit has to come
  from outside the parser.
- **zipfile sanitises; tarfile asks.** Zero of six members escaped zipfile, which has fixed this for a
  long time.
- **Sanitised is not unchanged.** Four of six members landed under a name they did not ask for, and an
  absolute path became a relative subdirectory called `abs`.
- **The three tar filters reject 0, 3 and 4 of seven members.** The difference between the last two is
  a character device, which is not a file you can write a payload into.
- **The absolute path is rewritten, not rejected, by every filter.** And the setuid member passes both
  of the strict ones, because a permission bit is not a path.
- **The safe option is not the default.** `extractall` with no filter uses `fully_trusted`, so the
  caller is the one who has to ask for something else.
- **Presence alone accepted seven hostile bodies out of twelve.** A body with every key present and
  the wrong type in each is a well-formed body.
- **`True` is an `int`.** `age=True` passes a type check and would pass the range check, because one
  is inside the range. Only `type(x) is t` catches it.
- **A validator is a predicate with a coverage number.** Each of the three here is a strict superset
  of the last, and none of them reports how much gap is left.
- **The record may carry a name; it may not carry a decision.** The allow-list resolved the four types
  the application has; `getattr(builtins, ...)` resolved none of those and all three of the dangerous
  ones.
- **A framing bug is a misattribution bug.** The reader that trusted the declared length got two
  messages right, then died, and the bytes it never read are attributed to the next sender.
- **A well-formed frame can still be too large.** The 2000-byte message agreed with its own declared
  length exactly, and the trusting reader has no way to notice the size.
- **A limit on one quantity is not a limit on another.** Six documents, all under a 4096-byte upload
  limit, three of them over a hundred-million-character budget.
- **When the limit and the cost are different quantities, the check has to move.** Refusing a document
  that declares its own entities caught all three, because it is a property of the document.
- **An extension check is about the file and the danger is in the content.** Eight uploads, eight
  passes, six of them with content that decides something.

## Practice

- [ ] **Find the entry points that run `__reduce__`.** In a project you have written, list every place
  an object can arrive from outside: a cache, a queue, a session store, a file, a request body. For
  each, work out whether the object is ever passed to `pickle.loads`, `copy.copy` or `copy.deepcopy`,
  and whether it was under your control at the moment it was created. Then replace one of them with a
  record that names a type and an allow-list that resolves it.
- [ ] **Bound a format that chooses its own size.** Pick a format your code parses that can nest or
  expand -- XML with entities, a nested JSON body, a compressed archive. Measure the smallest input
  that produces the largest output, then write the check that would have refused it and confirm the
  check is on a property of the input rather than of the output.
- [ ] **Take an archive apart by hand.** Build a tar and a zip containing the same eight member names,
  including two that walk upward, one absolute path and one backslash. Extract both into a temporary
  directory and record where each member lands. Then run the tar archive through each of the three
  filters and record which members each one refuses. Report the number of members that landed outside
  and the number that landed under a name they did not ask for -- the two numbers are different.
- [ ] **Write a validator and then count its coverage.** Take a request body from a project of yours
  and write the validator you would ship first. Then write twelve bodies it should reject, including
  one with the right keys and the wrong types and one that exploits `True` being an `int`. Report how
  many it accepts, then strengthen it and report the number again. Write both numbers down.

## Solutions

:::solution Exercise 1

Five callables, four entry points, and a payload nested inside containers.

```python run
#!/usr/bin/env python3
"""Exercise 1 -- five callables, four entry points, and payloads in a container.

A smaller version of parts 1 and 2 over a different application, plus the case
that is easy to miss: the payload does not have to be the object you pass. It
can be nested inside one, and the walk reaches every copy of it.
"""
import copy
import pickle

calls = []


class Payload:
    def __init__(self, target, args):
        self.target = target
        self.args = args

    def __reduce__(self):
        return (self.target, self.args)


class Nested:
    """A payload with no configuration, so containers can hold several."""

    def __reduce__(self):
        calls.append(1)
        return (abs, (-1,))


TARGETS = [
    ("abs", (abs, (-5,))),
    ("round", (round, (3.14159, 2))),
    ("divmod", (divmod, (17, 5))),
    ("sum", (sum, ([1, 2, 3],))),
    ("int", (int, ("42",))),
]

ENTRY_POINTS = [
    ("pickle.dumps", lambda p: pickle.dumps(p)),
    ("pickle.loads", lambda p: pickle.loads(pickle.dumps(p))),
    ("copy.copy", lambda p: copy.copy(p)),
    ("copy.deepcopy", lambda p: copy.deepcopy(p)),
]

SHAPES = [
    ("bare", lambda: Nested()),
    ("in a list of three", lambda: [Nested(), Nested(), Nested()]),
    ("in a dict, three keys",
     lambda: {"a": Nested(), "b": Nested(), "c": Nested()}),
    ("two deep, four leaves",
     lambda: [[Nested(), Nested()], [Nested(), Nested()]]),
]


def runs_on(fn):
    calls.clear()
    try:
        fn(Nested())
    except Exception:                                  # noqa: BLE001
        pass
    return bool(calls)


def main():
    print(f"  callables                          {len(TARGETS):>3}")
    print(f"  entry points                       {len(ENTRY_POINTS):>3}")
    print()
    print(f"    {'callable':<12}{'pickle.loads':>14}   returned")

    called = 0
    for label, (fn, args) in TARGETS:
        try:
            result = pickle.loads(pickle.dumps(Payload(fn, args)))
            called += 1
            shown = repr(result)
        except Exception as exc:                       # noqa: BLE001
            shown = type(exc).__name__
        print(f"    {label:<12}{'called':>14}   {shown}")

    print()
    print(f"  callables invoked                  {called:>3} of "
          f"{len(TARGETS)}")

    print()
    print("  the same payload, inside a container")
    for label, shape in SHAPES:
        calls.clear()
        try:
            pickle.loads(pickle.dumps(shape()))
        except Exception:                              # noqa: BLE001
            pass
        print(f"    {label:<24}{len(calls)} invocation(s)")

    print()
    print(f"  entry points that run __reduce__   "
          f"{sum(1 for label, fn in ENTRY_POINTS if runs_on(fn))} of "
          f"{len(ENTRY_POINTS)}")

    print()
    print("  a stream is a graph, not a value, and loads() walks all of it.")
    print("  one payload in a list of three is invoked three times, and the")
    print("  four leaves two levels down are invoked four times. wrapping a")
    print("  payload in a container does not hide it, because walking into")
    print("  containers is what the walk is for.")


if __name__ == "__main__":
    main()
```

```text
  callables                            5
  entry points                         4

    callable      pickle.loads   returned
    abs                 called   5
    round               called   3.14
    divmod              called   (3, 2)
    sum                 called   6
    int                 called   42

  callables invoked                    5 of 5

  the same payload, inside a container
    bare                    1 invocation(s)
    in a list of three      3 invocation(s)
    in a dict, three keys   3 invocation(s)
    two deep, four leaves   4 invocation(s)

  entry points that run __reduce__   4 of 4

  a stream is a graph, not a value, and loads() walks all of it.
  one payload in a list of three is invoked three times, and the
  four leaves two levels down are invoked four times. wrapping a
  payload in a container does not hide it, because walking into
  containers is what the walk is for.
```

:::

:::solution Exercise 2

Eight member names through both archive readers, and the two ways they disagree.

```python run
#!/usr/bin/env python3
"""Exercise 2 -- eight member names, two archive readers, one table.

The same question as parts 4 and 5 over a longer list, with both modules side by
side so the comparison is in one place.

The two columns are measured differently and the difference is deliberate.
tarfile's filter is the function that decides, so it is called directly and the
name it returns is the answer. zipfile's decision is inside its extract path, so
the archive is built and extracted and the answer is where the bytes ended up.
"""
import os
import tarfile
import tempfile
import zipfile

NAMES = [
    "../escape.txt",
    "../../escape.txt",
    "../../../escape.txt",
    "a/../../escape.txt",
    "a/b/../../../escape.txt",
    "/abs/escape.txt",
    "..\\escape.txt",
    "normal.txt",
]

DEST = "/srv/app/uploads"


def zip_result(name):
    """Extract one member and report the path it landed on."""
    with tempfile.TemporaryDirectory() as td:
        archive = os.path.join(td, "x.zip")
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(name, "owned")
        dest = os.path.join(td, "out")
        os.makedirs(dest)
        with zipfile.ZipFile(archive) as zf:
            zf.extract(name, dest)

        real_dest = os.path.realpath(dest)
        real_archive = os.path.realpath(archive)
        landed = []
        escaped = False
        for root, _dirs, files in os.walk(td):
            for f in files:
                full = os.path.realpath(os.path.join(root, f))
                if full == real_archive:
                    continue
                if not (full == real_dest or full.startswith(real_dest + os.sep)):
                    escaped = True
                landed.append(os.path.relpath(full, real_dest))
        return ", ".join(sorted(landed)), escaped


def tar_result(name):
    """Ask the strictest filter tarfile ships what it would do."""
    member = tarfile.TarInfo(name)
    member.mode, member.type = 0o644, tarfile.REGTYPE
    try:
        return tarfile.data_filter(member, DEST).name, False
    except tarfile.TarError:
        return "refused", False


def main():
    print(f"  member names                       {len(NAMES):>3}")
    print(f"  destination                        {DEST}")
    print()
    print(f"    {'member':<25}{'zipfile writes':<22}{'tarfile (data)':>15}")

    zip_rewritten = 0
    tar_refused = 0
    escaped_any = 0
    for name in NAMES:
        z, escaped = zip_result(name)
        t, _ = tar_result(name)
        if z != name:
            zip_rewritten += 1
        if t == "refused":
            tar_refused += 1
        if escaped:
            escaped_any += 1
        print(f"    {name:<25}{z:<22}{t:>15}")

    print()
    print(f"  names zipfile writes under a new one   {zip_rewritten:>2} of "
          f"{len(NAMES)}")
    print(f"  names the data filter refuses          {tar_refused:>2} of "
          f"{len(NAMES)}")
    print(f"  names that left the destination        {escaped_any:>2} of "
          f"{len(NAMES)}")
    print()
    print("  the two columns disagree on the five names that walk upward.")
    print("  zipfile never refuses a member -- it rewrites the name so that")
    print("  the write cannot leave -- so on those five it writes a file the")
    print("  filter would have stopped. the disagreement is not about where")
    print("  the file lands. it is about whether there is a file at all.")
    print()
    print("  they agree on the absolute one, and that agreement is worth a")
    print("  second look: both strip the leading slash and produce")
    print("  `abs/escape.txt`, so the member is written to a directory the")
    print("  archive never named. neither module calls that an escape,")
    print("  because it is not one.")
    print()
    print("  for an import feature the refusal is usually the behaviour you")
    print("  want. a member that asked to be written somewhere else is not a")
    print("  member you asked for, and silently writing it under a new name")
    print("  means the archive's own manifest no longer describes what was")
    print("  unpacked.")


if __name__ == "__main__":
    main()
```

```text
  member names                         8
  destination                        /srv/app/uploads

    member                   zipfile writes         tarfile (data)
    ../escape.txt            escape.txt                    refused
    ../../escape.txt         escape.txt                    refused
    ../../../escape.txt      escape.txt                    refused
    a/../../escape.txt       a/escape.txt                  refused
    a/b/../../../escape.txt  a/b/escape.txt                refused
    /abs/escape.txt          abs/escape.txt         abs/escape.txt
    ..\escape.txt            ..\escape.txt           ..\escape.txt
    normal.txt               normal.txt                 normal.txt

  names zipfile writes under a new one    6 of 8
  names the data filter refuses           5 of 8
  names that left the destination         0 of 8

  the two columns disagree on the five names that walk upward.
  zipfile never refuses a member -- it rewrites the name so that
  the write cannot leave -- so on those five it writes a file the
  filter would have stopped. the disagreement is not about where
  the file lands. it is about whether there is a file at all.

  they agree on the absolute one, and that agreement is worth a
  second look: both strip the leading slash and produce
  `abs/escape.txt`, so the member is written to a directory the
  archive never named. neither module calls that an escape,
  because it is not one.

  for an import feature the refusal is usually the behaviour you
  want. a member that asked to be written somewhere else is not a
  member you asked for, and silently writing it under a new name
  means the archive's own manifest no longer describes what was
  unpacked.
```

:::

:::solution Exercise 3

Ten order lines, three validators, and the one hostile body a type check cannot see.

```python run
#!/usr/bin/env python3
"""Exercise 3 -- ten order lines and three validators.

A different schema from part 6, with a numeric range and two length limits, so
the strictest validator has more to check and the middle one still has the same
hole in it.
"""
REQUIRED = {"sku": str, "qty": int, "note": str}
MAX_LEN = {"sku": 16, "note": 64}
ALLOWED = set(REQUIRED)

# label, body, is it legitimate
BODIES = [
    ("ok-1", {"sku": "A-100", "qty": 3, "note": "urgent"}, True),
    ("ok-2", {"sku": "B-200", "qty": 1, "note": ""}, True),
    ("ok-3", {"sku": "C-300", "qty": 999, "note": "gift"}, True),
    ("no sku", {"qty": 3, "note": "urgent"}, False),
    ("qty='3'", {"sku": "A-100", "qty": "3", "note": "urgent"}, False),
    ("qty=True", {"sku": "A-100", "qty": True, "note": "urgent"}, False),
    ("qty=0", {"sku": "A-100", "qty": 0, "note": "urgent"}, False),
    ("qty=1000", {"sku": "A-100", "qty": 1000, "note": "urgent"}, False),
    ("sku 20 chars", {"sku": "S" * 20, "qty": 3, "note": "urgent"}, False),
    ("extra key", {"sku": "A-100", "qty": 3, "note": "urgent", "price": 1}, False),
]


def presence(body):
    return all(k in body for k in REQUIRED)


def with_types(body):
    if not presence(body):
        return False
    return all(isinstance(body[k], t) for k, t in REQUIRED.items())


def with_bounds(body):
    if not with_types(body):
        return False
    if set(body) - ALLOWED:
        return False
    if any(type(body[k]) is not t for k, t in REQUIRED.items()):
        return False
    if not all(len(body[k]) <= MAX_LEN[k] for k in MAX_LEN):
        return False
    return 1 <= body["qty"] <= 999


VALIDATORS = [
    ("presence", presence),
    ("+ types", with_types),
    ("+ bounds", with_bounds),
]


def main():
    legit = sum(1 for _l, _b, ok in BODIES if ok)
    print(f"  bodies                             {len(BODIES):>3}")
    print(f"  legitimate                         {legit:>3}")
    print(f"  hostile                            {len(BODIES) - legit:>3}")
    print()
    print(f"    {'body':<14}{'presence':>10}{'+ types':>9}{'+ bounds':>10}")

    accepted = {n: 0 for n, _ in VALIDATORS}
    hostile = {n: 0 for n, _ in VALIDATORS}
    for label, body, ok in BODIES:
        cells = []
        for name, fn in VALIDATORS:
            passed = fn(body)
            cells.append("pass" if passed else "reject")
            if passed:
                accepted[name] += 1
                if not ok:
                    hostile[name] += 1
        print(f"    {label:<14}{cells[0]:>10}{cells[1]:>9}{cells[2]:>10}")

    print()
    for name, _ in VALIDATORS:
        print(f"  {name:<12} accepts {accepted[name]:>2} of {len(BODIES)}"
              f"   ({hostile[name]} of them hostile)")

    print()
    print(f"  `True` is an int, per isinstance      {isinstance(True, int)}")
    print(f"  `True` is inside the numeric range    {1 <= True <= 999}")
    print()
    print("  the range check is the interesting addition, because `qty=0`")
    print("  and `qty=1000` are both the right type. a type check cannot see")
    print("  them, and neither can a length limit, because an integer does")
    print("  not have one.")
    print()
    print("  `qty=True` is the one to remember. it passes the type check")
    print("  because `True` is an `int`, and the range check would have")
    print("  passed it too, because `True` is `1` and one is inside the")
    print("  range. only the exact-type comparison catches it, which is why")
    print("  the strictest validator uses `type(x) is t` rather than")
    print("  `isinstance`.")


if __name__ == "__main__":
    main()
```

```text
  bodies                              10
  legitimate                           3
  hostile                              7

    body            presence  + types  + bounds
    ok-1                pass     pass      pass
    ok-2                pass     pass      pass
    ok-3                pass     pass      pass
    no sku            reject   reject    reject
    qty='3'             pass   reject    reject
    qty=True            pass     pass    reject
    qty=0               pass     pass    reject
    qty=1000            pass     pass    reject
    sku 20 chars        pass     pass    reject
    extra key           pass     pass    reject

  presence     accepts  9 of 10   (6 of them hostile)
  + types      accepts  8 of 10   (5 of them hostile)
  + bounds     accepts  3 of 10   (0 of them hostile)

  `True` is an int, per isinstance      True
  `True` is inside the numeric range    True

  the range check is the interesting addition, because `qty=0`
  and `qty=1000` are both the right type. a type check cannot see
  them, and neither can a length limit, because an integer does
  not have one.

  `qty=True` is the one to remember. it passes the type check
  because `True` is an `int`, and the range check would have
  passed it too, because `True` is `1` and one is inside the
  range. only the exact-type comparison catches it, which is why
  the strictest validator uses `type(x) is t` rather than
  `isinstance`.
```

:::

:::solution Exercise 4

Five messages, two readers, and the count of bytes nobody read.

```python run
#!/usr/bin/env python3
"""Exercise 4 -- five messages, two readers, and the bytes nobody read.

The same framing question as part 8 over a shorter stream, with one addition:
when the trusting reader dies, the number of bytes it never consumed. Those
bytes are the ones that get attributed to the next sender, and the count is the
size of the mistake.
"""
LIMIT = 64

# declared length, the bytes that actually follow
FRAMES = [
    (4, b"abcd"),
    (2, b"abcd"),
    (64, b"y" * 64),
    (100, b"z"),
    (3, b"xyz"),
]


def stream():
    return b"".join(f"{n}\n".encode() + body + b"\n" for n, body in FRAMES)


def read_trusting(data, frames):
    i = 0
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        body = data[i:i + declared]
        i += declared
        trailer = data[i:i + 1]
        i += 1
        frames.append((declared, body, trailer, i))
    return i


def read_bounded(data, limit):
    i = 0
    accepted, rejected = [], []
    while i < len(data):
        j = data.index(b"\n", i)
        declared = int(data[i:j])
        i = j + 1
        k = data.index(b"\n", i)
        body = data[i:k]
        i = k + 1
        if len(body) != declared:
            rejected.append((declared, len(body), "declared length"))
        elif declared > limit:
            rejected.append((declared, len(body), "over the limit"))
        else:
            accepted.append((declared, body))
    return accepted, rejected


def main():
    data = stream()
    print(f"  messages sent                      {len(FRAMES):>3}")
    print(f"  bytes on the wire                  {len(data):>3}")
    print(f"  declared length limit              {LIMIT:>3}")

    frames = []
    stop = "-"
    try:
        read_trusting(data, frames)
    except ValueError as exc:
        stop = f"ValueError: {exc}"
    # how far the reader got before it died: the offset after the last
    # frame it managed to read
    consumed = frames[-1][3] if frames else 0

    accepted, rejected = read_bounded(data, LIMIT)

    print()
    print("  the reader that believes the number")
    for declared, body, trailer, at in frames:
        mark = "consistent" if trailer == b"\n" else "MISALIGNED"
        print(f"    declared {declared:>4}  read {len(body):>4} bytes  "
              f"next byte {trailer!r:>6}  {mark}")
    print(f"    stopped: {stop}")

    print()
    print(f"  frames it read                     {len(frames):>3} of "
          f"{len(FRAMES)}")
    print(f"  bytes it consumed                  {consumed:>3} of {len(data)}")
    print(f"  bytes it never read                {len(data) - consumed:>3}")

    print()
    print("  the reader that reads to the delimiter")
    print(f"    accepted {len(accepted)} of {len(FRAMES)}")
    for declared, got, why in rejected:
        print(f"    rejected  declared {declared:>4}  got {got:>4} bytes"
              f"  {why}")

    print()
    print("  the first reader is not merely wrong about one message. it read")
    print("  a length of two, took two bytes, and left the rest of that")
    print("  message standing where the next length should be -- so the next")
    print("  thing it tries to parse as a number is a letter.")
    print()
    print("  the number worth carrying is the last one. those bytes are not")
    print("  lost, they are misattributed: whatever is downstream of this")
    print("  reader will see them as part of something else, and the")
    print("  messages after the mistake will be attributed to the wrong")
    print("  sender. a framing bug is a misattribution bug.")


if __name__ == "__main__":
    main()
```

```text
  messages sent                        5
  bytes on the wire                   94
  declared length limit               64

  the reader that believes the number
    declared    4  read    4 bytes  next byte  b'\n'  consistent
    declared    2  read    2 bytes  next byte   b'c'  MISALIGNED
    stopped: ValueError: invalid literal for int() with base 10: b'd'

  frames it read                       2 of 5
  bytes it consumed                   12 of 94
  bytes it never read                 82

  the reader that reads to the delimiter
    accepted 3 of 5
    rejected  declared    2  got    4 bytes  declared length
    rejected  declared  100  got    1 bytes  declared length

  the first reader is not merely wrong about one message. it read
  a length of two, took two bytes, and left the rest of that
  message standing where the next length should be -- so the next
  thing it tries to parse as a number is a letter.

  the number worth carrying is the last one. those bytes are not
  lost, they are misattributed: whatever is downstream of this
  reader will see them as part of something else, and the
  messages after the mistake will be attributed to the wrong
  sender. a framing bug is a misattribution bug.
```

:::
