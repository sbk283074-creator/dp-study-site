#!/usr/bin/env python3
"""Chapter 50 demo, part 2 -- trust boundaries, counted.

A trust boundary is a place where the level of trust changes: where data
moves out of something you do not control into something you do, or the other
way round. Three counts matter and they are three different numbers:

  * how many components a request touches
  * how many trust boundaries it crosses
  * how many of those crossings have a check on them

The gap between the last two is the exposure, and it is not proportional to
the first. The path with the fewest components here has the only completely
unguarded boundary in the table, because it points outward -- and outbound
flows are the ones nobody draws on the diagram.

Nothing is timed; every number is a count over a fixed model of the
deployment.
"""

# Which trust zone each component sits in. Rank rises with trust: the public
# internet is 0 and the administrative network is 4.
ZONE_RANK = {"public": 0, "edge": 1, "app": 2, "data": 3, "admin": 4}

ZONE_OF = {
    "browser": "public",
    "external_api": "public",
    "cdn": "edge",
    "proxy": "edge",
    "app": "app",
    "worker": "app",
    "db": "data",
    "cache": "data",
    "objects": "data",
    "backup": "data",
    "bastion": "admin",
    "admin_cli": "admin",
}

# Every data flow in the deployment, as (from, to).
EDGES = [
    ("browser", "cdn"),
    ("cdn", "proxy"),
    ("proxy", "app"),
    ("app", "worker"),
    ("app", "db"),
    ("app", "cache"),
    ("app", "objects"),
    ("app", "external_api"),
    ("worker", "db"),
    ("worker", "objects"),
    ("db", "backup"),
    ("bastion", "admin_cli"),
    ("admin_cli", "db"),
]

# name, the components in order, the components that actually check what
# arrives at them.
PATHS = [
    ("login",        ["browser", "cdn", "proxy", "app", "db"],               ["proxy", "app", "db"]),
    ("render feed",  ["browser", "cdn", "proxy", "app", "cache"],            ["proxy", "app", "cache"]),
    ("upload",       ["browser", "cdn", "proxy", "app", "objects"],          ["proxy", "app"]),
    ("webhook in",   ["external_api", "app", "db"],                          ["app", "db"]),
    ("nightly job",  ["worker", "db", "objects"],                            ["db"]),
    ("admin export", ["bastion", "admin_cli", "db", "objects"],              ["admin_cli", "db"]),
    ("fetch image",  ["app", "external_api"],                                []),
]


def crosses(u, v):
    """Does the flow u -> v leave its zone?"""
    return ZONE_OF[u] != ZONE_OF[v]


def direction(u, v):
    """Inward means towards more trust; outward means towards less."""
    return "in" if ZONE_RANK[ZONE_OF[v]] > ZONE_RANK[ZONE_OF[u]] else "out"


def main():
    print("The deployment, by zone")
    print()
    for zone in sorted(ZONE_RANK, key=lambda z: ZONE_RANK[z]):
        names = [c for c in ZONE_OF if ZONE_OF[c] == zone]
        print(f"  {zone:<8} rank {ZONE_RANK[zone]}   {len(names):>2} components   "
              + ", ".join(sorted(names)))

    boundary_edges = [(u, v) for u, v in EDGES if crosses(u, v)]
    internal_edges = [(u, v) for u, v in EDGES if not crosses(u, v)]
    outward = [(u, v) for u, v in boundary_edges if direction(u, v) == "out"]

    print()
    print(f"  data flows in the model            {len(EDGES):>3}")
    print(f"  flows that cross a boundary        {len(boundary_edges):>3}"
          f"   ({len(boundary_edges) / len(EDGES):.1%})")
    print(f"  flows inside one zone              {len(internal_edges):>3}"
          f"   (these are the ones called \"internal\")")
    print(f"  boundary crossings pointing out    {len(outward):>3}"
          f"   {', '.join(f'{u}->{v}' for u, v in outward)}")

    print()
    print("Per request path: components, boundaries, checks, gap")
    print()
    print(f"  {'path':<14}{'components':>11}{'boundaries':>12}{'guarded':>9}{'gap':>6}"
          f"   the boundaries it crosses")
    totals = {"comp": 0, "bound": 0, "guarded": 0}
    for name, chain, checks in PATHS:
        pairs = list(zip(chain, chain[1:]))
        bnd = [(u, v) for u, v in pairs if crosses(u, v)]
        guarded = [(u, v) for u, v in bnd if v in checks]
        gap = len(bnd) - len(guarded)
        totals["comp"] += len(chain)
        totals["bound"] += len(bnd)
        totals["guarded"] += len(guarded)
        shown = " ".join(f"{u}->{v}({direction(u, v)})" for u, v in bnd)
        print(f"  {name:<14}{len(chain):>11}{len(bnd):>12}{len(guarded):>9}{gap:>6}   {shown}")

    print()
    print(f"  {'totals':<14}{totals['comp']:>11}{totals['bound']:>12}"
          f"{totals['guarded']:>9}{totals['bound'] - totals['guarded']:>6}")

    # Pull the rows worth talking about out of the table by *computed* property
    # rather than by name, so the prose cannot drift away from the data.
    stats = {}
    for name, chain, checks in PATHS:
        pairs = list(zip(chain, chain[1:]))
        bnd = [(u, v) for u, v in pairs if crosses(u, v)]
        guarded = [p for p in bnd if p[1] in checks]
        stats[name] = {
            "comp": len(chain),
            "bnd": len(bnd),
            "guarded": len(guarded),
            "gap": len(bnd) - len(guarded),
            "ratio": len(bnd) / len(chain),
            "all_out": bool(bnd) and all(direction(u, v) == "out" for u, v in bnd),
        }

    densest = max(stats, key=lambda n: stats[n]["ratio"])
    sparsest = min(stats, key=lambda n: stats[n]["ratio"])
    biggest_gap = max(stats, key=lambda n: (stats[n]["gap"], -stats[n]["comp"]))
    outward_open = [n for n in stats if stats[n]["all_out"] and stats[n]["gap"] > 0]

    print()
    print("  boundaries per component -- the same depth of system, two answers")
    for label, name in (("densest", densest), ("sparsest", sparsest)):
        s = stats[name]
        print(f"    {label:<10} {name:<14} {s['comp']} components, {s['bnd']} boundaries"
              f"   ({s['ratio']:.3f} per component)")
    print()
    print(f"  the largest unguarded gap   {biggest_gap:<14} "
          f"{stats[biggest_gap]['comp']} components, {stats[biggest_gap]['bnd']} boundaries, "
          f"{stats[biggest_gap]['guarded']} guarded, gap {stats[biggest_gap]['gap']}")
    for name in outward_open:
        s = stats[name]
        print(f"  the only wholly unguarded, outward path   {name:<12} "
              f"{s['comp']} components, {s['bnd']} boundary, {s['guarded']} guarded")


if __name__ == "__main__":
    main()
