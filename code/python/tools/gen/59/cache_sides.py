"""Chapter 59 -- three places to put the write.

Cache-aside, write-through and write-behind over the same interleaved read
and write sequence. The count is of store operations and of reads that
would get a different answer from the store than from the cache.
"""

KEYS = 20
WRITE_KEYS = 6
READS = 200
WRITES = 40
FLUSH_EVERY = 12


def read_sequence():
    out = []
    state = 7
    for _ in range(READS):
        state = (state * 1103515245 + 12345) % 2147483648
        out.append(state % KEYS)
    return out


def write_sequence():
    """The writes only ever touch the first few keys, which is what lets a
    write-behind cache batch them."""
    out = []
    state = 99
    for _ in range(WRITES):
        state = (state * 1103515245 + 12345) % 2147483648
        out.append(state % WRITE_KEYS)
    return out


def operations():
    """Reads and writes interleaved, so that a write can be seen by a later
    read. One write every sixth operation."""
    reads = read_sequence()
    writes = write_sequence()
    out = []
    read_at = 0
    write_at = 0
    for index in range(READS + WRITES):
        if index % 6 == 5 and write_at < WRITES:
            out.append(("write", writes[write_at]))
            write_at += 1
        elif read_at < READS:
            out.append(("read", reads[read_at]))
            read_at += 1
        else:
            out.append(("write", writes[write_at]))
            write_at += 1
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


def note_read(cache, key, store, count):
    if key in cache:
        count["hits"] += 1
        value = cache[key]
    else:
        count["misses"] += 1
        value = store.load(key)
        cache[key] = value
    if value != store.data[key]:
        count["disagree"] += 1


def cache_aside(ops, count):
    """On a write, write the store and drop the key."""
    store = Store(count)
    cache = {}
    for kind, key in ops:
        if kind == "read":
            note_read(cache, key, store, count)
        else:
            store.save(key, store.data[key] + 1)
            cache.pop(key, None)
    return len(cache)


def write_through(ops, count):
    """On a write, write both."""
    store = Store(count)
    cache = {}
    for kind, key in ops:
        if kind == "read":
            note_read(cache, key, store, count)
        else:
            store.save(key, store.data[key] + 1)
            cache[key] = store.data[key]
    return len(cache)


def write_behind(ops, count):
    """On a write, write the cache; the store catches up every so often."""
    store = Store(count)
    cache = {}
    pending = {}
    for kind, key in ops:
        if kind == "read":
            note_read(cache, key, store, count)
        else:
            value = cache.get(key, store.data[key]) + 1
            cache[key] = value
            pending[key] = value
            if len(pending) >= FLUSH_EVERY:
                for flush_key in sorted(pending):
                    store.save(flush_key, pending[flush_key])
                pending.clear()
                count["flushes"] += 1
    if pending:
        for flush_key in sorted(pending):
            store.save(flush_key, pending[flush_key])
        count["flushes"] += 1
    return len(cache)


DESIGNS = [
    ("cache-aside", cache_aside),
    ("write-through", write_through),
    ("write-behind", write_behind),
]


def main():
    ops = operations()
    print(f"  keys                                {KEYS}")
    print(f"  keys ever written to                {WRITE_KEYS}")
    print(f"  reads                               {sum(1 for k, _ in ops if k == 'read')}")
    print(f"  writes                              {sum(1 for k, _ in ops if k == 'write')}")
    print(f"  flush after this many dirty keys    {FLUSH_EVERY}")
    print()
    print("    design          store reads   store writes   hits   misses   disagree")
    results = {}
    for name, design in DESIGNS:
        count = {"store_reads": 0, "store_writes": 0, "hits": 0, "misses": 0,
                 "disagree": 0, "flushes": 0}
        held = design(ops, count)
        count["held"] = held
        results[name] = count
        print("    {:<15}{:>12}{:>15}{:>7}{:>9}{:>11}".format(
            name, count["store_reads"], count["store_writes"], count["hits"],
            count["misses"], count["disagree"]))
    print()

    aside = results["cache-aside"]
    through = results["write-through"]
    behind = results["write-behind"]
    print(f"  the three designs read the same sequence and produce the same")
    print(f"  answers. They differ in what the store was asked to do and in how")
    print(f"  often the cache and the store would disagree.")
    print()
    print(f"  cache-aside did {aside['store_reads']} store reads and write-through did")
    print(f"  {through['store_reads']}. The difference is the invalidation: dropping the key")
    print(f"  on a write means the next read of it misses, so the store is read")
    print(f"  {aside['store_reads'] - through['store_reads']} more times to fetch a value the cache had.")
    print()
    flushes = behind["flushes"]
    plural = "flush" if flushes == 1 else "flushes"
    print(f"  write-behind did {behind['store_writes']} store writes in {flushes} {plural},")
    print(f"  against {through['store_writes']} for the other two, and it is the only design")
    print(f"  with a disagreement count above zero: {behind['disagree']} reads got an answer")
    print("  the store did not have yet.")
    print()
    print(f"  the {behind['store_writes']} is not a rounding of {through['store_writes']} and it is not the")
    print(f"  number of writes either. The flush threshold is {FLUSH_EVERY} dirty keys and the")
    print(f"  writes only ever touch {WRITE_KEYS} of the {KEYS} keys, so the batch never reaches")
    print("  the threshold and the store is written once, at the end. A write-behind")
    print("  cache's store traffic is a function of how many distinct keys are dirty")
    print("  at the same moment, which is a property of the workload rather than of")
    print("  the design -- and it is the number to count before choosing one.")
    print()
    print("  that is the whole trade, and it is the same trade at every level")
    print("  of this chapter. Writing to both places keeps them in step and")
    print("  costs a store write per write. Writing to one and catching up")
    print("  later costs fewer store writes and buys a window in which two")
    print("  readers of the same key get different answers.")
    print()
    print(f"  the counts do not say which to choose. They say what the choice")
    print(f"  costs: {behind['store_writes']} store writes against {through['store_writes']}, and")
    print(f"  {behind['disagree']} disagreements against none. A disagreement count of zero")
    print("  is only achievable by writing both, and that is a fact about the")
    print("  design rather than a fact about how careful the code is.")


main()
