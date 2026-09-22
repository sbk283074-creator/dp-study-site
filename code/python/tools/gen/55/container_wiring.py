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
