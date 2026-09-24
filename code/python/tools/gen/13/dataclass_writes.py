"""Chapter 13 -- what the dataclass decorator writes, counted.

Three classes over the same two fields: one written by hand, one decorated with
@dataclass, one with a frozen dataclass. The count is of the four methods that
make a value type, and of how many of the three can be used as a dictionary key.
"""

import dataclasses

METHODS = ["__init__", "__repr__", "__eq__", "__hash__"]


class HandWritten:
    def __init__(self, name, qty):
        self.name = name
        self.qty = qty


@dataclasses.dataclass
class Generated:
    name: str
    qty: int


@dataclasses.dataclass(frozen=True)
class Frozen:
    name: str
    qty: int


CLASSES = [
    ("hand-written", HandWritten),
    ("@dataclass", Generated),
    ("frozen @dataclass", Frozen),
]


def defines(cls, name):
    """True only if the class itself defines the method with a real value."""
    return name in vars(cls) and vars(cls)[name] is not None


def usable_as_key(cls):
    try:
        hash(cls("widget", 3))
        return "yes"
    except TypeError:
        return "no"


print("three classes over the same two fields, name and qty")
print()
print(f"{'class':<20}{'init':>6}{'repr':>6}{'eq':>6}{'hash':>6}{'written':>9}"
      f"{'as a key':>10}")
print("-" * 63)
for label, cls in CLASSES:
    marks = ["yes" if defines(cls, name) else "no" for name in METHODS]
    written = sum(1 for name in METHODS if defines(cls, name))
    print(f"{label:<20}{marks[0]:>6}{marks[1]:>6}{marks[2]:>6}{marks[3]:>6}"
          f"{written:>9}{usable_as_key(cls):>10}")

equal = [label for label, cls in CLASSES if cls("widget", 3) == cls("widget", 3)]
unequal = [label for label, cls in CLASSES if label not in equal]

print()
print(f"two instances holding the same fields compare equal: {', '.join(equal)}")
print(f"they do not: {', '.join(unequal)}")

print()
print("The written column is the decorator's job. The hand-written class defines")
print("one of the four methods; @dataclass writes three; a frozen dataclass")
print("writes four. None of that is a saving in typing -- it is a saving in")
print("attention, because a hand-written value class usually has __init__ and")
print("nothing else, and then two equal objects are not equal.")
print()
print("The last column is the trap, and it is the one to take away. @dataclass")
print("sets __hash__ to None, so an instance cannot be a dictionary key or a set")
print("member -- the class defines three of the four methods and is still")
print("unusable in the two places a value type is most useful. Adding")
print("frozen=True writes the fourth method back.")
print()
print("So the default for a value object should be frozen. It buys hashing,")
print("which buys keys and sets, and it makes the object safe to share: a")
print("frozen instance cannot be mutated by a caller that was handed one. Make")
print("it mutable only when something has to change after construction, and")
print("then accept that it cannot be used as a key.")
