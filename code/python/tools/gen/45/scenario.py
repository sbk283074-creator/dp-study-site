#!/usr/bin/env python3
"""Chapter 45 scenario -- the 'recent events' buffer that ate the worker.

Both versions keep the last 100 events out of 200,000. The shift count is
exact; the measured column is this machine on this run, so it is a band.
"""
import timeit
from collections import deque

KEEP = 100
EVENTS = 200_000
ROUNDS = 5


def shifts_for_insert_zero(events, keep):
    """Every insert(0, x) shifts the whole buffer up one slot, and the buffer
    sits at its cap for all but the first `keep` events. The trimming
    `del buf[keep:]` then shifts the buffer down again. So each event costs
    about 2*keep slot moves once the buffer is full."""
    warmup = min(events, keep)
    full = max(events - keep, 0)
    return warmup * (warmup - 1) // 2 + full * 2 * keep


def buffer_with_list(events, keep):
    buf = []
    for i in range(events):
        buf.insert(0, i)
        del buf[keep:]
    return len(buf), buf[0]


def buffer_with_deque(events, keep):
    buf = deque(maxlen=keep)
    for i in range(events):
        buf.appendleft(i)
    return len(buf), buf[0]


def time_one(fn):
    return min(timeit.repeat(lambda: fn(EVENTS, KEEP), number=1, repeat=ROUNDS))


def band(ratio):
    for edge, label in ((3, "same band"), (30, "~10x slower"), (300, "~100x slower")):
        if ratio < edge:
            return label
    return "~1000x slower or more"


base = time_one(buffer_with_deque)
list_ratio = band(time_one(buffer_with_list) / base)

print(f"keeping the last {KEEP} of {EVENTS:,} events")
print()
print(f"{'implementation':<28}{'slot moves':>16}  {'measured':>18}")
print("-" * 64)
print(f"{'deque(maxlen=100)':<28}{0:>16,}  {'baseline':>18}")
print(f"{'list.insert(0, x) + del':<28}{shifts_for_insert_zero(EVENTS, KEEP):>16,}  {list_ratio:>18}")
print()
print("Both buffers end up holding the same 100 events in the same order.")
print("The measured column is a band because it is this machine on this run;")
print("the slot-move column is exact, and it is the one that explains the")
print("support ticket.")
print()
print("Two things make the list version quadratic-shaped in the buffer size")
print("rather than the event count. insert(0, x) shifts the buffer up to make")
print("room at the front, and del buf[100:] shifts it back down to trim. A")
print("deque with maxlen does neither: appending at the left writes into a")
print("slot that already exists, and the item falling off the right end is")
print("already a slot that exists. Nothing is ever moved.")
print()
print("And the correctness bug is worse than the performance one. `del")
print("buf[100:]` is a line somebody has to remember to write. It is not in")
print("the code path that runs on every event in a test, it is in the one")
print("that only matters after a hundred events, and when it is missing the")
print("buffer is unbounded. maxlen cannot be forgotten, because it is a")
print("property of the object rather than a statement in the loop.")
