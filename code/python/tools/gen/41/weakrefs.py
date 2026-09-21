import weakref


class Session:
    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return f"Session({self.user!r})"


print("a weak reference does not keep the object alive")
s = Session("ada")
ref = weakref.ref(s)
print("  ref() while s is alive ->", ref())
del s
print("  after del s            ->", ref())
print()

print("which is what makes a cache that does not leak")
cache = weakref.WeakValueDictionary()
tmp = Session("grace")
cache["grace"] = tmp
print("  cached, tmp alive      ->", dict(cache))
del tmp
print("  after del tmp          ->", dict(cache), " <- the entry went too")
print()

print("a strong cache would have kept it forever")
strong = {}
tmp = Session("alan")
strong["alan"] = tmp
del tmp
print("  strong cache holds     ->", dict(strong))
print("  and holds it until the program ends or the key is deleted")
