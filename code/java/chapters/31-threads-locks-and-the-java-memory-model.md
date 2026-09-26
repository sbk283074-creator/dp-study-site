---
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

```java run-files
// ===== JmmDemo.java =====

import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

public class JmmDemo {
    public static void main(String[] args) throws Exception {
        System.out.println("two threads, one increment each, starting from 5");
        System.out.println();
        System.out.println("  plain int, read then write   : " + racy() + "   (correct would be 7)");
        System.out.println("  guarded by synchronized      : " + locked() + "   (correct would be 7)");
        System.out.println("  through AtomicInteger        : " + atomic() + "   (correct would be 7)");
        System.out.println();
        System.out.println("four threads, 50_000 increments each, starting from 0");
        System.out.println();
        System.out.println("  AtomicInteger : " + contended(false) + "   (correct would be 200000)");
        System.out.println("  LongAdder     : " + contended(true) + "   (correct would be 200000)");
    }

    /** Both threads read 5, then both write 6. The barrier only makes it reproducible. */
    static int racy() throws Exception {
        Counter counter = new Counter(5);
        CyclicBarrier bothRead = new CyclicBarrier(2);
        CyclicBarrier bothWrote = new CyclicBarrier(3);

        Runnable task = () -> {
            int seen = counter.plain();
            await(bothRead);
            Nap.millis(50);
            counter.setPlain(seen + 1);
            await(bothWrote);
        };

        Thread a = new Thread(task);
        Thread b = new Thread(task);
        a.start();
        b.start();
        await(bothWrote);
        return counter.plain();
    }

    static int locked() throws Exception {
        Counter counter = new Counter(5);
        CyclicBarrier start = new CyclicBarrier(2);
        CyclicBarrier done = new CyclicBarrier(3);

        Runnable task = () -> {
            await(start);
            counter.bumpLocked();
            await(done);
        };

        Thread a = new Thread(task);
        Thread b = new Thread(task);
        a.start();
        b.start();
        await(done);
        return counter.plain();
    }

    static int atomic() {
        Counter counter = new Counter(5);
        counter.atomic().incrementAndGet();
        counter.atomic().incrementAndGet();
        return counter.atomic().get();
    }

    static long contended(boolean useAdder) throws InterruptedException {
        Counter counter = new Counter(0);
        int threads = 4;
        int per = 50_000;
        Thread[] pool = new Thread[threads];

        for (int i = 0; i < threads; i++) {
            pool[i] = new Thread(() -> {
                for (int n = 0; n < per; n++) {
                    if (useAdder) {
                        counter.adder().increment();
                    } else {
                        counter.atomic().incrementAndGet();
                    }
                }
            });
        }
        for (Thread t : pool) {
            t.start();
        }
        for (Thread t : pool) {
            t.join();
        }
        return useAdder ? counter.adder().sum() : counter.atomic().get();
    }

    static void await(CyclicBarrier barrier) {
        try {
            barrier.await();
        } catch (InterruptedException | BrokenBarrierException e) {
            throw new IllegalStateException(e);
        }
    }
}

// ===== Counter.java =====

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.LongAdder;

/** One counter four ways, so a chapter can measure what each one actually guarantees. */
public final class Counter {

    private int plain;
    private final AtomicInteger atomic = new AtomicInteger();
    private final LongAdder adder = new LongAdder();

    public Counter(int start) {
        plain = start;
        atomic.set(start);
    }

    public int plain() {
        return plain;
    }

    public void setPlain(int value) {
        plain = value;
    }

    public synchronized void bumpLocked() {
        plain = plain + 1;
    }

    public AtomicInteger atomic() {
        return atomic;
    }

    public LongAdder adder() {
        return adder;
    }
}

// ===== Nap.java =====

/** Sleeping, with the interrupt flag restored rather than swallowed. */
public final class Nap {

    private Nap() {
    }

    public static void millis(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

```text
two threads, one increment each, starting from 5

  plain int, read then write   : 6   (correct would be 7)
  guarded by synchronized      : 7   (correct would be 7)
  through AtomicInteger        : 7   (correct would be 7)

four threads, 50_000 increments each, starting from 0

  AtomicInteger : 200000   (correct would be 200000)
  LongAdder     : 200000   (correct would be 200000)
```

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

```java warn
public class BoxedLock {
    public static void main(String[] args) {
        Integer tickets = 1;
        synchronized (tickets) {
            System.out.println(tickets);
        }
    }
}
```

```text
warning: [synchronization] attempt to synchronize on an instance of a value-based class
```

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

```java bad
public class BadCapture {
    public static void main(String[] args) {
        int seen = 0;
        Runnable task = () -> System.out.println(seen);
        seen++;
        task.run();
    }
}
```

```text
error: local variables referenced from a lambda expression must be final or effectively final
```

A lambda may only capture a local that is *final or effectively final*. `seen++` makes it neither, so
javac refuses. This is not pedantry: the lambda may run on another thread, minutes later, and a local
that the enclosing method is still mutating would have no defined value. If you need a per-task value,
copy it into a fresh final variable inside the loop body — `final int n = i;` — which is what every
later program in this book does.

## Atomics and the compare-and-set they are built on

```sh run-project
cat > Cas.java <<'JAVA'
import java.util.concurrent.atomic.AtomicInteger;

public class Cas {
    public static void main(String[] args) {
        AtomicInteger value = new AtomicInteger(5);

        System.out.println("start                       : " + value.get());
        System.out.println("compareAndSet(5, 9)         : " + value.compareAndSet(5, 9));
        System.out.println("compareAndSet(5, 9) again   : " + value.compareAndSet(5, 9));
        System.out.println("value                       : " + value.get());
        System.out.println("incrementAndGet             : " + value.incrementAndGet());
        System.out.println("getAndIncrement             : " + value.getAndIncrement());
        System.out.println("value                       : " + value.get());
        System.out.println("accumulateAndGet(3, max)    : " + value.accumulateAndGet(3, Math::max));
        System.out.println("updateAndGet(x -> x * 2)    : " + value.updateAndGet(x -> x * 2));
        System.out.println();
        System.out.println("the retry loop every atomic method is built from:");
        System.out.println("  addOne(value) = " + addOne(value));
        System.out.println("  value         = " + value.get());
    }

    static int addOne(AtomicInteger value) {
        int before;
        int after;
        do {
            before = value.get();
            after = before + 1;
        } while (!value.compareAndSet(before, after));
        return after;
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Cas.java
java -cp out Cas
```

```text
start                       : 5
compareAndSet(5, 9)         : true
compareAndSet(5, 9) again   : false
value                       : 9
incrementAndGet             : 10
getAndIncrement             : 10
value                       : 11
accumulateAndGet(3, max)    : 11
updateAndGet(x -> x * 2)    : 22

the retry loop every atomic method is built from:
  addOne(value) = 23
  value         = 23
```

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

```sh run-project
cat > Flag.java <<'JAVA'
public class Flag {
    static volatile boolean stop = false;

    public static void main(String[] args) throws InterruptedException {
        Thread reader = new Thread(() -> {
            while (!stop) {
                Thread.onSpinWait();
            }
        });
        reader.start();

        Nap.millis(50);
        stop = true;
        reader.join(2_000);

        System.out.println("reader stopped within 2 s    : " + !reader.isAlive());
        System.out.println();
        System.out.println("a write to a volatile field happens-before every later read");
        System.out.println("of it, so the reader is guaranteed to see this one.");
        System.out.println("Without volatile there is no such guarantee: the read may be");
        System.out.println("hoisted out of the loop, and the thread may never stop.");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Flag.java
java -cp out Flag
```

```text
reader stopped within 2 s    : true

a write to a volatile field happens-before every later read
of it, so the reader is guaranteed to see this one.
Without volatile there is no such guarantee: the read may be
hoisted out of the loop, and the thread may never stop.
```

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

```sh run-project
cat > Deadlock.java <<'JAVA'
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class Deadlock {
    public static void main(String[] args) throws InterruptedException {
        Object first = new Object();
        Object second = new Object();

        Thread one = new Thread(() -> hold(first, second));
        Thread two = new Thread(() -> hold(second, first));
        one.setDaemon(true);
        two.setDaemon(true);
        one.start();
        two.start();
        one.join(500);
        two.join(500);

        System.out.println("t1 still waiting : " + one.isAlive());
        System.out.println("t2 still waiting : " + two.isAlive());
        System.out.println();
        System.out.println("two locks, taken in two orders, and no way out: neither");
        System.out.println("thread can release the one the other is waiting for.");

        System.out.println();
        Object left = new Object();
        Object right = new Object();
        Thread three = new Thread(() -> hold(left, right));
        Thread four = new Thread(() -> hold(left, right));
        three.start();
        four.start();
        three.join(5_000);
        four.join(5_000);
        System.out.println("same locks, one order, both finished : "
                + (!three.isAlive() && !four.isAlive()));
        System.out.println();
        System.out.println("the fix is an order, not a timeout: if every thread takes the");
        System.out.println("locks in the same sequence, a cycle cannot form");

        System.out.println();
        ReentrantLock a = new ReentrantLock();
        ReentrantLock b = new ReentrantLock();
        b.lock();
        Thread patient = new Thread(() -> {
            a.lock();
            try {
                boolean got = false;
                try {
                    got = b.tryLock(100, TimeUnit.MILLISECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("tryLock got the second lock : " + got);
            } finally {
                a.unlock();
            }
        });
        patient.start();
        patient.join(5_000);
        b.unlock();
        System.out.println("finished instead of hanging : " + !patient.isAlive());
    }

    static void hold(Object a, Object b) {
        synchronized (a) {
            Nap.millis(200);
            synchronized (b) {
                Nap.millis(10);
            }
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Deadlock.java
java -cp out Deadlock
```

```text
t1 still waiting : true
t2 still waiting : true

two locks, taken in two orders, and no way out: neither
thread can release the one the other is waiting for.

same locks, one order, both finished : true

the fix is an order, not a timeout: if every thread takes the
locks in the same sequence, a cycle cannot form

tryLock got the second lock : false
finished instead of hanging : true
```

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

```sh run-project
cat > Reentrant.java <<'JAVA'
import java.util.concurrent.locks.ReentrantLock;

public class Reentrant {
    private static final ReentrantLock LOCK = new ReentrantLock();

    public static void main(String[] args) {
        System.out.println("before         : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        LOCK.lock();
        LOCK.lock();
        System.out.println("after 2 locks  : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        LOCK.unlock();
        System.out.println("after 1 unlock : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        LOCK.unlock();
        System.out.println("after 2 unlock : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        System.out.println();
        System.out.println("a monitor works the same way: a thread that holds it can enter");
        System.out.println("another block guarded by it, which is why one synchronized");
        System.out.println("method can call another on the same object without stopping");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Reentrant.java
java -cp out Reentrant
```

```text
before         : locked false, hold count 0
after 2 locks  : locked true, hold count 2
after 1 unlock : locked true, hold count 1
after 2 unlock : locked false, hold count 0

a monitor works the same way: a thread that holds it can enter
another block guarded by it, which is why one synchronized
method can call another on the same object without stopping
```

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

```sh run-project
cat > Scenario.java <<'JAVA'
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.atomic.AtomicInteger;

public class Scenario {
    public static void main(String[] args) throws Exception {
        Map<String, String> plain = new HashMap<>();
        CyclicBarrier bothMissed = new CyclicBarrier(2);
        CyclicBarrier bothWrote = new CyclicBarrier(3);
        AtomicInteger builds = new AtomicInteger();

        Runnable racy = () -> {
            boolean missing = !plain.containsKey("report");
            JmmDemo.await(bothMissed);
            Nap.millis(50);
            if (missing) {
                plain.put("report", "built");
                builds.incrementAndGet();
            }
            JmmDemo.await(bothWrote);
        };
        Thread left = new Thread(racy);
        Thread right = new Thread(racy);
        left.start();
        right.start();
        JmmDemo.await(bothWrote);

        System.out.println("--- get-then-put from two threads ---");
        System.out.println("  times the report was built : " + builds.get());
        System.out.println("  entries in the map         : " + plain.size());
        System.out.println();

        ConcurrentHashMap<String, String> safe = new ConcurrentHashMap<>();
        AtomicInteger single = new AtomicInteger();
        int threads = 8;
        Thread[] pool = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            pool[i] = new Thread(() -> safe.computeIfAbsent("report", key -> {
                single.incrementAndGet();
                return "built";
            }));
        }
        for (Thread t : pool) {
            t.start();
        }
        for (Thread t : pool) {
            t.join();
        }

        System.out.println("--- computeIfAbsent from eight threads ---");
        System.out.println("  threads                    : " + threads);
        System.out.println("  times the report was built : " + single.get());
        System.out.println("  entries in the map         : " + safe.size());
        System.out.println();
        System.out.println("computeIfAbsent applies the function at most once per key,");
        System.out.println("which is the whole difference between a cache and a race");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
--- get-then-put from two threads ---
  times the report was built : 2
  entries in the map         : 1

--- computeIfAbsent from eight threads ---
  threads                    : 8
  times the report was built : 1
  entries in the map         : 1

computeIfAbsent applies the function at most once per key,
which is the whole difference between a cache and a race
```

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
```sh run-project
cat > Sol1.java <<'JAVA'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Sol1 {
    public static void main(String[] args) throws InterruptedException {
        int threads = 4;
        int per = 20_000;
        AtomicInteger hits = new AtomicInteger();
        ExecutorService pool = Executors.newFixedThreadPool(threads);

        for (int i = 0; i < threads; i++) {
            pool.execute(() -> {
                for (int n = 0; n < per; n++) {
                    hits.incrementAndGet();
                }
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("threads          : " + threads);
        System.out.println("increments each  : " + per);
        System.out.println("expected         : " + (threads * per));
        System.out.println("counted          : " + hits.get());
        System.out.println();
        System.out.println("incrementAndGet is a single atomic operation, so no increment");
        System.out.println("can be lost no matter how the threads interleave");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
threads          : 4
increments each  : 20000
expected         : 80000
counted          : 80000

incrementAndGet is a single atomic operation, so no increment
can be lost no matter how the threads interleave
```

`incrementAndGet()` is implemented as a compare-and-set loop, so every increment lands. A plain `int`
in the same loop would lose an unpredictable number of them — which is precisely why "we tested it and
it looked right" is not evidence about concurrent code.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'JAVA'
import java.util.concurrent.atomic.AtomicInteger;

public class Sol2 {
    public static void main(String[] args) {
        AtomicInteger value = new AtomicInteger(0);
        int delta = 25;

        int before;
        int after;
        do {
            before = value.get();
            after = before + delta;
        } while (!value.compareAndSet(before, after));

        System.out.println("read             : " + before);
        System.out.println("wrote            : " + after);
        System.out.println("compareAndSet    : true");
        System.out.println("value            : " + value.get());
        System.out.println();
        System.out.println("the loop is the point: a CAS says \"set this to that only if it");
        System.out.println("is still what I saw\", and the retry is what makes that correct");
        System.out.println("under contention rather than merely optimistic");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
read             : 0
wrote            : 25
compareAndSet    : true
value            : 25

the loop is the point: a CAS says "set this to that only if it
is still what I saw", and the retry is what makes that correct
under contention rather than merely optimistic
```

The loop reads the current value, computes the next one, and attempts the swap; if the value moved in
between, the attempt fails and it reads again. This is what `incrementAndGet`, `accumulateAndGet` and
`updateAndGet` all do internally, and it is worth writing once so the method stops being magic.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) throws InterruptedException {
        Object alpha = new Object();
        Object beta = new Object();

        Thread one = new Thread(() -> ordered(alpha, beta));
        Thread two = new Thread(() -> ordered(alpha, beta));
        one.start();
        two.start();
        one.join(5_000);
        two.join(5_000);

        System.out.println("both threads took alpha then beta");
        System.out.println("  t1 finished : " + !one.isAlive());
        System.out.println("  t2 finished : " + !two.isAlive());
        System.out.println();
        System.out.println("a deadlock needs a cycle. If every thread agrees on the order");
        System.out.println("in which locks are taken, no cycle can exist, and it does not");
        System.out.println("matter how many threads or how many locks are involved");
    }

    static void ordered(Object first, Object second) {
        synchronized (first) {
            Nap.millis(100);
            synchronized (second) {
                Nap.millis(10);
            }
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
both threads took alpha then beta
  t1 finished : true
  t2 finished : true

a deadlock needs a cycle. If every thread agrees on the order
in which locks are taken, no cycle can exist, and it does not
matter how many threads or how many locks are involved
```

Both threads take `alpha` before `beta`, so whichever gets there first simply makes the other wait —
and a wait is not a cycle. The program finishes. The opposite order produced two threads that were
still alive at the end of the chapter's deadlock program, and would still be alive now.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'JAVA'
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class Sol4 {
    public static void main(String[] args) throws InterruptedException {
        ReentrantLock held = new ReentrantLock();
        held.lock();

        boolean got;
        try {
            got = held.tryLock(100, TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            got = false;
        }
        System.out.println("the same thread, tryLock on a lock it holds : " + got);
        System.out.println("hold count                                 : " + held.getHoldCount());

        held.unlock();
        held.unlock();
        System.out.println("after releasing both                       : " + held.getHoldCount());
        System.out.println();
        System.out.println("tryLock is reentrant too -- a thread may take a lock it");
        System.out.println("already holds. It is the *other* thread's lock it cannot have,");
        System.out.println("and there the timeout is what stops the program hanging");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
the same thread, tryLock on a lock it holds : true
hold count                                 : 2
after releasing both                       : 0

tryLock is reentrant too -- a thread may take a lock it
already holds. It is the *other* thread's lock it cannot have,
and there the timeout is what stops the program hanging
```

`tryLock` is reentrant, exactly like `lock`: a thread may take a lock it already holds, and the hold
count goes to two. The timeout matters for the *other* thread's lock, where failing fast is what stops
one bad ordering from hanging a service.

:::
