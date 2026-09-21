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
