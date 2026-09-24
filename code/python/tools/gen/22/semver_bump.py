"""Chapter 22 -- what version number a set of changes forces.

Six releases described by what they changed, each scored against the rules of
semantic versioning and applied to a starting version. The count is of releases
that force a major bump, which is the one people avoid by accident.
"""

START = (1, 4, 7)

RULES = {
    "breaking": "major",
    "feature": "minor",
    "fix": "patch",
    "docs": "patch",
}

RELEASES = [
    ("added a --json flag", ["feature"]),
    ("fixed a typo in the help text", ["docs"]),
    ("renamed a public function", ["breaking"]),
    ("fixed a crash and added a flag", ["fix", "feature"]),
    ("removed a parameter and fixed a bug", ["breaking", "fix"]),
    ("sped up the parser", ["fix"]),
]

ORDER = {"patch": 0, "minor": 1, "major": 2}


def bump(changes):
    """The largest bump any single change forces -- not a sum, not an average."""
    biggest = max(changes, key=lambda kind: ORDER[RULES[kind]])
    return RULES[biggest]


def next_version(kind):
    major, minor, patch = START
    if kind == "major":
        return (major + 1, 0, 0)
    if kind == "minor":
        return (major, minor + 1, 0)
    return (major, minor, patch + 1)


rows = []
for label, changes in RELEASES:
    kind = bump(changes)
    rows.append((label, len(changes), kind, ".".join(str(n) for n in next_version(kind))))

print(f"six releases, each starting from {'.'.join(str(n) for n in START)}")
print()
print(f"{'release':<40}{'changes':>8}{'bump':>8}{'next version':>15}")
print("-" * 71)
for label, count, kind, version in rows:
    print(f"{label:<40}{count:>8}{kind:>8}{version:>15}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'releases described':<46}{len(rows):>8}")
print(f"{'changes across all of them':<46}{sum(r[1] for r in rows):>8}")
for kind in ("major", "minor", "patch"):
    print(f"{'releases that force a ' + kind + ' bump':<46}"
          f"{sum(1 for r in rows if r[2] == kind):>8}")

print()
print("The bump is a maximum, not a sum, and not an average. A release with one")
print("breaking change and one bug fix is a major release: the fix does not")
print("dilute it, and the two changes do not average out to a minor one. That")
print("is the whole rule, and it is the one that gets skipped -- because the")
print("person cutting the release remembers the fix they just made.")
print()
print("The two releases with more than one change are the ones to look at.")
print("Each of them contains a fix, and neither of them is a patch release,")
print("because the largest thing in the list sets the number. Read the list,")
print("not the last entry.")
print()
print("What the number is for is the reader of the dependency. A caret range")
print("in a manifest is a promise that the next release will not break the")
print("caller, and that promise is only worth what the bump rule is worth. A")
print("maintainer who ships a rename as 1.4.8 has not made a small mistake;")
print("they have made every caret range in every downstream project wrong at")
print("once, silently, at install time.")
