---
chapter: 61
part: 11
title: Counting Instead of Vectorising
summary: Build the array and the column store from the standard library, then count what a vectorised kernel actually saves — passes over the data rather than arithmetic — and where the column layout is the wrong tool. You will be able to choose a layout from a workload, count a group-by and a join three ways each, and say what a delete costs in each.
minutes: 110
tags: [array, column store, row store, vectorisation, passes, group by, hash join, sort merge, projection, tombstone]
---

Chapter 60 went to where the data lives. This chapter is about how it is arranged once it is there,
and it is the last chapter of the part, so it is the one that has to be honest about what it cannot
show you.

The honest part first. On most machines you would reach for a library here — something that stores a
column of numbers in a contiguous block and runs a loop over it in C rather than in Python. This
track is standard library only, so there is no such library, and that turns out to be an advantage
rather than a limitation. `array` is a contiguous block of numbers and `collections` is a hash
table; between them you can build both layouts and both algorithms yourself, and count what they
do. What you cannot do is measure the constant factor a C loop buys, and this chapter never tries
to. Every claim here is about **how many times the data is touched**, which is a property of the
layout and the algorithm, and not about how fast a touch is, which is a property of the language.

That distinction is the whole reason the chapter is called what it is called. "Vectorising" is
usually presented as a way to make arithmetic fast. What it actually does is change how many passes
over the data a computation needs, and the passes are what you can count. So the chapter counts
passes, values walked, containers touched and key comparisons — four numbers that a library would
hide from you and that decide everything.

## The record is the unit, or the field is

A table has two obvious arrangements. Keep each record together — a list of tuples — or keep each
field together — one array per field. The first is what you get by default in almost every language.
The second is what a column store is.

A hundred thousand records with six fields each, and one sum over one field. The count is of values
walked.

```python run
"""Chapter 61 -- one aggregate over one column, held two ways.

A hundred thousand records with six fields each, held as a list of tuples and
as one array per field. The query is a single sum over a single column. The
count is of the values the query has to walk past, and the difference is not
a constant factor: it is the number of fields in the record.
"""

import array

ROWS = 100000
FIELDS = 6


def row_store():
    """One tuple per record, so every field is next to every other."""
    return [(index, index % 50, index % 7, index % 1000, 100 + index % 900, 0)
            for index in range(ROWS)]


def column_store():
    """One array per field, so a field is next to itself."""
    return {
        "id": array.array("q", range(ROWS)),
        "region": array.array("q", (index % 50 for index in range(ROWS))),
        "channel": array.array("q", (index % 7 for index in range(ROWS))),
        "units": array.array("q", (index % 1000 for index in range(ROWS))),
        "price": array.array("q", (100 + index % 900 for index in range(ROWS))),
    }


def sum_units_from_rows(rows):
    """Walk the records and take one field out of each."""
    touched = 0
    total = 0
    for row in rows:
        touched += len(row)
        total += row[3]
    return total, touched


def sum_units_from_columns(columns):
    """Walk the one field the query needs."""
    touched = 0
    total = 0
    for value in columns["units"]:
        touched += 1
        total += value
    return total, touched


rows = row_store()
columns = column_store()

row_total, row_touched = sum_units_from_rows(rows)
col_total, col_touched = sum_units_from_columns(columns)

print(f"{ROWS:,} records, {FIELDS} fields each, one sum over one field")
print()
print(f"{'layout':<16}{'sum':>14}{'values walked':>15}{'per record':>12}")
print("-" * 57)
print(f"{'list of tuples':<16}{row_total:>14,}{row_touched:>15,}"
      f"{row_touched / ROWS:>12.0f}")
print(f"{'one array each':<16}{col_total:>14,}{col_touched:>15,}"
      f"{col_touched / ROWS:>12.0f}")

print()
print("Both layouts produce the same number. The second one walked")
print(f"{col_touched / row_touched:.3f} of the values the first one walked, because the")
print("record is the unit of storage in the first and the field is the unit")
print("in the second.")
print()
print("That ratio is not a constant. It is the number of fields in the record,")
print("so it grows with the record. A layout that keeps a record together is")
print("the right one when the query wants the record; it is the wrong one when")
print("the query wants one field, and it is the wrong one by exactly the")
print("width of the record.")
```

```text
100,000 records, 6 fields each, one sum over one field

layout                     sum  values walked  per record
---------------------------------------------------------
list of tuples      49,950,000        600,000           6
one array each      49,950,000        100,000           1

Both layouts produce the same number. The second one walked
0.167 of the values the first one walked, because the
record is the unit of storage in the first and the field is the unit
in the second.

That ratio is not a constant. It is the number of fields in the record,
so it grows with the record. A layout that keeps a record together is
the right one when the query wants the record; it is the wrong one when
the query wants one field, and it is the wrong one by exactly the
width of the record.
```

Both layouts produce forty-nine million nine hundred and fifty thousand, and the second one walked
a sixth of the values to produce it. The reason is a single sentence: in the first layout the record
is the unit of storage, so reading one field means holding the whole record; in the second the field
is the unit, so reading one field means reading one array.

The ratio is not a constant. It is the number of fields in the record, which is the thing to take
away from this block: a layout that keeps records together is right when the query wants the record
and wrong by exactly the width of the record when the query wants one field.

### The advantage is proportional to what the query does not want

If that were the whole story, the column store would always win and the chapter would be short. It
is not, because queries differ in how much of the record they read.

The same two layouts again, with the number of fields the query reads swept from one to six. The
count is of values walked.

```python run
"""Chapter 61 -- what a column layout is worth depends on the query.

The same two layouts, a hundred thousand records, and two queries: one that
reads a single field and one that reads five. The count is of values walked,
swept across the number of fields the query needs, and the sweep is the
point -- the advantage of a column layout is proportional to how much of the
record the query does not want.
"""

import array

ROWS = 100000

# One rule per field, so the two layouts cannot disagree about what a record
# contains -- which is the mistake this kind of comparison invites.
FIELDS = [
    lambda index: index,
    lambda index: index % 50,
    lambda index: index % 7,
    lambda index: index % 1000,
    lambda index: 100 + index % 900,
    lambda index: 0,
]
FIELD_COUNT = len(FIELDS)


def row_store():
    return [tuple(rule(index) for rule in FIELDS) for index in range(ROWS)]


def column_store():
    return [array.array("q", (rule(index) for index in range(ROWS)))
            for rule in FIELDS]


def rows_for_fields(rows, wanted):
    """Walk the records, taking the fields the query asked for."""
    touched = 0
    total = 0
    for row in rows:
        touched += len(row)
        for position in wanted:
            total += row[position]
    return total, touched


def columns_for_fields(columns, wanted):
    """Walk only the arrays the query asked for."""
    touched = 0
    total = 0
    for position in wanted:
        for value in columns[position]:
            touched += 1
            total += value
    return total, touched


rows = row_store()
columns = column_store()

print(f"{ROWS:,} records, {FIELD_COUNT} fields, reading 1 to {FIELD_COUNT} of them")
print()
print(f"{'fields read':>12}{'list of tuples':>18}{'one array each':>17}{'ratio':>9}")
print("-" * 56)
for count in range(1, FIELD_COUNT + 1):
    wanted = list(range(count))
    row_total, row_touched = rows_for_fields(rows, wanted)
    col_total, col_touched = columns_for_fields(columns, wanted)
    if row_total != col_total:
        raise SystemExit("the two layouts disagreed")
    print(f"{count:>12}{row_touched:>18,}{col_touched:>17,}"
          f"{row_touched / col_touched:>9.1f}")

print()
print("The last row is the one to remember. A query that reads every field")
print("walks exactly the same number of values in both layouts, so the column")
print("store is not faster -- it is the same, and it has paid for the")
print("transposition. The advantage of a column layout is not that columns are")
print("fast; it is that a query rarely wants the whole record, and the layout")
print("lets the query pay only for what it asked for.")
```

```text
100,000 records, 6 fields, reading 1 to 6 of them

 fields read    list of tuples   one array each    ratio
--------------------------------------------------------
           1           600,000          100,000      6.0
           2           600,000          200,000      3.0
           3           600,000          300,000      2.0
           4           600,000          400,000      1.5
           5           600,000          500,000      1.2
           6           600,000          600,000      1.0

The last row is the one to remember. A query that reads every field
walks exactly the same number of values in both layouts, so the column
store is not faster -- it is the same, and it has paid for the
transposition. The advantage of a column layout is not that columns are
fast; it is that a query rarely wants the whole record, and the layout
lets the query pay only for what it asked for.
```

The row-store column is six hundred thousand on every row of the table, because it does not matter
which fields the query asked for — the record was in hand either way. The column store climbs from
a hundred thousand to six hundred thousand, and at six fields the two are equal.

That last row is the one to remember. A query that reads every field walks exactly the same number
of values in both layouts, so the column store is not faster there; it is the same, and it has
already paid for the transposition. The advantage of a column layout is not that columns are fast.
It is that queries rarely want the whole record, and the layout lets a query pay only for what it
asked for.

## What a kernel actually saves is passes

This is where the word vectorising earns its place. Six transformations over a hundred thousand
values, done three ways: one pass per transformation writing back to the same container, one pass
per transformation building a new container, and one pass that does all six together. The count is
of reads and writes to the container.

```python run
"""Chapter 61 -- what a vectorised kernel actually saves: passes.

Six transformations over a hundred thousand values, done three ways: one pass
per transformation, one pass per transformation that rebuilds the container,
and one pass that does all six together. The count is of reads and writes to
the container, and the result is that rewriting a loop as a comprehension
changes nothing at all -- fusing the passes is the only one of the three that
removes work.
"""

VALUES = 100000
STEPS = 6


def separate(data, steps):
    """One pass per transformation, each writing back to the same container."""
    reads = 0
    writes = 0
    for _step in range(steps):
        for index in range(len(data)):
            reads += 1
            data[index] = (data[index] * 2 + 1) % 1000
            writes += 1
    return reads + writes, 0


def rebuilt(data, steps):
    """One pass per transformation, each building a new container."""
    reads = 0
    writes = 0
    containers = 1
    for _step in range(steps):
        out = []
        containers += 1
        for value in data:
            reads += 1
            out.append((value * 2 + 1) % 1000)
            writes += 1
        data = out
    return reads + writes, containers


def fused(data, steps):
    """One pass, every transformation applied inside it."""
    reads = 0
    writes = 0
    for index in range(len(data)):
        reads += 1
        value = data[index]
        for _step in range(steps):
            value = (value * 2 + 1) % 1000
        data[index] = value
        writes += 1
    return reads + writes, 0


print(f"{VALUES:,} values, up to {STEPS} transformations, counting reads and writes")
print()
print(f"{'steps':>6}{'one pass each':>15}{'rebuilt each time':>19}{'one fused pass':>16}"
      f"{'ratio':>8}")
print("-" * 64)
for steps in range(1, STEPS + 1):
    base = list(range(VALUES))
    ops_separate, _ = separate(list(base), steps)
    ops_rebuilt, containers = rebuilt(list(base), steps)
    ops_fused, _ = fused(list(base), steps)
    print(f"{steps:>6}{ops_separate:>15,}{ops_rebuilt:>19,}{ops_fused:>16,}"
          f"{ops_separate / ops_fused:>8.1f}")

base = list(range(VALUES))
_, containers = rebuilt(list(base), STEPS)

print()
print(f"At six transformations the separate version makes {6 * 2 * VALUES:,} reads and")
print(f"writes and the fused version makes {2 * VALUES:,} -- the same number it makes")
print("for one transformation, because the count is two operations per value")
print("however much arithmetic happens inside the pass. What differs between")
print("the two is how many times the container is walked.")
print()
print(f"The rebuilt version makes the same number of reads and writes as the")
print(f"separate one and allocates {containers} containers instead of one, so rewriting")
print("the loop as a comprehension is not an optimisation -- it moves the same")
print("amount of data and adds an allocation per pass. Fusing the passes is the")
print("change that removes work, and it is the only one of the three that does.")
```

```text
100,000 values, up to 6 transformations, counting reads and writes

 steps  one pass each  rebuilt each time  one fused pass   ratio
----------------------------------------------------------------
     1        200,000            200,000         200,000     1.0
     2        400,000            400,000         200,000     2.0
     3        600,000            600,000         200,000     3.0
     4        800,000            800,000         200,000     4.0
     5      1,000,000          1,000,000         200,000     5.0
     6      1,200,000          1,200,000         200,000     6.0

At six transformations the separate version makes 1,200,000 reads and
writes and the fused version makes 200,000 -- the same number it makes
for one transformation, because the count is two operations per value
however much arithmetic happens inside the pass. What differs between
the two is how many times the container is walked.

The rebuilt version makes the same number of reads and writes as the
separate one and allocates 7 containers instead of one, so rewriting
the loop as a comprehension is not an optimisation -- it moves the same
amount of data and adds an allocation per pass. Fusing the passes is the
change that removes work, and it is the only one of the three that does.
```

At one transformation all three are two hundred thousand. At six, the first and second are one
million two hundred thousand and the third is still two hundred thousand. The arithmetic is
identical in all three; what differs is how many times the container is walked.

The second design is the one worth looking at twice, because it is what "vectorising" looks like
when you write it by hand: replace the loop with a comprehension, build a new list, repeat. It makes
exactly the same number of reads and writes as the first design and allocates seven containers
instead of one. Rewriting a loop as a comprehension is not an optimisation. Fusing the passes is,
and it is the only one of the three that removes any work.

So when a library says it vectorises an operation, the number that matters is not how fast the loop
runs. It is whether the operation was three passes or one.

## Group by, counted

A group-by looks like a single operation and is four different algorithms depending on how you write
it. Twenty thousand keys over fifty groups, grouped four ways, counting items examined.

```python run
"""Chapter 61 -- group by, counted four ways.

Twenty thousand keys over fifty groups, grouped four ways. The count is of
items examined, and the four designs sit in three different growth classes:
one is the product of the group count and the row count, one is n log n, and
two are linear -- and the two linear ones differ in whether they hash.
"""

import array

ROWS = 20000
GROUPS = 50


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


KEYS = array.array("q", (mix(11 + index) % GROUPS for index in range(ROWS)))

# The same rows, already in key order -- as they arrive from a storage layer
# that keeps them that way. The sort that produced this order happened before
# the query, so it is not part of the count below.
ORDERED = array.array("q", sorted(KEYS))


def per_group(keys):
    """For each group, walk every row and count the matches."""
    examined = 0
    counts = []
    for group in range(GROUPS):
        found = 0
        for key in keys:
            examined += 1
            if key == group:
                found += 1
        counts.append(found)
    return sum(counts), examined


def sort_then_group(keys):
    """Put the rows in key order, then walk the order once."""
    examined = [0]

    def merge_sort(items):
        if len(items) <= 1:
            return list(items)
        middle = len(items) // 2
        left = merge_sort(items[:middle])
        right = merge_sort(items[middle:])
        out = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            examined[0] += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    ordered = merge_sort(keys)
    counts = []
    run = 0
    previous = None
    for key in ordered:
        examined[0] += 1
        if key != previous and previous is not None:
            counts.append(run)
            run = 0
        run += 1
        previous = key
    counts.append(run)
    return sum(counts), examined[0]


def one_pass(keys):
    """One walk, one hash lookup per row."""
    examined = 0
    counts = {}
    for key in keys:
        examined += 1
        counts[key] = counts.get(key, 0) + 1
    return sum(counts.values()), examined


def already_sorted(keys):
    """The rows arrive in key order, so grouping is one walk and no hashing."""
    ordered = sorted(keys)
    examined = 0
    counts = []
    run = 0
    previous = None
    for key in ordered:
        examined += 1
        if key != previous and previous is not None:
            counts.append(run)
            run = 0
        run += 1
        previous = key
    counts.append(run)
    return sum(counts), examined


DESIGNS = [
    ("a walk per group", per_group),
    ("sort, then walk", sort_then_group),
    ("one walk, hashing", one_pass),
    ("already in key order", already_sorted),
]

print(f"{ROWS:,} rows, {GROUPS} groups")
print()
print(f"{'design':<24}{'rows grouped':>14}{'items examined':>16}{'per row':>10}")
print("-" * 64)
for name, design in DESIGNS:
    grouped, examined = design(KEYS)
    if grouped != ROWS:
        raise SystemExit(f"{name} grouped {grouped} of {ROWS}")
    print(f"{name:<24}{grouped:>14,}{examined:>16,}{examined / ROWS:>10.1f}")

print()
print(f"The first design examined {GROUPS * ROWS:,} items to group {ROWS:,} rows, because it")
print("walks the whole table once for each group. That is the product of the")
print("group count and the row count, and it is the shape to recognise: it")
print("looks like a loop over groups, and the inner loop is the whole table.")
print()
print("The second design is n log n, and the third and fourth are linear. The")
print("difference between the last two is what makes the count worth taking:")
print("they examine exactly the same number of items, and one of them hashes")
print("every row while the other does not. When the rows already arrive in key")
print("order, the hash table is work you do not have to do -- and nothing in")
print("the output of the query tells you which case you are in.")
```

```text
20,000 rows, 50 groups

design                    rows grouped  items examined   per row
----------------------------------------------------------------
a walk per group                20,000       1,000,000      50.0
sort, then walk                 20,000         279,682      14.0
one walk, hashing               20,000          20,000       1.0
already in key order            20,000          20,000       1.0

The first design examined 1,000,000 items to group 20,000 rows, because it
walks the whole table once for each group. That is the product of the
group count and the row count, and it is the shape to recognise: it
looks like a loop over groups, and the inner loop is the whole table.

The second design is n log n, and the third and fourth are linear. The
difference between the last two is what makes the count worth taking:
they examine exactly the same number of items, and one of them hashes
every row while the other does not. When the rows already arrive in key
order, the hash table is work you do not have to do -- and nothing in
the output of the query tells you which case you are in.
```

The first design examined a million items to group twenty thousand rows, because it walks the whole
table once for each group. That is the product of the group count and the row count, and it is the
shape to recognise in your own code: it looks like a loop over groups, and the inner loop is the
entire table.

The second design is n log n and the third and fourth are linear. The difference between the last
two is the part worth the count. They examine exactly the same number of items, and one of them
hashes every row while the other does not. When the rows already arrive in key order — because a
storage layer keeps them that way, or because the previous stage sorted them — the hash table is
work you do not have to do, and nothing in the query's output tells you which case you are in.

## A join, counted

The same three-way split applies to a join, and it is where the growth classes are easiest to see.
Orders and customers, joined on the customer key, counting key comparisons.

```python run
"""Chapter 61 -- a join, counted three ways.

Orders and customers, joined on the customer key. Three designs: a nested
loop, which is what a join is if you write it yourself; a sort of both sides
followed by a merge; and a hash table built on one side. The count is of key
comparisons, and the three sit in three different growth classes.
"""

CUSTOMERS = 1000
ORDER_COUNTS = [1000, 2000, 4000]


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


def orders(count):
    return [(index, mix(7 + index) % CUSTOMERS) for index in range(count)]


def customers():
    return [(index, f"customer-{index:04d}") for index in range(CUSTOMERS)]


def nested_loop(order_rows, customer_rows):
    """Every order against every customer. The inner scan cannot stop early,
    because a key on the inner side may match more than one row."""
    comparisons = 0
    matched = 0
    for _order_id, customer_id in order_rows:
        for other_id, _name in customer_rows:
            comparisons += 1
            if other_id == customer_id:
                matched += 1
    return matched, comparisons


def hash_join(order_rows, customer_rows):
    """One hash per customer, one probe per order."""
    probes = 0
    table = {}
    for customer_id, name in customer_rows:
        probes += 1
        table[customer_id] = name
    matched = 0
    for _order_id, customer_id in order_rows:
        probes += 1
        if customer_id in table:
            matched += 1
    return matched, probes


def sort_merge(order_rows, customer_rows):
    """Put both sides in key order, then walk them together."""
    comparisons = [0]

    def merge_sort(items, key):
        if len(items) <= 1:
            return list(items)
        middle = len(items) // 2
        left = merge_sort(items[:middle], key)
        right = merge_sort(items[middle:], key)
        out = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if key(left[i]) <= key(right[j]):
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    left = merge_sort(order_rows, lambda row: row[1])
    right = merge_sort(customer_rows, lambda row: row[0])
    i = 0
    j = 0
    matched = 0
    while i < len(left) and j < len(right):
        comparisons[0] += 1
        if left[i][1] < right[j][0]:
            i += 1
        elif left[i][1] > right[j][0]:
            j += 1
        else:
            matched += 1
            i += 1
    return matched, comparisons[0]


customer_rows = customers()

print(f"{CUSTOMERS:,} customers, orders from {ORDER_COUNTS[0]:,} to {ORDER_COUNTS[-1]:,}")
print()
print(f"{'orders':>8}{'nested loop':>14}{'sort and merge':>16}{'hash table':>12}"
      f"{'nested/hash':>13}")
print("-" * 63)
for count in ORDER_COUNTS:
    order_rows = orders(count)
    matched_nested, nested = nested_loop(order_rows, customer_rows)
    matched_merge, merge = sort_merge(order_rows, customer_rows)
    matched_hash, hashed = hash_join(order_rows, customer_rows)
    if not matched_nested == matched_merge == matched_hash:
        raise SystemExit("the three designs disagreed about the answer")
    print(f"{count:>8,}{nested:>14,}{merge:>16,}{hashed:>12,}"
          f"{nested / hashed:>13.1f}")

print()
print("All three produce the same answer and the same match count, so nothing")
print("in the result distinguishes them.")
print()
print("The nested loop is the product of the two sizes: doubling the orders")
print("doubles it, and doubling the customers would double it again. The hash")
print("table is the sum of the two sizes, so it is linear in each. Sort and")
print("merge is n log n in each side, which is why it sits between them -- and")
print("it is the design that wins when one side is already in key order,")
print("because then there is nothing to sort and the merge is a single walk.")
print()
print("The column that matters is the last one. At a thousand orders the")
print("nested loop is five hundred times the hash table, and the ratio grows")
print("with the table, because one design is a product and the other is a sum.")
```

```text
1,000 customers, orders from 1,000 to 4,000

  orders   nested loop  sort and merge  hash table  nested/hash
---------------------------------------------------------------
   1,000     1,000,000          15,639       2,000        500.0
   2,000     2,000,000          27,352       3,000        666.7
   4,000     4,000,000          52,778       5,000        800.0

All three produce the same answer and the same match count, so nothing
in the result distinguishes them.

The nested loop is the product of the two sizes: doubling the orders
doubles it, and doubling the customers would double it again. The hash
table is the sum of the two sizes, so it is linear in each. Sort and
merge is n log n in each side, which is why it sits between them -- and
it is the design that wins when one side is already in key order,
because then there is nothing to sort and the merge is a single walk.

The column that matters is the last one. At a thousand orders the
nested loop is five hundred times the hash table, and the ratio grows
with the table, because one design is a product and the other is a sum.
```

All three produce the same answer and the same match count, so nothing in the result distinguishes
them. The nested loop is the product of the two sizes — doubling the orders doubles it, and doubling
the customers would double it again. The hash table is the sum of the two sizes. Sort and merge is
n log n on each side, which is why it sits between them, and why it is the design that wins when one
side is already in key order and the merge becomes a single walk.

At a thousand orders the nested loop is five hundred times the hash table, and the ratio grows with
the table. That is the sentence to carry into a code review: one design is a product and the other
is a sum, so the gap is not a constant you can wave away.

## Where the column layout is the wrong tool

Everything above makes the column store look like the right answer. It is not, and the reason is
that reads are only half of what a table does.

The same hundred thousand records in both layouts, and two operations that change the data. The
count is of containers the operation has to touch and elements it has to move.

```python run
"""Chapter 61 -- where the column layout is the wrong tool.

The same hundred thousand records in the two layouts again, and four
operations. The count is of containers the operation has to touch and of
elements it has to move. The result is that the layout that wins every read
in the previous blocks loses the delete by exactly the width of the record.
"""

import array

ROWS = 100000

FIELDS = [
    lambda index: index,
    lambda index: index % 50,
    lambda index: index % 7,
    lambda index: index % 1000,
    lambda index: 100 + index % 900,
    lambda index: 0,
]
FIELD_COUNT = len(FIELDS)


def row_store():
    return [tuple(rule(index) for rule in FIELDS) for index in range(ROWS)]


def column_store():
    return [array.array("q", (rule(index) for index in range(ROWS)))
            for rule in FIELDS]


def delete_row(rows, position, value):
    """One container, and every element after the hole moves."""
    containers = 1
    moved = len(rows) - position - 1
    del rows[position]
    return containers, moved


def delete_column(columns, position, value):
    """One container per field, and every element after the hole moves in each."""
    containers = len(columns)
    moved = containers * (len(columns[0]) - position - 1)
    for column in columns:
        del column[position]
    return containers, moved


def update_field_row(rows, position, value):
    """A record is the unit, so writing one field rebuilds the record."""
    containers = 1
    moved = len(rows[position])
    row = list(rows[position])
    row[3] = value
    rows[position] = tuple(row)
    return containers, moved


def update_field_column(columns, position, value):
    """A field is the unit, so writing one field writes one value."""
    columns[3][position] = value
    return 1, 1


POSITION = 10

print(f"{ROWS:,} records, {FIELD_COUNT} fields, deleting and updating at position {POSITION}")
print()
print(f"{'operation':<28}{'row parts':>11}{'row moved':>12}"
      f"{'col parts':>11}{'col moved':>11}")
print("-" * 73)
for label, on_rows, on_columns in (
    ("delete one record", delete_row, delete_column),
    ("update one field of one record", update_field_row, update_field_column),
):
    row_parts, row_moved = on_rows(row_store(), POSITION, 0)
    col_parts, col_moved = on_columns(column_store(), POSITION, 0)
    print(f"{label:<28}{row_parts:>11}{row_moved:>12,}{col_parts:>11}{col_moved:>11,}")

print()
print("The read blocks and this table are the same trade seen twice. A record")
print("is the unit of storage in one layout, so reading a field costs the whole")
print("record and writing a field costs the whole record -- and the delete")
print("costs one container instead of six. A field is the unit in the other, so")
print("reading and writing a field cost one value, and a delete costs every")
print("field in the record.")
print()
print("Nothing here is a reason to prefer one layout. It is a reason to know")
print("which operations the table has to serve: a table that is written once")
print("and read a million times wants the columns, and a table that is deleted")
print("from constantly wants the records.")
```

```text
100,000 records, 6 fields, deleting and updating at position 10

operation                     row parts   row moved  col parts  col moved
-------------------------------------------------------------------------
delete one record                     1      99,989          6    599,934
update one field of one record          1           6          1          1

The read blocks and this table are the same trade seen twice. A record
is the unit of storage in one layout, so reading a field costs the whole
record and writing a field costs the whole record -- and the delete
costs one container instead of six. A field is the unit in the other, so
reading and writing a field cost one value, and a delete costs every
field in the record.

Nothing here is a reason to prefer one layout. It is a reason to know
which operations the table has to serve: a table that is written once
and read a million times wants the columns, and a table that is deleted
from constantly wants the records.
```

A delete costs the record layout one container and the column layout six, and six times the shifted
elements, because the record has to be removed from every array. That is the same trade seen from
the other side: a record is the unit of storage in one layout, so reading a field costs the whole
record and writing a field costs the whole record — and a delete costs one container instead of six.

Nothing here is a reason to prefer either layout. It is a reason to know which operations the table
has to serve. A table written once and read a million times wants the columns. A table deleted from
constantly wants the records.

## The transform that runs before the filter

:::pitfall Vectorising the rows the filter was about to remove

The most expensive mistake in this chapter is not a slow algorithm. It is a fast algorithm applied
to rows that were never going to survive the next step.

A million rows, six transformations, and a filter that keeps one row in ten. Two orders for the same
two steps, counting element visits.

```python run
"""Chapter 61 -- the pitfall: transforming rows the filter was about to remove.

Two orders for the same two steps, and the count is of element visits. Doing
the filter first is the largest single saving in this chapter, and the second
table is the case where the reordering is not allowed at all -- with the
counts that show the answer changed.
"""

ROWS = 1000000
STEPS = 6
KEEP_EVERY = 10


def transform_then_filter(data, steps):
    """Transform every row, then throw nine of every ten away."""
    visits = 0
    current = data
    for _step in range(steps):
        out = []
        for region, value in current:
            visits += 1
            out.append((region, value * 2 + 1))
        current = out
    kept = 0
    for region, _value in current:
        visits += 1
        if region < KEEP_EVERY:
            kept += 1
    return kept, visits


def filter_then_transform(data, steps):
    """Throw nine of every ten away, then transform what is left."""
    visits = 0
    survivors = []
    for region, value in data:
        visits += 1
        if region < KEEP_EVERY:
            survivors.append((region, value))
    current = survivors
    for _step in range(steps):
        out = []
        for region, value in current:
            visits += 1
            out.append((region, value * 2 + 1))
        current = out
    return len(current), visits


data = [(index % 100, index % 97) for index in range(ROWS)]

print(f"{ROWS:,} rows, a filter keeping one row in {100 // KEEP_EVERY}")
print()
print(f"{'steps':>6}{'transform first':>18}{'filter first':>15}{'ratio':>9}")
print("-" * 48)
for steps in range(1, STEPS + 1):
    kept_a, visits_a = transform_then_filter(data, steps)
    kept_b, visits_b = filter_then_transform(data, steps)
    if kept_a != kept_b:
        raise SystemExit("the two orders kept different rows")
    print(f"{steps:>6}{visits_a:>18,}{visits_b:>15,}{visits_a / visits_b:>9.1f}")

print()
print(f"Both orders keep the same {kept_a:,} rows and produce the same values, and")
print(f"at six steps the first one visits {visits_a / visits_b:.1f} times as many elements.")
print("The filter is not an optimisation to add after the pipeline works. It")
print("is a decision about where the pipeline starts, and how much it is worth")
print("depends on what it is moved in front of: here the transform is six")
print("passes over every row, so moving the filter ahead of it removes five")
print("sixths of the work. In the scenario at the end of this chapter the")
print("transform is a single pass and the group and the join dominate, so the")
print("same reordering is worth almost nothing. The count is the only thing")
print("that tells those two cases apart.")

print()
print("The reordering is only allowed when the transform does not change the")
print("field the filter reads. When it does, the two orders are different")
print("programs:")
print()
SMALL = 1000


def transform_first():
    """Keep rows where x * 2 < 500, transforming before the test."""
    kept = 0
    for value in range(SMALL):
        if value * 2 < 500:
            kept += 1
    return kept


def filter_first():
    """Keep rows where x < 500, then transform."""
    kept = 0
    for value in range(SMALL):
        if value < 500:
            kept += 1
    return kept


print(f"{'order':<24}{'rows kept':>12}")
print("-" * 36)
print(f"{'transform, then filter':<24}{transform_first():>12,}")
print(f"{'filter, then transform':<24}{filter_first():>12,}")
print()
print(f"The same rule applied to the same {SMALL:,} values keeps {transform_first()} rows one way")
print(f"and {filter_first()} the other, because doubling a value changes whether the")
print("filter would have kept it. Moving a filter earlier is a change to what")
print("the program means, and the only thing that tells you which of the two")
print("you have is knowing what the transform touches.")
```

```text
1,000,000 rows, a filter keeping one row in 10

 steps   transform first   filter first    ratio
------------------------------------------------
     1         2,000,000      1,100,000      1.8
     2         3,000,000      1,200,000      2.5
     3         4,000,000      1,300,000      3.1
     4         5,000,000      1,400,000      3.6
     5         6,000,000      1,500,000      4.0
     6         7,000,000      1,600,000      4.4

Both orders keep the same 100,000 rows and produce the same values, and
at six steps the first one visits 4.4 times as many elements.
The filter is not an optimisation to add after the pipeline works. It
is a decision about where the pipeline starts, and how much it is worth
depends on what it is moved in front of: here the transform is six
passes over every row, so moving the filter ahead of it removes five
sixths of the work. In the scenario at the end of this chapter the
transform is a single pass and the group and the join dominate, so the
same reordering is worth almost nothing. The count is the only thing
that tells those two cases apart.

The reordering is only allowed when the transform does not change the
field the filter reads. When it does, the two orders are different
programs:

order                      rows kept
------------------------------------
transform, then filter           250
filter, then transform           500

The same rule applied to the same 1,000 values keeps 250 rows one way
and 500 the other, because doubling a value changes whether the
filter would have kept it. Moving a filter earlier is a change to what
the program means, and the only thing that tells you which of the two
you have is knowing what the transform touches.
```

Both orders keep the same hundred thousand rows and produce the same values, and at six steps the
first visits four point four times as many elements. The filter is not an optimisation to add once
the pipeline works. It is a decision about where the pipeline starts.

And the decision is not free of meaning. The reordering is only allowed when the transform does not
change the field the filter reads. The second table is the case where it does: the same rule applied
to the same thousand values keeps two hundred and fifty rows one way and five hundred the other,
because doubling a value changes whether the filter would have kept it. Moving a filter earlier is
a change to what the program means, and the only thing that tells you which of the two you have is
knowing what the transform touches.

:::

## The scenario: a pipeline that runs once a night

:::scenario The job that takes longer than the window it has

A hundred thousand rows through four stages — a filter, a transform, a group and a join — and the
job has to finish before the next one starts. It was written in the order the requirements were
read out: transform the data, filter it, group it, join it. Four stages, and two orderings of them.

```python run
"""Chapter 61 -- the scenario. A data pipeline that runs once a night.

A hundred thousand rows through four stages: a filter, a transform, a group
and a join. Two orderings of the same four stages, and the count is of
element visits per stage -- keyed by the stage, so the two orderings are
compared stage against stage rather than position against position.
"""

ROWS = 100000
KEEP = 1000
GROUPS = 1000
DIMENSION = 1000
ORDER = ["filter", "transform", "group", "join"]


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


def source():
    """Rows with a group key, a value, and whether the filter keeps them."""
    return [(mix(3 + index) % GROUPS, index % 97, index % (ROWS // KEEP) == 0)
            for index in range(ROWS)]


def dimension():
    return [(key, f"group-{key:04d}") for key in range(DIMENSION)]


def transform_first(data, dim):
    """Transform everything, then filter, then group and join the slow way."""
    visits = {}

    count = 0
    transformed = []
    for group, value, keep in data:
        count += 1
        transformed.append((group, value * 2 + 1, keep))
    visits["transform"] = count

    count = 0
    kept = []
    for group, value, keep in transformed:
        count += 1
        if keep:
            kept.append((group, value))
    visits["filter"] = count

    count = 0
    totals = {}
    for group in range(GROUPS):
        total = 0
        for other, value in kept:
            count += 1
            if other == group:
                total += value
        if total:
            totals[group] = total
    visits["group"] = count

    count = 0
    joined = 0
    for group, value in kept:
        for key, _name in dim:
            count += 1
            if key == group:
                joined += value
    visits["join"] = count
    return visits, totals, joined


def filter_first(data, dim):
    """Filter, then transform the survivors, then group and join in one pass."""
    visits = {}

    count = 0
    kept = []
    for group, value, keep in data:
        count += 1
        if keep:
            kept.append((group, value))
    visits["filter"] = count

    count = 0
    transformed = []
    for group, value in kept:
        count += 1
        transformed.append((group, value * 2 + 1))
    visits["transform"] = count

    count = 0
    totals = {}
    for group, value in transformed:
        count += 1
        totals[group] = totals.get(group, 0) + value
    visits["group"] = count

    count = 0
    table = {}
    for key, name in dim:
        count += 1
        table[key] = name
    joined = 0
    for group, value in transformed:
        count += 1
        if group in table:
            joined += value
    visits["join"] = count
    return visits, totals, joined


data = source()
dim = dimension()
before, totals_before, joined_before = transform_first(data, dim)
after, totals_after, joined_after = filter_first(data, dim)

if totals_before != totals_after or joined_before != joined_after:
    raise SystemExit("the two pipelines disagreed about the answer")

print(f"{ROWS:,} rows, {KEEP:,} survive the filter, {GROUPS:,} groups, "
      f"{DIMENSION:,} dimension rows")
print()
print(f"{'stage':<14}{'before':>12}{'after':>12}{'removed':>12}")
print("-" * 50)
total_before = 0
total_after = 0
for stage in ORDER:
    total_before += before[stage]
    total_after += after[stage]
    print(f"{stage:<14}{before[stage]:>12,}{after[stage]:>12,}"
          f"{before[stage] - after[stage]:>12,}")
print("-" * 50)
print(f"{'total':<14}{total_before:>12,}{total_after:>12,}"
      f"{total_before - total_after:>12,}")

grouped = before["group"] + before["join"]

print()
print("Both pipelines produce the same totals and the same join, and the first")
print(f"one visits {total_before / total_after:.1f} times as many elements as the second.")
print()
print(f"The group and the join are {grouped:,} of the {total_before:,} visits, which is")
print(f"{grouped / total_before:.1%} of the pipeline. The transform -- the stage people optimise")
print(f"first, because it is the one with the arithmetic in it -- is")
print(f"{before['transform']:,} of the {total_before:,}, which is {before['transform'] / total_before:.1%}.")
print()
print("The two stages that cost the most are the two that walk the data once")
print("per key. Both of them are one line each to replace with a single pass")
print("over a dictionary, and neither of them is a change to the arithmetic.")
print()
print("Notice that the filter costs the same in both orderings, and that the")
print("transform goes from a hundred thousand visits to a thousand. That is")
print("the whole difference between the two pipelines at that stage, and it is")
print("invisible in the stage's own output.")
```

```text
100,000 rows, 1,000 survive the filter, 1,000 groups, 1,000 dimension rows

stage               before       after     removed
--------------------------------------------------
filter             100,000     100,000           0
transform          100,000       1,000      99,000
group            1,000,000       1,000     999,000
join             1,000,000       2,000     998,000
--------------------------------------------------
total            2,200,000     104,000   2,096,000

Both pipelines produce the same totals and the same join, and the first
one visits 21.2 times as many elements as the second.

The group and the join are 2,000,000 of the 2,200,000 visits, which is
90.9% of the pipeline. The transform -- the stage people optimise
first, because it is the one with the arithmetic in it -- is
100,000 of the 2,200,000, which is 4.5%.

The two stages that cost the most are the two that walk the data once
per key. Both of them are one line each to replace with a single pass
over a dictionary, and neither of them is a change to the arithmetic.

Notice that the filter costs the same in both orderings, and that the
transform goes from a hundred thousand visits to a thousand. That is
the whole difference between the two pipelines at that stage, and it is
invisible in the stage's own output.
```

Both pipelines produce the same totals and the same join, and the first visits twenty-one times as
many elements as the second. The stage table is where the work is: the group and the join are two
million of the two million two hundred thousand visits, which is ninety-one per cent of the
pipeline. The transform — the stage people optimise first, because it is the one with the arithmetic
in it — is a hundred thousand of the two million two hundred thousand, which is four and a half per
cent.

Notice also that the filter costs the same in both orderings. That is the honest part of this
scenario: moving the filter in front of the transform saves ninety-nine thousand visits here, which
is a rounding error against the two million the group and the join cost. In the pitfall above the
same reordering was worth four times the whole pipeline, because there the transform was six passes
over every row. The same change is worth everything in one program and nothing in the other, and
the count is the only thing that tells them apart.

:::

:::solution The four changes, in the order the counts give them

1. **Replace the group-by with one pass over a dictionary.** Removes nine hundred and ninety-nine
   thousand visits, the largest single number in the table. Costs one line, and it is the change
   that looks least like an optimisation because the code gets shorter.
2. **Replace the nested-loop join with a hash join.** Removes nine hundred and ninety-eight
   thousand visits. Costs building one dictionary of the smaller side, which is a thousand entries
   here.
3. **Move the filter in front of the transform.** Removes ninety-nine thousand visits. It is third
   rather than first because the transform in this pipeline is a single pass — and it would be first
   if the transform were six passes, which is exactly the comparison the pitfall above makes.
4. **Leave the transform alone.** It is four and a half per cent of the pipeline, and the arithmetic
   inside it is the part that is easiest to make wrong. Optimising it would be the change that
   produces a bug report rather than a faster job.

The order is not a style choice. Each of the first two changes removes about a million element
visits and each is one line, and no amount of care inside the transform can remove more than a
hundred thousand.

:::

## Key takeaways

- **A layout decides which unit is contiguous: the record or the field.** Reading one field from a
  list of tuples walks six values per record; from one array per field it walks one.
- **The column layout's advantage is the width of the record.** A hundred thousand six-field records
  walked six hundred thousand values as records and a hundred thousand as a column, and the ratio is
  six because the record is six fields wide.
- **The advantage is proportional to what the query does not want.** Reading one field, the column
  layout walked a sixth as much; reading all six, the two walked exactly the same.
- **A query that reads every field is not faster in a column layout.** It is the same, and the
  transposition has already been paid for.
- **A vectorised kernel's real saving is passes, not arithmetic.** Six transformations as six passes
  cost one million two hundred thousand reads and writes; fused into one pass they cost two hundred
  thousand, for the same arithmetic.
- **Rewriting a loop as a comprehension removes no work.** The rebuilt version made the same reads
  and writes as the in-place version and allocated seven containers instead of one.
- **A group-by written as a walk per group is the product of the two counts.** Fifty groups over
  twenty thousand rows examined a million items to group twenty thousand.
- **One pass over a dictionary is linear, and so is one walk of key-ordered rows.** They examined
  exactly the same number of items, and only one of them hashes.
- **A join written as a nested loop is the product of the two table sizes.** Four thousand orders
  against a thousand customers is four million comparisons; a hash join is five thousand.
- **The gap between a product and a sum grows with the table.** The nested loop was five hundred
  times the hash table at a thousand orders and eight hundred times at four thousand.
- **Sort and merge sits between the two and wins when a side is already ordered.** It is n log n on
  each side, and the merge becomes a single walk when there is nothing to sort.
- **A delete costs the column layout one container per field.** One record, six arrays, six times
  the shifted elements — and one container in the record layout.
- **A field is the unit of storage, so writing one field writes one value.** In the record layout it
  rebuilds the whole record, which is why the update and the delete disagree about the layout.
- **The layout question is a workload question, not a correctness one.** Both layouts hold the same
  data; what changes is which operations are cheap.
- **Filtering after transforming is the most expensive mistake in this chapter.** A million rows with
  six transforms visited seven million elements; filtering first visited one million six hundred
  thousand.
- **Moving a filter earlier can change the answer.** The same rule on the same thousand values kept
  two hundred and fifty rows one way and five hundred the other, because the transform changed the
  field the filter read.
- **The filter reordering is worth everything or nothing depending on the transform.** Four point
  four times the pipeline when the transform is six passes; a rounding error when it is one.
- **The stage with the arithmetic in it is usually not the stage that costs.** The transform was
  four and a half per cent of the pipeline and the group and the join were ninety-one per cent.
- **Two stages that walk the data once per key are two one-line fixes.** Nine hundred and ninety-nine
  thousand and nine hundred and ninety-eight thousand element visits removed, for a dictionary each.
- **Choosing the join and the filter position separately gets you the second-best pair.** Filter then
  nested loop was four hundred thousand comparisons; filter then hash join was one thousand four
  hundred.
- **A layout verdict is a weighted sum, and the weights are the workload.** The column layout saved
  three hundred and sixty-five million values on reads and paid four hundred and ninety-nine million
  extra on deletes, so on that workload the records won.
- **A tombstone trades a delete for a read, and it needs the right mix to pay.** Moving the cost from
  six shifted arrays to one flag per read breaks even at one hundred and sixty-seven deletes per
  thousand reads.
- **The default layout is rarely the worst and rarely the best.** A list of tuples lost on both the
  reads and the deletes here, and it is what you get by not deciding.

## Practice

- [ ] **Count the passes in a pipeline you have written.** Take a function that transforms a
  collection and find every loop over it, including the ones inside comprehensions and the ones
  hidden in a helper. Write down how many times each element is touched, then fuse two of the passes
  and count again. Report both counts and the number of containers each version allocates.
- [ ] **Measure one query against two layouts.** Take a table you actually query and a list of the
  fields each query reads. For the most frequent query, count the values walked by a list of tuples
  and by one array per field. Report both counts, the ratio, and the field count — then say what the
  ratio would be if the query read one more field, and check your prediction against the program.
- [ ] **Rewrite a group-by three ways and count each.** Take a grouping you have written and
  implement it as a walk per group, as one pass over a dictionary, and as a sort followed by a walk
  of the runs. Count the items examined in each and report the three numbers. Then say which of the
  three your original code was, and whether the rows arrive in key order in your case.
- [ ] **Find a filter that runs after the work it removes.** Look for a place where your code
  transforms or computes something for every row and then discards most of them. Count the element
  visits with the filter where it is and with the filter moved in front. Report both counts, and
  then check whether the transform changes any field the filter reads — because if it does, the
  reordering is a different program and the counts are not comparable.

## Solutions

:::solution Exercise 1

Five queries with different field lists and call counts, plus a thousand deletes. The reads save
three hundred and sixty-five million values for the column layout; the deletes cost it four hundred
and ninety-nine million extra moved elements, and the crossover is seven hundred and thirty deletes.

```python run
"""Chapter 61 -- solution 1. Choosing a layout from the access pattern.

Five queries with different column lists and different call counts, plus a
thousand deletes. The count is of values walked by the reads and elements
moved by the deletes, and the verdict is not "columns are faster" -- it is a
weighted sum, so the answer depends on the mix of the two.
"""

ROWS = 100000
FIELDS = 6

WORKLOAD = [
    # columns the query reads, how often it is called
    (1, 500),
    (2, 200),
    (3, 100),
    (5, 50),
    (6, 150),
]

DELETES = 1000
POSITION = 10


def row_store_values_walked():
    """Every call walks the whole record."""
    return sum(calls * FIELDS * ROWS for _columns, calls in WORKLOAD)


def column_store_values_walked():
    """Every call walks only the fields it named."""
    return sum(calls * columns * ROWS for columns, calls in WORKLOAD)


MOVE_PER_DELETE_ROW = ROWS - POSITION - 1
MOVE_PER_DELETE_COLUMN = FIELDS * (ROWS - POSITION - 1)

calls_total = sum(calls for _columns, calls in WORKLOAD)
row_walked = row_store_values_walked()
col_walked = column_store_values_walked()
row_moved = DELETES * MOVE_PER_DELETE_ROW
col_moved = DELETES * MOVE_PER_DELETE_COLUMN

print(f"{ROWS:,} records, {FIELDS} fields, {calls_total:,} queries, {DELETES:,} deletes")
print()
print(f"{'columns read':>13}{'calls':>8}{'row store':>16}{'column store':>15}")
print("-" * 52)
for columns, calls in WORKLOAD:
    print(f"{columns:>13}{calls:>8}{calls * FIELDS * ROWS:>16,}"
          f"{calls * columns * ROWS:>15,}")
print("-" * 52)
print(f"{'reads, total':>13}{calls_total:>8}{row_walked:>16,}{col_walked:>15,}")
print(f"{'deletes, moved':>13}{DELETES:>8}{row_moved:>16,}{col_moved:>15,}")
print(f"{'total':>13}{'':>8}{row_walked + row_moved:>16,}"
      f"{col_walked + col_moved:>15,}")

read_saving = row_walked - col_walked
write_penalty = col_moved - row_moved
per_delete = MOVE_PER_DELETE_COLUMN - MOVE_PER_DELETE_ROW

print()
print(f"The column layout walks {read_saving:,} fewer values across the reads")
print(f"and shifts {write_penalty:,} more elements across the deletes, so on")
print(f"this workload the list of tuples wins by {write_penalty - read_saving:,}.")
print()
print(f"The two sides cross at {read_saving / per_delete:.0f} deletes: below that the")
print(f"columns win, above it the records do. At {DELETES:,} deletes per")
print(f"{calls_total:,} queries the deletes are the whole story, and the reason is")
print(f"that a delete costs {MOVE_PER_DELETE_COLUMN:,} shifted elements in the column")
print(f"layout against {MOVE_PER_DELETE_ROW:,} in the record layout -- six containers")
print("against one.")
print()
print("So the verdict is not a property of the layout. Change the number of")
print("deletes and the answer changes; make the sixth query, which reads the")
print("whole record, the only query and the columns win by nothing at all.")
print("The count is what tells you which of those workloads you have.")
```

```text
100,000 records, 6 fields, 1,000 queries, 1,000 deletes

 columns read   calls       row store   column store
----------------------------------------------------
            1     500     300,000,000     50,000,000
            2     200     120,000,000     40,000,000
            3     100      60,000,000     30,000,000
            5      50      30,000,000     25,000,000
            6     150      90,000,000     90,000,000
----------------------------------------------------
 reads, total    1000     600,000,000    235,000,000
deletes, moved    1000      99,989,000    599,934,000
        total             699,989,000    834,934,000

The column layout walks 365,000,000 fewer values across the reads
and shifts 499,945,000 more elements across the deletes, so on
this workload the list of tuples wins by 134,945,000.

The two sides cross at 730 deletes: below that the
columns win, above it the records do. At 1,000 deletes per
1,000 queries the deletes are the whole story, and the reason is
that a delete costs 599,934 shifted elements in the column
layout against 99,989 in the record layout -- six containers
against one.

So the verdict is not a property of the layout. Change the number of
deletes and the answer changes; make the sixth query, which reads the
whole record, the only query and the columns win by nothing at all.
The count is what tells you which of those workloads you have.
```

:::

:::solution Exercise 2

The largest value per group rather than a count, three ways, to show that the aggregate is not what
decides the count — and the one extra case the one-pass version has to get right.

```python run
"""Chapter 61 -- solution 2. The largest value per group, counted three ways.

The same shape as the counting group-by, with a different aggregate, because
the aggregate is not what decides. The count is of comparisons, and the
per-group design is a product again -- but the one-pass design has to keep a
maximum rather than a sum, which changes nothing about the count and adds one
thing to get right.
"""

import array

ROWS = 20000
GROUPS = 50


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


KEYS = array.array("q", (mix(11 + index) % GROUPS for index in range(ROWS)))
VALUES = array.array("q", (mix(29 + index) % 100000 for index in range(ROWS)))


def per_group(keys, values):
    """For each group, walk every row and keep the largest value."""
    comparisons = 0
    best = {}
    for group in range(GROUPS):
        top = None
        for position in range(len(keys)):
            comparisons += 1
            if keys[position] == group:
                value = values[position]
                if top is None or value > top:
                    top = value
        if top is not None:
            best[group] = top
    return best, comparisons


def one_pass(keys, values):
    """One walk, one lookup per row, one comparison against the current best."""
    comparisons = 0
    best = {}
    for position in range(len(keys)):
        comparisons += 1
        key = keys[position]
        value = values[position]
        if key not in best or value > best[key]:
            best[key] = value
    return best, comparisons


def sort_then_walk(keys, values):
    """Put the rows in key order, then take the maximum of each run."""
    comparisons = [0]

    def merge_sort(order):
        if len(order) <= 1:
            return list(order)
        middle = len(order) // 2
        left = merge_sort(order[:middle])
        right = merge_sort(order[middle:])
        out = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if keys[left[i]] <= keys[right[j]]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    order = merge_sort(range(len(keys)))
    best = {}
    previous = None
    top = None
    for position in order:
        comparisons[0] += 1
        key = keys[position]
        if key != previous and previous is not None:
            best[previous] = top
            top = None
        value = values[position]
        if top is None or value > top:
            top = value
        previous = key
    best[previous] = top
    return best, comparisons[0]


DESIGNS = [
    ("a walk per group", per_group),
    ("one walk, a dictionary", one_pass),
    ("sort, then walk", sort_then_walk),
]

print(f"{ROWS:,} rows, {GROUPS} groups, the largest value in each group")
print()
print(f"{'design':<24}{'comparisons':>13}{'per row':>10}")
print("-" * 47)
answers = []
for name, design in DESIGNS:
    best, comparisons = design(KEYS, VALUES)
    answers.append(best)
    print(f"{name:<24}{comparisons:>13,}{comparisons / ROWS:>10.1f}")

if not answers[0] == answers[1] == answers[2]:
    raise SystemExit("the three designs disagreed about the answer")

print()
print(f"All three agree on the {len(answers[0])} group maxima, and the first design")
print(f"examined {GROUPS} times as many items as the second, because it walks the")
print("table once for each group.")
print()
print("The aggregate changed and the ranking did not, which is the point: what")
print("decides the count is how many times the table is walked, and a maximum")
print("is no harder to keep in one pass than a sum.")
print()
print("What the one-pass version does add is a case to get right. A key that")
print("has never been seen is not the same as a key whose largest value so far")
print("is zero, so the test has to be `key not in best or value > best[key]`")
print("rather than a comparison against a starting value of zero. That is a")
print("correctness difference between the two designs, and it does not show up")
print("in the count at all.")
```

```text
20,000 rows, 50 groups, the largest value in each group

design                    comparisons   per row
-----------------------------------------------
a walk per group            1,000,000      50.0
one walk, a dictionary         20,000       1.0
sort, then walk               279,682      14.0

All three agree on the 50 group maxima, and the first design
examined 50 times as many items as the second, because it walks the
table once for each group.

The aggregate changed and the ranking did not, which is the point: what
decides the count is how many times the table is walked, and a maximum
is no harder to keep in one pass than a sum.

What the one-pass version does add is a case to get right. A key that
has never been seen is not the same as a key whose largest value so far
is zero, so the test has to be `key not in best or value > best[key]`
rather than a comparison against a starting value of zero. That is a
correctness difference between the two designs, and it does not show up
in the count at all.
```

:::

:::solution Exercise 3

Four thousand orders and a filter keeping one in ten, joined three ways. The join design and the
filter position are not independent choices, and the cheapest pair is not the cheapest of each.

```python run
"""Chapter 61 -- solution 3. A join with a filter in front of it.

Four thousand orders, a thousand customers, and a filter that keeps one order
in ten. Three designs, and the count is of key comparisons. The result is
that the join design and the filter position are not independent choices --
the cheapest pair is not the cheapest join plus the cheapest filter.
"""

CUSTOMERS = 1000
ORDERS = 4000
KEEP_EVERY = 10


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


def orders():
    return [(index, mix(7 + index) % CUSTOMERS) for index in range(ORDERS)]


def customers():
    return [(index, f"customer-{index:04d}") for index in range(CUSTOMERS)]


def nested_then_filter(order_rows, customer_rows):
    """Join everything, then throw nine tenths of it away."""
    comparisons = 0
    kept = 0
    for _order_id, customer_id in order_rows:
        for other_id, _name in customer_rows:
            comparisons += 1
            if other_id == customer_id and customer_id % KEEP_EVERY == 0:
                kept += 1
    return kept, comparisons


def filter_then_nested(order_rows, customer_rows):
    """Throw nine tenths away, then join what is left the same way."""
    comparisons = 0
    survivors = [row for row in order_rows if row[1] % KEEP_EVERY == 0]
    for _order_id, customer_id in survivors:
        for other_id, _name in customer_rows:
            comparisons += 1
            if other_id == customer_id:
                pass
    return len(survivors), comparisons


def filter_then_hash(order_rows, customer_rows):
    """Throw nine tenths away, then probe a table built once."""
    comparisons = 0
    table = {}
    for customer_id, name in customer_rows:
        comparisons += 1
        table[customer_id] = name
    kept = 0
    for _order_id, customer_id in order_rows:
        if customer_id % KEEP_EVERY:
            continue
        comparisons += 1
        if customer_id in table:
            kept += 1
    return kept, comparisons


order_rows = orders()
customer_rows = customers()

DESIGNS = [
    ("join, then filter", nested_then_filter),
    ("filter, then join", filter_then_nested),
    ("filter, then a hash join", filter_then_hash),
]

print(f"{ORDERS:,} orders, {CUSTOMERS:,} customers, one order in {KEEP_EVERY} survives")
print()
print(f"{'design':<26}{'rows joined':>13}{'comparisons':>14}{'per survivor':>14}")
print("-" * 67)
results = []
for name, design in DESIGNS:
    kept, comparisons = design(order_rows, customer_rows)
    results.append((name, kept, comparisons))
    print(f"{name:<26}{kept:>13,}{comparisons:>14,}{comparisons / kept:>14.0f}")

if len({kept for _name, kept, _c in results}) != 1:
    raise SystemExit("the three designs disagreed about the answer")

print()
print("All three produce the same rows, and the first one compares every order")
print("against every customer before discovering that nine tenths of the result")
print("was not wanted. Moving the filter in front of the join removes that work")
print("without changing the join at all.")
print()
print("The third row is the one worth noticing: it is the same filter position")
print("as the second and a different join, and it is the cheapest of the three.")
print("The two decisions are not independent -- a filter that shrinks the outer")
print("side by ten makes a nested loop affordable, and it makes a hash join")
print("better still, and choosing the join first and the filter position second")
print("gets you the second row instead of the third.")
```

```text
4,000 orders, 1,000 customers, one order in 10 survives

design                      rows joined   comparisons  per survivor
-------------------------------------------------------------------
join, then filter                   400     4,000,000         10000
filter, then join                   400       400,000          1000
filter, then a hash join            400         1,400             4

All three produce the same rows, and the first one compares every order
against every customer before discovering that nine tenths of the result
was not wanted. Moving the filter in front of the join removes that work
without changing the join at all.

The third row is the one worth noticing: it is the same filter position
as the second and a different join, and it is the cheapest of the three.
The two decisions are not independent -- a filter that shrinks the outer
side by ten makes a nested loop affordable, and it makes a hash join
better still, and choosing the join first and the filter position second
gets you the second row instead of the third.
```

:::

:::solution Exercise 4

A hundred deletes and a thousand reads against three layouts, including the one that marks a row
deleted instead of removing it — which moves no elements at all and still loses, because it moves
its cost to every read.

```python run
"""Chapter 61 -- solution 4. What a delete costs in each layout.

Three layouts for the same hundred thousand records: a list of tuples, one
array per field, and the column layout with a bitmap marking deleted rows.
The count is of elements moved by the deletes and elements walked by the
reads, and the tombstone design -- the one that looks free -- is the one that
loses, because it moves its cost from the writes to the reads.
"""

ROWS = 100000
FIELDS = 6
DELETES = 100
READS = 1000
POSITION = 10


def row_store():
    """One container: a delete shifts the elements after it, and reads walk records."""
    moved = DELETES * (ROWS - POSITION - 1)
    walked = READS * FIELDS * ROWS
    return moved, walked


def column_store():
    """One container per field: a delete shifts elements in every one of them."""
    moved = DELETES * FIELDS * (ROWS - POSITION - 1)
    walked = READS * ROWS
    return moved, walked


def column_store_with_tombstones():
    """Mark the row deleted instead of removing it, and skip it on the way past."""
    moved = 0
    walked = READS * ROWS + READS * ROWS
    return moved, walked


LAYOUTS = [
    ("list of tuples", row_store),
    ("one array per field", column_store),
    ("arrays plus a tombstone", column_store_with_tombstones),
]

print(f"{ROWS:,} records, {FIELDS} fields, {DELETES:,} deletes, {READS:,} reads of one field")
print()
print(f"{'layout':<26}{'moved by deletes':>18}{'walked by reads':>17}{'total':>15}")
print("-" * 76)
totals = {}
for name, layout in LAYOUTS:
    moved, walked = layout()
    totals[name] = moved + walked
    print(f"{name:<26}{moved:>18,}{walked:>17,}{moved + walked:>15,}")

plain = totals["one array per field"]
tomb = totals["arrays plus a tombstone"]
moved_saved = FIELDS * (ROWS - POSITION - 1)
extra_read = READS * ROWS
break_even = extra_read / moved_saved

print()
print(f"The tombstone moves no elements at all on a delete, and it is")
print(f"{tomb - plain:,} operations worse than the plain column layout, because")
print(f"every read now walks the whole column and then checks every flag. It")
print(f"trades {moved_saved:,} shifted elements per delete for {ROWS:,} checks per read.")
print()
print(f"That trade breaks even at {break_even:.0f} deletes per {READS:,} reads. Below that the")
print(f"plain column layout wins; above it the tombstone does. With {DELETES} deletes")
print("and a thousand reads the plain layout wins by a wide margin, and the")
print("design that looked like a free delete is the one to reject.")
print()
print("The row store is the only layout that loses on both counts here, and it")
print("is the layout you get by default. That is the honest summary of this")
print("chapter: the default is rarely the worst choice for every workload, and")
print("it is rarely the best one either.")
```

```text
100,000 records, 6 fields, 100 deletes, 1,000 reads of one field

layout                      moved by deletes  walked by reads          total
----------------------------------------------------------------------------
list of tuples                     9,998,900      600,000,000    609,998,900
one array per field               59,993,400      100,000,000    159,993,400
arrays plus a tombstone                    0      200,000,000    200,000,000

The tombstone moves no elements at all on a delete, and it is
40,006,600 operations worse than the plain column layout, because
every read now walks the whole column and then checks every flag. It
trades 599,934 shifted elements per delete for 100,000 checks per read.

That trade breaks even at 167 deletes per 1,000 reads. Below that the
plain column layout wins; above it the tombstone does. With 100 deletes
and a thousand reads the plain layout wins by a wide margin, and the
design that looked like a free delete is the one to reject.

The row store is the only layout that loses on both counts here, and it
is the layout you get by default. That is the honest summary of this
chapter: the default is rarely the worst choice for every workload, and
it is rarely the best one either.
```

:::
