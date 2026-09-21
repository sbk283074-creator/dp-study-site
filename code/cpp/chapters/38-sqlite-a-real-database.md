---
chapter: 38
part: 5
title: SQLite — a Real Database
summary: Store, query and update structured data in a single file, using prepared statements that cannot be injected into and transactions that cannot half-apply.
minutes: 70
tags: [sqlite, sql, prepared-statements, transactions, raii, injection]
libs: sqlite3
---

Chapter 37 gave the service a memory that survived a restart: an append-only log with a
length prefix and a checksum. It works, and it is honest about what it is. It is also the
wrong shape for the first question you cannot answer cheaply.

Ask that log *which requests came from this user*, or *how many failed yesterday*, and there
is no way to answer without reading every byte. Ask it to *change* one record and there is no
way at all, short of rewriting everything after it. A flat file is a perfectly good journal;
it is a terrible index.

SQLite is the fix that does not require a server. It is a library, not a process: you call
functions, it reads and writes one file, and that file is a real relational database with
indexes, a query planner, transactions and crash recovery. It is the most widely deployed SQL
engine in the world — in every phone, every browser, most aircraft — and the whole engine is a
single C file you could compile into your program. This chapter is about driving it from C++
without leaking a handle, trusting a string, or writing a transaction that half-applies.

## Opening a database

Every SQLite program starts the same way: ask for a connection to a file, and check the code
that comes back.

```cpp run
#include <sqlite3.h>

#include <cstdio>

int main() {
    std::printf("SQLite %s\n", sqlite3_libversion());
    std::printf("version number %d\n", sqlite3_libversion_number());

    sqlite3 *db = nullptr;
    const int rc = sqlite3_open(":memory:", &db);
    std::printf("open(:memory:) rc=%d\n", rc);
    // An in-memory database has no filename; that empty string is the tell.
    std::printf("filename of main db = [%s]\n", sqlite3_db_filename(db, "main"));

    sqlite3_close(db);
    return 0;
}
```

```text
SQLite 3.51.0
version number 3051000
open(:memory:) rc=0
filename of main db = []
```

Three things in that output are worth pausing on. `sqlite3_libversion()` is the string the
library reports about itself and `sqlite3_libversion_number()` is the same thing as an integer
you can compare against — `3051000` is 3.51.0, major × 1 000 000 + minor × 1 000 + patch. **Both
are measured on this machine**; the SQLite in your SDK or your package manager will be a
different version, and the number is how you find out which one you are actually talking to
rather than which one you assume you are.

The third line is the one people skip. `sqlite3_open` returned `0`, which is `SQLITE_OK`, but
that is not the point: the point is that **it can fail and still hand you a handle**. A corrupt
or locked file returns an error code *and* fills in `handle`, and that handle is the only place
the real message lives. Any wrapper that throws on a non-zero code without reading
`sqlite3_errmsg` first has thrown away the explanation.

The last line shows the trick used throughout this chapter: `":memory:"` is a database that
lives in RAM and is destroyed when the connection closes. Its filename is the empty string,
which is how you can tell a real file from a scratch one.

:::note Where the library comes from
The header and the link flag are not portable facts. On macOS both live in the SDK —
`<sqlite3.h>` needs no `-I` and `-lsqlite3` just works, which is what this chapter's
`libs: sqlite3` front matter expands to. On Debian and Ubuntu it is
`apt install libsqlite3-dev`; on Fedora, `dnf install sqlite-devel`. Or you drop
`sqlite3.c` and `sqlite3.h` — the famous amalgamation, one 250 000-line C file — into your
tree and compile it with everything else, which is what most embedded products do.
:::

## Two ways in: `exec` and `prepare`

SQLite has one convenience API and one real API. You need to know both, and you need to know
exactly when the first one stops being safe.

### `sqlite3_exec`: a string in, a callback out

```cpp run
#include <sqlite3.h>

#include <cstdio>

// sqlite3_exec is the "do exactly what I typed" entry point. The callback runs
// once per result row; the fourth argument is the column name array.
static int print_row(void *unused, int columns, char **values, char **names) {
    (void)unused;
    for (int i = 0; i < columns; ++i) {
        std::printf("  %s = %s\n", names[i], values[i] ? values[i] : "NULL");
    }
    return 0;
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    char *err = nullptr;
    int rc = sqlite3_exec(db,
                          "CREATE TABLE users ("
                          "  id   INTEGER PRIMARY KEY,"
                          "  name TEXT NOT NULL,"
                          "  age  INTEGER);"
                          "INSERT INTO users (name, age) VALUES"
                          "  ('ada', 36), ('grace', 45), ('alan', 41);",
                          nullptr, nullptr, &err);
    std::printf("setup rc=%d\n", rc);
    if (rc != SQLITE_OK) {
        std::printf("setup failed: %s\n", err);
        sqlite3_free(err);
    }

    rc = sqlite3_exec(db, "SELECT name, age FROM users WHERE age > 40 ORDER BY name;",
                      print_row, nullptr, &err);
    std::printf("select rc=%d\n", rc);

    sqlite3_close(db);
    return 0;
}
```

```text
setup rc=0
  name = alan
  age = 41
  name = grace
  age = 45
select rc=0
```

`sqlite3_exec` takes a whole SQL string and runs it. It accepts several statements separated by
semicolons, which is why the setup above can `CREATE` and `INSERT` in one call. The callback
runs once per result row with two parallel arrays: the values as strings, and the column names.
A `NULL` arrives as a null pointer, so `values[i] ? values[i] : "NULL"` is not defensive
padding — it is the difference between printing `NULL` and dereferencing nothing.

Returning non-zero from the callback aborts the query. That is the documented way to stop
early.

### Why you stop using `exec` the moment input arrives

Here is the same program, asked to store one note typed by a user.

```cpp run
#include <sqlite3.h>

#include <cstdio>
#include <string>

static void exec(sqlite3 *db, const std::string &sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("  error: %s\n", err);
        sqlite3_free(err);
    }
}

static int print_text(void *unused, int columns, char **values, char **names) {
    (void)unused;
    (void)names;
    for (int i = 0; i < columns; ++i) std::printf("  row: %s\n", values[i] ? values[i] : "NULL");
    return 0;
}

static void count(sqlite3 *db, const char *label) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, "SELECT text FROM secrets;", print_text, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("%s: %s\n", label, err);
        sqlite3_free(err);
    }
}

int main() {
    // What a hostile user types into the "note" field of a web form.
    const std::string input = "x'); DROP TABLE secrets; --";

    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    // ---- 1. the naive way: build SQL by pasting strings together -------------
    exec(db, "CREATE TABLE secrets (text TEXT); INSERT INTO secrets VALUES ('alpha');");
    const std::string naive = "INSERT INTO secrets VALUES ('" + input + "');";
    std::printf("naive SQL: %s\n", naive.c_str());
    exec(db, naive);
    count(db, "after naive");

    // ---- 2. the same input, bound as a value --------------------------------
    exec(db, "CREATE TABLE secrets (text TEXT); INSERT INTO secrets VALUES ('alpha');");
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO secrets VALUES (?);", -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, input.c_str(), -1, SQLITE_TRANSIENT);
    const int rc = sqlite3_step(stmt);
    std::printf("bound step rc=%d\n", rc);
    sqlite3_finalize(stmt);
    count(db, "after bound");

    sqlite3_close(db);
    return 0;
}
```

```text
naive SQL: INSERT INTO secrets VALUES ('x'); DROP TABLE secrets; --');
after naive: no such table: secrets
bound step rc=101
  row: alpha
  row: x'); DROP TABLE secrets; --
```

Read the first line of output as SQL, not as a string. The user's text contained a closing
quote, a semicolon, and a `DROP TABLE`. Paste it into the literal and the engine sees three
statements: insert a row, **drop the table**, and a `--` comment that swallows the rest of your
own syntax. The table is gone. The second half of the output is the same input bound as a
value: the row is stored verbatim, quotes and all, and the table is untouched.

That is the whole lesson, and it is not about SQLite. **Building a query by pasting strings
together means the data is code.** The value is not being stored; it is being parsed. The
second version cannot be attacked, because a bound parameter is handed to the engine *after*
parsing has finished — there is no syntax left for it to inject into.

:::danger This is not a hypothetical
SQL injection has been in the OWASP top three for two decades and it still works, because the
vulnerable shape is the obvious one. If you find yourself writing `"... '" + value + "' ..."`
in any language, stop. Every database API worth using has a placeholder.
:::

### Prepared statements: compile once, bind, step

The real API is four calls: prepare, bind, step, finalize.

```cpp run
#include <sqlite3.h>

#include <cstdio>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);",
                 nullptr, nullptr, &err);

    // ---- write: bind, step once, expect DONE --------------------------------
    sqlite3_stmt *insert = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO users (name, age) VALUES (?, ?);", -1, &insert, nullptr);
    std::printf("parameter count = %d\n", sqlite3_bind_parameter_count(insert));

    sqlite3_bind_text(insert, 1, "ada", -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(insert, 2, 36);
    int rc = sqlite3_step(insert);
    std::printf("insert step rc=%d (SQLITE_DONE=%d)\n", rc, SQLITE_DONE);
    std::printf("last_insert_rowid=%lld\n", (long long)sqlite3_last_insert_rowid(db));
    std::printf("changes=%d\n", sqlite3_changes(db));

    // A prepared statement is reusable: reset, rebind, step again.
    sqlite3_reset(insert);
    sqlite3_bind_text(insert, 1, "grace", -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(insert, 2, 45);
    rc = sqlite3_step(insert);
    std::printf("second insert rc=%d, rowid=%lld\n", rc,
                (long long)sqlite3_last_insert_rowid(db));
    sqlite3_finalize(insert);

    // ---- read: step until it stops returning rows ---------------------------
    sqlite3_stmt *select = nullptr;
    sqlite3_prepare_v2(db, "SELECT id, name, age FROM users ORDER BY id;", -1, &select, nullptr);
    std::printf("column count = %d\n", sqlite3_column_count(select));
    int rows = 0;
    while ((rc = sqlite3_step(select)) == SQLITE_ROW) {
        ++rows;
        std::printf("  %d: %s (%d)\n", sqlite3_column_int(select, 0),
                    sqlite3_column_text(select, 1), sqlite3_column_int(select, 2));
    }
    std::printf("rows=%d, final rc=%d (SQLITE_ROW=%d SQLITE_DONE=%d)\n", rows, rc,
                SQLITE_ROW, SQLITE_DONE);
    sqlite3_finalize(select);

    sqlite3_close(db);
    return 0;
}
```

```text
parameter count = 2
insert step rc=101 (SQLITE_DONE=101)
last_insert_rowid=1
changes=1
second insert rc=101, rowid=2
column count = 3
  1: ada (36)
  2: grace (45)
rows=2, final rc=101 (SQLITE_ROW=100 SQLITE_DONE=101)
```

The lifecycle matters more than the syntax:

1. **`sqlite3_prepare_v2`** compiles the SQL into a statement. Nothing has run yet. The `v2`
   is not a version number you can skip — the original `sqlite3_prepare` is retained only for
   backwards compatibility and behaves worse on schema changes.
2. **`sqlite3_bind_*`** supplies a value for each `?`. Indexing starts at **1**, and there is
   no zero.
3. **`sqlite3_step`** advances. It returns `SQLITE_ROW` (100) while there is another row and
   `SQLITE_DONE` (101) when the statement has finished. A write statement returns `DONE`
   immediately.
4. **`sqlite3_finalize`** releases the statement. Skip it and you leak — and on a connection
   that is about to be closed, `sqlite3_close` will return `SQLITE_BUSY` and refuse.

The two numbers in that output that a service actually uses are `last_insert_rowid` — the
`id` the engine assigned, which you need in order to insert a child row — and `changes`, the
number of rows the last statement touched. Note that `sqlite3_reset` lets you re-run the same
compiled statement with new values: the second insert reuses everything, and the rowid moves
to 2.

## Parameters: named, and the copy rule

Positional `?` gets anonymous fast. SQLite also supports `:name`, `@name` and `$name`.

```cpp run
#include <sqlite3.h>

#include <cstdio>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);",
                 nullptr, nullptr, &err);

    // Positional `?` is anonymous; `:name`, `@name` and `$name` are named.
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO users (name, age) VALUES (:who, :years);", -1, &stmt,
                       nullptr);
    std::printf("parameter count = %d\n", sqlite3_bind_parameter_count(stmt));
    std::printf("index of :who   = %d\n", sqlite3_bind_parameter_index(stmt, ":who"));
    std::printf("index of :years = %d\n", sqlite3_bind_parameter_index(stmt, ":years"));
    std::printf("index of :nope  = %d\n", sqlite3_bind_parameter_index(stmt, ":nope"));
    std::printf("name of 1       = %s\n", sqlite3_bind_parameter_name(stmt, 1));

    sqlite3_bind_text(stmt, sqlite3_bind_parameter_index(stmt, ":who"), "ada", -1,
                      SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, sqlite3_bind_parameter_index(stmt, ":years"), 36);
    std::printf("step rc=%d\n", sqlite3_step(stmt));
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    return 0;
}
```

```text
parameter count = 2
index of :who   = 1
index of :years = 2
index of :nope  = 0
name of 1       = :who
step rc=101
```

`sqlite3_bind_parameter_index` maps a name to its 1-based index and returns **0** for a name
that is not in the statement — not -1, not an error. Bind to index 0 and nothing happens; the
parameter stays `NULL` and the insert succeeds with a hole in it. If a name is generated from
a map of user input, check for 0.

### The fifth argument to `sqlite3_bind_text` is a promise about memory

```cpp bad
#include <sqlite3.h>

#include <string>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO notes VALUES (?);", -1, &stmt, nullptr);

    // sqlite3_bind_text wants a const char *, not a std::string. There is no
    // implicit conversion, so this is a hard compile error -- which is exactly
    // what you want, because the "working" version would be a dangling pointer.
    const std::string body = "hello";
    sqlite3_bind_text(stmt, 1, body, -1, SQLITE_TRANSIENT);

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 0;
}
```

```text
error: no matching function for call to 'sqlite3_bind_text'
```

That rejection is a gift. `sqlite3_bind_text` wants a `const char *`; a `std::string` does not
convert to one, so the compiler stops you before you get to the interesting part. The
"working" version is `body.c_str()`, and now the fifth argument decides whether the program is
correct:

- **`SQLITE_TRANSIENT`** — SQLite copies the bytes now. Always correct. Costs a copy.
- **`SQLITE_STATIC`** — SQLite keeps your pointer and reads it later. Free, and a trap.

```cpp run-san-catch
#include <sqlite3.h>

#include <cstdio>
#include <string>

// SQLITE_STATIC tells SQLite "this buffer outlives the statement, do not copy
// it". That is a promise about memory, and breaking it is use-after-free.
int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE notes (body TEXT);", nullptr, nullptr, &err);

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO notes VALUES (?);", -1, &stmt, nullptr);
    {
        std::string temporary = "a string long enough to live on the heap";
        sqlite3_bind_text(stmt, 1, temporary.c_str(), -1, SQLITE_STATIC);
    }  // `temporary` is destroyed here; SQLite still holds the pointer.

    const int rc = sqlite3_step(stmt);  // reads the dead buffer
    std::printf("step rc=%d\n", rc);
    sqlite3_finalize(stmt);

    sqlite3_stmt *check = nullptr;
    sqlite3_prepare_v2(db, "SELECT body FROM notes;", -1, &check, nullptr);
    if (sqlite3_step(check) == SQLITE_ROW) {
        std::printf("stored: %s\n", sqlite3_column_text(check, 0));
    }
    sqlite3_finalize(check);

    sqlite3_close(db);
    return 0;
}
```

```text
ERROR: AddressSanitizer: heap-use-after-free
```

The `std::string` died at the closing brace. SQLite still held the pointer, and `sqlite3_step`
read it — AddressSanitizer reports `heap-use-after-free` inside `sqlite3VdbeExec`, the
interpreter loop, which is where a bound value is finally consumed. The read does not happen
at bind time, which is exactly why this bug survives a casual test: with a short string the
bytes may still be sitting there untouched, and the row looks fine on your machine.

Use `SQLITE_TRANSIENT` unless you have a buffer whose lifetime you can prove in one sentence.
The one legitimate use of `SQLITE_STATIC` is a string literal or a `static` array, both of
which outlive everything.

## Error codes, and where the message lives

```cpp run
#include <sqlite3.h>

#include <cstdio>

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    sqlite3_stmt *stmt = nullptr;
    const int rc = sqlite3_prepare_v2(db, "SELECT * FROM nope;", -1, &stmt, nullptr);
    std::printf("prepare rc=%d (SQLITE_OK=%d, SQLITE_ERROR=%d)\n", rc, SQLITE_OK, SQLITE_ERROR);
    std::printf("sqlite3_errmsg: %s\n", sqlite3_errmsg(db));
    std::printf("extended code:  %d\n", sqlite3_extended_errcode(db));
    std::printf("handle is %s\n", stmt == nullptr ? "null" : "not null");

    // A constraint failure is reported the same way, with its own code.
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE t (n INTEGER CHECK (n > 0));", nullptr, nullptr, &err);
    const int bad = sqlite3_exec(db, "INSERT INTO t VALUES (-1);", nullptr, nullptr, &err);
    std::printf("\nconstraint rc=%d: %s\n", bad, err);
    std::printf("extended code:  %d\n", sqlite3_extended_errcode(db));
    sqlite3_free(err);

    sqlite3_close(db);
    return 0;
}
```

```text
prepare rc=1 (SQLITE_OK=0, SQLITE_ERROR=1)
sqlite3_errmsg: no such table: nope
extended code:  1
handle is null

constraint rc=19: CHECK constraint failed: n > 0
extended code:  275
```

Three facts, all worth memorising:

- Success is not the only non-error. `SQLITE_OK` is 0, `SQLITE_ROW` is 100 and `SQLITE_DONE`
  is 101. A wrapper that throws on "not OK" throws on every successful `SELECT`.
- A failed `prepare` leaves the statement **null** and the message on the *connection*, not on
  the statement — there is no statement to ask.
- `sqlite3_extended_errcode` splits the generic `SQLITE_CONSTRAINT` (19) into the specific
  `275`, which is `SQLITE_CONSTRAINT_CHECK`. `sqlite3_errstr` turns either back into text if
  you want to log it.

The message from `sqlite3_exec` is allocated with `sqlite3_malloc`, so it must be released
with `sqlite3_free` and not `delete` or `free`.

## Declared types are a preference, not a promise

Most SQL engines reject a value that does not match its column. SQLite does not, and this
surprises everyone.

```cpp run
#include <sqlite3.h>

#include <cstdio>

// SQLite columns have *affinity*, not a fixed type: the declared type is a
// preference applied when a value is stored, not a constraint enforced forever.
int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE t (n INTEGER, r REAL, b BLOB, s TEXT);"
                 "INSERT INTO t VALUES ('abc', '3.5', 42, 42);"
                 "INSERT INTO t VALUES ('42',  'x',   42, 42);",
                 nullptr, nullptr, &err);

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT typeof(n), n, typeof(r), r, typeof(b), b, typeof(s), s FROM t;",
                       -1, &stmt, nullptr);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("n: %-7s %-5s | r: %-7s %-5s | b: %-7s %-5s | s: %-7s %s\n",
                    sqlite3_column_text(stmt, 0), sqlite3_column_text(stmt, 1),
                    sqlite3_column_text(stmt, 2), sqlite3_column_text(stmt, 3),
                    sqlite3_column_text(stmt, 4), sqlite3_column_text(stmt, 5),
                    sqlite3_column_text(stmt, 6), sqlite3_column_text(stmt, 7));
    }
    sqlite3_finalize(stmt);

    // A BLOB column has no affinity at all, so nothing is ever converted.
    sqlite3_exec(db, "INSERT INTO t VALUES (1, 1, 'still text', 1);", nullptr, nullptr, &err);
    std::printf("blob column kept: %s\n", "see last row");
    sqlite3_prepare_v2(db, "SELECT typeof(b), b FROM t WHERE rowid = 3;", -1, &stmt, nullptr);
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("row 3 -> typeof=%s value=%s\n", sqlite3_column_text(stmt, 0),
                    sqlite3_column_text(stmt, 1));
    }
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    return 0;
}
```

```text
n: text    abc   | r: real    3.5   | b: integer 42    | s: text    42
n: integer 42    | r: text    x     | b: integer 42    | s: text    42
blob column kept: see last row
row 3 -> typeof=text value=still text
```

Measured, row by row:

| Column declared | Value written | Stored as | Why |
|---|---|---|---|
| `INTEGER` | `'abc'` | `text` | cannot be converted losslessly, so it is kept as text |
| `INTEGER` | `'42'` | `integer` | converts without loss, so it is converted |
| `REAL` | `'3.5'` | `real` | same rule, numeric affinity |
| `REAL` | `'x'` | `text` | not a number, so it stays text |
| `BLOB` | `42` | `integer` | **no affinity at all** — the value is stored exactly as given |
| `BLOB` | `'still text'` | `text` | ditto |
| `TEXT` | `42` | `text` | text affinity converts numbers to text |

This is *type affinity*: the declared type is a preference applied when a value is stored, not
a constraint enforced forever. It is genuinely useful — a column can hold both — and genuinely
dangerous, because a typo in a schema declaration will not show up as an error, only as a
column full of strings where you expected integers. If you want the constraint, add
`CHECK (typeof(n) = 'integer')`, or use `STRICT` tables, available from SQLite 3.37.

## Transactions: all of it or none of it

Without an explicit transaction, SQLite commits after every statement. That is called
autocommit, and it is the default because it is the simplest correct thing — not the thing you
want.

```cpp run
#include <sqlite3.h>

#include <cstdio>

static int count_rows(sqlite3 *db) {
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT count(*) FROM accounts;", -1, &stmt, nullptr);
    int n = -1;
    if (sqlite3_step(stmt) == SQLITE_ROW) n = sqlite3_column_int(stmt, 0);
    sqlite3_finalize(stmt);
    return n;
}

static void try_insert(sqlite3 *db, const char *name, const char *label) {
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO accounts (name) VALUES (?);", -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, name, -1, SQLITE_TRANSIENT);
    const int rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        std::printf("  %s -> rejected (%s)\n", label, sqlite3_errmsg(db));
    } else {
        std::printf("  %s -> stored\n", label);
    }
    sqlite3_finalize(stmt);
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;

    // ---- no transaction: every statement commits on its own -----------------
    sqlite3_exec(db, "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT UNIQUE);",
                 nullptr, nullptr, &err);
    try_insert(db, "ada", "insert ada");
    try_insert(db, "bob", "insert bob");
    try_insert(db, "ada", "insert ada again");
    std::printf("autocommit: rows = %d\n", count_rows(db));

    // ---- one transaction: all of it lands or none of it does ---------------
    sqlite3_exec(db, "DROP TABLE accounts;", nullptr, nullptr, &err);
    sqlite3_exec(db, "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT UNIQUE);",
                 nullptr, nullptr, &err);
    sqlite3_exec(db, "BEGIN;", nullptr, nullptr, &err);
    try_insert(db, "ada", "insert ada");
    try_insert(db, "bob", "insert bob");
    try_insert(db, "ada", "insert ada again");
    sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, &err);
    std::printf("after rollback: rows = %d\n", count_rows(db));

    // ---- and a transaction that does commit --------------------------------
    sqlite3_exec(db, "BEGIN;", nullptr, nullptr, &err);
    try_insert(db, "cleo", "insert cleo");
    try_insert(db, "dana", "insert dana");
    sqlite3_exec(db, "COMMIT;", nullptr, nullptr, &err);
    std::printf("after commit: rows = %d\n", count_rows(db));

    sqlite3_close(db);
    return 0;
}
```

```text
  insert ada -> stored
  insert bob -> stored
  insert ada again -> rejected (UNIQUE constraint failed: accounts.name)
autocommit: rows = 2
  insert ada -> stored
  insert bob -> stored
  insert ada again -> rejected (UNIQUE constraint failed: accounts.name)
after rollback: rows = 0
  insert cleo -> stored
  insert dana -> stored
after commit: rows = 2
```

Left to itself, the third insert fails and the first two stay: the database now holds a
half-finished piece of work. Wrapped in `BEGIN` … `ROLLBACK`, the same failure leaves nothing.
Wrapped in `BEGIN` … `COMMIT`, both rows land together.

The rule this makes possible is the one that matters: **a transaction is a unit, and the only
question is whether it committed.** A transfer that debits one account and credits another has
no intermediate state that any other reader can see, and no partial state that survives a
crash.

```cpp run
#include <sqlite3.h>

#include <cstdio>

static int count_rows(sqlite3 *db) {
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT count(*) FROM ledger;", -1, &stmt, nullptr);
    int n = -1;
    if (sqlite3_step(stmt) == SQLITE_ROW) n = sqlite3_column_int(stmt, 0);
    sqlite3_finalize(stmt);
    return n;
}

static void run(const char *sql) {
    sqlite3 *db = nullptr;
    sqlite3_open("ledger.db", &db);
    char *err = nullptr;
    sqlite3_exec(db, sql, nullptr, nullptr, &err);
    if (err) {
        std::printf("  error: %s\n", err);
        sqlite3_free(err);
    }
    std::printf("  rows visible here = %d\n", count_rows(db));
    sqlite3_close(db);
}

int main() {
    std::remove("ledger.db");
    run("CREATE TABLE ledger (id INTEGER PRIMARY KEY, note TEXT);"
        "INSERT INTO ledger (note) VALUES ('committed');");

    // BEGIN without COMMIT: sqlite3_close rolls the transaction back.
    run("BEGIN; INSERT INTO ledger (note) VALUES ('never committed');");

    std::printf("reopened:\n");
    run("SELECT 1;");

    // WAL changes who can read while someone writes, not whether COMMIT means
    // durable -- so it has to be asked for explicitly, per connection.
    sqlite3 *db = nullptr;
    sqlite3_open("ledger.db", &db);
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "PRAGMA journal_mode = WAL;", -1, &stmt, nullptr);
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("journal_mode after pragma = %s\n", sqlite3_column_text(stmt, 0));
    }
    sqlite3_finalize(stmt);
    sqlite3_close(db);

    std::remove("ledger.db");
    std::remove("ledger.db-wal");
    std::remove("ledger.db-shm");
    return 0;
}
```

```text
  rows visible here = 1
  rows visible here = 2
reopened:
  rows visible here = 1
journal_mode after pragma = wal
```

The second line is the one to internalise: the row was visible in the connection that wrote
it, and invisible after a reopen, because `BEGIN` without `COMMIT` is rolled back when the
connection closes. **Uncommitted work is not durable, and closing does not commit it.**

`PRAGMA journal_mode = WAL` switches the database into write-ahead logging, where readers do
not block writers and writers do not block readers. It is a per-database, persistent setting —
set it once and it survives in the file — but the *other* pragmas you care about are
per-connection and are not.

## Foreign keys are off unless you turn them on

```cpp run
#include <sqlite3.h>

#include <cstdio>

static void exec(sqlite3 *db, const char *sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("  rejected: %s\n", err);
        sqlite3_free(err);
    } else {
        std::printf("  accepted: %s\n", sql);
    }
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);

    exec(db, "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);");
    exec(db, "CREATE TABLE books (id INTEGER PRIMARY KEY,"
             " author_id INTEGER REFERENCES authors(id));");
    exec(db, "INSERT INTO authors VALUES (1, 'Ada');");

    int fk = 0;
    sqlite3_stmt *q = nullptr;
    sqlite3_prepare_v2(db, "PRAGMA foreign_keys;", -1, &q, nullptr);
    if (sqlite3_step(q) == SQLITE_ROW) fk = sqlite3_column_int(q, 0);
    sqlite3_finalize(q);
    std::printf("foreign_keys at startup = %d\n", fk);

    std::printf("with the pragma off:\n");
    exec(db, "INSERT INTO books VALUES (1, 99);");  // author 99 does not exist

    exec(db, "PRAGMA foreign_keys = ON;");
    std::printf("with the pragma on:\n");
    exec(db, "INSERT INTO books VALUES (2, 99);");

    sqlite3_prepare_v2(db, "SELECT count(*) FROM books;", -1, &q, nullptr);
    if (sqlite3_step(q) == SQLITE_ROW) {
        std::printf("books stored = %d\n", sqlite3_column_int(q, 0));
    }
    sqlite3_finalize(q);

    sqlite3_close(db);
    return 0;
}
```

```text
  accepted: CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
  accepted: CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER REFERENCES authors(id));
  accepted: INSERT INTO authors VALUES (1, 'Ada');
foreign_keys at startup = 0
with the pragma off:
  accepted: INSERT INTO books VALUES (1, 99);
  accepted: PRAGMA foreign_keys = ON;
with the pragma on:
  rejected: FOREIGN KEY constraint failed
books stored = 1
```

`foreign_keys` is **0** when a connection opens, and it stays 0 until you set it. Every
`REFERENCES` clause you wrote is documentation until then: the insert of a book with
`author_id = 99` is accepted silently, and you discover the orphan months later. One
`PRAGMA foreign_keys = ON;` immediately after `sqlite3_open` fixes it forever, in that
connection. Put it in the constructor of your wrapper so it cannot be forgotten.

This is not a quirk to shrug at. It is the same class of problem as the compiler warning you
turned off: a safety feature that is real, and off by default, and therefore absent from every
codebase whose author did not know to ask.

## A `TEXT` value is bytes, not a C string

```cpp run
#include <sqlite3.h>

#include <cstdio>
#include <cstring>

// A SQLite TEXT value is a counted byte string, not a C string. It can contain
// a zero byte, and every C API that treats it as one will silently truncate.
int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE blobs (payload TEXT);", nullptr, nullptr, &err);

    const char payload[] = {'a', '\0', 'b', 'c'};  // 4 bytes, one of them NUL
    sqlite3_stmt *insert = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO blobs VALUES (?);", -1, &insert, nullptr);
    sqlite3_bind_text(insert, 1, payload, static_cast<int>(sizeof(payload)), SQLITE_TRANSIENT);
    sqlite3_step(insert);
    sqlite3_finalize(insert);

    sqlite3_stmt *select = nullptr;
    sqlite3_prepare_v2(db, "SELECT payload FROM blobs;", -1, &select, nullptr);
    if (sqlite3_step(select) == SQLITE_ROW) {
        const unsigned char *text = sqlite3_column_text(select, 0);
        const int bytes = sqlite3_column_bytes(select, 0);
        std::printf("sqlite3_column_bytes = %d\n", bytes);
        std::printf("strlen               = %zu\n", std::strlen(reinterpret_cast<const char *>(text)));
        std::printf("bytes:");
        for (int i = 0; i < bytes; ++i) std::printf(" %02x", text[i]);
        std::printf("\n");
    }
    sqlite3_finalize(select);

    sqlite3_close(db);
    return 0;
}
```

```text
sqlite3_column_bytes = 4
strlen               = 1
bytes: 61 00 62 63
```

Four bytes were stored and `strlen` sees one, because the second byte is zero. Every SQLite
text value is a counted byte string, and the count is `sqlite3_column_bytes`. Anything that
treats the result of `sqlite3_column_text` as a C string — `strlen`, `printf("%s")`,
`std::string(char_ptr)` — truncates at the first zero byte. That is how a binary payload
becomes a two-character string, and it is also how an attacker hides content after a NUL from
a validator that reads it as C text.

There is one more lifetime rule hiding here: the pointer `sqlite3_column_text` returns is
valid **until the next `sqlite3_step` or `finalize`**. Copy it if you are going to keep it.

## Wrapping it: never call `close` by hand

Every rule above is a cleanup rule, and cleanup rules belong in destructors. Here is the whole
wrapper — the header, the implementation, a program that uses it, and the `Makefile` that
builds it. Each file is introduced by a banner comment; the banners are separators for the
listing, not part of the files.

```cpp make-files
/* ===== db.h ===== */

#ifndef DB_H
#define DB_H

#include <sqlite3.h>

#include <stdexcept>
#include <string>

// Every SQLite handle is a resource whose cleanup has a destructor-shaped rule,
// so this header is the one place the rule is written down.
class DbError : public std::runtime_error {
public:
    explicit DbError(const std::string &message) : std::runtime_error(message) {}
};

class Db {
public:
    explicit Db(const std::string &path);
    ~Db();
    Db(const Db &) = delete;
    Db &operator=(const Db &) = delete;

    void exec(const std::string &sql);
    long long last_row_id() const;
    sqlite3 *handle() const { return handle_; }

private:
    sqlite3 *handle_ = nullptr;
};

class Stmt {
public:
    Stmt(Db &db, const std::string &sql);
    ~Stmt();
    Stmt(const Stmt &) = delete;
    Stmt &operator=(const Stmt &) = delete;

    Stmt &bind(int index, const std::string &value);
    Stmt &bind(int index, int value);
    bool step();  // true while there is another row
    std::string text(int column) const;
    int integer(int column) const;
    void reset();

private:
    sqlite3 *db_;
    sqlite3_stmt *stmt_ = nullptr;
};

#endif

/* ===== db.cpp ===== */

#include "db.h"

#include <cstddef>

namespace {

void check(int rc, sqlite3 *db, const char *what) {
    if (rc != SQLITE_OK && rc != SQLITE_DONE && rc != SQLITE_ROW) {
        throw DbError(std::string(what) + ": " + sqlite3_errmsg(db));
    }
}

}  // namespace

Db::Db(const std::string &path) {
    const int rc = sqlite3_open(path.c_str(), &handle_);
    if (rc != SQLITE_OK) {
        // sqlite3_open still hands back a handle on most failures, and that
        // handle is the only place the real message lives.
        const std::string message =
            handle_ ? sqlite3_errmsg(handle_) : "could not allocate a handle";
        if (handle_) sqlite3_close(handle_);
        handle_ = nullptr;
        throw DbError("open " + path + ": " + message);
    }
}

Db::~Db() {
    // close() can fail (an unfinalised statement, a busy database) and a
    // destructor must not throw, so the code is dropped on purpose.
    if (handle_) sqlite3_close(handle_);
}

void Db::exec(const std::string &sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(handle_, sql.c_str(), nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::string message = err ? err : "unknown error";
        sqlite3_free(err);
        throw DbError("exec: " + message);
    }
}

long long Db::last_row_id() const { return sqlite3_last_insert_rowid(handle_); }

Stmt::Stmt(Db &db, const std::string &sql) : db_(db.handle()) {
    const int rc = sqlite3_prepare_v2(db_, sql.c_str(), -1, &stmt_, nullptr);
    if (rc != SQLITE_OK) {
        throw DbError("prepare: " + std::string(sqlite3_errmsg(db_)));
    }
}

Stmt::~Stmt() {
    if (stmt_) sqlite3_finalize(stmt_);
}

Stmt &Stmt::bind(int index, const std::string &value) {
    // SQLITE_TRANSIENT tells SQLite to copy now. The alternative,
    // SQLITE_STATIC, is a promise that the buffer outlives the statement --
    // see the pitfall in this chapter for what happens when it does not.
    check(sqlite3_bind_text(stmt_, index, value.c_str(), -1, SQLITE_TRANSIENT), db_, "bind text");
    return *this;
}

Stmt &Stmt::bind(int index, int value) {
    check(sqlite3_bind_int(stmt_, index, value), db_, "bind int");
    return *this;
}

bool Stmt::step() {
    const int rc = sqlite3_step(stmt_);
    if (rc == SQLITE_ROW) return true;
    if (rc == SQLITE_DONE) return false;
    throw DbError("step: " + std::string(sqlite3_errmsg(db_)));
}

std::string Stmt::text(int column) const {
    const unsigned char *value = sqlite3_column_text(stmt_, column);
    if (value == nullptr) return std::string();
    return std::string(reinterpret_cast<const char *>(value),
                       static_cast<std::size_t>(sqlite3_column_bytes(stmt_, column)));
}

int Stmt::integer(int column) const { return sqlite3_column_int(stmt_, column); }

void Stmt::reset() {
    // reset() reports the error from the *previous* execution, which is why a
    // serious wrapper checks it instead of assuming it succeeded.
    check(sqlite3_reset(stmt_), db_, "reset");
}

/* ===== main.cpp ===== */

#include "db.h"

#include <cstdio>

int main() {
    try {
        Db db(":memory:");
        db.exec("CREATE TABLE notes ("
                "  id    INTEGER PRIMARY KEY,"
                "  title TEXT NOT NULL,"
                "  body  TEXT);");

        Stmt insert(db, "INSERT INTO notes (title, body) VALUES (?, ?);");
        insert.bind(1, "first").bind(2, "written by the RAII wrapper").step();
        insert.reset();
        insert.bind(1, "second").bind(2, "same statement, rebound").step();
        std::printf("inserted, last rowid = %lld\n", db.last_row_id());

        Stmt select(db, "SELECT id, title, body FROM notes ORDER BY id;");
        while (select.step()) {
            std::printf("  %d. %s -- %s\n", select.integer(0), select.text(1).c_str(),
                        select.text(2).c_str());
        }

        // A failed statement is an exception, not a return code nobody checks.
        db.exec("INSERT INTO notes (title) VALUES (NULL);");
        std::printf("this line is never reached\n");
    } catch (const DbError &error) {
        std::printf("caught: %s\n", error.what());
    }
    return 0;
}

/* ===== Makefile ===== */

CXXFLAGS = -std=c++17 -Wall -Wextra -Werror
LDLIBS   = -lsqlite3

prog: main.cpp db.cpp db.h
	$(CXX) $(CXXFLAGS) -o prog main.cpp db.cpp $(LDLIBS)

clean:
	rm -f prog
```

```text
inserted, last rowid = 2
  1. first -- written by the RAII wrapper
  2. second -- same statement, rebound
caught: exec: NOT NULL constraint failed: notes.title
```

Three decisions in that code are worth defending:

- **`Db` opens, `Db::~Db` closes.** The destructor drops the result of `sqlite3_close`, because
  a destructor must not throw and `close` can fail. That is not sloppiness, it is the only
  legal option; if you need to know whether a close failed, call it explicitly before the
  object dies.
- **`Stmt` prepares, `Stmt::~Stmt` finalises.** Now a `return` in the middle of a query, or an
  exception thrown by the code around it, cannot leak a statement. Compare with the previous
  chapter's file handles: this is the same argument, one layer up.
- **Failures are exceptions, not return codes.** `DbError` carries
  `sqlite3_errmsg`, so the message you log is the message SQLite produced rather than a guess.

The `Makefile` needs `-lsqlite3`, and it needs it **after** the object files — on many linkers
a `-l` placed before the thing that needs it is silently ignored. That is the whole reason this
chapter declares `libs: sqlite3` in its front matter: the harness adds the flag in the right
place, and you should too.

```sh run-project
make clean
make
./prog
```

```text
rm -f prog
c++ -std=c++17 -Wall -Wextra -Werror -o prog main.cpp db.cpp -lsqlite3
inserted, last rowid = 2
  1. first -- written by the RAII wrapper
  2. second -- same statement, rebound
caught: exec: NOT NULL constraint failed: notes.title
```

:::scenario The migration that must not lose a row
Your service has 40 000 rows in a table, and a release needs to add a `NOT NULL` column with a
default. The migration script runs `ALTER TABLE` inside a loop that also backfills the new
column row by row, and the release must be reversible. Halfway through on one machine it dies:
power, or a `SIGKILL` from the supervisor, or a disk that filled. What does the database look
like when it comes back, and what should the script have done?
:::

:::solution Migration
**What it looks like:** unchanged. SQLite is a transactional database with a write-ahead
rollback journal, so a connection that dies mid-transaction leaves the file in a state that the
*next* reader repairs before it answers its first query. The `ALTER TABLE` and every backfill
row written inside the transaction disappear together. What does *not* disappear is anything
you committed outside a transaction, which is why the loop matters: if the backfill ran in
autocommit, rows 1 through 18 442 are now permanently half-migrated and there is no
"undo" — only another migration that has to figure out where it stopped.

**What the script should have done:**

1. One transaction for the whole migration: `BEGIN;` … `ALTER TABLE` … backfill …
   `COMMIT;`. Measured in this chapter, the failure then leaves zero rows changed instead of
   18 442.
2. `PRAGMA foreign_keys = ON;` in the same connection, first thing — a migration that adds a
   foreign key but never turns the pragma on is adding a comment.
3. A version stamp written *in the same transaction*:
   `INSERT INTO schema_meta (version) VALUES (7);`. Then "did the migration run?" is a query,
   not an inference from whether a column exists.
4. Make it reversible by writing the down-migration before the up-migration ships, and by
   keeping the destructive step — `DROP COLUMN`, or a rewrite that loses data — in a later
   release. A migration that is safe to run and unsafe to undo is a one-way door.

The general shape: **a migration is a transaction, and a transaction's only two outcomes are
"all of it" and "none of it".** Design for the second one.
:::

:::pitfall The five mistakes that actually happen
1. **`SQLITE_STATIC` on a temporary.** Use-after-free at `sqlite3_step`, invisible without a
   sanitizer, and the object is a `std::string::c_str()` nine times out of ten.
2. **`sqlite3_column_text` treated as a C string.** Truncates at an embedded zero byte, and
   the pointer dies at the next `step`. Copy with `sqlite3_column_bytes`.
3. **Binding to index 0.** `sqlite3_bind_parameter_index` returns 0 for an unknown name, and
   binding to 0 is a silent no-op that leaves the column `NULL`.
4. **Forgetting `PRAGMA foreign_keys = ON`.** Every `REFERENCES` clause is decorative until
   you do.
5. **`BEGIN` without `COMMIT`.** Closing the connection rolls it back, so the work was never
   durable — and in autocommit there is no transaction to roll back, so a mid-way failure
   leaves a half-finished state permanently.
:::

## Key takeaways

- `sqlite3_open` can return an error **and** a usable handle; read `sqlite3_errmsg` from that
  handle before you decide the message is unavailable.
- `sqlite3_exec` runs whatever SQL text you hand it, including several statements at once, so
  it is only safe when every value in that text is a literal you wrote.
- A bound parameter is applied after parsing, which is why it cannot be injected into; string
  concatenation happens before parsing, which is why it can.
- `sqlite3_step` returns `SQLITE_ROW` (100) while rows remain and `SQLITE_DONE` (101) at the
  end; a wrapper that treats "not `SQLITE_OK`" as failure breaks every successful query.
- `SQLITE_TRANSIENT` copies a bound string; `SQLITE_STATIC` stores the pointer and reads it
  later, and a pointer to a dead `std::string` is `heap-use-after-free` inside `sqlite3VdbeExec`.
- Column types are *affinity*: SQLite converts when it can and stores as given when it cannot,
  and a `BLOB` column has no affinity at all.
- A transaction is atomic: `BEGIN` … `COMMIT` lands together, `ROLLBACK` leaves nothing, and
  closing a connection with an open transaction rolls it back.
- `foreign_keys` is off when a connection opens and must be turned on per connection, or every
  `REFERENCES` clause you wrote is documentation.
- SQLite text is a counted byte string: `sqlite3_column_bytes` is the length, `strlen` is a
  guess that stops at the first zero byte.
- Put `sqlite3_close` in a destructor and `sqlite3_finalize` in another one, and the cleanup
  rules above stop being things you have to remember.

## Practice

- [ ] **Exercise 1.** Open a *file-backed* database, create `visits (url TEXT PRIMARY KEY,
      hits INTEGER NOT NULL DEFAULT 0)`, insert three rows, update one, and print
      `sqlite3_total_changes` after each step. Then write an upsert with
      `ON CONFLICT (url) DO UPDATE SET hits = hits + 1` and confirm it increments instead of
      failing.
- [ ] **Exercise 2.** Here is a lookup that leaks every row:

      `const std::string sql = "SELECT email FROM people WHERE name = '" + name + "';";`

      Rewrite it with a bound parameter, and prove the fix by passing
      `' OR '1' = '1` to both versions.
- [ ] **Exercise 3.** Insert 500 rows into a table, then use `EXPLAIN QUERY PLAN` to show that
      a `SELECT ... WHERE kind = 'click'` scans the table before an index exists and searches
      the index after it does.
- [ ] **Exercise 4.** `ROLLBACK` undoes a whole transaction. Use `SAVEPOINT` / `ROLLBACK TO` /
      `RELEASE` to undo only the second half of one, keeping the first.
- [ ] **Exercise 5.** Write `std::optional<std::string> scalar(sqlite3 *, const std::string &)`
      that returns the first column of the first row, and make it distinguish *no row* from *a
      row whose value is NULL* from *bad SQL*.

## Solutions

:::solution Exercise 1
`sqlite3_total_changes` counts every row the connection has ever changed, while
`sqlite3_changes` counts only the last statement — so it is the one to print when you are
checking a batch. The upsert is the interesting part: it is one statement, so it cannot be
interrupted between "look for the row" and "insert it".

```cpp run
#include <sqlite3.h>

#include <cstdio>

int main() {
    std::remove("visits.db");
    sqlite3 *db = nullptr;
    sqlite3_open("visits.db", &db);
    char *err = nullptr;

    sqlite3_exec(db,
                 "CREATE TABLE visits ("
                 "  url  TEXT PRIMARY KEY,"
                 "  hits INTEGER NOT NULL DEFAULT 0);"
                 "INSERT INTO visits (url) VALUES ('/'), ('/about'), ('/pricing');",
                 nullptr, nullptr, &err);
    std::printf("total_changes after setup = %d\n", sqlite3_total_changes(db));

    sqlite3_exec(db, "UPDATE visits SET hits = hits + 1 WHERE url = '/';", nullptr, nullptr, &err);
    std::printf("total_changes after update = %d\n", sqlite3_total_changes(db));

    // An upsert: insert, or fold into the existing row. No SELECT-then-decide.
    sqlite3_exec(db,
                 "INSERT INTO visits (url, hits) VALUES ('/', 1)"
                 " ON CONFLICT (url) DO UPDATE SET hits = hits + 1;",
                 nullptr, nullptr, &err);
    std::printf("total_changes after upsert = %d\n", sqlite3_total_changes(db));

    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, "SELECT url, hits FROM visits ORDER BY url;", -1, &stmt, nullptr);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("  %-10s %d\n", sqlite3_column_text(stmt, 0), sqlite3_column_int(stmt, 1));
    }
    sqlite3_finalize(stmt);

    sqlite3_close(db);
    std::remove("visits.db");
    return 0;
}
```

```text
total_changes after setup = 3
total_changes after update = 4
total_changes after upsert = 5
  /          2
  /about     0
  /pricing   0
```

The `PRIMARY KEY` on `url` is what `ON CONFLICT` needs in order to know what counts as a
conflict; without it, the insert would just succeed and you would have two rows for `/`.
:::

:::solution Exercise 2
The unsafe version returns the whole table, because `'1' = '1'` is true for every row. The
fixed version returns nothing for the same input and the right row for a real name:

```cpp run
#include <sqlite3.h>

#include <cstdio>
#include <string>
#include <vector>

// The shape the exercise starts from: the caller's string is part of the SQL.
static std::vector<std::string> find_by_name_unsafe(sqlite3 *db, const std::string &name) {
    const std::string sql = "SELECT email FROM people WHERE name = '" + name + "';";
    std::vector<std::string> out;
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
        std::printf("  rejected: %s\n", sqlite3_errmsg(db));
        return out;
    }
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        out.emplace_back(reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0)));
    }
    sqlite3_finalize(stmt);
    return out;
}

// The fix: the caller's string becomes a value the engine binds, never text it parses.
static std::vector<std::string> find_by_name(sqlite3 *db, const std::string &name) {
    std::vector<std::string> out;
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, "SELECT email FROM people WHERE name = ?;", -1, &stmt, nullptr) !=
        SQLITE_OK) {
        std::printf("  rejected: %s\n", sqlite3_errmsg(db));
        return out;
    }
    sqlite3_bind_text(stmt, 1, name.c_str(), -1, SQLITE_TRANSIENT);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char *text = sqlite3_column_text(stmt, 0);
        out.emplace_back(reinterpret_cast<const char *>(text),
                         static_cast<std::size_t>(sqlite3_column_bytes(stmt, 0)));
    }
    sqlite3_finalize(stmt);
    return out;
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE people (name TEXT, email TEXT);"
                 "INSERT INTO people VALUES ('ada', 'ada@example.com');",
                 nullptr, nullptr, &err);

    const std::string attack = "' OR '1' = '1";

    std::printf("unsafe, with %s:\n", attack.c_str());
    for (const std::string &s : find_by_name_unsafe(db, attack)) std::printf("  hit: %s\n", s.c_str());

    std::printf("bound, with the same string:\n");
    const std::vector<std::string> hits = find_by_name(db, attack);
    std::printf("  hits: %zu\n", hits.size());
    for (const std::string &s : hits) std::printf("  hit: %s\n", s.c_str());

    std::printf("bound, with a real name:\n");
    for (const std::string &s : find_by_name(db, "ada")) std::printf("  hit: %s\n", s.c_str());

    sqlite3_close(db);
    return 0;
}
```

```text
unsafe, with ' OR '1' = '1:
  hit: ada@example.com
bound, with the same string:
  hits: 0
bound, with a real name:
  hit: ada@example.com
```

Note that the fixed version also copies with `sqlite3_column_bytes` instead of constructing
from `char *`, so a value containing a zero byte survives.
:::

:::solution Exercise 3
`EXPLAIN QUERY PLAN` is a query whose result *is* the plan: run it and read column 3.

```cpp run
#include <sqlite3.h>

#include <cstdio>
#include <string>

static void plan(sqlite3 *db, const char *label, const char *sql) {
    const std::string explained = std::string("EXPLAIN QUERY PLAN ") + sql;
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, explained.c_str(), -1, &stmt, nullptr);
    std::printf("%s\n", label);
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        std::printf("  %s\n", sqlite3_column_text(stmt, 3));
    }
    sqlite3_finalize(stmt);
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db, "CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT, at INTEGER);",
                 nullptr, nullptr, &err);

    sqlite3_stmt *fill = nullptr;
    sqlite3_prepare_v2(db, "INSERT INTO events (kind, at) VALUES (?, ?);", -1, &fill, nullptr);
    for (int i = 0; i < 500; ++i) {
        sqlite3_bind_text(fill, 1, i % 2 ? "click" : "view", -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(fill, 2, i);
        sqlite3_step(fill);
        sqlite3_reset(fill);
    }
    sqlite3_finalize(fill);

    const char *query = "SELECT id FROM events WHERE kind = 'click';";
    plan(db, "before the index:", query);

    sqlite3_exec(db, "CREATE INDEX events_kind ON events (kind);", nullptr, nullptr, &err);
    plan(db, "after the index:", query);

    // ANALYZE tells the planner how the data is distributed, which is what it
    // uses to decide whether the index is worth using at all.
    sqlite3_exec(db, "ANALYZE;", nullptr, nullptr, &err);
    plan(db, "after ANALYZE:", query);

    sqlite3_close(db);
    return 0;
}
```

```text
before the index:
  SCAN events
after the index:
  SEARCH events USING COVERING INDEX events_kind (kind=?)
after ANALYZE:
  SEARCH events USING COVERING INDEX events_kind (kind=?)
```

`SCAN` means every row was examined; `SEARCH ... USING COVERING INDEX` means the index
answered the question without touching the table at all, because `id` is in the index too (an
index on `(kind)` carries the rowid). With 500 rows evenly split between two kinds, SQLite
sometimes still prefers a scan — the planner uses statistics, and `ANALYZE` is what fills them
in. Small tables are the classic case where an index does not help.
:::

:::solution Exercise 4
A savepoint is a named mark inside a transaction. `ROLLBACK TO` rewinds to the mark and keeps
the transaction open; `RELEASE` then discards the mark.

```cpp run
#include <sqlite3.h>

#include <cstdio>
#include <string>

static void exec(sqlite3 *db, const char *sql) {
    char *err = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &err);
    if (rc != SQLITE_OK) {
        std::printf("  rejected: %s\n", err);
        sqlite3_free(err);
    }
}

static int count(sqlite3 *db, const char *table) {
    sqlite3_stmt *stmt = nullptr;
    const std::string sql = std::string("SELECT count(*) FROM ") + table + ";";
    sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    int n = -1;
    if (sqlite3_step(stmt) == SQLITE_ROW) n = sqlite3_column_int(stmt, 0);
    sqlite3_finalize(stmt);
    return n;
}

static void add(sqlite3 *db, const char *table, const char *note) {
    sqlite3_stmt *stmt = nullptr;
    const std::string sql = std::string("INSERT INTO ") + table + " (note) VALUES (?);";
    sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, note, -1, SQLITE_TRANSIENT);
    const int rc = sqlite3_step(stmt);
    std::printf("  add %-8s -> %s\n", note, rc == SQLITE_DONE ? "ok" : sqlite3_errmsg(db));
    sqlite3_finalize(stmt);
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    exec(db, "CREATE TABLE ledger (id INTEGER PRIMARY KEY, note TEXT UNIQUE);");

    // One outer transaction, one savepoint inside it. Rolling back to the
    // savepoint keeps the work done before it and discards only what came after.
    exec(db, "BEGIN;");
    add(db, "ledger", "alpha");

    exec(db, "SAVEPOINT risky;");
    add(db, "ledger", "bravo");
    add(db, "ledger", "alpha");  // UNIQUE violation, inside the savepoint
    exec(db, "ROLLBACK TO risky;");
    exec(db, "RELEASE risky;");
    std::printf("after ROLLBACK TO: rows = %d\n", count(db, "ledger"));

    add(db, "ledger", "charlie");
    exec(db, "COMMIT;");
    std::printf("after COMMIT:      rows = %d\n", count(db, "ledger"));

    sqlite3_close(db);
    return 0;
}
```

```text
  add alpha    -> ok
  add bravo    -> ok
  add alpha    -> UNIQUE constraint failed: ledger.note
after ROLLBACK TO: rows = 1
  add charlie  -> ok
after COMMIT:      rows = 2
```

`alpha` survives, `bravo` does not, and `charlie` was added after the savepoint was released,
so it survives too. Note that `ROLLBACK TO` does **not** end the transaction — you still need
`COMMIT`, and `RELEASE` is not `COMMIT`.
:::

:::solution Exercise 5
`sqlite3_column_type` is what separates "no row" from "NULL": with no row, `sqlite3_step`
returns `SQLITE_DONE` and there is nothing to inspect; with a row, the column type says
whether the value is `SQLITE_NULL`.

```cpp run
#include <sqlite3.h>

#include <cstdio>
#include <optional>
#include <string>

// A missing row and a row holding NULL are different facts, and collapsing them
// into "" is how a service ends up reporting a zero that was never recorded.
static std::optional<std::string> scalar(sqlite3 *db, const std::string &sql) {
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) return std::nullopt;
    const int rc = sqlite3_step(stmt);
    std::optional<std::string> out;
    if (rc == SQLITE_ROW) {
        if (sqlite3_column_type(stmt, 0) == SQLITE_NULL) {
            out = std::nullopt;  // there is a row, and its value is NULL
        } else {
            const unsigned char *text = sqlite3_column_text(stmt, 0);
            out = std::string(reinterpret_cast<const char *>(text),
                              static_cast<std::size_t>(sqlite3_column_bytes(stmt, 0)));
        }
    }
    sqlite3_finalize(stmt);
    return out;
}

static void report(const char *label, const std::optional<std::string> &value) {
    if (!value.has_value()) {
        std::printf("%s -> (no value)\n", label);
    } else {
        std::printf("%s -> %s\n", label, value->c_str());
    }
}

int main() {
    sqlite3 *db = nullptr;
    sqlite3_open(":memory:", &db);
    char *err = nullptr;
    sqlite3_exec(db,
                 "CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT);"
                 "INSERT INTO settings VALUES ('theme', 'dark'), ('tz', NULL);",
                 nullptr, nullptr, &err);

    report("theme", scalar(db, "SELECT value FROM settings WHERE key = 'theme';"));
    report("tz    ", scalar(db, "SELECT value FROM settings WHERE key = 'tz';"));
    report("missing", scalar(db, "SELECT value FROM settings WHERE key = 'nope';"));
    report("bad sql", scalar(db, "SELECT value FROM no_such_table;"));

    sqlite3_close(db);
    return 0;
}
```

```text
theme -> dark
tz     -> (no value)
missing -> (no value)
bad sql -> (no value)
```

Distinguishing the two is not pedantry. "The setting is absent" and "the setting is present and
empty" are different states, and a service that collapses them will report a default where the
user asked for nothing, or silently drop a value that was deliberately blank.
:::
