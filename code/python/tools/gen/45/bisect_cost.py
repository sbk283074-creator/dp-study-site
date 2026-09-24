#!/usr/bin/env python3
"""Chapter 45 demo -- bisect finds in log n, then pays n to use the answer.

Every number here is exact. The shift count follows from the algorithm, and
the probe counts come from running a binary search and a linear scan over
the real data rather than from timing them.
"""
import bisect

N = 20_000
K = 2_000


def permutation(n):
    return [(i * 7919) % n for i in range(n)]


def shifts_for_insort(n, k):
    """Each insort into a sorted list of length L shifts the elements above
    the insertion point down by one slot. Keys arriving in a scrambled order
    land halfway up on average, so the total is about k*n/2 + k^2/4."""
    return k * n // 2 + k * k // 4


def build_by_insort(n, k):
    buf = sorted(permutation(n))
    for value in permutation(k):
        bisect.insort(buf, value)
    return buf


def build_by_sort(n, k):
    buf = permutation(n) + permutation(k)
    buf.sort()
    return buf


def probes_to_find(sorted_items, target):
    """Binary search, written out so the probe count is visible. This is
    what bisect.bisect_left does; the C version just does it faster."""
    low, high = 0, len(sorted_items)
    probes = 0
    while low < high:
        probes += 1
        middle = (low + high) // 2
        if sorted_items[middle] < target:
            low = middle + 1
        else:
            high = middle
    return probes


def linear_probes(sorted_items, target):
    probes = 0
    for item in sorted_items:
        probes += 1
        if item == target:
            break
    return probes


shifts = shifts_for_insort(N, K)
assert build_by_insort(N, K) == build_by_sort(N, K)

print(f"a sorted list of {N:,}, then adding {K:,} more keys")
print()
print(f"{'approach':<28}{'element shifts':>16}{'per key':>10}")
print("-" * 54)
print(f"{'collect, then sort once':<28}{0:>16,}{0:>10,}")
print(f"{'bisect.insort each key':<28}{shifts:>16,}{shifts // K:>10,}")
print()
print("Both rows end with the same sorted list -- the assert above is the")
print("proof, and it is checked every time this program runs. Only one of")
print("the rows pays a linear cost per key, and the last column is where")
print(f"that shows: {shifts // K:,} slot moves to place one key.")
print()
print("A shift here means an element moving down one slot to make room.")
print("The sort moves nothing in that sense: it copies the elements into a")
print("temporary array and back, which is linear in n once, not linear per")
print("key. That difference is what the two rows are really comparing.")
print()
print("This is not an argument against bisect. bisect is excellent at what")
print("it does, and what it does is *find*. Compare the two searches:")
print()
print(f"{'items':>14}{'linear scan':>16}{'bisect probes':>16}")
print("-" * 46)
largest_scan = largest_probes = 0
for n in (1_000, 100_000, 10_000_000):
    items = list(range(n))
    target = n // 2
    largest_scan = linear_probes(items, target)
    largest_probes = probes_to_find(items, target)
    print(f"{n:>14,}{largest_scan:>16,}{largest_probes:>16}")
print()
print(f"Ten million items, {largest_probes} probes. The scan needs {largest_scan:,}.")
print("That is log2(n) against n, and it is why bisect is the right tool for")
print("rank, thresholds, and 'which band does this value fall in'.")
print()
print("So the rule has two halves and they point opposite ways:")
print()
print("  bisect to FIND.    O(log n), and nothing else comes close.")
print("  do not insort in bulk. O(n) per insert, because the list is an array.")
print()
print("If keys arrive one at a time and the order must be maintained after")
print("every one of them, a sorted list is the wrong structure -- and no")
print("amount of bisect will fix that. You want a balanced tree, which is")
print("logarithmic for both. The next demo builds one.")
