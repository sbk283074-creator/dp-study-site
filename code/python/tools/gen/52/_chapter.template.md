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

<<BLOCK:pickle_reduce>>

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

<<BLOCK:reduce_sites>>

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

<<BLOCK:xml_entities>>

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

<<BLOCK:zip_slip>>

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

<<BLOCK:tar_filter>>

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

<<BLOCK:schema_boundary>>

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

<<BLOCK:json_hooks>>

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

<<BLOCK:size_limits>>

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

<<BLOCK:pitfall>>

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

<<BLOCK:scenario>>

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

<<BLOCK:sol1>>

:::

:::solution Exercise 2

Eight member names through both archive readers, and the two ways they disagree.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

Ten order lines, three validators, and the one hostile body a type check cannot see.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

Five messages, two readers, and the count of bytes nobody read.

<<BLOCK:sol4>>

:::
