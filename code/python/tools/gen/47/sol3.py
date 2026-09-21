#!/usr/bin/env python3
"""Chapter 47 solution 3 -- Kruskal's minimum spanning tree, which is a sort
and a union-find and nothing else.

The problem: connect n points as cheaply as possible. The algorithm: sort
every candidate edge by weight, then walk them cheapest first, keeping an edge
unless its two ends are already connected. "Already connected" is one
union-find query, which is why the structure from earlier in the chapter is
the entire engine and the sort is the only other moving part.
"""
import heapq
import random


class UnionFind:
    __slots__ = ("parent", "rank")

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


TOWNS = 30
rng = random.Random(3)
POINTS = [(rng.randrange(100), rng.randrange(100)) for _ in range(TOWNS)]


def distance(a, b):
    dx = POINTS[a][0] - POINTS[b][0]
    dy = POINTS[a][1] - POINTS[b][1]
    return round((dx * dx + dy * dy) ** 0.5)


CANDIDATES = [(distance(a, b), a, b)
              for a in range(TOWNS) for b in range(a + 1, TOWNS)]
ADJ = {i: [] for i in range(TOWNS)}
for w, a, b in CANDIDATES:
    ADJ[a].append((b, w))
    ADJ[b].append((a, w))


def kruskal(n, candidates):
    """Sort, then take the cheapest edge that does not close a loop."""
    uf = UnionFind(n)
    chosen = []
    total = 0
    examined = 0
    rejected = 0
    for w, a, b in sorted(candidates):
        examined += 1
        if uf.union(a, b):
            chosen.append((a, b, w))
            total += w
        else:
            rejected += 1
        if len(chosen) == n - 1:
            break
    return chosen, total, examined, rejected


def prim(n, adj):
    """Grow one tree outwards, always taking the cheapest edge that leaves it."""
    in_tree = [False] * n
    in_tree[0] = True
    heap = [(w, 0, v) for v, w in adj[0]]
    heapq.heapify(heap)
    total = 0
    count = 0
    pushes = len(heap)
    while heap and count < n - 1:
        w, a, b = heapq.heappop(heap)
        if in_tree[b]:
            continue
        in_tree[b] = True
        total += w
        count += 1
        for v, wv in adj[b]:
            if not in_tree[v]:
                heapq.heappush(heap, (wv, b, v))
                pushes += 1
    return total, pushes


chosen, total, examined, rejected = kruskal(TOWNS, CANDIDATES)
prim_total, prim_pushes = prim(TOWNS, ADJ)
EDGES = len(CANDIDATES)

print(f"{TOWNS} towns scattered in a 100x100 square")
print(f"  candidate edges      : {EDGES:,} (every pair)")
print(f"  edges in the tree    : {len(chosen)} (always n - 1)")
print()
print(f"{'algorithm':<12}{'total length':>14}{'edges examined':>16}"
      f"{'work':>16}")
print("-" * 58)
print(f"{'Kruskal':<12}{total:>14,}{examined:>16,}{'1 sort + ' + str(examined) + ' finds':>16}")
print(f"{'Prim':<12}{prim_total:>14,}{'':>16}{str(prim_pushes) + ' heap pushes':>16}")
print()
print(f"  the two agree on the total length : {total == prim_total}")
print(f"  edges Kruskal rejected as loops   : {rejected}")
print()
print("Both produce a minimum spanning tree and both are correct; they are")
print("different because they make the same greedy choice in different")
print("orders. Kruskal considers edges globally, cheapest first, and asks 'do")
print("these two ends already belong to the same piece?'. Prim considers one")
print("growing tree and asks 'what is the cheapest way out of it?'.")
print()
print("The rejected count is the part that needs union-find. The n-1 edges")
print("that make the tree are the cheap ones; every other edge was considered")
print("and discarded because its two ends were already joined. Without a fast")
print("'already joined' test, Kruskal is a sort followed by a search through")
print("the chosen edges -- which is O(E log E) becoming O(E*V).")
print()
print("Why the greedy choice is safe is the interesting part, and it is the")
print("cut property: for any way of splitting the towns into two groups, the")
print("cheapest edge crossing that split is in *some* minimum spanning tree.")
print("Kruskal's first accepted edge is the cheapest edge overall, which")
print("crosses every split that separates its two ends, so it is safe. The")
print("same argument then applies to the remaining graph.")
print()
print()
print("The tree itself")
print()
by_weight = sorted(chosen, key=lambda e: -e[2])
print(f"  {'edge':>10}{'length':>9}   {'edge':>10}{'length':>9}")
print("  " + "-" * 40)
half = (len(by_weight) + 1) // 2
for i in range(half):
    left = by_weight[i]
    right = by_weight[i + half] if i + half < len(by_weight) else None
    left_text = f"{left[0]:>4} - {left[1]:<4}{left[2]:>9}"
    right_text = (f"{right[0]:>4} - {right[1]:<4}{right[2]:>9}"
                  if right else "")
    print(f"  {left_text}   {right_text}")
print()
print(f"  longest edge in the tree : {by_weight[0][2]}")
print(f"  shortest edge in the tree: {by_weight[-1][2]}")
print(f"  mean edge length         : {total / len(chosen):.1f}")
print()
print("The longest edge is the one to look at, because it is the answer to a")
print("question people actually ask: 'if I connect these towns as cheaply as")
print("possible, what is the worst connection I still have to pay for?' That")
print("is a minimax problem, and the minimum spanning tree solves it -- the")
print("longest edge in the MST is the smallest possible value for the largest")
print("edge in any connected network over these points.")
print()
print(f"  all {TOWNS} towns reachable through the tree: "
      f"{len(chosen) == TOWNS - 1}")
