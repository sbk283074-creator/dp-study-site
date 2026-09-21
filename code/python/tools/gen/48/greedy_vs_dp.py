#!/usr/bin/env python3
"""Chapter 48 demo -- the exchange argument, and what happens without one.

A greedy algorithm is correct when you can prove that taking the locally best
option can never be a mistake -- an *exchange argument*. Coin change is the
cleanest place to see both halves: for some coin systems the argument goes
through and greedy is optimal, and for others it does not and greedy is
simply wrong.

The section ends somewhere unexpected. Coin change turns out to be a shortest
path problem wearing different clothes, which connects this chapter back to
the previous one.
"""
import collections


def fewest_dp(coins, target):
    """The DP. One dimension, not two -- the state is just the amount left.

    The recurrence reads `1 + the best answer for a smaller amount`, which is
    a strange way to describe coin change until you notice that 'a smaller
    amount' is exactly what a shortest-path relaxation looks like.
    """
    INF = target + 1
    best = [0] + [INF] * target
    for amount in range(1, target + 1):
        for coin in coins:
            if coin <= amount and best[amount - coin] + 1 < best[amount]:
                best[amount] = best[amount - coin] + 1
    return best


def fewest_greedy(coins, target):
    """Largest coin first, every time. Returns the coins used, or None if the
    system cannot make the amount at all."""
    used = []
    for coin in sorted(coins, reverse=True):
        while target >= coin:
            target -= coin
            used.append(coin)
    return used if target == 0 else None


print("Part 1 -- the counterexample, and it is three coins long")
print()
COINS = (1, 3, 4)
TARGET = 6
SWEEP = 60
greedy_used = fewest_greedy(COINS, TARGET)
best = fewest_dp(COINS, SWEEP)
print(f"  coins {COINS}, target {TARGET}")
print()
print(f"  greedy (largest first) : {'+'.join(map(str, greedy_used))} = "
      f"{len(greedy_used)} coins")
print(f"  optimal                : 3+3 = {best[TARGET]} coins")
print()
print("Four is the largest coin that fits, so the greedy takes it and is left")
print("with 2 -- which needs two more coins. The optimal answer never touches")
print("4 and uses two 3s. There is no tie-breaking rule that saves this: the")
print("greedy is not unlucky, it is choosing a coin that no optimal solution")
print("contains.")
print()
print()
print("Part 2 -- how often it is wrong")
print()
print(f"  coins {COINS}, sweeping every target up to {SWEEP}")
print()
print(f"{'target':>8}{'greedy':>9}{'optimal':>10}{'verdict':>12}")
print("-" * 39)
wrong = []
for amount in range(1, SWEEP + 1):
    used = fewest_greedy(COINS, amount)
    greedy_count = len(used) if used else None
    optimal = best[amount]
    if greedy_count != optimal:
        wrong.append(amount)
        if len(wrong) <= 6:
            print(f"{amount:>8}{greedy_count:>9}{optimal:>10}"
                  f"{'WRONG':>12}")
print(f"  ... {len(wrong)} of {SWEEP} targets wrong: {wrong[:12]}")
print()
print("Two things are worth reading off that list. The first is the rate:")
print(f"{len(wrong)} of {SWEEP} targets, so the greedy is right "
      f"{100 * (SWEEP - len(wrong)) / SWEEP:.0f}% of the time. A")
print("heuristic that is wrong nearly a quarter of the time is worse than")
print("useless in a payment system, and it is dangerous precisely because it")
print("is right most of the time -- a test with a handful of amounts in it")
print("will pass.")
print()
print("The second is the pattern, which is exact rather than approximate.")
print(f"Every wrong target is 4k + 2 for some k: {wrong[:6]}, and so on.")
print("The reason is that 4k + 2 = 4(k-1) + 6, and 6 is two 3s -- so the")
print("optimal answer is k-1 fours and two threes, which is k+1 coins,")
print("while the greedy takes k fours and two 1s, which is k+2. The greedy")
print("is not occasionally unlucky. It is systematically one coin worse on")
print("an infinite family of inputs.")
print()
print()
print("Part 3 -- the same algorithm, on a system where it is provably correct")
print()
print("A coin system is called *canonical* when greedy is optimal for it. The")
print("usual decimal systems are canonical, and the reason is an exchange")
print("argument rather than a proof by exhaustion. A sufficient condition is")
print("that every coin is worth at least twice the one below it, and here is")
print("the shape of the argument:")
print()
print("  take the largest coin c that fits in the amount. Any solution that")
print("  avoids c has to make up at least c from smaller coins, and since the")
print("  next coin down is worth at most c/2, that takes at least two coins.")
print("  Swapping those two for a single c cannot make the count worse, so no")
print("  optimal solution avoids c. Repeat on the remainder.")
print()
print("That argument is why the property has to be checked rather than")
print("assumed. It holds for the decimal system and it fails for {1, 3, 4},")
print("where 4 is less than twice 3 -- so the next coin down is worth *more*")
print("than half of c, one of them can substitute for c, and the swap the")
print("argument depends on does not exist.")
print()
CANONICAL = (1, 2, 5, 10, 20, 50, 100, 200)
canonical_best = fewest_dp(CANONICAL, 400)
canonical_wrong = []
for amount in range(1, 401):
    used = fewest_greedy(CANONICAL, amount)
    if used is None or len(used) != canonical_best[amount]:
        canonical_wrong.append(amount)
print(f"  coins {CANONICAL}")
print(f"  targets 1..400, disagreements with the DP : {len(canonical_wrong)}")
print()
print("Zero disagreements over four hundred targets. That is evidence, not a")
print("proof -- but combined with the exchange argument above it is the")
print("reason the coin change problem you meet in a shop is solved greedily")
print("and the one you meet in an interview is solved with a table.")
print()
print()
print("Part 4 -- where this connects to the previous chapter")
print()
print("The DP above has a one-dimensional state and a recurrence of the form")
print("'best[a] = 1 + min(best[a - c])'. That is not obviously a graph")
print("problem. Write it as one and it becomes obvious.")
print()


def fewest_bfs(coins, target):
    """Amounts are nodes. A coin is an edge from a to a + coin. Then the
    fewest coins to reach `target` is the fewest edges -- a breadth-first
    search, exactly as in the graphs chapter."""
    distance = {0: 0}
    queue = collections.deque([0])
    while queue:
        amount = queue.popleft()
        for coin in coins:
            nxt = amount + coin
            if nxt <= target and nxt not in distance:
                distance[nxt] = distance[amount] + 1
                queue.append(nxt)
    return distance


bfs = fewest_bfs(COINS, 60)
dp = fewest_dp(COINS, 60)
print(f"  {'amount':>8}{'DP':>8}{'BFS':>8}{'agree':>8}")
print("-" * 32)
for amount in (1, 3, 4, 6, 12, 30, 59, 60):
    print(f"{amount:>8}{dp[amount]:>8}{bfs[amount]:>8}"
          f"{str(dp[amount] == bfs[amount]):>8}")
print()
print(f"  all 60 amounts agree : "
      f"{all(dp[a] == bfs[a] for a in range(1, 61))}")
print()
print("The two are the same algorithm. Dijkstra's algorithm is the DP for a")
print("weighted graph; this is the unweighted case, so BFS is enough, and")
print("the 'table' is just the array of distances. The relaxation step")
print("`best[a] = 1 + best[a - coin]` is a graph edge relaxation with a")
print("weight of 1.")
print()
print("That is worth noticing because it is a general pattern rather than a")
print("coincidence. A DP is a shortest path through its own state space, and")
print("the state space is a graph whether or not you draw it. The previous")
print("chapter's algorithms are the special case where you can write the")
print("edges down explicitly; this chapter's are the case where the edges")
print("are implied by the recurrence and you enumerate them on the fly.")
print()
print("It also explains the direction of the loops, which was the whole")
print("difference between 0/1 and unbounded knapsack. In a graph where a")
print("coin edge goes from a to a + coin, walking the amounts *forwards*")
print("means each edge can be traversed again from its own endpoint -- which")
print("is exactly what 'unbounded' means. Walking backwards visits each edge")
print("once. Same graph, two different questions.")
