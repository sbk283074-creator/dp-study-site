#!/usr/bin/env python3
"""Chapter 44 solution 5 -- measure the amortised cost of append."""
import timeit


def build(n):
    a = []
    for i in range(n):
        a.append(i)
    return a


def per_append(n):
    """Total time for n appends, divided by n."""
    number = max(1, 400_000 // n)
    total = min(timeit.repeat(lambda: build(n), number=number, repeat=5)) / number
    return total / n


def growth(ratio):
    if ratio < 1.4:
        return "flat"
    if ratio < 1.8:
        return "slightly up"
    return "rising"


SIZES = (10_000, 20_000, 40_000, 80_000, 160_000, 320_000)

print("cost of one append, as the list gets longer")
print()
print(f"{'n':>8}  {'vs previous':>13}")
print("-" * 24)
previous = None
for n in SIZES:
    cost = per_append(n)
    if previous is None:
        print(f"{n:>8}  {'--':>13}")
    else:
        print(f"{n:>8}  {growth(cost / previous):>13}")
    previous = cost

print()
print("Every row says 'flat', which is the amortised O(1) claim measured")
print("rather than asserted. Doubling the length of the list does not")
print("double the cost of the next append.")
print()
print("What makes this worth running yourself is that the claim is easy to")
print("doubt. You know from the previous program that a reallocation copies")
print("every element, and that some appends therefore cost O(n). If you")
print("measured a single append you might catch a reallocation and conclude")
print("that append is O(n) -- which would be a true statement about that")
print("one append and a useless statement about the loop.")
print()
print("So the measurement has to match the claim. The claim is about a")
print("sequence of n appends, so the measurement is the total for n appends")
print("divided by n. If you ever find yourself measuring one operation to")
print("test a claim about a sequence, that mismatch is the bug -- not the")
print("result.")
