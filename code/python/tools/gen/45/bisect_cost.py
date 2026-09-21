#!/usr/bin/env python3
"""Chapter 45 demo -- bisect finds in log n, then pays n to use the answer."""
import bisect
import timeit

N = 20_000
K = 2_000
ROUNDS = 5


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


def time_one(fn):
    return min(timeit.repeat(lambda: fn(N, K), number=1, repeat=ROUNDS))


def band(ratio):
    """The measured column is this machine on this run, so it is a band.
    The shift column next to it is exact and is the one to trust."""
    for edge, label in ((3, "same band"), (8, "~5x slower"), (20, "~10x slower")):
        if ratio < edge:
            return label
    return "~30x slower or more"


base = time_one(build_by_sort)
verdict = band(time_one(build_by_insort) / base)

print(f"a sorted list of {N:,}, then adding {K:,} more keys")
print()
print(f"{'approach':<28}{'element shifts':>16}  {'measured':>14}")
print("-" * 60)
print(f"{'collect, then sort once':<28}{0:>16,}  {'baseline':>14}")
print(f"{'bisect.insort each key':<28}{shifts_for_insort(N, K):>16,}  {verdict:>14}")
print()
print("Both rows end with the same sorted list. Only one of them pays a")
print("linear cost per key, and the shift column says which. For 20,000 and")
print("2,000 that is about 21 million slot moves to insert 2,000 items.")
print()
print("This is not an argument against bisect. bisect is excellent at what")
print("it does, and what it does is *find*. Compare the two searches:")
print()
print(f"{'items':>14}{'linear scan':>16}{'bisect probes':>16}")
print("-" * 46)
for n in (1_000, 100_000, 10_000_000):
    items = list(range(n))
    target = n // 2
    print(f"{n:>14,}{linear_probes(items, target):>16,}{probes_to_find(items, target):>16}")
print()
print("Ten million items, twenty-three probes. The scan needs five million.")
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
