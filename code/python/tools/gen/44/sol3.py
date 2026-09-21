#!/usr/bin/env python3
"""Chapter 44 solution 3 -- predict the capacity, then check it."""
import sys

EMPTY = sys.getsizeof([])


def next_capacity(size):
    """CPython's growth rule, from list_resize()."""
    newsize = size + 1
    return (newsize + (newsize >> 3) + 6) & ~3


def predict(length):
    """The capacity a list ends up with after `length` appends."""
    capacity = 0
    size = 0
    for _ in range(length):
        if size == capacity:
            capacity = next_capacity(capacity)
        size += 1
    return capacity


def build(length):
    """Build by appending, one at a time."""
    buf = []
    for _ in range(length):
        buf.append(0)
    return buf


def measured(lst):
    return (sys.getsizeof(lst) - EMPTY) // 8


print("a list built by appending, one element at a time:")
print()
print(f"{'length':>8}  {'predicted':>10}  {'measured':>9}  {'agree':>6}")
print("-" * 38)
for length in (100, 500, 1_000, 2_000, 5_000, 10_000):
    predicted = predict(length)
    actual = measured(build(length))
    print(f"{length:>8}  {predicted:>10}  {actual:>9}  "
          f"{'yes' if predicted == actual else 'NO':>6}")

print()
print("The rule reproduces the real capacity at every size, so you can")
print("answer 'how much memory will this list waste?' without running")
print("anything. A list of 10,000 items does not hold 10,000 slots; it")
print("holds however many the growth rule last asked for, and that is")
print("always a little more.")
print()
print("One more thing worth knowing, because it trips people up when they")
print("try this at home:")
print()
n = 10_000
print(f"  built by appending     {measured(build(n)):>7} slots")
print(f"  built from list(range) {measured(list(range(n))):>7} slots")
print()
print("Both lists have the same length and hold the same values, but they")
print("do not have the same capacity. `list(iterable)` is told the length")
print("in advance, so it allocates exactly the slots it needs and never")
print("overshoots -- which is why it uses less memory than the same list")
print("built by appending, and why the growth rule above does not describe")
print("it. The lesson generalises past lists: the cost of building a")
print("structure depends on how you build it, not only on what it ends up")
print("containing.")
