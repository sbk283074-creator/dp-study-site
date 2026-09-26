#!/usr/bin/env python3
"""Generate chapters/31-threads-locks-and-the-java-memory-model.md.

    python3 tools/gen/31/gen.py

Chapter 30 was about *how many* things run at once. This one is about what happens
when those things touch the same memory: lost updates, visibility, `volatile`,
`synchronized`, atomics, and the deadlock that needs a cycle to form. Every race
below is forced with a `CyclicBarrier` so that the interleaving -- and therefore
the transcript -- is reproducible rather than merely observed once.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "31-threads-locks-and-the-java-memory-model.md")

BLOCKS = {
    "core": gen.run_files(["JmmDemo.java", "Counter.java", "Nap.java"]),
    "cas": gen.sh("cas.sh", "run-project"),
    "volatile": gen.sh("volatile.sh", "run-project"),
    "deadlock": gen.sh("deadlock.sh", "run-project"),
    "reentrant": gen.sh("reentrant.sh", "run-project"),
    "bad": gen.bad("BadCapture.java", "effectively final"),
    "warn": gen.warn("BoxedLock.java", "value-based class"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 31
part: 4
title: Threads, Locks and the Java Memory Model
summary: What actually goes wrong when two threads touch the same field. A lost update forced with a barrier so it is reproducible, what synchronized and the atomics each guarantee, volatile as a visibility promise rather than a magic word, a deadlock that forms on purpose, and the cache that built the same report eight times.
minutes: 80
tags: [concurrency, memory-model, volatile, synchronized, atomics, deadlock]
---

Chapter 30 decided *how many* things run at once. This chapter is about what happens when those things
look at the same memory, which is where concurrency stops being a performance topic and becomes a
correctness one. The Java Memory Model is the set of rules that says when a write by one thread is
guaranteed to be visible to another, and the uncomfortable part of it is how little it promises: unless
you establish a happens-before relationship, the JVM is allowed to let a thread read a value that was
written years ago in wall-clock terms.

The claim that organises everything below is this: **concurrency bugs are not rare interleavings, they
are missing guarantees.** You do not debug them by reproducing the timing — you fix them by adding the
guarantee that makes the timing irrelevant.

## `count++` is three operations

@@core@@

Read the first line of that transcript again: two threads, one increment each, starting from 5 — and
the answer is 6. One increment vanished. Nothing threw, nothing logged, and the program exited
successfully.

The reason is that `plain = plain + 1` is not one operation. It is a **read**, an **add**, and a
**write**, and the Java Memory Model promises nothing about other threads' timing between them. Both
threads read 5, both compute 6, both write 6, and one increment is gone. The `CyclicBarrier` in that
program is not what causes the bug — it is what makes a timing that a real service hits once a week
happen every single run, so that it can be talked about instead of guessed at.

The other two lines are the two families of fix, and they differ in what they cost:

- **`synchronized`** makes the read-add-write *mutually exclusive*. Only one thread is inside
  `bumpLocked()` at a time, so the three steps cannot interleave. It is a lock: a thread that cannot
  get in waits, blocked, until the holder leaves.
- **`AtomicInteger`** makes the read-add-write a *single atomic operation*, with no lock and no
  waiting. It is built on a compare-and-set instruction, described below.

Both give 7 here. They are not interchangeable: `synchronized` can protect an invariant that spans
several fields and several statements, which an atomic variable cannot; an atomic variable does not
block, so it cannot deadlock, and it is dramatically cheaper under contention.

## What `synchronized` actually buys

Three things, and all three are worth naming separately because most explanations give only the first:

1. **Mutual exclusion.** Only one thread at a time holds the monitor.
2. **Visibility.** Everything a thread did before releasing a monitor is visible to every thread that
   subsequently acquires the *same* monitor. This is the part people forget, and it is the part that
   makes `synchronized` a memory-model construct rather than merely a lock.
3. **Atomicity of the protected region.** The whole block is one unit as far as other threads
   synchronizing on the same monitor are concerned.

The second point has a consequence that catches people: **locking on the wrong object gives you mutual
exclusion and none of the visibility.** Two threads that synchronize on two different objects are not
ordered with respect to each other at all.

:::danger Never lock on a value-based object
The lock object has to be *the same object* for every thread, forever, and that rules out the two
things people reach for. javac catches one of them:

@@warn@@

`Integer` is a value-based class, and small values are cached and shared: `Integer.valueOf(1)` may
return the same instance to two completely unrelated parts of the program. Synchronizing on it means
your lock is held by code you have never read. The second trap is the non-final field —
`private Object lock = new Object()` — because assigning a new lock object while another thread holds
the old one silently splits your critical section in two. The rule is `private final Object lock =
new Object()`, and nothing else.
:::

### The value a thread captures must not change

There is one more rule that bites constantly once you start submitting tasks in a loop, and it is a
compile error rather than a race — which is the good kind of failure:

@@bad@@

A lambda may only capture a local that is *final or effectively final*. `seen++` makes it neither, so
javac refuses. This is not pedantry: the lambda may run on another thread, minutes later, and a local
that the enclosing method is still mutating would have no defined value. If you need a per-task value,
copy it into a fresh final variable inside the loop body — `final int n = i;` — which is what every
later program in this book does.

## Atomics and the compare-and-set they are built on

@@cas@@

The two `compareAndSet` calls are the whole idea. The first succeeds because the value still *is* what
the caller believed it was; the second fails because it is not, and — this is the part that matters —
**the failure tells you the value changed, so you can retry.** That is what `incrementAndGet` does
internally, in the loop shown at the bottom of the transcript: read, compute, attempt, and if the
attempt failed, read again.

Compare-and-set is the reason atomics do not block. A thread that loses the race is not suspended; it
finds out and tries again. Under heavy contention that means burning CPU on retries, which is why
`LongAdder` exists: it spreads the counter across several cells so that different threads mostly
contend with different ones, and sums them only when you ask. `LongAdder` is the right choice for a
counter that is written constantly and read rarely — request counts, bytes sent, cache misses — and
`AtomicInteger` is the right choice when you need a single value you can read exactly at any moment.

Atomics give you atomicity and visibility for **one variable**. They do not give you a transaction
across two. If two fields must change together — a balance and an audit entry, a head and a tail — you
need a lock, or you need to put both values in one immutable object and replace it atomically with
`AtomicReference`.

## Visibility, and what `volatile` is for

@@volatile@@

That program stops. The interesting thing is not that it stopped, it is *why it is allowed to stop*:
`volatile` establishes that the write `stop = true` happens-before any subsequent read of `stop`, so
the reader is guaranteed to see it.

Without `volatile` the program is not guaranteed to stop at all. Nothing in the JMM requires the
reader to ever observe the write, and in practice a JIT that hoists the read out of the loop produces
exactly that: a thread that spins forever on a flag that has been true for an hour. That is a real
failure mode, it is invisible in testing, and it is one keyword away from being impossible.

What `volatile` does **not** give you is atomicity. A `volatile int` that two threads increment is
still a lost update, because the read-add-write is still three operations. `volatile` is for a value
that one thread writes and others read — a shutdown flag, a configuration switch, a published
reference — not for a value that many threads update.

## Deadlock

@@deadlock@@

Two threads, two locks, taken in opposite orders, and neither can ever proceed. This is the one
concurrency failure that is genuinely deterministic — given the right interleaving — and it is the one
that takes a service down rather than corrupting a number, because the threads are *stuck*, not wrong.

The deadlock needs four conditions at once, and all of them are usually described in operating-system
courses as the Coffman conditions:

1. **Mutual exclusion** — a lock is held by one thread at a time.
2. **Hold and wait** — a thread holds one lock while waiting for another.
3. **No preemption** — a lock cannot be taken away from its holder.
4. **Circular wait** — thread A waits for B, B waits for A.

You cannot remove the first three; they are what a lock is. So every real fix attacks the fourth, and
there are exactly two ways to do it:

- **Order the locks.** If every thread acquires locks in the same global order, a cycle cannot form.
  This is the real fix, it costs nothing at runtime, and it scales to any number of locks.
- **Bound the wait.** `tryLock(timeout)` gives up instead of waiting forever, which breaks the cycle
  by removing one edge from it. It is a safety net, not a design: a `tryLock` that fails needs a
  `finally` to release what it already holds, and a decision about what to do with a request it could
  not complete.

`jstack` prints the cycle for you — "Found one Java-level deadlock" followed by both threads and the
lock each is waiting for — so a hung service is diagnosable after the fact. That is worth knowing, and
it is not a substitute for ordering your locks.

## Reentrancy

@@reentrant@@

A lock that a thread already holds is a lock that thread may take again, and the counter is how the
JVM knows when to actually release it. This is not a convenience — it is why one `synchronized` method
can call another `synchronized` method on the same object without the thread deadlocking against
itself, which happens in real code constantly because subclass methods call superclass methods.

The rule that follows is mechanical: **every `lock()` goes in a `try` with `unlock()` in the
`finally`.** An exception between the two leaves the lock held forever, and every other thread then
waits for a thread that is already gone.

:::pitfall "I made the field volatile, so it is thread-safe"
`volatile` fixes visibility, not atomicity, and the sentence above is the most common way a
concurrency bug survives a code review. `volatile` is correct when *one* thread writes and others
read. For anything where several threads update the same value — a counter, a sum, a "last seen"
timestamp that more than one thread sets — you want an atomic variable, or a lock. A rule of thumb
that holds up: if the new value depends on the old value, `volatile` is not enough.
:::

:::scenario The cache that built the same report eight times
A service caches an expensive report behind a `HashMap`. The code reads: look the key up, and if it is
absent, build it and put it in. Eight requests arrive at once for a key that is not cached yet. The
report takes four seconds to build and costs a database query each time.

@@scenario@@

Two threads, two builds, one entry — the second write overwrote the first, and the work was done
twice. With eight threads it is eight builds: eight database queries, thirty-two seconds of CPU, and
eight objects that were thrown away. Nobody notices, because the answers are correct. What is noticed,
weeks later, is that the database is doing eight times the queries it should during every cold start
and every cache expiry.

:::solution
The bug is that *check* and *act* are two steps, and nothing makes them atomic. `ConcurrentHashMap`
has a method whose whole purpose is to make them one:

```java
report = cache.computeIfAbsent(key, Report::build);
```

`computeIfAbsent` applies the mapping function at most once per key, even under contention, which is
exactly the guarantee the get-then-put version lacked — eight threads, one build, as the transcript
shows. Two things to know about it:

- The mapping function must not modify the map it is being computed into. That is documented, and
  violating it can deadlock or throw.
- The function runs while the bin is locked, so it must be short. If building the report takes four
  seconds, wrap the work in a `CompletableFuture` and put *that* in the map, so the lock is held for
  microseconds and the eight callers all await the same future.

If you cannot use `ConcurrentHashMap` — the cache is a `Map` field inside an object you do not control
— the same guarantee comes from a `synchronized` block around the whole check-then-act, at the cost of
serialising every cache miss.
:::

## Key takeaways

- `plain = plain + 1` is a read, an add and a write; two threads doing it can lose one increment and nothing will complain.
- A race is a missing guarantee, not an unlucky timing: fix it by adding the guarantee, not by reproducing the timing.
- `synchronized` gives mutual exclusion, visibility for everything done under the same monitor, and atomicity of the block.
- Locking on the wrong object gives you exclusion with none of the visibility; `private final Object lock` is the only safe form.
- Atomics make one variable's read-modify-write a single operation via compare-and-set, and they never block.
- `LongAdder` beats `AtomicInteger` for a counter written constantly and read rarely, because it spreads the contention.
- `volatile` gives visibility and ordering for one variable, and gives no atomicity at all: if the new value depends on the old, it is not enough.
- A deadlock needs a cycle; ordering your locks removes the cycle and costs nothing at runtime.
- Every `lock()` belongs in a `try` with `unlock()` in the `finally`, or one exception holds the lock forever.
- Get-then-put is two steps; `ConcurrentHashMap.computeIfAbsent` is one, and applies the function at most once per key.

## Practice

- [ ] Count 80,000 increments across four threads with `AtomicInteger.incrementAndGet()` and confirm the total is exact.
- [ ] Write the compare-and-set retry loop by hand to add 25 to an `AtomicInteger`, and print what it read and what it wrote.
- [ ] Make two threads take two locks in the same order and show that both finish, where the opposite order deadlocked.
- [ ] Show that `ReentrantLock.tryLock` succeeds for a thread that already holds the lock, using the hold count.

## Solutions

:::solution Exercise 1
@@sol1@@

`incrementAndGet()` is implemented as a compare-and-set loop, so every increment lands. A plain `int`
in the same loop would lose an unpredictable number of them — which is precisely why "we tested it and
it looked right" is not evidence about concurrent code.

:::

:::solution Exercise 2
@@sol2@@

The loop reads the current value, computes the next one, and attempts the swap; if the value moved in
between, the attempt fails and it reads again. This is what `incrementAndGet`, `accumulateAndGet` and
`updateAndGet` all do internally, and it is worth writing once so the method stops being magic.

:::

:::solution Exercise 3
@@sol3@@

Both threads take `alpha` before `beta`, so whichever gets there first simply makes the other wait —
and a wait is not a cycle. The program finishes. The opposite order produced two threads that were
still alive at the end of the chapter's deadlock program, and would still be alive now.

:::

:::solution Exercise 4
@@sol4@@

`tryLock` is reentrant, exactly like `lock`: a thread may take a lock it already holds, and the hold
count goes to two. The timeout matters for the *other* thread's lock, where failing fast is what stops
one bad ordering from hanging a service.

:::
"""

gen.write(TEMPLATE, BLOCKS)
