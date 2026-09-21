#!/usr/bin/env python3
"""Chapter 47 demo -- the fewest steps and the cheapest route are different
questions.

BFS minimises the number of *edges*. Dijkstra minimises the sum of the
*weights*. On an unweighted graph those are the same question -- which is
exactly why BFS is a special case of Dijkstra -- and on a weighted graph they
are not, which is why reaching for BFS on a road network produces a
confident, plausible, wrong answer.
"""
import heapq
import random
from collections import deque

ROADS = {
    "A": [("B", 1), ("C", 4)],
    "B": [("A", 1), ("C", 1), ("D", 5)],
    "C": [("A", 4), ("B", 1), ("D", 1)],
    "D": [("B", 5), ("C", 1)],
}


def bfs_route(adj, source, target):
    parent = {source: None}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        if u == target:
            break
        for v, _ in adj[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
    return rebuild(parent, target)


def dijkstra_route(adj, source, target):
    dist = {source: 0}
    parent = {source: None}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue
        for v, w in adj[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(heap, (d + w, v))
    return rebuild(parent, target)


def rebuild(parent, target):
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def cost(adj, path):
    """Walk the route and add up the weights."""
    lookup = {u: dict(edges) for u, edges in adj.items()}
    return sum(lookup[path[i]][path[i + 1]] for i in range(len(path) - 1))


print("Part 1 -- four towns, one edge that changes everything")
print()
for node, edges in ROADS.items():
    print(f"    {node:<3} {', '.join(f'{v}:{w}' for v, w in edges)}")
print()
hops = bfs_route(ROADS, "A", "D")
cheap = dijkstra_route(ROADS, "A", "D")
print(f"  fewest edges (BFS)     : {' -> '.join(hops)}"
      f"   {len(hops) - 1} edges, weight {cost(ROADS, hops)}")
print(f"  cheapest (Dijkstra)    : {' -> '.join(cheap)}"
      f"   {len(cheap) - 1} edges, weight {cost(ROADS, cheap)}")
print()
print("BFS is not confused. It was asked for the route with the fewest edges")
print("and it returned the route with the fewest edges. The mistake is in the")
print("question: on a road network nobody wants fewer roads, they want fewer")
print("miles. A and C are joined by one edge of weight 4, and by two edges of")
print("weight 1 each -- so the answer that looks worse is twice as good.")
print()
print("The general statement is that BFS is Dijkstra with every weight set to")
print("1. That is why the two algorithms are the same shape and why only one")
print("of them is correct on a weighted graph.")
print()
print()
print("Part 2 -- what that costs on a real road network")
print()
GRID = 40


def weighted_grid(size, seed):
    rng = random.Random(seed)
    adj = {r * size + c: [] for r in range(size) for c in range(size)}
    for r in range(size):
        for c in range(size):
            u = r * size + c
            for dr, dc in ((1, 0), (0, 1)):
                nr, nc = r + dr, c + dc
                if nr < size and nc < size:
                    v = nr * size + nc
                    w = rng.randint(1, 9)
                    adj[u].append((v, w))
                    adj[v].append((u, w))
    return adj


ADJ = weighted_grid(GRID, seed=5)
START = 0


def bfs_tree(adj, source):
    parent = {source: None}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v, _ in adj[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
    return parent


def dijkstra_tree(adj, source):
    dist = {source: 0}
    parent = {source: None}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue
        for v, w in adj[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(heap, (d + w, v))
    return dist, parent


def route_cost(parent, target):
    """The actual weight of the route BFS chose."""
    total = 0
    node = target
    while parent[node] is not None:
        prev = parent[node]
        total += next(w for v, w in ADJ[prev] if v == node)
        node = prev
    return total


bfs_parent = bfs_tree(ADJ, START)
dist, dij_parent = dijkstra_tree(ADJ, START)
worse = 0
total_penalty = 0
worst = (0, None)
for node in ADJ:
    bfs_cost = route_cost(bfs_parent, node)
    if bfs_cost > dist[node]:
        worse += 1
        total_penalty += bfs_cost - dist[node]
        if bfs_cost - dist[node] > worst[0]:
            worst = (bfs_cost - dist[node], node)
print(f"a {GRID}x{GRID} grid, {len(ADJ):,} nodes, weights 1..9, all from one corner")
print()
print(f"  nodes where the BFS route costs more than the cheapest: {worse:,}"
      f" of {len(ADJ):,} ({worse / len(ADJ) * 100:.1f}%)")
print(f"  total excess weight across all routes  : {total_penalty:,}")
print(f"  mean excess per affected node          : {total_penalty / worse:.1f}")
print(f"  worst single node                      : +{worst[0]} "
      f"(node {worst[1]})")
print()
print(f"{worse / len(ADJ) * 100:.0f} percent of the nodes are reached by a route that is")
print("longer than it needs to be, and the excess is not a rounding error --")
print("the worst node is reached by a route several times more expensive than")
print("the cheapest one. And notice what BFS did *not* do: it never raised,")
print("never warned, and produced a route that is genuinely the")
print("fewest-edges route. There is no signal anywhere in the output that the")
print("answer is wrong.")
print()
print("That is the failure mode to remember. A wrong shortest path looks")
print("exactly like a right one -- it is a list of nodes, it starts at the")
print("source and ends at the target, and every consecutive pair really is")
print("joined by an edge. The only way to catch it is to know which question")
print("you asked.")
print()
print(f"  shortest hop count to the far corner : "
      f"{len(rebuild(bfs_parent, len(ADJ) - 1)) - 1}")
print(f"  cheapest weight to the far corner    : {dist[len(ADJ) - 1]}")
