#!/usr/bin/env python3
"""Generate chapter 29 of the C/C++ track.

Every `text` fence in the chapter is captured by compiling and running the demo it
belongs to, so the transcripts cannot drift from the code.

Run from anywhere:  python3 code/cpp/tools/gen/29/gen.py
"""
import pathlib
import shlex
import subprocess
import sys

SRC = pathlib.Path(__file__).resolve().parent
PROJ = SRC / "proj"
CHAPTERS = SRC.parents[2] / "chapters"
OUT = CHAPTERS / "29-json-by-hand.md"

CXX = "clang++"
BASE = "-std=c++17 -Wall -Wextra"


def run(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode


def fence(lang, body):
    return "```" + lang + "\n" + body.rstrip("\n") + "\n```"


def clean(text):
    lines = text.replace("\r\n", "\n").split("\n")
    lines = [ln.rstrip() for ln in lines]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def capture(src_name, flags=BASE, mode="stdout", expect_fail=False):
    exe = SRC / (pathlib.Path(src_name).stem + "-gen")
    out, err, rc = run(f"{CXX} {flags} -o {shlex.quote(str(exe))} {shlex.quote(src_name)}", cwd=SRC)
    if expect_fail:
        if rc == 0:
            sys.exit(f"{src_name} was expected to fail to compile, but it built")
        return clean(out + err), rc
    if rc != 0:
        sys.exit(f"compile failed for {src_name}:\n{out}{err}")
    so, se, rc = run(shlex.quote(str(exe)), cwd=SRC)
    return clean(so if mode == "stdout" else se), rc


def balanced(lines, start_line):
    depth = 0
    out = []
    for ln in lines[start_line - 1:]:
        out.append(ln)
        depth += ln.count("{") - ln.count("}")
        if depth == 0 and len(out) > 1:
            break
    return "\n".join(out)


def frag(path, marker):
    lines = pathlib.Path(path).read_text().split("\n")
    for i, ln in enumerate(lines, 1):
        if marker in ln:
            return balanced(lines, i)
    sys.exit(f"marker not found: {marker}")


# ---------------------------------------------------------------- evidence

nolib_out, _ = capture("nolib.cpp", expect_fail=True)
escape_out, _ = capture("escape.cpp")
comma_out, _ = capture("comma.cpp")
utf8_out, _ = capture("utf8.cpp")
bomb_out, _ = capture("bomb2.cpp", flags=BASE + " -fsanitize=address,undefined", mode="stderr")
wrong_out, _ = capture("wrongshape.cpp", flags=BASE + " -Werror", mode="stderr")

run("make clean >/dev/null 2>&1 && make", cwd=PROJ)
proj_out, _, _ = run("./prog", cwd=PROJ)
proj_out = clean(proj_out)

cli_out, _, _ = run(
    'sh -c "./prog --help; echo ---; ./prog /api/items/2; ./prog /api/items/99; ./prog /nope"',
    cwd=PROJ,
)
cli_out = clean(cli_out)

FILES = ["json.h", "json.cpp", "api.h", "api.cpp", "main.cpp", "Makefile"]
listing = "\n".join(
    f"/* ===== {name} ===== */\n" + (PROJ / name).read_text().rstrip("\n")
    for name in FILES
)

NLOHMANN = "'nlohmann/json.hpp' file not found"
assert NLOHMANN in nolib_out, nolib_out
assert "stack-overflow" in bomb_out, bomb_out
assert "std::bad_variant_access" in wrong_out, wrong_out
assert "Content-Length: 190" in proj_out, proj_out

# Measured with Node 22 (V8, the same engine a browser uses).
NODE_MSG = "Expected ',' or '}' after property value in JSON at position 14 (line 1 column 15)"
NODE_TRAIL = "Unexpected non-whitespace character after JSON at position 3 (line 1 column 4)"

S = []
A = S.append

A("""---
chapter: 29
part: 5
title: JSON by Hand
summary: Build a JSON writer and a recursive-descent parser, and use them to answer an /api/ route with real application/json.
minutes: 80
tags: [json, parsing, escaping, variant, recursion, api, unicode]
---

Chapter 28's router answered `/health` and `/items` with bodies that were string literals:

```cpp
return text(Status::Ok, "{\\"status\\":\\"ok\\"}\\n");
```

Every quote on that line was escaped by a human, and the shape was checked by nobody. That is fine for
four words that will never change. It stops being fine the moment the value comes from somewhere else
— a file, a socket, a struct field a user typed. An item called `nut "heavy duty"` turns into
`{"name":"nut "heavy duty""}`, which is not JSON, and the browser reports it as a blank page and one
line in a console you are not looking at.

This chapter builds the thing that writes those bytes and the thing that reads them back. There is no
JSON library on this machine, and that is a fact about the machine rather than a preference:

""")

A(fence("cpp bad", (SRC / "nolib.cpp").read_text().rstrip("\n")))
A("")
A(fence("text", NLOHMANN))
A("""
`nlohmann/json.hpp` is the library most C++ projects reach for, and it is excellent. It is also not
installed here, and it is not going to be — this book is self-contained, and a chapter that begins
with *install a package* is a chapter that stops working the day the package changes. So you will
write it. Escaping, a value type and a recursive-descent parser are the three skills every
serialization format needs, and JSON is the smallest format that has all three.

If your machine does have the library, read the chapter anyway. Being able to say what your JSON
library is doing — and what it is *not* doing — is most of the reason to use one.

## Escaping: two characters you must, and thirty-two you must not forget

A JSON string is a run of characters between two `"`. Inside it, exactly two characters cannot appear
as themselves: the double quote, because it would end the string, and the backslash, because it is the
escape character itself. Everything else is allowed *except* the thirty-two control characters
`U+0000` to `U+001F`, which the specification forbids outright. Five of those have short forms; the
rest are written `\\u00XX`.

Here is what that means for every kind of character you might find in real data:

""")

A(fence("cpp run", (SRC / "escape.cpp").read_text().rstrip("\n")))
A("")
A(fence("text", escape_out))
A("""
Read the middle of the first table, because it is where a hand-written escaper usually goes wrong. The
forward slash is **not** escaped. Some encoders write it as `\\/` — that is legal JSON, and pointless,
and it is why a naive "escape everything that is not alphanumeric" loop produces output nobody can
read. The bell, `U+0007`, has no short form, so it becomes `\\u0007`; the tab and the newline do.

The second table is the point of the whole function. The naive writer — the one that just puts the
string between quotes — emitted a body containing **one raw control character**. That body is not
JSON, and a parser is required to reject it, so the failure is not subtle; it is total, and it happens
on the client, far from the line that caused it. The escaped version contains none, and it is one byte
longer, which is the trade: one extra byte for each character that needed escaping.

Two things `json_escape` deliberately does not do, and you should know both:

- **It does not validate UTF-8.** Non-ASCII characters pass through as their original bytes, which is
  correct — JSON strings are sequences of Unicode characters and UTF-8 is the encoding everyone uses.
  But if the bytes arriving were never valid UTF-8, the bytes leaving are not either, and the document
  is invalid in a way no amount of escaping would have fixed. Validation is a separate job, done at
  the boundary where the bytes enter the program.
- **It does not escape the forward slash**, for the reason above. If you need a `</script>` sequence to
  be safe inside an HTML `<script>` block, that is an HTML problem, and it is solved by writing `<` as
  `\\u003c` on the way out — which this function also does not do, and which the next chapter will.

## Building a value instead of a string

Escaping handles one string. An array of them has a second problem, and it is the one that survives
testing because an empty list never triggers it:

""")

A(fence("cpp run", (SRC / "comma.cpp").read_text().rstrip("\n")))
A("")
A(fence("text", comma_out))
A("""
`["alpha","beta","gamma",]` is not JSON. The rule is that commas go *between* elements, and "put a
comma after every element" is not the same rule — it only looks the same until the last one.

Notice that the naive version gets the empty array right. That is the trap. A test that builds an empty
list, or a list with one element, passes; the bug appears the first time real data arrives, and it is a
client-side syntax error again.

The fix is a `bool` that remembers whether anything has been written yet. It is three lines, and it is
the same three lines at every level of nesting — which is why the right move is to stop writing strings
and start writing a **value type**. A value knows its own shape, so it knows whether it needs a comma
in front of it:

""")

A(fence("cpp", frag(PROJ / "json.h", "class Json {")))
A("""
Six shapes, one class. The storage is a `std::variant`, so a `Json` is exactly one of those six at any
moment and `is_*()` tells you which. The two container alternatives mention `Json` inside their own
definition, which looks circular and is not: `std::vector<Json>` and `std::map<std::string, Json>` are
complete types even while `Json` is still being declared, because the standard library containers are
specified to work with an incomplete element type. That is what makes a recursive type like this
possible at all.

Writing one out is a recursion over the shape, and the comma logic falls out of it:

""")

A(fence("cpp", frag(PROJ / "json.cpp", "void Json::dump_into")))
A("""
Two things in there are worth more than they look.

**A string goes through `json_escape` on the way out, not on the way in.** This is the most important
design decision in the chapter. If you escape when you *build* the value, you have to remember to do it
at every place that builds one, and you have to know not to do it twice when a value is copied. If you
escape when you *write* it, there is exactly one place in the program where a character becomes a byte,
and it is the line above.

**Object keys go through it too.** A key is a string, and a key containing a quote is exactly as
illegal as a value containing one. `json_escape(pair.first)` is easy to forget, because keys usually
look like identifiers.

The keys come out **sorted**, because the storage is a `std::map`. That is worth knowing and worth not
caring about: JSON says the members of an object are unordered, so a client that depends on the order
they arrive in is already broken. You will see it in the transcript below, where `{"b":1,"a":2}` comes
back as `{"a":2,"b":1}`.

It is also worth knowing that JavaScript does not sort. `JSON.stringify({b:1,a:2})` in Node prints
`{"b":1,"a":2}`, in insertion order, and both answers are correct. The two implementations agree on the
*value* and disagree on the bytes, which is exactly why comparing JSON as text is a mistake — and why
the next time you write a test that asserts on a JSON response, it should parse both sides first.

## Reading it back: a recursive-descent parser

Writing JSON is a walk over a tree you already have. Reading it is a walk over text you do not trust,
and that is the harder half of the chapter.

The parser is one class holding the text and a position, with one method per shape. `parse_value` looks
at the next character and decides which of the others to call:

""")

A(fence("cpp", frag(PROJ / "json.cpp", "std::optional<Json> parse_value")))
A("""
Everything returns `std::optional`. There is no exception, no error code to forget to check, and no
half-built value to leak — a failure at any depth propagates out as an empty optional, and the caller
has one decision to make. For a parser that will be fed bytes from a network, that is the right
default: invalid input is an ordinary outcome, not an exceptional one.

Note the first line: `if (depth > max_depth_) return std::nullopt;`. It is the guard against input that
is not malicious but is 200,000 characters of `[`, and it gets its own section below.

### Numbers: scan the shape, then convert

The obvious way to parse a number is to find where it ends and hand the text to `strtod`. The problem is
that `strtod` accepts a *superset* of JSON: `nan`, `inf`, `+5`, `.5`, `0x10` and `1e999` all convert
happily. So the parser scans the shape JSON allows first, and only then converts:

""")

A(fence("cpp", frag(PROJ / "json.cpp", "std::optional<Json> parse_number")))
A("""
The grammar being enforced here is narrower than C's, and every rejection is a real case:

| Rejected | Why JSON says no | What `strtod` would have done |
|---|---|---|
| `01` | a leading zero has to stand alone | returned `1` |
| `+5` | no leading plus sign | returned `5` |
| `.5` | the whole-number part is required | returned `0.5` |
| `1.` | a decimal point needs a digit after it | returned `1` |
| `1e` | an exponent needs digits | returned `1`, leaving the `e` behind |
| `nan`, `inf` | not JSON values at all | returned a NaN or an infinity |

Every one of those is in the transcript below, marked `refused`. This is the difference between a
parser and a converter: a converter takes what it can, and a parser decides what is allowed.

### Strings, and the escape that is really four bytes

Strings are the fiddly half. The scanner has to reject a raw control character, reject an unknown
escape such as `\\x`, and handle `\\uXXXX` — which is not a character but a **code point**, and has to
become the one, two, three or four bytes that UTF-8 writes for it:

""")

A(fence("cpp run", (SRC / "utf8.cpp").read_text().rstrip("\n")))
A("")
A(fence("text", utf8_out))
A("""
That arithmetic is the whole of UTF-8, and it is worth reading twice. `U+00E9` is `é`, two bytes.
`U+1F600` is an emoji, four bytes. The second table is the part that catches people out: a character
outside the first 65,536 is written in JSON as **two** `\\u` escapes, because one `\\uXXXX` can only
carry sixteen bits. `\\ud83d\\ude00` is one character, four bytes on the wire, and a parser that treats
each escape as a character of its own produces two pieces of garbage.

That is why `parse_unicode` does arithmetic instead of a table lookup:

""")

A(fence("cpp", frag(PROJ / "json.cpp", "std::optional<std::string> parse_unicode")))
A("""
The range checks are not decoration. `0xD800`–`0xDFFF` is the block Unicode reserves for exactly this
encoding trick, and a code point in that range is **not a character**. A lone high half, a lone low
half, or a high half followed by anything other than a low half is invalid input — so the function
returns nothing rather than inventing a replacement. Three of those cases are in the transcript as
`refused`. Rejecting is a choice; silently substituting `?` is also a choice, and it is the one that
turns a bug in your client into a mystery.

The object parser is the last piece, and it holds one small decision:

""")

A(fence("cpp", frag(PROJ / "json.cpp", "std::optional<Json> parse_object")))
A("""
`fields.insert_or_assign(...)` means a repeated key keeps the **last** value. JSON's specification does
not say what should happen, implementations disagree, and JavaScript keeps the last one — so matching
JavaScript is the least surprising choice. But it is a choice. If your protocol depends on what a
duplicate key means, your protocol is under-specified, and the fix belongs in the protocol.

### Depth is a limit, not a detail

The `max_depth_` check costs one comparison per value. Without it, this is what a 200,000-character body
does to your server:

""")

A(fence("cpp run-san-catch", (SRC / "bomb2.cpp").read_text().rstrip("\n")))
A("")
A(fence("text", "stack-overflow"))
A("""
The program above has the same shape as the real parser: one stack frame per nesting level, no limit,
and text that is nothing but opening brackets. The output before the crash is missing because the
`printf` never ran — the recursion was already 200,000 frames deep, and the process died on the way in.
AddressSanitizer names it `stack-overflow` and prints the frames that led there.

A stack overflow is not an exception. It cannot be caught, it does not unwind, and it does not run a
destructor — the guard page at the end of the stack is hit and the process is gone. There is no
recovery from inside the program, so the only defence is to refuse the input before recursing, which is
what the one-line check does.

The project's self-test shows both halves of that: 40 levels of nesting are refused at the default
limit of 32, and accepted when the limit is raised to 64. The parser did not get smarter; it was told
how deep it was allowed to go.

### Trailing text

The last rule is the one that separates a parser from a scanner:

```cpp
std::optional<Json> parse_document() {
    std::optional<Json> value = parse_value(0);
    if (!value) return std::nullopt;
    skip_ws();
    /* Anything left over means the text was not JSON, however good the start was. */
    if (pos_ != text_.size()) return std::nullopt;
    return value;
}
```

`123abc` begins with a perfectly good number. A parser that stopped when the number ended would return
`123` and leave `abc` for the next caller to trip over. Checking that the position reached the end is
the difference between "this text begins with JSON" and "this text is JSON" — and for a request body,
only the second is safe to act on. Node agrees, and says so in its own words:

```text
Unexpected non-whitespace character after JSON at position 3 (line 1 column 4)
```

## Check the shape before you read it

A `Json` can hold six different things, and asking for the wrong one is not a conversion:

""")

A(fence("cpp run-abort", (SRC / "wrongshape.cpp").read_text().rstrip("\n")))
A("")
A(fence("text", "std::bad_variant_access"))
A("""
`std::get<int>` on a variant holding a string throws `std::bad_variant_access`. It does not return zero
and it does not convert. That is the correct behaviour — a silent `0` would be a bug that surfaces three
functions later as a wrong price — but it does mean the check is your job:

```cpp
if (value.is_number()) {
    use(value.as_number());
} else {
    /* The client sent something else. Say so. */
}
```

`is_*()` and then `as_*()`. Every `as_*()` in this class is a promise that you already checked, and the
one time you forget, the exception names the problem precisely.

## The project

Six files: the JSON module, a small API layer that builds the payloads, a `main` that exercises both,
and a `Makefile`. It is a model of the service rather than the service — no sockets — so the output is
deterministic and the HTTP layer is visible as bytes rather than as behaviour.

The `/* ===== name ===== */` lines are listing separators, not file contents. Everything between two of
them is exactly what you would type into the file it names.

""")

A(fence("cpp make-files", listing))
A("")
A(fence("text", proj_out))
A("""
Read the transcript in three places.

**The two tables.** Every accepted input comes back as a `dump()` of the value it became, and the
differences are the lessons. `2e3` comes back as `2000` — a round trip preserves the *value*, not the
spelling, so never compare JSON text for equality. `{"b":1,"a":2}` comes back as `{"a":2,"b":1}`
because of the `std::map`. `\\u00e9` and `\\ud83d\\ude00` come back as the actual characters, which is
the only way to see that the decoding worked.

**The refusals.** Fourteen inputs that look plausible and are not JSON. A parser is defined by what it
turns down at least as much as by what it accepts, and every line here is a decision made deliberately
rather than a case that happened not to be thought about.

**The payload and the wire dump.** `count` comes first and `items` follows it — alphabetical, not the
order they were inserted. Item 3's name shows `\\"` where the quote is, and item 4's shows `\\n` where
the newline is. Those are the two characters `json_escape` exists for, visible in the bytes that would
leave the socket. And `Content-Length: 190` counts the **escaped** body, which is longer than the
source text of the names — the length header has to describe what is actually sent, not what it came
from.

## Driving it from the shell

""")

A(fence("sh run-project", """#!/bin/sh
./prog --help
echo "---"
./prog /api/items/2
./prog /api/items/99
./prog /nope
exit 0"""))
A("")
A(fence("text", cli_out))
A("""
The command line answers one path at a time and prints the response exactly as the socket would carry
it, with `\\r` spelled out so the carriage returns are visible. `GET /api/items/2` is a hit and answers
`200 OK`. `GET /api/items/99` is a miss and answers `404 Not Found` — with a *body* that is also valid
JSON, because an API's errors are part of its protocol and a client should not have to parse HTML to
find out what went wrong. That pair is the subject of the pitfall below, because the first version of
this project got it wrong in a way worth seeing.

:::scenario The item that blanked the page

A user saves an item named `nut "heavy duty"`. The handler builds its response with the obvious line:

```cpp
const std::string body = "{\\"name\\":\\"" + item.name + "\\"}";
```

The server logs `200 OK` and no error. The browser shows a blank page, and its console has one line —
this one is from Node 22, which is the same V8 engine a browser runs:

```text
NODEMSG
```

Why is the page blank rather than showing a mangled name, and what is the smallest change that fixes
it?

:::solution Unescaping is not a formatting problem

The body that went out was `{"name":"nut "heavy duty""}`. A JSON parser reads the key `name`, then the
string `"nut "`, then expects `,` or `}` — and finds `h`. The parse fails at the very first object, so
there is no partial result to render. Nothing is displayed because nothing could be decoded, which is
why the page is empty rather than wrong.

The smallest change is to route the value through the escaper at the one place where it becomes bytes:

```cpp
const std::string body = "{\\"name\\":" + Json(item.name).dump() + "}";
```

That is the whole fix, and it is small because the escaping lives in `dump()` rather than at the call
site. Compare the alternative — escaping at every site that builds a body — where the fix is "remember
to escape, everywhere, forever", and the next new handler is a new chance to forget.

Two details make this worse than it looks. The server sent `200 OK`, because building a body by
concatenation cannot fail; there is nothing in the server's logs to notice. And the `Content-Length`
that went with the broken body was computed from the *unescaped* text, so it was wrong too — which
means a client that reads exactly `Content-Length` bytes gets a truncated body and a *different*
error. One unescaped character produces two independent protocol failures.

:::

:::

:::pitfall The status code that disagreed with the body

The first version of this chapter's project looked up an item like this:

```cpp
Json item_payload(const std::string &id) {
    for (const Item &item : kItems) {
        if (std::to_string(item.id) == id) return item_to_json(item);
    }
    return error_payload(404, "no item " + id);   // <- the fallback is an error body
}
```

and the caller used it like this:

```cpp
return render_json(item_payload(path.substr(11)), 200, "OK");
```

So `GET /api/items/99` answered this:

```text
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 36

{"error":"no item 99","status":404}
```

One response, two statements about what happened, and they disagree. The status line says success; the
body says 404. A client that trusts the status line caches the failure as a success. A client that
trusts the body shows an error. Both behaviours are defensible, which means the bug will be found by
whichever kind of client you did not test with — and the code that produced it looks entirely
reasonable, because every function did what its name said.

The problem is that `item_payload` is answering a question it was not asked. It knows whether the item
exists; it does not know what the *route* should say about that, and it cannot know, because the status
code belongs to the response and the response belongs to the dispatcher. The fix is to let the function
that builds a body decline to build one:

```cpp
std::optional<Json> item_payload(const std::string &id);   // nothing when there is no such item
```

and let the one place that knows the path choose the status:

```cpp
if (const std::optional<Json> item = item_payload(id)) {
    return render_json(*item, 200, "OK");
}
return render_json(error_payload(404, "no item " + id), 404, "Not Found");
```

That version is in the listing above, and the `./prog /api/items/99` transcript shows it answering
`404 Not Found` with a matching body. The rule generalises: **a function that returns a payload must
not also decide the status code.** The moment it can, you have two authorities on one question.

:::

## Key takeaways

- Inside a JSON string, escape `"`, `\\\\`, and every character below `U+0020`. Do not escape `/`, and
  do not assume anything else needs escaping.
- **Escape on the way out, never on the way in.** One place in the program turns a character into a
  byte, and that is the place that escapes.
- Commas go *between* elements. The "comma after every element" version passes an empty-list test and
  fails on real data — so write the `bool first` version, or use a value type that cannot get it wrong.
- A round trip preserves the **value**, not the text: `2e3` becomes `2000`, and object keys come back
  sorted from a `std::map` and unsorted from JavaScript. Never compare JSON text for equality.
- Scan a number's shape before converting it. `strtod` accepts `nan`, `+5`, `.5` and `1e999`, none of
  which are JSON.
- `\\uXXXX` is a code point, not a character. Anything outside the first 65,536 arrives as two escapes,
  and lone surrogates must be rejected rather than substituted.
- Recursion over untrusted input needs a depth limit. A stack overflow cannot be caught, so the check
  has to happen before the recursive call.
- Check that the position reached the end. `123abc` is not JSON, and a parser that returns `123` is a
  scanner.
- `is_*()` before `as_*()`. Reading the wrong shape throws, by design.
- A function that builds a body must not also choose the status code.

## Practice

- [ ] Write a program that takes a string as `argv[1]` and prints `valid` or `invalid` depending on
      whether `Json::parse` accepts it. Feed it `[1,2,3]`, `[1,2,3,]`, `{"a":}` and `\\u0041`.
- [ ] Add a `Json::as_int()` that returns the number rounded to the nearest `int`, and throws when the
      value is not a number. Explain why it must not silently return `0`.
- [ ] `json_number` writes an integral `double` as a bare integer, and everything else with `%.15g`.
      Find a `double` that `%.15g` does **not** round-trip, and change the function so that it does.
- [ ] The parser accepts `{"a":1,"a":2}` and keeps the last value. Change it to keep the *first*, and
      say which behaviour you would ship and why.
- [ ] Add a `Json::at(const std::string &key)` that returns `std::optional<Json>` for an object and
      nothing for any other shape. Use it to read `count` out of `items_payload()`.
- [ ] `parse_unicode` rejects a lone surrogate. Change it to substitute `U+FFFD`, the replacement
      character, and explain in one sentence why the original choice is the safer default for a server.

## Solutions

:::solution Exercise 1

The whole program is the parse call and a branch.

```cpp
#include "json.h"

#include <cstdio>
#include <string>

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    const std::string text = argv[1];
    std::printf("%s -> %s\\n", text.c_str(), Json::parse(text) ? "valid" : "invalid");
    return 0;
}
```

Compiled and run on five inputs:

| Input | Result | Why |
|---|---|---|
| `[1,2,3]` | `valid` | three numbers |
| `[1,2,3,]` | `invalid` | a trailing comma is not allowed in an array, exactly as it is not in an object |
| `{"a":}` | `invalid` | a value is required after the colon |
| `\\u0041` | `invalid` | an escape is only meaningful inside a string, and there is no opening quote |
| `"\\u0041"` | `valid` | the same escape, quoted — and it is the string `A` |

The last two rows are the pair worth having. `\\u0041` on its own is not JSON at all; the escape only
means something once a parser is inside a string. Nothing about the four characters changed between the
two rows — only the context they arrived in — which is the whole reason a parser is a state machine
rather than a list of regular expressions.

:::

:::solution Exercise 2

Rounding is the easy part; the decision is what to do when the value is not a number at all.

```cpp
int Json::as_int() const {
    if (!is_number()) throw std::bad_variant_access();
    return static_cast<int>(std::lround(as_number()));
}
```

It must not return `0`, because `0` is a perfectly good value that a caller cannot distinguish from a
failure. A function that reports failure by returning a legal value has moved the problem to every call
site, and the one that forgets is the one that ships. `std::bad_variant_access` is not the ideal
exception type here — a `JsonError` would say more — but it is the right *shape*: refuse loudly.

Compiled against the module, this prints `as_int(3.7) = 4` and `as_int on a string threw: yes`. Note
that `4` is the rounded value and not a truncation: `std::lround` rounds half away from zero, where a
plain `static_cast<int>` would give `3`. Pick one deliberately, because a JSON number that is 3.5 and
comes back as 3 has lost a bit that somebody may have meant.

:::

:::solution Exercise 3

The loss is in `%.15g`, not in the integer branch. Fifteen significant digits is not always enough to
name a `double` again. Measured, with `strtod` on the printed text compared back to the original:

| `double` | `%.15g` writes | round-trips? | `%.17g` writes |
|---|---|---|---|
| `0.1` | `0.1` | yes | `0.10000000000000001` |
| `0.1 + 0.2` | `0.3` | **no** | `0.30000000000000004` |
| `1.0 / 3.0` | `0.333333333333333` | **no** | `0.33333333333333331` |
| `1e16` | `1e+16` | yes | `10000000000000000` |

`0.1 + 0.2` is the one to remember: `%.15g` writes `0.3`, and parsing `0.3` back gives a different
`double` than the one you started with. The fix is one character:

```cpp
char buf[32];
std::snprintf(buf, sizeof buf, "%.17g", d);
return buf;
```

Seventeen significant digits always suffice to round-trip any `double`; fifteen do not. It is uglier —
`0.1` comes out as `0.10000000000000001`, a number that looks wrong and is exactly right — which is why
real libraries ship a shortest-round-trip algorithm instead: the shortest text that still names the same
`double`. `0.1` has one, and it is `0.1`. That algorithm is a genuine piece of work, and it is the honest
reason to use a library for anything that has to be exact.

Two notes on the integer branch while you are in there. `1e16 == 1e16 + 1` is **true** for `double`,
because above `2^53` the spacing between representable values is greater than one, so writing
`10000000000000000` as digits suggests a precision that is not there. And the `std::fabs(d) < 1e15` guard
is what keeps the branch away from that range — a guard that is correct, and that nobody reading
`std::to_string(static_cast<long long>(d))` would guess was load-bearing.

:::

:::solution Exercise 4

Replace `insert_or_assign` with a check, so the first value wins:

```cpp
if (fields.find(*key) == fields.end()) fields.emplace(std::move(*key), std::move(*value));
```

Which to ship depends on the protocol. Keeping the last matches JavaScript, so a browser and the server
agree on what a duplicated key meant. Keeping the first is what a strict validator wants, because a
duplicate key is almost always a bug in the producer and silently discarding one of the two values
hides it. The two defensible positions are "reject the document" and "match the client". Keeping
either one silently, without deciding, is the only wrong answer.

Compiled against the module, the patched parser turns `{"a":1,"a":2}` into `{"a":1}` — the opposite of
the version in the listing, which gives `{"a":2}`. Both are one line apart, and neither announces
itself, which is the whole reason to write the choice down somewhere a reader will find it.

:::

:::solution Exercise 5

```cpp
std::optional<Json> Json::at(const std::string &key) const {
    if (!is_object()) return std::nullopt;
    const auto it = as_object().find(key);
    if (it == as_object().end()) return std::nullopt;
    return it->second;
}
```

`items_payload().at("count")` gives a `Json` holding `4`. Note that a missing key and a wrong shape both
give `std::nullopt` — convenient here, but worth a second thought: a caller that needs to tell "no such
key" from "this is an array" has to check `is_object()` itself first.

Compiled against the module, the three cases come out as `at("count") = 4`, `at("nope") = nothing`, and
`at on an array = nothing`. The last one is the design decision: `.at()` on an array is not an error and
not an exception, it is simply "no such key", because an array has no keys. If you would rather that be
a bug, throw — but decide, and put the reason in the comment.

:::

:::solution Exercise 6

Substituting is not one line. There are three places where a surrogate is rejected, and a lone half can
arrive at any of them, so every one of them has to change:

```cpp
/* 1. a high half with no low half after it */
if (pos_ + 2 > text_.size() || text_[pos_] != '\\\\' || text_[pos_ + 1] != 'u') {
    return utf8(0xFFFD);
}

/* 2. a high half followed by something that is not a low half */
if (*second < 0xDC00 || *second > 0xDFFF) return utf8(0xFFFD);

/* 3. a low half with nothing in front of it */
} else if (cp >= 0xDC00 && cp <= 0xDFFF) {
    return utf8(0xFFFD);
}
```

Compiled and run against all five cases, the result is:

| Input | What comes out | Bytes |
|---|---|---|
| `"\\ud83d"` — a lone high half | `U+FFFD` | `ef bf bd` |
| `"\\udc00"` — a lone low half | `U+FFFD` | `ef bf bd` |
| `"\\ud83d\\u0041"` — high, then not a low half | `U+FFFD` | `ef bf bd` |
| `"\\ud83d\\ude00"` — a real pair | the emoji | `f0 9f 98 80` |
| `"\\u00e9"` — an ordinary escape | `é` | `c3 a9` |

`ef bf bd` is the three-byte UTF-8 encoding of `U+FFFD`, the replacement character — the question mark
in a diamond you have seen when a file's encoding is wrong.

The last two rows are the ones that matter. A valid pair still decodes to four bytes, so the substitution
did not break the good case. And this is why the obvious one-line version is wrong: putting
`if (cp >= 0xD800 && cp <= 0xDFFF) return utf8(0xFFFD);` at the top of the function looks like it does
the job, and it fails the fourth row — it fires before the parser has looked for a low half, so every
real emoji in the input gets replaced too. A patch that passes the tests you thought of and corrupts the
data you did not is worse than the refusal it replaced.

The original is safer because a lone surrogate means the input is **not valid JSON**, and a server's job
is to say so. Substituting produces a document that parses and is quietly wrong — the client sees a name
with a replacement character in it and has no way to know the server discarded something. Refusing gives
the client an error it can act on; substituting gives it corrupted data and no signal. For a library a
person is debugging, substituting is friendlier. For a server parsing bytes from a network, refuse.

:::
""")

body = "\n".join(S).replace("NODEMSG", NODE_MSG)
OUT.write_text(body)
print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(body.splitlines())} lines)")
