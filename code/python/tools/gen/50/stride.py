#!/usr/bin/env python3
"""Chapter 50 demo, part 4 -- the threat model as arithmetic.

STRIDE is a completeness device: six questions to ask of every element on a
data-flow diagram, so that you do not forget one. It is not a ranking device,
and this script shows why the difference matters.

Two counts come out of it and they say different things. The first is the
number of applicable threats, which is what people quote. The second is the
number of threats *per category*, which is a property of how many elements of
each kind your diagram happens to have -- not of your risk. Redraw the same
system with one box labelled differently and the total moves without a line
of code changing.
"""

STRIDE = (
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information disclosure",
    "Denial of service",
    "Elevation of privilege",
)

# Which of the six questions apply to which kind of element. This is the
# standard applicability matrix, not a judgement about this system.
APPLICABLE = {
    "external entity": ("Spoofing", "Repudiation"),
    "process": STRIDE,
    "data store": ("Tampering", "Repudiation", "Information disclosure", "Denial of service"),
    "data flow": ("Tampering", "Information disclosure", "Denial of service"),
}

KINDS = ("external entity", "process", "data store", "data flow")

ELEMENTS = [
    ("browser", "external entity"),
    ("external_api", "external entity"),
    ("proxy", "process"),
    ("app", "process"),
    ("worker", "process"),
    ("admin_cli", "process"),
    ("db", "data store"),
    ("cache", "data store"),
    ("objects", "data store"),
    ("backup", "data store"),
    ("browser->cdn", "data flow"),
    ("proxy->app", "data flow"),
    ("app->db", "data flow"),
    ("app->cache", "data flow"),
    ("app->objects", "data flow"),
    ("app->external_api", "data flow"),
    ("worker->db", "data flow"),
    ("admin_cli->db", "data flow"),
]

SHORT = {
    "Spoofing": "S",
    "Tampering": "T",
    "Repudiation": "R",
    "Information disclosure": "I",
    "Denial of service": "D",
    "Elevation of privilege": "E",
}


def build(elements):
    """Return (cells, applicable, per_category, per_kind)."""
    cells = []
    for name, kind in elements:
        for cat in STRIDE:
            cells.append((name, kind, cat, cat in APPLICABLE[kind]))
    applicable = [c for c in cells if c[3]]
    per_cat = {cat: sum(1 for c in applicable if c[2] == cat) for cat in STRIDE}
    per_kind = {k: sum(1 for c in applicable if c[1] == k) for k in KINDS}
    return cells, applicable, per_cat, per_kind


def main():
    cells, applicable, per_cat, per_kind = build(ELEMENTS)

    print(f"  elements on the diagram             {len(ELEMENTS):>3}")
    print(f"  STRIDE questions per element        {len(STRIDE):>3}")
    print(f"  cells in the matrix                 {len(cells):>3}")
    print(f"  cells that apply                    {len(applicable):>3}"
          f"   ({len(applicable) / len(cells):.1%})")

    print()
    print("  the matrix, as a diagram would draw it")
    print()
    print(f"    {'element':<20}{'kind':<16}" + "".join(f"{SHORT[c]:>3}" for c in STRIDE))
    for name, kind in ELEMENTS:
        row = "".join(("  x" if cat in APPLICABLE[kind] else "  .").rjust(3) for cat in STRIDE)
        print(f"    {name:<20}{kind:<16}{row}")
    print(f"    {'':<20}{'':<16}" + "".join(f"{SHORT[c]:>3}" for c in STRIDE))

    print()
    print("  threats per category -- a property of the diagram, not of the risk")
    ranked = sorted(STRIDE, key=lambda c: (-per_cat[c], c))
    for cat in ranked:
        bar = "#" * per_cat[cat]
        print(f"    {cat:<26}{per_cat[cat]:>3}  {bar}")

    print()
    print("  threats per element kind")
    for kind in KINDS:
        n = sum(1 for _, k in ELEMENTS if k == kind)
        each = len(APPLICABLE[kind])
        print(f"    {kind:<18}{n:>3} elements x {each} questions = {per_kind[kind]:>3}")

    # The counterfactual: the same system, one box relabelled. Nothing about the
    # software changed -- only which word is written under the box.
    swapped = [(name, "process" if kind == "data store" else kind) for name, kind in ELEMENTS]
    _, applicable2, per_cat2, _ = build(swapped)
    moved = sum(1 for cat in STRIDE if per_cat[cat] != per_cat2[cat])

    print()
    print("  the same system, with the four data stores drawn as processes instead")
    print(f"    applicable threats                 {len(applicable):>3} -> {len(applicable2)}"
          f"   ({len(applicable2) - len(applicable):+d})")
    print(f"    categories whose count changed     {moved:>3} of {len(STRIDE)}")
    for cat in STRIDE:
        if per_cat[cat] != per_cat2[cat]:
            print(f"      {cat:<26}{per_cat[cat]:>3} -> {per_cat2[cat]}")
    print()
    print("  nothing in the code changed. Only the words under the boxes.")


if __name__ == "__main__":
    main()
