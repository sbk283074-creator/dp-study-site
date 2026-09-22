#!/usr/bin/env python3
"""Chapter 53 demo, part 2 -- the cookie rule that is not all-or-nothing.

SameSite is the setting people reach for after reading about CSRF, and the
sentence they remember is "set it to Lax and the browser stops sending the
cookie". It stops sending it on most cross-site requests. This block encodes the
rule as a table and counts which ones it stops.

The rules here are the specification's, written out rather than measured in a
browser, and the counts are derived from the table. The point is the shape of
the table, not the number of browsers that implement it.
"""
SETTINGS = ["None", "Lax", "Strict"]

# request shape, is it cross-site, is it a top-level navigation, is the method safe
REQUESTS = [
    ("typed URL", False, True, True),
    ("same-site form POST", False, False, False),
    ("cross-site link click", True, True, True),
    ("cross-site form POST", True, True, False),
    ("cross-site image GET", True, False, True),
    ("cross-site iframe GET", True, False, True),
    ("cross-site fetch GET", True, False, True),
    ("cross-site fetch POST", True, False, False),
]


def sends(setting, cross_site, top_level, safe_method):
    """Does the cookie go out, given the request and the setting?"""
    if setting == "None":
        return True
    if not cross_site:
        return True
    if setting == "Strict":
        return False
    # Lax: a top-level navigation, with a safe method
    return top_level and safe_method


def main():
    print(f"  request shapes                     {len(REQUESTS):>3}")
    print(f"  settings                           {len(SETTINGS):>3}")
    print()
    print(f"    {'request':<24}" + "".join(f"{s:>9}" for s in SETTINGS))

    sent = {s: 0 for s in SETTINGS}
    cross_total = 0
    cross_sent = {s: 0 for s in SETTINGS}
    for label, cross, top, safe in REQUESTS:
        if cross:
            cross_total += 1
        cells = []
        for setting in SETTINGS:
            yes = sends(setting, cross, top, safe)
            cells.append("sent" if yes else "held")
            if yes:
                sent[setting] += 1
                if cross:
                    cross_sent[setting] += 1
        print(f"    {label:<24}" + "".join(f"{c:>9}" for c in cells))

    print()
    for setting in SETTINGS:
        print(f"  SameSite={setting:<7} sent on {sent[setting]:>2} of "
              f"{len(REQUESTS)} shapes, {cross_sent[setting]:>2} of the "
              f"{cross_total} cross-site ones")

    print()
    print("  Strict sends on every same-site request and none of the")
    print("  cross-site ones, which is the setting people imagine when they")
    print("  say \"set it to Lax\".")
    print()
    print("  Lax holds the cookie on all but one of the cross-site shapes,")
    print("  and the one it lets through is a top-level navigation with a")
    print("  safe method. that is the exception the setting exists for --")
    print("  following a link to a page you are logged in to has to work --")
    print("  and it is why \"state changes must not be GETs\" is a rule with")
    print("  consequences rather than a matter of taste.")
    print()
    print("  SameSite=None sent on all of them, which is the setting you get")
    print("  when you need a cookie to work in an iframe or from another")
    print("  origin. it is not a weaker Lax; it is the absence of the")
    print("  protection, and the token is still the thing doing the work.")


if __name__ == "__main__":
    main()
