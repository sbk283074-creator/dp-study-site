#!/usr/bin/env python3
"""Exercise 3 -- the sandbox that only removed one door.

Loading a small configuration file with eval is a real habit, and the first fix
everyone reaches for is to empty __builtins__. This script measures how much
that actually buys, against six hostile strings and four ordinary ones, using
three loaders.
"""
import ast

BENIGN = [
    "8",
    "'production'",
    "[1, 2, 3]",
    "{'debug': False}",
]

HOSTILE = [
    "__import__('os').environ",
    "open(__file__).read()",
    "globals()",
    "(1).__class__.__base__.__subclasses__()",
    "().__class__.__base__.__subclasses__()",
    "lambda: 1",
]


def load_plain(src):
    return eval(src)  # noqa: S307 -- this is the thing being measured


def load_no_builtins(src):
    return eval(src, {"__builtins__": {}})  # noqa: S307


def load_literal(src):
    return ast.literal_eval(src)


def try_load(fn, src):
    try:
        fn(src)
        return True
    except Exception:
        return False


def main():
    print(f"  ordinary configs                    {len(BENIGN):>3}")
    print(f"  hostile configs                     {len(HOSTILE):>3}")
    print()
    print(f"    {'loader':<24}{'accepted':>10}{'ran hostile':>13}")

    for name, fn in (("eval(src)", load_plain),
                     ("eval, no builtins", load_no_builtins),
                     ("ast.literal_eval", load_literal)):
        good = sum(1 for s in BENIGN if try_load(fn, s))
        bad = sum(1 for s in HOSTILE if try_load(fn, s))
        print(f"    {name:<24}{good:>6} of {len(BENIGN):<3}{bad:>7}"
              f" of {len(HOSTILE):<3}")

    print()
    print("  which hostile strings survive the empty-builtins sandbox")
    for src in HOSTILE:
        survived = try_load(load_no_builtins, src)
        mark = "runs" if survived else "blocked"
        print(f"    {mark:<9}{src}")

    print()
    print("  emptying __builtins__ removes the names. it does not remove")
    print("  attribute access, and attribute access is enough to walk from")
    print("  any object to the class hierarchy and back out to a module")
    print("  that does have __builtins__. three of the six never needed a")
    print("  builtin name in the first place.")
    print()
    print("  literal_eval is a different kind of answer: it does not run")
    print("  less of the string, it refuses to accept a string that is not")
    print("  data. that is why it also keeps all four ordinary configs.")


if __name__ == "__main__":
    main()
