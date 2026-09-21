#!/usr/bin/env python3
"""Chapter 44 demo 8 -- what list.append actually does to memory."""
import sys

EMPTY = sys.getsizeof([])


def capacity(lst):
    """The list object holds a pointer to a separate array of slots.
    getsizeof reports both, so the difference is the slot count."""
    return (sys.getsizeof(lst) - EMPTY) // 8


def next_capacity(size):
    """CPython's growth rule from list_resize():
        newsize + (newsize >> 3) + 6,  rounded down to a multiple of 4
    where newsize is the length being asked for."""
    newsize = size + 1
    return (newsize + (newsize >> 3) + 6) & ~3


buf = []
previous = 0
print(f"sys.getsizeof([]) = {EMPTY} bytes, so each slot costs 8 bytes")
print()
print(f"{'length':>7}  {'capacity':>9}  {'rule predicts':>14}  {'match?':>6}")
print("-" * 42)
for length in range(1, 150):
    buf.append(length)
    now = capacity(buf)
    if now != previous:
        predicted = next_capacity(previous)
        verdict = "yes" if predicted == now else "NO"
        print(f"{length:>7}  {now:>9}  {predicted:>14}  {verdict:>6}")
        previous = now

print()
print("Every reallocation follows the same rule, and the rule never")
print("allocates exactly the length asked for. It always overshoots, and")
print("by more than a fixed amount: the surplus grows with the list.")
print()
print("That overshoot is the reason appending is cheap on average. A list")
print("that grew by exactly one slot each time would have to copy the whole")
print("array on every single append. Because it grows by a fraction of its")
print("own size, the copies get rarer the bigger the list gets -- and the")
print("total copying for n appends comes out proportional to n, not n^2.")
