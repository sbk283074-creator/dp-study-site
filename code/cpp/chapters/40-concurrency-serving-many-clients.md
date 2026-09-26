---
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

```cpp run
#include <cstdio>
#include <thread>
#include <utility>
#include <vector>

// Each thread writes into its own slot, so the printed order is the order the
// results were requested in -- not the order the threads happened to run.
int main() {
    std::vector<int> squares(4);
    std::vector<std::thread> threads;

    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([i, &squares] { squares[static_cast<std::size_t>(i)] = i * i; });
    }

    std::printf("before join, main is still running\n");
    for (std::thread &t : threads) t.join();
    std::printf("after join, every thread has finished\n");

    for (int v : squares) std::printf("%d ", v);
    std::printf("\n");
    return 0;
}
```

```text
before join, main is still running
after join, every thread has finished
0 1 4 9 
```

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

```cpp run
#include <atomic>
#include <cstdio>
#include <thread>
#include <vector>

// `[&, i]` captures the loop variable by value. Every thread gets its own copy,
// taken at the moment the lambda was created.
int main() {
    std::atomic<bool> go{false};
    std::vector<int> results(4, -1);
    std::vector<std::thread> threads;

    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&, i] {
            while (!go.load()) {
            }
            results[static_cast<std::size_t>(i)] = i;
        });
    }

    go.store(true);
    for (std::thread &t : threads) t.join();
    for (int v : results) std::printf("%d ", v);
    std::printf("\n");
    return 0;
}
```

```text
0 1 2 3 
```

`[&, i]` means: capture everything by reference, *except* `i`, which is copied per thread. Each
lambda gets its own private integer taken at the moment the lambda was created, so by the time the
threads actually run it does not matter what the loop variable is doing.

Now delete that one character — capture the loop variable by reference too:

```cpp run-san-catch
#include <atomic>
#include <cstdio>
#include <thread>
#include <vector>

// `[&]` captures the loop variable by reference. The loop is over by the time
// any thread runs, so every thread reads the same `i` -- and that `i` is 4,
// one past the end of the vector.
int main() {
    std::atomic<bool> go{false};
    std::vector<int> results(4, -1);
    std::vector<std::thread> threads;

    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&] {
            while (!go.load()) {
            }
            results[static_cast<std::size_t>(i)] = i;
        });
    }

    go.store(true);
    for (std::thread &t : threads) t.join();
    for (int v : results) std::printf("%d ", v);
    std::printf("\n");
    return 0;
}
```

```text
ERROR: AddressSanitizer: stack-use-after-scope
```

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

```cpp run-san-catch
#include <atomic>
#include <cstdio>
#include <string>
#include <thread>

std::atomic<bool> go{false};

// A detached thread that outlives what it captured. The thread is still
// runnable when the enclosing scope ends, and it reads a string that no longer
// exists.
int main() {
    std::thread worker;
    {
        std::string request(64, 'x');
        worker = std::thread([&] {
            while (!go.load()) {
            }
            std::printf("worker read %zu bytes\n", request.size());
        });
    }  // `request` is destroyed here

    go.store(true);
    worker.join();
    return 0;
}
```

```text
ERROR: AddressSanitizer: stack-use-after-scope
```

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

```cpp run
#include <cstdio>
#include <map>
#include <mutex>
#include <thread>
#include <vector>

std::vector<int> entries;
std::mutex log_mutex;

void record(int id, int times) {
    for (int i = 0; i < times; ++i) {
        // lock_guard unlocks on every exit path, including an exception thrown
        // by push_back. A manual lock()/unlock() pair would leave it held.
        std::lock_guard<std::mutex> guard(log_mutex);
        entries.push_back(id);
    }
}

int main() {
    std::vector<std::thread> threads;
    for (int id = 0; id < 4; ++id) threads.emplace_back(record, id, 1000);
    for (std::thread &t : threads) t.join();

    std::printf("entries = %zu\n", entries.size());
    std::map<int, int> per_thread;
    for (int id : entries) ++per_thread[id];
    for (const auto &[id, count] : per_thread) std::printf("  thread %d wrote %d\n", id, count);
    return 0;
}
```

```text
entries = 4000
  thread 0 wrote 1000
  thread 1 wrote 1000
  thread 2 wrote 1000
  thread 3 wrote 1000
```

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

```cpp bad
#include <mutex>

int main() {
    std::mutex original;

    // A mutex is a movable, non-copyable resource: two objects cannot both own
    // the same lock. The compiler refuses rather than letting two threads
    // believe they hold it.
    std::mutex copy = original;
    return 0;
}
```

```text
error: call to deleted constructor of 'std::mutex'
```

That diagnostic is the language doing you a favour. A copyable mutex would give you two objects,
each believing it holds the lock, both proceeding — which is not a deadlock but a race, and much
harder to find.

## Deadlock, the failure that looks like a hang

Two threads, two locks, taken in opposite orders. Neither thread can proceed, neither can be
preempted, and no thread will ever release what it holds:

```cpp run
#include <array>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <mutex>
#include <string>
#include <thread>

std::timed_mutex first;
std::timed_mutex second;

std::atomic<int> holding{0};
std::atomic<int> tried{0};
std::array<std::string, 2> outcome;

// Two threads, two locks, opposite orders. The barriers make this observation
// rather than a race: both threads hold their first lock before either asks for
// the second, and neither releases it until both have finished asking.
void take_both(int who) {
    std::timed_mutex &mine = who == 0 ? first : second;
    std::timed_mutex &theirs = who == 0 ? second : first;
    {
        std::unique_lock<std::timed_mutex> held(mine);
        holding.fetch_add(1);
        while (holding.load() < 2) {
        }

        const bool got = theirs.try_lock_for(std::chrono::milliseconds(300));
        outcome[static_cast<std::size_t>(who)] = got ? "acquired" : "TIMED OUT";
        if (got) theirs.unlock();

        tried.fetch_add(1);
        while (tried.load() < 2) {
        }
    }
}

int main() {
    std::thread a(take_both, 0);
    std::thread b(take_both, 1);
    a.join();
    b.join();
    std::printf("thread 0 second lock: %s\n", outcome[0].c_str());
    std::printf("thread 1 second lock: %s\n", outcome[1].c_str());
    return 0;
}
```

```text
thread 0 second lock: TIMED OUT
thread 1 second lock: TIMED OUT
```

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

```cpp run
#include <array>
#include <atomic>
#include <cstdio>
#include <mutex>
#include <thread>

struct Account {
    int balance = 0;
    std::mutex mutex;
};

Account alice;
Account bob;

// std::scoped_lock takes any number of mutexes and acquires them with
// std::lock's deadlock-avoiding algorithm, so the order does not matter.
void transfer(Account &from, Account &to, int amount) {
    std::scoped_lock lock(from.mutex, to.mutex);
    from.balance -= amount;
    to.balance += amount;
}

void churn(int who) {
    for (int i = 0; i < 2000; ++i) {
        if (who == 0) {
            transfer(alice, bob, 1);
        } else {
            transfer(bob, alice, 1);
        }
    }
}

int main() {
    alice.balance = 5000;
    bob.balance = 5000;

    std::array<std::thread, 4> threads;
    for (int i = 0; i < 4; ++i) threads[static_cast<std::size_t>(i)] = std::thread(churn, i % 2);
    for (std::thread &t : threads) t.join();

    std::printf("alice = %d, bob = %d\n", alice.balance, bob.balance);
    std::printf("sum   = %d (started at 10000)\n", alice.balance + bob.balance);
    std::printf("money is %s\n", alice.balance + bob.balance == 10000 ? "conserved" : "MISSING");
    return 0;
}
```

```text
alice = 5000, bob = 5000
sum   = 10000 (started at 10000)
money is conserved
```

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

```cpp run
#include <atomic>
#include <cstdio>
#include <thread>
#include <vector>

std::atomic<int> counter{0};
std::atomic<bool> ready{false};

void bump(int times) {
    for (int i = 0; i < times; ++i) counter.fetch_add(1);
}

int main() {
    std::printf("atomic<int>  lock free: %s\n", counter.is_lock_free() ? "yes" : "no");
    std::printf("atomic<bool> lock free: %s\n", ready.is_lock_free() ? "yes" : "no");

    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) threads.emplace_back(bump, 50000);
    for (std::thread &t : threads) t.join();
    std::printf("counter = %d (4 threads x 50000)\n", counter.load());

    // exchange swaps and hands back the old value.
    std::printf("exchange(99) returned %d, now %d\n", counter.exchange(99), counter.load());

    // compare_exchange_weak is the primitive every lock-free structure is
    // built from: "if it is still `expected`, write `desired`; otherwise tell
    // me what it really is".
    int expected = 99;
    const bool won = counter.compare_exchange_weak(expected, 100);
    std::printf("cas(99 -> 100) = %s, value now %d\n", won ? "won" : "lost", counter.load());

    int stale = 0;
    const bool lost = counter.compare_exchange_weak(stale, 777);
    std::printf("cas(0 -> 777)  = %s, expected updated to %d\n", lost ? "won" : "lost", stale);
    std::printf("value unchanged: %d\n", counter.load());
    return 0;
}
```

```text
atomic<int>  lock free: yes
atomic<bool> lock free: yes
counter = 200000 (4 threads x 50000)
exchange(99) returned 200000, now 99
cas(99 -> 100) = won, value now 100
cas(0 -> 777)  = lost, expected updated to 100
value unchanged: 100
```

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

```cpp run
#include <cstdio>
#include <thread>
#include <vector>

// One object per thread, with static storage duration inside that thread.
// Not shared, so not racy -- which is the whole point.
thread_local int calls = 0;
thread_local int worker_id = -1;

int record_call() {
    ++calls;
    return calls;
}

void work(int id) {
    worker_id = id;
    for (int i = 0; i < 3; ++i) record_call();
}

int main() {
    std::vector<int> seen(3);
    std::vector<std::thread> threads;
    for (int id = 0; id < 3; ++id) {
        threads.emplace_back([id, &seen] {
            work(id);
            seen[static_cast<std::size_t>(id)] = calls;   // each thread's own
        });
    }
    for (std::thread &t : threads) t.join();

    // The main thread never called record_call, so its own counter is 0.
    std::printf("main thread calls   = %d\n", calls);
    for (std::size_t i = 0; i < seen.size(); ++i) {
        std::printf("worker %zu saw       = %d\n", i, seen[i]);
    }
    return 0;
}
```

```text
main thread calls   = 0
worker 0 saw       = 3
worker 1 saw       = 3
worker 2 saw       = 3
```

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

```cpp run
#include <chrono>
#include <cstdio>
#include <future>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

static int work(int n) {
    int total = 0;
    for (int i = 1; i <= n; ++i) total += i;
    return total;
}

int main() {
    // std::async hands back a future immediately; get() waits for the value.
    std::vector<std::future<int>> futures;
    for (int n : {10, 100, 1000}) {
        futures.push_back(std::async(std::launch::async, work, n));
    }
    for (std::size_t i = 0; i < futures.size(); ++i) {
        std::printf("result %zu = %d\n", i, futures[i].get());
    }

    // An exception thrown inside the task is stored in the future and rethrown
    // by get(). Without get(), it is swallowed silently.
    std::future<int> broken = std::async(std::launch::async, []() -> int {
        throw std::runtime_error("the worker could not reach the database");
    });
    try {
        broken.get();
    } catch (const std::runtime_error &error) {
        std::printf("caught from the future: %s\n", error.what());
    }

    // wait_for lets a caller give up instead of blocking forever.
    std::future<int> slow = std::async(std::launch::async, [] {
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
        return 1;
    });
    const auto state = slow.wait_for(std::chrono::milliseconds(10));
    std::printf("after 10ms the slow task is %s\n",
                state == std::future_status::ready      ? "ready"
                : state == std::future_status::timeout  ? "still running"
                                                        : "deferred");
    std::printf("eventually: %d\n", slow.get());
    return 0;
}
```

```text
result 0 = 55
result 1 = 5050
result 2 = 500500
caught from the future: the worker could not reach the database
after 10ms the slow task is still running
eventually: 1
```

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

```cpp make-files
/* ===== pool.h ===== */

#ifndef POOL_H
#define POOL_H

#include <condition_variable>
#include <cstddef>
#include <deque>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

// A fixed set of workers pulling from one queue. The point of the pool is not
// speed, it is a bound: a service that spawns a thread per request eventually
// runs out of memory, and long before that it runs out of scheduler.
class ThreadPool {
public:
    explicit ThreadPool(std::size_t threads);
    ~ThreadPool();

    ThreadPool(const ThreadPool &) = delete;
    ThreadPool &operator=(const ThreadPool &) = delete;

    // Returns a future, so the caller decides when to wait and what to do with
    // an exception -- see the futures section of this chapter.
    template <class F, class... Args>
    std::future<std::invoke_result_t<std::decay_t<F>, std::decay_t<Args>...>> submit(
        F &&work, Args &&...args) {
        using Result = std::invoke_result_t<std::decay_t<F>, std::decay_t<Args>...>;
        auto bound = std::bind(std::forward<F>(work), std::forward<Args>(args)...);
        auto task = std::make_shared<std::packaged_task<Result()>>(std::move(bound));
        std::future<Result> outcome = task->get_future();
        {
            std::lock_guard<std::mutex> guard(mutex_);
            if (stopping_) throw std::runtime_error("submit() on a pool that is shutting down");
            queue_.push_back([task] { (*task)(); });
            ++submitted_;
        }
        // notify_one, not notify_all: one job arrived, one worker should wake.
        ready_.notify_one();
        return outcome;
    }

    std::size_t size() const;
    std::size_t submitted() const;
    std::size_t completed() const;

private:
    void run();

    std::vector<std::thread> workers_;
    std::deque<std::function<void()>> queue_;
    mutable std::mutex mutex_;
    std::condition_variable ready_;
    bool stopping_ = false;
    std::size_t submitted_ = 0;
    std::size_t completed_ = 0;
};

#endif

/* ===== pool.cpp ===== */

#include "pool.h"

ThreadPool::ThreadPool(std::size_t threads) {
    for (std::size_t i = 0; i < threads; ++i) workers_.emplace_back(&ThreadPool::run, this);
}

ThreadPool::~ThreadPool() {
    {
        std::lock_guard<std::mutex> guard(mutex_);
        stopping_ = true;
    }
    // Every worker is blocked in wait(), so all of them have to be woken.
    ready_.notify_all();
    for (std::thread &worker : workers_) worker.join();
}

void ThreadPool::run() {
    for (;;) {
        std::function<void()> job;
        {
            std::unique_lock<std::mutex> guard(mutex_);
            // The predicate is not optional. wait() may wake spuriously, and
            // waking with an empty queue would pop from nothing.
            ready_.wait(guard, [this] { return stopping_ || !queue_.empty(); });
            if (queue_.empty()) return;  // stopping, and nothing left to do
            job = std::move(queue_.front());
            queue_.pop_front();
        }
        job();
        {
            std::lock_guard<std::mutex> guard(mutex_);
            ++completed_;
        }
    }
}

std::size_t ThreadPool::size() const { return workers_.size(); }

std::size_t ThreadPool::submitted() const {
    std::lock_guard<std::mutex> guard(mutex_);
    return submitted_;
}

std::size_t ThreadPool::completed() const {
    std::lock_guard<std::mutex> guard(mutex_);
    return completed_;
}

/* ===== main.cpp ===== */

#include "pool.h"

#include <cstdio>
#include <vector>

namespace {

bool is_prime(int n) {
    if (n < 2) return false;
    for (int d = 2; d * d <= n; ++d) {
        if (n % d == 0) return false;
    }
    return true;
}

int count_primes(int low, int high) {
    int found = 0;
    for (int n = low; n < high; ++n) {
        if (is_prime(n)) ++found;
    }
    return found;
}

}  // namespace

int main() {
    ThreadPool pool(4);
    std::printf("workers = %zu\n", pool.size());

    std::vector<std::future<int>> results;
    for (int slice = 0; slice < 8; ++slice) {
        const int low = slice * 50000 + 1;
        results.push_back(pool.submit(count_primes, low, low + 50000));
    }

    // The futures are collected in submission order even though the slices
    // finish in whatever order the workers get to them.
    int total = 0;
    for (std::size_t i = 0; i < results.size(); ++i) {
        const int found = results[i].get();
        total += found;
        std::printf("slice %zu: %d primes\n", i, found);
    }
    std::printf("total: %d primes below 400001\n", total);

    std::printf("submitted = %zu, completed = %zu\n", pool.submitted(), pool.completed());
    return 0;
}

/* ===== Makefile ===== */

CXXFLAGS = -std=c++17 -Wall -Wextra -Werror
LDLIBS   = -pthread

prog: main.cpp pool.cpp pool.h
	$(CXX) $(CXXFLAGS) -o prog main.cpp pool.cpp $(LDLIBS)

clean:
	rm -f prog
```

```text
workers = 4
slice 0: 5133 primes
slice 1: 4459 primes
slice 2: 4256 primes
slice 3: 4136 primes
slice 4: 4060 primes
slice 5: 3953 primes
slice 6: 3980 primes
slice 7: 3883 primes
total: 33860 primes below 400001
submitted = 8, completed = 8
```

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

```sh run
cat > counter.cpp <<'EOF'
#include <atomic>
#include <cstdio>
#include <thread>

int plain = 0;
std::atomic<int> guarded{0};

void bump_plain()   { for (int i = 0; i < 50000; ++i) plain++; }
void bump_guarded() { for (int i = 0; i < 50000; ++i) guarded.fetch_add(1); }

int main(int argc, char **) {
    if (argc > 1) {
        std::thread a(bump_guarded), b(bump_guarded);
        a.join(); b.join();
        std::printf("guarded = %d\n", guarded.load());
        return 0;
    }
    std::thread a(bump_plain), b(bump_plain);
    a.join(); b.join();
    std::printf("plain   = %d\n", plain);
    return 0;
}
EOF

clang++ -std=c++17 -fsanitize=thread -g -o counter_tsan counter.cpp

echo "--- plain int, built with -fsanitize=thread ---"
./counter_tsan > /dev/null 2> racy.txt
if grep -q "WARNING: ThreadSanitizer" racy.txt; then
  echo "ThreadSanitizer: data race reported"
else
  echo "ThreadSanitizer reported nothing"
fi

echo "--- std::atomic<int>, built with -fsanitize=thread ---"
./counter_tsan atomic 2> safe.txt
if grep -q "WARNING: ThreadSanitizer" safe.txt; then
  echo "ThreadSanitizer: data race reported"
else
  echo "ThreadSanitizer reported nothing"
fi
```

```text
--- plain int, built with -fsanitize=thread ---
ThreadSanitizer: data race reported
--- std::atomic<int>, built with -fsanitize=thread ---
guarded = 100000
ThreadSanitizer reported nothing
```

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

```cpp run
#include <atomic>
#include <cstddef>
#include <cstdio>
#include <mutex>
#include <thread>
#include <vector>

// Two pieces of state, two different tools. A single number is an atomic; a
// container is a structure, and a structure has an invariant that a single
// instruction cannot preserve.
class Stats {
public:
    void record(int ms) {
        ++requests_;
        std::lock_guard<std::mutex> guard(mutex_);
        latencies_.push_back(ms);
    }

    long requests() const { return requests_.load(); }

    long total_ms() const {
        std::lock_guard<std::mutex> guard(mutex_);
        long total = 0;
        for (int ms : latencies_) total += ms;
        return total;
    }

    std::size_t samples() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return latencies_.size();
    }

private:
    std::atomic<long> requests_{0};
    mutable std::mutex mutex_;
    std::vector<int> latencies_;
};

int main() {
    Stats stats;
    std::vector<std::thread> workers;

    for (int w = 0; w < 4; ++w) {
        workers.emplace_back([&stats, w] {
            for (int i = 0; i < 10000; ++i) stats.record(w + 1);
        });
    }
    for (std::thread &t : workers) t.join();

    std::printf("requests   = %ld (4 workers x 10000)\n", stats.requests());
    std::printf("samples    = %zu\n", stats.samples());
    std::printf("total ms   = %ld (1+2+3+4 per round x 10000)\n", stats.total_ms());
    std::printf("counts agree: %s\n",
                stats.requests() == static_cast<long>(stats.samples()) ? "yes" : "NO");
    return 0;
}
```

```text
requests   = 40000 (4 workers x 10000)
samples    = 40000
total ms   = 100000 (1+2+3+4 per round x 10000)
counts agree: yes
```

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

```cpp run
#include <chrono>
#include <cstdio>
#include <mutex>
#include <thread>
#include <vector>

// The mutex lives with the data it protects, and no code path outside this
// class can touch `value_` without going through it.
class Counter {
public:
    void add(int amount) {
        std::lock_guard<std::mutex> guard(mutex_);
        value_ += amount;
    }

    int value() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return value_;
    }

    // try_lock never blocks: it is the right primitive when "someone else is
    // using this" is an answer rather than a reason to wait.
    bool try_add(int amount) {
        std::unique_lock<std::mutex> guard(mutex_, std::try_to_lock);
        if (!guard.owns_lock()) return false;
        value_ += amount;
        return true;
    }

    void hold_for(std::chrono::milliseconds how_long) {
        std::lock_guard<std::mutex> guard(mutex_);
        std::this_thread::sleep_for(how_long);
    }

private:
    mutable std::mutex mutex_;
    int value_ = 0;
};

int main() {
    Counter counter;
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&counter] {
            for (int n = 0; n < 50000; ++n) counter.add(1);
        });
    }
    for (std::thread &t : threads) t.join();
    std::printf("counter = %d (4 threads x 50000)\n", counter.value());

    std::thread holder([&counter] { counter.hold_for(std::chrono::milliseconds(300)); });
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::printf("try_add while held: %s\n", counter.try_add(1) ? "got the lock" : "refused");
    holder.join();

    std::printf("try_add when free : %s\n", counter.try_add(1) ? "got the lock" : "refused");
    std::printf("counter = %d\n", counter.value());
    return 0;
}
```

```text
counter = 200000 (4 threads x 50000)
try_add while held: refused
try_add when free : got the lock
counter = 200001
```

`try_add while held: refused` is the measured proof that `std::try_to_lock` does not block.
`while free : got the lock` shows the same call succeeding a moment later, and the final counter is
200001 — the one successful `try_add` on top of the 200000 from the four threads.
:::

:::solution Exercise 3
`std::shared_mutex` plus `std::shared_lock` lets any number of readers in and keeps the writer out
until the last one leaves:

```cpp run
#include <atomic>
#include <chrono>
#include <cstdio>
#include <mutex>
#include <shared_mutex>
#include <thread>
#include <vector>

// One writer, many readers. A plain mutex would serialise the readers too,
// which is the entire thing shared_mutex buys.
std::shared_mutex mutex;
std::atomic<int> value{0};

std::atomic<int> holding{0};
std::atomic<int> recorded{0};
std::atomic<int> release{0};
std::vector<int> seen(3);

void reader(int id) {
    std::shared_lock<std::shared_mutex> lock(mutex);
    holding.fetch_add(1);
    // All three readers get in: shared locks do not exclude each other.
    while (holding.load() < 3) {
    }
    seen[static_cast<std::size_t>(id)] = holding.load();
    recorded.fetch_add(1);
    while (release.load() == 0) {
    }  // stay inside until main says go
}

void writer() {
    std::unique_lock<std::shared_mutex> lock(mutex);
    value.store(7);
}

int main() {
    std::vector<std::thread> readers;
    for (int i = 0; i < 3; ++i) readers.emplace_back(reader, i);

    while (holding.load() < 3) {
    }
    // Wait for the *writers* of `seen`, not merely for the count. Three threads
    // have incremented `holding` by the time the loop above ends, but printing
    // `seen` here would read a slot that no reader has stored into yet -- the
    // vector's initial value, which is exactly what "reader saw 0" means.
    while (recorded.load() < 3) {
    }
    for (int s : seen) std::printf("reader saw %d readers inside\n", s);

    // The writer starts while three shared locks are held, so it must wait.
    std::thread write(writer);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::printf("writer got in while they held it : %s\n", value.load() == 0 ? "no" : "yes");

    release.store(1);
    for (std::thread &r : readers) r.join();
    write.join();
    std::printf("value after the writer           : %d\n", value.load());
    return 0;
}
```

```text
reader saw 3 readers inside
reader saw 3 readers inside
reader saw 3 readers inside
writer got in while they held it : no
value after the writer           : 7
```

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

```cpp run
#include <cstdio>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>

struct Account {
    int balance = 0;
    std::mutex mutex;
};

// Impose one global order on the two locks, using the only ordering every
// thread can agree on: the addresses. If every thread locks low-then-high,
// no thread can hold high and wait for low, so no cycle can form.
void transfer(Account &from, Account &to, int amount) {
    Account *low = &from;
    Account *high = &to;
    if (low > high) std::swap(low, high);

    std::unique_lock<std::mutex> first(low->mutex);
    std::unique_lock<std::mutex> second(high->mutex);
    from.balance -= amount;
    to.balance += amount;
}

int main() {
    std::vector<Account> accounts(4);
    for (Account &a : accounts) a.balance = 1000;

    std::vector<std::thread> threads;
    for (int i = 0; i < 8; ++i) {
        threads.emplace_back([&accounts, i] {
            for (int n = 0; n < 500; ++n) {
                const std::size_t a = static_cast<std::size_t>(i) % accounts.size();
                const std::size_t b = (static_cast<std::size_t>(i) + 1) % accounts.size();
                transfer(accounts[a], accounts[b], 1);
            }
        });
    }
    for (std::thread &t : threads) t.join();

    int total = 0;
    for (std::size_t i = 0; i < accounts.size(); ++i) {
        std::printf("account %zu = %d\n", i, accounts[i].balance);
        total += accounts[i].balance;
    }
    std::printf("total = %d (started at 4000)\n", total);
    std::printf("no thread deadlocked, money is %s\n", total == 4000 ? "conserved" : "MISSING");
    return 0;
}
```

```text
account 0 = 1000
account 1 = 1000
account 2 = 1000
account 3 = 1000
total = 4000 (started at 4000)
no thread deadlocked, money is conserved
```

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

```cpp run
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <memory>
#include <deque>
#include <functional>
#include <future>
#include <mutex>
#include <thread>
#include <type_traits>
#include <utility>
#include <vector>

// `wait()` blocks until every submitted job has finished, so a caller can hand
// over a batch and then collect it without sleeping and hoping.
class Pool {
public:
    explicit Pool(std::size_t workers) {
        for (std::size_t i = 0; i < workers; ++i) threads_.emplace_back(&Pool::run, this);
    }

    ~Pool() {
        {
            std::lock_guard<std::mutex> guard(mutex_);
            stopping_ = true;
        }
        work_.notify_all();
        for (std::thread &t : threads_) t.join();
    }

    template <class F>
    std::future<std::invoke_result_t<std::decay_t<F>>> submit(F &&job) {
        using Result = std::invoke_result_t<std::decay_t<F>>;
        auto task = std::make_shared<std::packaged_task<Result()>>(std::forward<F>(job));
        std::future<Result> outcome = task->get_future();
        {
            std::lock_guard<std::mutex> guard(mutex_);
            queue_.push_back([task] { (*task)(); });
            ++submitted_;
        }
        work_.notify_one();
        return outcome;
    }

    void wait() {
        std::unique_lock<std::mutex> guard(mutex_);
        // The predicate must cover *in flight* as well as queued: an empty
        // queue with four workers still running is not idle.
        idle_.wait(guard, [this] { return queue_.empty() && busy_ == 0; });
    }

    std::size_t submitted() const { return submitted_.load(); }
    std::size_t completed() const { return completed_.load(); }

private:
    void run() {
        for (;;) {
            std::function<void()> job;
            {
                std::unique_lock<std::mutex> guard(mutex_);
                work_.wait(guard, [this] { return stopping_ || !queue_.empty(); });
                if (queue_.empty()) return;
                job = std::move(queue_.front());
                queue_.pop_front();
                ++busy_;
            }
            job();
            {
                std::lock_guard<std::mutex> guard(mutex_);
                --busy_;
                ++completed_;
            }
            idle_.notify_all();
        }
    }

    std::vector<std::thread> threads_;
    std::deque<std::function<void()>> queue_;
    std::mutex mutex_;
    std::condition_variable work_;
    std::condition_variable idle_;
    bool stopping_ = false;
    std::size_t busy_ = 0;
    std::atomic<std::size_t> submitted_{0};
    std::atomic<std::size_t> completed_{0};
};

int main() {
    Pool pool(4);
    std::vector<std::future<int>> results;
    for (int i = 0; i < 20; ++i) {
        results.push_back(pool.submit([i] {
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
            return i * i;
        }));
    }

    pool.wait();  // every job has finished, but the workers stay alive
    std::printf("after wait(): submitted = %zu, completed = %zu\n", pool.submitted(),
                pool.completed());

    int total = 0;
    for (std::future<int> &f : results) total += f.get();
    std::printf("sum of squares 0..19 = %d\n", total);
    std::printf("batch is %s\n", pool.completed() == 20 ? "complete" : "INCOMPLETE");
    return 0;
}
```

```text
after wait(): submitted = 20, completed = 20
sum of squares 0..19 = 2470
batch is complete
```

`after wait(): submitted = 20, completed = 20` is the proof it waited correctly, and the workers
are still alive to prove that `wait()` is not `stop()`. Without the `busy_ == 0` half, a worker
that had already popped the last job but not finished it would let `wait()` return early — the
queue is empty, the work is not done, and the caller collects a future that is not ready.
:::

:::solution Exercise 6
`std::promise` is the writing end of a future you create yourself, which is how a worker reports one
result or one failure to whoever is waiting:

```cpp run
#include <chrono>
#include <cstdio>
#include <exception>
#include <future>
#include <stdexcept>
#include <thread>

int main() {
    // A promise is the writing end of a future you create yourself. It is how
    // a worker reports one result -- or one failure -- to whoever is waiting.
    std::promise<int> done;
    std::future<int> answer = done.get_future();

    std::thread worker([&done] {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        done.set_value(42);  // move-only: a promise can be fulfilled once
    });

    std::printf("waiting...\n");
    std::printf("worker answered: %d\n", answer.get());
    worker.join();

    // The failure path matters more. Without set_exception, an exception that
    // escapes a thread function calls std::terminate and the process dies.
    std::promise<int> failing;
    std::future<int> outcome = failing.get_future();
    std::thread risky([&failing] {
        try {
            throw std::runtime_error("connection reset by peer");
        } catch (...) {
            failing.set_exception(std::current_exception());
        }
    });
    try {
        outcome.get();
    } catch (const std::runtime_error &error) {
        std::printf("delivered through the future: %s\n", error.what());
    }
    risky.join();

    // A promise that is destroyed unfulfilled breaks its future with
    // std::future_error, which is the third case a caller has to handle.
    std::future<int> orphan;
    {
        std::promise<int> abandoned;
        orphan = abandoned.get_future();
    }
    try {
        orphan.get();
    } catch (const std::future_error &error) {
        std::printf("broken promise: %s\n", error.what());
    }
    return 0;
}
```

```text
waiting...
worker answered: 42
delivered through the future: connection reset by peer
broken promise: The associated promise has been destructed prior to the associated state becoming ready.
```

Three cases, one API: `worker answered: 42` is the ordinary path;
`delivered through the future: connection reset by peer` is an exception moved across the thread
boundary with `set_exception` and `std::current_exception`; and
`broken promise: The associated promise has been destructed prior to the associated state becoming
ready.` is the third — a promise destroyed without being fulfilled, which breaks its future with
`std::future_error`. That message text is libc++'s wording; the standard only fixes that the
exception is a `std::future_error` with `broken_promise` as its code.
:::
