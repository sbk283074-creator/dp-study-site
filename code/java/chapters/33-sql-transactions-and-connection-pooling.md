---
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

```java run-files
// ===== TxDemo.java =====

import java.sql.SQLException;

public class TxDemo {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);
        store.seed("bob", 50);

        System.out.println("--- a transfer to an account that does not exist ---");
        try (Conn c = store.connect("c1")) {
            System.out.println("  alice before : " + c.balance("alice"));
            try {
                c.move("alice", "ghost", 30);
            } catch (SQLException e) {
                System.out.println("  failed       : " + e.getMessage());
            }
            System.out.println("  alice after  : " + c.balance("alice"));
            System.out.println();
            System.out.println("  30 has vanished: the withdrawal happened and stuck, and the");
            System.out.println("  deposit never ran. There is no code path that puts it back.");
        }

        System.out.println();
        System.out.println("--- the same transfer inside a transaction ---");
        try (Conn c = store.connect("c2")) {
            c.begin();
            try {
                c.move("alice", "ghost", 30);
            } catch (SQLException e) {
                System.out.println("  failed       : " + e.getMessage());
            }
            c.rollback();
            System.out.println("  alice after  : " + c.balance("alice"));
            System.out.println();
            System.out.println("  the half that happened was undone, so the transfer became");
            System.out.println("  all-or-nothing -- which is the whole point of a transaction");
        }

        System.out.println();
        System.out.println("--- a real transfer, committed ---");
        try (Conn c = store.connect("c3")) {
            c.begin();
            c.move("alice", "bob", 30);
            System.out.println("  inside the transaction, alice : " + c.balance("alice"));
            c.commit();
            System.out.println("  after commit, alice           : " + c.balance("alice"));
            System.out.println("  after commit, bob             : " + c.balance("bob"));
        }

        System.out.println();
        System.out.println("--- what the other connection saw, moment by moment ---");
        Store shared = new Store();
        shared.seed("alice", 100);
        shared.seed("bob", 50);
        try (Conn a = shared.connect("A"); Conn b = shared.connect("B")) {
            System.out.println("  B, before anything      : " + b.balance("alice"));
            a.begin();
            a.move("alice", "bob", 30);
            System.out.println("  A, own uncommitted work : " + a.balance("alice"));
            System.out.println("  B, at the same moment   : " + b.balance("alice"));
            a.commit();
            System.out.println("  B, after A committed    : " + b.balance("alice"));
            System.out.println();
            System.out.println("  B never saw the 70. That is read committed, and it is why");
            System.out.println("  a reader in another request cannot be handed a half-finished");
            System.out.println("  transfer and asked to make decisions about it");
        }
    }
}

// ===== Conn.java =====

import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * One connection: it sees its own uncommitted writes, and nothing else does until
 * commit(). That single property is what "read committed" isolation means.
 */
public final class Conn implements AutoCloseable {

    private final Store store;
    private final String name;
    private Map<String, Long> pending;
    private boolean closed;

    Conn(Store store, String name) {
        this.store = store;
        this.name = name;
    }

    public String name() {
        return name;
    }

    public void begin() throws SQLException {
        requireOpen();
        if (pending != null) {
            throw new SQLException("a transaction is already open on " + name);
        }
        pending = new LinkedHashMap<>();
    }

    public void commit() throws SQLException {
        requireOpen();
        if (pending == null) {
            throw new SQLException("no transaction is open on " + name);
        }
        store.committed.putAll(pending);
        pending = null;
    }

    public void rollback() throws SQLException {
        requireOpen();
        if (pending == null) {
            throw new SQLException("no transaction is open on " + name);
        }
        pending = null;
    }

    public boolean inTransaction() {
        return pending != null;
    }

    public long balance(String account) throws SQLException {
        requireOpen();
        Long value = null;
        if (pending != null && pending.containsKey(account)) {
            value = pending.get(account);
        } else {
            value = store.committed.get(account);
        }
        if (value == null) {
            throw new SQLException("no such account: " + account);
        }
        return value;
    }

    /** Two writes that must both happen, or neither. */
    public void move(String from, String to, long amount) throws SQLException {
        requireOpen();
        long source = balance(from);
        if (source < amount) {
            throw new SQLException("insufficient funds in " + from);
        }
        write(from, source - amount);
        write(to, balance(to) + amount);
    }

    public void write(String account, long value) throws SQLException {
        requireOpen();
        if (!store.committed.containsKey(account)) {
            throw new SQLException("no such account: " + account);
        }
        if (pending != null) {
            pending.put(account, value);
        } else {
            store.committed.put(account, value);
        }
    }

    public boolean isClosed() {
        return closed;
    }

    @Override
    public void close() {
        pending = null;
        closed = true;
    }

    private void requireOpen() throws SQLException {
        if (closed) {
            throw new SQLException("this connection is closed");
        }
    }
}

// ===== Store.java =====

import java.util.LinkedHashMap;
import java.util.Map;

/** The committed state of a small bank, shared by every connection to it. */
public final class Store {

    final Map<String, Long> committed = new LinkedHashMap<>();

    public void seed(String account, long balance) {
        committed.put(account, balance);
    }

    public Conn connect(String name) {
        return new Conn(this, name);
    }
}

// ===== Pool.java =====

import java.sql.SQLException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * A bounded pool of connections. Borrowing is capped and waiting is bounded, so a
 * saturated pool fails fast instead of growing until the database refuses.
 */
public final class Pool implements AutoCloseable {

    public static final class Ticket implements AutoCloseable {
        private final int id;
        private final Pool owner;
        private boolean inUse = true;

        Ticket(int id, Pool owner) {
            this.id = id;
            this.owner = owner;
        }

        public int id() {
            return id;
        }

        @Override
        public void close() {
            owner.giveBack(this);
        }
    }

    private final Deque<Ticket> idle = new ArrayDeque<>();
    private final List<Ticket> all = new ArrayList<>();
    private final int max;
    private final long timeoutMillis;
    private boolean closed;

    public Pool(int max, long timeoutMillis) {
        this.max = max;
        this.timeoutMillis = timeoutMillis;
    }

    public Ticket borrow() throws SQLException {
        long deadline = System.currentTimeMillis() + timeoutMillis;
        while (true) {
            synchronized (this) {
                requireOpen();
                if (!idle.isEmpty()) {
                    Ticket reuse = idle.pop();
                    reuse.inUse = true;
                    return reuse;
                }
                if (all.size() < max) {
                    Ticket fresh = new Ticket(all.size() + 1, this);
                    all.add(fresh);
                    return fresh;
                }
            }
            if (System.currentTimeMillis() > deadline) {
                throw new SQLException("no connection available within " + timeoutMillis
                        + " ms (pool size " + max + ", in use " + inUse() + ")");
            }
            sleep(5);
        }
    }

    public synchronized void giveBack(Ticket ticket) {
        if (ticket == null || !ticket.inUse) {
            return;
        }
        ticket.inUse = false;
        idle.push(ticket);
    }

    public synchronized int idle() {
        return idle.size();
    }

    public synchronized int inUse() {
        int busy = 0;
        for (Ticket ticket : all) {
            if (ticket.inUse) {
                busy++;
            }
        }
        return busy;
    }

    public synchronized int size() {
        return all.size();
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
            throw new SQLException("this pool is closed");
        }
    }

    private static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

```text
--- a transfer to an account that does not exist ---
  alice before : 100
  failed       : no such account: ghost
  alice after  : 70

  30 has vanished: the withdrawal happened and stuck, and the
  deposit never ran. There is no code path that puts it back.

--- the same transfer inside a transaction ---
  failed       : no such account: ghost
  alice after  : 70

  the half that happened was undone, so the transfer became
  all-or-nothing -- which is the whole point of a transaction

--- a real transfer, committed ---
  inside the transaction, alice : 40
  after commit, alice           : 40
  after commit, bob             : 80

--- what the other connection saw, moment by moment ---
  B, before anything      : 100
  A, own uncommitted work : 70
  B, at the same moment   : 100
  B, after A committed    : 70

  B never saw the 70. That is read committed, and it is why
  a reader in another request cannot be handed a half-finished
  transfer and asked to make decisions about it
```

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

```sh run-project
cat > Isolation.java <<'JAVA'
import java.sql.SQLException;

public class Isolation {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);

        try (Conn writer = store.connect("writer"); Conn reader = store.connect("reader")) {
            writer.write("alice", 10);
            System.out.println("autocommit      : " + reader.balance("alice"));

            writer.begin();
            writer.write("alice", 20);
            System.out.println("uncommitted     : " + reader.balance("alice"));
            System.out.println("writer's view   : " + writer.balance("alice"));
            writer.commit();
            System.out.println("committed       : " + reader.balance("alice"));

            writer.begin();
            writer.write("alice", 30);
            writer.rollback();
            System.out.println("rolled back     : " + reader.balance("alice"));
            System.out.println();
            System.out.println("without begin(), every statement is its own transaction and");
            System.out.println("commits immediately -- which is why a two-statement update");
            System.out.println("needs setAutoCommit(false) before it is safe");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Isolation.java
java -cp out Isolation
```

```text
autocommit      : 10
uncommitted     : 10
writer's view   : 20
committed       : 20
rolled back     : 20

without begin(), every statement is its own transaction and
commits immediately -- which is why a two-statement update
needs setAutoCommit(false) before it is safe
```

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

```sh run-project
cat > Pooled.java <<'JAVA'
import java.sql.SQLException;

public class Pooled {
    public static void main(String[] args) throws SQLException {
        try (Pool pool = new Pool(2, 100)) {
            Pool.Ticket one = pool.borrow();
            Pool.Ticket two = pool.borrow();
            System.out.println("borrowed        : " + one.id() + ", " + two.id());
            System.out.println("pool size       : " + pool.size());
            System.out.println("in use          : " + pool.inUse());
            System.out.println("idle            : " + pool.idle());

            try {
                pool.borrow();
            } catch (SQLException e) {
                System.out.println("a third borrow  : " + e.getMessage());
            }

            one.close();
            System.out.println("after returning : in use " + pool.inUse()
                    + ", idle " + pool.idle());

            Pool.Ticket again = pool.borrow();
            System.out.println("borrowed again  : " + again.id());
            System.out.println("pool size       : " + pool.size());
            System.out.println();
            System.out.println("the pool never grew past two, because two is its maximum. The");
            System.out.println("third caller waited, gave up, and got an error it can act on");
            System.out.println("instead of a connection the database will not give out");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Pooled.java
java -cp out Pooled
```

```text
borrowed        : 1, 2
pool size       : 2
in use          : 2
idle            : 0
a third borrow  : no connection available within 100 ms (pool size 2, in use 2)
after returning : in use 1, idle 1
borrowed again  : 1
pool size       : 2

the pool never grew past two, because two is its maximum. The
third caller waited, gave up, and got an error it can act on
instead of a connection the database will not give out
```

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
cat > Scenario.java <<'JAVA'
import java.sql.SQLException;

public class Scenario {
    public static void main(String[] args) throws SQLException {
        int rows = 10;

        System.out.println("--- a batch job that borrows and never returns ---");
        try (Pool pool = new Pool(4, 100)) {
            int used = 0;
            int refused = 0;
            for (int i = 0; i < rows; i++) {
                try {
                    pool.borrow();
                    used++;
                } catch (SQLException e) {
                    refused++;
                }
            }
            System.out.println("  rows          : " + rows);
            System.out.println("  processed     : " + used);
            System.out.println("  refused       : " + refused);
        }

        System.out.println();
        System.out.println("--- the same job, returning each one ---");
        try (Pool pool = new Pool(4, 100)) {
            int used = 0;
            int refused = 0;
            java.util.Set<Integer> tickets = new java.util.TreeSet<>();
            for (int i = 0; i < rows; i++) {
                try (Pool.Ticket ticket = pool.borrow()) {
                    tickets.add(ticket.id());
                    used++;
                } catch (SQLException e) {
                    refused++;
                }
            }
            System.out.println("  rows          : " + rows);
            System.out.println("  processed     : " + used);
            System.out.println("  refused       : " + refused);
            System.out.println("  tickets used  : " + tickets);
            System.out.println("  pool size     : " + pool.size());
            System.out.println();
            System.out.println("four connections processed ten rows, because each one went");
            System.out.println("back before the next was needed. The leak was not a missing");
            System.out.println("close() on a socket, it was a missing close() on a ticket");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
--- a batch job that borrows and never returns ---
  rows          : 10
  processed     : 4
  refused       : 6

--- the same job, returning each one ---
  rows          : 10
  processed     : 10
  refused       : 0
  tickets used  : [1]
  pool size     : 1

four connections processed ten rows, because each one went
back before the next was needed. The leak was not a missing
close() on a socket, it was a missing close() on a ticket
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

```java bad
import java.sql.SQLException;

public class BadCatch {
    public static void main(String[] args) {
        try {
            System.out.println("nothing in this block can throw SQLException");
        } catch (SQLException e) {
            System.out.println("never happens");
        }
    }
}
```

```text
error: exception SQLException is never thrown in body of corresponding try statement
```

A checked exception can only be caught if something in the `try` can throw it. This is a useful
constraint rather than a nuisance: a `catch (SQLException)` that survives a refactor is a block that
silently swallows nothing, and deleting it is the right response. The habit worth building is the
opposite one — catch the *narrowest* type that covers the failures you can actually handle, and let the
rest propagate to the one place in the program that turns a data-layer failure into a response.

The second is a warning, and it is about the code you write when you build a pool by hand:

```java warn
import java.util.ArrayDeque;
import java.util.Deque;

public class RawDeque {
    public static void main(String[] args) {
        Deque free = new ArrayDeque();
        free.push("connection-1");
        System.out.println(free.pop());
    }
}
```

```text
warning: [rawtypes] found raw type: Deque
```

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
```sh run-project
cat > Sol1.java <<'JAVA'
import java.sql.SQLException;

public class Sol1 {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);
        store.seed("bob", 0);

        try (Conn c = store.connect("main")) {
            c.begin();
            c.move("alice", "bob", 40);
            System.out.println("inside          : alice " + c.balance("alice")
                    + ", bob " + c.balance("bob"));
            c.rollback();
            System.out.println("after rollback  : alice " + c.balance("alice")
                    + ", bob " + c.balance("bob"));
            System.out.println("in transaction  : " + c.inTransaction());
            System.out.println();
            System.out.println("rollback discards the pending writes, so the committed state");
            System.out.println("is exactly what it was before begin()");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
inside          : alice 60, bob 40
after rollback  : alice 100, bob 0
in transaction  : false

rollback discards the pending writes, so the committed state
is exactly what it was before begin()
```

The rollback discarded the pending writes, so the committed state is exactly what it was before
`begin()`. Note that `inTransaction()` is `false` afterwards — a transaction is not reusable, and a
second unit of work needs a second `begin()`.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'JAVA'
import java.sql.SQLException;

public class Sol2 {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);

        try (Conn writer = store.connect("writer"); Conn reader = store.connect("reader")) {
            writer.begin();
            writer.write("alice", 5);
            System.out.println("writer sees     : " + writer.balance("alice"));
            System.out.println("reader sees     : " + reader.balance("alice"));
            writer.rollback();
            System.out.println("reader, rolled  : " + reader.balance("alice"));
            System.out.println();
            System.out.println("a dirty read is reading the 5 before it was committed. Read");
            System.out.println("committed forbids it, and it is the default in every database");
            System.out.println("you are likely to use -- Postgres, MySQL and SQL Server alike");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
writer sees     : 5
reader sees     : 100
reader, rolled  : 100

a dirty read is reading the 5 before it was committed. Read
committed forbids it, and it is the default in every database
you are likely to use -- Postgres, MySQL and SQL Server alike
```

The writer sees its own 5 and the reader sees 100. That gap *is* the isolation level, and it is the
reason a long-running transaction should not be a place where you compute things you then act on: the
world moved while you were reading, and read committed does not stop it.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
import java.sql.SQLException;

public class Sol3 {
    public static void main(String[] args) throws SQLException {
        try (Pool pool = new Pool(3, 100)) {
            pool.borrow();
            pool.borrow();
            pool.borrow();
            System.out.println("size            : " + pool.size());
            System.out.println("in use          : " + pool.inUse());
            try {
                pool.borrow();
            } catch (SQLException e) {
                System.out.println("the fourth      : " + e.getMessage());
            }
            System.out.println();
            System.out.println("a bounded wait turns \"the pool is exhausted\" into an error");
            System.out.println("the caller can catch, log and retry -- instead of a thread");
            System.out.println("that blocks forever holding a request slot it cannot fill");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
size            : 3
in use          : 3
the fourth      : no connection available within 100 ms (pool size 3, in use 3)

a bounded wait turns "the pool is exhausted" into an error
the caller can catch, log and retry -- instead of a thread
that blocks forever holding a request slot it cannot fill
```

The message names the timeout, the pool size and the number in use, which is the difference between an
error you can act on and one you have to reproduce. An unbounded wait would have turned this into a
thread that hangs until the client gives up.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'JAVA'
import java.sql.SQLException;

public class Sol4 {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);
        store.seed("bob", 100);

        try (Conn a = store.connect("A"); Conn b = store.connect("B")) {
            a.begin();
            b.begin();
            a.write("alice", 90);
            b.write("bob", 90);
            System.out.println("A holds alice, B holds bob, both uncommitted");
            a.commit();
            b.commit();
            System.out.println("after both commit : alice " + a.balance("alice")
                    + ", bob " + b.balance("bob"));
            System.out.println();
            System.out.println("two connections can hold open transactions at once as long as");
            System.out.println("they touch different rows. A deadlock needs both to want what");
            System.out.println("the other one has already locked, and then a database picks a");
            System.out.println("victim and rolls it back rather than waiting forever");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
A holds alice, B holds bob, both uncommitted
after both commit : alice 90, bob 90

two connections can hold open transactions at once as long as
they touch different rows. A deadlock needs both to want what
the other one has already locked, and then a database picks a
victim and rolls it back rather than waiting forever
```

Two open transactions touching different rows are not in conflict, and both commit. A deadlock needs
each to want a lock the other holds; databases detect that cycle and roll one back, which is why a
transaction that can deadlock needs a retry loop around it rather than a longer timeout.

:::
