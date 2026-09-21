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
