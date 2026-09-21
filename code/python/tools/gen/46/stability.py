#!/usr/bin/env python3
"""Chapter 46 demo -- stability, and the one-line way to lose it.

A sort is stable if items that compare equal come out in the order they went
in. Python guarantees this for `sorted` and `list.sort`, and the guarantee is
what makes multi-key sorting work without tuple keys.
"""
RECORDS = [
    ("eve", 91),
    ("bob", 78),
    ("hal", 91),
    ("dee", 78),
    ("ada", 91),
    ("fay", 65),
    ("gus", 78),
    ("cyd", 91),
]


def score(record):
    return record[1]


def names(records):
    return [name for name, _ in records]


def show(label, records):
    print(f"  {label:<38}{names(records)}")


print("the input, in the order it arrived")
show("as given", RECORDS)
print()
print("sorting by score, highest first")
print()
show("key=score, reverse=True", sorted(RECORDS, key=score, reverse=True))
show("key=score, then [::-1]", sorted(RECORDS, key=score)[::-1])
print()
print("Both produce a list in descending score order, and they are not the")
print("same list. The four 91s come out eve, hal, ada, cyd in the first --")
print("their order of arrival -- and cyd, ada, hal, eve in the second,")
print("which is exactly reversed.")
print()
print("`reverse=True` reverses the *comparison*, so equal items are still")
print("compared as equal and the stable tie-break survives. Slicing with")
print("[::-1] reverses the *result*, so it reverses the ties too. This is")
print("the most common way to lose stability, and it looks like a harmless")
print("rewrite of the line above it.")
print()
print("The guarantee is worth having because it replaces tuple keys for")
print("multi-key sorts. To sort by score and then by name, sort by the")
print("*secondary* key first and the primary key second:")
print()
first_pass = sorted(RECORDS, key=lambda record: record[0])
show("sorted by name", first_pass)
second_pass = sorted(first_pass, key=score, reverse=True)
show("then by score, reverse=True", second_pass)
print()
print("Compare the 91s in that last line with the 91s from the single stable")
print("sort above it. The two-pass version gives ada, cyd, eve, hal -- name")
print("order -- where the single pass gave arrival order. Each pass is")
print("stable, so the name order established in the first pass survives")
print("inside every group of equal scores.")
print()
print("The tuple-key version `key=lambda r: (-r[1], r[0])` gets the same")
print("answer in one pass and is usually the better code -- but it only")
print("works when the keys are orderable, and the two-pass version works")
print("when they are not.")
print()
print("A stable sort is also what makes 'group by' expressible without a")
print("dict. Sort by the group key and the groups come out contiguous and")
print("internally in arrival order:")
print()
by_score = sorted(RECORDS, key=score, reverse=True)
runs = []
for record in by_score:
    if not runs or runs[-1][0] != record[1]:
        runs.append((record[1], []))
    runs[-1][1].append(record[0])
for value, group in runs:
    print(f"  score {value}: {group}")
