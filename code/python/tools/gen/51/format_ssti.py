#!/usr/bin/env python3
"""Chapter 51 demo, part 4 -- the template engine is a code path.

Server-side template injection is usually taught with a template library,
which hides the mechanism behind the interesting question: which string was
the *template*? This script uses `str.format`, which is in the standard
library and is enough to show the whole thing.

`str.format` evaluates attribute access and indexing inside the braces. So a
string that reaches `.format()` as the format string is a program, and a
string that reaches it as an argument is data. The payload set is the same in
both cases; only the position changes.

Nothing prints a payload's *result*, because a repr of a class contains an
address. The script counts whether a payload expanded and whether it read the
attribute it was aiming at.
"""


class Vault:
    def __init__(self):
        self.secret = "s3cr3t"


PAYLOADS = [
    "{0}",
    "{0.secret}",
    "{0.__class__}",
    "{0.__class__.__mro__}",
    "{0.__class__.__mro__[1].__subclasses__}",
    "{0.__init__.__globals__}",
    "{0[0]}",
]

FIXED = "Hello, {name}!"


def main():
    thing = Vault()

    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  the object passed to format()      Vault(secret={thing.secret!r})")
    print()
    print(f"    {'payload':<46}{'as the template':>16}{'as an argument':>15}")

    expanded, leaked = 0, 0
    as_data = 0
    for p in PAYLOADS:
        # The payload is the template: it is parsed.
        try:
            out = p.format(thing)
            did_expand = True
        except (AttributeError, IndexError, KeyError, TypeError, ValueError):
            did_expand = False
        if did_expand:
            expanded += 1
            if thing.secret in out:
                leaked += 1

        # The payload is an argument: it is a value.
        out2 = FIXED.format(name=p)
        if p in out2:
            as_data += 1

        print(f"    {p:<46}{('yes' if did_expand else 'no'):>16}"
              f"{('data' if p in out2 else '?'):>15}")

    print()
    print(f"  payloads that expanded as the template      {expanded} of {len(PAYLOADS)}")
    print(f"  of those, payloads that read .secret        {leaked}")
    print(f"  payloads treated as data as an argument     {as_data} of {len(PAYLOADS)}")

    # The minimal fix for this mechanism, measured the same way. Note the test
    # cannot be "did it raise" -- nothing raises once the braces are doubled;
    # the question is whether the payload came back as data.
    doubled_as_data = 0
    for p in PAYLOADS:
        doubled = p.replace("{", "{{").replace("}", "}}")
        try:
            out = doubled.format(thing)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError):
            continue
        if out == p:
            doubled_as_data += 1
    print()
    print(f"  with braces doubled first                   {doubled_as_data} of "
          f"{len(PAYLOADS)} come back as data")

    print()
    print(f"  the same payloads, the same call. the two columns disagree on {expanded}")
    print(f"  of the {len(PAYLOADS)} rows -- every row where the payload was interpreted as a")
    print("  template. the vulnerability is not in the payload.")


if __name__ == "__main__":
    main()
