"""Chapter 55 -- practice 4.

Three implementations of one protocol. All three have the names, and the
count is of the ones whose behaviour the consumer can tell apart -- and
of the differences the protocol does not name.
"""

from typing import Protocol


class Cache(Protocol):
    def put(self, key, value):
        ...

    def get(self, key):
        ...


class Plain:
    def __init__(self):
        self.rows = {}

    def put(self, key, value):
        self.rows[key] = value

    def get(self, key):
        return self.rows.get(key)


class Bounded:
    """Keeps the two most recent entries, which the protocol does not
    mention."""

    def __init__(self):
        self.rows = {}
        self.order = []

    def put(self, key, value):
        self.rows[key] = value
        self.order.append(key)
        while len(self.order) > 2:
            self.rows.pop(self.order.pop(0), None)

    def get(self, key):
        return self.rows.get(key)


class Expiring:
    """Answers only for the entry written most recently."""

    def __init__(self):
        self.rows = {}
        self.last = None

    def put(self, key, value):
        self.rows[key] = value
        self.last = key

    def get(self, key):
        return self.rows.get(key) if key == self.last else None


PAIRS = [("a", 1), ("b", 2), ("c", 3)]

IMPLEMENTATIONS = [
    ("Plain", Plain, "nothing"),
    ("Bounded", Bounded, "drops entries past the two most recent"),
    ("Expiring", Expiring, "answers only for the newest key"),
]

METHODS = ["put", "get"]

DIFFERENCES = ["eviction", "expiry"]


def round_trip(cache):
    """Write three entries, then read all three back, which is the only
    thing the protocol promised."""
    for key, value in PAIRS:
        cache.put(key, value)
    return [cache.get(key) for key, _ in PAIRS]


def main():
    print(f"  methods in the protocol             {len(METHODS)}")
    print(f"  implementations                     {len(IMPLEMENTATIONS)}")
    print()
    print("    implementation   has both names   round trips")
    for label, cls, _ in IMPLEMENTATIONS:
        cache = cls()
        has = all(hasattr(cache, name) for name in METHODS)
        back = round_trip(cls())
        got = sum(1 for value in back if value is not None)
        print("    {:<17}{:<17}{} of {}".format(
            label, "yes" if has else "no", got, len(PAIRS)))
    print()

    print("    what each one does that the protocol does not say")
    for label, _, difference in IMPLEMENTATIONS:
        print("    {:<17}{}".format(label, difference))
    print()

    print("    the differences, and whether the protocol names them")
    for name in DIFFERENCES:
        print("    {:<34}{}".format(name, "no"))
    print()
    print("  all three have both names, and the consumer can tell all three")
    print("  apart -- one after three writes, one after two, and one after")
    print("  one. the protocol covers none of that, because a protocol names")
    print("  methods and not behaviour.")
    print()
    print("  the row to read twice is the middle one. `Bounded` is not")
    print("  broken: it is a cache with a size, which is a reasonable thing")
    print("  for a cache to be, and the consumer was written against a")
    print("  protocol that never said the cache was unbounded. so the bug is")
    print("  in the interface rather than in either implementation, and it")
    print("  was introduced by writing one implementation first and naming")
    print("  the interface after it.")
    print()
    print("  what catches it is a test that writes three and reads three,")
    print("  which is the round trip above. that test is the specification,")
    print("  and it is worth writing it against the protocol rather than")
    print("  against `Plain` -- because a test written against `Plain` passes")
    print("  for `Plain` and tells you nothing about the other two.")


main()
