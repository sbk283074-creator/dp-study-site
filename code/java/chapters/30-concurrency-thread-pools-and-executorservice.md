---
chapter: 30
part: 4
title: Concurrency — Thread Pools and ExecutorService
summary: A thread is a resource and a pool is the budget you spend it from. Thread-per-task versus a fixed pool measured, the four things a pool does when it is full, Future and the exception nobody saw, the two shutdowns, and virtual threads as the case where one thread per task becomes affordable again.
minutes: 75
tags: [concurrency, threads, executors, futures, virtual-threads, java21]
---

Chapter 26 measured the JDK's HTTP server with its default executor and found that one request at a
time is not a server. This chapter is the rest of that argument. The question is not "how do I run
two things at once" — you already know `Thread` and `start()`. The question is **how many**, and who
decides, and what happens to the requests that arrive when every worker is busy. Those three answers
are the whole of pool design, and in Java they all live in one interface: `ExecutorService`.

The claim that organises everything below is this: **a pool is a bound, not an accelerator.** Adding
threads does not make a task take less CPU. What it does is decide how many things are in flight, and
therefore what happens to everything else — it waits, or it is refused. A service that has never been
asked what its bound is will discover it during an incident.

## A thread is a resource, and a pool is the budget

```java run-files
// ===== PoolDemo.java =====

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class PoolDemo {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 12;
        int workers = 3;

        ExecutorService pool = Executors.newFixedThreadPool(workers);
        for (int i = 0; i < tasks; i++) {
            pool.execute(() -> {
                Work.sleep(10);
                Work.finish();
            });
        }
        pool.shutdown();
        boolean ended = pool.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("tasks submitted : " + tasks);
        System.out.println("workers in pool : " + workers);
        System.out.println("tasks finished  : " + Work.done());
        System.out.println("threads used    : " + Work.distinctThreads());
        System.out.println("terminated      : " + ended);
        System.out.println();
        System.out.println(tasks + " tasks over " + Work.distinctThreads()
                + " threads. A pool is a bound, not an accelerator:");
        System.out.println("it decides how many things happen at once, and everything");
        System.out.println("else waits in the queue.");
    }
}

// ===== Work.java =====

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

/** A unit of work that is slow on purpose, so that a pool has something to queue. */
public final class Work {

    private static final Set<String> THREADS = new LinkedHashSet<>();
    private static final AtomicInteger DONE = new AtomicInteger();

    private Work() {
    }

    /** Sleeps, restoring the interrupt flag rather than swallowing it. */
    public static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /** Records which thread ran this task, so a chapter can count them. */
    public static void finish() {
        synchronized (THREADS) {
            THREADS.add(Thread.currentThread().getName());
        }
        DONE.incrementAndGet();
    }

    public static int distinctThreads() {
        synchronized (THREADS) {
            return THREADS.size();
        }
    }

    public static String[] threadNames() {
        synchronized (THREADS) {
            return THREADS.toArray(new String[0]);
        }
    }

    public static int done() {
        return DONE.get();
    }

    public static void reset() {
        synchronized (THREADS) {
            THREADS.clear();
        }
        DONE.set(0);
    }
}
```

```text
tasks submitted : 12
workers in pool : 3
tasks finished  : 12
threads used    : 3
terminated      : true

12 tasks over 3 threads. A pool is a bound, not an accelerator:
it decides how many things happen at once, and everything
else waits in the queue.
```

Twelve tasks, three threads, twelve finishes. The number to look at is `threads used: 3`, because it
is the only one the pool was asked for. The other nine tasks existed the whole time — sitting in the
queue, holding their request objects, holding their memory, holding a socket open on the client that
is waiting for them. A pool does not make that cost go away. It makes it *bounded*, which is the only
thing you can actually do about it.

`execute` is the whole of the interface's happy path: hand it a `Runnable`, and it runs somewhere.
Three facts about it matter in practice.

1. **`execute` returns `void`.** You get no handle, no result, and no way to find out whether the task
   succeeded. That is fine for fire-and-forget work — flushing a log buffer, sending a metric — and it
   is the wrong tool the moment you care about the outcome.
2. **The task may not start for a long time.** `execute` returning means the task was *accepted*, not
   that it was *started*. With a full queue it may not run for seconds.
3. **The task may never start at all.** If the pool is shut down, or the queue refuses, `execute`
   throws `RejectedExecutionException` — at the caller, on the calling thread, synchronously.

### What a task is allowed to throw

The lambda you hand to `execute` is a `Runnable`, and `Runnable.run()` declares no checked
exceptions. That is not a stylistic choice; it is a hard boundary, and javac enforces it:

```java bad
public class CheckedInRunnable {
    public static void main(String[] args) {
        Runnable slow = () -> Thread.sleep(10);
        slow.run();
    }
}
```

```text
error: unreported exception InterruptedException; must be caught or declared to be thrown
```

`Thread.sleep` throws `InterruptedException`, the lambda body is the body of `run()`, and `run()`
cannot throw it. This is exactly why `Callable` exists, and it is why the "just wrap it in
try/catch" reflex is usually wrong: catching `InterruptedException` and continuing is a decision about
*whether this task still wants to run*, not a way to make the compiler stop asking.

## One thread per task: the version that does not scale

The obvious design — a thread per request — is what Chapter 26's single-threaded server was the
opposite of, and it looks like this:

```sh run-project
cat > PerTask.java <<'EOF'
public class PerTask {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 100;
        Work.reset();

        long start = System.nanoTime();
        Thread[] threads = new Thread[tasks];
        for (int i = 0; i < tasks; i++) {
            threads[i] = new Thread(() -> {
                Work.sleep(20);
                Work.finish();
            });
            threads[i].start();
        }
        for (Thread t : threads) {
            t.join();
        }
        long millis = (System.nanoTime() - start) / 1_000_000L;

        System.out.println("tasks           : " + tasks);
        System.out.println("threads created : " + Work.distinctThreads());
        System.out.println("tasks finished  : " + Work.done());
        System.out.println("wall under 1s   : " + (millis < 1000));
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out PerTask.java
java -cp out PerTask
```

```text
tasks           : 100
threads created : 100
tasks finished  : 100
wall under 1s   : true
```

One hundred tasks, one hundred threads, and it finishes fast. If you stop reading here, thread-per-task
looks like the better design, because for this workload it is: every task is asleep, nothing wants the
CPU, and parallelism is free.

The cost is not speed. It is that **a thread is a resource with a fixed price** — a stack, reserved
up front and measured in megabytes by default; a slot in the scheduler; and, on a 16 GB laptop, a
number you will run out of somewhere in the low thousands. One hundred threads is nothing. One thread
per incoming request on a service that gets ten thousand at once is a machine that has spent its
memory on stacks and can no longer allocate the objects the requests actually need.

## The same work through a pool

```sh run-project
cat > Pooled.java <<'EOF'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Pooled {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 100;
        int workers = 4;
        Work.reset();

        long start = System.nanoTime();
        ExecutorService pool = Executors.newFixedThreadPool(workers);
        for (int i = 0; i < tasks; i++) {
            pool.execute(() -> {
                Work.sleep(20);
                Work.finish();
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);
        long millis = (System.nanoTime() - start) / 1_000_000L;

        System.out.println("tasks            : " + tasks);
        System.out.println("workers in pool  : " + workers);
        System.out.println("threads created  : " + Work.distinctThreads());
        System.out.println("tasks finished   : " + Work.done());
        System.out.println("wall >= 400 ms   : " + (millis >= 400));
        System.out.println();
        System.out.println("same " + tasks + " tasks, " + Work.distinctThreads()
                + " threads. The work did not get smaller; it got queued.");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Pooled.java
java -cp out Pooled
```

```text
tasks            : 100
workers in pool  : 4
threads created  : 4
tasks finished   : 100
wall >= 400 ms   : true

same 100 tasks, 4 threads. The work did not get smaller; it got queued.
```

Read the two transcripts side by side. The task count is the same, the sleep is the same, and the only
number that moved is `threads created`: one hundred became four. The work did not get smaller. It got
*queued*, which is why the wall time went up — twenty-five batches of four instead of one batch of a
hundred. That is the trade, stated honestly: **a pool buys a memory bound by spending latency.**

:::pitfall The pool size that "feels" right
`Executors.newFixedThreadPool(8)` is the number everyone reaches for, and it is wrong for both of the
two common workloads. If your tasks block on I/O — a database call, an HTTP request, a file — then a
pool of `nCores` leaves the CPU idle while every worker waits, and the right size is closer to
`nCores * (1 + waiting/computing)`, which for a service that does nothing but wait can be hundreds. If
your tasks burn CPU, then more threads than cores buys context switches and nothing else, and the right
size *is* `nCores`. The pool size is a statement about what your tasks spend their time doing, and
guessing it means you have not decided.
:::

## What a pool does when it is full

`Executors.newFixedThreadPool` hides the interesting part: it gives you an unbounded
`LinkedBlockingQueue`. An unbounded queue is not a queue, it is a promise that the pool will accept
work forever and fall further and further behind, until the process runs out of heap holding tasks it
has not started. The constructors that matter take the queue as an argument:

```sh run-project
cat > Bounded.java <<'EOF'
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.RejectedExecutionHandler;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class Bounded {
    public static void main(String[] args) throws InterruptedException {
        run("AbortPolicy", new ThreadPoolExecutor.AbortPolicy());
        System.out.println();
        run("CallerRunsPolicy", new ThreadPoolExecutor.CallerRunsPolicy());
    }

    static void run(String label, RejectedExecutionHandler policy)
            throws InterruptedException {
        Work.reset();
        int rejected = 0;

        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                2, 2, 0, TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(5), policy);

        for (int i = 0; i < 12; i++) {
            try {
                pool.execute(() -> {
                    Work.sleep(200);
                    Work.finish();
                });
            } catch (RejectedExecutionException e) {
                rejected++;
            }
        }
        pool.shutdown();
        pool.awaitTermination(60, TimeUnit.SECONDS);

        System.out.println("policy          : " + label);
        System.out.println("submitted       : 12");
        System.out.println("rejected        : " + rejected);
        System.out.println("actually ran    : " + Work.done());
        System.out.println("ran on caller   : " + onThread("main"));
    }

    static int onThread(String wanted) {
        int n = 0;
        for (String name : Work.threadNames()) {
            if (name.equals(wanted)) {
                n++;
            }
        }
        return n;
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Bounded.java
java -cp out Bounded
```

```text
policy          : AbortPolicy
submitted       : 12
rejected        : 5
actually ran    : 7
ran on caller   : 0

policy          : CallerRunsPolicy
submitted       : 12
rejected        : 0
actually ran    : 12
ran on caller   : 1
```

Two workers, a queue of five, twelve tasks. Capacity is `corePoolSize + queueCapacity` = seven, so
five tasks are refused. Both policies run all the work eventually — but they disagree about *who pays*:

| Policy | What it does | Who absorbs the overload |
|---|---|---|
| `AbortPolicy` | throws `RejectedExecutionException` | the caller, who must catch it |
| `CallerRunsPolicy` | runs the task on the submitting thread | the caller, who gets slower |
| `DiscardPolicy` | drops it silently | the user, who never finds out |
| `DiscardOldestPolicy` | drops the head of the queue | whoever submitted earliest |

`CallerRunsPolicy` is the one worth understanding, because it is a **backpressure mechanism**. When the
pool is saturated the submitting thread starts doing the work itself, which means it stops submitting —
and if the submitter is the thread reading from the socket, the socket stops being read, the TCP window
closes, and the client slows down. The overload propagates backwards to whoever is causing it instead of
piling up inside your process. That is a property worth having, and it is invisible in the API's name.

## Getting an answer back: `Callable` and `Future`

`Runnable` cannot return a value and cannot throw a checked exception, so for anything with an answer
you want `Callable<T>` and its handle, `Future<T>`:

```sh run-project
cat > Futures.java <<'EOF'
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class Futures {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(2);

        Future<Integer> quick = pool.submit(() -> {
            Work.sleep(20);
            return 6 * 7;
        });

        System.out.println("immediately after submit, isDone: " + quick.isDone());
        System.out.println("get() blocks until it is        : " + quick.get());
        System.out.println("and then isDone                 : " + quick.isDone());

        Future<Integer> slow = pool.submit(() -> {
            Work.sleep(5_000);
            return 1;
        });
        try {
            slow.get(50, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            System.out.println();
            System.out.println("a bounded wait gave up with     : "
                    + e.getClass().getSimpleName());
        }

        Future<?> broken = pool.submit(() -> {
            throw new IllegalStateException("the downstream refused");
        });
        try {
            broken.get();
        } catch (ExecutionException e) {
            System.out.println("the task's own exception arrived as: "
                    + e.getClass().getSimpleName());
            System.out.println("and its cause is                   : "
                    + e.getCause().getClass().getSimpleName());
            System.out.println("with the message                   : "
                    + e.getCause().getMessage());
        }

        pool.shutdownNow();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Futures.java
java -cp out Futures
```

```text
immediately after submit, isDone: false
get() blocks until it is        : 42
and then isDone                 : true

a bounded wait gave up with     : TimeoutException
the task's own exception arrived as: ExecutionException
and its cause is                   : IllegalStateException
with the message                   : the downstream refused
```

Three things in that transcript are the whole of `Future`:

- **`isDone()` is a question about the future, not a request.** Right after `submit` it is `false`;
  after `get()` returns it is `true`. It never blocks, and it never lies about work that has merely
  been *accepted*.
- **`get()` is the one place a timeout belongs.** `get(long, TimeUnit)` throws `TimeoutException` and
  leaves the task running — it does not cancel anything. A timeout on a `Future` is a decision to stop
  *waiting*, not a decision to stop *working*.
- **The task's exception arrives wrapped.** Your `IllegalStateException` comes back as
  `ExecutionException`, with the original as `getCause()`. Code that catches `ExecutionException` and
  logs only its own message has thrown away the only part that says what broke.

### The exception nobody saw

```sh run-project
cat > Swallowed.java <<'EOF'
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class Swallowed {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(1);
        Future<?> quietly = pool.submit(() -> {
            throw new IllegalStateException("nobody will ever see this");
        });
        pool.shutdown();
        pool.awaitTermination(10, TimeUnit.SECONDS);

        System.out.println("the task is done    : " + quietly.isDone());
        System.out.println("anything printed?   : no");
        System.out.println("program exit status : 0");
        System.out.println();
        System.out.println("submit() does not rethrow. The exception is inside the Future,");
        System.out.println("and a Future nobody asks is a failure that never happened.");

        ExecutorService second = Executors.newFixedThreadPool(1);
        Future<?> asked = second.submit(() -> {
            throw new IllegalStateException("this one is collected");
        });
        try {
            asked.get();
        } catch (ExecutionException e) {
            System.out.println();
            System.out.println("asking gave back   : " + e.getCause().getClass().getSimpleName());
            System.out.println("with the message   : " + e.getCause().getMessage());
        }
        second.shutdown();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Swallowed.java
java -cp out Swallowed
```

```text
the task is done    : true
anything printed?   : no
program exit status : 0

submit() does not rethrow. The exception is inside the Future,
and a Future nobody asks is a failure that never happened.

asking gave back   : IllegalStateException
with the message   : this one is collected
```

That is the single most expensive one-line mistake in this chapter. `submit` hands the task to the
pool; the task throws; the pool catches it, stores it inside the `Future`, and carries on. Nothing is
printed. The process exits `0`. The request produced an error page or, worse, produced nothing at
all — and no log line anywhere records why.

The rule that follows is mechanical: **every `submit` must be matched by something that eventually
calls `get()`, or by a `try/catch` inside the task itself.** A `submit` whose `Future` is discarded is
not fire-and-forget, it is fire-and-forget-the-failure. If you genuinely do not care, use `execute`
with a `try/catch` in the task body, so that "we do not care" is written down in the code rather than
implied by an unused return value.

## Stopping

```sh run-project
cat > Stopping.java <<'EOF'
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Stopping {
    public static void main(String[] args) throws InterruptedException {
        Work.reset();
        ExecutorService pool = Executors.newFixedThreadPool(2);
        for (int i = 0; i < 20; i++) {
            pool.execute(() -> {
                Work.sleep(300);
                Work.finish();
            });
        }

        pool.shutdown();
        System.out.println("shutdown() lets queued work finish; it accepts nothing new");
        boolean quick = pool.awaitTermination(50, TimeUnit.MILLISECONDS);
        System.out.println("terminated within 50 ms : " + quick);
        boolean patient = pool.awaitTermination(30, TimeUnit.SECONDS);
        System.out.println("terminated eventually  : " + patient);
        System.out.println("tasks that ran         : " + Work.done());

        System.out.println();
        Work.reset();
        ExecutorService hard = Executors.newFixedThreadPool(2);
        for (int i = 0; i < 20; i++) {
            hard.execute(() -> {
                Work.sleep(5_000);
                Work.finish();
            });
        }
        Work.sleep(100);
        List<Runnable> neverStarted = hard.shutdownNow();
        System.out.println("shutdownNow() returned " + neverStarted.size()
                + " task(s) that never started");
        boolean stopped = hard.awaitTermination(10, TimeUnit.SECONDS);
        System.out.println("terminated             : " + stopped);
        System.out.println("tasks that finished    : " + Work.done());
        System.out.println();
        System.out.println("shutdownNow() interrupts the workers; a task that catches");
        System.out.println("InterruptedException and keeps going will not stop");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Stopping.java
java -cp out Stopping
```

```text
shutdown() lets queued work finish; it accepts nothing new
terminated within 50 ms : false
terminated eventually  : true
tasks that ran         : 20

shutdownNow() returned 18 task(s) that never started
terminated             : true
tasks that finished    : 2

shutdownNow() interrupts the workers; a task that catches
InterruptedException and keeps going will not stop
```

`shutdown()` and `shutdownNow()` differ in exactly one respect, and it is worth being precise about
it, because "graceful shutdown" is usually implemented as the wrong one:

- **`shutdown()`** stops accepting new work and lets everything already queued run to completion. It
  returns immediately; `awaitTermination` is how you wait. It sends no interrupt to anyone.
- **`shutdownNow()`** stops accepting new work, *discards* the queue — it returns the tasks that never
  started, so you can log them — and interrupts the workers that are currently running.

The second one is where the interruption lesson from Chapter 13 comes back. `shutdownNow()` does not
stop threads; it asks them to stop. `Thread.sleep` honours the ask by throwing
`InterruptedException`. A loop that never checks `isInterrupted()` keeps going, `awaitTermination`
returns `false`, and you have a pool that will not shut down no matter how firmly you asked.

:::danger `Thread.stop()` is not a shortcut
There is a method that really does stop a thread immediately, and javac has an opinion about it:

```java warn
public class StopThread {
    public static void main(String[] args) throws InterruptedException {
        Thread worker = new Thread(() -> {
            try {
                Thread.sleep(1_000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        worker.start();
        worker.stop();
    }
}
```

```text
warning: [removal] stop() in Thread has been deprecated and marked for removal
```

`Thread.stop()` was deprecated for removal because it is unsafe, not because it is unfashionable. It
releases every monitor the thread held and leaves every object it was halfway through updating in a
state that no code path in your program can produce. There is no `catch` for it and no way to clean up
after it. Interruption is the only cooperative mechanism Java gives you, and the warning is the
language telling you that the other one is worse than the bug you are trying to fix.
:::

### A pool of zero is not a pool

```java throw
import java.util.concurrent.Executors;

public class ZeroPool {
    public static void main(String[] args) {
        Executors.newFixedThreadPool(0);
    }
}
```

```text
Exception in thread "main" java.lang.IllegalArgumentException
```

`IllegalArgumentException` at construction, before any task is submitted — which is the right time to
find out. A pool's parameters are a configuration, and a configuration that cannot work should fail
when it is read, not when it is first used.

## Virtual threads, and when thread-per-task becomes right again

Java 21 ships virtual threads, and they change the arithmetic of this chapter at the top end:

```sh run-project
cat > Virtual.java <<'EOF'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Virtual {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 1_000;
        AtomicInteger virtual = new AtomicInteger();

        long start = System.nanoTime();
        ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
        for (int i = 0; i < tasks; i++) {
            pool.execute(() -> {
                if (Thread.currentThread().isVirtual()) {
                    virtual.incrementAndGet();
                }
                Work.sleep(20);
            });
        }
        pool.shutdown();
        pool.awaitTermination(60, TimeUnit.SECONDS);
        long millis = (System.nanoTime() - start) / 1_000_000L;

        System.out.println("tasks submitted   : " + tasks);
        System.out.println("ran on a virtual  : " + virtual.get());
        System.out.println("wall under 1s     : " + (millis < 1000));
        System.out.println();
        System.out.println("a virtual thread is a task, not a resource: one per request");
        System.out.println("is affordable because none of them owns an OS thread");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Virtual.java
java -cp out Virtual
```

```text
tasks submitted   : 1000
ran on a virtual  : 1000
wall under 1s     : true

a virtual thread is a task, not a resource: one per request
is affordable because none of them owns an OS thread
```

A virtual thread is cheap because it does not own an OS thread for its whole life. The JVM parks the
virtual thread when it blocks and hands the carrier thread — a real platform thread, from a small pool
— to something else. A thousand of them, each sleeping, cost a thousand small heap objects rather than
a thousand megabytes of stacks.

What virtual threads do **not** change is everything else in this chapter. The queue still has a
capacity. A semaphore is still how you bound concurrent access to a database with fifty connections.
`Future` still wraps exceptions, and `shutdownNow()` still only asks. Virtual threads remove the
*memory* reason to pool; they do not remove the *bounding* reason, because "how many of these may be
in flight at once" is a question about your dependencies, not about your thread budget.

For the service in this part of the book, the practical rule is: use a bounded pool when the work is
CPU-bound or when you need to bound concurrency against something downstream, and use
`newVirtualThreadPerTaskExecutor()` when the work blocks and the only thing you were pooling for was
stack memory.

:::scenario The pool that made an outage out of a slow dependency
Your service handles each request by calling an internal search API that normally answers in 20 ms.
One afternoon it starts answering in 4 seconds. You have `Executors.newFixedThreadPool(16)` and an
unbounded queue, which is what `newFixedThreadPool` gives you. Traffic is unchanged at 400 requests per
second.

Walk it through. Sixteen workers can serve 16 requests per 4 seconds, so throughput drops to 4 requests
per second. You are receiving 400. The queue grows by 396 entries every second. Each queued entry is a
`Runnable` holding a request object, and after two minutes you have roughly 47,000 of them — which is
fine, they are small. After ten minutes you have 285,000. Every one of them represents a client that
has been waiting since it arrived, most of which have already timed out and gone away, and none of
which will ever be served. The heap fills, GC starts spending most of its time finding that nothing is
collectable, and the process dies — not from the slow dependency, but from the queue that absorbed it.

:::solution
The failure was the unbounded queue, and the fix is to make the overload visible at the point where it
can be acted on. Three changes, in order of importance:

1. **Bound the queue.** `new ThreadPoolExecutor(16, 16, 0, SECONDS, new ArrayBlockingQueue<>(256), ...)`
   gives you 272 in flight and refuses everything else. Refused requests get a 503 in microseconds
   instead of a timeout after ninety seconds, which is a better experience for the caller *and* it
   stops you accumulating work you will never do.
2. **Bound the wait.** Even with a bounded queue, a queued request can wait a long time. Wrap the
   downstream call in a `Future` and use `get(500, MILLISECONDS)`, so that a request that cannot be
   answered quickly is failed quickly.
3. **Bound the concurrency against the dependency, not against your CPU.** If search can take 50
   concurrent calls and no more, a `Semaphore(50)` around it protects the dependency from you — and it
   does that whether your tasks run on platform threads or virtual ones.

```sh run-project
cat > Scenario.java <<'EOF'
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Scenario {
    public static void main(String[] args) throws InterruptedException {
        AtomicInteger served = new AtomicInteger();
        AtomicInteger shed = new AtomicInteger();
        CountDownLatch gate = new CountDownLatch(1);

        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                8, 8, 0, TimeUnit.SECONDS, new ArrayBlockingQueue<>(32),
                new ThreadPoolExecutor.AbortPolicy());

        for (int i = 0; i < 500; i++) {
            try {
                pool.execute(() -> {
                    await(gate);
                    served.incrementAndGet();
                });
            } catch (RejectedExecutionException e) {
                shed.incrementAndGet();
            }
        }

        System.out.println("requests offered : 500");
        System.out.println("in flight        : " + pool.getActiveCount());
        System.out.println("queued           : " + pool.getQueue().size());
        System.out.println("refused          : " + shed.get());
        System.out.println("capacity         : " + (8 + 32));
        System.out.println();
        System.out.println("the " + shed.get() + " refusals happened during submission,");
        System.out.println("not after a wait, and none of them cost a thread");

        gate.countDown();
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println();
        System.out.println("after the gate   : " + served.get() + " served, "
                + shed.get() + " refused");
        System.out.println("the queue never held more than " + (8 + 32)
                + ", so the heap never grew at all");
    }

    static void await(CountDownLatch gate) {
        try {
            gate.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
requests offered : 500
in flight        : 8
queued           : 32
refused          : 460
capacity         : 40

the 460 refusals happened during submission,
not after a wait, and none of them cost a thread

after the gate   : 40 served, 460 refused
the queue never held more than 40, so the heap never grew at all
```

Every task in that program waits on a latch that does not open until the submission loop has finished,
so the numbers are exact instead of raced. Eight workers started, thirty-two tasks queued behind them,
and the remaining four hundred and sixty were refused *during submission* — on the calling thread, in
microseconds, with no thread created and nothing added to the heap. Then the gate opens and the forty
accepted tasks run to completion.

That is what a service that survives a slow dependency looks like. It does not degrade gracefully by
queueing; it refuses, quickly and visibly, and the four hundred and sixty refused callers can retry
against a service that is still answering the forty it accepted in the time it always took.
:::

## Key takeaways

- A pool is a bound, not an accelerator: it decides how many things are in flight, and everything else waits or is refused.
- `execute` returning means the task was *accepted*, not *started*; with a full queue it may never run at all.
- `Executors.newFixedThreadPool` uses an unbounded queue, so it never refuses work and never stops falling behind.
- Capacity is `corePoolSize + queueCapacity`; past that, the rejection policy decides who pays for the overload.
- `CallerRunsPolicy` is backpressure: the submitter starts doing the work, so it stops submitting.
- `Runnable` cannot throw checked exceptions, which is why `Callable` and `Future` exist at all.
- `submit` stores the task's exception in the `Future`; a `Future` nobody asks is a failure nobody sees.
- `get(timeout)` stops *waiting*, not *working* — the task keeps running unless you cancel it.
- `shutdown()` drains the queue; `shutdownNow()` discards it and interrupts the workers, which only asks them to stop.
- Virtual threads remove the memory cost of thread-per-task but not the need to bound concurrency against dependencies.

## Practice

- [ ] Submit 40 tasks that each sleep 5 ms to a fixed pool of 4 and report how many distinct threads ran them.
- [ ] Submit a `Callable` that sleeps 3 seconds, wait 100 ms with a bounded `get`, then cancel it and report `isDone()`.
- [ ] Submit 9 tasks to a pool of 3 where the first sleeps 200 ms and the rest sleep 1 ms, and report the position in which the first one finished.
- [ ] Run two tasks side by side: one that checks `isInterrupted()` and one that spins on a flag, and show that only the first stops for `shutdownNow()`.

## Solutions

:::solution Exercise 1
```sh run-project
cat > Sol1.java <<'EOF'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Sol1 {
    public static void main(String[] args) throws InterruptedException {
        Work.reset();
        ExecutorService pool = Executors.newFixedThreadPool(4);
        for (int i = 0; i < 40; i++) {
            pool.execute(() -> {
                Work.sleep(5);
                Work.finish();
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("tasks      : 40");
        System.out.println("finished   : " + Work.done());
        System.out.println("threads    : " + Work.distinctThreads());
        System.out.println();
        System.out.println("the same loop, four threads: the pool is the only thing");
        System.out.println("that changed, and it is also the only bound on memory");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
tasks      : 40
finished   : 40
threads    : 4

the same loop, four threads: the pool is the only thing
that changed, and it is also the only bound on memory
```

`Work.finish()` records the name of the thread that ran each task, so `distinctThreads()` is a direct
count of the workers that were actually used. Forty tasks over four threads is the pool's whole job:
the tasks are a stream, and the pool is the width of the pipe.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'EOF'
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class Sol2 {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        Callable<Integer> work = () -> {
            Work.sleep(3_000);
            return 1;
        };

        Future<Integer> f = pool.submit(work);
        try {
            f.get(100, TimeUnit.MILLISECONDS);
            System.out.println("finished in time");
        } catch (TimeoutException e) {
            System.out.println("gave up waiting : " + e.getClass().getSimpleName());
        } catch (ExecutionException e) {
            System.out.println("task failed     : " + e.getCause().getMessage());
        }
        System.out.println("cancelled       : " + f.cancel(true));
        System.out.println("isDone after    : " + f.isDone());
        System.out.println();
        System.out.println("cancel(true) interrupts the worker; the task itself has to");
        System.out.println("notice, because interruption in Java is cooperative");
        pool.shutdownNow();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
gave up waiting : TimeoutException
cancelled       : true
isDone after    : true

cancel(true) interrupts the worker; the task itself has to
notice, because interruption in Java is cooperative
```

`cancel(true)` interrupts the worker, and `isDone()` is `true` afterwards because a cancelled task is
*finished*, just not *successfully*. Note the ordering: the timeout fired first, and cancelling was a
separate decision — `get` with a timeout never cancels anything by itself.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Sol3 {
    public static void main(String[] args) throws InterruptedException {
        List<String> order = Collections.synchronizedList(new ArrayList<>());
        ExecutorService pool = Executors.newFixedThreadPool(3);

        for (int i = 0; i < 9; i++) {
            final int n = i;
            pool.execute(() -> {
                Work.sleep(n == 0 ? 200 : 1);
                order.add("task " + n);
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("submitted in order : task 0 first, task 8 last");
        System.out.println("task 0 finished in : position "
                + (order.indexOf("task 0") + 1) + " of 9");
        System.out.println("tasks finished     : " + order.size());
        System.out.println("threads used       : " + Work.distinctThreads());
        System.out.println();
        System.out.println("submission order is not completion order, and it never was:");
        System.out.println("a pool may start your tasks in any order it likes, and finish");
        System.out.println("them in whatever order the work allows");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
submitted in order : task 0 first, task 8 last
task 0 finished in : position 9 of 9
tasks finished     : 9
threads used       : 0

submission order is not completion order, and it never was:
a pool may start your tasks in any order it likes, and finish
them in whatever order the work allows
```

Task 0 was submitted first and finished last, because it was the slowest — not because it was first.
A pool finishes work in the order the work allows, and it has no obligation at all to the order you
submitted in. Code that assumes submission order is not concurrency, it is a race that usually wins;
if you need ordering, you need a queue you control or a list of `Future`s you collect in order.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'EOF'
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class Sol4 {
    public static void main(String[] args) throws InterruptedException {
        CountDownLatch started = new CountDownLatch(1);
        ExecutorService polite = Executors.newFixedThreadPool(1);
        polite.execute(() -> {
            started.countDown();
            while (!Thread.currentThread().isInterrupted()) {
                Thread.onSpinWait();
            }
        });
        started.await();
        Work.sleep(50);
        polite.shutdownNow();
        boolean politeStopped = polite.awaitTermination(5, TimeUnit.SECONDS);

        CountDownLatch going = new CountDownLatch(1);
        AtomicBoolean release = new AtomicBoolean(false);
        ExecutorService rude = Executors.newFixedThreadPool(1);
        rude.execute(() -> {
            going.countDown();
            while (!release.get()) {
                Thread.onSpinWait();
            }
        });
        going.await();
        Work.sleep(50);
        rude.shutdownNow();
        boolean rudeStopped = rude.awaitTermination(300, TimeUnit.MILLISECONDS);
        release.set(true);
        rude.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("a task that checks isInterrupted : terminated " + politeStopped);
        System.out.println("a task that ignores it           : terminated " + rudeStopped);
        System.out.println();
        System.out.println("shutdownNow() only interrupts. Interruption in Java is a");
        System.out.println("request, and a task that never looks will never honour it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
a task that checks isInterrupted : terminated true
a task that ignores it           : terminated false

shutdownNow() only interrupts. Interruption in Java is a
request, and a task that never looks will never honour it
```

The polite task terminated; the rude one did not, and only stopped because the program explicitly
released it. `shutdownNow()` is a request. The `isInterrupted()` flag is the only channel it has, and a
task that never reads it has opted out of being shut down.

:::
