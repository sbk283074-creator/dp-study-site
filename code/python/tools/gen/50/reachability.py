#!/usr/bin/env python3
"""Chapter 50 demo, part 6 -- "it is only reachable from inside".

The claim is almost always true when it is made and false when it matters,
because it is a claim about the network and the network is not the only way
in. This script walks the deployment graph from the internet and reports
which components are actually reachable.

The result worth sitting with is not the two components the URL-fetch bug
exposes. It is the ten that were already reachable before the bug existed.
"Internal" is doing less work in that sentence than anybody thinks, and the
count is how you find out how much less.

Reachability is breadth-first search over the directed graph, which is the
same algorithm as Chapter 47's -- a shortest path here is a number of hops.
"""

COMPONENTS = [
    "cdn", "proxy", "app", "worker", "db", "cache", "objects", "backup",
    "bastion", "admin_cli", "metadata", "metrics", "external_api",
]

# Directed: u -> v means u can open a connection to v.
FLOWS = [
    ("internet", "cdn"),
    ("internet", "proxy"),
    ("cdn", "proxy"),
    ("proxy", "app"),
    ("app", "db"),
    ("app", "cache"),
    ("app", "objects"),
    ("app", "worker"),
    ("app", "external_api"),
    ("worker", "db"),
    ("worker", "objects"),
    ("db", "backup"),
    ("bastion", "admin_cli"),
    ("admin_cli", "db"),
]

# The edges that exist only because the app fetches a URL it was given.
SSRF_FLOWS = [
    ("app", "metadata"),
    ("app", "metrics"),
]

# Does reaching this component require a credential?
NEEDS_CREDENTIAL = {
    "cdn": False,
    "proxy": False,
    "app": True,          # a session, for the routes that have one
    "worker": False,
    "db": True,
    "cache": True,
    "objects": False,
    "backup": False,
    "bastion": True,
    "admin_cli": True,
    "metadata": False,
    "metrics": False,
    "external_api": True,
}


def bfs(edges, source):
    """Return {node: hops} for everything reachable from source."""
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
    base = bfs(FLOWS, "internet")
    with_ssrf = bfs(FLOWS + SSRF_FLOWS, "internet")

    reachable = [c for c in COMPONENTS if c in base]
    unreachable = [c for c in COMPONENTS if c not in base]
    ssrf_only = sorted(set(with_ssrf) - set(base))

    print(f"  components in the deployment        {len(COMPONENTS):>3}")
    print(f"  reachable from the internet         {len(reachable):>3}"
          f"   ({len(reachable) / len(COMPONENTS):.1%})")
    print(f"  not reachable from the internet     {len(unreachable):>3}"
          f"   {', '.join(unreachable)}")

    print()
    print("  hops from the internet")
    for node in sorted(base, key=lambda n: (base[n], n)):
        if node == "internet":
            continue
        hops = base[node]
        cred = "credential required" if NEEDS_CREDENTIAL.get(node) else "NO CREDENTIAL"
        print(f"    {hops:>2} hop{'' if hops == 1 else 's':<1}  {node:<14}{cred}")

    open_nodes = [n for n in reachable if not NEEDS_CREDENTIAL.get(n)]
    print()
    print(f"  reachable and needing no credential {len(open_nodes):>3} of {len(reachable)}"
          f"   {', '.join(sorted(open_nodes))}")
    locked = [n for n in unreachable if NEEDS_CREDENTIAL.get(n)]
    unlocked = [n for n in unreachable if not NEEDS_CREDENTIAL.get(n)]
    print(f"  unreachable, credential required    {len(locked):>3}"
          f"   {', '.join(sorted(locked))}")
    print(f"  unreachable, no credential either   {len(unlocked):>3}"
          f"   {', '.join(sorted(unlocked))}")

    print()
    print("  now add the app's URL-fetch endpoint, which takes a URL from the request")
    for node in ssrf_only:
        print(f"    newly reachable   {node:<14}{with_ssrf[node]} hops"
              f"   {'NO CREDENTIAL' if not NEEDS_CREDENTIAL.get(node) else 'credential required'}")
    print(f"    reachable before   {len(reachable):>3}")
    print(f"    reachable after    {len([c for c in COMPONENTS if c in with_ssrf]):>3}"
          f"   (+{len(ssrf_only)})")
    print()
    print("  the fetch bug added "
          f"{len(ssrf_only)} component(s). "
          f"{len(reachable)} were already reachable without it.")


if __name__ == "__main__":
    main()
