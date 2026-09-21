#!/usr/bin/env python3
"""Chapter 48 demo -- knapsack, and the one word that qualifies every
complexity claim in this chapter.

Knapsack is the DP that turns up most often in practice, because 'pick the
best subset under a budget' is what most resource decisions actually are. It
is also where the phrase 'polynomial time' stops meaning what it looks like,
and the table at the end is the reason.

Everything here is counted: values, capacities and table cells. No timings.
"""

ITEMS = [
    ("map", 9, 150), ("compass", 13, 35), ("water", 153, 200),
    ("sandwich", 50, 160), ("glucose", 15, 60), ("banana", 27, 60),
    ("suntan", 11, 70), ("camera", 32, 30), ("note-case", 22, 80),
    ("socks", 4, 50), ("book", 30, 10), ("sunglasses", 6, 20),
]
CAPACITY = 200


def knapsack_table(items, capacity):
    """table[i][w] = the best value obtainable from the first i items with a
    budget of w.

    Two dimensions, and the second one is the surprise: the state includes
    the budget, so the size of the table depends on a *number* rather than on
    how many things there are.
    """
    n = len(items)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        name, weight, value = items[i - 1]
        for w in range(capacity + 1):
            skip = table[i - 1][w]
            if weight > w:
                table[i][w] = skip
            else:
                take = table[i - 1][w - weight] + value
                table[i][w] = max(skip, take)
    return table


def knapsack_pick(items, capacity, table):
    """Walk back to find which items were taken. The table stores values, so
    the decision has to be re-derived -- same as the edit-distance traceback."""
    w = capacity
    taken = []
    for i in range(len(items), 0, -1):
        if table[i][w] != table[i - 1][w]:
            name, weight, value = items[i - 1]
            taken.append((name, weight, value))
            w -= weight
    return list(reversed(taken))


print("Part 1 -- the greedy that looks right and is not")
print()
print("Packing a rucksack by 'take the item with the best value per unit of")
print("weight first' is the natural idea, and it is wrong. Here is the")
print("smallest case that shows it:")
print()
TOY = [("A", 6, 30), ("B", 5, 24), ("C", 5, 24)]
print(f"  capacity 10, three items:")
for name, weight, value in TOY:
    print(f"    {name}  weight {weight}  value {value}  "
          f"ratio {value / weight:.1f}")
print()
by_ratio = sorted(TOY, key=lambda item: item[2] / item[1], reverse=True)
room, greedy_value, greedy_took = 10, 0, []
for name, weight, value in by_ratio:
    if weight <= room:
        room -= weight
        greedy_value += value
        greedy_took.append(name)
toy_table = knapsack_table(TOY, 10)
best_value = toy_table[len(TOY)][10]
best_took = [name for name, _, _ in knapsack_pick(TOY, 10, toy_table)]
print(f"  greedy by ratio : takes {'+'.join(greedy_took)}, "
      f"value {greedy_value}")
print(f"  optimal         : takes {'+'.join(best_took)}, value {best_value}")
print()
print(f"  the greedy is {greedy_value} where {best_value} was available -- "
      f"{best_value / greedy_value:.1f}x worse")
print()
print("The greedy takes A because its ratio is the best, and that leaves 4")
print("units of room with nothing that fits. The optimal answer skips A")
print("entirely and takes two mediocre items that happen to fit exactly.")
print()
print("This is the general shape of the failure: greedy decisions are")
print("irrevocable, and a locally best choice can consume a resource in a way")
print("that makes the remainder unusable. The ratio is not a bad heuristic --")
print("it is a heuristic, and knapsack has no exchange argument to justify")
print("it. Coin change does, for some coin systems, which is the next")
print("section.")
print()
print()
print("Part 2 -- the table, on a real instance")
print()
table = knapsack_table(ITEMS, CAPACITY)
taken = knapsack_pick(ITEMS, CAPACITY, table)
total_weight = sum(weight for _, weight, _ in taken)
total_value = sum(value for _, _, value in taken)
print(f"  {len(ITEMS)} items, capacity {CAPACITY}")
print()
print(f"  {'item':<12}{'weight':>8}{'value':>8}{'running weight':>17}"
      f"{'running value':>15}")
print("-" * 60)
weight_so_far = value_so_far = 0
for name, weight, value in taken:
    weight_so_far += weight
    value_so_far += value
    print(f"  {name:<12}{weight:>8}{value:>8}{weight_so_far:>17}"
          f"{value_so_far:>15}")
print("-" * 60)
print(f"  {'total':<12}{total_weight:>8}{total_value:>8}")
print()
print(f"  capacity used : {total_weight} of {CAPACITY}")
print(f"  table cells   : {(len(ITEMS) + 1) * (CAPACITY + 1):,}")
print(f"  cells per item: {CAPACITY + 1:,}")
print()
print("The last two lines are the shape of the whole algorithm. The table is")
print("(items + 1) x (capacity + 1), so it grows with the number of items --")
print("which is what you would expect -- and also with the capacity, which is")
print("a *quantity*, not a count of anything.")
print()
print()
print("Part 3 -- the word that qualifies every claim in this chapter")
print()
print("'Polynomial time' means polynomial in the length of the input. For a")
print("list of n items the input length is roughly n. For a capacity, the")
print("input length is the number of *digits* -- writing 100000 takes six")
print("characters, not a hundred thousand.")
print()
print(f"{'capacity':>12}{'digits':>9}{'table cells':>15}{'work vs previous':>19}")
print("-" * 55)
previous = None
for power in (3, 4, 5, 6):
    capacity = 10 ** power
    cells = (len(ITEMS) + 1) * (capacity + 1)
    ratio = "-" if previous is None else f"{cells / previous:.1f}x"
    print(f"{capacity:>12,}{len(str(capacity)):>9}{cells:>15,}{ratio:>19}")
    previous = cells
print()
print("Read the first and last columns together. Every extra digit of")
print("capacity multiplies the table by ten, while the input grows by one")
print("character. So the running time is polynomial in the *value* of the")
print("capacity and exponential in the *length* of it -- which is why")
print("knapsack is called pseudo-polynomial, and why it is not a")
print("counterexample to knapsack being NP-hard.")
print()
print("Both statements are true at once and they are not in tension:")
print()
print("  - for a fixed capacity, or one that fits in a machine word, the")
print("    table is a fixed size and the algorithm is linear in the items")
print("  - for a capacity given as an arbitrarily long number, the table is")
print("    exponential in the input and no shortcut is known")
print()
print("The practical reading is the useful one. This is the right algorithm")
print("when the budget is a real quantity you can afford to enumerate --")
print("200 grams, 48 hours, 5000 dollars. It is the wrong algorithm when the")
print("budget is 10^18, and in that case the usual move is to look for")
print("structure in the values instead of the capacity.")
print()
print()
print("Part 4 -- and the one-line change that breaks it")
print()


def knapsack_1d(items, capacity, descending=True):
    """One row instead of a table.

    The direction of the inner loop is the whole algorithm. Going downwards
    means each item is considered once, against a row that still holds the
    answers from *before* this item. Going upwards means the row has already
    been updated with this item, so the item can be taken again -- which is
    not knapsack 0/1 any more, it is unbounded knapsack.
    """
    best = [0] * (capacity + 1)
    for name, weight, value in items:
        span = range(capacity, weight - 1, -1) if descending \
            else range(weight, capacity + 1)
        for w in span:
            candidate = best[w - weight] + value
            if candidate > best[w]:
                best[w] = candidate
    return best[capacity]


print(f"  two-dimensional table          : {table[len(ITEMS)][CAPACITY]}")
print(f"  one row, capacity downwards    : "
      f"{knapsack_1d(ITEMS, CAPACITY, descending=True)}")
print(f"  one row, capacity upwards      : "
      f"{knapsack_1d(ITEMS, CAPACITY, descending=False)}")
print()
print("The first two agree and the third does not, and the third is the bug")
print("you get by reversing a loop. Going upwards, the cell `best[w-weight]`")
print("has already been written this round, so it may already contain this")
print("item -- and the algorithm happily takes it again, and again, until the")
print("capacity runs out.")
print()
unbounded = knapsack_1d(ITEMS, CAPACITY, descending=False)
best_ratio = max(ITEMS, key=lambda item: item[2] / item[1])
repeats = unbounded // best_ratio[2]
print(f"  the extra value comes from one item taken over and over:")
print(f"    {best_ratio[0]!r} is weight {best_ratio[1]}, value {best_ratio[2]}, "
      f"ratio {best_ratio[2] / best_ratio[1]:.1f}")
print(f"    {repeats} copies of it weigh {repeats * best_ratio[1]} and are worth "
      f"{repeats * best_ratio[2]}")
print()
print("The wrong version is not nonsense. It is a correct solution to a")
print("different problem, unbounded knapsack, where every item is available")
print("in unlimited supply. That is why the bug is easy to miss: the code")
print("runs, the answer is larger than the right one rather than obviously")
print("absurd, and a test that only checks 'is it bigger than zero' passes.")
print("The version that is wrong here is the version you *want* for coin")
print("change, which is the next section -- same table, same loop, opposite")
print("direction.")
print()
print(f"  table cells for the 2-D version : "
      f"{(len(ITEMS) + 1) * (CAPACITY + 1):,}")
print(f"  table cells for the 1-D version : {CAPACITY + 1:,}")
print(f"  saving                          : "
      f"{(len(ITEMS) + 1) * (CAPACITY + 1) / (CAPACITY + 1):.0f}x")
print()
print("The rolling row keeps the answer and throws away the ability to say")
print("*which* items were chosen -- the same trade the edit-distance")
print("traceback made. Everything a DP can tell you comes out of the table,")
print("so a table you did not keep is a question you can no longer answer.")
