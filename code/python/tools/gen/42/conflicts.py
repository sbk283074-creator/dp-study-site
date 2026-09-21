from functools import cached_property


print("1. cached_property caches by writing into the instance __dict__")
print("   a class with __slots__ and no __dict__ has nowhere to put it:")


class WithSlots:
    __slots__ = ("rows",)

    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def summary(self):
        return sum(self.rows)


try:
    WithSlots([1, 2, 3]).summary
except TypeError as exc:
    print("   TypeError:", exc)
print()


print("2. adding __dict__ to __slots__ fixes it, and gives back the memory")
print("   you were trying to save:")


class WithBoth:
    __slots__ = ("rows", "__dict__")

    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def summary(self):
        return sum(self.rows)


w = WithBoth([1, 2, 3])
print("   summary  ->", w.summary)
print("   __dict__ ->", w.__dict__)
print()


print("3. the expensive version of the same rule: an instance attribute")
print("   that shadows a method, because a function is a NON-data")
print("   descriptor and loses to the instance dict")


class Cart:
    def __init__(self, items):
        self.items = items

    def total(self):
        return sum(self.items)


c = Cart([1, 2, 3])
print("   c.total() ->", c.total())

c.total = 6.0
print("   after c.total = 6.0, c.total ->", c.total)
try:
    c.total()
except TypeError as exc:
    print("   c.total() ->", exc)
print()

print("4. a property cannot be shadowed, because it is a DATA descriptor")


class SafeCart:
    def __init__(self, items):
        self.items = items

    @property
    def total(self):
        return sum(self.items)


s = SafeCart([1, 2, 3])
print("   s.total ->", s.total)
try:
    s.total = 6.0
except AttributeError as exc:
    print("   s.total = 6.0 ->", exc)
print("   the mistake is impossible rather than merely discouraged")
