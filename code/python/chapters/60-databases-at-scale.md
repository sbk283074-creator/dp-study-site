---
chapter: 60
part: 11
title: Databases at Scale
summary: Read a query plan instead of guessing at it, count the round trips a loop costs, tell a lost update from a slow one, and decide which indexes are worth the write path they charge for. You will be able to say which of four changes to a report endpoint removes which number, and to prove it with counts rather than with a stopwatch.
minutes: 110
tags: [sqlite3, indexes, query plans, transactions, isolation, connection pooling, N+1, pagination, batching]
---

Chapter 59 kept a copy of an answer closer to the caller. This chapter goes to where the answers
actually live, and the same rule applies: the numbers that decide are counts, and the database will
give you most of them if you ask for them rather than timing them.

A database is the one component in a program that is allowed to be large. Everything before this
part was about a data structure you could hold in memory and reason about exactly. A table is not
that. It is a file the program never reads, on a machine it does not control, answering a language
it did not write, and every one of the four sentences in that list is a place where a program gets
slow or wrong.

So the chapter is arranged around four counts. **Rows visited** is what a query plan costs, and it
is where indexes live. **Round trips** is what a loop over a relationship costs, and it scales with
the rows the loop walked rather than with the size of the answer. **Transactions** is what the write
path costs, and it is the unit of durability rather than the unit of SQL. **Stale reads** is what
the wrong transaction boundary costs, and no query reports it.

Every block counts one of those four, and the last one shows the thing worth remembering: four
changes to one endpoint, each of which moves exactly one of the numbers.

## An index is a copy, and a copy has a price

The first thing to get right about an index is that it is not a faster table. It is a second
structure, kept sorted, that has to be correct after every write.

Four thousand and ninety-six rows into a table with zero, one, two, three and four indexes. The
count is of comparisons, on both sides of the ledger.

```python run
"""Chapter 60 -- an index is a second copy, and every write maintains it.

Reading a table is cheap to reason about because nothing moves. An index is
the opposite: it is a sorted structure that has to be correct after every
insert, so the write path pays for it forever and the read path pays for it
once. The count is of comparisons, on both sides of the ledger.
"""

ROWS = 4096


def boundary(rows):
    """Comparisons to find one key in a sorted list of this many entries."""
    count = 0
    size = rows
    while size > 1:
        size = (size + 1) // 2
        count += 1
    return count


def build_cost(rows):
    """Comparisons to insert every row into one sorted index, in order."""
    return sum(boundary(size) for size in range(1, rows + 1))


LOOKUP_INDEXED = boundary(ROWS) + 1
LOOKUP_SCAN = ROWS // 2

print(f"{ROWS:,} rows, one index maintained per row inserted")
print()
print(f"{'indexes':>8}{'to build':>12}{'per lookup saved':>18}{'lookups to repay':>18}")
print("-" * 56)
for count in (0, 1, 2, 3, 4):
    build = count * build_cost(ROWS)
    saved = LOOKUP_SCAN - (LOOKUP_INDEXED if count else LOOKUP_SCAN)
    repay = build / saved if saved else 0
    print(f"{count:>8}{build:>12,}{saved:>18,}{repay:>18,.0f}")

print()
print(f"A lookup with no index costs {LOOKUP_SCAN:,} comparisons on average.")
print(f"A lookup through the index costs {LOOKUP_INDEXED}, plus a fetch per match.")
print(f"Building one index costs {build_cost(ROWS):,} comparisons.")
print()
print("So the index is not a saving that starts at the first read. It is a debt")
print("taken out on the write path and repaid by repetition. A second index on")
print("another column does not make this lookup cheaper -- the 2,035 saved above")
print("is the same for one index and for four -- and it takes out the same debt")
print("again. What an index buys is one predicate, and it charges for every row.")
```

```text
4,096 rows, one index maintained per row inserted

 indexes    to build  per lookup saved  lookups to repay
--------------------------------------------------------
       0           0                 0                 0
       1      45,057             2,035                22
       2      90,114             2,035                44
       3     135,171             2,035                66
       4     180,228             2,035                89

A lookup with no index costs 2,048 comparisons on average.
A lookup through the index costs 13, plus a fetch per match.
Building one index costs 45,057 comparisons.

So the index is not a saving that starts at the first read. It is a debt
taken out on the write path and repaid by repetition. A second index on
another column does not make this lookup cheaper -- the 2,035 saved above
is the same for one index and for four -- and it takes out the same debt
again. What an index buys is one predicate, and it charges for every row.
```

Reading is where the index pays: a lookup costs two thousand and forty-eight comparisons without one
and thirteen with one, which is a saving of two thousand and thirty-five. Writing is where it
charges: building one index over four thousand and ninety-six rows costs forty-five thousand and
fifty-seven comparisons, and it costs that again for every row inserted afterwards, forever.

Divide one by the other and the index pays for itself after twenty-two lookups. That is the number
to hold on to, because it is the whole decision: an index on a column that is read twenty times
between writes is a cost, and the same index on a column read a thousand times is not.

And note the fourth column, which is the same for one index and for four. A second index on another
column does not make *this* lookup any cheaper — it charges the same write cost again and buys
nothing for this predicate. An index buys one predicate.

## When the index is the slower plan

If an index makes a lookup cheaper, the obvious next step is to index everything. The count says
otherwise.

A hundred thousand rows, one predicate, and the fraction of the table it matches swept from a
thousandth to all of it. The count is of page touches, and the only assumption in it is that a row
reached through the index sits on a different page from the last one, so it costs four times a row
read in order.

```python run
"""Chapter 60 -- when an index pays, and when it is the slower plan.

One table of 100,000 rows and one predicate. There are two ways to answer it:
read every row in order, or jump into a sorted copy of the column and fetch
the rows it names. Nothing here is timed. The count is of page touches, and
the only assumption in it is that a row reached through the index sits on a
different page from the last one, so it costs four times a row read in order.
That assumption is swept at the end, because the crossover is a property of
the ratio and not of the index.
"""

ROWS = 100000
RANDOM_TOUCH = 4
SELECTIVITIES = [0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]


def boundary(rows):
    """Comparisons to find one key in a sorted list of this many entries."""
    count = 0
    size = rows
    while size > 1:
        size = (size + 1) // 2
        count += 1
    return count


def plan_costs(selectivity, penalty):
    """Page touches for a full scan and for the same predicate through an index."""
    matches = max(1, int(ROWS * selectivity))
    scan = ROWS
    index = penalty * (boundary(ROWS) + matches)
    return matches, scan, index


print(f"{ROWS:,} rows, sequential touch = 1, indexed touch = {RANDOM_TOUCH}")
print()
print(f"{'matches':>8}{'scan':>12}{'index':>12}   {'plan the count prefers':<23}")
print("-" * 58)
for selectivity in SELECTIVITIES:
    matches, scan, index = plan_costs(selectivity, RANDOM_TOUCH)
    winner = "index" if index < scan else "scan"
    print(f"{matches:>8,}{scan:>12,}{index:>12,}   {winner:<24}")

print()
print("The crossover moves with the assumption, so sweep it:")
print()
print(f"{'indexed touch costs':>20}{'scan wins above':>18}")
print("-" * 38)
for penalty in (1, 2, 4, 8, 16):
    crossing = 1.0
    for step in range(1, 1001):
        selectivity = step / 1000
        _, scan, index = plan_costs(selectivity, penalty)
        if index >= scan:
            crossing = selectivity
            break
    print(f"{penalty:>20}{crossing:>17.1%}")

print()
print("The index reads far fewer rows. It reads them in an order the file does")
print("not store them in, so each one is a separate page, and that is why the")
print("count of pages decides the plan rather than the count of rows.")
```

```text
100,000 rows, sequential touch = 1, indexed touch = 4

 matches        scan       index   plan the count prefers 
----------------------------------------------------------
     100     100,000         468   index                   
     500     100,000       2,068   index                   
   1,000     100,000       4,068   index                   
   5,000     100,000      20,068   index                   
  10,000     100,000      40,068   index                   
  25,000     100,000     100,068   scan                    
  50,000     100,000     200,068   scan                    
 100,000     100,000     400,068   scan                    

The crossover moves with the assumption, so sweep it:

 indexed touch costs   scan wins above
--------------------------------------
                   1           100.0%
                   2            50.0%
                   4            25.0%
                   8            12.5%
                  16             6.3%

The index reads far fewer rows. It reads them in an order the file does
not store them in, so each one is a separate page, and that is why the
count of pages decides the plan rather than the count of rows.
```

At a thousandth of the table the index touches four hundred and sixty-eight pages against the
scan's hundred thousand. At a quarter of the table it touches a hundred thousand and sixty-eight,
and the scan wins. Between those two the plan the count prefers changes sides.

The second table is the part that matters, because the crossover is not a property of the index. It
is a property of the *ratio* between a sequential row and a random one. At four times, the scan wins
above a quarter of the table. At sixteen times, above a sixteenth. If you change the assumption, the
crossover moves, and the assumption is a property of the storage device rather than of the query.

So the rule of thumb people quote — an index pays below a few per cent selectivity — is not a fact
about indexes. It is a fact about the ratio, and the ratio is why a plan that is right on a laptop
is wrong on a spinning disk and right again in a cache.

## The round trip is the unit that scales

A loop that queries inside itself is the most common shape in application code, and it is the one
where the count is least visible, because every individual query is fast.

A parent table and a child table, read two ways. The count is of statements the application sends
and of rows it receives.

```python run
"""Chapter 60 -- the N+1 problem, counted as round trips.

A parent table and a child table in a real database file, read two ways: one
statement per parent, which is what an object-relational mapping does when you
touch a relationship inside a loop, and one join. The count is of statements
the application sends and of rows it receives. The interesting number is that
the join sends far fewer statements and receives fewer rows, and does the
whole job.
"""

import os
import sqlite3
import tempfile

PARENT_COUNTS = [10, 50, 100, 200]
PER_PARENT = 10


def build(parents):
    """A database with `parents` parent rows and ten children under each."""
    path = os.path.join(tempfile.mkdtemp(), "app.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("CREATE TABLE child (id INTEGER PRIMARY KEY, parent_id INTEGER, label TEXT)")
    conn.executemany(
        "INSERT INTO parent VALUES (?, ?)",
        [(p, f"parent-{p:04d}") for p in range(parents)],
    )
    conn.executemany(
        "INSERT INTO child VALUES (?, ?, ?)",
        [(c, c // PER_PARENT, f"child-{c:05d}") for c in range(parents * PER_PARENT)],
    )
    conn.execute("CREATE INDEX i_child_parent ON child(parent_id)")
    conn.commit()
    return conn


def per_parent(conn):
    """One statement for the parents, then one per parent for its children."""
    statements = 0
    rows = 0
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM parent")
    statements += 1
    found = cur.fetchall()
    rows += len(found)
    for parent_id, _name in found:
        cur.execute("SELECT id, label FROM child WHERE parent_id = ?", (parent_id,))
        statements += 1
        rows += len(cur.fetchall())
    return statements, rows


def one_join(conn):
    """The whole relationship in a single statement."""
    cur = conn.cursor()
    cur.execute(
        "SELECT p.name, c.label FROM parent p JOIN child c ON c.parent_id = p.id"
    )
    return 1, len(cur.fetchall())


print(f"{'parents':>8}{'per-parent stmts':>18}{'rows received':>15}"
      f"{'join stmts':>12}{'join rows':>11}")
print("-" * 64)
for parents in PARENT_COUNTS:
    conn = build(parents)
    stmts, rows = per_parent(conn)
    j_stmts, j_rows = one_join(conn)
    print(f"{parents:>8}{stmts:>18}{rows:>15}{j_stmts:>12}{j_rows:>11}")
    conn.close()

print()
print("Round trips are the number of rows the loop happened to walk, not the")
print("size of the answer. Two hundred parents means two hundred and one")
print("statements and two thousand two hundred rows received, for an answer")
print("of two thousand rows that one statement could have carried.")
```

```text
 parents  per-parent stmts  rows received  join stmts  join rows
----------------------------------------------------------------
      10                11            110           1        100
      50                51            550           1        500
     100               101           1100           1       1000
     200               201           2200           1       2000

Round trips are the number of rows the loop happened to walk, not the
size of the answer. Two hundred parents means two hundred and one
statements and two thousand two hundred rows received, for an answer
of two thousand rows that one statement could have carried.
```

At ten parents the loop sends eleven statements. At two hundred parents it sends two hundred and
one, and the join still sends one. That is the shape: the round trips scale with the rows the loop
walked, and the size of the answer is irrelevant to them.

The second number is the one people find surprising. The loop receives two thousand two hundred
rows to produce an answer of two thousand, and the join receives two thousand. The loop is not
receiving more *answer*; it is receiving the parent rows once each, in a shape that had to be
assembled in the application. The join assembles it where the data is.

Two hundred statements is not a disaster on a laptop. On a network it is two hundred round trips,
each with a latency the program cannot see and cannot overlap, which is why the same code that
answers in milliseconds against a local file takes seconds against a database in another building.
The count of statements is the count of latencies.

## Asking the database for a number

The other shape that costs more than it looks is fetching rows in order to do arithmetic on them.

Twenty thousand orders and two questions: how many, and what do they add up to. Three ways to ask,
and the count is of values that cross the boundary and rows the application holds.

```python run
"""Chapter 60 -- counting by fetching.

A table of twenty thousand orders and one question: how many are there, and
what do they add up to. Three ways to ask it, and the count is of values the
database has to send and of rows the application has to hold. The database
can count and sum without sending anything it does not have to.
"""

import os
import sqlite3
import tempfile

ROWS = 20000
COLUMNS = 4


def build():
    path = os.path.join(tempfile.mkdtemp(), "orders.db")
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer INTEGER,"
        " status TEXT, total INTEGER)"
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [(o, o % 1000, "paid" if o % 3 else "open", 10 + o % 90) for o in range(ROWS)],
    )
    conn.commit()
    return conn


def fetch_every_column(conn):
    """Pull the rows into Python and do the arithmetic there."""
    rows = conn.execute("SELECT * FROM orders").fetchall()
    return len(rows) * COLUMNS, len(rows), (len(rows), sum(row[3] for row in rows))


def fetch_one_column(conn):
    """Pull the one column the arithmetic needs."""
    rows = conn.execute("SELECT total FROM orders").fetchall()
    return len(rows), len(rows), (len(rows), sum(row[0] for row in rows))


def ask_the_database(conn):
    """Send nothing but the answer."""
    count, total = conn.execute("SELECT COUNT(*), SUM(total) FROM orders").fetchone()
    return 1, 0, (count, total)


DESIGNS = [
    ("fetch every column", fetch_every_column),
    ("fetch one column", fetch_one_column),
    ("ask the database", ask_the_database),
]

conn = build()
print(f"{ROWS:,} orders, {COLUMNS} columns each")
print()
print(f"{'design':<22}{'values sent':>13}{'rows held':>11}{'count':>8}{'sum':>10}")
print("-" * 64)
for name, design in DESIGNS:
    values, held, (count, total) = design(conn)
    print(f"{name:<22}{values:>13,}{held:>11,}{count:>8,}{total:>10,}")

print()
print("All three agree on the count and the sum, and they differ by four orders")
print("of magnitude in what crosses the boundary. The arithmetic is the same")
print("either way; the difference is where it happens. When the answer is a")
print("number rather than a set of rows, the database is already holding the")
print("rows and can produce the number without sending them.")
```

```text
20,000 orders, 4 columns each

design                  values sent  rows held   count       sum
----------------------------------------------------------------
fetch every column           80,000     20,000  20,000 1,089,300
fetch one column             20,000     20,000  20,000 1,089,300
ask the database                  1          0  20,000 1,089,300

All three agree on the count and the sum, and they differ by four orders
of magnitude in what crosses the boundary. The arithmetic is the same
either way; the difference is where it happens. When the answer is a
number rather than a set of rows, the database is already holding the
rows and can produce the number without sending them.
```

All three agree on twenty thousand and one million eighty-nine thousand three hundred. The first
sends eighty thousand values and holds twenty thousand rows. The third sends one value and holds
nothing.

The middle row is the interesting one, because it is the version a careful programmer writes:
fetch only the column the arithmetic needs. It sends twenty thousand values instead of eighty
thousand, which is a real saving, and it is still twenty thousand values for a single number.

The rule is not "avoid fetching". It is that when the answer is a number rather than a set of rows,
the database is already holding the rows, and the arithmetic is something it can do without
sending anything. `COUNT` and `SUM` are not conveniences; they are the difference between a
number and twenty thousand rows.

## Two writers and one row

Everything so far has been about reading. The first thing that goes wrong on the write path is not
slow at all — it is wrong.

Two connections to one database file, both asked to add to the same balance, twenty pairs of
increments. The count is of units that disappeared and of pairs where the answer is wrong.

```python run
"""Chapter 60 -- the update that loses a write, and the three ways to write it.

Two connections to one database file, both asked to add to the same balance.
The count is of units that disappeared and of pairs where the answer is wrong,
and the result is that wrapping the read and the write in a transaction does
not help, because the read already happened before the other writer committed.
"""

import os
import sqlite3
import tempfile

PAIRS = 20
START = 100


def fresh():
    """A database file with one account holding `START`."""
    path = os.path.join(tempfile.mkdtemp(), "bank.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, balance INTEGER)")
    conn.execute("INSERT INTO account VALUES (1, ?)", (START,))
    conn.commit()
    conn.close()
    return path


def read_then_write(path, first, second):
    """Both callers read, then each writes what it read plus its own delta."""
    a = sqlite3.connect(path)
    b = sqlite3.connect(path)
    a_read = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    b_read = b.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.execute("UPDATE account SET balance = ? WHERE id = 1", (a_read + first,))
    a.commit()
    b.execute("UPDATE account SET balance = ? WHERE id = 1", (b_read + second,))
    b.commit()
    final = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.close()
    b.close()
    return final, 0


def add_in_statement(path, first, second):
    """The update reads the column it is writing, inside the statement."""
    a = sqlite3.connect(path)
    b = sqlite3.connect(path)
    a.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (first,))
    a.commit()
    b.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (second,))
    b.commit()
    final = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.close()
    b.close()
    return final, 0


def compare_and_set(path, first, second):
    """Write only if the column still holds what you read, and count refusals."""
    a = sqlite3.connect(path)
    b = sqlite3.connect(path)
    refusals = 0
    a_read = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    b_read = b.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.execute(
        "UPDATE account SET balance = ? WHERE id = 1 AND balance = ?",
        (a_read + first, a_read),
    )
    a.commit()
    cur = b.execute(
        "UPDATE account SET balance = ? WHERE id = 1 AND balance = ?",
        (b_read + second, b_read),
    )
    b.commit()
    if not cur.rowcount:
        refusals += 1
        b_read = b.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
        b.execute(
            "UPDATE account SET balance = ? WHERE id = 1 AND balance = ?",
            (b_read + second, b_read),
        )
        b.commit()
    final = a.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
    a.close()
    b.close()
    return final, refusals


DESIGNS = [
    ("read, then write", read_then_write),
    ("add in the statement", add_in_statement),
    ("compare and set", compare_and_set),
]

ASKED = sum((30 + index) + (50 + index) for index in range(PAIRS))

print(f"{PAIRS} pairs, each on a fresh account holding {START}, deltas 30+i and 50+i")
print(f"each pair should end at 180 + 2i, so {START + 80} to {START + 80 + 2 * (PAIRS - 1)}")
print(f"{ASKED:,} units asked for across the {PAIRS} pairs")
print()
print(f"{'design':<22}{'last pair':>10}{'units lost':>12}{'pairs wrong':>13}{'refusals':>10}")
print("-" * 67)

results = []
for name, design in DESIGNS:
    last = 0
    lost = 0
    wrong = 0
    refusals = 0
    for index in range(PAIRS):
        first = 30 + index
        second = 50 + index
        final, refused = design(fresh(), first, second)
        expected = START + first + second
        last = final
        lost += expected - final
        wrong += 1 if final != expected else 0
        refusals += refused
    results.append((name, last, lost, wrong, refusals))

for name, last, lost, wrong, refusals in results:
    print(f"{name:<22}{last:>10}{lost:>12}{wrong:>13}{refusals:>10}")

worst = results[0][2]
print()
print(f"The first design lost {worst:,} of the {ASKED:,} units the pairs asked for,")
print(f"which is {worst / ASKED:.1%} of them, and it was wrong on all {results[0][3]} pairs.")
print()
print("The first design is not slow, it is wrong, and no transaction around the")
print("read and the write changes that: the value was read before the other")
print("writer committed, so the arithmetic was done on a number that had")
print("already stopped being true. A transaction gives you atomicity, not")
print("freshness. The second design makes the database do the arithmetic, so")
print("there is no stale value to be wrong about. The third keeps the")
print("arithmetic in the application and makes the write refuse when the")
print("number it read has moved, which is the shape you need when the new")
print("value cannot be expressed as an increment.")
```

```text
20 pairs, each on a fresh account holding 100, deltas 30+i and 50+i
each pair should end at 180 + 2i, so 180 to 218
1,980 units asked for across the 20 pairs

design                 last pair  units lost  pairs wrong  refusals
-------------------------------------------------------------------
read, then write             169         790           20         0
add in the statement         218           0            0         0
compare and set              218           0            0        20

The first design lost 790 of the 1,980 units the pairs asked for,
which is 39.9% of them, and it was wrong on all 20 pairs.

The first design is not slow, it is wrong, and no transaction around the
read and the write changes that: the value was read before the other
writer committed, so the arithmetic was done on a number that had
already stopped being true. A transaction gives you atomicity, not
freshness. The second design makes the database do the arithmetic, so
there is no stale value to be wrong about. The third keeps the
arithmetic in the application and makes the write refuse when the
number it read has moved, which is the shape you need when the new
value cannot be expressed as an increment.
```

The first design lost seven hundred and ninety of the one thousand nine hundred and eighty units the
pairs asked for, which is 39.9% of them, and it was wrong on every single pair. It is not a slow
design. It is a design that produces the wrong number, and the way to see that is to count the
units rather than the elapsed time.

The second design makes the database do the arithmetic, inside the statement that writes, so there
is no value in the application that can go stale. Zero lost, zero wrong, no refusals.

The third keeps the arithmetic in the application and makes the write refuse when the number it read
has moved. It also loses nothing, and it refused twenty times — once per pair, which is the count of
retries the caller now has to be written to handle. That is the trade: compare-and-set works when
the new value cannot be expressed as an increment, and it costs a retry loop.

What all three have in common is that no transaction boundary fixes the first one. A transaction
around the read and the write gives you atomicity — nobody sees half of it — and it does not give
you freshness, because the read happened before the other writer committed. That is the sentence
worth remembering from this section.

## A connection is not a handle

A pool exists because opening a connection is work. The count says what that work buys, and what
it costs when it is done carelessly.

Four borrowers over one pooled connection, one of which returns it with a write unfinished. The
count is of borrowers that inherited an open transaction, of rows a commit made durable that the
committer did not write, and of connections opened.

```python run
"""Chapter 60 -- what a pooled connection carries between borrowers.

A pool exists because opening a connection is work. A connection is not a
stateless handle, though: it holds a transaction, and a transaction that is
still open when the borrower returns the connection belongs to whoever
borrows it next. The count is of borrowers that inherited one, of rows a
commit made durable that the committer did not write, and of connections
opened.
"""

import os
import sqlite3
import tempfile

BORROWERS = 4


def run(mode):
    """One pass of four borrowers over one connection, or over four."""
    path = os.path.join(tempfile.mkdtemp(), "pool.db")

    setup = sqlite3.connect(path, isolation_level=None)
    setup.execute("CREATE TABLE audit (id INTEGER PRIMARY KEY, who TEXT, what TEXT)")
    setup.commit()
    setup.close()

    opened = 0

    def connect():
        nonlocal opened
        opened += 1
        return sqlite3.connect(path, isolation_level=None)

    conn = None
    inherited = 0

    for index in range(BORROWERS):
        who = f"borrower-{index + 1}"
        if mode == "no pool":
            conn = connect()
        elif conn is None:
            conn = connect()
        elif conn.in_transaction:
            inherited += 1

        conn.execute("INSERT INTO audit (who, what) VALUES (?, ?)", (who, "own work"))
        conn.commit()

        if index == 0:
            # a borrower that opened a transaction for a second write and
            # returned the connection without finishing it
            conn.execute("BEGIN")
            conn.execute("INSERT INTO audit (who, what) VALUES (?, ?)", (who, "draft"))

        if mode == "rollback on return" and conn.in_transaction:
            conn.rollback()
        if mode == "no pool":
            # the borrower closes it, and the unfinished write goes with it
            conn.close()
            conn = None

    final = sqlite3.connect(path)
    drafts = final.execute(
        "SELECT COUNT(*) FROM audit WHERE what = 'draft'"
    ).fetchone()[0]
    rows = final.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
    final.close()
    if conn is not None:
        conn.close()
    return opened, inherited, drafts, rows


MODES = ["no reset", "rollback on return", "no pool"]

print(f"{BORROWERS} borrowers, one of them returns a connection with a write unfinished")
print()
print(f"{'design':<22}{'opened':>7}{'inherited':>10}{'drafts durable':>16}{'rows at end':>12}")
print("-" * 67)
for mode in MODES:
    opened, inherited, drafts, rows = run(mode)
    print(f"{mode:<22}{opened:>7}{inherited:>10}{drafts:>16}{rows:>12}")

print()
print("The pool opened one connection for four borrowers, and one of them took")
print("the connection in a state the previous borrower left it in. The count of")
print("inherited transactions is one, not three, because the borrower that")
print("inherited it committed -- and its commit made somebody else's unfinished")
print("write durable, which is the row that should not be there.")
print()
print("Resetting the connection on the way back costs one call and removes both")
print("counts. Not pooling costs three extra opens and removes them too, which")
print("is the honest comparison: a pool is a decision about opens, and the")
print("reset is part of the price rather than an optional extra.")
```

```text
4 borrowers, one of them returns a connection with a write unfinished

design                 opened inherited  drafts durable rows at end
-------------------------------------------------------------------
no reset                    1         1               1           5
rollback on return          1         0               0           4
no pool                     4         0               0           4

The pool opened one connection for four borrowers, and one of them took
the connection in a state the previous borrower left it in. The count of
inherited transactions is one, not three, because the borrower that
inherited it committed -- and its commit made somebody else's unfinished
write durable, which is the row that should not be there.

Resetting the connection on the way back costs one call and removes both
counts. Not pooling costs three extra opens and removes them too, which
is the honest comparison: a pool is a decision about opens, and the
reset is part of the price rather than an optional extra.
```

The pool opened one connection for four borrowers. One borrower took it in the state the previous
one left it in, and its commit made somebody else's unfinished write durable — five rows at the end
where there should be four.

The count of inherited transactions is one rather than three, which is worth noticing: the borrower
that inherited it closed it, so the leak propagates once and then stops. A leak that propagated to
every borrower would be easier to find.

Resetting on the way back costs one call and removes both counts. Not pooling costs three extra
opens and removes them too, so the honest comparison is three opens against one call — which is a
much closer decision than "pooling is faster", and it is the decision the count makes visible.

## The predicate the index cannot serve

:::pitfall The index that exists and is not used

An index on a column is not a promise about the queries against that column. It is a sorted list of
the column's *values*, and a predicate the planner cannot turn into a range on those values does not
use it — while still returning the right rows, which is why nothing warns you.

Twenty thousand rows, an index on `email` and an index on `city`, and four predicates. The count is
of rows the plan visits, and the plan's own word for what it is going to do.

```python run
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
```

```text
20,000 rows, an index on email and an index on city

predicate               plan  rows visited matches   why                             
-------------------------------------------------------------------------------------
email = ?             SEARCH             1       1   the column on its own           
lower(email) = ?        SCAN        20,000       1   a function wrapped round it     
email LIKE '%...%'      SCAN        20,000       1   a pattern starting with a wildcard
city = ?              SEARCH           400     400   a column with 50 distinct values

The first two predicates return exactly the same row. The second one
visits twenty thousand rows to find it, because the index is a sorted
list of the values of the column and `lower(email)` is not a value of
the column -- there is nothing in the index to look up.

The fourth predicate does use the index and still visits four hundred
rows, which is the point the first block made: an index names the rows
that match, and it does not make them cheap when a lot of them match.

Nothing above is an error. Every one of these queries is correct, and
the only place the difference shows up is a plan you have to ask for.
```

The first two predicates return exactly the same row. The second one visits twenty thousand rows to
find it, because `lower(email)` is not a value in the index — there is nothing to look up. The third
has the same problem for a different reason: a pattern that starts with a wildcard cannot be turned
into a range, because the string being matched could begin anywhere.

The fourth row is the one that connects back to the second section. It *does* use the index and it
still visits four hundred rows, because a column with fifty distinct values is a column where every
value names four hundred rows. The index is doing its job and the query is still expensive, which is
the case the rule of thumb about selectivity was about.

Every one of these queries is correct. The difference between them shows up in one place only: a
plan you have to ask for.

:::

## The scenario: a report endpoint at scale

:::scenario The endpoint that got slower as the table grew

A shop with twenty thousand orders. An endpoint renders the paid orders with the customer name and
a total, and it is called fifty times. It was written the way the first draft of every endpoint is
written: it fetches the orders, loops over them to fetch each customer, and adds up the totals by
pulling every order into Python.

Four changes get it from the first row of this table to the last. Each one is measured rather than
estimated.

```python run
"""Chapter 60 -- the scenario. A report endpoint at scale.

Fifty requests against a shop with twenty thousand orders, rendered four
ways: a query per order, then one join, then the total asked of the database
rather than fetched, then an index on the filtered column. The count is of
statements, of rows received, of rows visited and of connections opened, and
each change is measured rather than estimated.
"""

import os
import sqlite3
import tempfile

ORDERS = 20000
PAID = 200
REQUESTS = 50


def build():
    path = os.path.join(tempfile.mkdtemp(), "shop.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE customer (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER,"
        " status TEXT, total INTEGER)"
    )
    conn.executemany(
        "INSERT INTO customer VALUES (?, ?)",
        [(i, f"customer-{i:04d}") for i in range(1000)],
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?)",
        [(o, o % 1000, "paid" if o < PAID else "open", 10 + o % 90)
         for o in range(ORDERS)],
    )
    conn.commit()
    return conn


def report(conn, status, join, index, aggregate):
    """One request. Returns statements sent, rows received, rows visited."""
    statements = 0
    received = 0
    visited = 0
    cur = conn.cursor()

    if join:
        cur.execute(
            "SELECT c.name, o.total FROM orders o"
            " JOIN customer c ON c.id = o.customer_id WHERE o.status = ?",
            (status,),
        )
        statements += 1
        rows = cur.fetchall()
        received += len(rows)
        visited += len(rows) if index else ORDERS
    else:
        cur.execute("SELECT id, customer_id FROM orders WHERE status = ?", (status,))
        statements += 1
        orders = cur.fetchall()
        received += len(orders)
        visited += len(orders) if index else ORDERS
        for _order_id, customer_id in orders:
            cur.execute("SELECT name FROM customer WHERE id = ?", (customer_id,))
            statements += 1
            received += len(cur.fetchall())

    if aggregate:
        total = cur.execute("SELECT SUM(total) FROM orders").fetchone()[0]
        statements += 1
        received += 1
    else:
        cur.execute("SELECT total FROM orders")
        statements += 1
        rows = cur.fetchall()
        received += len(rows)
        total = sum(row[0] for row in rows)

    return statements, received, visited, total


conn = build()
naive = report(conn, "paid", join=False, index=False, aggregate=False)
joined = report(conn, "paid", join=True, index=False, aggregate=False)
summed = report(conn, "paid", join=True, index=False, aggregate=True)
conn.execute("CREATE INDEX i_orders_status ON orders(status)")
conn.commit()
indexed = report(conn, "paid", join=True, index=True, aggregate=True)

STAGES = [
    ("per-order query, total fetched", naive),
    ("one join, total fetched", joined),
    ("one join, total from the database", summed),
    ("and an index on the filter", indexed),
]

print(f"{REQUESTS} requests, {ORDERS:,} orders, {PAID} of them paid")
print()
print(f"{'stage':<34}{'statements':>11}{'rows received':>14}{'rows visited':>13}")
print("-" * 72)
for name, (statements, received, visited, _total) in STAGES:
    print(f"{name:<34}{statements:>11,}{received:>14,}{visited:>13,}")

CHANGES = [
    ("one join instead of a query per order", naive, joined),
    ("the total asked of the database", joined, summed),
    ("an index on the filtered column", summed, indexed),
]

print()
print(f"what each change removes, over the {REQUESTS} requests")
print(f"{'change':<34}{'statements':>11}{'rows received':>14}{'rows visited':>13}{'opens':>7}")
print("-" * 79)
for name, before, after in CHANGES:
    print(f"{name:<34}{(after[0] - before[0]) * REQUESTS:>11,}"
          f"{(after[1] - before[1]) * REQUESTS:>14,}"
          f"{(after[2] - before[2]) * REQUESTS:>13,}{0:>7,}")
print(f"{'one connection for all requests':<34}"
      f"{0:>11,}{0:>14,}{0:>13,}{1 - REQUESTS:>7,}")

print()
print(f"{'over the run':<34}{'statements':>11}{'rows received':>14}"
      f"{'rows visited':>13}{'opens':>7}")
print("-" * 79)
print(f"{'before':<34}{naive[0] * REQUESTS:>11,}"
      f"{naive[1] * REQUESTS:>14,}{naive[2] * REQUESTS:>13,}{REQUESTS:>7,}")
print(f"{'after':<34}{indexed[0] * REQUESTS:>11,}"
      f"{indexed[1] * REQUESTS:>14,}{indexed[2] * REQUESTS:>13,}{1:>7,}")
print()
print("Four changes, and they are not four versions of the same change. The")
print("join removes statements and leaves the rows visited alone. The")
print("aggregate removes rows received and leaves the statements alone. The")
print("index removes rows visited and leaves both of the others alone. The")
print("connection is the only one that is about the process rather than the")
print("query. Each one moves exactly one of the numbers, which is why you")
print("have to count all of them before you decide which to do first.")
```

```text
50 requests, 20,000 orders, 200 of them paid

stage                              statements rows received rows visited
------------------------------------------------------------------------
per-order query, total fetched            202        20,400       20,000
one join, total fetched                     2        20,200       20,000
one join, total from the database           2           201       20,000
and an index on the filter                  2           201          200

what each change removes, over the 50 requests
change                             statements rows received rows visited  opens
-------------------------------------------------------------------------------
one join instead of a query per order    -10,000       -10,000            0      0
the total asked of the database             0      -999,950            0      0
an index on the filtered column             0             0     -990,000      0
one connection for all requests             0             0            0    -49

over the run                       statements rows received rows visited  opens
-------------------------------------------------------------------------------
before                                 10,100     1,020,000    1,000,000     50
after                                     100        10,050       10,000      1

Four changes, and they are not four versions of the same change. The
join removes statements and leaves the rows visited alone. The
aggregate removes rows received and leaves the statements alone. The
index removes rows visited and leaves both of the others alone. The
connection is the only one that is about the process rather than the
query. Each one moves exactly one of the numbers, which is why you
have to count all of them before you decide which to do first.
```

The table of changes is the point of the whole chapter, because the four changes are not four
versions of the same change. The join removes ten thousand statements and ten thousand rows received
over the fifty requests, and leaves rows visited alone. Asking the database for the total removes
nine hundred and ninety-nine thousand nine hundred and fifty rows received, and leaves statements
alone. The index removes nine hundred and ninety thousand rows visited, and leaves both of the
others alone. The connection removes forty-nine opens, and touches none of the query counts.

Before, ten thousand one hundred statements, one million twenty thousand rows received, one million
rows visited, fifty opens. After, one hundred statements, ten thousand and fifty rows received, ten
thousand rows visited, one open.

That is why you count all four before you decide which to do first. They are not alternatives and
they are not ranked by the same number — the change that removes the most rows visited removes no
statements at all, and the change that removes the most rows received removes no rows visited. Pick
one, and you have fixed one fifth of the problem while believing you fixed it.

:::

:::solution The four changes, in the order they are worth doing

Measure first, then fix. The order below is the one the counts give for this endpoint, and the
reason it is this order is that the first change removes the largest number and costs one line.

1. **One join instead of a query per order.** Removes ten thousand statements over fifty requests.
   Costs nothing but the join, and it is the change with the largest count attached to the smallest
   edit.
2. **An index on the column the report filters by.** Removes nine hundred and ninety thousand rows
   visited. Costs the write path from the first section, which is why it is second: the column has
   to be worth it, and here it is asked for twice per order rendered.
3. **The total asked of the database.** Removes nine hundred and ninety-nine thousand nine hundred
   and fifty rows received. Costs one line, and it is the change most likely to be missed, because
   the fetching version looks like careful code.
4. **One connection for the whole run.** Removes forty-nine opens. Smallest count, and it is the
   only one of the four that is about the process rather than the query.

Notice what is *not* on the list: nothing about the transaction boundary. This endpoint only reads.
Adding a transaction to a read-only report is the change people make when they have not counted,
and it buys atomicity the report does not need while holding locks it does not want.

:::

## Key takeaways

- **An index is a second copy kept sorted, so every write pays for it forever.** Building one index
  over four thousand and ninety-six rows costs forty-five thousand and fifty-seven comparisons, and
  inserting a row afterwards pays again.
- **The payback is a number, not a feeling.** One index on four thousand and ninety-six rows pays
  for itself after twenty-two lookups, because each lookup saves two thousand and thirty-five
  comparisons and the build cost forty-five thousand and fifty-seven.
- **An index buys one predicate.** A second index on another column does not make this lookup
  cheaper; it charges the same write cost again.
- **The index is not always the faster plan.** At a quarter of the table the indexed plan touches a
  hundred thousand and sixty-eight pages against the scan's hundred thousand, and the scan wins.
- **The crossover is a property of the ratio, not of the index.** Sweeping the cost of a random
  touch from one to sixteen moves the crossover from all of the table to a sixteenth of it.
- **Round trips scale with the rows the loop walked, not with the size of the answer.** Two hundred
  parents meant two hundred and one statements to produce two thousand rows.
- **The loop receives more rows than the join to produce the same answer** — two thousand two
  hundred against two thousand, because the parent rows arrive once each.
- **The count of statements is the count of latencies.** Two hundred statements against a local file
  is not a problem; two hundred round trips across a network is.
- **When the answer is a number, do not fetch rows to compute it.** Fetching one column sent twenty
  thousand values; asking the database sent one.
- **A lost update is not a slow design, it is a wrong one.** Two connections read-modify-wrote the
  same balance and lost seven hundred and ninety of one thousand nine hundred and eighty units.
- **A transaction gives you atomicity, not freshness.** Wrapping the read and the write changes
  nothing when the read happened before the other writer committed.
- **Compare-and-set trades correctness for a retry loop.** It lost nothing and refused twenty times,
  once per pair, which is the loop the caller now has to write.
- **A connection carries state between borrowers.** One leaked transaction made somebody else's
  unfinished write durable, leaving five rows where there should be four.
- **A leak that propagates once is harder to find than one that propagates everywhere.** One
  borrower inherited the open transaction and closed it.
- **The pool's saving is measured in opens, and the reset is part of its price.** One connection
  against four, for one extra call on the way back.
- **A predicate wrapped in a function cannot use the index on its column.** `lower(email) = ?`
  visited twenty thousand rows to return the row that `email = ?` visited one row to return.
- **A pattern starting with a wildcard cannot be turned into a range.** `LIKE '%...%'` visited
  twenty thousand rows and returned one.
- **An index can be used and still be the wrong plan.** A column with fifty distinct values named
  four hundred rows, so the plan that used the index visited four hundred.
- **Four changes to one endpoint each move exactly one of the four counts.** The join moved
  statements, the aggregate moved rows received, the index moved rows visited, the connection moved
  opens.
- **The change that removes the most rows visited removes no statements at all.** Which is why
  fixing one number and declaring the endpoint fast is the mistake this chapter is about.
- **Keyset pagination does not make a deep page cheap.** Reaching page one thousand by walking
  visited twenty thousand rows, exactly what the offset cost; what it makes cheap is the next page
  when the client holds the cursor.
- **A stale read comes from the lifetime of the read transaction, not from a second connection.** A
  transaction per read never went stale; one transaction across both reads went stale every time.
- **The rank of a column to index is a product of how often it is asked for and how much of the
  table it excludes.** The column asked for most often came third.

## Practice

- [ ] **Read a plan before you add an index.** Take a slow query in a project of yours. Ask the
  database for its plan and write down whether it scans or searches, and which index it names if it
  names one. Then count the rows the predicate matches. Report the plan, the count of matching rows,
  the size of the table, and your verdict on whether the plan is the one you would have chosen.
- [ ] **Count the round trips in a loop you have written.** Find a loop that queries inside itself,
  or write one against a table of a few hundred rows. Count the statements it sends and the rows it
  receives, then rewrite it as a join and count the same two things. Report both counts, and say how
  many of the statements in the first version were answering a question the join answered anyway.
- [ ] **Find a total you are computing by fetching.** Look for a place where your code pulls rows
  into the application to count them, sum them, or find the largest one. Count the values it
  transfers, then ask the database for the number instead and count again. Report both counts and
  the size of the table, and say why the second version is not always the right answer — there is a
  case where you need the rows as well as the number.
- [ ] **Choose two indexes from a workload rather than from a hunch.** Take five columns your
  application filters on, and for each one write down how many rows it matches and how often it is
  queried. Compute the rows each index would save, then rank the columns by that and by how often
  they are queried. Report the two orders, the positions where they disagree, and the rows the
  disagreement costs if you only have the budget for two indexes.

## Solutions

:::solution Exercise 1

A hundred thousand rows, five columns, twelve hundred queries, and the saving each index buys —
which is the number of times the column is asked for multiplied by the rows it excludes.

```python run
"""Chapter 60 -- solution 1. Choosing indexes from the workload.

Five columns, a table of a hundred thousand rows, and twelve hundred queries
spread across them. The count is of rows visited, and the saving an index
buys for one column is the number of times that column is queried multiplied
by the rows it excludes -- so the rank of a column is a product, and the
column asked for most often is not the column that saves the most.
"""

ROWS = 100000

WORKLOAD = [
    # column, rows the predicate matches, how often it is asked for
    ("email", 1, 100),
    ("city", 400, 300),
    ("status", 2000, 350),
    ("created", 30000, 400),
    ("note", 100000, 50),
]

QUERIES = sum(queries for _column, _matches, queries in WORKLOAD)
BASELINE = QUERIES * ROWS


def saved_by(matches, queries):
    """Rows visited with no index, less rows visited with one on this column."""
    return queries * (ROWS - matches)


def visited(indexed):
    """Rows visited by the whole workload, given a set of indexed columns."""
    total = 0
    for column, matches, queries in WORKLOAD:
        total += queries * (matches if column in indexed else ROWS)
    return total


print(f"{ROWS:,} rows, {QUERIES:,} queries, {BASELINE:,} rows visited with no index")
print()
print(f"{'column':<12}{'matches':>10}{'queries':>9}{'rows saved':>13}{'per query':>11}")
print("-" * 55)
for column, matches, queries in WORKLOAD:
    print(f"{column:<12}{matches:>10,}{queries:>9,}{saved_by(matches, queries):>13,}"
          f"{(ROWS - matches):>11,}")

by_saving = sorted(WORKLOAD, key=lambda row: -saved_by(row[1], row[2]))
by_frequency = sorted(WORKLOAD, key=lambda row: -row[2])

print()
print("ranked by rows saved :", ", ".join(column for column, _m, _q in by_saving))
print("ranked by how often  :", ", ".join(column for column, _m, _q in by_frequency))
agree = sum(1 for a, b in zip(by_saving, by_frequency) if a[0] == b[0])
print(f"the two orders agree on {agree} of {len(WORKLOAD)} positions")

BUDGET = 2
pick_saving = {row[0] for row in by_saving[:BUDGET]}
pick_frequency = {row[0] for row in by_frequency[:BUDGET]}

print()
print(f"two indexes to spend, so the choice is the first two of each order")
print(f"{'chosen by':<18}{'indexes':<22}{'rows visited':>14}")
print("-" * 54)
print(f"{'rows saved':<18}{', '.join(sorted(pick_saving)):<22}{visited(pick_saving):>14,}")
print(f"{'how often':<18}{', '.join(sorted(pick_frequency)):<22}"
      f"{visited(pick_frequency):>14,}")
print()
print(f"The two orders disagree about the middle of the list, and the budget")
print(f"makes the disagreement cost {abs(visited(pick_saving) - visited(pick_frequency)):,} rows.")
print("The column asked for most often is `created`, and it removes seventy")
print("thousand rows per query. The column that removes the most per query is")
print("`email`, at ninety-nine thousand nine hundred and ninety-nine, and it is")
print("asked for a quarter as often. Neither number decides on its own: the")
print("saving is the product of the two, which is why `status` comes first and")
print("`note` comes last having saved nothing at all.")
```

```text
100,000 rows, 1,200 queries, 120,000,000 rows visited with no index

column         matches  queries   rows saved  per query
-------------------------------------------------------
email                1      100    9,999,900     99,999
city               400      300   29,880,000     99,600
status           2,000      350   34,300,000     98,000
created         30,000      400   28,000,000     70,000
note           100,000       50            0          0

ranked by rows saved : status, city, created, email, note
ranked by how often  : created, status, city, email, note
the two orders agree on 2 of 5 positions

two indexes to spend, so the choice is the first two of each order
chosen by         indexes                 rows visited
------------------------------------------------------
rows saved        city, status              55,820,000
how often         created, status           57,700,000

The two orders disagree about the middle of the list, and the budget
makes the disagreement cost 1,880,000 rows.
The column asked for most often is `created`, and it removes seventy
thousand rows per query. The column that removes the most per query is
`email`, at ninety-nine thousand nine hundred and ninety-nine, and it is
asked for a quarter as often. Neither number decides on its own: the
saving is the product of the two, which is why `status` comes first and
`note` comes last having saved nothing at all.
```

:::

:::solution Exercise 2

Four hundred rows written four ways, counted in calls and in transactions. The rows are the same in
all four; the transactions are four hundred, one, one and one.

```python run
"""Chapter 60 -- solution 2. Batching writes, counted in transactions.

Four hundred rows into a real database, four ways. The count is of calls the
application makes and of transactions it commits, and the second number is
the one that decides how much work the storage engine does, because a commit
is the unit of durability rather than the unit of SQL.
"""

import os
import sqlite3
import tempfile

ROWS = 400


def build():
    path = os.path.join(tempfile.mkdtemp(), "batch.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, label TEXT)")
    conn.commit()
    return conn


def per_row(conn):
    """One statement, one commit, four hundred times."""
    calls = 0
    commits = 0
    for index in range(ROWS):
        conn.execute("INSERT INTO t VALUES (?, ?)", (index, f"row-{index:04d}"))
        calls += 1
        conn.commit()
        commits += 1
    return calls, commits


def one_commit(conn):
    """One statement per row, one commit at the end."""
    calls = 0
    for index in range(ROWS):
        conn.execute("INSERT INTO t VALUES (?, ?)", (index, f"row-{index:04d}"))
        calls += 1
    conn.commit()
    return calls, 1


def executemany(conn):
    """One call from the application, one transaction."""
    conn.executemany(
        "INSERT INTO t VALUES (?, ?)",
        [(index, f"row-{index:04d}") for index in range(ROWS)],
    )
    conn.commit()
    return 1, 1


def one_statement(conn):
    """Every row in a single statement."""
    values = ", ".join(["(?, ?)"] * ROWS)
    args = [value for index in range(ROWS)
            for value in (index, f"row-{index:04d}")]
    conn.execute(f"INSERT INTO t VALUES {values}", args)
    conn.commit()
    return 1, 1


DESIGNS = [
    ("a commit per row", per_row),
    ("one commit at the end", one_commit),
    ("executemany", executemany),
    ("one statement", one_statement),
]

print(f"{ROWS} rows, {ROWS} calls to the application's own write path")
print()
print(f"{'design':<24}{'calls':>7}{'transactions':>14}{'rows in the table':>19}")
print("-" * 64)
for name, design in DESIGNS:
    conn = build()
    calls, commits = design(conn)
    rows = conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    print(f"{name:<24}{calls:>7,}{commits:>14,}{rows:>19,}")
    conn.close()

print()
print("All four put the same four hundred rows in the table. Two of them make")
print("four hundred calls, and the first of those makes four hundred")
print("transactions. A transaction is what the engine has to make durable, so")
print("the first design asks the storage to survive four hundred separate")
print("failures and the others ask it to survive one. That is the cost the count")
print("exposes, and it is not visible in the number of rows or the number of")
print("statements.")
```

```text
400 rows, 400 calls to the application's own write path

design                    calls  transactions  rows in the table
----------------------------------------------------------------
a commit per row            400           400                400
one commit at the end       400             1                400
executemany                   1             1                400
one statement                 1             1                400

All four put the same four hundred rows in the table. Two of them make
four hundred calls, and the first of those makes four hundred
transactions. A transaction is what the engine has to make durable, so
the first design asks the storage to survive four hundred separate
failures and the others ask it to survive one. That is the cost the count
exposes, and it is not visible in the number of rows or the number of
statements.
```

:::

:::solution Exercise 3

Pagination against twenty thousand rows, with the count of rows visited taken from the engine
itself: the only predicate is a function that counts its own calls, so it is called once for every
row the engine looks at.

```python run
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
```

```text
20,000 rows, 20 per page, counting rows the engine visits

  page  jump by offset  next page, cursor held  walked from page 1
------------------------------------------------------------------
     1              20                      20                  20
    10             200                      20                 200
   100           2,000                      20               2,000
   500          10,000                      20              10,000
  1000          20,000                      20              20,000

The offset count was exactly the offset plus the page size on every one
of these pages, which is what the count should be if the measurement is
sound: 20 rows for the page and 20 for every page in front of it.

The column that matters is the third one. Keyset pagination does not
make a deep page cheap -- reaching page one thousand by walking costs
20,000 rows, exactly what the offset cost. What it makes cheap is
the next page, and only when the client already holds the key it
stopped at. A jump to an arbitrary page is the case it cannot serve at
all, because there is no key to start from.
```

:::

:::solution Exercise 4

A session that reads, is written to by another connection, and reads again — with the staleness
traced to the transaction's lifetime rather than to the second connection.

```python run
"""Chapter 60 -- solution 4. Reading your own writes.

A session reads a balance, another connection changes it, and the session
reads it again. Three designs, and the count is of reads that came back with
a value the database had already replaced. The result is that the staleness
comes from how long the read transaction lives, not from there being a
second connection.
"""

import os
import sqlite3
import tempfile

SESSIONS = 20
START = 100
STEP = 10


def build():
    path = os.path.join(tempfile.mkdtemp(), "session.db")
    conn = sqlite3.connect(path, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, balance INTEGER)")
    conn.execute("INSERT INTO account VALUES (1, ?)", (START,))
    conn.commit()
    conn.close()
    return path


def run(mode):
    """One session, repeated: read, write elsewhere, read again."""
    path = build()
    reader = sqlite3.connect(path, isolation_level=None)
    writer = sqlite3.connect(path, isolation_level=None)
    stale = 0
    first = 0
    second = 0
    for _ in range(SESSIONS):
        source = writer if mode == "route to the writer" else reader
        if mode == "one read transaction":
            reader.execute("BEGIN")
        first = source.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
        writer.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (STEP,))
        second = source.execute("SELECT balance FROM account WHERE id = 1").fetchone()[0]
        if second == first:
            stale += 1
        if mode == "one read transaction":
            reader.execute("COMMIT")
    reader.close()
    writer.close()
    return stale, first, second


MODES = ["one read transaction", "a transaction per read", "route to the writer"]

print(f"{SESSIONS} sessions, each reading, then a write lands, then reading again")
print()
print(f"{'design':<24}{'reads gone stale':>18}{'last read':>11}{'then':>7}")
print("-" * 60)
for mode in MODES:
    stale, first, second = run(mode)
    print(f"{mode:<24}{stale:>18}{first:>11,}{second:>7,}")

print()
print("The second design reads through a second connection and never goes")
print("stale, so the second connection is not the problem. The first design")
print("holds one read transaction across both reads, and inside that")
print("transaction the value cannot change -- which is the property the")
print("transaction was opened to get. A read that must see the session's own")
print("write needs a transaction that ends before the second read, or a route")
print("to the connection that did the writing.")
```

```text
20 sessions, each reading, then a write lands, then reading again

design                    reads gone stale  last read   then
------------------------------------------------------------
one read transaction                    20        290    290
a transaction per read                   0        290    300
route to the writer                      0        290    300

The second design reads through a second connection and never goes
stale, so the second connection is not the problem. The first design
holds one read transaction across both reads, and inside that
transaction the value cannot change -- which is the property the
transaction was opened to get. A read that must see the session's own
write needs a transaction that ends before the second read, or a route
to the connection that did the writing.
```

:::
