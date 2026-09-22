#!/usr/bin/env python3
"""Chapter 49, Exercise 4 -- the complexity depends on the input.

Every claim in this chapter has been of the form "this costs about n log n".
That is a shorthand, and this exercise is about what the shorthand hides. A
single function can be O(1) and O(n) and O(n^2), depending on which input it
is handed, and a budget derived from the wrong case is a budget for a program
you are not writing.

Two functions. The first is a linear search, where the spread is n. The
second is an early-exit duplicate check, where the spread is n^2 -- and where
the case that actually happens is nowhere near the worst one.
"""
import math
import random
from itertools import product

# --------------------------------------------------------------- the search


def linear_search_counted(values, target):
    """Return (index, comparisons). The count depends on where target sits."""
    comparisons = 0
    for i, v in enumerate(values):
        comparisons += 1
        if v == target:
            return i, comparisons
    return -1, comparisons


rng = random.Random(49)
N = 1_000
values = rng.sample(range(10 * N), N)

print("A linear search, run four times on the same list with four targets.\n")
print(f"   {'target':<28}{'index':>8}{'comparisons':>14}")
print("   " + "-" * 50)
cases = [
    ("the first element", values[0]),
    ("the middle element", values[N // 2]),
    ("the last element", values[-1]),
    ("not present at all", -1),
]
for label, target in cases:
    index, comparisons = linear_search_counted(values, target)
    print(f"   {label:<28}{index:>8,}{comparisons:>14,}")

print()
print("One function, one list, and the cost ranges from 1 to 1,000. So 'this")
print("search is O(n)' is not a statement about the function. It is a")
print("statement about the worst case, and the worst case is the one where")
print("the element is last or absent.\n")
print("The average over all possible targets has an exact value, and it is")
print("worth deriving rather than guessing: a target at position i costs i + 1")
print("comparisons, so the total over every position is 1 + 2 + ... + n.\n")
n = 500
total = sum(linear_search_counted(values, values[i])[1] for i in range(n))
print(f"   positions summed            : {n:,}")
print(f"   comparisons in total        : {total:,}")
print(f"   n(n+1)/2                    : {n * (n + 1) // 2:,}")
print(f"   average per search          : {total / n:.1f}")
print(f"   (n+1)/2                     : {(n + 1) / 2:.1f}")
print()
print("The average is (n+1)/2, exactly, which is half the worst case. That is")
print("the usual shape: the average sits between the best and the worst, and")
print("the budget has to be built from the worst unless you can prove the")
print("worst cannot happen.")

# ------------------------------------------------------------- the early exit


def has_duplicate_counted(values):
    """Early exit on the first duplicate. Returns (found, comparisons)."""
    comparisons = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            comparisons += 1
            if values[i] == values[j]:
                return True, comparisons
    return False, comparisons


print("\nNow the interesting one. Here is a function whose worst case is")
print("n(n-1)/2 comparisons and whose real cost is nowhere near it.\n")
print("The early exit makes the count a random variable, so a sample says")
print("nothing -- the distribution is heavy-tailed and a handful of runs")
print("lands anywhere. Do not sample it. Enumerate *every* input instead: for")
print("n values drawn from n possibilities there are n^n of them, and up to")
print("n = 7 that is under a million, so the distribution can be counted")
print("exactly rather than estimated.\n")
print(f"   {'n':>3}{'inputs':>10}{'smallest':>10}{'median':>8}{'mean':>9}"
      f"{'mean / n':>10}{'worst':>8}{'at the worst':>14}")
print("   " + "-" * 73)
sizes = []
for n in range(2, 8):
    counts = sorted(has_duplicate_counted(xs)[1] for xs in product(range(n), repeat=n))
    total = len(counts)
    mean = sum(counts) / total
    at_worst = sum(1 for c in counts if c == counts[-1]) / total
    sizes.append((n, total, mean, counts[-1], at_worst))
    print(f"   {n:>3}{total:>10,}{counts[0]:>10}{counts[total // 2]:>8}"
          f"{mean:>9.3f}{mean / n:>10.3f}{counts[-1]:>8}{at_worst:>13.1%}")

print()
print("Every number in that table is exact. The `mean / n` column climbs")
print("towards 1 and the `at the worst` column collapses, and the two facts")
print("have the same cause.\n")
print("Look at the first row of the double loop. It compares v[0] with")
print("v[1], v[2], ... and stops at the first value equal to v[0]. Each")
print("candidate matches with probability 1/n, so finding one takes about n")
print("draws -- but the row is only n-1 long. So the first row alone accounts")
print("for about n comparisons when it succeeds, and it fails to find")
print("anything with probability (1 - 1/n)^(n-1):\n")
print(f"   {'n':>8}{'(1 - 1/n)^(n-1)':>20}{'1/e':>10}")
print("   " + "-" * 38)
for n in (5, 50, 500, 50_000):
    print(f"   {n:>8,}{(1 - 1 / n) ** (n - 1):>20.4f}{1 / math.e:>10.4f}")

print()
print("So roughly a third of the time the first row finds nothing and the")
print("work moves to the second row, which behaves the same way. The total")
print("therefore lands on the order of n rather than n^2, and the mean/n")
print("column is that fact measured rather than argued.")
print()
print("What the table also shows is that the worst case is not merely")
print("unlikely, it is *rare*: at n = 7 only 1.2% of the 823,543 possible")
print("inputs reach n(n-1)/2 comparisons, and the mean is 6.3 against a worst")
print("of 21. The worst case needs every value distinct, which is the input")
print("the function was written to detect and the one the distribution almost")
print("never produces.")
print()
print("Three numbers, disagreeing by orders of magnitude: 1 comparison in the")
print("best case, about 0.9n in the case that happens, and n(n-1)/2 in the")
print("worst. A complexity claim that names none of them is not a claim, and")
print("a budget built from the worst case would have rejected a function that")
print("is fine -- the same mistake as building one from the best case, made")
print("in the other direction.")
