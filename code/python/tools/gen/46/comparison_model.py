#!/usr/bin/env python3
"""Chapter 46 demo -- the bill a comparison sort has to pay.

`sorted` is C, so it cannot be instrumented. But every comparison it makes
goes through `<` on the objects it holds, so wrapping the values in a class
with a counting __lt__ turns the algorithm into a number. That number is a
property of the algorithm and the input, not of this machine.
"""
import math
import random


class Counted:
    """A value that reports how often it was compared."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value

    def __repr__(self):
        return f"Counted({self.value})"


def shuffled(n, seed=0):
    """A genuinely scrambled permutation. Note that a formula like
    `(i * k) % n` will not do: it produces an arithmetic progression, which
    contains long ascending runs for Timsort to find, and the counts come out
    flattering and wrong."""
    values = list(range(n))
    random.Random(seed).shuffle(values)
    return values


def count_sort(values):
    counter = [0]
    items = [Counted(v, counter) for v in values]
    result = sorted(items)
    return counter[0], result


def information_bound(n):
    """log2(n!) -- the number of yes/no answers needed to pin down which of
    the n! possible orders this input is in. Every comparison yields exactly
    one bit, so this is a floor on any comparison sort."""
    return sum(math.log2(k) for k in range(1, n + 1))


print("comparisons made by sorted() on a scrambled input")
print()
print(f"{'n':>9}{'comparisons':>14}{'log2(n!)':>14}{'ratio':>8}"
      f"{'per item':>10}{'log2 n':>8}")
print("-" * 64)
for n in (100, 1_000, 10_000, 100_000):
    comparisons, _ = count_sort(shuffled(n))
    bound = information_bound(n)
    print(f"{n:>9,}{comparisons:>14,}{bound:>14,.0f}"
          f"{comparisons / bound:>8.2f}{comparisons / n:>10.1f}{math.log2(n):>8.1f}")
print()
print("The ratio column is the one to read, and it is deliberately")
print("anticlimactic. As n grows by a factor of a thousand the comparisons")
print("grow by a factor of about two thousand nine hundred -- n log n, not")
print("n^2 -- and the ratio to the theoretical floor stays between 1.01 and")
print("1.02.")
print()
print("That floor is not a coincidence and it is not a property of Timsort.")
print("A comparison sort only ever learns about the input by asking 'is")
print("a < b?', and each answer splits the remaining possibilities in two.")
print("Telling apart the n! possible orderings therefore needs at least")
print("log2(n!) comparisons, and Stirling's approximation gives")
print("log2(n!) ~ n log2 n.")
print()
print("So no comparison sort beats this by more than a constant factor, and")
print("Timsort on scrambled data is already within two percent of the")
print("bound. There is nothing left to win in the algorithm. Everything")
print("interesting is in the constant -- and in the input, which is the")
print("subject of the next two demos.")
