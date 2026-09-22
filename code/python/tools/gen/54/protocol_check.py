"""Chapter 54 -- interfaces, and what a check on one is worth.

A `Protocol` and an `ABC` both name an interface. What they do with
`isinstance` is different, and the difference is what the word
"structural" costs.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Store(Protocol):
    def get(self, key):
        ...


@runtime_checkable
class Checkable(Protocol):
    def get(self, key):
        ...


class BaseStore(ABC):
    @abstractmethod
    def get(self, key):
        ...


class Real:
    def get(self, key):
        return "the value for " + key


class WrongArity:
    """The right name and the wrong signature."""

    def get(self):
        return "no key taken"


class NotCallable:
    """The right name bound to something that is not a method."""

    get = 5


class Subclass(BaseStore):
    def get(self, key):
        return "subclassed"


OBJECTS = [
    ("a class with the method", Real()),
    ("the right name, wrong signature", WrongArity()),
    ("the right name, not callable", NotCallable()),
    ("a subclass of the ABC", Subclass()),
]


def check(obj, cls):
    try:
        return "True" if isinstance(obj, cls) else "False"
    except TypeError as exc:
        return type(exc).__name__


def main():
    print(f"  objects                             {len(OBJECTS)}")
    print(f"  interfaces named                    {3}")
    print()

    print("    object                           Store      Checkable  BaseStore")
    for label, obj in OBJECTS:
        print("    {:<33}{:<11}{:<11}{}".format(
            label, check(obj, Store), check(obj, Checkable),
            check(obj, BaseStore)))
    print()

    plain = set(check(obj, Store) for _, obj in OBJECTS)
    structural = [label for label, obj in OBJECTS if check(obj, Checkable) == "True"]
    nominal = [label for label, obj in OBJECTS if check(obj, BaseStore) == "True"]
    print(f"  the plain Protocol raises {', '.join(sorted(plain))} for all "
          f"{len(OBJECTS)} objects,")
    print("  which is a decision rather than an oversight: a structural check")
    print("  costs a walk over the attributes on every call, and the default")
    print("  is to not pay it.")
    print()
    print(f"  `runtime_checkable` accepts {len(structural)} of the {len(OBJECTS)}:")
    for label in structural:
        print("    " + label)
    print()
    print(f"  the ABC accepts {len(nominal)}: {', '.join(nominal)}. it is the strictest")
    print("  of the three, and it is strict in the way that costs the most --")
    print("  a class that already does the right thing has to be edited to say")
    print("  so, which is a change to code that was not wrong.")
    print()
    print("  the row to read twice is the second one. an object whose method")
    print("  takes no arguments passed a check for an interface whose method")
    print("  takes a key, because the runtime check looks at whether the")
    print("  attribute exists and not at what it accepts. so the one check")
    print("  that is available at runtime is a check on names.")
    print()
    print("  that is the trade the whole idea rests on. the interface is for")
    print("  the reader and the type checker, both of which can see the")
    print("  signature. the runtime check is for the code path you cannot")
    print("  prove, and it is weaker than it looks -- which is fine, as long")
    print("  as it is not the only thing standing between a request and a")
    print("  call.")


main()
