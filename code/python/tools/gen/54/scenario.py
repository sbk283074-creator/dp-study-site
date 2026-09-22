"""Chapter 54 -- the scenario. A plugin host.

Eight plugins, four of which are broken in four different ways, and five
hosts that differ in what they do about it. The count is of requests
answered, and the column that matters is when the broken ones are found.
"""


class Plugin:
    name = "plugin"

    def handle(self, request):
        raise NotImplementedError


class Good(Plugin):
    def __init__(self, name, answer):
        self.name = name
        self._answer = answer

    def handle(self, request):
        return self._answer


class Raiser(Plugin):
    def __init__(self, name, error):
        self.name = name
        self._error = error

    def handle(self, request):
        raise self._error


class OldSignature(Plugin):
    """Written against the first version of the interface, which took no
    request."""

    name = "old"

    def handle(self):
        return "old answer"


class NotCallable(Plugin):
    name = "not-callable"
    handle = 5


def build():
    return [
        Good("alpha", "alpha ok"),
        Good("beta", "beta ok"),
        Good("gamma", "gamma ok"),
        Good("delta", "delta ok"),
        Raiser("epsilon", RuntimeError("epsilon failed")),
        Raiser("zeta", KeyError("zeta failed")),
        OldSignature(),
        NotCallable(),
    ]


def try_call(plugin, request):
    """Returns (answered, the answer or the error name)."""
    try:
        return True, plugin.handle(request)
    except Exception as exc:
        return False, type(exc).__name__


def adapt(plugin):
    """The adapter for the old signature, which is one place that knows
    the old shape."""
    if isinstance(plugin, OldSignature):
        return _Adapted(plugin)
    return plugin


class _Adapted(Plugin):
    def __init__(self, inner):
        self.inner = inner
        self.name = inner.name

    def handle(self, request):
        return self.inner.handle()


def probe(plugins):
    """What a startup check would find, and it is the same call the
    request path makes."""
    ok, broken = [], []
    for plugin in plugins:
        answered, _ = try_call(plugin, "probe")
        (ok if answered else broken).append(plugin.name)
    return ok, broken


def main():
    plugins = build()
    print(f"  plugins                             {len(plugins)}")
    print(f"  good                                "
          f"{sum(1 for p in plugins if type(p) is Good)}")
    print(f"  broken                              "
          f"{sum(1 for p in plugins if type(p) is not Good)}")
    print()

    rows = []

    # A: call each plugin directly and let it fail
    answered, crashed = 0, False
    for plugin in plugins:
        ok, _ = try_call(plugin, "request")
        if ok:
            answered += 1
        else:
            crashed = True
            break
    rows.append(("call it and let it fail", answered, crashed, "at the first request"))

    # B: isolate each call
    answered = 0
    for plugin in plugins:
        ok, _ = try_call(plugin, "request")
        answered += 1 if ok else 0
    rows.append(("isolate each call", answered, False, "at the first request"))

    # C: isolate, and check the interface first
    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class Handles(Protocol):
        def handle(self, request):
            ...

    answered, accepted = 0, 0
    for plugin in plugins:
        if isinstance(plugin, Handles):
            accepted += 1
        ok, _ = try_call(plugin, "request")
        answered += 1 if ok else 0
    rows.append(("isolate, and check the interface", answered, False,
                 "at the first request"))

    # D: plus the adapter
    adapted = [adapt(p) for p in plugins]
    answered = 0
    for plugin in adapted:
        ok, _ = try_call(plugin, "request")
        answered += 1 if ok else 0
    rows.append(("and adapt the old signature", answered, False,
                 "at the first request"))

    # E: plus a startup probe
    ok, broken = probe(adapted)
    answered = 0
    for plugin in adapted:
        if plugin.name in ok:
            good, _ = try_call(plugin, "request")
            answered += 1 if good else 0
    rows.append(("and probe every plugin at startup", answered, False,
                 "before the first request"))

    print("    host                              answered  survived   found")
    for label, answered, crashed, when in rows:
        print("    {:<34}{:>8}  {:<9}{}".format(
            label, "%d of %d" % (answered, len(plugins)),
            "no" if crashed else "yes", when))
    print()

    print(f"  the interface check accepted {accepted} of the {len(plugins)} plugins and")
    print("  changed nothing, because a runtime protocol check asks whether")
    print("  the name is there -- and for the plugin whose `handle` is the")
    print("  number five, it is.")
    print()
    print("  isolation is what keeps the host up, and the adapter is what")
    print("  gets one more plugin answering. neither of them tells you which")
    print("  plugin is broken.")
    print()
    print("  the last row does not answer more requests than the one above it.")
    print("  it answers the same number and it finds the broken ones *before*")
    print("  the first request, which is the only difference and the whole of")
    print("  it. a plugin host is a place where the patterns give you the")
    print("  shape -- a registry, an interface, a dispatch, an adapter -- and")
    print("  the shape is not the part that decides whether the system works.")
    print("  the part that decides is the one line nobody writes: the probe")
    print("  that calls every plugin once, at startup, and names the ones that")
    print("  did not answer.")


main()
