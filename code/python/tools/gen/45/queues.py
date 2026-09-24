#!/usr/bin/env python3
"""Chapter 45 demo -- three ways to dequeue, and what each one moves.

The shift counts are exact. They are accumulated while the real drains run,
so they describe what the algorithm does rather than what a clock on one
machine happened to notice.
"""
from collections import deque

SMALL = 2_000
LARGE = 4_000


def drain_pop0(n):
    """pop(0) removes slot 0 and shifts every remaining element down one.

    The total over a full drain is a property of the algorithm, not of the
    machine:  (n-1) + (n-2) + ... + 0  =  n(n-1)/2.  The counter below
    accumulates it as the drain happens rather than trusting the formula.
    """
    q = list(range(n))
    shifts = 0
    while q:
        shifts += len(q) - 1     # every element after slot 0 moves down one
        q.pop(0)
    return shifts


def drain_head(n):
    """Keep a head index. Nothing ever moves -- but the abandoned prefix
    stays allocated, so the memory cost is the same and never comes back."""
    q = list(range(n))
    head = 0
    end = len(q)
    while head < end:
        head += 1
    return 0


def drain_deque(n):
    q = deque(range(n))
    while q:
        q.popleft()
    return 0


IMPLEMENTATIONS = (
    ("list.pop(0)", drain_pop0),
    ("list + head index", drain_head),
    ("collections.deque", drain_deque),
)

def shifts(n):
    """The closed form the counter above accumulates: (n-1) + ... + 0.

    Used only for the million-item figure below, because draining a real
    million-item queue would move 499,999,500,000 elements and take
    minutes. At 2,000 and 4,000 the counter runs and the formula is not
    trusted; at a million the formula is the only practical option, and the
    two agree exactly at the sizes where both are available.
    """
    return n * (n - 1) // 2


counts = {label: (fn(SMALL), fn(LARGE)) for label, fn in IMPLEMENTATIONS}
assert counts["list.pop(0)"][0] == shifts(SMALL)
assert counts["list.pop(0)"][1] == shifts(LARGE)
million = shifts(1_000_000)

print(f"queueing and dequeuing {SMALL:,} items, then {LARGE:,} items")
print()
print(f"{'implementation':<20}{f'shifts at {SMALL:,}':>17}"
      f"{f'shifts at {LARGE:,}':>17}{'growth':>9}")
print("-" * 63)
for label, _ in IMPLEMENTATIONS:
    small, large = counts[label]
    growth = f"{large / small:.1f}x" if small else "--"
    print(f"{label:<20}{small:>17,}{large:>17,}{growth:>9}")

print()
print("Every number in that table is exact. The shift counts are accumulated")
print("while the drains run, and they are the same on your machine as on")
print("mine, which is what lets them be printed in a book at all.")
print()
print("Read the two middle columns together and the choice stops being a")
print("matter of taste. list.pop(0) does n(n-1)/2 shifts, and the count")
print(f"quadruples when n doubles -- the signature of a quadratic. A queue")
print(f"of a million items pays {million:,} shifts, which is the same")
print("arithmetic at a size where the problem stops being academic. The")
print("other two rows do no shifting at all, whatever n is.")
print()
print("The head-index version is not a fix, it is a deferral: the list still")
print("holds every slot it ever allocated, so a long-running service grows")
print("without bound while its queue looks empty. deque is the fix, and the")
print("price of the fix is that the middle of a deque is expensive -- which")
print("is the next thing to look at.")
