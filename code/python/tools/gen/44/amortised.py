#!/usr/bin/env python3
"""Chapter 44 demo 9 -- the amortised argument, counted."""


def cpython_growth(size):
    """CPython's list_resize growth rule: overshoot by about an eighth."""
    newsize = size + 1
    return (newsize + (newsize >> 3) + 6) & ~3


def doubling_growth(size):
    """The other classic policy: double the array when it fills up."""
    return max(4, size * 2)


def copies_for(n, growth):
    """Total element copies performed while appending n items to an empty
    list. A reallocation copies every element the list already holds."""
    total = 0
    capacity = 0
    size = 0
    for _ in range(n):
        if size == capacity:
            total += size                 # every existing element moves
            capacity = growth(capacity)
        size += 1
    return total


print("what does appending n items to an empty list really cost?")
print()
print(f"{'n':>9}  {'CPython':>10}  {'copies/n':>9}  {'doubling':>10}  {'copies/n':>9}")
print("-" * 54)
for n in (1_000, 10_000, 100_000, 1_000_000):
    c = copies_for(n, cpython_growth)
    d = copies_for(n, doubling_growth)
    print(f"{n:>9}  {c:>10}  {c / n:>9.2f}  {d:>10}  {d / n:>9.2f}")

print()
print("Both columns grow in step with n, so the total work for n appends is")
print("proportional to n either way. That is the amortised argument: divide")
print("the total by n and you get a constant, so a single append is O(1) on")
print("average -- even though the append that triggers a reallocation is")
print("O(n) all by itself.")
print()
print("The two policies differ in the size of that constant, and the reason")
print("is worth working out. CPython overshoots by an eighth, so each")
print("reallocation is 9/8 of the last and the copies form a geometric series")
print("with ratio 8/9, which sums to at most 9 times the final size. Doubling")
print("has a ratio of 1/2, which sums to at most 2. So the CPython column")
print("sits near 8 or 9 and the doubling column sits between 1 and 2 -- a")
print("factor of about five in copying, in the doubling policy's favour.")
print()
print("It pays for that in memory. A doubling list is, at worst, twice as long")
print("as it needs to be; CPython's is at worst an eighth too long. The")
print("interpreter chose to spend memory to save copying, and it made the")
print("same trade-off for dicts and for bytearray. When you write a growable")
print("container of your own, that is the decision in front of you.")
