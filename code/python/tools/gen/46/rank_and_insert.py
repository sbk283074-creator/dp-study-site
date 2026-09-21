#!/usr/bin/env python3
"""Chapter 46 demo -- rank, and what insertion actually costs.

`bisect` answers one question: how many items are below this value. That is
a rank. `insort` uses the answer to place an item -- a log n search to find
the slot, and then a shift to make room for it. The search is cheap and the
shift is not, and that asymmetry is the whole reason a sorted list is a bad
thing to maintain one insert at a time.
"""
import bisect
import math
import random


class Counted:
    """A value that reports how often it was compared. `sorted` is C and
    cannot be instrumented, but every comparison it makes goes through `<`,
    so this turns the algorithm into an exact number."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value

    def __repr__(self):
        return f"Counted({self.value})"


def count_sorted(values):
    counter = [0]
    result = sorted(Counted(v, counter) for v in values)
    return counter[0], [item.value for item in result]


def shuffled(n, seed=0):
    values = list(range(n))
    random.Random(seed).shuffle(values)
    return values


TIMES = [10.2, 10.2, 10.2, 11.5, 12.0, 12.0, 13.7]


def competition_rank(ordered, value):
    """How many are strictly better, plus one. Ties share a rank and the
    next rank skips, so the ranks read 1, 2, 2, 4 -- which is what a
    leaderboard does and what `bisect_left` gives you for free."""
    return bisect.bisect_left(ordered, value) + 1


def dense_rank(ordered, value):
    """How many *distinct* values are better, plus one: 1, 2, 2, 3. This one
    cannot be a single bisect, because a bisect cannot tell a repeat from a
    new value -- it has to see the whole list."""
    return len({item for item in ordered if item < value}) + 1


print("Part 1 -- a rank is a bisect")
print()
print(f"finishing times, ascending: {TIMES}")
print()
print(f"{'time':>7}{'below':>8}{'competition':>13}{'dense':>8}{'percentile':>12}")
print("-" * 48)
for value in sorted(set(TIMES)):
    below = bisect.bisect_left(TIMES, value)
    print(f"{value:>7.1f}{below:>8}{competition_rank(TIMES, value):>13}"
          f"{dense_rank(TIMES, value):>8}{below / len(TIMES) * 100:>11.0f}%")
print()
print("The two rank columns disagree, and both are correct. They answer")
print("different questions: 'how many people beat me' (competition, which")
print("skips) and 'how many distinct results are better' (dense, which does")
print("not). Pick one, name it in the function, and never mix them in one")
print("table -- that is how a leaderboard ends up with two people at rank 3")
print("and nobody at rank 4.")
print()
print("The 'below' column is the whole mechanism: it is one bisect_left, and")
print("everything else in the table is arithmetic on top of it.")
print()
linear = [sum(1 for item in TIMES if item < value) for value in TIMES]
from_bisect = [bisect.bisect_left(TIMES, value) for value in TIMES]
print(f"  counting linearly  : {linear}")
print(f"  counting by bisect : {from_bisect}")
print(f"  same answer? {linear == from_bisect}")
print()
print("Both give the same numbers -- the difference is that the first reads")
print("every item and the second reads about log2(7) = 3 of them. On a")
print("leaderboard of ten million rows that is three reads against ten")
print("million, for an answer that is identical by construction.")
print()
print()
print("Part 2 -- insertion: a constant search and a shifting bill")
print()


def insort_counted(items, value):
    """Place `value` and report what it cost: one log n search, and then
    `len(items) - index` slots pushed up by one. The second number is the
    one that decides whether this is a good idea."""
    index = bisect.bisect_right(items, value)
    shifts = len(items) - index
    items.insert(index, value)
    return index, shifts


BASIS = list(range(0, 2000, 2))
print(f"inserting one item into a list of {len(BASIS):,} items")
print()
print(f"{'value':>8}{'lands at':>10}{'slots shifted':>15}{'search cost':>13}")
print("-" * 46)
for value in (-1, 499, 999, 1499, 2001):
    items = list(BASIS)
    index, shifts = insort_counted(items, value)
    print(f"{value:>8,}{index:>10,}{shifts:>15,}"
          f"{math.ceil(math.log2(len(BASIS) + 1)):>13}")
print()
print("The right-hand column is identical in all five rows, and that is the")
print("point: the search is logarithmic and barely notices where the item")
print("belongs. The shift column varies by a factor of a thousand -- from")
print("1000 slots to none at all -- because `list.insert` moves everything")
print("above the slot, and a list is a flat array.")
print()
print("So `insort` is O(log n) to find and O(n) to place. It is only worth")
print("using when the list is short, or when you are inserting near the end,")
print("or when the list has to be sorted at every instant. It is not a way to")
print("build a sorted collection.")
print()
print()
print("Part 3 -- the cost of building a sorted list, both ways")
print()


def build_by_insort(values):
    """n inserts, each with its own shift. Returns the total slot moves."""
    items = []
    shifts = 0
    for value in values:
        index = bisect.bisect_right(items, value)
        shifts += len(items) - index
        items.insert(index, value)
    return shifts, items


print(f"{'n':>7}{'insort shifts':>15}{'sorted() cmps':>15}{'ratio':>8}"
      f"{'shifts/n^2':>12}")
print("-" * 57)
results = {}
for n in (100, 400, 1_600, 6_400):
    values = shuffled(n)
    shifts, built = build_by_insort(values)
    comparisons, sorted_once = count_sorted(values)
    results[n] = (shifts, comparisons, built == sorted_once)
    print(f"{n:>7,}{shifts:>15,}{comparisons:>15,}"
          f"{shifts / comparisons:>8.1f}{shifts / n ** 2:>12.2f}")
print()
worst = max(results)
print("Both routes produce the same list, and the ratio between them is not a")
print("constant -- it climbs with n, because one column is n^2 and the other")
print("is n log n. The last column is the tell: the shift total settles at")
print("n^2/4, which is what you get when each of n inserts moves about half")
print("of a list that is on average half full.")
print()
print(f"At n = {worst:,} the insort route has done about")
print(f"{results[worst][0] / results[worst][1]:.0f} times the work of a single sort, and the gap")
print("keeps widening. Append everything and call sorted() once: one pass")
print("to build, one n log n sort, and no shifting at all.")
print()
print("The one case where insort is right is a stream you have to query")
print("between arrivals -- a running median, a live percentile, a 'top 10 of")
print("the last minute'. Then the list has to be correct at every instant,")
print("and you are paying for that rather than for the sorting.")
print()
agreed = [ok for _, _, ok in results.values()]
print(f"  every route agreed on the result: {all(agreed)}")
print(f"  of {len(agreed)} sizes checked: {sum(agreed)} agreed")
