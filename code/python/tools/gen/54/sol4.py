"""Chapter 54 -- practice 4.

An audit of one interface. Five collaborators and four ways of asking
whether each of them satisfies it, so that the question "which check
should I use" can be answered with a table instead of an opinion.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Fetches(Protocol):
    """The interface the code relies on. One method, one argument."""

    def fetch(self, key):
        ...


@runtime_checkable
class FetchesChecked(Protocol):
    def fetch(self, key):
        ...


class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, key):
        ...


class Correct:
    def fetch(self, key):
        return "the value for " + key


class WrongArity:
    def fetch(self):
        return "no key"


class NotCallable:
    fetch = "a string"


class Missing:
    def get(self, key):
        return "the wrong name"


class Subclass(BaseFetcher):
    def fetch(self, key):
        return "subclassed"


COLLABORATORS = [
    ("the method, with the right signature", Correct()),
    ("the name, with no argument", WrongArity()),
    ("the name, bound to a string", NotCallable()),
    ("the wrong name entirely", Missing()),
    ("a subclass of the abc", Subclass()),
]

CHECKS = [
    ("hasattr", lambda obj: hasattr(obj, "fetch")),
    ("Protocol", lambda obj: _safe(obj, Fetches)),
    ("runtime", lambda obj: _safe(obj, FetchesChecked)),
    ("ABC", lambda obj: _safe(obj, BaseFetcher)),
]


def _safe(obj, cls):
    try:
        return isinstance(obj, cls)
    except TypeError:
        return "TypeError"


def main():
    print(f"  collaborators                       {len(COLLABORATORS)}")
    print(f"  ways of asking                      {len(CHECKS)}")
    print()

    print("    collaborator                        " +
          "".join("{:>10}".format(name) for name, _ in CHECKS))
    for label, obj in COLLABORATORS:
        row = "    {:<36}".format(label)
        for _, check in CHECKS:
            row += "{:>10}".format(str(check(obj)))
        print(row)
    print()

    for name, check in CHECKS:
        accepted = [label for label, obj in COLLABORATORS if check(obj) is True]
        print("    {:<32}{} of {} accepted".format(
            name, len(accepted), len(COLLABORATORS)))
    print()

    print(f"  the strictest check is the ABC, and it accepts "
          f"{len([1 for _, o in COLLABORATORS if _safe(o, BaseFetcher) is True])} of")
    print("  the five: only the collaborator that was written to satisfy it.")
    print("  it costs the most, because every class that already satisfies the")
    print("  interface has to be edited to say so, and that is a change to")
    print("  code that was not wrong.")
    print()
    print("  `hasattr` and the runtime protocol check accept the same four,")
    print("  and the third of those is the one worth looking at: `fetch` is")
    print("  bound to a string, so the attribute is there and calling it will")
    print("  fail. a runtime check on a name cannot tell that from a method,")
    print("  because it does not call anything.")
    print()
    print("  so the answer to which check to use is not one check. the")
    print("  interface is for the reader and the type checker, both of which")
    print("  can see the signature. the runtime check is a cheap guard that")
    print("  catches the collaborator that is missing the name entirely, which")
    print("  is the mistake that actually happens when a dependency is")
    print("  swapped. and the thing that catches the other two is a test that")
    print("  calls `fetch` and looks at what comes back -- which is the only")
    print("  one of the four that is asking about behaviour rather than about")
    print("  names.")


main()
