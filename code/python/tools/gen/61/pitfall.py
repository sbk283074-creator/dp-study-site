"""Chapter 61 -- the pitfall: transforming rows the filter was about to remove.

Two orders for the same two steps, and the count is of element visits. Doing
the filter first is the largest single saving in this chapter, and the second
table is the case where the reordering is not allowed at all -- with the
counts that show the answer changed.
"""

ROWS = 1000000
STEPS = 6
KEEP_EVERY = 10


def transform_then_filter(data, steps):
    """Transform every row, then throw nine of every ten away."""
    visits = 0
    current = data
    for _step in range(steps):
        out = []
        for region, value in current:
            visits += 1
            out.append((region, value * 2 + 1))
        current = out
    kept = 0
    for region, _value in current:
        visits += 1
        if region < KEEP_EVERY:
            kept += 1
    return kept, visits


def filter_then_transform(data, steps):
    """Throw nine of every ten away, then transform what is left."""
    visits = 0
    survivors = []
    for region, value in data:
        visits += 1
        if region < KEEP_EVERY:
            survivors.append((region, value))
    current = survivors
    for _step in range(steps):
        out = []
        for region, value in current:
            visits += 1
            out.append((region, value * 2 + 1))
        current = out
    return len(current), visits


data = [(index % 100, index % 97) for index in range(ROWS)]

print(f"{ROWS:,} rows, a filter keeping one row in {100 // KEEP_EVERY}")
print()
print(f"{'steps':>6}{'transform first':>18}{'filter first':>15}{'ratio':>9}")
print("-" * 48)
for steps in range(1, STEPS + 1):
    kept_a, visits_a = transform_then_filter(data, steps)
    kept_b, visits_b = filter_then_transform(data, steps)
    if kept_a != kept_b:
        raise SystemExit("the two orders kept different rows")
    print(f"{steps:>6}{visits_a:>18,}{visits_b:>15,}{visits_a / visits_b:>9.1f}")

print()
print(f"Both orders keep the same {kept_a:,} rows and produce the same values, and")
print(f"at six steps the first one visits {visits_a / visits_b:.1f} times as many elements.")
print("The filter is not an optimisation to add after the pipeline works. It")
print("is a decision about where the pipeline starts, and how much it is worth")
print("depends on what it is moved in front of: here the transform is six")
print("passes over every row, so moving the filter ahead of it removes five")
print("sixths of the work. In the scenario at the end of this chapter the")
print("transform is a single pass and the group and the join dominate, so the")
print("same reordering is worth almost nothing. The count is the only thing")
print("that tells those two cases apart.")

print()
print("The reordering is only allowed when the transform does not change the")
print("field the filter reads. When it does, the two orders are different")
print("programs:")
print()
SMALL = 1000


def transform_first():
    """Keep rows where x * 2 < 500, transforming before the test."""
    kept = 0
    for value in range(SMALL):
        if value * 2 < 500:
            kept += 1
    return kept


def filter_first():
    """Keep rows where x < 500, then transform."""
    kept = 0
    for value in range(SMALL):
        if value < 500:
            kept += 1
    return kept


print(f"{'order':<24}{'rows kept':>12}")
print("-" * 36)
print(f"{'transform, then filter':<24}{transform_first():>12,}")
print(f"{'filter, then transform':<24}{filter_first():>12,}")
print()
print(f"The same rule applied to the same {SMALL:,} values keeps {transform_first()} rows one way")
print(f"and {filter_first()} the other, because doubling a value changes whether the")
print("filter would have kept it. Moving a filter earlier is a change to what")
print("the program means, and the only thing that tells you which of the two")
print("you have is knowing what the transform touches.")
