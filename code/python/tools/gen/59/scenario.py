"""Chapter 59 -- the scenario. A read-heavy service with four workers.

Four designs for the cache: none, one per worker, one shared, and one per
worker with the invalidation published to all of them. The count is of
store reads, of reads served from a cache, and of stale reads.
"""

KEYS = 50
WORKERS = 4
OPS = 1000
WRITE_EVERY = 20


def mix(state):
    """A deterministic value in [0, 1)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) / 4294967296.0


def operations():
    """Reads and writes, with a write every twentieth operation."""
    out = []
    state = 3
    for index in range(OPS):
        state += 1
        key = int(KEYS * mix(state))
        kind = "write" if index % WRITE_EVERY == 0 else "read"
        out.append((kind, key, index % WORKERS))
    return out


class Store:
    """The slow thing. Every call into it is counted."""

    def __init__(self, count):
        self.data = {key: 0 for key in range(KEYS)}
        self.count = count

    def load(self, key):
        self.count["store_reads"] += 1
        return self.data[key]

    def save(self, key, value):
        self.count["store_writes"] += 1
        self.data[key] = value


def serve(cache, key, store, count):
    if key in cache:
        count["cached"] += 1
        value = cache[key]
    else:
        value = store.load(key)
        cache[key] = value
    if value != store.data[key]:
        count["stale"] += 1
    return value


def no_cache(ops, count):
    store = Store(count)
    for kind, key, _worker in ops:
        if kind == "read":
            store.load(key)
        else:
            store.save(key, store.data[key] + 1)
    return 0


def per_worker(ops, count):
    """Each worker keeps its own cache, and a write clears only its own."""
    store = Store(count)
    caches = {worker: {} for worker in range(WORKERS)}
    for kind, key, worker in ops:
        if kind == "read":
            serve(caches[worker], key, store, count)
        else:
            store.save(key, store.data[key] + 1)
            caches[worker].pop(key, None)
    return sum(len(cache) for cache in caches.values())


def shared(ops, count):
    """One cache, and a write clears it."""
    store = Store(count)
    cache = {}
    for kind, key, _worker in ops:
        if kind == "read":
            serve(cache, key, store, count)
        else:
            store.save(key, store.data[key] + 1)
            cache.pop(key, None)
    return len(cache)


def per_worker_published(ops, count):
    """Each worker keeps its own cache, and a write tells all of them."""
    store = Store(count)
    caches = {worker: {} for worker in range(WORKERS)}
    for kind, key, worker in ops:
        if kind == "read":
            serve(caches[worker], key, store, count)
        else:
            store.save(key, store.data[key] + 1)
            for cache in caches.values():
                cache.pop(key, None)
    return sum(len(cache) for cache in caches.values())


DESIGNS = [
    ("no cache", no_cache),
    ("one per worker", per_worker),
    ("one shared", shared),
    ("per worker, published", per_worker_published),
]


def main():
    ops = operations()
    reads = sum(1 for kind, _key, _worker in ops if kind == "read")
    print(f"  keys                                {KEYS}")
    print(f"  workers                             {WORKERS}")
    print(f"  operations                          {OPS}")
    print(f"  of which reads                      {reads}")
    print()
    print("    design                 store reads   from cache   stale reads   entries")
    results = {}
    for name, design in DESIGNS:
        count = {"store_reads": 0, "store_writes": 0, "cached": 0, "stale": 0}
        held = design(ops, count)
        results[name] = (count["store_reads"], count["cached"], count["stale"],
                         held)
        print("    {:<23}{:>11}{:>13}{:>14}{:>10}".format(
            name, count["store_reads"], count["cached"], count["stale"],
            held))
    print()

    plain = results["no cache"]
    worker = results["one per worker"]
    one = results["one shared"]
    published = results["per worker, published"]
    print(f"  the first row is the prize. Reading the store {plain[0]} times is what the")
    print(f"  cache is there to avoid, and everything below it is a fraction of")
    print(f"  that.")
    print()
    print(f"  one cache per worker is the design to look at first, and it fails")
    print(f"  on both counts. It does {worker[0]} store reads, against {one[0]} for a single")
    print(f"  shared cache, and {worker[2]} of its reads returned a value the store no longer")
    print(f"  had. A write clears the writing worker's copy and leaves the other")
    print(f"  three serving the old value, and nothing raises.")
    print()
    print(f"  one shared cache is correct and is the cheapest of the four, at {one[0]}")
    print(f"  store reads. Its cost is not in this table: it throws the whole cache")
    print(f"  away on every write when one key was what changed, and it is the")
    print(f"  design that every worker contends on.")
    print()
    print(f"  the last row is the per-worker design with the invalidation")
    print(f"  published to every worker. It is correct -- {published[2]} stale reads -- and it")
    print(f"  costs {published[0]} store reads, which is {published[0] / one[0]:.1f} times the shared cache.")
    print(f"  Four private copies mean a write invalidates four entries instead of")
    print(f"  one, and every worker that held the key has to fetch it again.")
    print()
    print(f"  so the table argues against private caches rather than for them, and")
    print(f"  it does so on the count that matters. The stale version is wrong; the")
    print(f"  correct version is more expensive than not having private copies at")
    print(f"  all. The difference between the two is whether the invalidation")
    print(f"  reaches every copy, and the difference between the correct version")
    print(f"  and the shared cache is how many copies there are.")
    print()
    print(f"  that is the whole chapter in one table. What separates the four rows")
    print(f"  is not the cache, the key, the size or the eviction policy. It is")
    print(f"  how many copies of an entry exist and whether a write reaches all of")
    print(f"  them -- and the only way to know is to count stale reads, which no")
    print(f"  cache reports about itself.")


main()
