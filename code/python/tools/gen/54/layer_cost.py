"""Chapter 54 -- the cost of a layer, measured in frames.

One rule, wrapped in four layers that each do nothing but forward. The
count is of frames, and of the implementations each layer actually has.
"""

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


def frames_between(outer, inner, argument):
    """How many of our own frames sit between the call and the rule."""
    global TRACE
    TRACE = []
    outer(argument)
    return list(TRACE)


def main():
    direct = frames_between(core, core, 10.0)
    layered = frames_between(handler, core, 10.0)
    print(f"  frames for the rule called directly  {len(direct)}")
    print(f"  frames for the rule behind a handler {len(layered)}")
    print("    " + " -> ".join(layered))
    print()

    print(f"  the rule is one expression, and a call from the outside reaches")
    print(f"  it through {len(layered)} frames, {len(layered) - len(direct)} of which only")
    print("  forward their argument to the next one.")
    print()
    print("  that is not an argument against layers. it is the number to put")
    print("  next to them, because a layer is a claim about a change that")
    print("  might happen, and the claim can be checked.")
    print()

    layers = ["handler", "controller", "service", "repository", "core"]
    print("    layer            implementations")
    for name in layers:
        print("    {:<17}{}".format(name, 1))
    print()
    print(f"  {len(layers)} layers and {len(layers)} implementations, so the seam each")
    print("  one creates is a seam with one thing on each side. swapping the")
    print("  rule changes one line with the layers and one line without them,")
    print("  and adding a second implementation to any layer is what would")
    print("  make the count go up.")
    print()
    print("  the honest way to read the frame count is as a question rather")
    print("  than a verdict: how many implementations does each of these")
    print("  layers have, and how many does it have in six months? a layer")
    print("  that keeps one implementation is a layer that has been paying")
    print("  rent without a tenant, and the four frames are what the rent")
    print("  looks like at the call site.")
    print()
    print("  what makes it worth paying is the direction, and the direction is")
    print("  not visible in the frames. if the rule is at the bottom and the")
    print("  layers point down at it, then the thing at the top can be")
    print("  replaced without touching it. if the rule ever imports the")
    print("  handler, the stack has become a cycle and the layers are no")
    print("  longer a boundary -- they are a detour.")


main()
