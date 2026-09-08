---
chapter: 24
part: 4
title: How the Web Works
summary: Understand the full life of a web request — DNS, TCP, TLS, HTTP, status codes, cookies — so that framework magic in Chapter 26 is a convenience rather than a mystery.
minutes: 35
tags: [http, dns, tls, status codes, cookies, devtools, client-server]
---

A web framework can hide the network from you, but the network is where every bug you have not
met yet is waiting: a request that never arrives, a response that is cached when it should not
be, a form that works once and then mysteriously does not, a page that is fine on your laptop and
broken for everyone else. Chapter 18 showed you how to *send* HTTP requests from Python. This
chapter is the other half: what happens on the wire, and what the server actually receives. Get
this straight and FastAPI in Chapter 26 reads as a convenient way to write things you already
understand instead of a box of tricks.

## The client/server model

Two programs, one conversation. The **client** (a browser, `curl`, `requests`, your own script)
asks. The **server** (a long-running process bound to a port on a machine that is always on)
answers. The server never initiates contact with the client — it cannot, because it does not know
the client's address until the client speaks first, and by then the conversation is already over.

That asymmetry explains a lot of web architecture:

- The client is untrusted and possibly hostile. Every value that arrives is attacker-controlled
  until proven otherwise.
- The server is shared. One process serves thousands of clients, so it must not keep per-client
  state in memory if it can avoid it.
- Push (notifications, live updates) is not part of the basic model. Chapter 28 covers how we
  fake it.

## What happens when you type a URL

You type `https://example.com/news?page=2` and press Enter. In about 200 milliseconds:

1. **Parse the URL.** The browser splits it into scheme (`https`), host (`example.com`), port
   (implied `443`), path (`/news`), and query (`page=2`).
2. **Check the cache.** Fresh copy in the HTTP cache? Use it, skip everything below. This is why
   "it works after a hard reload" is a real debugging clue.
3. **DNS resolution.** The host name is not routable; IP addresses are. The browser asks its
   resolver (your router, then your ISP, then the root name servers) for the address of
   `example.com`, walking `com` → `example.com` until it gets an `A`/`AAAA` record. Results are
   cached at every level for the duration of their TTL.
4. **TCP connection.** Three-way handshake: client sends `SYN`, server replies `SYN-ACK`, client
   sends `ACK`. A reliable, ordered byte stream now exists between the two machines.
5. **TLS handshake.** Because the scheme is `https`: the server presents a certificate chaining
   to a trusted root, the client verifies the name matches the host, and both sides derive a
   shared symmetric session key. Everything after this point is encrypted.
6. **Send the HTTP request.** Plain text over the encrypted tunnel:

   ```text
   GET /news?page=2 HTTP/1.1
   Host: example.com
   User-Agent: Mozilla/5.0 ...
   Accept: text/html,application/xhtml+xml
   Accept-Encoding: gzip, br
   Cookie: session=9f2c...
   ```

   An empty line, then — for GET — no body at all.
7. **Server work.** The server routes on method + path, reads headers and query string, parses
   cookies, possibly queries a database, and renders a response.
8. **Receive the HTTP response.** Status line, headers, blank line, body:

   ```text
   HTTP/1.1 200 OK
   Content-Type: text/html; charset=utf-8
   Content-Length: 14253
   Cache-Control: max-age=0, private, must-revalidate
   Set-Cookie: session=9f2c...; HttpOnly; Secure; SameSite=Lax
   ```

9. **Render.** The HTML parser builds the DOM, discovers `<link>`, `<script>`, and `<img>` tags,
   and — here is the part beginners miss — **repeats steps 3–8 for each one**. A "page load" is
   twenty to two hundred requests, not one.
10. **Close or reuse.** HTTP/1.1 keep-alive and HTTP/2 multiplexing reuse the connection. When it
    does close, it is a four-way `FIN`/`ACK` teardown.

Step 9 is why the Network tab in DevTools is the single most useful debugging tool in web
development: it shows you the whole conversation, request by request.

## The parts of a URL

```text
https://example.com:8443/news/world?page=2&tag=tech#comments
└─┬──┘ └────┬────┘ └┬─┘└───┬────┘└───────┬──────┘ └───┬───┘
scheme   host     port    path         query        fragment
```

| Part | Meaning | Who reads it |
| --- | --- | --- |
| scheme | `http` or `https`; also `mailto`, `ws` (WebSocket) | client |
| host | domain or IP; `localhost` means this machine | DNS, then server |
| port | defaults to 80 / 443; anything else must be explicit | TCP |
| path | which resource; what a framework routes on | server |
| query | `?key=value&key2=value2` — parameters, never secrets | server |
| fragment | `#comments` — **never sent to the server** | browser only |

Two things people get wrong: the fragment never appears in a request (it is client-side only,
which is why single-page apps use it for routing), and the query string is the wrong place for
anything sensitive — it lands in server logs, browser history, and `Referer` headers.

## HTTP in detail

### Methods, safety, and idempotency

| Method | Purpose | Safe | Idempotent | Body |
| --- | --- | --- | --- | --- |
| GET | Read a resource | yes | yes | no |
| HEAD | GET without a body | yes | yes | no |
| POST | Create, or trigger an action | no | no | yes |
| PUT | Replace a resource wholesale | no | yes | yes |
| PATCH | Modify part of a resource | no | yes | yes |
| DELETE | Remove a resource | no | yes | usually no |
| OPTIONS | Ask what is allowed | yes | yes | no |

- **Safe** means "does not change server state". Safe methods can be cached, prefetched, crawled,
  and retried without asking anyone.
- **Idempotent** means "sending it N times has the same effect as sending it once". `DELETE
  /tasks/12` twice leaves the task deleted. `POST /tasks` twice creates two tasks.

This is not pedantry. It is the rule that tells you what happens when the network is flaky: you
can retry a `GET` or a `PUT` freely, and you must not blindly retry a `POST /payments`. It is
also why browsers warn before resubmitting a form, and why a refresh after a purchase can charge
twice if the developer used `GET` for a state change. Never change state with `GET`.

### Headers

Headers are metadata: key-value pairs, one per line, terminated by a blank line. The useful ones:

```text
Host: example.com                  # which site, when one IP serves many
Content-Type: application/json     # how to interpret the body
Content-Length: 31                 # body size in bytes
Accept: application/json           # what the client wants back
Authorization: Bearer eyJhbGci...  # credentials
Cookie: session=abc123             # client sends what Set-Cookie stored
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
Cache-Control: no-store            # caching policy, both directions
Location: /tasks/12                # where to go, with 3xx
```

`Content-Type` is the one that bites. A client that sends JSON without
`Content-Type: application/json` gets nothing parsed on the server side, and a server that
returns JSON with `Content-Type: text/html` gets a rendered string in the browser.

### Status codes

| Class | Meaning | Ones you will actually see |
| --- | --- | --- |
| 1xx | Informational | `101 Switching Protocols` (WebSockets) |
| 2xx | Success | `200 OK`, `201 Created`, `204 No Content` |
| 3xx | Redirection | `301 Moved Permanently`, `302 Found`, `304 Not Modified`, `307/308` preserve the method |
| 4xx | Client error | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `429 Too Many Requests` |
| 5xx | Server error | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout` |

The mnemonic that matters: **4xx means the client has a problem, so stop retrying; 5xx means the
server has a problem, so retrying might work.** A `404` is not a bug in your code. A `500` is, and
the traceback is in your server log, not in the browser.

`201 Created` with a `Location` header is the correct answer to a successful `POST`. `204 No
Content` is right for a `DELETE` that has nothing to say. FastAPI gets these right for you once
you return the right thing.

## Statelessness, and how we fake state

HTTP is stateless: each request is complete in itself, and the server is under no obligation to
remember anything about the previous one. This is a feature. It means any server in a fleet can
handle any request, which is why you can scale a web app horizontally by adding machines.

It also means "logged in" needs machinery, and there are three standard answers:

1. **Cookies** — the server sends `Set-Cookie: session=abc123`; the browser stores it for that
   domain and attaches `Cookie: session=abc123` to every subsequent request automatically. A
   cookie is storage in the client, not state in the server.
2. **Sessions** — the cookie holds only an opaque id. The server keeps a dictionary (in memory,
   in Redis, in a signed cookie) mapping `abc123` → `{user_id: 7, ...}`. Server-side state, keyed
   by a client-held token.
3. **Tokens** — the cookie (or an `Authorization: Bearer ...` header) carries a signed blob,
   typically a JWT, containing the claims themselves. The server verifies the signature instead of
   looking anything up. Stateless again, at the cost of not being able to revoke a token before it
   expires.

All three are the same trick: the client presents a credential on every request, and the server
reconstructs who you are from it. Nothing is "remembered" between requests; it is re-derived every
time.

## HTTPS and TLS in one paragraph

TLS is a layer between TCP and HTTP that provides three things: **encryption** (a passive observer
sees only ciphertext), **integrity** (a modified byte is detected), and **authentication** (the
certificate chain proves you are talking to the real `example.com` and not someone who
intercepted the connection). The certificate is signed by a certificate authority whose public key
ships in your operating system's trust store; if the signature or the hostname does not check
out, the browser refuses to connect, and that refusal is the only thing standing between a user
and a man-in-the-middle. On a public site, HTTPS is not optional. Locally, `http://127.0.0.1:8000`
is fine because there is no network to eavesdrop on.

## Static vs dynamic

A **static** response is a file on disk: the bytes are the same for everyone, so a CDN can cache
it at the edge and your server never sees the request. HTML, CSS, JS, images, fonts.

A **dynamic** response is generated per request by your code: it depends on the URL, the user, the
time, and the contents of a database. It cannot be cached by a CDN (at least not without careful
`Cache-Control` headers), and it is where your Python runs.

The practical rule: serve `/static/*` from disk (or a CDN), and keep everything else dynamic. Mixing
them up — generating CSS in Python, or serving a user-specific page from a cache — is a source of
both slow sites and data leaks.

## What a web framework actually does

Given a request, every framework performs the same six jobs. Knowing them turns the framework from
magic into a to-do list you could implement yourself (and Chapter 30's capstone basically does):

1. **Listen** on a socket and speak HTTP (or delegate to a server like Uvicorn that does).
2. **Route** — map `(method, path)` to a Python function. `/tasks/12` with `GET` → `read_task(12)`.
3. **Parse** — read the query string, headers, cookies, and body; turn JSON into `dict`s and form
   fields into Python values.
4. **Validate** — reject garbage with a `422` before your code sees it. This is most of what
   FastAPI's type hints buy you.
5. **Execute** your handler, which talks to a database and returns data.
6. **Serialize** — turn your return value into an HTTP response with the right status, headers,
   and body (JSON for an API, HTML from a template for a page).

Plus the cross-cutting parts: authentication, error handling, CSRF protection, and static files.

## localhost, ports, and why 127.0.0.1:8000 means what it means

A machine has one network identity but needs to run dozens of networked programs at once, so
**ports** (0–65535) distinguish them. One process binds one port. `127.0.0.1` is the loopback
address: it always means "this machine", and traffic to it never leaves the computer. `localhost`
is the host name for the same thing (usually resolving to `127.0.0.1`, sometimes to `::1` for
IPv6 — a classic "why does it work with one and not the other" bug).

So `http://127.0.0.1:8000` reads as: plain HTTP, to a server on *my own machine*, on port 8000.
Nothing else on the internet can reach it, which is exactly what you want during development.

Ports below 1024 are privileged and need root, which is why development servers use 8000, 5000,
or 3000. Watch for these:

```bash
python3 -m http.server 8000        # static file server, useful for testing
python3 -m uvicorn main:app --reload   # what Chapter 26 will use
```

```text
ERROR:    [Errno 48] Address already in use
```

Something already holds the port — usually a previous run of your own server that you started with
`--reload` and forgot about. Find and stop it (`lsof -i :8000` on macOS/Linux,
`netstat -ano | findstr :8000` on Windows) rather than blindly switching ports, or you will end up
debugging a stale process.

## Seeing a real request in DevTools

Theory is cheap; here is the practice. In Chrome or Firefox: press `F12`, open the **Network**
tab, tick **Disable cache**, load a page, and click the first request. You get:

- **Headers** — the exact request line, request headers, response headers, and status code.
- **Response** — the body you got back (HTML, JSON, whatever).
- **Timing** — how long DNS, connect, TLS, waiting (server time), and download each took. If
  "Waiting" is 3 seconds, your Python or your database is slow. If "DNS" is 3 seconds, it is not
  your problem.
- **A list of every sub-resource**, with a waterfall showing what loaded in parallel and what
  blocked.

Do this once on a site you use daily. Twenty requests becomes obvious, and so does how much of
"the page" is JavaScript and images rather than the HTML you think of as the page.

## JSON APIs vs server-rendered HTML

Two ways to deliver the same application.

**JSON API + JavaScript front end.** The server returns data; the browser runs JS that fetches it
and rewrites the page in place.

```json
{ "id": 12, "title": "Write the report", "done": false, "priority": "high" }
```

Same origin, no reload, and the same API serves your mobile app. Costs you a second codebase in
JavaScript, and the first request renders little or nothing.

**Server-rendered HTML.** The server returns a complete page; the browser just displays it.

```html
<li class="task priority-high">Write the report <span class="due">Fri</span></li>
```

Fast first paint, no JavaScript required, forms work without a framework, and your Python stays
the only language in the project. Navigation means a page load.

This book teaches both, deliberately. Chapters 26 and 27 build a JSON API with FastAPI. Chapter 28
adds templates and HTMX, which keeps the logic in Python and swaps HTML fragments over the wire —
for a Python developer, usually the better trade.

## What FastAPI will do

Chapter 26 starts here:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/tasks/{task_id}")
def read_task(task_id: int) -> dict:
    return {"id": task_id, "title": "Write the report", "done": False}
```

FastAPI reads the decorator to build the route, the `task_id: int` annotation to convert and
validate the path parameter (a non-integer gets a `422` with a precise error message, not a
`500`), the return annotation to document the response, and — because the function returns a
`dict` — serialises it to JSON with `Content-Type: application/json`. It also generates an
interactive API documentation page from those same annotations. Every line of that is one of the
six framework jobs above, made declarative.

:::scenario "It works on my machine" — the form submits twice in production
You built a checkout form. On your laptop it works. In production, customers are charged twice.
The code has not changed and there are no errors in the logs.
:::

:::solution The bug is in the method, and the fix is POST + redirect + token
Three separate things are going wrong, and they compound.

**1. The form probably used `GET`, or submitted to a URL that leaves a state change on reload.**
If `/charge?amount=49` is a `GET`, then every prefetch, every crawler, and every refresh after
submission runs the charge. Change state only with `POST`, and never put an amount in a URL — the
client can edit it.

**2. After a successful POST, redirect.** This is the **POST/redirect/GET** pattern. Returning
HTML directly from a `POST` means the browser's current URL is the state-changing one, so refresh
re-submits. Return `303 See Other` with a `Location` header instead:

```python
@app.post("/checkout")
def checkout(payload: CheckoutIn):
    order = charge(payload)
    return RedirectResponse(url=f"/orders/{order.id}", status_code=303)
```

After the redirect, the browser's URL is `/orders/42` — a `GET` — so refresh reloads a
confirmation page instead of re-charging.

**3. Even with all that, a double-click or a retry can send two POSTs.** Add an **idempotency
key**: the client generates a UUID per checkout attempt and sends it in a header; the server
records `(key) → (result)` and returns the stored result if it sees the key again.

```python
@app.post("/checkout")
def checkout(payload: CheckoutIn, idempotency_key: str = Header(alias="Idempotency-Key")):
    if (existing := store.get(idempotency_key)) is not None:
        return existing
    result = charge(payload)
    store[idempotency_key] = result
    return result
```

The general lesson: pick the method for its semantics, not its convenience. `GET` for reads,
`POST` for actions, redirect after a state change, and an idempotency key when money is involved.
:::

:::pitfall Assuming the server remembers anything between requests
This is the mistake that separates "it works locally" from "it works", and it shows up in four
common shapes:

```python
# WRONG: module-level state
current_user = None
recent_searches = []


@app.get("/me")
def me():
    return current_user  # whose? every user shares this variable
```

1. **Shared global state.** A module-level variable is shared by every request from every user.
   With one Uvicorn worker and one user it "works". With two users, or with `--workers 4`, user A
   sees user B's data. That is not a race you can win with a lock; it is the wrong place for the
   data. Per-user state goes in a database, in Redis, or in a signed cookie.
2. **Assuming one process.** Production runs several worker processes, often on several machines.
   Anything you cached in memory exists in exactly one of them, so the next request — possibly
   routed elsewhere — misses it, and your behaviour becomes load-dependent and unreproducible.
3. **Assuming order.** Nothing guarantees request 2 follows request 1, or that they hit the same
   process, or that a request was not retried. Never write code of the form "step 1 stores it in a
   global, step 2 reads it back". Carry the state in the request: a cookie, a token, a hidden form
   field, or a database row keyed by an id.
4. **Assuming the client is still there.** A user closes the tab mid-checkout. Your server has no
   idea. Timeouts, cleanup jobs, and "resume where you left off" all have to be derived from
   persisted state, never from a live connection.

When you catch yourself writing `global`, or storing something "for the next request", stop and
ask where it lives if there are four processes and the user comes back tomorrow. The answer is
almost always: a row in the database.
:::

## Key takeaways

- A browser and a server hold a request/response conversation the client always starts; the server
  never initiates contact.
- Loading one page means DNS → TCP → TLS → request → response → render, then that whole cycle
  again for every stylesheet, script, and image.
- URLs split into scheme, host, port, path, query, and fragment; the fragment never reaches the
  server and the query string is never private.
- Safe methods do not change state; idempotent methods can be repeated with the same effect. Never
  use `GET` for a state change.
- Status codes are a contract: 2xx succeeded, 3xx go elsewhere, 4xx is the client's fault (do not
  retry), 5xx is the server's fault (retrying may help).
- HTTP is stateless; login works because the client re-presents a cookie or token on every single
  request and the server re-derives who you are.
- `127.0.0.1:8000` means "a server on my own machine, on port 8000" — unreachable from anywhere
  else, which is what makes it safe for development.
- A framework routes, parses, validates, executes, and serialises; FastAPI does all six from your
  type hints and decorators.
- The DevTools Network tab shows the real request, the real response, and where the time went.

## Practice

- [ ] Run `curl -i https://example.com` and write down the status line, three response headers,
      and where the body starts.
- [ ] Start `python3 -m http.server 8000` in a folder with an `index.html`, open
      `http://127.0.0.1:8000`, then read the request line the server printed to the terminal.
      Explain in one sentence why no other computer can reach it.
- [ ] Send a `GET` and then a `POST` to `https://httpbin.org/get` and `https://httpbin.org/post`.
      Run each twice and note which one is idempotent.
- [ ] Use `curl -c cookies.txt https://httpbin.org/cookies/set?theme=dark` then
      `curl -b cookies.txt https://httpbin.org/cookies`. Explain what the two flags do and how
      the server recognised you on the second call.
- [ ] Collect one example of each status class using `curl -i`: `200`, `301`, `404`, and a `500`
      from a deliberately broken local server.
- [ ] Open DevTools on a site you use, disable cache, reload, and report: how many requests, which
      took longest, and which part of the timing (DNS, connect, waiting, download) dominated.

## Solutions

:::solution Exercise 1
```bash
curl -i https://example.com
```
```text
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1256
Cache-Control: max-age=604800

<!doctype html>
<html>...
```
`-i` includes the response headers. The blank line after the headers is the separator: everything
above it is metadata, everything below is the body. `Content-Length` tells the client how many
bytes to read; `Cache-Control: max-age=604800` tells it not to ask again for a week.
:::

:::solution Exercise 3
```bash
curl https://httpbin.org/get
curl -X POST https://httpbin.org/post -d "name=ada"
```
```text
{
  "args": {},
  "headers": { "Host": "httpbin.org", ... },
  "url": "https://httpbin.org/get"
}
```
Running `GET` twice produces the same response both times and changes nothing on the server — it
is safe and idempotent. Running `POST` twice creates two submissions; the server's state differs
after the second call, so it is neither safe nor idempotent. That is why a browser warns before
resubmitting a form and why your checkout endpoint needs an idempotency key.
:::

:::solution Exercise 4
```bash
curl -c cookies.txt "https://httpbin.org/cookies/set?theme=dark"
curl -b cookies.txt "https://httpbin.org/cookies"
```
```text
{
  "cookies": {
    "theme": "dark"
  }
}
```
`-c` writes cookies the server sent into a file (the "cookie jar"); `-b` reads them back and
attaches them to the next request. The second request arrives with `Cookie: theme=dark`, and the
server — which remembered nothing — reads your identity/preferences back out of it. This is
exactly what a browser does automatically, and it is the entire basis of "staying logged in".
:::

:::solution Exercise 5
```bash
curl -i https://example.com/                       # 200 OK
curl -i http://github.com                          # 301 Moved Permanently + Location
curl -i https://httpbin.org/status/404             # 404 Not Found
python3 -c "from http.server import HTTPServer, BaseHTTPRequestHandler as H; \
class B(H):
 def do_GET(s): raise ValueError('boom')
HTTPServer(('127.0.0.1', 8001), B).serve_forever()" &
curl -i http://127.0.0.1:8001/                     # 500 Internal Server Error
```
```text
HTTP/1.1 500 Internal Server Error
Content-Type: text/plain;charset=utf-8
```
The `301` response carries a `Location:` header — that header *is* the redirect; `curl -L` follows
it. The `500` proves the point about where errors live: the browser gets one meaningless line and
the actual traceback is in the server's terminal. When a local app returns `500`, always read the
server log, never the page.
:::

:::solution Exercise 6
Typical result for a news site: 180 requests, 2.4 MB, finish in 3.1 s. The slowest single item is
usually a tracking script or a hero image, not the HTML. The timing breakdown is where the
diagnosis lives:

- **DNS/Connect/TLS** large → network or certificate problem, not your code.
- **Waiting (TTFB)** large → the server is slow: your Python handler or a database query.
- **Download** large → the payload is too big; compress, resize, or lazy-load.

If the HTML itself is only 20 KB and the remaining 2.38 MB is scripts and images, optimising your
Python is the wrong fix — no matter how tempting it is.
:::
