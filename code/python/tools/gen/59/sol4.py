"""Solution 4 -- a key that does not name everything.

A cached value derived from two arguments, keyed on one. The count is of
answers computed for the wrong arguments, and then of stale reads once the
key is widened and the invalidation has to follow it.
"""

REGIONS = 4
CHANNELS = 3
ROUNDS = 3
CALLS = REGIONS * CHANNELS * ROUNDS


def total(region, channel):
    return (region + 1) * 10 + channel


def on_the_region(region, channel, cache):
    """The key names the argument that looks important."""
    if region not in cache:
        cache[region] = total(region, channel)
    return cache[region]


def on_both(region, channel, cache):
    if (region, channel) not in cache:
        cache[(region, channel)] = total(region, channel)
    return cache[(region, channel)]


DESIGNS = [
    ("the region alone", on_the_region),
    ("the region and the channel", on_both),
]


def sequence():
    out = []
    for _round in range(ROUNDS):
        for region in range(REGIONS):
            for channel in range(CHANNELS):
                out.append((region, channel))
    return out


def main():
    ops = sequence()
    print(f"  regions                             {REGIONS}")
    print(f"  channels                            {CHANNELS}")
    print(f"  calls                               {CALLS}")
    print()
    print("    what the key names           misses   hits   wrong")
    results = {}
    for name, design in DESIGNS:
        cache = {}
        misses = 0
        hits = 0
        wrong = 0
        for region, channel in ops:
            before = len(cache)
            value = design(region, channel, cache)
            if len(cache) > before:
                misses += 1
            else:
                hits += 1
            if value != total(region, channel):
                wrong += 1
        results[name] = (misses, hits, wrong)
        print("    {:<27}{:>8}{:>7}{:>8}".format(name, misses, hits, wrong))
    print()

    narrow = results["the region alone"]
    wide = results["the region and the channel"]
    print(f"  the construction that finds the bug is the one worth writing down.")
    print(f"  Take two calls that differ only in the argument the key does not")
    print(f"  name, and check whether they produce the same key and different")
    print(f"  values. Here `total(0, 0)` is 10 and `total(0, 1)` is 11, both key")
    print(f"  on region 0, and the second call is served the first one's answer.")
    print()
    print(f"  that is {narrow[2]} wrong answers out of {CALLS}, from a cache with a hit rate of")
    print(f"  {100.0 * narrow[1] / CALLS:.1f}%. The wider key gets {wide[2]} wrong answers and a hit rate of")
    print(f"  {100.0 * wide[1] / CALLS:.1f}%.")
    print()
    print(f"  the second half of the exercise is the invalidation, because")
    print(f"  widening a key widens what has to be dropped. `on_the_region` could")
    print(f"  be invalidated by dropping one entry per region. `on_both` needs one")
    print(f"  entry dropped per region per channel, and a write that changes a")
    print(f"  region has to drop all {CHANNELS} of them.")
    print()
    print(f"  so the key and the invalidation are the same statement written")
    print(f"  twice. A key says what the value depends on, and an invalidation")
    print(f"  has to reach every key that statement covers. A cache where those")
    print(f"  two lists disagree is a cache with stale reads, and the count of")
    print(f"  wrong answers above is the size of the disagreement.")


main()
