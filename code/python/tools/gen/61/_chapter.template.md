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

<!--BLOCK:column_store-->

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

<!--BLOCK:projection-->

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

<!--BLOCK:pass_fusion-->

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

<!--BLOCK:groupby_as_counts-->

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

<!--BLOCK:join_as_counts-->

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

<!--BLOCK:array_is_wrong-->

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

<!--BLOCK:pitfall-->

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

<!--BLOCK:scenario-->

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

<!--BLOCK:sol1-->

:::

:::solution Exercise 2

The largest value per group rather than a count, three ways, to show that the aggregate is not what
decides the count — and the one extra case the one-pass version has to get right.

<!--BLOCK:sol2-->

:::

:::solution Exercise 3

Four thousand orders and a filter keeping one in ten, joined three ways. The join design and the
filter position are not independent choices, and the cheapest pair is not the cheapest of each.

<!--BLOCK:sol3-->

:::

:::solution Exercise 4

A hundred deletes and a thousand reads against three layouts, including the one that marks a row
deleted instead of removing it — which moves no elements at all and still loses, because it moves
its cost to every read.

<!--BLOCK:sol4-->

:::
