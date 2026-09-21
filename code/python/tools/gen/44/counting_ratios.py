#!/usr/bin/env python3
"""Chapter 44 demo 3 -- the doubling ratio is the fingerprint."""


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


def steps_cubic(n):
    count = 0
    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                count += 1
    return count


CASES = [
    ("log n", steps_log),
    ("n", steps_linear),
    ("n log n", steps_nlogn),
    ("n^2", steps_quadratic),
    ("n^3", steps_cubic),
]

print("double n and watch what the step count does")
print()
print(f"{'shape':>8}  {'n=64':>10}  {'n=128':>10}  {'n=256':>10}   ratio at each doubling")
print("-" * 72)
for name, fn in CASES:
    a, b, c = fn(64), fn(128), fn(256)
    r1, r2 = b / a, c / b
    print(f"{name:>8}  {a:>10}  {b:>10}  {c:>10}   {r1:>5.2f} then {r2:>5.2f}")

print()
print("Read the last column, not the middle one:")
print()
print("  log n     adds a constant, so the ratio falls towards 1")
print("  n         ratio 2      -- doubling the input doubles the work")
print("  n log n   ratio 2.2    -- barely more than n; the log is a small factor")
print("  n^2       ratio 4      -- doubling the input quadruples the work")
print("  n^3       ratio 8      -- and this is where it stops being usable")
print()
print("A ratio of 4 is the signature of a quadratic. It does not matter what")
print("the machine is, what the language is, or how fast the constant factor")
print("is: doubling the input multiplies the work by four, every time.")
