"""Chapter 58 -- predicting the size you have not run.

Three algorithms counted at four sizes, each fit to an exponent from the
ratios, then used to predict a fifth size. The prediction is then checked
against a count taken at that size.
"""

import math

MEASURED = [100, 200, 400, 800]
PREDICTED = 1600


def pair_scan(items, count):
    """Every pair of positions, once."""
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            count[0] += 1
    return count[0]


def merge_sort(items, count):
    """Comparisons made by a merge sort, counted where they happen."""
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


def one_pass(items, count):
    for _item in items:
        count[0] += 1
    return count[0]


ALGORITHMS = [
    ("scan every pair", pair_scan),
    ("merge sort", merge_sort),
    ("one pass", one_pass),
]


def measure(items, algorithm):
    count = [0]
    algorithm(items, count)
    return count[0]


def exponent(series):
    """The power the counts grow as, fitted from the measured ratios."""
    logs = [math.log(series[i + 1] / series[i]) for i in range(len(series) - 1)]
    return sum(logs) / len(logs) / math.log(2)


def main():
    print(f"  measured sizes                      {MEASURED}")
    print(f"  size to predict                     {PREDICTED}")
    print()
    counts = {}
    print("    size     scan every pair    merge sort    one pass")
    for size in MEASURED:
        items = list(range(size))
        cells = []
        for name, algorithm in ALGORITHMS:
            value = measure(items, algorithm)
            counts.setdefault(name, []).append(value)
            cells.append(value)
        print("    {:>6}{:>18}{:>14}{:>12}".format(size, *cells))
    print()

    print("    fitted from the ratios, and checked at %d" % PREDICTED)
    print("    {:<18}{:>9}{:>12}{:>12}{:>9}".format(
        "", "power", "predicted", "measured", "error"))
    errors = []
    for name, algorithm in ALGORITHMS:
        series = counts[name]
        power = exponent(series)
        predicted = series[-1] * (PREDICTED / MEASURED[-1]) ** power
        actual = measure(list(range(PREDICTED)), algorithm)
        error = 100.0 * (predicted - actual) / actual
        errors.append((name, power, predicted, actual, error))
        print("    {:<18}{:>8.2f}{:>12.0f}{:>12}{:>8.1f}%".format(
            name, power, predicted, actual, error))
    print()

    worst = max(errors, key=lambda entry: abs(entry[4]))
    print("  the fit is from four counts, and the check is a size the program")
    print(f"  has not run when it makes the prediction. The worst of the three")
    print(f"  predictions is off by {abs(worst[4]):.1f}%, and it is `{worst[0]}`.")
    print()
    print("  that is what a complexity class is for. It is not a label to")
    print("  write beside a function; it is the thing that answers `what")
    print("  happens at ten times the size` without running it, which is the")
    print("  question that decides whether a design can ship.")
    print()
    print("  the linear and the quadratic fit are almost exact, because the")
    print("  counts are integers and the ratios have nowhere to hide. The")
    print("  middle column is the interesting one: a sort's comparisons grow")
    print("  by a little more than two per doubling, and the fit lands near")
    print("  that without the code saying so anywhere.")
    print()
    print("  so the number to carry away is the ratio rather than the count.")
    print("  Doubling the input multiplies the work by about 4 for the pair")
    print("  scan, by about 2 for the pass, and by a number in between for")
    print("  the sort, and those three numbers are the same on every machine")
    print("  -- which is the only reason they can be written down at all.")


main()
