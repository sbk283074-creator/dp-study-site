---
chapter: 33
part: 5
title: Game Architecture
summary: Structure a game that survives past 1000 lines — scene stack, fixed timestep, event bus, components, resource and data layers, debug tooling and a package layout.
minutes: 45
tags: [architecture, scenes, event bus, ECS, data-driven, resources, debug]
---

The shooter from Chapter 32 is one file and about 150 lines, and it works. Add a menu, a pause
screen, three enemy types, an inventory, a save system, and sound options, and you have 3000
lines in `main.py` where every function can see every variable and every change risks breaking
something unrelated. That is not a code-size problem, it is a coupling problem — and it is the
same problem you solved in Chapters 12 and 13 with classes and composition, applied to a program
that never stops running. This chapter gives you the five structures that keep a game
maintainable: a scene stack, a deterministic timestep, an event bus, a component-ish entity
model, and a resource layer. Plus the tooling — debug overlay, settings, saves — that makes the
difference between a demo and something you can finish.

## Scenes: one stack, many states

A game is not one loop; it is several modes that behave differently. The menu shows text and
ignores the world. Playing runs physics. Paused keeps rendering the world but stops updating it.
Game over shows a score and waits for input. Writing these as `if state == "menu":` branches
inside one loop is how 3000-line `main.py` files are born.

Model each mode as an object with the same three methods as the game loop, and stack them.

```python
# app.py — a runnable scene-stack skeleton
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
FIXED_DT = 1 / 60
MAX_FRAME = 0.25
INK = (232, 234, 240)


def centre(surface, font, text, color=INK):
    label = font.render(text, True, color)
    surface.blit(label, label.get_rect(center=surface.get_rect().center))


class Scene:
    """One mode of the game. Override only what you need."""

    def __init__(self, app):
        self.app = app

    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def handle_events(self, events) -> None: ...
    def update(self, dt: float) -> None: ...
    def draw(self, surface: pygame.Surface) -> None: ...


class SceneManager:
    def __init__(self, app, factories: dict[str, type[Scene]], start: str):
        self.app = app
        self.factories = factories      # name -> class; we build a FRESH instance each push
        self.stack: list[Scene] = []
        self.push(start)

    @property
    def current(self) -> Scene | None:
        return self.stack[-1] if self.stack else None

    def push(self, name: str) -> None:
        scene = self.factories[name](self.app)
        self.stack.append(scene)
        scene.on_enter()

    def pop(self) -> None:
        if self.stack:
            self.stack.pop().on_exit()

    def replace(self, name: str) -> None:
        self.pop()
        self.push(name)


class MenuScene(Scene):
    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.app.scenes.push("playing")

    def draw(self, surface) -> None:
        surface.fill((20, 22, 30))
        centre(surface, self.app.font, "PRESS ENTER TO PLAY")


class PlayingScene(Scene):
    def on_enter(self) -> None:
        self.app.score = 0.0
        self.player = pygame.Rect(0, 0, 32, 32)
        self.player.center = (WIDTH // 2, HEIGHT // 2)
        self.enemy = pygame.Rect(0, 0, 24, 24)
        self.enemy.center = (700, 140)
        self.vel = pygame.Vector2(190, 150)

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.app.scenes.push("paused")

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.player.x += round((keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 300 * dt)
        self.player.y += round((keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 300 * dt)
        self.player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        self.enemy.x += round(self.vel.x * dt)
        self.enemy.y += round(self.vel.y * dt)
        if self.enemy.left < 0 or self.enemy.right > WIDTH:
            self.vel.x *= -1
        if self.enemy.top < 0 or self.enemy.bottom > HEIGHT:
            self.vel.y *= -1

        self.app.score += dt
        if self.player.colliderect(self.enemy):
            self.app.scenes.replace("gameover")

    def draw(self, surface) -> None:
        surface.fill((24, 26, 34))
        pygame.draw.rect(surface, (110, 214, 148), self.player, border_radius=6)
        pygame.draw.circle(surface, (244, 114, 182), self.enemy.center, 12)
        surface.blit(self.app.font.render(f"{int(self.app.score)}", True, INK), (12, 12))


class PausedScene(Scene):
    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.app.scenes.pop()

    def update(self, dt: float) -> None:
        pass                                    # the world is frozen; that is the point

    def draw(self, surface) -> None:
        self.app.scenes.stack[-2].draw(surface)  # render the scene underneath
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((8, 8, 14, 170))
        surface.blit(shade, (0, 0))
        centre(surface, self.app.font, "PAUSED — Esc to resume")


class GameOverScene(Scene):
    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.app.scenes.replace("playing")
                elif event.key == pygame.K_ESCAPE:
                    self.app.scenes.replace("menu")

    def draw(self, surface) -> None:
        surface.fill((30, 20, 26))
        centre(surface, self.app.font, f"GAME OVER — {int(self.app.score)}", (244, 114, 182))
        small = self.app.small
        centre(surface, small, "R to retry · Esc for menu", (150, 156, 170))


class App:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Scene stack")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.small = pygame.font.Font(None, 24)
        self.score = 0.0
        self.scenes = SceneManager(self, {
            "menu": MenuScene,
            "playing": PlayingScene,
            "paused": PausedScene,
            "gameover": GameOverScene,
        }, "menu")

    def run(self) -> None:
        accumulator = 0.0
        running = True
        while running:
            frame_dt = min(self.clock.tick(FPS) / 1000.0, MAX_FRAME)

            events = pygame.event.get()
            if any(e.type == pygame.QUIT for e in events):
                running = False
                break
            self.scenes.current.handle_events(events)

            # fixed timestep: physics always advances in identical slices
            accumulator += frame_dt
            steps = 0
            while accumulator >= FIXED_DT and steps < 5:
                scene = self.scenes.current
                scene.update(FIXED_DT)
                accumulator -= FIXED_DT
                steps += 1
                if self.scenes.current is not scene:
                    accumulator = 0.0        # a scene switch invalidates leftover time
                    break

            self.scenes.current.draw(self.screen)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    App().run()
```

Notice what the stack buys you. Pause is a *push*, not a replacement, so the playing scene keeps
its state and `PausedScene` can render it underneath — that one line is why pause works at all.
Game over is a `replace`, so retrying constructs a brand-new `PlayingScene` and nothing leaks
from the previous run. And `self.factories[name](self.app)` builds a **fresh instance every
push**; holding one instance per scene and reusing it is exactly how stale scores survive a
restart.

## Fixed timestep: determinism

Variable `dt` is fine for a lone square. It is not fine for physics: with `dt` varying, a jump
reaches a slightly different height every run, collision resolution depends on the frame's
length, and a bug you saw once cannot be reproduced. The fix is to accumulate real time and
consume it in fixed slices:

```python
accumulator += frame_dt
while accumulator >= FIXED_DT:
    update(FIXED_DT)          # identical every time, on every machine
    accumulator -= FIXED_DT
alpha = accumulator / FIXED_DT   # leftover fraction, for render interpolation
```

Two guards matter. `MAX_FRAME` (0.25 s) prevents a "spiral of death": after a stall the
accumulator is huge, the loop runs hundreds of updates, and the game falls further behind. The
`steps < 5` cap does the same thing. And `alpha` is available if you want to interpolate
positions between physics steps for extra-smooth rendering — most 2D games do not need it.

## Event bus: decoupling

When an enemy dies, who needs to know? The score, the particle system, the sound player, the
quest tracker, the achievement system. If the enemy calls all of them, the enemy class imports
half your codebase, and adding a feature means editing it.

Post a fact instead, and let whoever cares subscribe:

```python
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class EnemyDied:
    kind: str
    x: int
    y: int
    points: int


class EventBus:
    """Queue-based: posted events are delivered when dispatch() runs, never re-entrantly."""

    def __init__(self) -> None:
        self._subs: dict[type, list] = defaultdict(list)
        self._queue: deque = deque()

    def subscribe(self, event_type: type, handler) -> None:
        self._subs[event_type].append(handler)

    def post(self, event) -> None:
        self._queue.append(event)

    def dispatch(self) -> None:
        while self._queue:
            event = self._queue.popleft()
            for handler in list(self._subs[type(event)]):
                handler(event)
```

```python
bus.subscribe(EnemyDied, lambda e: score.add(e.points))
bus.subscribe(EnemyDied, lambda e: particles.burst(e.x, e.y))
bus.subscribe(EnemyDied, lambda e: bus.post(PlaySound("boom.wav")))

# deep inside Enemy.update — it knows nothing about score, particles or audio
bus.post(EnemyDied(kind=self.kind, x=self.rect.centerx, y=self.rect.centery, points=10))
```

Queued delivery (rather than calling handlers inside `post`) avoids the nastiest failure mode: a
handler that posts another event and re-enters the dispatch loop while you are iterating it.
Call `bus.dispatch()` once per update, after systems have run.

## Entities: inheritance or components?

You have two options for "a thing in the world". Neither is always right.

**Inheritance** — class per entity type, shared behaviour in a base class:

```python
class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = image.get_rect(center=pos)

class Goblin(Entity):
    def update(self, dt, *args):
        self.rect.x += round(self.speed * dt)

class Chest(Entity):
    def update(self, dt, *args):
        pass          # chests do not walk
```

**Components** — an entity is a bag of small data objects; systems operate on all entities that
have the parts they need:

```python
from dataclasses import dataclass


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Velocity:
    vx: float = 0.0
    vy: float = 0.0


@dataclass
class Health:
    hp: int = 1
    max_hp: int = 1


@dataclass
class Render:
    image: object = None        # a pygame.Surface in real code


def movement_system(world: list[dict], dt: float) -> None:
    for entity in world:
        pos, vel = entity.get("pos"), entity.get("vel")
        if pos and vel:
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt


def death_system(world: list[dict], bus) -> None:
    for entity in world:
        health = entity.get("health")
        if health and health.hp <= 0:
            pos = entity["pos"]
            bus.post(EnemyDied(entity["kind"], round(pos.x), round(pos.y), 10))
            entity["dead"] = True
    world[:] = [e for e in world if not e.get("dead")]
```

| | Inheritance | Components |
| --- | --- | --- |
| Best for | Few types, distinct behaviour per type | Many combinations of shared traits |
| Adding a new type | New class | New dict of components |
| "A flying, poison-immune chest" | New subclass, or diamond inheritance | Add `Flying()` and `Immunity()` |
| Debug/inspect | Read the class | Print the dict |
| Cost | Simple, familiar | More indirection, slower lookups |

The pragmatic answer: **start with sprite inheritance** (Chapter 32 style) and switch to
components when you catch yourself writing `class FlyingPoisonChest(Chest, Flyer, Poisonable)`.
The component version above is deliberately plain — a dict per entity and functions over a list —
because that is all an ECS really is, and a full framework is overkill below about fifty entity
types.

## Resource manager

Every chapter so far has said "load it once". Here is the one place that happens:

```python
from pathlib import Path
import pygame


class Resources:
    """Loads assets once, caches by (path, variant), and keeps sheets alive for subsurfaces."""

    def __init__(self, root: str | Path = "assets") -> None:
        self.root = Path(root)
        self._images: dict[tuple, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._fonts: dict[tuple, pygame.font.Font] = {}

    def image(self, rel: str, scale: float = 1.0) -> pygame.Surface:
        key = (rel, scale)
        if key not in self._images:
            surface = pygame.image.load(self.root / rel).convert_alpha()
            if scale != 1.0:
                surface = pygame.transform.scale(
                    surface,
                    (int(surface.get_width() * scale), int(surface.get_height() * scale)),
                )
            self._images[key] = surface
        return self._images[key]

    def sound(self, rel: str, volume: float = 0.5):
        if rel not in self._sounds:
            path = self.root / rel
            self._sounds[rel] = pygame.mixer.Sound(path) if path.is_file() else None
            if self._sounds[rel]:
                self._sounds[rel].set_volume(volume)
        return self._sounds[rel]

    def font(self, size: int, rel: str | None = None) -> pygame.font.Font:
        key = (rel, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(str(self.root / rel) if rel else None, size)
        return self._fonts[key]

    def clear(self) -> None:
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()
```

One instance, created in `App.__init__`, passed to anything that needs it. `clear()` exists
because reloading assets on the fly (a mod, a level pack switch, a test) should not require a
restart.

## Data-driven design

Hard-coded numbers are the enemy of tuning. If changing goblin speed requires a code edit and a
restart, you will not experiment, and your game will feel worse.

```json
{
  "bat": {"hp": 1, "speed": 150, "points": 10, "color": [180, 120, 240]},
  "goblin": {"hp": 3, "speed": 90, "points": 25, "color": [110, 200, 120]},
  "ogre": {"hp": 8, "speed": 55, "points": 60, "color": [200, 90, 90]}
}
```

```python
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnemyStats:
    kind: str
    hp: int
    speed: int
    points: int
    color: tuple[int, int, int]


def load_enemy_stats(path: str | Path) -> dict[str, EnemyStats]:
    raw = json.loads(Path(path).read_text())
    return {
        kind: EnemyStats(kind, v["hp"], v["speed"], v["points"], tuple(v["color"]))
        for kind, v in raw.items()
    }


STATS = load_enemy_stats("data/enemies.json")
enemy = make_enemy(STATS["goblin"])      # designers edit JSON, not Python
```

The same trick applies to weapons, wave tables, level layouts, and dialogue. Chapter 19 covered
the persistence side; here the point is that **tuning becomes a data change**, which means a
designer can do it without you.

## Settings and configuration

```python
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

SAVE_DIR = Path.home() / ".mystudios" / "mygame"


@dataclass
class Settings:
    width: int = 960
    height: int = 540
    fullscreen: bool = False
    music_volume: float = 0.5
    sfx_volume: float = 0.8
    keybindings: dict[str, int] = field(default_factory=lambda: {"left": 97, "right": 100})

    @classmethod
    def load(cls, path: Path) -> "Settings":
        if path.is_file():
            saved = json.loads(path.read_text())
            known = {k: v for k, v in saved.items() if k in cls().__dict__}
            return cls(**known)          # ignore keys from older versions
        return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2))
```

Filtering unknown keys on load is the cheap version of schema migration: an old save file with a
removed setting loads instead of crashing. Chapter 8 covered the file mechanics; the new idea is
`Path.home()` so you never write config next to your source.

## Debug overlay

Build it on day one, not when you are stuck.

```python
class Debug:
    def __init__(self, resources) -> None:
        self.enabled = False
        self.font = resources.font(18)

    def handle(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.enabled = not self.enabled

    def draw(self, surface, clock, world, camera=None) -> None:
        if not self.enabled:
            return
        lines = [f"fps {clock.get_fps():5.1f}", f"entities {len(world)}"]
        for i, text in enumerate(lines):
            surface.blit(self.font.render(text, True, (255, 220, 120)), (8, 8 + i * 20))
        for entity in world:                       # hitboxes in world space
            hitbox = entity.get("hitbox")
            if hitbox:
                rect = camera.apply(hitbox) if camera else hitbox
                pygame.draw.rect(surface, (255, 60, 60), rect, width=1)
```

FPS, entity count, and visible hitboxes answer "why is it slow", "did that spawn", and "is the
collision shape where I think it is" without adding a single `print`.

## Saving and loading game state

```python
def save_game(path: Path, state: dict) -> None:
    state = {**state, "version": 1}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def load_game(path: Path) -> dict | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    if data.get("version") != 1:
        return None                     # refuse rather than corrupt: offer a fresh start
    return data
```

Save coordinates, hp, inventory ids, level index, and RNG seeds — never Surfaces, sprites, or
live objects. Store *ids* and rebuild the objects on load.

## Project layout

```text
mygame/
  main.py               # creates App, calls run()
  core/
    __init__.py
    app.py              # window, clock, scene manager, main loop
    scenes.py           # Scene, SceneManager
    events.py           # EventBus, event dataclasses
    resources.py        # image/sound/font caches
    config.py           # Settings load/save
    debug.py            # Debug overlay
  entities/
    __init__.py
    player.py
    enemies.py
  systems/
    __init__.py
    physics.py          # movement, collision resolution
    combat.py           # damage, death events
    spawn.py
  scenes/
    __init__.py
    menu.py
    playing.py
    paused.py
    gameover.py
  data/
    enemies.json
    waves.json
    level1.txt
  assets/
    images/
    sounds/
    fonts/
  tests/
    test_physics.py
```

Rules of thumb: `core/` knows nothing about your game; `entities/` and `systems/` know nothing
about pygame's display; `scenes/` is the only place that wires them together. If `core/` imports
from `scenes/`, the dependency is backwards — that is the smell to watch for. Chapter 22's
packaging guidance applies directly; Chapter 36 turns this into a distributable build.

:::scenario "Restarting after game over keeps the old score, and nobody can write tests"
QA files two bugs. After dying and pressing R, the score starts where the last run ended and a
few enemies are still on screen from the previous life. Separately, a developer tries to write a
unit test for the scoring system and discovers that importing `enemies.py` opens a window.
:::

:::solution Make scenes disposable, inject dependencies, and delete the globals
Both symptoms trace to module-level mutable state. Somewhere in the code lives
`score = 0` at module scope, plus an `ENEMIES = []` list that scenes append to and forget to
clear. Because the values live on the module, they outlive every scene.

Three changes fix it for good:

1. **Scene factories, not scene singletons.** `SceneManager` stores classes and constructs a new
   instance per push, so `on_enter()` is a real initialiser for scene state:

   ```python
   # before: one instance reused forever
   self.scenes = {"playing": PlayingScene(self), "menu": MenuScene(self)}

   # after: fresh state on every push
   self.factories = {"playing": PlayingScene, "menu": MenuScene}
   scene = self.factories[name](self.app)
   ```

2. **State lives on the scene or on an explicit context object**, never at module level. Pass the
   context in:

   ```python
   class PlayingScene(Scene):
       def __init__(self, app):
           super().__init__(app)
           self.world: list[dict] = []      # per-run state, dies with the scene
           self.score = 0
   ```

3. **Inject pygame rather than importing it at module scope in logic modules.** `systems/physics.py`
   should take rects and numbers, not touch `pygame.display`. Then a test can run headless:

   ```python
   # tests/test_physics.py
   from systems.physics import resolve_x

   def test_player_stops_at_wall():
       player = pygame.Rect(0, 0, 32, 32)
       wall = pygame.Rect(40, 0, 32, 32)
       resolve_x(player, [wall], dx=20)
       assert player.right == wall.left
   ```

A useful rule: if you cannot construct two independent instances of a system and run them side by
side, it has hidden global state, and it will bite you the first time you need a replay, a test,
or a second level.
:::

:::pitfall Singletons and global mutable state
`SCORE = 0`, `ENEMIES = []`, `resources = Resources()` at module level look convenient — no
passing things around. They also mean: state survives restarts, so bugs appear only on the second
run; two systems silently share one list; tests cannot run in isolation or in parallel; and you
cannot reset the game without restarting the process. Create objects in one place (the `App`),
pass them explicitly, and let scenes own their state. The only module-level names in your game
should be constants and functions.
:::

## Key takeaways

- Model each game mode as a `Scene` with `handle_events`, `update`, and `draw`; a `SceneManager`
  stack gives you pause (push) and restart (replace/fresh instance) for free.
- Build a new scene instance on every push so `on_enter()` is a genuine reset; reusing instances
  is how stale state survives a restart.
- A fixed timestep accumulator makes physics deterministic and reproducible; clamp frame time and
  cap the number of catch-up steps to avoid the spiral of death.
- An event bus decouples producers from consumers: an enemy posts `EnemyDied` and never learns
  that a score exists. Dispatch from a queue to avoid re-entrancy.
- Use sprite inheritance until type combinations explode, then move to entities-as-dicts with
  systems — that is all a lightweight ECS is.
- Cache images, sounds, and fonts in one resource manager, and move tunable numbers into JSON so
  balance changes are data edits.
- Ship a debug overlay (FPS, entity count, hitboxes) and a settings file under `Path.home()`
  before the game gets complicated.
- Keep `core/` game-agnostic: dependencies point inward, never from core to scenes.

## Practice

- [ ] Add a `HelpScene` to the skeleton: pushed from the menu with `H`, popped with Escape, drawn
      over a dimmed menu.
- [ ] Change the loop to log (to the console, once a second) how many fixed updates ran in the
      last frame, then verify it stays at 1 on a healthy machine.
- [ ] Add an `EventBus` to the skeleton: post `EnemyDied` when the enemy is touched, and have two
      subscribers — one that adds points to the score and one that spawns three short-lived
      particle rects.
- [ ] Write `Resources` and a `data/enemies.json`, then spawn three enemy types from the JSON
      instead of hard-coded stats.
- [ ] Add a `Settings` dataclass persisted to `Path.home()`, an F3 debug overlay showing FPS and
      hitboxes, and save/load that restores score and player position with a version check.

## Solutions

:::solution Exercise 1
```python
class HelpScene(Scene):
    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_h):
                self.app.scenes.pop()

    def draw(self, surface) -> None:
        self.app.scenes.stack[-2].draw(surface)
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((8, 8, 14, 170))
        surface.blit(shade, (0, 0))
        centre(surface, self.app.font, "ARROWS move · Esc back", (232, 234, 240))


# in MenuScene.handle_events — the branch that opens the help scene on top:
if event.key == pygame.K_RETURN:
    self.app.scenes.push("playing")
elif event.key == pygame.K_h:
    self.app.scenes.push("help")

# in App.__init__ factories dict:
scene_factories = {"menu": MenuScene, "playing": PlayingScene, "help": HelpScene}
```
Because pause and help are pushes, they can render whatever is below them on the stack. That is
the entire argument for a stack over a single "current state" variable.
:::

:::solution Exercise 2
```python
# inside App.run
report = 0.0
frames = 0
steps_total = 0

while running:
    frame_dt = min(self.clock.tick(FPS) / 1000.0, MAX_FRAME)
    steps = 0
    accumulator += frame_dt
    while accumulator >= FIXED_DT and steps < 5:
        self.scenes.current.update(FIXED_DT)
        accumulator -= FIXED_DT
        steps += 1

    frames += 1
    steps_total += steps
    report += frame_dt
    if report >= 1.0:
        print(f"updates/frame: {steps_total / frames:.2f}  fps: {frames / report:.1f}")
        report = frames = steps_total = 0
```
```text
updates/frame: 1.00  fps: 60.0
updates/frame: 2.31  fps: 32.4
```
A healthy machine shows exactly 1.00. Sustained 2.0 means the fixed step is too expensive for
the frame budget — optimise or raise `FIXED_DT`; the `steps < 5` cap is silently dropping time
and the game is running in slow motion.
:::

:::solution Exercise 3
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EnemyDied:
    x: int
    y: int
    points: int


class PlayingScene(Scene):
    def on_enter(self) -> None:
        self.bus = self.app.bus
        self.bus.subscribe(EnemyDied, self._on_enemy_died)
        self.bus.subscribe(EnemyDied, self._spawn_particles)
        self.particles: list[dict] = []
        ...

    def _on_enemy_died(self, event: EnemyDied) -> None:
        self.score += event.points

    def _spawn_particles(self, event: EnemyDied) -> None:
        for dx, dy in ((-1, 0), (1, 0), (0, -1)):
            self.particles.append({"x": event.x, "y": event.y, "vx": dx * 180, "vy": dy * 180,
                                   "life": 0.4})

    def update(self, dt: float) -> None:
        ...
        if self.player.colliderect(self.enemy):
            self.bus.post(EnemyDied(*self.enemy.center, 25))
            self.enemy.center = (700, 140)
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.particles[:] = [p for p in self.particles if p["life"] > 0]
        self.bus.dispatch()
```
The enemy/player collision code knows nothing about scoring or particles — it states a fact and
moves on. Adding a sound effect later is one new subscriber, with zero changes to this class.
:::

:::solution Exercise 4
```python
import json
from dataclasses import dataclass
from pathlib import Path
import pygame


@dataclass(frozen=True)
class Stats:
    kind: str
    hp: int
    speed: int
    points: int
    color: tuple[int, int, int]


STATS = {k: Stats(k, **v) for k, v in json.loads(Path("data/enemies.json").read_text()).items()}


class Enemy(pygame.sprite.Sprite):
    def __init__(self, stats: Stats, x: int, y: int, *groups):
        super().__init__(*groups)
        self.stats = stats
        self.hp = stats.hp
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.rect(self.image, stats.color, (0, 0, 28, 28), border_radius=8)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt: float, *args) -> None:
        self.rect.x += round(self.stats.speed * dt)


goblins = pygame.sprite.Group(Enemy(STATS["goblin"], 100, 200) for _ in range(3))
```
`Stats(k, **v)` maps a JSON object straight onto a frozen dataclass, so a missing key fails at
load time with a clear error instead of silently defaulting halfway through a run. Tune `hp` in
the JSON, restart, done — no code edit.
:::

:::solution Exercise 5
```python
import json
from dataclasses import dataclass, asdict
from pathlib import Path
import pygame

SAVE_DIR = Path.home() / ".mystudios" / "mygame"


@dataclass
class Settings:
    width: int = 960
    height: int = 540
    sfx_volume: float = 0.8

    @classmethod
    def load(cls) -> "Settings":
        path = SAVE_DIR / "settings.json"
        if path.is_file():
            known = {k: v for k, v in json.loads(path.read_text()).items() if k in cls().__dict__}
            return cls(**known)
        return cls()

    def save(self) -> None:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        (SAVE_DIR / "settings.json").write_text(json.dumps(asdict(self), indent=2))


def save_game(state: dict) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    (SAVE_DIR / "save.json").write_text(json.dumps({**state, "version": 1}, indent=2))


def load_game() -> dict | None:
    path = SAVE_DIR / "save.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    return data if data.get("version") == 1 else None


class Debug:
    def __init__(self) -> None:
        self.enabled = False
        self.font = pygame.font.Font(None, 18)

    def handle(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.enabled = not self.enabled

    def draw(self, surface, clock, sprites) -> None:
        if not self.enabled:
            return
        surface.blit(self.font.render(f"fps {clock.get_fps():5.1f}  sprites {len(sprites)}",
                                      True, (255, 220, 120)), (8, 8))
        for sprite in sprites:
            box = getattr(sprite, "hitbox", sprite.rect)
            pygame.draw.rect(surface, (255, 60, 60), box, width=1)
```
Call `settings.save()` when the options screen closes and `save_game(...)` at each level
transition. The version check means a save from a future build is rejected instead of half-loaded,
which is always better than a corrupted run.
:::
