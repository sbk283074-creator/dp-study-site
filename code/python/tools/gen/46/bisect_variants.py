#!/usr/bin/env python3
"""Chapter 46 demo -- the two bisects, and what each one is for.

`bisect_left` and `bisect_right` differ by one comparison and answer two
different questions. Choosing the wrong one is a silent off-by-one in every
duplicate group.
"""
import bisect

SCORES = [40, 55, 55, 55, 70, 82, 82, 95]
GRADES = [(0, 50, "F"), (50, 60, "D"), (60, 70, "C"),
          (70, 80, "B"), (80, 101, "A")]
BOUNDARIES = [low for low, _, _ in GRADES[1:]]


def count_below(items, target):
    return bisect.bisect_left(items, target)


def count_at_most(items, target):
    return bisect.bisect_right(items, target)


print(f"a sorted list with duplicates: {SCORES}")
print()
print(f"{'target':>8}{'bisect_left':>14}{'bisect_right':>15}{'copies':>10}")
print("-" * 48)
for target in (40, 55, 70, 82, 95, 60):
    left = count_below(SCORES, target)
    right = count_at_most(SCORES, target)
    print(f"{target:>8}{left:>14}{right:>15}{right - left:>10}")
print()
print("The two functions are the same search with `<` and `<=`, and the")
print("difference is only visible where there are duplicates.")
print()
print("  bisect_left  is the number of items *strictly below* the target --")
print("               the index a new copy would take if it had to go")
print("               before the existing ones.")
print("  bisect_right is the number of items *at or below* the target -- the")
print("               index a new copy would take if it had to go after.")
print()
print("So `right - left` is the number of copies present, computed in two")
print("log n searches without counting anything. That is the standard way to")
print("answer 'how many of these are there' on sorted data.")
print()
print("It is also the whole of the 'insort stability' question. To see it, the")
print("items need to be distinguishable while still comparing equal -- so here")
print("is a class that compares on value only:")
print()


class Scored:
    """`bisect` needs nothing from an item except `<`, so a class that
    defines only that is a legal element of a sorted list."""

    __slots__ = ("value", "tag")

    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return f"{self.tag}{self.value}"


def tagged(values):
    return [Scored(value, chr(ord("a") + i)) for i, value in enumerate(values)]


print(f"  starting list: {tagged([40, 55, 55, 55, 70])}")
print("  inserting N55, which compares equal to three existing items")
print()
for function, name in ((bisect.insort_left, "insort_left"),
                       (bisect.insort_right, "insort_right")):
    items = tagged([40, 55, 55, 55, 70])
    function(items, Scored(55, "N"))
    print(f"  {name:<14} -> {items}")
print()
print("The new item lands at index 1 with insort_left and at index 4 with")
print("insort_right -- before its equals or after them. Both keep the list")
print("sorted by value, and only one keeps whatever order those three 55s")
print("already had. That is the same stability question as the previous")
print("demo, and the same one-character difference answers it.")
print()
print("Now the use that pays for knowing both. Grade bands are a list of")
print("boundaries and a search, not a chain of comparisons:")
print()
print(f"  boundaries: {BOUNDARIES}")
print(f"  grades    : {[label for _, _, label in GRADES]}")
print()
print(f"{'score':>8}{'bisect_right':>14}{'grade':>8}")
print("-" * 32)
for score in (0, 49, 50, 59, 60, 71, 80, 100):
    index = bisect.bisect_right(BOUNDARIES, score)
    print(f"{score:>8}{index:>14}{GRADES[index][2]:>8}")
print()
print("bisect_right is the correct one here, and getting it wrong is a")
print("one-mark error on every boundary score. A score of exactly 50 must")
print("land in D, not F, so the question is 'how many boundaries is this")
print("score at or above' -- which is bisect_right. Using bisect_left would")
print("put 50 in F and 80 in B, and the bug would look like a rounding")
print("problem rather than an indexing one.")
print()
print("That is the pattern to carry away. An if/elif chain over bands costs")
print("one comparison per band and grows with the number of bands; a bisect")
print("costs log n comparisons and does not care how many bands there are.")
print("For five grades it is a matter of taste. For the 500 tax brackets in")
print("a real payroll system it is not.")
