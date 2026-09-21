#!/usr/bin/env python3
"""Chapter 46 demo -- the multi-key sort, and the three ways to get it wrong.

The requirement is 'highest score first, ties broken by earliest submission'.
Note that the rows below do *not* arrive in submission order -- which is what
makes the naive version wrong in a way nobody notices.
"""
ROWS = [
    ("hal", 91, "2026-03-05"),
    ("bob", 78, "2026-03-01"),
    ("eve", 91, "2026-03-02"),
    ("dee", 78, "2026-03-09"),
    ("cyd", 91, "2026-03-08"),
    ("fay", 65, "2026-03-04"),
    ("gus", 78, "2026-03-07"),
    ("ada", 91, "2026-03-03"),
]


def score(row):
    return row[1]


def submitted(row):
    return row[2]


def show(label, rows):
    print(f"  {label}")
    for name, points, date in rows:
        print(f"    {name:<5}{points:>4}   {date}")
    print()


print("the leaderboard requirement: highest score first, and ties broken by")
print("earliest submission")
print()
show("as the rows arrive", ROWS)

naive = sorted(ROWS, key=score, reverse=True)
show("sorted by score, reverse=True", naive)

wrong = sorted(naive, key=submitted)
show("...then sorted by submission date to fix the ties", wrong)

right = sorted(sorted(ROWS, key=submitted), key=score, reverse=True)
show("submission date first, then score  (correct)", right)

tuple_key = sorted(ROWS, key=lambda row: (-row[1], row[2]))
show("key=lambda row: (-row[1], row[2])", tuple_key)
print(f"  agrees with the two-pass version: {tuple_key == right}")
print()
print("The first version looks right, and it is wrong. The scores are in the")
print("right order, and the four 91s are in arrival order -- hal, eve, cyd,")
print("ada -- where the requirement asks for eve, ada, hal, cyd. Stability")
print("preserved an order nobody asked for.")
print()
print("That is the trap. `sorted` is stable, so a single-key sort silently")
print("inherits whatever order the input happened to be in, and that order")
print("is invisible in the code that does the sorting. It works in every")
print("test where the fixture is already in submission order.")
print()
print("The second version is the fix somebody reaches for after noticing:")
print("sort by score, then sort by the tie-break key. It replaces the wrong")
print("tie order with a completely wrong report -- now ordered by date, with")
print("the 65 sitting above two of the 91s. The score, which is the whole")
print("point of the page, is gone.")
print()
print("The rule is that a stable sort preserves the order it was *given*, so")
print("the last pass decides the primary order. Sort by the least significant")
print("key first and the most significant key last. Each pass can only")
print("rearrange items whose keys differ, so every earlier pass survives")
print("exactly inside the groups the final pass created.")
print()
print("The tuple key gets the same answer in one pass and is the version to")
print("prefer when it is available. Note the negation: `sorted` has no")
print("per-key direction, so 'descending on the score' means negating it")
print("inside the key -- which works for numbers and not much else.")
print()
print("`reverse=True` is no help either, because it reverses *every* key, so")
print("it cannot express 'descending on one and ascending on another'. That")
print("is the case where the two-pass version is not a stylistic choice but")
print("the only correct one.")
print()
print("And then the version that survives code review, because the keys are")
print("in the right order and only the direction is wrong:")
print()
sliced = sorted(ROWS, key=score)[::-1]
show("key=score, then [::-1]", sliced)
print("Same scores in the same order. The four 91s are now ada, cyd, eve,")
print("hal -- which is neither the arrival order nor the submission order,")
print("it is the arrival order reversed. Nothing raises, no test fails, and")
print("the only symptom is an ordering somebody has to notice by reading the")
print("output.")
print()
print("Compare the 91s across all four attempts:")
print()
for label, rows in (("arrival order", ROWS),
                    ("sorted by score", naive),
                    ("score then [::-1]", sliced),
                    ("the requirement", right)):
    names = [row[0] for row in rows if row[1] == 91]
    print(f"  {label:<20}{names}")
print()
print("Only the last line satisfies the requirement, and three of the four")
print("lines are things people write on purpose.")
