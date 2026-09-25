#!/usr/bin/env python3
"""Generate chapters/28-json-parsing-and-generating.md.

    python3 tools/gen/28/gen.py

The JDK ships no JSON parser and this track takes no third-party jars, so the
library in `gen/28/` is written by hand. One establishing listing seeds it and
every later block is a `sh run-project` script that drops in a driver -- the
Chapter 27 pattern, which is the only way to print a library once.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "28-json-parsing-and-generating.md")

BLOCKS = {
    "core": gen.run_files(
        ["JsonDemo.java", "Json.java", "JsonParser.java", "JsonWriter.java"]),
    "escape": gen.sh("escape.sh", "run-project"),
    "numbers": gen.sh("numbers.sh", "run-project"),
    "errors": gen.sh("errors.sh", "run-project"),
    "depth": gen.sh("depth.sh", "run-project"),
    "roundtrip": gen.sh("roundtrip.sh", "run-project"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 28
part: 4
title: JSON -- Parsing and Generating
summary: The JDK has no JSON parser, so write one. Eight grammar rules, a sealed value type, escaping measured character by character, numbers that must stay text, and the 10 KB body that kills a thread.
minutes: 75
tags: [json, parsing, recursion, escaping, unicode, security]
---

Chapter 27 ended with a service that speaks HTTP and has no idea what its bodies mean. The next thing
every web service needs is a body format, and the one everybody uses is JSON.

Here is the fact that shapes this chapter: **the JDK has no JSON parser.** Not a deprecated one, not an
internal one — nothing in `java.*` reads or writes JSON. And this track takes no third-party jars, for
the same reason Chapter 19 built its own test runner and Chapter 32 will build its own database: a
format you have to implement is a format you have to understand.

That is not a hardship. JSON's entire grammar is eight rules and a parser for it is about a hundred
lines. By the end of this chapter you will have written one, and you will know exactly which of its
decisions are yours to make.

## JSON is eight rules

```
value   = object | array | string | number | "true" | "false" | "null"
object  = "{" [ member { "," member } ] "}"
member  = string ":" value
array   = "[" [ value { "," value } ] "]"
string  = '"' { character | escape } '"'
escape  = "\" ( '"' | "\" | "/" | "b" | "f" | "n" | "r" | "t" | "u" four-hex-digits )
number  = [ "-" ] ( "0" | digit-1-to-9 { digit } ) [ "." digit { digit } ]
                   [ ( "e" | "E" ) [ "+" | "-" ] digit { digit } ]
```

Two things about that grammar matter more than the rest.

**It never recurses on the left.** A `value` can contain an `array`, which can contain a `value` — so
the parser recurses, but only ever forward, and one character of lookahead is enough to choose. That is
why recursive descent is not merely *a* way to write this parser; it is the shape the grammar already
has.

**`number` is a syntactic definition, not a numeric one.** It says what a number *looks like* and
nothing about what type it is. JSON has exactly one number type, Java has several, and that mismatch is
the source of the most expensive bug in this chapter.

## A value is a sealed interface

@@core@@

That listing is the whole library: a sealed interface with six record implementations, a parser, a
writer, and a demo that drives them. It compiles with no dependency, because there is nothing to depend
on.

Start with the type. `Json` is **sealed** (Chapter 16), so the set of implementations is closed and the
compiler knows it. Every `switch` over a `Json` is therefore checked for exhaustiveness: add a seventh
kind of value and every switch that handles the six stops compiling. For a format whose whole job is to
be read by code you have not written yet, that is the most useful property a type can have.

`Obj` holds a `LinkedHashMap`, not a `HashMap`. JSON objects are ordered on the wire, and while the
specification says a reader must not *depend* on that order, a writer that reorders its input makes
every diff, test and log line unstable for no reason at all. Insertion order costs nothing here and
removes an entire class of "it changed but nothing changed".

And `Num` holds a **`String`**. That looks wrong for about five minutes; the section on numbers below is
the argument for it.

## Parsing: a cursor and one character of lookahead

Read `JsonParser` and you will find no cleverness anywhere. There is a `String`, an `int at`, and a
`peek()` that returns the character at `at` or a NUL past the end. Every method advances `at`. There is
no tokenizer, no separate pass, no lookahead buffer.

`value(int depth)` is the whole dispatch, and it is a `switch` on a single character:

```java
return switch (peek()) {
    case '{' -> object(depth);
    case '[' -> array(depth);
    case '"' -> new Json.Str(string());
    case 't' -> literal("true", new Json.Bool(true));
    case 'f' -> literal("false", new Json.Bool(false));
    case 'n' -> literal("null", new Json.Nil());
    case END -> throw error("the input ended where a value was expected");
    default -> number();
};
```

One character decides everything, which is exactly what "no left recursion" buys you. `object` and
`array` recurse into `value(depth + 1)`, and nothing else recurses at all.

Two details are worth noticing before the rest of the chapter uses them.

- **The depth is threaded, not stored.** `value` is told the depth it is being called at, and
  `parse(text, maxDepth)` refuses past a limit. That is the only defence in the file, and "The failure
  that is not an exception" is the reason it is not optional.
- **Errors carry a position.** `error(message)` walks from the start of the input to `at` counting
  newlines, so every failure says *where* it happened. A parser that reports "invalid JSON" and nothing
  else is a parser whose bugs become other people's debugging sessions.

## Strings, and the escapes that are not required

@@escape@@

Read the two columns and the escaping rules fall out of them. Nine inputs, and what the writer does with
each:

- `"` becomes `\"` and `\` becomes `\\` — required, because each would otherwise end or confuse the
  string literal it sits in.
- A raw newline becomes `\n`, a tab `\t`, and `U+0001` becomes `\u0001` — required, because JSON forbids
  a raw control character, meaning anything below `0x20`, inside a string.
- `café` is written **unchanged**. `é` is above `0x20`, so JSON allows it raw, and escaping it would be
  legal but wasteful: six bytes where two would do, for a character that needs no protection.
- `slash/here` is written unchanged. `/` **may** be escaped as `\/` and need not be; the parser accepts
  both and the writer emits the shorter one. That is the last line of the output — `a\/b -> a/b` — and it
  is the general shape of a format: the reader is the permissive one, and a writer is free to be stricter
  than the grammar requires.
- `sep\u2028here` is escaped even though JSON does not require it. `U+2028` and `U+2029` are legal raw
  in JSON and are **line terminators in JavaScript**, so a document pasted into a `<script>` block or
  handed to `eval` breaks a line that the JSON specification says is one line. Six bytes, one whole
  category of "it works until it does not".

The `all 9 came back unchanged: true` line is the property that matters, and it is worth being precise
about what it does and does not prove. It proves the writer and the reader agree about these nine
strings. It does not prove either is correct — that is what the grammar is for, and it is why this
section is a measurement rather than a proof.

## Numbers are text, because a double is not a JSON number

@@numbers@@

The table is the argument. Read the `same?` column: **five of the seven texts change when they become a
`double`.**

- `1` becomes `1.0`. A document that said "the id is the integer 1" now says "1.0", and a strict reader
  on the other end may reject it or may store a float.
- `1e3` becomes `1000.0` — the same value in different text, and `1e3` was legal input.
- `-0` becomes `-0.0`. Negative zero is a real IEEE value and a real JSON text, and they are not the
  same token.
- `9007199254740993` becomes `9.007199254740992E15`. This is the one that matters.

That number is `2^53 + 1`, and `2^53` is the largest integer a `double` can represent exactly. Above it,
consecutive doubles are more than one apart, so the odd integers simply do not exist. The block makes
the loss concrete:

```
  as a long    : 9007199254740993
  as a double  : 9007199254740992
  written back : 9007199254740993
```

Read that again, because the third line is the point. A parser that stored a `double` would have written
`...992` back — **silently, with no error anywhere, in a document that is still perfectly valid JSON.**
No test that asks "did it parse" can see it. The only defence is to refuse to throw the text away, which
is why `Num` holds a `String` and offers `asDouble()`, `asLong()` and `isIntegral()` as *conversions*
rather than as storage.

The rule generalises, and it is the same rule as Chapter 18's `BigDecimal`: **a number that arrives as
text and leaves as text should never pass through a binary float.** Identifiers, nanosecond timestamps,
currency amounts, and anything that came out of a 64-bit counter all belong in that category.

## Rejecting is most of the job

@@errors@@

Ten malformed documents, ten rejections, and every message carries a position. A parser is judged by
what it refuses, and the interesting thing about this list is how much of it is *nearly* valid:

- `{"a":1}x` — the object is fine; the `x` after it is not. The check is one line at the end of `parse`,
  and without it the parser would silently ignore everything after the first value. Solution 4 is about
  that line.
- `[1,2` — the array is unterminated, and the message says `expected ']' but found the end of the input`,
  which is exactly the sentence a person needs.
- `{"a":01}` — JSON forbids a leading zero and this parser rejects it. Notice *how*: the message is
  `expected '}' but found '1'`, because `number()` consumed the `0` and stopped. The refusal is correct
  and the reason given is not the one you would write down. That is normal for a hand-written parser, and
  it is worth knowing that a correct refusal can carry an imprecise explanation.
- `tru` — `literal()` uses `startsWith`, so a truncated keyword fails at the keyword rather than at some
  later bracket.
- `""`, the empty input — a value was expected and the input ended. An empty body is not an empty
  document, and a service that treats it as one has quietly invented a default.

Nothing here throws a `NullPointerException` and nothing reports a bare index into a string. Every
failure is an `IllegalArgumentException` carrying a line and a column — which is precisely the type the
dispatcher in Chapter 27 catches.

## The failure that is not an exception

@@depth@@

Now the interesting one, and it is not a bug in the parser. It is a property of recursion.

```
  1000 levels,   2000 characters -> parsed
  5000 levels,  10000 characters -> StackOverflowError
```

Ten kilobytes. Ten thousand characters of `[` and `]` — smaller than one image upload, smaller than most
HTML pages — and the parser dies. Not "returns an error": **dies**, because every nesting level costs a
stack frame and the stack is a fixed size.

Two things make that worse than it looks.

**It is a property of the thread, not of the input.** The exact threshold depends on the stack size and
the frame size, so those numbers are this JVM on this machine, and a different `-Xss` moves them. What
does not move is the shape: some depth kills it, and the depth is small.

**`StackOverflowError` is an `Error`, not a `RuntimeException`.** Chapter 27's dispatcher is

```java
try {
    response = router.route(Requests.from(exchange));
} catch (RuntimeException e) {
    response = Response.text(500, "the service failed: " + e.getMessage());
}
```

and that `catch` does not catch this. The output says so directly:

```
  it escaped that catch and arrived as java.lang.StackOverflowError
```

So the client receives **nothing at all** — the dropped connection Chapter 27 measured, arriving through
a door that chapter did not know existed. A malformed body is a `400`; a deeply nested body is a dead
thread.

:::warning A size limit is not a shape limit

It is tempting to conclude "limit the body to 1 MB and move on". The body in that block is **10 KB**. A
size limit bounds how much memory a request may consume; it says nothing about how deep the document is,
and depth is what kills a recursive parser. They are different limits and you need both.

:::

The fix is the `maxDepth` parameter, and the same block shows it working: `nested deeper than 64 levels
at line 1, column 66` — an ordinary refusal, caught by an ordinary `catch`, turned into an ordinary
response.

## Writing back is not the same as printing

@@roundtrip@@

`JsonWriter` is a `switch` over the sealed interface with no `default`, which is the exhaustiveness
property from the top of the chapter paying off: it is impossible to add a seventh kind of `Json` and
forget to teach the writer about it, because the compiler will not let you.

The measurement is a round trip, and the column that matters is the last one:

```
{"a":[]}                       -> {"a":[]}                       stable=true
  {  "spaced" :  1  }          -> {"spaced":1}                   stable=true
```

**Writing is not printing.** The input `  {  "spaced" :  1  }  ` is a perfectly valid JSON document and
the output is not the same string — the whitespace is gone, because whitespace is not part of the value.
That is why `stable` is the property to test and not `equal`: writing, parsing and writing again has to
produce the same bytes, and it does, for all seven documents.

That property is what makes a JSON body diffable in a test, hashable in a cache, and safe to log. A
writer that emitted a `HashMap`'s iteration order would break all three — which is the other half of the
reason `Obj` holds a `LinkedHashMap`.

:::scenario A 10 KB body that kills the thread

A service accepts `POST /notes` with a JSON body. There is a size limit — 1 MB, checked before the
parser runs — and the dispatcher is Chapter 27's, with `catch (RuntimeException e)` wrapped around the
whole route.

An attacker sends a body of 200,000 characters, all of them `[`.

The body is five times smaller than the limit. What does the client receive, and what is the smallest
change that turns this into a normal error?

:::solution
@@scenario@@

The client receives **nothing at all**. The first line of the output shows the ordinary case working — a
malformed body becomes a clean `400` — and the second shows the nested one:

```
a nested body of 200000 character(s):
  the dispatcher never returned: java.lang.StackOverflowError
```

The dispatcher never returned, so nothing was ever written to the socket, so the connection closed with
an unanswered request. Chapter 27 established that an uncaught *exception* costs the client its
response; this is the same failure with a different cause, and it is worse, because `catch
(RuntimeException)` is not the wrong catch by accident. It is exactly the right catch for exceptions and
no catch at all for errors.

Three things make this a real vulnerability rather than a curiosity:

1. **The size limit does not help.** 200 KB is well under 1 MB, and the parser dies at roughly 5 KB of
   nesting.
2. **It costs the attacker almost nothing.** The body is one repeated character. There is no computation
   to prepare and no state to keep.
3. **It is caught nowhere.** The thread serving the request dies with the error, and if that handler is
   running on a pool thread, the pool is now one thread smaller.

The smallest change that fixes it is a depth limit inside the parser:

```java
if (depth > maxDepth) {
    throw error("nested deeper than " + maxDepth + " levels");
}
```

One `int`, one comparison, in one place — and it converts an `Error` that escapes every catch into an
`IllegalArgumentException` that the existing dispatcher already handles. Solution 1 is that fix,
measured against the same 200 KB body.

The lesson generalises well past JSON: **a limit on input size is not a limit on input shape.** Every
recursive consumer of untrusted input needs a depth bound, and the bound belongs to the consumer rather
than to whoever calls it — because the caller is the one who forgot.
:::
:::

## Solutions

### 1. A depth limit belongs to the parser

The scenario's fix, and the reason it goes in `JsonParser` rather than in the handler.

@@sol1@@

The same 200 KB body, twice. With no limit it is a `StackOverflowError` that nothing can catch; with a
limit of 64 it is a sentence with a position in it.

Putting the limit in the parser rather than in the caller is the whole point. A handler that remembers to
call `parse(body, 64)` is a handler that can forget, and the failure mode of forgetting is not an error
message — it is a dead thread. A default of `Integer.MAX_VALUE` and an explicit opt-in to a bound would
be exactly backwards: the safe choice has to be the one you get by accident, which means the bound
belongs in the API the caller already uses.

### 2. A duplicate name is not a merge

JSON permits an object to contain the same member name twice. The specification does not say what a
reader should do about it, and that silence is the problem.

@@sol2@@

Two members named `role` went in and one came out, and nothing said so. This parser keeps the last one,
because `members.put` overwrites — a reasonable choice, and not the only reasonable one. A reader that
keeps the **first** is equally defensible.

That is what makes it a security problem rather than a style question. If a proxy validates the first
`role` and the service acts on the last, then a body that both ends consider valid produces an
authorisation decision the proxy did not make. This is the same shape as Chapter 25's `%2F` smuggling:
two components disagreeing about what a valid input means.

The fix is to reject rather than to choose. `Obj`'s compact constructor is already the right place to
notice, or the parser can check `members.containsKey(name)` before putting — and either way the answer
becomes a `400` instead of a guess.

### 3. Money is not a double

The number section established that a `double` loses large integers. It loses small decimals too, and
money is the case that costs real money.

@@sol3@@

Both lines came out of the same body, and only one of them is money. `0.1` and `0.2` are exactly
representable in base 10 and not at all in base 2, so the `double` sum carries a rounding error that no
amount of later formatting removes.

`BigDecimal` can only be built from the text — there is no constructor that takes a `double` and gives
you back the value you meant — which is precisely why the parser keeps the raw string. `Num.raw()` is
not a convenience for debugging; it is the only field that can produce a correct `BigDecimal`, and it is
the reason the type is shaped the way it is.

### 4. The input has to end

One line at the end of `parse` decides whether a body is one document or the beginning of one.

@@sol4@@

Trailing whitespace is accepted and a second value is not, and the distinction is exact: the check is
*"the input ended"*, not *"the first value ended"*. `parse` skips whitespace, parses a value, skips
whitespace again, and then requires `at == text.length()`.

Without that line, `{"a":1}{"b":2}` parses to `{"a":1}` and the second document is left in the buffer
unread and unreported. That matters because a body is not always consumed by one reader: a proxy that
counts the bytes, a logger that records the raw text, and the service that parses it are three readers
of one string, and they must agree on where it ends. A parser that stops early silently hands the next
reader a different document.

## Key takeaways

- **The JDK has no JSON parser**, and this track adds no jars, so the parser is part of the book rather
  than a dependency of it.
- JSON's grammar is eight rules, none of them left-recursive, which is why a cursor, one character of
  lookahead and recursive descent are enough.
- `Json` is a **sealed** interface with six records, so every `switch` over a value is checked for
  exhaustiveness — including `JsonWriter`'s, which has no `default`.
- `Obj` holds a **`LinkedHashMap`**: JSON objects are ordered, and a writer that reorders its input makes
  every diff, hash and log line unstable for nothing.
- `Num` holds a **`String`**. `2^53 + 1` becomes `2^53` as a `double`, silently, in a document that is
  still valid JSON.
- A number that arrives as text and leaves as text must never pass through a binary float. `BigDecimal`
  is built from `Num.raw()` or it is wrong.
- Escaping is **per character**: `"` and `\` and every character below `0x20` are required; `é` and `/`
  are not; `U+2028` and `U+2029` are not required by JSON and are escaped anyway, because they terminate
  a line in JavaScript.
- The reader is the permissive one. `\/` is accepted and never emitted — a writer may be stricter than
  the grammar.
- Every error is an **`IllegalArgumentException` with a line and a column**. A parser that says "invalid
  JSON" is a parser whose bugs become someone else's afternoon.
- A correct refusal can carry an imprecise reason: `{"a":01}` is rejected with a message about `}`
  because the `0` was consumed first.
- **`StackOverflowError` is an `Error`, not a `RuntimeException`**, so Chapter 27's
  `catch (RuntimeException e)` does not catch it and the client gets no response at all.
- A **size** limit is not a **shape** limit. A 10 KB body of `[` kills a recursive parser; the depth
  bound belongs in the parser, where it cannot be forgotten.
- Writing is not printing: whitespace is not part of the value, so the property to test is
  **write → parse → write is byte-identical**, not `equal`.
- A duplicate member name is a **disagreement waiting to happen** between two readers of the same body.
  Reject it rather than choosing a winner.

## Practice

- [ ] Add `Json.Bool` handling to a `switch` you write yourself and then delete one arm. Which error do
      you get, and why does that only work because `Json` is sealed?
- [ ] `Obj` copies its map in the compact constructor. What breaks if it does not, and what does the
      copy cost?
- [ ] Write `Num.asBigDecimal()`. What should it do with `1e3`, and what should `isIntegral()` mean for
      `1.0`?
- [ ] The writer emits compact JSON. Write an indenting variant and make the round-trip property still
      hold — or explain why it cannot.
- [ ] A body arrives with a byte-order mark (`EF BB BF`) before the `{`. What does this parser do, and
      which layer should have removed it?
- [ ] The parser rejects a raw control character inside a string. Which other characters below `0x20`
      are legal *outside* a string in JSON, and what does that tell you about where the check belongs?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Removing an arm gives `the switch expression does not cover all possible input values` — a compile
   error, not a runtime one. It works because `Json` is sealed: the compiler can enumerate the permitted
   subtypes, so exhaustiveness is decidable. With a non-sealed interface it would have to insert a
   synthetic `default` that throws, and you would find out at run time, on the one input you did not
   test. This is the strongest practical argument for sealing a closed set of variants.
2. Without the copy, `Obj` would share the caller's map, so mutating the map after constructing the
   object would change a value that is supposed to be immutable — and `Json` is passed around a service
   precisely because it is safe to share. The cost is one `LinkedHashMap` allocation and a copy of the
   entries, which for a request body is negligible next to the parsing itself. Note that `Arr` uses
   `List.copyOf`, which is even cheaper because it can return the same instance when the list is already
   immutable.
3. `new BigDecimal(raw)` for every case, which is exactly what makes `1e3` interesting: `BigDecimal`
   accepts `1e3` and gives `1E+3`, whose `scale()` is negative. That is correct — the text really does
   have no decimal places — but a caller expecting `scale() == 0` will be surprised. `isIntegral()`
   answers "does the text contain a `.` or an `e`", which is a *syntactic* question and is why it returns
   `false` for `1.0`: the value is an integer and the text is not. Two different questions, and the
   method name should say which one it answers.
4. An indenting writer breaks the round-trip property as stated, because `write(parse(write(v)))` inserts
   whitespace the first output did not have. The property that survives is weaker and more useful: parse
   both outputs and compare the *values*, or define the canonical form as compact and let indentation be
   a separate, explicitly non-canonical view. This is why pretty-printing belongs to a debug command and
   not to the response path.
5. This parser rejects it, with `expected a value`, because the BOM is a character the grammar does not
   allow there. The right place to remove it is the layer that decoded the bytes: a BOM is an encoding
   artefact, not a document feature, so the code that turns `byte[]` into `String` should strip a leading
   `U+FEFF` once. The general rule is that a parser should see text, and the text should already be in
   the encoding the format assumes.
6. The four JSON whitespace characters — space, tab, newline and carriage return — are legal anywhere
   between tokens, so `skip()` is called at every point where a token may be preceded by whitespace, and
   *not* inside `string()`. Inside a string, a raw newline is a control character and is rejected. That
   is the answer to "where does the check belong": a character's legality depends on the state the parser
   is in, which is exactly why the check lives in `string()` and not in a pre-pass over the input.
"""

gen.write(TEMPLATE, BLOCKS)
