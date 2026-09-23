"""Chapter 60 -- the pitfall: the index that exists and is not used.

An index on a column, and four predicates against that column. All four
return the right rows, so nothing in the result tells you which plan ran.
The count is of rows the plan visits, derived from the planner's own word for
what it is about to do plus a real count of the rows that match.
"""

import os
import sqlite3
import tempfile

ROWS = 20000
DISTINCT_CITIES = 50


def build():
    path = os.path.join(tempfile.mkdtemp(), "people.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE person (id INTEGER PRIMARY KEY, email TEXT, city TEXT)")
    conn.executemany(
        "INSERT INTO person VALUES (?, ?, ?)",
        [(i, f"user{i:06d}@example.com", f"city-{i % DISTINCT_CITIES:02d}")
         for i in range(ROWS)],
    )
    conn.execute("CREATE INDEX i_person_email ON person(email)")
    conn.execute("CREATE INDEX i_person_city ON person(city)")
    conn.commit()
    return conn


def plan_verb(conn, sql, args):
    """The planner's own word: it either scans the table or searches the index."""
    detail = conn.execute("EXPLAIN QUERY PLAN " + sql, args).fetchall()[0][-1]
    return detail.split()[0].upper()


CASES = [
    ("email = ?", "SELECT id FROM person WHERE email = ?",
     ("user000123@example.com",), "the column on its own"),
    ("lower(email) = ?", "SELECT id FROM person WHERE lower(email) = ?",
     ("user000123@example.com",), "a function wrapped round it"),
    ("email LIKE '%...%'", "SELECT id FROM person WHERE email LIKE ?",
     ("%000123%",), "a pattern starting with a wildcard"),
    ("city = ?", "SELECT id FROM person WHERE city = ?",
     ("city-07",), "a column with 50 distinct values"),
]

conn = build()
print(f"{ROWS:,} rows, an index on email and an index on city")
print()
print(f"{'predicate':<20}{'plan':>8}{'rows visited':>14}{'matches':>8}   {'why':<32}")
print("-" * 85)
for label, sql, args, why in CASES:
    verb = plan_verb(conn, sql, args)
    matches = conn.execute(
        "SELECT COUNT(*) FROM person WHERE " + sql.split("WHERE ", 1)[1], args
    ).fetchone()[0]
    visited = matches if verb == "SEARCH" else ROWS
    print(f"{label:<20}{verb:>8}{visited:>14,}{matches:>8,}   {why:<32}")

print()
print("The first two predicates return exactly the same row. The second one")
print("visits twenty thousand rows to find it, because the index is a sorted")
print("list of the values of the column and `lower(email)` is not a value of")
print("the column -- there is nothing in the index to look up.")
print()
print("The fourth predicate does use the index and still visits four hundred")
print("rows, which is the point the first block made: an index names the rows")
print("that match, and it does not make them cheap when a lot of them match.")
print()
print("Nothing above is an error. Every one of these queries is correct, and")
print("the only place the difference shows up is a plan you have to ask for.")
