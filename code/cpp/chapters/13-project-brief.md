---
chapter: 13
part: 3
title: The Project — A Static HTTP Server
summary: Understand what a systems tool is, read HTTP as the plain text it actually is, and build the request-to-response core that the rest of the project wraps in a socket loop.
minutes: 55
tags: [http, server, request, response, content-length, status-code, systems]
---

Every program so far has run and stopped. A systems tool is a program that keeps running and talks
to the outside world: it waits, it answers, it stays up, and it keeps working when the thing on the
other end misbehaves. The clearest first example is an HTTP server, because you use one every day and
its wire format is plain text you can read with your own eyes. Building one in C forces the three
things this part is about — bytes on a socket, files on a disk, and a request from a stranger that
you must not trust. By the end of Part III you will have a working static file server, and you will
have watched it answer real requests.

## What makes something a "systems tool"

The difference is not size. It is that the program sits between the operating system and a client,
and it owns resources that the operating system will not clean up for it.

A normal program opens a file, reads it, exits. The kernel reclaims everything. A server is
different in three specific ways, and each one is a category of bug you have not had to think about:

- **It runs forever.** Any resource it acquires per request must be released per request, or the
  thousandth request fails where the first succeeded.
- **It is driven by untrusted input.** The bytes arriving on the socket were chosen by someone else.
  A path like `/../../etc/passwd` is not a filename, it is an attack, and the server has to decide
  that deliberately rather than by accident.
- **It fails partially.** A read that returns 3 bytes when you wanted 40 is normal, not exceptional.
  Code written for files assumes a read either works or fails; code written for sockets cannot.

Those three are the whole reason this project exists. Everything you learned in Parts I and II gets
used, but the failure modes are new.

## HTTP is text on a wire

An HTTP exchange is two messages of plain ASCII. A request looks like this, and the bytes between
the lines are the characters `\r` and `\n` — carriage return and line feed, not a newline character
alone:

```c run
#include <stdio.h>
#include <string.h>

static void dump(const char *label, const char *data, size_t len) {
    printf("%s (%zu bytes)\n", label, len);
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)data[i];
        if (c == '\r')      fputs("\\r", stdout);
        else if (c == '\n') fputs("\\n\n", stdout);
        else                putchar(c);
    }
}

int main(void) {
    const char *request =
        "GET /index.html HTTP/1.1\r\n"
        "Host: localhost:8080\r\n"
        "Accept: */*\r\n"
        "\r\n";

    dump("request", request, strlen(request));

    const char *body = "<h1>Hello</h1>\n";
    char response[512];
    int n = snprintf(response, sizeof response,
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: %zu\r\n"
        "\r\n"
        "%s",
        strlen(body), body);

    dump("response", response, (size_t)n);
    return 0;
}
```

```text
request (63 bytes)
GET /index.html HTTP/1.1\r\n
Host: localhost:8080\r\n
Accept: */*\r\n
\r\n
response (79 bytes)
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 15\r\n
\r\n
<h1>Hello</h1>\n
```

Read that output slowly, because the whole protocol is in it.

- The first line of the request is the **request line**: method, target, version, separated by single
  spaces and ended by `\r\n`.
- After it come **headers**, one per line, also `\r\n`-terminated.
- A **blank line** — that is, `\r\n` immediately after a `\r\n` — ends the headers. That empty line is
  the single most important byte pair in the protocol, because it is how both sides know the metadata
  has stopped.
- The response has the same shape, except the first line is a **status line**: version, numeric
  status code, and a human-readable reason phrase.

Two details in that dump are worth more than the rest. First, `Content-Length: 15` is the length of
the *body* — the `<h1>Hello</h1>\n` — and not the length of the whole message, which is 79 bytes.
Second, the body is not terminated by anything. The client reads exactly `Content-Length` bytes and
then stops. There is no closing marker, no NUL, no terminator of any kind. If you get that number
wrong the client will hang waiting for bytes that never come, or silently truncate what it received.

The `dump` helper above is worth keeping. Printing `\r` and `\n` as visible escape sequences is the
only way to see this protocol's structure; if you print the raw bytes, every line just ends and you
cannot tell a correct message from one missing its blank line.

## The shape of the whole server

Strip away the sockets and the files and an HTTP server is a function from a request to a response.
That function is where all the logic lives, and it is the only part worth testing carefully:

```c run
#include <stdio.h>
#include <string.h>

/* The whole server is this shape: text in, text out.
   A real server reads a file and opens a socket here; the skeleton is identical. */
static size_t respond(const char *status, const char *body, char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: %zu\r\n"
        "\r\n"
        "%s", status, strlen(body), body);
    return n > 0 ? (size_t)n : 0;
}

static size_t handle(const char *request, char *out, size_t outsz) {
    const char *eol = strstr(request, "\r\n");
    size_t line_len = eol ? (size_t)(eol - request) : strlen(request);

    char line[256];
    if (line_len >= sizeof line)
        return respond("414 URI Too Long", "request line too long\n", out, outsz);
    memcpy(line, request, line_len);
    line[line_len] = '\0';

    char method[16], target[128], version[16];
    if (sscanf(line, "%15s %127s %15s", method, target, version) != 3)
        return respond("400 Bad Request", "malformed request line\n", out, outsz);
    if (strcmp(method, "GET") != 0)
        return respond("405 Method Not Allowed", "only GET is supported\n", out, outsz);

    char body[256];
    snprintf(body, sizeof body, "you asked for %s\n", target);
    return respond("200 OK", body, out, outsz);
}

static void dump(const char *label, const char *data, size_t len) {
    printf("--- %s (%zu bytes) ---\n", label, len);
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)data[i];
        if (c == '\r')      fputs("\\r", stdout);
        else if (c == '\n') fputs("\\n\n", stdout);
        else                putchar(c);
    }
}

int main(void) {
    const char *requests[] = {
        "GET /about.html HTTP/1.1\r\nHost: x\r\n\r\n",
        "POST /about.html HTTP/1.1\r\nHost: x\r\n\r\n",
        "nonsense\r\n\r\n",
    };
    for (size_t i = 0; i < sizeof requests / sizeof requests[0]; i++) {
        char out[1024];
        size_t n = handle(requests[i], out, sizeof out);
        dump("response", out, n);
    }
    return 0;
}
```

```text
--- response (91 bytes) ---
HTTP/1.1 200 OK\r\n
Content-Type: text/plain\r\n
Content-Length: 26\r\n
\r\n
you asked for /about.html\n
--- response (103 bytes) ---
HTTP/1.1 405 Method Not Allowed\r\n
Content-Type: text/plain\r\n
Content-Length: 22\r\n
\r\n
only GET is supported\n
--- response (97 bytes) ---
HTTP/1.1 400 Bad Request\r\n
Content-Type: text/plain\r\n
Content-Length: 23\r\n
\r\n
malformed request line\n
```

Three things in `handle` are deliberate and you should copy them into your own code.

**`strstr(request, "\r\n")` finds the end of the request line**, and the code copies exactly that
many bytes into a fixed buffer before adding a NUL. It does not call `strtok`, and it does not modify
the caller's buffer. A server parses the same request more than once — for logging, for routing — so
a parser that destroys its input is a parser you can only call once.

**`sscanf` with explicit field widths.** `%15s` into `char method[16]` means "at most 15
non-whitespace characters". Without the width, a client sending a 4000-character method overflows the
buffer, which is a remote code execution bug in a server. The number in the format string must always
be one less than the size of the array, because `%s` appends a NUL.

**Every path out of the function returns a complete response.** There is no `return 0` for "nothing
to do". A client is waiting for bytes; a function that returns nothing leaves that client hanging
until it times out. If you cannot produce a real answer, produce an error page.

## The four layers

The project is built in four layers, and keeping them apart is what makes it testable. Each layer
knows only about the one below it.

| Layer | Question it answers | Where the bugs live |
|---|---|---|
| **Parse** | What did the client ask for? | Buffer overflows, missing field widths, assuming the whole request arrived at once |
| **Resolve** | Which file on disk is that, and is it allowed? | Path traversal, percent-encoding, symlinks |
| **Build** | What bytes should go back? | `Content-Length` mismatches, wrong `Content-Type`, non-terminated strings |
| **Send** | Push those bytes onto the socket | Partial writes, `SIGPIPE`, file descriptors that are never closed |

Only the first two are pure functions of their input, which is why they are the two we will test
hardest. The send layer is where C servers die in production, and it gets its own chapter.

## Getting the headers right

Forgetting an include in C is not a warning. It is an error, and a loud one:

```c bad
#include <stdio.h>

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) { perror("socket"); return 1; }
    close(fd);
    return 0;
}
```

```text
call to undeclared function 'socket'
```

That message is worth reading carefully, because it is C telling you something the C++ track would
not. In C, a call to a function the compiler has never seen is not automatically fatal by the
language standard — but since C99 it is an error, and clang reports it as
`ISO C99 and later do not support implicit function declarations`. The lesson is that `socket`,
`AF_INET`, `SOCK_STREAM` and `close` all live in headers you must include: `<sys/socket.h>` for the
first three, `<unistd.h>` for `close`. The compiler names the identifier it does not recognise, so
read the list of errors rather than only the first one.

## Comparing the method

The other mistake that every first HTTP server makes is comparing the method with `==`:

```c warn
#include <stdio.h>
#include <string.h>

int main(void) {
    char method[16] = "GET";
    if (method == "GET") {
        printf("it was a GET\n");
    }
    return 0;
}
```

```text
result of comparison against a string literal is unspecified
```

`method` is an array, and an array in an expression decays to a pointer to its first element. So
`method == "GET"` compares two *addresses*: the address of your local array against the address of
the string literal. They are never equal, so the branch is never taken, and the program does nothing
while looking perfectly correct. It compiles, it runs, it is wrong.

You met this in the chapter on strings, and the fix is `strcmp(method, "GET") == 0`. What is new here
is that clang can catch it — but only in this exact form. It fires when one side is written out as a
literal at the comparison. Store the literal in a `const char *` variable first and the warning
disappears while the bug stays, which is why `strcmp` has to be a habit rather than something you
wait to be told about.

:::scenario The server that ran out of file descriptors at request 1,018

A developer deploys a small C server to a staging box. It works all morning. In the afternoon it
stops answering and the log fills with `accept: Too many open files`. Restarting fixes it, so the
team calls it a memory leak for two days.

It is not a memory leak. Every request path in the code looks like this:

```c run
#include <stdio.h>
#include <string.h>

/* A stand-in for "handle one connection", so the shape is visible. */
static int handle_one(int fake_connection_fd, const char *request) {
    if (strncmp(request, "GET ", 4) != 0) {
        return 404;                 /* <-- returns without closing anything */
    }
    printf("served %d\n", fake_connection_fd);
    return 200;
}

int main(void) {
    const char *requests[] = { "GET /a", "POST /b", "GET /c", "DELETE /d" };
    int open_handles = 0;
    for (size_t i = 0; i < sizeof requests / sizeof requests[0]; i++) {
        open_handles++;                       /* the accept() in a real server */
        int status = handle_one(100 + (int)i, requests[i]);
        if (status == 200) {
            open_handles--;                   /* only the happy path closes it */
        }
        printf("  %-10s -> %d, open handles now %d\n", requests[i], status, open_handles);
    }
    printf("after 4 requests: %d handle(s) still open\n", open_handles);
    return 0;
}
```

```text
served 100
  GET /a     -> 200, open handles now 0
  POST /b    -> 404, open handles now 1
served 102
  GET /c     -> 200, open handles now 1
  DELETE /d  -> 404, open handles now 2
after 4 requests: 2 handle(s) still open
```

The error paths return early and never close the connection. Two of four requests leaked a
descriptor, so the process dies at roughly a thousand requests — which is why it survived testing and
died in production. The limit is `ulimit -n`, and on macOS it defaults to 256, so the real server
would have died much sooner than the developer's mental model suggested.

:::solution Close on every path, or close in one place

The fix is structural rather than a matter of remembering. Either close before every `return`, or
restructure so there is exactly one exit:

```c run
#include <stdio.h>
#include <string.h>

/* One exit. `status` is decided first; the cleanup happens once. */
static int handle_one(int fake_connection_fd, const char *request) {
    int status;
    if (strncmp(request, "GET ", 4) != 0) {
        status = 404;
    } else {
        printf("served %d\n", fake_connection_fd);
        status = 200;
    }
    /* close(fake_connection_fd);  <- the real server's single cleanup point */
    return status;
}

int main(void) {
    const char *requests[] = { "GET /a", "POST /b", "GET /c", "DELETE /d" };
    int open_handles = 0;
    for (size_t i = 0; i < sizeof requests / sizeof requests[0]; i++) {
        open_handles++;
        int status = handle_one(100 + (int)i, requests[i]);
        open_handles--;                       /* now unconditional */
        printf("  %-10s -> %d, open handles now %d\n", requests[i], status, open_handles);
    }
    printf("after 4 requests: %d handle(s) still open\n", open_handles);
    return 0;
}
```

```text
served 100
  GET /a     -> 200, open handles now 0
  POST /b    -> 404, open handles now 0
served 102
  GET /c     -> 200, open handles now 0
  DELETE /d  -> 404, open handles now 0
after 4 requests: 0 handle(s) still open
```

Every request now returns to zero. This is the same discipline as `free` in the dynamic memory
chapter, applied to a different kind of resource: acquire once, release once, and make the release
impossible to skip. When the project gets real, the release will be `fclose`, `close`, and `free`,
and it will happen on the same single path.

:::

:::pitfall One read does not give you the whole request

This is the bug that separates code that works on your laptop from code that works. A single `read`
on a socket returns **whatever has arrived so far** — not the whole request, and not even a whole
line. A client on the same machine usually delivers the request in one packet, so
`read(fd, buf, sizeof buf)` appears to work. A client on a real network, or a slow client, or a
client sending a large header, delivers it in pieces.

```c run
#include <stdio.h>
#include <string.h>

static void show(const char *label, const char *buf) {
    printf("%s: ", label);
    for (const char *p = buf; *p != '\0'; p++) {
        if (*p == '\r')      fputs("\\r", stdout);
        else if (*p == '\n') fputs("\\n\n", stdout);
        else                 putchar(*p);
    }
    printf("  complete? %s\n", strstr(buf, "\r\n\r\n") ? "yes" : "no");
}

int main(void) {
    const char *piece_1 = "GET /index.html HTT";
    const char *piece_2 = "P/1.1\r\nHost: x\r\n\r\n";

    char buf[128];
    snprintf(buf, sizeof buf, "%s", piece_1);
    show("after first read ", buf);
    strcat(buf, piece_2);
    show("after second read", buf);
    return 0;
}
```

```text
after first read : GET /index.html HTT  complete? no
after second read: GET /index.html HTTP/1.1\r\n
Host: x\r\n
\r\n
  complete? yes
```

The first read produced a request that does not parse. A server that assumes one read is enough will
answer `400 Bad Request` to a perfectly valid request, intermittently, depending on network timing.

The rule is: **read in a loop until you have seen the end of the headers**, which is the byte
sequence `\r\n\r\n`. If you never see it and the buffer fills up, answer `431` or `400` and close.
Never loop forever waiting for a client that has stopped sending — that is how a server becomes
trivially easy to hang. The socket chapter builds this loop properly.

:::

## Key takeaways

- A systems tool keeps running and owns resources per request; anything acquired per request must be
  released per request, on every path out of the handler.
- HTTP is plain ASCII. Lines end with `\r\n`, and a blank line ends the headers.
- `Content-Length` counts **body** bytes, not total bytes. The body has no terminator, so that number
  is the only thing telling the client where the message stops.
- `%s` in `scanf`/`sscanf` must carry a width one less than the destination array. Without it, remote
  input overflows a local buffer.
- Parse the request line by locating `\r\n` and copying exactly that many bytes; do not destroy the
  caller's buffer, because you will want to parse it more than once.
- A handler must always produce a response. Returning nothing leaves the client waiting until it
  times out.
- In C, calling a function whose header you have not included is an error
  (`call to undeclared function 'socket'`), so a missing include is caught at build time.
- `method == "GET"` compares addresses, never matches, and is caught by `-Wstring-compare` only when
  the literal is written at the comparison. Use `strcmp`.
- One `read` on a socket does not return the whole request. Loop until you see `\r\n\r\n`.

## Practice

- [ ] Write a program that prints a hard-coded request and response with `\r` and `\n` shown as
      escape sequences, and print the byte length of each.
- [ ] Write `static const char *reason(int code)` returning the reason phrase for `200`, `400`, `403`,
      `404`, `405`, `414` and `500`, and `"Unknown"` for anything else.
- [ ] Write `handle` that additionally rejects a target longer than 128 characters with `414`, and
      test it with a target of exactly 128 and one of 129.
- [ ] Write a program that builds a response for a body containing a NUL byte and prints the
      `Content-Length` it computed, explaining in a comment why `strlen` is the wrong tool.
- [ ] Write a function that reports whether a buffer contains the end of the headers, and use it to
      print the verdict for four different partial requests.
- [ ] Explain, in one sentence each, why the parse layer and the resolve layer are the two that can
      be tested with ordinary function calls while the send layer cannot.

## Solutions

:::solution Exercise 1

```c run
#include <stdio.h>
#include <string.h>

static void dump(const char *label, const char *data, size_t len) {
    printf("%s (%zu bytes)\n", label, len);
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)data[i];
        if (c == '\r')      fputs("\\r", stdout);
        else if (c == '\n') fputs("\\n\n", stdout);
        else                putchar(c);
    }
}

int main(void) {
    const char *request  = "GET / HTTP/1.1\r\nHost: x\r\n\r\n";
    const char *response = "HTTP/1.1 204 No Content\r\n\r\n";
    dump("request",  request,  strlen(request));
    dump("response", response, strlen(response));
    return 0;
}
```

```text
request (27 bytes)
GET / HTTP/1.1\r\n
Host: x\r\n
\r\n
response (27 bytes)
HTTP/1.1 204 No Content\r\n
\r\n
```

A `204` has no body and therefore needs no `Content-Length` at all, which is a good reminder that the
header is about the body and not a mandatory part of the message.

:::

:::solution Exercise 2

```c run
#include <stdio.h>
#include <string.h>

static const char *reason(int code) {
    switch (code) {
    case 200: return "OK";
    case 400: return "Bad Request";
    case 403: return "Forbidden";
    case 404: return "Not Found";
    case 405: return "Method Not Allowed";
    case 414: return "URI Too Long";
    case 500: return "Internal Server Error";
    default:  return "Unknown";
    }
}

int main(void) {
    int codes[] = { 200, 301, 403, 404, 418, 500 };
    for (size_t i = 0; i < sizeof codes / sizeof codes[0]; i++)
        printf("%d %s\n", codes[i], reason(codes[i]));
    return 0;
}
```

```text
200 OK
301 Unknown
403 Forbidden
404 Not Found
418 Unknown
500 Internal Server Error
```

Returning `"Unknown"` rather than `NULL` keeps the caller simple: the status line is always
printable, and a code you did not plan for still produces a valid response.

:::

:::solution Exercise 3

```c run
#include <stdio.h>
#include <string.h>

static size_t respond(const char *status, const char *body, char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\nContent-Type: text/plain\r\nContent-Length: %zu\r\n\r\n%s",
        status, strlen(body), body);
    return n > 0 ? (size_t)n : 0;
}

static size_t handle(const char *target, char *out, size_t outsz) {
    if (strlen(target) > 128)
        return respond("414 URI Too Long", "target too long\n", out, outsz);
    char body[256];
    snprintf(body, sizeof body, "target is %zu bytes\n", strlen(target));
    return respond("200 OK", body, out, outsz);
}

int main(void) {
    char long_target[131];
    memset(long_target, 'a', 130);
    long_target[130] = '\0';

    char short_target[129];
    memset(short_target, 'a', 128);
    short_target[128] = '\0';

    char out[512];
    handle(short_target, out, sizeof out);
    printf("128 chars -> %.*s", (int)strcspn(out, "\r"), out);
    printf("  (status line above)\n");
    handle(long_target, out, sizeof out);
    printf("130 chars -> %.*s\n", (int)strcspn(out, "\r"), out);
    return 0;
}
```

```text
128 chars -> HTTP/1.1 200 OK  (status line above)
130 chars -> HTTP/1.1 414 URI Too Long
```

The boundary is `> 128`, so exactly 128 is accepted and 129 is not. Testing the value on each side of
a limit rather than only a value far from it is what catches off-by-one errors.

:::

:::solution Exercise 4

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    /* A body that contains a NUL byte in the middle. */
    const char body[] = { 'A', 'B', '\0', 'C', 'D' };
    size_t real_length = sizeof body;

    printf("sizeof body        = %zu\n", real_length);
    printf("strlen(body)       = %zu   <- stops at the NUL\n", strlen(body));
    printf("Content-Length must be %zu, not %zu\n", real_length, strlen(body));
    return 0;
}
```

```text
sizeof body        = 5
strlen(body)       = 2   <- stops at the NUL
Content-Length must be 5, not 2
```

`strlen` counts up to the first NUL byte, which is correct for a C string and wrong for a file. A PNG
almost always contains NUL bytes in its first few dozen bytes, so a server that computes
`Content-Length` with `strlen` truncates every image it serves and looks fine for text. This is the
same lesson as the `read_file` function: **the body is bytes, and its length is tracked separately
from its contents.**

:::

:::solution Exercise 5

```c run
#include <stdio.h>
#include <string.h>

static int headers_complete(const char *buf) {
    return strstr(buf, "\r\n\r\n") != NULL;
}

int main(void) {
    const char *cases[] = {
        "GET / HTTP/1.1\r\n",
        "GET / HTTP/1.1\r\nHost: x\r\n",
        "GET / HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET / HTTP/1.1\nHost: x\n\n",
    };
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        char printable[64];
        snprintf(printable, sizeof printable, "%s", cases[i]);
        /* Make the invisible bytes visible: R is \r, N is \n. */
        for (char *p = printable; *p; p++) {
            if (*p == '\r')      { *p = 'R'; }
            else if (*p == '\n') { *p = 'N'; }
        }
        printf("%-32s complete? %s\n", printable, headers_complete(cases[i]) ? "yes" : "no");
    }
    return 0;
}
```

```text
GET / HTTP/1.1RN                 complete? no
GET / HTTP/1.1RNHost: xRN        complete? no
GET / HTTP/1.1RNHost: xRNRN      complete? yes
GET / HTTP/1.1NHost: xNN         complete? no
```

The `R` and `N` are the carriage return and line feed printed as letters, so you can see where the
line breaks actually are. The first three cases end their lines with a proper `\r\n`, which prints as
`RN`; the fourth ends them with a bare `\n`, which prints as a single `N`.

That fourth case is the interesting one. Its lines end with a bare `\n`, which is what you get from a
text editor on Unix and from many hand-written test clients. The header block is over, but it is not
over in the way HTTP defines, so `strstr(buf, "\r\n\r\n")` correctly says no. A real server has to
decide what to do about that: the common choice is to answer `400` and be strict, because accepting
both forms makes it possible to smuggle a request past a proxy that only looks for one of them.

:::

:::solution Exercise 6

The parse and resolve layers take a string and return a value or a decision, so a test is an ordinary
function call with a chosen input and an asserted output — no socket, no client, no timing.

The send layer's correctness depends on the operating system: a `write` may accept only part of the
buffer, a peer may disappear mid-write, and the number of bytes delivered is not the number you asked
for. Its failures only appear under conditions you cannot create by calling a function, so it has to
be tested by actually connecting a client and reading what comes back.

:::
