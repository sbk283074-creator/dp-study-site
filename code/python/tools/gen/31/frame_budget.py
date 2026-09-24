"""Chapter 31 -- a frame rate cap is arithmetic, and the loop is where it lives.

Two seconds of game loop at three frame rates, with frames counted rather than
timed. The count is of frames drawn, and of update steps a fixed timestep runs.
"""

MILLISECONDS = 2000
RATES = [30, 60, 144]
STEP_MS = 16


def frames(rate):
    return MILLISECONDS * rate // 1000


def steps():
    return MILLISECONDS // STEP_MS


def per_frame(rate):
    return f"{steps() / frames(rate):.2f}"


fixed_steps = steps()

print(f"{MILLISECONDS} milliseconds of loop, fixed update step of {STEP_MS} ms")
print()
print(f"{'frame rate':<14}{'frames drawn':>14}{'update steps':>14}"
      f"{'ms per frame':>14}")
print("-" * 56)
for rate in RATES:
    print(f"{rate:<14}{frames(rate):>14}{fixed_steps:>14}{1000 // rate:>14}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'milliseconds simulated':<46}{MILLISECONDS:>8}")
for rate in RATES:
    print(f"{'frames drawn at ' + str(rate) + ' fps':<46}{frames(rate):>8}")
print(f"{'update steps, at every frame rate':<46}{fixed_steps:>8}")
for rate in RATES:
    print(f"{'updates per frame at ' + str(rate) + ' fps':<46}{per_frame(rate):>8}")

print()
print("The row that does not move is the point. Two seconds of loop performs")
print(f"{fixed_steps} update steps whether the machine draws 60 frames or 288, because the")
print("update is driven by elapsed time and a fixed step rather than by the")
print("frame. That is what makes the simulation reproducible: the same input")
print("sequence produces the same positions on a laptop and on a desktop, and a")
print("replay is a list of inputs rather than a recording of a session.")
print()
print("The cost is visible in the last rows and it is paid at the slow end. At")
print(f"30 fps each frame runs {per_frame(30)} updates, so the drawing and the simulation")
print("are competing for the same frame. At 144 fps each frame runs")
print(f"{per_frame(144)} of an update, so most frames draw a world that has not changed")
print("since the last one. Neither is wrong -- they are the two ends of the")
print("same trade, and the fixed step is what lets you choose where to sit.")
print()
print("What it does not do is remove the need for a cap. A loop that runs")
print("free will render as fast as the machine allows, which is 288 frames of")
print("work for 125 frames of state, and it will spin a laptop fan to do it.")
print("The cap is not there to make the game smooth; it is there to stop the")
print("loop spending a resource that buys nothing.")
