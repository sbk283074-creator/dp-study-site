#!/usr/bin/env python3
"""Chapter 51 demo, part 1 -- binding is a protocol, not a string treatment.

A parameterised query is not a string that has been made safe. It is a
different arrangement: the statement is parsed first, and the values are sent
afterwards, so a value is never parsed as SQL at all. That is why no payload
defeats it, and it is why hand-rolled escaping is a different thing that only
looks like the same thing.

Twelve payloads, each against a fresh in-memory database, so the destructive
one is contained. The counts are exact; nothing is timed.
"""
import sqlite3

PAYLOADS = [
    "ada",
    "' OR '1'='1",
    "' OR 1=1 --",
    "admin'--",
    "' OR 'x'='x",
    "') OR ('1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT id, name FROM secrets --",
    "1 OR 1=1",
    "1; DROP TABLE users",
    "%' OR 1=1 --",
    "' OR 1 LIKE 1 --",
]

USERS = [(1, "ada"), (2, "grace"), (3, "alan"), (4, "edsger"), (5, "barbara")]
SECRETS = [(1, "api-key-9f3a"), (2, "db-password")]


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", USERS)
    conn.execute("CREATE TABLE secrets (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO secrets VALUES (?, ?)", SECRETS)
    return conn


def tables(conn):
    return sorted(r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"))


def main():
    print(f"  users in the table                 {len(USERS):>3} rows")
    print(f"  rows in the secrets table          {len(SECRETS):>3} rows")
    print(f"  payloads                           {len(PAYLOADS):>3}")

    interp_rows, bound_rows = [], []
    interp_dropped, script_dropped = 0, 0

    for p in PAYLOADS:
        conn = fresh()
        try:
            got = conn.execute(
                f"SELECT id, name FROM users WHERE name = '{p}'").fetchall()
        except (sqlite3.Error, sqlite3.Warning):
            got = []
        interp_rows.append(len(got))
        if "users" not in tables(conn):
            interp_dropped += 1
        conn.close()

        conn = fresh()
        got = conn.execute(
            "SELECT id, name FROM users WHERE name = ?", (p,)).fetchall()
        bound_rows.append(len(got))
        conn.close()

        # executescript, by contrast, is happy to run several statements.
        conn = fresh()
        try:
            conn.executescript(
                f"SELECT id, name FROM users WHERE name = '{p}';")
        except (sqlite3.Error, sqlite3.Warning):
            pass
        if "users" not in tables(conn):
            script_dropped += 1
        conn.close()

    print()
    print(f"    {'payload':<46}{'interpolated':>13}{'bound':>7}")
    for p, a, b in zip(PAYLOADS, interp_rows, bound_rows):
        print(f"    {p:<46}{a:>13}{b:>7}")

    print()
    print(f"  rows returned, total               {sum(interp_rows):>3}"
          f" interpolated   {sum(bound_rows):>3} bound")
    print(f"  payloads that returned a row       "
          f"{sum(1 for n in interp_rows if n):>3} interpolated   "
          f"{sum(1 for n in bound_rows if n):>3} bound")
    print(f"  of {len(PAYLOADS)} payloads, the intended answer is 0 rows for every one.")

    print()
    print("  the same payloads through execute() and through executescript()")
    print(f"    tables dropped by execute()      {interp_dropped:>3}")
    print(f"    tables dropped by executescript() {script_dropped:>3}"
          f"   (one statement is allowed to be several)")

    print()
    print("  the bound column is not a smaller number. it is a different")
    print("  arrangement: the statement was parsed before the value existed.")


if __name__ == "__main__":
    main()
