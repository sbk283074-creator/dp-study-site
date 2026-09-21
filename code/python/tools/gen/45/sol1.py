#!/usr/bin/env python3
"""Chapter 45 solution 1 -- a stack that also reports its minimum in O(1)."""
import random


class MinStack:
    """The trick is a second stack that holds the minimum as it was *at each
    depth*. Each entry is only valid while the stack is that tall, which is
    exactly what a stack gives you for free."""

    def __init__(self):
        self._items = []
        self._minimums = []

    def push(self, value):
        self._items.append(value)
        self._minimums.append(
            value if not self._minimums else min(value, self._minimums[-1])
        )

    def pop(self):
        self._minimums.pop()
        return self._items.pop()

    def minimum(self):
        return self._minimums[-1]

    def __len__(self):
        return len(self._items)


def rescan_minimum(stack):
    """The obvious version: look at every item. This is what the second
    stack is buying you out of."""
    return min(stack)


rng = random.Random(0)
values = [rng.randrange(1_000) for _ in range(500)]

stack = MinStack()
pushed = []
agree = True
rescans = 0
for value in values:
    stack.push(value)
    pushed.append(value)
    if stack.minimum() != rescan_minimum(pushed):
        agree = False
        break
    rescans += len(pushed)

print(f"{len(values)} pushes, checking minimum() against a full rescan each time")
print()
print(f"  every minimum agreed with the rescan : {agree}")
print(f"  items rescanned to check them        : {rescans:,}")
print(f"  items the MinStack looked at         : {len(values):,}")
print()
print("The rescan column is O(n) per call and the MinStack column is O(1) per")
print("call, which is the entire point. The second stack costs one extra slot")
print("per push and makes `minimum()` a peek at the top.")
print()
print("Popping is where the design earns its keep. Removing an item does not")
print("invalidate the minimums below it, because each recorded minimum belongs")
print("to a depth rather than to a value. Pop the tall entry and the minimum")
print("of the shorter stack is still sitting underneath, correct and free.")
print()
print("This is the general pattern for 'keep an aggregate that must survive")
print("removal': store the aggregate per depth, per version, or per node, and")
print("let the structure's own ordering do the bookkeeping. The naive")
print("alternative -- recompute the aggregate after every removal -- is O(n)")
print("per operation and is the reason people reach for a tree when a stack")
print("would have done.")
