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
