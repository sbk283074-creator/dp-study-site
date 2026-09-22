#!/usr/bin/env python3
"""Exercise 1 -- an inventory, and a year of log lines.

A smaller version of the first block, over a different application: six
assets, three controls, and a request trace of three hundred lines.
"""
ASSETS = [
    # name, documented, owned, encrypted
    ("notes",         True,  True,  False),
    ("attachments",   True,  True,  False),
    ("accounts",      True,  True,  True),
    ("sessions",      False, False, False),
    ("api keys",      False, False, True),
    ("audit trail",   False, True,  False),
]

SHAPES = [
    "GET /notes",
    "GET /notes/12",
    "POST /notes title=groceries&body=milk",
    "POST /auth email=sam@example.com&password=correct-horse",
    "GET /me Authorization=Bearer eyJhbGciOiJIUzI1NiJ9",
    "POST /notes/12/attachment file=scan.pdf",
    "GET /share token=eyJhbGciOiJIUzI1NiJ9",
    "DELETE /notes/12",
    "GET /search q=holiday",
    "POST /auth/reset email=sam@example.com",
]

SECRET = ("password", "token", "authorization")
PII = ("@",)
REQUESTS = 300


def main():
    print(f"  assets                              {len(ASSETS):>3}")
    for name, doc, owned, enc in ASSETS:
        bad = sum(1 for v in (doc, owned, enc) if not v)
        print(f"    {name:<14} failing {bad} of 3")

    worst = [a[0] for a in ASSETS if not (a[1] and a[2] and a[3])]
    print(f"  failing at least one control        {len(worst)}")
    print(f"  passing all three                   "
          f"{len(ASSETS) - len(worst)}   "
          f"{[a[0] for a in ASSETS if a[1] and a[2] and a[3]]}")

    trace = [SHAPES[i % len(SHAPES)] for i in range(REQUESTS)]
    secrets = [t for t in trace if any(m in t.lower() for m in SECRET)]
    pii = [t for t in trace if any(m in t for m in PII)]

    print()
    print(f"  log lines                           {len(trace)}")
    print(f"  carrying a credential               {len(secrets)}"
          f"   ({len(secrets) / len(trace):.1%})")
    print(f"  carrying an email                   {len(pii)}"
          f"   ({len(pii) / len(trace):.1%})")

    leaky = [s for s in SHAPES if any(m in s.lower() for m in SECRET)]
    print(f"  shapes responsible                  {len(leaky)} of {len(SHAPES)}")
    for s in leaky:
        print(f"    {s}")

    print()
    print(f"  a year at {REQUESTS} a day: "
          f"{len(secrets) * 365:,} credential-bearing lines")


if __name__ == "__main__":
    main()
