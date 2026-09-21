#!/usr/bin/env python3
"""Chapter 44 solution 2 -- removing from the front of a list is not free."""
import timeit
from collections import deque


def drain_list(n):
    """pop(0) removes the first element and shifts everything left."""
    xs = list(range(n))
    while xs:
        xs.pop(0)


def drain_deque(n):
    """popleft removes the first element and shifts nothing."""
    d = deque(range(n))
    while d:
        d.popleft()


def per_call(fn, n, number=3, repeat=5):
    return min(timeit.repeat(lambda: fn(n), number=number, repeat=repeat)) / number


def growth(ratio):
    if ratio < 1.4:
        return "~1  (constant)"
    if ratio < 3.0:
        return "~2  (linear)"
    if ratio < 6.8:
        return "~4  (quadratic)"
    return "~8  (cubic)"


SIZES = (1_000, 2_000, 4_000, 8_000)
list_times = [per_call(drain_list, n) for n in SIZES]
deque_times = [per_call(drain_deque, n) for n in SIZES]

print("drain n items from the front, two ways")
print()
print(f"{'n':>7}  {'pop(0)':>18}  {'popleft':>18}")
print("-" * 46)
for i, n in enumerate(SIZES):
    if i == 0:
        continue
    print(f"{n:>7}  {growth(list_times[i] / list_times[i - 1]):>18}  "
          f"{growth(deque_times[i] / deque_times[i - 1]):>18}")

print()
print("Both loops remove every element, and both are correct. The left")
print("column is quadratic and the right column is linear, and the reason")
print("is one line of the implementation: a list stores its elements in one")
print("contiguous array, so removing the first one leaves a hole that every")
print("remaining element has to move into. A deque is a ring buffer, so")
print("removing the first element moves a pointer and nothing else.")
print()
print("This is the everyday version of the chapter's argument. `while xs:`")
print("looks the same in both functions; the cost model is entirely")
print("different; and at a thousand items you would not notice. The rule")
print("that falls out of it: if you are removing from the front of a queue,")
print("use a deque. If you are removing from the front of a list, ask")
print("yourself why.")
