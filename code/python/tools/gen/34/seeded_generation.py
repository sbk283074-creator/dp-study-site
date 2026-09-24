"""Chapter 34 -- a seed is a promise that the same world comes back.

A small generator of the kind a game can reimplement in any language, run with
three seeds. The count is of tiles that differ between runs, and of the separate
landmasses a generated map contains.
"""

WORLD = 32
WATER_LEVEL = 0.42

# A 32-bit linear congruential generator. The constants are the ones from
# Numerical Recipes; what matters is that the sequence is defined by the
# arithmetic rather than by the interpreter.
MULTIPLIER = 1664525
INCREMENT = 1013904223
MODULUS = 2 ** 32


class Rand:
    def __init__(self, seed):
        self.state = seed & (MODULUS - 1)

    def next_float(self):
        self.state = (self.state * MULTIPLIER + INCREMENT) % MODULUS
        return self.state / MODULUS


def generate(seed):
    rng = Rand(seed)
    return [[rng.next_float() < WATER_LEVEL for _ in range(WORLD)]
            for _ in range(WORLD)]


def landmasses(world):
    """Count the connected regions of land, four-way."""
    seen = set()
    regions = 0
    for y in range(WORLD):
        for x in range(WORLD):
            if world[y][x] or (x, y) in seen:
                continue
            regions += 1
            stack = [(x, y)]
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if not (0 <= nx < WORLD and 0 <= ny < WORLD):
                        continue
                    if world[ny][nx] or (nx, ny) in seen:
                        continue
                    seen.add((nx, ny))
                    stack.append((nx, ny))
    return regions


first = generate(1)
again = generate(1)
other = generate(2)
third = generate(3)

differ_same = sum(1 for y in range(WORLD) for x in range(WORLD)
                  if first[y][x] != again[y][x])
differ_other = sum(1 for y in range(WORLD) for x in range(WORLD)
                   if first[y][x] != other[y][x])

rows = [
    ("seed 1", first),
    ("seed 1 again", again),
    ("seed 2", other),
    ("seed 3", third),
]

print(f"a {WORLD} by {WORLD} world, water below {WATER_LEVEL}")
print()
print(f"{'run':<16}{'land tiles':>12}{'water tiles':>13}{'landmasses':>12}")
print("-" * 53)
for label, world in rows:
    land = sum(1 for row in world for tile in row if not tile)
    print(f"{label:<16}{land:>12}{WORLD * WORLD - land:>13}"
          f"{landmasses(world):>12}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'tiles in the world':<46}{WORLD * WORLD:>8}")
print(f"{'runs':<46}{len(rows):>8}")
print(f"{'tiles differing between seed 1 and seed 1':<46}{differ_same:>8}")
print(f"{'tiles differing between seed 1 and seed 2':<46}{differ_other:>8}")
print(f"{'distinct seeds':<46}{len({1, 2, 3}):>8}")
print(f"{'landmasses in seed 1':<46}{landmasses(first):>8}")
print(f"{'landmasses in seed 2':<46}{landmasses(other):>8}")

print()
print("The first two rows are identical tile for tile, which is the whole")
print("contract: a seed is not a hint, it is the entire world. Two players who")
print("share a seed share a map, and a bug report of the form 'seed 4815162342,")
print("third room, the door is in the wall' is reproducible by anyone.")
print()
print("The bottom rows are the part a screenshot cannot tell you. All four runs")
print("produce a map that is roughly 58% land and they are not the same map at")
print(f"all -- seed 1 differs from seed 2 on {differ_other} of the {WORLD * WORLD} tiles. What the land")
print(f"count cannot see is that seed 1 is broken into {landmasses(first)} separate")
print(f"landmasses and seed 2 into {landmasses(other)}, so a player spawning in the wrong one")
print("can walk to a fraction of the world and no further. Counting the")
print("landmasses is how a generator gets tested -- not 'does it look right' but")
print("'does every seed produce a map the player can cross'.")
print()
print("That is why the generator has to be yours. `random` is reproducible on")
print("one interpreter version and is not a specification; a dozen lines of")
print("arithmetic is. When the map is part of the save file, the generator is")
print("part of the save format, and a save format that depends on the standard")
print("library's implementation is a save format that can break in a patch")
print("release.")
