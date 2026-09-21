class Counter:
    def __init__(self):
        self.n = 0

    def bump(self):
        self.n += 1
        return self.n


c = Counter()

print("a function has __get__ ->", hasattr(Counter.bump, "__get__"))
print("a function has __set__ ->", hasattr(Counter.bump, "__set__"))
print("so a function is a NON-data descriptor, and that is all a method is.")
print()

bound = Counter.bump.__get__(c, Counter)
print("calling __get__ by hand builds the bound method:")
print("  type(bound).__name__   ->", type(bound).__name__)
print("  bound.__self__ is c    ->", bound.__self__ is c)
print("  bound.__func__.__name__->", bound.__func__.__name__)
print("  bound()                ->", bound())
print()

print("accessed on the CLASS, __get__ receives obj=None and hands back")
print("the plain function:")
print("  Counter.bump.__name__        ->", Counter.bump.__name__)
print("  Counter.bump is bound.__func__ ->", Counter.bump is bound.__func__)
print()

print("So `self` is not a keyword and not an argument you pass. It is")
print("whatever __get__ was given when the attribute was looked up.")
