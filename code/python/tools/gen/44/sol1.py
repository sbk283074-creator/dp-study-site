#!/usr/bin/env python3
"""Chapter 44 solution 1 -- count the comparisons for a maximum."""


def largest(xs):
    """Return (value, comparisons) for the largest element."""
    best = xs[0]
    comparisons = 0
    for x in xs[1:]:
        comparisons += 1
        if x > best:
            best = x
    return best, comparisons


print(f"{'n':>6}  {'largest':>8}  {'comparisons':>12}  {'n - 1':>6}")
print("-" * 38)
for n in (10, 100, 1_000, 10_000):
    value, comparisons = largest(list(range(n)))
    print(f"{n:>6}  {value:>8}  {comparisons:>12}  {n - 1:>6}")

print()
print("The comparison count is exactly n - 1 at every size, so this")
print("function is Theta(n) with no case to argue about.")
print()
print("That is worth contrasting with find() from earlier in the chapter,")
print("where the answer depended on where the target was. A search can")
print("stop early; a maximum cannot. To know that nothing is bigger than")
print("what you are holding, you have to have looked at everything else.")
print("So the best case and the worst case here are the same, and the")
print("bound is tight in both directions -- which is what Theta means.")
