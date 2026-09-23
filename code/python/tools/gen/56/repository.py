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
