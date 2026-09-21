#!/usr/bin/env python3
"""Chapter 47 solution 2 -- bidirectional BFS, the one search in this chapter
that improves the exponent rather than the constant.

Plain BFS from one end grows a ball of radius d, and on a graph that branches
b ways that ball holds roughly b^d nodes. Two balls of radius d/2 hold
roughly 2*b^(d/2) -- which is the *square root* of the one-ball count. The
saving is not a constant factor, it is a change in the exponent.

On a square grid that saving is nearly invisible, because both balls get
clipped by the edges of the square. This demo uses a graph that branches
instead, so the effect is the one being measured rather than an artefact of
the picture frame.
"""
import random
from collections import deque

N = 20_000
OUT_DEGREE = 3


def build(n, degree, seed):
    """A random graph with a fixed out-degree per node, so the mean degree is
    exactly 2*degree and every node is equally connected."""
    rng = random.Random(seed)
    adj = [[] for _ in range(n)]
    for u in range(n):
        for _ in range(degree):
            v = rng.randrange(n)
            if v != u:
                adj[u].append(v)
                adj[v].append(u)
    return adj


def bfs(adj, source, target):
    dist = {source: 0}
    queue = deque([source])
    expanded = 0
    while queue:
        u = queue.popleft()
        if u == target:
            return dist[u], expanded, len(dist)
        expanded += 1
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return None, expanded, len(dist)


def bidirectional(adj, source, target):
    """Expand whichever frontier is smaller, and stop the moment the two
    touch: the touching node has a known distance to each end, and the sum is
    the length of a shortest route."""
    if source == target:
        return 0, 0, 0
    dist_a = {source: 0}
    dist_b = {target: 0}
    frontier_a = deque([source])
    frontier_b = deque([target])
    expanded = 0
    while frontier_a and frontier_b:
        if len(frontier_a) <= len(frontier_b):
            frontier, own, other = frontier_a, dist_a, dist_b
        else:
            frontier, own, other = frontier_b, dist_b, dist_a
        for _ in range(len(frontier)):
            u = frontier.popleft()
            expanded += 1
            for v in adj[u]:
                if v in own:
                    continue
                own[v] = own[u] + 1
                if v in other:
                    return own[v] + other[v], expanded, len(own) + len(other)
                frontier.append(v)
    return None, expanded, len(dist_a) + len(dist_b)


ADJ = build(N, OUT_DEGREE, seed=17)
EDGES = sum(len(v) for v in ADJ) // 2

# A pair as far apart as the graph allows, found rather than assumed: BFS from
# node 0 and take whatever it reached last.
_, _, _ = 0, 0, 0
dist_from_0 = {0: 0}
queue = deque([0])
while queue:
    u = queue.popleft()
    for v in ADJ[u]:
        if v not in dist_from_0:
            dist_from_0[v] = dist_from_0[u] + 1
            queue.append(v)
FAR = max(dist_from_0, key=lambda node: dist_from_0[node])

one_way, one_exp, one_seen = bfs(ADJ, 0, FAR)
both_way, both_exp, both_seen = bidirectional(ADJ, 0, FAR)
print(f"a random graph: {N:,} nodes, {EDGES:,} edges, mean degree "
      f"{2 * EDGES / N:.1f}")
print(f"  reachable from node 0     : {len(dist_from_0):,}")
print(f"  farthest node from 0      : {FAR}, at distance {dist_from_0[FAR]}")
print()
print(f"{'search':<22}{'route':>7}{'expanded':>11}{'nodes seen':>13}")
print("-" * 53)
print(f"{'BFS from one end':<22}{one_way:>7}{one_exp:>11,}{one_seen:>13,}")
print(f"{'bidirectional BFS':<22}{both_way:>7}{both_exp:>11,}{both_seen:>13,}")
print()
print(f"  the two agree on the distance : {one_way == both_way}")
print(f"  nodes expanded                : {one_exp / both_exp:.1f}x fewer")
print(f"  nodes ever put in a dictionary: {one_seen / both_seen:.1f}x fewer")
print()
print("That is the square root, and the arithmetic is the whole explanation.")
print(f"The route is {one_way} steps long. BFS from one end grows a ball of radius")
print(f"{one_way}; two searches grow balls of radius {one_way / 2:.0f}. On a graph that")
print(f"branches about {2 * EDGES / N:.0f} ways, a ball of radius r holds roughly")
print(f"{2 * EDGES / N:.0f}^r nodes -- so halving r does not halve the work, it")
print("square-roots it.")
print()
print("This is why the technique is worth knowing even though it needs an")
print("extra frontier, an extra dictionary, and a stopping rule that has to be")
print("proved. On a graph with a large diameter and a small branching factor")
print("the saving is modest. On one that branches -- a state space, a puzzle,")
print("a word graph -- it is the difference between a search that finishes and")
print("one that does not.")
print()
print("The stopping rule is the part that has to be argued, because it is not")
print("obvious that the *first* touch is on a shortest route. Suppose the two")
print("frontiers meet at a node at distance a from the start and b from the")
print("goal. Every node still in the forward frontier is at distance at least")
print("a, and every node in the backward frontier at distance at least b -- so")
print("any route not yet found has length at least a + b, which is exactly the")
print("length of the route just found. Nothing shorter is hiding.")
print()
print("That argument needs the graph to be unweighted, or at least symmetric.")
print("On a weighted graph the two searches grow at different rates -- five")
print("units from one side is not comparable to five units from the other --")
print("and the meeting test stops being a proof. Bidirectional Dijkstra exists,")
print("and its stopping condition is *not* 'the frontiers touched'.")
print()
print(f"  route length {one_way} on a graph of diameter {dist_from_0[FAR]}")
print("  (the same demo on a square grid shows almost no saving, because the")
print("   frame clips both balls -- which is why this one uses a graph)")
