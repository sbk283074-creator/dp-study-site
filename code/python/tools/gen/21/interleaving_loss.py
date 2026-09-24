"""Chapter 21 -- a race is a count, not a timing.

Two workers each read a counter, add to it, and write it back. Every
interleaving of their six operations is enumerated. The count is of interleavings
that lose an update, and no clock is involved anywhere.
"""

import itertools

STEPS = ("read", "add", "write")
WORKERS = ("A", "B")
LENGTH = len(STEPS) * len(WORKERS)


def merge(first_positions):
    """One interleaving, chosen by which slots the first worker's steps take."""
    sequence = []
    queues = {name: list(STEPS) for name in WORKERS}
    for index in range(LENGTH):
        name = WORKERS[0] if index in first_positions else WORKERS[1]
        sequence.append((name, queues[name].pop(0)))
    return sequence


def simulate(sequence):
    counter = 0
    registers = {name: 0 for name in WORKERS}
    for name, step in sequence:
        if step == "read":
            registers[name] = counter
        elif step == "add":
            registers[name] += 1
        else:
            counter = registers[name]
    return counter


def atomic_simulate():
    """The same work with the read, the add and the write held as one step."""
    counter = 0
    for _ in WORKERS:
        counter = counter + 1
    return counter


outcomes = {}
for positions in itertools.combinations(range(LENGTH), len(STEPS)):
    value = simulate(merge(positions))
    outcomes[value] = outcomes.get(value, 0) + 1

total = sum(outcomes.values())
kept = outcomes.get(len(WORKERS), 0)

print(f"{len(WORKERS)} workers, {len(STEPS)} steps each, every interleaving enumerated")
print()
print(f"{'final counter':<18}{'interleavings':>16}")
print("-" * 34)
for value in sorted(outcomes):
    print(f"{value:<18}{outcomes[value]:>16}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'interleavings enumerated':<46}{total:>8}")
print(f"{'interleavings that keep both updates':<46}{kept:>8}")
print(f"{'interleavings that lose one update':<46}{total - kept:>8}")
print(f"{'updates kept with the three steps held together':<46}"
      f"{atomic_simulate():>8}")

print()
print(f"The middle row is the whole lesson: {total - kept} of the {total} possible orderings lose")
print("an update. No clock, no scheduler, no thread -- the count is a property")
print("of the code. Two workers read the same value, each adds one to its own")
print("copy, and each writes it back. The second write is not wrong; it is")
print("overwriting an answer that was correct at the moment it was read.")
print()
print("That is why 'it passes on my machine' is not evidence about a race.")
print("Whether the bad ordering happens is decided by the machine. How many")
print("orderings are bad is decided by the code, and it is decided before the")
print("program runs -- which is the number a test can be built on.")
print()
print("The last row is the fix, and it is not a lock. If the read, the add and")
print("the write cannot be separated, there are no interleavings left to lose")
print("an update in: the work is one step, and every ordering of one step is")
print("the same ordering. When the operation cannot be made atomic, put a lock")
print("around it. When it can, the lock was never the point.")
