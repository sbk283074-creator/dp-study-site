"""Chapter 38 -- the same problem, two solutions, and a count that separates them.

A warm-up shape: find the two numbers in a list that add up to a target. The
count is of pairs the nested loop examines against lookups the hash set does.
"""

COUNT = 200
TARGET = 341

# One pair sums to the target; the rest are placed so that no other pair does.
NUMBERS = [(index * 37) % 500 for index in range(COUNT)]
NUMBERS[41] = 120
NUMBERS[173] = TARGET - 120


def nested(numbers, target):
    """Every pair, which is the answer everyone writes first."""
    examined = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            examined += 1
            if numbers[i] + numbers[j] == target:
                return (i, j), examined
    return None, examined


def hashed(numbers, target):
    """Remember what you have seen, and ask for the complement."""
    seen = {}
    lookups = 0
    for index, value in enumerate(numbers):
        lookups += 1
        if target - value in seen:
            return (seen[target - value], index), lookups
        seen[value] = index
    return None, lookups


nested_pair, nested_cost = nested(NUMBERS, TARGET)
hashed_pair, hashed_cost = hashed(NUMBERS, TARGET)

rows = [
    ("every pair", nested_pair, nested_cost),
    ("a hash set", hashed_pair, hashed_cost),
]

print(f"{COUNT} numbers, one target, two solutions")
print()
print(f"{'solution':<16}{'answer':>12}{'operations':>13}")
print("-" * 41)
for label, pair, cost in rows:
    print(f"{label:<16}{str(pair):>12}{cost:>13}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'numbers in the list':<46}{COUNT:>8}")
print(f"{'pairs if every pair is checked':<46}{COUNT * (COUNT - 1) // 2:>8}")
print(f"{'pairs the nested loop examined':<46}{nested_cost:>8}")
print(f"{'lookups the hash set made':<46}{hashed_cost:>8}")
print(f"{'solutions that found the pair':<46}"
      f"{sum(1 for _, pair, _ in rows if pair is not None):>8}")
print(f"{'solutions that agree on the answer':<46}"
      f"{int(nested_pair == hashed_pair):>8}")
print(f"{'ratio of the two costs':<46}"
      f"{round(nested_cost / hashed_cost):>8}")

print()
print("Both rows are correct and they are the same answer, which is the part that")
print("makes the comparison worth making. The nested loop is the solution anyone")
print("writes first because it is the definition of the problem restated -- look")
print(f"at every pair -- and it costs {nested_cost} additions to find a pair that a")
print(f"hash set finds in {hashed_cost} lookups.")
print()
print("The number that matters is not the ratio, it is the shape. The nested loop")
print("is quadratic: doubling the list quadruples the work, so it is fine for the")
print(f"{COUNT} numbers in an exercise and useless for the million in a log file. The")
print("hash set is linear, and the price is that it remembers every value it has")
print("seen -- a trade of memory for time that the nested loop does not make.")
print()
print("So the habit worth taking from this problem is not 'use a hash set'. It is")
print("to write the count down before choosing. 'Look at every pair' is a")
print("statement about a loop, and it converts into a number: pairs, additions,")
print("comparisons. A solution whose cost you can name is one you can defend, and")
print("the two-line change between these rows is much easier to make once the")
print("number is on the page.")
