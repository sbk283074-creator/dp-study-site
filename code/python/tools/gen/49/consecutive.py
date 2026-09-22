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
