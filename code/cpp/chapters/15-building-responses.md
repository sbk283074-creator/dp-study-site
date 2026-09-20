---
chapter: 15
part: 3
title: Building Responses
summary: Turn a resolved path into a complete HTTP response — pick the Content-Type, read the file as bytes rather than a string, size the buffer for headers and body together, and release the body only after it has been sent.
minutes: 65
tags: [http, response, content-length, content-type, mime, file-io, buffer-sizing, free]
---

The resolver from the last chapter hands back a path it has proved is inside the document root. What
is left is to turn that path into bytes a client can parse: a status line, a set of headers, and a
body that is exactly as long as the headers claim. Almost every way this goes wrong produces the same
symptom — the client waits forever — which is why the arithmetic here deserves more care than its
size suggests. The body also has to be read as **bytes**, not as a string, and that distinction is
where the classic image-truncating bug lives.

## A response is a header block plus a body

Every response this server sends has the same skeleton:

```text
HTTP/1.1 <status> \r\n
Content-Type: <type> \r\n
Content-Length: <n> \r\n
Connection: close \r\n
\r\n
<n bytes of body>
```

Four headers, then the blank line, then exactly `n` bytes. `Connection: close` tells the client the
server will hang up when the body is done, which removes any need to parse a `Content-Length` to know
where the message ends — a deliberate simplification for a first server. It costs a TCP connection
per request, which is the right trade for a tool you are learning on and the wrong one for production.

`Content-Length` is the field that matters. It counts the **body** only, it is a byte count and not a
character count, and the client will read exactly that many bytes and no more. Send one byte too few
and the client blocks until it times out. Send one too many and the extra byte becomes the start of a
response the client was not expecting.

## Choosing a Content-Type

Browsers decide how to render a response from its `Content-Type`, not from the file extension, so
guessing this wrong makes a page display as source text or a stylesheet do nothing. A table keyed on
the extension is enough:

```c run
#include <stdio.h>
#include <string.h>

static const char *mime_type(const char *path) {
    const char *dot = strrchr(path, '.');
    if (dot == NULL) return "application/octet-stream";
    if (strcmp(dot, ".html") == 0 || strcmp(dot, ".htm") == 0) return "text/html";
    if (strcmp(dot, ".css")  == 0) return "text/css";
    if (strcmp(dot, ".js")   == 0) return "text/javascript";
    if (strcmp(dot, ".txt")  == 0) return "text/plain";
    if (strcmp(dot, ".png")  == 0) return "image/png";
    if (strcmp(dot, ".json") == 0) return "application/json";
    return "application/octet-stream";
}

int main(void) {
    const char *names[] = { "index.html", "style.css", "app.js", "notes.txt",
                            "data.json", "photo.png", "README", "archive.tar.gz" };
    for (size_t i = 0; i < sizeof names / sizeof names[0]; i++)
        printf("%-16s %s\n", names[i], mime_type(names[i]));
    return 0;
}
```

```text
index.html       text/html
style.css        text/css
app.js           text/javascript
notes.txt        text/plain
data.json        application/json
photo.png        image/png
README           application/octet-stream
archive.tar.gz   application/octet-stream
```

Three details are worth noticing.

**`strrchr`, not `strchr`.** It finds the *last* dot, so `archive.tar.gz` keys on `.gz` rather than
`.tar`. Using `strchr` would classify it by the first dot and get it wrong — and worse, it would
classify a directory like `notes.v2/index.html` by the dot in the *directory* name.

**A file with no dot gets `application/octet-stream`**, which means "some binary data, download it".
That is the safe default: a browser will not try to render it, and it will not execute it. The
dangerous default is `text/html`, because then any file a client can name becomes a script the
browser will run in your origin.

**A short table is a feature.** A server that guesses `text/html` for unknown extensions, or that
tries to sniff content, is a server that can be made to serve user-uploaded bytes as executable
markup. Unknown means download.

## Reading the file as bytes

`fopen`, `fseek` to the end, `ftell`, `rewind`, `malloc`, `fread`. The subtlety is that the length and
the contents are two separate things, and only the length is authoritative:

```c run
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *read_file(const char *path, size_t *len_out) {
    FILE *f = fopen(path, "rb");
    if (f == NULL) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long size = ftell(f);
    if (size < 0) { fclose(f); return NULL; }
    rewind(f);
    char *buf = malloc((size_t)size + 1);
    if (buf == NULL) { fclose(f); return NULL; }
    size_t got = fread(buf, 1, (size_t)size, f);
    fclose(f);
    if (got != (size_t)size) { free(buf); return NULL; }
    buf[got] = '\0';
    *len_out = got;
    return buf;
}

int main(void) {
    /* A file whose contents contain a NUL byte, as any PNG or JPEG will. */
    const char payload[] = { 'A', 'B', 0x00, 'C', 'D' };
    FILE *f = fopen("body.bin", "wb");
    fwrite(payload, 1, sizeof payload, f);
    fclose(f);

    size_t len = 0;
    char *body = read_file("body.bin", &len);
    printf("read %zu bytes, strlen says %zu\n", len, strlen(body));
    printf("bytes:");
    for (size_t i = 0; i < len; i++) printf(" %02x", (unsigned char)body[i]);
    putchar('\n');
    free(body);
    return 0;
}
```

```text
read 5 bytes, strlen says 2
bytes: 41 42 00 43 44
```

`len` is 5 and `strlen(body)` is 2, and the second number is the one that must never reach a
`Content-Length` header. A PNG contains NUL bytes within its first few dozen bytes, so a server that
computes the length with `strlen` sends a truncated image and a header claiming a size it did not
send — which is precisely the mismatch that hangs clients.

The `+ 1` in the `malloc` and the `buf[got] = '\0'` are a convenience, not a requirement. They let
`read_file` return something that can be printed during debugging. The body itself is `len` bytes and
must be treated as such.

Two other details in that function are deliberate. `"rb"` is a binary read: on a system where text
mode translates line endings, a `"r"` read would silently change the byte count and break the
`Content-Length` arithmetic. And the `fread` result is compared against the expected size, so a file
that shrank between the `ftell` and the `fread` is reported as a failure rather than served short.

The path the file is opened with also has to be built, and that is one place where C will not let you
be casual:

```c bad
#include <stdio.h>

static int resolve(const char *target, char *out) {
    char full[256];
    full = target;
    snprintf(out, 256, "%s", full);
    return 0;
}

int main(void) {
    char out[256];
    resolve("/index.html", out);
    printf("%s\n", out);
    return 0;
}
```

```text
array type 'char[256]' is not assignable
```

The path has to be *copied into* the buffer, not assigned to it, and that is why the resolver from
the previous chapter carries `len` around explicitly: it is building the string one segment at a time
and needs to know where the next segment goes.

## Putting the pipeline together

Everything from the last three chapters, in one function. This is `handle` in its final form, minus
the socket:

```c run
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

/* ---------- path layer (from chapter 14) ---------- */
static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}
static int percent_decode(const char *in, char *out, size_t outsz) {
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0'; i++) {
        int c = (unsigned char)in[i];
        if (c == '%') {
            int hi = hex_value(in[i + 1]), lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return -1;
            c = hi * 16 + lo;
            if (c == 0) return -1;
            i += 2;
        }
        if (j + 1 >= outsz) return -1;
        out[j++] = (char)c;
    }
    out[j] = '\0';
    return (int)j;
}
static int resolve_path(const char *root, const char *target, char *out, size_t outsz) {
    if (target[0] != '/') return -1;
    int n = snprintf(out, outsz, "%s", root);
    if (n < 0 || (size_t)n >= outsz) return -1;
    size_t len = (size_t)n, rootlen = len;
    const char *p = target;
    while (*p != '\0') {
        while (*p == '/') p++;
        if (*p == '\0') break;
        const char *seg = p;
        while (*p != '\0' && *p != '/') p++;
        size_t seglen = (size_t)(p - seg);
        if (seglen == 1 && seg[0] == '.') continue;
        if (seglen == 2 && seg[0] == '.' && seg[1] == '.') {
            if (len <= rootlen) return -1;
            while (len > 0 && out[len - 1] != '/') len--;
            if (len > 0) len--;
            out[len] = '\0';
            continue;
        }
        if (len + 1 + seglen + 1 > outsz) return -1;
        out[len++] = '/';
        memcpy(out + len, seg, seglen);
        len += seglen;
        out[len] = '\0';
    }
    if (len == rootlen) {
        static const char index[] = "/index.html";
        if (len + sizeof index > outsz) return -1;
        memcpy(out + len, index, sizeof index);
    }
    return 0;
}

/* ---------- response layer ---------- */
static const char *mime_type(const char *path) {
    const char *dot = strrchr(path, '.');
    if (dot == NULL) return "application/octet-stream";
    if (strcmp(dot, ".html") == 0 || strcmp(dot, ".htm") == 0) return "text/html";
    if (strcmp(dot, ".css")  == 0) return "text/css";
    if (strcmp(dot, ".js")   == 0) return "text/javascript";
    if (strcmp(dot, ".txt")  == 0) return "text/plain";
    if (strcmp(dot, ".png")  == 0) return "image/png";
    if (strcmp(dot, ".json") == 0) return "application/json";
    return "application/octet-stream";
}

static char *read_file(const char *path, size_t *len_out) {
    FILE *f = fopen(path, "rb");
    if (f == NULL) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long size = ftell(f);
    if (size < 0) { fclose(f); return NULL; }
    rewind(f);
    char *buf = malloc((size_t)size + 1);
    if (buf == NULL) { fclose(f); return NULL; }
    size_t got = fread(buf, 1, (size_t)size, f);
    fclose(f);
    if (got != (size_t)size) { free(buf); return NULL; }
    buf[got] = '\0';
    *len_out = got;
    return buf;
}

static size_t build_response(const char *status, const char *type,
                             const char *body, size_t body_len,
                             char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || (size_t)n >= outsz) return 0;
    if ((size_t)n + body_len > outsz) return 0;
    memcpy(out + n, body, body_len);
    return (size_t)n + body_len;
}

static size_t error_page(const char *status, const char *message,
                         char *out, size_t outsz) {
    return build_response(status, "text/plain", message, strlen(message), out, outsz);
}

static size_t handle(const char *root, const char *raw, char *out, size_t outsz) {
    const char *eol = strstr(raw, "\r\n");
    size_t linelen = eol ? (size_t)(eol - raw) : strlen(raw);
    char line[512];
    if (linelen >= sizeof line)
        return error_page("414 URI Too Long", "request line too long\n", out, outsz);
    memcpy(line, raw, linelen);
    line[linelen] = '\0';

    char method[16], target[256], version[16];
    if (sscanf(line, "%15s %255s %15s", method, target, version) != 3)
        return error_page("400 Bad Request", "malformed request line\n", out, outsz);
    if (strcmp(method, "GET") != 0 && strcmp(method, "HEAD") != 0)
        return error_page("405 Method Not Allowed", "only GET and HEAD\n", out, outsz);

    char decoded[512], full[1024];
    if (percent_decode(target, decoded, sizeof decoded) < 0)
        return error_page("400 Bad Request", "bad escape in target\n", out, outsz);
    if (resolve_path(root, decoded, full, sizeof full) < 0)
        return error_page("403 Forbidden", "outside the document root\n", out, outsz);

    size_t len = 0;
    char *body = read_file(full, &len);
    if (body == NULL)
        return error_page("404 Not Found", "no such file\n", out, outsz);

    size_t total = build_response("200 OK", mime_type(full), body, len, out, outsz);
    free(body);
    return total;
}

/* ---------- driver ---------- */
static void make_fixture(const char *root) {
    mkdir(root, 0755);
    char path[512];
    FILE *f;

    snprintf(path, sizeof path, "%s/index.html", root);
    f = fopen(path, "wb");
    fputs("<h1>hello</h1>\n", f);
    fclose(f);

    snprintf(path, sizeof path, "%s/style.css", root);
    f = fopen(path, "wb");
    fputs("body { color: #333; }\n", f);
    fclose(f);
}

static void dump_headers(const char *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (i + 3 < len && data[i] == '\r' && data[i+1] == '\n'
                       && data[i+2] == '\r' && data[i+3] == '\n') {
            printf("\\r\\n\\r\\n<%zu body byte(s)>\n", len - (i + 4));
            return;
        }
        unsigned char c = (unsigned char)data[i];
        if (c == '\r')      fputs("\\r", stdout);
        else if (c == '\n') fputs("\\n\n", stdout);
        else                putchar(c);
    }
}

int main(void) {
    const char *root = "docroot";
    make_fixture(root);

    const char *requests[] = {
        "GET / HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /style.css HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /missing.txt HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /../etc/passwd HTTP/1.1\r\nHost: x\r\n\r\n",
        "POST / HTTP/1.1\r\nHost: x\r\n\r\n",
    };
    for (size_t i = 0; i < sizeof requests / sizeof requests[0]; i++) {
        char out[8192];
        size_t n = handle(root, requests[i], out, sizeof out);
        char label[64];
        snprintf(label, sizeof label, "%.*s", (int)strcspn(requests[i], "\r"), requests[i]);
        printf("%-30s %zu bytes\n", label, n);
        dump_headers(out, n);
    }
    return 0;
}
```

```text
GET / HTTP/1.1                 98 bytes
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 15\r\n
Connection: close\r\n\r\n<15 body byte(s)>
GET /style.css HTTP/1.1        104 bytes
HTTP/1.1 200 OK\r\n
Content-Type: text/css\r\n
Content-Length: 22\r\n
Connection: close\r\n\r\n<22 body byte(s)>
GET /missing.txt HTTP/1.1      104 bytes
HTTP/1.1 404 Not Found\r\n
Content-Type: text/plain\r\n
Content-Length: 13\r\n
Connection: close\r\n\r\n<13 body byte(s)>
GET /../etc/passwd HTTP/1.1    117 bytes
HTTP/1.1 403 Forbidden\r\n
Content-Type: text/plain\r\n
Content-Length: 26\r\n
Connection: close\r\n\r\n<26 body byte(s)>
POST / HTTP/1.1                118 bytes
HTTP/1.1 405 Method Not Allowed\r\n
Content-Type: text/plain\r\n
Content-Length: 18\r\n
Connection: close\r\n\r\n<18 body byte(s)>
```

Five requests, five complete responses, and every one of them is a valid HTTP message. The `200`
lines carry the file's real type and real length; the `404`, `403` and `405` lines carry a short
plain-text explanation. A server that answers every problem with a complete response is a server that
clients can rely on, and that reliability is what makes the error cases worth writing carefully.

## Free the body after you send it

`handle` allocates the body, copies it into the response buffer, and then frees it. The order matters,
and getting it wrong is a bug that only appears under load:

```c run-san-catch
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    char *body = malloc(32);
    if (body == NULL) return 1;
    snprintf(body, 32, "the response body");

    /* ... send the response ... */
    size_t length = strlen(body);
    free(body);

    /* Now log it, out of habit. The bytes are gone. */
    printf("logged %zu bytes: %s\n", length, body);
    return 0;
}
```

```text
heap-use-after-free
```

The `free` is not the bug — freeing early to "save memory" is a reasonable instinct and it is wrong
here, because the response has not been written to the socket yet. The correct order is: read the
body, build the response, **send** the response, then free. In the version above the body is freed
before it is logged, and `printf` reads bytes that the allocator has already reclaimed.

This is why the socket chapter's `serve_one` builds the complete response in a buffer *before* calling
`write`. Once the response is in the buffer, the body allocation is dead and can be released
immediately, and the buffer is what goes on the wire. Keeping the two lifetimes separate — the body's
and the response's — is what makes the ordering easy to get right.

:::pitfall The response that did not fit

`build_response` returns the number of bytes to send, and it returns **0** when the response does not
fit in the caller's buffer. A caller that ignores the return value sends nothing and leaves the client
waiting.

The header block is bigger than it looks, and it grows with the body:

```c run
#include <stdio.h>
#include <string.h>

static size_t build_response(const char *status, const char *type,
                             const char *body, size_t body_len,
                             char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || (size_t)n >= outsz) return 0;
    if ((size_t)n + body_len > outsz) return 0;
    memcpy(out + n, body, body_len);
    return (size_t)n + body_len;
}

int main(void) {
    static char body[9000];
    memset(body, 'x', sizeof body - 1);
    body[sizeof body - 1] = '\0';
    size_t body_len = sizeof body - 1;

    static char scratch[16384];
    size_t headers_empty = build_response("200 OK", "text/html", "", 0, scratch, sizeof scratch);
    size_t whole         = build_response("200 OK", "text/html", body, body_len, scratch, sizeof scratch);
    printf("headers for a 0-byte body : %zu bytes\n", headers_empty);
    printf("headers for this body     : %zu bytes   <- Content-Length itself got longer\n",
           whole - body_len);
    printf("body                      : %zu bytes\n", body_len);

    struct { size_t bufsize; const char *label; } cases[] = {
        { 8192, "out[8192]"  },
        { 4096, "out[4096]"  },
        { 16384, "out[16384]" },
    };
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        static char out[16384];
        size_t total = build_response("200 OK", "text/html", body, body_len,
                                      out, cases[i].bufsize);
        if (total == 0)
            printf("%-10s -> returns 0 (the response did not fit)\n", cases[i].label);
        else
            printf("%-10s -> returns %zu\n", cases[i].label, total);
    }
    return 0;
}
```

```text
headers for a 0-byte body : 82 bytes
headers for this body     : 85 bytes   <- Content-Length itself got longer
body                      : 8999 bytes
out[8192]  -> returns 0 (the response did not fit)
out[4096]  -> returns 0 (the response did not fit)
out[16384] -> returns 9084
```

The first two lines contain a trap that is easy to miss: the header block for a 9000-byte body is
**three bytes longer** than the header block for an empty one, because `Content-Length: 8999` is three
characters longer than `Content-Length: 0`. The header block is not a constant. Any calculation that
assumes it is will be wrong by exactly the number of digits the body length grew by.

The three `out[...]` lines show the failure mode. A 9084-byte response does not fit in 8192 bytes, and
`build_response` correctly reports that by returning 0 — but a caller that writes `build_response(...)`
and passes the result straight to `write` will write zero bytes. The client sees a connection that
opens, accepts the request, and then closes without a response. There is no error message anywhere.

Two fixes, and you want both. Check the return value and answer `500` if it is 0. And size the
response buffer for the largest response you are willing to produce — or, better, do not build the
whole response in one buffer at all. A server that writes the headers first and then streams the body
in fixed-size chunks has no size limit and no arithmetic to get wrong; that is what a real server
does, and it is the natural next step after this project works.

:::

:::scenario The 2 GB file that took the whole machine down

A team adds a `/downloads` directory to a small internal file server. It works perfectly for weeks,
serving reports of a few hundred kilobytes. Then someone drops a 2 GB database dump into the folder,
a colleague clicks it, and the server's memory usage jumps until the machine starts swapping and
every other request times out.

The cause is `read_file`, exactly as written above: it calls `ftell` to learn the size, then
`malloc`s the whole thing. For a 400 KB report that is fine. For 2 GB it is not, and the failure is
not graceful — the process does not get a clean `malloc` failure it can turn into a `500`. On a
machine with overcommit it gets the memory, touches it all through `fread`, and pushes the machine
into swap.

The fix is a size cap, and it belongs at the point where the size becomes known:

```c run
#include <stdio.h>

#define MAX_BODY (8u * 1024u * 1024u)     /* 8 MiB */

static const char *admit(long size) {
    if (size < 0)                       return "500 Internal Server Error";
    if ((unsigned long)size > MAX_BODY) return "413 Payload Too Large";
    return "200 OK";
}

int main(void) {
    long sizes[] = { 0, 4096, 400000, 8 * 1024 * 1024, 8 * 1024 * 1024 + 1, 2147483648L };
    for (size_t i = 0; i < sizeof sizes / sizeof sizes[0]; i++)
        printf("%12ld bytes -> %s\n", sizes[i], admit(sizes[i]));
    return 0;
}
```

```text
           0 bytes -> 200 OK
        4096 bytes -> 200 OK
      400000 bytes -> 200 OK
     8388608 bytes -> 200 OK
     8388609 bytes -> 413 Payload Too Large
  2147483648 bytes -> 413 Payload Too Large
```

Note the boundary: exactly 8 MiB is served, and one byte more is refused. That is the same
test-each-side-of-the-limit discipline as the `414` check on the target length, and it is what stops
the cap from being off by one.

`413` is the correct status — the server is refusing because the *response* would be too large, and
the client should be told why rather than left with a hang. A cap is not a limitation to be
apologised for; it is the thing that keeps the process alive when someone else decides how big a file
is. Every server that reads a whole resource into memory needs one, and the number should be chosen
deliberately rather than inherited from whatever the machine happened to have free.

:::

## Key takeaways

- A response is a status line, four headers, a blank line, and exactly `Content-Length` bytes.
- `Content-Length` counts body bytes only. It is not a character count and it is not the total message
  size.
- The body is bytes, not a string. Use the length returned by `read_file`, never `strlen`, because a
  binary file contains NUL bytes.
- `"rb"` for the read mode. Text mode can translate bytes and change the count.
- `strrchr` for the extension, so `archive.tar.gz` keys on `.gz`. A missing extension gets
  `application/octet-stream`, which is the safe default; never default to `text/html`.
- Read the size with `fseek(SEEK_END)` plus `ftell`, and compare the `fread` result against it.
- `build_response` returns the total byte count, or 0 when the response does not fit. Check for 0 and
  answer `500` — writing zero bytes leaves the client hanging with no diagnostic.
- The header block grows with the body, because `Content-Length`'s own digits are part of it. It is
  not a constant.
- Free the body only after the response has been built. Freeing before sending is a use-after-free.
- Cap the body size. A server that `malloc`s whatever a file's size says is a server one large file
  can take down.

## Practice

- [ ] Write `static const char *mime_type(const char *path)` and test it on `a.HTML`, `a.`, `.hidden`
      and a path with a dot in a directory name. Explain each result.
- [ ] Write `static size_t header_size(const char *status, size_t body_len)` that returns the size of
      the header block without writing it, and show it is three bytes smaller for a 4-digit body than
      for a 6-digit one.
- [ ] Write a `HEAD` handler: same headers as `GET`, including the real `Content-Length`, but no body
      bytes at all. Explain what `Content-Length` must say and why.
- [ ] Write `static int too_big(long size, unsigned long limit)` and test it on `limit - 1`, `limit`
      and `limit + 1`.
- [ ] Change `handle` so a `404` response is generated *without* a body, and explain why a body-less
      `404` still needs a correct `Content-Length: 0`.
- [ ] Write a program that builds a response for a 100-byte body into buffers of 180, 181 and 182
      bytes and prints which ones succeed. Predict the answer before running it.

## Solutions

:::solution Exercise 1

```c run
#include <stdio.h>
#include <string.h>

static const char *mime_type(const char *path) {
    const char *dot = strrchr(path, '.');
    if (dot == NULL) return "application/octet-stream";
    if (strcmp(dot, ".html") == 0 || strcmp(dot, ".htm") == 0) return "text/html";
    if (strcmp(dot, ".css")  == 0) return "text/css";
    if (strcmp(dot, ".js")   == 0) return "text/javascript";
    if (strcmp(dot, ".txt")  == 0) return "text/plain";
    return "application/octet-stream";
}

int main(void) {
    const char *paths[] = { "a.html", "a.HTML", "a.", ".hidden", "dir.v2/index.html", "noext" };
    for (size_t i = 0; i < sizeof paths / sizeof paths[0]; i++)
        printf("%-20s -> %s\n", paths[i], mime_type(paths[i]));
    return 0;
}
```

```text
a.html               -> text/html
a.HTML               -> application/octet-stream
a.                   -> application/octet-stream
.hidden              -> application/octet-stream
dir.v2/index.html    -> text/html
noext                -> application/octet-stream
```

`a.HTML` falls through because the table compares `.html` exactly — MIME types are conventionally
lowercase and extensions on a real filesystem are case-sensitive, so the strict comparison is correct
for a Unix server and wrong for one serving files written on Windows. `a.` has a dot but nothing after
it, so `strcmp` fails and the default applies. `.hidden` has its only dot at position zero, which is
why it is *not* treated as an extension — the code would need an explicit guard to distinguish "no
extension" from "empty extension", and here both land on the safe default. `dir.v2/index.html`
demonstrates why `strrchr` matters: the last dot is in the filename, not the directory, so the answer
is right.

:::

:::solution Exercise 2

```c run
#include <stdio.h>

static size_t header_size(const char *status, size_t body_len) {
    char buf[512];
    int n = snprintf(buf, sizeof buf,
        "HTTP/1.1 %s\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, body_len);
    return n > 0 ? (size_t)n : 0;
}

int main(void) {
    size_t sizes[] = { 0, 9, 10, 99, 100, 999, 1000, 99999, 100000 };
    for (size_t i = 0; i < sizeof sizes / sizeof sizes[0]; i++)
        printf("body %6zu bytes -> headers %zu bytes\n", sizes[i], header_size("200 OK", sizes[i]));
    return 0;
}
```

```text
body      0 bytes -> headers 82 bytes
body      9 bytes -> headers 82 bytes
body     10 bytes -> headers 83 bytes
body     99 bytes -> headers 83 bytes
body    100 bytes -> headers 84 bytes
body    999 bytes -> headers 84 bytes
body   1000 bytes -> headers 85 bytes
body  99999 bytes -> headers 86 bytes
body 100000 bytes -> headers 87 bytes
```

The header block grows by exactly one byte each time `Content-Length` gains a digit, which happens at
10, 100, 1000, 10000 and 100000. This is the reason a response buffer sized as
`body_len + 128` is a reasonable rule of thumb and `body_len + 82` is a bug waiting for a
six-digit body. Computing the header size instead of guessing it removes the question entirely.

:::

:::solution Exercise 3

```c run
#include <stdio.h>
#include <string.h>

static size_t build_response(const char *status, const char *type,
                             const char *body, size_t body_len,
                             int head_only, char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || (size_t)n >= outsz) return 0;
    if (head_only) return (size_t)n;                 /* headers only */
    if ((size_t)n + body_len > outsz) return 0;
    memcpy(out + n, body, body_len);
    return (size_t)n + body_len;
}

int main(void) {
    const char *body = "<h1>hello</h1>\n";
    size_t body_len = strlen(body);
    char out[512];

    size_t get_len  = build_response("200 OK", "text/html", body, body_len, 0, out, sizeof out);
    size_t head_len = build_response("200 OK", "text/html", body, body_len, 1, out, sizeof out);

    printf("GET  -> %zu bytes on the wire\n", get_len);
    printf("HEAD -> %zu bytes on the wire\n", head_len);
    printf("both advertise Content-Length: %zu\n", body_len);
    return 0;
}
```

```text
GET  -> 98 bytes on the wire
HEAD -> 83 bytes on the wire
both advertise Content-Length: 15
```

A `HEAD` response carries the same headers as the `GET` would — including the real body length — but
no body bytes. The client is asking "how big would this be and what type is it", so
`Content-Length` must be the length the body *would* have had, not 0. Getting this wrong breaks every
download manager and link checker that uses `HEAD` to decide whether to fetch something.

:::

:::solution Exercise 4

```c run
#include <stdio.h>

#define MAX_BODY (8u * 1024u * 1024u)

static int too_big(long size, unsigned long limit) {
    if (size < 0) return 1;
    return (unsigned long)size > limit;
}

int main(void) {
    unsigned long limit = MAX_BODY;
    long cases[] = { (long)limit - 1, (long)limit, (long)limit + 1 };
    const char *labels[] = { "limit - 1", "limit", "limit + 1" };
    for (size_t i = 0; i < 3; i++)
        printf("%-10s (%ld) -> %s\n", labels[i], cases[i],
               too_big(cases[i], limit) ? "refuse" : "serve");
    printf("negative  (-1) -> %s\n", too_big(-1, limit) ? "refuse" : "serve");
    return 0;
}
```

```text
limit - 1  (8388607) -> serve
limit      (8388608) -> serve
limit + 1  (8388609) -> refuse
negative  (-1) -> refuse
```

Note the boundary. `limit` itself is **served**, because the test is `> limit`. Writing `>=` would
refuse a file of exactly the limit, which is the kind of off-by-one that is invisible when you read
the code and obvious the moment you print both sides of the boundary. That is the whole reason this
exercise asks for three cases rather than one.

The negative case is refused explicitly because `long` is signed: a `-1` cast to `unsigned long`
becomes the largest value that type can hold, which would pass a naive `size > limit` test and then be
handed to `malloc` as a size. Any function that takes a size from the outside needs a signedness check
before it does anything else.

:::

:::solution Exercise 5

```c run
#include <stdio.h>
#include <string.h>

static size_t build_response(const char *status, const char *type,
                             const char *body, size_t body_len,
                             char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || (size_t)n >= outsz) return 0;
    if ((size_t)n + body_len > outsz) return 0;
    memcpy(out + n, body, body_len);
    return (size_t)n + body_len;
}

int main(void) {
    char out[512];
    size_t n = build_response("404 Not Found", "text/plain", "", 0, out, sizeof out);
    printf("%zu bytes, Content-Length: 0\n", n);
    printf("the blank line is still there:\n");
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)out[i];
        if (c == '\r')      fputs("\\r", stdout);
        else if (c == '\n') fputs("\\n\n", stdout);
        else                putchar(c);
    }
    return 0;
}
```

```text
90 bytes, Content-Length: 0
the blank line is still there:
HTTP/1.1 404 Not Found\r\n
Content-Type: text/plain\r\n
Content-Length: 0\r\n
Connection: close\r\n
\r\n
```

A body-less response still needs `Content-Length: 0`, because the header block has to end with the
blank line regardless of whether a body follows. Omitting the header entirely is also legal in HTTP —
its absence is defined to mean zero — but writing it explicitly means the client never has to apply
that rule, and a response that is obvious to a human reading a packet capture is worth one extra
header line.

:::

:::solution Exercise 6

```c run
#include <stdio.h>
#include <string.h>

static size_t build_response(const char *status, const char *type,
                             const char *body, size_t body_len,
                             char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || (size_t)n >= outsz) return 0;
    if ((size_t)n + body_len > outsz) return 0;
    memcpy(out + n, body, body_len);
    return (size_t)n + body_len;
}

int main(void) {
    char body[101];
    memset(body, 'y', 100);
    body[100] = '\0';
    size_t body_len = 100;

    size_t buffers[] = { 180, 181, 182, 183, 184, 185, 186 };
    for (size_t i = 0; i < sizeof buffers / sizeof buffers[0]; i++) {
        static char out[256];
        size_t total = build_response("200 OK", "text/html", body, body_len, out, buffers[i]);
        printf("out[%3zu] -> %s\n", buffers[i],
               total == 0 ? "returns 0" : "fits");
    }
    return 0;
}
```

```text
out[180] -> returns 0
out[181] -> returns 0
out[182] -> returns 0
out[183] -> returns 0
out[184] -> fits
out[185] -> fits
out[186] -> fits
```

The response is 184 bytes: an 84-byte header block plus 100 body bytes. Every buffer below 184
returns 0, and 184 itself fits exactly.

If you predicted 182 — body plus the 82-byte header you measured earlier — that is exactly the trap
from the pitfall. The header grew by two bytes, because `Content-Length: 100` has three digits where
`Content-Length: 0` has one. The safe habit is to compute the requirement rather than remember it:
`header_size("200 OK", body_len) + body_len`, which is what this exercise is really teaching.

:::
