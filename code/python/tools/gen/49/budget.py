#!/usr/bin/env python3
"""Chapter 49 demo -- the constraints are the specification.

A problem statement's size limit is not decoration. It is the intended
complexity, written in the only language the statement has: arithmetic.
This script does that arithmetic for every complexity class and reports the
largest n that still fits a fixed operation budget.

Everything is computed in log10 space. That is not a trick for looking
clever -- it is forced. The operation counts span more than four hundred
thousand orders of magnitude (n! at n = 100,000), so no float can hold them
and any code that tries will raise OverflowError. log10 is monotone, so a
search in log space finds exactly the same n, and every comparison stays a
comparison of small numbers.

Nothing here is timed. A count is a fact about the algorithm; a timing is a
fact about this machine.
"""
import math

BUDGET_LOG10 = 8.0          # log10(100,000,000)
N_CEILING = 10 ** 12

CLASSES = [
    ("O(1)", lambda n: 0.0),
    ("O(log n)", lambda n: math.log10(math.log2(n)) if n > 1 else 0.0),
    ("O(n)", lambda n: math.log10(n)),
    ("O(n log n)", lambda n: math.log10(n) + math.log10(math.log2(n)) if n > 1 else 0.0),
    ("O(n^2)", lambda n: 2 * math.log10(n)),
    ("O(n^3)", lambda n: 3 * math.log10(n)),
    ("O(2^n)", lambda n: n * math.log10(2)),
    ("O(n!)", lambda n: math.lgamma(n + 1) / math.log(10)),
]


def largest_fitting(log10_ops):
    """Largest n in [1, N_CEILING] with log10_ops(n) <= BUDGET_LOG10.

    Doubling finds a bracket, binary search closes it. Both are needed: the
    classes span fifteen orders of magnitude in n as well, so a fixed step
    would either crawl at one end or be useless at the other.
    """
    lo, hi = 1, 2
    while log10_ops(hi) <= BUDGET_LOG10:
        if hi >= N_CEILING:
            return None                  # no limit at any n we care about
        lo, hi = hi, min(hi * 2, N_CEILING)
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if log10_ops(mid) <= BUDGET_LOG10:
            lo = mid
        else:
            hi = mid
    return lo


def show_ops(log10_ops):
    """Render an operation count from its log10, whatever its size."""
    if log10_ops <= 12:
        return f"{10 ** log10_ops:,.0f}"
    return f"10^{log10_ops:,.0f}"


print(f"An operation budget of {10 ** BUDGET_LOG10:,.0f} is the one constant.")
print("For each complexity class, the largest n that still fits it:\n")
print(f"   {'class':<11}{'largest n that fits':>21}{'operations there':>18}")
print("   " + "-" * 48)
for name, log10_ops in CLASSES:
    n = largest_fitting(log10_ops)
    if n is None:
        print(f"   {name:<11}{'beyond ' + f'{N_CEILING:,}':>21}{'-':>18}")
    else:
        print(f"   {name:<11}{n:>21,}{show_ops(log10_ops(n)):>18}")

print()
print("Read the right-hand column downwards: every class lands in the same")
print("band, because the budget is what is fixed and n is what moves. The")
print("size limit in a problem statement is that band, restated in the one")
print("variable the statement is allowed to mention.")

# ---------------------------------------------------------------- the decision
N = 100_000
print(f"\nNow fix n instead. At n = {N:,}, which classes still fit?\n")
print(f"   {'class':<11}{'operations':>14}   {'fits the budget?':<17}")
print("   " + "-" * 44)
for name, log10_ops in CLASSES:
    ops = log10_ops(N)
    print(f"   {name:<11}{show_ops(ops):>14}   "
          f"{'yes' if ops <= BUDGET_LOG10 else 'NO':<17}")

print()
print("Two of those eight rows are the whole chapter. At n = 100,000 an")
print("O(n^2) solution does 10,000,000,000 operations where an O(n log n)")
print("solution does about 1,660,000 -- six thousand times fewer, and the")
print("difference between a timeout and a pass.")

# ------------------------------------------------------------------ the rate
slow_log10 = 2 * math.log10(N)          # O(n^2) at n = 100,000
seconds = 10 ** (slow_log10 - 7)        # at a stated 10^7 operations/second
print(f"\nConverting one row to time needs a rate, and the rate is an")
print(f"assumption rather than a measurement. Take 10^7 operations per")
print(f"second -- roughly a straightforward Python loop:")
print(f"\n   O(n^2) at n = {N:,}   {10 ** slow_log10:,.0f} operations")
print(f"                          about {seconds:,.0f} seconds "
      f"({seconds / 60:,.0f} minutes)")
fast = 10 ** (math.log10(N) + math.log10(math.log2(N)))
print(f"   O(n log n) at the same n   {fast:,.0f} operations")
print(f"                              about {fast / 1e7:.2f} seconds")
print()
print("A tight loop in C is a hundred times faster and a slow one in pure")
print("Python is a hundred times slower, so the seconds are soft. The")
print("decision is not: a factor of six thousand does not get eaten by a")
print("constant factor.")
