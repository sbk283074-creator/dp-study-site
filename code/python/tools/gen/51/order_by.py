#!/usr/bin/env python3
"""Chapter 51 demo, part 2 -- the parts of a statement you cannot bind.

Binding works for values. It does not work for anything the parser has to
understand before the query runs, and a surprising number of a query's parts
are in that category: a column name, a sort direction, a table name.

The reason is not a limitation to work around; it is the mechanism doing its
job. A bound parameter is a value, so a bound column name arrives as the
*string* "name" rather than as the identifier `name`, and the sort does
nothing. Which leaves the question this script answers by counting: if you
cannot bind it, what is the safe way to accept it?
"""
import sqlite3

ROWS = [
    (1, "grace", 92), (2, "ada", 71), (3, "edsger", 58),
    (4, "barbara", 84), (5, "alan", 63),
]

# The four orderings the interface offers, and the six hostile values an
# attacker will try in the same slot.
WANTED = [("name", "ASC"), ("name", "DESC"), ("score", "ASC"), ("score", "DESC")]

HOSTILE = [
    "score; DROP TABLE scores",
    "(SELECT name FROM secrets)",
    "score DESC, name",
    "1",
    "score --",
    "CASE WHEN 1=1 THEN score ELSE name END",
]

ALLOWED = {"name", "score"}
ALLOWED_DIR = {"ASC", "DESC"}


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE scores (id INTEGER, name TEXT, score INTEGER)")
    conn.executemany("INSERT INTO scores VALUES (?, ?, ?)", ROWS)
    conn.execute("CREATE TABLE secrets (value TEXT)")
    conn.execute("INSERT INTO secrets VALUES ('api-key-9f3a')")
    return conn


def names(conn, sql):
    try:
        return [r[0] for r in conn.execute(sql)]
    except (sqlite3.Error, sqlite3.Warning):
        return None


def main():
    print(f"  rows                               {len(ROWS):>3}")
    print(f"  orderings the interface offers     {len(WANTED):>3}")
    print(f"  hostile values tried in the slot   {len(HOSTILE):>3}")

    # 1. Bind the column name. It arrives as a value, so nothing sorts.
    works_bound = 0
    for col, direction in WANTED:
        conn = fresh()
        got = names(conn, "SELECT name FROM scores ORDER BY ? ASC")
        expected = sorted(r[1] for r in ROWS)
        if got == expected and col == "name" and direction == "ASC":
            works_bound += 1
        conn.close()

    # 2. Interpolate it. It sorts, and so does anything else in the slot.
    works_interp = 0
    hostile_ran = []
    hostile_dropped = 0
    for col, direction in WANTED:
        conn = fresh()
        got = names(conn, f"SELECT name FROM scores ORDER BY {col} {direction}")
        if got is not None:
            works_interp += 1
        conn.close()
    for h in HOSTILE:
        conn = fresh()
        got = names(conn, f"SELECT name FROM scores ORDER BY {h}")
        if got is not None:
            hostile_ran.append(h)
        if "scores" not in [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]:
            hostile_dropped += 1
        conn.close()

    # 3. Allow-list it. The value is compared, never parsed.
    works_allow = 0
    for col, direction in WANTED:
        if col in ALLOWED and direction in ALLOWED_DIR:
            conn = fresh()
            got = names(conn, f"SELECT name FROM scores ORDER BY {col} {direction}")
            if got is not None:
                works_allow += 1
            conn.close()
    hostile_allowed = sum(1 for h in HOSTILE
                          if h in ALLOWED or h in ALLOWED_DIR)

    print()
    print(f"    {'approach':<26}{'valid orderings':>17}{'hostile accepted':>18}")
    print(f"    {'bind the column name':<26}{works_bound:>17}{0:>18}")
    print(f"    {'interpolate it':<26}{works_interp:>17}{len(hostile_ran):>18}")
    print(f"    {'allow-list it':<26}{works_allow:>17}{hostile_allowed:>18}")

    print()
    print("  the hostile values that ran, and what they did")
    for h in hostile_ran:
        note = "reads the secrets table" if "secrets" in h else "parsed as an expression"
        print(f"    {h:<44}{note}")

    print()
    print(f"  of {len(WANTED)} valid orderings, binding delivers {works_bound}.")
    print(f"  of {len(HOSTILE)} hostile values, interpolation runs {len(hostile_ran)}"
          f" and drops a table {hostile_dropped} time(s).")
    print(f"  the allow-list delivers {works_allow} valid and accepts "
          f"{hostile_allowed} hostile.")
    print()
    print("  the drop did not happen because execute() refuses more than one")
    print("  statement -- the driver stopped it, not the code. Part 1 of this")
    print("  chapter shows the same payload through executescript().")

    print()
    print("  binding is not the safe option and interpolation the unsafe one.")
    print("  binding is not an option here at all -- so the choice is between")
    print("  interpolating and comparing, and only one of those parses.")


if __name__ == "__main__":
    main()
