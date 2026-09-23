"""Solution 3 -- the largest TTL that meets a staleness budget.

A source that changes on a schedule, a budget of how many stale reads out
of a thousand are allowed, and a sweep over the TTL. The sweep is the
answer, and the reason it cannot be reasoned about is in the table.
"""

TICKS = 1110
CHANGE_EVERY = 37
BUDGET = 100
TTLS = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 35]


def source_value(tick):
    return tick // CHANGE_EVERY


def run(ttl):
    count = {"loads": 0, "stale": 0, "worst": 0}
    cached = None
    cached_at = 0
    for tick in range(TICKS):
        if cached is None or tick - cached_at >= ttl:
            cached = source_value(tick)
            cached_at = tick
            count["loads"] += 1
        if cached != source_value(tick):
            count["stale"] += 1
            count["worst"] = max(count["worst"], tick - cached_at)
    return count


def main():
    print(f"  ticks                               {TICKS}")
    print(f"  the source changes every            {CHANGE_EVERY}")
    print(f"  stale reads allowed                 {BUDGET}")
    print()
    print("    ttl      loads   stale reads   worst staleness   within budget")
    results = {}
    for ttl in TTLS:
        count = run(ttl)
        results[ttl] = count
        ok = "yes" if count["stale"] <= BUDGET else "no"
        print("    {:<9}{:>5}{:>14}{:>18}   {}".format(
            ttl, count["loads"], count["stale"], count["worst"], ok))
    print()

    passing = [ttl for ttl in TTLS if results[ttl]["stale"] <= BUDGET]
    best = max(passing)
    over = [ttl for ttl in TTLS if results[ttl]["stale"] > BUDGET]
    print(f"  the sweep is the answer to the question a staleness budget")
    print(f"  actually asks, which is not `what TTL should I use` but `how large")
    print(f"  can the TTL be and still meet the budget`.")
    print()
    print(f"  the largest TTL that stays within {BUDGET} stale reads is {best}, at")
    print(f"  {results[best]['stale']} stale reads and {results[best]['loads']} loads. Every larger value in the sweep")
    print(f"  is over budget, and the count of stale reads rises with the TTL")
    print(f"  throughout.")
    print()
    print(f"  the sweep is monotone here, and the reason it is monotone is that")
    print(f"  no TTL in the list divides the change period of {CHANGE_EVERY}. That is not")
    print(f"  a property of the method; it is a property of the numbers that were")
    print(f"  chosen. A TTL that divides the change period gives zero stale reads")
    print(f"  however large it is, because every expiry lands exactly on a change")
    print(f"  and the cache never serves a value the source has moved past.")
    print()
    print(f"  so a sweep of the TTLs that look reasonable is not enough. The")
    print(f"  values to test are the ones that fall against the change period, and")
    print(f"  the two to test first are a TTL just under the period and a TTL that")
    print(f"  divides it exactly.")
    print()
    print(f"  the worst staleness column tells the other half of the story. It is")
    print(f"  {results[best]['worst']} ticks at a TTL of {best}, which is one tick below the TTL, and it")
    print(f"  rises with the TTL rather than with the count of stale reads. A")
    print(f"  reader who set the TTL from the staleness bound alone would pick")
    print(f"  {CHANGE_EVERY - 1}, and would get {run(CHANGE_EVERY - 1)['stale']} stale reads against a budget of {BUDGET}.")
    print()
    print(f"  the bound is the number a cache can reason about on its own and the")
    print(f"  count of bad reads is the number a user experiences. They are not")
    print(f"  the same number, and only one of them can be computed without")
    print(f"  knowing how often the source changes.")


main()
