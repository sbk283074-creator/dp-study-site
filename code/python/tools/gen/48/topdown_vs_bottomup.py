#!/usr/bin/env python3
"""Chapter 48 demo -- the same recurrence, run in both directions.

Top-down starts at the answer and asks for whatever it needs; bottom-up starts
at the base cases and builds towards the answer. They fill in the same table,
and they differ in two things that matter: which states get visited, and how
much stack the recursion uses.

Neither is better. The counts below show where each one wins.
"""
import random
import sys

LIMIT = sys.getrecursionlimit()


def fib_top_down(n, memo, tally):
    tally[0] += 1
    if n < 2:
        return n
    if n in memo:
        tally[1] += 1
        return memo[n]
    memo[n] = fib_top_down(n - 1, memo, tally) + fib_top_down(n - 2, memo, tally)
    return memo[n]


def fib_bottom_up(n, tally):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        tally[0] += 1
        previous, current = current, previous + current
    return current


print("Part 1 -- the same recurrence, and where each version stops")
print()
print(f"  the interpreter's recursion limit is {LIMIT}")
print()
print(f"{'n':>7}{'top-down entries':>19}{'outcome':>18}")
print("-" * 44)
for n in (10, 100, 500, 1_000, 2_000, 5_000):
    tally = [0, 0]
    try:
        fib_top_down(n, {}, tally)
        entries, outcome = f"{tally[0]:,}", "ok"
    except RecursionError:
        entries, outcome = "-", "RecursionError"
    print(f"{n:>7,}{entries:>19}{outcome:>18}")
print()
print(f"{'n':>7}{'bottom-up steps':>19}{'outcome':>18}")
print("-" * 44)
for n in (10, 100, 500, 1_000, 2_000, 5_000):
    tally = [0]
    fib_bottom_up(n, tally)
    print(f"{n:>7,}{tally[0]:>19,}{'ok':>18}")
print()
print("The two tables are the point, and they disagree in the second column.")
print("Top-down works at n = 500 and raises `RecursionError` at n = 1,000,")
print("with no change to the recurrence at all. Bottom-up does not care how")
print("large n gets, because it never recurses -- there is no stack to")
print("overflow.")
print()
print("The exact n where top-down breaks is somewhere just below the limit")
print("printed above, and it is not worth pinning down more precisely than")
print("that: the boundary depends on how many frames the interpreter had")
print("already used before the call, which is not a property of the")
print("algorithm. What *is* a property of the algorithm is the shape -- the")
print("depth grows linearly with n, so the limit is a hard ceiling on n.")
print()
print("Notice the relationship between the two tables while they are both")
print("available. Bottom-up runs one loop step per subproblem above the base")
print("cases, so n - 1 of them: 9, 99, 499. Top-down enters the function")
print("2n - 1 times at every n in the table -- 19, 199, 999 -- which is one")
print("entry per subproblem, plus one more for each time a subproblem is")
print("asked for after it has already been computed. The arithmetic behind")
print("those entries is the same n - 1 additions either way. That is what")
print("'they fill in the same table' means: identical work, different order")
print("and different bookkeeping.")
print()
print()
print("Part 2 -- the recursion limit, and the thing that is not a fix")
print()
probe = 1_500
tally = [0, 0]
try:
    fib_top_down(probe, {}, tally)
    print(f"  at n = {probe:,}, default limit      : ok")
except RecursionError:
    print(f"  at n = {probe:,}, default limit      : RecursionError")
sys.setrecursionlimit(10_000)
tally = [0, 0]
fib_top_down(probe, {}, tally)
print(f"  at n = {probe:,}, limit raised       : ok, {tally[0]:,} entries")
print(f"  the new limit                     : {sys.getrecursionlimit():,}")
sys.setrecursionlimit(LIMIT)
print(f"  restored to                       : {sys.getrecursionlimit():,}")
print()
print("Raising the limit worked here, and it is still not the fix. What")
print("`sys.setrecursionlimit` changes is a *counter* that CPython checks on")
print("entry to each frame. It does not make the real call stack any larger.")
print("Set it high enough and a recursion that would have raised a catchable")
print("`RecursionError` instead runs off the end of the actual stack and takes")
print("the interpreter down with it -- no exception, no traceback, no chance")
print("to log anything.")
print()
print("So the limit is not a nuisance to be configured away. It is a")
print("constraint on the *design*: a recurrence that recurses once per")
print("element has a hard ceiling on the input it can handle, and that ceiling")
print("belongs in the decision about how to write it, not in a startup line.")
print()
print()
print("Part 3 -- and the case where top-down wins outright")
print()
ROWS = COLS = 40
CELLS = ROWS * COLS


def build(density, seed=13):
    rng = random.Random(seed)
    blocked = {(r, c) for r in range(ROWS) for c in range(COLS)
               if rng.random() < density}
    blocked.discard((0, 0))
    blocked.discard((ROWS - 1, COLS - 1))
    return blocked


def paths_top_down(blocked):
    """Count the routes from (0, 0) to (r, c) moving only down and right.
    Cells that cannot be part of any route are never visited, because nothing
    asks about them."""
    memo = {}

    def go(r, c):
        if r < 0 or c < 0 or (r, c) in blocked:
            return 0
        if r == 0 and c == 0:
            return 1
        if (r, c) in memo:
            return memo[(r, c)]
        memo[(r, c)] = go(r - 1, c) + go(r, c - 1)
        return memo[(r, c)]

    value = go(ROWS - 1, COLS - 1)
    return len(memo), value


def paths_bottom_up(blocked):
    """Fill every cell in row-major order, whether or not it can be reached."""
    steps = 0
    table = [[0] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            steps += 1
            if (r, c) in blocked:
                continue
            if r == 0 and c == 0:
                table[r][c] = 1
            else:
                from_above = table[r - 1][c] if r > 0 else 0
                from_left = table[r][c - 1] if c > 0 else 0
                table[r][c] = from_above + from_left
    return steps, table[ROWS - 1][COLS - 1]


print(f"  a {ROWS}x{COLS} grid, {CELLS:,} cells, walls dropped in at random")
print()
print(f"{'walls':>7}{'blocked':>9}{'top-down':>11}{'bottom-up':>11}"
      f"{'saving':>9}{'routes':>13}")
print("-" * 60)
for density in (0.05, 0.10, 0.15, 0.20, 0.25, 0.28, 0.30, 0.32, 0.34, 0.38):
    blocked = build(density)
    down_states, down_value = paths_top_down(blocked)
    up_states, up_value = paths_bottom_up(blocked)
    assert down_value == up_value
    print(f"{density:>6.0%}{len(blocked):>9,}{down_states:>11,}{up_states:>11,}"
          f"{up_states / down_states:>8.1f}x{down_value:>13.3e}")
print()
print("(The route counts are in scientific notation because they run to two")
print(" dozen digits at low wall density, and the exact value is not the")
print(" point -- whether the last column is zero is.)")
print()
print("Read the two count columns together with the last one, because on")
print("their own they are misleading.")
print()
print("At the top of the table almost nothing is blocked and top-down saves")
print("almost nothing -- because with no walls, every cell lies on some route")
print("to the corner, so the states the answer depends on *are* the whole")
print("grid. The two approaches visit the same set and the saving is 1.1x.")
print()
print("As walls go in, the reachable set shrinks faster than the grid does,")
print("and the gap opens up. That is the real advantage of top-down: not that")
print("it is cleverer, but that it never looks at a state the answer does not")
print("depend on.")
print()
print("Now look at the bottom of the table, where the last column goes to 0.")
print("The saving keeps climbing -- and it is climbing for the worst possible")
print("reason. Once the walls seal the corner off, the recursion unwinds")
print("immediately, explores a few dozen cells, finds nothing and returns 0.")
print("The ratio is largest exactly where the search is doing no work at all.")
print()
print("That is worth keeping. A count is only a measure of anything when the")
print("two runs are computing the same non-trivial thing. This table is built")
print("so that the answer is checkable in every row, which is why the zero in")
print("the last column is visible at all -- a benchmark that only reported")
print("the ratio would have ranked the failed searches first.")
print()
print("The rule of thumb that falls out: bottom-up when the state space is")
print("dense and you will need most of it; top-down when it is sparse, or when")
print("the reachable part is hard to characterise, or when you want the")
print("recurrence to stay readable next to its definition.")
print()
print("What you are choosing between is not speed and clarity. It is whether")
print("you want to visit the states the answer depends on, or all the states")
print("that exist -- and those are different sets more often than they look.")
print()
dense = build(0.05)
sparse = build(0.32)
dense_states, dense_value = paths_top_down(dense)
sparse_states, sparse_value = paths_top_down(sparse)
print(f"  cells in the grid           : {CELLS:,}")
print(f"  states visited, 5% walls    : {dense_states:,} "
      f"({dense_states / CELLS:.0%} of the grid)")
print(f"  states visited, 32% walls   : {sparse_states:,} "
      f"({sparse_states / CELLS:.0%} of the grid)")
print(f"  routes, 5% walls            : {dense_value:.3e} (non-zero)")
print(f"  routes, 32% walls           : {sparse_value:.3e} (non-zero)")
