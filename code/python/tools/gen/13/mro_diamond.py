"""Chapter 13 -- the method resolution order is a list, and super() walks it.

A diamond: one base, two classes inheriting it, and one class inheriting both.
The count is of classes consulted before a name is found, and of __init__ bodies
that run for a single instantiation.
"""

RUNS = []


class Base:
    def __init__(self):
        RUNS.append("Base")

    def tag(self):
        return "base"


class Left(Base):
    def __init__(self):
        RUNS.append("Left")
        super().__init__()


class Right(Base):
    def __init__(self):
        RUNS.append("Right")
        super().__init__()


class Cooperative(Left, Right):
    def __init__(self):
        RUNS.append("Cooperative")
        super().__init__()


class Uncooperative(Left, Right):
    def __init__(self):
        RUNS.append("Uncooperative")


order = [cls.__name__ for cls in Cooperative.__mro__]

RUNS.clear()
Cooperative()
with_super = list(RUNS)

RUNS.clear()
Uncooperative()
without_super = list(RUNS)

definers = [cls.__name__ for cls in Cooperative.__mro__ if "tag" in vars(cls)]
consulted = order.index(definers[0])

print("one instantiation of a class that inherits two classes that share a base")
print()
print(f"{'what is counted':<50}{'count':>8}")
print("-" * 58)
print(f"{'classes in the resolution order':<50}{len(order):>8}")
print(f"{'classes that define tag':<50}{len(definers):>8}")
print(f"{'classes consulted before the answer is found':<50}{consulted:>8}")
print(f"{'__init__ bodies that ran, calling super()':<50}{len(with_super):>8}")
print(f"{'__init__ bodies that ran, not calling it':<50}{len(without_super):>8}")
print()
print(f"the resolution order is: {' -> '.join(order)}")
print(f"the bodies that ran with super() are: {', '.join(with_super)}")
print(f"the bodies that ran without it are: {', '.join(without_super)}")

print()
print("The third row is the part that surprises people. Three classes are")
print("consulted before `tag` is found, because the order is a single list and")
print("the answer sits at the end of it. It is not 'ask each parent, then each")
print("grandparent' -- the base appears once, in the position the algorithm")
print("gives it, and that is what makes a diamond safe.")
print()
print("The last two rows are the bug. `super()` does not mean 'my parent'. It")
print("means 'the next class in the resolution order of the object being")
print("built', which is why Right runs even though the class inherits from Left")
print("first. Drop the call and 1 of the 4 bodies runs, so every class above")
print("the first one is never initialised -- silently, with no error, on an")
print("object that looks perfectly fine.")
print()
print("That is the whole rule: in a hierarchy that will ever be inherited from")
print("more than once, every __init__ calls super().__init__(), and no __init__")
print("assumes it is the only one running.")
