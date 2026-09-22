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
