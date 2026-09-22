#!/usr/bin/env python3
"""Exercise 3 -- ten order lines and three validators.

A different schema from part 6, with a numeric range and two length limits, so
the strictest validator has more to check and the middle one still has the same
hole in it.
"""
REQUIRED = {"sku": str, "qty": int, "note": str}
MAX_LEN = {"sku": 16, "note": 64}
ALLOWED = set(REQUIRED)

# label, body, is it legitimate
BODIES = [
    ("ok-1", {"sku": "A-100", "qty": 3, "note": "urgent"}, True),
    ("ok-2", {"sku": "B-200", "qty": 1, "note": ""}, True),
    ("ok-3", {"sku": "C-300", "qty": 999, "note": "gift"}, True),
    ("no sku", {"qty": 3, "note": "urgent"}, False),
    ("qty='3'", {"sku": "A-100", "qty": "3", "note": "urgent"}, False),
    ("qty=True", {"sku": "A-100", "qty": True, "note": "urgent"}, False),
    ("qty=0", {"sku": "A-100", "qty": 0, "note": "urgent"}, False),
    ("qty=1000", {"sku": "A-100", "qty": 1000, "note": "urgent"}, False),
    ("sku 20 chars", {"sku": "S" * 20, "qty": 3, "note": "urgent"}, False),
    ("extra key", {"sku": "A-100", "qty": 3, "note": "urgent", "price": 1}, False),
]


def presence(body):
    return all(k in body for k in REQUIRED)


def with_types(body):
    if not presence(body):
        return False
    return all(isinstance(body[k], t) for k, t in REQUIRED.items())


def with_bounds(body):
    if not with_types(body):
        return False
    if set(body) - ALLOWED:
        return False
    if any(type(body[k]) is not t for k, t in REQUIRED.items()):
        return False
    if not all(len(body[k]) <= MAX_LEN[k] for k in MAX_LEN):
        return False
    return 1 <= body["qty"] <= 999


VALIDATORS = [
    ("presence", presence),
    ("+ types", with_types),
    ("+ bounds", with_bounds),
]


def main():
    legit = sum(1 for _l, _b, ok in BODIES if ok)
    print(f"  bodies                             {len(BODIES):>3}")
    print(f"  legitimate                         {legit:>3}")
    print(f"  hostile                            {len(BODIES) - legit:>3}")
    print()
    print(f"    {'body':<14}{'presence':>10}{'+ types':>9}{'+ bounds':>10}")

    accepted = {n: 0 for n, _ in VALIDATORS}
    hostile = {n: 0 for n, _ in VALIDATORS}
    for label, body, ok in BODIES:
        cells = []
        for name, fn in VALIDATORS:
            passed = fn(body)
            cells.append("pass" if passed else "reject")
            if passed:
                accepted[name] += 1
                if not ok:
                    hostile[name] += 1
        print(f"    {label:<14}{cells[0]:>10}{cells[1]:>9}{cells[2]:>10}")

    print()
    for name, _ in VALIDATORS:
        print(f"  {name:<12} accepts {accepted[name]:>2} of {len(BODIES)}"
              f"   ({hostile[name]} of them hostile)")

    print()
    print(f"  `True` is an int, per isinstance      {isinstance(True, int)}")
    print(f"  `True` is inside the numeric range    {1 <= True <= 999}")
    print()
    print("  the range check is the interesting addition, because `qty=0`")
    print("  and `qty=1000` are both the right type. a type check cannot see")
    print("  them, and neither can a length limit, because an integer does")
    print("  not have one.")
    print()
    print("  `qty=True` is the one to remember. it passes the type check")
    print("  because `True` is an `int`, and the range check would have")
    print("  passed it too, because `True` is `1` and one is inside the")
    print("  range. only the exact-type comparison catches it, which is why")
    print("  the strictest validator uses `type(x) is t` rather than")
    print("  `isinstance`.")


if __name__ == "__main__":
    main()
