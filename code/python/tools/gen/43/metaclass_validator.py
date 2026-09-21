class Validated(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        for attr, value in namespace.items():
            if attr.startswith("_") or not callable(value):
                continue
            if not value.__doc__:
                raise TypeError(
                    f"{name}.{attr}() has no docstring: every public method "
                    f"must document itself")
        return super().__new__(mcls, name, bases, namespace)


print("the metaclass inspects the class at creation time:")


class Service(metaclass=Validated):
    def connect(self):
        """Open the connection."""

    def close(self):
        """Close the connection."""


print("  Service was created, so both methods had docstrings")
print("  public methods ->",
      sorted(n for n, v in vars(Service).items()
             if callable(v) and not n.startswith("_")))
print()

print("and now one method that does not:")
try:
    class Broken(metaclass=Validated):
        def connect(self):
            """Open the connection."""

        def close(self):
            pass
except TypeError as exc:
    print("  TypeError:", exc)
print()
print("The failure happened when the class was DEFINED, not when it was")
print("used, not in a test, and not in production. That is the entire")
print("argument for validating at class-creation time.")
print()
print("and the check is inherited, because the metaclass is:")
try:
    class SubService(Service):
        def reset(self):
            pass
except TypeError as exc:
    print("  TypeError:", exc)
