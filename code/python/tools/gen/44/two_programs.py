#!/usr/bin/env python3
"""Chapter 44 demo 1 -- two programs, one answer, very different cost."""
import timeit

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


def scan_each():
    return [in_list(q) for q in QUERIES]


def hash_each():
    return [in_set(q) for q in QUERIES]


def best(fn, number, repeat=7):
    return min(timeit.repeat(fn, number=number, repeat=repeat))


def magnitude(ratio):
    """Coarse bands: the third significant figure is noise, not evidence."""
    for edge, label in ((5, "~2x"), (20, "~10x"), (60, "~30x"), (400, "~100x")):
        if ratio < edge:
            return label
    return "~1000x or more"


scan_answers = [ok for ok, _ in scan_each()]
set_answers = [ok for ok, _ in hash_each()]
worst_comparisons = max(c for _, c in scan_each())

print(f"the same {len(QUERIES)} questions, asked two ways")
print("both give identical answers:", scan_answers == set_answers)
print()
print("  scanning the list")
print(f"    worst case per question : {worst_comparisons} comparisons")
print(f"    total for this run      : {sum(c for _, c in scan_each())} comparisons")
print("  asking the set")
print("    per question            : 1 hash, whatever the size")
print()
t_list = best(scan_each, 20)
t_set = best(hash_each, 20)
print(f"  measured cost of the list version : {magnitude(t_list / t_set)} the set version")
print()
print("Nothing about the answers changed. Only the cost did.")
print()
print("The list version's cost is proportional to the number of members.")
print("The set version's cost is not. Add a million more members and the")
print("first gets a million times worse while the second does not move.")
print("That difference is a growth rate, and no amount of tuning the")
print("constant factor will close it.")
