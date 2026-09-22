#!/usr/bin/env python3
"""Chapter 50 demo, part 9 -- the blast radius of one credential.

Least privilege is usually argued as a matter of taste. It is not: it is a
count of what one stolen credential reaches, and the count is computed by the
same breadth-first search as Chapter 47.

The graph here is a credential graph, not a network graph. An edge u -> v means
"u holds something that grants access to v", which is why the traversal crosses
layers that the network diagram shows as separate: a database account reaches
a production shell without any network path between them, because a value
stored in a table is a credential.

Two grants are compared. They differ by three tables.
"""

# The grant a new service is given by default, and the grant it needs.
LEAST_PRIVILEGE = [
    ("app db account", "users table"),
    ("app db account", "decks table"),
    ("app db account", "cards table"),
]

EXTRA_BY_DEFAULT = [
    ("app db account", "config table"),
    ("app db account", "sessions table"),
    ("app db account", "request log"),
]

# Everything downstream: what each resource contains, and what that unlocks.
DOWNSTREAM = [
    ("config table", "s3 key"),
    ("s3 key", "backup bucket"),
    ("backup bucket", "nightly db dump"),
    ("nightly db dump", "admin password hash"),
    ("admin password hash", "prod shell"),
    ("prod shell", "secrets manager"),
    ("prod shell", "audit log"),
    ("secrets manager", "billing api"),
    ("secrets manager", "github token"),
    ("github token", "source repo"),
    ("source repo", "ci runner"),
    ("ci runner", "prod shell"),
]

START = "app db account"


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
    least = bfs(LEAST_PRIVILEGE + DOWNSTREAM, START)
    actual = bfs(LEAST_PRIVILEGE + EXTRA_BY_DEFAULT + DOWNSTREAM, START)

    print(f"  edges in the credential graph        "
          f"{len(LEAST_PRIVILEGE) + len(EXTRA_BY_DEFAULT) + len(DOWNSTREAM):>3}")
    print(f"  starting from                        {START}")

    print()
    print("  least privilege: three tables, and nothing downstream of them")
    for node in sorted(least, key=lambda n: (least[n], n)):
        if node == START:
            continue
        h = least[node]
        print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node}")
    print(f"    reachable resources                {len(least) - 1:>3}")

    print()
    print("  the same account, with the three tables it was given by default")
    for node in sorted(actual, key=lambda n: (actual[n], n)):
        if node == START:
            continue
        h = actual[node]
        mark = "" if node in least else "   <- only reachable through the extra grant"
        print(f"    {h:>2} hop{'' if h == 1 else 's'}   {node:<22}{mark}")

    # Tie-break by name. Sorting on the hop count alone is not deterministic:
    # the input is a set, so equal-hop nodes come out in hash order.
    only_actual = sorted(set(actual) - set(least), key=lambda n: (actual[n], n))
    print()
    print(f"    reachable resources                {len(actual) - 1:>3}")
    print(f"    reachable only via the extras      {len(only_actual):>3}"
          f"   {', '.join(only_actual)}")

    print()
    print(f"  three extra tables turn {len(least) - 1} reachable resources into "
          f"{len(actual) - 1}.")
    factor = (len(actual) - 1) / (len(least) - 1)
    print(f"  that is {factor:.1f}x the blast radius, from a grant nobody would call broad.")

    # The hop that makes it cross a layer boundary: table -> shell.
    if "prod shell" in actual:
        print()
        print(f"  the database account reaches a production shell in "
              f"{actual['prod shell']} hops.")
        print(f"  no network path connects them. A value in a table does.")


if __name__ == "__main__":
    main()
