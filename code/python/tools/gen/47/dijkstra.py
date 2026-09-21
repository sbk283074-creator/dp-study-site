#!/usr/bin/env python3
"""Chapter 47 demo -- Dijkstra, counted, against the version with no heap.

Dijkstra is BFS with a priority queue instead of a queue. That single change
is what lets it handle weights, and it is also where all the cost goes. A
binary heap has no "decrease this key" operation, so the standard trick is to
push a *new* entry and discard the stale one when it comes out -- and
counting those stale pops is the whole reason the heap version is worth the
trouble over a plain array scan.
"""
import heapq
import random

ROADS = {
    "home": [("shop", 4), ("school", 9)],
    "shop": [("home", 4), ("school", 2), ("gym", 7)],
    "school": [("home", 9), ("shop", 2), ("gym", 3), ("work", 8)],
    "gym": [("shop", 7), ("school", 3), ("work", 2)],
    "work": [("school", 8), ("gym", 2)],
}


def dijkstra_named(adj, source):
    """The lazy-deletion version: never decrease a key, just push a better
    one and throw away the worse one when it surfaces."""
    dist = {source: 0}
    parent = {source: None}
    heap = [(0, source)]
    pushes = pops = stale = 0
    while heap:
        d, u = heapq.heappop(heap)
        pops += 1
        if d > dist.get(u, float("inf")):
            stale += 1
            continue
        for v, w in adj[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(heap, (d + w, v))
                pushes += 1
    return dist, parent, pushes, pops, stale


def route(parent, target):
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


print("Part 1 -- a small weighted graph")
print()
print("  the graph, as 'from: (to, weight)'")
for node, edges in ROADS.items():
    print(f"    {node:<7} {', '.join(f'{v}:{w}' for v, w in edges)}")
print()
dist, parent, pushes, pops, stale = dijkstra_named(ROADS, "home")
print(f"  {'node':<8}{'distance':>9}   route")
print("  " + "-" * 44)
for node in sorted(dist, key=lambda n: dist[n]):
    print(f"  {node:<8}{dist[node]:>9}   {' -> '.join(route(parent, node))}")
print()
print(f"  heap pushes        : {pushes}")
print(f"  heap pops          : {pops}")
print(f"  stale pops         : {stale}")
print()
print("Look at the distances rather than the code. Every one of them is")
print("final the moment it is popped, and that is Dijkstra's actual claim: the")
print("next node out of the heap is the nearest node not yet settled. The heap")
print("is not an optimisation of the search, it *is* the search -- and the")
print("proof depends on every edge weight being non-negative, which the next")
print("two sections take apart.")
print()
print("The stale pops are the price of the interface. When a shorter route to")
print("a node is found, the old entry cannot be deleted from the middle of a")
print("heap, so a second entry is pushed and the first one is recognised as")
print("obsolete by comparing its distance with the best known. That is why")
print("there are more pushes than there are nodes: a node can be pushed more")
print("than once, and every push after the first is a duplicate waiting to be")
print("thrown away.")
print()
print()
print("Part 2 -- the same job with no heap at all")
print()
GRID = 40


def weighted_grid(size, seed):
    """A grid where every edge has a length in 1..9. Weights make it a road
    network rather than a maze, and they are what BFS cannot handle."""
    rng = random.Random(seed)
    adj = [[] for _ in range(size * size)]
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
V = GRID * GRID


def dijkstra_heap(n, adj, source):
    dist = [float("inf")] * n
    dist[source] = 0
    heap = [(0, source)]
    pushes = pops = stale = relaxations = 0
    while heap:
        d, u = heapq.heappop(heap)
        pops += 1
        if d > dist[u]:
            stale += 1
            continue
        for v, w in adj[u]:
            relaxations += 1
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
                pushes += 1
    return dist, pushes, pops, stale, relaxations


def dijkstra_array(n, adj, source):
    """No heap: scan every node for the nearest unfinished one. The scan is
    n long, and it happens once per node, so the cost is n^2 -- regardless of
    how few edges there are."""
    dist = [float("inf")] * n
    dist[source] = 0
    done = [False] * n
    scans = relaxations = 0
    for _ in range(n):
        best = -1
        best_d = float("inf")
        for v in range(n):
            scans += 1
            if not done[v] and dist[v] < best_d:
                best, best_d = v, dist[v]
        if best < 0:
            break
        done[best] = True
        for v, w in adj[best]:
            relaxations += 1
            if best_d + w < dist[v]:
                dist[v] = best_d + w
    return dist, scans, relaxations


heap_dist, pushes, pops, stale, relaxations = dijkstra_heap(V, ADJ, 0)
array_dist, scans, array_relax = dijkstra_array(V, ADJ, 0)
EDGES = relaxations // 2
print(f"a {GRID}x{GRID} grid, {V:,} nodes, {EDGES:,} edges, weights 1..9")
print()
print(f"{'implementation':<24}{'work units':>13}{'per node':>11}")
print("-" * 48)
print(f"{'heap: edge relaxations':<24}{relaxations:>13,}{relaxations / V:>11.1f}")
print(f"{'heap: pushes':<24}{pushes:>13,}{pushes / V:>11.1f}")
print(f"{'heap: pops':<24}{pops:>13,}{pops / V:>11.1f}")
print(f"{'  of which stale':<24}{stale:>13,}{stale / V:>11.1f}")
print(f"{'array: nearest-node scans':<24}{scans:>13,}{scans / V:>11.1f}")
print(f"{'array: edge relaxations':<24}{array_relax:>13,}{array_relax / V:>11.1f}")
print()
print(f"  the two agree on every distance : {heap_dist == array_dist}")
print(f"  array scans / heap pops         : {scans / pops:.1f}x")
print()
print("Both implementations are Dijkstra and both are correct; only the data")
print("structure differs. The heap's work is proportional to the *edges* -- it")
print("touches a node when an edge improves it, and never otherwise. The")
print("array's work is proportional to the *nodes squared*, because finding")
print("the nearest unfinished node means looking at all of them, every time,")
print("whether or not any of them has changed.")
print()
print("That is the whole argument for the heap, and it has an edge case worth")
print("knowing. On a dense graph the number of edges approaches n^2, so both")
print("are n^2 and the heap's log factor makes it *worse*. The heap wins on")
print("sparse graphs -- which is what a road network, a dependency tree and a")
print("social graph all are.")
print()
print(f"  heap entries pushed in total    : {pushes:,}")
print(f"  stale entries thrown away       : {stale:,} ({stale / pushes * 100:.1f}% of pushes)")
print(f"  relaxations that improved a node: {pushes - 1:,}")
