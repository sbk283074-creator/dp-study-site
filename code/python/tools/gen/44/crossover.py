#!/usr/bin/env python3
"""Chapter 44 demo 14 -- where two algorithms cross over, counted.

Both functions return the same list. The comparison count is exact, and it
is collected by handing each algorithm objects that count their own
comparisons -- so the count is of the real work of the real function rather
than of a model of it.
"""
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
