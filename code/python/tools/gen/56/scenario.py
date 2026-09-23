"""Chapter 56 -- scenario: the quote engine has to be reachable two ways,
and the rate table has to move out of the database.

Two requirements arrive the same week. The measurement is where the edits
land, and how much of the engine either requirement touched.
"""

from __future__ import annotations

import csv
import io
import sqlite3
from dataclasses import dataclass, field
from typing import Protocol


# ------------------------------------------------------------- domain


@dataclass(frozen=True)
class Money:
    cents: int

    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)

    def __repr__(self) -> str:
        return f"${self.cents / 100:.2f}"


class TaxRates(Protocol):
    def rate_bp(self, country: str) -> int: ...


@dataclass
class Cart:
    country: str
    lines: list[tuple[str, Money]] = field(default_factory=list)

    def subtotal(self) -> Money:
        return Money(sum(p.cents for _, p in self.lines))


def quote(cart: Cart, rates: TaxRates) -> Money:
    return cart.subtotal() + Money(
        cart.subtotal().cents * rates.rate_bp(cart.country) // 10_000
    )


# ----------------------------------------------------------- adapters


class SqlRates:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def rate_bp(self, country: str) -> int:
        row = self._conn.execute(
            "select bp from rates where country = ?", (country,)
        ).fetchone()
        return int(row[0])


class FileRates:
    """Reads a rates.csv that ships with the application."""

    def __init__(self, text: str) -> None:
        reader = csv.DictReader(io.StringIO(text))
        self._table = {row["country"]: int(row["bp"]) for row in reader}

    def rate_bp(self, country: str) -> int:
        return self._table[country]


# --------------------------------------------------- delivery mechanisms


def cli_entry(country: str, rates: TaxRates) -> str:
    cart = Cart(country, [("keyboard", Money(12_000)), ("keycaps", Money(4_500))])
    return f"CLI  {country}  {quote(cart, rates)}"


def http_entry(country: str, rates: TaxRates) -> dict[str, object]:
    cart = Cart(country, [("keyboard", Money(12_000)), ("keycaps", Money(4_500))])
    total = quote(cart, rates)
    return {"status": 200, "body": {"country": country, "total": total.cents}}


CSV = "country,bp\nDE,1900\nFR,2000\nJP,1000\nUS,0\n"


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("create table rates (country text primary key, bp integer)")
    conn.executemany(
        "insert into rates values (?,?)", [("DE", 1900), ("FR", 2000), ("JP", 1000), ("US", 0)]
    )

    shared = SqlRates(conn)
    moving = FileRates(CSV)

    print("one quote function, reached two ways, with rates from either source")
    print()
    print("  delivery   rate source   result")
    print(f"  {cli_entry('DE', shared)}")
    print(f"  {cli_entry('FR', moving)}")
    body = http_entry("DE", shared)
    print(f"  HTTP      sqlite3       status={body['status']} body={body['body']}")
    body2 = http_entry("JP", moving)
    print(f"  HTTP      rates.csv     status={body2['status']} body={body2['body']}")
    print()

    print("the two requirements, and where each one landed")
    print()
    print("  requirement                        domain edits   outside edits")
    print("  add an HTTP entry point                    0           1")
    print("  move rates to a shipped CSV                0           1")
    print()
    print("  neither requirement edited quote(), Cart or Money, because the only")
    print("  thing they all agree on is one line: a method that answers a country")
    print("  with basis points. that line is the port, and it was written before")
    print("  either requirement existed -- which is why both were cheap.")
    print()
    print("  the counterfactual is what makes the case. had the engine read the")
    print("  sqlite table directly, requirement two touches the function that")
    print("  computes the price, and the price stops being testable without a")
    print("  database. the seam is not there to satisfy an architecture diagram;")
    print("  it is there so that a request nobody has made yet costs one file.")


if __name__ == "__main__":
    main()
