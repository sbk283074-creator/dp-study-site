"""Solution 1 -- is the cache worth its memory?

One function, two access logs, and the three counts that decide: the hit
rate, the work removed, and the entries held at the end.
"""

KEYS = 400
CALLS = 400
UNITS = 30
SIZE = 50
WORTH = 25.0


def mix(state):
    """A deterministic value in [0, 1)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) / 4294967296.0


def log_flat():
    return [int(KEYS * mix(i + 1)) for i in range(CALLS)]


def log_skewed():
    return [int(KEYS * mix(i + 1) ** 6) for i in range(CALLS)]


LOGS = [
    ("every key equally", log_flat),
    ("a few keys, often", log_skewed),
]


def run(keys):
    """A bounded cache, counting what it saved and what it holds."""
    cache = {}
    order = []
    count = {"hits": 0, "misses": 0}
    for key in keys:
        if key in cache:
            count["hits"] += 1
        else:
            count["misses"] += 1
            if len(cache) >= SIZE:
                del cache[order.pop(0)]
            cache[key] = True
            order.append(key)
    return count, len(cache)


def main():
    print(f"  keys in the space                   {KEYS}")
    print(f"  calls                               {CALLS}")
    print(f"  units per call                      {UNITS}")
    print(f"  cache size                          {SIZE}")
    print(f"  worth it above                      {WORTH:.0f}% of the work")
    print()
    print("    access log           hit rate   work removed   entries held   verdict")
    results = {}
    for name, make in LOGS:
        count, held = run(make())
        removed = count["hits"] * UNITS
        rate = 100.0 * count["hits"] / CALLS
        share = 100.0 * removed / (CALLS * UNITS)
        worth = "worth it" if share > WORTH else "not worth it"
        results[name] = (rate, removed, held, worth, share)
        print("    {:<20}{:>8.1f}%{:>15}{:>15}   {}".format(
            name, rate, removed, held, worth))
    print()

    flat = results["every key equally"]
    skewed = results["a few keys, often"]
    print(f"  the function, the cache and the cache size are the same in both")
    print(f"  rows. The skewed log has a hit rate of {skewed[0]:.1f}% and removes")
    print(f"  {skewed[1]} units; the flat log has {flat[0]:.1f}% and removes {flat[1]}.")
    print()
    print(f"  the number that decides is the work removed, and it is the hit")
    print(f"  count multiplied by the cost of a miss. A hit rate on its own says")
    print(f"  nothing about whether the cache paid for itself, because a hit on a")
    print(f"  function that costs nothing is worth nothing.")
    print()
    print(f"  the entries held is the other half of the decision, and it is the")
    print(f"  half that does not shrink when the cache is ineffective. Both rows")
    print(f"  hold {SIZE} entries, because that is the bound -- so the cache costs the same")
    print(f"  memory in the log where it removes {skewed[1]} units and in the log where")
    print(f"  it removes {flat[1]}.")
    print()
    print(f"  so the three counts to take before adding a cache are the hit rate,")
    print(f"  the cost of a miss, and the number of entries. The first two")
    print(f"  multiply into the saving and the third is what the cache costs")
    print(f"  whether it saves anything or not. Here the flat log removes")
    print(f"  {flat[4]:.1f}% of the work, which is exactly its hit rate and not enough to")
    print(f"  justify the memory; the skewed log removes {skewed[4]:.1f}%, which is.")


main()
