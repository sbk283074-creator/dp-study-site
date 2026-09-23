"""Chapter 59 -- the hit rate, and what it is a property of.

The same function behind the same cache, called over two access patterns.
The count is of hits and misses, and the two patterns disagree about
whether the cache was worth writing.
"""

from functools import lru_cache

KEYS = 1000
CALLS = 1000
UNITS = 6

WORK = [0]


def uniform(i):
    """A deterministic value in [0, 1) that does not repeat quickly. The
    mixing matters, because a weak generator would give the two patterns
    below the same set of keys by accident."""
    state = (i + 1) * 2654435761 % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) / 4294967296.0


def pattern_heavy(i):
    """One very hot key and a long tail: the share of the space a call lands
    in is raised to the twenty-fourth power, so most calls land on the first
    few keys."""
    return int(KEYS * uniform(i) ** 24)


def pattern_flat(i):
    """Every key in the space equally likely."""
    return int(KEYS * uniform(i))


@lru_cache(maxsize=None)
def compute(key):
    WORK[0] += 1
    total = 0
    for i in range(UNITS - 1):
        WORK[0] += 1
        total += key * i
    return total


PATTERNS = [
    ("a few keys, often", pattern_heavy),
    ("every key equally", pattern_flat),
]


def run(pattern):
    compute.cache_clear()
    WORK[0] = 0
    keys = [pattern(i) for i in range(CALLS)]
    for key in keys:
        compute(key)
    info = compute.cache_info()
    return {
        "hits": info.hits,
        "misses": info.misses,
        "work": WORK[0],
        "distinct": len(set(keys)),
    }


def main():
    print(f"  keys in the space                   {KEYS}")
    print(f"  calls                               {CALLS}")
    print(f"  work units per computation          {UNITS}")
    print()
    print("    access pattern        distinct keys   hits   misses   hit rate")
    results = {}
    for name, pattern in PATTERNS:
        result = run(pattern)
        results[name] = result
        rate = 100.0 * result["hits"] / CALLS
        print("    {:<22}{:>14}{:>7}{:>9}{:>10.1f}%".format(
            name, result["distinct"], result["hits"], result["misses"], rate))
    print()

    heavy = results["a few keys, often"]
    flat = results["every key equally"]
    print("  the function, the cache and the number of calls are the same in")
    print("  both rows. The heavy-tailed pattern got a hit rate of")
    print(f"  {100.0 * heavy['hits'] / CALLS:.1f}% and the flat one got {100.0 * flat['hits'] / CALLS:.1f}%.")
    print()
    print("  the misses are the number of distinct keys and nothing else. The")
    print(f"  heavy pattern reached {heavy['distinct']} of the {KEYS} keys in the space and the")
    print(f"  flat one reached {flat['distinct']}, so the flat pattern asked for")
    print(f"  {flat['distinct'] / heavy['distinct']:.1f} times as many different things. A cache does not")
    print("  make a function cheaper. It makes a repeat cheaper, and how many")
    print("  repeats there are is a property of the caller rather than of the")
    print("  function.")
    print()
    print("  the work is the other half of the same fact. Without a cache both")
    print(f"  patterns cost {CALLS * UNITS} units, because both call the function {CALLS}")
    print(f"  times. With one, the heavy pattern costs {heavy['work']} and the flat one")
    print(f"  {flat['work']}.")
    print()
    print("  so the first question about a cache is not which cache. It is how")
    print("  often the same question is asked twice, and that is a number you")
    print("  can count before writing any of it.")


main()
