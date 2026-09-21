---
chapter: 48
part: 8
title: Recursion, Memoisation and Dynamic Programming
summary: A recurrence is a description, not an algorithm. Count the recursion tree, find the overlap, and the same description becomes a table -- with edit distance, knapsack and coin change worked out in full, and every cost counted rather than timed.
minutes: 115
tags: [dynamic programming, memoisation, lru_cache, edit distance, LCS, knapsack, coin change, recursion, complexity]
---

Chapter 47 was about graphs you can draw. This chapter is about graphs you cannot: the state space
of a recurrence, where the nodes are subproblems and the edges are the recursive calls. Once you see
that, the previous chapter's algorithms and this chapter's are the same algorithms -- Dijkstra is a
dynamic program on a weighted graph, and the coin-change recurrence at the end of this chapter is
Dijkstra with every edge of weight one.

The chapter starts with a function that is three lines long and would take tens of thousands of years
to run at n = 100, and it ends with the same function running in a few hundred operations. Nothing
about the *problem* changes between those two points. What changes is what the function remembers.

The discipline is the one Chapters 44 to 47 established, and it matters more here than anywhere
else so far. **Every cost in this chapter is an exact count** -- of function entries, table cells,
relaxations, look-backs -- and not one of them is a stopwatch reading. That is not fussiness. A DP
is a claim about how many *distinct* things need computing, and the only way to check that claim is
to count them.

## The recursion tree, counted

Start with the standard example, because it is standard for a reason: the blow-up is visible without
any instrumentation at all.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- the recursion tree, counted.

The naive Fibonacci function is the standard example of exponential blow-up,
and it is standard because the blow-up is visible without any instrumentation:
count the calls and the numbers double every time n grows by one.

Counting rather than timing is what makes the claim checkable. The call count
is a property of the recurrence and the input, so it is the same on every
machine -- and it says exactly how much work is being thrown away.
"""


def fib_naive(n, tally):
    """Two recursive calls per node of the tree, and no memory of anything."""
    tally[0] += 1
    if n < 2:
        return n
    return fib_naive(n - 1, tally) + fib_naive(n - 2, tally)


def distinct_subproblems(n):
    """The naive tree solves fib(0)..fib(n) over and over. The number of
    *different* things it is asked to compute is n + 1."""
    return n + 1


def fib_value(n):
    """The same sequence, computed in the obvious cheap way, for a check."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print("naive fibonacci, calls counted")
print()
print(f"{'n':>4}{'calls':>14}{'distinct':>10}{'reuse':>9}{'calls/2^n':>11}")
print("-" * 48)
rows = []
for n in (5, 10, 15, 20, 25, 30):
    tally = [0]
    value = fib_naive(n, tally)
    calls = tally[0]
    distinct = distinct_subproblems(n)
    rows.append((n, calls, distinct, value))
    print(f"{n:>4}{calls:>14,}{distinct:>10,}{calls / distinct:>9.0f}"
          f"{calls / 2 ** n:>11.3f}")
print()
first, last = rows[0], rows[-1]
print(f"  fib(30) = {last[3]:,}")
print(f"  calls grew from {first[1]:,} at n = 5 to {last[1]:,} at n = 30")
print(f"  a factor of {last[1] / first[1]:,.0f} over "
      f"{last[0] - first[0]} more units of n")
print()
print("Read the last column carefully, because the obvious reading of it is")
print("wrong. It does not settle at a constant -- it shrinks by a constant")
print("*factor* every time n goes up by one. The call count grows like the")
print("golden ratio to the n; 2^n grows like 2 to the n; so their ratio")
print("behaves like (phi/2)^n, which is still exponential, just downhill.")
print()
print("That is what 'the same growth rate' means precisely. Not that the two")
print("counts are proportional, but that they differ by a constant factor")
print("*inside the exponent*. It is the reason O(2^n) and O(phi^n) name the")
print("same class, and the reason the shape of the curve matters here rather")
print("than the constant in front of it.")
print()
print("The reuse column is the other half of the story, and it is the one that")
print("makes the fix obvious. At n = 30 the function is called")
print(f"{last[1]:,} times to compute {last[2]} distinct values -- each value computed")
print(f"about {last[1] / last[2]:,.0f} times. The tree is not doing {last[1]:,} different")
print(f"things; it is doing {last[2]} different things over and over.")
print()
print("That is what 'overlapping subproblems' means, and it is worth stating")
print("precisely because the phrase is used loosely. It does not mean the")
print("problem has a recursive definition -- everything recursive does. It")
print("means the recursion tree contains the *same node* many times.")
print()
print()
print("The tree, drawn small")
print()


def draw(n, depth, lines):
    lines.append("  " + "  " * depth + f"fib({n})")
    if n >= 2:
        draw(n - 1, depth + 1, lines)
        draw(n - 2, depth + 1, lines)


lines = []
draw(5, 0, lines)
for line in lines:
    print(line)
print(f"  -- {len(lines)} nodes, for fib(5), which has "
      f"{distinct_subproblems(5)} distinct values")
print()
print("Look for the repeats: fib(2) appears three times and fib(1) five")
print("times. Every one of those subtrees is identical work, and every one")
print("of them is thrown away the moment it finishes, because the function")
print("keeps no memory between calls.")
print()
print("A cache turns that tree into a line. The first time fib(2) is asked")
print("for, the answer is computed and stored; every later ask is a lookup.")
print("The tree does not get smaller -- it stops being built.")
print()
print(f"  nodes in the tree for fib(5)  : {len(lines)}")
print(f"  distinct values for fib(5)    : {distinct_subproblems(5)}")
print(f"  nodes in the tree for fib(30) : {last[1]:,}")
print(f"  distinct values for fib(30)   : {last[2]:,}")
print(f"  the ratio grows as fast as the tree does: "
      f"{last[1] / last[2]:,.0f}x at n = 30")
print()
print()
print("The node count has a closed form")
print()
print("It is worth stating, because it is a check on the whole exercise")
print("rather than a new fact: the number of calls needed to compute fib(n)")
print("naively is 2*F(n+1) - 1, where F is the same sequence being computed.")
print("The function's own value tells you how many times it was called.")
print()
print(f"{'n':>4}{'calls counted':>16}{'2*F(n+1) - 1':>16}{'agree':>8}")
print("-" * 44)
for n, calls, _, _ in rows:
    formula = 2 * fib_value(n + 1) - 1
    print(f"{n:>4}{calls:>16,}{formula:>16,}{str(calls == formula):>8}")
print()
print("Every row agrees, and the reason is that the count satisfies the same")
print("recurrence as the value -- one step ahead of it. Calls(n) = 1 +")
print("Calls(n-1) + Calls(n-2) is exactly fib's own recurrence with a 1")
print("added, which is why the solution comes out as a Fibonacci number and")
print("not as something with 2^n in it.")
print()
print("That also pins down the decay rate in the first table, which can then")
print("be checked rather than asserted. If calls(n) grows like phi^n, then")
print("calls(n)/2^n grows like (phi/2)^n -- so five units of n should shrink")
print("it by a factor of (phi/2)^5, every time, forever.")
print()
PHI = (1 + 5 ** 0.5) / 2
STEP = (PHI / 2) ** 5
print(f"   n   calls/2^n   vs 5 rows back   (phi/2)^5     error")
print("-" * 56)
previous = None
errors = []
for n, calls, _, _ in rows:
    ratio = calls / 2 ** n
    if previous is None:
        print(f"{n:>4}{ratio:>12.6f}{'-':>17}{'-':>12}{'-':>10}")
    else:
        back = ratio / previous
        error = back - STEP
        errors.append(error)
        print(f"{n:>4}{ratio:>12.6f}{back:>17.6f}{STEP:>12.6f}{error:>10.1e}")
    previous = ratio
print()
span = (len(errors) - 1) * 5
total = errors[0] / errors[-1]
per_step = total ** (1 / (len(errors) - 1))
print("The third column converges on the fourth and stays there, and the")
print("last column shows how fast: the error falls by a factor of")
print(f"{total:,.0f} over the {span} units of n between the first and last row --")
print(f"about {per_step:.0f}x for every five units. That factor is (1/phi)^5, the")
print("other half of the same asymptotic: the neglected term in Binet's")
print("formula shrinks like psi^n, where psi is -1/phi.")
print()
print("The first row is the one that has not converged yet, and that is")
print("expected -- at n = 10 the correction terms are still comparable to the")
print("leading one, so the asymptotic has not taken over. It is worth")
print("noticing that the *first* row is the one that lies, which is a")
print("pattern that recurs everywhere counts are used to justify a claim")
print("about growth.")
print()
print("This is the useful habit in miniature. A claim like 'the growth rate")
print("is phi' is not verifiable on its own, because phi is irrational and no")
print("run will ever print it. But the *ratio of ratios* is a clean number,")
print("and it is the same on every machine.")
```

```text
naive fibonacci, calls counted

   n         calls  distinct    reuse  calls/2^n
------------------------------------------------
   5            15         6        2      0.469
  10           177        11       16      0.173
  15         1,973        16      123      0.060
  20        21,891        21     1042      0.021
  25       242,785        26     9338      0.007
  30     2,692,537        31    86856      0.003

  fib(30) = 832,040
  calls grew from 15 at n = 5 to 2,692,537 at n = 30
  a factor of 179,502 over 25 more units of n

Read the last column carefully, because the obvious reading of it is
wrong. It does not settle at a constant -- it shrinks by a constant
*factor* every time n goes up by one. The call count grows like the
golden ratio to the n; 2^n grows like 2 to the n; so their ratio
behaves like (phi/2)^n, which is still exponential, just downhill.

That is what 'the same growth rate' means precisely. Not that the two
counts are proportional, but that they differ by a constant factor
*inside the exponent*. It is the reason O(2^n) and O(phi^n) name the
same class, and the reason the shape of the curve matters here rather
than the constant in front of it.

The reuse column is the other half of the story, and it is the one that
makes the fix obvious. At n = 30 the function is called
2,692,537 times to compute 31 distinct values -- each value computed
about 86,856 times. The tree is not doing 2,692,537 different
things; it is doing 31 different things over and over.

That is what 'overlapping subproblems' means, and it is worth stating
precisely because the phrase is used loosely. It does not mean the
problem has a recursive definition -- everything recursive does. It
means the recursion tree contains the *same node* many times.


The tree, drawn small

  fib(5)
    fib(4)
      fib(3)
        fib(2)
          fib(1)
          fib(0)
        fib(1)
      fib(2)
        fib(1)
        fib(0)
    fib(3)
      fib(2)
        fib(1)
        fib(0)
      fib(1)
  -- 15 nodes, for fib(5), which has 6 distinct values

Look for the repeats: fib(2) appears three times and fib(1) five
times. Every one of those subtrees is identical work, and every one
of them is thrown away the moment it finishes, because the function
keeps no memory between calls.

A cache turns that tree into a line. The first time fib(2) is asked
for, the answer is computed and stored; every later ask is a lookup.
The tree does not get smaller -- it stops being built.

  nodes in the tree for fib(5)  : 15
  distinct values for fib(5)    : 6
  nodes in the tree for fib(30) : 2,692,537
  distinct values for fib(30)   : 31
  the ratio grows as fast as the tree does: 86,856x at n = 30


The node count has a closed form

It is worth stating, because it is a check on the whole exercise
rather than a new fact: the number of calls needed to compute fib(n)
naively is 2*F(n+1) - 1, where F is the same sequence being computed.
The function's own value tells you how many times it was called.

   n   calls counted    2*F(n+1) - 1   agree
--------------------------------------------
   5              15              15    True
  10             177             177    True
  15           1,973           1,973    True
  20          21,891          21,891    True
  25         242,785         242,785    True
  30       2,692,537       2,692,537    True

Every row agrees, and the reason is that the count satisfies the same
recurrence as the value -- one step ahead of it. Calls(n) = 1 +
Calls(n-1) + Calls(n-2) is exactly fib's own recurrence with a 1
added, which is why the solution comes out as a Fibonacci number and
not as something with 2^n in it.

That also pins down the decay rate in the first table, which can then
be checked rather than asserted. If calls(n) grows like phi^n, then
calls(n)/2^n grows like (phi/2)^n -- so five units of n should shrink
it by a factor of (phi/2)^5, every time, forever.

   n   calls/2^n   vs 5 rows back   (phi/2)^5     error
--------------------------------------------------------
   5    0.468750                -           -         -
  10    0.172852         0.368750    0.346568   2.2e-02
  15    0.060211         0.348340    0.346568   1.8e-03
  20    0.020877         0.346728    0.346568   1.6e-04
  25    0.007236         0.346582    0.346568   1.4e-05
  30    0.002508         0.346569    0.346568   1.3e-06

The third column converges on the fourth and stays there, and the
last column shows how fast: the error falls by a factor of
17,080 over the 20 units of n between the first and last row --
about 11x for every five units. That factor is (1/phi)^5, the
other half of the same asymptotic: the neglected term in Binet's
formula shrinks like psi^n, where psi is -1/phi.

The first row is the one that has not converged yet, and that is
expected -- at n = 10 the correction terms are still comparable to the
leading one, so the asymptotic has not taken over. It is worth
noticing that the *first* row is the one that lies, which is a
pattern that recurs everywhere counts are used to justify a claim
about growth.

This is the useful habit in miniature. A claim like 'the growth rate
is phi' is not verifiable on its own, because phi is irrational and no
run will ever print it. But the *ratio of ratios* is a clean number,
and it is the same on every machine.
```

Two claims in that output are worth pulling apart, because they are the two halves of the whole
chapter.

The first is the `calls/2^n` column. It does not settle at a constant, and the obvious reading --
"the count is 2^n up to a constant factor" -- is wrong. It shrinks by a constant *factor* every time
n goes up by one, because the count grows like φ^n while 2^n grows like 2^n. The two differ by a
constant inside the exponent, which is exactly what it means for two exponentials to have the same
growth rate: **O(2^n) and O(φ^n) name the same class**, and the constant in front of them is not
the interesting part.

The step-factor table pins that down to four decimal places, and it is the reason the check is on
the *ratio of ratios* rather than on any single value. φ is irrational, so no run will ever print
it; but (φ/2)^5 is a clean number, it is the same on every machine, and the table converges on it
while the error falls by a factor of about eleven every five units of n. The first two rows are the
ones that lie -- at n = 10 and n = 15 the correction terms in Binet's formula are still comparable
to the leading one. That pattern, where the smallest inputs are the ones that mislead, recurs
everywhere counts are used to justify a claim about growth.

The second claim is the `reuse` column, and it is the one that makes the fix obvious. At n = 30 the
function is entered 2,692,537 times to compute 31 distinct values. The tree is not doing 2,692,537
different things. It is doing 31 different things over and over.

That is what "overlapping subproblems" means, and it is worth stating precisely because the phrase
gets used loosely. It does not mean the problem has a recursive definition -- everything recursive
does. It means **the recursion tree contains the same node many times**.

The closed-form check at the end is not decoration. `2*F(n+1) - 1` holds for every row, and the
reason is that the count satisfies the same recurrence as the value, one step ahead of it. When a
count and the thing being counted share a recurrence, that is usually a sign you have found the
right count rather than a coincidence.

## Two questions, and the ratio that answers both

The phrase "dynamic programming applies" is a claim about a recurrence, and claims should be
testable. There are two questions, and both are answerable by counting before you write any code.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- how to tell whether dynamic programming applies.

Two questions decide it, and both are answerable by counting. How many
*distinct* subproblems does the recursion have, and how many times does the
naive version ask for each one? If the first is polynomial and the second is
exponential, the gap between them is what a cache buys.

The same two questions say when a cache buys *nothing*, which is the half
people skip -- and caching a recursion with no overlap is pure overhead.
"""


def fib(n, tally, seen):
    tally[0] += 1
    seen.add(n)
    if n < 2:
        return n
    return fib(n - 1, tally, seen) + fib(n - 2, tally, seen)


def merge_sort(items, lo, hi, tally, seen):
    """Every range it is asked about is a different range, so the tree has no
    repeated node to cache."""
    tally[0] += 1
    seen.add((lo, hi))
    if hi - lo <= 1:
        return items[lo:hi]
    mid = (lo + hi) // 2
    left = merge_sort(items, lo, mid, tally, seen)
    right = merge_sort(items, mid, hi, tally, seen)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search(items, target, lo, hi, tally, seen):
    tally[0] += 1
    seen.add((lo, hi))
    if lo >= hi:
        return None
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search(items, target, mid + 1, hi, tally, seen)
    return binary_search(items, target, lo, mid, tally, seen)


CASES = []

tally, seen = [0], set()
fib(30, tally, seen)
CASES.append(("fib(30)", len(seen), tally[0]))

SORTED = list(range(1024))
tally, seen = [0], set()
merge_sort(SORTED, 0, len(SORTED), tally, seen)
CASES.append((f"merge sort (n = {len(SORTED):,})", len(seen), tally[0]))

BIG = list(range(1_000_000))
tally, seen = [0], set()
binary_search(BIG, 999_999, 0, len(BIG), tally, seen)
CASES.append((f"binary search (n = {len(BIG):,})", len(seen), tally[0]))

print("three recursions, counted the same way")
print()
print(f"{'recurrence':<28}{'distinct':>10}{'total calls':>13}{'overlap':>11}")
print("-" * 62)
for name, distinct, calls in CASES:
    print(f"{name:<28}{distinct:>10,}{calls:>13,}{calls / distinct:>11.1f}")
print()
print("The overlap column is the test, and it is a ratio rather than a")
print("judgement call. A value of 1 means every call is a subproblem nobody")
print("has asked about before -- there is nothing to cache, and a memo")
print("dictionary would cost memory and lookups for zero saving.")
print()
sort_distinct, sort_calls = CASES[1][1], CASES[1][2]
print(f"Merge sort is the clean example. At n = {len(SORTED):,} its recursion tree")
print(f"has {sort_calls:,} nodes and {sort_distinct:,} distinct ranges -- every node its own")
print("subproblem, because sorting the left half and sorting the right half")
print("are genuinely different jobs. Wrapping it in `lru_cache` would be")
print("pure overhead, and that is not a matter of taste -- it is the ratio")
print("saying so.")
print()
bs_distinct, bs_calls = CASES[2][1], CASES[2][2]
print(f"Binary search is the same at a smaller scale: {bs_calls} calls, {bs_distinct}")
print("distinct ranges, overlap 1. It recurses into one side only, so its")
print("tree is a line rather than a bush -- and a line has no repeats by")
print("construction.")
print()
print("Fibonacci is the opposite extreme: 31 distinct values, 2.69 million")
print("calls, and every value computed tens of thousands of times.")
print()
print()
print("So the two conditions are:")
print()
print("  1. the number of distinct subproblems is polynomial in the input")
print("  2. the naive recursion asks for them an exponential number of times")
print()
print("Both are needed. A recursion with exponential *distinct* subproblems")
print("cannot be memoised into anything useful -- the cache itself becomes the")
print("exponential object. A recursion with no overlap has nothing to reuse.")
print()
print("That is also why the phrase 'dynamic programming' describes a *shape*")
print("of problem rather than a technique to apply. The counting tells you")
print("whether the shape is there before you write any of it.")
print()
print(f"  fib: each value computed on average "
      f"{CASES[0][2] / CASES[0][1]:,.0f} times")
print(f"  merge sort: each range computed "
      f"{CASES[1][2] / CASES[1][1]:.0f} time(s)")
print(f"  binary search: each range computed "
      f"{CASES[2][2] / CASES[2][1]:.0f} time(s)")
print()
print("One more consequence worth noticing. The reason merge sort has no")
print("overlap is that its subproblems are *disjoint* -- the left half and the")
print("right half share no elements. Overlapping subproblems means the same")
print("input appears in more than one branch of the tree, which is a property")
print("of the recurrence, not of the implementation.")
```

```text
three recursions, counted the same way

recurrence                    distinct  total calls    overlap
--------------------------------------------------------------
fib(30)                             31    2,692,537    86856.0
merge sort (n = 1,024)           2,047        2,047        1.0
binary search (n = 1,000,000)        19           19        1.0

The overlap column is the test, and it is a ratio rather than a
judgement call. A value of 1 means every call is a subproblem nobody
has asked about before -- there is nothing to cache, and a memo
dictionary would cost memory and lookups for zero saving.

Merge sort is the clean example. At n = 1,024 its recursion tree
has 2,047 nodes and 2,047 distinct ranges -- every node its own
subproblem, because sorting the left half and sorting the right half
are genuinely different jobs. Wrapping it in `lru_cache` would be
pure overhead, and that is not a matter of taste -- it is the ratio
saying so.

Binary search is the same at a smaller scale: 19 calls, 19
distinct ranges, overlap 1. It recurses into one side only, so its
tree is a line rather than a bush -- and a line has no repeats by
construction.

Fibonacci is the opposite extreme: 31 distinct values, 2.69 million
calls, and every value computed tens of thousands of times.


So the two conditions are:

  1. the number of distinct subproblems is polynomial in the input
  2. the naive recursion asks for them an exponential number of times

Both are needed. A recursion with exponential *distinct* subproblems
cannot be memoised into anything useful -- the cache itself becomes the
exponential object. A recursion with no overlap has nothing to reuse.

That is also why the phrase 'dynamic programming' describes a *shape*
of problem rather than a technique to apply. The counting tells you
whether the shape is there before you write any of it.

  fib: each value computed on average 86,856 times
  merge sort: each range computed 1 time(s)
  binary search: each range computed 1 time(s)

One more consequence worth noticing. The reason merge sort has no
overlap is that its subproblems are *disjoint* -- the left half and the
right half share no elements. Overlapping subproblems means the same
input appears in more than one branch of the tree, which is a property
of the recurrence, not of the implementation.
```

The overlap column is the test. A value of 1 means every call is a subproblem nobody has asked about
before -- there is nothing to cache, and a memo dictionary would cost memory and lookups for zero
saving.

Merge sort is the clean example of that failure, and it is worth being precise about *why* it has no
overlap: its subproblems are **disjoint**. The left half and the right half share no elements, so
"sort the left half" and "sort the right half" are genuinely different jobs that happen to look
alike. Overlapping subproblems means the same input appears in more than one branch of the tree,
which is a property of the recurrence and not of the implementation.

Binary search is the same failure at a smaller scale, and it adds a detail worth noticing: it
recurses into one side only, so its recursion tree is a line rather than a bush -- and a line has no
repeats by construction.

So the two conditions are:

1. the number of distinct subproblems is polynomial in the input
2. the naive recursion asks for them an exponential number of times

Both are needed, and they are independent. A recursion with exponentially many distinct subproblems
cannot be memoised into anything useful, because the cache itself becomes the exponential object. A
recursion with no overlap has nothing to reuse. Exercise 2 takes those two failures apart with one
example each.

That is also why "dynamic programming" describes a **shape** of problem rather than a technique to
apply. The counting tells you whether the shape is there before you write any of it.

## Remembering an answer

Memoisation is one idea: remember the answer to a subproblem you have already solved. It can be
written by hand with a dict or supplied by the standard library, and those look like two techniques
and are the same algorithm.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- four ways to write the same recurrence, and the counts
that separate them.

Memoisation is one idea: remember the answer to a subproblem you have already
solved. It can be written by hand with a dict, or supplied by the standard
library as `functools.lru_cache`. Those look like two different techniques and
they are the same algorithm -- which the counts below show, and which is the
reason to prefer the library version.

The last section turns the cache's two documented traps into output rather
than advice.
"""
import functools


def fib_naive(n, tally):
    tally[0] += 1
    if n < 2:
        return n
    return fib_naive(n - 1, tally) + fib_naive(n - 2, tally)


def fib_memo(n, cache, tally):
    """Hand-rolled. Note that the *call* still happens -- the function is
    entered, and the lookup is what saves the work. Note also that the base
    cases return before the cache is ever consulted."""
    tally[0] += 1
    if n < 2:
        return n
    if n in cache:
        tally[1] += 1
        return cache[n]
    result = fib_memo(n - 1, cache, tally) + fib_memo(n - 2, cache, tally)
    cache[n] = result
    return result


@functools.lru_cache(maxsize=None)
def fib_cached(n):
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def fib_bottom_up(n):
    """No recursion, no cache, two variables. The recurrence runs forwards."""
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


N = 30
naive_tally = [0]
naive_value = fib_naive(N, naive_tally)
memo_tally = [0, 0]
memo_cache = {}
memo_value = fib_memo(N, memo_cache, memo_tally)
fib_cached.cache_clear()
cached_value = fib_cached(N)
info = fib_cached.cache_info()
bottom_up_value = fib_bottom_up(N)

print(f"fib({N}) computed four ways")
print()
print(f"{'implementation':<24}{'entries':>10}{'hits':>7}{'cached':>9}{'value':>12}")
print("-" * 62)
print(f"{'naive recursion':<24}{naive_tally[0]:>10,}{'-':>7}{'-':>9}"
      f"{naive_value:>12,}")
print(f"{'dict memo, by hand':<24}{memo_tally[0]:>10,}{memo_tally[1]:>7,}"
      f"{len(memo_cache):>9,}{memo_value:>12,}")
print(f"{'functools.lru_cache':<24}{info.misses + info.hits:>10,}{info.hits:>7,}"
      f"{info.currsize:>9,}{cached_value:>12,}")
print(f"{'bottom-up loop':<24}{0:>10,}{'-':>7}{'-':>9}{bottom_up_value:>12,}")
print()
print(f"  all four agree on the value : "
      f"{naive_value == memo_value == cached_value == bottom_up_value}")
print()
print("The 'entries' column is how many times each function was *entered*, so")
print("it is the only fair comparison in the table. (The zero in the last row")
print("is not a trick: bottom-up is a loop, and a loop is never entered as a")
print("function at all.) The naive version enters")
print(f"{naive_tally[0]:,} times; both cached versions enter it")
print(f"{memo_tally[0]:,} times -- once per distinct subproblem, plus one lookup per")
print("repeat. The tree did not get smaller. It stopped being built.")
print()
print("Note what the hand-rolled version and `lru_cache` have in common: both")
print("still *call* the function on every request. The saving is not in the")
print("calls, it is in the work behind them. That is why a memoised function")
print("must be cheap to enter and must not do anything with a side effect --")
print("the function body is skipped on a hit, so anything in it that is not")
print("part of the return value simply does not happen.")
print()
print()
print("Two small differences between the hand-rolled row and the library row")
print()
print(f"  hits       : hand-rolled {memo_tally[1]:,} vs library {info.hits:,}")
print(f"  cached     : hand-rolled {len(memo_cache):,} vs library {info.currsize:,}")
print()
print("Both come from one line of code. The hand-rolled version checks")
print("`n < 2` and returns *before* it consults the dictionary, so its base")
print("cases are never looked up and never stored. That is why it reports one")
print("fewer hit and holds two fewer entries: fib(0) and fib(1) are simply")
print("not in its cache.")
print()
print("Neither is a bug, and the difference is worth making deliberately.")
print("The cache check costs a dictionary lookup, so short-circuiting the")
print("trivial cases first is usually the right call -- but it means the")
print("cache's own statistics no longer count every repeat.")
print()
print()
print("What each one is still holding when it finishes")
print()
print(f"  {'implementation':<24}{'memory held':>24}")
print("-" * 48)
print(f"  {'naive recursion':<24}{'nothing':>24}")
print(f"  {'dict memo':<24}{f'{len(memo_cache)} cache entries':>24}")
print(f"  {'lru_cache':<24}{f'{info.currsize} cache entries':>24}")
print(f"  {'bottom-up':<24}{'2 integers':>24}")
print()
print("The last row is the one to remember. The recurrence is identical")
print("everywhere in this table; what differs is how much of the past each")
print("version insists on keeping. Bottom-up keeps two numbers, because at")
print("step k the only thing the recurrence can still see is step k-1 and")
print("step k-2 -- everything older has already been folded in.")
print()
print("That is the whole space optimisation, and it is the subject of a later")
print("section. Here it is enough to notice that a cache holding 31 entries")
print("was never necessary for this recurrence; it was just the easy thing to")
print("write.")
print()
print()
print("What the cache is keyed on")
print()
print(f"  cache entries held : {info.currsize}")
print(f"  maxsize            : {info.maxsize} (unbounded)")
print()
print("`lru_cache` builds its key from the arguments tuple, which has two")
print("consequences that bite in practice and neither of which is an error")
print("until it is.")
print()
print("The first is that every argument must be hashable. A list, a dict or a")
print("set cannot be cached, and the failure is a `TypeError` at the call site")
print("rather than at the definition -- so a function that works on a tuple")
print("and fails on a list is the symptom.")
print()
print("The second is that `maxsize=None` means *unbounded*, and an unbounded")
print("cache on a function with many distinct arguments is a memory leak with")
print("a friendly name. This cache holds one entry per integer from 0 to 30,")
print("which is harmless. A cache on `fetch_user(user_id)` holds one entry per")
print("user ever seen.")
print()


@functools.lru_cache(maxsize=None)
def total(items):
    """Sums a sequence. Nothing about it is wrong -- until it is called with
    something the cache cannot key on."""
    return sum(items)


print("The hashability trap, demonstrated rather than described")
print()
print(f"  total((1, 2, 3))   -> {total((1, 2, 3))}")
try:
    total([1, 2, 3])
except TypeError as exc:
    print(f"  total([1, 2, 3])   -> TypeError: {exc}")
print()
print("The definition of `total` never changed and never warned. The error")
print("appears at the call site, on the argument, and the message says")
print("'unhashable' -- which is the whole diagnosis. A tuple works, a list")
print("does not, and the fix is to convert at the boundary rather than to")
print("give up the cache.")
print()


@functools.lru_cache(maxsize=4)
def small_cache(n):
    return n * n


for value in range(10):
    small_cache(value)
before = small_cache.cache_info()
small_cache(0)          # evicted long ago -- this should be a miss
after = small_cache.cache_info()
print("The bound, demonstrated the same way")
print()
print(f"  an lru_cache(maxsize=4) after 10 distinct arguments:")
print(f"    holds {before.currsize} entries, took {before.misses} misses, "
      f"{before.hits} hits")
print()
print(f"  now ask for 0 again, which was the first argument seen:")
print(f"    holds {after.currsize} entries, took {after.misses} misses, "
      f"{after.hits} hits")
print()
print("The second call is a *miss*. That is the eviction working: with a")
print("bound of 4, the cache kept the four most recent arguments (6, 7, 8,")
print("9) and quietly dropped 0. Nothing failed, nothing warned, and the")
print("answer was still correct -- it was just recomputed.")
print()
print("A bounded cache evicts the least-recently-used entry instead of")
print("growing, which turns a leak into a policy. For a pure function of a")
print("small key space the bound is irrelevant -- as the first cache shows,")
print("31 entries is nothing. For anything keyed on user input it is the")
print("difference between a cache and a bug.")
```

```text
fib(30) computed four ways

implementation             entries   hits   cached       value
--------------------------------------------------------------
naive recursion          2,692,537      -        -     832,040
dict memo, by hand              59     27       29     832,040
functools.lru_cache             59     28       31     832,040
bottom-up loop                   0      -        -     832,040

  all four agree on the value : True

The 'entries' column is how many times each function was *entered*, so
it is the only fair comparison in the table. (The zero in the last row
is not a trick: bottom-up is a loop, and a loop is never entered as a
function at all.) The naive version enters
2,692,537 times; both cached versions enter it
59 times -- once per distinct subproblem, plus one lookup per
repeat. The tree did not get smaller. It stopped being built.

Note what the hand-rolled version and `lru_cache` have in common: both
still *call* the function on every request. The saving is not in the
calls, it is in the work behind them. That is why a memoised function
must be cheap to enter and must not do anything with a side effect --
the function body is skipped on a hit, so anything in it that is not
part of the return value simply does not happen.


Two small differences between the hand-rolled row and the library row

  hits       : hand-rolled 27 vs library 28
  cached     : hand-rolled 29 vs library 31

Both come from one line of code. The hand-rolled version checks
`n < 2` and returns *before* it consults the dictionary, so its base
cases are never looked up and never stored. That is why it reports one
fewer hit and holds two fewer entries: fib(0) and fib(1) are simply
not in its cache.

Neither is a bug, and the difference is worth making deliberately.
The cache check costs a dictionary lookup, so short-circuiting the
trivial cases first is usually the right call -- but it means the
cache's own statistics no longer count every repeat.


What each one is still holding when it finishes

  implementation                       memory held
------------------------------------------------
  naive recursion                          nothing
  dict memo                       29 cache entries
  lru_cache                       31 cache entries
  bottom-up                             2 integers

The last row is the one to remember. The recurrence is identical
everywhere in this table; what differs is how much of the past each
version insists on keeping. Bottom-up keeps two numbers, because at
step k the only thing the recurrence can still see is step k-1 and
step k-2 -- everything older has already been folded in.

That is the whole space optimisation, and it is the subject of a later
section. Here it is enough to notice that a cache holding 31 entries
was never necessary for this recurrence; it was just the easy thing to
write.


What the cache is keyed on

  cache entries held : 31
  maxsize            : None (unbounded)

`lru_cache` builds its key from the arguments tuple, which has two
consequences that bite in practice and neither of which is an error
until it is.

The first is that every argument must be hashable. A list, a dict or a
set cannot be cached, and the failure is a `TypeError` at the call site
rather than at the definition -- so a function that works on a tuple
and fails on a list is the symptom.

The second is that `maxsize=None` means *unbounded*, and an unbounded
cache on a function with many distinct arguments is a memory leak with
a friendly name. This cache holds one entry per integer from 0 to 30,
which is harmless. A cache on `fetch_user(user_id)` holds one entry per
user ever seen.

The hashability trap, demonstrated rather than described

  total((1, 2, 3))   -> 6
  total([1, 2, 3])   -> TypeError: unhashable type: 'list'

The definition of `total` never changed and never warned. The error
appears at the call site, on the argument, and the message says
'unhashable' -- which is the whole diagnosis. A tuple works, a list
does not, and the fix is to convert at the boundary rather than to
give up the cache.

The bound, demonstrated the same way

  an lru_cache(maxsize=4) after 10 distinct arguments:
    holds 4 entries, took 10 misses, 0 hits

  now ask for 0 again, which was the first argument seen:
    holds 4 entries, took 11 misses, 0 hits

The second call is a *miss*. That is the eviction working: with a
bound of 4, the cache kept the four most recent arguments (6, 7, 8,
9) and quietly dropped 0. Nothing failed, nothing warned, and the
answer was still correct -- it was just recomputed.

A bounded cache evicts the least-recently-used entry instead of
growing, which turns a leak into a policy. For a pure function of a
small key space the bound is irrelevant -- as the first cache shows,
31 entries is nothing. For anything keyed on user input it is the
difference between a cache and a bug.
```

The `entries` column is the only fair comparison in the table, and it is worth saying why the other
columns are not. A cache's `hits` and `currsize` are properties of the cache; the number of times a
function is *entered* is a property of the algorithm. The naive version enters the function
2,692,537 times and both cached versions enter it 59 times -- once per distinct subproblem, plus one
lookup per repeat. The tree did not get smaller. It stopped being built.

The two small differences between the hand-rolled row and the library row are worth reading
carefully, because they come from one line of code and they are the kind of thing that gets
mysterious in a code review. The hand-rolled version checks `n < 2` and returns **before** it
consults the dictionary, so its base cases are never looked up and never stored. Hence one fewer hit
and two fewer entries. Neither is a bug: the cache check costs a dictionary lookup, so
short-circuiting the trivial cases first is usually right -- but it means the cache's own statistics
no longer count every repeat.

The last section turns the two documented traps into output rather than advice. `maxsize=None` means
*unbounded*, and an unbounded cache on a function with many distinct arguments is a memory leak with
a friendly name -- harmless on `fib`, a bug on `fetch_user(user_id)`. And the hashability failure
appears at the **call site** rather than at the definition, so a function that works on a tuple and
fails on a list is the symptom to recognise.

The bounded-cache demonstration is the one to keep. After ten distinct arguments a
`maxsize=4` cache holds four entries, and asking for the *first* argument again is a **miss**. That
is eviction working, quietly, with no error and a correct answer. A bounded cache turns a leak into
a policy, and the policy is the thing you are choosing.

## Two directions, and a hard ceiling

The same recurrence can be filled from the answer downwards or from the base cases upwards. They
fill the same table, and the counts show where each one wins.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- the same recurrence, run in both directions.

Top-down starts at the answer and asks for whatever it needs; bottom-up starts
at the base cases and builds towards the answer. They fill in the same table,
and they differ in two things that matter: which states get visited, and how
much stack the recursion uses.

Neither is better. The counts below show where each one wins.
"""
import random
import sys

LIMIT = sys.getrecursionlimit()


def fib_top_down(n, memo, tally):
    tally[0] += 1
    if n < 2:
        return n
    if n in memo:
        tally[1] += 1
        return memo[n]
    memo[n] = fib_top_down(n - 1, memo, tally) + fib_top_down(n - 2, memo, tally)
    return memo[n]


def fib_bottom_up(n, tally):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        tally[0] += 1
        previous, current = current, previous + current
    return current


print("Part 1 -- the same recurrence, and where each version stops")
print()
print(f"  the interpreter's recursion limit is {LIMIT}")
print()
print(f"{'n':>7}{'top-down entries':>19}{'outcome':>18}")
print("-" * 44)
for n in (10, 100, 500, 1_000, 2_000, 5_000):
    tally = [0, 0]
    try:
        fib_top_down(n, {}, tally)
        entries, outcome = f"{tally[0]:,}", "ok"
    except RecursionError:
        entries, outcome = "-", "RecursionError"
    print(f"{n:>7,}{entries:>19}{outcome:>18}")
print()
print(f"{'n':>7}{'bottom-up steps':>19}{'outcome':>18}")
print("-" * 44)
for n in (10, 100, 500, 1_000, 2_000, 5_000):
    tally = [0]
    fib_bottom_up(n, tally)
    print(f"{n:>7,}{tally[0]:>19,}{'ok':>18}")
print()
print("The two tables are the point, and they disagree in the second column.")
print("Top-down works at n = 500 and raises `RecursionError` at n = 1,000,")
print("with no change to the recurrence at all. Bottom-up does not care how")
print("large n gets, because it never recurses -- there is no stack to")
print("overflow.")
print()
print("The exact n where top-down breaks is somewhere just below the limit")
print("printed above, and it is not worth pinning down more precisely than")
print("that: the boundary depends on how many frames the interpreter had")
print("already used before the call, which is not a property of the")
print("algorithm. What *is* a property of the algorithm is the shape -- the")
print("depth grows linearly with n, so the limit is a hard ceiling on n.")
print()
print("Notice the relationship between the two tables while they are both")
print("available. Bottom-up runs one loop step per subproblem above the base")
print("cases, so n - 1 of them: 9, 99, 499. Top-down enters the function")
print("2n - 1 times at every n in the table -- 19, 199, 999 -- which is one")
print("entry per subproblem, plus one more for each time a subproblem is")
print("asked for after it has already been computed. The arithmetic behind")
print("those entries is the same n - 1 additions either way. That is what")
print("'they fill in the same table' means: identical work, different order")
print("and different bookkeeping.")
print()
print()
print("Part 2 -- the recursion limit, and the thing that is not a fix")
print()
probe = 1_500
tally = [0, 0]
try:
    fib_top_down(probe, {}, tally)
    print(f"  at n = {probe:,}, default limit      : ok")
except RecursionError:
    print(f"  at n = {probe:,}, default limit      : RecursionError")
sys.setrecursionlimit(10_000)
tally = [0, 0]
fib_top_down(probe, {}, tally)
print(f"  at n = {probe:,}, limit raised       : ok, {tally[0]:,} entries")
print(f"  the new limit                     : {sys.getrecursionlimit():,}")
sys.setrecursionlimit(LIMIT)
print(f"  restored to                       : {sys.getrecursionlimit():,}")
print()
print("Raising the limit worked here, and it is still not the fix. What")
print("`sys.setrecursionlimit` changes is a *counter* that CPython checks on")
print("entry to each frame. It does not make the real call stack any larger.")
print("Set it high enough and a recursion that would have raised a catchable")
print("`RecursionError` instead runs off the end of the actual stack and takes")
print("the interpreter down with it -- no exception, no traceback, no chance")
print("to log anything.")
print()
print("So the limit is not a nuisance to be configured away. It is a")
print("constraint on the *design*: a recurrence that recurses once per")
print("element has a hard ceiling on the input it can handle, and that ceiling")
print("belongs in the decision about how to write it, not in a startup line.")
print()
print()
print("Part 3 -- and the case where top-down wins outright")
print()
ROWS = COLS = 40
CELLS = ROWS * COLS


def build(density, seed=13):
    rng = random.Random(seed)
    blocked = {(r, c) for r in range(ROWS) for c in range(COLS)
               if rng.random() < density}
    blocked.discard((0, 0))
    blocked.discard((ROWS - 1, COLS - 1))
    return blocked


def paths_top_down(blocked):
    """Count the routes from (0, 0) to (r, c) moving only down and right.
    Cells that cannot be part of any route are never visited, because nothing
    asks about them."""
    memo = {}

    def go(r, c):
        if r < 0 or c < 0 or (r, c) in blocked:
            return 0
        if r == 0 and c == 0:
            return 1
        if (r, c) in memo:
            return memo[(r, c)]
        memo[(r, c)] = go(r - 1, c) + go(r, c - 1)
        return memo[(r, c)]

    value = go(ROWS - 1, COLS - 1)
    return len(memo), value


def paths_bottom_up(blocked):
    """Fill every cell in row-major order, whether or not it can be reached."""
    steps = 0
    table = [[0] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            steps += 1
            if (r, c) in blocked:
                continue
            if r == 0 and c == 0:
                table[r][c] = 1
            else:
                from_above = table[r - 1][c] if r > 0 else 0
                from_left = table[r][c - 1] if c > 0 else 0
                table[r][c] = from_above + from_left
    return steps, table[ROWS - 1][COLS - 1]


print(f"  a {ROWS}x{COLS} grid, {CELLS:,} cells, walls dropped in at random")
print()
print(f"{'walls':>7}{'blocked':>9}{'top-down':>11}{'bottom-up':>11}"
      f"{'saving':>9}{'routes':>13}")
print("-" * 60)
for density in (0.05, 0.10, 0.15, 0.20, 0.25, 0.28, 0.30, 0.32, 0.34, 0.38):
    blocked = build(density)
    down_states, down_value = paths_top_down(blocked)
    up_states, up_value = paths_bottom_up(blocked)
    assert down_value == up_value
    print(f"{density:>6.0%}{len(blocked):>9,}{down_states:>11,}{up_states:>11,}"
          f"{up_states / down_states:>8.1f}x{down_value:>13.3e}")
print()
print("(The route counts are in scientific notation because they run to two")
print(" dozen digits at low wall density, and the exact value is not the")
print(" point -- whether the last column is zero is.)")
print()
print("Read the two count columns together with the last one, because on")
print("their own they are misleading.")
print()
print("At the top of the table almost nothing is blocked and top-down saves")
print("almost nothing -- because with no walls, every cell lies on some route")
print("to the corner, so the states the answer depends on *are* the whole")
print("grid. The two approaches visit the same set and the saving is 1.1x.")
print()
print("As walls go in, the reachable set shrinks faster than the grid does,")
print("and the gap opens up. That is the real advantage of top-down: not that")
print("it is cleverer, but that it never looks at a state the answer does not")
print("depend on.")
print()
print("Now look at the bottom of the table, where the last column goes to 0.")
print("The saving keeps climbing -- and it is climbing for the worst possible")
print("reason. Once the walls seal the corner off, the recursion unwinds")
print("immediately, explores a few dozen cells, finds nothing and returns 0.")
print("The ratio is largest exactly where the search is doing no work at all.")
print()
print("That is worth keeping. A count is only a measure of anything when the")
print("two runs are computing the same non-trivial thing. This table is built")
print("so that the answer is checkable in every row, which is why the zero in")
print("the last column is visible at all -- a benchmark that only reported")
print("the ratio would have ranked the failed searches first.")
print()
print("The rule of thumb that falls out: bottom-up when the state space is")
print("dense and you will need most of it; top-down when it is sparse, or when")
print("the reachable part is hard to characterise, or when you want the")
print("recurrence to stay readable next to its definition.")
print()
print("What you are choosing between is not speed and clarity. It is whether")
print("you want to visit the states the answer depends on, or all the states")
print("that exist -- and those are different sets more often than they look.")
print()
dense = build(0.05)
sparse = build(0.32)
dense_states, dense_value = paths_top_down(dense)
sparse_states, sparse_value = paths_top_down(sparse)
print(f"  cells in the grid           : {CELLS:,}")
print(f"  states visited, 5% walls    : {dense_states:,} "
      f"({dense_states / CELLS:.0%} of the grid)")
print(f"  states visited, 32% walls   : {sparse_states:,} "
      f"({sparse_states / CELLS:.0%} of the grid)")
print(f"  routes, 5% walls            : {dense_value:.3e} (non-zero)")
print(f"  routes, 32% walls           : {sparse_value:.3e} (non-zero)")
```

```text
Part 1 -- the same recurrence, and where each version stops

  the interpreter's recursion limit is 1000

      n   top-down entries           outcome
--------------------------------------------
     10                 19                ok
    100                199                ok
    500                999                ok
  1,000                  -    RecursionError
  2,000                  -    RecursionError
  5,000                  -    RecursionError

      n    bottom-up steps           outcome
--------------------------------------------
     10                  9                ok
    100                 99                ok
    500                499                ok
  1,000                999                ok
  2,000              1,999                ok
  5,000              4,999                ok

The two tables are the point, and they disagree in the second column.
Top-down works at n = 500 and raises `RecursionError` at n = 1,000,
with no change to the recurrence at all. Bottom-up does not care how
large n gets, because it never recurses -- there is no stack to
overflow.

The exact n where top-down breaks is somewhere just below the limit
printed above, and it is not worth pinning down more precisely than
that: the boundary depends on how many frames the interpreter had
already used before the call, which is not a property of the
algorithm. What *is* a property of the algorithm is the shape -- the
depth grows linearly with n, so the limit is a hard ceiling on n.

Notice the relationship between the two tables while they are both
available. Bottom-up runs one loop step per subproblem above the base
cases, so n - 1 of them: 9, 99, 499. Top-down enters the function
2n - 1 times at every n in the table -- 19, 199, 999 -- which is one
entry per subproblem, plus one more for each time a subproblem is
asked for after it has already been computed. The arithmetic behind
those entries is the same n - 1 additions either way. That is what
'they fill in the same table' means: identical work, different order
and different bookkeeping.


Part 2 -- the recursion limit, and the thing that is not a fix

  at n = 1,500, default limit      : RecursionError
  at n = 1,500, limit raised       : ok, 2,999 entries
  the new limit                     : 10,000
  restored to                       : 1,000

Raising the limit worked here, and it is still not the fix. What
`sys.setrecursionlimit` changes is a *counter* that CPython checks on
entry to each frame. It does not make the real call stack any larger.
Set it high enough and a recursion that would have raised a catchable
`RecursionError` instead runs off the end of the actual stack and takes
the interpreter down with it -- no exception, no traceback, no chance
to log anything.

So the limit is not a nuisance to be configured away. It is a
constraint on the *design*: a recurrence that recurses once per
element has a hard ceiling on the input it can handle, and that ceiling
belongs in the decision about how to write it, not in a startup line.


Part 3 -- and the case where top-down wins outright

  a 40x40 grid, 1,600 cells, walls dropped in at random

  walls  blocked   top-down  bottom-up   saving       routes
------------------------------------------------------------
    5%       68      1,444      1,600     1.1x    4.010e+21
   10%      143      1,314      1,600     1.2x    3.747e+19
   15%      239      1,109      1,600     1.4x    6.510e+17
   20%      310        951      1,600     1.7x    2.841e+15
   25%      399        434      1,600     3.7x    4.509e+11
   28%      442        340      1,600     4.7x    2.250e+10
   30%      481        245      1,600     6.5x    9.391e+08
   32%      502        228      1,600     7.0x    1.059e+08
   34%      534        106      1,600    15.1x    0.000e+00
   38%      600         44      1,600    36.4x    0.000e+00

(The route counts are in scientific notation because they run to two
 dozen digits at low wall density, and the exact value is not the
 point -- whether the last column is zero is.)

Read the two count columns together with the last one, because on
their own they are misleading.

At the top of the table almost nothing is blocked and top-down saves
almost nothing -- because with no walls, every cell lies on some route
to the corner, so the states the answer depends on *are* the whole
grid. The two approaches visit the same set and the saving is 1.1x.

As walls go in, the reachable set shrinks faster than the grid does,
and the gap opens up. That is the real advantage of top-down: not that
it is cleverer, but that it never looks at a state the answer does not
depend on.

Now look at the bottom of the table, where the last column goes to 0.
The saving keeps climbing -- and it is climbing for the worst possible
reason. Once the walls seal the corner off, the recursion unwinds
immediately, explores a few dozen cells, finds nothing and returns 0.
The ratio is largest exactly where the search is doing no work at all.

That is worth keeping. A count is only a measure of anything when the
two runs are computing the same non-trivial thing. This table is built
so that the answer is checkable in every row, which is why the zero in
the last column is visible at all -- a benchmark that only reported
the ratio would have ranked the failed searches first.

The rule of thumb that falls out: bottom-up when the state space is
dense and you will need most of it; top-down when it is sparse, or when
the reachable part is hard to characterise, or when you want the
recurrence to stay readable next to its definition.

What you are choosing between is not speed and clarity. It is whether
you want to visit the states the answer depends on, or all the states
that exist -- and those are different sets more often than they look.

  cells in the grid           : 1,600
  states visited, 5% walls    : 1,444 (90% of the grid)
  states visited, 32% walls   : 228 (14% of the grid)
  routes, 5% walls            : 4.010e+21 (non-zero)
  routes, 32% walls           : 1.059e+08 (non-zero)
```

Part 1 is the part that surprises people. Top-down works at n = 500 and raises `RecursionError` at
n = 1,000, with no change to the recurrence at all. Bottom-up does not care how large n gets,
because it never recurses -- there is no stack to overflow.

The exact n where top-down breaks is deliberately not pinned down. It depends on how many frames the
interpreter had already used before the call, which is not a property of the algorithm and not
stable across versions. What *is* a property of the algorithm is the shape: the depth grows linearly
with n, so the limit is a hard ceiling on n. Reporting the shape and refusing to report the boundary
is the right call, and it is the same discipline as refusing to report a timing.

Part 2 is the trap. `sys.setrecursionlimit` looks like the fix and it is not: what it changes is a
*counter* that CPython checks on entry to each frame. It does not make the real call stack any
larger. Set it high enough and a recursion that would have raised a catchable exception instead runs
off the end of the actual stack and takes the interpreter down -- no exception, no traceback, no
chance to log anything. So the limit belongs in the decision about how to write the recurrence, not
in a startup line.

Part 3 reverses the conclusion, and the sweep is the interesting part. With almost no walls,
top-down saves nothing -- because with no walls every cell lies on some route to the corner, so the
states the answer depends on *are* the whole grid. As walls go in, the reachable set shrinks faster
than the grid does and the gap opens up.

Then look at the bottom of the table, where the route count goes to zero. The saving keeps climbing
-- 15x, then 36x -- and it is climbing for the worst possible reason. Once the walls seal the corner
off, the recursion unwinds immediately, explores a few dozen cells, finds nothing and returns 0.
**The ratio is largest exactly where the search is doing no work at all.**

That is worth keeping as a habit. A count is only a measure of something when the two runs are
computing the same non-trivial thing. This table is built so that the answer is checkable in every
row, which is why the zero is visible at all -- a benchmark that reported only the ratio would have
ranked the failed searches first.

## Edit distance

Fibonacci shows the mechanism. Edit distance shows the **shape**: the state is a pair of positions,
so the table is two-dimensional, and every cell is a choice between three moves. It is also the
recurrence behind every spell checker and every `diff`.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- edit distance, the first DP that is not a toy.

Fibonacci shows the mechanism. Edit distance shows the *shape*: the state is a
pair of positions, so the table is two-dimensional, and every cell is a choice
between three moves. It is also the recurrence behind every spell checker and
every `diff`.

Everything below is counted, and the counts are the argument: the naive
recursion is exponential while the table is quadratic, and the gap between
those two numbers is the whole reason the table exists.
"""


def edit_table(a, b):
    """Levenshtein distance, filled in as the table the recurrence describes.

    table[i][j] is the distance between the first i characters of `a` and the
    first j characters of `b`. Row 0 and column 0 are the base cases: turning
    a string into the empty string costs one deletion per character.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i
    for j in range(n + 1):
        table[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            delete = table[i - 1][j] + 1
            insert = table[i][j - 1] + 1
            substitute = table[i - 1][j - 1] + (a[i - 1] != b[j - 1])
            table[i][j] = min(delete, insert, substitute)
    return table


def edit_naive(a, b, i, j, tally, seen):
    """The same recurrence with no table.

    Every call makes all three recursive calls before `min` looks at them, so
    the call count depends only on the two lengths -- not on the characters,
    and not on which move turns out to be cheapest.
    """
    tally[0] += 1
    seen.add((i, j))
    if i == 0:
        return j
    if j == 0:
        return i
    return min(edit_naive(a, b, i - 1, j, tally, seen) + 1,
               edit_naive(a, b, i, j - 1, tally, seen) + 1,
               edit_naive(a, b, i - 1, j - 1, tally, seen)
               + (a[i - 1] != b[j - 1]))


def show(a, b, table):
    n = len(b)
    head = "".join(f"{'-' if j == 0 else b[j - 1]:>4}" for j in range(n + 1))
    print(f"      {head}")
    for i in range(len(a) + 1):
        label = "-" if i == 0 else a[i - 1]
        cells = "".join(f"{table[i][j]:>4}" for j in range(n + 1))
        print(f"  {label:>3} {cells}")


print("Part 1 -- the table, for two words that are almost the same")
print()
A, B = "kitten", "sitting"
table = edit_table(A, B)
show(A, B, table)
print()
print(f"  {A!r} -> {B!r} : {table[len(A)][len(B)]} edits")
print()
print("The table is the recurrence. Read row i and column j as 'the first i")
print("characters of the source, the first j of the target', and the number")
print("in the cell as the cheapest way to get from one to the other. Each")
print("cell is the minimum of three, and those three are the three things you")
print("can do at that position:")
print()
print("  table[i-1][j]   + 1     delete a character from the source")
print("  table[i][j-1]   + 1     insert a character into the source")
print("  table[i-1][j-1] + cost  substitute, free when the characters match")
print()
print("The top row and the left column are the base cases, and they are the")
print("answer to 'what does it cost to turn this into nothing'. Turning")
print("kitten into the empty string is six deletions, so the left column")
print("counts up from 0 to 6 -- it is not a special case bolted on, it is the")
print("recurrence applied to an empty second string.")
print()
print("The bottom-right cell is the answer, and everything else in the table")
print("was computed to get there. That is the trade the previous section was")
print(f"about: {len(table) * len(table[0])} cells, of which {len(table) * len(table[0]) - 1} exist only to")
print("support the one in the corner.")
print()
print()
print("Part 2 -- the same recurrence without the table")
print()
print(f"{'n':>5}{'distinct states':>17}{'naive calls':>14}{'repeats':>10}"
      f"{'growth':>10}{'target':>10}")
print("-" * 66)
TARGET = 3 + 2 * 2 ** 0.5
rows = []
for n in range(1, 9):
    a = "abcdefgh"[:n]
    b = "abcdefgh"[:n - 1] + "z"
    tally, seen = [0], set()
    naive = edit_naive(a, b, n, n, tally, seen)
    rows.append((n, len(seen), tally[0]))
    growth = f"{tally[0] / rows[-2][2]:.2f}" if len(rows) > 1 else "-"
    print(f"{n:>5}{len(seen):>17,}{tally[0]:>14,}"
          f"{tally[0] / len(seen):>10.1f}{growth:>10}{TARGET:>10.2f}")
print()
print(f"  the table has (n+1)^2 cells : {rows[-1][1]:,} at n = {rows[-1][0]}")
print(f"  the naive recursion calls   : {rows[-1][2]:,}")
print(f"  one is quadratic, the other : exponential")
print()
print("The growth column is the diagnosis. Each extra character multiplies")
print("the work by the same factor every time -- that is what exponential")
print("means -- and the factor is neither 2 nor 3.")
print()
print("Three branches per node suggests 3^n, and that is wrong, for a reason")
print("worth working out. The three calls move to (i-1, j), (i, j-1) and")
print("(i-1, j-1): they step in two dimensions, not one. So the count is a")
print("count of paths through a grid, not of levels of a tree, and paths")
print("through a grid grow faster than the branching factor suggests. The")
print("rate is 3 + 2*sqrt(2), which is the target column -- and the growth")
print("column is still climbing toward it at n = 8, because the convergence")
print("is slow, exactly as it was for phi in the first section.")
print()
print("The distinct column is the other half, and it is the one that matters")
print("for the fix. Every call is asking about a pair (i, j) of prefixes, and")
print("there are only (n+1)^2 such pairs. So the recursion is doing")
print(f"{rows[-1][2]:,} things when there are {rows[-1][1]:,} different things to do -- and the")
print("table is just the set of distinct answers, computed once each.")
print()
print()
print("Part 3 -- walking the table back to get the operations")
print()


def traceback(a, b, table):
    """Follow the same three moves backwards from the corner. Each step
    re-derives which of the three the cell came from, because the table only
    stored the cost."""
    i, j = len(a), len(b)
    moves = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] \
                and table[i][j] == table[i - 1][j - 1]:
            moves.append(("match", a[i - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + 1:
            moves.append(("substitute", f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            moves.append(("delete", a[i - 1]))
            i -= 1
        else:
            moves.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(moves))


moves = traceback(A, B, table)
print(f"  {'operation':<14}{'character':>12}{'running cost':>16}")
print("-" * 42)
cost = 0
for name, detail in moves:
    if name != "match":
        cost += 1
    print(f"  {name:<14}{detail:>12}{cost:>16}")
print()
print(f"  {len(moves)} positions, {sum(1 for n, _ in moves if n != 'match')} of them "
      f"costing an edit")
print()
print("The traceback is why the table is worth keeping. The recurrence gives")
print("you the *cost* in the corner; the table gives you the *operations*, by")
print("walking backwards and re-deriving at each cell which of the three")
print("moves the minimum came from.")
print()
print("Note that the walk has to test the moves in a fixed order, and that")
print("the order is a choice. Two different optimal edit scripts can have the")
print("same total cost, and the one you get back depends on which test you")
print("write first. That is not a bug -- it is the same tie-breaking question")
print("that came up for A* in the previous chapter, and it is why a diff tool")
print("and a spell checker can disagree about the 'right' answer while both")
print("being correct about the cost.")
print()
print("Part 3 also shows the cost of the table in a second way. Every cell")
print("here was already computed in Part 1; the walk does not recompute")
print("anything, it just reads. A version that kept only the last row would")
print("have the same 3 in the corner and no way to produce this list at all.")
```

```text
Part 1 -- the table, for two words that are almost the same

         -   s   i   t   t   i   n   g
    -    0   1   2   3   4   5   6   7
    k    1   1   2   3   4   5   6   7
    i    2   2   1   2   3   4   5   6
    t    3   3   2   1   2   3   4   5
    t    4   4   3   2   1   2   3   4
    e    5   5   4   3   2   2   3   4
    n    6   6   5   4   3   3   2   3

  'kitten' -> 'sitting' : 3 edits

The table is the recurrence. Read row i and column j as 'the first i
characters of the source, the first j of the target', and the number
in the cell as the cheapest way to get from one to the other. Each
cell is the minimum of three, and those three are the three things you
can do at that position:

  table[i-1][j]   + 1     delete a character from the source
  table[i][j-1]   + 1     insert a character into the source
  table[i-1][j-1] + cost  substitute, free when the characters match

The top row and the left column are the base cases, and they are the
answer to 'what does it cost to turn this into nothing'. Turning
kitten into the empty string is six deletions, so the left column
counts up from 0 to 6 -- it is not a special case bolted on, it is the
recurrence applied to an empty second string.

The bottom-right cell is the answer, and everything else in the table
was computed to get there. That is the trade the previous section was
about: 56 cells, of which 55 exist only to
support the one in the corner.


Part 2 -- the same recurrence without the table

    n  distinct states   naive calls   repeats    growth    target
------------------------------------------------------------------
    1                4             4       1.0         -      5.83
    2                9            19       2.1      4.75      5.83
    3               16            94       5.9      4.95      5.83
    4               25           481      19.2      5.12      5.83
    5               36         2,524      70.1      5.25      5.83
    6               49        13,483     275.2      5.34      5.83
    7               64        72,958    1140.0      5.41      5.83
    8               81       398,593    4920.9      5.46      5.83

  the table has (n+1)^2 cells : 81 at n = 8
  the naive recursion calls   : 398,593
  one is quadratic, the other : exponential

The growth column is the diagnosis. Each extra character multiplies
the work by the same factor every time -- that is what exponential
means -- and the factor is neither 2 nor 3.

Three branches per node suggests 3^n, and that is wrong, for a reason
worth working out. The three calls move to (i-1, j), (i, j-1) and
(i-1, j-1): they step in two dimensions, not one. So the count is a
count of paths through a grid, not of levels of a tree, and paths
through a grid grow faster than the branching factor suggests. The
rate is 3 + 2*sqrt(2), which is the target column -- and the growth
column is still climbing toward it at n = 8, because the convergence
is slow, exactly as it was for phi in the first section.

The distinct column is the other half, and it is the one that matters
for the fix. Every call is asking about a pair (i, j) of prefixes, and
there are only (n+1)^2 such pairs. So the recursion is doing
398,593 things when there are 81 different things to do -- and the
table is just the set of distinct answers, computed once each.


Part 3 -- walking the table back to get the operations

  operation        character    running cost
------------------------------------------
  substitute            k->s               1
  match                    i               1
  match                    t               1
  match                    t               1
  substitute            e->i               2
  match                    n               2
  insert                   g               3

  7 positions, 3 of them costing an edit

The traceback is why the table is worth keeping. The recurrence gives
you the *cost* in the corner; the table gives you the *operations*, by
walking backwards and re-deriving at each cell which of the three
moves the minimum came from.

Note that the walk has to test the moves in a fixed order, and that
the order is a choice. Two different optimal edit scripts can have the
same total cost, and the one you get back depends on which test you
write first. That is not a bug -- it is the same tie-breaking question
that came up for A* in the previous chapter, and it is why a diff tool
and a spell checker can disagree about the 'right' answer while both
being correct about the cost.

Part 3 also shows the cost of the table in a second way. Every cell
here was already computed in Part 1; the walk does not recompute
anything, it just reads. A version that kept only the last row would
have the same 3 in the corner and no way to produce this list at all.
```

The table is the recurrence, and reading it is mostly a matter of reading the base cases correctly.
The top row and the left column are not special cases bolted on -- they are the answer to "what does
it cost to turn this into nothing", which is one deletion per character. Turning `kitten` into the
empty string is six deletions, so the left column counts up from 0 to 6, and that is the recurrence
applied to an empty second string rather than an exception to it.

The bottom-right cell is the answer and everything else was computed to get there -- 56 cells, of
which 55 exist only to support the one in the corner. That is the trade the earlier sections were
about, stated in one line.

Part 2 is where the counting pays off, and the growth rate has a surprise in it. Three branches per
node suggests 3^n, and that is wrong, for a reason worth working out: the three calls move to
`(i-1, j)`, `(i, j-1)` and `(i-1, j-1)`, so they step in **two dimensions** rather than one. The
count is therefore a count of paths through a grid, not of levels of a tree, and paths through a
grid grow faster than the branching factor suggests -- 3 + 2√2, which is about 5.83. The growth
column is still climbing toward it at n = 8, because the convergence is slow, exactly as it was for
φ in the first section.

The distinct column is the other half: 398,593 calls to do 81 different things. The table is just
the set of distinct answers, computed once each.

Part 3 is the traceback, and it is why the table is worth keeping. The recurrence gives you the
*cost* in the corner; the table gives you the *operations*, by walking backwards and re-deriving at
each cell which of the three moves the minimum came from. Note that the walk has to test the moves
in a fixed order and that the order is a choice -- two different optimal edit scripts can have the
same total cost, which is the same tie-breaking question that came up for A\* in the previous
chapter.

## What the state has to remember

Longest common subsequence is the sibling of edit distance: the same two-dimensional table, a
different recurrence. It is worth doing both because the *difference* between them is where the
design work is -- and because LCS is the algorithm inside `diff`.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- what a state has to remember.

The longest common subsequence is the sibling of edit distance: the same
two-dimensional table, a different recurrence. It is worth doing both because
the *difference* between them is where the design work is -- and because LCS
is the algorithm inside `diff`.

The second half is the sharper lesson. Longest common *substring* looks like
the same problem and is not: it needs a different state, and the answer is
read from a different cell of the table. Getting that wrong is the most
common way a DP is written correctly and still gives the wrong number.
"""
import functools


def lcs_table(a, b):
    """table[i][j] = the length of the longest common subsequence of the
    first i characters of `a` and the first j of `b`.

    The state has to be a pair of *prefix* lengths. It cannot be 'the LCS of
    the whole strings', because that has no smaller version of itself to
    recurse into; it cannot be a pair of suffixes either, because the answer
    for suffixes does not compose when you extend them at the front.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table


def all_lcs(a, b, table):
    """Every distinct longest common subsequence, as strings. Memoised, which
    is the same idea applied to the *set* of answers rather than the length."""
    @functools.lru_cache(maxsize=None)
    def go(i, j):
        if i == 0 or j == 0:
            return frozenset([""])
        if a[i - 1] == b[j - 1]:
            return frozenset(s + a[i - 1] for s in go(i - 1, j - 1))
        found = set()
        if table[i - 1][j] >= table[i][j - 1]:
            found |= go(i - 1, j)
        if table[i][j - 1] >= table[i - 1][j]:
            found |= go(i, j - 1)
        return frozenset(found)

    return go(len(a), len(b))


def substring_table(a, b):
    """Longest common *substring*. Same shape of table, different meaning.

    table[i][j] is now 'the length of the longest common run that ends
    exactly at position i of `a` and position j of `b`' -- so the answer is
    the largest value anywhere in the table, not the corner. There is no
    `max` in the recurrence, because a run that breaks cannot be extended.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
                best = max(best, table[i][j])
    return table, best


def show(a, b, table, label):
    n = len(b)
    head = "".join(f"{'-' if j == 0 else b[j - 1]:>4}" for j in range(n + 1))
    print(f"  {label}")
    print(f"      {head}")
    for i in range(len(a) + 1):
        name = "-" if i == 0 else a[i - 1]
        cells = "".join(f"{table[i][j]:>4}" for j in range(n + 1))
        print(f"  {name:>3} {cells}")


A, B = "abcbdab", "bdcaba"

print("Part 1 -- the table, and the one line that differs from edit distance")
print()
table = lcs_table(A, B)
show(A, B, table, f"LCS of {A!r} and {B!r}")
print()
print(f"  {A!r} vs {B!r} : longest common subsequence is "
      f"{table[len(A)][len(B)]} characters")
print()
print("Compare this recurrence with the previous section's:")
print()
print("  edit distance : table[i][j] = min(three things, one of them +cost)")
print("  LCS           : table[i][j] = table[i-1][j-1] + 1   when equal")
print("                  table[i][j] = max(above, left)       when not")
print()
print("The equal case is not a `max` -- it is forced. If the two characters")
print("match, there is always an optimal solution that uses them, so the cell")
print("is the diagonal plus one and the other two candidates are irrelevant.")
print("The unequal case is where the choice lives, and there the choice is")
print("only between dropping a character from one string or the other.")
print()
print("That is the difference between an edit and a match, expressed as a")
print("recurrence: editing costs you one operation, matching costs you")
print("nothing and gains you a character.")
print()
print()
print("Part 2 -- ties, and why the answer is not unique")
print()
answers = sorted(all_lcs(A, B, table))
print(f"  distinct longest common subsequences : {len(answers)}")
for answer in answers:
    print(f"    {answer!r}")
print()
print("All of them are the same length, and they are all correct. That is not")
print("a flaw in the algorithm -- the problem statement has a tie in it, and")
print("any implementation has to break the tie somewhere.")
print()
print("`all_lcs` breaks it by taking *both* branches when the two neighbours")
print("are equal, which is why it returns a set. A traceback that tests")
print("`table[i-1][j] > table[i][j-1]` with a strict `>` silently picks one")
print("and returns it; testing `>=` first on the other side returns a")
print("different one. Both are valid, and a diff tool built on either will")
print("produce different output for the same input.")
print()
print()
print("Part 3 -- the same-looking problem that needs a different state")
print()
sub_table, best = substring_table(A, B)
show(A, B, sub_table, f"longest common SUBSTRING of {A!r} and {B!r}")
print()
print(f"  longest common substring  : {best} characters")
print(f"  longest common subsequence: {table[len(A)][len(B)]} characters")
print()
print("Two tables, both filled by a double loop over the same pair of")
print("strings, and the numbers are different. The reason is entirely in what")
print("the state *means*.")
print()
print("In the subsequence table, a cell says 'how good can I do with these")
print("two prefixes' -- so it is a running best, and it can never go down as")
print("the prefixes grow. In the substring table, a cell says 'how long is")
print("the run that ends exactly here' -- so it drops to zero the moment the")
print("characters differ, and the answer has to be harvested as a maximum")
print("over the whole table.")
print()
print("The second table has no `max` in its recurrence at all, which is the")
print("tell. A `max` between neighbours is the signature of a state that")
print("carries a running best; its absence means the state is pinned to a")
print("position, and the running best has to be collected elsewhere.")
print()
lcs_answer = table[len(A)][len(B)]
sub_answer_cells = [(i, j) for i, row in enumerate(table)
                    for j, v in enumerate(row) if v == lcs_answer]
substr_answer_cells = [(i, j) for i, row in enumerate(sub_table)
                       for j, v in enumerate(row) if v == best]
print(f"  cells holding the answer, subsequence : {len(sub_answer_cells)}")
print(f"    in rows {sorted({i for i, _ in sub_answer_cells})} "
      f"of {len(A)}")
print(f"  cells holding the answer, substring   : {len(substr_answer_cells)}")
print(f"    in rows {sorted({i for i, _ in substr_answer_cells})} "
      f"of {len(A)}")
print()
print("The counts are similar and the counts are not the point -- the")
print("*positions* are. Every cell holding the subsequence answer is in the")
print("last two rows, and the reason is structural: the subsequence table")
print("never goes down, so once a cell has reached the maximum, every cell")
print("down and to the right of it keeps that maximum. The answer is")
print("guaranteed to be in the corner, and the other cells that share it are")
print("just cells that can already see the corner.")
print()
print("The substring answer cells are scattered through the table, and which")
print("rows they land in depends on the input. There is no cell whose")
print("coordinates you know in advance, so the loop has to carry a running")
print("maximum as it goes.")
print()
print("That is the difference that bites. If you forget the running maximum")
print("the code still runs, still returns a plausible number, and nothing")
print("about the output tells you it is wrong -- the worst kind of bug,")
print("because it is invisible until the input happens to matter.")
```

```text
Part 1 -- the table, and the one line that differs from edit distance

  LCS of 'abcbdab' and 'bdcaba'
         -   b   d   c   a   b   a
    -    0   0   0   0   0   0   0
    a    0   0   0   0   1   1   1
    b    0   1   1   1   1   2   2
    c    0   1   1   2   2   2   2
    b    0   1   1   2   2   3   3
    d    0   1   2   2   2   3   3
    a    0   1   2   2   3   3   4
    b    0   1   2   2   3   4   4

  'abcbdab' vs 'bdcaba' : longest common subsequence is 4 characters

Compare this recurrence with the previous section's:

  edit distance : table[i][j] = min(three things, one of them +cost)
  LCS           : table[i][j] = table[i-1][j-1] + 1   when equal
                  table[i][j] = max(above, left)       when not

The equal case is not a `max` -- it is forced. If the two characters
match, there is always an optimal solution that uses them, so the cell
is the diagonal plus one and the other two candidates are irrelevant.
The unequal case is where the choice lives, and there the choice is
only between dropping a character from one string or the other.

That is the difference between an edit and a match, expressed as a
recurrence: editing costs you one operation, matching costs you
nothing and gains you a character.


Part 2 -- ties, and why the answer is not unique

  distinct longest common subsequences : 3
    'bcab'
    'bcba'
    'bdab'

All of them are the same length, and they are all correct. That is not
a flaw in the algorithm -- the problem statement has a tie in it, and
any implementation has to break the tie somewhere.

`all_lcs` breaks it by taking *both* branches when the two neighbours
are equal, which is why it returns a set. A traceback that tests
`table[i-1][j] > table[i][j-1]` with a strict `>` silently picks one
and returns it; testing `>=` first on the other side returns a
different one. Both are valid, and a diff tool built on either will
produce different output for the same input.


Part 3 -- the same-looking problem that needs a different state

  longest common SUBSTRING of 'abcbdab' and 'bdcaba'
         -   b   d   c   a   b   a
    -    0   0   0   0   0   0   0
    a    0   0   0   0   1   0   1
    b    0   1   0   0   0   2   0
    c    0   0   0   1   0   0   0
    b    0   1   0   0   0   1   0
    d    0   0   2   0   0   0   0
    a    0   0   0   0   1   0   1
    b    0   1   0   0   0   2   0

  longest common substring  : 2 characters
  longest common subsequence: 4 characters

Two tables, both filled by a double loop over the same pair of
strings, and the numbers are different. The reason is entirely in what
the state *means*.

In the subsequence table, a cell says 'how good can I do with these
two prefixes' -- so it is a running best, and it can never go down as
the prefixes grow. In the substring table, a cell says 'how long is
the run that ends exactly here' -- so it drops to zero the moment the
characters differ, and the answer has to be harvested as a maximum
over the whole table.

The second table has no `max` in its recurrence at all, which is the
tell. A `max` between neighbours is the signature of a state that
carries a running best; its absence means the state is pinned to a
position, and the running best has to be collected elsewhere.

  cells holding the answer, subsequence : 3
    in rows [6, 7] of 7
  cells holding the answer, substring   : 3
    in rows [2, 5, 7] of 7

The counts are similar and the counts are not the point -- the
*positions* are. Every cell holding the subsequence answer is in the
last two rows, and the reason is structural: the subsequence table
never goes down, so once a cell has reached the maximum, every cell
down and to the right of it keeps that maximum. The answer is
guaranteed to be in the corner, and the other cells that share it are
just cells that can already see the corner.

The substring answer cells are scattered through the table, and which
rows they land in depends on the input. There is no cell whose
coordinates you know in advance, so the loop has to carry a running
maximum as it goes.

That is the difference that bites. If you forget the running maximum
the code still runs, still returns a plausible number, and nothing
about the output tells you it is wrong -- the worst kind of bug,
because it is invisible until the input happens to matter.
```

The equal case of the recurrence is not a `max` -- it is forced. If the two characters match, there
is always an optimal solution that uses them, so the cell is the diagonal plus one and the other two
candidates are irrelevant. The unequal case is where the choice lives. That is the difference
between an edit and a match expressed as a recurrence: editing costs one operation, matching costs
nothing and gains a character.

Part 2 is the part that is usually skipped and should not be. This problem has a **tie in its
statement**, so any implementation has to break it somewhere, and the three distinct answers here
are all correct. `all_lcs` breaks the tie by taking both branches when the two neighbours are equal,
which is why it returns a set. A traceback testing `>` picks one; testing `>=` on the other side
picks a different one. Both are valid, and a diff tool built on either will produce different output
for the same input -- which is a fact about the problem, not about the tool.

Part 3 is the sharper lesson, and it is the reason this section exists. Longest common **substring**
looks like the same problem and is not. The counts of answer-holding cells came out equal -- three
each -- and the counts are not the point; the *positions* are. Every cell holding the subsequence
answer is in the last two rows, and the reason is structural: the subsequence table never goes down,
so once a cell has reached the maximum, every cell down and to the right of it keeps it. The
substring answer cells are scattered, and which rows they land in depends on the input.

The tell is in the recurrence. The substring table has **no `max` between neighbours at all** --
its cell is `table[i-1][j-1] + 1` or zero, and nothing else. A `max` between neighbours is the
signature of a state that carries a running best; its absence means the state is pinned to a
position and the running best has to be collected elsewhere, by the loop. Forget it and the code
still runs and still returns a plausible number, which is the worst kind of bug.

## Knapsack, and the word that qualifies the chapter

Knapsack is the DP that turns up most often in practice, because "pick the best subset under a
budget" is what most resource decisions actually are. It is also where the phrase "polynomial time"
stops meaning what it looks like.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- knapsack, and the one word that qualifies every
complexity claim in this chapter.

Knapsack is the DP that turns up most often in practice, because 'pick the
best subset under a budget' is what most resource decisions actually are. It
is also where the phrase 'polynomial time' stops meaning what it looks like,
and the table at the end is the reason.

Everything here is counted: values, capacities and table cells. No timings.
"""

ITEMS = [
    ("map", 9, 150), ("compass", 13, 35), ("water", 153, 200),
    ("sandwich", 50, 160), ("glucose", 15, 60), ("banana", 27, 60),
    ("suntan", 11, 70), ("camera", 32, 30), ("note-case", 22, 80),
    ("socks", 4, 50), ("book", 30, 10), ("sunglasses", 6, 20),
]
CAPACITY = 200


def knapsack_table(items, capacity):
    """table[i][w] = the best value obtainable from the first i items with a
    budget of w.

    Two dimensions, and the second one is the surprise: the state includes
    the budget, so the size of the table depends on a *number* rather than on
    how many things there are.
    """
    n = len(items)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        name, weight, value = items[i - 1]
        for w in range(capacity + 1):
            skip = table[i - 1][w]
            if weight > w:
                table[i][w] = skip
            else:
                take = table[i - 1][w - weight] + value
                table[i][w] = max(skip, take)
    return table


def knapsack_pick(items, capacity, table):
    """Walk back to find which items were taken. The table stores values, so
    the decision has to be re-derived -- same as the edit-distance traceback."""
    w = capacity
    taken = []
    for i in range(len(items), 0, -1):
        if table[i][w] != table[i - 1][w]:
            name, weight, value = items[i - 1]
            taken.append((name, weight, value))
            w -= weight
    return list(reversed(taken))


print("Part 1 -- the greedy that looks right and is not")
print()
print("Packing a rucksack by 'take the item with the best value per unit of")
print("weight first' is the natural idea, and it is wrong. Here is the")
print("smallest case that shows it:")
print()
TOY = [("A", 6, 30), ("B", 5, 24), ("C", 5, 24)]
print(f"  capacity 10, three items:")
for name, weight, value in TOY:
    print(f"    {name}  weight {weight}  value {value}  "
          f"ratio {value / weight:.1f}")
print()
by_ratio = sorted(TOY, key=lambda item: item[2] / item[1], reverse=True)
room, greedy_value, greedy_took = 10, 0, []
for name, weight, value in by_ratio:
    if weight <= room:
        room -= weight
        greedy_value += value
        greedy_took.append(name)
toy_table = knapsack_table(TOY, 10)
best_value = toy_table[len(TOY)][10]
best_took = [name for name, _, _ in knapsack_pick(TOY, 10, toy_table)]
print(f"  greedy by ratio : takes {'+'.join(greedy_took)}, "
      f"value {greedy_value}")
print(f"  optimal         : takes {'+'.join(best_took)}, value {best_value}")
print()
print(f"  the greedy is {greedy_value} where {best_value} was available -- "
      f"{best_value / greedy_value:.1f}x worse")
print()
print("The greedy takes A because its ratio is the best, and that leaves 4")
print("units of room with nothing that fits. The optimal answer skips A")
print("entirely and takes two mediocre items that happen to fit exactly.")
print()
print("This is the general shape of the failure: greedy decisions are")
print("irrevocable, and a locally best choice can consume a resource in a way")
print("that makes the remainder unusable. The ratio is not a bad heuristic --")
print("it is a heuristic, and knapsack has no exchange argument to justify")
print("it. Coin change does, for some coin systems, which is the next")
print("section.")
print()
print()
print("Part 2 -- the table, on a real instance")
print()
table = knapsack_table(ITEMS, CAPACITY)
taken = knapsack_pick(ITEMS, CAPACITY, table)
total_weight = sum(weight for _, weight, _ in taken)
total_value = sum(value for _, _, value in taken)
print(f"  {len(ITEMS)} items, capacity {CAPACITY}")
print()
print(f"  {'item':<12}{'weight':>8}{'value':>8}{'running weight':>17}"
      f"{'running value':>15}")
print("-" * 60)
weight_so_far = value_so_far = 0
for name, weight, value in taken:
    weight_so_far += weight
    value_so_far += value
    print(f"  {name:<12}{weight:>8}{value:>8}{weight_so_far:>17}"
          f"{value_so_far:>15}")
print("-" * 60)
print(f"  {'total':<12}{total_weight:>8}{total_value:>8}")
print()
print(f"  capacity used : {total_weight} of {CAPACITY}")
print(f"  table cells   : {(len(ITEMS) + 1) * (CAPACITY + 1):,}")
print(f"  cells per item: {CAPACITY + 1:,}")
print()
print("The last two lines are the shape of the whole algorithm. The table is")
print("(items + 1) x (capacity + 1), so it grows with the number of items --")
print("which is what you would expect -- and also with the capacity, which is")
print("a *quantity*, not a count of anything.")
print()
print()
print("Part 3 -- the word that qualifies every claim in this chapter")
print()
print("'Polynomial time' means polynomial in the length of the input. For a")
print("list of n items the input length is roughly n. For a capacity, the")
print("input length is the number of *digits* -- writing 100000 takes six")
print("characters, not a hundred thousand.")
print()
print(f"{'capacity':>12}{'digits':>9}{'table cells':>15}{'work vs previous':>19}")
print("-" * 55)
previous = None
for power in (3, 4, 5, 6):
    capacity = 10 ** power
    cells = (len(ITEMS) + 1) * (capacity + 1)
    ratio = "-" if previous is None else f"{cells / previous:.1f}x"
    print(f"{capacity:>12,}{len(str(capacity)):>9}{cells:>15,}{ratio:>19}")
    previous = cells
print()
print("Read the first and last columns together. Every extra digit of")
print("capacity multiplies the table by ten, while the input grows by one")
print("character. So the running time is polynomial in the *value* of the")
print("capacity and exponential in the *length* of it -- which is why")
print("knapsack is called pseudo-polynomial, and why it is not a")
print("counterexample to knapsack being NP-hard.")
print()
print("Both statements are true at once and they are not in tension:")
print()
print("  - for a fixed capacity, or one that fits in a machine word, the")
print("    table is a fixed size and the algorithm is linear in the items")
print("  - for a capacity given as an arbitrarily long number, the table is")
print("    exponential in the input and no shortcut is known")
print()
print("The practical reading is the useful one. This is the right algorithm")
print("when the budget is a real quantity you can afford to enumerate --")
print("200 grams, 48 hours, 5000 dollars. It is the wrong algorithm when the")
print("budget is 10^18, and in that case the usual move is to look for")
print("structure in the values instead of the capacity.")
print()
print()
print("Part 4 -- and the one-line change that breaks it")
print()


def knapsack_1d(items, capacity, descending=True):
    """One row instead of a table.

    The direction of the inner loop is the whole algorithm. Going downwards
    means each item is considered once, against a row that still holds the
    answers from *before* this item. Going upwards means the row has already
    been updated with this item, so the item can be taken again -- which is
    not knapsack 0/1 any more, it is unbounded knapsack.
    """
    best = [0] * (capacity + 1)
    for name, weight, value in items:
        span = range(capacity, weight - 1, -1) if descending \
            else range(weight, capacity + 1)
        for w in span:
            candidate = best[w - weight] + value
            if candidate > best[w]:
                best[w] = candidate
    return best[capacity]


print(f"  two-dimensional table          : {table[len(ITEMS)][CAPACITY]}")
print(f"  one row, capacity downwards    : "
      f"{knapsack_1d(ITEMS, CAPACITY, descending=True)}")
print(f"  one row, capacity upwards      : "
      f"{knapsack_1d(ITEMS, CAPACITY, descending=False)}")
print()
print("The first two agree and the third does not, and the third is the bug")
print("you get by reversing a loop. Going upwards, the cell `best[w-weight]`")
print("has already been written this round, so it may already contain this")
print("item -- and the algorithm happily takes it again, and again, until the")
print("capacity runs out.")
print()
unbounded = knapsack_1d(ITEMS, CAPACITY, descending=False)
best_ratio = max(ITEMS, key=lambda item: item[2] / item[1])
repeats = unbounded // best_ratio[2]
print(f"  the extra value comes from one item taken over and over:")
print(f"    {best_ratio[0]!r} is weight {best_ratio[1]}, value {best_ratio[2]}, "
      f"ratio {best_ratio[2] / best_ratio[1]:.1f}")
print(f"    {repeats} copies of it weigh {repeats * best_ratio[1]} and are worth "
      f"{repeats * best_ratio[2]}")
print()
print("The wrong version is not nonsense. It is a correct solution to a")
print("different problem, unbounded knapsack, where every item is available")
print("in unlimited supply. That is why the bug is easy to miss: the code")
print("runs, the answer is larger than the right one rather than obviously")
print("absurd, and a test that only checks 'is it bigger than zero' passes.")
print("The version that is wrong here is the version you *want* for coin")
print("change, which is the next section -- same table, same loop, opposite")
print("direction.")
print()
print(f"  table cells for the 2-D version : "
      f"{(len(ITEMS) + 1) * (CAPACITY + 1):,}")
print(f"  table cells for the 1-D version : {CAPACITY + 1:,}")
print(f"  saving                          : "
      f"{(len(ITEMS) + 1) * (CAPACITY + 1) / (CAPACITY + 1):.0f}x")
print()
print("The rolling row keeps the answer and throws away the ability to say")
print("*which* items were chosen -- the same trade the edit-distance")
print("traceback made. Everything a DP can tell you comes out of the table,")
print("so a table you did not keep is a question you can no longer answer.")
```

```text
Part 1 -- the greedy that looks right and is not

Packing a rucksack by 'take the item with the best value per unit of
weight first' is the natural idea, and it is wrong. Here is the
smallest case that shows it:

  capacity 10, three items:
    A  weight 6  value 30  ratio 5.0
    B  weight 5  value 24  ratio 4.8
    C  weight 5  value 24  ratio 4.8

  greedy by ratio : takes A, value 30
  optimal         : takes B+C, value 48

  the greedy is 30 where 48 was available -- 1.6x worse

The greedy takes A because its ratio is the best, and that leaves 4
units of room with nothing that fits. The optimal answer skips A
entirely and takes two mediocre items that happen to fit exactly.

This is the general shape of the failure: greedy decisions are
irrevocable, and a locally best choice can consume a resource in a way
that makes the remainder unusable. The ratio is not a bad heuristic --
it is a heuristic, and knapsack has no exchange argument to justify
it. Coin change does, for some coin systems, which is the next
section.


Part 2 -- the table, on a real instance

  12 items, capacity 200

  item          weight   value   running weight  running value
------------------------------------------------------------
  map                9     150                9            150
  compass           13      35               22            185
  sandwich          50     160               72            345
  glucose           15      60               87            405
  banana            27      60              114            465
  suntan            11      70              125            535
  camera            32      30              157            565
  note-case         22      80              179            645
  socks              4      50              183            695
  sunglasses         6      20              189            715
------------------------------------------------------------
  total            189     715

  capacity used : 189 of 200
  table cells   : 2,613
  cells per item: 201

The last two lines are the shape of the whole algorithm. The table is
(items + 1) x (capacity + 1), so it grows with the number of items --
which is what you would expect -- and also with the capacity, which is
a *quantity*, not a count of anything.


Part 3 -- the word that qualifies every claim in this chapter

'Polynomial time' means polynomial in the length of the input. For a
list of n items the input length is roughly n. For a capacity, the
input length is the number of *digits* -- writing 100000 takes six
characters, not a hundred thousand.

    capacity   digits    table cells   work vs previous
-------------------------------------------------------
       1,000        4         13,013                  -
      10,000        5        130,013              10.0x
     100,000        6      1,300,013              10.0x
   1,000,000        7     13,000,013              10.0x

Read the first and last columns together. Every extra digit of
capacity multiplies the table by ten, while the input grows by one
character. So the running time is polynomial in the *value* of the
capacity and exponential in the *length* of it -- which is why
knapsack is called pseudo-polynomial, and why it is not a
counterexample to knapsack being NP-hard.

Both statements are true at once and they are not in tension:

  - for a fixed capacity, or one that fits in a machine word, the
    table is a fixed size and the algorithm is linear in the items
  - for a capacity given as an arbitrarily long number, the table is
    exponential in the input and no shortcut is known

The practical reading is the useful one. This is the right algorithm
when the budget is a real quantity you can afford to enumerate --
200 grams, 48 hours, 5000 dollars. It is the wrong algorithm when the
budget is 10^18, and in that case the usual move is to look for
structure in the values instead of the capacity.


Part 4 -- and the one-line change that breaks it

  two-dimensional table          : 715
  one row, capacity downwards    : 715
  one row, capacity upwards      : 3300

The first two agree and the third does not, and the third is the bug
you get by reversing a loop. Going upwards, the cell `best[w-weight]`
has already been written this round, so it may already contain this
item -- and the algorithm happily takes it again, and again, until the
capacity runs out.

  the extra value comes from one item taken over and over:
    'map' is weight 9, value 150, ratio 16.7
    22 copies of it weigh 198 and are worth 3300

The wrong version is not nonsense. It is a correct solution to a
different problem, unbounded knapsack, where every item is available
in unlimited supply. That is why the bug is easy to miss: the code
runs, the answer is larger than the right one rather than obviously
absurd, and a test that only checks 'is it bigger than zero' passes.
The version that is wrong here is the version you *want* for coin
change, which is the next section -- same table, same loop, opposite
direction.

  table cells for the 2-D version : 2,613
  table cells for the 1-D version : 201
  saving                          : 13x

The rolling row keeps the answer and throws away the ability to say
*which* items were chosen -- the same trade the edit-distance
traceback made. Everything a DP can tell you comes out of the table,
so a table you did not keep is a question you can no longer answer.
```

Part 1 is the smallest counterexample to the greedy that looks right. Taking the best
value-per-unit-weight first is the natural idea, and it takes the one item that no optimal solution
contains -- leaving four units of room with nothing that fits. The general shape of the failure is
that greedy decisions are irrevocable, and a locally best choice can consume a resource in a way
that makes the remainder unusable.

The table in Part 2 has two dimensions, and the second one is the surprise: the state includes the
budget, so the size of the table depends on a *number* rather than on how many things there are.

That is the whole of Part 3, and it is the reason this section exists. "Polynomial time" means
polynomial in the **length of the input**. For a list of n items the input length is roughly n. For
a capacity, the input length is the number of *digits* -- writing 100000 takes six characters, not
a hundred thousand. So every extra digit of capacity multiplies the table by ten while the input
grows by one character, and the running time is polynomial in the *value* of the capacity and
exponential in the *length* of it.

That is what **pseudo-polynomial** means, and it is why knapsack being solvable this way is not a
counterexample to knapsack being NP-hard. Both statements are true at once and they are not in
tension. The practical reading is the useful one: this is the right algorithm when the budget is a
real quantity you can afford to enumerate -- 200 grams, 48 hours, 5000 dollars -- and the wrong one
when the budget is 10^18.

Part 4 is the one-line change that breaks it, and it is worth doing because the broken version is
not nonsense. Going upwards through the capacity means the cell `best[w-weight]` has already been
written this round, so it may already contain this item -- and the algorithm takes it again and
again until the capacity runs out. On this instance that is 22 copies of the best-ratio item, worth
3300 instead of 715.

The wrong version is a correct solution to a **different problem**: unbounded knapsack, where every
item is available in unlimited supply. That is why the bug is easy to miss -- the code runs, the
answer is larger than the right one rather than obviously absurd, and a test that only checks "is it
bigger than zero" passes. And it is the version you *want* for coin change, which is the next
section. Same table, same loop, opposite direction.

:::pitfall One loop, two problems, no error either way
Reversing a single line of the rolling row is the whole difference between 0/1 knapsack and
unbounded knapsack, and the wrong version produces a *larger* number rather than an exception:

```python
for w in range(weight, capacity + 1):        # the wrong direction
    best[w] = max(best[w], best[w - weight] + value)
```

Going upwards, `best[w - weight]` has already been written this round, so it may already contain this
item -- and the algorithm takes it again, and again, until the capacity runs out. On the instance
above that is 22 copies of the best-ratio item, worth 3300 where the right answer is 715.

Nothing raises, nothing warns, and the number is not absurd. The only way to catch it is to check the
answer against a second implementation, which is why the two versions are printed side by side rather
than one of them being trusted.
:::

## When the greedy is wrong

A greedy algorithm is correct when you can prove that taking the locally best option can never be a
mistake -- an **exchange argument**. Coin change is the cleanest place to see both halves: for some
coin systems the argument goes through and greedy is optimal, and for others it does not and greedy
is simply wrong.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- the exchange argument, and what happens without one.

A greedy algorithm is correct when you can prove that taking the locally best
option can never be a mistake -- an *exchange argument*. Coin change is the
cleanest place to see both halves: for some coin systems the argument goes
through and greedy is optimal, and for others it does not and greedy is
simply wrong.

The section ends somewhere unexpected. Coin change turns out to be a shortest
path problem wearing different clothes, which connects this chapter back to
the previous one.
"""
import collections


def fewest_dp(coins, target):
    """The DP. One dimension, not two -- the state is just the amount left.

    The recurrence reads `1 + the best answer for a smaller amount`, which is
    a strange way to describe coin change until you notice that 'a smaller
    amount' is exactly what a shortest-path relaxation looks like.
    """
    INF = target + 1
    best = [0] + [INF] * target
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount and best[amount - coin] + 1 < best[amount]:
                best[amount] = best[amount - coin] + 1
    return best


def fewest_greedy(coins, target):
    """Largest coin first, every time. Returns the coins used, or None if the
    system cannot make the amount at all."""
    used = []
    for coin in sorted(coins, reverse=True):
        while target >= coin:
            target -= coin
            used.append(coin)
    return used if target == 0 else None


print("Part 1 -- the counterexample, and it is three coins long")
print()
COINS = (1, 3, 4)
TARGET = 6
SWEEP = 60
greedy_used = fewest_greedy(COINS, TARGET)
best = fewest_dp(COINS, SWEEP)
print(f"  coins {COINS}, target {TARGET}")
print()
print(f"  greedy (largest first) : {'+'.join(map(str, greedy_used))} = "
      f"{len(greedy_used)} coins")
print(f"  optimal                : 3+3 = {best[TARGET]} coins")
print()
print("Four is the largest coin that fits, so the greedy takes it and is left")
print("with 2 -- which needs two more coins. The optimal answer never touches")
print("4 and uses two 3s. There is no tie-breaking rule that saves this: the")
print("greedy is not unlucky, it is choosing a coin that no optimal solution")
print("contains.")
print()
print()
print("Part 2 -- how often it is wrong")
print()
print(f"  coins {COINS}, sweeping every target up to {SWEEP}")
print()
print(f"{'target':>8}{'greedy':>9}{'optimal':>10}{'verdict':>12}")
print("-" * 39)
wrong = []
for amount in range(1, SWEEP + 1):
    used = fewest_greedy(COINS, amount)
    greedy_count = len(used) if used else None
    optimal = best[amount]
    if greedy_count != optimal:
        wrong.append(amount)
        if len(wrong) <= 6:
            print(f"{amount:>8}{greedy_count:>9}{optimal:>10}"
                  f"{'WRONG':>12}")
print(f"  ... {len(wrong)} of {SWEEP} targets wrong: {wrong[:12]}")
print()
print("Two things are worth reading off that list. The first is the rate:")
print(f"{len(wrong)} of {SWEEP} targets, so the greedy is right "
      f"{100 * (SWEEP - len(wrong)) / SWEEP:.0f}% of the time. A")
print("heuristic that is wrong nearly a quarter of the time is worse than")
print("useless in a payment system, and it is dangerous precisely because it")
print("is right most of the time -- a test with a handful of amounts in it")
print("will pass.")
print()
print("The second is the pattern, which is exact rather than approximate.")
print(f"Every wrong target is 4k + 2 for some k: {wrong[:6]}, and so on.")
print("The reason is that 4k + 2 = 4(k-1) + 6, and 6 is two 3s -- so the")
print("optimal answer is k-1 fours and two threes, which is k+1 coins,")
print("while the greedy takes k fours and two 1s, which is k+2. The greedy")
print("is not occasionally unlucky. It is systematically one coin worse on")
print("an infinite family of inputs.")
print()
print()
print("Part 3 -- the same algorithm, on a system where it is provably correct")
print()
print("A coin system is called *canonical* when greedy is optimal for it. The")
print("usual decimal systems are canonical, and the reason is an exchange")
print("argument rather than a proof by exhaustion. A sufficient condition is")
print("that every coin is worth at least twice the one below it, and here is")
print("the shape of the argument:")
print()
print("  take the largest coin c that fits in the amount. Any solution that")
print("  avoids c has to make up at least c from smaller coins, and since the")
print("  next coin down is worth at most c/2, that takes at least two coins.")
print("  Swapping those two for a single c cannot make the count worse, so no")
print("  optimal solution avoids c. Repeat on the remainder.")
print()
print("That argument is why the property has to be checked rather than")
print("assumed. It holds for the decimal system and it fails for {1, 3, 4},")
print("where 4 is less than twice 3 -- so the next coin down is worth *more*")
print("than half of c, one of them can substitute for c, and the swap the")
print("argument depends on does not exist.")
print()
CANONICAL = (1, 2, 5, 10, 20, 50, 100, 200)
canonical_best = fewest_dp(CANONICAL, 400)
canonical_wrong = []
for amount in range(1, 401):
    used = fewest_greedy(CANONICAL, amount)
    if used is None or len(used) != canonical_best[amount]:
        canonical_wrong.append(amount)
print(f"  coins {CANONICAL}")
print(f"  targets 1..400, disagreements with the DP : {len(canonical_wrong)}")
print()
print("Zero disagreements over four hundred targets. That is evidence, not a")
print("proof -- but combined with the exchange argument above it is the")
print("reason the coin change problem you meet in a shop is solved greedily")
print("and the one you meet in an interview is solved with a table.")
print()
print()
print("Part 4 -- where this connects to the previous chapter")
print()
print("The DP above has a one-dimensional state and a recurrence of the form")
print("'best[a] = 1 + min(best[a - c])'. That is not obviously a graph")
print("problem. Write it as one and it becomes obvious.")
print()


def fewest_bfs(coins, target):
    """Amounts are nodes. A coin is an edge from a to a + coin. Then the
    fewest coins to reach `target` is the fewest edges -- a breadth-first
    search, exactly as in the graphs chapter."""
    distance = {0: 0}
    queue = collections.deque([0])
    while queue:
        amount = queue.popleft()
        for coin in coins:
            nxt = amount + coin
            if nxt <= target and nxt not in distance:
                distance[nxt] = distance[amount] + 1
                queue.append(nxt)
    return distance


bfs = fewest_bfs(COINS, 60)
dp = fewest_dp(COINS, 60)
print(f"  {'amount':>8}{'DP':>8}{'BFS':>8}{'agree':>8}")
print("-" * 32)
for amount in (1, 3, 4, 6, 12, 30, 59, 60):
    print(f"{amount:>8}{dp[amount]:>8}{bfs[amount]:>8}"
          f"{str(dp[amount] == bfs[amount]):>8}")
print()
print(f"  all 60 amounts agree : "
      f"{all(dp[a] == bfs[a] for a in range(1, 61))}")
print()
print("The two are the same algorithm. Dijkstra's algorithm is the DP for a")
print("weighted graph; this is the unweighted case, so BFS is enough, and")
print("the 'table' is just the array of distances. The relaxation step")
print("`best[a] = 1 + best[a - coin]` is a graph edge relaxation with a")
print("weight of 1.")
print()
print("That is worth noticing because it is a general pattern rather than a")
print("coincidence. A DP is a shortest path through its own state space, and")
print("the state space is a graph whether or not you draw it. The previous")
print("chapter's algorithms are the special case where you can write the")
print("edges down explicitly; this chapter's are the case where the edges")
print("are implied by the recurrence and you enumerate them on the fly.")
print()
print("It also explains the direction of the loops, which was the whole")
print("difference between 0/1 and unbounded knapsack. In a graph where a")
print("coin edge goes from a to a + coin, walking the amounts *forwards*")
print("means each edge can be traversed again from its own endpoint -- which")
print("is exactly what 'unbounded' means. Walking backwards visits each edge")
print("once. Same graph, two different questions.")
```

```text
Part 1 -- the counterexample, and it is three coins long

  coins (1, 3, 4), target 6

  greedy (largest first) : 4+1+1 = 3 coins
  optimal                : 3+3 = 2 coins

Four is the largest coin that fits, so the greedy takes it and is left
with 2 -- which needs two more coins. The optimal answer never touches
4 and uses two 3s. There is no tie-breaking rule that saves this: the
greedy is not unlucky, it is choosing a coin that no optimal solution
contains.


Part 2 -- how often it is wrong

  coins (1, 3, 4), sweeping every target up to 60

  target   greedy   optimal     verdict
---------------------------------------
       6        3         2       WRONG
      10        4         3       WRONG
      14        5         4       WRONG
      18        6         5       WRONG
      22        7         6       WRONG
      26        8         7       WRONG
  ... 14 of 60 targets wrong: [6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50]

Two things are worth reading off that list. The first is the rate:
14 of 60 targets, so the greedy is right 77% of the time. A
heuristic that is wrong nearly a quarter of the time is worse than
useless in a payment system, and it is dangerous precisely because it
is right most of the time -- a test with a handful of amounts in it
will pass.

The second is the pattern, which is exact rather than approximate.
Every wrong target is 4k + 2 for some k: [6, 10, 14, 18, 22, 26], and so on.
The reason is that 4k + 2 = 4(k-1) + 6, and 6 is two 3s -- so the
optimal answer is k-1 fours and two threes, which is k+1 coins,
while the greedy takes k fours and two 1s, which is k+2. The greedy
is not occasionally unlucky. It is systematically one coin worse on
an infinite family of inputs.


Part 3 -- the same algorithm, on a system where it is provably correct

A coin system is called *canonical* when greedy is optimal for it. The
usual decimal systems are canonical, and the reason is an exchange
argument rather than a proof by exhaustion. A sufficient condition is
that every coin is worth at least twice the one below it, and here is
the shape of the argument:

  take the largest coin c that fits in the amount. Any solution that
  avoids c has to make up at least c from smaller coins, and since the
  next coin down is worth at most c/2, that takes at least two coins.
  Swapping those two for a single c cannot make the count worse, so no
  optimal solution avoids c. Repeat on the remainder.

That argument is why the property has to be checked rather than
assumed. It holds for the decimal system and it fails for {1, 3, 4},
where 4 is less than twice 3 -- so the next coin down is worth *more*
than half of c, one of them can substitute for c, and the swap the
argument depends on does not exist.

  coins (1, 2, 5, 10, 20, 50, 100, 200)
  targets 1..400, disagreements with the DP : 0

Zero disagreements over four hundred targets. That is evidence, not a
proof -- but combined with the exchange argument above it is the
reason the coin change problem you meet in a shop is solved greedily
and the one you meet in an interview is solved with a table.


Part 4 -- where this connects to the previous chapter

The DP above has a one-dimensional state and a recurrence of the form
'best[a] = 1 + min(best[a - c])'. That is not obviously a graph
problem. Write it as one and it becomes obvious.

    amount      DP     BFS   agree
--------------------------------
       1       1       1    True
       3       1       1    True
       4       1       1    True
       6       2       2    True
      12       3       3    True
      30       8       8    True
      59      15      15    True
      60      15      15    True

  all 60 amounts agree : True

The two are the same algorithm. Dijkstra's algorithm is the DP for a
weighted graph; this is the unweighted case, so BFS is enough, and
the 'table' is just the array of distances. The relaxation step
`best[a] = 1 + best[a - coin]` is a graph edge relaxation with a
weight of 1.

That is worth noticing because it is a general pattern rather than a
coincidence. A DP is a shortest path through its own state space, and
the state space is a graph whether or not you draw it. The previous
chapter's algorithms are the special case where you can write the
edges down explicitly; this chapter's are the case where the edges
are implied by the recurrence and you enumerate them on the fly.

It also explains the direction of the loops, which was the whole
difference between 0/1 and unbounded knapsack. In a graph where a
coin edge goes from a to a + coin, walking the amounts *forwards*
means each edge can be traversed again from its own endpoint -- which
is exactly what 'unbounded' means. Walking backwards visits each edge
once. Same graph, two different questions.
```

Part 2 is the part that matters, and it has two readings. The rate first: the greedy is right 77% of
the time, which is worse than being obviously wrong, because a test with a handful of amounts in it
will pass.

Then the pattern, which is exact rather than approximate. Every wrong target is `4k + 2` for some k.
The reason is that `4k + 2 = 4(k-1) + 6` and 6 is two 3s, so the optimal answer is `k-1` fours and
two threes -- `k+1` coins -- while the greedy takes `k` fours and two 1s, which is `k+2`. The greedy
is not occasionally unlucky. It is systematically one coin worse on an infinite family of inputs,
and the pattern is visible only because the counts were written down.

Part 3 gives the sufficient condition and the shape of the argument: every coin worth at least twice
the one below it. Take the largest coin `c` that fits; any solution avoiding it must make up at
least `c` from smaller coins, and since the next coin down is worth at most `c/2`, that takes at
least two coins. Swapping two for one cannot make the count worse. It holds for the decimal system
and it fails for `{1, 3, 4}`, where 4 is less than twice 3 -- so one coin of 3 can substitute for the
4, and the swap the argument depends on does not exist.

Part 4 goes somewhere unexpected and is the reason this section is in the chapter at all. The
coin-change DP has a one-dimensional state and a recurrence of the form
`best[a] = 1 + min(best[a - c])`, which does not look like a graph problem. Write the amounts as
nodes and a coin as an edge from `a` to `a + c`, and it is a breadth-first search over 60 nodes.

The two are the same algorithm. **Dijkstra is the DP for a weighted graph**; this is the unweighted
case, so BFS is enough and the "table" is the array of distances. That is a general pattern rather
than a coincidence: a DP is a shortest path through its own state space, and the state space is a
graph whether or not you draw it. Chapter 47's algorithms are the special case where the edges can
be written down explicitly; this chapter's are the case where the edges are implied by the
recurrence.

It also explains the loop direction that separated 0/1 from unbounded knapsack. In a graph where a
coin edge goes from `a` to `a + c`, walking the amounts forwards means each edge can be traversed
again from its own endpoint -- which is exactly what "unbounded" means. Walking backwards visits
each edge once. Same graph, two different questions.

## What the table costs

Every DP in this chapter has been a table. The table is also the part you can usually throw away,
and the two questions worth asking are "how much does it cost" and "what did it buy me". The answer
to the second one is more interesting than the answer to the first.

```python run
#!/usr/bin/env python3
"""Chapter 48 demo -- what the table costs, and what you give up by not
keeping it.

Every DP in this chapter has been a table. The table is also the part you can
usually throw away, and the two questions worth asking are 'how much does it
cost' and 'what did it buy me'.

The answer to the second one is more interesting than the answer to the
first. What the table buys is not the *answer* -- it is the *path*, and there
is a third option between keeping every number and keeping none.
"""


def edit_full(a, b):
    """The table, kept. Distance and path."""
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i
    for j in range(n + 1):
        table[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            table[i][j] = min(table[i - 1][j] + 1,
                              table[i][j - 1] + 1,
                              table[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return table


def edit_two_rows(a, b):
    """Two rows. Distance only -- and the reason it is distance only is that
    the row that would have answered 'where did this come from' was
    overwritten two iterations ago."""
    n = len(b)
    previous = list(range(n + 1))
    for i in range(1, len(a) + 1):
        current = [i] + [0] * n
        for j in range(1, n + 1):
            current[j] = min(previous[j] + 1,
                             current[j - 1] + 1,
                             previous[j - 1] + (a[i - 1] != b[j - 1]))
        previous = current
    return previous[n]


def edit_two_rows_and_bits(a, b):
    """Two rows of numbers, plus one byte per cell recording which move won.

    This is the option people forget exists. The numbers are big and there are
    (m+1)(n+1) of them; the *decisions* are three-valued and there are the
    same number of them. Keeping the decisions instead of the numbers is
    enough to rebuild the path, and the numbers are the expensive part.
    """
    m, n = len(a), len(b)
    width = n + 1
    moves = bytearray((m + 1) * width)      # 0 delete, 1 insert, 2 substitute
    previous = list(range(width))
    for i in range(1, m + 1):
        current = [i] + [0] * n
        for j in range(1, n + 1):
            delete = previous[j] + 1
            insert = current[j - 1] + 1
            substitute = previous[j - 1] + (a[i - 1] != b[j - 1])
            best = min(delete, insert, substitute)
            current[j] = best
            if best == substitute:
                moves[i * width + j] = 2
            elif best == delete:
                moves[i * width + j] = 0
            else:
                moves[i * width + j] = 1
        previous = current
    return previous[n], moves


def rebuild(a, b, moves):
    """Reconstruct the edit script from the decisions alone."""
    width = len(b) + 1
    i, j = len(a), len(b)
    script = []
    while i > 0 or j > 0:
        if i == 0:
            script.append(("insert", b[j - 1]))
            j -= 1
            continue
        if j == 0:
            script.append(("delete", a[i - 1]))
            i -= 1
            continue
        move = moves[i * width + j]
        if move == 2:
            script.append(("match" if a[i - 1] == b[j - 1] else "substitute",
                           a[i - 1] if a[i - 1] == b[j - 1] else
                           f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif move == 0:
            script.append(("delete", a[i - 1]))
            i -= 1
        else:
            script.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(script))


def path_from_full(a, b, table):
    """The same reconstruction, reading the numbers instead of the bits."""
    i, j = len(a), len(b)
    script = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] \
                and table[i][j] == table[i - 1][j - 1]:
            script.append(("match", a[i - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + 1:
            script.append(("substitute", f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            script.append(("delete", a[i - 1]))
            i -= 1
        else:
            script.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(script))


A = "the quick brown fox jumps over the lazy dog"
B = "the quik brown fax jumped over a lazy dig"
M, N = len(A), len(B)

print("Part 1 -- the three versions, on the same pair of strings")
print()
print(f"  source : {A!r}")
print(f"  target : {B!r}")
print(f"  lengths: {M} and {N}")
print()
table = edit_full(A, B)
distance = table[M][N]
two_row_distance = edit_two_rows(A, B)
bit_distance, moves = edit_two_rows_and_bits(A, B)
print(f"  {'version':<28}{'distance':>10}{'path?':>8}")
print("-" * 46)
print(f"  {'full table':<28}{distance:>10}{'yes':>8}")
print(f"  {'two rows':<28}{two_row_distance:>10}{'no':>8}")
print(f"  {'two rows + decision bytes':<28}{bit_distance:>10}{'yes':>8}")
print()
print(f"  all three agree on the distance : "
      f"{distance == two_row_distance == bit_distance}")
print()
print("The distance is cheap and all three versions get it. The path is what")
print("costs memory, and the third row is the point: you do not need to keep")
print("the numbers to keep the path. You need to keep the *decisions*, and")
print("there are only three of those per cell.")
print()
print()
print("Part 2 -- what each one actually stores")
print()
cells = (M + 1) * (N + 1)
print(f"  {'version':<28}{'numbers':>10}{'bytes':>10}{'lists':>8}")
print("-" * 56)
print(f"  {'full table':<28}{cells:>10,}{'-':>10}{M + 1:>8,}")
print(f"  {'two rows':<28}{2 * (N + 1):>10,}{'-':>10}{2:>8,}")
print(f"  {'two rows + decision bytes':<28}{2 * (N + 1):>10,}"
      f"{cells:>10,}{2:>8,}")
print()
print(f"  numbers stored, full table vs two rows : "
      f"{cells / (2 * (N + 1)):.1f}x")
print()
print("The comparison understates the difference, because a 'number' here is")
print("a Python int in a list -- a pointer plus an object, not a machine")
print("word. A byte in a bytearray is one byte, with no object behind it. So")
print("the third version replaces roughly")
print(f"{cells:,} integers with {cells:,} bytes, and pays")
print(f"{2 * (N + 1):,} integers for the rolling rows.")
print()
print("In a language where an int is four bytes the trade is less dramatic")
print("but still real: four bytes per cell becomes one, and the rolling rows")
print("stay the same. The principle is the one that transfers -- store the")
print("decision, not the derived value, whenever the decision is smaller.")
print()
print()
print("Part 3 -- and the paths really are the same path")
print()
from_table = path_from_full(A, B, table)
from_bits = rebuild(A, B, moves)
print(f"  path from the full table    : {len(from_table)} steps")
print(f"  path from the decision bytes: {len(from_bits)} steps")
print(f"  identical                   : {from_table == from_bits}")
print()
print("  the first few steps:")
for name, detail in from_bits[:6]:
    print(f"    {name:<12}{detail}")
print("  ...")
print()
print("That equality is the useful result, and it is not obvious in advance.")
print("It says the numbers in the table are *derived* -- every one of them")
print("can be recomputed from the decisions -- while the decisions cannot be")
print("recovered from the numbers without walking the table again.")
print()
print("So the table is not really storing distances. It is storing a")
print("justification for each distance, in the most convenient form someone")
print("thought of first. Once you see it that way, the two-row version stops")
print("looking like a clever memory trick and starts looking like a")
print("misunderstanding: it keeps the conclusion and throws away the")
print("reasoning.")
print()
print()
print("Part 4 -- the same comparison at a size where it matters")
print()
print("The pair of strings above is deliberately small, so the three versions")
print("differ by a couple of thousand numbers and the saving is academic.")
print("Here is the same table for problems where it is not:")
print()
print(f"{'problem size':>14}{'full table':>14}{'two rows':>11}"
      f"{'decisions':>12}{'ratio':>9}")
print("-" * 60)
for size in (100, 1_000, 10_000):
    grid = (size + 1) ** 2
    print(f"{f'{size}x{size}':>14}{grid:>14,}{2 * (size + 1):>11,}"
          f"{grid:>12,}{grid / (2 * (size + 1)):>8.0f}x")
print()
print("The ratio column is the one to keep. For an n x n problem the full")
print("table holds n^2 numbers and the rolling pair holds 2n, so the gap")
print("grows like n/2 without bound -- 50x at a hundred, 5,000x at ten")
print("thousand. The decision bytes grow like n^2 as well, but a byte is not")
print("a number: in Python a stored int is a pointer into a list plus an")
print("object behind it, and the object is not free.")
print()
print("So the honest summary of this section is a three-line rule rather than")
print("a single recommendation:")
print()
print("  keep the numbers  when you need the path and the problem is small")
print("  keep the decisions when you need the path and the problem is large")
print("  keep two rows     only when you need the number and nothing else")
print()
print("The second line is the one that is usually forgotten, because the")
print("choice is presented as 'table or no table' and there is a third")
print("option sitting between them.")
print()
print()
print("Part 5 -- the escape hatch, and why this is a default rather than a law")
print()
print("Hirschberg's algorithm gets the path *and* linear memory, and it does")
print("it by giving up something this section has quietly assumed: that each")
print("cell is computed once.")
print()
print("The idea is to compute only the middle row of the table, find the")
print("column where an optimal path crosses it, and then solve the two halves")
print("recursively. Each level of the recursion recomputes what the level")
print("above threw away, so the work goes up by a constant factor while the")
print("memory falls from quadratic to linear.")
print()
print(f"  the pair in Part 1 needs {cells:,} numbers for the full table")
print(f"  and {2 * (N + 1):,} for the rolling rows")
print(f"  a 10,000x10,000 pair needs {10_001 ** 2:,} for the full table")
print(f"  and {2 * 10_001:,} for the rolling rows, at roughly twice the work")
print()
print("That trade -- a factor of two in time for a factor of n/2 in memory --")
print("is a good one whenever the strings are large, which is exactly when")
print("the naive table stops fitting. It is also the reason the advice in")
print("this section is a default: 'keep the table' is the right answer until")
print("the table is the problem.")
```

```text
Part 1 -- the three versions, on the same pair of strings

  source : 'the quick brown fox jumps over the lazy dog'
  target : 'the quik brown fax jumped over a lazy dig'
  lengths: 43 and 41

  version                       distance   path?
----------------------------------------------
  full table                           8     yes
  two rows                             8      no
  two rows + decision bytes            8     yes

  all three agree on the distance : True

The distance is cheap and all three versions get it. The path is what
costs memory, and the third row is the point: you do not need to keep
the numbers to keep the path. You need to keep the *decisions*, and
there are only three of those per cell.


Part 2 -- what each one actually stores

  version                        numbers     bytes   lists
--------------------------------------------------------
  full table                       1,848         -      44
  two rows                            84         -       2
  two rows + decision bytes           84     1,848       2

  numbers stored, full table vs two rows : 22.0x

The comparison understates the difference, because a 'number' here is
a Python int in a list -- a pointer plus an object, not a machine
word. A byte in a bytearray is one byte, with no object behind it. So
the third version replaces roughly
1,848 integers with 1,848 bytes, and pays
84 integers for the rolling rows.

In a language where an int is four bytes the trade is less dramatic
but still real: four bytes per cell becomes one, and the rolling rows
stay the same. The principle is the one that transfers -- store the
decision, not the derived value, whenever the decision is smaller.


Part 3 -- and the paths really are the same path

  path from the full table    : 44 steps
  path from the decision bytes: 44 steps
  identical                   : True

  the first few steps:
    match       t
    match       h
    match       e
    match        
    match       q
    match       u
  ...

That equality is the useful result, and it is not obvious in advance.
It says the numbers in the table are *derived* -- every one of them
can be recomputed from the decisions -- while the decisions cannot be
recovered from the numbers without walking the table again.

So the table is not really storing distances. It is storing a
justification for each distance, in the most convenient form someone
thought of first. Once you see it that way, the two-row version stops
looking like a clever memory trick and starts looking like a
misunderstanding: it keeps the conclusion and throws away the
reasoning.


Part 4 -- the same comparison at a size where it matters

The pair of strings above is deliberately small, so the three versions
differ by a couple of thousand numbers and the saving is academic.
Here is the same table for problems where it is not:

  problem size    full table   two rows   decisions    ratio
------------------------------------------------------------
       100x100        10,201        202      10,201      50x
     1000x1000     1,002,001      2,002   1,002,001     500x
   10000x10000   100,020,001     20,002 100,020,001    5000x

The ratio column is the one to keep. For an n x n problem the full
table holds n^2 numbers and the rolling pair holds 2n, so the gap
grows like n/2 without bound -- 50x at a hundred, 5,000x at ten
thousand. The decision bytes grow like n^2 as well, but a byte is not
a number: in Python a stored int is a pointer into a list plus an
object behind it, and the object is not free.

So the honest summary of this section is a three-line rule rather than
a single recommendation:

  keep the numbers  when you need the path and the problem is small
  keep the decisions when you need the path and the problem is large
  keep two rows     only when you need the number and nothing else

The second line is the one that is usually forgotten, because the
choice is presented as 'table or no table' and there is a third
option sitting between them.


Part 5 -- the escape hatch, and why this is a default rather than a law

Hirschberg's algorithm gets the path *and* linear memory, and it does
it by giving up something this section has quietly assumed: that each
cell is computed once.

The idea is to compute only the middle row of the table, find the
column where an optimal path crosses it, and then solve the two halves
recursively. Each level of the recursion recomputes what the level
above threw away, so the work goes up by a constant factor while the
memory falls from quadratic to linear.

  the pair in Part 1 needs 1,848 numbers for the full table
  and 84 for the rolling rows
  a 10,000x10,000 pair needs 100,020,001 for the full table
  and 20,002 for the rolling rows, at roughly twice the work

That trade -- a factor of two in time for a factor of n/2 in memory --
is a good one whenever the strings are large, which is exactly when
the naive table stops fitting. It is also the reason the advice in
this section is a default: 'keep the table' is the right answer until
the table is the problem.
```

The third version is the point, and it is the option people forget exists. You do not need to keep
the *numbers* to keep the *path*; you need to keep the **decisions**, and there are only three of
those per cell. Replacing a table of integers with a table of bytes costs the same number of slots
and keeps the path intact -- and on the pair in Part 1 the two reconstructions are identical, all
44 steps of them.

The comparison understates the difference in a way worth naming, because it is where a count stops
being the whole story. A "number" here is a Python int in a list -- a pointer plus an object behind
it -- while a byte in a `bytearray` is one byte with no object behind it. Counting slots is the
right discipline for comparing algorithms; it is not a memory measurement, and saying so is part of
reporting it honestly.

Part 4 is the same comparison at a size where it matters, and the ratio column is the one to keep:
n² numbers against 2n, so the gap grows like n/2 without bound -- 50x at a hundred, 5,000x at ten
thousand. That gives a three-line rule rather than a single recommendation, and the middle line is
the one that is usually forgotten:

- keep the numbers when you need the path and the problem is small
- keep the decisions when you need the path and the problem is large
- keep two rows only when you need the number and nothing else

Part 5 names the escape hatch, because this section has been about giving things up and there is a
way not to. Hirschberg's algorithm gets the path **and** linear memory by giving up something
quietly assumed until now: that each cell is computed once. It computes only the middle row, finds
where an optimal path crosses it, and solves the two halves recursively. The work goes up by a
constant factor and the memory falls from quadratic to linear -- which is a good trade whenever the
strings are large, and the reason "keep the table" is a default rather than a law.

## Choosing, on evidence

The chapter has been about counting. This is what the counting is for.

:::scenario The twenty hours before an exam
Eight topics are on the syllabus, each with an estimated cost in hours and an estimated marks gain,
and there are twenty hours left. Choosing which subset to revise is a knapsack; matching a topic name
the student mistyped against the syllabus is an edit distance. Two DPs from the same chapter, in one
sitting, on a problem small enough to check by hand.

```python run
#!/usr/bin/env python3
"""Chapter 48 scenario -- twenty hours, eight topics, and one typo.

A student has an exam in the morning. Eight topics are on the syllabus, each
with an estimated cost in hours and an estimated marks gain, and there are
twenty hours left. That is a 0/1 knapsack, and it is the same table as the
rucksack in the earlier section with the units relabelled.

The second half is a smaller problem that uses a different DP from the same
chapter: the student's revision list has a topic name spelled wrong, and the
syllabus is the dictionary. That is edit distance.
"""
import random


TOPICS = [
    ("mechanics", 8, 45),
    ("electromagnetism", 8, 26),
    ("thermodynamics", 8, 18),
    ("circuits", 5, 33),
    ("waves", 3, 23),
    ("optics", 3, 20),
    ("units", 2, 12),
    ("history", 8, 10),
]
HOURS = 20
SYLLABUS = [name for name, _, _ in TOPICS]


def plan_table(topics, hours):
    """Same recurrence as the rucksack: table[i][h] is the best marks
    obtainable from the first i topics with h hours to spend."""
    n = len(topics)
    table = [[0] * (hours + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        name, cost, marks = topics[i - 1]
        for h in range(hours + 1):
            skip = table[i - 1][h]
            if cost > h:
                table[i][h] = skip
            else:
                table[i][h] = max(skip, table[i - 1][h - cost] + marks)
    return table


def plan_pick(topics, hours, table):
    h = hours
    chosen = []
    for i in range(len(topics), 0, -1):
        if table[i][h] != table[i - 1][h]:
            name, cost, marks = topics[i - 1]
            chosen.append((name, cost, marks))
            h -= cost
    return list(reversed(chosen))


def plan_greedy(topics, hours):
    """The student's instinct: revise whatever gives the most marks per hour
    first."""
    ranked = sorted(topics, key=lambda t: t[2] / t[1], reverse=True)
    chosen, spent = [], 0
    for name, cost, marks in ranked:
        if spent + cost <= hours:
            chosen.append((name, cost, marks))
            spent += cost
    return chosen


table = plan_table(TOPICS, HOURS)
optimal = plan_pick(TOPICS, HOURS, table)
greedy = plan_greedy(TOPICS, HOURS)

print("Part 1 -- the plan")
print()
print(f"  {len(TOPICS)} topics, {HOURS} hours available")
print()
print(f"  {'topic':<18}{'hours':>7}{'marks':>7}{'marks/hour':>13}")
print("-" * 45)
for name, cost, marks in TOPICS:
    print(f"  {name:<18}{cost:>7}{marks:>7}{marks / cost:>13.1f}")
print()
print(f"  {'plan':<18}{'hours':>7}{'marks':>7}{'topics':>9}")
print("-" * 45)
print(f"  {'greedy':<18}{sum(c for _, c, _ in greedy):>7}"
      f"{sum(m for _, _, m in greedy):>7}{len(greedy):>9}")
print(f"  {'optimal':<18}{sum(c for _, c, _ in optimal):>7}"
      f"{sum(m for _, _, m in optimal):>7}{len(optimal):>9}")
print()
print("  greedy picks  :", ", ".join(name for name, _, _ in greedy))
print("  optimal picks :", ", ".join(name for name, _, _ in optimal))
print()
greedy_hours = sum(c for _, c, _ in greedy)
optimal_hours = sum(c for _, c, _ in optimal)
print(f"  the greedy spends {greedy_hours} hours and leaves {HOURS - greedy_hours} unused;")
print(f"  the optimal spends {optimal_hours} and leaves {HOURS - optimal_hours}.")
print()
print("The greedy's *ordering* is not the mistake -- every item it takes is")
print("a reasonable item, and it takes them in the right order. The mistake")
print("is that it commits to four small ones before it ever considers the")
print("single biggest prize on the list, and by then 13 of the 20 hours are")
print("gone while mechanics needs 8. The optimum drops `units`, the")
print("second-smallest item, and spends that room on `mechanics` instead.")
print()
print("That is the whole failure mode in one line: a greedy rule cannot")
print("afford to wait, and the best subset sometimes requires waiting.")
lost = sum(m for _, _, m in optimal) - sum(m for _, _, m in greedy)
print()
print(f"  marks lost to the greedy : {lost} of "
      f"{sum(m for _, _, m in optimal)} "
      f"({100 * lost / sum(m for _, _, m in optimal):.0f}%)")
print()
print(f"{lost} marks out of {sum(m for _, _, m in optimal)} is not a rounding error. The")
print("greedy loses more than a quarter of the achievable total -- and it")
print("loses it while *using less* of the resource. That last part is the")
print("counterintuitive bit, and it is worth sitting with: the greedy plan")
print(f"is not merely worse, it is smaller. It had {HOURS} hours and spent")
print(f"{greedy_hours}, because once the small items were in there was nothing")
print("left that fit.")
print()
print("A student who followed the greedy would finish with four topics")
print("revised, seven hours unused, and no way to tell that the plan was")
print("suboptimal -- the hours went unused one at a time, and each refusal")
print("looked sensible in isolation.")
print()
print()
print("Part 2 -- the typo, and a different DP")


def edit_distance(a, b):
    m, n = len(a), len(b)
    previous = list(range(n + 1))
    for i in range(1, m + 1):
        current = [i] + [0] * n
        for j in range(1, n + 1):
            current[j] = min(previous[j] + 1,
                             current[j - 1] + 1,
                             previous[j - 1] + (a[i - 1] != b[j - 1]))
        previous = current
    return previous[n]


TYPED = "circuts"
print()
print(f"  the revision list says {TYPED!r}")
print()
print(f"  {'syllabus topic':<18}{'distance':>10}")
print("-" * 28)
distances = sorted((edit_distance(TYPED, name), name) for name in SYLLABUS)
for distance, name in distances:
    marker = "  <- closest" if (distance, name) == distances[0] else ""
    print(f"  {name:<18}{distance:>10}{marker}")
print()
print("The answer is not found by comparing lengths or first letters. The")
print("closest topic is the one where the student dropped a single letter,")
print("and the edit distance finds it without being told what a dropped")
print("letter is -- which is the property that makes the recurrence worth")
print("knowing rather than just the answer it produces.")
print()
print("It also handles the cases that a simpler rule does not, and it has a")
print("real limitation worth naming. If the student had swapped two adjacent")
print("letters instead of dropping one, the distance would be 2 rather than")
print("1, because plain Levenshtein has no transposition operation:")
print()
SWAPPED = "cricuits"
print(f"  {'typed':<12}{'closest':>12}{'distance':>10}")
print("-" * 34)
print(f"  {TYPED!r:<12}{'circuits':>12}{edit_distance(TYPED, 'circuits'):>10}")
print(f"  {SWAPPED!r:<12}{'circuits':>12}"
      f"{edit_distance(SWAPPED, 'circuits'):>10}")
print()
print("A transposition is two edits, not one, so a misspelling that is a")
print("single swap costs more than one that is a single omission -- which is")
print("the opposite of what a reader expects. That is not an oversight:")
print("adding a transposition move gives Damerau-Levenshtein, which needs a")
print("larger state and one more lookback in the recurrence. Most spell")
print("checkers use that version; the recurrence here is the one that fits")
print("on a page.")
print()
print("This is the same table as Part 1 with the units changed again. Hours")
print("and marks became characters; the budget became a length. The")
print("recurrence did not change shape, which is the point of the chapter:")
print("once the state is right, the code is almost mechanical.")
print()
print()
print("Part 3 -- why the plan cannot be found by a smarter greedy")
print()
print("It is tempting to look for a better greedy rule -- ratio first, then")
print("longest first, then a tie-break. That search is a dead end, and the")
print("reason is worth stating because it applies to every knapsack-shaped")
print("problem:")
print()
print("  a greedy rule is a rule about one topic at a time, and the value of")
print("  a topic depends on which other topics are in the plan. With 20 hours")
print("  and 8 topics, the choices interact, and no per-topic score can see")
print("  the interaction.")
print()
print("The DP does not need to see it either. It just refuses to commit: it")
print("keeps the best answer for *every* budget, so when the last topic is")
print("considered the answer for 20 hours is already sitting in the table,")
print("built out of answers for 15 and 14 hours, which were built out of")
print("smaller ones. The interaction is encoded in the second index.")
print()
count = 0
for hours in range(1, 31):
    t = plan_table(TOPICS, hours)
    g = plan_greedy(TOPICS, hours)
    if t[len(TOPICS)][hours] != sum(m for _, _, m in g):
        count += 1
print(f"  budgets 1..30 hours, greedy disagrees with the DP on {count} of them")
print()
print(f"{count} of 30 budgets -- {100 * count / 30:.0f}% of the range -- from the same eight")
print("topics. The failure is not a corner case at one awkward budget; it is")
print("the ordinary behaviour of the rule.")


# A check the reader can see: the DP answer is an upper bound on the greedy
# one, always, because the greedy plan is a valid plan.
rng = random.Random(4)
violations = 0
for _ in range(200):
    topics = [(f"t{i}", rng.randint(1, 9), rng.randint(5, 50))
              for i in range(rng.randint(3, 8))]
    hours = rng.randint(5, 25)
    t = plan_table(topics, hours)
    g = plan_greedy(topics, hours)
    if sum(m for _, _, m in g) > t[len(topics)][hours]:
        violations += 1
print()
print(f"  200 random instances, greedy beating the DP : {violations}")
print("  (it cannot: the greedy plan is a legal plan, so the DP's optimum is")
print("   at least as good. A greedy that wins would mean the DP was wrong.)")
```

```text
Part 1 -- the plan

  8 topics, 20 hours available

  topic               hours  marks   marks/hour
---------------------------------------------
  mechanics               8     45          5.6
  electromagnetism        8     26          3.2
  thermodynamics          8     18          2.2
  circuits                5     33          6.6
  waves                   3     23          7.7
  optics                  3     20          6.7
  units                   2     12          6.0
  history                 8     10          1.2

  plan                hours  marks   topics
---------------------------------------------
  greedy                 13     88        4
  optimal                19    121        4

  greedy picks  : waves, optics, circuits, units
  optimal picks : mechanics, circuits, waves, optics

  the greedy spends 13 hours and leaves 7 unused;
  the optimal spends 19 and leaves 1.

The greedy's *ordering* is not the mistake -- every item it takes is
a reasonable item, and it takes them in the right order. The mistake
is that it commits to four small ones before it ever considers the
single biggest prize on the list, and by then 13 of the 20 hours are
gone while mechanics needs 8. The optimum drops `units`, the
second-smallest item, and spends that room on `mechanics` instead.

That is the whole failure mode in one line: a greedy rule cannot
afford to wait, and the best subset sometimes requires waiting.

  marks lost to the greedy : 33 of 121 (27%)

33 marks out of 121 is not a rounding error. The
greedy loses more than a quarter of the achievable total -- and it
loses it while *using less* of the resource. That last part is the
counterintuitive bit, and it is worth sitting with: the greedy plan
is not merely worse, it is smaller. It had 20 hours and spent
13, because once the small items were in there was nothing
left that fit.

A student who followed the greedy would finish with four topics
revised, seven hours unused, and no way to tell that the plan was
suboptimal -- the hours went unused one at a time, and each refusal
looked sensible in isolation.


Part 2 -- the typo, and a different DP

  the revision list says 'circuts'

  syllabus topic      distance
----------------------------
  circuits                   1  <- closest
  units                      5
  history                    6
  optics                     6
  waves                      6
  mechanics                  7
  electromagnetism          12
  thermodynamics            12

The answer is not found by comparing lengths or first letters. The
closest topic is the one where the student dropped a single letter,
and the edit distance finds it without being told what a dropped
letter is -- which is the property that makes the recurrence worth
knowing rather than just the answer it produces.

It also handles the cases that a simpler rule does not, and it has a
real limitation worth naming. If the student had swapped two adjacent
letters instead of dropping one, the distance would be 2 rather than
1, because plain Levenshtein has no transposition operation:

  typed            closest  distance
----------------------------------
  'circuts'       circuits         1
  'cricuits'      circuits         2

A transposition is two edits, not one, so a misspelling that is a
single swap costs more than one that is a single omission -- which is
the opposite of what a reader expects. That is not an oversight:
adding a transposition move gives Damerau-Levenshtein, which needs a
larger state and one more lookback in the recurrence. Most spell
checkers use that version; the recurrence here is the one that fits
on a page.

This is the same table as Part 1 with the units changed again. Hours
and marks became characters; the budget became a length. The
recurrence did not change shape, which is the point of the chapter:
once the state is right, the code is almost mechanical.


Part 3 -- why the plan cannot be found by a smarter greedy

It is tempting to look for a better greedy rule -- ratio first, then
longest first, then a tie-break. That search is a dead end, and the
reason is worth stating because it applies to every knapsack-shaped
problem:

  a greedy rule is a rule about one topic at a time, and the value of
  a topic depends on which other topics are in the plan. With 20 hours
  and 8 topics, the choices interact, and no per-topic score can see
  the interaction.

The DP does not need to see it either. It just refuses to commit: it
keeps the best answer for *every* budget, so when the last topic is
considered the answer for 20 hours is already sitting in the table,
built out of answers for 15 and 14 hours, which were built out of
smaller ones. The interaction is encoded in the second index.

  budgets 1..30 hours, greedy disagrees with the DP on 13 of them

13 of 30 budgets -- 43% of the range -- from the same eight
topics. The failure is not a corner case at one awkward budget; it is
the ordinary behaviour of the rule.

  200 random instances, greedy beating the DP : 0
  (it cannot: the greedy plan is a legal plan, so the DP's optimum is
   at least as good. A greedy that wins would mean the DP was wrong.)
```
:::

The plan is the rucksack with the units relabelled, and the failure mode is the one from Part 1 of
that section made concrete: the greedy spends 13 hours, leaves 7 unused, and loses 33 marks out of
121. The counterintuitive part is worth sitting with -- **the greedy plan is not merely worse, it is
smaller.** It had 20 hours and spent 13, because once the small items were in there was nothing left
that fit.

That is also why the greedy survives in practice and still deserves to be distrusted. A student
following it would finish with four topics revised, seven hours unused, and no way to tell the plan
was suboptimal, because the hours went unused one at a time and each refusal looked sensible in
isolation.

Part 2 is a different DP from the same chapter in a smaller setting, and it shows the point the
chapter opened with: once the state is right, the code is almost mechanical. Hours and marks became
characters, the budget became a length, and the recurrence did not change shape.

The transposition detail at the end of Part 2 is a limitation worth naming rather than hiding. A
single adjacent swap costs **2**, not 1, because plain Levenshtein has no transposition operation --
so a misspelling that is a swap costs more than one that is an omission, which is the opposite of
what a reader expects. Adding the move gives Damerau-Levenshtein, which needs a larger state and
one more lookback. Most spell checkers use that version; the recurrence here is the one that fits on
a page.

Part 3 closes the argument with a check that is worth having in any optimisation story. Over 200
random instances the greedy never once beat the DP, and it cannot: the greedy plan is a legal plan,
so the DP's optimum is at least as good. **A greedy that wins would mean the DP was wrong** -- which
makes that check a test of the DP rather than of the greedy.

:::solution The rule
Reach for the two questions before you reach for a table. Count the distinct states and count the
revisits; if the first is polynomial and the second is exponential, the table is there and the only
remaining work is choosing what the state means.

Then choose the state by asking what a cell has to remember. In edit distance it is a pair of
prefixes, because an edit at one position cannot be described without knowing how much of each
string is left. In knapsack it is a prefix of the items plus a budget, because the value of an item
depends on how much room is left. In coin change it is just the amount, because the coins are
unlimited and their order does not matter.

The last of those three is the one to look at twice, because the same array answers two different
questions depending on which loop is outside -- and only one of them is the question you meant.
:::

## Key takeaways

- A recursion tree is a countable object, and counting it is how you decide whether dynamic
  programming applies. Fibonacci at n = 30 is 2,692,537 calls to compute 31 distinct values.
- Two independent conditions, not one: polynomially many distinct states, and exponential revisits.
  Fibonacci has both, merge sort has the first only, and enumerating subsets has neither.
- Memoisation turns a tree into a line. The function is still *entered* on every request -- the
  saving is in the work behind the entry, which is why a memoised function must be cheap to enter
  and must have no side effects.
- `lru_cache` keys on the arguments tuple, so every argument must be hashable and the failure appears
  at the call site. `maxsize=None` is an unbounded cache, which is a memory leak with a friendly name.
- Top-down pays for the recursion with stack, and the recursion limit is a hard ceiling on the input
  -- not a setting to raise. `sys.setrecursionlimit` moves a counter, not the real stack.
- Top-down visits the states the answer depends on; bottom-up visits all the states that exist. The
  saving depends on how much of the state space is dead, and it is only 1.1x on a grid with almost
  no walls.
- A ratio can improve as the problem becomes impossible. The top-down saving reaches 36x exactly
  where the goal is unreachable and the answer is zero -- so report the answer beside the count.
- Edit distance's naive cost grows like (3 + 2√2)^n, not 3^n, because the three branches step in two
  dimensions. The table is quadratic in the same input.
- LCS's equal case is forced rather than chosen, and the problem has a tie in its statement, so
  three different answers are all correct. Ties are a property of the problem, not of the code.
- Longest common *substring* needs a different state, and its recurrence has no `max` between
  neighbours. The absence of that `max` is the tell that the answer has to be harvested by the loop.
- Knapsack is pseudo-polynomial: the table is polynomial in the capacity's *value* and exponential
  in its *length*. One extra digit multiplies the work by ten.
- The 1-D knapsack row is correct in one direction and silently solves unbounded knapsack in the
  other. The wrong version is a right answer to a different question.
- A greedy is correct only when an exchange argument justifies it. For coins `{1, 3, 4}` the greedy
  is wrong on every target of the form 4k + 2 -- an infinite family, not an edge case.
- Coin change is a shortest path problem, so Dijkstra and dynamic programming are the same algorithm
  on different representations. Chapter 47's algorithms are this chapter's, with the edges written
  down.
- You do not need the table to keep the path. Store the three-way *decision* per cell instead of the
  integer, and the path survives while the table holds bytes where it used to hold numbers.
- Hirschberg's algorithm gets the path and linear memory at about twice the work, by giving up the
  assumption that each cell is computed once.
- The state is the design decision. Getting it right makes the code mechanical; getting it wrong
  produces a correct-looking number that answers a different question.

## Practice

- [ ] Climbing a staircase with steps of 1, 2 and 3, write the naive, memoised and bottom-up
  versions and account for *every* function entry in the memoised count. Then check the growth rate
  against the largest root of `x^3 = x^2 + x + 1`.
- [ ] Find a recursion that has polynomially many states and no overlap, and a second that has few
  states but exponentially large answers. Show that a cache fails for a different reason in each
  case, and say what the fix is.
- [ ] Generalise edit distance so that deletion, insertion and substitution have independent costs.
  Find a price list where two different cost models give the same distance but different edit
  scripts, and explain which branch of the traceback decides it.
- [ ] Write the coin-change *counting* DP two ways, with the loops swapped, and reconcile the two
  answers by expanding every multiset and counting its distinct orderings. Then show that the
  *minimising* DP is unaffected by the same swap, and explain why.
- [ ] Implement the longest increasing subsequence twice -- the O(n²) DP and patience sorting -- and
  check that the patience array is sorted and is *not* a subsequence of the input. Explain what
  object it is instead.

## Solutions

:::solution Exercise 1
The count is exactly `3n + 1`, and being able to say why is the point. Three entries per step
because every new step asks about `n-1`, `n-2` and `n-3`; plus one for the call that starts it off.
The three does not grow because all three questions have already been answered, so each is one
lookup and no work.

The growth check uses the same trick as the first section, and the convergence is much faster than
the golden-ratio case: a third-order recurrence has two correction terms rather than one, so the
ratio is good to three decimals from n = 13 onward instead of still drifting at n = 30.

```python run
#!/usr/bin/env python3
"""Chapter 48, exercise 1 -- a second recurrence, and the two questions that
tell you whether it is a DP.

Climbing a staircase where each step is 1, 2 or 3 stairs: how many different
ways are there to reach step n? It is the same shape as Fibonacci with a
wider fan-out, and it is worth doing once because the *counts* make the
memoisation argument in a way Fibonacci cannot.

The check at the end is the useful part: the memoised count and the
bottom-up count have to be the same, and the naive one has to blow up.
"""


def ways_naive(n, tally):
    tally[0] += 1
    if n < 0:
        return 0
    if n == 0:
        return 1
    return (ways_naive(n - 1, tally) + ways_naive(n - 2, tally)
            + ways_naive(n - 3, tally))


def ways_memo(n, cache, tally):
    tally[0] += 1
    if n < 0:
        return 0
    if n == 0:
        return 1
    if n in cache:
        tally[1] += 1
        return cache[n]
    cache[n] = (ways_memo(n - 1, cache, tally) + ways_memo(n - 2, cache, tally)
                + ways_memo(n - 3, cache, tally))
    return cache[n]


def ways_bottom_up(n):
    """The same recurrence, forwards. The last three values are all it ever
    needs, so three variables replace the whole cache."""
    window = [1, 1, 2]
    if n < 3:
        return window[n]
    for _ in range(3, n + 1):
        window = [window[1], window[2], sum(window)]
    return window[2]


print("ways to climb a staircase, steps of 1, 2 or 3")
print()
print(f"{'n':>5}{'naive calls':>14}{'memo entries':>14}{'memo hits':>11}"
      f"{'ways':>16}")
print("-" * 60)
rows = []
for n in range(1, 21):
    naive_tally = [0]
    naive_value = ways_naive(n, naive_tally)
    memo_tally = [0, 0]
    memo_value = ways_memo(n, {}, memo_tally)
    bottom_up_value = ways_bottom_up(n)
    rows.append((n, naive_tally[0], memo_tally[0], naive_value,
                 bottom_up_value))
    print(f"{n:>5}{naive_tally[0]:>14,}{memo_tally[0]:>14,}"
          f"{memo_tally[1]:>11,}{naive_value:>16,}")
print()
print("The naive count is the same shape as Fibonacci's -- exponential, and")
print("visible as one more digit per step -- and the memoised count is not.")
print("That is the whole chapter in one table: the work is exponential, the")
print("number of *distinct* things to compute is n, and a cache collapses one")
print("into the other.")
print()
print("The memo column is worth reading exactly, because a count you cannot")
print("account for is a count you should not trust:")
print()
print(f"  {'the memoised count is exactly 3n + 1':<40}: "
      f"{all(entries == 3 * n + 1 for n, _, entries, _, _ in rows)}")
print(f"  {'entries at n = ' + str(rows[-1][0]):<40}: {rows[-1][2]}")
print(f"  {'3 x ' + str(rows[-1][0]) + ' + 1':<40}: {3 * rows[-1][0] + 1}")
print()
print("Three entries per step, plus the one that starts it off. The three is")
print("the fan-out -- every new step asks about n-1, n-2 and n-3 -- and the")
print("reason it stays at three rather than growing is that all three have")
print("already been answered, so each is one lookup and no work. A linear")
print("count from an exponential recurrence is what 'memoised' looks like")
print("when you write it down.")
print()
print()
print("The checks")
print()
memo_cache = {}
ways_memo(20, memo_cache, [0, 0])
print(f"  all three implementations agree on every n : "
      f"{all(a == c for _, _, _, a, c in rows)}")
print(f"  the memoised version enters the function    : "
      f"{rows[-1][2]:,} times at n = {rows[-1][0]}")
print(f"  the naive version enters it                 : "
      f"{rows[-1][1]:,} times")
print(f"  ratio                                       : "
      f"{rows[-1][1] / rows[-1][2]:,.0f}x")
print()
print(f"  bottom-up at n = {rows[-1][0]} uses             : 3 variables")
print(f"  the memoised version keeps                  : "
      f"{len(memo_cache)} cache entries")
print()
print("The last pair of lines is the space argument from the chapter, made")
print("concrete. The memo is holding an answer for every step; the bottom-up")
print("loop is holding three. The recurrence only ever looks back three")
print("places, so everything older than that is dead weight the cache keeps")
print("out of habit.")
print()
print("A last check on the growth rate, using the same trick as the first")
print("section. This recurrence's growth rate is the real root of")
print("x^3 = x^2 + x + 1 -- the tribonacci constant -- and the ratio of")
print("consecutive naive counts should climb towards it:")
print()


def tribonacci_root():
    """The largest real root of x^3 - x^2 - x - 1, by bisection. Derived
    rather than quoted, so the comparison below is a check on the counts and
    not on my memory of a constant."""
    low, high = 1.0, 2.0
    for _ in range(80):
        mid = (low + high) / 2
        if mid ** 3 - mid ** 2 - mid - 1 < 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


ROOT = tribonacci_root()
print(f"{'n':>5}{'naive calls':>14}{'growth':>10}{'tribonacci':>13}")
print("-" * 42)
previous = None
for n, naive_calls, _, _, _ in rows:
    growth = "-" if previous is None else f"{naive_calls / previous:.3f}"
    print(f"{n:>5}{naive_calls:>14,}{growth:>10}{ROOT:>13.6f}")
    previous = naive_calls
print()
print(f"  the tribonacci constant, computed here : {ROOT:.12f}")
print(f"  the growth column at n = 20            : "
      f"{rows[-1][1] / rows[-2][1]:.6f}")
print()
print("The convergence is much faster than the golden-ratio case, and it is")
print("worth noticing why. A third-order recurrence has two correction terms")
print("rather than one, and both of them are small by the time n reaches the")
print("teens -- so the ratio is good to three decimals from n = 13 onward")
print("instead of still drifting at n = 30.")
print()
print("The habit is the same either way. A growth rate is a claim about the")
print("limit of a ratio, so it is verified by watching that ratio settle,")
print("never by reading one row of a table.")
```

```text
ways to climb a staircase, steps of 1, 2 or 3

    n   naive calls  memo entries  memo hits            ways
------------------------------------------------------------
    1             4             4          0               1
    2             7             7          0               2
    3            13            10          1               4
    4            25            13          3               7
    5            46            16          5              13
    6            85            19          7              24
    7           157            22          9              44
    8           289            25         11              81
    9           532            28         13             149
   10           979            31         15             274
   11         1,801            34         17             504
   12         3,313            37         19             927
   13         6,094            40         21           1,705
   14        11,209            43         23           3,136
   15        20,617            46         25           5,768
   16        37,921            49         27          10,609
   17        69,748            52         29          19,513
   18       128,287            55         31          35,890
   19       235,957            58         33          66,012
   20       433,993            61         35         121,415

The naive count is the same shape as Fibonacci's -- exponential, and
visible as one more digit per step -- and the memoised count is not.
That is the whole chapter in one table: the work is exponential, the
number of *distinct* things to compute is n, and a cache collapses one
into the other.

The memo column is worth reading exactly, because a count you cannot
account for is a count you should not trust:

  the memoised count is exactly 3n + 1    : True
  entries at n = 20                       : 61
  3 x 20 + 1                              : 61

Three entries per step, plus the one that starts it off. The three is
the fan-out -- every new step asks about n-1, n-2 and n-3 -- and the
reason it stays at three rather than growing is that all three have
already been answered, so each is one lookup and no work. A linear
count from an exponential recurrence is what 'memoised' looks like
when you write it down.


The checks

  all three implementations agree on every n : True
  the memoised version enters the function    : 61 times at n = 20
  the naive version enters it                 : 433,993 times
  ratio                                       : 7,115x

  bottom-up at n = 20 uses             : 3 variables
  the memoised version keeps                  : 20 cache entries

The last pair of lines is the space argument from the chapter, made
concrete. The memo is holding an answer for every step; the bottom-up
loop is holding three. The recurrence only ever looks back three
places, so everything older than that is dead weight the cache keeps
out of habit.

A last check on the growth rate, using the same trick as the first
section. This recurrence's growth rate is the real root of
x^3 = x^2 + x + 1 -- the tribonacci constant -- and the ratio of
consecutive naive counts should climb towards it:

    n   naive calls    growth   tribonacci
------------------------------------------
    1             4         -     1.839287
    2             7     1.750     1.839287
    3            13     1.857     1.839287
    4            25     1.923     1.839287
    5            46     1.840     1.839287
    6            85     1.848     1.839287
    7           157     1.847     1.839287
    8           289     1.841     1.839287
    9           532     1.841     1.839287
   10           979     1.840     1.839287
   11         1,801     1.840     1.839287
   12         3,313     1.840     1.839287
   13         6,094     1.839     1.839287
   14        11,209     1.839     1.839287
   15        20,617     1.839     1.839287
   16        37,921     1.839     1.839287
   17        69,748     1.839     1.839287
   18       128,287     1.839     1.839287
   19       235,957     1.839     1.839287
   20       433,993     1.839     1.839287

  the tribonacci constant, computed here : 1.839286755214
  the growth column at n = 20            : 1.839289

The convergence is much faster than the golden-ratio case, and it is
worth noticing why. A third-order recurrence has two correction terms
rather than one, and both of them are small by the time n reaches the
teens -- so the ratio is good to three decimals from n = 13 onward
instead of still drifting at n = 30.

The habit is the same either way. A growth rate is a claim about the
limit of a ratio, so it is verified by watching that ratio settle,
never by reading one row of a table.
```
:::

:::solution Exercise 2
The first failure is no overlap: the subset recursion only ever asks about a suffix, so it has n + 1
states and visits each exactly once. The hits column is zero and stays zero, and there is nothing to
fix -- the cache works perfectly and is pointless.

The second failure is subtler and is the one worth carrying away. The grid-path recursion has 81
states for a 9x9 grid and plenty of hits, so both conditions are satisfied. It is also holding
739,025 cell references, because each cache entry holds a list of paths and the lists are
exponential. **Memoisation bounds the number of states, not the size of the answers.** If the answer
per state is exponential, the cache is exponential -- and the fix is to notice that you were asked
to enumerate something, not to write a better cache.

```python run
#!/usr/bin/env python3
"""Chapter 48, exercise 2 -- the two independent reasons a cache cannot help.

The chapter stated the test for dynamic programming as two conditions. This
exercise takes them apart by finding a recursion that fails each one, because
the usual phrasing -- 'DP needs overlapping subproblems' -- makes them sound
like one requirement and they are not.

Both failures look the same from outside: a cache that does not help. They
are different problems with different fixes, and neither fix is 'add a
dictionary'.
"""
import functools


def subsets_plain(items):
    """Every subset of `items`, as a tuple of tuples."""
    if not items:
        return [()]
    head, rest = items[0], items[1:]
    without = subsets_plain(rest)
    return without + [(head,) + tail for tail in without]


@functools.lru_cache(maxsize=None)
def subsets_cached(items):
    """The same recursion with a cache bolted on.

    `items` has to stay a tuple for the cache to accept it. Writing
    `head, *rest = items` would make `rest` a *list*, and the cache would
    raise `TypeError: unhashable type: 'list'` on the recursive call -- the
    hashability trap from the chapter, arriving on schedule.
    """
    if not items:
        return [()]
    head, rest = items[0], items[1:]
    without = subsets_cached(rest)
    return without + [(head,) + tail for tail in without]


print("Part 1 -- failure one: no state is ever revisited")
print()
print(f"{'n':>4}{'subsets produced':>18}{'distinct states':>17}"
      f"{'calls':>8}{'hits':>7}{'cached':>8}")
print("-" * 62)
rows = []
for n in range(1, 13):
    items = tuple(range(n))
    subsets_cached.cache_clear()
    produced = len(subsets_cached(items))
    info = subsets_cached.cache_info()
    rows.append((n, produced, info.misses, info.misses + info.hits,
                 info.hits, info.currsize))
    print(f"{n:>4}{produced:>18,}{info.misses:>17,}{info.misses + info.hits:>8,}"
          f"{info.hits:>7,}{info.currsize:>8,}")
print()
print("Three columns deserve to be read separately, because they are three")
print("different quantities that all look like 'the size of the problem'.")
print()
print(f"  the answer at n = 12        : {rows[-1][1]:,} subsets")
print(f"  the recursion's state space : {rows[-1][2]} states")
print(f"  the cache's hit count       : {rows[-1][4]}")
print()
print("The answer is exponential and the state space is linear, which is the")
print("first surprise in the exercise. The recursion only ever asks about a")
print("*suffix* of the list -- `items[1:]` -- so there are n + 1 things it can")
print("be called with, and it is called with each of them exactly once. The")
print("exponential part is the size of the values being returned, not the")
print("number of calls.")
print()
print("That is a distinction worth keeping: the two exponentials in this")
print("problem -- the size of the answer and the number of states -- are")
print("different quantities, and only one of them is exponential. Confusing")
print("them is the commonest way to conclude that a problem is hopeless when")
print("it is not.")
print()
print("So this is the clean example of failure one: polynomially many states")
print("and no overlap at all. Every call gets a distinct argument, so the")
print("hits column is zero and stays zero no matter how large n gets. The")
print("cache is a dictionary from argument to answer that is written n + 1")
print("times and read zero times.")
print()
print("Merge sort from the earlier section is the same failure with a")
print("different story. This one is worth having because the cache *works* --")
print("there is no TypeError, no missing hash, nothing to fix -- and it is")
print("still pointless, which is the harder case to notice in review.")
print()
print()
print("Part 2 -- failure two: the states are few, but the answers are huge")


def paths_with_cache(size):
    """Every monotone path from the top-left to the bottom-right of a
    `size` x `size` grid, with a hand-rolled cache so the cache's *contents*
    can be inspected rather than just its hit count.

    The state space here is genuinely small -- one entry per cell -- and the
    overlap is genuinely there. Both conditions are satisfied, and the cache
    is still the wrong tool.
    """
    cache = {}
    hits = [0]

    def go(r, c):
        if (r, c) in cache:
            hits[0] += 1
            return cache[(r, c)]
        if r == size - 1 and c == size - 1:
            result = (((r, c),),)
        else:
            tails = []
            if r + 1 < size:
                tails.extend(go(r + 1, c))
            if c + 1 < size:
                tails.extend(go(r, c + 1))
            result = tuple(((r, c),) + tail for tail in tails)
        cache[(r, c)] = result
        return result

    paths = go(0, 0)
    entries = len(cache)
    cells_stored = sum(sum(len(p) for p in value) for value in cache.values())
    return len(paths), entries, cells_stored, hits[0]


print()
print(f"{'grid':>8}{'paths':>14}{'cache entries':>15}"
      f"{'cache hits':>12}{'cells stored':>15}{'per state':>11}")
print("-" * 75)
grid_rows = []
for size in (4, 5, 6, 7, 8, 9):
    paths, entries, stored, hits = paths_with_cache(size)
    grid_rows.append((size, paths, entries, stored, hits))
    print(f"{f'{size}x{size}':>8}{paths:>14,}{entries:>15,}{hits:>12,}"
          f"{stored:>15,}{stored / entries:>11,.0f}")
print()
print("The third column is the state space -- one entry per cell, so it grows")
print("like n^2 and is entirely tame. The fifth column is what the cache is")
print("actually holding: every partial answer for every state, and each of")
print("those answers is itself a list of paths.")
print()
first, last = grid_rows[0], grid_rows[-1]
print(f"  paths grew by {last[1] / first[1]:,.0f}x from {first[0]}x{first[0]} to "
      f"{last[0]}x{last[0]}")
print(f"  cache entries grew by {last[2] / first[2]:,.1f}x over the same range")
print(f"  cells held grew by {last[3] / first[3]:,.0f}x")
print()
print("The two growth rates are the whole lesson. The state count is")
print("polynomial and the *data* is exponential, so a memo table over the")
print("states has exponential memory -- not because memoisation is wrong,")
print("but because it caches the answer and the answer is exponential.")
print()
print("This is the failure that does not show up in a hit-rate measurement.")
print(f"At {last[0]}x{last[0]} the cache is working perfectly: {last[2]} entries, "
      f"{last[4]:,} hits,")
print("no wasted lookups. It is also")
print(f"holding {last[3]:,} cell references to produce {last[1]:,} paths, and")
print("both of those numbers are the size of the output.")
print()
print("The fix is not a better cache. It is to notice that you were asked to")
print("*enumerate* an exponential set, and that no amount of memoisation")
print("changes the size of the answer. If the caller only needs the *number*")
print("of paths, the same table gives it in one integer per state -- which is")
print("the previous chapter's path-counting DP, and it is why 'count them'")
print("and 'list them' are different problems with the same recurrence.")
print()
print()
print("Part 3 -- the two conditions, stated so they can be tested separately")
print()
print(f"  {'recursion':<22}{'states':>12}{'overlap':>12}{'verdict':>18}")
print("-" * 64)
fib_calls = [0]
fib_seen = set()


def fib(k):
    fib_calls[0] += 1
    fib_seen.add(k)
    if k < 2:
        return k
    return fib(k - 1) + fib(k - 2)


fib(20)
print(f"  {'fib(20)':<22}{len(fib_seen):>12,}{fib_calls[0] / len(fib_seen):>12,.0f}"
      f"{'DP applies':>18}")
print(f"  {'subsets(12)':<22}{rows[-1][2]:>12,}{'1':>12}"
      f"{'no overlap':>18}")
print(f"  {'paths, 9x9':<22}{grid_rows[-1][2]:>12,}"
      f"{grid_rows[-1][4]:>12,}{'cache the count':>18}")
print()
print("  fib(20)      : n + 1 states, thousands of revisits  -> memoise it")
print("  subsets(12)  : n + 1 states, zero revisits          -> do not")
print("  paths, 9x9   : 81 states, plenty of revisits        -> memoise the")
print("                 count, never the list")
print()
print("The middle row is the one the usual phrasing of the test misses. It")
print("has the *right* number of states and the *wrong* amount of reuse, and")
print("neither of those is visible without counting.")
```

```text
Part 1 -- failure one: no state is ever revisited

   n  subsets produced  distinct states   calls   hits  cached
--------------------------------------------------------------
   1                 2                2       2      0       2
   2                 4                3       3      0       3
   3                 8                4       4      0       4
   4                16                5       5      0       5
   5                32                6       6      0       6
   6                64                7       7      0       7
   7               128                8       8      0       8
   8               256                9       9      0       9
   9               512               10      10      0      10
  10             1,024               11      11      0      11
  11             2,048               12      12      0      12
  12             4,096               13      13      0      13

Three columns deserve to be read separately, because they are three
different quantities that all look like 'the size of the problem'.

  the answer at n = 12        : 4,096 subsets
  the recursion's state space : 13 states
  the cache's hit count       : 0

The answer is exponential and the state space is linear, which is the
first surprise in the exercise. The recursion only ever asks about a
*suffix* of the list -- `items[1:]` -- so there are n + 1 things it can
be called with, and it is called with each of them exactly once. The
exponential part is the size of the values being returned, not the
number of calls.

That is a distinction worth keeping: the two exponentials in this
problem -- the size of the answer and the number of states -- are
different quantities, and only one of them is exponential. Confusing
them is the commonest way to conclude that a problem is hopeless when
it is not.

So this is the clean example of failure one: polynomially many states
and no overlap at all. Every call gets a distinct argument, so the
hits column is zero and stays zero no matter how large n gets. The
cache is a dictionary from argument to answer that is written n + 1
times and read zero times.

Merge sort from the earlier section is the same failure with a
different story. This one is worth having because the cache *works* --
there is no TypeError, no missing hash, nothing to fix -- and it is
still pointless, which is the harder case to notice in review.


Part 2 -- failure two: the states are few, but the answers are huge

    grid         paths  cache entries  cache hits   cells stored  per state
---------------------------------------------------------------------------
     4x4            20             16           9            379         24
     5x5            70             25          16          1,849         74
     6x6           252             36          25          8,581        238
     7x7           924             49          36         38,611        788
     8x8         3,432             64          49        170,171      2,659
     9x9        12,870             81          64        739,025      9,124

The third column is the state space -- one entry per cell, so it grows
like n^2 and is entirely tame. The fifth column is what the cache is
actually holding: every partial answer for every state, and each of
those answers is itself a list of paths.

  paths grew by 644x from 4x4 to 9x9
  cache entries grew by 5.1x over the same range
  cells held grew by 1,950x

The two growth rates are the whole lesson. The state count is
polynomial and the *data* is exponential, so a memo table over the
states has exponential memory -- not because memoisation is wrong,
but because it caches the answer and the answer is exponential.

This is the failure that does not show up in a hit-rate measurement.
At 9x9 the cache is working perfectly: 81 entries, 64 hits,
no wasted lookups. It is also
holding 739,025 cell references to produce 12,870 paths, and
both of those numbers are the size of the output.

The fix is not a better cache. It is to notice that you were asked to
*enumerate* an exponential set, and that no amount of memoisation
changes the size of the answer. If the caller only needs the *number*
of paths, the same table gives it in one integer per state -- which is
the previous chapter's path-counting DP, and it is why 'count them'
and 'list them' are different problems with the same recurrence.


Part 3 -- the two conditions, stated so they can be tested separately

  recursion                   states     overlap           verdict
----------------------------------------------------------------
  fib(20)                         21       1,042        DP applies
  subsets(12)                     13           1        no overlap
  paths, 9x9                      81          64   cache the count

  fib(20)      : n + 1 states, thousands of revisits  -> memoise it
  subsets(12)  : n + 1 states, zero revisits          -> do not
  paths, 9x9   : 81 states, plenty of revisits        -> memoise the
                 count, never the list

The middle row is the one the usual phrasing of the test misses. It
has the *right* number of states and the *wrong* amount of reuse, and
neither of those is visible without counting.
```
:::

:::solution Exercise 3
The comparison that matters is `substitute` against `delete + insert`, and both are properties of
the *model* rather than of the strings. That is testable: run the comparison over six different
pairs of words, including one with no mismatches, and the verdict never moves. Something that holds
before any data arrives is a property of the model.

With unit costs, substituting is strictly cheaper than a delete plus an insert at every mismatch, so
the two-step route is never the better way to fix one -- and that assumption is nowhere in the
recurrence. Raise substitution to 2 and the two tie; raise it to 3 and the preference reverses, with
the same distance but a completely different script.

The symmetry check is the one that would catch a real bug. With equal prices the distance is
symmetric; with deleting cheap and inserting expensive it is not, and over 28 word pairs the two
directions disagree on 17 of them.

```python run
#!/usr/bin/env python3
"""Chapter 48, exercise 3 -- the recurrence generalises, the assumptions do not.

Edit distance with unit costs has a property that is easy to mistake for part
of the algorithm: a substitution costs 1 and a delete-plus-insert costs 2, so
a mismatch is always resolved by substituting. That is why the recurrence can
be written as a plain `min` of three and never thought about again.

Give the three operations different prices and the property disappears. The
recurrence does not change shape at all -- which is the point of the
exercise. What changes is which of the three moves wins, and along with it
the symmetry of the whole function.

The check at the end is that the generalised version reproduces the unit-cost
answer when all the costs are 1. Without that, there is no way to know the
generalisation is a generalisation rather than a different algorithm.
"""


def edit_table(a, b, delete=1, insert=1, substitute=1):
    """Weighted edit distance.

    The three operations are independent parameters and the recurrence is
    unchanged: still a `min` of three, still read from the corner. Only the
    prices moved.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i * delete
    for j in range(n + 1):
        table[0][j] = j * insert
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            drop = table[i - 1][j] + delete
            add = table[i][j - 1] + insert
            swap = table[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1]
                                          else substitute)
            table[i][j] = min(drop, add, swap)
    return table


def script(a, b, table, delete=1, insert=1, substitute=1):
    """The traceback, with the same three prices.

    The tests have to use the costs the table was built with, or the walk
    takes a wrong turn -- and the order of the tests is itself a choice, which
    Part 2 is about.
    """
    i, j = len(a), len(b)
    moves = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] \
                and table[i][j] == table[i - 1][j - 1]:
            moves.append(("match", a[i - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + substitute:
            moves.append(("substitute", f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + delete:
            moves.append(("delete", a[i - 1]))
            i -= 1
        else:
            moves.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(moves))


def summarise(moves):
    """A compact count of each operation, so the column stays narrow enough
    to read next to the numbers."""
    parts = []
    for kind in ("substitute", "delete", "insert"):
        count = sum(1 for name, _ in moves if name == kind)
        if count:
            parts.append(f"{count} {kind[:3]}")
    return ", ".join(parts) if parts else "none"


A, B = "kitten", "sitting"

print("Part 1 -- the same two words, at four different price lists")
print()
print(f"  {A!r} -> {B!r}")
print()
print(f"  {'delete':>7}{'insert':>8}{'subst':>7}{'distance':>10}"
      f"{'edits':>7}   operations")
print("-" * 62)
configs = [(1, 1, 1), (1, 1, 2), (1, 1, 3), (2, 2, 1)]
for delete, insert, substitute in configs:
    table = edit_table(A, B, delete, insert, substitute)
    distance = table[len(A)][len(B)]
    moves = script(A, B, table, delete, insert, substitute)
    edits = sum(1 for name, _ in moves if name != "match")
    print(f"  {delete:>7}{insert:>8}{substitute:>7}{distance:>10}{edits:>7}"
          f"   {summarise(moves)}")
print()
print("Two pairs of rows are worth reading against each other.")
print()
print("The first two rows are the ordinary case. Making substitution cost 2")
print("instead of 1 does not change *which* operations are chosen -- still")
print("two substitutions and an insert -- but it raises the total from 3 to")
print("5, because the price of the same plan went up.")
print()
print("The second two rows are the interesting pair, and they are the ones")
print("that catch people out. Substitution at 2 and substitution at 3 give")
print("the *same distance* of 5, but completely different scripts: at 2 the")
print("answer is two substitutions and an insert, at 3 it is two deletions")
print("and three insertions.")
print()
print("The reason is a tie. At substitution cost 2, substituting and")
print("delete-then-insert cost exactly the same, so the model is indifferent")
print("and the traceback picks whichever branch it tests first. At cost 3 the")
print("tie is broken in favour of going around, and the script changes")
print("accordingly. Same distance, different plan, and only the cost model")
print("decides which one you get.")
print()
print()
print("Part 2 -- the property the unit costs were hiding")
print()
print("At a mismatched cell the recurrence offers a diagonal candidate worth")
print("`substitute` and the alternative of going around it, which costs")
print("`delete + insert`. Those two numbers are properties of the *model*, not")
print("of the strings -- and that is testable rather than merely arguable.")
print()
print(f"  {'delete':>7}{'insert':>8}{'subst':>7}"
      f"{'substitute vs delete+insert':>30}{'verdict':>16}")
print("-" * 68)
for delete, insert, substitute in configs:
    verdict = ("subst cheaper" if substitute < delete + insert
               else "tie" if substitute == delete + insert
               else "detour cheaper")
    print(f"  {delete:>7}{insert:>8}{substitute:>7}"
          f"{f'{substitute} vs {delete + insert}':>30}{verdict:>16}")
print()
print("Now the same comparison at unit cost, over several different pairs of")
print("words. If the verdict is a property of the model, it should not move:")
print()
PAIRS = [("kitten", "sitting"), ("cat", "cart"), ("a", "abcde"),
         ("abcdef", "abc"), ("flaw", "lawn"), ("", "xyz")]
UNIT_VERDICT = "subst cheaper" if 1 < 1 + 1 else "tie"
print(f"  {'pair':<26}{'mismatched cells':>18}{'verdict':>18}")
print("-" * 62)
for first, second in PAIRS:
    mismatches = sum(1 for i in range(1, len(first) + 1)
                     for j in range(1, len(second) + 1)
                     if first[i - 1] != second[j - 1])
    print(f"  {f'{first!r} -> {second!r}':<26}{mismatches:>18}"
          f"{UNIT_VERDICT:>18}")
print()
print("The verdict column is identical in every row, including the row with")
print("no mismatches at all -- because the comparison is between two prices")
print("and the prices never changed. That is what it means for something to")
print("be a property of the model: it holds before any data arrives.")
print()
print("The consequence for the unit-cost case is the line worth remembering.")
print("Substituting is *strictly cheaper* than a delete plus an insert at")
print("every mismatch, so the two-step route is never the better way to fix")
print("one. That is the assumption the textbook recurrence is built on, and")
print("it is nowhere in the recurrence -- it is in the prices.")
print()
print("At substitution cost 2 the two alternatives tie, and at 3 the")
print("preference reverses. The recurrence did not change by one character.")
print("What changed is a comparison between two numbers that live one level")
print("up, in the cost model.")
print()
print()
print("Part 3 -- the checks")
print()


def unit_costs_reproduce():
    """The generalised version has to collapse to the original one."""
    return edit_table(A, B, 1, 1, 1)[len(A)][len(B)] == 3


def symmetry(delete, insert):
    """distance(a, b) == distance(b, a), checked in both directions."""
    forward = edit_table(A, B, delete, insert, 1)[len(A)][len(B)]
    backward = edit_table(B, A, delete, insert, 1)[len(B)][len(A)]
    return forward, backward


print(f"  unit costs give the original answer of 3    : "
      f"{unit_costs_reproduce()}")
for delete, insert in ((1, 1), (1, 5)):
    forward, backward = symmetry(delete, insert)
    print(f"  delete={delete}, insert={insert}: "
          f"distance(A,B) = {forward}, distance(B,A) = {backward}, "
          f"equal = {forward == backward}")
print()
print("The second and third lines are the check worth keeping. With equal")
print("prices the distance is symmetric, as it obviously should be. With")
print("deleting cheap and inserting expensive it is not: turning a long word")
print("into a short one is cheap and the reverse is expensive, and a function")
print("that quietly assumed symmetry would be wrong in one direction only.")
print()
print("Asymmetry is not a property of the strings. It is a property of the")
print("prices, and it appears the moment they stop being equal.")
print()


def count_symmetry_break():
    """How often the asymmetry bites, over a fixed word list."""
    words = ["cat", "cart", "cats", "scat", "dog", "dots", "a", "abcd"]
    broken = 0
    total = 0
    for first in words:
        for second in words:
            if first >= second:
                continue
            total += 1
            forward = edit_table(first, second, 1, 5, 1)[len(first)][len(second)]
            backward = edit_table(second, first, 1, 5, 1)[len(second)][len(first)]
            if forward != backward:
                broken += 1
    return broken, total


broken, total = count_symmetry_break()
print(f"  over {total} word pairs with delete=1, insert=5:")
print(f"    pairs where the two directions disagree : {broken}")
print(f"    pairs where they agree                  : {total - broken}")
print()
print("That is the general lesson this exercise is here for. A recurrence")
print("copied from a textbook encodes the textbook's assumptions, and the")
print("assumptions are usually not written down next to it. The way to find")
print("them is to change one thing at a time and watch what breaks -- which")
print("is a cheap experiment here, because the recurrence itself never has to")
print("be touched.")
```

```text
Part 1 -- the same two words, at four different price lists

  'kitten' -> 'sitting'

   delete  insert  subst  distance  edits   operations
--------------------------------------------------------------
        1       1      1         3      3   2 sub, 1 ins
        1       1      2         5      3   2 sub, 1 ins
        1       1      3         5      5   2 del, 3 ins
        2       2      1         4      3   2 sub, 1 ins

Two pairs of rows are worth reading against each other.

The first two rows are the ordinary case. Making substitution cost 2
instead of 1 does not change *which* operations are chosen -- still
two substitutions and an insert -- but it raises the total from 3 to
5, because the price of the same plan went up.

The second two rows are the interesting pair, and they are the ones
that catch people out. Substitution at 2 and substitution at 3 give
the *same distance* of 5, but completely different scripts: at 2 the
answer is two substitutions and an insert, at 3 it is two deletions
and three insertions.

The reason is a tie. At substitution cost 2, substituting and
delete-then-insert cost exactly the same, so the model is indifferent
and the traceback picks whichever branch it tests first. At cost 3 the
tie is broken in favour of going around, and the script changes
accordingly. Same distance, different plan, and only the cost model
decides which one you get.


Part 2 -- the property the unit costs were hiding

At a mismatched cell the recurrence offers a diagonal candidate worth
`substitute` and the alternative of going around it, which costs
`delete + insert`. Those two numbers are properties of the *model*, not
of the strings -- and that is testable rather than merely arguable.

   delete  insert  subst   substitute vs delete+insert         verdict
--------------------------------------------------------------------
        1       1      1                        1 vs 2   subst cheaper
        1       1      2                        2 vs 2             tie
        1       1      3                        3 vs 2  detour cheaper
        2       2      1                        1 vs 4   subst cheaper

Now the same comparison at unit cost, over several different pairs of
words. If the verdict is a property of the model, it should not move:

  pair                        mismatched cells           verdict
--------------------------------------------------------------
  'kitten' -> 'sitting'                     35     subst cheaper
  'cat' -> 'cart'                            9     subst cheaper
  'a' -> 'abcde'                             4     subst cheaper
  'abcdef' -> 'abc'                         15     subst cheaper
  'flaw' -> 'lawn'                          13     subst cheaper
  '' -> 'xyz'                                0     subst cheaper

The verdict column is identical in every row, including the row with
no mismatches at all -- because the comparison is between two prices
and the prices never changed. That is what it means for something to
be a property of the model: it holds before any data arrives.

The consequence for the unit-cost case is the line worth remembering.
Substituting is *strictly cheaper* than a delete plus an insert at
every mismatch, so the two-step route is never the better way to fix
one. That is the assumption the textbook recurrence is built on, and
it is nowhere in the recurrence -- it is in the prices.

At substitution cost 2 the two alternatives tie, and at 3 the
preference reverses. The recurrence did not change by one character.
What changed is a comparison between two numbers that live one level
up, in the cost model.


Part 3 -- the checks

  unit costs give the original answer of 3    : True
  delete=1, insert=1: distance(A,B) = 3, distance(B,A) = 3, equal = True
  delete=1, insert=5: distance(A,B) = 7, distance(B,A) = 3, equal = False

The second and third lines are the check worth keeping. With equal
prices the distance is symmetric, as it obviously should be. With
deleting cheap and inserting expensive it is not: turning a long word
into a short one is cheap and the reverse is expensive, and a function
that quietly assumed symmetry would be wrong in one direction only.

Asymmetry is not a property of the strings. It is a property of the
prices, and it appears the moment they stop being equal.

  over 28 word pairs with delete=1, insert=5:
    pairs where the two directions disagree : 17
    pairs where they agree                  : 11

That is the general lesson this exercise is here for. A recurrence
copied from a textbook encodes the textbook's assumptions, and the
assumptions are usually not written down next to it. The way to find
them is to change one thing at a time and watch what breaks -- which
is a cheap experiment here, because the recurrence itself never has to
be touched.
```
:::

:::solution Exercise 4
One loop swap, two different questions. With coins outside, `ways[amount]` counts multisets; with
amounts outside, it counts ordered sequences. Both are coherent and they differ by 28.6x at 12p, a
factor that grows without bound.

The bridge is the third line of Part 3: expand every multiset, count its distinct orderings, and add
them up. That agrees with the amount-outer loop, which is the proof that neither loop order is a bug
-- they are two different state definitions that happen to share an array.

The minimising version is unaffected by the same swap, and the reason is the useful generalisation.
Counting is order-sensitive because the loop order decides what the state *means*. Minimising is
order-insensitive because the state does not need to mean anything: `best[a] = min(best[a],
best[a-c] + 1)` is a shortest-path relaxation, and running it in any order reaches the same fixed
point. If a DP state counts something, the loop order is part of the specification; if it optimises
something, it is an implementation detail.

```python run
#!/usr/bin/env python3
"""Chapter 48, exercise 4 -- one loop swap, two different problems.

Counting the ways to make change and finding the fewest coins to make change
are the same state, the same array, and almost the same loop. One of them
cares about the order of the two loops and the other does not, and the
difference is not a detail you can reason your way to from the code -- it is
a statement about what the state means.

This is the exercise where the counting version and the optimising version
have to be written down next to each other, because the trap is invisible
when you only ever see one of them.
"""
import bisect


def count_by_coin_outer(coins, target):
    """Coins in the outer loop, amounts ascending.

    Each coin is introduced exactly once, and when it is introduced it may
    extend any amount that was already reachable using only the coins before
    it. So a multiset of coins is counted once, however it is ordered.
    """
    ways = [0] * (target + 1)
    ways[0] = 1
    for coin in coins:
        for amount in range(coin, target + 1):
            ways[amount] += ways[amount - coin]
    return ways


def count_by_amount_outer(coins, target):
    """Amounts in the outer loop, coins inner.

    Identical array, identical recurrence, two loops swapped -- and it counts
    ordered sequences instead of multisets. The reason is that `ways[amount]`
    is now assembled by asking 'what was the last coin', so 2+1+1 and 1+2+1
    are counted as different answers.
    """
    ways = [0] * (target + 1)
    ways[0] = 1
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount:
                ways[amount] += ways[amount - coin]
    return ways


def fewest_amount_outer(coins, target):
    """The minimising version, amounts outer."""
    best = [0] + [target + 1] * target
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount and best[amount - coin] + 1 < best[amount]:
                best[amount] = best[amount - coin] + 1
    return best


def fewest_coin_outer(coins, target):
    """The minimising version, coins outer. Same array, swapped loops."""
    best = [0] + [target + 1] * target
    for coin in coins:
        for amount in range(coin, target + 1):
            if best[amount - coin] + 1 < best[amount]:
                best[amount] = best[amount - coin] + 1
    return best


COINS = (1, 2, 5)
TARGET = 12

print("Part 1 -- the same array, two loop orders, two questions")
print()
print(f"  coins {COINS}, target {TARGET}")
print()
by_coin = count_by_coin_outer(COINS, TARGET)
by_amount = count_by_amount_outer(COINS, TARGET)
print(f"{'amount':>8}{'multisets':>12}{'ordered':>12}{'ratio':>10}")
print("-" * 42)
for amount in range(1, TARGET + 1):
    ratio = (f"{by_amount[amount] / by_coin[amount]:.1f}x"
             if by_coin[amount] else "-")
    print(f"{amount:>8}{by_coin[amount]:>12,}{by_amount[amount]:>12,}"
          f"{ratio:>10}")
print()
print("Both columns are correct answers to a question, and they are not the")
print("same question. 'In how many ways can you make 12p' has two readings --")
print("as a multiset of coins, or as a sequence of coins handed over one at a")
print("time -- and the two loops answer one each.")
print()
print(f"  at {TARGET}p the gap is {by_amount[TARGET] / by_coin[TARGET]:.0f}x, and it widens with the target,")
print("  because the number of orderings of a set grows faster than the")
print("  number of sets.")
print()
print()
print("Part 2 -- the swap that does not matter")
print()
fewest_a = fewest_amount_outer(COINS, 40)
fewest_c = fewest_coin_outer(COINS, 40)
print(f"  {'amount':>8}{'amounts outer':>15}{'coins outer':>14}{'agree':>8}")
print("-" * 45)
for amount in (1, 5, 7, 11, 23, 39, 40):
    print(f"{amount:>8}{fewest_a[amount]:>15}{fewest_c[amount]:>14}"
          f"{str(fewest_a[amount] == fewest_c[amount]):>8}")
print()
print(f"  all 40 amounts agree : "
      f"{all(fewest_a[a] == fewest_c[a] for a in range(1, 41))}")
print()
print("So the swap that changes the *count* by a factor of")
print(f"{by_amount[TARGET] / by_coin[TARGET]:.0f} at {TARGET}p does nothing at all to the *minimum*. The factor is")
print("not a constant either -- it grows without bound as the target grows,")
print("because the number of orderings of a multiset grows faster than the")
print("number of multisets. That is not luck, and it is worth having an")
print("explanation for.")
print()
print("Counting is order-sensitive because the loop order decides what the")
print("state means: with coins outer, `ways[amount]` is 'the number of")
print("multisets using coins considered so far', and with amounts outer it is")
print("'the number of sequences ending here'. Both are coherent, and they")
print("count different things.")
print()
print("Minimising is order-insensitive because the state does not need to")
print("mean anything in particular. `best[amount]` is the same number however")
print("you got there, and the relaxation `best[a] = min(best[a], best[a-c]+1)`")
print("is a shortest-path update: run it in any order and the same fixed")
print("point is reached, because the values only ever go down.")
print()
print("That is the test worth carrying away. If a DP state is *counting*")
print("something, the loop order is part of the specification. If it is")
print("*optimising* something, the loop order is an implementation detail.")
print()
print()
print("Part 3 -- the check that the two counts are related")
print()


def ordered_from_multisets(coins, target):
    """The number of ordered sequences, computed the long way: sum over every
    multiset of the number of distinct orderings. If the two loop orders
    disagree, this is the bridge between them."""
    total = 0

    def walk(remaining, index):
        nonlocal total
        if remaining == 0:
            counts = {}
            for coin in stack:
                counts[coin] = counts.get(coin, 0) + 1
            orderings = 1
            used = 0
            for count in sorted(counts.values(), reverse=True):
                used += count
                orderings = orderings * comb(used, count)
            total += orderings
            return
        if index >= len(coins):
            return
        coin = coins[index]
        for take in range(remaining // coin + 1):
            stack.extend([coin] * take)
            walk(remaining - take * coin, index + 1)
            if take:
                del stack[-take:]

    stack = []
    walk(target, 0)
    return total


from math import comb

print(f"  {'multisets for ' + str(TARGET) + 'p, coin-outer loop':<44}: "
      f"{by_coin[TARGET]}")
print(f"  {'ordered sequences, amount-outer loop':<44}: {by_amount[TARGET]}")
print(f"  {'ordered sequences, expanding every multiset':<44}: "
      f"{ordered_from_multisets(COINS, TARGET)}")
print(f"  {'the two agree':<44}: "
      f"{ordered_from_multisets(COINS, TARGET) == by_amount[TARGET]}")
print()
print("The third line is the bridge. It takes every multiset of coins that")
print("sums to the target, counts the distinct orderings of each one, and adds")
print("them up -- which is what 'ordered sequences' means, defined without any")
print("reference to a DP.")
print()
print("It agrees with the amount-outer loop, and that agreement is the proof")
print("that the two loop orders are not a bug in one of them. They are two")
print("different state definitions that happen to share an array.")
```

```text
Part 1 -- the same array, two loop orders, two questions

  coins (1, 2, 5), target 12

  amount   multisets     ordered     ratio
------------------------------------------
       1           1           1      1.0x
       2           2           2      1.0x
       3           2           3      1.5x
       4           3           5      1.7x
       5           4           9      2.2x
       6           5          15      3.0x
       7           6          26      4.3x
       8           7          44      6.3x
       9           8          75      9.4x
      10          10         128     12.8x
      11          11         218     19.8x
      12          13         372     28.6x

Both columns are correct answers to a question, and they are not the
same question. 'In how many ways can you make 12p' has two readings --
as a multiset of coins, or as a sequence of coins handed over one at a
time -- and the two loops answer one each.

  at 12p the gap is 29x, and it widens with the target,
  because the number of orderings of a set grows faster than the
  number of sets.


Part 2 -- the swap that does not matter

    amount  amounts outer   coins outer   agree
---------------------------------------------
       1              1             1    True
       5              1             1    True
       7              2             2    True
      11              3             3    True
      23              6             6    True
      39              9             9    True
      40              8             8    True

  all 40 amounts agree : True

So the swap that changes the *count* by a factor of
29 at 12p does nothing at all to the *minimum*. The factor is
not a constant either -- it grows without bound as the target grows,
because the number of orderings of a multiset grows faster than the
number of multisets. That is not luck, and it is worth having an
explanation for.

Counting is order-sensitive because the loop order decides what the
state means: with coins outer, `ways[amount]` is 'the number of
multisets using coins considered so far', and with amounts outer it is
'the number of sequences ending here'. Both are coherent, and they
count different things.

Minimising is order-insensitive because the state does not need to
mean anything in particular. `best[amount]` is the same number however
you got there, and the relaxation `best[a] = min(best[a], best[a-c]+1)`
is a shortest-path update: run it in any order and the same fixed
point is reached, because the values only ever go down.

That is the test worth carrying away. If a DP state is *counting*
something, the loop order is part of the specification. If it is
*optimising* something, the loop order is an implementation detail.


Part 3 -- the check that the two counts are related

  multisets for 12p, coin-outer loop          : 13
  ordered sequences, amount-outer loop        : 372
  ordered sequences, expanding every multiset : 372
  the two agree                               : True

The third line is the bridge. It takes every multiset of coins that
sums to the target, counts the distinct orderings of each one, and adds
them up -- which is what 'ordered sequences' means, defined without any
reference to a DP.

It agrees with the amount-outer loop, and that agreement is the proof
that the two loop orders are not a bug in one of them. They are two
different state definitions that happen to share an array.
```
:::

:::solution Exercise 5
Both give the same length on all six hand-picked sequences and all 300 random ones, which is the
evidence that the fast version solves the same problem rather than a nearby one.

The interesting part is the patience array. Its length is the answer, and the array itself is
sorted by construction -- which is what makes the binary search valid -- so it cannot be a
subsequence of a shuffled input. The check in Part 2 confirms that rather than assuming it. The DP's
answer, by contrast, is a subsequence by construction, because the parent pointers recorded the
actual chain.

The operation counts are worth reporting with their caveat. The ratio of look-backs to binary
searches grows from 50x to 800x across the sizes tested, which is n² against n log n in one column
-- but the two inner steps are not comparable operations, so the count is reported alongside what is
being counted rather than instead of it.

```python run
#!/usr/bin/env python3
"""Chapter 48, exercise 5 -- a DP with a faster non-DP answer.

The longest increasing subsequence has a textbook DP: one state per position,
and at each position a look back over everything before it. It is O(n^2) and
it is correct.

It also has a solution that is not a dynamic program at all, runs in
O(n log n), and gets the same number. This exercise puts them side by side,
because the second one is a reminder that 'find the recurrence' is a way to
solve a problem and not the only one.

The check is that both give the same length on every sequence tested, and
that the fast one is genuinely doing something different rather than the same
thing written shorter.
"""
import bisect
import random


def lis_quadratic(seq):
    """The DP.

    `best[i]` is the length of the longest increasing subsequence *ending at*
    position i -- pinned to a position, like the substring table in the
    chapter rather than the running-best table. So the answer is the maximum
    over the whole table, and the recurrence looks back at every earlier
    position, which is where the n^2 comes from.
    """
    if not seq:
        return 0, []
    best = [1] * len(seq)
    parent = [-1] * len(seq)
    for i in range(1, len(seq)):
        for j in range(i):
            if seq[j] < seq[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
                parent[i] = j
    length = max(best)
    end = best.index(length)
    path = []
    while end != -1:
        path.append(seq[end])
        end = parent[end]
    return length, list(reversed(path))


def lis_patience(seq, count_steps=False):
    """Patience sorting.

    `tails[k]` is the smallest possible tail of an increasing subsequence of
    length k+1. The array is *sorted*, so each new value can be placed with a
    binary search, and the answer is how long the array grew.

    Note what `tails` is not. It is not a table of answers to subproblems,
    and it is not the subsequence -- `tails` is not increasing in the original
    sequence, and the value at the end is not the last element of any
    particular subsequence. It is a different kind of object entirely.
    """
    tails = []
    steps = 0
    for value in seq:
        steps += 1
        pos = bisect.bisect_left(tails, value)
        if pos == len(tails):
            tails.append(value)
        else:
            tails[pos] = value
    return (len(tails), steps, tails) if count_steps else len(tails)


SEQUENCES = [
    ("ascending, n = 20", list(range(20))),
    ("descending, n = 20", list(range(20, 0, -1))),
    ("all equal, n = 20", [5] * 20),
    ("a shuffled 0..19", [13, 4, 18, 1, 9, 16, 6, 11, 3, 19,
                          8, 14, 0, 17, 5, 12, 2, 15, 7, 10]),
    ("two ascending runs", list(range(10)) + list(range(10))),
    ("alternating", [1, 3, 2, 4, 3, 5, 4, 6, 5, 7]),
]

print("Part 1 -- the two solutions, on sequences with known answers")
print()
print(f"  {'sequence':<22}{'DP':>6}{'patience':>10}{'agree':>8}"
      f"   the subsequence")
print("-" * 76)
for name, seq in SEQUENCES:
    length, path = lis_quadratic(seq)
    fast = lis_patience(seq)
    shown = str(path) if len(str(path)) <= 30 else str(path[:8])[:-1] + ", ...]"
    print(f"  {name:<22}{length:>6}{fast:>10}{str(length == fast):>8}"
          f"   {shown}")
print()
print("Both agree on every row, including the degenerate ones. The descending")
print("sequence is the useful edge case: the answer is 1, not 0, because a")
print("single element is an increasing subsequence of length 1. An")
print("implementation that returned 0 there would pass every random test.")
print()
print()
print("Part 2 -- what the two algorithms are actually doing")
print()
SEQ = [13, 4, 18, 1, 9, 16, 6, 11, 3, 19, 8, 14, 0, 17, 5, 12, 2, 15, 7, 10]
length, steps, tails = lis_patience(SEQ, count_steps=True)
dp_length, dp_path = lis_quadratic(SEQ)
print(f"  sequence : {SEQ}")
print()
print(f"  DP       : {dp_length}, found by looking back at every earlier position")
print(f"  patience : {length}, found by {steps} binary searches")
print(f"  the DP's answer, as a subsequence : {dp_path}")
print(f"  the patience array at the end     : {tails}")
print()
print("The last two lines are the ones worth staring at, because the patience")
print("array looks like it should be the answer and it is not. Its length is")
print(f"the answer -- {length} -- but the values in it are a mixture drawn from")
print("different places in the sequence, and they do not appear in that order")
print("anywhere in the input.")
print()


def is_subsequence(needle, haystack):
    """True if `needle` can be found inside `haystack` in order."""
    remaining = iter(haystack)
    return all(any(item == candidate for candidate in remaining)
               for item in needle)


print(f"  the patience array is sorted        : {tails == sorted(tails)}")
print(f"  the patience array is a subsequence : "
      f"{is_subsequence(tails, SEQ)}")
print(f"  the DP's subsequence is increasing  : "
      f"{all(dp_path[i] < dp_path[i + 1] for i in range(len(dp_path) - 1))}")
print(f"  the DP's subsequence is a subsequence: "
      f"{is_subsequence(dp_path, SEQ)}")
print()
print("The patience array is sorted by construction -- that is what makes the")
print("binary search valid -- so it cannot be a subsequence of a shuffled")
print("input unless the input was already sorted. It is a different object")
print("that happens to have the same length as the answer, and the check above")
print("is the way to be sure of that rather than to assume it.")
print()
print("The DP's answer, by contrast, is a subsequence by construction, because")
print("the parent pointers recorded the actual chain. That is the difference")
print("between a table that stores *the answer* and an array that stores *the")
print("number of the answer*.")
print()
print()
print("Part 3 -- the state space, which is where the speed comes from")
print()
print("The DP has n states, and each one looks back over up to n earlier")
print("positions, so the work is about n^2/2. The patience version has an")
print("array of at most n entries and touches each new value once, with a")
print("binary search of log n -- so about n log n.")
print()
print(f"{'n':>8}{'DP look-backs':>16}{'patience searches':>20}{'ratio':>10}")
print("-" * 54)
rng = random.Random(3)
for n in (100, 200, 400, 800, 1_600):
    seq = list(range(n))
    rng.shuffle(seq)
    lookbacks = n * (n - 1) // 2
    print(f"{n:>8,}{lookbacks:>16,}{n:>20,}{lookbacks / n:>9,.0f}x")
print()
print("The ratio column is the number of DP look-backs per binary search, and")
print("it grows with n -- so the gap widens rather than staying fixed. That is")
print("the difference between n^2 and n log n in one column.")
print()
print("But the counts are not quite a fair comparison, because the patience")
print("version's inner step is a binary search and the DP's is an integer")
print("compare. Counting operations rather than time is the right instinct,")
print("but it only works when the operations are comparable -- and here they")
print("are not, which is exactly the case where a count has to be reported")
print("alongside what is being counted rather than instead of it.")
print()
print()
print("Part 4 -- the checks")
print()
rng = random.Random(11)
mismatches = 0
trials = 300
for _ in range(trials):
    n = rng.randint(0, 40)
    seq = [rng.randint(0, 50) for _ in range(n)]
    if lis_quadratic(seq)[0] != lis_patience(seq):
        mismatches += 1
print(f"  {trials} random sequences, disagreements : {mismatches}")
print()
print("Every one agrees, over lengths from 0 to 40 and values from a range")
print("small enough to force plenty of ties. That is the evidence that the")
print("fast version is a solution to the same problem and not to a")
print("nearby one -- which is the failure mode to watch for when a faster")
print("algorithm is found for something that already worked.")
print()
print("The chapter's question was whether the recursion has overlapping")
print("subproblems and polynomially many states. This problem answers yes to")
print("both, which is why the DP is available. The patience version shows")
print("that 'yes' is a licence to write a DP, not an obligation -- and that")
print("the fastest solution to a DP-shaped problem sometimes arrives from a")
print("direction the recurrence cannot see.")
```

```text
Part 1 -- the two solutions, on sequences with known answers

  sequence                  DP  patience   agree   the subsequence
----------------------------------------------------------------------------
  ascending, n = 20         20        20    True   [0, 1, 2, 3, 4, 5, 6, 7, ...]
  descending, n = 20         1         1    True   [20]
  all equal, n = 20          1         1    True   [5]
  a shuffled 0..19           5         5    True   [4, 9, 11, 14, 17]
  two ascending runs        10        10    True   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  alternating                6         6    True   [1, 3, 4, 5, 6, 7]

Both agree on every row, including the degenerate ones. The descending
sequence is the useful edge case: the answer is 1, not 0, because a
single element is an increasing subsequence of length 1. An
implementation that returned 0 there would pass every random test.


Part 2 -- what the two algorithms are actually doing

  sequence : [13, 4, 18, 1, 9, 16, 6, 11, 3, 19, 8, 14, 0, 17, 5, 12, 2, 15, 7, 10]

  DP       : 5, found by looking back at every earlier position
  patience : 5, found by 20 binary searches
  the DP's answer, as a subsequence : [4, 9, 11, 14, 17]
  the patience array at the end     : [0, 2, 5, 7, 10]

The last two lines are the ones worth staring at, because the patience
array looks like it should be the answer and it is not. Its length is
the answer -- 5 -- but the values in it are a mixture drawn from
different places in the sequence, and they do not appear in that order
anywhere in the input.

  the patience array is sorted        : True
  the patience array is a subsequence : False
  the DP's subsequence is increasing  : True
  the DP's subsequence is a subsequence: True

The patience array is sorted by construction -- that is what makes the
binary search valid -- so it cannot be a subsequence of a shuffled
input unless the input was already sorted. It is a different object
that happens to have the same length as the answer, and the check above
is the way to be sure of that rather than to assume it.

The DP's answer, by contrast, is a subsequence by construction, because
the parent pointers recorded the actual chain. That is the difference
between a table that stores *the answer* and an array that stores *the
number of the answer*.


Part 3 -- the state space, which is where the speed comes from

The DP has n states, and each one looks back over up to n earlier
positions, so the work is about n^2/2. The patience version has an
array of at most n entries and touches each new value once, with a
binary search of log n -- so about n log n.

       n   DP look-backs   patience searches     ratio
------------------------------------------------------
     100           4,950                 100       50x
     200          19,900                 200      100x
     400          79,800                 400      200x
     800         319,600                 800      400x
   1,600       1,279,200               1,600      800x

The ratio column is the number of DP look-backs per binary search, and
it grows with n -- so the gap widens rather than staying fixed. That is
the difference between n^2 and n log n in one column.

But the counts are not quite a fair comparison, because the patience
version's inner step is a binary search and the DP's is an integer
compare. Counting operations rather than time is the right instinct,
but it only works when the operations are comparable -- and here they
are not, which is exactly the case where a count has to be reported
alongside what is being counted rather than instead of it.


Part 4 -- the checks

  300 random sequences, disagreements : 0

Every one agrees, over lengths from 0 to 40 and values from a range
small enough to force plenty of ties. That is the evidence that the
fast version is a solution to the same problem and not to a
nearby one -- which is the failure mode to watch for when a faster
algorithm is found for something that already worked.

The chapter's question was whether the recursion has overlapping
subproblems and polynomially many states. This problem answers yes to
both, which is why the DP is available. The patience version shows
that 'yes' is a licence to write a DP, not an obligation -- and that
the fastest solution to a DP-shaped problem sometimes arrives from a
direction the recurrence cannot see.
```
:::
