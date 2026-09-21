#!/usr/bin/env python3
"""Chapter 45 solution 3 -- an LRU cache, which needs two structures at once."""


class Node:
    """A doubly linked node, because eviction has to unlink from the middle
    of the recency order and a singly linked node cannot do that."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """A dict for the lookup, a doubly linked list for the order. Neither one
    alone can do both jobs: the dict cannot tell you the oldest key without
    scanning, and the list cannot find a key without walking."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.index = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.lookups = 0
        self.relinks = 0

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self.relinks += 2

    def _push_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.relinks += 4

    def get(self, key):
        self.lookups += 1
        node = self.index.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key, value):
        self.lookups += 1
        node = self.index.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return None
        if len(self.index) >= self.capacity:
            oldest = self.tail.prev
            self._unlink(oldest)
            del self.index[oldest.key]
        node = Node(key, value)
        self.index[key] = node
        self._push_front(node)
        return None

    def order(self):
        """Most recently used first, for the tests to read."""
        out = []
        node = self.head.next
        while node is not self.tail:
            out.append(node.key)
            node = node.next
        return out


cache = LRUCache(capacity=3)
SCRIPT = [
    ("put", "a", 1),
    ("put", "b", 2),
    ("put", "c", 3),
    ("get", "a", None),
    ("put", "d", 4),
    ("get", "b", None),
    ("get", "a", None),
    ("put", "e", 5),
]

print("a cache of 3, given this sequence")
print()
print(f"{'operation':<16}{'result':>10}   keys, most recent first")
print("-" * 56)
for action, key, value in SCRIPT:
    if action == "put":
        cache.put(key, value)
        shown = f"put {key}={value}"
        result = "-"
    else:
        found = cache.get(key)
        shown = f"get {key}"
        result = "None" if found is None else str(found)
    print(f"{shown:<16}{result:>10}   {cache.order()}")
print()
print(f"dict lookups: {cache.lookups}   pointer rewires: {cache.relinks}")
print()
print("Every operation is O(1) and the counters show why. `get` is one dict")
print("lookup to find the node, then four pointer writes to move it to the")
print("front. Eviction is one dict delete and two pointer writes, because")
print("`tail.prev` is the least recently used node -- no scan, no timestamp")
print("comparison, no sorting.")
print()
print("The doubly linked part is not decoration. Unlinking a node needs")
print("`node.prev`, and a singly linked list has no way to reach it. That is")
print("the whole reason this structure is doubly linked: the access pattern")
print("is 'remove from the middle, insert at the front', and only a doubly")
print("linked list does both in constant time.")
print()
print("Chapter 18 used `functools.lru_cache`, which does exactly this in C.")
print("You do not need to write it. You need to know that a cache with a")
print("size limit is two structures holding the same objects for two")
print("different questions, because that shape recurs everywhere: an index")
print("and a journal, a lookup table and an ordering, a dict and a heap.")
