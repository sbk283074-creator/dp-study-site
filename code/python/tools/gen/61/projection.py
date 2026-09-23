"""Chapter 61 -- what a column layout is worth depends on the query.

The same two layouts, a hundred thousand records, and two queries: one that
reads a single field and one that reads five. The count is of values walked,
swept across the number of fields the query needs, and the sweep is the
point -- the advantage of a column layout is proportional to how much of the
record the query does not want.
"""

import array

ROWS = 100000

# One rule per field, so the two layouts cannot disagree about what a record
# contains -- which is the mistake this kind of comparison invites.
FIELDS = [
    lambda index: index,
    lambda index: index % 50,
    lambda index: index % 7,
    lambda index: index % 1000,
    lambda index: 100 + index % 900,
    lambda index: 0,
]
FIELD_COUNT = len(FIELDS)


def row_store():
    return [tuple(rule(index) for rule in FIELDS) for index in range(ROWS)]


def column_store():
    return [array.array("q", (rule(index) for index in range(ROWS)))
            for rule in FIELDS]


def rows_for_fields(rows, wanted):
    """Walk the records, taking the fields the query asked for."""
    touched = 0
    total = 0
    for row in rows:
        touched += len(row)
        for position in wanted:
            total += row[position]
    return total, touched


def columns_for_fields(columns, wanted):
    """Walk only the arrays the query asked for."""
    touched = 0
    total = 0
    for position in wanted:
        for value in columns[position]:
            touched += 1
            total += value
    return total, touched


rows = row_store()
columns = column_store()

print(f"{ROWS:,} records, {FIELD_COUNT} fields, reading 1 to {FIELD_COUNT} of them")
print()
print(f"{'fields read':>12}{'list of tuples':>18}{'one array each':>17}{'ratio':>9}")
print("-" * 56)
for count in range(1, FIELD_COUNT + 1):
    wanted = list(range(count))
    row_total, row_touched = rows_for_fields(rows, wanted)
    col_total, col_touched = columns_for_fields(columns, wanted)
    if row_total != col_total:
        raise SystemExit("the two layouts disagreed")
    print(f"{count:>12}{row_touched:>18,}{col_touched:>17,}"
          f"{row_touched / col_touched:>9.1f}")

print()
print("The last row is the one to remember. A query that reads every field")
print("walks exactly the same number of values in both layouts, so the column")
print("store is not faster -- it is the same, and it has paid for the")
print("transposition. The advantage of a column layout is not that columns are")
print("fast; it is that a query rarely wants the whole record, and the layout")
print("lets the query pay only for what it asked for.")
