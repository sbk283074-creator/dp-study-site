"""Chapter 53 -- practice 3.

A route guard and a row scope are two different checks in two different
places. Every endpoint here has a guard; the question is which rows the
answer is allowed to contain.
"""

CALLERS = ["u1", "u2", None]

# label, the guard on the route, who owns the thing the guard is about,
# and the rows the handler ends up reading, as id -> owner
ENDPOINTS = [
    ("GET /notes/12", "parent is the caller's", "u1", {12: "u1"}),
    ("GET /notes/12/comments", "parent is the caller's", "u1", {5: "u1"}),
    ("GET /notes/12/comments/6", "parent is the caller's", "u1", {6: "u2"}),
    ("GET /notes?ids=12,13", "caller has a session", None, {12: "u1", 13: "u2"}),
    ("POST /notes/12/share", "none", None, {12: "u1"}),
]


def serve(endpoint, caller, scope):
    """Return the rows the caller receives, or None if the route guard
    refused the request before the rows were read."""
    _, guard, parent_owner, rows = endpoint
    if guard.startswith("parent") and caller != parent_owner:
        return None
    if guard == "caller has a session" and caller is None:
        return None
    got = []
    for row_id, owner in rows.items():
        if scope == "none" or owner == caller:
            got.append(row_id)
    return got


def verdict(endpoint, caller, scope):
    got = serve(endpoint, caller, scope)
    if got is None:
        return "refused"
    if not got:
        return "no rows"
    _, _, _, rows = endpoint
    if all(rows[r] == caller for r in got):
        return "own"
    return "LEAK"


def count_leaks(scope):
    return sum(1 for e in ENDPOINTS for c in CALLERS
               if verdict(e, c, scope) == "LEAK")


def main():
    print(f"  endpoints                           {len(ENDPOINTS)}")
    print(f"  callers                             {len(CALLERS)}")
    print(f"  pairs tested                        "
          f"{len(ENDPOINTS) * len(CALLERS)}")
    print()

    print("    {:<25}{:<24}{:>8}{:>8}{:>8}".format(
        "endpoint", "the guard", "owner", "other", "anon"))
    for endpoint in ENDPOINTS:
        row = "    {:<25}{:<24}".format(endpoint[0], endpoint[1])
        for caller in CALLERS:
            row += "{:>8}".format(verdict(endpoint, caller, "none"))
        print(row)
    print()

    guarded = count_leaks("none")
    scoped = count_leaks("row")
    print(f"  pairs where a non-owner got data         {guarded}")
    print()
    print("  the same rows, with the scope applied where they are read")
    print(f"    pairs where a non-owner got data       {scoped}")
    print()
    print("  every endpoint above has a guard, and the guard is the part")
    print("  somebody wrote while looking at the route. the third one has")
    print("  a guard that is correct and still leaks: it asks whether the")
    print("  note belongs to the caller, and then reads a comment by id")
    print("  without asking whether that comment belongs to the note. the")
    print("  guard was on the parent and the row was the child, and the")
    print("  two were never connected.")
    print()
    print("  the fourth is the same mistake at the level of a query: the")
    print("  ids came from the caller, so the set of rows is caller-")
    print("  chosen, and a session check does not narrow it. the fifth")
    print("  has no guard at all and is the only one where an anonymous")
    print("  caller reads somebody's data.")
    print()
    print("  the second count is what the fix costs, and it is the same")
    print("  move as putting the rule at the repository instead of at the")
    print("  handler: one scope, applied where the rows are read, and the")
    print("  guard above it becomes a separate question about whether the")
    print("  request should be served at all.")


main()
