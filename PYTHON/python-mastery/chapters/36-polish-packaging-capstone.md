---
chapter: 36
part: 5
title: "Polish, Packaging & CAPSTONE B"
summary: Add juice, UI, saves and performance work to your game, then build the complete Neon Dungeon roguelike: procedural floors, combat, three enemy AIs, two bosses, loot, progression, and a packaged build you can send to a friend.
minutes: 180
tags: [juice, particle systems, HUD, save system, profiling, PyInstaller, capstone, roguelike]
---

A game that works and a game that people finish are two different artefacts. The gap between them
is not more content — it is feedback, clarity, and the confidence that comes from a build that
starts on someone else's machine. This chapter closes the game track in two halves: first the
craft of polish and shipping, taught properly with real code you can drop into any project, then
CAPSTONE B, a complete roguelike specification with seven milestones and the code for the parts
that matter. Work through the first half and retrofit your existing projects; work through the
second and you will have shipped a game.

## Where this track ends

Three screens from Neon Dungeon, the game you build in the second half of this chapter. This is
the target, and the reason the polish work in part one is worth doing.

![The title screen: one selected menu item, a best-run badge, and no clutter.](figures/neon-title.svg)

The play screen is where every system meets: the tilemap and camera from Chapter 34, the enemy
AI from Chapter 35, and the HUD, damage numbers and glow you are about to add.

![Gameplay: health and XP bars, a live minimap, a message log, an item bar, and a damage number frozen mid-hit.](figures/neon-play.svg)

The inventory and level-up screen is almost pure polish — rarity colours, stat bars, a selection
glow. It is also the screen players judge your game on.

![Inventory and level-up: a rarity-coded item grid, the selected item's stats, and a choice of bonuses.](figures/neon-inventory.svg)

## Part one — Polish and shipping

### What polish actually buys you

Polish is not decoration. Every piece of it answers a question the player is asking subconsciously:

- *Did my input register?* — a sound, a flash, a controller rumble.
- *Was that hit mine?* — a damage number, a hitstop, a knockback.
- *Am I in danger?* — a telegraph, a colour shift, a rising audio cue.
- *Am I making progress?* — XP, a filled bar, a number going up.

When players describe a game as "juicy" or "game feel", they are describing the density of those
answers. The good news is that each one is a small, self-contained system. Here they are.

### Screen shake

Shake is the cheapest impact you can buy: offset the camera by a random amount that decays. Two
rules keep it from becoming nauseating — cap the magnitude, and decay exponentially rather than
linearly so it dies fast.

```python
# fx/camera.py
import random

import pygame as pg


class Camera:
    def __init__(self, viewport: tuple[int, int]):
        self.pos = pg.math.Vector2()            # top-left of the view, in world space
        self.offset = pg.math.Vector2()         # shake offset applied on top
        self.viewport = pg.math.Vector2(viewport)
        self.shake = 0.0
        self.bounds: pg.Rect | None = None      # set to the floor size to clamp scrolling

    def add_shake(self, amount: float) -> None:
        self.shake = min(self.shake + amount, 26.0)

    def follow(self, target, dt: float, smoothing: float = 8.0) -> None:
        desired = pg.math.Vector2(target) - self.viewport / 2
        self.pos += (desired - self.pos) * min(1.0, smoothing * dt)
        if self.bounds is not None:
            self.pos.x = max(self.bounds.left,
                             min(self.pos.x, self.bounds.right - self.viewport.x))
            self.pos.y = max(self.bounds.top,
                             min(self.pos.y, self.bounds.bottom - self.viewport.y))

    def update(self, dt: float) -> None:
        if self.shake > 0.05:
            self.shake *= 0.88 ** (dt * 60)     # ~12% decay per frame at 60 fps
            self.offset = pg.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * self.shake
        else:
            self.shake = 0.0
            self.offset.update(0, 0)

    def apply(self, pos) -> pg.math.Vector2:
        """World position -> screen position."""
        return pg.math.Vector2(pos) - self.pos + self.offset

    @property
    def view_rect(self) -> pg.Rect:
        return pg.Rect(self.pos - self.offset, self.viewport)
```

Note the order in `apply`: shake is added *after* the camera translation, so shaking never fights
with the follow logic. Draw the world through `camera.apply`, draw the HUD in raw screen
coordinates afterwards, and the HUD stays rock steady while the world rattles — which is what makes
shake read as "the world moved" rather than "the monitor broke".

:::tip Shake scales with consequence, not with damage
A pistol shot should be 2 units of shake; a boss slam, 14; a death, 22. If a trash enemy hit
shakes as hard as a boss hit, you have destroyed your own difficulty hierarchy.
:::

### Hit flash and squash-and-stretch

A one-frame white silhouette says "that connected" more clearly than any number of particles.
`pg.mask.from_surface` builds the silhouette, but it is expensive, so build it once at load time
and cache it next to the original.

```python
# fx/flash.py
import pygame as pg


def make_flash_variant(image: pg.Surface) -> pg.Surface:
    """All-opaque pixels become white; transparent stay transparent."""
    mask = pg.mask.from_surface(image)
    return mask.to_surface(setcolor=(255, 255, 255, 255),
                           unsetcolor=(0, 0, 0, 0)).convert_alpha()


class FlashMixin:
    flash: float = 0.0

    def tick_flash(self, dt: float) -> None:
        self.flash = max(0.0, self.flash - dt)


def draw_entity(surface, camera, entity, image):
    dest = camera.apply(entity.pos)
    dest.x -= image.get_width() / 2
    dest.y -= image.get_height() / 2
    surface.blit(image, dest)
    if getattr(entity, "flash", 0.0) > 0:
        silhouette = entity.flash_image
        silhouette.set_alpha(int(230 * min(1.0, entity.flash / 0.12)))
        surface.blit(silhouette, dest)
```

**Squash-and-stretch** is the other half of readable impact: scale the sprite non-uniformly for a
few frames after a hit — wide and short on landing, tall and thin on a jump. Do it with a tween on
a `scale` vector, but cache your scaled surfaces: calling `pg.transform.scale` every frame for
every entity is a real cost. Quantising to a handful of steps and caching is the pragmatic
compromise.

```python
def stretch(entity, amount: float = 0.35) -> None:
    entity.scale = pg.math.Vector2(1.0 + amount, 1.0 - amount * 0.8)
    entity.tweens.add(Tween(0.18, ease_out_back,
                            on_update=lambda t: setattr(
                                entity, "scale",
                                pg.math.Vector2(1 + amount * (1 - t), 1 - amount * 0.8 * (1 - t)))))
```

### A particle system

Every puff of dust, spark, and blood drop is a particle: position, velocity, lifetime, and a
draw rule. The naive implementation appends dicts and removes dead ones, which allocates thousands
of objects per second. Use a **fixed pool**: allocate once, recycle slots, never resize.

```python
# fx/particles.py
import random
from dataclasses import dataclass

import pygame as pg


@dataclass
class Particle:
    pos: pg.math.Vector2
    vel: pg.math.Vector2
    life: float
    max_life: float
    size: int
    color: tuple[int, int, int]
    drag: float = 0.94
    gravity: float = 0.0
    shrink: bool = True


class ParticleSystem:
    """Fixed-capacity pool. Emitting past capacity drops the new particle, not the old one."""

    def __init__(self, capacity: int = 2000):
        self.pool = [Particle(pg.math.Vector2(), pg.math.Vector2(), 0.0, 1.0, 1, (255, 255, 255))
                     for _ in range(capacity)]
        self.live = 0

    def emit(self, pos, count: int = 10, speed: tuple[float, float] = (40, 180),
             life: tuple[float, float] = (0.25, 0.7), size: tuple[int, int] = (2, 4),
             color: tuple[int, int, int] = (255, 210, 120),
             spread: tuple[float, float] = (0, 360), gravity: float = 0.0,
             drag: float = 0.94) -> None:
        for _ in range(count):
            if self.live >= len(self.pool):
                return                                   # pool full: drop the request
            p = self.pool[self.live]
            self.live += 1
            angle = random.uniform(*spread)
            p.pos.update(pos)
            p.vel.from_polar((random.uniform(*speed), angle))
            p.max_life = random.uniform(*life)
            p.life = p.max_life
            p.size = random.randint(*size)
            p.color = color
            p.gravity = gravity
            p.drag = drag

    def update(self, dt: float) -> None:
        i = 0
        while i < self.live:
            p = self.pool[i]
            p.life -= dt
            if p.life <= 0:
                self.live -= 1
                self.pool[i], self.pool[self.live] = self.pool[self.live], self.pool[i]
                continue                                 # swapped in a live one: re-test index i
            p.vel.y += p.gravity * dt
            p.vel *= p.drag
            p.pos += p.vel * dt
            i += 1

    def draw(self, surface: pg.Surface, camera) -> None:
        view = camera.view_rect
        for i in range(self.live):
            p = self.pool[i]
            screen = camera.apply(p.pos)
            if not view.collidepoint(screen):            # cull: off-screen particles cost nothing
                continue
            if p.shrink:
                size = max(1, int(p.size * (p.life / p.max_life)))
            else:
                size = p.size
            surface.fill(p.color, (int(screen.x), int(screen.y), size, size))

    def clear(self) -> None:
        self.live = 0
```

The swap-with-last removal in `update` is O(1) and never shifts the list. The `continue` without
incrementing `i` is the part people get wrong — after swapping, slot `i` holds a different
particle that still needs testing.

`p.vel.from_polar((speed, angle))` is a neat pygame trick: set a vector from a magnitude and an
angle in degrees, no trigonometry in your own code.

### Easing and tweening

Linear motion looks mechanical because nothing in the physical world moves linearly. An **easing
function** maps progress `t` in `[0, 1]` to a new value in `[0, 1]` with a curve.

```python
# fx/easing.py
import math


def linear(t: float) -> float:
    return t


def ease_in_quad(t: float) -> float:
    return t * t


def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) * (1 - t)


def ease_in_out_cubic(t: float) -> float:
    return 4 * t ** 3 if t < 0.5 else 1 - ((-2 * t + 2) ** 3) / 2


def ease_out_back(t: float) -> float:
    """Overshoots then settles. Ideal for menus and pickups."""
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_elastic(t: float) -> float:
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1


EASINGS = {
    "linear": linear,
    "in_quad": ease_in_quad,
    "out_quad": ease_out_quad,
    "in_out_cubic": ease_in_out_cubic,
    "out_back": ease_out_back,
    "out_elastic": ease_out_elastic,
}


class Tween:
    """One animated value. Returns True when finished, so the group can drop it."""

    def __init__(self, duration: float, easing="out_quad", on_update=None, on_done=None):
        self.duration = max(0.0001, duration)
        self.easing = EASINGS[easing] if isinstance(easing, str) else easing
        self.elapsed = 0.0
        self.on_update = on_update
        self.on_done = on_done

    def update(self, dt: float) -> bool:
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        if self.on_update is not None:
            self.on_update(self.easing(t))
        if t >= 1.0:
            if self.on_done is not None:
                self.on_done()
            return True
        return False


class TweenGroup:
    def __init__(self):
        self.active: list[Tween] = []

    def add(self, tween: Tween) -> Tween:
        self.active.append(tween)
        return tween

    def update(self, dt: float) -> None:
        for tween in self.active:
            tween.update(dt)
        self.active = [t for t in self.active if t.elapsed < t.duration]

    def clear(self) -> None:
        self.active.clear()
```

Use `out_quad` for movement, `out_back` for UI that should pop, `in_quad` for things falling, and
`out_elastic` sparingly — it is loud.

### Knockback, hitstop, and damage numbers

Three effects that together make a hit feel like a hit. **Knockback** is an impulse added to
velocity. **Hitstop** is a brief freeze of the simulation at the moment of impact — 40 to 80
milliseconds — which is the single highest-value trick in this chapter. **Damage numbers** are
rendered once at spawn and faded out, never re-rendered per frame.

```python
# fx/feedback.py
from dataclasses import dataclass

import pygame as pg


@dataclass
class FloatingText:
    image: pg.Surface
    pos: pg.math.Vector2
    vel: pg.math.Vector2
    life: float
    max_life: float


class FloatingTextLayer:
    def __init__(self, font: pg.font.Font, default_color=(255, 240, 200)):
        self.font = font
        self.default_color = default_color
        self.items: list[FloatingText] = []

    def add(self, text: str, pos, color=None, rise: float = 46.0, life: float = 0.8):
        image = self.font.render(str(text), True, color or self.default_color)
        self.items.append(FloatingText(
            image=image,
            pos=pg.math.Vector2(pos),
            vel=pg.math.Vector2(0, -rise),
            life=life,
            max_life=life,
        ))

    def update(self, dt: float) -> None:
        for item in self.items:
            item.life -= dt
            item.pos += item.vel * dt
            item.vel *= 0.92
        self.items = [i for i in self.items if i.life > 0]

    def draw(self, surface: pg.Surface, camera) -> None:
        for item in self.items:
            alpha = int(255 * min(1.0, item.life / item.max_life * 1.6))
            item.image.set_alpha(alpha)
            screen = camera.apply(item.pos)
            surface.blit(item.image, (screen.x - item.image.get_width() / 2, screen.y))
```

Hitstop lives in the game loop, not in the entity:

```python
class GameScene:
    def update(self, dt: float) -> None:
        if self.hitstop > 0:
            self.hitstop -= dt
            self.fx.update(dt)          # particles and floating numbers keep moving
            return                      # ...but the world is frozen
        self.world.update(dt)
        self.fx.update(dt)
```

Freezing the world while particles keep flying is what sells it. Freeze everything and it reads as
a stutter bug.

### Sound: layering and variation

Sound is half of game feel and the half most often skipped. Three rules:

1. **Limit voices.** Twenty identical gunshots in one frame is a clipping mess. Cooldown per sound
   name.
2. **Vary every repetition.** Same sample at the same volume four times in a row sounds like a
   machine; the ear forgives anything that changes.
3. **Pan by screen position.** Stereo position tells the player where things are.

```python
# core/audio.py
import random
import time

import pygame as pg


class SoundBank:
    def __init__(self, channels: int = 32):
        pg.mixer.set_num_channels(channels)
        self.variants: dict[str, list[pg.mixer.Sound]] = {}
        self.last_played: dict[str, float] = {}
        self.master = 1.0
        self.sfx_volume = 0.8
        self.music_volume = 0.5

    def load(self, name: str, path) -> None:
        self.variants.setdefault(name, []).append(pg.mixer.Sound(str(path)))

    def play(self, name: str, volume: float = 1.0, pan: float = 0.0,
             cooldown: float = 0.04) -> pg.mixer.Channel | None:
        variants = self.variants.get(name)
        if not variants:
            return None
        now = time.monotonic()
        if now - self.last_played.get(name, -1.0) < cooldown:
            return None                                   # voice limit
        self.last_played[name] = now

        sound = random.choice(variants)
        channel = sound.play()
        if channel is None:
            return None
        p = max(-1.0, min(1.0, pan))
        vol = volume * self.sfx_volume * self.master * random.uniform(0.88, 1.0)
        left = vol * (1 - max(0.0, p))
        right = vol * (1 + min(0.0, p))
        channel.set_volume(max(0.0, min(1.0, left)), max(0.0, min(1.0, right)))
        return channel

    def play_music(self, path, loops: int = -1) -> None:
        pg.mixer.music.load(str(path))
        pg.mixer.music.set_volume(self.music_volume * self.master)
        pg.mixer.music.play(loops)
```

The `random.uniform(0.88, 1.0)` on volume is the cheap half of variation. The other half is pitch,
and here is the honest situation: **pygame has no playback-rate control**. You cannot set pitch on
a `Sound`. Your options are to ship several pre-pitched variants of each sample (`hit_01.wav`,
`hit_02.wav`, `hit_03.wav` — record three takes, or pitch-shift one take by ±4% in Audacity and
save it three times), or to resample at load time with `pygame.sndarray` and NumPy. Pre-rendered
variants cost a few kilobytes and zero runtime; that is the right answer for a game like this.

## Interface

### HUD

A HUD is a thin layer drawn in screen space after the world. Keep it dumb: it reads state, it does
not own it.

```python
# ui/hud.py
import pygame as pg


class HUD:
    def __init__(self, font: pg.font.Font, palette: dict):
        self.font = font
        self.palette = palette

    def bar(self, surface, rect, fraction: float, color, bg=(30, 30, 42)) -> None:
        pg.draw.rect(surface, bg, rect, border_radius=3)
        inner = pg.Rect(rect.x + 2, rect.y + 2,
                        max(0, int((rect.width - 4) * max(0.0, min(1.0, fraction)))),
                        rect.height - 4)
        pg.draw.rect(surface, color, inner, border_radius=2)
        pg.draw.rect(surface, self.palette["outline"], rect, 1, border_radius=3)

    def draw(self, surface, player, run) -> None:
        pad = 16
        self.bar(surface, pg.Rect(pad, pad, 220, 18), player.health / player.max_health,
                 self.palette["health"])
        self.bar(surface, pg.Rect(pad, pad + 24, 160, 10), player.xp / player.xp_to_next,
                 self.palette["xp"])
        surface.blit(self.font.render(f"Lv {player.level}", True, self.palette["text"]),
                     (pad + 170, pad + 20))
        self.bar(surface, pg.Rect(pad, pad + 40, 120, 10), player.ammo / player.max_ammo,
                 self.palette["ammo"])

        right = surface.get_width() - pad
        score = self.font.render(f"{run.score:>7}", True, self.palette["text"])
        surface.blit(score, (right - score.get_width(), pad))
        floor = self.font.render(f"Floor {run.floor_index + 1}", True, self.palette["text"])
        surface.blit(floor, (right - floor.get_width(), pad + 22))
        gold = self.font.render(f"{run.gold}g", True, self.palette["gold"])
        surface.blit(gold, (right - gold.get_width(), pad + 44))
```

### Buttons, menus, and modals

A button is four states — idle, hover, pressed, disabled — and the discipline to handle
`MOUSEBUTTONUP` on the button, not `MOUSEBUTTONDOWN`, so a user can slide off to cancel.

```python
# ui/widgets.py
import pygame as pg


class Button:
    def __init__(self, rect, label: str, on_click, font: pg.font.Font, palette: dict,
                 enabled: bool = True, sound=None):
        self.rect = pg.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.font = font
        self.palette = palette
        self.enabled = enabled
        self.sound = sound
        self.hovered = False
        self.pressed = False

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos):     # released *on* the button
                    if self.sound:
                        self.sound()
                    if self.on_click:
                        self.on_click()
                    return True
        return False

    def draw(self, surface: pg.Surface) -> None:
        if not self.enabled:
            face, text = self.palette["disabled"], self.palette["text_dim"]
        elif self.pressed:
            face, text = self.palette["pressed"], self.palette["text"]
        elif self.hovered:
            face, text = self.palette["hover"], self.palette["text"]
        else:
            face, text = self.palette["panel"], self.palette["text_dim"]
        shadow = self.rect.move(0, 4 if not self.pressed else 1)
        pg.draw.rect(surface, self.palette["shadow"], shadow, border_radius=6)
        pg.draw.rect(surface, face, self.rect, border_radius=6)
        pg.draw.rect(surface, self.palette["outline"], self.rect, 2, border_radius=6)
        label = self.font.render(self.label, True, text)
        surface.blit(label, label.get_rect(center=self.rect.center))


class Slider:
    def __init__(self, rect, label: str, value: float, on_change, font: pg.font.Font,
                 palette: dict):
        self.rect = pg.Rect(rect)
        self.label = label
        self.value = max(0.0, min(1.0, value))
        self.on_change = on_change
        self.font = font
        self.palette = palette
        self.dragging = False

    def handle_event(self, event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos)
                return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pg.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos)
            return True
        return False

    def _set_from_mouse(self, pos) -> None:
        self.value = max(0.0, min(1.0, (pos[0] - self.rect.x) / self.rect.width))
        if self.on_change:
            self.on_change(self.value)

    def draw(self, surface: pg.Surface) -> None:
        surface.blit(self.font.render(self.label, True, self.palette["text_dim"]),
                     (self.rect.x, self.rect.y - 20))
        track = pg.Rect(self.rect.x, self.rect.y + self.rect.height // 2 - 3,
                        self.rect.width, 6)
        pg.draw.rect(surface, self.palette["panel"], track, border_radius=3)
        pg.draw.rect(surface, self.palette["accent"],
                     pg.Rect(track.x, track.y, int(track.width * self.value), track.height),
                     border_radius=3)
        knob = (self.rect.x + int(self.rect.width * self.value), self.rect.centery)
        pg.draw.circle(surface, self.palette["text"], knob, 9)
```

A **modal** is a scrim plus a panel plus "consume the events so nothing behind it reacts". That
last part is the whole trick:

```python
class Modal:
    """Returns True from handle_event when it swallowed the event."""

    def __init__(self, size, title: str, body: str, buttons, font, palette):
        self.rect = pg.Rect(0, 0, *size)
        self.title, self.body, self.buttons = title, body, buttons
        self.font, self.palette = font, palette

    def layout(self, screen_rect: pg.Rect) -> None:
        self.rect.center = screen_rect.center
        y = self.rect.bottom - 56
        for button in reversed(self.buttons):
            button.rect.midbottom = (self.rect.centerx, y)
            y -= button.rect.height + 10

    def handle_event(self, event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        # Swallow everything else so the scene underneath never sees it.
        return event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION, pg.KEYDOWN)

    def draw(self, surface: pg.Surface) -> None:
        scrim = pg.Surface(surface.get_size(), pg.SRCALPHA)
        scrim.fill((0, 0, 0, 170))
        surface.blit(scrim, (0, 0))
        pg.draw.rect(surface, self.palette["panel"], self.rect, border_radius=8)
        pg.draw.rect(surface, self.palette["outline"], self.rect, 2, border_radius=8)
        surface.blit(self.font.render(self.title, True, self.palette["accent"]),
                     (self.rect.x + 20, self.rect.y + 18))
        for i, line in enumerate(self.body.splitlines()):
            surface.blit(self.font.render(line, True, self.palette["text_dim"]),
                         (self.rect.x + 20, self.rect.y + 52 + i * 22))
        for button in self.buttons:
            button.draw(surface)
```

### Pause, settings, and remappable keys

The pause menu is a scene pushed onto the stack from Chapter 33, which means the game scene keeps
its state underneath and simply stops updating. Settings need three widgets: a slider for volume,
a toggle for fullscreen, and a key-capture row.

```python
class KeybindRow:
    def __init__(self, action: str, key: int, font: pg.font.Font, rect, palette: dict):
        self.action = action
        self.key = key
        self.font = font
        self.rect = pg.Rect(rect)
        self.palette = palette
        self.capturing = False

    def handle_event(self, event) -> bool:
        if not self.capturing:
            if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1
                    and self.rect.collidepoint(event.pos)):
                self.capturing = True
                return True
            return False
        if event.type == pg.KEYDOWN:
            if event.key != pg.K_ESCAPE:
                self.key = event.key
            self.capturing = False
            return True
        return True                       # while capturing, swallow everything

    def draw(self, surface: pg.Surface) -> None:
        label = pg.key.name(self.key).upper() if not self.capturing else "PRESS A KEY..."
        color = self.palette["accent"] if self.capturing else self.palette["text"]
        surface.blit(self.font.render(self.action, True, self.palette["text_dim"]),
                     (self.rect.x, self.rect.y))
        text = self.font.render(label, True, color)
        surface.blit(text, (self.rect.right - text.get_width(), self.rect.y))
```

Store bindings as a dict of action name to key code in your settings file, and translate every
incoming `KEYDOWN` through a reverse map. Never compare against `pg.K_LEFT` directly in gameplay
code — compare against `bindings["move_left"]`.

```python
DEFAULT_BINDINGS = {
    "up": pg.K_w, "down": pg.K_s, "left": pg.K_a, "right": pg.K_d,
    "dash": pg.K_LSHIFT, "attack": pg.K_SPACE, "interact": pg.K_e,
    "inventory": pg.K_i, "pause": pg.K_ESCAPE,
}


def action_for(bindings: dict[int, str], key: int) -> str | None:
    return bindings.get(key)
```

Build the reverse map once when settings change, not per event.

## Saving the game

### What to persist (and what not to)

Save the *run*, not the *frame*. Persist:

- run identity and seed, floor index, RNG state if you want deterministic continuation
- player stats, equipment, inventory contents (`by key`, never by object)
- meta-progression (unlocks, currency, best score) — this lives outside the run
- settings and keybindings — a separate file, so a corrupt save never costs the player their
  controls
- a `version` integer

Do not persist live surfaces, entity objects, `Vector2`s, or anything that only exists while the
frame is running. JSON handles `dict`, `list`, `str`, `int`, `float`, `bool`, and `None`. Anything
else needs converting at the boundary — that conversion function is the save format.

### Where to put it

Never write next to your `.py` files. On Windows, `Program Files` is read-only for normal users;
on macOS the app bundle is signed and will break; on Linux the install directory may be
root-owned. Ask the OS for the right directory.

```python
# core/paths.py
import os
import sys
from pathlib import Path


def user_data_dir(app_name: str = "neon_dungeon", author: str = "you") -> Path:
    """Per-OS writable data directory. Creates it if needed."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        path = base / app_name
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / app_name
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_config_dir(app_name: str = "neon_dungeon") -> Path:
    return user_data_dir(app_name) / "config"
```

That function is exactly what the third-party `platformdirs` package does, with more edge cases
handled (Flatpak, snap, macOS sandbox containers). If you would rather not own it:

```bash
python3 -m pip install platformdirs
```

```python
from platformdirs import user_data_dir, user_config_dir

data = Path(user_data_dir("neon_dungeon", "yourname"))
config = Path(user_config_dir("neon_dungeon", "yourname"))
```

Either way, one helper called once at startup, and every path in your game flows through it.

### Atomic writes

The failure mode you are preventing: the game writes the save file, the power dies halfway, and the
player loads a truncated JSON file that throws on parse — losing a run they did nothing wrong to
lose. **Write to a temporary file in the same directory, then atomically rename it.** `os.replace`
is atomic on POSIX and on Windows for same-volume renames, so a reader either sees the old file or
the new one, never a half.

```python
# core/savefile.py
import json
import os
import tempfile
from pathlib import Path


def write_json_atomic(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".save-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())       # actually push it to disk
        os.replace(tmp_name, path)          # atomic swap
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
```

Keep one generation of backup as well: before replacing, copy the existing save to `slot1.bak`.
Two files, and you survive a corrupted write that the atomic rename cannot protect you from — the
one where your own serializer emitted garbage.

### Versioning so old saves do not crash

The moment you ship, players have saves in the old shape. Handle it with a version integer and a
chain of migration functions.

```python
# core/save.py
import time
from pathlib import Path

SAVE_VERSION = 3


def migrate_1_to_2(data: dict) -> dict:
    """v2 renamed 'hp' to 'health' and moved gold into the run."""
    player = data.get("player", {})
    if "hp" in player:
        player["health"] = player.pop("hp")
    data.setdefault("run", {}).setdefault("gold", data.pop("gold", 0))
    data["version"] = 2
    return data


def migrate_2_to_3(data: dict) -> dict:
    """v3 added meta-progression and per-slot unlocks."""
    data.setdefault("meta", {"unlocks": [], "currency": 0, "runs": 0})
    data.setdefault("stats", {"kills": 0, "floors": 0, "deaths": 0})
    data["version"] = 3
    return data


MIGRATIONS = {1: migrate_1_to_2, 2: migrate_2_to_3}


def load_game(path: Path) -> dict | None:
    data = read_json(path)
    if data is None:
        return None
    version = int(data.get("version", 1))
    if version > SAVE_VERSION:
        # A newer build wrote this. Do not guess: refuse, and say so.
        raise ValueError(f"Save is from a newer version ({version} > {SAVE_VERSION}).")
    while version < SAVE_VERSION:
        step = MIGRATIONS.get(version)
        if step is None:
            raise ValueError(f"No migration from save version {version}.")
        data = step(data)
        version = int(data["version"])
    return data


def save_game(path: Path, world) -> None:
    write_json_atomic(path, {
        "version": SAVE_VERSION,
        "saved_at": time.time(),
        "run": world.run.to_dict(),
        "player": world.player.to_dict(),
        "inventory": [item.key if item else None for item in world.inventory.slots],
        "floor": {
            "index": world.floor_index,
            "seed": world.seed,
            "explored": world.floor.explored_rows(),
        },
        "meta": world.meta,
        "stats": world.stats,
    })
```

:::scenario Version 2 launches and every existing save crashes on load
You added a `stamina` field, the loader does `player["stamina"]`, and a thousand players with
version 1 saves get a `KeyError` on the title screen. The reviews are brutal and, from the
player's point of view, correct.
:::

:::solution Version the payload, migrate forward, and never trust a field to exist
Three changes, in order of importance:

1. **Bump `SAVE_VERSION` and write migrations.** Every shape change gets one function that turns
   the old dict into the new one, and `load_game` runs them in a chain. Migrations are ten lines
   each and they are permanent — never delete one.
2. **Read with `get` defaults, never `[]`.** `player.get("stamina", 100)` survives a missing field;
   `player["stamina"]` does not. Get in the habit at the load boundary even when a migration
   guarantees the field.
3. **Quarantine rather than crash.** If a save fails to load, do not delete it and do not throw at
   the player. Move it aside and tell them:

```python
def safe_load(path: Path):
    try:
        return load_game(path)
    except Exception as exc:                       # noqa: BLE001 - deliberately broad
        backup = path.with_suffix(path.suffix + ".corrupt")
        try:
            path.replace(backup)
        except OSError:
            pass
        log.warning("Could not load %s (%s); moved to %s", path, exc, backup)
        return None
```

A player who loses a run to a bug stops playing. A player who sees "your save could not be read,
starting a new run" is mildly annoyed and keeps going. Ship the second one.
:::

## Accessibility and feel

Small changes here widen your audience by a lot, and most of them are an afternoon.

**Colourblind-safe palettes.** Roughly 1 in 12 men has some form of colour vision deficiency, most
commonly deuteranopia (red-green). If red and green are the only difference between "enemy" and
"ally", you have made your game unplayable for them. Rules:

1. Never encode meaning in hue alone. Pair every colour with a shape, icon, or pattern.
2. Choose palettes that survive greyscale — check by desaturating a screenshot.
3. Offer a palette switch in settings; it is a dict swap, not a rewrite.

```python
# core/palette.py
PALETTES = {
    "neon": {
        "health": (255, 84, 112), "xp": (86, 204, 242), "ammo": (247, 208, 92),
        "accent": (120, 255, 214), "danger": (255, 92, 92), "gold": (255, 200, 80),
        "panel": (24, 26, 38), "outline": (68, 74, 104), "shadow": (8, 8, 14),
        "text": (236, 240, 255), "text_dim": (150, 158, 190),
        "enemy": (255, 92, 92), "ally": (120, 200, 255),
    },
    # Deuteranopia/protanopia safe: blue vs orange, never red vs green.
    "cvd": {
        "health": (0, 150, 255), "xp": (120, 200, 255), "ammo": (240, 200, 60),
        "accent": (0, 190, 255), "danger": (255, 160, 0), "gold": (255, 215, 0),
        "panel": (24, 26, 38), "outline": (68, 74, 104), "shadow": (8, 8, 14),
        "text": (236, 240, 255), "text_dim": (150, 158, 190),
        "enemy": (255, 160, 0), "ally": (0, 170, 255),
    },
}
```

Note that the "cvd" palette also keeps a **shape-coded** rule in the design: enemies are spiky,
allies are round. Colour is the redundant channel, not the only one.

**Remappable keys** — covered above. Also support arrow keys as a second default, and never require
two-hand combinations for a core action.

**Adjustable difficulty** — reuse the tuning table from Chapter 35, and expose it as three presets
plus a custom screen. Add at least one *assist* option that is not a difficulty level: reduced
screen shake, and a "high contrast" toggle. Both are one-line checks and both are frequently the
difference between someone playing your game and not.

## Performance: find the hot loop first

Guessing is the enemy. `cProfile` tells you where the time actually goes, and it is in the standard
library.

```python
# tools/profile_run.py
import cProfile
import io
import pstats

from main import Game


def main(frames: int = 900) -> None:
    game = Game(headless=True)
    profiler = cProfile.Profile()
    profiler.enable()
    game.run_frames(frames)              # 15 seconds at 60fps, no rendering
    profiler.disable()
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats("cumtime").print_stats(18)
    print(stream.getvalue())


if __name__ == "__main__":
    main()
```

```text
         1843200 function calls in 3.412 seconds

   ncalls  tottime  cumtime  percall filename:lineno(function)
      900    0.041    2.980    0.003 game.py:88(update)
   144000    0.310    1.884    0.000 enemy.py:203(sense)
   144000    0.720    1.120    0.000 grid.py:41(has_line_of_sight)
   900000    0.480    0.480    0.000 {method 'distance_to' of 'pygame.math.Vector2'}
      900    0.120    0.380    0.000 scene.py:51(draw)
```

Read `tottime` before `cumtime`. `tottime` is time *inside* the function itself; `cumtime` includes
its children. Here the story is clear: 900 frames, 160 enemies, each calling `sense` every frame,
and `has_line_of_sight` burning 1.12 seconds of 3.4. The fix is not "optimise line of sight" — it
is "do not call it 144,000 times". Throttle perception to every third frame, stagger it across
enemies, and the number drops by two thirds before you touch a line of code.

Five fixes that cover almost every pygame performance problem:

1. **Cull before you draw.** A sprite off-screen should cost a rectangle test, nothing more.

```python
view = camera.view_rect
for entity in world.entities:
    rect = entity.screen_rect(camera)
    if not view.colliderect(rect):
        continue
    surface.blit(entity.image, rect)
```

2. **Convert your surfaces.** `pg.image.load` gives you a surface in the file's pixel format, and
   every blit then has to convert on the fly. One `convert()` (or `convert_alpha()` for
   transparency) at load time removes that cost forever.

```python
def load_image(path, alpha: bool = True) -> pg.Surface:
    surface = pg.image.load(str(path))
    return surface.convert_alpha() if alpha else surface.convert()
```

3. **Stop allocating per frame.** `Vector2(...)` construction, list comprehensions, and especially
   `font.render` inside a loop are the usual suspects. Render text once and cache the surface;
   damage numbers above already do this. Reuse scratch vectors for intermediate maths.

4. **Dirty-rect rendering.** Instead of `pg.display.flip()` (redraw everything), collect the
   rectangles that changed and pass them to `pg.display.update(rects)`. This is a big win for
   mostly-static scenes — menus, HUD-heavy screens, tile games with a static camera — and a small
   win for a scrolling action game where nearly everything moves anyway.

```python
self.dirty: list[pg.Rect] = []

def draw(self, surface):
    for entity in self.entities:
        old = self.last_rects.get(entity.id)
        new = entity.screen_rect(self.camera)
        if old != new:
            self.dirty.append(old)
            self.dirty.append(new)
            self.last_rects[entity.id] = new
        surface.blit(entity.image, new)
    pg.display.update(self.dirty)
    self.dirty.clear()
```

5. **Cap the work, not the frame rate.** Budgets (as in Chapter 35's `PathfinderService`),
   particle caps, and a hard entity ceiling keep worst-case frames survivable. A game that runs at
   60 fps normally and 45 in a swarm beats one that runs at 60 and 8.

:::pitfall Optimising the wrong loop
The most common profiling mistake is optimising the function with the highest `cumtime` — usually
`update` or `draw`, because everything is under them. Look at `tottime`, find the leaf that is
actually burning CPU, and fix that. The second most common mistake is measuring with the profiler
attached and drawing conclusions about real frame time: `cProfile` adds 2–5x overhead. Use it to
find *where*, then measure *how fast* with `time.perf_counter()` around the specific loop.
:::

## Packaging: shipping a thing people can run

Your game running on your machine proves nothing. Packaging turns a folder of `.py` files and
assets into something a stranger can double-click.

```bash
python3 -m pip install pyinstaller
pyinstaller --onedir --windowed --name "Neon Dungeon" \
    --add-data "assets:assets" \
    --add-data "data:data" \
    main.py
```

```text
...
Building EXE from EXE-00.toc completed successfully.
```

:::warning The `--add-data` separator is platform-specific
macOS and Linux use a colon: `--add-data "assets:assets"`. Windows uses a semicolon:
`--add-data "assets;assets"`. If you build on Windows for Windows, get this wrong and your assets
silently do not ship.
:::

### The spec file

The command line gets unwieldy fast. PyInstaller writes a `.spec` file for you on the first build;
edit it and build from it thereafter, so the build is reproducible and lives in version control.

```python
# build/neon_dungeon.spec
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

datas = [
    ("assets", "assets"),
    ("data", "data"),
]
datas += collect_data_files("neon_dungeon", include_py_files=False)

hiddenimports = collect_submodules("systems") + collect_submodules("entities")

a = Analysis(
    ["main.py"],
    pathex=[".", "src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "PIL"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Neon Dungeon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # False = no terminal window. Set True while debugging.
    icon="assets/icons/app.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="Neon Dungeon",
)
```

```bash
pyinstaller --noconfirm build/neon_dungeon.spec
```

### One-file vs one-directory

| | `--onefile` | `--onedir` |
|---|---|---|
| Output | A single executable | A folder with an executable plus dependencies |
| Startup | Slow: unpacks to a temp directory every launch | Fast: nothing to unpack |
| Updates | Replace one file | Replace the folder |
| Antivirus | False positives are more common | Less suspicious |
| Debugging | Harder — assets live in a temp dir | Easy — everything is visible |
| Recommendation | Demos, jam builds | Anything you will iterate on |

Start with `--onedir`. Ship `--onefile` when you are confident, or when the distribution channel
(zip on itch.io) makes a folder awkward.

### The hidden-imports trap

PyInstaller finds imports by static analysis. Anything it cannot *see* is not bundled. The usual
offenders:

- `importlib.import_module("systems." + name)` — dynamic imports, common in mod/plugin loaders.
- Packages that import C extensions or data files at runtime (`numpy`, `soundfile`, some `pygame`
  extras).
- Namespace packages and anything imported only inside a function that never runs at build time.

Fix it with `hiddenimports=[...]` in the spec, or `collect_submodules("yourpackage")` to sweep a
whole package. When in doubt, add it — an extra module costs kilobytes, and a missing one costs a
crash.

### Asset paths: the crash you will definitely hit

In a frozen build, your files are unpacked to a temporary directory. `Path("assets/player.png")`
resolves relative to the *current working directory*, which is wherever the user double-clicked
from — not your bundle. PyInstaller exposes the unpack location as `sys._MEIPASS`.

```python
# core/resources.py
import sys
from pathlib import Path


def app_root() -> Path:
    """Directory assets live in: works from source and from a frozen bundle."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)          # PyInstaller onefile/onedir temp dir
    return Path(__file__).resolve().parent.parent


def asset_path(*parts: str) -> Path:
    return app_root().joinpath(*parts)


class ResourceManager:
    def __init__(self, root: Path):
        self.root = root
        self._images: dict[str, pg.Surface] = {}
        self._flash: dict[str, pg.Surface] = {}
        self._json: dict[str, dict] = {}
        self._sounds: dict[str, pg.mixer.Sound] = {}
        self._fonts: dict[tuple[str, int], pg.font.Font] = {}

    def image(self, name: str) -> pg.Surface:
        if name not in self._images:
            surface = pg.image.load(self.root / "assets" / "images" / name)
            self._images[name] = surface.convert_alpha()
            self._flash[name] = make_flash_variant(self._images[name])
        return self._images[name]

    def flash_image(self, name: str) -> pg.Surface:
        self.image(name)                   # ensures the variant exists
        return self._flash[name]

    def json(self, name: str) -> dict:
        if name not in self._json:
            import json
            self._json[name] = json.loads((self.root / "data" / name).read_text(encoding="utf-8"))
        return self._json[name]

    def sound(self, name: str) -> pg.mixer.Sound:
        if name not in self._sounds:
            self._sounds[name] = pg.mixer.Sound(self.root / "assets" / "audio" / name)
        return self._sounds[name]

    def font(self, name: str, size: int) -> pg.font.Font:
        key = (name, size)
        if key not in self._fonts:
            self._fonts[key] = pg.font.Font(self.root / "assets" / "fonts" / name, size)
        return self._fonts[key]
```

Note the caching and the `convert_alpha()` in `image()`: no asset is ever loaded twice, and every
surface is converted once at load. That is most of your rendering performance budget, handled in
one place.

:::scenario The packaged exe crashes on launch with "FileNotFoundError: assets/images/player.png"
It runs perfectly from source. The built executable opens, flashes a console window, and dies.
:::

:::solution Every path in your game must go through one resolver that knows about sys._MEIPASS
```python
resources = ResourceManager(app_root())
player_img = resources.image("player.png")
```

Then verify three things:

1. **The assets were bundled at all.** Open the `dist/` output and look. With `--onedir`, assets
   should be a folder next to the exe. If they are missing, your `--add-data` path or separator is
   wrong. On Windows: `--add-data "assets;assets"`.
2. **The separator matches the platform.** Colon on macOS/Linux, semicolon on Windows. This is the
   single most common packaging failure and the error message never mentions it.
3. **You are not using the current working directory anywhere.** Grep for `open(`, `pg.image.load(`
   and `Path(` and confirm every one goes through `resources` or `asset_path`. A relative path
   works in development because your shell happens to be in the project folder; users launch from
   a desktop, a Downloads folder, or a Steam directory.

Debug it properly by temporarily building with `console=True` and `--onedir` so the traceback is
visible, then print `sys.frozen`, `sys._MEIPASS`, and `Path.cwd()` on the first line of `main()`.
Three lines, and the cause is never a mystery.
:::

### Testing the build on a clean machine

A build that works on your machine has been tested against your Python, your PATH, your assets, and
your save directory. None of that exists on a player's machine. Minimum viable test procedure:

1. Build with `--onedir`, `console=True` first. Fix everything you see in the terminal. Then flip
   to `console=False`.
2. Run the executable from a *different* working directory: `cd / && /path/to/dist/Neon\ Dungeon/Neon\ Dungeon`.
   This alone catches every `cwd`-relative path bug.
3. Run it as a different OS user, or in a virtual machine, or on a friend's laptop. A fresh user
   has no `~/Library/Application Support/neon_dungeon`, no settings file, and no save — exactly
   the first-run experience.
4. Delete your save and settings, then launch. Then corrupt one deliberately (truncate the JSON)
   and launch again. It should not crash.
5. Check the antivirus. Windows Defender and many third-party scanners quarantine unsigned
   PyInstaller binaries with some regularity, especially `--onefile`.

### Code signing, honestly

Here is the situation, without marketing. **Windows**: an unsigned executable triggers SmartScreen
("Windows protected your PC"), and the user must click "More info → Run anyway". The warning fades
as your binary builds reputation, but for a first release it is there. Removing it properly means
an OV or EV code-signing certificate, roughly 100 to 400 USD per year, from a commercial CA, plus a
timestamping step in your build. **macOS**: Gatekeeper blocks unsigned apps outright; users can
right-click → Open to bypass it once. Doing it properly means a 99 USD/year Apple Developer
membership, a Developer ID certificate, `codesign` on the bundle, and notarisation via
`notarytool`, which requires a network round trip and takes a few minutes per build. **Linux**:
no signing culture for desktop apps; ship an AppImage, a Flatpak, or a tarball.

For a first game: do not buy a certificate. Ship unsigned, and write one clear sentence in your
itch.io description telling users what the warning is and how to get past it. Sign when the game is
making money or when you are shipping to people who are not your friends.

### Distributing on itch.io

itch.io takes a zip and gives you a page. Two paths:

```bash
# Manual: zip the onedir output, upload on the web dashboard.
cd dist && zip -r "NeonDungeon-macOS.zip" "Neon Dungeon"
```

```bash
# Butler (itch.io's CLI) pushes versioned builds and patches them efficiently.
butler login
butler push dist/NeonDungeon-windows yourname/neon-dungeon:win
butler push dist/NeonDungeon-macOS.zip yourname/neon-dungeon:mac
butler push dist/NeonDungeon-linux yourname/neon-dungeon:linux
butler status yourname/neon-dungeon
```

Butler only uploads the changed blocks between builds, so a 200 MB game with a 5 MB patch uploads
5 MB. Build once per platform, per release, on that platform — cross-compiling PyInstaller builds
does not work.

:::note The web build question
Players will ask for a browser version. Plain Pygame cannot run in a browser, but **pygbag** can
package a `pygame-ce` project to WebAssembly and host it on itch.io with a `web` channel. It
requires `pygame-ce` (the community edition), an `asyncio`-based main loop, and it is a real port,
not a checkbox. Treat it as an extension after 1.0, not part of the first release.
:::

## Part two — CAPSTONE B: Neon Dungeon

Everything in this book so far converges here. Neon Dungeon is a real-time roguelike: procedurally
generated floors, permadeath with meta-progression, three enemy types with the AI from Chapter 35,
two bosses, loot and an inventory, a shop between floors, XP and level-ups, a minimap, save-on-quit,
and a scoreboard. It is a big project. It is also, now, a straightforward one — every piece is
something you have already built once.

### The spec

Write the spec down before you write code, and keep it to one page. Constraints are what make a
project finishable.

| | |
|---|---|
| Genre | Real-time top-down roguelike, twin-stick-ish |
| Run length | 10 floors, ~15–25 minutes |
| Death | Permadeath for the run; gold and unlocks persist |
| Floors | Procedural, 5–14 rooms, one shop room boss room every 5th floor |
| Enemies | Drone (patrol/ranged), Brute (slow/tanky/melee), Stalker (ambush/flees when hurt) |
| Bosses | The Warden (floor 5), The Neural Mass (floor 10) |
| Progression | XP, 10 levels, +stats per level; loot modifies damage, speed, crit |
| Economy | Gold from kills; shop between floors sells 3 offers |
| Interface | HUD, pause menu, inventory, minimap, settings, death screen |
| Persistence | Save-on-quit (one slot), meta-progression file, scoreboard |
| Target | 60 fps with 40 entities on a 1280x720 window |

Cut list — decide now what you are *not* building: no multiplayer, no controller support, no
controller rumble, no modding API, no story, no dialogue trees. Those are in the extensions
section, and they are all after 1.0.

### Data model: entities and components

A deep class hierarchy (`Enemy` → `FlyingEnemy` → `RangedFlyingEnemy`) dies the first time you
want a flying melee enemy. Use **composition**: an `Entity` is an id plus a bag of components;
**systems** are functions that operate on entities having certain components.

```python
# entities/entity.py
import itertools
from dataclasses import dataclass, field

import pygame as pg


@dataclass
class Transform:
    pos: pg.math.Vector2
    vel: pg.math.Vector2 = field(default_factory=lambda: pg.math.Vector2())
    facing: pg.math.Vector2 = field(default_factory=lambda: pg.math.Vector2(1, 0))
    radius: float = 10.0


@dataclass
class Health:
    current: int
    maximum: int
    iframes: float = 0.0
    flash: float = 0.0


@dataclass
class Sprite:
    image_name: str
    layer: int = 0


@dataclass
class Brain:
    kind: str                       # "drone" | "brute" | "stalker" | "boss"
    machine: object = None          # StateMachine from Chapter 35
    behaviour: str = "patrol"


@dataclass
class Loot:
    table: str
    gold: tuple[int, int] = (1, 6)


@dataclass
class Inventory:
    slots: list                     # list[Item | None]
    gold: int = 0


class Entity:
    _ids = itertools.count(1)

    def __init__(self, kind: str, pos, *components):
        self.id = next(Entity._ids)
        self.kind = kind
        self.alive = True
        self.components: dict[type, object] = {}
        self.add(Transform(pg.math.Vector2(pos)))
        for component in components:
            self.add(component)

    def add(self, component):
        self.components[type(component)] = component
        return self

    def get(self, cls):
        return self.components.get(cls)

    def has(self, cls) -> bool:
        return cls in self.components

    def remove(self, cls) -> None:
        self.components.pop(cls, None)
```

Systems read like plain functions, and that is the point — no framework, no registration ceremony:

```python
# systems/movement.py
def movement_system(world, dt: float) -> None:
    for entity in world.entities:
        tf = entity.get(Transform)
        if tf is None:
            continue
        tf.pos = world.move_with_collision(entity, tf.pos + tf.vel * dt)
        tf.vel *= 0.86                              # friction; tune per entity later


def health_system(world, dt: float) -> None:
    for entity in world.entities:
        hp = entity.get(Health)
        if hp is None:
            continue
        hp.iframes = max(0.0, hp.iframes - dt)
        hp.flash = max(0.0, hp.flash - dt)
        if hp.current <= 0 and entity.alive:
            world.kill(entity)
```

Content lives in JSON so you can tune without touching Python — this is the payoff for the file
handling in Chapter 13 and the resource manager you just wrote.

```json
{
  "version": 1,
  "enemies": {
    "drone": {
      "sprite": "drone.png",
      "behaviour": "patrol",
      "stats": {
        "max_health": 24, "speed": 95, "sight_range": 260, "fov": 120,
        "hearing": 150, "memory": 3.0, "attack_range": 210, "attack_damage": 7,
        "attack_windup": 0.45, "attack_recover": 0.5, "attack_cooldown": 1.4,
        "flee_below": 0, "reaction": 0.28, "accuracy_deg": 6.0
      },
      "xp": 8, "loot": "common"
    },
    "brute": {
      "sprite": "brute.png",
      "behaviour": "patrol",
      "stats": {
        "max_health": 90, "speed": 58, "sight_range": 200, "fov": 90,
        "hearing": 220, "memory": 5.0, "attack_range": 52, "attack_damage": 18,
        "attack_windup": 0.7, "attack_recover": 0.8, "attack_cooldown": 1.8,
        "flee_below": 0, "reaction": 0.35, "accuracy_deg": 0.0
      },
      "xp": 22, "loot": "uncommon"
    },
    "stalker": {
      "sprite": "stalker.png",
      "behaviour": "ambush",
      "stats": {
        "max_health": 34, "speed": 150, "sight_range": 320, "fov": 200,
        "hearing": 260, "memory": 6.0, "attack_range": 40, "attack_damage": 14,
        "attack_windup": 0.25, "attack_recover": 0.35, "attack_cooldown": 1.0,
        "flee_below": 12, "reaction": 0.12, "accuracy_deg": 2.0
      },
      "xp": 18, "loot": "uncommon"
    },
    "warden": {
      "sprite": "warden.png",
      "behaviour": "boss",
      "boss": "warden",
      "stats": {
        "max_health": 600, "speed": 70, "sight_range": 900, "fov": 360,
        "hearing": 900, "memory": 20.0, "attack_range": 70, "attack_damage": 22,
        "attack_windup": 0.8, "attack_recover": 0.9, "attack_cooldown": 2.0,
        "flee_below": 0, "reaction": 0.1, "accuracy_deg": 0.0
      },
      "xp": 250, "loot": "boss"
    },
    "neural_mass": {
      "sprite": "neural.png",
      "behaviour": "boss",
      "boss": "neural_mass",
      "stats": {
        "max_health": 1400, "speed": 84, "sight_range": 900, "fov": 360,
        "hearing": 900, "memory": 20.0, "attack_range": 80, "attack_damage": 26,
        "attack_windup": 0.7, "attack_recover": 0.7, "attack_cooldown": 1.6,
        "flee_below": 0, "reaction": 0.08, "accuracy_deg": 0.0
      },
      "xp": 900, "loot": "boss"
    }
  }
}
```

```json
{
  "version": 1,
  "items": {
    "pulse_cell": {
      "name": "Pulse Cell", "slot": "core", "rarity": 1,
      "mods": {"damage": 3.0}, "flavour": "Overcharges the emitter."
    },
    "phase_boots": {
      "name": "Phase Boots", "slot": "boots", "rarity": 2,
      "mods": {"speed": 28.0, "dash_cooldown": -0.2},
      "flavour": "You arrive a moment before you leave."
    },
    "prism_shard": {
      "name": "Prism Shard", "slot": "core", "rarity": 3,
      "mods": {"crit_chance": 0.15, "damage": 2.0},
      "flavour": "Splits light. Splits enemies."
    },
    "vital_mesh": {
      "name": "Vital Mesh", "slot": "body", "rarity": 2,
      "mods": {"max_health": 25}, "flavour": "Knits itself back together. Slowly."
    },
    "targeting_lens": {
      "name": "Targeting Lens", "slot": "core", "rarity": 2,
      "mods": {"accuracy_deg": -3.0, "range": 40.0}, "flavour": "The world narrows."
    }
  },
  "loot_tables": {
    "common": {
      "drop_chance": 0.35,
      "entries": [
        {"item": "pulse_cell", "weight": 10, "rarity": 1},
        {"item": "targeting_lens", "weight": 4, "rarity": 2}
      ]
    },
    "uncommon": {
      "drop_chance": 0.6,
      "entries": [
        {"item": "phase_boots", "weight": 6, "rarity": 2},
        {"item": "vital_mesh", "weight": 6, "rarity": 2},
        {"item": "prism_shard", "weight": 2, "rarity": 3}
      ]
    },
    "boss": {
      "drop_chance": 1.0,
      "entries": [
        {"item": "prism_shard", "weight": 5, "rarity": 3},
        {"item": "vital_mesh", "weight": 5, "rarity": 2},
        {"item": "phase_boots", "weight": 5, "rarity": 2}
      ]
    }
  }
}
```

Those two files define every enemy and every item in the game. Adding a fourth enemy type is now
a JSON edit plus one sprite.

### Project layout

```text
neon_dungeon/
├── main.py                     # entry point: build the App, run the loop
├── core/
│   ├── __init__.py
│   ├── app.py                  # window, clock, scene stack, fixed-step updates
│   ├── config.py               # constants: TILE_SIZE, FPS, window size
│   ├── events.py               # custom event types (ON_KILL, ON_LEVEL_UP, ...)
│   ├── paths.py                # app_root, asset_path, user_data_dir
│   ├── resources.py            # ResourceManager: images, sounds, fonts, json
│   ├── audio.py                # SoundBank
│   ├── palette.py              # colour palettes, incl. colourblind-safe
│   ├── save.py                 # versioned save/load + migrations
│   ├── savefile.py             # atomic read/write
│   └── settings.py             # keybindings, volume, difficulty (separate file)
├── world/
│   ├── dungeon.py              # Floor, Room, generate_floor
│   ├── grid.py                 # Grid: is_walkable, has_line_of_sight
│   └── minimap.py
├── entities/
│   ├── entity.py               # Entity + components
│   ├── player.py
│   ├── enemy.py                # Enemy: Chapter 35 FSM host
│   └── boss.py                 # phase/telegraph controller
├── systems/
│   ├── movement.py
│   ├── combat.py               # apply_damage, i-frames, knockback
│   ├── ai.py                   # PathfinderService, perception polling
│   ├── loot.py
│   ├── progression.py
│   └── spatial.py              # SpatialHash
├── fx/
│   ├── camera.py
│   ├── particles.py
│   ├── easing.py
│   ├── feedback.py             # floating text, hitstop helper
│   └── flash.py
├── ui/
│   ├── hud.py
│   ├── widgets.py              # Button, Slider, KeybindRow
│   ├── menus.py                # title, pause, settings, death, shop
│   └── modal.py
├── scenes/
│   ├── game.py
│   ├── shop.py
│   ├── menu.py
│   └── scoreboard.py
├── data/
│   ├── enemies.json
│   ├── items.json
│   └── tuning.json
├── assets/
│   ├── images/
│   ├── audio/
│   └── fonts/
├── saves/                      # dev only; real saves go to user_data_dir
├── tests/
│   ├── test_dungeon.py
│   ├── test_combat.py
│   └── test_progression.py
├── tools/
│   └── profile_run.py
├── build/
│   └── neon_dungeon.spec
├── requirements.txt
└── README.md
```

`requirements.txt` should be short and pinned:

```text
pygame-ce==2.5.2
platformdirs==4.3.6
```

### Milestone 1 — Floor generation

Reuse the generator from Chapter 34, now with rooms, doors, and a boss room. The algorithm:
scatter non-overlapping rectangles, carve them, connect their centres with L-shaped corridors,
then decorate corridor mouths with doors.

```python
# world/dungeon.py
import random
from dataclasses import dataclass, field

WALL, FLOOR, DOOR, STAIRS = 0, 1, 2, 3
WALKABLE = {FLOOR, DOOR, STAIRS}
BLOCKS_SIGHT = {WALL, DOOR}


@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int
    kind: str = "normal"                  # normal | start | shop | boss

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other: "Room", pad: int = 1) -> bool:
        return not (self.x - pad > other.x + other.w
                    or self.x + self.w + pad < other.x
                    or self.y - pad > other.y + other.h
                    or self.y + self.h + pad < other.y)

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h


@dataclass
class Floor:
    width: int
    height: int
    tiles: list[list[int]]
    rooms: list[Room] = field(default_factory=list)
    doors: set[tuple[int, int]] = field(default_factory=set)
    spawn: tuple[int, int] = (1, 1)
    stairs: tuple[int, int] = (1, 1)
    spawns: list[tuple[int, int]] = field(default_factory=list)
    explored: set = field(default_factory=set)

    def is_walkable(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and self.tiles[y][x] in WALKABLE

    def blocks_sight(self, x: int, y: int) -> bool:
        return not (0 <= x < self.width and 0 <= y < self.height) or self.tiles[y][x] in BLOCKS_SIGHT


def generate_floor(index: int, rng: random.Random,
                   width: int = 72, height: int = 54) -> Floor:
    floor = Floor(width, height, [[WALL] * width for _ in range(height)])
    budget = min(14, 6 + index // 2)
    attempts = 0

    while len(floor.rooms) < budget and attempts < 500:
        attempts += 1
        w = rng.randint(6, 12)
        h = rng.randint(5, 9)
        x = rng.randint(1, width - w - 2)
        y = rng.randint(1, height - h - 2)
        candidate = Room(x, y, w, h)
        if any(candidate.intersects(r, pad=2) for r in floor.rooms):
            continue
        floor.rooms.append(candidate)

    for room in floor.rooms:
        _carve_room(floor, room)

    # Connect rooms nearest-first: avoids the long diagonal spider web you get
    # by linking them in placement order.
    chain = _nearest_chain(floor.rooms)
    for a, b in zip(chain, chain[1:]):
        _carve_corridor(floor, a.center, b.center, rng)

    for room in floor.rooms:
        _place_doors(floor, room, rng, chance=0.3)

    start = chain[0]
    start.kind = "start"
    floor.spawn = start.center
    floor.spawns = [r.center for r in floor.rooms if r is not start]

    if index % 5 == 4:                                   # floors 5 and 10
        boss = _add_boss_room(floor, rng, chain)
        floor.spawns = [c for c in floor.spawns if not boss.contains(*c)]
    else:
        floor.stairs = max((r for r in floor.rooms if r is not start),
                           key=lambda r: _manhattan(r.center, floor.spawn)).center
        shop = rng.choice([r for r in floor.rooms if r not in (start,)])
        shop.kind = "shop"
        floor.tiles[floor.stairs[1]][floor.stairs[0]] = STAIRS

    return floor


def _carve_room(floor: Floor, room: Room) -> None:
    for y in range(room.y, room.y + room.h):
        for x in range(room.x, room.x + room.w):
            floor.tiles[y][x] = FLOOR


def _carve_h(floor: Floor, x0: int, x1: int, y: int) -> None:
    for x in range(min(x0, x1), max(x0, x1) + 1):
        if 0 < x < floor.width - 1 and floor.tiles[y][x] == WALL:
            floor.tiles[y][x] = FLOOR


def _carve_v(floor: Floor, y0: int, y1: int, x: int) -> None:
    for y in range(min(y0, y1), max(y0, y1) + 1):
        if 0 < y < floor.height - 1 and floor.tiles[y][x] == WALL:
            floor.tiles[y][x] = FLOOR


def _carve_corridor(floor: Floor, a, b, rng: random.Random) -> None:
    x1, y1 = a
    x2, y2 = b
    if rng.random() < 0.5:
        _carve_h(floor, x1, x2, y1)
        _carve_v(floor, y1, y2, x2)
    else:
        _carve_v(floor, y1, y2, x1)
        _carve_h(floor, x1, x2, y2)


def _place_doors(floor: Floor, room: Room, rng: random.Random, chance: float) -> None:
    """Doors sit on the ring just outside a room, where a corridor meets it."""
    ring: list[tuple[int, int]] = []
    for x in range(room.x - 1, room.x + room.w + 1):
        ring += [(x, room.y - 1), (x, room.y + room.h)]
    for y in range(room.y - 1, room.y + room.h + 1):
        ring += [(room.x - 1, y), (room.x + room.w, y)]
    for x, y in ring:
        if not (0 <= x < floor.width and 0 <= y < floor.height):
            continue
        if floor.tiles[y][x] == FLOOR and rng.random() < chance:
            floor.tiles[y][x] = DOOR
            floor.doors.add((x, y))


def _nearest_chain(rooms: list[Room]) -> list[Room]:
    remaining = list(rooms)
    chain = [remaining.pop(0)]
    while remaining:
        last = chain[-1]
        nxt = min(remaining, key=lambda r: _manhattan(r.center, last.center))
        remaining.remove(nxt)
        chain.append(nxt)
    return chain


def _manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _add_boss_room(floor: Floor, rng: random.Random, chain: list[Room]) -> Room:
    """A big room carved last, joined to the map by a single corridor."""
    anchor = chain[-1]
    for _ in range(200):
        w, h = 18, 14
        x = rng.randint(1, floor.width - w - 2)
        y = rng.randint(1, floor.height - h - 2)
        candidate = Room(x, y, w, h, kind="boss")
        if any(candidate.intersects(r, pad=3) for r in floor.rooms):
            continue
        floor.rooms.append(candidate)
        _carve_room(floor, candidate)
        _carve_corridor(floor, anchor.center, candidate.center, rng)
        floor.stairs = candidate.center
        return candidate
    fallback = chain[-1]
    fallback.kind = "boss"
    floor.stairs = fallback.center
    return fallback
```

Two things make generated floors feel designed rather than random: connecting rooms
nearest-first (which prevents corridors criss-crossing the whole map), and giving the last room a
distinct job (stairs, shop, or boss).

Always seed it:

```python
rng = random.Random(seed)
floor = generate_floor(index, rng)
```

Same seed, same floor, every time — which means a bug report with a seed is reproducible, and
"daily run" is a two-line feature.

### Milestone 2 — Movement, camera, and collision

Straight out of Chapters 32 and 33: input to velocity, velocity to position, position through
collision, camera follows the player. One addition — the dash, because it is the movement verb that
makes combat readable.

```python
# entities/player.py
import pygame as pg

from entities.entity import Entity, Health, Sprite, Transform


class Player(Entity):
    dash_speed = 900.0
    dash_time = 0.14
    dash_cooldown = 0.9

    def __init__(self, pos, bindings: dict[str, int]):
        super().__init__("player", pos, Health(100, 100), Sprite("player.png"))
        self.bindings = bindings
        self.keys_down: set[int] = set()
        self.dash_timer = 0.0
        self.dash_left = 0.0
        self.facing = pg.math.Vector2(1, 0)
        self.mods = {"damage": 0.0, "speed": 0.0, "crit_chance": 0.0, "accuracy_deg": 0.0}

    def handle_event(self, event) -> None:
        if event.type == pg.KEYDOWN and event.key in self.bindings.values():
            if event.key == self.bindings["dash"]:
                self.try_dash()
        # track held keys in the scene's key state, not per-event, for smooth movement

    def try_dash(self) -> None:
        if self.dash_timer > 0 or self.dash_left > 0:
            return
        tf = self.get(Transform)
        self.dash_left = self.dash_time
        self.dash_timer = self.dash_cooldown
        self.get(Health).iframes = max(self.get(Health).iframes, self.dash_time + 0.05)
        tf.vel = self.facing * self.dash_speed

    def update(self, dt: float, keys: set[int]) -> None:
        b = self.bindings
        tf = self.get(Transform)
        self.dash_timer = max(0.0, self.dash_timer - dt)

        if self.dash_left > 0:
            self.dash_left -= dt
            return                                     # dashing overrides steering

        move = pg.math.Vector2(
            (b["right"] in keys) - (b["left"] in keys),
            (b["down"] in keys) - (b["up"] in keys),
        )
        if move.length_squared() > 0:
            self.facing = move.normalize()
        speed = 230.0 + self.mods["speed"]
        desired = move.normalize() * speed if move.length_squared() else pg.math.Vector2()
        tf.vel += (desired - tf.vel) * min(1.0, 14.0 * dt)     # acceleration, not teleport
```

Note the dash grants i-frames. That single line turns the dash from a movement tool into a
defensive one, and it is why the combat below feels like a dance instead of a stat check.

### Milestone 3 — Combat

One function owns all damage. Every rule — i-frames, knockback, flash, hitstop, death — lives in
one place, so balance changes are one edit.

```python
# systems/combat.py
import pygame as pg

from entities.entity import Health, Transform


def apply_damage(world, target, amount: int, source_pos=None,
                 knockback: float = 220.0, iframes: float = 0.6,
                 can_crit: bool = True) -> int:
    """The single entry point for damage. Returns the amount actually dealt."""
    hp: Health | None = target.get(Health)
    if hp is None or not target.alive or hp.iframes > 0:
        return 0

    dealt = max(1, int(amount))
    if can_crit and world.rng.random() < world.player.mods.get("crit_chance", 0.0):
        dealt = int(dealt * 1.8)
        world.audio.play("crit", volume=0.9)

    hp.current -= dealt
    hp.iframes = iframes
    hp.flash = 0.12
    tf: Transform = target.get(Transform)

    if source_pos is not None:
        push = tf.pos - pg.math.Vector2(source_pos)
        if push.length_squared() < 1:
            push = pg.math.Vector2(1, 0)
        tf.vel += push.normalize() * knockback

    world.fx.text.add(str(dealt), tf.pos,
                      color=(255, 120, 120) if target.kind == "player" else (255, 240, 200))
    world.fx.particles.emit(tf.pos, count=10, speed=(60, 260),
                            color=(255, 190, 90), life=(0.2, 0.5))
    world.camera.add_shake(min(10.0, 2.0 + dealt * 0.3))
    world.hitstop = max(world.hitstop, 0.05)
    world.audio.play("hit", volume=0.75,
                     pan=(tf.pos.x - world.camera.pos.x) / world.camera.viewport.x * 2 - 1)

    if hp.current <= 0:
        world.kill(target)
    return dealt


def strike(world, attacker, target, damage: int, spread_deg: float = 0.0) -> int:
    """Melee/ranged attack: applies accuracy spread, then damage."""
    tf = attacker.get(Transform)
    if spread_deg and world.rng.uniform(-spread_deg, spread_deg) > spread_deg * 0.7:
        return 0                                        # a clean miss: no damage, no i-frames
    return apply_damage(world, target, damage, source_pos=tf.pos)
```

The i-frame check at the top is what prevents stun-lock: for `iframes` seconds after a hit, nothing
can damage this entity again. This is the mechanic that makes being surrounded survivable, and it
is one `if`.

:::scenario Playtesters say the game feels unfair
The feedback is consistent: "I died and I don't know why", "the brute hits me from off-screen",
"sometimes I lose half my health instantly". The numbers are fine — time-to-kill and damage-per-hit
are both reasonable.
:::

:::solution Unfairness is almost always a readability problem, not a balance problem
Work through these four fixes in order; usually the first two solve it.

1. **Telegraph everything that costs health.** Every enemy attack gets a visible wind-up of at
   least 0.25 s (the `attack_windup` field), with a distinct animation *and* a distinct sound that
   starts at the beginning of the wind-up. Draw the danger area during the wind-up so the shape of
   the threat is legible:

```python
def draw_telegraph(surface, camera, shape, telegraph_left: float, total: float) -> None:
    progress = 1.0 - (telegraph_left / total)          # 0 -> 1 as the attack approaches
    alpha = int(60 + 160 * progress)
    outline = pg.Surface(surface.get_size(), pg.SRCALPHA)
    pg.draw.circle(outline, (255, 90, 90, alpha),
                   (int(camera.apply(shape.center).x), int(camera.apply(shape.center).y)),
                   int(shape.radius), max(2, int(4 * progress)))
    surface.blit(outline, (0, 0))
```

2. **Guarantee i-frames and check them everywhere.** 0.6 s for the player. Confirm that *nothing*
   bypasses `apply_damage` — no direct `hp.current -= x` anywhere in the codebase. Grep for it.
3. **Explain the death.** On the death screen, show the last three damage events with source and
   amount. Players forgive a fair death they understand; they quit over an unexplained one.
4. **Cap incoming damage per second, not per hit.** If three enemies can hit in the same frame,
   the player loses three times the health in one unreactable instant. Let the i-frame window do
   this for you, and additionally suppress spawns so that no more than two enemies can be within
   melee range at once (an **attack token** system: enemies must acquire a token before entering
   their attack state, and there are two tokens).

The last one is the real lesson: fairness is an information problem. Give the player the signal
early enough to act on it, and let them be wrong, and they will call the game hard rather than
unfair.
:::

### Milestone 4 — Three enemy types

The `Enemy` from Chapter 35 becomes the host for data-driven variants. The FSM is shared; the
stats and one behaviour flag differ.

```python
# entities/enemy.py
import pygame as pg

from ai.fsm import StateMachine
from ai.perception import Perception
from entities.entity import Brain, Entity, Health, Loot, Sprite, Transform
from steering import Agent
from systems.combat import EnemyStats


class Enemy(Entity, Agent):
    def __init__(self, kind: str, pos, spec: dict, waypoints=()):
        stats = EnemyStats(**spec["stats"])
        Entity.__init__(self, kind, pos, Health(stats.max_health, stats.max_health),
                        Sprite(spec["sprite"]), Brain(kind, behaviour=spec["behaviour"]),
                        Loot(spec.get("loot", "common")))
        Agent.__init__(self, pos, max_speed=stats.speed, radius=11.0)
        self.spec = spec
        self.stats = stats
        self.perception = Perception(sight_range=stats.sight_range, fov=stats.fov,
                                     hearing=stats.hearing, memory=stats.memory)
        self.waypoints = list(waypoints)
        self.waypoint_index = 0
        self.path: list = []
        self.destination = pg.math.Vector2(pos)
        self.goal_cell = None
        self.repath_timer = 0.0
        self.alert = 0.0
        self.last_known = None
        self.reaction_left = 0.0
        self.cooldown = 0.0
        self.wait = 0.0
        self.remove = False
        self.machine = StateMachine(self, {
            "patrol": Patrol(), "chase": Chase(), "attack": Attack(),
            "flee": Flee(), "dead": Dead(),
        }, "patrol")

    # Patrol/Chase/Attack/Flee/Dead are the classes from Chapter 35, unchanged.
    def update(self, dt: float, world) -> None:
        tf = self.get(Transform)
        tf.pos.update(self.pos)
        tf.vel.update(self.vel)
        self.cooldown = max(0.0, self.cooldown - dt)
        self.reaction_left = max(0.0, self.reaction_left - dt)
        if self.machine.state.name != "dead" and self.get(Health).current <= 0:
            self.machine.change("dead")
        self.machine.update(dt, world)
```

Wire the pathfinding service into the world so repathing is budgeted, and give each enemy a
behaviour twist on top of the shared states:

```python
# systems/ai.py
from systems.spatial import SpatialHash


class AIDirector:
    """Owns perception polling, path requests, and the attack-token economy."""

    def __init__(self, grid, pathfinder, attack_tokens: int = 2):
        self.grid = grid
        self.pathfinder = pathfinder
        self.hash = SpatialHash(cell_size=64)
        self.attack_tokens = attack_tokens
        self.token_holders: set[int] = set()

    def update(self, world, dt: float) -> None:
        enemies = [e for e in world.entities if e.has(Brain)]
        self.hash.rebuild(enemies)                 # one rebuild per frame

        for enemy in enemies:
            enemy.neighbours = list(self.hash.query(enemy.pos, 48))
            if enemy.machine.state.name == "chase":
                if enemy.id in self.token_holders or len(self.token_holders) < self.attack_tokens:
                    self.token_holders.add(enemy.id)      # reserve before reaching Attack
            else:
                self.token_holders.discard(enemy.id)
            enemy.update(dt, world)

        self.pathfinder.update(dt)
```

The `attack_tokens` set is the fix for the "surrounded and shredded" complaint: at most two
enemies may be in the attack pipeline at once. The rest circle, which looks like tactics.

### Milestone 5 — Loot, inventory, shop, and progression

```python
# systems/loot.py
import random


def roll_loot(tables: dict, table_name: str, rng: random.Random,
              luck: float = 0.0, rolls: int = 1) -> list[str]:
    table = tables.get(table_name)
    if table is None:
        return []
    if rng.random() > table.get("drop_chance", 1.0):
        return []
    entries = table["entries"]
    weights = [e["weight"] * (1.0 + luck * 0.1 * e["rarity"]) for e in entries]
    return [rng.choices(entries, weights=weights, k=1)[0]["item"] for _ in range(rolls)]


def make_item(key: str, items: dict):
    spec = items[key]
    return type("Item", (), {})() if False else Item(key, spec)     # see below
```

That last line is silly. Simplify — write the item class properly:

```python
# systems/loot.py (continued)
from dataclasses import dataclass, field


@dataclass
class Item:
    key: str
    name: str
    slot: str
    rarity: int
    mods: dict[str, float] = field(default_factory=dict)
    flavour: str = ""

    @classmethod
    def from_spec(cls, key: str, spec: dict) -> "Item":
        return cls(key=key, name=spec["name"], slot=spec["slot"],
                   rarity=spec["rarity"], mods=dict(spec.get("mods", {})),
                   flavour=spec.get("flavour", ""))


class Inventory:
    def __init__(self, size: int = 6, gold: int = 0):
        self.slots: list[Item | None] = [None] * size
        self.gold = gold

    def add(self, item: Item) -> bool:
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item
                return True
        return False                                  # full: the shop or the floor gets it

    def remove(self, index: int) -> Item | None:
        item = self.slots[index]
        self.slots[index] = None
        return item

    def total_mods(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        for item in self.slots:
            if item is None:
                continue
            for key, value in item.mods.items():
                totals[key] = totals.get(key, 0.0) + value
        return totals

    def to_dict(self) -> dict:
        return {"slots": [i.key if i else None for i in self.slots], "gold": self.gold}

    @classmethod
    def from_dict(cls, data: dict, items: dict) -> "Inventory":
        inv = cls(len(data["slots"]), data.get("gold", 0))
        inv.slots = [Item.from_spec(k, items[k]) if k else None for k in data["slots"]]
        return inv
```

```python
# systems/progression.py
def xp_for_level(level: int) -> int:
    """Super-linear, so later levels take longer but never stop being reachable."""
    return int(80 * level ** 1.5)


LEVEL_GAINS = {"max_health": 8, "damage": 2.0, "speed": 3.0}


def grant_xp(player, amount: int, on_level=None) -> int:
    player.xp += amount
    levels = 0
    while player.xp >= xp_for_level(player.level):
        player.xp -= xp_for_level(player.level)
        player.level += 1
        levels += 1
        hp = player.get(Health)
        hp.maximum += LEVEL_GAINS["max_health"]
        hp.current = min(hp.maximum, hp.current + LEVEL_GAINS["max_health"])
        player.mods["damage"] += LEVEL_GAINS["damage"]
        player.mods["speed"] += LEVEL_GAINS["speed"]
        if on_level:
            on_level(player.level)
    return levels
```

```text
Level  1 -> 2 :      80 xp      (about  8 drones)
Level  4 -> 5 :     800 xp
Level  9 -> 10:   2,278 xp
```

The shop between floors is three `Button`s and a price table:

```python
# scenes/shop.py
def build_offers(items: dict, tables: dict, rng: random.Random, floor_index: int,
                 count: int = 3) -> list[tuple[Item, int]]:
    keys = roll_loot(tables, "uncommon", rng, rolls=count * 3)
    offers = []
    for key in dict.fromkeys(keys):                   # de-duplicate, keep order
        if len(offers) >= count:
            break
        item = Item.from_spec(key, items[key])
        price = int((40 + 25 * item.rarity ** 2) * (1 + 0.12 * floor_index))
        offers.append((item, price))
    return offers
```

### Milestone 6 — Bosses

A boss is an enemy whose attacks are **scripted and telegraphed** rather than reactive. Model it as
phases, where each phase is a list of attack names, and each attack has a telegraph duration.

```python
# entities/boss.py
from dataclasses import dataclass, field


@dataclass
class Attack:
    name: str
    telegraph: float        # seconds of visible warning before it lands
    duration: float
    damage: int
    shape: str              # "ring" | "cone" | "dash" | "bullets"
    radius: float = 0.0
    cooldown: float = 1.6


@dataclass
class Phase:
    above: float            # active while health fraction is above this
    attacks: list[str]
    speed_scale: float = 1.0
    telegraph_scale: float = 1.0


ATTACKS: dict[str, Attack] = {
    "slam": Attack("slam", telegraph=0.75, duration=0.35, damage=26, shape="ring", radius=96),
    "sweep": Attack("sweep", telegraph=0.6, duration=0.4, damage=20, shape="cone", radius=170),
    "dash": Attack("dash", telegraph=0.5, duration=0.28, damage=18, shape="dash", radius=40),
    "spiral": Attack("spiral", telegraph=0.9, duration=1.2, damage=10, shape="bullets", radius=0),
}

BOSS_SPECS: dict[str, list[Phase]] = {
    "warden": [
        Phase(above=0.6, attacks=["slam", "sweep"], speed_scale=1.0, telegraph_scale=1.15),
        Phase(above=0.25, attacks=["slam", "dash", "sweep"], speed_scale=1.2, telegraph_scale=1.0),
        Phase(above=0.0, attacks=["dash", "slam", "dash"], speed_scale=1.45, telegraph_scale=0.85),
    ],
    "neural_mass": [
        Phase(above=0.7, attacks=["spiral", "sweep"], speed_scale=1.0, telegraph_scale=1.2),
        Phase(above=0.4, attacks=["spiral", "slam", "sweep"], speed_scale=1.15, telegraph_scale=1.0),
        Phase(above=0.0, attacks=["spiral", "dash", "spiral"], speed_scale=1.3, telegraph_scale=0.85),
    ],
}


class BossController:
    """Drives a boss entity through phases with telegraphed attacks."""

    def __init__(self, boss_name: str, rng):
        self.phases = BOSS_SPECS[boss_name]
        self.rng = rng
        self.phase = self.phases[0]
        self.pending: Attack | None = None
        self.telegraph_left = 0.0
        self.telegraph_total = 1.0
        self.cooldown = 1.5
        self.attack_pos = None

    def _select_phase(self, hp_fraction: float) -> Phase:
        for phase in self.phases:
            if hp_fraction > phase.above:
                return phase
        return self.phases[-1]

    def update(self, boss, dt: float, world) -> None:
        hp = boss.get(Health)
        new_phase = self._select_phase(hp.current / hp.maximum)
        if new_phase is not self.phase:
            self.phase = new_phase
            self.pending = None
            self.telegraph_left = 0.0
            self.cooldown = 1.2
            world.on_phase_change(boss, self.phase)         # flash, roar, arena change

        if self.telegraph_left > 0:
            self.telegraph_left -= dt
            if self.telegraph_left <= 0:
                self._fire(boss, world)
            return

        self.cooldown -= dt
        if self.cooldown <= 0:
            name = self.rng.choice(self.phase.attacks)
            attack = ATTACKS[name]
            self.pending = attack
            self.telegraph_total = attack.telegraph * self.phase.telegraph_scale
            self.telegraph_left = self.telegraph_total
            self.attack_pos = pg.math.Vector2(world.player.get(Transform).pos)
            world.audio.play("telegraph", volume=0.9)
            self.cooldown = attack.cooldown + self.telegraph_total

    def _fire(self, boss, world) -> None:
        attack = self.pending
        boss_tf = boss.get(Transform)
        player_tf = world.player.get(Transform)
        if attack.shape == "ring":
            if boss_tf.pos.distance_to(player_tf.pos) <= attack.radius:
                apply_damage(world, world.player, attack.damage, source_pos=boss_tf.pos,
                             knockback=340.0)
        elif attack.shape == "cone":
            to_player = player_tf.pos - boss_tf.pos
            if to_player.length() <= attack.radius and abs(boss_tf.facing.angle_to(to_player)) < 45:
                apply_damage(world, world.player, attack.damage, source_pos=boss_tf.pos)
        elif attack.shape == "dash":
            direction = (self.attack_pos - boss_tf.pos)
            if direction.length_squared() > 0:
                boss_tf.vel = direction.normalize() * 620 * self.phase.speed_scale
        elif attack.shape == "bullets":
            for i in range(18):
                angle = i * 20 + self.rng.uniform(-4, 4)
                world.spawn_projectile(boss_tf.pos, angle, speed=260, damage=attack.damage)
        world.camera.add_shake(9.0)
        world.audio.play("boss_impact", volume=1.0)
        world.fx.particles.emit(boss_tf.pos, count=26, speed=(90, 340),
                                color=(255, 120, 220), life=(0.3, 0.8))
        self.pending = None
```

Two design rules encoded here. First, `telegraph_scale` *shrinks* as the fight gets harder — later
phases are faster and give less warning, which is a legitimate difficulty curve that never removes
the warning entirely. Second, `self.attack_pos` is captured at telegraph time, not at fire time:
the player can walk out of a telegraphed slam. If you re-read the player position on fire, dodging
does nothing and the fight becomes a coin flip.

### Milestone 7 — Save, minimap, scoreboard, ship

Minimap: render the floor once to a small surface, then reveal explored cells as the player sees
them.

```python
# world/minimap.py
import pygame as pg


class Minimap:
    COLOURS = {0: (14, 14, 22), 1: (90, 100, 150), 2: (255, 200, 90), 3: (120, 255, 200)}

    def __init__(self, floor, scale: int = 3):
        self.scale = scale
        self.size = (floor.width * scale, floor.height * scale)
        self.surface = pg.Surface(self.size).convert()
        self.surface.fill((14, 14, 22))
        self.floor = floor
        self.drawn: set[tuple[int, int]] = set()

    def reveal_around(self, cell: tuple[int, int], radius: int = 9) -> None:
        cx, cy = cell
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x, y) in self.drawn or not self.floor.is_walkable(x, y):
                    continue
                if (x - cx) ** 2 + (y - cy) ** 2 > radius ** 2:
                    continue
                self.surface.fill(self.COLOURS[self.floor.tiles[y][x]],
                                  (x * self.scale, y * self.scale, self.scale, self.scale))
                self.drawn.add((x, y))
                self.floor.explored.add((x, y))

    def draw(self, surface: pg.Surface, player_cell, dest_pos=(0, 0), alpha: int = 210) -> None:
        view = pg.Surface(self.size).convert()
        view.blit(self.surface, (0, 0))
        view.set_alpha(alpha)
        pg.draw.rect(view, (255, 90, 120),
                     (player_cell[0] * self.scale - 1, player_cell[1] * self.scale - 1,
                      self.scale + 2, self.scale + 2))
        surface.blit(view, dest_pos)
```

Scoreboard: append one JSON object per run, keep the top ten.

```python
# core/scoreboard.py
import json
from pathlib import Path


def record_run(path: Path, run: dict, limit: int = 10) -> list[dict]:
    entries: list[dict] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue                        # a torn line costs one entry, not the file
    entries.append(run)
    entries.sort(key=lambda e: e.get("score", 0), reverse=True)
    entries = entries[:limit]
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
    return entries
```

JSON Lines (one JSON object per line) is the right format for append-only logs: a crash mid-write
loses one line instead of corrupting the whole file.

Save on quit:

```python
# scenes/game.py
def on_quit(self) -> None:
    save_game(self.save_path, self.world)
    self.app.quit()
```

And load at the title screen, with the "Continue" button disabled when `load_game` returns `None`
or raises.

## Key takeaways

- Polish answers player questions: did my input register, was that hit mine, am I in danger, am I
  progressing. Each answer is a small, reusable system.
- Screen shake, hit flash, particles, tweens, knockback, hitstop, and varied audio are the entire
  juice toolkit; shake magnitude must scale with consequence.
- Particle systems use a fixed pool and swap-with-last removal; never allocate per particle.
- HUD draws in screen space after the world; buttons commit on `MOUSEBUTTONUP`; modals swallow
  events so nothing behind them reacts.
- Save to the OS-provided data directory, write atomically via a temp file plus `os.replace`, keep
  one backup generation, and version the payload with a chain of migrations.
- Colourblind safety means never encoding meaning in hue alone; ship a second palette and a shape
  code.
- Profile with `cProfile` and read `tottime`, not `cumtime`; then cull, convert surfaces, stop
  per-frame allocation, and consider dirty rects.
- Packaging means a `.spec` file in version control, correct `--add-data` separators per platform,
  `sys._MEIPASS`-aware asset paths, hidden imports for dynamic code, and a test on a machine that
  is not yours.
- Neon Dungeon is a composition of systems you already have: generated floors, a shared combat
  function with i-frames, data-driven enemies using Chapter 35's FSM, telegraphed boss phases, and
  a versioned save.
- Fairness is information. Telegraph, guarantee i-frames, explain deaths, and cap simultaneous
  attackers before you touch a single damage number.

## Milestone checklist

Ship in this order. Each milestone ends with something you can play.

**Milestone 1 — Floors**
- [ ] `Floor`, `Room`, and `generate_floor(index, rng)` produce 6–14 non-overlapping rooms.
- [ ] Rooms are connected nearest-first with L-shaped corridors; no room is unreachable.
- [ ] Doors appear on corridor mouths and are walkable but block line of sight.
- [ ] Floor 5 and floor 10 generate a boss room; other floors place stairs in the farthest room.
- [ ] Same seed reproduces the same floor — verify with two runs of `generate_floor(3, Random(42))`.

**Milestone 2 — Movement and camera**
- [ ] Player accelerates toward input instead of teleporting; camera follows with smoothing.
- [ ] Camera clamps to floor bounds so you never see past the map edge.
- [ ] Dash works, has a cooldown, and grants i-frames.
- [ ] Collision from Chapter 33 stops the player at every wall, including diagonally.
- [ ] Off-screen tiles are culled before blitting.

**Milestone 3 — Combat**
- [ ] All damage flows through `apply_damage`; grep proves there is no other `hp.current -=` anywhere.
- [ ] i-frames prevent stun-lock; test by standing in a group of three enemies.
- [ ] Hits produce knockback, flash, particles, shake, hitstop, and a damage number.
- [ ] Player death shows the last three damage sources with amounts.

**Milestone 4 — Enemies**
- [ ] Drone, Brute, and Stalker load from `data/enemies.json` and use the Chapter 35 FSM.
- [ ] Enemies path with A\*, throttled and budgeted through `PathfinderService`; verify with F1
      debug drawing that paths never cross walls.
- [ ] Separation keeps enemies from stacking; check a doorway with five enemies chasing.
- [ ] Attack tokens limit simultaneous attackers to two.
- [ ] Sight cones, hearing radii, and alert memory are tunable per enemy type.

**Milestone 5 — Loot and progression**
- [ ] `roll_loot` respects weights and drop chance; run 1000 rolls and sanity-check the
      distribution.
- [ ] Inventory holds six items, sums mods, and serializes to and from JSON by key.
- [ ] XP curve grants levels; each level raises health, damage, and speed.
- [ ] Shop between floors offers three items with prices that scale with floor index.
- [ ] Buying and equipping both work, and a bought item survives a save/load cycle.

**Milestone 6 — Bosses**
- [ ] The Warden appears on floor 5 and the Neural Mass on floor 10.
- [ ] Each boss has at least three phases with different attack lists and speed scales.
- [ ] Every attack telegraphs before it lands, and the telegraph is drawn.
- [ ] Telegraph position is captured at telegraph time, so dodging actually works.
- [ ] Phase changes are signalled visually and audibly.

**Milestone 7 — Ship it**
- [ ] Save-on-quit writes a versioned payload atomically; corrupt it by hand and confirm the game
      still starts.
- [ ] Minimap reveals as you explore and persists across save/load.
- [ ] Scoreboard keeps the top ten runs in JSON Lines.
- [ ] Settings (volume, palette, keybindings, difficulty) persist in a separate file.
- [ ] `cProfile` shows no single function above 15% of frame time with 40 entities.
- [ ] Build with PyInstaller on your own platform and run it from a different working directory.
- [ ] Run the build on a second machine or a fresh user account, first-run, no save, no settings.
- [ ] Upload to itch.io with a short description that mentions the unsigned-executable warning.

## Where to take it next

Neon Dungeon 1.0 is the end of the book, not the end of the project. Ten extensions, roughly in
order of value per hour:

1. **New biomes.** A second tileset, palette, and enemy mix per biome (cryo labs, overgrown
   surface). Cheapest content you can add, because the generator does not change.
2. **Daily seeded runs.** Seed the RNG from the date, share the seed, and rank everyone who plays
   the same floor. Twenty lines, and it converts single-player into a competition.
3. **Mod support via data files.** Load `data/*.json` from the user data directory *in addition to*
   the bundled files, with user files overriding by key. Players will write enemies you would never
   have thought of.
4. **Controller support.** `pg.joystick` plus an abstraction layer over input ("move_vector",
   "pressed(action)") so keyboard and gamepad produce the same events. Do this before you add more
   actions, not after.
5. **More meta-progression.** Persistent unlocks: new starting weapons, new enemy variants that
   appear from floor 3, a shop upgrade that adds a fourth offer.
6. **Steam release.** Steamworks has a free tier now, but budget for the fee, a store page, achievements
   via the Steamworks SDK, and cloud saves. Treat it as a business task, not a coding one.
7. **Mobile with pygame-ce.** Portrait layout, touch controls (virtual stick plus tap-to-shoot),
   and a fixed timestep that survives backgrounding. Build with `briefcase` or
   `python-for-android`.
8. **Web build with pygbag.** Compile to WebAssembly and host the `web` channel on itch.io. Zero
   install for players, and a real constraint on asset size.
9. **Moddable scripting.** Expose a sandboxed Lua or a restricted Python subset so rooms, traps, and
   custom enemy brains can be defined in text files. Big feature, but it is what turns a game into
   a platform.
10. **Replay and ghost runs.** Record input per frame, store it with the seed, and replay any run
    deterministically. The hard requirement is that *nothing* in your simulation reads the system
    clock or unseeded `random` — a discipline worth adopting now, because it also makes every bug
    reproducible.
