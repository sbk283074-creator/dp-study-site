def require_docstrings(cls):
    """The same validation as the metaclass, as a decorator."""
    for attr, value in vars(cls).items():
        if attr.startswith("_") or not callable(value):
            continue
        if not value.__doc__:
            raise TypeError(f"{cls.__name__}.{attr}() has no docstring")
    return cls


print("the same rule, enforced by a decorator -- no metaclass:")


@require_docstrings
class Good:
    def go(self):
        """Go."""


print("  Good was created; its docstring is present")
try:
    @require_docstrings
    class Bad:
        def go(self):
            pass
except TypeError as exc:
    print("  TypeError:", exc)
print()
print("but a decorator runs AFTER the class body, and it is not inherited:")


class SubGood(Good):
    def also(self):
        pass


print("  SubGood was created with no complaint")
print("  SubGood.also.__doc__ ->", SubGood.also.__doc__)
print()
print("A metaclass is inherited, so the rule reaches subclasses written")
print("years later in another file. That is the one thing a decorator")
print("cannot do, and it is usually the only reason to reach for a")
print("metaclass at all.")
print()
print("So the order to try is:")
print("  1. a plain function or __init__ check   -- simplest")
print("  2. a decorator                          -- one class, one rule")
print("  3. __init_subclass__                    -- the rule must be inherited")
print("  4. a metaclass                          -- you must change the")
print("                                             NAMESPACE before the")
print("                                             class body runs, or")
print("                                             replace the class object")
