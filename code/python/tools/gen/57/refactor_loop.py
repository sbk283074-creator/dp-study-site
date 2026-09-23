"""Chapter 57 -- refactoring, verified by behaviour instead of by reading.

One messy function, refactored in five steps. Each step is checked against
the previous one by comparing what both versions return for every input we
can think of -- which is what makes the step a refactor rather than a
rewrite. The measurement is how many behaviours survived each step.
"""

from __future__ import annotations

from dataclasses import dataclass


# ------------------------------------------------- version 1: as found


def price_order_v1(raw: dict) -> dict:
    # do not judge too hard; this is a real function i have met
    out = {}
    out["total"] = 0
    out["items"] = 0
    for line in raw["lines"]:
        qty = line[2]
        cents = line[1]
        disc = 0
        if qty >= 10:
            disc = 10
        elif qty >= 5:
            disc = 5
        if raw["member"]:
            disc = disc + 5
        if disc > 20:
            disc = 20
        line_total = cents * qty
        line_total = line_total - (line_total * disc // 100)
        out["total"] = out["total"] + line_total
        out["items"] = out["items"] + qty
    if out["total"] > 50000:
        ship = 0
    elif out["total"] > 20000:
        ship = 500
    else:
        ship = 995
    out["shipping"] = ship
    out["total"] = out["total"] + ship
    out["currency"] = raw.get("currency", "USD")
    return out


# ------------------------------------------- version 2: name the concepts


@dataclass(frozen=True)
class Line:
    sku: str
    cents: int
    qty: int


def _tier_discount(qty: int) -> int:
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


def _member_bonus(is_member: bool) -> int:
    return 5 if is_member else 0


def discount_pct(line: Line, is_member: bool) -> int:
    return min(20, _tier_discount(line.qty) + _member_bonus(is_member))


def _shipping(subtotal_cents: int) -> int:
    if subtotal_cents > 50000:
        return 0
    if subtotal_cents > 20000:
        return 500
    return 995


def price_order_v2(raw: dict) -> dict:
    lines = [Line(sku, cents, qty) for sku, cents, qty in raw["lines"]]
    member = raw["member"]
    subtotal = 0
    items = 0
    for line in lines:
        pct = discount_pct(line, member)
        gross = line.cents * line.qty
        subtotal += gross - (gross * pct // 100)
        items += line.qty
    ship = _shipping(subtotal)
    return {
        "total": subtotal + ship,
        "items": items,
        "shipping": ship,
        "currency": raw.get("currency", "USD"),
    }


# ------------------------------------ version 3: a table instead of branch


TIERS = ((10, 10), (5, 5))  # (minimum qty, discount %)


def tier_discount_table(qty: int) -> int:
    for minimum, pct in TIERS:
        if qty >= minimum:
            return pct
    return 0


def discount_pct_table(line: Line, is_member: bool) -> int:
    return min(20, tier_discount_table(line.qty) + _member_bonus(is_member))


def price_order_v3(raw: dict) -> dict:
    lines = [Line(sku, cents, qty) for sku, cents, qty in raw["lines"]]
    member = raw["member"]
    subtotal = 0
    items = 0
    for line in lines:
        pct = discount_pct_table(line, member)
        gross = line.cents * line.qty
        subtotal += gross - (gross * pct // 100)
        items += line.qty
    ship = _shipping(subtotal)
    return {
        "total": subtotal + ship,
        "items": items,
        "shipping": ship,
        "currency": raw.get("currency", "USD"),
    }


# ------------------------------- version 4: composition instead of fields


def line_total_cents(line: Line, member: bool) -> int:
    gross = line.cents * line.qty
    pct = discount_pct_table(line, member)
    return gross - (gross * pct // 100)


def price_order_v4(raw: dict) -> dict:
    lines = [Line(*triple) for triple in raw["lines"]]
    member = raw["member"]
    subtotal = sum(line_total_cents(line, member) for line in lines)
    items = sum(line.qty for line in lines)
    ship = _shipping(subtotal)
    return {
        "total": subtotal + ship,
        "items": items,
        "shipping": ship,
        "currency": raw.get("currency", "USD"),
    }


# ------------------------------------------------- behaviour comparison


def make_cases() -> list[dict]:
    """Every shape of input the current callers can produce."""
    cases = []
    for member in (True, False):
        for qty in (0, 1, 4, 5, 9, 10, 25):
            for cents in (0, 99, 12_000, 40_000, 250_000):
                cases.append(
                    {
                        "lines": [("A", cents, qty), ("B", 500, 3)],
                        "member": member,
                    }
                )
    return cases


VERSIONS = [
    ("v1 as found", price_order_v1),
    ("v2 named", price_order_v2),
    ("v3 table", price_order_v3),
    ("v4 composed", price_order_v4),
]


def main() -> None:
    cases = make_cases()
    baseline = [price_order_v1(c) for c in cases]

    print("every version against every input v1 sees")
    print()
    print(f"  input shapes compared            {len(cases)}")
    print()
    print("  version          behaviours preserved   behaviours changed")
    for name, fn in VERSIONS:
        got = [fn(c) for c in cases]
        same = sum(1 for a, b in zip(got, baseline) if a == b)
        print(f"  {name:16} {same:>21} {len(cases) - same:>19}")
    print()

    print("what each step bought")
    print()
    steps = [
        ("v1 -> v2", "the three ideas inside the loop have names now"),
        ("v2 -> v3", "a tier is data, so adding one is one row and not a branch"),
        ("v3 -> v4", "the total is a sum of a named thing, not an accumulator"),
    ]
    for pair, gain in steps:
        print(f"  {pair:10} {gain}")
    print()
    print("  and what none of them changed: the answer. every row in the first")
    print("  table reads the same number, which is the only evidence that matters.")
    print("  a refactor is not a rewrite you feel good about -- it is one whose")
    print("  outputs you compared. if you did not compare them, you rewrote it.")
    print()

    print("adding a tier now costs")
    print()
    print("  before the step                 a new elif inside the hot loop")
    print("  after it                        (4, 2) appended to TIERS")
    print()
    print("  and this is the part to be honest about: v3 is not shorter than v2 and")
    print("  not simpler to read on its own. it is better only because the change")
    print("  somebody actually asked for became a data edit instead of a branch.")


if __name__ == "__main__":
    main()
