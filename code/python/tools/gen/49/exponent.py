#!/usr/bin/env python3
"""Chapter 49 demo -- proving a complexity instead of claiming it.

"Every element is compared with every other" is a sentence. n(n-1)/2 is a
number. The step between them is counting, and it is the step that turns an
intuition into evidence.

This script counts operations for four shapes, fits the exponent from the
counts, and then does the same fit on a pure model -- because the interesting
result is what the fit does when you already know the answer.

Nothing is timed. Every number is a count.
"""
import math
import random

# ------------------------------------------------------------------- shapes


def merge_sort_counted(values):
    """Merge sort that reports its exact comparison count."""
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(values), comparisons


def one_pass(values):
    """One look at each element."""
    ops = 0
    total = 0
    for v in values:
        ops += 1
        total += v
    return ops


def all_pairs(values):
    """Every unordered pair, once."""
    ops = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            ops += 1
    return ops


def halving_loop(values):
    """A nested loop that is NOT quadratic. Read it before you trust it."""
    ops = 0
    i = len(values)
    while i > 0:
        for _ in range(i):
            ops += 1
        i //= 2
    return ops


def sort_then_scan(values):
    """Sort, then one pass."""
    _, comparisons = merge_sort_counted(values)
    return comparisons + one_pass(values)


SHAPES = [
    ("one pass", one_pass),
    ("all pairs", all_pairs),
    ("halving loop", halving_loop),
    ("sort + scan", sort_then_scan),
]

SIZES = [256, 512, 1_024, 2_048]

rng = random.Random(49)
counts = {}
for name, fn in SHAPES:
    counts[name] = [fn([rng.randint(0, 1_000) for _ in range(n)]) for n in SIZES]


def exponent(xs, ys):
    """Fitted exponent between the last two points: log(y2/y1) / log(x2/x1)."""
    return math.log(ys[-1] / ys[-2]) / math.log(xs[-1] / xs[-2])


print("Four shapes, operations counted, and the exponent fitted from the")
print("last two sizes. The fitted value is a measurement, not a label.\n")
head = f"   {'shape':<14}" + "".join(f"{n:>12,}" for n in SIZES) + f"{'fitted':>10}"
print(head)
print("   " + "-" * (len(head) - 3))
for name, _ in SHAPES:
    row = f"   {name:<14}" + "".join(f"{c:>12,}" for c in counts[name])
    print(row + f"{exponent(SIZES, counts[name]):>10.2f}")

print()
print("`halving loop` is the one to look at twice. It has an inner `for` inside")
print("an outer `while`, so it reads as a nested loop and a reader who pattern-")
print("matches on shape will call it quadratic. Count it instead: the outer")
print("loop's bound halves, so the total is n + n/2 + n/4 + ... which is about")
print("2n. The fit says 1.00, and the fit is right.\n")
print(f"   {'n':>8}{'halving counted':>18}{'2n - 1':>10}{'agree':>8}")
print("   " + "-" * 44)
for n, c in zip(SIZES, counts["halving loop"]):
    print(f"   {n:>8,}{c:>18,}{2 * n - 1:>10,}{str(c == 2 * n - 1):>8}")
print()
print("For powers of two the sum is exactly 2n - 1, and the column confirms")
print("it. That is a proof of the linear bound for these inputs, and the")
print("reasoning -- a geometric series with ratio 1/2 -- covers the rest.")

# --------------------------------------------------- the fit is not a constant

print("\nNow the part that matters when you use a fit as evidence. Apply the")
print("same procedure to four complexity classes you already know, over a")
print("range of sizes, and watch the fitted exponent for n log n:\n")
WIDTHS = {"O(n)": 9, "O(n log n)": 13, "O(n^2)": 9, "O(n^3)": 9}
print(f"   {'range':<22}" + "".join(f"{k:>{w}}" for k, w in WIDTHS.items()))
print("   " + "-" * (25 + sum(WIDTHS.values())))
drift = []
prev = None
for n in (1_024, 4_096, 16_384, 65_536, 262_144, 1_048_576):
    model = {"O(n)": float(n),
             "O(n log n)": n * math.log2(n),
             "O(n^2)": float(n) ** 2,
             "O(n^3)": float(n) ** 3}
    if prev is not None:
        pn, pm = prev
        row = f"   {f'{pn:,} -> {n:,}':<22}"
        for key, w in WIDTHS.items():
            e = math.log(model[key] / pm[key]) / math.log(n / pn)
            row += f"{e:>{w}.2f}"
            if key == "O(n log n)":
                drift.append((f"{pn:,} -> {n:,}", e))
        print(row)
    prev = (n, model)

print()
print("The O(n), O(n^2) and O(n^3) columns report 1, 2 and 3 at every range --")
print("a polynomial's exponent is a constant, so doubling n multiplies the")
print("count by a fixed factor and the fit recovers it exactly.")
print()
first_range, first_e = drift[0]
last_range, last_e = drift[-1]
print(f"The n log n column does not settle. It reads {first_e:.2f} over the")
print(f"first range and {last_e:.2f} over the last, falling towards 1 at every")
print("step: slowly, because the log grows slowly. So a fitted exponent near")
print("1.1 is not a proof that an algorithm is n log n, and it is not a")
print("refutation of a linear one either. A single fitted number is evidence")
print("for a class; the way it drifts as the range grows is what separates")
print("n log n from n.")
