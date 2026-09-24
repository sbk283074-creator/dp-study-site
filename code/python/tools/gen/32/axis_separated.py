"""Chapter 32 -- resolving movement one axis at a time is what lets a player slide.

A player walking diagonally into a wall, resolved two ways. The count is of steps
that moved at all, and of the diagonal gaps each method lets the player through.
"""

WIDTH = 12
HEIGHT = 12

# A vertical wall in column 8, from row 0 to row 9. Rows 10 and 11 are the gap
# under it.
WALLS = {(8, y) for y in range(10)}

START = (5, 5)
STEP = (1, 1)
STEPS = 6


def blocked(x, y):
    return not (0 <= x < WIDTH and 0 <= y < HEIGHT) or (x, y) in WALLS


def combined(start, step, steps):
    """Move both axes at once; refuse the whole step if either is blocked."""
    x, y = start
    moved = 0
    refused = 0
    for _ in range(steps):
        nx, ny = x + step[0], y + step[1]
        if blocked(nx, ny):
            refused += 1
            continue
        x, y = nx, ny
        moved += 1
    return (x, y), moved, refused


def separated(start, step, steps):
    """Move each axis on its own; keep whichever one is free."""
    x, y = start
    moved = 0
    x_blocked = 0
    y_blocked = 0
    for _ in range(steps):
        if blocked(x + step[0], y):
            x_blocked += 1
        else:
            x += step[0]
        if blocked(x, y + step[1]):
            y_blocked += 1
        else:
            y += step[1]
        moved += 1
    return (x, y), moved, x_blocked, y_blocked


end_c, moved_c, refused_c = combined(START, STEP, STEPS)
end_s, moved_s, xb_s, yb_s = separated(START, STEP, STEPS)

rows = [
    ("both axes at once", moved_c, f"{end_c}", refused_c),
    ("one axis at a time", moved_s, f"{end_s}", 0),
]

print(f"player at {START} stepping {STEP}, {STEPS} steps, wall in column 8")
print()
print(f"{'resolution':<22}{'steps moved':>12}{'ends at':>12}{'steps refused':>15}")
print("-" * 61)
for label, moved, end, refused in rows:
    print(f"{label:<22}{moved:>12}{end:>12}{refused:>15}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'steps attempted':<46}{STEPS:>8}")
print(f"{'steps moved, both axes at once':<46}{moved_c:>8}")
print(f"{'steps moved, one axis at a time':<46}{moved_s:>8}")
print(f"{'steps refused, both axes at once':<46}{refused_c:>8}")
print(f"{'steps with the x axis blocked':<46}{xb_s:>8}")
print(f"{'steps with the y axis blocked':<46}{yb_s:>8}")
print(f"{'distance travelled, both axes':<46}"
      f"{abs(end_c[0] - START[0]) + abs(end_c[1] - START[1]):>8}")
print(f"{'distance travelled, one axis':<46}"
      f"{abs(end_s[0] - START[0]) + abs(end_s[1] - START[1]):>8}")

print()
print("The two rows are the same input and they are not the same game. Moving")
print("both axes at once refuses the whole step whenever either one is blocked,")
print(f"so {refused_c} of the {STEPS} steps are thrown away and the player ends at")
print(f"{end_c} -- pressed into the wall with the free axis unused. Moving one axis")
print("at a time refuses only the blocked axis, so the player keeps the free one")
print(f"and ends at {end_s}, which is {abs(end_s[1] - START[1])} tiles further down the wall.")
print()
print("That is the entire reason platformers resolve axes separately, and it is")
print("worth seeing as a decision rather than a detail. Sliding is not a feature")
print("that was added; it is what happens when the blocked axis is discarded")
print("instead of the whole step.")
print()
print("The price is the row that is not in the table: a player moving diagonally")
print("can pass through a corner where two walls meet, because neither axis is")
print("blocked on its own. Every engine that resolves per axis has to decide")
print("what to do about that, and the honest options are to test the destination")
print("square as well, or to accept corner-cutting as a movement technique. Both")
print("are defensible. Not noticing it is not.")
