#!/usr/bin/env python3
"""Chapter 51 demo, part 8 -- the check must run after the normalisation.

A blocklist that looks for `../` is not wrong. It is wrong *in the position it
is usually placed*, which is before the value has been decoded. The value that
reaches the file system is not the value that arrived in the request; there is
a decoding step in between, and a check that runs on the wrong side of it is
checking a string nobody will use.

Nine payloads, three placements. The third placement decodes until the value
stops changing, which is the property that makes a normalisation usable as a
security boundary: it has to be idempotent.
"""
import urllib.parse

PAYLOADS = [
    "../etc/passwd",
    "%2e%2e%2fetc/passwd",
    "..%2fetc/passwd",
    "%252e%252e%252fetc/passwd",
    "....//etc/passwd",
    "..%5cetc%5cpasswd",
    "%2e./etc/passwd",
    "..%2Fetc%2Fpasswd",
    "....//....//etc/passwd",
]


def is_traversal(value):
    v = value.replace("\\", "/")
    return "../" in v or v.startswith("/") or v.endswith("/..")


def normalise_once(value):
    return urllib.parse.unquote(value)


def normalise_stable(value):
    """Decode until the value stops changing, then fold separators."""
    seen = value
    while True:
        nxt = normalise_once(seen)
        if nxt == seen:
            break
        seen = nxt
    return seen.replace("\\", "/")


def passes_needed(value):
    n, seen = 0, value
    while True:
        nxt = normalise_once(seen)
        if nxt == seen:
            return n
        seen, n = nxt, n + 1


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print()
    print(f"    {'payload':<34}{'raw':>6}{'once':>7}{'stable':>8}{'passes':>8}")

    raw_caught = once_caught = stable_caught = 0
    multi = 0
    for p in PAYLOADS:
        a = is_traversal(p)
        b = is_traversal(normalise_once(p))
        c = is_traversal(normalise_stable(p))
        n = passes_needed(p)
        raw_caught += a
        once_caught += b
        stable_caught += c
        if n > 1:
            multi += 1
        print(f"    {p:<34}{('yes' if a else 'no'):>6}{('yes' if b else 'no'):>7}"
              f"{('yes' if c else 'no'):>8}{n:>8}")

    total = len(PAYLOADS)
    print()
    print(f"  checked before decoding            {raw_caught:>3} of {total}"
          f"   ({raw_caught / total:.1%})")
    print(f"  checked after decoding once        {once_caught:>3} of {total}"
          f"   ({once_caught / total:.1%})")
    print(f"  checked after decoding to a fixed point {stable_caught:>3} of {total}"
          f"   ({stable_caught / total:.1%})")

    print()
    print(f"  payloads needing more than one pass {multi:>3}"
          f"   (the double-encoded one)")

    missed_once = [p for p in PAYLOADS if not is_traversal(normalise_once(p))]
    print(f"  what the one-pass check misses     {len(missed_once):>3}")
    for p in missed_once:
        print(f"    {p}  ->  {normalise_once(p)}")

    print()
    print("  the rule is not 'decode first'. it is 'the value you check must be")
    print("  the value you use' -- and since decoding can be applied more than")
    print("  once by the layers in front of you, the check belongs after the")
    print("  fixed point, not after one call.")


if __name__ == "__main__":
    main()
