---
chapter: 59
part: 11
title: Caching
summary: Put a copy of an answer somewhere closer, and measure what that costs as well as what it saves. You will be able to decide whether a cache is worth its memory from the hit rate and the cost of a miss, to find the key that makes a cache wrong, to bound staleness with a TTL chosen from the source's own change rate, and to count the stale reads that no cache reports about itself.
minutes: 110
tags: [caching, lru_cache, hit rate, invalidation, TTL, staleness, stampede, eviction, memoisation, cache keys]
---

Chapter 58 was about finding out where the work is. This chapter is about the first thing everybody does
once they have found it, and it is the one thing in this part that can make a program *wrong* rather than
slow.

A cache is a copy of an answer, kept somewhere cheaper to reach. Everything else follows from that
sentence. A copy can be out of date, so a cache is a correctness decision before it is a performance one.
A copy costs memory whether or not it is ever read, so a cache has a cost that does not shrink when it is
useless. And a copy has to be thrown away when the original changes, so a cache has an invalidation
policy, and that policy is the part that goes wrong.

The chapter is arranged so that the counts get harder as they go. The first blocks count hits and misses,
which is easy and which is also the only count a cache reports about itself. The middle blocks count the
things a cache cannot report: the work a hit saved, the answers it got wrong, the reads that came back
stale. The last blocks count the cost side — entries held, copies to invalidate, computations repeated
under load. Every block is a program that counts something and reports what the count says, and the
recurring result is that the number the cache offers you is not the number that decides.

## The hit rate is a property of the caller

The first thing to understand about a cache is that it does not make a function cheaper. It makes a
*repeat* cheaper, and whether there are repeats is a property of whoever is calling.

One function behind one unbounded cache, called a thousand times over two access patterns. The counts are
of hits and misses, and the two patterns are the same in every respect except which keys they ask for.

<!--BLOCK:hit_rate-->

The function, the cache and the number of calls are identical in both rows. The heavy-tailed pattern got a
hit rate of 82.8% and the flat one got 36.6%, and the only difference is the distribution of the keys.

The misses are the number of distinct keys and nothing else — that is the whole mechanism. The heavy
pattern reached 172 of the 1,000 keys in the space and the flat one reached 634, so the flat pattern asked
for 3.7 times as many different things. The work follows the same ratio: without a cache both patterns cost
6,000 units, and with one they cost 1,032 and 3,804.

So the first question about a cache is not which cache. It is how often the same question is asked twice,
and that is a number you can count before writing any of it.

## Three places to put the write

A cache has two operations and only one of them is interesting. Reads are easy: look, miss, fill. Writes
are where the designs differ, because a write has to decide how many places it is going to touch.

Cache-aside, write-through and write-behind over the same interleaved sequence of 200 reads and 40 writes.
The count is of store operations and of reads that would get a different answer from the store than from
the cache.

<!--BLOCK:cache_sides-->

All three produce the same answers, and the store was asked to do three different amounts of work.

Cache-aside did 41 store reads and write-through did 16. The difference is the invalidation: dropping the
key on a write means the next read of it misses, so the store is read 25 more times to fetch a value the
cache had held. That is the hidden cost of the simplest correct invalidation, and it is invisible unless
you count store reads.

Write-behind did 6 store writes against 40 for the other two, and it is the only design with a
disagreement count above zero: 45 reads got an answer the store did not have yet. The 6 is not a rounding
of 40 — the flush threshold is 12 dirty keys and the writes only ever touch 6 of the 20 keys, so the batch
never fills and the store is written once, at the end. A write-behind cache's store traffic is a function
of how many distinct keys are dirty at the same moment, which is a property of the workload rather than of
the design.

That is the whole trade, and it is the same trade at every level of this chapter. Writing to both places
keeps them in step and costs a store write per write. Writing to one and catching up later costs fewer
store writes and buys a window in which two readers of the same key get different answers.

## Invalidation is the hard part

Everything so far has been about how often a cache is right. This is about what happens when it is wrong,
and the surprising part is that the careful answer is the wrong one.

A cache of thirteen entries derived from four sources, and one write. The count is of entries dropped and
of reads that came back with a value the source no longer had.

<!--BLOCK:invalidation-->

One write to source 2 changes three of the twelve entries and the summary. Dropping the source's three
entries drops 3 and leaves 10 reads stale; dropping everything drops 13 and leaves none.

The first row is the mistake this whole section is about. That invalidation is precise, it is efficient, it
is what the key says to do, and it is wrong — because one cached value is derived from the source and does
not name it in its key. The third row is the same mistake made cheaper: it drops 1 entry where three
needed dropping and leaves 14 stale reads, so a reader looking only at the dropped count would rank it as
the most careful of the three.

That is why invalidation is the hard part rather than the bookkeeping part. A key is a claim about what a
value depends on, and the summary here depends on all four sources while its key names none of them. The
count of stale reads is the only thing that checks the claim, and it is not visible in the invalidation
code.

The safe answer is the second row, and its cost is measurable too. It drops 13 entries where three needed
dropping, so the next reads of the untouched sources all miss. Clearing the cache is always correct, and it
is the right thing to do until the keys can be made to say what they actually depend on.

## The TTL is two numbers

A time-to-live is the invalidation policy for people who cannot enumerate their keys. It is also the only
part of a cache that is usually set by taste, which is a shame, because both of its numbers are countable.

One key behind a cache, a source that changes every thirty-seven ticks, and four TTLs. The count is of
loads, of reads that came back with a value the source no longer had, and of how old the oldest such value
was.

<!--BLOCK:ttl-->

A TTL is two numbers at once and the table prints both. It is a bound on how wrong a read can be, and a tax
on how often the source is asked.

With no TTL the cache is loaded once and is wrong for 363 of the 400 reads, by up to 399 ticks. That is a
perfect hit rate on a cache that is useless. At a TTL of 5 the worst staleness is 4 ticks and the loads
rise to 80; at 20 it is 19 ticks and 20 loads; at 100 it is 99 ticks and 4 loads. The bound is one tick
below the TTL in every case, because an entry is still fresh on the tick it is due to expire.

The number of stale reads is not a function of the TTL on its own. A TTL of 5 loads 80 times and leaves 20
stale reads; a TTL of 100 loads 4 times and leaves 297. The second is 14.8 times as many stale reads from
20 times fewer loads, and that relationship comes from how the TTL falls against the source's own change
period of 37 — which is not a number the cache controls.

So a TTL is chosen from two facts that live outside the cache: how stale a read is allowed to be, and how
often the source changes. The first is a decision. The second is a measurement.

## The stampede

A cache that is correct is not the same as a cache that is efficient, and the difference shows up in one
instant rather than over a run.

Callers arriving together at keys the cache does not hold. The count is of how many of them recompute the
same answer.

<!--BLOCK:stampede-->

The first table is fifty callers arriving together for one key. The second is the same fifty callers spread
over ten keys that are all missing. Every caller still arrives before any of them has a result, so every
caller still computes.

Without protection, all fifty callers compute in both tables. With a per-key lock, one caller per key
computes and the rest wait. Protection removes all 49 duplicates in the first table and all 40 in the
second, so the count scales with the number of callers rather than with the number of keys.

Neither design is wrong, and that is the point. Both return the correct value to every caller and both
leave the cache full at the end. No test of the returned values can tell them apart. And a hit rate is
computed after the fact over all the calls, so a cache with an excellent hit rate can still perform the
same expensive query fifty times without the hit rate showing it.

## The key is the correctness

The key is not an optimisation. It is the statement of what the cached value depends on, and a cache is
correct exactly when that statement is complete.

One function whose answer depends on two arguments, cached four ways. The count is of calls that got an
answer computed for different arguments.

<!--BLOCK:cache_key-->

Two of the four designs returned an answer computed for different arguments, and both of them report an
excellent hit rate.

`the item alone` is the mistake that looks reasonable. The item is the interesting half of the call and the
currency feels like a detail, so the key names the item and the currency is captured in the value. After
warm-up it hits on 30 of the 40 calls and 18 of those answers are wrong.

`the type of both` is the same mistake taken further, and the table shows what taking it further buys: 39
hits instead of 30, and 36 wrong answers instead of 18. A key that names less is a cache that hits more and
is wrong more, and the two counts move together.

The other two designs agree on every count in the table: 20 misses, 20 hits, no wrong answers. The
difference between them appears when a third currency is added. The tuple key needs no change. The string
key needs its separator to stay unambiguous, which is a property of the data rather than of the code.

## The hit rate is not what a cache is for

This is the block that makes the rest of the chapter usable, because it is the one that says which number
to look at.

Two caches over two functions with very different costs. The count is of the work removed, and the cache
with the better hit rate removes less.

<!--BLOCK:cache_effectiveness-->

The first cache has a hit rate of 90% and the second of 40%. The second removes 22.2 times as much work.

The arithmetic is not subtle and it is worth saying out loud. A hit saves the cost of one call, so the work
a cache removes is the hit count multiplied by the cost of the thing being cached. The hit rate is one
factor of two, and it is the one everybody quotes because it is the one the cache can report about itself.

`lru_cache` will tell you its own hit rate and it cannot tell you what a call costs, so the number it
offers is the number that gets optimised. A cache in front of a function that costs two units is a data
structure that saves you 180 units out of 200, and it costs a dictionary, an eviction policy and a place
where staleness can happen.

## The eviction policy is a claim

A bounded cache has to choose what to throw away, and the choice is not a detail to be defaulted. It is a
claim about the access pattern.

Four policies over a cyclic scan of two hundred keys with a cache of fifty. The count is of hits.

<!--BLOCK:eviction_policy-->

Every bounded policy fails this pattern. Least recently used got 0 hits out of 400, first in first out got
0, and choosing a victim at random got 7.

The reason is one line long. The cache holds 50 entries and the scan walks 200, so by the time the scan
comes back to a key that key was evicted 150 accesses ago — and least recently used evicts exactly the
entry it is about to be asked for.

Random replacement is the policy with no claim at all about the access pattern, and it beats the policy
with the strongest claim by 7 accesses out of 400. That difference is tiny, and the number beside it is the
one to read: not evicting at all gets 200. The spread across the three bounded policies is 1.8 percentage
points; the spread between any bounded policy and keeping everything is 48.2.

So on a scan the eviction policy is not what is losing the hits, and tuning it is tuning the wrong thing.
The fix is a different shape — either bound nothing, or let the caller mark an access as one that will not
be repeated.

## Two levels, and what the second one buys

Caches stack, and the arithmetic of stacking is the reason they do.

An in-process cache in front of a shared one in front of the store. The count is of where each read was
served.

<!--BLOCK:two_levels-->

The first level holds 20 of the 200 keys and the pattern is skewed, so it catches 240 of the 500 reads and
sends 260 to the store. Adding the second level takes the store loads from 260 to 125, which is 2.1 times
fewer, and the second level serves 51.9% of the reads the first level missed.

That is the multiplication this shape is for. The store load rate is the first level's miss rate multiplied
by the second level's, and each level is cheap to size because each one is a count rather than a guess. The
same arithmetic is why a third level stops helping: the second level already caught most of what the first
missed.

The cost is not in the table, and it is the reason to think before adding a level. An entry now exists in
two caches and the store, so an invalidation has to reach all three — and the level easiest to forget is
the one inside the process, because it is the one that lives in the language rather than in a service you
can call.

:::pitfall The cache whose key is different every time

A key is the only part of a cache that can be wrong without anything raising. It has to be hashable, and
that is the only requirement, and it is a very weak one.

Five cache designs over fifty calls that alternate between two arguments. The count is of answers that came
back computed for the wrong arguments, and of entries that can never be found again.

<!--BLOCK:pitfall-->

One of the five answers the wrong question on half the calls, and it is not the one with the worst key.

`how many arguments there are` is the one to look at. Both arguments are one element long, so the key is 1
every time, and the second argument is served the first argument's answer for the rest of the run: 25
answers out of 50 that no cache reports as anything other than a hit.

`the arguments plus a counter` is the opposite failure and it is the one that looks harmless. It is never
wrong, and it holds 50 entries for 50 calls, because every call builds a key that no later call can
produce. That is a memory leak with a hit rate of zero, and it is the reason a cache should be bounded even
when it is correct.

The last row raises `TypeError`, which makes it the only design here that fails loudly. A key has to be
hashable and a list is not, so a mutable argument cannot survive a single call — which makes it the least
dangerous mistake on the list, because it is the only one a test would catch on the first line.

None of the five is separated by a hit count. Two of them answer every call correctly and one of those
never reuses an entry. The column that separates them is the count of answers computed for the wrong
arguments, and no cache reports that column about itself.

:::

:::scenario A read-heavy service with four workers

A service that reads far more than it writes, running four workers, with a cache design to choose. The
count is of store reads, of reads served from a cache, and of stale reads.

<!--BLOCK:scenario-->

The first row is the prize. Reading the store 950 times is what the cache is there to avoid, and everything
below it is a fraction of that.

One cache per worker is the design to look at first, and it fails on both counts. It does 221 store reads
against 95 for a single shared cache, and 199 of its reads returned a value the store no longer had. A
write clears the writing worker's copy and leaves the other three serving the old value, and nothing
raises.

One shared cache is correct and is the cheapest of the four at 95 store reads. Its cost is not in this
table: it throws the whole cache away on every write when one key was what changed, and it is the design
every worker contends on.

The last row is the per-worker design with the invalidation published to every worker. It is correct — zero
stale reads — and it costs 307 store reads, which is 3.2 times the shared cache. Four private copies mean a
write invalidates four entries instead of one, and every worker that held the key has to fetch it again.

So the table argues against private caches rather than for them, and it does so on the count that matters.
The stale version is wrong; the correct version is more expensive than not having private copies at all.
What separates the four rows is not the cache, the key, the size or the eviction policy. It is how many
copies of an entry exist and whether a write reaches all of them.

:::

## Key takeaways

- **A cache is a copy of an answer, so it is a correctness decision before it is a performance one.** Every
  block in this chapter that found a bug found it by counting wrong or stale answers rather than by timing.
- **A cache does not make a function cheaper; it makes a repeat cheaper.** The same function and the same
  cache gave an 82.8% hit rate on one access pattern and 36.6% on another.
- **The misses are the number of distinct keys and nothing else.** 172 distinct keys produced 172 misses;
  634 produced 634.
- **The hit rate is a property of the caller.** It is the first number to count and it is not a number the
  function's author controls.
- **A write has to decide how many places to touch, and that decision is the whole design.** Cache-aside
  did 41 store reads, write-through 16, and write-behind 6 store writes against 40.
- **Write-behind's store traffic depends on how many distinct keys are dirty at once**, not on how many
  writes happened — so it is a property of the workload rather than of the design.
- **Dropping a key on a write costs a store read later.** Cache-aside's invalidation cost it 25 extra store
  reads to re-fetch values it had held.
- **The precise invalidation is the wrong one.** Dropping the three entries the key named left 10 reads
  stale, because a derived value depended on the source without naming it.
- **A reader who looks only at how many entries an invalidation dropped would rank the worst policy as the
  most careful.** Dropping 1 entry left 14 stale reads; dropping 13 left none.
- **A key is a claim about what a value depends on, and invalidation has to reach everything that claim
  covers.** Where the two lists disagree, the difference is measured in stale reads.
- **A TTL is a staleness bound and a tax at the same time.** 5 ticks gave a bound of 4 and 80 loads; 100
  ticks gave a bound of 99 and 4 loads.
- **The staleness bound is one tick below the TTL, always.** It is the number a cache can reason about
  alone, and it is not the number of bad reads a user experiences.
- **The count of stale reads is not a function of the TTL by itself.** It comes from how the TTL falls
  against the source's change period, which the cache does not control.
- **A correct cache is not an efficient one.** Fifty callers arriving together computed the same answer
  fifty times, and a hit rate computed afterwards would not show it.
- **A stampede's cost scales with the number of callers, not with the number of keys.** Protection removed
  49 duplicates over one key and 40 over ten.
- **The key that names less hits more and is wrong more.** Naming the item gave 30 hits and 18 wrong
  answers; naming the type gave 39 hits and 36 wrong answers.
- **A key that is different on every call is a memory leak with a hit rate of zero.** 50 entries for 50
  calls, and never wrong.
- **A key that is not hashable is the safest mistake on the list**, because it fails on the first call
  rather than silently on the hundredth.
- **The work a cache removes is the hit count multiplied by the cost of a miss.** A 90% hit rate over a
  two-unit call removed 180 units; a 40% hit rate over a hundred-unit call removed 4,000.
- **The hit rate is one factor of two and it is the factor the cache can report about itself.** Which is
  why it is the factor that gets optimised.
- **Every bounded eviction policy fails a scan, and the spread between them is 1.8 percentage points.**
  Least recently used, first in first out and random got 0, 0 and 7 hits out of 400; not evicting got 200.
- **The eviction policy is a claim about the access pattern, and a scan is the pattern that makes the
  strongest claim false.**
- **Two levels multiply their miss rates.** A 20-entry first level sent 260 reads to the store; adding a
  second level took that to 125.
- **A second level adds a copy, so an invalidation has to reach one more place** — and the copy inside the
  process is the one that gets forgotten.
- **Private caches are worse than a shared one on both counts.** Per-worker caches did 221 store reads with
  199 stale reads; a shared cache did 95 with none; publishing the invalidation to every worker was correct
  and cost 307.

## Practice

- [ ] **Count the repeats before you write the cache.** Take a function in a project of yours and a log of
  the arguments it is called with. Count the distinct arguments, the calls, and the hit rate that an
  unbounded cache would produce. Then count the cost of one call. Report the hit rate, the work the cache
  would remove, and your verdict on whether it is worth the memory — and say which of those three numbers
  changed your mind.
- [ ] **Measure a stampede you already have.** Find a cached call that can be reached by more than one
  caller at once, or write a loop that simulates several arriving together. Count how many times the
  underlying computation runs when the key is cold, before and after adding per-key protection. Report both
  counts, and say what the largest number of simultaneous callers you expect actually is — because that is
  the number the fix is sized against.
- [ ] **Choose a TTL from a budget rather than from taste.** Take a cached value with a source that changes
  on a known schedule. Write down how many stale reads out of a thousand you are willing to accept, then
  sweep the TTL and find the largest one that meets it. Report the sweep, the TTL you chose, and the worst
  staleness at that setting. Then check whether any TTL you tested divides the source's change period, and
  say why that matters.
- [ ] **Find a key that does not name everything.** Take a cache in your own code and list every input the
  cached value depends on. Compare that list against what the key contains. For each input the key omits,
  construct two calls that produce the same key and different values, and count how many calls would get a
  wrong answer. Report the key you started with, the key you ended with, and the count of entries the wider
  key forces an invalidation to reach.

## Solutions

:::solution Exercise 1

One function, two access logs, a bounded cache, and the three counts that decide: the hit rate, the work
removed, and the entries held.

<!--BLOCK:sol1-->

:::

:::solution Exercise 2

Callers arriving together at cold keys, counted with and without a per-key lock, across five arrival sizes
and two sizes of cold set.

<!--BLOCK:sol2-->

:::

:::solution Exercise 3

A source that changes every thirty-seven ticks, a budget of a hundred stale reads out of a thousand, and a
sweep over thirteen TTLs to find the largest one that meets it.

<!--BLOCK:sol3-->

:::

:::solution Exercise 4

A value derived from two arguments and keyed on one, with the wrong-answer count before and after the key
is widened — and the invalidation the wider key forces.

<!--BLOCK:sol4-->

:::
