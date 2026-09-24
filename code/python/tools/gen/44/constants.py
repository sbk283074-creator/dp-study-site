#!/usr/bin/env python3
"""Chapter 44 demo 6 -- the real constant factors, counted instead of timed.

The clock says these operations sit within a small factor of each other. The
count says the same thing, exactly, and it does not depend on what else the
machine was doing. The measure is the number of interpreter instructions one
evaluation of the expression compiles to.
"""
import dis


def instructions(expression):
    """How many instructions the interpreter runs for one evaluation."""
    code = compile(expression, "<operation>", "eval")
    return sum(1 for _ in dis.get_instructions(code))


# (label, the expression as it would be written in source)
OPS = [
    ("local read      x", "x"),
    ("global read     len", "len"),
    ("attribute read  p.x", "p.x"),
    ("list index      lst[0]", "lst[0]"),
    ("dict lookup     d['k']", "d['k']"),
    ("builtin call    len(lst)", "len(lst)"),
    ("isinstance      isinstance(x, int)", "isinstance(x, int)"),
    ("list build      [x, x]", "[x, x]"),
    ("method call     lst.count(1)", "lst.count(1)"),
    ("dict build      {'a': x}", "{'a': x}"),
    ("set build       {x, 1}", "{x, 1}"),
    ("f-string        f'{x}'", "f'{x}'"),
]

rows = [(label, instructions(expression)) for label, expression in OPS]
cheapest = min(count for _, count in rows)
dearest = max(count for _, count in rows)

print("every operation below is one evaluation of one expression. The")
print("measure is instructions run, which is exact and does not change")
print("with the machine or with the load on it.")
print()
print(f"{'operation':<36}{'instructions':>13}{'vs cheapest':>13}")
print("-" * 62)
for label, count in rows:
    print(f"{label:<36}{count:>13}{count / cheapest:>12.1f}x")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'operations compared':<46}{len(rows):>8}")
print(f"{'cheapest, in instructions':<46}{cheapest:>8}")
print(f"{'dearest, in instructions':<46}{dearest:>8}")
print(f"{'spread, dearest over cheapest':<46}{dearest / cheapest:>8.1f}")
print(f"{'operations within twice the cheapest':<46}"
      f"{sum(1 for _, c in rows if c <= 2 * cheapest):>8}")
print(f"{'operations within a factor of ten':<46}"
      f"{sum(1 for _, c in rows if c <= 10 * cheapest):>8}")

print()
print(f"The spread from the cheapest row to the dearest is {dearest / cheapest:.1f} times, and")
print("every operation here is within an order of magnitude of every other.")
print("That is the fact this chapter is built on: a constant factor of two or")
print("three is not worth restructuring a program for, because the operations")
print("you would restructure into are the same size as the ones you left.")
print()
print("It is also why the folklore about these operations is mostly wrong. The")
print("advice 'a dict lookup is fast but an attribute read is slow' is a claim")
print("about a difference you can see in this table and cannot notice in a")
print("program. What you can notice is doing one of them a million times more")
print("often -- which is a statement about the loop, not about the operation.")
print()
print("And counting is the honest way to make that argument. A stopwatch puts")
print("these twelve in one order on a quiet machine and a different order on a")
print("busy one, because the differences are smaller than the noise. The")
print("instruction count is the same number every time, which is what lets it")
print("be printed in a book.")
