"""Chapter 60 -- solution 1. Choosing indexes from the workload.

Five columns, a table of a hundred thousand rows, and twelve hundred queries
spread across them. The count is of rows visited, and the saving an index
buys for one column is the number of times that column is queried multiplied
by the rows it excludes -- so the rank of a column is a product, and the
column asked for most often is not the column that saves the most.
"""

ROWS = 100000

WORKLOAD = [
    # column, rows the predicate matches, how often it is asked for
    ("email", 1, 100),
    ("city", 400, 300),
    ("status", 2000, 350),
    ("created", 30000, 400),
    ("note", 100000, 50),
]

QUERIES = sum(queries for _column, _matches, queries in WORKLOAD)
BASELINE = QUERIES * ROWS


def saved_by(matches, queries):
    """Rows visited with no index, less rows visited with one on this column."""
    return queries * (ROWS - matches)


def visited(indexed):
    """Rows visited by the whole workload, given a set of indexed columns."""
    total = 0
    for column, matches, queries in WORKLOAD:
        total += queries * (matches if column in indexed else ROWS)
    return total


print(f"{ROWS:,} rows, {QUERIES:,} queries, {BASELINE:,} rows visited with no index")
print()
print(f"{'column':<12}{'matches':>10}{'queries':>9}{'rows saved':>13}{'per query':>11}")
print("-" * 55)
for column, matches, queries in WORKLOAD:
    print(f"{column:<12}{matches:>10,}{queries:>9,}{saved_by(matches, queries):>13,}"
          f"{(ROWS - matches):>11,}")

by_saving = sorted(WORKLOAD, key=lambda row: -saved_by(row[1], row[2]))
by_frequency = sorted(WORKLOAD, key=lambda row: -row[2])

print()
print("ranked by rows saved :", ", ".join(column for column, _m, _q in by_saving))
print("ranked by how often  :", ", ".join(column for column, _m, _q in by_frequency))
agree = sum(1 for a, b in zip(by_saving, by_frequency) if a[0] == b[0])
print(f"the two orders agree on {agree} of {len(WORKLOAD)} positions")

BUDGET = 2
pick_saving = {row[0] for row in by_saving[:BUDGET]}
pick_frequency = {row[0] for row in by_frequency[:BUDGET]}

print()
print(f"two indexes to spend, so the choice is the first two of each order")
print(f"{'chosen by':<18}{'indexes':<22}{'rows visited':>14}")
print("-" * 54)
print(f"{'rows saved':<18}{', '.join(sorted(pick_saving)):<22}{visited(pick_saving):>14,}")
print(f"{'how often':<18}{', '.join(sorted(pick_frequency)):<22}"
      f"{visited(pick_frequency):>14,}")
print()
print(f"The two orders disagree about the middle of the list, and the budget")
print(f"makes the disagreement cost {abs(visited(pick_saving) - visited(pick_frequency)):,} rows.")
print("The column asked for most often is `created`, and it removes seventy")
print("thousand rows per query. The column that removes the most per query is")
print("`email`, at ninety-nine thousand nine hundred and ninety-nine, and it is")
print("asked for a quarter as often. Neither number decides on its own: the")
print("saving is the product of the two, which is why `status` comes first and")
print("`note` comes last having saved nothing at all.")
