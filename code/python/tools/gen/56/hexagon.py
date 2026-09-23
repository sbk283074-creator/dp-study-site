"""Chapter 56 -- the hexagon, and what actually stays out of the middle.

A pricing domain, one port the domain wrote for itself, and two adapters
that satisfy it. The measurement is how much of the domain mentions a
concrete technology, and how much has to change to swap one.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Protocol

# --------------------------------------------------------------- domain


@dataclass(frozen=True)
class Money:
    cents: int

    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)

    def __repr__(self) -> str:
        return f"${self.cents / 100:.2f}"


class TaxRates(Protocol):  # the port. the domain wrote this itself.
    def rate_bp(self, country: str) -> int:
        """VAT/sales tax in basis points -- hundredths of a percent."""
        ...


@dataclass
class Cart:
    country: str
    lines: list[tuple[str, Money]] = field(default_factory=list)

    def add(self, name: str, price: Money) -> None:
        self.lines.append((name, price))

    def subtotal(self) -> Money:
        return Money(sum(price.cents for _, price in self.lines))


def quote(cart: Cart, rates: TaxRates) -> Money:
    """Pure domain logic: subtotal plus the rate for this country."""
    taxable = cart.subtotal().cents * rates.rate_bp(cart.country) // 10_000
    return cart.subtotal() + Money(taxable)


# ------------------------------------------------------------- adapters


class FixedRates:
    """The adapter you write first: a constant rate for everybody."""

    def __init__(self, bp: int) -> None:
        self._bp = bp

    def rate_bp(self, country: str) -> int:
        return self._bp


class TableRates:
    """The adapter you write second: rates in a database table."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def rate_bp(self, country: str) -> int:
        row = self._conn.execute(
            "select bp from rates where country = ?", (country,)
        ).fetchone()
        if row is None:
            raise KeyError(f"no rate for {country!r}")
        return int(row[0])


# ----------------------------------------------------------- the count

DOMAIN_SOURCE = '''\
class TaxRates(Protocol):
    def rate_bp(self, country: str) -> int: ...

@dataclass
class Cart:
    country: str
    lines: list[tuple[str, Money]]

def quote(cart, rates):
    taxable = cart.subtotal().cents * rates.rate_bp(cart.country) // 10_000
    return cart.subtotal() + Money(taxable)'''


def main() -> None:
    DOMAIN_TECH = ("sqlite", "conn", "execute", "select ", "requests", "http")

    domain_lines = DOMAIN_SOURCE.splitlines()
    domain_mentions = [
        line.strip()
        for line in domain_lines
        for tech in DOMAIN_TECH
        if tech in line
    ]

    print("the domain, and how much technology it names")
    print()
    print(f"  lines in the domain                     {len(domain_lines)}")
    print(f"  lines naming a concrete technology      {len(domain_mentions)}")
    print(f"  technologies looked for                 {len(DOMAIN_TECH)}")
    print()

    conn = sqlite3.connect(":memory:")
    conn.execute("create table rates (country text primary key, bp integer)")
    conn.executemany(
        "insert into rates values (?, ?)",
        [("DE", 1900), ("FR", 2000), ("JP", 1000), ("US", 0)],
    )

    cart = Cart("DE")
    cart.add("mechanical keyboard", Money(12_000))
    cart.add("keycap set", Money(4_500))

    print("one domain, two adapters")
    print()
    print("  adapter        source                quote")
    for name, rates in (
        ("FixedRates", FixedRates(1900)),
        ("TableRates", TableRates(conn)),
    ):
        print(f"  {name:14} {rates.rate_bp('DE'):>3} bp from memory/db  {quote(cart, rates)}")
    print()

    print("what changed to swap them")
    print()
    print("  lines edited inside the domain          0")
    print("  lines written outside it                1  (which adapter you pass)")
    print()
    print("  the port is one method wide, so the whole seam is one signature:")
    print("  'i need a number for a country, and i will not say where it comes from'.")


if __name__ == "__main__":
    main()
