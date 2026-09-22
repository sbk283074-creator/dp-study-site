#!/usr/bin/env python3
"""Exercise 4 -- a blast radius over a credential graph of your own.

Ten resources, one starting credential, and two grants. The traversal is the
same breadth-first search as the ninth block, on a different graph.
"""

LEAST = [
    ("reporting account", "orders table"),
    ("reporting account", "order lines table"),
]

DEFAULT = LEAST + [
    ("reporting account", "customers table"),
]

# resource -> what is stored inside it, and what that unlocks
CONTAINS = [
    ("customers table", "support api token"),
    ("support api token", "support console"),
    ("support console", "customer export tool"),
    ("customer export tool", "full customer export"),
    ("reporting account", "warehouse key"),
    ("warehouse key", "analytics bucket"),
    ("analytics bucket", "raw event stream"),
]

START = "reporting account"


def bfs(edges, source):
    adjacency = {}
    for u, v in edges:
        adjacency.setdefault(u, []).append(v)
    for u in adjacency:
        adjacency[u].sort()
    seen = {source: 0}
    queue = [source]
    while queue:
        node = queue.pop(0)
        for nxt in adjacency.get(node, ()):
            if nxt not in seen:
                seen[nxt] = seen[node] + 1
                queue.append(nxt)
    return seen


def main():
    least = bfs(LEAST + CONTAINS, START)
    default = bfs(DEFAULT + CONTAINS, START)

    print(f"  starting credential                 {START}")
    print()
    print("  least privilege")
    for node in sorted(least, key=lambda n: (least[n], n)):
        if node != START:
            h = least[node]
            print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node}")
    print(f"    reachable                           {len(least) - 1}")

    print()
    print("  with one extra table")
    for node in sorted(default, key=lambda n: (default[n], n)):
        if node == START:
            continue
        h = default[node]
        mark = "" if node in least else "   <- only through the extra grant"
        print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node:<26}{mark}")
    print(f"    reachable                           {len(default) - 1}")

    extra = sorted(set(default) - set(least), key=lambda n: (default[n], n))
    print()
    print(f"  one table added                     {len(extra)} resources to the radius")
    for node in extra:
        print(f"    {node}")
    print()
    print(f"  the radius grew from {len(least) - 1} to {len(default) - 1}, "
          f"a factor of {(len(default) - 1) / (len(least) - 1):.1f}.")
    print("  nobody would describe that grant as broad.")


if __name__ == "__main__":
    main()
