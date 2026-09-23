---
chapter: 58
part: 11
title: Measure First
summary: Find where a program actually spends its work by counting rather than by guessing or by timing. You will be able to instrument a function that takes three seconds and say which of its five loops to change, to tell a linear algorithm from a quadratic one out of counts at four sizes, and to order a list of candidate fixes by the work each removes per line it changes.
minutes: 100
tags: [performance, profiling, cProfile, timeit, measurement, complexity, benchmarking, tracemalloc, optimisation, counting]
---

Parts VII to X were about what code *is* — how the interpreter runs it, what a security boundary is worth,
where a boundary belongs. This part is about what code *costs*, and it opens with the only step that is
not optional.

The rule for this chapter is one sentence long: **a number you did not count is a guess**. Not a bad
guess, necessarily. A guess that is usually wrong in a specific way — it points at the code that is
easiest to suspect rather than the code that does the work. Every block below is a program that counts
something and then reports what the count says, and in five of the nine the count contradicts what the
code looks like it does.

That gives the chapter a second subject, which is the one that matters more: **what a count can and
cannot see**. A count of loop iterations cannot see the cost of a statement inside the loop. A count
inside a function cannot see who called it. A count of comparisons inside a sort cannot see the sort.
Each of those is a block below, and each one is a place where an honest measurement produces a confident
wrong answer.

Everything here is counted rather than timed, and that is a decision rather than a limitation. A timing
is a property of the machine, so it cannot be written down; a count of operations is a property of the
algorithm, so it can. When this chapter says an algorithm does 319,600 comparisons at eight hundred
items, that number is the same on your machine as on mine, and it is the reason the book is allowed to
state it at all.

## The loop count that ranks nothing

Start with the simplest instrument there is: a counter beside each phase, incremented once per iteration.
It is the first thing everybody writes and it is nearly useless, and the reason is worth seeing before
the fix.

Four phases, each looping over the same four hundred rows. The left column of counts is the one the
instrumentation was written to produce. The right column is a second counter, placed inside each loop
body, counting the work the iteration actually does.

<!--BLOCK:guess_vs_count-->

Every phase ran its loop exactly four hundred times. The loop counts are therefore identical for all four
of them and cannot rank them at all — the order they print in is the order they were written in, which is
not a measurement. The work counts rank them, and the ranking is not close.

The gap is in one statement. `join` appends a line to a string, and a string is not appendable: each `+=`
builds a new string and copies everything accumulated so far into it. So the work done on iteration
number *i* is proportional to *i*, not to one, and the total is the sum of all the lengths rather than the
number of lines. A count of iterations cannot see that, and a count of iterations is what the first
instrument reports.

So the first question about any measurement is not "what is the number" but **what unit does it count**.
A count of loop trips counts how often code was reached. A count of work counts what it did. The two agree
only when every trip does the same amount of work, which is exactly the assumption a slow loop breaks.

## What a profiler counts, and what it cannot see

The standard tool for this is `cProfile`, and it is better than a hand-written loop counter because it
does not need you to guess where to put the counter. What it produces is a table of call counts, and the
first thing to understand is what a call count is.

A small text pipeline, profiled over five repeats of the same six-hundred-word input. Two columns are
counted for each function: how many times the profiler saw it entered, and how many operations the
function performs inside its own body.

<!--BLOCK:profile_counts-->

`normalise` is entered three thousand times and does one thing each time. `count_words` is entered five
times and does twelve hundred things each time. The two rankings disagree about which of them to look at
first, and the disagreement is the whole lesson.

A profiler counts *entries into a function*. It cannot see the loop inside one. `count_words` gets a
single row for the whole of its loop body, and `normalise` gets a row per call, so the profiler's headline
number is a count of how often code was entered. That is a shape — a picture of how the call graph is
wired — and it is not a cost. Reading it as a cost is how a program gets optimised in the wrong place for
an afternoon.

The profiler does have a second column, and this chapter does not print it. The time column is the one
everybody wants and the one that cannot be written into a book, because it changes with the machine, the
interpreter build and whatever else is running. The counts do not change. That is why every measured claim
in this chapter rests on a count.

## The shape, from four counts

A single count tells you almost nothing, because you do not know what it is large *relative to*. Two
counts at different sizes tell you something much better: the ratio between them is a property of the
algorithm.

Three ways to look for a duplicate in a list, each counting its comparisons at four sizes. The count is
then turned into an exponent — the power the work grows as — and the exponent is what names the shape.

<!--BLOCK:growth_classified-->

Doubling the input multiplies the pair scan's work by four, the set's by two, and the sort's by something
in between. Those three numbers are the same on every machine, and they are the reason an algorithm has a
*name* rather than just a cost.

The exponent is that measurement with the ratio's arithmetic taken out. It is 2.00 for the pair scan, 1.00
for the set, and 1.19 for the sort — and the last of those cannot be read off the code, because nothing in
a merge sort says `log`. It is also the number the count only finds because the sort's own comparisons are
inside it. Count the pass over neighbours and leave the sort out, and this algorithm reports itself as
linear.

Two methodological notes, because they decide whether the table means anything. The input is shuffled
rather than sorted, so the sort is measured in its average case instead of the one case it is fastest at.
And the classification comes from the measured exponent, not from knowing the answer in advance — which is
the only version of this that is a measurement rather than a demonstration.

The exponent also tells you the size at which the shape starts to matter. At a hundred items the quadratic
version makes 4,950 comparisons, which is nothing at all. The exponent is what says it will be 319,600 at
eight hundred, and it is the second number that should decide what you do next.

## The objects the code asks for

Comparisons are not the only countable thing. A program's other cost is the memory it holds, and the
countable version of that is not bytes — a byte count depends on the interpreter build — but **how many
containers the code asks for and how long they are**.

Three ways to total one column of three hundred rows, each counting the intermediate containers it builds.

<!--BLOCK:allocations-->

All three produce 897. The first builds two lists holding 557 items between them, the second builds one
list of 257, and the third builds nothing at all because it adds as it walks.

The count is of containers the code asks for, so it is the same on every machine, and it is the part of
the memory cost a reader can act on. `sys.getsizeof` would give a byte count and that count depends on the
build, which puts it in the same category as a timing: real, useful, and not something a book can print.

The reason to look at this number at all is the peak. Two containers of a few hundred small integers is
nothing; the same shape over a million rows is two lists of a million, and the fix is not to make the
lists smaller but to stop making them. Which is what the third way does, and it is shorter to write.

## Who calls the hot function

A profiler's table is indexed by function. That is the wrong index for the question you usually have,
which is not "which function is slow" but "who is making it slow".

One field-touching function with four call sites, counting calls attributed to the site that made them.

<!--BLOCK:caller_share-->

`touch` is one function entered from four places. The largest single caller is `validate`, at 4,200 calls
and 48.8% of everything done inside it, and `load_body` is within 2.3 points of that. Two call sites
account for 95% of the function's work, and the two others account for 4.6% between them.

The second of those two is the finding. `validate` walks the fields the loaders have just walked. A walk
that has already happened happens again, and a count is what makes a duplicate pass look like work instead
of looking like care.

Now compare the two possible fixes. Halving the cost of `touch` removes 4,300 units and edits a function
that four call sites share. Deleting the repeat removes 4,200 units and edits one caller. Those are the
same size of win, and only one of them is a deletion. That is the shape of finding that attribution gives
you and a function-indexed profile cannot: a profile reports one row for `touch`, at 100% of the time,
because every call goes through it.

## One run is not a measurement

The reason to count rather than time is not that counting is more precise. It is that a timing has an
error you cannot see, and the error is often larger than the difference you are trying to measure.

Five candidates whose true costs differ by twenty units, measured with a wobble three times that size. The
wobble is a fixed sequence so that this program prints the same bytes on every run — the property being
modelled is only that it is larger than the gaps.

<!--BLOCK:repeat_noise-->

The first run gets one of the five positions right. Across nine runs the average is 1.11 out of 5, and two
of the nine runs get the order entirely wrong. The gaps between neighbours are twenty units and the wobble
is sixty, so a single run is ranking the wobble rather than the candidates.

The median of the nine gets all five, and the reason is specific rather than lucky: the wobble is
symmetric about zero, and a median of an odd number of runs removes a symmetric error. That is the whole
argument for repeating a measurement and taking the middle one rather than the best one — and note
*median*, because the best of nine is a number that has been selected for being too good.

Then count the work instead. That gets five of five on the first run and needs no repetition at all,
because a count of operations is an integer the code produces rather than a duration a machine produces.
The trade is not "counts are more accurate than times". It is that a count measures a different thing, and
the thing it measures is the one that is stable enough to reason about.

When there is no count to make, the number that decides how many runs are enough is the gap you are trying
to resolve. Here twenty units needs the wobble down to well under twenty, which one run cannot do and nine
runs can.

## The size you have not run

A complexity class is usually taught as a label you write beside a function. Its actual use is narrower and
much more valuable: it is the thing that answers *what happens at ten times the size* without running it.

Three algorithms counted at four sizes, each fitted to an exponent from the measured ratios, and then used
to predict a size the program has not run. The prediction is then checked against a count taken at that
size.

<!--BLOCK:scaling_law-->

The fit is from four counts and the check is a fifth size, and the worst of the three predictions is off by
2.8%. That number is the value of the whole idea: you can decide whether a design can ship without
building the machine that would be needed to test it.

The linear and the quadratic fit are almost exact, because the counts are integers and the ratios have
nowhere to hide. The middle column is the interesting one — a sort's comparisons grow by a little more than
two per doubling, and the fit lands near that without the code saying so anywhere. When the prediction is a
few percent out rather than exact, that is not a failure of the method; it is the method reporting that
this algorithm's growth is not a clean power.

So the number to carry away is the ratio rather than the count. Doubling the input multiplies the work by
about four for the pair scan, by about two for the pass, and by a number in between for the sort, and those
three numbers are the same on every machine — which is the only reason they can be written down at all.

## The peak, not the total

Everything so far has been about time-shaped cost. The other kind is space, and it has a different failure
mode: a program that is too slow finishes late, and a program that holds too much does not finish.

Three ways to process the same five thousand rows, each counting the items it holds at once.

<!--BLOCK:memory_peak-->

All three read every row exactly once. The column a total-work measurement reports is 5,000 for all three
and cannot tell them apart. The peak separates them by a factor of five thousand, and the peak is the
number that decides whether the program runs at all, because a machine that cannot hold the peak does not
run slowly — it stops, and it stops at the row where the peak is reached.

The fix is a change of shape rather than a change of speed. Both of the others read the same five thousand
rows and do the same additions; the window holds 32 rows at a time and the streaming version holds 1.
Reading a file in chunks is not longer code than reading it whole. It is one extra loop.

The count here is of containers the code asks for, which is why it is the same on every machine.
`tracemalloc` reports the same shape in bytes and a different number on each interpreter build, so the
shape is what a book can print and the bytes are what a profiler is for.

## The order to fix things in

Measuring is not the last step. The output of a measurement is a list of candidate fixes, and the list has
to be ordered, and ordering it by taste is how the wrong one gets done first.

Six fixes to the report from earlier, each with the work it removes and the lines it changes. Both of those
are counted, so the order is not a matter of opinion.

<!--BLOCK:fix_ranking-->

Both orders put the join first, and it is the one everybody finds: 184,335 units for two lines. They part
company at the second move. A global memo removes 60,000 units in 40 lines; a set for the dedupe removes
19,700 in 3. The first is worth three times the work and costs thirteen times the lines, so per line it is
the worse of the two — 1,500 against 6,567.

The ranking to use is the second one, and the reason is not that small changes are safer. It is that a fix
has to survive review before it removes anything, and the lines changed is the part of that cost which is
countable. Work removed per line changed is a real ratio, and it is the one that orders the list here.

Note also what the bottom of the list is. The two fixes a reader reaches for first — caching the format
string and trimming the row count — are the two with an obvious better spelling, and together they are 400
units out of 206,970. They are correct, they are worth doing eventually, and their order does not matter at
all.

:::pitfall The benchmark that measures something else

The trap this whole chapter is built around, and it is not a wrong number. It is a real number, correctly
produced, of the wrong thing.

Six benchmark designs, each declared to measure the same function over the same fifty inputs. What is
counted is how many times that function was actually entered.

<!--BLOCK:pitfall-->

One of the six enters the function fifty times. Four never enter it at all, and the sixth enters it once.
Every one of them is a loop, or a call, inside a timer, and every one of them produces a number.

None of those six designs would look wrong in a file. That is the point. A measurement is a claim with two
halves — *this is the number*, and *this is what produced it* — and the second half is the one that goes
missing, because the first half is what gets printed. The way to keep the second half is to count something
the code under test controls, and to check that the count is what you expected **before** you look at the
number.

:::

:::scenario The report that takes too long

A report over two hundred rows that a user has described as slow. Five phases, each counting its own work,
and four candidate fixes. The count is of the work each fix removes, which is what decides the order to try
them in.

<!--BLOCK:scenario-->

Two phases account for 99.7% of the work: the dedupe at 19,900 units and the join at 186,470. Everything
else in the report is a rounding error, and both of the expensive phases are loops that look like one line.

The dedupe is a nested loop with a `break`, which reads as a scan and is quadratic. The join is a `+=` on a
string, which reads as an append and copies the whole string every time. Neither is visible by reading, and
both are visible by counting. Replacing the dedupe with a set removes 19,700 units; replacing the join with
`"".join` removes 184,335, which is 89.1% of the total.

The two fixes that do not matter are the two a reader would reach for first, because they are the ones with
an obvious better spelling. Caching the format string and trimming the row count are each worth 200 units —
0.1% each. They are correct, they are cheap, and doing them first would have looked like progress while
changing nothing measurable.

That is the whole reason to measure before optimising. The four fixes are all correct and all worth doing
eventually, and only two of them change the answer.

:::

## Key takeaways

- **A number you did not count is a guess, and the guess has a direction.** It points at the code that is
  easiest to suspect, which is the code written in the fewest lines.
- **The first question about a measurement is what unit it counts.** A count of loop trips counts how
  often code was reached; a count of work counts what it did. They agree only when every trip does the same
  amount of work.
- **Four phases of a report each ran their loop exactly 400 times.** The loop counts were identical and
  could not rank them; the work counts said one phase did 99.8% of the work.
- **A profiler counts entries into a function and cannot see the loop inside one.** `normalise` was entered
  3,000 times doing one thing, `count_words` five times doing 1,200, and the two rankings disagreed about
  which to look at first.
- **The time column is the one you want and the one that cannot be written down.** It changes with the
  machine; the counts do not, which is why every claim here rests on them.
- **Two counts at different sizes are worth far more than one count.** The ratio between them is a property
  of the algorithm rather than of the machine or of the run.
- **Doubling the input multiplied the work by 4.01, 2.28 and 2.00** for a pair scan, a sort and a set. Those
  three numbers are the algorithms' names.
- **Fit the exponent rather than reading the ratio.** It is 2.00, 1.19 and 1.00 for the same three, and
  1.19 is the number nothing in the source states.
- **A count only sees what you instrumented.** Counting the pass over neighbours and leaving the sort out
  makes a sort-based algorithm report itself as linear.
- **All three ways to total a column produced 897.** One held 557 items in intermediates, one 257, one none
  — the answer was identical and the memory was not.
- **`sys.getsizeof` is in the same category as a timing.** Real, useful, and dependent on the interpreter
  build, so not something a book can print.
- **A profile is indexed by function and the question is usually about the caller.** `touch` was entered
  8,600 times from four sites, and two of them were 95% of it.
- **Halving the cost of a shared function removed 4,300 units; deleting one duplicate pass removed 4,200.**
  The same size of win, and only one of them is a deletion.
- **One run of a noisy measurement got one of five positions right**, and nine runs averaged 1.11. The gaps
  were 20 units and the wobble was 60.
- **The median of an odd number of runs removes a symmetric error.** The best of nine is a number that has
  been selected for being too good.
- **A count needs no repetition.** It ranked all five correctly on the first run, because an integer the
  code produces is not a duration a machine produces.
- **The exponent predicts a size you have not run.** Four counts fitted an exponent that predicted a fifth
  size to within 2.8%, which is how a design decision gets made without the machine.
- **The peak decides whether a program runs; the total decides how long it takes.** 5,000 rows held at once
  against 32 or 1, with every row read exactly once in all three.
- **Order the fixes by work removed per line changed.** A memo removed three times the work of a set and
  cost thirteen times the lines, so per line it was the worse first move.
- **The fixes with an obvious better spelling are the ones that do not matter.** Two of them together were
  400 units out of 206,970.
- **One of six benchmark designs entered the function it claimed to measure.** Four never entered it at
  all, and all six produced a number.
- **Check the count before you look at the number.** A measurement is two claims, and the one that goes
  missing is *this is what produced it*.

## Practice

- [ ] **Instrument a slow function of yours by counting.** Pick a function in a project of yours that
  takes long enough to notice. Put a counter inside each loop rather than around it, and record the work
  each loop does. Report the loop you expected to dominate, the one that actually did, and the unit you
  counted in each case. If the two are the same, say what made the guess right.
- [ ] **Classify two implementations from counts at four sizes.** Take two implementations of the same
  operation — a search, a dedupe, a join — and count a comparison or an iteration at four doubling sizes.
  Report the exponent for each, the shape you would name it, and the size at which the faster one stops
  being faster. Then say which of the two counts you would have had to instrument differently to see the
  cost you missed.
- [ ] **Measure what a cache costs as well as what it saves.** Take a function with a `functools.lru_cache`
  or a hand-written memo. Count the work it removes, the entries it holds at its peak, and the number of
  distinct keys. Report all three, and then say what happens to the third one when the input becomes
  unbounded — and what would have to evict.
- [ ] **Write a benchmark that fails loudly when it measures nothing.** Take a loop you have timed. Add a
  counter to the code under test, declare how many times it should be entered, and make the benchmark
  compare the two and report. Then deliberately break it three ways — a copy of the input, an empty loop, a
  different function — and confirm that your check catches all three. Report which of the three your first
  version of the check missed.

## Solutions

:::solution Exercise 1

A report builder with five loops, instrumented by counting rather than by timing, and the loop that turns
out to hold 93% of the work.

<!--BLOCK:sol1-->

:::

:::solution Exercise 2

Two sorts that both claim to be `n log n`, counted at four sizes on the same reverse-ordered input. The
ratios reject the claim for one of them.

<!--BLOCK:sol2-->

:::

:::solution Exercise 3

The same function called over the same keys with and without a memo, counting the work removed, the misses,
and the entries held at the peak.

<!--BLOCK:sol3-->

:::

:::solution Exercise 4

Four benchmark designs run through a four-line harness that declares how many times the code under test
should be entered and reports which designs measure what they claim.

<!--BLOCK:sol4-->

:::
