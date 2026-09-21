#!/usr/bin/env python3
"""Chapter 46 demo -- binary search, its two classic off-by-ones, and the
probe count that makes the whole thing worth getting right.

Both bugs below are written out and made to fail on a named input, because
'be careful with the boundary' is not advice anybody can act on.
"""
CAP = 60
SORTED = list(range(0, 200, 2))


def lower_bound(items, target):
    """The index of the first item that is >= target. This is the version
    that answers 'where does this belong', and it is the one to memorise."""
    low, high = 0, len(items)
    probes = 0
    while low < high:
        probes += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low, probes


def contains(items, target):
    """Membership. Note the different invariants: high starts at len-1, the
    loop runs while low <= high, and both bounds move past middle."""
    low, high = 0, len(items) - 1
    probes = 0
    while low <= high:
        probes += 1
        middle = (low + high) // 2
        if items[middle] == target:
            return True, probes
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return False, probes


def lower_bound_bug_low(items, target):
    """BUG 1: `low = middle` instead of `middle + 1`. When the target is above
    every item, low stops moving and the loop never terminates."""
    low, high = 0, len(items)
    probes = 0
    while low < high:
        probes += 1
        if probes > CAP:
            return None, probes
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle
        else:
            high = middle
    return low, probes


def lower_bound_bug_high(items, target):
    """BUG 2: `high = middle - 1` in a lower-bound search. It is correct for
    membership and wrong here, because the answer can be *at* middle."""
    low, high = 0, len(items)
    probes = 0
    while low < high:
        probes += 1
        middle = (low + high) // 2
        if items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return low, probes


print(f"a sorted list of {len(SORTED)} even numbers, 0 to {SORTED[-1]}")
print()
print(f"{'target':>8}{'lower_bound':>14}{'correct?':>10}{'probes':>9}"
      f"{'linear scan':>13}")
print("-" * 54)
for target in (0, 1, 100, 199, 200):
    index, probes = lower_bound(SORTED, target)
    expected = sum(1 for value in SORTED if value < target)
    scan = 0
    for value in SORTED:
        scan += 1
        if value >= target:
            break
    else:
        scan = len(SORTED)
    print(f"{target:>8}{index:>14}{str(index == expected):>10}{probes:>9}{scan:>13}")
print()
print("Every answer is the count of items below the target, and every one")
print("costs six or seven probes against a scan of up to a hundred. The odd")
print("targets are the interesting ones: 1 and 199 are not in the list at")
print("all, and lower_bound still answers 'where would it go' rather than")
print("failing.")
print()
print("That is the difference between a search and a *rank*. A search wants")
print("a yes or a no; a rank wants a position, and a position always exists.")
print()
print("Now the two bugs. Both are one character wrong.")
print()
print(f"{'case':<46}{'result':>10}")
print("-" * 56)
for target in (500, 2):
    _, probes = lower_bound_bug_low(SORTED, target)
    print(f"{'bug 1: low = middle, target ' + str(target):<46}{'hangs':>10}")
    print(f"{'  probes before the step cap stopped it':<46}{probes:>10}")
_, probes = lower_bound_bug_low(SORTED, 0)
print(f"{'bug 1: low = middle, target 0':<46}{'ok':>10}")
print(f"{'  the one target it survives':<46}{probes:>10}")
print()
correct, _ = lower_bound(SORTED, 100)
buggy, _ = lower_bound_bug_high(SORTED, 100)
print(f"{'bug 2: high = middle - 1, target 100':<46}{buggy:>10}")
print(f"{'  correct answer':<46}{correct:>10}")
buggy, _ = lower_bound_bug_high(SORTED, 0)
print(f"{'bug 2: high = middle - 1, target 0':<46}{buggy:>10}")
print(f"{'  correct answer':<46}{0:>10}")
print()
print("Bug 1 does not give a wrong answer, it gives *no* answer. With the")
print("target above the first item, low and middle converge on the same index")
print("and low stops advancing, so the loop spins until something else kills")
print("it. Only target 0 terminates, because the answer is 0 and low never")
print("has to move. A hang in production is worse than an exception: nothing")
print("in the logs says which line is at fault.")
print()
print("Bug 2 gives a wrong answer silently, off by one, and it is correct")
print("for target 0 and wrong for target 100 -- exactly the shape of bug that")
print("passes the two tests somebody wrote by hand.")
print()
print("Both come from the same mistake: treating the two bounds as if they")
print("were the same kind of thing. In a lower-bound search the invariant is")
print("that the answer lies in [low, high), and high is *exclusive* -- so it")
print("starts at len(items), never at len(items) - 1, and it is set to middle")
print("rather than middle - 1. In a membership search both bounds are")
print("inclusive and both move past middle. Pick one convention, write it")
print("down, and do not mix them.")
print()
print("The standard library has both, tested and in C:")
print()
print("  bisect.bisect_left(items, x)   first index where items[i] >= x")
print("  bisect.bisect_right(items, x)  first index where items[i] >  x")
print()
print("bisect_left is the lower bound above. bisect_right is the same search")
print("with `<=` instead of `<`, and it is the one that matters when the list")
print("has duplicates.")
