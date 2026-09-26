#!/usr/bin/env python3
"""Generate chapters/32-jdbc-and-a-real-database.md.

    python3 tools/gen/32/gen.py

JDBC is a service-provider interface: `java.sql` is almost entirely interfaces and
the driver is a jar you add. The JDK ships no driver, so this chapter proves that
with the real API first, then builds a small engine behind JDBC-*shaped* types so
that the rest -- placeholders, the cursor, SQLException, resources -- is still
verified rather than asserted.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "32-jdbc-and-a-real-database.md")

BLOCKS = {
    "nodriver": gen.run("NoDriver.java"),
    "core": gen.run_files(["DbDemo.java", "Db.java", "Rows.java"]),
    "injection": gen.sh("injection.sh", "run-project"),
    "types": gen.sh("types.sh", "run-project"),
    "checked": gen.bad("Unreported.java", "unreported exception SQLException"),
    "resource": gen.warn("UnusedResource.java", "never referenced"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 32
part: 4
title: JDBC and a Real Database
summary: JDBC is a service-provider interface, and the JDK ships no driver — proved with the real API before anything else. Then the shape of a result set, the one-based cursor, why the ? placeholder is what prevents SQL injection, SQLException as a checked exception, and why every JDBC object belongs in try-with-resources.
minutes: 80
tags: [jdbc, sql, database, prepared-statement, sql-injection, sqlexception]
---

Every chapter so far has been verifiable with the JDK alone. This is the first one where that stops
being free, and the reason is worth stating before anything else: **JDBC is a service-provider
interface, not a database.** `java.sql` is a package of interfaces — `Connection`, `Statement`,
`PreparedStatement`, `ResultSet` — plus `DriverManager`, which finds an implementation at runtime. The
implementation is the driver, it is a jar you add, and the JDK does not ship one.

Here is that fact, measured rather than asserted:

@@nodriver@@

Zero drivers, and a `SQLException` whose message is the whole lesson: *no suitable driver*. Adding
SQLite, H2 or PostgreSQL to a real project means adding one jar, and everything below is the code you
write once you have.

That constraint shapes this chapter. `ResultSet` alone has around 190 methods, and implementing it by
hand is not a lesson about databases — it is a lesson about typing. So the rest of the chapter uses a
small engine behind **JDBC-shaped** types: one-based column numbers, a cursor that starts before the
first row, typed getters, `?` placeholders, and the real `java.sql.SQLException`. The shape is what
transfers; the engine is only what makes it checkable here.

## The four objects

| Type | What it is | Lifetime |
|---|---|---|
| `DriverManager` | finds a `Driver` for a URL and hands you a connection | one per JVM |
| `Connection` | a session with the database; transactions live here | one per unit of work |
| `PreparedStatement` | one SQL statement, parsed once, with `?` slots for values | one per statement |
| `ResultSet` | the rows a query returned, behind a cursor | one per query |

The URL is how the driver is chosen: `jdbc:sqlite:bulletin.db`, `jdbc:postgresql://localhost/bulletin`,
`jdbc:h2:mem:bulletin`. Everything after `jdbc:` is the driver's business, which is why the same code
works against three databases and three jars.

@@core@@

Four things in that transcript are JDBC's shape, and all four are still true with a real driver:

1. **`ResultSet` is a cursor, not a list.** It starts *before* the first row. `next()` moves it and
   returns whether there is a row there, so `while (rows.next())` is the whole idiom — and forgetting
   the first `next()` is the single most commonJDBC bug, because reading before it throws rather than
   returning null.
2. **Column numbers start at 1.** `getString(1)` is the first column. This is genuinely unusual in
   Java and there is no way to make it less surprising except to say it often.
3. **A query and an update are different calls.** `query` returns rows; `update` returns a *count of
   rows affected*. That count is the only confirmation you get that your `WHERE` matched what you
   thought it matched.
4. **`SELECT COUNT(*)` is a query with one row.** You still have to call `next()` before reading it.

## The `?` placeholder is the whole security story

@@injection@@

Read the concatenated statement carefully. The value contained `'); DROP TABLE people; --`, and once
the string is concatenated it is not a value any more — it is *part of the SQL*, and the database will
parse and run it. That is SQL injection, and it is not an exotic attack: it is what happens when a
value reaches the parser.

This engine has no `DROP`, so it rejected the statement. A real database would have dropped the table.
The bound version stored the hostile string verbatim and returned it unchanged, because a placeholder
changes where the value goes: **the statement is parsed before the value arrives**, so the value has
no opportunity to become syntax. It travels in its own channel, as data.

The rule that follows has no exceptions worth naming: **never concatenate a value into SQL.** Not a
number, not a value you validated, not one from a dropdown. `PreparedStatement` with `?` is not a
performance optimisation you can skip when it is inconvenient — it is the only thing separating your
data from your code.

:::danger A placeholder cannot parameterise an identifier
`?` is a slot for a *value*. It cannot be a table name, a column name, or a sort direction, because
those are part of the statement's syntax and must be decided before parsing. `SELECT * FROM ?` is not
a thing. When a column name genuinely has to vary — a configurable sort field — the only safe move is
an allowlist: map the user's input to one of a fixed set of literal SQL strings you wrote, and never
put the input itself in the statement. That is the same rule as Chapter 29's URL scheme allowlist, and
it fails closed for the same reason.
:::

## Types, nulls and what the cursor will not do

@@types@@

Three separate lessons hide in that transcript.

**A typo in SQL is a runtime error, not a compile error.** `... FROM notes ORDER` is a `SQLException`
about a missing table. The compiler cannot check a string, which is why a data layer wants its SQL in
one place where it can be read and tested, and why an ORM exists at all — at the cost of hiding the
SQL, which is why this book is not using one.

**`null` needs a type-aware getter.** `getInt` on a `null` column returns `0` here; JDBC's contract is
that `getInt` returns `0` and you then call `wasNull()` to find out whether it was really `null`. That
is a design from 1997 and it is still the interface, so a nullable numeric column needs the extra
check. `getString` has no such problem: it returns `null`, and `null` is a perfectly good `String`
answer.

**Reading out of bounds throws.** Column 9 of a three-column result is a `SQLException`, and so is
reading after `close()`. Both are programming errors, and both arrive as the same checked exception
the environment errors do — which is the cost of `SQLException` covering everything.

## `SQLException` is checked, and that is the design

@@checked@@

`SQLException` is checked, so every database call is either inside a `try` or inside a method that
declares `throws`. This is Chapter 13's argument applied to the most checked-exception-heavy API in the
JDK, and the honest assessment is that JDBC is the strongest case *for* checked exceptions that Java
has: a database call fails for reasons outside your program's control, constantly, and a language that
lets you forget to handle that would produce worse code.

The cost is real, though, and it is the reason almost every real code base writes one of two things: a
small helper that wraps `SQLException` in an unchecked type of its own, or a data-access layer whose
methods all declare `throws SQLException` and whose callers handle it once. What nobody should write
is `catch (SQLException e) { }` — an empty catch block on the one exception that means "your data did
not arrive".

## Every JDBC object is a resource

@@resource@@

The warning is pedantic in this toy program and load-bearing in a real one. A `Connection` is a socket
to another process; a `Statement` is server-side state; a `ResultSet` is a cursor held open on the
server. Leaking any of them is not a memory leak in your JVM, it is a resource leak in the *database*,
and a database has a hard limit on how many it will give you. `try`-with-resources is not a style
choice here, it is how you give them back:

```java
try (Connection c = DriverManager.getConnection(url);
     PreparedStatement s = c.prepareStatement(sql)) {
    s.setString(1, name);
    try (ResultSet r = s.executeQuery()) {
        while (r.next()) {
            ...
        }
    }
}
```

Note the nesting: the statement's resource block closes before the connection's, because
try-with-resources closes in reverse order of declaration. Getting that backwards — closing the
connection inside the statement's block — is a mistake that fails only under load.

:::pitfall One connection shared across threads
A `Connection` is not thread-safe, and the failure mode is the bad kind: it usually works, and
produces interleaved transactions, mixed-up result sets, or a deadlock in the driver when it does not.
A service therefore does not share one connection; it holds a **pool** and hands one out per unit of
work, which is exactly what Chapter 33 builds. If you take one thing from this chapter into a code
review, make it this: a `Connection` field on a service class is a bug, and the fix is a pool.
:::

:::scenario The search box that returned everyone's data
An internal directory service has a lookup endpoint: given an email, return the user's row. It is
written with concatenation because it started as an admin tool nobody worried about. Someone types
`' OR '1'='1` into the box.

```sh run-project
@@scenario@@
```

With a placeholder, the hostile input is just an email address that does not exist, and the endpoint
returns an empty list — which is what it should have done. With concatenation, the statement that
reaches the database is `... WHERE email = '' OR '1'='1'`, and `'1'='1'` is true for every row, so the
endpoint returns every user in the directory. That is the whole attack, and it is one line of code
away from being impossible.

:::solution
Replace every concatenated statement with a `PreparedStatement`, and make it impossible to go back:

1. **Parameterise every value.** `"SELECT email FROM users WHERE email = ?"` with
   `setString(1, email)`. Not sanitised, not escaped — *bound*, so it is never parsed.
2. **Grep for the pattern that reintroduces it.** `"` + `+` inside a SQL string, or any use of
   `String.format` to build SQL, is a review blocker. It is a mechanical check and it catches this
   class of bug completely, which is rare enough to be worth having.
3. **Identifiers still need an allowlist.** If the endpoint ever grows `?sort=email`, remember that
   `?` cannot hold a column name — map it through a fixed `Map<String, String>` of SQL you wrote.
4. **Return an empty list, not an error, for "not found".** The transcript shows `[]` for both the
   missing user and the hostile input, which is also a small privacy property: an endpoint that
   distinguishes them tells an attacker which addresses exist.

:::

## Key takeaways

- JDBC is a service-provider interface: `java.sql` is interfaces, and the driver is a jar you add — the JDK ships none.
- `DriverManager.getConnection` throws `SQLException: No suitable driver found` when no driver matches the URL.
- A `ResultSet` is a cursor positioned before the first row, so `while (next())` is the only correct reading loop.
- Column numbers in JDBC start at 1, not 0.
- An update returns the number of rows affected, which is the only check that your `WHERE` matched what you meant.
- A `?` placeholder is parsed before the value arrives, so the value can never become syntax — that is what prevents SQL injection.
- `?` cannot hold a table or column name; varying identifiers needs an allowlist of SQL you wrote.
- `SQLException` is checked, and JDBC is the strongest argument Java has for checked exceptions being right.
- `getInt` returns 0 for a SQL `null`, so a nullable numeric column needs `wasNull()`.
- A `Connection` is not thread-safe and is a remote resource: never one field, always a pool, always try-with-resources.

## Practice

- [ ] Create a table, insert five rows, and read them back with `while (next())`, printing the row count first.
- [ ] Delete one row by id with a placeholder and confirm the remaining count with `SELECT COUNT(*)`.
- [ ] Call a method on a closed connection, and create a table twice, and print both `SQLException` messages.
- [ ] Sum an integer column across three rows by iterating the cursor, and print both the total and the number of rows seen.

## Solutions

:::solution Exercise 1
@@sol1@@

`size()` is a convenience this engine has and JDBC does not — a real `ResultSet` cannot tell you how
many rows are coming, because it streams them. The loop is therefore the only way to count, and the
count is only known at the end.

:::

:::solution Exercise 2
@@sol2@@

`DELETE` returned 1, which is the number of rows the `WHERE` matched. A `DELETE` with no `WHERE`
matches every row, and the count is what tells you that you have just emptied the table instead of
removing one entry — which is why the count is worth checking rather than discarding.

:::

:::solution Exercise 3
@@sol3@@

Two environment errors, one checked type. The messages differ, the `SQLState` and vendor code differ,
and a production log needs all three: the class name alone tells you that a database call failed and
nothing about which one or why.

:::

:::solution Exercise 4
@@sol4@@

Three rows, twelve stars. The cursor starts before the first row and ends after the last, so a
`while (next())` loop visits each row exactly once — and the accumulator only works because
`getInt` returned a number for every row, which is why checking `wasNull()` matters when the column is
nullable.

:::
"""

gen.write(TEMPLATE, BLOCKS)
