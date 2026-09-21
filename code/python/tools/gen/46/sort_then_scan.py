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
