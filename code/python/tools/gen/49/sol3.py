#!/usr/bin/env python3
"""Chapter 49, Exercise 3 -- the structure is a set, and a set changes the answer.

The problem: given two lists, return the elements that appear in both.

The slow version asks, of each element of the first list, "is it anywhere in
the second?" and answers by walking the second list. The fast version puts
the second list in a set and asks the set. Both are correct, and the counting
is not the interesting part of this exercise.

The interesting part is what a set cannot represent. It holds each value
once, so the fast version quietly drops duplicates the slow version emitted.
That is the same defect as the one in this chapter's scenario, and it is
worth meeting twice.
"""
import random
from collections import Counter

# ------------------------------------------------------------------ solutions


def intersect_scanning(a, b):
    """Ask the second list about each element of the first."""
    comparisons = 0
    rows = []
    for x in a:
        for y in b:
            comparisons += 1
            if x == y:
                rows.append(x)
                break
    return rows, comparisons


def intersect_set(a, b):
    """Put b in a set, then ask it once per element of a."""
    lookup = set(b)
    work = len(b)
    rows = []
    for x in a:
        work += 1
        if x in lookup:
            rows.append(x)
    return rows, work


def intersect_counted(a, b):
    """Keep a's order and a's multiplicity, capped by b's multiplicity."""
    limit = Counter(b)
    work = len(b)
    rows = []
    for x in a:
        work += 1
        if limit[x] > 0:
            limit[x] -= 1
            rows.append(x)
    return rows, work


# ---------------------------------------------------------------- correctness

print("Three implementations. The first two agree on *membership* and disagree")
print("on *multiplicity*, which is the whole point of the exercise.\n")
rng = random.Random(49)
a = [rng.randint(1, 12) for _ in range(30)]
b = [rng.randint(1, 12) for _ in range(20)]
scan_rows, _ = intersect_scanning(a, b)
set_rows, _ = intersect_set(a, b)
counted_rows, _ = intersect_counted(a, b)

print(f"   a has {len(a)} elements, b has {len(b)}")
print(f"   scanning, rows returned      : {len(scan_rows)}")
print(f"   set, rows returned           : {len(set_rows)}")
print(f"   counted, rows returned       : {len(counted_rows)}")
print(f"   scanning vs set, identical   : {scan_rows == set_rows}")
print(f"   scanning vs counted, identical : {scan_rows == counted_rows}")
print()
print("The set version returns fewer rows, and every row it returns is in the")
print("other two. It is not wrong about which values are shared; it is wrong")
print("about how many times each one is shared, and it has no way to record")
print("that. A set is the right structure for a membership question and the")
print("wrong one for a multiplicity question -- and the two questions look")
print("identical until you count the rows.\n")

# --------------------------------------------------------------- the counting

print("Now the cost. The scanning version does one comparison per pair, so its")
print("count is at most len(a) * len(b), reached when nothing matches. A match")
print("stops the inner loop early, so the count lands under the product:\n")
print(f"   {'len(a)':>8}{'len(b)':>8}{'comparisons':>14}{'a x b':>10}"
      f"{'under it by':>13}")
print("   " + "-" * 53)
for n, m in ((40, 30), (80, 60), (160, 120)):
    xs = [rng.randint(1, n) for _ in range(n)]
    ys = [rng.randint(1, n) for _ in range(m)]
    _, comparisons = intersect_scanning(xs, ys)
    print(f"   {n:>8,}{m:>8,}{comparisons:>14,}{n * m:>10,}"
          f"{(n * m - comparisons) / (n * m):>12.1%}")

print()
print("The counted value is always below the product and the gap is the work")
print("the early exits saved. A budget uses the product anyway, because a")
print("bound that depends on how many values the two lists share is not a")
print("bound -- it is a measurement of the input.\n")
print(f"   {'len(a)':>10}{'len(b)':>10}{'scanning, worst':>18}{'set':>12}"
      f"{'ratio':>10}")
print("   " + "-" * 60)
for n, m in ((1_000, 1_000), (10_000, 10_000), (100_000, 100_000)):
    xs = [rng.randint(1, n) for _ in range(n)]
    ys = [rng.randint(1, n) for _ in range(m)]
    slow = n * m
    _, fast = intersect_set(xs, ys)
    print(f"   {n:>10,}{m:>10,}{slow:>18,}{fast:>12,}{slow / fast:>9,.0f}x")

print()
print("The set version costs len(b) to build the set plus len(a) to ask it,")
print("so the ratio against len(a) * len(b) is about n/2 when the lists are")
print("the same length. As with every other exercise in this chapter the")
print("ratio grows with n, and the reason is the same: one side is a product")
print("and the other is a sum.")
