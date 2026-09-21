#!/usr/bin/env python3
"""Chapter 46 demo -- insertion sort, counted, on four shapes of input.

Insertion sort is the sort nobody ships and everybody should read once,
because its cost depends on the input's existing order more than on n -- and
that is exactly the fact Timsort is built around.
"""
import random

N = 2_000


def ascending(n):
    return list(range(n))


def descending(n):
    return list(range(n - 1, -1, -1))


def scrambled(n):
    values = list(range(n))
    random.Random(0).shuffle(values)
    return values


def nearly_sorted(n, swaps=10):
    """Ascending, with a few adjacent pairs transposed. The shape of a list
    that was sorted last week and has had a handful of edits since."""
    values = ascending(n)
    for i in range(swaps):
        j = (i * 37) % (n - 1)
        values[j], values[j + 1] = values[j + 1], values[j]
    return values


def insertion_sort(items, counter):
    """Walk left to right, and slide each item back to where it belongs.
    Returns the number of element moves, which is the other half of the
    cost and the half people forget."""
    moves = 0
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        while j >= 0:
            counter[0] += 1
            if items[j] <= key:
                break
            items[j + 1] = items[j]
            moves += 1
            j -= 1
        items[j + 1] = key
    return moves


SHAPES = [
    ("already ascending", ascending),
    ("already descending", descending),
    ("nearly sorted", nearly_sorted),
    ("scrambled", scrambled),
]

print(f"insertion sort on {N:,} items, four input shapes")
print()
print(f"{'input':<22}{'comparisons':>14}{'per item':>10}{'moves':>12}")
print("-" * 58)
for label, make in SHAPES:
    counter = [0]
    moves = insertion_sort(make(N), counter)
    print(f"{label:<22}{counter[0]:>14,}{counter[0] / N:>10.1f}{moves:>12,}")
print()
print("Four different costs for the same algorithm and the same n. The")
print("ascending input is the giveaway: one comparison per item, because")
print("every item is already in place and the inner loop exits immediately.")
print("Descending input is the worst case, at n(n-1)/2 comparisons, and")
print("scrambled input lands about halfway -- n^2/4, which is a million")
print("comparisons for two thousand items.")
print()
print("That spread is not a curiosity. It means 'sorting is O(n^2)' and")
print("'sorting is O(n)' are both true statements about insertion sort, and")
print("the difference is a property of the *data*, not the code. Any sort")
print("that wants to be fast on real inputs has to exploit that -- and the")
print("moves column is the other half, because a move is a write and a")
print("write costs more than a comparison on real hardware.")
print()
print("Now the same shapes through the sort you actually use.")
