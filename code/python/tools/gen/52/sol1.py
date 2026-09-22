#!/usr/bin/env python3
"""Exercise 1 -- five callables, four entry points, and payloads in a container.

A smaller version of parts 1 and 2 over a different application, plus the case
that is easy to miss: the payload does not have to be the object you pass. It
can be nested inside one, and the walk reaches every copy of it.
"""
import copy
import pickle

calls = []


class Payload:
    def __init__(self, target, args):
        self.target = target
        self.args = args

    def __reduce__(self):
        return (self.target, self.args)


class Nested:
    """A payload with no configuration, so containers can hold several."""

    def __reduce__(self):
        calls.append(1)
        return (abs, (-1,))


TARGETS = [
    ("abs", (abs, (-5,))),
    ("round", (round, (3.14159, 2))),
    ("divmod", (divmod, (17, 5))),
    ("sum", (sum, ([1, 2, 3],))),
    ("int", (int, ("42",))),
]

ENTRY_POINTS = [
    ("pickle.dumps", lambda p: pickle.dumps(p)),
    ("pickle.loads", lambda p: pickle.loads(pickle.dumps(p))),
    ("copy.copy", lambda p: copy.copy(p)),
    ("copy.deepcopy", lambda p: copy.deepcopy(p)),
]

SHAPES = [
    ("bare", lambda: Nested()),
    ("in a list of three", lambda: [Nested(), Nested(), Nested()]),
    ("in a dict, three keys",
     lambda: {"a": Nested(), "b": Nested(), "c": Nested()}),
    ("two deep, four leaves",
     lambda: [[Nested(), Nested()], [Nested(), Nested()]]),
]


def runs_on(fn):
    calls.clear()
    try:
        fn(Nested())
    except Exception:                                  # noqa: BLE001
        pass
    return bool(calls)


def main():
    print(f"  callables                          {len(TARGETS):>3}")
    print(f"  entry points                       {len(ENTRY_POINTS):>3}")
    print()
    print(f"    {'callable':<12}{'pickle.loads':>14}   returned")

    called = 0
    for label, (fn, args) in TARGETS:
        try:
            result = pickle.loads(pickle.dumps(Payload(fn, args)))
            called += 1
            shown = repr(result)
        except Exception as exc:                       # noqa: BLE001
            shown = type(exc).__name__
        print(f"    {label:<12}{'called':>14}   {shown}")

    print()
    print(f"  callables invoked                  {called:>3} of "
          f"{len(TARGETS)}")

    print()
    print("  the same payload, inside a container")
    for label, shape in SHAPES:
        calls.clear()
        try:
            pickle.loads(pickle.dumps(shape()))
        except Exception:                              # noqa: BLE001
            pass
        print(f"    {label:<24}{len(calls)} invocation(s)")

    print()
    print(f"  entry points that run __reduce__   "
          f"{sum(1 for label, fn in ENTRY_POINTS if runs_on(fn))} of "
          f"{len(ENTRY_POINTS)}")

    print()
    print("  a stream is a graph, not a value, and loads() walks all of it.")
    print("  one payload in a list of three is invoked three times, and the")
    print("  four leaves two levels down are invoked four times. wrapping a")
    print("  payload in a container does not hide it, because walking into")
    print("  containers is what the walk is for.")


if __name__ == "__main__":
    main()
