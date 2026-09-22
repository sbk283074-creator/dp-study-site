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
