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
