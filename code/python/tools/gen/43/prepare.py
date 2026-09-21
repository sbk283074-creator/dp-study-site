class Recording(dict):
    """A namespace that remembers the order names were defined in."""

    def __init__(self):
        super().__init__()
        self.order = []

    def __setitem__(self, key, value):
        if key not in self:
            self.order.append(key)
        super().__setitem__(key, value)


class OrderedMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        print(f"  __prepare__ is handing the class body a "
              f"{Recording.__name__} for {name}")
        return Recording()

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace)
        cls.declared = [n for n in namespace.order if not n.startswith("_")]
        return cls


class Model(metaclass=OrderedMeta):
    title = "a string"
    created = "a date"
    author = "a foreign key"


print()
print("the class body wrote into our mapping, so we know the order:")
print("  Model.declared ->", Model.declared)
print()
print("Be honest about how much this buys: a plain dict has preserved")
print("insertion order since Python 3.7, so `__prepare__` returning a")
print("dict would have given the same order here. The hook exists so you")
print("can supply a mapping that does something a dict cannot --")
print("recording duplicates, rejecting a name, or resolving a name")
print("through a lookup instead of storing it.")
