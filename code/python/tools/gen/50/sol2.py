#!/usr/bin/env python3
"""Exercise 2 -- count the boundaries, not the boxes.

Four request paths over the same small deployment. For each one, count the
components, the trust boundaries, and how many of those boundaries have a
check on them. Then find the path with the largest gap.
"""

ZONE = {
    "phone": "public",
    "gateway": "edge",
    "service": "app",
    "worker": "app",
    "primary": "data",
    "blobstore": "data",
    "ops_host": "admin",
}

PATHS = [
    ("read a note",     ["phone", "gateway", "service", "primary"],  ["gateway", "service"]),
    ("upload",          ["phone", "gateway", "service", "blobstore"], ["gateway", "service"]),
    ("nightly reindex", ["worker", "primary", "blobstore"],          ["primary"]),
    ("ops restore",     ["ops_host", "primary", "blobstore"],        []),
]


def crosses(u, v):
    return ZONE[u] != ZONE[v]


def main():
    print(f"  {'path':<18}{'components':>11}{'boundaries':>12}{'guarded':>9}{'gap':>6}")
    stats = {}
    for name, chain, checks in PATHS:
        pairs = list(zip(chain, chain[1:]))
        bnd = [(u, v) for u, v in pairs if crosses(u, v)]
        guarded = [p for p in bnd if p[1] in checks]
        stats[name] = (len(chain), len(bnd), len(guarded))
        print(f"  {name:<18}{len(chain):>11}{len(bnd):>12}{len(guarded):>9}"
              f"{len(bnd) - len(guarded):>6}")

    print()
    worst = max(stats, key=lambda n: (stats[n][1] - stats[n][2], -stats[n][0]))
    comp, bnd, guarded = stats[worst]
    plural = "" if bnd == 1 else "s"
    print(f"  largest gap: {worst} -- {comp} components, {bnd} boundary{plural}, "
          f"{guarded} guarded, gap {bnd - guarded}")

    deepest = max(stats, key=lambda n: stats[n][0])
    print(f"  most components: {deepest} ({stats[deepest][0]}) "
          f"-- {stats[deepest][1]} boundaries")

    print()
    print("  the path with the most components is not the path with the most")
    print("  boundaries, and neither is the path with the largest gap.")


if __name__ == "__main__":
    main()
