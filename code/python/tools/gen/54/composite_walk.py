"""Chapter 54 -- the composite pattern.

A tree whose leaves and whose branches answer the same questions. The
pattern's claim is that a new kind of node is one new class, and that is
measurable: count the implementations against the number of nodes.
"""


class Node:
    kind = "node"

    def size(self, visits):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError


class File(Node):
    kind = "file"

    def __init__(self, name, size):
        self.name = name
        self._size = size

    def size(self, visits):
        visits[0] += 1
        return self._size

    def count(self):
        return 1


class Dir(Node):
    kind = "dir"

    def __init__(self, name, children):
        self.name = name
        self.children = children

    def size(self, visits):
        visits[0] += 1
        return sum(child.size(visits) for child in self.children)

    def count(self):
        return 1 + sum(child.count() for child in self.children)


class Cached(Node):
    """The same interface again, with the answer remembered. This is the
    node that makes the pattern pay, and it is also the node that has to
    know about invalidation."""

    def __init__(self, child):
        self.child = child
        self._cached = None

    def size(self, visits):
        visits[0] += 1
        if self._cached is None:
            self._cached = self.child.size(visits)
        return self._cached

    def count(self):
        return self.child.count()


TREE = Dir("root", [
    File("readme.md", 12),
    Dir("src", [
        File("main.py", 40),
        File("util.py", 15),
        Dir("lib", [File("a.py", 8), File("b.py", 9)]),
    ]),
    Dir("docs", [File("index.md", 30), File("api.md", 22)]),
    File("setup.py", 6),
])


def nodes(node):
    yield node
    for child in getattr(node, "children", []):
        yield from nodes(child)


def main():
    kinds = {}
    for node in nodes(TREE):
        kinds[node.kind] = kinds.get(node.kind, 0) + 1
    implementations = [File, Dir, Cached]
    print(f"  nodes in the tree                   {sum(kinds.values())}")
    for kind in ("file", "dir"):
        print("    {:<34}{}".format(kind, kinds[kind]))
    print(f"  implementations of the interface    {len(implementations)}")
    print("    {:<34}{}".format(
        "and the node types the tree uses", len(set(type(n) for n in nodes(TREE)))))
    print()

    print(f"  the whole tree is {TREE.count()} entries and "
          f"{TREE.size([0])} bytes.")
    print()

    print("    query on the root          nodes visited")
    for label in ("the first", "the second", "the third"):
        visits = [0]
        TREE.size(visits)
        print("    {:<27}{}".format(label, visits[0]))
    print()
    print("  every query walks every node. the pattern gives the leaf and the")
    print("  branch the same interface, and it does not give them the same")
    print("  cost -- a branch is a fold over its children, so asking the root")
    print("  a question is asking the whole tree that question.")
    print()

    cached = Cached(TREE)
    print("    the same, with one caching node at the root")
    for label in ("the first", "the second", "the third"):
        visits = [0]
        cached.size(visits)
        print("    {:<27}{}".format(label, visits[0]))
    print()
    print("  the caching node implements the same interface, so nothing above")
    print("  it changed and nothing above it can tell. that is the pattern")
    print("  working exactly as advertised.")
    print()
    print("  it is also the node that has to be told when the answer stops")
    print("  being true, and nothing in the interface has a method for that.")
    print("  the pattern made the tree uniform and left invalidation as the")
    print("  thing the uniform interface cannot express.")


main()
