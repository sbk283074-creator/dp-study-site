"""Chapter 61 -- where the column layout is the wrong tool.

The same hundred thousand records in the two layouts again, and four
operations. The count is of containers the operation has to touch and of
elements it has to move. The result is that the layout that wins every read
in the previous blocks loses the delete by exactly the width of the record.
"""

import array

ROWS = 100000

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


def delete_row(rows, position, value):
    """One container, and every element after the hole moves."""
    containers = 1
    moved = len(rows) - position - 1
    del rows[position]
    return containers, moved


def delete_column(columns, position, value):
    """One container per field, and every element after the hole moves in each."""
    containers = len(columns)
    moved = containers * (len(columns[0]) - position - 1)
    for column in columns:
        del column[position]
    return containers, moved


def update_field_row(rows, position, value):
    """A record is the unit, so writing one field rebuilds the record."""
    containers = 1
    moved = len(rows[position])
    row = list(rows[position])
    row[3] = value
    rows[position] = tuple(row)
    return containers, moved


def update_field_column(columns, position, value):
    """A field is the unit, so writing one field writes one value."""
    columns[3][position] = value
    return 1, 1


POSITION = 10

print(f"{ROWS:,} records, {FIELD_COUNT} fields, deleting and updating at position {POSITION}")
print()
print(f"{'operation':<28}{'row parts':>11}{'row moved':>12}"
      f"{'col parts':>11}{'col moved':>11}")
print("-" * 73)
for label, on_rows, on_columns in (
    ("delete one record", delete_row, delete_column),
    ("update one field of one record", update_field_row, update_field_column),
):
    row_parts, row_moved = on_rows(row_store(), POSITION, 0)
    col_parts, col_moved = on_columns(column_store(), POSITION, 0)
    print(f"{label:<28}{row_parts:>11}{row_moved:>12,}{col_parts:>11}{col_moved:>11,}")

print()
print("The read blocks and this table are the same trade seen twice. A record")
print("is the unit of storage in one layout, so reading a field costs the whole")
print("record and writing a field costs the whole record -- and the delete")
print("costs one container instead of six. A field is the unit in the other, so")
print("reading and writing a field cost one value, and a delete costs every")
print("field in the record.")
print()
print("Nothing here is a reason to prefer one layout. It is a reason to know")
print("which operations the table has to serve: a table that is written once")
print("and read a million times wants the columns, and a table that is deleted")
print("from constantly wants the records.")
