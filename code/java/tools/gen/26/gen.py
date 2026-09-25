#!/usr/bin/env python3
"""Generate chapters/26-the-jdk-http-server.md.

    python3 tools/gen/26/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "26-the-jdk-http-server.md")

BLOCKS = {
    "minimal": gen.run("Minimal.java"),
    "lengths": gen.run("Lengths.java"),
    "introspect": gen.run("Introspect.java"),
    "contexts": gen.run("Contexts.java"),
    "notfound": gen.run("NotFound.java"),
    "threads": gen.run("Threads.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 26
part: 4
title: The JDK HTTP Server
summary: Use the HTTP server that ships with the JDK -- see which of Chapter 25's decisions it makes for you, which it leaves to you, and the three ways to say how long a body is.
minutes: 65
tags: [http, httpserver, handlers, executors, routing, security]
---

Chapter 25 read HTTP off a socket and found three decisions in every message: where the head ends,
where the body ends, and what the status code means. This chapter uses the server that ships with the
JDK — `com.sun.net.httpserver` — and the interesting question is not what it does but **which of those
decisions it takes away from you**. That set is smaller than most people expect, and knowing its
boundary is what makes the rest of this Part possible without a framework.

There is no dependency to add. `com.sun.net.httpserver` is a module in the JDK, so it compiles and
runs with exactly the flags every other chapter has used.

## The smallest server that works

@@minimal@@

That is the whole server: a listener, a context, a handler. Compare it with Chapter 25's
`ServerSocket` version and the split is clear.

**The server wrote for you:** the status line, the `Date` header, and the `Content-length`. It also
read the request head, split the request line, parsed every header, and handed the handler an object.
There is no `\r\n` anywhere in that code, and no byte counting.

**It did not write for you:** the content type (you set that), the body, and — this is the part that
matters — anything at all about what a path *means*. A context is a path prefix and a handler. There is
no router, no JSON, no templating, no sessions, no static files, no logging. Everything this Part adds
from here is a decision the JDK deliberately left open.

Note the header names the server sent: `Content-type` and `Content-length`, not `Content-Type` and
`Content-Length`. The JDK re-cases names on the way out. That is legal — Chapter 25 measured that
header names are case-insensitive — and it is the first of several places where this server's choices
are visible only if you look at the bytes.

## The three ways to say how long the body is

`sendResponseHeaders(int code, long length)` is the method that writes the status line and the headers,
and its second argument is doing more than it looks like it is:

@@lengths@@

Three calls, three different protocols:

- **`length` greater than zero** — that many bytes follow, and the response carries
  `Content-length: 12`. This is the one to use whenever you know the size.
- **`length` exactly zero** — the size is *not* known, so the server switches to
  `Transfer-encoding: chunked` and writes no `Content-length` at all. The body is a series of
  sized chunks, ending with a zero-sized one.
- **`length` less than zero** — there is no body, and the server omits `Content-length` entirely. With
  `204 No Content` that is exactly right.

The trap is the middle one, and it is a trap because `0` reads like "an empty body". It means the
opposite: an unknown-length body, framed the expensive way. An empty response is `-1`; a response whose
length you know is that length. Writing `sendResponseHeaders(200, 0)` and then a body gets you chunked
encoding, which is correct but not what you meant — and it is one of the few places where a wrong
number still produces a working response, which is why it survives testing.

:::warning
`204 No Content` and `304 Not Modified` must not have a body, and the JDK will let you try. If you call
`sendResponseHeaders(204, 5)` and write five bytes, the framing is wrong in a way a client cannot
recover from: the five bytes become the start of the next response on a keep-alive connection. Use
`-1` for both, and let the status code say what happened.
:::

## What the handler is handed

A handler receives an `HttpExchange`, and everything Chapter 25 did by hand is already done:

@@introspect@@

The method, the path, the raw query, the headers and the body — all parsed. `getRequestURI()` returns a
`java.net.URI`, which means every measurement from Chapter 25 applies directly: `getPath()` is decoded
and `getRawPath()` is not, and `getRawQuery()` returns `null` when there is no query. The escaping trap
does not go away because a framework is holding the string.

Two things about the body are worth naming.

`getRequestBody()` returns an `InputStream`, and `readAllBytes()` reads it into memory. For a note
service that is the right call — a note body is small and you want the whole thing before you parse it.
For an upload endpoint it is the wrong call, because the memory you use is the size of the request, and
the client controls the size. Chapter 34 comes back to that with a limit.

And the body must be read **before** the response is sent. On a keep-alive connection, unread request
bytes are still in the socket when the next request arrives, and the server will read them as the
beginning of the next request line. That is the same failure as Chapter 25's short response, seen from
the other side.

:::tip
`header(exchange, "x-note")` found a header the client sent as `X-Note`. That is Chapter 25's
case-insensitivity rule being enforced *for* you by the server's header map, and it is worth relying on
rather than reimplementing — a lookup helper that lowercases the name and then looks in a case-sensitive
map is a bug that only appears when a client's casing differs from your test's.
:::

## Contexts are path prefixes, matched by segment

`createContext(path, handler)` is the entire routing mechanism, and it has exactly two rules:

@@contexts@@

**A context matches whole path segments.** `/notes` matched `/notes`, `/notes/7` and `/notes/7/edit`,
because each of those begins with the segment `notes`. It did **not** match `/noteworthy`, even though
`/noteworthy` starts with the five characters `/note`. The match is on segments, so `notes` and
`noteworthy` are different words and not a prefix and a continuation.

**Where two contexts both match, the longest one wins.** `/notes/7` matched both `/notes` and `/`; the
handler that ran was `/notes`. That is the rule that lets a root context exist as a catch-all without
shadowing everything else.

Which makes the root context the design decision to make consciously. Registering `/` gives you a
handler that sees every request the more specific contexts did not take, and *not* registering it hands
those requests to the server — which brings us to the next section.

## An unmatched path is answered by the server, not by you

@@notfound@@

Three requests, and the third one is the interesting one. `/notes` and `/missing` were answered by
handlers, which set their own content type and their own status. `/no-such-context` was answered by
**the server itself**, and look at how different its response is:

- `Content-Length` — capital `L`, where every handler-written response said `Content-length`.
- `Content-Type: text/html` — and a body that is HTML, `<h1>404 Not Found</h1>No context found for
  request`.
- `Connection: close`, and **no `Date` header at all**.

So a service that registers only its own paths has two different 404 responses with two different
content types, and a client that asked for JSON gets a fragment of HTML. That is not a bug in the JDK;
it is the JDK declining to guess what your service's error format is. The repair is to register `/`
and return your own 404 in your own format, which is what Solution 1's router is for.

## One thread, unless you say otherwise

The last thing the server leaves to you is the most consequential, and it is a one-line omission with a
measurable effect. `HttpServer` uses an executor, and the default executor is **the single thread that
accepts connections**:

@@threads@@

Both runs fire two requests at the same moment, and both count two things: how many distinct threads
answered, and how many handlers saw *both* requests in flight before either replied.

With no executor set, **one** thread answered both requests, and only one handler ever saw both in
flight — because the second request could not even be accepted until the first handler returned. The
accept loop and the handler are the same thread, so a handler that waits is a server that stops
accepting. A handler that waits for *another request* — a lock, a cache warm-up, a call to the same
service — deadlocks a single-threaded server permanently.

With a fixed pool of two, two threads answered, and both handlers saw both requests in flight. The
accept loop was free to accept the second connection while the first handler was still running.

`server.setExecutor(Executors.newFixedThreadPool(4))` is the fix, and there are two details in it worth
noticing now because Chapter 30 is about them. The pool's threads are non-daemon by default, so the JVM
will not exit while the pool is alive — the block above calls `pool.shutdown()` for that reason. And
"four threads" is a *bound* on concurrency, not a guarantee of it; it says how many handlers may run at
once, and nothing about how quickly they finish.

:::scenario The response that declared 100 bytes and wrote 14

A handler is written in two steps that look independent:

```java
exchange.sendResponseHeaders(200, 100);
try (OutputStream out = exchange.getResponseBody()) {
    out.write("only fourteen!".getBytes(StandardCharsets.UTF_8));
}
```

The number 100 is a placeholder that was never replaced, and the body is fourteen bytes.

:::solution
The JDK does catch it — this is not one of the silent failures Chapter 25 measured:

@@scenario@@

The client received `HTTP/1.1 200 OK` with `Content-length: 100`, and then fourteen bytes. The handler
caught `java.io.IOException: insufficient bytes written to stream`, thrown when the response body was
closed with eighty-six bytes still owed.

The exception is better than silence, and it arrives **too late**. By the time it is thrown the status
line and the headers are already on the wire; a status code cannot be revised. The client is now
waiting for eighty-six bytes that will never arrive, and on a keep-alive connection those bytes would
be the next response's status line. So the handler's exception is a *log* entry, not a recovery — and
the repair has to be upstream of the response, which is Chapter 25's rule restated: derive the length
from the same byte array that produces the body.

There is one more thing to take from the shape of this bug. The two numbers were written on two
different lines, and nothing tied them together. `sendResponseHeaders(200, 100)` followed by a write is
the pattern to avoid; the pattern to want is a single value — a byte array, or a small record holding
the status, the content type and the bytes — that the writer consumes. Then there is no second number
to get wrong.
:::
:::

## Solutions

### 1. Routing is a pure function

Chapter 25's lesson was that a request is data. Here is the routing decision as data too, with no
server anywhere:

@@sol1@@

`route` takes a method and a path and returns a `Response`. There is no socket, no port, no server, no
thread — and therefore no flakiness, no timeout and no teardown. Every routing rule the service has is
visible in one function and testable in one loop.

Look at what the switch expresses. `405` is produced when the method is wrong, before the path is even
considered, because "this path exists but not for that method" is a different answer from "no such
path". `/notes/` is handled by a `startsWith` **outside** the switch, because it is a family of paths
rather than a fixed one. And the `default` arm returns the service's own 404 with its own content type —
which is the repair for the previous section, expressed as one line.

The server-side version of this is three lines: a context, a call to `route`, and a call to
`sendResponseHeaders` with the length of `response.body()`. **The router does not need to know it is on
a network**, and that separation is the difference between a service whose rules are testable and one
whose rules can only be exercised by making requests.

### 2. The query string is a map to a list

`getRawQuery()` gives you the raw text after the `?`, and it is still raw — no splitting, no decoding,
and `null` when there is nothing after the `?`:

@@sol2@@

Four decisions are packed into that small function, and each one is a decision because the spec does not
make it for you.

`null` and the empty string both produce an empty map. They are different inputs — one means there was
no `?` at all — and collapsing them is a choice, made here because every caller would otherwise have to
test for both.

A name with no `=` is **present with an empty value**, not absent. `?flag` and `?flag=` produce the same
map, and `flag` is a key in both. That matters for a filter: "the caller asked for the flag" and "the
caller did not mention the flag" are different intentions and a map that cannot tell them apart cannot
serve them.

A repeated name keeps every value, in the order written, which is why the type is a map to a list.
`?tag=a&tag=b` most naturally means "either tag" — a union — and a `Map<String, String>` would silently
keep only `b`.

And the values are decoded with `URLDecoder`, which is the right tool *here* and the wrong tool for a
path: it turns `+` into a space, which is correct in a query string and wrong in a path segment. Chapter
25 measured both spellings; this is where the measurement becomes a line of code.

### 3. The length argument wins over a header

Here is a small experiment with a surprising outcome. Set `Content-Length` by hand, then tell
`sendResponseHeaders` a different number:

@@sol3@@

The response says `Content-length: 11`, which is the length of the JSON body. The `999` that was set on
the header map is simply gone.

That is the right behaviour and the reason for it is the design of the API: the length is an argument
to `sendResponseHeaders` precisely so that it cannot drift from the body. A header map is for headers
whose value *is* the value you set — `Content-Type`, `Cache-Control`, `Location`. A header the server
must compute to keep the framing consistent is not yours to set, and the API takes it away from you.

The same experiment also shows the re-casing again: `Content-Type` went out as `Content-type`. If you
have ever wondered whether header names are really case-insensitive, this server normalises them on
every response, and every client that works with it is proof.

### 4. `set` replaces, `add` appends

A response header map is the same shape as a request header map — a name to a list — and the API gives
you two methods that differ only in which of those they do:

@@sol4@@

`set("X-Tag", "first")` followed by `set("X-Tag", "second")` left one header with the value `second`.
`set("Set-Cookie", "a=1")` followed by `add("Set-Cookie", "b=2")` left **two** `Set-cookie` headers, in
the order written.

The distinction is exactly Chapter 25's "a name may appear more than once", and it is the reason
cookies work at all: a response that sets two cookies must send two `Set-Cookie` headers, because a
single comma-separated header is not equivalent — cookie values are allowed to contain commas. Using
`set` for the second cookie silently drops the first, and the user's session disappears with it.

Notice too that the names went out as `Set-cookie` and `X-tag`. Same normalisation as before, and the
same conclusion: the wire spelling of a header name is not something to depend on in either direction.

## Key takeaways

- `com.sun.net.httpserver` is a **JDK module**: no dependency, and it compiles with the same flags as
  every other chapter.
- The server writes the status line, `Date`, `Content-length` and the framing. It does **not** write your
  content type, your body, or any opinion about what a path means.
- `sendResponseHeaders(code, length)`: **positive** = exactly that many bytes, **zero** = unknown length
  and chunked encoding, **negative** = no body. `0` does not mean "empty".
- `204` and `304` must have no body. Use a negative length, or the body poisons the next response on a
  keep-alive connection.
- A handler gets a parsed request — method, `URI`, headers, body stream. The `URI` rules from Chapter 25
  still apply: `getPath()` is decoded, `getRawPath()` is not, `getRawQuery()` may be `null`.
- Read the request body **before** sending the response, or its unread bytes are the next request's
  first line.
- A context matches **whole path segments** — `/notes` does not match `/noteworthy` — and the longest
  matching context wins.
- An unmatched path is answered by the **server**, with `Content-Type: text/html`, different header
  casing and no `Date`. Register `/` and return your own 404 in your own format.
- The default executor is the accepting thread. **One thread, one request at a time**, and a handler
  that waits stops the server accepting.
- `setExecutor` with a pool is the fix; the pool's threads are non-daemon, so shut it down or the JVM
  will not exit.
- Routing is a pure function of `(method, path)` returning a response value. Keep it out of the handler
  and it needs no server to test.
- A query string is a map to a **list**; a name with no `=` is present with an empty value; `null` and
  `""` are different inputs and only you can decide whether they mean the same thing.
- `Content-Length` is an argument to `sendResponseHeaders`, not a header you set — and if you set one
  anyway, the argument wins.
- `set` replaces, `add` appends. Two cookies need two `Set-Cookie` headers.

## Practice

- [ ] Register only `/notes` and request `/notes/7/edit`. Add a handler that pulls `7` out of the path.
      Where does that parsing belong — in the handler, or in the router from Solution 1?
- [ ] Make every response in the service go through one method that takes the `Response` record and
      writes it. What does that buy you for the 404 case, and what does it cost?
- [ ] Register `/` so nothing reaches the built-in 404, then prove with a raw client that the service
      never returns HTML.
- [ ] Change `Threads` to use a pool of four and re-measure. Which number changes, which does not, and
      why?
- [ ] Read `getRequestBody()` twice in one handler and report what the second read returns. Then explain
      why that is the same rule as "read the body before responding".
- [ ] Send a request with `Expect: 100-continue` and see what the server does with it. Which of the five
      status-code families is `100`, and what is the client supposed to do next?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The parsing belongs in the router, for the same reason `route` takes a `String` path rather than an
   `HttpExchange`: the moment a handler starts slicing paths it needs a request to be tested, and the
   rule "the third segment after `/notes/` is the id" becomes a fact that only exists inside a running
   server. Have `route` return either a `Response` or a value describing which handler and which
   argument, and the server-side code stays three lines.
2. Every response goes through one writer, which means the status line, the content type and the length
   are decided in **one** place — and the length comes from the byte array, so the scenario above cannot
   happen. The 404 case is the payoff: the built-in HTML 404 disappears entirely, because there is no
   path left that does not reach the writer. The cost is a little indirection: a handler can no longer
   stream a large body, because it has to produce the whole thing first. That is a real trade and it is
   the right one for small JSON responses.
3. Register `/` and return a 404 in the service's format. Prove it with a raw `Socket` rather than a
   client library, because the claim is about bytes: read the head, assert the status is `404`, assert
   the content type is the service's, and assert no `<h1>` appears anywhere in the body. A library would
   hide exactly the difference you are testing for.
4. The distinct-thread count changes only if there are more concurrent requests than the pool has
   threads; with two requests, a pool of two and a pool of four both answer on two threads. What does
   *not* change is the number of handlers that saw both requests in flight — it stays at two, because
   the constraint was never the pool size but whether the accept loop was free. The lesson is that a
   pool bounds concurrency without creating it.
5. The second read returns `-1`, immediately — the stream is at its end, and `-1` is the same value it
   would return for an empty body, which is why a double read is silent rather than an error. It is the
   same rule as reading before responding: the body is a stream with a position, it is consumed once,
   and any code that assumes otherwise is relying on a body it cannot see. If you need the bytes twice,
   read them once into a byte array.
6. `Expect: 100-continue` asks the server to send an interim `100 Continue` before the client commits to
   uploading the body, so that a request which is going to be rejected can be rejected without the
   upload. `100` is the **informational** family — the request was received and processing continues —
   and the client's next move is to send the body it was holding back. The reason it exists is worth
   carrying: a body can be expensive to send, and a protocol that lets the receiver say "don't bother"
   before the cost is paid is a protocol designed by people who had paid it.
"""

gen.write(TEMPLATE, BLOCKS)
