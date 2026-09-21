#!/usr/bin/env python3
"""Chapter 48 demo -- what a state has to remember.

The longest common subsequence is the sibling of edit distance: the same
two-dimensional table, a different recurrence. It is worth doing both because
the *difference* between them is where the design work is -- and because LCS
is the algorithm inside `diff`.

The second half is the sharper lesson. Longest common *substring* looks like
the same problem and is not: it needs a different state, and the answer is
read from a different cell of the table. Getting that wrong is the most
common way a DP is written correctly and still gives the wrong number.
"""
import functools


def lcs_table(a, b):
    """table[i][j] = the length of the longest common subsequence of the
    first i characters of `a` and the first j of `b`.

    The state has to be a pair of *prefix* lengths. It cannot be 'the LCS of
    the whole strings', because that has no smaller version of itself to
    recurse into; it cannot be a pair of suffixes either, because the answer
    for suffixes does not compose when you extend them at the front.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table


def all_lcs(a, b, table):
    """Every distinct longest common subsequence, as strings. Memoised, which
    is the same idea applied to the *set* of answers rather than the length."""
    @functools.lru_cache(maxsize=None)
    def go(i, j):
        if i == 0 or j == 0:
            return frozenset([""])
        if a[i - 1] == b[j - 1]:
            return frozenset(s + a[i - 1] for s in go(i - 1, j - 1))
        found = set()
        if table[i - 1][j] >= table[i][j - 1]:
            found |= go(i - 1, j)
        if table[i][j - 1] >= table[i - 1][j]:
            found |= go(i, j - 1)
        return frozenset(found)

    return go(len(a), len(b))


def substring_table(a, b):
    """Longest common *substring*. Same shape of table, different meaning.

    table[i][j] is now 'the length of the longest common run that ends
    exactly at position i of `a` and position j of `b`' -- so the answer is
    the largest value anywhere in the table, not the corner. There is no
    `max` in the recurrence, because a run that breaks cannot be extended.
    """
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
                best = max(best, table[i][j])
    return table, best


def show(a, b, table, label):
    n = len(b)
    head = "".join(f"{'-' if j == 0 else b[j - 1]:>4}" for j in range(n + 1))
    print(f"  {label}")
    print(f"      {head}")
    for i in range(len(a) + 1):
        name = "-" if i == 0 else a[i - 1]
        cells = "".join(f"{table[i][j]:>4}" for j in range(n + 1))
        print(f"  {name:>3} {cells}")


A, B = "abcbdab", "bdcaba"

print("Part 1 -- the table, and the one line that differs from edit distance")
print()
table = lcs_table(A, B)
show(A, B, table, f"LCS of {A!r} and {B!r}")
print()
print(f"  {A!r} vs {B!r} : longest common subsequence is "
      f"{table[len(A)][len(B)]} characters")
print()
print("Compare this recurrence with the previous section's:")
print()
print("  edit distance : table[i][j] = min(three things, one of them +cost)")
print("  LCS           : table[i][j] = table[i-1][j-1] + 1   when equal")
print("                  table[i][j] = max(above, left)       when not")
print()
print("The equal case is not a `max` -- it is forced. If the two characters")
print("match, there is always an optimal solution that uses them, so the cell")
print("is the diagonal plus one and the other two candidates are irrelevant.")
print("The unequal case is where the choice lives, and there the choice is")
print("only between dropping a character from one string or the other.")
print()
print("That is the difference between an edit and a match, expressed as a")
print("recurrence: editing costs you one operation, matching costs you")
print("nothing and gains you a character.")
print()
print()
print("Part 2 -- ties, and why the answer is not unique")
print()
answers = sorted(all_lcs(A, B, table))
print(f"  distinct longest common subsequences : {len(answers)}")
for answer in answers:
    print(f"    {answer!r}")
print()
print("All of them are the same length, and they are all correct. That is not")
print("a flaw in the algorithm -- the problem statement has a tie in it, and")
print("any implementation has to break the tie somewhere.")
print()
print("`all_lcs` breaks it by taking *both* branches when the two neighbours")
print("are equal, which is why it returns a set. A traceback that tests")
print("`table[i-1][j] > table[i][j-1]` with a strict `>` silently picks one")
print("and returns it; testing `>=` first on the other side returns a")
print("different one. Both are valid, and a diff tool built on either will")
print("produce different output for the same input.")
print()
print()
print("Part 3 -- the same-looking problem that needs a different state")
print()
sub_table, best = substring_table(A, B)
show(A, B, sub_table, f"longest common SUBSTRING of {A!r} and {B!r}")
print()
print(f"  longest common substring  : {best} characters")
print(f"  longest common subsequence: {table[len(A)][len(B)]} characters")
print()
print("Two tables, both filled by a double loop over the same pair of")
print("strings, and the numbers are different. The reason is entirely in what")
print("the state *means*.")
print()
print("In the subsequence table, a cell says 'how good can I do with these")
print("two prefixes' -- so it is a running best, and it can never go down as")
print("the prefixes grow. In the substring table, a cell says 'how long is")
print("the run that ends exactly here' -- so it drops to zero the moment the")
print("characters differ, and the answer has to be harvested as a maximum")
print("over the whole table.")
print()
print("The second table has no `max` in its recurrence at all, which is the")
print("tell. A `max` between neighbours is the signature of a state that")
print("carries a running best; its absence means the state is pinned to a")
print("position, and the running best has to be collected elsewhere.")
print()
lcs_answer = table[len(A)][len(B)]
sub_answer_cells = [(i, j) for i, row in enumerate(table)
                    for j, v in enumerate(row) if v == lcs_answer]
substr_answer_cells = [(i, j) for i, row in enumerate(sub_table)
                       for j, v in enumerate(row) if v == best]
print(f"  cells holding the answer, subsequence : {len(sub_answer_cells)}")
print(f"    in rows {sorted({i for i, _ in sub_answer_cells})} "
      f"of {len(A)}")
print(f"  cells holding the answer, substring   : {len(substr_answer_cells)}")
print(f"    in rows {sorted({i for i, _ in substr_answer_cells})} "
      f"of {len(A)}")
print()
print("The counts are similar and the counts are not the point -- the")
print("*positions* are. Every cell holding the subsequence answer is in the")
print("last two rows, and the reason is structural: the subsequence table")
print("never goes down, so once a cell has reached the maximum, every cell")
print("down and to the right of it keeps that maximum. The answer is")
print("guaranteed to be in the corner, and the other cells that share it are")
print("just cells that can already see the corner.")
print()
print("The substring answer cells are scattered through the table, and which")
print("rows they land in depends on the input. There is no cell whose")
print("coordinates you know in advance, so the loop has to carry a running")
print("maximum as it goes.")
print()
print("That is the difference that bites. If you forget the running maximum")
print("the code still runs, still returns a plausible number, and nothing")
print("about the output tells you it is wrong -- the worst kind of bug,")
print("because it is invisible until the input happens to matter.")
