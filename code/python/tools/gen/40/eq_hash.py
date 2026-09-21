class Money:
    def __init__(self, amount, currency="GBP"):
        self.amount = amount
        self.currency = currency

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"


print("define __eq__ and nothing else:")
print("  Money.__hash__ is None ->", Money.__hash__ is None)
try:
    {Money(1)}
except TypeError as exc:
    print("  putting one in a set raises:", exc)
print()

print("so add __hash__ over the SAME fields __eq__ compares:")


class Hashable(Money):
    def __hash__(self):
        return hash((self.amount, self.currency))


print("  equal values hash equal  ->", hash(Hashable(1)) == hash(Hashable(1)))
print("  a set collapses the pair ->", {Hashable(1), Hashable(1)})
print("  a dict finds by value    ->", {Hashable(1): "found"}[Hashable(1)])
print()

print("returning NotImplemented hands the comparison back to the other side:")
print("  Money(1) == 1 ->", Money(1) == 1)
print("  Money(1) != 1 ->", Money(1) != 1)
print()

print("the contract: a == b must imply hash(a) == hash(b)")
print("  1 == 1.0  ->", 1 == 1.0, "  hash equal ->", hash(1) == hash(1.0))
print("  True == 1 ->", True == 1, "  hash equal ->", hash(True) == hash(1))
d = {1: "one"}
print("  so one dict entry answers to all three:")
print("    d[1] ->", d[1], "   d[1.0] ->", d[1.0], "   d[True] ->", d[True])
print()

print("and the failure mode -- a hash key that can change:")


class Bad:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return hash(self.n)

    def __eq__(self, other):
        return isinstance(other, Bad) and self.n == other.n

    def __repr__(self):
        return f"Bad(n={self.n})"


k = Bad(1)
cache = {k: "computed"}
print("  stored while n == 1: cache[Bad(1)] ->", cache[Bad(1)])
k.n = 2
print("  after k.n = 2:       cache[Bad(1)] ->",
      cache.get(Bad(1), "NOT FOUND"))
print("  the entry is still in the dict:", list(cache))
print("  it sits in the bucket for hash(1); nothing can reach it by value now.")
