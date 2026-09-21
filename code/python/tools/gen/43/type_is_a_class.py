class Statement:
    """Built with the class statement."""
    kind = "statement"

    def describe(self):
        return f"I am a {self.kind}"


def describe(self):
    return f"I am a {self.kind}"


Built = type("Built", (), {"kind": "type()", "describe": describe})

print("type(Statement) ->", type(Statement).__name__)
print("type(Built)     ->", type(Built).__name__)
print("type(3)         ->", type(3).__name__)
print()
print("so a class is an instance of type, and `type` is itself a class:")
print("  isinstance(Statement, type) ->", isinstance(Statement, type))
print("  isinstance(Built, type)     ->", isinstance(Built, type))
print("  isinstance(Statement, object) ->", isinstance(Statement, object))
print()
print("and both classes behave identically:")
print("  Statement().describe() ->", Statement().describe())
print("  Built().describe()     ->", Built().describe())
print()
print("`class Foo(Base): ...` is sugar for three arguments -- a name, a")
print("tuple of bases, and a namespace dict -- handed to a callable that")
print("produces the class. That callable is the metaclass, and by default")
print("it is `type` itself.")
