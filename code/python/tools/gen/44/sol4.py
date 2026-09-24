#!/usr/bin/env python3
"""Chapter 44 solution 4 -- the cheapest way to find one element.

Both approaches are counted here, and that is the whole point of the exercise:
n and n log n are not distinguishable by timing at any size you can
conveniently measure, so the argument for one of them has to be made by
counting.
"""
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
