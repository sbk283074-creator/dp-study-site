---
chapter: 27
part: 5
title: Porting serve to C++
summary: Rebuild the Part III file server in C++ — an RAII socket, std::string instead of buffers and size arguments, and a Server class that owns its connections — then prove the responses are byte-for-byte the same.
minutes: 75
tags: [raii, socket, move-semantics, std-string, unique_ptr, porting, project, curl]
---

Chapter 17's server works. Five `.c` files, a Makefile, a self-test, and a hardening checklist it
passes. Nothing in this part changes what it *does*; everything changes what it *cannot do*. The C
version is correct because every path out of every function goes through the cleanup — and that is a
property of your discipline, which lasts exactly as long as your attention does. The C++ version makes
it a property of the types.

Two things survive the port unchanged: the socket calls (`socket`, `bind`, `listen`, `accept`, `read`,
`write`, `close`) and the bytes on the wire. HTTP does not care what language produced it, and a
response is a response. What goes away is the category of code that exists only to undo something —
the `close(conn)` on every exit path, the `free(body)`, and the `outsz` parameter with the
`if (it did not fit) return 0` branch that always follows it.

By the end of this chapter you will have the same server answering the same requests, and you will be
able to point at three specific classes of bug that the compiler now refuses to let you write.

## The descriptor that leaks on the early return

Here is the shape of `serve_one` from Chapter 17, reduced to what matters:

```c
int serve_one(int listen_fd, const char *root) {
    int conn = accept(listen_fd, NULL, NULL);
    if (conn < 0) return -1;

    char request[REQUEST_MAX];
    read_request(conn, request, sizeof request);

    char response[RESPONSE_MAX];
    size_t total = handle(root, request, response, sizeof response);
    if (total == 0) { /* ... */ }
    send_all(conn, response, total);

    close(conn);                    /* one statement, at the end */
    return 0;
}
```

`close(conn)` is a statement you have to *reach*. Today you reach it. Next month someone adds a
`Connection: keep-alive` branch that returns early, and the descriptor is not closed. The program does
not crash, prints nothing, and passes its self-test. That is the whole problem with manual cleanup: the
failure is silent and it accumulates.

The measurement below counts this process's open descriptors by listing `/dev/fd` — which is a real
count, not a guess — and reports the *difference* across one call. Only differences are meaningful: the
absolute number depends on what the shell handed the process.

```cpp run
#include <cstdio>
#include <dirent.h>
#include <unistd.h>
#include <sys/socket.h>

/* Count the descriptors this process has open, by listing /dev/fd. The
   absolute number depends on what the shell handed us, so only differences
   between two calls mean anything. */
static int open_count() {
    DIR *d = ::opendir("/dev/fd");
    if (d == nullptr) return -1;
    int n = 0;
    while (::readdir(d) != nullptr) n++;
    ::closedir(d);
    return n - 3;                      /* "." , ".." , and the directory itself */
}

/* One connection: we keep fds[0] and drop the peer end. */
static int make_connection() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) return -1;
    ::close(fds[1]);
    return fds[0];
}

/* The C shape: the descriptor is closed by hand, at the end. */
static void serve_c(int reject) {
    int conn = make_connection();
    if (conn < 0) return;
    if (reject) return;                /* the early exit: close() never runs */
    ::close(conn);
}

class Socket {
public:
    explicit Socket(int fd) : fd_(fd) {}
    ~Socket() { if (fd_ >= 0) ::close(fd_); }
    Socket(const Socket &) = delete;
    Socket &operator=(const Socket &) = delete;
private:
    int fd_;
};

/* The C++ shape: the same early exit, and the descriptor is still closed. */
static void serve_cpp(int reject) {
    int conn = make_connection();
    if (conn < 0) return;
    Socket guard(conn);
    if (reject) return;                /* guard's destructor runs here */
}

int main() {
    int before = open_count();
    serve_c(1);
    std::printf("C   request refused   %+d descriptor(s)\n", open_count() - before);

    before = open_count();
    serve_c(0);
    std::printf("C   request answered  %+d descriptor(s)\n", open_count() - before);

    before = open_count();
    serve_cpp(1);
    std::printf("C++ request refused   %+d descriptor(s)\n", open_count() - before);

    before = open_count();
    serve_cpp(0);
    std::printf("C++ request answered  %+d descriptor(s)\n", open_count() - before);
    return 0;
}
```

```text
C   request refused   +1 descriptor(s)
C   request answered  +0 descriptor(s)
C++ request refused   +0 descriptor(s)
C++ request answered  +0 descriptor(s)
```

Four calls, four measurements, and the difference between the two implementations is a single line:
`Socket guard(conn);`. In the C version the early `return` is a leak; in the C++ version the same
early `return` runs a destructor.

The reason this matters more than it looks is what a leaked descriptor does to a *server*. Nothing, at
first. Then, after enough refused requests, `accept` starts failing with `EMFILE` — "too many open
files" — and the server stops answering anybody, with no log line, no crash, and no symptom that
appears earlier. `ulimit -n` is 256 by default on macOS and 1024 on most Linux systems, so the number
of requests you can leak before the server dies is small enough to reach in an afternoon of testing
and large enough that the cause is nowhere near the symptom. Chapter 17's checklist asked "does every
path out of the handler release what it acquired?" — and the answer, in C, is a claim about every
future edit. In C++ it is a claim about the type.

## The Socket class

So make the type. This is the RAII socket the rest of the part is built on — a descriptor that closes
itself, that cannot be copied, and that can be moved:

```cpp run
#include <cstdio>
#include <stdexcept>
#include <unistd.h>
#include <sys/socket.h>

class Socket {
public:
    Socket(int fd, const char *name) : fd_(fd), name_(name) {}

    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
            std::printf("closed %s\n", name_);
        }
    }

    Socket(const Socket &) = delete;
    Socket &operator=(const Socket &) = delete;

    Socket(Socket &&other) noexcept : fd_(other.fd_), name_(other.name_) {
        other.fd_ = -1;
    }

    int fd() const { return fd_; }

private:
    int fd_;
    const char *name_;
};

int main() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) {
        std::printf("socketpair failed\n");
        return 1;
    }

    Socket reader(fds[0], "reader");
    {
        Socket writer(fds[1], "writer");
        const char *msg = "ping";
        if (::write(writer.fd(), msg, 4) != 4) std::printf("short write\n");

        char buf[8] = {};
        ssize_t n = ::read(reader.fd(), buf, sizeof buf);
        std::printf("read %ld bytes: %s\n", (long)n, buf);
    }
    std::printf("writer went out of scope\n");
    return 0;
}
```

```text
read 4 bytes: ping
closed writer
writer went out of scope
closed reader
```

Read the order of those last three lines, because it is the whole idea. `writer` is destroyed at the
end of its block, so it prints `closed writer` *before* the `printf` on the next line runs. `reader`
lives to the end of `main`, so its `closed reader` comes last. Nobody wrote a `close` statement; the
scope did it.

That `name_` member is not decoration, and it is worth understanding why a demonstration has it. The
obvious version of this program prints the descriptor number — `closed fd 8` — and that number is
different on every run, because it depends on which descriptors the shell happened to hand the
process. A transcript that changes between runs is not evidence of anything; it is a program you have
to take on faith. Naming the sockets makes the output identical every time, which is what makes the
order visible. When you write a test that is supposed to *prove* something, this is the kind of
detail that decides whether it does.

Four declarations turn a plain class into a resource type:

| Declaration | What it buys |
|---|---|
| `~Socket()` | The resource is released when the scope ends, including on an early `return` or a thrown exception. |
| `Socket(const Socket &) = delete;` | Two `Socket` objects can never hold the same descriptor. |
| `Socket &operator=(const Socket &) = delete;` | Same, for assignment. |
| `Socket(Socket &&other) noexcept` | Ownership can be handed on, and the source is left inert. |

The second and third are the ones people forget, and the reason they matter is worse than a leak. If
`Socket` were copyable, this would compile:

```cpp bad
#include <unistd.h>
#include <sys/socket.h>

class Socket {
public:
    explicit Socket(int fd) : fd_(fd) {}
    ~Socket() { if (fd_ >= 0) ::close(fd_); }
    Socket(const Socket &) = delete;
    Socket &operator=(const Socket &) = delete;
    Socket(Socket &&other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    int fd() const { return fd_; }

private:
    int fd_;
};

int main() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) return 1;
    Socket a(fds[0]);
    Socket b = a;
    (void)b;
    ::close(fds[1]);
    return 0;
}
```

```text
error: call to deleted constructor of 'Socket'
```

The compiler stops it at the point of the mistake, and the message names the line in the class where
you said so. Without those two `= delete` lines the program would compile, and both destructors would
call `close` on the same number. The first `close` is harmless. The second is not: by then the
descriptor may have been recycled by something else in the program, so you close a connection that
belongs to a different part of the server. That is the failure mode to keep in mind — **a double close
is worse than a leak**, because a leak wastes a resource and a double close corrupts an unrelated one.

Move, by contrast, is safe and necessary, because a function has to be able to *return* a socket:

```cpp run
#include <cstdio>
#include <utility>
#include <unistd.h>
#include <sys/socket.h>

class Socket {
public:
    Socket(int fd, const char *name) : fd_(fd), name_(name) {}
    ~Socket() {
        if (fd_ >= 0) { ::close(fd_); std::printf("closed %s\n", name_); }
    }
    Socket(const Socket &) = delete;
    Socket &operator=(const Socket &) = delete;
    Socket(Socket &&other) noexcept : fd_(other.fd_), name_(other.name_) {
        other.fd_ = -1;
    }
    int fd() const { return fd_; }

private:
    int fd_;
    const char *name_;
};

static Socket take(Socket s) { return s; }

int main() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) return 1;

    Socket s(fds[0], "the socket");
    Socket moved = std::move(s);
    std::printf("after the move:      s is %s, moved is %s\n",
                s.fd() < 0 ? "empty" : "open", moved.fd() < 0 ? "empty" : "open");

    Socket handed = take(std::move(moved));
    std::printf("after passing it on: moved is %s, handed is %s\n",
                moved.fd() < 0 ? "empty" : "open", handed.fd() < 0 ? "empty" : "open");

    ::close(fds[1]);
    return 0;
}
```

```text
after the move:      s is empty, moved is open
after passing it on: moved is empty, handed is open
closed the socket
```

Only one `closed` line, though three `Socket` objects were constructed. That is what the
`other.fd_ = -1` in the move constructor buys: the moved-from object still exists and its destructor
still runs, but `fd_` is `-1`, so the destructor does nothing. **A moved-from object must be left in a
state where destroying it is harmless** — for a resource type that means "empty", and the check
`if (fd_ >= 0)` is what makes empty safe.

The pay-off is that `Socket` can be returned by value from a factory function. `Listener::accept_one`
in the project below does exactly that, and the return costs nothing but a pointer copy — no duplicate
descriptor is ever created, so no `close` is ever duplicated.

## Strings instead of buffers and size arguments

The C server's response builder takes six arguments, three of which exist only to describe storage:

```c
size_t build_response(const char *status, const char *type,
                      const char *body, size_t body_len,
                      char *out, size_t outsz);
```

`out` and `outsz` are there because the function cannot allocate. `body_len` is there because the
function cannot ask the body how long it is. That last one is the dangerous argument, and the
demonstration below is the reason:

```cpp run
#include <cstdio>
#include <cstring>
#include <string>

/* C: the caller supplies a buffer, its size, AND the body length. */
static std::size_t build_c(const char *status, const char *type,
                           const char *body, std::size_t body_len,
                           char *out, std::size_t outsz) {
    const int n = std::snprintf(out, outsz,
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Connection: close\r\n"
        "\r\n", status, type, body_len);
    if (n < 0 || static_cast<std::size_t>(n) >= outsz) return 0;
    const std::size_t header = static_cast<std::size_t>(n);
    if (header + body_len > outsz) return 0;
    std::memcpy(out + header, body, body_len);
    return header + body_len;
}

/* C++: no buffer, no size, and the length is not the caller's to get wrong. */
static std::string build_cpp(const std::string &status, const std::string &type,
                             const std::string &body) {
    return "HTTP/1.1 " + status + "\r\n"
           "Content-Type: " + type + "\r\n"
           "Content-Length: " + std::to_string(body.size()) + "\r\n"
           "Connection: close\r\n"
           "\r\n" + body;
}

static std::size_t declared_length(const std::string &response) {
    const std::string key = "Content-Length: ";
    const std::size_t at = response.find(key) + key.size();
    return static_cast<std::size_t>(std::stoul(response.substr(at)));
}

int main() {
    const std::string page(100000, 'x');          /* a 100 KB page */

    char small[256];
    const std::size_t n = build_c("200 OK", "text/html", page.data(), page.size(),
                                  small, sizeof small);
    std::printf("C   into a 256-byte buffer: %s\n", n == 0 ? "did not fit" : "built");

    const std::string r = build_cpp("200 OK", "text/html", page);
    std::printf("C++ with no buffer at all:  built, %zu bytes\n", r.size());

    /* A body that is not text: eight bytes, one of them a NUL. */
    const std::string png("abc\0defg", 8);

    char out[256];
    const std::size_t m = build_c("200 OK", "image/png", png.data(),
                                  std::strlen(png.c_str()), out, sizeof out);
    const std::string c_out(out, m);
    const std::string cpp_out = build_cpp("200 OK", "image/png", png);

    std::printf("the body is %zu bytes, strlen() says %zu\n",
                png.size(), std::strlen(png.c_str()));
    std::printf("C   declares Content-Length: %zu, response is %zu bytes\n",
                declared_length(c_out), c_out.size());
    std::printf("C++ declares Content-Length: %zu, response is %zu bytes\n",
                declared_length(cpp_out), cpp_out.size());
    return 0;
}
```

```text
C   into a 256-byte buffer: did not fit
C++ with no buffer at all:  built, 100087 bytes
the body is 8 bytes, strlen() says 3
C   declares Content-Length: 3, response is 85 bytes
C++ declares Content-Length: 8, response is 90 bytes
```

Three things to take from that transcript.

First, the C version cannot serve a 100 KB page into a 256-byte buffer, and it says so by returning
`0`. That `0` is a value the caller has to check, which is why Chapter 17's `serve_one` carries this:

```c
size_t total = handle(root, request, response, sizeof response);
if (total == 0) {
    total = error_page("500 Internal Server Error", "response too large\n",
                       response, sizeof response);
}
```

In the C++ version that branch does not exist, because `build_response` returns a `std::string` and a
`std::string` cannot fail to be big enough. The only size limit left is the one you deliberately
impose with `MAX_BODY_BYTES`, and that is a policy decision rather than a buffer constraint.

Second, the body length is now a *fact about the body* rather than a number the caller supplies.
`body.size()` is the length by definition, so the header and the payload cannot disagree. In the C
version they are two independent values, and the demo shows what happens when they diverge: a PNG body
of eight bytes whose third byte is a NUL gets `strlen`'d to three, so the response declares
`Content-Length: 3` and is five bytes shorter than it should be. A client that trusts the header sees a
truncated image; a client that waits for more bytes than were declared hangs until it times out. This
is the failure Chapter 17's checklist called "a truncated body with a `Content-Length` for the full
size is the failure mode that hangs clients" — and the fix is not to be more careful with `strlen`, it
is to remove the second source of truth.

Third, `+` on `std::string` allocates and concatenates, so the response is built by describing it
rather than by writing into storage you sized in advance. It is not faster than `memcpy`; it is
impossible to get wrong.

:::note `c++` and `clang++` are the same compiler

The project's Makefile sets `CXX = c++`, which is the portable name. On this machine `c++` is a
symlink to `clang++`, so the two produce identical binaries. `g++` is the GNU equivalent and the
Makefile works unchanged on a Linux box where `c++` points at it. The compiler names in this book are
interchangeable as long as the standard is set explicitly, which is what `-std=c++17` does.

:::

## The pointer you must not keep

Returning a `std::string` from `read_file` rather than a `char *` changes who owns the bytes, and it
removes a whole category of C bug. But it introduces one of its own, and it is the single most common
way a ported program breaks:

```cpp run-san-catch
#include <cstdio>
#include <string>

int main() {
    std::string s(64, 'a');
    const char *p = s.c_str();
    for (int i = 0; i < 100; i++) s += " more text";
    std::printf("p still starts with %c\n", p[0]);
    return 0;
}
```

```text
ERROR: AddressSanitizer: heap-use-after-free
```

`c_str()` does not give you a string. It gives you a pointer to the string's internal buffer, and that
buffer moves whenever the string grows past its capacity. After a hundred appends the buffer has been
reallocated several times, so `p` points at memory that has been freed and possibly handed to something
else.

The C version of this code had the same hazard, but it was *visible*: `read_file` returned a `char *`
and the documentation said "caller frees", so you knew the pointer was a resource with a lifetime. The
C++ version hides it, because the `std::string` is still alive and still holds the right text — it is
only the pointer that died. The rule that keeps you out of it:

- **Take `const std::string &` as a parameter.** Never `const char *` for something you will store.
- **Call `.c_str()` at the call site**, on the same line as the C function that needs it, and never
  keep the result.
- **Store a `std::string`**, not a pointer into one.

The one exception is passing to a C API — `std::fopen(path.c_str(), "rb")` — where the pointer is used
and discarded within the same expression, before anything can reallocate.

## Resources that are not descriptors

`std::unique_ptr` from Chapter 22 is the tool for a resource you acquire once and release in one place,
and `std::FILE *` is exactly that:

```cpp run
#include <cstdio>
#include <memory>

int main() {
    std::unique_ptr<std::FILE, int (*)(std::FILE *)> log(std::fopen("out.txt", "w"), std::fclose);
    std::printf("file is %s\n", log ? "open" : "closed");
    return 0;
}
```

```text
file is open
```

The second template argument is the deleter, and here it is a *function pointer* — `int (*)(std::FILE *)`
— because `std::fclose` is an ordinary C function. Writing `decltype(&std::fclose)` instead produces
the same type; naming it explicitly is more readable and is what the project does.

So far so good. Now the temptation: a socket is a resource too, so why not

```cpp bad
#include <memory>
#include <unistd.h>

int main() {
    std::unique_ptr<int, int (*)(int)> owned(new int(5), ::close);
    return 0;
}
```

```text
error: cannot initialize a parameter of type 'int' with an lvalue of type 'pointer' (aka 'int *')
```

Because `unique_ptr<T, D>` calls `D` with a `T *`, and `close` takes an `int`. There is no `T` you can
write that makes `int (*)(int)` the right deleter, because a file descriptor is not a pointer to
anything — it is a handle, an index into a table the kernel owns. `unique_ptr` owns things you reach
*through* a pointer; a descriptor is not one of those things.

That is why `Socket` is a class rather than a `unique_ptr` alias. It is the same idea — one owner, one
release, move but never copy — implemented for a resource that the standard library has no wrapper for.
When you meet a handle like this (a file descriptor, a window handle, a database connection id), the
answer is a small RAII class of your own, and it is about twenty lines.

The error message itself is worth a second look, because it is the kind of diagnostic that makes people
give up on C++. It points into a library header, mentions `reset()`, and never says "you cannot own a
file descriptor with a `unique_ptr`". The lesson is not that the compiler is unhelpful; it is that when
a template error points somewhere you did not write, the problem is a *type* you asked for that does not
make sense. Read the first `error:` line, which is the one that names the mismatch, and ignore the
`note:` lines until you have understood it.

## The ported project

Everything above, assembled into the same four layers Chapter 17 had. `path` has become `files`, and
the `Server` class now owns the listener and the document root:

```cpp make-files
/* ===== socket.h ===== */
#ifndef SOCKET_H
#define SOCKET_H

#include <cstddef>
#include <string>

/* An owned file descriptor. The destructor closes it, so every exit from a
   function releases it - including the early returns that forget. */
class Socket {
public:
    Socket() = default;
    explicit Socket(int fd) : fd_(fd) {}
    ~Socket();

    Socket(const Socket &) = delete;
    Socket &operator=(const Socket &) = delete;
    Socket(Socket &&other) noexcept;
    Socket &operator=(Socket &&other) noexcept;

    bool valid() const { return fd_ >= 0; }
    int fd() const { return fd_; }

    /* Read until `got` contains `marker`, the peer closes, or `cap` bytes. */
    std::string read_until(const std::string &marker, std::size_t cap) const;

    /* Write every byte, or throw. A short write is normal, not an error. */
    void write_all(const std::string &data) const;

private:
    int fd_ = -1;
};

/* A bound, listening socket. Asking for port 0 lets the kernel choose, and
   port() reports the one it chose. */
class Listener {
public:
    explicit Listener(int port);
    int fd() const { return sock_.fd(); }
    int port() const { return port_; }
    Socket accept_one() const;

private:
    Socket sock_;
    int port_ = 0;
};

#endif
/* ===== socket.cpp ===== */
#include "socket.h"

#include <stdexcept>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

Socket::~Socket() {
    if (fd_ >= 0) ::close(fd_);
}

Socket::Socket(Socket &&other) noexcept : fd_(other.fd_) {
    other.fd_ = -1;
}

Socket &Socket::operator=(Socket &&other) noexcept {
    if (this != &other) {
        if (fd_ >= 0) ::close(fd_);
        fd_ = other.fd_;
        other.fd_ = -1;
    }
    return *this;
}

std::string Socket::read_until(const std::string &marker, std::size_t cap) const {
    std::string got;
    char buf[1024];
    while (got.size() < cap) {
        const ssize_t n = ::read(fd_, buf, sizeof buf);
        if (n <= 0) break;
        got.append(buf, static_cast<std::size_t>(n));
        if (got.find(marker) != std::string::npos) break;
    }
    return got;
}

void Socket::write_all(const std::string &data) const {
    std::size_t sent = 0;
    while (sent < data.size()) {
        const ssize_t w = ::write(fd_, data.data() + sent, data.size() - sent);
        if (w <= 0) throw std::runtime_error("write failed");
        sent += static_cast<std::size_t>(w);
    }
}

Listener::Listener(int port) : port_(port) {
    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) throw std::runtime_error("socket() failed");
    sock_ = Socket(fd);                    /* the move takes ownership */

    const int one = 1;
    ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (::bind(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) < 0)
        throw std::runtime_error("bind() failed");
    if (::listen(fd, 16) < 0)
        throw std::runtime_error("listen() failed");

    socklen_t len = sizeof addr;
    if (::getsockname(fd, reinterpret_cast<sockaddr *>(&addr), &len) < 0)
        throw std::runtime_error("getsockname() failed");
    port_ = ntohs(addr.sin_port);
}

Socket Listener::accept_one() const {
    const int conn = ::accept(sock_.fd(), nullptr, nullptr);
    if (conn < 0) throw std::runtime_error("accept() failed");
    return Socket(conn);
}
/* ===== files.h ===== */
#ifndef FILES_H
#define FILES_H

#include <cstddef>
#include <optional>
#include <string>

const char *mime_type(const std::string &path);

/* The file's bytes, or nothing if it cannot be read whole or exceeds max_bytes. */
std::optional<std::string> read_file(const std::string &path, std::size_t max_bytes);

/* Percent-decode a target. Nothing if the escape is malformed or encodes NUL. */
std::optional<std::string> percent_decode(const std::string &in);

/* Join root and an already-decoded target. Nothing if it would leave the root. */
std::optional<std::string> resolve_path(const std::string &root, const std::string &target);

#endif
/* ===== files.cpp ===== */
#include "files.h"

#include <cstdio>
#include <cstring>
#include <memory>

namespace {

int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* A FILE* that closes itself. The deleter is a function pointer, so the
   unique_ptr knows exactly which C function releases the resource. */
using FilePtr = std::unique_ptr<std::FILE, int (*)(std::FILE *)>;

}  // namespace

const char *mime_type(const std::string &path) {
    const std::size_t dot = path.rfind('.');
    if (dot == std::string::npos) return "application/octet-stream";
    const std::string ext = path.substr(dot);
    if (ext == ".html" || ext == ".htm") return "text/html";
    if (ext == ".css") return "text/css";
    if (ext == ".js") return "text/javascript";
    if (ext == ".txt") return "text/plain";
    if (ext == ".json") return "application/json";
    if (ext == ".png") return "image/png";
    return "application/octet-stream";
}

std::optional<std::string> read_file(const std::string &path, std::size_t max_bytes) {
    FilePtr f(std::fopen(path.c_str(), "rb"), std::fclose);
    if (!f) return std::nullopt;

    if (std::fseek(f.get(), 0, SEEK_END) != 0) return std::nullopt;
    const long size = std::ftell(f.get());
    if (size < 0) return std::nullopt;
    if (static_cast<unsigned long>(size) > max_bytes) return std::nullopt;
    std::rewind(f.get());

    std::string body(static_cast<std::size_t>(size), '\0');
    if (!body.empty()) {
        const std::size_t got = std::fread(body.data(), 1, body.size(), f.get());
        if (got != body.size()) return std::nullopt;
    }
    return body;
}

std::optional<std::string> percent_decode(const std::string &in) {
    std::string out;
    out.reserve(in.size());
    for (std::size_t i = 0; i < in.size(); i++) {
        unsigned char c = static_cast<unsigned char>(in[i]);
        if (c == '%') {
            if (i + 2 >= in.size()) return std::nullopt;
            const int hi = hex_value(in[i + 1]);
            const int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return std::nullopt;
            c = static_cast<unsigned char>(hi * 16 + lo);
            if (c == 0) return std::nullopt;
            i += 2;
        }
        out.push_back(static_cast<char>(c));
    }
    return out;
}

std::optional<std::string> resolve_path(const std::string &root, const std::string &target) {
    if (target.empty() || target[0] != '/') return std::nullopt;

    std::string full = root;
    const std::size_t rootlen = full.size();

    std::size_t i = 0;
    while (i < target.size()) {
        while (i < target.size() && target[i] == '/') i++;
        if (i >= target.size()) break;

        const std::size_t start = i;
        while (i < target.size() && target[i] != '/') i++;
        const std::string seg = target.substr(start, i - start);

        if (seg == ".") continue;
        if (seg == "..") {
            if (full.size() <= rootlen) return std::nullopt;
            full.erase(full.rfind('/'));
            continue;
        }
        full += '/';
        full += seg;
    }

    if (full.size() == rootlen) full += "/index.html";
    return full;
}
/* ===== server.h ===== */
#ifndef SERVER_H
#define SERVER_H

#include <cstddef>
#include <string>

#include "socket.h"

/* Owns the listening socket, the document root, and every connection it
   accepts. A connection lives in a local Socket inside serve_one, so it is
   closed whether the request succeeds, fails, or throws. */
class Server {
public:
    Server(int port, std::string root);

    int port() const { return listener_.port(); }
    std::size_t served() const { return served_; }

    /* Accept one connection and answer it. Never throws for a bad client. */
    void serve_one();

    /* Accept until the listener fails. */
    void serve_forever();

    /* Request text in, response text out. Exposed so a test can call it. */
    std::string handle(const std::string &raw) const;

private:
    Listener listener_;
    std::string root_;
    std::size_t served_ = 0;
};

#endif
/* ===== server.cpp ===== */
#include "server.h"

#include "files.h"

#include <sstream>
#include <stdexcept>
#include <utility>

namespace {

constexpr std::size_t kRequestCap = 8192;
constexpr std::size_t kMaxBody = 8u * 1024u * 1024u;

std::string build_response(const std::string &status, const std::string &type,
                           const std::string &body) {
    return "HTTP/1.1 " + status + "\r\n"
           "Content-Type: " + type + "\r\n"
           "Content-Length: " + std::to_string(body.size()) + "\r\n"
           "Connection: close\r\n"
           "\r\n" + body;
}

std::string error_response(const std::string &status, const std::string &message) {
    return build_response(status, "text/plain", message + "\n");
}

}  // namespace

Server::Server(int port, std::string root)
    : listener_(port), root_(std::move(root)) {}

std::string Server::handle(const std::string &raw) const {
    /* Chapter 28 replaces this with a real request model; for now the request
       line is all this server looks at. */
    const std::string line = raw.substr(0, raw.find("\r\n"));

    std::istringstream in(line);
    std::string method, target, version;
    if (!(in >> method >> target >> version))
        return error_response("400 Bad Request", "malformed request line");
    if (method != "GET" && method != "HEAD")
        return error_response("405 Method Not Allowed", "only GET and HEAD");

    const auto decoded = percent_decode(target);
    if (!decoded) return error_response("400 Bad Request", "bad escape in target");

    const auto full = resolve_path(root_, *decoded);
    if (!full) return error_response("403 Forbidden", "outside the document root");

    const auto body = read_file(*full, kMaxBody);
    if (!body) return error_response("404 Not Found", "no such file, or too large");

    std::string response = build_response("200 OK", mime_type(*full), *body);
    if (method == "HEAD") response.resize(response.size() - body->size());
    return response;
}

void Server::serve_one() {
    Socket conn = listener_.accept_one();
    try {
        const std::string raw = conn.read_until("\r\n\r\n", kRequestCap);
        conn.write_all(handle(raw));
        served_++;
    } catch (const std::exception &) {
        /* A client that vanished mid-request is not the server's problem. */
    }
}

void Server::serve_forever() {
    for (;;) {
        try {
            serve_one();
        } catch (const std::exception &) {
            break;                     /* accept failed: the listener is gone */
        }
    }
}
/* ===== main.cpp ===== */
#include "server.h"

#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/stat.h>
#include <sys/wait.h>

namespace {

const char *kDefaultRoot = "docroot";

void make_fixture(const std::string &root) {
    ::mkdir(root.c_str(), 0755);

    std::FILE *f = std::fopen((root + "/index.html").c_str(), "wb");
    if (f != nullptr) { std::fputs("<h1>hello from serve++</h1>\n", f); std::fclose(f); }

    f = std::fopen((root + "/notes.txt").c_str(), "wb");
    if (f != nullptr) { std::fputs("a plain text file\n", f); std::fclose(f); }
}

/* Print a response with CR LF made visible, the way chapter 17 did. */
void dump(const std::string &label, const std::string &data) {
    std::printf("=== %s -> %zu bytes ===\n", label.c_str(), data.size());
    for (char ch : data) {
        if (ch == '\r')      std::fputs("\\r", stdout);
        else if (ch == '\n') std::fputs("\\n\n", stdout);
        else                 std::putchar(ch);
    }
}

int run_self_test(const std::string &root) {
    make_fixture(root);

    Server server(0, root);
    const int port = server.port();

    const std::string requests[] = {
        "GET / HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /notes.txt HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /missing.txt HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /../etc/passwd HTTP/1.1\r\nHost: x\r\n\r\n",
        "PUT / HTTP/1.1\r\nHost: x\r\n\r\n",
    };
    const std::size_t count = sizeof requests / sizeof requests[0];

    /* The child serves; this process does every read and every print, so the
       transcript is reproducible. */
    const pid_t child = ::fork();
    if (child == 0) {
        for (std::size_t i = 0; i < count; i++) server.serve_one();
        ::_exit(0);
    }

    ::usleep(150000);                  /* let the child reach accept() */

    for (std::size_t i = 0; i < count; i++) {
        Socket c(::socket(AF_INET, SOCK_STREAM, 0));
        if (!c.valid()) { std::perror("socket"); return 1; }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<uint16_t>(port));
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        if (::connect(c.fd(), reinterpret_cast<sockaddr *>(&addr), sizeof addr) < 0) {
            std::perror("connect");
            return 1;
        }

        if (::write(c.fd(), requests[i].data(), requests[i].size()) < 0) {
            std::perror("write");
            return 1;
        }

        std::string got;
        char buf[1024];
        ssize_t n;
        while ((n = ::read(c.fd(), buf, sizeof buf)) > 0)
            got.append(buf, static_cast<std::size_t>(n));

        dump(requests[i].substr(0, requests[i].find("\r")), got);
    }

    ::waitpid(child, nullptr, 0);
    return 0;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 1) {
        std::printf("no arguments: running the built-in self-test\n");
        return run_self_test(kDefaultRoot);
    }
    if (std::strcmp(argv[1], "--help") == 0) {
        std::printf("usage: %s                run the built-in self-test\n", argv[0]);
        std::printf("       %s <port> [root]  serve files from root (default %s)\n",
                    argv[0], kDefaultRoot);
        return 0;
    }

    const int port = std::atoi(argv[1]);
    if (port <= 0 || port > 65535) {
        std::fprintf(stderr, "%s: not a port number: %s\n", argv[0], argv[1]);
        return 2;
    }
    const std::string root = argc > 2 ? argv[2] : kDefaultRoot;

    try {
        std::signal(SIGPIPE, SIG_IGN);      /* a vanished client is not fatal */
        Server server(port, root);
        std::printf("serving %s on http://127.0.0.1:%d/\n", root.c_str(), server.port());
        std::fflush(stdout);
        server.serve_forever();
    } catch (const std::exception &e) {
        std::fprintf(stderr, "%s\n", e.what());
        return 1;
    }
    return 0;
}
/* ===== Makefile ===== */
CXX     = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2

OBJS    = main.o socket.o files.o server.o

prog: $(OBJS)
	$(CXX) $(CXXFLAGS) -o prog $(OBJS)

main.o: main.cpp server.h
	$(CXX) $(CXXFLAGS) -c main.cpp

socket.o: socket.cpp socket.h
	$(CXX) $(CXXFLAGS) -c socket.cpp

files.o: files.cpp files.h
	$(CXX) $(CXXFLAGS) -c files.cpp

server.o: server.cpp server.h files.h socket.h
	$(CXX) $(CXXFLAGS) -c server.cpp

clean:
	rm -f prog $(OBJS)

.PHONY: clean
```

```text
no arguments: running the built-in self-test
=== GET / HTTP/1.1 -> 111 bytes ===
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 28\r\n
Connection: close\r\n
\r\n
<h1>hello from serve++</h1>\n
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

Put that next to Chapter 17's transcript and the comparison is the point of the whole chapter. The
`404`, the `403`, the `405` and the `notes.txt` response are **byte-for-byte identical** — same
`Content-Length`, same body, same order. The only difference is the two extra bytes in `serve++`,
because the fixture's own text changed. A port that changes behaviour is a rewrite, and a rewrite is
how bugs get in; this one changed nothing but the way the resources are held.

Two things in that listing are worth a closer look.

`Listener`'s constructor is where RAII earns its keep in a way that is easy to miss. If `bind` fails it
throws — and by that point `sock_` is already a live `Socket`. Because the member was constructed, its
destructor runs when the exception leaves the constructor, so the descriptor is closed even though no
`Listener` object was ever completed. **A half-constructed object still has its fully-constructed
members destroyed.** That is why `sock_` is a `Socket` member rather than a bare `int` assigned after
the `bind` succeeded.

`Server::serve_one` is the other half of the argument. The connection is a local `Socket`, so it is
closed when the function returns — after a success, after a bad request, and after an exception:

```cpp
void Server::serve_one() {
    Socket conn = listener_.accept_one();
    try {
        const std::string raw = conn.read_until("\r\n\r\n", kRequestCap);
        conn.write_all(handle(raw));
        served_++;
    } catch (const std::exception &) {
        /* A client that vanished mid-request is not the server's problem. */
    }
}
```

Note where the `try` is. It is *inside* `serve_one`, around the connection handling, so one broken
client cannot take the server down. The `try` in `serve_forever` wraps `serve_one` for a different
reason — it catches the `accept` failure, which means the listener itself is gone and there is nothing
left to do but stop. Two `try` blocks, two different meanings, and putting them in the right places is
most of what makes a server survive its clients.

## Building it

```sh run-project
make clean
make
```

```text
rm -f prog main.o socket.o files.o server.o
c++ -std=c++17 -Wall -Wextra -Werror -O2 -c main.cpp
c++ -std=c++17 -Wall -Wextra -Werror -O2 -c socket.cpp
c++ -std=c++17 -Wall -Wextra -Werror -O2 -c files.cpp
c++ -std=c++17 -Wall -Wextra -Werror -O2 -c server.cpp
c++ -std=c++17 -Wall -Wextra -Werror -O2 -o prog main.o socket.o files.o server.o
```

The Makefile is Chapter 17's, with `CC` changed to `CXX` and `-std=c17` to `-std=c++17`. Everything
else — the dependency lines, the `.PHONY` target, the `clean` rule — is the same, because separate
compilation is a property of the *linker*, not of the language.

## Driving it with curl

The self-test proves the server answers its own client. `curl` proves it answers someone else's:

```sh run-project
mkdir -p live
printf '<h1>live</h1>\n' > live/index.html
printf 'body { color: red; }\n' > live/style.css

./prog 8793 live > server.log 2>&1 &
srv=$!
trap 'kill $srv 2>/dev/null' EXIT
sleep 1

cat server.log
curl -s -i http://127.0.0.1:8793/
curl -s -i http://127.0.0.1:8793/style.css

kill $srv
wait $srv 2>/dev/null
exit 0
```

```text
serving live on http://127.0.0.1:8793/
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

Identical to the C server's transcript, down to the byte count. The refusals are where the C++ version
has something new to show, because `HEAD` is now a real branch:

```sh run-project
mkdir -p live
printf '<h1>live</h1>\n' > live/index.html

./prog 8794 live > server.log 2>&1 &
srv=$!
trap 'kill $srv 2>/dev/null' EXIT
sleep 1

curl -s -o /dev/null -w "status=%{http_code}\n" http://127.0.0.1:8794/nope
curl -s -o /dev/null -w "status=%{http_code}\n" --path-as-is "http://127.0.0.1:8794/../../../../etc/passwd"
curl -s -o /dev/null -w "status=%{http_code}\n" -X POST http://127.0.0.1:8794/
curl -s -I http://127.0.0.1:8794/
curl -s -o /dev/null -w "HEAD body bytes=%{size_download}\n" -I http://127.0.0.1:8794/

kill $srv
wait $srv 2>/dev/null
exit 0
```

```text
status=404
status=403
status=405
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 14
Connection: close

HEAD body bytes=0
```

The last two commands are the interesting pair. `curl -I` sends `HEAD` and prints the headers, and
`Content-Length: 14` is there — the length the body *would* have had. `size_download=0` says no body
bytes arrived. Both are correct, and both are required: a client asking "how big is this" must be told
the real size, not zero, or every download manager and link checker that uses `HEAD` to decide whether
to fetch will get the answer wrong. Chapter 17 left this as an exercise. Here it is one line:

```cpp
std::string response = build_response("200 OK", mime_type(*full), *body);
if (method == "HEAD") response.resize(response.size() - body->size());
return response;
```

`resize` down to the header's length — and because `std::string` knows its own size, the arithmetic is
`size() - body->size()` rather than a `size_t header_len` you carried out of `build_response`. In the C
version, `build_response` returned the total, so the header length was `total - body_len`, and a
mistake there would silently corrupt the response. Here both numbers come from the same object.

:::scenario The image that came back half blank

A developer ports the file server to C++ over a weekend. The port is careful: the socket class is
straight out of this chapter, the error paths all throw, and the self-test passes. Monday morning the
site's PNGs render as the top third of the image with grey below.

The old server served them fine, and the C++ server serves the HTML and CSS fine, which is what makes
it confusing. The HTML is text, so a length computed with `strlen` is right. The PNG is not text — its
fourth byte is often a NUL — so `strlen` stops early:

```text
the body is 8 bytes, strlen() says 3
C   declares Content-Length: 3, response is 85 bytes
C++ declares Content-Length: 8, response is 90 bytes
```

Five bytes of a 90-byte response. On a real image that is a truncated file, and a browser that has been
told the size shows what it managed to decode and fills the rest with grey. Nothing in the server logs
a problem, because from the server's point of view there was no problem: it read the file, built a
response, and sent all of it.

:::solution Take the body as a `std::string` and let it report its own size

```cpp
std::string build_response(const std::string &status, const std::string &type,
                           const std::string &body);
```

The signature change is the fix. `body` is no longer a `const char *` plus a separate length, so there
is no second value to disagree with `Content-Length`. Every caller that had been passing
`strlen(ptr)` now passes the object, and `body.size()` is correct for a PNG, a UTF-8 HTML page with
multi-byte characters, and a response whose body is empty.

The reason to prefer this over "use `memchr` instead of `strlen`" is that the second approach keeps the
bug reachable. The bug is not that `strlen` is wrong for binary data; it is that the response had two
sources of truth for one quantity. Fixing the *caller* fixes today's bug and leaves the next caller to
find it again.

:::

:::

:::pitfall The member that is destroyed before you are done with it

A `Session` class holds the connection socket and a logger that writes a final line when it is
destroyed. Both look fine. The logger writes to a closed socket:

```cpp run
#include <cstdio>
#include <string>
#include <utility>

/* Stand-ins for the two members a connection handler really has: the socket it
   writes to, and a logger that writes to that socket on the way out. */
struct Socket {
    std::string name;
    explicit Socket(std::string n) : name(std::move(n)) {
        std::printf("open  %s\n", name.c_str());
    }
    ~Socket() { std::printf("close %s\n", name.c_str()); }
    void send(const char *text) const {
        std::printf("send  %s -> %s\n", text, name.c_str());
    }
};

struct Logger {
    const Socket *sock;
    explicit Logger(const Socket *s) : sock(s) {}
    ~Logger() { sock->send("bye"); }
};

/* Members are destroyed in REVERSE declaration order. Here the logger is
   declared first, so it is destroyed LAST - after the socket it writes to. */
struct BadSession {
    Logger log;
    Socket sock;
    BadSession() : log(&sock), sock("bad-session") {}
};

/* The socket is declared first, so it is destroyed last, so the logger still
   has something to write to. */
struct GoodSession {
    Socket sock;
    Logger log;
    GoodSession() : sock("good-session"), log(&sock) {}
};

int main() {
    std::printf("--- Logger declared first ---\n");
    { BadSession s; }

    std::printf("--- Socket declared first ---\n");
    { GoodSession s; }
    return 0;
}
```

```text
--- Logger declared first ---
open  bad-session
close bad-session
send  bye -> bad-session
--- Socket declared first ---
open  good-session
send  bye -> good-session
close good-session
```

Members are destroyed in **reverse declaration order**, so `BadSession` closes its socket first and
then asks its logger to write to it. In this program the logger prints anyway, because the `Socket` is
a stand-in and its name is a `std::string` that is still readable. In the real thing the logger holds a
descriptor number, and a write to a closed descriptor either fails with `EBADF` or — worse, because it
is silent — succeeds against whatever has since been given that number.

The rule is not "put the socket last". It is: **a member that another member depends on must be
declared before it**, because declaration order is construction order and reverse declaration order is
destruction order. That is the same ordering rule Chapter 20 showed you with `-Wreorder-ctor`, seen
from the other end of the object's life. When a class has a resource member and a helper that uses it,
the resource goes first.

:::

## Key takeaways

- RAII replaces "remember to release" with "the scope releases". The measurement is not a claim about
  discipline; it is four calls and a difference of one line.
- A leaked descriptor is invisible until `accept` fails with `EMFILE`, and by then the cause is
  nowhere near the symptom.
- A resource type needs a destructor, a deleted copy constructor, a deleted copy assignment, and a
  move constructor. Without the two `= delete`s the copy double-releases; **a double close is worse
  than a leak**, because the descriptor may have been recycled.
- A move constructor must leave the source inert (`fd_ = -1`) so that its destructor is harmless.
  Every resource type in the standard library does this, and it is why a moved-from object is valid
  but unspecified rather than unusable.
- Return `std::string` instead of `char *` plus a length. The `outsz` parameter and its
  `if (did not fit) return 0` branch disappear, and `Content-Length` can no longer disagree with the
  body.
- `c_str()` gives you a pointer into the string's buffer, valid only until the next operation that may
  reallocate. Take `const std::string &` and call `.c_str()` at the call site.
- `unique_ptr<T, D>` calls `D` with a `T *`, so it cannot own a file descriptor. Handles that are not
  pointers need a small RAII class of their own.
- A constructor that throws still destroys the members it had already constructed, which is why a
  member that must be released is a `Socket` and not a bare `int`.
- Put the `try` around the *connection* inside `serve_one` and around *`accept`* in `serve_forever`.
  One broken client must not stop the server; a dead listener must.
- Members are destroyed in reverse declaration order. A member that depends on another must be
  declared after it.
- A port that changes behaviour is a rewrite. Byte-for-byte identical transcripts are the evidence
  that this one did not.

## Practice

- [ ] Give `Socket` a `static` counter of descriptors it has closed, and prove that a moved-from
      `Socket` closes nothing. Explain what would go wrong if the move constructor did not set
      `fd_ = -1`.
- [ ] Rewrite `read_file` using `std::ifstream` and `std::string`, with no `FILE *` anywhere, and
      check that it still reads a file containing a NUL byte whole and still respects the size cap.
- [ ] `resolve_path` refuses a target containing `..`, and `percent_decode` turns `%2e%2e` into `..`.
      Write a program that shows why the order matters — and what the server would serve if you
      resolved first and decoded second.
- [ ] `Socket::read_until` silently returns a truncated request when the cap is reached. Change it to
      report *why* it stopped, and test all three outcomes: complete, closed, too long. Explain which
      HTTP status each one should become.
- [ ] Run `./prog --help`, `./prog 0` and `./prog nonsense`, and account for every exit status.
      Why is `0` rejected as a port number when `Listener` would happily accept it?
- [ ] Add a `--version` flag, a `port()` accessor printed at startup, and a `requests served` line
      printed when the server is interrupted. Which of those three needs `serve_forever` to change,
      and why?

## Solutions

:::solution Exercise 1

A `static` member counts every descriptor the destructor closes. Because it belongs to the class and
not to an object, it survives the objects it is counting:

```cpp run
#include <cstdio>
#include <utility>
#include <unistd.h>
#include <sys/socket.h>

class Socket {
public:
    explicit Socket(int fd) : fd_(fd) {}
    ~Socket() {
        if (fd_ >= 0) { ::close(fd_); closes_++; }
    }
    Socket(const Socket &) = delete;
    Socket &operator=(const Socket &) = delete;
    Socket(Socket &&other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    bool valid() const { return fd_ >= 0; }
    static int closes() { return closes_; }

private:
    int fd_;
    static int closes_;
};

int Socket::closes_ = 0;

static int make_connection() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) return -1;
    ::close(fds[1]);
    return fds[0];
}

int main() {
    {
        Socket a(make_connection());
        std::printf("closes with one socket alive:  %d\n", Socket::closes());
        Socket b(std::move(a));
        std::printf("the moved-from socket is open: %s\n", a.valid() ? "yes" : "no");
    }
    std::printf("closes after both are gone:    %d\n", Socket::closes());
    return 0;
}
```

```text
closes with one socket alive:  0
the moved-from socket is open: no
closes after both are gone:    1
```

Two `Socket` objects, one `close`. Without `other.fd_ = -1` in the move constructor, `a` would still
hold the descriptor, so `a`'s destructor would close it a second time — and the counter would read `2`
for a single socket. The counter is doing the job a sanitizer cannot: there is nothing wrong with the
memory, and the second `close` may well return success because by then the number belongs to something
else.

The `static` definition outside the class is required, and it is the same rule Chapter 20 covered:
the declaration inside the class allocates nothing, so exactly one translation unit has to provide the
storage. In a header-and-source project that definition goes in `socket.cpp`.

:::

:::solution Exercise 2

`std::ifstream` with `std::ios::binary` is the direct replacement, and the rest is `std::string`:

```cpp run
#include <cstdio>
#include <fstream>
#include <optional>
#include <string>

/* The same contract as the FILE* version, with no C library in sight. */
std::optional<std::string> read_file(const std::string &path, std::size_t max_bytes) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return std::nullopt;

    in.seekg(0, std::ios::end);
    const std::streamoff size = in.tellg();
    if (size < 0) return std::nullopt;
    if (static_cast<unsigned long long>(size) > max_bytes) return std::nullopt;
    in.seekg(0, std::ios::beg);

    std::string body(static_cast<std::size_t>(size), '\0');
    if (!body.empty()) {
        in.read(body.data(), static_cast<std::streamsize>(body.size()));
        if (!in) return std::nullopt;
    }
    return body;
}

int main() {
    {   /* a body that is not text: eight bytes, one of them a NUL */
        std::ofstream out("blob.bin", std::ios::binary);
        out.write("abc\0defg", 8);
    }

    const auto body = read_file("blob.bin", 1024);
    std::printf("read %zu bytes\n", body ? body->size() : 0);
    std::printf("byte 3 is still NUL:  %s\n", body && (*body)[3] == '\0' ? "yes" : "no");
    std::printf("a 1-byte cap refuses: %s\n", read_file("blob.bin", 1) ? "no" : "yes");
    std::printf("a missing file:       %s\n", read_file("nope.bin", 1024) ? "opened" : "refused");
    return 0;
}
```

```text
read 8 bytes
byte 3 is still NUL:  yes
a 1-byte cap refuses: yes
a missing file:       refused
```

Four properties, four lines. The stream is opened in binary mode so the NUL survives; the size is
known before the read so the buffer can be sized once and the cap checked before any allocation; the
`!in` test after `read` catches a short read, which is the failure the `FILE *` version checked with
`got != size`; and the destructor of `in` closes the stream, so there is no `fclose` on any path.

`std::streamoff` and `std::streamsize` are the types the stream API uses, and the casts are there
because they are signed while `std::string`'s size is not. Converting a negative `tellg()` result to
`std::size_t` without checking would produce an enormous allocation, which is why the `size < 0` test
comes first.

:::

:::solution Exercise 3

Encode the traversal and watch the two orders diverge:

```cpp run
#include <cstdio>
#include <optional>
#include <string>

static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

std::optional<std::string> percent_decode(const std::string &in) {
    std::string out;
    out.reserve(in.size());
    for (std::size_t i = 0; i < in.size(); i++) {
        unsigned char c = static_cast<unsigned char>(in[i]);
        if (c == '%') {
            if (i + 2 >= in.size()) return std::nullopt;
            const int hi = hex_value(in[i + 1]);
            const int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return std::nullopt;
            c = static_cast<unsigned char>(hi * 16 + lo);
            if (c == 0) return std::nullopt;
            i += 2;
        }
        out.push_back(static_cast<char>(c));
    }
    return out;
}

std::optional<std::string> resolve_path(const std::string &root, const std::string &target) {
    if (target.empty() || target[0] != '/') return std::nullopt;
    std::string full = root;
    const std::size_t rootlen = full.size();
    std::size_t i = 0;
    while (i < target.size()) {
        while (i < target.size() && target[i] == '/') i++;
        if (i >= target.size()) break;
        const std::size_t start = i;
        while (i < target.size() && target[i] != '/') i++;
        const std::string seg = target.substr(start, i - start);
        if (seg == ".") continue;
        if (seg == "..") {
            if (full.size() <= rootlen) return std::nullopt;
            full.erase(full.rfind('/'));
            continue;
        }
        full += '/';
        full += seg;
    }
    if (full.size() == rootlen) full += "/index.html";
    return full;
}

int main() {
    const std::string encoded = "/%2e%2e/%2e%2e/etc/passwd";

    /* RIGHT: decode, then resolve - the traversal is visible to the resolver. */
    const auto decoded = percent_decode(encoded);
    const auto good = decoded ? resolve_path("docroot", *decoded) : std::nullopt;
    std::printf("decode then resolve: %s\n", good ? good->c_str() : "(refused)");

    /* WRONG: resolve, then decode - the escape survives the check. */
    const auto bad = resolve_path("docroot", encoded);
    std::printf("resolve then decode: %s\n", bad ? bad->c_str() : "(refused)");
    return 0;
}
```

```text
decode then resolve: (refused)
resolve then decode: docroot/%2e%2e/%2e%2e/etc/passwd
```

Decoding first turns the target into `/../../etc/passwd`, the resolver sees two `..` segments, and it
refuses. Resolving first is the dangerous order: `%2e%2e` is not `..`, so the resolver treats it as an
ordinary directory name, walks one level down, and happily returns
`docroot/%2e%2e/%2e%2e/etc/passwd` — a path that passed the traversal check. Decode it afterwards and
you are opening `../../etc/passwd` from a string that was already declared safe.

The general rule: **every security check must run on the value you are actually going to use.** A check
on an intermediate representation is a check on something else. This is why the project's `handle`
calls `percent_decode` and then `resolve_path`, in that order, and why the `403` you get from
`curl --path-as-is` is the check firing for real rather than a coincidence of the fixture.

:::

:::solution Exercise 4

Return an enum instead of a string, so the caller is forced to deal with the three cases:

```cpp run
#include <cstdio>
#include <string>
#include <unistd.h>
#include <sys/socket.h>

enum class ReadResult { Complete, Closed, TooLong };

/* The project's read_until reports why it stopped instead of quietly
   returning a truncated request. */
static ReadResult read_until(int fd, const std::string &marker,
                             std::size_t cap, std::string *out) {
    out->clear();
    char buf[256];
    while (out->size() < cap) {
        const ssize_t n = ::read(fd, buf, sizeof buf);
        if (n <= 0) return ReadResult::Closed;
        out->append(buf, static_cast<std::size_t>(n));
        if (out->size() > cap) return ReadResult::TooLong;
        if (out->find(marker) != std::string::npos) return ReadResult::Complete;
    }
    return ReadResult::TooLong;
}

static const char *name(ReadResult r) {
    switch (r) {
        case ReadResult::Complete: return "complete";
        case ReadResult::Closed:   return "closed";
        case ReadResult::TooLong:  return "too long";
    }
    return "?";
}

int main() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) return 1;

    const std::string small = "GET / HTTP/1.1\r\n\r\n";
    if (::write(fds[1], small.data(), small.size()) < 0) return 1;
    std::string got;
    std::printf("a short request:      %s\n", name(read_until(fds[0], "\r\n\r\n", 1024, &got)));
    std::printf("  bytes kept:         %zu\n", got.size());

    std::string huge = "GET /";
    huge.append(500, 'a');
    huge += " HTTP/1.1\r\n\r\n";
    if (::write(fds[1], huge.data(), huge.size()) < 0) return 1;
    std::printf("a 513-byte request:   %s\n", name(read_until(fds[0], "\r\n\r\n", 64, &got)));

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
a short request:      complete
  bytes kept:         18
a 513-byte request:   too long
```

The three outcomes map onto three different responses, and keeping them apart is what stops the server
from lying about what happened:

- **Complete** — the request arrived whole. Serve it.
- **Closed** — the peer went away before sending the end of the headers. `400 Bad Request` is
  defensible, but there is nobody left to send it to, so the useful action is to close and count it.
- **Too long** — the request exceeded the cap. This is `414 URI Too Long`, which is a real status code
  for exactly this situation and which Chapter 17 used. The version that returns a truncated string
  cannot tell this case from `Complete`, so a request line that was cut in half gets parsed as a
  malformed request and reported as `400` — a status that blames the client for something the server
  did.

Note the order of the two tests inside the loop. The cap is checked *after* appending and *before*
looking for the marker, because a single `read` can deliver more than the cap in one go: with a 64-byte
cap, the 513-byte request arrives and the marker is present, so checking the marker first would call it
complete. Test the limit before the success condition, or a large request passes as a small one.

:::

:::solution Exercise 5

```sh run-project
./prog --help
echo "exit status: $?"
./prog 0 2>&1
echo "exit status: $?"
./prog nonsense 2>&1
echo "exit status: $?"
exit 0
```

```text
usage: ./prog                run the built-in self-test
       ./prog <port> [root]  serve files from root (default docroot)
exit status: 0
./prog: not a port number: 0
exit status: 2
./prog: not a port number: nonsense
exit status: 2
```

Three runs, two exit statuses, and the split is deliberate. `--help` is something the user asked for,
so it writes to `stdout` and exits `0` — the output is data a script may capture. The two rejected
ports are diagnostics, so they write to `stderr` and exit `2` — the `2>&1` in the script is what folds
them into the transcript you see. `0` and `nonsense` get the same treatment because they fail for the
same reason from `main`'s point of view: neither is a port this program will serve on.

`Listener` would accept `0` quite happily — it is the "let the kernel choose" value the self-test uses
— which is exactly why `main` has to reject it. A server started as `./prog 0` would bind to a random
port and print it, so the person who typed `0` would have no idea where their server went, and a
script that reads the port from a config file would have a silent failure instead of an error. The
library is permissive because a *test* needs `0`; the program is strict because a *user* does not. That
is a general shape: put the permissive behaviour in the mechanism and the strict behaviour at the
boundary where a human is involved.

:::

:::solution Exercise 6

`--version` is a branch in `main` next to `--help`, and it needs nothing else:

```cpp
#define VERSION "serve++ 1.0"
```

`port()` already exists — `Listener::port()` reports the port the kernel chose, and `Server` forwards
it, so `main` can print `server.port()` and it will be right even when `0` was passed.

The `requests served` line is the one that needs `serve_forever` to change, and the reason is worth
understanding. `Server::served()` counts requests, but the counter lives in the server process, and
`serve_forever` never returns — it loops until `accept` fails. So the count is never printed, because
there is no point in the program at which the loop has ended and the count is still available.

Three ways out, in increasing order of how much they teach you:

1. Print the count from `serve_one`, after each request. Trivial, and it puts a line on `stdout` per
   request, which is a real cost and makes the log useless.
2. Make `serve_forever` return when a signal arrives — install a handler for `SIGINT` that sets a
   `volatile std::sig_atomic_t` flag, check it in the loop, and print the count after the loop. This is
   the standard shape and it is what Chapter 32 does properly, with `std::atomic` instead.
3. Count in a way that survives the process, which is Chapter 33's problem when the service has more
   than one process.

The pattern behind all three: a counter that only exists in memory is only observable while the
process is alive, so a graceful shutdown is not a nicety — it is what makes your own instrumentation
readable.

:::
