"""Chapter 57 -- the strangler fig: replacing something that cannot stop.

A legacy pricing module with six callers. A rewrite means one afternoon with
nothing deployed and no way back. The strangler routes callers across one at
a time, so at every step both paths exist and either can serve everyone.
"""

from __future__ import annotations


def legacy_price(qty: int, cents: int) -> int:
    """1960 called. It rounds in a way nobody remembers choosing."""
    total = cents * qty
    if qty >= 10:
        total = total - total // 10
    return total + 995


def new_price(qty: int, cents: int) -> int:
    tier = 10 if qty >= 10 else (5 if qty >= 5 else 0)
    net = cents * qty
    return net - (net * tier // 100) + new_shipping(net)


def new_shipping(net: int) -> int:
    if net > 50_000 or net == 0:
        return 0
    if net > 20_000:
        return 500
    return 995


CALLERS = ["checkout", "invoice", "csv-export", "admin-preview", "api-v1", "batch-job"]


def step(routed: int) -> dict[str, str]:
    """Which implementation answers each caller at this point in the migration."""
    return {
        caller: ("new" if i < routed else "legacy")
        for i, caller in enumerate(CALLERS)
    }


def main() -> None:
    print("the migration, one caller at a time")
    print()
    print(f"  callers in total                    {len(CALLERS)}")
    print()
    print("  step   on new path   on legacy path   can roll back")
    for routed in range(len(CALLERS) + 1):
        table = step(routed)
        n_new = sum(1 for v in table.values() if v == "new")
        n_old = len(CALLERS) - n_new
        rollback = "yes" if routed < len(CALLERS) else "no -- nothing left to fall to"
        print(f"  {routed:>4} {n_new:>13} {n_old:>17}   {rollback}")
    print()

    print("the step nobody warns you about")
    print()
    table = step(3)
    print("  at step 3 the two implementations disagree somewhere:")
    print()
    print("  qty   cents     legacy      new     same")
    disagreements = 0
    checked = 0
    for qty in (1, 5, 9, 10, 25):
        for cents in (500, 12_000, 40_000):
            checked += 1
            a, b = legacy_price(qty, cents), new_price(qty, cents)
            same = a == b
            if not same:
                disagreements += 1
            print(f"  {qty:>3} {cents:>7} {a:>10} {b:>8}     {'yes' if same else 'NO'}")
    print()
    print(f"  inputs compared                     {checked}")
    print(f"  inputs where they disagree          {disagreements}")
    print()
    print("  this is why the strangler is not just a rewrite done slowly. while both")
    print("  paths run, the system has two answers to the same question, and every")
    print("  row above that says NO is a decision somebody has to make on purpose --")
    print("  either the legacy behaviour was a bug, or the new one is. guessing is")
    print("  how migrations ship a silent refund.")
    print()
    print("  the good part is that you find this out three callers in, with five")
    print("  still on the old path and a switch you can flip back.")


if __name__ == "__main__":
    main()
