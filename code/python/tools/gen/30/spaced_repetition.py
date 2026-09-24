"""Chapter 30 -- a review schedule is arithmetic, and the arithmetic is the product.

One card reviewed on a growing interval, with and without a lapse. The count is of
reviews needed to push the interval past a year, and of what one wrong answer
costs.
"""

START_INTERVAL = 1
EASE = 2.5
FLOOR_EASE = 1.3
TARGET = 365
LIMIT = 60


def bump(interval, ease):
    return max(1, int(interval * ease + 0.5))


def run(lapse_at=None):
    interval = START_INTERVAL
    ease = EASE
    days = 0
    trace = []
    for review in range(1, LIMIT + 1):
        if review == lapse_at:
            interval = START_INTERVAL
            ease = max(FLOOR_EASE, ease - 0.2)
        else:
            interval = bump(interval, ease)
        days += interval
        trace.append((review, interval, days))
        if interval >= TARGET:
            return review, days, interval, trace
    return LIMIT, days, interval, trace


none = run()
early = run(3)
late = run(6)

print(f"one card, target interval {TARGET} days, ease factor {EASE}")
print()
print(f"{'sequence':<28}{'reviews':>9}{'days covered':>14}{'final interval':>16}")
print("-" * 67)
for label, result in (("no lapse", none),
                      ("a lapse at review 3", early),
                      ("a lapse at review 6", late)):
    print(f"{label:<28}{result[0]:>9}{result[1]:>14}{result[2]:>16}")

print()
print("the first six reviews with no lapse:")
print(f"{'review':>7}{'interval':>10}{'days covered':>14}")
for review, interval, days in none[3][:6]:
    print(f"{review:>7}{interval:>10}{days:>14}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'target interval in days':<46}{TARGET:>8}")
print(f"{'reviews to reach it with no lapse':<46}{none[0]:>8}")
print(f"{'reviews to reach it with a lapse at 3':<46}{early[0]:>8}")
print(f"{'reviews to reach it with a lapse at 6':<46}{late[0]:>8}")
print(f"{'extra reviews an early lapse costs':<46}{early[0] - none[0]:>8}")
print(f"{'extra reviews a late lapse costs':<46}{late[0] - none[0]:>8}")

print()
print("Seven reviews take one card past a year, and the table of intervals is")
print("the product: the schedule is a handful of multiplications, and nothing")
print("about it needs a database or a service. That is the point of putting the")
print("scheduler in a pure core -- it can be tested against a list of answers")
print("like the one above, with no fixtures and no clock.")
print()
print("The last two rows are the surprising part, and they are why this is")
print("worth counting rather than reasoning about. A lapse at review 3 costs")
print("four extra reviews to get back to a year. A lapse at review 6 costs")
print("seven. The later failure is the more expensive one, because by then the")
print("interval has grown to a hundred and twenty-five days and the reset")
print("throws all of it away.")
print()
print("So the shape of the curve is worth knowing before you tune the")
print("constants. A lapse does not cost a fixed amount; it costs what the")
print("interval had grown to, which means the cards that hurt most when you")
print("forget them are the ones you had learned best. That is either the")
print("feature you wanted or the one you have to design around, and you cannot")
print("tell which without the numbers.")
