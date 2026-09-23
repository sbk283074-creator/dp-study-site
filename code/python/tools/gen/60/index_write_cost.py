"""Chapter 60 -- an index is a second copy, and every write maintains it.

Reading a table is cheap to reason about because nothing moves. An index is
the opposite: it is a sorted structure that has to be correct after every
insert, so the write path pays for it forever and the read path pays for it
once. The count is of comparisons, on both sides of the ledger.
"""

ROWS = 4096


def boundary(rows):
    """Comparisons to find one key in a sorted list of this many entries."""
    count = 0
    size = rows
    while size > 1:
        size = (size + 1) // 2
        count += 1
    return count


def build_cost(rows):
    """Comparisons to insert every row into one sorted index, in order."""
    return sum(boundary(size) for size in range(1, rows + 1))


LOOKUP_INDEXED = boundary(ROWS) + 1
LOOKUP_SCAN = ROWS // 2

print(f"{ROWS:,} rows, one index maintained per row inserted")
print()
print(f"{'indexes':>8}{'to build':>12}{'per lookup saved':>18}{'lookups to repay':>18}")
print("-" * 56)
for count in (0, 1, 2, 3, 4):
    build = count * build_cost(ROWS)
    saved = LOOKUP_SCAN - (LOOKUP_INDEXED if count else LOOKUP_SCAN)
    repay = build / saved if saved else 0
    print(f"{count:>8}{build:>12,}{saved:>18,}{repay:>18,.0f}")

print()
print(f"A lookup with no index costs {LOOKUP_SCAN:,} comparisons on average.")
print(f"A lookup through the index costs {LOOKUP_INDEXED}, plus a fetch per match.")
print(f"Building one index costs {build_cost(ROWS):,} comparisons.")
print()
print("So the index is not a saving that starts at the first read. It is a debt")
print("taken out on the write path and repaid by repetition. A second index on")
print("another column does not make this lookup cheaper -- the 2,035 saved above")
print("is the same for one index and for four -- and it takes out the same debt")
print("again. What an index buys is one predicate, and it charges for every row.")
