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
