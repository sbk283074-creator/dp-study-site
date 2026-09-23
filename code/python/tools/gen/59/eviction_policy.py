"""Chapter 59 -- the eviction policy is a measurement, not a detail.

Four policies over a cyclic scan. The count is of hits, and the policy with
the best reputation does worst.
"""

KEYS = 200
PASSES = 2
SIZE = 50


def accesses():
    out = []
    for _ in range(PASSES):
        out.extend(range(KEYS))
    return out


def lru(ops, count):
    """The entry used longest ago goes."""
    cache = {}
    order = []
    for key in ops:
        if key in cache:
            count["hits"] += 1
            order.remove(key)
            order.append(key)
        else:
            count["misses"] += 1
            if len(cache) >= SIZE:
                del cache[order.pop(0)]
            cache[key] = True
            order.append(key)
    return len(cache)


def fifo(ops, count):
    """The entry inserted first goes."""
    cache = {}
    order = []
    for key in ops:
        if key in cache:
            count["hits"] += 1
        else:
            count["misses"] += 1
            if len(cache) >= SIZE:
                del cache[order.pop(0)]
            cache[key] = True
            order.append(key)
    return len(cache)


def mix(state):
    """A deterministic value in [0, 1). The high bits matter: a generator
    whose low bits are used to index a list of fifty entries would evict
    almost the same entry every time, and the policy would look far worse
    than a random one actually is."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) / 4294967296.0


def random_replacement(ops, count):
    """Any entry goes, chosen by a fixed sequence."""
    cache = {}
    order = []
    state = 5
    for key in ops:
        if key in cache:
            count["hits"] += 1
        else:
            count["misses"] += 1
            if len(cache) >= SIZE:
                state += 1
                victim = order[int(len(order) * mix(state))]
                order.remove(victim)
                del cache[victim]
            cache[key] = True
            order.append(key)
    return len(cache)


def unbounded(ops, count):
    """Nothing goes."""
    cache = {}
    for key in ops:
        if key in cache:
            count["hits"] += 1
        else:
            count["misses"] += 1
            cache[key] = True
    return len(cache)


POLICIES = [
    ("least recently used", lru),
    ("first in, first out", fifo),
    ("any entry at all", random_replacement),
    ("nothing is evicted", unbounded),
]


def main():
    ops = accesses()
    print(f"  keys                                {KEYS}")
    print(f"  cache size                          {SIZE}")
    print(f"  accesses                            {len(ops)}")
    print(f"  the access pattern is 0..{KEYS - 1}, twice")
    print()
    print("    eviction policy            hits   misses   hit rate   entries held")
    results = {}
    for name, policy in POLICIES:
        count = {"hits": 0, "misses": 0}
        held = policy(ops, count)
        results[name] = (count["hits"], count["misses"], held)
        rate = 100.0 * count["hits"] / len(ops)
        print("    {:<26}{:>5}{:>9}{:>11.1f}%{:>15}".format(
            name, count["hits"], count["misses"], rate, held))
    print()

    lru_hits = results["least recently used"][0]
    fifo_hits = results["first in, first out"][0]
    random_hits = results["any entry at all"][0]
    all_hits = results["nothing is evicted"][0]
    print("  the access pattern is the one every cache is worst at, and every")
    print("  bounded policy fails it. Least recently used got")
    print(f"  {lru_hits} hits out of {len(ops)}, first in, first out got {fifo_hits}, and choosing a")
    print(f"  victim at random got {random_hits}.")
    print()
    print(f"  the reason is one line long. The cache holds {SIZE} entries and the scan")
    print(f"  walks {KEYS}, so by the time the scan comes back to a key that key was")
    print(f"  evicted {KEYS - SIZE} accesses ago -- and least recently used evicts exactly")
    print("  the entry it is about to be asked for.")
    print()
    print("  random replacement is the policy with no claim at all about the")
    print(f"  access pattern, and it beats the policy with the strongest claim by")
    print(f"  {random_hits} accesses out of {len(ops)}. That difference is tiny, and the number")
    print(f"  beside it is the one to read: not evicting at all gets {all_hits}.")
    print()
    print(f"  so the spread across the three bounded policies is")
    print(f"  {100.0 * (random_hits - lru_hits) / len(ops):.1f} percentage points, and the spread between any")
    print(f"  bounded policy and keeping everything is {100.0 * (all_hits - random_hits) / len(ops):.1f}. On a scan the")
    print("  eviction policy is not what is losing the hits, and tuning it is")
    print("  tuning the wrong thing.")
    print()
    print("  the fix for a scan is therefore not a better policy. It is a")
    print("  different shape: either bound nothing, or let the caller mark an")
    print("  access as one that will not be repeated. Both are changes to what")
    print("  the cache is rather than to how it chooses.")


main()
