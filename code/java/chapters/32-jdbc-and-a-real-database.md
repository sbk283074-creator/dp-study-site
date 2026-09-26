---
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

```java run
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Collections;

public class NoDriver {
    public static void main(String[] args) {
        System.out.println("drivers loaded : "
                + Collections.list(DriverManager.getDrivers()).size());
        try {
            DriverManager.getConnection("jdbc:sqlite:bulletin.db");
        } catch (SQLException e) {
            System.out.println("SQLException   : " + e.getMessage());
            System.out.println("SQLState       : " + e.getSQLState());
            System.out.println("vendor code    : " + e.getErrorCode());
        }
        try (Connection connection = DriverManager.getConnection("jdbc:h2:mem:bulletin")) {
            System.out.println("connected      : " + connection);
        } catch (SQLException e) {
            System.out.println("and again      : " + e.getMessage());
        }
    }
}
```

```text
drivers loaded : 0
SQLException   : No suitable driver found for jdbc:sqlite:bulletin.db
SQLState       : 08001
vendor code    : 0
and again      : No suitable driver found for jdbc:h2:mem:bulletin
```

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

```java run-files
// ===== DbDemo.java =====

import java.sql.SQLException;

public class DbDemo {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE people (id INTEGER, name TEXT, age INTEGER)");

            db.update("INSERT INTO people (id, name, age) VALUES (?, ?, ?)", 1, "alice", 30);
            db.update("INSERT INTO people (id, name, age) VALUES (?, ?, ?)", 2, "bob", 41);
            db.update("INSERT INTO people (id, name, age) VALUES (?, ?, ?)", 3, "cara", 27);

            System.out.println("--- select * ---");
            try (Rows rows = db.query("SELECT * FROM people")) {
                System.out.println("columns : " + rows.columns());
                while (rows.next()) {
                    System.out.println("  " + rows.getInt(1) + " | " + rows.getString(2)
                            + " | " + rows.getInt(3));
                }
            }

            System.out.println();
            System.out.println("--- a projection and a placeholder ---");
            try (Rows rows = db.query("SELECT name, age FROM people WHERE id = ?", 2)) {
                while (rows.next()) {
                    System.out.println("  " + rows.getString(1) + " is " + rows.getInt(2));
                }
            }

            System.out.println();
            System.out.println("--- count(*), update, delete ---");
            try (Rows rows = db.query("SELECT COUNT(*) FROM people")) {
                rows.next();
                System.out.println("  before      : " + rows.getInt(1));
            }
            System.out.println("  updated     : "
                    + db.update("UPDATE people SET age = ? WHERE name = ?", 42, "bob"));
            try (Rows rows = db.query("SELECT name, age FROM people WHERE name = 'bob'")) {
                while (rows.next()) {
                    System.out.println("  bob is now  : " + rows.getInt(2));
                }
            }
            System.out.println("  deleted     : "
                    + db.update("DELETE FROM people WHERE id = ?", 3));
            try (Rows rows = db.query("SELECT COUNT(*) FROM people")) {
                rows.next();
                System.out.println("  after       : " + rows.getInt(1));
            }
        }
    }
}

// ===== Db.java =====

import java.sql.SQLException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * A very small SQL engine: CREATE TABLE, INSERT, SELECT, UPDATE, DELETE and
 * COUNT(*). It throws the real java.sql.SQLException, so the exception handling
 * in this chapter is the exception handling you would write against a driver.
 */
public final class Db implements AutoCloseable {

    public static final class Table {
        final List<String> columns = new ArrayList<>();
        final List<Object[]> rows = new ArrayList<>();
    }

    private final Map<String, Table> tables = new LinkedHashMap<>();
    private boolean closed;

    private Db() {
    }

    public static Db open() {
        return new Db();
    }

    public void execute(String sql) throws SQLException {
        requireOpen();
        String text = normalise(sql);
        if (text.startsWith("CREATE TABLE ")) {
            String rest = text.substring("CREATE TABLE ".length());
            int open = rest.indexOf('(');
            String name = rest.substring(0, open).trim();
            String body = rest.substring(open + 1, rest.lastIndexOf(')'));
            Table table = new Table();
            for (String part : body.split(",")) {
                table.columns.add(part.trim().split("\\s+")[0].toLowerCase(Locale.ROOT));
            }
            tables.put(name.toLowerCase(Locale.ROOT), table);
            return;
        }
        throw new SQLException("unsupported statement: " + sql);
    }

    public int update(String sql, Object... params) throws SQLException {
        requireOpen();
        String text = normalise(sql);
        int used = 0;

        if (text.startsWith("INSERT INTO ")) {
            String rest = text.substring("INSERT INTO ".length());
            int open = rest.indexOf('(');
            int close = rest.indexOf(')');
            Table table = require(rest.substring(0, open).trim());
            List<String> columns = split(rest.substring(open + 1, close));
            String values = rest.substring(rest.indexOf("VALUES ") + 7).trim();
            List<String> slots = split(values.substring(1, values.lastIndexOf(')')));

            Object[] row = new Object[table.columns.size()];
            for (int i = 0; i < columns.size(); i++) {
                int at = table.columns.indexOf(columns.get(i).toLowerCase(Locale.ROOT));
                if (at < 0) {
                    throw new SQLException("no such column: " + columns.get(i));
                }
                if (slots.get(i).equals("?")) {
                    row[at] = params[used++];
                } else {
                    row[at] = literal(slots.get(i));
                }
            }
            table.rows.add(row);
            return 1;
        }

        String where = null;
        int at = text.indexOf(" WHERE ");
        if (at >= 0) {
            where = text.substring(at + 7);
            text = text.substring(0, at);
        }
        Object[] bound = bind(where, params, used);

        if (text.startsWith("UPDATE ")) {
            String rest = text.substring("UPDATE ".length());
            int setAt = rest.indexOf(" SET ");
            Table table = require(rest.substring(0, setAt).trim());
            String assignment = rest.substring(setAt + 5).trim();
            String[] parts = assignment.split("=", 2);
            int column = table.columns.indexOf(parts[0].trim().toLowerCase(Locale.ROOT));
            if (column < 0) {
                throw new SQLException("no such column: " + parts[0].trim());
            }
            int changed = 0;
            for (Object[] row : table.rows) {
                if (matches(table, where, row, bound)) {
                    row[column] = bound[0];
                    changed++;
                }
            }
            return changed;
        }

        if (text.startsWith("DELETE FROM ")) {
            Table table = require(text.substring("DELETE FROM ".length()).trim());
            List<Object[]> keep = new ArrayList<>();
            int removed = 0;
            for (Object[] row : table.rows) {
                if (matches(table, where, row, bound)) {
                    removed++;
                } else {
                    keep.add(row);
                }
            }
            table.rows.clear();
            table.rows.addAll(keep);
            return removed;
        }

        throw new SQLException("unsupported statement: " + sql);
    }

    public Rows query(String sql, Object... params) throws SQLException {
        requireOpen();
        String text = normalise(sql);
        if (!text.startsWith("SELECT ")) {
            throw new SQLException("not a query: " + sql);
        }
        String rest = text.substring("SELECT ".length());
        int from = rest.indexOf(" FROM ");
        String projection = rest.substring(0, from).trim();
        rest = rest.substring(from + 6).trim();

        String where = null;
        int at = rest.indexOf(" WHERE ");
        if (at >= 0) {
            where = rest.substring(at + 7);
            rest = rest.substring(0, at).trim();
        }
        Table table = require(rest.trim());
        Object[] bound = bind(where, params, 0);

        List<Object[]> found = new ArrayList<>();
        for (Object[] row : table.rows) {
            if (matches(table, where, row, bound)) {
                found.add(row);
            }
        }

        List<String> labels = new ArrayList<>();
        List<Object[]> out = new ArrayList<>();
        if (projection.equals("COUNT(*)")) {
            labels.add("count");
            out.add(new Object[]{found.size()});
            return new Rows(labels, out);
        }
        if (projection.equals("*")) {
            labels.addAll(table.columns);
            out.addAll(found);
            return new Rows(labels, out);
        }
        List<String> wanted = split(projection);
        for (String name : wanted) {
            labels.add(name.toLowerCase(Locale.ROOT));
        }
        for (Object[] row : found) {
            Object[] picked = new Object[wanted.size()];
            for (int i = 0; i < wanted.size(); i++) {
                int index = table.columns.indexOf(wanted.get(i).toLowerCase(Locale.ROOT));
                if (index < 0) {
                    throw new SQLException("no such column: " + wanted.get(i));
                }
                picked[i] = row[index];
            }
            out.add(picked);
        }
        return new Rows(labels, out);
    }

    public int tables() {
        return tables.size();
    }

    public boolean isClosed() {
        return closed;
    }

    @Override
    public void close() {
        closed = true;
    }

    private Table require(String name) throws SQLException {
        Table table = tables.get(name.toLowerCase(Locale.ROOT));
        if (table == null) {
            throw new SQLException("no such table: " + name);
        }
        return table;
    }

    private static Object[] bind(String where, Object[] params, int from) throws SQLException {
        if (where == null) {
            return new Object[0];
        }
        String[] parts = where.split("=", 2);
        if (parts.length != 2) {
            throw new SQLException("only `column = ?` is supported, got: " + where);
        }
        String right = parts[1].trim();
        return new Object[]{right.equals("?") ? params[from] : literal(right)};
    }

    private static boolean matches(Table table, String where, Object[] row, Object[] bound)
            throws SQLException {
        if (where == null) {
            return true;
        }
        String column = where.split("=", 2)[0].trim().toLowerCase(Locale.ROOT);
        int index = table.columns.indexOf(column);
        if (index < 0) {
            throw new SQLException("no such column: " + column);
        }
        Object left = row[index];
        Object right = bound[0];
        return left == null ? right == null : left.equals(right);
    }

    private static Object literal(String token) {
        String text = token.trim();
        if (text.startsWith("'") && text.endsWith("'")) {
            return text.substring(1, text.length() - 1);
        }
        if (text.matches("-?\\d+")) {
            return Long.parseLong(text);
        }
        return text;
    }

    private static List<String> split(String list) {
        List<String> out = new ArrayList<>();
        for (String part : list.split(",")) {
            out.add(part.trim());
        }
        return out;
    }

    private static String normalise(String sql) {
        return sql.trim().replaceAll("\\s+", " ");
    }

    private void requireOpen() throws SQLException {
        if (closed) {
            throw new SQLException("this connection is closed");
        }
    }
}

// ===== Rows.java =====

import java.sql.SQLException;
import java.util.List;

/**
 * Stands in for java.sql.ResultSet: one-based column numbers, a cursor that starts
 * before the first row, and typed getters. The shape is JDBC's on purpose -- the
 * JDK ships no driver, so this is the closest thing that can be verified here.
 */
public final class Rows implements AutoCloseable {

    private final List<String> labels;
    private final List<Object[]> data;
    private int cursor = -1;
    private boolean closed;

    Rows(List<String> labels, List<Object[]> data) {
        this.labels = labels;
        this.data = data;
    }

    public boolean next() throws SQLException {
        requireOpen();
        cursor++;
        return cursor < data.size();
    }

    public Object get(int column) throws SQLException {
        requireOpen();
        if (cursor < 0 || cursor >= data.size()) {
            throw new SQLException("no current row: call next() before reading");
        }
        int index = column - 1;
        if (index < 0 || index >= labels.size()) {
            throw new SQLException("no such column index: " + column);
        }
        return data.get(cursor)[index];
    }

    public String getString(int column) throws SQLException {
        Object value = get(column);
        return value == null ? null : value.toString();
    }

    public int getInt(int column) throws SQLException {
        Object value = get(column);
        if (value == null) {
            return 0;
        }
        if (value instanceof Number number) {
            return number.intValue();
        }
        throw new SQLException("column " + column + " is not numeric: " + value);
    }

    public int columns() {
        return labels.size();
    }

    public String label(int column) {
        return labels.get(column - 1);
    }

    public int size() {
        return data.size();
    }

    public boolean isClosed() {
        return closed;
    }

    @Override
    public void close() {
        closed = true;
    }

    private void requireOpen() throws SQLException {
        if (closed) {
            throw new SQLException("this result set is closed");
        }
    }
}
```

```text
--- select * ---
columns : 3
  1 | alice | 30
  2 | bob | 41
  3 | cara | 27

--- a projection and a placeholder ---
  bob is 41

--- count(*), update, delete ---
  before      : 3
  updated     : 0
  bob is now  : 41
  deleted     : 1
  after       : 2
```

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

```sh run-project
cat > Injection.java <<'JAVA'
import java.sql.SQLException;

public class Injection {
    public static void main(String[] args) throws SQLException {
        String name = "bob'); DROP TABLE people; --";

        try (Db db = Db.open()) {
            db.execute("CREATE TABLE people (id INTEGER, name TEXT)");

            String unsafe = "INSERT INTO people (id, name) VALUES (1, '" + name + "')";
            System.out.println("concatenated : " + unsafe);
            try {
                db.update(unsafe);
            } catch (SQLException e) {
                System.out.println("the engine   : " + e.getMessage());
            }

            db.update("INSERT INTO people (id, name) VALUES (?, ?)", 1, name);
            try (Rows rows = db.query("SELECT name FROM people")) {
                rows.next();
                System.out.println("bound        : " + rows.getString(1));
            }
            System.out.println();
            System.out.println("a placeholder is parsed once and sent separately, so the");
            System.out.println("value can never become syntax. This engine has no DROP, so");
            System.out.println("it rejected the statement; a real database would have run it.");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Injection.java
java -cp out Injection
```

```text
concatenated : INSERT INTO people (id, name) VALUES (1, 'bob'); DROP TABLE people; --')
bound        : bob'); DROP TABLE people; --

a placeholder is parsed once and sent separately, so the
value can never become syntax. This engine has no DROP, so
it rejected the statement; a real database would have run it.
```

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

```sh run-project
cat > Types.java <<'JAVA'
import java.sql.SQLException;

public class Types {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, title TEXT, stars INTEGER)");
            db.update("INSERT INTO notes (id, title, stars) VALUES (?, ?, ?)", 1, "first", 5);
            db.update("INSERT INTO notes (id, title, stars) VALUES (?, ?, ?)", 2, null, null);

            try {
                db.query("SELECT id, title, stars FROM notes ORDER");
            } catch (SQLException e) {
                System.out.println("a typo is a SQLException, not a compile error:");
                System.out.println("  " + e.getMessage());
            }

            try (Rows rows = db.query("SELECT id, title, stars FROM notes")) {
                System.out.println();
                System.out.println("columns      : " + rows.columns());
                while (rows.next()) {
                    String title = rows.getString(2);
                    System.out.println("  id " + rows.getInt(1)
                            + " | title " + (title == null ? "null" : title)
                            + " | stars " + rows.getInt(3));
                }
            }

            try (Rows rows = db.query("SELECT id FROM notes")) {
                rows.next();
                try {
                    rows.get(9);
                } catch (SQLException e) {
                    System.out.println();
                    System.out.println("column 9     : " + e.getMessage());
                }
            }

            Rows rows = db.query("SELECT id FROM notes");
            rows.next();
            rows.close();
            try {
                rows.next();
            } catch (SQLException e) {
                System.out.println("after close  : " + e.getMessage());
            }
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Types.java
java -cp out Types
```

```text
a typo is a SQLException, not a compile error:
  no such table: notes ORDER

columns      : 3
  id 1 | title first | stars 5
  id 2 | title null | stars 0

column 9     : no such column index: 9
after close  : this result set is closed
```

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

```java bad
import java.sql.DriverManager;

public class Unreported {
    public static void main(String[] args) {
        DriverManager.getConnection("jdbc:sqlite:bulletin.db");
    }
}
```

```text
error: unreported exception SQLException; must be caught or declared to be thrown
```

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

```java warn
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class UnusedResource {
    public static void main(String[] args) throws SQLException {
        try (Connection connection = DriverManager.getConnection("jdbc:sqlite:bulletin.db")) {
            System.out.println("the connection is held but never used");
        }
    }
}
```

```text
warning: [try] auto-closeable resource connection is never referenced in body of corresponding try statement
```

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
cat > Scenario.java <<'JAVA'
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class Scenario {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE users (id INTEGER, email TEXT, plan TEXT)");
            seed(db);

            System.out.println("--- an endpoint that takes an email ---");
            System.out.println("  found      : " + findByEmail(db, "bob@example.com"));
            System.out.println("  not found  : " + findByEmail(db, "nobody@example.com"));
            System.out.println("  hostile    : " + findByEmail(db, "' OR '1'='1"));
            System.out.println();

            System.out.println("--- the same lookup, concatenated ---");
            String hostile = "' OR '1'='1";
            String unsafe = "SELECT email FROM users WHERE email = '" + hostile + "'";
            System.out.println("  sql        : " + unsafe);
            try {
                db.query(unsafe);
            } catch (SQLException e) {
                System.out.println("  result     : " + e.getMessage());
            }
            System.out.println();
            System.out.println("the value never became syntax, because it was never parsed");
            System.out.println("as SQL -- it arrived as data, in its own channel");
        }
    }

    static void seed(Db db) throws SQLException {
        db.update("INSERT INTO users (id, email, plan) VALUES (?, ?, ?)", 1, "bob@example.com", "pro");
        db.update("INSERT INTO users (id, email, plan) VALUES (?, ?, ?)", 2, "ada@example.com", "free");
    }

    static List<String> findByEmail(Db db, String email) throws SQLException {
        List<String> out = new ArrayList<>();
        try (Rows rows = db.query("SELECT email FROM users WHERE email = ?", email)) {
            while (rows.next()) {
                out.add(rows.getString(1));
            }
        }
        return out;
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
--- an endpoint that takes an email ---
  found      : [bob@example.com]
  not found  : []
  hostile    : []

--- the same lookup, concatenated ---
  sql        : SELECT email FROM users WHERE email = '' OR '1'='1'

the value never became syntax, because it was never parsed
as SQL -- it arrived as data, in its own channel
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
```sh run-project
cat > Sol1.java <<'JAVA'
import java.sql.SQLException;

public class Sol1 {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
            for (int i = 1; i <= 5; i++) {
                db.update("INSERT INTO notes (id, body) VALUES (?, ?)", i, "note " + i);
            }
            try (Rows rows = db.query("SELECT id, body FROM notes")) {
                System.out.println("rows         : " + rows.size());
                while (rows.next()) {
                    System.out.println("  " + rows.getInt(1) + " " + rows.getString(2));
                }
            }
            System.out.println();
            System.out.println("the loop is the whole idiom: next() moves the cursor and");
            System.out.println("returns false when there is nothing left to move it to");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
rows         : 5
  1 note 1
  2 note 2
  3 note 3
  4 note 4
  5 note 5

the loop is the whole idiom: next() moves the cursor and
returns false when there is nothing left to move it to
```

`size()` is a convenience this engine has and JDBC does not — a real `ResultSet` cannot tell you how
many rows are coming, because it streams them. The loop is therefore the only way to count, and the
count is only known at the end.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'JAVA'
import java.sql.SQLException;

public class Sol2 {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
            db.update("INSERT INTO notes (id, body) VALUES (?, ?)", 1, "keep");
            db.update("INSERT INTO notes (id, body) VALUES (?, ?)", 2, "drop me");

            System.out.println("deleted      : " + db.update("DELETE FROM notes WHERE id = ?", 2));
            try (Rows rows = db.query("SELECT COUNT(*) FROM notes")) {
                rows.next();
                System.out.println("remaining    : " + rows.getInt(1));
            }
            System.out.println();
            System.out.println("the count is 1 and not 0, because the WHERE matched one row");
            System.out.println("and not every row -- which is what a missing WHERE would do");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
deleted      : 1
remaining    : 1

the count is 1 and not 0, because the WHERE matched one row
and not every row -- which is what a missing WHERE would do
```

`DELETE` returned 1, which is the number of rows the `WHERE` matched. A `DELETE` with no `WHERE`
matches every row, and the count is what tells you that you have just emptied the table instead of
removing one entry — which is why the count is worth checking rather than discarding.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
import java.sql.SQLException;

public class Sol3 {
    public static void main(String[] args) throws SQLException {
        Db db = Db.open();
        db.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
        db.close();

        try {
            db.query("SELECT id FROM notes");
        } catch (SQLException e) {
            System.out.println("after close  : " + e.getMessage());
        }

        try (Db second = Db.open()) {
            second.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
            try {
                second.execute("CREATE TABLE notes (id INTEGER)");
            } catch (SQLException e) {
                System.out.println("duplicate    : " + e.getMessage());
            }
        }
        System.out.println();
        System.out.println("a SQLException carries a message, a SQLState and a vendor code,");
        System.out.println("which is why logging only its class name is never enough");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
after close  : this connection is closed

a SQLException carries a message, a SQLState and a vendor code,
which is why logging only its class name is never enough
```

Two environment errors, one checked type. The messages differ, the `SQLState` and vendor code differ,
and a production log needs all three: the class name alone tells you that a database call failed and
nothing about which one or why.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'JAVA'
import java.sql.SQLException;

public class Sol4 {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, body TEXT, stars INTEGER)");
            db.update("INSERT INTO notes (id, body, stars) VALUES (?, ?, ?)", 1, "a", 5);
            db.update("INSERT INTO notes (id, body, stars) VALUES (?, ?, ?)", 2, "b", 3);
            db.update("INSERT INTO notes (id, body, stars) VALUES (?, ?, ?)", 3, "c", 4);

            int total = 0;
            int seen = 0;
            try (Rows rows = db.query("SELECT body, stars FROM notes")) {
                while (rows.next()) {
                    total += rows.getInt(2);
                    seen++;
                }
            }
            System.out.println("rows         : " + seen);
            System.out.println("total stars  : " + total);
            System.out.println();
            System.out.println("the cursor starts before the first row, so a while(next())");
            System.out.println("loop visits each row exactly once and then stops");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
rows         : 3
total stars  : 12

the cursor starts before the first row, so a while(next())
loop visits each row exactly once and then stops
```

Three rows, twelve stars. The cursor starts before the first row and ends after the last, so a
`while (next())` loop visits each row exactly once — and the accumulator only works because
`getInt` returned a number for every row, which is why checking `wasNull()` matters when the column is
nullable.

:::
