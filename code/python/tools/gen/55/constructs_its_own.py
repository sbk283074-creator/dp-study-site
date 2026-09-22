"""Chapter 55 -- what injection changes, measured on a test suite.

A ledger that builds its own database handle, and the same ledger taking
one as an argument. Six behaviours, and the count is of the behaviours a
test can hand a stand-in to.
"""

import pathlib


class RealDB:
    """Stands in for a driver. Constructing it is the thing a unit test
    is trying not to do."""

    def __init__(self):
        self.rows = {"a": 0}

    def get(self, key):
        return self.rows.get(key, 0)

    def add(self, key, amount):
        self.rows[key] = self.get(key) + amount
        return self.rows[key]


# --- own
class LedgerOwn:
    def __init__(self):
        self.db = RealDB()

    def balance(self):
        return self.db.get("a")

    def deposit(self, amount):
        return self.db.add("a", amount)


# --- injected
class LedgerInjected:
    def __init__(self, db):
        self.db = db

    def balance(self):
        return self.db.get("a")

    def deposit(self, amount):
        return self.db.add("a", amount)
# --- end


class FakeDB:
    """The stand-in: the same two methods and no database."""

    def __init__(self):
        self.rows = {}
        self.calls = []

    def get(self, key):
        return self.rows.get(key, 0)

    def add(self, key, amount):
        self.calls.append((key, amount))
        self.rows[key] = self.get(key) + amount
        return self.rows[key]


def reads_zero(ledger):
    return ledger.balance() == 0


def one_deposit(ledger):
    return ledger.deposit(5) == 5


def deposits_accumulate(ledger):
    ledger.deposit(5)
    ledger.deposit(3)
    return ledger.balance() == 8


def zero_changes_nothing(ledger):
    ledger.deposit(0)
    return ledger.balance() == 0


def balance_is_a_number(ledger):
    return isinstance(ledger.balance(), int)


def negative_is_allowed(ledger):
    return ledger.deposit(-2) == -2


BEHAVIOURS = [
    ("a new ledger reads zero", reads_zero),
    ("one deposit is visible", one_deposit),
    ("deposits accumulate", deposits_accumulate),
    ("a zero deposit changes nothing", zero_changes_nothing),
    ("the balance is a number", balance_is_a_number),
    ("a negative deposit is allowed", negative_is_allowed),
]

SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
OWN_SRC = SOURCE.split("# --- own")[1].split("# --- injected")[0]
INJ_SRC = SOURCE.split("# --- injected")[1].split("# --- end")[0]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def can_be_handed_a_stand_in(cls):
    """The measurement, and it is a question about the constructor."""
    try:
        cls(FakeDB())
        return True
    except TypeError:
        return False


def run_all(make):
    passed = 0
    for _, behaviour in BEHAVIOURS:
        try:
            passed += 1 if behaviour(make()) else 0
        except Exception:
            pass
    return passed


def main():
    print(f"  behaviours                          {len(BEHAVIOURS)}")
    print()
    print("    design                    accepts a stand-in   names the real type")
    designs = (
        ("constructs its own", LedgerOwn, OWN_SRC),
        ("takes one as an argument", LedgerInjected, INJ_SRC),
    )
    isolated = {}
    for label, cls, source in designs:
        isolated[label] = can_be_handed_a_stand_in(cls)
        print("    {:<26}{:<20}{}".format(
            label,
            "yes" if isolated[label] else "no",
            "%d place(s)" % mentions(source, "RealDB")))
    print()

    print("    the same six behaviours, run against each design")
    for label, make in (("the self-constructing design", LedgerOwn),
                        ("the injected design",
                         lambda: LedgerInjected(FakeDB()))):
        print("    {:<38}{} of {}".format(
            label, run_all(make), len(BEHAVIOURS)))
    print()

    print("    behaviours a test can hand a stand-in to")
    for label, _, _ in designs:
        count = len(BEHAVIOURS) if isolated[label] else 0
        print("    {:<34}{} of {}".format(label, count, len(BEHAVIOURS)))
    print()
    print("  both suites are green, and that is the whole point. the")
    print("  self-constructing design passes all six behaviours against the")
    print("  real driver, so nothing in the suite reports a problem -- and not")
    print("  one of the six can be handed a different implementation, because")
    print("  there is no parameter to pass it through.")
    print()
    print("  the one line that names `RealDB` is the line that decides this.")
    print("  injection is not a style. it is the difference between a test")
    print("  that runs the dependency and a test that replaces it, and the")
    print("  count of behaviours that can be replaced is zero until the")
    print("  dependency is a parameter.")


main()
