#!/usr/bin/env python3
"""Chapter 45 demo -- what resizing buys, counted exactly.

Same hash, same keys, same code. The only difference is whether the table
is allowed to grow.
"""
KEY_COUNT = 2_000


def hash_polynomial(key):
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % (2**61 - 1)
    return value


class ChainedTable:
    def __init__(self, capacity=8, grow=True):
        self.buckets = [[] for _ in range(capacity)]
        self.grow = grow
        self.size = 0
        self.comparisons = 0
        self.resizes = 0

    def _bucket(self, key):
        return self.buckets[hash_polynomial(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for index, (existing, _) in enumerate(bucket):
            self.comparisons += 1
            if existing == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        # Load factor 2 is generous. CPython's dict resizes at 2/3.
        if self.grow and self.size > 2 * len(self.buckets):
            self._resize()

    def get(self, key):
        for existing, value in self._bucket(key):
            self.comparisons += 1
            if existing == key:
                return value
        raise KeyError(key)

    def _resize(self):
        pairs = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(len(self.buckets) * 2)]
        self.resizes += 1
        self.size = 0
        for key, value in pairs:
            self.put(key, value)


def hash_table_lookups(key_count):
    """How many keys the hand-written table compares, per successful lookup."""
    table = ChainedTable()
    for i in range(key_count):
        table.put(f"user{i:04d}", i)
    table.comparisons = 0
    for i in range(key_count):
        table.get(f"user{i:04d}")
    return table


def dict_lookups(key_count):
    """The same thing with the built-in. Returns a count we cannot see
    inside -- which is itself the point."""
    table = {}
    for i in range(key_count):
        table[f"user{i:04d}"] = i
    for i in range(key_count):
        table[f"user{i:04d}"]
    return table


print(f"inserting {KEY_COUNT:,} keys, starting from 8 buckets")
print()
print(f"{'table':<26}{'key comparisons':>18}{'per insert':>12}{'resizes':>10}")
print("-" * 66)
for grow, label in ((True, "grows at load factor 2"), (False, "fixed at 8 buckets")):
    table = ChainedTable(grow=grow)
    for i in range(KEY_COUNT):
        table.put(f"user{i:04d}", i)
    print(f"{label:<26}{table.comparisons:>18,}"
          f"{table.comparisons / KEY_COUNT:>12.1f}{table.resizes:>10}")
print()
print("The fixed table is a set of linked lists. With 8 buckets and n keys,")
print("insert number i finds about i/8 keys already in its chain, so the")
print("total is roughly n^2/16 -- for n = 2,000 that predicts 250,000, and")
print("the table reports 249,019. The resize column is what prevents it.")
print()
print("Double the key count and watch which column changes shape.")
print()
print(f"{'keys':>8}{'growing':>14}{'fixed':>14}{'fixed/growing':>16}")
print("-" * 52)
previous = None
for key_count in (500, 1_000, 2_000):
    growing = ChainedTable(grow=True)
    fixed = ChainedTable(grow=False)
    for i in range(key_count):
        growing.put(f"user{i:04d}", i)
        fixed.put(f"user{i:04d}", i)
    row = (growing.comparisons, fixed.comparisons)
    ratio = "" if previous is None else f"{row[1] / previous[1]:>15.1f}x"
    print(f"{key_count:>8,}{row[0]:>14,}{row[1]:>14,}{ratio}")
    previous = row
print()
print("The growing table's column roughly doubles each time. The fixed")
print("table's column multiplies by four. Same code, same keys, same hash")
print("function -- one boolean in the constructor.")
print()
print("lookups on the finished tables")
print()
print(f"{'table':<32}{'comparisons':>14}")
print("-" * 46)
hand = hash_table_lookups(KEY_COUNT)
print(f"{'hand-written, 2,000 keys':<32}{hand.comparisons:>14,}")
print(f"{'built-in dict, 2,000 keys':<32}{'not visible':>14}")
print(f"  mean per lookup                {hand.comparisons / KEY_COUNT:>14.1f}")
print()
print("A dict does not expose a comparison count, and that is not an")
print("oversight -- there is nothing in Python to count. The chains are")
print("arrays of indices inside a C struct, the hash is cached in the")
print("entry, and a probe is a memory read rather than a method call. So")
print("the honest question is not 'which is faster' but 'which complexity")
print("did you choose', and the answer to that is identical for both.")
print()
print("Use dict. Write one once, so you know what you are using.")
