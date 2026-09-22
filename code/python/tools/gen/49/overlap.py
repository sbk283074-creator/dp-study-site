#!/usr/bin/env python3
"""Chapter 49 demo -- when the answer is "sort it first".

The problem: given a list of half-open intervals [start, end), what is the
largest number of them that are open at the same moment?

Two things here are not what they look like.

First, the obvious method -- "ask each interval how many others overlap it,
take the largest answer" -- is not slow. It is wrong, and the smallest
counterexample has three intervals.

Second, the half-open bracket is load-bearing. [0, 5) and [5, 10) do not
overlap, so at time 5 the closing event must be processed before the opening
one. That tie-break is part of the algorithm.
"""
import random

# ------------------------------------------------------------------ solutions


def overlaps(a, b):
    """Half-open: [0, 5) and [5, 10) do not overlap."""
    return a[0] < b[1] and b[0] < a[1]


def max_overlap_pairwise(intervals):
    """The obvious method. Returns (depth, tests). Wrong -- see below."""
    tests = 0
    best = 0
    for i, a in enumerate(intervals):
        depth = 1
        for j, b in enumerate(intervals):
            if i == j:
                continue
            tests += 1
            if overlaps(a, b):
                depth += 1
        best = max(best, depth)
    return best, tests


def max_overlap_by_points(intervals):
    """Correct and slow: the deepest point is always some interval's start."""
    tests = 0
    best = 0
    for start, _ in intervals:
        depth = 0
        for s, e in intervals:
            tests += 1
            if s <= start < e:
                depth += 1
        best = max(best, depth)
    return best, tests


def merge_sort_counted(events):
    """Merge sort on (time, delta) with the comparison count reported."""
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(events), comparisons


def max_overlap_sweep(intervals):
    """Sort the events, then one pass. Returns (depth, work)."""
    events = []
    for start, end in intervals:
        events.append((start, +1))
        events.append((end, -1))
    ordered, comparisons = merge_sort_counted(events)
    depth = 0
    best = 0
    steps = 0
    for _, delta in ordered:
        steps += 1
        depth += delta
        best = max(best, depth)
    return best, comparisons + steps


def max_overlap_sweep_starts_first(intervals):
    """The same sweep with the tie-break reversed. This one is wrong."""
    events = []
    for start, end in intervals:
        events.append((start, +1))
        events.append((end, -1))
    ordered, _ = merge_sort_counted(events)
    ordered.sort(key=lambda e: (e[0], -e[1]))       # starts before ends
    depth = 0
    best = 0
    for _, delta in ordered:
        depth += delta
        best = max(best, depth)
    return best


# ------------------------------------------------------------------- the trap

print("Three intervals. One long one covering the other two, and the other")
print("two sitting side by side without touching:\n")
covering = [(0, 10), (0, 5), (5, 10)]
print(f"   intervals {covering}\n")
print(f"   pairwise, 'how many overlap me?' : {max_overlap_pairwise(covering)[0]}")
print(f"   every start point, counted       : {max_overlap_by_points(covering)[0]}")
print(f"   sort the events, sweep           : {max_overlap_sweep(covering)[0]}")
print()
print("The pairwise method says 3. The answer is 2: [0, 5) and [5, 10) are")
print("never open at the same time, so the long interval can only ever be")
print("sharing its moment with one of them. The method counts intervals that")
print("overlap a *given* interval, and that is a different question from the")
print("largest number open at a *point*. Three intervals overlap the long one")
print("at various times; no two of the three are ever open together.")
print()
rng = random.Random(49)
pairwise_wrong = 0
over = 0
under = 0
for _ in range(300):
    n = rng.randint(1, 30)
    spans = []
    for _ in range(n):
        a = rng.randint(0, 40)
        spans.append((a, a + rng.randint(1, 8)))
    got = max_overlap_pairwise(spans)[0]
    truth = max_overlap_sweep(spans)[0]
    if got != truth:
        pairwise_wrong += 1
        over += got > truth
        under += got < truth
print(f"   300 random instances, the pairwise method is wrong on "
      f"{pairwise_wrong} of them")
print(f"   of those, overcounted {over}, undercounted {under}")
print("   It can only overcount, and the reason is structural: the method")
print("   counts intervals that overlap a given interval, and any such set is")
print("   a candidate answer, so it can never miss one that is larger.")

# ------------------------------------------------------------ the tie-break

print("\nNow the second trap, in the sweep itself. Two intervals that touch:\n")
touching = [(0, 5), (5, 10)]
print(f"   intervals {touching}   -- half-open, so they do not overlap\n")
print(f"   every start point, counted                : "
      f"{max_overlap_by_points(touching)[0]}")
print(f"   sweep, ends before starts at equal times  : "
      f"{max_overlap_sweep(touching)[0]}")
print(f"   sweep, starts before ends at equal times  : "
      f"{max_overlap_sweep_starts_first(touching)}")
print()
print("The wrong tie-break reports two intervals open at time 5, when the")
print("first has just closed. It is right on most inputs and wrong on the")
print("ones with shared endpoints, which is the worst kind of bug: it")
print("survives the tests you thought to write.\n")
tie_bad = 0
rng = random.Random(7)
for _ in range(300):
    n = rng.randint(1, 30)
    spans = []
    for _ in range(n):
        a = rng.randint(0, 40)
        spans.append((a, a + rng.randint(1, 8)))
    if max_overlap_sweep_starts_first(spans) != max_overlap_by_points(spans)[0]:
        tie_bad += 1
print(f"   300 random instances, the wrong tie-break is wrong on "
      f"{tie_bad} of them")

# -------------------------------------------------------------- the agreement

print("\nThe two correct methods, over random inputs:\n")
disagreements = 0
for _ in range(300):
    n = rng.randint(1, 40)
    spans = []
    for _ in range(n):
        a = rng.randint(0, 60)
        spans.append((a, a + rng.randint(1, 10)))
    if max_overlap_sweep(spans)[0] != max_overlap_by_points(spans)[0]:
        disagreements += 1
print(f"   300 random instances, sort-and-sweep vs every start point : "
      f"{disagreements} disagreements")

# ---------------------------------------------------------------- the formula

print("\nThe slow-but-correct version tests every start against every interval,")
print("so its cost is n^2 before the data arrives. Check that:\n")
print(f"   {'n':>7}{'tests counted':>16}{'n^2':>12}{'agree':>8}")
print("   " + "-" * 43)
for n in (100, 200, 400):
    spans = [(i, i + 3) for i in range(n)]
    _, tests = max_overlap_by_points(spans)
    print(f"   {n:>7,}{tests:>16,}{n * n:>12,}{str(tests == n * n):>8}")

print("\nAnd the two correct versions side by side at scale. The n^2 column is")
print("the formula just verified; the sweep column is counted, including its")
print("own sort.\n")
print(f"   {'n':>10}{'every start point':>20}{'sort + sweep':>16}{'ratio':>10}")
print("   " + "-" * 56)
for n in (1_000, 10_000, 100_000):
    spans = []
    for _ in range(n):
        a = rng.randint(0, 10 * n)
        spans.append((a, a + rng.randint(1, 100)))
    slow = n * n
    _, sweep = max_overlap_sweep(spans)
    print(f"   {n:>10,}{slow:>20,}{sweep:>16,}{slow / sweep:>9,.0f}x")

print()
print("The ratio grows with n and never stops growing, because one side is n^2")
print("and the other is 2n log 2n. Sorting is the reason: the sweep never asks")
print("whether two intervals overlap. It only asks whether an interval has")
print("started or stopped. The pairwise question did not get faster -- it")
print("stopped being asked.")
