#!/usr/bin/env python3
"""Chapter 44 solution 5 -- count the copies that make append amortised O(1).

`append` is O(1) *amortised*, and that word is doing real work: most appends
write into a slot that already exists, and occasionally one finds the array
full and reallocates, copying everything. This program counts the copies by
watching the list's own reported size change -- so the count is of what the
interpreter really did, not of a model of what it should have done.
"""
import sys


def build(n):
    """Append n items; return the reallocations and the elements copied."""
    items = []
    copies = 0
    reallocations = 0
    size = sys.getsizeof(items)
    for i in range(n):
        items.append(i)
        grown = sys.getsizeof(items)
        if grown != size:
            copies += len(items) - 1     # everything already there was copied
            reallocations += 1
            size = grown
    return copies, reallocations


SIZES = (10_000, 20_000, 40_000, 80_000, 160_000, 320_000)

print("what one append costs, as the list gets longer")
print()
print(f"{'n':>9}{'reallocations':>15}{'elements copied':>17}{'copies per append':>19}")
print("-" * 60)
per_append = []
for n in SIZES:
    copies, reallocations = build(n)
    per_append.append(copies / n)
    print(f"{n:>9,}{reallocations:>15,}{copies:>17,}{copies / n:>19.2f}")

print()
print(f"The last column is the one to read, and it does not grow. It wobbles")
print(f"between {min(per_append):.2f} and {max(per_append):.2f} and has no trend: multiplying the")
print("length of the list by thirty-two leaves the copies per append where")
print("it found them. The total number of copies grows in proportion to n,")
print("which means the average append copies a constant number of elements")
print("-- and that is what amortised O(1) means.")
print()
print("The reallocation column is the reason the claim is easy to doubt.")
print("Look at how few reallocations there are: the array does not grow by")
print("one slot at a time, it overshoots, and the overshoot is what buys the")
print("amortised constant. A policy that grew by one slot per append would")
print("copy n(n-1)/2 elements over n appends -- quadratic, and the copies")
print("per append would double every time n did.")
print()
print("That is also why measuring one append proves nothing. Some appends")
print("cost nothing at all and a handful cost O(n). If you timed a single")
print("append you might catch a reallocation and conclude that append is")
print("O(n) -- which would be a true statement about that one append and a")
print("useless statement about the loop.")
print()
print("So the measurement has to match the claim. The claim is about a")
print("sequence of n appends, so the measurement is the total for n appends")
print("divided by n. If you ever find yourself measuring one operation to")
print("test a claim about a sequence, that mismatch is the bug -- not the")
print("result.")
