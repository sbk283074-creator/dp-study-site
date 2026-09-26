#!/usr/bin/env python3
"""Generate chapters/33-sql-transactions-and-connection-pooling.md.

    python3 tools/gen/33/gen.py

Chapter 32 got rows in and out. This one is about the two things that make a data
layer a data layer: a transaction is the unit of *failure*, not the unit of work,
and a connection is a pooled resource you borrow rather than a field you keep.
Both are demonstrated on a two-connection model, so the isolation story is visible
rather than asserted.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "33-sql-transactions-and-connection-pooling.md")

BLOCKS = {
    "core": gen.run_files(["TxDemo.java", "Conn.java", "Store.java", "Pool.java"]),
    "isolation": gen.sh("isolation.sh", "run-project"),
    "pool": gen.sh("pool.sh", "run-project"),
    "catch": gen.bad("BadCatch.java", "never thrown"),
    "raw": gen.warn("RawDeque.java", "raw type"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 33
part: 4
title: SQL, Transactions and Connection Pooling
summary: A transaction is the unit of failure, not the unit of work: a transfer that fails halfway without one loses the money. What another connection is allowed to see, autocommit, and why a Connection is a pooled resource you borrow for one unit of work rather than a field you keep.
minutes: 80
tags: [sql, transactions, acid, isolation, connection-pool, deadlock]
---

Moving money from one account to another is two writes: subtract here, add there. There is no version
of that which is one statement, and there is no machine on which it cannot fail between the two. So the
question a data layer has to answer is not "how do I write these two rows" but **"what happens if only
one of them happens"** — and the answer the database gives you is a transaction.

The claim that organises this chapter is that **a transaction is the unit of failure, not the unit of
work.** Its purpose is not to make two statements faster or tidier; it is to make the pair
all-or-nothing, because the alternative is a state your code has no path out of.

## A transfer that fails halfway

@@core@@

The first section is the whole argument. Thirty units left Alice's account and never arrived anywhere,
because the withdrawal committed and then the deposit threw. No exception was lost, no log was missed —
the program behaved exactly as written. It is simply that "subtract, then add" is not an atomic
operation and never was.

The second section is the same code inside `begin()` / `rollback()`. The failure still happened, the
`SQLException` still propagated, and the balance is back to 100 because the half that ran was discarded.
That is atomicity: the A in ACID, and the only one of the four that most application code ever thinks
about.

The four are worth knowing as a set, because they are what you are buying:

| Letter | Property | What it prevents |
|---|---|---|
| **A** | Atomicity | a change that half happened |
| **C** | Consistency | a write that violates the schema's rules — a constraint, a type, a foreign key |
| **I** | Isolation | one transaction seeing another's unfinished work |
| **D** | Durability | a committed write that disappears because the power went out |

Consistency and durability are the database's job and largely out of your hands. Atomicity and
isolation are the two you control, and both are one call away: `begin()` for the first, an isolation
level for the second.

## What another connection is allowed to see

@@isolation@@

Four numbers in that transcript, and the middle two are the lesson. The writer set Alice to 20 inside
a transaction, and **the writer sees 20 while the reader still sees 10**. The writer's own uncommitted
changes are visible to it; nobody else's are. Then `commit()` happens and the reader sees 20.

That is *read committed*, and it is the default in PostgreSQL, MySQL, SQL Server and Oracle — not
because it is the strongest option but because the stronger ones cost concurrency. The anomalies the
levels prevent, from weakest to strongest:

| Level | Dirty read | Non-repeatable read | Phantom row |
|---|---|---|---|
| Read uncommitted | possible | possible | possible |
| **Read committed** (the default) | prevented | possible | possible |
| Repeatable read | prevented | prevented | possible |
| Serializable | prevented | prevented | prevented |

- A **dirty read** is reading a value another transaction has not committed — and might roll back.
- A **non-repeatable read** is reading the same row twice in one transaction and getting two answers,
  because someone committed in between.
- A **phantom** is re-running a `WHERE` and finding new rows that were not there before.

You need repeatable read when one transaction makes several reads that have to agree with each other —
a report that sums three tables, or a check-then-write that would otherwise be a race. You need
serializable almost never, and you pay for it with aborts: the database resolves conflicts by rolling
one transaction back, so a serializable transaction needs a retry loop around it.

### Autocommit is on

Note the first line of that transcript: with no `begin()`, the write was visible immediately. **Every
statement is its own transaction unless you say otherwise.** That is what `setAutoCommit(false)` turns
off, and forgetting it is the most common way a transaction silently fails to exist — the code calls
`commit()` at the end, and each statement already committed itself, so the "transaction" covered
nothing at all.

## A connection is borrowed, not kept

Chapter 32 ended with the rule that a `Connection` is not thread-safe and must not be a field. The
mechanism that makes that workable is a pool:

@@pool@@

Three properties are visible in that transcript and all three are deliberate:

1. **The pool never grows past its maximum.** Two connections exist after four borrows, because two is
   the cap. An unbounded pool is not a pool; it is a slow way to exhaust the database's own connection
   limit, which is a hard number — PostgreSQL defaults to 100 — and hitting it produces errors in
   *other* services that share the database.
2. **Waiting is bounded.** The third borrow waited 100 ms and threw. An unbounded wait is worse than an
   error: the caller holds a thread, a request slot and a client connection for the entire time.
3. **A returned connection is reused.** Borrowing again handed back connection 1, not a new one. The
   expensive part of a connection is establishing it — TCP, TLS, authentication — and a pool's whole
   economic case is paying that once.

The size of a pool is a real tuning decision and it is counter-intuitive: **a smaller pool is often
faster.** If your database has 8 cores, 50 connections competing for them spend their time switching
rather than working. The usual rule of thumb is roughly `core_count * 2 + spindle_count`, which for a
modern SSD-backed database lands somewhere under 20 even for a busy service.

:::pitfall The connection that was never returned
A pool with a leak does not fail at the leak; it fails minutes later, in unrelated requests, with
"timed out waiting for a connection". The cause is always the same shape: a connection was borrowed on
a path that could throw, and the `finally` that returned it was missing. `try`-with-resources fixes it
structurally, which is why `Connection`, `Statement` and `ResultSet` all implement `AutoCloseable` —
closing a pooled connection does not close the socket, it *returns the connection to the pool*, and
that is the single most useful thing to know about pooling.
:::

:::scenario The batch job that took the service down
A nightly job exports ten thousand rows. It borrows a connection, writes the row, and moves on — and
because it was written as a script that exits when it is done, nobody ever returned anything. The pool
holds four connections. During the day, request handlers borrow and return normally.

```sh run-project
@@scenario@@
```

Four rows processed, six refused — and in production the six are real user requests that got a 500. The
job did not crash, the pool did not log anything at the moment of the leak, and the symptom showed up as
a partial outage whose cause was forty lines away in a different class.

:::solution
The fix is one line per row, and it is the same fix as every other resource in this book: borrow in a
`try`-with-resources so the return cannot be skipped.

```java
for (Row row : rows) {
    try (Connection c = pool.borrow()) {
        export(c, row);
    }
}
```

Three things to add once that is in place:

1. **Bound the wait everywhere.** A borrow with no timeout turns a pool problem into a thread problem.
   The transcript's error message includes the pool size and the number in use, which is what makes the
   failure diagnosable from the log alone.
2. **Log the borrow and the return together during development.** A pool whose borrow count exceeds its
   return count has a leak, and a counter is a five-minute check that finds it before your users do.
   HikariCP, which is what most Java services actually use, has `leakDetectionThreshold` for exactly
   this.
3. **Do not hold a connection across a slow call.** Borrow as late as possible and return as early as
   possible. A handler that borrows a connection and then spends 400 ms calling a payment API is
   holding a scarce resource for 400 ms of work that needs none.

:::

### Two mistakes javac can catch for you

The first is a catch block that cannot ever run, which javac rejects outright:

@@catch@@

A checked exception can only be caught if something in the `try` can throw it. This is a useful
constraint rather than a nuisance: a `catch (SQLException)` that survives a refactor is a block that
silently swallows nothing, and deleting it is the right response. The habit worth building is the
opposite one — catch the *narrowest* type that covers the failures you can actually handle, and let the
rest propagate to the one place in the program that turns a data-layer failure into a response.

The second is a warning, and it is about the code you write when you build a pool by hand:

@@raw@@

A raw `Deque` compiles, and then every element comes back as `Object` and every caller casts. A pool
that hands out `Object` is a pool whose misuse is a `ClassCastException` at a call site far away. The
parameterised version — `Deque<Connection>` — costs nothing and moves that error to compile time, which
is what Chapter 11's erasure chapter was preparing you for.

## Key takeaways

- A transaction is the unit of failure: its job is to make a multi-statement change all-or-nothing.
- A transfer that fails halfway without a transaction loses the money, and no code path puts it back.
- ACID: atomicity and isolation are yours to control; consistency and durability are the database's.
- A connection sees its own uncommitted writes; no other connection does. That is read committed.
- Autocommit is on: every statement is its own transaction until `setAutoCommit(false)`.
- The isolation anomalies, weakest to strongest: dirty read, non-repeatable read, phantom row.
- A pool never grows past its maximum, and a saturated pool fails fast rather than growing.
- Closing a pooled connection returns it to the pool — it does not close the socket.
- A smaller pool is often faster: connections beyond the database's core count contend rather than work.
- Borrow as late as possible and return as early as possible; never hold one across a slow call.

## Practice

- [ ] Move 40 from one account to another inside a transaction, roll it back, and print both balances and `inTransaction()`.
- [ ] Show that a second connection cannot see an uncommitted write, and that it can after the commit.
- [ ] Build a pool of three, borrow all three, and print the message the fourth borrow fails with.
- [ ] Open transactions on two connections at once, write to different accounts on each, and commit both.

## Solutions

:::solution Exercise 1
@@sol1@@

The rollback discarded the pending writes, so the committed state is exactly what it was before
`begin()`. Note that `inTransaction()` is `false` afterwards — a transaction is not reusable, and a
second unit of work needs a second `begin()`.

:::

:::solution Exercise 2
@@sol2@@

The writer sees its own 5 and the reader sees 100. That gap *is* the isolation level, and it is the
reason a long-running transaction should not be a place where you compute things you then act on: the
world moved while you were reading, and read committed does not stop it.

:::

:::solution Exercise 3
@@sol3@@

The message names the timeout, the pool size and the number in use, which is the difference between an
error you can act on and one you have to reproduce. An unbounded wait would have turned this into a
thread that hangs until the client gives up.

:::

:::solution Exercise 4
@@sol4@@

Two open transactions touching different rows are not in conflict, and both commit. A deadlock needs
each to want a lock the other holds; databases detect that cycle and roll one back, which is why a
transaction that can deadlock needs a retry loop around it rather than a longer timeout.

:::
"""

gen.write(TEMPLATE, BLOCKS)
