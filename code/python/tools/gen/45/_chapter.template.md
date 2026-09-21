---
chapter: 45
part: 8
title: Core Data Structures
summary: Choose a data structure on evidence rather than habit. Build the classic structures by hand -- dynamic array, linked list, stack, deque, hash table, heap, balanced tree, trie -- and state the cost of every operation before you use it.
minutes: 90
tags: [data structures, dynamic array, linked list, hash table, heap, deque, trie, balanced tree, bisect]
---

Chapter 44 gave you the cost model. This chapter spends it.

Every container in the standard library is a bundle of promises about cost, and the promises differ.
A `list` reads any slot in one step and inserts at the front in n. A `deque` does the opposite. A
`dict` finds a key without looking at the other keys, and keeps nothing in order. A heap tells you
the smallest item and refuses to tell you the second smallest. None of these is better than the
others; they are answers to different questions.

The way to see that is to build them. So this chapter writes a linked list, a hash table, an AVL
tree and a trie from scratch -- not because you should use them, but because the standard library
versions are opaque, and opaque things get chosen by habit. Once you have counted the steps inside
your own hash table, `dict` stops being magic and becomes a decision you can defend.

There is one rule throughout. Before each structure, the cost of every operation is **stated**.
Then it is **measured** -- counted where counting is possible, timed where it is not -- and the two
are compared. Where they disagree, the measurement wins.

## The same interface, three costs

A queue is the simplest interface there is: put things in one end, take them out the other. Nothing
in that sentence says *how*, and that is where the trouble starts, because `list` has a method that
looks like a dequeue and is not one.

<<BLOCK:queues>>

The two right-hand columns answer different questions, and keeping them apart is most of the skill.
The shift count is exact: it follows from the algorithm and is the same on your machine. The
doubling column is this machine on this run, which is why it is a band rather than a figure.

Read them together and the choice stops being a matter of taste. The `pop(0)` version does n(n-1)/2
shifts, and its cost **quadruples** when n doubles. The other two do no shifting at all and merely
double. That is a difference in growth rate, and no amount of tuning a constant factor will close
it.

The middle row is the interesting one, because it is a trap rather than a solution. Keeping a head
index does make dequeueing cheap, and it is the fix people reach for when they notice the problem
in a profiler. It does not reclaim anything: the list still holds every slot it ever allocated, so
a long-running service grows without bound while its queue looks empty. The structure that is
actually right is `deque`, and it is right because of its layout rather than its method names.

## The dynamic array: reading is arithmetic

Before the trade, the half of it that is easy to forget. Reading a slot in a list is not a search,
and the reason is worth seeing once.

<<BLOCK:index_cost>>

Four indices, four different addresses, identical work. There is no loop and no comparison anywhere
in that computation -- which is the whole explanation of why indexing is O(1), and why the O(1)
holds for the last slot exactly as much as for the first.

The measurement underneath is a control, not evidence. Three traversal orders give identical totals
because the total is a property of the data; the *band* is what rules out a hidden search. If
indexing had to walk to its slot, the middle-out walk would have been the one that noticed.

## The dynamic array: writing is not

Reading is O(1) for every index. Writing is not, and the asymmetry is the single most useful thing
to know about a list.

<<BLOCK:insert_where>>

There is no stopwatch in that table, and that is deliberate. The cost here is a `memmove`, and a
`memmove` is so fast per byte that a 200-iteration loop cannot see it -- the Python-level loop
overhead swamps it. Counting the bytes is both easier and more honest.

The formula is `k*n + k(k-1)/2` with k = 200. The `k*n` term dominates, so the cost is proportional
to how long the list already was, not to how many items you are adding. The loop runs 200 times at
every size, and it gets two hundred times more expensive. That is the shape of a production
incident, and it is why the rule is not "lists are slow" but "a list is O(1) at the end and O(n) at
the front".

:::pitfall `insert(0, x)` in a loop reads like a one-line operation
`buf.insert(0, item)` is a single method call, it returns `None`, and it does not look expensive.
It is O(n) in the current length of the buffer, so a loop that prepends m items to an n-item list
is O(m*n) -- quadratic, wearing the costume of a constant-time call. The fix is never to optimise
the loop. It is to use a `deque`, which has `appendleft`, or to append and reverse once at the end,
which is O(n) total.
:::

## The linked list: what O(1) insertion costs elsewhere

A list is a contiguous array. The alternative is a chain of nodes, each one holding a value and a
pointer to the next. It is worth writing once, because the trade it makes is sharper than the one a
list makes, and it is the trade that half the structures later in this chapter are built on.

<<BLOCK:linked_list>>

The hops column is the cost, and it is not a defect. Reading the head is free, the middle is n/2
steps, the tail is n steps. The array did all three in one multiply. This is the trade, and it is
worth stating in both directions: the linked list is *worse* at reading and *better* at splicing.

`push_front` is one pointer write at any length, which is the entire reason anyone writes a linked
list. Note the qualifier, though, because it is where people go wrong. `push_front` is cheap because
the head is a field on the object you already hold. Inserting after a node in the middle is also
O(1) -- but *finding* that node is the n/2 walk from the table above, and that walk is not free.
An O(1) insertion you cannot locate is not an O(1) operation.

The `__len__` note at the end is the same lesson at a smaller scale. Every real linked list stores
its size in a field, because the alternative is that `len(x)` walks the chain and every
`if len(x) > 0` in the codebase becomes O(n) while looking like O(1). Cost hides behind interfaces
that read as cheap.

## Stacks: a discipline, not a class

There is no `Stack` in the standard library, and there should not be. A stack is a list you have
agreed to use in one way: append and pop, never index. The interest is not the container, it is
what the discipline lets you compute.

<<BLOCK:stack>>

Row 2 is the whole point. `([)]` has two opening brackets and two closing brackets, so a counter
says balanced. It is not balanced, and a parser that believes the counter builds a tree with the
wrong shape -- or, more often, does not notice until a much later stage does something strange and
the stack trace points at the wrong file.

The stack gets it right because it stores the *order*. Popping returns the bracket you are inside,
so `stack.pop() != PAIRS[char]` is a comparison a pair of integers cannot express. That is the
general lesson: when the correctness of an algorithm depends on nesting or history, the container
has to hold the history, not a summary of it. Chapter 48 meets this again when recursion does the
same job with the call stack instead of a list.

`max_depth` is not decoration either. It is the number you want before you feed a parser a file you
did not write: an input nested 50,000 deep will not trouble this list, but it will overflow the
recursive version, and measuring depth is how you find out which one you have before production
does.

## Queues and `deque`: two ends, and a middle

`deque` is the right answer to the queue problem, and it is not a drop-in replacement for a list.
Knowing exactly what it gave up is what stops you from making things slower with it.

<<BLOCK:deque_features>>

The measurement is blunt: the middle of a deque is a thousand times slower than either end. That is
not a wart, it is the price of the layout. A deque is a doubly linked list of fixed-size blocks, so
reaching index n/2 means walking the block chain -- and CPython walks from whichever end is nearer,
which is why the right end and its neighbours are as fast as the left.

So the rule is about access pattern, not about which container is "faster". Swap a list for a deque
because you push and pop at the ends. If your code does `items[i]` in a loop, a deque makes it
worse, and the profiler will not explain why.

What you get in exchange is a ring buffer, and a ring buffer has a property a list cannot imitate: a
fixed maximum length. `deque(maxlen=5)` drops the item at the far end when it fills, in O(1), with
no eviction code. The list equivalent is `buf.append(x); del buf[:-5]`, which is correct, which
everyone eventually forgets to write, and which leaves an unbounded buffer when they do.

## A hash table, written by hand

This is the structure people treat as magic, and it is the one where the magic turns out to be
somewhere unexpected. Twenty lines of Python is enough to see why `dict` is O(1) -- and why that
claim has a precondition.

<<BLOCK:hash_table>>

Read the first row against the third. `len(key)` is a perfectly deterministic function of the key,
and it is useless: every key in this set has length 8, so every key lands in bucket 8 and the table
is a linked list wearing a hat. A mean lookup compares five hundred keys.

`sum(ord(c))` is the row worth pausing on. It is not *wrong* -- it separates different keys, so
every key is findable. It is merely weak: the sums cluster in a narrow band, and after `% 256` the
keys pile into a few buckets. A weak hash does not produce incorrect answers. It produces a table
that is quietly slow, which is worse, because nothing fails.

So the answer to "why is `dict` O(1)?" is not the table. The table is twenty lines. The O(1) comes
from the hash function scattering the keys, and from resizing before the chains get long. Both
halves matter, and the second one is a number.

<<BLOCK:hash_growth>>

The fixed-capacity table is a set of linked lists, and the arithmetic is worth doing once: with c
buckets and n keys, insert number i finds about i/c keys already in its chain, so the total is
roughly n²/(2c). For n = 2,000 and c = 8 that predicts 250,000, and the table reports 249,019. The
resize column is what prevents it -- seven doublings, and the per-insert cost stays flat.

The doubling table is the growth-rate test from Chapter 44 applied to a container rather than a
loop. The growing column roughly doubles; the fixed column multiplies by four. Same code, same
keys, same hash function, one boolean in the constructor.

The last table is a deliberate disappointment. A `dict` will not tell you how many comparisons it
made, and there is nothing in Python to count -- the chains are arrays of indices inside a C struct,
the hash is cached in the entry, and a probe is a memory read rather than a method call. So the
honest question is not "which is faster" but "which complexity did you choose", and the answer is
identical for both. Use `dict`. Write one once, so you know what you are using.

## Hashes are salted, and that is a feature

One more thing about hashing that you will meet as a bug report rather than a lesson, usually in the
form of "the same script printed a different order today".

<<BLOCK:hash_seed>>

Two runs of the identical program, and the keys land in different buckets, because CPython picks a
random salt at startup and mixes it into the hash of every `str` and `bytes` object. Hash values are
not reproducible across processes, and no amount of testing will make them so.

The harmless consequence is that iterating a `set` of strings gives a different order in a different
process. `set` iteration order was never a promise; this is the mechanism behind that. `dict`s are
unaffected, because insertion order has been a language guarantee since 3.7 -- a guarantee about
dicts, not a property of hashing.

The consequence that matters is security. Without the salt, an attacker who knows the hash function
can choose keys that all collide, and a dict lookup becomes a linear scan. That is hash flooding, and
it turns a JSON request body into a denial of service. The salt is the fix, and it is on by default.
Chapter 52 returns to this when it covers untrusted input; for now the point is that `hash()` is not
a pure function of its argument, and code that assumes it is has a latent bug.

## Heaps: a structure that answers one question

A heap is the clearest example in the chapter of a structure that is not a general container. It
answers exactly one question, and it answers it faster than anything that answers more.

<<BLOCK:heap>>

Every comparison a heap makes goes through `<` on the objects it holds, which is what makes this
countable. Wrapping the values in a class with a counting `__lt__` turns the algorithm into a number
-- the same number on every machine, in every run.

Sorting compares about twelve times per item, which is log2(10,000) with Timsort's constant folded
in. `heapify` compares under two, because it is O(n) rather than O(n log n): it sifts down from the
middle rather than pushing from the left, and most of the nodes are near the bottom where a sift is
short. Popping every item is O(log n) each, which is why heap sort costs what a sort costs -- and why
a heap built by pushing one item at a time is worse than `heapify` on the same data.

Then the part that surprises people. The heap array is not sorted. Only the root is guaranteed; the
array satisfies `parent <= both children` at every position and nothing else. That is exactly enough
to answer "what is the smallest?" in O(1) and to remove it in O(log n), and not enough to answer
anything else -- you cannot ask for the second smallest without popping the first.

:::tip `heapq` is a min-heap, and the tuple is how you control the order
There is no max-heap in the standard library. For numbers you negate the key. For anything else you
push a tuple and let the comparison stop at the first field that differs -- `(priority, sequence,
item)`, where `sequence` is a counter that makes the order total. Without that middle field, two
items with equal priority make the heap compare the items themselves, and if they are not orderable
you get a `TypeError` from deep inside `heapq` rather than from your code.
:::

## Ordered keys: `bisect`, and the tree it does not replace

Everything so far either keeps no order or keeps a weak one. Keeping full order is the expensive
promise, and the standard library gives you one half of it.

<<BLOCK:bisect_cost>>

Two rows, the same sorted list at the end, and a twenty-one-million-slot difference in how it got
there. The shift column is the one to trust; the measured column is a band because it is this
machine on this run.

This is not an argument against `bisect`, and the second table says why. Ten million items, twenty-
three probes, against five million for a scan. That is log n against n, and nothing else in the
standard library comes close for the question "where would this value go?". The rule has two halves
that point in opposite directions: **bisect to find**, and **do not insort in bulk**.

If keys arrive one at a time and the order must hold after every one of them, a sorted list is the
wrong structure, and no amount of `bisect` fixes that. You want a balanced tree. So let us build
one, and let the log n claim stop being something you take on faith.

<<BLOCK:avl>>

Thirteen visits per insert against a log2(20,000) of 14.3 -- the tree is behaving like a perfectly
balanced one, and the height column is the proof it is not luck. An unbalanced tree built from
ascending keys would be 19,999 levels tall, and the visits to build it would be in the hundreds of
millions. The rotations are what buy that, and there are 9,377 of them.

Now the three structures can be compared on one job -- keep 20,000 keys available while 2,000 more
arrive -- and the comparison is not a ranking. The tree is the only one that is logarithmic for both
operations *and* keeps the keys in order. The dict is faster at both and keeps nothing in order. The
sorted list searches fastest and maintains worst.

Which you want is decided by the question you are actually asking. If you never need "the keys
between 40 and 60", the dict wins and the tree is a hundred lines of code you did not need. That is
why Python has no sorted mapping in the standard library: most code that reaches for one only needed
a dict, or a sort at the end. When you do need one, `sortedcontainers` is a third-party package and
that is a deliberate boundary rather than an omission.

## Tries: when the key is a string

The last structure in the chapter is the one that shows a dict is not the only way to store keys --
and that which key operation you need decides the structure, not the other way round.

<<BLOCK:trie>>

Both columns find the same words. The scan pays for every word in the vocabulary; the trie pays for
the prefix plus the answers. Watch the two columns as the prefix changes: the trie's cost follows the
size of the answer, and the scan's does not move.

That is the property a dict cannot offer. You could precompute `{'ab': [...]}`, and it would answer
this one query in a single hash -- and it would be wrong the moment the vocabulary grows, because
every prefix has to be enumerated in advance. A trie derives the answer from the words themselves.

The cost is memory and nothing else: 2,731 nodes for 2,028 words, each node holding a dict of its
own. For an autocomplete over a million words that is hundreds of megabytes, and the production
answer is a compressed trie or a sorted array with two `bisect` calls -- which is the same trade the
whole chapter keeps making. The fastest structure for the query you have, at the memory you are
willing to pay.

## Choosing, on evidence

One problem, solved with everything above, counted. "Find the ten most common words" is the smallest
problem that needs two structures in sequence: a hash table to count, and something ordered to rank.
The counting is a dict and is not interesting. The ranking is where the choice lives.

<<BLOCK:topk>>

All three approaches return the same ten words. Sorting compares about eleven times per word,
because it is answering a question nobody asked: the full order of 5,000 words. The heap answers only
the question that was asked, in one comparison per word, because the heap is never larger than ten
and almost every word loses to its smallest member on the first try. A factor of ten, for the same
answer, from a different structure.

That is the chapter in one table. A data structure is not a container you pick by habit; it is the
shape of the question you are asking, and picking the wrong one means paying for answers you throw
away.

:::scenario The recent-events buffer that ate the worker
A log-processing service keeps the last 100 events in memory so the `/status` endpoint can show
recent activity. The first version was written in a hurry:

```python
recent = []

def record(event):
    recent.insert(0, event)
    del recent[100:]
```

It passed every test, because every test recorded a handful of events. In production it recorded
200,000 a day, and the worker's CPU time went up until the container was throttled. Nothing was
wrong in the sense of being incorrect -- the buffer held the right 100 events in the right order --
and the profiler pointed at `record`, which is one `insert` and one `del`.

The other version of this bug is worse. Somebody "fixes" the cost by dropping the `del` line, the
buffer becomes unbounded, and the service now leaks about a hundred megabytes a day. Neither version
is a performance problem in the usual sense; both are the wrong structure for the question.

Here is the cost, counted:

<<BLOCK:scenario>>
:::

:::solution The fix
The question is "the last N things", which is a ring buffer, and the standard library has one.

```python
from collections import deque

recent = deque(maxlen=100)

def record(event):
    recent.appendleft(event)
```

Both costs disappear at once, and for different reasons. `appendleft` writes into a slot that
already exists rather than shifting the buffer, so it is O(1). `maxlen` drops the item at the far
end automatically, so there is no eviction line to forget and no way for the buffer to grow.

The counts from the demo above make the first half concrete: 39,984,950 slot moves become zero. The
second half does not show up in a benchmark at all, and it is the more valuable half -- the memory
bound is now a property of the object rather than a statement somebody has to remember to write.
:::

## Key takeaways

- A container is a set of cost promises, not a bag of methods. A list is O(1) to read at any index
  and O(n) to insert at the front; a `deque` is O(1) at both ends and O(n) to read in the middle.
  Neither is "faster".
- State the cost before you measure it. The shift counts and comparison counts in this chapter are
  exact and identical on every machine; timings are a property of the machine and belong in bands.
- `list.pop(0)` and `list.insert(0, x)` are both O(n) and both look like O(1). Use `deque` when the
  ends are where the traffic is.
- A hash table's O(1) comes from the hash function spreading the keys and from resizing before the
  chains get long. Change either one and you get a linked list with extra steps.
- `hash()` of a string is salted per process. That is why `set` iteration order varies between runs,
  and it is what stops hash-flooding attacks. Never depend on a hash value.
- A heap answers one question -- the minimum -- in O(1) to read and O(log n) to change, and it is not
  sorted. `heapify` is O(n); pushing n items one at a time is O(n log n).
- `bisect` finds in O(log n) and `insort` inserts in O(n), because a list is an array. Find with
  `bisect`; do not maintain a sorted list one insert at a time.
- A trie costs memory and buys prefix queries a dict cannot answer. A balanced tree costs code and
  buys order plus logarithmic updates. The question you are asking picks the structure.

## Practice

- [ ] Build a `MinStack` that supports `push`, `pop` and `minimum`, all in O(1), and check its
  `minimum()` against a full rescan of the stack after every push.
- [ ] Write `merge_sorted(lists)` that merges k sorted lists into one, using a heap that never holds
  more than k items. Compare its output against a plain `sorted()` over everything.
- [ ] Build an `LRUCache` with a size limit, using a `dict` and a doubly linked list. Show the cache
  contents in most-recently-used order after a scripted sequence of `get` and `put` calls.
- [ ] Write `longest_common_prefix(words)` using a trie, and a second version that compares the
  words directly. Check that they agree on a single word, on a set with no shared first character,
  and on repeated words.
- [ ] Write an open-addressed hash table with linear probing. Measure the mean probes per lookup at
  load factors from 0.12 to 0.98, and demonstrate the deletion bug that clearing a slot causes.

## Solutions

:::solution Exercise 1
The trick is a second stack holding the minimum *as it was at each depth*. Each entry is only valid
while the stack is that tall, which is exactly what a stack gives you for free.

<<BLOCK:sol1>>
:::

:::solution Exercise 2
Put the head of each list in a heap. Take the smallest, then push the next item from the list it came
from. The heap never holds more than k items, so every step costs log k rather than log of the total.

<<BLOCK:sol2>>
:::

:::solution Exercise 3
A dict for the lookup, a doubly linked list for the order. Neither one alone can do both jobs: the
dict cannot tell you the oldest key without scanning, and the list cannot find a key without walking.

<<BLOCK:sol3>>
:::

:::solution Exercise 4
Walk down the trie while there is exactly one way to go and no word has ended. Both conditions
matter: a word ending here means it is itself the common prefix, and two children means the paths
have diverged.

<<BLOCK:sol4>>
:::

:::solution Exercise 5
Chaining puts several keys in one bucket; open addressing puts one key per slot and probes forward
when the slot is taken. The probe counts show where "expected O(1)" stops being true, and the
deletion case shows why a sentinel is required.

<<BLOCK:sol5>>
:::
