#!/usr/bin/env python3
"""Chapter 47 demo -- A* is Dijkstra with an opinion about where the goal is,
and the opinion is only half of it.

Dijkstra expands in rings because it has no idea where the target is. A* adds
a heuristic -- an estimate of the remaining distance -- to the priority, and
the search leans towards the goal.

Two things have to be right for that to pay off, and they are independent.
The estimate must never *overstate* the true remaining cost, or the answer is
wrong. And the queue has to break ties towards the goal, or the estimate buys
almost nothing -- which is the part that surprises people, and the reason the
first version below looks broken.
"""
import heapq
import random

SIZE = 60
START, GOAL = (0, 0), (SIZE - 1, SIZE - 1)
MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))
WALL_RATIO = 0.15


def build_walls(size, ratio, seed):
    rng = random.Random(seed)
    walls = {(r, c) for r in range(size) for c in range(size)
             if rng.random() < ratio}
    walls.discard(START)
    walls.discard(GOAL)
    return walls


def neighbours(walls, cell):
    r, c = cell
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE and (nr, nc) not in walls:
            yield (nr, nc)


def search(walls, heuristic, prefer_deep):
    """`heuristic` is the estimate of the remaining cost. `prefer_deep` decides
    which of two cells with the same estimated total comes out of the heap
    first: the one nearer the start, or the one nearer the goal.

    The heap entry is (f, tie-break key, g, cell) -- the four fields are kept
    separate so that neither the key nor the sign of g can be confused for the
    other.
    """
    best = {START: 0}
    heap = [(heuristic(START), 0, 0, START)]
    expanded = 0
    pushed = 0
    while heap:
        _, _, g, u = heapq.heappop(heap)
        if u == GOAL:
            break
        if g > best.get(u, float("inf")):
            continue
        expanded += 1
        for v in neighbours(walls, u):
            if g + 1 < best.get(v, float("inf")):
                gv = g + 1
                best[v] = gv
                key = -gv if prefer_deep else gv
                heapq.heappush(heap, (gv + heuristic(v), key, gv, v))
                pushed += 1
    return best.get(GOAL), expanded, pushed


def manhattan(cell):
    return abs(cell[0] - GOAL[0]) + abs(cell[1] - GOAL[1])


def zero(cell):
    return 0


def inflated(cell):
    return 3 * manhattan(cell)


def reachable(walls):
    seen = {START}
    stack = [START]
    while stack:
        u = stack.pop()
        if u == GOAL:
            return True
        for v in neighbours(walls, u):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return False


for seed in range(300):
    WALLS = build_walls(SIZE, WALL_RATIO, seed)
    if reachable(WALLS):
        break
else:
    raise SystemExit("no reachable layout in 300 seeds")

CASES = [
    ("Dijkstra (h = 0)", zero, False),
    ("A* (Manhattan, shallow ties)", manhattan, False),
    ("A* (Manhattan, deep ties)", manhattan, True),
    ("A* (Manhattan x 3, shallow)", inflated, False),
]
rows = []
for name, heuristic, prefer_deep in CASES:
    cost, expanded, pushed = search(WALLS, heuristic, prefer_deep)
    rows.append((name, cost, expanded, pushed))

straight = SIZE + SIZE - 2
base = rows[0][2]
print(f"a {SIZE}x{SIZE} grid, {len(WALLS):,} walls ({WALL_RATIO:.0%})")
print(f"the straight-line distance is {straight} steps")
print()
print(f"{'search':<30}{'route':>7}{'expanded':>10}{'vs Dijkstra':>13}")
print("-" * 60)
for name, cost, expanded, pushed in rows:
    print(f"{name:<30}{cost:>7}{expanded:>10,}{base / expanded:>12.1f}x")
print()
print("Read the second row first, because it is the one that does not match")
print("the textbook. An admissible heuristic, correct code, optimal route --")
print(f"and {base / rows[1][2]:.1f} times fewer cells expanded than Dijkstra. All that")
print("work for almost nothing.")
print()
print("The reason is ties. `f = g + h` is the estimated total cost of a route")
print("through a cell, and near the optimum *every* cell on every good route")
print("has the same f -- that is what 'good route' means. So the heap is full")
print("of cells with identical priority, and something has to decide between")
print("them. Pushing `(f, g, cell)` decides in favour of the *smallest* g, and")
print("the smallest g is the cell nearest the start -- so the search expands")
print("outwards in rings, which is precisely what Dijkstra did. The heuristic")
print("is in the arithmetic and absent from the behaviour.")
print()
print("Row three changes one thing: on an equal f, the *largest* g comes out")
print("first. Now the search dives towards the goal along whatever route looks")
print("cheapest, and the expansions collapse.")
print()
print(f"  cells expanded: {rows[1][2]:,} -> {rows[2][2]:,}"
      f"   ({rows[1][2] / rows[2][2]:.1f}x fewer)")
print(f"  the route is unchanged, and still optimal: {rows[1][1] == rows[2][1]}")
print()
print("Same heuristic, same proof, same answer. The only difference is which")
print("of two equally-good cells is looked at first. This is the single most")
print("valuable thing to know about implementing A* in practice, and it is")
print("invisible in every description of the algorithm -- because the")
print("description is about the arithmetic, and this is about the queue.")
print()
print("The usual refinement is to break ties by the cross-product of the")
print("direction to the goal and the direction to the neighbour, which prefers")
print("a straight line over a staircase. Preferring depth is the cheap version")
print("and gets most of the effect.")
print()
print()
print("Now the other half of the contract, which is about correctness")
print()
print(f"  {'search':<30}{'route':>7}{'optimal?':>10}")
print("-" * 47)
for name, cost, expanded, pushed in rows:
    print(f"  {name:<30}{cost:>7}{str(cost == rows[0][1]):>10}")
print()
print("Multiplying the estimate by three makes the search even more focused")
print(f"-- {rows[3][2]:,} cells, the fewest of the four -- and the route it returns is")
print(f"{rows[3][1] - rows[0][1]} steps longer than the best one. Manhattan distance is exactly")
print("the true remaining cost on an open four-directional grid, so tripling")
print("it overstates the cost of every route. A* then abandons a route that is")
print("already known to be good in favour of one that merely *looks* good.")
print()
print("That is the admissibility condition: `h(n)` must never exceed the true")
print("remaining cost. It is the price of the speedup, and it is a property of")
print("a function you wrote, not of the algorithm. Dijkstra needs no such")
print("promise because it has no heuristic to be wrong about.")
print()
print("A second condition, consistency, keeps A* from having to re-open cells")
print("it has already settled: `h(u) <= cost(u, v) + h(v)` for every edge. A")
print("consistent heuristic is automatically admissible, and Manhattan")
print("distance on this grid is both. An admissible-but-inconsistent")
print("heuristic still gives the optimal answer; it may just expand a cell")
print("more than once on the way.")
print()
print("And the link back to Chapter 35: the enemy pathfinding there was this")
print("function, on a tilemap, with Manhattan distance as the estimate. A* is")
print("not a different algorithm from Dijkstra. It is Dijkstra with one extra")
print("term in the priority -- and everything that makes it fast is also")
print("everything that makes its correctness depend on a function you supply.")
print()
print(f"  expanded / pushed: {rows[2][2]:,} / {rows[2][3]:,}")
print(f"  open cells in the grid: {SIZE * SIZE - len(WALLS):,}")
