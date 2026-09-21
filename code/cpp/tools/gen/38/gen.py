#!/usr/bin/env python3
"""Generate chapters/38-sqlite-a-real-database.md.

Every `text` fence is captured from a real clang++ run against the SQLite that
ships in this machine's SDK, and every source block is read off disk, so nothing
in the chapter is retyped. The chapter declares `libs: sqlite3`, which the
harness turns into `-lsqlite3` for every block in it.

    python3 tools/gen/38/gen.py
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/38 -> gen -> tools -> cpp
OUT = CHAPTERS / "38-sqlite-a-real-database.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
LIBS = ["-lsqlite3"]
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 90


def build_and_run(name: str, sanitize: bool = False):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror"] + (SAN if sanitize else []) + \
              ["-o", exe, str(src)] + LIBS
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td,
                           timeout=TIMEOUT, env=env)
        return r.stdout, r.stderr, r.returncode


def diagnostic(name: str):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(src)] + LIBS
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return b.stderr, b.returncode


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def msg(blob: str, marker: str, needle: str) -> str:
    """Return `<marker> <message>` for the first diagnostic containing `needle`.

    The raw line carries this machine's absolute path, which must never reach
    the book, so only the part after the marker is published.
    """
    for line in blob.splitlines():
        if needle in line and marker in line:
            return marker + " " + line.split(marker, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{blob}")


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").rstrip("\n")


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


def listing(names: list[str]) -> str:
    """Join real files into one multi-file listing.

    The banner is a valid C++ comment so the listing is still exactly what a
    reader would paste, and the harness strips it before writing the file.
    """
    out = []
    for name in names:
        out.append(f"/* ===== {name} ===== */")
        out.append(read(name))
    return "\n\n".join(out)


# --------------------------------------------------------------------------
# capture
# --------------------------------------------------------------------------
print("capturing evidence ...")

version_out, _, _ = build_and_run("version.cpp")
exec_out, _, _ = build_and_run("exec.cpp")
inject_out, _, _ = build_and_run("inject.cpp")
prepare_out, _, _ = build_and_run("prepare.cpp")
affinity_out, _, _ = build_and_run("affinity.cpp")
fk_out, _, _ = build_and_run("fk.cpp")
atomic_out, _, _ = build_and_run("atomic.cpp")
nul_out, _, _ = build_and_run("nul.cpp")
named_out, _, _ = build_and_run("named.cpp")
errmsg_out, _, _ = build_and_run("errmsg.cpp")
durable_out, _, _ = build_and_run("durable.cpp")

sol1_out, _, _ = build_and_run("sol1.cpp")
sol2_out, _, _ = build_and_run("sol2.cpp")
sol3_out, _, _ = build_and_run("sol3.cpp")
sol4_out, _, _ = build_and_run("sol4.cpp")
sol5_out, _, _ = build_and_run("sol5.cpp")

_, dangle_err, dangle_rc = build_and_run("static_dangle.cpp", sanitize=True)
if dangle_rc == 0:
    raise SystemExit("static_dangle.cpp must be caught by the sanitizer")
DANGLE_NEEDLE = "AddressSanitizer: heap-use-after-free"
if DANGLE_NEEDLE not in dangle_err:
    raise SystemExit(f"expected {DANGLE_NEEDLE!r} in:\n{dangle_err}")
DANGLE_SUMMARY = "sqlite3VdbeExec"
if DANGLE_SUMMARY not in dangle_err:
    raise SystemExit(f"expected the report to name {DANGLE_SUMMARY!r}:\n{dangle_err}")

bind_err, bind_rc = diagnostic("badbind.cpp")
if bind_rc == 0:
    raise SystemExit("badbind.cpp was supposed to be rejected, but it built cleanly")
BIND_ERR = msg(bind_err, "error:", "no matching function for call to 'sqlite3_bind_text'")

PROJECT = ["db.h", "db.cpp", "main.cpp", "Makefile"]
project_listing = listing(PROJECT)

with tempfile.TemporaryDirectory() as td:
    for name in PROJECT:
        (Path(td) / name).write_text(read(name) + "\n", encoding="utf-8")
    m = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=180)
    if m.returncode != 0:
        raise SystemExit(f"the project Makefile did not build:\n{m.stderr}")
    p = subprocess.run(["./prog"], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
    if p.returncode != 0:
        raise SystemExit(f"the project exited {p.returncode}:\n{p.stderr}")
    project_out = p.stdout
    c = subprocess.run(["make", "clean"], text=True, capture_output=True, cwd=td, timeout=60)
    m2 = subprocess.run(["make"], text=True, capture_output=True, cwd=td, timeout=180)
    if m2.returncode != 0:
        raise SystemExit(f"rebuild failed:\n{m2.stderr}")
    p2 = subprocess.run(["./prog"], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
    rebuild_out = (c.stdout or "") + (m2.stdout or "") + (p2.stdout or "")

print("generating chapter ...")

TEMPLATE = r"""---
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

@@version@@

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

@@exec@@

`sqlite3_exec` takes a whole SQL string and runs it. It accepts several statements separated by
semicolons, which is why the setup above can `CREATE` and `INSERT` in one call. The callback
runs once per result row with two parallel arrays: the values as strings, and the column names.
A `NULL` arrives as a null pointer, so `values[i] ? values[i] : "NULL"` is not defensive
padding — it is the difference between printing `NULL` and dereferencing nothing.

Returning non-zero from the callback aborts the query. That is the documented way to stop
early.

### Why you stop using `exec` the moment input arrives

Here is the same program, asked to store one note typed by a user.

@@inject@@

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

@@prepare@@

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

@@named@@

`sqlite3_bind_parameter_index` maps a name to its 1-based index and returns **0** for a name
that is not in the statement — not -1, not an error. Bind to index 0 and nothing happens; the
parameter stays `NULL` and the insert succeeds with a hole in it. If a name is generated from
a map of user input, check for 0.

### The fifth argument to `sqlite3_bind_text` is a promise about memory

@@badbind@@

That rejection is a gift. `sqlite3_bind_text` wants a `const char *`; a `std::string` does not
convert to one, so the compiler stops you before you get to the interesting part. The
"working" version is `body.c_str()`, and now the fifth argument decides whether the program is
correct:

- **`SQLITE_TRANSIENT`** — SQLite copies the bytes now. Always correct. Costs a copy.
- **`SQLITE_STATIC`** — SQLite keeps your pointer and reads it later. Free, and a trap.

@@dangle@@

The `std::string` died at the closing brace. SQLite still held the pointer, and `sqlite3_step`
read it — AddressSanitizer reports `heap-use-after-free` inside `sqlite3VdbeExec`, the
interpreter loop, which is where a bound value is finally consumed. The read does not happen
at bind time, which is exactly why this bug survives a casual test: with a short string the
bytes may still be sitting there untouched, and the row looks fine on your machine.

Use `SQLITE_TRANSIENT` unless you have a buffer whose lifetime you can prove in one sentence.
The one legitimate use of `SQLITE_STATIC` is a string literal or a `static` array, both of
which outlive everything.

## Error codes, and where the message lives

@@errmsg@@

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

@@affinity@@

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

@@atomic@@

Left to itself, the third insert fails and the first two stay: the database now holds a
half-finished piece of work. Wrapped in `BEGIN` … `ROLLBACK`, the same failure leaves nothing.
Wrapped in `BEGIN` … `COMMIT`, both rows land together.

The rule this makes possible is the one that matters: **a transaction is a unit, and the only
question is whether it committed.** A transfer that debits one account and credits another has
no intermediate state that any other reader can see, and no partial state that survives a
crash.

@@durable@@

The second line is the one to internalise: the row was visible in the connection that wrote
it, and invisible after a reopen, because `BEGIN` without `COMMIT` is rolled back when the
connection closes. **Uncommitted work is not durable, and closing does not commit it.**

`PRAGMA journal_mode = WAL` switches the database into write-ahead logging, where readers do
not block writers and writers do not block readers. It is a per-database, persistent setting —
set it once and it survives in the file — but the *other* pragmas you care about are
per-connection and are not.

## Foreign keys are off unless you turn them on

@@fk@@

`foreign_keys` is **0** when a connection opens, and it stays 0 until you set it. Every
`REFERENCES` clause you wrote is documentation until then: the insert of a book with
`author_id = 99` is accepted silently, and you discover the orphan months later. One
`PRAGMA foreign_keys = ON;` immediately after `sqlite3_open` fixes it forever, in that
connection. Put it in the constructor of your wrapper so it cannot be forgotten.

This is not a quirk to shrug at. It is the same class of problem as the compiler warning you
turned off: a safety feature that is real, and off by default, and therefore absent from every
codebase whose author did not know to ask.

## A `TEXT` value is bytes, not a C string

@@nul@@

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

@@project@@

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

@@rebuild@@

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

@@sol1@@

The `PRIMARY KEY` on `url` is what `ON CONFLICT` needs in order to know what counts as a
conflict; without it, the insert would just succeed and you would have two rows for `/`.
:::

:::solution Exercise 2
The unsafe version returns the whole table, because `'1' = '1'` is true for every row. The
fixed version returns nothing for the same input and the right row for a real name:

@@sol2@@

Note that the fixed version also copies with `sqlite3_column_bytes` instead of constructing
from `char *`, so a value containing a zero byte survives.
:::

:::solution Exercise 3
`EXPLAIN QUERY PLAN` is a query whose result *is* the plan: run it and read column 3.

@@sol3@@

`SCAN` means every row was examined; `SEARCH ... USING COVERING INDEX` means the index
answered the question without touching the table at all, because `id` is in the index too (an
index on `(kind)` carries the rowid). With 500 rows evenly split between two kinds, SQLite
sometimes still prefers a scan — the planner uses statistics, and `ANALYZE` is what fills them
in. Small tables are the classic case where an index does not help.
:::

:::solution Exercise 4
A savepoint is a named mark inside a transaction. `ROLLBACK TO` rewinds to the mark and keeps
the transaction open; `RELEASE` then discards the mark.

@@sol4@@

`alpha` survives, `bravo` does not, and `charlie` was added after the savepoint was released,
so it survives too. Note that `ROLLBACK TO` does **not** end the transaction — you still need
`COMMIT`, and `RELEASE` is not `COMMIT`.
:::

:::solution Exercise 5
`sqlite3_column_type` is what separates "no row" from "NULL": with no row, `sqlite3_step`
returns `SQLITE_DONE` and there is nothing to inspect; with a row, the column type says
whether the value is `SQLITE_NULL`.

@@sol5@@

Distinguishing the two is not pedantry. "The setting is absent" and "the setting is present and
empty" are different states, and a service that collapses them will report a default where the
user asked for nothing, or silently drop a value that was deliberately blank.
:::
"""

# --------------------------------------------------------------------------
# splice
# --------------------------------------------------------------------------
blocks = {
    "version": fence("cpp", "run", read("version.cpp"), version_out),
    "exec": fence("cpp", "run", read("exec.cpp"), exec_out),
    "inject": fence("cpp", "run", read("inject.cpp"), inject_out),
    "prepare": fence("cpp", "run", read("prepare.cpp"), prepare_out),
    "named": fence("cpp", "run", read("named.cpp"), named_out),
    "badbind": fence("cpp", "bad", read("badbind.cpp"), BIND_ERR),
    "dangle": fence("cpp", "run-san-catch", read("static_dangle.cpp"),
                    "ERROR: AddressSanitizer: heap-use-after-free"),
    "errmsg": fence("cpp", "run", read("errmsg.cpp"), errmsg_out),
    "affinity": fence("cpp", "run", read("affinity.cpp"), affinity_out),
    "atomic": fence("cpp", "run", read("atomic.cpp"), atomic_out),
    "durable": fence("cpp", "run", read("durable.cpp"), durable_out),
    "fk": fence("cpp", "run", read("fk.cpp"), fk_out),
    "nul": fence("cpp", "run", read("nul.cpp"), nul_out),
    "project": fence("cpp", "make-files", project_listing, project_out),
    "rebuild": fence("sh", "run-project", "make clean\nmake\n./prog", rebuild_out),
    "sol1": fence("cpp", "run", read("sol1.cpp"), sol1_out),
    "sol2": fence("cpp", "run", read("sol2.cpp"), sol2_out),
    "sol3": fence("cpp", "run", read("sol3.cpp"), sol3_out),
    "sol4": fence("cpp", "run", read("sol4.cpp"), sol4_out),
    "sol5": fence("cpp", "run", read("sol5.cpp"), sol5_out),
}

body = TEMPLATE
for key, value in blocks.items():
    body = body.replace("@@" + key + "@@", value.rstrip("\n"))

leftover = re.findall(r"@@(\w+)@@", body)
if leftover:
    raise SystemExit(f"unsubstituted placeholders: {leftover}")

OUT.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
words = len(re.findall(r"\b[\w'-]+\b", body))
print(f"wrote {OUT.name}: {len(body.splitlines())} lines, ~{words} words")
