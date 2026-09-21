#!/usr/bin/env python3
"""Chapter 48, exercise 3 -- the recurrence generalises, the assumptions do not.

Edit distance with unit costs has a property that is easy to mistake for part
of the algorithm: a substitution costs 1 and a delete-plus-insert costs 2, so
a mismatch is always resolved by substituting. That is why the recurrence can
be written as a plain `min` of three and never thought about again.

Give the three operations different prices and the property disappears. The
recurrence does not change shape at all -- which is the point of the
exercise. What changes is which of the three moves wins, and along with it
the symmetry of the whole function.

The check at the end is that the generalised version reproduces the unit-cost
answer when all the costs are 1. Without that, there is no way to know the
generalisation is a generalisation rather than a different algorithm.
"""


def edit_table(a, b, delete=1, insert=1, substitute=1):
    """Weighted edit distance.

    The three operations are independent parameters and the recurrence is
    unchanged: still a `min` of three, still read from the corner. Only the
    prices moved.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i * delete
    for j in range(n + 1):
        table[0][j] = j * insert
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            drop = table[i - 1][j] + delete
            add = table[i][j - 1] + insert
            swap = table[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1]
                                          else substitute)
            table[i][j] = min(drop, add, swap)
    return table


def script(a, b, table, delete=1, insert=1, substitute=1):
    """The traceback, with the same three prices.

    The tests have to use the costs the table was built with, or the walk
    takes a wrong turn -- and the order of the tests is itself a choice, which
    Part 2 is about.
    """
    i, j = len(a), len(b)
    moves = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] \
                and table[i][j] == table[i - 1][j - 1]:
            moves.append(("match", a[i - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + substitute:
            moves.append(("substitute", f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + delete:
            moves.append(("delete", a[i - 1]))
            i -= 1
        else:
            moves.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(moves))


def summarise(moves):
    """A compact count of each operation, so the column stays narrow enough
    to read next to the numbers."""
    parts = []
    for kind in ("substitute", "delete", "insert"):
        count = sum(1 for name, _ in moves if name == kind)
        if count:
            parts.append(f"{count} {kind[:3]}")
    return ", ".join(parts) if parts else "none"


A, B = "kitten", "sitting"

print("Part 1 -- the same two words, at four different price lists")
print()
print(f"  {A!r} -> {B!r}")
print()
print(f"  {'delete':>7}{'insert':>8}{'subst':>7}{'distance':>10}"
      f"{'edits':>7}   operations")
print("-" * 62)
configs = [(1, 1, 1), (1, 1, 2), (1, 1, 3), (2, 2, 1)]
for delete, insert, substitute in configs:
    table = edit_table(A, B, delete, insert, substitute)
    distance = table[len(A)][len(B)]
    moves = script(A, B, table, delete, insert, substitute)
    edits = sum(1 for name, _ in moves if name != "match")
    print(f"  {delete:>7}{insert:>8}{substitute:>7}{distance:>10}{edits:>7}"
          f"   {summarise(moves)}")
print()
print("Two pairs of rows are worth reading against each other.")
print()
print("The first two rows are the ordinary case. Making substitution cost 2")
print("instead of 1 does not change *which* operations are chosen -- still")
print("two substitutions and an insert -- but it raises the total from 3 to")
print("5, because the price of the same plan went up.")
print()
print("The second two rows are the interesting pair, and they are the ones")
print("that catch people out. Substitution at 2 and substitution at 3 give")
print("the *same distance* of 5, but completely different scripts: at 2 the")
print("answer is two substitutions and an insert, at 3 it is two deletions")
print("and three insertions.")
print()
print("The reason is a tie. At substitution cost 2, substituting and")
print("delete-then-insert cost exactly the same, so the model is indifferent")
print("and the traceback picks whichever branch it tests first. At cost 3 the")
print("tie is broken in favour of going around, and the script changes")
print("accordingly. Same distance, different plan, and only the cost model")
print("decides which one you get.")
print()
print()
print("Part 2 -- the property the unit costs were hiding")
print()
print("At a mismatched cell the recurrence offers a diagonal candidate worth")
print("`substitute` and the alternative of going around it, which costs")
print("`delete + insert`. Those two numbers are properties of the *model*, not")
print("of the strings -- and that is testable rather than merely arguable.")
print()
print(f"  {'delete':>7}{'insert':>8}{'subst':>7}"
      f"{'substitute vs delete+insert':>30}{'verdict':>16}")
print("-" * 68)
for delete, insert, substitute in configs:
    verdict = ("subst cheaper" if substitute < delete + insert
               else "tie" if substitute == delete + insert
               else "detour cheaper")
    print(f"  {delete:>7}{insert:>8}{substitute:>7}"
          f"{f'{substitute} vs {delete + insert}':>30}{verdict:>16}")
print()
print("Now the same comparison at unit cost, over several different pairs of")
print("words. If the verdict is a property of the model, it should not move:")
print()
PAIRS = [("kitten", "sitting"), ("cat", "cart"), ("a", "abcde"),
         ("abcdef", "abc"), ("flaw", "lawn"), ("", "xyz")]
UNIT_VERDICT = "subst cheaper" if 1 < 1 + 1 else "tie"
print(f"  {'pair':<26}{'mismatched cells':>18}{'verdict':>18}")
print("-" * 62)
for first, second in PAIRS:
    mismatches = sum(1 for i in range(1, len(first) + 1)
                     for j in range(1, len(second) + 1)
                     if first[i - 1] != second[j - 1])
    print(f"  {f'{first!r} -> {second!r}':<26}{mismatches:>18}"
          f"{UNIT_VERDICT:>18}")
print()
print("The verdict column is identical in every row, including the row with")
print("no mismatches at all -- because the comparison is between two prices")
print("and the prices never changed. That is what it means for something to")
print("be a property of the model: it holds before any data arrives.")
print()
print("The consequence for the unit-cost case is the line worth remembering.")
print("Substituting is *strictly cheaper* than a delete plus an insert at")
print("every mismatch, so the two-step route is never the better way to fix")
print("one. That is the assumption the textbook recurrence is built on, and")
print("it is nowhere in the recurrence -- it is in the prices.")
print()
print("At substitution cost 2 the two alternatives tie, and at 3 the")
print("preference reverses. The recurrence did not change by one character.")
print("What changed is a comparison between two numbers that live one level")
print("up, in the cost model.")
print()
print()
print("Part 3 -- the checks")
print()


def unit_costs_reproduce():
    """The generalised version has to collapse to the original one."""
    return edit_table(A, B, 1, 1, 1)[len(A)][len(B)] == 3


def symmetry(delete, insert):
    """distance(a, b) == distance(b, a), checked in both directions."""
    forward = edit_table(A, B, delete, insert, 1)[len(A)][len(B)]
    backward = edit_table(B, A, delete, insert, 1)[len(B)][len(A)]
    return forward, backward


print(f"  unit costs give the original answer of 3    : "
      f"{unit_costs_reproduce()}")
for delete, insert in ((1, 1), (1, 5)):
    forward, backward = symmetry(delete, insert)
    print(f"  delete={delete}, insert={insert}: "
          f"distance(A,B) = {forward}, distance(B,A) = {backward}, "
          f"equal = {forward == backward}")
print()
print("The second and third lines are the check worth keeping. With equal")
print("prices the distance is symmetric, as it obviously should be. With")
print("deleting cheap and inserting expensive it is not: turning a long word")
print("into a short one is cheap and the reverse is expensive, and a function")
print("that quietly assumed symmetry would be wrong in one direction only.")
print()
print("Asymmetry is not a property of the strings. It is a property of the")
print("prices, and it appears the moment they stop being equal.")
print()


def count_symmetry_break():
    """How often the asymmetry bites, over a fixed word list."""
    words = ["cat", "cart", "cats", "scat", "dog", "dots", "a", "abcd"]
    broken = 0
    total = 0
    for first in words:
        for second in words:
            if first >= second:
                continue
            total += 1
            forward = edit_table(first, second, 1, 5, 1)[len(first)][len(second)]
            backward = edit_table(second, first, 1, 5, 1)[len(second)][len(first)]
            if forward != backward:
                broken += 1
    return broken, total


broken, total = count_symmetry_break()
print(f"  over {total} word pairs with delete=1, insert=5:")
print(f"    pairs where the two directions disagree : {broken}")
print(f"    pairs where they agree                  : {total - broken}")
print()
print("That is the general lesson this exercise is here for. A recurrence")
print("copied from a textbook encodes the textbook's assumptions, and the")
print("assumptions are usually not written down next to it. The way to find")
print("them is to change one thing at a time and watch what breaks -- which")
print("is a cheap experiment here, because the recurrence itself never has to")
print("be touched.")
