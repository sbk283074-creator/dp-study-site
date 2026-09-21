#!/usr/bin/env python3
"""Chapter 48, exercise 4 -- one loop swap, two different problems.

Counting the ways to make change and finding the fewest coins to make change
are the same state, the same array, and almost the same loop. One of them
cares about the order of the two loops and the other does not, and the
difference is not a detail you can reason your way to from the code -- it is
a statement about what the state means.

This is the exercise where the counting version and the optimising version
have to be written down next to each other, because the trap is invisible
when you only ever see one of them.
"""
import bisect


def count_by_coin_outer(coins, target):
    """Coins in the outer loop, amounts ascending.

    Each coin is introduced exactly once, and when it is introduced it may
    extend any amount that was already reachable using only the coins before
    it. So a multiset of coins is counted once, however it is ordered.
    """
    ways = [0] * (target + 1)
    ways[0] = 1
    for coin in coins:
        for amount in range(coin, target + 1):
            ways[amount] += ways[amount - coin]
    return ways


def count_by_amount_outer(coins, target):
    """Amounts in the outer loop, coins inner.

    Identical array, identical recurrence, two loops swapped -- and it counts
    ordered sequences instead of multisets. The reason is that `ways[amount]`
    is now assembled by asking 'what was the last coin', so 2+1+1 and 1+2+1
    are counted as different answers.
    """
    ways = [0] * (target + 1)
    ways[0] = 1
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount:
                ways[amount] += ways[amount - coin]
    return ways


def fewest_amount_outer(coins, target):
    """The minimising version, amounts outer."""
    best = [0] + [target + 1] * target
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount and best[amount - coin] + 1 < best[amount]:
                best[amount] = best[amount - coin] + 1
    return best


def fewest_coin_outer(coins, target):
    """The minimising version, coins outer. Same array, swapped loops."""
    best = [0] + [target + 1] * target
    for coin in coins:
        for amount in range(coin, target + 1):
            if best[amount - coin] + 1 < best[amount]:
                best[amount] = best[amount - coin] + 1
    return best


COINS = (1, 2, 5)
TARGET = 12

print("Part 1 -- the same array, two loop orders, two questions")
print()
print(f"  coins {COINS}, target {TARGET}")
print()
by_coin = count_by_coin_outer(COINS, TARGET)
by_amount = count_by_amount_outer(COINS, TARGET)
print(f"{'amount':>8}{'multisets':>12}{'ordered':>12}{'ratio':>10}")
print("-" * 42)
for amount in range(1, TARGET + 1):
    ratio = (f"{by_amount[amount] / by_coin[amount]:.1f}x"
             if by_coin[amount] else "-")
    print(f"{amount:>8}{by_coin[amount]:>12,}{by_amount[amount]:>12,}"
          f"{ratio:>10}")
print()
print("Both columns are correct answers to a question, and they are not the")
print("same question. 'In how many ways can you make 12p' has two readings --")
print("as a multiset of coins, or as a sequence of coins handed over one at a")
print("time -- and the two loops answer one each.")
print()
print(f"  at {TARGET}p the gap is {by_amount[TARGET] / by_coin[TARGET]:.0f}x, and it widens with the target,")
print("  because the number of orderings of a set grows faster than the")
print("  number of sets.")
print()
print()
print("Part 2 -- the swap that does not matter")
print()
fewest_a = fewest_amount_outer(COINS, 40)
fewest_c = fewest_coin_outer(COINS, 40)
print(f"  {'amount':>8}{'amounts outer':>15}{'coins outer':>14}{'agree':>8}")
print("-" * 45)
for amount in (1, 5, 7, 11, 23, 39, 40):
    print(f"{amount:>8}{fewest_a[amount]:>15}{fewest_c[amount]:>14}"
          f"{str(fewest_a[amount] == fewest_c[amount]):>8}")
print()
print(f"  all 40 amounts agree : "
      f"{all(fewest_a[a] == fewest_c[a] for a in range(1, 41))}")
print()
print("So the swap that changes the *count* by a factor of")
print(f"{by_amount[TARGET] / by_coin[TARGET]:.0f} at {TARGET}p does nothing at all to the *minimum*. The factor is")
print("not a constant either -- it grows without bound as the target grows,")
print("because the number of orderings of a multiset grows faster than the")
print("number of multisets. That is not luck, and it is worth having an")
print("explanation for.")
print()
print("Counting is order-sensitive because the loop order decides what the")
print("state means: with coins outer, `ways[amount]` is 'the number of")
print("multisets using coins considered so far', and with amounts outer it is")
print("'the number of sequences ending here'. Both are coherent, and they")
print("count different things.")
print()
print("Minimising is order-insensitive because the state does not need to")
print("mean anything in particular. `best[amount]` is the same number however")
print("you got there, and the relaxation `best[a] = min(best[a], best[a-c]+1)`")
print("is a shortest-path update: run it in any order and the same fixed")
print("point is reached, because the values only ever go down.")
print()
print("That is the test worth carrying away. If a DP state is *counting*")
print("something, the loop order is part of the specification. If it is")
print("*optimising* something, the loop order is an implementation detail.")
print()
print()
print("Part 3 -- the check that the two counts are related")
print()


def ordered_from_multisets(coins, target):
    """The number of ordered sequences, computed the long way: sum over every
    multiset of the number of distinct orderings. If the two loop orders
    disagree, this is the bridge between them."""
    total = 0

    def walk(remaining, index):
        nonlocal total
        if remaining == 0:
            counts = {}
            for coin in stack:
                counts[coin] = counts.get(coin, 0) + 1
            orderings = 1
            used = 0
            for count in sorted(counts.values(), reverse=True):
                used += count
                orderings = orderings * comb(used, count)
            total += orderings
            return
        if index >= len(coins):
            return
        coin = coins[index]
        for take in range(remaining // coin + 1):
            stack.extend([coin] * take)
            walk(remaining - take * coin, index + 1)
            if take:
                del stack[-take:]

    stack = []
    walk(target, 0)
    return total


from math import comb

print(f"  {'multisets for ' + str(TARGET) + 'p, coin-outer loop':<44}: "
      f"{by_coin[TARGET]}")
print(f"  {'ordered sequences, amount-outer loop':<44}: {by_amount[TARGET]}")
print(f"  {'ordered sequences, expanding every multiset':<44}: "
      f"{ordered_from_multisets(COINS, TARGET)}")
print(f"  {'the two agree':<44}: "
      f"{ordered_from_multisets(COINS, TARGET) == by_amount[TARGET]}")
print()
print("The third line is the bridge. It takes every multiset of coins that")
print("sums to the target, counts the distinct orderings of each one, and adds")
print("them up -- which is what 'ordered sequences' means, defined without any")
print("reference to a DP.")
print()
print("It agrees with the amount-outer loop, and that agreement is the proof")
print("that the two loop orders are not a bug in one of them. They are two")
print("different state definitions that happen to share an array.")
