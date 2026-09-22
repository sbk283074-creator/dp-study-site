#!/usr/bin/env python3
"""Chapter 52 demo, part 9 -- the limit is on the bytes you received.

Everything so far has been about a format that can carry more than data. This
is about the check that is supposed to bound the damage, and the mistake is not
that the check is wrong. It is that the check is on a different quantity from
the one that costs.

An upload endpoint with a four-kilobyte limit. Six documents, three ordinary
and three with entity declarations. Every one of them is well under the limit,
and the number that matters is not on the same axis as the number being checked.

The expansion figures for the three large documents are arithmetic from the
factor measured in part 3, not measurements -- parsing the middle one would need
three gigabytes.
"""
import xml.etree.ElementTree as ET

LIMIT_BYTES = 4096
BUDGET_CHARS = 100_000_000
BASE = "lol"
FACTOR = 10
ANCHOR = 4          # the depth that is actually parsed, as a check on the factor


def entity_document(depth):
    lines = [f'<!ENTITY e0 "{BASE}">']
    for level in range(1, depth + 1):
        refs = "".join(f"&e{level - 1};" for _ in range(FACTOR))
        lines.append(f'<!ENTITY e{level} "{refs}">')
    return ('<?xml version="1.0"?>\n<!DOCTYPE r [\n' + "\n".join(lines) + "\n]>\n"
            f"<r>&e{depth};</r>")


def plain_document(title):
    return ('<?xml version="1.0"?>\n'
            f"<note><title>{title}</title><body>nothing here</body></note>")


def uploads():
    rows = [
        ("notes.xml", plain_document("notes"), None),
        ("export.xml", plain_document("export"), None),
        ("backup.xml", plain_document("backup"), None),
        ("config.xml", entity_document(8), 8),
        ("theme.xml", entity_document(9), 9),
        ("report.xml", entity_document(10), 10),
    ]
    return rows


def main():
    # one real parse, to check the factor the projections rest on
    anchor = entity_document(ANCHOR)
    anchor_chars = len(ET.fromstring(anchor).text or "")

    print(f"  upload limit                       {LIMIT_BYTES:>5} bytes")
    print(f"  processing budget                  {BUDGET_CHARS:,} characters")
    print(f"  factor per entity level            {FACTOR:>5}x")
    print(f"  checked by parsing depth {ANCHOR}        {anchor_chars:>5} characters")
    print()
    print(f"    {'file':<14}{'bytes':>7}{'under limit':>13}"
          f"{'chars after parse':>19}{'over budget':>13}")

    under = 0
    over = 0
    flagged = 0
    largest = 0
    for name, doc, depth in uploads():
        size = len(doc.encode())
        chars = (len(BASE) * FACTOR ** depth) if depth else len(doc)
        is_under = size <= LIMIT_BYTES
        is_over = chars > BUDGET_CHARS
        has_dtd = b"<!ENTITY" in doc.encode()
        under += is_under
        over += is_over
        flagged += has_dtd
        largest = max(largest, size)
        print(f"    {name:<14}{size:>7}{'yes' if is_under else 'no':>13}"
              f"{chars:>19,}{'yes' if is_over else 'no':>13}")

    print()
    print(f"  documents under the upload limit      {under:>2} of "
          f"{len(uploads())}")
    print(f"  documents over the processing budget  {over:>2} of "
          f"{len(uploads())}")
    print(f"  documents carrying a DTD              {flagged:>2} of "
          f"{len(uploads())}")

    print()
    print("  the endpoint is not missing a check. it has one, the check is")
    print("  enforced, and every document passes it honestly -- the largest")
    print(f"  of the six is {largest} bytes.")
    print()
    print("  the problem is that the check is on the bytes received and the")
    print("  cost is on the value produced, and the format lets those two")
    print("  numbers be different by a factor the sender chooses. a limit on")
    print("  one of them is not a limit on the other.")
    print()
    print("  the third count is the one that would have worked. refusing a")
    print("  document that declares its own entities catches all three, and")
    print("  it is a property of the document rather than of the value, so")
    print("  it can be decided before anything is expanded.")


if __name__ == "__main__":
    main()
