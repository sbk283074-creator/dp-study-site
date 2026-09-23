"""Chapter 60 -- the N+1 problem, counted as round trips.

A parent table and a child table in a real database file, read two ways: one
statement per parent, which is what an object-relational mapping does when you
touch a relationship inside a loop, and one join. The count is of statements
the application sends and of rows it receives. The interesting number is that
the join sends far fewer statements and receives fewer rows, and does the
whole job.
"""

import os
import sqlite3
import tempfile

PARENT_COUNTS = [10, 50, 100, 200]
PER_PARENT = 10


def build(parents):
    """A database with `parents` parent rows and ten children under each."""
    path = os.path.join(tempfile.mkdtemp(), "app.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("CREATE TABLE child (id INTEGER PRIMARY KEY, parent_id INTEGER, label TEXT)")
    conn.executemany(
        "INSERT INTO parent VALUES (?, ?)",
        [(p, f"parent-{p:04d}") for p in range(parents)],
    )
    conn.executemany(
        "INSERT INTO child VALUES (?, ?, ?)",
        [(c, c // PER_PARENT, f"child-{c:05d}") for c in range(parents * PER_PARENT)],
    )
    conn.execute("CREATE INDEX i_child_parent ON child(parent_id)")
    conn.commit()
    return conn


def per_parent(conn):
    """One statement for the parents, then one per parent for its children."""
    statements = 0
    rows = 0
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM parent")
    statements += 1
    found = cur.fetchall()
    rows += len(found)
    for parent_id, _name in found:
        cur.execute("SELECT id, label FROM child WHERE parent_id = ?", (parent_id,))
        statements += 1
        rows += len(cur.fetchall())
    return statements, rows


def one_join(conn):
    """The whole relationship in a single statement."""
    cur = conn.cursor()
    cur.execute(
        "SELECT p.name, c.label FROM parent p JOIN child c ON c.parent_id = p.id"
    )
    return 1, len(cur.fetchall())


print(f"{'parents':>8}{'per-parent stmts':>18}{'rows received':>15}"
      f"{'join stmts':>12}{'join rows':>11}")
print("-" * 64)
for parents in PARENT_COUNTS:
    conn = build(parents)
    stmts, rows = per_parent(conn)
    j_stmts, j_rows = one_join(conn)
    print(f"{parents:>8}{stmts:>18}{rows:>15}{j_stmts:>12}{j_rows:>11}")
    conn.close()

print()
print("Round trips are the number of rows the loop happened to walk, not the")
print("size of the answer. Two hundred parents means two hundred and one")
print("statements and two thousand two hundred rows received, for an answer")
print("of two thousand rows that one statement could have carried.")
