---
chapter: 19
part: 3
title: Working with Data: CSV, SQLite & SQLAlchemy
summary: Move data out of ad-hoc lists and into real storage — read and write messy CSVs, design and query a SQLite database safely, and map it to Python objects with SQLAlchemy 2.x.
minutes: 50
tags: [csv, sqlite, sqlalchemy, sql, migrations, orm]
---

A list of dicts is the right tool right up until it isn't: the data outlives the process, two
programs need it at once, or someone asks "what was the total in March?" and you have to load
400 MB into memory to answer. That is the moment to give the data a home — a file format with
rules, or a database. This chapter covers both, starting with the format every business on earth
sends you, then the database that is already installed on your machine.

## When a list of dicts stops being enough

Ask four questions. If any answer is yes, you need storage:

- Does the data need to survive the program exiting?
- Is it too big to fit comfortably in memory?
- Do you need to ask questions of it (filter, group, join) rather than just loop over it?
- Does more than one process write to it?

Under a few thousand short records, a list of dicts in a JSON file is fine — Chapter 8 territory.
Above that, or when the shape matters, use a database. And when someone hands you a spreadsheet,
use `csv`.

## Reading CSV with DictReader

The `csv` module is in the standard library. `DictReader` gives you each row as a dict keyed by
the header row, which is nearly always what you want.

```python
import csv
from pathlib import Path


def read_sales(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


for row in read_sales(Path("sales.csv")):
    print(row["Region"], row["Total"])
```

Two details that save real debugging. `newline=""` is **required** by the docs — the csv module
handles line endings itself, and without it you get blank rows on files from Windows. And
`encoding="utf-8-sig"` strips the byte-order mark that Excel adds; without it your first column
name becomes `\ufeffRegion` and every lookup on it fails mysteriously.

Real files are messy: headers arrive as `Total Sales `, `TOTAL_SALES`, or `totalSales` depending
on who exported the file that week. Normalise at the edge, once:

```python
def normalise(row: dict[str, str | None]) -> dict[str, str]:
    """Lower-case, underscore, strip every header; blank out missing values."""
    clean: dict[str, str] = {}
    for key, value in row.items():
        if key is None:                     # csv puts extra columns under None
            continue
        clean[key.strip().lower().replace(" ", "_")] = (value or "").strip()
    return clean


rows = [normalise(row) for row in read_sales(Path("sales.csv"))]
print(rows[0])
```

`DictReader` has two behaviours worth knowing: a row with *more* fields than headers collects the
extras under `restkey` (which defaults to `None`, hence the check above), and a row with *fewer*
fills the gaps with `restval`, which defaults to `None` — not `""`. That is why the function
coerces with `or ""`.

## Writing CSV with DictWriter

```python
FIELDS = ["region", "total", "sales_rep"]


def write_clean_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


write_clean_csv(Path("clean.csv"), rows)
```

`extrasaction="ignore"` lets you pass full rows without hand-picking columns; the default is
`"raise"`, which is a decent early-warning system for typos.

For non-standard separators use a dialect, which bundles delimiter, quoting, and line terminator:

```python
csv.register_dialect("pipes", delimiter="|", quoting=csv.QUOTE_MINIMAL)

with Path("legacy.txt").open("w", newline="", encoding="utf-8") as handle:
    csv.writer(handle, dialect="pipes").writerows([["a", "b"], ["c", "d"]])
```

`csv.Sniffer` can guess a dialect from a sample, but it guesses wrong often enough that you
should just ask whoever produced the file.

## SQLite: the database in your pocket

SQLite is a full SQL database that stores everything in one file, needs no server, and ships with
Python. It handles gigabytes and concurrent readers happily. Use it unless you have a reason not
to.

```python
import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path("shop.db"))
conn.execute("PRAGMA foreign_keys = ON")   # OFF by default in SQLite, per connection
conn.row_factory = sqlite3.Row             # rows behave like dicts instead of tuples
```

Both of those lines matter. Foreign key constraints are silently ignored unless you enable the
pragma, and without `row_factory` you get positional tuples, so `row[1]` breaks the moment
someone adds a column.

```python
conn.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        id      INTEGER PRIMARY KEY,
        email   TEXT NOT NULL UNIQUE,
        name    TEXT NOT NULL,
        country TEXT NOT NULL DEFAULT 'US',
        created TEXT NOT NULL DEFAULT (datetime('now'))
    )
""")

conn.executemany(
    "INSERT OR IGNORE INTO customer (email, name) VALUES (?, ?)",
    [("ada@example.com", "Ada"), ("linus@example.com", "Linus")],
)
conn.commit()

row = conn.execute("SELECT id, name FROM customer WHERE email = ?", ("ada@example.com",)).fetchone()
print(row["id"], row["name"])
```

`executemany` is the difference between one round trip and a thousand. `INSERT OR IGNORE`
makes the load idempotent — run it twice and you still have two customers.

### Transactions

A transaction is "all of this or none of it". The connection is a context manager that commits on
success and rolls back on any exception:

```python
try:
    with conn:
        conn.execute("UPDATE customer SET name = ? WHERE id = ?", ("Ada L.", 1))
        conn.execute("INSERT INTO purchase (customer_id, amount_cents) VALUES (?, ?)", (1, 2500))
        conn.execute("INSERT INTO purchase (customer_id, amount_cents) VALUES (?, ?)", (999, 100))
except sqlite3.IntegrityError as exc:
    print("nothing was saved:", exc)
```

The third insert violates the foreign key, so the rename never happened either. Note that
`with conn:` does **not** close the connection — call `conn.close()` when you are done, or use
`contextlib.closing`.

:::pitfall Forgetting to commit
In Python's `sqlite3`, writes are invisible to other connections until you commit, and lost
entirely if the process dies first. Autocommit is not the default. Rely on `with conn:` for
anything multi-statement, call `conn.commit()` for one-offs, and never assume a write landed —
read it back in your test.
:::

## Never build SQL with string formatting

This is the most important security rule in the chapter.

```python
# BROKEN - and not just "theoretically" broken
def find_customer(conn, email: str):
    return conn.execute(f"SELECT * FROM customer WHERE email = '{email}'").fetchall()
```

Hand it a value from a web form and you get SQL injection:

```python
print(len(find_customer(conn, "' OR '1'='1")))   # every customer in the table
```

The database cannot tell the difference between your SQL and their data, because you pasted the
data into the SQL. Pass values separately and let the driver do the escaping:

```python
# CORRECT - the ? is a placeholder, the tuple is the data
def find_customer(conn, email: str):
    return conn.execute("SELECT * FROM customer WHERE email = ?", (email,)).fetchall()


print(len(find_customer(conn, "' OR '1'='1")))   # 0
```

Placeholders are not string interpolation: the driver sends the SQL and the values separately, so
injected quotes are just characters. They also handle `None`, dates, and quoting automatically.
Never use `%`, `.format()`, or f-strings to put a value into SQL. Identifiers (table and column
names) cannot be parameterised — validate those against an allow-list.

## Schema design that survives contact with reality

```sql
CREATE TABLE IF NOT EXISTS purchase (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customer(id) ON DELETE CASCADE,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    placed_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_purchase_customer ON purchase(customer_id);
```

The rules that pay off:

- **Primary key** on every table. In SQLite, `INTEGER PRIMARY KEY` is also the rowid — free and
  fast.
- **`NOT NULL`** everywhere you can. Optional fields become `None` in Python and every consumer
  has to handle them; be explicit about which ones really are optional.
- **Foreign keys** with `ON DELETE CASCADE` so deleting a customer cleans up their purchases.
- **Indexes** on columns you filter or join on. Check with `EXPLAIN QUERY PLAN SELECT ...` — if
  you see `SCAN` on a big table, you are missing one.
- **Money as integer cents**, never a float. `0.1 + 0.2` is not `0.3`.
- Never name a table `order`, `select`, or `group` — reserved words force quoting forever.

## JOINs and aggregates

A `JOIN` stitches tables together; `GROUP BY` collapses rows into summaries.

```sql
SELECT c.name,
       COUNT(p.id)                    AS purchases,
       COALESCE(SUM(p.amount_cents), 0) AS total_cents
FROM customer c
LEFT JOIN purchase p ON p.customer_id = c.id
GROUP BY c.id
ORDER BY total_cents DESC;
```

`LEFT JOIN` keeps customers with zero purchases — an inner `JOIN` would silently drop them, which
is a classic "why is my report missing people" bug. `COALESCE` turns the resulting `NULL` sum
into `0`.

```python
sql = """
SELECT c.name, COUNT(p.id) AS purchases, COALESCE(SUM(p.amount_cents), 0) AS total_cents
FROM customer c LEFT JOIN purchase p ON p.customer_id = c.id
GROUP BY c.id ORDER BY total_cents DESC
"""
for row in conn.execute(sql):
    print(f"{row['name']:<12}{row['purchases']:>3}  {row['total_cents'] / 100:>8.2f}")
```

## SQLAlchemy 2.x: tables as Python classes

Raw SQL is the right answer for analytics and one-off queries. For application code — objects you
create, modify, and save — an ORM (object-relational mapper) keeps you out of string-building and
gives you type-checked models.

```bash
python3 -m pip install "sqlalchemy>=2.0"
```

```python
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    purchases: Mapped[list[Purchase]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class Purchase(Base):
    __tablename__ = "purchase"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id", ondelete="CASCADE"))
    amount_cents: Mapped[int] = mapped_column()
    placed_on: Mapped[date | None] = mapped_column(Date, default=None)
    customer: Mapped[Customer] = relationship(back_populates="purchases")
```

`Mapped[int]` says "this column is an int and cannot be null"; `Mapped[date | None]` says it can.
Those annotations are not decoration — SQLAlchemy reads them to pick column types and nullability,
and your type checker reads them too (Chapter 16).

```python
engine = create_engine("sqlite:///shop.db", echo=False)
Base.metadata.create_all(engine)          # creates missing tables; never alters existing ones


def seed() -> None:
    with Session(engine) as session:
        ada = Customer(name="Ada", email="ada@example.com")
        ada.purchases = [Purchase(amount_cents=2500), Purchase(amount_cents=9900)]
        session.add(ada)
        session.commit()                  # INSERTs both rows, in one transaction


def rename(customer_id: int, new_name: str) -> None:
    with Session(engine) as session:
        customer = session.get(Customer, customer_id)
        if customer is None:
            raise LookupError(f"no customer {customer_id}")
        customer.name = new_name          # just assign; the session tracks the change
        session.commit()


def delete_small_purchases() -> int:
    with Session(engine) as session:
        doomed = session.scalars(select(Purchase).where(Purchase.amount_cents < 100)).all()
        for purchase in doomed:
            session.delete(purchase)
        session.commit()
        return len(doomed)
```

Query with `select()`, the 2.x style — do not use the legacy `session.query(Customer)` form:

```python
with Session(engine) as session:
    big = session.scalars(
        select(Customer).join(Customer.purchases).where(Purchase.amount_cents > 5000)
    ).unique().all()

    totals = session.execute(
        select(Customer.name, func.sum(Purchase.amount_cents).label("total"))
        .join(Customer.purchases)
        .group_by(Customer.id)
        .order_by(func.sum(Purchase.amount_cents).desc())
    ).all()

for name, total in totals:
    print(f"{name:<12}{(total or 0) / 100:>8.2f}")
```

`session.scalars()` returns model objects (use it when selecting whole entities);
`session.execute()` returns rows (use it for columns and aggregates). The `.unique()` after a
joined eager load is required in 2.x — joined eager loading against a collection returns the same
parent once per child row.

## The N+1 problem

Relationships are lazy by default, so touching `customer.purchases` issues a fresh `SELECT`. In a
loop, that is one query for the list plus one per customer: N+1.

```python
# BAD: 1 query for customers + 1 per customer
with Session(engine) as session:
    for customer in session.scalars(select(Customer)):
        print(customer.name, sum(p.amount_cents for p in customer.purchases))

# GOOD: exactly 2 queries
with Session(engine) as session:
    stmt = select(Customer).options(selectinload(Customer.purchases))
    for customer in session.scalars(stmt):
        print(customer.name, sum(p.amount_cents for p in customer.purchases))
```

`selectinload` loads the whole collection for every parent in a second query using `IN (...)`.
Use `joinedload` when you want a single `JOIN` instead (better for one-to-one or small sets). Run
with `echo=True` on the engine to see the difference for yourself:

```text
-- BAD, 200 customers
SELECT customer.id, customer.email, customer.name FROM customer
SELECT purchase.id, ... FROM purchase WHERE purchase.customer_id = ?   -- x200
```

:::pitfall The N+1 query problem
Ten customers is fine. Ten thousand is a minute-long page load and a database on its knees, and
it happens invisibly — the code looks identical either way. Turn on `echo=True` in development,
or use `selectinload`/`joinedload` by default whenever you *know* you will touch a relationship in
a loop. This bites hardest in web templates, which is why Chapter 27 revisits it.
:::

## Transactions and rollback

The session is a transaction. Flush to send SQL without committing; commit to make it permanent;
rollback to throw it away.

```python
from sqlalchemy.exc import IntegrityError

with Session(engine) as session:
    session.add(Customer(name="Grace", email="ada@example.com"))   # duplicate email!
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print("duplicate email - nothing saved")
```

`get` after commit, or `session.refresh(obj)`, if you need generated values. And keep sessions
short-lived: one per request or per unit of work, never a global session shared between threads —
`Session` is not thread-safe, `engine` is.

## Migrations with Alembic

`create_all()` creates tables once. It will not add a column to a table that already exists, and
production data cannot be dropped and recreated. That is what migrations are for. Alembic is the
standard tool: it versions your schema and applies changes in order.

```bash
python3 -m pip install alembic
alembic init migrations
```

Point it at your models by editing the generated `migrations/env.py`:

```python
from models import Base          # the module with your DeclarativeBase subclass
target_metadata = Base.metadata
```

Set the URL in `alembic.ini` (`sqlalchemy.url = sqlite:///shop.db`) or, better, read it from the
environment inside `env.py`. Then the two commands you use constantly:

```bash
alembic revision --autogenerate -m "add placed_on to purchase"
alembic upgrade head
```

`--autogenerate` diffs your models against the live database and writes the migration; **read
what it generated** — it cannot detect every change (renames, in particular, look like a drop
plus an add, which destroys data). `upgrade head` applies everything pending. Also worth knowing:
`alembic downgrade -1` steps back, `alembic current` shows where you are, `alembic history` lists
revisions. Commit the `migrations/versions/` directory with your code.

## Choosing the right storage

| Need | Use | Why |
| --- | --- | --- |
| Config, a few hundred records | JSON file | Human-readable, zero setup |
| Data interchange with non-programmers | CSV | Universal, but no types or constraints |
| Structured app data, single process | SQLite + `sqlite3` | No server, real SQL, real constraints |
| App data accessed as objects | SQLite/Postgres + SQLAlchemy | Models, relationships, migrations |
| Many concurrent writers, or a real server | PostgreSQL | Row-level locking, roles, extensions |

The pipeline in practice: receive CSV, normalise it, load it into SQLite, query it with SQL or the
ORM. Everything above is one tool in that chain.

:::scenario Two teams send you the same data in different shapes and the monthly total is wrong
Every month you merge two CSVs. March's total came out 18% high. One file uses `Total (USD)`,
the other `total_usd`; one has a trailing summary row; and a customer appears twice because their
email was re-sent after an edit. Nobody can tell you which rows are real.
:::

:::solution Normalise at the edge, then let the database enforce the rules
Do not reconcile the columns in your head — normalise headers to one canonical set on the way in,
skip rows that are not data, and give the database a `UNIQUE` constraint so duplicates are
impossible rather than merely unlikely.

```python
def load_month(conn, path: Path) -> tuple[int, int]:
    """Load one CSV. Returns (rows inserted, rows skipped)."""
    inserted = skipped = 0
    for raw in csv.DictReader(path.open(newline="", encoding="utf-8-sig")):
        row = normalise(raw)
        try:
            amount = int(float(row["total_usd"]) * 100)
        except (KeyError, ValueError):
            skipped += 1                       # summary rows, blanks, typos
            continue
        with conn:
            conn.execute(
                "INSERT INTO purchase (customer_id, amount_cents, external_id) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT(external_id) DO UPDATE SET amount_cents = excluded.amount_cents",
                (customer_id_for(conn, row["email"]), amount, row["order_id"]),
            )
        inserted += 1
    return inserted, skipped
```

Three things fix the class of bug, not just this instance. Normalising headers means a renamed
column is a one-line mapping change. Skipping unparseable rows *loudly* — log them, count them,
report the count — means a bad export shows up as "skipped 3 rows", not as a silent 18% error.
And `ON CONFLICT ... DO UPDATE` (an upsert) makes the load idempotent: re-running March gives the
same answer, because `external_id` is unique and the last write wins deliberately rather than
accidentally.

Finally, once the data is in SQL, answer the question there:
`SELECT SUM(amount_cents)/100.0 FROM purchase WHERE placed_at LIKE '2026-03%'`. If that disagrees
with the spreadsheet, you can now diff row by row instead of guessing.
:::

## Key takeaways

- `csv.DictReader`/`DictWriter` need `newline=""`, and files from Excel need `encoding="utf-8-sig"`.
- Normalise messy headers once, at the edge, before any other code sees the data.
- SQLite needs `PRAGMA foreign_keys = ON` per connection, and `row_factory = sqlite3.Row` for
  dict-like rows.
- Never interpolate values into SQL — pass them as parameters; placeholders make injection
  impossible and quoting automatic.
- Every table gets a primary key, `NOT NULL` where possible, foreign keys, and indexes on
  filtered or joined columns; store money as integer cents.
- `LEFT JOIN` keeps rows with no match; `COALESCE` turns their `NULL` aggregates into zero.
- SQLAlchemy 2.x uses `Mapped`/`mapped_column` models, `Session`, and `select()`; use
  `selectinload` whenever you touch a relationship inside a loop.
- `create_all()` creates tables; Alembic evolves them.

## Practice

- [ ] Write `count_rows(path)` that returns the number of data rows in a CSV using `DictReader`
      (not counting the header).
- [ ] Write `normalise_header(name)` that turns `"  Total (USD) "` into `"total_usd"`, and use it
      to rewrite a CSV's headers into a clean copy.
- [ ] Create the `customer` and `purchase` tables above in a scratch database, insert 100 rows
      with `executemany`, and time it against 100 individual `execute()` calls.
- [ ] Take a broken `find_customer` that uses an f-string and prove the injection with the input
      `"' OR '1'='1"`, then fix it with a placeholder.
- [ ] Write one SQL query that lists each customer's name, purchase count, and total in dollars,
      including customers who bought nothing, ordered by total descending.
- [ ] Define `Customer`/`Purchase` models in SQLAlchemy, insert three customers with purchases,
      and print the same report twice — once triggering N+1, once with `selectinload` — with
      `echo=True` so you can count the queries.

## Solutions

:::solution Exercise 1
```python
import csv
from pathlib import Path


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return sum(1 for _ in csv.DictReader(handle))


print(count_rows(Path("sales.csv")))
```
`DictReader` skips the header itself, and the generator inside `sum` avoids building a list you
are going to throw away — the same laziness you saw with generators in Chapter 14.
:::

:::solution Exercise 2
```python
import csv
import re
from pathlib import Path


def normalise_header(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug


with Path("sales.csv").open(newline="", encoding="utf-8-sig") as src:
    reader = csv.DictReader(src)
    rows = [{normalise_header(k): v for k, v in row.items()} for row in reader]

with Path("clean.csv").open("w", newline="", encoding="utf-8") as dst:
    writer = csv.DictWriter(dst, fieldnames=list(rows[0]), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
```
A regex beats a chain of `.replace()` because it collapses punctuation, spaces, and repeated
underscores in one pass — `"Total (USD)"` and `"total/USD"` both become `total_usd`.
:::

:::solution Exercise 3
```python
import sqlite3
import time
from pathlib import Path

conn = sqlite3.connect(Path(":memory:"))
conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, n INTEGER, label TEXT)")
rows = [(i, i * 2, f"row-{i}") for i in range(100)]

start = time.perf_counter()
conn.executemany("INSERT INTO t (id, n, label) VALUES (?, ?, ?)", rows)
print("executemany:", time.perf_counter() - start)
```
`executemany` parses the statement once and reuses the plan for every row, which is why it is
roughly an order of magnitude faster than looping over `execute()`. With `:memory:` the database
is discarded when the connection closes — ideal for tests.
:::

:::solution Exercise 4
```python
def find_customer_broken(conn, email: str):
    return conn.execute(f"SELECT * FROM customer WHERE email = '{email}'").fetchall()


def find_customer_fixed(conn, email: str):
    return conn.execute("SELECT * FROM customer WHERE email = ?", (email,)).fetchall()


evil = "' OR '1'='1"
print(len(find_customer_broken(conn, evil)))   # every row - the quote closed the string
print(len(find_customer_fixed(conn, evil)))    # 0 - the value is data, never SQL
```
The fixed version cannot be injected even in principle: the statement reaches the database as
text with a `?`, and the value travels separately, so no amount of quoting can change the SQL's
structure.
:::

:::solution Exercise 5
```sql
SELECT c.name,
       COUNT(p.id)                       AS purchases,
       COALESCE(SUM(p.amount_cents), 0) / 100.0 AS total_dollars
FROM customer c
LEFT JOIN purchase p ON p.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY total_dollars DESC;
```
`LEFT JOIN` plus `COALESCE` is what keeps zero-purchase customers in the report at `$0.00`.
Grouping by `c.id` (the primary key) is sufficient and unambiguous; adding `c.name` keeps
strict-mode databases happy.
:::

:::solution Exercise 6
```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, selectinload

engine = create_engine("sqlite:///scratch.db", echo=True)
Base.metadata.create_all(engine)

with Session(engine) as session:
    for name, email, amounts in [
        ("Ada", "ada@example.com", [2500, 9900]),
        ("Linus", "linus@example.com", [1500]),
        ("Grace", "grace@example.com", [100, 200]),
    ]:
        session.add(Customer(name=name, email=email,
                             purchases=[Purchase(amount_cents=a) for a in amounts]))
    session.commit()

with Session(engine) as session:                       # 1 + N queries
    for c in session.scalars(select(Customer)):
        print(c.name, sum(p.amount_cents for p in c.purchases))

with Session(engine) as session:                       # 2 queries
    stmt = select(Customer).options(selectinload(Customer.purchases))
    for c in session.scalars(stmt):
        print(c.name, sum(p.amount_cents for p in c.purchases))
```
In the `echo=True` output the first loop emits one `SELECT purchase ... WHERE customer_id = ?` per
customer; the second emits exactly one extra query with `IN (1, 2, 3)`. Same results, N fewer
round trips — and the difference grows linearly with your data.
:::
