"""Chapter 58 -- counting the objects a phase creates.

Four ways to total one column, each counting the intermediate containers
it builds. The count is of objects the code creates, which is a property
of the code rather than of the interpreter.
"""

ROWS = 300


def make_rows():
    return [{"v": i % 7} for i in range(ROWS)]


def two_comprehensions(data, count):
    """A list of values, then a filtered list of them."""
    values = [row["v"] for row in data]
    count["made"] += 1
    count["held"] += len(values)
    kept = [value for value in values if value]
    count["made"] += 1
    count["held"] += len(kept)
    return sum(kept)


def sorted_copy(data, count):
    """One container, because the filter is folded into the sort."""
    kept = sorted(row["v"] for row in data if row["v"])
    count["made"] += 1
    count["held"] += len(kept)
    return sum(kept)


def one_pass(data, count):
    """No container at all: the loop adds as it goes."""
    total = 0
    for row in data:
        if row["v"]:
            total += row["v"]
    return total


WAYS = [
    ("two comprehensions", two_comprehensions),
    ("a sorted copy", sorted_copy),
    ("one pass", one_pass),
]


def main():
    data = make_rows()
    print(f"  rows                                {ROWS}")
    print()
    print("    how the column is totalled      containers   items held")
    results = []
    totals = []
    for name, way in WAYS:
        count = {"made": 0, "held": 0}
        totals.append(way(data, count))
        results.append((name, count["made"], count["held"]))
    for name, made, held in results:
        print("    {:<32}{:>10}{:>13}".format(name, made, held))
    print()

    same = len(set(totals)) == 1
    print("    the three totals                    {}".format(
        "identical" if same else "different"))
    print("    the answer                          {}".format(totals[0]))
    print()

    heavy = max(results, key=lambda r: r[2])
    light = min(results, key=lambda r: r[2])
    print(f"  all three produce the same number, and `{heavy[0]}` holds")
    print(f"  {heavy[2]} items in intermediates to produce it, against {light[2]} for")
    print(f"  `{light[0]}`.")
    print()
    print("  the count is of containers the code asks for, which is why it is")
    print("  the same on every machine. `sys.getsizeof` would give you a byte")
    print("  count and that count depends on the interpreter build, so it")
    print("  cannot be written into a book -- but `how many lists did this")
    print("  function make, and how long were they` can be, and it is the")
    print("  part of the cost that a reader can act on.")
    print()
    print("  the reason to look at this number at all is the peak. two")
    print("  containers of a few hundred small integers is nothing; the same")
    print("  shape over a million rows is two lists of a million, and the")
    print("  fix is not to make the lists smaller but to stop making them --")
    print("  which is what the third way does, and it is shorter to write.")


main()
