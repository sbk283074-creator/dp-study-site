#!/usr/bin/env python3
"""Chapter 53 demo, part 8 -- the log that leaks what it should record.

Logging and monitoring failures are the OWASP category with no syntax-level fix,
which is why they are easy to leave out of a chapter like this and why they
belong in it. The category is usually described as "you did not log enough",
and half the problem runs the other way.

Ten event types, sixty requests. For each type: does the application write a
line, does the line carry a credential, and is the event one an incident review
would need.
"""
# name, requests, is a line written, does the line carry a credential,
# is the event security-relevant
EVENTS = [
    ("login success", 12, True, True, True),
    ("login failure", 8, True, True, True),
    ("password reset", 2, True, True, True),
    ("token refresh", 10, True, True, False),
    ("page view", 15, True, False, False),
    ("note created", 6, True, False, False),
    ("permission denied", 3, False, False, True),
    ("role changed", 1, False, False, True),
    ("account locked", 2, False, False, True),
    ("export downloaded", 1, True, False, True),
]


def main():
    total = sum(n for _e, n, _l, _s, _r in EVENTS)
    print(f"  event types                        {len(EVENTS):>3}")
    print(f"  requests                           {total:>3}")
    print()
    print(f"    {'event':<20}{'count':>6}{'logged':>8}{'credential':>12}"
          f"{'needed':>8}")

    lines = 0
    leaky = 0
    needed = 0
    needed_logged = 0
    silent = []
    for name, count, logged, sensitive, relevant in EVENTS:
        if logged:
            lines += count
            if sensitive:
                leaky += count
        if relevant:
            needed += count
            if logged:
                needed_logged += count
            else:
                silent.append((name, count))
        print(f"    {name:<20}{count:>6}{'yes' if logged else 'no':>8}"
              f"{'yes' if sensitive else '-':>12}"
              f"{'yes' if relevant else '-':>8}")

    print()
    print(f"  lines written                      {lines:>3} of {total}")
    print(f"  lines carrying a credential        {leaky:>3} of {lines}")
    print(f"  security-relevant requests         {needed:>3}")
    print(f"  of those, requests with no line    "
          f"{needed - needed_logged:>3}")

    print()
    print("  security-relevant events that leave no trace at all")
    for name, count in silent:
        print(f"    {name:<20}{count}")

    print()
    print("  two numbers, and they are opposite problems in the same file.")
    print()
    print(f"  {leaky} of the {lines} lines written carry a credential, because")
    print("  the line is built from the request body and the request body is")
    print("  where the password is. the log is the most copied artefact in an")
    print("  incident and the least protected one in most systems.")
    print()
    print(f"  and {needed - needed_logged} of the {needed} requests an incident")
    print("  review would need produced no line, because nobody decided they")
    print("  should. the ones missing are the failures and the changes: a")
    print("  refusal, a role change, a lockout. those are the events that")
    print("  describe an attack, and they are the ones nobody is watching")
    print("  for, because a successful request is the thing the log was")
    print("  built to record.")
    print()
    print("  the fix for the first is a field allow-list rather than a body")
    print("  dump. the fix for the second is a list of events that must")
    print("  always produce a line, written down and tested like any other")
    print("  requirement -- which is the whole of the category, and the")
    print("  reason it has no syntax-level fix.")


if __name__ == "__main__":
    main()
