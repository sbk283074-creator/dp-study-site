#!/usr/bin/env python3
"""Chapter 45 demo -- a hash table written by hand, so that `dict` stops
being magic.

Everything counted here is a Python-level step: key comparisons and bucket
visits. No timing, so the numbers are exact and machine-independent.
"""
CAPACITY = 256
KEYS = [f"user{i:04d}" for i in range(1_000)]


def hash_by_length(key):
    return len(key)


def hash_by_sum(key):
    return sum(ord(char) for char in key)


def hash_polynomial(key):
    """Multiply by a small prime and add the next character. Two different
    strings almost never land on the same value, which is the property
    `len` does not have."""
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % (2**61 - 1)
    return value


class ChainedTable:
    """A dict is this, in C, with a better hash and no linked tuples."""

    def __init__(self, capacity=CAPACITY, hash_fn=hash_polynomial):
        self.buckets = [[] for _ in range(capacity)]
        self.hash_fn = hash_fn
        self.size = 0
        self.comparisons = 0

    def _bucket(self, key):
        return self.buckets[self.hash_fn(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for index, (existing, _) in enumerate(bucket):
            self.comparisons += 1
            if existing == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        for existing, value in self._bucket(key):
            self.comparisons += 1
            if existing == key:
                return value
        raise KeyError(key)

    def chain_lengths(self):
        return [len(bucket) for bucket in self.buckets]


print(f"{len(KEYS):,} keys, each {len(KEYS[0])} characters long,")
print(f"into {CAPACITY} buckets")
print()
print(f"{'hash function':<20}{'buckets used':>14}{'longest chain':>15}{'lookup cost':>14}")
print("-" * 63)
for label, fn in (("len(key)", hash_by_length),
                  ("sum(ord(c))", hash_by_sum),
                  ("polynomial", hash_polynomial)):
    table = ChainedTable(hash_fn=fn)
    for i, key in enumerate(KEYS):
        table.put(key, i)
    lengths = table.chain_lengths()
    used = sum(1 for length in lengths if length)
    table.comparisons = 0
    for key in KEYS:
        table.get(key)
    print(f"{label:<20}{used:>14}{max(lengths):>15}{table.comparisons / len(KEYS):>14.1f}")
print()
print("'lookup cost' is the mean number of keys compared to find a key that")
print("is definitely in the table -- the best case for a lookup, since every")
print("one of these succeeds.")
print()
print("Read the first row against the third. `len(key)` is a perfectly")
print("deterministic function of the key, and it is useless: every key in")
print("this set has length 8, so every key lands in bucket 8, and the table")
print("is a linked list wearing a hat. The mean lookup compares 500 keys.")
print()
print("`sum(ord(c))` is the interesting row. It is not wrong -- it separates")
print("different keys -- but the sums cluster in a narrow band, so after")
print("`% 256` the keys pile into a handful of buckets. A weak hash does not")
print("produce wrong answers, it produces a table that is quietly slow.")
print()
print("That is the answer to 'why is dict O(1)?' and it is not the table.")
print("The table is twenty lines. The O(1) comes from the hash function")
print("spreading the keys, and from resizing before the chains get long.")
