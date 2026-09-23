"""Chapter 60 -- the update that loses a write, and the three ways to write it.

Two connections to one database file, both asked to add to the same balance.
The count is of units that disappeared and of pairs where the answer is wrong,
and the result is that wrapping the read and the write in a transaction does
not help, because the read already happened before the other writer committed.
"""

import os
import sqlite3
import tempfile

PAIRS = 20
START = 100


def fresh():
    """A database file with one account holding `START`."""
    path = os.path.join(tempfile.mkdtemp(), "bank.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, balance INTEGER)")
    conn.execute("INSERT INTO account VALUES (1, ?)", (START,))
    conn.commit()
    conn.close()
    return path


def read_then_write(path, first, second):
    """Both callers read, then each writes what it read plus its own delta."""
    a = sqlite3.connect(path)
    b = sqlite3.connect(path)
    a_read = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    b_read = b.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.execute("UPDATE account SET balance = ? WHERE id = 1", (a_read + first,))
    a.commit()
    b.execute("UPDATE account SET balance = ? WHERE id = 1", (b_read + second,))
    b.commit()
    final = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.close()
    b.close()
    return final, 0


def add_in_statement(path, first, second):
    """The update reads the column it is writing, inside the statement."""
    a = sqlite3.connect(path)
    b = sqlite3.connect(path)
    a.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (first,))
    a.commit()
    b.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (second,))
    b.commit()
    final = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.close()
    b.close()
    return final, 0


def compare_and_set(path, first, second):
    """Write only if the column still holds what you read, and count refusals."""
    a = sqlite3.connect(path)
    b = sqlite3.connect(path)
    refusals = 0
    a_read = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    b_read = b.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.execute(
        "UPDATE account SET balance = ? WHERE id = 1 AND balance = ?",
        (a_read + first, a_read),
    )
    a.commit()
    cur = b.execute(
        "UPDATE account SET balance = ? WHERE id = 1 AND balance = ?",
        (b_read + second, b_read),
    )
    b.commit()
    if not cur.rowcount:
        refusals += 1
        b_read = b.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
        b.execute(
            "UPDATE account SET balance = ? WHERE id = 1 AND balance = ?",
            (b_read + second, b_read),
        )
        b.commit()
    final = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.close()
    b.close()
    return final, refusals


DESIGNS = [
    ("read, then write", read_then_write),
    ("add in the statement", add_in_statement),
    ("compare and set", compare_and_set),
]

ASKED = sum((30 + index) + (50 + index) for index in range(PAIRS))

print(f"{PAIRS} pairs, each on a fresh account holding {START}, deltas 30+i and 50+i")
print(f"each pair should end at 180 + 2i, so {START + 80} to {START + 80 + 2 * (PAIRS - 1)}")
print(f"{ASKED:,} units asked for across the {PAIRS} pairs")
print()
print(f"{'design':<22}{'last pair':>10}{'units lost':>12}{'pairs wrong':>13}{'refusals':>10}")
print("-" * 67)

results = []
for name, design in DESIGNS:
    last = 0
    lost = 0
    wrong = 0
    refusals = 0
    for index in range(PAIRS):
        first = 30 + index
        second = 50 + index
        final, refused = design(fresh(), first, second)
        expected = START + first + second
        last = final
        lost += expected - final
        wrong += 1 if final != expected else 0
        refusals += refused
    results.append((name, last, lost, wrong, refusals))

for name, last, lost, wrong, refusals in results:
    print(f"{name:<22}{last:>10}{lost:>12}{wrong:>13}{refusals:>10}")

worst = results[0][2]
print()
print(f"The first design lost {worst:,} of the {ASKED:,} units the pairs asked for,")
print(f"which is {worst / ASKED:.1%} of them, and it was wrong on all {results[0][3]} pairs.")
print()
print("The first design is not slow, it is wrong, and no transaction around the")
print("read and the write changes that: the value was read before the other")
print("writer committed, so the arithmetic was done on a number that had")
print("already stopped being true. A transaction gives you atomicity, not")
print("freshness. The second design makes the database do the arithmetic, so")
print("there is no stale value to be wrong about. The third keeps the")
print("arithmetic in the application and makes the write refuse when the")
print("number it read has moved, which is the shape you need when the new")
print("value cannot be expressed as an increment.")
