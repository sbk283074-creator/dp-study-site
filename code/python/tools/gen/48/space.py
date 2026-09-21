#!/usr/bin/env python3
"""Chapter 48 demo -- what the table costs, and what you give up by not
keeping it.

Every DP in this chapter has been a table. The table is also the part you can
usually throw away, and the two questions worth asking are 'how much does it
cost' and 'what did it buy me'.

The answer to the second one is more interesting than the answer to the
first. What the table buys is not the *answer* -- it is the *path*, and there
is a third option between keeping every number and keeping none.
"""


def edit_full(a, b):
    """The table, kept. Distance and path."""
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i
    for j in range(n + 1):
        table[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            table[i][j] = min(table[i - 1][j] + 1,
                              table[i][j - 1] + 1,
                              table[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    return table


def edit_two_rows(a, b):
    """Two rows. Distance only -- and the reason it is distance only is that
    the row that would have answered 'where did this come from' was
    overwritten two iterations ago."""
    n = len(b)
    previous = list(range(n + 1))
    for i in range(1, len(a) + 1):
        current = [i] + [0] * n
        for j in range(1, n + 1):
            current[j] = min(previous[j] + 1,
                             current[j - 1] + 1,
                             previous[j - 1] + (a[i - 1] != b[j - 1]))
        previous = current
    return previous[n]


def edit_two_rows_and_bits(a, b):
    """Two rows of numbers, plus one byte per cell recording which move won.

    This is the option people forget exists. The numbers are big and there are
    (m+1)(n+1) of them; the *decisions* are three-valued and there are the
    same number of them. Keeping the decisions instead of the numbers is
    enough to rebuild the path, and the numbers are the expensive part.
    """
    m, n = len(a), len(b)
    width = n + 1
    moves = bytearray((m + 1) * width)      # 0 delete, 1 insert, 2 substitute
    previous = list(range(width))
    for i in range(1, m + 1):
        current = [i] + [0] * n
        for j in range(1, n + 1):
            delete = previous[j] + 1
            insert = current[j - 1] + 1
            substitute = previous[j - 1] + (a[i - 1] != b[j - 1])
            best = min(delete, insert, substitute)
            current[j] = best
            if best == substitute:
                moves[i * width + j] = 2
            elif best == delete:
                moves[i * width + j] = 0
            else:
                moves[i * width + j] = 1
        previous = current
    return previous[n], moves


def rebuild(a, b, moves):
    """Reconstruct the edit script from the decisions alone."""
    width = len(b) + 1
    i, j = len(a), len(b)
    script = []
    while i > 0 or j > 0:
        if i == 0:
            script.append(("insert", b[j - 1]))
            j -= 1
            continue
        if j == 0:
            script.append(("delete", a[i - 1]))
            i -= 1
            continue
        move = moves[i * width + j]
        if move == 2:
            script.append(("match" if a[i - 1] == b[j - 1] else "substitute",
                           a[i - 1] if a[i - 1] == b[j - 1] else
                           f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif move == 0:
            script.append(("delete", a[i - 1]))
            i -= 1
        else:
            script.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(script))


def path_from_full(a, b, table):
    """The same reconstruction, reading the numbers instead of the bits."""
    i, j = len(a), len(b)
    script = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] \
                and table[i][j] == table[i - 1][j - 1]:
            script.append(("match", a[i - 1]))
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + 1:
            script.append(("substitute", f"{a[i - 1]}->{b[j - 1]}"))
            i, j = i - 1, j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            script.append(("delete", a[i - 1]))
            i -= 1
        else:
            script.append(("insert", b[j - 1]))
            j -= 1
    return list(reversed(script))


A = "the quick brown fox jumps over the lazy dog"
B = "the quik brown fax jumped over a lazy dig"
M, N = len(A), len(B)

print("Part 1 -- the three versions, on the same pair of strings")
print()
print(f"  source : {A!r}")
print(f"  target : {B!r}")
print(f"  lengths: {M} and {N}")
print()
table = edit_full(A, B)
distance = table[M][N]
two_row_distance = edit_two_rows(A, B)
bit_distance, moves = edit_two_rows_and_bits(A, B)
print(f"  {'version':<28}{'distance':>10}{'path?':>8}")
print("-" * 46)
print(f"  {'full table':<28}{distance:>10}{'yes':>8}")
print(f"  {'two rows':<28}{two_row_distance:>10}{'no':>8}")
print(f"  {'two rows + decision bytes':<28}{bit_distance:>10}{'yes':>8}")
print()
print(f"  all three agree on the distance : "
      f"{distance == two_row_distance == bit_distance}")
print()
print("The distance is cheap and all three versions get it. The path is what")
print("costs memory, and the third row is the point: you do not need to keep")
print("the numbers to keep the path. You need to keep the *decisions*, and")
print("there are only three of those per cell.")
print()
print()
print("Part 2 -- what each one actually stores")
print()
cells = (M + 1) * (N + 1)
print(f"  {'version':<28}{'numbers':>10}{'bytes':>10}{'lists':>8}")
print("-" * 56)
print(f"  {'full table':<28}{cells:>10,}{'-':>10}{M + 1:>8,}")
print(f"  {'two rows':<28}{2 * (N + 1):>10,}{'-':>10}{2:>8,}")
print(f"  {'two rows + decision bytes':<28}{2 * (N + 1):>10,}"
      f"{cells:>10,}{2:>8,}")
print()
print(f"  numbers stored, full table vs two rows : "
      f"{cells / (2 * (N + 1)):.1f}x")
print()
print("The comparison understates the difference, because a 'number' here is")
print("a Python int in a list -- a pointer plus an object, not a machine")
print("word. A byte in a bytearray is one byte, with no object behind it. So")
print("the third version replaces roughly")
print(f"{cells:,} integers with {cells:,} bytes, and pays")
print(f"{2 * (N + 1):,} integers for the rolling rows.")
print()
print("In a language where an int is four bytes the trade is less dramatic")
print("but still real: four bytes per cell becomes one, and the rolling rows")
print("stay the same. The principle is the one that transfers -- store the")
print("decision, not the derived value, whenever the decision is smaller.")
print()
print()
print("Part 3 -- and the paths really are the same path")
print()
from_table = path_from_full(A, B, table)
from_bits = rebuild(A, B, moves)
print(f"  path from the full table    : {len(from_table)} steps")
print(f"  path from the decision bytes: {len(from_bits)} steps")
print(f"  identical                   : {from_table == from_bits}")
print()
print("  the first few steps:")
for name, detail in from_bits[:6]:
    print(f"    {name:<12}{detail}")
print("  ...")
print()
print("That equality is the useful result, and it is not obvious in advance.")
print("It says the numbers in the table are *derived* -- every one of them")
print("can be recomputed from the decisions -- while the decisions cannot be")
print("recovered from the numbers without walking the table again.")
print()
print("So the table is not really storing distances. It is storing a")
print("justification for each distance, in the most convenient form someone")
print("thought of first. Once you see it that way, the two-row version stops")
print("looking like a clever memory trick and starts looking like a")
print("misunderstanding: it keeps the conclusion and throws away the")
print("reasoning.")
print()
print()
print("Part 4 -- the same comparison at a size where it matters")
print()
print("The pair of strings above is deliberately small, so the three versions")
print("differ by a couple of thousand numbers and the saving is academic.")
print("Here is the same table for problems where it is not:")
print()
print(f"{'problem size':>14}{'full table':>14}{'two rows':>11}"
      f"{'decisions':>12}{'ratio':>9}")
print("-" * 60)
for size in (100, 1_000, 10_000):
    grid = (size + 1) ** 2
    print(f"{f'{size}x{size}':>14}{grid:>14,}{2 * (size + 1):>11,}"
          f"{grid:>12,}{grid / (2 * (size + 1)):>8.0f}x")
print()
print("The ratio column is the one to keep. For an n x n problem the full")
print("table holds n^2 numbers and the rolling pair holds 2n, so the gap")
print("grows like n/2 without bound -- 50x at a hundred, 5,000x at ten")
print("thousand. The decision bytes grow like n^2 as well, but a byte is not")
print("a number: in Python a stored int is a pointer into a list plus an")
print("object behind it, and the object is not free.")
print()
print("So the honest summary of this section is a three-line rule rather than")
print("a single recommendation:")
print()
print("  keep the numbers  when you need the path and the problem is small")
print("  keep the decisions when you need the path and the problem is large")
print("  keep two rows     only when you need the number and nothing else")
print()
print("The second line is the one that is usually forgotten, because the")
print("choice is presented as 'table or no table' and there is a third")
print("option sitting between them.")
print()
print()
print("Part 5 -- the escape hatch, and why this is a default rather than a law")
print()
print("Hirschberg's algorithm gets the path *and* linear memory, and it does")
print("it by giving up something this section has quietly assumed: that each")
print("cell is computed once.")
print()
print("The idea is to compute only the middle row of the table, find the")
print("column where an optimal path crosses it, and then solve the two halves")
print("recursively. Each level of the recursion recomputes what the level")
print("above threw away, so the work goes up by a constant factor while the")
print("memory falls from quadratic to linear.")
print()
print(f"  the pair in Part 1 needs {cells:,} numbers for the full table")
print(f"  and {2 * (N + 1):,} for the rolling rows")
print(f"  a 10,000x10,000 pair needs {10_001 ** 2:,} for the full table")
print(f"  and {2 * 10_001:,} for the rolling rows, at roughly twice the work")
print()
print("That trade -- a factor of two in time for a factor of n/2 in memory --")
print("is a good one whenever the strings are large, which is exactly when")
print("the naive table stops fitting. It is also the reason the advice in")
print("this section is a default: 'keep the table' is the right answer until")
print("the table is the problem.")
