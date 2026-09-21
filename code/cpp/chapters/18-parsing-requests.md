---
chapter: 18
part: 3
title: Parsing Requests Safely
summary: Split a request line into its three fields without corrupting the buffer, decode percent-escapes, and turn an attacker-chosen target into a file path that cannot leave the document root.
minutes: 70
tags: [parsing, sscanf, strtok, percent-encoding, path-traversal, security, validation]
---

The request line looks like three harmless words separated by spaces, and treating it that way is how
servers get broken into. Everything in that line was chosen by whoever connected to your port, so the
parser's job is not to understand the request but to **reject** everything it cannot prove safe. This
chapter builds the two functions that decide that — one that splits the line, and one that turns a
target like `/a/../b` into a real file path while guaranteeing the result stays inside the directory
you meant to serve. Both are pure functions, so both can be tested by calling them.

## Splitting the request line

The request line has exactly three fields: method, target, version. `sscanf` reads them, and the
field widths are what make it safe:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *request = "GET /a/b.html HTTP/1.1\r\nHost: x\r\n\r\n";

    /* Copy just the request line out, so the parser cannot damage the original. */
    size_t line_len = (size_t)(strstr(request, "\r\n") - request);
    char line[256];
    memcpy(line, request, line_len);
    line[line_len] = '\0';
    printf("request line: [%s] (%zu bytes)\n", line, line_len);

    char method[16], target[128], version[16];
    int fields = sscanf(line, "%15s %127s %15s", method, target, version);
    printf("fields read : %d\n", fields);
    printf("method      : [%s]\n", method);
    printf("target      : [%s]\n", target);
    printf("version     : [%s]\n", version);

    /* A request line with only two fields. */
    const char *broken = "GET /only-two";
    fields = sscanf(broken, "%15s %127s %15s", method, target, version);
    printf("broken line : %d field(s) read -> reject\n", fields);
    return 0;
}
```

```text
request line: [GET /a/b.html HTTP/1.1] (22 bytes)
fields read : 3
method      : [GET]
target      : [/a/b.html]
version     : [HTTP/1.1]
broken line : 2 field(s) read -> reject
```

Three decisions are visible in that code.

**`%15s` into `char method[16]`.** The width is one less than the array because `%s` writes a
terminating NUL after the characters. Get this wrong in the other direction — `%s` with no width at
all — and a client sending a 5000-character method writes 5000 bytes into a 16-byte local array. That
is a stack buffer overflow reachable from the network, and it is the single most common serious bug in
hand-written C servers.

**`sscanf` returns the number of fields it converted**, and the return value is checked against 3.
A line with two fields leaves `version` holding whatever was in it before — stale data from the
previous request, if the buffers are reused across the accept loop. Reading an uninitialised local is
undefined behaviour, and in a server it is also a way to leak memory contents to a client. Reject the
request; do not guess the missing field.

**The request line is copied before it is parsed.** `sscanf` does not modify its input, but the next
section shows what happens when you reach for a function that does.

### Two ways a target buffer goes wrong

The target is copied into a fixed buffer, and both ways of getting that wrong are visible at build
time. The first is asking for too little room:

```c warn
#include <stdio.h>

int main(void) {
    char target[8] = "/index.html";
    printf("%s\n", target);
    return 0;
}
```

```text
initializer-string for char array is too long
```

The literal is 12 bytes including its NUL and the array holds 8, so clang keeps 7 characters plus the
NUL and discards the rest. It is a warning rather than an error because C has always allowed an
over-long initialiser to be truncated — which is exactly what makes it dangerous: the program
compiles, runs, and serves `/index.h`. Sizing a target buffer is a decision about how much of a URL
you are willing to accept, and the compiler will not make that decision for you. Pick a size, and
answer `414` above it.

The second mistake is trying to assign to the array instead of copying into it:

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

An array is not a pointer and it is not a value you can assign. `full = target` is not a copy in any
language whose arrays are value types, and in C it is not even legal syntax. The copy is
`memcpy(full, target, len)` or `snprintf(full, sizeof full, "%s", target)`, and both need the length —
which is the whole reason the resolver in this chapter tracks `len` explicitly instead of calling
`strlen` after every step.

## Why not `strtok`

`strtok` looks like the natural tool and is the wrong one. It does not return pieces of your string —
it *rewrites* your string, replacing each separator with a NUL byte and returning pointers into the
modified buffer:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    char line[] = "GET /a/b.html HTTP/1.1";
    char *save = NULL;
    char *method = strtok_r(line, " ", &save);
    char *target = strtok_r(NULL, " ", &save);
    printf("method = %s\n", method);
    printf("target = %s\n", target);
    printf("line is now %zu bytes, but was %zu\n", strlen(line), (size_t)22);
    printf("bytes of line:");
    for (size_t i = 0; i < 23; i++) printf(" %02x", (unsigned char)line[i]);
    putchar('\n');
    return 0;
}
```

```text
method = GET
target = /a/b.html
line is now 3 bytes, but was 22
bytes of line: 47 45 54 00 2f 61 2f 62 2e 68 74 6d 6c 00 48 54 54 50 2f 31 2e 31 00
```

Read the hex. The original bytes `47 45 54` are `GET`, then the space has become `00`, then the
target, then another `00` where the second space was. `strlen(line)` now reports 3 because the string
ends at the first NUL that `strtok_r` wrote. The 22-byte request line is still there in memory, but it
is no longer a string.

That matters for two reasons. A server wants to log the request line as it arrived — after `strtok`
the original is gone. And a second parse of the same buffer sees a truncated line, which is how a
request can be validated one way and interpreted another.

Use `strtok_r` rather than `strtok` if you must use it at all: `strtok` keeps its position in a
hidden global, so it is not reentrant and cannot be used from two threads. Better still, copy the
field you want and leave the original alone, which is what `sscanf` into separate buffers does.

## Percent-encoding

A URL cannot contain a space or a `?`, so those bytes are written as `%` followed by two hexadecimal
digits: `%20` is a space, `%2F` is `/`, `%2E` is `.`. Decoding happens **before** any path decision,
because a client that writes `%2e%2e` is asking for `..` and the difference is only spelling:

```c run
#include <stdio.h>
#include <string.h>

#define DECODE_BAD_ESCAPE  (-1)
#define DECODE_ENCODED_NUL (-2)

static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Decode `in` into `out`. Returns the length, or a negative reason code. */
static int percent_decode(const char *in, char *out, size_t outsz) {
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0'; i++) {
        int c = (unsigned char)in[i];
        if (c == '%') {
            int hi = hex_value(in[i + 1]);
            int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return DECODE_BAD_ESCAPE;
            c = hi * 16 + lo;
            if (c == 0) return DECODE_ENCODED_NUL;
            i += 2;
        }
        if (j + 1 >= outsz) return DECODE_BAD_ESCAPE;
        out[j++] = (char)c;
    }
    out[j] = '\0';
    return (int)j;
}

int main(void) {
    const char *cases[] = { "hello%20world", "a%2Fb", "%2e%2e", "%zz", "a%00b", "plain" };
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        char out[128];
        int n = percent_decode(cases[i], out, sizeof out);
        if (n == DECODE_BAD_ESCAPE)       printf("%-14s -> 400 (bad escape)\n", cases[i]);
        else if (n == DECODE_ENCODED_NUL) printf("%-14s -> 400 (encoded NUL)\n", cases[i]);
        else                              printf("%-14s -> [%s]\n", cases[i], out);
    }
    return 0;
}
```

```text
hello%20world  -> [hello world]
a%2Fb          -> [a/b]
%2e%2e         -> [..]
%zz            -> 400 (bad escape)
a%00b          -> 400 (encoded NUL)
plain          -> [plain]
```

Two of those refusals are security decisions, not error handling.

`%zz` is a malformed escape: `z` is not a hexadecimal digit. A decoder that silently passes through
an unrecognised escape produces a different string from the one the client intended, and that gap
between what the client sent and what the server understood is exactly where request-smuggling bugs
live. Refuse it.

`a%00b` decodes to `a`, NUL, `b`. Every C string function stops at that NUL, so the path the server
validates (`a`) and the path it opens (`a`) agree — but a *different* layer that does not stop at NUL
would see `a\0b`. Rejecting encoded NULs outright removes the whole class. Note that the decoder
never trusts `in[i + 1]` and `in[i + 2]` to exist: `hex_value` is called on whatever byte is there,
and the terminator is not a hex digit, so a truncated `%2` at the end of the string is caught by the
same check as `%zz`.

## The path is not a filename

Here is the attack, in one line. The server is told to serve files from `/srv/www`. A client asks for
`/../../etc/passwd`. If the server builds the path by concatenation, it opens `/srv/www/../../etc/passwd`,
which the kernel happily resolves to `/etc/passwd`. The client has just read a file the server was
never meant to expose, using nothing but `..`.

Refusing any target containing `..` is the tempting fix and it is wrong twice over. It misses `%2e%2e`
if decoding happens later, and it refuses `report..txt`, which is a perfectly ordinary filename. The
correct approach is to stop thinking of the target as a string and start thinking of it as a **path**
— a sequence of segments — and to enforce the rule segment by segment.

The rule is a single invariant: **the resolved path must have the document root as a prefix, and the
counter never goes below zero.** Walking the segments left to right with a depth counter enforces it:

- `.` contributes nothing.
- `..` removes the most recently accepted segment. If there is nothing left to remove — that is, if
  the path is already back at the root — the request is refused.
- anything else is appended.

```c run
#include <stdio.h>
#include <string.h>

#define DECODE_BAD_ESCAPE  (-1)
#define DECODE_ENCODED_NUL (-2)

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
            int hi = hex_value(in[i + 1]);
            int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return DECODE_BAD_ESCAPE;
            c = hi * 16 + lo;
            if (c == 0) return DECODE_ENCODED_NUL;
            i += 2;
        }
        if (j + 1 >= outsz) return DECODE_BAD_ESCAPE;
        out[j++] = (char)c;
    }
    out[j] = '\0';
    return (int)j;
}

/* Join `root` and an already-decoded target, refusing anything that leaves the root. */
static int resolve_path(const char *root, const char *target, char *out, size_t outsz) {
    if (target[0] != '/') return -1;
    int n = snprintf(out, outsz, "%s", root);
    if (n < 0 || (size_t)n >= outsz) return -1;
    size_t len = (size_t)n, rootlen = len;

    const char *p = target;
    while (*p != '\0') {
        while (*p == '/') p++;                     /* collapse repeated slashes */
        if (*p == '\0') break;

        const char *seg = p;
        while (*p != '\0' && *p != '/') p++;
        size_t seglen = (size_t)(p - seg);

        if (seglen == 1 && seg[0] == '.') continue;
        if (seglen == 2 && seg[0] == '.' && seg[1] == '.') {
            if (len <= rootlen) return -1;         /* nothing left to remove */
            while (len > 0 && out[len - 1] != '/') len--;
            if (len > 0) len--;                    /* drop the '/' as well */
            out[len] = '\0';
            continue;
        }
        if (len + 1 + seglen + 1 > outsz) return -1;
        out[len++] = '/';
        memcpy(out + len, seg, seglen);
        len += seglen;
        out[len] = '\0';
    }

    if (len == rootlen) {                          /* "/" or "/a/.." lands on the index */
        static const char index[] = "/index.html";
        if (len + sizeof index > outsz) return -1;
        memcpy(out + len, index, sizeof index);
    }
    return 0;
}

static void show(const char *target) {
    char decoded[512], full[512];
    int d = percent_decode(target, decoded, sizeof decoded);
    if (d == DECODE_BAD_ESCAPE)    { printf("%-32s -> 400 (bad escape)\n", target); return; }
    if (d == DECODE_ENCODED_NUL)   { printf("%-32s -> 400 (encoded NUL)\n", target); return; }
    if (resolve_path("/srv/www", decoded, full, sizeof full) < 0) {
        printf("%-32s -> 403 (escapes the root)\n", target);
        return;
    }
    printf("%-32s -> %s\n", target, full);
}

int main(void) {
    show("/");
    show("/index.html");
    show("/a/b.txt");
    show("/a/./b.txt");
    show("//a///b.txt");
    show("/a/../b.txt");
    show("/a/..");
    show("/../etc/passwd");
    show("/a/../../etc/passwd");
    show("/%2e%2e/secret");
    show("/%2E%2E%2F%2E%2E%2Fetc%2Fpasswd");
    show("/a%00b");
    show("/%zz");
    show("index.html");
    return 0;
}
```

```text
/                                -> /srv/www/index.html
/index.html                      -> /srv/www/index.html
/a/b.txt                         -> /srv/www/a/b.txt
/a/./b.txt                       -> /srv/www/a/b.txt
//a///b.txt                      -> /srv/www/a/b.txt
/a/../b.txt                      -> /srv/www/b.txt
/a/..                            -> /srv/www/index.html
/../etc/passwd                   -> 403 (escapes the root)
/a/../../etc/passwd              -> 403 (escapes the root)
/%2e%2e/secret                   -> 403 (escapes the root)
/%2E%2E%2F%2E%2E%2Fetc%2Fpasswd  -> 403 (escapes the root)
/a%00b                           -> 400 (encoded NUL)
/%zz                             -> 400 (bad escape)
index.html                       -> 403 (escapes the root)
```

Every line in that table is a decision, and the interesting ones are the last seven.

`/a/../b.txt` resolves to `/srv/www/b.txt`. Traversal that stays inside the root is *legal* and must
be allowed — a client is entitled to write a relative path, and refusing every `..` would break real
clients. What is forbidden is *leaving* the root, and that is precisely what the depth counter
measures. `/../etc/passwd` tries to pop the root itself and is refused. `/a/../../etc/passwd` climbs
out by two steps and is refused at the second.

`/%2E%2E%2F%2E%2E%2Fetc%2Fpasswd` is the whole attack written in escapes. It is refused for exactly
the same reason as the plain-text version, because decoding happens first. That ordering is not a
detail: decode after resolving and this line becomes a valid read of `/etc/passwd`.

`index.html` has no leading slash, so it is refused. A target always begins with `/`; a relative one
is not a request the server can interpret, and guessing what it meant is how you get a second path
grammar that disagrees with the first.

Note also what the function refuses to do: it never calls `realpath`, never follows a symlink, and
never touches the filesystem at all. It is a pure string function, so all fourteen lines above are
unit tests that run in microseconds. The one thing it cannot defend against is a symlink *inside* the
root that points outside it — that is a filesystem property, and the defence is to not create one.

:::scenario The directory listing that served the deploy keys

A team ships an internal tool that serves build artifacts from `/var/artifacts`. It has no index, so
it answers `404` for `/` and everyone uses it by typing full paths. Six months later an external
penetration test reports that `GET /../../etc/shadow` returns the file, and worse,
`GET /../deploy/keys/id_rsa` returns a private key, because the artifacts directory sits next to a
deploy directory.

The code was:

```c run
#include <stdio.h>
#include <string.h>

/* The bug, reproduced without a filesystem. */
static void naive(const char *root, const char *target) {
    char full[512];
    snprintf(full, sizeof full, "%s%s", root, target);
    printf("GET %-24s -> opens %s\n", target, full);
}

int main(void) {
    naive("/var/artifacts", "/build-41.tar.gz");
    naive("/var/artifacts", "/../../etc/shadow");
    naive("/var/artifacts", "/../deploy/keys/id_rsa");
    return 0;
}
```

```text
GET /build-41.tar.gz         -> opens /var/artifacts/build-41.tar.gz
GET /../../etc/shadow        -> opens /var/artifacts/../../etc/shadow
GET /../deploy/keys/id_rsa   -> opens /var/artifacts/../deploy/keys/id_rsa
```

`snprintf` did its job perfectly — it produced exactly the string it was asked for. The bug is that
nobody asked what that string resolves to. The second and third lines are not paths under
`/var/artifacts`; the kernel will follow the `..` segments and hand over `/etc/shadow` and the key.
The formatter was never the problem, which is why code review did not catch it.

:::solution Resolve, then decide

Replace the concatenation with `resolve_path` from this chapter, and make the refusal visible:

```c run
#include <stdio.h>
#include <string.h>

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

static void attempt(const char *target) {
    char full[512];
    if (resolve_path("/var/artifacts", target, full, sizeof full) < 0) {
        printf("GET %-24s -> 403 Forbidden\n", target);
        return;
    }
    printf("GET %-24s -> opens %s\n", target, full);
}

int main(void) {
    attempt("/build-41.tar.gz");
    attempt("/../../etc/shadow");
    attempt("/../deploy/keys/id_rsa");
    attempt("/v2/../build-41.tar.gz");
    return 0;
}
```

```text
GET /build-41.tar.gz         -> opens /var/artifacts/build-41.tar.gz
GET /../../etc/shadow        -> 403 Forbidden
GET /../deploy/keys/id_rsa   -> 403 Forbidden
GET /v2/../build-41.tar.gz   -> opens /var/artifacts/build-41.tar.gz
```

The last line matters as much as the refusals. A client using `..` to navigate *within* the served
tree still works, so the fix does not break legitimate users — which is the difference between a
security fix that ships and one that gets reverted a week later.

:::

:::pitfall Checking for ".." with strstr

The obvious-looking validation is a substring search, and it fails in both directions:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *targets[] = {
        "/a/../b.txt",
        "/report..txt",
        "/%2e%2e/etc/passwd",
    };
    for (size_t i = 0; i < sizeof targets / sizeof targets[0]; i++) {
        int rejected = strstr(targets[i], "..") != NULL;
        printf("%-20s strstr says %-6s\n", targets[i], rejected ? "REJECT" : "allow");
    }
    return 0;
}
```

```text
/a/../b.txt          strstr says REJECT
/report..txt         strstr says REJECT
/%2e%2e/etc/passwd   strstr says allow
```

**All three verdicts are wrong**, and they are wrong in both directions.

`/a/../b.txt` is a legitimate request that stays inside the root, and the check rejects it. That is
the false positive that makes people disable the check after a bug report.

`/report..txt` is an ordinary filename that happens to contain two adjacent dots, and it is rejected
too. `strstr` cannot tell it apart from traversal, because it is not looking at path structure at all
— it is looking for two characters.

`/%2e%2e/etc/passwd` is the real attack and it sails through, because at the moment of the check the
string does not contain two literal dots. It contains `%2e%2e`. Decode it later and it becomes `..`.

So the check is simultaneously too strict for two legitimate inputs and too permissive for the one
input that matters. That is the signature of a validator written against the wrong representation.

The lesson generalises: **a security check written against the un-normalised form of a string is
guaranteed to be wrong.** Normalise first — decode, then resolve — and check the *result*, which is
the one thing you can actually make a statement about. `strstr` is not a validator.

:::

## Key takeaways

- `sscanf` field widths are mandatory, not optional: `%15s` into `char method[16]`. Without a width,
  remote input overflows a local array.
- Check `sscanf`'s return value against the number of fields you asked for. A missing field leaves a
  buffer holding stale data from the previous request.
- Copy the request line before parsing it. `strtok`/`strtok_r` rewrite the buffer, replacing
  separators with NUL bytes, so the original request line is destroyed.
- `strtok` is not reentrant — it keeps state in a global. `strtok_r` takes an explicit cursor.
- Percent-decode **before** any path decision. `%2e%2e` and `..` must reach the resolver as the same
  string, or the check and the file open disagree.
- Reject malformed escapes and encoded NULs. Both create a gap between what the client sent and what
  the server understood.
- Do not concatenate a target onto a root. Walk the segments with a depth counter that may never go
  below zero, so the root stays a prefix of the result.
- Traversal that stays inside the root is legal and must be allowed; only leaving the root is
  forbidden.
- Never validate with `strstr(target, "..")`. It rejects valid paths and accepts encoded attacks.
- A pure resolver can be tested in microseconds. Keep the filesystem out of it.

## Practice

- [ ] Write `static int split_request_line(const char *line, char *method, size_t msz, char *target,
      size_t tsz, char *version, size_t vsz)` that returns the number of fields read, and test it on
      a complete line, a two-field line, and an empty string.
- [ ] Write `static int percent_decode` that additionally refuses a `%` appearing in the last two
      bytes of the string, and show the difference from the version in this chapter.
- [ ] Extend `resolve_path` to reject any segment beginning with a dot that is not exactly `.` or
      `..`, so `/a/.hidden` is refused. Explain why a real static server might not want that.
- [ ] Write `static int is_under_root(const char *root, const char *resolved)` that checks the root
      is a prefix **and** that the next character is a `/` or the end of the string. Test it on
      `/srv/www` against `/srv/www/a`, `/srv/wwwx/a` and `/srv/www`.
- [ ] Write a program that prints the decision for twenty targets of your own choosing, including at
      least three you expect to be refused, and confirm each verdict.
- [ ] Explain in two sentences why decoding after resolving turns `/%2e%2e/etc/passwd` into a read of
      `/etc/passwd`.

## Solutions

:::solution Exercise 1

```c run
#include <stdio.h>
#include <string.h>

static int split_request_line(const char *line, char *method, size_t msz,
                              char *target, size_t tsz,
                              char *version, size_t vsz) {
    char fmt[64];
    snprintf(fmt, sizeof fmt, "%%%zus %%%zus %%%zus", msz - 1, tsz - 1, vsz - 1);
    return sscanf(line, fmt, method, target, version);
}

static void check(const char *line) {
    char method[16], target[128], version[16];
    method[0] = target[0] = version[0] = '\0';
    int n = split_request_line(line, method, sizeof method,
                                     target, sizeof target,
                                     version, sizeof version);
    printf("[%s] -> %d field(s)", line, n);
    if (n >= 1) printf(" method=[%s]", method);
    if (n >= 2) printf(" target=[%s]", target);
    if (n >= 3) printf(" version=[%s]", version);
    putchar('\n');
}

int main(void) {
    check("GET /a/b.html HTTP/1.1");
    check("GET /only-two");
    check("");
    return 0;
}
```

```text
[GET /a/b.html HTTP/1.1] -> 3 field(s) method=[GET] target=[/a/b.html] version=[HTTP/1.1]
[GET /only-two] -> 2 field(s) method=[GET] target=[/only-two]
[] -> -1 field(s)
```

Building the format string from the caller's buffer sizes is the difference between a helper that is
safe for any caller and one that is only safe for the sizes the author happened to test. `msz - 1` is
the width, because `%s` needs room for the NUL.

The empty string produces `-1`, not `0`. `sscanf` returns `EOF` when it runs out of input before
converting anything, and `EOF` is `-1` on every implementation that matters. That is a second reason
to compare against the exact number you wanted rather than against a truthy value: `if (n)` would
accept `-1` as success.

:::

:::solution Exercise 2

```c run
#include <stdio.h>

static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Stricter: a '%' must have two hex digits after it. */
static int percent_decode_strict(const char *in, char *out, size_t outsz) {
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0'; i++) {
        int c = (unsigned char)in[i];
        if (c == '%') {
            if (in[i + 1] == '\0' || in[i + 2] == '\0') return -1;
            int hi = hex_value(in[i + 1]);
            int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return -1;
            c = hi * 16 + lo;
            if (c == 0) return -2;
            i += 2;
        }
        if (j + 1 >= outsz) return -1;
        out[j++] = (char)c;
    }
    out[j] = '\0';
    return (int)j;
}

int main(void) {
    const char *cases[] = { "a%20b", "a%2", "a%", "a%zz", "plain" };
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++) {
        char out[64];
        int n = percent_decode_strict(cases[i], out, sizeof out);
        if (n == -1)      printf("%-8s -> 400 (malformed escape)\n", cases[i]);
        else if (n == -2) printf("%-8s -> 400 (encoded NUL)\n", cases[i]);
        else              printf("%-8s -> [%s]\n", cases[i], out);
    }
    return 0;
}
```

```text
a%20b    -> [a b]
a%2      -> 400 (malformed escape)
a%       -> 400 (malformed escape)
a%zz     -> 400 (malformed escape)
plain    -> [plain]
```

The original version was already correct on these inputs, because `hex_value('\0')` returns `-1` and
the terminator fails the same test as `z`. The explicit length check makes that reasoning visible
rather than accidental — and if the buffer were not NUL-terminated, the explicit check is the only
one that works. This is worth noticing: a guard that is redundant *given an invariant* stops being
redundant the moment the invariant is broken elsewhere.

:::

:::solution Exercise 3

```c run
#include <stdio.h>
#include <string.h>

static int resolve_path_strict(const char *root, const char *target,
                               char *out, size_t outsz) {
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
        if (seg[0] == '.') return -1;              /* dot-files are hidden */
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

int main(void) {
    const char *targets[] = { "/a/b.txt", "/a/.hidden", "/.git/config", "/a/../b.txt" };
    for (size_t i = 0; i < sizeof targets / sizeof targets[0]; i++) {
        char full[256];
        if (resolve_path_strict("/srv/www", targets[i], full, sizeof full) < 0)
            printf("%-16s -> 403\n", targets[i]);
        else
            printf("%-16s -> %s\n", targets[i], full);
    }
    return 0;
}
```

```text
/a/b.txt         -> /srv/www/a/b.txt
/a/.hidden       -> 403
/.git/config     -> 403
/a/../b.txt      -> /srv/www/b.txt
```

Refusing dot-files is a policy decision, not a correctness one, and it is worth being explicit about
which you are making. Many static servers *want* to serve `.well-known/`, and a site's own build
output may include dot-directories. Blocking them is a sensible default for a server whose root is a
home directory and a bad one for a server whose root is a published site. The resolver should enforce
the invariant — stay inside the root — and the *policy* about dot-files belongs in a separate,
clearly named check, so the next person can find and change it.

:::

:::solution Exercise 4

```c run
#include <stdio.h>
#include <string.h>

/* True only if `resolved` is `root` itself or a path underneath it. */
static int is_under_root(const char *root, const char *resolved) {
    size_t rlen = strlen(root);
    if (strncmp(root, resolved, rlen) != 0) return 0;
    return resolved[rlen] == '\0' || resolved[rlen] == '/';
}

int main(void) {
    const char *root = "/srv/www";
    const char *cases[] = { "/srv/www/a", "/srv/wwwx/a", "/srv/www", "/srv/ww" };
    for (size_t i = 0; i < sizeof cases / sizeof cases[0]; i++)
        printf("%-14s under %s ? %s\n", cases[i], root,
               is_under_root(root, cases[i]) ? "yes" : "no");
    return 0;
}
```

```text
/srv/www/a     under /srv/www ? yes
/srv/wwwx/a    under /srv/www ? no
/srv/www       under /srv/www ? yes
/srv/ww        under /srv/www ? no
```

The `/srv/wwwx/a` case is the reason this function exists. A plain `strncmp` prefix test says yes,
because `/srv/wwwx` starts with the eight characters `/srv/www` — but `x` is a *sibling* directory,
not a child. Requiring the next character to be `/` or the end of the string is what turns "starts
with" into "is inside". This is the same class of mistake as the `strstr` pitfall, and it is why a
path check should be written as a function with its own tests rather than inlined at the call site.

:::

:::solution Exercise 5

```c run
#include <stdio.h>
#include <string.h>

#define DECODE_BAD_ESCAPE  (-1)
#define DECODE_ENCODED_NUL (-2)

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
            int hi = hex_value(in[i + 1]);
            int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return DECODE_BAD_ESCAPE;
            c = hi * 16 + lo;
            if (c == 0) return DECODE_ENCODED_NUL;
            i += 2;
        }
        if (j + 1 >= outsz) return DECODE_BAD_ESCAPE;
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

static void decide(const char *target) {
    char decoded[256], full[256];
    int d = percent_decode(target, decoded, sizeof decoded);
    if (d == DECODE_BAD_ESCAPE)   { printf("%-28s -> 400 bad escape\n", target); return; }
    if (d == DECODE_ENCODED_NUL)  { printf("%-28s -> 400 encoded NUL\n", target); return; }
    if (resolve_path("/srv/www", decoded, full, sizeof full) < 0) {
        printf("%-28s -> 403\n", target);
        return;
    }
    printf("%-28s -> %s\n", target, full);
}

int main(void) {
    const char *targets[] = {
        "/", "/index.html", "/a.txt", "/dir/file.css", "/a/./b", "/a//b", "/a/b/",
        "/a/../b", "/a/..", "/a/b/../../c", "/..", "/../x", "/../../x",
        "/a/../../x", "/%2e%2e/x", "/%2E%2E%2Fx", "/a%2fb", "/a%00b", "/%2", "/a b",
    };
    for (size_t i = 0; i < sizeof targets / sizeof targets[0]; i++)
        decide(targets[i]);
    return 0;
}
```

```text
/                            -> /srv/www/index.html
/index.html                  -> /srv/www/index.html
/a.txt                       -> /srv/www/a.txt
/dir/file.css                -> /srv/www/dir/file.css
/a/./b                       -> /srv/www/a/b
/a//b                        -> /srv/www/a/b
/a/b/                        -> /srv/www/a/b
/a/../b                      -> /srv/www/b
/a/..                        -> /srv/www/index.html
/a/b/../../c                 -> /srv/www/c
/..                          -> 403
/../x                        -> 403
/../../x                     -> 403
/a/../../x                   -> 403
/%2e%2e/x                    -> 403
/%2E%2E%2Fx                  -> 403
/a%2fb                       -> /srv/www/a/b
/a%00b                       -> 400 encoded NUL
/%2                          -> 400 bad escape
/a b                         -> /srv/www/a b
```

Four cases deserve a second look. `/a/b/` with a trailing slash resolves to `/srv/www/a/b`, because
the loop collapses the trailing separator — the file/directory distinction is made later, by the
`fopen` that either succeeds or does not. `/a/b/../../c` climbs two levels and lands back inside the
root, so it is allowed; the counter never went negative. `/%2E%2E%2Fx` uses uppercase hex digits and
is refused identically, because `hex_value` accepts both cases — a decoder that only handled
lowercase would let the attack through. And `/a%2fb` decodes to `/a/b`, so **an encoded slash is a
separator**. That is correct here, but it is worth knowing that many servers deliberately refuse
`%2F` precisely because it lets a client reach a path that a front-end router did not see as
containing a slash.

:::

:::solution Exercise 6

Decoding after resolving means the resolver examines the string `/%2e%2e/etc/passwd`, in which the
only segment is `%2e%2e` — a single ordinary segment with no dot-dot in it, so the depth counter
stays at one and the request is accepted.

The decoded string `../etc/passwd` is then used as the path, and the kernel resolves `..` for you,
which is the same thing as asking for `/etc/passwd`. The resolver's guarantee was about a string that
was not the string that reached the filesystem.

:::
