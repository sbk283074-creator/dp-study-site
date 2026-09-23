"""Chapter 58 -- telling O(n) from O(n^2) by counting, not by timing.

Three ways to look for a duplicate, each counting the comparisons it makes
at four sizes. The count is turned into an exponent, and the exponent is
what names the shape.
"""

import math

SIZES = [100, 200, 400, 800]


def shuffled(size):
    """A deterministic permutation, so the sort is not measured in the one
    case it is fastest at."""
    items = list(range(size))
    state = 12345
    for i in range(size - 1, 0, -1):
        state = (state * 1103515245 + 12345) % 2147483648
        j = state % (i + 1)
        items[i], items[j] = items[j], items[i]
    return items


def by_scan(items, count):
    """Every item against every item before it."""
    seen = []
    for item in items:
        for other in seen:
            count[0] += 1
            if other == item:
                return True
        seen.append(item)
    return False


def merge_sort(items, count):
    """A sort whose comparisons are counted where they happen. Counting
    only the pass after the sort would make this look linear."""
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], count)
    right = merge_sort(items[mid:], count)
    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        count[0] += 1
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def by_sort(items, count):
    """A sort, then one pass over neighbours."""
    ordered = merge_sort(items, count)
    for left, right in zip(ordered, ordered[1:]):
        count[0] += 1
        if left == right:
            return True
    return False


def by_set(items, count):
    seen = set()
    for item in items:
        count[0] += 1
        if item in seen:
            return True
        seen.add(item)
    return False


ALGORITHMS = [
    ("scan every pair", by_scan),
    ("sort then compare", by_sort),
    ("a set", by_set),
]


def fit(series):
    """The exponent the counts grow as, from the measured ratios."""
    logs = [math.log(series[i + 1] / series[i]) for i in range(len(series) - 1)]
    return sum(logs) / len(logs) / math.log(2)


def classify(power):
    """Named from the fitted exponent, not from knowing the answer."""
    if power > 1.5:
        return "quadratic"
    if power > 1.1:
        return "n log n"
    return "linear"


def main():
    print(f"  sizes                               {len(SIZES)}")
    print(f"  algorithms                          {len(ALGORITHMS)}")
    print()
    counts = {name: [] for name, _ in ALGORITHMS}
    print("    size     scan every pair   sort then compare   a set")
    for size in SIZES:
        items = shuffled(size)
        cells = []
        for name, algorithm in ALGORITHMS:
            count = [0]
            algorithm(items, count)
            counts[name].append(count[0])
            cells.append(count[0])
        print("    {:>6}{:>18}{:>20}{:>8}".format(size, *cells))
    print()

    powers = {name: fit(counts[name]) for name, _ in ALGORITHMS}
    shapes = {name: classify(powers[name]) for name, _ in ALGORITHMS}
    print("    growth when the size doubles")
    print("    {:<22}{:>9}{:>10}   {}".format("", "ratio", "exponent", "shape"))
    for name, _ in ALGORITHMS:
        series = counts[name]
        ratios = [series[i + 1] / series[i] for i in range(len(series) - 1)]
        average = sum(ratios) / len(ratios)
        print("    {:<22}{:>8.2f}x{:>10.2f}   {}".format(
            name, average, powers[name], shapes[name]))
    print()

    quadratic = [name for name, _ in ALGORITHMS if shapes[name] == "quadratic"]
    print("  the counts are exact integers, so the ratio between two sizes is a")
    print("  property of the algorithm: doubling the input multiplies the work")
    print(f"  by about 4 for {len(quadratic)} of the {len(ALGORITHMS)}, by about 2 for another, and by")
    print("  something in between for the third.")
    print()
    print("  the exponent is that measurement with the ratio's arithmetic taken")
    print(f"  out. It is {powers['scan every pair']:.2f} for the pair scan, {powers['a set']:.2f} for the set, and")
    print(f"  {powers['sort then compare']:.2f} for the sort -- and that last one is the number")
    print("  that cannot be read off the code, because nothing in a merge sort")
    print("  says `log`. It is also the number the count only finds because the")
    print("  sort's own comparisons are inside it: counting the pass over")
    print("  neighbours and not the sort makes this algorithm look linear.")
    print()
    print("  the input is shuffled rather than sorted, so the sort is measured")
    print("  in its average case rather than the one case it is fastest at.")
    print("  That choice does not change the exponent; it changes the constant")
    print("  in front of it, which is the part of a measurement that a reader")
    print("  should not trust across machines anyway.")
    print()
    print("  the ratio is the measurement that survives being written down. A")
    print("  timing would give the same shape on any machine and a different")
    print("  number on each one, so a book can only print the shape. The counts")
    print("  are the same everywhere, which is why they can be printed at all.")
    print()
    print(f"  the other thing the counts buy is the size at which the shape")
    print(f"  matters. At {SIZES[0]} items the quadratic version makes {counts['scan every pair'][0]}")
    print(f"  comparisons, which is nothing; the exponent is what says it will be")
    print(f"  {counts['scan every pair'][-1]} at {SIZES[-1]}, and that is the number to carry away.")


main()
