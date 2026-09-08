---
chapter: 34
part: 5
title: Worlds: Tilemaps, Cameras & Procedural Generation
summary: Build tile-based worlds from text files, draw only what is visible, drive a clamped scrolling camera with parallax, and generate reproducible levels with seeded procedural algorithms.
minutes: 50
tags: [tilemaps, culling, camera, parallax, procgen, flood fill, seeds]
---

A level hardcoded as a list of rects is fine for ten platforms and useless for a hundred screens
of cave. Real 2D worlds are **grids**: one character per cell, one integer per cell, one lookup
away from "what is at this position". Grids are easy to author, easy to save, easy to collide
against, and — the part that matters later — easy to generate. This chapter covers the whole
pipeline: authoring a level as text, drawing only the visible slice of it, moving a camera
through a world bigger than the window, and then throwing the hand-made levels away and
generating them from a seed instead.

## The world as a grid

A tilemap is a list of lists. Each cell holds a tile id — usually a single character, because
that makes levels editable in a text editor.

```text
####################
#..................#
#....P.............#
#..........###.....#
#..................#
#.....####.........#
#..................#
#..............##..#
#...^^.............#
####################
```

```python
# tilemap.py
from pathlib import Path
import pygame

TILE = 32

TILES: dict[str, dict] = {
    "#": {"solid": True,  "hazard": False, "color": (72, 78, 100)},
    ".": {"solid": False, "hazard": False, "color": (28, 32, 44)},
    "^": {"solid": True,  "hazard": True,  "color": (214, 92, 92)},
    "P": {"solid": False, "hazard": False, "spawn": "player", "color": (28, 32, 44)},
}


def load_level(path: str | Path) -> list[list[str]]:
    """Read a level file into a grid. Blank lines are skipped."""
    text = Path(path).read_text()
    return [list(line) for line in text.splitlines() if line.strip()]


def world_size(grid: list[list[str]]) -> tuple[int, int]:
    return len(grid[0]) * TILE, len(grid) * TILE


def find_spawns(grid: list[list[str]], kind: str) -> list[tuple[int, int]]:
    """Centre points (in world pixels) of every tile flagged as a spawn of this kind."""
    return [
        (col * TILE + TILE // 2, row * TILE + TILE // 2)
        for row, line in enumerate(grid)
        for col, ch in enumerate(line)
        if TILES[ch].get("spawn") == kind
    ]
```

Conversions you will type constantly:

```python
world_x = col * TILE          # tile -> world
col     = world_x // TILE     # world -> tile
screen_x = world_x - camera_x # world -> screen
```

:::tip Author levels as text
A `.txt` level costs nothing to edit, diffs cleanly in Git (Chapter 22), and lets you sketch a
room in ten seconds without opening an editor plugin. Professional tools like Tiled exist for a
reason, and they all export to grids — but start with text.
:::

## Culling: draw only what you can see

The naive draw loop walks the whole grid. A 200×200 level is 40,000 blits per frame; a 640×480
window shows about 20×15 = 300 tiles. You are doing 130× the necessary work.

```python
def draw_tiles_naive(screen, grid, camera) -> None:
    for row, line in enumerate(grid):
        for col, ch in enumerate(line):
            screen.blit(TILE_IMAGES[ch],
                        (col * TILE - round(camera.pos.x), row * TILE - round(camera.pos.y)))


def draw_tiles_culled(screen, grid, camera) -> None:
    """Only touch the tiles that intersect the view. Same picture, ~1% of the work."""
    cam_x, cam_y = int(camera.pos.x), int(camera.pos.y)
    first_col = max(0, cam_x // TILE)
    last_col = min(len(grid[0]) - 1, (cam_x + screen.get_width()) // TILE + 1)
    first_row = max(0, cam_y // TILE)
    last_row = min(len(grid) - 1, (cam_y + screen.get_height()) // TILE + 1)

    for row in range(first_row, last_row + 1):
        line = grid[row]
        for col in range(first_col, last_col + 1):
            screen.blit(TILE_IMAGES[line[col]],
                        (col * TILE - cam_x, row * TILE - cam_y))
```

Measure instead of assuming:

```python
import time


def bench(screen, grid, camera, frames: int = 200) -> None:
    for label, culled in (("naive", False), ("culled", True)):
        start = time.perf_counter()
        for _ in range(frames):
            (draw_tiles_culled if culled else draw_tiles_naive)(screen, grid, camera)
            pygame.display.flip()
        elapsed = (time.perf_counter() - start) / frames * 1000
        print(f"{label:7s} {elapsed:6.2f} ms/frame")
```

```text
naive    18.42 ms/frame
culled    0.61 ms/frame
```

18 ms is 54 fps spent on tiles alone, before a single enemy moves. Culling is the single highest
value optimisation in a tile engine, and it is four lines of arithmetic. The `+ 1` in the bounds
is not optional: without it, tiles on the right and bottom edges pop in and out as the camera
crosses a tile boundary.

## The camera, with bounds

```python
class Camera:
    def __init__(self, view_w: int, view_h: int, world_w: int, world_h: int) -> None:
        self.view = pygame.Rect(0, 0, view_w, view_h)
        self.world_w, self.world_h = world_w, world_h
        self.pos = pygame.Vector2(0, 0)          # top-left of the view, in world pixels

    def follow(self, target, dt: float, smooth: float = 6.0) -> None:
        desired = pygame.Vector2(target.centerx - self.view.width / 2,
                                 target.centery - self.view.height / 2)
        self.pos += (desired - self.pos) * min(1.0, smooth * dt)
        self.clamp()

    def snap_to(self, target) -> None:
        self.pos.update(target.centerx - self.view.width / 2,
                        target.centery - self.view.height / 2)
        self.clamp()

    def clamp(self) -> None:
        max_x = max(0, self.world_w - self.view.width)
        max_y = max(0, self.world_h - self.view.height)
        self.pos.x = max(0.0, min(self.pos.x, max_x))
        self.pos.y = max(0.0, min(self.pos.y, max_y))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """World rect -> screen rect (a copy; safe for tiles and entities)."""
        return rect.move(-round(self.pos.x), -round(self.pos.y))

    def apply_rect(self, entity) -> pygame.Rect:
        """Same transform for an object that owns a .rect."""
        return self.apply(entity.rect)
```

Two rules: build the camera once and pass it around (never hand-roll offsets in drawing code),
and always `clamp()` — an unclamped camera is the classic "player walks into black void" bug.

## Parallax background layers

Background layers scroll slower than the world, which reads as depth. Multiply the camera offset
by a factor below 1 and tile the image horizontally:

```python
def draw_parallax(screen, layers, camera) -> None:
    """layers = [(surface, factor), ...] — 0.0 is static, 1.0 moves with the world."""
    for image, factor in layers:
        width = image.get_width()
        offset = -(camera.pos.x * factor) % width
        for x in range(offset, screen.get_width(), width):
            screen.blit(image, (round(x), 0))
```

`range(offset, ...)` starting at a negative value covers the left edge; the modulo keeps the
layer seamless over an infinitely scrolling world.

## Tile properties and a collision layer

Never re-scan the grid for collisions. Build the solid rects once, when the level loads:

```python
def build_collision(grid: list[list[str]]) -> list[pygame.Rect]:
    return [
        pygame.Rect(col * TILE, row * TILE, TILE, TILE)
        for row, line in enumerate(grid)
        for col, ch in enumerate(line)
        if TILES[ch]["solid"]
    ]


def nearby_solids(grid: list[list[str]], rect: pygame.Rect) -> list[pygame.Rect]:
    """Only the solid tiles that could touch this rect — O(area), not O(world)."""
    first_col = max(0, rect.left // TILE)
    last_col = min(len(grid[0]) - 1, rect.right // TILE)
    first_row = max(0, rect.top // TILE)
    last_row = min(len(grid) - 1, rect.bottom // TILE)
    return [
        pygame.Rect(col * TILE, row * TILE, TILE, TILE)
        for row in range(first_row, last_row + 1)
        for col in range(first_col, last_col + 1)
        if TILES[grid[row][col]]["solid"]
    ]
```

`nearby_solids` is what you actually want at runtime: it queries the *grid* (cheap) rather than
testing against 40,000 rects, and it composes with the axis-separated resolution from Chapter 32.
Keep separate layers for separate purposes — a solid layer for physics, a hazard layer for
damage, a spawn layer for entity placement — all derived from the same characters.

## Minimap

```python
def draw_minimap(surface, grid, scale: int = 3, padding: int = 8) -> None:
    width, height = len(grid[0]) * scale, len(grid) * scale
    panel = pygame.Surface((width + 8, height + 8), pygame.SRCALPHA)
    panel.fill((10, 12, 20, 170))
    for row, line in enumerate(grid):
        for col, ch in enumerate(line):
            pygame.draw.rect(panel, TILES[ch]["color"],
                             (4 + col * scale, 4 + row * scale, scale, scale))
    surface.blit(panel, (padding, padding))
```

Render the minimap from the same grid the world uses, so it can never disagree with it. On a big
map, cache the panel Surface and refresh it only when a tile changes.

## Procedural generation: seed everything

A generator is a function from a seed to a world. The moment you use the global `random` module,
that stops being true: your world depends on every previous call in the process, and a bug report
you cannot reproduce is a bug you cannot fix.

```python
import random

rng = random.Random(1234)        # local, isolated, reproducible
print(rng.randint(0, 100), rng.choice("abcd"))
```

Pass a `random.Random(seed)` instance into every generator. Now "world 8821 has an unreachable
chest" is a sentence someone can act on: run seed 8821, see the bug, fix it, re-run 8821.

### Technique 1: room placement and corridors

```python
def generate_rooms(width: int, height: int, seed: int,
                   max_rooms: int = 12, attempts: int = 60) -> tuple[list[list[str]], list]:
    rng = random.Random(seed)
    grid = [["#"] * width for _ in range(height)]
    rooms: list[pygame.Rect] = []

    for _ in range(attempts):
        room_w, room_h = rng.randint(5, 10), rng.randint(4, 8)
        room = pygame.Rect(rng.randint(1, width - room_w - 2),
                           rng.randint(1, height - room_h - 2), room_w, room_h)
        if any(room.inflate(2, 2).colliderect(other) for other in rooms):
            continue                                    # overlap: try another placement

        for y in range(room.top, room.bottom):          # carve the room
            for x in range(room.left, room.right):
                grid[y][x] = "."
        if rooms:
            carve_corridor(grid, rooms[-1].center, room.center, rng)
        rooms.append(room)
        if len(rooms) >= max_rooms:
            break
    return grid, rooms


def carve_corridor(grid, start: tuple[int, int], end: tuple[int, int], rng) -> None:
    x, y = start
    target_x, target_y = end
    if rng.random() < 0.5:                              # L-shaped, elbow randomised
        for x in _towards(x, target_x):
            grid[y][x] = "."
        for y in _towards(y, target_y):
            grid[y][x] = "."
    else:
        for y in _towards(y, target_y):
            grid[y][x] = "."
        for x in _towards(x, target_x):
            grid[y][x] = "."


def _towards(start: int, end: int):
    step = 1 if end >= start else -1
    return range(start, end + step, step)
```

The `rooms` list is the valuable output as much as the grid is: rooms are your spawn points,
chest locations, and boss arenas.

### Technique 2: cellular-automata caves

Organic-looking caves from a noise field, smoothed by a neighbour rule: a cell becomes wall if
four or more of its eight neighbours are wall.

```python
def generate_cave(width: int, height: int, seed: int,
                  fill: float = 0.45, steps: int = 5) -> list[list[str]]:
    rng = random.Random(seed)
    grid = [["#" if rng.random() < fill else "." for _ in range(width)] for _ in range(height)]

    for _ in range(steps):
        next_grid = [row[:] for row in grid]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                walls = sum(
                    grid[y + dy][x + dx] == "#"
                    for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                )
                if grid[y][x] == "#":
                    next_grid[y][x] = "#" if walls >= 4 else "."
                else:
                    next_grid[y][x] = "#" if walls >= 5 else "."
        grid = next_grid

    for x in range(width):                              # seal the border
        grid[0][x] = grid[height - 1][x] = "#"
    for y in range(height):
        grid[y][0] = grid[y][width - 1] = "#"
    return grid
```

Note `next_grid`: you must read from the old grid while writing to a new one, or the result
depends on iteration order and stops being deterministic. `fill` controls how open the cave is;
4–5 smoothing steps is the sweet spot.

### Technique 3: the drunkard's walk

Best for a single connected cavern — a walker that stumbles around carving floor until enough of
it exists.

```python
def generate_drunkard(width: int, height: int, seed: int,
                      target_floor: float = 0.35) -> list[list[str]]:
    rng = random.Random(seed)
    grid = [["#"] * width for _ in range(height)]
    x, y = width // 2, height // 2
    carved = 0
    needed = int(width * height * target_floor)

    while carved < needed:
        if grid[y][x] != ".":
            grid[y][x] = "."
            carved += 1
        dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        x = max(1, min(width - 2, x + dx))
        y = max(1, min(height - 2, y + dy))
    return grid
```

Note the guarantee: because the walker only ever moves from floor to floor, **everything it
carves is connected by construction**. That is why the drunkard's walk rarely needs validation
while room placement always does.

## Validating a generated map

Corridor carving can leave islands; cellular automata almost always do. Before you hand a map to
the player, flood fill from the spawn and check that every floor tile was reached.

```python
from collections import deque


def flood_fill(grid: list[list[str]], start: tuple[int, int]) -> set[tuple[int, int]]:
    height, width = len(grid), len(grid[0])
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen \
                    and grid[ny][nx] == ".":
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def is_fully_connected(grid: list[list[str]], min_ratio: float = 1.0) -> bool:
    floors = [(x, y) for y, line in enumerate(grid)
              for x, ch in enumerate(line) if ch == "."]
    if not floors:
        return False
    reached = flood_fill(grid, floors[0])
    return len(reached) >= len(floors) * min_ratio


def generate_valid(width: int, height: int, seed: int, max_attempts: int = 20):
    """Never return a broken map: bump the seed and retry instead."""
    for attempt in range(max_attempts):
        grid, rooms = generate_rooms(width, height, seed + attempt)
        if is_fully_connected(grid):
            return grid, rooms, seed + attempt
    raise RuntimeError(f"no valid map after {max_attempts} attempts from seed {seed}")
```

Allowing `min_ratio < 1.0` (say 0.8) trades strictness for speed when you do not mind a few
sealed-off bonus rooms — just delete the unreachable tiles rather than leaving them as
unreachable treasure.

## Placing entities, and scaling difficulty

Generate geometry first, then populate it. Rooms give you natural spawn zones; depth gives you
the difficulty curve.

```python
def difficulty_for(depth: int) -> dict:
    return {
        "enemies": 3 + depth * 2,
        "chests": max(1, 4 - depth // 3),
        "enemy_hp": 2 + depth // 2,
        "hazards": min(30, depth * 4),
    }


def place_entities(grid, rooms, seed: int, depth: int) -> dict:
    rng = random.Random(seed ^ 0x5EED)          # different stream from the layout
    stats = difficulty_for(depth)
    plan = {"player": None, "enemies": [], "chests": []}

    def point_in(room) -> tuple[int, int]:
        return (rng.randint(room.left, room.right - 1) * TILE + TILE // 2,
                rng.randint(room.top, room.bottom - 1) * TILE + TILE // 2)

    if rooms:
        plan["player"] = point_in(rooms[0])
        for room in rooms[1:]:
            for _ in range(stats["enemies"] // max(1, len(rooms) - 1)):
                plan["enemies"].append(point_in(room))
            if rng.random() < 0.6:
                plan["chests"].append(point_in(room))

    floors = [(x, y) for y, line in enumerate(grid)
              for x, ch in enumerate(line) if ch == "."]
    rng.shuffle(floors)
    for _ in range(stats["hazards"]):
        if floors:
            x, y = floors.pop()
            grid[y][x] = "^"
    return plan
```

`seed ^ 0x5EED` derives a second stream from the same seed, so one number still reproduces the
entire level — layout and contents — while layout and entity rolls stay statistically separate.

:::scenario "QA found a chest on an unreachable island and we cannot reproduce it"
A tester plays seed-less builds for an hour, finds one level where a chest sits behind solid rock,
and screenshots it. Nobody on the team can see the same level again. Meanwhile the level loader
takes four seconds to start a run.
:::

:::solution Log the seed, validate the map, and hoist generation out of the loop
Three fixes, in priority order:

1. **Make every run reproducible.** Generate one seed at startup, `seed = random.randrange(2**31)`,
   print it, show it on the debug overlay (Chapter 33), and accept it from the command line. Now
   "level 1908443721 is broken" is a ticket someone can open.

2. **Validate before you hand the map to the player**, using the flood-fill check above, and
   regenerate on failure. For the chest specifically, validate placements too — never place loot
   on a tile the player cannot walk to:

   ```python
   reachable = flood_fill(grid, plan["player"])
   plan["chests"] = [c for c in plan["chests"]
                     if (c[0] // TILE, c[1] // TILE) in reachable]
   ```

3. **Generate once, not every frame.** The four-second load is the classic symptom of a generator
   called inside the update loop:

   ```python
   # BROKEN: the world flickers and the game runs at 0.2 fps
   def update(self, dt):
       self.grid = generate_cave(200, 200, random.randrange(10**9))

   # RIGHT: once per level
   def on_enter(self):
       self.grid = generate_cave(200, 200, self.seed)
   ```

   Build the grid once, then build `TILE_IMAGES`, the collision rects, and the minimap panel from
   it once. Everything per frame should be a lookup.
:::

:::pitfall Generating every frame, or forgetting to seed
Two faces of the same mistake. If generation runs inside the loop, the world changes sixty times
a second — it flickers, collision rects go stale, and your frame time collapses. If you use the
global `random` module instead of `random.Random(seed)`, the world is different every run and no
bug is reproducible. Generate in `on_enter`, store the grid, and thread one `random.Random`
instance through every generator. If your game has no seed visible anywhere on screen, you have
already lost the next bug report.
:::

## Key takeaways

- A tilemap is a list of lists of tile ids; author levels as text so they are diffable and
  editable in seconds.
- Convert between tile, world, and screen coordinates with `col * TILE` and `world - camera`;
  keep those conversions in one place.
- Cull: compute the visible tile range from the camera and draw only that. It is the cheapest
  large win in a tile engine.
- A camera owns `apply()` / `apply_rect()` for world-to-screen conversion and clamps itself to
  world bounds; parallax is the same offset multiplied by a factor below 1.
- Build collision rects once at load time, and query `nearby_solids(grid, rect)` at runtime
  instead of testing the whole world.
- Every procedural generator takes a `random.Random(seed)` instance, never the global `random`
  module, so any world can be reproduced from one integer.
- Room-and-corridor, cellular automata, and the drunkard's walk produce dungeons, caves, and
  single connected caverns respectively; automate cellular steps from a copy of the grid.
- Validate generated maps with a flood fill and regenerate on failure; place entities only on
  reachable tiles and scale their counts by depth.

## Practice

- [ ] Write a 20×12 level in a text file using `#`, `.`, `^`, and `P`, load it, and draw it with
      one colour per tile type.
- [ ] Add culling to your draw loop and print `ms/frame` for the naive and culled versions side
      by side on a 200×200 map.
- [ ] Give the level a camera: smooth follow of a player rect, clamped to world bounds, with the
      player drawn through `camera.apply_rect`.
- [ ] Write `generate_cave` and prove reproducibility: generate the same cave twice with the same
      seed and assert the grids are equal.
- [ ] Add flood-fill validation with regeneration, place the player in the first room plus
      enemies and chests in the rest, and scale enemy count and hazards with `depth`.

## Solutions

:::solution Exercise 1
```python
import pygame
from pathlib import Path

TILE = 32
TILES = {
    "#": {"solid": True,  "hazard": False, "color": (72, 78, 100)},
    ".": {"solid": False, "hazard": False, "color": (28, 32, 44)},
    "^": {"solid": True,  "hazard": True,  "color": (214, 92, 92)},
    "P": {"solid": False, "hazard": False, "spawn": "player", "color": (28, 32, 44)},
}

grid = [list(line) for line in Path("data/level1.txt").read_text().splitlines() if line.strip()]
WIDTH, HEIGHT = len(grid[0]) * TILE, len(grid) * TILE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Text level")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((12, 14, 20))
    for row, line in enumerate(grid):
        for col, ch in enumerate(line):
            pygame.draw.rect(screen, TILES[ch]["color"],
                             (col * TILE, row * TILE, TILE, TILE))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```
Drawing rects instead of images is perfectly legitimate while you are iterating on layout — swap
in blitted tiles once the level design settles, and nothing else changes.
:::

:::solution Exercise 2
```python
import time
import pygame

def draw_tiles(screen, grid, cam_x, cam_y, culled: bool):
    rows, cols = len(grid), len(grid[0])
    if culled:
        row_range = range(max(0, cam_y // TILE),
                          min(rows, (cam_y + screen.get_height()) // TILE + 1))
        col_range = range(max(0, cam_x // TILE),
                          min(cols, (cam_x + screen.get_width()) // TILE + 1))
    else:
        row_range, col_range = range(rows), range(cols)
    drawn = 0
    for row in row_range:
        for col in col_range:
            pygame.draw.rect(screen, TILES[grid[row][col]]["color"],
                             (col * TILE - cam_x, row * TILE - cam_y, TILE, TILE))
            drawn += 1
    return drawn


def bench(screen, grid, frames=120):
    for label, culled in (("naive", False), ("culled", True)):
        start = time.perf_counter()
        drawn = 0
        for _ in range(frames):
            drawn = draw_tiles(screen, grid, 512, 512, culled)
            pygame.display.flip()
        ms = (time.perf_counter() - start) / frames * 1000
        print(f"{label:7s} {ms:6.2f} ms/frame  tiles drawn: {drawn}")
```
```text
naive    16.80 ms/frame  tiles drawn: 40000
culled    0.44 ms/frame  tiles drawn: 336
```
The tile count tells the whole story: 336 visible blits beat 40,000 every time. Numbers this
lopsided are why you should always print a work counter alongside the timing — it confirms the
optimisation did what you think it did.
:::

:::solution Exercise 3
```python
import pygame

WIDTH, HEIGHT = 640, 480
TILE = 32


class Camera:
    def __init__(self, world_w, world_h):
        self.pos = pygame.Vector2(0, 0)
        self.world_w, self.world_h = world_w, world_h

    def follow(self, target, dt, smooth=6.0):
        desired = pygame.Vector2(target.centerx - WIDTH / 2, target.centery - HEIGHT / 2)
        self.pos += (desired - self.pos) * min(1.0, smooth * dt)
        self.pos.x = max(0.0, min(self.pos.x, self.world_w - WIDTH))
        self.pos.y = max(0.0, min(self.pos.y, self.world_h - HEIGHT))

    def apply(self, rect):
        return rect.move(-round(self.pos.x), -round(self.pos.y))

    def apply_rect(self, entity):
        return self.apply(entity.rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    grid = [[".", ] * 60 for _ in range(40)]
    world_w, world_h = len(grid[0]) * TILE, len(grid) * TILE

    player = pygame.Rect(0, 0, 28, 28)
    player.center = (world_w // 2, world_h // 2)
    camera = Camera(world_w, world_h)
    camera.follow(player, 1.0, smooth=1.0)      # snap on the first frame

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.x += round((keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 260 * dt)
        player.y += round((keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 260 * dt)
        player.clamp_ip(pygame.Rect(0, 0, world_w, world_h))
        camera.follow(player, dt)

        screen.fill((16, 18, 26))
        for row in range(max(0, int(camera.pos.y) // TILE), min(len(grid), (int(camera.pos.y) + HEIGHT) // TILE + 1)):
            for col in range(max(0, int(camera.pos.x) // TILE), min(len(grid[0]), (int(camera.pos.x) + WIDTH) // TILE + 1)):
                pygame.draw.rect(screen, (40, 46, 64), (col * TILE - round(camera.pos.x), row * TILE - round(camera.pos.y), TILE, TILE), width=1)
        pygame.draw.rect(screen, (110, 214, 148), camera.apply(player), border_radius=5)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```
`camera.apply(player)` is the only transform in the draw code, which is what lets a 60×40-tile
world exist behind a 640×480 window. Clamping in `follow` means the camera stops at the edges
while the player keeps walking.
:::

:::solution Exercise 4
```python
import random


def generate_cave(width, height, seed, fill=0.45, steps=5):
    rng = random.Random(seed)
    grid = [["#" if rng.random() < fill else "." for _ in range(width)] for _ in range(height)]
    for _ in range(steps):
        nxt = [row[:] for row in grid]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                walls = sum(grid[y + dy][x + dx] == "#"
                            for dy in (-1, 0, 1) for dx in (-1, 0, 1))
                nxt[y][x] = "#" if walls >= (4 if grid[y][x] == "#" else 5) else "."
        grid = nxt
    return grid


def render(grid):
    return "\n".join("".join(row) for row in grid)


a = generate_cave(40, 20, seed=42)
b = generate_cave(40, 20, seed=42)
c = generate_cave(40, 20, seed=43)

assert render(a) == render(b), "same seed must give the same world"
assert render(a) != render(c), "different seeds must differ"
print(render(a))
```
The two asserts are the contract of a seeded generator, and they belong in your test suite
(Chapter 11). If they ever fail, something reached for the global `random` module — most likely a
stray `random.choice` you forgot to convert to `rng.choice`.
:::

:::solution Exercise 5
```python
from collections import deque


def reachable(grid, start):
    height, width = len(grid), len(grid[0])
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and grid[ny][nx] == ".":
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def build_level(seed, depth, width=60, height=40):
    for attempt in range(25):
        grid, rooms = generate_rooms(width, height, seed + attempt)
        if not rooms:
            continue
        spawn = (rooms[0].centerx, rooms[0].centery)
        floors = [(x, y) for y, line in enumerate(grid) for x, ch in enumerate(line) if ch == "."]
        seen = reachable(grid, spawn)
        if len(seen) < len(floors) * 0.9:
            continue                                  # too fragmented: next seed

        stats = {"enemies": 3 + depth * 2, "hazards": min(30, depth * 4)}
        for tile in [f for f in floors if f not in seen]:
            grid[tile[1]][tile[0]] = "#"              # delete unreachable pockets
        return grid, rooms, spawn, stats
    raise RuntimeError("no valid level generated")
```
Deleting unreachable tiles is often better than strict rejection: you keep the interesting
geometry, you throw away the parts that would strand the player or hide loot, and the same
flood-fill result tells you which tiles are legal spawn points. Run the check once at generation
time, not once per frame.
:::
