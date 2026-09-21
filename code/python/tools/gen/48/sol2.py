#!/usr/bin/env python3
"""Chapter 48, exercise 2 -- the two independent reasons a cache cannot help.

The chapter stated the test for dynamic programming as two conditions. This
exercise takes them apart by finding a recursion that fails each one, because
the usual phrasing -- 'DP needs overlapping subproblems' -- makes them sound
like one requirement and they are not.

Both failures look the same from outside: a cache that does not help. They
are different problems with different fixes, and neither fix is 'add a
dictionary'.
"""
import functools


def subsets_plain(items):
    """Every subset of `items`, as a tuple of tuples."""
    if not items:
        return [()]
    head, rest = items[0], items[1:]
    without = subsets_plain(rest)
    return without + [(head,) + tail for tail in without]


@functools.lru_cache(maxsize=None)
def subsets_cached(items):
    """The same recursion with a cache bolted on.

    `items` has to stay a tuple for the cache to accept it. Writing
    `head, *rest = items` would make `rest` a *list*, and the cache would
    raise `TypeError: unhashable type: 'list'` on the recursive call -- the
    hashability trap from the chapter, arriving on schedule.
    """
    if not items:
        return [()]
    head, rest = items[0], items[1:]
    without = subsets_cached(rest)
    return without + [(head,) + tail for tail in without]


print("Part 1 -- failure one: no state is ever revisited")
print()
print(f"{'n':>4}{'subsets produced':>18}{'distinct states':>17}"
      f"{'calls':>8}{'hits':>7}{'cached':>8}")
print("-" * 62)
rows = []
for n in range(1, 13):
    items = tuple(range(n))
    subsets_cached.cache_clear()
    produced = len(subsets_cached(items))
    info = subsets_cached.cache_info()
    rows.append((n, produced, info.misses, info.misses + info.hits,
                 info.hits, info.currsize))
    print(f"{n:>4}{produced:>18,}{info.misses:>17,}{info.misses + info.hits:>8,}"
          f"{info.hits:>7,}{info.currsize:>8,}")
print()
print("Three columns deserve to be read separately, because they are three")
print("different quantities that all look like 'the size of the problem'.")
print()
print(f"  the answer at n = 12        : {rows[-1][1]:,} subsets")
print(f"  the recursion's state space : {rows[-1][2]} states")
print(f"  the cache's hit count       : {rows[-1][4]}")
print()
print("The answer is exponential and the state space is linear, which is the")
print("first surprise in the exercise. The recursion only ever asks about a")
print("*suffix* of the list -- `items[1:]` -- so there are n + 1 things it can")
print("be called with, and it is called with each of them exactly once. The")
print("exponential part is the size of the values being returned, not the")
print("number of calls.")
print()
print("That is a distinction worth keeping: the two exponentials in this")
print("problem -- the size of the answer and the number of states -- are")
print("different quantities, and only one of them is exponential. Confusing")
print("them is the commonest way to conclude that a problem is hopeless when")
print("it is not.")
print()
print("So this is the clean example of failure one: polynomially many states")
print("and no overlap at all. Every call gets a distinct argument, so the")
print("hits column is zero and stays zero no matter how large n gets. The")
print("cache is a dictionary from argument to answer that is written n + 1")
print("times and read zero times.")
print()
print("Merge sort from the earlier section is the same failure with a")
print("different story. This one is worth having because the cache *works* --")
print("there is no TypeError, no missing hash, nothing to fix -- and it is")
print("still pointless, which is the harder case to notice in review.")
print()
print()
print("Part 2 -- failure two: the states are few, but the answers are huge")


def paths_with_cache(size):
    """Every monotone path from the top-left to the bottom-right of a
    `size` x `size` grid, with a hand-rolled cache so the cache's *contents*
    can be inspected rather than just its hit count.

    The state space here is genuinely small -- one entry per cell -- and the
    overlap is genuinely there. Both conditions are satisfied, and the cache
    is still the wrong tool.
    """
    cache = {}
    hits = [0]

    def go(r, c):
        if (r, c) in cache:
            hits[0] += 1
            return cache[(r, c)]
        if r == size - 1 and c == size - 1:
            result = (((r, c),),)
        else:
            tails = []
            if r + 1 < size:
                tails.extend(go(r + 1, c))
            if c + 1 < size:
                tails.extend(go(r, c + 1))
            result = tuple(((r, c),) + tail for tail in tails)
        cache[(r, c)] = result
        return result

    paths = go(0, 0)
    entries = len(cache)
    cells_stored = sum(sum(len(p) for p in value) for value in cache.values())
    return len(paths), entries, cells_stored, hits[0]


print()
print(f"{'grid':>8}{'paths':>14}{'cache entries':>15}"
      f"{'cache hits':>12}{'cells stored':>15}{'per state':>11}")
print("-" * 75)
grid_rows = []
for size in (4, 5, 6, 7, 8, 9):
    paths, entries, stored, hits = paths_with_cache(size)
    grid_rows.append((size, paths, entries, stored, hits))
    print(f"{f'{size}x{size}':>8}{paths:>14,}{entries:>15,}{hits:>12,}"
          f"{stored:>15,}{stored / entries:>11,.0f}")
print()
print("The third column is the state space -- one entry per cell, so it grows")
print("like n^2 and is entirely tame. The fifth column is what the cache is")
print("actually holding: every partial answer for every state, and each of")
print("those answers is itself a list of paths.")
print()
first, last = grid_rows[0], grid_rows[-1]
print(f"  paths grew by {last[1] / first[1]:,.0f}x from {first[0]}x{first[0]} to "
      f"{last[0]}x{last[0]}")
print(f"  cache entries grew by {last[2] / first[2]:,.1f}x over the same range")
print(f"  cells held grew by {last[3] / first[3]:,.0f}x")
print()
print("The two growth rates are the whole lesson. The state count is")
print("polynomial and the *data* is exponential, so a memo table over the")
print("states has exponential memory -- not because memoisation is wrong,")
print("but because it caches the answer and the answer is exponential.")
print()
print("This is the failure that does not show up in a hit-rate measurement.")
print(f"At {last[0]}x{last[0]} the cache is working perfectly: {last[2]} entries, "
      f"{last[4]:,} hits,")
print("no wasted lookups. It is also")
print(f"holding {last[3]:,} cell references to produce {last[1]:,} paths, and")
print("both of those numbers are the size of the output.")
print()
print("The fix is not a better cache. It is to notice that you were asked to")
print("*enumerate* an exponential set, and that no amount of memoisation")
print("changes the size of the answer. If the caller only needs the *number*")
print("of paths, the same table gives it in one integer per state -- which is")
print("the previous chapter's path-counting DP, and it is why 'count them'")
print("and 'list them' are different problems with the same recurrence.")
print()
print()
print("Part 3 -- the two conditions, stated so they can be tested separately")
print()
print(f"  {'recursion':<22}{'states':>12}{'overlap':>12}{'verdict':>18}")
print("-" * 64)
fib_calls = [0]
fib_seen = set()


def fib(k):
    fib_calls[0] += 1
    fib_seen.add(k)
    if k < 2:
        return k
    return fib(k - 1) + fib(k - 2)


fib(20)
print(f"  {'fib(20)':<22}{len(fib_seen):>12,}{fib_calls[0] / len(fib_seen):>12,.0f}"
      f"{'DP applies':>18}")
print(f"  {'subsets(12)':<22}{rows[-1][2]:>12,}{'1':>12}"
      f"{'no overlap':>18}")
print(f"  {'paths, 9x9':<22}{grid_rows[-1][2]:>12,}"
      f"{grid_rows[-1][4]:>12,}{'cache the count':>18}")
print()
print("  fib(20)      : n + 1 states, thousands of revisits  -> memoise it")
print("  subsets(12)  : n + 1 states, zero revisits          -> do not")
print("  paths, 9x9   : 81 states, plenty of revisits        -> memoise the")
print("                 count, never the list")
print()
print("The middle row is the one the usual phrasing of the test misses. It")
print("has the *right* number of states and the *wrong* amount of reuse, and")
print("neither of those is visible without counting.")
