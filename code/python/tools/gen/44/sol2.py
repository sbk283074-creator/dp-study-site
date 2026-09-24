#!/usr/bin/env python3
"""Chapter 44 solution 2 -- removing from the front of a list is not free.

The count is of elements moved. It follows from the data structure rather than
from the machine: a list is one contiguous array, so removing the first element
leaves a hole that every remaining element has to move into.
"""
from collections import deque


def drain_list(n):
    """pop(0) removes the first element and shifts everything left."""
    xs = list(range(n))
    moved = 0
    while xs:
        xs.pop(0)
        moved += len(xs)      # every remaining element shifts down one slot
    return moved


def drain_deque(n):
    """popleft removes the first element and moves a pointer instead."""
    d = deque(range(n))
    moved = 0
    while d:
        d.popleft()
    return moved


SIZES = (1_000, 2_000, 4_000, 8_000)
list_moves = [drain_list(n) for n in SIZES]
deque_moves = [drain_deque(n) for n in SIZES]

print("drain n items from the front, two ways")
print()
print(f"{'n':>7}{'pop(0) moves':>16}{'popleft moves':>16}")
print("-" * 39)
for index, n in enumerate(SIZES):
    print(f"{n:>7}{list_moves[index]:>16,}{deque_moves[index]:>16,}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes tried':<46}{len(SIZES):>8}")
print(f"{'elements drained, largest n':<46}{SIZES[-1]:>8}")
print(f"{'moves, pop(0), smallest n':<46}{list_moves[0]:>8}")
print(f"{'moves, pop(0), largest n':<46}{list_moves[-1]:>8}")
print(f"{'moves, popleft, every n':<46}{deque_moves[-1]:>8}")
print(f"{'on doubling n, pop(0)':<46}"
      f"{list_moves[-1] / list_moves[-2]:>8.1f}")
print(f"{'on doubling n, popleft':<46}{1.0:>8.1f}")
print(f"{'times more work pop(0) does, largest n':<46}"
      f"{list_moves[-1] / max(1, SIZES[-1]):>8.0f}")

print()
print("Both loops remove every element, and both are correct. The left column")
print("is quadratic and the right column is zero, and the reason is one line of")
print("the implementation: a list stores its elements in one contiguous array,")
print("so removing the first one leaves a hole that every remaining element has")
print("to move into. A deque is a ring buffer, so removing the first element")
print("moves a pointer and nothing else.")
print()
print(f"The zero is the part worth looking at. It is not a small number, it is")
print(f"the absence of the operation: at {SIZES[-1]:,} items the list has moved")
print(f"{list_moves[-1]:,} elements and the deque has moved none. No constant factor")
print("closes a gap like that -- only changing the data structure does.")
print()
print("This is the everyday version of the chapter's argument. `while xs:` looks")
print("the same in both functions, the cost model is entirely different, and at")
print("a thousand items you would not notice. The rule that falls out of it: if")
print("you are removing from the front of a queue, use a deque. If you are")
print("removing from the front of a list, ask yourself why.")
