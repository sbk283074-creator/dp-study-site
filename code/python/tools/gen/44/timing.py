#!/usr/bin/env python3
"""Chapter 44 demo 5 -- the four shapes, counted exactly.

There is no clock anywhere in this program. Every number printed is
arithmetic, so it is the same on every machine, on every run, under any
load. That is the difference between a count and a measurement, and this
chapter is about telling them apart.
"""


def steps_log(n):
    """Halve until you get to one."""
    count = 0
    while n > 1:
        n //= 2
        count += 1
    return count


def steps_linear(n):
    """One pass over n things."""
    count = 0
    for _ in range(n):
        count += 1
    return count


def steps_nlogn(n):
    """log n passes over n things."""
    count = 0
    size = 1
    while size < n:
        for _ in range(n):
            count += 1
        size *= 2
    return count


def steps_quadratic(n):
    """n passes over n things."""
    count = 0
    for _ in range(n):
        for _ in range(n):
            count += 1
    return count


# Each shape gets the largest n whose work still finishes in a moment. The
# quadratic row is the one that forces a smaller n -- which is itself the
# point of the table.
CASES = [
    ("log n", steps_log, 2 ** 18),
    ("n", steps_linear, 2 ** 18),
    ("n log n", steps_nlogn, 2 ** 18),
    ("n^2", steps_quadratic, 2 ** 10),
]

print("the ratio at a doubling is what names the class")
print()
print(f"{'shape':>8}{'n':>10}{'steps(n)':>18}{'steps(2n)':>18}{'ratio':>8}")
print("-" * 62)
ratios = {}
for name, steps, n in CASES:
    here = steps(n)
    there = steps(2 * n)
    ratios[name] = there / here
    print(f"{name:>8}{n:>10,}{here:>18,}{there:>18,}{ratios[name]:>8.2f}")

gap = ratios["n log n"] - ratios["n"]
print()
print("Every number above is arithmetic. There is no clock in this program,")
print("so the table is the same on your machine as it is on mine, and the")
print("same tomorrow as it is today.")
print()
print("The ratio column is the one that names the class: about 1 for")
print("constant, 2 for linear, 4 for quadratic. A ratio that stays the same")
print("when n doubles is the signature of the class, and it does not care")
print("how big n is or how fast the machine is.")
print()
print("Now look at the two middle rows, because they are the interesting")
print(f"pair. The linear ratio is {ratios['n']:.2f} and the n log n ratio is")
print(f"{ratios['n log n']:.2f} -- a gap of {gap:.2f}, about "
      f"{100 * gap / ratios['n']:.0f} per cent.")
print("That gap is real and it is the whole difference between the two")
print("classes: it is 2 / log2(n), so it shrinks as n grows, but it never")
print("reaches zero. It is also far smaller than the repeatability of a")
print("clock reading taken on a machine that is doing anything else, which")
print("is why a timing puts those two rows in the same bucket and a count")
print("does not.")
print()
print("So when the question is 'which class is this?', count. The count is")
print("exact, it is printable, and it settles the question. When the")
print("question is 'how many seconds will this take?', you have to time it,")
print("and the answer comes back as a band rather than a number -- because")
print("it is a fact about a machine rather than a fact about the algorithm.")
