---
chapter: 49
part: 8
title: A Method for Unseen Problems
summary: A repeatable procedure for a problem you have never seen -- read the constraints as a complexity budget, choose the structure the budget allows, then prove the complexity by counting. Worked end to end on the problems where the answer is "sort it first", the problems where it is a dictionary, and the ones where the budget says exponential.
minutes: 110
tags: [complexity, big-O, problem solving, sorting, hashing, sliding window, meet in the middle, counting]
---

Eight chapters of Part VIII have given you the algorithms: the structures, the sorts, the searches,
the graphs, the recurrences. This one is about the step before any of them, which is deciding which
one the problem is asking for. That step is a procedure, it can be written down, and it is the
difference between solving an unseen problem in twenty minutes and guessing at it for an hour.

The procedure has four questions and they are asked in a fixed order. What do the constraints say
about the complexity I am allowed? Which structure does that complexity require? Which algorithm does
that structure make available? And how do I know the answer I wrote down is the complexity I claimed?
The first question is answered by arithmetic on the size limit, the second falls out of the first,
and the fourth is answered by counting operations rather than by believing the code.

That last point is the discipline the whole Part has been built on, and it is what makes this chapter
possible at all. **Every number below is a count** -- of comparisons, of dictionary lookups, of
subsets enumerated -- and not one of them is a stopwatch reading. A complexity claim is a claim about
how many operations a program performs, and the only way to check such a claim is to count the
operations. When you can count, "this is O(n log n)" stops being an assertion and becomes a
measurement you can be wrong about.

## Four questions, in order

Start with the one that costs nothing and is wrong most often. A problem statement's size limit is not
decoration and it is not a hint; it is the intended complexity, written in the only language the
statement has, which is arithmetic. Do the arithmetic before writing any code.

<<BLOCK:budget>>

The table is the whole of the first question. Read the right-hand column downwards: every complexity
class lands in the same band of operations, because the budget is what a problem setter fixes and n
is what moves to meet it. Then read the second table, which fixes n instead, and note which classes
survive at n = 100,000.

Two entries are worth committing to memory, because they recur constantly. A quadratic solution
reaches a hundred million operations at n = 10,000. A linearithmic one reaches the same hundred
million at about four and a half million. So when a statement says n <= 10^4 it is telling you that a
quadratic answer is expected, and when it says n <= 10^5 it is telling you that a quadratic answer is
not an answer. That is the same algorithm and the same code, and the two statements ask for opposite
things.

## One problem, three algorithms

The second and third questions are easier to see on a single problem solved three ways, so here is the
smallest interesting one: given a list and a target, is there a pair of elements that sums to the
target?

<<BLOCK:two_sum>>

Three shapes, and every problem of this family has them. Look at everything, which is quadratic and
needs no thought. Sort first, which is linearithmic and needs the insight that order helps. Or
remember what you have seen, which is linear and needs a structure -- here a set, and in the next
section a dictionary.

The counting makes the choice unambiguous, and it also makes the *ratio* unambiguous, which matters
more. The brute force is not slower by a constant factor that a faster machine could absorb; it is
slower by a factor that grows with n. The last column is exactly (n-1)/2, because the set version
performs exactly n lookups. A constant factor is a reason to buy a better computer. A growing factor
is a reason to change the algorithm, and the budget from the first section tells you which one you
have.

The agreement check at the top of that block is worth a second look, because it reports something
that is easy to assume away: on 122 of 400 instances the three methods found *different* pairs. All
three were right, because the decision is unique and the witness is not. When you compare two
implementations of the same idea, compare the answers you actually promised to compare. "Both return
a valid pair" is a weaker claim than "both return the same pair", and only the first one is true here.

## Proving a complexity instead of claiming it

You have now chosen an algorithm on the strength of a complexity claim. The fourth question is how you
know the claim is true, and the answer is that you count and then fit.

<<BLOCK:exponent>>

The fit is the part that generalises, and it is also the part that can mislead you, which is why the
second half of that block does the same fit on functions whose complexity you already know. For a
polynomial the fitted exponent is a constant and the fit recovers it exactly: 1, 2 and 3 for n, n^2
and n^3, at every range. For n log n it does not settle. It drifts downwards towards 1 as the range
grows, and the drift is the signature.

So a single fitted number is evidence for a class and not a proof of it. A fitted exponent near 1.1 is
consistent with n log n and with nothing worse; it is not consistent with n^2, whose fit would read 2.
What you are really doing when you fit is separating an exponent from a constant, and you should say
which you have done.

The other result in that block is the one to carry into an interview. `halving loop` is a nested loop
-- a `for` inside a `while` -- and it is linear, because the outer bound halves and the total is a
geometric series summing to about 2n. The fit says 1.00 and the exact count is 2n - 1. Reading a
function's cost off the shape of its indentation is a habit that is right most of the time and
silently wrong the rest of it.

## When the answer is "sort it first"

Sorting costs n log n, which is more than the linear scan you might hope for, so it is worth being
clear about what it buys. Here is a problem where it buys the entire solution: given a list of
half-open intervals, what is the largest number of them open at the same moment?

<<BLOCK:overlap>>

Two findings in that block contradict what almost everyone writes first, and both are worth having in
your head before an interview rather than during one.

The first is that the obvious method is not slow, it is **wrong**. Asking each interval how many
others overlap it answers a different question from the one that was asked, and the smallest
counterexample has three intervals: one long one covering two shorter ones that sit side by side
without touching. The pairwise method counts three; the truth is two. It overcounts on 234 of 300
random instances and never undercounts, and the reason it can only ever overcount is structural --
any set of intervals sharing a point is a candidate, so it can never miss a larger answer.

The second is that the sort alone is not the algorithm. The intervals are half-open, so [0, 5) and
[5, 10) do not overlap, which means that at time 5 the closing event must be processed before the
opening one. Get that tie-break backwards and the sweep is wrong on 138 of 300 instances -- right most
of the time, which is the worst kind of wrong.

What sorting actually buys is not speed. It makes the answer **local**: once the events are in order,
the deepest point is a running maximum and one pass finds it. The pairwise question did not get
faster; it stopped being asked. That is the sense in which "sort it first" is a technique rather than
a tip.

## When a set is not enough

Sorting is the answer to a surprising number of problems and the wrong answer to a specific few. Here
is one: given an unsorted list of integers, how long is the longest run of consecutive values?

<<BLOCK:consecutive>>

The interesting row is not the quadratic one. It is the two set rows, which hold the same data
structure, ask the same question -- "is x + 1 present?" -- at the same one comparison each, and differ
by 500x on the input that matters.

The difference is a guard. Without it, every element walks the whole run in front of it, so a single
run of n consecutive values costs about n^2/2 membership tests and the set has bought nothing. With
it, an element whose predecessor is present is skipped in one comparison, so only the first element of
each run walks it and each element is examined at most twice.

The guard is not free, and the table above shows that too: on data with no long runs the unguarded set
is *cheaper*, because the guard adds one comparison per element and has nothing to save. So this is a
deliberate trade rather than a rule. The cost is a constant factor; the thing bought is a bound. Make
that trade on purpose, and know which of the two you are choosing.

## When the structure falls out of the data

A set is the right structure for a membership question. Some problems look like membership questions
and are not, and the difference is a property of the data rather than a matter of taste.

<<BLOCK:prefix>>

The problem is to count the contiguous stretches that sum to a target. The obvious structure is a set
of the running totals seen so far, and it is wrong as soon as two different prefixes land on the same
sum. The reason is combinatorial and it is exact: for a prefix value seen c times, the dictionary adds
the number of *pairs*, c(c-1)/2, while the set adds one per position that has any predecessor, which
is c-1. Those agree at c = 1 and c = 2 and diverge from c = 3, so the set version is correct exactly
while no count in the dictionary ever exceeds 2.

That is a condition on the data, and it fails more often the longer the list gets. So the structure
the problem needs is a counting dictionary, and the argument for it is arithmetic rather than
preference.

There is a second thing in that block that is easy to get wrong and worth naming, because it is the
same mistake in a different costume. A repeated prefix sum is the same statement as some stretch
summing to zero -- and the empty prefix counts as one of them. A stretch beginning at index 0 sums to
zero exactly when its running total reaches 0, which is a repeat of the empty prefix and of nothing
else. Forget that entry and the count is wrong; it is the entry that is easiest to drop and it is the
same one the dictionary is seeded with.

## When the budget says exponential

Everything so far has been about choosing between polynomial algorithms. Some problems have no
polynomial algorithm to choose, and then the budget does something different: it tells you the name of
the technique.

<<BLOCK:meet_in_middle>>

Meet in the middle does not make the search faster. It changes the exponent from n to n/2, by
enumerating each half and searching the halves against each other, and the return on that is nearly a
doubling of the input the budget can reach: 26 becomes 45.

Two things about that block are worth keeping. The first is that the *enumeration* is the cost, not
the search. When a solution exists, the right half's sums are dense enough that a match turns up on
the first left sum -- all 500 targets in a window were reachable by one half alone. So the technique
pays for two lists of a million sums before it asks a single question, and the worst case is the honest
comparison to make.

The second is the shape of the return. Halving the exponent sounds like a factor of two and is worth
far more, because the wall is exponential: every unit of n doubles the work, so extending the reachable
n from 26 to 45 is not a 1.7x improvement in the problem size, it is the difference between a problem
that can be solved and one that cannot.

:::pitfall The constraint is not always about the size of n

The first question of this chapter is "what do the constraints say about complexity", and it is easy
to hear only the size limit. The size limit is the loudest thing in a statement and it is not the only
thing. Assumptions are quieter and they decide which algorithms are available at all.

<<BLOCK:pitfall>>

Note what the second half of that block is doing. The fast version of that counting problem carries a
precondition -- the empty prefix has to be in the dictionary before the loop starts -- and the slow
version carries none. The precondition is exercised on a minority of small inputs and a majority of
large ones, which means a handful of small tests will probably miss it and the production data will
not.

That is the shape of the trade you are making every time you reach for the clever answer, and it is
why the third question of this chapter is asked *after* the second. Derive the budget from the
constraint first, choose the structure that meets it, and stop there. A solution faster than the
budget requires is not better; it is more to get right than the problem asked for. And a solution
slower than the budget allows is not slower. It is wrong.

:::

:::scenario The job that takes forty minutes

A reporting job joins orders to customers. It works, it has worked for a year, and it has grown slow
enough that the team schedules around it. Nobody has looked at it, because nothing is broken.

<<BLOCK:scenario>>

The counting takes about a minute. The nested loop does one comparison per pair, so its cost is fixed
by the sizes before the data is read, and at the production sizes that is 24 billion comparisons.
Turning it into an index is a few lines and brings it to a third of a second.

What takes longer is the second half of the review, and it is the part that a code review is actually
for. The index that makes the job fast also changes its answers, because a dictionary keyed by
customer id holds one name per key while the nested loop appends a row for every match. A duplicate id
in the customer table means three orders lose a row each. The report changes, and it changes only on
the orders that touch that customer, which is why nobody noticed for a year.

So two things were needed and only one of them was about speed. The index fixed the time. Finding the
duplicate, and deciding what the report should say about it, fixed the correctness -- and it would have
been introduced as a bug if nobody had diffed the two outputs before shipping the faster version.

:::

## Key takeaways

- **Ask the four questions in order**: what complexity do the constraints allow, which structure does
  that require, which algorithm does that structure make available, and how do I know. The order is
  not a formality; each answer narrows the next.
- **A size limit is a complexity budget.** Every complexity class reaches about 10^8 operations at
  some n, and the statement's n tells you which class was intended.
- **Two limits to memorise**: n^2 reaches 10^8 at n = 10,000, and n log n reaches it at about
  4,500,000. So n <= 10^4 invites a quadratic answer and n <= 10^5 forbids one.
- **Prove a complexity by counting and fitting**, not by asserting it. A polynomial's fitted exponent
  is a constant; an n log n fit drifts downwards as the range grows, and that drift is its signature.
- **A nested loop is not automatically quadratic.** The `halving loop` has a `for` inside a `while`
  and is exactly 2n - 1 operations. Read the bounds, not the indentation.
- **"Sort it first" is a technique, not a tip.** Sorting makes the answer local -- the pair that
  matters becomes two neighbours -- so the pairwise question disappears rather than getting faster.
- **The obvious pairwise method is sometimes wrong, not just slow.** For maximum overlap it overcounts,
  and the smallest counterexample has three intervals. Always check the question the code answers
  against the question that was asked.
- **A sort is not a complete algorithm when the data has a tie-break.** Half-open intervals require
  ends before starts at equal times; the wrong order is right most of the time and wrong on shared
  endpoints.
- **A hash set makes lookups O(1) and does not make an algorithm linear.** The run-start guard is what
  bounds the consecutive-run problem, and the guard costs a constant factor that it earns back only on
  long runs.
- **Choose the structure from the data.** A set is right for membership and wrong for multiplicity;
  the criterion is exact -- the set version is correct only while no count exceeds 2.
- **Do not forget the empty prefix.** A stretch starting at index 0 that sums to zero matches the
  seeded empty prefix, and it is the entry that is easiest to drop.
- **When the budget says exponential, the technique has a name.** Meet in the middle halves the
  exponent and nearly doubles the reachable n, because the wall is exponential rather than polynomial.
- **The enumeration is the cost of meet in the middle, not the search.** When a solution exists the
  match arrives almost immediately; the worst case is the honest comparison.
- **Name the case when you state a complexity.** Best, average and worst can differ by orders of
  magnitude -- 1, about 0.9n, and n(n-1)/2 for one early-exit function -- and a claim that names none
  of them is not a claim.
- **Sample a heavy-tailed cost and you learn nothing.** Count the exact distribution instead: for the
  early-exit function, enumerating all n^n inputs shows the worst case is only 1.2% of them at n = 7.
- **Read the assumptions, not just the size limit.** The sliding window is O(n) and correct only while
  the values are non-negative; with a negative it is silently wrong, and the smallest witness is three
  elements long.
- **A faster-than-required solution is not free.** It carries preconditions the slow one does not, and
  those preconditions are exercised least on the small inputs you would test with.

## Practice

- [ ] **Sort it first.** Write two functions that find the largest gap between values that are adjacent
  in sorted order: one that finds each element's successor by scanning, and one that sorts and walks.
  Count the comparisons in both and confirm the scanning version is exactly n^2. Then find the input
  size at which the sorted version first beats the scanning one by more than 100x.
- [ ] **The budget decides.** Write three functions that return the first element of a list that
  occurs exactly once: a scanning version, a version using `list.count` inside a loop, and a version
  using `collections.Counter`. Show by counting that the first two do the same work, and state the
  size limit at which the third becomes necessary rather than merely nicer.
- [ ] **A set changes the answer.** Write three functions that return the elements two lists share: a
  scanning version, a set version, and a version that keeps the first list's order and multiplicity up
  to the second list's count. Find an input where the first and second disagree, and say which of the
  three answers the phrase "the elements they share" actually means.
- [ ] **Name the case.** Take the early-exit duplicate check and compute the *exact* distribution of
  its comparison count over every possible input for n = 2 through n = 7, by enumerating them. Report
  the smallest, median, mean and largest counts and the fraction of inputs at the largest. Then
  explain why the mean grows like n rather than n^2, using the probability that the first row of the
  double loop finds nothing.
- [ ] **Check the assumption.** Write a sliding-window function for the longest stretch summing to at
  most k, and a quadratic function that is correct for any values. Find the shortest input where they
  disagree, count how often they disagree over random mixed-sign inputs, and then state what you would
  actually do if the values could be negative.

## Solutions

:::solution Exercise 1

Two implementations, and the counting that separates them.

<<BLOCK:sol1>>

:::

:::solution Exercise 2

The middle implementation is the interesting one, because a built-in method makes a quadratic loop
read like a fast one.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

The set version is right about which values are shared and wrong about how many times. That is a
difference in the question, not a bug in the code.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

One sample of a heavy-tailed cost tells you nothing, so this one enumerates every input instead and
counts the distribution exactly.

<<BLOCK:sol4>>

:::

:::solution Exercise 5

The window is the O(n) answer and it depends on an assumption that the statement may not have made.

<<BLOCK:sol5>>

:::
