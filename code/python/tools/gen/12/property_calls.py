"""Chapter 12 -- a property is a function call wearing an attribute's clothes.

One class with a plain attribute and one with a validated property, read the
same number of times and assigned the same number of times. The count is of
getter invocations, and of assignments the guard refused.
"""

READS = 1000
SETS = 50
FLOOR = -273.15


class Plain:
    def __init__(self, value):
        self.value = value


class Guarded:
    def __init__(self, value):
        self.gets = 0
        self.refusals = 0
        self.value = value

    @property
    def value(self):
        self.gets += 1
        return self._value

    @value.setter
    def value(self, new):
        if new < FLOOR:
            self.refusals += 1
            raise ValueError(f"{new} is below absolute zero")
        self._value = new


plain = Plain(20.0)
guarded = Guarded(20.0)

for _ in range(READS):
    plain.value
    guarded.value
gets_after_reads = guarded.gets

accepted = 0
refused = 0
for index in range(SETS):
    candidate = FLOOR - 1 if index % 10 == 0 else 20.0 + index
    try:
        guarded.value = candidate
        accepted += 1
    except ValueError:
        refused += 1

print(f"{READS} reads and {SETS} assignments to each class")
print()
print(f"{'what is counted':<42}{'plain':>8}{'property':>10}")
print("-" * 60)
print(f"{'reads performed':<42}{READS:>8}{READS:>10}")
print(f"{'functions called by those reads':<42}{0:>8}{gets_after_reads:>10}")
print(f"{'assignments attempted':<42}{SETS:>8}{SETS:>10}")
print(f"{'assignments accepted':<42}{SETS:>8}{accepted:>10}")
print(f"{'assignments refused by the guard':<42}{0:>8}{refused:>10}")

print()
print("The second row is the price. A thousand reads of the plain attribute")
print("called nothing; a thousand reads of the property called the getter a")
print(f"thousand times, because a property is a descriptor and every read goes")
print("through it. That is a real cost, and it is why a property is worth")
print("writing for a rule and not for tidiness.")
print()
print(f"The last two rows are what the cost buys. {refused} of the {SETS} assignments")
print("never reached the attribute, because the setter checked the value")
print("before storing it, and every one of them raised rather than corrupting")
print("the object. A plain attribute has no such moment: an assignment either")
print("happens or does not, and what it stores is whatever it was handed.")
print()
print("So the rule is the one the chapter states. Use a property when there is")
print("an invariant to keep -- a floor, a range, a derived value, a rename that")
print("must not break callers. Do not use one to make an attribute look")
print("public, because that pays the call on every read and enforces nothing.")
