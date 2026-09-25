#!/usr/bin/env python3
"""Generate chapters/27-requests-responses-and-routing.md.

    python3 tools/gen/27/gen.py

Structure note. Every block that needs the router runs as a `sh run-project`
script against the project seeded by the single `core` listing. That is the
Chapter 24 pattern, and it exists for a measured reason: a `run-files` listing
carries the full text of every file it needs, so giving each of the seven
router-dependent blocks its own listing printed `Router.java` seven times and
`Request.java` seven times -- about 40% of the chapter was repetition. A
script drops in one driver and compiles it against the already-built `out/`.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "27-requests-responses-and-routing.md")

# The one listing that establishes the project for every later `run-project`
# block. RouteDemo comes first because the harness runs the *first* file that
# holds a `main`; ServiceDemo is the probe the end-to-end section runs.
PROJECT = ["RouteDemo.java", "ServiceDemo.java", "Router.java", "Request.java",
           "Response.java", "Requests.java", "Query.java"]

BLOCKS = {
    "request": gen.run_files(["RequestDemo.java", "Request.java"]),
    "response": gen.run_files(["ResponseDemo.java", "Response.java"]),
    "adapter": gen.run_files(
        ["AdapterDemo.java", "Requests.java", "Query.java", "Request.java", "Response.java"]),
    "core": gen.run_files(PROJECT),
    "specificity": gen.sh("specificity.sh", "run-project"),
    "errors": gen.sh("errors.sh", "run-project"),
    "service": gen.sh("service.sh", "run-project"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 27
part: 4
title: Requests, Responses and Routing
summary: Move the service off HttpExchange. A request and a response become plain values, one adapter file touches the socket, and the router keeps 404 and 405 apart.
minutes: 70
tags: [http, routing, records, design, adapters, status-codes]
---

Chapter 26 left you with a working server and a handler that takes an `HttpExchange`. That handler is
holding a live socket. It can read the network and write the network, and there is no way to call it
with a path and see what it answers — testing it means starting a server, opening a connection, and
reading bytes back. Every routing rule you write lives inside a running process.

This chapter moves the service off that type. The move is small, it is mechanical, and it is the single
change that makes the rest of this Part possible: **a request and a response become plain values**, and
one file — exactly one — still knows what a socket is. Everything after that file is ordinary Java that
runs in a `main` method with no server anywhere.

## A handler that is holding a socket

Here is the shape Chapter 26 ended with:

```java
server.createContext("/notes", exchange -> {
    String id = exchange.getRequestURI().getPath().substring("/notes/".length());
    byte[] body = ("note " + id).getBytes(StandardCharsets.UTF_8);
    exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
    exchange.sendResponseHeaders(200, body.length);
    try (OutputStream out = exchange.getResponseBody()) {
        out.write(body);
    }
});
```

Count what this handler knows. It knows the path format (`/notes/` plus an id, sliced by character
offset). It knows the content type and the encoding. It knows that `sendResponseHeaders` takes a length
in bytes. It knows the response body is an `OutputStream` that has to be closed. It knows `200`.

Now ask a smaller question: **which of those things is the answer to "what should `GET /notes/7`
return?"** Only the last two lines. The rest is protocol plumbing that has nothing to do with notes.

:::tip Separate the decision from the transport

The test for this separation is a sentence: *"the handler decides what the answer is; something else
decides how an answer becomes bytes."* When a handler contains `\r\n`, a `byte[]`, or the word
`Content-Type`, the two jobs have been mixed, and the mixing is what forces a server into every test.

:::

So the service gets two new types. A `Request` is what a handler is allowed to know. A `Response` is
what a handler is allowed to produce.

## A request as a value

@@request@@

Six components, and none of them is a socket: the method, the path, the query parameters, the headers,
the body, and the path variables the router pulled out of the pattern.

Three details in that output are the whole point of the type.

**Asking for a variable that is not there throws.** `no path variable nope on /notes/7` — not `null`.
That is a deliberate choice. A handler that reads `var("id")` on a route whose pattern has no `{id}` has
a bug in the *pattern*, and the pattern is written somewhere else, in the table the router was built
from. Returning `null` would move that bug into the handler's body, where it becomes a
`NullPointerException` two frames later with no mention of routing. Throwing names the mistake where it
was made. This is the same instinct as Chapter 24's exit codes: a failure should be reported as itself.

**Header lookup ignores case.** The record stores `accept` and the call asked for `Accept`. Chapter 25
measured on the wire that header names are case-insensitive; this is that rule implemented, once, in one
method, so that no handler has to remember it.

**`withVars` returns a copy.** After `request.withVars(Map.of("id", "9"))`, the original still says `7`.
A record cannot be edited in place, so a router can attach variables to a request without any possibility
of a handler seeing another request's variables. The compiler enforces it, not discipline.

## A response as a value

@@response@@

The record has three components — status, content type, body — and the factories exist so that a handler
never spells out `200` or `text/plain; charset=utf-8` by hand. `Response.notFound(path)` is the one that
pays for itself, because it makes the service's 404 format a single decision instead of one decision per
handler.

The interesting method is `length()`, and the measurement above is why:

```
'hello' is 5 char(s) and 5 byte(s)
'héllo' is 5 char(s) and 6 byte(s)
```

Five characters either way. Six bytes for the second one, because `é` is two bytes in UTF-8. So
`Response.ok("héllo").length()` is `6`, and a writer that promised `body.length()` would promise 5 and
send 6 — which is precisely the understated-header failure Chapter 25 measured, where the client read
five bytes, dropped the last character, and no status code said anything was wrong.

`writeTo` is where that gets fixed, and it is worth reading closely. It converts the body to a `byte[]`
**once**, then uses that one array for both the header and the write:

```java
byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
exchange.sendResponseHeaders(status, bytes.length);
```

One array, one length, one place. The two numbers cannot disagree, because there is only one number. That
is the structural answer to Chapter 26's scenario — the response that declared 100 bytes and wrote 14 —
and it is a better answer than care, because care is not checkable.

:::warning One writer, or none

The moment a second place writes a response, the guarantee is gone. The rule is not "remember to count
bytes"; the rule is "`Response` is the only type that calls `sendResponseHeaders`". Everything else
returns a `Response` and lets this method frame it.

:::

## The one file that still knows about the socket

@@adapter@@

`Requests.from(exchange)` is the only code in the service that names both `HttpExchange` and `Request`.
That is the whole design in one sentence: the socket is read in exactly one place, converted to a value,
and never mentioned again. Nothing downstream can reach the network, which means nothing downstream needs
a network to be tested.

The request above was sent as

```
POST /notes?q=hot%20milk&tag=a&tag=b
```

and the handler saw `q` as `hot milk` — decoded, because `%20` is a space — and `tag` as `a`, while the
record still holds `[a, b]`. Two rules are visible in that pair of lines:

- **A name is a map to a *list*.** `?tag=a&tag=b` is legal, common, and means both values. The record
  keeps the list; `query(name)` is a convenience that returns the first one. Know which of the two you
  are calling. Chapter 26's practice problem about `null` and `""` is the same warning from the other
  direction: a query string is not a map to a string.
- **Decoding happens once, at the edge.** The handler never sees `%20`, because `URLDecoder` ran in the
  adapter. If a handler decoded again, `a%2520b` would become a space when it should have stayed
  `a%20b` — the double-decoding bug, which is a security bug when the value is a path or a filename.

And the body arrives as a `String`. That is not free — the adapter reads the whole thing with
`readAllBytes()` before the handler runs — but it is *correct*, because Chapter 26 established that the
body must be read before the response is sent, and the adapter is the one place that can guarantee the
order. A streaming design would return a stream instead; this service returns a `String`, and that is a
size limit the chapter's practice questions come back to.

## The router, and the two probes that drive it

Everything so far has been types. Here is the router, and with it the complete library — five types and
the two probes that drive them. `RouteDemo` comes first and is what the run below prints; `ServiceDemo`
is the end-to-end probe the last section of this chapter runs, and it is in this listing because it is
the program that uses every one of these files.

@@core@@

The table has four routes and the eight calls above land on all of them plus both failure modes. Read the
last four lines carefully, because they are the reason this router is not three lines long:

```
PUT     /notes           -> 405  PUT is not allowed; try GET, POST
DELETE  /notes           -> 405  DELETE is not allowed; try GET, POST
GET     /notes/7/edit    -> 404  no route for /notes/7/edit
GET     /other           -> 404  no route for /other
```

`PUT /notes` and `GET /other` are both refusals, and they are not the same refusal. `/notes` **exists** —
there are two methods registered at that path — and `PUT` is not one of them. `/other` does not exist at
all. `405` says "this path means something, and you asked the wrong way". `404` says "this path means
nothing here". A client that gets `404` for `PUT /notes` will conclude the resource is missing, and may
try to create it, or report a broken link to a user. Neither is what happened.

So `route` cannot answer as soon as a pattern fails to match. It has to walk the **entire** table,
collecting the methods that did match the path, and only then decide:

- at least one method matched the path, but not this one → `405`, with the collected methods
- nothing matched the path at all → `404`

That is why the method is written with an accumulator and no early return. The list it builds is not
decoration either: it becomes the `Allow` header, which is what lets a client retry correctly instead of
guessing. The router hands the list to `Response.methodNotAllowed`, and the response carries it.

From here on the blocks are shell scripts. Each one drops a single driver into the project this listing
built and compiles it against the already-compiled `out/`, which is why no source above is printed twice.

## Registration order decides

@@specificity@@

Both routers above contain the same two routes. They differ only in the order they were added, and the
second line of each block is a different answer:

```
{id} registered first:
  /notes/latest    -> 200  a note with id=latest
literal registered first:
  /notes/latest    -> 200  the latest note
```

`/notes/{id}` matches `/notes/latest` — `latest` is a perfectly good `id`. `/notes/latest` also matches
`/notes/latest`. Two routes match, so *something* has to break the tie, and this router breaks it by
registration order: **first match wins**.

That is a deliberate choice, and it is worth being explicit about what it buys and what it costs. It buys
predictability — the table is a list, it is read top to bottom, and there is no hidden scoring function to
learn. It costs an ordering obligation on whoever writes the table: a literal path must be registered
**before** the variable that would swallow it, and nothing in the router will tell you when you get it
wrong. The symptom is not an error; it is a handler that quietly never runs.

:::tip The order rule, stated once

Register the specific before the general. `/notes/latest` before `/notes/{id}`, `/notes/{id}/edit` before
`/notes/{id}`. If you find yourself wanting a scoring function, ask first whether the table can simply be
written in the right order.

:::

## What a thrown exception looks like from the client

@@errors@@

A handler that throws is not a handler that returns `500`. Those are two different events, and the
measurement is blunt about the difference:

```
GET /uncaught ->
  the client received nothing at all
GET /caught ->
  HTTP/1.1 500 Internal Server Error
  the service failed: somebody caught this
```

The first handler threw and the connection closed with no response at all. Not a `500` — nothing. The
client is left holding a half-open socket and an unanswered request. The second handler caught its own
exception and produced a complete response.

So the catch-all in the dispatcher is not defensive programming; it is the only thing that can turn an
unexpected failure into an answer. Without it, every bug in every handler becomes a dropped connection,
and a dropped connection is the hardest kind of failure to diagnose: the server's log and the client's
error do not agree on what happened, because the client never heard anything.

## The whole service, end to end

`ServiceDemo.java` — the last file in the listing above — is the whole service in one program, and this
is what it prints:

@@service@@

The dispatcher it drives is three statements inside one context:

```java
server.createContext("/", exchange -> {
    Response response;
    try {
        response = router.route(Requests.from(exchange));
    } catch (RuntimeException e) {
        response = Response.text(500, "the service failed: " + e.getMessage());
    }
    response.writeTo(exchange);
});
```

Adapt, route, write. One context, registered at `/`, so that no path can reach Chapter 26's built-in HTML
404 — every request lands here and gets a `Response` in the service's own format.

The run makes seven calls and every one of them got a complete response: two reads, a `POST` that changed
the state (note that the third `GET` sees `buy milk`, so the handler really did mutate the list), a
`405`, a `404`, and a `500` from a handler that threw. That is the payoff. The failure modes are all
still failures, but they are now *answers*, and every one of them came from the same three lines.

:::scenario The router that answered 404 for a path it knew

A colleague writes the router the obvious way — search the table for the pair `(method, path)` and return
`404` when the pair is not there:

```java
for (Pair pair : PAIRS) {
    if (pair.method().equals(method) && match(pair.pattern().split("/"), path) != null) {
        return Response.ok("handled");
    }
}
return Response.notFound(path);
```

The table has `GET /notes`, `POST /notes` and `DELETE /notes/{id}`. A client sends `DELETE /notes`.

What does it receive, what will it conclude, and what does the correct router answer instead?

:::solution
@@scenario@@

The naive router answers `404  no route for /notes`. The correct one answers
`405  DELETE is not allowed; try GET, POST`.

The path `/notes` is in the table twice. The naive router compares the **pair**, so a method that is
absent makes the pair absent, and a missing pair is indistinguishable from a missing path. It collapses
two different failures into one answer — and it collapses them in the direction that lies, because the
`404` says the resource does not exist when the resource is right there with two methods on it.

The consequences are concrete. A client that gets `404` on a `DELETE` may reasonably decide the item is
already gone and report success to the user. An API explorer will mark the endpoint as nonexistent and
stop offering it. A retry loop will keep retrying, because `404` reads like a routing mistake rather than
a method mistake.

The real router scans the whole table and accumulates the methods that matched the path. It only reaches
`405` after the scan, and the accumulator becomes the `Allow` header — so the client is not merely told
"no", it is told `try GET, POST`, which is a fact it can act on. That is the difference between a refusal
and a dead end.
:::
:::

## Solutions

### 1. A 405 has to say what is allowed

The status code says the method was refused. It does not say which methods would have worked, and without
that the client is guessing. `Allow` is the header that carries the answer.

@@sol1@@

The head shows the whole story: `405`, then `Allow: GET, POST`, then a body the service wrote itself.
Compare this with Chapter 26's built-in 404 — `Content-Type: text/html`, `<h1>404 Not Found</h1>` — and
the difference is the same in both cases. A response the service wrote is a response the service
controls, and the parts a client actually reads are the ones you chose.

Note the casing: `Content-length`, not `Content-Length`, and `Allow` exactly as set. Chapter 26 measured
that the JDK re-cases header names on the way out; the `Allow` you set is the `Allow` the client sees
only because it happened to already be in that case. Header names are case-insensitive, so this is legal
— but a client that does a string comparison against `"Allow"` is relying on the JDK's casing, not on
the protocol.

### 2. A route that exists and an id that is wrong are not the same failure

The first `405`-versus-`404` split was about the method. This is the same discipline applied one level
down, to the value inside the path.

@@sol2@@

Five paths, four outcomes, and each one is a different sentence:

- `/notes` → `200`, the collection
- `/notes/7` → `200`, the item, because `7` parses
- `/notes/seven` → `400`, because the route matched and the *argument* is malformed
- `/notes/7/edit` → `404`, because no pattern has three segments after the root
- `/other` → `404`, because no pattern starts with `other`

The `400` is the one that gets skipped in a hurry. `Integer.parseInt` throws `NumberFormatException`, and
the lazy version lets it escape — which, per the previous section, means the client receives nothing at
all. Catching it and returning `400` costs three lines and turns a dropped connection into a sentence the
client can act on. `400` is also the honest code: the request is syntactically fine and the *value* is
not acceptable, which is exactly what `400 Bad Request` means.

### 3. A path matches exactly, segment for segment

What counts as the same path is a question with a surprising answer, so it is worth measuring rather than
assuming.

@@sol3@@

`'/notes/'` matched. That is not the rule anyone writes down — it is an accident of `String.split`, which
**discards trailing empty segments**. `"/notes/".split("/")` is `["", "notes"]`, not
`["", "notes", ""]`, so it produces the same two segments as `/notes` and the two paths are
indistinguishable to this router.

`'//notes'` did not match, and the reason is the same call: `["", "", "notes"]` has three segments, and
only the *trailing* empties are dropped. So the trailing-slash tolerance is not a rule you designed, it
is a side effect you inherited — and it is the kind of side effect that should be written down, because
the day someone "fixes" the split the behaviour changes silently.

The other two lines are not accidents. `'/NOTES'` is a different path because matching is case-sensitive,
and `'/notes/ '` is a different path because a space is a character like any other — it is not padding to
be trimmed. A client that sends either one gets a `404`, and the `404` is correct.

### 4. The `Allow` list comes from the same table

`405` needs an `Allow` list. `OPTIONS` needs an `Allow` list. It would be easy to write the list twice —
once in the router and once in an `OPTIONS` handler — and it would be wrong the first time a route is
added.

@@sol4@@

The list is computed by running every route's pattern against the path and collecting the methods that
matched, which is the *same* test the router performs, on the *same* table. So it cannot go stale: add a
`PATCH` route and both `405` and `OPTIONS` report it, with no second list to remember.

`match` is `static` for exactly this reason. The router needs it, and so does any code that wants to ask
"which methods are allowed here" without performing a route — which is what `OPTIONS` is for. Making it
package-private and static keeps one implementation of the matching rule and lets the answer be computed
from outside the router.

## Key takeaways

- A handler should decide **what the answer is**; something else decides how an answer becomes bytes. A
  handler containing `\r\n`, a `byte[]` or `Content-Type` has mixed the two jobs.
- `Request` and `Response` are **records**, so they are immutable: a router can attach path variables
  without any risk of a handler mutating another request's data.
- A missing path variable **throws** rather than returning `null`, so the bug is reported where it was
  made — in the pattern — instead of two frames later as a `NullPointerException`.
- `header(name)` is **case-insensitive**, because header names are. Chapter 25 measured it on the wire;
  this implements it once.
- `Response.length()` counts **bytes**, not characters. `"héllo"` is 5 characters and 6 bytes, and the
  header must promise 6.
- `writeTo` converts the body to a `byte[]` **once** and uses that one array for the header and the
  write, so the two numbers cannot disagree. One writer, or the guarantee is gone.
- `Requests.from` is the **only** file that names both `HttpExchange` and `Request`. Nothing downstream
  can reach the network, so nothing downstream needs a network to be tested.
- A query string is a map to a **list**. `query(name)` returns the first value; the record keeps them all.
  Decode once, at the edge — double-decoding turns `%2520` into a space and is a security bug.
- `404` and `405` are different answers. `404` says the path means nothing; `405` says the path exists and
  the method is wrong, and it carries `Allow` so the client can retry correctly.
- Answering `405` requires scanning the **whole** table first, because `Allow` is built from the routes
  that matched the path. An early return cannot produce it.
- The router is **first match wins**. A literal must be registered before the variable that would swallow
  it, and getting the order wrong fails silently — a handler that never runs.
- An uncaught handler exception gives the client **nothing at all**, not a `500`. The dispatcher's
  catch-all is the only thing that turns a bug into an answer.
- `String.split("/")` discards **trailing** empty segments, so `/notes/` and `/notes` are the same route
  by accident, while `//notes` is not.

## Practice

- [ ] Add a `PATCH /notes/{id}` route and make `Allow` report it. What has to change — the table, the
      matching rule, or both?
- [ ] `Requests.from` reads the body with `readAllBytes()`. What does that cost for a 100 MB upload, and
      what would you change if the service had to accept one?
- [ ] `query(name)` returns the *first* value for a repeated name. Write a version that returns the last,
      and explain why "first" is the conventional choice.
- [ ] `Requests.from` joins multi-valued headers with `", "`. Why is that correct for `Accept` and wrong
      for `Set-Cookie`?
- [ ] The router returns `405` with an `Allow` list. What should `OPTIONS` return, and how much of that
      can be computed from the same table?
- [ ] `Response.writeTo` takes an `HttpExchange`. What would it take to make it write to an
      `OutputStream` instead, and what would that buy you?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Only the table. Add `router.patch(pattern, handler)` as a one-line wrapper around `add`, register the
   route, and both `405` and `OPTIONS` report it — because `Allow` is computed by scanning the table, not
   by a second list. The matching rule does not change at all: `match` compares segments and treats
   `{...}` as a variable, and it has no idea which method it is serving. That is the payoff of keeping
   the method out of the matcher.
2. `readAllBytes()` holds the whole body in memory, and it holds it as a `String`, which for UTF-8 is
   roughly the byte count again. A 100 MB upload becomes 100 MB of byte array plus a `String`, and
   several concurrent uploads become an out-of-memory error. The fix is to stop returning a `String`:
   give `Request` a body that is either a `byte[]` for small bodies or an `InputStream` the handler
   consumes, and decide the limit by the route. Note that the eager read is *deliberate* for the ordinary
   case — Chapter 26 established that the body must be read before the response is sent, and doing it in
   the adapter makes that impossible to get wrong. The change is to bound it, not to remove it.
3. The last value is `values.get(values.size() - 1)`, or a `LinkedHashMap` overwrite if you do not need
   the earlier ones. "First" is conventional because a query string is a *list* in order, and a client
   that sends `?tag=a&tag=b` has expressed a preference that reads left to right — the same convention as
   `Accept`, where the first media type is the preferred one. Both are defensible; what matters is that
   the choice is documented, because a caller cannot tell the difference from the outside.
4. Because HTTP defines a comma-separated list as the meaning of a repeated header for *most* headers, so
   `Accept: text/html, application/json` and two `Accept` lines mean the same thing. `Set-Cookie` is the
   famous exception: a cookie value may itself contain a comma — `Expires=Wed, 21 Oct 2026 07:28:00 GMT`
   is a single value with a comma in it — so joining two cookies with `", "` produces one unparseable
   header. Chapter 26 measured the rule from the other side: `set` replaces and `add` appends, and two
   cookies need two `Set-Cookie` headers. The general lesson is that "join with a comma" is a decision
   per header, not a default.
5. `OPTIONS` should return `204 No Content` with an `Allow` header listing the methods for that path —
   and `204` means no body, which per Chapter 26 means a negative length, not `0`. All of the list comes
   from the same scan: run every route's pattern against the path and collect the methods that matched,
   exactly as `Allow` is built for `405`. The one thing that cannot come from that scan is whether the
   *path itself* exists, so an `OPTIONS` for a path with no routes should be a `404` — the same rule as
   `route`, applied without a method.
6. `writeTo` needs to stop naming `HttpExchange` and take an `OutputStream` plus a way to say the status
   and the content type — in practice a small `Head` record, or just the two values as arguments. What it
   buys is that the writer no longer depends on the JDK server: it can write into a `ByteArrayOutputStream`
   in a test, or into a file, and the framing can be asserted without a socket. That is the same trade
   this chapter made one level up, applied to the last file that still touched the framework. The cost is
   that the caller now has to remember to call `sendResponseHeaders`, so the split only pays if a thin
   adapter does it once.
"""

gen.write(TEMPLATE, BLOCKS)
