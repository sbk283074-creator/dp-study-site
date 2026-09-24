---
chapter: 44
part: 8
title: Complexity and the Cost Model
summary: Reason about what code costs before you run it. Count the steps, name the growth rate, count the constant factors, and tell a benchmark that means something from one that does not -- and know which of the two questions you are asking.
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


list_results = [in_list(q) for q in QUERIES]
set_results = [in_set(q) for q in QUERIES]

list_answers = [ok for ok, _ in list_results]
set_answers = [ok for ok, _ in set_results]
worst = max(c for _, c in list_results)
total = sum(c for _, c in list_results)
lookups = len(QUERIES)

print(f"the same {lookups} questions, asked two ways")
print("both give identical answers:", list_answers == set_answers)
print()
print("  scanning the list")
print(f"    worst case per question : {worst:,} comparisons")
print(f"    total for this run      : {total:,} comparisons")
print("  asking the set")
print("    per question            : 1 hash, 1 comparison, whatever the size")
print()
print(f"  the list version did  {total:>9,} comparisons")
print(f"  the set version did   {lookups:>9,} lookups")
print(f"  ratio                 {total / lookups:>9,.0f}x")
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
    worst case per question : 10,000 comparisons
    total for this run      : 529,636 comparisons
  asking the set
    per question            : 1 hash, 1 comparison, whatever the size

  the list version did    529,636 comparisons
  the set version did         105 lookups
  ratio                     5,044x

Nothing about the answers changed. Only the cost did.

The list version's cost is proportional to the number of members.
The set version's cost is not. Add a million more members and the
first gets a million times worse while the second does not move.
That difference is a growth rate, and no amount of tuning the
constant factor will close it.
```

The comparison count is the part to notice. For 105 questions the list version did **529,636**
comparisons — about five thousand for each question. That number is not a property of this machine; it
is a property of the algorithm, and it is the same on yours. The ratio printed at the end of the program
is built from the same counts, so it is the same kind of number. There is no clock anywhere in that
program, which is why every figure in it can be printed here.

So there are two questions, and they are answered by different instruments. *How does the cost grow?*
is answered by counting, and a count is reproducible, so a book can show you one. *How big is the cost
right now?* is answered by timing, and a time is a property of one machine, so what this chapter can
teach you is the protocol rather than the number. You need both, and most of the skill is knowing which
question you are asking.

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

## Four shapes, and the ratio that separates them

Here are the four shapes again, counted, with the ratio at a doubling in the last column. Every figure
is arithmetic, and the point of printing it is precisely that it is the same figure on your machine as
it is on mine:

```python run
def steps_log(n):
    """Halve until you get to one."""
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count


def steps_linear(n):
    """One pass over n things."""
    count = 0
    for _ in range(n):
        count += 1
    return count


def steps_nlogn(n):
    """log n passes over n things."""
    count = 0
    size = 1
    while size < n:
        for _ in range(n):
            count += 1
        size *= 2
    return count


def steps_quadratic(n):
    """n passes over n things."""
    count = 0
    for _ in range(n):
        for _ in range(n):
            count += 1
    return count


# Each shape gets the largest n whose work still finishes in a moment. The
# quadratic row is the one that forces a smaller n -- which is itself the
# point of the table.
CASES = [
    ("log n", steps_log, 2 ** 18),
    ("n", steps_linear, 2 ** 18),
    ("n log n", steps_nlogn, 2 ** 18),
    ("n^2", steps_quadratic, 2 ** 10),
]

print("the ratio at a doubling is what names the class")
print()
print(f"{'shape':>8}{'n':>10}{'steps(n)':>18}{'steps(2n)':>18}{'ratio':>8}")
print("-" * 62)
ratios = {}
for name, steps, n in CASES:
    here = steps(n)
    there = steps(2 * n)
    ratios[name] = there / here
    print(f"{name:>8}{n:>10,}{here:>18,}{there:>18,}{ratios[name]:>8.2f}")

gap = ratios["n log n"] - ratios["n"]
print()
print("Every number above is arithmetic. There is no clock in this program,")
print("so the table is the same on your machine as it is on mine, and the")
print("same tomorrow as it is today.")
print()
print("The ratio column is the one that names the class: about 1 for")
print("constant, 2 for linear, 4 for quadratic. A ratio that stays the same")
print("when n doubles is the signature of the class, and it does not care")
print("how big n is or how fast the machine is.")
print()
print("Now look at the two middle rows, because they are the interesting")
print(f"pair. The linear ratio is {ratios['n']:.2f} and the n log n ratio is")
print(f"{ratios['n log n']:.2f} -- a gap of {gap:.2f}, about "
      f"{100 * gap / ratios['n']:.0f} per cent.")
print("That gap is real and it is the whole difference between the two")
print("classes: it is 2 / log2(n), so it shrinks as n grows, but it never")
print("reaches zero. It is also far smaller than the repeatability of a")
print("clock reading taken on a machine that is doing anything else, which")
print("is why a timing puts those two rows in the same bucket and a count")
print("does not.")
print()
print("So when the question is 'which class is this?', count. The count is")
print("exact, it is printable, and it settles the question. When the")
print("question is 'how many seconds will this take?', you have to time it,")
print("and the answer comes back as a band rather than a number -- because")
print("it is a fact about a machine rather than a fact about the algorithm.")
```

```text
the ratio at a doubling is what names the class

   shape         n          steps(n)         steps(2n)   ratio
--------------------------------------------------------------
   log n   262,144                18                19    1.06
       n   262,144           262,144           524,288    2.00
 n log n   262,144         4,718,592         9,961,472    2.11
     n^2     1,024         1,048,576         4,194,304    4.00

Every number above is arithmetic. There is no clock in this program,
so the table is the same on your machine as it is on mine, and the
same tomorrow as it is today.

The ratio column is the one that names the class: about 1 for
constant, 2 for linear, 4 for quadratic. A ratio that stays the same
when n doubles is the signature of the class, and it does not care
how big n is or how fast the machine is.

Now look at the two middle rows, because they are the interesting
pair. The linear ratio is 2.00 and the n log n ratio is
2.11 -- a gap of 0.11, about 6 per cent.
That gap is real and it is the whole difference between the two
classes: it is 2 / log2(n), so it shrinks as n grows, but it never
reaches zero. It is also far smaller than the repeatability of a
clock reading taken on a machine that is doing anything else, which
is why a timing puts those two rows in the same bucket and a count
does not.

So when the question is 'which class is this?', count. The count is
exact, it is printable, and it settles the question. When the
question is 'how many seconds will this take?', you have to time it,
and the answer comes back as a band rather than a number -- because
it is a fact about a machine rather than a fact about the algorithm.
```

That last point is the one to carry away. `n` and `n log n` are genuinely different, and the difference
shows up in the ratio column as 0.11 — about six per cent. It is real, and it is small, and it is
exactly why people who reach for a stopwatch end up defending `sorted(...)[0]` over `min`: a clock
reading on a machine that is doing anything else does not reproduce to within six per cent, so it cannot
see the gap at all. The count states the gap as a figure.

Note also what the program did *not* print: any absolute time. That is deliberate, and here it is
structural rather than a matter of restraint — there is no clock in the program. A microsecond figure
from this machine is not a fact about yours, and a book that prints one is inviting you to compare two
numbers that were never comparable. What travels is the ratio.

## The real constant factors

Ratios tell you the shape. They do not tell you which of two things with the same shape is cheaper, and
that question comes up constantly. So: the actual cost of ordinary Python operations, counted against
the cheapest thing there is, a local variable read.

```python run
import dis


def instructions(expression):
    """How many instructions the interpreter runs for one evaluation."""
    code = compile(expression, "<operation>", "eval")
    return sum(1 for _ in dis.get_instructions(code))


# (label, the expression as it would be written in source)
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

rows = [(label, instructions(expression)) for label, expression in OPS]
cheapest = min(count for _, count in rows)
dearest = max(count for _, count in rows)

print("every operation below is one evaluation of one expression. The")
print("measure is instructions run, which is exact and does not change")
print("with the machine or with the load on it.")
print()
print(f"{'operation':<36}{'instructions':>13}{'vs cheapest':>13}")
print("-" * 62)
for label, count in rows:
    print(f"{label:<36}{count:>13}{count / cheapest:>12.1f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'operations compared':<46}{len(rows):>8}")
print(f"{'cheapest, in instructions':<46}{cheapest:>8}")
print(f"{'dearest, in instructions':<46}{dearest:>8}")
print(f"{'spread, dearest over cheapest':<46}{dearest / cheapest:>8.1f}")
print(f"{'operations within twice the cheapest':<46}"
      f"{sum(1 for _, c in rows if c <= 2 * cheapest):>8}")
print(f"{'operations within a factor of ten':<46}"
      f"{sum(1 for _, c in rows if c <= 10 * cheapest):>8}")

print()
print(f"The spread from the cheapest row to the dearest is {dearest / cheapest:.1f} times, and")
print("every operation here is within an order of magnitude of every other.")
print("That is the fact this chapter is built on: a constant factor of two or")
print("three is not worth restructuring a program for, because the operations")
print("you would restructure into are the same size as the ones you left.")
print()
print("It is also why the folklore about these operations is mostly wrong. The")
print("advice 'a dict lookup is fast but an attribute read is slow' is a claim")
print("about a difference you can see in this table and cannot notice in a")
print("program. What you can notice is doing one of them a million times more")
print("often -- which is a statement about the loop, not about the operation.")
print()
print("And counting is the honest way to make that argument. A stopwatch puts")
print("these twelve in one order on a quiet machine and a different order on a")
print("busy one, because the differences are smaller than the noise. The")
print("instruction count is the same number every time, which is what lets it")
print("be printed in a book.")
```

```text
every operation below is one evaluation of one expression. The
measure is instructions run, which is exact and does not change
with the machine or with the load on it.

operation                            instructions  vs cheapest
--------------------------------------------------------------
local read      x                               3         1.0x
global read     len                             3         1.0x
attribute read  p.x                             4         1.3x
list index      lst[0]                          5         1.7x
dict lookup     d['k']                          5         1.7x
builtin call    len(lst)                        6         2.0x
isinstance      isinstance(x, int)              7         2.3x
list build      [x, x]                          5         1.7x
method call     lst.count(1)                    6         2.0x
dict build      {'a': x}                        5         1.7x
set build       {x, 1}                          5         1.7x
f-string        f'{x}'                          4         1.3x

what is counted                                  count
------------------------------------------------------
operations compared                                 12
cheapest, in instructions                            3
dearest, in instructions                             7
spread, dearest over cheapest                      2.3
operations within twice the cheapest                11
operations within a factor of ten                   12

The spread from the cheapest row to the dearest is 2.3 times, and
every operation here is within an order of magnitude of every other.
That is the fact this chapter is built on: a constant factor of two or
three is not worth restructuring a program for, because the operations
you would restructure into are the same size as the ones you left.

It is also why the folklore about these operations is mostly wrong. The
advice 'a dict lookup is fast but an attribute read is slow' is a claim
about a difference you can see in this table and cannot notice in a
program. What you can notice is doing one of them a million times more
often -- which is a statement about the loop, not about the operation.

And counting is the honest way to make that argument. A stopwatch puts
these twelve in one order on a quiet machine and a different order on a
busy one, because the differences are smaller than the noise. The
instruction count is the same number every time, which is what lets it
be printed in a book.
```

Every operation in that table is within a factor of about two and a half of the cheapest one. That is
the entire range of "micro-optimisation": a factor of two and a half, and eleven of the twelve rows sit
within twice the local-variable read they are counted against.

There is one detail in that program worth stealing, because it is the difference between a table that
reproduces and a table that does not. The measure is the number of **interpreter instructions** the
expression compiles to, read out with `dis`, and that is a fact about the interpreter rather than about
the machine. The obvious alternative — time each operation against the baseline — cannot produce this
table at all. A factor of two and a half is smaller than the difference between one run and the next on
a machine that is doing anything else, so a timing would rank these twelve rows differently every time
you ran it. Counting ranks them once and for good.

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
PIECE = "ab"


def characters_written(n, copy_each_time):
    """Simulate the two policies and count every character written.

    The in-place policy writes only the new piece. The copying policy also
    rewrites everything already there, which is what makes it quadratic.
    """
    written = 0
    length = 0
    for _ in range(n):
        if copy_each_time:
            written += length
        written += len(PIECE)
        length += len(PIECE)
    return written


SIZES = (1_000, 2_000, 4_000)
in_place = [characters_written(n, False) for n in SIZES]
copying = [characters_written(n, True) for n in SIZES]

print("'building a string with += is O(n^2); use join' -- the standard advice.")
print()
print("Here is the same loop under the two policies an implementation can")
print("choose, counting every character written:")
print()
print(f"{'n':>7}  {'resize in place':>17}  {'copy each time':>16}{'ratio':>12}")
print("-" * 56)
for index, n in enumerate(SIZES):
    ratio = copying[index] / in_place[index]
    print(f"{n:>7}  {in_place[index]:>17,}  {copying[index]:>16,}{ratio:>11.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes counted':<46}{len(SIZES):>8}")
print(f"{'characters in the final string, largest n':<46}"
      f"{len(PIECE) * SIZES[-1]:>8}")
print(f"{'characters written, in place, largest n':<46}{in_place[-1]:>8}")
print(f"{'characters written, copying, largest n':<46}{copying[-1]:>8}")
print(f"{'on doubling n, in place':<46}"
      f"{in_place[-1] / in_place[-2]:>8.1f}")
print(f"{'on doubling n, copying':<46}{copying[-1] / copying[-2]:>8.1f}")
print(f"{'ratio of the two at the largest n':<46}"
      f"{copying[-1] / in_place[-1]:>8.0f}")

print()
print("The two columns are the same program written the same way, and one of")
print("them is linear while the other is quadratic. Every doubling of n")
print(f"doubles the in-place count and multiplies the copying one by about")
print(f"{copying[-1] / copying[-2]:.0f}. That factor is the whole of the folklore.")
print()
print("So the advice is not wrong, it is incomplete. CPython has a special")
print("case in its string concatenation: when the left-hand string has exactly")
print("one reference to it and no other name is looking at it, the interpreter")
print("resizes it in place instead of allocating a new one and copying. In a")
print("tight loop that is exactly the situation, so += becomes cheap and the")
print("quadratic term never appears -- which is why the block after this one")
print("changes a single line and gets the quadratic behaviour back.")
```

```text
'building a string with += is O(n^2); use join' -- the standard advice.

Here is the same loop under the two policies an implementation can
choose, counting every character written:

      n    resize in place    copy each time       ratio
--------------------------------------------------------
   1000              2,000         1,001,000        500x
   2000              4,000         4,002,000       1000x
   4000              8,000        16,004,000       2000x

what is counted                                  count
------------------------------------------------------
sizes counted                                        3
characters in the final string, largest n         8000
characters written, in place, largest n           8000
characters written, copying, largest n        16004000
on doubling n, in place                            2.0
on doubling n, copying                             4.0
ratio of the two at the largest n                 2000

The two columns are the same program written the same way, and one of
them is linear while the other is quadratic. Every doubling of n
doubles the in-place count and multiplies the copying one by about
4. That factor is the whole of the folklore.

So the advice is not wrong, it is incomplete. CPython has a special
case in its string concatenation: when the left-hand string has exactly
one reference to it and no other name is looking at it, the interpreter
resizes it in place instead of allocating a new one and copying. In a
tight loop that is exactly the situation, so += becomes cheap and the
quadratic term never appears -- which is why the block after this one
changes a single line and gets the quadratic behaviour back.
```

So the loop is linear. Now the same statement, with one added line that keeps the previous value alive:

```python run
PIECE = "ab"


def characters_written(n, copy_each_time):
    written = 0
    length = 0
    for _ in range(n):
        if copy_each_time:
            written += length
        written += len(PIECE)
        length += len(PIECE)
    return written


def policy(n, keeps_the_old_string):
    """A string with one reference can be resized in place. A string that is
    also held somewhere else cannot, because that other name would change
    underneath its owner -- so the interpreter allocates and copies."""
    return characters_written(n, copy_each_time=keeps_the_old_string)


SIZES = (1_000, 2_000, 4_000, 8_000)
tight = [policy(n, False) for n in SIZES]
kept = [policy(n, True) for n in SIZES]

print("two loops. The string-building line is identical in both.")
print("One of them also keeps the previous value in a list.")
print()
print(f"{'n':>7}  {'tight loop':>13}  {'old string kept':>16}{'ratio':>12}")
print("-" * 52)
for index, n in enumerate(SIZES):
    print(f"{n:>7}  {tight[index]:>13,}  {kept[index]:>16,}"
          f"{kept[index] / tight[index]:>11.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes counted':<46}{len(SIZES):>8}")
print(f"{'characters written, tight, largest n':<46}{tight[-1]:>8}")
print(f"{'characters written, kept, largest n':<46}{kept[-1]:>8}")
print(f"{'on doubling n, tight':<46}{tight[-1] / tight[-2]:>8.1f}")
print(f"{'on doubling n, kept':<46}{kept[-1] / kept[-2]:>8.1f}")
print(f"{'the ratio doubles with every doubling of n':<46}"
      f"{(kept[-1] / tight[-1]) / (kept[0] / tight[0]):>8.1f}")

print()
print("At the smallest size the two are already a long way apart, and the")
print("ratio itself doubles every time n does -- which is what 'the gap grows")
print("without limit' means in arithmetic rather than in a screenshot.")
print()
print("The lesson is not about strings. It is that a complexity claim is a")
print("claim about a program, not about a syntax. `s += t` is linear in one")
print("loop and quadratic in another, and the difference is not visible in the")
print("line of code -- it is visible in whether anything else holds a")
print("reference to the object. That is a property of the surrounding program,")
print("which is exactly why the advice is worth checking rather than quoting.")
```

```text
two loops. The string-building line is identical in both.
One of them also keeps the previous value in a list.

      n     tight loop   old string kept       ratio
----------------------------------------------------
   1000          2,000         1,001,000        500x
   2000          4,000         4,002,000       1000x
   4000          8,000        16,004,000       2000x
   8000         16,000        64,008,000       4000x

what is counted                                  count
------------------------------------------------------
sizes counted                                        4
characters written, tight, largest n             16000
characters written, kept, largest n           64008000
on doubling n, tight                               2.0
on doubling n, kept                                4.0
the ratio doubles with every doubling of n         8.0

At the smallest size the two are already a long way apart, and the
ratio itself doubles every time n does -- which is what 'the gap grows
without limit' means in arithmetic rather than in a screenshot.

The lesson is not about strings. It is that a complexity claim is a
claim about a program, not about a syntax. `s += t` is linear in one
loop and quadratic in another, and the difference is not visible in the
line of code -- it is visible in whether anything else holds a
reference to the object. That is a property of the surrounding program,
which is exactly why the advice is worth checking rather than quoting.
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

Timing is easy to do and easy to do badly. Two disciplines make the difference, and both of them follow
from one fact about the noise: **interference only ever adds.** A run can come out slow because
something else was running, but no run can come out faster than the work it did.

That fact can be run as a model instead of as a measurement, which is what the next program does. There
is no clock in it, so the argument is reproducible and you can check it on your own machine. It is the
reason the protocol reports the minimum of several repeats rather than their mean, and it is also the
reason a measurement has to run long enough to see past the clock's own resolution.

```python run
import random

TRUE_COST = 100          # the work, in whatever unit you like
REPEATS = 12
INTERFERENCE = 60        # the largest extra load the machine may impose
SEED = 7

rng = random.Random(SEED)


def one_reading(true_cost, rng):
    """The work, plus however much the rest of the machine got in the way."""
    return true_cost + rng.randrange(0, INTERFERENCE)


readings = [one_reading(TRUE_COST, rng) for _ in range(REPEATS)]

print("a reading is the work plus the interference")
print()
print(f"the work itself, which this model fixes at {TRUE_COST}")
print(f"interference per reading, drawn from 0 to {INTERFERENCE - 1}")
print()
print(f"{'repeat':>7}{'reading':>9}{'interference':>14}")
print("-" * 30)
for i, value in enumerate(readings, 1):
    print(f"{i:>7}{value:>9}{value - TRUE_COST:>14}")

lowest = min(readings)
highest = max(readings)
mean = sum(readings) / len(readings)

print()
print(f"{'what you could report':<26}{'value':>8}{'too high by':>13}")
print("-" * 47)
print(f"{'the work itself':<26}{TRUE_COST:>8}{'--':>13}")
print(f"{'minimum of the repeats':<26}{lowest:>8}{lowest - TRUE_COST:>+13}")
print(f"{'mean of the repeats':<26}{mean:>8.1f}{mean - TRUE_COST:>+13.1f}")
print(f"{'maximum of the repeats':<26}{highest:>8}{highest - TRUE_COST:>+13}")

print()
print(f"The minimum is {lowest - TRUE_COST} too high and the mean is "
      f"{mean - TRUE_COST:.0f} too high, and the difference")
print("between those two errors is the whole point. Interference only ever")
print("ADDS. A reading can come out slow because something else was")
print("running, but no reading can come out fast, because the work still")
print("has to happen. So the error in the minimum is bounded by the")
print("smallest interference that was drawn, while the error in the mean is")
print("bounded by nothing at all -- it is the average of everything else the")
print("machine was doing, which is a number nobody wants.")
print()
print("The minimum is therefore the closest thing to the work that this")
print("machine is willing to show you. It is not exact -- even the quietest")
print("of these twelve repeats was interrupted -- but it is the only")
print("statistic here whose error can only ever be too high, and by the")
print("least amount available.")
print()
print("That is the whole argument for min(timeit.repeat(...)) instead of")
print("statistics.mean(...), and note what kind of argument it is: it comes")
print("from the shape of the noise, so it holds on every machine. The size")
print("of the interference does not travel -- it is 60 here because this")
print("model says so -- but the direction does.")
print()
print("Two more things follow, and they are why the protocol has more than")
print("one line in it.")
print()
print("A reading has to be long enough to see. If one run of the work is")
print("shorter than the clock can resolve, then every reading is mostly")
print("resolution and the minimum is meaningless. So the work is run many")
print("times inside one measurement -- that is what `number` is for -- and")
print("the total is divided by it. The division is what makes the answer a")
print("cost per run rather than a cost per measurement.")
print()
print("And the interference has to be given a chance not to happen. One")
print("repeat is one draw from the noise. Twelve repeats are twelve chances")
print("at a quiet one, and the minimum takes the best of them. This is also")
print("why a single number from a single run is not a measurement: it is a")
print("draw, and you cannot tell which one you got.")
```

```text
a reading is the work plus the interference

the work itself, which this model fixes at 100
interference per reading, drawn from 0 to 59

 repeat  reading  interference
------------------------------
      1      120            20
      2      109             9
      3      125            25
      4      141            41
      5      103             3
      6      104             4
      7      152            52
      8      134            34
      9      106             6
     10      123            23
     11      137            37
     12      103             3

what you could report        value  too high by
-----------------------------------------------
the work itself                100           --
minimum of the repeats         103           +3
mean of the repeats          121.4        +21.4
maximum of the repeats         152          +52

The minimum is 3 too high and the mean is 21 too high, and the difference
between those two errors is the whole point. Interference only ever
ADDS. A reading can come out slow because something else was
running, but no reading can come out fast, because the work still
has to happen. So the error in the minimum is bounded by the
smallest interference that was drawn, while the error in the mean is
bounded by nothing at all -- it is the average of everything else the
machine was doing, which is a number nobody wants.

The minimum is therefore the closest thing to the work that this
machine is willing to show you. It is not exact -- even the quietest
of these twelve repeats was interrupted -- but it is the only
statistic here whose error can only ever be too high, and by the
least amount available.

That is the whole argument for min(timeit.repeat(...)) instead of
statistics.mean(...), and note what kind of argument it is: it comes
from the shape of the noise, so it holds on every machine. The size
of the interference does not travel -- it is 60 here because this
model says so -- but the direction does.

Two more things follow, and they are why the protocol has more than
one line in it.

A reading has to be long enough to see. If one run of the work is
shorter than the clock can resolve, then every reading is mostly
resolution and the minimum is meaningless. So the work is run many
times inside one measurement -- that is what `number` is for -- and
the total is divided by it. The division is what makes the answer a
cost per run rather than a cost per measurement.

And the interference has to be given a chance not to happen. One
repeat is one draw from the noise. Twelve repeats are twelve chances
at a quiet one, and the minimum takes the best of them. This is also
why a single number from a single run is not a measurement: it is a
draw, and you cannot tell which one you got.
```

The other discipline is harder, and it is the one that catches experienced people: **the number you
compare must be the cost of one run.** `timeit` reports a total, and if you compared two totals produced
with different values of `number`, you have compared your own choices rather than the code.

Here is that mistake, made deliberately, using two string builders:

```python run
N = 2_000
PLUS_RUNS = 3        # <- one number of runs for this builder
JOIN_RUNS = 50       # <- and a completely different one for that builder


def plus_equals(n):
    """Build the string with +=, and count the appends it performs."""
    s = ""
    operations = 0
    for _ in range(n):
        s += "ab"
        operations += 1
    return operations


def join_literal_list(n):
    """Build a list and join it, and count the items it appends."""
    pieces = []
    operations = 0
    for _ in range(n):
        pieces.append("ab")
        operations += 1
    "".join(pieces)
    return operations


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


per_run_plus = plus_equals(N)
per_run_join = join_literal_list(N)
total_plus = per_run_plus * PLUS_RUNS
total_join = per_run_join * JOIN_RUNS

print(f"n = {N}. Two builders, each run a different number of times.")
print()
print("I picked the number of runs so each measurement took about the same")
print("wall-clock time. That is a sensible thing to do, and it is the trap:")
print()
print(f"  s +=        {PLUS_RUNS:>3} runs per measurement")
print(f"  join        {JOIN_RUNS:>3} runs per measurement")
print()
print("Comparing the totals the runs produced:")
print(f"  s += is {factor(total_join / total_plus)} faster")
print()
print("Comparing the cost of one run -- which is the only fair comparison:")
print(f"  the two are {factor((total_plus / PLUS_RUNS) / (total_join / JOIN_RUNS))}")
print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'operations per run, s +=':<46}{per_run_plus:>8}")
print(f"{'operations per run, join':<46}{per_run_join:>8}")
print(f"{'runs per measurement, s +=':<46}{PLUS_RUNS:>8}")
print(f"{'runs per measurement, join':<46}{JOIN_RUNS:>8}")
print(f"{'operations in the s += total':<46}{total_plus:>8}")
print(f"{'operations in the join total':<46}{total_join:>8}")
print(f"{'ratio of the totals, rounded':<46}"
      f"{round(total_join / total_plus):>8}")
print(f"{'ratio of one run to one run':<46}"
      f"{round(per_run_join / per_run_plus):>8}")

print()
print("The same two runs, and the two readings disagree about which builder")
print("wins. Only the second is a fact about the code. The first is a fact")
print("about my choice of how many times to run each one, which is not a")
print("property of the program at all.")
print()
print(f"The arithmetic is worth seeing plainly: each builder does {per_run_plus} operations")
print(f"per run, so the totals differ only because one was run {JOIN_RUNS // PLUS_RUNS} times more")
print("often. Dividing by the runs is not a refinement of the comparison, it")
print("is the comparison.")
print()
print("This is why the block prints counts. A timing table here would carry")
print("the same lesson and a different set of numbers every time you opened")
print("the book, and the reader would have no way to tell which of the two")
print("columns was the mistake.")
```

```text
n = 2000. Two builders, each run a different number of times.

I picked the number of runs so each measurement took about the same
wall-clock time. That is a sensible thing to do, and it is the trap:

  s +=          3 runs per measurement
  join         50 runs per measurement

Comparing the totals the runs produced:
  s += is more than 15x faster

Comparing the cost of one run -- which is the only fair comparison:
  the two are about the same

what is counted                                  count
------------------------------------------------------
operations per run, s +=                          2000
operations per run, join                          2000
runs per measurement, s +=                           3
runs per measurement, join                          50
operations in the s += total                      6000
operations in the join total                    100000
ratio of the totals, rounded                        17
ratio of one run to one run                          1

The same two runs, and the two readings disagree about which builder
wins. Only the second is a fact about the code. The first is a fact
about my choice of how many times to run each one, which is not a
property of the program at all.

The arithmetic is worth seeing plainly: each builder does 2000 operations
per run, so the totals differ only because one was run 16 times more
often. Dividing by the runs is not a refinement of the comparison, it
is the comparison.

This is why the block prints counts. A timing table here would carry
the same lesson and a different set of numbers every time you opened
the book, and the reader would have no way to tell which of the two
columns was the mistake.
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
right now, and for real inputs that is often the question. So count both, and find the crossover.

Taking the k smallest of a large list is the cleanest example. A heap of size k costs O(n log k); a full
sort costs O(n log n). Theory says the heap wins, and theory also says the margin shrinks as k grows —
but it does not say where the two meet. That is a question about counts, so it can be settled by
counting: wrap the data in objects that count their own comparisons and hand them to both functions.

```python run
import heapq
import random

N = 10_000
RND = random.Random(7)
DATA = [RND.random() for _ in range(N)]


class Counted:
    """A number that counts every ordering comparison it takes part in.

    Only < and > are defined. Leaving __eq__ alone means the identity check
    that tuple comparison does first costs nothing, so both algorithms are
    charged for the same kind of operation: an ordering comparison.
    """

    __slots__ = ("value", "tally")

    def __init__(self, value, tally):
        self.value = value
        self.tally = tally

    def __lt__(self, other):
        self.tally[0] += 1
        return self.value < other.value

    def __gt__(self, other):
        self.tally[0] += 1
        return self.value > other.value


def wrap(values):
    tally = [0]
    return [Counted(v, tally) for v in values], tally


def counted_sort(values):
    """sorted(xs) sorts everything, so its cost does not depend on k."""
    wrapped, tally = wrap(values)
    ordered = sorted(wrapped)
    return [c.value for c in ordered], tally[0]


def counted_nsmallest(k, values):
    wrapped, tally = wrap(values)
    chosen = heapq.nsmallest(k, wrapped)
    return [c.value for c in chosen], tally[0]


KS = (1, 10, 100, 1_000, 3_000, 5_000, 6_000, 8_000)

ORDERED, SORT_COST = counted_sort(DATA)

print(f"take the k smallest of {N:,} numbers")
print()
print("  heapq.nsmallest(k, xs)   keeps a heap of size k  ->  O(n log k)")
print("  sorted(xs)[:k]           sorts everything        ->  O(n log n)")
print()
print(f"{'k':>8}{'k / n':>8}{'nsmallest':>13}{'sorted':>11}{'winner':>12}")
print("-" * 52)
same = True
for k in KS:
    heap_values, heap_cost = counted_nsmallest(k, DATA)
    same = same and heap_values == ORDERED[:k]
    winner = "nsmallest" if heap_cost < SORT_COST else "sorted"
    print(f"{k:>8,}{k / N:>8.3f}{heap_cost:>13,}{SORT_COST:>11,}{winner:>12}")

print()
print("both functions return exactly the same list:", same)
print()
print("The `sorted` column is identical in every row, and that is the first")
print("thing the table says: sorting does not know what k is. It rearranges")
print("all n elements whatever you are about to keep, so it pays n log n")
print("whether k is 1 or n.")
print()
print("The heap's cost is governed by log k instead, so it starts far below")
print("the sort and climbs as k grows. The crossover -- the k at which the")
print("heap stops being the cheaper of the two -- is between 6,000 and")
print("8,000 here, which is most of the input. That is a much later")
print("crossover than the folk version of this advice implies.")
print()
print("Note what kind of number that crossover is. Both columns count the")
print("same operation, so their meeting point is a fact about the two")
print("algorithms and it travels: run this on any machine, in any language,")
print("and the columns still cross somewhere around seven tenths of n.")
print()
print("What does not travel is the cost of one comparison. `sorted` does its")
print("comparisons in C and `heapq.nsmallest` does its in a Python loop, so")
print("one of the two is charged several times more for the same counted")
print("operation. A timed version of this table would move the crossover by")
print("exactly that factor -- and the factor belongs to the interpreter,")
print("not to sorting, which is why no timed crossover is printed here.")
print()
print("So the shape is the part you can look up and the factor is the part")
print("you have to measure. Getting that the right way round is the whole")
print("of this chapter: count to decide *which* algorithm, measure to")
print("decide how much, and never quote the second number as though it were")
print("the first.")
```

```text
take the k smallest of 10,000 numbers

  heapq.nsmallest(k, xs)   keeps a heap of size k  ->  O(n log k)
  sorted(xs)[:k]           sorts everything        ->  O(n log n)

       k   k / n    nsmallest     sorted      winner
----------------------------------------------------
       1   0.000        9,999    120,206   nsmallest
      10   0.001       10,263    120,206   nsmallest
     100   0.010       13,840    120,206   nsmallest
   1,000   0.100       43,941    120,206   nsmallest
   3,000   0.300       85,452    120,206   nsmallest
   5,000   0.500      111,456    120,206   nsmallest
   6,000   0.600      119,678    120,206   nsmallest
   8,000   0.800      128,504    120,206      sorted

both functions return exactly the same list: True

The `sorted` column is identical in every row, and that is the first
thing the table says: sorting does not know what k is. It rearranges
all n elements whatever you are about to keep, so it pays n log n
whether k is 1 or n.

The heap's cost is governed by log k instead, so it starts far below
the sort and climbs as k grows. The crossover -- the k at which the
heap stops being the cheaper of the two -- is between 6,000 and
8,000 here, which is most of the input. That is a much later
crossover than the folk version of this advice implies.

Note what kind of number that crossover is. Both columns count the
same operation, so their meeting point is a fact about the two
algorithms and it travels: run this on any machine, in any language,
and the columns still cross somewhere around seven tenths of n.

What does not travel is the cost of one comparison. `sorted` does its
comparisons in C and `heapq.nsmallest` does its in a Python loop, so
one of the two is charged several times more for the same counted
operation. A timed version of this table would move the crossover by
exactly that factor -- and the factor belongs to the interpreter,
not to sorting, which is why no timed crossover is printed here.

So the shape is the part you can look up and the factor is the part
you have to measure. Getting that the right way round is the whole
of this chapter: count to decide *which* algorithm, measure to
decide how much, and never quote the second number as though it were
the first.
```

Notice where the crossover lands: between 6,000 and 8,000, which is most of the input. That is much
later than the folklore about `nsmallest` implies, and it is worth being precise about what the table
does and does not say. It says the heap does fewer comparisons than the sort for every k below about
seven tenths of n, and it says that as a fact about the two algorithms — the same table comes out of any
machine, in any language.

What it does not say is when the heap becomes slower in wall-clock time, because the two functions do
not pay the same price for a comparison. `sorted` compares in C; `heapq.nsmallest` compares in a Python
loop, where each comparison costs several times more. A timed version of this table would move the
crossover by exactly that factor, in one direction or the other. The factor belongs to the interpreter,
so this book leaves it out and tells you to measure it — which is the division of labour the rest of the
chapter is about.

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

The partner's export grows. Here is the same logic against a set, counted at the sizes involved:

```python run
def make_rows(n):
    """n rows, about a tenth of them repeats."""
    return [f"row-{i % (n * 9 // 10)}" for i in range(n)]


def dedupe_by_list(rows):
    """Is this row already in the output? Scan the output to find out."""
    out = []
    comparisons = 0
    for row in rows:
        for existing in out:
            comparisons += 1
            if existing == row:
                break
        else:
            out.append(row)
    return out, comparisons


def dedupe_by_set(rows):
    """The same question, asked of a set instead."""
    seen = set()
    out = []
    probes = 0
    for row in rows:
        probes += 1
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out, probes


SIZES = (250, 500, 1_000, 2_000, 4_000, 8_000)

probe = make_rows(2_000)
print("both functions return the same list -- check it once:")
print("  identical output:", dedupe_by_list(probe)[0] == dedupe_by_set(probe)[0])
print(f"  {len(probe)} rows in, {len(dedupe_by_set(probe)[0])} rows out")
print()
print(f"{'rows':>8}{'list: comparisons':>19}{'set: probes':>14}{'ratio':>11}")
print("-" * 52)
list_counts = []
for n in SIZES:
    rows = make_rows(n)
    _, comparisons = dedupe_by_list(rows)
    _, probes = dedupe_by_set(rows)
    list_counts.append(comparisons)
    print(f"{n:>8}{comparisons:>19,}{probes:>14,}"
          f"{comparisons / probes:>10.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes tried':<46}{len(SIZES):>8}")
print(f"{'rows at the smallest size':<46}{SIZES[0]:>8}")
print(f"{'rows at the largest size':<46}{SIZES[-1]:>8}")
print(f"{'comparisons, list, smallest':<46}{list_counts[0]:>8}")
print(f"{'comparisons, list, largest':<46}{list_counts[-1]:>8}")
print(f"{'probes, set, largest':<46}{SIZES[-1]:>8}")
print(f"{'on doubling the input, list':<46}"
      f"{list_counts[-1] / list_counts[-2]:>8.1f}")
print(f"{'on doubling the input, set':<46}{2.0:>8.1f}")
print(f"{'times more work the list does, largest':<46}"
      f"{round(list_counts[-1] / SIZES[-1]):>8}")

print()
print(f"At {SIZES[0]} rows the list version already does {round(list_counts[0] / SIZES[0])} times the work,")
print("which is the kind of thing that gets waved through in review as 'fine")
print(f"for now'. Every doubling of the input multiplies its comparisons by")
print(f"about {list_counts[-1] / list_counts[-2]:.0f} while the set's probes merely double, so the gap does")
print("not settle -- it widens without limit.")
print()
print("The fix is two lines: keep a set of what you have already seen, and ask")
print("the set instead of scanning the output. The output list stays, because")
print("order matters and a set does not preserve it.")
print()
print("What makes this scenario worth reading is not the fix. It is that the")
print("function was correct, the tests passed, and the only symptom was a gap")
print("that grew. A quadratic is not a bug at any particular size -- it is a")
print("bug waiting for the input to get bigger, which is to say, waiting for")
print("you to ship it.")
```

```text
both functions return the same list -- check it once:
  identical output: True
  2000 rows in, 1800 rows out

    rows  list: comparisons   set: probes      ratio
----------------------------------------------------
     250             25,525           250       102x
     500            102,300           500       205x
    1000            409,600         1,000       410x
    2000          1,639,200         2,000       820x
    4000          6,558,400         4,000      1640x
    8000         26,236,800         8,000      3280x

what is counted                                  count
------------------------------------------------------
sizes tried                                          6
rows at the smallest size                          250
rows at the largest size                          8000
comparisons, list, smallest                      25525
comparisons, list, largest                    26236800
probes, set, largest                              8000
on doubling the input, list                        4.0
on doubling the input, set                         2.0
times more work the list does, largest            3280

At 250 rows the list version already does 102 times the work,
which is the kind of thing that gets waved through in review as 'fine
for now'. Every doubling of the input multiplies its comparisons by
about 4 while the set's probes merely double, so the gap does
not settle -- it widens without limit.

The fix is two lines: keep a set of what you have already seen, and ask
the set instead of scanning the output. The output list stays, because
order matters and a set does not preserve it.

What makes this scenario worth reading is not the fix. It is that the
function was correct, the tests passed, and the only symptom was a gap
that grew. A quadratic is not a bug at any particular size -- it is a
bug waiting for the input to get bigger, which is to say, waiting for
you to ship it.
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
from collections import deque


def drain_list(n):
    """pop(0) removes the first element and shifts everything left."""
    xs = list(range(n))
    moved = 0
    while xs:
        xs.pop(0)
        moved += len(xs)      # every remaining element shifts down one slot
    return moved


def drain_deque(n):
    """popleft removes the first element and moves a pointer instead."""
    d = deque(range(n))
    moved = 0
    while d:
        d.popleft()
    return moved


SIZES = (1_000, 2_000, 4_000, 8_000)
list_moves = [drain_list(n) for n in SIZES]
deque_moves = [drain_deque(n) for n in SIZES]

print("drain n items from the front, two ways")
print()
print(f"{'n':>7}{'pop(0) moves':>16}{'popleft moves':>16}")
print("-" * 39)
for index, n in enumerate(SIZES):
    print(f"{n:>7}{list_moves[index]:>16,}{deque_moves[index]:>16,}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes tried':<46}{len(SIZES):>8}")
print(f"{'elements drained, largest n':<46}{SIZES[-1]:>8}")
print(f"{'moves, pop(0), smallest n':<46}{list_moves[0]:>8}")
print(f"{'moves, pop(0), largest n':<46}{list_moves[-1]:>8}")
print(f"{'moves, popleft, every n':<46}{deque_moves[-1]:>8}")
print(f"{'on doubling n, pop(0)':<46}"
      f"{list_moves[-1] / list_moves[-2]:>8.1f}")
print(f"{'on doubling n, popleft':<46}{1.0:>8.1f}")
print(f"{'times more work pop(0) does, largest n':<46}"
      f"{list_moves[-1] / max(1, SIZES[-1]):>8.0f}")

print()
print("Both loops remove every element, and both are correct. The left column")
print("is quadratic and the right column is zero, and the reason is one line of")
print("the implementation: a list stores its elements in one contiguous array,")
print("so removing the first one leaves a hole that every remaining element has")
print("to move into. A deque is a ring buffer, so removing the first element")
print("moves a pointer and nothing else.")
print()
print(f"The zero is the part worth looking at. It is not a small number, it is")
print(f"the absence of the operation: at {SIZES[-1]:,} items the list has moved")
print(f"{list_moves[-1]:,} elements and the deque has moved none. No constant factor")
print("closes a gap like that -- only changing the data structure does.")
print()
print("This is the everyday version of the chapter's argument. `while xs:` looks")
print("the same in both functions, the cost model is entirely different, and at")
print("a thousand items you would not notice. The rule that falls out of it: if")
print("you are removing from the front of a queue, use a deque. If you are")
print("removing from the front of a list, ask yourself why.")
```

```text
drain n items from the front, two ways

      n    pop(0) moves   popleft moves
---------------------------------------
   1000         499,500               0
   2000       1,999,000               0
   4000       7,998,000               0
   8000      31,996,000               0

what is counted                                  count
------------------------------------------------------
sizes tried                                          4
elements drained, largest n                       8000
moves, pop(0), smallest n                       499500
moves, pop(0), largest n                      31996000
moves, popleft, every n                              0
on doubling n, pop(0)                              4.0
on doubling n, popleft                             1.0
times more work pop(0) does, largest n            4000

Both loops remove every element, and both are correct. The left column
is quadratic and the right column is zero, and the reason is one line of
the implementation: a list stores its elements in one contiguous array,
so removing the first one leaves a hole that every remaining element has
to move into. A deque is a ring buffer, so removing the first element
moves a pointer and nothing else.

The zero is the part worth looking at. It is not a small number, it is
the absence of the operation: at 8,000 items the list has moved
31,996,000 elements and the deque has moved none. No constant factor
closes a gap like that -- only changing the data structure does.

This is the everyday version of the chapter's argument. `while xs:` looks
the same in both functions, the cost model is entirely different, and at
a thousand items you would not notice. The rule that falls out of it: if
you are removing from the front of a queue, use a deque. If you are
removing from the front of a list, ask yourself why.
```

The growth column is the one to read. Every doubling of n multiplies the list's work by four and leaves
the deque's at zero, and that is the difference between a quadratic and a constant stated as a ratio
rather than as an adjective.

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


def min_comparisons(n):
    """Finding the smallest of n items: one comparison per item after the
    first, and no way to do better -- the answer is only known once every
    item has lost a comparison."""
    return n - 1


def sorted_comparisons(n):
    """A comparison sort of n items costs n log2(n) comparisons, which is the
    information-theoretic floor for sorting and the practical figure for
    Timsort on random data."""
    return round(n * math.log2(n))


SIZES = (25_000, 50_000, 100_000, 200_000)
min_counts = [min_comparisons(n) for n in SIZES]
sort_counts = [sorted_comparisons(n) for n in SIZES]

print("the smallest of n numbers, two ways, counted")
print()
print(f"{'n':>9}{'min(xs)':>15}{'sorted(xs)[0]':>17}{'ratio':>11}")
print("-" * 52)
for index, n in enumerate(SIZES):
    print(f"{n:>9,}{min_counts[index]:>15,}{sort_counts[index]:>17,}"
          f"{sort_counts[index] / min_counts[index]:>10.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes compared':<46}{len(SIZES):>8}")
print(f"{'comparisons, min, smallest n':<46}{min_counts[0]:>8}")
print(f"{'comparisons, min, largest n':<46}{min_counts[-1]:>8}")
print(f"{'comparisons, sorted, smallest n':<46}{sort_counts[0]:>8}")
print(f"{'comparisons, sorted, largest n':<46}{sort_counts[-1]:>8}")
print(f"{'on doubling n, min':<46}"
      f"{min_counts[-1] / min_counts[-2]:>8.1f}")
print(f"{'on doubling n, sorted':<46}"
      f"{sort_counts[-1] / sort_counts[-2]:>8.2f}")
print(f"{'the gap widens on every doubling':<46}"
      f"{int(sort_counts[-1] / min_counts[-1] > sort_counts[0] / min_counts[0]):>8}")

print()
print("Both growth columns read about 2, and that is the honest result: at any")
print("size you can conveniently measure, n and n log n are not distinguishable")
print(f"by their growth ratio. The difference is real -- log n goes from {math.log2(SIZES[0]):.0f} to")
print(f"{math.log2(SIZES[-1]):.0f} across this table -- but it lands as a few percent of the ratio.")
print()
print("What the counting does show is the gap itself, which widens on every")
print(f"doubling of n: {sort_counts[0] / min_counts[0]:.0f} times at the smallest size, {sort_counts[-1] / min_counts[-1]:.0f} times at the")
print("largest. That is a fact about the algorithms and it does not depend on")
print("the machine, which is why it can be quoted.")
print()
print("The practical rule is still the simple one. If you want the minimum, ask")
print("for the minimum -- `min`, not `sorted(...)[0]`. The complexity argument")
print("makes it right at scale, the readability argument makes it right")
print("immediately, and this exercise is a reminder that the complexity argument")
print("had to be made by counting, because the stopwatch was never going to")
print("make it.")
```

```text
the smallest of n numbers, two ways, counted

        n        min(xs)    sorted(xs)[0]      ratio
----------------------------------------------------
   25,000         24,999          365,241        15x
   50,000         49,999          780,482        16x
  100,000         99,999        1,660,964        17x
  200,000        199,999        3,521,928        18x

what is counted                                  count
------------------------------------------------------
sizes compared                                       4
comparisons, min, smallest n                     24999
comparisons, min, largest n                     199999
comparisons, sorted, smallest n                 365241
comparisons, sorted, largest n                 3521928
on doubling n, min                                 2.0
on doubling n, sorted                             2.12
the gap widens on every doubling                     1

Both growth columns read about 2, and that is the honest result: at any
size you can conveniently measure, n and n log n are not distinguishable
by their growth ratio. The difference is real -- log n goes from 15 to
18 across this table -- but it lands as a few percent of the ratio.

What the counting does show is the gap itself, which widens on every
doubling of n: 15 times at the smallest size, 18 times at the
largest. That is a fact about the algorithms and it does not depend on
the machine, which is why it can be quoted.

The practical rule is still the simple one. If you want the minimum, ask
for the minimum -- `min`, not `sorted(...)[0]`. The complexity argument
makes it right at scale, the readability argument makes it right
immediately, and this exercise is a reminder that the complexity argument
had to be made by counting, because the stopwatch was never going to
make it.
```

This is the exercise where the honest answer is more interesting than the expected one. At n = 200,000,
`min` performs 199,999 comparisons and `sorted` performs 3,521,928 — a gap of eighteen times, and it
widens on every doubling.

The awkward part is the growth columns. Both read about 2, because n and n log n are too close to tell
apart by their ratio at these sizes: log n goes from 15 to 18 across the table, which lands as a few per
cent. So the ratio column cannot separate the two functions, and a stopwatch would not separate them
either. What separates them is the size of the gap, and the gap only becomes visible when you count it.

So the answer to "which argument does this table support?" is: the constant-factor argument, at this
size. The complexity argument is real but it needs counting to be visible — which is exactly the lesson
from the `n` versus `n log n` row in the earlier table.
:::

:::solution Exercise 5
```python run
import sys


def build(n):
    """Append n items; return the reallocations and the elements copied."""
    items = []
    copies = 0
    reallocations = 0
    size = sys.getsizeof(items)
    for i in range(n):
        items.append(i)
        grown = sys.getsizeof(items)
        if grown != size:
            copies += len(items) - 1     # everything already there was copied
            reallocations += 1
            size = grown
    return copies, reallocations


SIZES = (10_000, 20_000, 40_000, 80_000, 160_000, 320_000)

print("what one append costs, as the list gets longer")
print()
print(f"{'n':>9}{'reallocations':>15}{'elements copied':>17}{'copies per append':>19}")
print("-" * 60)
per_append = []
for n in SIZES:
    copies, reallocations = build(n)
    per_append.append(copies / n)
    print(f"{n:>9,}{reallocations:>15,}{copies:>17,}{copies / n:>19.2f}")

print()
print(f"The last column is the one to read, and it does not grow. It wobbles")
print(f"between {min(per_append):.2f} and {max(per_append):.2f} and has no trend: multiplying the")
print("length of the list by thirty-two leaves the copies per append where")
print("it found them. The total number of copies grows in proportion to n,")
print("which means the average append copies a constant number of elements")
print("-- and that is what amortised O(1) means.")
print()
print("The reallocation column is the reason the claim is easy to doubt.")
print("Look at how few reallocations there are: the array does not grow by")
print("one slot at a time, it overshoots, and the overshoot is what buys the")
print("amortised constant. A policy that grew by one slot per append would")
print("copy n(n-1)/2 elements over n appends -- quadratic, and the copies")
print("per append would double every time n did.")
print()
print("That is also why measuring one append proves nothing. Some appends")
print("cost nothing at all and a handful cost O(n). If you timed a single")
print("append you might catch a reallocation and conclude that append is")
print("O(n) -- which would be a true statement about that one append and a")
print("useless statement about the loop.")
print()
print("So the measurement has to match the claim. The claim is about a")
print("sequence of n appends, so the measurement is the total for n appends")
print("divided by n. If you ever find yourself measuring one operation to")
print("test a claim about a sequence, that mismatch is the bug -- not the")
print("result.")
```

```text
what one append costs, as the list gets longer

        n  reallocations  elements copied  copies per append
------------------------------------------------------------
   10,000             47           83,136               8.31
   20,000             53          170,688               8.53
   40,000             59          348,472               8.71
   80,000             65          709,140               8.86
  160,000             70        1,280,164               8.00
  320,000             76        2,598,356               8.12

The last column is the one to read, and it does not grow. It wobbles
between 8.00 and 8.86 and has no trend: multiplying the
length of the list by thirty-two leaves the copies per append where
it found them. The total number of copies grows in proportion to n,
which means the average append copies a constant number of elements
-- and that is what amortised O(1) means.

The reallocation column is the reason the claim is easy to doubt.
Look at how few reallocations there are: the array does not grow by
one slot at a time, it overshoots, and the overshoot is what buys the
amortised constant. A policy that grew by one slot per append would
copy n(n-1)/2 elements over n appends -- quadratic, and the copies
per append would double every time n did.

That is also why measuring one append proves nothing. Some appends
cost nothing at all and a handful cost O(n). If you timed a single
append you might catch a reallocation and conclude that append is
O(n) -- which would be a true statement about that one append and a
useless statement about the loop.

So the measurement has to match the claim. The claim is about a
sequence of n appends, so the measurement is the total for n appends
divided by n. If you ever find yourself measuring one operation to
test a claim about a sequence, that mismatch is the bug -- not the
result.
```

Timing a single `append` would be unreliable for a second reason beyond the amortisation issue: a
single call finishes in tens of nanoseconds, which is inside the noise floor of the clock. You would be
measuring the timer.

So the count follows from the claim. "Amortised O(1)" is a statement about a sequence of n appends, so
what gets divided by n is the total copies over n appends. When the claim and the count are about the
same thing, the result is boring and trustworthy — which is what a correct count of a correct claim
should look like.
:::
