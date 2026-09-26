#!/usr/bin/env python3
"""Generate chapters/40-concurrency-serving-many-clients.md.

Every `text` fence is captured from a real clang++ run and every source block is
read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/40/gen.py
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/40 -> gen -> tools -> cpp
OUT = CHAPTERS / "40-concurrency-serving-many-clients.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 120


def sanitizer_env() -> dict:
    env = dict(os.environ)
    env["ASAN_OPTIONS"] = "abort_on_error=0"
    env["UBSAN_OPTIONS"] = "print_stacktrace=0"
    return env


def build_and_run(name: str, sanitize: bool = False) -> str:
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror"] + (SAN if sanitize else []) + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td,
                           timeout=TIMEOUT, env=sanitizer_env())
        if r.returncode == 0:
            raise SystemExit(f"{name} was expected to be caught, but exited 0")
        return r.stderr


def run_clean(name: str) -> str:
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror", "-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if r.returncode != 0:
            raise SystemExit(f"{name} exited {r.returncode}:\n{r.stderr}")
        return r.stdout


def diagnostic(name: str) -> str:
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode == 0:
            raise SystemExit(f"{name} was supposed to be rejected, but it built cleanly")
        return b.stderr


def san_report(blob: str, needle: str) -> str:
    """The one line the `text` fence quotes: ERROR: AddressSanitizer: <kind>."""
    hit = re.search(r"ERROR: AddressSanitizer: ([a-z-]+)", blob)
    if not hit or needle not in blob:
        raise SystemExit(f"no {needle!r} in:\n{blob[:2000]}")
    return f"ERROR: AddressSanitizer: {hit.group(1)}"


def msg(blob: str, marker: str, needle: str) -> str:
    for line in blob.splitlines():
        if needle in line and marker in line:
            return "error: " + line.split(marker, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{blob}")


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").rstrip("\n")


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


# --------------------------------------------------------------------------
# capture
# --------------------------------------------------------------------------
print("capturing evidence ...")

join_out = run_clean("join.cpp")
capture_out = run_clean("capture.cpp")
mutex_out = run_clean("mutex.cpp")
scoped_out = run_clean("scoped.cpp")
deadlock_out = run_clean("deadlock.cpp")
atomic_out = run_clean("atomic.cpp")
tls_out = run_clean("tls.cpp")
futures_out = run_clean("futures.cpp")
scenario_out = run_clean("scenario.cpp")

capture_bad_err = build_and_run("capture_bad.cpp", sanitize=True)
dangling_err = build_and_run("dangling.cpp", sanitize=True)
CAPTURE_BAD = san_report(capture_bad_err, "stack-use-after-scope")
DANGLING = san_report(dangling_err, "stack-use-after-scope")

badmutex_err = diagnostic("badmutex.cpp")
BADMUTEX = msg(badmutex_err, "error:", "deleted constructor of 'std::mutex'")

PROJECT = ["pool.h", "pool.cpp", "main.cpp", "Makefile"]
project_listing = listing(PROJECT)

with tempfile.TemporaryDirectory() as td:
    for name in PROJECT:
        (Path(td) / name).write_text(read(name) + "\n", encoding="utf-8")
    m = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=180)
    if m.returncode != 0:
        raise SystemExit(f"the project Makefile did not build:\n{m.stderr}")
    p = subprocess.run(["./prog"], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
    if p.returncode != 0:
        raise SystemExit(f"the project exited {p.returncode}:\n{p.stderr}")
    project_out = p.stdout

with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(["sh", str(HERE / "race.sh")], text=True, capture_output=True,
                       cwd=td, timeout=180)
    if r.returncode != 0:
        raise SystemExit(f"race.sh exited {r.returncode}:\n{r.stderr}")
    race_out = r.stdout

sol_out = {}
for n in range(1, 6):
    sol_out[f"sol{n}"] = run_clean(f"sol{n}.cpp")

print("generating chapter ...")

TEMPLATE = r"""---
chapter: 40
part: 5
title: Concurrency — Serving Many Clients
summary: Serve many clients at once with threads, bound the work with a pool, protect the shared state with mutexes and atomics, and let ThreadSanitizer prove the race instead of a customer.
minutes: 70
tags: [threads, mutex, atomic, thread pool, data race, deadlock, sanitizer, condition_variable]
---

Chapter 20 gave the server a loop that accepts one connection, serves it, closes it, and comes
back for the next. That is the simplest correct server, and it has a cost you can measure: while
one client is being read, every other client is waiting in the kernel's backlog, and a slow client
holds the whole process. The fix is to do more than one thing at once.

C++ concurrency has a property nothing else in this book has: **a program can be wrong without
ever being broken**. A data race does not throw, does not return an error, and usually does not
crash. It returns a plausible answer most of the time, and the exceptions cluster around the worst
possible moment. That is why this chapter builds from one thread to a pool one small step at a
time, and why every failure mode here gets measured with a sanitizer rather than described.

Everything below compiles with `-std=c++17 -Wall -Wextra -Werror`, as always. One platform note
before we start: on this macOS toolchain `std::thread`, `std::mutex` and `std::atomic` link
without any extra flag, but on Linux the same code needs `-pthread` on both the compile and the
link line. The book's Makefiles pass it, so the recipes below work in both places.

## One thread, one job

`std::thread` takes anything callable and starts running it immediately — construction is the
start, not a request to start.

@@join@@

Two things about that program are load-bearing.

The first is the printed order. Every thread writes into its own slot of `squares`, and the
results are read after the joins, so the output is `0 1 4 9` — the order the values were
*requested* in, not the order the threads happened to run in. Threads got to slot 1 before slot 0
and you cannot tell from the output. **Print order is never evidence about execution order**, and
a program whose correctness depends on which thread runs first is a program you cannot test.

The second is `join()`. It is a wait and it is also an ownership transfer: it says "this thread is
finished, and the main thread is no longer responsible for it." If you let a `std::thread`
destructor run while the thread is still joinable — never joined, never detached — the standard
library calls `std::terminate` and the process dies on the spot. There is no exception, no error
message from your code, and a stack trace that points at the destructor rather than at the missing
`join()`. When a concurrency program dies instantly with no output, this is the first thing to look
for.

:::note `join()` before you can see the result
A join is not just cleanup. Until it returns, the thread's writes are not guaranteed to be visible
to `main`, and reading `squares` before the joins would be a data race. The rule is not "join at
the end" but "every read of a thread's output happens after a join".
:::

## The bug you will write first

This is the mistake that costs a day, because the program usually works. Here is the correct
version, with the loop variable captured **by value**:

@@capture@@

`[&, i]` means: capture everything by reference, *except* `i`, which is copied per thread. Each
lambda gets its own private integer taken at the moment the lambda was created, so by the time the
threads actually run it does not matter what the loop variable is doing.

Now delete that one character — capture the loop variable by reference too:

@@capture_bad@@

It compiles and it often prints something reasonable. AddressSanitizer, which compiles this block
with `-fsanitize=address,undefined`, has no such patience, and the report names the real problem:
**`stack-use-after-scope`**. The variable `i` in a
`for (int i = 0; ...)` lives in the loop's scope, which ended before `go` was ever set. Every
lambda still holds a reference to storage that no longer belongs to it — the same dangling
reference Chapter 25 is about, except here the compiler cannot see it because a lambda capture is
not a named local. If the stack slot happens to still read `4`, the write lands one past the end
of `results` as well, and you get a corrupted vector on top of a bad read. Both are symptoms; the
sanitizer reports the one it hits first.

The rule is short. **A thread's captures must outlive the thread**, and a loop variable never
does. Capture it by value, or copy it into a local first:

```cpp
for (int i = 0; i < 4; ++i) {
    const int slot = i;                 // ordinary local, one per iteration
    threads.emplace_back([&results, slot] { results[slot] = slot; });
}
```

That version makes the lifetime explicit, which is the point. An explicit capture list is not
verbosity; it is the compiler being told what to check.

### The same bug arriving from the other direction

The capture bug hands a thread a reference to something short-lived. The mirror image is a thread
that simply outlives what it was given:

@@dangling@@

Same report, `stack-use-after-scope`, different blame. The capture was correct here: `request`
really was alive when the thread was created, and the lambda asked for exactly the one thing it
needed. The bug is that **the thread was still running when the scope closed** — the join came
after the owner was gone. `worker` is declared outside the block for that reason alone: a
`std::thread` created inside a scope and left joinable there calls `std::terminate` at the closing
brace, which is a different failure, and arguably a kinder one than reading freed memory.

Two habits cover both directions. Keep a thread's lifetime inside the lifetime of everything it
touches — declare the owner first, join before its scope ends. And when a thread genuinely must
outlive its data, let it **own** that data: move the string into the lambda instead of referring to
it, and the question never arises.

## Protecting shared state

Threads that never share anything never need a lock, and a design where threads share nothing is
better than any amount of locking. That is not always available — a log, a counter, a connection
cache are shared by definition.

@@mutex@@

`entries = 4000` is the assertion, and the per-thread breakdown is what proves the lock did
something: without it, four threads calling `push_back` on the same `std::vector` corrupt the
size and the data pointer, because reallocation is a multi-step operation. The output would be a
smaller number, or a crash, or — and this is the bad case — the right answer.

Two details in that function are not decoration:

- **`std::lock_guard` and not `lock()` / `unlock()`.** The guard unlocks in its destructor, so it
  unlocks on every exit path, including the one where `push_back` throws `std::bad_alloc`. A
  manual pair leaves the mutex held forever and every other thread blocks on it — a deadlock that
  only happens when the machine is out of memory.
- **The mutex is a member, and it is the only way in.** `entries` is at file scope in this example
  so the demo is short, but the shape you want is Chapter 24's: the mutex and the data it protects
  live in the same class, `private`, and no public member touches the data without taking the
  lock. A mutex that is not attached to its data is a convention, and conventions do not compile.

A mutex is a resource, and resources here behave like the ones in Chapter 25 — non-copyable,
because two objects cannot both own one lock:

@@badmutex@@

That diagnostic is the language doing you a favour. A copyable mutex would give you two objects,
each believing it holds the lock, both proceeding — which is not a deadlock but a race, and much
harder to find.

## Deadlock, the failure that looks like a hang

Two threads, two locks, taken in opposite orders. Neither thread can proceed, neither can be
preempted, and no thread will ever release what it holds:

@@deadlock@@

Both lines say `TIMED OUT`, and that is deliberate. A real deadlock never prints anything: the
program simply stops, and the only evidence is a stack trace of two threads parked in `lock()`.
Showing it with `try_lock_for` makes the same failure *observable* — the thread says "I waited
300 ms and the lock never came" and keeps going, which is exactly what you want in production code
and exactly what a teaching example needs.

The four conditions that must all hold for a deadlock, named by Coffman and worth memorising
because breaking any one of them prevents it:

1. **Mutual exclusion** — the resource really is exclusive.
2. **Hold and wait** — a thread holds one lock while requesting another.
3. **No preemption** — nobody can take a lock away.
4. **Circular wait** — A waits for B's lock while B waits for A's.

You cannot remove 1 (that is the point of a lock) and you will not add 3 to a `std::mutex`. What
you *can* do is remove 4 — and the standard library does it for you.

### One order for every lock

`std::scoped_lock` takes any number of mutexes and acquires them all with the deadlock-avoiding
algorithm, so the order you write them in does not matter and the second lock is never requested
while the first is held:

@@scoped@@

Two threads churn the same pair of accounts in opposite directions, 2000 transfers each, and
`alice = 5000, bob = 5000, money is conserved`. The sum is the assertion that matters: **a
transfer is two writes, and a partial transfer is money that does not exist.** If the second write
could be skipped — no lock, or a lock that only covers one of the two updates — the total would
drift below 10000 and the program would still exit 0.

:::warning `std::lock`'s algorithm needs both locks to be the same kind
`std::scoped_lock` calls `std::lock` in a loop, and `std::lock` on a plain `std::mutex` is what
makes the order irrelevant. If you write to two *different* mutex types it will fall back to
recursive locking, which means you own the ordering yourself. Two mutex types and one transfer
path is a design smell, not a code smell.
:::

## When a mutex is too much: atomics

A mutex protects a *region* of code. When the shared state is a single value and the operation is
a single instruction's worth of work, the atomic types say so directly — and on a plain integer
that is not merely shorter, it is a different instruction:

@@atomic@@

Read the output as three separate lessons.

`is_lock_free()` answers the question people ask about atomics and rarely check: **is this
implemented without a lock?** Here, on this arm64 macOS, both are — the answer is platform
dependent, and on some 32-bit targets a 64-bit atomic is implemented with a hidden mutex, which
means code that "uses atomics instead of a mutex" can be using one. If the answer matters, print
it and say which target you measured.

`counter = 200000` after four threads × 50000 increments is the assertion. The equivalent with a
plain `int` is not "usually slightly less" — it is undefined behaviour, and the increments that
vanish are the read-modify-write sequences that interleaved. We will prove that with
ThreadSanitizer below rather than asserting it.

`exchange(99) returned 200000, now 99` is the simplest atomic primitive that a mutex cannot
express: swap and hand back the old value, in one step, with no window in between. The
`compare_exchange_weak` pair shows the one every lock-free structure is built on — *if it is still
`expected`, write `desired`; otherwise tell me what it really is* — and the second call is the
interesting one, because it **lost** and updated `expected` from 0 to 100. A lost
compare-exchange is not an error; it is the mechanism reporting what it saw. `_weak` may also fail
spuriously, which is why it belongs in a loop.

:::danger An atomic is not a small mutex
An atomic makes *one object* safe to touch from two threads. The moment the invariant spans two
objects, it stops helping: `if (a + b < limit) { ++a; ++b; }` is three separate atomic operations
with two windows between them, and another thread can observe the halfway state. That needs a
mutex covering all of it. The test is not "is it a single variable" — it is "can another thread
see a state that must never exist". If yes, you need a critical section, however short.
:::

## Per-thread state instead of shared state

The cheapest lock is the one you do not need. If each thread wants its own copy of something,
`thread_local` gives it one — a separate object per thread with static storage duration inside that
thread:

@@tls@@

The main thread never called `record_call`, so its own `calls` is 0 while each worker's reached 3.
There is nothing to synchronise because there is nothing shared: three separate objects that happen
to have the same name. This is how a per-worker buffer or a per-thread random generator is normally
written, and it removes the contention a shared counter would create even when it is correct.

Two limits worth knowing before reaching for it. `thread_local` storage is constructed on first
use **in that thread**, so its destructor runs at thread exit — an object that must outlive its
thread (a cache the whole service shares, for example) cannot live there. And with a thread pool
the object is per *worker*, not per *request*: a request that lands on worker 3 and then on worker
1 sees two different objects, and any state you were hoping to carry across the two is gone.

## Handing work over: futures

Starting a thread and hoping you can collect the answer later is how a program ends up with global
variables for results. A future is the answer:

@@futures@@

Two lines there are the reason to prefer this shape over raw threads. `get()` **rethrows** the
exception the task threw, which means a failing job does not have to kill the process — it arrives
at whoever asked for the value. And `wait_for` lets a caller give up instead of blocking forever,
which is what a request handler with a deadline needs. The catch worth remembering: if nobody ever
calls `get()`, the exception is still stored, then discarded when the future is destroyed — the
worker failed and the program carried on as if it had not.

## The thread pool

One thread per connection is a bomb with a slow fuse. It is not that threads are slow; it is that
each one costs a stack (8 MB by default on Linux, and a real amount of address space on macOS) and
a scheduler slot. At a thousand concurrent clients you have spent 8 GB of stacks before doing any
work, and context switching starts dominating the actual computation. The pool replaces that with a
**bound**: a fixed number of workers pulling from one queue.

Here is the whole module — header, implementation, and a program that uses it as a service would,
with its own `Makefile`. As in the earlier project chapters, the `/* ===== name ===== */` lines are
listing separators, not file contents:

@@project@@

The output is the assertion that the bound held: eight slices of 50000 numbers, four workers,
33,860 primes, `submitted = 8, completed = 8`. The slice results arrive in *submission* order
because the futures are collected in order — the workers finished them in whatever order they got
to them, and the program does not care.

Three decisions in `ThreadPool` are worth reading twice, because each one is a bug in the version
that skips it.

**The wait predicate is not optional.** `ready_.wait(guard, predicate)` re-checks the condition
every time it wakes. A condition variable is allowed to wake *spuriously* — no notification, no
new job — and a bare `wait()` that then pops `queue_.front()` on an empty queue is undefined
behaviour. The predicate is what turns "I woke up" into "I woke up and there is work".

**`notify_one` when a job arrives, `notify_all` when shutting down.** One job is one worker's
worth of work, so waking all of them to have three go back to sleep is pure contention. But the
destructor sets `stopping_` and then has to wake *every* worker, because every worker is parked in
`wait()` and each one needs to see the flag. Getting this backwards is the classic pool bug: the
program hangs on exit, and the stack trace shows threads that will never be woken.

**The destructor is the shutdown protocol, and RAII is why it works.** `~ThreadPool` sets the flag
under the lock, notifies, and joins every worker. Because it is a destructor, it runs on every
exit path — normal return, early return, an exception unwinding through `main`. A pool with a
separate `stop()` that callers must remember to call is a pool that leaks threads the first time
somebody adds an early return.

`submit` returns a future rather than a value for the same reason `std::async` does: the caller
decides when to wait. That is what makes the pool usable from a request handler, where waiting is
the one thing you must not do while holding anything else.

:::note Why not a thread per request, with a cap
A cap on threads-per-request is a pool with extra steps and one extra failure: under load, the
arrival rate exceeds the service rate, the queue grows, and the cap turns into a rejection or an
unbounded backlog. A pool makes the queue explicit, which means you can measure it, bound it, and
decide what to do when it is full — which is Chapter 43's job.
:::

## Proving the race

Everything so far has an output fence, which proves what the program printed. That is not enough
for a race: the wrong version of `counter` *usually prints the right answer*, so a `run` block
would pass and teach nothing. ThreadSanitizer is the tool that sees the thing the output cannot:

@@race@@

The script compiles the same program twice and runs it both ways. With a plain `int`, two threads
incrementing `plain` 50000 times each is a data race, and ThreadSanitizer reports it — the process
aborts with a report naming both stacks. With `std::atomic<int>` and `fetch_add`, the run is clean:
`guarded = 100000`, no warning, no report.

Two caveats belong with that evidence. `-fsanitize=thread` is a **separate build** — it is not part
of `-fsanitize=address,undefined` and cannot be combined with it, so a TSan run means recompiling.
And it costs roughly five to fifteen times the runtime, which is why it goes in the test suite and
not in production. It is available on this machine; if `clang++` reports an unknown sanitizer on
yours, that toolchain was built without it, and the fallback is a design review of every shared
variable.

:::scenario The counter that is short under load
A service reports `requests served` from a `/stats` endpoint. Under a load test the number comes
back a few hundred short, never long, and never in development. The code is one line in the
request handler: `++requests_served;`, where `requests_served` is a plain `long` at file scope.

The diagnosis is not a guess. "Never long, sometimes short" is the signature of a lost update: two
workers read the same value, both add one, both write back, and one increment disappears. It only
shows under load because the window is a few nanoseconds wide, and a laptop with one request at a
time never lands in it.
:::

:::solution Short counter, or a lock?
The fix depends on what else is in the structure, which is the part people get wrong in the
opposite direction. A lone counter is an atomic — the whole update is one instruction's worth and
nothing else has to agree with it. The moment the counter is one of several fields that must be
consistent with each other, an atomic is the wrong tool and the whole group needs one mutex:

@@scenario@@

`counts agree: yes` is the point. The atomic protects the single number; the mutex protects the
vector and its invariant. Reach for the atomic where an atomic is enough, and for the mutex where
"two fields agree" is the thing being promised — a service that reports 40000 requests and 39998
latencies is more alarming than one that reports both slightly wrong.
:::

:::pitfall Five ways this chapter's bug comes back
- **Capturing the loop variable by reference.** Covered above; it is the first one everybody
  writes. The fix is `[&, i]` or an explicit local, never a bare `[&]`.
- **Forgetting `join()` on a path.** Any early `return` or thrown exception between starting a
  thread and joining it calls `std::terminate`. If several threads are started, hold them in a
  `std::vector<std::thread>` and join in a loop, so there is one exit path and not five.
- **Holding a lock while calling out.** Calling a callback, writing a log, or acquiring a second
  lock *while holding* the first is how hold-and-wait becomes circular. Take the lock, copy what
  you need, release it, then call out.
- **A spin loop instead of a condition variable.** `while (!ready) {}` burns a core, and without an
  atomic or a fence around `ready` it is also a data race the optimiser is allowed to hoist out of
  the loop entirely. It looks like it works on `-O0` and never terminates on `-O2`.
- **Assuming a `std::vector` is safe to share because each thread touches a different index.**
  Different elements are different objects, so that part is fine — until one `push_back`
  reallocates and the threads holding pointers or references into the old buffer are writing to
  freed memory. Reserve, or index into a fixed-size container.
:::

## Key takeaways

- A `std::thread` starts running when it is constructed, and a joinable thread that is never
  joined or detached calls `std::terminate` from its destructor.
- Print order is not execution order. Test by joining and then reading, never by reading output
  order.
- A lambda's captures must outlive the thread. Capturing a loop variable by reference is undefined
  behaviour, and AddressSanitizer reports it as `stack-use-after-scope`.
- `std::lock_guard` unlocks on every exit path; a manual `lock()`/`unlock()` pair does not, and the
  failure mode is a permanently held lock rather than an error.
- A mutex is neither copyable nor movable, because one lock cannot have two owners.
- Deadlock needs all four of mutual exclusion, hold-and-wait, no preemption and circular wait;
  `std::scoped_lock` removes the fourth by acquiring all its mutexes with the deadlock-avoiding
  algorithm.
- An atomic makes one object safe. An invariant spanning two objects needs a mutex, however short
  the region.
- A condition variable's wait takes a predicate, `notify_one` is for work and `notify_all` is for
  shutdown, and the pool's destructor is the place the shutdown protocol belongs.
- ThreadSanitizer is a separate build (`-fsanitize=thread`) that finds the races whose output looks
  correct.

## Practice

- [ ] Build a program with four threads that each write their own slot of a `std::vector<int>` and
  print the vector after joining. Then change the capture to `[&]` and explain what the sanitizer
  says and why.
- [ ] Build a `Counter` class whose `std::mutex` is a private member, with `add(int)`, `value()`
  and a `try_add(int)` that refuses rather than waits. Drive it from four threads and print the
  total, then show `try_add` refusing while another thread holds the lock.
- [ ] Build a statistics cache that one writer updates and three readers read, using
  `std::shared_mutex` so the readers do not serialise against each other. Prove that the writer
  cannot get in while a reader holds a shared lock.
- [ ] Build four accounts and eight threads transferring between neighbours in both directions.
  Impose a single order on the two locks using their addresses, and print the per-account balances
  and the total.
- [ ] Extend the pool with a `wait()` that blocks until every submitted job has finished, then
  submit twenty jobs and print the totals before and after. Explain why the predicate must count
  jobs *in flight* and not just jobs queued.
- [ ] Hand one result, and one failure, from a worker thread to whoever is waiting, using a
  `std::promise` / `std::future` pair. Include the third case: a promise that is destroyed without
  ever being fulfilled.

## Solutions

:::solution Exercise 1
The vector is fixed-size and each thread owns one index, so the writes do not conflict — the
capture is the whole bug:

```cpp
results[static_cast<std::size_t>(i)] = i;   // with [&, i]  -- one slot per thread
results[static_cast<std::size_t>(i)] = i;   // with [&]    -- all four read the same i
```

With `[&]` the report is `stack-use-after-scope`: `i` belonged to the loop's scope, the loop
finished before any thread ran, and every thread dereferences a stale reference. If the stale slot
still reads `4`, the write also lands past the end of `results`. Capturing the loop variable by
value — `[&, i]`, or an explicit `const int slot = i;` — fixes both.
:::

:::solution Exercise 2
The mutex is a member, so it cannot be forgotten at the call site, and `try_add` returns a bool
instead of waiting:

@@sol1@@

`try_add while held: refused` is the measured proof that `std::try_to_lock` does not block.
`while free : got the lock` shows the same call succeeding a moment later, and the final counter is
200001 — the one successful `try_add` on top of the 200000 from the four threads.
:::

:::solution Exercise 3
`std::shared_mutex` plus `std::shared_lock` lets any number of readers in and keeps the writer out
until the last one leaves:

@@sol2@@

All three readers report `reader saw 3 readers inside` — a shared lock does not exclude another
shared lock, which is the entire reason this type exists. The writer was started while all three
still held theirs, and `writer got in while they held it : no` is the assertion; the value is
updated to 7 only after `release` lets the readers out.

Note the two waits in the code, which are not the same thing. `holding` counts threads that have
*entered* the lock; `recorded` counts threads that have *stored their result*. Waiting on the first
and then reading `seen` races with the writes and prints the vector's initial `0` — a data race in
the code that reads the evidence, which is where it is least expected and exactly what this
program printed before the second wait was added.

Note also the ordering constraint: the writer must be created *before* the check, or the program
would be measuring whether a thread had started rather than whether the lock was free.
:::

:::solution Exercise 4
Impose one order on the two locks — and the only order every thread can agree on without
coordination is the addresses:

@@sol3@@

`account 0..3 = 1000` and `total = 4000` after eight threads did 4000 transfers: nothing was lost
and nothing deadlocked. If either thread had locked in argument order instead, the pattern
`transfer(a, b)` from one thread and `transfer(b, a)` from another is precisely the deadlock from
the `deadlock.cpp` example, and the difference is the two lines that sort the pointers.

This is also the version to reach for when the locks are not both available at once — address
ordering is a *global* rule that any thread can apply locally, so it composes across a codebase in
a way that "always lock the account before the session" does not.
:::

:::solution Exercise 5
`wait()` needs one predicate that covers both halves of "idle": the queue is empty **and** no
worker is mid-job:

@@sol4@@

`after wait(): submitted = 20, completed = 20` is the proof it waited correctly, and the workers
are still alive to prove that `wait()` is not `stop()`. Without the `busy_ == 0` half, a worker
that had already popped the last job but not finished it would let `wait()` return early — the
queue is empty, the work is not done, and the caller collects a future that is not ready.
:::

:::solution Exercise 6
`std::promise` is the writing end of a future you create yourself, which is how a worker reports one
result or one failure to whoever is waiting:

@@sol5@@

Three cases, one API: `worker answered: 42` is the ordinary path;
`delivered through the future: connection reset by peer` is an exception moved across the thread
boundary with `set_exception` and `std::current_exception`; and
`broken promise: The associated promise has been destructed prior to the associated state becoming
ready.` is the third — a promise destroyed without being fulfilled, which breaks its future with
`std::future_error`. That message text is libc++'s wording; the standard only fixes that the
exception is a `std::future_error` with `broken_promise` as its code.
:::
"""

blocks = {
    "join": fence("cpp", "run", read("join.cpp"), join_out),
    "capture": fence("cpp", "run", read("capture.cpp"), capture_out),
    "capture_bad": fence("cpp", "run-san-catch", read("capture_bad.cpp"), CAPTURE_BAD),
    "dangling": fence("cpp", "run-san-catch", read("dangling.cpp"), DANGLING),
    "mutex": fence("cpp", "run", read("mutex.cpp"), mutex_out),
    "badmutex": fence("cpp", "bad", read("badmutex.cpp"), BADMUTEX),
    "deadlock": fence("cpp", "run", read("deadlock.cpp"), deadlock_out),
    "scoped": fence("cpp", "run", read("scoped.cpp"), scoped_out),
    "atomic": fence("cpp", "run", read("atomic.cpp"), atomic_out),
    "tls": fence("cpp", "run", read("tls.cpp"), tls_out),
    "futures": fence("cpp", "run", read("futures.cpp"), futures_out),
    "project": fence("cpp", "make-files", project_listing, project_out),
    "race": fence("sh", "run", read("race.sh"), race_out),
    "scenario": fence("cpp", "run", read("scenario.cpp"), scenario_out),
}
for key, out in sol_out.items():
    blocks[key] = fence("cpp", "run", read(key + ".cpp"), out)

body = TEMPLATE
for key, value in blocks.items():
    body = body.replace("@@" + key + "@@", value.rstrip("\n"))

leftover = re.findall(r"@@(\w+)@@", body)
if leftover:
    raise SystemExit(f"unsubstituted placeholders: {leftover}")

OUT.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
words = len(re.findall(r"\b[\w'-]+\b", body))
print(f"wrote {OUT.name}: {len(body.splitlines())} lines, ~{words} words")
