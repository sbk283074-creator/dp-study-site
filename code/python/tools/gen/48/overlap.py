#!/usr/bin/env python3
"""Chapter 48 demo -- how to tell whether dynamic programming applies.

Two questions decide it, and both are answerable by counting. How many
*distinct* subproblems does the recursion have, and how many times does the
naive version ask for each one? If the first is polynomial and the second is
exponential, the gap between them is what a cache buys.

The same two questions say when a cache buys *nothing*, which is the half
people skip -- and caching a recursion with no overlap is pure overhead.
"""


def fib(n, tally, seen):
    tally[0] += 1
    seen.add(n)
    if n < 2:
        return n
    return fib(n - 1, tally, seen) + fib(n - 2, tally, seen)


def merge_sort(items, lo, hi, tally, seen):
    """Every range it is asked about is a different range, so the tree has no
    repeated node to cache."""
    tally[0] += 1
    seen.add((lo, hi))
    if hi - lo <= 1:
        return items[lo:hi]
    mid = (lo + hi) // 2
    left = merge_sort(items, lo, mid, tally, seen)
    right = merge_sort(items, mid, hi, tally, seen)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search(items, target, lo, hi, tally, seen):
    tally[0] += 1
    seen.add((lo, hi))
    if lo >= hi:
        return None
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search(items, target, mid + 1, hi, tally, seen)
    return binary_search(items, target, lo, mid, tally, seen)


CASES = []

tally, seen = [0], set()
fib(30, tally, seen)
CASES.append(("fib(30)", len(seen), tally[0]))

SORTED = list(range(1024))
tally, seen = [0], set()
merge_sort(SORTED, 0, len(SORTED), tally, seen)
CASES.append((f"merge sort (n = {len(SORTED):,})", len(seen), tally[0]))

BIG = list(range(1_000_000))
tally, seen = [0], set()
binary_search(BIG, 999_999, 0, len(BIG), tally, seen)
CASES.append((f"binary search (n = {len(BIG):,})", len(seen), tally[0]))

print("three recursions, counted the same way")
print()
print(f"{'recurrence':<28}{'distinct':>10}{'total calls':>13}{'overlap':>11}")
print("-" * 62)
for name, distinct, calls in CASES:
    print(f"{name:<28}{distinct:>10,}{calls:>13,}{calls / distinct:>11.1f}")
print()
print("The overlap column is the test, and it is a ratio rather than a")
print("judgement call. A value of 1 means every call is a subproblem nobody")
print("has asked about before -- there is nothing to cache, and a memo")
print("dictionary would cost memory and lookups for zero saving.")
print()
sort_distinct, sort_calls = CASES[1][1], CASES[1][2]
print(f"Merge sort is the clean example. At n = {len(SORTED):,} its recursion tree")
print(f"has {sort_calls:,} nodes and {sort_distinct:,} distinct ranges -- every node its own")
print("subproblem, because sorting the left half and sorting the right half")
print("are genuinely different jobs. Wrapping it in `lru_cache` would be")
print("pure overhead, and that is not a matter of taste -- it is the ratio")
print("saying so.")
print()
bs_distinct, bs_calls = CASES[2][1], CASES[2][2]
print(f"Binary search is the same at a smaller scale: {bs_calls} calls, {bs_distinct}")
print("distinct ranges, overlap 1. It recurses into one side only, so its")
print("tree is a line rather than a bush -- and a line has no repeats by")
print("construction.")
print()
print("Fibonacci is the opposite extreme: 31 distinct values, 2.69 million")
print("calls, and every value computed tens of thousands of times.")
print()
print()
print("So the two conditions are:")
print()
print("  1. the number of distinct subproblems is polynomial in the input")
print("  2. the naive recursion asks for them an exponential number of times")
print()
print("Both are needed. A recursion with exponential *distinct* subproblems")
print("cannot be memoised into anything useful -- the cache itself becomes the")
print("exponential object. A recursion with no overlap has nothing to reuse.")
print()
print("That is also why the phrase 'dynamic programming' describes a *shape*")
print("of problem rather than a technique to apply. The counting tells you")
print("whether the shape is there before you write any of it.")
print()
print(f"  fib: each value computed on average "
      f"{CASES[0][2] / CASES[0][1]:,.0f} times")
print(f"  merge sort: each range computed "
      f"{CASES[1][2] / CASES[1][1]:.0f} time(s)")
print(f"  binary search: each range computed "
      f"{CASES[2][2] / CASES[2][1]:.0f} time(s)")
print()
print("One more consequence worth noticing. The reason merge sort has no")
print("overlap is that its subproblems are *disjoint* -- the left half and the")
print("right half share no elements. Overlapping subproblems means the same")
print("input appears in more than one branch of the tree, which is a property")
print("of the recurrence, not of the implementation.")
