---
chapter: 7
part: 1
title: Loops, Comprehensions & Iteration Patterns
summary: Read and write every loop a real Python program needs, transform data with comprehensions, and stop writing loops that silently skip elements.
minutes: 40
tags: [for, while, comprehension, enumerate, zip, itertools]
---

Chapter 6 gave you containers; this chapter gives you the machinery to walk them. Almost every
program you will ever write is a handful of recognisable loop shapes wearing different clothes:
transform every item, keep some of them, fold them into one answer, find the first match, or group
them by a key. Learn those five shapes and you can read anybody's Python — including your own,
six months from now.

## `for` works on anything iterable

`for` does not need a list. It needs an **iterable** — anything that can hand out its items one at
a time. Lists, tuples, strings, dicts, sets, files, and `range()` all qualify.

```python
>>> for ch in "python":
...     print(ch.upper(), end="")
PYTHON
>>> for key in {"a": 1, "b": 2}:
...     print(key)
a
b
```

Iterating a string gives characters. Iterating a dict gives keys — use `.values()` or `.items()`
if you want more.

## `range()`, `enumerate()`, `zip()`

`range(stop)`, `range(start, stop)`, `range(start, stop, step)` produces numbers lazily without
building a list, which means `range(10_000_000)` costs nothing.

```python
>>> list(range(5))
[0, 1, 2, 3, 4]
>>> list(range(2, 10, 3))
[2, 5, 8]
```

You need the index *and* the value. Beginners write `for i in range(len(items))`. Don't — use
`enumerate()`, which yields `(index, value)` pairs and takes an optional `start`.

```python
names = ["ada", "grace", "linus"]
for position, name in enumerate(names, start=1):
    print(f"{position}. {name}")
```
```text
1. ada
2. grace
3. linus
```

You need to walk two sequences together. That's `zip()`, which stops at the shortest input.

```python
questions = ["name", "quest", "colour"]
answers = ["lancelot", "the grail", "blue"]
for q, a in zip(questions, answers):
    print(f"{q}: {a}")

# Turn parallel columns into rows
pairs = list(zip(questions, answers))
```

And `zip(*rows)` — note the star — unzips: it transposes rows into columns.

```python
rows = [("ada", 36), ("grace", 45), ("linus", 54)]
names, ages = zip(*rows)
print(names)   # ('ada', 'grace', 'linus')
print(ages)    # (36, 45, 54)
```

The star unpacks `rows` into three separate arguments, so `zip` receives three 2-tuples and pairs
up their first elements and their second elements. It is the standard way to pivot data without
a library.

:::warning `zip` silently drops leftovers
`zip(["a", "b", "c"], [1, 2])` yields two pairs, not three. If mismatched lengths are a bug in
your program, pass `strict=True` (Python 3.10+) and Python raises `ValueError` instead of quietly
losing data.
:::

## The five loop patterns

Nearly all loops are one of these. Naming them makes code readable before it is finished.

**1. Map — transform every item.**

```python
prices = [10.0, 20.0, 30.0]
with_tax = [round(p * 1.2, 2) for p in prices]
```

**2. Filter — keep the ones that pass.**

```python
big = [p for p in prices if p > 15]
```

**3. Accumulate — fold everything into one value.**

```python
total = 0
for p in prices:
    total += p
# or, when it is a simple sum:
total = sum(prices)
```

**4. Find first — stop as soon as you know the answer.**

```python
found = None
for p in prices:
    if p > 25:
        found = p
        break
```

**5. Group — bucket items under a key.** Chapter 6's `setdefault` and `defaultdict` are built for
this.

```python
from collections import defaultdict

words = ["apple", "avocado", "banana", "blueberry", "cherry"]
by_letter = defaultdict(list)
for w in words:
    by_letter[w[0]].append(w)
```

### `else` on loops

A `for` or `while` loop can have an `else` clause. It runs **only if the loop finished without
`break`** — which makes it the clean way to express "search and report failure".

```python
for p in prices:
    if p > 100:
        print("expensive item found")
        break
else:
    print("nothing expensive")
```

Read it as "no-break". It is unusual enough that some teams ban it; it is also the tidiest
solution to the search-and-handle-miss problem, so at least recognise it.

## Never mutate a list while iterating over it

This is the bug that produces plausible-but-wrong results, so it survives testing.

:::pitfall Removing items while iterating skips elements
The for-loop tracks a hidden internal index. Remove the current item and every later item shifts
one slot left — so the loop's next step jumps straight past one.

```python
numbers = [1, 2, 3, 4, 5, 6]
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)
print(numbers)
```
```text
[1, 3, 5]
```

That looks correct, which is what makes the bug so expensive. Change the data slightly and it
falls apart:

```python
numbers = [1, 2, 2, 3]
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)
print(numbers)
```
```text
[1, 2, 3]
```

A `2` survived. The loop removed the first `2`, everything shifted left, and the internal index
moved on to what is now the last slot — skipping the second `2` entirely.
:::

Three correct fixes, in order of preference:

```python
# 1. Build a new list (clearest, and usually what you want)
evens = [n for n in numbers if n % 2 != 0]

# 2. Iterate over a copy, mutate the original
for n in numbers[:]:        # or list(numbers)
    if n % 2 == 0:
        numbers.remove(n)

# 3. Iterate backwards when you must delete in place by index
for i in range(len(numbers) - 1, -1, -1):
    if numbers[i] % 2 == 0:
        del numbers[i]
```

Option 1 is the one you should reach for. It is shorter, obviously correct, and does not need a
comment explaining why the slice is there.

## Comprehensions

A comprehension is a compact `for` loop that builds a collection. The shape is
`[expression for item in iterable if condition]`, and the `if` is optional.

```python
squares = [n * n for n in range(10)]
lengths = {w: len(w) for w in ["ada", "grace"]}     # dict comprehension
unique = {n % 3 for n in range(20)}                 # set comprehension
matrix = [[r * c for c in range(3)] for r in range(3)]
```

Read them outside-in: "give me `n * n` for each `n` in `range(10)`". Nested comprehensions read in
the same order as the nested loops they replace — the outer loop comes first:

```python
# These are the same
pairs = [(x, y) for x in range(3) for y in range(2)]

pairs = []
for x in range(3):
    for y in range(2):
        pairs.append((x, y))
```

Conditionals go at the end for filtering, or in the expression position for a conditional value:

```python
[n for n in range(10) if n % 2 == 0]                  # keep only evens
["even" if n % 2 == 0 else "odd" for n in range(5)]   # transform differently
```

:::note When not to use a comprehension
The rule of thumb is simple: **one loop and at most one condition**. Past that — nested loops with
their own conditions, multiple statements per item, or anything you would have to read twice —
write the real loop. A comprehension is not faster in any way that matters; it is a readability
device, and the moment it stops being readable it has failed. Never use one purely for side
effects (`[print(x) for x in items]`) — that builds a list of `None`s to throw away.
:::

## Unpacking inside `for`

When the items are themselves tuples, unpack them right in the loop header. This is why
`.items()` and `enumerate()` feel so clean.

```python
scores = [("ada", 42), ("grace", 91)]
for name, score in scores:
    print(f"{name}: {score}")

# Unpack a dict of dicts
users = {"ada": {"team": "red"}, "grace": {"team": "blue"}}
for name, info in users.items():
    print(name, info["team"])
```

## Built-ins that replace loops

Before writing an accumulation loop, check whether a built-in already does it. These are written
in C and are faster than anything you will hand-roll:

```python
numbers = [4, 8, 15, 16, 23, 42]

sum(numbers)                                  # 108
min(numbers), max(numbers)                    # (4, 42)
sorted(numbers, reverse=True)                 # new list, descending
list(reversed(numbers))                       # [42, 23, 16, 15, 8, 4]
any(n > 40 for n in numbers)                  # True  — is at least one true?
all(n > 0 for n in numbers)                   # True  — are they all true?
max(numbers, key=lambda n: n % 10)            # 8  — largest last digit
len(numbers)                                  # 6
```

`any()` and `all()` short-circuit: they stop at the first decisive answer. `reversed()` and
`sorted()` return new sequences rather than mutating; `list.reverse()` and `list.sort()` mutate and
return `None`.

## A taste of `itertools`

`itertools` is a standard-library bag of fast iterator tools. Four you will use immediately:

```python
from itertools import chain, islice, pairwise, groupby

list(chain([1, 2], [3, 4], [5]))        # [1, 2, 3, 4, 5]      — flatten one level
list(islice(range(100), 5))             # [0, 1, 2, 3, 4]      — slice any iterable
list(islice(range(100), 10, 15))        # [10, 11, 12, 13, 14]
list(pairwise([1, 2, 3, 4]))            # [(1, 2), (2, 3), (3, 4)] — consecutive pairs
```

`groupby` groups *consecutive* items sharing a key — and this is where everyone gets burned:

```python
rows = [("red", "ada"), ("blue", "grace"), ("red", "linus")]
for colour, group in groupby(rows, key=lambda r: r[0]):
    print(colour, list(group))
```
```text
red [('red', 'ada')]
blue [('blue', 'grace')]
red [('red', 'linus')]
```

Two "red" groups, because `groupby` only merges *neighbours*. Sort by the same key first:

```python
for colour, group in groupby(sorted(rows, key=lambda r: r[0]), key=lambda r: r[0]):
    print(colour, list(group))
```
```text
blue [('blue', 'grace')]
red [('red', 'ada'), ('red', 'linus')]
```

If you are grouping from unsorted data anyway, `defaultdict(list)` is usually the clearer choice.
Reach for `groupby` when the data already arrives sorted — log lines by timestamp, for instance.

:::scenario A nightly job sends duplicate invoices
Finance reports that roughly one customer in fifty is billed twice. The export script has been
running unchanged for a year. You open it and find a loop that removes already-processed orders
from a list while walking that same list.
:::

:::solution Stop mutating the thing you are iterating
The code looked like this:

```python
for order in pending:
    if already_invoiced(order):
        pending.remove(order)     # shifts everything left; the next order is skipped
    else:
        charge(order)
```

Because `remove` shifts the list, the order immediately after a removed one was never charged — and
then appeared in the next night's run, where it *was* charged. Hence duplicates, roughly
interleaved, roughly random-looking. The fix keeps the loop honest:

```python
remaining = [o for o in pending if not already_invoiced(o)]
for order in remaining:
    charge(order)
```

Two passes, no mutation during iteration, and the first pass is now a named variable you can
inspect, log, or count. Where in-place removal is genuinely required (a very large list where
copying is expensive), iterate a copy: `for order in pending[:]`. The deeper lesson: loops that
mutate their own input are where correctness goes to die. Prefer producing a new collection, and
leave the old one alone until the loop is over.
:::

## Key takeaways

- `for` iterates any iterable; strings give characters, dicts give keys unless you ask for
  `.values()` or `.items()`.
- `enumerate()` gives index and value; `zip()` walks sequences together; `zip(*rows)` transposes
  them.
- Five patterns cover most loops: map, filter, accumulate, find-first with `break`, and group into
  a dict.
- A loop's `else` runs only when no `break` happened — it is the "searched and found nothing"
  clause.
- Never add to or remove from a list while iterating it; build a new list, or iterate a copy with
  `items[:]`.
- Comprehensions build lists, dicts, and sets in one expression; keep them to one loop and one
  condition or write a real loop.
- `sum`, `min`, `max`, `sorted`, `reversed`, `any`, and `all` replace most accumulation loops and
  accept `key=`.
- `itertools.groupby` merges only *adjacent* items — sort by the same key first.

## Practice

- [ ] Write `tables.py`: print the multiplication table for 1–5 using nested loops and an
      f-string, one row per number.
- [ ] Write `temperatures.py`: given `["Mon 18", "Tue 21", "Wed 19", "Thu 25"]`, print the hottest
      day, the coldest day, and the average — using `max`, `min`, and `sum` with `key=`, and no
      manual comparison loop.
- [ ] Write `pairs.py`: turn `["ada", "grace", "linus"]` into `[(1, "ada"), (2, "grace"),
      (3, "linus")]` with `enumerate`, then back to two separate tuples with `zip(*)`.
- [ ] Write `clean.py`: given `["ok", "", "  ", "data", "", "end"]`, produce a new list containing
      only the non-empty entries after `strip()` — using a comprehension, and without modifying
      the original list.
- [ ] Write `sales.py`: given a list of `(region, amount)` tuples, print total sales per region
      using a dict (or `defaultdict`), sorted from highest-earning region to lowest.
- [ ] Write `runs.py`: given `[1, 1, 2, 2, 2, 3, 1, 1]`, print each run of consecutive equal values
      as `(value, count)` using `itertools.groupby` — for example `(1, 2), (2, 3), (3, 1), (1, 2)`.

## Solutions

:::solution Exercise 1
```python
# tables.py
for row in range(1, 6):
    cells = []
    for col in range(1, 6):
        cells.append(f"{row * col:2}")
    print(" ".join(cells))
```
```text
 1  2  3  4  5
 2  4  6  8 10
 3  6  9 12 15
 4  8 12 16 20
 5 10 15 20 25
```
The outer loop is the row, the inner loop is the column. `f"{value:2}"` pads each number to width
two so the columns line up, and `" ".join(cells)` glues the row into one string.
:::

:::solution Exercise 2
```python
temperatures = {"Mon": 18, "Tue": 21, "Wed": 19, "Thu": 25}
hottest = max(temperatures, key=temperatures.get)
coldest = min(temperatures, key=temperatures.get)
average = sum(temperatures.values()) / len(temperatures)
print(f"hottest: {hottest} ({temperatures[hottest]}C)")
print(f"coldest: {coldest} ({temperatures[coldest]}C)")
print(f"average: {average:.1f}C")
```
`max(d, key=d.get)` compares the *values* but returns the *key*, which is what you want to print.
Iterating a dict gives keys, so `sum(temperatures.values())` is the way to total the numbers.
:::

:::solution Exercise 3
```python
names = ["ada", "grace", "linus"]
numbered = list(enumerate(names, start=1))
print(numbered)                    # [(1, 'ada'), (2, 'grace'), (3, 'linus')]
positions, people = zip(*numbered)
print(positions, people)           # (1, 2, 3) ('ada', 'grace', 'linus')
```
`enumerate` produces the pairs; `zip(*numbered)` unpacks the list of pairs into two positional
arguments and re-zips them, which pivots rows into columns.
:::

:::solution Exercise 4
```python
raw = ["ok", "", "  ", "data", "", "end"]
cleaned = [s.strip() for s in raw if s.strip()]
print(cleaned)      # ['ok', 'data', 'end']
print(raw)          # unchanged
```
The comprehension filters first (`if s.strip()` — an empty string is falsy) and then transforms
what survives. Calling `strip()` twice is mildly wasteful; for anything larger you would write a
plain loop with an intermediate variable, which is exactly the readability trade-off to keep in
mind.
:::

:::solution Exercise 5
```python
from collections import defaultdict

sales = [("north", 120), ("south", 90), ("north", 60), ("east", 200), ("south", 30)]
totals = defaultdict(int)
for region, amount in sales:
    totals[region] += amount

for region, total in sorted(totals.items(), key=lambda item: item[1], reverse=True):
    print(f"{region:<6} {total:>5}")
```
```text
east     200
north    180
south    120
```
`defaultdict(int)` starts every unseen region at zero, so the loop body is a single line. Sorting
`.items()` needs a `key` that reaches into the second element of each pair — hence `item[1]`.
:::

:::solution Exercise 6
```python
from itertools import groupby

values = [1, 1, 2, 2, 2, 3, 1, 1]
runs = [(value, len(list(group))) for value, group in groupby(values)]
print(runs)
```
```text
[(1, 2), (2, 3), (3, 1), (1, 2)]
```
Here `groupby` groups *adjacent* equal values, which is precisely what "run" means, so no pre-sort
is needed — sorting would destroy the answer. Each `group` is a lazy iterator, so `len(list(...))`
is how you count it; call `list()` once, because the iterator is exhausted afterwards.
:::
