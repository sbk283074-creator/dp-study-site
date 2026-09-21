class Probe:
    def __new__(cls, *args, **kwargs):
        print("  __new__     called, args =", args)
        instance = super().__new__(cls)
        print("  __new__     built an empty", type(instance).__name__)
        return instance

    def __init__(self, value):
        print("  __init__    called, value =", value)
        self.value = value


print("Probe(1):")
p = Probe(1)
print("  result: p.value =", p.value)
print()

print("Now a class whose __new__ returns something that is NOT an instance")
print("of the class:")


class Factory:
    def __new__(cls):
        print("  __new__  returning a list instead of a Factory")
        return [1, 2, 3]

    def __init__(self):
        print("  __init__ ran -- you should NOT see this line")


f = Factory()
print("  result:", f, type(f).__name__)
print()

print("And the case that forces you to use __new__: an immutable base.")


class Frozen(tuple):
    def __new__(cls, *values):
        return super().__new__(cls, values)


fz = Frozen(1, 2, 3)
print("  Frozen(1, 2, 3) ->", fz, " type:", type(fz).__name__)
print("  isinstance(fz, tuple) ->", isinstance(fz, tuple))
print("  a tuple subclass cannot set attributes in __init__: the value is")
print("  already fixed by the time __new__ returns, which is the whole point.")
