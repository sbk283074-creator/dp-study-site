class computed:
    """A minimal property: __get__ only, so a NON-data descriptor."""

    def __init__(self, fget):
        self.fget = fget
        self.__doc__ = fget.__doc__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @computed
    def area(self):
        return round(3.141592653589793 * self.radius ** 2, 4)


c = Circle(2)
print("a working computed attribute: c.area ->", c.area)
print()
print("but it can be overwritten, because a non-data descriptor loses to")
print("the instance dict:")
c.area = 999
print("  after c.area = 999 ->", c.area)
print("  c.__dict__ ->", c.__dict__)
print()

print("the real property closes that hole with __set__:")


class readonly:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)

    def __set__(self, obj, value):
        raise AttributeError("property has no setter")


class Circle2:
    def __init__(self, radius):
        self.radius = radius

    @readonly
    def area(self):
        return round(3.141592653589793 * self.radius ** 2, 4)


c2 = Circle2(2)
print("  c2.area ->", c2.area)
try:
    c2.area = 999
except AttributeError as exc:
    print("  c2.area = 999 ->", exc)
print()
print("and the built-in property is the same object, in C:")


class Circle3:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return round(3.141592653589793 * self.radius ** 2, 4)


c3 = Circle3(2)
print("  c3.area ->", c3.area)
try:
    c3.area = 999
except AttributeError as exc:
    print("  c3.area = 999 ->", exc)
