#!/usr/bin/env python3
"""Chapter 48 demo -- edit distance, the first DP that is not a toy.

Fibonacci shows the mechanism. Edit distance shows the *shape*: the state is a
pair of positions, so the table is two-dimensional, and every cell is a choice
between three moves. It is also the recurrence behind every spell checker and
every `diff`.

Everything below is counted, and the counts are the argument: the naive
recursion is exponential while the table is quadratic, and the gap between
those two numbers is the whole reason the table exists.
"""


def edit_table(a, b):
    """Levenshtein distance, filled in as the table the recurrence describes.

    table[i][j] is the distance between the first i characters of `a` and the
    first j characters of `b`. Row 0 and column 0 are the base cases: turning
    a string into the empty string costs one deletion per character.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i
    for j in range(n + 1):
        table[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            delete = table[i - 1][j] + 1
            insert = table[i][j - 1] + 1
            substitute = table[i - 1][j - 1] + (a[i - 1] != b[j - 1])
            table[i][j] = min(delete, insert, substitute)
    return table


def edit_naive(a, b, i, j, tally, seen):
    """The same recurrence with no table.

    Every call makes all three recursive calls before `min` looks at them, so
    the call count depends only on the two lengths -- not on the characters,
    and not on which move turns out to be cheapest.
    """
    tally[0] += 1
    seen.add((i, j))
    if i == 0:
        return j
    if j == 0:
        return i
    return min(edit_naive(a, b, i - 1, j, tally, seen) + 1,
               edit_naive(a, b, i, j - 1, tally, seen) + 1,
               edit_naive(a, b, i - 1, j - 1, tally, seen)
               + (a[i - 1] != b[j - 1]))


def show(a, b, table):
    n = len(b)
    head = "".join(f"{'-' if j == 0 else b[j - 1]:>4}" for j in range(n + 1))
    print(f"      {head}")
    for i in range(len(a) + 1):
        label = "-" if i == 0 else a[i - 1]
        cells = "".join(f"{table[i][j]:>4}" for j in range(n + 1))
        print(f"  {label:>3} {cells}")


print("Part 1 -- the table, for two words that are almost the same")
print()
A, B = "kitten", "sitting"
table = edit_table(A, B)
show(A, B, table)
print()
print(f"  {A!r} -> {B!r} : {table[len(A)][len(B)]} edits")
print()
print("The table is the recurrence. Read row i and column j as 'the first i")
print("characters of the source, the first j of the target', and the number")
print("in the cell as the cheapest way to get from one to the other. Each")
print("cell is the minimum of three, and those three are the three things you")
print("can do at that position:")
print()
print("  table[i-1][j]   + 1     delete a character from the source")
print("  table[i][j-1]   + 1     insert a character into the source")
print("  table[i-1][j-1] + cost  substitute, free when the characters match")
print()
print("The top row and the left column are the base cases, and they are the")
print("answer to 'what does it cost to turn this into nothing'. Turning")
print("kitten into the empty string is six deletions, so the left column")
print("counts up from 0 to 6 -- it is not a special case bolted on, it is the")
print("recurrence applied to an empty second string.")
print()
print("The bottom-right cell is the answer, and everything else in the table")
print("was computed to get there. That is the trade the previous section was")
print(f"about: {len(table) * len(table[0])} cells, of which {len(table) * len(table[0]) - 1} exist only to")
print("support the one in the corner.")
print()
print()
print("Part 2 -- the same recurrence without the table")
print()
print(f"{'n':>5}{'distinct states':>17}{'naive calls':>14}{'repeats':>10}"
      f"{'growth':>10}{'target':>10}")
print("-" * 66)
TARGET = 3 + 2 * 2 ** 0.5
rows = []
for n in range(1, 9):
    a = "abcdefgh"[:n]
    b = "abcdefgh"[:n - 1] + "z"
    tally, seen = [0], set()
    naive = edit_naive(a, b, n, n, tally, seen)
    rows.append((n, len(seen), tally[0]))
    growth = f"{tally[0] / rows[-2][2]:.2f}" if len(rows) > 1 else "-"
    print(f"{n:>5}{len(seen):>17,}{tally[0]:>14,}"
          f"{tally[0] / len(seen):>10.1f}{growth:>10}{TARGET:>10.2f}")
print()
print(f"  the table has (n+1)^2 cells : {rows[-1][1]:,} at n = {rows[-1][0]}")
print(f"  the naive recursion calls   : {rows[-1][2]:,}")
print(f"  one is quadratic, the other : exponential")
print()
print("The growth column is the diagnosis. Each extra character multiplies")
print("the work by the same factor every time -- that is what exponential")
print("means -- and the factor is neither 2 nor 3.")
print()
print("Three branches per node suggests 3^n, and that is wrong, for a reason")
print("worth working out. The three calls move to (i-1, j), (i, j-1) and")
print("(i-1, j-1): they step in two dimensions, not one. So the count is a")
print("count of paths through a grid, not of levels of a tree, and paths")
print("through a grid grow faster than the branching factor suggests. The")
print("rate is 3 + 2*sqrt(2), which is the target column -- and the growth")
print("column is still climbing toward it at n = 8, because the convergence")
print("is slow, exactly as it was for phi in the first section.")
print()
print("The distinct column is the other half, and it is the one that matters")
print("for the fix. Every call is asking about a pair (i, j) of prefixes, and")
print("there are only (n+1)^2 such pairs. So the recursion is doing")
print(f"{rows[-1][2]:,} things when there are {rows[-1][1]:,} different things to do -- and the")
print("table is just the set of distinct answers, computed once each.")
print()
print()
print("Part 3 -- walking the table back to get the operations")
print()


def traceback(a, b, table):
    """Follow the same three moves backwards from the corner. Each step
    re-derives which of the three the cell came from, because the table only
    stored the cost."""
    i, j = len(a), len(b)
    moves = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] \
                and table[i][j] == table[i - 1][j - 1]:
            moves.append(("match", a[i - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + 1:
            moves.append(("substitute", f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            moves.append(("delete", a[i - 1]))
            i -= 1
        else:
            moves.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(moves))


moves = traceback(A, B, table)
print(f"  {'operation':<14}{'character':>12}{'running cost':>16}")
print("-" * 42)
cost = 0
for name, detail in moves:
    if name != "match":
        cost += 1
    print(f"  {name:<14}{detail:>12}{cost:>16}")
print()
print(f"  {len(moves)} positions, {sum(1 for n, _ in moves if n != 'match')} of them "
      f"costing an edit")
print()
print("The traceback is why the table is worth keeping. The recurrence gives")
print("you the *cost* in the corner; the table gives you the *operations*, by")
print("walking backwards and re-deriving at each cell which of the three")
print("moves the minimum came from.")
print()
print("Note that the walk has to test the moves in a fixed order, and that")
print("the order is a choice. Two different optimal edit scripts can have the")
print("same total cost, and the one you get back depends on which test you")
print("write first. That is not a bug -- it is the same tie-breaking question")
print("that came up for A* in the previous chapter, and it is why a diff tool")
print("and a spell checker can disagree about the 'right' answer while both")
print("being correct about the cost.")
print()
print("Part 3 also shows the cost of the table in a second way. Every cell")
print("here was already computed in Part 1; the walk does not recompute")
print("anything, it just reads. A version that kept only the last row would")
print("have the same 3 in the corner and no way to produce this list at all.")
