"""Chapter 59 -- a hit rate is not the thing a cache is for.

Two caches over two functions with very different costs. The count is of
the work removed, and the cache with the better hit rate removes less.
"""

CALLS = 100
CHEAP_UNITS = 2
EXPENSIVE_UNITS = 100

CACHES = [
    ("a cheap call, cached well", CHEAP_UNITS, 90),
    ("an expensive call, cached badly", EXPENSIVE_UNITS, 40),
]


def main():
    print(f"  calls per cache                     {CALLS}")
    print()
    print("    {:<28}{:>9}{:>13}{:>15}{:>11}".format(
        "the cache", "hit rate", "units/call", "work removed", "per call"))
    rows = []
    for name, units, hits in CACHES:
        misses = CALLS - hits
        without = CALLS * units
        with_cache = misses * units
        removed = without - with_cache
        rows.append((name, hits, units, removed, without))
        print("    {:<28}{:>9}{:>13}{:>15}{:>11.1f}".format(
            name, "%d%%" % hits, units, removed, removed / CALLS))
    print()

    good = rows[0]
    bad = rows[1]
    print(f"  the first cache has a hit rate of {good[1]}% and the second of {bad[1]}%.")
    print(f"  The second removes {bad[3] / good[3]:.1f} times as much work.")
    print()
    print(f"  the arithmetic is not subtle and it is worth saying out loud. A")
    print(f"  hit saves the cost of one call, so the work a cache removes is the")
    print(f"  hit count multiplied by the cost of the thing being cached. The")
    print(f"  hit rate is one factor of two, and it is the one everybody quotes")
    print(f"  because it is the one the cache can report about itself.")
    print()
    print(f"  that is the shape of the mistake. `lru_cache` will tell you its own")
    print(f"  hit rate and it cannot tell you what a call costs, so the number it")
    print(f"  offers is the number that gets optimised. A cache in front of a")
    print(f"  function that costs two units is a data structure that saves you")
    print(f"  {good[3]} units out of {good[4]}, and it costs a dictionary, an eviction policy")
    print(f"  and a place where staleness can happen.")
    print()
    print(f"  so the number to take before adding a cache is not the hit rate. It")
    print(f"  is the cost of a miss, and the two of them together. The hit rate")
    print(f"  is a measurement of the cache. The work removed is a measurement of")
    print(f"  the program, and only one of those is the question.")


main()
