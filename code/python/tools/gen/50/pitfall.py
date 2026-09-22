#!/usr/bin/env python3
"""Chapter 50 demo, part 10 -- where you put the rule decides how many rules you have.

A rule like "only the owner may read this" has to be enforced somewhere. The
number of places it has to be *correct* is not a property of the rule; it is a
property of where you put it, and the two answers differ by an order of
magnitude once the codebase has grown.

This script counts the enforcement sites for the same application under two
designs across five releases. The route-level design needs one correct site
per route that touches owned data. The repository-level design needs one site
in total, and every exception to it is an explicit declaration.

The second half is about the failure mode, which is the part that decides how
long the bug lives. One design fails silently; the other fails in the first
test run.
"""

# release, routes added that read owned data
RELEASES = [("R1", 0), ("R2", 2), ("R3", 3), ("R4", 2), ("R5", 2)]
STARTING_ROUTES = 12

# The genuinely public reads, which are the same under both designs.
PUBLIC_READS = ["GET /health", "GET /decks (shared)", "GET /search", "POST /login"]


def main():
    print(f"  routes that read owned data at R1    {STARTING_ROUTES:>3}")
    print(f"  releases                             {len(RELEASES):>3}")
    print()
    print(f"    {'release':<9}{'added':>7}{'total routes':>14}"
          f"{'route-level sites':>19}{'repository sites':>18}")

    total = STARTING_ROUTES
    for name, added in RELEASES:
        total += added
        print(f"    {name:<9}{added:>7}{total:>14}{total:>19}{1:>18}")

    print()
    print(f"  after {len(RELEASES)} releases")
    print(f"    route-level:     {total} sites must each be correct")
    print(f"    repository-level: 1 site, plus {len(PUBLIC_READS)} explicit public reads")
    print(f"    sites added by the last {len(RELEASES)} releases: "
          f"{total - STARTING_ROUTES} under the first design, 0 under the second")

    print()
    print("  the failure modes, which is what decides how long the bug lives")
    print()
    print(f"    {'design':<18}{'a forgotten site':<36}{'what the caller sees'}")
    print(f"    {'route-level':<18}{'returns rows owned by someone else':<36}"
          f"{'200 OK, plausible body'}")
    print(f"    {'repository-level':<18}{'raises on the missing opt-out':<36}"
          f"{'500 in the first test run'}")

    print()
    print(f"  route-level: 1 forgotten site out of {total} exposes "
          f"{1 / total:.1%} of the owned-data routes, silently.")
    print(f"  repository-level: a forgotten opt-out breaks "
          f"{len(PUBLIC_READS)} public routes, loudly.")
    print()
    print("  a silent failure on one route is worse than a loud failure on four.")
    print("  the loud one is found by the next person to run the tests.")


if __name__ == "__main__":
    main()
