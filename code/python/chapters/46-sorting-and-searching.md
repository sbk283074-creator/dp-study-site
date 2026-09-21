---
chapter: 46
part: 8
title: Sorting and Searching
summary: Sorting is the algorithm you never write, which is exactly why the decisions have moved into the key and the direction. Count what a comparison costs, see why `sorted` is Timsort and stable, choose between `key=` and `cmp_to_key`, and write binary search -- including the two one-character bugs that break it.
minutes: 95
tags: [sorting, timsort, stability, binary search, bisect, cmp_to_key, complexity, ranking]
---

Chapter 45 built the structures. This chapter spends them on the operation that every program
performs more often than any other, and that almost nobody writes.

Sorting is a solved problem, and the solution is one call. `sorted` is correct, it is in C, and it
is faster than anything you would write. That is precisely why the subject deserves a chapter: the
interesting decisions have not gone away, they have *moved*. They are now in the key, in the
direction, in whether the sort was needed at all, and in what you do with the order once you have
it. Those are the four things that go wrong in real code, and none of them raises an exception.

Searching has the opposite shape. You *will* write binary search by hand -- it is the standard
interview question because it is short, and it is the standard bug report because it is subtle. Two
specific one-character mistakes account for most of the failures, and both are in this chapter,
running, with the exact input that breaks them.

One rule carries over from Chapter 44 and it matters more here than anywhere else. **State the cost,
then measure it** -- and here, measure it by *counting*. Every sort in this chapter is measured in
comparisons, not seconds, because a comparison count is a property of the algorithm and the input,
while a timing is a property of this laptop on this afternoon. The counting is done by wrapping the
values in a class with a counting `__lt__`, which is the only way to instrument code that lives in
C.

## What a comparison sort has to pay

Start with the bill, because it sets the ceiling for everything that follows.

A comparison sort learns about its input in exactly one way: it asks "is a < b?". Each answer is one
bit, and it halves the space of possibilities that remain. To pin down which of the n! possible
orders the input is in, you therefore need at least log2(n!) answers -- and Stirling's approximation
says that is about n log2 n.

That is a *floor*, not an estimate. No comparison sort beats it by more than a constant factor, and
this one is already standing on it.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- the bill a comparison sort has to pay.

`sorted` is C, so it cannot be instrumented. But every comparison it makes
goes through `<` on the objects it holds, so wrapping the values in a class
with a counting __lt__ turns the algorithm into a number. That number is a
property of the algorithm and the input, not of this machine.
"""
import math
import random


class Counted:
    """A value that reports how often it was compared."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value

    def __repr__(self):
        return f"Counted({self.value})"


def shuffled(n, seed=0):
    """A genuinely scrambled permutation. Note that a formula like
    `(i * k) % n` will not do: it produces an arithmetic progression, which
    contains long ascending runs for Timsort to find, and the counts come out
    flattering and wrong."""
    values = list(range(n))
    random.Random(seed).shuffle(values)
    return values


def count_sort(values):
    counter = [0]
    items = [Counted(v, counter) for v in values]
    result = sorted(items)
    return counter[0], result


def information_bound(n):
    """log2(n!) -- the number of yes/no answers needed to pin down which of
    the n! possible orders this input is in. Every comparison yields exactly
    one bit, so this is a floor on any comparison sort."""
    return sum(math.log2(k) for k in range(1, n + 1))


print("comparisons made by sorted() on a scrambled input")
print()
print(f"{'n':>9}{'comparisons':>14}{'log2(n!)':>14}{'ratio':>8}"
      f"{'per item':>10}{'log2 n':>8}")
print("-" * 64)
for n in (100, 1_000, 10_000, 100_000):
    comparisons, _ = count_sort(shuffled(n))
    bound = information_bound(n)
    print(f"{n:>9,}{comparisons:>14,}{bound:>14,.0f}"
          f"{comparisons / bound:>8.2f}{comparisons / n:>10.1f}{math.log2(n):>8.1f}")
print()
print("The ratio column is the one to read, and it is deliberately")
print("anticlimactic. As n grows by a factor of a thousand the comparisons")
print("grow by a factor of about two thousand nine hundred -- n log n, not")
print("n^2 -- and the ratio to the theoretical floor stays between 1.01 and")
print("1.02.")
print()
print("That floor is not a coincidence and it is not a property of Timsort.")
print("A comparison sort only ever learns about the input by asking 'is")
print("a < b?', and each answer splits the remaining possibilities in two.")
print("Telling apart the n! possible orderings therefore needs at least")
print("log2(n!) comparisons, and Stirling's approximation gives")
print("log2(n!) ~ n log2 n.")
print()
print("So no comparison sort beats this by more than a constant factor, and")
print("Timsort on scrambled data is already within two percent of the")
print("bound. There is nothing left to win in the algorithm. Everything")
print("interesting is in the constant -- and in the input, which is the")
print("subject of the next two demos.")
```

```text
comparisons made by sorted() on a scrambled input

        n   comparisons      log2(n!)   ratio  per item  log2 n
----------------------------------------------------------------
      100           532           525    1.01       5.3     6.6
    1,000         8,650         8,529    1.01       8.7    10.0
   10,000       120,251       118,458    1.02      12.0    13.3
  100,000     1,531,798     1,516,704    1.01      15.3    16.6

The ratio column is the one to read, and it is deliberately
anticlimactic. As n grows by a factor of a thousand the comparisons
grow by a factor of about two thousand nine hundred -- n log n, not
n^2 -- and the ratio to the theoretical floor stays between 1.01 and
1.02.

That floor is not a coincidence and it is not a property of Timsort.
A comparison sort only ever learns about the input by asking 'is
a < b?', and each answer splits the remaining possibilities in two.
Telling apart the n! possible orderings therefore needs at least
log2(n!) comparisons, and Stirling's approximation gives
log2(n!) ~ n log2 n.

So no comparison sort beats this by more than a constant factor, and
Timsort on scrambled data is already within two percent of the
bound. There is nothing left to win in the algorithm. Everything
interesting is in the constant -- and in the input, which is the
subject of the next two demos.
```

The ratio column is the anticlimax the chapter is built on. Grow the input by a factor of a thousand
-- from 100 items to 100,000 -- and the comparisons grow by a factor of about two thousand nine
hundred. That is n log n, not n², and the gap to the theoretical floor never opens beyond 1.01 or
1.02.

Two consequences follow, and both are worth holding on to. The first is that there is nothing left
to win in the *algorithm*. Timsort on scrambled data is within two percent of a bound that no
algorithm can beat, so anyone who claims a new general-purpose sort is "faster" is talking about the
constant, not the class. The second is that everything interesting has moved into the *input*. A
floor of n log n is the price of sorting data you know nothing about -- and you frequently know
something about your data. That is the subject of the next two sections.

## Insertion sort: one algorithm, four costs

Insertion sort is what you write when you have not thought about sorting, and it is also the
algorithm inside every real sort's finishing pass. It is worth seeing both faces.

The idea is the one you use for a hand of cards. Take the next item, walk left while the item to
your left is larger, and drop it in the gap. Two nested loops, about eight lines, obviously correct.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- insertion sort, counted, on four shapes of input.

Insertion sort is the sort nobody ships and everybody should read once,
because its cost depends on the input's existing order more than on n -- and
that is exactly the fact Timsort is built around.
"""
import random

N = 2_000


def ascending(n):
    return list(range(n))


def descending(n):
    return list(range(n - 1, -1, -1))


def scrambled(n):
    values = list(range(n))
    random.Random(0).shuffle(values)
    return values


def nearly_sorted(n, swaps=10):
    """Ascending, with a few adjacent pairs transposed. The shape of a list
    that was sorted last week and has had a handful of edits since."""
    values = ascending(n)
    for i in range(swaps):
        j = (i * 37) % (n - 1)
        values[j], values[j + 1] = values[j + 1], values[j]
    return values


def insertion_sort(items, counter):
    """Walk left to right, and slide each item back to where it belongs.
    Returns the number of element moves, which is the other half of the
    cost and the half people forget."""
    moves = 0
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        while j >= 0:
            counter[0] += 1
            if items[j] <= key:
                break
            items[j + 1] = items[j]
            moves += 1
            j -= 1
        items[j + 1] = key
    return moves


SHAPES = [
    ("already ascending", ascending),
    ("already descending", descending),
    ("nearly sorted", nearly_sorted),
    ("scrambled", scrambled),
]

print(f"insertion sort on {N:,} items, four input shapes")
print()
print(f"{'input':<22}{'comparisons':>14}{'per item':>10}{'moves':>12}")
print("-" * 58)
for label, make in SHAPES:
    counter = [0]
    moves = insertion_sort(make(N), counter)
    print(f"{label:<22}{counter[0]:>14,}{counter[0] / N:>10.1f}{moves:>12,}")
print()
print("Four different costs for the same algorithm and the same n. The")
print("ascending input is the giveaway: one comparison per item, because")
print("every item is already in place and the inner loop exits immediately.")
print("Descending input is the worst case, at n(n-1)/2 comparisons, and")
print("scrambled input lands about halfway -- n^2/4, which is a million")
print("comparisons for two thousand items.")
print()
print("That spread is not a curiosity. It means 'sorting is O(n^2)' and")
print("'sorting is O(n)' are both true statements about insertion sort, and")
print("the difference is a property of the *data*, not the code. Any sort")
print("that wants to be fast on real inputs has to exploit that -- and the")
print("moves column is the other half, because a move is a write and a")
print("write costs more than a comparison on real hardware.")
print()
print("Now the same shapes through the sort you actually use.")
```

```text
insertion sort on 2,000 items, four input shapes

input                    comparisons  per item       moves
----------------------------------------------------------
already ascending              1,999       1.0           0
already descending         1,999,000     999.5   1,999,000
nearly sorted                  2,008       1.0          10
scrambled                    979,425     489.7     977,437

Four different costs for the same algorithm and the same n. The
ascending input is the giveaway: one comparison per item, because
every item is already in place and the inner loop exits immediately.
Descending input is the worst case, at n(n-1)/2 comparisons, and
scrambled input lands about halfway -- n^2/4, which is a million
comparisons for two thousand items.

That spread is not a curiosity. It means 'sorting is O(n^2)' and
'sorting is O(n)' are both true statements about insertion sort, and
the difference is a property of the *data*, not the code. Any sort
that wants to be fast on real inputs has to exploit that -- and the
moves column is the other half, because a move is a write and a
write costs more than a comparison on real hardware.

Now the same shapes through the sort you actually use.
```

Four different costs, one algorithm, one n. The ascending input costs one comparison per item,
because every item is already in place and the inner loop exits on its first test. The descending
input costs n(n-1)/2 -- 1,999,000 comparisons for two thousand items -- because every item has to
travel the full length of the sorted prefix. The scrambled input lands about halfway, at n²/4, which
is a million comparisons for the same two thousand items.

So "insertion sort is O(n²)" and "insertion sort is O(n)" are both true statements, and the
difference is entirely in the data. This is why an honest complexity statement is not a single
symbol: it is a symbol *plus* the shape of the input you are claiming it for.

The moves column is the other half, and it is the half people forget. A comparison is a read; a move
is a write. On real hardware a write is more expensive than a read, and in insertion sort the two
columns are nearly identical on scrambled input -- 979,425 comparisons and 977,437 moves. Any sort
that wants to be fast on real inputs has to exploit order where it finds it, which is exactly what
the sort you actually use does.

## Why `sorted` is not insertion sort

`sorted` is Timsort, and Timsort is built on a single observation: real data is almost never
scrambled. It scans the input looking for *runs* -- maximal stretches that are already ordered, in
either direction -- and merges them. A descending run is accepted as a run and reversed, which is
one line of code that saves an entire worst case.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- what `sorted` does with order that is already there.

Timsort is a merge sort with two additions: it finds the runs already present
in the input, and it uses insertion sort on short stretches. Both additions
pay off enormously on real data, and the comparison counts show exactly how.
"""
import math
import random

N = 20_000


class Counted:
    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value


def ascending(n):
    return list(range(n))


def descending(n):
    return list(range(n - 1, -1, -1))


def scrambled(n):
    values = list(range(n))
    random.Random(0).shuffle(values)
    return values


def two_runs(n):
    """Two ascending runs concatenated -- a merge of two sorted halves, which
    is what you get from merging log files or from a database union."""
    half = n // 2
    return list(range(half)) + list(range(half, n))


def nearly_sorted(n, swaps=20):
    values = ascending(n)
    for i in range(swaps):
        j = (i * 37) % (n - 1)
        values[j], values[j + 1] = values[j + 1], values[j]
    return values


def all_equal(n):
    return [7] * n


def count_sort(values):
    counter = [0]
    items = [Counted(v, counter) for v in values]
    result = sorted(items)
    return counter[0], [item.value for item in result]


def information_bound(n):
    return sum(math.log2(k) for k in range(1, n + 1))


SHAPES = [
    ("already ascending", ascending),
    ("already descending", descending),
    ("nearly sorted", nearly_sorted),
    ("two ascending runs", two_runs),
    ("all items equal", all_equal),
    ("scrambled", scrambled),
]

print(f"sorted() on {N:,} items, six input shapes")
print(f"  log2({N:,}) = {math.log2(N):.1f}; the theoretical floor is "
      f"log2(n!) = {information_bound(N):,.0f} comparisons")
print()
print(f"{'input':<22}{'comparisons':>14}{'per item':>10}{'vs floor':>10}")
print("-" * 56)
rows = {}
for label, make in SHAPES:
    comparisons, result = count_sort(make(N))
    rows[label] = result
    print(f"{label:<22}{comparisons:>14,}{comparisons / N:>10.1f}"
          f"{comparisons / information_bound(N):>10.2f}")
print()
print("Five of the six shapes cost about one comparison per item. Only the")
print("scrambled one pays the n log n price, and it lands within two percent")
print("of the floor -- so there is nothing left to win there.")
print()
print("Each of the five cheap rows is a different trick, and they are worth")
print("telling apart because only one of them is an optimisation.")
print()
print("  ascending    one run. Timsort walks the input once, sees the whole")
print("               thing is already in order, and stops. n-1 comparisons.")
print("  descending   also one run -- Timsort accepts a *descending* run and")
print("               reverses it. A hand-written merge sort pays n log n")
print("               here and a naive quicksort pays n^2.")
print("  two runs     this is a merge, not a sort. Two sorted halves need")
print("               n-1 comparisons to interleave, which is why 'merge two")
print("               sorted lists' and 'sort a list' have different costs.")
print("  nearly       one run, plus a handful of out-of-place items that the")
print("               insertion-sort tail fixes. Real files look like this.")
print("  all equal    every comparison returns False, so the run never")
print("               breaks. This is the input that degrades a naive")
print("               quicksort to quadratic; Timsort simply runs out of")
print("               comparisons to make.")
print()
print("So 'how fast is sorted?' has no single answer: on the same n, the")
print("cost spans from n to n log n -- a factor of 13 here. The useful")
print("question is not about the algorithm but about the input.")
print()
print("That is also why five rows can sit at 0.08 of a column headed")
print("'floor'. log2(n!) is the cost of working out the order of an input")
print("you know nothing about. An input that is already in order needs no")
print("comparisons to identify its order, so the bound does not apply to")
print("it -- and a sort that pays n log n for sorted input is paying for")
print("information it was handed for free.")
print()
print("All the shapes holding the same values came back in the same order:")
same_values = ("already ascending", "already descending", "nearly sorted",
               "two ascending runs", "scrambled")
print(f"  {rows['scrambled'][:12]}")
print(f"  {rows['already descending'][:12]}")
print(f"  all five agree: {len({tuple(rows[k]) for k in same_values}) == 1}")
print(f"  'all items equal' holds {len(rows['all items equal']):,} copies of 7: "
      f"{set(rows['all items equal']) == {7}}")
```

```text
sorted() on 20,000 items, six input shapes
  log2(20,000) = 14.3; the theoretical floor is log2(n!) = 256,909 comparisons

input                    comparisons  per item  vs floor
--------------------------------------------------------
already ascending             19,999       1.0      0.08
already descending            19,999       1.0      0.08
nearly sorted                 21,258       1.1      0.08
two ascending runs            19,999       1.0      0.08
all items equal               19,999       1.0      0.08
scrambled                    260,341      13.0      1.01

Five of the six shapes cost about one comparison per item. Only the
scrambled one pays the n log n price, and it lands within two percent
of the floor -- so there is nothing left to win there.

Each of the five cheap rows is a different trick, and they are worth
telling apart because only one of them is an optimisation.

  ascending    one run. Timsort walks the input once, sees the whole
               thing is already in order, and stops. n-1 comparisons.
  descending   also one run -- Timsort accepts a *descending* run and
               reverses it. A hand-written merge sort pays n log n
               here and a naive quicksort pays n^2.
  two runs     this is a merge, not a sort. Two sorted halves need
               n-1 comparisons to interleave, which is why 'merge two
               sorted lists' and 'sort a list' have different costs.
  nearly       one run, plus a handful of out-of-place items that the
               insertion-sort tail fixes. Real files look like this.
  all equal    every comparison returns False, so the run never
               breaks. This is the input that degrades a naive
               quicksort to quadratic; Timsort simply runs out of
               comparisons to make.

So 'how fast is sorted?' has no single answer: on the same n, the
cost spans from n to n log n -- a factor of 13 here. The useful
question is not about the algorithm but about the input.

That is also why five rows can sit at 0.08 of a column headed
'floor'. log2(n!) is the cost of working out the order of an input
you know nothing about. An input that is already in order needs no
comparisons to identify its order, so the bound does not apply to
it -- and a sort that pays n log n for sorted input is paying for
information it was handed for free.

All the shapes holding the same values came back in the same order:
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  all five agree: True
  'all items equal' holds 20,000 copies of 7: True
```

Six input shapes, and five of them cost about one comparison per item. Only the scrambled shape pays
the n log n price -- and it lands within two percent of the floor, so even there nothing is wasted.

Each cheap row is a different trick, and they are worth telling apart, because only some of them are
optimisations:

- **Ascending.** One run covering the whole input. Timsort walks it once, sees it is ordered, and
  stops: 19,999 comparisons for 20,000 items.
- **Descending.** Also one run. Timsort accepts it and reverses it. A hand-written merge sort pays
  n log n here and a naive quicksort pays n², so this row is a deliberate design decision rather
  than luck.
- **Two ascending runs.** This is a *merge*, not a sort. Interleaving two sorted halves costs n-1
  comparisons, which is why "merge two sorted lists" and "sort this list" have different costs --
  and why the merge step of a merge sort is linear.
- **Nearly sorted.** One run plus a handful of out-of-place items that the insertion-sort tail fixes.
  Real files look like this, which is the entire reason Timsort exists.
- **All items equal.** Every comparison returns `False`, so the run never breaks. This is the input
  that degrades a naive quicksort to quadratic; Timsort simply runs out of comparisons to make.

So "how fast is `sorted`?" has no single answer. On the same 20,000 items the cost spans a factor of
thirteen, and the useful question is not about the algorithm but about the input you are handing it.

The last block of that output explains why five rows can sit at 0.08 of a column headed "floor",
which looks like a violation until you read the heading. log2(n!) is the cost of working out the
order of an input you know *nothing* about. An input that is already in order needs no comparisons
to identify its order, so the bound does not apply to it. A sort that pays n log n for sorted input
is paying for information it was handed for free.

## Stability: the guarantee you did not ask for

Python's `sorted` is *stable*: items that compare equal come out in the order they went in. The
guarantee is invisible until you depend on it, and then it is load-bearing.

It is also the easiest guarantee in the standard library to destroy by accident, because the two ways
to sort descending look interchangeable and are not.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- stability, and the one-line way to lose it.

A sort is stable if items that compare equal come out in the order they went
in. Python guarantees this for `sorted` and `list.sort`, and the guarantee is
what makes multi-key sorting work without tuple keys.
"""
RECORDS = [
    ("eve", 91),
    ("bob", 78),
    ("hal", 91),
    ("dee", 78),
    ("ada", 91),
    ("fay", 65),
    ("gus", 78),
    ("cyd", 91),
]


def score(record):
    return record[1]


def names(records):
    return [name for name, _ in records]


def show(label, records):
    print(f"  {label:<38}{names(records)}")


print("the input, in the order it arrived")
show("as given", RECORDS)
print()
print("sorting by score, highest first")
print()
show("key=score, reverse=True", sorted(RECORDS, key=score, reverse=True))
show("key=score, then [::-1]", sorted(RECORDS, key=score)[::-1])
print()
print("Both produce a list in descending score order, and they are not the")
print("same list. The four 91s come out eve, hal, ada, cyd in the first --")
print("their order of arrival -- and cyd, ada, hal, eve in the second,")
print("which is exactly reversed.")
print()
print("`reverse=True` reverses the *comparison*, so equal items are still")
print("compared as equal and the stable tie-break survives. Slicing with")
print("[::-1] reverses the *result*, so it reverses the ties too. This is")
print("the most common way to lose stability, and it looks like a harmless")
print("rewrite of the line above it.")
print()
print("The guarantee is worth having because it replaces tuple keys for")
print("multi-key sorts. To sort by score and then by name, sort by the")
print("*secondary* key first and the primary key second:")
print()
first_pass = sorted(RECORDS, key=lambda record: record[0])
show("sorted by name", first_pass)
second_pass = sorted(first_pass, key=score, reverse=True)
show("then by score, reverse=True", second_pass)
print()
print("Compare the 91s in that last line with the 91s from the single stable")
print("sort above it. The two-pass version gives ada, cyd, eve, hal -- name")
print("order -- where the single pass gave arrival order. Each pass is")
print("stable, so the name order established in the first pass survives")
print("inside every group of equal scores.")
print()
print("The tuple-key version `key=lambda r: (-r[1], r[0])` gets the same")
print("answer in one pass and is usually the better code -- but it only")
print("works when the keys are orderable, and the two-pass version works")
print("when they are not.")
print()
print("A stable sort is also what makes 'group by' expressible without a")
print("dict. Sort by the group key and the groups come out contiguous and")
print("internally in arrival order:")
print()
by_score = sorted(RECORDS, key=score, reverse=True)
runs = []
for record in by_score:
    if not runs or runs[-1][0] != record[1]:
        runs.append((record[1], []))
    runs[-1][1].append(record[0])
for value, group in runs:
    print(f"  score {value}: {group}")
```

```text
the input, in the order it arrived
  as given                              ['eve', 'bob', 'hal', 'dee', 'ada', 'fay', 'gus', 'cyd']

sorting by score, highest first

  key=score, reverse=True               ['eve', 'hal', 'ada', 'cyd', 'bob', 'dee', 'gus', 'fay']
  key=score, then [::-1]                ['cyd', 'ada', 'hal', 'eve', 'gus', 'dee', 'bob', 'fay']

Both produce a list in descending score order, and they are not the
same list. The four 91s come out eve, hal, ada, cyd in the first --
their order of arrival -- and cyd, ada, hal, eve in the second,
which is exactly reversed.

`reverse=True` reverses the *comparison*, so equal items are still
compared as equal and the stable tie-break survives. Slicing with
[::-1] reverses the *result*, so it reverses the ties too. This is
the most common way to lose stability, and it looks like a harmless
rewrite of the line above it.

The guarantee is worth having because it replaces tuple keys for
multi-key sorts. To sort by score and then by name, sort by the
*secondary* key first and the primary key second:

  sorted by name                        ['ada', 'bob', 'cyd', 'dee', 'eve', 'fay', 'gus', 'hal']
  then by score, reverse=True           ['ada', 'cyd', 'eve', 'hal', 'bob', 'dee', 'gus', 'fay']

Compare the 91s in that last line with the 91s from the single stable
sort above it. The two-pass version gives ada, cyd, eve, hal -- name
order -- where the single pass gave arrival order. Each pass is
stable, so the name order established in the first pass survives
inside every group of equal scores.

The tuple-key version `key=lambda r: (-r[1], r[0])` gets the same
answer in one pass and is usually the better code -- but it only
works when the keys are orderable, and the two-pass version works
when they are not.

A stable sort is also what makes 'group by' expressible without a
dict. Sort by the group key and the groups come out contiguous and
internally in arrival order:

  score 91: ['eve', 'hal', 'ada', 'cyd']
  score 78: ['bob', 'dee', 'gus']
  score 65: ['fay']
```

Read the four 91s across those two lines. `key=score, reverse=True` gives them back as eve, hal, ada,
cyd -- their order of arrival. `key=score` followed by `[::-1]` gives cyd, ada, hal, eve, which is
exactly reversed. Both lists are in descending score order. Only one of them kept the tie-break.

The reason is that `reverse=True` reverses the *comparison*: equal items are still compared as equal,
so the stable tie-break survives and simply runs backwards through the ordering that was already
there. Slicing with `[::-1]` reverses the *result*, which reverses the ties along with everything
else.

:::pitfall `[::-1]` looks like a shorter way to write `reverse=True`
They are not the same operation and they do not produce the same list. `reverse=True` sorts
descending and keeps stability; `[::-1]` sorts ascending and then turns the whole result around,
which inverts every group of equal keys. The failure is silent, the output is still sorted, and the
only symptom is an order somebody has to notice. If you want descending, say `reverse=True`.
:::

The guarantee earns its keep because it replaces tuple keys for multi-key sorting. To sort by score
and then by name, sort by the *secondary* key first and the primary key last. Each pass is stable, so
whatever order the earlier pass established survives inside every group the final pass creates. The
output above shows exactly that: sorting by name and then by score gives ada, cyd, eve, hal among
the 91s -- name order -- where the single-pass sort gave arrival order.

The tuple key `key=lambda r: (-r[1], r[0])` gets the same answer in one pass, and it is usually the
better code. It is not always available, though, and the next two sections are about what to do when
it is not.

## `key=` or `cmp_to_key`

The interface offers two ways to tell a sort what "in order" means, and they are not equally
expensive.

A **key** is a function from one item to a value that can be compared with `<`. A **comparator** is a
function from two items to a negative number, zero, or a positive number. Python applies a key
*before* the sort and then sorts the resulting values, so the key runs exactly once per item. A
comparator cannot be precomputed -- it has to be consulted during the sort -- so it runs once per
comparison.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- how often each of the two sorting interfaces runs your code.

`sorted(x, key=f)` and `sorted(x, key=cmp_to_key(g))` look like two spellings
of the same request. They are not: one calls your function once per item and
the other calls it once per comparison, and the difference is a factor of
log n on every sort you write.
"""
import functools
import math
import random

N = 2_000

KEY_CALLS = [0]
CMP_CALLS = [0]


def records(n):
    rng = random.Random(0)
    return [(f"row{i:05d}", rng.randrange(1_000)) for i in range(n)]


ROWS = records(N)


def by_score(record):
    KEY_CALLS[0] += 1
    return record[1]


def compare_score(left, right):
    CMP_CALLS[0] += 1
    if left[1] != right[1]:
        return -1 if left[1] < right[1] else 1
    return -1 if left[0] < right[0] else (1 if left[0] > right[0] else 0)


print(f"sorting {N:,} rows by score, two ways")
print()
print(f"{'interface':<34}{'your function is called':>26}")
print("-" * 60)
KEY_CALLS[0] = 0
by_key = sorted(ROWS, key=by_score)
key_calls = KEY_CALLS[0]
print(f"{'key=by_score':<34}{key_calls:>26,}")
CMP_CALLS[0] = 0
by_cmp = sorted(ROWS, key=functools.cmp_to_key(compare_score))
cmp_calls = CMP_CALLS[0]
print(f"{'key=cmp_to_key(compare_score)':<34}{cmp_calls:>26,}")
print(f"{'ratio':<34}{cmp_calls / key_calls:>26.1f}")
print()
print(f"{'same answer either way':<34}{str(by_key == by_cmp):>26}")
print(f"{'log2(n) for reference':<34}{math.log2(N):>26.1f}")
print()
print("The key function runs exactly n times, and the comparator runs about")
print("ten times as often -- which is the log n factor, with Timsort's own")
print("constant folded in.")
print()
print("That is not a micro-optimisation. A key function is called once per")
print("item no matter how the sort goes, because Python applies it first and")
print("then sorts the *keys*. That is the decorate-sort-undecorate pattern")
print("from the old days, built into the interface: for an expensive key,")
print("the difference between n and n log n calls is the difference between")
print("a report that takes a second and one that takes a minute.")
print()
print("So the rule is: reach for a key. It is called less often, it is")
print("easier to read, and it cannot introduce an inconsistent comparator.")
print()
print("But a key is not always available, and that is what cmp_to_key is")
print("for. A key must map each item to something independently -- the")
print("comparison is then just '<' on the keys. When the right order")
print("depends on the *pair*, no such mapping exists:")
print()
NUMBERS = [10, 2, 30, 5, 9, 100, 1]
print(f"  numbers: {NUMBERS}")
print("  task: arrange them so the concatenation is the largest number")
print(f"  a key would need: 'is 10 before 2?' -- and the answer depends on")
print("  the other item, not on the item alone.")
print()


def largest_first(left, right):
    """Compare the two possible concatenations. There is no key that does
    this, because 'a before b' depends on b."""
    if left + right > right + left:
        return -1
    if left + right < right + left:
        return 1
    return 0


texts = [str(n) for n in NUMBERS]
arranged = sorted(texts, key=functools.cmp_to_key(largest_first))
by_value = sorted(texts, key=int, reverse=True)
print(f"  cmp_to_key result : {arranged}")
print(f"  concatenated      : {''.join(arranged)}")
print(f"  sorted as integers: {by_value}")
print(f"  concatenated      : {''.join(by_value)}")
print(f"  the comparator wins: {int(''.join(arranged)) > int(''.join(by_value))}")
print()
print("The comparison is 'does a+b beat b+a', and that is not a property of")
print("a alone, so no key can express it. Sorting by numeric value gives a")
print("different and smaller concatenation. That is the case cmp_to_key")
print("exists for, and it is rare enough that reaching for it should be a")
print("deliberate decision rather than the default.")
```

```text
sorting 2,000 rows by score, two ways

interface                            your function is called
------------------------------------------------------------
key=by_score                                           2,000
key=cmp_to_key(compare_score)                         19,329
ratio                                                    9.7

same answer either way                                  True
log2(n) for reference                                   11.0

The key function runs exactly n times, and the comparator runs about
ten times as often -- which is the log n factor, with Timsort's own
constant folded in.

That is not a micro-optimisation. A key function is called once per
item no matter how the sort goes, because Python applies it first and
then sorts the *keys*. That is the decorate-sort-undecorate pattern
from the old days, built into the interface: for an expensive key,
the difference between n and n log n calls is the difference between
a report that takes a second and one that takes a minute.

So the rule is: reach for a key. It is called less often, it is
easier to read, and it cannot introduce an inconsistent comparator.

But a key is not always available, and that is what cmp_to_key is
for. A key must map each item to something independently -- the
comparison is then just '<' on the keys. When the right order
depends on the *pair*, no such mapping exists:

  numbers: [10, 2, 30, 5, 9, 100, 1]
  task: arrange them so the concatenation is the largest number
  a key would need: 'is 10 before 2?' -- and the answer depends on
  the other item, not on the item alone.

  cmp_to_key result : ['9', '5', '30', '2', '1', '10', '100']
  concatenated      : 95302110100
  sorted as integers: ['100', '30', '10', '9', '5', '2', '1']
  concatenated      : 10030109521
  the comparator wins: True

The comparison is 'does a+b beat b+a', and that is not a property of
a alone, so no key can express it. Sorting by numeric value gives a
different and smaller concatenation. That is the case cmp_to_key
exists for, and it is rare enough that reaching for it should be a
deliberate decision rather than the default.
```

Two thousand items. The key is called 2,000 times and the comparator 19,329 times, a ratio of 9.7
against a log2(n) of 11.0. That is the log n factor, with Timsort's own constant folded in.

This is not a micro-optimisation. For a key that does real work -- parsing a date, normalising a
string, hitting a cache -- the difference between n calls and n log n calls is the difference between
a report that takes a second and one that takes a minute. A key is also easier to read and *cannot*
be internally inconsistent, because it is a pure function of one item. A comparator can be, and a
comparator that is inconsistent -- "a before b, b before c, c before a" -- produces an arbitrary
order with no error.

:::tip Reach for a key first, then a richer key, then `cmp_to_key`
The order to try them in is: a key, then a key that encodes more of the rule, then `cmp_to_key`.
`cmp_to_key` is the escape hatch for the case where the order of a pair depends on *both* items at
once, so no per-item mapping exists. The largest-number problem in the output above is that case: to
decide whether 10 goes before 2 you have to compare "102" with "210", and that answer is not a
property of 10. Once you have written a comparator, you have also given up the ability to look at
one item and say where it belongs -- so use it deliberately, not by default.
:::

## Binary search, and the two one-character bugs

Now the searching half. Binary search is short enough to write from memory and subtle enough that
most people's memory of it is wrong in one of two specific places.

The version to memorise answers "where does this belong?", not "is it here?". That is a *rank*, and
a rank always exists -- which removes the not-found case entirely.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- binary search, its two classic off-by-ones, and the
probe count that makes the whole thing worth getting right.

Both bugs below are written out and made to fail on a named input, because
'be careful with the boundary' is not advice anybody can act on.
"""
CAP = 60
SORTED = list(range(0, 200, 2))


def lower_bound(items, target):
    """The index of the first item that is >= target. This is the version
    that answers 'where does this belong', and it is the one to memorise."""
    low, high = 0, len(items)
    probes = 0
    while low < high:
        probes += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low, probes


def contains(items, target):
    """Membership. Note the different invariants: high starts at len-1, the
    loop runs while low <= high, and both bounds move past middle."""
    low, high = 0, len(items) - 1
    probes = 0
    while low <= high:
        probes += 1
        middle = (low + high) // 2
        if items[middle] == target:
            return True, probes
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return False, probes


def lower_bound_bug_low(items, target):
    """BUG 1: `low = middle` instead of `middle + 1`. When the target is above
    every item, low stops moving and the loop never terminates."""
    low, high = 0, len(items)
    probes = 0
    while low < high:
        probes += 1
        if probes > CAP:
            return None, probes
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle
        else:
            high = middle
    return low, probes


def lower_bound_bug_high(items, target):
    """BUG 2: `high = middle - 1` in a lower-bound search. It is correct for
    membership and wrong here, because the answer can be *at* middle."""
    low, high = 0, len(items)
    probes = 0
    while low < high:
        probes += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return low, probes


print(f"a sorted list of {len(SORTED)} even numbers, 0 to {SORTED[-1]}")
print()
print(f"{'target':>8}{'lower_bound':>14}{'correct?':>10}{'probes':>9}"
      f"{'linear scan':>13}")
print("-" * 54)
for target in (0, 1, 100, 199, 200):
    index, probes = lower_bound(SORTED, target)
    expected = sum(1 for value in SORTED if value < target)
    scan = 0
    for value in SORTED:
        scan += 1
        if value >= target:
            break
    else:
        scan = len(SORTED)
    print(f"{target:>8}{index:>14}{str(index == expected):>10}{probes:>9}{scan:>13}")
print()
print("Every answer is the count of items below the target, and every one")
print("costs six or seven probes against a scan of up to a hundred. The odd")
print("targets are the interesting ones: 1 and 199 are not in the list at")
print("all, and lower_bound still answers 'where would it go' rather than")
print("failing.")
print()
print("That is the difference between a search and a *rank*. A search wants")
print("a yes or a no; a rank wants a position, and a position always exists.")
print()
print("Now the two bugs. Both are one character wrong.")
print()
print(f"{'case':<46}{'result':>10}")
print("-" * 56)
for target in (500, 2):
    _, probes = lower_bound_bug_low(SORTED, target)
    print(f"{'bug 1: low = middle, target ' + str(target):<46}{'hangs':>10}")
    print(f"{'  probes before the step cap stopped it':<46}{probes:>10}")
_, probes = lower_bound_bug_low(SORTED, 0)
print(f"{'bug 1: low = middle, target 0':<46}{'ok':>10}")
print(f"{'  the one target it survives':<46}{probes:>10}")
print()
correct, _ = lower_bound(SORTED, 100)
buggy, _ = lower_bound_bug_high(SORTED, 100)
print(f"{'bug 2: high = middle - 1, target 100':<46}{buggy:>10}")
print(f"{'  correct answer':<46}{correct:>10}")
buggy, _ = lower_bound_bug_high(SORTED, 0)
print(f"{'bug 2: high = middle - 1, target 0':<46}{buggy:>10}")
print(f"{'  correct answer':<46}{0:>10}")
print()
print("Bug 1 does not give a wrong answer, it gives *no* answer. With the")
print("target above the first item, low and middle converge on the same index")
print("and low stops advancing, so the loop spins until something else kills")
print("it. Only target 0 terminates, because the answer is 0 and low never")
print("has to move. A hang in production is worse than an exception: nothing")
print("in the logs says which line is at fault.")
print()
print("Bug 2 gives a wrong answer silently, off by one, and it is correct")
print("for target 0 and wrong for target 100 -- exactly the shape of bug that")
print("passes the two tests somebody wrote by hand.")
print()
print("Both come from the same mistake: treating the two bounds as if they")
print("were the same kind of thing. In a lower-bound search the invariant is")
print("that the answer lies in [low, high), and high is *exclusive* -- so it")
print("starts at len(items), never at len(items) - 1, and it is set to middle")
print("rather than middle - 1. In a membership search both bounds are")
print("inclusive and both move past middle. Pick one convention, write it")
print("down, and do not mix them.")
print()
print("The standard library has both, tested and in C:")
print()
print("  bisect.bisect_left(items, x)   first index where items[i] >= x")
print("  bisect.bisect_right(items, x)  first index where items[i] >  x")
print()
print("bisect_left is the lower bound above. bisect_right is the same search")
print("with `<=` instead of `<`, and it is the one that matters when the list")
print("has duplicates.")
```

```text
a sorted list of 100 even numbers, 0 to 198

  target   lower_bound  correct?   probes  linear scan
------------------------------------------------------
       0             0      True        7            1
       1             1      True        7            2
     100            50      True        6           51
     199           100      True        6          100
     200           100      True        6          100

Every answer is the count of items below the target, and every one
costs six or seven probes against a scan of up to a hundred. The odd
targets are the interesting ones: 1 and 199 are not in the list at
all, and lower_bound still answers 'where would it go' rather than
failing.

That is the difference between a search and a *rank*. A search wants
a yes or a no; a rank wants a position, and a position always exists.

Now the two bugs. Both are one character wrong.

case                                              result
--------------------------------------------------------
bug 1: low = middle, target 500                    hangs
  probes before the step cap stopped it               61
bug 1: low = middle, target 2                      hangs
  probes before the step cap stopped it               61
bug 1: low = middle, target 0                         ok
  the one target it survives                           7

bug 2: high = middle - 1, target 100                  49
  correct answer                                      50
bug 2: high = middle - 1, target 0                     0
  correct answer                                       0

Bug 1 does not give a wrong answer, it gives *no* answer. With the
target above the first item, low and middle converge on the same index
and low stops advancing, so the loop spins until something else kills
it. Only target 0 terminates, because the answer is 0 and low never
has to move. A hang in production is worse than an exception: nothing
in the logs says which line is at fault.

Bug 2 gives a wrong answer silently, off by one, and it is correct
for target 0 and wrong for target 100 -- exactly the shape of bug that
passes the two tests somebody wrote by hand.

Both come from the same mistake: treating the two bounds as if they
were the same kind of thing. In a lower-bound search the invariant is
that the answer lies in [low, high), and high is *exclusive* -- so it
starts at len(items), never at len(items) - 1, and it is set to middle
rather than middle - 1. In a membership search both bounds are
inclusive and both move past middle. Pick one convention, write it
down, and do not mix them.

The standard library has both, tested and in C:

  bisect.bisect_left(items, x)   first index where items[i] >= x
  bisect.bisect_right(items, x)  first index where items[i] >  x

bisect_left is the lower bound above. bisect_right is the same search
with `<=` instead of `<`, and it is the one that matters when the list
has duplicates.
```

Every answer in that first table is the count of items below the target, and every one costs six or
seven probes against a scan of up to a hundred. The odd targets are the interesting ones: 1 and 199
are not in the list at all, and the search still answers "where would it go" rather than failing.

That distinction -- a search wants a yes or a no, a rank wants a position -- is the whole reason
`bisect` is more useful than `in`.

Then the two bugs, each one character wrong, each made to fail on a named input:

- **`low = middle` instead of `middle + 1`.** The lower bound never advances, so the loop never
  terminates. It does not produce a wrong answer, it produces *no* answer: the two hanging cases in
  the table are still spinning when the step cap stops them at 61 probes. The single target it
  survives is 0, because the answer is 0 and `low` never has to move.
- **`high = middle - 1` in a lower-bound search.** This is correct for *membership* and wrong here,
  because the answer can be *at* `middle`. For target 100 it returns 49 where the answer is 50, and
  for target 0 it returns the right answer -- which is the shape of bug that passes the two tests
  somebody wrote by hand.

Both come from the same mistake: treating the two bounds as if they were the same kind of thing. A
lower-bound search keeps the answer in `[low, high)` with `high` **exclusive**, so it starts at
`len(items)` -- never `len(items) - 1` -- and it is set to `middle`, not `middle - 1`. A membership
search uses inclusive bounds and moves both of them past `middle`. Pick one convention, write it
down, and do not mix them: mixing them gives you a hang in one direction and a silent off-by-one in
the other.

A hang is worse than an exception, by the way. Nothing in the logs says which line is at fault.

## The two bisects

The standard library has both conventions, tested, in C. `bisect_left` is the lower bound above;
`bisect_right` is the same search with `<=` instead of `<`. They differ by one comparison and answer
two different questions, and choosing wrong is a silent off-by-one in every group of duplicates.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- the two bisects, and what each one is for.

`bisect_left` and `bisect_right` differ by one comparison and answer two
different questions. Choosing the wrong one is a silent off-by-one in every
duplicate group.
"""
import bisect

SCORES = [40, 55, 55, 55, 70, 82, 82, 95]
GRADES = [(0, 50, "F"), (50, 60, "D"), (60, 70, "C"),
          (70, 80, "B"), (80, 101, "A")]
BOUNDARIES = [low for low, _, _ in GRADES[1:]]


def count_below(items, target):
    return bisect.bisect_left(items, target)


def count_at_most(items, target):
    return bisect.bisect_right(items, target)


print(f"a sorted list with duplicates: {SCORES}")
print()
print(f"{'target':>8}{'bisect_left':>14}{'bisect_right':>15}{'copies':>10}")
print("-" * 48)
for target in (40, 55, 70, 82, 95, 60):
    left = count_below(SCORES, target)
    right = count_at_most(SCORES, target)
    print(f"{target:>8}{left:>14}{right:>15}{right - left:>10}")
print()
print("The two functions are the same search with `<` and `<=`, and the")
print("difference is only visible where there are duplicates.")
print()
print("  bisect_left  is the number of items *strictly below* the target --")
print("               the index a new copy would take if it had to go")
print("               before the existing ones.")
print("  bisect_right is the number of items *at or below* the target -- the")
print("               index a new copy would take if it had to go after.")
print()
print("So `right - left` is the number of copies present, computed in two")
print("log n searches without counting anything. That is the standard way to")
print("answer 'how many of these are there' on sorted data.")
print()
print("It is also the whole of the 'insort stability' question. To see it, the")
print("items need to be distinguishable while still comparing equal -- so here")
print("is a class that compares on value only:")
print()


class Scored:
    """`bisect` needs nothing from an item except `<`, so a class that
    defines only that is a legal element of a sorted list."""

    __slots__ = ("value", "tag")

    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return f"{self.tag}{self.value}"


def tagged(values):
    return [Scored(value, chr(ord("a") + i)) for i, value in enumerate(values)]


print(f"  starting list: {tagged([40, 55, 55, 55, 70])}")
print("  inserting N55, which compares equal to three existing items")
print()
for function, name in ((bisect.insort_left, "insort_left"),
                       (bisect.insort_right, "insort_right")):
    items = tagged([40, 55, 55, 55, 70])
    function(items, Scored(55, "N"))
    print(f"  {name:<14} -> {items}")
print()
print("The new item lands at index 1 with insort_left and at index 4 with")
print("insort_right -- before its equals or after them. Both keep the list")
print("sorted by value, and only one keeps whatever order those three 55s")
print("already had. That is the same stability question as the previous")
print("demo, and the same one-character difference answers it.")
print()
print("Now the use that pays for knowing both. Grade bands are a list of")
print("boundaries and a search, not a chain of comparisons:")
print()
print(f"  boundaries: {BOUNDARIES}")
print(f"  grades    : {[label for _, _, label in GRADES]}")
print()
print(f"{'score':>8}{'bisect_right':>14}{'grade':>8}")
print("-" * 32)
for score in (0, 49, 50, 59, 60, 71, 80, 100):
    index = bisect.bisect_right(BOUNDARIES, score)
    print(f"{score:>8}{index:>14}{GRADES[index][2]:>8}")
print()
print("bisect_right is the correct one here, and getting it wrong is a")
print("one-mark error on every boundary score. A score of exactly 50 must")
print("land in D, not F, so the question is 'how many boundaries is this")
print("score at or above' -- which is bisect_right. Using bisect_left would")
print("put 50 in F and 80 in B, and the bug would look like a rounding")
print("problem rather than an indexing one.")
print()
print("That is the pattern to carry away. An if/elif chain over bands costs")
print("one comparison per band and grows with the number of bands; a bisect")
print("costs log n comparisons and does not care how many bands there are.")
print("For five grades it is a matter of taste. For the 500 tax brackets in")
print("a real payroll system it is not.")
```

```text
a sorted list with duplicates: [40, 55, 55, 55, 70, 82, 82, 95]

  target   bisect_left   bisect_right    copies
------------------------------------------------
      40             0              1         1
      55             1              4         3
      70             4              5         1
      82             5              7         2
      95             7              8         1
      60             4              4         0

The two functions are the same search with `<` and `<=`, and the
difference is only visible where there are duplicates.

  bisect_left  is the number of items *strictly below* the target --
               the index a new copy would take if it had to go
               before the existing ones.
  bisect_right is the number of items *at or below* the target -- the
               index a new copy would take if it had to go after.

So `right - left` is the number of copies present, computed in two
log n searches without counting anything. That is the standard way to
answer 'how many of these are there' on sorted data.

It is also the whole of the 'insort stability' question. To see it, the
items need to be distinguishable while still comparing equal -- so here
is a class that compares on value only:

  starting list: [a40, b55, c55, d55, e70]
  inserting N55, which compares equal to three existing items

  insort_left    -> [a40, N55, b55, c55, d55, e70]
  insort_right   -> [a40, b55, c55, d55, N55, e70]

The new item lands at index 1 with insort_left and at index 4 with
insort_right -- before its equals or after them. Both keep the list
sorted by value, and only one keeps whatever order those three 55s
already had. That is the same stability question as the previous
demo, and the same one-character difference answers it.

Now the use that pays for knowing both. Grade bands are a list of
boundaries and a search, not a chain of comparisons:

  boundaries: [50, 60, 70, 80]
  grades    : ['F', 'D', 'C', 'B', 'A']

   score  bisect_right   grade
--------------------------------
       0             0       F
      49             0       F
      50             1       D
      59             1       D
      60             2       C
      71             3       B
      80             4       A
     100             4       A

bisect_right is the correct one here, and getting it wrong is a
one-mark error on every boundary score. A score of exactly 50 must
land in D, not F, so the question is 'how many boundaries is this
score at or above' -- which is bisect_right. Using bisect_left would
put 50 in F and 80 in B, and the bug would look like a rounding
problem rather than an indexing one.

That is the pattern to carry away. An if/elif chain over bands costs
one comparison per band and grows with the number of bands; a bisect
costs log n comparisons and does not care how many bands there are.
For five grades it is a matter of taste. For the 500 tax brackets in
a real payroll system it is not.
```

`bisect_left` counts the items *strictly below* the target -- the index a new copy would take if it
had to go before its equals. `bisect_right` counts the items *at or below* it -- the index a new copy
would take if it had to go after. Their difference is the number of copies present, computed in two
log n searches without counting anything, which is the standard way to answer "how many of these are
there" on sorted data.

The `insort` pair is the same one-character distinction applied to insertion, and it is the whole of
the stability question from earlier in the chapter. The new item lands at index 1 with `insort_left`
and at index 4 with `insort_right` -- before its three equals or after them. Both keep the list
sorted by value; only one keeps whatever order those three already had.

The grade-band table is the use that pays for knowing both. A score of exactly 50 must land in D, not
F, so the question is "how many boundaries is this score at or above" -- which is `bisect_right`.
Using `bisect_left` would put 50 in F and 80 in B, and because both answers are plausible grades, the
bug would present as a rounding dispute rather than an indexing one.

That is also the argument against the if/elif chain. A chain over bands costs one comparison per band
and grows with the number of bands; a bisect costs log n and does not care how many bands there are.
For five grades that is a matter of taste. For the 500 tax brackets in a real payroll system it is
not.

## Rank and insertion

Two jobs remain, and they are the two that `bisect` is actually for in application code: turning a
value into a position, and placing a value into an order.

Ranking is the first, and the surprise is that "rank" is not one number. A leaderboard with three
people tied at the top has to decide whether the next competitor is fourth or second, and both
answers are defensible.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- rank, and what insertion actually costs.

`bisect` answers one question: how many items are below this value. That is
a rank. `insort` uses the answer to place an item -- a log n search to find
the slot, and then a shift to make room for it. The search is cheap and the
shift is not, and that asymmetry is the whole reason a sorted list is a bad
thing to maintain one insert at a time.
"""
import bisect
import math
import random


class Counted:
    """A value that reports how often it was compared. `sorted` is C and
    cannot be instrumented, but every comparison it makes goes through `<`,
    so this turns the algorithm into an exact number."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value

    def __repr__(self):
        return f"Counted({self.value})"


def count_sorted(values):
    counter = [0]
    result = sorted(Counted(v, counter) for v in values)
    return counter[0], [item.value for item in result]


def shuffled(n, seed=0):
    values = list(range(n))
    random.Random(seed).shuffle(values)
    return values


TIMES = [10.2, 10.2, 10.2, 11.5, 12.0, 12.0, 13.7]


def competition_rank(ordered, value):
    """How many are strictly better, plus one. Ties share a rank and the
    next rank skips, so the ranks read 1, 2, 2, 4 -- which is what a
    leaderboard does and what `bisect_left` gives you for free."""
    return bisect.bisect_left(ordered, value) + 1


def dense_rank(ordered, value):
    """How many *distinct* values are better, plus one: 1, 2, 2, 3. This one
    cannot be a single bisect, because a bisect cannot tell a repeat from a
    new value -- it has to see the whole list."""
    return len({item for item in ordered if item < value}) + 1


print("Part 1 -- a rank is a bisect")
print()
print(f"finishing times, ascending: {TIMES}")
print()
print(f"{'time':>7}{'below':>8}{'competition':>13}{'dense':>8}{'percentile':>12}")
print("-" * 48)
for value in sorted(set(TIMES)):
    below = bisect.bisect_left(TIMES, value)
    print(f"{value:>7.1f}{below:>8}{competition_rank(TIMES, value):>13}"
          f"{dense_rank(TIMES, value):>8}{below / len(TIMES) * 100:>11.0f}%")
print()
print("The two rank columns disagree, and both are correct. They answer")
print("different questions: 'how many people beat me' (competition, which")
print("skips) and 'how many distinct results are better' (dense, which does")
print("not). Pick one, name it in the function, and never mix them in one")
print("table -- that is how a leaderboard ends up with two people at rank 3")
print("and nobody at rank 4.")
print()
print("The 'below' column is the whole mechanism: it is one bisect_left, and")
print("everything else in the table is arithmetic on top of it.")
print()
linear = [sum(1 for item in TIMES if item < value) for value in TIMES]
from_bisect = [bisect.bisect_left(TIMES, value) for value in TIMES]
print(f"  counting linearly  : {linear}")
print(f"  counting by bisect : {from_bisect}")
print(f"  same answer? {linear == from_bisect}")
print()
print("Both give the same numbers -- the difference is that the first reads")
print("every item and the second reads about log2(7) = 3 of them. On a")
print("leaderboard of ten million rows that is three reads against ten")
print("million, for an answer that is identical by construction.")
print()
print()
print("Part 2 -- insertion: a constant search and a shifting bill")
print()


def insort_counted(items, value):
    """Place `value` and report what it cost: one log n search, and then
    `len(items) - index` slots pushed up by one. The second number is the
    one that decides whether this is a good idea."""
    index = bisect.bisect_right(items, value)
    shifts = len(items) - index
    items.insert(index, value)
    return index, shifts


BASIS = list(range(0, 2000, 2))
print(f"inserting one item into a list of {len(BASIS):,} items")
print()
print(f"{'value':>8}{'lands at':>10}{'slots shifted':>15}{'search cost':>13}")
print("-" * 46)
for value in (-1, 499, 999, 1499, 2001):
    items = list(BASIS)
    index, shifts = insort_counted(items, value)
    print(f"{value:>8,}{index:>10,}{shifts:>15,}"
          f"{math.ceil(math.log2(len(BASIS) + 1)):>13}")
print()
print("The right-hand column is identical in all five rows, and that is the")
print("point: the search is logarithmic and barely notices where the item")
print("belongs. The shift column varies by a factor of a thousand -- from")
print("1000 slots to none at all -- because `list.insert` moves everything")
print("above the slot, and a list is a flat array.")
print()
print("So `insort` is O(log n) to find and O(n) to place. It is only worth")
print("using when the list is short, or when you are inserting near the end,")
print("or when the list has to be sorted at every instant. It is not a way to")
print("build a sorted collection.")
print()
print()
print("Part 3 -- the cost of building a sorted list, both ways")
print()


def build_by_insort(values):
    """n inserts, each with its own shift. Returns the total slot moves."""
    items = []
    shifts = 0
    for value in values:
        index = bisect.bisect_right(items, value)
        shifts += len(items) - index
        items.insert(index, value)
    return shifts, items


print(f"{'n':>7}{'insort shifts':>15}{'sorted() cmps':>15}{'ratio':>8}"
      f"{'shifts/n^2':>12}")
print("-" * 57)
results = {}
for n in (100, 400, 1_600, 6_400):
    values = shuffled(n)
    shifts, built = build_by_insort(values)
    comparisons, sorted_once = count_sorted(values)
    results[n] = (shifts, comparisons, built == sorted_once)
    print(f"{n:>7,}{shifts:>15,}{comparisons:>15,}"
          f"{shifts / comparisons:>8.1f}{shifts / n ** 2:>12.2f}")
print()
worst = max(results)
print("Both routes produce the same list, and the ratio between them is not a")
print("constant -- it climbs with n, because one column is n^2 and the other")
print("is n log n. The last column is the tell: the shift total settles at")
print("n^2/4, which is what you get when each of n inserts moves about half")
print("of a list that is on average half full.")
print()
print(f"At n = {worst:,} the insort route has done about")
print(f"{results[worst][0] / results[worst][1]:.0f} times the work of a single sort, and the gap")
print("keeps widening. Append everything and call sorted() once: one pass")
print("to build, one n log n sort, and no shifting at all.")
print()
print("The one case where insort is right is a stream you have to query")
print("between arrivals -- a running median, a live percentile, a 'top 10 of")
print("the last minute'. Then the list has to be correct at every instant,")
print("and you are paying for that rather than for the sorting.")
print()
agreed = [ok for _, _, ok in results.values()]
print(f"  every route agreed on the result: {all(agreed)}")
print(f"  of {len(agreed)} sizes checked: {sum(agreed)} agreed")
```

```text
Part 1 -- a rank is a bisect

finishing times, ascending: [10.2, 10.2, 10.2, 11.5, 12.0, 12.0, 13.7]

   time   below  competition   dense  percentile
------------------------------------------------
   10.2       0            1       1          0%
   11.5       3            4       2         43%
   12.0       4            5       3         57%
   13.7       6            7       4         86%

The two rank columns disagree, and both are correct. They answer
different questions: 'how many people beat me' (competition, which
skips) and 'how many distinct results are better' (dense, which does
not). Pick one, name it in the function, and never mix them in one
table -- that is how a leaderboard ends up with two people at rank 3
and nobody at rank 4.

The 'below' column is the whole mechanism: it is one bisect_left, and
everything else in the table is arithmetic on top of it.

  counting linearly  : [0, 0, 0, 3, 4, 4, 6]
  counting by bisect : [0, 0, 0, 3, 4, 4, 6]
  same answer? True

Both give the same numbers -- the difference is that the first reads
every item and the second reads about log2(7) = 3 of them. On a
leaderboard of ten million rows that is three reads against ten
million, for an answer that is identical by construction.


Part 2 -- insertion: a constant search and a shifting bill

inserting one item into a list of 1,000 items

   value  lands at  slots shifted  search cost
----------------------------------------------
      -1         0          1,000           10
     499       250            750           10
     999       500            500           10
   1,499       750            250           10
   2,001     1,000              0           10

The right-hand column is identical in all five rows, and that is the
point: the search is logarithmic and barely notices where the item
belongs. The shift column varies by a factor of a thousand -- from
1000 slots to none at all -- because `list.insert` moves everything
above the slot, and a list is a flat array.

So `insort` is O(log n) to find and O(n) to place. It is only worth
using when the list is short, or when you are inserting near the end,
or when the list has to be sorted at every instant. It is not a way to
build a sorted collection.


Part 3 -- the cost of building a sorted list, both ways

      n  insort shifts  sorted() cmps   ratio  shifts/n^2
---------------------------------------------------------
    100          2,245            532     4.2        0.22
    400         40,084          2,933    13.7        0.25
  1,600        628,845         14,946    42.1        0.25
  6,400     10,193,346         72,645   140.3        0.25

Both routes produce the same list, and the ratio between them is not a
constant -- it climbs with n, because one column is n^2 and the other
is n log n. The last column is the tell: the shift total settles at
n^2/4, which is what you get when each of n inserts moves about half
of a list that is on average half full.

At n = 6,400 the insort route has done about
140 times the work of a single sort, and the gap
keeps widening. Append everything and call sorted() once: one pass
to build, one n log n sort, and no shifting at all.

The one case where insort is right is a stream you have to query
between arrivals -- a running median, a live percentile, a 'top 10 of
the last minute'. Then the list has to be correct at every instant,
and you are paying for that rather than for the sorting.

  every route agreed on the result: True
  of 4 sizes checked: 4 agreed
```

The two rank columns disagree, and both are correct. Competition rank answers "how many beat me",
plus one -- so the three competitors who finished on 10.2 all rank 1, and the next one down ranks 4,
because ranks 2 and 3 were consumed by the tie. Dense rank answers "how many distinct results are
better", plus one, so it never skips and reads 1, 2, 3, 4 straight down the same rows. The mechanism
underneath is one `bisect_left`; everything else in that table is arithmetic on top of it.

Dense rank cannot be a single bisect, and the reason is worth stating: a bisect can tell you how many
items are below a value, but it cannot tell a repeat from a new value, because that is a property of
the *set* of items below rather than of the position of a boundary. Anything that needs to know
"how many distinct" has to look at the items.

The insertion half is where the cost story pays off. `insort` finds the slot in log n comparisons and
then shifts everything above it -- and the search cost is identical in all five rows of that table
while the shift cost varies by a factor of a thousand, from 1,000 slots to none.

So `insort` is O(log n) to find and O(n) to place. It is worth using when the list is short, when you
are inserting near the end, or when the list has to be sorted at *every instant*. It is not a way to
build a sorted collection, and the third table shows why: at n = 6,400 the insort route has already
done about 140 times the work of one `sorted()` call, and the gap widens with n because one column is
n² and the other is n log n. The `shifts/n²` column settling at 0.25 is the tell -- n²/4 is what you
get when each of n inserts moves about half of a list that is on average half full.

Append everything and call `sorted()` once. One pass to build, one n log n sort, no shifting at all.

## Sorting is often the whole solution

The most valuable habit in this chapter is not about sorting at all. It is asking, before optimising
a nested loop, whether having the data *in order* would make the loop unnecessary.

Here is the clearest example: find every pair in a list that sums to a target.

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- the move that turns an n^2 problem into an n log n one.

A surprising number of problems are really 'get the data in order first'.
Sorting costs n log n, and it buys a scan that replaces a nested loop.
"""
import random

N = 1_000
TARGET = 250


class Counted:
    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value


def distinct_values(n):
    values = list(range(n))
    random.Random(0).shuffle(values)
    return values


VALUES = distinct_values(N)


def pairs_by_brute_force(values, target):
    """Every unordered pair, compared. n(n-1)/2 pairs, which is the cost
    people write by accident because the double loop reads so naturally."""
    operations = 0
    found = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            operations += 1
            if values[i] + values[j] == target:
                found.append(tuple(sorted((values[i], values[j]))))
    return sorted(found), operations


def pairs_by_sorting(values, target):
    """Sort once, then walk inwards from both ends. The walk moves one
    pointer per step, so it cannot exceed n steps."""
    counter = [0]
    items = [Counted(v, counter) for v in values]
    items.sort()
    ordered = [item.value for item in items]
    sort_cost = counter[0]

    operations = 0
    found = []
    low, high = 0, len(ordered) - 1
    while low < high:
        operations += 1
        total = ordered[low] + ordered[high]
        if total == target:
            found.append((ordered[low], ordered[high]))
            low += 1
            high -= 1
        elif total < target:
            low += 1
        else:
            high -= 1
    return sorted(found), sort_cost + operations, sort_cost, operations


def closest_pair_brute_force(values):
    operations = 0
    best = None
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            operations += 1
            gap = abs(values[i] - values[j])
            if best is None or gap < best:
                best = gap
    return best, operations


def closest_pair_by_sorting(values):
    counter = [0]
    items = [Counted(v, counter) for v in values]
    items.sort()
    ordered = [item.value for item in items]
    sort_cost = counter[0]

    operations = 0
    best = None
    for i in range(1, len(ordered)):
        operations += 1
        gap = ordered[i] - ordered[i - 1]
        if best is None or gap < best:
            best = gap
    return best, sort_cost + operations, sort_cost


print(f"every pair summing to {TARGET}, in {N:,} distinct values")
print()
brute_pairs, brute_ops = pairs_by_brute_force(VALUES, TARGET)
sort_pairs, sort_ops, sort_part, walk_part = pairs_by_sorting(VALUES, TARGET)
print(f"{'approach':<34}{'operations':>14}{'per item':>10}")
print("-" * 58)
print(f"{'every pair, nested loop':<34}{brute_ops:>14,}{brute_ops / N:>10.1f}")
print(f"{'sort, then walk inwards':<34}{sort_ops:>14,}{sort_ops / N:>10.1f}")
print(f"{'  of which sorting':<34}{sort_part:>14,}")
print(f"{'  of which the walk':<34}{walk_part:>14,}")
print()
print(f"{'same pairs found':<34}{str(brute_pairs == sort_pairs):>14}")
print(f"{'pairs':<34}{str(brute_pairs[:4]):>14}")
print()
print("The nested loop compares every pair: n(n-1)/2 of them, which is the")
print("definition of quadratic and the reason it does not survive a larger")
print("input. Sorting first costs n log n, and it buys a walk that touches")
print("each item once.")
print()
print("The walk is the part worth remembering. In a sorted list, if the two")
print("ends sum to too little then the smallest value is too small for *any*")
print("partner -- so it can be discarded, and one pointer moves. If they sum")
print("to too much, the largest is too big and it is discarded instead. Each")
print("step eliminates one item permanently, so the walk never exceeds n")
print("steps, however many pairs it finds.")
print()
print("The same move works on any problem where sorting makes a local")
print("decision safe. The closest pair in one dimension is the clearest")
print("example:")
print()
# Floats rather than integers, so the answer is not the boring 'the gap is
# 1 because these are consecutive whole numbers'. Note the single Random
# instance: `random.Random(1).random()` inside the comprehension would build
# a fresh generator each time and return the same first value n times.
_FLOATS = random.Random(1)
FLOATS = [_FLOATS.random() * 100 for _ in range(N)]
brute_best, brute_ops = closest_pair_brute_force(FLOATS)
sort_best, sort_ops, sort_part = closest_pair_by_sorting(FLOATS)
print(f"{'approach':<34}{'operations':>14}{'closest gap':>16}")
print("-" * 64)
print(f"{'every pair, nested loop':<34}{brute_ops:>14,}{brute_best:>16.2e}")
print(f"{'sort, then compare neighbours':<34}{sort_ops:>14,}{sort_best:>16.2e}")
print(f"{'  of which sorting':<34}{sort_part:>14,}")
print(f"{'  same answer':<34}{str(brute_best == sort_best):>16}")
print()
print("In a sorted list the closest pair must be adjacent. That is a")
print("one-sentence argument, and it collapses n^2/2 distance computations")
print("into n-1 subtractions. Not a better constant -- a different class.")
print()
print("That is the habit this chapter is arguing for. Before optimising a")
print("loop, ask whether the data being in order would make the loop")
print("unnecessary. The sort is rarely the expensive part; the nested loop")
print("usually is.")
```

```text
every pair summing to 250, in 1,000 distinct values

approach                              operations  per item
----------------------------------------------------------
every pair, nested loop                  499,500     499.5
sort, then walk inwards                    9,524       9.5
  of which sorting                         8,650
  of which the walk                          874

same pairs found                            True
pairs                             [(0, 250), (1, 249), (2, 248), (3, 247)]

The nested loop compares every pair: n(n-1)/2 of them, which is the
definition of quadratic and the reason it does not survive a larger
input. Sorting first costs n log n, and it buys a walk that touches
each item once.

The walk is the part worth remembering. In a sorted list, if the two
ends sum to too little then the smallest value is too small for *any*
partner -- so it can be discarded, and one pointer moves. If they sum
to too much, the largest is too big and it is discarded instead. Each
step eliminates one item permanently, so the walk never exceeds n
steps, however many pairs it finds.

The same move works on any problem where sorting makes a local
decision safe. The closest pair in one dimension is the clearest
example:

approach                              operations     closest gap
----------------------------------------------------------------
every pair, nested loop                  499,500        1.15e-04
sort, then compare neighbours              9,651        1.15e-04
  of which sorting                         8,652
  same answer                                 True

In a sorted list the closest pair must be adjacent. That is a
one-sentence argument, and it collapses n^2/2 distance computations
into n-1 subtractions. Not a better constant -- a different class.

That is the habit this chapter is arguing for. Before optimising a
loop, ask whether the data being in order would make the loop
unnecessary. The sort is rarely the expensive part; the nested loop
usually is.
```

The nested loop compares every pair -- n(n-1)/2 of them, 499,500 for a thousand items -- which is the
definition of quadratic. Sorting first costs n log n and buys a walk that touches each item once.

The walk is the part to remember. In a sorted list, if the two ends sum to too little, then the
smallest value is too small for *any* partner, so it can be discarded and one pointer moves. If they
sum to too much, the largest is too big and it is discarded instead. Each step eliminates one item
permanently, so the walk never exceeds n steps however many pairs it finds.

The closest-pair demo is the same move on a different problem, and it is the cleaner argument: in a
sorted list the closest pair must be adjacent. That is a one-sentence proof, and it collapses n²/2
distance computations into n-1 subtractions. Note the shape of the numbers -- 499,500 against 9,651,
where the *sorting* is 8,652 of that 9,651. The sort is rarely the expensive part. The nested loop
usually is.

## Choosing, on evidence

One requirement, four implementations, and three of them are wrong in ways that pass review.

The requirement is a leaderboard: highest score first, and ties broken by earliest submission.

:::scenario The leaderboard that sorted by the wrong tie-break
The obvious version is one line, and it looks correct:

```python
rows = sorted(rows, key=lambda row: row[1], reverse=True)
```

It sorts by score, descending. It is also wrong, and it is wrong in a way that no test written
against the current fixture will catch, because the fixture happens to be in submission order. Read
the 91s in the first table below.

Here are all four attempts, side by side:

```python run
#!/usr/bin/env python3
"""Chapter 46 demo -- the multi-key sort, and the three ways to get it wrong.

The requirement is 'highest score first, ties broken by earliest submission'.
Note that the rows below do *not* arrive in submission order -- which is what
makes the naive version wrong in a way nobody notices.
"""
ROWS = [
    ("hal", 91, "2026-03-05"),
    ("bob", 78, "2026-03-01"),
    ("eve", 91, "2026-03-02"),
    ("dee", 78, "2026-03-09"),
    ("cyd", 91, "2026-03-08"),
    ("fay", 65, "2026-03-04"),
    ("gus", 78, "2026-03-07"),
    ("ada", 91, "2026-03-03"),
]


def score(row):
    return row[1]


def submitted(row):
    return row[2]


def show(label, rows):
    print(f"  {label}")
    for name, points, date in rows:
        print(f"    {name:<5}{points:>4}   {date}")
    print()


print("the leaderboard requirement: highest score first, and ties broken by")
print("earliest submission")
print()
show("as the rows arrive", ROWS)

naive = sorted(ROWS, key=score, reverse=True)
show("sorted by score, reverse=True", naive)

wrong = sorted(naive, key=submitted)
show("...then sorted by submission date to fix the ties", wrong)

right = sorted(sorted(ROWS, key=submitted), key=score, reverse=True)
show("submission date first, then score  (correct)", right)

tuple_key = sorted(ROWS, key=lambda row: (-row[1], row[2]))
show("key=lambda row: (-row[1], row[2])", tuple_key)
print(f"  agrees with the two-pass version: {tuple_key == right}")
print()
print("The first version looks right, and it is wrong. The scores are in the")
print("right order, and the four 91s are in arrival order -- hal, eve, cyd,")
print("ada -- where the requirement asks for eve, ada, hal, cyd. Stability")
print("preserved an order nobody asked for.")
print()
print("That is the trap. `sorted` is stable, so a single-key sort silently")
print("inherits whatever order the input happened to be in, and that order")
print("is invisible in the code that does the sorting. It works in every")
print("test where the fixture is already in submission order.")
print()
print("The second version is the fix somebody reaches for after noticing:")
print("sort by score, then sort by the tie-break key. It replaces the wrong")
print("tie order with a completely wrong report -- now ordered by date, with")
print("the 65 sitting above two of the 91s. The score, which is the whole")
print("point of the page, is gone.")
print()
print("The rule is that a stable sort preserves the order it was *given*, so")
print("the last pass decides the primary order. Sort by the least significant")
print("key first and the most significant key last. Each pass can only")
print("rearrange items whose keys differ, so every earlier pass survives")
print("exactly inside the groups the final pass created.")
print()
print("The tuple key gets the same answer in one pass and is the version to")
print("prefer when it is available. Note the negation: `sorted` has no")
print("per-key direction, so 'descending on the score' means negating it")
print("inside the key -- which works for numbers and not much else.")
print()
print("`reverse=True` is no help either, because it reverses *every* key, so")
print("it cannot express 'descending on one and ascending on another'. That")
print("is the case where the two-pass version is not a stylistic choice but")
print("the only correct one.")
print()
print("And then the version that survives code review, because the keys are")
print("in the right order and only the direction is wrong:")
print()
sliced = sorted(ROWS, key=score)[::-1]
show("key=score, then [::-1]", sliced)
print("Same scores in the same order. The four 91s are now ada, cyd, eve,")
print("hal -- which is neither the arrival order nor the submission order,")
print("it is the arrival order reversed. Nothing raises, no test fails, and")
print("the only symptom is an ordering somebody has to notice by reading the")
print("output.")
print()
print("Compare the 91s across all four attempts:")
print()
for label, rows in (("arrival order", ROWS),
                    ("sorted by score", naive),
                    ("score then [::-1]", sliced),
                    ("the requirement", right)):
    names = [row[0] for row in rows if row[1] == 91]
    print(f"  {label:<20}{names}")
print()
print("Only the last line satisfies the requirement, and three of the four")
print("lines are things people write on purpose.")
```

```text
the leaderboard requirement: highest score first, and ties broken by
earliest submission

  as the rows arrive
    hal    91   2026-03-05
    bob    78   2026-03-01
    eve    91   2026-03-02
    dee    78   2026-03-09
    cyd    91   2026-03-08
    fay    65   2026-03-04
    gus    78   2026-03-07
    ada    91   2026-03-03

  sorted by score, reverse=True
    hal    91   2026-03-05
    eve    91   2026-03-02
    cyd    91   2026-03-08
    ada    91   2026-03-03
    bob    78   2026-03-01
    dee    78   2026-03-09
    gus    78   2026-03-07
    fay    65   2026-03-04

  ...then sorted by submission date to fix the ties
    bob    78   2026-03-01
    eve    91   2026-03-02
    ada    91   2026-03-03
    fay    65   2026-03-04
    hal    91   2026-03-05
    gus    78   2026-03-07
    cyd    91   2026-03-08
    dee    78   2026-03-09

  submission date first, then score  (correct)
    eve    91   2026-03-02
    ada    91   2026-03-03
    hal    91   2026-03-05
    cyd    91   2026-03-08
    bob    78   2026-03-01
    gus    78   2026-03-07
    dee    78   2026-03-09
    fay    65   2026-03-04

  key=lambda row: (-row[1], row[2])
    eve    91   2026-03-02
    ada    91   2026-03-03
    hal    91   2026-03-05
    cyd    91   2026-03-08
    bob    78   2026-03-01
    gus    78   2026-03-07
    dee    78   2026-03-09
    fay    65   2026-03-04

  agrees with the two-pass version: True

The first version looks right, and it is wrong. The scores are in the
right order, and the four 91s are in arrival order -- hal, eve, cyd,
ada -- where the requirement asks for eve, ada, hal, cyd. Stability
preserved an order nobody asked for.

That is the trap. `sorted` is stable, so a single-key sort silently
inherits whatever order the input happened to be in, and that order
is invisible in the code that does the sorting. It works in every
test where the fixture is already in submission order.

The second version is the fix somebody reaches for after noticing:
sort by score, then sort by the tie-break key. It replaces the wrong
tie order with a completely wrong report -- now ordered by date, with
the 65 sitting above two of the 91s. The score, which is the whole
point of the page, is gone.

The rule is that a stable sort preserves the order it was *given*, so
the last pass decides the primary order. Sort by the least significant
key first and the most significant key last. Each pass can only
rearrange items whose keys differ, so every earlier pass survives
exactly inside the groups the final pass created.

The tuple key gets the same answer in one pass and is the version to
prefer when it is available. Note the negation: `sorted` has no
per-key direction, so 'descending on the score' means negating it
inside the key -- which works for numbers and not much else.

`reverse=True` is no help either, because it reverses *every* key, so
it cannot express 'descending on one and ascending on another'. That
is the case where the two-pass version is not a stylistic choice but
the only correct one.

And then the version that survives code review, because the keys are
in the right order and only the direction is wrong:

  key=score, then [::-1]
    ada    91   2026-03-03
    cyd    91   2026-03-08
    eve    91   2026-03-02
    hal    91   2026-03-05
    gus    78   2026-03-07
    dee    78   2026-03-09
    bob    78   2026-03-01
    fay    65   2026-03-04

Same scores in the same order. The four 91s are now ada, cyd, eve,
hal -- which is neither the arrival order nor the submission order,
it is the arrival order reversed. Nothing raises, no test fails, and
the only symptom is an ordering somebody has to notice by reading the
output.

Compare the 91s across all four attempts:

  arrival order       ['hal', 'eve', 'cyd', 'ada']
  sorted by score     ['hal', 'eve', 'cyd', 'ada']
  score then [::-1]   ['ada', 'cyd', 'eve', 'hal']
  the requirement     ['eve', 'ada', 'hal', 'cyd']

Only the last line satisfies the requirement, and three of the four
lines are things people write on purpose.
```
:::

:::solution The rule
A stable sort preserves the order it was *given*, so the last pass decides the primary order. Sort by
the **least significant key first** and the **most significant key last**, and every earlier pass
survives inside the groups the final pass creates.

The two-pass version is correct but it is not the version to prefer, because it cannot express
"descending on one key and ascending on another" -- `reverse=True` reverses *every* key. The tuple
key `(-row[1], row[2])` does express it, in one pass, and it is the version to reach for when the
keys are orderable.

Note the negation in that key. `sorted` has no per-key direction, so descending on a number means
negating it inside the key. That works for numbers and for little else -- there is no negation for a
string, which is exactly the case where the multi-pass version stops being a stylistic choice and
becomes the only correct one.
:::

The third attempt in that output is the one that survives code review, and it is worth understanding
why. Sorting by score and then reversing the result keeps the scores in the right order and inverts
every group of ties -- so the output is sorted, plausible, and wrong. Nothing raises. No test fails.
The only symptom is an ordering somebody has to notice by reading the output.

That is the recurring shape of this whole chapter. Sorting and searching have no exceptions to throw,
because every wrong answer is still a valid index, a valid grade, or a valid order.

## Key takeaways

- A comparison sort cannot beat log2(n!) comparisons, and Timsort on scrambled input is within two
  percent of that floor. The remaining wins are all in the input, not the algorithm.
- Count comparisons instead of timing them. A count is a property of the algorithm and the input; a
  timing is a property of the machine. Wrapping values in a class with a counting `__lt__` is how you
  instrument code that lives in C.
- Insertion sort is O(n) on sorted input and O(n²) on reversed input. "Sorting is O(n²)" is not a
  fact about sorting, it is a fact about an input shape.
- Timsort is linear on ascending, descending, two-run, all-equal and nearly-sorted input, and n log n
  only on genuinely scrambled input. Real data is rarely scrambled, which is why it is the default.
- `sorted` is stable, so a single-key sort silently inherits the input's order. `reverse=True`
  reverses the comparison and keeps stability; `[::-1]` reverses the result and destroys it.
- For multi-key sorting, sort by the least significant key first. `reverse=True` cannot express
  mixed directions; a tuple key can, but only when the keys are orderable.
- A key runs n times and a comparator runs about n log n times. Reach for a key, then a richer key,
  then `cmp_to_key` -- and use `cmp_to_key` only when the order of a pair depends on both items.
- Binary search's two classic bugs are `low = middle` (a hang) and `high = middle - 1` in a
  lower-bound search (a silent off-by-one). Keep `high` exclusive in a lower bound and both go away.
- `bisect_left` is the count of items strictly below; `bisect_right` is the count at or below. Their
  difference is the number of copies, and `insort_right` is what keeps duplicates stable.
- `insort` is O(log n) to find and O(n) to place. Never build a sorted collection one insert at a
  time -- append and call `sorted()` once.
- Before optimising a nested loop, ask whether sorting first would make the loop unnecessary. In a
  sorted list the closest pair is adjacent and the two-pointer walk is linear.

## Practice

- [ ] Sort a list of records by three keys -- group ascending, score descending, name ascending --
  as a tuple key and as three successive passes. Then reorder the passes and show the output changes.
  Explain which order is correct and why.
- [ ] Write `rank(samples, value)` returning a `(below, equal, above)` triple using two bisects, and
  a second version that counts with a scan. Check that both agree on the smallest value, the largest,
  a value above everything and a value below everything -- and that every triple sums to n.
- [ ] Write `first_index` and `last_index` by hand, as a lower bound and an upper bound on a list
  with duplicates, then compare both against `bisect_left` and `bisect_right` on the same list.
  Include a target that is not present.
- [ ] Group a list of events by department using `itertools.groupby`, and demonstrate the bug by
  calling it on unsorted input. Then produce the same report with a dict, and say which one you would
  ship and when.
- [ ] Sort version strings like `"1.10"` and `"1.2.3"` correctly, using a key. Then add a
  pre-release suffix (`"1.2.3-rc1"`) and decide between a richer key and `cmp_to_key`.

## Solutions

:::solution Exercise 1
The tuple key is one expression and one pass, and it is correct as written because tuple comparison
is lexicographic. The three-pass version is correct only if the passes run least-significant first:
name, then score, then group. Run them in any other order and the output is still sorted -- by the
last key you used -- with the other two silently discarded.

```python run
#!/usr/bin/env python3
"""Chapter 46 solution 1 -- a three-key sort, two ways, and the wrong way."""
ROWS = [
    ("eve", 91, "eng"),
    ("bob", 78, "ops"),
    ("hal", 91, "ops"),
    ("dee", 78, "eng"),
    ("ada", 91, "eng"),
    ("fay", 65, "ops"),
    ("gus", 78, "ops"),
    ("cyd", 91, "eng"),
]


def by_tuple(rows):
    """One pass. The key is a tuple, so Python compares dept first, then
    -score, then name -- and stops at whichever field differs."""
    return sorted(rows, key=lambda row: (row[2], -row[1], row[0]))


def by_passes(rows):
    """Three passes, least significant key first. Each pass is stable, so
    the order each one establishes survives inside the groups the next one
    creates."""
    ordered = sorted(rows, key=lambda row: row[0])              # name
    ordered = sorted(ordered, key=lambda row: row[1], reverse=True)  # score
    ordered = sorted(ordered, key=lambda row: row[2])           # dept
    return ordered


def by_passes_wrong_order(rows):
    """The same three passes, applied most-significant first."""
    ordered = sorted(rows, key=lambda row: row[2])              # dept
    ordered = sorted(ordered, key=lambda row: row[1], reverse=True)  # score
    ordered = sorted(ordered, key=lambda row: row[0])           # name
    return ordered


def show(label, rows):
    print(f"  {label}")
    for name, points, dept in rows:
        print(f"    {dept:<5}{name:<5}{points:>4}")
    print()


tuple_result = by_tuple(ROWS)
passes_result = by_passes(ROWS)
wrong_result = by_passes_wrong_order(ROWS)

print("sort by department, then by score descending, then by name")
print()
show("key=lambda row: (row[2], -row[1], row[0])", tuple_result)
print(f"  the three-pass version agrees: {tuple_result == passes_result}")
print()
show("the three passes in the wrong order", wrong_result)
print(f"  and that one agrees: {tuple_result == wrong_result}")
print()
print("The tuple key is one expression and one pass. The three-pass version")
print("is three sorts -- three times the work, since each pass is n log n --")
print("and it is correct only if the passes are in the right order.")
print()
print("It is still worth knowing, for two reasons. The first is that a key")
print("must be orderable as a tuple, and mixing directions inside one is")
print("only possible by negating: `-row[1]` works because the score is a")
print("number. There is no negation for a string, so 'department ascending")
print("and name descending' cannot be written as a tuple key at all -- and")
print("then the passes are the only way.")
print()
print("The second reason is that the wrong-order version is not obviously")
print("wrong. All three keys are used, every pass is stable, and the output")
print("is sorted by name. It has simply lost the two keys that mattered.")
print()
print("If you do write the passes, write them in one place with the keys in")
print("a list, least significant first, so the order is visible:")
print()
KEYS = [("name", lambda row: row[0], False),
        ("score", lambda row: row[1], True),
        ("dept", lambda row: row[2], False)]
ordered = list(ROWS)
for label, key, descending in KEYS:
    ordered.sort(key=key, reverse=descending)
    print(f"    after sorting by {label:<6} (descending={descending}): "
          f"{[row[0] for row in ordered]}")
print()
print(f"  agrees with the tuple key: {ordered == tuple_result}")
```

```text
sort by department, then by score descending, then by name

  key=lambda row: (row[2], -row[1], row[0])
    eng  ada    91
    eng  cyd    91
    eng  eve    91
    eng  dee    78
    ops  hal    91
    ops  bob    78
    ops  gus    78
    ops  fay    65

  the three-pass version agrees: True

  the three passes in the wrong order
    eng  ada    91
    ops  bob    78
    eng  cyd    91
    eng  dee    78
    eng  eve    91
    ops  fay    65
    ops  gus    78
    ops  hal    91

  and that one agrees: False

The tuple key is one expression and one pass. The three-pass version
is three sorts -- three times the work, since each pass is n log n --
and it is correct only if the passes are in the right order.

It is still worth knowing, for two reasons. The first is that a key
must be orderable as a tuple, and mixing directions inside one is
only possible by negating: `-row[1]` works because the score is a
number. There is no negation for a string, so 'department ascending
and name descending' cannot be written as a tuple key at all -- and
then the passes are the only way.

The second reason is that the wrong-order version is not obviously
wrong. All three keys are used, every pass is stable, and the output
is sorted by name. It has simply lost the two keys that mattered.

If you do write the passes, write them in one place with the keys in
a list, least significant first, so the order is visible:

    after sorting by name   (descending=False): ['ada', 'bob', 'cyd', 'dee', 'eve', 'fay', 'gus', 'hal']
    after sorting by score  (descending=True): ['ada', 'cyd', 'eve', 'hal', 'bob', 'dee', 'gus', 'fay']
    after sorting by dept   (descending=False): ['ada', 'cyd', 'eve', 'dee', 'hal', 'bob', 'gus', 'fay']

  agrees with the tuple key: True
```
:::

:::solution Exercise 2
`bisect_left` counts the items below and `bisect_right` counts the items at or below, so the number
equal is the difference and the number above is what is left. Every triple sums to n, which is the
check that the two searches were combined correctly.

```python run
#!/usr/bin/env python3
"""Chapter 46 solution 2 -- rank and percentile from two bisects."""
import bisect
import random

N = 200
_rng = random.Random(0)
SAMPLES = sorted(_rng.randrange(0, 1_000) for _ in range(N))


def rank(sorted_items, value):
    """Returns (below, equal, above). Both searches are log n, so this is
    log n for the whole thing -- no counting, no scanning."""
    below = bisect.bisect_left(sorted_items, value)
    above = len(sorted_items) - bisect.bisect_right(sorted_items, value)
    equal = len(sorted_items) - below - above
    return below, equal, above


def percentile(sorted_items, value):
    """The share of items strictly below the value, as a percentage."""
    below = bisect.bisect_left(sorted_items, value)
    return 100 * below / len(sorted_items)


def rank_by_scan(sorted_items, value):
    """The version everybody writes first, for comparison."""
    below = equal = above = 0
    for item in sorted_items:
        if item < value:
            below += 1
        elif item == value:
            equal += 1
        else:
            above += 1
    return below, equal, above


print(f"{N} sorted samples, values from 0 to {SAMPLES[-1]}")
print(f"  first 10: {SAMPLES[:10]}")
print()
print(f"{'value':>7}{'below':>8}{'equal':>8}{'above':>8}{'total':>8}{'percentile':>13}")
print("-" * 52)
for value in (SAMPLES[0], SAMPLES[N // 2], SAMPLES[-1], 999, 0):
    below, equal, above = rank(SAMPLES, value)
    print(f"{value:>7}{below:>8}{equal:>8}{above:>8}{below + equal + above:>8}"
          f"{percentile(SAMPLES, value):>12.1f}%")
print()
print("Every row sums to n, which is the check that the two bisects were")
print("combined correctly. That is the part people get wrong: `bisect_left`")
print("counts the items *below* the value and `bisect_right` counts the items")
print("at or below it, so the number equal is the difference between them and")
print("the number above is what is left.")
print()
print("A value of 999 is above every sample, so below is 200 and percentile")
print("is 100. A value of 0 is at or below all of them, so below is 0. Neither")
print("is a special case in the code -- the searches just return the ends.")
print()
print(f"{'value':>7}{'rank()':>18}{'scan()':>18}  {'agree':>6}")
print("-" * 52)
for value in (SAMPLES[0], SAMPLES[N // 2], SAMPLES[-1], 999, 0):
    print(f"{value:>7}{str(rank(SAMPLES, value)):>18}"
          f"{str(rank_by_scan(SAMPLES, value)):>18}"
          f"  {str(rank(SAMPLES, value) == rank_by_scan(SAMPLES, value)):>6}")
print()
print("The scan is O(n) and the bisects are O(log n), and on 200 items that")
print("is the difference between 200 comparisons and 16. The reason to")
print("prefer the bisects is not the constant, though -- it is that the scan")
print("has three counters to keep consistent and the bisects have none.")
print()
print("One caveat worth stating, because it is a real trap: both of these")
print("assume the list is sorted. Nothing checks. `bisect` on an unsorted")
print("list returns a plausible index and a wrong answer, and no exception is")
print("raised anywhere. Here is the smallest example the search below could")
print("find -- it is searched for rather than asserted, because not every")
print("unsorted list produces a mismatch:")
print()


def first_mismatch(target):
    candidates = ([1, 5, 9, 3, 7], [9, 1, 5, 3, 7], [5, 9, 1, 3, 7],
                  [7, 3, 9, 5, 1], [3, 7, 1, 9, 5])
    for candidate in candidates:
        wrong = bisect.bisect_left(candidate, target)
        right = bisect.bisect_left(sorted(candidate), target)
        if wrong != right:
            return candidate, wrong, right
    raise SystemExit("no mismatch found -- this demo would prove nothing")


UNSORTED, wrong_answer, right_answer = first_mismatch(5)
print(f"  unsorted list         : {UNSORTED}")
print(f"  bisect_left(., 5)     : {wrong_answer}")
print(f"  same values, sorted   : {sorted(UNSORTED)}")
print(f"  bisect_left(., 5)     : {right_answer}")
print()
print("Two items in that list are below 5, so the rank is 2. The unsorted")
print("search returns 1, because it descended into a half that the ordering")
print("it assumed did not exist. Both are valid indices and neither raises,")
print("so the failure is silent -- which is the whole reason to treat 'the")
print("list is sorted' as a precondition you assert rather than hope for.")
print()
print("If you are handing a list to bisect and you did not just sort it,")
print("check it:")
print()
print(f"  all(a <= b for a, b in zip(xs, xs[1:])) -> "
      f"{all(a <= b for a, b in zip(SAMPLES, SAMPLES[1:]))}")
```

```text
200 sorted samples, values from 0 to 991
  first 10: [1, 14, 16, 33, 39, 41, 63, 64, 70, 75]

  value   below   equal   above   total   percentile
----------------------------------------------------
      1       0       1     199     200         0.0%
    560     100       2      98     200        50.0%
    991     199       1       0     200        99.5%
    999     200       0       0     200       100.0%
      0       0       0     200     200         0.0%

Every row sums to n, which is the check that the two bisects were
combined correctly. That is the part people get wrong: `bisect_left`
counts the items *below* the value and `bisect_right` counts the items
at or below it, so the number equal is the difference between them and
the number above is what is left.

A value of 999 is above every sample, so below is 200 and percentile
is 100. A value of 0 is at or below all of them, so below is 0. Neither
is a special case in the code -- the searches just return the ends.

  value            rank()            scan()   agree
----------------------------------------------------
      1       (0, 1, 199)       (0, 1, 199)    True
    560      (100, 2, 98)      (100, 2, 98)    True
    991       (199, 1, 0)       (199, 1, 0)    True
    999       (200, 0, 0)       (200, 0, 0)    True
      0       (0, 0, 200)       (0, 0, 200)    True

The scan is O(n) and the bisects are O(log n), and on 200 items that
is the difference between 200 comparisons and 16. The reason to
prefer the bisects is not the constant, though -- it is that the scan
has three counters to keep consistent and the bisects have none.

One caveat worth stating, because it is a real trap: both of these
assume the list is sorted. Nothing checks. `bisect` on an unsorted
list returns a plausible index and a wrong answer, and no exception is
raised anywhere. Here is the smallest example the search below could
find -- it is searched for rather than asserted, because not every
unsorted list produces a mismatch:

  unsorted list         : [1, 5, 9, 3, 7]
  bisect_left(., 5)     : 1
  same values, sorted   : [1, 3, 5, 7, 9]
  bisect_left(., 5)     : 2

Two items in that list are below 5, so the rank is 2. The unsorted
search returns 1, because it descended into a half that the ordering
it assumed did not exist. Both are valid indices and neither raises,
so the failure is silent -- which is the whole reason to treat 'the
list is sorted' as a precondition you assert rather than hope for.

If you are handing a list to bisect and you did not just sort it,
check it:

  all(a <= b for a, b in zip(xs, xs[1:])) -> True
```
:::

:::solution Exercise 3
Both are the same search with a different comparison. `first_index` finds the boundary between "less
than" and "not less than"; `last_index` finds the boundary between "not greater than" and "greater
than". A boundary is a position, and every list has one -- so there is no not-found case and no
`return -1` anywhere.

```python run
#!/usr/bin/env python3
"""Chapter 46 solution 3 -- first and last index of a value, from `<` alone.

Both searches below use only `<`, which is all `bisect` requires of an item.
Counting the probes shows the two searches are still logarithmic even though
neither of them ever finds the value it is looking for.
"""
import bisect

VALUES = [10, 20, 20, 20, 20, 35, 35, 50, 60, 60, 75]


def first_index(items, target, counter=None):
    """The lower bound: the first index whose item is >= target. Note that
    this never compares for equality -- it only ever asks `items[mid] < x`,
    which is why it works on any type that supports `<`."""
    low, high = 0, len(items)
    while low < high:
        if counter is not None:
            counter[0] += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low


def last_index(items, target, counter=None):
    """The index *after* the last occurrence, which is what bisect_right
    returns. Asking for 'one past the end' instead of 'the last one' is what
    removes the special case for an empty range."""
    low, high = 0, len(items)
    while low < high:
        if counter is not None:
            counter[0] += 1
        middle = (low + high) // 2
        if target < items[middle]:
            high = middle
        else:
            low = middle + 1
    return low


print(f"a sorted list with duplicate runs: {VALUES}")
print()
print(f"{'target':>8}{'first':>8}{'last':>7}{'count':>8}{'slice':>26}"
      f"{'probes':>9}")
print("-" * 68)
for target in (10, 20, 35, 50, 60, 75, 15):
    counter = [0]
    start = first_index(VALUES, target, counter)
    stop = last_index(VALUES, target, counter)
    print(f"{target:>8}{start:>8}{stop:>7}{stop - start:>8}"
          f"{str(VALUES[start:stop]):>26}{counter[0]:>9}")
print()
print("Both searches are O(log n) even though neither one looks for the")
print("value. `first_index` finds the boundary between 'less than' and 'not")
print("less than'; `last_index` finds the boundary between 'not greater than'")
print("and 'greater than'. A boundary is a position, and every list has one,")
print("so there is no not-found case to handle and no `return -1` anywhere.")
print()
print("That is why the pair is the right primitive. A search that returns a")
print("bool has to be written twice to answer 'how many', and the second")
print("version grows its own off-by-one. These two compose into every")
print("question you actually have:")
print()
print("  count of target      stop - start")
print("  is target present    start < stop")
print("  rank of target       start")
print("  the items equal it   items[start:stop]")
print()
print("Two of the rows above are worth naming. Target 15 is not in the list")
print("at all, and both searches still return an answer -- start == stop == 1,")
print("so the count is 0 and the slice is empty. Target 10 is the first item,")
print("so start is 0, which is a valid index and also falsy; code that writes")
print("`if first_index(...)` to test for presence gets that row wrong.")
print()
print(f"{'target':>8}{'my first':>10}{'bisect_left':>14}{'my last':>10}"
      f"{'bisect_right':>15}")
print("-" * 60)
for target in (10, 20, 35, 50, 60, 75, 15):
    print(f"{target:>8}{first_index(VALUES, target):>10}"
          f"{bisect.bisect_left(VALUES, target):>14}"
          f"{last_index(VALUES, target):>10}"
          f"{bisect.bisect_right(VALUES, target):>15}")
print()
print("Which is the honest conclusion: the standard library already has")
print("these, tested, in C, and named after the convention they use. Write")
print("them once by hand so the invariant is yours; then use `bisect`.")
```

```text
a sorted list with duplicate runs: [10, 20, 20, 20, 20, 35, 35, 50, 60, 60, 75]

  target   first   last   count                     slice   probes
--------------------------------------------------------------------
      10       0      1       1                      [10]        8
      20       1      5       4          [20, 20, 20, 20]        7
      35       5      7       2                  [35, 35]        7
      50       7      8       1                      [50]        7
      60       8     10       2                  [60, 60]        7
      75      10     11       1                      [75]        7
      15       1      1       0                        []        8

Both searches are O(log n) even though neither one looks for the
value. `first_index` finds the boundary between 'less than' and 'not
less than'; `last_index` finds the boundary between 'not greater than'
and 'greater than'. A boundary is a position, and every list has one,
so there is no not-found case to handle and no `return -1` anywhere.

That is why the pair is the right primitive. A search that returns a
bool has to be written twice to answer 'how many', and the second
version grows its own off-by-one. These two compose into every
question you actually have:

  count of target      stop - start
  is target present    start < stop
  rank of target       start
  the items equal it   items[start:stop]

Two of the rows above are worth naming. Target 15 is not in the list
at all, and both searches still return an answer -- start == stop == 1,
so the count is 0 and the slice is empty. Target 10 is the first item,
so start is 0, which is a valid index and also falsy; code that writes
`if first_index(...)` to test for presence gets that row wrong.

  target  my first   bisect_left   my last   bisect_right
------------------------------------------------------------
      10         0             0         1              1
      20         1             1         5              5
      35         5             5         7              7
      50         7             7         8              8
      60         8             8        10             10
      75        10            10        11             11
      15         1             1         1              1

Which is the honest conclusion: the standard library already has
these, tested, in C, and named after the convention they use. Write
them once by hand so the invariant is yours; then use `bisect`.
```
:::

:::solution Exercise 4
`groupby` collapses *adjacent* equal keys, so it splits a sequence into runs rather than grouping it.
The sort is not an optimisation, it is what makes the grouping correct. A dict is O(n) and needs no
sort, so use it when you only need the members; use the sort when the *order* of the groups is part
of the output.

```python run
#!/usr/bin/env python3
"""Chapter 46 solution 4 -- grouping with a sort, and the trap in groupby."""
import itertools

EVENTS = [
    ("eng", "ada"),
    ("ops", "bob"),
    ("eng", "cyd"),
    ("ops", "dee"),
    ("eng", "eve"),
    ("ops", "fay"),
    ("eng", "gus"),
]


def groupby_as_is(rows, key):
    """`groupby` collapses *adjacent* equal keys. Given the rows in arrival
    order it returns runs, not groups -- and nothing about the call says so."""
    return [(value, [row[1] for row in group])
            for value, group in itertools.groupby(rows, key=key)]


def grouped(rows, key):
    """The sort is not an optimisation here -- it is what makes the grouping
    correct, because it puts equal keys next to each other."""
    ordered = sorted(rows, key=key)
    return [(value, [row[1] for row in group])
            for value, group in itertools.groupby(ordered, key=key)]


def department(row):
    return row[0]


print(f"events in arrival order: {[row[1] for row in EVENTS]}")
print(f"departments, as they arrive: {[row[0] for row in EVENTS]}")
print()
print("grouping without sorting first -- groupby_as_is(EVENTS, department)")
as_is = groupby_as_is(EVENTS, department)
for value, members in as_is:
    print(f"  {value}: {members}")
print(f"  -> {len(as_is)} 'groups', and "
      f"{sum(1 for value, _ in as_is if value == 'eng')} of them are eng")
print()
print("grouping after sorting by the group key -- grouped(EVENTS, department)")
after = grouped(EVENTS, department)
for value, members in after:
    print(f"  {value}: {members}")
print(f"  -> {len(after)} groups, one per department")
print()
print(f"same answer? {as_is == after}")
print()
print("`itertools.groupby` does not group a sequence. It splits a sequence")
print("into runs of adjacent equal keys, which is a different operation and")
print("a cheaper one -- it never has to hold more than one group in memory.")
print("The name is the whole problem: nothing in the call site says the input")
print("must be sorted, so the unsorted call returns a plausible answer.")
print()
print("Notice that the *members* come back in arrival order, not sorted")
print("order, inside each group. The sort moved whole groups around; the")
print("stable tie-break left the items within a group where they were. So")
print("'sort by the group key, then keep arrival order inside each group' is")
print("what this pair of operations does, and it is exactly what you want")
print("for a report.")
print()
print("The same shape answers 'deduplicate adjacent' and 'find runs':")
print()
RUNS = [1, 1, 2, 2, 2, 5, 1, 1]
print(f"  input runs : {RUNS}")
print(f"  runs       : {[(value, len(list(group))) for value, group in itertools.groupby(RUNS)]}")
print()
print("Two runs of 1, because they are not adjacent -- which is correct for")
print("'find runs' and a bug for 'count occurrences'. The fix is the same in")
print("both cases: decide whether you want runs or groups, and if you want")
print("groups, sort first or reach for a dict.")
print()
counts = {}
for value in RUNS:
    counts[value] = counts.get(value, 0) + 1
print(f"  a dict instead, for counts: {counts}")
print()
print("The dict is O(n) and the sort is O(n log n), so for counting alone")
print("the dict wins. The sort earns its keep when you need the groups in a")
print("specific *order* -- by name, by size, by earliest member -- because")
print("then the ordering is the output, and a dict has no order to give you.")
```

```text
events in arrival order: ['ada', 'bob', 'cyd', 'dee', 'eve', 'fay', 'gus']
departments, as they arrive: ['eng', 'ops', 'eng', 'ops', 'eng', 'ops', 'eng']

grouping without sorting first -- groupby_as_is(EVENTS, department)
  eng: ['ada']
  ops: ['bob']
  eng: ['cyd']
  ops: ['dee']
  eng: ['eve']
  ops: ['fay']
  eng: ['gus']
  -> 7 'groups', and 4 of them are eng

grouping after sorting by the group key -- grouped(EVENTS, department)
  eng: ['ada', 'cyd', 'eve', 'gus']
  ops: ['bob', 'dee', 'fay']
  -> 2 groups, one per department

same answer? False

`itertools.groupby` does not group a sequence. It splits a sequence
into runs of adjacent equal keys, which is a different operation and
a cheaper one -- it never has to hold more than one group in memory.
The name is the whole problem: nothing in the call site says the input
must be sorted, so the unsorted call returns a plausible answer.

Notice that the *members* come back in arrival order, not sorted
order, inside each group. The sort moved whole groups around; the
stable tie-break left the items within a group where they were. So
'sort by the group key, then keep arrival order inside each group' is
what this pair of operations does, and it is exactly what you want
for a report.

The same shape answers 'deduplicate adjacent' and 'find runs':

  input runs : [1, 1, 2, 2, 2, 5, 1, 1]
  runs       : [(1, 2), (2, 3), (5, 1), (1, 2)]

Two runs of 1, because they are not adjacent -- which is correct for
'find runs' and a bug for 'count occurrences'. The fix is the same in
both cases: decide whether you want runs or groups, and if you want
groups, sort first or reach for a dict.

  a dict instead, for counts: {1: 4, 2: 3, 5: 1}

The dict is O(n) and the sort is O(n log n), so for counting alone
the dict wins. The sort earns its keep when you need the groups in a
specific *order* -- by name, by size, by earliest member -- because
then the ordering is the output, and a dict has no order to give you.
```
:::

:::solution Exercise 5
A key that turns each version into a tuple of integers fixes the `"1.10"` before `"1.9"` bug and
costs nothing. A pre-release suffix breaks it, because `int("3-rc1")` is not a number -- but the fix
is still a richer key, encoding the rule "no suffix outranks any suffix, then compare the suffix
text". `cmp_to_key` is only needed when no such encoding exists.

```python run
#!/usr/bin/env python3
"""Chapter 46 solution 5 -- sorting version strings, where a key gets hard."""
import functools

VERSIONS = ["1.9", "1.10", "1.2.3", "1.2", "2.0", "1.10.1", "1.2.10", "1.2.2"]


def numeric_key(text):
    """Split on dots and convert each part to an int. Works for plain
    numeric versions and nothing else."""
    return tuple(int(part) for part in text.split("."))


def compare_numeric(left, right):
    left_parts = numeric_key(left)
    right_parts = numeric_key(right)
    if left_parts < right_parts:
        return -1
    if left_parts > right_parts:
        return 1
    return 0


print(f"versions: {VERSIONS}")
print()
print("sorted() with no key sorts them as text:")
print(f"  {sorted(VERSIONS)}")
print()
print("'1.10' comes before '1.9', because '1' < '9' at the third character.")
print("Every version-comparison bug in every build system starts here.")
print()
print("sorted() with a numeric key:")
print(f"  {sorted(VERSIONS, key=numeric_key)}")
print()
print("Now 1.9 precedes 1.10, which is what the version number means. The")
print("key turns each version into a tuple of ints, and tuple comparison")
print("does the rest -- element by element, and a shorter tuple that is a")
print("prefix of a longer one sorts first.")
print()
print("That last rule is worth seeing, because it is a decision rather than")
print("an accident:")
print()
print(f"  {'1.2':<8} -> {numeric_key('1.2')}")
print(f"  {'1.2.0':<8} -> {numeric_key('1.2.0')}")
print(f"  1.2 sorts before 1.2.0 : {numeric_key('1.2') < numeric_key('1.2.0')}")
print()
print("Whether those two are the same release is a policy question, and the")
print("tuple key has answered it silently in favour of 'different'. If your")
print("policy says they are equal, pad the tuples to the same length first.")
print()
print("cmp_to_key gives the same answer as the key, and costs more:")
print()
print(f"  {sorted(VERSIONS, key=functools.cmp_to_key(compare_numeric))}")
print(f"  agrees with the key version: "
      f"{sorted(VERSIONS, key=functools.cmp_to_key(compare_numeric)) == sorted(VERSIONS, key=numeric_key)}")
print()
print("So far the key has won on every count. Here is where it stops being")
print("easy -- pre-release suffixes:")
print()
RELEASES = ["1.2.3", "1.2.3-rc1", "1.2.3-rc2", "1.2.3-beta", "1.2.4"]
print(f"  {RELEASES}")
try:
    sorted(RELEASES, key=numeric_key)
except ValueError as error:
    print(f"  numeric_key raises: ValueError: {error}")
print()
print("`int('3-rc1')` is not a number. The key can still be written -- it")
print("just has to encode the ordering rule, which for semantic versioning")
print("is 'no suffix outranks any suffix, then compare the suffix text':")
print()


def release_key(text):
    if "-" not in text:
        return (numeric_key(text), 1, "")
    base, suffix = text.split("-", 1)
    return (numeric_key(base), 0, suffix)


print(f"  {sorted(RELEASES, key=release_key)}")
print()
print("That works and it is still a key, so the sort stays single-pass and")
print("the rule stays in one function. cmp_to_key is the escape hatch for the")
print("cases where no such encoding exists -- when the comparison depends on")
print("the pair rather than on each item alone, as in the largest-number")
print("problem earlier in this chapter.")
print()
print("The order to try them in is: a key, then a richer key, then")
print("cmp_to_key. Reaching for cmp_to_key first costs a factor of log n in")
print("calls and gives up the ability to look at one item and say where it")
print("belongs.")
```

```text
versions: ['1.9', '1.10', '1.2.3', '1.2', '2.0', '1.10.1', '1.2.10', '1.2.2']

sorted() with no key sorts them as text:
  ['1.10', '1.10.1', '1.2', '1.2.10', '1.2.2', '1.2.3', '1.9', '2.0']

'1.10' comes before '1.9', because '1' < '9' at the third character.
Every version-comparison bug in every build system starts here.

sorted() with a numeric key:
  ['1.2', '1.2.2', '1.2.3', '1.2.10', '1.9', '1.10', '1.10.1', '2.0']

Now 1.9 precedes 1.10, which is what the version number means. The
key turns each version into a tuple of ints, and tuple comparison
does the rest -- element by element, and a shorter tuple that is a
prefix of a longer one sorts first.

That last rule is worth seeing, because it is a decision rather than
an accident:

  1.2      -> (1, 2)
  1.2.0    -> (1, 2, 0)
  1.2 sorts before 1.2.0 : True

Whether those two are the same release is a policy question, and the
tuple key has answered it silently in favour of 'different'. If your
policy says they are equal, pad the tuples to the same length first.

cmp_to_key gives the same answer as the key, and costs more:

  ['1.2', '1.2.2', '1.2.3', '1.2.10', '1.9', '1.10', '1.10.1', '2.0']
  agrees with the key version: True

So far the key has won on every count. Here is where it stops being
easy -- pre-release suffixes:

  ['1.2.3', '1.2.3-rc1', '1.2.3-rc2', '1.2.3-beta', '1.2.4']
  numeric_key raises: ValueError: invalid literal for int() with base 10: '3-rc1'

`int('3-rc1')` is not a number. The key can still be written -- it
just has to encode the ordering rule, which for semantic versioning
is 'no suffix outranks any suffix, then compare the suffix text':

  ['1.2.3-beta', '1.2.3-rc1', '1.2.3-rc2', '1.2.3', '1.2.4']

That works and it is still a key, so the sort stays single-pass and
the rule stays in one function. cmp_to_key is the escape hatch for the
cases where no such encoding exists -- when the comparison depends on
the pair rather than on each item alone, as in the largest-number
problem earlier in this chapter.

The order to try them in is: a key, then a richer key, then
cmp_to_key. Reaching for cmp_to_key first costs a factor of log n in
calls and gives up the ability to look at one item and say where it
belongs.
```
:::
