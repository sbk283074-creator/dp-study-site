#!/usr/bin/env python3
"""Chapter 46 solution 3 -- first and last index of a value, from `<` alone.

Both searches below use only `<`, which is all `bisect` requires of an item.
Counting the probes shows the two searches are still logarithmic even though
neither of them ever finds the value it is looking for.
"""
import bisect

VALUES = [10, 20, 20, 20, 20, 35, 35, 50, 60, 60, 75]


def first_index(items, target, counter=None):
    """The lower bound: the first index whose item is >= target. Note that
    this never compares for equality -- it only ever asks `items[mid] < x`,
    which is why it works on any type that supports `<`."""
    low, high = 0, len(items)
    while low < high:
        if counter is not None:
            counter[0] += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low


def last_index(items, target, counter=None):
    """The index *after* the last occurrence, which is what bisect_right
    returns. Asking for 'one past the end' instead of 'the last one' is what
    removes the special case for an empty range."""
    low, high = 0, len(items)
    while low < high:
        if counter is not None:
            counter[0] += 1
        middle = (low + high) // 2
        if target < items[middle]:
            high = middle
        else:
            low = middle + 1
    return low


print(f"a sorted list with duplicate runs: {VALUES}")
print()
print(f"{'target':>8}{'first':>8}{'last':>7}{'count':>8}{'slice':>26}"
      f"{'probes':>9}")
print("-" * 68)
for target in (10, 20, 35, 50, 60, 75, 15):
    counter = [0]
    start = first_index(VALUES, target, counter)
    stop = last_index(VALUES, target, counter)
    print(f"{target:>8}{start:>8}{stop:>7}{stop - start:>8}"
          f"{str(VALUES[start:stop]):>26}{counter[0]:>9}")
print()
print("Both searches are O(log n) even though neither one looks for the")
print("value. `first_index` finds the boundary between 'less than' and 'not")
print("less than'; `last_index` finds the boundary between 'not greater than'")
print("and 'greater than'. A boundary is a position, and every list has one,")
print("so there is no not-found case to handle and no `return -1` anywhere.")
print()
print("That is why the pair is the right primitive. A search that returns a")
print("bool has to be written twice to answer 'how many', and the second")
print("version grows its own off-by-one. These two compose into every")
print("question you actually have:")
print()
print("  count of target      stop - start")
print("  is target present    start < stop")
print("  rank of target       start")
print("  the items equal it   items[start:stop]")
print()
print("Two of the rows above are worth naming. Target 15 is not in the list")
print("at all, and both searches still return an answer -- start == stop == 1,")
print("so the count is 0 and the slice is empty. Target 10 is the first item,")
print("so start is 0, which is a valid index and also falsy; code that writes")
print("`if first_index(...)` to test for presence gets that row wrong.")
print()
print(f"{'target':>8}{'my first':>10}{'bisect_left':>14}{'my last':>10}"
      f"{'bisect_right':>15}")
print("-" * 60)
for target in (10, 20, 35, 50, 60, 75, 15):
    print(f"{target:>8}{first_index(VALUES, target):>10}"
          f"{bisect.bisect_left(VALUES, target):>14}"
          f"{last_index(VALUES, target):>10}"
          f"{bisect.bisect_right(VALUES, target):>15}")
print()
print("Which is the honest conclusion: the standard library already has")
print("these, tested, in C, and named after the convention they use. Write")
print("them once by hand so the invariant is yours; then use `bisect`.")
