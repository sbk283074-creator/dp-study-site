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

```python run
"""Chapter 58 -- where the work is, counted rather than guessed.

A four-phase report in which every phase counts two things: how many
times its loop ran, and how much work it did inside. The first column is
identical for all four phases and the second is not.
"""

ROWS = 400


def load(count):
    out = []
    for i in range(ROWS):
        count["rows"] += 1
        count["work"] += 1
        out.append({"id": i, "name": "row-%d" % i, "value": i % 17})
    return out


def validate(rows, count):
    """Touches every row and keeps every row, so the loop counts stay
    comparable with the phases on either side of it."""
    for row in rows:
        count["rows"] += 1
        count["work"] += 1
        if not isinstance(row["value"], int):
            raise TypeError("value")
    return rows


def render(rows, count):
    out = []
    for row in rows:
        count["rows"] += 1
        count["work"] += 1
        out.append("%s=%s" % (row["name"], row["value"]))
    return out


def join_all(lines, count):
    """The phase whose loop count says nothing about its cost."""
    out = ""
    for line in lines:
        count["rows"] += 1
        count["work"] += len(out)
        out += line + "\n"
    return out


PHASES = [
    ("load", load),
    ("validate", validate),
    ("render", render),
    ("join", join_all),
]


def run():
    counts = {}
    rows = None
    for name, phase in PHASES:
        counts[name] = {"rows": 0, "work": 0}
        if name == "load":
            rows = phase(counts[name])
        else:
            rows = phase(rows, counts[name])
    return counts


def main():
    counts = run()
    print(f"  rows                                {ROWS}")
    print(f"  phases                              {len(PHASES)}")
    print()
    print("    phase      loop iterations   work units   share of the work")
    total = sum(counts[name]["work"] for name, _ in PHASES)
    for name, _ in PHASES:
        share = 100.0 * counts[name]["work"] / total
        print("    {:<11}{:>15}{:>13}{:>15.1f}%".format(
            name, counts[name]["rows"], counts[name]["work"], share))
    print("    {:<11}{:>15}{:>13}{:>15}".format(
        "total", sum(counts[name]["rows"] for name, _ in PHASES), total,
        "100.0%"))
    print()

    print("    the order the loop counts give you")
    for index, (name, _) in enumerate(
            sorted(PHASES, key=lambda p: -counts[p[0]]["rows"]), 1):
        print("    {:<3}{:<12}{:>8}".format(index, name,
                                           counts[name]["rows"]))
    print("    every phase is 400, so this ranking is the order the phases")
    print("    happen to be written in and nothing more.")
    print()

    print("    the order the work counts give you")
    ranked = sorted(PHASES, key=lambda p: -counts[p[0]]["work"])
    for index, (name, _) in enumerate(ranked, 1):
        print("    {:<3}{:<12}{:>10}".format(index, name,
                                             counts[name]["work"]))
    print()

    heaviest = ranked[0][0]
    lightest = ranked[-1][0]
    ratio = counts[heaviest]["work"] / counts[lightest]["work"]
    print(f"  every phase ran its loop exactly {ROWS} times, so the loop count")
    print("  is identical for all four and cannot rank them at all. the work")
    print(f"  count says `{heaviest}` does {ratio:.0f} times the work of")
    print(f"  `{lightest}`, and it is the phase written in one line.")
    print()
    print("  the reason is in the statement the counter sits next to. `join`")
    print("  copies the whole string it has built so far on every iteration,")
    print("  so its work is the sum of all the lengths rather than the number")
    print("  of lines. counting iterations cannot see that, and counting")
    print("  iterations is what a first measurement usually does.")
    print()
    print("  so the first question about any measurement is what unit it")
    print("  counts. a count of loop trips counts how often the code was")
    print("  reached, not what it did, and the two agree only when every trip")
    print("  does the same amount of work -- which is exactly the assumption")
    print("  a slow loop tends to break.")


main()
```

```text
  rows                                400
  phases                              4

    phase      loop iterations   work units   share of the work
    load                   400          400            0.1%
    validate               400          400            0.1%
    render                 400          400            0.1%
    join                   400       791144           99.8%
    total                 1600       792344         100.0%

    the order the loop counts give you
    1  load             400
    2  validate         400
    3  render           400
    4  join             400
    every phase is 400, so this ranking is the order the phases
    happen to be written in and nothing more.

    the order the work counts give you
    1  join            791144
    2  load               400
    3  validate           400
    4  render             400

  every phase ran its loop exactly 400 times, so the loop count
  is identical for all four and cannot rank them at all. the work
  count says `join` does 1978 times the work of
  `render`, and it is the phase written in one line.

  the reason is in the statement the counter sits next to. `join`
  copies the whole string it has built so far on every iteration,
  so its work is the sum of all the lengths rather than the number
  of lines. counting iterations cannot see that, and counting
  iterations is what a first measurement usually does.

  so the first question about any measurement is what unit it
  counts. a count of loop trips counts how often the code was
  reached, not what it did, and the two agree only when every trip
  does the same amount of work -- which is exactly the assumption
  a slow loop tends to break.
```

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

```python run
"""Chapter 58 -- what a profiler counts, and what it cannot see.

A small text pipeline profiled with cProfile. Only the call counts are
printed, because they are the part of a profile that is the same on every
machine, and the operations inside each function are counted separately.
"""

import cProfile
import pstats

OPS = {}


def bump(name, count=1):
    OPS[name] = OPS.get(name, 0) + count


def normalise(word):
    bump("normalise")
    return word.strip().lower()


def tokenise(text):
    parts = text.split()
    bump("tokenise", len(parts))
    return parts


def keep_long(words):
    out = []
    for word in words:
        bump("keep_long")
        word = normalise(word)
        if len(word) > 3:
            out.append(word)
    return out


def count_words(words):
    counts = {}
    for word in words:
        bump("count_words", 2)
        counts[word] = counts.get(word, 0) + 1
    return counts


def report(text):
    bump("report")
    words = keep_long(tokenise(text))
    return sorted(count_words(words).items())


TEXT = " ".join("word%d" % (i % 40) for i in range(600))
REPEATS = 5

WATCHED = ["report", "tokenise", "keep_long", "count_words", "normalise"]


def profile():
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(REPEATS):
        report(TEXT)
    profiler.disable()
    return pstats.Stats(profiler)


def main():
    stats = profile()
    calls = {}
    for (_file, _line, name), entry in stats.stats.items():
        if name in WATCHED:
            calls[name] = entry[1]

    print(f"  repeats                             {REPEATS}")
    print(f"  words per call                      {len(TEXT.split())}")
    print()
    print("    function        calls   ops per call   total ops")
    for name in WATCHED:
        count = calls.get(name, 0)
        ops = OPS.get(name, 0)
        per = ops // count if count else 0
        print("    {:<16}{:>6}{:>15}{:>12}".format(name, count, per, ops))
    print()

    print("    the order the call counts give you")
    for index, name in enumerate(
            sorted(WATCHED, key=lambda n: -calls.get(n, 0)), 1):
        print("    {:<3}{:<14}{:>7} calls".format(index, name,
                                                 calls.get(name, 0)))
    print()

    print("    the order the operation counts give you")
    for index, name in enumerate(sorted(WATCHED, key=lambda n: -OPS.get(n, 0)),
                                 1):
        print("    {:<3}{:<14}{:>7} operations".format(index, name,
                                                      OPS.get(name, 0)))
    print()

    top_calls = max(WATCHED, key=lambda n: calls.get(n, 0))
    top_ops = max(WATCHED, key=lambda n: OPS.get(n, 0))
    print(f"  `{top_calls}` is called {calls[top_calls]} times and does one thing")
    print(f"  each time. `{top_ops}` is called {calls[top_ops]} times and does")
    print(f"  {OPS[top_ops] // calls[top_ops]} things each time, so the two rankings disagree")
    print("  about which one to look at first.")
    print()
    print("  the profiler counts entries into a function, and it cannot see")
    print("  the loop inside one. `count_words` gets a single row for the")
    print("  whole of its loop body, and `normalise` gets a row per call, so")
    print("  a profile's headline number is a count of how often code was")
    print("  entered -- which is a shape, not a cost.")
    print()
    print("  that is why the profiler's other column exists, and why this")
    print("  chapter does not print it. the time column is the one you want")
    print("  and it is the one that cannot be written into a book, because")
    print("  it changes with the machine. the counts do not, so they are")
    print("  what a measured claim has to rest on.")


main()
```

```text
  repeats                             5
  words per call                      600

    function        calls   ops per call   total ops
    report               5              1           5
    tokenise             5            600        3000
    keep_long            5            600        3000
    count_words          5           1200        6000
    normalise         3000              1        3000

    the order the call counts give you
    1  normalise        3000 calls
    2  report              5 calls
    3  tokenise            5 calls
    4  keep_long           5 calls
    5  count_words         5 calls

    the order the operation counts give you
    1  count_words      6000 operations
    2  tokenise         3000 operations
    3  keep_long        3000 operations
    4  normalise        3000 operations
    5  report              5 operations

  `normalise` is called 3000 times and does one thing
  each time. `count_words` is called 5 times and does
  1200 things each time, so the two rankings disagree
  about which one to look at first.

  the profiler counts entries into a function, and it cannot see
  the loop inside one. `count_words` gets a single row for the
  whole of its loop body, and `normalise` gets a row per call, so
  a profile's headline number is a count of how often code was
  entered -- which is a shape, not a cost.

  that is why the profiler's other column exists, and why this
  chapter does not print it. the time column is the one you want
  and it is the one that cannot be written into a book, because
  it changes with the machine. the counts do not, so they are
  what a measured claim has to rest on.
```

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

```python run
"""Chapter 58 -- telling O(n) from O(n^2) by counting, not by timing.

Three ways to look for a duplicate, each counting the comparisons it makes
at four sizes. The count is turned into an exponent, and the exponent is
what names the shape.
"""

import math

SIZES = [100, 200, 400, 800]


def shuffled(size):
    """A deterministic permutation, so the sort is not measured in the one
    case it is fastest at."""
    items = list(range(size))
    state = 12345
    for i in range(size - 1, 0, -1):
        state = (state * 1103515245 + 12345) % 2147483648
        j = state % (i + 1)
        items[i], items[j] = items[j], items[i]
    return items


def by_scan(items, count):
    """Every item against every item before it."""
    seen = []
    for item in items:
        for other in seen:
            count[0] += 1
            if other == item:
                return True
        seen.append(item)
    return False


def merge_sort(items, count):
    """A sort whose comparisons are counted where they happen. Counting
    only the pass after the sort would make this look linear."""
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], count)
    right = merge_sort(items[mid:], count)
    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        count[0] += 1
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def by_sort(items, count):
    """A sort, then one pass over neighbours."""
    ordered = merge_sort(items, count)
    for left, right in zip(ordered, ordered[1:]):
        count[0] += 1
        if left == right:
            return True
    return False


def by_set(items, count):
    seen = set()
    for item in items:
        count[0] += 1
        if item in seen:
            return True
        seen.add(item)
    return False


ALGORITHMS = [
    ("scan every pair", by_scan),
    ("sort then compare", by_sort),
    ("a set", by_set),
]


def fit(series):
    """The exponent the counts grow as, from the measured ratios."""
    logs = [math.log(series[i + 1] / series[i]) for i in range(len(series) - 1)]
    return sum(logs) / len(logs) / math.log(2)


def classify(power):
    """Named from the fitted exponent, not from knowing the answer."""
    if power > 1.5:
        return "quadratic"
    if power > 1.1:
        return "n log n"
    return "linear"


def main():
    print(f"  sizes                               {len(SIZES)}")
    print(f"  algorithms                          {len(ALGORITHMS)}")
    print()
    counts = {name: [] for name, _ in ALGORITHMS}
    print("    size     scan every pair   sort then compare   a set")
    for size in SIZES:
        items = shuffled(size)
        cells = []
        for name, algorithm in ALGORITHMS:
            count = [0]
            algorithm(items, count)
            counts[name].append(count[0])
            cells.append(count[0])
        print("    {:>6}{:>18}{:>20}{:>8}".format(size, *cells))
    print()

    powers = {name: fit(counts[name]) for name, _ in ALGORITHMS}
    shapes = {name: classify(powers[name]) for name, _ in ALGORITHMS}
    print("    growth when the size doubles")
    print("    {:<22}{:>9}{:>10}   {}".format("", "ratio", "exponent", "shape"))
    for name, _ in ALGORITHMS:
        series = counts[name]
        ratios = [series[i + 1] / series[i] for i in range(len(series) - 1)]
        average = sum(ratios) / len(ratios)
        print("    {:<22}{:>8.2f}x{:>10.2f}   {}".format(
            name, average, powers[name], shapes[name]))
    print()

    quadratic = [name for name, _ in ALGORITHMS if shapes[name] == "quadratic"]
    print("  the counts are exact integers, so the ratio between two sizes is a")
    print("  property of the algorithm: doubling the input multiplies the work")
    print(f"  by about 4 for {len(quadratic)} of the {len(ALGORITHMS)}, by about 2 for another, and by")
    print("  something in between for the third.")
    print()
    print("  the exponent is that measurement with the ratio's arithmetic taken")
    print(f"  out. It is {powers['scan every pair']:.2f} for the pair scan, {powers['a set']:.2f} for the set, and")
    print(f"  {powers['sort then compare']:.2f} for the sort -- and that last one is the number")
    print("  that cannot be read off the code, because nothing in a merge sort")
    print("  says `log`. It is also the number the count only finds because the")
    print("  sort's own comparisons are inside it: counting the pass over")
    print("  neighbours and not the sort makes this algorithm look linear.")
    print()
    print("  the input is shuffled rather than sorted, so the sort is measured")
    print("  in its average case rather than the one case it is fastest at.")
    print("  That choice does not change the exponent; it changes the constant")
    print("  in front of it, which is the part of a measurement that a reader")
    print("  should not trust across machines anyway.")
    print()
    print("  the ratio is the measurement that survives being written down. A")
    print("  timing would give the same shape on any machine and a different")
    print("  number on each one, so a book can only print the shape. The counts")
    print("  are the same everywhere, which is why they can be printed at all.")
    print()
    print(f"  the other thing the counts buy is the size at which the shape")
    print(f"  matters. At {SIZES[0]} items the quadratic version makes {counts['scan every pair'][0]}")
    print(f"  comparisons, which is nothing; the exponent is what says it will be")
    print(f"  {counts['scan every pair'][-1]} at {SIZES[-1]}, and that is the number to carry away.")


main()
```

```text
  sizes                               4
  algorithms                          3

    size     scan every pair   sort then compare   a set
       100              4950                 638     100
       200             19900                1473     200
       400             79800                3388     400
       800            319600                7530     800

    growth when the size doubles
                              ratio  exponent   shape
    scan every pair           4.01x      2.00   quadratic
    sort then compare         2.28x      1.19   n log n
    a set                     2.00x      1.00   linear

  the counts are exact integers, so the ratio between two sizes is a
  property of the algorithm: doubling the input multiplies the work
  by about 4 for 1 of the 3, by about 2 for another, and by
  something in between for the third.

  the exponent is that measurement with the ratio's arithmetic taken
  out. It is 2.00 for the pair scan, 1.00 for the set, and
  1.19 for the sort -- and that last one is the number
  that cannot be read off the code, because nothing in a merge sort
  says `log`. It is also the number the count only finds because the
  sort's own comparisons are inside it: counting the pass over
  neighbours and not the sort makes this algorithm look linear.

  the input is shuffled rather than sorted, so the sort is measured
  in its average case rather than the one case it is fastest at.
  That choice does not change the exponent; it changes the constant
  in front of it, which is the part of a measurement that a reader
  should not trust across machines anyway.

  the ratio is the measurement that survives being written down. A
  timing would give the same shape on any machine and a different
  number on each one, so a book can only print the shape. The counts
  are the same everywhere, which is why they can be printed at all.

  the other thing the counts buy is the size at which the shape
  matters. At 100 items the quadratic version makes 4950
  comparisons, which is nothing; the exponent is what says it will be
  319600 at 800, and that is the number to carry away.
```

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

```python run
"""Chapter 58 -- counting the objects a phase creates.

Four ways to total one column, each counting the intermediate containers
it builds. The count is of objects the code creates, which is a property
of the code rather than of the interpreter.
"""

ROWS = 300


def make_rows():
    return [{"v": i % 7} for i in range(ROWS)]


def two_comprehensions(data, count):
    """A list of values, then a filtered list of them."""
    values = [row["v"] for row in data]
    count["made"] += 1
    count["held"] += len(values)
    kept = [value for value in values if value]
    count["made"] += 1
    count["held"] += len(kept)
    return sum(kept)


def sorted_copy(data, count):
    """One container, because the filter is folded into the sort."""
    kept = sorted(row["v"] for row in data if row["v"])
    count["made"] += 1
    count["held"] += len(kept)
    return sum(kept)


def one_pass(data, count):
    """No container at all: the loop adds as it goes."""
    total = 0
    for row in data:
        if row["v"]:
            total += row["v"]
    return total


WAYS = [
    ("two comprehensions", two_comprehensions),
    ("a sorted copy", sorted_copy),
    ("one pass", one_pass),
]


def main():
    data = make_rows()
    print(f"  rows                                {ROWS}")
    print()
    print("    how the column is totalled      containers   items held")
    results = []
    totals = []
    for name, way in WAYS:
        count = {"made": 0, "held": 0}
        totals.append(way(data, count))
        results.append((name, count["made"], count["held"]))
    for name, made, held in results:
        print("    {:<32}{:>10}{:>13}".format(name, made, held))
    print()

    same = len(set(totals)) == 1
    print("    the three totals                    {}".format(
        "identical" if same else "different"))
    print("    the answer                          {}".format(totals[0]))
    print()

    heavy = max(results, key=lambda r: r[2])
    light = min(results, key=lambda r: r[2])
    print(f"  all three produce the same number, and `{heavy[0]}` holds")
    print(f"  {heavy[2]} items in intermediates to produce it, against {light[2]} for")
    print(f"  `{light[0]}`.")
    print()
    print("  the count is of containers the code asks for, which is why it is")
    print("  the same on every machine. `sys.getsizeof` would give you a byte")
    print("  count and that count depends on the interpreter build, so it")
    print("  cannot be written into a book -- but `how many lists did this")
    print("  function make, and how long were they` can be, and it is the")
    print("  part of the cost that a reader can act on.")
    print()
    print("  the reason to look at this number at all is the peak. two")
    print("  containers of a few hundred small integers is nothing; the same")
    print("  shape over a million rows is two lists of a million, and the")
    print("  fix is not to make the lists smaller but to stop making them --")
    print("  which is what the third way does, and it is shorter to write.")


main()
```

```text
  rows                                300

    how the column is totalled      containers   items held
    two comprehensions                       2          557
    a sorted copy                            1          257
    one pass                                 0            0

    the three totals                    identical
    the answer                          897

  all three produce the same number, and `two comprehensions` holds
  557 items in intermediates to produce it, against 0 for
  `one pass`.

  the count is of containers the code asks for, which is why it is
  the same on every machine. `sys.getsizeof` would give you a byte
  count and that count depends on the interpreter build, so it
  cannot be written into a book -- but `how many lists did this
  function make, and how long were they` can be, and it is the
  part of the cost that a reader can act on.

  the reason to look at this number at all is the peak. two
  containers of a few hundred small integers is nothing; the same
  shape over a million rows is two lists of a million, and the
  fix is not to make the lists smaller but to stop making them --
  which is what the third way does, and it is shorter to write.
```

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

```python run
"""Chapter 58 -- who calls the hot function.

One field-touching function with four call sites. The count is of calls
attributed to the site that made them, which is what decides whether the
function or a caller is the thing to change.
"""

DOCS = 200
FIELDS = 20

CALL_SITES = ["load_header", "load_body", "load_footer", "validate"]


def touch(field, site, count):
    count[site] = count.get(site, 0) + 1
    return field.strip().lower()


def load_header(doc, count):
    return touch(doc["id"], "load_header", count)


def load_body(doc, count):
    out = []
    for field in doc["fields"]:
        out.append(touch(field, "load_body", count))
    return out


def load_footer(doc, count):
    return touch(doc["tail"], "load_footer", count)


def validate(doc, count):
    """Touches every field the loaders have already touched, plus the tail."""
    for field in doc["fields"]:
        touch(field, "validate", count)
    touch(doc["tail"], "validate", count)
    return True


def make_doc(index):
    return {
        "id": "doc-%d" % index,
        "tail": "tail-%d" % index,
        "fields": ["f%d" % (i % 9) for i in range(FIELDS)],
    }


def run():
    count = {}
    for index in range(DOCS):
        doc = make_doc(index)
        load_header(doc, count)
        load_body(doc, count)
        load_footer(doc, count)
        validate(doc, count)
    return count


def main():
    count = run()
    total = sum(count.values())
    fields = DOCS * FIELDS
    print(f"  documents                           {DOCS}")
    print(f"  fields per document                 {FIELDS}")
    print(f"  fields touched at least once      {fields:>8}")
    print()
    print("    call site       calls   share of all calls")
    for site in CALL_SITES:
        print("    {:<14}{:>8}{:>18.1f}%".format(site, count[site],
                                                100.0 * count[site] / total))
    print("    {:<14}{:>8}{:>18}".format("total", total, "100.0%"))
    print()

    ranked = sorted(CALL_SITES, key=lambda s: -count[s])
    top = ranked[0]
    other = ranked[1]
    per_field = total / fields
    print("    the same function, entered       %6d times" % total)
    print("    to touch                         %6d fields" % fields)
    print("    so each field is touched         %6.2f times" % per_field)
    print()
    print(f"  `touch` is one function entered from {len(CALL_SITES)} places. The largest")
    print(f"  single caller is `{top}` with {count[top]} calls, {100.0 * count[top] / total:.1f}% of")
    print(f"  everything done inside it, and `{other}` is within")
    print(f"  {100.0 * (count[top] - count[other]) / total:.1f} points of that.")
    print()
    print("  the second of those two is the finding. `validate` walks the")
    print("  fields the loaders have just walked, so a walk that has already")
    print("  happened happens again, and a count is what makes a duplicate")
    print("  pass look like work instead of looking like care.")
    print()
    print(f"  halving the cost of `touch` removes {total // 2} units and edits a")
    print(f"  function that {len(CALL_SITES)} call sites share. Deleting the repeat removes")
    print(f"  {count[top]} units and edits one caller. Those are the same size of")
    print("  win, and only one of them is a deletion.")
    print()
    print("  a profile of this program reports one row for `touch`, at 100% of")
    print("  the time, because every call goes through it. The count of who")
    print("  called it is the column a profile does not have, and here it is")
    print("  the column that says what to delete.")


main()
```

```text
  documents                           200
  fields per document                 20
  fields touched at least once          4000

    call site       calls   share of all calls
    load_header        200               2.3%
    load_body         4000              46.5%
    load_footer        200               2.3%
    validate          4200              48.8%
    total             8600            100.0%

    the same function, entered         8600 times
    to touch                           4000 fields
    so each field is touched           2.15 times

  `touch` is one function entered from 4 places. The largest
  single caller is `validate` with 4200 calls, 48.8% of
  everything done inside it, and `load_body` is within
  2.3 points of that.

  the second of those two is the finding. `validate` walks the
  fields the loaders have just walked, so a walk that has already
  happened happens again, and a count is what makes a duplicate
  pass look like work instead of looking like care.

  halving the cost of `touch` removes 4300 units and edits a
  function that 4 call sites share. Deleting the repeat removes
  4200 units and edits one caller. Those are the same size of
  win, and only one of them is a deletion.

  a profile of this program reports one row for `touch`, at 100% of
  the time, because every call goes through it. The count of who
  called it is the column a profile does not have, and here it is
  the column that says what to delete.
```

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

```python run
"""Chapter 58 -- how many runs a measurement needs.

Five candidates whose true costs differ by twenty units, measured with a
deterministic wobble that is three times larger. The count is of how many
of the five positions a single run gets right.
"""

# A fixed sequence, so this program prints the same bytes on every run.
# Real noise is not this polite; the only property being modelled is that
# it is larger than the gaps between the candidates. The nine values are
# symmetric about zero, which is what lets a median of nine runs land on
# the true value.
WOBBLE = [-60, 45, -30, 60, -45, 30, 15, -15, 0]
AMPLITUDE = 60

CANDIDATES = [
    ("format a row", 100),
    ("copy a dict", 120),
    ("strip a field", 140),
    ("look up a key", 160),
    ("compare a date", 180),
]

RUNS = len(WOBBLE)
NAMES = [name for name, _ in CANDIDATES]
EXACT = {name: cost for name, cost in CANDIDATES}


def wobble(seed, index):
    return WOBBLE[(seed + index) % len(WOBBLE)]


def estimate(seed):
    return {name: cost + wobble(seed, index)
            for index, (name, cost) in enumerate(CANDIDATES)}


def rank_of(values):
    return [name for name, _ in sorted(values.items(), key=lambda kv: kv[1])]


def true_rank():
    return [name for name, _ in sorted(CANDIDATES, key=lambda c: c[1])]


def positions_right(ranking, truth):
    return sum(1 for a, b in zip(ranking, truth) if a == b)


def median(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def main():
    gap = CANDIDATES[1][1] - CANDIDATES[0][1]
    truth = true_rank()
    print(f"  candidates                          {len(CANDIDATES)}")
    print(f"  runs                                {RUNS}")
    print(f"  gap between neighbours              {gap}")
    print(f"  wobble, either way                  {AMPLITUDE}")
    print()
    print("    run 1, the five estimates")
    first = estimate(1)
    for name in NAMES:
        print("    {:<18}{:>7}".format(name, first[name]))
    print()
    print("    run 1 ranks them as")
    first_rank = rank_of(first)
    for index, name in enumerate(first_rank, 1):
        print("    {:<3}{:<18}{:>6}".format(index, name, first[name]))
    print()
    print("    how many of the five positions each run gets right")
    per_run = []
    for seed in range(1, RUNS + 1):
        right = positions_right(rank_of(estimate(seed)), truth)
        per_run.append(right)
        print("    run {:<3}{:>6} of {}".format(seed, right, len(NAMES)))
    print()

    pooled = {name: median([estimate(seed)[name] for seed in range(1, RUNS + 1)])
              for name in NAMES}
    pooled_rank = rank_of(pooled)
    print("    the median of the nine runs, ranked")
    for index, name in enumerate(pooled_rank, 1):
        print("    {:<3}{:<18}{:>6}".format(index, name, pooled[name]))
    print()

    total = sum(per_run)
    print(f"  a single run gets {per_run[0]} of the {len(NAMES)} positions right, and the")
    print(f"  nine runs average {total / RUNS:.2f}. The gaps between neighbours are")
    print(f"  {gap} units and the wobble is {AMPLITUDE}, so a single run is ranking the")
    print("  wobble rather than the candidates.")
    print()
    print(f"  the median of the nine gets {positions_right(pooled_rank, truth)} of {len(NAMES)}, because the")
    print("  wobble is symmetric about zero and a median of an odd number of")
    print("  runs removes a symmetric error. That is the whole argument for")
    print("  repeating a measurement and taking the middle one rather than")
    print("  the best one.")
    print()
    print(f"  counting the work instead gets {positions_right(rank_of(EXACT), truth)} of {len(NAMES)} on the first")
    print("  run and needs no repetition at all, because a count of operations")
    print("  is an integer the code produces rather than a duration a machine")
    print("  produces. That is the trade: a count is the more useful unit and")
    print("  it measures a different thing than elapsed time does.")
    print()
    print(f"  when there is no count to make, the number that decides how many")
    print(f"  runs are enough is the gap you are trying to resolve. Here {gap} units")
    print(f"  needs the wobble down to well under {gap}, which one run cannot do and")
    print("  nine runs can.")


main()
```

```text
  candidates                          5
  runs                                9
  gap between neighbours              20
  wobble, either way                  60

    run 1, the five estimates
    format a row          145
    copy a dict            90
    strip a field         200
    look up a key         115
    compare a date        210

    run 1 ranks them as
    1  copy a dict           90
    2  look up a key        115
    3  format a row         145
    4  strip a field        200
    5  compare a date       210

    how many of the five positions each run gets right
    run 1       1 of 5
    run 2       3 of 5
    run 3       0 of 5
    run 4       2 of 5
    run 5       0 of 5
    run 6       2 of 5
    run 7       0 of 5
    run 8       1 of 5
    run 9       1 of 5

    the median of the nine runs, ranked
    1  format a row         100
    2  copy a dict          120
    3  strip a field        140
    4  look up a key        160
    5  compare a date       180

  a single run gets 1 of the 5 positions right, and the
  nine runs average 1.11. The gaps between neighbours are
  20 units and the wobble is 60, so a single run is ranking the
  wobble rather than the candidates.

  the median of the nine gets 5 of 5, because the
  wobble is symmetric about zero and a median of an odd number of
  runs removes a symmetric error. That is the whole argument for
  repeating a measurement and taking the middle one rather than
  the best one.

  counting the work instead gets 5 of 5 on the first
  run and needs no repetition at all, because a count of operations
  is an integer the code produces rather than a duration a machine
  produces. That is the trade: a count is the more useful unit and
  it measures a different thing than elapsed time does.

  when there is no count to make, the number that decides how many
  runs are enough is the gap you are trying to resolve. Here 20 units
  needs the wobble down to well under 20, which one run cannot do and
  nine runs can.
```

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

```python run
"""Chapter 58 -- predicting the size you have not run.

Three algorithms counted at four sizes, each fit to an exponent from the
ratios, then used to predict a fifth size. The prediction is then checked
against a count taken at that size.
"""

import math

MEASURED = [100, 200, 400, 800]
PREDICTED = 1600


def pair_scan(items, count):
    """Every pair of positions, once."""
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            count[0] += 1
    return count[0]


def merge_sort(items, count):
    """Comparisons made by a merge sort, counted where they happen."""
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], count)
    right = merge_sort(items[mid:], count)
    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        count[0] += 1
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def one_pass(items, count):
    for _item in items:
        count[0] += 1
    return count[0]


ALGORITHMS = [
    ("scan every pair", pair_scan),
    ("merge sort", merge_sort),
    ("one pass", one_pass),
]


def measure(items, algorithm):
    count = [0]
    algorithm(items, count)
    return count[0]


def exponent(series):
    """The power the counts grow as, fitted from the measured ratios."""
    logs = [math.log(series[i + 1] / series[i]) for i in range(len(series) - 1)]
    return sum(logs) / len(logs) / math.log(2)


def main():
    print(f"  measured sizes                      {MEASURED}")
    print(f"  size to predict                     {PREDICTED}")
    print()
    counts = {}
    print("    size     scan every pair    merge sort    one pass")
    for size in MEASURED:
        items = list(range(size))
        cells = []
        for name, algorithm in ALGORITHMS:
            value = measure(items, algorithm)
            counts.setdefault(name, []).append(value)
            cells.append(value)
        print("    {:>6}{:>18}{:>14}{:>12}".format(size, *cells))
    print()

    print("    fitted from the ratios, and checked at %d" % PREDICTED)
    print("    {:<18}{:>9}{:>12}{:>12}{:>9}".format(
        "", "power", "predicted", "measured", "error"))
    errors = []
    for name, algorithm in ALGORITHMS:
        series = counts[name]
        power = exponent(series)
        predicted = series[-1] * (PREDICTED / MEASURED[-1]) ** power
        actual = measure(list(range(PREDICTED)), algorithm)
        error = 100.0 * (predicted - actual) / actual
        errors.append((name, power, predicted, actual, error))
        print("    {:<18}{:>8.2f}{:>12.0f}{:>12}{:>8.1f}%".format(
            name, power, predicted, actual, error))
    print()

    worst = max(errors, key=lambda entry: abs(entry[4]))
    print("  the fit is from four counts, and the check is a size the program")
    print(f"  has not run when it makes the prediction. The worst of the three")
    print(f"  predictions is off by {abs(worst[4]):.1f}%, and it is `{worst[0]}`.")
    print()
    print("  that is what a complexity class is for. It is not a label to")
    print("  write beside a function; it is the thing that answers `what")
    print("  happens at ten times the size` without running it, which is the")
    print("  question that decides whether a design can ship.")
    print()
    print("  the linear and the quadratic fit are almost exact, because the")
    print("  counts are integers and the ratios have nowhere to hide. The")
    print("  middle column is the interesting one: a sort's comparisons grow")
    print("  by a little more than two per doubling, and the fit lands near")
    print("  that without the code saying so anywhere.")
    print()
    print("  so the number to carry away is the ratio rather than the count.")
    print("  Doubling the input multiplies the work by about 4 for the pair")
    print("  scan, by about 2 for the pass, and by a number in between for")
    print("  the sort, and those three numbers are the same on every machine")
    print("  -- which is the only reason they can be written down at all.")


main()
```

```text
  measured sizes                      [100, 200, 400, 800]
  size to predict                     1600

    size     scan every pair    merge sort    one pass
       100              4950           316         100
       200             19900           732         200
       400             79800          1664         400
       800            319600          3728         800

    fitted from the ratios, and checked at 1600
                          power   predicted    measured    error
    scan every pair       2.00     1282155     1279200     0.2%
    merge sort            1.19        8487        8256     2.8%
    one pass              1.00        1600        1600     0.0%

  the fit is from four counts, and the check is a size the program
  has not run when it makes the prediction. The worst of the three
  predictions is off by 2.8%, and it is `merge sort`.

  that is what a complexity class is for. It is not a label to
  write beside a function; it is the thing that answers `what
  happens at ten times the size` without running it, which is the
  question that decides whether a design can ship.

  the linear and the quadratic fit are almost exact, because the
  counts are integers and the ratios have nowhere to hide. The
  middle column is the interesting one: a sort's comparisons grow
  by a little more than two per doubling, and the fit lands near
  that without the code saying so anywhere.

  so the number to carry away is the ratio rather than the count.
  Doubling the input multiplies the work by about 4 for the pair
  scan, by about 2 for the pass, and by a number in between for
  the sort, and those three numbers are the same on every machine
  -- which is the only reason they can be written down at all.
```

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

```python run
"""Chapter 58 -- the peak, not the total.

Three ways to process the same five thousand rows, each counting the items
it holds at once. The total items touched is identical for all three; the
high-water mark is not.
"""

ROWS = 5000
BATCH = 32


def read_all(count):
    """One container holding every row."""
    rows = [{"v": i % 11} for i in range(ROWS)]
    count["peak"] = max(count["peak"], len(rows))
    count["touched"] += len(rows)
    total = 0
    for row in rows:
        total += row["v"]
    return total


def streamed(count):
    """One row at a time, discarded after use."""
    total = 0
    for i in range(ROWS):
        count["peak"] = max(count["peak"], 1)
        count["touched"] += 1
        total += i % 11
    return total


def batched(count):
    """A window of rows, discarded after each window."""
    total = 0
    for start in range(0, ROWS, BATCH):
        window = [{"v": i % 11} for i in range(start, min(start + BATCH, ROWS))]
        count["peak"] = max(count["peak"], len(window))
        count["touched"] += len(window)
        for row in window:
            total += row["v"]
    return total


WAYS = [
    ("read all, then process", read_all),
    ("one row at a time", streamed),
    ("a window of %d" % BATCH, batched),
]


def main():
    print(f"  rows                                {ROWS}")
    print()
    print("    how the rows are read         items touched   peak live at once")
    results = []
    totals = []
    for name, way in WAYS:
        count = {"touched": 0, "peak": 0}
        totals.append(way(count))
        results.append((name, count["touched"], count["peak"]))
    for name, touched, peak in results:
        print("    {:<29}{:>14}{:>20}".format(name, touched, peak))
    print()

    same = len(set(totals)) == 1
    print("    the three totals                    {}".format(
        "identical" if same else "different"))
    print("    the answer                          {}".format(totals[0]))
    print()

    heavy = max(results, key=lambda row: row[2])
    light = min(results, key=lambda row: row[2])
    window = results[2]
    print("  all three read every row exactly once, so the column a")
    print(f"  `total work` measurement reports is {results[0][1]} for all three and")
    print(f"  cannot tell them apart. The peak separates them: {heavy[2]} rows")
    print(f"  live at once, or {window[2]}, or {light[2]}.")
    print()
    print("  that ratio is the subject of this block. The total decides how")
    print("  long a program takes; the peak decides whether it runs at all,")
    print("  because a machine that cannot hold the peak does not run slowly.")
    print("  It stops, and it stops at the row where the peak is reached.")
    print()
    print("  the fix is a change of shape rather than a change of speed. Both")
    print(f"  of the others read the same {ROWS} rows and do the same additions:")
    print(f"  the window holds {window[2]} rows at a time and the streaming version")
    print(f"  holds {light[2]}. Reading a file in chunks is not longer code than")
    print("  reading it whole; it is one extra loop.")
    print()
    print("  the count here is of containers the code asks for, which is why")
    print("  it is the same on every machine. `tracemalloc` reports the same")
    print("  shape in bytes and a different number on each interpreter build,")
    print("  so the shape is what a book can print and the bytes are what a")
    print("  profiler is for.")


main()
```

```text
  rows                                5000

    how the rows are read         items touched   peak live at once
    read all, then process                 5000                5000
    one row at a time                      5000                   1
    a window of 32                         5000                  32

    the three totals                    identical
    the answer                          24985

  all three read every row exactly once, so the column a
  `total work` measurement reports is 5000 for all three and
  cannot tell them apart. The peak separates them: 5000 rows
  live at once, or 32, or 1.

  that ratio is the subject of this block. The total decides how
  long a program takes; the peak decides whether it runs at all,
  because a machine that cannot hold the peak does not run slowly.
  It stops, and it stops at the row where the peak is reached.

  the fix is a change of shape rather than a change of speed. Both
  of the others read the same 5000 rows and do the same additions:
  the window holds 32 rows at a time and the streaming version
  holds 1. Reading a file in chunks is not longer code than
  reading it whole; it is one extra loop.

  the count here is of containers the code asks for, which is why
  it is the same on every machine. `tracemalloc` reports the same
  shape in bytes and a different number on each interpreter build,
  so the shape is what a book can print and the bytes are what a
  profiler is for.
```

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

```python run
"""Chapter 58 -- the order to make the fixes in.

Six fixes to one report, each with the work it removes and the lines it
changes. Both of those are counted, so the order is not a matter of taste.
"""

TOTAL_WORK = 206970

# name, work removed, lines changed
FIXES = [
    ("a join for the string", 184335, 2),
    ("a global memo", 60000, 40),
    ("a set for the dedupe", 19700, 3),
    ("a check off the hot path", 400, 1),
    ("a cached format string", 200, 4),
    ("fewer rows to start with", 200, 6),
]


def per_line(fix):
    return fix[1] / fix[2]


def main():
    print(f"  work in the report                 {TOTAL_WORK}")
    print(f"  fixes considered                    {len(FIXES)}")
    print()
    print("    {:<33}{:>11}{:>8}{:>11}".format("fix", "work removed", "lines",
                                                "per line"))
    for name, work, lines in FIXES:
        print("    {:<33}{:>11}{:>8}{:>11.0f}".format(name, work, lines,
                                                   work / lines))
    print()

    by_work = sorted(FIXES, key=lambda fix: -fix[1])
    by_line = sorted(FIXES, key=lambda fix: -per_line(fix))
    print("    {:<24}{:>10}   {:<24}{:>10}".format(
        "ranked by work removed", "", "ranked by work per line", ""))
    for left, right in zip(by_work, by_line):
        print("    {:<24}{:>10}   {:<24}{:>10.0f}".format(
            left[0], left[1], right[0], per_line(right)))
    print()

    moved = [index for index, (left, right) in
             enumerate(zip(by_work, by_line), 1) if left[0] != right[0]]
    print(f"  the two orders disagree in {len(moved)} of the {len(FIXES)} positions.")
    print()

    top = by_work[0]
    second = by_work[1]
    alt = by_line[1]
    print(f"  both orders put `{top[0]}` first, and it is the one")
    print(f"  everybody finds: {top[1]} units and {top[2]} lines.")
    print()
    print(f"  they part company at the second move. `{second[0]}` removes")
    print(f"  {second[1]} units in {second[2]} lines; `{alt[0]}` removes {alt[1]} in")
    print(f"  {alt[2]}. The first is worth {second[1] / alt[1]:.1f} times the work and costs")
    print(f"  {second[2] / alt[2]:.1f} times the lines, so per line it is the worse of the")
    print(f"  two -- {per_line(second):.0f} against {per_line(alt):.0f}.")
    print()
    print("  the ranking to use is the second one, and the reason is not that")
    print("  small changes are safer. It is that a fix has to survive review")
    print("  before it removes anything, and the lines changed is the part of")
    print("  that cost which is countable. Work removed per line changed is a")
    print("  real ratio, and it is the one that orders the list here.")
    print()
    print("  the two fixes at the bottom are the ones a reader reaches for")
    print("  first, because they are the ones with an obvious better spelling.")
    print(f"  Together they are {FIXES[4][1] + FIXES[5][1]} units out of {TOTAL_WORK}, so the")
    print("  order they appear in does not matter at all.")


main()
```

```text
  work in the report                 206970
  fixes considered                    6

    fix                              work removed   lines   per line
    a join for the string                 184335       2      92168
    a global memo                          60000      40       1500
    a set for the dedupe                   19700       3       6567
    a check off the hot path                 400       1        400
    a cached format string                   200       4         50
    fewer rows to start with                 200       6         33

    ranked by work removed               ranked by work per line           
    a join for the string       184335   a join for the string        92168
    a global memo                60000   a set for the dedupe          6567
    a set for the dedupe         19700   a global memo                 1500
    a check off the hot path       400   a check off the hot path       400
    a cached format string         200   a cached format string          50
    fewer rows to start with       200   fewer rows to start with        33

  the two orders disagree in 2 of the 6 positions.

  both orders put `a join for the string` first, and it is the one
  everybody finds: 184335 units and 2 lines.

  they part company at the second move. `a global memo` removes
  60000 units in 40 lines; `a set for the dedupe` removes 19700 in
  3. The first is worth 3.0 times the work and costs
  13.3 times the lines, so per line it is the worse of the
  two -- 1500 against 6567.

  the ranking to use is the second one, and the reason is not that
  small changes are safer. It is that a fix has to survive review
  before it removes anything, and the lines changed is the part of
  that cost which is countable. Work removed per line changed is a
  real ratio, and it is the one that orders the list here.

  the two fixes at the bottom are the ones a reader reaches for
  first, because they are the ones with an obvious better spelling.
  Together they are 400 units out of 206970, so the
  order they appear in does not matter at all.
```

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

```python run
"""Chapter 58 -- the benchmark that measures something else.

Six benchmark designs, each declared to measure the same function over
the same fifty inputs. The count is of how many times that function was
actually entered, which is what decides whether the number means
anything.
"""

CALLS = [0]


def parse(text):
    CALLS[0] += 1
    return len(text.split())


TEXTS = ["a b c"] * 50
CACHE = {}


def cached_parse(text):
    if text not in CACHE:
        CACHE[text] = parse(text)
    return CACHE[text]


for _text in TEXTS:
    cached_parse(_text)
CALLS[0] = 0


def warm_the_cache():
    for text in TEXTS:
        cached_parse(text)


def the_loop():
    for text in TEXTS:
        parse(text)


def copy_the_input():
    TEXTS[:]


def an_empty_loop():
    for text in []:
        parse(text)


def the_wrong_function():
    for text in TEXTS:
        len(text)


def one_call_not_fifty():
    parse(TEXTS[0])


BENCHMARKS = [
    ("the loop over the texts", the_loop),
    ("the memoised wrapper", warm_the_cache),
    ("a copy of the input", copy_the_input),
    ("an empty loop", an_empty_loop),
    ("len() instead of parse()", the_wrong_function),
    ("one call, not fifty", one_call_not_fifty),
]

DECLARED = 50


def main():
    print(f"  inputs                              {len(TEXTS)}")
    print(f"  benchmarks                          {len(BENCHMARKS)}")
    print()
    print("    benchmark                    declared   parse() was entered")
    rows = []
    for name, benchmark in BENCHMARKS:
        CALLS[0] = 0
        benchmark()
        rows.append((name, CALLS[0]))
        print("    {:<29}{:>8}{:>22}".format(name, DECLARED, CALLS[0]))
    print()

    right = sum(1 for _, entered in rows if entered == DECLARED)
    zero = sum(1 for _, entered in rows if entered == 0)
    verb = "enters" if right == 1 else "enter"
    print(f"  {right} of the {len(BENCHMARKS)} benchmarks {verb} the function as many")
    print(f"  times as it claims. {zero} of them never enter it at all, and the")
    print("  number each one produces is a real measurement of something --")
    print("  a dict lookup, a list copy, an empty loop, `len`, or one call")
    print("  instead of fifty.")
    print()
    print("  none of those six designs would look wrong in a file. every one")
    print("  of them is a loop, or a call, inside a timer, and the only thing")
    print("  that separates them is whether the code under test is the code")
    print("  that ran.")
    print()
    print("  that is what makes this the first trap of the subject. a")
    print("  measurement is a claim, and the claim has two halves: this is")
    print("  the number, and this is what produced it. the second half is")
    print("  the one that goes missing, and the way to keep it is to count")
    print("  something the code under test controls -- entries, comparisons,")
    print("  containers -- and check that the count is what you expected")
    print("  before you look at the number at all.")


main()
```

```text
  inputs                              50
  benchmarks                          6

    benchmark                    declared   parse() was entered
    the loop over the texts            50                    50
    the memoised wrapper               50                     0
    a copy of the input                50                     0
    an empty loop                      50                     0
    len() instead of parse()           50                     0
    one call, not fifty                50                     1

  1 of the 6 benchmarks enters the function as many
  times as it claims. 4 of them never enter it at all, and the
  number each one produces is a real measurement of something --
  a dict lookup, a list copy, an empty loop, `len`, or one call
  instead of fifty.

  none of those six designs would look wrong in a file. every one
  of them is a loop, or a call, inside a timer, and the only thing
  that separates them is whether the code under test is the code
  that ran.

  that is what makes this the first trap of the subject. a
  measurement is a claim, and the claim has two halves: this is
  the number, and this is what produced it. the second half is
  the one that goes missing, and the way to keep it is to count
  something the code under test controls -- entries, comparisons,
  containers -- and check that the count is what you expected
  before you look at the number at all.
```

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

```python run
"""Chapter 58 -- the scenario. A slow report.

Five phases, each counting its own work, and four candidate fixes. The
count is of the work each fix removes, which is what decides the order to
try them in.
"""

ROWS = 200


def load(count):
    out = []
    for i in range(ROWS):
        count["load"] += 1
        out.append({"id": i, "name": "row-%d" % i, "v": i % 13})
    return out


def dedupe(rows, count):
    """Every row against every row already kept."""
    kept = []
    for row in rows:
        for other in kept:
            count["dedupe"] += 1
            if other["id"] == row["id"]:
                break
        else:
            kept.append(row)
    return kept


def render(rows, count):
    out = []
    for row in rows:
        count["render"] += 1
        out.append("%s=%d" % (row["name"], row["v"]))
    return out


def join_all(lines, count):
    out = ""
    for line in lines:
        count["join"] += len(out)
        out += line + "\n"
    return out


def write(text, count):
    for _line in text.splitlines():
        count["write"] += 1
    return len(text)


PHASES = [
    ("load", load),
    ("dedupe", dedupe),
    ("render", render),
    ("join", join_all),
    ("write", write),
]


def measure():
    count = {name: 0 for name, _ in PHASES}
    rows = None
    for name, phase in PHASES:
        if name == "load":
            rows = phase(count)
        elif name == "write":
            phase(rows, count)
        else:
            rows = phase(rows, count)
    return count


def fixed_dedupe():
    count = {name: 0 for name, _ in PHASES}
    count["load"] = ROWS
    rows = [{"id": i, "name": "row-%d" % i, "v": i % 13} for i in range(ROWS)]
    seen = set()
    for row in rows:
        count["dedupe"] += 1
        seen.add(row["id"])
    return count


def fixed_join():
    lines = ["row-%d=%d" % (i, i % 13) for i in range(ROWS)]
    out = "".join(line + "\n" for line in lines)
    count = {name: 0 for name, _ in PHASES}
    count["join"] = len(out) + ROWS
    return count


def main():
    count = measure()
    total = sum(count.values())
    print(f"  rows                                {ROWS}")
    print(f"  phases                              {len(PHASES)}")
    print()
    print("    phase      work units   share")
    for name, _ in PHASES:
        share = 100.0 * count[name] / total
        print("    {:<11}{:>10}{:>9.1f}%".format(name, count[name], share))
    print("    {:<11}{:>10}{:>9}".format("total", total, "100.0%"))
    print()

    print("    the work each candidate fix removes")
    fixes = []
    dedupe = fixed_dedupe()
    removed = count["dedupe"] - dedupe["dedupe"]
    fixes.append(("a set for the dedupe", removed))
    join = fixed_join()
    removed_join = count["join"] - join["join"]
    fixes.append(("a join for the string", removed_join))
    fixes.append(("a cached format string", count["render"]))
    fixes.append(("fewer rows to start with", count["load"]))
    for name, removed in sorted(fixes, key=lambda f: -f[1]):
        print("    {:<30}{:>10}  {:.1f}% of the total".format(
            name, removed, 100.0 * removed / total))
    print()

    ranked = sorted(fixes, key=lambda f: -f[1])
    print(f"  `{ranked[0][0]}` removes {ranked[0][1]} work units and")
    print(f"  `{ranked[-1][0]}` removes {ranked[-1][1]}, so the order to try")
    print("  them in is not the order they look easiest in.")
    print()
    print("  the two that matter are both loops that look like one line. the")
    print("  dedupe is a nested loop with a `break`, which reads as a scan")
    print("  and is quadratic; the join is a `+=` on a string, which reads as")
    print("  an append and copies the whole string every time. neither is")
    print("  visible by reading, and both are visible by counting.")
    print()
    print("  the two that do not matter are the ones a reader would reach for")
    print("  first, because they are the ones with an obvious better")
    print("  spelling. the format string can be cached and the row count can")
    print("  be trimmed, and together they are a few hundred units out of a")
    print("  number in the hundreds of thousands.")
    print()
    print("  that is the whole reason to measure before optimising. the four")
    print("  fixes are all correct, all worth doing eventually, and only two")
    print("  of them change the answer.")


main()
```

```text
  rows                                200
  phases                              5

    phase      work units   share
    load              200      0.1%
    dedupe          19900      9.6%
    render            200      0.1%
    join           186470     90.1%
    write             200      0.1%
    total          206970   100.0%

    the work each candidate fix removes
    a join for the string             184335  89.1% of the total
    a set for the dedupe               19700  9.5% of the total
    a cached format string               200  0.1% of the total
    fewer rows to start with             200  0.1% of the total

  `a join for the string` removes 184335 work units and
  `fewer rows to start with` removes 200, so the order to try
  them in is not the order they look easiest in.

  the two that matter are both loops that look like one line. the
  dedupe is a nested loop with a `break`, which reads as a scan
  and is quadratic; the join is a `+=` on a string, which reads as
  an append and copies the whole string every time. neither is
  visible by reading, and both are visible by counting.

  the two that do not matter are the ones a reader would reach for
  first, because they are the ones with an obvious better
  spelling. the format string can be cached and the row count can
  be trimmed, and together they are a few hundred units out of a
  number in the hundreds of thousands.

  that is the whole reason to measure before optimising. the four
  fixes are all correct, all worth doing eventually, and only two
  of them change the answer.
```

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

```python run
"""Solution 1 -- which of five loops to fix.

A report builder is instrumented by counting rather than by timing. The
count is of the work each of its five loops does, in the unit that loop
works in.
"""

ROWS = 200


def build(rows, count):
    parsed = []
    for row in rows:
        count["parse"] += 1
        parsed.append(row.split(","))
    kept = []
    for row in parsed:
        for other in kept:
            count["dedupe"] += 1
            if other[0] == row[0]:
                break
        else:
            kept.append(row)
    enriched = []
    for row in kept:
        count["enrich"] += 1
        enriched.append({"id": row[0], "n": len(row)})
    ordered = merge_sort(enriched, count)
    lines = []
    for row in ordered:
        count["format"] += 1
        lines.append("%s:%d" % (row["id"], row["n"]))
    return lines


def merge_sort(items, count):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], count)
    right = merge_sort(items[mid:], count)
    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        count["sort"] += 1
        if left[i]["id"] <= right[j]["id"]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


LOOPS = ["parse", "dedupe", "enrich", "sort", "format"]


def main():
    rows = ["id-%d,%d" % (i, i % 7) for i in range(ROWS)]
    count = {name: 0 for name in LOOPS}
    lines = build(rows, count)
    total = sum(count.values())
    print(f"  rows                                {ROWS}")
    print(f"  lines produced                      {len(lines)}")
    print()
    print("    loop        work units   share")
    for name in LOOPS:
        print("    {:<12}{:>10}{:>9.1f}%".format(name, count[name],
                                                100.0 * count[name] / total))
    print("    {:<12}{:>10}{:>9}".format("total", total, "100.0%"))
    print()

    ranked = sorted(LOOPS, key=lambda name: -count[name])
    top = ranked[0]
    per_row = [name for name in LOOPS if name != top and count[name] == ROWS]
    sort_name = [name for name in LOOPS if name not in per_row and name != top][0]
    print(f"  `{top}` does {count[top]} of the {total} units, {100.0 * count[top] / total:.1f}% of the")
    print(f"  work. The other four together do {total - count[top]}.")
    print()
    print(f"  {len(per_row)} of those four do exactly {ROWS} units, one per row, and the")
    print(f"  fourth is `{sort_name}` at {count[sort_name]}, or about {count[sort_name] // ROWS}")
    print(f"  units per row. Only `{top}` grows with the square of the row")
    print("  count, and it is the only one of the five that contains a")
    print("  second loop.")
    print()
    print("  that is the answer the instrumentation was there to produce, and")
    print("  it is not visible in the source. Four of the five loops are two")
    print("  or three lines and the fifth is two or three lines as well; the")
    print("  difference is that one of them compares a row against rows")
    print("  already kept, so its count grows with the square.")
    print()
    print("  the fix replaces the kept-list scan with a set of the ids seen")
    print(f"  so far. `{top}` then costs {ROWS} units like the others and the report")
    print(f"  falls from {total} units to about {total - count[top] + ROWS}. Nothing else in")
    print("  the function needs to change, and the counts are what says so.")


main()
```

```text
  rows                                200
  lines produced                      200

    loop        work units   share
    parse              200      0.9%
    dedupe           19900     93.4%
    enrich             200      0.9%
    sort               815      3.8%
    format             200      0.9%
    total            21315   100.0%

  `dedupe` does 19900 of the 21315 units, 93.4% of the
  work. The other four together do 1415.

  3 of those four do exactly 200 units, one per row, and the
  fourth is `sort` at 815, or about 4
  units per row. Only `dedupe` grows with the square of the row
  count, and it is the only one of the five that contains a
  second loop.

  that is the answer the instrumentation was there to produce, and
  it is not visible in the source. Four of the five loops are two
  or three lines and the fifth is two or three lines as well; the
  difference is that one of them compares a row against rows
  already kept, so its count grows with the square.

  the fix replaces the kept-list scan with a set of the ids seen
  so far. `dedupe` then costs 200 units like the others and the report
  falls from 21315 units to about 1615. Nothing else in
  the function needs to change, and the counts are what says so.
```

:::

:::solution Exercise 2

Two sorts that both claim to be `n log n`, counted at four sizes on the same reverse-ordered input. The
ratios reject the claim for one of them.

```python run
"""Solution 2 -- deciding between two sorts that both claim to be n log n.

Both are counted at four sizes and the ratios decide. The claim is true
for one of them and false for the other.
"""

SIZES = [200, 400, 800, 1600]


def merge_sort(items, count):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], count)
    right = merge_sort(items[mid:], count)
    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        count[0] += 1
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def insertion_sort(items, count):
    out = list(items)
    for i in range(1, len(out)):
        value = out[i]
        j = i - 1
        while j >= 0:
            count[0] += 1
            if out[j] <= value:
                break
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = value
    return out


SORTS = [
    ("merge sort", merge_sort),
    ("insertion sort", insertion_sort),
]


def main():
    print(f"  sizes                               {len(SIZES)}")
    print()
    counts = {name: [] for name, _ in SORTS}
    print("    size       merge sort   insertion sort")
    for size in SIZES:
        items = list(range(size, 0, -1))
        cells = []
        for name, sort in SORTS:
            count = [0]
            sort(items, count)
            counts[name].append(count[0])
            cells.append(count[0])
        print("    {:>6}{:>15}{:>17}".format(size, *cells))
    print()

    print("    growth when the size doubles")
    print("    {:<18}{:>9}   {}".format("", "ratio", "shape"))
    verdict = {}
    for name, _ in SORTS:
        series = counts[name]
        ratios = [series[i + 1] / series[i] for i in range(len(series) - 1)]
        average = sum(ratios) / len(ratios)
        shape = "n log n" if average < 2.6 else "quadratic"
        verdict[name] = (average, shape)
        print("    {:<18}{:>8.2f}x   {}".format(name, average, shape))
    print()

    wrong = [name for name, _ in SORTS if verdict[name][1] != "n log n"]
    good = "merge sort"
    bad = wrong[0]
    print(f"  the claim under test is that both are n log n, and the ratios")
    print(f"  reject it for {len(wrong)} of the {len(SORTS)}: {', '.join(wrong)}.")
    print()
    print("  the counts are exact integers, so the verdict does not depend on")
    print("  the machine, on the interpreter, or on how many times the program")
    print(f"  was run. Doubling the size multiplies merge sort's comparisons by")
    print(f"  {verdict[good][0]:.2f} and multiplies insertion sort's by {verdict[bad][0]:.2f}.")
    print()
    print("  the reverse-ordered input is the case insertion sort is worst at,")
    print("  and that is deliberate. A benchmark that runs the best case is")
    print("  the pitfall from earlier in this chapter wearing a different hat.")
    print("  An average over random inputs would land between the two, and a")
    print("  number between two complexity classes is not one of them.")
    print()
    print("  the first size already shows the two are different, and it cannot")
    print(f"  show why. At {SIZES[0]} the counts differ by a factor of")
    print(f"  {counts['insertion sort'][0] / counts['merge sort'][0]:.1f}, and at {SIZES[-1]} by")
    print(f"  {counts['insertion sort'][-1] / counts['merge sort'][-1]:.0f}. A single size cannot tell you which of those")
    print("  factors keeps growing, and the ratios can. A claim about growth")
    print("  needs at least three sizes to check and four to be sure the last")
    print("  ratio is not a fluke.")


main()
```

```text
  sizes                               4

    size       merge sort   insertion sort
       200            812            19900
       400           1824            79800
       800           4048           319600
      1600           8896          1279200

    growth when the size doubles
                          ratio   shape
    merge sort            2.22x   n log n
    insertion sort        4.01x   quadratic

  the claim under test is that both are n log n, and the ratios
  reject it for 1 of the 2: insertion sort.

  the counts are exact integers, so the verdict does not depend on
  the machine, on the interpreter, or on how many times the program
  was run. Doubling the size multiplies merge sort's comparisons by
  2.22 and multiplies insertion sort's by 4.01.

  the reverse-ordered input is the case insertion sort is worst at,
  and that is deliberate. A benchmark that runs the best case is
  the pitfall from earlier in this chapter wearing a different hat.
  An average over random inputs would land between the two, and a
  number between two complexity classes is not one of them.

  the first size already shows the two are different, and it cannot
  show why. At 200 the counts differ by a factor of
  24.5, and at 1600 by
  144. A single size cannot tell you which of those
  factors keeps growing, and the ratios can. A claim about growth
  needs at least three sizes to check and four to be sure the last
  ratio is not a fluke.
```

:::

:::solution Exercise 3

The same function called over the same keys with and without a memo, counting the work removed, the misses,
and the entries held at the peak.

```python run
"""Solution 3 -- what a memo does to the work and to the peak.

The same function called over the same inputs with and without a cache.
The count is of the work the function does, of the calls that miss, and of
the entries held at once.
"""

from collections import Counter

INPUTS = list(range(20))
CALL_KEYS = INPUTS + INPUTS[:12]
CALLS = len(CALL_KEYS)
REPEATED = sum(1 for _key, times in Counter(CALL_KEYS).items() if times > 1)


def expensive(key, count):
    count["work"] += 1
    total = 0
    for i in range(key % 7 + 1):
        count["work"] += 1
        total += i
    return total


def without_memo(keys, count):
    out = []
    for key in keys:
        out.append(expensive(key, count))
    return out


def with_memo(keys, count):
    cache = {}
    out = []
    for key in keys:
        if key not in cache:
            count["misses"] += 1
            cache[key] = expensive(key, count)
        count["peak"] = max(count["peak"], len(cache))
        out.append(cache[key])
    return out


WAYS = [
    ("no memo", without_memo),
    ("a memo", with_memo),
]


def main():
    print(f"  calls                               {CALLS}")
    print(f"  distinct inputs                     {len(INPUTS)}")
    print()
    print("    how it is called        work units   misses   entries held")
    rows = []
    for name, way in WAYS:
        count = {"work": 0, "misses": 0, "peak": 0}
        results = way(CALL_KEYS, count)
        rows.append((name, count["work"], count["misses"], count["peak"],
                     results))
    for name, work, misses, peak, _results in rows:
        print("    {:<22}{:>11}{:>9}{:>15}".format(name, work, misses, peak))
    print()

    same = len(set(tuple(row[4]) for row in rows)) == 1
    print("    the two return the same list          {}".format(
        "yes" if same else "no"))
    print()

    plain = rows[0]
    memo = rows[1]
    saved = plain[1] - memo[1]
    print(f"  the memo removes {saved} of the {plain[1]} units, which is")
    print(f"  {100.0 * saved / plain[1]:.1f}%, and it does that by remembering {memo[3]} answers.")
    print()
    print("  the column that got worse is the last one. The plain version")
    print(f"  holds nothing between calls; the memo holds {memo[3]} entries at its")
    print(f"  peak, and {REPEATED} of them are answers to questions the caller asked")
    print("  more than once.")
    print()
    print("  that trade is the whole of caching. The count of misses is the")
    print(f"  number to read first: {memo[2]} misses for {CALLS} calls is a hit rate of")
    print(f"  {100.0 * (CALLS - memo[2]) / CALLS:.1f}%, and a hit rate is what decides whether a")
    print("  cache is worth its memory.")
    print()
    print("  two things follow that these numbers do not show. A cache is only")
    print("  correct if the function is pure, because the second caller gets")
    print("  the first caller's answer; and it is only bounded if something")
    print("  evicts, because the entries held grows with the number of distinct")
    print("  inputs rather than with the number of calls. Here there are")
    print(f"  {len(INPUTS)} distinct inputs; with a million inputs the peak is a million.")
    print()
    print("  so the two counts to take before adding a memo are how many of")
    print("  the calls repeat and how many distinct keys there are. The first")
    print("  is the saving and the second is the cost.")


main()
```

```text
  calls                               32
  distinct inputs                     20

    how it is called        work units   misses   entries held
    no memo                       152        0              0
    a memo                         97       20             20

    the two return the same list          yes

  the memo removes 55 of the 152 units, which is
  36.2%, and it does that by remembering 20 answers.

  the column that got worse is the last one. The plain version
  holds nothing between calls; the memo holds 20 entries at its
  peak, and 12 of them are answers to questions the caller asked
  more than once.

  that trade is the whole of caching. The count of misses is the
  number to read first: 20 misses for 32 calls is a hit rate of
  37.5%, and a hit rate is what decides whether a
  cache is worth its memory.

  two things follow that these numbers do not show. A cache is only
  correct if the function is pure, because the second caller gets
  the first caller's answer; and it is only bounded if something
  evicts, because the entries held grows with the number of distinct
  inputs rather than with the number of calls. Here there are
  20 distinct inputs; with a million inputs the peak is a million.

  so the two counts to take before adding a memo are how many of
  the calls repeat and how many distinct keys there are. The first
  is the saving and the second is the cost.
```

:::

:::solution Exercise 4

Four benchmark designs run through a four-line harness that declares how many times the code under test
should be entered and reports which designs measure what they claim.

```python run
"""Solution 4 -- a benchmark that checks itself.

Four designs run through a harness that asserts how many times the code
under test was entered. The harness reports which designs measure what
they claim to.
"""

CALLS = [0]


def work(text):
    CALLS[0] += 1
    return len(text.split())


TEXTS = ["a b c"] * 30
CACHE = {}


def memoised(text):
    if text not in CACHE:
        CACHE[text] = work(text)
    return CACHE[text]


for _text in TEXTS:
    memoised(_text)
CALLS[0] = 0


def the_loop():
    for text in TEXTS:
        work(text)


def the_warm_cache():
    for text in TEXTS:
        memoised(text)


def a_copy_of_the_input():
    TEXTS[:]


def the_wrong_function():
    for text in TEXTS:
        len(text)


DESIGNS = [
    ("the loop", the_loop, len(TEXTS)),
    ("the warm cache", the_warm_cache, len(TEXTS)),
    ("a copy of the input", a_copy_of_the_input, len(TEXTS)),
    ("len instead of work", the_wrong_function, len(TEXTS)),
]


def bench(design, expected):
    """Run one design and report how many times the function was entered."""
    CALLS[0] = 0
    design()
    entered = CALLS[0]
    return entered, entered == expected


def main():
    print(f"  inputs                              {len(TEXTS)}")
    print(f"  designs                             {len(DESIGNS)}")
    print()
    print("    design                  declared   entered   verdict")
    passed = 0
    for name, design, expected in DESIGNS:
        entered, ok = bench(design, expected)
        passed += 1 if ok else 0
        verdict = "measures it" if ok else "measures something else"
        print("    {:<24}{:>8}{:>10}   {}".format(name, expected, entered,
                                                 verdict))
    print()
    print(f"  {passed} of the {len(DESIGNS)} designs measure what they declare. The other")
    print(f"  {len(DESIGNS) - passed} produce a number that is a real measurement of a real")
    print("  thing, and not of the thing they were written to measure.")
    print()
    print("  the harness is four lines and it is the part that matters. It")
    print("  resets the counter, runs the design, and compares the counter")
    print("  against the number the design declares. A design that cannot")
    print("  pass that comparison is not a slow benchmark; it is not a")
    print("  benchmark, and the difference is invisible in the source of any")
    print("  of the four above.")
    print()
    print("  the declared count is also the assumption the design rests on.")
    print(f"  Writing `{len(TEXTS)}` beside a loop over {len(TEXTS)} texts is a claim about")
    print("  the input, and the harness checks that claim against the run")
    print("  rather than against the reader's confidence.")
    print()
    print("  so the pattern for any measurement worth keeping is: count")
    print("  something the code under test controls, declare what that count")
    print("  should be, and fail loudly when it is not. The number a benchmark")
    print("  prints is worth as much as the check standing beside it.")


main()
```

```text
  inputs                              30
  designs                             4

    design                  declared   entered   verdict
    the loop                      30        30   measures it
    the warm cache                30         0   measures something else
    a copy of the input           30         0   measures something else
    len instead of work           30         0   measures something else

  1 of the 4 designs measure what they declare. The other
  3 produce a number that is a real measurement of a real
  thing, and not of the thing they were written to measure.

  the harness is four lines and it is the part that matters. It
  resets the counter, runs the design, and compares the counter
  against the number the design declares. A design that cannot
  pass that comparison is not a slow benchmark; it is not a
  benchmark, and the difference is invisible in the source of any
  of the four above.

  the declared count is also the assumption the design rests on.
  Writing `30` beside a loop over 30 texts is a claim about
  the input, and the harness checks that claim against the run
  rather than against the reader's confidence.

  so the pattern for any measurement worth keeping is: count
  something the code under test controls, declare what that count
  should be, and fail loudly when it is not. The number a benchmark
  prints is worth as much as the check standing beside it.
```

:::
