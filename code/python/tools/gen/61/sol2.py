"""Chapter 61 -- solution 2. The largest value per group, counted three ways.

The same shape as the counting group-by, with a different aggregate, because
the aggregate is not what decides. The count is of comparisons, and the
per-group design is a product again -- but the one-pass design has to keep a
maximum rather than a sum, which changes nothing about the count and adds one
thing to get right.
"""

import array

ROWS = 20000
GROUPS = 50


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


KEYS = array.array("q", (mix(11 + index) % GROUPS for index in range(ROWS)))
VALUES = array.array("q", (mix(29 + index) % 100000 for index in range(ROWS)))


def per_group(keys, values):
    """For each group, walk every row and keep the largest value."""
    comparisons = 0
    best = {}
    for group in range(GROUPS):
        top = None
        for position in range(len(keys)):
            comparisons += 1
            if keys[position] == group:
                value = values[position]
                if top is None or value > top:
                    top = value
        if top is not None:
            best[group] = top
    return best, comparisons


def one_pass(keys, values):
    """One walk, one lookup per row, one comparison against the current best."""
    comparisons = 0
    best = {}
    for position in range(len(keys)):
        comparisons += 1
        key = keys[position]
        value = values[position]
        if key not in best or value > best[key]:
            best[key] = value
    return best, comparisons


def sort_then_walk(keys, values):
    """Put the rows in key order, then take the maximum of each run."""
    comparisons = [0]

    def merge_sort(order):
        if len(order) <= 1:
            return list(order)
        middle = len(order) // 2
        left = merge_sort(order[:middle])
        right = merge_sort(order[middle:])
        out = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if keys[left[i]] <= keys[right[j]]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    order = merge_sort(range(len(keys)))
    best = {}
    previous = None
    top = None
    for position in order:
        comparisons[0] += 1
        key = keys[position]
        if key != previous and previous is not None:
            best[previous] = top
            top = None
        value = values[position]
        if top is None or value > top:
            top = value
        previous = key
    best[previous] = top
    return best, comparisons[0]


DESIGNS = [
    ("a walk per group", per_group),
    ("one walk, a dictionary", one_pass),
    ("sort, then walk", sort_then_walk),
]

print(f"{ROWS:,} rows, {GROUPS} groups, the largest value in each group")
print()
print(f"{'design':<24}{'comparisons':>13}{'per row':>10}")
print("-" * 47)
answers = []
for name, design in DESIGNS:
    best, comparisons = design(KEYS, VALUES)
    answers.append(best)
    print(f"{name:<24}{comparisons:>13,}{comparisons / ROWS:>10.1f}")

if not answers[0] == answers[1] == answers[2]:
    raise SystemExit("the three designs disagreed about the answer")

print()
print(f"All three agree on the {len(answers[0])} group maxima, and the first design")
print(f"examined {GROUPS} times as many items as the second, because it walks the")
print("table once for each group.")
print()
print("The aggregate changed and the ranking did not, which is the point: what")
print("decides the count is how many times the table is walked, and a maximum")
print("is no harder to keep in one pass than a sum.")
print()
print("What the one-pass version does add is a case to get right. A key that")
print("has never been seen is not the same as a key whose largest value so far")
print("is zero, so the test has to be `key not in best or value > best[key]`")
print("rather than a comparison against a starting value of zero. That is a")
print("correctness difference between the two designs, and it does not show up")
print("in the count at all.")
