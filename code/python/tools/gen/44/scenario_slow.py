#!/usr/bin/env python3
"""Chapter 44 demo 15 -- the scenario: a dedupe that was fine until it wasn't.

The count is of comparisons: how many times the two versions look at a value
that is already in the output. It is exact, so the growth is visible in the
table rather than argued about.
"""


def make_rows(n):
    """n rows, about a tenth of them repeats."""
    return [f"row-{i % (n * 9 // 10)}" for i in range(n)]


def dedupe_by_list(rows):
    """Is this row already in the output? Scan the output to find out."""
    out = []
    comparisons = 0
    for row in rows:
        for existing in out:
            comparisons += 1
            if existing == row:
                break
        else:
            out.append(row)
    return out, comparisons


def dedupe_by_set(rows):
    """The same question, asked of a set instead."""
    seen = set()
    out = []
    probes = 0
    for row in rows:
        probes += 1
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out, probes


SIZES = (250, 500, 1_000, 2_000, 4_000, 8_000)

probe = make_rows(2_000)
print("both functions return the same list -- check it once:")
print("  identical output:", dedupe_by_list(probe)[0] == dedupe_by_set(probe)[0])
print(f"  {len(probe)} rows in, {len(dedupe_by_set(probe)[0])} rows out")
print()
print(f"{'rows':>8}{'list: comparisons':>19}{'set: probes':>14}{'ratio':>11}")
print("-" * 52)
list_counts = []
for n in SIZES:
    rows = make_rows(n)
    _, comparisons = dedupe_by_list(rows)
    _, probes = dedupe_by_set(rows)
    list_counts.append(comparisons)
    print(f"{n:>8}{comparisons:>19,}{probes:>14,}"
          f"{comparisons / probes:>10.0f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sizes tried':<46}{len(SIZES):>8}")
print(f"{'rows at the smallest size':<46}{SIZES[0]:>8}")
print(f"{'rows at the largest size':<46}{SIZES[-1]:>8}")
print(f"{'comparisons, list, smallest':<46}{list_counts[0]:>8}")
print(f"{'comparisons, list, largest':<46}{list_counts[-1]:>8}")
print(f"{'probes, set, largest':<46}{SIZES[-1]:>8}")
print(f"{'on doubling the input, list':<46}"
      f"{list_counts[-1] / list_counts[-2]:>8.1f}")
print(f"{'on doubling the input, set':<46}{2.0:>8.1f}")
print(f"{'times more work the list does, largest':<46}"
      f"{round(list_counts[-1] / SIZES[-1]):>8}")

print()
print(f"At {SIZES[0]} rows the list version already does {round(list_counts[0] / SIZES[0])} times the work,")
print("which is the kind of thing that gets waved through in review as 'fine")
print(f"for now'. Every doubling of the input multiplies its comparisons by")
print(f"about {list_counts[-1] / list_counts[-2]:.0f} while the set's probes merely double, so the gap does")
print("not settle -- it widens without limit.")
print()
print("The fix is two lines: keep a set of what you have already seen, and ask")
print("the set instead of scanning the output. The output list stays, because")
print("order matters and a set does not preserve it.")
print()
print("What makes this scenario worth reading is not the fix. It is that the")
print("function was correct, the tests passed, and the only symptom was a gap")
print("that grew. A quadratic is not a bug at any particular size -- it is a")
print("bug waiting for the input to get bigger, which is to say, waiting for")
print("you to ship it.")
