#!/usr/bin/env python3
"""Chapter 53 demo, part 3 -- the allow-list that matches too much.

SSRF is the bug where your server makes a request on the caller's behalf, and
the fix everybody reaches for is a list of hosts the server is allowed to reach.
The list is the right idea. The matching is where it goes wrong, and there are
four ways to write the same list that accept different things.

Sixteen URLs, one of which is the legitimate target. Four validators.
"""
import ipaddress
from urllib.parse import urlparse

ALLOWED_HOST = "api.example.com"
LEGITIMATE = "https://api.example.com/v1/items"

# url, is it a request we should refuse
URLS = [
    (LEGITIMATE, False),
    ("https://api.example.com/v1/other", False),
    ("https://api.example.com.evil.com/v1", True),
    ("https://notexample.com/v1", True),
    ("https://api.example.com@evil.com/v1", True),
    ("https://evil.com/?u=https://api.example.com", True),
    ("http://api.example.com/v1", True),
    ("http://127.0.0.1:8000/admin", True),
    ("http://169.254.169.254/latest/meta-data/", True),
    ("http://[::1]/admin", True),
    ("http://2130706433/admin", True),
    ("http://0x7f000001/admin", True),
    ("http://0177.0.0.1/admin", True),
    ("file:///etc/passwd", True),
    ("gopher://api.example.com/x", True),
    ("https://api.example.com./v1", True),
]


def prefix(url):
    return url.startswith("https://api.example.com")


def suffix(url):
    host = urlparse(url).hostname or ""
    return host.endswith("example.com")


def exact_host(url):
    return urlparse(url).hostname == ALLOWED_HOST


def exact_host_and_public(url):
    parts = urlparse(url)
    if parts.scheme != "https" or parts.hostname != ALLOWED_HOST:
        return False
    try:
        ip = ipaddress.ip_address(parts.hostname)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved)


VALIDATORS = [
    ("startswith", prefix),
    ("hostname endswith", suffix),
    ("hostname ==", exact_host),
    ("host + public IP", exact_host_and_public),
]


def main():
    legit = sum(1 for _u, bad in URLS if not bad)
    print(f"  urls                               {len(URLS):>3}")
    print(f"  should be refused                  "
          f"{len(URLS) - legit:>3}")
    print(f"  the allow-list                     {ALLOWED_HOST}")
    print()
    print(f"    {'validator':<20}{'accepted':>9}{'legitimate':>12}"
          f"{'refused that should pass':>26}")

    accepted_bad = {}
    for name, fn in VALIDATORS:
        good = sum(1 for u, bad in URLS if not bad and fn(u))
        bad = sum(1 for u, bad in URLS if bad and fn(u))
        accepted_bad[name] = [u for u, is_bad in URLS if is_bad and fn(u)]
        print(f"    {name:<20}{bad:>9}{good:>12}{legit - good:>26}")

    print()
    print("  the hostile urls each validator accepts")
    for name, _fn in VALIDATORS:
        urls = accepted_bad[name]
        print(f"    {name:<20}{len(urls)}")
        for u in urls:
            print(f"      {u}")

    print()
    print("  read the four accepted lists as a sequence rather than as four")
    print("  attempts. each one removes a class the one above it missed, and")
    print("  the classes are different in kind.")
    print()
    print("  `startswith` accepts three, and all three are the string")
    print("  beginning with the allowed host without the host being that host:")
    print("  a longer name that starts with it, a userinfo section that is")
    print("  it, and a trailing dot that makes it a different name.")
    print()
    print("  `endswith` accepts three, and they are not the same three. it")
    print("  drops the userinfo and the trailing dot, and it accepts a")
    print("  domain that ends with the allowed one without a dot in front of")
    print("  it -- plus two urls whose scheme is not https at all. a")
    print("  hostname check is not a scheme check.")
    print()
    print("  comparing the hostname drops the domain-suffix case and still")
    print("  accepts the two wrong schemes, which is what the fourth")
    print("  validator is for. it checks the scheme and the hostname, and")
    print("  then asks what the hostname is if it happens to be an address.")
    print("  nothing here resolves anything, so this is the shape of the")
    print("  check rather than the whole of it -- but the shape is the point:")
    print("  a check on the name is not a check on where the connection goes.")


if __name__ == "__main__":
    main()
