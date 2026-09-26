---
chapter: 41
part: 5
title: Async I/O — Non-blocking Sockets and the Event Loop
summary: Handle thousands of connections in one thread by asking the kernel which descriptors are ready, dispatching work in a loop, and never letting a send silently drop bytes.
minutes: 75
tags: [non-blocking, poll, event loop, reactor, readiness, curl, sockets]
---

Chapter 40 served many clients by giving each one a thread. That works, and it has a price that
shows up before the CPU does: every thread costs a stack, and every context switch costs more than
the work it was switched to. A thousand idle connections should cost a thousand file descriptors
and almost no CPU, and with thread-per-connection they cost a thousand threads and a scheduler
that never stops moving.

The alternative is to stop treating "waiting for a client" as something a thread does. One thread
can hold every connection if it never blocks on any of them, and asks the kernel a different
question instead: **which of these is ready right now?** Everything in this chapter follows from
that question. It is also the design every production server you have used is built on --
`nginx`, `redis`, `node`, and the `epoll`/`kqueue` layer under all of them.

## A descriptor is blocking unless you say otherwise

By default, `recv()` on a socket with nothing to read *waits*. That single behaviour is what makes
one-thread-per-connection necessary, because the waiting is done by the calling thread and that
thread can do nothing else. Turn it off and `recv()` answers immediately instead:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

// "Nothing to read yet" is a normal state on a non-blocking descriptor, not a failure.
bool would_block() { return errno == EAGAIN || errno == EWOULDBLOCK; }

}  // namespace

#include <cstdio>

int main() {
    int fds[2];
    if (!make_pair(fds)) {
        std::printf("socketpair failed\n");
        return 1;
    }

    // A descriptor is blocking by default: recv() waits until there is
    // something to hand you. The flag below is what makes it answer instead.
    std::printf("non-blocking mode: %s\n", set_nonblocking(fds[0]) ? "set" : "FAILED");

    char buffer[16];
    ssize_t n = ::recv(fds[0], buffer, sizeof buffer, 0);
    std::printf("recv before any data: n = %zd, errno says \"not yet\": %s\n", n,
                would_block() ? "yes" : "no");

    const char message[] = "hello";
    ::send(fds[1], message, sizeof message - 1, 0);

    n = ::recv(fds[0], buffer, sizeof buffer, 0);
    std::printf("recv after one send:  n = %zd, data = %.*s\n", n, static_cast<int>(n), buffer);

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
non-blocking mode: set
recv before any data: n = -1, errno says "not yet": yes
recv after one send:  n = 5, data = hello
```

The `-1` is not an error. `EAGAIN` -- "try again later" -- is the normal state of a connection you
are not finished with, and it is the value the whole event loop is built on. Treating it as a
failure is the first bug in every hand-written event loop, and it is worth internalising the
distinction now: **on a non-blocking descriptor, "nothing yet" is not a failure.**

A `socketpair` stands in for a network connection here, and it is worth knowing why. It is two
connected descriptors with no listener, no port and no client: whatever is written to one end is
readable at the other. It buffers, it fills up, and it can be made non-blocking exactly like a TCP
socket, which makes it the smallest thing that behaves like a connection -- so every readiness
experiment below runs in a single process with no timing to arrange.

:::warning The flag is on the descriptor, not the socket
`O_NONBLOCK` is a property of the *open file description*, which means every descriptor referring
to the same socket shares it. On Linux, `accept4()` can set it on the new connection in the same
syscall that creates it -- worth knowing, because a `listen()`ing socket being non-blocking does
**not** make the connections it returns non-blocking. Forgetting that is a server that works under
one client and hangs under two.
:::

## The spin you will write next

Non-blocking alone gets you a server that hammers the CPU, because the obvious next step is a loop
that calls `recv()` on every connection, gets `EAGAIN` from all of them, and immediately tries
again. That is a busy-wait: a core at 100% doing nothing.

The question you actually want to ask the kernel is narrower -- *is any of this readable?* -- and
`poll()` answers it in one call:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

}  // namespace

#include <cstdio>
#include <poll.h>

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);

    struct pollfd watch;
    watch.fd = fds[0];
    watch.events = POLLIN;
    watch.revents = 0;

    // A zero timeout turns poll() from a wait into a question: "is anything
    // ready right now?" That is the primitive an event loop is built on.
    int ready = ::poll(&watch, 1, 0);
    std::printf("nothing written yet: poll() = %d, readable = %s\n", ready,
                (watch.revents & POLLIN) ? "yes" : "no");

    ::send(fds[1], "x", 1, 0);

    watch.revents = 0;
    ready = ::poll(&watch, 1, 0);
    std::printf("after one byte:      poll() = %d, readable = %s\n", ready,
                (watch.revents & POLLIN) ? "yes" : "no");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
nothing written yet: poll() = 0, readable = no
after one byte:      poll() = 1, readable = yes
```

`poll()` takes a timeout in milliseconds, and **zero makes it a question rather than a wait**: it
returns at once with how many descriptors are ready, and sets `revents` on the ones that are. That
is the primitive. The whole `1`-vs-`0` distinction in that output is the difference between a loop
that burns a core and one that sleeps until there is work.

The timeout is the other half of the design, and it is not only about efficiency. With a timeout,
a single-threaded server can notice things that are not events: a client that has been silent for
30 seconds, a request that has taken too long, a periodic flush. Without one, the loop only wakes
when a descriptor moves, and any rule of the form "if nothing happens for N seconds, do X" becomes
impossible to implement.

## Watching all of them at once

The reason this scales is that one `poll()` call covers every descriptor you care about, and tells
you which ones moved:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

}  // namespace

#include <cstddef>
#include <cstdio>
#include <poll.h>
#include <vector>

int main() {
    const std::size_t count = 3;
    int pairs[3][2];
    std::vector<struct pollfd> watched;

    for (std::size_t i = 0; i < count; ++i) {
        if (!make_pair(pairs[i])) return 1;
        set_nonblocking(pairs[i][0]);
        struct pollfd entry;
        entry.fd = pairs[i][0];
        entry.events = POLLIN;
        entry.revents = 0;
        watched.push_back(entry);
    }

    // One byte, into the middle connection only.
    ::send(pairs[1][1], "?", 1, 0);

    const int ready = ::poll(watched.data(), watched.size(), 0);
    std::printf("poll() reports %d of %zu connections ready\n", ready, watched.size());
    for (std::size_t i = 0; i < watched.size(); ++i) {
        // The index is what is stable. The descriptor number is not: it
        // depends on what else the process has open, so never quote it.
        if (watched[i].revents & POLLIN) std::printf("connection %zu is readable\n", i);
    }

    for (std::size_t i = 0; i < count; ++i) {
        ::close(pairs[i][0]);
        ::close(pairs[i][1]);
    }
    return 0;
}
```

```text
poll() reports 1 of 3 connections ready
connection 1 is readable
```

Two details in that output matter more than they look.

The first is that `poll()` reports **one** ready connection out of three, not all of them. That is
the whole economy of the design: you pay for the descriptors that are ready, not the ones that
are idle. A thousand idle connections cost one `poll()` call that returns 0.

The second is that the program prints `connection 1`, an **index**, and never the descriptor
number. Descriptor numbers are assigned by the kernel from whatever the process already has open,
so they change between runs and between machines. A transcript that quotes them cannot be
verified, and a test that asserts on them is a test that fails on someone else's laptop. This is
the same rule as any other machine-dependent number: report the stable thing, and say what you
measured.

:::note Why this is `poll` and not `epoll` or `kqueue`
`poll()` is the portable one: it exists on Linux, macOS and the BSDs with the same signature, so
it is what this book teaches. The design cost is that you hand it the whole list every time and it
walks the whole list -- O(n) per call, and the kernel copies the array in and out. `epoll`
(Linux) and `kqueue` (macOS/BSD) fix that by keeping the interest list *in the kernel* and
returning only what changed, which is what makes a hundred thousand connections practical. The
shape of the loop does not change at all: same ready-set, same dispatch, different syscall. Learn
this one and the others are a weekend.
:::

## A send is not a delivery

Here is the bug that survives every test you write by hand: `send()` returns the number of bytes it
accepted, and it is allowed to accept fewer than you gave it.

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

// "Nothing to read yet" is a normal state on a non-blocking descriptor, not a failure.
bool would_block() { return errno == EAGAIN || errno == EWOULDBLOCK; }

}  // namespace

#include <cstddef>
#include <cstdio>
#include <vector>

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);
    set_nonblocking(fds[1]);

    const std::size_t wanted = 1024 * 1024;
    std::vector<char> payload(wanted, 'a');

    // One send() is not one delivery. A socket has a finite send buffer, so a
    // non-blocking send() fills what it can and returns -- with a *count*, not
    // an error. Code that assumes the count equals the request loses the rest.
    const ssize_t first = ::send(fds[1], payload.data(), payload.size(), 0);
    std::printf("asked to send %zu bytes in a single call\n", wanted);
    std::printf("the call accepted fewer: %s\n",
                (first > 0 && static_cast<std::size_t>(first) < wanted) ? "yes" : "no");

    // The pattern that works: keep sending what is left, and drain the other
    // end as you go, because the reason you cannot send is that the buffer is
    // full and nothing is emptying it.
    std::size_t sent = first > 0 ? static_cast<std::size_t>(first) : 0;
    std::vector<char> sink(64 * 1024);
    while (sent < wanted) {
        while (::recv(fds[0], sink.data(), sink.size(), 0) > 0) {
        }
        const ssize_t n = ::send(fds[1], payload.data() + sent, wanted - sent, 0);
        if (n > 0) {
            sent += static_cast<std::size_t>(n);
        } else if (!would_block()) {
            std::printf("send failed at %zu bytes\n", sent);
            return 1;
        }
    }
    std::printf("after the loop: %zu of %zu\n", sent, wanted);
    std::printf("the message is %s\n", sent == wanted ? "complete" : "TRUNCATED");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
asked to send 1048576 bytes in a single call
the call accepted fewer: yes
after the loop: 1048576 of 1048576
the message is complete
```

Read the two numbers. The first `send()` was asked for a megabyte and accepted a fraction of it,
**with no error**: a socket has a finite send buffer, a non-blocking `send()` fills what it can,
and the return value is a count. Code that ignores that count -- `send(fd, buf, len, 0);` and
carries on -- silently truncates the response. It is the worst kind of bug, because small replies
fit in the buffer and work perfectly, so it ships, and then one large response arrives and the
client gets half a document.

The loop that fixes it is the one in the second half of that program, and its shape is worth
naming: **keep the unsent remainder, and drain the peer as you go**, because the reason you cannot
send is that the buffer is full and nothing is emptying it. In a real server the remainder lives in
a per-connection write queue and the loop waits for `POLLOUT` instead of draining a socketpair.
That is Exercise 3.

## The reactor

So far the pieces are: mark descriptors non-blocking, ask `poll()` which are ready, and read or
write what you can. The structure that puts them together has a name, and separating it from the
sockets is what makes a server maintainable:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

}  // namespace

#include <cstddef>
#include <cstdio>
#include <functional>
#include <map>
#include <poll.h>
#include <utility>
#include <vector>

// A reactor: a table mapping "this descriptor is readable" to "do this". The
// loop knows nothing about sockets, HTTP or connections -- it watches, and it
// dispatches. That separation is the whole difference between this chapter's
// server and Chapter 20's, which accepted, served and closed in one function.
class Reactor {
public:
    void on_readable(int fd, std::function<void()> handler) {
        handlers_[fd] = std::move(handler);
    }

    // One turn of the loop. Returns how many handlers ran, 0 if nothing was
    // ready, or -1 if poll() itself failed.
    int turn(int timeout_ms) {
        std::vector<struct pollfd> watched;
        watched.reserve(handlers_.size());
        for (const auto &entry : handlers_) {
            struct pollfd item;
            item.fd = entry.first;
            item.events = POLLIN;
            item.revents = 0;
            watched.push_back(item);
        }
        const int ready = ::poll(watched.data(), watched.size(), timeout_ms);
        if (ready <= 0) return ready;

        int dispatched = 0;
        for (const struct pollfd &item : watched) {
            if (item.revents & POLLIN) {
                handlers_[item.fd]();
                ++dispatched;
            }
        }
        return dispatched;
    }

private:
    std::map<int, std::function<void()>> handlers_;
};

// A handler that reads what is there. Reading is not optional: a level-triggered
// poll() keeps reporting a descriptor as readable until the bytes are consumed,
// so a handler that only looks at `revents` makes the loop run forever.
std::function<void()> reader(int fd, const char *name) {
    return [fd, name] {
        char buffer[8];
        const ssize_t n = ::recv(fd, buffer, sizeof buffer, 0);
        std::printf("handler %s consumed %zd byte(s)\n", name, n);
    };
}

int main() {
    int first_pair[2];
    int second_pair[2];
    if (!make_pair(first_pair) || !make_pair(second_pair)) return 1;

    Reactor reactor;
    // Each handler closes over the name it should print, so the transcript
    // never depends on a descriptor number.
    reactor.on_readable(first_pair[0], reader(first_pair[0], "A"));
    reactor.on_readable(second_pair[0], reader(second_pair[0], "B"));

    ::send(first_pair[1], "a", 1, 0);
    ::send(second_pair[1], "b", 1, 0);

    std::printf("one byte queued on each connection\n");
    const int first_turn = reactor.turn(0);
    std::printf("turn() dispatched %d handler(s)\n", first_turn);
    const int second_turn = reactor.turn(0);
    std::printf("turn() again dispatched %d handler(s), because both were drained\n",
                second_turn);

    ::close(first_pair[0]);
    ::close(first_pair[1]);
    ::close(second_pair[0]);
    ::close(second_pair[1]);
    return 0;
}
```

```text
one byte queued on each connection
handler A consumed 1 byte(s)
handler B consumed 1 byte(s)
turn() dispatched 2 handler(s)
turn() again dispatched 0 handler(s), because both were drained
```

The `Reactor` holds one thing: a table from descriptor to a function to run when it is readable.
It does not know what a connection is, what HTTP is, or how many there are. Its `turn()` method
does exactly three things -- build the watch list, `poll()`, dispatch -- and returns how many
handlers ran.

That separation is the difference between this and Chapter 20's server, where accepting, parsing,
responding and closing were one function. It buys you three things: a handler can be tested by
calling it, a new kind of descriptor (a timer, a pipe, a signal) is a new entry in the table
rather than a new branch, and the loop itself has no state to get wrong.

There is one rule in that handler that is easy to miss and expensive to learn: **the handler reads
the socket.** `poll()` is level-triggered, which means it keeps reporting a descriptor as readable
for as long as the bytes are there. A handler that only looks at `revents` and does not consume
anything is a loop that runs the same handler forever at full speed -- a hot spin that looks, from
the outside, exactly like a hang. The second `turn()` in that output returns 0 precisely because
the first one drained both connections.

## A server, and the only honest way to test one

Everything above is now assembled into a non-blocking HTTP server: one thread, `poll()`, a
listen socket, and a client list. The same listing convention as the earlier project chapters --
the `/* ===== name ===== */` lines are separators, not file contents:

```cpp compile-files
/* ===== common.hpp ===== */

#ifndef COMMON_HPP
#define COMMON_HPP

#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

// A socketpair is two connected descriptors with no network in between:
// whatever is written to one end is readable at the other. It behaves like a
// connection in every way this chapter cares about -- it is non-blocking, it
// buffers, and it fills up -- without needing a port, a client or a listener.
inline bool make_pair(int fds[2]) {
    return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0;
}

inline bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

// The two errno values every event loop has to tell apart. "Nothing to read
// yet" is not an error -- it is the normal state of a connection you are not
// finished with, and treating it as one is how a loop turns into a spin.
inline bool would_block() { return errno == EAGAIN || errno == EWOULDBLOCK; }

#endif

/* ===== poll_server.cpp ===== */

#include "common.hpp"

#include <algorithm>
#include <arpa/inet.h>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <netinet/in.h>
#include <poll.h>
#include <string>
#include <vector>

namespace {

// "GET /hello HTTP/1.1" -> "/hello". A real parser is Chapter 18's job; this
// chapter is about when the bytes arrive, not what they mean.
std::string request_path(const std::string &head) {
    const std::size_t first = head.find(' ');
    if (first == std::string::npos) return "/";
    const std::size_t second = head.find(' ', first + 1);
    if (second == std::string::npos) return "/";
    return head.substr(first + 1, second - first - 1);
}

void forget(std::vector<int> &clients, int fd) {
    clients.erase(std::remove(clients.begin(), clients.end(), fd), clients.end());
}

}  // namespace

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: prog <port>\n");
        return 2;
    }
    const int port = std::atoi(argv[1]);

    // Writing to a socket whose peer has gone does not return an error: it
    // raises SIGPIPE, whose default action is to kill the process. Every
    // network program ignores it and checks the return value instead.
    std::signal(SIGPIPE, SIG_IGN);

    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) return 1;

    int reuse = 1;
    ::setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof reuse);

    struct sockaddr_in address;
    std::memset(&address, 0, sizeof address);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(static_cast<std::uint16_t>(port));
    if (::bind(listener, reinterpret_cast<struct sockaddr *>(&address), sizeof address) != 0) {
        std::fprintf(stderr, "bind failed\n");
        return 1;
    }
    if (::listen(listener, 16) != 0) return 1;
    set_nonblocking(listener);

    // No port number in this line on purpose: it changes every run, and a
    // transcript that quotes it cannot be verified.
    std::printf("listening on 127.0.0.1\n");
    std::fflush(stdout);

    std::vector<int> clients;
    int served = 0;

    for (;;) {
        std::vector<struct pollfd> watched;
        struct pollfd listener_entry;
        listener_entry.fd = listener;
        listener_entry.events = POLLIN;
        listener_entry.revents = 0;
        watched.push_back(listener_entry);
        for (const int fd : clients) {
            struct pollfd entry;
            entry.fd = fd;
            entry.events = POLLIN;
            entry.revents = 0;
            watched.push_back(entry);
        }

        // -1 means "wait as long as it takes". This is the line that makes the
        // loop cost nothing while it is idle: no spinning, no polling timer.
        const int ready = ::poll(watched.data(), watched.size(), -1);
        if (ready < 0) {
            if (errno == EINTR) continue;  // a signal arrived; the loop survives
            break;
        }

        if (watched[0].revents & POLLIN) {
            for (;;) {
                const int fd = ::accept(listener, nullptr, nullptr);
                if (fd < 0) break;  // EAGAIN: every pending connection is taken
                set_nonblocking(fd);
                clients.push_back(fd);
            }
        }

        for (std::size_t i = 1; i < watched.size(); ++i) {
            if (!(watched[i].revents & POLLIN)) continue;
            const int fd = watched[i].fd;

            char buffer[1024];
            const ssize_t n = ::recv(fd, buffer, sizeof buffer - 1, 0);
            if (n <= 0) {
                ::close(fd);
                forget(clients, fd);
                break;
            }
            buffer[n] = '\0';
            const std::string path = request_path(buffer);
            ++served;
            std::printf("served #%d GET %s\n", served, path.c_str());
            std::fflush(stdout);

            const std::string body = "you asked for " + path + "\n";
            char head[160];
            std::snprintf(head, sizeof head,
                          "HTTP/1.1 200 OK\r\n"
                          "Content-Type: text/plain\r\n"
                          "Content-Length: %zu\r\n"
                          "Connection: close\r\n\r\n",
                          body.size());
            const std::string response = std::string(head) + body;

            std::size_t sent = 0;
            while (sent < response.size()) {
                const ssize_t written =
                    ::send(fd, response.data() + sent, response.size() - sent, 0);
                // A real server keeps what it could not send and waits for
                // POLLOUT. This one has no write queue, so it gives up -- and
                // that limitation is the exercise at the end of the chapter.
                if (written <= 0) break;
                sent += static_cast<std::size_t>(written);
            }

            ::close(fd);
            forget(clients, fd);
            break;  // the descriptor list changed; rebuild it on the next turn
        }
    }

    for (const int fd : clients) ::close(fd);
    ::close(listener);
    return 0;
}

/* ===== Makefile ===== */

CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: poll_server.cpp common.hpp
	$(CXX) $(CXXFLAGS) -o prog poll_server.cpp

clean:
	rm -f prog
```

Built with its own `Makefile`, and then driven by a real client. `curl` is a third-party program
that knows nothing about this code, which is what makes its agreement evidence rather than a
tautology:

```sh run-project
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

./prog "$PORT" > server.log 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT

# Wait for the listener by asking it, rather than by sleeping and hoping.
# --noproxy: an HTTP proxy in the environment would send even a 127.0.0.1
# request to the proxy, and the proxy cannot reach this process.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/probe" && break
  sleep 0.2
done

echo "--- GET /hello ---"
curl -s --noproxy '*' "http://127.0.0.1:$PORT/hello"
echo "--- GET /stats ---"
curl -s --noproxy '*' "http://127.0.0.1:$PORT/stats"
echo "--- the server's own log ---"
cat server.log

kill $SRV 2>/dev/null
wait $SRV 2>/dev/null
echo "server stopped"
```

```text
--- GET /hello ---
you asked for /hello
--- GET /stats ---
you asked for /stats
--- the server's own log ---
listening on 127.0.0.1
served #1 GET /probe
served #2 GET /hello
served #3 GET /stats
server stopped
```

Read the server's own log at the bottom: `served #1 GET /probe` is the script's readiness probe --
`#2` and `#3` are the two requests whose responses are printed above them. Three requests, one
thread, and the process never blocked on any of them.

Two things about that script are the part people get wrong when they move from a demo to a test.
The port is chosen by asking the kernel for a free one and printing it, rather than hard-coded,
because a fixed port collides with whatever else is running and turns a green test red for no
reason. And the server is started in the background with its output redirected to a file, killed
through a `trap`, and waited for -- because a test that leaves a listener behind fails the *next*
run, with an error that has nothing to do with the code.

:::danger `curl` rewrites your path before it sends it
`curl` normalises the URL, so a request for `/../etc/passwd` arrives at the server as
`/etc/passwd`. A path-traversal test written with plain `curl` therefore tests nothing at all --
the server never sees the traversal. Use `--path-as-is` when the path is the thing under test.
:::

:::scenario The connection that was never closed
A service built on this loop runs fine for hours and then stops accepting new connections. The
process is alive, the CPU is idle, and `curl` gets a connection refused. `lsof -p <pid> | wc -l`
says the process holds 61,000 descriptors, and the limit is 61,440.

Nothing is leaking in the sense of "allocated and forgotten": the loop closes every socket, on the
paths that return normally. The leak is on the paths that do not. When a client disconnects in the
middle of a request, `recv()` returns 0, and the code path for that case removes the descriptor
from the client list and returns -- without closing it. The descriptor is invisible to the loop
from then on and unusable to anyone else, and it will never be reused, because descriptor numbers
are not recycled while the process that holds them is alive.

The fix is not "remember to close it" -- that is the rule that was already broken. The fix is to
make the descriptor an object whose destructor closes it, so that *every* exit path from the
handler closes it, including the ones added next year:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

}  // namespace

#include <cstdio>
#include <dirent.h>

// Counting the entries in /dev/fd is the only honest way to prove a descriptor
// was released. No sanitizer can see this leak: the descriptor belongs to the
// kernel, not to the heap, and macOS has no leak detector to ask anyway.
// Print the *difference*, never the absolute count -- the baseline depends on
// what the shell handed the process.
int open_descriptors() {
    DIR *dir = ::opendir("/dev/fd");
    if (dir == nullptr) return -1;
    int count = 0;
    while (::readdir(dir) != nullptr) ++count;
    ::closedir(dir);
    return count - 3;  // '.', '..' and the descriptor opendir itself used
}

// The Chapter 26 rule applied to a socket: if it is owned by an object, the
// destructor closes it on every path, including the one where an exception
// unwinds through the function.
class Descriptor {
public:
    explicit Descriptor(int fd) : fd_(fd) {}
    ~Descriptor() {
        if (fd_ >= 0) ::close(fd_);
    }
    Descriptor(const Descriptor &) = delete;
    Descriptor &operator=(const Descriptor &) = delete;
    int get() const { return fd_; }

private:
    int fd_;
};

int main() {
    const int baseline = open_descriptors();
    std::printf("baseline descriptor count differs per run; only the difference is printed\n");

    {
        int fds[2];
        if (!make_pair(fds)) return 1;
        Descriptor guard(fds[0]);
        ::send(fds[1], "x", 1, 0);
        ::close(fds[1]);  // the other end, closed by hand

        const int inside = open_descriptors();
        std::printf("while the guard is alive: %+d vs the baseline\n", inside - baseline);
    }

    const int after = open_descriptors();
    std::printf("after the guard's scope:  %+d vs the baseline\n", after - baseline);
    std::printf("the descriptor was released: %s\n", after == baseline ? "yes" : "NO");

    return 0;
}
```

```text
baseline descriptor count differs per run; only the difference is printed
while the guard is alive: +1 vs the baseline
after the guard's scope:  +0 vs the baseline
the descriptor was released: yes
```

`after the guard's scope: +0 vs the baseline` is the assertion, and the first line of that output
is the honesty requirement: the *absolute* descriptor count depends on what the shell handed the
process, so only the difference means anything. `/dev/fd` is the only way to measure this at all --
no memory sanitizer can see a descriptor leak, because the descriptor belongs to the kernel.
:::

:::pitfall Six ways this loop breaks
- **Treating `EAGAIN` as an error.** It is the normal answer for a connection with nothing to say.
  A loop that logs it fills a disk; one that closes the connection drops live clients.
- **A handler that reads nothing.** Level-triggered `poll()` reports the descriptor until the bytes
  are consumed, so a handler that ignores the data is an infinite hot loop.
- **One `accept()` per turn.** The backlog grows while you serve one connection at a time. Drain
  the queue with a loop until `accept()` returns `EAGAIN`.
- **Forgetting `SIGPIPE`.** Writing to a socket whose peer has gone raises `SIGPIPE`, whose default
  action terminates the process. Ignore it and check `send()`'s return value instead.
- **Ignoring a short `send()`.** The count is the contract; the remainder is your problem, and it
  only shows up when a response is bigger than the send buffer.
- **Assuming `O_NONBLOCK` on the listener covers its connections.** It does not. Each accepted
  descriptor is blocking by default and has to be set separately, or on Linux via `accept4()`.
:::

## Key takeaways

- A blocking `recv()` waits by occupying a thread; `O_NONBLOCK` makes it return `EAGAIN` instead,
  and `EAGAIN` on a non-blocking descriptor is a normal state, not an error.
- `poll()` answers "which of these is ready", and a zero timeout makes it a question rather than a
  wait; a non-zero timeout is what makes idle-timeout rules implementable in one thread.
- One `poll()` call covers every descriptor, so idle connections cost nothing; `poll()` is O(n) per
  call, which is why `epoll` and `kqueue` exist, and they change the syscall rather than the loop.
- `send()` returns how many bytes it accepted and may accept fewer than requested; the unsent
  remainder must be kept and retried when the descriptor is writable.
- A reactor separates "which descriptors are ready" from "what to do about it", so handlers can be
  tested on their own and new event sources are table entries rather than branches.
- Level-triggered readiness stays true until the bytes are consumed, so a handler must drain what
  it was told about or the loop spins.
- A descriptor that is only closed on the normal path is a leak; wrapping it in an object whose
  destructor closes it covers the paths you have not written yet.
- Descriptor numbers, port numbers and partial-write counts are machine-dependent, so they never
  belong in a transcript or a test.

## Practice

- [ ] Write a function that reads everything currently available from a non-blocking descriptor
  into a `std::string`, stopping on `EAGAIN` and on the peer closing. Send three separate messages
  from the other end first, and explain why they arrive as one read.
- [ ] Build a listener on `127.0.0.1:0`, connect three clients to it, and accept in a loop until
  `accept()` returns `EAGAIN`. Compare the number of turns that takes with one `accept()` per turn.
- [ ] Write a per-connection `Writer` that holds a `std::string` of pending bytes, sends what it
  can, and keeps the rest. Drive it with a megabyte against a peer that is not reading, then
  finish the transfer after `poll()` reports `POLLOUT`, and prove nothing was lost.
- [ ] Use `poll()`'s timeout to implement an idle timeout: a loop that wakes every 50 ms even
  when nothing happens, and prints what `poll()` returned in each case.
- [ ] Wrap a descriptor in a class whose destructor closes it, and prove with `/dev/fd` that the
  count returns to its starting value when the object leaves scope.
- [ ] Add a write queue to the server so that a response larger than the send buffer is delivered
  completely. Then make the client read slowly and confirm the server does not spin.

## Solutions

:::solution Exercise 1
Read until `EAGAIN`, and understand that what you have collected is everything that has *arrived*,
not the message:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

}  // namespace

#include <cstddef>
#include <cstdio>
#include <string>

// Reading until EAGAIN is how a non-blocking reader learns it has everything
// that has *arrived*. It is not the same as the whole message: only the
// protocol can say where a message ends, which is what a length prefix or a
// delimiter in the framing is for.
std::string drain(int fd) {
    std::string out;
    char buffer[4096];
    for (;;) {
        const ssize_t n = ::recv(fd, buffer, sizeof buffer, 0);
        if (n > 0) {
            out.append(buffer, static_cast<std::size_t>(n));
            continue;
        }
        // 0 is the peer closing, a negative return with EAGAIN is "come back
        // later", and any other negative return is a real error. Only the
        // first two are reasons to stop quietly.
        break;
    }
    return out;
}

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);

    ::send(fds[1], "abc", 3, 0);
    ::send(fds[1], "def", 3, 0);
    ::send(fds[1], "ghi", 3, 0);

    const std::string first = drain(fds[0]);
    std::printf("first drain:  %zu bytes, \"%s\"\n", first.size(), first.c_str());

    ::send(fds[1], "jkl", 3, 0);
    const std::string second = drain(fds[0]);
    std::printf("second drain: %zu bytes, \"%s\"\n", second.size(), second.c_str());
    std::printf("three sends arrived as one read of %zu bytes, not three of 3\n", first.size());

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
first drain:  9 bytes, "abcdefghi"
second drain: 3 bytes, "jkl"
three sends arrived as one read of 9 bytes, not three of 3
```

`first drain: 9 bytes, "abcdefghi"` -- three separate `send()` calls of three bytes each all landed
in the buffer before the reader ran, and one `recv()` loop collected them in one `std::string`.
There is no correspondence between the number of sends and the number of reads: **a read boundary
is not a message boundary.** Only the protocol can say where a message ends, which is why HTTP has
`Content-Length` and a blank-line delimiter, and why a server that forwards TCP bytes is a design
waiting for a bug.
:::

:::solution Exercise 2
Draining the accept queue costs one extra syscall when it is empty, and saves a turn per connection
when it is not:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

}  // namespace

#include <arpa/inet.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <netinet/in.h>
#include <vector>

int main() {
    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) return 1;

    struct sockaddr_in address;
    std::memset(&address, 0, sizeof address);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = 0;  // port 0 asks the kernel to choose one
    if (::bind(listener, reinterpret_cast<struct sockaddr *>(&address), sizeof address) != 0)
        return 1;
    if (::listen(listener, 8) != 0) return 1;
    set_nonblocking(listener);

    // Ask which port we were given. Nothing here prints it: a port number is
    // not stable across runs, so it never belongs in a transcript.
    socklen_t length = sizeof address;
    if (::getsockname(listener, reinterpret_cast<struct sockaddr *>(&address), &length) != 0)
        return 1;

    std::vector<int> clients;
    for (int i = 0; i < 3; ++i) {
        const int client = ::socket(AF_INET, SOCK_STREAM, 0);
        if (client < 0) continue;
        if (::connect(client, reinterpret_cast<struct sockaddr *>(&address), sizeof address) == 0)
            clients.push_back(client);
    }
    std::printf("clients connected: %zu\n", clients.size());

    // Accepting once per turn is how a server falls behind: the backlog grows
    // while it serves one connection at a time. Draining the queue costs one
    // extra syscall when it is empty, which is a bargain.
    int accepted = 0;
    for (;;) {
        const int fd = ::accept(listener, nullptr, nullptr);
        if (fd < 0) break;  // EAGAIN: the queue is empty
        ++accepted;
        ::close(fd);
    }
    std::printf("accept() returned %d connections, then EAGAIN\n", accepted);
    std::printf("one accept per turn would have taken 3 turns; this took one\n");

    for (const int client : clients) ::close(client);
    ::close(listener);
    return 0;
}
```

```text
clients connected: 3
accept() returned 3 connections, then EAGAIN
one accept per turn would have taken 3 turns; this took one
```

`accept() returned 3 connections, then EAGAIN` -- three connections in one turn, because the
listener was non-blocking and `EAGAIN` ended the loop cleanly. Doing it one per turn would have
taken three turns, during which the third client sits in the backlog. Under load the backlog is
what overflows, and a full backlog is a connection refused for a client who did nothing wrong.
:::

:::solution Exercise 3
The `Writer` keeps what the socket refused, and `flush()` tells the caller whether it finished:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

}  // namespace

#include <cstddef>
#include <cstdio>
#include <poll.h>
#include <string>
#include <utility>
#include <vector>

// A writer that never loses bytes: what cannot be sent now is kept, and the
// caller is told to come back when the descriptor is writable.
class Writer {
public:
    explicit Writer(int fd) : fd_(fd) {}

    void queue(std::string text) { pending_ += std::move(text); }

    // Returns true when the queue is empty, false when the socket is full.
    bool flush() {
        while (!pending_.empty()) {
            const ssize_t n = ::send(fd_, pending_.data(), pending_.size(), 0);
            if (n > 0) {
                pending_.erase(0, static_cast<std::size_t>(n));
                continue;
            }
            return false;  // EAGAIN (or a dead peer) -- either way, stop
        }
        return true;
    }

    std::size_t pending() const { return pending_.size(); }

private:
    int fd_;
    std::string pending_;
};

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    // Both ends. If the reading end blocks, a single-threaded program that
    // fills the socket and then tries to drain it waits forever for data only
    // it could have produced.
    set_nonblocking(fds[0]);
    set_nonblocking(fds[1]);

    Writer writer(fds[1]);
    const std::string big(1024 * 1024, 'z');
    writer.queue(big);

    const bool finished = writer.flush();
    std::printf("queued %zu bytes\n", big.size());
    std::printf("the first flush emptied the queue: %s\n", finished ? "yes" : "no");

    struct pollfd watch;
    watch.fd = fds[1];
    watch.events = POLLOUT;
    watch.revents = 0;

    std::vector<char> sink(256 * 1024);
    std::size_t received = 0;
    const auto drain_peer = [&] {
        for (;;) {
            const ssize_t n = ::recv(fds[0], sink.data(), sink.size(), 0);
            if (n <= 0) break;
            received += static_cast<std::size_t>(n);
        }
    };

    while (!writer.flush()) {
        drain_peer();  // the socket is full because nobody is emptying it
        watch.revents = 0;
        if (::poll(&watch, 1, 2000) <= 0) break;
    }
    drain_peer();

    std::printf("queue empty at the end: %s\n", writer.pending() == 0 ? "yes" : "no");
    std::printf("sent %zu bytes, the peer received %zu\n", big.size(), received);
    std::printf("nothing was lost: %s\n", received == big.size() ? "yes" : "NO");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
queued 1048576 bytes
the first flush emptied the queue: no
queue empty at the end: yes
sent 1048576 bytes, the peer received 1048576
nothing was lost: yes
```

`the first flush emptied the queue: no` is the whole lesson of a partly-full socket, and
`sent 1048576 bytes, the peer received 1048576` is the assertion that nothing was dropped. Note
the two ends are both non-blocking: a reader that blocks while the writer waits for space is a
single-threaded program deadlocking against itself -- which is exactly how this solution behaved
before the second `set_nonblocking` call was added.
:::

:::solution Exercise 4
A timeout is what turns the loop into a scheduler, so it can act on time as well as on events:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}

}  // namespace

#include <cstdio>
#include <poll.h>

int main() {
    int fds[2];
    if (!make_pair(fds)) return 1;
    set_nonblocking(fds[0]);

    struct pollfd watch;
    watch.fd = fds[0];
    watch.events = POLLIN;
    watch.revents = 0;

    // A timeout is what turns a blocking wait into a scheduler. With a deadline
    // the loop wakes up even when nothing happened, which is the only way a
    // single-threaded server can notice an idle or slow client.
    const int quiet = ::poll(&watch, 1, 50);
    std::printf("silent connection, 50 ms timeout -> poll() = %d\n", quiet);
    std::printf("that is %s\n", quiet == 0 ? "a timeout, not an error" : "unexpected");
    std::printf("revents after a timeout: %s\n", watch.revents == 0 ? "no events set" : "set");

    ::send(fds[1], "x", 1, 0);
    watch.revents = 0;
    const int ready = ::poll(&watch, 1, 50);
    std::printf("after one byte, same timeout  -> poll() = %d, immediately\n", ready);
    std::printf("readable: %s\n", (watch.revents & POLLIN) ? "yes" : "no");

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
silent connection, 50 ms timeout -> poll() = 0
that is a timeout, not an error
revents after a timeout: no events set
after one byte, same timeout  -> poll() = 1, immediately
readable: yes
```

`poll() = 0` after 50 ms with `no events set` in `revents`: a timeout is reported by the *return
value*, not by an error and not by a flag. This is the mechanism behind every idle timeout and
keepalive in a real server -- the loop wakes on a schedule, checks which connections have been
quiet for too long, and closes them. Without a timeout there is no moment at which "nothing
happened" is a thing the program can observe.
:::

:::solution Exercise 5
An object whose destructor closes the descriptor, and a measurement that proves it:

```cpp run
#include <cerrno>
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>

namespace {

// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }

}  // namespace

#include <cstdio>
#include <dirent.h>

// Counting the entries in /dev/fd is the only honest way to prove a descriptor
// was released. No sanitizer can see this leak: the descriptor belongs to the
// kernel, not to the heap, and macOS has no leak detector to ask anyway.
// Print the *difference*, never the absolute count -- the baseline depends on
// what the shell handed the process.
int open_descriptors() {
    DIR *dir = ::opendir("/dev/fd");
    if (dir == nullptr) return -1;
    int count = 0;
    while (::readdir(dir) != nullptr) ++count;
    ::closedir(dir);
    return count - 3;  // '.', '..' and the descriptor opendir itself used
}

// The Chapter 26 rule applied to a socket: if it is owned by an object, the
// destructor closes it on every path, including the one where an exception
// unwinds through the function.
class Descriptor {
public:
    explicit Descriptor(int fd) : fd_(fd) {}
    ~Descriptor() {
        if (fd_ >= 0) ::close(fd_);
    }
    Descriptor(const Descriptor &) = delete;
    Descriptor &operator=(const Descriptor &) = delete;
    int get() const { return fd_; }

private:
    int fd_;
};

int main() {
    const int baseline = open_descriptors();
    std::printf("baseline descriptor count differs per run; only the difference is printed\n");

    {
        int fds[2];
        if (!make_pair(fds)) return 1;
        Descriptor guard(fds[0]);
        ::send(fds[1], "x", 1, 0);
        ::close(fds[1]);  // the other end, closed by hand

        const int inside = open_descriptors();
        std::printf("while the guard is alive: %+d vs the baseline\n", inside - baseline);
    }

    const int after = open_descriptors();
    std::printf("after the guard's scope:  %+d vs the baseline\n", after - baseline);
    std::printf("the descriptor was released: %s\n", after == baseline ? "yes" : "NO");

    return 0;
}
```

```text
baseline descriptor count differs per run; only the difference is printed
while the guard is alive: +1 vs the baseline
after the guard's scope:  +0 vs the baseline
the descriptor was released: yes
```

`while the guard is alive: +1 vs the baseline` and `after the guard's scope: +0` -- the difference
is the only stable thing about that measurement, and printing the absolute count instead would
make the transcript depend on the shell. This is Chapter 26's RAII argument applied to a resource
the heap does not own, and it is the reason the server in this chapter can grow a new exit path
without growing a leak.
:::

:::solution Exercise 6
Give each connection a `Writer` and watch for `POLLOUT`:

```cpp
struct Connection {
    int fd;
    Writer out;                 // keeps the unsent remainder
    std::string in;             // accumulates until the request is complete
};
```

Poll `POLLOUT` **only** while `out.pending() > 0`. Registering it always means `poll()` returns
immediately for every connection that has room in its send buffer, which turns the loop back into
the busy-wait this chapter opened with. Once `out.flush()` returns true, drop the interest:

```cpp
short events_for(const Connection &c) {
    return c.out.pending() > 0 ? (POLLIN | POLLOUT) : POLLIN;
}
```

The measurable outcome: a 4 MB response delivered to a client that reads 64 KB at a time, with the
server's CPU near zero while it waits. If the server spins instead, the interest flag is being set
when the queue is empty.
:::
