"""Chapter 59 -- invalidation, which is the hard part.

A cache of twelve entries derived from four sources, and one write. The
count is of entries dropped and of reads that came back with a value the
source no longer had.
"""

SOURCES = 4
FILTERS = 3
READS = 60


def entry_keys():
    out = []
    for source in range(SOURCES):
        for filt in range(FILTERS):
            out.append((source, filt))
    out.append(("summary", None))
    return out


def read_sequence():
    """Sixty reads, weighted so that the summary is read often."""
    keys = entry_keys()
    out = []
    for index in range(READS):
        if index % 4 == 3:
            out.append(("summary", None))
        else:
            out.append(keys[index % (SOURCES * FILTERS)])
    return out


class Source:
    """The four sources and the summary derived from them."""

    def __init__(self):
        self.data = {source: 1 for source in range(SOURCES)}
        self.summary = SOURCES

    def load(self, key):
        if key[0] == "summary":
            return self.summary
        return self.data[key[0]]

    def write(self, source):
        self.data[source] += 1
        self.summary = sum(self.data.values())


def precise(cache, key):
    """Drop the three entries for one source, and only those."""
    for filt in range(FILTERS):
        cache.pop((key, filt), None)


def everything(cache):
    cache.clear()


def incomplete(cache, key):
    """Drop one of the source's three entries and none of the others."""
    cache.pop((key, 0), None)


INVALIDATIONS = [
    ("the source's entries", precise),
    ("everything", None),
    ("one of the source's entries", incomplete),
]


def run(invalidate):
    source = Source()
    cache = {}
    count = {"dropped": 0, "stale": 0, "hits": 0, "misses": 0, "loads": 0}

    def fill(key):
        count["loads"] += 1
        value = source.load(key)
        cache[key] = value
        return value

    for key in entry_keys():
        fill(key)

    for index, key in enumerate(read_sequence()):
        if index == 20:
            source.write(2)
            before = len(cache)
            if invalidate is None:
                everything(cache)
            else:
                invalidate(cache, 2)
            count["dropped"] += before - len(cache)
        if key in cache:
            count["hits"] += 1
            value = cache[key]
        else:
            count["misses"] += 1
            value = fill(key)
        if value != source.load(key):
            count["stale"] += 1
    return count


def main():
    print(f"  sources                             {SOURCES}")
    print(f"  filters                             {FILTERS}")
    print(f"  cache entries                       {len(entry_keys())}")
    print(f"  reads after the write               {READS - 20}")
    print()
    print("    how the write invalidates          dropped   stale reads")
    results = {}
    for name, invalidate in INVALIDATIONS:
        count = run(invalidate)
        results[name] = count
        print("    {:<34}{:>8}{:>14}".format(name, count["dropped"],
                                            count["stale"]))
    print()

    precise_count = results["the source's entries"]
    all_count = results["everything"]
    partial = results["one of the source's entries"]
    print(f"  one write to source 2 changes three of the twelve entries and the")
    print(f"  summary. Dropping the source's three entries drops")
    print(f"  {precise_count['dropped']} and leaves {precise_count['stale']} reads stale; dropping")
    print(f"  everything drops {all_count['dropped']} and leaves {all_count['stale']}.")
    print()
    print("  the first row is the mistake this whole section is about. That")
    print("  invalidation is precise, it is efficient, it is what the key says")
    print("  to do, and it is wrong, because one cached value is derived from")
    print("  the source and does not name it in its key.")
    print()
    print(f"  the third row is the same mistake made cheaper. It drops")
    print(f"  {partial['dropped']} entry where three needed dropping and leaves")
    print(f"  {partial['stale']} stale reads, so a reader who looked only at the dropped")
    print("  count would rank it as the most careful of the three.")
    print()
    print("  that is why invalidation is the hard part rather than the")
    print("  bookkeeping part. A key is a claim about what a value depends on,")
    print("  and the summary depends on all four sources while its key names")
    print("  none of them. The count of stale reads is the only thing that")
    print("  checks the claim, and it is not visible in the invalidation code.")
    print()
    print(f"  the safe answer is the second row, and its cost is measurable too.")
    print(f"  It drops {all_count['dropped']} entries where three needed dropping, so the next")
    print("  reads of the untouched sources all miss. Clearing the cache is")
    print("  always correct, and it is the right thing to do until the keys can")
    print("  be made to say what they actually depend on.")


main()
