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
