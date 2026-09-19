---
chapter: 32
part: 5
title: Pygame II: Sprites, Input & Collisions
summary: Use sprites and groups, handle continuous and discrete input correctly, resolve collisions without sticking to walls, and build a complete space shooter with pooling, animation and sound.
minutes: 50
tags: [pygame, sprites, collisions, physics, camera, pooling, animation]
---

Chapter 31 gave you a loop and a moving square. That is enough for a toy, not for a game. The
moment you have twenty enemies, a hundred bullets, and a player who must stop at walls instead of
sliding through them, hand-rolled lists of rects turn into a mess of duplicated loops. Pygame
answers with two small classes — `Sprite` and `Group` — plus a collision module that does the
broad-phase work for you. Add the correct way to read input, a physics step that separates axes,
and a camera, and you have everything a 2D game needs. We build a complete shooter at the end.

## Sprites and Groups

A **Sprite** is any game object that has an `image` (a Surface) and a `rect` (where it is). A
**Group** is a container of sprites that can update them all and draw them all.

```python
import random
import pygame

WIDTH, HEIGHT = 480, 720


class Star(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(*groups)          # registers with every group passed in
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (220, 226, 240), (3, 3), 3)
        self.rect = self.image.get_rect(center=pos)
        self.speed = random.randint(40, 160)

    def update(self, dt: float, *args) -> None:
        self.rect.y += round(self.speed * dt)
        if self.rect.top > HEIGHT:
            self.kill()                    # removes itself from every group
```

Two behaviours are worth memorising because they are the entire API:

- `group.update(dt, *extra)` calls `sprite.update(dt, *extra)` on every member. Extra arguments
  are passed straight through, so `group.update(dt, keys)` works if your sprites accept them.
- `group.draw(surface)` blits each member's `image` at its `rect`. It draws in insertion order;
  for z-ordering use `pygame.sprite.LayeredUpdates` and pass `_layer` on construction.

Other members you will use daily: `len(group)`, `for s in group`, `group.add(...)`,
`group.empty()`, `sprite.kill()`, `sprite.alive()`, and `group.sprites()` when you need a real
list (usually before mutating the group while iterating it).

:::note Why `*args` in update
`Group.update` passes the same arguments to every sprite, so a sprite that does not care about
`keys` still has to tolerate it. `def update(self, dt, *args)` is the idiomatic signature.
:::

## Input: held keys vs pressed keys

Events are **discrete**: `KEYDOWN` fires once when the key goes down. Movement is
**continuous**: you want to know "is Left held down, right now". That is
`pygame.key.get_pressed()`, which returns a sequence of booleans indexed by key constant.

| You want | Use |
| --- | --- |
| "Is the key held?" (movement, charging) | `pygame.key.get_pressed()` in update |
| "Did it just happen?" (jump, shoot, pause, type) | `KEYDOWN` / `KEYUP` events |
| Text entry | `event.unicode` on `KEYDOWN` |

```python
keys = pygame.key.get_pressed()
dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]     # True/False act as 1/0
dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
```

Booleans are integers in Python, so subtracting them gives you `-1`, `0`, or `1` — a direction
vector for free.

### Normalize diagonals

Add `dx` and `dy` and you get the classic bug: holding Right+Down moves the player 1.41× faster
than holding Right alone, because the vector `(1, 1)` is longer than `(1, 0)`. Players notice,
and speedrunners exploit it.

```python
vel = pygame.Vector2(dx, dy)
if vel.length_squared() > 0:          # cheaper than length(); avoids a sqrt
    vel = vel.normalize() * SPEED     # now every direction is exactly SPEED
```

`normalize()` scales the vector to length 1. Guard against the zero vector — `normalize()` on
`(0, 0)` raises `ValueError` in recent pygame, and at best returns garbage.

## Collisions

Four tools, in increasing cost and precision:

```python
# 1. Rect vs Rect — cheapest, and usually enough
if player.rect.colliderect(wall.rect): ...

# 2. Sprite vs Group — returns the list of overlapping sprites
hits = pygame.sprite.spritecollide(player, enemies, dokill=False)
for enemy in hits: ...

# 3. Group vs Group — returns {sprite_from_a: [sprites_from_b, ...]}
hits = pygame.sprite.groupcollide(bullets, enemies, dokilla=True, dokillb=True)
for bullet, victims in hits.items():
    score += len(victims)

# 4. Pixel-perfect, via masks
self.mask = pygame.mask.from_surface(self.image)
hits = pygame.sprite.spritecollide(player, spikes, False, pygame.sprite.collide_mask)
```

`colliderect` is a rectangle test, and for most games a rectangle is *too big* — a spaceship's
image is mostly empty corners. Use a **hitbox** smaller than the sprite:

```python
self.rect = self.image.get_rect(center=pos)     # drawing + broad phase
self.hitbox = self.rect.inflate(-18, -14)       # what actually takes hits
```

Then feed a custom callback so the collision uses the hitbox while drawing still uses the rect:

```python
def player_hit(player, enemy) -> bool:
    return player.hitbox.colliderect(enemy.rect)

if pygame.sprite.spritecollide(player, enemies, dokill=True, collided=player_hit):
    game_over()
```

The callback receives `(sprite, group_member)` and returns a bool. `dokill=True` only kills the
group member; the lone sprite is your responsibility.

:::warning Masks cost, and they go stale
`collide_mask` builds a bitmask per sprite and compares overlapping bits — precise for irregular
shapes, but far slower than a rect test and wrong the moment you swap `self.image` without
rebuilding `self.mask`. Use it for a handful of objects (player vs spikes), never for
bullet-vs-everything.
:::

## Platformer physics: gravity, jump, axis-separated resolution

Platformer movement has one rule that fixes a surprising number of bugs: **move on one axis,
resolve collisions, then move on the other axis and resolve again.** Resolving both at once makes
it impossible to tell whether you hit a floor or a wall, so players stick to walls and fall
through floors.

```python
# platformer.py — gravity, jumping with coyote time, axis-separated collision
import pygame

TILE = 40
LEVEL = [
    "####################",
    "#..................#",
    "#..................#",
    "#........###.......#",
    "#..................#",
    "#.....####.........#",
    "#..................#",
    "#..............##..#",
    "#..................#",
    "####################",
]
WIDTH, HEIGHT = len(LEVEL[0]) * TILE, len(LEVEL) * TILE
GRAVITY = 2000     # px/sec^2, positive is DOWN
JUMP = -640        # px/sec, negative is UP
MOVE = 260         # px/sec
COYOTE = 0.10      # seconds of grace after walking off a ledge


def build_tiles(level: list[str]) -> list[pygame.Rect]:
    return [
        pygame.Rect(col * TILE, row * TILE, TILE, TILE)
        for row, line in enumerate(level)
        for col, ch in enumerate(line)
        if ch == "#"
    ]


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Platformer physics")
    clock = pygame.time.Clock()
    tiles = build_tiles(LEVEL)

    player = pygame.Rect(0, 0, 28, 36)
    player.midbottom = (2 * TILE, 9 * TILE)
    vel = pygame.Vector2(0, 0)
    coyote = 0.0

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if coyote > 0:                 # coyote time: still allowed to jump
                    vel.y = JUMP
                    coyote = 0.0

        keys = pygame.key.get_pressed()
        vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE

        # --- vertical: integrate, move, resolve -------------------------
        vel.y = min(vel.y + GRAVITY * dt, 1200)
        player.y += round(vel.y * dt)
        on_ground = False
        for tile in tiles:
            if player.colliderect(tile):
                if vel.y > 0:
                    player.bottom = tile.top
                    on_ground = True
                elif vel.y < 0:
                    player.top = tile.bottom
                vel.y = 0

        # --- horizontal: move, resolve (separately!) --------------------
        player.x += round(vel.x * dt)
        for tile in tiles:
            if player.colliderect(tile):
                if vel.x > 0:
                    player.right = tile.left
                elif vel.x < 0:
                    player.left = tile.right
                vel.x = 0

        coyote = COYOTE if on_ground else max(0.0, coyote - dt)

        screen.fill((24, 26, 34))
        for tile in tiles:
            pygame.draw.rect(screen, (60, 66, 86), tile)
        pygame.draw.rect(screen, (110, 214, 148), player, border_radius=5)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

Three details make it feel right. Gravity integrates into velocity rather than position, so
jumps arc properly. Terminal velocity (`min(..., 1200)`) stops the player from tunnelling when a
frame is long. And **coyote time** — a tenth of a second of grace after leaving the ground —
turns "the jump didn't register!" into "that felt fair". Jump buffering (remembering a jump
pressed slightly before landing) is the mirror image of it, and both are three lines of code.

## Animation: an accumulator, then sprite sheets

Do not animate per frame; animate per *time*. A 10 fps walk cycle should take the same wall-clock
time whether the game is at 60 or 144 fps.

```python
class Animation:
    def __init__(self, frames: list[pygame.Surface], fps: float = 10, loop: bool = True):
        self.frames, self.step, self.loop = frames, 1.0 / fps, loop
        self.time = 0.0
        self.index = 0
        self.done = False

    def update(self, dt: float) -> None:
        if self.done:
            return
        self.time += dt
        while self.time >= self.step:      # while, not if: catches long frames
            self.time -= self.step
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.done = True

    @property
    def image(self) -> pygame.Surface:
        return self.frames[self.index]
```

Sprite sheets are one image holding every frame. Slice them once at load time:

```python
def strip_frames(sheet: pygame.Surface, frame_w: int, frame_h: int,
                 count: int | None = None) -> list[pygame.Surface]:
    count = count or sheet.get_width() // frame_w
    return [sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
            for i in range(count)]

walk = Animation(strip_frames(sheet, 32, 32, 6), fps=12)
```

:::note Subsurfaces share pixels
`subsurface()` returns a view onto the parent, not a copy — cheap, but the parent Surface must
stay alive or the children point at freed memory. Keep the sheet referenced (a resource manager,
as in Chapter 33, does this for you).
:::

## A camera that follows the player

Once the world is bigger than the window, everything you draw needs a world-to-screen transform.
Put it in one class so you never sprinkle `- camera.x` through your code.

```python
class Camera:
    def __init__(self, view_w: int, view_h: int, world_w: int, world_h: int):
        self.view = pygame.Rect(0, 0, view_w, view_h)
        self.world = pygame.Rect(0, 0, world_w, world_h)
        self.pos = pygame.Vector2(0, 0)     # top-left of the view, in world pixels

    def update(self, target: pygame.sprite.Sprite, dt: float, smooth: float = 6.0) -> None:
        desired = pygame.Vector2(target.rect.centerx - self.view.width / 2,
                                 target.rect.centery - self.view.height / 2)
        self.pos += (desired - self.pos) * min(1.0, smooth * dt)
        self.clamp()

    def snap(self, target: pygame.sprite.Sprite) -> None:
        self.pos.update(target.rect.centerx - self.view.width / 2,
                        target.rect.centery - self.view.height / 2)
        self.clamp()

    def clamp(self) -> None:
        max_x = max(0, self.world.width - self.view.width)
        max_y = max(0, self.world.height - self.view.height)
        self.pos.x = max(0.0, min(self.pos.x, max_x))
        self.pos.y = max(0.0, min(self.pos.y, max_y))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """World rect -> screen rect. Returns a copy, safe for tiles and images."""
        return rect.move(-round(self.pos.x), -round(self.pos.y))

    def apply_rect(self, entity: pygame.sprite.Sprite) -> pygame.Rect:
        """Same transform for a sprite that owns a .rect."""
        return self.apply(entity.rect)
```

Draw with `screen.blit(image, camera.apply_rect(sprite))`. `clamp()` keeps the view inside the
level so you never show the void beyond the edges; without it, the camera follows the player off
into blackness. Chapter 34 extends this with parallax and culling.

## Projectiles and object pooling

Creating and destroying hundreds of bullets per second churns memory and fragments it. Preallocate
a fixed number, take one when you fire, and hand it back when it dies.

```python
class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups: list[pygame.sprite.Group]):
        super().__init__()                 # start OUT of every group
        self.groups = groups
        self.image = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 236, 150), (0, 0, 6, 16), border_radius=3)
        self.rect = self.image.get_rect()
        self.vel = pygame.Vector2(0, 0)
        self.expired = False

    def activate(self, pos, vel) -> None:
        self.rect.midbottom = pos
        self.vel.update(vel)
        self.expired = False
        for group in self.groups:
            group.add(self)

    def update(self, dt: float, *args) -> None:
        self.rect.y += round(self.vel.y * dt)
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.expired = True            # the pool reclaims it, not us


class BulletPool:
    def __init__(self, size: int, groups: list[pygame.sprite.Group]):
        self.free = [Bullet(groups) for _ in range(size)]

    def spawn(self, pos, vel) -> None:
        if self.free:
            self.free.pop().activate(pos, vel)

    def release(self, bullet: Bullet) -> None:
        bullet.kill()                      # out of every group
        self.free.append(bullet)
```

The bullet never returns itself to the pool — it only flags `expired`. The game loop decides,
which keeps ownership in one place and makes the pool usable with collisions too (a bullet that
hits an enemy is released exactly like one that flies off screen).

## Sound

Call `pygame.mixer.pre_init(44100, -16, 2, 512)` *before* `pygame.init()` for low-latency
playback. Then load each sound once and keep the object:

```python
from pathlib import Path
import pygame

def try_sound(path: str, volume: float = 0.3):
    """Load a sound if the file exists, else return None. Never load inside the loop."""
    if not Path(path).is_file():
        return None
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound

shoot_sfx = try_sound("assets/shoot.wav")
if shoot_sfx:
    shoot_sfx.play()

pygame.mixer.music.load("assets/music.ogg")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)                # -1 = loop forever
```

Use `mixer.Sound` for effects and `mixer.music` for one streamed background track. If a sound
fires more than a few times a second, cap it:
`channel = pygame.mixer.find_channel(); if channel: channel.play(sfx)` — otherwise every enemy
death spawns a channel and you hit the 8-channel default limit.

## Building it: a complete space shooter

```python
# shooter.py
import random
from pathlib import Path
import pygame

WIDTH, HEIGHT = 480, 720
FPS = 60
BG = (16, 18, 28)
INK = (232, 234, 240)


def try_sound(path: str, volume: float = 0.3):
    if not Path(path).is_file():
        return None
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound


def player_hit(player, enemy) -> bool:
    return player.hitbox.colliderect(enemy.rect)


class Player(pygame.sprite.Sprite):
    SPEED = 320
    FIRE_RATE = 0.16

    def __init__(self, fire):
        super().__init__()
        self.image = pygame.Surface((38, 44), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (120, 220, 255),
                            [(19, 0), (38, 44), (19, 34), (0, 44)])
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
        self.hitbox = self.rect.inflate(-18, -14)
        self.cooldown = 0.0
        self.fire = fire

    def update(self, dt: float, keys) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        move = pygame.Vector2(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                              keys[pygame.K_DOWN] - keys[pygame.K_UP])
        if move.length_squared():
            move = move.normalize() * self.SPEED
            self.rect.x += round(move.x * dt)
            self.rect.y += round(move.y * dt)
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self.hitbox.center = self.rect.center

        if keys[pygame.K_SPACE] and self.cooldown == 0.0:
            self.fire(self.rect.midtop)
            self.cooldown = self.FIRE_RATE


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: int, radius: int, speed: int):
        super().__init__()
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (240, 90, 110), (radius, radius), radius)
        pygame.draw.circle(self.image, (255, 210, 220), (radius, radius), max(2, radius // 3))
        self.rect = self.image.get_rect(center=(x, -radius))
        self.speed = speed

    def update(self, dt: float, *args) -> None:
        self.rect.y += round(self.speed * dt)
        if self.rect.top > HEIGHT:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__()
        self.groups = groups
        self.image = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 236, 150), (0, 0, 6, 16), border_radius=3)
        self.rect = self.image.get_rect()
        self.vel = pygame.Vector2(0, 0)
        self.expired = False

    def activate(self, pos, vel) -> None:
        self.rect.midbottom = pos
        self.vel.update(vel)
        self.expired = False
        for group in self.groups:
            group.add(self)

    def update(self, dt: float, *args) -> None:
        self.rect.y += round(self.vel.y * dt)
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.expired = True


class BulletPool:
    def __init__(self, size: int, groups):
        self.free = [Bullet(groups) for _ in range(size)]

    def spawn(self, pos, vel) -> None:
        if self.free:
            self.free.pop().activate(pos, vel)

    def release(self, bullet: Bullet) -> None:
        bullet.kill()
        self.free.append(bullet)


def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chapter 32 — shooter")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    shoot_sfx = try_sound("assets/shoot.wav", 0.25)
    boom_sfx = try_sound("assets/boom.wav", 0.5)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    groups = [all_sprites, bullets]

    pool = BulletPool(64, groups)

    def fire(pos) -> None:
        pool.spawn(pos, (0, -640))
        if shoot_sfx:
            shoot_sfx.play()

    player = Player(fire)
    all_sprites.add(player)

    score = 0
    spawn_timer = 0.0
    alive = True
    running = True

    def reset() -> None:
        nonlocal score, alive, spawn_timer
        for enemy in list(enemies):
            enemy.kill()
        for bullet in list(bullets):
            pool.release(bullet)
        score, alive, spawn_timer = 0, True, 0.0
        player.rect.midbottom = (WIDTH // 2, HEIGHT - 20)
        player.hitbox.center = player.rect.center

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and not alive:
                    reset()

        keys = pygame.key.get_pressed()

        if alive:
            spawn_timer -= dt
            if spawn_timer <= 0.0:
                spawn_timer = 0.5
                enemy = Enemy(random.randint(24, WIDTH - 24),
                              random.randint(12, 22), random.randint(80, 170))
                all_sprites.add(enemy)
                enemies.add(enemy)

            all_sprites.update(dt, keys)

            # reclaim bullets that left the screen
            for bullet in [b for b in bullets if b.expired]:
                pool.release(bullet)

            # bullets vs enemies: kill the enemy, keep the bullet (we recycle it)
            hits = pygame.sprite.groupcollide(bullets, enemies, False, True)
            for bullet, victims in hits.items():
                pool.release(bullet)
                score += len(victims)
                if boom_sfx:
                    boom_sfx.play()

            if pygame.sprite.spritecollide(player, enemies, True, collided=player_hit):
                alive = False

        screen.fill(BG)
        all_sprites.draw(screen)
        screen.blit(font.render(f"Score {score}", True, INK), (14, 12))
        if not alive:
            label = font.render("GAME OVER — press R", True, (244, 114, 182))
            screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

Drop any `.wav` files into `assets/` and they play; leave them out and `try_sound` returns
`None` and the game runs silent. That is the pattern you want for optional assets — never let a
missing file crash a build.

:::scenario "The player sticks to walls, and at high speed falls through the floor"
You ship a build. Two reports come in: on a 144 Hz monitor the player sometimes clips through a
platform when falling fast, and on a ladder-adjacent wall the player "sticks" and stops falling
while pressing into it.
:::

:::solution Separate the axes, then substep
Both symptoms come from the same mistake: moving on both axes in one step and then guessing which
surface was hit. When `dx` and `dy` are applied together, a fast diagonal move can land the player
entirely *past* a thin platform (tunnelling), and a corner overlap gets resolved against a wall
as if it were a floor, which zeroes vertical velocity and leaves the player glued in mid-air.

Fix it in two steps. First, resolve one axis at a time, as in the platformer code above — vertical
movement settles floors and ceilings, horizontal movement settles walls, and each resolution knows
which way it was moving.

Second, stop letting a single frame move further than your thinnest wall:

```python
MAX_STEP = TILE // 2          # never move more than half a tile per substep

def move_axis(entity, tiles, dx, dy):
    entity.rect.x += round(dx)
    for t in tiles:
        if entity.rect.colliderect(t):
            entity.rect.right = t.left if dx > 0 else entity.rect.right
            entity.rect.left = t.right if dx < 0 else entity.rect.left
    entity.rect.y += round(dy)
    for t in tiles:
        if entity.rect.colliderect(t):
            if dy > 0:
                entity.rect.bottom = t.top
                entity.on_ground = True
            elif dy < 0:
                entity.rect.top = t.bottom

def move_and_collide(entity, tiles, vel, dt):
    remaining = pygame.Vector2(vel.x * dt, vel.y * dt)
    steps = max(1, int(max(abs(remaining.x), abs(remaining.y)) // MAX_STEP) + 1)
    for _ in range(steps):
        move_axis(entity, tiles, remaining.x / steps, remaining.y / steps)
```

`move_and_collide` splits the frame's movement into chunks small enough that no chunk can skip a
tile. This is the standard fix for tunnelling in every 2D engine, and it costs nothing at normal
speeds because `steps` is 1.
:::

:::pitfall Checking collisions before moving, or resolving both axes together
The tempting order is *move, move, then check everything* — apply `dx` and `dy`, then loop over
tiles and push the player out. You now cannot tell a floor hit from a wall hit, so you pick wrong,
zero the wrong velocity, and the player either sticks to walls or sinks through floors. The
correct order per frame is: **move X → resolve X → move Y → resolve Y → check collisions against
the final position.**
:::

## Key takeaways

- A `Sprite` needs an `image` and a `rect`; `super().__init__(*groups)` registers it, and
  `kill()` removes it from every group.
- `group.update(*args)` forwards arguments to every sprite's `update`; `group.draw(surface)`
  blits every member at its rect.
- `key.get_pressed()` answers "held now" (movement); `KEYDOWN`/`KEYUP` events answer "just
  happened" (jump, shoot, pause).
- Normalize diagonal input with `Vector2.normalize()`, guarded by `length_squared() > 0`, or
  diagonals are 1.41× faster.
- Use a hitbox smaller than the sprite (`rect.inflate(-w, -h)`) and pass a `collided` callback;
  reserve `collide_mask` for a few irregular shapes.
- Resolve movement one axis at a time — move X, resolve, move Y, resolve — and substep when a
  frame's movement exceeds half a tile.
- Animate with a time accumulator, not a frame counter, and slice sprite sheets into subsurfaces
  once at load.
- Pool frequently created objects, load sounds once, and keep world-to-screen conversion inside a
  single camera class.

## Practice

- [ ] Write a `Star` sprite and a `Group` of 60 stars that fall at random speeds and are removed
      when they leave the bottom of the screen; print `len(group)` each frame.
- [ ] Give the player 8-direction movement that is exactly 300 px/s in every direction, including
      diagonals, and print `round(vel.length(), 1)` to prove it.
- [ ] Add targets and bullets: use `groupcollide` to destroy both and add to a score, then switch
      to a custom `collided` callback so the player's smaller hitbox decides the hit.
- [ ] Extend `platformer.py` with jump buffering (remember a jump pressed up to 0.12 s before
      landing) and variable jump height (releasing Space early cuts the jump short).
- [ ] Build a side-scrolling level three screens wide: a `Camera` with smooth follow and
      clamping, an animated walk cycle from a generated sprite sheet, and pooled projectiles.

## Solutions

:::solution Exercise 1
```python
import random
import pygame

WIDTH, HEIGHT = 480, 720


class Star(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (220, 226, 240), (3, 3), 3)
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(-HEIGHT, 0))
        )
        self.speed = random.randint(40, 180)

    def update(self, dt, *args):
        self.rect.y += round(self.speed * dt)
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(0, WIDTH)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    stars = pygame.sprite.Group(Star() for _ in range(60))

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        stars.update(dt)
        screen.fill((12, 14, 24))
        stars.draw(screen)
        screen.blit(font.render(f"stars: {len(stars)}", True, (232, 234, 240)), (12, 12))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```
Recycling stars to the top instead of killing them keeps the count constant — the same idea as
object pooling, applied to decoration. `Group(generator)` accepts any iterable of sprites.
:::

:::solution Exercise 2
```python
import pygame

SPEED = 300


def read_move(keys) -> pygame.Vector2:
    move = pygame.Vector2(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
                          keys[pygame.K_DOWN] - keys[pygame.K_UP])
    if move.length_squared() > 0:
        move = move.normalize() * SPEED
    return move


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 26)
    player = pygame.Rect(0, 0, 40, 40)
    player.center = (320, 240)

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        move = read_move(pygame.key.get_pressed())
        player.x += round(move.x * dt)
        player.y += round(move.y * dt)
        player.clamp_ip(screen.get_rect())

        screen.fill((24, 26, 34))
        pygame.draw.rect(screen, (86, 204, 242), player, border_radius=6)
        screen.blit(font.render(f"speed {move.length():6.1f}", True, (232, 234, 240)), (12, 12))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```
`normalize()` guarantees length 1, so the magnitude prints as either `0.0` or exactly `300.0`
in every direction. Without it, diagonals print `300.0 * sqrt(2)` and feel faster.
:::

:::solution Exercise 3
```python
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

player = pygame.sprite.Sprite()
player.image = pygame.Surface((48, 48), pygame.SRCALPHA)
pygame.draw.circle(player.image, (86, 204, 242), (24, 24), 24)
player.rect = player.image.get_rect(center=(320, 400))
player.hitbox = player.rect.inflate(-24, -24)

targets = pygame.sprite.Group()
bullets = pygame.sprite.Group()
for i in range(6):
    t = pygame.sprite.Sprite()
    t.image = pygame.Surface((36, 36), pygame.SRCALPHA)
    pygame.draw.rect(t.image, (244, 114, 182), (0, 0, 36, 36), border_radius=6)
    t.rect = t.image.get_rect(center=(80 + i * 90, 80))
    targets.add(t)

score = 0
running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            b = pygame.sprite.Sprite()
            b.image = pygame.Surface((6, 14), pygame.SRCALPHA)
            pygame.draw.rect(b.image, (255, 236, 150), (0, 0, 6, 14), border_radius=3)
            b.rect = b.image.get_rect(midbottom=player.rect.midtop)
            bullets.add(b)

    keys = pygame.key.get_pressed()
    player.rect.x += round((keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 320 * dt)
    player.hitbox.center = player.rect.center

    for b in bullets:
        b.rect.y -= round(700 * dt)
        if b.rect.bottom < 0:
            b.kill()

    hits = pygame.sprite.groupcollide(bullets, targets, True, True)
    score += sum(len(v) for v in hits.values())

    screen.fill((24, 26, 34))
    targets.draw(screen)
    bullets.draw(screen)
    screen.blit(player.image, player.rect)
    pygame.draw.rect(screen, (255, 80, 80), player.hitbox, width=1)
    screen.blit(font.render(f"score {score}", True, (232, 234, 240)), (12, 12))
    pygame.display.flip()

pygame.quit()
```
`groupcollide` returns a dict, so `sum(len(v) for v in hits.values())` counts every target
destroyed even when one bullet somehow overlaps two. Drawing the hitbox in red for one frame is
the fastest way to confirm your `inflate` numbers are sane.
:::

:::solution Exercise 4
```python
# jump_feel.py — coyote time + jump buffering + variable jump height
import pygame

TILE = 40
LEVEL = [
    "####################",
    "#..................#",
    "#..................#",
    "#..........###.....#",
    "#..................#",
    "#.....####.........#",
    "#..................#",
    "#..............##..#",
    "#..................#",
    "####################",
]
WIDTH, HEIGHT = len(LEVEL[0]) * TILE, len(LEVEL) * TILE
GRAVITY, JUMP, MOVE = 2000, -640, 260
COYOTE, BUFFER, CUT = 0.10, 0.12, 0.45


def build_tiles(level):
    return [pygame.Rect(c * TILE, r * TILE, TILE, TILE)
            for r, line in enumerate(level) for c, ch in enumerate(line) if ch == "#"]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jump feel")
    clock = pygame.time.Clock()
    tiles = build_tiles(LEVEL)

    player = pygame.Rect(0, 0, 28, 36)
    player.midbottom = (2 * TILE, 9 * TILE)
    vel = pygame.Vector2(0, 0)
    coyote = buffer = 0.0
    rising = False

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                buffer = BUFFER                 # remember the intent to jump
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                if rising and vel.y < 0:
                    vel.y *= CUT                # released early -> shorter hop
                rising = False

        keys = pygame.key.get_pressed()
        vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE
        buffer = max(0.0, buffer - dt)
        coyote = max(0.0, coyote - dt)

        if buffer > 0 and coyote > 0:           # buffered press + ground grace
            vel.y = JUMP
            buffer = coyote = 0.0
            rising = True

        vel.y = min(vel.y + GRAVITY * dt, 1200)
        player.y += round(vel.y * dt)
        on_ground = False
        for tile in tiles:
            if player.colliderect(tile):
                if vel.y > 0:
                    player.bottom = tile.top
                    on_ground = True
                elif vel.y < 0:
                    player.top = tile.bottom
                vel.y = 0
                rising = False
        if on_ground:
            coyote = COYOTE

        player.x += round(vel.x * dt)
        for tile in tiles:
            if player.colliderect(tile):
                if vel.x > 0:
                    player.right = tile.left
                elif vel.x < 0:
                    player.left = tile.right

        screen.fill((24, 26, 34))
        for tile in tiles:
            pygame.draw.rect(screen, (60, 66, 86), tile)
        pygame.draw.rect(screen, (110, 214, 148), player, border_radius=5)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```
Jump buffering stores the *intent* to jump for 0.12 s, so a press a few frames before landing
still fires. Jump cutting multiplies upward velocity on release, which turns a tap into a hop and
a hold into a full jump — the biggest "feel" upgrade per line of code in platformers. Both are
three-line additions once coyote time exists.
:::

:::solution Exercise 5
```python
import pygame

WIDTH, HEIGHT = 800, 480
WORLD_W, WORLD_H = WIDTH * 3, HEIGHT
TILE = 40


def make_sheet(colors, frame=32):
    sheet = pygame.Surface((frame * len(colors), frame), pygame.SRCALPHA)
    for i, color in enumerate(colors):
        pygame.draw.circle(sheet, color, (i * frame + frame // 2, frame - 8), 8)
        pygame.draw.rect(sheet, color, (i * frame + 8, frame - 16, 16, 12), border_radius=4)
    return sheet


class Camera:
    def __init__(self, world_w, world_h):
        self.pos = pygame.Vector2(0, 0)
        self.world_w, self.world_h = world_w, world_h

    def update(self, target, dt, smooth=5.0):
        desired = pygame.Vector2(target.rect.centerx - WIDTH / 2, 0)
        self.pos += (desired - self.pos) * min(1.0, smooth * dt)
        self.pos.x = max(0.0, min(self.pos.x, self.world_w - WIDTH))

    def apply(self, rect):
        return rect.move(-round(self.pos.x), -round(self.pos.y))

    def apply_rect(self, entity):
        return self.apply(entity.rect)


class Hero(pygame.sprite.Sprite):
    def __init__(self, frames):
        super().__init__()
        self.frames, self.index, self.time = frames, 0, 0.0
        self.image = frames[0]
        self.rect = self.image.get_rect(midbottom=(120, WORLD_H - TILE))
        self.speed = 260

    def update(self, dt, keys):
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.rect.x += round(dx * self.speed * dt)
        self.rect.x = max(0, min(self.rect.x, WORLD_W - self.rect.width))
        if dx:
            self.time += dt
            while self.time >= 1 / 8:
                self.time -= 1 / 8
                self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    sheet = make_sheet([(110, 214, 148), (134, 226, 168), (158, 238, 190), (134, 226, 168)])
    frames = [sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32)) for i in range(4)]
    hero = Hero(frames)
    all_sprites = pygame.sprite.Group(hero)
    camera = Camera(WORLD_W, WORLD_H)
    ground = pygame.Rect(0, WORLD_H - TILE, WORLD_W, TILE)

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update(dt, pygame.key.get_pressed())
        camera.update(hero, dt)

        screen.fill((24, 26, 34))
        pygame.draw.rect(screen, (60, 66, 86), camera.apply(ground))
        for x in range(0, WORLD_W, TILE):
            pygame.draw.line(screen, (40, 44, 60),
                             (x - round(camera.pos.x), WORLD_H - TILE - round(camera.pos.y)),
                             (x - round(camera.pos.x), WORLD_H - round(camera.pos.y)))
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply_rect(sprite))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```
Generation stands in for real art: `make_sheet` builds a four-frame strip at runtime so the
example runs with no assets. Everything drawn passes through `camera.apply`, which is why the
world can be three screens wide without a single other change.
:::
