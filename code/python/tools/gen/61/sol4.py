"""Chapter 61 -- solution 4. What a delete costs in each layout.

Three layouts for the same hundred thousand records: a list of tuples, one
array per field, and the column layout with a bitmap marking deleted rows.
The count is of elements moved by the deletes and elements walked by the
reads, and the tombstone design -- the one that looks free -- is the one that
loses, because it moves its cost from the writes to the reads.
"""

ROWS = 100000
FIELDS = 6
DELETES = 100
READS = 1000
POSITION = 10


def row_store():
    """One container: a delete shifts the elements after it, and reads walk records."""
    moved = DELETES * (ROWS - POSITION - 1)
    walked = READS * FIELDS * ROWS
    return moved, walked


def column_store():
    """One container per field: a delete shifts elements in every one of them."""
    moved = DELETES * FIELDS * (ROWS - POSITION - 1)
    walked = READS * ROWS
    return moved, walked


def column_store_with_tombstones():
    """Mark the row deleted instead of removing it, and skip it on the way past."""
    moved = 0
    walked = READS * ROWS + READS * ROWS
    return moved, walked


LAYOUTS = [
    ("list of tuples", row_store),
    ("one array per field", column_store),
    ("arrays plus a tombstone", column_store_with_tombstones),
]

print(f"{ROWS:,} records, {FIELDS} fields, {DELETES:,} deletes, {READS:,} reads of one field")
print()
print(f"{'layout':<26}{'moved by deletes':>18}{'walked by reads':>17}{'total':>15}")
print("-" * 76)
totals = {}
for name, layout in LAYOUTS:
    moved, walked = layout()
    totals[name] = moved + walked
    print(f"{name:<26}{moved:>18,}{walked:>17,}{moved + walked:>15,}")

plain = totals["one array per field"]
tomb = totals["arrays plus a tombstone"]
moved_saved = FIELDS * (ROWS - POSITION - 1)
extra_read = READS * ROWS
break_even = extra_read / moved_saved

print()
print(f"The tombstone moves no elements at all on a delete, and it is")
print(f"{tomb - plain:,} operations worse than the plain column layout, because")
print(f"every read now walks the whole column and then checks every flag. It")
print(f"trades {moved_saved:,} shifted elements per delete for {ROWS:,} checks per read.")
print()
print(f"That trade breaks even at {break_even:.0f} deletes per {READS:,} reads. Below that the")
print(f"plain column layout wins; above it the tombstone does. With {DELETES} deletes")
print("and a thousand reads the plain layout wins by a wide margin, and the")
print("design that looked like a free delete is the one to reject.")
print()
print("The row store is the only layout that loses on both counts here, and it")
print("is the layout you get by default. That is the honest summary of this")
print("chapter: the default is rarely the worst choice for every workload, and")
print("it is rarely the best one either.")
