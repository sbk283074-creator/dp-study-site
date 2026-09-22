#!/usr/bin/env python3
"""Chapter 52 demo, part 1 -- the payload names the function to call.

A serialised object is not a description of an object. It is a program that
builds one, and for the classes that define __reduce__ the program is written
in terms of a callable and its arguments. That is the whole design: pickling
has to be able to reconstruct an object whose class it cannot see, so the
stream carries instructions rather than a layout.

Six payloads. Each one is a tiny class whose __reduce__ returns a callable that
is a stdlib function and arguments that are constants. None of them does
anything visible, which is the point -- the question is not what these six do,
it is that loads() will call whatever the stream names.
"""
import json
import marshal
import operator
import os
import pickle


class Payload:
    """Stand-in for the object a stream would reconstruct."""

    def __init__(self, target, args):
        self.target = target
        self.args = args

    def __reduce__(self):
        return (self.target, self.args)


# label, the callable the stream names, its arguments
PAYLOADS = [
    ("len", (len, ("abcdef",))),
    ("str.upper", (str.upper, ("abc",))),
    ("sorted", (sorted, ([3, 1, 2],))),
    ("os.path.join", (os.path.join, ("/a", "b"))),
    ("max", (max, ([1, 9, 4],))),
    ("operator.add", (operator.add, (2, 3))),
]


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print("  what each stream names            a stdlib callable + constants")
    print()
    print(f"    {'callable':<16}{'pickle.loads':>13}{'json.dumps':>12}{'marshal':>10}")

    pickle_called = 0
    json_ok = 0
    marshal_ok = 0
    for label, (fn, args) in PAYLOADS:
        try:
            pickle.loads(pickle.dumps(Payload(fn, args)))
            pickle_called += 1
            pk = "called"
        except Exception as exc:                       # noqa: BLE001
            pk = type(exc).__name__

        try:
            json.dumps(Payload(fn, args))
            json_ok += 1
            js = "ok"
        except TypeError:
            js = "refused"

        try:
            marshal.dumps(Payload(fn, args))
            marshal_ok += 1
            ms = "ok"
        except ValueError:
            ms = "refused"

        print(f"    {label:<16}{pk:>13}{js:>12}{ms:>10}")

    print()
    print("  what the six calls returned, in order")
    returned = []
    for label, (fn, args) in PAYLOADS:
        returned.append(f"{label} -> {pickle.loads(pickle.dumps(Payload(fn, args)))!r}")
    for item in returned:
        print(f"    {item}")

    print()
    print(f"  pickle.loads called the named function  {pickle_called} of "
          f"{len(PAYLOADS)}")
    print(f"  json.dumps could express                {json_ok} of "
          f"{len(PAYLOADS)}")
    print(f"  marshal.dumps could express             {marshal_ok} of "
          f"{len(PAYLOADS)}")
    print()
    print("  none of the six is a class of yours, and none of them needed")
    print("  one. the stream carries the name of the function and the")
    print("  arguments to hand it, and loads() is the thing that does the")
    print("  calling.")
    print()
    print("  the last two columns are not safer versions of the first. they")
    print("  are formats that cannot express the object at all, which is a")
    print("  different property -- and it stops being available the moment")
    print("  you need the object back.")


if __name__ == "__main__":
    main()
