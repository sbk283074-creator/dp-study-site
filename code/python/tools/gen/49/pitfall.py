#!/usr/bin/env python3
"""Chapter 49 demo -- the arithmetic that decides pass or fail.

A size limit is a statement about the intended complexity, and reading it
wrong is the most expensive mistake in this chapter. The same O(n^2)
solution passes one constraint and fails another, and the only way to know
which is to do the arithmetic before writing the code.

The second half is the error in the other direction. Reaching for the
clever algorithm when the constraint does not require it is not free, and
what it costs is not lines of code -- it is a precondition, and this script
measures how often a small random test would exercise it.
"""
import math
import random

BUDGET_LOG10 = 8.0          # a hundred million operations
RATE_LOG10 = 7.0            # a stated assumption: 10^7 operations per second


def largest_fitting(log10_ops, ceiling=10 ** 12):
    """Largest n with log10_ops(n) <= BUDGET_LOG10, by doubling then bisecting."""
    lo, hi = 1, 2
    while log10_ops(hi) <= BUDGET_LOG10:
        if hi >= ceiling:
            return None
        lo, hi = hi, min(hi * 2, ceiling)
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if log10_ops(mid) <= BUDGET_LOG10:
            lo = mid
        else:
            hi = mid
    return lo


CLASSES = [
    ("O(n)", lambda n: math.log10(n)),
    ("O(n log n)", lambda n: math.log10(n) + math.log10(math.log2(n))),
    ("O(n^2)", lambda n: 2 * math.log10(n)),
    ("O(n^3)", lambda n: 3 * math.log10(n)),
]

# --------------------------------------------- the same code, two constraints

print("One algorithm, six constraints. O(n^2) does not have a verdict -- only")
print("an O(n^2) *at a size* does.\n")
print(f"   {'n':>12}{'O(n)':>20}{'O(n log n)':>20}{'O(n^2)':>22}"
      f"   {'O(n^2) verdict':<12}")
print("   " + "-" * 90)
for n in (1_000, 5_000, 10_000, 50_000, 100_000, 1_000_000):
    line = f"   {n:>12,}"
    for _, fn in CLASSES[:3]:
        value = 10 ** fn(n)
        line += f"{value:>20,.0f}" if fn(n) <= 15 else f"{'10^' + f'{fn(n):.0f}':>20}"
    verdict = "fits" if CLASSES[2][1](n) <= BUDGET_LOG10 else "does not fit"
    print(line + f"   {verdict:<12}")

print()
print("The verdict flips between n = 10,000 and n = 50,000, and the exact")
print("place is worth remembering: n^2 reaches a hundred million at n =")
print("10,000. So a constraint of n <= 10^4 is a setter telling you that a")
print("quadratic solution is expected, and a constraint of n <= 10^5 is a")
print("setter telling you that it is not. Same algorithm, same code, opposite")
print("answers -- and the difference is one digit in the statement.")

print("\nStated as limits, which is how a setter thinks about them:\n")
print(f"   {'complexity':<14}{'largest n inside the budget':>30}")
print("   " + "-" * 44)
for name, fn in CLASSES:
    n = largest_fitting(fn)
    shown = f"{n:,}" if n is not None else "no limit below 10^12"
    print(f"   {name:<14}{shown:>30}")

print()
print("Read a constraint off this table rather than off the algorithm. If the")
print("statement says n <= 100,000, the intended solution is O(n log n) or")
print("better, and an O(n^2) sketch is not a slow version of the answer --")
print("it is not an answer.")

# ---------------------------------------------- the error in the other direction


def count_naive(values, k):
    """The slow, obvious version. No preconditions."""
    total = 0
    for i in range(len(values)):
        running = 0
        for j in range(i, len(values)):
            running += values[j]
            if running == k:
                total += 1
    return total


def count_with_prefix(values, k, seed=True):
    """The fast version. The seeded entry is a precondition."""
    seen = {0: 1} if seed else {}
    running = 0
    total = 0
    for v in values:
        running += v
        total += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return total


print("\nNow the other direction. At n = 1,000 the quadratic version above does")
print("499,500 additions. At the stated rate that is five hundredths of a")
print("second, which is inside every budget this book has used. So the clever")
print("version is not needed here, and choosing it is a decision about code")
print("rather than about speed.\n")
print(f"   {'n':>10}{'additions':>18}{'seconds at 1e7/s':>20}")
print("   " + "-" * 48)
for n in (100, 1_000, 10_000):
    pairs = n * (n + 1) // 2
    print(f"   {n:>10,}{pairs:>18,}{pairs / 10 ** RATE_LOG10:>19.4f}")

print()
print("What the clever version costs is not lines -- in Python it is usually")
print("shorter. It is a precondition: the empty prefix has to be in the")
print("dictionary before the loop starts, or every subarray that begins at")
print("index 0 is missed. Measure how often a random test would catch that")
print("omission:\n")
rng = random.Random(49)
print(f"   {'n range':<12}{'instances':>12}{'seed matters':>14}{'would catch it':>16}")
print("   " + "-" * 54)
for hi in (10, 20, 50, 200):
    instances = 2_000
    caught = 0
    for _ in range(instances):
        n = rng.randint(1, hi)
        values = [rng.randint(-3, 3) for _ in range(n)]
        k = rng.randint(-5, 5)
        if count_with_prefix(values, k, seed=True) != count_with_prefix(
                values, k, seed=False):
            caught += 1
    print(f"   {'1..' + str(hi):<12}{instances:>12,}{caught:>14,}"
          f"{100 * caught / instances:>15.1f}%")

print()
print("At the sizes a quick test uses, the omission is invisible most of the")
print("time, and the rate climbs as the list grows -- 31% at ten elements,")
print("58% at fifty. That is the shape of the trade: the fast version carries")
print("a precondition, the slow one carries none, and the precondition is")
print("exercised least on exactly the small inputs you would test with.")

print("\nSo the third question -- 'which structure?' -- comes after the second.")
print("Derive the budget from the constraint, choose the structure that meets")
print("it, and stop. A solution faster than the budget requires is not better;")
print("it is more to get right than the problem asked for. And a solution")
print("slower than the budget allows is not slower -- it is wrong.")
