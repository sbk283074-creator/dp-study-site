class Node:
    def __init__(self, name):
        self.name = name
        self.children = []


print("shape 1: a container that only ever grows")
root = Node("root")
seen = []
for i in range(1000):
    child = Node(f"c{i}")
    root.children.append(child)
    seen.append(child)
print("  root.children ->", len(root.children), "  seen ->", len(seen))
print("  every child is alive because two containers point at it")
print()

print("shape 2: a closure that keeps everything it ever computed")
def make_counter(seed):
    history = [seed]
    def counter():
        history.append(history[-1] + 1)
        return history[-1]
    return counter


c = make_counter(0)
for _ in range(5):
    c()
print("  c() ->", c())
print("  the closure still holds the whole history ->",
      c.__closure__[0].cell_contents)
print()

print("shape 3: an exception holding a traceback, which holds a frame")
def boom():
    payload = [0] * 1000
    raise ValueError("captured")


held = None
try:
    boom()
except ValueError as exc:
    held = exc
print("  held.__traceback__ ->", type(held.__traceback__).__name__)
print("  the frame it holds still has its locals ->",
      list(held.__traceback__.tb_next.tb_frame.f_locals))
print("  so `payload` -- a thousand elements -- is alive as long as `held` is")
print()
print("none of these is a bug on its own. Each is a reference you did not")
print("notice you were keeping, which is what a leak in Python looks like.")
