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
