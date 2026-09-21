#!/usr/bin/env python3
"""Chapter 44 demo 15 -- the scenario: a dedupe that was fine until it wasn't."""
import timeit


def make_rows(n):
    """n rows, about a tenth of them repeats."""
    return [f"row-{i % (n * 9 // 10)}" for i in range(n)]


def dedupe_by_list(rows):
    """Is this row already in the output? Scan the output to find out."""
    out = []
    for row in rows:
        if row not in out:          # O(len(out)) -- a scan, every time
            out.append(row)
    return out


def dedupe_by_set(rows):
    """The same question, asked of a set instead."""
    seen = set()
    out = []
    for row in rows:
        if row not in seen:         # O(1)
            seen.add(row)
            out.append(row)
    return out


def band(ratio):
    if ratio < 12.0:
        return "~10x"
    if ratio < 45.0:
        return "~25x"
    if ratio < 130.0:
        return "~80x"
    if ratio < 300.0:
        return "~200x"
    return "400x or more"


def per_call(stmt, number, globs):
    return min(timeit.repeat(stmt, number=number, repeat=5, globals=globs)) / number


print("both functions return the same list -- check it once:")
probe = make_rows(2_000)
print("  identical output:", dedupe_by_list(probe) == dedupe_by_set(probe))
print(f"  {len(probe)} rows in, {len(dedupe_by_set(probe))} rows out")
print()
print(f"{'rows':>8}  {'list version / set version':>28}")
print("-" * 40)
for n in (250, 500, 1_000, 2_000, 4_000, 8_000):
    rows = make_rows(n)
    number = max(1, 2_000 // n)
    g = {"f": dedupe_by_list, "rows": rows}
    t_list = per_call("f(rows)", number, g)
    g = {"f": dedupe_by_set, "rows": rows}
    t_set = per_call("f(rows)", number, g)
    print(f"{n:>8}  {band(t_list / t_set):>28}")

print()
print("At 250 rows the list version is already about 25 times slower -- the")
print("kind of thing that gets waved through in review as 'fine for now'.")
print("Every doubling of the input doubles that gap again, because one")
print("version is O(n) and the other is O(n^2). By 8000 rows it is four")
print("hundred times slower, and it has not finished getting worse.")
print()
print("The fix is two lines: keep a set of what you have already seen, and")
print("ask the set instead of scanning the output. The output list stays,")
print("because order matters and a set does not preserve it.")
print()
print("What makes this scenario worth reading is not the fix. It is that")
print("the function was correct, the tests passed, and the only symptom")
print("was a gap that grew. A quadratic is not a bug at any particular")
print("size -- it is a bug waiting for the input to get bigger, which is")
print("to say, waiting for you to ship it.")
