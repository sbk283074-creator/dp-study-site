#!/usr/bin/env python3
"""Chapter 45 demo -- what a heap actually buys, counted exactly.

Every comparison a heap makes goes through `<` on the objects it holds, so
wrapping the values in a class with a counting __lt__ turns the algorithm
into a number. That number is the same on every machine and in every run.
"""
import heapq

N = 10_000


class Counted:
    """A value that reports how often it was compared."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value

    def __repr__(self):
        return f"Counted({self.value})"


def permutation(n):
    """A fixed, well-mixed order with no randomness in it: multiply by a
    prime coprime to n and take the remainder."""
    return [(i * 7919) % n for i in range(n)]


values = permutation(N)
counter = [0]
items = [Counted(v, counter) for v in values]

heap = list(items)
counter[0] = 0
heapq.heapify(heap)
heapify_cost = counter[0]

counter[0] = 0
pushed = []
for item in items:
    heapq.heappush(pushed, item)
push_cost = counter[0]

counter[0] = 0
drained = []
while pushed:
    drained.append(heapq.heappop(pushed))
pop_cost = counter[0]

counter[0] = 0
ordered = sorted(items)
sort_cost = counter[0]

print(f"{N:,} values, in a fixed scrambled order")
print()
print(f"{'operation':<34}{'comparisons':>14}{'per item':>10}")
print("-" * 58)
print(f"{'heapq.heapify (all at once)':<34}{heapify_cost:>14,}{heapify_cost / N:>10.1f}")
print(f"{'n x heapq.heappush':<34}{push_cost:>14,}{push_cost / N:>10.1f}")
print(f"{'n x heapq.heappop':<34}{pop_cost:>14,}{pop_cost / N:>10.1f}")
print(f"{'sorted (for comparison)':<34}{sort_cost:>14,}{sort_cost / N:>10.1f}")
print()
print("Read the first row against the last. Sorting compares about twelve")
print("times per item, which is log2(10,000) with Timsort's constant folded")
print("in. heapify compares under two -- it is O(n), not O(n log n), because")
print("it sifts down from the middle rather than pushing from the left, and")
print("most of the nodes are near the bottom where a sift is short.")
print()
print("The middle two rows show the other half of the story. Popping every")
print("item is O(log n) each, which is why a heap sort costs what a sort")
print("costs. And a heap built by pushing one item at a time is O(n log n),")
print("worse than heapify on the same data. If you already have all the")
print("items, heapify them.")
print()
print("Now the part that surprises people. The heap is not sorted.")
print()
print(f"{'heap array, first 8':<24}{[item.value for item in heap[:8]]}")
print(f"{'sorted list, first 8':<24}{[item.value for item in ordered[:8]]}")
print(f"{'heap[0] is the minimum':<24}{heap[0].value}")
print()
print("Only the root is guaranteed. The array behind the heap satisfies")
print("`parent <= both children` at every position and nothing else, which")
print("is exactly enough to answer 'what is the smallest?' in O(1) and to")
print("remove it in O(log n) -- and not enough to answer anything else.")
print()
print("That is the trade to remember. A heap answers one question, costs")
print("under two comparisons per item to build, and accepts a new item in")
print("log n. A sorted list answers every question about order, costs")
print("twelve comparisons per item to build, and cannot accept a new item")
print("without paying n shifts for it.")
