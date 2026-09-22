"""Chapter 54 -- the factory pattern, as a registry.

A decorator that files a function under its own name, which is the
whole of the pattern. Two things go wrong with it, and neither is in the
decorator: a handler that lives in a module nobody imported, and a
lookup that goes through `globals()` instead of through the registry.
"""

REGISTRY = {}


def handles(fn):
    REGISTRY[fn.__name__] = fn
    return fn


@handles
def read_csv(source):
    return "csv from " + source


@handles
def read_json(source):
    return "json from " + source


@handles
def read_tsv(source):
    return "tsv from " + source


# two more handlers, in a module that nothing has imported yet
LAZY = [("read_xml", lambda source: "xml from " + source),
        ("read_yaml", lambda source: "yaml from " + source)]


def import_lazy_module():
    """What importing the module would do, as a side effect of the
    decorator running at import time."""
    for name, fn in LAZY:
        REGISTRY[name] = fn


REQUESTED = ["read_csv", "read_json", "read_tsv", "read_xml", "read_yaml",
             "handles", "main", "REGISTRY"]


def resolve(name):
    return REGISTRY.get(name)


def main():
    print(f"  handlers the service defines        {len(REGISTRY) + len(LAZY)}")
    print(f"  handlers in the registry at import  {len(REGISTRY)}")
    print()

    print("    request             before the import   after")
    before = {name: resolve(name) for name in REQUESTED}
    import_lazy_module()
    after = {name: resolve(name) for name in REQUESTED}
    for name in REQUESTED:
        print("    {:<20}{:<21}{}".format(
            name,
            "found" if before[name] else "not in the registry",
            "found" if after[name] else "not in the registry"))
    print()
    print(f"  importing the other module took the registry from "
          f"{sum(1 for n in REQUESTED if before[n])} to "
          f"{sum(1 for n in REQUESTED if after[n])} of the "
          f"{len(REQUESTED)} requests.")
    print("  the registration happened as a side effect of an import that")
    print("  nobody wrote for that reason, so which handlers exist depends on")
    print("  which modules the process happened to touch -- and the failure")
    print("  is a missing key at request time, in a different file from the")
    print("  handler that was never registered.")
    print()

    print("    how a name becomes a handler")
    for label, lookup in (("the registry", resolve),
                          ("globals()", lambda n: globals().get(n))):
        found = [n for n in REQUESTED if lookup(n)]
        print("      {:<14}{} of {} requests resolved".format(
            label, len(found), len(REQUESTED)))
    via_globals = [n for n in REQUESTED if globals().get(n)]
    extra = [n for n in via_globals if n not in REGISTRY]
    print()
    print(f"  `globals()` resolved {len(extra)} names the registry does not have, and")
    print(f"  they are {', '.join('`' + n + '`' for n in extra)}. none of them is a")
    print("  format handler, and a lookup that goes through the module's own")
    print("  namespace cannot tell the difference -- it answers with whatever")
    print("  the name happens to be bound to, which is the same failure as")
    print("  the resolver in the untrusted-data chapter, one layer up.")
    print()
    print("  the registry is worth having for that reason rather than for the")
    print("  decorator. it is a list of the things that are allowed to answer,")
    print("  written where you can read it, and the import-order problem is")
    print("  the price: the list is built by side effects, so it is only")
    print("  complete once everything that contributes to it has been")
    print("  imported. importing the handler modules explicitly, for that")
    print("  reason, is the fix.")


main()
