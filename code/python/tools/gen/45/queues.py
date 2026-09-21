#!/usr/bin/env python3
"""Chapter 45 demo -- three ways to dequeue, and what each one moves."""
import timeit
from collections import deque

SMALL = 2_000
LARGE = 4_000
ROUNDS = 7


def shifts(n):
    """pop(0) removes slot 0 and shifts every remaining element down one.
    The total over a full drain is a property of the algorithm, not of the
    machine:  (n-1) + (n-2) + ... + 0  =  n(n-1)/2."""
    return n * (n - 1) // 2


def drain_pop0(n):
    q = list(range(n))
    while q:
        q.pop(0)
    return len(q)


def drain_head(n):
    """Keep a head index. Nothing ever moves -- but the abandoned prefix
    stays allocated, so the memory cost is the same and never comes back."""
    q = list(range(n))
    head = 0
    end = len(q)
    while head < end:
        head += 1
    return head


def drain_deque(n):
    q = deque(range(n))
    while q:
        q.popleft()
    return len(q)


def time_one(fn, n):
    return min(timeit.repeat(lambda: fn(n), number=1, repeat=ROUNDS))


def shape(ratio):
    if ratio < 3.0:
        return "~2x  (linear)"
    return "~4x  (quadratic)"


shapes = []
for fn in (drain_pop0, drain_head, drain_deque):
    shapes.append(shape(time_one(fn, LARGE) / time_one(fn, SMALL)))

print(f"queueing and dequeuing {SMALL:,} items, then {LARGE:,} items")
print()
print(f"{'implementation':<20}{'element shifts':>16}  {'doubling n':>16}")
print("-" * 54)
print(f"{'list.pop(0)':<20}{shifts(SMALL):>16,}  {shapes[0]:>16}")
print(f"{'list + head index':<20}{0:>16,}  {shapes[1]:>16}")
print(f"{'collections.deque':<20}{0:>16,}  {shapes[2]:>16}")
print()
print("The two right-hand columns answer different questions. The shift")
print("count is exact and follows from the algorithm; the doubling column")
print("is this machine on this run, so it is reported as a band.")
print()
print("Read them together and the choice stops being a matter of taste.")
print("drain_pop0 does n(n-1)/2 shifts -- for a million-item queue that is")
print("499,999,500,000 of them -- and its cost quadruples when n doubles.")
print("The other two do no shifting at all and merely double.")
print()
print("The head-index version is not a fix, it is a deferral: the list")
print("still holds every slot it ever allocated, so a long-running service")
print("grows without bound while its queue looks empty. deque is the fix.")
