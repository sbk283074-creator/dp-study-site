"""Chapter 33 -- a scene stack decides what still runs when something is on top.

Five configurations of the same stack. The count is of scenes that update, of
scenes that draw, and of pops the stack refuses.
"""


class Scene:
    def __init__(self, name, blocks_update, blocks_draw):
        self.name = name
        self.blocks_update = blocks_update
        self.blocks_draw = blocks_draw


class Stack:
    def __init__(self, scenes):
        self.scenes = list(scenes)
        self.refused = 0

    def pop(self):
        if len(self.scenes) <= 1:
            self.refused += 1
            return None
        return self.scenes.pop()

    def update_list(self):
        """A scene updates unless something above it blocks the update."""
        running = []
        for index, scene in enumerate(self.scenes):
            above = self.scenes[index + 1:]
            if not any(other.blocks_update for other in above):
                running.append(scene.name)
        return running

    def draw_list(self):
        """A scene draws unless something above it is opaque."""
        visible = []
        for index, scene in enumerate(self.scenes):
            above = self.scenes[index + 1:]
            if not any(other.blocks_draw for other in above):
                visible.append(scene.name)
        return visible


play = Scene("play", True, True)
pause_opaque = Scene("pause", True, True)
pause_see_through = Scene("pause", True, False)
hud = Scene("hud", False, False)
settings = Scene("settings", True, True)

configs = [
    ("one scene", [play]),
    ("pause on top, opaque", [play, pause_opaque]),
    ("pause on top, see-through", [play, pause_see_through]),
    ("settings over a pause", [play, pause_opaque, settings]),
    ("hud over play", [play, hud]),
]

rows = []
for label, scenes in configs:
    stack = Stack(scenes)
    rows.append((label, len(scenes), stack.update_list(), stack.draw_list()))

# The stack refuses to pop its last scene, however often it is asked.
floor = Stack([play])
for _ in range(3):
    floor.pop()

print(f"{len(configs)} configurations of a scene stack")
print()
print(f"{'configuration':<28}{'scenes':>8}{'update':>9}{'draw':>7}")
print("-" * 52)
for label, count, updates, draws in rows:
    print(f"{label:<28}{count:>8}{len(updates):>9}{len(draws):>7}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'configurations tried':<46}{len(configs):>8}")
print(f"{'scenes on the stack, largest':<46}"
      f"{max(count for _, count, _, _ in rows):>8}")
print(f"{'scenes updating, largest stack':<46}{len(rows[3][2]):>8}")
print(f"{'scenes drawing, largest stack':<46}{len(rows[3][3]):>8}")
print(f"{'scenes updating, see-through pause':<46}{len(rows[2][2]):>8}")
print(f"{'scenes drawing, see-through pause':<46}{len(rows[2][3]):>8}")
print(f"{'scenes drawing, opaque pause':<46}{len(rows[1][3]):>8}")
print(f"{'scenes updating, hud over play':<46}{len(rows[4][2]):>8}")
print(f"{'pops refused on the last scene':<46}{floor.refused:>8}")

print()
print("The two pause rows are the same scene with one flag changed, and they")
print("differ in exactly the way the flag says. An opaque pause stops the play")
print("scene drawing; a see-through one does not, so the world stays visible")
print("behind the menu while the game is still paused. In both cases the play")
print("scene stops updating, because that is what pausing means.")
print()
print("The hud row is the one that shows why there are two flags rather than")
print("one. A heads-up display that blocks nothing leaves the scene below it")
print("updating and drawing, so the stack is an overlay rather than a mode")
print("change. With a single 'opaque' flag the two cases cannot be told apart,")
print("and a status bar would silently pause the game underneath it.")
print()
print("And the number that does not change: with three scenes on the stack,")
print("exactly one updates. A stack does not mean 'run everything'; it means")
print("the top scene decides, and the scenes below are there to be drawn or")
print("resumed rather than to run. That is why the pop needs a floor -- popping")
print("the last scene leaves the frame with no owner, so the operation has to")
print("be refused rather than allowed, and the refusal belongs in the stack")
print("rather than in every caller.")
