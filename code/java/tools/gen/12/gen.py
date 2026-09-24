#!/usr/bin/env python3
"""Generate chapters/12-the-collections-framework.md.

    python3 tools/gen/12/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "12-the-collections-framework.md")

BLOCKS = {
    "listops": gen.run("ListOps.java"),
    "setorders": gen.run("SetOrders.java"),
    "mapops": gen.run("MapOps.java"),
    "navigable": gen.run("Navigable.java"),
    "naturalorder": gen.run("NaturalOrder.java"),
    "comparators": gen.run("Comparators.java"),
    "immutable": gen.run("Immutable.java"),
    "immutableadd": gen.throw("ImmutableAdd.java", "UnsupportedOperationException"),
    "cme": gen.throw("CmeRemove.java", "ConcurrentModificationException"),
    "cmesilent": gen.run("CmeSilent.java"),
    "equality": gen.run("EqualityInSets.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 12
part: 2
title: The Collections Framework
summary: Pick the right container for the question you are actually asking — and let the interface you choose say what you need.
minutes: 60
tags: [collections, List, Set, Map, TreeMap, Comparator, Comparable, iteration, immutability]
---

Chapter 10 was the contract objects must keep. This is the machinery that keeps it for you, and it is
the reason the contract mattered: `List`, `Set` and `Map` are three different *questions* about the
same data, and the collection you pick is a statement about which questions you will ask.

There are two skills here and they are separate. The first is choosing between the interfaces — a
`List` when order and duplicates matter, a `Set` when membership does, a `Map` when you are looking
things up by key. The second is choosing between the *implementations* of the one you picked, because
`HashSet`, `LinkedHashSet` and `TreeSet` all answer "is this in the set?" and differ entirely in what
they do with the order. Most collection bugs are a wrong choice in the second category: the code works,
the tests pass, and the output arrives in an order nobody chose.

## `List`: order, duplicates, and index

@@listops@@

Every method here is the obvious one, and the reason to look at the list as a whole is the last three
lines. A `LinkedList` and an `ArrayList` both implement `List`, so both accept every method in the
table, and `linked.equals(queue)` is `true` — the *contract* is identical.

The difference is hidden behind a marker interface. `ArrayList` implements `RandomAccess` and
`LinkedList` does not, which is a promise about `get(i)`: constant time for one, linear for the other.
Nothing enforces it at the type level; it is a flag that algorithms like `Collections.binarySearch`
read to decide whether to use an index or an iterator.

:::note
Reach for `ArrayList` unless you have measured otherwise. `LinkedList` wins only when you are inserting
and removing at the ends of a very long list, and `ArrayDeque` beats it at that. In practice a
`LinkedList` in application code is almost always a default rather than a decision.
:::

## `Set`: the order question

A `Set` answers "have I seen this?" and the three implementations differ in the order they hand things
back.

@@setorders@@

The input has four elements and three survive, because `apple` arrived twice and a set does not hold
duplicates. That part is the same in all three.

The order is not. `LinkedHashSet` keeps arrival order, `TreeSet` sorts, and `HashSet` — the default,
and the one people reach for without thinking — gives an order derived from `hashCode` and meaningful
to nobody. It is *stable* for a given set of keys, which is what makes the bug so durable: it looks
like a deliberate order because it does not change between runs.

:::pitfall
**A `HashSet` is not "an unordered list" — it is a set with an order you did not choose and cannot
predict from the code.** The moment that order reaches a report, a file or a user, you have a defect
that will survive every test that compares sets rather than sequences. If order matters, say so in the
type: `LinkedHashSet` for arrival, `TreeSet` for sorted.
:::

## `Map`: the methods that remove the boilerplate

A `Map` is a lookup, and the modern API has collapsed the five-line patterns into one call each.

@@mapops@@

`merge` is the counting idiom: `counts.merge(word, 1, Integer::sum)` means "if absent put 1, else
replace with the old value plus 1". `computeIfAbsent` is the grouping idiom, and note the shape — it
returns the value *that is now present*, so `.add(word)` attaches to the list you just created or the
one that was already there. Writing that by hand takes four lines and one of them is usually wrong.

The last four lines are the two ways a missing key behaves, and they are the opposite of each other.
`getOrDefault` gives you a value back; `get` gives you `null`, and `null` is not `0` — `counts.get("zzz")
+ 1` throws a `NullPointerException` while `counts.getOrDefault("zzz", 0) + 1` prints `1`. And
`putIfAbsent` returns the value that was *already there* (`3`), not the one you passed, which is how you
detect that you lost the race.

:::warning
A `Map` with a `null` value and a `Map` with no entry are different, and `get` cannot tell you which you
have. If `null` is a legal value in your map, use `containsKey` — or refuse to store `null` in the first
place, which is the cleaner rule and what `Map.of` enforces.
:::

## `NavigableMap`: the questions a sorted map can answer

`TreeMap` implements `NavigableMap`, and the extra methods are about *neighbours* rather than exact keys.

@@navigable@@

`floorEntry` gives the largest key that is not greater than the one you asked for; `ceilingEntry` gives
the smallest key that is not smaller. `floorEntry(4)` lands on `1=gold` and `ceilingEntry(4)` on
`5=silver`, and when there is nothing above, `ceilingEntry(11)` returns `null` rather than throwing.

This is the shape a tiered pricing table or a rate band wants: you store the *boundaries* and ask
"which band am I in" with one call, instead of looping over a list comparing ranges. `headMap` and
`tailMap` give you views — live views, so a change through either is visible in both.

## `Comparable` and `Comparator` are different jobs

`Comparable` is a property of a type: it says "objects of this class have a natural order". `Comparator`
is a standalone object that says "sort *these* by *this* rule". A class can have only one natural order
and any number of comparators.

@@naturalorder@@

`Version` implements `Comparable<Version>`, so `Collections.sort` works on it, and so do `min`, `max`
and `binarySearch` — all four are written against `Comparable` and get your ordering for free.

The last two lines are the reason the `compareTo` is written the long way. Sorting the same versions
*as text* gives `[1.10, 1.9, 2.10, 2.2]`, because `"1.10" < "1.9"` lexicographically. That is
numerically wrong, and it is exactly what you get if you store a version as a `String` and sort it —
a defect that appears only when a minor version reaches double digits.

When the order is not a property of the type — or when there are several plausible ones — use a
`Comparator`.

@@comparators@@

`Comparator.comparing` builds one from a key extractor; `thenComparing` chains a tie-break; `reversed`
flips it. Read the first two lines together: sorting by age alone and sorting by age *then name* give
the same answer here, because `ada` and `bob` are both 36 and already in that order. The tie-break only
shows itself when the input order disagrees with it, which is why a comparator without a tie-break is a
latent bug rather than a visible one.

`nullsLast` is the piece people miss. A comparator that calls `compareTo` on a `null` key throws, and
the fix is to wrap it: `Comparator.nullsLast(Comparator.naturalOrder())` puts `null` at the end and
never asks it to compare itself.

:::tip
**Always give a sort a total order.** If two elements can compare equal, the sort is free to leave them
in any relative order — and `List.sort` is stable, so it will leave them in the *input* order, which
means your report's layout depends on how the data happened to arrive. Add a tie-break on a unique
field and the output stops being an accident.
:::

## Immutable collections, and the two failures they prevent

`List.of`, `Set.of` and `Map.of` build collections that cannot change.

@@immutable@@

`List.of` and friends are the right default for a value that is handed around: nothing downstream can
add to it, clear it, or sort it in place. They reject `null` outright, which is why `List.of(a, b)` is
a stronger promise than `Arrays.asList(a, b)`.

The last three lines contain a surprise worth knowing. `List.copyOf` returns an *immutable* list, and
if the argument is already one it may return **the same object** — so `alsoCopy != fixed` is `false`.
That is legal because the two are indistinguishable: an immutable object has no identity-dependent
behaviour, so sharing one is safe. Do not write code that depends on `copyOf` returning a fresh
instance.

What happens when you forget they are immutable is worth seeing once.

@@immutableadd@@

`UnsupportedOperationException` from `ImmutableCollections.add`. Note the stack trace: the exception is
thrown inside `add`, at the call site, and it names the line that did it — which is the whole reason an
immutable collection is a *better* failure than a mutable one that quietly changes underneath a caller.

## Iterating and modifying at the same time

This is the collection bug that bites hardest, and it has two faces.

@@cmesilent@@

No exception. The list came out correct. And the loop **examined two of the three elements** — `cal` was
never looked at, because removing `bob` shrank the list while the iterator was still counting, and
`hasNext()` compared a cursor against a size that had just changed.

The output is right by luck. Change one character and it is not.

@@cme@@

Four elements, and now the iterator catches it: `ConcurrentModificationException`. The difference is
that after removing `bob` there is still an element to visit, so `next()` runs its modification check
and fails. **The same bug is silent or fatal depending only on the length of the input**, which is why
this defect ships: it is tested with three items and fails in production with four.

:::danger
**Never modify a collection inside a for-each loop over it.** Use `iterator.remove()`, which is the one
removal the iterator knows about, or `Collection.removeIf`, or build a new collection with a stream
filter. The for-each loop is implemented on an iterator you cannot see, so you cannot tell it what you
did.
:::

## Equality is what makes a set a set

Chapter 10 said collections depend on the `equals`/`hashCode` contract. Here is what it looks like when
the contract is missing.

@@equality@@

`WithoutEquals` inherits identity from `Object`, so two badges with the same `id` are two different
values as far as the set is concerned: `2 entries`, and `contains` answers `false` for an object that
is plainly in there. `WithEquals` is a `record`, so the compiler wrote the pair, and it behaves: `1
entry`, `contains` returns `true`.

Nothing in this chapter works properly without that contract, and nothing warns you when it is absent.
The type system will happily let you put a key into a `HashMap` that can never be found again.

:::scenario The report whose row order nobody chose

A nightly job groups sales by region and prints a summary. The numbers are right. The order is not.

:::solution
The rows come out of a `HashMap`, so their order is derived from `hashCode` and has nothing to do with
the data. It is stable for a given set of keys, which is what makes it look intentional — until a new
region is added and the whole report reshuffles.

@@scenario@@

The three maps hold **identical counts** — the last line confirms it — and they print in three
different orders. `LinkedHashMap` gives `[west, east, north, south]`, which is the order the rows
arrived. `TreeMap` gives `[east, north, south, west]`, which is sorted. `HashMap` gives
`[east, south, north, west]`, which is neither.

Notice what is *not* wrong here. The counts are correct, the code is idiomatic, and no test that
compares maps rather than sequences will ever catch it. The defect is entirely in a choice that was
never made deliberately — `new HashMap<>()` was typed out of habit, and the report inherited an order
from a hash function.

The fix is to decide, and to put the decision in the type: `LinkedHashMap` if the report should read in
arrival order, `TreeMap` if it should be sorted. Either is defensible. `HashMap` is not, because it is
not an answer to the question the report is asking.
:::

## Solutions

### 1. Let the container do the work

@@sol1@@

Two hundred words, twenty distinct. `List.contains` inside a loop asks the question by scanning, so it
cost **2,080** `equals` calls; a `LinkedHashSet` hashes once per word and needs **180**. The ratio grows
with the square of the input, which is the difference between a helper that is fine in a test and one
that is not fine in a job.

Both answers are identical — `and both kept arrival order: true` — so this is a pure cost change with no
behavioural risk. That is the easiest kind of improvement to make and the easiest to skip, because
nothing is visibly broken.

The counting is done by a static counter inside `Word.equals`, which is worth noticing as a technique:
to find out how many comparisons an algorithm makes, put the counter in the object being compared, not
in the algorithm.

### 2. Make the sort a total order

@@sol2@@

Sorting by score alone puts the three 90s in `[eve, ada, cal]` — the order they arrived, because
`List.sort` is stable. Adding `thenComparing(Entry::name)` gives `[ada, cal, eve]`. The tied group is
the same three people either way, and the order inside it is the difference between a report that is
reproducible and one that depends on the input order.

The tie-break costs one line and removes an entire class of "it looked different yesterday" bug.

### 3. Build the report you actually want to read

@@sol3@@

`TreeMap` for the outer map makes the regions sorted; a second `TreeMap` inside makes the products
sorted within each region; `merge` accumulates and `computeIfAbsent` groups. The result prints in an
order that a reader can predict, and the last line is the check that matters — the parts sum to the
whole, so the grouping has not lost anything.

That check is worth writing even in throwaway code. Grouping bugs are silent: a `merge` with the wrong
key, or a `computeIfAbsent` whose function returns a shared list, produces a report that looks plausible
and totals wrong.

### 4. Remove without breaking the loop

@@sol4@@

`removeIf` is the one-liner, and `iterator.remove()` is what it does underneath — that is why both give
`[ada, cal]`. The iterator's `remove` is the only modification the iteration machinery knows to expect,
which is exactly what the for-each loop cannot give you.

The stream version is a third option and it is the safest of the three: `filter` builds a *new* list and
leaves the original untouched (`[ada, bob, cal, ben]`). When you are unsure whether something else holds
a reference to the collection, prefer producing a new one over mutating the old one — the class of bug
in the previous section cannot happen if nothing is being modified.

:::tip
Choose by what the caller expects. `removeIf` when the collection is yours and the mutation is the
point; a `filter` into a new list when the value might be shared. `iterator.remove()` when you need to
do something more complex per element than a predicate can express.
:::

## Key takeaways

- `List`, `Set` and `Map` are three questions about the same data. Pick the interface by the question,
  then the implementation by the order you need.
- `ArrayList` and `LinkedList` satisfy the same `List` contract and differ in `get(i)` cost;
  `RandomAccess` is the marker interface that tells an algorithm which it has.
- `HashSet` has an order derived from `hashCode` and meaningless to a reader. It is stable for a given
  set of keys, which is why the bug survives testing. Use `LinkedHashSet` or `TreeSet` when order
  matters.
- `merge`, `computeIfAbsent`, `getOrDefault` and `putIfAbsent` replace the boilerplate patterns, and
  `putIfAbsent` returns the value that was *already there*.
- `NavigableMap` answers neighbour questions — `floorEntry`, `ceilingEntry`, `headMap`, `tailMap` — and
  is the right shape for bands and tiers.
- `Comparable` is a property of the type; `Comparator` is a separate object. Give every sort a total
  order with a tie-break on a unique field, or its output depends on the input order.
- `List.of`, `Set.of` and `Map.of` are immutable and reject `null`. `List.copyOf` may return the same
  instance you passed in, so do not depend on it copying.
- Modifying a collection inside a for-each loop is silent with three elements and fatal with four. Use
  `removeIf`, `iterator.remove()`, or a stream that builds a new collection.
- A `HashSet` of objects without `equals` holds every one of them. The contract from Chapter 10 is what
  makes every collection in this chapter work.

## Practice

- [ ] Build a word-frequency report from a paragraph twice: once with `HashMap`, once with `TreeMap`.
      Write down which one you would ship and why.
- [ ] Store a version as a `String` and sort it. Find the smallest input that comes out wrong, then fix
      it with a `Comparable` type.
- [ ] Write a `Comparator<Person>` that sorts by last name, then first name, then date of birth. Say
      which of the three is the tie-break and which are the keys.
- [ ] Implement a rate band with a `NavigableMap<Integer, Double>` keyed by threshold, and find the band
      for a value with one call. Then do it with a `List` and a loop, and count the comparisons.
- [ ] Take the `CmeSilent` program and add a fourth name. Explain the two different outcomes from the
      length of the list alone.
- [ ] Write a method that returns `List.copyOf(input)`, then prove by reflection or identity that it
      sometimes returns its argument.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `TreeMap` for anything a human reads, because sorted output is reproducible and diffable. `HashMap`
   only when the map is never iterated — a pure lookup table.
2. Two versions where the text order differs from the numeric order, for example `1.9` and `1.10`.
   Sorting as text gives `1.10` first, which is numerically wrong.
3. Keys: last name, then first name. Tie-break: date of birth, which is unique in practice. A tie-break
   that is not unique leaves the order to the input.
4. `bands.floorEntry(value)` returns the whole band in one lookup. The `List` version scans every
   threshold, which is O(n) per lookup and O(n·m) for m lookups.
5. With three names the loop silently ends early after the removal; with four, `next()` runs its
   modification check and throws `ConcurrentModificationException`. Same bug, different input length.
6. `List.copyOf(listOfAB) == listOfAB` is `true`, because an immutable list has no identity-dependent
   behaviour and can safely be shared.
"""

gen.write(TEMPLATE, BLOCKS)
