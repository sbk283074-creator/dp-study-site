#!/usr/bin/env python3
"""Chapter 46 solution 2 -- rank and percentile from two bisects."""
import bisect
import random

N = 200
_rng = random.Random(0)
SAMPLES = sorted(_rng.randrange(0, 1_000) for _ in range(N))


def rank(sorted_items, value):
    """Returns (below, equal, above). Both searches are log n, so this is
    log n for the whole thing -- no counting, no scanning."""
    below = bisect.bisect_left(sorted_items, value)
    above = len(sorted_items) - bisect.bisect_right(sorted_items, value)
    equal = len(sorted_items) - below - above
    return below, equal, above


def percentile(sorted_items, value):
    """The share of items strictly below the value, as a percentage."""
    below = bisect.bisect_left(sorted_items, value)
    return 100 * below / len(sorted_items)


def rank_by_scan(sorted_items, value):
    """The version everybody writes first, for comparison."""
    below = equal = above = 0
    for item in sorted_items:
        if item < value:
            below += 1
        elif item == value:
            equal += 1
        else:
            above += 1
    return below, equal, above


print(f"{N} sorted samples, values from 0 to {SAMPLES[-1]}")
print(f"  first 10: {SAMPLES[:10]}")
print()
print(f"{'value':>7}{'below':>8}{'equal':>8}{'above':>8}{'total':>8}{'percentile':>13}")
print("-" * 52)
for value in (SAMPLES[0], SAMPLES[N // 2], SAMPLES[-1], 999, 0):
    below, equal, above = rank(SAMPLES, value)
    print(f"{value:>7}{below:>8}{equal:>8}{above:>8}{below + equal + above:>8}"
          f"{percentile(SAMPLES, value):>12.1f}%")
print()
print("Every row sums to n, which is the check that the two bisects were")
print("combined correctly. That is the part people get wrong: `bisect_left`")
print("counts the items *below* the value and `bisect_right` counts the items")
print("at or below it, so the number equal is the difference between them and")
print("the number above is what is left.")
print()
print("A value of 999 is above every sample, so below is 200 and percentile")
print("is 100. A value of 0 is at or below all of them, so below is 0. Neither")
print("is a special case in the code -- the searches just return the ends.")
print()
print(f"{'value':>7}{'rank()':>18}{'scan()':>18}  {'agree':>6}")
print("-" * 52)
for value in (SAMPLES[0], SAMPLES[N // 2], SAMPLES[-1], 999, 0):
    print(f"{value:>7}{str(rank(SAMPLES, value)):>18}"
          f"{str(rank_by_scan(SAMPLES, value)):>18}"
          f"  {str(rank(SAMPLES, value) == rank_by_scan(SAMPLES, value)):>6}")
print()
print("The scan is O(n) and the bisects are O(log n), and on 200 items that")
print("is the difference between 200 comparisons and 16. The reason to")
print("prefer the bisects is not the constant, though -- it is that the scan")
print("has three counters to keep consistent and the bisects have none.")
print()
print("One caveat worth stating, because it is a real trap: both of these")
print("assume the list is sorted. Nothing checks. `bisect` on an unsorted")
print("list returns a plausible index and a wrong answer, and no exception is")
print("raised anywhere. Here is the smallest example the search below could")
print("find -- it is searched for rather than asserted, because not every")
print("unsorted list produces a mismatch:")
print()


def first_mismatch(target):
    candidates = ([1, 5, 9, 3, 7], [9, 1, 5, 3, 7], [5, 9, 1, 3, 7],
                  [7, 3, 9, 5, 1], [3, 7, 1, 9, 5])
    for candidate in candidates:
        wrong = bisect.bisect_left(candidate, target)
        right = bisect.bisect_left(sorted(candidate), target)
        if wrong != right:
            return candidate, wrong, right
    raise SystemExit("no mismatch found -- this demo would prove nothing")


UNSORTED, wrong_answer, right_answer = first_mismatch(5)
print(f"  unsorted list         : {UNSORTED}")
print(f"  bisect_left(., 5)     : {wrong_answer}")
print(f"  same values, sorted   : {sorted(UNSORTED)}")
print(f"  bisect_left(., 5)     : {right_answer}")
print()
print("Two items in that list are below 5, so the rank is 2. The unsorted")
print("search returns 1, because it descended into a half that the ordering")
print("it assumed did not exist. Both are valid indices and neither raises,")
print("so the failure is silent -- which is the whole reason to treat 'the")
print("list is sorted' as a precondition you assert rather than hope for.")
print()
print("If you are handing a list to bisect and you did not just sort it,")
print("check it:")
print()
print(f"  all(a <= b for a, b in zip(xs, xs[1:])) -> "
      f"{all(a <= b for a, b in zip(SAMPLES, SAMPLES[1:]))}")
