"""Chapter 61 -- group by, counted four ways.

Twenty thousand keys over fifty groups, grouped four ways. The count is of
items examined, and the four designs sit in three different growth classes:
one is the product of the group count and the row count, one is n log n, and
two are linear -- and the two linear ones differ in whether they hash.
"""

import array

ROWS = 20000
GROUPS = 50


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


KEYS = array.array("q", (mix(11 + index) % GROUPS for index in range(ROWS)))

# The same rows, already in key order -- as they arrive from a storage layer
# that keeps them that way. The sort that produced this order happened before
# the query, so it is not part of the count below.
ORDERED = array.array("q", sorted(KEYS))


def per_group(keys):
    """For each group, walk every row and count the matches."""
    examined = 0
    counts = []
    for group in range(GROUPS):
        found = 0
        for key in keys:
            examined += 1
            if key == group:
                found += 1
        counts.append(found)
    return sum(counts), examined


def sort_then_group(keys):
    """Put the rows in key order, then walk the order once."""
    examined = [0]

    def merge_sort(items):
        if len(items) <= 1:
            return list(items)
        middle = len(items) // 2
        left = merge_sort(items[:middle])
        right = merge_sort(items[middle:])
        out = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            examined[0] += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    ordered = merge_sort(keys)
    counts = []
    run = 0
    previous = None
    for key in ordered:
        examined[0] += 1
        if key != previous and previous is not None:
            counts.append(run)
            run = 0
        run += 1
        previous = key
    counts.append(run)
    return sum(counts), examined[0]


def one_pass(keys):
    """One walk, one hash lookup per row."""
    examined = 0
    counts = {}
    for key in keys:
        examined += 1
        counts[key] = counts.get(key, 0) + 1
    return sum(counts.values()), examined


def already_sorted(keys):
    """The rows arrive in key order, so grouping is one walk and no hashing."""
    ordered = sorted(keys)
    examined = 0
    counts = []
    run = 0
    previous = None
    for key in ordered:
        examined += 1
        if key != previous and previous is not None:
            counts.append(run)
            run = 0
        run += 1
        previous = key
    counts.append(run)
    return sum(counts), examined


DESIGNS = [
    ("a walk per group", per_group),
    ("sort, then walk", sort_then_group),
    ("one walk, hashing", one_pass),
    ("already in key order", already_sorted),
]

print(f"{ROWS:,} rows, {GROUPS} groups")
print()
print(f"{'design':<24}{'rows grouped':>14}{'items examined':>16}{'per row':>10}")
print("-" * 64)
for name, design in DESIGNS:
    grouped, examined = design(KEYS)
    if grouped != ROWS:
        raise SystemExit(f"{name} grouped {grouped} of {ROWS}")
    print(f"{name:<24}{grouped:>14,}{examined:>16,}{examined / ROWS:>10.1f}")

print()
print(f"The first design examined {GROUPS * ROWS:,} items to group {ROWS:,} rows, because it")
print("walks the whole table once for each group. That is the product of the")
print("group count and the row count, and it is the shape to recognise: it")
print("looks like a loop over groups, and the inner loop is the whole table.")
print()
print("The second design is n log n, and the third and fourth are linear. The")
print("difference between the last two is what makes the count worth taking:")
print("they examine exactly the same number of items, and one of them hashes")
print("every row while the other does not. When the rows already arrive in key")
print("order, the hash table is work you do not have to do -- and nothing in")
print("the output of the query tells you which case you are in.")
