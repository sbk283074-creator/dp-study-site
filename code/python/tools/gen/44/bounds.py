#!/usr/bin/env python3
"""Chapter 44 demo 4 -- one function, two bounds."""


def find(xs, target):
    """Return (index, comparisons); index is -1 when target is absent."""
    for i, x in enumerate(xs):
        if x == target:
            return i, i + 1
    return -1, len(xs)


DATA = list(range(1_000))

print("the same function, asked three different questions")
print()
idx, cmp_best = find(DATA, 0)
print(f"  target at the front : index {idx:>3}, {cmp_best:>4} comparisons")
idx, cmp_worst = find(DATA, 999)
print(f"  target at the back  : index {idx:>3}, {cmp_worst:>4} comparisons")
idx, cmp_absent = find(DATA, -1)
print(f"  target absent       : index {idx:>3}, {cmp_absent:>4} comparisons")
print()

n = len(DATA)
print(f"n = {n}")
print(f"  best case    : 1 comparison          -> the function is Omega(1)")
print(f"  worst case   : n comparisons          -> the function is O(n)")
print(f"  average case : (n + 1) / 2 = {n + 1} / 2 = {(n + 1) / 2}")
print()
print("So 'what is the complexity of find()?' has no single answer, and the")
print("question is incomplete without a case. Omega(1) and O(n) are both")
print("true of this one function. A bound on its own is not a claim about")
print("speed -- it is a claim about which case you are describing.")
