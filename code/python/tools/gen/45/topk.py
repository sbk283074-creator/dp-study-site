#!/usr/bin/env python3
"""Chapter 45 demo -- one problem, three structures, counted.

'Find the ten most common words' is the smallest problem that needs two data
structures in sequence: a hash table to count, and something ordered to rank.
The counting is a dict; the ranking is the interesting choice.
"""
import heapq
import random
from collections import Counter

TOKENS = 200_000
VOCABULARY = 5_000
TOP = 10


class Counted:
    """A (count, word) pair that reports every comparison made against it."""

    __slots__ = ("count", "word", "counter")

    def __init__(self, count, word, counter):
        self.count = count
        self.word = word
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return (self.count, self.word) < (other.count, other.word)


def corpus():
    """A skewed vocabulary with no randomness in it: word w0000 is the most
    common, w4999 the rarest, and the token order is a fixed permutation."""
    rng = random.Random(0)
    words = [f"w{i:04d}" for i in range(VOCABULARY)]
    weights = [1.0 / (i + 1) for i in range(VOCABULARY)]
    return rng.choices(words, weights=weights, k=TOKENS)


def rank_by_sorting(pairs, counter):
    items = [Counted(count, word, counter) for word, count in pairs]
    ordered = sorted(items, reverse=True)
    return [(item.count, item.word) for item in ordered[:TOP]]


def rank_by_nlargest(pairs, counter):
    items = [Counted(count, word, counter) for word, count in pairs]
    best = heapq.nlargest(TOP, items)
    return [(item.count, item.word) for item in best]


def rank_by_hand(pairs, counter):
    """Keep a heap of the top ten as you go. Same complexity as nlargest,
    written out so the two comparisons per item are visible."""
    items = [Counted(count, word, counter) for word, count in pairs]
    heap = items[:TOP]
    heapq.heapify(heap)
    for item in items[TOP:]:
        if heap[0] < item:
            heapq.heapreplace(heap, item)
    return [(item.count, item.word) for item in sorted(heap, reverse=True)]


text = corpus()
counts = Counter(text)
pairs = list(counts.items())

print(f"{len(text):,} tokens, {len(counts):,} distinct words")
print()
print(f"{'counting':<34}{'steps':>14}")
print("-" * 48)
print(f"{'one dict lookup per token':<34}{len(text):>14,}")
print(f"{'distinct keys after counting':<34}{len(counts):>14,}")
print()
print("Counting is not the interesting part. A dict makes it one hash per")
print("token -- 200,000 steps for 200,000 tokens, and the distinct count")
print("does not change the per-token cost. Ranking is where the choice is.")
print()
print(f"now the top {TOP}, three ways")
print()
print(f"{'approach':<26}{'comparisons':>14}{'per word':>10}")
print("-" * 50)
results = {}
for label, fn in (("sorted() then slice", rank_by_sorting),
                  ("heapq.nlargest", rank_by_nlargest),
                  ("heap of 10, hand-rolled", rank_by_hand)):
    counter = [0]
    results[label] = fn(pairs, counter)
    print(f"{label:<26}{counter[0]:>14,}{counter[0] / len(pairs):>10.1f}")
print()
print("All three return the same answer:", len(set(map(tuple, results.values()))) == 1)
print()
print("the answer")
print("-" * 50)
for count, word in results["heapq.nlargest"]:
    print(f"  {word}  appeared {count:,} times")
print()
print("Sorting compares every word against its neighbours, about eleven")
print("times each, because it is answering a question nobody asked: the")
print("full order of 5,000 words. The heap answers only the question that")
print("was asked -- which ten are largest -- in one comparison per word,")
print("because the heap is never bigger than ten and almost every word")
print("loses to the smallest member on the first try. That is a factor of")
print("ten, for the same answer, from a different structure.")
print()
print("That is the whole chapter in one table. The data structure is not a")
print("container you pick by habit; it is the shape of the question you are")
print("asking, and picking the wrong one means paying for answers you threw")
print("away. Chapter 44 called this the cost model. This is it, applied.")
