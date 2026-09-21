import tracemalloc


class WithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WithSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


def footprint(cls, n):
    """Total bytes still allocated for n instances of cls."""
    tracemalloc.start()
    objs = [cls(1, 2) for _ in range(n)]
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del objs
    return current


N = 200_000
d = footprint(WithDict, N)
s = footprint(WithSlots, N)

print(f"  {N:,} objects, measured with tracemalloc")
print(f"  WithDict  -> {d:>10,} bytes   ({d / N:5.1f} per object)")
print(f"  WithSlots -> {s:>10,} bytes   ({s / N:5.1f} per object)")
print(f"  saved     -> {d - s:>10,} bytes")
print()
print("the saving is the per-instance __dict__, which slots removes:")
print("  hasattr(a, '__dict__') ->", hasattr(WithDict(1, 2), "__dict__"))
print("  hasattr(b, '__dict__') ->", hasattr(WithSlots(1, 2), "__dict__"))
print()
print("and what it costs -- the class can no longer gain attributes:")
try:
    WithSlots(1, 2).z = 3
except AttributeError as exc:
    print("  b.z = 3 ->", exc)
print()
print("That is the whole trade: no __dict__ means no room for a new")
print("attribute. At 200,000 objects it is eight megabytes.")
