#!/usr/bin/env python3
"""Chapter 44 demo 10 -- the claim everybody repeats about string +=.

The claim is that `s += "ab"` in a loop is O(n^2). The count below is the
number of characters written, under the two policies an implementation can
choose: resize the string in place, or allocate a new one and copy.

Counting is the only way to see this. Both policies produce the same string,
so a program that prints it cannot tell you which one ran, and a stopwatch
tells you only that one is faster on the day you measured.
"""

PIECE = "ab"


def characters_written(n, copy_each_time):
    """Simulate the two policies and count every character written.

    The in-place policy writes only the new piece. The copying policy also
    rewrites everything already there, which is what makes it quadratic.
    """
    written = 0
    length = 0
    for _ in range(n):
        if copy_each_time:
            written += length
        written += len(PIECE)
        length += len(PIECE)
    return written


SIZES = (1_000, 2_000, 4_000)
in_place = [characters_written(n, False) for n in SIZES]
copying = [characters_written(n, True) for n in SIZES]

print("'building a string with += is O(n^2); use join' -- the standard advice.")
print()
print("Here is the same loop under the two policies an implementation can")
print("choose, counting every character written:")
print()
print(f"{'n':>7}  {'resize in place':>17}  {'copy each time':>16}{'ratio':>12}")
print("-" * 56)
for index, n in enumerate(SIZES):
    ratio = copying[index] / in_place[index]
    print(f"{n:>7}  {in_place[index]:>17,}  {copying[index]:>16,}{ratio:>11.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes counted':<46}{len(SIZES):>8}")
print(f"{'characters in the final string, largest n':<46}"
      f"{len(PIECE) * SIZES[-1]:>8}")
print(f"{'characters written, in place, largest n':<46}{in_place[-1]:>8}")
print(f"{'characters written, copying, largest n':<46}{copying[-1]:>8}")
print(f"{'on doubling n, in place':<46}"
      f"{in_place[-1] / in_place[-2]:>8.1f}")
print(f"{'on doubling n, copying':<46}{copying[-1] / copying[-2]:>8.1f}")
print(f"{'ratio of the two at the largest n':<46}"
      f"{copying[-1] / in_place[-1]:>8.0f}")

print()
print("The two columns are the same program written the same way, and one of")
print("them is linear while the other is quadratic. Every doubling of n")
print(f"doubles the in-place count and multiplies the copying one by about")
print(f"{copying[-1] / copying[-2]:.0f}. That factor is the whole of the folklore.")
print()
print("So the advice is not wrong, it is incomplete. CPython has a special")
print("case in its string concatenation: when the left-hand string has exactly")
print("one reference to it and no other name is looking at it, the interpreter")
print("resizes it in place instead of allocating a new one and copying. In a")
print("tight loop that is exactly the situation, so += becomes cheap and the")
print("quadratic term never appears -- which is why the block after this one")
print("changes a single line and gets the quadratic behaviour back.")
