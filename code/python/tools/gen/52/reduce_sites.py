#!/usr/bin/env python3
"""Chapter 52 demo, part 2 -- four operations that run the same method.

If __reduce__ were only reached by loads(), the rule would be "never unpickle
untrusted data" and the chapter could stop. It is reached by four operations,
and only one of them is called deserialisation. This script counts the calls
for each one.
"""
import copy
import pickle


class Payload:
    def __init__(self, log):
        self.log = log

    def __reduce__(self):
        self.log.append("reduce")
        return (len, ("ab",))


OPERATIONS = [
    ("pickle.dumps", lambda p: pickle.dumps(p)),
    ("pickle.loads", lambda p: pickle.loads(pickle.dumps(p))),
    ("copy.copy", lambda p: copy.copy(p)),
    ("copy.deepcopy", lambda p: copy.deepcopy(p)),
]


def main():
    print(f"  operations tested                  {len(OPERATIONS):>3}")
    print("  the method                         Payload.__reduce__")
    print()
    print(f"    {'operation':<16}{'calls':>7}   result")

    called = 0
    for label, fn in OPERATIONS:
        log = []
        try:
            result = fn(Payload(log))
            # a written stream is bytes; report its size, not its contents
            shown = f"{len(result)} bytes" if isinstance(result, bytes) else repr(result)
        except Exception as exc:                       # noqa: BLE001
            shown = type(exc).__name__
        if log:
            called += 1
        print(f"    {label:<16}{len(log):>7}   {shown}")

    print()
    print(f"  operations that ran __reduce__     {called} of {len(OPERATIONS)}")
    print()
    print("  dumps runs it, which is the one place the callable is not")
    print("  invoked -- the tuple is being written down rather than used.")
    print("  loads runs it, which is the case the documentation warns about.")
    print()
    print("  copy and deepcopy run it too, and neither of them is called")
    print("  deserialisation. both take an object you already have, and an")
    print("  object you already have can be one that arrived from a stream.")
    print("  the boundary is not the function name. it is whether the object")
    print("  was ever under your control.")


if __name__ == "__main__":
    main()
