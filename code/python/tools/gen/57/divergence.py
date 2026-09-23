"""Chapter 57 -- the abstraction that couples things which were going to differ.

Two departments want "the same" discount report. DRY is applied, and it
works until they diverge. The measurement is how many edits a real change
request costs in each design, and how many callers break in the wrong one.
"""

from __future__ import annotations


# ------------------------------------------- duplicated across two callers


def retail_discount(qty: int) -> int:
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


def wholesale_discount(qty: int) -> int:
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


# -------------------------------------------------------- DRY'd into one


def shared_discount(qty: int) -> int:
    """Used by both retail and wholesale. Looks like the obvious win."""
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


def measure_change(fn, label: str) -> None:
    """Apply wholesale's new rule, then ask what happened to retail."""
    print(f"  {label}")
    print(f"    requirements stated by retail          3 tiers")
    print(f"    requirements stated by wholesale       3 tiers (then one more)")


def main() -> None:
    print("two callers, one function; they have always returned the same number")
    print()
    print("  qty    retail    wholesale")
    for qty in (1, 5, 9, 10, 25):
        print(f"  {qty:<6} {retail_discount(qty):>6} {wholesale_discount(qty):>12}")
    print()

    print("the request: wholesale adds a 15% tier at qty >= 50")
    print()
    print("  design A -- two separate functions")
    print("    files edited                            1")
    print("    callers of retail affected              0")
    print("    retail's behaviour after the change     unchanged")
    print()
    print("  design B -- one shared function")
    print("    files edited                            1")
    print("    callers of retail affected              1")
    print("    retail's behaviour after the change     now has a 15% tier too")
    print()

    print("and here it is, actually happening")
    print()

    def shared_updated(qty: int) -> int:
        if qty >= 50:
            return 15
        if qty >= 10:
            return 10
        if qty >= 5:
            return 5
        return 0

    print("  qty    retail before   retail after")
    for qty in (25, 60):
        print(f"  {qty:<6} {retail_discount(qty):>13} {shared_updated(qty):>13}")
    print()
    print("  retail silently gained a discount tier nobody asked for. six callers")
    print("  down the line that shows up as a margin report that nobody can explain,")
    print("  because the change that caused it was made for a different department")
    print("  months earlier and every test for it passed.")
    print()

    print("the count that decides it")
    print()
    print("  identical today                           yes")
    print("  identical for a reason either can state   no")
    print("  owners                                    2 different teams")
    print()
    print("  duplication is far cheaper than the wrong abstraction, because a wrong")
    print("  abstraction is edited in one place and breaks in two, while duplication")
    print("  is edited in two places and breaks in none.")


if __name__ == "__main__":
    main()
