#!/usr/bin/env python3
"""Chapter 49 demo -- one problem, three algorithms, and the count that picks.

The problem: given a list of integers and a target, is there a pair of
elements that sums to the target? If so, which pair?

The three solutions are the three shapes every "find a pair" problem has:
look at everything, sort first, or remember what you have seen. Each one is
instrumented with a counter, so the comparison is a comparison of counts and
not of stopwatches.

The sort is a merge sort written here rather than `sorted()`, for one reason:
`list.sort` does not tell you how many comparisons it made, and a modelled
n log n is a claim where a counted one is a fact.
"""
import random

# --------------------------------------------------------------- solutions


def by_brute_force(values, target):
    """Every pair. Returns (pair, probes) where probes counts pair tests."""
    probes = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            probes += 1
            if values[i] + values[j] == target:
                a, b = values[i], values[j]
                return (min(a, b), max(a, b)), probes
    return None, probes


def merge_sort_counted(values):
    """Merge sort that reports how many comparisons it made.

    The count is exact and deterministic for a given input, which is what
    makes it usable as evidence. It is not a model of a comparison count.
    """
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


def by_sorting(values, target):
    """Sort, then walk inwards from both ends."""
    ordered, comparisons = merge_sort_counted(values)
    probes = 0
    lo, hi = 0, len(ordered) - 1
    while lo < hi:
        probes += 1
        total = ordered[lo] + ordered[hi]
        if total == target:
            return (ordered[lo], ordered[hi]), comparisons + probes
        if total < target:
            lo += 1
        else:
            hi -= 1
    return None, comparisons + probes


def by_remembering(values, target):
    """One pass, with a set of everything already seen."""
    seen = set()
    probes = 0
    for v in values:
        probes += 1
        want = target - v
        if want in seen:
            return (min(v, want), max(v, want)), probes
        seen.add(v)
    return None, probes


# ------------------------------------------------------------------ checking

def valid(values, target, pair):
    """A returned pair must sum to the target and come from the input."""
    if pair is None:
        return True
    a, b = pair
    return a + b == target and a in values and b in values


rng = random.Random(49)
disagreements = 0
differing_witnesses = 0
for _ in range(400):
    n = rng.randint(2, 40)
    values = [rng.randint(-50, 50) for _ in range(n)]
    target = rng.randint(-60, 60)
    got = [by_brute_force(values, target)[0],
           by_sorting(values, target)[0],
           by_remembering(values, target)[0]]
    if len({p is None for p in got}) != 1:
        disagreements += 1
    for pair in got:
        assert valid(values, target, pair), (values, target, pair)
    if len({p for p in got if p is not None}) > 1:
        differing_witnesses += 1

print("Correctness first, because a fast wrong answer is not an answer.")
print(f"\n   400 random instances, three implementations each")
print(f"   decisions that disagree      : {disagreements}")
print(f"   instances where all three found a pair but not the same one : "
      f"{differing_witnesses}")
print()
print("The decision is unique; the witness is not. When several pairs sum to")
print("the target, each method returns whichever it reaches first, and that")
print("depends on the method. Compare the answers you promised to compare.")

# ------------------------------------------------- the formula, then the scale

print("\nThe brute force tests every pair, so when no pair works its probe")
print("count is exactly n(n-1)/2. Check that before using it as a formula:\n")
print(f"   {'n':>7}{'probes counted':>16}{'n(n-1)/2':>14}{'agree':>8}")
print("   " + "-" * 45)
for n in (100, 200, 400, 800, 1_600):
    values = [rng.randint(0, 10 * n) for _ in range(n)]
    _, probes = by_brute_force(values, -1)
    formula = n * (n - 1) // 2
    print(f"   {n:>7,}{probes:>16,}{formula:>14,}{str(probes == formula):>8}")

print()
print("`probes` below counts the candidate tests and the membership questions --")
print("the work that scales with the input, not the loop overhead. The brute")
print("force row is the formula just verified; at n = 10^6 the loop itself would")
print("be five hundred billion tests, which is the point being made.\n")
print(f"   {'n':>10}{'brute force':>18}{'sort + walk':>14}{'remember':>12}"
      f"{'brute / best':>14}")
print("   " + "-" * 68)
for n in (10_000, 100_000, 1_000_000):
    values = [rng.randint(0, 10 * n) for _ in range(n)]
    target = -1                      # unreachable: worst case for all three
    _, p_sort = by_sorting(values, target)
    _, p_rem = by_remembering(values, target)
    p_brute = n * (n - 1) // 2
    best = min(p_sort, p_rem)
    print(f"   {n:>10,}{p_brute:>18,}{p_sort:>14,}{p_rem:>12,}"
          f"{p_brute / best:>13,.0f}x")

print()
print("A target that cannot be reached is the honest case to compare: every")
print("method has to finish, so nothing is flattered by where it stopped.")
print("Sorting costs n log n comparisons and then n pointer moves; the set")
print("costs one membership test per element and never sorts at all. Since")
print("the set does exactly n probes, the last column is exactly (n-1)/2 --")
print("check it against the rows: 4,999.5 at n = 10,000 and 499,999.5 at")
print("n = 10^6, rounded in the display. The margin is not a constant factor")
print("that a faster machine could absorb; it grows with n.")
