---
chapter: 48
part: 8
title: Recursion, Memoisation and Dynamic Programming
summary: A recurrence is a description, not an algorithm. Count the recursion tree, find the overlap, and the same description becomes a table -- with edit distance, knapsack and coin change worked out in full, and every cost counted rather than timed.
minutes: 115
tags: [dynamic programming, memoisation, lru_cache, edit distance, LCS, knapsack, coin change, recursion, complexity]
---

Chapter 47 was about graphs you can draw. This chapter is about graphs you cannot: the state space
of a recurrence, where the nodes are subproblems and the edges are the recursive calls. Once you see
that, the previous chapter's algorithms and this chapter's are the same algorithms -- Dijkstra is a
dynamic program on a weighted graph, and the coin-change recurrence at the end of this chapter is
Dijkstra with every edge of weight one.

The chapter starts with a function that is three lines long and would take tens of thousands of years
to run at n = 100, and it ends with the same function running in a few hundred operations. Nothing
about the *problem* changes between those two points. What changes is what the function remembers.

The discipline is the one Chapters 44 to 47 established, and it matters more here than anywhere
else so far. **Every cost in this chapter is an exact count** -- of function entries, table cells,
relaxations, look-backs -- and not one of them is a stopwatch reading. That is not fussiness. A DP
is a claim about how many *distinct* things need computing, and the only way to check that claim is
to count them.

## The recursion tree, counted

Start with the standard example, because it is standard for a reason: the blow-up is visible without
any instrumentation at all.

<<BLOCK:recursion_tree>>

Two claims in that output are worth pulling apart, because they are the two halves of the whole
chapter.

The first is the `calls/2^n` column. It does not settle at a constant, and the obvious reading --
"the count is 2^n up to a constant factor" -- is wrong. It shrinks by a constant *factor* every time
n goes up by one, because the count grows like φ^n while 2^n grows like 2^n. The two differ by a
constant inside the exponent, which is exactly what it means for two exponentials to have the same
growth rate: **O(2^n) and O(φ^n) name the same class**, and the constant in front of them is not
the interesting part.

The step-factor table pins that down to four decimal places, and it is the reason the check is on
the *ratio of ratios* rather than on any single value. φ is irrational, so no run will ever print
it; but (φ/2)^5 is a clean number, it is the same on every machine, and the table converges on it
while the error falls by a factor of about eleven every five units of n. The first two rows are the
ones that lie -- at n = 10 and n = 15 the correction terms in Binet's formula are still comparable
to the leading one. That pattern, where the smallest inputs are the ones that mislead, recurs
everywhere counts are used to justify a claim about growth.

The second claim is the `reuse` column, and it is the one that makes the fix obvious. At n = 30 the
function is entered 2,692,537 times to compute 31 distinct values. The tree is not doing 2,692,537
different things. It is doing 31 different things over and over.

That is what "overlapping subproblems" means, and it is worth stating precisely because the phrase
gets used loosely. It does not mean the problem has a recursive definition -- everything recursive
does. It means **the recursion tree contains the same node many times**.

The closed-form check at the end is not decoration. `2*F(n+1) - 1` holds for every row, and the
reason is that the count satisfies the same recurrence as the value, one step ahead of it. When a
count and the thing being counted share a recurrence, that is usually a sign you have found the
right count rather than a coincidence.

## Two questions, and the ratio that answers both

The phrase "dynamic programming applies" is a claim about a recurrence, and claims should be
testable. There are two questions, and both are answerable by counting before you write any code.

<<BLOCK:overlap>>

The overlap column is the test. A value of 1 means every call is a subproblem nobody has asked about
before -- there is nothing to cache, and a memo dictionary would cost memory and lookups for zero
saving.

Merge sort is the clean example of that failure, and it is worth being precise about *why* it has no
overlap: its subproblems are **disjoint**. The left half and the right half share no elements, so
"sort the left half" and "sort the right half" are genuinely different jobs that happen to look
alike. Overlapping subproblems means the same input appears in more than one branch of the tree,
which is a property of the recurrence and not of the implementation.

Binary search is the same failure at a smaller scale, and it adds a detail worth noticing: it
recurses into one side only, so its recursion tree is a line rather than a bush -- and a line has no
repeats by construction.

So the two conditions are:

1. the number of distinct subproblems is polynomial in the input
2. the naive recursion asks for them an exponential number of times

Both are needed, and they are independent. A recursion with exponentially many distinct subproblems
cannot be memoised into anything useful, because the cache itself becomes the exponential object. A
recursion with no overlap has nothing to reuse. Exercise 2 takes those two failures apart with one
example each.

That is also why "dynamic programming" describes a **shape** of problem rather than a technique to
apply. The counting tells you whether the shape is there before you write any of it.

## Remembering an answer

Memoisation is one idea: remember the answer to a subproblem you have already solved. It can be
written by hand with a dict or supplied by the standard library, and those look like two techniques
and are the same algorithm.

<<BLOCK:memo>>

The `entries` column is the only fair comparison in the table, and it is worth saying why the other
columns are not. A cache's `hits` and `currsize` are properties of the cache; the number of times a
function is *entered* is a property of the algorithm. The naive version enters the function
2,692,537 times and both cached versions enter it 59 times -- once per distinct subproblem, plus one
lookup per repeat. The tree did not get smaller. It stopped being built.

The two small differences between the hand-rolled row and the library row are worth reading
carefully, because they come from one line of code and they are the kind of thing that gets
mysterious in a code review. The hand-rolled version checks `n < 2` and returns **before** it
consults the dictionary, so its base cases are never looked up and never stored. Hence one fewer hit
and two fewer entries. Neither is a bug: the cache check costs a dictionary lookup, so
short-circuiting the trivial cases first is usually right -- but it means the cache's own statistics
no longer count every repeat.

The last section turns the two documented traps into output rather than advice. `maxsize=None` means
*unbounded*, and an unbounded cache on a function with many distinct arguments is a memory leak with
a friendly name -- harmless on `fib`, a bug on `fetch_user(user_id)`. And the hashability failure
appears at the **call site** rather than at the definition, so a function that works on a tuple and
fails on a list is the symptom to recognise.

The bounded-cache demonstration is the one to keep. After ten distinct arguments a
`maxsize=4` cache holds four entries, and asking for the *first* argument again is a **miss**. That
is eviction working, quietly, with no error and a correct answer. A bounded cache turns a leak into
a policy, and the policy is the thing you are choosing.

## Two directions, and a hard ceiling

The same recurrence can be filled from the answer downwards or from the base cases upwards. They
fill the same table, and the counts show where each one wins.

<<BLOCK:topdown_vs_bottomup>>

Part 1 is the part that surprises people. Top-down works at n = 500 and raises `RecursionError` at
n = 1,000, with no change to the recurrence at all. Bottom-up does not care how large n gets,
because it never recurses -- there is no stack to overflow.

The exact n where top-down breaks is deliberately not pinned down. It depends on how many frames the
interpreter had already used before the call, which is not a property of the algorithm and not
stable across versions. What *is* a property of the algorithm is the shape: the depth grows linearly
with n, so the limit is a hard ceiling on n. Reporting the shape and refusing to report the boundary
is the right call, and it is the same discipline as refusing to report a timing.

Part 2 is the trap. `sys.setrecursionlimit` looks like the fix and it is not: what it changes is a
*counter* that CPython checks on entry to each frame. It does not make the real call stack any
larger. Set it high enough and a recursion that would have raised a catchable exception instead runs
off the end of the actual stack and takes the interpreter down -- no exception, no traceback, no
chance to log anything. So the limit belongs in the decision about how to write the recurrence, not
in a startup line.

Part 3 reverses the conclusion, and the sweep is the interesting part. With almost no walls,
top-down saves nothing -- because with no walls every cell lies on some route to the corner, so the
states the answer depends on *are* the whole grid. As walls go in, the reachable set shrinks faster
than the grid does and the gap opens up.

Then look at the bottom of the table, where the route count goes to zero. The saving keeps climbing
-- 15x, then 36x -- and it is climbing for the worst possible reason. Once the walls seal the corner
off, the recursion unwinds immediately, explores a few dozen cells, finds nothing and returns 0.
**The ratio is largest exactly where the search is doing no work at all.**

That is worth keeping as a habit. A count is only a measure of something when the two runs are
computing the same non-trivial thing. This table is built so that the answer is checkable in every
row, which is why the zero is visible at all -- a benchmark that reported only the ratio would have
ranked the failed searches first.

## Edit distance

Fibonacci shows the mechanism. Edit distance shows the **shape**: the state is a pair of positions,
so the table is two-dimensional, and every cell is a choice between three moves. It is also the
recurrence behind every spell checker and every `diff`.

<<BLOCK:edit_distance>>

The table is the recurrence, and reading it is mostly a matter of reading the base cases correctly.
The top row and the left column are not special cases bolted on -- they are the answer to "what does
it cost to turn this into nothing", which is one deletion per character. Turning `kitten` into the
empty string is six deletions, so the left column counts up from 0 to 6, and that is the recurrence
applied to an empty second string rather than an exception to it.

The bottom-right cell is the answer and everything else was computed to get there -- 56 cells, of
which 55 exist only to support the one in the corner. That is the trade the earlier sections were
about, stated in one line.

Part 2 is where the counting pays off, and the growth rate has a surprise in it. Three branches per
node suggests 3^n, and that is wrong, for a reason worth working out: the three calls move to
`(i-1, j)`, `(i, j-1)` and `(i-1, j-1)`, so they step in **two dimensions** rather than one. The
count is therefore a count of paths through a grid, not of levels of a tree, and paths through a
grid grow faster than the branching factor suggests -- 3 + 2√2, which is about 5.83. The growth
column is still climbing toward it at n = 8, because the convergence is slow, exactly as it was for
φ in the first section.

The distinct column is the other half: 398,593 calls to do 81 different things. The table is just
the set of distinct answers, computed once each.

Part 3 is the traceback, and it is why the table is worth keeping. The recurrence gives you the
*cost* in the corner; the table gives you the *operations*, by walking backwards and re-deriving at
each cell which of the three moves the minimum came from. Note that the walk has to test the moves
in a fixed order and that the order is a choice -- two different optimal edit scripts can have the
same total cost, which is the same tie-breaking question that came up for A\* in the previous
chapter.

## What the state has to remember

Longest common subsequence is the sibling of edit distance: the same two-dimensional table, a
different recurrence. It is worth doing both because the *difference* between them is where the
design work is -- and because LCS is the algorithm inside `diff`.

<<BLOCK:lcs>>

The equal case of the recurrence is not a `max` -- it is forced. If the two characters match, there
is always an optimal solution that uses them, so the cell is the diagonal plus one and the other two
candidates are irrelevant. The unequal case is where the choice lives. That is the difference
between an edit and a match expressed as a recurrence: editing costs one operation, matching costs
nothing and gains a character.

Part 2 is the part that is usually skipped and should not be. This problem has a **tie in its
statement**, so any implementation has to break it somewhere, and the three distinct answers here
are all correct. `all_lcs` breaks the tie by taking both branches when the two neighbours are equal,
which is why it returns a set. A traceback testing `>` picks one; testing `>=` on the other side
picks a different one. Both are valid, and a diff tool built on either will produce different output
for the same input -- which is a fact about the problem, not about the tool.

Part 3 is the sharper lesson, and it is the reason this section exists. Longest common **substring**
looks like the same problem and is not. The counts of answer-holding cells came out equal -- three
each -- and the counts are not the point; the *positions* are. Every cell holding the subsequence
answer is in the last two rows, and the reason is structural: the subsequence table never goes down,
so once a cell has reached the maximum, every cell down and to the right of it keeps it. The
substring answer cells are scattered, and which rows they land in depends on the input.

The tell is in the recurrence. The substring table has **no `max` between neighbours at all** --
its cell is `table[i-1][j-1] + 1` or zero, and nothing else. A `max` between neighbours is the
signature of a state that carries a running best; its absence means the state is pinned to a
position and the running best has to be collected elsewhere, by the loop. Forget it and the code
still runs and still returns a plausible number, which is the worst kind of bug.

## Knapsack, and the word that qualifies the chapter

Knapsack is the DP that turns up most often in practice, because "pick the best subset under a
budget" is what most resource decisions actually are. It is also where the phrase "polynomial time"
stops meaning what it looks like.

<<BLOCK:knapsack>>

Part 1 is the smallest counterexample to the greedy that looks right. Taking the best
value-per-unit-weight first is the natural idea, and it takes the one item that no optimal solution
contains -- leaving four units of room with nothing that fits. The general shape of the failure is
that greedy decisions are irrevocable, and a locally best choice can consume a resource in a way
that makes the remainder unusable.

The table in Part 2 has two dimensions, and the second one is the surprise: the state includes the
budget, so the size of the table depends on a *number* rather than on how many things there are.

That is the whole of Part 3, and it is the reason this section exists. "Polynomial time" means
polynomial in the **length of the input**. For a list of n items the input length is roughly n. For
a capacity, the input length is the number of *digits* -- writing 100000 takes six characters, not
a hundred thousand. So every extra digit of capacity multiplies the table by ten while the input
grows by one character, and the running time is polynomial in the *value* of the capacity and
exponential in the *length* of it.

That is what **pseudo-polynomial** means, and it is why knapsack being solvable this way is not a
counterexample to knapsack being NP-hard. Both statements are true at once and they are not in
tension. The practical reading is the useful one: this is the right algorithm when the budget is a
real quantity you can afford to enumerate -- 200 grams, 48 hours, 5000 dollars -- and the wrong one
when the budget is 10^18.

Part 4 is the one-line change that breaks it, and it is worth doing because the broken version is
not nonsense. Going upwards through the capacity means the cell `best[w-weight]` has already been
written this round, so it may already contain this item -- and the algorithm takes it again and
again until the capacity runs out. On this instance that is 22 copies of the best-ratio item, worth
3300 instead of 715.

The wrong version is a correct solution to a **different problem**: unbounded knapsack, where every
item is available in unlimited supply. That is why the bug is easy to miss -- the code runs, the
answer is larger than the right one rather than obviously absurd, and a test that only checks "is it
bigger than zero" passes. And it is the version you *want* for coin change, which is the next
section. Same table, same loop, opposite direction.

:::pitfall One loop, two problems, no error either way
Reversing a single line of the rolling row is the whole difference between 0/1 knapsack and
unbounded knapsack, and the wrong version produces a *larger* number rather than an exception:

```python
for w in range(weight, capacity + 1):        # the wrong direction
    best[w] = max(best[w], best[w - weight] + value)
```

Going upwards, `best[w - weight]` has already been written this round, so it may already contain this
item -- and the algorithm takes it again, and again, until the capacity runs out. On the instance
above that is 22 copies of the best-ratio item, worth 3300 where the right answer is 715.

Nothing raises, nothing warns, and the number is not absurd. The only way to catch it is to check the
answer against a second implementation, which is why the two versions are printed side by side rather
than one of them being trusted.
:::

## When the greedy is wrong

A greedy algorithm is correct when you can prove that taking the locally best option can never be a
mistake -- an **exchange argument**. Coin change is the cleanest place to see both halves: for some
coin systems the argument goes through and greedy is optimal, and for others it does not and greedy
is simply wrong.

<<BLOCK:greedy_vs_dp>>

Part 2 is the part that matters, and it has two readings. The rate first: the greedy is right 77% of
the time, which is worse than being obviously wrong, because a test with a handful of amounts in it
will pass.

Then the pattern, which is exact rather than approximate. Every wrong target is `4k + 2` for some k.
The reason is that `4k + 2 = 4(k-1) + 6` and 6 is two 3s, so the optimal answer is `k-1` fours and
two threes -- `k+1` coins -- while the greedy takes `k` fours and two 1s, which is `k+2`. The greedy
is not occasionally unlucky. It is systematically one coin worse on an infinite family of inputs,
and the pattern is visible only because the counts were written down.

Part 3 gives the sufficient condition and the shape of the argument: every coin worth at least twice
the one below it. Take the largest coin `c` that fits; any solution avoiding it must make up at
least `c` from smaller coins, and since the next coin down is worth at most `c/2`, that takes at
least two coins. Swapping two for one cannot make the count worse. It holds for the decimal system
and it fails for `{1, 3, 4}`, where 4 is less than twice 3 -- so one coin of 3 can substitute for the
4, and the swap the argument depends on does not exist.

Part 4 goes somewhere unexpected and is the reason this section is in the chapter at all. The
coin-change DP has a one-dimensional state and a recurrence of the form
`best[a] = 1 + min(best[a - c])`, which does not look like a graph problem. Write the amounts as
nodes and a coin as an edge from `a` to `a + c`, and it is a breadth-first search over 60 nodes.

The two are the same algorithm. **Dijkstra is the DP for a weighted graph**; this is the unweighted
case, so BFS is enough and the "table" is the array of distances. That is a general pattern rather
than a coincidence: a DP is a shortest path through its own state space, and the state space is a
graph whether or not you draw it. Chapter 47's algorithms are the special case where the edges can
be written down explicitly; this chapter's are the case where the edges are implied by the
recurrence.

It also explains the loop direction that separated 0/1 from unbounded knapsack. In a graph where a
coin edge goes from `a` to `a + c`, walking the amounts forwards means each edge can be traversed
again from its own endpoint -- which is exactly what "unbounded" means. Walking backwards visits
each edge once. Same graph, two different questions.

## What the table costs

Every DP in this chapter has been a table. The table is also the part you can usually throw away,
and the two questions worth asking are "how much does it cost" and "what did it buy me". The answer
to the second one is more interesting than the answer to the first.

<<BLOCK:space>>

The third version is the point, and it is the option people forget exists. You do not need to keep
the *numbers* to keep the *path*; you need to keep the **decisions**, and there are only three of
those per cell. Replacing a table of integers with a table of bytes costs the same number of slots
and keeps the path intact -- and on the pair in Part 1 the two reconstructions are identical, all
44 steps of them.

The comparison understates the difference in a way worth naming, because it is where a count stops
being the whole story. A "number" here is a Python int in a list -- a pointer plus an object behind
it -- while a byte in a `bytearray` is one byte with no object behind it. Counting slots is the
right discipline for comparing algorithms; it is not a memory measurement, and saying so is part of
reporting it honestly.

Part 4 is the same comparison at a size where it matters, and the ratio column is the one to keep:
n² numbers against 2n, so the gap grows like n/2 without bound -- 50x at a hundred, 5,000x at ten
thousand. That gives a three-line rule rather than a single recommendation, and the middle line is
the one that is usually forgotten:

- keep the numbers when you need the path and the problem is small
- keep the decisions when you need the path and the problem is large
- keep two rows only when you need the number and nothing else

Part 5 names the escape hatch, because this section has been about giving things up and there is a
way not to. Hirschberg's algorithm gets the path **and** linear memory by giving up something
quietly assumed until now: that each cell is computed once. It computes only the middle row, finds
where an optimal path crosses it, and solves the two halves recursively. The work goes up by a
constant factor and the memory falls from quadratic to linear -- which is a good trade whenever the
strings are large, and the reason "keep the table" is a default rather than a law.

## Choosing, on evidence

The chapter has been about counting. This is what the counting is for.

:::scenario The twenty hours before an exam
Eight topics are on the syllabus, each with an estimated cost in hours and an estimated marks gain,
and there are twenty hours left. Choosing which subset to revise is a knapsack; matching a topic name
the student mistyped against the syllabus is an edit distance. Two DPs from the same chapter, in one
sitting, on a problem small enough to check by hand.

<<BLOCK:scenario>>
:::

The plan is the rucksack with the units relabelled, and the failure mode is the one from Part 1 of
that section made concrete: the greedy spends 13 hours, leaves 7 unused, and loses 33 marks out of
121. The counterintuitive part is worth sitting with -- **the greedy plan is not merely worse, it is
smaller.** It had 20 hours and spent 13, because once the small items were in there was nothing left
that fit.

That is also why the greedy survives in practice and still deserves to be distrusted. A student
following it would finish with four topics revised, seven hours unused, and no way to tell the plan
was suboptimal, because the hours went unused one at a time and each refusal looked sensible in
isolation.

Part 2 is a different DP from the same chapter in a smaller setting, and it shows the point the
chapter opened with: once the state is right, the code is almost mechanical. Hours and marks became
characters, the budget became a length, and the recurrence did not change shape.

The transposition detail at the end of Part 2 is a limitation worth naming rather than hiding. A
single adjacent swap costs **2**, not 1, because plain Levenshtein has no transposition operation --
so a misspelling that is a swap costs more than one that is an omission, which is the opposite of
what a reader expects. Adding the move gives Damerau-Levenshtein, which needs a larger state and
one more lookback. Most spell checkers use that version; the recurrence here is the one that fits on
a page.

Part 3 closes the argument with a check that is worth having in any optimisation story. Over 200
random instances the greedy never once beat the DP, and it cannot: the greedy plan is a legal plan,
so the DP's optimum is at least as good. **A greedy that wins would mean the DP was wrong** -- which
makes that check a test of the DP rather than of the greedy.

:::solution The rule
Reach for the two questions before you reach for a table. Count the distinct states and count the
revisits; if the first is polynomial and the second is exponential, the table is there and the only
remaining work is choosing what the state means.

Then choose the state by asking what a cell has to remember. In edit distance it is a pair of
prefixes, because an edit at one position cannot be described without knowing how much of each
string is left. In knapsack it is a prefix of the items plus a budget, because the value of an item
depends on how much room is left. In coin change it is just the amount, because the coins are
unlimited and their order does not matter.

The last of those three is the one to look at twice, because the same array answers two different
questions depending on which loop is outside -- and only one of them is the question you meant.
:::

## Key takeaways

- A recursion tree is a countable object, and counting it is how you decide whether dynamic
  programming applies. Fibonacci at n = 30 is 2,692,537 calls to compute 31 distinct values.
- Two independent conditions, not one: polynomially many distinct states, and exponential revisits.
  Fibonacci has both, merge sort has the first only, and enumerating subsets has neither.
- Memoisation turns a tree into a line. The function is still *entered* on every request -- the
  saving is in the work behind the entry, which is why a memoised function must be cheap to enter
  and must have no side effects.
- `lru_cache` keys on the arguments tuple, so every argument must be hashable and the failure appears
  at the call site. `maxsize=None` is an unbounded cache, which is a memory leak with a friendly name.
- Top-down pays for the recursion with stack, and the recursion limit is a hard ceiling on the input
  -- not a setting to raise. `sys.setrecursionlimit` moves a counter, not the real stack.
- Top-down visits the states the answer depends on; bottom-up visits all the states that exist. The
  saving depends on how much of the state space is dead, and it is only 1.1x on a grid with almost
  no walls.
- A ratio can improve as the problem becomes impossible. The top-down saving reaches 36x exactly
  where the goal is unreachable and the answer is zero -- so report the answer beside the count.
- Edit distance's naive cost grows like (3 + 2√2)^n, not 3^n, because the three branches step in two
  dimensions. The table is quadratic in the same input.
- LCS's equal case is forced rather than chosen, and the problem has a tie in its statement, so
  three different answers are all correct. Ties are a property of the problem, not of the code.
- Longest common *substring* needs a different state, and its recurrence has no `max` between
  neighbours. The absence of that `max` is the tell that the answer has to be harvested by the loop.
- Knapsack is pseudo-polynomial: the table is polynomial in the capacity's *value* and exponential
  in its *length*. One extra digit multiplies the work by ten.
- The 1-D knapsack row is correct in one direction and silently solves unbounded knapsack in the
  other. The wrong version is a right answer to a different question.
- A greedy is correct only when an exchange argument justifies it. For coins `{1, 3, 4}` the greedy
  is wrong on every target of the form 4k + 2 -- an infinite family, not an edge case.
- Coin change is a shortest path problem, so Dijkstra and dynamic programming are the same algorithm
  on different representations. Chapter 47's algorithms are this chapter's, with the edges written
  down.
- You do not need the table to keep the path. Store the three-way *decision* per cell instead of the
  integer, and the path survives while the table holds bytes where it used to hold numbers.
- Hirschberg's algorithm gets the path and linear memory at about twice the work, by giving up the
  assumption that each cell is computed once.
- The state is the design decision. Getting it right makes the code mechanical; getting it wrong
  produces a correct-looking number that answers a different question.

## Practice

- [ ] Climbing a staircase with steps of 1, 2 and 3, write the naive, memoised and bottom-up
  versions and account for *every* function entry in the memoised count. Then check the growth rate
  against the largest root of `x^3 = x^2 + x + 1`.
- [ ] Find a recursion that has polynomially many states and no overlap, and a second that has few
  states but exponentially large answers. Show that a cache fails for a different reason in each
  case, and say what the fix is.
- [ ] Generalise edit distance so that deletion, insertion and substitution have independent costs.
  Find a price list where two different cost models give the same distance but different edit
  scripts, and explain which branch of the traceback decides it.
- [ ] Write the coin-change *counting* DP two ways, with the loops swapped, and reconcile the two
  answers by expanding every multiset and counting its distinct orderings. Then show that the
  *minimising* DP is unaffected by the same swap, and explain why.
- [ ] Implement the longest increasing subsequence twice -- the O(n²) DP and patience sorting -- and
  check that the patience array is sorted and is *not* a subsequence of the input. Explain what
  object it is instead.

## Solutions

:::solution Exercise 1
The count is exactly `3n + 1`, and being able to say why is the point. Three entries per step
because every new step asks about `n-1`, `n-2` and `n-3`; plus one for the call that starts it off.
The three does not grow because all three questions have already been answered, so each is one
lookup and no work.

The growth check uses the same trick as the first section, and the convergence is much faster than
the golden-ratio case: a third-order recurrence has two correction terms rather than one, so the
ratio is good to three decimals from n = 13 onward instead of still drifting at n = 30.

<<BLOCK:sol1>>
:::

:::solution Exercise 2
The first failure is no overlap: the subset recursion only ever asks about a suffix, so it has n + 1
states and visits each exactly once. The hits column is zero and stays zero, and there is nothing to
fix -- the cache works perfectly and is pointless.

The second failure is subtler and is the one worth carrying away. The grid-path recursion has 81
states for a 9x9 grid and plenty of hits, so both conditions are satisfied. It is also holding
739,025 cell references, because each cache entry holds a list of paths and the lists are
exponential. **Memoisation bounds the number of states, not the size of the answers.** If the answer
per state is exponential, the cache is exponential -- and the fix is to notice that you were asked
to enumerate something, not to write a better cache.

<<BLOCK:sol2>>
:::

:::solution Exercise 3
The comparison that matters is `substitute` against `delete + insert`, and both are properties of
the *model* rather than of the strings. That is testable: run the comparison over six different
pairs of words, including one with no mismatches, and the verdict never moves. Something that holds
before any data arrives is a property of the model.

With unit costs, substituting is strictly cheaper than a delete plus an insert at every mismatch, so
the two-step route is never the better way to fix one -- and that assumption is nowhere in the
recurrence. Raise substitution to 2 and the two tie; raise it to 3 and the preference reverses, with
the same distance but a completely different script.

The symmetry check is the one that would catch a real bug. With equal prices the distance is
symmetric; with deleting cheap and inserting expensive it is not, and over 28 word pairs the two
directions disagree on 17 of them.

<<BLOCK:sol3>>
:::

:::solution Exercise 4
One loop swap, two different questions. With coins outside, `ways[amount]` counts multisets; with
amounts outside, it counts ordered sequences. Both are coherent and they differ by 28.6x at 12p, a
factor that grows without bound.

The bridge is the third line of Part 3: expand every multiset, count its distinct orderings, and add
them up. That agrees with the amount-outer loop, which is the proof that neither loop order is a bug
-- they are two different state definitions that happen to share an array.

The minimising version is unaffected by the same swap, and the reason is the useful generalisation.
Counting is order-sensitive because the loop order decides what the state *means*. Minimising is
order-insensitive because the state does not need to mean anything: `best[a] = min(best[a],
best[a-c] + 1)` is a shortest-path relaxation, and running it in any order reaches the same fixed
point. If a DP state counts something, the loop order is part of the specification; if it optimises
something, it is an implementation detail.

<<BLOCK:sol4>>
:::

:::solution Exercise 5
Both give the same length on all six hand-picked sequences and all 300 random ones, which is the
evidence that the fast version solves the same problem rather than a nearby one.

The interesting part is the patience array. Its length is the answer, and the array itself is
sorted by construction -- which is what makes the binary search valid -- so it cannot be a
subsequence of a shuffled input. The check in Part 2 confirms that rather than assuming it. The DP's
answer, by contrast, is a subsequence by construction, because the parent pointers recorded the
actual chain.

The operation counts are worth reporting with their caveat. The ratio of look-backs to binary
searches grows from 50x to 800x across the sizes tested, which is n² against n log n in one column
-- but the two inner steps are not comparable operations, so the count is reported alongside what is
being counted rather than instead of it.

<<BLOCK:sol5>>
:::
