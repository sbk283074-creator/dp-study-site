#!/usr/bin/env python3
"""Chapter 44 demo 12 -- why a timing reports the minimum of its repeats.

There is no clock in this program either. What it contains is the *model*
behind the rule, run deterministically: a reading is the work plus whatever
else the machine was doing, and that something is never negative. The model
is what makes the protocol a rule rather than a superstition.
"""
import random

TRUE_COST = 100          # the work, in whatever unit you like
REPEATS = 12
INTERFERENCE = 60        # the largest extra load the machine may impose
SEED = 7

rng = random.Random(SEED)


def one_reading(true_cost, rng):
    """The work, plus however much the rest of the machine got in the way."""
    return true_cost + rng.randrange(0, INTERFERENCE)


readings = [one_reading(TRUE_COST, rng) for _ in range(REPEATS)]

print("a reading is the work plus the interference")
print()
print(f"the work itself, which this model fixes at {TRUE_COST}")
print(f"interference per reading, drawn from 0 to {INTERFERENCE - 1}")
print()
print(f"{'repeat':>7}{'reading':>9}{'interference':>14}")
print("-" * 30)
for i, value in enumerate(readings, 1):
    print(f"{i:>7}{value:>9}{value - TRUE_COST:>14}")

lowest = min(readings)
highest = max(readings)
mean = sum(readings) / len(readings)

print()
print(f"{'what you could report':<26}{'value':>8}{'too high by':>13}")
print("-" * 47)
print(f"{'the work itself':<26}{TRUE_COST:>8}{'--':>13}")
print(f"{'minimum of the repeats':<26}{lowest:>8}{lowest - TRUE_COST:>+13}")
print(f"{'mean of the repeats':<26}{mean:>8.1f}{mean - TRUE_COST:>+13.1f}")
print(f"{'maximum of the repeats':<26}{highest:>8}{highest - TRUE_COST:>+13}")

print()
print(f"The minimum is {lowest - TRUE_COST} too high and the mean is "
      f"{mean - TRUE_COST:.0f} too high, and the difference")
print("between those two errors is the whole point. Interference only ever")
print("ADDS. A reading can come out slow because something else was")
print("running, but no reading can come out fast, because the work still")
print("has to happen. So the error in the minimum is bounded by the")
print("smallest interference that was drawn, while the error in the mean is")
print("bounded by nothing at all -- it is the average of everything else the")
print("machine was doing, which is a number nobody wants.")
print()
print("The minimum is therefore the closest thing to the work that this")
print("machine is willing to show you. It is not exact -- even the quietest")
print("of these twelve repeats was interrupted -- but it is the only")
print("statistic here whose error can only ever be too high, and by the")
print("least amount available.")
print()
print("That is the whole argument for min(timeit.repeat(...)) instead of")
print("statistics.mean(...), and note what kind of argument it is: it comes")
print("from the shape of the noise, so it holds on every machine. The size")
print("of the interference does not travel -- it is 60 here because this")
print("model says so -- but the direction does.")
print()
print("Two more things follow, and they are why the protocol has more than")
print("one line in it.")
print()
print("A reading has to be long enough to see. If one run of the work is")
print("shorter than the clock can resolve, then every reading is mostly")
print("resolution and the minimum is meaningless. So the work is run many")
print("times inside one measurement -- that is what `number` is for -- and")
print("the total is divided by it. The division is what makes the answer a")
print("cost per run rather than a cost per measurement.")
print()
print("And the interference has to be given a chance not to happen. One")
print("repeat is one draw from the noise. Twelve repeats are twelve chances")
print("at a quiet one, and the minimum takes the best of them. This is also")
print("why a single number from a single run is not a measurement: it is a")
print("draw, and you cannot tell which one you got.")
