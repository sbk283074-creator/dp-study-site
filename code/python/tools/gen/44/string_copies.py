#!/usr/bin/env python3
"""Chapter 44 demo 11 -- the same statement, one extra reference, O(n^2)."""
import timeit


def tight(n):
    """The old string dies at each assignment, so CPython resizes in place."""
    s = ""
    for _ in range(n):
        s += "ab"
    return s


def with_a_second_reference(n):
    """Identical loop, except the previous string is kept alive."""
    s = ""
    history = []
    for _ in range(n):
        history.append(s)      # <- the only difference
        s += "ab"
    return s


def best(fn, n, number=3, repeat=7):
    return min(timeit.repeat(lambda: fn(n), number=number, repeat=repeat))


def band(ratio):
    if ratio < 2.0:
        return "~1x"
    if ratio < 4.5:
        return "~3x"
    if ratio < 8.0:
        return "~6x"
    return "~10x or more"


print("two functions. The string-building loop is the same statement.")
print("One of them also keeps the previous value in a list.")
print()
print(f"{'n':>7}  {'kept version / tight version':>29}")
print("-" * 40)
for n in (1_000, 2_000, 4_000, 8_000):
    gap = best(with_a_second_reference, n) / best(tight, n)
    print(f"{n:>7}  {band(gap):>29}")

print()
print("At n=1000 the two are within a small factor of each other. By n=8000")
print("the gap has grown by roughly an order of magnitude -- and it is still")
print("growing, because one is linear and the other is quadratic.")
print()
print("The lesson is not about strings. It is that a complexity claim is a")
print("claim about a program, not about a syntax. `s += t` is O(1) amortised")
print("in one loop and O(n) per step in another, and the difference is not")
print("visible in the line of code -- it is visible in what else holds a")
print("reference to the object.")
print()
print("This is why the folklore is worth checking. 'Always use join' is")
print("cheap advice that is sometimes wrong; 'measure the pattern you")
print("actually wrote' is expensive advice that is never wrong.")
