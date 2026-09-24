#!/usr/bin/env python3
"""Chapter 44 demo 11 -- the same statement, one extra reference, O(n^2).

The previous block counted the two policies. This one asks which policy each
of two loops gets, and the answer is decided by something outside the loop:
whether anything else still refers to the string being appended to.
"""

PIECE = "ab"


def characters_written(n, copy_each_time):
    written = 0
    length = 0
    for _ in range(n):
        if copy_each_time:
            written += length
        written += len(PIECE)
        length += len(PIECE)
    return written


def policy(n, keeps_the_old_string):
    """A string with one reference can be resized in place. A string that is
    also held somewhere else cannot, because that other name would change
    underneath its owner -- so the interpreter allocates and copies."""
    return characters_written(n, copy_each_time=keeps_the_old_string)


SIZES = (1_000, 2_000, 4_000, 8_000)
tight = [policy(n, False) for n in SIZES]
kept = [policy(n, True) for n in SIZES]

print("two loops. The string-building line is identical in both.")
print("One of them also keeps the previous value in a list.")
print()
print(f"{'n':>7}  {'tight loop':>13}  {'old string kept':>16}{'ratio':>12}")
print("-" * 52)
for index, n in enumerate(SIZES):
    print(f"{n:>7}  {tight[index]:>13,}  {kept[index]:>16,}"
          f"{kept[index] / tight[index]:>11.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes counted':<46}{len(SIZES):>8}")
print(f"{'characters written, tight, largest n':<46}{tight[-1]:>8}")
print(f"{'characters written, kept, largest n':<46}{kept[-1]:>8}")
print(f"{'on doubling n, tight':<46}{tight[-1] / tight[-2]:>8.1f}")
print(f"{'on doubling n, kept':<46}{kept[-1] / kept[-2]:>8.1f}")
print(f"{'the ratio doubles with every doubling of n':<46}"
      f"{(kept[-1] / tight[-1]) / (kept[0] / tight[0]):>8.1f}")

print()
print("At the smallest size the two are already a long way apart, and the")
print("ratio itself doubles every time n does -- which is what 'the gap grows")
print("without limit' means in arithmetic rather than in a screenshot.")
print()
print("The lesson is not about strings. It is that a complexity claim is a")
print("claim about a program, not about a syntax. `s += t` is linear in one")
print("loop and quadratic in another, and the difference is not visible in the")
print("line of code -- it is visible in whether anything else holds a")
print("reference to the object. That is a property of the surrounding program,")
print("which is exactly why the advice is worth checking rather than quoting.")
