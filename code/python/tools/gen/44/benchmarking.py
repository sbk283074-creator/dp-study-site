#!/usr/bin/env python3
"""Chapter 44 demo 12 -- how to take a timing that means something."""
import timeit


def time_band(seconds):
    if seconds < 1e-3:
        return "under 1 ms"
    if seconds < 1.0:
        return "1 ms to 1 s"
    return "over 1 s"


def verdict(seconds):
    if seconds < 1e-3:
        return "too short"
    return "usable"


CASES = [
    ("x = 1", "x = 1", 1),
    ("x = 1", "x = 1", 10_000_000),
    ("sum(range(1000))", "sum(range(1000))", 1),
    ("sum(range(1000))", "sum(range(1000))", 10_000),
    ("sorted(range(10000))", "sorted(range(10000))", 100),
]

print("the same statements, each measured 7 times, at two different")
print("values of `number`. `number` is how many times the statement runs")
print("inside one measurement; only the total is timed.")
print()
print(f"{'statement':<22}{'number':>10}  {'measured total':>15}  {'verdict':>10}")
print("-" * 62)
for label, stmt, number in CASES:
    total = min(timeit.repeat(stmt, number=number, repeat=7))
    print(f"{label:<22}{number:>10}  {time_band(total):>15}  {verdict(total):>10}")

print()
print("A statement that finishes in tens of nanoseconds cannot be measured")
print("once. The clock is good, but not that good, and everything else")
print("happening on the machine -- the operating system, other processes,")
print("the CPU changing frequency -- is larger than the thing you are")
print("trying to measure. Run it a million times and divide: the noise")
print("averages out because the work does not.")
print()
print("Aim for a measurement that takes at least a tenth of a second. If")
print("it is shorter, raise `number`. timeit will pick one for you if you")
print("let it.")
print()
print("And once you have the repeats, take the *minimum*, not the mean.")
print("Noise on a shared machine only ever adds time -- a run can be slow")
print("because something else was running, but it cannot be faster than")
print("the work itself. So the fastest run is the closest estimate of the")
print("true cost, and the mean is an estimate of the true cost plus")
print("whatever else the machine was doing at the time.")
