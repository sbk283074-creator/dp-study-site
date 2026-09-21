#!/usr/bin/env python3
"""Chapter 45 demo -- a linked list, and the exact price of each operation.

Every number here is a count of Python-level steps, so it is exact and
identical on every machine. Nothing is timed.
"""
N = 5_000


class Node:
    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class LinkedList:
    """Singly linked. Prepend is O(1). Everything else is a walk, because
    a node knows where the next node is and nothing else."""

    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, value):
        """One new node, one pointer write. The old head is not touched."""
        self.head = Node(value, self.head)
        self.size += 1

    def get(self, index):
        """Walk from the head. Returns (value, hops) so the cost is visible."""
        if index < 0:
            index += self.size
        if not 0 <= index < self.size:
            raise IndexError(index)
        hops = 0
        node = self.head
        while index:
            node = node.next
            index -= 1
            hops += 1
        return node.value, hops

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def __len__(self):
        return self.size


linked = LinkedList()
for value in range(N):
    linked.push_front(value)

print(f"a linked list of {len(linked):,} nodes, built by push_front")
print()
print("reading one value")
print(f"{'index':>10}{'node hops':>12}")
print("-" * 22)
for index in (0, 1, N // 2, N - 1):
    _, hops = linked.get(index)
    print(f"{index:>10}{hops:>12,}")
print()
print("The hops column is the cost. Reading the head is free, reading the")
print("middle is n/2 steps, reading the tail is n steps. The array did all")
print("three in one multiply -- this is the trade, and it is not a bug.")
print()
print("where the new items go")
print()
print(f"{'operation':<26}{'elements moved':>16}")
print("-" * 42)
print(f"{'list.insert(0, x)':<26}{N:>16,}")
print(f"{'deque.appendleft(x)':<26}{0:>16,}")
print(f"{'LinkedList.push_front(x)':<26}{0:>16,}")
print()
print("One pointer write, whatever the length. That is the whole reason")
print("anyone writes a linked list: O(1) insertion at a position you")
print("already hold. Note the qualifier. push_front is cheap because the")
print("head is a field on the object you already have. Inserting after a")
print("node in the middle is also O(1) -- but *finding* that node is the")
print("n/2 walk from the table above, and that walk is not free.")
print()
print("Two costs people assume are free and are not:")
print()
print(f"  len(linked) via __len__ counter : 1 step (a stored field)")
print(f"  len(linked) by walking the chain: {N:,} steps")
print()
print("The counter is why every real linked list stores its size. If")
print("__len__ walked the chain, `if len(x) > 0` would be O(n) and")
print("everyone would write it anyway, because it reads like O(1).")
