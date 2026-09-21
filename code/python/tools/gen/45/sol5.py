#!/usr/bin/env python3
"""Chapter 45 solution 5 -- open addressing, its precondition, and its bug.

Chaining puts several keys in one bucket. Open addressing puts one key per
slot and probes forward when the slot is taken. Both are O(1) while the table
is not too full -- and 'not too full' is a number, which this measures.
"""
CAPACITY = 1024
MASK = (1 << 64) - 1
TOMBSTONE = object()


def hash_plain(key):
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % (2**61 - 1)
    return value


def hash_mixed(key):
    """The same polynomial, then an avalanche step. A hash only has to be
    injective to be correct, and it has to be *spread out* to be fast."""
    value = hash_plain(key)
    value ^= value >> 33
    value = (value * 0xFF51AFD7ED558CCD) & MASK
    value ^= value >> 33
    return value


class OpenTable:
    """Linear probing: if the slot is taken, try the next one."""

    def __init__(self, capacity=CAPACITY, hash_fn=hash_mixed):
        self.slots = [None] * capacity
        self.hash_fn = hash_fn
        self.size = 0
        self.probes = 0

    def put(self, key, value):
        index = self.hash_fn(key) % len(self.slots)
        while True:
            entry = self.slots[index]
            if entry is None or entry is TOMBSTONE:
                self.slots[index] = (key, value)
                self.size += 1
                return
            self.probes += 1
            if entry[0] == key:
                self.slots[index] = (key, value)
                return
            index = (index + 1) % len(self.slots)

    def get(self, key):
        index = self.hash_fn(key) % len(self.slots)
        while True:
            entry = self.slots[index]
            if entry is None:
                return None
            self.probes += 1
            if entry is not TOMBSTONE and entry[0] == key:
                return entry[1]
            index = (index + 1) % len(self.slots)


def mean_probe(key_count, hash_fn):
    table = OpenTable(hash_fn=hash_fn)
    for i in range(key_count):
        table.put(f"user{i:05d}", i)
    table.probes = 0
    for i in range(key_count):
        table.get(f"user{i:05d}")
    return table.probes / key_count


print("first, the hash function itself")
print()
print("  the keys are user00000, user00001, user00002, ... -- consecutive")
print("  integers, which is the most common shape a real key has.")
print()
print(f"{'keys':>8}{'load':>8}{'plain polynomial':>20}{'with avalanche':>18}")
print("-" * 54)
for key_count in (128, 512, 922):
    load = key_count / CAPACITY
    print(f"{key_count:>8,}{load:>8.2f}{mean_probe(key_count, hash_plain):>20.2f}"
          f"{mean_probe(key_count, hash_mixed):>18.2f}")
print()
print("The plain polynomial hash is injective -- it gives different answers")
print("for different keys -- and it is terrible here. Consecutive keys differ")
print("in their last character only, so their hash values differ by 1, and")
print("modulo 1024 that puts them in *consecutive* slots. Linear probing")
print("turns that into one long run, and a lookup for the last key in the")
print("run walks the whole thing. A hash does not only have to be correct;")
print("it has to scatter, and the avalanche step is what scatters it.")
print()
print("Now the load factor, with the good hash.")
print()
print(f"{'keys':>8}{'load factor':>14}{'mean probes per lookup':>24}")
print("-" * 46)
for key_count in (128, 256, 512, 768, 922, 1_000):
    print(f"{key_count:>8,}{key_count / CAPACITY:>14.2f}"
          f"{mean_probe(key_count, hash_mixed):>24.2f}")
print()
print("This is the textbook curve. Up to a load factor of about 0.75 a")
print("successful lookup costs about three probes or fewer, and then it")
print("climbs. At 0.98 the table has almost no empty slot left to stop a")
print("probe run, and the cost is twenty-five.")
print()
print("That cliff is why CPython's dict resizes at a load factor of 2/3, and")
print("it is why 'expected O(1)' has a precondition attached. The notation")
print("hides the precondition; the table does not.")
print()
print("Now the bug. Deletion in an open-addressed table cannot just clear the")
print("slot, because an empty slot is how a probe run knows to stop.")
print()
small = OpenTable(capacity=8, hash_fn=lambda key: 0)
for key in ("aa", "bb", "cc"):
    small.put(key, key.upper())
print(f"  slots after putting aa, bb, cc : {[e[0] if e else None for e in small.slots[:4]]}")
small.slots[1] = None
print(f"  after deleting bb by clearing it : {[e[0] if e else None for e in small.slots[:4]]}")
print(f"  get('cc')                       : {small.get('cc')}")
print()
print("All three keys hash to slot 0, so they were placed in slots 0, 1 and")
print("2. `cc` is still sitting in slot 2, untouched -- and the lookup for it")
print("stops at the hole in slot 1 and reports the key as absent. A cache")
print("that reports a hit as a miss is not a slow cache, it is a wrong one,")
print("and the failure is invisible until keys collide, which in a test with")
print("ten keys they usually do not.")
print()
print("The fix is a sentinel: a deleted slot is marked rather than cleared,")
print("so a probe run walks past it, and only a genuinely empty slot ends the")
print("run. That sentinel is why the class above tests for TOMBSTONE as well")
print("as None. It is also why the standard library's dict is not something")
print("to reimplement in order to save an import.")
