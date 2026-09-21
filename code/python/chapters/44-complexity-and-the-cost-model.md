---
chapter: 44
part: 8
title: Complexity and the Cost Model
summary: Reason about what code costs before you run it, and measure it afterwards without fooling yourself. Count the steps, name the growth rate, measure the constant factors, and tell a benchmark that means something from one that does not.
minutes: 75
tags: [big-o, theta, omega, growth rates, amortised cost, timeit, benchmarking]
---

Every program in this book so far has been written to be correct. This part of the book is about the
other question: what does it cost?

That question has a reputation for being academic, and it earns that reputation when it is taught as
notation. But you have already met it in a practical form. In Chapter 35 the enemies searched a grid;
in Chapter 19 a database query returned a list you then scanned; in Chapter 6 you learned that a set
answers "is this in here?" and a list does not. Each of those was a cost decision, made or missed.

This chapter gives you the two tools for making those decisions deliberately: **counting**, which is
exact and tells you the shape of the curve, and **timing**, which is noisy and tells you the height of
it. Getting them the right way round is most of the skill.

## Two programs, one answer

Here is a membership check written two ways. They return identical answers for identical input.

```python run
import timeit

MEMBERS = [f"user{i}" for i in range(10_000)]
MEMBERS_SET = set(MEMBERS)
QUERIES = [f"user{i}" for i in range(0, 10_000, 97)] + ["nobody"]


def in_list(name):
    """Compare the name against every entry, in order."""
    comparisons = 0
    for member in MEMBERS:
        comparisons += 1
        if member == name:
            return True, comparisons
    return False, comparisons


def in_set(name):
    """Hash the name once and look in one bucket."""
    return name in MEMBERS_SET, 1


def scan_each():
    return [in_list(q) for q in QUERIES]


def hash_each():
    return [in_set(q) for q in QUERIES]


def best(fn, number, repeat=7):
    return min(timeit.repeat(fn, number=number, repeat=repeat))


def magnitude(ratio):
    """Coarse bands: the third significant figure is noise, not evidence."""
    for edge, label in ((5, "~2x"), (20, "~10x"), (60, "~30x"), (400, "~100x")):
        if ratio < edge:
            return label
    return "~1000x or more"


scan_answers = [ok for ok, _ in scan_each()]
set_answers = [ok for ok, _ in hash_each()]
worst_comparisons = max(c for _, c in scan_each())

print(f"the same {len(QUERIES)} questions, asked two ways")
print("both give identical answers:", scan_answers == set_answers)
print()
print("  scanning the list")
print(f"    worst case per question : {worst_comparisons} comparisons")
print(f"    total for this run      : {sum(c for _, c in scan_each())} comparisons")
print("  asking the set")
print("    per question            : 1 hash, whatever the size")
print()
t_list = best(scan_each, 20)
t_set = best(hash_each, 20)
print(f"  measured cost of the list version : {magnitude(t_list / t_set)} the set version")
print()
print("Nothing about the answers changed. Only the cost did.")
print()
print("The list version's cost is proportional to the number of members.")
print("The set version's cost is not. Add a million more members and the")
print("first gets a million times worse while the second does not move.")
print("That difference is a growth rate, and no amount of tuning the")
print("constant factor will close it.")
```

```text
the same 105 questions, asked two ways
both give identical answers: True

  scanning the list
    worst case per question : 10000 comparisons
    total for this run      : 529636 comparisons
  asking the set
    per question            : 1 hash, whatever the size

  measured cost of the list version : ~1000x or more the set version

Nothing about the answers changed. Only the cost did.

The list version's cost is proportional to the number of members.
The set version's cost is not. Add a million more members and the
first gets a million times worse while the second does not move.
That difference is a growth rate, and no amount of tuning the
constant factor will close it.
```

The comparison count is the part to notice. For 105 questions the list version did **529,636**
comparisons. That number is not a property of this machine — it is a property of the algorithm, and it
is the same on yours. The measured ratio, by contrast, is a property of this machine on this run, which
is why it is reported as a band rather than as a figure.

So there are two questions, and they are answered by different instruments. *How does the cost grow?*
is answered by counting. *How big is the cost right now?* is answered by timing. A benchmark without a
growth rate is a snapshot of a moving target, and a growth rate without a measurement is a claim about
the world that nobody has checked.

## Count the steps first

Before timing anything, count. Counting is exact, it is reproducible, and it does not care what else
the machine is doing.

Each function below returns the number of iterations it performed. Nothing is being measured; the
program is just doing arithmetic on the shapes.

```python run
def count_constant(n):
    """One step, whatever n is."""
    return 1


def count_log(n):
    """Halve until you reach 1."""
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps


def count_linear(n):
    """One step per item."""
    steps = 0
    for _ in range(n):
        steps += 1
    return steps


def count_nlogn(n):
    """A linear pass, repeated while the window doubles."""
    steps = 0
    size = 1
    while size < n:
        for _ in range(n):
            steps += 1
        size *= 2
    return steps


def count_quadratic(n):
    """Every item against every other item."""
    steps = 0
    for _ in range(n):
        for _ in range(n):
            steps += 1
    return steps


def count_cubic(n):
    """Every pair, against every item."""
    steps = 0
    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                steps += 1
    return steps


COLUMNS = [
    ("const", count_constant),
    ("log n", count_log),
    ("n", count_linear),
    ("n log n", count_nlogn),
    ("n^2", count_quadratic),
    ("n^3", count_cubic),
]

header = f"{'n':>6}  " + "  ".join(f"{name:>9}" for name, _ in COLUMNS)
print(header)
print("-" * len(header))
for n in (1, 2, 4, 8, 16, 32, 64, 128, 256):
    row = [fn(n) for _, fn in COLUMNS]
    print(f"{n:>6}  " + "  ".join(f"{v:>9}" for v in row))

print()
print("The numbers are exact and reproducible: nothing here depends on")
print("the machine, the clock, or the interpreter. Counting is the first")
print("tool, and the one you should reach for before timing anything.")
```

```text
     n      const      log n          n    n log n        n^2        n^3
------------------------------------------------------------------------
     1          1          0          1          0          1          1
     2          1          1          2          2          4          8
     4          1          2          4          8         16         64
     8          1          3          8         24         64        512
    16          1          4         16         64        256       4096
    32          1          5         32        160       1024      32768
    64          1          6         64        384       4096     262144
   128          1          7        128        896      16384    2097152
   256          1          8        256       2048      65536   16777216

The numbers are exact and reproducible: nothing here depends on
the machine, the clock, or the interpreter. Counting is the first
tool, and the one you should reach for before timing anything.
```

The table is the whole of complexity theory in practice. `n^3` is 16,777,216 at n=256, and the only
reason that program finished is that 256 is small. Double n once more and it is 134 million steps.
Double it again and you are waiting.

Now look at what happens to each column when you double n. That ratio is the fingerprint of the shape,
and it is a better thing to learn than the notation:

```python run
def steps_log(n):
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count


def steps_linear(n):
    count = 0
    for _ in range(n):
        count += 1
    return count


def steps_nlogn(n):
    count = 0
    size = 1
    while size < n:
        for _ in range(n):
            count += 1
        size *= 2
    return count


def steps_quadratic(n):
    count = 0
    for _ in range(n):
        for _ in range(n):
            count += 1
    return count


def steps_cubic(n):
    count = 0
    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                count += 1
    return count


CASES = [
    ("log n", steps_log),
    ("n", steps_linear),
    ("n log n", steps_nlogn),
    ("n^2", steps_quadratic),
    ("n^3", steps_cubic),
]

print("double n and watch what the step count does")
print()
print(f"{'shape':>8}  {'n=64':>10}  {'n=128':>10}  {'n=256':>10}   ratio at each doubling")
print("-" * 72)
for name, fn in CASES:
    a, b, c = fn(64), fn(128), fn(256)
    r1, r2 = b / a, c / b
    print(f"{name:>8}  {a:>10}  {b:>10}  {c:>10}   {r1:>5.2f} then {r2:>5.2f}")

print()
print("Read the last column, not the middle one:")
print()
print("  log n     adds a constant, so the ratio falls towards 1")
print("  n         ratio 2      -- doubling the input doubles the work")
print("  n log n   ratio 2.2    -- barely more than n; the log is a small factor")
print("  n^2       ratio 4      -- doubling the input quadruples the work")
print("  n^3       ratio 8      -- and this is where it stops being usable")
print()
print("A ratio of 4 is the signature of a quadratic. It does not matter what")
print("the machine is, what the language is, or how fast the constant factor")
print("is: doubling the input multiplies the work by four, every time.")
```

```text
double n and watch what the step count does

   shape        n=64       n=128       n=256   ratio at each doubling
------------------------------------------------------------------------
   log n           6           7           8    1.17 then  1.14
       n          64         128         256    2.00 then  2.00
 n log n         384         896        2048    2.33 then  2.29
     n^2        4096       16384       65536    4.00 then  4.00
     n^3      262144     2097152    16777216    8.00 then  8.00

Read the last column, not the middle one:

  log n     adds a constant, so the ratio falls towards 1
  n         ratio 2      -- doubling the input doubles the work
  n log n   ratio 2.2    -- barely more than n; the log is a small factor
  n^2       ratio 4      -- doubling the input quadruples the work
  n^3       ratio 8      -- and this is where it stops being usable

A ratio of 4 is the signature of a quadratic. It does not matter what
the machine is, what the language is, or how fast the constant factor
is: doubling the input multiplies the work by four, every time.
```

Logarithmic growth is worth a second look, because its ratio *falls* towards 1 rather than sitting at
some value. Halving reaches 1 in a fixed number of steps, and each doubling of n only adds one more:

```python repl
>>> def halvings(n):
...     steps = 0
...     while n > 1:
...         n //= 2
...         steps += 1
...     return steps
>>> halvings(1_000_000)
19
>>> halvings(2_000_000)
20
>>> halvings(4_000_000)
21
```

A million becomes two million and the work grows by one step. That is why a log-time algorithm is
almost always worth having: the input can grow by a factor of a thousand and the cost barely moves.

## O, Θ and Ω are three different claims

The notation gets used loosely, and the looseness causes real arguments. Here is what each symbol
actually claims.

- **O(f)** is an upper bound. The cost grows *no faster than* f.
- **Ω(f)** is a lower bound. The cost grows *no slower than* f.
- **Θ(f)** is both. The cost grows *at the same rate as* f.

Saying "this is O(n²)" is a weak claim. It is also true of a function that is O(n), because n is no
faster than n². The useful statement is usually Θ.

The subtlety that catches people is that a single function can have different bounds depending on
which input you ask about:

```python run
def find(xs, target):
    """Return (index, comparisons); index is -1 when target is absent."""
    for i, x in enumerate(xs):
        if x == target:
            return i, i + 1
    return -1, len(xs)


DATA = list(range(1_000))

print("the same function, asked three different questions")
print()
idx, cmp_best = find(DATA, 0)
print(f"  target at the front : index {idx:>3}, {cmp_best:>4} comparisons")
idx, cmp_worst = find(DATA, 999)
print(f"  target at the back  : index {idx:>3}, {cmp_worst:>4} comparisons")
idx, cmp_absent = find(DATA, -1)
print(f"  target absent       : index {idx:>3}, {cmp_absent:>4} comparisons")
print()

n = len(DATA)
print(f"n = {n}")
print(f"  best case    : 1 comparison          -> the function is Omega(1)")
print(f"  worst case   : n comparisons          -> the function is O(n)")
print(f"  average case : (n + 1) / 2 = {n + 1} / 2 = {(n + 1) / 2}")
print()
print("So 'what is the complexity of find()?' has no single answer, and the")
print("question is incomplete without a case. Omega(1) and O(n) are both")
print("true of this one function. A bound on its own is not a claim about")
print("speed -- it is a claim about which case you are describing.")
```

```text
the same function, asked three different questions

  target at the front : index   0,    1 comparisons
  target at the back  : index 999, 1000 comparisons
  target absent       : index  -1, 1000 comparisons

n = 1000
  best case    : 1 comparison          -> the function is Omega(1)
  worst case   : n comparisons          -> the function is O(n)
  average case : (n + 1) / 2 = 1001 / 2 = 500.5

So 'what is the complexity of find()?' has no single answer, and the
question is incomplete without a case. Omega(1) and O(n) are both
true of this one function. A bound on its own is not a claim about
speed -- it is a claim about which case you are describing.
```

:::pitfall "Worst case" is not "the case you will meet"
When somebody says an algorithm is O(n²), they almost always mean the worst case, and the worst case
is often adversarial rather than typical. Quicksort's worst case is O(n²) and its average case is
O(n log n), and in practice it behaves like the average case on nearly every input you will hand it.

So the worst case is the bound you quote when you need a guarantee, and the average case is the bound
you quote when you need a prediction. Saying which one you mean is the difference between a
specification and a rumour.
:::

## Timing tells you the height, not the shape

Now the other instrument. The same four shapes, measured with a clock instead of counted:

```python run
import timeit


# --- counters: exact, machine-independent -------------------------------
def steps_log(n):
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count


def steps_linear(n):
    count = 0
    for _ in range(n):
        count += 1
    return count


def steps_nlogn(n):
    count = 0
    size = 1
    while size < n:
        for _ in range(n):
            count += 1
        size *= 2
    return count


def steps_quadratic(n):
    count = 0
    for _ in range(n):
        for _ in range(n):
            count += 1
    return count


# --- the same four shapes, as real work ---------------------------------
def work_log(n):
    total = 0
    while n > 1:
        n //= 2
        total += 1
    return total


def work_linear(n):
    return sum(range(n))


def work_nlogn(n):
    return sorted(range(n))


def work_quadratic(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total


def best(fn, n, number, repeat=7):
    """The minimum of several repeats. Noise only ever ADDS time, so the
    minimum is the closest thing to the true cost that we can measure."""
    return min(timeit.repeat(lambda: fn(n), number=number, repeat=repeat))


def measured_shape(ratio):
    """Deliberately wide bands. A measured ratio is an estimate, and the
    gaps between the real classes are much wider than the noise."""
    if ratio < 1.5:
        return "~1"
    if ratio < 3.0:
        return "~2"
    if ratio < 7.0:
        return "~4-6"
    return "~8+"


CASES = [
    ("log n", steps_log, work_log, 400_000, 20),
    ("n", steps_linear, work_linear, 400_000, 20),
    ("n log n", steps_nlogn, work_nlogn, 200_000, 10),
    ("n^2", steps_quadratic, work_quadratic, 400, 1),
]

print("the counted ratio is exact; the measured one is an estimate")
print()
print(f"{'shape':>8}  {'counted':>8}  {'measured':>9}  {'verdict':>9}")
print("-" * 42)
for name, steps, work, n, number in CASES:
    counted = steps(2 * n) / steps(n)
    measured = measured_shape(best(work, 2 * n, number) / best(work, n, number))
    verdict = "agrees" if measured == measured_shape(counted) else "DISAGREES"
    print(f"{name:>8}  {counted:>8.2f}  {measured:>9}  {verdict:>9}")

print()
print("The counted column is arithmetic: it is the same on every machine,")
print("and it is the one to quote. The measured column is a clock reading,")
print("and it is only ever an estimate -- which is why it is reported as a")
print("band and not as a number.")
print()
print("Both columns put every shape in the same bucket. That is what makes a")
print("complexity claim worth something: the ratio is a property of the")
print("algorithm, so it survives the move from counting to timing.")
print()
print("Notice that n and n log n land in the same bucket. At the sizes we")
print("timed, log n goes from 18 to 19, so the n log n ratio comes out at")
print("2.11 against the linear shape's 2.00 -- a difference far smaller than")
print("the noise in any clock reading. If you need to tell those two apart,")
print("count; do not time.")
```

```text
the counted ratio is exact; the measured one is an estimate

   shape   counted   measured    verdict
------------------------------------------
   log n      1.06         ~1     agrees
       n      2.00         ~2     agrees
 n log n      2.11         ~2     agrees
     n^2      4.00       ~4-6     agrees

The counted column is arithmetic: it is the same on every machine,
and it is the one to quote. The measured column is a clock reading,
and it is only ever an estimate -- which is why it is reported as a
band and not as a number.

Both columns put every shape in the same bucket. That is what makes a
complexity claim worth something: the ratio is a property of the
algorithm, so it survives the move from counting to timing.

Notice that n and n log n land in the same bucket. At the sizes we
timed, log n goes from 18 to 19, so the n log n ratio comes out at
2.11 against the linear shape's 2.00 -- a difference far smaller than
the noise in any clock reading. If you need to tell those two apart,
count; do not time.
```

That last point is the one to carry away. `n` and `n log n` are genuinely different, and at any size
you can conveniently measure they are indistinguishable. The difference is real and it is small, and
pretending a stopwatch can resolve it is how people end up defending `sorted(...)[0]` over `min`.

Note also what the program did *not* print: any absolute time. That is deliberate. A microsecond figure
from this machine is not a fact about yours, and a book that prints one is inviting you to compare two
numbers that were never comparable. What travels is the ratio.

## The real constant factors

Ratios tell you the shape. They do not tell you which of two things with the same shape is cheaper, and
that question comes up constantly. So: the actual cost of ordinary Python operations, measured against
the cheapest thing there is, a local variable read.

```python run
import timeit


class Point:
    __slots__ = ("x",)

    def __init__(self):
        self.x = 1


P = Point()
D = {"k": 1}
LST = [1, 2, 3]
X = 3
G = {"p": P, "d": D, "lst": LST, "x": X}

OPS = [
    ("local read      x", "x"),
    ("global read     len", "len"),
    ("attribute read  p.x", "p.x"),
    ("list index      lst[0]", "lst[0]"),
    ("dict lookup     d['k']", "d['k']"),
    ("builtin call    len(lst)", "len(lst)"),
    ("isinstance      isinstance(x, int)", "isinstance(x, int)"),
    ("list build      [x, x]", "[x, x]"),
    ("method call     lst.count(1)", "lst.count(1)"),
    ("dict build      {'a': x}", "{'a': x}"),
    ("set build       {x, 1}", "{x, 1}"),
    ("f-string        f'{x}'", "f'{x}'"),
]

NUMBER = 500_000
ROUNDS = 7


def multiple(ratio):
    """Deliberately coarse. The exact value is noise; the order is not."""
    if ratio < 1.6:
        return "1x"
    if ratio < 2.5:
        return "2x"
    if ratio < 3.5:
        return "3x"
    if ratio < 5.5:
        return "4x"
    if ratio < 7.0:
        return "6x"
    return "10x or more"


def measure():
    """Interleave the operations, round by round, and keep the fastest
    reading of each. Measuring all of one operation and then all of the
    next would let the machine drift between them; alternating spreads
    any drift across every row equally."""
    base = float("inf")
    bests = {label: float("inf") for label, _ in OPS}
    for _ in range(ROUNDS):
        base = min(base, timeit.timeit("x", number=NUMBER, globals=G))
        for label, stmt in OPS:
            bests[label] = min(bests[label],
                               timeit.timeit(stmt, number=NUMBER, globals=G))
    return base, bests


base, bests = measure()

print("every operation below costs about the same, in the same loop,")
print("measured against a bare local-variable read.")
print()
print(f"{'operation':<36}{'cost':>14}")
print("-" * 50)
for label, _ in OPS:
    print(f"{label:<36}{multiple(bests[label] / base):>14}")

print()
print("The spread from the cheapest row to the dearest is roughly sixfold.")
print("Everything in that range is 'one thing', which is why a program that")
print("does the same number of things twice as fast is not interesting, and")
print("a program that does a million times more things is.")
```

```text
every operation below costs about the same, in the same loop,
measured against a bare local-variable read.

operation                                     cost
--------------------------------------------------
local read      x                               1x
global read     len                             1x
attribute read  p.x                             1x
list index      lst[0]                          1x
dict lookup     d['k']                          2x
builtin call    len(lst)                        2x
isinstance      isinstance(x, int)              2x
list build      [x, x]                          4x
method call     lst.count(1)                    4x
dict build      {'a': x}                        4x
set build       {x, 1}                          6x
f-string        f'{x}'                          6x

The spread from the cheapest row to the dearest is roughly sixfold.
Everything in that range is 'one thing', which is why a program that
does the same number of things twice as fast is not interesting, and
a program that does a million times more things is.
```

Every operation in that table is between one and six times the cost of reading a local variable. That
is the entire range of "micro-optimisation": a factor of six, and most of the table sits at one or two.

There is one detail in that program worth stealing, because it is the difference between a table that
reproduces and a table that does not. The measurements are **interleaved**: round one measures the
baseline and every operation, round two does the same, and so on, keeping the fastest reading of each.
The obvious alternative — measure the baseline seven times, then measure each operation seven times —
lets the machine drift between the two groups. A CPU that changes frequency halfway through the run
then produces a ratio that is partly a fact about the frequency change. Alternating spreads any drift
across every row equally, and the table stops wobbling between runs.

Now compare that with the previous section, where a change of data structure moved the cost by three
orders of magnitude and kept going. That is the whole argument for caring about complexity before you
care about constants, and it is also the argument for not caring about constants *until* you have the
shapes right. The order matters: pick the right curve first, then worry about where on it you sit.

:::tip The one constant factor worth knowing
Everything in the table is within a factor of six, so memorising it buys you very little. The
exceptions are the operations that are not in the same class at all: `len()` is O(1) rather than O(n),
`x in dict` is O(1) rather than O(n), and `list.append` is amortised O(1). Those are worth knowing
cold. The rest is noise you can measure when it matters.
:::

## Amortised cost: why `append` is O(1)

`list.append` is the standard example of a cost that is not what it appears to be. Appending to a list
is O(1). But sometimes appending to a list copies the entire list. Both statements are true, and
understanding how they fit together is the point of this section.

A list is a small object holding a pointer to a separate array of slots. `sys.getsizeof` reports the
size of both, so subtracting the size of an empty list gives the slot count:

```python run
import sys

EMPTY = sys.getsizeof([])


def capacity(lst):
    """The list object holds a pointer to a separate array of slots.
    getsizeof reports both, so the difference is the slot count."""
    return (sys.getsizeof(lst) - EMPTY) // 8


def next_capacity(size):
    """CPython's growth rule from list_resize():
        newsize + (newsize >> 3) + 6,  rounded down to a multiple of 4
    where newsize is the length being asked for."""
    newsize = size + 1
    return (newsize + (newsize >> 3) + 6) & ~3


buf = []
previous = 0
print(f"sys.getsizeof([]) = {EMPTY} bytes, so each slot costs 8 bytes")
print()
print(f"{'length':>7}  {'capacity':>9}  {'rule predicts':>14}  {'match?':>6}")
print("-" * 42)
for length in range(1, 150):
    buf.append(length)
    now = capacity(buf)
    if now != previous:
        predicted = next_capacity(previous)
        verdict = "yes" if predicted == now else "NO"
        print(f"{length:>7}  {now:>9}  {predicted:>14}  {verdict:>6}")
        previous = now

print()
print("Every reallocation follows the same rule, and the rule never")
print("allocates exactly the length asked for. It always overshoots, and")
print("by more than a fixed amount: the surplus grows with the list.")
print()
print("That overshoot is the reason appending is cheap on average. A list")
print("that grew by exactly one slot each time would have to copy the whole")
print("array on every single append. Because it grows by a fraction of its")
print("own size, the copies get rarer the bigger the list gets -- and the")
print("total copying for n appends comes out proportional to n, not n^2.")
```

```text
sys.getsizeof([]) = 56 bytes, so each slot costs 8 bytes

 length   capacity   rule predicts  match?
------------------------------------------
      1          4               4     yes
      5          8               8     yes
      9         16              16     yes
     17         24              24     yes
     25         32              32     yes
     33         40              40     yes
     41         52              52     yes
     53         64              64     yes
     65         76              76     yes
     77         92              92     yes
     93        108             108     yes
    109        128             128     yes
    129        148             148     yes
    149        172             172     yes

Every reallocation follows the same rule, and the rule never
allocates exactly the length asked for. It always overshoots, and
by more than a fixed amount: the surplus grows with the list.

That overshoot is the reason appending is cheap on average. A list
that grew by exactly one slot each time would have to copy the whole
array on every single append. Because it grows by a fraction of its
own size, the copies get rarer the bigger the list gets -- and the
total copying for n appends comes out proportional to n, not n^2.
```

Look at the capacities: 4, 8, 16, 24, 32, 40, 52, 64, 76, 92, 108, 128, 148, 172. Each one is the
previous length plus an eighth of itself plus six, rounded down to a multiple of four. The list
overshoots, and the overshoot grows with the list.

That is what makes the amortised argument work. Let us count the total copying:

```python run
def cpython_growth(size):
    """CPython's list_resize growth rule: overshoot by about an eighth."""
    newsize = size + 1
    return (newsize + (newsize >> 3) + 6) & ~3


def doubling_growth(size):
    """The other classic policy: double the array when it fills up."""
    return max(4, size * 2)


def copies_for(n, growth):
    """Total element copies performed while appending n items to an empty
    list. A reallocation copies every element the list already holds."""
    total = 0
    capacity = 0
    size = 0
    for _ in range(n):
        if size == capacity:
            total += size                 # every existing element moves
            capacity = growth(capacity)
        size += 1
    return total


print("what does appending n items to an empty list really cost?")
print()
print(f"{'n':>9}  {'CPython':>10}  {'copies/n':>9}  {'doubling':>10}  {'copies/n':>9}")
print("-" * 54)
for n in (1_000, 10_000, 100_000, 1_000_000):
    c = copies_for(n, cpython_growth)
    d = copies_for(n, doubling_growth)
    print(f"{n:>9}  {c:>10}  {c / n:>9.2f}  {d:>10}  {d / n:>9.2f}")

print()
print("Both columns grow in step with n, so the total work for n appends is")
print("proportional to n either way. That is the amortised argument: divide")
print("the total by n and you get a constant, so a single append is O(1) on")
print("average -- even though the append that triggers a reallocation is")
print("O(n) all by itself.")
print()
print("The two policies differ in the size of that constant, and the reason")
print("is worth working out. CPython overshoots by an eighth, so each")
print("reallocation is 9/8 of the last and the copies form a geometric series")
print("with ratio 8/9, which sums to at most 9 times the final size. Doubling")
print("has a ratio of 1/2, which sums to at most 2. So the CPython column")
print("sits near 8 or 9 and the doubling column sits between 1 and 2 -- a")
print("factor of about five in copying, in the doubling policy's favour.")
print()
print("It pays for that in memory. A doubling list is, at worst, twice as long")
print("as it needs to be; CPython's is at worst an eighth too long. The")
print("interpreter chose to spend memory to save copying, and it made the")
print("same trade-off for dicts and for bytearray. When you write a growable")
print("container of your own, that is the decision in front of you.")
```

```text
what does appending n items to an empty list really cost?

        n     CPython   copies/n    doubling   copies/n
------------------------------------------------------
     1000        7556       7.56        1020       1.02
    10000       83136       8.31       16380       1.64
   100000      798128       7.98      131068       1.31
  1000000     8445096       8.45     1048572       1.05

Both columns grow in step with n, so the total work for n appends is
proportional to n either way. That is the amortised argument: divide
the total by n and you get a constant, so a single append is O(1) on
average -- even though the append that triggers a reallocation is
O(n) all by itself.

The two policies differ in the size of that constant, and the reason
is worth working out. CPython overshoots by an eighth, so each
reallocation is 9/8 of the last and the copies form a geometric series
with ratio 8/9, which sums to at most 9 times the final size. Doubling
has a ratio of 1/2, which sums to at most 2. So the CPython column
sits near 8 or 9 and the doubling column sits between 1 and 2 -- a
factor of about five in copying, in the doubling policy's favour.

It pays for that in memory. A doubling list is, at worst, twice as long
as it needs to be; CPython's is at worst an eighth too long. The
interpreter chose to spend memory to save copying, and it made the
same trade-off for dicts and for bytearray. When you write a growable
container of your own, that is the decision in front of you.
```

So "append is O(1)" is a claim about a *sequence* of appends, not about any individual one. The
individual append that triggers a reallocation is O(n) — genuinely, measurably, and unavoidably. What
the amortised bound says is that those expensive appends are rare enough that they do not change the
total.

This is the shape of a whole family of results. `dict` insertion is amortised O(1) for the same reason.
`deque.appendleft` is amortised O(1). Any time you see the word *amortised*, it means "this operation
is occasionally expensive, and the expensive ones are spread thinly enough that the total stays
proportional to the count".

## A claim about a program, not about a syntax

Here is a piece of folklore you have probably met: *building a string with `+=` is O(n²); use `join`.*

It is worth checking, because the reason people give for it turns out to be wrong.

```python run
import timeit


def build(n):
    s = ""
    for _ in range(n):
        s += "ab"
    return s


def best(n, number=3, repeat=7):
    return min(timeit.repeat(lambda: build(n), number=number, repeat=repeat))


def growth(ratio):
    """Bucketed, because a measured ratio is an estimate."""
    if ratio < 1.4:
        return "~1  (constant)"
    if ratio < 3.0:
        return "~2  (linear)"
    if ratio < 6.8:
        return "~4  (quadratic)"
    return "~8  (cubic)"


print("'building a string with += is O(n^2); use join' -- the standard advice.")
print()
print("Here is that exact pattern, measured:")
print()
print(f"{'n':>7}  {'on doubling n':>16}")
print("-" * 26)
for n in (1_000, 2_000, 4_000):
    print(f"{n:>7}  {growth(best(2 * n) / best(n)):>16}")

print()
print("Every doubling doubles the time. That is linear, not quadratic.")
print()
print("The advice is not wrong, it is incomplete. CPython has a special case")
print("in its string concatenation: when the left-hand string has exactly one")
print("reference to it, and no other name is looking at it, the interpreter")
print("resizes it in place instead of allocating a new one and copying. In a")
print("tight loop that is exactly the situation, so += becomes cheap and the")
print("quadratic term never appears.")
print()
print("Which means the next program is the interesting one: change one line")
print("so that the old string is still referenced, and watch what happens.")
```

```text
'building a string with += is O(n^2); use join' -- the standard advice.

Here is that exact pattern, measured:

      n     on doubling n
--------------------------
   1000      ~2  (linear)
   2000      ~2  (linear)
   4000      ~2  (linear)

Every doubling doubles the time. That is linear, not quadratic.

The advice is not wrong, it is incomplete. CPython has a special case
in its string concatenation: when the left-hand string has exactly one
reference to it, and no other name is looking at it, the interpreter
resizes it in place instead of allocating a new one and copying. In a
tight loop that is exactly the situation, so += becomes cheap and the
quadratic term never appears.

Which means the next program is the interesting one: change one line
so that the old string is still referenced, and watch what happens.
```

So the loop is linear. Now the same statement, with one added line that keeps the previous value alive:

```python run
import timeit


def tight(n):
    """The old string dies at each assignment, so CPython resizes in place."""
    s = ""
    for _ in range(n):
        s += "ab"
    return s


def with_a_second_reference(n):
    """Identical loop, except the previous string is kept alive."""
    s = ""
    history = []
    for _ in range(n):
        history.append(s)      # <- the only difference
        s += "ab"
    return s


def best(fn, n, number=3, repeat=7):
    return min(timeit.repeat(lambda: fn(n), number=number, repeat=repeat))


def band(ratio):
    if ratio < 2.0:
        return "~1x"
    if ratio < 4.5:
        return "~3x"
    if ratio < 8.0:
        return "~6x"
    return "~10x or more"


print("two functions. The string-building loop is the same statement.")
print("One of them also keeps the previous value in a list.")
print()
print(f"{'n':>7}  {'kept version / tight version':>29}")
print("-" * 40)
for n in (1_000, 2_000, 4_000, 8_000):
    gap = best(with_a_second_reference, n) / best(tight, n)
    print(f"{n:>7}  {band(gap):>29}")

print()
print("At n=1000 the two are within a small factor of each other. By n=8000")
print("the gap has grown by roughly an order of magnitude -- and it is still")
print("growing, because one is linear and the other is quadratic.")
print()
print("The lesson is not about strings. It is that a complexity claim is a")
print("claim about a program, not about a syntax. `s += t` is O(1) amortised")
print("in one loop and O(n) per step in another, and the difference is not")
print("visible in the line of code -- it is visible in what else holds a")
print("reference to the object.")
print()
print("This is why the folklore is worth checking. 'Always use join' is")
print("cheap advice that is sometimes wrong; 'measure the pattern you")
print("actually wrote' is expensive advice that is never wrong.")
```

```text
two functions. The string-building loop is the same statement.
One of them also keeps the previous value in a list.

      n   kept version / tight version
----------------------------------------
   1000                            ~3x
   2000                            ~3x
   4000                            ~6x
   8000                   ~10x or more

At n=1000 the two are within a small factor of each other. By n=8000
the gap has grown by roughly an order of magnitude -- and it is still
growing, because one is linear and the other is quadratic.

The lesson is not about strings. It is that a complexity claim is a
claim about a program, not about a syntax. `s += t` is O(1) amortised
in one loop and O(n) per step in another, and the difference is not
visible in the line of code -- it is visible in what else holds a
reference to the object.

This is why the folklore is worth checking. 'Always use join' is
cheap advice that is sometimes wrong; 'measure the pattern you
actually wrote' is expensive advice that is never wrong.
```

Two loops, the same `+=`, and one is linear while the other is quadratic. The only difference is that in
the second version the previous string is still reachable, so CPython cannot resize in place and has to
allocate a fresh string and copy the old one into it. Every append copies the whole accumulated string,
and the copies add up to n².

:::warning The bound is a property of the program, not the line
This is the most practically useful idea in the chapter, and the easiest to get wrong. You cannot read
complexity off a line of code. `x in things` is O(1) if `things` is a set and O(n) if it is a list.
`sorted(xs)[0]` is O(n log n) where `min(xs)` is O(n). `list.pop(0)` is O(n) where `deque.popleft()` is
O(1).

In each case the syntax is nearly identical and the cost model is completely different. When you
reason about cost, reason about the *objects* involved and what they are made of — not about the shape
of the expression.
:::

## A measurement that means something

Timing is easy to do and easy to do badly. Two disciplines make the difference.

The first is choosing how long to measure for. `timeit` runs a statement some number of times and
reports the total; if the total is too small, you are measuring the clock rather than the code.

```python run
import timeit


def time_band(seconds):
    if seconds < 1e-3:
        return "under 1 ms"
    if seconds < 1.0:
        return "1 ms to 1 s"
    return "over 1 s"


def verdict(seconds):
    if seconds < 1e-3:
        return "too short"
    return "usable"


CASES = [
    ("x = 1", "x = 1", 1),
    ("x = 1", "x = 1", 10_000_000),
    ("sum(range(1000))", "sum(range(1000))", 1),
    ("sum(range(1000))", "sum(range(1000))", 10_000),
    ("sorted(range(10000))", "sorted(range(10000))", 100),
]

print("the same statements, each measured 7 times, at two different")
print("values of `number`. `number` is how many times the statement runs")
print("inside one measurement; only the total is timed.")
print()
print(f"{'statement':<22}{'number':>10}  {'measured total':>15}  {'verdict':>10}")
print("-" * 62)
for label, stmt, number in CASES:
    total = min(timeit.repeat(stmt, number=number, repeat=7))
    print(f"{label:<22}{number:>10}  {time_band(total):>15}  {verdict(total):>10}")

print()
print("A statement that finishes in tens of nanoseconds cannot be measured")
print("once. The clock is good, but not that good, and everything else")
print("happening on the machine -- the operating system, other processes,")
print("the CPU changing frequency -- is larger than the thing you are")
print("trying to measure. Run it a million times and divide: the noise")
print("averages out because the work does not.")
print()
print("Aim for a measurement that takes at least a tenth of a second. If")
print("it is shorter, raise `number`. timeit will pick one for you if you")
print("let it.")
print()
print("And once you have the repeats, take the *minimum*, not the mean.")
print("Noise on a shared machine only ever adds time -- a run can be slow")
print("because something else was running, but it cannot be faster than")
print("the work itself. So the fastest run is the closest estimate of the")
print("true cost, and the mean is an estimate of the true cost plus")
print("whatever else the machine was doing at the time.")
```

```text
the same statements, each measured 7 times, at two different
values of `number`. `number` is how many times the statement runs
inside one measurement; only the total is timed.

statement                 number   measured total     verdict
--------------------------------------------------------------
x = 1                          1       under 1 ms   too short
x = 1                   10000000      1 ms to 1 s      usable
sum(range(1000))               1       under 1 ms   too short
sum(range(1000))           10000      1 ms to 1 s      usable
sorted(range(10000))         100      1 ms to 1 s      usable

A statement that finishes in tens of nanoseconds cannot be measured
once. The clock is good, but not that good, and everything else
happening on the machine -- the operating system, other processes,
the CPU changing frequency -- is larger than the thing you are
trying to measure. Run it a million times and divide: the noise
averages out because the work does not.

Aim for a measurement that takes at least a tenth of a second. If
it is shorter, raise `number`. timeit will pick one for you if you
let it.

And once you have the repeats, take the *minimum*, not the mean.
Noise on a shared machine only ever adds time -- a run can be slow
because something else was running, but it cannot be faster than
the work itself. So the fastest run is the closest estimate of the
true cost, and the mean is an estimate of the true cost plus
whatever else the machine was doing at the time.
```

The second discipline is harder, and it is the one that catches experienced people: **the number you
compare must be the cost of one run.** `timeit` reports a total, and if you compared two totals produced
with different values of `number`, you have compared your own choices rather than the code.

Here is that mistake, made deliberately, using two string builders:

```python run
import timeit


def plus_equals(n):
    s = ""
    for _ in range(n):
        s += "ab"
    return s


def join_literal_list(n):
    return "".join(["ab"] * n)


def factor(ratio):
    if ratio < 1.3:
        return "about the same"
    if ratio < 3.0:
        return "about 2x"
    if ratio < 5.0:
        return "about 4x"
    if ratio < 15.0:
        return "about 9x"
    return "more than 15x"


N = 2_000
PLUS_RUNS = 3        # <- one number of runs for this builder
JOIN_RUNS = 50       # <- and a completely different one for that builder

totals_plus = min(timeit.repeat(lambda: plus_equals(N), number=PLUS_RUNS, repeat=7))
totals_join = min(timeit.repeat(lambda: join_literal_list(N), number=JOIN_RUNS, repeat=7))

print(f"n = {N}. Two builders, both measured with timeit.")
print()
print("I picked the number of runs so each measurement took about the same")
print("wall-clock time. That is a sensible thing to do, and it is the trap:")
print()
print(f"  s +=        {PLUS_RUNS:>3} runs per measurement")
print(f"  join        {JOIN_RUNS:>3} runs per measurement")
print()
print("Comparing the numbers timeit handed back:")
print(f"  s += is {factor(totals_join / totals_plus)} faster")
print()
print("Comparing the cost of one run -- which is the only fair comparison:")
print(f"  join is {factor((totals_plus / PLUS_RUNS) / (totals_join / JOIN_RUNS))} faster")
print()
print("The same two measurements, and the two readings disagree about which")
print("builder wins. Only the second is a fact about the code. The first is")
print("a fact about my choice of `number`, which is not a property of the")
print("program at all.")
print()
print("Every number in this chapter was produced by dividing a measured")
print("total by the number of runs inside it. Do that division before you")
print("compare anything, and be suspicious of any timing table -- including")
print("one in a book -- where you cannot see what the runs were.")
```

```text
n = 2000. Two builders, both measured with timeit.

I picked the number of runs so each measurement took about the same
wall-clock time. That is a sensible thing to do, and it is the trap:

  s +=          3 runs per measurement
  join         50 runs per measurement

Comparing the numbers timeit handed back:
  s += is about 2x faster

Comparing the cost of one run -- which is the only fair comparison:
  join is about 9x faster

The same two measurements, and the two readings disagree about which
builder wins. Only the second is a fact about the code. The first is
a fact about my choice of `number`, which is not a property of the
program at all.

Every number in this chapter was produced by dividing a measured
total by the number of runs inside it. Do that division before you
compare anything, and be suspicious of any timing table -- including
one in a book -- where you cannot see what the runs were.
```

:::pitfall Reading the ratio off the wrong number
The mistake in that program is not exotic. It is the single most common way a benchmark misleads, and
it does not look like a mistake while you are making it — the code runs, the numbers come out, and the
conclusion is clean and wrong.

Two habits prevent it. First, always divide by the count before you compare. Second, whenever a
benchmark says two things differ by a constant factor, ask what else the timed region did. A
measurement that includes setup, allocation, or I/O is measuring those too, and the ranking it produces
may be a ranking of the setup.
:::

## Where the curves cross

Complexity tells you which way a gap is heading. It does not tell you which side of the gap you are on
right now, and for real inputs that is often the question. So measure both, and find the crossover.

Taking the k smallest of a large list is the cleanest example. A heap of size k costs O(n log k); a full
sort costs O(n log n). Theory says the heap wins, and theory also says the margin shrinks as k grows —
but it does not say where the two meet.

```python run
import heapq
import random
import timeit

N = 100_000
RND = random.Random(7)
DATA = [RND.random() for _ in range(N)]


def per_call(stmt, number, globs):
    """timeit hands back the total for `number` runs. Divide it out."""
    return min(timeit.repeat(stmt, number=number, repeat=5, globals=globs)) / number


def verdict(ratio):
    """ratio is nsmallest / sorted, so below 1 means the heap wins."""
    if ratio < 0.3:
        return "much faster"
    if ratio < 1.0:
        return "faster"
    return "slower"


print(f"take the k smallest of {N:,} numbers")
print()
print("  heapq.nsmallest(k, xs)   keeps a heap of size k  ->  O(n log k)")
print("  sorted(xs)[:k]           sorts everything        ->  O(n log n)")
print()
print(f"{'k':>8}  {'k / n':>8}  {'nsmallest':>14}  {'winner':>10}")
print("-" * 46)
for k in (1, 100, 1_000, 5_000, 10_000, 50_000):
    g = {"xs": DATA, "k": k, "heapq": heapq}
    t_heap = per_call("heapq.nsmallest(k, xs)", 3, g)
    t_sort = per_call("sorted(xs)[:k]", 3, g)
    ratio = t_heap / t_sort
    winner = "nsmallest" if ratio < 1.0 else "sorted"
    print(f"{k:>8}  {k / N:>8.2f}  {verdict(ratio):>14}  {winner:>10}")

print()
print("Both functions return exactly the same list. The only question is")
print("which one you are paying for.")
print()
print("When k is tiny the heap wins by a wide margin. It touches each")
print("element once and only keeps k of them, so its cost is governed by")
print("log k. Sorting has to look at every element and rearrange all of")
print("them, which costs log n per element -- and log n is what it is no")
print("matter how small k gets.")
print()
print("As k grows towards n, log k approaches log n and the growth rates")
print("stop being different. At that point the winner is decided by the")
print("constant factors: sorted is C code running over one contiguous")
print("array, while the heap is a Python loop doing one comparison at a")
print("time. That is why the crossover lands between k = 5000 and")
print("k = 10000 here -- a tenth of the input -- rather than at k = n,")
print("which is where the complexity analysis alone would put it.")
print()
print("So there are two facts and you need both. The growth rate tells you")
print("which way the gap is heading. The constant factor tells you where it")
print("currently is. A table like this one is what you get when you insist")
print("on both instead of arguing about either.")
```

```text
take the k smallest of 100,000 numbers

  heapq.nsmallest(k, xs)   keeps a heap of size k  ->  O(n log k)
  sorted(xs)[:k]           sorts everything        ->  O(n log n)

       k     k / n       nsmallest      winner
----------------------------------------------
       1      0.00     much faster   nsmallest
     100      0.00     much faster   nsmallest
    1000      0.01     much faster   nsmallest
    5000      0.05          faster   nsmallest
   10000      0.10          slower      sorted
   50000      0.50          slower      sorted

Both functions return exactly the same list. The only question is
which one you are paying for.

When k is tiny the heap wins by a wide margin. It touches each
element once and only keeps k of them, so its cost is governed by
log k. Sorting has to look at every element and rearrange all of
them, which costs log n per element -- and log n is what it is no
matter how small k gets.

As k grows towards n, log k approaches log n and the growth rates
stop being different. At that point the winner is decided by the
constant factors: sorted is C code running over one contiguous
array, while the heap is a Python loop doing one comparison at a
time. That is why the crossover lands between k = 5000 and
k = 10000 here -- a tenth of the input -- rather than at k = n,
which is where the complexity analysis alone would put it.

So there are two facts and you need both. The growth rate tells you
which way the gap is heading. The constant factor tells you where it
currently is. A table like this one is what you get when you insist
on both instead of arguing about either.
```

Notice that the crossover is nowhere near where the complexity analysis would put it. Both functions are
asymptotically different, but the heap is written in Python and the sort is written in C, so the heap
starts losing at a tenth of the input rather than at the end of it. A pure asymptotic argument would
have told you the heap always wins; a pure benchmark at k=100 would have told you the heap always wins;
only measuring across the range shows the flip.

:::scenario The dedupe that was fine until it wasn't
A service ingests rows from a partner's export file. Some rows repeat, and the downstream consumer
needs them unique while preserving order. The function that does it has been in production for a year:

```python run
def dedupe(rows):
    out = []
    for row in rows:
        if row not in out:
            out.append(row)
    return out
```

It is correct. It has tests. It preserves order, which a `set(rows)` would not. Nobody has ever
complained about it.

The partner's export grows. Here is the same logic against a set, measured at the sizes involved:

```python run
import timeit


def make_rows(n):
    """n rows, about a tenth of them repeats."""
    return [f"row-{i % (n * 9 // 10)}" for i in range(n)]


def dedupe_by_list(rows):
    """Is this row already in the output? Scan the output to find out."""
    out = []
    for row in rows:
        if row not in out:          # O(len(out)) -- a scan, every time
            out.append(row)
    return out


def dedupe_by_set(rows):
    """The same question, asked of a set instead."""
    seen = set()
    out = []
    for row in rows:
        if row not in seen:         # O(1)
            seen.add(row)
            out.append(row)
    return out


def band(ratio):
    if ratio < 12.0:
        return "~10x"
    if ratio < 45.0:
        return "~25x"
    if ratio < 130.0:
        return "~80x"
    if ratio < 300.0:
        return "~200x"
    return "400x or more"


def per_call(stmt, number, globs):
    return min(timeit.repeat(stmt, number=number, repeat=5, globals=globs)) / number


print("both functions return the same list -- check it once:")
probe = make_rows(2_000)
print("  identical output:", dedupe_by_list(probe) == dedupe_by_set(probe))
print(f"  {len(probe)} rows in, {len(dedupe_by_set(probe))} rows out")
print()
print(f"{'rows':>8}  {'list version / set version':>28}")
print("-" * 40)
for n in (250, 500, 1_000, 2_000, 4_000, 8_000):
    rows = make_rows(n)
    number = max(1, 2_000 // n)
    g = {"f": dedupe_by_list, "rows": rows}
    t_list = per_call("f(rows)", number, g)
    g = {"f": dedupe_by_set, "rows": rows}
    t_set = per_call("f(rows)", number, g)
    print(f"{n:>8}  {band(t_list / t_set):>28}")

print()
print("At 250 rows the list version is already about 25 times slower -- the")
print("kind of thing that gets waved through in review as 'fine for now'.")
print("Every doubling of the input doubles that gap again, because one")
print("version is O(n) and the other is O(n^2). By 8000 rows it is four")
print("hundred times slower, and it has not finished getting worse.")
print()
print("The fix is two lines: keep a set of what you have already seen, and")
print("ask the set instead of scanning the output. The output list stays,")
print("because order matters and a set does not preserve it.")
print()
print("What makes this scenario worth reading is not the fix. It is that")
print("the function was correct, the tests passed, and the only symptom")
print("was a gap that grew. A quadratic is not a bug at any particular")
print("size -- it is a bug waiting for the input to get bigger, which is")
print("to say, waiting for you to ship it.")
```

```text
both functions return the same list -- check it once:
  identical output: True
  2000 rows in, 1800 rows out

    rows    list version / set version
----------------------------------------
     250                          ~25x
     500                          ~25x
    1000                          ~80x
    2000                          ~80x
    4000                         ~200x
    8000                  400x or more

At 250 rows the list version is already about 25 times slower -- the
kind of thing that gets waved through in review as 'fine for now'.
Every doubling of the input doubles that gap again, because one
version is O(n) and the other is O(n^2). By 8000 rows it is four
hundred times slower, and it has not finished getting worse.

The fix is two lines: keep a set of what you have already seen, and
ask the set instead of scanning the output. The output list stays,
because order matters and a set does not preserve it.

What makes this scenario worth reading is not the fix. It is that
the function was correct, the tests passed, and the only symptom
was a gap that grew. A quadratic is not a bug at any particular
size -- it is a bug waiting for the input to get bigger, which is
to say, waiting for you to ship it.
```

The corrected version keeps the output list — because order matters and a set does not preserve it — and
adds a second structure that does not need to preserve anything.
:::

:::solution The fix
```python run
def dedupe(rows):
    """Order-preserving, one pass, O(n)."""
    seen = set()
    out = []
    for row in rows:
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out


print(dedupe(["a", "b", "a", "c", "b", "d"]))
```

```text
['a', 'b', 'c', 'd']
```

Two structures, each doing the job it is good at: the list preserves order, and the set answers the
membership question in constant time. The extra memory is one pointer per unique row.

That is the general shape of the fix for a quadratic that turns out to matter. Find the inner scan, and
ask whether a different structure answers the same question without walking anything. Often it does, and
often it costs a little memory.
:::

You can find a `dedupe` like this in almost any codebase that has been running long enough. It is worth
learning to spot the shape: a loop with a scan inside it, where the scan is over something that grows
as the loop runs.

## Key takeaways

- **Counting and timing answer different questions.** Counting tells you the shape of the cost curve
  and is exact and machine-independent. Timing tells you the height of it and is an estimate.
- **Count first.** A `text`-fence table of step counts is reproducible; a table of microseconds is not,
  and it will not be the same on the reader's machine.
- **The doubling ratio identifies the shape.** 2 is linear, 4 is quadratic, 8 is cubic, and about 1
  means logarithmic. This survives the move from counting to timing, which is what makes it useful.
- **O is an upper bound, Ω is a lower, Θ is both.** "This is O(n²)" is a weak claim — it is also true of
  anything faster. Quote Θ when you mean the rate, and say which case you mean.
- **A single function can have several bounds.** `find` is Ω(1) in the best case and O(n) in the worst.
  The question "what is its complexity?" is incomplete without a case.
- **Every ordinary Python operation is within a factor of six of a local variable read.** That whole
  range is noise compared with a change of complexity class, which is why you fix the curve before you
  tune the constants.
- **`append` is amortised O(1), and the individual append that reallocates is O(n).** Both are true; the
  amortised claim is about a sequence, which is why you measure a sequence to check it.
- **Complexity is a property of the program, not of a line of code.** `x in things` is O(1) for a set and
  O(n) for a list, and the expression looks identical.
- **A benchmark must divide by the number of runs before it compares anything.** Two totals from runs
  with different counts are not comparable, and the conclusion you draw from them will be wrong.
- **Take the minimum of the repeats, not the mean.** Noise only ever adds time, so the fastest run is
  the closest estimate of the true cost.
- **Asymptotics tell you which way a gap is heading; constants tell you where it is.** For real inputs
  you need both, which means measuring across a range and looking for the crossover.
- **A quadratic is not a bug at any particular size.** It is a bug that arrives when the input grows,
  which usually means after you have shipped it.

## Practice

- [ ] Write a function that finds the largest element of a list and counts its comparisons. Show that
      the count is n − 1 at every size, and say why this function is Θ(n) with no best case.
- [ ] Measure `list.pop(0)` against `collections.deque.popleft` for draining n items. Report the
      doubling ratio of each and say which shape each one is.
- [ ] Use the capacity rule to predict how many slots a list has after 10,000 appends, then check it
      with `sys.getsizeof`. Then compare that with `list(range(10_000))` and explain the difference.
- [ ] Compare `min(xs)` with `sorted(xs)[0]` at four sizes. Report the doubling ratio of each and the
      ratio between them, and say which of the two arguments for `min` the timing supports.
- [ ] Measure the amortised cost of `append` by timing n appends and dividing by n, at six values of n.
      Say why measuring a single append would give a misleading answer.

## Solutions

:::solution Exercise 1
```python run
def largest(xs):
    """Return (value, comparisons) for the largest element."""
    best = xs[0]
    comparisons = 0
    for x in xs[1:]:
        comparisons += 1
        if x > best:
            best = x
    return best, comparisons


print(f"{'n':>6}  {'largest':>8}  {'comparisons':>12}  {'n - 1':>6}")
print("-" * 38)
for n in (10, 100, 1_000, 10_000):
    value, comparisons = largest(list(range(n)))
    print(f"{n:>6}  {value:>8}  {comparisons:>12}  {n - 1:>6}")

print()
print("The comparison count is exactly n - 1 at every size, so this")
print("function is Theta(n) with no case to argue about.")
print()
print("That is worth contrasting with find() from earlier in the chapter,")
print("where the answer depended on where the target was. A search can")
print("stop early; a maximum cannot. To know that nothing is bigger than")
print("what you are holding, you have to have looked at everything else.")
print("So the best case and the worst case here are the same, and the")
print("bound is tight in both directions -- which is what Theta means.")
```

```text
     n   largest   comparisons   n - 1
--------------------------------------
    10         9             9       9
   100        99            99      99
  1000       999           999     999
 10000      9999          9999    9999

The comparison count is exactly n - 1 at every size, so this
function is Theta(n) with no case to argue about.

That is worth contrasting with find() from earlier in the chapter,
where the answer depended on where the target was. A search can
stop early; a maximum cannot. To know that nothing is bigger than
what you are holding, you have to have looked at everything else.
So the best case and the worst case here are the same, and the
bound is tight in both directions -- which is what Theta means.
```

The loop starts from `xs[1:]` because the first element is already the running best, so it is not
compared with itself. That is where the `n − 1` comes from rather than `n`.

The contrast with `find` is the point. A search has an early exit, so its cost depends on the input; a
maximum has none, because there is no way to know you have the largest without looking at everything
else. That is what makes this function Θ(n) rather than merely O(n) — the bound is tight from both
sides at once.
:::

:::solution Exercise 2
```python run
import timeit
from collections import deque


def drain_list(n):
    """pop(0) removes the first element and shifts everything left."""
    xs = list(range(n))
    while xs:
        xs.pop(0)


def drain_deque(n):
    """popleft removes the first element and shifts nothing."""
    d = deque(range(n))
    while d:
        d.popleft()


def per_call(fn, n, number=3, repeat=5):
    return min(timeit.repeat(lambda: fn(n), number=number, repeat=repeat)) / number


def growth(ratio):
    if ratio < 1.4:
        return "~1  (constant)"
    if ratio < 3.0:
        return "~2  (linear)"
    if ratio < 6.8:
        return "~4  (quadratic)"
    return "~8  (cubic)"


SIZES = (1_000, 2_000, 4_000, 8_000)
list_times = [per_call(drain_list, n) for n in SIZES]
deque_times = [per_call(drain_deque, n) for n in SIZES]

print("drain n items from the front, two ways")
print()
print(f"{'n':>7}  {'pop(0)':>18}  {'popleft':>18}")
print("-" * 46)
for i, n in enumerate(SIZES):
    if i == 0:
        continue
    print(f"{n:>7}  {growth(list_times[i] / list_times[i - 1]):>18}  "
          f"{growth(deque_times[i] / deque_times[i - 1]):>18}")

print()
print("Both loops remove every element, and both are correct. The left")
print("column is quadratic and the right column is linear, and the reason")
print("is one line of the implementation: a list stores its elements in one")
print("contiguous array, so removing the first one leaves a hole that every")
print("remaining element has to move into. A deque is a ring buffer, so")
print("removing the first element moves a pointer and nothing else.")
print()
print("This is the everyday version of the chapter's argument. `while xs:`")
print("looks the same in both functions; the cost model is entirely")
print("different; and at a thousand items you would not notice. The rule")
print("that falls out of it: if you are removing from the front of a queue,")
print("use a deque. If you are removing from the front of a list, ask")
print("yourself why.")
```

```text
drain n items from the front, two ways

      n              pop(0)             popleft
----------------------------------------------
   2000     ~4  (quadratic)        ~2  (linear)
   4000     ~4  (quadratic)        ~2  (linear)
   8000     ~4  (quadratic)        ~2  (linear)

Both loops remove every element, and both are correct. The left
column is quadratic and the right column is linear, and the reason
is one line of the implementation: a list stores its elements in one
contiguous array, so removing the first one leaves a hole that every
remaining element has to move into. A deque is a ring buffer, so
removing the first element moves a pointer and nothing else.

This is the everyday version of the chapter's argument. `while xs:`
looks the same in both functions; the cost model is entirely
different; and at a thousand items you would not notice. The rule
that falls out of it: if you are removing from the front of a queue,
use a deque. If you are removing from the front of a list, ask
yourself why.
```

The first row is skipped because at n=500→1000 the O(n) setup still competes with the O(n²) drain, so
the ratio has not settled. That is itself worth noticing: a growth ratio is only informative once the
term you care about dominates.

The fix is a data-structure change, not a micro-optimisation. `deque` is a ring buffer — a fixed array
with a head pointer — so removing from the front advances the pointer instead of shifting anything.
:::

:::solution Exercise 3
```python run
import sys

EMPTY = sys.getsizeof([])


def next_capacity(size):
    """CPython's growth rule, from list_resize()."""
    newsize = size + 1
    return (newsize + (newsize >> 3) + 6) & ~3


def predict(length):
    """The capacity a list ends up with after `length` appends."""
    capacity = 0
    size = 0
    for _ in range(length):
        if size == capacity:
            capacity = next_capacity(capacity)
        size += 1
    return capacity


def build(length):
    """Build by appending, one at a time."""
    buf = []
    for _ in range(length):
        buf.append(0)
    return buf


def measured(lst):
    return (sys.getsizeof(lst) - EMPTY) // 8


print("a list built by appending, one element at a time:")
print()
print(f"{'length':>8}  {'predicted':>10}  {'measured':>9}  {'agree':>6}")
print("-" * 38)
for length in (100, 500, 1_000, 2_000, 5_000, 10_000):
    predicted = predict(length)
    actual = measured(build(length))
    print(f"{length:>8}  {predicted:>10}  {actual:>9}  "
          f"{'yes' if predicted == actual else 'NO':>6}")

print()
print("The rule reproduces the real capacity at every size, so you can")
print("answer 'how much memory will this list waste?' without running")
print("anything. A list of 10,000 items does not hold 10,000 slots; it")
print("holds however many the growth rule last asked for, and that is")
print("always a little more.")
print()
print("One more thing worth knowing, because it trips people up when they")
print("try this at home:")
print()
n = 10_000
print(f"  built by appending     {measured(build(n)):>7} slots")
print(f"  built from list(range) {measured(list(range(n))):>7} slots")
print()
print("Both lists have the same length and hold the same values, but they")
print("do not have the same capacity. `list(iterable)` is told the length")
print("in advance, so it allocates exactly the slots it needs and never")
print("overshoots -- which is why it uses less memory than the same list")
print("built by appending, and why the growth rule above does not describe")
print("it. The lesson generalises past lists: the cost of building a")
print("structure depends on how you build it, not only on what it ends up")
print("containing.")
```

```text
a list built by appending, one element at a time:

  length   predicted   measured   agree
--------------------------------------
     100         108        108     yes
     500         520        520     yes
    1000        1100       1100     yes
    2000        2016       2016     yes
    5000        5228       5228     yes
   10000       10640      10640     yes

The rule reproduces the real capacity at every size, so you can
answer 'how much memory will this list waste?' without running
anything. A list of 10,000 items does not hold 10,000 slots; it
holds however many the growth rule last asked for, and that is
always a little more.

One more thing worth knowing, because it trips people up when they
try this at home:

  built by appending       10640 slots
  built from list(range)   10000 slots

Both lists have the same length and hold the same values, but they
do not have the same capacity. `list(iterable)` is told the length
in advance, so it allocates exactly the slots it needs and never
overshoots -- which is why it uses less memory than the same list
built by appending, and why the growth rule above does not describe
it. The lesson generalises past lists: the cost of building a
structure depends on how you build it, not only on what it ends up
containing.
```

The prediction for 10,000 appends is 10,640 slots — 640 more than the list holds elements, about 6%
wasted. That is the price of amortised O(1) append, and it is worth paying.

The `list(range(n))` comparison is the part that surprises people. Both lists have 10,000 elements and
the same values, and one uses 640 fewer slots. The difference is that `list(iterable)` knows the length
in advance and can allocate exactly once, while appending has to discover the length as it goes. Same
result, different cost — which is the chapter's recurring theme.
:::

:::solution Exercise 4
```python run
import math
import random
import timeit

RND = random.Random(11)
DATA = [RND.random() for _ in range(200_000)]


def per_call(stmt, number, globs):
    return min(timeit.repeat(stmt, number=number, repeat=5, globals=globs)) / number


def growth(ratio):
    if ratio < 1.4:
        return "~1  (constant)"
    if ratio < 3.0:
        return "~2  (linear)"
    if ratio < 6.8:
        return "~4  (quadratic)"
    return "~8  (cubic)"


def factor(ratio):
    if ratio < 1.5:
        return "about the same"
    if ratio < 3.0:
        return "~2x"
    if ratio < 7.0:
        return "~5x"
    if ratio < 15.0:
        return "~10x"
    return "15x or more"


print("the smallest of n numbers, two ways")
print()
print(f"{'n':>8}  {'min(xs)':>18}  {'sorted(xs)[0]':>18}")
print("-" * 48)
previous = {}
last_ratio = 1.0
for n in (25_000, 50_000, 100_000, 200_000):
    xs = DATA[:n]
    g = {"xs": xs}
    t_min = per_call("min(xs)", 20, g)
    t_sort = per_call("sorted(xs)[0]", 3, g)
    last_ratio = t_sort / t_min
    if previous:
        print(f"{n:>8}  {growth(t_min / previous['min']):>18}  "
              f"{growth(t_sort / previous['sort']):>18}")
    previous = {"min": t_min, "sort": t_sort}

print()
print(f"and at the largest size, sorted takes {factor(last_ratio)} what min takes")
print()
print("Both growth columns read about 2, and that is the honest result: at")
print("any size you can conveniently measure, n and n log n are not")
print("distinguishable by timing. The difference is real -- log n goes from")
print("17 to 18 between the last two rows -- but it lands as a few percent")
print("of the ratio, which is smaller than the noise in the clock.")
print()
print("So the argument for min does not come from that table. It comes")
print("from counting:")
print()
print(f"{'n':>8}  {'min: n - 1':>12}  {'sorted: n log n':>16}")
print("-" * 40)
for n in (25_000, 50_000, 100_000, 200_000):
    print(f"{n:>8}  {n - 1:>12}  {round(n * math.log2(n)):>16}")

print()
print("Those numbers are exact, and they say what the clock could not: the")
print("gap between the two approaches widens as n grows, without limit.")
print()
print("The practical rule is still the simple one. If you want the minimum,")
print("ask for the minimum -- `min`, not `sorted(...)[0]`. The complexity")
print("argument makes it right at scale, the readability argument makes it")
print("right immediately, and this exercise is a reminder that the")
print("complexity argument had to be made by counting, because the")
print("stopwatch was never going to make it.")
```

```text
the smallest of n numbers, two ways

       n             min(xs)       sorted(xs)[0]
------------------------------------------------
   50000        ~2  (linear)        ~2  (linear)
  100000        ~2  (linear)        ~2  (linear)
  200000        ~2  (linear)        ~2  (linear)

and at the largest size, sorted takes 15x or more what min takes

Both growth columns read about 2, and that is the honest result: at
any size you can conveniently measure, n and n log n are not
distinguishable by timing. The difference is real -- log n goes from
17 to 18 between the last two rows -- but it lands as a few percent
of the ratio, which is smaller than the noise in the clock.

So the argument for min does not come from that table. It comes
from counting:

       n    min: n - 1   sorted: n log n
----------------------------------------
   25000         24999            365241
   50000         49999            780482
  100000         99999           1660964
  200000        199999           3521928

Those numbers are exact, and they say what the clock could not: the
gap between the two approaches widens as n grows, without limit.

The practical rule is still the simple one. If you want the minimum,
ask for the minimum -- `min`, not `sorted(...)[0]`. The complexity
argument makes it right at scale, the readability argument makes it
right immediately, and this exercise is a reminder that the
complexity argument had to be made by counting, because the
stopwatch was never going to make it.
```

This is the exercise where the honest answer is more interesting than the expected one. The timing table
does not separate the two functions, because n and n log n are simply too close to tell apart at these
sizes. What the timing *does* show is the constant factor: `sorted` is more than fifteen times slower
right now, because it does far more work per element.

The counting table is what settles the argument. At n = 200,000, `min` performs 199,999 comparisons and
`sorted` performs about 3.5 million, and that gap grows by roughly a factor of 2.1 for every doubling
while the comparison counts grow by 2 and 2.1 respectively. Over enough doublings it becomes an order of
magnitude, then two.

So the answer to "which argument does the timing support?" is: the constant-factor argument, at this
size. The complexity argument is real but it needs counting to be visible — which is exactly the lesson
from the `n` versus `n log n` row in the earlier table.
:::

:::solution Exercise 5
```python run
import timeit


def build(n):
    a = []
    for i in range(n):
        a.append(i)
    return a


def per_append(n):
    """Total time for n appends, divided by n."""
    number = max(1, 400_000 // n)
    total = min(timeit.repeat(lambda: build(n), number=number, repeat=5)) / number
    return total / n


def growth(ratio):
    if ratio < 1.4:
        return "flat"
    if ratio < 1.8:
        return "slightly up"
    return "rising"


SIZES = (10_000, 20_000, 40_000, 80_000, 160_000, 320_000)

print("cost of one append, as the list gets longer")
print()
print(f"{'n':>8}  {'vs previous':>13}")
print("-" * 24)
previous = None
for n in SIZES:
    cost = per_append(n)
    if previous is None:
        print(f"{n:>8}  {'--':>13}")
    else:
        print(f"{n:>8}  {growth(cost / previous):>13}")
    previous = cost

print()
print("Every row says 'flat', which is the amortised O(1) claim measured")
print("rather than asserted. Doubling the length of the list does not")
print("double the cost of the next append.")
print()
print("What makes this worth running yourself is that the claim is easy to")
print("doubt. You know from the previous program that a reallocation copies")
print("every element, and that some appends therefore cost O(n). If you")
print("measured a single append you might catch a reallocation and conclude")
print("that append is O(n) -- which would be a true statement about that")
print("one append and a useless statement about the loop.")
print()
print("So the measurement has to match the claim. The claim is about a")
print("sequence of n appends, so the measurement is the total for n appends")
print("divided by n. If you ever find yourself measuring one operation to")
print("test a claim about a sequence, that mismatch is the bug -- not the")
print("result.")
```

```text
cost of one append, as the list gets longer

       n    vs previous
------------------------
   10000             --
   20000           flat
   40000           flat
   80000           flat
  160000           flat
  320000           flat

Every row says 'flat', which is the amortised O(1) claim measured
rather than asserted. Doubling the length of the list does not
double the cost of the next append.

What makes this worth running yourself is that the claim is easy to
doubt. You know from the previous program that a reallocation copies
every element, and that some appends therefore cost O(n). If you
measured a single append you might catch a reallocation and conclude
that append is O(n) -- which would be a true statement about that
one append and a useless statement about the loop.

So the measurement has to match the claim. The claim is about a
sequence of n appends, so the measurement is the total for n appends
divided by n. If you ever find yourself measuring one operation to
test a claim about a sequence, that mismatch is the bug -- not the
result.
```

Timing a single `append` is unreliable for a second reason beyond the amortisation issue: a single call
finishes in tens of nanoseconds, which is inside the noise floor of the clock. You would be measuring
the timer.

The right measurement follows from the claim. "Amortised O(1)" is a statement about a sequence of n
appends, so the measurement is the total for n appends divided by n. When the claim and the measurement
are about the same thing, the result is boring and trustworthy — which is what a correct measurement of
a correct claim should look like.
:::
