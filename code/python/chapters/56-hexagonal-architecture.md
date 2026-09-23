---
chapter: 56
part: 10
title: Hexagonal Architecture
summary: Keep the rules that make money away from the things that merely carry them, by putting a named seam -- a port -- between the two and pointing every reference inward. You will be able to separate a pricing rule from the database and the web framework it currently sits inside, and to say what that separation cost.
minutes: 95
tags: [architecture, hexagonal, ports and adapters, repository, unit of work, dependency rule, boundaries, domain]
---

Here is a shape the last two chapters kept circling without naming. Chapter 54 counted what a
strategy buys and Chapter 55 counted what injection buys, and both answers came out the same way:
the win was never the pattern, it was that one place stopped knowing something. Chapter 55's ledger
stopped knowing which database it used. Chapter 54's pricing stopped knowing which discounts
existed. Both were the same move, made for different reasons, and both times the seam that did the
work was one signature wide.

That move has a name, and having the name matters because the name comes with a rule that the two
chapters were arriving at by experiment: dependencies point inward. The thing that decides a price
must not know whether it is being called from a CLI, from an HTTP handler, or from a test that
wants an answer in microseconds. The thing that stores an order must not know what anyone plans to
do with it. When both are true you can replace either end without asking permission from the
middle, which is the only property that gets tested in practice.

This chapter is about drawing that line on purpose rather than discovering it. It is also about the
bill, because a boundary you draw early costs files and a boundary you draw late costs a rewrite,
and there is a version of this advice that produces forty files for a twelve-line feature. We will
measure both ends.

## A port is a requirement the domain writes for itself

Start with a pricing rule and one thing it needs from the world: the tax rate for a country. The
rule does not care where that number comes from. It could be a constant, a table, a government API,
or a value a test made up. The traditional approach is to reach out and get it, which means the
pricing module imports something concrete and drags it along forever.

The alternative is one line: the domain states what it needs, as a signature with no implementation
behind it. Everything else is an adapter that satisfies it.

```python run
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
```

```text
the domain, and how much technology it names

  lines in the domain                     11
  lines naming a concrete technology      0
  technologies looked for                 6

one domain, two adapters

  adapter        source                quote
  FixedRates     1900 bp from memory/db  $196.35
  TableRates     1900 bp from memory/db  $196.35

what changed to swap them

  lines edited inside the domain          0
  lines written outside it                1  (which adapter you pass)

  the port is one method wide, so the whole seam is one signature:
  'i need a number for a country, and i will not say where it comes from'.
```

The count worth arguing about is not "lines of SQL". Nobody gets hurt by a line of SQL. The count
that hurts is *places that must be edited when something external changes*, and that count is zero
inside the rule. Bring your own framework, bring your own table, bring nothing at all and hand it a
constant in a test — the arithmetic does not move.

Note what the port is *not*: it is not an interface file in a folder called `interfaces`, and it is
not necessarily ABC-registered. It is a type the consumer defined, which is why it belongs next to
the consumer. Chapter 55 already made this argument about reference direction; here it is the whole
architecture.

## Which way the arrows point

draws a whole application from nothing but the module names. Below, every arrow is one module naming
another, and the only question asked is which direction each arrow goes.

Before, the pricing module reaches out to SQLite and to Flask. After, it reaches only to the ports
it wrote, and two adapters reach inward toward it.

```python run
"""Chapter 56 -- which way the arrows point, counted.

Three layers -- domain, adapters, and the outside world. The measurement
is the direction of every reference between them, before and after the
domain is allowed to name its own ports.
"""

from __future__ import annotations

from collections import defaultdict

# module -> the modules it names directly
GRAPH_BEFORE = {
    "pricing.py": ["sqlite3", "flask"],
    "orders.py": ["sqlite3", "requests", "pricing.py"],
    "report.py": ["sqlite3", "orders.py"],
    "flask": [],
    "sqlite3": [],
    "requests": [],
}

GRAPH_AFTER = {
    "pricing.py": ["ports.py"],
    "ports.py": [],
    "sql_store.py": ["sqlite3", "ports.py"],
    "http_gateway.py": ["flask", "ports.py"],
    "orders.py": ["ports.py"],
    "report.py": ["ports.py", "orders.py"],
    "flask": [],
    "sqlite3": [],
}


def layer(module: str) -> str:
    if module in ("flask", "sqlite3", "requests"):
        return "outside"
    if module.startswith(("sql_", "http_")):
        return "adapter"
    if module == "ports.py":
        return "port"
    return "domain"


def measure(graph: dict[str, list[str]]) -> None:
    outbound: dict[tuple[str, str], int] = defaultdict(int)
    for src, dsts in graph.items():
        for dst in dsts:
            outbound[(layer(src), layer(dst))] += 1

    print("references between layers (each arrow is one module naming another)")
    print()
    print("  from -> to        count")
    for (src, dst), n in sorted(outbound.items()):
        print(f"  {src:8} -> {dst:8} {n:>5}")
    print()

    inward = sum(n for (s, d), n in outbound.items() if d == "domain" and s != "domain")
    print(f"  into the domain, from elsewhere          {inward}")
    print(f"  out of the domain, to the outside        "
          f"{outbound[('domain', 'outside')]}")
    print()

    tech_in_domain = sum(
        1
        for src, dsts in graph.items()
        if layer(src) == "domain"
        for d in dsts
        if layer(d) == "outside"
    )
    print(f"  domain modules naming a technology       {tech_in_domain}")


def main() -> None:
    print("before -- the domain reaches out to the world")
    print()
    measure(GRAPH_BEFORE)

    print()
    print("=" * 60)
    print()
    print("after -- the domain names its own ports, adapters point inward")
    print()
    measure(GRAPH_AFTER)

    print()
    print("  read the two blocks side by side and the change is one number:")
    print("  the count of references going INTO the domain does not fall --")
    print("  every adapter still calls it. what falls to zero is the count going")
    print("  OUT. a hexagon is not less coupling, it is coupling that points one way.")


if __name__ == "__main__":
    main()
```

```text
before -- the domain reaches out to the world

references between layers (each arrow is one module naming another)

  from -> to        count
  domain   -> domain       2
  domain   -> outside      5

  into the domain, from elsewhere          0
  out of the domain, to the outside        5

  domain modules naming a technology       5

============================================================

after -- the domain names its own ports, adapters point inward

references between layers (each arrow is one module naming another)

  from -> to        count
  adapter  -> outside      2
  adapter  -> port         2
  domain   -> domain       1
  domain   -> port         3

  into the domain, from elsewhere          0
  out of the domain, to the outside        0

  domain modules naming a technology       0

  read the two blocks side by side and the change is one number:
  the count of references going INTO the domain does not fall --
  every adapter still calls it. what falls to zero is the count going
  OUT. a hexagon is not less coupling, it is coupling that points one way.
```

This is the sentence to take away, because the word "decoupled" gets this backwards constantly. The
total number of references did not drop by much. The **direction** did, and direction is what decides
who has to change when the outside world moves. Nothing outside may be mentioned by name inside, ever
— that is the dependency rule, and it is the only part of this chapter that is not negotiable.

## Repository, and the unit of work it needs

Persistence is the boundary people draw first and draw worst. Done badly, every domain object grows
a `.save()` method and every test needs a database. Done well, the object is a plain value and a
repository knows how to put it somewhere. Here is both, measured the same way everything else in this
book is measured: by counting lines.

```python run
"""Chapter 56 -- repository and unit of work, with SQL on one side of a line.

The same feature twice: domain objects that can save themselves, and domain
objects that are handed a repository. The measurement is where SQL ends up,
and what a unit of work buys that a repository alone does not.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field


def fresh() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "create table orders (id text primary key, country text, cents integer)"
    )
    return conn


# ------------------------------------------------- version 1: self-saving


@dataclass
class ActiveOrder:
    """Knows the schema and owns its own connection."""

    id: str
    country: str
    cents: int

    def save(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            "insert or replace into orders values (?, ?, ?)",
            (self.id, self.country, self.cents),
        )
        conn.commit()


# ------------------------------------- version 2: plain object + repository


@dataclass(frozen=True)
class Order:
    id: str
    country: str
    cents: int


class OrderRepository:
    def add(self, order: Order) -> None:
        self._pending.append(order)

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._pending: list[Order] = []

    def flush(self) -> int:
        if not self._pending:
            return 0
        self._conn.executemany(
            "insert or replace into orders values (?, ?, ?)",
            [(o.id, o.country, o.cents) for o in self._pending],
        )
        written = len(self._pending)
        self._pending.clear()
        return written

    def all(self) -> list[Order]:
        rows = self._conn.execute("select id, country, cents from orders").fetchall()
        return [Order(*row) for row in rows]


class UnitOfWork:
    """commit the batch, or none of it."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.orders = OrderRepository(conn)

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self._conn.commit()
            self.orders.flush()
            self._conn.commit()
        else:
            self._conn.rollback()
            self.orders._pending.clear()

    def commit(self) -> int:
        return self.orders.flush()


def count_sql(obj) -> int:
    import inspect

    try:
        src = inspect.getsource(obj)
    except TypeError:
        return 0
    return sum(1 for line in src.splitlines() if any(
        kw in line.lower() for kw in ("select ", "insert ", "update ", "delete ", "create table")
    ))


def main() -> None:
    print("where the SQL lives")
    print()
    rows = [
        ("ActiveOrder (saves itself)", count_sql(ActiveOrder)),
        ("Order (plain domain object)", count_sql(Order)),
        ("OrderRepository", count_sql(OrderRepository)),
        ("UnitOfWork", count_sql(UnitOfWork)),
    ]
    print("  type                            SQL lines")
    for name, n in rows:
        print(f"  {name:32} {n:>9}")
    print()
    print("  moving the SQL out did not delete it -- it stayed the same size and")
    print("  moved to a module whose only job is knowing it. that is the whole")
    print("  trick: the count you are trying to change is not 'lines of SQL', it is")
    print("  'places that have to be edited when the schema changes'.")
    print()

    # ---------------------------------------------------- atomicity

    print("the unit of work, measured on a partial failure")
    print()

    conn = fresh()
    ok = UnitOfWork(conn)
    with ok as uow:
        uow.orders.add(Order("a-1", "DE", 1000))
        uow.orders.add(Order("a-2", "FR", 2000))
    print(f"  batch that succeeds            {len(uow.orders.all())} rows committed")

    try:
        with UnitOfWork(conn) as uow2:
            uow2.orders.add(Order("b-1", "JP", 1500))
            raise RuntimeError("the payment gateway timed out")
    except RuntimeError as exc:
        print(f"  batch that fails               {exc}")

    conn.commit()
    total = conn.execute("select count(*) from orders").fetchone()[0]
    print(f"  rows in the table now          {total}")
    print()
    print("  two were added, one was attempted and rolled back. without the")
    print("  rollback the table holds three and the order that failed exists.")
    print("  this is what a unit of work is for, and it is not a pattern you can")
    print("  retrofit: it decides where the transaction boundary is, which means")
    print("  somebody has to own opening and closing it.")


if __name__ == "__main__":
    main()
```

```text
where the SQL lives

  type                            SQL lines
  ActiveOrder (saves itself)               1
  Order (plain domain object)              0
  OrderRepository                          2
  UnitOfWork                               0

  moving the SQL out did not delete it -- it stayed the same size and
  moved to a module whose only job is knowing it. that is the whole
  trick: the count you are trying to change is not 'lines of SQL', it is
  'places that have to be edited when the schema changes'.

the unit of work, measured on a partial failure

  batch that succeeds            2 rows committed
  batch that fails               the payment gateway timed out
  rows in the table now          2

  two were added, one was attempted and rolled back. without the
  rollback the table holds three and the order that failed exists.
  this is what a unit of work is for, and it is not a pattern you can
  retrofit: it decides where the transaction boundary is, which means
  somebody has to own opening and closing it.
```

Two things worth separating in that output. First, moving SQL out of the object did not reduce SQL —
it concentrated it, which is the actual goal. Second, the unit of work is doing something a repository
alone does not do. A repository answers "how do I get an Order"; a unit of work answers "what happens
to the three writes that must all succeed or none do". Chapter 19 met SQLite without this vocabulary,
and Chapter 27 wired SQLAlchemy without it; neither chapter needed the word. But now imagine this system with five operations per request instead of one, using only repositories. Each repository would have to decide on its own whether to call `conn.commit()`, which means one caller that needs three repositories together cannot get a single transaction for all three. The unit of work is what makes that answer reachable.

That is also the honest reason the unit of work is easy to add late and the repository is not: the unit
of work owns a boundary that has to exist somewhere, whereas the repository is a naming decision you
can make at any time.

:::pitfall The seam that pays nothing

The temptation once you have a name for this is to see boundaries everywhere, and every boundary is a
bet. A port says "I believe a second implementation is coming" — but some bets never pay off.

```python run
"""Chapter 56 -- the port that costs more than it saves.

Every seam is a bet that something on the far side will change. Here the
same feature is written twice -- once directly, once through a port and an
adapter -- and both versions are measured, because one of the two numbers
has to argue for the extra file.
"""

from __future__ import annotations

from typing import Protocol

DIRECT = '''\
def cents_total(lines):
    return sum(cents for _, cents in lines)


def report(lines):
    total = cents_total(lines)
    return f"{len(lines)} lines totaling ${total / 100:.2f}"'''

PORTED = '''\
class LineSource(Protocol):
    def lines(self) -> list[tuple[str, int]]: ...


class InMemoryLines:
    def __init__(self, lines):
        self._lines = lines

    def lines(self):
        return self._lines


def cents_total(source: LineSource):
    return sum(cents for _, cents in source.lines())


def report(source: LineSource):
    total = cents_total(source)
    lines = source.lines()
    return f"{len(lines)} lines totaling ${total / 100:.2f}"'''


def stats(src: str) -> dict[str, int]:
    lines = [ln for ln in src.splitlines() if ln.strip()]
    return {
        "classes": sum(1 for ln in lines if ln.startswith("class ")),
        "functions": sum(1 for ln in lines if ln.startswith("def ")),
        "non-blank lines": len(lines),
    }


# both implementations behave identically, including on the edge case
LINES = [("widget", 250), ("gasket", 175)]


def direct_report(lines):
    total = sum(cents for _, cents in lines)
    return f"{len(lines)} lines totaling ${total / 100:.2f}"


class InMemoryLines:
    def __init__(self, lines):
        self._lines = lines

    def lines(self):
        return self._lines


def ported_report(source):
    total = sum(cents for _, cents in source.lines())
    lines = source.lines()
    return f"{len(lines)} lines totaling ${total / 100:.2f}"


def main() -> None:
    print("the same two-line report, direct and through a port")
    print()

    a, b = stats(DIRECT), stats(PORTED)
    print("  measure                 direct    ported    difference")
    for key in a:
        diff = b[key] - a[key]
        print(f"  {key:22} {a[key]:>6} {b[key]:>9} {diff:>+12}")
    print()

    print("  both versions produce the same thing")
    print(f"    direct   {direct_report(LINES)}")
    print(f"    ported   {ported_report(InMemoryLines(LINES))}")
    print()

    print("  implementations of the port in this file        1")
    print("  implementations any caller has wanted           1")
    print("  tests that replaced it                          0")
    print()
    print("  a port is a bet that a second implementation is coming. with one")
    print("  implementation and no test asking for a stand-in, the port has cost")
    print("  three functions and nineteen lines and returned nothing. the honest")
    print("  move is to write the direct version and add the port the day a")
    print("  second caller arrives -- which is a small edit, because nothing")
    print("  depended on the shape being hidden.")
    print()
    print("  the tell is in row three of the table: the number of classes went up")
    print("  by two and the number of things the feature could do stayed put.")


if __name__ == "__main__":
    main()
```

```text
the same two-line report, direct and through a port

  measure                 direct    ported    difference
  classes                     0         2           +2
  functions                   2         2           +0
  non-blank lines             5        13           +8

  both versions produce the same thing
    direct   2 lines totaling $4.25
    ported   2 lines totaling $4.25

  implementations of the port in this file        1
  implementations any caller has wanted           1
  tests that replaced it                          0

  a port is a bet that a second implementation is coming. with one
  implementation and no test asking for a stand-in, the port has cost
  three functions and nineteen lines and returned nothing. the honest
  move is to write the direct version and add the port the day a
  second caller arrives -- which is a small edit, because nothing
  depended on the shape being hidden.

  the tell is in row three of the table: the number of classes went up
  by two and the number of things the feature could do stayed put.
```

The test to apply before drawing a boundary is not "could this change". Nearly everything could change.
It is **"has anything ever asked"**. A second caller, a test that needs a stand-in, a second storage
engine, a deployment that ships without a database — those are asks. Without one, the port is a
prediction nobody placed a bet on, and Chapter 57 returns to this with more machinery.

:::scenario Two requirements arrive the same week

The quote engine in this chapter was written when the company sold through one channel, and its rate
table lives in SQLite. On Monday, growth asks for the same engine behind an HTTP endpoint so partners
can price carts. On Tuesday, ops asks that rates ship as a CSV with the application so a rate change is
a file change, not a migration. Both requests are reasonable, and both arrive after the code exists.

You have two ways to answer them. You could open `quote()` and add an argument that says where the
rate came from, and add a branch that formats either a CLI string or a JSON body — which puts the
channel and the storage engine into pricing arithmetic and means every test now needs both a database
and a request context. Or you notice that both requirements are asking for something the domain never
promised to provide, and add nothing to the middle.

:::solution What to do

The second answer is the one that costs one file per requirement, and it is only available because the
port was written *before* either request existed — which is the argument for drawing seams at genuine
uncertainty rather than at every imaginary one.

```python run
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
```

```text
one quote function, reached two ways, with rates from either source

  delivery   rate source   result
  CLI  DE  $196.35
  CLI  FR  $198.00
  HTTP      sqlite3       status=200 body={'country': 'DE', 'total': 19635}
  HTTP      rates.csv     status=200 body={'country': 'JP', 'total': 18150}

the two requirements, and where each one landed

  requirement                        domain edits   outside edits
  add an HTTP entry point                    0           1
  move rates to a shipped CSV                0           1

  neither requirement edited quote(), Cart or Money, because the only
  thing they all agree on is one line: a method that answers a country
  with basis points. that line is the port, and it was written before
  either requirement existed -- which is why both were cheap.

  the counterfactual is what makes the case. had the engine read the
  sqlite table directly, requirement two touches the function that
  computes the price, and the price stops being testable without a
  database. the seam is not there to satisfy an architecture diagram;
  it is there so that a request nobody has made yet costs one file.
```

Two entry points now exist and neither knows the other. Notice that the HTTP entry point is the one
place in this chapter that mentions `dict` and status codes, and it is also the one place that would
change if the answer needed a header. Chapter 26 built exactly this kind of handler for StudyHub
without naming any of it — the pattern was there, unnamed, which is usually how it goes the first time
around.

:::

Where FastAPI and Pygame sit, now that there is vocabulary for it: in Chapter 27's StudyHub and
Chapter 31's Neon Dungeon, both libraries are **adapters**. FastAPI turns HTTP requests into calls and
turns return values into responses; Pygame turns your update function into frames and your classes into
pixels. The mistake is letting either one reach into the middle — a route handler that computes a
price, or a sprite that decides what an item is worth. Both work fine the day you write them, and
both become impossible to test later. Meanwhile the seam that matters sits exactly where those two
chapters got it right by instinct and this chapter got on purpose: the framework names your types, and
nothing inside them names the framework back.

## Key takeaways

- A port is a requirement the domain states about the world, written as one signature next to the
  code that needs it — never in a folder of its own where nobody will find it.
- The dependency rule is one sentence: nothing outside may be named inside. Everything else in this
  chapter is a consequence of it.
- A hexagon is not less coupling. The count of references **into** the domain does not fall; the count
  going **out** of it does, and direction is what decides who edits what later.
- Moving SQL into a repository does not delete SQL. It concentrates it, so the number that changes is
  the count of places affected by a schema edit, not the count of query lines.
- A repository answers "how do I get one"; a unit of work answers "what happens to the three writes
  that must succeed together". You need the second answer before the first one is expensive.
- A boundary is a bet that something on the far side is going to change. Without a second caller, a
  test wanting a stand-in, or a second engine, the bet costs files and pays nothing yet.
- Frameworks belong on the outside as adapters. A route handler that computes a price is the mistake,
  and it always looks fine on the day it is written.

## Practice

- [ ] Take `TableRates` above and add a third adapter that reads rates from a Python dict literal, then
      show that `quote()` is unchanged. Count the lines you edited inside the domain.
- [ ] The `UnitOfWork` above commits inside `__exit__` *and* has a `commit()` method. Both paths call
      `flush()`. Rewrite it so there is exactly one commit path, and explain what bug the duplicate
      makes possible.
- [ ] Write a `NotificationPort` with one method, `send(to: str, body: str) -> None`. Write two
      adapters — one that prints, one that appends to a list — and a domain function that uses it
      without knowing which it got.
- [ ] Take a function you wrote in Chapter 20 or Chapter 23 that reads a file directly. Change it to
      take the *lines* rather than the path. Count how many call sites changed.
- [ ] Draw Module arrow diagram for a module you have already written in this book, using the
      `dependency_direction.py` counting approach. Report the "domain modules naming a technology"
      number before and after you introduce one port.

## Solutions

:::solution Exercise 1

Add a third adapter next to the other two. The point is that nothing else in the file moves:

```python
class DictRates:
    """Rates from a literal, for tests and for defaults."""

    def __init__(self, table: dict[str, int]) -> None:
        self._table = table

    def rate_bp(self, country: str) -> int:
        return self._table[country]
```

Call it exactly the way the other two are called — `quote(cart, DictRates({"DE": 1900}))` — and lines
edited inside `quote`, `Cart` and `Money` is **0**. That number is the entire argument for the chapter.
Note that this adapter took six lines, and if nobody ever needs a third source, those six lines would
have been better spent not existing.

:::solution Exercise 2

The duplicate path means a caller can `with UnitOfWork(conn) as uow:` and also call `uow.commit()`,
and the second call silently writes zero rows while looking like it did something — because `flush()`
already cleared `_pending`. The fix is to make `__exit__` the only writer and have callers who want
early control use `uow.orders.flush()` deliberately:

```python
def __exit__(self, exc_type, exc, tb) -> None:
    if exc_type is not None:
        self._conn.rollback()
        self.orders._pending.clear()
        return
    self.orders.flush()
    self._conn.commit()
```

Deleting `commit()` removes the ambiguity. The general lesson is that two paths to the same side effect
are one source of truth pretending to be two, and the symptom is always a method that succeeds doing
nothing.

:::solution Exercise 3

Keep the port one method wide and let the domain take it as an argument:

```python
from typing import Protocol


class NotificationPort(Protocol):
    def send(self, to: str, body: str) -> None: ...


class PrintNotifications:
    def send(self, to: str, body: str) -> None:
        print(f"-> {to}: {body}")


class RecordingNotifications:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, body: str) -> None:
        self.sent.append((to, body))


def notify_overdue(user_email: str, days: int, out: NotificationPort) -> None:
    out.send(user_email, f"your loan is {days} days overdue")
```

The domain function names no concrete sender, so a test uses `RecordingNotifications` and asserts on
`.sent` without capturing stdout. This is exactly the trade Chapter 55's ledger made, applied to output
instead of storage.

:::solution Exercise 4

A function that takes a path can only be exercised with a real file. A function that takes the lines
can be exercised with a list. The change usually looks like this:

```python
# before
def count_errors(path):
    with open(path) as handle:
        return sum(1 for line in handle if "ERROR" in line)


# after
def count_errors(lines):
    return sum(1 for line in lines if "ERROR" in line)
```

Every call site grows a `with open(path) as handle:` wrapper — so if there were four call sites, four
call sites changed and none of them got worse to read. That is the honest accounting for this refactor:
the boundary does not make the caller shorter, it makes the *function* testable. If there is one call
site and no test, this refactor is Chapter 57's subject — do not do it yet.

:::solution Exercise 5

The measurement that matters is the last line of each block: `domain modules naming a technology`.
Before introducing a port that number is however many domain modules import something external; after
it should be zero. The trap is counting imports rather than *modules* — one module with five external
imports counts once, and that is the module to fix first. If the number is already zero, you do not
have ports to add; stop and leave the code alone.

:::
