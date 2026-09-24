"""Chapter 35 -- seek drives at the target; arrive decides to stop.

One enemy, one target, two steering behaviours. The count is of steps taken, of
steps spent inside the arrival radius, and of how far past the target it went.
"""

TARGET = 100.0
MAX_SPEED = 5.0
ACCEL = 1.0
SLOW_RADIUS = 20.0
STEPS = 200


def run(mode):
    pos = 0.0
    vel = 0.0
    first_inside = None
    settled = None
    overshoot = 0.0
    inside_steps = 0
    for step in range(1, STEPS + 1):
        diff = TARGET - pos
        if mode == "arrive" and abs(diff) < SLOW_RADIUS:
            desired = MAX_SPEED * diff / SLOW_RADIUS
        else:
            desired = MAX_SPEED if diff > 0 else -MAX_SPEED
        steer = max(-ACCEL, min(ACCEL, desired - vel))
        vel += steer
        pos += vel
        overshoot = max(overshoot, pos - TARGET)
        if abs(TARGET - pos) <= 1.0:
            inside_steps += 1
            if first_inside is None:
                first_inside = step
        if abs(TARGET - pos) <= 0.5:
            if settled is None:
                settled = step
        else:
            settled = None
    return pos, vel, first_inside, settled, overshoot, inside_steps


rows = [(mode, run(mode)) for mode in ("seek", "arrive")]

print(f"one enemy, target at {TARGET:.0f}, max speed {MAX_SPEED:.0f}, "
      f"acceleration {ACCEL:.0f}")
print()
print(f"{'behaviour':<14}{'first within 1':>16}{'settles at':>13}"
      f"{'overshoot':>12}{'final error':>14}")
print("-" * 69)
for mode, (pos, _, first, settled, over, _) in rows:
    print(f"{mode:<14}{str(first):>16}{str(settled):>13}"
          f"{over:>12.1f}{abs(TARGET - pos):>14.1f}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'steps simulated':<46}{STEPS:>8}")
for mode, (_, _, first, settled, over, inside) in rows:
    print(f"{'steps before ' + mode + ' first reaches':<46}{first:>8}")
for mode, (_, _, _, settled, _, _) in rows:
    print(f"{'steps before ' + mode + ' settles':<46}"
          f"{(settled if settled is not None else STEPS):>8}")
for mode, (_, _, _, _, _, inside) in rows:
    print(f"{'steps spent inside the radius, ' + mode:<46}{inside:>8}")
for mode, (_, _, _, _, over, _) in rows:
    print(f"{'overshoot past the target, ' + mode:<46}{round(over):>8}")

print()
print("Both behaviours cross the target and neither of them stops there, which")
print("is the whole problem. Steering is a force, and a force that always points")
print("at the target will always be pointing at it from the other side one step")
print("later. The enemy does not arrive; it orbits.")
print()
print("What separates the two rows is the decision to slow down. `arrive` scales")
print("the desired speed by how close it is, so the last few units are crossed")
print("at a speed the enemy can actually shed, and it settles. `seek` has one")
print("speed and keeps it, so the same force that accelerated it now has to undo")
print("all of it -- and it spends the rest of the simulation doing that.")
print()
print("The last two columns are the ones to tune against. Overshoot is what the")
print("player sees as an enemy running past them, and final error is what the")
print("code sees as a failure to reach. A behaviour that is correct on average")
print("and oscillating at the end is the most common bug in a steering system,")
print("and it is invisible in a screenshot -- which is why the arrival radius is")
print("a number in the code rather than a feeling in the design document.")
