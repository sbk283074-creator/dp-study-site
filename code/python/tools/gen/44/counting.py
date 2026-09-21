#!/usr/bin/env python3
"""Chapter 44 demo 2 -- count the steps instead of timing them."""


def count_constant(n):
    """One step, whatever n is."""
    return 1


def count_log(n):
    """Halve until you reach 1."""
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps


def count_linear(n):
    """One step per item."""
    steps = 0
    for _ in range(n):
        steps += 1
    return steps


def count_nlogn(n):
    """A linear pass, repeated while the window doubles."""
    steps = 0
    size = 1
    while size < n:
        for _ in range(n):
            steps += 1
        size *= 2
    return steps


def count_quadratic(n):
    """Every item against every other item."""
    steps = 0
    for _ in range(n):
        for _ in range(n):
            steps += 1
    return steps


def count_cubic(n):
    """Every pair, against every item."""
    steps = 0
    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                steps += 1
    return steps


COLUMNS = [
    ("const", count_constant),
    ("log n", count_log),
    ("n", count_linear),
    ("n log n", count_nlogn),
    ("n^2", count_quadratic),
    ("n^3", count_cubic),
]

header = f"{'n':>6}  " + "  ".join(f"{name:>9}" for name, _ in COLUMNS)
print(header)
print("-" * len(header))
for n in (1, 2, 4, 8, 16, 32, 64, 128, 256):
    row = [fn(n) for _, fn in COLUMNS]
    print(f"{n:>6}  " + "  ".join(f"{v:>9}" for v in row))

print()
print("The numbers are exact and reproducible: nothing here depends on")
print("the machine, the clock, or the interpreter. Counting is the first")
print("tool, and the one you should reach for before timing anything.")
