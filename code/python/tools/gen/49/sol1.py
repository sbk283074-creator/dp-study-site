#!/usr/bin/env python3
"""Chapter 49, Exercise 1 -- sort it first.

The problem: given a list of numbers, find the largest gap between two
values that are adjacent *in sorted order*. [3, 1, 9, 4] sorted is
[1, 3, 4, 9] and the gaps are 2, 1, 5, so the answer is 5.

The slow version finds each value's successor by scanning the list, which is
n comparisons per element. The fast version sorts and walks once. Both are
correct, and the counting is what separates them.
"""
import random

# ------------------------------------------------------------------ solutions


def merge_sort_counted(values):
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

    return sort(values), comparisons


def largest_gap_scanning(values):
    """Find each element's successor by scanning. Returns (gap, comparisons)."""
    comparisons = 0
    ordered = []
    for v in values:
        best = None
        for w in values:
            comparisons += 1
            if w > v and (best is None or w < best):
                best = w
        ordered.append(best)
    gaps = [b - v for v, b in zip(values, ordered) if b is not None]
    return (max(gaps) if gaps else 0), comparisons


def largest_gap_sorted(values):
    """Sort, then look at neighbours. Returns (gap, comparisons)."""
    ordered, comparisons = merge_sort_counted(values)
    best = 0
    for i in range(1, len(ordered)):
        comparisons += 1
        best = max(best, ordered[i] - ordered[i - 1])
    return best, comparisons


# ---------------------------------------------------------------- correctness

print("Two methods, and the first question is whether they agree.\n")
rng = random.Random(49)
disagreements = 0
for _ in range(400):
    n = rng.randint(2, 40)
    values = rng.sample(range(10 * n), n)
    if largest_gap_scanning(values)[0] != largest_gap_sorted(values)[0]:
        disagreements += 1
print(f"   400 random instances, distinct answers : {disagreements}")
print()
print("The scanning version compares every element with every element, so its")
print("comparison count is n^2 whatever the data is. Check that:\n")
print(f"   {'n':>7}{'comparisons':>16}{'n^2':>12}{'agree':>8}")
print("   " + "-" * 43)
for n in (50, 100, 200, 400):
    values = rng.sample(range(10 * n), n)
    _, comparisons = largest_gap_scanning(values)
    print(f"   {n:>7,}{comparisons:>16,}{n * n:>12,}"
          f"{str(comparisons == n * n):>8}")

# ------------------------------------------------------------------ the cost

print("\nNow the two side by side. The scanning column is the formula just")
print("verified; the sorted column is counted, including its own sort.\n")
print(f"   {'n':>10}{'scan for successors':>22}{'sort + one pass':>18}"
      f"{'ratio':>10}")
print("   " + "-" * 60)
for n in (1_000, 10_000, 100_000):
    values = rng.sample(range(10 * n), n)
    slow = n * n
    _, fast = largest_gap_sorted(values)
    print(f"   {n:>10,}{slow:>22,}{fast:>18,}{slow / fast:>9,.0f}x")

print()
print("The sorted version's cost is n log n comparisons for the sort plus n for")
print("the walk, so the ratio is n^2 divided by about n log n -- which grows")
print("with n and does not stop. And the sort is not a detail that can be")
print("skipped: once the values are in order, the pair that matters is always")
print("two neighbours, so the question 'which two values are closest' becomes")
print("'which adjacent pair is closest', and a single pass answers it.")
print()
print("That is what 'sort it first' means. It is not that sorting is fast. It")
print("is that sorting makes the answer local.")
