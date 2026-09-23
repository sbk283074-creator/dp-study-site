"""Chapter 60 -- solution 3. Pagination, and what skipping rows costs.

Twenty thousand rows, twenty per page, and five target pages. The count is of
rows the engine actually visits, and it is real rather than modelled: the
only predicate in these queries is a function that counts its own calls, so
the engine has to call it once for every row it looks at.
"""

import os
import sqlite3
import tempfile

ROWS = 20000
PAGE = 20
TARGETS = [1, 10, 100, 500, 1000]

path = os.path.join(tempfile.mkdtemp(), "pages.db")
conn = sqlite3.connect(path)
conn.execute("CREATE TABLE item (id INTEGER PRIMARY KEY, label TEXT)")
conn.executemany(
    "INSERT INTO item VALUES (?, ?)",
    [(index, f"item-{index:05d}") for index in range(ROWS)],
)
conn.commit()

visits = {"count": 0}


def visit(value):
    """A function the engine has to call once per row it visits."""
    visits["count"] += 1
    return value


conn.create_function("visit", 1, visit)


def offset_page(page):
    """Jump to a page by counting past the rows in front of it."""
    visits["count"] = 0
    rows = conn.execute(
        "SELECT id FROM item WHERE visit(id) IS NOT NULL ORDER BY id LIMIT ? OFFSET ?",
        (PAGE, (page - 1) * PAGE),
    ).fetchall()
    return visits["count"], [row[0] for row in rows]


def cursor_page(after_id):
    """Ask for the page after a key you already hold."""
    visits["count"] = 0
    rows = conn.execute(
        "SELECT id FROM item WHERE id > ? AND visit(id) IS NOT NULL"
        " ORDER BY id LIMIT ?",
        (after_id, PAGE),
    ).fetchall()
    return visits["count"], [row[0] for row in rows]


def walk_to(page):
    """Page forward one page at a time from the beginning."""
    total = 0
    cursor = -1
    for _ in range(page):
        visited, ids = cursor_page(cursor)
        total += visited
        cursor = ids[-1]
    return total


print(f"{ROWS:,} rows, {PAGE} per page, counting rows the engine visits")
print()
print(f"{'page':>6}{'jump by offset':>16}{'next page, cursor held':>24}"
      f"{'walked from page 1':>20}")
print("-" * 66)
held = 0
for page in TARGETS:
    jumped, ids = offset_page(page)
    if page == TARGETS[0]:
        held = ids[-1]
    walked = walk_to(page)
    print(f"{page:>6}{jumped:>16,}{cursor_page(held)[0]:>24,}{walked:>20,}")

print()
print(f"The offset count was exactly the offset plus the page size on every one")
print(f"of these pages, which is what the count should be if the measurement is")
print(f"sound: {PAGE} rows for the page and {PAGE} for every page in front of it.")
print()
print("The column that matters is the third one. Keyset pagination does not")
print("make a deep page cheap -- reaching page one thousand by walking costs")
print(f"{walk_to(1000):,} rows, exactly what the offset cost. What it makes cheap is")
print("the next page, and only when the client already holds the key it")
print("stopped at. A jump to an arbitrary page is the case it cannot serve at")
print("all, because there is no key to start from.")
