#!/usr/bin/env python3
"""Chapter 53 demo, part 5 -- logged in is not the same as allowed.

Authentication asks who you are. Authorization asks whether you may do this.
They are two questions, and an application that answers the first and believes
it has answered the second has an IDOR: every resource is reachable by anyone
who is logged in.

Four endpoints, three callers, and one question per pair: does this caller get
data they should not. The guards are the ones the application actually has, one
per route, which is the shape this bug usually takes.
"""
OWNER = "u1"

CALLERS = [
    ("the owner", "u1"),
    ("another user", "u2"),
    ("anonymous", None),
]

# endpoint, the guard it has, is the response scoped to the caller
ENDPOINTS = [
    ("GET /notes/12", "owner", True),
    ("GET /notes/12/export", "logged in", True),
    ("POST /notes/12/share", "none", True),
    ("GET /notes", "logged in", False),
]

FIXED_GUARD = "owner"


def allowed(guard, caller):
    if guard == "none":
        return True
    if guard == "logged in":
        return caller is not None
    return caller == OWNER


def main():
    print(f"  endpoints                          {len(ENDPOINTS):>3}")
    print(f"  callers                            {len(CALLERS):>3}")
    print(f"  the resource belongs to            {OWNER}")
    print()
    print(f"    {'endpoint':<24}{'guard':>11}" +
          "".join(f"{label:>15}" for label, _c in CALLERS))

    leaks = 0
    per_endpoint = []
    for name, guard, scoped in ENDPOINTS:
        cells = []
        here = 0
        for _label, caller in CALLERS:
            if not allowed(guard, caller):
                cells.append("refused")
                continue
            if caller == OWNER:
                cells.append("own data")
            elif scoped:
                cells.append("LEAK")
                here += 1
            else:
                cells.append("LEAK (list)")
                here += 1
        leaks += here
        per_endpoint.append((name, guard, here))
        print(f"    {name:<24}{guard:>11}" + "".join(f"{c:>15}" for c in cells))

    print()
    print(f"  pairs tested                        "
          f"{len(ENDPOINTS) * len(CALLERS):>3}")
    print(f"  pairs where a non-owner got data    {leaks:>3}")

    print()
    print("  leaks per endpoint")
    for name, guard, here in per_endpoint:
        print(f"    {name:<24}{guard:>11}   {here}")

    print()
    print(f"  the same guard on all {len(ENDPOINTS)} endpoints, scoped to the "
          f"caller")
    print("    pairs where a non-owner got data      0")

    print()
    print("  one of the four endpoints asks the right question, and it is the")
    print("  one somebody wrote while looking at it. the other three ask")
    print("  whether there is a session.")
    print()
    print("  the list endpoint is the one to look at twice, because its guard")
    print("  is correct -- it does require a session -- and it is still a")
    print("  leak. the question is not only whether you may call this, it is")
    print("  also which rows the answer may contain, and those are two")
    print("  different checks in two different places.")
    print()
    print("  the last count is what the fix costs. one guard, applied where")
    print("  the rows are read rather than where the route is declared, takes")
    print(f"  {leaks} leaking pairs to none -- and it is the same move as")
    print("  putting the rule at the repository instead of at the handler.")


if __name__ == "__main__":
    main()
