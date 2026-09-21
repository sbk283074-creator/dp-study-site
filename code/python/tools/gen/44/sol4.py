#!/usr/bin/env python3
"""Chapter 44 solution 4 -- the cheapest way to find one element."""
import math
import random
import timeit

RND = random.Random(11)
DATA = [RND.random() for _ in range(200_000)]


def per_call(stmt, number, globs):
    return min(timeit.repeat(stmt, number=number, repeat=5, globals=globs)) / number


def growth(ratio):
    if ratio < 1.4:
        return "~1  (constant)"
    if ratio < 3.0:
        return "~2  (linear)"
    if ratio < 6.8:
        return "~4  (quadratic)"
    return "~8  (cubic)"


def factor(ratio):
    if ratio < 1.5:
        return "about the same"
    if ratio < 3.0:
        return "~2x"
    if ratio < 7.0:
        return "~5x"
    if ratio < 15.0:
        return "~10x"
    return "15x or more"


print("the smallest of n numbers, two ways")
print()
print(f"{'n':>8}  {'min(xs)':>18}  {'sorted(xs)[0]':>18}")
print("-" * 48)
previous = {}
last_ratio = 1.0
for n in (25_000, 50_000, 100_000, 200_000):
    xs = DATA[:n]
    g = {"xs": xs}
    t_min = per_call("min(xs)", 20, g)
    t_sort = per_call("sorted(xs)[0]", 3, g)
    last_ratio = t_sort / t_min
    if previous:
        print(f"{n:>8}  {growth(t_min / previous['min']):>18}  "
              f"{growth(t_sort / previous['sort']):>18}")
    previous = {"min": t_min, "sort": t_sort}

print()
print(f"and at the largest size, sorted takes {factor(last_ratio)} what min takes")
print()
print("Both growth columns read about 2, and that is the honest result: at")
print("any size you can conveniently measure, n and n log n are not")
print("distinguishable by timing. The difference is real -- log n goes from")
print("17 to 18 between the last two rows -- but it lands as a few percent")
print("of the ratio, which is smaller than the noise in the clock.")
print()
print("So the argument for min does not come from that table. It comes")
print("from counting:")
print()
print(f"{'n':>8}  {'min: n - 1':>12}  {'sorted: n log n':>16}")
print("-" * 40)
for n in (25_000, 50_000, 100_000, 200_000):
    print(f"{n:>8}  {n - 1:>12}  {round(n * math.log2(n)):>16}")

print()
print("Those numbers are exact, and they say what the clock could not: the")
print("gap between the two approaches widens as n grows, without limit.")
print()
print("The practical rule is still the simple one. If you want the minimum,")
print("ask for the minimum -- `min`, not `sorted(...)[0]`. The complexity")
print("argument makes it right at scale, the readability argument makes it")
print("right immediately, and this exercise is a reminder that the")
print("complexity argument had to be made by counting, because the")
print("stopwatch was never going to make it.")
