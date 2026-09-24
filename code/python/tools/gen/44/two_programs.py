#!/usr/bin/env python3
"""Chapter 44 demo 1 -- two programs, one answer, very different cost.

The comparison count is exact. in_list stops at the first match, so the
number of comparisons a query costs is a property of the data, not of the
machine, the load, or the interpreter build. That is what makes it the kind
of number a book can print.
"""

MEMBERS = [f"user{i}" for i in range(10_000)]
MEMBERS_SET = set(MEMBERS)
QUERIES = [f"user{i}" for i in range(0, 10_000, 97)] + ["nobody"]


def in_list(name):
    """Compare the name against every entry, in order."""
    comparisons = 0
    for member in MEMBERS:
        comparisons += 1
        if member == name:
            return True, comparisons
    return False, comparisons


def in_set(name):
    """Hash the name once and look in one bucket."""
    return name in MEMBERS_SET, 1


list_results = [in_list(q) for q in QUERIES]
set_results = [in_set(q) for q in QUERIES]

list_answers = [ok for ok, _ in list_results]
set_answers = [ok for ok, _ in set_results]
worst = max(c for _, c in list_results)
total = sum(c for _, c in list_results)
lookups = len(QUERIES)

print(f"the same {lookups} questions, asked two ways")
print("both give identical answers:", list_answers == set_answers)
print()
print("  scanning the list")
print(f"    worst case per question : {worst:,} comparisons")
print(f"    total for this run      : {total:,} comparisons")
print("  asking the set")
print("    per question            : 1 hash, 1 comparison, whatever the size")
print()
print(f"  the list version did  {total:>9,} comparisons")
print(f"  the set version did   {lookups:>9,} lookups")
print(f"  ratio                 {total / lookups:>9,.0f}x")
print()
print("Nothing about the answers changed. Only the cost did.")
print()
print("The list version's cost is proportional to the number of members.")
print("The set version's cost is not. Add a million more members and the")
print("first gets a million times worse while the second does not move.")
print("That difference is a growth rate, and no amount of tuning the")
print("constant factor will close it.")
