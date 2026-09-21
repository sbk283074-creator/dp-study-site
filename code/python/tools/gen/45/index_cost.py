#!/usr/bin/env python3
"""Chapter 45 demo -- reading a slot is arithmetic, not a search."""
import timeit

N = 100_000
ROUNDS = 7
ITEMS = list(range(N))

# The three index orders are built up front so that each timed loop does
# exactly the same per-iteration work. If one loop computed its index with
# a subtraction or a modulo and another did not, the difference in the
# table would be the arithmetic, not the memory access.
FORWARD = list(range(N))
BACKWARD = list(range(N - 1, -1, -1))
MIDDLE_OUT = [(N // 2 + offset) % N for offset in range(N)]


def address(base, index, width=8):
    """What a dynamic array does for lst[i]: one multiply, one add.
    The index never appears in a loop, so it never appears in the cost."""
    return base + index * width


def visit(order):
    total = 0
    for i in order:
        total += ITEMS[i]
    return total


def time_one(order):
    return min(timeit.repeat(lambda: visit(order), number=1, repeat=ROUNDS))


print("the slot address a dynamic array computes for each index")
print("  base = 1000 (pretend), 8 bytes per slot")
print()
print(f"{'index':>8}{'address':>12}   work done")
print("-" * 44)
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
print(f"{'order':<14}{'total':>16}  {'measured':>10}")
print("-" * 42)
print(f"{'front to back':<14}{visit(FORWARD):>16,}  {'baseline':>10}")
for label, order in (("back to front", BACKWARD), ("middle out", MIDDLE_OUT)):
    ratio = time_one(order) / time_one(FORWARD)
    verdict = "same band" if 0.7 < ratio < 1.4 else f"{ratio:.1f}x"
    print(f"{label:<14}{visit(order):>16,}  {verdict:>10}")
print()
print("Three traversal orders, three identical totals, one band. If")
print("indexing had to search for its slot, the middle-out walk would be")
print("the one that noticed -- and the total would still be the same, so")
print("it is the band that rules a search out and the arithmetic above")
print("that explains why there is nothing to search for.")
print()
print("Contrast that with the linked list, where the same three reads cost")
print("0, n/2 and n steps.")
