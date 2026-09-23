"""Solution 3 -- what a memo does to the work and to the peak.

The same function called over the same inputs with and without a cache.
The count is of the work the function does, of the calls that miss, and of
the entries held at once.
"""

from collections import Counter

INPUTS = list(range(20))
CALL_KEYS = INPUTS + INPUTS[:12]
CALLS = len(CALL_KEYS)
REPEATED = sum(1 for _key, times in Counter(CALL_KEYS).items() if times > 1)


def expensive(key, count):
    count["work"] += 1
    total = 0
    for i in range(key % 7 + 1):
        count["work"] += 1
        total += i
    return total


def without_memo(keys, count):
    out = []
    for key in keys:
        out.append(expensive(key, count))
    return out


def with_memo(keys, count):
    cache = {}
    out = []
    for key in keys:
        if key not in cache:
            count["misses"] += 1
            cache[key] = expensive(key, count)
        count["peak"] = max(count["peak"], len(cache))
        out.append(cache[key])
    return out


WAYS = [
    ("no memo", without_memo),
    ("a memo", with_memo),
]


def main():
    print(f"  calls                               {CALLS}")
    print(f"  distinct inputs                     {len(INPUTS)}")
    print()
    print("    how it is called        work units   misses   entries held")
    rows = []
    for name, way in WAYS:
        count = {"work": 0, "misses": 0, "peak": 0}
        results = way(CALL_KEYS, count)
        rows.append((name, count["work"], count["misses"], count["peak"],
                     results))
    for name, work, misses, peak, _results in rows:
        print("    {:<22}{:>11}{:>9}{:>15}".format(name, work, misses, peak))
    print()

    same = len(set(tuple(row[4]) for row in rows)) == 1
    print("    the two return the same list          {}".format(
        "yes" if same else "no"))
    print()

    plain = rows[0]
    memo = rows[1]
    saved = plain[1] - memo[1]
    print(f"  the memo removes {saved} of the {plain[1]} units, which is")
    print(f"  {100.0 * saved / plain[1]:.1f}%, and it does that by remembering {memo[3]} answers.")
    print()
    print("  the column that got worse is the last one. The plain version")
    print(f"  holds nothing between calls; the memo holds {memo[3]} entries at its")
    print(f"  peak, and {REPEATED} of them are answers to questions the caller asked")
    print("  more than once.")
    print()
    print("  that trade is the whole of caching. The count of misses is the")
    print(f"  number to read first: {memo[2]} misses for {CALLS} calls is a hit rate of")
    print(f"  {100.0 * (CALLS - memo[2]) / CALLS:.1f}%, and a hit rate is what decides whether a")
    print("  cache is worth its memory.")
    print()
    print("  two things follow that these numbers do not show. A cache is only")
    print("  correct if the function is pure, because the second caller gets")
    print("  the first caller's answer; and it is only bounded if something")
    print("  evicts, because the entries held grows with the number of distinct")
    print("  inputs rather than with the number of calls. Here there are")
    print(f"  {len(INPUTS)} distinct inputs; with a million inputs the peak is a million.")
    print()
    print("  so the two counts to take before adding a memo are how many of")
    print("  the calls repeat and how many distinct keys there are. The first")
    print("  is the saving and the second is the cost.")


main()
