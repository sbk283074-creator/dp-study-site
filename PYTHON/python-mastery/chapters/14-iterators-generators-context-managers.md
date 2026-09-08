---
chapter: 14
part: 2
title: Iterators, Generators & Context Managers
summary: Control iteration yourself with `iter`/`next`, process files larger than RAM with generator pipelines, and guarantee cleanup with `with`.
minutes: 45
tags: [iterators, generators, yield, itertools, context managers]
---

Every `for` loop you have written so far has been hiding a two-step conversation with the object
you were looping over. Most of the time you do not care. You care the day a 6 GB log file has to
be summarised on a machine with 2 GB of spare memory, or the day a script crashes halfway through
and leaves a file handle open. Both problems are the same problem: you handed control of *when*
and *how much* to something that assumed small inputs and clean exits. Iterators and context
managers are the two tools Python gives you to take that control back.

## Iterables and iterators

An **iterable** is anything you can loop over: a list, a string, a dict, a file object, a
`range`. An **iterator** is the thing that actually does the walking. They are not the same
object, and the distinction explains almost every confusing thing about looping.

```python
>>> nums = [10, 20, 30]
>>> it = iter(nums)      # ask the list for an iterator
>>> next(it)             # pull one value
10
>>> next(it)
20
>>> next(it)
30
>>> next(it)
Traceback (most recent call last):
  ...
StopIteration
```

`iter(obj)` calls `obj.__iter__()`, which must return an iterator. `next(it)` calls
`it.__next__()`, which returns the next value or raises `StopIteration` when there is nothing
left. That is the entire protocol: one method to get the walker, one method to take a step.

A `for` loop is sugar for exactly that, wrapped in a `try`:

```python
def manual_for(items):
    iterator = iter(items)
    while True:
        try:
            item = next(iterator)
        except StopIteration:
            return
        print(item)

manual_for(["a", "b", "c"])
```

```text
a
b
c
```

The loop stops on `StopIteration` and Python swallows the exception — that is why you never see
it. Knowing this lets you do things `for` cannot, like pulling two values at a time or stopping
on a sentinel value:

```python
>>> it = iter(["keep", "keep", "STOP", "never seen"])
>>> for line in it:
...     if line == "STOP":
...         break
...     print(line)
keep
keep
```

Because the iterator is a separate object with its own position, two loops over the same list do
not interfere — each calls `iter()` and gets a fresh iterator. Two loops over the *same
iterator* share one position, which is where the pitfall at the end of this chapter comes from.

Dictionaries make the iterable/iterator split obvious, because you choose what you want to walk:

```python
>>> d = {"a": 1, "b": 2}
>>> list(iter(d))
['a', 'b']
>>> list(iter(d.values()))
[1, 2]
>>> list(iter(d.items()))
[('a', 1), ('b', 2)]
```

### Writing an iterator by hand

Any class with `__iter__` and `__next__` is an iterator. You met classes in Chapter 12; this is
what they are for:

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self          # note: returns itself

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for n in Countdown(3):
    print(n)
```

```text
3
2
1
```

`__iter__` returning `self` is what makes this iterator **single-use**. Loop over the same
`Countdown(3)` object twice and the second loop prints nothing, because `self.current` is already
at zero. Lists do not have this problem because `list.__iter__` returns a *new* iterator object
each time.

## Generators: `yield` suspends a function

Writing `__iter__`/`__next__` by hand is tedious and error-prone. A **generator function** is a
function containing `yield`, and calling it gives you an iterator with no boilerplate at all:

```python
def countdown(start):
    while start > 0:
        yield start
        start -= 1

print(list(countdown(3)))
```

```text
[3, 2, 1]
```

You never see the class, but you get one. Calling `countdown(3)` does not run a single line of
the body — it returns a generator object:

```python
>>> countdown(3)
<generator object countdown at 0x104b8c2c0>
```

The body runs only when something calls `next()`. Here is the part worth internalising: when
execution reaches `yield`, the function **pauses**. Its local variables, its position in the
loop, everything on its stack, stay exactly as they are. The next `next()` call resumes from the
line after the `yield`.

```python
def stages():
    print("first run")
    yield 1
    print("second run")
    yield 2
    print("third run")

s = stages()
print(next(s))
print(next(s))
print(next(s))
```

```text
first run
1
second run
2
third run
```

That third `next(s)` printed `third run` and then raised `StopIteration` — it fell off the end of
the function without finding another `yield`. Watch for that: the code *after* the last `yield`
does run, on the call that ends the generator. Any cleanup you put there is real cleanup.

## Generator expressions vs list comprehensions

Chapter 7 introduced comprehensions. Swap the brackets for parentheses and you get a generator
expression: the same values, produced lazily instead of all at once.

```python
import sys

squares_list = [n * n for n in range(1_000_000)]
squares_gen = (n * n for n in range(1_000_000))

print(f"list:      {sys.getsizeof(squares_list):>10,} bytes")
print(f"generator: {sys.getsizeof(squares_gen):>10,} bytes")
```

```text
list:         8,000,056 bytes
generator:          104 bytes
```

Eight megabytes versus a hundred bytes, for the same million numbers. The generator is small
because it holds no values — only the recipe. The exact generator size varies by Python version;
it is always around a hundred bytes regardless of how many items it will produce. (And the list
understates the real cost: the `int` objects it points at are not counted by `getsizeof`.)

The rule:

- Use a **list comprehension** when you need the values more than once, or need `len()`, indexing,
  or sorting.
- Use a **generator expression** when you will consume the values exactly once, in order —
  especially as the argument to `sum()`, `any()`, `all()`, `max()`, `min()`, `join()`, or a
  `for` loop.

```python
>>> sum(n * n for n in range(1_000_000))
333332833333500000
```

That computed the same sum as the list version without ever holding a million values in memory.

## Infinite generators and `itertools`

A generator does not have to end. Since values are produced on demand, a generator can be
infinite and still be perfectly safe to use — as long as you take a finite piece of it.

```python
def naturals(start=1):
    while True:
        yield start
        start += 1

from itertools import islice

print(list(islice(naturals(), 5)))
print(list(islice(naturals(100), 3)))
```

```text
[1, 2, 3, 4, 5]
[100, 101, 102]
```

`islice(iterable, stop)` and `islice(iterable, start, stop[, step])` are the off switch. Without
it, `list(naturals())` will hang until your machine dies.

`itertools` is a library of exactly these pieces, all lazy and all written in C:

| Function | What it does |
|---|---|
| `count(start, step)` | infinite arithmetic sequence |
| `cycle(iterable)` | repeats an iterable forever |
| `chain(a, b, ...)` | iterates several iterables as one |
| `islice(it, n)` | takes a slice without materialising |
| `takewhile(pred, it)` | yields until the predicate first fails |
| `pairwise(it)` | overlapping pairs: `(1,2)`, `(2,3)`, ... |
| `batched(it, n)` | fixed-size tuples (new in 3.12) |

```python
>>> from itertools import batched, chain
>>> list(batched("abcdefg", 3))
[('a', 'b', 'c'), ('d', 'e', 'f'), ('g',)]
>>> list(chain.from_iterable([[1, 2], [3, 4]]))
[1, 2, 3, 4]
```

### `yield from`

When one generator needs to hand over to another iterable, `yield from` replaces the loop:

```python
# these are equivalent
yield from source
for item in source:
    yield item
```

It reads better and it is marginally faster. Its real use is flattening:

```python
from pathlib import Path

def read_many(paths):
    for path in paths:
        with open(path, encoding="utf-8") as f:
            yield from f          # every line of every file, one stream

def numbered(lines):
    for n, line in enumerate(lines, start=1):
        yield f"{n:>4} | {line.rstrip()}"
```

Two small generators, composed. Neither one knows or cares how many files or how many lines
there are.

## Pipelines: the shape that scales

Here is the payoff. Suppose a service writes logs like this and you need the error lines grouped
by service:

```python
from pathlib import Path

Path("app.log").write_text(
    """2026-09-07T09:01:12Z INFO  api.gateway path=/login status=200
2026-09-07T09:02:45Z ERROR api.auth invalid token for user 42
2026-09-07T09:03:10Z WARN  api.gateway slow response 1.9s
2026-09-07T09:04:02Z ERROR api.auth invalid token for user 17
""",
    encoding="utf-8",
)
```

Write four small generators and wire them together:

```python
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        yield from f

def parse(lines):
    for line in lines:
        timestamp, level, service, *rest = line.split(maxsplit=3)
        yield {
            "ts": timestamp,
            "level": level,
            "service": service,
            "message": " ".join(rest).strip(),
        }

def with_level(records, wanted):
    return (r for r in records if r["level"] == wanted)

def messages(records):
    return (r["message"] for r in records)

errors = with_level(parse(read_lines(Path("app.log"))), "ERROR")
for message in messages(errors):
    print(message)
```

```text
invalid token for user 42
invalid token for user 17
```

Nothing here builds a list. `read_lines` yields one line, `parse` yields one record,
`with_level` passes it on or drops it, and the loop prints it. Peak memory is one line, whether
the file is 4 KB or 40 GB. Total time to first output is microseconds, not however long it takes
to read the whole file.

This is the Unix pipe model, in Python, with real data structures instead of text. It is the
single most useful pattern in this chapter, and Chapter 20's automation tools are built on it.

:::note `send()`, `throw()`, `close()`
Generators also have `send(value)` (resume, and make the `yield` expression evaluate to
`value`), `throw(exc)` (raise an exception at the pause point), and `close()` (finish early).
These turn generators into coroutines, and they are the foundation of `async` code — which is a
Chapter 21 topic. For everyday data pipelines you will not need them. Know they exist; do not
reach for them.
:::

## Context managers: what `with` guarantees

You have been writing `with open(...) as f` since Chapter 8. Here is what it actually buys you.

```python
class Demo:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        print(f"exit (exception: {exc_type})")
        return False        # False = do not swallow the exception

with Demo():
    print("body")
```

```text
enter
body
exit (exception: None)
```

Run it again with `raise ValueError("boom")` in the body and you get `enter`, `exit (exception:
<class 'ValueError'>)`, then the traceback. **That is the guarantee: `__exit__` runs no matter
how the block ends** — normal fall-through, `return`, `break`, `continue`, or an exception
propagating up. It is `try/finally` with a name on it.

Return `True` from `__exit__` and you suppress the exception. That is occasionally right (see
`suppress` below) and usually a bug.

### Five-line context managers with `contextlib`

Writing the class every time is noise. `contextlib.contextmanager` turns a generator into one:

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.4f}s")

with timer("sort"):
    sorted(range(200_000), reverse=True)
```

```text
sort: 0.0104s
```

The mechanics map directly onto the class form: code before `yield` is `__enter__`, the yielded
value is what `as` binds, and code after `yield` is `__exit__`. Put the cleanup in `finally` so it
runs even if the body raises.

### The class form, when you need state

The generator form cannot easily keep state or be reused. Here is a temporary working directory
that always puts you back where you started — a genuinely useful thing in test suites and build
scripts:

```python
import os
import tempfile
from pathlib import Path

class temp_cwd:
    def __init__(self, path=None):
        self.path = Path(path or tempfile.mkdtemp())
        self.original = None

    def __enter__(self):
        self.original = Path.cwd()
        os.chdir(self.path)
        return self.path

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.original)
        return False
```

```python
print(Path.cwd())
with temp_cwd() as scratch:
    Path("note.txt").write_text("written in the scratch dir", encoding="utf-8")
    print(Path.cwd(), sorted(p.name for p in Path(".").iterdir()))
print(Path.cwd())
```

```text
/Users/you/python-mastery/14
/var/folders/xy/tmp8k1n2 ['note.txt']
/Users/you/python-mastery/14
```

Without the `with`, one exception anywhere in that block leaves your process in a directory that
may have been deleted underneath it. With it, you cannot get that wrong.

:::tip Two more from `contextlib`
`contextlib.suppress(*exceptions)` is a readable alternative to `try/except/pass`:
`with suppress(FileNotFoundError): Path("cache.json").unlink()`.

`ExitStack` handles a variable number of resources — you enter them in a loop and it closes all
of them in reverse order:

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(p, encoding="utf-8")) for p in Path(".").glob("*.log")]
    first_lines = [f.readline() for f in files]
```

Three files or three hundred, all of them get closed.
:::

:::scenario The nightly report job dies at 02:00
Your report job reads a day of application logs, filters them, and writes a summary. It worked
fine for months on the 40 MB staging export. In production it runs out of memory and gets killed,
and the on-call engineer has to re-run it by hand. The code looks harmless: three functions, each
returning a list, each feeding the next.
:::

:::solution Stop returning lists
The bug is the *shape*, not the logic. Every intermediate list holds the entire dataset, so peak
memory is three times the file size plus the original text:

```python
# before — three full copies in memory at once
def load(path):      return open(path).read().splitlines()
def errors(lines):   return [l for l in lines if " ERROR " in l]
def services(lines): return [l.split()[2] for l in lines]

counts = {}
for s in services(errors(load("app.log"))):
    counts[s] = counts.get(s, 0) + 1
```

Change each function to a generator and the pipeline streams. Peak memory becomes one line:

```python
# after — one line in flight at any moment
from collections import Counter

def load(path):
    with open(path, encoding="utf-8") as f:
        yield from f

def errors(lines):
    return (l for l in lines if " ERROR " in l)

def services(lines):
    return (l.split()[2] for l in lines)

counts = Counter(services(errors(load("app.log"))))
print(counts.most_common(5))
```

Two things to notice. First, `Counter` consumes any iterable, so it never needed a list. Second,
the call site reads identically — `services(errors(load(...)))` — because generators compose.
The general lesson: when a function's only job is to feed a loop, make it a generator. Lists are
for when you genuinely need the whole thing.
:::

:::pitfall An iterator is single-use
This bites everyone exactly once, usually in a debugging session:

```python
>>> gen = (n * 2 for n in range(3))
>>> list(gen)
[0, 2, 4]
>>> list(gen)
[]
>>> sum(gen)
0
>>> max(gen)
Traceback (most recent call last):
  ...
ValueError: max() arg is an empty sequence
```

The first `list(gen)` drained it. Every subsequent call sees an exhausted iterator and gets
nothing — no error from `list()` or `sum()`, just empty results that look like a logic bug
somewhere else. The same thing happens with a file object you have already read, and with
`map`/`filter` results.

Fixes, in order of preference: build the generator fresh each time you need it
(`list(n * 2 for n in range(3))` written twice), or materialise it once into a list or tuple if
you genuinely need multiple passes. If you find yourself re-running a pipeline, that is the
signal you wanted a list.
:::

## Key takeaways

- `iter(obj)` returns an iterator; `next(it)` advances it and raises `StopIteration` at the end.
- A `for` loop is `iter()` plus repeated `next()` plus a caught `StopIteration`.
- A generator function contains `yield`; calling it returns a paused generator object whose
  locals survive between `next()` calls.
- Generator expressions use the same syntax as list comprehensions with parentheses, and hold
  O(1) memory instead of O(n).
- Iterate an unbounded generator only through something that stops it, like `islice` or
  `takewhile`.
- `yield from other` is shorthand for `for x in other: yield x`, and is how you flatten streams.
- `with` guarantees `__exit__` (or the code after `yield`) runs on every exit path, including
  exceptions.
- `@contextmanager` plus `try`/`finally` gives you a context manager in five lines; use the
  `__enter__`/`__exit__` class form when you need to keep state.

## Practice

- [ ] Write a `countdown(n)` generator that yields `n, n-1, ..., 1`, and loop over it with `for`.
      Then replace the loop with `list(...)` and confirm the output.
- [ ] Write `manual_for(items)` using `iter()` and `next()` in a `while` loop with
      `try/except StopIteration`, and use it to print the characters of a string.
- [ ] Use `sys.getsizeof` to compare `[n**2 for n in range(1_000_000)]` with
      `(n**2 for n in range(1_000_000))`, then `sum()` both and confirm the results match.
- [ ] Build a three-stage pipeline over `app.log` from this chapter: yield raw lines, yield only
      lines whose level is `ERROR`, and yield `(timestamp, service)` tuples. Print them.
- [ ] Write `@contextmanager def timer(label)` and use it to time a `time.sleep(0.2)` call.
- [ ] Write a `temp_cwd` class context manager, change directory inside the block, create a file,
      and prove you are back in the original directory afterwards.

## Solutions

:::solution Exercise 1
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for value in countdown(5):
    print(value, end=" ")
print()
print(list(countdown(5)))
```
```text
5 4 3 2 1
[5, 4, 3, 2, 1]
```
`for` and `list()` both just drive `next()` until `StopIteration`; the generator does not care
which one is asking.
:::

:::solution Exercise 2
```python
def manual_for(items):
    iterator = iter(items)
    while True:
        try:
            item = next(iterator)
        except StopIteration:
            return
        print(item)

manual_for("python")
```
```text
p
y
t
h
o
n
```
`iter()` works on strings as well as lists, which is why `for ch in "python"` has always worked.
:::

:::solution Exercise 3
```python
import sys

squares_list = [n**2 for n in range(1_000_000)]
squares_gen = (n**2 for n in range(1_000_000))

print(sys.getsizeof(squares_list), sys.getsizeof(squares_gen))
print(sum(squares_list) == sum(squares_gen))
```
```text
8000056 104
True
```
Same answer, eight megabytes versus a hundred bytes. The list built a million integers up front;
the generator produced and discarded each one as `sum()` asked for it.
:::

:::solution Exercise 4
```python
from pathlib import Path

def raw_lines(path):
    with open(path, encoding="utf-8") as f:
        yield from f

def only_errors(lines):
    return (line for line in lines if " ERROR " in line)

def stamp_and_service(lines):
    return (line.split(maxsplit=3)[0::2] for line in lines)

records = stamp_and_service(only_errors(raw_lines(Path("app.log"))))
for ts, service in records:
    print(ts, service)
```
```text
2026-09-07T09:02:45Z api.auth
2026-09-07T09:04:02Z api.auth
```
`line.split(maxsplit=3)` gives `[ts, level, service, message]`; the slice `[0::2]` takes elements
0 and 2. Each stage is independent and testable, and none of them holds more than one line.
:::

:::solution Exercise 5
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.4f}s")

with timer("sleep"):
    time.sleep(0.2)
```
```text
sleep: 0.2013s
```
The `finally` matters: if the body raises, you still get the timing printed before the exception
propagates. Without `try`/`finally` an exception would skip the print entirely.
:::

:::solution Exercise 6
```python
import os
import tempfile
from pathlib import Path

class temp_cwd:
    def __init__(self, path=None):
        self.path = Path(path or tempfile.mkdtemp())
        self.original = None

    def __enter__(self):
        self.original = Path.cwd()
        os.chdir(self.path)
        return self.path

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.original)
        return False

before = Path.cwd()
with temp_cwd() as scratch:
    Path("hello.txt").write_text("hi", encoding="utf-8")
    print("inside:", Path.cwd())
print("after:", Path.cwd())
print("restored:", Path.cwd() == before)
```
```text
inside: /var/folders/xy/tmpq3z1_m
after: /Users/you/python-mastery/14
restored: True
```
Returning `False` from `__exit__` means exceptions are not suppressed — you still get
restored, but you also still see the error. Never `return True` here unless swallowing is the
actual requirement.
:::
