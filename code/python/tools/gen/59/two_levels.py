"""Chapter 59 -- two levels, and what the second one buys.

An in-process cache in front of a shared one in front of the store. The
count is of where each read was served.
"""

KEYS = 200
CALLS = 500
L1_SIZE = 20
L2_SIZE = 200


def uniform(i):
    """A deterministic value in [0, 1)."""
    state = (i + 1) * 2654435761 % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) / 4294967296.0


def sequence():
    """A skewed access pattern, so that a small first level has something to
    hold on to."""
    return [int(KEYS * uniform(i) ** 6) for i in range(CALLS)]


def no_cache(ops, count):
    for _key in ops:
        count["store"] += 1
    return 0, 0


def one_level(ops, count):
    l1 = {}
    order = []
    for key in ops:
        if key in l1:
            count["l1"] += 1
        else:
            count["store"] += 1
            if len(l1) >= L1_SIZE:
                del l1[order.pop(0)]
            l1[key] = True
            order.append(key)
    return len(l1), 0


def two_levels(ops, count):
    l1 = {}
    order = []
    l2 = {}
    for key in ops:
        if key in l1:
            count["l1"] += 1
        elif key in l2:
            count["l2"] += 1
        else:
            count["store"] += 1
            l2[key] = True
        if key not in l1:
            if len(l1) >= L1_SIZE:
                del l1[order.pop(0)]
            l1[key] = True
            order.append(key)
    return len(l1), len(l2)


DESIGNS = [
    ("the store only", no_cache),
    ("one level", one_level),
    ("two levels", two_levels),
]


def main():
    ops = sequence()
    print(f"  keys                                {KEYS}")
    print(f"  reads                               {CALLS}")
    print(f"  first level size                    {L1_SIZE}")
    print(f"  second level size                   {L2_SIZE}")
    print()
    print("    design           served by l1   served by l2   store loads   entries")
    results = {}
    for name, design in DESIGNS:
        count = {"l1": 0, "l2": 0, "store": 0}
        held1, held2 = design(ops, count)
        results[name] = (count["l1"], count["l2"], count["store"],
                         held1 + held2)
        print("    {:<17}{:>13}{:>15}{:>14}{:>10}".format(
            name, count["l1"], count["l2"], count["store"], held1 + held2))
    print()

    one = results["one level"]
    two = results["two levels"]
    plain = results["the store only"]
    print(f"  the first level holds {L1_SIZE} of the {KEYS} keys and the pattern is skewed,")
    print(f"  so it catches {one[0]} of the {CALLS} reads and sends {one[2]} to the store.")
    print()
    print(f"  adding the second level takes the store loads from {one[2]} to {two[2]},")
    print(f"  which is {one[2] / two[2]:.1f} times fewer. The reads the first level missed are")
    print(f"  {two[1]} and the second level serves {100.0 * two[1] / (two[1] + two[2]):.1f}% of them.")
    print()
    print(f"  that is the multiplication this shape is for. The store load rate")
    print(f"  is the first level's miss rate multiplied by the second level's,")
    print(f"  and each level is cheap to size because each one is a count rather")
    print(f"  than a guess. The same arithmetic is why a third level stops")
    print(f"  helping: the second level already caught most of what the first")
    print(f"  missed, so the third has little left to catch.")
    print()
    print("  the cost is not in the table, and it is the reason to think before")
    print("  adding a level. An entry now exists in two caches and the store, so")
    print("  an invalidation has to reach all three, and the level easiest to")
    print("  forget is the one inside the process -- because it is the one that")
    print("  lives in the language rather than in a service you can call.")
    print()
    print(f"  `the store only` is in the table to size the prize. It reads the")
    print(f"  store {plain[2]} times, and the two-level design reads it {two[2]}. Everything")
    print(f"  between those two numbers is what the cache is worth, and every")
    print(f"  invalidation bug lives in the gap.")


main()
