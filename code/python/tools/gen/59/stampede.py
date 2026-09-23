"""Chapter 59 -- the stampede.

Callers that arrive together at a key the cache does not hold. The count is
of how many of them recompute the same answer.
"""

CALLERS = 50
WIDE_KEYS = 10
UNITS = 4

WORK = [0]


def compute(key):
    WORK[0] += 1
    total = 0
    for i in range(UNITS - 1):
        WORK[0] += 1
        total += key * i
    return total


def plain(callers, count):
    """Every caller reads the cache before any of them fills it, so every
    caller finds it empty and every caller computes."""
    for key in callers:
        count["compute"] += 1
        compute(key)
    count["cache"].update({key: True for key in callers})
    return count


def single_flight(callers, count):
    """One caller per key computes; the rest wait for that caller's result."""
    in_flight = set()
    for key in callers:
        if key in count["cache"]:
            count["hit"] += 1
        elif key in in_flight:
            count["waited"] += 1
        else:
            count["compute"] += 1
            in_flight.add(key)
            compute(key)
    count["cache"].update({key: True for key in callers})
    return count


DESIGNS = [
    ("no protection", plain),
    ("single flight", single_flight),
]


def table(label, callers):
    print(f"    {label}")
    print("    {:<18}{:>10}{:>12}{:>10}{:>9}".format(
        "design", "computed", "duplicates", "hits", "work"))
    distinct = len(set(callers))
    rows = {}
    for name, design in DESIGNS:
        WORK[0] = 0
        count = {"compute": 0, "hit": 0, "waited": 0, "cache": {}}
        design(callers, count)
        rows[name] = (count["compute"], count["compute"] - distinct,
                      count["hit"], WORK[0])
        print("    {:<18}{:>10}{:>12}{:>10}{:>9}".format(
            name, count["compute"], count["compute"] - distinct,
            count["hit"], WORK[0]))
    print()
    return rows


def main():
    print(f"  callers                             {CALLERS}")
    print()
    print("  A stampede is what happens when a key is missing and every caller")
    print("  that wants it decides to fetch it at the same moment. The first")
    print(f"  table is {CALLERS} callers arriving together for one key.")
    print()
    one = table("all %d callers want one key" % CALLERS, [0] * CALLERS)
    print(f"  The second table is the same {CALLERS} callers spread over {WIDE_KEYS} keys that")
    print("  are all missing. Every caller still arrives before any of them has")
    print("  a result, so every caller still computes.")
    print()
    wide = table("the same callers over %d keys" % WIDE_KEYS,
                 [i % WIDE_KEYS for i in range(CALLERS)])
    print("  the column to read is `duplicates`. It is the number of times the")
    print("  same computation was performed more than once, and removing it is")
    print("  the only thing the cache was there to do.")
    print()
    print(f"  protection removes all of them, in both tables. It removes")
    print(f"  {one['no protection'][1]} duplicates when the callers all want one key and")
    print(f"  {wide['no protection'][1]} when they are spread over {WIDE_KEYS}, so the count scales with")
    print(f"  the number of callers rather than with the number of keys.")
    print()
    print("  neither design is wrong. Both return the correct value to every")
    print("  caller and both leave the cache full at the end. The difference is")
    print("  that one of them does the work once per caller and the other once")
    print("  per key, and no test of the returned values can tell them apart.")
    print()
    print("  that is the cache's version of the measurement problem from the")
    print("  previous chapter. A hit rate is computed after the fact, over all")
    print("  the calls, and a stampede happens inside one instant -- so a cache")
    print("  with an excellent hit rate can still perform the same expensive")
    print("  query fifty times, and the hit rate will not show it.")
    print()
    print("  the fix is a lock held per key rather than one lock for the whole")
    print("  cache, so that callers wanting different keys do not queue behind")
    print("  each other. That is a change of shape rather than of parameters,")
    print("  and the count it removes is the one printed above.")


main()
