import gc, weakref


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.parent = None


print("=== a list registry (the leak)")


def make_tree():
    root = Node("root")
    child = Node("child")
    child.parent = root
    root.children.append(child)
    return root


registry = []
for _ in range(100):
    registry.append(make_tree())

print("  gc.collect() freed   ->", gc.collect(), "objects")
print("  registry holds       ->", len(registry), "roots")
print("  so the trees are NOT garbage: they are reachable from registry")
print()

print("=== a WeakSet registry (the fix)")
weak_registry = weakref.WeakSet()
for _ in range(100):
    weak_registry.add(make_tree())

print("  gc.collect() freed   ->", gc.collect(), "objects")
print("  weak_registry holds  ->", len(weak_registry), "roots")
print("  nothing else referred to the trees, so they were freed and the")
print("  WeakSet dropped them on its own")
