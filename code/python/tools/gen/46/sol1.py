#!/usr/bin/env python3
"""Chapter 46 solution 1 -- a three-key sort, two ways, and the wrong way."""
ROWS = [
    ("eve", 91, "eng"),
    ("bob", 78, "ops"),
    ("hal", 91, "ops"),
    ("dee", 78, "eng"),
    ("ada", 91, "eng"),
    ("fay", 65, "ops"),
    ("gus", 78, "ops"),
    ("cyd", 91, "eng"),
]


def by_tuple(rows):
    """One pass. The key is a tuple, so Python compares dept first, then
    -score, then name -- and stops at whichever field differs."""
    return sorted(rows, key=lambda row: (row[2], -row[1], row[0]))


def by_passes(rows):
    """Three passes, least significant key first. Each pass is stable, so
    the order each one establishes survives inside the groups the next one
    creates."""
    ordered = sorted(rows, key=lambda row: row[0])              # name
    ordered = sorted(ordered, key=lambda row: row[1], reverse=True)  # score
    ordered = sorted(ordered, key=lambda row: row[2])           # dept
    return ordered


def by_passes_wrong_order(rows):
    """The same three passes, applied most-significant first."""
    ordered = sorted(rows, key=lambda row: row[2])              # dept
    ordered = sorted(ordered, key=lambda row: row[1], reverse=True)  # score
    ordered = sorted(ordered, key=lambda row: row[0])           # name
    return ordered


def show(label, rows):
    print(f"  {label}")
    for name, points, dept in rows:
        print(f"    {dept:<5}{name:<5}{points:>4}")
    print()


tuple_result = by_tuple(ROWS)
passes_result = by_passes(ROWS)
wrong_result = by_passes_wrong_order(ROWS)

print("sort by department, then by score descending, then by name")
print()
show("key=lambda row: (row[2], -row[1], row[0])", tuple_result)
print(f"  the three-pass version agrees: {tuple_result == passes_result}")
print()
show("the three passes in the wrong order", wrong_result)
print(f"  and that one agrees: {tuple_result == wrong_result}")
print()
print("The tuple key is one expression and one pass. The three-pass version")
print("is three sorts -- three times the work, since each pass is n log n --")
print("and it is correct only if the passes are in the right order.")
print()
print("It is still worth knowing, for two reasons. The first is that a key")
print("must be orderable as a tuple, and mixing directions inside one is")
print("only possible by negating: `-row[1]` works because the score is a")
print("number. There is no negation for a string, so 'department ascending")
print("and name descending' cannot be written as a tuple key at all -- and")
print("then the passes are the only way.")
print()
print("The second reason is that the wrong-order version is not obviously")
print("wrong. All three keys are used, every pass is stable, and the output")
print("is sorted by name. It has simply lost the two keys that mattered.")
print()
print("If you do write the passes, write them in one place with the keys in")
print("a list, least significant first, so the order is visible:")
print()
KEYS = [("name", lambda row: row[0], False),
        ("score", lambda row: row[1], True),
        ("dept", lambda row: row[2], False)]
ordered = list(ROWS)
for label, key, descending in KEYS:
    ordered.sort(key=key, reverse=descending)
    print(f"    after sorting by {label:<6} (descending={descending}): "
          f"{[row[0] for row in ordered]}")
print()
print(f"  agrees with the tuple key: {ordered == tuple_result}")
