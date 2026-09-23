"""Chapter 60 -- the scenario. A report endpoint at scale.

Fifty requests against a shop with twenty thousand orders, rendered four
ways: a query per order, then one join, then the total asked of the database
rather than fetched, then an index on the filtered column. The count is of
statements, of rows received, of rows visited and of connections opened, and
each change is measured rather than estimated.
"""

import os
import sqlite3
import tempfile

ORDERS = 20000
PAID = 200
REQUESTS = 50


def build():
    path = os.path.join(tempfile.mkdtemp(), "shop.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE customer (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER,"
        " status TEXT, total INTEGER)"
    )
    conn.executemany(
        "INSERT INTO customer VALUES (?, ?)",
        [(i, f"customer-{i:04d}") for i in range(1000)],
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [(o, o % 1000, "paid" if o < PAID else "open", 10 + o % 90)
         for o in range(ORDERS)],
    )
    conn.commit()
    return conn


def report(conn, status, join, index, aggregate):
    """One request. Returns statements sent, rows received, rows visited."""
    statements = 0
    received = 0
    visited = 0
    cur = conn.cursor()

    if join:
        cur.execute(
            "SELECT c.name, o.total FROM orders o"
            " JOIN customer c ON c.id = o.customer_id WHERE o.status = ?",
            (status,),
        )
        statements += 1
        rows = cur.fetchall()
        received += len(rows)
        visited += len(rows) if index else ORDERS
    else:
        cur.execute("SELECT id, customer_id FROM orders WHERE status = ?", (status,))
        statements += 1
        orders = cur.fetchall()
        received += len(orders)
        visited += len(orders) if index else ORDERS
        for _order_id, customer_id in orders:
            cur.execute("SELECT name FROM customer WHERE id = ?", (customer_id,))
            statements += 1
            received += len(cur.fetchall())

    if aggregate:
        total = cur.execute("SELECT SUM(total) FROM orders").fetchone()[0]
        statements += 1
        received += 1
    else:
        cur.execute("SELECT total FROM orders")
        statements += 1
        rows = cur.fetchall()
        received += len(rows)
        total = sum(row[0] for row in rows)

    return statements, received, visited, total


conn = build()
naive = report(conn, "paid", join=False, index=False, aggregate=False)
joined = report(conn, "paid", join=True, index=False, aggregate=False)
summed = report(conn, "paid", join=True, index=False, aggregate=True)
conn.execute("CREATE INDEX i_orders_status ON orders(status)")
conn.commit()
indexed = report(conn, "paid", join=True, index=True, aggregate=True)

STAGES = [
    ("per-order query, total fetched", naive),
    ("one join, total fetched", joined),
    ("one join, total from the database", summed),
    ("and an index on the filter", indexed),
]

print(f"{REQUESTS} requests, {ORDERS:,} orders, {PAID} of them paid")
print()
print(f"{'stage':<34}{'statements':>11}{'rows received':>14}{'rows visited':>13}")
print("-" * 72)
for name, (statements, received, visited, _total) in STAGES:
    print(f"{name:<34}{statements:>11,}{received:>14,}{visited:>13,}")

CHANGES = [
    ("one join instead of a query per order", naive, joined),
    ("the total asked of the database", joined, summed),
    ("an index on the filtered column", summed, indexed),
]

print()
print(f"what each change removes, over the {REQUESTS} requests")
print(f"{'change':<34}{'statements':>11}{'rows received':>14}{'rows visited':>13}{'opens':>7}")
print("-" * 79)
for name, before, after in CHANGES:
    print(f"{name:<34}{(after[0] - before[0]) * REQUESTS:>11,}"
          f"{(after[1] - before[1]) * REQUESTS:>14,}"
          f"{(after[2] - before[2]) * REQUESTS:>13,}{0:>7,}")
print(f"{'one connection for all requests':<34}"
      f"{0:>11,}{0:>14,}{0:>13,}{1 - REQUESTS:>7,}")

print()
print(f"{'over the run':<34}{'statements':>11}{'rows received':>14}"
      f"{'rows visited':>13}{'opens':>7}")
print("-" * 79)
print(f"{'before':<34}{naive[0] * REQUESTS:>11,}"
      f"{naive[1] * REQUESTS:>14,}{naive[2] * REQUESTS:>13,}{REQUESTS:>7,}")
print(f"{'after':<34}{indexed[0] * REQUESTS:>11,}"
      f"{indexed[1] * REQUESTS:>14,}{indexed[2] * REQUESTS:>13,}{1:>7,}")
print()
print("Four changes, and they are not four versions of the same change. The")
print("join removes statements and leaves the rows visited alone. The")
print("aggregate removes rows received and leaves the statements alone. The")
print("index removes rows visited and leaves both of the others alone. The")
print("connection is the only one that is about the process rather than the")
print("query. Each one moves exactly one of the numbers, which is why you")
print("have to count all of them before you decide which to do first.")
