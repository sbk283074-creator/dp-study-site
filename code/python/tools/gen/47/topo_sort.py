#!/usr/bin/env python3
"""Chapter 47 demo -- topological sort, two ways, and the cycle that breaks
both of them.

A topological order of a directed graph is an ordering in which every edge
points forwards. It exists if and only if the graph has no cycle -- which
makes topological sorting the standard way to *detect* a cycle in a
dependency graph, and the reason a build system can tell you that two modules
depend on each other instead of just looping until it runs out of memory.
"""
from collections import deque

PREREQUISITES = {
    "intro": [],
    "algebra": ["intro"],
    "systems": ["intro"],
    "calculus": ["algebra"],
    "stats": ["algebra"],
    "compilers": ["systems", "algebra"],
    "physics": ["calculus", "algebra"],
    "graphics": ["calculus", "systems"],
    "ml": ["calculus", "stats"],
}


def invert(prereqs):
    """Prerequisites are the natural way to write it down; adjacency from
    prerequisite to dependent is the way to compute with it."""
    adj = {course: [] for course in prereqs}
    for course, needs in prereqs.items():
        for need in needs:
            adj[need].append(course)
    return adj


def kahn(adj):
    """Peel off the nodes with nothing left pointing at them. Returns the
    order and whether it covered the whole graph -- which is the cycle test."""
    indegree = {u: 0 for u in adj}
    for u in adj:
        for v in adj[u]:
            indegree[v] += 1
    queue = deque(u for u in adj if indegree[u] == 0)
    order = []
    probes = 0
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            probes += 1
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return order, probes, len(order) == len(adj)


def dfs_topo(adj):
    """Post-order, reversed. A node is appended only after everything it
    points at has been appended, so reversing puts prerequisites first."""
    seen = set()
    order = []
    probes = 0

    def visit(u):
        nonlocal probes
        seen.add(u)
        for v in adj[u]:
            probes += 1
            if v not in seen:
                visit(v)
        order.append(u)

    for u in adj:
        if u not in seen:
            visit(u)
    order.reverse()
    return order, probes


def is_valid(adj, order):
    """Every edge must point forwards in the order."""
    position = {u: i for i, u in enumerate(order)}
    return all(position[u] < position[v] for u in adj for v in adj[u])


ADJ = invert(PREREQUISITES)
EDGES = sum(len(v) for v in ADJ.values())

print(f"{len(ADJ)} courses, {EDGES} prerequisite edges")
print()
print("  the graph, as 'prerequisite -> what it unlocks'")
for course, unlocks in ADJ.items():
    if unlocks:
        print(f"    {course:<10} -> {', '.join(unlocks)}")
print()
kahn_order, kahn_probes, complete = kahn(ADJ)
dfs_order, dfs_probes = dfs_topo(ADJ)
print(f"  Kahn's algorithm  : {' -> '.join(kahn_order)}")
print(f"  DFS post-order    : {' -> '.join(dfs_order)}")
print()
print(f"  the two orders agree        : {kahn_order == dfs_order}")
print(f"  Kahn's order is valid       : {is_valid(ADJ, kahn_order)}")
print(f"  DFS order is valid          : {is_valid(ADJ, dfs_order)}")
print(f"  Kahn covered every node     : {complete}")
print(f"  Kahn's edge probes          : {kahn_probes} of {EDGES} edges")
print(f"  DFS's edge probes           : {dfs_probes} of {EDGES} edges")
print()
print("The two algorithms disagree about the order, and both are right. A")
print("topological order is not unique -- 'algebra before physics' is a")
print("constraint, and whether 'stats' comes before or after 'physics' is")
print("not specified by anything. Only the *relative* order of an edge's two")
print("endpoints is pinned, which is what `is_valid` checks and the only")
print("thing a topological sort promises.")
print()
print("Both are O(V + E): every node is enqueued once and every edge examined")
print("once, which is why the probe counts match the edge count exactly. Kahn")
print("spends O(V) memory on the in-degree table; DFS spends it on the")
print("recursion stack, and on a deep graph that is where the recursion limit")
print("from the previous section comes back to bite.")
print()
print()
print("Now the case that makes topological sorting worth knowing for: a cycle")
print()
CYCLIC = dict(PREREQUISITES)
CYCLIC["compilers"] = ["systems", "graphics"]
CYCLIC["graphics"] = ["compilers"]
BAD = invert(CYCLIC)
order, probes, complete = kahn(BAD)
stuck = [u for u in BAD if u not in order]
print(f"  compilers now requires graphics, and graphics requires compilers")
print()
print(f"  Kahn's order        : {' -> '.join(order)}")
print(f"  covered every node  : {complete}")
print(f"  nodes it could not place ({len(stuck)}): {', '.join(sorted(stuck))}")
print()
print("The algorithm did not hang and it did not raise. It ran out of nodes")
print("with no prerequisites and stopped, which is the whole cycle test: a")
print("directed graph is acyclic if and only if a topological sort consumes")
print("all of it. Everything left over is on a cycle or downstream of one --")
print("and here it is exactly the two nodes of the cycle, because nothing")
print("depends on them.")
print()
print("That distinction is the difference between a useful error and a")
print("useless one. 'Dependency cycle detected' sends somebody hunting;")
print("'compilers -> graphics -> compilers' does not. The leftover set is")
print("free -- it is exactly the nodes the algorithm never reached.")
print()
print(f"  is the stuck set a superset of the cycle? "
      f"{set(stuck) >= {'compilers', 'graphics'}}")
print(f"  the same test on the acyclic graph    : {kahn(ADJ)[2]}")
