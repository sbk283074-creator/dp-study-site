#!/usr/bin/env python3
"""Chapter 47 demo -- the assumption Dijkstra is standing on.

Dijkstra settles a node the moment it comes out of the heap, and the
correctness proof says that is safe *because every edge weight is
non-negative*. Remove that and the algorithm still runs, still terminates,
and returns a wrong answer with no warning anywhere.

Bellman-Ford makes no such assumption. It pays for that with a worse
complexity, and it gets the negative-cycle test for free -- which is the
reason it is still in every library.
"""
import heapq

NODES = ["S", "A", "B", "T"]
EDGES = [
    ("S", "A", 1),
    ("S", "B", 2),
    ("B", "A", -2),
    ("A", "T", 1),
]


def adjacency(nodes, edges):
    adj = {u: [] for u in nodes}
    for u, v, w in edges:
        adj[u].append((v, w))
    return adj


def dijkstra(adj, nodes, source):
    """The textbook version, with a settled set: once a node is popped it is
    never reconsidered. This is the version the proof is about."""
    dist = {u: float("inf") for u in nodes}
    dist[source] = 0
    settled = set()
    order = []
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in settled:
            continue
        settled.add(u)
        order.append(u)
        for v, w in adj[u]:
            if v not in settled and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return dist, order


def bellman_ford(nodes, edges, source):
    """Relax every edge, V-1 times. Returns the distances, how many rounds it
    actually needed, and whether a further round would still change
    something -- which is exactly the negative-cycle test."""
    dist = {u: float("inf") for u in nodes}
    dist[source] = 0
    rounds_used = 0
    for i in range(len(nodes) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        rounds_used = i + 1
        if not changed:
            break
    negative_cycle = any(dist[u] + w < dist[v] for u, v, w in edges)
    return dist, rounds_used, negative_cycle


ADJ = adjacency(NODES, EDGES)
print("the graph")
print()
for u, v, w in EDGES:
    print(f"    {u} -> {v}   weight {w:>3}")
print()
print("  one of those weights is negative, and B -> A is the only way to")
print("  reach A for less than 1.")
print()
dij_dist, order = dijkstra(ADJ, NODES, "S")
bf_dist, rounds, cycle = bellman_ford(NODES, EDGES, "S")
print(f"  Dijkstra settled the nodes in order: {' -> '.join(order)}")
print()
print(f"  {'node':<6}{'Dijkstra':>10}{'Bellman-Ford':>14}{'agree':>8}")
print("  " + "-" * 38)
for node in NODES:
    d = dij_dist[node]
    b = bf_dist[node]
    print(f"  {node:<6}{d:>10}{b:>14}{str(d == b):>8}")
print()
print(f"  Bellman-Ford rounds used : {rounds} of {len(NODES) - 1} allowed")
print()
print("The true cheapest route to T is S -> B -> A -> T, and it costs 2 - 2 + 1")
print("= 1. Dijkstra returns 2, because of the order it settled the nodes in:")
print("A came out of the heap at distance 1 and was declared final, and by the")
print("time B had been settled it was too late to revise A. The negative edge")
print("was discovered *after* the node it improves had been frozen.")
print()
print("That is the whole content of the non-negative assumption. Dijkstra's")
print("greedy step says 'the nearest unsettled node is final', and the proof")
print("of that step is: any other route to it would have to leave through a")
print("node that is already settled, and every edge adds a non-negative")
print("amount, so no detour can be cheaper. A negative edge makes a detour")
print("cheaper, and the argument collapses.")
print()
print("Nothing in the output says so. Both numbers are plausible, one is")
print("wrong, and the algorithm had no way to know -- it never computes the")
print("quantity that would tell it.")
print()
print()
print("Part 2 -- Bellman-Ford's second job")
print()
CYCLE_EDGES = EDGES + [("T", "B", -5)]
adj2 = adjacency(NODES, CYCLE_EDGES)
_, rounds2, cycle2 = bellman_ford(NODES, CYCLE_EDGES, "S")
print("  adding one more edge: T -> B  weight -5")
print()
print(f"  {'':<28}{'rounds used':>13}{'negative cycle':>16}")
print("  " + "-" * 57)
print(f"  {'the graph above':<28}{rounds:>13}{str(cycle):>16}")
print(f"  {'with T -> B added':<28}{rounds2:>13}{str(cycle2):>16}")
print()
print("The second graph has a cycle -- B -> A -> T -> B -- whose total weight")
print("is -2 + 1 - 5 = -6. A negative cycle means there is no shortest path at")
print("all: you can go round the loop again and pay less, forever, so the")
print("'shortest distance' to T is unbounded below and is not a number.")
print()
print("Bellman-Ford reports that for the cost of one extra pass over the")
print("edges. After V-1 rounds every shortest path has been found -- because a")
print("shortest path visits each node at most once -- so if a V-th round can")
print("still improve something, the only explanation is a negative cycle.")
print()
print("That is why the algorithm survives. It is slower than Dijkstra, and it")
print("is the only one of the two that can answer 'is this graph even")
print("well-posed?' -- which is a question you want answered before you trust")
print("a route, a price, or a schedule.")
print()
print(f"  V - 1 = {len(NODES) - 1} rounds is the guarantee; the first graph settled in")
print(f"  {rounds} rounds, and the second used all {rounds2}")
print(f"  Dijkstra on the cyclic graph : ", end="")
dij2, _ = dijkstra(adj2, NODES, "S")
print(f"T = {dij2['T']}, and it terminates without complaint")
