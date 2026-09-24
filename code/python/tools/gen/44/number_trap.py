#!/usr/bin/env python3
"""Chapter 44 demo 13 -- the benchmark that measured my own typo.

The trap is not the stopwatch, it is the comparison. Two builders are run a
different number of times, and the totals are compared as if they were the
same kind of number. Counting reproduces the mistake exactly -- and unlike a
timing table, it reproduces it the same way every time.
"""

N = 2_000
PLUS_RUNS = 3        # <- one number of runs for this builder
JOIN_RUNS = 50       # <- and a completely different one for that builder


def plus_equals(n):
    """Build the string with +=, and count the appends it performs."""
    s = ""
    operations = 0
    for _ in range(n):
        s += "ab"
        operations += 1
    return operations


def join_literal_list(n):
    """Build a list and join it, and count the items it appends."""
    pieces = []
    operations = 0
    for _ in range(n):
        pieces.append("ab")
        operations += 1
    "".join(pieces)
    return operations


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


per_run_plus = plus_equals(N)
per_run_join = join_literal_list(N)
total_plus = per_run_plus * PLUS_RUNS
total_join = per_run_join * JOIN_RUNS

print(f"n = {N}. Two builders, each run a different number of times.")
print()
print("I picked the number of runs so each measurement took about the same")
print("wall-clock time. That is a sensible thing to do, and it is the trap:")
print()
print(f"  s +=        {PLUS_RUNS:>3} runs per measurement")
print(f"  join        {JOIN_RUNS:>3} runs per measurement")
print()
print("Comparing the totals the runs produced:")
print(f"  s += is {factor(total_join / total_plus)} faster")
print()
print("Comparing the cost of one run -- which is the only fair comparison:")
print(f"  the two are {factor((total_plus / PLUS_RUNS) / (total_join / JOIN_RUNS))}")
print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'operations per run, s +=':<46}{per_run_plus:>8}")
print(f"{'operations per run, join':<46}{per_run_join:>8}")
print(f"{'runs per measurement, s +=':<46}{PLUS_RUNS:>8}")
print(f"{'runs per measurement, join':<46}{JOIN_RUNS:>8}")
print(f"{'operations in the s += total':<46}{total_plus:>8}")
print(f"{'operations in the join total':<46}{total_join:>8}")
print(f"{'ratio of the totals, rounded':<46}"
      f"{round(total_join / total_plus):>8}")
print(f"{'ratio of one run to one run':<46}"
      f"{round(per_run_join / per_run_plus):>8}")

print()
print("The same two runs, and the two readings disagree about which builder")
print("wins. Only the second is a fact about the code. The first is a fact")
print("about my choice of how many times to run each one, which is not a")
print("property of the program at all.")
print()
print(f"The arithmetic is worth seeing plainly: each builder does {per_run_plus} operations")
print(f"per run, so the totals differ only because one was run {JOIN_RUNS // PLUS_RUNS} times more")
print("often. Dividing by the runs is not a refinement of the comparison, it")
print("is the comparison.")
print()
print("This is why the block prints counts. A timing table here would carry")
print("the same lesson and a different set of numbers every time you opened")
print("the book, and the reader would have no way to tell which of the two")
print("columns was the mistake.")
