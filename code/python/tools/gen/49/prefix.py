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
