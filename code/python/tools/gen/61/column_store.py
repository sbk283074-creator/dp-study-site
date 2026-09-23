"""Chapter 61 -- one aggregate over one column, held two ways.

A hundred thousand records with six fields each, held as a list of tuples and
as one array per field. The query is a single sum over a single column. The
count is of the values the query has to walk past, and the difference is not
a constant factor: it is the number of fields in the record.
"""

import array

ROWS = 100000
FIELDS = 6


def row_store():
    """One tuple per record, so every field is next to every other."""
    return [(index, index % 50, index % 7, index % 1000, 100 + index % 900, 0)
            for index in range(ROWS)]


def column_store():
    """One array per field, so a field is next to itself."""
    return {
        "id": array.array("q", range(ROWS)),
        "region": array.array("q", (index % 50 for index in range(ROWS))),
        "channel": array.array("q", (index % 7 for index in range(ROWS))),
        "units": array.array("q", (index % 1000 for index in range(ROWS))),
        "price": array.array("q", (100 + index % 900 for index in range(ROWS))),
    }


def sum_units_from_rows(rows):
    """Walk the records and take one field out of each."""
    touched = 0
    total = 0
    for row in rows:
        touched += len(row)
        total += row[3]
    return total, touched


def sum_units_from_columns(columns):
    """Walk the one field the query needs."""
    touched = 0
    total = 0
    for value in columns["units"]:
        touched += 1
        total += value
    return total, touched


rows = row_store()
columns = column_store()

row_total, row_touched = sum_units_from_rows(rows)
col_total, col_touched = sum_units_from_columns(columns)

print(f"{ROWS:,} records, {FIELDS} fields each, one sum over one field")
print()
print(f"{'layout':<16}{'sum':>14}{'values walked':>15}{'per record':>12}")
print("-" * 57)
print(f"{'list of tuples':<16}{row_total:>14,}{row_touched:>15,}"
      f"{row_touched / ROWS:>12.0f}")
print(f"{'one array each':<16}{col_total:>14,}{col_touched:>15,}"
      f"{col_touched / ROWS:>12.0f}")

print()
print("Both layouts produce the same number. The second one walked")
print(f"{col_touched / row_touched:.3f} of the values the first one walked, because the")
print("record is the unit of storage in the first and the field is the unit")
print("in the second.")
print()
print("That ratio is not a constant. It is the number of fields in the record,")
print("so it grows with the record. A layout that keeps a record together is")
print("the right one when the query wants the record; it is the wrong one when")
print("the query wants one field, and it is the wrong one by exactly the")
print("width of the record.")
