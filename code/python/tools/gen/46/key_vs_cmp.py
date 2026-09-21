#!/usr/bin/env python3
"""Chapter 46 demo -- how often each of the two sorting interfaces runs your code.

`sorted(x, key=f)` and `sorted(x, key=cmp_to_key(g))` look like two spellings
of the same request. They are not: one calls your function once per item and
the other calls it once per comparison, and the difference is a factor of
log n on every sort you write.
"""
import functools
import math
import random

N = 2_000

KEY_CALLS = [0]
CMP_CALLS = [0]


def records(n):
    rng = random.Random(0)
    return [(f"row{i:05d}", rng.randrange(1_000)) for i in range(n)]


ROWS = records(N)


def by_score(record):
    KEY_CALLS[0] += 1
    return record[1]


def compare_score(left, right):
    CMP_CALLS[0] += 1
    if left[1] != right[1]:
        return -1 if left[1] < right[1] else 1
    return -1 if left[0] < right[0] else (1 if left[0] > right[0] else 0)


print(f"sorting {N:,} rows by score, two ways")
print()
print(f"{'interface':<34}{'your function is called':>26}")
print("-" * 60)
KEY_CALLS[0] = 0
by_key = sorted(ROWS, key=by_score)
key_calls = KEY_CALLS[0]
print(f"{'key=by_score':<34}{key_calls:>26,}")
CMP_CALLS[0] = 0
by_cmp = sorted(ROWS, key=functools.cmp_to_key(compare_score))
cmp_calls = CMP_CALLS[0]
print(f"{'key=cmp_to_key(compare_score)':<34}{cmp_calls:>26,}")
print(f"{'ratio':<34}{cmp_calls / key_calls:>26.1f}")
print()
print(f"{'same answer either way':<34}{str(by_key == by_cmp):>26}")
print(f"{'log2(n) for reference':<34}{math.log2(N):>26.1f}")
print()
print("The key function runs exactly n times, and the comparator runs about")
print("ten times as often -- which is the log n factor, with Timsort's own")
print("constant folded in.")
print()
print("That is not a micro-optimisation. A key function is called once per")
print("item no matter how the sort goes, because Python applies it first and")
print("then sorts the *keys*. That is the decorate-sort-undecorate pattern")
print("from the old days, built into the interface: for an expensive key,")
print("the difference between n and n log n calls is the difference between")
print("a report that takes a second and one that takes a minute.")
print()
print("So the rule is: reach for a key. It is called less often, it is")
print("easier to read, and it cannot introduce an inconsistent comparator.")
print()
print("But a key is not always available, and that is what cmp_to_key is")
print("for. A key must map each item to something independently -- the")
print("comparison is then just '<' on the keys. When the right order")
print("depends on the *pair*, no such mapping exists:")
print()
NUMBERS = [10, 2, 30, 5, 9, 100, 1]
print(f"  numbers: {NUMBERS}")
print("  task: arrange them so the concatenation is the largest number")
print(f"  a key would need: 'is 10 before 2?' -- and the answer depends on")
print("  the other item, not on the item alone.")
print()


def largest_first(left, right):
    """Compare the two possible concatenations. There is no key that does
    this, because 'a before b' depends on b."""
    if left + right > right + left:
        return -1
    if left + right < right + left:
        return 1
    return 0


texts = [str(n) for n in NUMBERS]
arranged = sorted(texts, key=functools.cmp_to_key(largest_first))
by_value = sorted(texts, key=int, reverse=True)
print(f"  cmp_to_key result : {arranged}")
print(f"  concatenated      : {''.join(arranged)}")
print(f"  sorted as integers: {by_value}")
print(f"  concatenated      : {''.join(by_value)}")
print(f"  the comparator wins: {int(''.join(arranged)) > int(''.join(by_value))}")
print()
print("The comparison is 'does a+b beat b+a', and that is not a property of")
print("a alone, so no key can express it. Sorting by numeric value gives a")
print("different and smaller concatenation. That is the case cmp_to_key")
print("exists for, and it is rare enough that reaching for it should be a")
print("deliberate decision rather than the default.")
