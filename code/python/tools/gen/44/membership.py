#!/usr/bin/env python3
"""Chapter 44 demo 7 -- the same question, asked of a list and a set."""
import sys
import timeit


def magnitude(ratio):
    for edge, label in ((5, "~2x"), (20, "~10x"), (60, "~30x"), (400, "~100x")):
        if ratio < edge:
            return label
    return "1000x+"


def best(stmt, number, repeat=7, globs=None):
    return min(timeit.repeat(stmt, number=number, repeat=repeat, globals=globs))


print("is the last item in this collection?  n grows, the answer does not")
print()
print(f"{'n':>7}  {'list':>10}  {'set':>10}")
print("-" * 32)
for n in (4, 16, 64, 256, 4_096):
    g = {"lst": list(range(n)), "st": set(range(n)), "n": n}
    t_list = best("n - 1 in lst", 2_000, globs=g)
    t_set = best("n - 1 in st", 2_000, globs=g)
    print(f"{n:>7}  {magnitude(t_list / t_set):>10}  {'1x':>10}")

print()
print("The set column is flat. It does not care how big it is, because")
print("hashing the value is one operation and the lookup is one operation.")
print()
print("The list column is not flat. At n=4 the set is only about twice as")
print("fast -- a constant factor, the kind you can argue about. By n=4096")
print("the gap is three orders of magnitude, and it keeps going. That is")
print("not a constant factor any more; it is a different curve.")
print()
print("This is the test to apply to any two approaches: double the input")
print("and measure again. If the gap stays the same size it is a constant.")
print("If the gap grows, you are looking at two different complexities.")
