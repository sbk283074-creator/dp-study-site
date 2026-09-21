#!/usr/bin/env python3
"""Chapter 47 demo -- breadth-first search, and the two things it gives you
that no other traversal does.

BFS explores in rings: everything one step away, then two, then three. Two
consequences follow, and together they are why BFS is the default choice for
anything unweighted. The level number *is* the shortest distance in edges,
and because a node is first reached by the shortest route, the parent you
recorded is on a shortest path.
"""
from collections import deque
import random

FRIENDS = {
    "you": ["alice", "bob", "claire"],
    "bob": ["anuj", "peggy"],
    "alice": ["peggy"],
    "claire": ["thom", "jonny"],
    "anuj": [],
    "peggy": [],
    "thom": [],
    "jonny": [],
}


def bfs(adj, start):
    """Returns the visit order, the level of each node, the parent each node
    was first reached from, and the number of edge examinations."""
    level = {start: 0}
    parent = {start: None}
    order = []
    queue = deque([start])
    probes = 0
    while queue:
        u = queue.popleft()
        order.append(u)
        for w in adj[u]:
            probes += 1
            if w not in level:
                level[w] = level[u] + 1
                parent[w] = u
                queue.append(w)
    return order, level, parent, probes


def path_to(parent, target):
    """Walk the parent chain backwards, then reverse it."""
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


print("Part 1 -- a small graph, read out loud")
print()
order, level, parent, probes = bfs(FRIENDS, "you")
print(f"  visit order : {' -> '.join(order)}")
print()
print(f"  {'node':<9}{'level':>6}   reached from")
print("  " + "-" * 30)
for node in sorted(level, key=lambda n: (level[n], n)):
    print(f"  {node:<9}{level[node]:>6}   {parent[node] or '(start)'}")
print()
print(f"  path to thom : {' -> '.join(path_to(parent, 'thom'))}"
      f"   ({level['thom']} steps)")
print(f"  edge probes  : {probes}")
print()
print("Two different things are being read off one traversal, and it is worth")
print("keeping them apart. The *order* is what BFS is doing. The *level* is a")
print("by-product, and it is the answer to 'how far away is this?' -- the")
print("level of a node is its shortest distance from the start, in edges,")
print("because BFS cannot reach a node at level 3 before it has finished")
print("level 2.")
print()
print("The parent map is the third by-product, and it is the one that turns a")
print("distance into an actual route. Nothing extra was computed to get it:")
print("the parent was recorded at the moment the node was first discovered,")
print("and 'first discovered' means 'discovered by a shortest route'.")
print()
print()
print("Part 2 -- a grid, where the same code answers a real question")
print()


def build_grid(rows, cols, wall_ratio, seed):
    rng = random.Random(seed)
    walls = set()
    for r in range(rows):
        for c in range(cols):
            if rng.random() < wall_ratio:
                walls.add((r, c))
    walls.discard((0, 0))
    walls.discard((rows - 1, cols - 1))
    return walls


def grid_neighbours(rows, cols, walls, cell):
    r, c = cell
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in walls:
            yield (nr, nc)


def grid_bfs(rows, cols, walls, start, goal):
    level = {start: 0}
    parent = {start: None}
    queue = deque([start])
    probes = 0
    while queue:
        u = queue.popleft()
        if u == goal:
            break
        for w in grid_neighbours(rows, cols, walls, u):
            probes += 1
            if w not in level:
                level[w] = level[u] + 1
                parent[w] = u
                queue.append(w)
    return level, parent, probes


def has_monotone_route(rows, cols, walls):
    """Is there a route using only down and right moves? If so the shortest
    route is exactly the straight-line distance and the demo is dull."""
    reach = [[False] * cols for _ in range(rows)]
    reach[0][0] = (0, 0) not in walls
    for r in range(rows):
        for c in range(cols):
            if (r, c) in walls or (r == 0 and c == 0):
                continue
            from_above = reach[r - 1][c] if r > 0 else False
            from_left = reach[r][c - 1] if c > 0 else False
            reach[r][c] = from_above or from_left
    return reach[rows - 1][cols - 1]


ROWS = COLS = 200
START, GOAL = (0, 0), (ROWS - 1, COLS - 1)
STRAIGHT = ROWS + COLS - 2

# A random wall layout can seal a corner off, or leave a straight staircase
# through. The seed is chosen so that the goal is reachable *and* no monotone
# route exists -- deterministic, because the same seed always wins.
for seed in range(200):
    WALLS = build_grid(ROWS, COLS, 0.28, seed)
    if not has_monotone_route(ROWS, COLS, WALLS):
        level, parent, probes = grid_bfs(ROWS, COLS, WALLS, START, GOAL)
        if GOAL in level:
            break
else:
    raise SystemExit("no suitable layout in 200 seeds")

route = path_to(parent, GOAL)
open_cells = ROWS * COLS - len(WALLS)
print(f"a {ROWS}x{COLS} grid, {len(WALLS):,} cells walled off")
print(f"  open cells                 : {open_cells:,}")
print(f"  the straight-line distance : {STRAIGHT} steps")
print(f"  shortest route             : {level[GOAL]} steps")
print(f"  detour forced by the walls : {level[GOAL] - STRAIGHT} steps")
print(f"  cells dequeued             : {len(level):,}")
print(f"  edge probes                : {probes:,}")
print(f"  probes per open cell       : {probes / open_cells:.2f}")
print()
print("The route is longer than the straight line, because the walls do not")
print("allow a straight line. BFS found the shortest way around them without")
print("ever considering the straight line, or the goal's position, or anything")
print("at all about where it was going.")
print()
print("That is simultaneously BFS's strength and its weakness, and the second")
print("half of this chapter is about the weakness. Expanding equally in every")
print("direction is what makes it provably correct on an unweighted graph, and")
print("it is also what makes it explore most of the grid to reach a corner. A")
print("heuristic is the fix, and it costs the proof.")
print()
print(f"  first three steps of the route: {route[:3]}")
print(f"  last three steps of the route : {route[-3:]}")
