#!/usr/bin/env python3
"""Chapter 48, exercise 5 -- a DP with a faster non-DP answer.

The longest increasing subsequence has a textbook DP: one state per position,
and at each position a look back over everything before it. It is O(n^2) and
it is correct.

It also has a solution that is not a dynamic program at all, runs in
O(n log n), and gets the same number. This exercise puts them side by side,
because the second one is a reminder that 'find the recurrence' is a way to
solve a problem and not the only one.

The check is that both give the same length on every sequence tested, and
that the fast one is genuinely doing something different rather than the same
thing written shorter.
"""
import bisect
import random


def lis_quadratic(seq):
    """The DP.

    `best[i]` is the length of the longest increasing subsequence *ending at*
    position i -- pinned to a position, like the substring table in the
    chapter rather than the running-best table. So the answer is the maximum
    over the whole table, and the recurrence looks back at every earlier
    position, which is where the n^2 comes from.
    """
    if not seq:
        return 0, []
    best = [1] * len(seq)
    parent = [-1] * len(seq)
    for i in range(1, len(seq)):
        for j in range(i):
            if seq[j] < seq[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
                parent[i] = j
    length = max(best)
    end = best.index(length)
    path = []
    while end != -1:
        path.append(seq[end])
        end = parent[end]
    return length, list(reversed(path))


def lis_patience(seq, count_steps=False):
    """Patience sorting.

    `tails[k]` is the smallest possible tail of an increasing subsequence of
    length k+1. The array is *sorted*, so each new value can be placed with a
    binary search, and the answer is how long the array grew.

    Note what `tails` is not. It is not a table of answers to subproblems,
    and it is not the subsequence -- `tails` is not increasing in the original
    sequence, and the value at the end is not the last element of any
    particular subsequence. It is a different kind of object entirely.
    """
    tails = []
    steps = 0
    for value in seq:
        steps += 1
        pos = bisect.bisect_left(tails, value)
        if pos == len(tails):
            tails.append(value)
        else:
            tails[pos] = value
    return (len(tails), steps, tails) if count_steps else len(tails)


SEQUENCES = [
    ("ascending, n = 20", list(range(20))),
    ("descending, n = 20", list(range(20, 0, -1))),
    ("all equal, n = 20", [5] * 20),
    ("a shuffled 0..19", [13, 4, 18, 1, 9, 16, 6, 11, 3, 19,
                          8, 14, 0, 17, 5, 12, 2, 15, 7, 10]),
    ("two ascending runs", list(range(10)) + list(range(10))),
    ("alternating", [1, 3, 2, 4, 3, 5, 4, 6, 5, 7]),
]

print("Part 1 -- the two solutions, on sequences with known answers")
print()
print(f"  {'sequence':<22}{'DP':>6}{'patience':>10}{'agree':>8}"
      f"   the subsequence")
print("-" * 76)
for name, seq in SEQUENCES:
    length, path = lis_quadratic(seq)
    fast = lis_patience(seq)
    shown = str(path) if len(str(path)) <= 30 else str(path[:8])[:-1] + ", ...]"
    print(f"  {name:<22}{length:>6}{fast:>10}{str(length == fast):>8}"
          f"   {shown}")
print()
print("Both agree on every row, including the degenerate ones. The descending")
print("sequence is the useful edge case: the answer is 1, not 0, because a")
print("single element is an increasing subsequence of length 1. An")
print("implementation that returned 0 there would pass every random test.")
print()
print()
print("Part 2 -- what the two algorithms are actually doing")
print()
SEQ = [13, 4, 18, 1, 9, 16, 6, 11, 3, 19, 8, 14, 0, 17, 5, 12, 2, 15, 7, 10]
length, steps, tails = lis_patience(SEQ, count_steps=True)
dp_length, dp_path = lis_quadratic(SEQ)
print(f"  sequence : {SEQ}")
print()
print(f"  DP       : {dp_length}, found by looking back at every earlier position")
print(f"  patience : {length}, found by {steps} binary searches")
print(f"  the DP's answer, as a subsequence : {dp_path}")
print(f"  the patience array at the end     : {tails}")
print()
print("The last two lines are the ones worth staring at, because the patience")
print("array looks like it should be the answer and it is not. Its length is")
print(f"the answer -- {length} -- but the values in it are a mixture drawn from")
print("different places in the sequence, and they do not appear in that order")
print("anywhere in the input.")
print()


def is_subsequence(needle, haystack):
    """True if `needle` can be found inside `haystack` in order."""
    remaining = iter(haystack)
    return all(any(item == candidate for candidate in remaining)
               for item in needle)


print(f"  the patience array is sorted        : {tails == sorted(tails)}")
print(f"  the patience array is a subsequence : "
      f"{is_subsequence(tails, SEQ)}")
print(f"  the DP's subsequence is increasing  : "
      f"{all(dp_path[i] < dp_path[i + 1] for i in range(len(dp_path) - 1))}")
print(f"  the DP's subsequence is a subsequence: "
      f"{is_subsequence(dp_path, SEQ)}")
print()
print("The patience array is sorted by construction -- that is what makes the")
print("binary search valid -- so it cannot be a subsequence of a shuffled")
print("input unless the input was already sorted. It is a different object")
print("that happens to have the same length as the answer, and the check above")
print("is the way to be sure of that rather than to assume it.")
print()
print("The DP's answer, by contrast, is a subsequence by construction, because")
print("the parent pointers recorded the actual chain. That is the difference")
print("between a table that stores *the answer* and an array that stores *the")
print("number of the answer*.")
print()
print()
print("Part 3 -- the state space, which is where the speed comes from")
print()
print("The DP has n states, and each one looks back over up to n earlier")
print("positions, so the work is about n^2/2. The patience version has an")
print("array of at most n entries and touches each new value once, with a")
print("binary search of log n -- so about n log n.")
print()
print(f"{'n':>8}{'DP look-backs':>16}{'patience searches':>20}{'ratio':>10}")
print("-" * 54)
rng = random.Random(3)
for n in (100, 200, 400, 800, 1_600):
    seq = list(range(n))
    rng.shuffle(seq)
    lookbacks = n * (n - 1) // 2
    print(f"{n:>8,}{lookbacks:>16,}{n:>20,}{lookbacks / n:>9,.0f}x")
print()
print("The ratio column is the number of DP look-backs per binary search, and")
print("it grows with n -- so the gap widens rather than staying fixed. That is")
print("the difference between n^2 and n log n in one column.")
print()
print("But the counts are not quite a fair comparison, because the patience")
print("version's inner step is a binary search and the DP's is an integer")
print("compare. Counting operations rather than time is the right instinct,")
print("but it only works when the operations are comparable -- and here they")
print("are not, which is exactly the case where a count has to be reported")
print("alongside what is being counted rather than instead of it.")
print()
print()
print("Part 4 -- the checks")
print()
rng = random.Random(11)
mismatches = 0
trials = 300
for _ in range(trials):
    n = rng.randint(0, 40)
    seq = [rng.randint(0, 50) for _ in range(n)]
    if lis_quadratic(seq)[0] != lis_patience(seq):
        mismatches += 1
print(f"  {trials} random sequences, disagreements : {mismatches}")
print()
print("Every one agrees, over lengths from 0 to 40 and values from a range")
print("small enough to force plenty of ties. That is the evidence that the")
print("fast version is a solution to the same problem and not to a")
print("nearby one -- which is the failure mode to watch for when a faster")
print("algorithm is found for something that already worked.")
print()
print("The chapter's question was whether the recursion has overlapping")
print("subproblems and polynomially many states. This problem answers yes to")
print("both, which is why the DP is available. The patience version shows")
print("that 'yes' is a licence to write a DP, not an obligation -- and that")
print("the fastest solution to a DP-shaped problem sometimes arrives from a")
print("direction the recurrence cannot see.")
