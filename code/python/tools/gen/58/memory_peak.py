"""Chapter 58 -- the peak, not the total.

Three ways to process the same five thousand rows, each counting the items
it holds at once. The total items touched is identical for all three; the
high-water mark is not.
"""

ROWS = 5000
BATCH = 32


def read_all(count):
    """One container holding every row."""
    rows = [{"v": i % 11} for i in range(ROWS)]
    count["peak"] = max(count["peak"], len(rows))
    count["touched"] += len(rows)
    total = 0
    for row in rows:
        total += row["v"]
    return total


def streamed(count):
    """One row at a time, discarded after use."""
    total = 0
    for i in range(ROWS):
        count["peak"] = max(count["peak"], 1)
        count["touched"] += 1
        total += i % 11
    return total


def batched(count):
    """A window of rows, discarded after each window."""
    total = 0
    for start in range(0, ROWS, BATCH):
        window = [{"v": i % 11} for i in range(start, min(start + BATCH, ROWS))]
        count["peak"] = max(count["peak"], len(window))
        count["touched"] += len(window)
        for row in window:
            total += row["v"]
    return total


WAYS = [
    ("read all, then process", read_all),
    ("one row at a time", streamed),
    ("a window of %d" % BATCH, batched),
]


def main():
    print(f"  rows                                {ROWS}")
    print()
    print("    how the rows are read         items touched   peak live at once")
    results = []
    totals = []
    for name, way in WAYS:
        count = {"touched": 0, "peak": 0}
        totals.append(way(count))
        results.append((name, count["touched"], count["peak"]))
    for name, touched, peak in results:
        print("    {:<29}{:>14}{:>20}".format(name, touched, peak))
    print()

    same = len(set(totals)) == 1
    print("    the three totals                    {}".format(
        "identical" if same else "different"))
    print("    the answer                          {}".format(totals[0]))
    print()

    heavy = max(results, key=lambda row: row[2])
    light = min(results, key=lambda row: row[2])
    window = results[2]
    print("  all three read every row exactly once, so the column a")
    print(f"  `total work` measurement reports is {results[0][1]} for all three and")
    print(f"  cannot tell them apart. The peak separates them: {heavy[2]} rows")
    print(f"  live at once, or {window[2]}, or {light[2]}.")
    print()
    print("  that ratio is the subject of this block. The total decides how")
    print("  long a program takes; the peak decides whether it runs at all,")
    print("  because a machine that cannot hold the peak does not run slowly.")
    print("  It stops, and it stops at the row where the peak is reached.")
    print()
    print("  the fix is a change of shape rather than a change of speed. Both")
    print(f"  of the others read the same {ROWS} rows and do the same additions:")
    print(f"  the window holds {window[2]} rows at a time and the streaming version")
    print(f"  holds {light[2]}. Reading a file in chunks is not longer code than")
    print("  reading it whole; it is one extra loop.")
    print()
    print("  the count here is of containers the code asks for, which is why")
    print("  it is the same on every machine. `tracemalloc` reports the same")
    print("  shape in bytes and a different number on each interpreter build,")
    print("  so the shape is what a book can print and the bytes are what a")
    print("  profiler is for.")


main()
