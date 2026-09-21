#!/usr/bin/env python3
"""Chapter 44 demo 13 -- the benchmark that measured my own typo."""
import timeit


def plus_equals(n):
    s = ""
    for _ in range(n):
        s += "ab"
    return s


def join_literal_list(n):
    return "".join(["ab"] * n)


def factor(ratio):
    if ratio < 1.3:
        return "about the same"
    if ratio < 3.0:
        return "about 2x"
    if ratio < 5.0:
        return "about 4x"
    if ratio < 15.0:
        return "about 9x"
    return "more than 15x"


N = 2_000
PLUS_RUNS = 3        # <- one number of runs for this builder
JOIN_RUNS = 50       # <- and a completely different one for that builder

totals_plus = min(timeit.repeat(lambda: plus_equals(N), number=PLUS_RUNS, repeat=7))
totals_join = min(timeit.repeat(lambda: join_literal_list(N), number=JOIN_RUNS, repeat=7))

print(f"n = {N}. Two builders, both measured with timeit.")
print()
print("I picked the number of runs so each measurement took about the same")
print("wall-clock time. That is a sensible thing to do, and it is the trap:")
print()
print(f"  s +=        {PLUS_RUNS:>3} runs per measurement")
print(f"  join        {JOIN_RUNS:>3} runs per measurement")
print()
print("Comparing the numbers timeit handed back:")
print(f"  s += is {factor(totals_join / totals_plus)} faster")
print()
print("Comparing the cost of one run -- which is the only fair comparison:")
print(f"  join is {factor((totals_plus / PLUS_RUNS) / (totals_join / JOIN_RUNS))} faster")
print()
print("The same two measurements, and the two readings disagree about which")
print("builder wins. Only the second is a fact about the code. The first is")
print("a fact about my choice of `number`, which is not a property of the")
print("program at all.")
print()
print("Every number in this chapter was produced by dividing a measured")
print("total by the number of runs inside it. Do that division before you")
print("compare anything, and be suspicious of any timing table -- including")
print("one in a book -- where you cannot see what the runs were.")
