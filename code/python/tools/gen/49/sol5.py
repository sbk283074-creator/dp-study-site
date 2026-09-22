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
