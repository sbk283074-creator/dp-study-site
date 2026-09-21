import gc, sys


class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

    def __repr__(self):
        return f"Node({self.name!r})"


gc.disable()          # leave only reference counting in play


def make_cycle():
    a = Node("a")
    b = Node("b")
    a.peer = b
    b.peer = a
    print("  inside, getrefcount(a) ->", sys.getrefcount(a),
          "(a, b.peer, and the argument)")
    return None


print("a two-node cycle, built inside a function")
make_cycle()
print("  the function returned, so both local names are gone")
print("  yet neither object was freed: each is kept alive by the other")
print("  their counts are 1, not 0, so reference counting cannot help")
print()
print("  gc.is_tracked is how the collector knows to look at them")
print("  gc.collect() ->", gc.collect(), "unreachable objects freed")
print()
print("reference counting frees acyclic garbage immediately and for free.")
print("The cycle collector exists only for the shapes refcounting cannot see.")
gc.enable()
