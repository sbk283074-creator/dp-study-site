"""Chapter 53 -- practice 2.

A fetch service that takes a url from a user. Five ways to reach an
address the service should not reach, against four validators whose only
difference is the moment each question is asked.
"""

import ipaddress

PUBLIC = "93.184.216.34"
INTERNAL = "10.0.0.7"
MAPPED = "::ffff:10.0.0.7"

ALLOWED = ["cdn.example.com", "files.example.com",
           "internal.example.com", "mapped.example.com"]


def looks_private(addr):
    """The version that knows the spellings somebody wrote down."""
    return (addr.startswith("10.") or addr.startswith("192.168.")
            or addr.startswith("127.") or addr == "::1")


def is_internal(addr):
    """The version that asks the address what it is."""
    ip = ipaddress.ip_address(addr)
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_private or ip.is_loopback or ip.is_link_local


class Net:
    def __init__(self, answers):
        self.answers = {h: list(v) for h, v in answers.items()}
        self.reached = []

    def resolve(self, host):
        try:
            ipaddress.ip_address(host)
            return host
        except ValueError:
            pass
        seq = self.answers.get(host)
        if not seq:
            return PUBLIC
        return seq.pop(0) if len(seq) > 1 else seq[0]

    def connect(self, address):
        self.reached.append(address)
        return address


def by_name(net, host):
    if host not in ALLOWED:
        return None
    return net.connect(net.resolve(host))


def by_name_then_address(net, host):
    if host not in ALLOWED:
        return None
    addr = net.resolve(host)
    if looks_private(addr):
        return None
    return net.connect(net.resolve(host))


def by_pinned_address(net, host):
    if host not in ALLOWED:
        return None
    addr = net.resolve(host)
    if is_internal(addr):
        return None
    return net.connect(addr)


VALIDATORS = [
    ("name", by_name, False),
    ("+addr", by_name_then_address, False),
    ("pin", by_pinned_address, False),
    ("hop", by_pinned_address, True),
]

ATTACKS = [
    ("the name rebinds between the check and the connect",
     "cdn.example.com", {"cdn.example.com": [PUBLIC, INTERNAL]}, {}),
    ("a redirect to an address inside",
     "files.example.com", {"files.example.com": [PUBLIC]},
     {"files.example.com": INTERNAL}),
    ("a redirect to a name that points inside",
     "cdn.example.com",
     {"cdn.example.com": [PUBLIC], "internal.example.com": [INTERNAL]},
     {"cdn.example.com": "internal.example.com"}),
    ("the name is on the list and points inside",
     "internal.example.com", {"internal.example.com": [INTERNAL]}, {}),
    ("an allowed name resolving to an IPv4-mapped address",
     "mapped.example.com", {"mapped.example.com": [MAPPED]}, {}),
]


def attempt(attack, fetch, revalidate):
    """True if the connection ended up somewhere inside."""
    _, start, answers, redirects = attack
    net = Net(answers)
    host = start
    for _ in range(4):
        if fetch(net, host) is None:
            return False
        target = redirects.get(host)
        if target is None:
            break
        if not revalidate:
            net.connect(net.resolve(target))
            break
        host = target
    return any(is_internal(a) for a in net.reached)


def main():
    print(f"  attacks                             {len(ATTACKS)}")
    print(f"  validators                          {len(VALIDATORS)}")
    print()

    print("    {:<49}".format("attack") +
          "".join("{:>7}".format(n) for n, _, _ in VALIDATORS))
    results = []
    for attack in ATTACKS:
        row = "    {:<49}".format(attack[0])
        row_results = []
        for _, fetch, revalidate in VALIDATORS:
            reached = attempt(attack, fetch, revalidate)
            row_results.append(reached)
            row += "{:>7}".format("in" if reached else "-")
        results.append(row_results)
        print(row)
    totals = [sum(1 for r in results if r[i]) for i in range(len(VALIDATORS))]
    through = [[ATTACKS[j][0] for j in range(len(ATTACKS)) if results[j][i]]
               for i in range(len(VALIDATORS))]
    print()
    print("    {:<49}".format("attacks that reach an internal address") +
          "".join("{:>7}".format(n) for n in totals))
    print()
    print("  `name` and `+addr` let {} and {} through, and {}".format(
        totals[0], totals[1],
        "not the same ones" if set(through[0]) != set(through[1])
        else "the same ones"))
    print("  the second one closes the name that points inside and opens")
    print("  the window between the check and the connect, because the")
    print("  check resolves the name and the connect resolves it again --")
    print("  two lookups, two answers, one decision made in between.")
    print("  adding a check is not the same as making it safer.")
    print()
    print("  `pin` is the row where the answer stops moving: the address")
    print("  that was checked is the address that is connected to, so the")
    print("  second lookup never happens.")
    print()
    print("  `hop` is the row where every redirect target is put through")
    print("  the same question, which is the only thing that closes a")
    print("  redirect -- a redirect is a second url, and a validator that")
    print("  runs once has validated one url.")
    print()

    print("    address              looks_private   is_internal")
    for addr in (PUBLIC, INTERNAL, MAPPED):
        print("    {:<21}{:>14}{:>13}".format(
            addr, str(looks_private(addr)), str(is_internal(addr))))
    disagree = [a for a in (PUBLIC, INTERNAL, MAPPED)
                if looks_private(a) != is_internal(a)]
    print()
    print(f"  the two address checks disagree on {len(disagree)} of the "
          f"{len((PUBLIC, INTERNAL, MAPPED))},")
    print("  and the one they disagree on is the one that gets through")
    print("  `+addr`. a private range written as a list of prefixes is a")
    print("  list of the spellings somebody thought of, and an address has")
    print("  more spellings than that.")
    print()
    print("  the fourth attack is worth reading twice, because it is also")
    print("  what a legitimate call to an internal service looks like. the")
    print("  reason the fix is an allow-list of addresses rather than a")
    print("  rule about private ranges is that the two are the same")
    print("  request, and only the deployment knows which one it is.")


main()
