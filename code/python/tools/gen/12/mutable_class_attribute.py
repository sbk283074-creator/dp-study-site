"""Chapter 12 -- the class attribute that is one object, not one per instance.

Ten instances of a class with a list defined on the class, then ten of a class
that assigns its own. The count is of instances whose view changed when a single
instance appended to the list.
"""

INSTANCES = 10


class SharedCart:
    items = []                      # one list, created once, on the class

    def __init__(self, name):
        self.name = name


class OwnCart:
    def __init__(self, name):
        self.name = name
        self.items = []             # one list per instance


def measure(cls):
    carts = [cls(f"cart-{index}") for index in range(INSTANCES)]
    carts[0].items.append("apple")
    return carts


shared = measure(SharedCart)
own = measure(OwnCart)

print(f"{INSTANCES} instances of each class, one append to the first instance")
print()
print(f"{'what is counted':<46}{'shared':>8}{'own':>8}")
print("-" * 62)
print(f"{'instances holding their own items list':<46}"
      f"{sum('items' in vars(cart) for cart in shared):>8}"
      f"{sum('items' in vars(cart) for cart in own):>8}")
print(f"{'instances whose view changed':<46}"
      f"{sum(1 for cart in shared if cart.items):>8}"
      f"{sum(1 for cart in own if cart.items):>8}")
print(f"{'entries the last instance can see':<46}"
      f"{len(shared[-1].items):>8}{len(own[-1].items):>8}")

print()
print("The first row is the difference. In the shared class no instance holds an")
print("items list of its own, because the class body ran once and created one")
print("list for the whole class. Ten instances, one append, and ten views")
print("changed -- the list on the class is not a default value, it is a single")
print("object every instance can reach.")
print()
print("The second class assigns in `__init__`, so each instance gets its own")
print("list. Ten instances, one append, and one view changed. The count in the")
print("third row is the one to remember: the last instance can see one entry")
print("under the first design and none under the second.")
print()
print("A mutable class attribute is therefore a shared cache that nobody")
print("declared as one, and the only safe class attributes are immutable --")
print("numbers, strings, tuples, None. A list, dict or set written in a class")
print("body is a bug waiting for the second instance.")
