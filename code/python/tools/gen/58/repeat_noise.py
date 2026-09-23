"""Chapter 58 -- how many runs a measurement needs.

Five candidates whose true costs differ by twenty units, measured with a
deterministic wobble that is three times larger. The count is of how many
of the five positions a single run gets right.
"""

# A fixed sequence, so this program prints the same bytes on every run.
# Real noise is not this polite; the only property being modelled is that
# it is larger than the gaps between the candidates. The nine values are
# symmetric about zero, which is what lets a median of nine runs land on
# the true value.
WOBBLE = [-60, 45, -30, 60, -45, 30, 15, -15, 0]
AMPLITUDE = 60

CANDIDATES = [
    ("format a row", 100),
    ("copy a dict", 120),
    ("strip a field", 140),
    ("look up a key", 160),
    ("compare a date", 180),
]

RUNS = len(WOBBLE)
NAMES = [name for name, _ in CANDIDATES]
EXACT = {name: cost for name, cost in CANDIDATES}


def wobble(seed, index):
    return WOBBLE[(seed + index) % len(WOBBLE)]


def estimate(seed):
    return {name: cost + wobble(seed, index)
            for index, (name, cost) in enumerate(CANDIDATES)}


def rank_of(values):
    return [name for name, _ in sorted(values.items(), key=lambda kv: kv[1])]


def true_rank():
    return [name for name, _ in sorted(CANDIDATES, key=lambda c: c[1])]


def positions_right(ranking, truth):
    return sum(1 for a, b in zip(ranking, truth) if a == b)


def median(values):
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def main():
    gap = CANDIDATES[1][1] - CANDIDATES[0][1]
    truth = true_rank()
    print(f"  candidates                          {len(CANDIDATES)}")
    print(f"  runs                                {RUNS}")
    print(f"  gap between neighbours              {gap}")
    print(f"  wobble, either way                  {AMPLITUDE}")
    print()
    print("    run 1, the five estimates")
    first = estimate(1)
    for name in NAMES:
        print("    {:<18}{:>7}".format(name, first[name]))
    print()
    print("    run 1 ranks them as")
    first_rank = rank_of(first)
    for index, name in enumerate(first_rank, 1):
        print("    {:<3}{:<18}{:>6}".format(index, name, first[name]))
    print()
    print("    how many of the five positions each run gets right")
    per_run = []
    for seed in range(1, RUNS + 1):
        right = positions_right(rank_of(estimate(seed)), truth)
        per_run.append(right)
        print("    run {:<3}{:>6} of {}".format(seed, right, len(NAMES)))
    print()

    pooled = {name: median([estimate(seed)[name] for seed in range(1, RUNS + 1)])
              for name in NAMES}
    pooled_rank = rank_of(pooled)
    print("    the median of the nine runs, ranked")
    for index, name in enumerate(pooled_rank, 1):
        print("    {:<3}{:<18}{:>6}".format(index, name, pooled[name]))
    print()

    total = sum(per_run)
    print(f"  a single run gets {per_run[0]} of the {len(NAMES)} positions right, and the")
    print(f"  nine runs average {total / RUNS:.2f}. The gaps between neighbours are")
    print(f"  {gap} units and the wobble is {AMPLITUDE}, so a single run is ranking the")
    print("  wobble rather than the candidates.")
    print()
    print(f"  the median of the nine gets {positions_right(pooled_rank, truth)} of {len(NAMES)}, because the")
    print("  wobble is symmetric about zero and a median of an odd number of")
    print("  runs removes a symmetric error. That is the whole argument for")
    print("  repeating a measurement and taking the middle one rather than")
    print("  the best one.")
    print()
    print(f"  counting the work instead gets {positions_right(rank_of(EXACT), truth)} of {len(NAMES)} on the first")
    print("  run and needs no repetition at all, because a count of operations")
    print("  is an integer the code produces rather than a duration a machine")
    print("  produces. That is the trade: a count is the more useful unit and")
    print("  it measures a different thing than elapsed time does.")
    print()
    print(f"  when there is no count to make, the number that decides how many")
    print(f"  runs are enough is the gap you are trying to resolve. Here {gap} units")
    print(f"  needs the wobble down to well under {gap}, which one run cannot do and")
    print("  nine runs can.")


main()
