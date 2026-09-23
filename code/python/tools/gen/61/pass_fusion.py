"""Chapter 61 -- what a vectorised kernel actually saves: passes.

Six transformations over a hundred thousand values, done three ways: one pass
per transformation, one pass per transformation that rebuilds the container,
and one pass that does all six together. The count is of reads and writes to
the container, and the result is that rewriting a loop as a comprehension
changes nothing at all -- fusing the passes is the only one of the three that
removes work.
"""

VALUES = 100000
STEPS = 6


def separate(data, steps):
    """One pass per transformation, each writing back to the same container."""
    reads = 0
    writes = 0
    for _step in range(steps):
        for index in range(len(data)):
            reads += 1
            data[index] = (data[index] * 2 + 1) % 1000
            writes += 1
    return reads + writes, 0


def rebuilt(data, steps):
    """One pass per transformation, each building a new container."""
    reads = 0
    writes = 0
    containers = 1
    for _step in range(steps):
        out = []
        containers += 1
        for value in data:
            reads += 1
            out.append((value * 2 + 1) % 1000)
            writes += 1
        data = out
    return reads + writes, containers


def fused(data, steps):
    """One pass, every transformation applied inside it."""
    reads = 0
    writes = 0
    for index in range(len(data)):
        reads += 1
        value = data[index]
        for _step in range(steps):
            value = (value * 2 + 1) % 1000
        data[index] = value
        writes += 1
    return reads + writes, 0


print(f"{VALUES:,} values, up to {STEPS} transformations, counting reads and writes")
print()
print(f"{'steps':>6}{'one pass each':>15}{'rebuilt each time':>19}{'one fused pass':>16}"
      f"{'ratio':>8}")
print("-" * 64)
for steps in range(1, STEPS + 1):
    base = list(range(VALUES))
    ops_separate, _ = separate(list(base), steps)
    ops_rebuilt, containers = rebuilt(list(base), steps)
    ops_fused, _ = fused(list(base), steps)
    print(f"{steps:>6}{ops_separate:>15,}{ops_rebuilt:>19,}{ops_fused:>16,}"
          f"{ops_separate / ops_fused:>8.1f}")

base = list(range(VALUES))
_, containers = rebuilt(list(base), STEPS)

print()
print(f"At six transformations the separate version makes {6 * 2 * VALUES:,} reads and")
print(f"writes and the fused version makes {2 * VALUES:,} -- the same number it makes")
print("for one transformation, because the count is two operations per value")
print("however much arithmetic happens inside the pass. What differs between")
print("the two is how many times the container is walked.")
print()
print(f"The rebuilt version makes the same number of reads and writes as the")
print(f"separate one and allocates {containers} containers instead of one, so rewriting")
print("the loop as a comprehension is not an optimisation -- it moves the same")
print("amount of data and adds an allocation per pass. Fusing the passes is the")
print("change that removes work, and it is the only one of the three that does.")
