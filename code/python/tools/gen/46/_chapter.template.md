---
chapter: 46
part: 8
title: Sorting and Searching
summary: Sorting is the algorithm you never write, which is exactly why the decisions have moved into the key and the direction. Count what a comparison costs, see why `sorted` is Timsort and stable, choose between `key=` and `cmp_to_key`, and write binary search -- including the two one-character bugs that break it.
minutes: 95
tags: [sorting, timsort, stability, binary search, bisect, cmp_to_key, complexity, ranking]
---

Chapter 45 built the structures. This chapter spends them on the operation that every program
performs more often than any other, and that almost nobody writes.

Sorting is a solved problem, and the solution is one call. `sorted` is correct, it is in C, and it
is faster than anything you would write. That is precisely why the subject deserves a chapter: the
interesting decisions have not gone away, they have *moved*. They are now in the key, in the
direction, in whether the sort was needed at all, and in what you do with the order once you have
it. Those are the four things that go wrong in real code, and none of them raises an exception.

Searching has the opposite shape. You *will* write binary search by hand -- it is the standard
interview question because it is short, and it is the standard bug report because it is subtle. Two
specific one-character mistakes account for most of the failures, and both are in this chapter,
running, with the exact input that breaks them.

One rule carries over from Chapter 44 and it matters more here than anywhere else. **State the cost,
then measure it** -- and here, measure it by *counting*. Every sort in this chapter is measured in
comparisons, not seconds, because a comparison count is a property of the algorithm and the input,
while a timing is a property of this laptop on this afternoon. The counting is done by wrapping the
values in a class with a counting `__lt__`, which is the only way to instrument code that lives in
C.

## What a comparison sort has to pay

Start with the bill, because it sets the ceiling for everything that follows.

A comparison sort learns about its input in exactly one way: it asks "is a < b?". Each answer is one
bit, and it halves the space of possibilities that remain. To pin down which of the n! possible
orders the input is in, you therefore need at least log2(n!) answers -- and Stirling's approximation
says that is about n log2 n.

That is a *floor*, not an estimate. No comparison sort beats it by more than a constant factor, and
this one is already standing on it.

<<BLOCK:comparison_model>>

The ratio column is the anticlimax the chapter is built on. Grow the input by a factor of a thousand
-- from 100 items to 100,000 -- and the comparisons grow by a factor of about two thousand nine
hundred. That is n log n, not n², and the gap to the theoretical floor never opens beyond 1.01 or
1.02.

Two consequences follow, and both are worth holding on to. The first is that there is nothing left
to win in the *algorithm*. Timsort on scrambled data is within two percent of a bound that no
algorithm can beat, so anyone who claims a new general-purpose sort is "faster" is talking about the
constant, not the class. The second is that everything interesting has moved into the *input*. A
floor of n log n is the price of sorting data you know nothing about -- and you frequently know
something about your data. That is the subject of the next two sections.

## Insertion sort: one algorithm, four costs

Insertion sort is what you write when you have not thought about sorting, and it is also the
algorithm inside every real sort's finishing pass. It is worth seeing both faces.

The idea is the one you use for a hand of cards. Take the next item, walk left while the item to
your left is larger, and drop it in the gap. Two nested loops, about eight lines, obviously correct.

<<BLOCK:insertion_sort>>

Four different costs, one algorithm, one n. The ascending input costs one comparison per item,
because every item is already in place and the inner loop exits on its first test. The descending
input costs n(n-1)/2 -- 1,999,000 comparisons for two thousand items -- because every item has to
travel the full length of the sorted prefix. The scrambled input lands about halfway, at n²/4, which
is a million comparisons for the same two thousand items.

So "insertion sort is O(n²)" and "insertion sort is O(n)" are both true statements, and the
difference is entirely in the data. This is why an honest complexity statement is not a single
symbol: it is a symbol *plus* the shape of the input you are claiming it for.

The moves column is the other half, and it is the half people forget. A comparison is a read; a move
is a write. On real hardware a write is more expensive than a read, and in insertion sort the two
columns are nearly identical on scrambled input -- 979,425 comparisons and 977,437 moves. Any sort
that wants to be fast on real inputs has to exploit order where it finds it, which is exactly what
the sort you actually use does.

## Why `sorted` is not insertion sort

`sorted` is Timsort, and Timsort is built on a single observation: real data is almost never
scrambled. It scans the input looking for *runs* -- maximal stretches that are already ordered, in
either direction -- and merges them. A descending run is accepted as a run and reversed, which is
one line of code that saves an entire worst case.

<<BLOCK:timsort_runs>>

Six input shapes, and five of them cost about one comparison per item. Only the scrambled shape pays
the n log n price -- and it lands within two percent of the floor, so even there nothing is wasted.

Each cheap row is a different trick, and they are worth telling apart, because only some of them are
optimisations:

- **Ascending.** One run covering the whole input. Timsort walks it once, sees it is ordered, and
  stops: 19,999 comparisons for 20,000 items.
- **Descending.** Also one run. Timsort accepts it and reverses it. A hand-written merge sort pays
  n log n here and a naive quicksort pays n², so this row is a deliberate design decision rather
  than luck.
- **Two ascending runs.** This is a *merge*, not a sort. Interleaving two sorted halves costs n-1
  comparisons, which is why "merge two sorted lists" and "sort this list" have different costs --
  and why the merge step of a merge sort is linear.
- **Nearly sorted.** One run plus a handful of out-of-place items that the insertion-sort tail fixes.
  Real files look like this, which is the entire reason Timsort exists.
- **All items equal.** Every comparison returns `False`, so the run never breaks. This is the input
  that degrades a naive quicksort to quadratic; Timsort simply runs out of comparisons to make.

So "how fast is `sorted`?" has no single answer. On the same 20,000 items the cost spans a factor of
thirteen, and the useful question is not about the algorithm but about the input you are handing it.

The last block of that output explains why five rows can sit at 0.08 of a column headed "floor",
which looks like a violation until you read the heading. log2(n!) is the cost of working out the
order of an input you know *nothing* about. An input that is already in order needs no comparisons
to identify its order, so the bound does not apply to it. A sort that pays n log n for sorted input
is paying for information it was handed for free.

## Stability: the guarantee you did not ask for

Python's `sorted` is *stable*: items that compare equal come out in the order they went in. The
guarantee is invisible until you depend on it, and then it is load-bearing.

It is also the easiest guarantee in the standard library to destroy by accident, because the two ways
to sort descending look interchangeable and are not.

<<BLOCK:stability>>

Read the four 91s across those two lines. `key=score, reverse=True` gives them back as eve, hal, ada,
cyd -- their order of arrival. `key=score` followed by `[::-1]` gives cyd, ada, hal, eve, which is
exactly reversed. Both lists are in descending score order. Only one of them kept the tie-break.

The reason is that `reverse=True` reverses the *comparison*: equal items are still compared as equal,
so the stable tie-break survives and simply runs backwards through the ordering that was already
there. Slicing with `[::-1]` reverses the *result*, which reverses the ties along with everything
else.

:::pitfall `[::-1]` looks like a shorter way to write `reverse=True`
They are not the same operation and they do not produce the same list. `reverse=True` sorts
descending and keeps stability; `[::-1]` sorts ascending and then turns the whole result around,
which inverts every group of equal keys. The failure is silent, the output is still sorted, and the
only symptom is an order somebody has to notice. If you want descending, say `reverse=True`.
:::

The guarantee earns its keep because it replaces tuple keys for multi-key sorting. To sort by score
and then by name, sort by the *secondary* key first and the primary key last. Each pass is stable, so
whatever order the earlier pass established survives inside every group the final pass creates. The
output above shows exactly that: sorting by name and then by score gives ada, cyd, eve, hal among
the 91s -- name order -- where the single-pass sort gave arrival order.

The tuple key `key=lambda r: (-r[1], r[0])` gets the same answer in one pass, and it is usually the
better code. It is not always available, though, and the next two sections are about what to do when
it is not.

## `key=` or `cmp_to_key`

The interface offers two ways to tell a sort what "in order" means, and they are not equally
expensive.

A **key** is a function from one item to a value that can be compared with `<`. A **comparator** is a
function from two items to a negative number, zero, or a positive number. Python applies a key
*before* the sort and then sorts the resulting values, so the key runs exactly once per item. A
comparator cannot be precomputed -- it has to be consulted during the sort -- so it runs once per
comparison.

<<BLOCK:key_vs_cmp>>

Two thousand items. The key is called 2,000 times and the comparator 19,329 times, a ratio of 9.7
against a log2(n) of 11.0. That is the log n factor, with Timsort's own constant folded in.

This is not a micro-optimisation. For a key that does real work -- parsing a date, normalising a
string, hitting a cache -- the difference between n calls and n log n calls is the difference between
a report that takes a second and one that takes a minute. A key is also easier to read and *cannot*
be internally inconsistent, because it is a pure function of one item. A comparator can be, and a
comparator that is inconsistent -- "a before b, b before c, c before a" -- produces an arbitrary
order with no error.

:::tip Reach for a key first, then a richer key, then `cmp_to_key`
The order to try them in is: a key, then a key that encodes more of the rule, then `cmp_to_key`.
`cmp_to_key` is the escape hatch for the case where the order of a pair depends on *both* items at
once, so no per-item mapping exists. The largest-number problem in the output above is that case: to
decide whether 10 goes before 2 you have to compare "102" with "210", and that answer is not a
property of 10. Once you have written a comparator, you have also given up the ability to look at
one item and say where it belongs -- so use it deliberately, not by default.
:::

## Binary search, and the two one-character bugs

Now the searching half. Binary search is short enough to write from memory and subtle enough that
most people's memory of it is wrong in one of two specific places.

The version to memorise answers "where does this belong?", not "is it here?". That is a *rank*, and
a rank always exists -- which removes the not-found case entirely.

<<BLOCK:binary_search>>

Every answer in that first table is the count of items below the target, and every one costs six or
seven probes against a scan of up to a hundred. The odd targets are the interesting ones: 1 and 199
are not in the list at all, and the search still answers "where would it go" rather than failing.

That distinction -- a search wants a yes or a no, a rank wants a position -- is the whole reason
`bisect` is more useful than `in`.

Then the two bugs, each one character wrong, each made to fail on a named input:

- **`low = middle` instead of `middle + 1`.** The lower bound never advances, so the loop never
  terminates. It does not produce a wrong answer, it produces *no* answer: the two hanging cases in
  the table are still spinning when the step cap stops them at 61 probes. The single target it
  survives is 0, because the answer is 0 and `low` never has to move.
- **`high = middle - 1` in a lower-bound search.** This is correct for *membership* and wrong here,
  because the answer can be *at* `middle`. For target 100 it returns 49 where the answer is 50, and
  for target 0 it returns the right answer -- which is the shape of bug that passes the two tests
  somebody wrote by hand.

Both come from the same mistake: treating the two bounds as if they were the same kind of thing. A
lower-bound search keeps the answer in `[low, high)` with `high` **exclusive**, so it starts at
`len(items)` -- never `len(items) - 1` -- and it is set to `middle`, not `middle - 1`. A membership
search uses inclusive bounds and moves both of them past `middle`. Pick one convention, write it
down, and do not mix them: mixing them gives you a hang in one direction and a silent off-by-one in
the other.

A hang is worse than an exception, by the way. Nothing in the logs says which line is at fault.

## The two bisects

The standard library has both conventions, tested, in C. `bisect_left` is the lower bound above;
`bisect_right` is the same search with `<=` instead of `<`. They differ by one comparison and answer
two different questions, and choosing wrong is a silent off-by-one in every group of duplicates.

<<BLOCK:bisect_variants>>

`bisect_left` counts the items *strictly below* the target -- the index a new copy would take if it
had to go before its equals. `bisect_right` counts the items *at or below* it -- the index a new copy
would take if it had to go after. Their difference is the number of copies present, computed in two
log n searches without counting anything, which is the standard way to answer "how many of these are
there" on sorted data.

The `insort` pair is the same one-character distinction applied to insertion, and it is the whole of
the stability question from earlier in the chapter. The new item lands at index 1 with `insort_left`
and at index 4 with `insort_right` -- before its three equals or after them. Both keep the list
sorted by value; only one keeps whatever order those three already had.

The grade-band table is the use that pays for knowing both. A score of exactly 50 must land in D, not
F, so the question is "how many boundaries is this score at or above" -- which is `bisect_right`.
Using `bisect_left` would put 50 in F and 80 in B, and because both answers are plausible grades, the
bug would present as a rounding dispute rather than an indexing one.

That is also the argument against the if/elif chain. A chain over bands costs one comparison per band
and grows with the number of bands; a bisect costs log n and does not care how many bands there are.
For five grades that is a matter of taste. For the 500 tax brackets in a real payroll system it is
not.

## Rank and insertion

Two jobs remain, and they are the two that `bisect` is actually for in application code: turning a
value into a position, and placing a value into an order.

Ranking is the first, and the surprise is that "rank" is not one number. A leaderboard with three
people tied at the top has to decide whether the next competitor is fourth or second, and both
answers are defensible.

<<BLOCK:rank_and_insert>>

The two rank columns disagree, and both are correct. Competition rank answers "how many beat me",
plus one -- so the three competitors who finished on 10.2 all rank 1, and the next one down ranks 4,
because ranks 2 and 3 were consumed by the tie. Dense rank answers "how many distinct results are
better", plus one, so it never skips and reads 1, 2, 3, 4 straight down the same rows. The mechanism
underneath is one `bisect_left`; everything else in that table is arithmetic on top of it.

Dense rank cannot be a single bisect, and the reason is worth stating: a bisect can tell you how many
items are below a value, but it cannot tell a repeat from a new value, because that is a property of
the *set* of items below rather than of the position of a boundary. Anything that needs to know
"how many distinct" has to look at the items.

The insertion half is where the cost story pays off. `insort` finds the slot in log n comparisons and
then shifts everything above it -- and the search cost is identical in all five rows of that table
while the shift cost varies by a factor of a thousand, from 1,000 slots to none.

So `insort` is O(log n) to find and O(n) to place. It is worth using when the list is short, when you
are inserting near the end, or when the list has to be sorted at *every instant*. It is not a way to
build a sorted collection, and the third table shows why: at n = 6,400 the insort route has already
done about 140 times the work of one `sorted()` call, and the gap widens with n because one column is
n² and the other is n log n. The `shifts/n²` column settling at 0.25 is the tell -- n²/4 is what you
get when each of n inserts moves about half of a list that is on average half full.

Append everything and call `sorted()` once. One pass to build, one n log n sort, no shifting at all.

## Sorting is often the whole solution

The most valuable habit in this chapter is not about sorting at all. It is asking, before optimising
a nested loop, whether having the data *in order* would make the loop unnecessary.

Here is the clearest example: find every pair in a list that sums to a target.

<<BLOCK:sort_then_scan>>

The nested loop compares every pair -- n(n-1)/2 of them, 499,500 for a thousand items -- which is the
definition of quadratic. Sorting first costs n log n and buys a walk that touches each item once.

The walk is the part to remember. In a sorted list, if the two ends sum to too little, then the
smallest value is too small for *any* partner, so it can be discarded and one pointer moves. If they
sum to too much, the largest is too big and it is discarded instead. Each step eliminates one item
permanently, so the walk never exceeds n steps however many pairs it finds.

The closest-pair demo is the same move on a different problem, and it is the cleaner argument: in a
sorted list the closest pair must be adjacent. That is a one-sentence proof, and it collapses n²/2
distance computations into n-1 subtractions. Note the shape of the numbers -- 499,500 against 9,651,
where the *sorting* is 8,652 of that 9,651. The sort is rarely the expensive part. The nested loop
usually is.

## Choosing, on evidence

One requirement, four implementations, and three of them are wrong in ways that pass review.

The requirement is a leaderboard: highest score first, and ties broken by earliest submission.

:::scenario The leaderboard that sorted by the wrong tie-break
The obvious version is one line, and it looks correct:

```python
rows = sorted(rows, key=lambda row: row[1], reverse=True)
```

It sorts by score, descending. It is also wrong, and it is wrong in a way that no test written
against the current fixture will catch, because the fixture happens to be in submission order. Read
the 91s in the first table below.

Here are all four attempts, side by side:

<<BLOCK:scenario>>
:::

:::solution The rule
A stable sort preserves the order it was *given*, so the last pass decides the primary order. Sort by
the **least significant key first** and the **most significant key last**, and every earlier pass
survives inside the groups the final pass creates.

The two-pass version is correct but it is not the version to prefer, because it cannot express
"descending on one key and ascending on another" -- `reverse=True` reverses *every* key. The tuple
key `(-row[1], row[2])` does express it, in one pass, and it is the version to reach for when the
keys are orderable.

Note the negation in that key. `sorted` has no per-key direction, so descending on a number means
negating it inside the key. That works for numbers and for little else -- there is no negation for a
string, which is exactly the case where the multi-pass version stops being a stylistic choice and
becomes the only correct one.
:::

The third attempt in that output is the one that survives code review, and it is worth understanding
why. Sorting by score and then reversing the result keeps the scores in the right order and inverts
every group of ties -- so the output is sorted, plausible, and wrong. Nothing raises. No test fails.
The only symptom is an ordering somebody has to notice by reading the output.

That is the recurring shape of this whole chapter. Sorting and searching have no exceptions to throw,
because every wrong answer is still a valid index, a valid grade, or a valid order.

## Key takeaways

- A comparison sort cannot beat log2(n!) comparisons, and Timsort on scrambled input is within two
  percent of that floor. The remaining wins are all in the input, not the algorithm.
- Count comparisons instead of timing them. A count is a property of the algorithm and the input; a
  timing is a property of the machine. Wrapping values in a class with a counting `__lt__` is how you
  instrument code that lives in C.
- Insertion sort is O(n) on sorted input and O(n²) on reversed input. "Sorting is O(n²)" is not a
  fact about sorting, it is a fact about an input shape.
- Timsort is linear on ascending, descending, two-run, all-equal and nearly-sorted input, and n log n
  only on genuinely scrambled input. Real data is rarely scrambled, which is why it is the default.
- `sorted` is stable, so a single-key sort silently inherits the input's order. `reverse=True`
  reverses the comparison and keeps stability; `[::-1]` reverses the result and destroys it.
- For multi-key sorting, sort by the least significant key first. `reverse=True` cannot express
  mixed directions; a tuple key can, but only when the keys are orderable.
- A key runs n times and a comparator runs about n log n times. Reach for a key, then a richer key,
  then `cmp_to_key` -- and use `cmp_to_key` only when the order of a pair depends on both items.
- Binary search's two classic bugs are `low = middle` (a hang) and `high = middle - 1` in a
  lower-bound search (a silent off-by-one). Keep `high` exclusive in a lower bound and both go away.
- `bisect_left` is the count of items strictly below; `bisect_right` is the count at or below. Their
  difference is the number of copies, and `insort_right` is what keeps duplicates stable.
- `insort` is O(log n) to find and O(n) to place. Never build a sorted collection one insert at a
  time -- append and call `sorted()` once.
- Before optimising a nested loop, ask whether sorting first would make the loop unnecessary. In a
  sorted list the closest pair is adjacent and the two-pointer walk is linear.

## Practice

- [ ] Sort a list of records by three keys -- group ascending, score descending, name ascending --
  as a tuple key and as three successive passes. Then reorder the passes and show the output changes.
  Explain which order is correct and why.
- [ ] Write `rank(samples, value)` returning a `(below, equal, above)` triple using two bisects, and
  a second version that counts with a scan. Check that both agree on the smallest value, the largest,
  a value above everything and a value below everything -- and that every triple sums to n.
- [ ] Write `first_index` and `last_index` by hand, as a lower bound and an upper bound on a list
  with duplicates, then compare both against `bisect_left` and `bisect_right` on the same list.
  Include a target that is not present.
- [ ] Group a list of events by department using `itertools.groupby`, and demonstrate the bug by
  calling it on unsorted input. Then produce the same report with a dict, and say which one you would
  ship and when.
- [ ] Sort version strings like `"1.10"` and `"1.2.3"` correctly, using a key. Then add a
  pre-release suffix (`"1.2.3-rc1"`) and decide between a richer key and `cmp_to_key`.

## Solutions

:::solution Exercise 1
The tuple key is one expression and one pass, and it is correct as written because tuple comparison
is lexicographic. The three-pass version is correct only if the passes run least-significant first:
name, then score, then group. Run them in any other order and the output is still sorted -- by the
last key you used -- with the other two silently discarded.

<<BLOCK:sol1>>
:::

:::solution Exercise 2
`bisect_left` counts the items below and `bisect_right` counts the items at or below, so the number
equal is the difference and the number above is what is left. Every triple sums to n, which is the
check that the two searches were combined correctly.

<<BLOCK:sol2>>
:::

:::solution Exercise 3
Both are the same search with a different comparison. `first_index` finds the boundary between "less
than" and "not less than"; `last_index` finds the boundary between "not greater than" and "greater
than". A boundary is a position, and every list has one -- so there is no not-found case and no
`return -1` anywhere.

<<BLOCK:sol3>>
:::

:::solution Exercise 4
`groupby` collapses *adjacent* equal keys, so it splits a sequence into runs rather than grouping it.
The sort is not an optimisation, it is what makes the grouping correct. A dict is O(n) and needs no
sort, so use it when you only need the members; use the sort when the *order* of the groups is part
of the output.

<<BLOCK:sol4>>
:::

:::solution Exercise 5
A key that turns each version into a tuple of integers fixes the `"1.10"` before `"1.9"` bug and
costs nothing. A pre-release suffix breaks it, because `int("3-rc1")` is not a number -- but the fix
is still a richer key, encoding the rule "no suffix outranks any suffix, then compare the suffix
text". `cmp_to_key` is only needed when no such encoding exists.

<<BLOCK:sol5>>
:::
