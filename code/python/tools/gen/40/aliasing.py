print("assignment never copies")
a = [1, 2, 3]
b = a
b.append(4)
print("  a ->", a, "   b ->", b)
print("  a is b ->", a is b)
print()

print("rebinding is not mutating")
c = [1, 2, 3]
d = c
d = d + [4]
print("  c ->", c, "   d ->", d)
print("  the + built a NEW list and pointed d at it; c never moved")
print()

print("the default-argument trap")


def collect(item, into=[]):
    into.append(item)
    return into


print("  collect(1) ->", collect(1))
print("  collect(2) ->", collect(2))
print("  collect(3) ->", collect(3))
print("  the default object itself ->", collect.__defaults__[0])
print()

print("the fix")


def collect_safe(item, into=None):
    if into is None:
        into = []
    into.append(item)
    return into


print("  collect_safe(1) ->", collect_safe(1))
print("  collect_safe(2) ->", collect_safe(2))
print()

print("immutables can be shared, because sharing is invisible")
x = (1, 2, 3)
y = x
print("  x is y ->", x is y, "  and mutating is impossible, so nobody notices")
print()

print("but a tuple can still hold something mutable")
t = ([],)
t[0].append("oops")
print("  t ->", t)
print("  the tuple never changed; the list inside it did")
