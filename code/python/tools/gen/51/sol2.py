#!/usr/bin/env python3
"""Exercise 2 -- the search box that is bound, and still wrong.

A parameterised query fixes injection. It does not fix the other half of the
same problem: the value you pass in is not always a value. In a LIKE pattern
the characters % and _ are syntax, so a bound parameter carrying them still
changes what the query means. Nothing is escaped by binding, because there is
nothing to escape -- the parameter is delivered as data, and it is data that
happens to be an operator.

Ten search terms, three ways of running each one, and a count of how often each
way agrees with a plain substring search.
"""
import sqlite3

CARDS = [
    (1, "hola"),
    (2, "adios"),
    (3, "gracias"),
    (4, "por favor"),
    (5, "buenos dias"),
]

TERMS = [
    "hola",
    "a",
    "buenos dias",
    "%",
    "_",
    "%%",
    "hol%",
    "hola_",
    "\\",
    "adios",
]


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE cards (id INTEGER, front TEXT)")
    conn.executemany("INSERT INTO cards VALUES (?, ?)", CARDS)
    return conn


def run(conn, sql, params=()):
    try:
        return [r[0] for r in conn.execute(sql, params).fetchall()]
    except (sqlite3.Error, sqlite3.Warning):
        return None


def escape_like(value):
    """Make a value mean itself inside a LIKE pattern."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def main():
    print(f"  cards                              {len(CARDS):>3}")
    print(f"  search terms                       {len(TERMS):>3}")
    print()
    print(f"    {'term':<14}{'literal':>9}{'LIKE ?':>9}{'ESCAPE':>9}")

    over = []
    exact = 0
    for term in TERMS:
        conn = fresh()
        literal = sorted(c[0] for c in CARDS if term in c[1])
        plain = run(conn, "SELECT id FROM cards WHERE front LIKE ?",
                    (f"%{term}%",))
        esc = run(conn, "SELECT id FROM cards WHERE front LIKE ? ESCAPE '\\'",
                  (f"%{escape_like(term)}%",))
        conn.close()

        if plain != literal:
            over.append(term)
        if esc == literal:
            exact += 1

        print(f"    {term:<14}{len(literal):>9}{len(plain):>9}{len(esc):>9}")

    print()
    print(f"  terms where binding alone over-matches   {len(over):>3}"
          f" of {len(TERMS)}")
    for term in over:
        print(f"    {term}")
    print(f"  terms where the escaping version is exact {exact:>3}"
          f" of {len(TERMS)}")

    print()
    print("  both columns are bound. the difference is not escaping -- the")
    print("  value is never parsed as SQL in either one. it is that LIKE")
    print("  gives three characters a meaning, and a bound parameter does")
    print("  not take that meaning away. binding removes the syntax from")
    print("  the statement; it cannot remove the syntax from the value.")


if __name__ == "__main__":
    main()
