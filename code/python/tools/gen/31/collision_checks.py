"""Chapter 31 -- collision detection is a count of pairs, and the grid changes it.

Two hundred sprites on a field, with the collisions found three ways: every pair,
the same cell only, and the full neighbourhood. The count is of pairs examined and
of collisions found. The field is deliberately crowded enough that the same-cell
grid misses some, so the row that is wrong can be seen to be wrong.
"""

SPRITES = 200
RADIUS = 8
FIELD = 100
CELL = 2 * RADIUS


def spots():
    return [((index * 37) % FIELD, (index * 71) % FIELD)
            for index in range(SPRITES)]


def close(first, second):
    return (first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2 <= RADIUS ** 2


def every_pair(points):
    pairs = 0
    hits = set()
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            pairs += 1
            if close(points[i], points[j]):
                hits.add((i, j))
    return pairs, hits


def grid(points, neighbourhood):
    cells = {}
    for index, point in enumerate(points):
        cells.setdefault((point[0] // CELL, point[1] // CELL), []).append(index)
    offsets = [(0, 0)]
    if neighbourhood:
        offsets = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    pairs = 0
    hits = set()
    seen = set()
    for key in sorted(cells):
        members = cells[key]
        neighbours = []
        for dx, dy in offsets:
            neighbours.extend(cells.get((key[0] + dx, key[1] + dy), []))
        for i in members:
            for j in neighbours:
                if i >= j:
                    continue
                if (i, j) in seen:
                    continue
                seen.add((i, j))
                pairs += 1
                if close(points[i], points[j]):
                    hits.add((i, j))
    return pairs, hits


points = spots()
brute_pairs, brute_hits = every_pair(points)
own_pairs, own_hits = grid(points, False)
full_pairs, full_hits = grid(points, True)

rows = [
    ("every pair", brute_pairs, len(brute_hits)),
    ("grid, own cell only", own_pairs, len(own_hits)),
    ("grid, full neighbourhood", full_pairs, len(full_hits)),
]

print(f"{SPRITES} sprites on a {FIELD} by {FIELD} field, radius {RADIUS}, "
      f"cell {CELL}")
print()
print(f"{'method':<28}{'pairs examined':>16}{'collisions found':>18}"
      f"{'missed':>9}")
print("-" * 71)
for label, pairs, found in rows:
    print(f"{label:<28}{pairs:>16}{found:>18}"
          f"{len(brute_hits) - found:>9}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'sprites':<46}{SPRITES:>8}")
print(f"{'pairs if every pair is checked':<46}"
      f"{SPRITES * (SPRITES - 1) // 2:>8}")
print(f"{'pairs the full neighbourhood examines':<46}{full_pairs:>8}")
print(f"{'pairs that the grid avoided':<46}"
      f"{brute_pairs - full_pairs:>8}")
print(f"{'collisions to find':<46}{len(brute_hits):>8}")
print(f"{'collisions the own-cell grid missed':<46}"
      f"{len(brute_hits) - len(own_hits):>8}")

print()
print(f"Two of the three rows agree and the middle one does not. Every pair is")
print(f"{brute_pairs:,} distance checks, and the full neighbourhood finds the same")
print(f"{len(brute_hits)} collisions in {full_pairs:,} of them. That is the part that has to be")
print(f"checked rather than assumed: a broad phase is only a speed-up if it is")
print(f"a speed-up that cannot miss.")
print()
print("The middle row is the mistake that looks like a fix, and this layout is")
print("crowded enough to show it. A grid that compares sprites inside the same")
print(f"cell only examines the fewest pairs of all -- {own_pairs} -- and misses")
print(f"{len(brute_hits) - len(own_hits)} of the {len(brute_hits)} collisions. Two sprites eight pixels apart, which")
print("is exactly touching at this radius, can sit on either side of a cell")
print("edge, and the cell that holds one never looks at the other.")
print()
print("So the rule is the one the counting gives. A broad phase must be tested")
print("against the brute-force answer on a real layout before it is trusted,")
print("and the test is the one above: the same collisions, in fewer pairs.")
print("Everything else about it -- the cell size, the neighbourhood, the data")
print("structure -- is an optimisation, and an optimisation that changes the")
print("answer is a bug with a benchmark attached.")
