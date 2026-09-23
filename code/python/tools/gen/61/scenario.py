"""Chapter 61 -- the scenario. A data pipeline that runs once a night.

A hundred thousand rows through four stages: a filter, a transform, a group
and a join. Two orderings of the same four stages, and the count is of
element visits per stage -- keyed by the stage, so the two orderings are
compared stage against stage rather than position against position.
"""

ROWS = 100000
KEEP = 1000
GROUPS = 1000
DIMENSION = 1000
ORDER = ["filter", "transform", "group", "join"]


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


def source():
    """Rows with a group key, a value, and whether the filter keeps them."""
    return [(mix(3 + index) % GROUPS, index % 97, index % (ROWS // KEEP) == 0)
            for index in range(ROWS)]


def dimension():
    return [(key, f"group-{key:04d}") for key in range(DIMENSION)]


def transform_first(data, dim):
    """Transform everything, then filter, then group and join the slow way."""
    visits = {}

    count = 0
    transformed = []
    for group, value, keep in data:
        count += 1
        transformed.append((group, value * 2 + 1, keep))
    visits["transform"] = count

    count = 0
    kept = []
    for group, value, keep in transformed:
        count += 1
        if keep:
            kept.append((group, value))
    visits["filter"] = count

    count = 0
    totals = {}
    for group in range(GROUPS):
        total = 0
        for other, value in kept:
            count += 1
            if other == group:
                total += value
        if total:
            totals[group] = total
    visits["group"] = count

    count = 0
    joined = 0
    for group, value in kept:
        for key, _name in dim:
            count += 1
            if key == group:
                joined += value
    visits["join"] = count
    return visits, totals, joined


def filter_first(data, dim):
    """Filter, then transform the survivors, then group and join in one pass."""
    visits = {}

    count = 0
    kept = []
    for group, value, keep in data:
        count += 1
        if keep:
            kept.append((group, value))
    visits["filter"] = count

    count = 0
    transformed = []
    for group, value in kept:
        count += 1
        transformed.append((group, value * 2 + 1))
    visits["transform"] = count

    count = 0
    totals = {}
    for group, value in transformed:
        count += 1
        totals[group] = totals.get(group, 0) + value
    visits["group"] = count

    count = 0
    table = {}
    for key, name in dim:
        count += 1
        table[key] = name
    joined = 0
    for group, value in transformed:
        count += 1
        if group in table:
            joined += value
    visits["join"] = count
    return visits, totals, joined


data = source()
dim = dimension()
before, totals_before, joined_before = transform_first(data, dim)
after, totals_after, joined_after = filter_first(data, dim)

if totals_before != totals_after or joined_before != joined_after:
    raise SystemExit("the two pipelines disagreed about the answer")

print(f"{ROWS:,} rows, {KEEP:,} survive the filter, {GROUPS:,} groups, "
      f"{DIMENSION:,} dimension rows")
print()
print(f"{'stage':<14}{'before':>12}{'after':>12}{'removed':>12}")
print("-" * 50)
total_before = 0
total_after = 0
for stage in ORDER:
    total_before += before[stage]
    total_after += after[stage]
    print(f"{stage:<14}{before[stage]:>12,}{after[stage]:>12,}"
          f"{before[stage] - after[stage]:>12,}")
print("-" * 50)
print(f"{'total':<14}{total_before:>12,}{total_after:>12,}"
      f"{total_before - total_after:>12,}")

grouped = before["group"] + before["join"]

print()
print("Both pipelines produce the same totals and the same join, and the first")
print(f"one visits {total_before / total_after:.1f} times as many elements as the second.")
print()
print(f"The group and the join are {grouped:,} of the {total_before:,} visits, which is")
print(f"{grouped / total_before:.1%} of the pipeline. The transform -- the stage people optimise")
print(f"first, because it is the one with the arithmetic in it -- is")
print(f"{before['transform']:,} of the {total_before:,}, which is {before['transform'] / total_before:.1%}.")
print()
print("The two stages that cost the most are the two that walk the data once")
print("per key. Both of them are one line each to replace with a single pass")
print("over a dictionary, and neither of them is a change to the arithmetic.")
print()
print("Notice that the filter costs the same in both orderings, and that the")
print("transform goes from a hundred thousand visits to a thousand. That is")
print("the whole difference between the two pipelines at that stage, and it is")
print("invisible in the stage's own output.")
