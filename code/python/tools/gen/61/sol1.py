"""Chapter 61 -- solution 1. Choosing a layout from the access pattern.

Five queries with different column lists and different call counts, plus a
thousand deletes. The count is of values walked by the reads and elements
moved by the deletes, and the verdict is not "columns are faster" -- it is a
weighted sum, so the answer depends on the mix of the two.
"""

ROWS = 100000
FIELDS = 6

WORKLOAD = [
    # columns the query reads, how often it is called
    (1, 500),
    (2, 200),
    (3, 100),
    (5, 50),
    (6, 150),
]

DELETES = 1000
POSITION = 10


def row_store_values_walked():
    """Every call walks the whole record."""
    return sum(calls * FIELDS * ROWS for _columns, calls in WORKLOAD)


def column_store_values_walked():
    """Every call walks only the fields it named."""
    return sum(calls * columns * ROWS for columns, calls in WORKLOAD)


MOVE_PER_DELETE_ROW = ROWS - POSITION - 1
MOVE_PER_DELETE_COLUMN = FIELDS * (ROWS - POSITION - 1)

calls_total = sum(calls for _columns, calls in WORKLOAD)
row_walked = row_store_values_walked()
col_walked = column_store_values_walked()
row_moved = DELETES * MOVE_PER_DELETE_ROW
col_moved = DELETES * MOVE_PER_DELETE_COLUMN

print(f"{ROWS:,} records, {FIELDS} fields, {calls_total:,} queries, {DELETES:,} deletes")
print()
print(f"{'columns read':>13}{'calls':>8}{'row store':>16}{'column store':>15}")
print("-" * 52)
for columns, calls in WORKLOAD:
    print(f"{columns:>13}{calls:>8}{calls * FIELDS * ROWS:>16,}"
          f"{calls * columns * ROWS:>15,}")
print("-" * 52)
print(f"{'reads, total':>13}{calls_total:>8}{row_walked:>16,}{col_walked:>15,}")
print(f"{'deletes, moved':>13}{DELETES:>8}{row_moved:>16,}{col_moved:>15,}")
print(f"{'total':>13}{'':>8}{row_walked + row_moved:>16,}"
      f"{col_walked + col_moved:>15,}")

read_saving = row_walked - col_walked
write_penalty = col_moved - row_moved
per_delete = MOVE_PER_DELETE_COLUMN - MOVE_PER_DELETE_ROW

print()
print(f"The column layout walks {read_saving:,} fewer values across the reads")
print(f"and shifts {write_penalty:,} more elements across the deletes, so on")
print(f"this workload the list of tuples wins by {write_penalty - read_saving:,}.")
print()
print(f"The two sides cross at {read_saving / per_delete:.0f} deletes: below that the")
print(f"columns win, above it the records do. At {DELETES:,} deletes per")
print(f"{calls_total:,} queries the deletes are the whole story, and the reason is")
print(f"that a delete costs {MOVE_PER_DELETE_COLUMN:,} shifted elements in the column")
print(f"layout against {MOVE_PER_DELETE_ROW:,} in the record layout -- six containers")
print("against one.")
print()
print("So the verdict is not a property of the layout. Change the number of")
print("deletes and the answer changes; make the sixth query, which reads the")
print("whole record, the only query and the columns win by nothing at all.")
print("The count is what tells you which of those workloads you have.")
