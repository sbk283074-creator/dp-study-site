#!/usr/bin/env python3
"""Chapter 45 demo -- what deque gives up to be O(1) at both ends.

The first table is counted rather than timed. CPython's deque is a doubly
linked list of fixed-size blocks, so reaching slot i means walking blocks
from whichever end is nearer -- and that walk can be counted exactly.
"""
from collections import deque

N = 100_000
BLOCK = 64          # CPython's deque block size, in pointers


def hops_to_reach(index):
    """Blocks the interpreter steps through to reach slot i.

    CPython indexes a deque from whichever end is nearer, so the cost is the
    distance to that end divided by the block size. The result is
    arithmetic: it is the same on every machine, and no clock appears.
    """
    if index < 0:
        index += N
    from_left = index // BLOCK
    from_right = (N - 1 - index) // BLOCK
    return min(from_left, from_right)


print("reaching one slot of a deque, by position")
print(f"  {N:,} items, {BLOCK} pointers per block")
print()
print(f"{'position':<18}{'index':>10}{'block hops':>13}")
print("-" * 41)
print(f"{'left end':<18}{0:>10}{hops_to_reach(0):>13,}")
for label, index in (("right end", -1),
                     ("near the right", N - 10),
                     ("a quarter in", N // 4),
                     ("middle", N // 2)):
    print(f"{label:<18}{index:>10}{hops_to_reach(index):>13,}")
print()
print("A deque is not a list with extra methods. It is a doubly linked list")
print("of fixed-size blocks, and that layout is why the two ends are cheap")
print("and the middle is not: reaching the middle of this deque means")
print(f"stepping through {hops_to_reach(N // 2):,} blocks, while reaching either end means stepping")
print("through none. CPython walks from whichever end is nearer, so both")
print("ends and both ends' neighbours are free and the centre is the worst")
print("case.")
print()
print("So `deque` is not a drop-in list replacement. Swap a list for a deque")
print("because you push and pop at the ends, not because it sounds faster.")
print("If your code does `items[i]` in a loop, a deque makes it worse.")
print()
print("What you get for that trade is a ring buffer, and a ring buffer has")
print("a feature a list cannot imitate: a fixed maximum length.")
print()
WINDOW = 5
rolling = deque(maxlen=WINDOW)
print(f"a deque(maxlen={WINDOW}) fed the numbers 1 to 9")
print()
print(f"{'input':>7}   contents")
print("-" * 30)
for value in range(1, 10):
    rolling.append(value)
    print(f"{value:>7}   {list(rolling)}")
print()
print("No eviction code. The deque drops the item at the other end when it")
print("is full, in O(1), and the buffer never grows. The list version of")
print("this is `buf.append(x); del buf[:-5]`, which is correct and which")
print("everyone eventually forgets to write -- at which point the buffer is")
print("unbounded and the memory leak is invisible until it is not.")
print()
print("rotate() is the other one worth knowing. It moves the seam rather")
print("than the data, so rotating by k costs k steps, not n:")
print()
ring = deque("abcdef")
print(f"  starting from  {list(ring)}")
ring.rotate(2)
print(f"  rotate(2)      {list(ring)}")
ring.rotate(-2)
print(f"  rotate(-2)     {list(ring)}")
print()
print("That is how you implement a round-robin scheduler without an index")
print("that has to be taken modulo everywhere it is used.")
