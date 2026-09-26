#!/usr/bin/env python3
"""Generate chapters/41-async-io-and-the-event-loop.md.

Every `text` fence is captured from a real clang++ / curl run and every source
block is read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/41/gen.py
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"
OUT = CHAPTERS / "41-async-io-and-the-event-loop.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
TIMEOUT = 120


def run_clean(name: str) -> str:
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror", "-I", str(HERE), "-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if r.returncode != 0:
            raise SystemExit(f"{name} exited {r.returncode}:\n{r.stderr}")
        return r.stdout


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").rstrip("\n")


# A `run` block is compiled as ONE self-contained program in a temp directory, so
# it cannot include a shared header -- only a multi-file listing can. The demos
# keep #include "common.hpp" on disk (so they can be compiled here with -I) and
# the generator expands it, emitting only the helpers that file actually calls.
# Only the ones it calls: an unused function in an anonymous namespace is
# -Wunused-function, which is fatal under the harness's -Werror.
HELPERS = {
    "make_pair": """// A socketpair is two connected descriptors with no network in between: what is
// written to one end is readable at the other. It behaves like a connection in
// every way this chapter cares about -- it buffers, it fills up, and it can be
// made non-blocking -- without needing a port, a listener or a client.
bool make_pair(int fds[2]) { return ::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0; }""",
    "set_nonblocking": """// O_NONBLOCK is what makes a read report "not yet" instead of waiting.
bool set_nonblocking(int fd) {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) return false;
    return ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) == 0;
}""",
    "would_block": """// "Nothing to read yet" is a normal state on a non-blocking descriptor, not a failure.
bool would_block() { return errno == EAGAIN || errno == EWOULDBLOCK; }""",
}


def expanded(name: str) -> str:
    src = read(name)
    if '#include "common.hpp"' not in src:
        return src
    body = src.replace('#include "common.hpp"', "")
    used = [key for key in HELPERS if re.search(rf"\b{key}\s*\(", body)]
    block = "\n".join([
        "#include <cerrno>",
        "#include <fcntl.h>",
        "#include <sys/socket.h>",
        "#include <unistd.h>",
        "",
        "namespace {",
        "",
        "\n\n".join(HELPERS[key] for key in used),
        "",
        "}  // namespace",
    ])
    return src.replace('#include "common.hpp"', block)


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


def listing(names: list[str]) -> str:
    out = []
    for name in names:
        out.append(f"/* ===== {name} ===== */")
        out.append(read(name))
    return "\n\n".join(out)


print("capturing evidence ...")

simple = {}
for name in ("nonblocking", "readiness", "multiplex", "partial", "reactor"):
    simple[name] = run_clean(f"{name}.cpp")

sol_out = {}
for n in range(1, 6):
    sol_out[f"sol{n}"] = run_clean(f"sol{n}.cpp")

PROJECT = ["common.hpp", "poll_server.cpp", "Makefile"]
project_listing = listing(PROJECT)

with tempfile.TemporaryDirectory() as td:
    for name in PROJECT:
        (Path(td) / name).write_text(read(name) + "\n", encoding="utf-8")
    m = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=180)
    if m.returncode != 0:
        raise SystemExit(f"the project Makefile did not build:\n{m.stderr}")

    (Path(td) / "curl_run.sh").write_text(read("curl_run.sh") + "\n", encoding="utf-8")
    script = subprocess.run(["sh", "curl_run.sh"], text=True, capture_output=True,
                            cwd=td, timeout=120)
    if script.returncode != 0:
        raise SystemExit(f"curl_run.sh exited {script.returncode}:\n{script.stderr}")
    curl_out = script.stdout

print("generating chapter ...")

TEMPLATE = r"""---
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

@@nonblocking@@

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

@@readiness@@

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

@@multiplex@@

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

@@partial@@

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

@@reactor@@

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

@@project@@

Built with its own `Makefile`, and then driven by a real client. `curl` is a third-party program
that knows nothing about this code, which is what makes its agreement evidence rather than a
tautology:

@@curl@@

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

@@sol5@@

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

@@sol1@@

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

@@sol2@@

`accept() returned 3 connections, then EAGAIN` -- three connections in one turn, because the
listener was non-blocking and `EAGAIN` ended the loop cleanly. Doing it one per turn would have
taken three turns, during which the third client sits in the backlog. Under load the backlog is
what overflows, and a full backlog is a connection refused for a client who did nothing wrong.
:::

:::solution Exercise 3
The `Writer` keeps what the socket refused, and `flush()` tells the caller whether it finished:

@@sol3@@

`the first flush emptied the queue: no` is the whole lesson of a partly-full socket, and
`sent 1048576 bytes, the peer received 1048576` is the assertion that nothing was dropped. Note
the two ends are both non-blocking: a reader that blocks while the writer waits for space is a
single-threaded program deadlocking against itself -- which is exactly how this solution behaved
before the second `set_nonblocking` call was added.
:::

:::solution Exercise 4
A timeout is what turns the loop into a scheduler, so it can act on time as well as on events:

@@sol4@@

`poll() = 0` after 50 ms with `no events set` in `revents`: a timeout is reported by the *return
value*, not by an error and not by a flag. This is the mechanism behind every idle timeout and
keepalive in a real server -- the loop wakes on a schedule, checks which connections have been
quiet for too long, and closes them. Without a timeout there is no moment at which "nothing
happened" is a thing the program can observe.
:::

:::solution Exercise 5
An object whose destructor closes the descriptor, and a measurement that proves it:

@@sol5@@

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
"""

blocks = {
    "nonblocking": fence("cpp", "run", expanded("nonblocking.cpp"), simple["nonblocking"]),
    "readiness": fence("cpp", "run", expanded("readiness.cpp"), simple["readiness"]),
    "multiplex": fence("cpp", "run", expanded("multiplex.cpp"), simple["multiplex"]),
    "partial": fence("cpp", "run", expanded("partial.cpp"), simple["partial"]),
    "reactor": fence("cpp", "run", expanded("reactor.cpp"), simple["reactor"]),
    # `compile-files`, not `make-files`: `make-files` also RUNS the program it built,
    # and this program is a server that never exits -- it would sit at RUN_TIMEOUT and
    # fail the block. The Makefile is still exercised, by the `sh run-project` block
    # below, which builds the most recent listing with `make` before running the script.
    "project": fence("cpp", "compile-files", project_listing, None),
    "curl": fence("sh", "run-project", read("curl_run.sh"), curl_out),
}
for key, out in sol_out.items():
    blocks[key] = fence("cpp", "run", expanded(key + ".cpp"), out)

body = TEMPLATE
for key, value in blocks.items():
    body = body.replace("@@" + key + "@@", value.rstrip("\n"))

leftover = re.findall(r"@@(\w+)@@", body)
if leftover:
    raise SystemExit(f"unsubstituted placeholders: {leftover}")

OUT.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
words = len(re.findall(r"\b[\w'-]+\b", body))
print(f"wrote {OUT.name}: {len(body.splitlines())} lines, ~{words} words")
