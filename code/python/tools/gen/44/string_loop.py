#!/usr/bin/env python3
"""Chapter 44 demo 10 -- the claim everybody repeats about string +=."""
import timeit


def build(n):
    s = ""
    for _ in range(n):
        s += "ab"
    return s


def best(n, number=3, repeat=7):
    return min(timeit.repeat(lambda: build(n), number=number, repeat=repeat))


def growth(ratio):
    """Bucketed, because a measured ratio is an estimate."""
    if ratio < 1.4:
        return "~1  (constant)"
    if ratio < 3.0:
        return "~2  (linear)"
    if ratio < 6.8:
        return "~4  (quadratic)"
    return "~8  (cubic)"


print("'building a string with += is O(n^2); use join' -- the standard advice.")
print()
print("Here is that exact pattern, measured:")
print()
print(f"{'n':>7}  {'on doubling n':>16}")
print("-" * 26)
for n in (1_000, 2_000, 4_000):
    print(f"{n:>7}  {growth(best(2 * n) / best(n)):>16}")

print()
print("Every doubling doubles the time. That is linear, not quadratic.")
print()
print("The advice is not wrong, it is incomplete. CPython has a special case")
print("in its string concatenation: when the left-hand string has exactly one")
print("reference to it, and no other name is looking at it, the interpreter")
print("resizes it in place instead of allocating a new one and copying. In a")
print("tight loop that is exactly the situation, so += becomes cheap and the")
print("quadratic term never appears.")
print()
print("Which means the next program is the interesting one: change one line")
print("so that the old string is still referenced, and watch what happens.")
