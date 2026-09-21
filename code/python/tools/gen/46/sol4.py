#!/usr/bin/env python3
"""Chapter 46 solution 4 -- grouping with a sort, and the trap in groupby."""
import itertools

EVENTS = [
    ("eng", "ada"),
    ("ops", "bob"),
    ("eng", "cyd"),
    ("ops", "dee"),
    ("eng", "eve"),
    ("ops", "fay"),
    ("eng", "gus"),
]


def groupby_as_is(rows, key):
    """`groupby` collapses *adjacent* equal keys. Given the rows in arrival
    order it returns runs, not groups -- and nothing about the call says so."""
    return [(value, [row[1] for row in group])
            for value, group in itertools.groupby(rows, key=key)]


def grouped(rows, key):
    """The sort is not an optimisation here -- it is what makes the grouping
    correct, because it puts equal keys next to each other."""
    ordered = sorted(rows, key=key)
    return [(value, [row[1] for row in group])
            for value, group in itertools.groupby(ordered, key=key)]


def department(row):
    return row[0]


print(f"events in arrival order: {[row[1] for row in EVENTS]}")
print(f"departments, as they arrive: {[row[0] for row in EVENTS]}")
print()
print("grouping without sorting first -- groupby_as_is(EVENTS, department)")
as_is = groupby_as_is(EVENTS, department)
for value, members in as_is:
    print(f"  {value}: {members}")
print(f"  -> {len(as_is)} 'groups', and "
      f"{sum(1 for value, _ in as_is if value == 'eng')} of them are eng")
print()
print("grouping after sorting by the group key -- grouped(EVENTS, department)")
after = grouped(EVENTS, department)
for value, members in after:
    print(f"  {value}: {members}")
print(f"  -> {len(after)} groups, one per department")
print()
print(f"same answer? {as_is == after}")
print()
print("`itertools.groupby` does not group a sequence. It splits a sequence")
print("into runs of adjacent equal keys, which is a different operation and")
print("a cheaper one -- it never has to hold more than one group in memory.")
print("The name is the whole problem: nothing in the call site says the input")
print("must be sorted, so the unsorted call returns a plausible answer.")
print()
print("Notice that the *members* come back in arrival order, not sorted")
print("order, inside each group. The sort moved whole groups around; the")
print("stable tie-break left the items within a group where they were. So")
print("'sort by the group key, then keep arrival order inside each group' is")
print("what this pair of operations does, and it is exactly what you want")
print("for a report.")
print()
print("The same shape answers 'deduplicate adjacent' and 'find runs':")
print()
RUNS = [1, 1, 2, 2, 2, 5, 1, 1]
print(f"  input runs : {RUNS}")
print(f"  runs       : {[(value, len(list(group))) for value, group in itertools.groupby(RUNS)]}")
print()
print("Two runs of 1, because they are not adjacent -- which is correct for")
print("'find runs' and a bug for 'count occurrences'. The fix is the same in")
print("both cases: decide whether you want runs or groups, and if you want")
print("groups, sort first or reach for a dict.")
print()
counts = {}
for value in RUNS:
    counts[value] = counts.get(value, 0) + 1
print(f"  a dict instead, for counts: {counts}")
print()
print("The dict is O(n) and the sort is O(n log n), so for counting alone")
print("the dict wins. The sort earns its keep when you need the groups in a")
print("specific *order* -- by name, by size, by earliest member -- because")
print("then the ordering is the output, and a dict has no order to give you.")
