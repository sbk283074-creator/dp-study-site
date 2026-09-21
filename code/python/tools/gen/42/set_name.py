class Field:
    def __set_name__(self, owner, name):
        self.name = name
        print(f"  __set_name__: {owner.__name__}.{name}")

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value

    def __repr__(self):
        return f"Field({self.name!r})"


print("the class body runs, and each Field is told its own name:")


class Config:
    host = Field()
    port = Field()


print()
print("so a descriptor can store under its own name without the user")
print("ever repeating it:")
print("  Config.host ->", Config.host)
print("  Config.port ->", Config.port)
print()
c = Config()
c.host = "localhost"
c.port = 8080
print("  c.host ->", c.host)
print("  c.port ->", c.port)
print("  c.__dict__ ->", c.__dict__)
print()
print("Note the storage name and the attribute name are the same, and the")
print("descriptor worked that out on its own. That is what __set_name__ is")
print("for, and it is how dataclasses and Django-style models work.")
