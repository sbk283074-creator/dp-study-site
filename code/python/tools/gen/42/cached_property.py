from functools import cached_property


class my_cached_property:
    def __init__(self, func):
        self.func = func
        self.attrname = None

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.attrname] = value
        return value


class Dataset:
    def __init__(self, rows):
        self.rows = rows
        self.computations = 0

    @my_cached_property
    def summary(self):
        self.computations += 1
        return f"n={len(self.rows)} sum={sum(self.rows)}"


d = Dataset([1, 2, 3, 4])
print("first  access ->", d.summary)
print("second access ->", d.summary)
print("third  access ->", d.summary)
print("the expensive function ran", d.computations, "time(s)")
print()
print("d.__dict__ ->", d.__dict__)
print()
print("From the second access on, the descriptor is never consulted:")
print("the value is in the instance dict, and a NON-data descriptor")
print("loses to the instance dict. The cache IS the shadowing rule.")
print()


class Same:
    def __init__(self, rows):
        self.rows = rows
        self.computations = 0

    @cached_property
    def summary(self):
        self.computations += 1
        return f"n={len(self.rows)} sum={sum(self.rows)}"


s = Same([1, 2, 3, 4])
s.summary
s.summary
s.summary
print("functools.cached_property behaves the same: ran",
      s.computations, "time(s)")
print("  s.__dict__ ->", s.__dict__)
