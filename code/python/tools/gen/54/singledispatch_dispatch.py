"""Chapter 54 -- dispatch, which Python already has.

`functools.singledispatch` is the strategy pattern as a language
feature. It dispatches on the type of one argument, and the two things
worth knowing are which argument and what it does with a subclass.
"""

from functools import singledispatch


@singledispatch
def render(value):
    return "the default"


@render.register
def _(value: int):
    return "int"


@render.register
def _(value: str):
    return "str"


@render.register
def _(value: list):
    return "list"


class Money(int):
    """A subclass of a registered type, which is the case that decides
    whether the dispatch is on the class or on the name."""


@singledispatch
def combine(first, second):
    return "the default"


@combine.register
def _(first: int, second):
    return "int first"


@combine.register
def _(first: str, second):
    return "str first"


VALUES = [1, True, 1.0, "a", [1], {"a": 1}, (1,), None, Money(707)]

CALLS = [
    (1, "a"),
    ("a", 1),
    (1.0, 1),
    ([1], 1),
    (True, "a"),
]


def main():
    print(f"  handlers registered                 {len(render.registry)}")
    print(f"  values                              {len(VALUES)}")
    print()

    print("    value                type        handler reached")
    for value in VALUES:
        print("    {:<21}{:<12}{}".format(
            repr(value), type(value).__name__, render(value)))
    print()

    reached = {}
    for value in VALUES:
        reached.setdefault(render(value), []).append(repr(value))
    default = reached.get("the default", [])
    print(f"  {len(default)} of the {len(VALUES)} reached the default, and the one")
    print("  worth reading is `True`. `bool` is a subclass of `int`, so it")
    print("  reached the int handler -- and so did `Money(7)`, which is a")
    print("  subclass you wrote. the dispatch walks the mro rather than")
    print("  matching the class name, which is why registering `int` is not")
    print("  the same as registering `int` and only `int`.")
    print()

    print("  the second argument decides nothing")
    print()
    print("    call                 first arg type   handler")
    for first, second in CALLS:
        print("    {:<21}{:<16}{}".format(
            "combine({}, {})".format(repr(first), repr(second)),
            type(first).__name__, combine(first, second)))
    print()
    print("  `combine(1, 'a')` and `combine(1, 1)` reach the same handler,")
    print("  and `combine('a', 1)` and `combine('a', 1.0)` reach another. the")
    print("  type of the second argument is never consulted, which is the")
    print("  limit of the mechanism and also its documentation: the function")
    print("  is dispatched on one value and every other argument is data.")
    print()
    print("  so this is the strategy pattern with the selection already")
    print("  written, and the trade is the same one as the table: the")
    print("  dispatch is a registration rather than a branch, and a type")
    print("  nobody registered is a default rather than a silent")
    print("  fall-through -- as long as you decide what the default is.")
    print("  the default here returns a string, which is the wrong answer")
    print("  that looks like the right one; raising would have been better.")


main()
