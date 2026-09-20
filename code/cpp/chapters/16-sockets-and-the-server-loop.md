---
chapter: 16
part: 3
title: Sockets and the Server Loop
summary: Open a listening socket, accept connections in a loop, read a request that arrives in pieces, write a response that may only partly send, and survive a client that hangs up mid-answer.
minutes: 75
tags: [socket, bind, listen, accept, tcp, sigpipe, partial-write, server-loop, fork]
---

The previous three chapters built a function that turns a request into a response. This chapter puts
it on the network. The socket API is small — five calls to start a server, two more per connection —
but every one of them has a failure mode that a file-based program never has to think about. Bytes
arrive in pieces, writes accept fewer bytes than you offer, and the client can vanish halfway through
your answer. Handling those three correctly is most of what separates a program that works on your
laptop from one that works.

## A socket is a file descriptor

`socket()` returns an `int`, and that integer is an entry in the same table that `open` uses. You read
and write it with `read` and `write`, and you release it with `close` — the same calls, the same
rules, and the same obligation to close it on every path out of the function. That is why the
descriptor-exhaustion scenario in the first chapter of this part was about sockets: every unclosed
connection is a leaked file, and the process has a hard limit on how many it can hold.

Starting a server takes four calls in a fixed order, and a fifth to find out which port you got:

```c run
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) { perror("socket"); return 1; }
    printf("socket() -> %s\n", fd >= 0 ? "a file descriptor" : "failed");

    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(0);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    printf("sizeof(struct sockaddr_in) = %zu\n", sizeof addr);
    printf("host byte order 8080 -> network order %u\n", (unsigned)htons(8080));
    printf("network order back   -> host order   %u\n", (unsigned)ntohs(htons(8080)));

    if (bind(fd, (struct sockaddr *)&addr, sizeof addr) < 0) { perror("bind"); return 1; }
    if (listen(fd, 16) < 0) { perror("listen"); return 1; }

    socklen_t len = sizeof addr;
    if (getsockname(fd, (struct sockaddr *)&addr, &len) < 0) { perror("getsockname"); return 1; }
    int port = ntohs(addr.sin_port);
    printf("bound to 127.0.0.1 on a kernel-assigned port (%s)\n",
           port > 0 && port < 65536 ? "a real port number" : "not a port");
    close(fd);
    return 0;
}
```

```text
socket() -> a file descriptor
sizeof(struct sockaddr_in) = 16
host byte order 8080 -> network order 36895
network order back   -> host order   8080
bound to 127.0.0.1 on a kernel-assigned port (a real port number)
```

`socket(AF_INET, SOCK_STREAM, 0)` asks for an IPv4 TCP socket. `AF_INET` is the address family,
`SOCK_STREAM` is the reliable byte-stream protocol, and the third argument is the protocol number —
`0` means "the default for this family and type", which is TCP.

`SO_REUSEADDR` is not optional in practice. Without it, a server that was killed and restarted within
about a minute fails to `bind` with `Address already in use`, because the old socket's port is still
in `TIME_WAIT`. Setting it lets you restart immediately, and the failure it prevents is one that
looks like a bug in your code when it is a property of TCP.

`htons(8080)` returning **36895** is worth pausing on. 8080 is `0x1F90`; network byte order is
big-endian, and this machine is little-endian, so the two bytes swap to `0x901F` = 36895. That is
exactly what `htons` is for. Ports and addresses always travel in network byte order, so every value
that goes into a `sockaddr_in` passes through `htons` or `htonl`, and every value read out passes
through `ntohs` or `ntohl`. On a big-endian machine the functions are no-ops — which is precisely why
forgetting them produces code that works on one architecture and fails on another.

`htons(0)` is how you ask the kernel to pick a free port. `getsockname` then tells you which one it
chose, which is what lets a test start a server without caring what else is running on the machine.

## The `sockaddr` dance

Every socket call takes a `struct sockaddr *`, and you always have a `struct sockaddr_in`. The two
are different types, and C will not quietly convert between them:

```c bad
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(void) {
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    struct sockaddr generic = addr;
    printf("%d\n", generic.sa_family);
    return 0;
}
```

```text
initializing 'struct sockaddr' with an expression of incompatible type 'struct sockaddr_in'
```

This is why every call in this chapter is written `bind(fd, (struct sockaddr *)&addr, sizeof addr)`.
The API predates `void *`, so it takes a pointer to a generic address structure plus a length, and the
cast is how you say "I know this is really an IPv4 address; the length tells you so". The `sizeof` is
not decoration either: `bind` uses it to decide which address family it is looking at. Passing the
size of the wrong structure is a bug that produces `EINVAL` at best.

`INADDR_LOOPBACK` restricts the socket to `127.0.0.1`, so only programs on this machine can connect.
The alternative, `INADDR_ANY`, listens on every interface — which is what you want on a server and
what you must not do by accident while learning, because it exposes the port to the network.

## Accepting connections

`accept` returns a **new** descriptor for the connection and leaves the listening socket untouched,
ready for the next client. That is the whole reason a server can handle more than one client: the
listening socket is a factory, and each `accept` produces a separate connection.

```c
for (;;) {
    int conn = accept(listen_fd, NULL, NULL);
    if (conn < 0) {
        if (errno == EINTR) continue;     /* a signal interrupted us; try again */
        break;                            /* something real went wrong */
    }
    serve_one(conn);
    close(conn);
}
```

Three details. `accept` blocks until a client connects, so an idle server costs nothing. `EINTR` means
a signal arrived while waiting, which is not an error and must not terminate the loop — without that
check, a server that receives any signal dies silently. And `conn` is closed inside the loop, on the
path that serves it, so the descriptor count returns to where it started after every request.

The two `NULL` arguments are the client's address and its length, which this server does not need. A
logging server passes pointers for both and gets the peer's IP and port.

## Reading a request that arrives in pieces

A single `read` returns whatever has arrived. For a request to be complete you need to see the blank
line that ends the headers, so the read is a loop:

```c
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
```

Four properties make this correct, and each one is a bug in the version most people write first.

It reads into `buf + used`, not `buf`, so the second read appends rather than overwriting. It asks for
`cap - 1 - used` bytes, so it can never write past the end and always leaves room for the NUL. It
NUL-terminates after every read, so `strstr` is safe at every point rather than only at the end. And
it stops as soon as `\r\n\r\n` appears, so a client that sends the headers and then stalls does not
hold the server forever.

`n <= 0` covers both ends: `0` means the client closed the connection, and a negative value is an
error. Both mean there is no request to answer.

The loop also has a bound. If a client sends 4000 bytes with no blank line, `used + 1 < cap` fails,
the loop exits, and the buffer holds a request that never ended. `handle` will fail to parse it and
answer `400`, which is the right outcome — and crucially, the server does not hang waiting for a
header block that is never coming.

## Writing a response that only partly sends

`write` returns the number of bytes it accepted, and it may accept fewer than you offered. On a
blocking socket it will usually block until it can take everything, but "usually" is not a guarantee:
a non-blocking socket returns immediately with whatever fits, and even a blocking socket can return
short. The fix is to loop:

```c
size_t sent = 0;
while (sent < total) {
    ssize_t w = write(conn, response + sent, total - sent);
    if (w <= 0) break;                    /* the peer is gone; give up */
    sent += (size_t)w;
}
```

This is the same shape as `read_request` and for the same reason: the operating system is allowed to
move fewer bytes than you asked for, so the program must track how far it got. A server that writes
once and assumes success produces responses that are truncated under load and complete in testing.

You can see a short write happen by shrinking the socket's send buffer and giving the client a
receive buffer it never drains:

```c run
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(0);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    bind(srv, (struct sockaddr *)&addr, sizeof addr);
    listen(srv, 4);
    socklen_t slen = sizeof addr;
    getsockname(srv, (struct sockaddr *)&addr, &slen);
    int port = ntohs(addr.sin_port);

    pid_t child = fork();
    if (child == 0) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in a2;
        memset(&a2, 0, sizeof a2);
        a2.sin_family = AF_INET;
        a2.sin_port = htons((uint16_t)port);
        a2.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        if (connect(c, (struct sockaddr *)&a2, sizeof a2) < 0) { perror("connect"); _exit(1); }
        pause();                        /* connect, then never read */
        _exit(0);
    }

    int conn = accept(srv, NULL, NULL);
    if (conn < 0) { perror("accept"); return 1; }

    int small = 2048;
    setsockopt(conn, SOL_SOCKET, SO_SNDBUF, &small, sizeof small);
    fcntl(conn, F_SETFL, fcntl(conn, F_GETFL, 0) | O_NONBLOCK);

    static char big[1024 * 1024];
    memset(big, 'z', sizeof big);

    size_t sent = 0;
    int short_writes = 0;
    for (int round = 1; round <= 4; round++) {
        ssize_t w = write(conn, big + sent, sizeof big - sent);
        if (w < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                printf("write #%d: nothing accepted (EAGAIN) after %zu bytes\n", round, sent);
                break;
            }
            perror("write");
            break;
        }
        if (w < (ssize_t)(sizeof big - sent)) short_writes++;
        printf("write #%d accepted %7zd of %zu remaining\n", round, w, sizeof big - sent);
        sent += (size_t)w;
    }
    printf("short writes: %d, total accepted %zu of %zu\n", short_writes, sent, sizeof big);

    close(conn);
    close(srv);
    kill(child, SIGKILL);               /* the peer is parked in pause() */
    waitpid(child, NULL, 0);
    return 0;
}
```

The exact numbers depend on your kernel's socket buffer defaults, so run it and read what you get
rather than expecting a particular count. What is invariant is the shape: the first write accepts far
less than the megabyte offered, and a later one accepts nothing at all and reports `EAGAIN`. A
program that had called `write` once and moved on would have sent a fraction of its response and
believed it was done.

`EAGAIN` is not a failure — it means "not right now". A real server either waits for the socket to
become writable with `select` or `poll`, or uses a blocking socket and lets the kernel do the waiting.
What it must not do is treat `EAGAIN` as an error and close the connection, because that turns a slow
client into a dropped request.

## The whole server, verified end to end

Here is the project, assembled. The path and response layers are the functions from the last two
chapters, unchanged; what is new is the socket layer and the loop around it.

The program runs a real server on a real port, and to keep the output reproducible it **forks**: the
child accepts and serves the requests, and the parent — which does all the printing — acts as the
client. That means one process produces a deterministic transcript of an actual HTTP conversation,
which is what makes this verifiable rather than merely plausible.

```c run
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* ---------- path layer ---------- */
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
    if (strcmp(dot, ".txt")  == 0) return "text/plain";
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

/* ---------- socket layer ---------- */
static int start_listening(int *port_out) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(0);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(fd, (struct sockaddr *)&addr, sizeof addr) < 0) { close(fd); return -1; }
    if (listen(fd, 16) < 0) { close(fd); return -1; }

    socklen_t len = sizeof addr;
    if (getsockname(fd, (struct sockaddr *)&addr, &len) < 0) { close(fd); return -1; }
    *port_out = ntohs(addr.sin_port);
    return fd;
}

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

static void serve_one(int listen_fd, const char *root) {
    int conn = accept(listen_fd, NULL, NULL);
    if (conn < 0) return;

    char request[4096];
    read_request(conn, request, sizeof request);

    char response[8192];
    size_t total = handle(root, request, response, sizeof response);

    size_t sent = 0;
    while (sent < total) {
        ssize_t w = write(conn, response + sent, total - sent);
        if (w <= 0) break;
        sent += (size_t)w;
    }
    close(conn);
}

/* ---------- driver ---------- */
static void make_fixture(const char *root) {
    mkdir(root, 0755);
    char path[512];
    snprintf(path, sizeof path, "%s/index.html", root);
    FILE *f = fopen(path, "wb");
    fputs("<h1>hello from serve</h1>\n", f);
    fclose(f);
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

int main(void) {
    const char *root = "docroot";
    make_fixture(root);

    int port = 0;
    int srv = start_listening(&port);
    if (srv < 0) { perror("listen"); return 1; }

    const char *requests[] = {
        "GET / HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /missing.txt HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /../etc/passwd HTTP/1.1\r\nHost: x\r\n\r\n",
        "PUT / HTTP/1.1\r\nHost: x\r\n\r\n",
    };
    size_t count = sizeof requests / sizeof requests[0];

    pid_t child = fork();
    if (child == 0) {
        for (size_t i = 0; i < count; i++) serve_one(srv, root);
        close(srv);
        _exit(0);
    }

    usleep(150000);                       /* let the child reach accept() */

    for (size_t i = 0; i < count; i++) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof addr);
        addr.sin_family = AF_INET;
        addr.sin_port = htons((uint16_t)port);
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        if (connect(c, (struct sockaddr *)&addr, sizeof addr) < 0) { perror("connect"); return 1; }

        if (write(c, requests[i], strlen(requests[i])) < 0) { perror("write"); return 1; }

        char got[8192];
        ssize_t total = 0, r;
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
```

```text
=== GET / HTTP/1.1 -> 109 bytes ===
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 26\r\n
Connection: close\r\n
\r\n
<h1>hello from serve</h1>\n
=== GET /missing.txt HTTP/1.1 -> 104 bytes ===
HTTP/1.1 404 Not Found\r\n
Content-Type: text/plain\r\n
Content-Length: 13\r\n
Connection: close\r\n
\r\n
no such file\n
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

Those are bytes that came back over a TCP connection from a server this program started. The
traversal attempt is refused, the unsupported method is refused, and the missing file produces a
complete `404` rather than a dropped connection.

One line in the driver is load-bearing and would be wrong in a real server: `usleep(150000)` before
the first `connect`. It is there because the parent and child race — the child has to reach `accept`
before the parent connects. On loopback the window is microseconds wide, and if the parent wins, the
`connect` still succeeds because the kernel completes the handshake into the listen backlog. The sleep
makes the transcript reproducible; a real server has no such line, because a client connecting to a
server that is not yet listening gets a refusal it can retry.

## When the peer disappears

A client can close the connection at any moment, including in the middle of your response. The first
`write` after that usually **succeeds** — the bytes go into the kernel's buffer and the error has not
come back yet. The failure surfaces on a later write, as `EPIPE`, and it also raises `SIGPIPE`:

```c run
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static int listening_socket(int *port_out) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(0);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    bind(fd, (struct sockaddr *)&addr, sizeof addr);
    listen(fd, 4);
    socklen_t len = sizeof addr;
    getsockname(fd, (struct sockaddr *)&addr, &len);
    *port_out = ntohs(addr.sin_port);
    return fd;
}

int main(void) {
    int port = 0;
    int srv = listening_socket(&port);

    /* Peer: connect, then hang up immediately without reading. */
    pid_t peer = fork();
    if (peer == 0) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in a;
        memset(&a, 0, sizeof a);
        a.sin_family = AF_INET;
        a.sin_port = htons((uint16_t)port);
        a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        connect(c, (struct sockaddr *)&a, sizeof a);
        close(c);
        _exit(0);
    }
    int conn = accept(srv, NULL, NULL);
    waitpid(peer, NULL, 0);
    usleep(150000);                     /* let the FIN reach us */

    /* Writer: a separate process, so its death cannot take this one down. */
    pid_t writer = fork();
    if (writer == 0) {
        signal(SIGPIPE, SIG_DFL);       /* the default: terminate */
        static char big[65536];
        memset(big, 'z', sizeof big);
        ssize_t first = write(conn, big, sizeof big);
        printf("  first write: %zd bytes accepted\n", first);
        fflush(stdout);
        usleep(150000);                 /* let the RST come back */
        errno = 0;
        ssize_t second = write(conn, big, sizeof big);
        printf("  second write: %zd, errno %d (%s)\n", second, errno, strerror(errno));
        printf("  this line is only reached if SIGPIPE is ignored\n");
        _exit(0);
    }

    int status = 0;
    waitpid(writer, &status, 0);

    if (WIFSIGNALED(status))
        printf("writer was killed by signal %d (SIGPIPE)\n", WTERMSIG(status));
    else
        printf("writer exited normally\n");

    close(conn);
    close(srv);
    return 0;
}
```

```text
  first write: 65536 bytes accepted
writer was killed by signal 13 (SIGPIPE)
```

The first write accepted all 65536 bytes even though the peer was already gone. The second never
returned: `SIGPIPE`'s default action is to terminate the process, and that is what happened to the
writer. Signal 13 is `SIGPIPE`, and the shell reports this as exit status 141 — 128 plus 13.

This is why a server dies "for no reason" the first time a user hits Stop in the browser. The fix is
one line, placed at startup:

```c
signal(SIGPIPE, SIG_IGN);
```

With `SIGPIPE` ignored, `write` returns `-1` with `errno == EPIPE` instead of killing the process, and
the send loop's `if (w <= 0) break;` handles it as the ordinary end of a connection. That is the
correct interpretation: the client hung up, the response is no longer wanted, and the server should
close the socket and accept the next connection.

Note what the demonstration had to do to be reproducible. `SIGPIPE` is **inherited**: if the program
that starts your server ignores it, so does the server, and the same code that dies under one
launcher survives under another. That is why this example forks a writer and explicitly restores
`SIG_DFL` — otherwise the answer would depend on the shell, and a lesson that changes with the
launcher is not a lesson. In your own code, set the disposition explicitly rather than relying on
what you inherited.

:::scenario The server that died every time someone closed a tab

A team ships an internal dashboard backed by a small C server. It runs for weeks. Then a colleague
closes a browser tab while a large report is still downloading, and the server is gone — no panic, no
log line, just a dead process and a `Connection refused` for everyone else.

The cause is `SIGPIPE`. Closing a tab closes the TCP connection, the server keeps writing the report,
and the write that discovers the closed socket raises `SIGPIPE`. The default action for that signal is
to terminate the process immediately, without unwinding, without flushing logs, and without running
any cleanup — so the only evidence is the exit status, which the supervisor recorded as `141`.

The diagnosis is one line of arithmetic: **141 = 128 + 13**, and signal 13 is `SIGPIPE`. Any process
that exits 141 was killed by a write to a socket nobody was reading.

:::solution Ignore SIGPIPE once, and treat a short write as a closed connection

```c run
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>

/* The send loop, with the two things a real server does. */
static int send_all(size_t total, ssize_t (*writer)(size_t, size_t), size_t *sent_out) {
    size_t sent = 0;
    while (sent < total) {
        ssize_t w = writer(total - sent, sent);
        if (w <= 0) {
            printf("  write returned %zd, errno %d (%s)\n", w, errno, strerror(errno));
            printf("  -> client is gone; close the socket and carry on\n");
            *sent_out = sent;
            return -1;
        }
        sent += (size_t)w;
    }
    *sent_out = sent;
    return 0;
}

static size_t g_available = 4096;

static ssize_t fake_writer(size_t want, size_t already) {
    (void)already;
    if (g_available == 0) { errno = EPIPE; return -1; }   /* peer vanished */
    size_t take = want < g_available ? want : g_available;
    g_available -= take;
    return (ssize_t)take;
}

int main(void) {
    signal(SIGPIPE, SIG_IGN);          /* the one line that keeps the process alive */

    size_t sent = 0;
    printf("sending 10000 bytes, peer will accept 4096 then vanish\n");
    if (send_all(10000, fake_writer, &sent) < 0)
        printf("  stopped after %zu of 10000 bytes\n", sent);
    printf("server is still running\n");
    return 0;
}
```

```text
sending 10000 bytes, peer will accept 4096 then vanish
  write returned -1, errno 32 (Broken pipe)
  -> client is gone; close the socket and carry on
  stopped after 4096 of 10000 bytes
server is still running
```

The server survived a client that disappeared mid-response, which is the only outcome that matters.
The response was not delivered — it could not be — but the process is alive to serve the next request,
and the connection is closed rather than leaked.

`signal(SIGPIPE, SIG_IGN)` goes once, at startup, before the first socket is created. Doing it inside
the request loop is too late for the request that was already in flight, and doing it per connection
is a waste of a syscall. The other half of the fix is the `w <= 0` check: ignoring `SIGPIPE` converts
a process-killing signal into an ordinary error return, and the error still has to be handled.

:::

:::pitfall A response buffer sized for the body alone

The response is written into one buffer, and that buffer has to hold the headers **and** the body. The
headers are not a fixed size — they grow with the length of `Content-Length` itself — so a buffer
sized as `body + 82` works until the body needs six digits.

Two habits prevent this. Size the buffer generously and check the return value of the function that
fills it, treating `0` as "did not fit" rather than "nothing to send". And remember that `write` is
called with a byte count, so an oversized buffer costs memory but never correctness — whereas an
undersized one costs a client that hangs.

The larger version of the same mistake is not buffering at all: reading a file whose size the client
chose into a `malloc` of that size. A static server should cap the body it is willing to serve, and
answer `413` above the cap. The cap belongs in the code that decides the size, not in a comment.

:::

## Key takeaways

- A socket is a file descriptor: `read`, `write` and `close` all apply, and it must be closed on every
  path out of the handler.
- Server startup is `socket`, `setsockopt(SO_REUSEADDR)`, `bind`, `listen`, then `getsockname` if you
  let the kernel choose the port.
- `htons`/`htonl` convert to network byte order and `ntohs`/`ntohl` convert back. On a little-endian
  machine `htons(8080)` is 36895, and forgetting the conversion is a bug that only appears on the
  other architecture.
- Every socket call takes `(struct sockaddr *)`, and the cast is required — `struct sockaddr_in` is a
  different type.
- `accept` returns a **new** descriptor and leaves the listening socket ready for the next client.
  Handle `EINTR` by continuing rather than exiting the loop.
- One `read` does not give you a whole request. Loop until `\r\n\r\n` appears, or the buffer fills.
- Read into `buf + used`, ask for `cap - 1 - used`, and NUL-terminate after every read.
- `write` may accept fewer bytes than you offer. Loop until everything is sent, and treat `w <= 0` as
  a closed connection.
- `EAGAIN` means "not now", not "error". Never close a connection because a socket was not ready.
- The first write to a peer that has already hung up usually **succeeds**; the failure surfaces on a
  later write as `EPIPE` plus `SIGPIPE`.
- `signal(SIGPIPE, SIG_IGN)` once at startup. Exit status **141 = 128 + 13** means a process was
  killed by a write to a socket nobody was reading.
- `SIGPIPE` is inherited, so a program's behaviour can depend on the launcher. Set it explicitly.

## Practice

- [ ] Write a program that creates a socket, binds to port 0 on loopback, and prints whether the
      kernel-assigned port is non-zero. Then do it twice in the same program and explain why the two
      ports differ.
- [ ] Write `static int port_from_args(int argc, char **argv)` that returns the port number given on
      the command line, or `8080` if none was given. Test it with no argument, with `8080`, and with
      something that is not a number.
- [ ] Write `static int send_all(int fd, const char *data, size_t len)` that loops until every byte is
      written, and returns `0` on success or `-1` on failure. Explain what it does when `write`
      returns 0.
- [ ] Extend `read_request` to reject a request whose headers exceed 8192 bytes with a `431` response,
      and explain why the loop's bound is what makes that possible.
- [ ] Write a program that starts a server, connects a client from a forked child, sends a request in
      two separate `write` calls with a delay between them, and shows that the server still answers
      correctly.
- [ ] Explain in two sentences why `signal(SIGPIPE, SIG_IGN)` must come before the first socket is
      created rather than inside the request handler.

## Solutions

:::solution Exercise 1

```c run
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static int bind_to_free_port(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(0);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (bind(fd, (struct sockaddr *)&addr, sizeof addr) < 0) { close(fd); return -1; }
    socklen_t len = sizeof addr;
    getsockname(fd, (struct sockaddr *)&addr, &len);
    printf("socket bound, port is %s\n",
           ntohs(addr.sin_port) > 0 ? "non-zero" : "zero");
    return fd;
}

int main(void) {
    int first = bind_to_free_port();
    int second = bind_to_free_port();
    printf("two sockets open at once: %s\n", (first >= 0 && second >= 0) ? "yes" : "no");
    close(first);
    close(second);
    return 0;
}
```

```text
socket bound, port is non-zero
socket bound, port is non-zero
two sockets open at once: yes
```

The two ports differ because `htons(0)` is not a port number — it is a request for one. The kernel
assigns an unused port at `bind` time and records it in the socket, which `getsockname` reads back.
That is why a test can start a server on a machine where other things are already listening, and why
the two sockets in this program can coexist: had both asked for 8080, the second `bind` would have
failed with `Address already in use` unless `SO_REUSEADDR` allowed it.

:::

:::solution Exercise 2

```c run
#include <stdio.h>
#include <stdlib.h>

static int port_from_args(int argc, char **argv) {
    if (argc < 2) return 8080;

    char *end = NULL;
    long value = strtol(argv[1], &end, 10);
    if (end == argv[1]) return 8080;          /* nothing numeric was read */
    if (*end != '\0')   return 8080;          /* trailing junk: "8080abc" */
    if (value < 1 || value > 65535) return 8080;
    return (int)value;
}

int main(void) {
    char *none[]    = { "serve" };
    char *good[]    = { "serve", "9000" };
    char *junk[]    = { "serve", "eighty" };
    char *partial[] = { "serve", "8080abc" };
    char *too_big[] = { "serve", "70000" };
    char *zero[]    = { "serve", "0" };

    printf("no argument  -> %d\n", port_from_args(1, none));
    printf("9000         -> %d\n", port_from_args(2, good));
    printf("eighty       -> %d\n", port_from_args(2, junk));
    printf("8080abc      -> %d\n", port_from_args(2, partial));
    printf("70000        -> %d\n", port_from_args(2, too_big));
    printf("0            -> %d\n", port_from_args(2, zero));
    return 0;
}
```

```text
no argument  -> 8080
9000         -> 9000
eighty       -> 8080
8080abc      -> 8080
70000        -> 8080
0            -> 8080
```

The `8080abc` case is the one worth studying. `strtol` parses the leading digits and leaves `end`
pointing at the `a`, so the `*end != '\0'` check is what rejects it — and without that check,
`8080abc` would silently become port 8080, which is worse than an error because it looks like it
worked. The `end == argv[1]` check catches the other direction: if nothing numeric was read at all,
`strtol` leaves `end` at the start of the string, and there is no value to inspect.

`0` is rejected because asking for port 0 means "kernel, choose one". That is exactly what this
chapter's own server does on purpose, but it is never what a user typing a port number intends, so a
command-line parser should refuse it while the code keeps the ability to use it.

The function returns `8080` for every invalid input rather than an error code. That is a reasonable
choice for a default port and a bad one for a value where "invalid" and "the default" must be
distinguished — the caller cannot tell "the user asked for 8080" from "the user typed nonsense". If
that distinction matters, return `-1` for invalid and let `main` decide.

:::

:::solution Exercise 3

```c run
#include <errno.h>
#include <stdio.h>
#include <string.h>

/* A stand-in for write(), so the loop can be tested without a socket. */
static size_t g_capacity = 1000;
static int    g_fail_after = -1;

static ssize_t fake_write(size_t want) {
    if (g_fail_after == 0) { errno = EPIPE; return -1; }
    if (g_fail_after > 0) g_fail_after--;
    if (g_capacity == 0) { errno = EAGAIN; return -1; }
    size_t take = want < g_capacity ? want : g_capacity;
    g_capacity -= take;
    return (ssize_t)take;
}

static int send_all(size_t len, size_t *sent_out) {
    size_t sent = 0;
    while (sent < len) {
        ssize_t w = fake_write(len - sent);
        if (w == 0) { printf("  write returned 0 -> treat as failure\n"); *sent_out = sent; return -1; }
        if (w < 0)  { printf("  write returned %zd, errno %d\n", w, errno); *sent_out = sent; return -1; }
        sent += (size_t)w;
    }
    *sent_out = sent;
    return 0;
}

int main(void) {
    size_t sent = 0;

    g_capacity = 1000; g_fail_after = -1;
    printf("capacity 1000, want 2500: %s\n", send_all(2500, &sent) == 0 ? "all sent" : "stopped");
    printf("  sent %zu of 2500\n", sent);

    g_capacity = 1000; g_fail_after = 1;
    printf("peer vanishes after one write: %s\n", send_all(2500, &sent) == 0 ? "all sent" : "stopped");
    printf("  sent %zu of 2500\n", sent);
    return 0;
}
```

```text
  write returned -1, errno 35
capacity 1000, want 2500: stopped
  sent 1000 of 2500
  write returned -1, errno 32
peer vanishes after one write: stopped
  sent 1000 of 2500
```

Read the order of those lines carefully, because it is not the order the source suggests. The
`write returned` line appears **before** the `capacity 1000` line it belongs to, even though the
`printf` for `capacity 1000` comes first in the file.

The reason is argument evaluation. `printf("capacity ... %s\n", send_all(2500, &sent) == 0 ? ... )`
has to evaluate `send_all(...)` before `printf` can do anything — and `send_all` prints. So the
inner output is produced first, and then the outer line is emitted with its already-computed string.
Nothing is out of order from the compiler's point of view; it is a reminder that a function called as
an argument runs before the call it is an argument to. A debugging `printf` placed inside an
expression like this will always appear to be out of place.

The `errno` values differ for a reason worth naming. The first case ends in `35`, which is `EAGAIN`
on this platform — the socket is full but not broken. The second ends in `32`, which is `EPIPE` — the
peer is gone. Treating those two as the same thing is the difference between a server that waits for
a slow client and one that drops it.

The first case is the one to read most carefully. A capacity of 1000 against 2500 bytes should take
three writes — 1000, 1000, 500 — and succeed, but it stopped after one. The stand-in never refills its
capacity, so it models a socket that is permanently full rather than one that is temporarily full.
That is the difference between this exercise and a real server: a real socket becomes writable again
once the peer reads, and the real loop would wait for that rather than give up.

The second case is the correct behaviour for a vanished peer: partial data sent, failure reported,
the count preserved so the caller can log exactly how much reached the client. Returning `0` from
`write` is treated as failure too — a zero-length write means the connection is gone, and a loop that
treated it as success would spin forever.

:::

:::solution Exercise 4

```c run
#include <stdio.h>
#include <string.h>

#define MAX_HEADERS 8192

static int read_request_from(const char *chunks[], size_t nchunks,
                             char *buf, size_t cap, size_t *used_out) {
    size_t used = 0;
    for (size_t i = 0; i < nchunks; i++) {
        size_t n = strlen(chunks[i]);
        if (used + n + 1 > cap) break;
        memcpy(buf + used, chunks[i], n);
        used += n;
        buf[used] = '\0';
        if (strstr(buf, "\r\n\r\n") != NULL) break;
    }
    *used_out = used;
    return used >= MAX_HEADERS ? 431 : 200;
}

int main(void) {
    static char buf[16384];

    const char *small[] = { "GET / HTTP/1.1\r\n", "Host: x\r\n\r\n" };
    const char *split[] = { "GET / HT", "TP/1.1\r\nHost: x", "\r\n\r\n" };

    static char huge[9000];
    memset(huge, 'a', sizeof huge - 1);
    huge[sizeof huge - 1] = '\0';
    const char *over[] = { huge };

    size_t used = 0;
    printf("small request  -> %d, %zu bytes buffered\n",
           read_request_from(small, 2, buf, sizeof buf, &used), used);
    printf("split request  -> %d, %zu bytes buffered\n",
           read_request_from(split, 3, buf, sizeof buf, &used), used);
    printf("oversized      -> %d, %zu bytes buffered\n",
           read_request_from(over, 1, buf, sizeof buf, &used), used);
    return 0;
}
```

```text
small request  -> 200, 27 bytes buffered
split request  -> 200, 27 bytes buffered
oversized      -> 431, 8999 bytes buffered
```

The second line is the point: a request delivered in three fragments produces exactly the same result
as one delivered whole, because the loop re-checks for `\r\n\r\n` after every fragment rather than
only at the end. The third line is what the bound buys — 8999 bytes with no terminator is detected as
oversized and answered with `431 Request Header Fields Too Large`, instead of being read until the
buffer overflows or the client gives up.

The bound has to be checked *before* the copy, not after. A loop that copies first and checks the
length second has already written past the end of the buffer by the time it notices.

:::

:::solution Exercise 5

```c run
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(void) {
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    int one = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof addr);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(0);
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    bind(srv, (struct sockaddr *)&addr, sizeof addr);
    listen(srv, 4);
    socklen_t slen = sizeof addr;
    getsockname(srv, (struct sockaddr *)&addr, &slen);
    int port = ntohs(addr.sin_port);

    pid_t child = fork();
    if (child == 0) {
        int conn = accept(srv, NULL, NULL);
        char buf[1024];
        size_t used = 0;
        while (used + 1 < sizeof buf) {
            ssize_t n = read(conn, buf + used, sizeof buf - 1 - used);
            if (n <= 0) break;
            used += (size_t)n;
            buf[used] = '\0';
            if (strstr(buf, "\r\n\r\n") != NULL) break;
        }
        printf("server saw %zu bytes and %s the blank line\n", used,
               strstr(buf, "\r\n\r\n") ? "found" : "missed");
        const char *resp = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok";
        write(conn, resp, strlen(resp));
        close(conn);
        close(srv);
        fflush(stdout);                /* _exit skips the flush; stdout is buffered */
        _exit(0);
    }

    usleep(150000);
    int c = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_port = htons((uint16_t)port);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    connect(c, (struct sockaddr *)&a, sizeof a);

    const char *part_1 = "GET / HTTP/1.1\r\n";
    const char *part_2 = "Host: x\r\n\r\n";
    write(c, part_1, strlen(part_1));
    usleep(80000);                     /* a deliberate pause mid-request */
    write(c, part_2, strlen(part_2));

    char got[512];
    ssize_t total = read(c, got, sizeof got - 1);
    if (total < 0) total = 0;
    got[total] = '\0';
    printf("client got: %.*s\n", (int)strcspn(got, "\r"), got);
    close(c);
    waitpid(child, NULL, 0);
    return 0;
}
```

```text
server saw 27 bytes and found the blank line
client got: HTTP/1.1 200 OK
```

The client sent the request in two pieces 80 milliseconds apart, and the server answered correctly.
That is the whole point of `read_request`: it keeps reading until it sees the blank line, so a request
that arrives in two packets is indistinguishable from one that arrives in one.

One line in the child is easy to miss and necessary: `fflush(stdout)` before `_exit(0)`. `_exit` is
the raw system call — it terminates the process immediately without running `atexit` handlers or
flushing stdio buffers — whereas `exit` flushes first. The child's `printf` output lives in a buffer,
and without the flush it is discarded when the process ends. The symptom is a program that prints
correctly when run from a terminal (where stdout is line-buffered) and silently loses output when
redirected to a pipe or a file (where it is block-buffered), which is exactly how a test harness runs
it.

A server that read once would have seen `GET / HTTP/1.1\r\n` — 16 bytes with no blank line — and
answered `400`. The bug would be invisible on loopback with a fast client and appear only on a real
network, which is the worst kind of bug to ship.

:::

:::solution Exercise 6

`signal(SIGPIPE, SIG_IGN)` changes the process's disposition for that signal, and a disposition is a
property of the process, not of a socket or a connection. It has to be in place *before* the write
that would raise the signal, and since any connection at any time can be the one whose peer has
vanished, the only safe moment is before the first socket is created.

Setting it inside the request handler is too late for the request already in flight: the write that
raises `SIGPIPE` is the one that discovers the closed connection, and if the handler has not yet
ignored the signal, the process is already gone. It is also the wrong place architecturally — the
signal disposition is a property of the whole server, and code that sets global state per request is
code that behaves differently depending on which request ran first.

:::
