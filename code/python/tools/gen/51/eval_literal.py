#!/usr/bin/env python3
"""Chapter 51 demo, part 5 -- eval, literal_eval, and a restricted eval.

`eval` runs its argument. `ast.literal_eval` parses its argument and returns
the value only if the whole thing is a literal. Those are different promises
and the difference is measurable: feed both the same set of strings and count
what each accepts.

The third column is the one that matters for people who try to fix `eval` by
taking the builtins away. That is a filter, not a sandbox, and a filter has a
coverage number.

Nothing prints a payload's *value* -- several of them return machine-specific
objects. The counts are of accepted versus rejected, which is a fact about the
functions rather than about this computer.
"""
import ast

LITERALS = [
    "[1, 2, 3]",
    '{"a": 1}',
    "(1, 2)",
    '"x"',
    "42",
    "True",
    "None",
    "1.5",
    "[[1], [2]]",
    "{1, 2}",
]

CODE = [
    '__import__("sys")',
    "1 + 1",
    "[i for i in range(3)]",
    "(lambda: 1)()",
    "().__class__",
    'exec("y = 1")',
    '__import__("os").getpid()',
    "globals()",
]

BIG = "[" + ",".join(["1"] * 20000) + "]"


def accepts(fn, text):
    try:
        fn(text)
        return True
    except Exception:
        return False


def main():
    print(f"  literal strings                    {len(LITERALS):>3}")
    print(f"  code strings                       {len(CODE):>3}")
    print()
    print(f"    {'input':<32}{'eval':>7}{'literal_eval':>14}{'restricted eval':>17}")

    ev = lv = rv = 0
    for s in LITERALS:
        a = accepts(eval, s)
        b = accepts(ast.literal_eval, s)
        c = accepts(lambda t: eval(t, {"__builtins__": {}}), s)
        ev += a
        lv += b
        rv += c
        print(f"    {s:<32}{('yes' if a else 'no'):>7}{('yes' if b else 'no'):>14}"
              f"{('yes' if c else 'no'):>17}")

    print()
    ev_c = lv_c = rv_c = 0
    for s in CODE:
        a = accepts(eval, s)
        b = accepts(ast.literal_eval, s)
        c = accepts(lambda t: eval(t, {"__builtins__": {}}), s)
        ev_c += a
        lv_c += b
        rv_c += c
        print(f"    {s:<32}{('yes' if a else 'no'):>7}{('yes' if b else 'no'):>14}"
              f"{('yes' if c else 'no'):>17}")

    print()
    print(f"  of {len(LITERALS)} literals   eval {ev}, literal_eval {lv}, restricted {rv}")
    print(f"  of {len(CODE)} code strings  eval {ev_c}, literal_eval {lv_c}, "
          f"restricted {rv_c}")
    print()
    print(f"  literal_eval rejected {len(CODE) - lv_c} of {len(CODE)} code strings"
          f" and {len(LITERALS) - lv} of {len(LITERALS)} literals.")
    print(f"  restricted eval still ran {rv_c} of {len(CODE)}"
          f" -- a filter, with a coverage number.")

    # Safety from code execution is not safety from resource use.
    print()
    print(f"  a literal of {len(BIG):,} characters")
    try:
        obj = ast.literal_eval(BIG)
        print(f"    literal_eval accepts it            {len(obj):>7,} elements")
    except Exception as exc:
        print(f"    literal_eval rejects it            {type(exc).__name__}")
    print("    both functions accept it, because neither has a size limit.")
    print("    literal_eval is a promise about *parsing*, not about resources.")


if __name__ == "__main__":
    main()
