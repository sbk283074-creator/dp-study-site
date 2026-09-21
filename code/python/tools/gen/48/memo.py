#!/usr/bin/env python3
"""Chapter 48 demo -- four ways to write the same recurrence, and the counts
that separate them.

Memoisation is one idea: remember the answer to a subproblem you have already
solved. It can be written by hand with a dict, or supplied by the standard
library as `functools.lru_cache`. Those look like two different techniques and
they are the same algorithm -- which the counts below show, and which is the
reason to prefer the library version.

The last section turns the cache's two documented traps into output rather
than advice.
"""
import functools


def fib_naive(n, tally):
    tally[0] += 1
    if n < 2:
        return n
    return fib_naive(n - 1, tally) + fib_naive(n - 2, tally)


def fib_memo(n, cache, tally):
    """Hand-rolled. Note that the *call* still happens -- the function is
    entered, and the lookup is what saves the work. Note also that the base
    cases return before the cache is ever consulted."""
    tally[0] += 1
    if n < 2:
        return n
    if n in cache:
        tally[1] += 1
        return cache[n]
    result = fib_memo(n - 1, cache, tally) + fib_memo(n - 2, cache, tally)
    cache[n] = result
    return result


@functools.lru_cache(maxsize=None)
def fib_cached(n):
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def fib_bottom_up(n):
    """No recursion, no cache, two variables. The recurrence runs forwards."""
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


N = 30
naive_tally = [0]
naive_value = fib_naive(N, naive_tally)
memo_tally = [0, 0]
memo_cache = {}
memo_value = fib_memo(N, memo_cache, memo_tally)
fib_cached.cache_clear()
cached_value = fib_cached(N)
info = fib_cached.cache_info()
bottom_up_value = fib_bottom_up(N)

print(f"fib({N}) computed four ways")
print()
print(f"{'implementation':<24}{'entries':>10}{'hits':>7}{'cached':>9}{'value':>12}")
print("-" * 62)
print(f"{'naive recursion':<24}{naive_tally[0]:>10,}{'-':>7}{'-':>9}"
      f"{naive_value:>12,}")
print(f"{'dict memo, by hand':<24}{memo_tally[0]:>10,}{memo_tally[1]:>7,}"
      f"{len(memo_cache):>9,}{memo_value:>12,}")
print(f"{'functools.lru_cache':<24}{info.misses + info.hits:>10,}{info.hits:>7,}"
      f"{info.currsize:>9,}{cached_value:>12,}")
print(f"{'bottom-up loop':<24}{0:>10,}{'-':>7}{'-':>9}{bottom_up_value:>12,}")
print()
print(f"  all four agree on the value : "
      f"{naive_value == memo_value == cached_value == bottom_up_value}")
print()
print("The 'entries' column is how many times each function was *entered*, so")
print("it is the only fair comparison in the table. (The zero in the last row")
print("is not a trick: bottom-up is a loop, and a loop is never entered as a")
print("function at all.) The naive version enters")
print(f"{naive_tally[0]:,} times; both cached versions enter it")
print(f"{memo_tally[0]:,} times -- once per distinct subproblem, plus one lookup per")
print("repeat. The tree did not get smaller. It stopped being built.")
print()
print("Note what the hand-rolled version and `lru_cache` have in common: both")
print("still *call* the function on every request. The saving is not in the")
print("calls, it is in the work behind them. That is why a memoised function")
print("must be cheap to enter and must not do anything with a side effect --")
print("the function body is skipped on a hit, so anything in it that is not")
print("part of the return value simply does not happen.")
print()
print()
print("Two small differences between the hand-rolled row and the library row")
print()
print(f"  hits       : hand-rolled {memo_tally[1]:,} vs library {info.hits:,}")
print(f"  cached     : hand-rolled {len(memo_cache):,} vs library {info.currsize:,}")
print()
print("Both come from one line of code. The hand-rolled version checks")
print("`n < 2` and returns *before* it consults the dictionary, so its base")
print("cases are never looked up and never stored. That is why it reports one")
print("fewer hit and holds two fewer entries: fib(0) and fib(1) are simply")
print("not in its cache.")
print()
print("Neither is a bug, and the difference is worth making deliberately.")
print("The cache check costs a dictionary lookup, so short-circuiting the")
print("trivial cases first is usually the right call -- but it means the")
print("cache's own statistics no longer count every repeat.")
print()
print()
print("What each one is still holding when it finishes")
print()
print(f"  {'implementation':<24}{'memory held':>24}")
print("-" * 48)
print(f"  {'naive recursion':<24}{'nothing':>24}")
print(f"  {'dict memo':<24}{f'{len(memo_cache)} cache entries':>24}")
print(f"  {'lru_cache':<24}{f'{info.currsize} cache entries':>24}")
print(f"  {'bottom-up':<24}{'2 integers':>24}")
print()
print("The last row is the one to remember. The recurrence is identical")
print("everywhere in this table; what differs is how much of the past each")
print("version insists on keeping. Bottom-up keeps two numbers, because at")
print("step k the only thing the recurrence can still see is step k-1 and")
print("step k-2 -- everything older has already been folded in.")
print()
print("That is the whole space optimisation, and it is the subject of a later")
print("section. Here it is enough to notice that a cache holding 31 entries")
print("was never necessary for this recurrence; it was just the easy thing to")
print("write.")
print()
print()
print("What the cache is keyed on")
print()
print(f"  cache entries held : {info.currsize}")
print(f"  maxsize            : {info.maxsize} (unbounded)")
print()
print("`lru_cache` builds its key from the arguments tuple, which has two")
print("consequences that bite in practice and neither of which is an error")
print("until it is.")
print()
print("The first is that every argument must be hashable. A list, a dict or a")
print("set cannot be cached, and the failure is a `TypeError` at the call site")
print("rather than at the definition -- so a function that works on a tuple")
print("and fails on a list is the symptom.")
print()
print("The second is that `maxsize=None` means *unbounded*, and an unbounded")
print("cache on a function with many distinct arguments is a memory leak with")
print("a friendly name. This cache holds one entry per integer from 0 to 30,")
print("which is harmless. A cache on `fetch_user(user_id)` holds one entry per")
print("user ever seen.")
print()


@functools.lru_cache(maxsize=None)
def total(items):
    """Sums a sequence. Nothing about it is wrong -- until it is called with
    something the cache cannot key on."""
    return sum(items)


print("The hashability trap, demonstrated rather than described")
print()
print(f"  total((1, 2, 3))   -> {total((1, 2, 3))}")
try:
    total([1, 2, 3])
except TypeError as exc:
    print(f"  total([1, 2, 3])   -> TypeError: {exc}")
print()
print("The definition of `total` never changed and never warned. The error")
print("appears at the call site, on the argument, and the message says")
print("'unhashable' -- which is the whole diagnosis. A tuple works, a list")
print("does not, and the fix is to convert at the boundary rather than to")
print("give up the cache.")
print()


@functools.lru_cache(maxsize=4)
def small_cache(n):
    return n * n


for value in range(10):
    small_cache(value)
before = small_cache.cache_info()
small_cache(0)          # evicted long ago -- this should be a miss
after = small_cache.cache_info()
print("The bound, demonstrated the same way")
print()
print(f"  an lru_cache(maxsize=4) after 10 distinct arguments:")
print(f"    holds {before.currsize} entries, took {before.misses} misses, "
      f"{before.hits} hits")
print()
print(f"  now ask for 0 again, which was the first argument seen:")
print(f"    holds {after.currsize} entries, took {after.misses} misses, "
      f"{after.hits} hits")
print()
print("The second call is a *miss*. That is the eviction working: with a")
print("bound of 4, the cache kept the four most recent arguments (6, 7, 8,")
print("9) and quietly dropped 0. Nothing failed, nothing warned, and the")
print("answer was still correct -- it was just recomputed.")
print()
print("A bounded cache evicts the least-recently-used entry instead of")
print("growing, which turns a leak into a policy. For a pure function of a")
print("small key space the bound is irrelevant -- as the first cache shows,")
print("31 entries is nothing. For anything keyed on user input it is the")
print("difference between a cache and a bug.")
