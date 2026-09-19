---
chapter: 21
part: 3
title: "Concurrency: Threads, Processes & async/await"
summary: Pick the right concurrency tool for the job — threads or async for waiting on the network, processes for burning CPU — and measure the difference instead of guessing. Avoid the shared-state and blocking-call mistakes that make concurrent code slower and harder to debug than the sequential version.
minutes: 50
tags: [threading, multiprocessing, asyncio, GIL]
---

Your nightly job fetches 3,000 records from an API one at a time. Each round-trip is 800 ms of
waiting and 1 ms of your CPU doing anything useful, so the script spends forty minutes asleep and
essentially all of it is waste. Concurrency is how you stop paying for other people's latency. It is
also the fastest way to turn a fifty-line script into a bug that reproduces once a week, so the goal
is not "use threads everywhere" — it is knowing which of the three tools fits, and when the answer
is none of them.

## Concurrency is not parallelism

**Concurrency** is about *structure*: several tasks in progress at once, and you make progress on
whichever one is ready. **Parallelism** is about *hardware*: two instructions execute at the same
instant on two cores. One chef cooking three dishes works concurrently — chopping while the pan
heats, plating while the sauce reduces — but nothing happens in parallel; three chefs would be
parallel. Concurrency is how you organise work, parallelism is how you execute it, and you can have
the first without the second. Most of the speed-up in this chapter comes from that distinction.

## What the GIL actually does

CPython has a **Global Interpreter Lock**: a mutex that only one thread may hold at a time, and
which a thread must hold to execute Python bytecode. So no matter how many cores you have, only one
thread runs Python at any instant. Threads still help, because the interpreter releases the GIL
whenever a thread blocks on I/O — a socket read, a file write, a database query, `time.sleep` — and
another thread runs while the first one waits. That is why eight threads downloading fifty URLs is
roughly eight times faster. It is also why eight threads doing arithmetic is not faster than one:
the work is bytecode, the lock is global, and you have added scheduling overhead for nothing.
(Note the release valve: C extensions such as NumPy and Pillow drop the GIL around their heavy
loops, so threaded numeric code *can* scale — but pure Python never will.)

## `concurrent.futures`: start here

Two executors, one interface, and a `Future` object that stands in for a result you do not have
yet. Learn this API before learning `threading` and `multiprocessing` directly; it is harder to
leak a thread with it.

### `ThreadPoolExecutor` for I/O-bound work

```python
import time
import httpx
from concurrent.futures import ThreadPoolExecutor

URLS = [f"https://httpbin.org/get?n={i}" for i in range(50)]


def fetch(url: str) -> int:
    with httpx.Client(timeout=10.0) as client:
        return client.get(url).status_code


def timed(label: str, fn) -> None:
    start = time.perf_counter()
    result = fn()
    print(f"{label:<12} {time.perf_counter() - start:6.2f}s  {len(result)} responses")


def sequential() -> list[int]:
    return [fetch(u) for u in URLS]


def threaded() -> list[int]:
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(fetch, URLS))


timed("sequential", sequential)
timed("8 threads", threaded)
```

```text
sequential    74.30s  50 responses
8 threads     10.62s  50 responses
```

Roughly a 7x speed-up from one line, and nothing about the download function changed. Those numbers
depend on your network and on how willing the server is to talk to you; run it twice and compare
ratios rather than absolute seconds.

`max_workers` defaults to `min(32, os.cpu_count() + 4)`. For I/O-bound work you can go far above
your core count — 8 to 32 is a sane range — because the threads are mostly blocked. Past that you
are not going faster, you are spending memory and annoying the server.

### `submit`, `as_completed`, and where exceptions land

`map` is right when you want every result in order. When you want results *as they finish*, submit
individual jobs and iterate the futures:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(fetch, url): url for url in URLS}
    for future in as_completed(futures):
        url = futures[future]
        try:
            print(url, future.result())
        except Exception as exc:                  # re-raised here, in your thread
            print(f"{url} failed: {type(exc).__name__}: {exc}")
```

The rule that surprises people: **an exception inside a worker is not raised inside the worker.** It
is captured, stored on the `Future`, and re-raised in *your* thread when you call `future.result()`
(or when `map`'s iterator reaches that item). Nothing is lost, but if you never call `result()` the
failure vanishes silently — which is the concurrent version of `except Exception: pass`.

### `ProcessPoolExecutor` for CPU-bound work

Same API, different machinery: separate interpreter processes, each with its own GIL, so bytecode
genuinely runs in parallel.

```python
import hashlib
import time
from concurrent.futures import ProcessPoolExecutor

# Must be importable at module level - see the pitfall below.
def slow_hash(n: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", str(n).encode(), b"salt", 200_000).hex()


def main() -> None:
    numbers = list(range(64))
    start = time.perf_counter()
    digests = list(ProcessPoolExecutor().map(slow_hash, numbers))
    print(f"processes {time.perf_counter() - start:.2f}s  {len(digests)} digests")


if __name__ == "__main__":
    main()
```

Swap `ProcessPoolExecutor()` for `ThreadPoolExecutor()` and the threaded version will be no faster
than the plain loop. That single experiment teaches the GIL better than any diagram.

:::pitfall ProcessPoolExecutor deadlocks on macOS and Windows without `if __name__ == "__main__"`
Those platforms start worker processes with **spawn**, which imports your module fresh in each
child. Without the guard, every child re-runs the top-level code and tries to spawn more pools.
The failure appears as a hang, a wall of tracebacks, or `RuntimeError: An attempt has been started
a new process before the current process finished its bootstrapping phase`. Two corollaries: the
worker function must be importable at module level (a lambda, a closure, or a nested function
cannot be pickled), and everything it touches must be picklable — an instance holding a database
connection or an open socket is not.
:::

Processes are expensive to start and cannot share memory cheaply, so reserve them for work that is
genuinely CPU-bound: hashing, thumbnail generation, image resizing, parsing gigabytes, numeric
simulation.

## Shared mutable state: avoid it first

Every concurrency bug traces back to two pieces of code touching the same object at once. The
cheapest fix is not to share: let each worker take input and return output, and let the parent own
the state. That is why `map` and `submit` are the default — you never *need* a shared counter if
every job returns its own number.

Here is what happens when you do share — a cache in front of an expensive lookup, the shape of half
the concurrency bugs in production:

```python
import threading
import time

cache: dict[str, str] = {}
fetches = 0


def expensive(key: str) -> str:
    global fetches
    time.sleep(0.05)          # stand-in for a real API call or disk read
    fetches += 1
    return key.upper()


def load(key: str) -> str:
    if key in cache:          # check
        return cache[key]
    value = expensive(key)    # ...meanwhile, seven other threads are also here
    cache[key] = value        # act
    return value


threads = [threading.Thread(target=load, args=("customer:42",)) for _ in range(8)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(f"8 threads asked for 1 key, we fetched it {fetches} times")
```

```text
8 threads asked for 1 key, we fetched it 8 times
```

The bug is **check-then-act**: eight threads test `key in cache`, all find it missing, and all start
the expensive work. The GIL does not save you — `time.sleep` releases it, which is precisely the
moment a thread switch happens. Swap the sleep for any real I/O and the behaviour is identical.

:::pitfall `counter += 1` looks like the classic race demo, and on current CPython it often is not
`counter += 1` compiles to a read, an add, and a store, so in principle two threads read `5`, both
compute `6`, both store `6`, and one increment evaporates. In practice CPython checks for a thread
switch only at certain points, mostly loop boundaries, so a tight increment loop can run millions of
iterations without losing a beat. That is the worst outcome: the bug is real but invisible, and it
surfaces the day you add a function call inside the loop or move to a free-threaded build. Never
rely on atomicity you have not been promised.
:::

When you truly must mutate shared state, guard the smallest possible region with a `Lock`:

```python
cache: dict[str, str] = {}
lock = threading.Lock()


def load_locked(key: str) -> str:
    with lock:                # one thread at a time in this block
        if key in cache:
            return cache[key]
        value = expensive(key)
        cache[key] = value
        return value
```

Run it with eight threads and `fetches` comes out as `1`. Two cautions: holding the lock across
`expensive()` serialises the work you parallelised, so production code usually takes a per-key lock
or accepts the duplicate and deduplicates later; and a lock held around code that can wait on that
same lock is a deadlock.

Better still, don't touch the shared object at all — hand work through a `queue.Queue`, which is
already synchronised and is the right structure for producer/consumer pipelines:

```python
import queue
import threading
import httpx

WORKERS = 4
work: queue.Queue[str | None] = queue.Queue(maxsize=100)


def producer(urls: list[str]) -> None:
    for url in urls:
        work.put(url)
    for _ in range(WORKERS):      # one sentinel per worker, or they never exit
        work.put(None)


def worker(client: httpx.Client) -> None:
    while (url := work.get()) is not None:
        try:
            print(url, client.get(url, timeout=10.0).status_code)
        except httpx.RequestError as exc:
            print(f"{url} failed: {exc}")
        work.task_done()


with httpx.Client(timeout=10.0) as client:
    workers = [threading.Thread(target=worker, args=(client,)) for _ in range(WORKERS)]
    for thread in workers:
        thread.start()
    producer(URLS)
    for thread in workers:
        thread.join()
```

`get()` blocks until something arrives, so workers idle without burning CPU; `maxsize` stops a fast
producer from filling memory; the sentinel values are how you shut the pipeline down cleanly.

## `asyncio`: one thread, cooperative switching

Where threads are switched by the operating system at arbitrary moments, `asyncio` runs one thread
and switches only where you wrote `await`. That is the whole mental model: **a single loop, a queue
of ready coroutines, and a hand-off at every `await`.** Nothing is pre-empted, so a race condition
on ordinary Python objects is basically impossible — and in exchange, any code that does not `await`
blocks everyone.

```python
import asyncio
import time


async def brew(name: str, seconds: float) -> str:
    print(f"{time.strftime('%X')} {name}: start")
    await asyncio.sleep(seconds)      # <-- hands control back to the loop
    print(f"{time.strftime('%X')} {name}: done")
    return name


async def main() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(brew("espresso", 2), brew("pour-over", 3))
    print(results, f"{time.perf_counter() - start:.2f}s total")


asyncio.run(main())
```

```text
14:03:01 espresso: start
14:03:01 pour-over: start
14:03:03 espresso: done
14:03:04 pour-over: done
['espresso', 'pour-over'] 3.00s total
```

Three seconds, not five: the loop started the second task during the first one's sleep.

Three things to internalise:

- `async def` defines a **coroutine function**; calling it builds a coroutine object and runs
  nothing. Only `await` runs it.
- `asyncio.run(main())` is the single entry point, called once from synchronous code: it creates the
  loop, runs `main`, and shuts everything down.
- `await asyncio.gather(...)` runs coroutines concurrently and returns results in the order you
  passed them. `asyncio.create_task(coro)` starts one now and returns a `Task` you `await` later.

### Capping concurrency with a `Semaphore`

Untethered concurrency against a real server is how you get rate-limited or banned. A semaphore is
a counter that blocks once too many coroutines hold it:

```python
import asyncio


async def fetch_one(sem: asyncio.Semaphore, url: str) -> str:
    async with sem:                 # at most N of these blocks run at once
        await asyncio.sleep(0.1)    # stand-in for a real request
        return url


async def main() -> None:
    sem = asyncio.Semaphore(10)
    urls = [f"https://example.com/{i}" for i in range(200)]
    pages = await asyncio.gather(*(fetch_one(sem, u) for u in urls))
    print(len(pages))


asyncio.run(main())
```

### Timeouts and cancellation

Wrap any block in `asyncio.timeout`; when the deadline passes, the coroutine inside is **cancelled**
— a `CancelledError` is raised at its current `await` — and you get a `TimeoutError`:

```python
import asyncio


async def slow() -> str:
    await asyncio.sleep(30)
    return "never"


async def main() -> None:
    try:
        async with asyncio.timeout(2.0):
            print(await slow())
    except TimeoutError:
        print("gave up after 2s")


asyncio.run(main())
```

Cancellation is cooperative too: the loop cannot kill a task, it can only ask. Catch
`asyncio.CancelledError` if you need to release a resource, then re-raise it. For a single
awaitable, `asyncio.wait_for(coro, 2.0)` still works; prefer `asyncio.timeout` around a block,
because it cannot leave a half-created task behind.

## Async HTTP: the fifty-download benchmark, again

`httpx.AsyncClient` has the same interface as the client from Chapter 18, so the change is small:

```python
import asyncio
import time
import httpx

URLS = [f"https://httpbin.org/get?n={i}" for i in range(50)]


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    response = await client.get(url)
    return response.status_code


async def main() -> None:
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=10)
    async with httpx.AsyncClient(timeout=10.0, limits=limits) as client:
        start = time.perf_counter()
        codes = await asyncio.gather(*(fetch(client, u) for u in URLS))
        print(f"async {time.perf_counter() - start:.2f}s  {len(codes)} responses")


asyncio.run(main())
```

```text
async  8.95s  50 responses
```

Comparable to eight threads, with a fraction of the memory: fifty tasks cost kilobytes, fifty
threads cost megabytes. Create **one** client for the whole run and share it — that is what owns the
connection pool (Chapter 18), and the same rule applies to `httpx.Client` in threads.

## Choosing: the decision table

| Your work is | Symptom | Use | Why |
| --- | --- | --- | --- |
| I/O-bound, few connections, blocking libs | Waiting on HTTP, files, `subprocess` | `ThreadPoolExecutor` | No code changes; blocking calls are fine |
| I/O-bound, many connections, or a server | Thousands of sockets, WebSockets | `asyncio` | One thread, cheap tasks, no context-switch cost |
| CPU-bound, pure Python | 100% CPU, no waiting | `ProcessPoolExecutor` | Only processes beat the GIL |
| CPU-bound inside NumPy/Pillow | Releases the GIL | Threads or processes | Measure; threads share memory cheaply |
| Mixed | Fetch, then compute | Fetch async/threaded, compute in a pool | Keep the two halves separate |

**Most real problems are I/O-bound, so start with threads or async.** Reach for processes only
after you have watched a CPU pegged at 100%.

## Mixing the two worlds

Blocking code inside async is the mistake that silently destroys the whole exercise. The loop is one
thread, so `time.sleep`, `requests.get`, and an unmoved `pathlib.read_text` on a big file freeze
*every* task — including the one that would have finished in 10 ms.

```python
async def bad():
    time.sleep(2)        # freezes the entire event loop
    requests.get(url)    # same problem
```

Push it into a thread and await the result:

```python
async def good():
    await asyncio.to_thread(time.sleep, 2)                    # loop keeps running
    payload = await asyncio.to_thread(requests.get, url)      # bridge for a sync library
```

The reverse direction is one line: synchronous code calls `asyncio.run(main())`. You cannot call it
from inside a running loop — `asyncio.run` raises `RuntimeError` if a loop is already running, which
is what you will see if you try it from a FastAPI handler (Chapter 27), where the framework owns the
loop and you just `await`.

## Debugging async

Three messages you will meet, and what they actually mean:

```text
RuntimeWarning: coroutine 'fetch' was never awaited
```

You called `fetch(url)` and threw the coroutine object away. Nothing ran, nothing failed, no output.
Fix: `await fetch(url)`, or `asyncio.create_task(fetch(url))`.

```python
result = fetch(url)          # a coroutine object, not the data
type(result)                 # <class 'coroutine'>
```

A missing `await` produces no error at all until something downstream chokes on a coroutine object
where it expected a dict. Type hints (Chapter 16) catch this: `async def fetch(...) -> dict` means
`fetch(url)` is a `Coroutine[..., dict]`, not a `dict`.

```text
Task was destroyed but it is pending!
```

You created a task and the run ended before it finished, or you dropped the only reference to it so
the garbage collector removed it mid-flight. Keep a reference to every `asyncio.create_task` result
until you `await` it, and make sure `main` awaits everything it started.

:::scenario The nightly job takes 40 minutes and 90% of it is waiting
Your sync job pulls 3,000 customer records one at a time from a vendor API, enriches each one, and
writes to SQLite (Chapter 19). It runs at 02:00 and now finishes at 02:40, inside a maintenance
window that closes at 03:00. Each request takes about 800 ms; your CPU sits at 3%. Someone proposes
rewriting it in asyncio.
:::

:::solution ThreadPoolExecutor, then re-measure — you do not need a rewrite
The work is I/O-bound, so processes buy nothing and a full async rewrite is unnecessary risk. Wrap
the existing blocking fetch in a thread pool, keep the enrichment and the database write sequential,
and cap concurrency so the vendor does not rate-limit you into a 429 storm.

```python
import logging
from concurrent.futures import ThreadPoolExecutor
from itertools import islice

log = logging.getLogger(__name__)


def fetch_customer(api, customer_id: str) -> dict | None:
    try:
        return api.get_json(f"/v1/customers/{customer_id}")
    except Exception:
        log.exception("customer %s failed", customer_id)
        return None


def nightly_sync(api, customer_ids: list[str], db) -> int:
    saved = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        for payload in pool.map(lambda cid: fetch_customer(api, cid), customer_ids):
            if payload is None:
                continue
            db.upsert_customer(enrich(payload))
            saved += 1
    return saved
```

```text
before: 3000 x 0.8s = 2400s of waiting  -> 40 min end to end
after:  8 threads   =  300s of waiting  -> ~7 min, same machine
```

Three details matter more than the speed-up. The `try/except` inside the worker keeps one bad record
from killing the run — `pool.map` re-raises in the caller, so without it you would lose all 3,000 on
the first failure. `max_workers=8` is deliberately modest: check the vendor's rate limit first and
add the `RateLimiter` from Chapter 18 if they publish one. If the database write ever becomes the
bottleneck, move only that part — one writer thread fed by a `queue.Queue`, one transaction per
batch.
:::

## When concurrency is not worth it

Concurrent code is harder to read, harder to test, and produces bugs that do not reproduce. If the
sequential version takes two seconds, or two minutes unattended while nobody waits, leave it alone.
Measure first — `time.perf_counter()` around the real workload, then check whether the time is spent
waiting on I/O or burning CPU (`htop`, or `cProfile` from Chapter 11). Add concurrency only when the
measurement says the wait is real.

## Key takeaways

- Concurrency is about structure; parallelism is about hardware, and the GIL means pure-Python
  threads never execute bytecode in parallel.
- Threads and async speed up I/O-bound work; only `ProcessPoolExecutor` speeds up CPU-bound Python.
- `concurrent.futures` gives one interface for both: `map` for ordered results, `submit` plus
  `as_completed` for results as they arrive, and `Future.result()` is where worker exceptions are
  re-raised.
- Prefer pure functions that take input and return output over shared state; when you must share,
  use a `Lock` for the smallest region or a `queue.Queue` for hand-offs.
- `asyncio` runs one thread and switches only at `await`, so blocking calls freeze every task —
  move them out with `asyncio.to_thread`.
- Use `asyncio.gather` to run coroutines concurrently, `asyncio.Semaphore` to cap concurrency, and
  `asyncio.timeout` to bound how long a block may run.
- "coroutine was never awaited" means you built a coroutine and discarded it; a task whose only
  reference you drop can disappear mid-flight.
- Most real workloads are I/O-bound, so start with threads or async, and measure before and after.

## Practice

- [ ] Fetch 20 URLs sequentially with `httpx`, then with `ThreadPoolExecutor(max_workers=8)`, and
      print both wall-clock times plus the speed-up ratio.
- [ ] Write `slow_hash(n)` using `hashlib.pbkdf2_hmac` with 200,000 iterations. Time
      `ProcessPoolExecutor.map` over 64 numbers against a plain `for` loop, and explain the
      difference in the output.
- [ ] Take the `load()` cache above and add a `threading.Lock`. Run eight threads against one key
      ten times and assert `fetches == 1` every time. Then remove the lock and report how many runs
      fetched more than once.
- [ ] Rewrite the 20-URL fetch with `asyncio.gather` and an `asyncio.Semaphore(5)`, then wrap the
      whole gather in `asyncio.timeout(10)` and print a fallback message on `TimeoutError`.
- [ ] You have a blocking `parse_pdf(path)` that takes ~1s. Write `parse_all(paths)` that keeps the
      event loop responsive using `asyncio.to_thread` and returns results in the original order.
- [ ] Build `sync_customers(api, ids, db)`: fetch customers concurrently with a thread pool, retry
      each failure once with the backoff helper from Chapter 18, upsert into SQLite in batches of
      100, and return a report of succeeded and failed ids.

## Solutions

:::solution Exercise 1
```python
import time
import httpx
from concurrent.futures import ThreadPoolExecutor

URLS = [f"https://httpbin.org/get?n={i}" for i in range(20)]


def fetch(url: str) -> int:
    with httpx.Client(timeout=10.0) as client:
        return client.get(url).status_code


start = time.perf_counter()
sequential = [fetch(u) for u in URLS]
seq_time = time.perf_counter() - start

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as pool:
    threaded = list(pool.map(fetch, URLS))
thread_time = time.perf_counter() - start

print(f"sequential {seq_time:.2f}s")
print(f"8 threads  {thread_time:.2f}s")
print(f"speed-up   {seq_time / thread_time:.1f}x")
assert sequential == threaded, "same answers, different order of waiting"
```
Timing with `perf_counter` rather than `time.time` protects you from clock adjustments, and the
assertion is the point of the exercise: concurrency changes how long you wait, never what you get.
:::

:::solution Exercise 2
```python
import hashlib
import time
from concurrent.futures import ProcessPoolExecutor


def slow_hash(n: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", str(n).encode(), b"salt", 200_000).hex()


def main() -> None:
    numbers = list(range(64))

    start = time.perf_counter()
    serial = [slow_hash(n) for n in numbers]
    serial_time = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor() as pool:
        parallel = list(pool.map(slow_hash, numbers))
    parallel_time = time.perf_counter() - start

    print(f"serial    {serial_time:.2f}s")
    print(f"processes {parallel_time:.2f}s  ({serial_time / parallel_time:.1f}x)")
    assert serial == parallel


if __name__ == "__main__":
    main()
```
Expect a speed-up close to your core count. Swap in `ThreadPoolExecutor` and the ratio drops to
about 1.0 — that is the GIL: hashing is bytecode, and only one thread may execute bytecode at a
time. The `__main__` guard is mandatory under spawn.
:::

:::solution Exercise 3
```python
import threading
import time

cache: dict[str, str] = {}
fetches = 0
lock = threading.Lock()


def expensive(key: str) -> str:
    global fetches
    time.sleep(0.05)
    fetches += 1
    return key.upper()


def load_racy(key: str) -> str:
    if key in cache:
        return cache[key]
    value = expensive(key)
    cache[key] = value
    return value


def load_locked(key: str) -> str:
    with lock:
        if key in cache:
            return cache[key]
        value = expensive(key)
        cache[key] = value
        return value


def run(loader, *, threads: int = 8) -> int:
    global cache, fetches
    cache, fetches = {}, 0
    pool = [threading.Thread(target=loader, args=("customer:42",)) for _ in range(threads)]
    for thread in pool:
        thread.start()
    for thread in pool:
        thread.join()
    return fetches


racy = [run(load_racy) for _ in range(10)]
locked = [run(load_locked) for _ in range(10)]
print(f"racy:   {racy}   -> {sum(f > 1 for f in racy)}/10 runs duplicated the fetch")
print(f"locked: {locked} -> {sum(f > 1 for f in locked)}/10 runs duplicated the fetch")
assert set(locked) == {1}
```
```text
racy:   [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]   -> 10/10 runs duplicated the fetch
locked: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] -> 0/10 runs duplicated the fetch
```
`with lock` makes the check and the act one indivisible step, so the second thread sees the cache
already populated. Note that the lock covers the whole check-then-act region — guarding only the
`cache[key] = value` line would leave the window open, which is the mistake people make after
hearing "keep the critical section small".
:::

:::solution Exercise 4
```python
import asyncio
import httpx

URLS = [f"https://httpbin.org/get?n={i}" for i in range(20)]


async def fetch(client: httpx.AsyncClient, sem: asyncio.Semaphore, url: str) -> int:
    async with sem:
        return (await client.get(url)).status_code


async def main() -> None:
    sem = asyncio.Semaphore(5)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            async with asyncio.timeout(10):
                codes = await asyncio.gather(*(fetch(client, sem, u) for u in URLS))
        except TimeoutError:
            print("timed out - falling back to cached data")
            return
        print(codes)


asyncio.run(main())
```
The semaphore limits in-flight requests to five regardless of how many you submit, and
`asyncio.timeout` cancels the remaining tasks when the deadline passes rather than waiting for them
to finish. `asyncio.run` is called once, from synchronous code.
:::

:::solution Exercise 5
```python
import asyncio


def parse_pdf(path: str) -> dict:
    import time

    time.sleep(1)                     # stand-in for a real blocking parser
    return {"path": path, "pages": 7}


async def parse_all(paths: list[str]) -> list[dict]:
    return list(await asyncio.gather(*(asyncio.to_thread(parse_pdf, p) for p in paths)))


async def heartbeat() -> None:
    for _ in range(3):
        print("loop still responsive")
        await asyncio.sleep(0.4)


async def main() -> None:
    results, _ = await asyncio.gather(
        parse_all(["a.pdf", "b.pdf", "c.pdf"]), heartbeat()
    )
    print([r["path"] for r in results])


asyncio.run(main())
```
`asyncio.gather` preserves the order you passed, so results line up with `paths` even though the
threads finish out of order. The heartbeat proves the point: with `parse_pdf` called directly, those
three prints would appear only after everything finished.
:::

:::solution Exercise 6
```python
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import islice

import httpx

RETRYABLE = {429, 500, 502, 503, 504}


def fetch_customer(client: httpx.Client, customer_id: str) -> dict:
    for attempt in range(1, 3):
        response = client.get(f"/v1/customers/{customer_id}")
        if response.status_code not in RETRYABLE or attempt == 2:
            response.raise_for_status()
            return response.json()
        time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def batched(items: list, size: int):
    it = iter(items)
    while batch := list(islice(it, size)):
        yield batch


def sync_customers(base_url: str, customer_ids: list[str], db) -> dict:
    ok: list[str] = []
    failed: list[str] = []

    with httpx.Client(base_url=base_url, timeout=10.0) as client, \
            ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_customer, client, cid): cid for cid in customer_ids}

        for batch in batched(list(futures), 100):
            rows = []
            for future in batch:
                customer_id = futures[future]
                try:
                    rows.append(future.result())
                    ok.append(customer_id)
                except Exception as exc:
                    failed.append(customer_id)
                    print(f"{customer_id}: {type(exc).__name__}: {exc}")
            db.executemany("INSERT OR REPLACE INTO customers (id, payload) VALUES (?, ?)",
                           [(r["id"], str(r)) for r in rows])
            db.commit()

    return {"succeeded": ok, "failed": failed}
```
One shared `httpx.Client` is safe across threads and owns the connection pool; one retry inside the
worker keeps a single 503 from failing the night. Because `future.result()` re-raises in this
thread, per-record failures are collected instead of aborting the run, and batching writes means
3,000 records cost 30 transactions rather than 3,000.
:::
