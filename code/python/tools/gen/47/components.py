#!/usr/bin/env python3
"""Chapter 47 demo -- connected components, the simplest thing a traversal
can tell you.

"How many separate pieces is this made of?" is the first question worth
asking about any graph you did not build yourself. It costs one traversal per
piece, and the traversal is a flood fill -- which is the same BFS from earlier
in the chapter, with the queue swapped for a stack or left alone, because the
answer does not depend on the order.
"""
import random
from collections import deque

ROWS, COLS = 18, 56
SEED = 4
rng = random.Random(SEED)
LAND = {(r, c) for r in range(ROWS) for c in range(COLS)
        if rng.random() < 0.42}


def flood_fill(start, seen, stack_based):
    """One component. The frontier is a stack or a queue, and the *set of
    cells reached* is identical either way."""
    frontier = [start] if stack_based else deque([start])
    seen.add(start)
    members = []
    cells = 0
    while frontier:
        cell = frontier.pop() if stack_based else frontier.popleft()
        members.append(cell)
        cells += 1
        r, c = cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (nr, nc) in LAND and (nr, nc) not in seen:
                seen.add((nr, nc))
                frontier.append((nr, nc))
    return members, cells


def components(stack_based):
    seen = set()
    found = []
    cells = 0
    for cell in sorted(LAND):
        if cell not in seen:
            members, touched = flood_fill(cell, seen, stack_based)
            found.append(members)
            cells += touched
    return found, cells


by_stack, cells_stack = components(stack_based=True)
by_queue, cells_queue = components(stack_based=False)

print(f"a {ROWS}x{COLS} map, {len(LAND):,} land cells of {ROWS * COLS:,}")
print()
for r in range(ROWS):
    print("  " + "".join("#" if (r, c) in LAND else "." for c in range(COLS)))
print()
sizes = sorted((len(m) for m in by_stack), reverse=True)
print(f"  components found by a stack : {len(by_stack)}")
print(f"  components found by a queue : {len(by_queue)}")
print(f"  the two partitions are equal: "
      f"{ {frozenset(m) for m in by_stack} == {frozenset(m) for m in by_queue} }")
print(f"  cells accounted for         : {cells_stack:,} of {len(LAND):,} land")
print(f"  sizes, largest first        : {sizes}")
print()
print("The two traversals produce exactly the same partition, and that is not")
print("a coincidence -- it is the definition of a connected component. Two")
print("cells are in the same component if some path of land joins them, and")
print("that is a property of the map. The order in which a traversal discovers")
print("them cannot change it.")
print()
print("That is why components are the easy question. Every other question in")
print("this chapter -- how far, how expensive, in what order -- has an answer")
print("that depends on *how* you traversed. This one does not, so the code can")
print("be the simplest version of the traversal with no loss at all.")
print()
print("The cost is one pass over the cells, O(V + E), and it is worth noting")
print("how much of the work is the `seen` set rather than the traversal. Every")
print("land cell is added to it once and tested against it four times, which")
print("is why the flood fill is memory-bound rather than compute-bound.")
print()
print()
print("Part 2 -- the same idea on a graph with no geometry")
print()
NODES = 400
EDGES_PER_NODE = 3
rng2 = random.Random(SEED)
adj = {i: [] for i in range(NODES)}
for _ in range(NODES * EDGES_PER_NODE // 2):
    a = rng2.randrange(NODES)
    b = rng2.randrange(NODES)
    if a != b:
        adj[a].append(b)
        adj[b].append(a)
EDGE_COUNT = sum(len(v) for v in adj.values()) // 2
seen = set()
groups = []
for node in adj:
    if node not in seen:
        stack = [node]
        seen.add(node)
        group = []
        while stack:
            u = stack.pop()
            group.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        groups.append(group)
sizes2 = sorted((len(g) for g in groups), reverse=True)
print(f"  {NODES:,} nodes, {EDGE_COUNT:,} random edges, mean degree "
      f"{2 * EDGE_COUNT / NODES:.1f}")
print(f"  components                  : {len(groups)}")
print(f"  largest component           : {sizes2[0]:,} nodes "
      f"({sizes2[0] / NODES * 100:.0f}% of the graph)")
print(f"  isolated nodes              : {sum(1 for g in groups if len(g) == 1)}")
print(f"  component sizes             : {sizes2}")
print()
print("A random graph with mean degree 3 is almost entirely one blob with a")
print("handful of stragglers, and that is a fact about random graphs rather")
print("than about this code -- the largest component swallows nearly")
print("everything well before the mean degree reaches 2.")
print()
print("The practical version of this question is asked constantly: is this")
print("network still one network, which accounts are unreachable, does this")
print("migration plan leave anything stranded. All of them are one flood fill")
print("and a count, and the count is the interesting part -- a component of")
print("size 1 is a node that can never talk to anything.")
print()
print(f"  every land cell reached exactly once: {cells_stack == len(LAND)}")
print(f"  every node reached exactly once    : "
      f"{sum(len(g) for g in groups) == NODES}")
