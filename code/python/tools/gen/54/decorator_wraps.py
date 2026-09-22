"""Chapter 54 -- the decorator pattern, which in Python is punctuation.

`@` is the pattern. What it does not do by itself is preserve anything
about the function it wraps, and the list of what is lost is short
enough to check.
"""

import functools
import inspect


def original(a, b=2, *rest, **named):
    """Add two numbers.

    A docstring, which is one of the things at stake.
    """
    return a + b


def bare(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def keeping(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def logging_around(fn):
    """A decorator with arguments is a factory: one more layer, and the
    one that is usually written wrong."""
    def decorate(inner):
        @functools.wraps(inner)
        def wrapper(*args, **kwargs):
            return inner(*args, **kwargs)
        return wrapper
    return decorate


CHECKS = [
    ("__name__", lambda f: f.__name__),
    ("__doc__", lambda f: (f.__doc__ or "").strip().split("\n")[0]),
    ("__qualname__", lambda f: f.__qualname__),
    ("__module__", lambda f: f.__module__),
    ("signature", lambda f: str(inspect.signature(f))),
]


def main():
    variants = [
        ("the original", original),
        ("after a bare decorator", bare(original)),
        ("after functools.wraps", keeping(original)),
        ("after a decorator factory", logging_around("why")(original)),
    ]
    print(f"  things a function carries           {len(CHECKS)}")
    print()

    print("    what                    the original          after a bare decorator")
    for label, read in CHECKS:
        print("    {:<24}{:<22}{}".format(
            label, read(original), read(bare(original))))
    print()
    print("    what                    after functools.wraps")
    for label, read in CHECKS:
        print("    {:<24}{}".format(label, read(keeping(original))))
    print()

    lost = [label for label, read in CHECKS
            if read(bare(original)) != read(original)]
    kept = [label for label, read in CHECKS
            if read(keeping(original)) == read(original)]
    print(f"  the bare decorator loses {len(lost)} of the {len(CHECKS)}: "
          f"{', '.join(lost)}.")
    print(f"  `functools.wraps` restores {len(kept)} of the {len(CHECKS)}.")
    print()
    print("  the one that matters most in practice is the signature, and it")
    print("  matters because nothing in the code fails. a wrapped function")
    print("  still runs, and a caller who passes the wrong argument still gets")
    print("  the original's own error. what breaks is every tool that reads")
    print("  the function rather than calls it -- a help page, an editor, a")
    print("  schema generator -- and those all report the wrapper.")
    print()
    print("  the fourth variant is there because the factory is the shape")
    print("  that gets it wrong: `@logging_around(\"why\")` is three nested")
    print("  functions, and putting `functools.wraps` on the outer one instead")
    print("  of the inner one is the mistake that looks like a fix. the")
    print("  measurement above is the inner one, which is the right one.")


main()
