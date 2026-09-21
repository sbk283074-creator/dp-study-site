---
chapter: 47
part: 8
title: Graphs
summary: A graph is a set of edges and a decision about how to store them. Traverse it in rings or in paths, order it, weigh it, and search it -- BFS, DFS, topological sort, Dijkstra, A*, union-find -- with every cost counted rather than timed.
minutes: 110
tags: [graphs, BFS, DFS, topological sort, Dijkstra, A*, union-find, complexity, pathfinding]
---

Chapter 45 gave you the containers and Chapter 46 the sorting. This chapter is where they stop being
exercises and start being the shape of the problem.

A graph is the most general data structure there is. A tree is a graph. A list is a graph. A
dependency file, a road network, a social network, a game map, a state space, and the call graph of
your own program are all graphs, and they are all the same object: a set of things, and a set of
pairs of things that are related.

That generality is the difficulty. There is no single graph algorithm, because there is no single
graph question -- and the questions in this chapter look so similar that choosing the wrong one
produces a confident, plausible, wrong answer with no exception raised. That is the theme, and it
runs through every section: **a wrong shortest path looks exactly like a right one**.

Two things keep it honest. The first is that Chapter 35 already built A\*, so by the end of this
chapter you will be able to see that the enemy pathfinding there was graph search with a heuristic,
rather than a technique that arrived from nowhere. The second is the counting discipline from
Chapters 44 to 46: every cost below is an exact count of probes, expansions, relaxations or hops,
and not one of them is a stopwatch reading.

## The two ways to store a graph

Everything in this chapter is a decision about representation, so start with the representation
itself. There are two, they are both obvious, and the trade between them is a factor of the number
of nodes.

```python run
#!/usr/bin/env python3
"""Chapter 47 demo -- the two ways to store a graph, and what each one costs.

A graph is just a set of edges. How you store it decides which question is
cheap: "are u and v joined?" or "who is u joined to?". Those two questions
have different answers, and the gap between them is a factor of n.

Both costs below are exact counts -- slots allocated and slots probed -- so
nothing here depends on the machine.
"""
import random

N = 300
TARGET_EDGES = 900


def build_edges(n, target, seed=0):
    """A connected graph: a ring, plus random chords until it has enough
    edges. The ring guarantees connectivity, so no query is trivially
    uninteresting."""
    rng = random.Random(seed)
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    while len(edges) < target:
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    return sorted(edges)


def as_matrix(n, edges):
    """n^2 slots, whether or not the edges exist. One read answers any
    pair question -- including for a pair that is not joined."""
    matrix = [[False] * n for _ in range(n)]
    for u, v in edges:
        matrix[u][v] = True
        matrix[v][u] = True
    return matrix


def as_lists(n, edges):
    """One slot per *edge end*. Answering "are u and v joined?" means
    walking u's list until it is found or exhausted."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def list_probes(adj, u, v):
    probes = 0
    for w in adj[u]:
        probes += 1
        if w == v:
            break
    return probes


def who_is_u_joined_to(adj, matrix, u):
    """The other question, counted both ways."""
    return len(adj[u]), len(matrix[u])


EDGES = build_edges(N, TARGET_EDGES)
MATRIX = as_matrix(N, EDGES)
ADJ = as_lists(N, EDGES)
M = len(EDGES)

print(f"a connected graph: {N:,} nodes, {M:,} edges, mean degree "
      f"{2 * M / N:.1f}")
print()
print("storage")
print()
print(f"{'representation':<20}{'slots':>14}{'slots per edge':>17}")
print("-" * 51)
print(f"{'adjacency matrix':<20}{N * N:>14,}{N * N / M:>17.1f}")
print(f"{'adjacency lists':<20}{2 * M:>14,}{2 * M / M:>17.1f}")
print()
print(f"  the matrix needs {N * N / (2 * M):.0f}x the slots for the same graph")
print()
print("The matrix is the same size whether the graph has 900 edges or")
print("90,000, because it allocates a slot for every pair that *could*")
print("exist. The list allocates a slot for every edge that *does*. On a")
print("sparse graph -- and almost every graph that models something real is")
print("sparse -- that is the whole argument.")
print()
print()
print("cost of asking 'are u and v joined?', over every ordered pair")
print()


def count_pair_probes(matrix, adj, n):
    """Exact totals over all n^2 ordered pairs, both representations."""
    matrix_total = 0
    list_total = 0
    list_found = 0
    for u in range(n):
        for v in range(n):
            matrix_total += 1
            probes = list_probes(adj, u, v)
            list_total += probes
            if probes and adj[u][probes - 1] == v:
                list_found += 1
    return matrix_total, list_total, list_found


matrix_total, list_total, list_found = count_pair_probes(MATRIX, ADJ, N)
print(f"{'representation':<20}{'total probes':>14}{'per query':>12}"
      f"{'worst case':>13}")
print("-" * 59)
print(f"{'adjacency matrix':<20}{matrix_total:>14,}{matrix_total / N ** 2:>12.2f}"
      f"{1:>13,}")
print(f"{'adjacency lists':<20}{list_total:>14,}{list_total / N ** 2:>12.2f}"
      f"{max(len(a) for a in ADJ):>13,}")
print()
print("One read either way, for a pair that is joined -- the matrix wins")
print("nothing there. The gap is in the *other* case. When the edge is")
print("absent, the matrix still answers in one read, and the list has to")
print("walk the whole neighbour list before it can say no. That is why the")
print("list column averages well above 1 and the matrix column is exactly")
print("1.00.")
print()
print()
print("cost of asking 'who is u joined to?', over every node")
print()
matrix_scan = sum(who_is_u_joined_to(ADJ, MATRIX, u)[1] for u in range(N))
list_scan = sum(who_is_u_joined_to(ADJ, MATRIX, u)[0] for u in range(N))
print(f"{'representation':<20}{'total probes':>14}{'per node':>12}")
print("-" * 46)
print(f"{'adjacency matrix':<20}{matrix_scan:>14,}{matrix_scan / N:>12.1f}")
print(f"{'adjacency lists':<20}{list_scan:>14,}{list_scan / N:>12.1f}")
print()
print("And now it reverses completely. Listing a node's neighbours means")
print("scanning all n slots of its matrix row and discarding the empty ones;")
print("the list *is* the answer, and iterating it touches nothing else. Any")
print("algorithm whose inner loop is 'for each neighbour of u' -- which is")
print("every traversal in this chapter -- is paying the matrix's cost on")
print("every single step.")
print()
print("So the rule is not 'lists are better'. It is that the matrix buys")
print("constant-time *pair* queries by paying n^2 memory and n per neighbour")
print("scan, and a dense graph is the only thing that makes that trade good.")
print()
print(f"  pairs that are joined      : {list_found:,}")
print(f"  density                    : {2 * M / (N * (N - 1)):.4f}")
print(f"  matrix slots per real edge : {N * N / M:.0f}")
```

```text
a connected graph: 300 nodes, 900 edges, mean degree 6.0

storage

representation               slots   slots per edge
---------------------------------------------------
adjacency matrix            90,000            100.0
adjacency lists              1,800              2.0

  the matrix needs 50x the slots for the same graph

The matrix is the same size whether the graph has 900 edges or
90,000, because it allocates a slot for every pair that *could*
exist. The list allocates a slot for every edge that *does*. On a
sparse graph -- and almost every graph that models something real is
sparse -- that is the whole argument.


cost of asking 'are u and v joined?', over every ordered pair

representation        total probes   per query   worst case
-----------------------------------------------------------
adjacency matrix            90,000        1.00            1
adjacency lists            534,898        5.94           12

One read either way, for a pair that is joined -- the matrix wins
nothing there. The gap is in the *other* case. When the edge is
absent, the matrix still answers in one read, and the list has to
walk the whole neighbour list before it can say no. That is why the
list column averages well above 1 and the matrix column is exactly
1.00.


cost of asking 'who is u joined to?', over every node

representation        total probes    per node
----------------------------------------------
adjacency matrix            90,000       300.0
adjacency lists              1,800         6.0

And now it reverses completely. Listing a node's neighbours means
scanning all n slots of its matrix row and discarding the empty ones;
the list *is* the answer, and iterating it touches nothing else. Any
algorithm whose inner loop is 'for each neighbour of u' -- which is
every traversal in this chapter -- is paying the matrix's cost on
every single step.

So the rule is not 'lists are better'. It is that the matrix buys
constant-time *pair* queries by paying n^2 memory and n per neighbour
scan, and a dense graph is the only thing that makes that trade good.

  pairs that are joined      : 1,800
  density                    : 0.0201
  matrix slots per real edge : 100
```

The matrix allocates a slot for every pair that *could* be joined; the list allocates one per edge
that *is*. On this graph that is 90,000 slots against 1,800 -- a factor of fifty -- and the ratio
gets worse as the graph gets sparser, which is the direction every graph that models something real
goes.

But the matrix is not a mistake, and the second table is why. Asking "are these two joined?" costs
exactly one read in a matrix, whether or not the edge exists. In a list it costs an average of 5.94
reads, because an absent edge means walking the whole neighbour list before you can say no.

The third table is the one that decides it for this chapter. Every traversal here has "for each
neighbour of u" in its inner loop, and that costs 300 probes per node in a matrix against 6 in a
list. Since the inner loop runs once per node, the matrix is paying its n² price on every step of
every algorithm. Use a matrix when the graph is dense, or when the question is a pair query; use
lists for everything else.

## Breadth-first search

BFS explores in rings, and that single fact gives it three things at once.

```python run
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
```

```text
Part 1 -- a small graph, read out loud

  visit order : you -> alice -> bob -> claire -> peggy -> anuj -> thom -> jonny

  node      level   reached from
  ------------------------------
  you           0   (start)
  alice         1   you
  bob           1   you
  claire        1   you
  anuj          2   bob
  jonny         2   claire
  peggy         2   alice
  thom          2   claire

  path to thom : you -> claire -> thom   (2 steps)
  edge probes  : 8

Two different things are being read off one traversal, and it is worth
keeping them apart. The *order* is what BFS is doing. The *level* is a
by-product, and it is the answer to 'how far away is this?' -- the
level of a node is its shortest distance from the start, in edges,
because BFS cannot reach a node at level 3 before it has finished
level 2.

The parent map is the third by-product, and it is the one that turns a
distance into an actual route. Nothing extra was computed to get it:
the parent was recorded at the moment the node was first discovered,
and 'first discovered' means 'discovered by a shortest route'.


Part 2 -- a grid, where the same code answers a real question

a 200x200 grid, 11,210 cells walled off
  open cells                 : 28,790
  the straight-line distance : 398 steps
  shortest route             : 400 steps
  detour forced by the walls : 2 steps
  cells dequeued             : 28,405
  edge probes                : 82,085
  probes per open cell       : 2.85

The route is longer than the straight line, because the walls do not
allow a straight line. BFS found the shortest way around them without
ever considering the straight line, or the goal's position, or anything
at all about where it was going.

That is simultaneously BFS's strength and its weakness, and the second
half of this chapter is about the weakness. Expanding equally in every
direction is what makes it provably correct on an unweighted graph, and
it is also what makes it explore most of the grid to reach a corner. A
heuristic is the fix, and it costs the proof.

  first three steps of the route: [(0, 0), (1, 0), (2, 0)]
  last three steps of the route : [(198, 198), (198, 199), (199, 199)]
```

Read the small graph carefully, because three separate outputs come out of one traversal and it is
worth keeping them apart. The visit *order* is what BFS is doing. The *level* of each node is the
answer to "how far away is this?", and it is the shortest distance in edges, because BFS cannot
reach a node at level 3 before it has finished level 2. And the *parent* map is what turns a distance
into an actual route -- recorded at the moment each node was first discovered, which is by definition
the moment it was discovered by a shortest route.

Nothing extra was computed for the parent map. That is the point of it: the information was already
there in the traversal, and writing it down is what makes BFS a pathfinder rather than a visitor.

The grid is the same code answering a question with a right answer. The route is 400 steps against a
straight-line distance of 398, so the walls forced a detour of exactly 2 -- and BFS found the
shortest possible detour without ever considering the straight line, the goal's position, or
anything at all about where it was going. It expanded 28,405 of the 28,790 open cells to do it.

That is BFS's strength and its weakness in one number. Expanding equally in every direction is what
makes it provably correct on an unweighted graph, and it is also why reaching a corner cost it
almost the entire grid. The second half of this chapter is about paying less, and about what that
costs.

## Depth-first search

DFS is the traversal you get for free from a recursive function: visit a node, then visit each of its
neighbours in turn. It is shorter than BFS, it answers different questions, and it has two traps.

```python run
#!/usr/bin/env python3
"""Chapter 47 demo -- depth-first search, and the traps it has.

DFS is the traversal you get for free from a recursive function. It is
shorter than BFS and it answers different questions -- connectivity, cycles,
topological order -- but it has failure modes BFS does not: it follows a path
to its end before backing up, so it can exhaust the call stack, and the
obvious iterative rewrite does *not* reproduce the recursive order.
"""
import random
from collections import deque

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


def dfs_recursive(adj, node, seen=None, order=None):
    """The version everybody writes first. The recursion *is* the stack."""
    if seen is None:
        seen, order = set(), []
    seen.add(node)
    order.append(node)
    for w in adj[node]:
        if w not in seen:
            dfs_recursive(adj, w, seen, order)
    return order


def dfs_stack(adj, start):
    """The obvious rewrite: push the neighbours, pop the next one. It is a
    correct traversal and it is *not* the same traversal."""
    seen = set()
    order = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for w in adj[node]:
            if w not in seen:
                stack.append(w)
    return order


def dfs_stack_matching(adj, start):
    """Push the neighbours in reverse and the order comes out the same as the
    recursive version. One `reversed()` is the whole difference."""
    seen = set()
    order = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for w in reversed(adj[node]):
            if w not in seen:
                stack.append(w)
    return order


recursive = dfs_recursive(FRIENDS, "you")
naive = dfs_stack(FRIENDS, "you")
matching = dfs_stack_matching(FRIENDS, "you")
print("Part 1 -- the iterative rewrite is not the same traversal")
print()
print(f"  recursive             : {' -> '.join(recursive)}")
print(f"  stack, pushed in order: {' -> '.join(naive)}")
print(f"  stack, pushed reversed: {' -> '.join(matching)}")
print()
print(f"  naive matches recursive?    {naive == recursive}")
print(f"  reversed matches recursive? {matching == recursive}")
print()
print("Both stack versions visit every node exactly once, so both are")
print("legitimate depth-first traversals, and only one of them is *the same*")
print("traversal as the recursive version. The reason is a stack's defining")
print("property: it returns the last thing you put in. Recursive DFS recurses")
print("into the first neighbour; the naive stack pops the last one. Reversing")
print("the push order cancels that out exactly.")
print()
print("This matters because algorithms get built on the order. A topological")
print("sort reads the *finish* order, and a finish order that depends on")
print("which way the stack was filled is a different answer -- still valid,")
print("sometimes, and not the one you proved correct.")
print()
print()
print("Part 2 -- the recursion limit is a real limit")
print()
CHAIN = 5_000
chain = {i: [i + 1] for i in range(CHAIN - 1)}
chain[CHAIN - 1] = []


def descend(adj, node, seen, depth, record):
    """The same traversal, but it reports how deep it got before it stopped."""
    seen.add(node)
    record[0] = max(record[0], depth)
    for w in adj[node]:
        if w not in seen:
            descend(adj, w, seen, depth + 1, record)


record = [0]
failed = False
try:
    descend(chain, 0, set(), 0, record)
except RecursionError:
    failed = True
print(f"  a chain graph of {CHAIN:,} nodes")
print(f"  recursive DFS raised RecursionError : {failed}")
print(f"  deepest call it reached             : {record[0]:,}")
print()
stack = [0]
seen = set()
while stack:
    node = stack.pop()
    if node in seen:
        continue
    seen.add(node)
    stack.extend(w for w in chain[node] if w not in seen)
print(f"  iterative DFS visited               : {len(seen):,} of {CHAIN:,}")
print()
print("The recursive version does not run out of memory, it runs out of")
print("*call frames*, and the default limit is a thousand. A thousand-deep")
print("recursion is easy to reach by accident: a linked list, a file tree, a")
print("deep JSON document, or a graph with one long path in it.")
print()
print("The fix is not 'raise the limit'. A raised limit is a bigger number")
print("with the same failure mode, and CPython's stack can overflow for real")
print("-- a segfault, not an exception -- before the counter stops you.")
print("Rewrite the traversal with an explicit stack. That is the version that")
print("scales, and it is also the version you can inspect.")
print()
print()
print("Part 3 -- what each traversal actually holds in memory")
print()


def neighbours(rows, cols, walls, cell):
    r, c = cell
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in walls:
            yield (nr, nc)


def bfs_peak(rows, cols, walls, start, goal):
    """BFS holds the frontier -- the widest ring it has to remember."""
    level = {start: 0}
    queue = deque([start])
    peak = 0
    while queue:
        peak = max(peak, len(queue))
        u = queue.popleft()
        if u == goal:
            break
        for w in neighbours(rows, cols, walls, u):
            if w not in level:
                level[w] = level[u] + 1
                queue.append(w)
    return peak, len(level)


def dfs_peak_marked_on_pop(rows, cols, walls, start, goal):
    """The textbook iterative DFS: push every unvisited neighbour, and mark a
    node only when it is popped. Duplicates pile up in the stack."""
    seen = set()
    stack = [start]
    peak = 0
    while stack:
        peak = max(peak, len(stack))
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        if u == goal:
            break
        for w in neighbours(rows, cols, walls, u):
            if w not in seen:
                stack.append(w)
    return peak, len(seen)


def dfs_peak_marked_on_push(rows, cols, walls, start, goal):
    """Mark on push instead. Nothing is ever queued twice, so the stack holds
    the current path and its siblings -- which is what 'DFS is O(depth)' means."""
    seen = {start}
    stack = [start]
    peak = 0
    while stack:
        peak = max(peak, len(stack))
        u = stack.pop()
        if u == goal:
            break
        for w in neighbours(rows, cols, walls, u):
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return peak, len(seen)


rng = random.Random(11)
ROWS = COLS = 150
WALLS = {(r, c) for r in range(ROWS) for c in range(COLS)
         if rng.random() < 0.28}
WALLS.discard((0, 0))
WALLS.discard((ROWS - 1, COLS - 1))
START, GOAL = (0, 0), (ROWS - 1, COLS - 1)

b_peak, b_seen = bfs_peak(ROWS, COLS, WALLS, START, GOAL)
p_peak, p_seen = dfs_peak_marked_on_pop(ROWS, COLS, WALLS, START, GOAL)
s_peak, s_seen = dfs_peak_marked_on_push(ROWS, COLS, WALLS, START, GOAL)

print(f"  a {ROWS}x{COLS} grid, {len(WALLS):,} walls, from {START} to {GOAL}")
print()
print(f"  {'traversal':<34}{'peak held':>11}{'visited':>10}")
print("  " + "-" * 55)
print(f"  {'BFS (frontier)':<34}{b_peak:>11,}{b_seen:>10,}")
print(f"  {'DFS, marked on pop (the usual rewrite)':<34}{p_peak:>11,}{p_seen:>10,}")
print(f"  {'DFS, marked on push':<34}{s_peak:>11,}{s_seen:>10,}")
print()
print(f"  the naive DFS stack is {p_peak / b_peak:.1f}x the BFS frontier")
print(f"  marking on push cuts it by {p_peak / s_peak:.1f}x")
print()
print("This is the folklore turned inside out, and it is worth reading")
print("carefully. The textbook claim is 'BFS holds the frontier, DFS holds the")
print("path, so DFS uses less memory' -- and the middle row is the version")
print("almost everybody writes, and it holds *more* than BFS does.")
print()
print("The reason is that it marks a node when it is *popped* rather than when")
print("it is pushed, so a node with three unvisited neighbours is queued three")
print("times before any of them is examined. Those duplicates are never")
print("traversed -- the `if u in seen: continue` at the top throws them away --")
print("but they are in the list, and the list is the memory.")
print()
print("Marking on push removes them, and now the stack really does hold the")
print("current path plus the siblings still to try. On a grid that is still")
print("wider than BFS's frontier, because a path is long and a ring is short")
print("-- so the folklore is right about the *shape* of the memory and wrong")
print("about which of the two is smaller here.")
print()
print("The transferable rule is about the marking, not the traversal: decide")
print("when a node is considered visited, and do it as early as you can. Every")
print("duplicate in that stack was work you paid for and threw away.")
```

```text
Part 1 -- the iterative rewrite is not the same traversal

  recursive             : you -> alice -> peggy -> bob -> anuj -> claire -> thom -> jonny
  stack, pushed in order: you -> claire -> jonny -> thom -> bob -> peggy -> anuj -> alice
  stack, pushed reversed: you -> alice -> peggy -> bob -> anuj -> claire -> thom -> jonny

  naive matches recursive?    False
  reversed matches recursive? True

Both stack versions visit every node exactly once, so both are
legitimate depth-first traversals, and only one of them is *the same*
traversal as the recursive version. The reason is a stack's defining
property: it returns the last thing you put in. Recursive DFS recurses
into the first neighbour; the naive stack pops the last one. Reversing
the push order cancels that out exactly.

This matters because algorithms get built on the order. A topological
sort reads the *finish* order, and a finish order that depends on
which way the stack was filled is a different answer -- still valid,
sometimes, and not the one you proved correct.


Part 2 -- the recursion limit is a real limit

  a chain graph of 5,000 nodes
  recursive DFS raised RecursionError : True
  deepest call it reached             : 998

  iterative DFS visited               : 5,000 of 5,000

The recursive version does not run out of memory, it runs out of
*call frames*, and the default limit is a thousand. A thousand-deep
recursion is easy to reach by accident: a linked list, a file tree, a
deep JSON document, or a graph with one long path in it.

The fix is not 'raise the limit'. A raised limit is a bigger number
with the same failure mode, and CPython's stack can overflow for real
-- a segfault, not an exception -- before the counter stops you.
Rewrite the traversal with an explicit stack. That is the version that
scales, and it is also the version you can inspect.


Part 3 -- what each traversal actually holds in memory

  a 150x150 grid, 6,415 walls, from (0, 0) to (149, 149)

  traversal                           peak held   visited
  -------------------------------------------------------
  BFS (frontier)                            142    15,868
  DFS, marked on pop (the usual rewrite)      4,297    10,472
  DFS, marked on push                     2,769    11,324

  the naive DFS stack is 30.3x the BFS frontier
  marking on push cuts it by 1.6x

This is the folklore turned inside out, and it is worth reading
carefully. The textbook claim is 'BFS holds the frontier, DFS holds the
path, so DFS uses less memory' -- and the middle row is the version
almost everybody writes, and it holds *more* than BFS does.

The reason is that it marks a node when it is *popped* rather than when
it is pushed, so a node with three unvisited neighbours is queued three
times before any of them is examined. Those duplicates are never
traversed -- the `if u in seen: continue` at the top throws them away --
but they are in the list, and the list is the memory.

Marking on push removes them, and now the stack really does hold the
current path plus the siblings still to try. On a grid that is still
wider than BFS's frontier, because a path is long and a ring is short
-- so the folklore is right about the *shape* of the memory and wrong
about which of the two is smaller here.

The transferable rule is about the marking, not the traversal: decide
when a node is considered visited, and do it as early as you can. Every
duplicate in that stack was work you paid for and threw away.
```

The first trap is in the first table. Both stack versions visit every node exactly once, so both are
legitimate depth-first traversals -- and only one of them is *the same* traversal as the recursive
version. A stack returns the last thing you put in; recursive DFS recurses into the *first*
neighbour. So the naive rewrite pops the last neighbour instead, and reversing the push order
cancels that out exactly.

This matters more than it looks, because algorithms get built on the order. A topological sort reads
the *finish* order. A finish order that depends on which way the stack was filled is a different
answer -- sometimes still valid, and not the one you proved correct.

The second trap is that DFS follows a path to its end before backing up. On a chain of 5,000 nodes
the recursive version does not run out of memory, it runs out of *call frames*, and the default
limit stops it at a depth of 998. The fix is not to raise the limit: a raised limit is a bigger
number with the same failure mode, and CPython's stack can overflow for real -- a segfault rather
than an exception -- before the counter stops you. Rewrite the traversal with an explicit stack.

The third table is the part that does not match the folklore, and it is worth reading twice. The
textbook claim is "BFS holds the frontier, DFS holds the path, so DFS uses less memory". The middle
row is the version almost everybody writes, and it holds **more** than BFS does -- 4,297 entries
against a frontier of 142.

The reason is the marking, not the traversal. That version marks a node as visited when it is
*popped*, so a node with three unvisited neighbours is queued three times before any of them is
examined. Those duplicates are never traversed -- the `if u in seen: continue` at the top throws them
away -- but they are in the list, and the list is the memory. Marking on push removes them, and the
stack really does hold the current path plus the siblings still to try.

The transferable rule is about the marking: decide when a node counts as visited, and decide it as
early as you can. Every duplicate in that stack was work you paid for and threw away.

## The same graph, two questions

"Find a route from A to B" has two meanings, and the two traversals answer different ones.

```python run
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
```

```text
a 40x40 grid, 404 walls, from (0, 0) to (39, 39)
the straight-line distance is 78 steps

traversal      steps  vs straight line   cells seen    probes
-------------------------------------------------------------
BFS               78                 0        1,186     3,486
DFS              380               302        1,057     2,262

  DFS route is 4.8x the length of the BFS route
  both reach the goal: True

Both traversals visit the goal, and only one of them arrives by a
sensible route. The DFS route is not a bug -- it is exactly what
'follow the first unexplored neighbour' means. DFS commits to a
direction and does not reconsider until it is forced to, so it can
walk the entire grid before it happens to fall into the goal.

That is why the choice of traversal is a choice about the *question*,
not about speed. On this grid DFS looked at fewer cells, because it
committed early and got lucky; on a graph where the goal is behind a
wall it would look at more, and the route would still be bad.

The rule to carry: if the edge count matters, it is BFS and only BFS.
DFS is for questions where the *order* is the answer -- is this
connected, does it contain a cycle, in what order must these run --
and it says nothing useful about distance.

  first 4 cells of the BFS route: [(0, 0), (1, 0), (2, 0), (3, 0)]
  first 4 cells of the DFS route: [(0, 0), (0, 1), (0, 2), (0, 3)]
  routes are identical: False
```

Both reach the goal. BFS arrives in 78 steps, which is exactly the straight-line distance. DFS
arrives in 380 steps -- 302 more than the shortest route -- and it is not a bug. It is precisely what
"follow the first unexplored neighbour and do not reconsider" means, and on this grid DFS looked at
*fewer* cells, because it committed early and got lucky.

That is why the choice of traversal is a choice about the question and not about speed. If the edge
count matters, it is BFS and only BFS. DFS is for questions where the *order* is the answer -- is
this connected, does it contain a cycle, in what order must these run -- and it says nothing useful
about distance.

## Ordering a graph

A topological order is an ordering in which every edge points forwards. It exists if and only if the
graph has no cycle, which makes topological sorting the standard way to *detect* a cycle in a
dependency graph -- and the reason a build system can tell you that two modules depend on each other
instead of looping until it runs out of memory.

```python run
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
```

```text
9 courses, 12 prerequisite edges

  the graph, as 'prerequisite -> what it unlocks'
    intro      -> algebra, systems
    algebra    -> calculus, stats, compilers, physics
    systems    -> compilers, graphics
    calculus   -> physics, graphics, ml
    stats      -> ml

  Kahn's algorithm  : intro -> algebra -> systems -> calculus -> stats -> compilers -> physics -> graphics -> ml
  DFS post-order    : intro -> systems -> algebra -> compilers -> stats -> calculus -> ml -> graphics -> physics

  the two orders agree        : False
  Kahn's order is valid       : True
  DFS order is valid          : True
  Kahn covered every node     : True
  Kahn's edge probes          : 12 of 12 edges
  DFS's edge probes           : 12 of 12 edges

The two algorithms disagree about the order, and both are right. A
topological order is not unique -- 'algebra before physics' is a
constraint, and whether 'stats' comes before or after 'physics' is
not specified by anything. Only the *relative* order of an edge's two
endpoints is pinned, which is what `is_valid` checks and the only
thing a topological sort promises.

Both are O(V + E): every node is enqueued once and every edge examined
once, which is why the probe counts match the edge count exactly. Kahn
spends O(V) memory on the in-degree table; DFS spends it on the
recursion stack, and on a deep graph that is where the recursion limit
from the previous section comes back to bite.


Now the case that makes topological sorting worth knowing for: a cycle

  compilers now requires graphics, and graphics requires compilers

  Kahn's order        : intro -> algebra -> systems -> calculus -> stats -> physics -> ml
  covered every node  : False
  nodes it could not place (2): compilers, graphics

The algorithm did not hang and it did not raise. It ran out of nodes
with no prerequisites and stopped, which is the whole cycle test: a
directed graph is acyclic if and only if a topological sort consumes
all of it. Everything left over is on a cycle or downstream of one --
and here it is exactly the two nodes of the cycle, because nothing
depends on them.

That distinction is the difference between a useful error and a
useless one. 'Dependency cycle detected' sends somebody hunting;
'compilers -> graphics -> compilers' does not. The leftover set is
free -- it is exactly the nodes the algorithm never reached.

  is the stuck set a superset of the cycle? True
  the same test on the acyclic graph    : True
```

The two algorithms disagree about the order, and both are right. A topological order is not unique:
"algebra before physics" is a constraint, and whether statistics comes before or after physics is
specified by nothing. Only the *relative* order of an edge's two endpoints is pinned, which is what
the validity check tests and the only thing a topological sort promises.

Both are O(V + E) -- every node is enqueued once and every edge examined once, which is why the probe
counts match the edge count exactly. Kahn's algorithm spends O(V) memory on an in-degree table; DFS
spends it on the recursion stack, which is where the previous section's recursion limit comes back.

Then the cycle, and this is the case that makes the whole technique worth knowing. Kahn's algorithm
does not hang and does not raise. It runs out of nodes with no prerequisites and stops -- and a
directed graph is acyclic if and only if a topological sort consumes all of it. Everything left over
is on a cycle or downstream of one.

## Weighted graphs: Dijkstra

Dijkstra is BFS with a priority queue instead of a queue. That one change is what lets it handle
weights, and it is also where all the cost goes.

```python run
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
```

```text
Part 1 -- a small weighted graph

  the graph, as 'from: (to, weight)'
    home    shop:4, school:9
    shop    home:4, school:2, gym:7
    school  home:9, shop:2, gym:3, work:8
    gym     shop:7, school:3, work:2
    work    school:8, gym:2

  node     distance   route
  --------------------------------------------
  home            0   home
  shop            4   home -> shop
  school          6   home -> shop -> school
  gym             9   home -> shop -> school -> gym
  work           11   home -> shop -> school -> gym -> work

  heap pushes        : 7
  heap pops          : 8
  stale pops         : 3

Look at the distances rather than the code. Every one of them is
final the moment it is popped, and that is Dijkstra's actual claim: the
next node out of the heap is the nearest node not yet settled. The heap
is not an optimisation of the search, it *is* the search -- and the
proof depends on every edge weight being non-negative, which the next
two sections take apart.

The stale pops are the price of the interface. When a shorter route to
a node is found, the old entry cannot be deleted from the middle of a
heap, so a second entry is pushed and the first one is recognised as
obsolete by comparing its distance with the best known. That is why
there are more pushes than there are nodes: a node can be pushed more
than once, and every push after the first is a duplicate waiting to be
thrown away.


Part 2 -- the same job with no heap at all

a 40x40 grid, 1,600 nodes, 3,120 edges, weights 1..9

implementation             work units   per node
------------------------------------------------
heap: edge relaxations          6,240        3.9
heap: pushes                    2,004        1.3
heap: pops                      2,005        1.3
  of which stale                  405        0.3
array: nearest-node scans    2,560,000     1600.0
array: edge relaxations         6,240        3.9

  the two agree on every distance : True
  array scans / heap pops         : 1276.8x

Both implementations are Dijkstra and both are correct; only the data
structure differs. The heap's work is proportional to the *edges* -- it
touches a node when an edge improves it, and never otherwise. The
array's work is proportional to the *nodes squared*, because finding
the nearest unfinished node means looking at all of them, every time,
whether or not any of them has changed.

That is the whole argument for the heap, and it has an edge case worth
knowing. On a dense graph the number of edges approaches n^2, so both
are n^2 and the heap's log factor makes it *worse*. The heap wins on
sparse graphs -- which is what a road network, a dependency tree and a
social graph all are.

  heap entries pushed in total    : 2,004
  stale entries thrown away       : 405 (20.2% of pushes)
  relaxations that improved a node: 2,003
```

Every distance in that first table is final the moment it is popped, and that is Dijkstra's actual
claim: the next node out of the heap is the nearest node not yet settled. The heap is not an
optimisation of the search, it *is* the search.

The stale pops are the price of the interface. A binary heap has no "decrease this key" operation,
so when a shorter route to a node is found, a second entry is pushed and the first is recognised as
obsolete by comparing its distance with the best known. That is why there are more pushes than there
are nodes -- 2,004 pushes for 1,600 nodes -- and why 405 entries were thrown away after being
popped.

The second table is the argument for the heap, and it has an edge case worth knowing. The heap's work
is proportional to the *edges*; the array's nearest-node scan is proportional to the *nodes squared*,
because finding the nearest unfinished node means looking at all of them every time, whether or not
any of them has changed. That is 2,560,000 scans against 2,005 pops.

But on a *dense* graph the edge count approaches n², so both are n² and the heap's log factor makes
it worse. The heap wins on sparse graphs -- which is what a road network, a dependency tree and a
social graph all are.

## The fewest steps and the cheapest route

BFS minimises the number of edges. Dijkstra minimises the sum of the weights. On an unweighted graph
those are the same question -- which is exactly why BFS is a special case of Dijkstra -- and on a
weighted graph they are not.

```python run
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
```

```text
Part 1 -- four towns, one edge that changes everything

    A   B:1, C:4
    B   A:1, C:1, D:5
    C   A:4, B:1, D:1
    D   B:5, C:1

  fewest edges (BFS)     : A -> B -> D   2 edges, weight 6
  cheapest (Dijkstra)    : A -> B -> C -> D   3 edges, weight 3

BFS is not confused. It was asked for the route with the fewest edges
and it returned the route with the fewest edges. The mistake is in the
question: on a road network nobody wants fewer roads, they want fewer
miles. A and C are joined by one edge of weight 4, and by two edges of
weight 1 each -- so the answer that looks worse is twice as good.

The general statement is that BFS is Dijkstra with every weight set to
1. That is why the two algorithms are the same shape and why only one
of them is correct on a weighted graph.


Part 2 -- what that costs on a real road network

a 40x40 grid, 1,600 nodes, weights 1..9, all from one corner

  nodes where the BFS route costs more than the cheapest: 1,577 of 1,600 (98.6%)
  total excess weight across all routes  : 120,594
  mean excess per affected node          : 76.5
  worst single node                      : +194 (node 1595)

99 percent of the nodes are reached by a route that is
longer than it needs to be, and the excess is not a rounding error --
the worst node is reached by a route several times more expensive than
the cheapest one. And notice what BFS did *not* do: it never raised,
never warned, and produced a route that is genuinely the
fewest-edges route. There is no signal anywhere in the output that the
answer is wrong.

That is the failure mode to remember. A wrong shortest path looks
exactly like a right one -- it is a list of nodes, it starts at the
source and ends at the target, and every consecutive pair really is
joined by an edge. The only way to catch it is to know which question
you asked.

  shortest hop count to the far corner : 78
  cheapest weight to the far corner    : 207
```

BFS is not confused. It was asked for the route with the fewest edges and it returned the route with
the fewest edges. The mistake is in the question: on a road network nobody wants fewer roads, they
want fewer miles. The two-edge route costs 6 and the three-edge route costs 3, so the answer that
looks worse is twice as good.

The second table is what that costs at scale. 98.6% of the nodes are reached by a route that is
longer than it needs to be, the total excess across the grid is 120,594, and the worst single node is
reached by a route costing 194 more than the cheapest one.

And notice what BFS did *not* do. It never raised, never warned, and produced a route that is
genuinely the fewest-edges route. A wrong shortest path is a list of nodes that starts at the source,
ends at the target, and has every consecutive pair genuinely joined by an edge. The only way to
catch it is to know which question you asked.

## The assumption Dijkstra is standing on

Dijkstra settles a node when it comes out of the heap, and the correctness proof says that is safe
*because every edge weight is non-negative*. Remove that and the algorithm still runs, still
terminates, and returns a wrong answer.

```python run
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
```

```text
the graph

    S -> A   weight   1
    S -> B   weight   2
    B -> A   weight  -2
    A -> T   weight   1

  one of those weights is negative, and B -> A is the only way to
  reach A for less than 1.

  Dijkstra settled the nodes in order: S -> A -> B -> T

  node    Dijkstra  Bellman-Ford   agree
  --------------------------------------
  S              0             0    True
  A              1             0   False
  B              2             2    True
  T              2             1   False

  Bellman-Ford rounds used : 2 of 3 allowed

The true cheapest route to T is S -> B -> A -> T, and it costs 2 - 2 + 1
= 1. Dijkstra returns 2, because of the order it settled the nodes in:
A came out of the heap at distance 1 and was declared final, and by the
time B had been settled it was too late to revise A. The negative edge
was discovered *after* the node it improves had been frozen.

That is the whole content of the non-negative assumption. Dijkstra's
greedy step says 'the nearest unsettled node is final', and the proof
of that step is: any other route to it would have to leave through a
node that is already settled, and every edge adds a non-negative
amount, so no detour can be cheaper. A negative edge makes a detour
cheaper, and the argument collapses.

Nothing in the output says so. Both numbers are plausible, one is
wrong, and the algorithm had no way to know -- it never computes the
quantity that would tell it.


Part 2 -- Bellman-Ford's second job

  adding one more edge: T -> B  weight -5

                                rounds used  negative cycle
  ---------------------------------------------------------
  the graph above                         2           False
  with T -> B added                       3            True

The second graph has a cycle -- B -> A -> T -> B -- whose total weight
is -2 + 1 - 5 = -6. A negative cycle means there is no shortest path at
all: you can go round the loop again and pay less, forever, so the
'shortest distance' to T is unbounded below and is not a number.

Bellman-Ford reports that for the cost of one extra pass over the
edges. After V-1 rounds every shortest path has been found -- because a
shortest path visits each node at most once -- so if a V-th round can
still improve something, the only explanation is a negative cycle.

That is why the algorithm survives. It is slower than Dijkstra, and it
is the only one of the two that can answer 'is this graph even
well-posed?' -- which is a question you want answered before you trust
a route, a price, or a schedule.

  V - 1 = 3 rounds is the guarantee; the first graph settled in
  2 rounds, and the second used all 3
  Dijkstra on the cyclic graph : T = 2, and it terminates without complaint
```

The true cheapest route to T costs 1, and Dijkstra returns 2. A came out of the heap at distance 1
and was declared final; by the time B had been settled it was too late to revise A. The negative edge
was discovered *after* the node it improves had been frozen.

That is the whole content of the assumption. Dijkstra's greedy step says "the nearest unsettled node
is final", and the proof is: any other route to it would have to leave through a node that is already
settled, and every edge adds a non-negative amount, so no detour can be cheaper. A negative edge
makes a detour cheaper, and the argument collapses.

Bellman-Ford makes no such assumption, pays for it with V-1 rounds over every edge, and gets the
negative-cycle test for free. A negative cycle means there is no shortest path at all -- you can go
round the loop again and pay less, forever -- and "the shortest distance is not a number" is a
question you want answered before you trust a route, a price, or a schedule.

## A\*: Dijkstra with an opinion

Dijkstra expands in rings because it has no idea where the target is. A\* adds a heuristic -- an
estimate of the remaining distance -- to the priority, and the search leans towards the goal.

```python run
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
```

```text
a 60x60 grid, 550 walls (15%)
the straight-line distance is 118 steps

search                          route  expanded  vs Dijkstra
------------------------------------------------------------
Dijkstra (h = 0)                  118     3,047         1.0x
A* (Manhattan, shallow ties)      118     2,389         1.3x
A* (Manhattan, deep ties)         118       294        10.4x
A* (Manhattan x 3, shallow)       134       144        21.2x

Read the second row first, because it is the one that does not match
the textbook. An admissible heuristic, correct code, optimal route --
and 1.3 times fewer cells expanded than Dijkstra. All that
work for almost nothing.

The reason is ties. `f = g + h` is the estimated total cost of a route
through a cell, and near the optimum *every* cell on every good route
has the same f -- that is what 'good route' means. So the heap is full
of cells with identical priority, and something has to decide between
them. Pushing `(f, g, cell)` decides in favour of the *smallest* g, and
the smallest g is the cell nearest the start -- so the search expands
outwards in rings, which is precisely what Dijkstra did. The heuristic
is in the arithmetic and absent from the behaviour.

Row three changes one thing: on an equal f, the *largest* g comes out
first. Now the search dives towards the goal along whatever route looks
cheapest, and the expansions collapse.

  cells expanded: 2,389 -> 294   (8.1x fewer)
  the route is unchanged, and still optimal: True

Same heuristic, same proof, same answer. The only difference is which
of two equally-good cells is looked at first. This is the single most
valuable thing to know about implementing A* in practice, and it is
invisible in every description of the algorithm -- because the
description is about the arithmetic, and this is about the queue.

The usual refinement is to break ties by the cross-product of the
direction to the goal and the direction to the neighbour, which prefers
a straight line over a staircase. Preferring depth is the cheap version
and gets most of the effect.


Now the other half of the contract, which is about correctness

  search                          route  optimal?
-----------------------------------------------
  Dijkstra (h = 0)                  118      True
  A* (Manhattan, shallow ties)      118      True
  A* (Manhattan, deep ties)         118      True
  A* (Manhattan x 3, shallow)       134     False

Multiplying the estimate by three makes the search even more focused
-- 144 cells, the fewest of the four -- and the route it returns is
16 steps longer than the best one. Manhattan distance is exactly
the true remaining cost on an open four-directional grid, so tripling
it overstates the cost of every route. A* then abandons a route that is
already known to be good in favour of one that merely *looks* good.

That is the admissibility condition: `h(n)` must never exceed the true
remaining cost. It is the price of the speedup, and it is a property of
a function you wrote, not of the algorithm. Dijkstra needs no such
promise because it has no heuristic to be wrong about.

A second condition, consistency, keeps A* from having to re-open cells
it has already settled: `h(u) <= cost(u, v) + h(v)` for every edge. A
consistent heuristic is automatically admissible, and Manhattan
distance on this grid is both. An admissible-but-inconsistent
heuristic still gives the optimal answer; it may just expand a cell
more than once on the way.

And the link back to Chapter 35: the enemy pathfinding there was this
function, on a tilemap, with Manhattan distance as the estimate. A* is
not a different algorithm from Dijkstra. It is Dijkstra with one extra
term in the priority -- and everything that makes it fast is also
everything that makes its correctness depend on a function you supply.

  expanded / pushed: 294 / 510
  open cells in the grid: 3,050
```

Read the second row first, because it is the one that does not match the textbook. An admissible
heuristic, correct code, an optimal route -- and 1.3 times fewer cells expanded than Dijkstra. All
that work for almost nothing.

The reason is ties. `f = g + h` is the estimated total cost of a route through a cell, and near the
optimum *every* cell on every good route has the same `f` -- that is what "good route" means. So the
heap is full of cells with identical priority, and something has to decide between them. Pushing
`(f, g, cell)` decides in favour of the smallest `g`, and the smallest `g` is the cell nearest the
start, so the search expands outwards in rings -- which is precisely what Dijkstra did. The
heuristic is in the arithmetic and absent from the behaviour.

Change one thing -- on an equal `f`, let the *largest* `g` come out first -- and the search dives
towards the goal. The expansions collapse from 2,389 to 294, an 8.1-fold saving, with the same
heuristic, the same proof, and the same optimal route.

:::tip Tie-breaking is not a detail in A\*
Every description of A\* is about the arithmetic, and this is about the queue -- which is why it is
invisible in the literature and decisive in practice. The cheap version is to prefer the deeper node;
the usual refinement is to break ties by the cross-product of the direction to the goal and the
direction to the neighbour, which prefers a straight line over a staircase. Either way, if your A\*
"works but is slow", the heuristic is probably fine and the tie-break is not.
:::

Then the other half of the contract, which is about correctness rather than speed. Multiplying the
estimate by three makes the search even more focused -- 144 cells, the fewest of the four -- and the
route it returns is 16 steps longer than the best one. Manhattan distance is exactly the true
remaining cost on an open four-directional grid, so tripling it overstates every route, and A\*
abandons a route it knows is good in favour of one that merely looks good.

That is the admissibility condition: `h(n)` must never exceed the true remaining cost. It is the price
of the speedup, and it is a property of a function *you* wrote, not of the algorithm. Dijkstra needs
no such promise because it has no heuristic to be wrong about.

## Connected components

Before the harder questions, the simplest one a traversal can answer: how many separate pieces is
this made of? It is the first thing worth asking about any graph you did not build yourself.

```python run
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
```

```text
a 18x56 map, 427 land cells of 1,008

  ######...#.####....##....#...#.#...#.....#..##.##.#..#.#
  ##.##.#..###..###.#.....##..#...##.##.####.###..####.##.
  #.#..#..###.#...#####.##...#.....##...#.......#..#...#.#
  ..##....##.#.#.....#.#....##....##..#..#.#.##..##......#
  .##...#.##.#...##....##.#.....#...#....#.#.###.#.#.#.##.
  #.####.....#......#.....#.#...###...##.####...#..##....#
  ###...###.#....#.######.#............#..##.##..##.#.#.##
  ..#...#.....#...#..#...#.#..#..#.........##....###...#..
  .#...#.#.##...##.##...#....##..#.#..#.#.###.#.#.###....#
  #..##.#.#...#.#.#.#####..#.##....#....###...#...####.#.#
  #..##.###....##.###.#.##..###.....#....#..####.#.##....#
  #..#.#.#...#..#..#....##..#.#...###...#.#..#...#...###..
  #......#.##.###.#.#.#...##...#.#.....#.....######.##.#..
  #.##.##.#..##.##..##.###.....##.##......#######....#..#.
  #...........###...##..#.#.#.#....####.........#......#.#
  .##..##..#...###...#.#.###.##.#....#.###.#..###.##......
  ....###....#.#.###..#..#....#...#..###.#.#..#..#.##.#..#
  .#..#.###...###...#.....##.......##...#.####.##..##..#.#

  components found by a stack : 117
  components found by a queue : 117
  the two partitions are equal: True
  cells accounted for         : 427 of 427 land
  sizes, largest first        : [27, 26, 25, 20, 18, 14, 14, 14, 11, 10, 9, 8, 8, 7, 7, 6, 6, 6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

The two traversals produce exactly the same partition, and that is not
a coincidence -- it is the definition of a connected component. Two
cells are in the same component if some path of land joins them, and
that is a property of the map. The order in which a traversal discovers
them cannot change it.

That is why components are the easy question. Every other question in
this chapter -- how far, how expensive, in what order -- has an answer
that depends on *how* you traversed. This one does not, so the code can
be the simplest version of the traversal with no loss at all.

The cost is one pass over the cells, O(V + E), and it is worth noting
how much of the work is the `seen` set rather than the traversal. Every
land cell is added to it once and tested against it four times, which
is why the flood fill is memory-bound rather than compute-bound.


Part 2 -- the same idea on a graph with no geometry

  400 nodes, 600 random edges, mean degree 3.0
  components                  : 27
  largest component           : 371 nodes (93% of the graph)
  isolated nodes              : 24
  component sizes             : [371, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

A random graph with mean degree 3 is almost entirely one blob with a
handful of stragglers, and that is a fact about random graphs rather
than about this code -- the largest component swallows nearly
everything well before the mean degree reaches 2.

The practical version of this question is asked constantly: is this
network still one network, which accounts are unreachable, does this
migration plan leave anything stranded. All of them are one flood fill
and a count, and the count is the interesting part -- a component of
size 1 is a node that can never talk to anything.

  every land cell reached exactly once: True
  every node reached exactly once    : True
```

The two traversals produce exactly the same partition, and that is not a coincidence -- it is the
definition of a connected component. Two cells are in the same component if some path joins them, and
that is a property of the map; the order in which a traversal discovers them cannot change it. So
this is the one question in the chapter whose answer does not depend on *how* you traversed, and the
code can be the simplest version of the traversal with no loss at all.

The second half is the same idea on a graph with no geometry, and the answer is a fact about random
graphs rather than about the code: with a mean degree of 3, one component swallows 93% of the graph,
and 24 of the nodes are isolated -- reachable from nothing and leading nowhere. The practical version
of the question is asked constantly -- is this network still one network, which accounts are
unreachable, does this migration leave anything stranded -- and a component of size 1 is a node that
can never talk to anything.

## Union-find

A traversal answers "are these two in the same group?" by flood-filling, which means redoing the work
from scratch every time an edge is added. Union-find absorbs the additions and answers incrementally,
and it is fast for a reason worth counting: two independent tricks, each of which is a single line.

```python run
#!/usr/bin/env python3
"""Chapter 47 demo -- union-find, and the two one-line tricks that turn it
from quadratic into almost linear.

Union-find answers one question -- "are these two in the same group?" -- and
takes one instruction: "merge these two groups". It beats a traversal because
it never rebuilds the groups, and it is fast for a reason worth counting:
two independent tricks, each of which is a single line, and each of which
fixes a different failure.
"""


class UnionFind:
    def __init__(self, n, compress=True, by_rank=True):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.compress = compress
        self.by_rank = by_rank
        self.hops = 0

    def find(self, x):
        """Walk to the root, counting the steps. That count *is* the cost."""
        root = x
        while self.parent[root] != root:
            self.hops += 1
            root = self.parent[root]
        if self.compress:
            while self.parent[x] != root:
                self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.by_rank and self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.by_rank and self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


N = 2_000


def chain_then_query(compress, by_rank):
    """The sequence that separates the four variants.

    `union(i + 1, i)` is deliberate. `union(a, b)` hangs the root of `b` under
    the root of `a`, so merging *forwards* builds a chain one link at a time --
    and merging backwards would attach every new node to the same root and
    build a star of depth 1, which is the opposite of the worst case.
    """
    uf = UnionFind(N, compress=compress, by_rank=by_rank)
    for i in range(N - 1):
        uf.union(i + 1, i)
    uf.hops = 0
    for i in range(N):
        uf.find(0)
    return uf.hops


print(f"{N:,} elements, merged into one chain, then {N:,} finds of the far end")
print()
print(f"{'variant':<34}{'parent hops':>13}{'per find':>11}")
print("-" * 58)
variants = [
    ("no compression, no union by rank", False, False),
    ("union by rank only", False, True),
    ("path compression only", True, False),
    ("both", True, True),
]
counts = {}
for name, compress, by_rank in variants:
    hops = chain_then_query(compress, by_rank)
    counts[name] = hops
    print(f"{name:<34}{hops:>13,}{hops / N:>11.1f}")
print()
worst = counts["no compression, no union by rank"]
best = counts["both"]
print(f"  the naive version costs {worst / best:,.0f}x the full version")
print()
print("The naive version is quadratic, and the arithmetic is easy to see: the")
print("chain has length n, and asking for the root of the far end walks the")
print("whole chain. Do that n times and you have n(n-1) hops -- which is what")
print("the first row shows, to the digit. That is why the first implementation")
print("anybody writes is unusable on real data.")
print()
print("The two fixes address two different things, which is why they stack.")
print()
print("Union by rank decides *which* root becomes the child. Always hanging")
print("the second tree under the first is what builds a chain; hanging the")
print("smaller under the larger keeps the depth logarithmic. It costs one")
print("comparison and one extra array, and it is the trick that makes the")
print("worst case provably shallow.")
print()
print("Path compression changes the tree while you are walking it. Every node")
print("on the way to the root is re-pointed directly at the root, so the")
print("second find on the same path is one step. It costs a few assignments")
print("and it is the trick that makes repeated queries almost free.")
print()
print("Together they give the result that makes union-find worth knowing: the")
print("amortised cost per operation is effectively constant -- the inverse of")
print("the Ackermann function, which is below 5 for any input that fits in the")
print("universe. Not 'log n'. Effectively 1.")
print()
print("The order to reach for them is worth noting. Path compression alone is")
print("usually enough, and it is the one you get for free in any implementation")
print("that re-points while walking. Union by rank is the one that bounds the")
print("*first* query, which matters when you build the structure once and query")
print("it a handful of times.")
print()
print()
print("Part 2 -- the question it answers that a traversal cannot")
print()
rng_state = 12345


def next_random(state, limit):
    """A tiny linear congruential generator, so the demo is the same on every
    machine and every Python."""
    state = (1103515245 * state + 12345) % (2 ** 31)
    return state, state % limit


state = rng_state
pairs = []
for _ in range(6):
    state, a = next_random(state, N)
    state, b = next_random(state, N)
    pairs.append((a, b))
uf = UnionFind(N, compress=True, by_rank=True)
for i in range(0, 200, 2):
    uf.union(i, i + 1)
print(f"  merged {100} pairs, from a universe of {N:,}")
print()
print(f"  {'pair':>18}{'same group?':>14}")
print("  " + "-" * 32)
for a, b in pairs:
    print(f"  {f'{a:>7} {b:>7}':>18}{str(uf.find(a) == uf.find(b)):>14}")
print()
print("A traversal can answer this too -- flood fill, then check the labels --")
print("but it has to be redone from scratch every time an edge is added. Union")
print("find absorbs the additions and answers queries incrementally, which is")
print("the difference between a structure and a computation.")
print()
print("That is what makes it the right tool for Kruskal's minimum spanning")
print("tree: sort the edges, then walk them cheapest first, merging groups as")
print("you go and skipping any edge whose two ends are already joined. The")
print("cycle test -- 'would this edge close a loop?' -- is exactly 'are these")
print("two already in the same group?', which is one find each.")
print()
print(f"  the two ends of a merged pair, always same group: "
      f"{all(uf.find(i) == uf.find(i + 1) for i in range(0, 200, 2))}")
```

```text
2,000 elements, merged into one chain, then 2,000 finds of the far end

variant                             parent hops   per find
----------------------------------------------------------
no compression, no union by rank      3,998,000     1999.0
union by rank only                        2,000        1.0
path compression only                     3,998        2.0
both                                      2,000        1.0

  the naive version costs 1,999x the full version

The naive version is quadratic, and the arithmetic is easy to see: the
chain has length n, and asking for the root of the far end walks the
whole chain. Do that n times and you have n(n-1) hops -- which is what
the first row shows, to the digit. That is why the first implementation
anybody writes is unusable on real data.

The two fixes address two different things, which is why they stack.

Union by rank decides *which* root becomes the child. Always hanging
the second tree under the first is what builds a chain; hanging the
smaller under the larger keeps the depth logarithmic. It costs one
comparison and one extra array, and it is the trick that makes the
worst case provably shallow.

Path compression changes the tree while you are walking it. Every node
on the way to the root is re-pointed directly at the root, so the
second find on the same path is one step. It costs a few assignments
and it is the trick that makes repeated queries almost free.

Together they give the result that makes union-find worth knowing: the
amortised cost per operation is effectively constant -- the inverse of
the Ackermann function, which is below 5 for any input that fits in the
universe. Not 'log n'. Effectively 1.

The order to reach for them is worth noting. Path compression alone is
usually enough, and it is the one you get for free in any implementation
that re-points while walking. Union by rank is the one that bounds the
*first* query, which matters when you build the structure once and query
it a handful of times.


Part 2 -- the question it answers that a traversal cannot

  merged 100 pairs, from a universe of 2,000

                pair   same group?
  --------------------------------
         606    1775         False
         924    1573         False
        1178     459         False
        1192    1793         False
         310     167         False
         244    1197         False

A traversal can answer this too -- flood fill, then check the labels --
but it has to be redone from scratch every time an edge is added. Union
find absorbs the additions and answers queries incrementally, which is
the difference between a structure and a computation.

That is what makes it the right tool for Kruskal's minimum spanning
tree: sort the edges, then walk them cheapest first, merging groups as
you go and skipping any edge whose two ends are already joined. The
cycle test -- 'would this edge close a loop?' -- is exactly 'are these
two already in the same group?', which is one find each.

  the two ends of a merged pair, always same group: True
```

The naive version is quadratic and the arithmetic is easy to see. The chain has length n, asking for
the root of the far end walks the whole chain, and doing that n times is n(n-1) hops -- which is what
the first row shows, to the digit.

The two fixes address two different things, which is why they stack. **Union by rank** decides which
root becomes the child: always hanging the second tree under the first is what builds the chain, and
hanging the smaller under the larger keeps the depth logarithmic. **Path compression** changes the
tree while you are walking it, re-pointing every node on the path directly at the root, so the second
query on that path is one step.

Together they give the result that makes union-find worth knowing: the amortised cost per operation
is effectively constant -- the inverse of the Ackermann function, which is below 5 for any input that
fits in the universe. Not "log n". Effectively 1.

:::pitfall `union(a, b)` hangs `b` under `a`, and that is what makes the worst case
The order of the two arguments is not cosmetic. Merging *forwards* along a chain builds a chain one
link at a time; merging backwards attaches every new node to the same root and builds a star of depth
1, which is the best case rather than the worst. A benchmark that measures the wrong direction will
report that union-find is fine without either optimisation, and it will be measuring the wrong thing.
:::

## Choosing, on evidence

One requirement, several implementations, and a failure that is reported two ways.

:::scenario The deploy that could not be ordered
A deployment pipeline has services that must start after the things they depend on. That is a
topological sort, and it fails in exactly one situation. Here is the version that ships:

```python
started = []
while True:
    for name, needs in services.items():
        if name not in started and all(n in started for n in needs):
            started.append(name)
```

It re-scans every service on every round, so it is O(V²) where the topological sort is O(V + E) --
and worse, it has no way to say *why* it stopped. It knows only that nothing happened.

Here is the same failure, reported both ways:

```python run
#!/usr/bin/env python3
"""Chapter 47 demo -- the deploy that could not be ordered, and the error
message that fixed it.

A deployment pipeline has services that must start after the things they
depend on. That is a topological sort. It fails in exactly one situation -- a
cycle -- and how the failure is *reported* decides whether the next person
fixes it in five minutes or five hours.
"""
from collections import deque

SERVICES = {
    "db": [],
    "cache": [],
    "auth": ["db"],
    "api": ["db", "cache", "auth"],
    "worker": ["db", "cache"],
    "search": ["db", "cache"],
    "metrics": ["api", "worker"],
    "web": ["api"],
    "gateway": ["web", "metrics"],
}

WHITE, GREY, BLACK = 0, 1, 2


def dependents(services):
    """Dependencies are the natural way to write it; 'what does this unlock'
    is the way to compute with it."""
    adj = {name: [] for name in services}
    for name, needs in services.items():
        for need in needs:
            adj[need].append(name)
    return adj


def start_order(adj):
    """Kahn's algorithm, plus the honest answer to 'did it work'."""
    indegree = {u: 0 for u in adj}
    for u in adj:
        for v in adj[u]:
            indegree[v] += 1
    queue = deque(u for u in adj if indegree[u] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return order, [u for u in adj if u not in order]


def find_cycle(adj):
    """DFS with a colour per node. A grey node met again is a back edge, and
    the grey path from that node to here *is* the cycle -- so the message can
    name it instead of announcing its existence."""
    colour = {u: WHITE for u in adj}
    path = []

    def visit(u):
        colour[u] = GREY
        path.append(u)
        for v in adj[u]:
            if colour[v] == GREY:
                return path[path.index(v):] + [v]
            if colour[v] == WHITE:
                found = visit(v)
                if found:
                    return found
        path.pop()
        colour[u] = BLACK
        return None

    for u in adj:
        if colour[u] == WHITE:
            found = visit(u)
            if found:
                return found
    return None


def retry_loop(services):
    """The strawman: repeatedly start anything whose dependencies are up, and
    wait if nothing can start. Counts the rounds before it gives up."""
    started = []
    rounds = 0
    while True:
        rounds += 1
        progress = False
        for name, needs in services.items():
            if name not in started and all(n in started for n in needs):
                started.append(name)
                progress = True
        if not progress:
            return started, rounds


ADJ = dependents(SERVICES)
order, stuck = start_order(ADJ)
print(f"{len(SERVICES)} services, {sum(len(v) for v in ADJ.values())} "
      f"dependency edges")
print()
print(f"  a correct start order ({len(order)} services):")
print(f"    {' -> '.join(order)}")
print(f"  anything left over: {stuck}")
print()
started, rounds = retry_loop(SERVICES)
print(f"  the retry loop started {len(started)} of {len(SERVICES)} services")
print(f"  and gave up after {rounds} rounds with nothing left to try")
print()
print("Both approaches work on a pipeline that is acyclic, and they are not")
print("equally good. The retry loop re-scans every service on every round, so")
print("it is O(V^2) where the topological sort is O(V + E) -- and worse, the")
print("loop has no way to say *why* it stopped. It knows only that nothing")
print("happened.")
print()
print()
print("Now the version that ships. One service gets a dependency it should not")
print()
BROKEN = dict(SERVICES)
BROKEN["auth"] = ["db", "api"]
BAD = dependents(BROKEN)
order, stuck = start_order(BAD)
started, rounds = retry_loop(BROKEN)
print(f"  'auth' now depends on 'api', and 'api' already depends on 'auth'")
print()
print(f"  services that could be started : {len(order)} of {len(BROKEN)}")
print(f"  stuck set                      : {', '.join(sorted(stuck))}")
print(f"  retry loop gave up after       : {rounds} rounds")
print(f"  services it never started      : "
      f"{', '.join(sorted(set(BROKEN) - set(started)))}")
print()
print("Both of those are true and neither is useful. 'auth' and 'api' are")
print("named, and the actual problem -- that they depend on each other -- is")
print("left for the reader to work out from a dependency list.")
print()
print("Here is the same failure, reported by the cycle finder:")
print()
cycle = find_cycle(BAD)
print(f"    dependency cycle: {' -> '.join(cycle)}")
print()
print("That is one line, it names every service involved in the order they")
print("form the loop, and it is what a person needs. It costs one extra")
print("traversal -- a DFS that keeps a colour per node, where a node is grey")
print("while it is on the current path and black once it is finished. Meeting")
print("a grey node means an edge has closed a loop, and the grey path from")
print("that node to here is the loop itself.")
print()
print("The lesson generalises past pipelines. A traversal that reports")
print("*whether* something failed is a different tool from one that reports")
print("*where* -- and the second one usually costs the same, because the")
print("information was already there. Kahn's algorithm was holding the answer")
print("in the stuck set; the DFS was holding it in the grey path. Neither")
print("required any extra bookkeeping, only the decision to look.")
print()
print(f"  the acyclic pipeline had no cycle: {find_cycle(ADJ) is None}")
print(f"  the cycle is closed by one edge  : "
      f"{cycle[0]} -> {cycle[-2]}")
print(f"  services downstream of the cycle : "
      f"{sum(1 for s in BAD if s not in cycle and s in stuck)} of {len(BAD)}")
```

```text
9 services, 13 dependency edges

  a correct start order (9 services):
    db -> cache -> auth -> worker -> search -> api -> metrics -> web -> gateway
  anything left over: []

  the retry loop started 9 of 9 services
  and gave up after 2 rounds with nothing left to try

Both approaches work on a pipeline that is acyclic, and they are not
equally good. The retry loop re-scans every service on every round, so
it is O(V^2) where the topological sort is O(V + E) -- and worse, the
loop has no way to say *why* it stopped. It knows only that nothing
happened.


Now the version that ships. One service gets a dependency it should not

  'auth' now depends on 'api', and 'api' already depends on 'auth'

  services that could be started : 4 of 9
  stuck set                      : api, auth, gateway, metrics, web
  retry loop gave up after       : 2 rounds
  services it never started      : api, auth, gateway, metrics, web

Both of those are true and neither is useful. 'auth' and 'api' are
named, and the actual problem -- that they depend on each other -- is
left for the reader to work out from a dependency list.

Here is the same failure, reported by the cycle finder:

    dependency cycle: auth -> api -> auth

That is one line, it names every service involved in the order they
form the loop, and it is what a person needs. It costs one extra
traversal -- a DFS that keeps a colour per node, where a node is grey
while it is on the current path and black once it is finished. Meeting
a grey node means an edge has closed a loop, and the grey path from
that node to here is the loop itself.

The lesson generalises past pipelines. A traversal that reports
*whether* something failed is a different tool from one that reports
*where* -- and the second one usually costs the same, because the
information was already there. Kahn's algorithm was holding the answer
in the stuck set; the DFS was holding it in the grey path. Neither
required any extra bookkeeping, only the decision to look.

  the acyclic pipeline had no cycle: True
  the cycle is closed by one edge  : auth -> api
  services downstream of the cycle : 3 of 9
```
:::

:::solution The rule
A traversal that reports *whether* something failed is a different tool from one that reports
*where* -- and the second one usually costs the same, because the information was already there.
Kahn's algorithm was holding the answer in the stuck set; the DFS was holding it in the grey path. A
node is grey while it is on the current path and black once it is finished, and meeting a grey node
means an edge has closed a loop.

Neither required any extra bookkeeping. Only the decision to look.
:::

## Key takeaways

- A graph is a set of edges and a decision about how to store them. An adjacency matrix costs n²
  slots and answers pair queries in one read; adjacency lists cost 2m slots and make "for each
  neighbour" free. Every traversal in this chapter has that inner loop, so the list is usually right.
- BFS explores in rings, and one traversal gives you the visit order, the shortest distance in edges,
  and a parent map that reconstructs the route. Nothing extra is computed for the parent map.
- DFS is the traversal a recursive function gives you for free, and the obvious iterative rewrite is
  *not* the same traversal. Push the neighbours in reverse and the order matches.
- DFS exhausts the call stack on a deep graph. Rewrite it with an explicit stack rather than raising
  the recursion limit -- a raised limit has the same failure mode, and the real failure is a segfault.
- "BFS holds the frontier, DFS holds the path" is about the shape of the memory, not its size. Mark a
  node visited when you *push* it, or the stack fills with duplicates -- 4,297 entries against a
  frontier of 142.
- A topological sort exists if and only if the graph is acyclic, so a failed sort is a cycle test. The
  nodes it could not place are on a cycle or downstream of one; a DFS with colours names the cycle.
- Dijkstra is BFS with a heap. It is correct only on non-negative weights, and it fails silently: a
  wrong shortest path is a valid list of nodes.
- BFS minimises edges and Dijkstra minimises weight. On a weighted graph BFS is wrong for 98.6% of
  the nodes, and nothing about the output says so.
- A heuristic must never overstate the true remaining cost, or A\* returns a suboptimal route. That is
  a property of a function you wrote, not of the algorithm.
- In A\*, breaking ties towards the goal is worth more than the heuristic: 2,389 expansions become 294
  with the same admissible estimate and the same optimal route.
- Connected components are the one question whose answer does not depend on the traversal, so the
  simplest traversal is the right one.
- Union-find answers "same group?" incrementally. Union by rank bounds the depth and path compression
  flattens the tree; together they make the amortised cost effectively constant.

## Practice

- [ ] Write a word ladder: BFS over an implicit graph where two four-letter words are joined when
  they differ in one letter. Count the candidate strings built, and explain why the neighbour
  function is where the cost is.
- [ ] Implement bidirectional BFS and compare the nodes expanded against plain BFS on a graph that
  branches. Explain why the saving is a square root rather than a factor, and why the same demo on a
  square grid shows almost nothing.
- [ ] Build a minimum spanning tree two ways -- Kruskal with union-find, Prim with a heap -- and check
  that both give the same total weight. Report the longest edge in the tree and say what that number
  means.
- [ ] Cross a grid where you may break at most k walls. Model the state as `(cell, walls_broken)` and
  solve it with plain BFS, then measure the blow-up in the state space as k grows.
- [ ] Decide whether a set of courses can be examined in two slots, using a two-colouring. When the
  answer is no, report the edge or the odd cycle that proves it rather than the word "no".

## Solutions

:::solution Exercise 1
The graph is never built. The traversal asks a node for its neighbours and the neighbour function
does 100 candidate tests per word, so the search is cheap and the neighbour function is not -- which
is the standard reason to make an implicit graph explicit where the search touches it often.

```python run
#!/usr/bin/env python3
"""Chapter 47 solution 1 -- a word ladder, which is BFS on a graph nobody
built.

The graph is implicit. The nodes are words, two words are joined when they
differ in exactly one letter, and no edge is ever stored. That is the normal
situation rather than the exception: the graph is described by a *rule*, and
materialising it would cost far more than searching it. So the traversal has
to be able to ask a node for its neighbours, and the neighbour function is
where all the cost lives.
"""
from collections import deque

WORDS = {
    "cold", "cord", "card", "ward", "warm", "word", "wood", "wool", "cool",
    "pool", "poll", "pole", "pale", "sale", "sage", "gale", "gall", "wall",
    "well", "weld", "wild", "wind", "wine", "fine", "find", "fond", "fund",
    "bold", "bald", "balm", "calm", "palm", "pall", "fall", "fell", "feel",
    "heel", "heal", "teal", "tell", "tall", "tale", "male", "malt", "halt",
    "half", "hall", "hale", "hole", "home", "hope", "rope", "rose", "rise",
    "wise", "wish", "wash", "cash", "case", "cave", "save", "same", "some",
    "come", "cone", "bone", "born", "burn", "barn", "yarn", "yard", "hard",
    "hare", "care", "cart", "cast", "cost", "coat", "boat", "bolt", "belt",
    "best", "nest", "next", "text", "test", "tent", "rent", "rest", "rust",
    "dust", "dusk", "disk", "dish", "fish", "fist", "fast", "last", "list",
    "lost", "lose", "lone", "lane", "land", "sand", "send", "seed", "seek",
    "week", "weed", "deed", "dead", "dear", "fear", "near", "neat", "seat",
    "seal", "meal", "mean", "mane", "made", "make", "wake", "cake", "came",
    "game", "gate", "late", "lake", "bake", "bark", "dark", "dare", "bare",
    "base", "ease", "easy", "east", "vast", "vest", "west", "pest", "past",
}
LETTERS = "abcdefghijklmnopqrstuvwxyz"
LENGTH = 4
CANDIDATES_PER_WORD = LENGTH * (len(LETTERS) - 1)


def neighbours(word, tally=None):
    """Every word in the dictionary one letter away.

    Note what this costs. For each of the 4 positions it tries all 25 other
    letters, so 100 candidate strings are built and hashed *per word*,
    whether or not any of them is a word. That 100 is the real price of an
    implicit graph, and it is why the tally below counts candidates rather
    than edges.
    """
    for i in range(LENGTH):
        for ch in LETTERS:
            if ch != word[i]:
                if tally is not None:
                    tally[0] += 1
                candidate = word[:i] + ch + word[i + 1:]
                if candidate in WORDS:
                    if tally is not None:
                        tally[1] += 1
                    yield candidate


def ladder(start, goal):
    """BFS over an implicit graph, with both costs counted: candidates built
    (the neighbour function's work) and edges found (the graph's size)."""
    parent = {start: None}
    queue = deque([start])
    tally = [0, 0]
    while queue:
        u = queue.popleft()
        if u == goal:
            break
        for v in neighbours(u, tally):
            if v not in parent:
                parent[v] = u
                queue.append(v)
    if goal not in parent:
        return None, tally, len(parent)
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path, tally, len(parent)


print(f"a dictionary of {len(WORDS)} four-letter words")
print(f"every word has {CANDIDATES_PER_WORD} candidate neighbours to test")
print()
route, tally, visited = ladder("cold", "warm")
print(f"  cold -> warm     : {' -> '.join(route)}")
print(f"  steps            : {len(route) - 1}")
print(f"  words visited    : {visited}")
print(f"  candidates built : {tally[0]:,}")
print(f"  real edges found : {tally[1]:,}")
print(f"  candidates per edge: {tally[0] / tally[1]:.0f}")
print()
print("Every step changes exactly one letter, which is the only constraint the")
print("problem stated. The route is not the one a person would guess -- 'cold,")
print("cord, card, ward, warm' goes through two words that have nothing to do")
print("with temperature -- and it is the shortest one, because BFS has no")
print("opinions about which words are related.")
print()
print("Now the cost, which is the interesting half. The graph was never built,")
print("and the traversal touched only the part of it that mattered. But look")
print("at the ratio: every *edge* the search found cost")
print(f"{tally[0] / tally[1]:.0f} candidate strings built and hashed. The search is cheap")
print("and the neighbour function is not, and on a real dictionary that ratio")
print("is what decides whether this runs in a second or a minute.")
print()
print("The standard fix is to stop generating neighbours and start looking")
print("them up: index the dictionary by wildcard pattern, so that 'c_ld' maps")
print("to every word matching it. Then a word's neighbours are four dictionary")
print("lookups instead of a hundred hash tests, and the implicit graph has")
print("been made explicit exactly where the search touches it. That is the")
print("usual trade -- pay memory to remove a constant factor -- and it is")
print("worth making only because the search visits these words many times.")
print()
print()
print("The same code on a pair with no route")
print()
route, tally, visited = ladder("cold", "zzzz")
print(f"  cold -> zzzz     : {route}")
print(f"  words visited    : {visited} of {len(WORDS)}")
print(f"  candidates built : {tally[0]:,}")
print()
print("The search exhausts the entire connected component of 'cold' and")
print("reports that there is no route -- which is the correct answer, and one")
print("that can only be known by looking. Note that 'no route' and 'the goal")
print("is isolated' are different facts, and this code cannot tell them apart:")
print("both produce the same empty result.")
print()
print(f"  is zzzz reachable from cold? {route is not None}")
print(f"  words one letter from cold : {sorted(neighbours('cold'))}")
print(f"  words one letter from warm : {sorted(neighbours('warm'))}")
```

```text
a dictionary of 144 four-letter words
every word has 100 candidate neighbours to test

  cold -> warm     : cold -> cord -> word -> ward -> warm
  steps            : 4
  words visited    : 40
  candidates built : 2,000
  real edges found : 71
  candidates per edge: 28

Every step changes exactly one letter, which is the only constraint the
problem stated. The route is not the one a person would guess -- 'cold,
cord, card, ward, warm' goes through two words that have nothing to do
with temperature -- and it is the shortest one, because BFS has no
opinions about which words are related.

Now the cost, which is the interesting half. The graph was never built,
and the traversal touched only the part of it that mattered. But look
at the ratio: every *edge* the search found cost
28 candidate strings built and hashed. The search is cheap
and the neighbour function is not, and on a real dictionary that ratio
is what decides whether this runs in a second or a minute.

The standard fix is to stop generating neighbours and start looking
them up: index the dictionary by wildcard pattern, so that 'c_ld' maps
to every word matching it. Then a word's neighbours are four dictionary
lookups instead of a hundred hash tests, and the implicit graph has
been made explicit exactly where the search touches it. That is the
usual trade -- pay memory to remove a constant factor -- and it is
worth making only because the search visits these words many times.


The same code on a pair with no route

  cold -> zzzz     : None
  words visited    : 144 of 144
  candidates built : 14,400

The search exhausts the entire connected component of 'cold' and
reports that there is no route -- which is the correct answer, and one
that can only be known by looking. Note that 'no route' and 'the goal
is isolated' are different facts, and this code cannot tell them apart:
both produce the same empty result.

  is zzzz reachable from cold? False
  words one letter from cold : ['bold', 'cord']
  words one letter from warm : ['ward']
```
:::

:::solution Exercise 2
One search grows a ball of radius d; two grow balls of radius d/2, and a ball of radius r on a graph
that branches b ways holds about b^r nodes. Halving r square-roots the work. The stopping rule has to
be proved -- and it needs the graph to be unweighted for the proof to hold.

```python run
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
```

```text
a random graph: 20,000 nodes, 59,996 edges, mean degree 6.0
  reachable from node 0     : 20,000
  farthest node from 0      : 19754, at distance 8

search                  route   expanded   nodes seen
-----------------------------------------------------
BFS from one end            8     19,829       20,000
bidirectional BFS           8        163          875

  the two agree on the distance : True
  nodes expanded                : 121.7x fewer
  nodes ever put in a dictionary: 22.9x fewer

That is the square root, and the arithmetic is the whole explanation.
The route is 8 steps long. BFS from one end grows a ball of radius
8; two searches grow balls of radius 4. On a graph that
branches about 6 ways, a ball of radius r holds roughly
6^r nodes -- so halving r does not halve the work, it
square-roots it.

This is why the technique is worth knowing even though it needs an
extra frontier, an extra dictionary, and a stopping rule that has to be
proved. On a graph with a large diameter and a small branching factor
the saving is modest. On one that branches -- a state space, a puzzle,
a word graph -- it is the difference between a search that finishes and
one that does not.

The stopping rule is the part that has to be argued, because it is not
obvious that the *first* touch is on a shortest route. Suppose the two
frontiers meet at a node at distance a from the start and b from the
goal. Every node still in the forward frontier is at distance at least
a, and every node in the backward frontier at distance at least b -- so
any route not yet found has length at least a + b, which is exactly the
length of the route just found. Nothing shorter is hiding.

That argument needs the graph to be unweighted, or at least symmetric.
On a weighted graph the two searches grow at different rates -- five
units from one side is not comparable to five units from the other --
and the meeting test stops being a proof. Bidirectional Dijkstra exists,
and its stopping condition is *not* 'the frontiers touched'.

  route length 8 on a graph of diameter 8
  (the same demo on a square grid shows almost no saving, because the
   frame clips both balls -- which is why this one uses a graph)
```
:::

:::solution Exercise 3
Sort the edges, walk them cheapest first, and keep an edge unless its two ends are already connected.
"Already connected" is one union-find query, which is the whole reason the structure exists.

```python run
#!/usr/bin/env python3
"""Chapter 47 solution 3 -- Kruskal's minimum spanning tree, which is a sort
and a union-find and nothing else.

The problem: connect n points as cheaply as possible. The algorithm: sort
every candidate edge by weight, then walk them cheapest first, keeping an edge
unless its two ends are already connected. "Already connected" is one
union-find query, which is why the structure from earlier in the chapter is
the entire engine and the sort is the only other moving part.
"""
import heapq
import random


class UnionFind:
    __slots__ = ("parent", "rank")

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


TOWNS = 30
rng = random.Random(3)
POINTS = [(rng.randrange(100), rng.randrange(100)) for _ in range(TOWNS)]


def distance(a, b):
    dx = POINTS[a][0] - POINTS[b][0]
    dy = POINTS[a][1] - POINTS[b][1]
    return round((dx * dx + dy * dy) ** 0.5)


CANDIDATES = [(distance(a, b), a, b)
              for a in range(TOWNS) for b in range(a + 1, TOWNS)]
ADJ = {i: [] for i in range(TOWNS)}
for w, a, b in CANDIDATES:
    ADJ[a].append((b, w))
    ADJ[b].append((a, w))


def kruskal(n, candidates):
    """Sort, then take the cheapest edge that does not close a loop."""
    uf = UnionFind(n)
    chosen = []
    total = 0
    examined = 0
    rejected = 0
    for w, a, b in sorted(candidates):
        examined += 1
        if uf.union(a, b):
            chosen.append((a, b, w))
            total += w
        else:
            rejected += 1
        if len(chosen) == n - 1:
            break
    return chosen, total, examined, rejected


def prim(n, adj):
    """Grow one tree outwards, always taking the cheapest edge that leaves it."""
    in_tree = [False] * n
    in_tree[0] = True
    heap = [(w, 0, v) for v, w in adj[0]]
    heapq.heapify(heap)
    total = 0
    count = 0
    pushes = len(heap)
    while heap and count < n - 1:
        w, a, b = heapq.heappop(heap)
        if in_tree[b]:
            continue
        in_tree[b] = True
        total += w
        count += 1
        for v, wv in adj[b]:
            if not in_tree[v]:
                heapq.heappush(heap, (wv, b, v))
                pushes += 1
    return total, pushes


chosen, total, examined, rejected = kruskal(TOWNS, CANDIDATES)
prim_total, prim_pushes = prim(TOWNS, ADJ)
EDGES = len(CANDIDATES)

print(f"{TOWNS} towns scattered in a 100x100 square")
print(f"  candidate edges      : {EDGES:,} (every pair)")
print(f"  edges in the tree    : {len(chosen)} (always n - 1)")
print()
print(f"{'algorithm':<12}{'total length':>14}{'edges examined':>16}"
      f"{'work':>16}")
print("-" * 58)
print(f"{'Kruskal':<12}{total:>14,}{examined:>16,}{'1 sort + ' + str(examined) + ' finds':>16}")
print(f"{'Prim':<12}{prim_total:>14,}{'':>16}{str(prim_pushes) + ' heap pushes':>16}")
print()
print(f"  the two agree on the total length : {total == prim_total}")
print(f"  edges Kruskal rejected as loops   : {rejected}")
print()
print("Both produce a minimum spanning tree and both are correct; they are")
print("different because they make the same greedy choice in different")
print("orders. Kruskal considers edges globally, cheapest first, and asks 'do")
print("these two ends already belong to the same piece?'. Prim considers one")
print("growing tree and asks 'what is the cheapest way out of it?'.")
print()
print("The rejected count is the part that needs union-find. The n-1 edges")
print("that make the tree are the cheap ones; every other edge was considered")
print("and discarded because its two ends were already joined. Without a fast")
print("'already joined' test, Kruskal is a sort followed by a search through")
print("the chosen edges -- which is O(E log E) becoming O(E*V).")
print()
print("Why the greedy choice is safe is the interesting part, and it is the")
print("cut property: for any way of splitting the towns into two groups, the")
print("cheapest edge crossing that split is in *some* minimum spanning tree.")
print("Kruskal's first accepted edge is the cheapest edge overall, which")
print("crosses every split that separates its two ends, so it is safe. The")
print("same argument then applies to the remaining graph.")
print()
print()
print("The tree itself")
print()
by_weight = sorted(chosen, key=lambda e: -e[2])
print(f"  {'edge':>10}{'length':>9}   {'edge':>10}{'length':>9}")
print("  " + "-" * 40)
half = (len(by_weight) + 1) // 2
for i in range(half):
    left = by_weight[i]
    right = by_weight[i + half] if i + half < len(by_weight) else None
    left_text = f"{left[0]:>4} - {left[1]:<4}{left[2]:>9}"
    right_text = (f"{right[0]:>4} - {right[1]:<4}{right[2]:>9}"
                  if right else "")
    print(f"  {left_text}   {right_text}")
print()
print(f"  longest edge in the tree : {by_weight[0][2]}")
print(f"  shortest edge in the tree: {by_weight[-1][2]}")
print(f"  mean edge length         : {total / len(chosen):.1f}")
print()
print("The longest edge is the one to look at, because it is the answer to a")
print("question people actually ask: 'if I connect these towns as cheaply as")
print("possible, what is the worst connection I still have to pay for?' That")
print("is a minimax problem, and the minimum spanning tree solves it -- the")
print("longest edge in the MST is the smallest possible value for the largest")
print("edge in any connected network over these points.")
print()
print(f"  all {TOWNS} towns reachable through the tree: "
      f"{len(chosen) == TOWNS - 1}")
```

```text
30 towns scattered in a 100x100 square
  candidate edges      : 435 (every pair)
  edges in the tree    : 29 (always n - 1)

algorithm     total length  edges examined            work
----------------------------------------------------------
Kruskal                369             1061 sort + 106 finds
Prim                   369                 435 heap pushes

  the two agree on the total length : True
  edges Kruskal rejected as loops   : 77

Both produce a minimum spanning tree and both are correct; they are
different because they make the same greedy choice in different
orders. Kruskal considers edges globally, cheapest first, and asks 'do
these two ends already belong to the same piece?'. Prim considers one
growing tree and asks 'what is the cheapest way out of it?'.

The rejected count is the part that needs union-find. The n-1 edges
that make the tree are the cheap ones; every other edge was considered
and discarded because its two ends were already joined. Without a fast
'already joined' test, Kruskal is a sort followed by a search through
the chosen edges -- which is O(E log E) becoming O(E*V).

Why the greedy choice is safe is the interesting part, and it is the
cut property: for any way of splitting the towns into two groups, the
cheapest edge crossing that split is in *some* minimum spanning tree.
Kruskal's first accepted edge is the cheapest edge overall, which
crosses every split that separates its two ends, so it is safe. The
same argument then applies to the remaining graph.


The tree itself

        edge   length         edge   length
  ----------------------------------------
    12 - 27         32     26 - 29         12
    22 - 25         25      3 - 9          11
     3 - 22         20     16 - 22         11
     0 - 2          17     26 - 27         11
     0 - 8          17      3 - 11         10
     5 - 15         17     11 - 23         10
     6 - 14         17      1 - 4           9
    12 - 19         17      4 - 5           8
     0 - 21         16      6 - 29          7
    12 - 17         14      7 - 29          7
     1 - 7          13      2 - 11          5
     9 - 10         13     15 - 20          5
     1 - 13         12     17 - 28          5
    10 - 14         12     18 - 25          4
    14 - 24         12   

  longest edge in the tree : 32
  shortest edge in the tree: 4
  mean edge length         : 12.7

The longest edge is the one to look at, because it is the answer to a
question people actually ask: 'if I connect these towns as cheaply as
possible, what is the worst connection I still have to pay for?' That
is a minimax problem, and the minimum spanning tree solves it -- the
longest edge in the MST is the smallest possible value for the largest
edge in any connected network over these points.

  all 30 towns reachable through the tree: True
```
:::

:::solution Exercise 4
Put the extra information into the node and the problem stops being special. The search does not
change -- only the graph it runs on -- and the price is `cells * (budget + 1)`.

```python run
#!/usr/bin/env python3
"""Chapter 47 solution 4 -- when the graph you have is not the graph you need.

The problem: cross a grid, and you are allowed to walk through at most k
walls. The trick is not an algorithm. It is a change in what a *node* is.
Make a node the pair (cell, walls broken so far) and the problem becomes an
ordinary unweighted shortest path on a bigger graph -- solved by the same BFS
from earlier in the chapter, with no modification at all.

That move -- expanding the state until the problem is one you already have --
is the most reusable idea in this part of the book, and it is worth seeing
once in full.
"""
import random
from collections import deque

SIZE = 30
START, GOAL = (0, 0), (SIZE - 1, SIZE - 1)
MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))
BUDGETS = (0, 6, 12)


def build_walls(size, ratio, seed):
    rng = random.Random(seed)
    walls = {(r, c) for r in range(size) for c in range(size)
             if rng.random() < ratio}
    walls.discard(START)
    walls.discard(GOAL)
    return walls


def steps(walls, cell):
    """A move is (neighbour, walls_it_costs). Walking into a wall costs one
    unit of budget; walking anywhere else costs none."""
    r, c = cell
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            yield (nr, nc), (1 if (nr, nc) in walls else 0)


def plain_bfs(walls):
    """No budget: walls are simply impassable."""
    dist = {START: 0}
    queue = deque([START])
    expanded = 0
    while queue:
        u = queue.popleft()
        if u == GOAL:
            return dist[u], expanded
        expanded += 1
        for v, cost in steps(walls, u):
            if cost == 0 and v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return None, expanded


def budgeted_bfs(walls, budget):
    """The node is now (cell, walls_broken). A wall move goes to a state one
    layer up; a free move stays on the same layer. Every edge still costs one
    step, so BFS is still the right search -- on a graph with
    `cells * (budget + 1)` nodes instead of `cells`."""
    start_state = (START, 0)
    dist = {start_state: 0}
    queue = deque([start_state])
    expanded = 0
    while queue:
        state = queue.popleft()
        cell, spent = state
        d = dist[state]
        if cell == GOAL:
            return d, expanded, len(dist)
        expanded += 1
        for v, cost in steps(walls, cell):
            if spent + cost > budget:
                continue
            nxt = (v, spent + cost)
            if nxt not in dist:
                dist[nxt] = d + 1
                queue.append(nxt)
    return None, expanded, len(dist)


WALLS = build_walls(SIZE, 0.35, seed=7)
no_budget, plain_expanded = plain_bfs(WALLS)
results = [(budget, *budgeted_bfs(WALLS, budget)) for budget in BUDGETS]

print(f"a {SIZE}x{SIZE} grid, {len(WALLS):,} walls "
      f"({len(WALLS) / (SIZE * SIZE):.0%}), {START} to {GOAL}")
print(f"the straight-line distance is {SIZE + SIZE - 2} steps")
print()
print(f"  {'search':<36}{'route':>9}{'expanded':>11}{'states':>10}")
print("-" * 66)
label = "plain BFS (walls impassable)"
print(f"  {label:<36}"
      f"{('no route' if no_budget is None else no_budget):>9}"
      f"{plain_expanded:>11,}{plain_expanded:>10,}")
for budget, route, expanded, states in results:
    label = f"BFS on (cell, walls broken), budget {budget}"
    print(f"  {label:<36}"
          f"{('no route' if route is None else route):>9}"
          f"{expanded:>11,}{states:>10,}")
print()
last_budget, last_route, last_expanded, last_states = results[-1]
print(f"With the walls impassable there is no route at all, which is why the")
print(f"first row says so. Give the search a budget of {last_budget} and the same")
print(f"code -- the same BFS, unchanged -- returns a route of {last_route} steps.")
print("Nothing was added to the search. What changed is that a state now")
print("carries one extra number, and that number is what makes a wall")
print("passable once and only once.")
print()
print("Read down the expanded column, because that is the price. Raising the")
print("budget from 0 to 6 makes the state space seven times bigger and lets")
print("the search find a route at all; raising it again to 12 makes it")
print("thirteen times bigger, doubles the work, and returns exactly the same")
print("route. Six walls were enough -- and the search had no way to know that")
print("in advance, so it paid for the budget it was given rather than the")
print("budget it needed.")
print()
print("That is the practical shape of the trick. The blow-up is exactly the")
print("factor you would predict -- `cells * (budget + 1)` -- and it is the")
print("thing to check before reaching for this on a large grid. A budget you")
print("cannot afford is worse than no budget at all, because the search will")
print("spend it.")
print()
print("This is the standard move for a whole family of problems that look like")
print("they need new machinery:")
print()
print("  at most k walls broken      -> (cell, k)")
print("  a key you have or have not  -> (cell, has_key)")
print("  fuel left in the tank       -> (cell, fuel_left)")
print("  parity of the steps taken   -> (cell, steps % 2)")
print("  which side of a fence       -> (cell, side)")
print()
print("In every case the answer is the same sentence: put the extra")
print("information into the node, and the problem stops being special. The")
print("search does not change; only the graph it is running on does.")
print()
print("One detail matters and it is easy to get wrong. BFS is still correct")
print("here *because every move costs exactly one step* -- walking into a wall")
print("costs one step and one unit of budget, and walking into open ground")
print("costs one step and nothing else. If a wall move cost two steps this")
print("would be a weighted graph and BFS would return a wrong answer, exactly")
print("as the earlier section showed. Expanding the state does not change")
print("which search is correct; it only changes the graph.")
print()
print(f"  states in the expanded graph : {last_states:,}")
print(f"  cells in the grid            : {SIZE * SIZE:,}")
print(f"  blow-up factor               : {last_states / (SIZE * SIZE):.2f}x")
print(f"  a route exists without breaking walls : {no_budget is not None}")
print(f"  budgets tried                : {', '.join(str(b) for b in BUDGETS)}")
```

```text
a 30x30 grid, 351 walls (39%), (0, 0) to (29, 29)
the straight-line distance is 58 steps

  search                                  route   expanded    states
------------------------------------------------------------------
  plain BFS (walls impassable)         no route        319       319
  BFS on (cell, walls broken), budget 0 no route        319       319
  BFS on (cell, walls broken), budget 6       58      5,288     5,313
  BFS on (cell, walls broken), budget 12       58     10,682    10,713

With the walls impassable there is no route at all, which is why the
first row says so. Give the search a budget of 12 and the same
code -- the same BFS, unchanged -- returns a route of 58 steps.
Nothing was added to the search. What changed is that a state now
carries one extra number, and that number is what makes a wall
passable once and only once.

Read down the expanded column, because that is the price. Raising the
budget from 0 to 6 makes the state space seven times bigger and lets
the search find a route at all; raising it again to 12 makes it
thirteen times bigger, doubles the work, and returns exactly the same
route. Six walls were enough -- and the search had no way to know that
in advance, so it paid for the budget it was given rather than the
budget it needed.

That is the practical shape of the trick. The blow-up is exactly the
factor you would predict -- `cells * (budget + 1)` -- and it is the
thing to check before reaching for this on a large grid. A budget you
cannot afford is worse than no budget at all, because the search will
spend it.

This is the standard move for a whole family of problems that look like
they need new machinery:

  at most k walls broken      -> (cell, k)
  a key you have or have not  -> (cell, has_key)
  fuel left in the tank       -> (cell, fuel_left)
  parity of the steps taken   -> (cell, steps % 2)
  which side of a fence       -> (cell, side)

In every case the answer is the same sentence: put the extra
information into the node, and the problem stops being special. The
search does not change; only the graph it is running on does.

One detail matters and it is easy to get wrong. BFS is still correct
here *because every move costs exactly one step* -- walking into a wall
costs one step and one unit of budget, and walking into open ground
costs one step and nothing else. If a wall move cost two steps this
would be a weighted graph and BFS would return a wrong answer, exactly
as the earlier section showed. Expanding the state does not change
which search is correct; it only changes the graph.

  states in the expanded graph : 10,713
  cells in the grid            : 900
  blow-up factor               : 11.90x
  a route exists without breaking walls : False
  budgets tried                : 0, 6, 12
```
:::

:::solution Exercise 5
Colour each neighbour the opposite of its parent. An odd cycle forces the last node to match the
first, and the edge that closes the loop is the proof you hand to somebody instead of an assertion.

```python run
#!/usr/bin/env python3
"""Chapter 47 solution 5 -- two colours, one traversal, and a surprising
number of real problems.

"Can these be split into two groups so that no two conflicting things end up
together?" is exactly "is this graph bipartite?", and a BFS that colours as it
goes answers it in a single pass. The traversal is the same one from earlier
in the chapter. The only addition is an array of colours -- and the realisation
that a conflict is not a property of the nodes at all.
"""
from collections import deque

CYCLE_4 = {
    "a": ["b", "d"],
    "b": ["a", "c"],
    "c": ["b", "d"],
    "d": ["a", "c"],
}

CYCLE_5 = {
    "a": ["b", "e"],
    "b": ["a", "c"],
    "c": ["b", "d"],
    "d": ["c", "e"],
    "e": ["d", "a"],
}

COURSES = {
    "maths": ["physics", "stats"],
    "physics": ["maths", "chem"],
    "chem": ["physics", "bio"],
    "bio": ["chem"],
    "stats": ["maths", "cs"],
    "cs": ["stats"],
}


def two_colour(adj):
    """BFS from every unvisited node, colouring each neighbour the opposite of
    its parent. Returns the colouring, or the edge that makes it impossible."""
    colour = {}
    for start in adj:
        if start in colour:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in colour:
                    colour[v] = 1 - colour[u]
                    queue.append(v)
                elif colour[v] == colour[u]:
                    return None, (u, v)
    return colour, None


def show(adj, label):
    colour, clash = two_colour(adj)
    print(f"  {label}")
    if colour is None:
        print(f"    not bipartite -- the edge {clash[0]}-{clash[1]} "
              f"joins two nodes of the same colour")
        return
    groups = {0: [], 1: []}
    for node, c in colour.items():
        groups[c].append(node)
    print(f"    bipartite, in one pass")
    print(f"    group A: {', '.join(sorted(groups[0]))}")
    print(f"    group B: {', '.join(sorted(groups[1]))}")


print("Part 1 -- what the traversal is looking for")
print()
show(CYCLE_4, "a four-cycle")
print()
show(CYCLE_5, "a five-cycle")
print()
print("An even cycle alternates colours all the way round and closes cleanly.")
print("An odd cycle does not: walking round it flips the colour five times,")
print("so the last node is forced to be the same colour as the first -- and")
print("the edge that closes the loop then joins two nodes that must differ.")
print()
print("That is the whole theory, and it is worth stating as one line: a graph")
print("is bipartite if and only if it contains no odd cycle. The traversal")
print("finds this by *doing* it -- it tries to colour the graph, and the")
print("attempt fails at exactly the edge that cannot be satisfied.")
print()
print("The failure report is the useful part. 'Not bipartite' tells you")
print("nothing; the edge tells you which pair of things you have to separate")
print("by some other means.")
print()
print()
print("Part 2 -- the same question with consequences")
print()
print("  six courses, where two courses are joined if a student takes both")
print()
for course, clashes in COURSES.items():
    print(f"    {course:<8} shares a student with: {', '.join(clashes)}")
print()
show(COURSES, "can these be examined in two slots?")
print()
print("Two exam slots, no student in two places at once -- that is a two")
print("colouring, and it works. Group A sits in the morning and group B in")
print("the afternoon, and no student has two exams in the same slot.")
print()
print("Notice what the graph is. The nodes are courses and the edges are")
print("*conflicts*, which is the opposite of the graphs earlier in this")
print("chapter: there, an edge meant 'connected' and we looked for paths")
print("through it. Here an edge means 'must not be together' and we look for")
print("a way to avoid it. The traversal is identical; only the reading of an")
print("edge changed.")
print()
print("That reframing is what makes the technique portable. 'Can I do this in")
print("two rounds?' is bipartiteness whenever the constraint is pairwise and")
print("binary -- two teams, two machines, two shifts, two colours, black and")
print("white. And when the answer is no, the odd cycle is the *proof*: it is a")
print("concrete set of things that cannot be split, and you can hand it to")
print("somebody instead of an assertion.")
print()
print()
print("Part 3 -- and when two is not enough")
print()
TRIANGLE = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}
show(TRIANGLE, "three mutually conflicting courses")
print()
print("Three courses, every pair in conflict: two slots cannot work, and no")
print("colouring will make them. That is not a failure of the traversal -- it")
print("is the answer, and the edge it reports is the proof. The general")
print("question ('how many slots?') is graph colouring, which is hard, and")
print("the two-colour case is the one special case that is easy.")
print()
print("Knowing where the easy case stops is most of the value. Bipartiteness")
print("is one BFS. Three colours is NP-hard. The gap between them is not a")
print("gap in effort; it is a gap in what is known to be possible.")
print()
print(f"  the four-cycle is bipartite : {two_colour(CYCLE_4)[0] is not None}")
print(f"  the five-cycle is bipartite : {two_colour(CYCLE_5)[0] is not None}")
print(f"  the courses are bipartite   : {two_colour(COURSES)[0] is not None}")
print(f"  the triangle is bipartite   : {two_colour(TRIANGLE)[0] is not None}")
```

```text
Part 1 -- what the traversal is looking for

  a four-cycle
    bipartite, in one pass
    group A: a, c
    group B: b, d

  a five-cycle
    not bipartite -- the edge c-d joins two nodes of the same colour

An even cycle alternates colours all the way round and closes cleanly.
An odd cycle does not: walking round it flips the colour five times,
so the last node is forced to be the same colour as the first -- and
the edge that closes the loop then joins two nodes that must differ.

That is the whole theory, and it is worth stating as one line: a graph
is bipartite if and only if it contains no odd cycle. The traversal
finds this by *doing* it -- it tries to colour the graph, and the
attempt fails at exactly the edge that cannot be satisfied.

The failure report is the useful part. 'Not bipartite' tells you
nothing; the edge tells you which pair of things you have to separate
by some other means.


Part 2 -- the same question with consequences

  six courses, where two courses are joined if a student takes both

    maths    shares a student with: physics, stats
    physics  shares a student with: maths, chem
    chem     shares a student with: physics, bio
    bio      shares a student with: chem
    stats    shares a student with: maths, cs
    cs       shares a student with: stats

  can these be examined in two slots?
    bipartite, in one pass
    group A: chem, cs, maths
    group B: bio, physics, stats

Two exam slots, no student in two places at once -- that is a two
colouring, and it works. Group A sits in the morning and group B in
the afternoon, and no student has two exams in the same slot.

Notice what the graph is. The nodes are courses and the edges are
*conflicts*, which is the opposite of the graphs earlier in this
chapter: there, an edge meant 'connected' and we looked for paths
through it. Here an edge means 'must not be together' and we look for
a way to avoid it. The traversal is identical; only the reading of an
edge changed.

That reframing is what makes the technique portable. 'Can I do this in
two rounds?' is bipartiteness whenever the constraint is pairwise and
binary -- two teams, two machines, two shifts, two colours, black and
white. And when the answer is no, the odd cycle is the *proof*: it is a
concrete set of things that cannot be split, and you can hand it to
somebody instead of an assertion.


Part 3 -- and when two is not enough

  three mutually conflicting courses
    not bipartite -- the edge y-z joins two nodes of the same colour

Three courses, every pair in conflict: two slots cannot work, and no
colouring will make them. That is not a failure of the traversal -- it
is the answer, and the edge it reports is the proof. The general
question ('how many slots?') is graph colouring, which is hard, and
the two-colour case is the one special case that is easy.

Knowing where the easy case stops is most of the value. Bipartiteness
is one BFS. Three colours is NP-hard. The gap between them is not a
gap in effort; it is a gap in what is known to be possible.

  the four-cycle is bipartite : True
  the five-cycle is bipartite : False
  the courses are bipartite   : True
  the triangle is bipartite   : False
```
:::
