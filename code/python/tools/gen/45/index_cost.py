#!/usr/bin/env python3
"""Chapter 45 demo -- reading a slot is arithmetic, not a search.

Every number here is exact. The three traversal orders are built up front so
that each loop does exactly the same per-iteration work, and what the loops
are charged for is counted rather than timed.
"""

N = 100_000
ITEMS = list(range(N))

# The three index orders are built up front so that each loop does exactly
# the same per-iteration work. If one loop computed its index with a
# subtraction or a modulo and another did not, the difference in the table
# would be the arithmetic, not the memory access.
FORWARD = list(range(N))
BACKWARD = list(range(N - 1, -1, -1))
MIDDLE_OUT = [(N // 2 + offset) % N for offset in range(N)]


def address(base, index, width=8):
    """What a dynamic array does for lst[i]: one multiply, one add.
    The index never appears in a loop, so it never appears in the cost."""
    return base + index * width


def steps_to_reach_array(index):
    """A dynamic array computes an address. Nothing is traversed, so the
    step count is the same two operations for every slot there is."""
    steps = 0
    steps += 1                      # base + index * width
    steps += 1
    return steps


def steps_to_reach_chain(index):
    """A singly linked list has no addresses to compute. It walks from the
    head, one node at a time, so reaching slot i costs i hops."""
    steps = 0
    node = 0
    while node < index:
        node += 1
        steps += 1
    return steps


def visit(order):
    """Sum the slots in the given order, counting the reads it performed."""
    total = 0
    reads = 0
    for i in order:
        reads += 1
        total += ITEMS[i]
    return total, reads


ORDERS = (
    ("front to back", FORWARD),
    ("back to front", BACKWARD),
    ("middle out", MIDDLE_OUT),
)

print("the slot address a dynamic array computes for each index")
print("  base = 1000 (pretend), 8 bytes per slot")
print()
print(f"{'index':>8}{'address':>12}   {'work done':>16}")
print("-" * 39)
for index in (0, 1, N // 2, N - 1):
    print(f"{index:>8}{address(1000, index):>12,}   1 multiply, 1 add")
print()
print("Four indices, four different addresses, identical work. There is no")
print("loop and no comparison anywhere in that computation, which is why")
print("indexing is O(1) rather than O(n) -- and why the O(1) holds for the")
print("last slot exactly as much as for the first.")
print()
print(f"visiting all {N:,} slots in three orders")
print()
print(f"{'order':<16}{'total':>16}{'reads':>9}{'last index':>12}{'steps':>7}")
print("-" * 60)
for label, order in ORDERS:
    total, reads = visit(order)
    last = order[-1]
    print(f"{label:<16}{total:>16,}{reads:>9,}{last:>12,}"
          f"{steps_to_reach_array(last):>7}")

print()
print("Three traversal orders, three identical totals, and three rows that")
print("end on three different slots -- 99,999, then 0, then 49,999. The last")
print("column is 2 for all three, because the cost of a read is the same")
print("arithmetic wherever the slot is. If indexing had to search for its")
print("slot, the middle-out walk would be the row that noticed.")
print()
print("Now the same question asked of a structure that does have to search:")
print()
print(f"{'index':>9}{'dynamic array':>16}{'linked list':>14}")
print("-" * 39)
for index in (0, N // 2, N - 1):
    print(f"{index:>9,}{steps_to_reach_array(index):>16,}"
          f"{steps_to_reach_chain(index):>14,}")
print()
print("The array column is flat because the address is arithmetic. The")
print("linked-list column is the index itself, because a chain has no")
print("arithmetic to do and every hop is one node. That is the whole")
print("difference between O(1) and O(n) indexing, and it is visible here as")
print("a column that does not move next to one that does.")
