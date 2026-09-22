"""Chapter 55 -- the seam, and what an interface does not promise.

One consumer and three implementations behind a `Protocol`. The count is
of the implementations the consumer can be handed without being edited,
and of the ones whose behaviour it can actually tell apart.
"""

import pathlib

from typing import Protocol


class Store(Protocol):
    def get(self, key):
        ...

    def put(self, key, value):
        ...


class Memory:
    def __init__(self):
        self.rows = {}

    def get(self, key):
        return self.rows.get(key)

    def put(self, key, value):
        self.rows[key] = value


class Counting:
    """Wraps another store and counts what goes through it."""

    def __init__(self, inner):
        self.inner = inner
        self.puts = 0

    def get(self, key):
        return self.inner.get(key)

    def put(self, key, value):
        self.puts += 1
        self.inner.put(key, value)


class Rejecting:
    """Wraps another store and refuses keys it does not like."""

    def __init__(self, inner):
        self.inner = inner
        self.refused = []

    def get(self, key):
        return self.inner.get(key)

    def put(self, key, value):
        if key.startswith("x"):
            self.refused.append(key)
            return
        self.inner.put(key, value)


def save_all(store, pairs):
    """The consumer. It names no implementation, and it does not have to
    know which one it was given."""
    for key, value in pairs:
        store.put(key, value)
    return [store.get(key) for key, _ in pairs]


PAIRS = [("name", "ada"), ("age", 36), ("x-secret", "hidden")]

IMPLEMENTATIONS = [
    ("Memory", lambda: Memory()),
    ("Counting", lambda: Counting(Memory())),
    ("Rejecting", lambda: Rejecting(Memory())),
]

METHODS = ["get", "put"]

SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
CONSUMER_SRC = SOURCE.split("def save_all")[1].split("PAIRS =")[0]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  methods in the interface            {len(METHODS)}")
    print(f"  implementations behind it           {len(IMPLEMENTATIONS)}")
    print()
    print("    implementation   consumer names it   values returned")
    for label, make in IMPLEMENTATIONS:
        returned = save_all(make(), PAIRS)
        got = sum(1 for value in returned if value is not None)
        print("    {:<17}{:<20}{} of {}".format(
            label, "no" if not mentions(CONSUMER_SRC, label) else "yes",
            got, len(PAIRS)))
    print()

    print("    what each implementation does with the third key")
    for label, make in IMPLEMENTATIONS:
        store = make()
        save_all(store, PAIRS)
        if label == "Counting":
            detail = "%d put(s) counted" % store.puts
        elif label == "Rejecting":
            detail = "%d key(s) refused: %s" % (
                len(store.refused), ", ".join(store.refused))
        else:
            detail = "all %d stored" % len(PAIRS)
        print("    {:<17}{}".format(label, detail))
    print()
    print("  the consumer names none of the three, so the seam does what it")
    print("  is for: one implementation can be swapped for another without")
    print("  the consumer being edited. that is a count of zero places, and")
    print("  it is the whole of the claim.")
    print()
    print("  the second table is the part the seam does not cover. two of the")
    print("  three return a value for every key and the third returns two and")
    print("  a `None`, and the interface said nothing about which of those is")
    print("  allowed. it named two methods and their names are all it named --")
    print("  no signature, no postcondition, and no way for the consumer to")
    print("  find out without calling one.")
    print()
    print("  so the seam is worth having and it is not a guarantee. it buys")
    print("  the swap and it does not buy the behaviour, which is why the")
    print("  thing that catches the third implementation is a test and not a")
    print("  type.")


main()
