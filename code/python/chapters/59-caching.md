---
chapter: 59
part: 11
title: Caching
summary: Put a copy of an answer somewhere closer, and measure what that costs as well as what it saves. You will be able to decide whether a cache is worth its memory from the hit rate and the cost of a miss, to find the key that makes a cache wrong, to bound staleness with a TTL chosen from the source's own change rate, and to count the stale reads that no cache reports about itself.
minutes: 110
tags: [caching, lru_cache, hit rate, invalidation, TTL, staleness, stampede, eviction, memoisation, cache keys]
---

Chapter 58 was about finding out where the work is. This chapter is about the first thing everybody does
once they have found it, and it is the one thing in this part that can make a program *wrong* rather than
slow.

A cache is a copy of an answer, kept somewhere cheaper to reach. Everything else follows from that
sentence. A copy can be out of date, so a cache is a correctness decision before it is a performance one.
A copy costs memory whether or not it is ever read, so a cache has a cost that does not shrink when it is
useless. And a copy has to be thrown away when the original changes, so a cache has an invalidation
policy, and that policy is the part that goes wrong.

The chapter is arranged so that the counts get harder as they go. The first blocks count hits and misses,
which is easy and which is also the only count a cache reports about itself. The middle blocks count the
things a cache cannot report: the work a hit saved, the answers it got wrong, the reads that came back
stale. The last blocks count the cost side — entries held, copies to invalidate, computations repeated
under load. Every block is a program that counts something and reports what the count says, and the
recurring result is that the number the cache offers you is not the number that decides.

## The hit rate is a property of the caller

The first thing to understand about a cache is that it does not make a function cheaper. It makes a
*repeat* cheaper, and whether there are repeats is a property of whoever is calling.

One function behind one unbounded cache, called a thousand times over two access patterns. The counts are
of hits and misses, and the two patterns are the same in every respect except which keys they ask for.

```python run
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
```

```text
  keys in the space                   1000
  calls                               1000
  work units per computation          6

    access pattern        distinct keys   hits   misses   hit rate
    a few keys, often                172    828      172      82.8%
    every key equally                634    366      634      36.6%

  the function, the cache and the number of calls are the same in
  both rows. The heavy-tailed pattern got a hit rate of
  82.8% and the flat one got 36.6%.

  the misses are the number of distinct keys and nothing else. The
  heavy pattern reached 172 of the 1000 keys in the space and the
  flat one reached 634, so the flat pattern asked for
  3.7 times as many different things. A cache does not
  make a function cheaper. It makes a repeat cheaper, and how many
  repeats there are is a property of the caller rather than of the
  function.

  the work is the other half of the same fact. Without a cache both
  patterns cost 6000 units, because both call the function 1000
  times. With one, the heavy pattern costs 1032 and the flat one
  3804.

  so the first question about a cache is not which cache. It is how
  often the same question is asked twice, and that is a number you
  can count before writing any of it.
```

The function, the cache and the number of calls are identical in both rows. The heavy-tailed pattern got a
hit rate of 82.8% and the flat one got 36.6%, and the only difference is the distribution of the keys.

The misses are the number of distinct keys and nothing else — that is the whole mechanism. The heavy
pattern reached 172 of the 1,000 keys in the space and the flat one reached 634, so the flat pattern asked
for 3.7 times as many different things. The work follows the same ratio: without a cache both patterns cost
6,000 units, and with one they cost 1,032 and 3,804.

So the first question about a cache is not which cache. It is how often the same question is asked twice,
and that is a number you can count before writing any of it.

## Three places to put the write

A cache has two operations and only one of them is interesting. Reads are easy: look, miss, fill. Writes
are where the designs differ, because a write has to decide how many places it is going to touch.

Cache-aside, write-through and write-behind over the same interleaved sequence of 200 reads and 40 writes.
The count is of store operations and of reads that would get a different answer from the store than from
the cache.

```python run
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
```

```text
  keys                                20
  keys ever written to                6
  reads                               200
  writes                              40
  flush after this many dirty keys    12

    design          store reads   store writes   hits   misses   disagree
    cache-aside              41             40    159       41          0
    write-through            16             40    184       16          0
    write-behind             16              6    184       16         45

  the three designs read the same sequence and produce the same
  answers. They differ in what the store was asked to do and in how
  often the cache and the store would disagree.

  cache-aside did 41 store reads and write-through did
  16. The difference is the invalidation: dropping the key
  on a write means the next read of it misses, so the store is read
  25 more times to fetch a value the cache had.

  write-behind did 6 store writes in 1 flush,
  against 40 for the other two, and it is the only design
  with a disagreement count above zero: 45 reads got an answer
  the store did not have yet.

  the 6 is not a rounding of 40 and it is not the
  number of writes either. The flush threshold is 12 dirty keys and the
  writes only ever touch 6 of the 20 keys, so the batch never reaches
  the threshold and the store is written once, at the end. A write-behind
  cache's store traffic is a function of how many distinct keys are dirty
  at the same moment, which is a property of the workload rather than of
  the design -- and it is the number to count before choosing one.

  that is the whole trade, and it is the same trade at every level
  of this chapter. Writing to both places keeps them in step and
  costs a store write per write. Writing to one and catching up
  later costs fewer store writes and buys a window in which two
  readers of the same key get different answers.

  the counts do not say which to choose. They say what the choice
  costs: 6 store writes against 40, and
  45 disagreements against none. A disagreement count of zero
  is only achievable by writing both, and that is a fact about the
  design rather than a fact about how careful the code is.
```

All three produce the same answers, and the store was asked to do three different amounts of work.

Cache-aside did 41 store reads and write-through did 16. The difference is the invalidation: dropping the
key on a write means the next read of it misses, so the store is read 25 more times to fetch a value the
cache had held. That is the hidden cost of the simplest correct invalidation, and it is invisible unless
you count store reads.

Write-behind did 6 store writes against 40 for the other two, and it is the only design with a
disagreement count above zero: 45 reads got an answer the store did not have yet. The 6 is not a rounding
of 40 — the flush threshold is 12 dirty keys and the writes only ever touch 6 of the 20 keys, so the batch
never fills and the store is written once, at the end. A write-behind cache's store traffic is a function
of how many distinct keys are dirty at the same moment, which is a property of the workload rather than of
the design.

That is the whole trade, and it is the same trade at every level of this chapter. Writing to both places
keeps them in step and costs a store write per write. Writing to one and catching up later costs fewer
store writes and buys a window in which two readers of the same key get different answers.

## Invalidation is the hard part

Everything so far has been about how often a cache is right. This is about what happens when it is wrong,
and the surprising part is that the careful answer is the wrong one.

A cache of thirteen entries derived from four sources, and one write. The count is of entries dropped and
of reads that came back with a value the source no longer had.

```python run
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
```

```text
  sources                             4
  filters                             3
  cache entries                       13
  reads after the write               40

    how the write invalidates          dropped   stale reads
    the source's entries                     3            10
    everything                              13             0
    one of the source's entries              1            14

  one write to source 2 changes three of the twelve entries and the
  summary. Dropping the source's three entries drops
  3 and leaves 10 reads stale; dropping
  everything drops 13 and leaves 0.

  the first row is the mistake this whole section is about. That
  invalidation is precise, it is efficient, it is what the key says
  to do, and it is wrong, because one cached value is derived from
  the source and does not name it in its key.

  the third row is the same mistake made cheaper. It drops
  1 entry where three needed dropping and leaves
  14 stale reads, so a reader who looked only at the dropped
  count would rank it as the most careful of the three.

  that is why invalidation is the hard part rather than the
  bookkeeping part. A key is a claim about what a value depends on,
  and the summary depends on all four sources while its key names
  none of them. The count of stale reads is the only thing that
  checks the claim, and it is not visible in the invalidation code.

  the safe answer is the second row, and its cost is measurable too.
  It drops 13 entries where three needed dropping, so the next
  reads of the untouched sources all miss. Clearing the cache is
  always correct, and it is the right thing to do until the keys can
  be made to say what they actually depend on.
```

One write to source 2 changes three of the twelve entries and the summary. Dropping the source's three
entries drops 3 and leaves 10 reads stale; dropping everything drops 13 and leaves none.

The first row is the mistake this whole section is about. That invalidation is precise, it is efficient, it
is what the key says to do, and it is wrong — because one cached value is derived from the source and does
not name it in its key. The third row is the same mistake made cheaper: it drops 1 entry where three
needed dropping and leaves 14 stale reads, so a reader looking only at the dropped count would rank it as
the most careful of the three.

That is why invalidation is the hard part rather than the bookkeeping part. A key is a claim about what a
value depends on, and the summary here depends on all four sources while its key names none of them. The
count of stale reads is the only thing that checks the claim, and it is not visible in the invalidation
code.

The safe answer is the second row, and its cost is measurable too. It drops 13 entries where three needed
dropping, so the next reads of the untouched sources all miss. Clearing the cache is always correct, and it
is the right thing to do until the keys can be made to say what they actually depend on.

## The TTL is two numbers

A time-to-live is the invalidation policy for people who cannot enumerate their keys. It is also the only
part of a cache that is usually set by taste, which is a shame, because both of its numbers are countable.

One key behind a cache, a source that changes every thirty-seven ticks, and four TTLs. The count is of
loads, of reads that came back with a value the source no longer had, and of how old the oldest such value
was.

```python run
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
```

```text
  ticks                               400
  the source changes every            37

    ttl      loads   hits   stale reads   worst staleness
    none         1    399           363               399
    100          4    396           297                99
    20          20    380            85                19
    5           80    320            20                 4

  a TTL is two numbers at once and the table prints both. It is a
  bound on how wrong a read can be, and a tax on how often the
  source is asked.

  with no TTL the cache is loaded 1 time and is wrong for
  363 of the 400 reads, by up to 399 ticks. That is a
  perfect hit rate on a cache that is useless.

  at a TTL of 5 the worst staleness is 4 ticks and the loads
  rise to 80. At 20 it is 19 ticks and 20 loads, and
  at 100 it is 99 ticks and 4 loads. The bound is one tick
  below the TTL in every case, because an entry is still fresh on the
  tick it is due to expire.

  the number of stale reads is not a function of the TTL on its own.
  A TTL of 5 loads 80 times and leaves 20 stale reads;
  a TTL of 100 loads 4 times and leaves 297. The second is
  14.8 times as many stale reads from 20 times fewer
  loads, and that relationship comes from how the TTL falls against
  the source's own change period of 37 -- which is not a number the
  cache controls.

  so a TTL is chosen from two facts that live outside the cache: how
  stale a read is allowed to be, and how often the source changes.
  The first is a decision. The second is a measurement, and setting a
  TTL without taking it is how a cache ends up with a staleness bound
  that is met exactly while the number of bad reads is far worse than
  the bound suggests.
```

A TTL is two numbers at once and the table prints both. It is a bound on how wrong a read can be, and a tax
on how often the source is asked.

With no TTL the cache is loaded once and is wrong for 363 of the 400 reads, by up to 399 ticks. That is a
perfect hit rate on a cache that is useless. At a TTL of 5 the worst staleness is 4 ticks and the loads
rise to 80; at 20 it is 19 ticks and 20 loads; at 100 it is 99 ticks and 4 loads. The bound is one tick
below the TTL in every case, because an entry is still fresh on the tick it is due to expire.

The number of stale reads is not a function of the TTL on its own. A TTL of 5 loads 80 times and leaves 20
stale reads; a TTL of 100 loads 4 times and leaves 297. The second is 14.8 times as many stale reads from
20 times fewer loads, and that relationship comes from how the TTL falls against the source's own change
period of 37 — which is not a number the cache controls.

So a TTL is chosen from two facts that live outside the cache: how stale a read is allowed to be, and how
often the source changes. The first is a decision. The second is a measurement.

## The stampede

A cache that is correct is not the same as a cache that is efficient, and the difference shows up in one
instant rather than over a run.

Callers arriving together at keys the cache does not hold. The count is of how many of them recompute the
same answer.

```python run
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
```

```text
  callers                             50

  A stampede is what happens when a key is missing and every caller
  that wants it decides to fetch it at the same moment. The first
  table is 50 callers arriving together for one key.

    all 50 callers want one key
    design              computed  duplicates      hits     work
    no protection             50          49         0      200
    single flight              1           0         0        4

  The second table is the same 50 callers spread over 10 keys that
  are all missing. Every caller still arrives before any of them has
  a result, so every caller still computes.

    the same callers over 10 keys
    design              computed  duplicates      hits     work
    no protection             50          40         0      200
    single flight             10           0         0       40

  the column to read is `duplicates`. It is the number of times the
  same computation was performed more than once, and removing it is
  the only thing the cache was there to do.

  protection removes all of them, in both tables. It removes
  49 duplicates when the callers all want one key and
  40 when they are spread over 10, so the count scales with
  the number of callers rather than with the number of keys.

  neither design is wrong. Both return the correct value to every
  caller and both leave the cache full at the end. The difference is
  that one of them does the work once per caller and the other once
  per key, and no test of the returned values can tell them apart.

  that is the cache's version of the measurement problem from the
  previous chapter. A hit rate is computed after the fact, over all
  the calls, and a stampede happens inside one instant -- so a cache
  with an excellent hit rate can still perform the same expensive
  query fifty times, and the hit rate will not show it.

  the fix is a lock held per key rather than one lock for the whole
  cache, so that callers wanting different keys do not queue behind
  each other. That is a change of shape rather than of parameters,
  and the count it removes is the one printed above.
```

The first table is fifty callers arriving together for one key. The second is the same fifty callers spread
over ten keys that are all missing. Every caller still arrives before any of them has a result, so every
caller still computes.

Without protection, all fifty callers compute in both tables. With a per-key lock, one caller per key
computes and the rest wait. Protection removes all 49 duplicates in the first table and all 40 in the
second, so the count scales with the number of callers rather than with the number of keys.

Neither design is wrong, and that is the point. Both return the correct value to every caller and both
leave the cache full at the end. No test of the returned values can tell them apart. And a hit rate is
computed after the fact over all the calls, so a cache with an excellent hit rate can still perform the
same expensive query fifty times without the hit rate showing it.

## The key is the correctness

The key is not an optimisation. It is the statement of what the cached value depends on, and a cache is
correct exactly when that statement is complete.

One function whose answer depends on two arguments, cached four ways. The count is of calls that got an
answer computed for different arguments.

```python run
"""Chapter 59 -- what the key has to contain.

One function whose answer depends on two arguments, cached four ways. The
count is of calls that got an answer computed for different arguments.
"""

ITEMS = 10
CURRENCIES = ["eur", "usd"]
ROUNDS = 2
CALLS = ITEMS * len(CURRENCIES) * ROUNDS
RATES = {"eur": 1, "usd": 2}


def price(item, currency):
    return item * RATES[currency]


def on_the_item(item, currency, cache):
    """The key names one of the two arguments the answer depends on."""
    if item not in cache:
        cache[item] = price(item, currency)
    return cache[item]


def on_both(item, currency, cache):
    if (item, currency) not in cache:
        cache[(item, currency)] = price(item, currency)
    return cache[(item, currency)]


def on_a_string(item, currency, cache):
    """Both arguments, joined into one string."""
    key = "%s-%s" % (item, currency)
    if key not in cache:
        cache[key] = price(item, currency)
    return cache[key]


def on_the_types(item, currency, cache):
    """Both arguments, reduced to what type they are."""
    key = (type(item), type(currency))
    if key not in cache:
        cache[key] = price(item, currency)
    return cache[key]


DESIGNS = [
    ("the item alone", on_the_item),
    ("the item and the currency", on_both),
    ("a string of both", on_a_string),
    ("the type of both", on_the_types),
]


def sequence():
    out = []
    for _round in range(ROUNDS):
        for currency in CURRENCIES:
            for item in range(ITEMS):
                out.append((item, currency))
    return out


def main():
    ops = sequence()
    print(f"  items                               {ITEMS}")
    print(f"  currencies                          {len(CURRENCIES)}")
    print(f"  calls                               {CALLS}")
    print()
    print("    what the key names           misses   hits   wrong   entries")
    results = {}
    for name, design in DESIGNS:
        cache = {}
        misses = 0
        hits = 0
        wrong = 0
        for item, currency in ops:
            before = len(cache)
            value = design(item, currency, cache)
            if len(cache) > before:
                misses += 1
            else:
                hits += 1
            if value != price(item, currency):
                wrong += 1
        results[name] = (misses, hits, wrong, len(cache))
        print("    {:<25}{:>8}{:>7}{:>8}{:>10}".format(
            name, misses, hits, wrong, len(cache)))
    print()

    bad = [name for name, row in results.items() if row[2] > 0]
    item_row = results["the item alone"]
    type_row = results["the type of both"]
    print(f"  {len(bad)} of the {len(DESIGNS)} designs returned an answer computed for different")
    print(f"  arguments, and both of them report an excellent hit rate.")
    print()
    print(f"  `the item alone` is the mistake that looks reasonable. The item is")
    print(f"  the interesting half of the call and the currency feels like a")
    print(f"  detail, so the key names the item and the currency is captured in")
    print(f"  the value. After warm-up it hits on {item_row[1]} of the {CALLS} calls and")
    print(f"  {item_row[2]} of those answers are wrong.")
    print()
    print(f"  `the type of both` is the same mistake taken further, and the table")
    print(f"  shows what taking it further buys: {type_row[1]} hits instead of {item_row[1]}, and")
    print(f"  {type_row[2]} wrong answers instead of {item_row[2]}. A key that names less is a")
    print(f"  cache that hits more and is wrong more, and the two counts move")
    print(f"  together.")
    print()
    print("  the key is not an optimisation. It is the statement of what the")
    print("  cached value depends on, and a cache is correct exactly when that")
    print("  statement is complete. Nothing in either of the wrong designs looks")
    print("  wrong, and no test that calls it with one currency would fail.")
    print()
    print(f"  the other two designs are both right, and they agree on every")
    print(f"  count in the table: {results['the item and the currency'][0]} misses, {results['the item and the currency'][1]} hits, no wrong")
    print(f"  answers. The difference between them appears when a third currency")
    print("  is added. The tuple key needs no change. The string key needs its")
    print("  separator to stay unambiguous, which is a property of the data")
    print("  rather than of the code -- and `eu-r` is a currency code that would")
    print("  break it.")


main()
```

```text
  items                               10
  currencies                          2
  calls                               40

    what the key names           misses   hits   wrong   entries
    the item alone                 10     30      18        10
    the item and the currency      20     20       0        20
    a string of both               20     20       0        20
    the type of both                1     39      36         1

  2 of the 4 designs returned an answer computed for different
  arguments, and both of them report an excellent hit rate.

  `the item alone` is the mistake that looks reasonable. The item is
  the interesting half of the call and the currency feels like a
  detail, so the key names the item and the currency is captured in
  the value. After warm-up it hits on 30 of the 40 calls and
  18 of those answers are wrong.

  `the type of both` is the same mistake taken further, and the table
  shows what taking it further buys: 39 hits instead of 30, and
  36 wrong answers instead of 18. A key that names less is a
  cache that hits more and is wrong more, and the two counts move
  together.

  the key is not an optimisation. It is the statement of what the
  cached value depends on, and a cache is correct exactly when that
  statement is complete. Nothing in either of the wrong designs looks
  wrong, and no test that calls it with one currency would fail.

  the other two designs are both right, and they agree on every
  count in the table: 20 misses, 20 hits, no wrong
  answers. The difference between them appears when a third currency
  is added. The tuple key needs no change. The string key needs its
  separator to stay unambiguous, which is a property of the data
  rather than of the code -- and `eu-r` is a currency code that would
  break it.
```

Two of the four designs returned an answer computed for different arguments, and both of them report an
excellent hit rate.

`the item alone` is the mistake that looks reasonable. The item is the interesting half of the call and the
currency feels like a detail, so the key names the item and the currency is captured in the value. After
warm-up it hits on 30 of the 40 calls and 18 of those answers are wrong.

`the type of both` is the same mistake taken further, and the table shows what taking it further buys: 39
hits instead of 30, and 36 wrong answers instead of 18. A key that names less is a cache that hits more and
is wrong more, and the two counts move together.

The other two designs agree on every count in the table: 20 misses, 20 hits, no wrong answers. The
difference between them appears when a third currency is added. The tuple key needs no change. The string
key needs its separator to stay unambiguous, which is a property of the data rather than of the code.

## The hit rate is not what a cache is for

This is the block that makes the rest of the chapter usable, because it is the one that says which number
to look at.

Two caches over two functions with very different costs. The count is of the work removed, and the cache
with the better hit rate removes less.

```python run
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
```

```text
  calls per cache                     100

    the cache                    hit rate   units/call   work removed   per call
    a cheap call, cached well         90%            2            180        1.8
    an expensive call, cached badly      40%          100           4000       40.0

  the first cache has a hit rate of 90% and the second of 40%.
  The second removes 22.2 times as much work.

  the arithmetic is not subtle and it is worth saying out loud. A
  hit saves the cost of one call, so the work a cache removes is the
  hit count multiplied by the cost of the thing being cached. The
  hit rate is one factor of two, and it is the one everybody quotes
  because it is the one the cache can report about itself.

  that is the shape of the mistake. `lru_cache` will tell you its own
  hit rate and it cannot tell you what a call costs, so the number it
  offers is the number that gets optimised. A cache in front of a
  function that costs two units is a data structure that saves you
  180 units out of 200, and it costs a dictionary, an eviction policy
  and a place where staleness can happen.

  so the number to take before adding a cache is not the hit rate. It
  is the cost of a miss, and the two of them together. The hit rate
  is a measurement of the cache. The work removed is a measurement of
  the program, and only one of those is the question.
```

The first cache has a hit rate of 90% and the second of 40%. The second removes 22.2 times as much work.

The arithmetic is not subtle and it is worth saying out loud. A hit saves the cost of one call, so the work
a cache removes is the hit count multiplied by the cost of the thing being cached. The hit rate is one
factor of two, and it is the one everybody quotes because it is the one the cache can report about itself.

`lru_cache` will tell you its own hit rate and it cannot tell you what a call costs, so the number it
offers is the number that gets optimised. A cache in front of a function that costs two units is a data
structure that saves you 180 units out of 200, and it costs a dictionary, an eviction policy and a place
where staleness can happen.

## The eviction policy is a claim

A bounded cache has to choose what to throw away, and the choice is not a detail to be defaulted. It is a
claim about the access pattern.

Four policies over a cyclic scan of two hundred keys with a cache of fifty. The count is of hits.

```python run
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
```

```text
  keys                                200
  cache size                          50
  accesses                            400
  the access pattern is 0..199, twice

    eviction policy            hits   misses   hit rate   entries held
    least recently used           0      400        0.0%             50
    first in, first out           0      400        0.0%             50
    any entry at all              7      393        1.8%             50
    nothing is evicted          200      200       50.0%            200

  the access pattern is the one every cache is worst at, and every
  bounded policy fails it. Least recently used got
  0 hits out of 400, first in, first out got 0, and choosing a
  victim at random got 7.

  the reason is one line long. The cache holds 50 entries and the scan
  walks 200, so by the time the scan comes back to a key that key was
  evicted 150 accesses ago -- and least recently used evicts exactly
  the entry it is about to be asked for.

  random replacement is the policy with no claim at all about the
  access pattern, and it beats the policy with the strongest claim by
  7 accesses out of 400. That difference is tiny, and the number
  beside it is the one to read: not evicting at all gets 200.

  so the spread across the three bounded policies is
  1.8 percentage points, and the spread between any
  bounded policy and keeping everything is 48.2. On a scan the
  eviction policy is not what is losing the hits, and tuning it is
  tuning the wrong thing.

  the fix for a scan is therefore not a better policy. It is a
  different shape: either bound nothing, or let the caller mark an
  access as one that will not be repeated. Both are changes to what
  the cache is rather than to how it chooses.
```

Every bounded policy fails this pattern. Least recently used got 0 hits out of 400, first in first out got
0, and choosing a victim at random got 7.

The reason is one line long. The cache holds 50 entries and the scan walks 200, so by the time the scan
comes back to a key that key was evicted 150 accesses ago — and least recently used evicts exactly the
entry it is about to be asked for.

Random replacement is the policy with no claim at all about the access pattern, and it beats the policy
with the strongest claim by 7 accesses out of 400. That difference is tiny, and the number beside it is the
one to read: not evicting at all gets 200. The spread across the three bounded policies is 1.8 percentage
points; the spread between any bounded policy and keeping everything is 48.2.

So on a scan the eviction policy is not what is losing the hits, and tuning it is tuning the wrong thing.
The fix is a different shape — either bound nothing, or let the caller mark an access as one that will not
be repeated.

## Two levels, and what the second one buys

Caches stack, and the arithmetic of stacking is the reason they do.

An in-process cache in front of a shared one in front of the store. The count is of where each read was
served.

```python run
"""Chapter 59 -- two levels, and what the second one buys.

An in-process cache in front of a shared one in front of the store. The
count is of where each read was served.
"""

KEYS = 200
CALLS = 500
L1_SIZE = 20
L2_SIZE = 200


def uniform(i):
    """A deterministic value in [0, 1)."""
    state = (i + 1) * 2654435761 % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) / 4294967296.0


def sequence():
    """A skewed access pattern, so that a small first level has something to
    hold on to."""
    return [int(KEYS * uniform(i) ** 6) for i in range(CALLS)]


def no_cache(ops, count):
    for _key in ops:
        count["store"] += 1
    return 0, 0


def one_level(ops, count):
    l1 = {}
    order = []
    for key in ops:
        if key in l1:
            count["l1"] += 1
        else:
            count["store"] += 1
            if len(l1) >= L1_SIZE:
                del l1[order.pop(0)]
            l1[key] = True
            order.append(key)
    return len(l1), 0


def two_levels(ops, count):
    l1 = {}
    order = []
    l2 = {}
    for key in ops:
        if key in l1:
            count["l1"] += 1
        elif key in l2:
            count["l2"] += 1
        else:
            count["store"] += 1
            l2[key] = True
        if key not in l1:
            if len(l1) >= L1_SIZE:
                del l1[order.pop(0)]
            l1[key] = True
            order.append(key)
    return len(l1), len(l2)


DESIGNS = [
    ("the store only", no_cache),
    ("one level", one_level),
    ("two levels", two_levels),
]


def main():
    ops = sequence()
    print(f"  keys                                {KEYS}")
    print(f"  reads                               {CALLS}")
    print(f"  first level size                    {L1_SIZE}")
    print(f"  second level size                   {L2_SIZE}")
    print()
    print("    design           served by l1   served by l2   store loads   entries")
    results = {}
    for name, design in DESIGNS:
        count = {"l1": 0, "l2": 0, "store": 0}
        held1, held2 = design(ops, count)
        results[name] = (count["l1"], count["l2"], count["store"],
                         held1 + held2)
        print("    {:<17}{:>13}{:>15}{:>14}{:>10}".format(
            name, count["l1"], count["l2"], count["store"], held1 + held2))
    print()

    one = results["one level"]
    two = results["two levels"]
    plain = results["the store only"]
    print(f"  the first level holds {L1_SIZE} of the {KEYS} keys and the pattern is skewed,")
    print(f"  so it catches {one[0]} of the {CALLS} reads and sends {one[2]} to the store.")
    print()
    print(f"  adding the second level takes the store loads from {one[2]} to {two[2]},")
    print(f"  which is {one[2] / two[2]:.1f} times fewer. The reads the first level missed are")
    print(f"  {two[1]} and the second level serves {100.0 * two[1] / (two[1] + two[2]):.1f}% of them.")
    print()
    print(f"  that is the multiplication this shape is for. The store load rate")
    print(f"  is the first level's miss rate multiplied by the second level's,")
    print(f"  and each level is cheap to size because each one is a count rather")
    print(f"  than a guess. The same arithmetic is why a third level stops")
    print(f"  helping: the second level already caught most of what the first")
    print(f"  missed, so the third has little left to catch.")
    print()
    print("  the cost is not in the table, and it is the reason to think before")
    print("  adding a level. An entry now exists in two caches and the store, so")
    print("  an invalidation has to reach all three, and the level easiest to")
    print("  forget is the one inside the process -- because it is the one that")
    print("  lives in the language rather than in a service you can call.")
    print()
    print(f"  `the store only` is in the table to size the prize. It reads the")
    print(f"  store {plain[2]} times, and the two-level design reads it {two[2]}. Everything")
    print(f"  between those two numbers is what the cache is worth, and every")
    print(f"  invalidation bug lives in the gap.")


main()
```

```text
  keys                                200
  reads                               500
  first level size                    20
  second level size                   200

    design           served by l1   served by l2   store loads   entries
    the store only               0              0           500         0
    one level                  240              0           260        20
    two levels                 240            135           125       145

  the first level holds 20 of the 200 keys and the pattern is skewed,
  so it catches 240 of the 500 reads and sends 260 to the store.

  adding the second level takes the store loads from 260 to 125,
  which is 2.1 times fewer. The reads the first level missed are
  135 and the second level serves 51.9% of them.

  that is the multiplication this shape is for. The store load rate
  is the first level's miss rate multiplied by the second level's,
  and each level is cheap to size because each one is a count rather
  than a guess. The same arithmetic is why a third level stops
  helping: the second level already caught most of what the first
  missed, so the third has little left to catch.

  the cost is not in the table, and it is the reason to think before
  adding a level. An entry now exists in two caches and the store, so
  an invalidation has to reach all three, and the level easiest to
  forget is the one inside the process -- because it is the one that
  lives in the language rather than in a service you can call.

  `the store only` is in the table to size the prize. It reads the
  store 500 times, and the two-level design reads it 125. Everything
  between those two numbers is what the cache is worth, and every
  invalidation bug lives in the gap.
```

The first level holds 20 of the 200 keys and the pattern is skewed, so it catches 240 of the 500 reads and
sends 260 to the store. Adding the second level takes the store loads from 260 to 125, which is 2.1 times
fewer, and the second level serves 51.9% of the reads the first level missed.

That is the multiplication this shape is for. The store load rate is the first level's miss rate multiplied
by the second level's, and each level is cheap to size because each one is a count rather than a guess. The
same arithmetic is why a third level stops helping: the second level already caught most of what the first
missed.

The cost is not in the table, and it is the reason to think before adding a level. An entry now exists in
two caches and the store, so an invalidation has to reach all three — and the level easiest to forget is
the one inside the process, because it is the one that lives in the language rather than in a service you
can call.

:::pitfall The cache whose key is different every time

A key is the only part of a cache that can be wrong without anything raising. It has to be hashable, and
that is the only requirement, and it is a very weak one.

Five cache designs over fifty calls that alternate between two arguments. The count is of answers that came
back computed for the wrong arguments, and of entries that can never be found again.

```python run
"""Chapter 59 -- the cache whose key is different every time.

Five cache designs over fifty calls that alternate between two arguments.
The count is of answers that came back computed for the wrong arguments,
and of entries that can never be found again.
"""

CALLS = 50
ARGS = [7, 8]
STAMP = [0]


def value(arg):
    return arg * 3


def on_the_arguments(args, cache):
    if args not in cache:
        cache[args] = value(args[0])
    return cache[args]


def on_the_text(args, cache):
    key = str(args)
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


def on_the_length(args, cache):
    key = len(args)
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


def on_a_changing_number(args, cache):
    """The key includes a value that is different on every call."""
    STAMP[0] += 1
    key = (args, STAMP[0])
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


def on_a_list(args, cache):
    key = list(args)
    if key not in cache:
        cache[key] = value(args[0])
    return cache[key]


DESIGNS = [
    ("the arguments", on_the_arguments),
    ("the arguments as text", on_the_text),
    ("how many arguments there are", on_the_length),
    ("the arguments plus a counter", on_a_changing_number),
    ("the arguments as a list", on_a_list),
]


def main():
    print(f"  calls                               {CALLS}")
    print(f"  arguments alternate between         {ARGS}")
    print()
    print("    what the key is                correct   wrong   entries   verdict")
    results = {}
    for name, design in DESIGNS:
        cache = {}
        correct = 0
        wrong = 0
        raised = ""
        for index in range(CALLS):
            arg = ARGS[index % len(ARGS)]
            try:
                got = design((arg,), cache)
            except TypeError as exc:
                raised = type(exc).__name__
                break
            if got == value(arg):
                correct += 1
            else:
                wrong += 1
        if raised:
            verdict = raised
            correct = 0
        elif wrong:
            verdict = "wrong answers"
        else:
            verdict = "correct"
        results[name] = (correct, wrong, len(cache), verdict)
        print("    {:<30}{:>8}{:>8}{:>10}   {}".format(
            name, correct, wrong, len(cache), verdict))
    print()

    bad = [name for name, row in results.items() if row[1] > 0]
    dead = [name for name, row in results.items() if row[2] == CALLS]
    print(f"  {len(bad)} of the {len(DESIGNS)} designs answers the wrong question on half the")
    print(f"  calls, and it is not the one with the worst key.")
    print()
    print("  `how many arguments there are` is the one to look at. Both")
    print(f"  arguments are one element long, so the key is {1} every time, and the")
    print("  second argument is served the first argument's answer for the rest")
    print(f"  of the run: {results['how many arguments there are'][1]} answers out of {CALLS} that no cache")
    print("  reports as anything other than a hit.")
    print()
    print(f"  `the arguments plus a counter` is the opposite failure and it is")
    print(f"  the one that looks harmless. It is never wrong, and it holds")
    print(f"  {results['the arguments plus a counter'][2]} entries for {CALLS} calls, because every call builds a key")
    print("  that no later call can produce. That is a memory leak with a hit")
    print("  rate of zero, and it is the reason a cache should be bounded even")
    print("  when it is correct.")
    print()
    print("  the last row raises `TypeError`, which makes it the only design")
    print("  here that fails loudly. A key has to be hashable and a list is not,")
    print("  so a mutable argument cannot survive a single call -- which makes")
    print("  it the least dangerous mistake on this list, because it is the only")
    print("  one a test would catch on the first line.")
    print()
    print("  none of the five is separated by a hit count. Two of them answer")
    print(f"  every call correctly and one of those never reuses an entry: {len(dead)} of")
    print(f"  the {len(DESIGNS)} holds a fresh entry for every call it has ever served. The")
    print("  column that separates them is the count of answers computed for the")
    print("  wrong arguments, and no cache reports that column about itself.")


main()
```

```text
  calls                               50
  arguments alternate between         [7, 8]

    what the key is                correct   wrong   entries   verdict
    the arguments                       50       0         2   correct
    the arguments as text               50       0         2   correct
    how many arguments there are        25      25         1   wrong answers
    the arguments plus a counter        50       0        50   correct
    the arguments as a list              0       0         0   TypeError

  1 of the 5 designs answers the wrong question on half the
  calls, and it is not the one with the worst key.

  `how many arguments there are` is the one to look at. Both
  arguments are one element long, so the key is 1 every time, and the
  second argument is served the first argument's answer for the rest
  of the run: 25 answers out of 50 that no cache
  reports as anything other than a hit.

  `the arguments plus a counter` is the opposite failure and it is
  the one that looks harmless. It is never wrong, and it holds
  50 entries for 50 calls, because every call builds a key
  that no later call can produce. That is a memory leak with a hit
  rate of zero, and it is the reason a cache should be bounded even
  when it is correct.

  the last row raises `TypeError`, which makes it the only design
  here that fails loudly. A key has to be hashable and a list is not,
  so a mutable argument cannot survive a single call -- which makes
  it the least dangerous mistake on this list, because it is the only
  one a test would catch on the first line.

  none of the five is separated by a hit count. Two of them answer
  every call correctly and one of those never reuses an entry: 1 of
  the 5 holds a fresh entry for every call it has ever served. The
  column that separates them is the count of answers computed for the
  wrong arguments, and no cache reports that column about itself.
```

One of the five answers the wrong question on half the calls, and it is not the one with the worst key.

`how many arguments there are` is the one to look at. Both arguments are one element long, so the key is 1
every time, and the second argument is served the first argument's answer for the rest of the run: 25
answers out of 50 that no cache reports as anything other than a hit.

`the arguments plus a counter` is the opposite failure and it is the one that looks harmless. It is never
wrong, and it holds 50 entries for 50 calls, because every call builds a key that no later call can
produce. That is a memory leak with a hit rate of zero, and it is the reason a cache should be bounded even
when it is correct.

The last row raises `TypeError`, which makes it the only design here that fails loudly. A key has to be
hashable and a list is not, so a mutable argument cannot survive a single call — which makes it the least
dangerous mistake on the list, because it is the only one a test would catch on the first line.

None of the five is separated by a hit count. Two of them answer every call correctly and one of those
never reuses an entry. The column that separates them is the count of answers computed for the wrong
arguments, and no cache reports that column about itself.

:::

:::scenario A read-heavy service with four workers

A service that reads far more than it writes, running four workers, with a cache design to choose. The
count is of store reads, of reads served from a cache, and of stale reads.

```python run
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
```

```text
  keys                                50
  workers                             4
  operations                          1000
  of which reads                      950

    design                 store reads   from cache   stale reads   entries
    no cache                       950            0             0         0
    one per worker                 221          729           199       188
    one shared                      95          855             0        49
    per worker, published          307          643             0       171

  the first row is the prize. Reading the store 950 times is what the
  cache is there to avoid, and everything below it is a fraction of
  that.

  one cache per worker is the design to look at first, and it fails
  on both counts. It does 221 store reads, against 95 for a single
  shared cache, and 199 of its reads returned a value the store no longer
  had. A write clears the writing worker's copy and leaves the other
  three serving the old value, and nothing raises.

  one shared cache is correct and is the cheapest of the four, at 95
  store reads. Its cost is not in this table: it throws the whole cache
  away on every write when one key was what changed, and it is the
  design that every worker contends on.

  the last row is the per-worker design with the invalidation
  published to every worker. It is correct -- 0 stale reads -- and it
  costs 307 store reads, which is 3.2 times the shared cache.
  Four private copies mean a write invalidates four entries instead of
  one, and every worker that held the key has to fetch it again.

  so the table argues against private caches rather than for them, and
  it does so on the count that matters. The stale version is wrong; the
  correct version is more expensive than not having private copies at
  all. The difference between the two is whether the invalidation
  reaches every copy, and the difference between the correct version
  and the shared cache is how many copies there are.

  that is the whole chapter in one table. What separates the four rows
  is not the cache, the key, the size or the eviction policy. It is
  how many copies of an entry exist and whether a write reaches all of
  them -- and the only way to know is to count stale reads, which no
  cache reports about itself.
```

The first row is the prize. Reading the store 950 times is what the cache is there to avoid, and everything
below it is a fraction of that.

One cache per worker is the design to look at first, and it fails on both counts. It does 221 store reads
against 95 for a single shared cache, and 199 of its reads returned a value the store no longer had. A
write clears the writing worker's copy and leaves the other three serving the old value, and nothing
raises.

One shared cache is correct and is the cheapest of the four at 95 store reads. Its cost is not in this
table: it throws the whole cache away on every write when one key was what changed, and it is the design
every worker contends on.

The last row is the per-worker design with the invalidation published to every worker. It is correct — zero
stale reads — and it costs 307 store reads, which is 3.2 times the shared cache. Four private copies mean a
write invalidates four entries instead of one, and every worker that held the key has to fetch it again.

So the table argues against private caches rather than for them, and it does so on the count that matters.
The stale version is wrong; the correct version is more expensive than not having private copies at all.
What separates the four rows is not the cache, the key, the size or the eviction policy. It is how many
copies of an entry exist and whether a write reaches all of them.

:::

## Key takeaways

- **A cache is a copy of an answer, so it is a correctness decision before it is a performance one.** Every
  block in this chapter that found a bug found it by counting wrong or stale answers rather than by timing.
- **A cache does not make a function cheaper; it makes a repeat cheaper.** The same function and the same
  cache gave an 82.8% hit rate on one access pattern and 36.6% on another.
- **The misses are the number of distinct keys and nothing else.** 172 distinct keys produced 172 misses;
  634 produced 634.
- **The hit rate is a property of the caller.** It is the first number to count and it is not a number the
  function's author controls.
- **A write has to decide how many places to touch, and that decision is the whole design.** Cache-aside
  did 41 store reads, write-through 16, and write-behind 6 store writes against 40.
- **Write-behind's store traffic depends on how many distinct keys are dirty at once**, not on how many
  writes happened — so it is a property of the workload rather than of the design.
- **Dropping a key on a write costs a store read later.** Cache-aside's invalidation cost it 25 extra store
  reads to re-fetch values it had held.
- **The precise invalidation is the wrong one.** Dropping the three entries the key named left 10 reads
  stale, because a derived value depended on the source without naming it.
- **A reader who looks only at how many entries an invalidation dropped would rank the worst policy as the
  most careful.** Dropping 1 entry left 14 stale reads; dropping 13 left none.
- **A key is a claim about what a value depends on, and invalidation has to reach everything that claim
  covers.** Where the two lists disagree, the difference is measured in stale reads.
- **A TTL is a staleness bound and a tax at the same time.** 5 ticks gave a bound of 4 and 80 loads; 100
  ticks gave a bound of 99 and 4 loads.
- **The staleness bound is one tick below the TTL, always.** It is the number a cache can reason about
  alone, and it is not the number of bad reads a user experiences.
- **The count of stale reads is not a function of the TTL by itself.** It comes from how the TTL falls
  against the source's change period, which the cache does not control.
- **A correct cache is not an efficient one.** Fifty callers arriving together computed the same answer
  fifty times, and a hit rate computed afterwards would not show it.
- **A stampede's cost scales with the number of callers, not with the number of keys.** Protection removed
  49 duplicates over one key and 40 over ten.
- **The key that names less hits more and is wrong more.** Naming the item gave 30 hits and 18 wrong
  answers; naming the type gave 39 hits and 36 wrong answers.
- **A key that is different on every call is a memory leak with a hit rate of zero.** 50 entries for 50
  calls, and never wrong.
- **A key that is not hashable is the safest mistake on the list**, because it fails on the first call
  rather than silently on the hundredth.
- **The work a cache removes is the hit count multiplied by the cost of a miss.** A 90% hit rate over a
  two-unit call removed 180 units; a 40% hit rate over a hundred-unit call removed 4,000.
- **The hit rate is one factor of two and it is the factor the cache can report about itself.** Which is
  why it is the factor that gets optimised.
- **Every bounded eviction policy fails a scan, and the spread between them is 1.8 percentage points.**
  Least recently used, first in first out and random got 0, 0 and 7 hits out of 400; not evicting got 200.
- **The eviction policy is a claim about the access pattern, and a scan is the pattern that makes the
  strongest claim false.**
- **Two levels multiply their miss rates.** A 20-entry first level sent 260 reads to the store; adding a
  second level took that to 125.
- **A second level adds a copy, so an invalidation has to reach one more place** — and the copy inside the
  process is the one that gets forgotten.
- **Private caches are worse than a shared one on both counts.** Per-worker caches did 221 store reads with
  199 stale reads; a shared cache did 95 with none; publishing the invalidation to every worker was correct
  and cost 307.

## Practice

- [ ] **Count the repeats before you write the cache.** Take a function in a project of yours and a log of
  the arguments it is called with. Count the distinct arguments, the calls, and the hit rate that an
  unbounded cache would produce. Then count the cost of one call. Report the hit rate, the work the cache
  would remove, and your verdict on whether it is worth the memory — and say which of those three numbers
  changed your mind.
- [ ] **Measure a stampede you already have.** Find a cached call that can be reached by more than one
  caller at once, or write a loop that simulates several arriving together. Count how many times the
  underlying computation runs when the key is cold, before and after adding per-key protection. Report both
  counts, and say what the largest number of simultaneous callers you expect actually is — because that is
  the number the fix is sized against.
- [ ] **Choose a TTL from a budget rather than from taste.** Take a cached value with a source that changes
  on a known schedule. Write down how many stale reads out of a thousand you are willing to accept, then
  sweep the TTL and find the largest one that meets it. Report the sweep, the TTL you chose, and the worst
  staleness at that setting. Then check whether any TTL you tested divides the source's change period, and
  say why that matters.
- [ ] **Find a key that does not name everything.** Take a cache in your own code and list every input the
  cached value depends on. Compare that list against what the key contains. For each input the key omits,
  construct two calls that produce the same key and different values, and count how many calls would get a
  wrong answer. Report the key you started with, the key you ended with, and the count of entries the wider
  key forces an invalidation to reach.

## Solutions

:::solution Exercise 1

One function, two access logs, a bounded cache, and the three counts that decide: the hit rate, the work
removed, and the entries held.

```python run
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
```

```text
  keys in the space                   400
  calls                               400
  units per call                      30
  cache size                          50
  worth it above                      25% of the work

    access log           hit rate   work removed   entries held   verdict
    every key equally        9.5%           1140             50   not worth it
    a few keys, often       49.2%           5910             50   worth it

  the function, the cache and the cache size are the same in both
  rows. The skewed log has a hit rate of 49.2% and removes
  5910 units; the flat log has 9.5% and removes 1140.

  the number that decides is the work removed, and it is the hit
  count multiplied by the cost of a miss. A hit rate on its own says
  nothing about whether the cache paid for itself, because a hit on a
  function that costs nothing is worth nothing.

  the entries held is the other half of the decision, and it is the
  half that does not shrink when the cache is ineffective. Both rows
  hold 50 entries, because that is the bound -- so the cache costs the same
  memory in the log where it removes 5910 units and in the log where
  it removes 1140.

  so the three counts to take before adding a cache are the hit rate,
  the cost of a miss, and the number of entries. The first two
  multiply into the saving and the third is what the cache costs
  whether it saves anything or not. Here the flat log removes
  9.5% of the work, which is exactly its hit rate and not enough to
  justify the memory; the skewed log removes 49.2%, which is.
```

:::

:::solution Exercise 2

Callers arriving together at cold keys, counted with and without a per-key lock, across five arrival sizes
and two sizes of cold set.

```python run
"""Solution 2 -- the stampede, and what a per-key lock removes.

Callers arriving together at cold keys, counted with and without
protection, over a range of how many arrive at once.
"""

UNITS = 5
ARRIVALS = [1, 2, 5, 10, 50]
KEY_COUNTS = [1, 5]

WORK = [0]


def compute(key):
    WORK[0] += 1
    total = 0
    for i in range(UNITS - 1):
        WORK[0] += 1
        total += key * i
    return total


def unprotected(callers):
    """Every caller reads the cache before any of them has filled it."""
    for key in callers:
        compute(key)


def protected(callers):
    """One caller per key computes; the others wait for that result."""
    seen = set()
    for key in callers:
        if key not in seen:
            seen.add(key)
            compute(key)


DESIGNS = [
    ("unprotected", unprotected),
    ("per-key lock", protected),
]


def main():
    print(f"  work units per computation          {UNITS}")
    print(f"  arrival sizes                       {ARRIVALS}")
    print(f"  keys in the cold set                {KEY_COUNTS}")
    print()
    print("    callers   keys   unprotected   protected   removed")
    rows = []
    for keys in KEY_COUNTS:
        for callers in ARRIVALS:
            workload = [index % keys for index in range(callers)]
            cells = []
            for _name, design in DESIGNS:
                WORK[0] = 0
                design(workload)
                cells.append(WORK[0] // UNITS)
            removed = cells[0] - cells[1]
            rows.append((callers, keys, cells[0], cells[1], removed))
            print("    {:>7}{:>7}{:>14}{:>12}{:>10}".format(
                callers, keys, cells[0], cells[1], removed))
    print()

    worst = max(rows, key=lambda row: row[4])
    plural = "key" if worst[1] == 1 else "keys"
    print(f"  the two columns are counts of how many times the same computation")
    print(f"  was performed. Without protection it is the number of callers;")
    print(f"  with a per-key lock it is the number of distinct keys.")
    print()
    print(f"  the largest saving in the table is {worst[4]} computations, at {worst[0]}")
    print(f"  callers over {worst[1]} {plural}. The saving is not a constant: it is the")
    print(f"  number of callers that arrived together beyond the first one for")
    print(f"  each key, which is a property of the workload.")
    print()
    print(f"  so the count to take before writing the lock is how many callers")
    print(f"  arrive together, not how many calls there are. A service with a")
    print(f"  thousand calls a second arriving one at a time has no stampede to")
    print(f"  fix, and a service with fifty arriving on the same key at the same")
    print(f"  instant has one whether it is busy or not.")
    print()
    print(f"  the lock has a cost the table does not show, and it is the reason")
    print(f"  to size it before adding it. A lock held per key means a caller for")
    print(f"  one key never waits behind a caller for another, and one lock held")
    print(f"  for the whole cache does -- which turns a stampede on one key into a")
    print(f"  queue on every key. The count that decides is the number of distinct")
    print(f"  keys being computed at the same moment.")


main()
```

```text
  work units per computation          5
  arrival sizes                       [1, 2, 5, 10, 50]
  keys in the cold set                [1, 5]

    callers   keys   unprotected   protected   removed
          1      1             1           1         0
          2      1             2           1         1
          5      1             5           1         4
         10      1            10           1         9
         50      1            50           1        49
          1      5             1           1         0
          2      5             2           2         0
          5      5             5           5         0
         10      5            10           5         5
         50      5            50           5        45

  the two columns are counts of how many times the same computation
  was performed. Without protection it is the number of callers;
  with a per-key lock it is the number of distinct keys.

  the largest saving in the table is 49 computations, at 50
  callers over 1 key. The saving is not a constant: it is the
  number of callers that arrived together beyond the first one for
  each key, which is a property of the workload.

  so the count to take before writing the lock is how many callers
  arrive together, not how many calls there are. A service with a
  thousand calls a second arriving one at a time has no stampede to
  fix, and a service with fifty arriving on the same key at the same
  instant has one whether it is busy or not.

  the lock has a cost the table does not show, and it is the reason
  to size it before adding it. A lock held per key means a caller for
  one key never waits behind a caller for another, and one lock held
  for the whole cache does -- which turns a stampede on one key into a
  queue on every key. The count that decides is the number of distinct
  keys being computed at the same moment.
```

:::

:::solution Exercise 3

A source that changes every thirty-seven ticks, a budget of a hundred stale reads out of a thousand, and a
sweep over thirteen TTLs to find the largest one that meets it.

```python run
"""Solution 3 -- the largest TTL that meets a staleness budget.

A source that changes on a schedule, a budget of how many stale reads out
of a thousand are allowed, and a sweep over the TTL. The sweep is the
answer, and the reason it cannot be reasoned about is in the table.
"""

TICKS = 1110
CHANGE_EVERY = 37
BUDGET = 100
TTLS = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 35]


def source_value(tick):
    return tick // CHANGE_EVERY


def run(ttl):
    count = {"loads": 0, "stale": 0, "worst": 0}
    cached = None
    cached_at = 0
    for tick in range(TICKS):
        if cached is None or tick - cached_at >= ttl:
            cached = source_value(tick)
            cached_at = tick
            count["loads"] += 1
        if cached != source_value(tick):
            count["stale"] += 1
            count["worst"] = max(count["worst"], tick - cached_at)
    return count


def main():
    print(f"  ticks                               {TICKS}")
    print(f"  the source changes every            {CHANGE_EVERY}")
    print(f"  stale reads allowed                 {BUDGET}")
    print()
    print("    ttl      loads   stale reads   worst staleness   within budget")
    results = {}
    for ttl in TTLS:
        count = run(ttl)
        results[ttl] = count
        ok = "yes" if count["stale"] <= BUDGET else "no"
        print("    {:<9}{:>5}{:>14}{:>18}   {}".format(
            ttl, count["loads"], count["stale"], count["worst"], ok))
    print()

    passing = [ttl for ttl in TTLS if results[ttl]["stale"] <= BUDGET]
    best = max(passing)
    over = [ttl for ttl in TTLS if results[ttl]["stale"] > BUDGET]
    print(f"  the sweep is the answer to the question a staleness budget")
    print(f"  actually asks, which is not `what TTL should I use` but `how large")
    print(f"  can the TTL be and still meet the budget`.")
    print()
    print(f"  the largest TTL that stays within {BUDGET} stale reads is {best}, at")
    print(f"  {results[best]['stale']} stale reads and {results[best]['loads']} loads. Every larger value in the sweep")
    print(f"  is over budget, and the count of stale reads rises with the TTL")
    print(f"  throughout.")
    print()
    print(f"  the sweep is monotone here, and the reason it is monotone is that")
    print(f"  no TTL in the list divides the change period of {CHANGE_EVERY}. That is not")
    print(f"  a property of the method; it is a property of the numbers that were")
    print(f"  chosen. A TTL that divides the change period gives zero stale reads")
    print(f"  however large it is, because every expiry lands exactly on a change")
    print(f"  and the cache never serves a value the source has moved past.")
    print()
    print(f"  so a sweep of the TTLs that look reasonable is not enough. The")
    print(f"  values to test are the ones that fall against the change period, and")
    print(f"  the two to test first are a TTL just under the period and a TTL that")
    print(f"  divides it exactly.")
    print()
    print(f"  the worst staleness column tells the other half of the story. It is")
    print(f"  {results[best]['worst']} ticks at a TTL of {best}, which is one tick below the TTL, and it")
    print(f"  rises with the TTL rather than with the count of stale reads. A")
    print(f"  reader who set the TTL from the staleness bound alone would pick")
    print(f"  {CHANGE_EVERY - 1}, and would get {run(CHANGE_EVERY - 1)['stale']} stale reads against a budget of {BUDGET}.")
    print()
    print(f"  the bound is the number a cache can reason about on its own and the")
    print(f"  count of bad reads is the number a user experiences. They are not")
    print(f"  the same number, and only one of them can be computed without")
    print(f"  knowing how often the source changes.")


main()
```

```text
  ticks                               1110
  the source changes every            37
  stale reads allowed                 100

    ttl      loads   stale reads   worst staleness   within budget
    2          555            15                 1   yes
    3          370            30                 2   yes
    4          278            45                 3   yes
    5          222            60                 4   yes
    6          185            75                 5   yes
    8          139           105                 7   no
    10         111           135                 9   no
    12          93           177                11   no
    15          74           210                14   no
    20          56           265                19   no
    25          45           330                24   no
    30          37           435                29   no
    35          32           565                34   no

  the sweep is the answer to the question a staleness budget
  actually asks, which is not `what TTL should I use` but `how large
  can the TTL be and still meet the budget`.

  the largest TTL that stays within 100 stale reads is 6, at
  75 stale reads and 185 loads. Every larger value in the sweep
  is over budget, and the count of stale reads rises with the TTL
  throughout.

  the sweep is monotone here, and the reason it is monotone is that
  no TTL in the list divides the change period of 37. That is not
  a property of the method; it is a property of the numbers that were
  chosen. A TTL that divides the change period gives zero stale reads
  however large it is, because every expiry lands exactly on a change
  and the cache never serves a value the source has moved past.

  so a sweep of the TTLs that look reasonable is not enough. The
  values to test are the ones that fall against the change period, and
  the two to test first are a TTL just under the period and a TTL that
  divides it exactly.

  the worst staleness column tells the other half of the story. It is
  5 ticks at a TTL of 6, which is one tick below the TTL, and it
  rises with the TTL rather than with the count of stale reads. A
  reader who set the TTL from the staleness bound alone would pick
  36, and would get 609 stale reads against a budget of 100.

  the bound is the number a cache can reason about on its own and the
  count of bad reads is the number a user experiences. They are not
  the same number, and only one of them can be computed without
  knowing how often the source changes.
```

:::

:::solution Exercise 4

A value derived from two arguments and keyed on one, with the wrong-answer count before and after the key
is widened — and the invalidation the wider key forces.

```python run
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
```

```text
  regions                             4
  channels                            3
  calls                               36

    what the key names           misses   hits   wrong
    the region alone                  4     32      24
    the region and the channel       12     24       0

  the construction that finds the bug is the one worth writing down.
  Take two calls that differ only in the argument the key does not
  name, and check whether they produce the same key and different
  values. Here `total(0, 0)` is 10 and `total(0, 1)` is 11, both key
  on region 0, and the second call is served the first one's answer.

  that is 24 wrong answers out of 36, from a cache with a hit rate of
  88.9%. The wider key gets 0 wrong answers and a hit rate of
  66.7%.

  the second half of the exercise is the invalidation, because
  widening a key widens what has to be dropped. `on_the_region` could
  be invalidated by dropping one entry per region. `on_both` needs one
  entry dropped per region per channel, and a write that changes a
  region has to drop all 3 of them.

  so the key and the invalidation are the same statement written
  twice. A key says what the value depends on, and an invalidation
  has to reach every key that statement covers. A cache where those
  two lists disagree is a cache with stale reads, and the count of
  wrong answers above is the size of the disagreement.
```

:::
