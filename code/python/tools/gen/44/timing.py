#!/usr/bin/env python3
"""Chapter 44 demo 5 -- counting and timing, side by side."""
import timeit


# --- counters: exact, machine-independent -------------------------------
def steps_log(n):
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count


def steps_linear(n):
    count = 0
    for _ in range(n):
        count += 1
    return count


def steps_nlogn(n):
    count = 0
    size = 1
    while size < n:
        for _ in range(n):
            count += 1
        size *= 2
    return count


def steps_quadratic(n):
    count = 0
    for _ in range(n):
        for _ in range(n):
            count += 1
    return count


# --- the same four shapes, as real work ---------------------------------
def work_log(n):
    total = 0
    while n > 1:
        n //= 2
        total += 1
    return total


def work_linear(n):
    return sum(range(n))


def work_nlogn(n):
    return sorted(range(n))


def work_quadratic(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total


def best(fn, n, number, repeat=7):
    """The minimum of several repeats. Noise only ever ADDS time, so the
    minimum is the closest thing to the true cost that we can measure."""
    return min(timeit.repeat(lambda: fn(n), number=number, repeat=repeat))


def measured_shape(ratio):
    """Deliberately wide bands. A measured ratio is an estimate, and the
    gaps between the real classes are much wider than the noise."""
    if ratio < 1.5:
        return "~1"
    if ratio < 3.0:
        return "~2"
    if ratio < 7.0:
        return "~4-6"
    return "~8+"


CASES = [
    ("log n", steps_log, work_log, 400_000, 20),
    ("n", steps_linear, work_linear, 400_000, 20),
    ("n log n", steps_nlogn, work_nlogn, 200_000, 10),
    ("n^2", steps_quadratic, work_quadratic, 400, 1),
]

print("the counted ratio is exact; the measured one is an estimate")
print()
print(f"{'shape':>8}  {'counted':>8}  {'measured':>9}  {'verdict':>9}")
print("-" * 42)
for name, steps, work, n, number in CASES:
    counted = steps(2 * n) / steps(n)
    measured = measured_shape(best(work, 2 * n, number) / best(work, n, number))
    verdict = "agrees" if measured == measured_shape(counted) else "DISAGREES"
    print(f"{name:>8}  {counted:>8.2f}  {measured:>9}  {verdict:>9}")

print()
print("The counted column is arithmetic: it is the same on every machine,")
print("and it is the one to quote. The measured column is a clock reading,")
print("and it is only ever an estimate -- which is why it is reported as a")
print("band and not as a number.")
print()
print("Both columns put every shape in the same bucket. That is what makes a")
print("complexity claim worth something: the ratio is a property of the")
print("algorithm, so it survives the move from counting to timing.")
print()
print("Notice that n and n log n land in the same bucket. At the sizes we")
print("timed, log n goes from 18 to 19, so the n log n ratio comes out at")
print("2.11 against the linear shape's 2.00 -- a difference far smaller than")
print("the noise in any clock reading. If you need to tell those two apart,")
print("count; do not time.")
