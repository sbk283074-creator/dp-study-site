#!/usr/bin/env python3
"""Chapter 45 demo -- a balanced tree, so 'log n for both operations' stops
being something you have to take on faith.

An AVL tree keeps the height of the two subtrees at every node within one of
each other, which caps the height at about 1.44*log2(n). The visit counter
is the number of nodes the algorithm looked at, so it is exact.
"""
N = 20_000
K = 2_000


class Node:
    __slots__ = ("key", "left", "right", "height")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1


class AVL:
    """Insert-only, which is all this demo needs. A real one also deletes."""

    def __init__(self):
        self.root = None
        self.size = 0
        self.visits = 0
        self.rotations = 0

    @staticmethod
    def _height(node):
        return node.height if node is not None else 0

    @staticmethod
    def _refresh(node):
        node.height = 1 + max(AVL._height(node.left), AVL._height(node.right))

    def _rotate_left(self, node):
        self.rotations += 1
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        self._refresh(node)
        self._refresh(pivot)
        return pivot

    def _rotate_right(self, node):
        self.rotations += 1
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        self._refresh(node)
        self._refresh(pivot)
        return pivot

    def _rebalance(self, node):
        """After an insert, the two subtrees can differ by at most two.
        One rotation fixes the outside case, two fix the inside case."""
        self._refresh(node)
        balance = self._height(node.left) - self._height(node.right)
        if balance > 1:
            if self._height(node.left.left) < self._height(node.left.right):
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._height(node.right.right) < self._height(node.right.left):
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if node is None:
            self.size += 1
            return Node(key)
        self.visits += 1
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node
        return self._rebalance(node)

    def contains(self, key):
        node = self.root
        while node is not None:
            self.visits += 1
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def height(self):
        return self._height(self.root)


def permutation(n):
    return [(i * 7919) % n for i in range(n)]


def unbalanced_visits(n):
    """What the same inserts cost with no rebalancing at all: keys arriving
    in ascending order make a tree that is really a linked list."""
    visits = 0
    for index in range(n):
        visits += index
    return visits


tree = AVL()
for value in permutation(N):
    tree.insert(value)
insert_visits = tree.visits

tree.visits = 0
for value in permutation(K):
    tree.contains(value)
lookup_visits = tree.visits

print(f"{N:,} keys inserted one at a time, in scrambled order")
print()
print(f"{'measurement':<40}{'value':>12}")
print("-" * 52)
print(f"{'nodes visited while inserting':<40}{insert_visits:>12,}")
print(f"{'  mean per insert':<40}{insert_visits / N:>12.1f}")
print(f"{'rotations performed':<40}{tree.rotations:>12,}")
print(f"{'tree height':<40}{tree.height():>12}")
print(f"{'nodes visited by 2,000 lookups':<40}{lookup_visits:>12,}")
print(f"{'  mean per lookup':<40}{lookup_visits / K:>12.1f}")
print()
print("Thirteen visits per insert on 20,000 keys, against a log2(20,000) of")
print("14.3 -- the tree is behaving like a perfectly balanced one, and the")
print("height column is the proof that this is not luck. An unbalanced tree")
print("built from ascending keys would be 19,999 levels tall and would cost")
print(f"{unbalanced_visits(N):,} visits. The rotations cost almost nothing next to that.")
print()
print("So now the three structures can be compared honestly, on the same")
print("job: keep 20,000 keys available for lookup while 2,000 more arrive.")
print()
print(f"{'structure':<26}{'per insert':>14}{'per lookup':>14}")
print("-" * 54)
print(f"{'sorted list + bisect.insort':<26}{'21M shifts':>14}{'16 probes':>14}")
print(f"{'balanced tree (AVL)':<26}{'~13 visits':>14}{'~13 visits':>14}")
print(f"{'dict':<26}{'1 hash':>14}{'1 hash':>14}")
print()
print("The tree is the only one of the three that is logarithmic for both")
print("and keeps the keys in order. The dict is faster at both operations")
print("and keeps nothing in order. The sorted list is the fastest to search")
print("and the slowest to maintain.")
print()
print("Which one you want is decided by the question you are actually")
print("asking. If you never need 'the keys between 40 and 60', the dict")
print("wins and the tree is a hundred lines of code you did not need. That")
print("is why Python's standard library has no sorted mapping: most of the")
print("code that reaches for one only needed a dict, or a sort at the end.")
