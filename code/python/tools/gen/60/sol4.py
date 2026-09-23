"""Chapter 60 -- solution 4. Reading your own writes.

A session reads a balance, another connection changes it, and the session
reads it again. Three designs, and the count is of reads that came back with
a value the database had already replaced. The result is that the staleness
comes from how long the read transaction lives, not from there being a
second connection.
"""

import os
import sqlite3
import tempfile

SESSIONS = 20
START = 100
STEP = 10


def build():
    path = os.path.join(tempfile.mkdtemp(), "session.db")
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, balance INTEGER)")
    conn.execute("INSERT INTO account VALUES (1, ?)", (START,))
    conn.commit()
    conn.close()
    return path


def run(mode):
    """One session, repeated: read, write elsewhere, read again."""
    path = build()
    reader = sqlite3.connect(path, isolation_level=None)
    writer = sqlite3.connect(path, isolation_level=None)
    stale = 0
    first = 0
    second = 0
    for _ in range(SESSIONS):
        source = writer if mode == "route to the writer" else reader
        if mode == "one read transaction":
            reader.execute("BEGIN")
        first = source.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
        writer.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (STEP,))
        second = source.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
        if second == first:
            stale += 1
        if mode == "one read transaction":
            reader.execute("COMMIT")
    reader.close()
    writer.close()
    return stale, first, second


MODES = ["one read transaction", "a transaction per read", "route to the writer"]

print(f"{SESSIONS} sessions, each reading, then a write lands, then reading again")
print()
print(f"{'design':<24}{'reads gone stale':>18}{'last read':>11}{'then':>7}")
print("-" * 60)
for mode in MODES:
    stale, first, second = run(mode)
    print(f"{mode:<24}{stale:>18}{first:>11,}{second:>7,}")

print()
print("The second design reads through a second connection and never goes")
print("stale, so the second connection is not the problem. The first design")
print("holds one read transaction across both reads, and inside that")
print("transaction the value cannot change -- which is the property the")
print("transaction was opened to get. A read that must see the session's own")
print("write needs a transaction that ends before the second read, or a route")
print("to the connection that did the writing.")
