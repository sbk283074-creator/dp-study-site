#!/usr/bin/env python3
"""Chapter 51 demo, part 10 -- an escaper only works where you remembered to quote.

The habit this chapter is about is real: escape the quotes before you build
the statement. It is also incomplete in a way that is invisible when you test
it in the place you wrote it, because the escaper's coverage is not a property
of the escaper. It is a property of the call site.

Twelve payloads, six of which were written for a quoted context and six of
which were written for a numeric one. The escaper is the standard one: double
the quote. Each payload is run against a fresh database.
"""
import sqlite3

# payload, the context it was written for, is this a legitimate value?
PAYLOADS = [
    ("ada", "quoted", True),
    ("' OR '1'='1", "quoted", False),
    ("' OR 1=1 --", "quoted", False),
    ("admin'--", "quoted", False),
    ("x' OR 'x'='x", "quoted", False),
    ("' UNION SELECT id, name FROM secrets --", "quoted", False),
    ("3", "numeric", True),
    ("0 OR 1=1", "numeric", False),
    ("1 OR 1=1", "numeric", False),
    ("0; DROP TABLE users", "numeric", False),
    ("1 UNION SELECT id, name FROM secrets", "numeric", False),
    ("9 OR 9=9", "numeric", False),
]

USERS = [(1, "ada"), (2, "grace"), (3, "alan")]
SECRETS = [(1, "api-key-9f3a")]


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", USERS)
    conn.execute("CREATE TABLE secrets (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO secrets VALUES (?, ?)", SECRETS)
    return conn


def escape_quotes(value):
    return value.replace("'", "''")


def run(conn, sql, params=()):
    try:
        return conn.execute(sql, params).fetchall()
    except (sqlite3.Error, sqlite3.Warning):
        return []


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print("  the escaper                        value.replace(\"'\", \"''\")")
    print()
    print(f"    {'payload':<44}{'context':>9}{'escaped':>9}{'bound':>7}")

    escaped_rows = {"quoted": 0, "numeric": 0}
    escaped_leaks = {"quoted": 0, "numeric": 0}
    bound_leaks = 0
    real_rows = 0
    for p, ctx, legit in PAYLOADS:
        e = escape_quotes(p)
        conn = fresh()
        if ctx == "quoted":
            esc = run(conn, f"SELECT id, name FROM users WHERE name = '{e}'")
            bnd = run(conn, "SELECT id, name FROM users WHERE name = ?", (p,))
        else:
            esc = run(conn, f"SELECT id, name FROM users WHERE id = {e}")
            bnd = run(conn, "SELECT id, name FROM users WHERE id = ?", (p,))
        conn.close()
        # a leak is rows coming back from a payload that was not a real value
        if esc and not legit:
            escaped_leaks[ctx] += 1
        if legit:
            real_rows += len(esc)
        else:
            escaped_rows[ctx] += len(esc)
        if bnd and not legit:
            bound_leaks += 1

        print(f"    {p:<44}{ctx:>9}{len(esc):>9}{len(bnd):>7}")

    nq = sum(1 for _, c, _ in PAYLOADS if c == "quoted")
    nn = len(PAYLOADS) - nq
    print()
    print(f"  the escaper, in the context it was written for   "
          f"{nq - escaped_leaks['quoted']} of {nq} payloads neutralised")
    print(f"  the escaper, in the other context                "
          f"{nn - escaped_leaks['numeric']} of {nn} payloads neutralised")
    print(f"  binding, in both contexts                        "
          f"{len(PAYLOADS) - bound_leaks} of {len(PAYLOADS)} neutralised")

    print()
    print(f"  rows returned by the payloads       "
          f"{escaped_rows['quoted'] + escaped_rows['numeric']}"
          f"   ({escaped_rows['quoted']} from the quoted context)")
    print(f"  rows returned by the real values    {real_rows}"
          f"   (what the query was asked for)")
    print()
    print("  there are no quotes in '0 OR 1=1', so there is nothing for the")
    print("  escaper to do, and the code that calls it looks exactly like the")
    print("  code that calls it correctly.")
    print()
    print("  an escaper is a treatment for one context. binding is a treatment")
    print("  for every context, which is why it is the one to standardise on.")


if __name__ == "__main__":
    main()
