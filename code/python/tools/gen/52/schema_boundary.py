#!/usr/bin/env python3
"""Chapter 52 demo, part 6 -- validation is a boundary, and a boundary has a shape.

"Validate your input" is the advice that replaces every other piece of advice in
this chapter, and it is not wrong. It is underspecified. A validator is a
predicate, and the useful question about a predicate is how many of the bodies
you do not want it accepts.

Twelve request bodies, three of which are legitimate. Three validators, each a
strict superset of the one above it, and the count of hostile bodies each one
lets through.
"""
REQUIRED = {"name": str, "age": int, "email": str}
MAX_LEN = {"name": 32, "email": 64}
ALLOWED = set(REQUIRED)

# label, body, is it legitimate
BODIES = [
    ("ada", {"name": "ada", "age": 36, "email": "ada@example.com"}, True),
    ("grace", {"name": "grace", "age": 45, "email": "grace@example.com"}, True),
    ("alan", {"name": "alan", "age": 41, "email": "alan@example.com"}, True),
    ("no name", {"age": 36, "email": "a@b.c"}, False),
    ("no age", {"name": "ada", "email": "a@b.c"}, False),
    ("name=5", {"name": 5, "age": 36, "email": "a@b.c"}, False),
    ("age='36'", {"name": "ada", "age": "36", "email": "a@b.c"}, False),
    ("age=True", {"name": "ada", "age": True, "email": "a@b.c"}, False),
    ("name 100 chars", {"name": "a" * 100, "age": 36, "email": "a@b.c"}, False),
    ("extra key", {"name": "ada", "age": 36, "email": "a@b.c", "role": "admin"}, False),
    ("age=-1", {"name": "ada", "age": -1, "email": "a@b.c"}, False),
    ("name=None", {"name": None, "age": 36, "email": "a@b.c"}, False),
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
    if set(body) - ALLOWED:                    # no keys you did not ask for
        return False
    if any(type(body[k]) is not t for k, t in REQUIRED.items()):
        return False                           # bool is an int; this is not
    if not all(len(body[k]) <= MAX_LEN[k] for k in MAX_LEN):
        return False
    return 0 <= body["age"] <= 150


VALIDATORS = [
    ("presence", presence),
    ("+ types", with_types),
    ("+ bounds", with_bounds),
]


def main():
    legit = sum(1 for _, _, ok in BODIES if ok)
    print(f"  bodies                             {len(BODIES):>3}")
    print(f"  legitimate                         {legit:>3}")
    print(f"  hostile                            {len(BODIES) - legit:>3}")
    print(f"  the strictest validator checks      keys, types, "
          f"{len(MAX_LEN)} length limits, 1 range")
    print()
    print(f"    {'body':<18}{'presence':>10}{'+ types':>9}{'+ bounds':>10}")

    accepted = {name: 0 for name, _ in VALIDATORS}
    hostile_accepted = {name: 0 for name, _ in VALIDATORS}
    for label, body, ok in BODIES:
        cells = []
        for name, fn in VALIDATORS:
            passed = fn(body)
            cells.append("pass" if passed else "reject")
            if passed:
                accepted[name] += 1
                if not ok:
                    hostile_accepted[name] += 1
        print(f"    {label:<18}{cells[0]:>10}{cells[1]:>9}{cells[2]:>10}")

    print()
    for name, _ in VALIDATORS:
        print(f"  {name:<12} accepts {accepted[name]:>2} of {len(BODIES)}"
              f"   ({hostile_accepted[name]} of them hostile)")

    print()
    print("  the strictest one accepts the three legitimate bodies and")
    print("  nothing else, which is what a boundary is supposed to do. the")
    print("  interesting column is the middle one.")
    print()
    print("  presence alone accepts seven hostile bodies, and the reason is")
    print("  not carelessness -- a body with every key present and the wrong")
    print("  type in each is a well-formed body. checking the types removes")
    print("  four of the seven and leaves one that no amount of isinstance")
    print("  will catch, because in Python `True` is an `int`.")
    print()
    print("  that is the shape of the problem. each validator is a strict")
    print("  superset of the last, and each one closes some of the gap. what")
    print("  none of them does is tell you how much gap is left, which is")
    print("  why the number is worth writing down next to the validator.")


if __name__ == "__main__":
    main()
