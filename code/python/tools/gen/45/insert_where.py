#!/usr/bin/env python3
"""Chapter 45 demo -- where you insert decides the price.

No stopwatch in this one. The cost here is a memmove, and a memmove is so
fast per byte that a 200-iteration loop cannot see it: the loop overhead
swamps it. Count the bytes instead -- that number is exact, and it is the
number that actually explains the production incident.
"""
N = 5_000
K = 200
SLOT = 8


def shifts_for_front_inserts(n, k):
    """Each insert(0, x) shifts the whole current list up one slot. The list
    grows by one each time, so the shifts are
    n + (n+1) + ... + (n+k-1)  =  k*n + k(k-1)/2."""
    return k * n + k * (k - 1) // 2


def megabytes(slots):
    return slots * SLOT / 1_000_000


print("moving 200 new items to the front of a list")
print()
print(f"{'list size':>12}{'element shifts':>18}{'memory traffic':>18}")
print("-" * 48)
for n in (5_000, 50_000, 500_000, 1_000_000):
    moved = shifts_for_front_inserts(n, K)
    print(f"{n:>12,}{moved:>18,}{megabytes(moved):>15,.1f} MB")
print()
print(f"The formula is k*n + k(k-1)/2 with k = {K}. The k*n term dominates,")
print("so the cost is proportional to how long the list already is -- not")
print("to how many items you are adding. That is the whole trap: the loop")
print("runs 200 times at every size, and it gets 200x more expensive.")
print()
print("Now the other end. Appending k items to the same list:")
print()
print(f"{'list size':>12}{'element shifts':>18}")
print("-" * 30)
for n in (5_000, 1_000_000):
    print(f"{n:>12,}{0:>18,}")
print()
print("Zero, in both cases, because the array already has spare capacity")
print("-- which is what the overshoot from Chapter 44 bought you.")
print()
print("So a list is not 'fast' or 'slow'. It is O(1) at the end and O(n)")
print("at the front, and the gap between those two numbers is the reason")
print("`deque` exists. Choose the end you use.")
