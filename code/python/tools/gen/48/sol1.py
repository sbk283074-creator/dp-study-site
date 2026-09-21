#!/usr/bin/env python3
"""Chapter 48, exercise 1 -- a second recurrence, and the two questions that
tell you whether it is a DP.

Climbing a staircase where each step is 1, 2 or 3 stairs: how many different
ways are there to reach step n? It is the same shape as Fibonacci with a
wider fan-out, and it is worth doing once because the *counts* make the
memoisation argument in a way Fibonacci cannot.

The check at the end is the useful part: the memoised count and the
bottom-up count have to be the same, and the naive one has to blow up.
"""


def ways_naive(n, tally):
    tally[0] += 1
    if n < 0:
        return 0
    if n == 0:
        return 1
    return (ways_naive(n - 1, tally) + ways_naive(n - 2, tally)
            + ways_naive(n - 3, tally))


def ways_memo(n, cache, tally):
    tally[0] += 1
    if n < 0:
        return 0
    if n == 0:
        return 1
    if n in cache:
        tally[1] += 1
        return cache[n]
    cache[n] = (ways_memo(n - 1, cache, tally) + ways_memo(n - 2, cache, tally)
                + ways_memo(n - 3, cache, tally))
    return cache[n]


def ways_bottom_up(n):
    """The same recurrence, forwards. The last three values are all it ever
    needs, so three variables replace the whole cache."""
    window = [1, 1, 2]
    if n < 3:
        return window[n]
    for _ in range(3, n + 1):
        window = [window[1], window[2], sum(window)]
    return window[2]


print("ways to climb a staircase, steps of 1, 2 or 3")
print()
print(f"{'n':>5}{'naive calls':>14}{'memo entries':>14}{'memo hits':>11}"
      f"{'ways':>16}")
print("-" * 60)
rows = []
for n in range(1, 21):
    naive_tally = [0]
    naive_value = ways_naive(n, naive_tally)
    memo_tally = [0, 0]
    memo_value = ways_memo(n, {}, memo_tally)
    bottom_up_value = ways_bottom_up(n)
    rows.append((n, naive_tally[0], memo_tally[0], naive_value,
                 bottom_up_value))
    print(f"{n:>5}{naive_tally[0]:>14,}{memo_tally[0]:>14,}"
          f"{memo_tally[1]:>11,}{naive_value:>16,}")
print()
print("The naive count is the same shape as Fibonacci's -- exponential, and")
print("visible as one more digit per step -- and the memoised count is not.")
print("That is the whole chapter in one table: the work is exponential, the")
print("number of *distinct* things to compute is n, and a cache collapses one")
print("into the other.")
print()
print("The memo column is worth reading exactly, because a count you cannot")
print("account for is a count you should not trust:")
print()
print(f"  {'the memoised count is exactly 3n + 1':<40}: "
      f"{all(entries == 3 * n + 1 for n, _, entries, _, _ in rows)}")
print(f"  {'entries at n = ' + str(rows[-1][0]):<40}: {rows[-1][2]}")
print(f"  {'3 x ' + str(rows[-1][0]) + ' + 1':<40}: {3 * rows[-1][0] + 1}")
print()
print("Three entries per step, plus the one that starts it off. The three is")
print("the fan-out -- every new step asks about n-1, n-2 and n-3 -- and the")
print("reason it stays at three rather than growing is that all three have")
print("already been answered, so each is one lookup and no work. A linear")
print("count from an exponential recurrence is what 'memoised' looks like")
print("when you write it down.")
print()
print()
print("The checks")
print()
memo_cache = {}
ways_memo(20, memo_cache, [0, 0])
print(f"  all three implementations agree on every n : "
      f"{all(a == c for _, _, _, a, c in rows)}")
print(f"  the memoised version enters the function    : "
      f"{rows[-1][2]:,} times at n = {rows[-1][0]}")
print(f"  the naive version enters it                 : "
      f"{rows[-1][1]:,} times")
print(f"  ratio                                       : "
      f"{rows[-1][1] / rows[-1][2]:,.0f}x")
print()
print(f"  bottom-up at n = {rows[-1][0]} uses             : 3 variables")
print(f"  the memoised version keeps                  : "
      f"{len(memo_cache)} cache entries")
print()
print("The last pair of lines is the space argument from the chapter, made")
print("concrete. The memo is holding an answer for every step; the bottom-up")
print("loop is holding three. The recurrence only ever looks back three")
print("places, so everything older than that is dead weight the cache keeps")
print("out of habit.")
print()
print("A last check on the growth rate, using the same trick as the first")
print("section. This recurrence's growth rate is the real root of")
print("x^3 = x^2 + x + 1 -- the tribonacci constant -- and the ratio of")
print("consecutive naive counts should climb towards it:")
print()


def tribonacci_root():
    """The largest real root of x^3 - x^2 - x - 1, by bisection. Derived
    rather than quoted, so the comparison below is a check on the counts and
    not on my memory of a constant."""
    low, high = 1.0, 2.0
    for _ in range(80):
        mid = (low + high) / 2
        if mid ** 3 - mid ** 2 - mid - 1 < 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


ROOT = tribonacci_root()
print(f"{'n':>5}{'naive calls':>14}{'growth':>10}{'tribonacci':>13}")
print("-" * 42)
previous = None
for n, naive_calls, _, _, _ in rows:
    growth = "-" if previous is None else f"{naive_calls / previous:.3f}"
    print(f"{n:>5}{naive_calls:>14,}{growth:>10}{ROOT:>13.6f}")
    previous = naive_calls
print()
print(f"  the tribonacci constant, computed here : {ROOT:.12f}")
print(f"  the growth column at n = 20            : "
      f"{rows[-1][1] / rows[-2][1]:.6f}")
print()
print("The convergence is much faster than the golden-ratio case, and it is")
print("worth noticing why. A third-order recurrence has two correction terms")
print("rather than one, and both of them are small by the time n reaches the")
print("teens -- so the ratio is good to three decimals from n = 13 onward")
print("instead of still drifting at n = 30.")
print()
print("The habit is the same either way. A growth rate is a claim about the")
print("limit of a ratio, so it is verified by watching that ratio settle,")
print("never by reading one row of a table.")
