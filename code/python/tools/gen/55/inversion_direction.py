"""Chapter 55 -- inversion, measured as the direction of the references.

The same two modules written twice: a policy and a mechanism. The count
is of references in each direction, and of the module that has to change
when the other one is replaced.
"""

POLICY_BUILDS_ITS_OWN = """\
from sql_store import SqlStore


class OrderPolicy:
    def __init__(self):
        self.store = SqlStore()

    def total(self, order_id):
        return self.store.get(order_id)
"""

MECHANISM_PLAIN = """\
class SqlStore:
    def __init__(self):
        self.rows = {}

    def get(self, key):
        return self.rows.get(key, 0)
"""

POLICY_TAKES_ONE = """\
class OrderPolicy:
    def __init__(self, store):
        self.store = store

    def total(self, order_id):
        return self.store.get(order_id)
"""

MECHANISM_IMPLEMENTS = """\
from policy import Store


class SqlStore(Store):
    def __init__(self):
        self.rows = {}

    def get(self, key):
        return self.rows.get(key, 0)
"""

DESIGNS = [
    ("the policy builds the mechanism", POLICY_BUILDS_ITS_OWN, MECHANISM_PLAIN),
    ("the mechanism implements it", POLICY_TAKES_ONE, MECHANISM_IMPLEMENTS),
]


def mentions(source, name):
    """Lines of `source` that name the other module."""
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  designs                             {len(DESIGNS)}")
    print()
    print("    design                          policy -> store   store -> policy")
    forward, backward = [], []
    for label, policy, mechanism in DESIGNS:
        out = mentions(policy, "sql_store")
        back = mentions(mechanism, "policy")
        forward.append(out)
        backward.append(back)
        print("    {:<32}{:<18}{}".format(
            label, "%d reference" % out, "%d reference" % back))
    print()

    print("    when the mechanism is replaced")
    for index, (label, _, _) in enumerate(DESIGNS):
        verdict = "the policy is edited too" if forward[index] \
            else "the policy is untouched"
        print("    {:<32}{}".format(label, verdict))
    print()

    print(f"  each design holds {forward[0] + backward[0]} reference between")
    print("  the two modules, and they point in opposite directions. so")
    print("  inversion is not a reduction in coupling -- the count is")
    print("  identical.")
    print()
    print("  what changes is which module is on the receiving end. in the")
    print("  first design the policy names the mechanism, so the stable thing")
    print("  depends on the unstable one and replacing the database edits the")
    print("  business rule. in the second the mechanism names the policy's")
    print("  interface, so the arrow runs from the thing that will be")
    print("  replaced towards the thing that will not.")
    print()
    print("  that is the whole of what the word inversion means here, and it")
    print("  is why the interface belongs to the consumer rather than to the")
    print("  implementation. a `Store` defined in the database module would")
    print("  have the arrow pointing the wrong way no matter where the")
    print("  `import` statement sits.")
    print()
    print("  the cost is one new module -- the interface -- and one new place")
    print("  that knows both sides, which is the composition root. the")
    print("  benefit is that the policy can be tested, replaced and reasoned")
    print("  about without the database existing, and that is what the")
    print("  direction buys.")


main()
