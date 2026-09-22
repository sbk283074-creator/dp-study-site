#!/usr/bin/env python3
"""Chapter 50 demo, part 8 -- the check that fails open.

An authorization check can fail in three ways: it says yes, it says no, or it
throws. The first two are the ones people write tests for. The third is the
one that decides whether the design is safe, and it is decided by a single
word in the except clause.

This script runs the same ten thousand requests through both call sites. The
two implementations differ by one token and produce identical responses on
almost all of them, which is exactly why the mistake survives code review: on
the traffic you test with, the two are the same program.

Nothing is timed. Every count is exact over the fixed request sequence.
"""

# The directory of accounts. Ids 970-996 were deleted but tokens for them are
# still in the wild, so a lookup for one of them raises.
DIRECTORY = set(range(970))
ID_SPACE = 997          # prime, so the request sequence cycles irregularly
REQUESTS = 10_000


def authorize(user_id, resource):
    """Raise when the account is gone. That is the whole point."""
    if user_id not in DIRECTORY:
        raise LookupError(f"no such account: {user_id}")
    return resource.owner == user_id


def fails_open(user_id, resource):
    try:
        return authorize(user_id, resource)
    except Exception:
        return True         # the one word


def fails_closed(user_id, resource):
    try:
        return authorize(user_id, resource)
    except Exception:
        return False        # the other one


class Resource:
    def __init__(self, owner):
        self.owner = owner


def main():
    resource = Resource(owner=3)
    stream = [i % ID_SPACE for i in range(REQUESTS)]

    errors = [u for u in stream if u not in DIRECTORY]
    open_allowed = sum(1 for u in stream if fails_open(u, resource))
    closed_allowed = sum(1 for u in stream if fails_closed(u, resource))
    differ = sum(1 for u in stream
                 if fails_open(u, resource) != fails_closed(u, resource))

    print(f"  accounts in the directory            {len(DIRECTORY):>6}")
    print(f"  ids the sequence can produce         {ID_SPACE:>6}")
    print(f"  ids with no account                  {ID_SPACE - len(DIRECTORY):>6}"
          f"   ({1 - len(DIRECTORY) / ID_SPACE:.2%} of the id space)")
    print(f"  requests                             {REQUESTS:>6}")

    print()
    print(f"  requests that take the error path    {len(errors):>6}"
          f"   ({len(errors) / REQUESTS:.2%})")
    print()
    print(f"  allowed by the failing-open site     {open_allowed:>6}"
          f"   ({open_allowed / REQUESTS:.2%})")
    print(f"  allowed by the failing-closed site   {closed_allowed:>6}"
          f"   ({closed_allowed / REQUESTS:.2%})")
    print(f"  requests where the two disagree      {differ:>6}"
          f"   ({differ / REQUESTS:.2%})")

    print()
    print(f"  requests authorised without a check  {differ:>6}")
    print(f"  requests where the two are identical {REQUESTS - differ:>6}"
          f"   ({(REQUESTS - differ) / REQUESTS:.2%})")

    print()
    print("  a year of this, at ten thousand requests a day")
    print(f"    requests authorised unchecked      {differ * 365:>9,}/year")

    print()
    print("  what a test suite sees")
    print(f"    a test that logs in as a valid user     both sites agree")
    print(f"    a test that checks a 403                both sites agree")
    print(f"    a test with a deleted account's token   the sites differ")
    print()
    print(f"  {differ} of {REQUESTS} requests distinguish them."
          f" The other {(REQUESTS - differ) / REQUESTS:.1%} cannot.")


if __name__ == "__main__":
    main()
