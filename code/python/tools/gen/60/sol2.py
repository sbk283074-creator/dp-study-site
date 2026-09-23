"""Chapter 60 -- solution 2. Batching writes, counted in transactions.

Four hundred rows into a real database, four ways. The count is of calls the
application makes and of transactions it commits, and the second number is
the one that decides how much work the storage engine does, because a commit
is the unit of durability rather than the unit of SQL.
"""

import os
import sqlite3
import tempfile

ROWS = 400


def build():
    path = os.path.join(tempfile.mkdtemp(), "batch.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, label TEXT)")
    conn.commit()
    return conn


def per_row(conn):
    """One statement, one commit, four hundred times."""
    calls = 0
    commits = 0
    for index in range(ROWS):
        conn.execute("INSERT INTO t VALUES (?, ?)", (index, f"row-{index:04d}"))
        calls += 1
        conn.commit()
        commits += 1
    return calls, commits


def one_commit(conn):
    """One statement per row, one commit at the end."""
    calls = 0
    for index in range(ROWS):
        conn.execute("INSERT INTO t VALUES (?, ?)", (index, f"row-{index:04d}"))
        calls += 1
    conn.commit()
    return calls, 1


def executemany(conn):
    """One call from the application, one transaction."""
    conn.executemany(
        "INSERT INTO t VALUES (?, ?)",
        [(index, f"row-{index:04d}") for index in range(ROWS)],
    )
    conn.commit()
    return 1, 1


def one_statement(conn):
    """Every row in a single statement."""
    values = ", ".join(["(?, ?)"] * ROWS)
    args = [value for index in range(ROWS)
            for value in (index, f"row-{index:04d}")]
    conn.execute(f"INSERT INTO t VALUES {values}", args)
    conn.commit()
    return 1, 1


DESIGNS = [
    ("a commit per row", per_row),
    ("one commit at the end", one_commit),
    ("executemany", executemany),
    ("one statement", one_statement),
]

print(f"{ROWS} rows, {ROWS} calls to the application's own write path")
print()
print(f"{'design':<24}{'calls':>7}{'transactions':>14}{'rows in the table':>19}")
print("-" * 64)
for name, design in DESIGNS:
    conn = build()
    calls, commits = design(conn)
    rows = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    print(f"{name:<24}{calls:>7,}{commits:>14,}{rows:>19,}")
    conn.close()

print()
print("All four put the same four hundred rows in the table. Two of them make")
print("four hundred calls, and the first of those makes four hundred")
print("transactions. A transaction is what the engine has to make durable, so")
print("the first design asks the storage to survive four hundred separate")
print("failures and the others ask it to survive one. That is the cost the count")
print("exposes, and it is not visible in the number of rows or the number of")
print("statements.")
