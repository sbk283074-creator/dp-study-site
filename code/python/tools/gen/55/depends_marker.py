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
