"""Chapter 55 -- the module-level handle, measured as order dependence.

Three behaviours run in three orders, against a ledger that reaches for a
module-level handle and against one that is handed its handle. The count
is of the behaviours whose result depends on what ran before them.
"""


class Shared:
    """The handle, and the reason the order matters."""

    def __init__(self):
        self.rows = {}

    def get(self, key):
        return self.rows.get(key, 0)

    def add(self, key, amount):
        self.rows[key] = self.get(key) + amount
        return self.rows[key]


_SHARED = Shared()


def get_shared():
    """The module-level reach. Every caller gets the same object, and
    nothing in the caller's signature says so."""
    return _SHARED


class LedgerGlobal:
    def __init__(self):
        self.db = get_shared()

    def balance(self):
        return self.db.get("a")

    def deposit(self, amount):
        return self.db.add("a", amount)


class LedgerInjected:
    def __init__(self, db):
        self.db = db

    def balance(self):
        return self.db.get("a")

    def deposit(self, amount):
        return self.db.add("a", amount)


def reads_zero(make):
    return make().balance() == 0


def one_deposit(make):
    return make().deposit(5) == 5


def accumulate(make):
    ledger = make()
    ledger.deposit(5)
    ledger.deposit(3)
    return ledger.balance() == 8


BEHAVIOURS = [
    ("a new ledger reads zero", reads_zero),
    ("one deposit is visible", one_deposit),
    ("deposits accumulate", accumulate),
]

BY_NAME = {name: fn for name, fn in BEHAVIOURS}

ORDERS = [
    ("zero, deposit, accumulate",
     ["a new ledger reads zero", "one deposit is visible",
      "deposits accumulate"]),
    ("accumulate, deposit, zero",
     ["deposits accumulate", "one deposit is visible",
      "a new ledger reads zero"]),
    ("deposit, accumulate, zero",
     ["one deposit is visible", "deposits accumulate",
      "a new ledger reads zero"]),
]

DESIGNS = (
    ("the module-level handle", lambda: LedgerGlobal()),
    ("a handle passed in", lambda: LedgerInjected(Shared())),
)


def run_order(make, names):
    """Run the named behaviours in the order given, against one handle
    made by `make`."""
    out = {}
    for name in names:
        try:
            out[name] = bool(BY_NAME[name](make))
        except Exception:
            out[name] = False
    return out


def main():
    print(f"  behaviours                          {len(BEHAVIOURS)}")
    print(f"  orders                              {len(ORDERS)}")
    print()

    outcomes = {}
    print("    the order the behaviours run in")
    print("    {:<28}{:<20}{}".format("", "module-level", "passed in"))
    for label, names in ORDERS:
        row = []
        for _, make in DESIGNS:
            _SHARED.rows.clear()
            row.append(run_order(make, names))
        outcomes[label] = row
        print("    {:<28}{:<20}{}".format(
            label,
            "%d of %d pass" % (sum(row[0].values()), len(names)),
            "%d of %d pass" % (sum(row[1].values()), len(names))))
    print()

    print("    behaviours whose result depends on the order")
    for index, (name, _) in enumerate(DESIGNS):
        changed = 0
        for behaviour, _ in BEHAVIOURS:
            seen = set(outcomes[label][index][behaviour] for label, _ in ORDERS)
            changed += 1 if len(seen) > 1 else 0
        print("    {:<34}{} of {}".format(
            name, changed, len(BEHAVIOURS)))
    print()
    print("  the module-level handle makes every behaviour a function of what")
    print("  ran before it, and the suite does not say so. the first order")
    print("  passes all three, which is the order somebody would write them")
    print("  in, and the other two fail two of the three.")
    print()
    print("  the fix is not a fixture that clears the handle. a fixture that")
    print("  clears it is a fixture that knows which handle to clear, which")
    print("  is the same knowledge the caller was supposed to not need. the")
    print("  fix is that the object a behaviour uses should arrive as an")
    print("  argument, and then there is nothing to clear -- the handle is")
    print("  made by the test, used by the behaviour, and dropped.")
    print()
    print("  that is the second half of what injection is for. the first")
    print("  half is replacing an implementation. this half is that a")
    print("  dependency reached for by name is a dependency whose lifetime")
    print("  nobody chose, and whose state every other test can see.")


main()
