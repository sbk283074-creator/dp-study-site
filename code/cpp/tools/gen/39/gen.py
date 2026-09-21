#!/usr/bin/env python3
"""Generate chapters/39-html-templates-and-escaping.md.

Every `text` fence is captured from a real clang++ run and every source block is
read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/39/gen.py
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/39 -> gen -> tools -> cpp
OUT = CHAPTERS / "39-html-templates-and-escaping.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
TIMEOUT = 90


def build_and_run(name: str):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror", "-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if r.returncode != 0:
            raise SystemExit(f"{name} exited {r.returncode}:\n{r.stderr}")
        return r.stdout


def diagnostic(name: str):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return b.stderr, b.returncode


def msg(blob: str, marker: str, needle: str) -> str:
    for line in blob.splitlines():
        if needle in line and marker in line:
            return marker + " " + line.split(marker, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{blob}")


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").rstrip("\n")


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


def listing(names: list[str]) -> str:
    out = []
    for name in names:
        out.append(f"/* ===== {name} ===== */")
        out.append(read(name))
    return "\n\n".join(out)


# --------------------------------------------------------------------------
# capture
# --------------------------------------------------------------------------
print("capturing evidence ...")

naive_out = build_and_run("naive.cpp")
escape_out = build_and_run("escape.cpp")
order_out = build_and_run("order.cpp")
attr_out = build_and_run("attr.cpp")
template_out = build_and_run("template.cpp")
truncate_out = build_and_run("truncate.cpp")
types_out = build_and_run("types.cpp")

types_err, types_rc = diagnostic("types_bad.cpp")
if types_rc == 0:
    raise SystemExit("types_bad.cpp was supposed to be rejected, but it built cleanly")
TYPES_ERR = msg(types_err, "error:", "no matching function for call to 'render'")

PROJECT = ["page.h", "page.cpp", "main.cpp", "Makefile"]
project_listing = listing(PROJECT)

with tempfile.TemporaryDirectory() as td:
    for name in PROJECT:
        (Path(td) / name).write_text(read(name) + "\n", encoding="utf-8")
    m = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=180)
    if m.returncode != 0:
        raise SystemExit(f"the project Makefile did not build:\n{m.stderr}")
    p = subprocess.run(["./prog"], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
    if p.returncode != 0:
        raise SystemExit(f"the project exited {p.returncode}:\n{p.stderr}")
    project_out = p.stdout
    c = subprocess.run(["make", "clean"], text=True, capture_output=True, cwd=td, timeout=60)
    m2 = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=180)
    if m2.returncode != 0:
        raise SystemExit(f"rebuild failed:\n{m2.stderr}")
    p2 = subprocess.run(["./prog"], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
    rebuild_out = (c.stdout or "") + (m2.stdout or "") + (p2.stdout or "")

print("generating chapter ...")

TEMPLATE = r"""---
chapter: 39
part: 5
title: HTML Templates and Escaping
summary: Render HTML from data without letting that data become markup, by escaping for the right context and making the unsafe version fail to compile.
minutes: 65
tags: [html, escaping, xss, templates, security, utf-8]
---

Chapter 38 taught the service to remember things in a database. Now it has to show them. That
means writing HTML, and HTML is the one output format where a value and an instruction share
the same alphabet: `<` is both a character you might want to display and the start of a tag.
Everything in this chapter follows from that single collision.

Cross-site scripting — XSS — is what happens when data you stored arrives at a browser as
markup instead. It is not an exotic attack. It is the default outcome of string concatenation,
and it has been in the OWASP top three for twenty years because the vulnerable shape is the
obvious one. This chapter is how to make the vulnerable shape impossible: escape for the
context, and give the dangerous value a type that will not convert.

## The bug, in full

Here is a comment rendered by pasting strings together. Every value below came from a user.

@@naive@@

Look at the fourth line. The user typed a URL into their "avatar" field, and the URL contained
a double quote. The quote closed the `src` attribute early, and the rest of their text —
`onerror="alert(document.cookie)"` — was parsed as a **new attribute**. No script tag, no angle
brackets, nothing that looks dangerous if you are grepping for `<script>`. Just a quote.

The second block is the same mistake in text context: `<script>` lands in the page and the
browser runs it. Both of them are one function call away from being correct.

:::danger "We escape it later, on the way out"
The most common defence offered in code review is "it is escaped in the view layer". That is
only a defence if *every* path into the view layer goes through the escaper, and the moment
someone adds an admin page, a CSV export or a JSON endpoint, it does not. Escaping at the point
of substitution is a property of the renderer; escaping "somewhere later" is a hope.
:::

## Escaping, done in one pass

Five characters matter in HTML text and in a quoted attribute.

@@escape@@

The loop is the whole implementation, and the property that makes it correct is that **it is
one pass**: each input byte is examined once and mapped to one output fragment, so the `&` in
`&amp;` is never reconsidered. Keep that in mind for the next section. `&` must be first in
*spirit* even though a switch does not have an order — and it matters enormously if you
implement this the other way.

Note `'` is escaped as `&#39;` rather than `&apos;`. `&apos;` is valid in XHTML and in HTML5
parsers, but `&#39;` works everywhere including inside attributes delimited by single quotes,
which is what you get when a template writes `onclick='...'`.

## The ordering bug, measured

Here is the same escaper written the way people naturally write it — a chain of replacements.

@@order@@

Escaping `<` and `>` first produces `&lt;`, and *then* escaping `&` turns that into `&amp;lt;`.
The browser decodes `&amp;lt;` to the four characters `&lt;`, so the user sees literal `&lt; b`
where they typed `< b`. The data has been through the escaper twice and is now wrong in a way
that looks like a rendering bug, which is why this survives code review.

If you must chain, `&` goes first. If you can write a loop, write the loop.

## Context: the same string is safe in one place and not in another

Escaping HTML syntax is necessary and, on its own, not sufficient. There are three contexts a
value can land in, and they need three different treatments.

@@attr@@

- **Text context** (`<p>{{value}}</p>`): escaping five characters is a complete answer.
- **Attribute context** (`<img src="{{value}}">`): escaping five characters is still a complete
  answer, *provided* the attribute is quoted. An unquoted attribute is broken by a single space.
- **URL context** (`<a href="{{value}}">`): **escaping does nothing.** Look at the output —
  `javascript:alert(document.cookie)` contains no HTML metacharacter, so it survives escaping
  untouched, and the browser executes it when the link is clicked. The danger here is the
  *scheme*, not the syntax.
- **JavaScript context** (`<script>var x = "{{value}}";</script>`): escaping is not the answer
  either. The value needs JSON string encoding, and even then `</script>` inside the string
  terminates the script element early because the HTML parser gets there first. The fix for
  this one is to not build JavaScript by interpolation.

`safe_url` above is the shape of the URL fix: an **allow-list of schemes**, everything else
replaced by a fallback. A deny-list — "reject if it contains `javascript:`" — loses, because
`JaVaScRiPt:`, `java\tscript:` and `&#106;avascript:` all reach the same place. Note that
`//evil.example` is rejected too: it is a protocol-relative URL, meaning "this path, on
another host".

## A template engine, with the escaper built in

A template is a string with named holes. The engine fills them, and the engine — not the
caller — decides whether to escape.

@@template@@

Two deliberate choices. First, `{{name}}` escapes and `{{{name}}}` does not: raw insertion is
available, but it has to be typed differently, so it is visible in review and greppable. Second,
a placeholder with no value is an **exception**, not an empty string. A typo in a template
should break the build's tests, not silently publish a page with a hole in it.

## Make the unsafe version fail to compile

Escaping by convention is escaping you will eventually forget. The move that actually holds is
a type: give unescaped values a type that cannot reach the renderer.

@@types@@

`escape` is the only way to turn an `Untrusted` into an `Html`, and `trusted` is the escape
hatch for markup you wrote yourself — spelled out at the call site, where a reviewer can see
it. Both constructors are `explicit`, so there is no implicit path between them.

@@types_bad@@

That rejection is the payoff. There is no runtime check, no lint rule, no "remember to escape"
comment: the program does not build. Compare this with Chapter 24's argument for `const` — the
point of a type is that the mistake stops being possible rather than merely discouraged.

## Truncating text without breaking it

A template that truncates a value to fit a layout has one more way to corrupt it.

@@truncate@@

At limit 7 the naive cut ends on the lead byte of `你`; at limit 8 it ends on a continuation
byte. Both are invalid UTF-8, and what the browser does with an invalid sequence is up to the
browser — typically a replacement character, sometimes a hole in the page. The safe version
walks back to the start of the character and cuts there.

This is the same lesson as Chapter 36's UTF-8 work from the other direction: a `std::string` is
a byte string, and "ten characters" is not `substr(0, 10)`.

## The module

Header, implementation, a program that renders a page and tests the renderer, and the
`Makefile`. Banners mark the file boundaries; they are separators for the listing, not part of
the files.

@@project@@

The self-test at the bottom is the part worth copying. Six assertions and one expected throw,
printed, and a non-zero exit if any of them fails — so `make && ./prog` in CI tells you the
escaper still works. An escaper with no test is a claim; this one is a measurement.

@@rebuild@@

:::scenario The "safe" markdown feature
A product manager asks for markdown in user comments. Your renderer already escapes
everything, so the team proposes: escape the input, then run a markdown-to-HTML converter over
the result and insert the HTML raw with `trusted`. Someone points out that escaping first means
the markdown syntax (`#`, `*`) has already been turned into entities and nothing will render,
so the order gets swapped: convert markdown to HTML, then escape. Now the headings render and
the script tags show as text, and it ships. Two weeks later a comment with a raw HTML block
executes. What went wrong, and what is the design that does not have this hole?
:::

:::solution Markdown
**What went wrong:** both orders are broken, because markdown and HTML are not separable by
escaping. Convert-then-escape disables markdown (the generated tags become visible text);
escape-then-convert is safe but useless; and the version that shipped — convert, then insert
raw — is safe only for the subset of markdown that cannot produce raw HTML, which is no subset
at all, because every markdown dialect lets you write `<div>` or `&#60;script&#62;` and get it
through verbatim.

**The design that works:**

1. **Convert markdown to HTML with a converter that has a sanitising mode**, running *after*
   conversion and *before* insertion. The order is fixed: markdown in, HTML out, **sanitise**,
   insert. Sanitising means parsing the generated HTML into a tree and rewriting it against an
   allow-list of tags and attributes — `p, em, strong, a[href], code, pre, ul, ol, li,
   blockquote, h1–h6` and nothing else. Anything not on the list is dropped, not escaped.
2. **Run `safe_url` on every surviving `href` and `src`**, using the same allow-list of schemes
   from this chapter. A sanitised tree with `href="javascript:..."` is still an XSS.
3. **Strip event handlers by construction**: if the attribute allow-list is `href`, `title` and
   `alt`, then `onerror` cannot survive, without anyone having to remember to look for it.
4. **Keep the result in the `Html` type** and let the template insert it with `{{{...}}}`. The
   type now means "produced by a sanitiser", which is a different claim from "written by us" —
   so name that constructor `sanitised`, not `trusted`, and reviewers can tell them apart.

The general rule: **escaping is for text; allow-listing is for markup.** Once user input is
allowed to produce markup at all, no amount of escaping will save you, because escaping and
markup are opposites. Sanitise a parsed tree against an allow-list, never against a deny-list.
:::

:::pitfall Five ways this chapter's bug comes back
1. **Escaping `<` and `>` but not `"` or `'`.** Enough for text context, useless the moment the
   value lands inside an attribute — which is where `src`, `href`, `value`, `alt` and `title`
   all live.
2. **Escaping at the wrong time.** Chained replacements that do `&` last double-escape. A
   one-pass loop cannot.
3. **Assuming escaping covers URLs.** `javascript:` has no HTML metacharacters. Allow-list the
   scheme, and reject `//host`.
4. **Truncating by bytes.** `substr(0, n)` can cut a UTF-8 character in half; the result is not
   valid text.
5. **Using `trusted()` on anything a user touched.** The type is there to make that call site
   visible, not to make it correct.
:::

## Key takeaways

- HTML confuses data with instructions because `<`, `>`, `"`, `'` and `&` are both content and
  syntax; escaping is what separates them again.
- Escape in **one pass** over the input. A chain of replacements that escapes `&` last turns
  `&lt;` into `&amp;lt;` and shows the user literal `&lt;`.
- Five characters are enough for **text context** and for a **quoted attribute**: `&`, `<`,
  `>`, `"`, `'`.
- Escaping does **nothing** in URL context — `javascript:` contains no metacharacters. Allow-list
  the scheme (`http`, `https`, `mailto`, site-relative) and reject `//host`.
- Escaping is also the wrong tool in JavaScript context. Do not build scripts by interpolation.
- A raw-insertion placeholder should look different from an escaped one, so it is visible in
  review and greppable.
- An unknown or unterminated placeholder should throw. A template typo must not publish a page
  with a hole in it.
- Give unescaped values their own type with no implicit conversion to the safe type, and the
  unsafe call site stops compiling instead of shipping.
- `substr` cuts bytes, not characters; truncating UTF-8 needs to walk back to a character
  boundary first.
- An escaper with a self-test is evidence; an escaper without one is an assertion.

## Practice

- [ ] **Exercise 1.** Write `escape_attribute` and show that it is the same function as
      `escape_html`. Then find a value that is safe in text context and dangerous in an
      **unquoted** attribute, and explain why quoting the attribute fixes it.
- [ ] **Exercise 2.** Extend `safe_url` so it also rejects `data:` and `vbscript:`, and prove
      with one run that `data:text/html;base64,...` does not survive.
- [ ] **Exercise 3.** Add `{{#if name}}...{{/if}}` to the template engine: render the block only
      if the variable was supplied. Keep the unknown-placeholder exception.
- [ ] **Exercise 4.** Write `std::string truncate_words(const std::string &, std::size_t)` that
      cuts at a word boundary **and** never mid-UTF-8-character, then verify the result is valid
      UTF-8 for an input whose 40th byte is inside a character.
- [ ] **Exercise 5.** Make the `Html` type carry its own provenance: add a `Provenance` enum
      (`escaped`, `sanitised`, `authored`) and print it in the rendered page's HTML comment, so a
      reviewer inspecting the output can see where each value came from.

## Solutions

:::solution Exercise 1
There is no separate function, and that is the answer: the five characters are the complete set
for both contexts. The difference is not the escaper, it is the **quotes**. In
`<img src={{value}}>` — unquoted — the value `x onerror=alert(1)` needs no metacharacter at
all: a space ends the attribute and `onerror=` starts a new one. Escaping turns it into
`x&#32;onerror=alert(1)`, which is still one token with a space inside it, so the attribute
never ends, but you are now relying on the escaper for structural integrity instead of for
syntax. Quote every attribute you interpolate into:

@@sol1@@
:::

:::solution Exercise 2
`data:` is the interesting one: it is a legitimate scheme for images and a complete HTML
document execution context for links. One allow-list, checked against the parsed scheme, and
everything that is not on it becomes the fallback:

@@sol2@@

Note that the check is on the **scheme**, not on a substring of the whole URL — a deny-list that
searches for `data:` anywhere would also reject
`https://example.com/page?ref=data:text/html`, which is a perfectly ordinary link.
:::

:::solution Exercise 3
A conditional is a block with a start marker and an end marker, so the scanner needs a stack —
or, as here, recursion over the segment. Keeping the "unknown placeholder throws" rule is what
makes the conditional safe to add: a typo inside the block is still an error rather than a
silently-rendered empty string.

@@sol3@@
:::

:::solution Exercise 4
Two constraints, applied in order: cut at a character boundary first, then walk back to the last
space inside what remains. The order matters — cutting to a word boundary and *then* fixing
UTF-8 would leave you back at an arbitrary byte.

@@sol4@@
:::

:::solution Exercise 5
Provenance is metadata about trust, and putting it in the output turns a code-review question
into something you can read off the page. The enum makes "written by us" and "produced by a
sanitiser" different values, which is the distinction the markdown scenario above depends on.

@@sol5@@
:::
"""

# --------------------------------------------------------------------------
# capture the solutions, too: they are verified `run` blocks
# --------------------------------------------------------------------------
SOLUTIONS = ["sol1.cpp", "sol2.cpp", "sol3.cpp", "sol4.cpp", "sol5.cpp"]
sol_out = {}
for name in SOLUTIONS:
    sol_out[name[:-4]] = build_and_run(name)

print("splicing ...")

blocks = {
    "naive": fence("cpp", "run", read("naive.cpp"), naive_out),
    "escape": fence("cpp", "run", read("escape.cpp"), escape_out),
    "order": fence("cpp", "run", read("order.cpp"), order_out),
    "attr": fence("cpp", "run", read("attr.cpp"), attr_out),
    "template": fence("cpp", "run", read("template.cpp"), template_out),
    "truncate": fence("cpp", "run", read("truncate.cpp"), truncate_out),
    "types": fence("cpp", "run", read("types.cpp"), types_out),
    "types_bad": fence("cpp", "bad", read("types_bad.cpp"), TYPES_ERR),
    "project": fence("cpp", "make-files", project_listing, project_out),
    "rebuild": fence("sh", "run-project", "make clean\nmake\n./prog", rebuild_out),
}
for key, out in sol_out.items():
    blocks[key] = fence("cpp", "run", read(key + ".cpp"), out)

body = TEMPLATE
for key, value in blocks.items():
    body = body.replace("@@" + key + "@@", value.rstrip("\n"))

leftover = re.findall(r"@@(\w+)@@", body)
if leftover:
    raise SystemExit(f"unsubstituted placeholders: {leftover}")

OUT.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
words = len(re.findall(r"\b[\w'-]+\b", body))
print(f"wrote {OUT.name}: {len(body.splitlines())} lines, ~{words} words")
