#!/usr/bin/env python3
"""Chapter 44 demo 6 -- the real constant factors, ranked."""
import timeit


class Point:
    __slots__ = ("x",)

    def __init__(self):
        self.x = 1


P = Point()
D = {"k": 1}
LST = [1, 2, 3]
X = 3
G = {"p": P, "d": D, "lst": LST, "x": X}

OPS = [
    ("local read      x", "x"),
    ("global read     len", "len"),
    ("attribute read  p.x", "p.x"),
    ("list index      lst[0]", "lst[0]"),
    ("dict lookup     d['k']", "d['k']"),
    ("builtin call    len(lst)", "len(lst)"),
    ("isinstance      isinstance(x, int)", "isinstance(x, int)"),
    ("list build      [x, x]", "[x, x]"),
    ("method call     lst.count(1)", "lst.count(1)"),
    ("dict build      {'a': x}", "{'a': x}"),
    ("set build       {x, 1}", "{x, 1}"),
    ("f-string        f'{x}'", "f'{x}'"),
]

NUMBER = 500_000
ROUNDS = 7


def multiple(ratio):
    """Deliberately coarse. The exact value is noise; the order is not."""
    if ratio < 1.6:
        return "1x"
    if ratio < 2.5:
        return "2x"
    if ratio < 3.5:
        return "3x"
    if ratio < 5.5:
        return "4x"
    if ratio < 7.0:
        return "6x"
    return "10x or more"


def measure():
    """Interleave the operations, round by round, and keep the fastest
    reading of each. Measuring all of one operation and then all of the
    next would let the machine drift between them; alternating spreads
    any drift across every row equally."""
    base = float("inf")
    bests = {label: float("inf") for label, _ in OPS}
    for _ in range(ROUNDS):
        base = min(base, timeit.timeit("x", number=NUMBER, globals=G))
        for label, stmt in OPS:
            bests[label] = min(bests[label],
                               timeit.timeit(stmt, number=NUMBER, globals=G))
    return base, bests


base, bests = measure()

print("every operation below costs about the same, in the same loop,")
print("measured against a bare local-variable read.")
print()
print(f"{'operation':<36}{'cost':>14}")
print("-" * 50)
for label, _ in OPS:
    print(f"{label:<36}{multiple(bests[label] / base):>14}")

print()
print("The spread from the cheapest row to the dearest is roughly sixfold.")
print("Everything in that range is 'one thing', which is why a program that")
print("does the same number of things twice as fast is not interesting, and")
print("a program that does a million times more things is.")
