"""Chapter 19 -- one query, two ways to build it, and six inputs.

A users table with three rows. Six names are looked up, one ordinary and five
written to break the query. The count is of rows returned, and of inputs that
produced an answer for a name that is not in the table.
"""

import sqlite3

ROWS = [("ada", "admin"), ("bob", "user"), ("eve", "user")]

INPUTS = [
    ("ada", "the ordinary case"),
    ("ada' --", "closes the quote and comments out the rest"),
    ("ada' OR '1'='1", "adds a condition that is always true"),
    ("nobody' OR '1'='1' --", "always true, for a name that is absent"),
    ("x' OR name LIKE '%' --", "always true, written differently"),
    ("x' UNION SELECT 'admin' --", "adds a row that was never stored"),
]


def fresh():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE users (name TEXT, role TEXT)")
    connection.executemany("INSERT INTO users VALUES (?, ?)", ROWS)
    return connection


def count(connection, sql, parameters=()):
    try:
        return len(connection.execute(sql, parameters).fetchall())
    except sqlite3.Error as error:
        return type(error).__name__


formatted_connection = fresh()
parameterised_connection = fresh()

rows = []
for text, _ in INPUTS:
    formatted = count(formatted_connection,
                      f"SELECT role FROM users WHERE name = '{text}'")
    parameterised = count(parameterised_connection,
                          "SELECT role FROM users WHERE name = ?", (text,))
    rows.append((text, formatted, parameterised))


def total(column):
    return sum(row[column] for row in rows if isinstance(row[column], int))


def answered(column):
    return sum(1 for row in rows
               if isinstance(row[column], int) and row[column] > 0)


print(f"{len(rows)} inputs against a table of {len(ROWS)} rows")
print()
print(f"{'input':<28}{'formatted':>11}{'parameterised':>15}")
print("-" * 54)
for text, formatted, parameterised in rows:
    print(f"{text:<28}{formatted:>11}{parameterised:>15}")

print()
print(f"{'what is counted':<44}{'count':>8}")
print("-" * 52)
print(f"{'inputs tried':<44}{len(rows):>8}")
print(f"{'inputs that returned rows, formatted':<44}{answered(1):>8}")
print(f"{'inputs that returned rows, parameterised':<44}{answered(2):>8}")
print(f"{'rows returned in total, formatted':<44}{total(1):>8}")
print(f"{'rows returned in total, parameterised':<44}{total(2):>8}")

print()
print("The two tables start identical and end different, and the only")
print("difference is that one query was built by joining strings and the other")
print("was handed the value separately. In the formatted column the input is")
print("part of the query, so a quote in it closes the string the author opened")
print("and whatever follows is read as SQL. The parameterised column never")
print("gives the database a chance to misread: the statement is fixed before")
print("the value arrives, and the value can only ever be a value.")
print()
print(f"Every one of the {len(rows)} inputs returned rows under the first query, and")
print(f"{total(1)} rows came back in total from a table of {len(ROWS)}. Under the second, only")
print(f"the one real name matched, and {total(2)} row came back. The two inputs that")
print("matter most are the last two: one of them returned every row in the")
print("table, and the other returned a row that does not exist -- a fabricated")
print("role handed to the caller as though the database had said it.")
print()
print("The rule has no exceptions worth making. SQL is code; values are data;")
print("they travel on different channels, and the placeholder is the channel.")
print("This is not about escaping quotes -- escaping is a blocklist of the")
print("characters somebody thought of, and the next encoding finds another one.")
print("A placeholder is a fixed statement, and a fixed statement cannot be")
print("rewritten by its input.")
