"""Chapter 55 -- practice 2.

Three tests that touch the same object, run in three orders, under four
arrangements. The count is of the tests whose result depends on the
order, and the third arrangement is the one worth reading.
"""


class Cart:
    def __init__(self):
        self.items = []

    def add(self, name):
        self.items.append(name)
        return len(self.items)


_SHARED = Cart()


def get_cart():
    return _SHARED


# --- raw
def raw_is_empty():
    return get_cart().items == []


def raw_one_item():
    return get_cart().add("a") == 1


def raw_two_items():
    cart = get_cart()
    cart.add("a")
    cart.add("b")
    return len(cart.items) == 2
# --- end


# --- cleared
def cleared_is_empty():
    cart = get_cart()
    cart.items.clear()
    return cart.items == []


def cleared_one_item():
    cart = get_cart()
    cart.items.clear()
    cart.add("a")
    return len(cart.items) == 1


def cleared_two_items():
    cart = get_cart()
    cart.items.clear()
    cart.add("a")
    cart.add("b")
    return len(cart.items) == 2
# --- end


# --- partial
def partial_is_empty():
    cart = get_cart()
    cart.items.clear()
    return cart.items == []


def partial_one_item():
    cart = get_cart()
    cart.items.clear()
    cart.add("a")
    return len(cart.items) == 1


def partial_two_items():
    """This one does not clear, which is the whole of the difference."""
    cart = get_cart()
    cart.add("a")
    cart.add("b")
    return len(cart.items) == 2
# --- end


# --- fresh
def fresh_is_empty():
    return Cart().items == []


def fresh_one_item():
    cart = Cart()
    cart.add("a")
    return len(cart.items) == 1


def fresh_two_items():
    cart = Cart()
    cart.add("a")
    cart.add("b")
    return len(cart.items) == 2
# --- end


NAMES = ["cart is empty", "one item", "two items"]

ARRANGEMENTS = [
    ("no clearing", [raw_is_empty, raw_one_item, raw_two_items]),
    ("cleared in all three", [cleared_is_empty, cleared_one_item,
                              cleared_two_items]),
    ("cleared in two of three", [partial_is_empty, partial_one_item,
                                 partial_two_items]),
    ("built in the test", [fresh_is_empty, fresh_one_item, fresh_two_items]),
]

ORDERS = [
    [0, 1, 2],
    [2, 1, 0],
    [1, 2, 0],
]


def run(suite, positions):
    """One run of the suite, in the order given. The shared cart is
    emptied first so that each order starts from the same place -- which
    is the condition the count below is measured under."""
    _SHARED.items.clear()
    out = {}
    for position in positions:
        try:
            out[position] = bool(suite[position]())
        except Exception:
            out[position] = False
    return out


def main():
    print(f"  tests                               {len(NAMES)}")
    print(f"  orders                              {len(ORDERS)}")
    print()

    print("    how the cart is arranged          passes, in each of the orders")
    results = {}
    for label, suite in ARRANGEMENTS:
        rows = []
        for positions in ORDERS:
            rows.append(run(suite, positions))
        results[label] = rows
        print("    {:<34}{}".format(
            label, "  ".join("%d of %d" % (sum(r.values()), len(r))
                             for r in rows)))
    print()

    print("    tests whose result depends on the order")
    for label, _ in ARRANGEMENTS:
        changed = 0
        for position in range(len(NAMES)):
            seen = set(row[position] for row in results[label])
            changed += 1 if len(seen) > 1 else 0
        print("    {:<34}{} of {}".format(label, changed, len(NAMES)))
    print()
    print("  clearing the shared cart works, and the third row is why it is")
    print("  not the fix. two of the three tests clear it and one does not,")
    print("  and one of the three is order-dependent again -- so the")
    print("  arrangement is correct only as long as every test remembers the")
    print("  line, and the next test somebody adds is a chance to forget it.")
    print()
    print("  that is the difference between a discipline and a guarantee. a")
    print("  test that clears shared state is a test that knows which state")
    print("  to clear, and the next person to add a test has to know it too.")
    print("  a test that builds its own cart cannot forget, because there is")
    print("  nothing to forget.")
    print()
    print("  the fourth row is the one to copy. it is not longer than the")
    print("  third, it does not need a fixture, and the order stops being an")
    print("  input to the result -- which is what the count in the middle of")
    print("  this table is measuring.")


main()
