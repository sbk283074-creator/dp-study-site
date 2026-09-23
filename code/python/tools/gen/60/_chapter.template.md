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

<!--BLOCK:index_write_cost-->

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

<!--BLOCK:index_pays_selectivity-->

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

<!--BLOCK:n_plus_one-->

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

<!--BLOCK:count_vs_fetch-->

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

<!--BLOCK:lost_update-->

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

<!--BLOCK:pool_state-->

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

<!--BLOCK:pitfall-->

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

<!--BLOCK:scenario-->

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

<!--BLOCK:sol1-->

:::

:::solution Exercise 2

Four hundred rows written four ways, counted in calls and in transactions. The rows are the same in
all four; the transactions are four hundred, one, one and one.

<!--BLOCK:sol2-->

:::

:::solution Exercise 3

Pagination against twenty thousand rows, with the count of rows visited taken from the engine
itself: the only predicate is a function that counts its own calls, so it is called once for every
row the engine looks at.

<!--BLOCK:sol3-->

:::

:::solution Exercise 4

A session that reads, is written to by another connection, and reads again — with the staleness
traced to the transaction's lifetime rather than to the second connection.

<!--BLOCK:sol4-->

:::
