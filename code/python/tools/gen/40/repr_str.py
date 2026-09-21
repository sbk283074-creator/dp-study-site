class Money:
    def __init__(self, amount, currency="GBP"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self):
        return f"{self.amount:.2f} {self.currency}"


m = Money(3.5)
print("repr(m)       ->", repr(m))
print("str(m)        ->", str(m))
print("f'{m}'        ->", f"{m}")
print("f'{m!r}'      ->", f"{m!r}")
print("inside a list ->", [m, m])
print("as a dict key ->", {m: "value"})
print()

print("a class with only __repr__:")


class OnlyRepr:
    def __repr__(self):
        return "OnlyRepr()"


o = OnlyRepr()
print("  str(o) ->", str(o), " <- __str__ falls back to __repr__")
print()

print("a class with neither:")


class Bare:
    pass


b = Bare()

import re

# The real repr contains an address, which differs on every run. Masking it
# keeps this listing honest and reproducible: the SHAPE is the lesson.
def masked(obj):
    return re.sub(r"0x[0-9a-f]+", "0x...", repr(obj))


print("  repr(b) ->", masked(b))
print("  str(b)  ->", masked(b))
print()
print("The default shows the class and an address. That is the cost of not")
print("writing __repr__: every debugging session pays it, every time.")
