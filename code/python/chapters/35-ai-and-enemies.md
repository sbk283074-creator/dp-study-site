---
chapter: 35
part: 5
title: AI, Pathfinding & Enemy Behavior
summary: Give enemies steering, senses, memory, states, and A* pathfinding that stays fast enough to run forty of them at once.
minutes: 50
tags: [game AI, steering behaviours, finite state machines, A*, pathfinding, spatial hashing]
---

An enemy that walks into a wall breaks the spell faster than a bad texture. Players do not
analyse your AI; they feel it. They feel whether the guard noticed them, whether it gave them a
chance, whether it got stuck on a corner. Everything in this chapter exists to make enemies feel
deliberate without being smart, and cheap without being obvious. You already have the pieces from
Chapters 31 to 34: a game loop with delta time, sprites and collision, a scene stack, and a
tilemap generator. Now you put a decision-making brain inside the sprites.

## Game AI is not machine learning

The "AI" in game AI means *artificial intelligence* in the 1970s sense: hand-authored rules that
produce believable behaviour. No training, no neural network, no model file. A wolf that chases
you when it sees you, loses interest after four seconds, and circles rather than walking into the
campfire is doing three things: **sensing**, **deciding**, and **moving**. Those are the three
layers this chapter builds, in that order, bottom-up:

| Layer | Question it answers | Technique |
|---|---|---|
| Movement | Given a goal, how do I get there? | Steering behaviours, A* pathfinding |
| Sensing | What do I know about the world? | Distance, line of sight, hearing, memory |
| Deciding | What do I do with what I know? | Finite state machines, behaviour trees |

Machine learning shows up in games for things like NPC dialogue or opponent modelling in
strategy titles. For an action roguelike, a hand-written state machine beats a neural network on
every axis that matters: it is debuggable at 2am, it is deterministic when you need to reproduce
a bug, and you can tune exactly the one behaviour a playtester complained about.

:::note The one rule that overrules everything else
**Readable beats optimal.** An enemy that paths perfectly and shoots with zero reaction time is
not fun; it is a wall. Every "flaw" you add on purpose — a wind-up before the swing, a half-second
of surprise, a shot that lands slightly wide — is a signal the player can read and respond to.
Tuning is the art of choosing which flaws to keep.
:::

## Steering behaviours

The problem: you want something to move toward a point without teleporting, without snapping to a
direction, and without you hand-writing a curve. **Steering behaviours** (Craig Reynolds, 1999)
solve this with three lines of vector maths. Each behaviour produces a *desired velocity*; the
steering force is `desired - current`, which means the agent accelerates smoothly instead of
jerking.

`pygame.math.Vector2` does the heavy lifting. Two habits from the start: use `length_squared()`
instead of `length()` when you are comparing distances (it skips a square root), and never
normalise a vector without knowing it is non-zero.

```python
# steering.py
import math
import random

import pygame as pg


def limit(vec: pg.math.Vector2, max_length: float) -> pg.math.Vector2:
    """Clamp a vector's length. Safe on the zero vector."""
    if vec.length_squared() > max_length * max_length:
        vec.scale_to_length(max_length)
    return vec


class Agent:
    """A point mass that steers. Everything else in this chapter moves one of these."""

    def __init__(self, pos, max_speed: float = 140.0, max_force: float = 420.0,
                 radius: float = 10.0):
        self.pos = pg.math.Vector2(pos)
        self.vel = pg.math.Vector2()
        self.facing = pg.math.Vector2(1, 0)
        self.max_speed = max_speed
        self.max_force = max_force
        self.radius = radius
        self._wander_angle = random.uniform(0, 360)

    # --- the core -------------------------------------------------------
    def steer(self, desired: pg.math.Vector2) -> pg.math.Vector2:
        """force = desired_velocity - current_velocity, clamped to max_force."""
        if desired.length_squared() == 0:
            return pg.math.Vector2()
        desired = desired.normalize() * self.max_speed
        return limit(desired - self.vel, self.max_force)

    def integrate(self, force: pg.math.Vector2, dt: float) -> None:
        self.vel += force * dt
        limit(self.vel, self.max_speed)
        if self.vel.length_squared() > 1:
            self.facing = self.vel.normalize()
        self.pos += self.vel * dt

    # --- behaviours -----------------------------------------------------
    def seek(self, target) -> pg.math.Vector2:
        """Full speed toward a point. Overshoots and orbits; that is what arrive() fixes."""
        return self.steer(pg.math.Vector2(target) - self.pos)

    def flee(self, target, panic_range: float = 220.0) -> pg.math.Vector2:
        diff = self.pos - pg.math.Vector2(target)
        if diff.length_squared() > panic_range * panic_range:
            return pg.math.Vector2()          # too far to care
        return self.steer(diff)

    def arrive(self, target, slow_radius: float = 70.0) -> pg.math.Vector2:
        """Seek, but ease off inside slow_radius so it settles instead of orbiting."""
        to_target = pg.math.Vector2(target) - self.pos
        dist = to_target.length()
        if dist == 0:
            return pg.math.Vector2()
        speed = self.max_speed * min(1.0, dist / slow_radius)
        desired = to_target / dist * speed
        return limit(desired - self.vel, self.max_force)

    def wander(self, dt: float, distance: float = 50.0, radius: float = 24.0,
               jitter: float = 90.0) -> pg.math.Vector2:
        """Idle movement that looks intentional: a point ahead, nudged by a drifting angle."""
        self._wander_angle += random.uniform(-jitter, jitter) * dt
        if self.vel.length_squared() > 0:
            ahead = self.vel.normalize() * distance
        else:
            ahead = pg.math.Vector2(distance, 0)
        offset = pg.math.Vector2()
        offset.from_polar((radius, self._wander_angle))   # (length, degrees)
        return self.steer(ahead + offset)
```

`seek` plus `integrate` is a complete homing missile:

```python
agent = Agent((400, 300))
for frame in range(600):                 # pretend loop
    force = agent.seek(target_pos)
    agent.integrate(force, dt)
```

`arrive` is `seek` with a speed ramp, and that ramp is the difference between a guard who parks
on his waypoint and one who orbits it forever. `wander` drifts a target point around a circle
ahead of the agent; small `jitter` gives a lazy sweep, large `jitter` gives a twitchy insect.

### Separation and cohesion

Two more behaviours handle crowds. **Separation** pushes an agent away from anyone inside a
personal-space radius; **cohesion** pulls it toward the local centre of mass. Separation alone
fixes the single most common AI complaint in the world: enemies stacking into one sprite.

```python
def separation(agent: Agent, neighbours, desired_gap: float | None = None) -> pg.math.Vector2:
    if desired_gap is None:
        desired_gap = agent.radius * 2.5
    push = pg.math.Vector2()
    for other in neighbours:
        if other is agent:
            continue
        away = agent.pos - other.pos
        d = away.length()
        if d == 0:                       # perfectly stacked: nudge randomly
            away = pg.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            continue
        if d < desired_gap:
            push += away / d * (desired_gap - d) / desired_gap
    if push.length_squared() == 0:
        return pg.math.Vector2()
    return agent.steer(push * agent.max_speed)


def cohesion(agent: Agent, neighbours, radius: float = 90.0) -> pg.math.Vector2:
    centre = pg.math.Vector2()
    count = 0
    for other in neighbours:
        if other is agent:
            continue
        if agent.pos.distance_to(other.pos) < radius:
            centre += other.pos
            count += 1
    if count == 0:
        return pg.math.Vector2()
    return agent.steer(centre / count - agent.pos)
```

Steering forces are just vectors, so combining them is addition with weights:

```python
force = (separation(agent, neighbours) * 1.6
         + cohesion(agent, neighbours) * 0.7
         + agent.wander(dt) * 0.4)
agent.integrate(force, dt)
```

Those three numbers *are* the personality. Crank separation and you get a skittish swarm. Crank
cohesion and you get a wolf pack. This pattern — sum weighted forces, integrate once — scales from
two bats to two hundred without new code.

:::pitfall Normalising the zero vector
`Vector2(0, 0).normalize()` raises `ValueError`, and even where it silently returns zero you
have a bug: an agent standing exactly on its target has no direction to move, and `desired - vel`
becomes a nudge toward the origin. Every normalize in your AI code needs a
`length_squared() > 0` guard, or a fallback direction like the random nudge in `separation`.
:::

## Perception: what an enemy knows

Movement without senses is a wind-up toy. Perception answers two questions, in this order: is the
player *detectable* at all (range, cone, occlusion), and if detection stops, how long do I keep
believing it (memory)?

Start with the grid — the same tilemap from Chapter 34, wrapped in the two queries AI needs. The
second one, line of sight, is implemented with **Bresenham's line algorithm**: walk the cells
between two points using integer arithmetic only, which is exactly what you want at 60 fps.

```python
# world/grid.py
import pygame as pg

WALL, FLOOR, DOOR = 0, 1, 2
WALKABLE = {FLOOR, DOOR}


class Grid:
    """Tilemap with the two AI queries: 'can I stand here' and 'can I see there'."""

    def __init__(self, width: int, height: int, tile_size: int = 32, fill: int = WALL):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = [[fill] * width for _ in range(height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.tiles[y][x] in WALKABLE

    def cell_at(self, world_pos) -> tuple[int, int]:
        return (int(world_pos[0] // self.tile_size), int(world_pos[1] // self.tile_size))

    def world_center(self, cell) -> pg.math.Vector2:
        return pg.math.Vector2((cell[0] + 0.5) * self.tile_size,
                               (cell[1] + 0.5) * self.tile_size)

    def has_line_of_sight(self, a_world, b_world) -> bool:
        """True if no wall cell lies between the two world positions."""
        x0, y0 = self.cell_at(a_world)
        x1, y1 = self.cell_at(b_world)
        for x, y in bresenham(x0, y0, x1, y1):
            if not self.is_walkable(x, y):
                return False
        return True


def bresenham(x0: int, y0: int, x1: int, y1: int):
    """Yield every cell on the integer line from (x0,y0) to (x1,y1), inclusive."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
```

Bresenham is not the physically correct visibility test — it can slip through a diagonal gap
between two wall corners. If that bothers you, use **supercover Bresenham** (step both axes when
`e2` hits the tie) or sample the segment every half tile:

```python
def has_line_of_sight_sampled(grid: Grid, a, b) -> bool:
    """Simpler, slower, and never squeezes through a diagonal crack."""
    a = pg.math.Vector2(a)
    b = pg.math.Vector2(b)
    steps = max(2, int(a.distance_to(b) / (grid.tile_size * 0.4)))
    for i in range(steps + 1):
        p = a.lerp(b, i / steps)
        if not grid.is_walkable(*grid.cell_at(p)):
            return False
    return True
```

Use Bresenham for the per-frame perception of many enemies, sampling for the rare case where
correctness matters more than cost (a sniper's shot, a "did the player see me" check).

Now the senses themselves:

```python
# ai/perception.py
from dataclasses import dataclass

import pygame as pg


@dataclass
class Perception:
    sight_range: float = 240.0
    fov: float = 110.0        # full angle in degrees; 360 means omniscient
    hearing: float = 160.0    # base radius, scaled by the target's noise level
    memory: float = 3.5       # seconds the enemy keeps believing an old sighting

    def in_cone(self, eye, forward: pg.math.Vector2, target) -> bool:
        to_target = pg.math.Vector2(target) - eye
        dist = to_target.length()
        if dist > self.sight_range:
            return False
        if dist == 0 or self.fov >= 360:
            return True
        return abs(forward.angle_to(to_target)) <= self.fov / 2

    def hears(self, ear, target, noise: float) -> bool:
        return pg.math.Vector2(ear).distance_to(target) <= self.hearing * noise
```

`Vector2.angle_to` returns the signed angle in degrees, so `abs(...) <= fov / 2` is the cone
test. The `noise` parameter is the trick that makes stealth work: the player carries a noise
multiplier — `0.35` crouching, `1.0` walking, `1.8` sprinting, `3.0` for a shotgun blast — and
hearing simply scales by it. You get a sneaking system for one multiplication.

**Alert memory** is what separates a believable guard from a goldfish. When the enemy loses sight,
it does not instantly forget; it keeps a `last_known` position and a countdown, walks there, and
then gives up. The countdown is also the fix for state thrash, which you will see in the scenario
at the end of this section.

## Finite state machines

You now have an enemy that can move and sense. It still cannot decide. The decision structure
that has shipped in more games than anything else is the **finite state machine**: a fixed set of
states, exactly one active, each with rules for leaving.

The class-per-state layout is the one worth learning first. Each state is an object with
`enter`, `update`, and `exit`; transitions are explicit `machine.change(...)` calls. It beats the
giant `if self.state == "chase"` ladder because adding a state means adding a file, not editing a
200-line function, and because `enter`/`exit` give you a guaranteed place to start and stop
things (animations, timers, sounds).

```python
# ai/fsm.py
class EnemyState:
    name = "unnamed"

    def enter(self, enemy) -> None:
        """Called once on transition in. Start animations and timers here."""

    def exit(self, enemy) -> None:
        """Called once on transition out. Cancel anything enter() started."""

    def update(self, enemy, dt: float, world) -> None:
        raise NotImplementedError


class StateMachine:
    def __init__(self, owner, states: dict[str, EnemyState], initial: str):
        self.owner = owner
        self.states = states
        self.state: EnemyState | None = None
        self.time_in_state = 0.0
        self.change(initial)

    def change(self, name: str) -> None:
        if self.state is not None and self.state.name == name:
            return                                   # already there: no-op
        if self.state is not None:
            self.state.exit(self.owner)
        self.state = self.states[name]
        self.time_in_state = 0.0
        self.state.enter(self.owner)

    def update(self, dt: float, world) -> None:
        self.time_in_state += dt
        self.state.update(self.owner, dt, world)
```

`time_in_state` looks like decoration. It is not — it is how you implement minimum dwell time,
which is the cure for the flip-flopping enemy below.

Here is the full enemy: stats, senses, a path to follow, and five states.

```python
# entities/enemy.py
from dataclasses import dataclass, field

import pygame as pg

from ai.fsm import StateMachine
from ai.perception import Perception
from steering import Agent


@dataclass
class EnemyStats:
    max_health: int = 30
    speed: float = 90.0
    sight_range: float = 240.0
    fov: float = 110.0
    hearing: float = 160.0
    memory: float = 3.5
    attack_range: float = 44.0
    attack_damage: int = 8
    attack_windup: float = 0.35     # telegraph: player can dodge
    attack_recover: float = 0.45    # punishable window
    attack_cooldown: float = 1.10
    flee_below: int = 0             # 0 = never flees
    reaction: float = 0.20          # "surprise" beat before acting
    accuracy_deg: float = 3.0


class Enemy(Agent):
    def __init__(self, pos, stats: EnemyStats, waypoints=()):
        super().__init__(pos, max_speed=stats.speed, radius=11.0)
        self.stats = stats
        self.health = stats.max_health
        self.perception = Perception(sight_range=stats.sight_range, fov=stats.fov,
                                     hearing=stats.hearing, memory=stats.memory)
        self.waypoints = list(waypoints)
        self.waypoint_index = 0
        self.path: list[tuple[int, int]] = []
        self.destination = pg.math.Vector2(pos)
        self.goal_cell: tuple[int, int] | None = None
        self.repath_timer = 0.0
        self.alert = 0.0             # >0 means "I believe the player was over there"
        self.last_known: pg.math.Vector2 | None = None
        self.reaction_left = 0.0
        self.cooldown = 0.0
        self.anim = "idle"
        self.remove = False
        self.machine = StateMachine(self, {
            "patrol": Patrol(),
            "chase": Chase(),
            "attack": Attack(),
            "flee": Flee(),
            "dead": Dead(),
        }, "patrol")

    # --- sensing --------------------------------------------------------
    def sense(self, world):
        """One perception poll per frame. Returns (can_see, position_or_None)."""
        player = world.player
        if not player.alive:
            return False, None
        if (self.perception.in_cone(self.pos, self.facing, player.pos)
                and world.grid.has_line_of_sight(self.pos, player.pos)):
            return True, player.pos
        if self.perception.hears(self.pos, player.pos, player.noise):
            return False, player.pos        # heard, not seen: go look
        return False, None

    # --- movement -------------------------------------------------------
    def set_destination(self, world_pos) -> None:
        self.destination = pg.math.Vector2(world_pos)
        self.goal_cell = None               # forces a fresh path request

    def step_toward(self, target, dt: float, world) -> None:
        desired = pg.math.Vector2(target) - self.pos
        if desired.length_squared() == 0:
            return
        self.vel = desired.normalize() * self.stats.speed
        self.facing = self.vel.normalize()
        self.pos = world.move_with_collision(self, self.pos + self.vel * dt)

    def follow_path(self, dt: float, world) -> bool:
        """Walk the path. Returns True when it has run out."""
        if not self.path:
            return True
        target = world.grid.world_center(self.path[0])
        if self.pos.distance_to(target) < 6.0:
            self.path.pop(0)
            return not self.path
        self.step_toward(target, dt, world)
        return False

    # --- lifecycle ------------------------------------------------------
    def update(self, dt: float, world) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        self.reaction_left = max(0.0, self.reaction_left - dt)
        if self.machine.state.name != "dead" and self.health <= 0:
            self.machine.change("dead")
        self.machine.update(dt, world)
```

`world.move_with_collision` is the swept collision resolution from Chapter 33. `set_destination`
clears `goal_cell` so the pathfinding service (below) knows to schedule a fresh search.

The five states:

```python
class Patrol(EnemyState):
    name = "patrol"

    def enter(self, enemy):
        enemy.anim = "walk"
        enemy.wait = 0.0
        if enemy.waypoints:
            enemy.set_destination(enemy.waypoints[enemy.waypoint_index])

    def update(self, enemy, dt, world):
        sensed, at = enemy.sense(world)
        if sensed:
            enemy.alert = enemy.perception.memory
            enemy.last_known = pg.math.Vector2(at)
            enemy.reaction_left = enemy.stats.reaction       # the "!" beat
            enemy.machine.change("chase")
            return
        if enemy.health <= enemy.stats.flee_below:
            enemy.machine.change("flee")
            return
        if enemy.wait > 0:                                   # pausing at a waypoint
            enemy.wait -= dt
            enemy.vel = pg.math.Vector2()
            return
        if enemy.follow_path(dt, world):
            enemy.wait = 0.8
            enemy.waypoint_index = (enemy.waypoint_index + 1) % max(1, len(enemy.waypoints))
            if enemy.waypoints:
                enemy.set_destination(enemy.waypoints[enemy.waypoint_index])


class Chase(EnemyState):
    name = "chase"

    def enter(self, enemy):
        enemy.anim = "run"
        enemy.repath_timer = 0.0

    def update(self, enemy, dt, world):
        if enemy.health <= enemy.stats.flee_below:
            enemy.machine.change("flee")
            return
        sensed, at = enemy.sense(world)
        if sensed:
            enemy.alert = enemy.perception.memory
            enemy.last_known = pg.math.Vector2(at)
        else:
            enemy.alert -= dt
            if enemy.alert <= 0:
                enemy.last_known = None
                enemy.machine.change("patrol")
                return

        if enemy.reaction_left > 0:                 # still surprised: stand and gawp
            enemy.vel = pg.math.Vector2()
            return

        dist = enemy.pos.distance_to(world.player.pos)
        if dist <= enemy.stats.attack_range and enemy.cooldown <= 0:
            enemy.machine.change("attack")
            return

        enemy.repath_timer -= dt
        if enemy.last_known is not None and enemy.repath_timer <= 0:
            enemy.set_destination(enemy.last_known)
            enemy.repath_timer = 0.4                # four times a second, not sixty
        enemy.follow_path(dt, world)


class Attack(EnemyState):
    name = "attack"

    def enter(self, enemy):
        enemy.anim = "windup"
        enemy.windup = enemy.stats.attack_windup
        enemy.struck = False
        enemy.vel = pg.math.Vector2()

    def update(self, enemy, dt, world):
        enemy.windup -= dt
        if not enemy.struck and enemy.windup <= 0:
            enemy.struck = True
            enemy.anim = "recover"
            world.combat.strike(enemy, world.player, enemy.stats.damage,
                                spread_deg=enemy.stats.accuracy_deg)
            enemy.cooldown = enemy.stats.attack_cooldown
        if enemy.windup <= -enemy.stats.attack_recover:
            enemy.machine.change("chase")


class Flee(EnemyState):
    name = "flee"

    def enter(self, enemy):
        enemy.anim = "run"
        enemy.flee_timer = 4.0
        enemy.path = []

    def update(self, enemy, dt, world):
        enemy.flee_timer -= dt
        if enemy.flee_timer <= 0 or enemy.health > enemy.stats.flee_below * 2:
            enemy.machine.change("patrol")
            return
        away = enemy.pos - world.player.pos
        if away.length_squared() < 1:
            away = pg.math.Vector2(1, 0)
        enemy.step_toward(enemy.pos + away.normalize() * 160, dt, world)


class Dead(EnemyState):
    name = "dead"

    def enter(self, enemy):
        enemy.anim = "death"
        enemy.vel = pg.math.Vector2()
        enemy.solid = False
        enemy.death_timer = 1.2

    def update(self, enemy, dt, world):
        enemy.death_timer -= dt
        if enemy.death_timer <= 0:
            enemy.remove = True
```

Read `Attack` carefully, because it is where fairness lives. The state spends
`attack_windup` seconds doing nothing but playing a wind-up animation — that is the player's
warning. Then it commits: damage happens once (`struck` guards against re-entry), and the enemy is
locked in recovery for `attack_recover` seconds. The enemy cannot cancel, which means a player who
dodged the swing now has a free punish window. Symmetric, learnable, fair.

:::note The dict-of-transitions alternative
For a small number of states, a transition table is more compact and easier to data-drive:

```python
TRANSITIONS = {
    "patrol": [("sees_player", "chase"), ("hurt_badly", "flee"), ("no_health", "dead")],
    "chase":  [("in_attack_range", "attack"), ("lost_player", "patrol"),
               ("hurt_badly", "flee"), ("no_health", "dead")],
    "attack": [("recovered", "chase"), ("no_health", "dead")],
    "flee":   [("safe_again", "patrol"), ("no_health", "dead")],
    "dead":   [],
}

def step_table(machine, enemy, world):
    for check, next_state in TRANSITIONS[machine.state.name]:
        if getattr(enemy, f"can_{check}")(world):
            machine.change(next_state)
            return
```

One line per edge, and the whole graph is readable at a glance. The cost is that the guard
functions pile onto the enemy class, and per-state timers are awkward because there is no `enter`.
Use the table for four states, class-per-state past six, and never a bare string ladder.
:::

:::scenario The enemy vibrates: Chase, Patrol, Chase, Patrol, sixty times a second
A guard stands at the edge of its sight cone. It sees the player, switches to Chase, immediately
steps to a pixel where the cone no longer contains the player, loses sight, and drops back to
Patrol — which turns it around, and it sees the player again. The result is a sprite jittering in
place with its animation restarting every frame.
:::

:::solution Add hysteresis: two different thresholds and a minimum dwell time
Never let a state end on the same condition that started it. Use a wider "give up" threshold than
the "notice" threshold, and refuse to leave a state for its first few frames:

```python
class Chase(EnemyState):
    name = "chase"
    min_dwell = 0.5          # seconds

    def update(self, enemy, dt, world):
        sensed, at = enemy.sense(world)
        if sensed:
            enemy.alert = enemy.perception.memory          # refresh the fuse
        else:
            enemy.alert -= dt

        # Hysteresis: only leave Chase once the fuse has fully burned down
        # AND we have been chasing for at least min_dwell.
        if enemy.alert <= 0 and enemy.machine.time_in_state >= self.min_dwell:
            enemy.last_known = None
            enemy.machine.change("patrol")
            return
```

The `alert` timer is doing double duty here: it is the enemy's belief ("the player was over
there") and the debounce that stops thrash. Three related fixes worth adopting at the same time:

1. **Asymmetric ranges.** Notice at `sight_range`, give up at `sight_range * 1.25`. Never one
   number for both directions.
2. **Minimum dwell per state.** `time_in_state >= 0.5` inside every transition check kills
   oscillation for good.
3. **Evaluate perception once per frame.** If `sense()` is called from three different places,
   you get three different answers in one frame. Poll once, store the result, read it.
:::

## A* pathfinding

Steering gets an enemy across an open room. It walks into walls in a corridor. For that you need a
**search**: given a grid and two cells, find a walkable route.

**A\*** (pronounced "A star") is Dijkstra's algorithm with a sense of direction. It keeps two
numbers per cell:

- **g** — the known cost to reach this cell from the start. Walking cost accumulates.
- **h** — the *heuristic*: an estimate of the cost from this cell to the goal. You compute it,
  cheaply, without searching.
- **f = g + h** — the priority. Small `f` means "promising", so that is what you expand next.

A\* keeps an **open set** (frontier cells worth expanding, held in a priority queue) and a
**closed set** (cells already settled). Pop the lowest `f` from open, expand it, and the first time
you pop the goal you have an optimal path — provided your heuristic never overestimates.

```python
# ai/pathfinding.py
import heapq
import math
from itertools import count

NEIGHBOURS_4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
NEIGHBOURS_8 = NEIGHBOURS_4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
SQRT2 = 1.41421356


def manhattan(a, b) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def octile(a, b) -> float:
    """Correct heuristic when diagonal steps cost sqrt(2)."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (SQRT2 - 1) * min(dx, dy)


def neighbours_of(grid, cell, diagonal: bool = False):
    """Yield (neighbour_cell, step_cost). No corner cutting."""
    x, y = cell
    for dx, dy in (NEIGHBOURS_8 if diagonal else NEIGHBOURS_4):
        nx, ny = x + dx, y + dy
        if not grid.in_bounds(nx, ny) or not grid.is_walkable(nx, ny):
            continue
        if dx and dy and not (grid.is_walkable(x + dx, y) and grid.is_walkable(x, y + dy)):
            continue                      # would squeeze between two wall corners
        yield (nx, ny), SQRT2 if (dx and dy) else 1.0


def astar(grid, start, goal, cost=None, diagonal: bool = False,
          max_expansions: int = 4000) -> list[tuple[int, int]]:
    """Return cells from start to goal inclusive, or [] if there is no route.

    cost(cell) -> float lets you price terrain (mud 3.0, road 0.8). Default 1.0 + neighbour cost.
    """
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))
    if not grid.is_walkable(*start) or not grid.is_walkable(*goal):
        return []
    if start == goal:
        return [start]

    heuristic = octile if diagonal else manhattan
    tie = count()                          # keeps the heap from comparing cells
    open_heap: list[tuple[float, int, tuple[int, int]]] = [(heuristic(start, goal), next(tie), start)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], float] = {start: 0.0}
    closed: set[tuple[int, int]] = set()
    expansions = 0

    while open_heap and expansions < max_expansions:
        _f, _tie, current = heapq.heappop(open_heap)
        if current in closed:
            continue                       # stale duplicate entry; ignore it
        closed.add(current)
        expansions += 1

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for neighbour, step in neighbours_of(grid, current, diagonal):
            if neighbour in closed:
                continue
            terrain = 1.0 if cost is None else cost(neighbour)
            tentative = g_score[current] + step * terrain
            if tentative < g_score.get(neighbour, math.inf):
                came_from[neighbour] = current
                g_score[neighbour] = tentative
                heapq.heappush(open_heap,
                               (tentative + heuristic(neighbour, goal), next(tie), neighbour))
    return []                              # unreachable, or budget exhausted
```

Four details in there are the difference between A\* that works and A\* that lies:

1. **The tie counter.** Without it, Python compares the third tuple element when `f` values match,
   and tuples of ints compare fine — but the moment you store an object there you get a
   `TypeError`. `itertools.count` gives a monotonic tiebreaker and also makes search deterministic.
2. **The `closed` check after popping.** You push the same cell several times with different `g`
   values. Rather than updating the heap (which `heapq` cannot do efficiently), you push a new
   entry and skip the stale ones when they surface. This is the standard trick, and forgetting it
   turns A\* into Dijkstra.
3. **`max_expansions`.** A budget guarantees a frame-time ceiling. A search that fails after 4000
   nodes returns `[]` and the enemy simply walks straight at the player for that frame.
4. **The heuristic must be admissible.** `h` may never exceed the true remaining cost.

That last point is the one people get wrong. Manhattan distance is admissible for 4-directional
movement on a grid where the cheapest step costs 1. Switch on diagonals and Manhattan now
*overestimates* (a diagonal move covers `dx` and `dy` in one step costing 1.414, not 2), so paths
come out slightly wrong — use `octile`. Add terrain where the minimum step cost is 3 and you must
multiply your heuristic by 3 or divide your costs, otherwise A\* stops being optimal. And if you
ever write `h * 1.2` to make the search faster, you have built **weighted A\***: faster, and up to
20% worse paths. That is a legitimate trade for a big open map, but it is a decision, not a
default.

### Path following and path smoothing

Raw A\* output hugs the grid: eight tiny steps to cross a room diagonally. Followed literally, the
enemy zig-zags like it is counting floor tiles. **String pulling** fixes it: from your current
cell, skip ahead to the furthest cell you still have line of sight to, and delete everything
between.

```python
def smooth_path(grid, path):
    """Keep only the corners. O(n^2) worst case in LOS checks; fine for n < 100."""
    if len(path) < 3:
        return list(path)
    out = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not grid.has_line_of_sight(grid.world_center(path[i]),
                                                       grid.world_center(path[j])):
            j -= 1
        out.append(path[j])
        i = j
    return out
```

The inner loop always terminates because `j = i + 1` is adjacent and therefore always visible.
The result is a handful of waypoints that a steering behaviour can follow smoothly — which is the
real lesson: **A\* plans, steering moves.** Pathfinding gives you a coarse route; `seek`/`arrive`
turns it into motion that looks like something a creature would do.

### Recompute only when it matters

Pathfinding is the most expensive thing an enemy does, so it should happen rarely. The rules:

- Recompute when you have no path.
- Recompute when the goal *cell* changes (not when the goal moves slightly within a cell).
- Recompute on a timer — 0.3 to 0.5 seconds while chasing, not every frame.
- Recompute immediately if the next step became unwalkable (a door closed).
- Reuse a path if it is still valid and the goal has not moved.

```python
class PathfinderService:
    """Budgeted, cached A*: a shared resource instead of a per-enemy habit."""

    def __init__(self, grid, budget_per_frame: int = 2, cache_ttl: float = 5.0):
        self.grid = grid
        self.budget = budget_per_frame
        self.cache_ttl = cache_ttl
        self.queue: list = []                     # enemies waiting for a path
        self.cache: dict[tuple, tuple[float, list]] = {}   # (start,goal) -> (age, path)
        self.grid_version = grid.version if hasattr(grid, "version") else 0

    def request(self, enemy, goal_cell) -> None:
        start = self.grid.cell_at(enemy.pos)
        goal = (int(goal_cell[0]), int(goal_cell[1]))
        if enemy.goal_cell == goal and enemy.path:
            return                                # same goal, still walking: nothing to do
        enemy.goal_cell = goal
        cached = self.cache.get((start, goal))
        if cached and cached[0] < self.cache_ttl:
            enemy.path = smooth_path(self.grid, cached[1])
            return
        if enemy not in self.queue:
            self.queue.append(enemy)

    def update(self, dt: float) -> None:
        version = getattr(self.grid, "version", 0)
        if version != self.grid_version:          # a door opened: everything is stale
            self.grid_version = version
            self.cache.clear()

        for (key, (age, _path)) in list(self.cache.items()):
            new_age = age + dt
            if new_age > self.cache_ttl:
                del self.cache[key]
            else:
                self.cache[key] = (new_age, _path)

        done = 0
        while self.queue and done < self.budget:
            enemy = self.queue.pop(0)
            start = self.grid.cell_at(enemy.pos)
            goal = enemy.goal_cell
            path = astar(self.grid, start, goal)
            self.cache[(start, goal)] = (0.0, path)
            enemy.path = smooth_path(self.grid, path)
            done += 1
```

`budget_per_frame = 2` means that with forty enemies all repathing at once, the work spreads over
twenty frames instead of blowing one. Nobody notices a guard hesitating for a fifth of a second;
everybody notices a dropped frame.

:::pitfall Recomputing A* for every enemy every frame
This is the single most common performance bug in hobby games. A 64x48 tilemap has 3072 cells; a
typical search touches a few hundred of them and allocates a dict entry, a heap tuple, and a
`count()` object per node. Sixty enemies at sixty frames per second is 3600 searches per second —
hundreds of thousands of allocations, all garbage collected while you are trying to render.
Symptom: the game runs at 60 fps with three enemies and 14 fps with thirty.

Three fixes, in order of preference:

1. **Throttle.** Repath on a 0.3–0.5 s timer, and only when the goal *cell* changes.
2. **Stagger.** A `PathfinderService` with a per-frame budget spreads the cost.
3. **Cache.** Key on `(start_cell, goal_cell)` with a short TTL, and invalidate when the map
   changes (`grid.version`).

And cap the search: `max_expansions=4000` turns a pathological case into a slightly dumb enemy
instead of a hung frame.
:::

## Tuning: making enemies fair

You now have an enemy that is *optimal*, which is to say unpleasant. Tuning is where you
deliberately make it worse in specific, legible ways.

```python
@dataclass
class Tuning:
    reaction: float = 0.22        # seconds of surprise before the enemy acts
    aim_error_deg: float = 4.0    # random cone applied to shots and lunges
    grace_frames: int = 12        # player invulnerability after being hit (at 60fps)
    windup_scale: float = 1.0     # multiplies every telegraph duration
    repath_interval: float = 0.4
```

| | Easy | Normal | Hard |
|---|---|---|---|
| Reaction time | 0.40 s | 0.22 s | 0.10 s |
| Aim error | 9° | 4° | 1° |
| Attack wind-up x | 1.5 | 1.0 | 0.8 |
| Sight range | x0.8 | x1.0 | x1.2 |
| Player i-frames | 18 frames | 12 frames | 8 frames |
| Repath interval | 0.6 s | 0.4 s | 0.25 s |

Notice that *nothing in that table makes the AI smarter*. Hard mode does not run a better
algorithm; it runs the same algorithm with less slack. That is deliberate: the player is learning
one enemy, not three. And note the two entries that give the player agency — wind-up duration and
i-frames — rather than taking it away. A longer telegraph on easy is a teaching tool; shorter
i-frames on hard is a punishment. Prefer the first.

The general shape of a fair enemy:

1. **Telegraph.** A visible, un-cancellable wind-up before anything that costs the player health.
2. **Recovery.** A window after attacking where the enemy is vulnerable. Punish the player's
   dodges with opportunities, not with extra damage.
3. **Reaction.** A beat of surprise on first sighting, so ambushes are winnable.
4. **Grace.** i-frames after a hit, so a stun-lock cannot kill.

## Behaviour trees: the upgrade

A state machine has one structural weakness: transitions are edges between states, so with N
states you can end up with N² edges, and a new behaviour often means touching many of them. A
**behaviour tree** replaces that with a tree of small nodes that return one of three statuses:
`SUCCESS`, `FAILURE`, or `RUNNING`. The tree is re-ticked from the root every frame, so priority is
expressed by *order* rather than by wiring.

```python
# ai/behaviour.py
SUCCESS, FAILURE, RUNNING = "success", "failure", "running"


class Node:
    def tick(self, bb) -> str:
        raise NotImplementedError


class Sequence(Node):
    """AND: run children in order; fail fast. The 'if A then B' of behaviour trees."""

    def __init__(self, *children):
        self.children = children
        self.index = 0

    def tick(self, bb) -> str:
        while self.index < len(self.children):
            result = self.children[self.index].tick(bb)
            if result == RUNNING:
                return RUNNING
            if result == FAILURE:
                self.index = 0            # reset for next tick
                return FAILURE
            self.index += 1
        self.index = 0
        return SUCCESS


class Selector(Node):
    """OR: first child that does not fail wins. Priority falls out of ordering."""

    def __init__(self, *children):
        self.children = children

    def tick(self, bb) -> str:
        for child in self.children:
            result = child.tick(bb)
            if result != FAILURE:
                return result
        return FAILURE


class Check(Node):
    def __init__(self, predicate):
        self.predicate = predicate

    def tick(self, bb) -> str:
        return SUCCESS if self.predicate(bb) else FAILURE


class Do(Node):
    def __init__(self, action):
        self.action = action

    def tick(self, bb) -> str:
        return self.action(bb)
```

Used like this:

```python
guard_tree = Selector(
    Sequence(Check(lambda bb: bb.health < bb.stats.max_health * 0.25),
             Do(lambda bb: bb.flee())),
    Sequence(Check(lambda bb: bb.can_see_player and bb.distance_to_player < 48),
             Do(lambda bb: bb.attack())),
    Sequence(Check(lambda bb: bb.alert > 0),
             Do(lambda bb: bb.investigate())),
    Do(lambda bb: bb.patrol()),
)
```

Read it top to bottom: flee if hurt, else attack if close, else investigate a remembered
sighting, else patrol. Adding a "call for help" behaviour is one new `Sequence` inserted in
priority order — no edges to rewire.

:::warning Behaviour trees are not automatically better
For a five-state enemy, a tree adds indirection and a per-frame allocation of tick results for no
benefit. Reach for a tree when you have a dozen behaviours with shared sub-parts (every enemy
needs "reload", "take cover", "call allies"), or when you want to author behaviour in data
instead of Python. Also note the `RUNNING` bookkeeping: a naive `Sequence` that restarts from
index 0 every tick will re-run its conditions each frame, which is usually what you want, but it
means a long-running action must return `RUNNING` or it will never finish.
:::

## Performance: stop asking every enemy about every enemy

Separation, cohesion, and "who is near me" are all neighbour queries. The obvious implementation
compares every pair:

```python
# O(n^2). Fine at 20 entities, fatal at 300.
for a in enemies:
    for b in enemies:
        if a is not b and a.pos.distance_to(b.pos) < 48:
            ...
```

**Spatial hashing** fixes it. Bucket entities into grid cells; to find neighbours, look at the
nine cells around you (or however many your query radius covers) and ignore the rest of the
world.

```python
# ai/spatial.py
from collections import defaultdict


class SpatialHash:
    """Uniform grid buckets. Insert is O(1); query is O(entities in nearby cells)."""

    def __init__(self, cell_size: float = 64.0):
        self.cell_size = cell_size
        self.buckets: dict[tuple[int, int], list] = defaultdict(list)

    def clear(self) -> None:
        self.buckets.clear()

    def _key(self, pos) -> tuple[int, int]:
        return (int(pos[0] // self.cell_size), int(pos[1] // self.cell_size))

    def insert(self, entity) -> None:
        self.buckets[self._key(entity.pos)].append(entity)

    def rebuild(self, entities) -> None:
        self.clear()
        for e in entities:
            self.insert(e)

    def query(self, pos, radius: float = 0.0):
        """Yield candidates in every cell the query circle touches."""
        cs = self.cell_size
        x0, x1 = int((pos[0] - radius) // cs), int((pos[0] + radius) // cs)
        y0, y1 = int((pos[1] - radius) // cs), int((pos[1] + radius) // cs)
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                yield from self.buckets.get((cx, cy), ())
```

Choose `cell_size` near your largest query radius: too small and you scan many empty cells, too
large and each cell holds half the map. For a 48-pixel separation radius, 64 is a good default.

| Entities | Pairwise checks/frame | Hash checks/frame (cell 64, r 48) |
|---|---|---|
| 50 | 2,500 | ~450 |
| 200 | 40,000 | ~1,800 |
| 500 | 250,000 | ~4,500 |

Rebuild the hash once per frame (`rebuild` is O(n)); every query that frame is then nearly free.
Do not rebuild per query — that is worse than the pairwise loop you were replacing.

Two more habits that matter at this scale:

- Avoid allocating `Vector2` objects inside inner loops when you can precompute. `length_squared()`
  on an existing vector is cheap; `Vector2(a) - Vector2(b)` per pair is not.
- Cache distances you will use twice. `distance_to` is a square root; `distance_squared_to` is not.

## Debugging AI

You cannot debug what you cannot see, and AI bugs are invisible by construction. Make the
invisible state drawable and bind it to a key.

```python
def draw_ai_debug(surface, enemy, world, camera, font) -> None:
    """F1 toggle. Draws senses, path, and state for one enemy."""
    origin = camera.apply(enemy.pos)

    # 1. sight cone: two rays at +/- fov/2 around the facing direction
    p = enemy.perception
    half = p.fov / 2
    for sign in (-1, 1):
        ray = enemy.facing.rotate(sign * half) * p.sight_range
        pg.draw.line(surface, (90, 200, 255), origin, camera.apply(enemy.pos + ray), 1)

    # 2. alert state: yellow while it still "remembers" the player
    if enemy.alert > 0 and enemy.last_known is not None:
        pg.draw.line(surface, (255, 220, 60), origin, camera.apply(enemy.last_known), 1)
        pg.draw.circle(surface, (255, 220, 60), camera.apply(enemy.last_known), 6, 1)

    # 3. the smoothed path it is walking
    if len(enemy.path) > 1:
        pts = [(int(p2.x), int(p2.y))
               for p2 in (camera.apply(world.grid.world_center(c)) for c in enemy.path)]
        pg.draw.lines(surface, (120, 255, 160), False, pts, 2)

    # 4. the state name over its head
    label = font.render(f"{enemy.machine.state.name} hp={enemy.health}", True, (255, 255, 255))
    surface.blit(label, (origin.x - label.get_width() / 2, origin.y - 34))
```

```python
# in the scene's handle_event
if event.type == pg.KEYDOWN and event.key == pg.K_F1:
    self.show_ai_debug = not self.show_ai_debug
```

Four overlays, and the four most common bugs become obvious instantly: the cone shows why it did
not see you, the yellow line shows that it is chasing a stale position, the path shows a route
through a wall (your `is_walkable` and your collision disagree), and the state name shows it
thrashing between two states.

:::scenario The enemy shot me through a wall
Playtesters report that a guard in the next room kills them through solid rock. The perception
code looks correct: range check, cone check, then line of sight.
:::

:::solution The bug is almost always one of three mismatches
1. **World vs cell coordinates.** The cone test runs in pixels, the LOS test in cells. If
   `cell_at` uses `round` instead of floor division, or the grid's `tile_size` disagrees with the
   tilemap you actually render, LOS is being tested between two cells that are not where the
   sprites are. Print `grid.cell_at(enemy.pos)` and `grid.cell_at(player.pos)` for one frame and
   compare them against what you see on screen.
2. **Bresenham slipping a diagonal.** Two walls touching corner-to-corner leave a mathematical
   gap; Bresenham's line goes through it and reports clear sight. Switch the *perception* test to
   `has_line_of_sight_sampled`, or disallow diagonal wall gaps in the generator.
3. **Stale alert plus a straight-line move.** The enemy is not seeing through the wall; it saw
   you two seconds ago, remembered `last_known`, and is now standing next to you while its
   `alert` timer is still counting down. That is *correct* behaviour and only feels wrong because
   `memory` is too long. Drop it from 3.5 s to 2.0 s, or clear `last_known` when the enemy gets
   within 20 pixels of it and finds nobody there.

The fourth possibility is the real one to internalise: the attack never checked LOS at all. Put
the visibility test in the *attack* transition, not only in the chase transition, so an enemy
cannot fire at a target it merely remembers.
:::

## Key takeaways

- Game AI is hand-authored rules for sensing, deciding, and moving — not machine learning.
- Steering behaviours produce a desired velocity; `force = desired - current`, clamped, integrates
  into smooth motion. Combine them by adding weighted forces.
- Never normalise a zero vector; guard with `length_squared() > 0`.
- Perception needs four parts: range cone, line of sight, hearing scaled by noise, and an alert
  memory timer that doubles as a debounce against state thrash.
- A finite state machine with `enter`/`update`/`exit` per state scales to a dozen states; a
  transition table is fine below that.
- A\* ranks cells by `f = g + h`, expands the lowest `f` from a `heapq`, and is optimal only while
  `h` never overestimates (Manhattan for 4-way, octile with diagonals).
- Throttle, stagger, and cache pathfinding; A\* per enemy per frame is the classic frame-rate
  killer.
- Fairness is tuning, not intelligence: telegraphs, recovery windows, reaction time, and i-frames.
- Spatial hashing turns O(n²) neighbour queries into O(neighbours); rebuild once per frame.
- Draw the cone, the path, the remembered position, and the state name. AI bugs are invisible
  until you render them.

## Practice

- [ ] Build a single-file demo: one agent that `seek`s the mouse cursor, and switch to `arrive`
      with the spacebar so you can feel the difference.
- [ ] Give a patrol guard three waypoints and an alert memory timer. When it loses sight of the
      player, it must walk to `last_known` before returning to patrol.
- [ ] Add terrain costs to `astar`: a `cost(cell)` function that makes mud (tile id 3) three times
      more expensive than floor, and verify the path visibly avoids it.
- [ ] Implement `smooth_path` and print `len(path)` before and after on ten random start/goal
      pairs. Report the average reduction.
- [ ] Add a `SpatialHash` to a scene with 200 wandering agents using separation, and measure frame
      time with and without it.
- [ ] Convert the five-state guard FSM into the behaviour tree from this chapter, keeping the
      `alert` hysteresis as a `Check` node.

## Solutions

:::solution Exercise 1
```python
import pygame as pg
from steering import Agent

pg.init()
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()
agent = Agent((400, 300), max_speed=220.0)
use_arrive = False
running = True

while running:
    dt = clock.tick(60) / 1000.0
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            use_arrive = not use_arrive

    target = pg.math.Vector2(pg.mouse.get_pos())
    force = agent.arrive(target, slow_radius=120) if use_arrive else agent.seek(target)
    agent.integrate(force, dt)

    screen.fill((18, 18, 24))
    pg.draw.circle(screen, (255, 90, 90), (int(target.x), int(target.y)), 6)
    pg.draw.circle(screen, (120, 220, 255), (int(agent.pos.x), int(agent.pos.y)), 10)
    pg.display.flip()
```
Seek overshoots and orbits the cursor because it always travels at full speed and must loop back.
Arrive ramps speed down inside `slow_radius` and settles. `dt` comes from `clock.tick(60)`, so
behaviour is identical on a 144 Hz display — that is the whole reason Chapter 31 insisted on delta
time.
:::

:::solution Exercise 2
```python
class Searching(EnemyState):
    """Heard or lost something: walk to the last known position, look around, give up."""
    name = "searching"

    def enter(self, enemy):
        enemy.anim = "walk"
        if enemy.last_known is not None:
            enemy.set_destination(enemy.last_known)
        enemy.search_timer = 2.0

    def update(self, enemy, dt, world):
        sensed, at = enemy.sense(world)
        if sensed:
            enemy.alert = enemy.perception.memory
            enemy.last_known = pg.math.Vector2(at)
            enemy.machine.change("chase")
            return

        if enemy.follow_path(dt, world):
            # Arrived at the remembered spot and found nobody: look around, then forget.
            enemy.search_timer -= dt
            enemy.vel = pg.math.Vector2()
            enemy.facing = enemy.facing.rotate(120 * dt)     # sweep the head
            if enemy.search_timer <= 0:
                enemy.last_known = None
                enemy.alert = 0.0
                enemy.machine.change("patrol")
```
Wire it in by changing Chase's "lost the player" branch to `machine.change("searching")` instead
of going straight back to patrol. The enemy now plays out the belief it already had, which is the
behaviour players read as "that guard is smart". Keep `alert` ticking down during the search too,
so a long search and a lost trail both expire.
:::

:::solution Exercise 3
```python
TERRAIN_COST = {FLOOR: 1.0, DOOR: 1.2, 3: 3.0}      # 3 == mud


def mud_cost(grid):
    def cost(cell):
        return TERRAIN_COST.get(grid.tiles[cell[1]][cell[0]], 1.0)
    return cost


path = astar(grid, start, goal, cost=mud_cost(grid))
```
Because the cheapest step is still 1.0, Manhattan remains admissible and paths stay optimal. If
you later make the *minimum* terrain cost 3.0 (say every floor tile costs 3), you must scale the
heuristic by 3 as well, or A\* will happily return a path that is longer than necessary. Never mix
an unscaled heuristic with a scaled cost function.
:::

:::solution Exercise 4
```python
import random

total_raw = total_smooth = 0
rng = random.Random(7)
for _ in range(10):
    while True:
        a = (rng.randrange(grid.width), rng.randrange(grid.height))
        b = (rng.randrange(grid.width), rng.randrange(grid.height))
        if grid.is_walkable(*a) and grid.is_walkable(*b):
            break
    raw = astar(grid, a, b)
    smooth = smooth_path(grid, raw)
    total_raw += len(raw)
    total_smooth += len(smooth)
    print(f"{a} -> {b}: {len(raw)} cells -> {len(smooth)} waypoints")

print(f"average {total_raw / 10:.1f} -> {total_smooth / 10:.1f}")
```
On an open dungeon you typically see a 5–10x reduction, because long straight runs collapse to a
single waypoint. Two caveats worth checking yourself: if the reduction is 1x your `is_walkable`
probably disagrees with `has_line_of_sight` (a door tile that blocks sight but not movement will
do it), and if `smooth_path` ever returns a path longer than the input, your LOS test is
asymmetric — check both directions.
:::

:::solution Exercise 5
```python
import time

def measure(entities, use_hash):
    grid_hash = SpatialHash(cell_size=64)
    for _ in range(120):                      # 120 simulated frames
        t0 = time.perf_counter()
        if use_hash:
            grid_hash.rebuild(entities)
            forces = [separation(a, list(grid_hash.query(a.pos, 48))) for a in entities]
        else:
            forces = [separation(a, entities) for a in entities]
        for a, f in zip(entities, forces):
            a.integrate(f, 1 / 60)
        elapsed = time.perf_counter() - t0
        yield elapsed

agents = [Agent((random.uniform(0, 1280), random.uniform(0, 720))) for _ in range(200)]
print("pairwise:", sum(measure(agents, False)))
print("hashed  :", sum(measure(agents, True)))
```
Expect the hashed version to be several times faster at 200 agents, and the gap to widen as you
add more. The important thing is the shape of the curve, not the absolute numbers: pairwise cost
grows quadratically, hashed cost grows roughly linearly. If the hashed version is *slower*, your
`cell_size` is wrong — try 48 or 96 and re-measure.
:::

:::solution Exercise 6
```python
def build_guard_tree(enemy):
    bb = enemy                                # the enemy is the blackboard
    return Selector(
        Sequence(Check(lambda e: e.health <= 0), Do(lambda e: e.set_state("dead"))),
        Sequence(Check(lambda e: e.health <= e.stats.flee_below),
                 Do(lambda e: e.set_state("flee"))),
        Sequence(Check(lambda e: e.can_see_player and e.dist_to_player <= e.stats.attack_range
                       and e.cooldown <= 0),
                 Do(lambda e: e.set_state("attack"))),
        Sequence(Check(lambda e: e.can_see_player or e.alert > 0),
                 Do(lambda e: e.set_state("chase"))),
        Do(lambda e: e.set_state("patrol")),
    )


class Enemy:                                  # in update()
    def update(self, dt, world):
        self.poll_senses(world)               # ONCE per frame: can_see_player, dist_to_player
        self.tree.tick(self)
        self.states[self.current_state].update(self, dt, world)
```
The clean way to migrate is a hybrid: the tree picks the *state*, and each state keeps its
`enter`/`update`/`exit` code untouched. You get priority-by-ordering without rewriting behaviours,
and `RUNNING` bookkeeping disappears because the state machine still owns continuity. The
`alert > 0` check in the fourth `Sequence` is the hysteresis — the tree cannot drop below it while
the enemy still remembers you.
:::
