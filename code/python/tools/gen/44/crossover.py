#!/usr/bin/env python3
"""Chapter 44 demo 14 -- where two algorithms cross over."""
import heapq
import random
import timeit

N = 100_000
RND = random.Random(7)
DATA = [RND.random() for _ in range(N)]


def per_call(stmt, number, globs):
    """timeit hands back the total for `number` runs. Divide it out."""
    return min(timeit.repeat(stmt, number=number, repeat=5, globals=globs)) / number


def verdict(ratio):
    """ratio is nsmallest / sorted, so below 1 means the heap wins."""
    if ratio < 0.3:
        return "much faster"
    if ratio < 1.0:
        return "faster"
    return "slower"


print(f"take the k smallest of {N:,} numbers")
print()
print("  heapq.nsmallest(k, xs)   keeps a heap of size k  ->  O(n log k)")
print("  sorted(xs)[:k]           sorts everything        ->  O(n log n)")
print()
print(f"{'k':>8}  {'k / n':>8}  {'nsmallest':>14}  {'winner':>10}")
print("-" * 46)
for k in (1, 100, 1_000, 5_000, 10_000, 50_000):
    g = {"xs": DATA, "k": k, "heapq": heapq}
    t_heap = per_call("heapq.nsmallest(k, xs)", 3, g)
    t_sort = per_call("sorted(xs)[:k]", 3, g)
    ratio = t_heap / t_sort
    winner = "nsmallest" if ratio < 1.0 else "sorted"
    print(f"{k:>8}  {k / N:>8.2f}  {verdict(ratio):>14}  {winner:>10}")

print()
print("Both functions return exactly the same list. The only question is")
print("which one you are paying for.")
print()
print("When k is tiny the heap wins by a wide margin. It touches each")
print("element once and only keeps k of them, so its cost is governed by")
print("log k. Sorting has to look at every element and rearrange all of")
print("them, which costs log n per element -- and log n is what it is no")
print("matter how small k gets.")
print()
print("As k grows towards n, log k approaches log n and the growth rates")
print("stop being different. At that point the winner is decided by the")
print("constant factors: sorted is C code running over one contiguous")
print("array, while the heap is a Python loop doing one comparison at a")
print("time. That is why the crossover lands between k = 5000 and")
print("k = 10000 here -- a tenth of the input -- rather than at k = n,")
print("which is where the complexity analysis alone would put it.")
print()
print("So there are two facts and you need both. The growth rate tells you")
print("which way the gap is heading. The constant factor tells you where it")
print("currently is. A table like this one is what you get when you insist")
print("on both instead of arguing about either.")
