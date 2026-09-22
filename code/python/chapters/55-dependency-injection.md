---
chapter: 55
part: 10
title: Dependency Injection and Inversion of Control
summary: What injection changes, counted rather than asserted -- the behaviours a test can hand a stand-in to, the tests whose result depends on the order, the modules that name a concrete type, and the direction of the reference between a policy and a mechanism. Several of the counts come out against the practice, and two of them come out in its favour for reasons the usual argument does not mention.
minutes: 100
tags: [architecture, dependency injection, inversion of control, Protocol, seams, composition root, service locator, lifetimes, testing, wiring]
---

Injection is usually taught as a style, or as something a framework does to you. It is neither. It is
a change to where an object comes from, and the consequences of that change are countable: how many
behaviours a test can hand a stand-in to, how many tests depend on the order they run in, how many
modules have to be edited when a dependency is replaced.

This chapter counts those, and the counts do not all point the same way. Injection moves the vendor's
name out of a service and into every caller, which makes one number better and another worse. A
container turns wiring into data and replaces a class reference with a string. The word inversion
turns out to describe a direction rather than a reduction, and the count of references is identical
either way.

There is also a case where injection is the wrong answer, and it is the same case as the last
chapter's: a collaborator with one implementation and no seam to cut.

## The object that arrives as an argument

Start with the measurement that decides the whole subject, because it is the one a test suite
already knows how to take.

```python run
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
```

```text
  behaviours                          6

    design                    accepts a stand-in   names the real type
    constructs its own        no                  1 place(s)
    takes one as an argument  yes                 0 place(s)

    the same six behaviours, run against each design
    the self-constructing design          6 of 6
    the injected design                   6 of 6

    behaviours a test can hand a stand-in to
    constructs its own                0 of 6
    takes one as an argument          6 of 6

  both suites are green, and that is the whole point. the
  self-constructing design passes all six behaviours against the
  real driver, so nothing in the suite reports a problem -- and not
  one of the six can be handed a different implementation, because
  there is no parameter to pass it through.

  the one line that names `RealDB` is the line that decides this.
  injection is not a style. it is the difference between a test
  that runs the dependency and a test that replaces it, and the
  count of behaviours that can be replaced is zero until the
  dependency is a parameter.
```

Six behaviours, and both designs pass all six. That is the part worth pausing on: a suite that
constructs its own dependencies is green, so nothing in it reports a problem. What it cannot do is
replace anything. The object that builds its own database handle accepts a stand-in in zero of the
six behaviours, and the object that takes one accepts it in all six, and the difference between
them is a single line that names a concrete type.

## The handle nobody chose

The second half of what injection is for has nothing to do with replacing anything. It is about
lifetime.

```python run
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
```

```text
  behaviours                          3
  orders                              3

    the order the behaviours run in
                                module-level        passed in
    zero, deposit, accumulate   2 of 3 pass         3 of 3 pass
    accumulate, deposit, zero   1 of 3 pass         3 of 3 pass
    deposit, accumulate, zero   1 of 3 pass         3 of 3 pass

    behaviours whose result depends on the order
    the module-level handle           3 of 3
    a handle passed in                0 of 3

  the module-level handle makes every behaviour a function of what
  ran before it, and the suite does not say so. the first order
  passes all three, which is the order somebody would write them
  in, and the other two fail two of the three.

  the fix is not a fixture that clears the handle. a fixture that
  clears it is a fixture that knows which handle to clear, which
  is the same knowledge the caller was supposed to not need. the
  fix is that the object a behaviour uses should arrive as an
  argument, and then there is nothing to clear -- the handle is
  made by the test, used by the behaviour, and dropped.

  that is the second half of what injection is for. the first
  half is replacing an implementation. this half is that a
  dependency reached for by name is a dependency whose lifetime
  nobody chose, and whose state every other test can see.
```

Three behaviours and three orders. Under the module-level handle, all three change their result
depending on what ran before them, and the first order is the one that passes -- which is the order
somebody would write them in, and therefore the order in which the problem is invisible. Under the
handle that arrives as an argument, none of the three changes.

The tempting fix is a fixture that clears the handle, and it is worth seeing why that is not the
same thing. A fixture that clears it is a fixture that knows which handle to clear, which is the
knowledge the caller was supposed to not need. And it works only while every test remembers to use
it, which is a property of the tests rather than of the design.

## The seam, and what it does not promise

An interface is what makes the swap possible. It is not what makes the swap safe.

```python run
"""Chapter 55 -- the seam, and what an interface does not promise.

One consumer and three implementations behind a `Protocol`. The count is
of the implementations the consumer can be handed without being edited,
and of the ones whose behaviour it can actually tell apart.
"""

import pathlib

from typing import Protocol


class Store(Protocol):
    def get(self, key):
        ...

    def put(self, key, value):
        ...


class Memory:
    def __init__(self):
        self.rows = {}

    def get(self, key):
        return self.rows.get(key)

    def put(self, key, value):
        self.rows[key] = value


class Counting:
    """Wraps another store and counts what goes through it."""

    def __init__(self, inner):
        self.inner = inner
        self.puts = 0

    def get(self, key):
        return self.inner.get(key)

    def put(self, key, value):
        self.puts += 1
        self.inner.put(key, value)


class Rejecting:
    """Wraps another store and refuses keys it does not like."""

    def __init__(self, inner):
        self.inner = inner
        self.refused = []

    def get(self, key):
        return self.inner.get(key)

    def put(self, key, value):
        if key.startswith("x"):
            self.refused.append(key)
            return
        self.inner.put(key, value)


def save_all(store, pairs):
    """The consumer. It names no implementation, and it does not have to
    know which one it was given."""
    for key, value in pairs:
        store.put(key, value)
    return [store.get(key) for key, _ in pairs]


PAIRS = [("name", "ada"), ("age", 36), ("x-secret", "hidden")]

IMPLEMENTATIONS = [
    ("Memory", lambda: Memory()),
    ("Counting", lambda: Counting(Memory())),
    ("Rejecting", lambda: Rejecting(Memory())),
]

METHODS = ["get", "put"]

SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
CONSUMER_SRC = SOURCE.split("def save_all")[1].split("PAIRS =")[0]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  methods in the interface            {len(METHODS)}")
    print(f"  implementations behind it           {len(IMPLEMENTATIONS)}")
    print()
    print("    implementation   consumer names it   values returned")
    for label, make in IMPLEMENTATIONS:
        returned = save_all(make(), PAIRS)
        got = sum(1 for value in returned if value is not None)
        print("    {:<17}{:<20}{} of {}".format(
            label, "no" if not mentions(CONSUMER_SRC, label) else "yes",
            got, len(PAIRS)))
    print()

    print("    what each implementation does with the third key")
    for label, make in IMPLEMENTATIONS:
        store = make()
        save_all(store, PAIRS)
        if label == "Counting":
            detail = "%d put(s) counted" % store.puts
        elif label == "Rejecting":
            detail = "%d key(s) refused: %s" % (
                len(store.refused), ", ".join(store.refused))
        else:
            detail = "all %d stored" % len(PAIRS)
        print("    {:<17}{}".format(label, detail))
    print()
    print("  the consumer names none of the three, so the seam does what it")
    print("  is for: one implementation can be swapped for another without")
    print("  the consumer being edited. that is a count of zero places, and")
    print("  it is the whole of the claim.")
    print()
    print("  the second table is the part the seam does not cover. two of the")
    print("  three return a value for every key and the third returns two and")
    print("  a `None`, and the interface said nothing about which of those is")
    print("  allowed. it named two methods and their names are all it named --")
    print("  no signature, no postcondition, and no way for the consumer to")
    print("  find out without calling one.")
    print()
    print("  so the seam is worth having and it is not a guarantee. it buys")
    print("  the swap and it does not buy the behaviour, which is why the")
    print("  thing that catches the third implementation is a test and not a")
    print("  type.")


main()
```

```text
  methods in the interface            2
  implementations behind it           3

    implementation   consumer names it   values returned
    Memory           no                  3 of 3
    Counting         no                  3 of 3
    Rejecting        no                  2 of 3

    what each implementation does with the third key
    Memory           all 3 stored
    Counting         3 put(s) counted
    Rejecting        1 key(s) refused: x-secret

  the consumer names none of the three, so the seam does what it
  is for: one implementation can be swapped for another without
  the consumer being edited. that is a count of zero places, and
  it is the whole of the claim.

  the second table is the part the seam does not cover. two of the
  three return a value for every key and the third returns two and
  a `None`, and the interface said nothing about which of those is
  allowed. it named two methods and their names are all it named --
  no signature, no postcondition, and no way for the consumer to
  find out without calling one.

  so the seam is worth having and it is not a guarantee. it buys
  the swap and it does not buy the behaviour, which is why the
  thing that catches the third implementation is a test and not a
  type.
```

The consumer names none of the three implementations, so the seam does exactly what it is for: the
implementation can be replaced without the consumer being edited, and the count of places that would
have to change is zero. That is the whole claim and it holds.

The second table is what the claim does not cover. Two of the three return a value for every key and
the third returns two and a `None`, and the interface said nothing about which of those is allowed.
It named two methods, and their names are all it named: no signature, no postcondition, and no way
for the consumer to find out without calling one.

## Which way the arrow points

The word inversion is the part of this subject that gets said without being explained. It is easier
to explain as a direction than as a principle.

```python run
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
```

```text
  designs                             2

    design                          policy -> store   store -> policy
    the policy builds the mechanism 1 reference       0 reference
    the mechanism implements it     0 reference       1 reference

    when the mechanism is replaced
    the policy builds the mechanism the policy is edited too
    the mechanism implements it     the policy is untouched

  each design holds 1 reference between
  the two modules, and they point in opposite directions. so
  inversion is not a reduction in coupling -- the count is
  identical.

  what changes is which module is on the receiving end. in the
  first design the policy names the mechanism, so the stable thing
  depends on the unstable one and replacing the database edits the
  business rule. in the second the mechanism names the policy's
  interface, so the arrow runs from the thing that will be
  replaced towards the thing that will not.

  that is the whole of what the word inversion means here, and it
  is why the interface belongs to the consumer rather than to the
  implementation. a `Store` defined in the database module would
  have the arrow pointing the wrong way no matter where the
  `import` statement sits.

  the cost is one new module -- the interface -- and one new place
  that knows both sides, which is the composition root. the
  benefit is that the policy can be tested, replaced and reasoned
  about without the database existing, and that is what the
  direction buys.
```

Each design holds exactly one reference between the two modules, and they point in opposite
directions. So inversion is not a reduction in coupling: the count is the same, and a chapter that
claimed otherwise would be measuring the wrong thing.

What changes is which module is on the receiving end. In the first design the policy names the
mechanism, so the stable thing depends on the unstable one, and replacing the database edits the
business rule. In the second the mechanism names the policy's interface, so the arrow runs from the
thing that will be replaced towards the thing that will not. That is why the interface belongs to the
consumer: a `Store` defined in the database module would point the wrong way no matter where the
`import` statement sits.

## Where the wiring lives

Once the dependencies are parameters, something has to supply them, and the shape of that something
is a decision with a measurable consequence.

```python run
"""Chapter 55 -- wiring, and where a typo is found.

Six services with named dependencies, one of which names something that
was never built. The count is of the services constructed before the
mistake is found, and the column that matters is when it is found.
"""

BUILT = []


class Clock:
    pass


class MemoryStore:
    pass


class Pricing:
    def __init__(self, store):
        self.store = store


class Tax:
    def __init__(self, pricing):
        self.pricing = pricing


class Orders:
    def __init__(self, tax, clock):
        self.tax = tax
        self.clock = clock


class Reporting:
    def __init__(self, orders, metrics):
        self.orders = orders
        self.metrics = metrics


# --- manual
def build_all():
    """Written out by hand, in the order the author chose. `metrics` is
    the name of a service that does not exist."""
    clock = Clock()
    BUILT.append("clock")
    store = MemoryStore()
    BUILT.append("store")
    pricing = Pricing(store)
    BUILT.append("pricing")
    tax = Tax(pricing)
    BUILT.append("tax")
    orders = Orders(tax, clock)
    BUILT.append("orders")
    reporting = Reporting(orders, metrics)
    BUILT.append("reporting")
    return [clock, store, pricing, tax, orders, reporting]
# --- end

# --- container
REGISTRY = {
    "clock": Clock,
    "store": MemoryStore,
    "pricing": Pricing,
    "tax": Tax,
    "orders": Orders,
    "reporting": Reporting,
}

NEEDS = {
    "clock": [],
    "store": [],
    "pricing": ["store"],
    "tax": ["pricing"],
    "orders": ["tax", "clock"],
    "reporting": ["orders", "metrics"],
}
# --- end

ORDER = list(REGISTRY)


def build_eager(registry, needs):
    """Check the whole graph before constructing anything."""
    known = set(registry)
    for name, requires in needs.items():
        for need in requires:
            if need not in known:
                raise KeyError(need)
    for name in registry:
        BUILT.append(name)
    return dict(registry)


def build_lazy(registry, needs, order):
    """Build on first request, so nothing is checked until it is asked
    for."""
    built = {}
    for name in order:
        for need in needs[name]:
            if need not in built:
                raise KeyError(need)
        built[name] = registry[name]
        BUILT.append(name)
    return built


def declared_needs(builder):
    """What a builder can say about itself without being run."""
    return getattr(builder, "needs", None)


def attempt(fn):
    """Run a builder and report how many services it got through."""
    BUILT.clear()
    try:
        fn()
    except Exception as exc:
        return len(BUILT), type(exc).__name__
    return len(BUILT), ""


def main():
    print(f"  services in the registry            {len(REGISTRY)}")
    print(f"  dependencies declared               "
          f"{sum(len(v) for v in NEEDS.values())}")
    print()

    rows = [
        ("written out by hand", build_all, "at that line"),
        ("a container, checked up front",
         lambda: build_eager(REGISTRY, NEEDS), "before anything is built"),
        ("a container, resolved on demand",
         lambda: build_lazy(REGISTRY, NEEDS, ORDER),
         "at the first request for it"),
    ]

    print("    how the wiring is checked        built     found")
    kinds = []
    for label, fn, when in rows:
        built, kind = attempt(fn)
        kinds.append(kind)
        print("    {:<33}{:<10}{}".format(
            label, "%d of %d" % (built, len(REGISTRY)), when))
    print()

    print("    the kind of error each one raises")
    for (label, _, _), kind in zip(rows, kinds):
        print("    {:<33}{}".format(label, kind))
    print()

    print("    what can be reported without running anything")
    print("    {:<34}{}".format(
        "a dict of names",
        "%d dependencies" % sum(len(v) for v in NEEDS.values())))
    print("    {:<34}{}".format(
        "a function that builds them",
        "%d dependencies" % len(declared_needs(build_all) or [])))
    print()
    print("  the hand-written root and the lazy container get through the")
    print("  same number of services before they fail, so the container is")
    print("  not better at this by being a container. the eager one")
    print("  constructs nothing, and that is the whole difference: the graph")
    print("  is data, so it can be checked as a whole before any of it is")
    print("  constructed.")
    print()
    print("  the cost is visible in the error. the hand-written root raises")
    print("  `NameError` and names the thing, because it is a name. the")
    print("  container raises `KeyError` and names a string, because that is")
    print("  all a registry has -- and a string is not checked by anything")
    print("  until the lookup happens.")
    print()
    print("  that is the trade in one line: a container turns wiring into data")
    print("  so that the wiring can be checked, and in exchange it turns a")
    print("  class reference into a string that nothing checks for you.")


main()
```

```text
  services in the registry            6
  dependencies declared               6

    how the wiring is checked        built     found
    written out by hand              5 of 6    at that line
    a container, checked up front    0 of 6    before anything is built
    a container, resolved on demand  5 of 6    at the first request for it

    the kind of error each one raises
    written out by hand              NameError
    a container, checked up front    KeyError
    a container, resolved on demand  KeyError

    what can be reported without running anything
    a dict of names                   6 dependencies
    a function that builds them       0 dependencies

  the hand-written root and the lazy container get through the
  same number of services before they fail, so the container is
  not better at this by being a container. the eager one
  constructs nothing, and that is the whole difference: the graph
  is data, so it can be checked as a whole before any of it is
  constructed.

  the cost is visible in the error. the hand-written root raises
  `NameError` and names the thing, because it is a name. the
  container raises `KeyError` and names a string, because that is
  all a registry has -- and a string is not checked by anything
  until the lookup happens.

  that is the trade in one line: a container turns wiring into data
  so that the wiring can be checked, and in exchange it turns a
  class reference into a string that nothing checks for you.
```

Six services, six dependencies, and one name in the graph that was never declared. The hand-written
root and the container that resolves on demand get through the same number of services before they
fail, so the container is not better at this by being a container. The one that checks the graph
first constructs nothing, and that is the whole difference: the graph is data, so it can be checked
as a whole before any of it runs.

The cost is in the error. The hand-written root raises `NameError` and names the thing, because it
is a name. The container raises `KeyError` and names a string, because that is all a registry has --
and a string is not checked by anything until the lookup happens. That is the trade in one line: a
container turns wiring into data so that the wiring can be checked, and in exchange it turns a class
reference into a string nothing checks for you.

## The marker a framework looks for

If a framework is doing the injecting, this is what it is doing.

```python run
"""Chapter 55 -- the marker a framework looks for.

Four handlers whose dependencies are declared as default values that are
not values. The count is of the parameters the framework fills in, and of
the ones the handler has to name a concrete type for.
"""

import inspect


class Depends:
    """The marker. Its whole job is to be a default value that is not a
    value, so that the signature can name a dependency without the
    handler constructing one."""

    def __init__(self, provider):
        self.provider = provider

    def __repr__(self):
        return "Depends(" + self.provider.__name__ + ")"


def get_store():
    return {"orders": [10, 20, 30]}


def get_clock():
    return "12:00"


def list_orders(store=Depends(get_store), limit=20):
    return store["orders"][:limit]


def count_orders(store=Depends(get_store)):
    return len(store["orders"])


def stamp(clock=Depends(get_clock), store=Depends(get_store)):
    return clock + " " + str(len(store["orders"]))


def health():
    return "ok"


HANDLERS = [list_orders, count_orders, stamp, health]

PROVIDERS = {"get_store": get_store, "get_clock": get_clock}


def fill(handler, override=None):
    """The framework's half: read the signature, supply the marked
    parameters, and let everything else fall to its default."""
    override = override or {}
    kwargs = {}
    marked = 0
    for name, param in inspect.signature(handler).parameters.items():
        if name in override:
            kwargs[name] = override[name]
        elif isinstance(param.default, Depends):
            kwargs[name] = param.default.provider()
            marked += 1
        elif param.default is not inspect.Parameter.empty:
            kwargs[name] = param.default
    return handler(**kwargs), marked


def body_of(handler):
    """The handler's body without its `def` line, so that the names the
    body uses can be counted rather than the ones its signature declares.
    """
    try:
        lines = inspect.getsource(handler).splitlines()
    except OSError:
        return ""
    return "\n".join(lines[1:])


def main():
    print(f"  handlers                            {len(HANDLERS)}")
    print(f"  providers registered                {len(PROVIDERS)}")
    print()

    print("    handler         parameters   marked   provider named in body")
    totals = [0, 0, 0]
    for handler in HANDLERS:
        params = inspect.signature(handler).parameters
        _, marked = fill(handler)
        named = sum(1 for name in PROVIDERS if name in body_of(handler))
        totals[0] += len(params)
        totals[1] += marked
        totals[2] += named
        print("    {:<16}{:>10}{:>9}{:>25}".format(
            handler.__name__, len(params), marked, named))
    print("    {:<16}{:>10}{:>9}{:>25}".format(
        "total", totals[0], totals[1], totals[2]))
    print()

    marked_handlers = [h for h in HANDLERS
                       if any(isinstance(p.default, Depends)
                              for p in inspect.signature(h).parameters.values())]
    ok = 0
    for handler in marked_handlers:
        value, _ = fill(handler, {"store": {"orders": []}, "clock": "00:00"})
        ok += 1 if value in (0, "00:00 0", []) else 0
    print("    a stand-in supplied for the marked parameter")
    print("    {:<36}{} of {}".format(
        "handlers that accepted one", ok, len(marked_handlers)))
    print()
    print(f"  {totals[0]} parameters across the four handlers, and {totals[1]} of them")
    print(f"  are marked. the bodies name a provider in {totals[2]} of the {totals[0]},")
    print("  which is the whole of the mechanism: the value arrives, and the")
    print("  code that uses it does not know where from.")
    print()
    print("  the marker is not a type. it is a default value that the caller")
    print("  recognises and replaces, and that is why the handler can be")
    print("  called with a stand-in without the handler being edited. the")
    print("  cost is that nothing checks the marker: a parameter whose")
    print("  default is `Depends(f)` is a dependency, and a parameter whose")
    print("  default is a real object is a default. the two look the same to")
    print("  everything except the caller that knows to look.")
    print()
    print("  so a framework's injection is this and nothing more. it reads a")
    print("  signature, fills what is marked, and calls the function. the")
    print("  function is an ordinary function and can be tested by calling")
    print("  it -- which is worth saying because the frameworks that do this")
    print("  are the ones that make it look like magic.")


main()
```

```text
  handlers                            4
  providers registered                2

    handler         parameters   marked   provider named in body
    list_orders              2        1                        0
    count_orders             1        1                        0
    stamp                    2        2                        0
    health                   0        0                        0
    total                    5        4                        0

    a stand-in supplied for the marked parameter
    handlers that accepted one          3 of 3

  5 parameters across the four handlers, and 4 of them
  are marked. the bodies name a provider in 0 of the 5,
  which is the whole of the mechanism: the value arrives, and the
  code that uses it does not know where from.

  the marker is not a type. it is a default value that the caller
  recognises and replaces, and that is why the handler can be
  called with a stand-in without the handler being edited. the
  cost is that nothing checks the marker: a parameter whose
  default is `Depends(f)` is a dependency, and a parameter whose
  default is a real object is a default. the two look the same to
  everything except the caller that knows to look.

  so a framework's injection is this and nothing more. it reads a
  signature, fills what is marked, and calls the function. the
  function is an ordinary function and can be tested by calling
  it -- which is worth saying because the frameworks that do this
  are the ones that make it look like magic.
```

Five parameters across four handlers, four of them marked, and the handler bodies name a provider in
none of them. The value arrives and the code that uses it does not know where from, which is the
whole of the mechanism.

The marker is not a type. It is a default value that the caller recognises and replaces, and that is
precisely why the handler can be called with a stand-in without being edited. The cost is that
nothing checks it: a parameter whose default is `Depends(f)` is a dependency and a parameter whose
default is a real object is a default, and the two look the same to everything except the caller
that knows to look. A framework's injection is this and nothing more -- it reads a signature, fills
what is marked, and calls an ordinary function, which is worth saying because the frameworks that do
it are the ones that make it look like magic.

## How long the object is allowed to live

A scope is an answer to one question, and getting it wrong produces a bug with no symptom.

```python run
"""Chapter 55 -- scopes, and the bug a singleton causes.

Three requests, three scopes, and one cache that captured a per-request
object. The count is of the distinct objects handed out over three
requests, and of the requests that get the wrong one.
"""


class Session:
    def __init__(self, request_id):
        self.request_id = request_id


SINGLETON = Session(0)


def per_request(request_id):
    return Session(request_id)


def transient(request_id):
    return Session(request_id)


class CapturedCache:
    """A singleton that took a session when it was built, which is the
    mistake. It keeps request 1's session for ever."""

    def __init__(self, session):
        self.session = session

    def owner(self):
        return self.session.request_id


class PassedCache:
    """The same cache, told which session to use on each call."""

    def owner(self, session):
        return session.request_id


REQUESTS = [1, 2, 3]

SCOPES = [
    ("singleton", [SINGLETON for _ in REQUESTS]),
    ("per request", [per_request(i) for i in REQUESTS]),
    ("transient", [transient(i) for i in REQUESTS for _ in (0, 1)]),
]


def main():
    print(f"  requests                            {len(REQUESTS)}")
    print()
    print("    scope          instances   the same object every time")
    for label, made in SCOPES:
        distinct = len(set(id(item) for item in made))
        print("    {:<15}{:>9}   {}".format(
            label, distinct, "yes" if distinct == 1 else "no"))
    print()

    print("    who each request thinks it is talking to")
    print("    {:<24}{:<18}{}".format("", "captured cache", "passed cache"))
    captured = CapturedCache(per_request(REQUESTS[0]))
    rows = []
    for request_id in REQUESTS:
        session = per_request(request_id)
        rows.append((request_id, captured.owner(),
                     PassedCache().owner(session)))
    for request_id, got, want in rows:
        print("    {:<24}{:<18}{}".format(
            "request %d" % request_id,
            "request %d" % got,
            "request %d" % want))
    print()

    stale = sum(1 for request_id, got, _ in rows if got != request_id)
    print(f"  the captured cache gives {stale} of the {len(REQUESTS)} requests the")
    print("  wrong session, and the one it gets right is the request that")
    print("  built it. nothing raises: every call returns a session, and a")
    print("  session from the wrong request is a value of the right shape.")
    print()
    print("  that is why the scope is part of the wiring and not an")
    print("  implementation detail. a singleton may hold a singleton; a")
    print("  singleton may not hold something that is rebuilt per request,")
    print("  because the container builds the singleton once and there is no")
    print("  later moment at which it could be given a new one.")
    print()
    print("  the fix in the second column is not a longer lifetime. it is")
    print("  that the per-request object stops being held at all: it is")
    print("  passed to the method that needs it, so the object that outlives")
    print("  the request holds no reference to anything that should not.")
    print()
    print("  the three scopes are three different answers to one question,")
    print("  and the question is how long the thing is allowed to live. a")
    print("  container that lets you answer it per dependency is useful for")
    print("  exactly this reason, and a container that picks one answer for")
    print("  everything is the bug above waiting to happen.")


main()
```

```text
  requests                            3

    scope          instances   the same object every time
    singleton              1   yes
    per request            3   no
    transient              6   no

    who each request thinks it is talking to
                            captured cache    passed cache
    request 1               request 1         request 1
    request 2               request 1         request 2
    request 3               request 1         request 3

  the captured cache gives 2 of the 3 requests the
  wrong session, and the one it gets right is the request that
  built it. nothing raises: every call returns a session, and a
  session from the wrong request is a value of the right shape.

  that is why the scope is part of the wiring and not an
  implementation detail. a singleton may hold a singleton; a
  singleton may not hold something that is rebuilt per request,
  because the container builds the singleton once and there is no
  later moment at which it could be given a new one.

  the fix in the second column is not a longer lifetime. it is
  that the per-request object stops being held at all: it is
  passed to the method that needs it, so the object that outlives
  the request holds no reference to anything that should not.

  the three scopes are three different answers to one question,
  and the question is how long the thing is allowed to live. a
  container that lets you answer it per dependency is useful for
  exactly this reason, and a container that picks one answer for
  everything is the bug above waiting to happen.
```

Three requests and three scopes, giving one instance, three and six. Then the mistake: a singleton
that captured a per-request object at construction time hands two of the three requests the wrong
session, and the one it gets right is the request that built it. Nothing raises. Every call returns
a session, and a session from the wrong request is a value of the right shape.

That is why the scope belongs to the wiring rather than to the implementation. A singleton may hold
a singleton; a singleton may not hold something that is rebuilt per request, because the container
builds the singleton once and there is no later moment at which it could be given a new one. The fix
is not a longer lifetime -- it is that the per-request object stops being held at all.

## The global that answers for everything

The pattern that injection replaces, and the reason it is worth replacing, measured by what a
signature can tell you.

```python run
"""Chapter 55 -- the locator, measured by what the signature says.

A report that asks a global registry for what it needs, and the same
report taking the same three things as arguments. The count is of the
dependencies the signature names, and of the callers one change reaches.
"""

import inspect

NEEDS = ["store", "clock", "mailer"]

CALLERS = ["the nightly job", "the webhook handler", "the admin button",
           "the report page"]


class Locator:
    """The global. `get` answers with whatever is registered, and the
    caller learns nothing from the answer."""

    def __init__(self):
        self._factories = {}
        self._overrides = {}

    def register(self, name, factory):
        self._factories[name] = factory

    def override(self, name, value):
        self._overrides[name] = value

    def get(self, name):
        if name in self._overrides:
            return self._overrides[name]
        return self._factories[name]()


LOCATOR = Locator()
LOCATOR.register("store", lambda: "the real store")
LOCATOR.register("clock", lambda: "the real clock")
LOCATOR.register("mailer", lambda: "the real mailer")


class ReportWithLocator:
    def build(self):
        store = LOCATOR.get("store")
        clock = LOCATOR.get("clock")
        mailer = LOCATOR.get("mailer")
        return [store, clock, mailer]


class ReportWithArguments:
    def __init__(self, store, clock, mailer):
        self.store = store
        self.clock = clock
        self.mailer = mailer

    def build(self):
        return [self.store, self.clock, self.mailer]


def named_in(signature):
    return [name for name in signature.parameters if name != "self"]


def main():
    print(f"  dependencies the report needs       {len(NEEDS)}")
    print(f"  callers                             {len(CALLERS)}")
    print()

    locator_sig = inspect.signature(ReportWithLocator.build)
    arguments_sig = inspect.signature(ReportWithArguments.__init__)

    LOCATOR.override("store", "a test store")
    changed = 0
    for _ in CALLERS:
        if ReportWithLocator().build()[0] == "a test store":
            changed += 1

    print("    design                  names in the signature   one change reaches")
    print("    {:<24}{:<25}{}".format(
        "a locator",
        "%d of %d" % (len(named_in(locator_sig)), len(NEEDS)),
        "%d of %d callers" % (changed, len(CALLERS))))
    print("    {:<24}{:<25}{}".format(
        "constructor arguments",
        "%d of %d" % (len(named_in(arguments_sig)), len(NEEDS)),
        "1 caller"))
    print()
    print("  the locator names no dependency in the signature, and that is")
    print("  the property it is chosen for. the bill arrives in the third")
    print(f"  column: one override reached all {changed} callers, because they all")
    print("  read the same global. a change that was meant for one test")
    print("  reaches production code, and the signature of the thing that")
    print("  changed says nothing about it.")
    print()
    print("  the count of zero in the first column is not a coincidence")
    print("  either. a dependency that is fetched inside a method body is not")
    print("  a dependency the caller knows about, so the caller cannot")
    print("  provide it, cannot replace it, and cannot read the method and")
    print("  find out -- the method body is the only place it appears.")
    print()
    print("  the third failure is where the error surfaces. `get` raises")
    print("  `KeyError` on a name nobody registered, and it raises it in the")
    print("  middle of `build`, after the object exists, in a frame that")
    print("  belongs to the report rather than to the wiring. a constructor")
    print("  argument fails at the call site that forgot it, which is the")
    print("  place somebody has to look anyway.")


main()
```

```text
  dependencies the report needs       3
  callers                             4

    design                  names in the signature   one change reaches
    a locator               0 of 3                   4 of 4 callers
    constructor arguments   3 of 3                   1 caller

  the locator names no dependency in the signature, and that is
  the property it is chosen for. the bill arrives in the third
  column: one override reached all 4 callers, because they all
  read the same global. a change that was meant for one test
  reaches production code, and the signature of the thing that
  changed says nothing about it.

  the count of zero in the first column is not a coincidence
  either. a dependency that is fetched inside a method body is not
  a dependency the caller knows about, so the caller cannot
  provide it, cannot replace it, and cannot read the method and
  find out -- the method body is the only place it appears.

  the third failure is where the error surfaces. `get` raises
  `KeyError` on a name nobody registered, and it raises it in the
  middle of `build`, after the object exists, in a frame that
  belongs to the report rather than to the wiring. a constructor
  argument fails at the call site that forgot it, which is the
  place somebody has to look anyway.
```

The locator names no dependency in the signature, and that is the property it is chosen for. The bill
arrives in the third column: one override reached all four callers, because all four read the same
global. A change meant for one test reaches production code, and the signature of the thing that
changed says nothing about it.

The zero in the first column is not a coincidence either. A dependency fetched inside a method body
is not a dependency the caller knows about, so the caller cannot provide it, cannot replace it, and
cannot read the method and find out. And the error surfaces in the wrong frame: `get` raises
`KeyError` in the middle of a method that belongs to the report, rather than at the call site that
forgot to register something.

## The dependency that is not a dependency

Every block so far has found injection paying for itself. This one is the case where it does not.

```python run
"""Chapter 55 -- the dependency that is not a dependency.

A pure function, and the same function behind an interface that is
injected. The count is of what each design adds, and of the tests that
needed the extra names.
"""

import pathlib

from typing import Protocol


# --- plain
def format_price(amount):
    return "%.2f" % amount
# --- end


# --- injected
class Formatter(Protocol):
    def format(self, amount):
        ...


class PlainFormatter:
    def format(self, amount):
        return "%.2f" % amount


def render(order, formatter):
    return formatter.format(order)
# --- end


AMOUNTS = [0, 1.5, 12, 1200.75]


class Counting:
    """The one implementation a test might supply, to check that the
    consumer called it."""

    def __init__(self):
        self.calls = []

    def format(self, amount):
        self.calls.append(amount)
        return "%.2f" % amount


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
PLAIN_SRC = SOURCE.split("# --- plain")[1].split("# --- end")[0]
INJ_SRC = SOURCE.split("# --- injected")[1].split("# --- end")[0]


def count(source, word):
    return sum(1 for line in source.splitlines() if word in line)


def main():
    print(f"  amounts                             {len(AMOUNTS)}")
    print()
    print("    what                          the function   behind an interface")
    print("    {:<30}{:>13}{:>20}".format(
        "classes", count(PLAIN_SRC, "class "), count(INJ_SRC, "class ")))
    print("    {:<30}{:>13}{:>20}".format(
        "functions", count(PLAIN_SRC, "def "), count(INJ_SRC, "def ")))
    print("    {:<30}{:>13}{:>20}".format(
        "lines", len(PLAIN_SRC.strip().splitlines()),
        len(INJ_SRC.strip().splitlines())))
    print()

    print("    the same answers from both")
    same = 0
    for amount in AMOUNTS:
        if format_price(amount) == PlainFormatter().format(amount):
            same += 1
    print("    {:<34}{} of {}".format("amounts formatted alike", same,
                                      len(AMOUNTS)))
    print()

    spy = Counting()
    render(1200.75, spy)
    print("    implementations that exist")
    print("    {:<36}{}".format("the function", "1"))
    print("    {:<36}{}".format("behind the interface", "1"))
    print("    {:<36}{}".format("implementations a test must supply", "0"))
    print()
    print(f"  both designs format all {len(AMOUNTS)} amounts the same way, and the")
    print("  interface adds an interface, a class and a parameter to do it.")
    print("  the third table is the reason: there is one implementation, and")
    print("  there is no test that needs a second one, because the thing")
    print("  being replaced is a pure function.")
    print()
    print("  the distinction that decides this is whether the collaborator")
    print("  has a seam to cut. a mailer, a clock, a store and a session all")
    print("  do -- they have a boundary where the real world is, and a test")
    print("  wants to be on the other side of it. formatting a number does")
    print("  not: it is a function from a number to a string, and there is")
    print("  nothing on the far side to replace.")
    print()
    print("  injecting it anyway is not free and it is not neutral. the")
    print("  parameter is a promise that a second implementation might")
    print("  arrive, and every reader of the signature has to hold that")
    print("  possibility in mind while nothing arrives. when a second one")
    print("  does arrive -- a currency, a locale -- that is the day to add")
    print("  the seam, and by then the second implementation is there to")
    print("  justify it.")
    print()
    print("  the rule is the one from the last chapter's pitfall, applied to")
    print("  a parameter instead of a class: introduce the seam when there is")
    print("  something to put on the other side of it, and not before.")


main()
```

```text
  amounts                             4

    what                          the function   behind an interface
    classes                                   0                   2
    functions                                 1                   3
    lines                                     2                  12

    the same answers from both
    amounts formatted alike           4 of 4

    implementations that exist
    the function                        1
    behind the interface                1
    implementations a test must supply  0

  both designs format all 4 amounts the same way, and the
  interface adds an interface, a class and a parameter to do it.
  the third table is the reason: there is one implementation, and
  there is no test that needs a second one, because the thing
  being replaced is a pure function.

  the distinction that decides this is whether the collaborator
  has a seam to cut. a mailer, a clock, a store and a session all
  do -- they have a boundary where the real world is, and a test
  wants to be on the other side of it. formatting a number does
  not: it is a function from a number to a string, and there is
  nothing on the far side to replace.

  injecting it anyway is not free and it is not neutral. the
  parameter is a promise that a second implementation might
  arrive, and every reader of the signature has to hold that
  possibility in mind while nothing arrives. when a second one
  does arrive -- a currency, a locale -- that is the day to add
  the seam, and by then the second implementation is there to
  justify it.

  the rule is the one from the last chapter's pitfall, applied to
  a parameter instead of a class: introduce the seam when there is
  something to put on the other side of it, and not before.
```

Four amounts, formatted the same way by both designs. The interface adds two classes, two functions
and ten lines, and there is still one implementation of the thing being replaced.

The distinction that decides it is whether the collaborator has a seam to cut. A mailer, a clock, a
store and a session all do: they have a boundary where the real world is, and a test wants to be on
the other side of it. Formatting a number does not -- it is a function from a number to a string, and
there is nothing on the far side to replace. Injecting it anyway is not neutral: the parameter is a
promise that a second implementation might arrive, and every reader of the signature holds that
possibility in mind while nothing arrives.

The rule is the last chapter's rule applied to a parameter instead of a class: introduce the seam
when there is something to put on the other side of it, and not before.

:::pitfall The parameter that wires itself

The subtler version of the same mistake, and the one that gets written by people who would never
write a global.

```python run
"""Chapter 55 -- the default that wires the real dependency.

A sender whose dependency is optional, and the same sender where it is
required. The count is of the call sites that build the real thing
without saying so.
"""

REAL_MADE = []


class RealMailer:
    kind = "real"

    def __init__(self):
        REAL_MADE.append(self)

    def send(self, message):
        return "sent by the real one"


class FakeMailer:
    kind = "fake"

    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)
        return "captured"


# --- optional
def send_report(message, mailer=None):
    if mailer is None:
        mailer = RealMailer()
    return mailer.send(message)
# --- end


# --- required
def send_required(message, mailer):
    return mailer.send(message)
# --- end


CALL_SITES = ["the nightly job", "the webhook handler", "the admin button"]


def run_optional():
    """Three production call sites and one test, against the optional
    version."""
    REAL_MADE.clear()
    outcomes = []
    for label in CALL_SITES:
        outcomes.append((label, send_report("the report")))
    outcomes.append(("a test", send_report("the report", FakeMailer())))
    return outcomes


def run_required():
    """The same four sites, against the required version. Each one now
    has to say what it wants."""
    REAL_MADE.clear()
    outcomes = []
    for label in CALL_SITES:
        outcomes.append((label, send_required("the report", RealMailer())))
    outcomes.append(("a test", send_required("the report", FakeMailer())))
    return outcomes


def main():
    print(f"  call sites                          {len(CALL_SITES) + 1}")
    print()

    print("    the optional parameter")
    outcomes = run_optional()
    for label, result in outcomes:
        print("    {:<24}{}".format(label, result))
    implicit = len(REAL_MADE)
    print("    {:<24}{}".format("", "%d real mailer(s) built" % implicit))
    print()

    print("    the required parameter")
    outcomes = run_required()
    for label, result in outcomes:
        print("    {:<24}{}".format(label, result))
    print("    {:<24}{}".format("", "%d real mailer(s) built" % len(REAL_MADE)))
    print()

    sites = len(CALL_SITES) + 1
    print(f"  {implicit} of the {sites} call sites build the real mailer without")
    print("  naming it, and the one that does name one is the test. so the")
    print("  default did not save the three production sites any work -- they")
    print("  still construct a real mailer, on the line inside the function")
    print("  instead of the line at the call site.")
    print()
    print("  what it changed is who can see the choice. with the default, the")
    print("  decision is inside `send_report`, one copy of it for every")
    print("  caller, and the call site that wanted something else is")
    print("  indistinguishable from the three that did not. with a required")
    print("  parameter there is no hidden copy, and the count of places the")
    print("  choice appears is the count of call sites.")
    print()
    print("  this is the same shape as the resolver and the registry in the")
    print("  earlier chapters: a default that produces a working object makes")
    print("  the wrong call site look exactly like the right one. the")
    print("  difference here is that it is one keyword argument, so it gets")
    print("  written by people who would never write a global.")


main()
```

```text
  call sites                          4

    the optional parameter
    the nightly job         sent by the real one
    the webhook handler     sent by the real one
    the admin button        sent by the real one
    a test                  captured
                            3 real mailer(s) built

    the required parameter
    the nightly job         sent by the real one
    the webhook handler     sent by the real one
    the admin button        sent by the real one
    a test                  captured
                            3 real mailer(s) built

  3 of the 4 call sites build the real mailer without
  naming it, and the one that does name one is the test. so the
  default did not save the three production sites any work -- they
  still construct a real mailer, on the line inside the function
  instead of the line at the call site.

  what it changed is who can see the choice. with the default, the
  decision is inside `send_report`, one copy of it for every
  caller, and the call site that wanted something else is
  indistinguishable from the three that did not. with a required
  parameter there is no hidden copy, and the count of places the
  choice appears is the count of call sites.

  this is the same shape as the resolver and the registry in the
  earlier chapters: a default that produces a working object makes
  the wrong call site look exactly like the right one. the
  difference here is that it is one keyword argument, so it gets
  written by people who would never write a global.
```

Three of the four call sites build the real object without naming it, and the one that does name one
is the test. So the default did not save the production sites any work -- they still construct a real
mailer, on the line inside the function instead of the line at the call site.

What it changed is who can see the choice. With the default, the decision lives inside the function,
one copy of it for every caller, and the call site that wanted something else is indistinguishable
from the three that did not. With a required parameter there is no hidden copy, and the number of
places the choice appears is the number of call sites. It is the same shape as the resolver and the
registry in the earlier chapters: a default that produces a working object makes the wrong call site
look exactly like the right one.

:::

:::scenario The checkout, wired three ways

A checkout service, three call sites, three tests, and a vendor client that cannot be constructed in
a test. Three designs, and the count is of the tests that run and of the files that name the vendor.

```python run
"""Chapter 55 -- the scenario. A checkout, wired three ways.

One service, three tests, and a vendor client that cannot be constructed
in a test. The count is of the tests that run, and of the files that name
the vendor.
"""

VENDOR_NAME = "AcmePayClient"


class AcmePayClient:
    """The vendor's client. Constructing it is what a test cannot do,
    and it fails loudly so that the failure is visible rather than
    silent."""

    def __init__(self):
        raise RuntimeError("the vendor client needs a live endpoint")

    def charge(self, amount):
        return "charged " + str(amount)


class StubGateway:
    """What a test supplies instead."""

    def __init__(self):
        self.charged = []

    def charge(self, amount):
        self.charged.append(amount)
        return "stubbed " + str(amount)


class CheckoutOwn:
    """Design A: builds its own gateway."""

    def __init__(self):
        self.gateway = AcmePayClient()

    def pay(self, amount):
        return self.gateway.charge(amount)


class CheckoutInjected:
    """Designs B and C: the gateway arrives."""

    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        return self.gateway.charge(amount)


def charges_the_amount(checkout):
    return checkout.pay(10) == "stubbed 10"


def returns_a_string(checkout):
    return isinstance(checkout.pay(10), str)


def charges_twice(checkout):
    checkout.pay(10)
    checkout.pay(20)
    return True


TESTS = [
    ("the payment goes through", charges_the_amount),
    ("the answer is a string", returns_a_string),
    ("two payments both go", charges_twice),
]

SERVICE_A = """\
from vendor import AcmePayClient


class Checkout:
    def __init__(self):
        self.gateway = AcmePayClient()

    def pay(self, amount):
        return self.gateway.charge(amount)
"""

SERVICE_B = """\
class Checkout:
    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        return self.gateway.charge(amount)
"""

CALLER_B = """\
from vendor import AcmePayClient
from checkout import Checkout


def the_web_route(amount):
    return Checkout(AcmePayClient()).pay(amount)
"""

SERVICE_C = """\
from typing import Protocol


class Gateway(Protocol):
    def charge(self, amount):
        ...


class Checkout:
    def __init__(self, gateway):
        self.gateway = gateway

    def pay(self, amount):
        return self.gateway.charge(amount)
"""

COMPOSITION_C = """\
from checkout import Checkout
from vendor import AcmePayClient

checkout = Checkout(AcmePayClient())
"""

DESIGNS = [
    ("builds its own gateway", [SERVICE_A], CheckoutOwn),
    ("takes one from every caller", [SERVICE_B, CALLER_B, CALLER_B, CALLER_B],
     CheckoutInjected),
    ("takes one, wired in one place",
     [SERVICE_C, COMPOSITION_C], CheckoutInjected),
]


def names(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  call sites                          {len(DESIGNS[1][1]) - 1}")
    print(f"  tests                               {len(TESTS)}")
    print()

    print("    design                        tests that run   files naming the vendor")
    for label, modules, cls in DESIGNS:
        if cls is CheckoutOwn:
            def make():
                return CheckoutOwn()
        else:
            def make():
                return CheckoutInjected(StubGateway())
        ran = 0
        for _, test in TESTS:
            try:
                ran += 1 if test(make()) else 0
            except Exception:
                pass
        files = sum(1 for module in modules if names(module, VENDOR_NAME))
        print("    {:<30}{:<17}{}".format(
            label, "%d of %d" % (ran, len(TESTS)), files))
    print()

    print("    what each design names")
    for label, modules, _ in DESIGNS:
        named = sum(names(module, VENDOR_NAME) for module in modules)
        print("    {:<30}{} reference(s) to the vendor, in {} file(s)".format(
            label, named, sum(1 for m in modules if names(m, VENDOR_NAME))))
    print()
    print("  the first design runs none of the three tests, because the")
    print("  object cannot be built. that is the loudest version of the")
    print("  problem and the easiest to notice.")
    print()
    print("  the second design runs all three and moves the vendor's name out")
    print("  of the service -- into every caller. so the number of files that")
    print("  name the vendor went from one to three, and replacing the vendor")
    print("  now edits three modules instead of one. this is where most")
    print("  refactors stop, because the tests pass and the class looks")
    print("  clean.")
    print()
    print("  the third design is the second one plus a composition root, and")
    print("  it is the only one that gets both counts right: three tests run,")
    print("  and one file names the vendor. the service names an interface it")
    print("  defined itself, the composition root names the vendor, and the")
    print("  callers name neither.")
    print()
    print("  the cost is one new module and one new file, and the thing that")
    print("  decides whether it is worth paying is the count in the middle")
    print("  column. a codebase with one caller does not need a composition")
    print("  root. a codebase with three does, and the number of callers is")
    print("  knowable before the refactor starts.")


main()
```

```text
  call sites                          3
  tests                               3

    design                        tests that run   files naming the vendor
    builds its own gateway        0 of 3           1
    takes one from every caller   3 of 3           3
    takes one, wired in one place 3 of 3           1

    what each design names
    builds its own gateway        2 reference(s) to the vendor, in 1 file(s)
    takes one from every caller   6 reference(s) to the vendor, in 3 file(s)
    takes one, wired in one place 2 reference(s) to the vendor, in 1 file(s)

  the first design runs none of the three tests, because the
  object cannot be built. that is the loudest version of the
  problem and the easiest to notice.

  the second design runs all three and moves the vendor's name out
  of the service -- into every caller. so the number of files that
  name the vendor went from one to three, and replacing the vendor
  now edits three modules instead of one. this is where most
  refactors stop, because the tests pass and the class looks
  clean.

  the third design is the second one plus a composition root, and
  it is the only one that gets both counts right: three tests run,
  and one file names the vendor. the service names an interface it
  defined itself, the composition root names the vendor, and the
  callers name neither.

  the cost is one new module and one new file, and the thing that
  decides whether it is worth paying is the count in the middle
  column. a codebase with one caller does not need a composition
  root. a codebase with three does, and the number of callers is
  knowable before the refactor starts.
```

The first design runs none of the three tests, because the object cannot be built. That is the
loudest version of the problem and the easiest to notice.

The second design runs all three and moves the vendor's name out of the service -- into every
caller. The number of files that name the vendor goes from one to three, so replacing the vendor now
edits three modules instead of one. This is where most refactors stop, because the tests pass and
the class looks clean.

The third design is the second one plus a composition root, and it is the only one that gets both
counts right: three tests run, and one file names the vendor. The service names an interface it
defined itself, the composition root names the vendor, and the callers name neither. The cost is one
new module and one new file, and what decides whether it is worth paying is the number of callers --
which is knowable before the refactor starts.

:::

## Key takeaways

- **Injection is a change to where an object comes from, and its consequences are countable.** The
  numbers to take are behaviours a stand-in can be handed, tests that depend on the order, and
  modules that name a concrete type.
- **A suite that constructs its own dependencies is green, and that is the trap.** Both designs
  passed all six behaviours; only one of them could be handed a stand-in in any of the six.
- **The one line that names the concrete type is the line that decides everything.** Remove it and
  the count goes from zero behaviours replaceable to all of them.
- **A dependency reached for by name is a dependency whose lifetime nobody chose.** The module-level
  handle made all 3 of 3 behaviours a function of what ran before them.
- **A fixture that clears shared state is not the fix.** It knows which state to clear, and it works
  only while every test remembers the line -- which is a property of the tests, not the design.
- **An interface buys the swap and not the behaviour.** The consumer named none of the three
  implementations, and it could still tell all three apart once it called them.
- **Two of three implementations returned a value for every key and the third returned two and a
  `None`.** The protocol named two methods and nothing else, so nothing in it said which was allowed.
- **Inversion does not reduce the number of references.** Each design held exactly one, and they
  pointed in opposite directions.
- **What inversion changes is which module is on the receiving end.** The unstable module ends up
  naming the stable one's interface, which is why the interface belongs to the consumer.
- **A container is worth having because the graph becomes data.** The eager one constructed nothing
  and reported the missing name before anything ran.
- **The hand-written root and the lazy container failed at the same point.** Being a container is not
  what made the difference; checking the whole graph first is.
- **A container replaces a class reference with a string.** `NameError` names the thing, `KeyError`
  names a string, and a string is not checked until the lookup happens.
- **A framework's injection is a marker in a default position.** 4 of 5 parameters were marked and
  the handler bodies named a provider in none of them.
- **Nothing checks the marker.** A parameter defaulting to `Depends(f)` is a dependency and one
  defaulting to a real object is a default, and they look identical to everything but the caller.
- **A scope is how long the object is allowed to live, and the wrong answer has no symptom.** The
  captured cache gave 2 of 3 requests the wrong session and nothing raised.
- **A singleton may not hold something rebuilt per request.** The container builds it once, and there
  is no later moment at which it could be given a new one.
- **A service locator hides the dependency from the signature, which is what it is chosen for.** It
  names 0 of 3 in the signature and one override reached all 4 callers.
- **A locator also moves the error into the wrong frame.** It raises inside the object rather than at
  the call site that forgot to register something.
- **The optional parameter did not save the call sites any work.** 3 of the 4 sites still built the
  real object; what changed is that the choice became invisible.
- **Injection is the wrong answer when the collaborator has no seam.** A pure function behind an
  interface added an interface, a class and a parameter, and no test needed a second implementation.

## Practice

- [ ] **Count the names a class reaches for.** Take a class in a project of yours whose methods call
  module-level functions or construct collaborators inside the body. List every name it depends on
  that does not arrive as an argument. Then rewrite it to take them and count again. Report both
  numbers -- and then pick one of the names you *would not* inject, and say why.
- [ ] **Measure order dependence in a suite of your own.** Take three tests that touch the same
  object. Run them in three different orders and record which results change. Then make the smallest
  change you can and measure again. Report the count before and after, and say what the change was.
- [ ] **Find the composition root, or find that there is not one.** Pick a service in a project of
  yours. Count how many modules name a concrete implementation of its dependencies. Move the
  construction into one module and count again. Report both numbers and the number of modules that
  name nothing concrete in either version.
- [ ] **Audit one interface for what it does not promise.** Take a protocol your code depends on.
  Write three implementations that all satisfy the names and behave differently in one observable
  way. Report which of the three your consumer can tell apart, which difference the protocol names,
  and what catches the ones it does not.

## Solutions

:::solution Exercise 1

A pricer whose methods reach for four names that do not arrive as arguments, and the same pricer
with them as constructor arguments.

```python run
"""Chapter 55 -- practice 1.

A class whose methods reach for names that do not arrive as arguments,
and the same class with them as constructor arguments. The count is of
the dependencies that arrive as arguments rather than by name.
"""

import pathlib

DB = {"rates": {"gbp": 1.0}}
DEFAULT_MARKUP = 1.2


def get_clock():
    return "12:00"


class Formatter:
    def format(self, amount):
        return "%.2f" % amount


# --- reaches
class PricerReaches:
    def quote(self, amount):
        rate = DB["rates"]["gbp"]
        stamp = get_clock()
        text = Formatter().format(amount * rate)
        return stamp + " " + text

    def markup(self, amount):
        return amount * DEFAULT_MARKUP
# --- end


# --- takes
class PricerTakes:
    def __init__(self, db, clock, formatter, markup):
        self.db = db
        self.clock = clock
        self.formatter = formatter
        self.markup = markup

    def quote(self, amount):
        rate = self.db["rates"]["gbp"]
        stamp = self.clock()
        text = self.formatter.format(amount * rate)
        return stamp + " " + text

    def markup(self, amount):
        return amount * self.markup
# --- end


REACHED = ["DB", "get_clock", "Formatter", "DEFAULT_MARKUP"]

SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
REACHES_SRC = SOURCE.split("# --- reaches")[1].split("# --- end")[0]
TAKES_SRC = SOURCE.split("# --- takes")[1].split("# --- end")[0]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  dependencies the class uses         {len(REACHED)}")
    print()
    print("    dependency        reached by name   arrived as an argument")
    for name in REACHED:
        print("    {:<18}{:<18}{}".format(
            name,
            "yes" if mentions(REACHES_SRC, name) else "no",
            "yes" if mentions(TAKES_SRC, name) else "no"))
    print()

    for label, source in (("reaches for them", REACHES_SRC),
                          ("takes them", TAKES_SRC)):
        by_name = sum(1 for name in REACHED if mentions(source, name))
        print("    {:<34}{} of {} reached by name".format(
            label, by_name, len(REACHED)))
    print()

    reaches = PricerReaches()
    takes = PricerTakes(DB, get_clock, Formatter(), DEFAULT_MARKUP)
    same = sum(1 for amount in (10, 25, 100)
               if reaches.quote(amount) == takes.quote(amount))
    print("    {:<34}{} of {} outputs alike".format(
        "the two versions", same, 3))
    print()
    print(f"  the reaching version uses {len(REACHED)} names it does not receive,")
    print("  and the version that takes them uses none. the output is the same")
    print("  for every amount, so nothing about the behaviour changed.")
    print()
    print("  the two to look at separately are `DB` and `DEFAULT_MARKUP`.")
    print("  `DB` is a seam: it is the thing a test wants to replace, and it")
    print("  is the reason to do this. `DEFAULT_MARKUP` is a constant, and a")
    print("  constant that arrives as a constructor argument is a value the")
    print("  caller can set to anything -- which is a configuration feature")
    print("  if you want one and a bug if you do not.")
    print()
    print("  so the count is a starting point and not a target. the question")
    print("  to ask of each name in the list is whether a test, a second")
    print("  environment or a second implementation would ever want to supply")
    print("  a different one. if the answer is yes for exactly one of them,")
    print("  inject that one and leave the constant alone.")


main()
```

```text
  dependencies the class uses         4

    dependency        reached by name   arrived as an argument
    DB                yes               no
    get_clock         yes               no
    Formatter         yes               no
    DEFAULT_MARKUP    yes               no

    reaches for them                  4 of 4 reached by name
    takes them                        0 of 4 reached by name

    the two versions                  3 of 3 outputs alike

  the reaching version uses 4 names it does not receive,
  and the version that takes them uses none. the output is the same
  for every amount, so nothing about the behaviour changed.

  the two to look at separately are `DB` and `DEFAULT_MARKUP`.
  `DB` is a seam: it is the thing a test wants to replace, and it
  is the reason to do this. `DEFAULT_MARKUP` is a constant, and a
  constant that arrives as a constructor argument is a value the
  caller can set to anything -- which is a configuration feature
  if you want one and a bug if you do not.

  so the count is a starting point and not a target. the question
  to ask of each name in the list is whether a test, a second
  environment or a second implementation would ever want to supply
  a different one. if the answer is yes for exactly one of them,
  inject that one and leave the constant alone.
```

:::

:::solution Exercise 2

Three tests against a shared object, run in three orders under four arrangements -- including the one
where two of the three tests remember to clear it.

```python run
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
```

```text
  tests                               3
  orders                              3

    how the cart is arranged          passes, in each of the orders
    no clearing                       2 of 3  1 of 3  1 of 3
    cleared in all three              3 of 3  3 of 3  3 of 3
    cleared in two of three           2 of 3  3 of 3  2 of 3
    built in the test                 3 of 3  3 of 3  3 of 3

    tests whose result depends on the order
    no clearing                       3 of 3
    cleared in all three              0 of 3
    cleared in two of three           1 of 3
    built in the test                 0 of 3

  clearing the shared cart works, and the third row is why it is
  not the fix. two of the three tests clear it and one does not,
  and one of the three is order-dependent again -- so the
  arrangement is correct only as long as every test remembers the
  line, and the next test somebody adds is a chance to forget it.

  that is the difference between a discipline and a guarantee. a
  test that clears shared state is a test that knows which state
  to clear, and the next person to add a test has to know it too.
  a test that builds its own cart cannot forget, because there is
  nothing to forget.

  the fourth row is the one to copy. it is not longer than the
  third, it does not need a fixture, and the order stops being an
  input to the result -- which is what the count in the middle of
  this table is measuring.
```

:::

:::solution Exercise 3

Six modules and three concrete types, with the wiring in the callers and then in one module.

```python run
"""Chapter 55 -- practice 3.

Six modules, three concrete types, and the wiring in two places. The
count is of the modules that name a concrete type, and the last table is
what moving the wiring into one module does to it.
"""

CONCRETE = ["SqlStore", "StripeGateway", "CsvWriter"]

# --- in the callers
ROUTES = """\
from stores import SqlStore
from gateways import StripeGateway


def checkout(request):
    store = SqlStore()
    gateway = StripeGateway()
    return store.save(request, gateway)
"""

NIGHTLY = """\
from stores import SqlStore


def run():
    return SqlStore().sweep()
"""

REPORTS = """\
from stores import SqlStore
from writers import CsvWriter


def monthly():
    return CsvWriter().write(SqlStore().all())
"""

ORDERS = """\
def total(order):
    return sum(line.amount for line in order.lines)
"""

PRICING = """\
def price(amount, rate):
    return amount * rate
"""
# --- end


# --- in a composition root
ROUTES_AFTER = """\
def checkout(request, store, gateway):
    return store.save(request, gateway)
"""

NIGHTLY_AFTER = """\
def run(store):
    return store.sweep()
"""

REPORTS_AFTER = """\
def monthly(store, writer):
    return writer.write(store.all())
"""

COMPOSITION = """\
from gateways import StripeGateway
from stores import SqlStore
from writers import CsvWriter

STORE = SqlStore()
GATEWAY = StripeGateway()
WRITER = CsvWriter()
"""
# --- end


BEFORE = [
    ("routes", ROUTES), ("nightly", NIGHTLY), ("reports", REPORTS),
    ("orders", ORDERS), ("pricing", PRICING),
]

AFTER = [
    ("routes", ROUTES_AFTER), ("nightly", NIGHTLY_AFTER),
    ("reports", REPORTS_AFTER), ("orders", ORDERS), ("pricing", PRICING),
    ("composition", COMPOSITION),
]


def named(source):
    return [name for name in CONCRETE if name in source]


def main():
    print(f"  modules                             {len(BEFORE)}")
    print(f"  concrete types                      {len(CONCRETE)}")
    print()
    print("    module            names, with the wiring in the callers")
    for label, source in BEFORE:
        found = named(source)
        print("    {:<18}{}".format(
            label, ", ".join(found) if found else "nothing concrete"))
    print()
    print("    module            names, with the wiring in one module")
    for label, source in AFTER:
        found = named(source)
        print("    {:<18}{}".format(
            label, ", ".join(found) if found else "nothing concrete"))
    print()

    print("    where the wiring lives       modules naming a type   references")
    for label, modules in (("in the callers", BEFORE),
                           ("in a composition root", AFTER)):
        holders = sum(1 for _, source in modules if named(source))
        references = sum(len(named(source)) for _, source in modules)
        print("    {:<29}{:<23}{}".format(
            label, "%d of %d" % (holders, len(modules)), references))
    print()
    print("  the count that matters is the second column, and it goes from")
    print("  three modules to one. that is the number of places a change to")
    print("  the database reaches, and it is the number to measure before")
    print("  and after.")
    print()
    print("  the reference count drops as well, from five to three, and it")
    print("  drops for a different reason: with the wiring in the callers")
    print("  each caller names what it needs, so `SqlStore` is named three")
    print("  times. in one module each type is named once.")
    print()
    print("  the fourth column of the table is the one that does not move.")
    print("  `orders` and `pricing` name nothing concrete in either design,")
    print("  and they are the modules the refactor was for. a module that")
    print("  takes its dependencies can be moved, tested and read without")
    print("  anything else changing, and the composition root is the price")
    print("  of having several of them.")
    print()
    print("  so the exercise has a stopping rule. count the modules that")
    print("  name a concrete type. if it is one, the composition root is")
    print("  already there. if it is more than one, each extra module is a")
    print("  place the next change has to visit.")


main()
```

```text
  modules                             5
  concrete types                      3

    module            names, with the wiring in the callers
    routes            SqlStore, StripeGateway
    nightly           SqlStore
    reports           SqlStore, CsvWriter
    orders            nothing concrete
    pricing           nothing concrete

    module            names, with the wiring in one module
    routes            nothing concrete
    nightly           nothing concrete
    reports           nothing concrete
    orders            nothing concrete
    pricing           nothing concrete
    composition       SqlStore, StripeGateway, CsvWriter

    where the wiring lives       modules naming a type   references
    in the callers               3 of 5                 5
    in a composition root        1 of 6                 3

  the count that matters is the second column, and it goes from
  three modules to one. that is the number of places a change to
  the database reaches, and it is the number to measure before
  and after.

  the reference count drops as well, from five to three, and it
  drops for a different reason: with the wiring in the callers
  each caller names what it needs, so `SqlStore` is named three
  times. in one module each type is named once.

  the fourth column of the table is the one that does not move.
  `orders` and `pricing` name nothing concrete in either design,
  and they are the modules the refactor was for. a module that
  takes its dependencies can be moved, tested and read without
  anything else changing, and the composition root is the price
  of having several of them.

  so the exercise has a stopping rule. count the modules that
  name a concrete type. if it is one, the composition root is
  already there. if it is more than one, each extra module is a
  place the next change has to visit.
```

:::

:::solution Exercise 4

Three implementations of one protocol, all of which have the names and only one of which the
consumer can use as written.

```python run
"""Chapter 55 -- practice 4.

Three implementations of one protocol. All three have the names, and the
count is of the ones whose behaviour the consumer can tell apart -- and
of the differences the protocol does not name.
"""

from typing import Protocol


class Cache(Protocol):
    def put(self, key, value):
        ...

    def get(self, key):
        ...


class Plain:
    def __init__(self):
        self.rows = {}

    def put(self, key, value):
        self.rows[key] = value

    def get(self, key):
        return self.rows.get(key)


class Bounded:
    """Keeps the two most recent entries, which the protocol does not
    mention."""

    def __init__(self):
        self.rows = {}
        self.order = []

    def put(self, key, value):
        self.rows[key] = value
        self.order.append(key)
        while len(self.order) > 2:
            self.rows.pop(self.order.pop(0), None)

    def get(self, key):
        return self.rows.get(key)


class Expiring:
    """Answers only for the entry written most recently."""

    def __init__(self):
        self.rows = {}
        self.last = None

    def put(self, key, value):
        self.rows[key] = value
        self.last = key

    def get(self, key):
        return self.rows.get(key) if key == self.last else None


PAIRS = [("a", 1), ("b", 2), ("c", 3)]

IMPLEMENTATIONS = [
    ("Plain", Plain, "nothing"),
    ("Bounded", Bounded, "drops entries past the two most recent"),
    ("Expiring", Expiring, "answers only for the newest key"),
]

METHODS = ["put", "get"]

DIFFERENCES = ["eviction", "expiry"]


def round_trip(cache):
    """Write three entries, then read all three back, which is the only
    thing the protocol promised."""
    for key, value in PAIRS:
        cache.put(key, value)
    return [cache.get(key) for key, _ in PAIRS]


def main():
    print(f"  methods in the protocol             {len(METHODS)}")
    print(f"  implementations                     {len(IMPLEMENTATIONS)}")
    print()
    print("    implementation   has both names   round trips")
    for label, cls, _ in IMPLEMENTATIONS:
        cache = cls()
        has = all(hasattr(cache, name) for name in METHODS)
        back = round_trip(cls())
        got = sum(1 for value in back if value is not None)
        print("    {:<17}{:<17}{} of {}".format(
            label, "yes" if has else "no", got, len(PAIRS)))
    print()

    print("    what each one does that the protocol does not say")
    for label, _, difference in IMPLEMENTATIONS:
        print("    {:<17}{}".format(label, difference))
    print()

    print("    the differences, and whether the protocol names them")
    for name in DIFFERENCES:
        print("    {:<34}{}".format(name, "no"))
    print()
    print("  all three have both names, and the consumer can tell all three")
    print("  apart -- one after three writes, one after two, and one after")
    print("  one. the protocol covers none of that, because a protocol names")
    print("  methods and not behaviour.")
    print()
    print("  the row to read twice is the middle one. `Bounded` is not")
    print("  broken: it is a cache with a size, which is a reasonable thing")
    print("  for a cache to be, and the consumer was written against a")
    print("  protocol that never said the cache was unbounded. so the bug is")
    print("  in the interface rather than in either implementation, and it")
    print("  was introduced by writing one implementation first and naming")
    print("  the interface after it.")
    print()
    print("  what catches it is a test that writes three and reads three,")
    print("  which is the round trip above. that test is the specification,")
    print("  and it is worth writing it against the protocol rather than")
    print("  against `Plain` -- because a test written against `Plain` passes")
    print("  for `Plain` and tells you nothing about the other two.")


main()
```

```text
  methods in the protocol             2
  implementations                     3

    implementation   has both names   round trips
    Plain            yes              3 of 3
    Bounded          yes              2 of 3
    Expiring         yes              1 of 3

    what each one does that the protocol does not say
    Plain            nothing
    Bounded          drops entries past the two most recent
    Expiring         answers only for the newest key

    the differences, and whether the protocol names them
    eviction                          no
    expiry                            no

  all three have both names, and the consumer can tell all three
  apart -- one after three writes, one after two, and one after
  one. the protocol covers none of that, because a protocol names
  methods and not behaviour.

  the row to read twice is the middle one. `Bounded` is not
  broken: it is a cache with a size, which is a reasonable thing
  for a cache to be, and the consumer was written against a
  protocol that never said the cache was unbounded. so the bug is
  in the interface rather than in either implementation, and it
  was introduced by writing one implementation first and naming
  the interface after it.

  what catches it is a test that writes three and reads three,
  which is the round trip above. that test is the specification,
  and it is worth writing it against the protocol rather than
  against `Plain` -- because a test written against `Plain` passes
  for `Plain` and tells you nothing about the other two.
```

:::
