registry = {}


class Handler:
    def __init_subclass__(cls, *, command=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if command is not None:
            registry[command] = cls
            print(f"  registered {cls.__name__} for command {command!r}")

    def run(self):
        raise NotImplementedError


print("subclassing registers -- no metaclass anywhere in this file:")


class Add(Handler, command="add"):
    def run(self):
        return "adding"


class Remove(Handler, command="remove"):
    def run(self):
        return "removing"


print()
print("registry ->", {k: v.__name__ for k, v in registry.items()})
print()
print("and the classes are ordinary classes:")
print("  Add().run()    ->", Add().run())
print("  Remove().run() ->", Remove().run())
print()
print("a subclass that omits the keyword is simply not registered:")
class Plain(Handler):
    def run(self):
        return "plain"


print("  registry after Plain ->", {k: v.__name__ for k, v in registry.items()})
print()
print("`command` is keyword-only and the hook receives it because it was")
print("declared with `**kwargs` in the class statement. That is how a base")
print("class accepts options from a subclass it has never seen.")
