"""Chapter 19 -- what a comma-separated file does to fields that contain commas.

Six rows written two ways: joined with commas by hand, and written by the csv
module. Both are read back. The count is of fields that survive the round trip.
"""

import csv
import io

FIELDS = ["name", "note"]

ROWS = [
    {"name": "ada", "note": "plain"},
    {"name": "bob", "note": "has, a comma"},
    {"name": "cy", "note": 'has "quotes"'},
    {"name": "dee", "note": "has\nnewline"},
    {"name": "eve", "note": ""},
    {"name": "fay", "note": " leading space"},
]


def write_by_hand(rows):
    return "\n".join(",".join(row[field] for field in FIELDS) for row in rows) + "\n"


def read_by_hand(text):
    out = []
    for line in text.split("\n"):
        if not line:
            continue
        parts = line.split(",")
        if len(parts) == len(FIELDS):
            out.append(dict(zip(FIELDS, parts)))
    return out


def write_with_csv(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def read_with_csv(text):
    return list(csv.DictReader(io.StringIO(text)))


def recovered(rows):
    """Fields that came back exactly as they went in, matched by name."""
    by_name = {row.get("name"): row for row in rows}
    good = 0
    for row in ROWS:
        found = by_name.get(row["name"])
        if found is None:
            continue
        for field in FIELDS:
            if found.get(field) == row[field]:
                good += 1
    return good


def verdict(rows, row):
    by_name = {entry.get("name"): entry for entry in rows}
    found = by_name.get(row["name"])
    if found is None:
        return "missing"
    return "ok" if found.get("note") == row["note"] else "wrong"


hand_text = write_by_hand(ROWS)
csv_text = write_with_csv(ROWS)
hand_rows = read_by_hand(hand_text)
csv_rows = read_with_csv(csv_text)
TOTAL = len(ROWS) * len(FIELDS)

print(f"{len(ROWS)} rows of {len(FIELDS)} fields, written and read back two ways")
print()
print(f"{'what is counted':<40}{'by hand':>12}{'csv':>8}")
print("-" * 60)
print(f"{'characters written':<40}{len(hand_text):>12}{len(csv_text):>8}")
print(f"{'rows recovered':<40}{len(hand_rows):>12}{len(csv_rows):>8}")
print(f"{'fields recovered unchanged':<40}"
      f"{recovered(hand_rows):>12}{recovered(csv_rows):>8}")
print(f"{'fields there were to recover':<40}{TOTAL:>12}{TOTAL:>8}")

print()
print(f"{'note as written':<26}{'by hand':>12}{'csv':>8}")
print("-" * 46)
for row in ROWS:
    shown = row["note"].replace("\n", "\\n") or "(empty)"
    print(f"{shown:<26}{verdict(hand_rows, row):>12}{verdict(csv_rows, row):>8}")

print()
print("The csv module costs characters and returns rows. It quotes a field that")
print("contains a comma, doubles a quote inside a quoted field, and keeps a")
print("newline inside the quotes where it belongs -- which is why the file it")
print("writes is longer than the one you would type, and why every row comes")
print("back.")
print()
print("The hand-rolled writer loses three fields and a whole row, and it loses")
print("them quietly. The row with a comma in it has the wrong number of parts,")
print("so it is dropped; the row with a newline in it is read as two lines, one")
print("of which looks like a perfectly good row with a truncated value. Nothing")
print("raises. The file parses, the program finishes, and the report is wrong.")
print()
print("The same argument as the placeholder applies here, and it is worth")
print("saying once more: a format with quoting rules is not a format you can")
print("implement with split. Use csv for reading and writing, set the dialect")
print("explicitly if the consumer is not Python, and never round-trip a value")
print("through string concatenation when a library already knows the rules.")
