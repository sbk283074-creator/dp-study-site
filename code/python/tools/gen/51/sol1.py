#!/usr/bin/env python3
"""Exercise 1 -- the deny-list that misses half the payloads.

The obvious defence after reading about injection is to strip the characters
the payloads are made of. This script builds that defence and runs it against
twelve inputs, counting two things: how many inputs it blocks, and how many
inputs still change the query's meaning without using any of the characters it
blocks.
"""
import sqlite3

USERS = [(1, "ada"), (2, "grace"), (3, "alan")]

# input, is this a legitimate value
INPUTS = [
    ("1", True),
    ("2", True),
    ("1 OR 1=1", False),
    ("0 OR 1=1", False),
    ("1 UNION SELECT id, name FROM users", False),
    ("2 OR id>0", False),
    ("1/**/OR/**/1=1", False),
    ("1 OR 0x31=0x31", False),
    ("' OR 1=1 --", False),
    ("1--", False),
    ("1; DROP TABLE users", False),
    ("1 OR 'a'='a", False),
]

# the characters the canonical payloads are made of
DENY = ("'", "--", ";")


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", USERS)
    return conn


def run(conn, sql, params=()):
    try:
        return conn.execute(sql, params).fetchall()
    except (sqlite3.Error, sqlite3.Warning):
        return []


def main():
    hostile = [v for v, ok in INPUTS if not ok]
    benign = [v for v, ok in INPUTS if ok]

    print(f"  inputs                             {len(INPUTS):>3}")
    print(f"  legitimate values                  {len(benign):>3}")
    print(f"  hostile inputs                     {len(hostile):>3}")
    print(f"  the deny-list                      {DENY}")
    print()
    print(f"    {'input':<36}{'kind':>9}{'blocked':>9}{'rows':>6}{'bound':>7}")

    blocked_hostile = 0
    leaked = []
    bound_leaks = []
    bound_ok = 0
    for value, legit in INPUTS:
        blocked = any(c in value for c in DENY)
        conn = fresh()
        if blocked:
            rows = []          # never reached the database
        else:
            rows = run(conn, f"SELECT id, name FROM users WHERE id = {value}")
        bnd = run(conn, "SELECT id, name FROM users WHERE id = ?", (value,))
        conn.close()

        if blocked and not legit:
            blocked_hostile += 1
        if rows and not legit:
            leaked.append(value)
        if bnd and not legit:
            bound_leaks.append(value)
        if bnd and legit:
            bound_ok += 1

        kind = "real" if legit else "hostile"
        print(f"    {value:<36}{kind:>9}{'yes' if blocked else 'no':>9}"
              f"{len(rows):>6}{len(bnd):>7}")

    ran = [v for v in hostile if not any(c in v for c in DENY)]

    print()
    print(f"  hostile inputs the deny-list blocks   {blocked_hostile:>3}"
          f" of {len(hostile)}")
    print(f"  hostile inputs it lets through        {len(ran):>3}")
    print(f"  of those, ones that change the result {len(leaked):>3}")
    print(f"  binding, hostile inputs that leak     {len(bound_leaks):>3}")
    print(f"  binding, legitimate values returned   {bound_ok:>3}"
          f" of {len(benign)}")

    print()
    print("  the ones that got through, and what they used instead of a quote")
    for value in leaked:
        print(f"    {value}")

    print()
    print("  stripping the characters the payloads are made of stops the")
    print("  payloads that are made of those characters. the rest of the")
    print("  grammar is still there, and 'OR' does not need a quote to be")
    print("  an operator.")


if __name__ == "__main__":
    main()
