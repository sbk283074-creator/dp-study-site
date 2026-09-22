#!/usr/bin/env python3
"""Chapter 50 demo, part 11 -- the test that was scoped, and what the scope left out.

A penetration test is a purchase. You buy a number of days, pointed at a
number of endpoints, and the report says what was found inside that rectangle.
The rectangle is the thing to read first, because a report is a statement
about what was looked at, and the endpoints nobody looked at produce no
findings by construction.

This script counts the rectangle. It is not a story about a careless tester --
the tester did the job they were given. It is a story about a scope being
mistaken for a result.
"""

# name, endpoints, who can reach it, does it require a session, records it holds
SERVICES = [
    ("public API",      18, "internet", True,      0),
    ("admin console",   23, "vpn",      False, 240_000),
    ("internal tools",  20, "internal", False,      0),
]

# What the engagement actually covered.
IN_SCOPE = ["public API"]

# Findings the engagement reported, and their severities.
FINDINGS = [
    ("public API", "low",      "missing security header"),
    ("public API", "low",      "verbose error message"),
    ("public API", "low",      "cookie without SameSite"),
    ("public API", "medium",   "rate limit absent on login"),
]

VPN_ACCOUNTS = 340
SHARED_VPN_ACCOUNTS = 3


def main():
    total_endpoints = sum(s[1] for s in SERVICES)
    in_scope = sum(s[1] for s in SERVICES if s[0] in IN_SCOPE)
    out_scope = total_endpoints - in_scope

    print("  the estate")
    print()
    print(f"    {'service':<16}{'endpoints':>11}{'reachable from':>16}"
          f"{'session required':>18}{'records':>10}")
    for name, eps, reach, auth, records in SERVICES:
        print(f"    {name:<16}{eps:>11}{reach:>16}"
              f"{('yes' if auth else 'NO'):>18}{records:>10,}")

    print()
    print(f"  endpoints in the estate              {total_endpoints:>3}")
    print(f"  endpoints in the engagement scope    {in_scope:>3}"
          f"   ({in_scope / total_endpoints:.1%})")
    print(f"  endpoints nobody looked at           {out_scope:>3}"
          f"   ({out_scope / total_endpoints:.1%})")

    print()
    print("  the report")
    print()
    by_sev = {}
    for service, sev, desc in FINDINGS:
        by_sev.setdefault(sev, []).append((service, desc))
    for sev in ("critical", "high", "medium", "low"):
        got = by_sev.get(sev, [])
        print(f"    {sev:<10}{len(got):>3}")
    print()
    print(f"    findings in scope                  {len(FINDINGS):>3}")
    print(f"    findings out of scope              {0:>3}"
          f"   (no endpoint out of scope was tested)")

    print()
    print("  what the rectangle left out")
    print()
    for name, eps, reach, auth, records in SERVICES:
        if name in IN_SCOPE:
            continue
        why = "no session required" if not auth else "session required"
        print(f"    {name:<16}{eps:>3} endpoints   reachable from {reach:<9}"
              f"{why:<20}{records:>9,} records")

    exposed = [s for s in SERVICES if not s[3] and s[0] not in IN_SCOPE]
    exposed_endpoints = sum(s[1] for s in exposed)
    exposed_records = sum(s[4] for s in exposed)
    print()
    print(f"  endpoints reachable with no session  {exposed_endpoints:>3}")
    print(f"  records behind them                  {exposed_records:>9,}")
    print(f"  reachable with one shared VPN login  {exposed_records:>9,}"
          f"   ({SHARED_VPN_ACCOUNTS} of {VPN_ACCOUNTS} accounts are shared)")

    print()
    print("  the fix")
    print("    one session middleware, applied to the two services that lack it")
    print(f"    covers {exposed_endpoints} endpoints, {exposed_records:,} records, "
          f"in one change")

    print()
    print(f"  the report said {len(FINDINGS)} findings, all in the {in_scope} endpoints"
          f" it was pointed at.")
    print(f"  the {out_scope} it was not pointed at held "
          f"{exposed_records:,} records and no session check.")


if __name__ == "__main__":
    main()
