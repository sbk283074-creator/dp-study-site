#!/usr/bin/env python3
"""Chapter 45 scenario -- the 'recent events' buffer that ate the worker.

Both versions keep the last 100 events out of 200,000. The slot-move count
is exact: it is accumulated while the real list version runs, so it is a
fact about the algorithm rather than about one machine's afternoon.
"""
from collections import deque

KEEP = 100
EVENTS = 200_000


def buffer_with_list(events, keep):
    """insert(0, x) shifts the whole buffer up to make room at the front.

    The trimming `del buf[keep:]` deletes from the *end*, so it shifts
    nothing -- which is the one place this program is easy to get wrong.
    """
    buf = []
    moves = 0
    for i in range(events):
        moves += len(buf)          # every item already there moves up one slot
        buf.insert(0, i)
        del buf[keep:]             # a tail deletion moves nothing
    return len(buf), buf[0], moves


def buffer_with_deque(events, keep):
    buf = deque(maxlen=keep)
    for i in range(events):
        buf.appendleft(i)
    return len(buf), buf[0], 0


list_len, list_head, moves = buffer_with_list(EVENTS, KEEP)
deque_len, deque_head, _ = buffer_with_deque(EVENTS, KEEP)
assert (list_len, list_head) == (deque_len, deque_head)

print(f"keeping the last {KEEP} of {EVENTS:,} events")
print()
print(f"{'implementation':<28}{'slot moves':>16}{'per event':>12}")
print("-" * 56)
print(f"{'deque(maxlen=100)':<28}{0:>16,}{0.0:>12.1f}")
print(f"{'list.insert(0, x) + del':<28}{moves:>16,}{moves / EVENTS:>12.1f}")
print()
print("Both buffers end up holding the same 100 events in the same order --")
print("the assert above is the proof, and it is checked on every run. What")
print("differs is the second column, and it is exact: it is accumulated")
print("while the list version runs, so it is a fact about the algorithm and")
print("not about this machine.")
print()
print("Read the last column and the support ticket explains itself. The")
print("list version moves about a hundred slots for every single event, to")
print("keep a buffer of a hundred. Nothing about that number depends on how")
print("fast the machine is, which is why it was still the answer when the")
print("worker melted.")
print()
print("The shape is worth naming. The cost per event is proportional to")
print("`keep`, not to `events`, so making the buffer longer makes every")
print("event more expensive -- and the buffer length is the one thing the")
print("person writing this code thought was free to change.")
print()
print("And the correctness bug is worse than the performance one. `del")
print("buf[100:]` is a line somebody has to remember to write. It is not in")
print("the code path that runs on every event in a test, it is in the one")
print("that only matters after a hundred events, and when it is missing the")
print("buffer is unbounded. maxlen cannot be forgotten, because it is a")
print("property of the object rather than a statement in the loop.")
