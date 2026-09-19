---
chapter: 31
part: 5
title: Pygame I: Window, Game Loop & Drawing
summary: Install pygame, open a window, and build a real game loop with delta-time movement, images, text and a first playable thing you can drive with the arrow keys.
minutes: 45
tags: [pygame, game loop, delta time, surfaces, rects, events]
---

Every program you have written so far runs top to bottom and exits. A game cannot work that
way: it has to keep answering questions — is a key held down, did the ball hit the wall, what
should be on screen right now — roughly sixty times a second, forever, until the player quits.
That single structural difference drives everything in this part of the book. Pygame gives you
a window, an event queue, and a pile of drawing functions; the *loop* that ties them together
is yours to write, and writing it well is the difference between a game that feels good and one
that stutters, freezes, or runs at a different speed on every machine.

## Installing pygame

```bash
python3 -m pip install pygame
```

Verify it before you write a single line of game code:

```python
# check_pygame.py
import sys
import pygame

print(f"pygame {pygame.version.ver} on Python {sys.version.split()[0]}")
```

```text
pygame 2.5.2 on Python 3.12.4
```

You need **pygame 2.x** (2.5+ recommended) on **Python 3.12+**. Anything from Part I applies
here too: install into a virtual environment (Chapter 10) once your game grows past a single
file.

:::note pygame vs pygame-ce
The project split in 2021. `pygame-ce` (Community Edition) is the actively developed fork and
ships as a drop-in replacement — you still `import pygame`, and `pygame.version.ver` reports a
`2.x` number. Every snippet in this book runs under either one. If a package you want declares
`pygame-ce` as a dependency, install that instead; nothing here changes.
:::

## The smallest window that works

```python
# blank.py
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Blank")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((24, 26, 34))
    pygame.display.flip()

pygame.quit()
```

Four calls do the heavy lifting:

1. `pygame.init()` boots every pygame subsystem (display, font, mixer, joystick). Call it once,
   at the top. It returns a `(successes, failures)` tuple you can ignore.
2. `pygame.display.set_mode((w, h))` creates the window and returns the **Surface** you draw
   onto. Store it — you will pass it to nearly every drawing function.
3. `pygame.display.flip()` pushes the finished frame to the screen. Until you call it (or
   `pygame.display.update()`), nothing you drew is visible.
4. `pygame.quit()` closes the window and releases resources. Without it, some platforms leave a
   frozen window or a stuck audio device behind.

## Why one draw is not a game

Beginners write this and are surprised when it does nothing useful:

```python
# not_a_game.py
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.draw.circle(screen, (230, 80, 90), (320, 240), 60)
pygame.display.flip()
pygame.quit()
```

The window appears and vanishes in the same instant. The tempting fix is
`pygame.time.wait(3000)` before `pygame.quit()` — and now you have a window that shows a circle
but ignores the mouse, ignores the keyboard, and gets the "application is not responding"
beachball on macOS, because the operating system keeps delivering events and nobody is reading
them.

The real fix is structure. Every game, from Pong to a 3D engine, runs the same three phases in
the same order, over and over:

| Phase | Question it answers | Typical work |
| --- | --- | --- |
| **Input** | What did the player do since last frame? | Drain the event queue, read held keys |
| **Update** | Where is everything now? | Move, collide, animate, spawn, score |
| **Draw** | What does the world look like? | Clear, blit, draw, flip |

```python
while running:
    handle_input()     # read events and held keys
    update(dt)         # move the world forward
    draw(screen)       # paint it
    clock.tick(FPS)    # wait until it is time for the next frame
```

Input before update means you react to this frame's keystrokes, not last frame's. Update before
draw means you never render a state that is half a step old. Get that order in your bones.

## Draining the event queue

Pygame does not hand you input when you ask for it; the OS appends events to a queue and pygame
buffers them. `pygame.event.get()` returns everything waiting and **empties the queue**. You
must call it every frame — if you don't, the queue grows without bound, `QUIT` never reaches
your code, and the OS marks your process as hung.

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            running = False
        elif event.key == pygame.K_SPACE:
            print("jump")
    elif event.type == pygame.KEYUP:
        print(f"released {pygame.key.name(event.key)}")
    elif event.type == pygame.MOUSEBUTTONDOWN:
        print(f"click at {event.pos}, button {event.button}")
    elif event.type == pygame.MOUSEMOTION:
        print(f"mouse moved to {event.pos}")
```

The events you will use constantly:

| Event | Fires when | Useful attributes |
| --- | --- | --- |
| `QUIT` | Window close button pressed | — |
| `KEYDOWN` | A key goes down (once) | `key`, `mod`, `unicode` |
| `KEYUP` | A key comes up | `key` |
| `MOUSEBUTTONDOWN` / `UP` | Mouse click | `pos`, `button` |
| `MOUSEMOTION` | Mouse moves | `pos`, `rel`, `buttons` |

`KEYDOWN` is *discrete*: it fires once per press, with OS key-repeat after a delay. Continuous
movement uses a different mechanism — see Chapter 32.

## Surfaces and Rects: the two types you will touch constantly

A **Surface** is a rectangular block of pixels. The window is a Surface. An image you load is a
Surface. Text you render is a Surface. Drawing always targets a Surface, and `blit` copies one
Surface onto another.

A **Rect** is pure geometry: `x, y, width, height`. It holds no pixels. You use it for position,
for collision, and as the destination argument to `blit`.

```python
player = pygame.Rect(100, 120, 48, 48)   # x, y, w, h
print(player.topleft, player.center, player.midbottom, player.right)
```

```text
(100, 120) (124, 144) (124, 168) 148
```

Rects give you dozens of aliases — `topleft`, `center`, `midbottom`, `bottomright`, `centerx`,
`size`, `w`, `h` — and assigning to any of them moves the rect. `other.get_rect()` is the
standard way to get a rect matching an image's size, and you can anchor it in one line:
`image.get_rect(center=(400, 300))`.

## The coordinate system

```text
(0,0) ──────────── x increases ──────────>
  │
  │        (400, 300) is right of (100, 300)
  │                  and ABOVE (100, 500)
  y
  increases
  downward
  │
  v
```

The origin is the **top-left corner** and **y grows downward**. This is the opposite of the
graph-paper maths you learned in school, and it trips people up constantly: increasing `y` moves
things *down*, so gravity is a positive `y` acceleration and "up" is negative.

## Drawing primitives

Name a colour once, use it everywhere. Pygame colours are `(r, g, b)` tuples, 0–255.

```python
# palette.py
BG      = (24, 26, 34)
PANEL   = (38, 42, 56)
INK     = (232, 234, 240)
CYAN    = (86, 204, 242)
ORANGE  = (244, 162, 97)
PINK    = (244, 114, 182)
GREEN   = (110, 214, 148)
```

```python
# shapes.py — every primitive, one screen
import pygame

BG, CYAN, ORANGE, PINK, GREEN, INK = (
    (24, 26, 34), (86, 204, 242), (244, 162, 97),
    (244, 114, 182), (110, 214, 148), (232, 234, 240),
)

pygame.init()
screen = pygame.display.set_mode((640, 420))
pygame.display.set_caption("Primitives")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG)

    pygame.draw.rect(screen, CYAN, (40, 40, 120, 80))               # filled
    pygame.draw.rect(screen, INK, (40, 40, 120, 80), width=3)       # outline
    pygame.draw.rect(screen, ORANGE, (200, 40, 120, 80), border_radius=14)

    pygame.draw.circle(screen, PINK, (110, 240), 50)
    pygame.draw.circle(screen, INK, (110, 240), 50, width=2)

    pygame.draw.ellipse(screen, GREEN, (220, 190, 160, 100))
    pygame.draw.line(screen, INK, (420, 40), (600, 200), width=4)
    pygame.draw.lines(screen, CYAN, False, [(420, 260), (480, 300), (560, 240)], width=3)
    pygame.draw.polygon(screen, ORANGE, [(440, 340), (520, 300), (600, 360), (500, 400)])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

`width=0` (the default) fills the shape; `width=n` strokes it. Note that these calls happen
*every frame* — that is cheap for primitives, and it is exactly what you do with shapes. Loading
an image every frame is not cheap, and we will get to that in a moment.

## Capping the frame rate

If you remove `clock.tick(60)`, the loop runs as fast as the CPU allows — two thousand frames
per second on a desktop, with the fan screaming and a laptop battery dying in forty minutes.
`pygame.time.Clock().tick(FPS)` sleeps just long enough to hold the target, and it returns how
many milliseconds passed since the previous call. Keep that return value; it is the foundation
of the next section.

## Delta time: move in pixels per second

Here is the bug that ships in a startling number of finished games:

```python
# BUG: speed depends on frame rate
player.x += 5          # "5 pixels per frame"
```

At 60 fps that is 300 px/sec. At 144 fps — a very ordinary gaming monitor — it is 720 px/sec.
Same code, different game, and the player with the faster machine moves more than twice as fast.

The fix is to stop counting frames and start counting seconds:

```python
# FIXED: speed is defined in pixels per second
SPEED = 300                       # px/sec, a real-world unit
dt = clock.tick(60) / 1000.0      # seconds since last frame (~0.0167 at 60fps)
player.x += SPEED * dt
```

Now the square crosses the screen in the same amount of wall-clock time on every machine, and
`SPEED` is a number you can reason about and tune.

:::note Clamp dt
After a tab switch, a breakpoint, or a slow loading stall, `clock.tick()` can report a huge
gap — 2 seconds, say — and your object teleports across the level, tunnelling straight through
walls. Clamp it: `dt = min(clock.tick(60) / 1000.0, 0.05)`. The game slows down for one frame
instead of breaking.
:::

## Images: load once, blit many

```python
import pygame
from pathlib import Path

def load_image(path: str | Path, scale: float = 1.0) -> pygame.Surface:
    """Load an image with alpha, optionally scaled. Call this at startup, never per frame."""
    image = pygame.image.load(str(path)).convert_alpha()
    if scale != 1.0:
        width, height = image.get_size()
        image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale))
        )
    return image
```

Two details matter:

- **`.convert_alpha()`** converts the pixel format to match the display, which makes blitting
  several times faster, and preserves transparency. Use plain `.convert()` only for images with
  no alpha channel (backgrounds).
- **Scaling and rotating are not free.** `pygame.transform.scale`, `.rotate`, and `.rotozoom`
  build a brand new Surface every call. Precompute them, or accept the cost knowingly.

```python
ship = load_image("assets/ship.png", scale=2.0)
rotated = pygame.transform.rotate(ship, 45)     # loses a little quality each call
smooth = pygame.transform.rotozoom(ship, 45, 1.0)  # filtered; better for animation

screen.blit(ship, ship.get_rect(center=(400, 300)))
```

:::tip No art yet? Generate a placeholder
Do not block on assets. Draw into a Surface with the primitives you already know and swap in
real art later:
```python
def placeholder(size: tuple[int, int], color: tuple[int, int, int]) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (size[0] // 2, size[1] // 2), min(size) // 2)
    return surf
```
:::

## Text: fonts and why you cache them

`pygame.font.Font(None, size)` loads pygame's built-in font; `pygame.font.SysFont("menlo", 24)`
uses a system font; `pygame.font.Font("assets/font.ttf", 24)` loads a file. Then
`font.render(text, antialias, color)` produces a Surface you blit like any other.

Creating a font object parses a font file. Creating one per frame is one of the fastest ways to
turn 60 fps into 8.

```python
class FontCache:
    """One Font object per (name, size). Build it once, reuse forever."""

    def __init__(self) -> None:
        self._fonts: dict[tuple[str | None, int], pygame.font.Font] = {}

    def get(self, size: int, name: str | None = None) -> pygame.font.Font:
        key = (name, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(name, size)
        return self._fonts[key]

    def render(self, text: str, size: int, color, name: str | None = None) -> pygame.Surface:
        return self.get(size, name).render(text, True, color)
```

Chapter 33 turns this into a full resource manager. The principle is identical: build once, look
up by key.

## Shutting down cleanly

`pygame.quit()` uninitialises every module. If you forget it, you can leave a zombie window or a
locked sound device that makes the *next* run fail. Wrap the loop so it happens even on a crash:

```python
def main() -> None:
    pygame.init()
    try:
        run_game()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
```

## Building it: a square you drive and a ball that bounces

```python
# first_game.py
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
SPEED = 300                       # pixels per second

BG     = (24, 26, 34)
PLAYER = (86, 204, 242)
BALL   = (244, 162, 97)
INK    = (232, 234, 240)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chapter 31 — drive the square")
    clock = pygame.time.Clock()

    # --- once, before the loop -------------------------------------------
    font = pygame.font.Font(None, 32)
    small = pygame.font.Font(None, 22)

    player = pygame.Rect(0, 0, 48, 48)
    player.center = (WIDTH // 2, HEIGHT // 2)

    ball_pos = pygame.Vector2(140, 90)
    ball_vel = pygame.Vector2(260, 190)
    BALL_R = 15

    score = 0
    running = True

    while running:
        # --- 1. input ---------------------------------------------------
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]

        # --- 2. update --------------------------------------------------
        player.x += round(dx * SPEED * dt)
        player.y += round(dy * SPEED * dt)
        player.clamp_ip(screen.get_rect())

        ball_pos += ball_vel * dt
        if ball_pos.x - BALL_R < 0:
            ball_pos.x, ball_vel.x = BALL_R, abs(ball_vel.x)
        elif ball_pos.x + BALL_R > WIDTH:
            ball_pos.x, ball_vel.x = WIDTH - BALL_R, -abs(ball_vel.x)
        if ball_pos.y - BALL_R < 0:
            ball_pos.y, ball_vel.y = BALL_R, abs(ball_vel.y)
        elif ball_pos.y + BALL_R > HEIGHT:
            ball_pos.y, ball_vel.y = HEIGHT - BALL_R, -abs(ball_vel.y)

        ball_rect = pygame.Rect(0, 0, BALL_R * 2, BALL_R * 2)
        ball_rect.center = (round(ball_pos.x), round(ball_pos.y))

        if ball_rect.colliderect(player):
            score += 1
            ball_vel = ball_vel.rotate(37) * 1.04     # deflect and speed up a little

        # --- 3. draw ----------------------------------------------------
        screen.fill(BG)
        pygame.draw.circle(screen, BALL, ball_rect.center, BALL_R)
        pygame.draw.rect(screen, PLAYER, player, border_radius=8)
        screen.blit(font.render(f"Score {score}", True, INK), (16, 14))
        screen.blit(
            small.render(f"{clock.get_fps():5.1f} fps — arrows to move, Esc to quit",
                         True, (150, 156, 170)),
            (16, HEIGHT - 32),
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

Study what lives where. Fonts, the player rect, and the ball's initial state are built *once*.
Only arithmetic, collision, and drawing happen per frame. That distinction is the whole
performance story of a 2D game.

:::scenario "It runs at 12 fps on my laptop and 60 on my desktop"
You finished a game with twenty animated enemies. On your desktop it is smooth. On a friend's
laptop it crawls, and the fan spins up. Same code, same assets, wildly different result.
:::

:::solution Measure where the frame goes, then move work out of the loop
Do not guess. Time the two halves of your loop for a hundred frames:

```python
import time

samples = {"update": 0.0, "draw": 0.0}
for _ in range(100):
    t0 = time.perf_counter()
    update(dt)
    t1 = time.perf_counter()
    draw(screen)
    t2 = time.perf_counter()
    samples["update"] += t1 - t0
    samples["draw"] += t2 - t1

print({k: round(v / 100 * 1000, 2) for k, v in samples.items()}, "ms/frame avg")
```

```text
{'update': 2.71, 'draw': 78.40} ms/frame avg
```

78 ms of drawing is 12 fps — that is your bug, and it is almost never the `pygame.draw` calls.
Grep the draw path for the three classic offenders:

```python
# 1. loading from disk 60 times a second
image = pygame.image.load("assets/enemy.png")            # move to startup
# 2. building a font object per frame
label = pygame.font.Font("assets/ui.ttf", 24).render(...)  # cache the Font
# 3. re-rendering text that has not changed
screen.blit(font.render("Score 12", True, INK), (0, 0))  # cache the Surface
```

Fix all three — load into a dict at startup, cache fonts by size, and only re-render a label
when its value changes — and the same scene drops to 3 ms and a locked 60 fps. The general
lesson transfers to Chapter 29 and every server you will ever write: disk and allocation inside
a hot loop are the enemy, and a profiler tells you which loop is hot.
:::

:::pitfall Doing per-frame work that belongs at startup
`pygame.image.load()`, `pygame.font.Font()`, `pygame.transform.scale()`, and
`pygame.Surface((...))` all read from disk or allocate memory. Inside the loop they run sixty
times a second and cost more than everything else combined. The rule is mechanical: **if the
result would be identical every frame, compute it once and store it.** When you catch yourself
writing a load or a font constructor inside `while running:`, that is the bug.
:::

## Key takeaways

- A game is a loop of input → update → draw, repeated until the player quits; a script that
  draws once and exits is not a game.
- `pygame.event.get()` drains the queue every frame; skipping it makes the window unresponsive
  and swallows `QUIT`.
- A Surface holds pixels; a Rect holds `x, y, w, h` and no pixels. You position and collide with
  Rects, you draw onto Surfaces.
- Screen coordinates start at the top-left and y grows downward, so gravity is a positive `y`.
- `clock.tick(FPS)` caps the frame rate and returns elapsed milliseconds; divide by 1000 to get
  `dt` in seconds.
- Multiply speeds by `dt` and express them in pixels per second, so movement is identical at 30,
  60 and 144 fps.
- Load images, fonts, and scaled/rotated Surfaces once at startup, then blit the cached result
  every frame.
- Always reach `pygame.quit()`, ideally in a `finally`, so the window and audio device release
  cleanly.

## Practice

- [ ] Change `blank.py` into a 640×480 window titled "Workbench", filled dark grey, that closes
      on both the window button and the `Escape` key.
- [ ] Draw a static scene with at least five primitives (rect, circle, ellipse, line, polygon)
      from a palette dict, and keep it on screen until the user quits.
- [ ] Make a 30 px ball bounce around the window forever, reversing direction at each edge, at
      a speed defined in pixels per second.
- [ ] Add an arrow-key-controlled 48×48 square that moves at 240 px/s using `dt`, is clamped
      inside the window, and displays its own position as text in the corner.
- [ ] Extend the square so it follows the mouse with smoothing (`rect.center` lerps toward
      `pygame.mouse.get_pos()`), render an FPS counter with a cached font, and print
      `MOUSEBUTTONDOWN` coordinates to the console.

## Solutions

:::solution Exercise 1
```python
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Workbench")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill((40, 42, 50))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```
Two independent quit paths is the minimum viable exit: players click the X far more often than
they find your keybind, and you need `Escape` anyway once the game goes fullscreen.
:::

:::solution Exercise 2
```python
import pygame

PALETTE = {
    "bg": (24, 26, 34), "cyan": (86, 204, 242),
    "orange": (244, 162, 97), "pink": (244, 114, 182), "ink": (232, 234, 240),
}

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Static scene")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(PALETTE["bg"])
    pygame.draw.rect(screen, PALETTE["cyan"], (40, 40, 140, 90), border_radius=10)
    pygame.draw.circle(screen, PALETTE["pink"], (320, 90), 45)
    pygame.draw.ellipse(screen, PALETTE["orange"], (400, 40, 150, 90))
    pygame.draw.line(screen, PALETTE["ink"], (40, 220), (560, 300), width=3)
    pygame.draw.polygon(screen, PALETTE["cyan"], [(200, 330), (300, 230), (400, 330)])
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```
"Static" means the same commands run every frame, not that the loop stops. The loop must keep
spinning so the event queue drains; the drawing just happens to produce the same picture.
:::

:::solution Exercise 3
```python
import pygame

WIDTH, HEIGHT = 640, 480
SPEED = 280          # px per second

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bounce")
clock = pygame.time.Clock()

pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
vel = pygame.Vector2(SPEED * 0.7, SPEED * 0.7)
R = 15

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pos += vel * dt
    if pos.x - R < 0:
        pos.x, vel.x = R, abs(vel.x)
    elif pos.x + R > WIDTH:
        pos.x, vel.x = WIDTH - R, -abs(vel.x)
    if pos.y - R < 0:
        pos.y, vel.y = R, abs(vel.y)
    elif pos.y + R > HEIGHT:
        pos.y, vel.y = HEIGHT - R, -abs(vel.y)

    screen.fill((24, 26, 34))
    pygame.draw.circle(screen, (244, 162, 97), (round(pos.x), round(pos.y)), R)
    pygame.display.flip()

pygame.quit()
```
Setting the velocity with `abs()` / `-abs()` rather than negating it guarantees the ball is
moving away from the wall it just hit; plain negation can leave it stuck oscillating inside the
edge after a clamp.
:::

:::solution Exercise 4
```python
import pygame

WIDTH, HEIGHT = 640, 480
SPEED = 240

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arrow keys")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 26)

player = pygame.Rect(0, 0, 48, 48)
player.center = (WIDTH // 2, HEIGHT // 2)

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.x += round((keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * SPEED * dt)
    player.y += round((keys[pygame.K_DOWN] - keys[pygame.K_UP]) * SPEED * dt)
    player.clamp_ip(screen.get_rect())

    screen.fill((24, 26, 34))
    pygame.draw.rect(screen, (86, 204, 242), player, border_radius=6)
    screen.blit(font.render(f"pos {player.topleft}", True, (232, 234, 240)), (12, 12))
    pygame.display.flip()

pygame.quit()
```
`clamp_ip` mutates the rect in place to keep it inside the given rect — no manual bounds checks.
The `_ip` suffix means "in place"; the non-`_ip` variants return a new Rect instead.
:::

:::solution Exercise 5
```python
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Follow + FPS")
clock = pygame.time.Clock()
fonts = {24: pygame.font.Font(None, 24), 18: pygame.font.Font(None, 18)}

player = pygame.Rect(0, 0, 44, 44)
player.center = (320, 240)
SMOOTH = 6.0

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"click {event.pos} button {event.button}")

    target = pygame.Vector2(pygame.mouse.get_pos())
    centre = pygame.Vector2(player.center).lerp(target, min(1.0, SMOOTH * dt))
    player.center = (round(centre.x), round(centre.y))

    screen.fill((24, 26, 34))
    pygame.draw.rect(screen, (110, 214, 148), player, border_radius=8)
    screen.blit(fonts[24].render(f"{clock.get_fps():5.1f} fps", True, (232, 234, 240)), (12, 12))
    screen.blit(fonts[18].render("click to log coords", True, (150, 156, 170)), (12, 40))
    pygame.display.flip()

pygame.quit()
```
`Vector2.lerp(target, t)` with `t = SMOOTH * dt` gives frame-rate-independent easing: the same
visual smoothing at any fps. Clamping `t` to 1.0 keeps a long frame from overshooting past the
target.
:::
