#!/usr/bin/env python3
"""Chapter 52 demo, part 3 -- the document that expands.

An XML document may declare its own entities, and an entity may be defined in
terms of the ones before it. Ten references to an entity of three characters
gives a thirty-character value; define the next entity as ten references to
that one and it gives three hundred. The document grows by one short line per
level. The value grows by a factor of ten.

The first five levels are parsed and measured. The rest is the same arithmetic,
and it is labelled as arithmetic rather than presented as a measurement,
because parsing level nine would need three gigabytes.
"""
import xml.etree.ElementTree as ET

BASE = "lol"
FACTOR = 10
MEASURED = 5
PROJECTED = 9
THRESHOLD = 1_000_000_000


def document(depth):
    lines = [f'<!ENTITY e0 "{BASE}">']
    for level in range(1, depth + 1):
        refs = "".join(f"&e{level - 1};" for _ in range(FACTOR))
        lines.append(f'<!ENTITY e{level} "{refs}">')
    return ('<?xml version="1.0"?>\n<!DOCTYPE r [\n' + "\n".join(lines) + "\n]>\n"
            f"<r>&e{depth};</r>")


def main():
    print(f"  base entity                        {BASE!r} ({len(BASE)} chars)")
    print(f"  references per level               {FACTOR}")
    print()
    print(f"    {'depth':>6}{'document bytes':>16}{'value chars':>15}{'growth':>9}")

    previous = len(BASE)
    measured = {}
    for depth in range(1, MEASURED + 1):
        doc = document(depth)
        try:
            root = ET.fromstring(doc)
            size = len(root.text or "")
        except ET.ParseError as exc:
            print(f"    {depth:>6}{len(doc):>16}{type(exc).__name__:>15}")
            break
        measured[depth] = size
        print(f"    {depth:>6}{len(doc):>16}{size:>15,}"
              f"{size / previous:>8.0f}x")
        previous = size

    print()
    print("  the same arithmetic, carried further")
    print(f"    {'depth':>6}{'document bytes':>16}{'value chars':>15}")
    for depth in range(MEASURED + 1, PROJECTED + 1):
        doc = document(depth)
        size = len(BASE) * FACTOR ** depth
        print(f"    {depth:>6}{len(doc):>16}{size:>15,}")

    smallest = next(d for d in range(1, 30)
                    if len(BASE) * FACTOR ** d >= THRESHOLD)
    doc = document(smallest)
    print()
    print(f"  a document of {len(doc)} bytes reaches "
          f"{len(BASE) * FACTOR ** smallest:,} characters")
    print(f"  at depth {smallest} -- the first level over "
          f"{THRESHOLD:,}.")
    print()
    print("  the reader that expands this is not broken. entity expansion is")
    print("  what the declaration is for. what the format does not have is a")
    print("  budget, and a parser cannot invent one, because it does not know")
    print("  how large a value the document was entitled to.")


if __name__ == "__main__":
    main()
