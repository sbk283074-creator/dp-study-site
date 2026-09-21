import gc


class Tracked:
    def __init__(self, name):
        self.name = name
        print(f"  created   {name}")

    def __del__(self):
        print(f"  finalized {self.name}")


print("1. no cycle -- finalized the moment the last reference goes")
t = Tracked("plain")
del t
print()

print("2. a cycle -- nothing happens until the collector runs")
gc.disable()
a = Tracked("a")
b = Tracked("b")
a.partner = b
b.partner = a
del a
del b
print("   both names are gone, and neither object was finalized")
print("   that is the whole point: their reference counts are not zero")
collected = gc.collect()
print("   gc.collect() collected", collected, "unreachable objects")
gc.enable()
