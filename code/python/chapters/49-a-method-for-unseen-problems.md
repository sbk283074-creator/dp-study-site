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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- the constraints are the specification.

A problem statement's size limit is not decoration. It is the intended
complexity, written in the only language the statement has: arithmetic.
This script does that arithmetic for every complexity class and reports the
largest n that still fits a fixed operation budget.

Everything is computed in log10 space. That is not a trick for looking
clever -- it is forced. The operation counts span more than four hundred
thousand orders of magnitude (n! at n = 100,000), so no float can hold them
and any code that tries will raise OverflowError. log10 is monotone, so a
search in log space finds exactly the same n, and every comparison stays a
comparison of small numbers.

Nothing here is timed. A count is a fact about the algorithm; a timing is a
fact about this machine.
"""
import math

BUDGET_LOG10 = 8.0          # log10(100,000,000)
N_CEILING = 10 ** 12

CLASSES = [
    ("O(1)", lambda n: 0.0),
    ("O(log n)", lambda n: math.log10(math.log2(n)) if n > 1 else 0.0),
    ("O(n)", lambda n: math.log10(n)),
    ("O(n log n)", lambda n: math.log10(n) + math.log10(math.log2(n)) if n > 1 else 0.0),
    ("O(n^2)", lambda n: 2 * math.log10(n)),
    ("O(n^3)", lambda n: 3 * math.log10(n)),
    ("O(2^n)", lambda n: n * math.log10(2)),
    ("O(n!)", lambda n: math.lgamma(n + 1) / math.log(10)),
]


def largest_fitting(log10_ops):
    """Largest n in [1, N_CEILING] with log10_ops(n) <= BUDGET_LOG10.

    Doubling finds a bracket, binary search closes it. Both are needed: the
    classes span fifteen orders of magnitude in n as well, so a fixed step
    would either crawl at one end or be useless at the other.
    """
    lo, hi = 1, 2
    while log10_ops(hi) <= BUDGET_LOG10:
        if hi >= N_CEILING:
            return None                  # no limit at any n we care about
        lo, hi = hi, min(hi * 2, N_CEILING)
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if log10_ops(mid) <= BUDGET_LOG10:
            lo = mid
        else:
            hi = mid
    return lo


def show_ops(log10_ops):
    """Render an operation count from its log10, whatever its size."""
    if log10_ops <= 12:
        return f"{10 ** log10_ops:,.0f}"
    return f"10^{log10_ops:,.0f}"


print(f"An operation budget of {10 ** BUDGET_LOG10:,.0f} is the one constant.")
print("For each complexity class, the largest n that still fits it:\n")
print(f"   {'class':<11}{'largest n that fits':>21}{'operations there':>18}")
print("   " + "-" * 48)
for name, log10_ops in CLASSES:
    n = largest_fitting(log10_ops)
    if n is None:
        print(f"   {name:<11}{'beyond ' + f'{N_CEILING:,}':>21}{'-':>18}")
    else:
        print(f"   {name:<11}{n:>21,}{show_ops(log10_ops(n)):>18}")

print()
print("Read the right-hand column downwards: every class lands in the same")
print("band, because the budget is what is fixed and n is what moves. The")
print("size limit in a problem statement is that band, restated in the one")
print("variable the statement is allowed to mention.")

# ---------------------------------------------------------------- the decision
N = 100_000
print(f"\nNow fix n instead. At n = {N:,}, which classes still fit?\n")
print(f"   {'class':<11}{'operations':>14}   {'fits the budget?':<17}")
print("   " + "-" * 44)
for name, log10_ops in CLASSES:
    ops = log10_ops(N)
    print(f"   {name:<11}{show_ops(ops):>14}   "
          f"{'yes' if ops <= BUDGET_LOG10 else 'NO':<17}")

print()
print("Two of those eight rows are the whole chapter. At n = 100,000 an")
print("O(n^2) solution does 10,000,000,000 operations where an O(n log n)")
print("solution does about 1,660,000 -- six thousand times fewer, and the")
print("difference between a timeout and a pass.")

# ------------------------------------------------------------------ the rate
slow_log10 = 2 * math.log10(N)          # O(n^2) at n = 100,000
seconds = 10 ** (slow_log10 - 7)        # at a stated 10^7 operations/second
print(f"\nConverting one row to time needs a rate, and the rate is an")
print(f"assumption rather than a measurement. Take 10^7 operations per")
print(f"second -- roughly a straightforward Python loop:")
print(f"\n   O(n^2) at n = {N:,}   {10 ** slow_log10:,.0f} operations")
print(f"                          about {seconds:,.0f} seconds "
      f"({seconds / 60:,.0f} minutes)")
fast = 10 ** (math.log10(N) + math.log10(math.log2(N)))
print(f"   O(n log n) at the same n   {fast:,.0f} operations")
print(f"                              about {fast / 1e7:.2f} seconds")
print()
print("A tight loop in C is a hundred times faster and a slow one in pure")
print("Python is a hundred times slower, so the seconds are soft. The")
print("decision is not: a factor of six thousand does not get eaten by a")
print("constant factor.")
```

```text
An operation budget of 100,000,000 is the one constant.
For each complexity class, the largest n that still fits it:

   class        largest n that fits  operations there
   ------------------------------------------------
   O(1)       beyond 1,000,000,000,000                 -
   O(log n)   beyond 1,000,000,000,000                 -
   O(n)                 100,000,000       100,000,000
   O(n log n)             4,523,071        99,999,994
   O(n^2)                    10,000       100,000,000
   O(n^3)                       464        99,897,344
   O(2^n)                        26        67,108,864
   O(n!)                         11        39,916,800

Read the right-hand column downwards: every class lands in the same
band, because the budget is what is fixed and n is what moves. The
size limit in a problem statement is that band, restated in the one
variable the statement is allowed to mention.

Now fix n instead. At n = 100,000, which classes still fit?

   class          operations   fits the budget? 
   --------------------------------------------
   O(1)                    1   yes              
   O(log n)               17   yes              
   O(n)              100,000   yes              
   O(n log n)      1,660,964   yes              
   O(n^2)     10,000,000,000   NO               
   O(n^3)              10^15   NO               
   O(2^n)          10^30,103   NO               
   O(n!)          10^456,573   NO               

Two of those eight rows are the whole chapter. At n = 100,000 an
O(n^2) solution does 10,000,000,000 operations where an O(n log n)
solution does about 1,660,000 -- six thousand times fewer, and the
difference between a timeout and a pass.

Converting one row to time needs a rate, and the rate is an
assumption rather than a measurement. Take 10^7 operations per
second -- roughly a straightforward Python loop:

   O(n^2) at n = 100,000   10,000,000,000 operations
                          about 1,000 seconds (17 minutes)
   O(n log n) at the same n   1,660,964 operations
                              about 0.17 seconds

A tight loop in C is a hundred times faster and a slow one in pure
Python is a hundred times slower, so the seconds are soft. The
decision is not: a factor of six thousand does not get eaten by a
constant factor.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- one problem, three algorithms, and the count that picks.

The problem: given a list of integers and a target, is there a pair of
elements that sums to the target? If so, which pair?

The three solutions are the three shapes every "find a pair" problem has:
look at everything, sort first, or remember what you have seen. Each one is
instrumented with a counter, so the comparison is a comparison of counts and
not of stopwatches.

The sort is a merge sort written here rather than `sorted()`, for one reason:
`list.sort` does not tell you how many comparisons it made, and a modelled
n log n is a claim where a counted one is a fact.
"""
import random

# --------------------------------------------------------------- solutions


def by_brute_force(values, target):
    """Every pair. Returns (pair, probes) where probes counts pair tests."""
    probes = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            probes += 1
            if values[i] + values[j] == target:
                a, b = values[i], values[j]
                return (min(a, b), max(a, b)), probes
    return None, probes


def merge_sort_counted(values):
    """Merge sort that reports how many comparisons it made.

    The count is exact and deterministic for a given input, which is what
    makes it usable as evidence. It is not a model of a comparison count.
    """
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(values), comparisons


def by_sorting(values, target):
    """Sort, then walk inwards from both ends."""
    ordered, comparisons = merge_sort_counted(values)
    probes = 0
    lo, hi = 0, len(ordered) - 1
    while lo < hi:
        probes += 1
        total = ordered[lo] + ordered[hi]
        if total == target:
            return (ordered[lo], ordered[hi]), comparisons + probes
        if total < target:
            lo += 1
        else:
            hi -= 1
    return None, comparisons + probes


def by_remembering(values, target):
    """One pass, with a set of everything already seen."""
    seen = set()
    probes = 0
    for v in values:
        probes += 1
        want = target - v
        if want in seen:
            return (min(v, want), max(v, want)), probes
        seen.add(v)
    return None, probes


# ------------------------------------------------------------------ checking

def valid(values, target, pair):
    """A returned pair must sum to the target and come from the input."""
    if pair is None:
        return True
    a, b = pair
    return a + b == target and a in values and b in values


rng = random.Random(49)
disagreements = 0
differing_witnesses = 0
for _ in range(400):
    n = rng.randint(2, 40)
    values = [rng.randint(-50, 50) for _ in range(n)]
    target = rng.randint(-60, 60)
    got = [by_brute_force(values, target)[0],
           by_sorting(values, target)[0],
           by_remembering(values, target)[0]]
    if len({p is None for p in got}) != 1:
        disagreements += 1
    for pair in got:
        assert valid(values, target, pair), (values, target, pair)
    if len({p for p in got if p is not None}) > 1:
        differing_witnesses += 1

print("Correctness first, because a fast wrong answer is not an answer.")
print(f"\n   400 random instances, three implementations each")
print(f"   decisions that disagree      : {disagreements}")
print(f"   instances where all three found a pair but not the same one : "
      f"{differing_witnesses}")
print()
print("The decision is unique; the witness is not. When several pairs sum to")
print("the target, each method returns whichever it reaches first, and that")
print("depends on the method. Compare the answers you promised to compare.")

# ------------------------------------------------- the formula, then the scale

print("\nThe brute force tests every pair, so when no pair works its probe")
print("count is exactly n(n-1)/2. Check that before using it as a formula:\n")
print(f"   {'n':>7}{'probes counted':>16}{'n(n-1)/2':>14}{'agree':>8}")
print("   " + "-" * 45)
for n in (100, 200, 400, 800, 1_600):
    values = [rng.randint(0, 10 * n) for _ in range(n)]
    _, probes = by_brute_force(values, -1)
    formula = n * (n - 1) // 2
    print(f"   {n:>7,}{probes:>16,}{formula:>14,}{str(probes == formula):>8}")

print()
print("`probes` below counts the candidate tests and the membership questions --")
print("the work that scales with the input, not the loop overhead. The brute")
print("force row is the formula just verified; at n = 10^6 the loop itself would")
print("be five hundred billion tests, which is the point being made.\n")
print(f"   {'n':>10}{'brute force':>18}{'sort + walk':>14}{'remember':>12}"
      f"{'brute / best':>14}")
print("   " + "-" * 68)
for n in (10_000, 100_000, 1_000_000):
    values = [rng.randint(0, 10 * n) for _ in range(n)]
    target = -1                      # unreachable: worst case for all three
    _, p_sort = by_sorting(values, target)
    _, p_rem = by_remembering(values, target)
    p_brute = n * (n - 1) // 2
    best = min(p_sort, p_rem)
    print(f"   {n:>10,}{p_brute:>18,}{p_sort:>14,}{p_rem:>12,}"
          f"{p_brute / best:>13,.0f}x")

print()
print("A target that cannot be reached is the honest case to compare: every")
print("method has to finish, so nothing is flattered by where it stopped.")
print("Sorting costs n log n comparisons and then n pointer moves; the set")
print("costs one membership test per element and never sorts at all. Since")
print("the set does exactly n probes, the last column is exactly (n-1)/2 --")
print("check it against the rows: 4,999.5 at n = 10,000 and 499,999.5 at")
print("n = 10^6, rounded in the display. The margin is not a constant factor")
print("that a faster machine could absorb; it grows with n.")
```

```text
Correctness first, because a fast wrong answer is not an answer.

   400 random instances, three implementations each
   decisions that disagree      : 0
   instances where all three found a pair but not the same one : 122

The decision is unique; the witness is not. When several pairs sum to
the target, each method returns whichever it reaches first, and that
depends on the method. Compare the answers you promised to compare.

The brute force tests every pair, so when no pair works its probe
count is exactly n(n-1)/2. Check that before using it as a formula:

         n  probes counted      n(n-1)/2   agree
   ---------------------------------------------
       100           4,950         4,950    True
       200          19,900        19,900    True
       400          79,800        79,800    True
       800         319,600       319,600    True
     1,600       1,279,200     1,279,200    True

`probes` below counts the candidate tests and the membership questions --
the work that scales with the input, not the loop overhead. The brute
force row is the formula just verified; at n = 10^6 the loop itself would
be five hundred billion tests, which is the point being made.

            n       brute force   sort + walk    remember  brute / best
   --------------------------------------------------------------------
       10,000        49,995,000       130,544      10,000        5,000x
      100,000     4,999,950,000     1,636,601     100,000       50,000x
    1,000,000   499,999,500,000    19,674,891   1,000,000      500,000x

A target that cannot be reached is the honest case to compare: every
method has to finish, so nothing is flattered by where it stopped.
Sorting costs n log n comparisons and then n pointer moves; the set
costs one membership test per element and never sorts at all. Since
the set does exactly n probes, the last column is exactly (n-1)/2 --
check it against the rows: 4,999.5 at n = 10,000 and 499,999.5 at
n = 10^6, rounded in the display. The margin is not a constant factor
that a faster machine could absorb; it grows with n.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- proving a complexity instead of claiming it.

"Every element is compared with every other" is a sentence. n(n-1)/2 is a
number. The step between them is counting, and it is the step that turns an
intuition into evidence.

This script counts operations for four shapes, fits the exponent from the
counts, and then does the same fit on a pure model -- because the interesting
result is what the fit does when you already know the answer.

Nothing is timed. Every number is a count.
"""
import math
import random

# ------------------------------------------------------------------- shapes


def merge_sort_counted(values):
    """Merge sort that reports its exact comparison count."""
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(values), comparisons


def one_pass(values):
    """One look at each element."""
    ops = 0
    total = 0
    for v in values:
        ops += 1
        total += v
    return ops


def all_pairs(values):
    """Every unordered pair, once."""
    ops = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            ops += 1
    return ops


def halving_loop(values):
    """A nested loop that is NOT quadratic. Read it before you trust it."""
    ops = 0
    i = len(values)
    while i > 0:
        for _ in range(i):
            ops += 1
        i //= 2
    return ops


def sort_then_scan(values):
    """Sort, then one pass."""
    _, comparisons = merge_sort_counted(values)
    return comparisons + one_pass(values)


SHAPES = [
    ("one pass", one_pass),
    ("all pairs", all_pairs),
    ("halving loop", halving_loop),
    ("sort + scan", sort_then_scan),
]

SIZES = [256, 512, 1_024, 2_048]

rng = random.Random(49)
counts = {}
for name, fn in SHAPES:
    counts[name] = [fn([rng.randint(0, 1_000) for _ in range(n)]) for n in SIZES]


def exponent(xs, ys):
    """Fitted exponent between the last two points: log(y2/y1) / log(x2/x1)."""
    return math.log(ys[-1] / ys[-2]) / math.log(xs[-1] / xs[-2])


print("Four shapes, operations counted, and the exponent fitted from the")
print("last two sizes. The fitted value is a measurement, not a label.\n")
head = f"   {'shape':<14}" + "".join(f"{n:>12,}" for n in SIZES) + f"{'fitted':>10}"
print(head)
print("   " + "-" * (len(head) - 3))
for name, _ in SHAPES:
    row = f"   {name:<14}" + "".join(f"{c:>12,}" for c in counts[name])
    print(row + f"{exponent(SIZES, counts[name]):>10.2f}")

print()
print("`halving loop` is the one to look at twice. It has an inner `for` inside")
print("an outer `while`, so it reads as a nested loop and a reader who pattern-")
print("matches on shape will call it quadratic. Count it instead: the outer")
print("loop's bound halves, so the total is n + n/2 + n/4 + ... which is about")
print("2n. The fit says 1.00, and the fit is right.\n")
print(f"   {'n':>8}{'halving counted':>18}{'2n - 1':>10}{'agree':>8}")
print("   " + "-" * 44)
for n, c in zip(SIZES, counts["halving loop"]):
    print(f"   {n:>8,}{c:>18,}{2 * n - 1:>10,}{str(c == 2 * n - 1):>8}")
print()
print("For powers of two the sum is exactly 2n - 1, and the column confirms")
print("it. That is a proof of the linear bound for these inputs, and the")
print("reasoning -- a geometric series with ratio 1/2 -- covers the rest.")

# --------------------------------------------------- the fit is not a constant

print("\nNow the part that matters when you use a fit as evidence. Apply the")
print("same procedure to four complexity classes you already know, over a")
print("range of sizes, and watch the fitted exponent for n log n:\n")
WIDTHS = {"O(n)": 9, "O(n log n)": 13, "O(n^2)": 9, "O(n^3)": 9}
print(f"   {'range':<22}" + "".join(f"{k:>{w}}" for k, w in WIDTHS.items()))
print("   " + "-" * (25 + sum(WIDTHS.values())))
drift = []
prev = None
for n in (1_024, 4_096, 16_384, 65_536, 262_144, 1_048_576):
    model = {"O(n)": float(n),
             "O(n log n)": n * math.log2(n),
             "O(n^2)": float(n) ** 2,
             "O(n^3)": float(n) ** 3}
    if prev is not None:
        pn, pm = prev
        row = f"   {f'{pn:,} -> {n:,}':<22}"
        for key, w in WIDTHS.items():
            e = math.log(model[key] / pm[key]) / math.log(n / pn)
            row += f"{e:>{w}.2f}"
            if key == "O(n log n)":
                drift.append((f"{pn:,} -> {n:,}", e))
        print(row)
    prev = (n, model)

print()
print("The O(n), O(n^2) and O(n^3) columns report 1, 2 and 3 at every range --")
print("a polynomial's exponent is a constant, so doubling n multiplies the")
print("count by a fixed factor and the fit recovers it exactly.")
print()
first_range, first_e = drift[0]
last_range, last_e = drift[-1]
print(f"The n log n column does not settle. It reads {first_e:.2f} over the")
print(f"first range and {last_e:.2f} over the last, falling towards 1 at every")
print("step: slowly, because the log grows slowly. So a fitted exponent near")
print("1.1 is not a proof that an algorithm is n log n, and it is not a")
print("refutation of a linear one either. A single fitted number is evidence")
print("for a class; the way it drifts as the range grows is what separates")
print("n log n from n.")
```

```text
Four shapes, operations counted, and the exponent fitted from the
last two sizes. The fitted value is a measurement, not a label.

   shape                  256         512       1,024       2,048    fitted
   ------------------------------------------------------------------------
   one pass               256         512       1,024       2,048      1.00
   all pairs           32,640     130,816     523,776   2,096,128      2.00
   halving loop           511       1,023       2,047       4,095      1.00
   sort + scan          1,980       4,469       9,966      22,007      1.14

`halving loop` is the one to look at twice. It has an inner `for` inside
an outer `while`, so it reads as a nested loop and a reader who pattern-
matches on shape will call it quadratic. Count it instead: the outer
loop's bound halves, so the total is n + n/2 + n/4 + ... which is about
2n. The fit says 1.00, and the fit is right.

          n   halving counted    2n - 1   agree
   --------------------------------------------
        256               511       511    True
        512             1,023     1,023    True
      1,024             2,047     2,047    True
      2,048             4,095     4,095    True

For powers of two the sum is exactly 2n - 1, and the column confirms
it. That is a proof of the linear bound for these inputs, and the
reasoning -- a geometric series with ratio 1/2 -- covers the rest.

Now the part that matters when you use a fit as evidence. Apply the
same procedure to four complexity classes you already know, over a
range of sizes, and watch the fitted exponent for n log n:

   range                      O(n)   O(n log n)   O(n^2)   O(n^3)
   -----------------------------------------------------------------
   1,024 -> 4,096             1.00         1.13     2.00     3.00
   4,096 -> 16,384            1.00         1.11     2.00     3.00
   16,384 -> 65,536           1.00         1.10     2.00     3.00
   65,536 -> 262,144          1.00         1.08     2.00     3.00
   262,144 -> 1,048,576       1.00         1.08     2.00     3.00

The O(n), O(n^2) and O(n^3) columns report 1, 2 and 3 at every range --
a polynomial's exponent is a constant, so doubling n multiplies the
count by a fixed factor and the fit recovers it exactly.

The n log n column does not settle. It reads 1.13 over the
first range and 1.08 over the last, falling towards 1 at every
step: slowly, because the log grows slowly. So a fitted exponent near
1.1 is not a proof that an algorithm is n log n, and it is not a
refutation of a linear one either. A single fitted number is evidence
for a class; the way it drifts as the range grows is what separates
n log n from n.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- when the answer is "sort it first".

The problem: given a list of half-open intervals [start, end), what is the
largest number of them that are open at the same moment?

Two things here are not what they look like.

First, the obvious method -- "ask each interval how many others overlap it,
take the largest answer" -- is not slow. It is wrong, and the smallest
counterexample has three intervals.

Second, the half-open bracket is load-bearing. [0, 5) and [5, 10) do not
overlap, so at time 5 the closing event must be processed before the opening
one. That tie-break is part of the algorithm.
"""
import random

# ------------------------------------------------------------------ solutions


def overlaps(a, b):
    """Half-open: [0, 5) and [5, 10) do not overlap."""
    return a[0] < b[1] and b[0] < a[1]


def max_overlap_pairwise(intervals):
    """The obvious method. Returns (depth, tests). Wrong -- see below."""
    tests = 0
    best = 0
    for i, a in enumerate(intervals):
        depth = 1
        for j, b in enumerate(intervals):
            if i == j:
                continue
            tests += 1
            if overlaps(a, b):
                depth += 1
        best = max(best, depth)
    return best, tests


def max_overlap_by_points(intervals):
    """Correct and slow: the deepest point is always some interval's start."""
    tests = 0
    best = 0
    for start, _ in intervals:
        depth = 0
        for s, e in intervals:
            tests += 1
            if s <= start < e:
                depth += 1
        best = max(best, depth)
    return best, tests


def merge_sort_counted(events):
    """Merge sort on (time, delta) with the comparison count reported."""
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(events), comparisons


def max_overlap_sweep(intervals):
    """Sort the events, then one pass. Returns (depth, work)."""
    events = []
    for start, end in intervals:
        events.append((start, +1))
        events.append((end, -1))
    ordered, comparisons = merge_sort_counted(events)
    depth = 0
    best = 0
    steps = 0
    for _, delta in ordered:
        steps += 1
        depth += delta
        best = max(best, depth)
    return best, comparisons + steps


def max_overlap_sweep_starts_first(intervals):
    """The same sweep with the tie-break reversed. This one is wrong."""
    events = []
    for start, end in intervals:
        events.append((start, +1))
        events.append((end, -1))
    ordered, _ = merge_sort_counted(events)
    ordered.sort(key=lambda e: (e[0], -e[1]))       # starts before ends
    depth = 0
    best = 0
    for _, delta in ordered:
        depth += delta
        best = max(best, depth)
    return best


# ------------------------------------------------------------------- the trap

print("Three intervals. One long one covering the other two, and the other")
print("two sitting side by side without touching:\n")
covering = [(0, 10), (0, 5), (5, 10)]
print(f"   intervals {covering}\n")
print(f"   pairwise, 'how many overlap me?' : {max_overlap_pairwise(covering)[0]}")
print(f"   every start point, counted       : {max_overlap_by_points(covering)[0]}")
print(f"   sort the events, sweep           : {max_overlap_sweep(covering)[0]}")
print()
print("The pairwise method says 3. The answer is 2: [0, 5) and [5, 10) are")
print("never open at the same time, so the long interval can only ever be")
print("sharing its moment with one of them. The method counts intervals that")
print("overlap a *given* interval, and that is a different question from the")
print("largest number open at a *point*. Three intervals overlap the long one")
print("at various times; no two of the three are ever open together.")
print()
rng = random.Random(49)
pairwise_wrong = 0
over = 0
under = 0
for _ in range(300):
    n = rng.randint(1, 30)
    spans = []
    for _ in range(n):
        a = rng.randint(0, 40)
        spans.append((a, a + rng.randint(1, 8)))
    got = max_overlap_pairwise(spans)[0]
    truth = max_overlap_sweep(spans)[0]
    if got != truth:
        pairwise_wrong += 1
        over += got > truth
        under += got < truth
print(f"   300 random instances, the pairwise method is wrong on "
      f"{pairwise_wrong} of them")
print(f"   of those, overcounted {over}, undercounted {under}")
print("   It can only overcount, and the reason is structural: the method")
print("   counts intervals that overlap a given interval, and any such set is")
print("   a candidate answer, so it can never miss one that is larger.")

# ------------------------------------------------------------ the tie-break

print("\nNow the second trap, in the sweep itself. Two intervals that touch:\n")
touching = [(0, 5), (5, 10)]
print(f"   intervals {touching}   -- half-open, so they do not overlap\n")
print(f"   every start point, counted                : "
      f"{max_overlap_by_points(touching)[0]}")
print(f"   sweep, ends before starts at equal times  : "
      f"{max_overlap_sweep(touching)[0]}")
print(f"   sweep, starts before ends at equal times  : "
      f"{max_overlap_sweep_starts_first(touching)}")
print()
print("The wrong tie-break reports two intervals open at time 5, when the")
print("first has just closed. It is right on most inputs and wrong on the")
print("ones with shared endpoints, which is the worst kind of bug: it")
print("survives the tests you thought to write.\n")
tie_bad = 0
rng = random.Random(7)
for _ in range(300):
    n = rng.randint(1, 30)
    spans = []
    for _ in range(n):
        a = rng.randint(0, 40)
        spans.append((a, a + rng.randint(1, 8)))
    if max_overlap_sweep_starts_first(spans) != max_overlap_by_points(spans)[0]:
        tie_bad += 1
print(f"   300 random instances, the wrong tie-break is wrong on "
      f"{tie_bad} of them")

# -------------------------------------------------------------- the agreement

print("\nThe two correct methods, over random inputs:\n")
disagreements = 0
for _ in range(300):
    n = rng.randint(1, 40)
    spans = []
    for _ in range(n):
        a = rng.randint(0, 60)
        spans.append((a, a + rng.randint(1, 10)))
    if max_overlap_sweep(spans)[0] != max_overlap_by_points(spans)[0]:
        disagreements += 1
print(f"   300 random instances, sort-and-sweep vs every start point : "
      f"{disagreements} disagreements")

# ---------------------------------------------------------------- the formula

print("\nThe slow-but-correct version tests every start against every interval,")
print("so its cost is n^2 before the data arrives. Check that:\n")
print(f"   {'n':>7}{'tests counted':>16}{'n^2':>12}{'agree':>8}")
print("   " + "-" * 43)
for n in (100, 200, 400):
    spans = [(i, i + 3) for i in range(n)]
    _, tests = max_overlap_by_points(spans)
    print(f"   {n:>7,}{tests:>16,}{n * n:>12,}{str(tests == n * n):>8}")

print("\nAnd the two correct versions side by side at scale. The n^2 column is")
print("the formula just verified; the sweep column is counted, including its")
print("own sort.\n")
print(f"   {'n':>10}{'every start point':>20}{'sort + sweep':>16}{'ratio':>10}")
print("   " + "-" * 56)
for n in (1_000, 10_000, 100_000):
    spans = []
    for _ in range(n):
        a = rng.randint(0, 10 * n)
        spans.append((a, a + rng.randint(1, 100)))
    slow = n * n
    _, sweep = max_overlap_sweep(spans)
    print(f"   {n:>10,}{slow:>20,}{sweep:>16,}{slow / sweep:>9,.0f}x")

print()
print("The ratio grows with n and never stops growing, because one side is n^2")
print("and the other is 2n log 2n. Sorting is the reason: the sweep never asks")
print("whether two intervals overlap. It only asks whether an interval has")
print("started or stopped. The pairwise question did not get faster -- it")
print("stopped being asked.")
```

```text
Three intervals. One long one covering the other two, and the other
two sitting side by side without touching:

   intervals [(0, 10), (0, 5), (5, 10)]

   pairwise, 'how many overlap me?' : 3
   every start point, counted       : 2
   sort the events, sweep           : 2

The pairwise method says 3. The answer is 2: [0, 5) and [5, 10) are
never open at the same time, so the long interval can only ever be
sharing its moment with one of them. The method counts intervals that
overlap a *given* interval, and that is a different question from the
largest number open at a *point*. Three intervals overlap the long one
at various times; no two of the three are ever open together.

   300 random instances, the pairwise method is wrong on 234 of them
   of those, overcounted 234, undercounted 0
   It can only overcount, and the reason is structural: the method
   counts intervals that overlap a given interval, and any such set is
   a candidate answer, so it can never miss one that is larger.

Now the second trap, in the sweep itself. Two intervals that touch:

   intervals [(0, 5), (5, 10)]   -- half-open, so they do not overlap

   every start point, counted                : 1
   sweep, ends before starts at equal times  : 1
   sweep, starts before ends at equal times  : 2

The wrong tie-break reports two intervals open at time 5, when the
first has just closed. It is right on most inputs and wrong on the
ones with shared endpoints, which is the worst kind of bug: it
survives the tests you thought to write.

   300 random instances, the wrong tie-break is wrong on 138 of them

The two correct methods, over random inputs:

   300 random instances, sort-and-sweep vs every start point : 0 disagreements

The slow-but-correct version tests every start against every interval,
so its cost is n^2 before the data arrives. Check that:

         n   tests counted         n^2   agree
   -------------------------------------------
       100          10,000      10,000    True
       200          40,000      40,000    True
       400         160,000     160,000    True

And the two correct versions side by side at scale. The n^2 column is
the formula just verified; the sweep column is counted, including its
own sort.

            n   every start point    sort + sweep     ratio
   --------------------------------------------------------
        1,000           1,000,000          20,870       48x
       10,000         100,000,000         274,662      364x
      100,000      10,000,000,000       3,407,793    2,934x

The ratio grows with n and never stops growing, because one side is n^2
and the other is 2n log 2n. Sorting is the reason: the sweep never asks
whether two intervals overlap. It only asks whether an interval has
started or stopped. The pairwise question did not get faster -- it
stopped being asked.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- when sorting is the wrong move, and when a set is not enough.

The problem: given an unsorted list of integers, how long is the longest run
of consecutive values? [100, 4, 200, 1, 3, 2] contains 1, 2, 3, 4.

Sorting solves this in n log n comparisons, and for a long time that is what
you would reach for. It is not the answer here, and the reason is the
constraint rather than taste: at n = 10^6, n log n is twenty million
operations and n is one million, and both fit -- but the point is that you
can *know* that before writing either.

The second half of this script is the part that is easy to miss. A hash set
makes each membership test one comparison. It does not make the algorithm
linear. Without a guard that skips values in the middle of a run, the set
version is quadratic on the input where it matters most.
"""
import random

# ------------------------------------------------------------------ solutions


def merge_sort_counted(values):
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(values), comparisons


def list_membership(values, x):
    """Membership by scanning. Returns the number of comparisons it cost."""
    cost = 0
    for v in values:
        cost += 1
        if v == x:
            return True, cost
    return False, cost


def longest_by_scanning(values):
    """No set. Every question is a walk over the list."""
    cost = 0
    best = 0
    for x in values:
        found, c = list_membership(values, x - 1)
        cost += c
        if found:
            continue                      # x is inside a run, not a start
        length = 1
        while True:
            found, c = list_membership(values, x + length)
            cost += c
            if not found:
                break
            length += 1
        best = max(best, length)
    return best, cost


def longest_by_set_no_guard(values):
    """A set, but every element starts counting. Quadratic on long runs."""
    present = set(values)
    cost = 0
    best = 0
    for x in values:
        length = 1
        while x + length in present:
            cost += 1
            length += 1
        cost += 1                        # the test that ended the loop
        best = max(best, length)
    return best, cost


def longest_by_set_with_guard(values):
    """A set and a guard: only start counting where a run begins."""
    present = set(values)
    cost = 0
    best = 0
    for x in values:
        cost += 1
        if x - 1 in present:
            continue                      # one comparison, then move on
        length = 1
        while x + length in present:
            cost += 1
            length += 1
        cost += 1
        best = max(best, length)
    return best, cost


def longest_by_sorting(values):
    """Sort, then one pass over neighbours."""
    ordered, comparisons = merge_sort_counted(values)
    cost = comparisons
    best = 0
    run = 0
    previous = None
    for v in ordered:
        cost += 1
        if previous is not None and v == previous:
            continue                      # duplicates do not extend a run
        run = run + 1 if previous is not None and v == previous + 1 else 1
        best = max(best, run)
        previous = v
    return best, cost


# ---------------------------------------------------------------- correctness

METHODS = [
    ("scan the list", longest_by_scanning),
    ("sort, then walk", longest_by_sorting),
    ("set, no guard", longest_by_set_no_guard),
    ("set + guard", longest_by_set_with_guard),
]

print("Four methods. All four are correct, so the interesting column is cost.\n")
rng = random.Random(49)
disagreements = 0
for _ in range(400):
    n = rng.randint(1, 40)
    values = rng.sample(range(3 * n), n)
    answers = {fn(values)[0] for _, fn in METHODS}
    if len(answers) != 1:
        disagreements += 1
print(f"   400 random instances, all four methods, distinct answers: "
      f"{disagreements}")
print()
print("The input that matters for the cost comparison is *distinct* values")
print("drawn from a range a few times wider than the list. That gives short")
print("runs and no duplicates, so no method is helped by a lucky shape.\n")

# ------------------------------------------------------------------ the budget

SIZES = [200, 400, 800, 1_600]
table = {}
for name, fn in METHODS:
    table[name] = [fn(rng.sample(range(4 * n), n))[1] for n in SIZES]

print(f"   {'method':<17}" + "".join(f"{n:>14,}" for n in SIZES))
print("   " + "-" * (17 + 14 * len(SIZES)))
for name, _ in METHODS:
    print(f"   {name:<17}" + "".join(f"{c:>14,}" for c in table[name]))

print()
print("Read the growth, not the totals. From 200 to 1,600 is eight times the")
print("input:")
for name, _ in METHODS:
    first, last = table[name][0], table[name][-1]
    print(f"   {name:<17} cost x{last / first:>7.1f}")

print()
print("A linear method multiplies by 8. A quadratic one multiplies by 64.")
print("Note the two set rows: on data with no long runs, the guard costs an")
print("extra n comparisons and buys nothing, which is the next section.")

# -------------------------------------------------------------------- the guard

print("\nNow give the methods the input that punishes the wrong one: a single")
print("run of n consecutive values, shuffled.\n")
GUARD_N = 2_000
shuffled = list(range(GUARD_N))
rng.shuffle(shuffled)

results = {}
for name, fn in METHODS:
    if name == "scan the list":
        continue                          # n^2 list scans: minutes, not seconds
    results[name] = fn(shuffled)

print(f"   {'method':<17}{'cost':>16}{'answer':>10}")
print("   " + "-" * 43)
for name in ("sort, then walk", "set, no guard", "set + guard"):
    answer, cost = results[name]
    print(f"   {name:<17}{cost:>16,}{answer:>10,}")

print()
noguard = results["set, no guard"][1]
guard = results["set + guard"][1]
print(f"   n = {GUARD_N:,}, and the two set versions differ by "
      f"{noguard / guard:,.0f}x")
print()
print("Both hold the same set and both ask the same question -- 'is x + 1")
print("present?' -- at one comparison each. The difference is which elements")
print("they ask about. Without the guard, every one of the n elements walks")
print("the whole run in front of it, so the total is about n^2/2 membership")
print("tests and the set has bought nothing. The guard skips any element")
print("whose predecessor is present, so only the first element of each run")
print("walks it: n tests for the guards plus n for the walks, which is 2n.\n")
print(f"   n(n-1)/2 + n, no-guard total : "
      f"{GUARD_N * (GUARD_N - 1) // 2 + GUARD_N:,}")
print(f"   2n,           guarded total  : {2 * GUARD_N:,}")
print(f"   measured, set without guard  : {noguard:,}")
print(f"   measured, set with guard     : {guard:,}")
print()
print("So the guard is not free and it is not optional. It adds one")
print("comparison per element -- visible in the table above, where the")
print("unguarded set looks cheaper on short-run data -- and in exchange it")
print("removes a quadratic worst case. That is the trade to make deliberately:")
print("the cost is a constant factor and the thing bought is a bound.")
```

```text
Four methods. All four are correct, so the interesting column is cost.

   400 random instances, all four methods, distinct answers: 0

The input that matters for the cost comparison is *distinct* values
drawn from a range a few times wider than the list. That gives short
runs and no duplicates, so no method is helped by a lucky shape.

   method                      200           400           800         1,600
   -------------------------------------------------------------------------
   scan the list            71,130       276,302     1,120,709     4,467,037
   sort, then walk           1,466         3,361         7,524        16,670
   set, no guard               262           533         1,084         2,107
   set + guard                 400           800         1,600         3,200

Read the growth, not the totals. From 200 to 1,600 is eight times the
input:
   scan the list     cost x   62.8
   sort, then walk   cost x   11.4
   set, no guard     cost x    8.0
   set + guard       cost x    8.0

A linear method multiplies by 8. A quadratic one multiplies by 64.
Note the two set rows: on data with no long runs, the guard costs an
extra n comparisons and buys nothing, which is the next section.

Now give the methods the input that punishes the wrong one: a single
run of n consecutive values, shuffled.

   method                       cost    answer
   -------------------------------------------
   sort, then walk            21,439     2,000
   set, no guard           2,001,000     2,000
   set + guard                 4,000     2,000

   n = 2,000, and the two set versions differ by 500x

Both hold the same set and both ask the same question -- 'is x + 1
present?' -- at one comparison each. The difference is which elements
they ask about. Without the guard, every one of the n elements walks
the whole run in front of it, so the total is about n^2/2 membership
tests and the set has bought nothing. The guard skips any element
whose predecessor is present, so only the first element of each run
walks it: n tests for the guards plus n for the walks, which is 2n.

   n(n-1)/2 + n, no-guard total : 2,001,000
   2n,           guarded total  : 4,000
   measured, set without guard  : 2,001,000
   measured, set with guard     : 4,000

So the guard is not free and it is not optional. It adds one
comparison per element -- visible in the table above, where the
unguarded set looks cheaper on short-run data -- and in exchange it
removes a quadratic worst case. That is the trade to make deliberately:
the cost is a constant factor and the thing bought is a bound.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- when the structure falls out of the problem.

The problem: count the contiguous subarrays of a list whose elements sum to
exactly k.

The naive answer adds up every subarray, which is n(n+1)/2 additions. The
answer that a complexity budget of n demands is a single pass with a
dictionary -- and the interesting part is *which* dictionary. A set of
prefix sums is the obvious choice and it is wrong as soon as the list
contains a negative number, because then the same prefix sum recurs and the
question stops being "has this sum been seen?" and becomes "how many times
has it been seen?".

So the structure is not a set. It is a counting dictionary, and the reason
is a property of the data rather than a preference.
"""
import random

# ------------------------------------------------------------------ solutions


def count_naive(values, k):
    """Every subarray, added up from scratch. Returns (count, additions)."""
    additions = 0
    total = 0
    for i in range(len(values)):
        running = 0
        for j in range(i, len(values)):
            running += values[j]
            additions += 1
            if running == k:
                total += 1
    return total, additions


def count_with_prefix_counts(values, k):
    """One pass. `seen[s]` is how many earlier prefixes summed to s."""
    seen = {0: 1}
    running = 0
    total = 0
    lookups = 0
    for v in values:
        running += v
        lookups += 1
        total += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return total, lookups


def count_with_prefix_set(values, k):
    """The same pass with a set. Correct only when prefixes never repeat."""
    seen = {0}
    running = 0
    total = 0
    for v in values:
        running += v
        if running - k in seen:
            total += 1
        seen.add(running)
    return total


# ---------------------------------------------------------------- correctness

print("First, agreement -- including negative numbers, which is where the")
print("naive and the prefix method could plausibly part company.\n")
rng = random.Random(49)
disagreements = 0
for _ in range(400):
    n = rng.randint(1, 30)
    values = [rng.randint(-5, 5) for _ in range(n)]
    k = rng.randint(-8, 8)
    if count_naive(values, k)[0] != count_with_prefix_counts(values, k)[0]:
        disagreements += 1
print(f"   400 random instances with negatives, naive vs prefix counts : "
      f"{disagreements} disagreements")

# ------------------------------------------------- why a dict and not a set

print("\nNow the structure question. Two different prefixes landing on the same")
print("sum is the same statement as some subarray summing to zero -- and a set")
print("can only record that a prefix was seen, never how often.\n")
print("The empty prefix counts as one of them. A subarray starting at index 0")
print("sums to zero exactly when its running total reaches 0, which is a repeat")
print("of the empty prefix and of nothing else. It is the entry that is easiest")
print("to forget and it is the same entry the dictionary is initialised with.\n")
print(f"   {'values':<22}{'prefixes':>9}{'distinct':>9}{'repeats':>9}"
      f"{'set agrees?':>13}")
print("   " + "-" * 62)
rows = []
for label, values in (
    ("all positive", [3, 1, 4, 1, 5, 9, 2, 6]),
    ("one negative", [3, 1, 4, -8, 5, 9, 2, 6]),
    ("mixed signs", [1, -1, 1, -1, 1, -1, 1, -1]),
    ("random walk", None),
):
    if values is None:
        values = [rng.choice((-3, -2, -1, 1, 2, 3)) for _ in range(20)]
    prefixes = [0]
    running = 0
    for v in values:
        running += v
        prefixes.append(running)
    distinct = len(set(prefixes))
    repeats = len(prefixes) - distinct
    same = count_with_prefix_set(values, 0) == count_with_prefix_counts(values, 0)[0]
    rows.append((values, repeats))
    print(f"   {label:<22}{len(prefixes):>9}{distinct:>9}{repeats:>9}"
          f"{str(same):>13}")

print()
print("`repeats > 0` is the same statement as `some subarray sums to zero`,")
print("because a repeated prefix sum is exactly a stretch whose total is zero.")
print("Check that equivalence rather than asserting it:\n")
print(f"   {'values':<22}{'repeats > 0':>13}{'zero-sum subarray':>19}"
      f"{'agree':>8}")
print("   " + "-" * 62)
for label, (values, repeats) in zip(
        ("all positive", "one negative", "mixed signs", "random walk"), rows):
    has_zero = count_naive(values, 0)[0] > 0
    print(f"   {label:<22}{str(repeats > 0):>13}{str(has_zero):>19}"
          f"{str((repeats > 0) == has_zero):>8}")

mismatches = 0
for _ in range(400):
    values = [rng.randint(-4, 4) for _ in range(rng.randint(1, 25))]
    running = 0
    seen = {0}                       # the empty prefix, again
    repeated = False
    for v in values:
        running += v
        if running in seen:
            repeated = True
        seen.add(running)
    if repeated != (count_naive(values, 0)[0] > 0):
        mismatches += 1
print(f"\n   400 random instances, the two statements disagree on : {mismatches}")

# ------------------------------------------- when exactly a set is good enough

print("\nThat is the criterion for the *problem*. The criterion for the *set* is")
print("narrower, and it is worth deriving rather than guessing.\n")
print("Take one value and let c be the count the dictionary holds for it --")
print("including the seeded empty prefix. When the running total reaches that")
print("value again, the dictionary adds c-1, because that is how many earlier")
print("prefixes carried it; summed over the value's occurrences that is the")
print("number of *pairs*, c(c-1)/2. The set adds one per position that has any")
print("predecessor at all, which is c-1. Compare them:\n")
print(f"   {'c':>4}{'pairs, what the dict adds':>28}"
      f"{'positions, what the set adds':>31}{'agree':>8}")
print("   " + "-" * 71)
for c in range(1, 8):
    pairs = c * (c - 1) // 2
    positions = c - 1
    print(f"   {c:>4}{pairs:>28}{positions:>31}{str(pairs == positions):>8}")
print()
print("They agree at c = 1 and c = 2 and diverge from c = 3. So the set version")
print("is correct exactly while no count in the dictionary ever exceeds 2 -- a")
print("condition on the data that you cannot check without looking, and one")
print("that fails more often the longer the list gets. Verify the claim:\n")
criterion_bad = 0
for _ in range(400):
    values = [rng.randint(-4, 4) for _ in range(rng.randint(1, 25))]
    running = 0
    counts = {0: 1}                  # the empty prefix, counted once
    for v in values:
        running += v
        counts[running] = counts.get(running, 0) + 1
    safe = max(counts.values()) <= 2
    agrees = count_with_prefix_set(values, 0) == count_with_prefix_counts(values, 0)[0]
    if safe != agrees:
        criterion_bad += 1
print(f"   400 random instances, `no count above 2` vs `set agrees` : "
      f"{criterion_bad} disagreements")
print()
print("Zero. A counting dictionary is the structure that is correct on every")
print("input; the set is correct on the inputs where it happens to be. That")
print("is an argument from the data, not a preference.")

# ---------------------------------------------------------------- the formula

print("\nThe naive method adds up n(n+1)/2 subarrays, fixed before the data")
print("arrives. Check it:\n")
print(f"   {'n':>7}{'additions':>14}{'n(n+1)/2':>14}{'agree':>8}")
print("   " + "-" * 43)
for n in (100, 200, 400):
    values = [rng.randint(-3, 3) for _ in range(n)]
    _, additions = count_naive(values, 0)
    print(f"   {n:>7,}{additions:>14,}{n * (n + 1) // 2:>14,}"
          f"{str(additions == n * (n + 1) // 2):>8}")

print("\nAnd the two correct versions at scale. The naive column is the")
print("formula just verified; the prefix column is counted.\n")
print(f"   {'n':>10}{'add up every subarray':>24}{'one pass + dict':>18}"
      f"{'ratio':>10}")
print("   " + "-" * 62)
for n in (1_000, 10_000, 100_000):
    values = [rng.randint(-3, 3) for _ in range(n)]
    naive = n * (n + 1) // 2
    _, lookups = count_with_prefix_counts(values, 0)
    print(f"   {n:>10,}{naive:>24,}{lookups:>18,}{naive / lookups:>9,.0f}x")

print()
print("The prefix method touches each element once and asks the dictionary")
print("one question about it. Nothing about the subarrays was made cheaper:")
print("they were never enumerated. The pair of nested loops became one loop")
print("and a lookup, and the ratio is n(n+1)/2 divided by n, which is about")
print("n/2 -- so it grows without limit, exactly as the two shapes predict.")
```

```text
First, agreement -- including negative numbers, which is where the
naive and the prefix method could plausibly part company.

   400 random instances with negatives, naive vs prefix counts : 0 disagreements

Now the structure question. Two different prefixes landing on the same
sum is the same statement as some subarray summing to zero -- and a set
can only record that a prefix was seen, never how often.

The empty prefix counts as one of them. A subarray starting at index 0
sums to zero exactly when its running total reaches 0, which is a repeat
of the empty prefix and of nothing else. It is the entry that is easiest
to forget and it is the same entry the dictionary is initialised with.

   values                 prefixes distinct  repeats  set agrees?
   --------------------------------------------------------------
   all positive                  9        9        0         True
   one negative                  9        8        1         True
   mixed signs                   9        2        7        False
   random walk                  21       11       10        False

`repeats > 0` is the same statement as `some subarray sums to zero`,
because a repeated prefix sum is exactly a stretch whose total is zero.
Check that equivalence rather than asserting it:

   values                  repeats > 0  zero-sum subarray   agree
   --------------------------------------------------------------
   all positive                  False              False    True
   one negative                   True               True    True
   mixed signs                    True               True    True
   random walk                    True               True    True

   400 random instances, the two statements disagree on : 0

That is the criterion for the *problem*. The criterion for the *set* is
narrower, and it is worth deriving rather than guessing.

Take one value and let c be the count the dictionary holds for it --
including the seeded empty prefix. When the running total reaches that
value again, the dictionary adds c-1, because that is how many earlier
prefixes carried it; summed over the value's occurrences that is the
number of *pairs*, c(c-1)/2. The set adds one per position that has any
predecessor at all, which is c-1. Compare them:

      c   pairs, what the dict adds   positions, what the set adds   agree
   -----------------------------------------------------------------------
      1                           0                              0    True
      2                           1                              1    True
      3                           3                              2   False
      4                           6                              3   False
      5                          10                              4   False
      6                          15                              5   False
      7                          21                              6   False

They agree at c = 1 and c = 2 and diverge from c = 3. So the set version
is correct exactly while no count in the dictionary ever exceeds 2 -- a
condition on the data that you cannot check without looking, and one
that fails more often the longer the list gets. Verify the claim:

   400 random instances, `no count above 2` vs `set agrees` : 0 disagreements

Zero. A counting dictionary is the structure that is correct on every
input; the set is correct on the inputs where it happens to be. That
is an argument from the data, not a preference.

The naive method adds up n(n+1)/2 subarrays, fixed before the data
arrives. Check it:

         n     additions      n(n+1)/2   agree
   -------------------------------------------
       100         5,050         5,050    True
       200        20,100        20,100    True
       400        80,200        80,200    True

And the two correct versions at scale. The naive column is the
formula just verified; the prefix column is counted.

            n   add up every subarray   one pass + dict     ratio
   --------------------------------------------------------------
        1,000                 500,500             1,000      500x
       10,000              50,005,000            10,000    5,000x
      100,000           5,000,050,000           100,000   50,000x

The prefix method touches each element once and asks the dictionary
one question about it. Nothing about the subarrays was made cheaper:
they were never enumerated. The pair of nested loops became one loop
and a lookup, and the ratio is n(n+1)/2 divided by n, which is about
n/2 -- so it grows without limit, exactly as the two shapes predict.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- when the budget says exponential.

The problem: given a list of numbers and a target, is there a subset whose
elements sum to exactly the target?

Subset sum is the canonical problem whose naive solution is 2^n, and 2^n is
the class where "just make it faster" stops being available. At n = 40 the
brute force is a trillion subsets; no constant factor and no faster machine
recovers that.

Meet in the middle does not make the search faster. It changes the exponent
from n to n/2, by splitting the list, enumerating each half, and looking the
two halves up against each other. The cost is still exponential -- it is
just exponential in something half as large, which is worth a great deal.
"""
import math
from bisect import bisect_left

BUDGET_LOG10 = 8.0


def all_sums(values):
    """Every subset sum of `values`, by doubling."""
    sums = [0]
    for v in values:
        sums = sums + [s + v for s in sums]
    return sums


def all_sums_and_masks(values):
    """Every subset sum, paired with the bitmask of the subset that made it.

    Returning the mask alongside the sum matters. The search sorts the right
    half, and a sorted list has lost the correspondence between a position
    and the subset it came from -- so decoding an index found by binary
    search against the *unsorted* list returns a different subset, with a
    different sum. Carrying the mask through the sort removes the chance to
    make that mistake.
    """
    sums = [0]
    masks = [0]
    for j, v in enumerate(values):
        sums = sums + [s + v for s in sums]
        masks = masks + [m | (1 << j) for m in masks]
    return sums, masks


def solve_brute(values, target):
    """Every subset, counted. Only usable while 2^n is small."""
    n = len(values)
    examined = 0
    for mask in range(1 << n):
        total = 0
        for j in range(n):
            if mask >> j & 1:
                total += values[j]
        examined += 1
        if total == target:
            return mask, examined
    return None, examined


def solve_meet_in_the_middle(values, target):
    """Split, enumerate both halves, search one against the other.

    Returns (left_mask, right_mask, worst_case_work, left_sums_examined).
    """
    mid = len(values) // 2
    left, right = values[:mid], values[mid:]
    left_sums, left_masks = all_sums_and_masks(left)
    right_sums, right_masks = all_sums_and_masks(right)
    half = len(right_sums)
    per_search = max(1, int(math.log2(half)))
    worst_case = len(left_sums) + half + len(left_sums) * per_search
    ordered = sorted(zip(right_sums, right_masks))
    sorted_values = [pair[0] for pair in ordered]
    examined = 0
    for s, m in zip(left_sums, left_masks):
        examined += 1
        want = target - s
        j = bisect_left(sorted_values, want)
        if j < len(sorted_values) and sorted_values[j] == want:
            return m, ordered[j][1], examined, worst_case
    return None, None, examined, worst_case


# --------------------------------------------------------- the size of 2^n

print("Start with what the two approaches cost, as counts rather than times.\n")
print(f"   {'n':>4}{'brute force 2^n':>22}{'meet in the middle':>26}")
print("   " + "-" * 52)
for n in (20, 26, 30, 40, 44, 50):
    brute = 10 ** (n * math.log10(2))
    half = n // 2
    mitm = 10 ** (half * math.log10(2)) * half
    print(f"   {n:>4}{brute:>22.3e}{mitm:>26.3e}")

print()
print("At n = 40 the brute force is 1.1e12 subsets and the split is 1.0e6 per")
print("half. The split is not a speed-up of the search; it is a different")
print("search, and the exponent is the reason.\n")
print("Under a 100,000,000-operation budget, the largest n each one reaches:\n")
limit = BUDGET_LOG10
n_brute = int(limit / math.log10(2))
n_mitm = 0
for n in range(1, 200):
    half = n // 2
    if half * math.log10(2) + math.log10(max(half, 1)) <= limit:
        n_mitm = n
print(f"   brute force, 2^n                : n = {n_brute}")
print(f"   meet in the middle, 2^(n/2)*n/2 : n = {n_mitm}")
print()
print(f"Halving the exponent nearly doubles the input the budget can reach:")
print(f"{n_brute} becomes {n_mitm}. That is the whole return on the technique, and")
print("it is a large one, because the wall is exponential and every unit of n")
print("doubles the work.")

# ------------------------------------------------------------------ correctness

print("\nNow check that the split gives the same answers as the brute force.")
print("Small n, where both can run:\n")
rng_vals = [3, 7, 11, 2, 19, 5, 23, 13, 17, 29, 4, 31]
disagreements = 0
checked = 0
for n in range(1, 13):
    values = rng_vals[:n]
    for target in range(0, 40):
        mask, _ = solve_brute(values, target)
        left_mask, _, _, _ = solve_meet_in_the_middle(values, target)
        brute_says = mask is not None
        split_says = left_mask is not None
        checked += 1
        if brute_says != split_says:
            disagreements += 1
print(f"   {checked} (values, target) pairs, decisions that disagree : "
      f"{disagreements}")

# --------------------------------------------------------------- the real one

N = 40
rng_state = 12345
values = []
x = rng_state
for _ in range(N):
    x = (1103515245 * x + 12345) % (1 << 31)
    values.append(x % 1000 + 1)

CHOSEN = [0, 3, 7, 11, 18, 22, 29, 33, 37, 39]
target = sum(values[i] for i in CHOSEN)

print(f"\nNow a real instance: n = {N}, values from a fixed generator, and a")
print(f"target that is the sum of {len(CHOSEN)} of them -- so a solution exists")
print("and the answer can be checked against it.\n")
left_count = len(values) // 2
right_sums_set = set(all_sums(values[left_count:]))
left_mask, right_mask, examined, worst_case = solve_meet_in_the_middle(values, target)
chosen = [v for j, v in enumerate(values[:left_count]) if left_mask >> j & 1]
chosen += [v for j, v in enumerate(values[left_count:]) if right_mask >> j & 1]

print(f"   target                          : {target:,}")
print(f"   subset found, size              : {len(chosen)}")
print(f"   subset found, sum               : {sum(chosen):,}")
print(f"   sums to the target              : {sum(chosen) == target}")
print(f"   every element is in the input   : "
      f"{all(chosen.count(v) <= values.count(v) for v in set(chosen))}")
print()
print(f"   subsets enumerated, left half   : {2 ** left_count:,}")
print(f"   subsets enumerated, right half  : {2 ** (N - left_count):,}")
print(f"   left sums examined before match : {examined:,}")
print(f"   work, worst case (all searches) : {worst_case:,}")
print(f"   subsets the brute force needs   : {2 ** N:,}")
print(f"   worst case vs brute force       : {2 ** N / worst_case:,.0f}x")
print()
print("The match arrives on the first left sum, and that is not luck. The")
print("right half has 1,048,576 subset sums spread over a range of a few")
print("hundred thousand, so they are dense -- ask how many targets near this")
print("one the right half can reach by itself:\n")
window = 500
reachable = sum(1 for e in range(window) if target + e in right_sums_set)
print(f"   targets checked                 : {window}")
print(f"   reachable by the right half     : {reachable}")
print()
print("The search is therefore not the expensive part of meet in the middle")
print("when a solution exists. The *enumeration* is: two lists of 2^20 sums,")
print("built before a single question is asked. That is the cost the")
print("technique actually pays, and it is why the worst case is what matters.")

print("\nSo measure the worst case. Give it a target no subset can reach:\n")
impossible = sum(values) + 1
left_mask, right_mask, examined, worst_case = solve_meet_in_the_middle(
    values, impossible)
print(f"   target                          : {impossible:,}")
print(f"   solution found                  : {left_mask is not None}")
print(f"   left sums examined              : {examined:,}  (all of them)")
print(f"   work, worst case                : {worst_case:,}")
print(f"   subsets the brute force needs   : {2 ** N:,}")
print(f"   worst case vs brute force       : {2 ** N / worst_case:,.0f}x")
print()
print("That is the honest comparison: the same split, with every search run")
print("and no early exit, still lands tens of thousands of times under the")
print("brute force. The gap is not a constant factor to be optimised away.")
print("It is an exponent, and halving it is the only thing that moves it.")
```

```text
Start with what the two approaches cost, as counts rather than times.

      n       brute force 2^n        meet in the middle
   ----------------------------------------------------
     20             1.049e+06                 1.024e+04
     26             6.711e+07                 1.065e+05
     30             1.074e+09                 4.915e+05
     40             1.100e+12                 2.097e+07
     44             1.759e+13                 9.227e+07
     50             1.126e+15                 8.389e+08

At n = 40 the brute force is 1.1e12 subsets and the split is 1.0e6 per
half. The split is not a speed-up of the search; it is a different
search, and the exponent is the reason.

Under a 100,000,000-operation budget, the largest n each one reaches:

   brute force, 2^n                : n = 26
   meet in the middle, 2^(n/2)*n/2 : n = 45

Halving the exponent nearly doubles the input the budget can reach:
26 becomes 45. That is the whole return on the technique, and
it is a large one, because the wall is exponential and every unit of n
doubles the work.

Now check that the split gives the same answers as the brute force.
Small n, where both can run:

   480 (values, target) pairs, decisions that disagree : 0

Now a real instance: n = 40, values from a fixed generator, and a
target that is the sum of 10 of them -- so a solution exists
and the answer can be checked against it.

   target                          : 5,157
   subset found, size              : 10
   subset found, sum               : 5,157
   sums to the target              : True
   every element is in the input   : True

   subsets enumerated, left half   : 1,048,576
   subsets enumerated, right half  : 1,048,576
   left sums examined before match : 1
   work, worst case (all searches) : 23,068,672
   subsets the brute force needs   : 1,099,511,627,776
   worst case vs brute force       : 47,663x

The match arrives on the first left sum, and that is not luck. The
right half has 1,048,576 subset sums spread over a range of a few
hundred thousand, so they are dense -- ask how many targets near this
one the right half can reach by itself:

   targets checked                 : 500
   reachable by the right half     : 500

The search is therefore not the expensive part of meet in the middle
when a solution exists. The *enumeration* is: two lists of 2^20 sums,
built before a single question is asked. That is the cost the
technique actually pays, and it is why the worst case is what matters.

So measure the worst case. Give it a target no subset can reach:

   target                          : 21,581
   solution found                  : False
   left sums examined              : 1,048,576  (all of them)
   work, worst case                : 23,068,672
   subsets the brute force needs   : 1,099,511,627,776
   worst case vs brute force       : 47,663x

That is the honest comparison: the same split, with every search run
and no early exit, still lands tens of thousands of times under the
brute force. The gap is not a constant factor to be optimised away.
It is an exponent, and halving it is the only thing that moves it.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- the arithmetic that decides pass or fail.

A size limit is a statement about the intended complexity, and reading it
wrong is the most expensive mistake in this chapter. The same O(n^2)
solution passes one constraint and fails another, and the only way to know
which is to do the arithmetic before writing the code.

The second half is the error in the other direction. Reaching for the
clever algorithm when the constraint does not require it is not free, and
what it costs is not lines of code -- it is a precondition, and this script
measures how often a small random test would exercise it.
"""
import math
import random

BUDGET_LOG10 = 8.0          # a hundred million operations
RATE_LOG10 = 7.0            # a stated assumption: 10^7 operations per second


def largest_fitting(log10_ops, ceiling=10 ** 12):
    """Largest n with log10_ops(n) <= BUDGET_LOG10, by doubling then bisecting."""
    lo, hi = 1, 2
    while log10_ops(hi) <= BUDGET_LOG10:
        if hi >= ceiling:
            return None
        lo, hi = hi, min(hi * 2, ceiling)
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if log10_ops(mid) <= BUDGET_LOG10:
            lo = mid
        else:
            hi = mid
    return lo


CLASSES = [
    ("O(n)", lambda n: math.log10(n)),
    ("O(n log n)", lambda n: math.log10(n) + math.log10(math.log2(n))),
    ("O(n^2)", lambda n: 2 * math.log10(n)),
    ("O(n^3)", lambda n: 3 * math.log10(n)),
]

# --------------------------------------------- the same code, two constraints

print("One algorithm, six constraints. O(n^2) does not have a verdict -- only")
print("an O(n^2) *at a size* does.\n")
print(f"   {'n':>12}{'O(n)':>20}{'O(n log n)':>20}{'O(n^2)':>22}"
      f"   {'O(n^2) verdict':<12}")
print("   " + "-" * 90)
for n in (1_000, 5_000, 10_000, 50_000, 100_000, 1_000_000):
    line = f"   {n:>12,}"
    for _, fn in CLASSES[:3]:
        value = 10 ** fn(n)
        line += f"{value:>20,.0f}" if fn(n) <= 15 else f"{'10^' + f'{fn(n):.0f}':>20}"
    verdict = "fits" if CLASSES[2][1](n) <= BUDGET_LOG10 else "does not fit"
    print(line + f"   {verdict:<12}")

print()
print("The verdict flips between n = 10,000 and n = 50,000, and the exact")
print("place is worth remembering: n^2 reaches a hundred million at n =")
print("10,000. So a constraint of n <= 10^4 is a setter telling you that a")
print("quadratic solution is expected, and a constraint of n <= 10^5 is a")
print("setter telling you that it is not. Same algorithm, same code, opposite")
print("answers -- and the difference is one digit in the statement.")

print("\nStated as limits, which is how a setter thinks about them:\n")
print(f"   {'complexity':<14}{'largest n inside the budget':>30}")
print("   " + "-" * 44)
for name, fn in CLASSES:
    n = largest_fitting(fn)
    shown = f"{n:,}" if n is not None else "no limit below 10^12"
    print(f"   {name:<14}{shown:>30}")

print()
print("Read a constraint off this table rather than off the algorithm. If the")
print("statement says n <= 100,000, the intended solution is O(n log n) or")
print("better, and an O(n^2) sketch is not a slow version of the answer --")
print("it is not an answer.")

# ---------------------------------------------- the error in the other direction


def count_naive(values, k):
    """The slow, obvious version. No preconditions."""
    total = 0
    for i in range(len(values)):
        running = 0
        for j in range(i, len(values)):
            running += values[j]
            if running == k:
                total += 1
    return total


def count_with_prefix(values, k, seed=True):
    """The fast version. The seeded entry is a precondition."""
    seen = {0: 1} if seed else {}
    running = 0
    total = 0
    for v in values:
        running += v
        total += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return total


print("\nNow the other direction. At n = 1,000 the quadratic version above does")
print("499,500 additions. At the stated rate that is five hundredths of a")
print("second, which is inside every budget this book has used. So the clever")
print("version is not needed here, and choosing it is a decision about code")
print("rather than about speed.\n")
print(f"   {'n':>10}{'additions':>18}{'seconds at 1e7/s':>20}")
print("   " + "-" * 48)
for n in (100, 1_000, 10_000):
    pairs = n * (n + 1) // 2
    print(f"   {n:>10,}{pairs:>18,}{pairs / 10 ** RATE_LOG10:>19.4f}")

print()
print("What the clever version costs is not lines -- in Python it is usually")
print("shorter. It is a precondition: the empty prefix has to be in the")
print("dictionary before the loop starts, or every subarray that begins at")
print("index 0 is missed. Measure how often a random test would catch that")
print("omission:\n")
rng = random.Random(49)
print(f"   {'n range':<12}{'instances':>12}{'seed matters':>14}{'would catch it':>16}")
print("   " + "-" * 54)
for hi in (10, 20, 50, 200):
    instances = 2_000
    caught = 0
    for _ in range(instances):
        n = rng.randint(1, hi)
        values = [rng.randint(-3, 3) for _ in range(n)]
        k = rng.randint(-5, 5)
        if count_with_prefix(values, k, seed=True) != count_with_prefix(
                values, k, seed=False):
            caught += 1
    print(f"   {'1..' + str(hi):<12}{instances:>12,}{caught:>14,}"
          f"{100 * caught / instances:>15.1f}%")

print()
print("At the sizes a quick test uses, the omission is invisible most of the")
print("time, and the rate climbs as the list grows -- 31% at ten elements,")
print("58% at fifty. That is the shape of the trade: the fast version carries")
print("a precondition, the slow one carries none, and the precondition is")
print("exercised least on exactly the small inputs you would test with.")

print("\nSo the third question -- 'which structure?' -- comes after the second.")
print("Derive the budget from the constraint, choose the structure that meets")
print("it, and stop. A solution faster than the budget requires is not better;")
print("it is more to get right than the problem asked for. And a solution")
print("slower than the budget allows is not slower -- it is wrong.")
```

```text
One algorithm, six constraints. O(n^2) does not have a verdict -- only
an O(n^2) *at a size* does.

              n                O(n)          O(n log n)                O(n^2)   O(n^2) verdict
   ------------------------------------------------------------------------------------------
          1,000               1,000               9,966           1,000,000   fits        
          5,000               5,000              61,439          25,000,000   fits        
         10,000              10,000             132,877         100,000,000   fits        
         50,000              50,000             780,482       2,500,000,000   does not fit
        100,000             100,000           1,660,964      10,000,000,000   does not fit
      1,000,000           1,000,000          19,931,569   1,000,000,000,000   does not fit

The verdict flips between n = 10,000 and n = 50,000, and the exact
place is worth remembering: n^2 reaches a hundred million at n =
10,000. So a constraint of n <= 10^4 is a setter telling you that a
quadratic solution is expected, and a constraint of n <= 10^5 is a
setter telling you that it is not. Same algorithm, same code, opposite
answers -- and the difference is one digit in the statement.

Stated as limits, which is how a setter thinks about them:

   complexity       largest n inside the budget
   --------------------------------------------
   O(n)                             100,000,000
   O(n log n)                         4,523,071
   O(n^2)                                10,000
   O(n^3)                                   464

Read a constraint off this table rather than off the algorithm. If the
statement says n <= 100,000, the intended solution is O(n log n) or
better, and an O(n^2) sketch is not a slow version of the answer --
it is not an answer.

Now the other direction. At n = 1,000 the quadratic version above does
499,500 additions. At the stated rate that is five hundredths of a
second, which is inside every budget this book has used. So the clever
version is not needed here, and choosing it is a decision about code
rather than about speed.

            n         additions    seconds at 1e7/s
   ------------------------------------------------
          100             5,050             0.0005
        1,000           500,500             0.0500
       10,000        50,005,000             5.0005

What the clever version costs is not lines -- in Python it is usually
shorter. It is a precondition: the empty prefix has to be in the
dictionary before the loop starts, or every subarray that begins at
index 0 is missed. Measure how often a random test would catch that
omission:

   n range        instances  seed matters  would catch it
   ------------------------------------------------------
   1..10              2,000           630           31.5%
   1..20              2,000           850           42.5%
   1..50              2,000         1,166           58.3%
   1..200             2,000         1,454           72.7%

At the sizes a quick test uses, the omission is invisible most of the
time, and the rate climbs as the list grows -- 31% at ten elements,
58% at fifty. That is the shape of the trade: the fast version carries
a precondition, the slow one carries none, and the precondition is
exercised least on exactly the small inputs you would test with.

So the third question -- 'which structure?' -- comes after the second.
Derive the budget from the constraint, choose the structure that meets
it, and stop. A solution faster than the budget requires is not better;
it is more to get right than the problem asked for. And a solution
slower than the budget allows is not slower -- it is wrong.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49 demo -- the scenario: a nightly job that takes forty minutes.

A reporting job joins orders to customers. It works, it has worked for a
year, and it has become slow enough that the team has started scheduling
around it. The task is to find out why and to fix it without changing what
the report says.

The counting takes about a minute. What takes longer is the second half:
the fix that makes it fast also changes its answers, on a case the original
code handled by accident. That is the part a code review is actually for.
"""
import random
from collections import Counter

# ------------------------------------------------------------------ the data

rng = random.Random(49)
CUSTOMERS = [(cid, f"Customer {cid}") for cid in range(1, 401)]
CUSTOMERS.append((137, "Customer 137 (duplicate import)"))   # data-quality artefact

ORDERS = [(oid, rng.randint(1, 400)) for oid in range(1, 1_001)]
# Three orders deliberately reference the duplicated customer, so the
# difference between the two joins is visible rather than theoretical.
DUPLICATE_ID = CUSTOMERS[-1][0]
for oid in (5, 50, 500):
    ORDERS[oid - 1] = (oid, DUPLICATE_ID)


def join_naive(orders, customers):
    """For every order, look at every customer. Returns (rows, comparisons)."""
    comparisons = 0
    rows = []
    for order_id, customer_id in orders:
        for cid, name in customers:
            comparisons += 1
            if cid == customer_id:
                rows.append((order_id, customer_id, name))
    return rows, comparisons


def join_indexed(orders, customers, keep="last"):
    """Build an index once, then one pass. Returns (rows, work)."""
    work = 0
    index = {}
    for cid, name in customers:
        work += 1
        if keep == "last" or cid not in index:
            index[cid] = name
    rows = []
    for order_id, customer_id in orders:
        work += 1
        if customer_id in index:
            rows.append((order_id, customer_id, index[customer_id]))
    return rows, work


def join_indexed_multi(orders, customers):
    """The index that keeps every match, so it agrees with the naive join."""
    work = 0
    index = {}
    for cid, name in customers:
        work += 1
        index.setdefault(cid, []).append(name)
    rows = []
    for order_id, customer_id in orders:
        work += 1
        for name in index.get(customer_id, ()):
            rows.append((order_id, customer_id, name))
    return rows, work


# ------------------------------------------------------------- the code review

print("The job joins 1,000 orders to 400 customers on customer id.\n")
naive_rows, naive_work = join_naive(ORDERS, CUSTOMERS)
index_rows, index_work = join_indexed(ORDERS, CUSTOMERS)
multi_rows, multi_work = join_indexed_multi(ORDERS, CUSTOMERS)

print(f"   nested loop          rows {len(naive_rows):>6,}   "
      f"comparisons {naive_work:>10,}")
print(f"   dict index, last wins rows {len(index_rows):>6,}   "
      f"work        {index_work:>10,}")
print(f"   dict index, all rows  rows {len(multi_rows):>6,}   "
      f"work        {multi_work:>10,}")
print()
print(f"   naive vs index, identical output : "
      f"{naive_rows == index_rows}")
print(f"   naive vs multi, identical output : "
      f"{naive_rows == multi_rows}")

naive_counts = Counter(row[0] for row in naive_rows)
index_counts = Counter(row[0] for row in index_rows)
differing = sorted(oid for oid in naive_counts if naive_counts[oid] != index_counts[oid])
affected = {cid for oid, cid in ORDERS if oid in set(differing)}
all_duplicate = affected == {DUPLICATE_ID}
print()
print(f"   orders whose rows differ between naive and index : {len(differing)}")
print(f"   those orders are {differing}")
print(f"   all of them reference customer {DUPLICATE_ID} : {all_duplicate}")
print(f"   rows the naive join produced   : {len(naive_rows):,}")
print(f"   rows the last-wins index made  : {len(index_rows):,}")
print()
print("This is the finding, and it is not a performance finding. The nested")
print("loop appends a row for *every* customer that matches, so the duplicate")
print("id produces two rows for each order that references it. A dictionary")
print("keyed by customer id holds one name per key, so the index version")
print("silently drops one of them. The report changes, and it changes only on")
print("the orders that touch that customer -- which is why nobody noticed.")

print("\nThe fix is an index of lists, which keeps every match. Verify it:\n")
print(f"   rows in the naive output      : {len(naive_rows):,}")
print(f"   rows in the list-index output : {len(multi_rows):,}")
print(f"   identical, row for row        : {naive_rows == multi_rows}")

# ------------------------------------------------------------- the arithmetic

print("\nNow the arithmetic, which is the part that takes a minute. The nested")
print("loop does one comparison per (order, customer) pair, so its cost is")
print("fixed by the sizes and not by the data. Check that:\n")
print(f"   {'orders':>8}{'customers':>11}{'comparisons':>14}"
      f"{'orders x customers':>21}{'agree':>8}")
print("   " + "-" * 62)
for n_orders, n_customers in ((100, 40), (200, 80), (400, 160)):
    orders = [(i, rng.randint(1, n_customers)) for i in range(n_orders)]
    customers = [(c, f"C{c}") for c in range(1, n_customers + 1)]
    _, work = join_naive(orders, customers)
    print(f"   {n_orders:>8,}{n_customers:>11,}{work:>14,}"
          f"{n_orders * n_customers:>21,}{str(work == n_orders * n_customers):>8}")

print("\nAnd at the sizes the job actually runs at. The nested-loop column is")
print("the formula just verified; the index column is counted.\n")
print(f"   {'orders':>10}{'customers':>11}{'nested loop':>18}"
      f"{'index':>12}{'ratio':>10}")
print("   " + "-" * 61)
for n_orders, n_customers in ((1_000, 400), (50_000, 20_000), (200_000, 120_000)):
    orders = [(i, rng.randint(1, n_customers)) for i in range(n_orders)]
    customers = [(c, f"C{c}") for c in range(1, n_customers + 1)]
    _, work = join_indexed_multi(orders, customers)
    nested = n_orders * n_customers
    print(f"   {n_orders:>10,}{n_customers:>11,}{nested:>18,}{work:>12,}"
          f"{nested / work:>9,.0f}x")

print()
n_orders, n_customers = 200_000, 120_000
nested = n_orders * n_customers
index_ops = n_orders + n_customers
print(f"At {n_orders:,} orders and {n_customers:,} customers the nested loop does")
print(f"{nested:,} comparisons. At a stated 10^7 comparisons per second that")
print(f"is {nested / 1e7:,.0f} seconds, or {nested / 1e7 / 60:,.0f} minutes -- which is")
print("the forty minutes the team has been scheduling around.")
print()
print(f"The index does {index_ops:,} operations instead: "
      f"{nested / index_ops:,.0f}x fewer, and")
print(f"{index_ops / 1e7:.3f} seconds instead of {nested / 1e7:,.0f}.")
print()
print("Two things were needed and only one of them was about speed. The index")
print("fixed the time. Finding the duplicate -- and deciding what the report")
print("should say about it -- fixed the correctness, and it would have been")
print("introduced as a bug if nobody had diffed the two outputs.")
```

```text
The job joins 1,000 orders to 400 customers on customer id.

   nested loop          rows  1,003   comparisons    401,000
   dict index, last wins rows  1,000   work             1,401
   dict index, all rows  rows  1,003   work             1,401

   naive vs index, identical output : False
   naive vs multi, identical output : True

   orders whose rows differ between naive and index : 3
   those orders are [5, 50, 500]
   all of them reference customer 137 : True
   rows the naive join produced   : 1,003
   rows the last-wins index made  : 1,000

This is the finding, and it is not a performance finding. The nested
loop appends a row for *every* customer that matches, so the duplicate
id produces two rows for each order that references it. A dictionary
keyed by customer id holds one name per key, so the index version
silently drops one of them. The report changes, and it changes only on
the orders that touch that customer -- which is why nobody noticed.

The fix is an index of lists, which keeps every match. Verify it:

   rows in the naive output      : 1,003
   rows in the list-index output : 1,003
   identical, row for row        : True

Now the arithmetic, which is the part that takes a minute. The nested
loop does one comparison per (order, customer) pair, so its cost is
fixed by the sizes and not by the data. Check that:

     orders  customers   comparisons   orders x customers   agree
   --------------------------------------------------------------
        100         40         4,000                4,000    True
        200         80        16,000               16,000    True
        400        160        64,000               64,000    True

And at the sizes the job actually runs at. The nested-loop column is
the formula just verified; the index column is counted.

       orders  customers       nested loop       index     ratio
   -------------------------------------------------------------
        1,000        400           400,000       1,400      286x
       50,000     20,000     1,000,000,000      70,000   14,286x
      200,000    120,000    24,000,000,000     320,000   75,000x

At 200,000 orders and 120,000 customers the nested loop does
24,000,000,000 comparisons. At a stated 10^7 comparisons per second that
is 2,400 seconds, or 40 minutes -- which is
the forty minutes the team has been scheduling around.

The index does 320,000 operations instead: 75,000x fewer, and
0.032 seconds instead of 2,400.

Two things were needed and only one of them was about speed. The index
fixed the time. Finding the duplicate -- and deciding what the report
should say about it -- fixed the correctness, and it would have been
introduced as a bug if nobody had diffed the two outputs.
```

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

```python run
#!/usr/bin/env python3
"""Chapter 49, Exercise 1 -- sort it first.

The problem: given a list of numbers, find the largest gap between two
values that are adjacent *in sorted order*. [3, 1, 9, 4] sorted is
[1, 3, 4, 9] and the gaps are 2, 1, 5, so the answer is 5.

The slow version finds each value's successor by scanning the list, which is
n comparisons per element. The fast version sorts and walks once. Both are
correct, and the counting is what separates them.
"""
import random

# ------------------------------------------------------------------ solutions


def merge_sort_counted(values):
    comparisons = 0

    def merge(left, right):
        nonlocal comparisons
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs):
        if len(xs) < 2:
            return list(xs)
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(values), comparisons


def largest_gap_scanning(values):
    """Find each element's successor by scanning. Returns (gap, comparisons)."""
    comparisons = 0
    ordered = []
    for v in values:
        best = None
        for w in values:
            comparisons += 1
            if w > v and (best is None or w < best):
                best = w
        ordered.append(best)
    gaps = [b - v for v, b in zip(values, ordered) if b is not None]
    return (max(gaps) if gaps else 0), comparisons


def largest_gap_sorted(values):
    """Sort, then look at neighbours. Returns (gap, comparisons)."""
    ordered, comparisons = merge_sort_counted(values)
    best = 0
    for i in range(1, len(ordered)):
        comparisons += 1
        best = max(best, ordered[i] - ordered[i - 1])
    return best, comparisons


# ---------------------------------------------------------------- correctness

print("Two methods, and the first question is whether they agree.\n")
rng = random.Random(49)
disagreements = 0
for _ in range(400):
    n = rng.randint(2, 40)
    values = rng.sample(range(10 * n), n)
    if largest_gap_scanning(values)[0] != largest_gap_sorted(values)[0]:
        disagreements += 1
print(f"   400 random instances, distinct answers : {disagreements}")
print()
print("The scanning version compares every element with every element, so its")
print("comparison count is n^2 whatever the data is. Check that:\n")
print(f"   {'n':>7}{'comparisons':>16}{'n^2':>12}{'agree':>8}")
print("   " + "-" * 43)
for n in (50, 100, 200, 400):
    values = rng.sample(range(10 * n), n)
    _, comparisons = largest_gap_scanning(values)
    print(f"   {n:>7,}{comparisons:>16,}{n * n:>12,}"
          f"{str(comparisons == n * n):>8}")

# ------------------------------------------------------------------ the cost

print("\nNow the two side by side. The scanning column is the formula just")
print("verified; the sorted column is counted, including its own sort.\n")
print(f"   {'n':>10}{'scan for successors':>22}{'sort + one pass':>18}"
      f"{'ratio':>10}")
print("   " + "-" * 60)
for n in (1_000, 10_000, 100_000):
    values = rng.sample(range(10 * n), n)
    slow = n * n
    _, fast = largest_gap_sorted(values)
    print(f"   {n:>10,}{slow:>22,}{fast:>18,}{slow / fast:>9,.0f}x")

print()
print("The sorted version's cost is n log n comparisons for the sort plus n for")
print("the walk, so the ratio is n^2 divided by about n log n -- which grows")
print("with n and does not stop. And the sort is not a detail that can be")
print("skipped: once the values are in order, the pair that matters is always")
print("two neighbours, so the question 'which two values are closest' becomes")
print("'which adjacent pair is closest', and a single pass answers it.")
print()
print("That is what 'sort it first' means. It is not that sorting is fast. It")
print("is that sorting makes the answer local.")
```

```text
Two methods, and the first question is whether they agree.

   400 random instances, distinct answers : 0

The scanning version compares every element with every element, so its
comparison count is n^2 whatever the data is. Check that:

         n     comparisons         n^2   agree
   -------------------------------------------
        50           2,500       2,500    True
       100          10,000      10,000    True
       200          40,000      40,000    True
       400         160,000     160,000    True

Now the two side by side. The scanning column is the formula just
verified; the sorted column is counted, including its own sort.

            n   scan for successors   sort + one pass     ratio
   ------------------------------------------------------------
        1,000             1,000,000             9,686      103x
       10,000           100,000,000           130,494      766x
      100,000        10,000,000,000         1,636,339    6,111x

The sorted version's cost is n log n comparisons for the sort plus n for
the walk, so the ratio is n^2 divided by about n log n -- which grows
with n and does not stop. And the sort is not a detail that can be
skipped: once the values are in order, the pair that matters is always
two neighbours, so the question 'which two values are closest' becomes
'which adjacent pair is closest', and a single pass answers it.

That is what 'sort it first' means. It is not that sorting is fast. It
is that sorting makes the answer local.
```

:::

:::solution Exercise 2

The middle implementation is the interesting one, because a built-in method makes a quadratic loop
read like a fast one.

```python run
#!/usr/bin/env python3
"""Chapter 49, Exercise 2 -- the budget says O(n).

The problem: given a list, return the first element that occurs exactly
once, in the order the list presents them. [4, 5, 4, 6, 5] has 6 as its
answer; [1, 1, 2, 2] has none.

The slow version asks, of each element in turn, "how many times does this
value occur?" and answers by looking at the whole list. The fast version
counts everything once and then asks a dictionary. The exercise is worth
doing because of a trap in the middle: the slow version can be written with
a built-in method that makes it *look* fast.
"""
import random
from collections import Counter

# ------------------------------------------------------------------ solutions


def first_unique_scanning(values):
    """Count each element's occurrences by walking the list.

    Returns (answer, comparisons, elements_examined).
    """
    comparisons = 0
    examined = 0
    for v in values:
        examined += 1
        occurrences = 0
        for w in values:
            comparisons += 1
            if w == v:
                occurrences += 1
        if occurrences == 1:
            return v, comparisons, examined
    return None, comparisons, examined


def first_unique_with_count(values):
    """The same loop written with list.count(). Returns (answer, calls)."""
    calls = 0
    for v in values:
        calls += 1
        if values.count(v) == 1:
            return v, calls
    return None, calls


def first_unique_counted(values):
    """One counting pass, then one lookup pass. Returns (answer, work)."""
    counts = Counter(values)
    work = len(values)
    for v in values:
        work += 1
        if counts[v] == 1:
            return v, work
    return None, work


# ---------------------------------------------------------------- correctness

print("Three implementations, and they must agree before any of them counts.\n")
rng = random.Random(49)
disagreements = 0
for _ in range(400):
    n = rng.randint(1, 40)
    values = [rng.randint(1, 12) for _ in range(n)]
    answers = {first_unique_scanning(values)[0],
               first_unique_with_count(values)[0],
               first_unique_counted(values)[0]}
    if len(answers) != 1:
        disagreements += 1
print(f"   400 random instances, distinct answers : {disagreements}")

# ------------------------------------------------------------------- the trap

print("\nHere is the trap. The middle implementation above reads like a library")
print("call, and it is quadratic anyway, because `list.count` walks the whole")
print("list. Show that the two slow versions do the same work:\n")
print(f"   {'n':>6}{'scanning comparisons':>22}{'calls to .count()':>19}"
      f"{'calls x n':>12}{'agree':>8}")
print("   " + "-" * 67)
for n in (50, 100, 200, 400):
    values = [rng.randint(1, n) for _ in range(n)]
    _, comparisons, examined = first_unique_scanning(values)
    _, calls = first_unique_with_count(values)
    print(f"   {n:>6,}{comparisons:>22,}{calls:>19,}{calls * n:>12,}"
          f"{str(comparisons == calls * n):>8}")

print()
print("The two columns agree because both do exactly one comparison per")
print("element per element examined. `list.count(v)` is a loop; it is written")
print("in C, which is why it feels free, and it is still n comparisons every")
print("time it is called. Replacing a hand-written loop with a built-in does")
print("not change the algorithm, and the complexity budget does not care which")
print("language the loop is written in.")

# ------------------------------------------------------------------ the cost

print("\nNow the version that changes the algorithm: count everything once, then")
print("ask the dictionary. Two passes, and each element is visited once per")
print("pass.\n")
print(f"   {'n':>10}{'quadratic':>18}{'Counter + pass':>17}{'ratio':>10}")
print("   " + "-" * 55)
for n in (1_000, 10_000, 100_000):
    values = [rng.randint(1, n) for _ in range(n)]
    slow = n * n
    _, fast = first_unique_counted(values)
    print(f"   {n:>10,}{slow:>18,}{fast:>17,}{slow / fast:>9,.0f}x")

print()
print("The ratio is n^2 over 2n, which is n/2, so it grows with the input and")
print("keeps growing. The constraint that would force this choice is n <= 10^5")
print("or larger: at n = 100,000 the quadratic version does ten billion")
print("comparisons and the counting version does two hundred thousand. Below")
print("n = 10^4 both fit a hundred-million-operation budget, and then the")
print("simpler one is the better answer.")
```

```text
Three implementations, and they must agree before any of them counts.

   400 random instances, distinct answers : 0

Here is the trap. The middle implementation above reads like a library
call, and it is quadratic anyway, because `list.count` walks the whole
list. Show that the two slow versions do the same work:

        n  scanning comparisons  calls to .count()   calls x n   agree
   -------------------------------------------------------------------
       50                   150                  3         150    True
      100                   200                  2         200    True
      200                   200                  1         200    True
      400                   800                  2         800    True

The two columns agree because both do exactly one comparison per
element per element examined. `list.count(v)` is a loop; it is written
in C, which is why it feels free, and it is still n comparisons every
time it is called. Replacing a hand-written loop with a built-in does
not change the algorithm, and the complexity budget does not care which
language the loop is written in.

Now the version that changes the algorithm: count everything once, then
ask the dictionary. Two passes, and each element is visited once per
pass.

            n         quadratic   Counter + pass     ratio
   -------------------------------------------------------
        1,000         1,000,000            1,001      999x
       10,000       100,000,000           10,001    9,999x
      100,000    10,000,000,000          100,004   99,996x

The ratio is n^2 over 2n, which is n/2, so it grows with the input and
keeps growing. The constraint that would force this choice is n <= 10^5
or larger: at n = 100,000 the quadratic version does ten billion
comparisons and the counting version does two hundred thousand. Below
n = 10^4 both fit a hundred-million-operation budget, and then the
simpler one is the better answer.
```

:::

:::solution Exercise 3

The set version is right about which values are shared and wrong about how many times. That is a
difference in the question, not a bug in the code.

```python run
#!/usr/bin/env python3
"""Chapter 49, Exercise 3 -- the structure is a set, and a set changes the answer.

The problem: given two lists, return the elements that appear in both.

The slow version asks, of each element of the first list, "is it anywhere in
the second?" and answers by walking the second list. The fast version puts
the second list in a set and asks the set. Both are correct, and the counting
is not the interesting part of this exercise.

The interesting part is what a set cannot represent. It holds each value
once, so the fast version quietly drops duplicates the slow version emitted.
That is the same defect as the one in this chapter's scenario, and it is
worth meeting twice.
"""
import random
from collections import Counter

# ------------------------------------------------------------------ solutions


def intersect_scanning(a, b):
    """Ask the second list about each element of the first."""
    comparisons = 0
    rows = []
    for x in a:
        for y in b:
            comparisons += 1
            if x == y:
                rows.append(x)
                break
    return rows, comparisons


def intersect_set(a, b):
    """Put b in a set, then ask it once per element of a."""
    lookup = set(b)
    work = len(b)
    rows = []
    for x in a:
        work += 1
        if x in lookup:
            rows.append(x)
    return rows, work


def intersect_counted(a, b):
    """Keep a's order and a's multiplicity, capped by b's multiplicity."""
    limit = Counter(b)
    work = len(b)
    rows = []
    for x in a:
        work += 1
        if limit[x] > 0:
            limit[x] -= 1
            rows.append(x)
    return rows, work


# ---------------------------------------------------------------- correctness

print("Three implementations. The first two agree on *membership* and disagree")
print("on *multiplicity*, which is the whole point of the exercise.\n")
rng = random.Random(49)
a = [rng.randint(1, 12) for _ in range(30)]
b = [rng.randint(1, 12) for _ in range(20)]
scan_rows, _ = intersect_scanning(a, b)
set_rows, _ = intersect_set(a, b)
counted_rows, _ = intersect_counted(a, b)

print(f"   a has {len(a)} elements, b has {len(b)}")
print(f"   scanning, rows returned      : {len(scan_rows)}")
print(f"   set, rows returned           : {len(set_rows)}")
print(f"   counted, rows returned       : {len(counted_rows)}")
print(f"   scanning vs set, identical   : {scan_rows == set_rows}")
print(f"   scanning vs counted, identical : {scan_rows == counted_rows}")
print()
print("The set version returns fewer rows, and every row it returns is in the")
print("other two. It is not wrong about which values are shared; it is wrong")
print("about how many times each one is shared, and it has no way to record")
print("that. A set is the right structure for a membership question and the")
print("wrong one for a multiplicity question -- and the two questions look")
print("identical until you count the rows.\n")

# --------------------------------------------------------------- the counting

print("Now the cost. The scanning version does one comparison per pair, so its")
print("count is at most len(a) * len(b), reached when nothing matches. A match")
print("stops the inner loop early, so the count lands under the product:\n")
print(f"   {'len(a)':>8}{'len(b)':>8}{'comparisons':>14}{'a x b':>10}"
      f"{'under it by':>13}")
print("   " + "-" * 53)
for n, m in ((40, 30), (80, 60), (160, 120)):
    xs = [rng.randint(1, n) for _ in range(n)]
    ys = [rng.randint(1, n) for _ in range(m)]
    _, comparisons = intersect_scanning(xs, ys)
    print(f"   {n:>8,}{m:>8,}{comparisons:>14,}{n * m:>10,}"
          f"{(n * m - comparisons) / (n * m):>12.1%}")

print()
print("The counted value is always below the product and the gap is the work")
print("the early exits saved. A budget uses the product anyway, because a")
print("bound that depends on how many values the two lists share is not a")
print("bound -- it is a measurement of the input.\n")
print(f"   {'len(a)':>10}{'len(b)':>10}{'scanning, worst':>18}{'set':>12}"
      f"{'ratio':>10}")
print("   " + "-" * 60)
for n, m in ((1_000, 1_000), (10_000, 10_000), (100_000, 100_000)):
    xs = [rng.randint(1, n) for _ in range(n)]
    ys = [rng.randint(1, n) for _ in range(m)]
    slow = n * m
    _, fast = intersect_set(xs, ys)
    print(f"   {n:>10,}{m:>10,}{slow:>18,}{fast:>12,}{slow / fast:>9,.0f}x")

print()
print("The set version costs len(b) to build the set plus len(a) to ask it,")
print("so the ratio against len(a) * len(b) is about n/2 when the lists are")
print("the same length. As with every other exercise in this chapter the")
print("ratio grows with n, and the reason is the same: one side is a product")
print("and the other is a sum.")
```

```text
Three implementations. The first two agree on *membership* and disagree
on *multiplicity*, which is the whole point of the exercise.

   a has 30 elements, b has 20
   scanning, rows returned      : 27
   set, rows returned           : 27
   counted, rows returned       : 15
   scanning vs set, identical   : True
   scanning vs counted, identical : False

The set version returns fewer rows, and every row it returns is in the
other two. It is not wrong about which values are shared; it is wrong
about how many times each one is shared, and it has no way to record
that. A set is the right structure for a membership question and the
wrong one for a multiplicity question -- and the two questions look
identical until you count the rows.

Now the cost. The scanning version does one comparison per pair, so its
count is at most len(a) * len(b), reached when nothing matches. A match
stops the inner loop early, so the count lands under the product:

     len(a)  len(b)   comparisons     a x b  under it by
   -----------------------------------------------------
         40      30           953     1,200       20.6%
         80      60         3,592     4,800       25.2%
        160     120        12,886    19,200       32.9%

The counted value is always below the product and the gap is the work
the early exits saved. A budget uses the product anyway, because a
bound that depends on how many values the two lists share is not a
bound -- it is a measurement of the input.

       len(a)    len(b)   scanning, worst         set     ratio
   ------------------------------------------------------------
        1,000     1,000         1,000,000       2,000      500x
       10,000    10,000       100,000,000      20,000    5,000x
      100,000   100,000    10,000,000,000     200,000   50,000x

The set version costs len(b) to build the set plus len(a) to ask it,
so the ratio against len(a) * len(b) is about n/2 when the lists are
the same length. As with every other exercise in this chapter the
ratio grows with n, and the reason is the same: one side is a product
and the other is a sum.
```

:::

:::solution Exercise 4

One sample of a heavy-tailed cost tells you nothing, so this one enumerates every input instead and
counts the distribution exactly.

```python run
#!/usr/bin/env python3
"""Chapter 49, Exercise 4 -- the complexity depends on the input.

Every claim in this chapter has been of the form "this costs about n log n".
That is a shorthand, and this exercise is about what the shorthand hides. A
single function can be O(1) and O(n) and O(n^2), depending on which input it
is handed, and a budget derived from the wrong case is a budget for a program
you are not writing.

Two functions. The first is a linear search, where the spread is n. The
second is an early-exit duplicate check, where the spread is n^2 -- and where
the case that actually happens is nowhere near the worst one.
"""
import math
import random
from itertools import product

# --------------------------------------------------------------- the search


def linear_search_counted(values, target):
    """Return (index, comparisons). The count depends on where target sits."""
    comparisons = 0
    for i, v in enumerate(values):
        comparisons += 1
        if v == target:
            return i, comparisons
    return -1, comparisons


rng = random.Random(49)
N = 1_000
values = rng.sample(range(10 * N), N)

print("A linear search, run four times on the same list with four targets.\n")
print(f"   {'target':<28}{'index':>8}{'comparisons':>14}")
print("   " + "-" * 50)
cases = [
    ("the first element", values[0]),
    ("the middle element", values[N // 2]),
    ("the last element", values[-1]),
    ("not present at all", -1),
]
for label, target in cases:
    index, comparisons = linear_search_counted(values, target)
    print(f"   {label:<28}{index:>8,}{comparisons:>14,}")

print()
print("One function, one list, and the cost ranges from 1 to 1,000. So 'this")
print("search is O(n)' is not a statement about the function. It is a")
print("statement about the worst case, and the worst case is the one where")
print("the element is last or absent.\n")
print("The average over all possible targets has an exact value, and it is")
print("worth deriving rather than guessing: a target at position i costs i + 1")
print("comparisons, so the total over every position is 1 + 2 + ... + n.\n")
n = 500
total = sum(linear_search_counted(values, values[i])[1] for i in range(n))
print(f"   positions summed            : {n:,}")
print(f"   comparisons in total        : {total:,}")
print(f"   n(n+1)/2                    : {n * (n + 1) // 2:,}")
print(f"   average per search          : {total / n:.1f}")
print(f"   (n+1)/2                     : {(n + 1) / 2:.1f}")
print()
print("The average is (n+1)/2, exactly, which is half the worst case. That is")
print("the usual shape: the average sits between the best and the worst, and")
print("the budget has to be built from the worst unless you can prove the")
print("worst cannot happen.")

# ------------------------------------------------------------- the early exit


def has_duplicate_counted(values):
    """Early exit on the first duplicate. Returns (found, comparisons)."""
    comparisons = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            comparisons += 1
            if values[i] == values[j]:
                return True, comparisons
    return False, comparisons


print("\nNow the interesting one. Here is a function whose worst case is")
print("n(n-1)/2 comparisons and whose real cost is nowhere near it.\n")
print("The early exit makes the count a random variable, so a sample says")
print("nothing -- the distribution is heavy-tailed and a handful of runs")
print("lands anywhere. Do not sample it. Enumerate *every* input instead: for")
print("n values drawn from n possibilities there are n^n of them, and up to")
print("n = 7 that is under a million, so the distribution can be counted")
print("exactly rather than estimated.\n")
print(f"   {'n':>3}{'inputs':>10}{'smallest':>10}{'median':>8}{'mean':>9}"
      f"{'mean / n':>10}{'worst':>8}{'at the worst':>14}")
print("   " + "-" * 73)
sizes = []
for n in range(2, 8):
    counts = sorted(has_duplicate_counted(xs)[1] for xs in product(range(n), repeat=n))
    total = len(counts)
    mean = sum(counts) / total
    at_worst = sum(1 for c in counts if c == counts[-1]) / total
    sizes.append((n, total, mean, counts[-1], at_worst))
    print(f"   {n:>3}{total:>10,}{counts[0]:>10}{counts[total // 2]:>8}"
          f"{mean:>9.3f}{mean / n:>10.3f}{counts[-1]:>8}{at_worst:>13.1%}")

print()
print("Every number in that table is exact. The `mean / n` column climbs")
print("towards 1 and the `at the worst` column collapses, and the two facts")
print("have the same cause.\n")
print("Look at the first row of the double loop. It compares v[0] with")
print("v[1], v[2], ... and stops at the first value equal to v[0]. Each")
print("candidate matches with probability 1/n, so finding one takes about n")
print("draws -- but the row is only n-1 long. So the first row alone accounts")
print("for about n comparisons when it succeeds, and it fails to find")
print("anything with probability (1 - 1/n)^(n-1):\n")
print(f"   {'n':>8}{'(1 - 1/n)^(n-1)':>20}{'1/e':>10}")
print("   " + "-" * 38)
for n in (5, 50, 500, 50_000):
    print(f"   {n:>8,}{(1 - 1 / n) ** (n - 1):>20.4f}{1 / math.e:>10.4f}")

print()
print("So roughly a third of the time the first row finds nothing and the")
print("work moves to the second row, which behaves the same way. The total")
print("therefore lands on the order of n rather than n^2, and the mean/n")
print("column is that fact measured rather than argued.")
print()
print("What the table also shows is that the worst case is not merely")
print("unlikely, it is *rare*: at n = 7 only 1.2% of the 823,543 possible")
print("inputs reach n(n-1)/2 comparisons, and the mean is 6.3 against a worst")
print("of 21. The worst case needs every value distinct, which is the input")
print("the function was written to detect and the one the distribution almost")
print("never produces.")
print()
print("Three numbers, disagreeing by orders of magnitude: 1 comparison in the")
print("best case, about 0.9n in the case that happens, and n(n-1)/2 in the")
print("worst. A complexity claim that names none of them is not a claim, and")
print("a budget built from the worst case would have rejected a function that")
print("is fine -- the same mistake as building one from the best case, made")
print("in the other direction.")
```

```text
A linear search, run four times on the same list with four targets.

   target                         index   comparisons
   --------------------------------------------------
   the first element                  0             1
   the middle element               500           501
   the last element                 999         1,000
   not present at all                -1         1,000

One function, one list, and the cost ranges from 1 to 1,000. So 'this
search is O(n)' is not a statement about the function. It is a
statement about the worst case, and the worst case is the one where
the element is last or absent.

The average over all possible targets has an exact value, and it is
worth deriving rather than guessing: a target at position i costs i + 1
comparisons, so the total over every position is 1 + 2 + ... + n.

   positions summed            : 500
   comparisons in total        : 125,250
   n(n+1)/2                    : 125,250
   average per search          : 250.5
   (n+1)/2                     : 250.5

The average is (n+1)/2, exactly, which is half the worst case. That is
the usual shape: the average sits between the best and the worst, and
the budget has to be built from the worst unless you can prove the
worst cannot happen.

Now the interesting one. Here is a function whose worst case is
n(n-1)/2 comparisons and whose real cost is nowhere near it.

The early exit makes the count a random variable, so a sample says
nothing -- the distribution is heavy-tailed and a handful of runs
lands anywhere. Do not sample it. Enumerate *every* input instead: for
n values drawn from n possibilities there are n^n of them, and up to
n = 7 that is under a million, so the distribution can be counted
exactly rather than estimated.

     n    inputs  smallest  median     mean  mean / n   worst  at the worst
   -------------------------------------------------------------------------
     2         4         1       1    1.000     0.500       1       100.0%
     3        27         1       2    2.111     0.704       3        44.4%
     4       256         1       3    3.203     0.801       6        18.8%
     5     3,125         1       4    4.264     0.853      10         7.7%
     6    46,656         1       4    5.302     0.884      15         3.1%
     7   823,543         1       5    6.327     0.904      21         1.2%

Every number in that table is exact. The `mean / n` column climbs
towards 1 and the `at the worst` column collapses, and the two facts
have the same cause.

Look at the first row of the double loop. It compares v[0] with
v[1], v[2], ... and stops at the first value equal to v[0]. Each
candidate matches with probability 1/n, so finding one takes about n
draws -- but the row is only n-1 long. So the first row alone accounts
for about n comparisons when it succeeds, and it fails to find
anything with probability (1 - 1/n)^(n-1):

          n     (1 - 1/n)^(n-1)       1/e
   --------------------------------------
          5              0.4096    0.3679
         50              0.3716    0.3679
        500              0.3682    0.3679
     50,000              0.3679    0.3679

So roughly a third of the time the first row finds nothing and the
work moves to the second row, which behaves the same way. The total
therefore lands on the order of n rather than n^2, and the mean/n
column is that fact measured rather than argued.

What the table also shows is that the worst case is not merely
unlikely, it is *rare*: at n = 7 only 1.2% of the 823,543 possible
inputs reach n(n-1)/2 comparisons, and the mean is 6.3 against a worst
of 21. The worst case needs every value distinct, which is the input
the function was written to detect and the one the distribution almost
never produces.

Three numbers, disagreeing by orders of magnitude: 1 comparison in the
best case, about 0.9n in the case that happens, and n(n-1)/2 in the
worst. A complexity claim that names none of them is not a claim, and
a budget built from the worst case would have rejected a function that
is fine -- the same mistake as building one from the best case, made
in the other direction.
```

:::

:::solution Exercise 5

The window is the O(n) answer and it depends on an assumption that the statement may not have made.

```python run
#!/usr/bin/env python3
"""Chapter 49, Exercise 5 -- the sliding window, and the assumption under it.

The problem: given a list and a number k, find the length of the longest
contiguous stretch whose elements sum to at most k.

This is the shape that usually ends a chapter on complexity budgets: n is
large, so the answer is O(n), and the O(n) answer is a window with two
pointers. This exercise is about the other half of reading a problem
statement. A size limit tells you the complexity you need; an *assumption*
tells you which algorithms are available. This one has both, and the
assumption is easy to read past.

The window is correct only while the values are non-negative. Take that away
and it is silently wrong -- not slow, wrong -- because the property it
depends on is gone.
"""
import random

# ------------------------------------------------------------------ solutions


def longest_naive(values, k):
    """Every stretch, added up from scratch. Correct for any values."""
    best = 0
    additions = 0
    for i in range(len(values)):
        running = 0
        for j in range(i, len(values)):
            running += values[j]
            additions += 1
            if running <= k:
                best = max(best, j - i + 1)
    return best, additions


def longest_window(values, k):
    """Two pointers. O(n) -- and only correct when every value is >= 0."""
    left = 0
    running = 0
    best = 0
    steps = 0
    for right in range(len(values)):
        running += values[right]
        steps += 1
        while running > k and left <= right:
            running -= values[left]
            left += 1
            steps += 1
        best = max(best, right - left + 1)
    return best, steps


# ------------------------------------------------------- the smallest witness

print("Start with the smallest input where the window is wrong, because a")
print("counterexample beats an argument.\n")
WITNESS = [4, -3, 2]
K = 3
print(f"   values {WITNESS}, k = {K}")
print(f"   every stretch, added up : {longest_naive(WITNESS, K)[0]}")
print(f"   sliding window          : {longest_window(WITNESS, K)[0]}")
print()
print("The answer is 3: the whole list sums to 3, which is within k. The")
print("window reports 2, and here is why. It expands to include the 4, sees")
print("the sum exceed k, and shrinks from the left -- discarding the 4. That")
print("is the only move it has, and it is the wrong one, because the -3 that")
print("follows would have brought the sum back under k. The window assumes")
print("that once the sum is too large, dropping the leftmost element is the")
print("only way to make it smaller. With a negative value still ahead, that")
print("is false.")

rng = random.Random(49)
print("\nNow count how often it happens:\n")
print(f"   {'values':<24}{'instances':>11}{'window wrong':>15}")
print("   " + "-" * 50)
wrong_counts = {}
for label, lo, hi in (("non-negative", 0, 9), ("mixed signs", -9, 9)):
    instances = 2_000
    wrong = 0
    for _ in range(instances):
        n = rng.randint(1, 12)
        values = [rng.randint(lo, hi) for _ in range(n)]
        k = rng.randint(-5, 15)
        if longest_window(values, k)[0] != longest_naive(values, k)[0]:
            wrong += 1
    wrong_counts[label] = wrong
    print(f"   {label:<24}{instances:>11,}{wrong:>15,}")

print()
print(f"Nothing when the values are non-negative, and {wrong_counts['mixed signs']:,} of "
      f"{2_000:,} when they")
print("are not -- about a third of the inputs. The algorithm did not change")
print("between those two rows and neither did the code. What changed is")
print("whether the assumption it depends on holds, and nothing in the window")
print("itself checks.")

# ---------------------------------------------------------------- the cost

print("\nThe cost is the reason the window is worth having at all. The naive")
print("version adds up n(n+1)/2 stretches, fixed before the data arrives:\n")
print(f"   {'n':>7}{'additions':>14}{'n(n+1)/2':>14}{'agree':>8}")
print("   " + "-" * 43)
for n in (100, 200, 400):
    values = [rng.randint(0, 9) for _ in range(n)]
    _, additions = longest_naive(values, 20)
    print(f"   {n:>7,}{additions:>14,}{n * (n + 1) // 2:>14,}"
          f"{str(additions == n * (n + 1) // 2):>8}")

print("\nAnd the two side by side, on non-negative data where both are right.\n")
print(f"   {'n':>10}{'add up every stretch':>22}{'window':>10}{'ratio':>10}")
print("   " + "-" * 52)
window_costs = []
for n in (1_000, 10_000, 100_000):
    values = [rng.randint(0, 9) for _ in range(n)]
    slow = n * (n + 1) // 2
    _, fast = longest_window(values, 5 * n)
    window_costs.append((n, fast))
    print(f"   {n:>10,}{slow:>22,}{fast:>10,}{slow / fast:>9,.0f}x")

print()
print("The window moves a pointer forward at most n times on the way in and n")
print("times on the way out, so its cost is at most 2n steps and the ratio is")
print(f"at least n/2. The column above shows exactly {window_costs[0][1]:,} at n = "
      f"{window_costs[0][0]:,} rather than 2n,")
print("because k here is generous enough that the sum never exceeds it and")
print("the left pointer never moves at all. The bound is 2n; this input uses")
print("the easy half of it, and the ratio grows either way.")
print()
print("So there are two ways to be wrong here and they are not symmetric. Use")
print("the window on negative data and the answers are wrong. Use the naive")
print("version on non-negative data and the answers are right and the program")
print("is too slow. The first is worse, and the only defence is reading the")
print("statement for its assumptions and not just its size limit.")
print()
print("If the values really can be negative, the window is not the tool. The")
print("honest options are the quadratic version above, or a prefix-sum index")
print("that answers 'the earliest prefix at least this large' -- a segment or")
print("Fenwick tree over the prefix values, which is O(n log n) and is not")
print("written here. Naming it is the point: the O(n) answer is available")
print("only because of an assumption, and an assumption is a thing you check.")
```

```text
Start with the smallest input where the window is wrong, because a
counterexample beats an argument.

   values [4, -3, 2], k = 3
   every stretch, added up : 3
   sliding window          : 2

The answer is 3: the whole list sums to 3, which is within k. The
window reports 2, and here is why. It expands to include the 4, sees
the sum exceed k, and shrinks from the left -- discarding the 4. That
is the only move it has, and it is the wrong one, because the -3 that
follows would have brought the sum back under k. The window assumes
that once the sum is too large, dropping the leftmost element is the
only way to make it smaller. With a negative value still ahead, that
is false.

Now count how often it happens:

   values                    instances   window wrong
   --------------------------------------------------
   non-negative                  2,000              0
   mixed signs                   2,000            636

Nothing when the values are non-negative, and 636 of 2,000 when they
are not -- about a third of the inputs. The algorithm did not change
between those two rows and neither did the code. What changed is
whether the assumption it depends on holds, and nothing in the window
itself checks.

The cost is the reason the window is worth having at all. The naive
version adds up n(n+1)/2 stretches, fixed before the data arrives:

         n     additions      n(n+1)/2   agree
   -------------------------------------------
       100         5,050         5,050    True
       200        20,100        20,100    True
       400        80,200        80,200    True

And the two side by side, on non-negative data where both are right.

            n  add up every stretch    window     ratio
   ----------------------------------------------------
        1,000               500,500     1,000      500x
       10,000            50,005,000    10,000    5,000x
      100,000         5,000,050,000   100,000   50,000x

The window moves a pointer forward at most n times on the way in and n
times on the way out, so its cost is at most 2n steps and the ratio is
at least n/2. The column above shows exactly 1,000 at n = 1,000 rather than 2n,
because k here is generous enough that the sum never exceeds it and
the left pointer never moves at all. The bound is 2n; this input uses
the easy half of it, and the ratio grows either way.

So there are two ways to be wrong here and they are not symmetric. Use
the window on negative data and the answers are wrong. Use the naive
version on non-negative data and the answers are right and the program
is too slow. The first is worse, and the only defence is reading the
statement for its assumptions and not just its size limit.

If the values really can be negative, the window is not the tool. The
honest options are the quadratic version above, or a prefix-sum index
that answers 'the earliest prefix at least this large' -- a segment or
Fenwick tree over the prefix values, which is O(n log n) and is not
written here. Naming it is the point: the O(n) answer is available
only because of an assumption, and an assumption is a thing you check.
```

:::
