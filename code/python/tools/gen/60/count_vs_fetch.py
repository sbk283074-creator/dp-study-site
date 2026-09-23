"""Chapter 60 -- counting by fetching.

A table of twenty thousand orders and one question: how many are there, and
what do they add up to. Three ways to ask it, and the count is of values the
database has to send and of rows the application has to hold. The database
can count and sum without sending anything it does not have to.
"""

import os
import sqlite3
import tempfile

ROWS = 20000
COLUMNS = 4


def build():
    path = os.path.join(tempfile.mkdtemp(), "orders.db")
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer INTEGER,"
        " status TEXT, total INTEGER)"
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [(o, o % 1000, "paid" if o % 3 else "open", 10 + o % 90) for o in range(ROWS)],
    )
    conn.commit()
    return conn


def fetch_every_column(conn):
    """Pull the rows into Python and do the arithmetic there."""
    rows = conn.execute("SELECT * FROM orders").fetchall()
    return len(rows) * COLUMNS, len(rows), (len(rows), sum(row[3] for row in rows))


def fetch_one_column(conn):
    """Pull the one column the arithmetic needs."""
    rows = conn.execute("SELECT total FROM orders").fetchall()
    return len(rows), len(rows), (len(rows), sum(row[0] for row in rows))


def ask_the_database(conn):
    """Send nothing but the answer."""
    count, total = conn.execute("SELECT COUNT(*), SUM(total) FROM orders").fetchone()
    return 1, 0, (count, total)


DESIGNS = [
    ("fetch every column", fetch_every_column),
    ("fetch one column", fetch_one_column),
    ("ask the database", ask_the_database),
]

conn = build()
print(f"{ROWS:,} orders, {COLUMNS} columns each")
print()
print(f"{'design':<22}{'values sent':>13}{'rows held':>11}{'count':>8}{'sum':>10}")
print("-" * 64)
for name, design in DESIGNS:
    values, held, (count, total) = design(conn)
    print(f"{name:<22}{values:>13,}{held:>11,}{count:>8,}{total:>10,}")

print()
print("All three agree on the count and the sum, and they differ by four orders")
print("of magnitude in what crosses the boundary. The arithmetic is the same")
print("either way; the difference is where it happens. When the answer is a")
print("number rather than a set of rows, the database is already holding the")
print("rows and can produce the number without sending them.")
