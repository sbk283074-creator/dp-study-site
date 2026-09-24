"""Chapter 35 -- a heuristic buys speed with a promise, and the promise is
admissibility.

One grid, one wall with a gap, three searches. The count is of nodes each one
expands, of the length of the path it returns, and of the cells where its
estimate of the remaining cost is larger than the truth.
"""

from collections import deque

WIDTH = 20
HEIGHT = 20
START = (0, 0)
GOAL = (19, 19)

# A wall in column 10 from row 0 to row 14. The gap is rows 15 to 19.
WALLS = {(10, y) for y in range(15)}


def neighbours(node):
    x, y = node
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and (nx, ny) not in WALLS:
            yield (nx, ny)


def manhattan(node):
    return abs(node[0] - GOAL[0]) + abs(node[1] - GOAL[1])


def true_distances():
    """Breadth-first from the goal, so every cell knows its real distance."""
    dist = {GOAL: 0}
    queue = deque([GOAL])
    while queue:
        node = queue.popleft()
        for nxt in neighbours(node):
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return dist


def search(weight):
    """Dijkstra when weight is 0, A* when it is 1, and an inflated A* above.

    The queue is kept as a list and the smallest entry taken each round, so the
    count of nodes expanded does not depend on a heap implementation.
    """
    open_set = [(weight * manhattan(START), 0, START)]
    best = {START: 0}
    expanded = 0
    while open_set:
        open_set.sort(key=lambda entry: entry[0])
        _, cost, node = open_set.pop(0)
        if cost > best.get(node, cost):
            continue
        expanded += 1
        if node == GOAL:
            return expanded, cost
        for nxt in neighbours(node):
            nxt_cost = cost + 1
            if nxt_cost < best.get(nxt, 1 << 30):
                best[nxt] = nxt_cost
                open_set.append((nxt_cost + weight * manhattan(nxt), nxt_cost, nxt))
    return expanded, None


distances = true_distances()
free_cells = sorted(distances)


def overstates(weight):
    """Cells where the estimate is larger than the true remaining cost."""
    return sum(1 for cell in free_cells if weight * manhattan(cell) > distances[cell])


rows = [
    ("no heuristic", 0),
    ("manhattan", 1),
    ("three times manhattan", 3),
]

results = []
for label, weight in rows:
    expanded, cost = search(weight)
    results.append((label, expanded, cost, overstates(weight)))

print(f"a {WIDTH} by {HEIGHT} grid, wall in column 10, gap at rows 15 to 19")
print()
print(f"{'search':<26}{'nodes expanded':>16}{'path length':>13}"
      f"{'overstated':>12}")
print("-" * 67)
for label, expanded, cost, over in results:
    print(f"{label:<26}{expanded:>16}{cost:>13}{over:>12}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'cells in the grid':<46}{WIDTH * HEIGHT:>8}")
print(f"{'cells the wall removes':<46}{len(WALLS):>8}")
print(f"{'cells reachable from the goal':<46}{len(free_cells):>8}")
for label, expanded, _, _ in results:
    print(f"{'nodes expanded, ' + label:<46}{expanded:>8}")
shortest = min(cost for _, _, cost, _ in results)
print(f"{'shortest path found':<46}{shortest:>8}")
for label, _, cost, _ in results:
    print(f"{'path length, ' + label:<46}{cost:>8}")
for label, _, _, over in results:
    print(f"{'estimate overstates, ' + label:<46}{over:>8}")

print()
print("The first two rows are the same answer and they are not the same search.")
print("Without a heuristic the queue spreads out in every direction and expands")
print(f"{results[0][1]} cells before it happens to reach the goal. Manhattan distance")
print(f"leans the queue toward the goal, so it expands {results[1][1]} and returns a path")
print("of exactly the same length.")
print()
print("The third row is the trap, and the column that catches it is the last")
print(f"one. Three times Manhattan expands only {results[2][1]} cells -- it is by far the")
print(f"fastest search in the table -- and its estimate is larger than the truth on")
print(f"{results[2][3]} of the {len(free_cells)} reachable cells. On most of the map it is not a")
print("lower bound on anything; it is a guess that happens to point the right")
print("way.")
print()
print(f"And on this map it still returns a path of {shortest}, which is the part that")
print("makes admissibility a proof rather than a test. A search with an inflated")
print("heuristic is allowed to return a worse path, not required to; whether it")
print("does depends on the map. So a heuristic is admissible because it can be")
print("shown to be, and Manhattan distance is: no route is shorter than the")
print("straight-line steps it counts, on a grid where every step costs one.")
print("Scaling it by anything destroys that argument, and the count in the last")
print("column is how much of the map the argument covered.")
