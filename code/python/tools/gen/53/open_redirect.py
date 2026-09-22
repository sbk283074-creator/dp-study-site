#!/usr/bin/env python3
"""Chapter 53 demo, part 4 -- the redirect check that passes the bad target.

An open redirect is a login page that sends you wherever the query string says.
The fix is a check on the target, and the check is usually written against the
one attack the author had in mind -- a target that starts with two slashes.

Twelve targets, three validators. The third is the one that accounts for the
browser's rules rather than for the string's shape.
"""
from urllib.parse import urlparse

TARGETS = [
    ("/settings", False),
    ("/notes/12?tab=body", False),
    ("//evil.com", True),
    ("///evil.com", True),
    ("/\\evil.com", True),
    ("\\/evil.com", True),
    ("\\evil.com", True),
    ("https://evil.com", True),
    ("https:evil.com", True),
    ("http:///evil.com", True),
    ("/%2F%2Fevil.com", True),
    ("/settings?next=//evil.com", False),
]


def starts_with_slash(target):
    return target.startswith("/")


def no_netloc(target):
    return urlparse(target).netloc == ""


def no_netloc_and_relative(target):
    if urlparse(target).netloc:
        return False
    if not target.startswith("/"):
        return False
    if target.startswith("//"):
        return False
    if "\\" in target:
        return False
    return True


VALIDATORS = [
    ("startswith('/')", starts_with_slash),
    ("urlparse netloc empty", no_netloc),
    ("+ not '//' + no backslash", no_netloc_and_relative),
]


def main():
    print(f"  targets                            {len(TARGETS):>3}")
    print(f"  should be refused                  "
          f"{sum(1 for _t, bad in TARGETS if bad):>3}")
    print()
    print(f"    {'validator':<26}{'accepted':>9}{'legitimate':>12}")

    accepted_bad = {}
    for name, fn in VALIDATORS:
        good = sum(1 for t, bad in TARGETS if not bad and fn(t))
        bad = sum(1 for t, bad in TARGETS if bad and fn(t))
        accepted_bad[name] = [t for t, is_bad in TARGETS if is_bad and fn(t)]
        print(f"    {name:<26}{bad:>9}{good:>12}")

    print()
    print("  the hostile targets each validator accepts")
    for name, _fn in VALIDATORS:
        targets = accepted_bad[name]
        print(f"    {name:<26}{len(targets)}")
        for t in targets:
            print(f"      {t}")

    print()
    print(f"  the first check accepts {len(accepted_bad['startswith(\'/\')'])}"
          f" of the {sum(1 for _t, bad in TARGETS if bad)}. it asks whether")
    print("  the target begins with a slash, and every one of the four it")
    print("  accepts does -- they simply continue with another one, or with a")
    print("  backslash, which the browser reads as one.")
    print()
    print("  the second check is the one that looks correct and is not. it")
    print("  accepts seven, more than the check it replaced, because")
    print("  urlparse leaves the netloc empty for anything it does not")
    print("  recognise as a host -- a backslash, a scheme with no slashes, a")
    print("  triple slash -- and an empty netloc is what the check is looking")
    print("  for.")
    print()
    print("  the third check accepts one, and the one it accepts is the")
    print("  percent-encoded target. it is refused by nothing here because")
    print("  nothing here decodes, and a browser that decodes it before")
    print("  following it turns it back into a protocol-relative url.")
    print()
    print("  that is the difference the third check encodes. a validator for")
    print("  a url has to know which characters the consumer treats as")
    print("  separators, and the consumer is the browser, not the parser you")
    print("  happened to use. the remaining one is the same lesson one layer")
    print("  down: the consumer also decodes, and the check does not.")


if __name__ == "__main__":
    main()
