#!/usr/bin/env python3
"""Chapter 45 solution 2 -- merging k sorted lists with a heap."""
import heapq


def merge_sorted(lists):
    """Put the head of each list in a heap. Take the smallest, then push the
    next item from the list it came from. The heap never holds more than k
    items, so every step costs log k rather than log of the total."""
    heap = []
    for index, items in enumerate(lists):
        if items:
            heap.append((items[0], index, 0))
    heapq.heapify(heap)

    merged = []
    while heap:
        value, list_index, offset = heapq.heappop(heap)
        merged.append(value)
        offset += 1
        source = lists[list_index]
        if offset < len(source):
            heapq.heappush(heap, (source[offset], list_index, offset))
    return merged


def merge_by_sorting(lists):
    return sorted(value for items in lists for value in items)


LISTS = [
    [0, 6, 12, 18],
    [1, 7, 13, 19],
    [2, 8, 14, 20],
    [3, 9, 15, 21],
    [4, 10, 16, 22],
    [5, 11, 17, 23],
]

merged = merge_sorted(LISTS)
print("six sorted lists")
for index, items in enumerate(LISTS):
    print(f"  list {index}: {items}")
print()
print(f"merged: {merged}")
print()
print("agrees with a plain sort :", merged == merge_by_sorting(LISTS))
print()
print("The tuple is doing work here. `(value, list_index, offset)` never")
print("compares equal on the first element alone, so the heap never has to")
print("compare a list to a list or an index to a value -- the comparison")
print("stops at whichever field settles it. Push bare values instead and the")
print("algorithm breaks on the first tie, with a TypeError rather than a")
print("wrong answer, which is at least the kinder failure.")
print()
print("The cost argument is the reason to do this rather than sort. Sorting")
print("n items from k lists costs n log n. The heap costs n log k, and the")
print("heap is never larger than k. With a hundred thousand items spread over")
print("four lists that is 17 comparisons per item against 2, and with a")
print("million items arriving in two streams it is 20 against 1.")
print()
print("That is the same trade as the top-ten demo: pay for the order you")
print("actually need. Merging k sorted streams needs the order of k things at")
print("a time, not the order of n.")
