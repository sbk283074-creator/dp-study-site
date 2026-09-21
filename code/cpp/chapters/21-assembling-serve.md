---
chapter: 21
part: 3
title: Assembling serve
summary: Split the project into headers and translation units, write a Makefile that rebuilds only what changed, drive the finished server with curl, and work through a hardening checklist before calling it done.
minutes: 70
tags: [makefile, make, headers, separate-compilation, linking, curl, project, hardening]
---

Everything in this part works as one file, and one file stops working somewhere around a thousand
lines. This chapter splits it into the shape a real C project has: a header per layer, a source file
per header, and a `main` that wires them together. The payoff is not tidiness — it is that a change to
the MIME table recompiles one object file instead of the whole program, and that each layer can be
read on its own. The cost is a set of rules about declarations and definitions, and a build recipe
that has to be right for the linker to see your work at all.

## Splitting the program

The four layers from the last chapter become four pairs of files, plus an entry point and a test:

| File | What it owns |
|---|---|
| `path.h` / `path.c` | `percent_decode`, `resolve_path` — turning a target into a safe filesystem path |
| `http.h` / `http.c` | `mime_type`, `read_file`, `build_response`, `error_page`, `handle` |
| `server.h` / `server.c` | `start_listening`, `serve_one`, `serve_loop` — the socket layer |
| `selftest.h` / `selftest.c` | `run_self_test` — starts a server in a child and drives it |
| `main.c` | argument parsing and dispatch |
| `Makefile` | how to build all of it |

The boundaries are chosen so that each header exposes only what the layer above needs. `server.c`
includes `http.h` because `serve_one` calls `handle`; `http.c` includes `path.h` because `handle`
calls `resolve_path`; nothing includes `selftest.h` except `main.c`. That gives a dependency order —
`path` before `http` before `server` — and the Makefile encodes it so a change rebuilds in the right
order.

Two functions are deliberately **not** in a header: `read_request` and `send_all` inside `server.c`
are `static`, because nothing outside that file should call them. `static` at file scope gives a
function internal linkage, so its name never reaches the linker's symbol table. That is not just
tidiness — it is what lets a second file define its own `send_all` without a `duplicate symbol` error,
and it means the compiler can see every caller of the function when deciding whether to inline it.

## What goes in a header

A header holds **declarations** and the things a caller cannot compile without. Concretely:

- Function prototypes, with parameter names where they help a reader.
- Types the prototypes need — a `struct`, a `typedef`, an enum.
- Macros the caller must use, like `MAX_BODY_BYTES`.
- Nothing that allocates storage or runs code.

That last rule is the one that bites. A header included by several translation units is *textually
inserted* into each of them, so anything in it that creates a definition creates one per file:

```c
/* Do NOT put this in a header. */
int requests_served = 0;              /* a definition: one per .c that includes it */
```

With two translation units including that header, the linker reports `duplicate symbol:
_requests_served`. The fix is `extern int requests_served;` in the header and the definition in
exactly one `.c` file. `const` is not a defence in C — unlike C++, a file-scope `const` in C still has
external linkage by default, so a `const` table in a header collides the same way. Either put the
definition in a `.c`, or mark it `static const` to give it internal linkage and accept a private copy
per file.

The include guard is the other half of the discipline:

```c
#ifndef PATH_H
#define PATH_H
/* ... */
#endif
```

Without it, a file that includes `path.h` directly and also through `http.h` sees the declarations
twice. For a function prototype a repeat is harmless, but for a `struct` or a `typedef` it is a
redefinition error. The guard makes the second inclusion a no-op, and the macro name must be unique
across the whole program — `PATH_H` rather than `PATH`, which some headers already define.

## The Makefile

A `Makefile` records two things per output: what it depends on, and the command that produces it.
`make` compares timestamps and runs only the commands whose outputs are older than their inputs, which
is where the whole speed advantage of separate compilation comes from.

The listing below is the complete project. The banner comments — `/* ===== path.h ===== */` and so on
— are **listing separators, not file contents**: they are valid C comments so the listing is exactly
what you would type, but when you create a real `Makefile` you leave its banner out. Every file is
named, and they are in dependency order.

```c make-files
/* ===== path.h ===== */
#ifndef PATH_H
#define PATH_H

#include <stddef.h>

/* Decode percent-escapes. Returns the decoded length, or -1 for a malformed
   escape or an encoded NUL. */
int percent_decode(const char *in, char *out, size_t outsz);

/* Join `root` and an already-decoded target. Returns 0 on success, or -1 if the
   result would leave the document root. */
int resolve_path(const char *root, const char *target, char *out, size_t outsz);

#endif
/* ===== path.c ===== */
#include "path.h"

#include <stdio.h>
#include <string.h>

static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

int percent_decode(const char *in, char *out, size_t outsz) {
    size_t j = 0;
    for (size_t i = 0; in[i] != '\0'; i++) {
        int c = (unsigned char)in[i];
        if (c == '%') {
            int hi = hex_value(in[i + 1]);
            int lo = hex_value(in[i + 2]);
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

int resolve_path(const char *root, const char *target, char *out, size_t outsz) {
    if (target[0] != '/') return -1;

    int n = snprintf(out, outsz, "%s", root);
    if (n < 0 || (size_t)n >= outsz) return -1;
    size_t len = (size_t)n;
    size_t rootlen = len;

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
/* ===== http.h ===== */
#ifndef HTTP_H
#define HTTP_H

#include <stddef.h>

/* The largest body this server will read into memory. */
#define MAX_BODY_BYTES (8u * 1024u * 1024u)

const char *mime_type(const char *path);

/* Caller frees. Returns NULL if the file cannot be read whole. */
char *read_file(const char *path, size_t *len_out);

/* Build a complete response. Returns the byte count, or 0 if it does not fit. */
size_t build_response(const char *status, const char *type,
                      const char *body, size_t body_len,
                      char *out, size_t outsz);

size_t error_page(const char *status, const char *message,
                  char *out, size_t outsz);

/* Request in, response out. Always produces a complete response. */
size_t handle(const char *root, const char *raw, char *out, size_t outsz);

#endif
/* ===== http.c ===== */
#include "http.h"
#include "path.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *mime_type(const char *path) {
    const char *dot = strrchr(path, '.');
    if (dot == NULL) return "application/octet-stream";
    if (strcmp(dot, ".html") == 0 || strcmp(dot, ".htm") == 0) return "text/html";
    if (strcmp(dot, ".css")  == 0) return "text/css";
    if (strcmp(dot, ".js")   == 0) return "text/javascript";
    if (strcmp(dot, ".txt")  == 0) return "text/plain";
    if (strcmp(dot, ".json") == 0) return "application/json";
    if (strcmp(dot, ".png")  == 0) return "image/png";
    return "application/octet-stream";
}

char *read_file(const char *path, size_t *len_out) {
    FILE *f = fopen(path, "rb");
    if (f == NULL) return NULL;

    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long size = ftell(f);
    if (size < 0) { fclose(f); return NULL; }
    if ((unsigned long)size > MAX_BODY_BYTES) { fclose(f); return NULL; }
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

size_t build_response(const char *status, const char *type,
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

size_t error_page(const char *status, const char *message,
                  char *out, size_t outsz) {
    return build_response(status, "text/plain", message, strlen(message), out, outsz);
}

size_t handle(const char *root, const char *raw, char *out, size_t outsz) {
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
        return error_page("404 Not Found", "no such file, or too large\n", out, outsz);

    size_t total = build_response("200 OK", mime_type(full), body, len, out, outsz);
    free(body);
    return total;
}
/* ===== server.h ===== */
#ifndef SERVER_H
#define SERVER_H

/* Bind and listen on 127.0.0.1:port. Pass 0 to let the kernel choose.
   Returns the listening descriptor, or -1, and writes the real port to *port_out. */
int start_listening(int port, int *port_out);

/* Accept one connection, answer it, close it. Returns 0, or -1 on accept failure. */
int serve_one(int listen_fd, const char *root);

/* Never returns: accept and serve until interrupted. */
int serve_loop(int listen_fd, const char *root);

#endif
/* ===== server.c ===== */
#include "server.h"
#include "http.h"

#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define REQUEST_MAX 4096
#define RESPONSE_MAX 16384

int start_listening(int port, int *port_out) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(fd, (struct sockaddr *)&addr, sizeof addr) < 0) { close(fd); return -1; }
    if (listen(fd, 16) < 0) { close(fd); return -1; }

    socklen_t len = sizeof addr;
    if (getsockname(fd, (struct sockaddr *)&addr, &len) < 0) { close(fd); return -1; }
    *port_out = ntohs(addr.sin_port);
    return fd;
}

/* Read until the blank line that ends the headers, or the buffer fills. */
static ssize_t read_request(int conn, char *buf, size_t cap) {
    size_t used = 0;
    while (used + 1 < cap) {
        ssize_t n = read(conn, buf + used, cap - 1 - used);
        if (n <= 0) break;
        used += (size_t)n;
        buf[used] = '\0';
        if (strstr(buf, "\r\n\r\n") != NULL) break;
    }
    buf[used] = '\0';
    return (ssize_t)used;
}

/* Send everything, or report failure. A short write is not an error. */
static int send_all(int fd, const char *data, size_t len) {
    size_t sent = 0;
    while (sent < len) {
        ssize_t w = write(fd, data + sent, len - sent);
        if (w <= 0) return -1;
        sent += (size_t)w;
    }
    return 0;
}

int serve_one(int listen_fd, const char *root) {
    int conn = accept(listen_fd, NULL, NULL);
    if (conn < 0) return -1;

    char request[REQUEST_MAX];
    read_request(conn, request, sizeof request);

    char response[RESPONSE_MAX];
    size_t total = handle(root, request, response, sizeof response);
    if (total == 0) {
        total = error_page("500 Internal Server Error", "response too large\n",
                           response, sizeof response);
    }
    send_all(conn, response, total);

    close(conn);
    return 0;
}

int serve_loop(int listen_fd, const char *root) {
    signal(SIGPIPE, SIG_IGN);          /* a vanished client is not fatal */
    for (;;) {
        if (serve_one(listen_fd, root) < 0) {
            if (errno == EINTR) continue;
            break;
        }
    }
    return 0;
}
/* ===== selftest.h ===== */
#ifndef SELFTEST_H
#define SELFTEST_H

/* Start a real server in a child process, drive it from this one, print the
   transcript, and return 0 if every response arrived. */
int run_self_test(const char *root);

#endif
/* ===== selftest.c ===== */
#include "selftest.h"
#include "server.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static void make_fixture(const char *root) {
    mkdir(root, 0755);

    char path[512];
    FILE *f;

    snprintf(path, sizeof path, "%s/index.html", root);
    f = fopen(path, "wb");
    if (f != NULL) { fputs("<h1>hello from serve</h1>\n", f); fclose(f); }

    snprintf(path, sizeof path, "%s/notes.txt", root);
    f = fopen(path, "wb");
    if (f != NULL) { fputs("a plain text file\n", f); fclose(f); }
}

static void dump(const char *label, const char *data, size_t len) {
    printf("=== %s -> %zu bytes ===\n", label, len);
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)data[i];
        if (c == '\r')      fputs("\\r", stdout);
        else if (c == '\n') fputs("\\n\n", stdout);
        else                putchar(c);
    }
}

int run_self_test(const char *root) {
    make_fixture(root);

    int port = 0;
    int srv = start_listening(0, &port);
    if (srv < 0) { perror("start_listening"); return 1; }

    const char *requests[] = {
        "GET / HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /notes.txt HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /missing.txt HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /../etc/passwd HTTP/1.1\r\nHost: x\r\n\r\n",
        "PUT / HTTP/1.1\r\nHost: x\r\n\r\n",
    };
    size_t count = sizeof requests / sizeof requests[0];

    /* The child serves; this process does every read and every print, so the
       transcript is reproducible. */
    pid_t child = fork();
    if (child == 0) {
        for (size_t i = 0; i < count; i++) serve_one(srv, root);
        close(srv);
        _exit(0);
    }

    usleep(150000);                     /* let the child reach accept() */

    for (size_t i = 0; i < count; i++) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        if (c < 0) { perror("socket"); return 1; }

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof addr);
        addr.sin_family = AF_INET;
        addr.sin_port = htons((uint16_t)port);
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        if (connect(c, (struct sockaddr *)&addr, sizeof addr) < 0) {
            perror("connect");
            return 1;
        }
        if (write(c, requests[i], strlen(requests[i])) < 0) {
            perror("write");
            return 1;
        }

        char got[8192];
        ssize_t total = 0;
        ssize_t r;
        while ((r = read(c, got + total, sizeof got - 1 - (size_t)total)) > 0) total += r;
        got[total] = '\0';

        char label[64];
        snprintf(label, sizeof label, "%.*s", (int)strcspn(requests[i], "\r"), requests[i]);
        dump(label, got, (size_t)total);
        close(c);
    }

    waitpid(child, NULL, 0);
    close(srv);
    return 0;
}
/* ===== main.c ===== */
#include "server.h"
#include "selftest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define DEFAULT_PORT 8080
#define DEFAULT_ROOT "docroot"

static int parse_port(const char *text, int *out) {
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0') return -1;
    if (value < 0 || value > 65535) return -1;
    *out = (int)value;
    return 0;
}

static void usage(const char *program) {
    printf("usage: %s                run the built-in self-test\n", program);
    printf("       %s <port> [root]  serve files from root (default %s)\n",
           program, DEFAULT_ROOT);
}

int main(int argc, char **argv) {
    if (argc == 1) {
        printf("no arguments: running the built-in self-test\n");
        return run_self_test(DEFAULT_ROOT);
    }
    if (strcmp(argv[1], "--help") == 0) {
        usage(argv[0]);
        return 0;
    }

    int port = DEFAULT_PORT;
    if (parse_port(argv[1], &port) != 0) {
        fprintf(stderr, "%s: not a port number: %s\n", argv[0], argv[1]);
        usage(argv[0]);
        return 2;
    }
    if (port == 0) {
        fprintf(stderr, "%s: port 0 means \"pick one\", which is for tests\n", argv[0]);
        return 2;
    }

    const char *root = argc > 2 ? argv[2] : DEFAULT_ROOT;

    int real_port = 0;
    int srv = start_listening(port, &real_port);
    if (srv < 0) {
        perror("start_listening");
        return 1;
    }

    printf("serving %s on http://127.0.0.1:%d/\n", root, real_port);
    fflush(stdout);

    serve_loop(srv, root);
    close(srv);
    return 0;
}
/* ===== Makefile ===== */
CC      = cc
CFLAGS  = -std=c17 -Wall -Wextra -Werror -O2

OBJS    = main.o path.o http.o server.o selftest.o

prog: $(OBJS)
	$(CC) $(CFLAGS) -o prog $(OBJS)

main.o: main.c server.h selftest.h
	$(CC) $(CFLAGS) -c main.c

path.o: path.c path.h
	$(CC) $(CFLAGS) -c path.c

http.o: http.c http.h path.h
	$(CC) $(CFLAGS) -c http.c

server.o: server.c server.h http.h
	$(CC) $(CFLAGS) -c server.c

selftest.o: selftest.c selftest.h server.h
	$(CC) $(CFLAGS) -c selftest.c

clean:
	rm -f prog $(OBJS)

.PHONY: clean
```

```text
no arguments: running the built-in self-test
=== GET / HTTP/1.1 -> 109 bytes ===
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 26\r\n
Connection: close\r\n
\r\n
<h1>hello from serve</h1>\n
=== GET /notes.txt HTTP/1.1 -> 102 bytes ===
HTTP/1.1 200 OK\r\n
Content-Type: text/plain\r\n
Content-Length: 18\r\n
Connection: close\r\n
\r\n
a plain text file\n
=== GET /missing.txt HTTP/1.1 -> 118 bytes ===
HTTP/1.1 404 Not Found\r\n
Content-Type: text/plain\r\n
Content-Length: 27\r\n
Connection: close\r\n
\r\n
no such file, or too large\n
=== GET /../etc/passwd HTTP/1.1 -> 117 bytes ===
HTTP/1.1 403 Forbidden\r\n
Content-Type: text/plain\r\n
Content-Length: 26\r\n
Connection: close\r\n
\r\n
outside the document root\n
=== PUT / HTTP/1.1 -> 118 bytes ===
HTTP/1.1 405 Method Not Allowed\r\n
Content-Type: text/plain\r\n
Content-Length: 18\r\n
Connection: close\r\n
\r\n
only GET and HEAD\n
```

`make` runs the recipe above, and then the `prog` it produced runs its own self-test. Five real HTTP
responses, over a real socket, produced by a program built by a real `make`. That is the whole
project working, and it is reproducible: running `prog` again prints the same transcript.

Making `prog` with no arguments run the self-test is a deliberate choice, and a useful habit. A build
that produces a binary you cannot run without arguments has no way to prove it works; a build whose
default action is a self-test makes `make && ./prog` a complete check.

## Building it

From clean, one command compiles five `.c` files and links them:

```sh run-project
make clean
make
```

```text
rm -f prog main.o path.o http.o server.o selftest.o
cc -std=c17 -Wall -Wextra -Werror -O2 -c main.c
cc -std=c17 -Wall -Wextra -Werror -O2 -c path.c
cc -std=c17 -Wall -Wextra -Werror -O2 -c http.c
cc -std=c17 -Wall -Wextra -Werror -O2 -c server.c
cc -std=c17 -Wall -Wextra -Werror -O2 -c selftest.c
cc -std=c17 -Wall -Wextra -Werror -O2 -o prog main.o path.o http.o server.o selftest.o
```

Run it again and it does nothing at all, because nothing it depends on has changed:

```sh run-project
make
```

```text
make: `prog' is up to date.
```

That wording is GNU Make 3.81's, which is what ships with macOS. The exact spelling is not stable
across versions, so do not build anything on it. What matters is the comparison underneath: `prog` is
newer than every `.o`, and every `.o` is newer than the `.c` it came from.

Now change one source file and watch what `make` decides to redo:

```sh run-project
sleep 1
touch http.c
make
```

```text
cc -std=c17 -Wall -Wextra -Werror -O2 -c http.c
cc -std=c17 -Wall -Wextra -Werror -O2 -o prog main.o path.o http.o server.o selftest.o
```

One compilation and one link — four compilations skipped. The dependency lines are what make this
possible: `http.o: http.c http.h path.h` tells `make` that `http.o` must be rebuilt when any of those
three changes, and that nothing else depends on `http.c`.

That `sleep 1` is not decoration, and leaving it out is a classic hour-long wild goose chase. `make`
decides by comparing timestamps; if you `touch` a file and rebuild within the same second, the touched
file can carry the same timestamp as the object already built from it, so `make` correctly concludes
there is nothing to do and you conclude that `make` is broken. Measured on this machine, without the
`sleep` the rebuild happened 2 times out of 5. When a build system seems to be ignoring your change,
rule this out before you rule out the build system.

Leave a dependency out and you get the opposite problem: change a header, `make` says nothing to be
done, and you link a stale object file against a new header. The symptom is a program that behaves
according to the old code — which is confusing enough that it is worth writing the dependency lines
carefully the first time. A missing dependency does not produce an error; it produces a program that
is quietly one edit behind.

## Driving it with curl

The self-test proves the server answers its own client. To prove it answers *other* clients, start it
on a port and point `curl` at it. `curl` is a separate program with its own HTTP implementation, so a
correct response from it is evidence the server speaks the protocol rather than merely matching
itself.

```sh run-project
mkdir -p live
printf '<h1>live</h1>\n' > live/index.html
printf 'body { color: red; }\n' > live/style.css

./prog 8791 live > server.log 2>&1 &
srv=$!
trap 'kill $srv 2>/dev/null' EXIT
sleep 1

cat server.log
curl -s -i http://127.0.0.1:8791/
curl -s -i http://127.0.0.1:8791/style.css

kill $srv
wait $srv 2>/dev/null
exit 0
```

```text
serving live on http://127.0.0.1:8791/
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 14
Connection: close

<h1>live</h1>
HTTP/1.1 200 OK
Content-Type: text/css
Content-Length: 21
Connection: close

body { color: red; }
```

Three details in that script are worth copying into your own testing habits. The server runs in the
background and its own output goes to `server.log` rather than to the terminal, so the transcript you
read is the *client's* view and not a jumble of two processes talking over each other. `kill` then
`wait` stops it, so nothing is left listening on the port when the script ends. And `trap ... EXIT`
means the server is stopped even if something above it fails — a stray server holding a port is the
single most annoying thing to debug, because the next run fails for a reason that has nothing to do
with the code you just changed.

`curl` prints these headers with `\r\n` line endings, because that is what HTTP uses on the wire. The
`\r` is invisible here, and it is the same `\r` the server writes in `build_response`.

The status codes are the interesting part, because each one exercises a different refusal — and the
middle two are the *same URL*:

```sh run-project
mkdir -p live
printf '<h1>live</h1>\n' > live/index.html

./prog 8792 live > server.log 2>&1 &
srv=$!
trap 'kill $srv 2>/dev/null' EXIT
sleep 1

curl -s -o /dev/null -w "status=%{http_code}\n" http://127.0.0.1:8792/nope
curl -s -o /dev/null -w "status=%{http_code}\n" http://127.0.0.1:8792/../../../../etc/passwd
curl -s -o /dev/null -w "status=%{http_code}\n" --path-as-is "http://127.0.0.1:8792/../../../../etc/passwd"
curl -s -o /dev/null -w "status=%{http_code}\n" -X POST http://127.0.0.1:8792/

kill $srv
wait $srv 2>/dev/null
exit 0
```

```text
status=404
status=404
status=403
status=405
```

Four requests, and every refusal comes from a different guard in `handle`: the file is not there, the
method is not allowed, the path escapes the root. Two of them return the same `404` for completely
different reasons, which is exactly why those two lines are worth reading together.

The two `.../../../../../etc/passwd` lines are the same URL, and the difference between them is the
whole lesson. By default `curl` normalises the path to `/etc/passwd` *before sending it*, because it is
trying to be a well-behaved client. The server never sees a `..`, so it looks for `/etc/passwd` inside
the document root, does not find it, and answers `404`. Add `--path-as-is` and the traversal is sent
literally: the resolver sees it, refuses it, and the answer becomes `403` — the security check firing
for real, against a real client, over a real socket.

That distinction matters when you test your own server: a traversal test that uses a normalising
client tests nothing. The attack only exists if the bytes reach your resolver, so the test has to
deliver them. A security test that passes because it never sent the attack is worse than no test at
all, because it is a passing security test and you will believe it.

:::scenario The Makefile that linked a stale object

A developer adds a new field to a struct in `http.h`, rebuilds, and the program behaves as though the
field does not exist — the new code reads garbage, and one response comes back with a
`Content-Length` that does not match its body. Rebuilding from clean fixes it. The suspicion falls on
the compiler, then on undefined behaviour, then on the filesystem.

The cause is a dependency line that names the `.c` file and not the headers:

```c
/* WRONG: http.o will not be rebuilt when http.h changes */
http.o: http.c
	$(CC) $(CFLAGS) -c http.c
```

`make` looks at two timestamps: `http.o` and `http.c`. `http.h` changed, `http.c` did not, so
`http.o` is newer than everything it is declared to depend on and `make` reports nothing to be done.
The link then combines a new `http.h` with an `http.o` compiled against the old one. Since C has no
name mangling and no type information at link time, the linker cannot notice — it just resolves
symbols.

:::solution List every header the file includes

```make
http.o: http.c http.h path.h
	$(CC) $(CFLAGS) -c http.c
```

`http.c` includes both `http.h` and `path.h`, so both are dependencies. That is the rule: **the
prerequisites of an object file are its source plus every header it includes, directly or
transitively.**

Writing that by hand does not scale, and the standard tool for it is the compiler itself. `cc` can
emit the dependency list as a side effect of compiling:

```sh run-project
cc -MM http.c
```

```text
http.o: http.c http.h path.h
```

`-MM` prints the rule `make` needs, including the headers it found, and omits system headers. The
conventional way to use it is to generate a `.d` file per source and include those files:

```make
CFLAGS += -MMD
-include $(OBJS:.o=.d)
```

With `-MMD`, compiling `http.c` also writes `http.d` containing the rule above; the `-include` line
pulls every `.d` file in if it exists and says nothing if it does not. The `-` prefix is what makes a
missing `.d` file on the first build a non-event. After that, `make` maintains its own dependency
information and a header change rebuilds exactly the files that include it — which is the thing
separate compilation was supposed to give you in the first place.

:::

:::pitfall One `main`, and only one

Splitting a program into several `.c` files means several translation units, and exactly one of them
may define `main`. A second `main` is not a warning and not a preference — it is a link error:

```text
duplicate symbol '_main' in:
    main.o
    selftest.o
```

The same applies to any function that is not `static`. Every non-`static` function in every `.c` file
becomes a symbol the linker must resolve to exactly one definition, which is why `read_request` and
`send_all` in `server.c` are `static`. If you find yourself wanting two files that both define
`init`, that is the compiler telling you the function should be private to each file.

The inverse error is just as common and reads more confusingly:

```text
Undefined symbols for architecture arm64:
  "_resolve_path", referenced from:
      _handle in http.o
```

That means a *declaration* existed — `http.c` included `path.h` and compiled fine — but no
translation unit provided a *definition*. Either `path.c` was not added to `OBJS`, or it was not
compiled, or the function name in the header does not match the one in the `.c` file. The compiler
cannot catch it, because each file is compiled independently and the declaration is a promise; only
the linker sees that the promise was never kept. When you meet it, the first thing to check is
whether the source file is in the `OBJS` list.

:::

## A hardening checklist

The project works. Before calling it finished, these are the questions worth answering, and each one
maps to something this part covered:

- **Does every path out of the handler release what it acquired?** `free` the body, `fclose` the file,
  `close` the connection. The leak that kills a server is a per-request resource leaked on an error
  path.
- **Is the response buffer sized for headers plus body, and is the `0` return checked?** `build_response`
  returning 0 means "did not fit"; sending nothing leaves the client hanging.
- **Is there a cap on the body size?** `MAX_BODY_BYTES` is checked before the `malloc`, so a large file
  produces a `404`-with-explanation rather than an out-of-memory kill.
- **Does the resolver reject traversal after decoding, not before?** The `403` from `curl --path-as-is`
  is the proof.
- **Is `SIGPIPE` ignored once at startup?** Otherwise one client closing a tab takes the process down.
- **Does every read and write loop?** A request that arrives in two packets and a response that only
  partly sends are both normal, not exceptional.
- **Are the buffers' sizes checked before every copy?** `sscanf` field widths, the target buffer, the
  request buffer, the response buffer.
- **Is `accept`'s failure handled?** `EINTR` means try again; anything else means stop.
- **Does the server bind to loopback, or deliberately to `INADDR_ANY`?** Listening on every interface
  by accident exposes the port to the network.

Two things this server deliberately does not do, both of which you should be able to name as
limitations rather than bugs: it serves **one connection at a time**, so a slow client blocks
everyone else, and it uses **`Connection: close`**, so every request costs a TCP handshake. Both are
correct choices for a first server and both are the first things to change in a real one — by adding
`fork` or `select`, and by parsing the `Connection` header.

## Key takeaways

- A header holds declarations, types and macros. Definitions go in exactly one `.c` file, or the
  linker reports `duplicate symbol`.
- In C, a file-scope `const` still has external linkage, so a `const` table in a header collides. Use
  `extern` plus one definition, or `static const`.
- Every header needs an include guard with a unique macro name, or a `struct` or `typedef` included
  twice is a redefinition error.
- `static` at file scope gives internal linkage: the name never reaches the linker, so two files can
  each have their own private helper.
- A Makefile rule is `target: prerequisites` plus a tab-indented recipe. `make` rebuilds a target only
  when a prerequisite is newer.
- An object file's prerequisites are its source **plus every header it includes**. Leaving one out
  produces a stale object and no error.
- `cc -MM source.c` prints the dependency rule for you, and `-MMD` plus `-include $(OBJS:.o=.d)` lets
  `make` maintain it automatically.
- `duplicate symbol` means two definitions of one name; `Undefined symbols` means a declaration with
  no definition — usually a source file missing from `OBJS`.
- `curl` is a separate HTTP implementation, so its agreement is real evidence. Use `--path-as-is` to
  test traversal, because by default `curl` normalises the path before sending it.
- Make a build self-testing: if the default action of the binary is a test, `make && ./prog` proves the
  build works.

## Practice

- [ ] Add `-MMD` and `-include $(OBJS:.o=.d)` to the Makefile, then `touch http.h` and confirm that
      exactly `http.o` and the link step rerun.
- [ ] Add a `HEAD` handler that sends the real `Content-Length` with no body, and check with
      `curl -I` that the header is right and the body is empty.
- [ ] Add an `Access-Control-Allow-Origin` header to every response and confirm with
      `curl -s -i` that it appears.
- [ ] Add a `requests_served` counter as `extern int` in a header plus one definition in `server.c`,
      increment it in `serve_one`, and print it when the process exits. Explain why the definition
      cannot go in the header.
- [ ] Add a `--version` flag that prints a version string, and make `--help` list both flags. Test
      `prog --version`, `prog --help` and `prog nonsense`.
- [ ] Change `MAX_BODY_BYTES` to 4096, create a 5000-byte file, and confirm the server refuses it
      rather than truncating it. Then explain why `413` would be a better status than `404`.

## Solutions

:::solution Exercise 1

```make
CC      = cc
CFLAGS  = -std=c17 -Wall -Wextra -Werror -O2 -MMD

OBJS    = main.o path.o http.o server.o selftest.o

prog: $(OBJS)
	$(CC) $(CFLAGS) -o prog $(OBJS)

-include $(OBJS:.o=.d)

clean:
	rm -f prog $(OBJS) $(OBJS:.o=.d)

.PHONY: clean
```

With `-MMD` you no longer need an explicit rule per object file: `make`'s built-in rule for `%.o: %.c`
compiles it, and the `.d` file supplies the header prerequisites. `$(OBJS:.o=.d)` is a substitution
reference — it takes the list `main.o path.o ...` and replaces the `.o` suffix with `.d`, producing
`main.d path.d ...`.

The block below writes that Makefile over the project's own and then drives it, so the recipe is
checked rather than described. It compiles from clean, prints the dependency file the compiler wrote,
and then touches `http.h` to see what `make` decides to redo:

```sh run-project
cat > Makefile <<'EOF'
CC      = cc
CFLAGS  = -std=c17 -Wall -Wextra -Werror -O2 -MMD

OBJS    = main.o path.o http.o server.o selftest.o

prog: $(OBJS)
	$(CC) $(CFLAGS) -o prog $(OBJS)

-include $(OBJS:.o=.d)

clean:
	rm -f prog $(OBJS) $(OBJS:.o=.d)

.PHONY: clean
EOF

make clean
make
cat http.d
sleep 1
touch http.h
make
```

```text
rm -f prog main.o path.o http.o server.o selftest.o main.d path.d http.d server.d selftest.d
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o main.o main.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o path.o path.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o http.o http.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o server.o server.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o selftest.o selftest.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD -o prog main.o path.o http.o server.o selftest.o
http.o: http.c http.h path.h
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o http.o http.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD   -c -o server.o server.c
cc -std=c17 -Wall -Wextra -Werror -O2 -MMD -o prog main.o path.o http.o server.o selftest.o
```

Read the last four lines carefully, because they are the whole point. Touching `http.h` recompiled
**two** files, not one: `http.c` and `server.c` both include `http.h`, and both `.d` files say so.
That is exactly the rebuild you want — and it is the rebuild the hand-written Makefile gets right too,
because its rules list `http.h` for both. What `-MMD` buys you is that you did not have to know that,
and it stays right when `server.c` starts including one more header.

`clean` removes the `.d` files as well, because a stale dependency file is as bad as a missing one —
it would name headers that no longer exist, and `make` would refuse to build a target whose
prerequisite it cannot find.

:::

:::solution Exercise 2

In `http.c`, the `handle` function gains a branch, and `build_response` needs to know whether to write
a body. The simplest change is a `head_only` parameter:

```c
size_t build_response(const char *status, const char *type,
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
```

and `handle` passes `strcmp(method, "HEAD") == 0`.

The function is small enough to test on its own, and testing it that way is quicker than starting a
server and pointing `curl` at it. It is also more honest: `curl -I` prints only headers, so it *cannot*
tell the two versions apart — both report `Content-Length: 14`. The difference is in the bytes:

```c run
#include <stdio.h>
#include <string.h>

size_t build_response(const char *status, const char *type,
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

static void dump(const char *label, const char *buf, size_t n) {
    printf("--- %s: %zu bytes ---\n", label, n);
    for (size_t i = 0; i < n; i++) {
        if (buf[i] == '\r')      printf("\\r");
        else if (buf[i] == '\n') printf("\\n\n");
        else                     putchar(buf[i]);
    }
}

int main(void) {
    const char *body = "<h1>live</h1>\n";
    char out[256];

    dump("GET",  out, build_response("200 OK", "text/html", body, strlen(body), 0, out, sizeof out));
    dump("HEAD", out, build_response("200 OK", "text/html", body, strlen(body), 1, out, sizeof out));
    return 0;
}
```

```text
--- GET: 97 bytes ---
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 14\r\n
Connection: close\r\n
\r\n
<h1>live</h1>\n
--- HEAD: 83 bytes ---
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 14\r\n
Connection: close\r\n
\r\n
```

Identical headers, identical `Content-Length: 14`, and fourteen fewer bytes. That is the whole of
`HEAD`. The `Content-Length` it reports is the length the body *would* have had: a client asking "how
big is this" must be told the real size, not zero, or every download manager and link checker that
uses `HEAD` to decide whether to fetch will get the answer wrong.

:::

:::solution Exercise 3

In `http.c`, `build_response` gains one header line:

```c
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
```

```c run
#include <stdio.h>
#include <string.h>

size_t build_response(const char *status, const char *type,
                      const char *body, size_t body_len,
                      char *out, size_t outsz) {
    int n = snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || (size_t)n >= outsz) return 0;
    if ((size_t)n + body_len > outsz) return 0;
    memcpy(out + n, body, body_len);
    return (size_t)n + body_len;
}

static void dump(const char *label, const char *buf, size_t n) {
    printf("--- %s: %zu bytes ---\n", label, n);
    for (size_t i = 0; i < n; i++) {
        if (buf[i] == '\r')      printf("\\r");
        else if (buf[i] == '\n') printf("\\n\n");
        else                     putchar(buf[i]);
    }
}

int main(void) {
    const char *page = "<h1>live</h1>\n";
    const char *miss = "no such file, or too large\n";
    char out[256];

    dump("200", out, build_response("200 OK", "text/html", page, strlen(page), out, sizeof out));
    dump("404", out, build_response("404 Not Found", "text/plain", miss, strlen(miss), out, sizeof out));
    return 0;
}
```

```text
--- 200: 129 bytes ---
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 14\r\n
Access-Control-Allow-Origin: *\r\n
Connection: close\r\n
\r\n
<h1>live</h1>\n
--- 404: 150 bytes ---
HTTP/1.1 404 Not Found\r\n
Content-Type: text/plain\r\n
Content-Length: 27\r\n
Access-Control-Allow-Origin: *\r\n
Connection: close\r\n
\r\n
no such file, or too large\n
```

The `404` is the interesting one. Every response goes through `build_response`, including the error
pages, so the header is on the failure too — which is what a browser needs, because a `fetch` that
fails is indistinguishable from a network error unless the error response carries the header that lets
the browser read it.

`*` is fine for a local tool and wrong for anything authenticated: it lets any web page in any origin
read your responses using the user's cookies. A real server echoes back a specific allowed origin
from a list.

:::

:::solution Exercise 4

`server.h` gains the declaration:

```c
extern int requests_served;
```

`server.c` gains the definition and the increment:

```c
int requests_served = 0;

int serve_one(int listen_fd, const char *root) {
    int conn = accept(listen_fd, NULL, NULL);
    if (conn < 0) return -1;
    requests_served++;
    /* ... */
}
```

and `serve_loop` prints it after the loop ends:

```c
    printf("served %d request(s)\n", requests_served);
```

The definition cannot go in the header because the header is inserted into every translation unit
that includes it. `int requests_served = 0;` is a definition — it asks the compiler to reserve storage
and give the symbol an address — so `server.c` and any other file including `server.h` would each
produce one, and the linker would report `duplicate symbol: _requests_served`. `extern` is a
declaration: it says "this name exists somewhere, do not allocate anything here", which is exactly
what a header is for.

:::

:::solution Exercise 5

Start from what the program does now. Both behaviours you are extending already exist — `--help` is
handled, and a bad port prints a diagnostic and exits `2` — so the quickest way to get this right is to
run them and look:

```sh run-project
./prog --help
echo "exit status: $?"
./prog nonsense 2>&1
echo "exit status: $?"
```

```text
usage: ./prog                run the built-in self-test
       ./prog <port> [root]  serve files from root (default docroot)
exit status: 0
./prog: not a port number: nonsense
usage: ./prog                run the built-in self-test
       ./prog <port> [root]  serve files from root (default docroot)
exit status: 2
```

The `2>&1` on the third line is doing the work: the diagnostic and the usage text both go to `stderr`,
and `2>&1` folds `stderr` into `stdout` so you can see them next to the exit status that follows.
`--help` writes to `stdout` and exits `0`; the bad port writes to `stderr` and exits `2`. That split
matters, because `--help` output is data a script may capture while a usage error is a diagnostic, and
a script that pipes one into the other needs to be able to tell them apart. Exit `0` means "I did what
you asked" and non-zero means "I did not".

The change is one more branch of the same shape, plus two lines in `usage` so the new flag is
discoverable:

```c
#define VERSION "serve 1.0"

static void usage(const char *program) {
    printf("usage: %s                run the built-in self-test\n", program);
    printf("       %s <port> [root]  serve files from root (default %s)\n",
           program, DEFAULT_ROOT);
    printf("       %s --help         show this message\n", program);
    printf("       %s --version      show the version\n", program);
}

int main(int argc, char **argv) {
    if (argc == 1) {
        printf("no arguments: running the built-in self-test\n");
        return run_self_test(DEFAULT_ROOT);
    }
    if (strcmp(argv[1], "--help") == 0) {
        usage(argv[0]);
        return 0;
    }
    if (strcmp(argv[1], "--version") == 0) {
        printf("%s\n", VERSION);
        return 0;
    }
    /* ... port parsing as before ... */
}
```

The transcript above is the program *before* this change, which is why `usage` prints two lines there
and four here. Those two extra lines are the only difference you should see.

:::

:::solution Exercise 6

With `MAX_BODY_BYTES` at 4096, `read_file` returns `NULL` for a 5000-byte file, because the size check
happens before the `malloc`:

```c
if ((unsigned long)size > MAX_BODY_BYTES) { fclose(f); return NULL; }
```

and `handle` turns any `NULL` into the same error page it uses for a missing file:

```text
HTTP/1.1 404 Not Found
Content-Type: text/plain
Content-Length: 27
Connection: close

no such file, or too large
```

The file is refused rather than truncated, which is the important part — a truncated body with a
`Content-Length` for the full size is the failure mode that hangs clients.

`413 Payload Too Large` would be better than `404` because the two situations are genuinely different.
`404` says "there is no such resource", and a client that gets one may reasonably stop asking. `413`
says "that resource exists but is too large for me to serve", which is information the client can act
on — by asking for a range, by using a different endpoint, or by reporting a useful error. The
distinction costs one extra status string and one branch in `read_file` to distinguish "cannot open"
from "too large", and it turns a confusing failure into an actionable one.
:::
