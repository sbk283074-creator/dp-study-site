#!/usr/bin/env python3
"""Chapter 51 demo, part 11 -- the report that tested for quotes.

A search box is the classic injection surface and the classic scoped test. The
standard payload set for SQL injection is built from quotes, because the
canonical payload is one, and a test built from the canonical payload finds
the canonical bug.

This script runs twelve inputs through a real search feature. Two of the twelve
contain a quote. Counting them is easy. Counting the ones that actually leak is
harder, because "leaked" does not mean the same thing in both slots: in the
search term it means rows came back that should not have, and in the sort key it
means a key ran that is not on the list. The row count is identical either way,
which is exactly why the sort bugs survive a report that only counts rows.
"""
import sqlite3

CARDS = [
    (1, "hola", "hello", "greetings"),
    (2, "adios", "goodbye", "greetings"),
    (3, "gracias", "thank you", "polite"),
    (4, "por favor", "please", "polite"),
    (5, "buenos dias", "good morning", "greetings"),
]

# input, the slot it is tried in
INPUTS = [
    ("hola", "term"),
    ("%", "term"),
    ("_", "term"),
    ("%%", "term"),
    ("' OR '1'='1", "term"),
    ("' UNION SELECT id, front FROM cards --", "term"),
    ("front", "sort"),
    ("back", "sort"),
    ("id", "sort"),
    ("(SELECT front FROM cards)", "sort"),
    ("CASE WHEN 1=1 THEN front ELSE back END", "sort"),
    ("front DESC, back", "sort"),
]

ALLOWED_SORT = {"front", "back", "id"}
QUOTE = "'"


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE cards (id INTEGER, front TEXT, back TEXT, tag TEXT)")
    conn.executemany("INSERT INTO cards VALUES (?, ?, ?, ?)", CARDS)
    return conn


def run(conn, sql):
    try:
        return conn.execute(sql).fetchall()
    except (sqlite3.Error, sqlite3.Warning):
        return None


def main():
    print(f"  cards in the table                 {len(CARDS):>3}")
    print(f"  inputs                             {len(INPUTS):>3}")
    print(f"  the sort allow-list                "
          f"{len(ALLOWED_SORT)} keys")

    results = []
    for value, slot in INPUTS:
        conn = fresh()
        if slot == "term":
            # what a literal substring search should return
            expected = [c[0] for c in CARDS if value in c[1]]
            rows = run(conn, f"SELECT id, front FROM cards WHERE front LIKE '%{value}%'")
            got = None if rows is None else [r[0] for r in rows]
            if rows is None:
                verdict = "rejected"
            elif got != expected:
                verdict = "leak: matched everything"
            else:
                verdict = "ok"
        else:
            base = run(conn, "SELECT id, front FROM cards")
            rows = run(conn, f"SELECT id, front FROM cards ORDER BY {value}")
            if rows is None:
                verdict = "rejected"
            elif value not in ALLOWED_SORT:
                verdict = "leak: key not on the list"
            else:
                moved = [r[0] for r in rows] != [r[0] for r in base]
                verdict = "ok (reordered)" if moved else "ok (same order)"
        conn.close()
        results.append((value, slot, rows, verdict))

    print()
    print(f"    {'input':<42}{'slot':>7}{'rows':>7}  {'verdict'}")
    for value, slot, rows, verdict in results:
        n = "-" if rows is None else str(len(rows))
        print(f"    {value:<42}{slot:>7}{n:>7}  {verdict}")

    quoted = [v for v, _ in INPUTS if QUOTE in v]
    leaked = [(v, slot, verdict) for v, slot, _, verdict in results
              if verdict.startswith("leak")]
    quoted_leaks = [v for v, _, _ in leaked if QUOTE in v]
    term_inputs = [v for v, s in INPUTS if s == "term"]
    sort_inputs = [v for v, s in INPUTS if s == "sort"]
    sort_leaks = [v for v, s, _ in leaked if s == "sort"]
    allowed = [v for v in sort_inputs if v in ALLOWED_SORT]

    print()
    print(f"  inputs containing a quote            {len(quoted):>3} of {len(INPUTS)}")
    print(f"  inputs that leaked                   {len(leaked):>3}")
    print(f"  of the leaking inputs, quoting        {len(quoted_leaks):>3}")
    print(f"  leaking in the term slot             {len(leaked) - len(sort_leaks):>3}"
          f" of {len(term_inputs)}")
    print(f"  leaking in the sort slot             {len(sort_leaks):>3}"
          f" of {len(sort_inputs)}")

    print()
    print("  every leaking input, and what it did")
    for value, slot, verdict in leaked:
        print(f"    {value:<42}{slot:>7}   {verdict}")

    print()
    print(f"  a test built from quotes covers {len(quoted_leaks)}"
          f" of the {len(leaked)} inputs that actually leak.")
    print(f"  all {len(leaked)} leaking inputs return "
          f"{len(CARDS)} rows, so a row count cannot see them.")
    print(f"  the allow-list accepts {len(allowed)} of the {len(sort_inputs)} "
          f"sort inputs and 0 hostile ones.")


if __name__ == "__main__":
    main()
