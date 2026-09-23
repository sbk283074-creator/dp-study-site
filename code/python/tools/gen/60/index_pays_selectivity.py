"""Chapter 60 -- when an index pays, and when it is the slower plan.

One table of 100,000 rows and one predicate. There are two ways to answer it:
read every row in order, or jump into a sorted copy of the column and fetch
the rows it names. Nothing here is timed. The count is of page touches, and
the only assumption in it is that a row reached through the index sits on a
different page from the last one, so it costs four times a row read in order.
That assumption is swept at the end, because the crossover is a property of
the ratio and not of the index.
"""

ROWS = 100000
RANDOM_TOUCH = 4
SELECTIVITIES = [0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]


def boundary(rows):
    """Comparisons to find one key in a sorted list of this many entries."""
    count = 0
    size = rows
    while size > 1:
        size = (size + 1) // 2
        count += 1
    return count


def plan_costs(selectivity, penalty):
    """Page touches for a full scan and for the same predicate through an index."""
    matches = max(1, int(ROWS * selectivity))
    scan = ROWS
    index = penalty * (boundary(ROWS) + matches)
    return matches, scan, index


print(f"{ROWS:,} rows, sequential touch = 1, indexed touch = {RANDOM_TOUCH}")
print()
print(f"{'matches':>8}{'scan':>12}{'index':>12}   {'plan the count prefers':<23}")
print("-" * 58)
for selectivity in SELECTIVITIES:
    matches, scan, index = plan_costs(selectivity, RANDOM_TOUCH)
    winner = "index" if index < scan else "scan"
    print(f"{matches:>8,}{scan:>12,}{index:>12,}   {winner:<24}")

print()
print("The crossover moves with the assumption, so sweep it:")
print()
print(f"{'indexed touch costs':>20}{'scan wins above':>18}")
print("-" * 38)
for penalty in (1, 2, 4, 8, 16):
    crossing = 1.0
    for step in range(1, 1001):
        selectivity = step / 1000
        _, scan, index = plan_costs(selectivity, penalty)
        if index >= scan:
            crossing = selectivity
            break
    print(f"{penalty:>20}{crossing:>17.1%}")

print()
print("The index reads far fewer rows. It reads them in an order the file does")
print("not store them in, so each one is a separate page, and that is why the")
print("count of pages decides the plan rather than the count of rows.")
