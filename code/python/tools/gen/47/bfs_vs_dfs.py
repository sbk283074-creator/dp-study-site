#!/usr/bin/env python3
"""Chapter 47 demo -- the same graph, the same question, two answers.

"Find a route from A to B" has two meanings. BFS answers "the fewest steps".
DFS answers "the first route I stumbled into". On an unweighted graph only
the first is a shortest path, and the gap between them is not a rounding
error -- it is the difference between a route and a random walk.
"""
import random
from collections import deque

ROWS = COLS = 40


def build(rows, cols, wall_ratio, seed):
    rng = random.Random(seed)
    walls = {(r, c) for r in range(rows) for c in range(cols)
             if rng.random() < wall_ratio}
    walls.discard((0, 0))
    walls.discard((rows - 1, cols - 1))
    return walls


WALLS = build(ROWS, COLS, 0.25, seed=3)
START, GOAL = (0, 0), (ROWS - 1, COLS - 1)
MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def neighbours(cell):
    r, c = cell
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in WALLS:
            yield (nr, nc)


def bfs_path(start, goal):
    """Record the parent of each node the first time it is reached. The
    parent chain of the goal is then a shortest path, by construction."""
    parent = {start: None}
    queue = deque([start])
    probes = 0
    while queue:
        u = queue.popleft()
        if u == goal:
            break
        for w in neighbours(u):
            probes += 1
            if w not in parent:
                parent[w] = u
                queue.append(w)
    return walk(parent, goal), probes, len(parent)


def dfs_path(start, goal):
    """First route found, with no promise about its length. The stack holds
    (node, parent) so the chain can still be rebuilt."""
    parent = {start: None}
    stack = [start]
    probes = 0
    while stack:
        u = stack.pop()
        if u == goal:
            break
        for w in neighbours(u):
            probes += 1
            if w not in parent:
                parent[w] = u
                stack.append(w)
    return walk(parent, goal), probes, len(parent)


def walk(parent, goal):
    if goal not in parent:
        return []
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


bfs_route, bfs_probes, bfs_seen = bfs_path(START, GOAL)
dfs_route, dfs_probes, dfs_seen = dfs_path(START, GOAL)
straight = ROWS + COLS - 2

print(f"a {ROWS}x{COLS} grid, {len(WALLS):,} walls, from {START} to {GOAL}")
print(f"the straight-line distance is {straight} steps")
print()
print(f"{'traversal':<12}{'steps':>8}{'vs straight line':>18}"
      f"{'cells seen':>13}{'probes':>10}")
print("-" * 61)
print(f"{'BFS':<12}{len(bfs_route) - 1:>8}{len(bfs_route) - 1 - straight:>18,}"
      f"{bfs_seen:>13,}{bfs_probes:>10,}")
print(f"{'DFS':<12}{len(dfs_route) - 1:>8}{len(dfs_route) - 1 - straight:>18,}"
      f"{dfs_seen:>13,}{dfs_probes:>10,}")
print()
print(f"  DFS route is {len(dfs_route) / len(bfs_route):.1f}x the length of the BFS route")
print(f"  both reach the goal: {bool(bfs_route) and bool(dfs_route)}")
print()
print("Both traversals visit the goal, and only one of them arrives by a")
print("sensible route. The DFS route is not a bug -- it is exactly what")
print("'follow the first unexplored neighbour' means. DFS commits to a")
print("direction and does not reconsider until it is forced to, so it can")
print("walk the entire grid before it happens to fall into the goal.")
print()
print("That is why the choice of traversal is a choice about the *question*,")
print("not about speed. On this grid DFS looked at fewer cells, because it")
print("committed early and got lucky; on a graph where the goal is behind a")
print("wall it would look at more, and the route would still be bad.")
print()
print("The rule to carry: if the edge count matters, it is BFS and only BFS.")
print("DFS is for questions where the *order* is the answer -- is this")
print("connected, does it contain a cycle, in what order must these run --")
print("and it says nothing useful about distance.")
print()
print(f"  first 4 cells of the BFS route: {bfs_route[:4]}")
print(f"  first 4 cells of the DFS route: {dfs_route[:4]}")
print(f"  routes are identical: {bfs_route == dfs_route}")
