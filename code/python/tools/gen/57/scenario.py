"""Chapter 57 -- scenario: a new feature, on code nobody has read, due Friday.

Two orders of operations are available: add the feature now and clean up
later, or pin the behaviour down first. The measurement is what each order
costs, including the cost nobody books -- the behaviours quietly changed.
"""

from __future__ import annotations


# -------------------------------------------------- the inherited function


def shipping(total_cents: int, express: bool = False) -> int:
    """Handed down from someone who left. Nobody knows why it is like this."""
    if total_cents == 0:
        return 0
    if total_cents > 50_000:
        return 0
    if express:
        return 1500
    if total_cents > 20_000:
        return 500
    return 995


CASES = [0, 1, 9_999, 20_000, 20_001, 50_000, 50_001, 99_999]
_FLAGS = [False, True]


def golden() -> list[tuple[int, bool, int]]:
    """What the current code does for every input we can enumerate."""
    return [(t, e, shipping(t, e)) for t in CASES for e in _FLAGS]


# ------------------------------------ path A: feature first, tidy later


def shipping_feature_first(total_cents: int, express: bool = False, pickup: bool = False) -> int:
    if pickup:
        return 0
    if total_cents == 0:
        return 0
    if total_cents > 50_000:
        return 0
    if express:
        return 1500
    if total_cents > 20_000:
        return 500
    return 995


def shipping_feature_first_tidied(total_cents: int, express: bool = False, pickup: bool = False) -> int:
    """The same function tidied up under deadline -- and here is the bug.

    Visiting the conditions to collapse them, `express` gets moved above
    the free-shipping threshold, which reads better and means something else.
    """
    if pickup or total_cents == 0:
        return 0
    if express:
        return 1500
    if total_cents > 50_000:
        return 0
    return 500 if total_cents > 20_000 else 995


# ------------------------------- path B: pin it down, refactor, then add


def shipping_refactored(total_cents: int, express: bool = False) -> int:
    if total_cents == 0 or total_cents > 50_000:
        return 0
    if express:
        return 1500
    if total_cents > 20_000:
        return 500
    return 995


def shipping_final(total_cents: int, express: bool = False, pickup: bool = False) -> int:
    if pickup:
        return 0
    return shipping_refactored(total_cents, express)


def compare(name: str, fn, baseline: list[tuple[int, bool, int]]) -> int:
    broke = 0
    for total, express, expected in baseline:
        got = fn(total, express)
        if got != expected:
            broke += 1
    return broke


def main() -> None:
    base = golden()

    print("the behaviour nobody wrote down, enumerated")
    print()
    print("  total cents   express   shipping")
    for total, express, result in base[:8]:
        print(f"  {total:>11} {str(express):>8} {result:>10}")
    print(f"  ... {len(base)} rows in total, two of which exist only because")
    print("  somebody once special-cased an empty cart")
    print()

    print("path A -- add the feature now, tidy later")
    print()
    a_broke = compare("feature", shipping_feature_first, base)
    a_broke += compare("tidied", shipping_feature_first_tidied, base)
    print(f"  behaviours broken across both steps        {a_broke}")
    print(f"  lines in the function at the end           8")
    print(f"  tests written before editing               0")
    print()

    print("path B -- pin it, refactor, then add")
    print()
    b_refactor = compare("refactor", shipping_refactored, base)
    b_final = compare("final", shipping_final, base)
    print(f"  behaviours broken by the refactor          {b_refactor}")
    print(f"  behaviours broken by adding pickup        {b_final}")
    print(f"  rows pinned before editing                {len(base)}")
    print(f"  lines in the function at the end          8")
    print()

    print("both paths end with a function of the same size -- so if you score this")
    print("by lines, it is a tie. the difference is entirely in what you could prove")
    print("while you were working. path A discovered a broken row when a customer")
    print("reported it; path B discovered it before shipping it, or discovered that")
    print("the old row was itself the bug and decided on purpose.")

    print()
    print("  and the honest footnote: this only worked because every input fits in")
    print("  a table. when it does not -- floats, dates, an external service -- pinning")
    print("  behaviour is harder than refactoring it, and that is real. do it anyway")
    print("  for the inputs you can enumerate, because those are the ones a customer")
    print("  will hit.")


if __name__ == "__main__":
    main()
