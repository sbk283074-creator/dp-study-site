"""Chapter 34 -- drawing the whole world is a count you can do in advance.

A tiled world and a viewport. The count is of tiles drawn with and without
culling, and of tiles a boundary mistake leaves off the edge of the screen.
"""

WORLD = 64
VIEW_W = 20
VIEW_H = 15
TILE = 16


def tiles_drawn(camera_x, camera_y, inclusive):
    """The tile range covering the viewport, in whole tiles.

    `inclusive` adds the partial tile at the right and bottom edges, which is
    what the camera actually shows when it is not tile-aligned.
    """
    first_x = camera_x // TILE
    first_y = camera_y // TILE
    last_x = first_x + VIEW_W + (1 if inclusive else 0)
    last_y = first_y + VIEW_H + (1 if inclusive else 0)
    return max(0, min(last_x, WORLD) - first_x) * max(0, min(last_y, WORLD) - first_y)


WHOLE_WORLD = WORLD * WORLD
aligned = tiles_drawn(0, 0, True)
offset = tiles_drawn(TILE // 2, TILE // 2, True)
offset_short = tiles_drawn(TILE // 2, TILE // 2, False)
missing = offset - offset_short

print(f"a {WORLD} by {WORLD} world, a {VIEW_W} by {VIEW_H} tile viewport")
print()
print(f"{'what is drawn':<38}{'tiles':>8}{'of the world':>15}")
print("-" * 61)
print(f"{'the whole world':<38}{WHOLE_WORLD:>8}"
      f"{100.0 * WHOLE_WORLD / WHOLE_WORLD:>14.1f}%")
print(f"{'the viewport, camera aligned':<38}{aligned:>8}"
      f"{100.0 * aligned / WHOLE_WORLD:>14.1f}%")
print(f"{'the viewport, camera half a tile off':<38}{offset:>8}"
      f"{100.0 * offset / WHOLE_WORLD:>14.1f}%")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'tiles in the world':<46}{WHOLE_WORLD:>8}")
print(f"{'tiles in one viewport':<46}{VIEW_W * VIEW_H:>8}")
print(f"{'tiles drawn, with the edge tiles':<46}{offset:>8}")
print(f"{'tiles drawn, without the edge tiles':<46}{offset_short:>8}")
print(f"{'tiles the view shows but does not draw':<46}{missing:>8}")
print(f"{'tiles the extra column and row cost':<46}"
      f"{VIEW_H + VIEW_W + 1:>8}")
print(f"{'share of the world drawn':<46}"
      f"{round(100.0 * offset / WHOLE_WORLD):>7}%")

print()
print("Culling is not an optimisation you add later, it is the difference")
print(f"between a frame that costs {WHOLE_WORLD:,} tile draws and one that costs {offset}.")
print("The world grows with the game and the viewport does not, so the number")
print("to keep in the frame is the small one -- and it is small because the")
print("camera tells you where to stop, not because anything was measured.")
print()
print("The row that matters is the one counting the tiles the view shows but")
print("does not draw, and it is the kind of mistake that only shows up as a")
print("visual bug. Computing the range as the viewport's width in whole tiles")
print("leaves the partial tile at the right and bottom edges undrawn, so there is")
print("a strip of background along two sides of the screen whenever the camera is")
print(f"not exactly tile-aligned. One extra tile in each direction fixes it: {missing}")
print(f"tiles out of {offset}, which is an extra column of {VIEW_H + 1} and an extra")
print(f"row of {VIEW_W}.")
print()
print("That is the general shape of an off-by-one in a loop bound. The mistake")
print("is free, the symptom is cosmetic, and the fix is to include the boundary")
print(f"rather than to exclude it. The count is what makes it visible -- {offset_short}")
print(f"against {offset} is a strip of missing floor, not a rounding detail.")
