import gc


class Node:
    def __init__(self):
        self.next = None


print("the collector is generational: young objects are scanned often,")
print("older ones rarely, because most garbage dies young")
print("  gc.get_threshold() ->", gc.get_threshold())
print("  gc.isenabled()     ->", gc.isenabled())
print()

print("an explicit collect always works, even with the collector switched off")
gc.disable()
a, b = Node(), Node()
a.next = b
b.next = a
del a, b
print("  gc.collect() ->", gc.collect(), "objects freed while gc is disabled")
gc.enable()
print()

print("tuning you may actually need:")
print("  gc.set_threshold(...)  -- scan less often, if collection shows up")
print("                            in a profile as the cost")
print("  gc.freeze()            -- exclude existing objects from collection,")
print("                            which is worth knowing before you fork")
print("  gc.set_debug(...)      -- report what the collector collects")
