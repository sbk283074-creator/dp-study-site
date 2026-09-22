"""Chapter 54 -- practice 3.

Implementations per layer. A call path is walked from the entry point to
the rule, and each function on the way is asked how many things
implement it.
"""

import pathlib

CALL_PATH = ["handler", "controller", "service", "repository", "core"]

# what each layer has behind it, counted rather than assumed
IMPLEMENTATIONS = {
    "handler": ["http", "cli"],
    "controller": ["orders"],
    "service": ["orders"],
    "repository": ["sql", "in-memory", "fake"],
    "core": ["standard"],
}

TRACE = []


def core(order):
    TRACE.append("core")
    return order * 1.2


def repository(order):
    TRACE.append("repository")
    return core(order)


def service(order):
    TRACE.append("service")
    return repository(order)


def controller(order):
    TRACE.append("controller")
    return service(order)


def handler(order):
    TRACE.append("handler")
    return controller(order)


def walk(entry, argument):
    global TRACE
    TRACE = []
    entry(argument)
    return list(TRACE)


def main():
    frames = walk(handler, 10.0)
    print(f"  frames from the entry point to the rule  {len(frames)}")
    print("    " + " -> ".join(frames))
    print(f"  frames when the rule is called directly  {len(walk(core, 10.0))}")
    print()

    print("    layer            implementations   what they are")
    for name in CALL_PATH:
        impls = IMPLEMENTATIONS[name]
        print("    {:<17}{:>15}   {}".format(name, len(impls), ", ".join(impls)))
    print()

    forwarding = [n for n in CALL_PATH
                  if len(IMPLEMENTATIONS[n]) == 1 and n != "core"]
    with_choice = [n for n in CALL_PATH if len(IMPLEMENTATIONS[n]) > 1]
    print(f"  {len(with_choice)} of the {len(CALL_PATH)} layers have more than one")
    print("  implementation, and those are the layers that are earning their")
    print("  frames. the other "
          f"{len(forwarding)} have exactly one, so every call through them")
    print("  reaches the same code it would have reached without them.")
    print()
    print("  that is not the same as saying they are wrong. a layer with one")
    print("  implementation is a seam that has been cut and not yet used, and")
    print("  the repository here shows what using it looks like: three")
    print("  implementations, one of which is a fake, and the fake is what")
    print("  makes the service testable without a database.")
    print()
    print("  the count to carry away is the one for the layers with a single")
    print("  implementation. each of them is a place a reader has to open to")
    print("  find the rule, and the rule is at the bottom. if the number of")
    print("  those layers grows while the number of implementations stays at")
    print("  one, the call path is getting longer and nothing is getting")
    print("  easier -- and that is the whole diagnosis, available by counting")
    print("  two columns instead of reading the code.")


main()
