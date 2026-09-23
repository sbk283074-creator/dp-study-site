"""Chapter 59 -- the TTL, counted as a staleness bound and a tax.

One key behind a cache, a source that changes on a schedule, and four TTLs.
The count is of loads, of reads that came back with a value the source no
longer had, and of how old the oldest such value was.
"""

TICKS = 400
CHANGE_EVERY = 37
TTLS = [None, 100, 20, 5]


def source_value(tick):
    """The truth. It changes every thirty-seven ticks."""
    return tick // CHANGE_EVERY


def run(ttl):
    count = {"loads": 0, "hits": 0, "stale": 0, "worst": 0}
    cached = None
    cached_at = 0
    for tick in range(TICKS):
        if cached is None or (ttl is not None and tick - cached_at >= ttl):
            cached = source_value(tick)
            cached_at = tick
            count["loads"] += 1
        else:
            count["hits"] += 1
        if cached != source_value(tick):
            count["stale"] += 1
            count["worst"] = max(count["worst"], tick - cached_at)
    return count


def main():
    print(f"  ticks                               {TICKS}")
    print(f"  the source changes every            {CHANGE_EVERY}")
    print()
    print("    ttl      loads   hits   stale reads   worst staleness")
    results = {}
    for ttl in TTLS:
        count = run(ttl)
        results[ttl] = count
        label = "none" if ttl is None else str(ttl)
        print("    {:<9}{:>5}{:>7}{:>14}{:>18}".format(
            label, count["loads"], count["hits"], count["stale"],
            count["worst"]))
    print()

    forever = results[None]
    short = results[5]
    mid = results[20]
    long_ttl = results[100]
    print("  a TTL is two numbers at once and the table prints both. It is a")
    print("  bound on how wrong a read can be, and a tax on how often the")
    print("  source is asked.")
    print()
    print(f"  with no TTL the cache is loaded {forever['loads']} time and is wrong for")
    print(f"  {forever['stale']} of the {TICKS} reads, by up to {forever['worst']} ticks. That is a")
    print("  perfect hit rate on a cache that is useless.")
    print()
    print(f"  at a TTL of {TTLS[-1]} the worst staleness is {short['worst']} ticks and the loads")
    print(f"  rise to {short['loads']}. At {TTLS[2]} it is {mid['worst']} ticks and {mid['loads']} loads, and")
    print(f"  at {TTLS[1]} it is {long_ttl['worst']} ticks and {long_ttl['loads']} loads. The bound is one tick")
    print("  below the TTL in every case, because an entry is still fresh on the")
    print("  tick it is due to expire.")
    print()
    print(f"  the number of stale reads is not a function of the TTL on its own.")
    print(f"  A TTL of {TTLS[-1]} loads {short['loads']} times and leaves {short['stale']} stale reads;")
    print(f"  a TTL of {TTLS[1]} loads {long_ttl['loads']} times and leaves {long_ttl['stale']}. The second is")
    print(f"  {long_ttl['stale'] / short['stale']:.1f} times as many stale reads from {short['loads'] / long_ttl['loads']:.0f} times fewer")
    print(f"  loads, and that relationship comes from how the TTL falls against")
    print(f"  the source's own change period of {CHANGE_EVERY} -- which is not a number the")
    print("  cache controls.")
    print()
    print("  so a TTL is chosen from two facts that live outside the cache: how")
    print("  stale a read is allowed to be, and how often the source changes.")
    print("  The first is a decision. The second is a measurement, and setting a")
    print("  TTL without taking it is how a cache ends up with a staleness bound")
    print("  that is met exactly while the number of bad reads is far worse than")
    print("  the bound suggests.")


main()
