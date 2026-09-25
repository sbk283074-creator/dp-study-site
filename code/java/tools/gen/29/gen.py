#!/usr/bin/env python3
"""Generate chapters/29-html-templates-and-escaping.md.

    python3 tools/gen/29/gen.py

Chapter 28 gave the service a body format to read. This chapter is the other
direction: a service that writes HTML back. The library in `gen/29/` is four
small classes -- `Html`, `Template`, `Url` and a demo -- and every later block is
a `sh run-project` script that drops in a driver, the Chapter 27 pattern.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "29-html-templates-and-escaping.md")

BLOCKS = {
    "core": gen.run_files(
        ["TemplateDemo.java", "Html.java", "Template.java", "Url.java"]),
    "escape": gen.sh("escape.sh", "run-project"),
    "contexts": gen.sh("contexts.sh", "run-project"),
    "xss": gen.sh("xss.sh", "run-project"),
    "schemes": gen.sh("schemes.sh", "run-project"),
    "script": gen.sh("script.sh", "run-project"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 29
part: 4
title: HTML Templates and Escaping
summary: A page is assembled from a template and a map of values, and every value that lands in markup is a potential injection. Escaping measured per character and per context, the URL scheme that contains none of the five characters, and the script block where entities are not decoded.
minutes: 70
tags: [html, escaping, xss, templates, security, urls]
---

Chapter 28 gave the service a body format it can read. This chapter is the other direction: a service
that writes HTML back, and the fact that assembling a page is the most common way a web application
becomes a vulnerability.

The claim that organises everything below is this: **escaping is not a property of a value, it is a
property of the place the value lands.** The same string is dangerous in an attribute and harmless in
an element body, dangerous in an `href` and harmless in a `<p>`, and there is no escaping function that
can be correct without knowing which of those it is writing into. Every mistake in this chapter is a
version of forgetting that.

## A template is a value with a hole in it

@@core@@

That is the whole library: five escape mappings, a placeholder parser, a URL scheme check, and a demo.
It compiles with no dependency, which is the point — a page generator is not a framework, it is a
`String` and a rule about who is allowed to produce markup.

Start with `Template`. It is compiled once into a `List<Part>`, where a `Part` is either a literal
chunk of the page or a named hole. `render` walks the list and, for a hole, looks the name up in the
map. Three decisions in those twenty lines carry the whole chapter.

**Escaping is the default and the marker is the exception.** `{{body}}` escapes; `{{{body}}}` does
not. The demo prints both:

```
escaped: A &lt;b&gt;bold&lt;/b&gt; claim, 5 &gt; 3, and a &quot;quote&quot;.
raw    : A <b>bold</b> claim, 5 > 3, and a "quote".
```

So there is exactly one way to get unescaped markup into a page, and it is a string you can grep for.
That is the entire safety argument, and it is worth being precise about what it does and does not buy
you: it does not make unsafe output impossible, it makes unsafe output **findable**. A codebase where
every raw marker is deliberate is a codebase where an audit is a search. Solution 4 is about what that
search does not catch.

**A missing value is an error.** `no value for nope` is a thrown `IllegalArgumentException`, not an
empty string. Rendering `{{title}}` with no `title` and getting a blank heading produces a page that is
wrong in a way nobody notices; throwing produces a stack trace naming the placeholder. For a template
engine, failing loudly is almost always the cheaper bug.

**The parser rejects an unclosed placeholder.** `{{body` with no `}}` throws at compile time rather
than rendering the braces as text. A typo in a template is a programming error, and the moment to
report it is when the template is loaded, not when a user is looking at the page.

## Five characters, and why the pass is one pass

@@escape@@

Read the table: `&`, `<`, `>`, `"` and `'` become `&amp;`, `&lt;`, `&gt;`, `&quot;` and `&#39;`.

`&` and `<` are the two that matter most, and they are the two that explain why this must be a single
pass. `escape` builds a fresh `StringBuilder` and copies each input character once, so the ampersands
it writes are never read again. If it were instead a chain of `replace` calls, `&` would have to be
first or last depending on the implementation, and getting that backwards is the classic bug: the
`&` inserted by the `<` replacement gets replaced again, and the reader sees `&amp;lt;`.

The block shows the failure directly, by escaping something that was already escaped:

```
the text          : &lt;script&gt;
escaped           : &amp;lt;script&amp;gt;
and escaped again : &amp;amp;lt;script&amp;amp;gt;
```

That is the shape of the bug, and it is worth naming what kind of bug it is. The output of the third
line is **still safe** — nothing has become markup. It is a *correctness* failure: a page that displays
`&lt;script&gt;` where the author wrote `<script>` as text. This is the bug that ships, because it is
invisible in review, and because the fix people reach for — "escape at the boundary, once" — is the
same sentence as the rule that prevents injection. Solution 1 is about where that boundary is.

`>` needs escaping less than `<` does, and `"` and `'` need escaping only inside attributes. `Html`
escapes all five anyway, in every context, and that is the right default: the cost is a few bytes in
the common case, and the alternative is a function that has to be told which context it is in by a
caller who has already forgotten.

:::warning Escaping twice is not safer than escaping once

It is tempting to read the block above and conclude "escape early and escape often". The second escape
is the one that breaks the page. The rule is **one escape, at the moment a value becomes markup**, and
the way to make that rule enforceable is that exactly one place in the program writes markup — the
template engine — so no handler ever has a reason to escape anything itself.

:::

## Where the text lands decides what it needs

@@contexts@@

This is the section the chapter exists for. One value, `" onmouseover="steal()`, written into two
places with two escape sets.

In element text, escaping `<` and `>` is enough:

```
  <p>" onmouseover="steal()</p>
```

The quote is just a character in a text node. The browser renders it and moves on.

In an attribute value, the same two characters are not enough, and the output says why:

```
  <a title="" onmouseover="steal()">x</a>
```

Read that tag carefully. The `title` attribute ends at the first `"` — the one that came *from the
value* — and `onmouseover="steal()"` is now a second attribute of the `a` element. The value did not
break a character; it **closed a context and started a new one**. Nothing about the five characters
was violated: `<` and `>` were escaped exactly as instructed. The escape set was correct for a context
the value was not in.

Escaping all five repairs it, because `&quot;` cannot close an attribute:

```
  <a title="&quot; onmouseover=&quot;steal()">x</a>
```

The generalisation is the one sentence to take away from this chapter: **an escaper is a function of
`(value, context)` and this one takes only `value`.** `Html.escape` is therefore not "the escaper" —
it is the escaper for the strictest context in HTML, applied everywhere, which is a safe approximation
and not a correct one. The contexts it is not right for are the ones where escaping does nothing at
all, and there are three of them in this chapter: a URL attribute, an unquoted attribute (Solution 2),
and a `<script>` block.

## The difference is one function call

@@xss@@

A comment field holding `<img src=x onerror=steal()>`, rendered two ways.

```
  <div class="comment"><img src=x onerror=steal()></div>
  <div class="comment">&lt;img src=x onerror=steal()&gt;</div>
```

The first document contains an `img` element. The second contains **text about** an `img` element. The
browser's parser is what makes that distinction, and it makes it on the raw bytes it receives — so the
question "is this page safe" is a question about the bytes, not about the intent of the code that
produced them.

This is the whole of cross-site scripting in one paragraph. A stored value — a comment, a display
name, a filename — is written into a page, and the page is served to a *different* user than the one
who supplied it. The value is not executed in the author's session, which is what makes stored XSS
worse than reflected: the attacker does not need to trick anyone into clicking a link, because the
victim loads the page themselves.

That also explains why this chapter is in a book about a service and not a chapter about browsers. The
bug is created in the code that assembles the response, it is created by a missing function call, and
the only place it can be prevented is the same place it is created.

## Escaping is not enough, and here is the proof

@@schemes@@

Now the case that defeats the whole approach, and it is why `Url` is in the library.

The table is a list of strings and whether each may be used as an `href`. Read the `NO` rows. Then look
at this line:

```
  javascript:steal() -> javascript:steal()
```

**HTML escaping does not change the payload at all.** It contains no `&`, no `<`, no `>`, no quote of
either kind. `Html.escape` is the identity function on it. A template engine that escapes every value
by default will emit

```html
<a href="javascript:steal()">the link</a>
```

and that is a link that runs script when clicked — with every escaping rule in this chapter satisfied.

The lesson is not "escaping is unreliable". It is that **escaping removes *characters* that have
structural meaning, and this attack has no such characters.** The danger is in the *interpretation* of
the whole string by a different component: the browser reads `javascript:` as a scheme and runs the
rest. There is no character to neutralise, so there is nothing for a character-based defence to do.

The defence has to be at the level the danger lives at, which is the scheme, and `Url.isSafe` is the
whole of it:

```java
private static final List<String> ALLOWED = List.of("http", "https", "mailto");
```

An **allowlist**, not a denylist — Solution 3 measures why. Two details in those fifteen lines are
worth more than the list itself:

- **The comparison folds case.** `JavaScript:steal()` is refused, because URL schemes are
  case-insensitive and the browser will run it. A check that used `equals` against a lowercase list
  would pass this value and the browser would not care.
- **The colon is only a scheme separator when it comes before any `/`, `?` or `#`.** `/a:b` is a
  relative path with a colon in it, and it is safe. `notes:7` has a colon before any of those, so
  `notes` *is* a scheme — an unknown one, and the allowlist refuses it for that reason. The first rule
  a hand-written URL check gets wrong is that a colon anywhere means a scheme; the second is that
  `javascript:` is the only dangerous one.

That second point is the same shape as Chapter 28's duplicate member name: two readers of one string
disagreeing about where its structure is. The browser's URL parser and your check have to find the same
scheme, or the check is decoration.

:::scenario A link that escaping cannot see

A note-taking service renders each note as

```html
<a href="{{url}}">the link</a>
```

where `{{url}}` is a value the user typed when saving the note. The template escapes every
substitution, and the handler does not escape anything itself, so there is exactly one escape and it is
in the right place.

A user saves a note whose URL is `javascript:steal()`.

The page renders. What does the escaping do to that value, and what does the browser do with the
result? What is the smallest change that makes the page safe?

:::solution
@@scenario@@

The escaping does **nothing**, and the browser follows the link.

```
the engine escaped every character it knows about:
  javascript:steal() -> javascript:steal()
which is to say it changed nothing at all
```

That line is the answer to the first question, and it is not a bug in the escaper. `Html.escape`
escapes five characters that can change the structure of a document, and this value contains none of
them. The escaper is doing exactly what it says. The value is not dangerous because of its characters.

The browser, meanwhile, has a URL parser and the URL parser has rules the template never sees. It reads
everything before the first `:` as a scheme, finds `javascript`, and — for a `javascript:` URL in an
`href` on a click — evaluates the rest of the string as a script in the page's origin. So the rendered
link

```
  <a href="javascript:steal()">the link</a>
```

is a link that runs attacker-supplied script in the session of whoever clicks it, on a page that
escaped every value it rendered.

The smallest change that makes the page safe is to check the **scheme** before the value reaches the
template, and to do it with an allowlist:

```java
if (!Url.isSafe(url)) {
    throw new IllegalArgumentException("refusing the url scheme");
}
```

That is one call, and it is the only kind of check that can work here, because it is the only one
looking at the property that is actually dangerous. Escaping asked "does this value contain a character
that changes the document's structure" and the answer was no, correctly. The scheme check asks "will a
browser treat this whole string as code" and the answer is yes.

The generalisation is the sentence the chapter opened with, now with teeth: **a value is safe or not
relative to a context, and the context is defined by the component that will read it.** For an `href`
that component is the browser's URL parser, and the only defence that speaks its language is a scheme
allowlist. Solution 3 is the measurement of what happens when you write that allowlist as a denylist
instead.
:::

## `<script>` is not an HTML context

@@script@@

The last place escaping fails is the one where it fails *in both directions*: inside a `<script>`
block, HTML entities are not decoded.

```
1. written raw into a script block:
  <script>const data = {"note":"</script>"};</script>
```

The HTML parser is scanning for `</script`, and it does not care that the `</script>` is inside a
JavaScript string literal. It ends the script element there, and the rest of the line — `"};</script>`
— is now markup. This is why the JSON of Chapter 28 must not be dropped into a script block raw, and
the payload does not even need to be an attack: any note containing the text `</script>` breaks the
page.

So the instinct is to escape it, and that produces the second line of the block:

```
2. HTML-escaped first:
  <script>
  const data = {&quot;note&quot;:&quot;&lt;/script&gt;&quot;};
  </script>
```

**That is safe and wrong.** No `</script` appears, so the HTML parser is satisfied — but the HTML
parser is not the only parser here. The *JavaScript* parser receives the text between the tags and
does not decode HTML entities, because entities are an HTML feature. The script is handed the literal
six-character sequence `&quot;` where it expected a quote, and `&lt;` where it expected `<`. The page
does not break in a way that looks like a security problem; it breaks in a way that looks like a
syntax error.

The third line is the correct fix, and it is a different escaping for a different parser:

```
3. escaped the way JavaScript reads it:
  <script>
  const data = {"note":"\u003c/script>"};
  </script>
```

`\u003c` is a JavaScript escape sequence, so the JavaScript parser decodes it back to `<` and the
value the script sees is the original string. The HTML parser, scanning the raw text, sees no `</script`
and does not end the element. One change satisfies both parsers, and it works because each of them
decodes the escape the other one ignores.

Two rules fall out, and both are about which parser you are feeding:

- **Inside a script block, escape for JavaScript, not for HTML.** Replacing `<` with `\u003c` is
  enough; `<`, `>`, `&`, `\u2028` and `\u2029` are the complete set. The general technique is called
  *script-safe JSON encoding*, and it is what `JSON.stringify` does not do for you.
- **Better still, do not put data in a script block.** Serve it as JSON from an endpoint — which is a
  Chapter 28 body — and have the script `fetch` it. That removes the context entirely, and removing a
  context is always better than escaping for it, because there is no escaping call to forget.

## Solutions

### 1. Escaping belongs at the last moment

The double-escaping block showed the bug. This is the rule that prevents it, and the reason it is a
rule about *placement* rather than about escaping.

@@sol1@@

Both outputs are safe. Only one is right.

```
the handler escapes, then the template escapes:
  Ben &amp;amp; Jerry&amp;#39;s

only the template escapes:
  Ben &amp; Jerry&#39;s
```

The value in the database is `Ben & Jerry's`. The first line shows the reader `&amp;amp;` where the
author typed an ampersand — the text has been escaped twice and decoded once, because the page is
decoded exactly once by the browser no matter how many times you encoded it.

The fix is not "escape less carefully". It is that **the handler must not escape at all**, because the
template is going to. Escaping is a transformation that maps a value into a representation, and the
only component that knows which representation is needed is the one writing the markup. A handler that
escapes is a handler guessing at a context it cannot see, and it is wrong in one of two directions:
either it escapes what the template will escape again, which is this bug, or it escapes something the
template will not, which is a false sense of safety.

So the rule is: **values travel raw, and escaping happens once, in the one place that writes markup.**
Everything in `Template` follows from it, and it is also why `{{{ }}}` has to exist — without an escape
hatch, the template would be unable to express a value that is itself markup, and people would go back
to concatenating strings.

### 2. An unquoted attribute cannot be escaped

`<a href={{url}}>` looks like a shortcut and is not one.

@@sol2@@

The value `x onclick=steal()` contains a space, and a space is not one of the five characters, so
escaping leaves it exactly as it was:

```
  <a href=x onclick=steal()>x</a>
```

The attribute ended at the space and `onclick=steal()` became a second attribute. Escaping cannot fix
this, and the reason is worth stating precisely: **the character that ends an unquoted attribute value
is whitespace, and whitespace is not escapable in HTML.** It is not a character with a structural
meaning to neutralise — it is the separator, and the only way to keep it inside the value is to put a
delimiter around the value.

```
  <a href="x onclick=steal()">x</a>
```

Quoted, the value is one attribute and the space is a space. That is the fix, and it is not an escaping
fix: it is a change to the *template*, made once, by the person who wrote the template.

This is why "always quote your attributes" is a rule with no exceptions rather than a style preference.
It is the same shape as the chapter's main claim — a value's safety is a property of where it lands —
with the twist that here the fix is to change the landing place rather than to escape for it.

### 3. Allowlists fail closed

The instinct on seeing `javascript:` is to write down the schemes you have heard of and refuse those.

@@sol3@@

Read the two columns of the table and count. The denylist catches the two rows it was written for, and
only in the exact lowercase spelling it was written in. It passes `JavaScript:steal()` and
`jAvAsCrIpT:steal()` — because `startsWith` is case-sensitive and URL schemes are not — and it passes
`notes:7`, which it has never heard of.

The allowlist refuses all five values it does not recognise.

The structural difference is the whole argument:

- A **denylist** has to be *complete* to be correct, and it has to be updated every time a browser
  ships a new scheme. It fails **open**: anything the author did not think of is allowed. `data:`,
  `vbscript:`, and the next one nobody has heard of yet all get through.
- An **allowlist** has to be *sufficient* to be correct — it may refuse something legitimate, which is
  a visible bug — and it fails **closed**: anything not on the list is refused, including attacks
  nobody has invented yet.

For a security decision the trade is not close. A false refusal is a broken link and a bug report; a
false acceptance is an exploit. That asymmetry is the same one Chapter 27's dispatcher made when it
chose to return a `500` rather than to guess, and it recurs every time a program has to decide whether
input is acceptable.

### 4. The escape hatch is unbounded

`{{{ }}}` is the only way to emit markup, and the chapter leans on it as an auditable one — a grep
finds every risk. This is what the grep does not catch.

@@sol4@@

The block prints the same input four ways. The last two are the ones to compare:

```
through {{ }} -- every character is text:
  nice &lt;b&gt;work&lt;/b&gt; &lt;script&gt;steal()&lt;/script&gt;

through a bold-only allowlist:
  nice <b>work</b> &lt;script&gt;steal()&lt;/script&gt;
```

The second line lets `<b>` through and refuses `<script>`, and it does it by escaping everything and
then un-escaping exactly two strings. That is an allowlist, and it is **bounded**: the set of things it
can emit as markup is two literals, written in the source, and a reviewer can check both.

Compare that with the raw marker, which emits whatever the value happens to contain. The number of
things `{{{ }}}` can put into the page is the number of strings the user can produce — unbounded, and
unreviewable, because the risk is not in the template but in the data.

So the grep for `{{{` is a good first pass and not a proof. What it finds is a *place* where raw output
is possible; what it cannot tell you is whether the value arriving there is bounded. The rule that
follows is: **`{{{ }}}` is acceptable when the value is a literal or is produced by a bounded
transformer, and unacceptable when it is user input.** A rich-text field that goes through a sanitizer
is the second kind; a note body is the first kind only if you accept that it may contain script.

## Key takeaways

- **Escaping is a property of the destination, not of the value.** The same string is safe in a text
  node and dangerous in an attribute; `Html.escape` is the escaper for the strictest HTML context,
  applied everywhere, which is a safe approximation rather than a correct one.
- `Html` escapes **five** characters — `& < > " '` — and the pass is **one pass** over a fresh buffer,
  so double-escaping is impossible by construction rather than by ordering the replacements correctly.
- Escaping something already escaped is **not a security failure, it is a correctness failure**: the
  page shows `&lt;script&gt;` where the author wrote `<script>`.
- **An attribute ends at the first unescaped quote that came from the value.** `" onmouseover="steal()`
  in a `title` does not break a character, it closes a context and opens another.
- **A missing value throws.** A blank heading is a bug nobody notices; `no value for title` is a bug
  that names itself.
- `{{value}}` escapes and `{{{value}}}` does not, so there is **exactly one** way to emit raw markup
  and it is greppable. What the grep finds is a place, not a proof — Solution 4.
- **Escaping does nothing to `javascript:steal()`**, because the payload contains none of the five
  characters. The danger is the browser's *interpretation* of the whole string, and a character-based
  defence has no character to work on.
- A URL check must **fold case** and must find the scheme the way the browser does: a colon is a
  scheme separator only when it precedes any `/`, `?` or `#`, so `/a:b` is a path and `notes:7` is an
  unknown scheme.
- **Allowlists fail closed and denylists fail open.** A denylist must be complete to be correct and an
  allowlist must only be sufficient; for a security decision the asymmetry decides it.
- **Inside `<script>`, HTML entities are not decoded.** HTML-escaping JSON before embedding it is safe
  and wrong — the script receives the text `&quot;` where it expected a quote.
- Escape for the parser you are feeding: `\u003c` satisfies the JavaScript parser and hides `</script`
  from the HTML parser at the same time. Better, do not embed data in a script block at all.
- **Escape once, at the last moment, in the one component that writes markup.** A handler that escapes
  "to be safe" produces `&amp;amp;`, and a second escape is never safer than the first.
- **Quote every attribute.** Whitespace ends an unquoted value and whitespace is not escapable in HTML,
  so no escaper can repair an unquoted attribute — the template has to.

## Practice

- [ ] `Html.escape` escapes `'` as `&#39;`, which XML does not require in a double-quoted attribute.
      Which HTML context needs it, and what happens in that context if you drop it?
- [ ] `Template.of("{{ }}")` trims the name to the empty string and then looks it up. What should
      happen, and why is throwing better than substituting an empty string?
- [ ] The template has no loop and no conditional, so a list of comments cannot be rendered. Add
      `{{#each comments}}...{{/each}}` and say precisely what happens to the "every substitution is
      escaped" property.
- [ ] `Url.isSafe("/notes?next=javascript:steal()")` is `true`. Is that a bug? Walk through what a
      browser does when the link is clicked, and what happens if the service later uses that value as
      a redirect target.
- [ ] The scheme comparison folds case. What else in a URL is case-insensitive, and does `Url.isSafe`
      care? Where would that matter?
- [ ] A reviewer greps for `{{{` to find every raw output. Name two ways a value can reach the page as
      markup without that grep firing.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The single-quoted attribute, `<a title='{{name}}'>`. An HTML parser ends that attribute at the first
   `'`, so a value containing one closes the context exactly as the double quote did in the chapter's
   example. It matters because it is easy to write the template with single quotes — it is valid HTML,
   it needs no escaping of the double quotes inside it, and it silently removes the protection that
   `&quot;` was providing. `Html.escape` escapes both quote characters so that it is correct in either
   quoting style, which is the right call for a function that cannot see the template.
2. It should throw. The name is empty, so no key in the map can match it, and the natural behaviour of
   the lookup is already `no value for ` with a trailing space — an error message that names nothing.
   An explicit check gives a message that says what is actually wrong, which is that the placeholder has
   no name. Substituting an empty string is the worse option for the reason the chapter gives about
   missing values generally: it turns a template typo into a page that renders and is wrong, and the
   person who finds it is a user rather than a developer.
3. The loop itself is easy: a `Part` gains a `children` list and `render` repeats it per element. The
   interesting part is that the escaping property survives, because each iteration re-enters the same
   substitution path — the loop is *structure*, and every value inside it still goes through
   `Html.escape`. What does change is the **failure mode**: a template with a loop can now fail at
   render time rather than at compile time, because `{{#each comments}}` over a key that is not a list
   is a runtime error. That is the real cost of adding control flow, and it is why the parser should
   still validate that every block is closed when the template is loaded.
4. It is not a bug, and it is worth being careful about why. `href="/notes?next=javascript:steal()"`
   is a relative URL to your own server; the `javascript:` is inside a query string, so the browser
   sends it to `/notes` as a parameter and never treats it as a scheme. The danger is not in this page,
   it is in the next one: if `/notes` reads `next` and issues a redirect to it, the browser's URL parser
   now sees `javascript:steal()` as the whole target and the scheme check has been bypassed by moving
   it one request later. That is an open redirect chained into a scheme injection, and the fix is to
   validate the value at the point it becomes a redirect target — with `Url.isSafe`, not with the
   template.
5. The **host** is case-insensitive, and so is the scheme. `Url.isSafe` folds the scheme and does not
   care about the host at all, because it never looks past the colon. That is fine for this function —
   it answers "is the scheme allowed" and nothing else — but it means the name is doing more work than
   the function is: a caller who reads `isSafe` as "this URL is safe" will be surprised that
   `https://evil.example.com/` returns `true`. The honest name is `hasAllowedScheme`, and a function
   that has to be trusted by a caller who cannot read its body should have a name that cannot be
   over-read. The same distinction applies to the path, which is case-*sensitive* on most servers and
   therefore cannot be normalised the way the scheme can.
6. Two ways. First, `{{{` is not the only path to raw output if the template engine ever gains a
   filter or a helper that returns markup — a `|markdown` pipe that sanitizes and then emits raw is a
   second door, and it does not contain the three braces. Second, and the one a source grep is
   structurally blind to: **the template need not live in the source tree at all.** A template loaded
   from a file, a database column or an admin screen can contain `{{{value}}}` written by someone who
   never opened the repository, and grepping `src/` finds nothing because there is nothing to find. That
   is the same boundary Chapter 27 drew between configuration and code, and it is why the useful
   question is not "where is the raw marker" but "what is the set of templates this service will
   render, and who can add to it".
"""

gen.write(TEMPLATE, BLOCKS)
