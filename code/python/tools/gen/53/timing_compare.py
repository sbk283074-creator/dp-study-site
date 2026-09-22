#!/usr/bin/env python3
"""Chapter 53 demo, part 6 -- a timing attack, counted instead of timed.

A comparison that stops at the first difference tells the caller how much of
their guess was right. Measuring that in seconds needs a quiet machine and a lot
of samples, and the number you get is a measurement rather than a fact.

So this block does not time anything. It counts the bytes each comparison
examines, which is the quantity the time is a proxy for, and it is exact. The
attack is then run against both comparisons and the result is a count too: how
many bytes of the secret can be recovered, and at what cost in probes.
"""
SECRET = b"correct-horse-battery-staple"


def compare_early(a, b):
    """Stop at the first difference. Returns (equal, bytes examined)."""
    if len(a) != len(b):
        return False, 0
    examined = 0
    for x, y in zip(a, b):
        examined += 1
        if x != y:
            return False, examined
    return True, examined


def compare_constant(a, b):
    """Examine every byte regardless. Returns (equal, bytes examined)."""
    examined = 0
    difference = len(a) ^ len(b)
    for x, y in zip(a, b):
        examined += 1
        difference |= x ^ y
    return difference == 0, examined


def recover(compare, secret):
    """Guess byte by byte, taking the candidate that examined the most."""
    known = bytearray()
    probes = 0
    counts = set()
    for position in range(len(secret)):
        best, best_count = 0, -1
        for guess in range(256):
            candidate = (bytes(known) + bytes([guess])
                         + b"\x00" * (len(secret) - position - 1))
            _equal, examined = compare(candidate, secret)
            probes += 1
            counts.add(examined)
            if examined > best_count:
                best, best_count = guess, examined
        known.append(best)
    return bytes(known), probes, counts


def main():
    print(f"  secret length                      {len(SECRET):>3} bytes")
    print(f"  candidates per position            {256:>3}")
    print(f"  total probes per attack            "
          f"{len(SECRET) * 256:>3}")
    print()
    print(f"    {'comparison':<20}{'probes':>9}{'distinct':>10}"
          f"{'bytes recovered':>17}")

    for name, fn in (("stops at first diff", compare_early),
                     ("examines every byte", compare_constant)):
        found, probes, counts = recover(fn, SECRET)
        matched = sum(1 for i, b in enumerate(found) if b == SECRET[i])
        print(f"    {name:<20}{probes:>9}{len(counts):>10}{matched:>17}")

    print()
    print("  what the leak looks like, position by position")
    known = bytearray()
    for position in (0, 1, 2):
        row = []
        for guess in range(256):
            candidate = (bytes(known) + bytes([guess])
                         + b"\x00" * (len(SECRET) - position - 1))
            _e, examined = compare_early(candidate, SECRET)
            row.append(examined)
        correct = SECRET[position]
        print(f"    position {position}: examined counts "
              f"{sorted(set(row))}, and the byte that examined the most is "
              f"{max(range(256), key=lambda g: row[g])} "
              f"({'correct' if max(range(256), key=lambda g: row[g]) == correct else 'wrong'})")
        known.append(correct)

    print()
    found, _probes, _counts = recover(compare_early, SECRET)
    missed = [i for i, b in enumerate(found) if b != SECRET[i]]
    print("  the positions the early-exit comparison could not recover")
    for i in missed:
        counts = set()
        for guess in range(256):
            candidate = (bytes(SECRET[:i]) + bytes([guess])
                         + b"\x00" * (len(SECRET) - i - 1))
            counts.add(compare_early(candidate, SECRET)[1])
        print(f"    position {i} of {len(SECRET)}: every one of the 256 guesses "
              f"examined {sorted(counts)} bytes")

    print()
    print("  both comparisons were probed the same number of times. the")
    print("  difference is not the cost of the attack, it is what a probe")
    print("  tells you: the early-exit comparison produces a number that")
    print("  varies with the position, and the constant one produces the same")
    print("  number for all of them.")
    print()
    print("  the early-exit comparison recovered all but one byte, and the")
    print("  byte it missed is the last one -- because there is no byte after")
    print("  it to differ at. a wrong guess at the final position examines")
    print("  the same number of bytes as a right one, so nothing ranks them.")
    print("  that is a property of the method rather than of the comparison:")
    print("  append a byte to the guess and the last position becomes")
    print("  recoverable like the others.")
    print()
    print("  the second count is the one that matters. the constant")
    print("  comparison recovered zero bytes -- not because it is hard to")
    print("  break, but because every wrong guess looks exactly like every")
    print("  other wrong guess, so there is nothing to rank them by.")
    print()
    print("  `hmac.compare_digest` is the standard library's version of the")
    print("  second function, written in C so that no interpreter detail can")
    print("  reintroduce the early exit. reach for it rather than writing one.")


if __name__ == "__main__":
    main()
