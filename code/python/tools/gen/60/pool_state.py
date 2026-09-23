"""Chapter 60 -- what a pooled connection carries between borrowers.

A pool exists because opening a connection is work. A connection is not a
stateless handle, though: it holds a transaction, and a transaction that is
still open when the borrower returns the connection belongs to whoever
borrows it next. The count is of borrowers that inherited one, of rows a
commit made durable that the committer did not write, and of connections
opened.
"""

import os
import sqlite3
import tempfile

BORROWERS = 4


def run(mode):
    """One pass of four borrowers over one connection, or over four."""
    path = os.path.join(tempfile.mkdtemp(), "pool.db")

    setup = sqlite3.connect(path, isolation_level=None)
    setup.execute("CREATE TABLE audit (id INTEGER PRIMARY KEY, who TEXT, what TEXT)")
    setup.commit()
    setup.close()

    opened = 0

    def connect():
        nonlocal opened
        opened += 1
        return sqlite3.connect(path, isolation_level=None)

    conn = None
    inherited = 0

    for index in range(BORROWERS):
        who = f"borrower-{index + 1}"
        if mode == "no pool":
            conn = connect()
        elif conn is None:
            conn = connect()
        elif conn.in_transaction:
            inherited += 1

        conn.execute("INSERT INTO audit (who, what) VALUES (?, ?)", (who, "own work"))
        conn.commit()

        if index == 0:
            # a borrower that opened a transaction for a second write and
            # returned the connection without finishing it
            conn.execute("BEGIN")
            conn.execute("INSERT INTO audit (who, what) VALUES (?, ?)", (who, "draft"))

        if mode == "rollback on return" and conn.in_transaction:
            conn.rollback()
        if mode == "no pool":
            # the borrower closes it, and the unfinished write goes with it
            conn.close()
            conn = None

    final = sqlite3.connect(path)
    drafts = final.execute(
        "SELECT COUNT(*) FROM audit WHERE what = 'draft'"
    ).fetchone()[0]
    rows = final.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
    final.close()
    if conn is not None:
        conn.close()
    return opened, inherited, drafts, rows


MODES = ["no reset", "rollback on return", "no pool"]

print(f"{BORROWERS} borrowers, one of them returns a connection with a write unfinished")
print()
print(f"{'design':<22}{'opened':>7}{'inherited':>10}{'drafts durable':>16}{'rows at end':>12}")
print("-" * 67)
for mode in MODES:
    opened, inherited, drafts, rows = run(mode)
    print(f"{mode:<22}{opened:>7}{inherited:>10}{drafts:>16}{rows:>12}")

print()
print("The pool opened one connection for four borrowers, and one of them took")
print("the connection in a state the previous borrower left it in. The count of")
print("inherited transactions is one, not three, because the borrower that")
print("inherited it committed -- and its commit made somebody else's unfinished")
print("write durable, which is the row that should not be there.")
print()
print("Resetting the connection on the way back costs one call and removes both")
print("counts. Not pooling costs three extra opens and removes them too, which")
print("is the honest comparison: a pool is a decision about opens, and the")
print("reset is part of the price rather than an optional extra.")
