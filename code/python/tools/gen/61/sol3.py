"""Chapter 61 -- solution 3. A join with a filter in front of it.

Four thousand orders, a thousand customers, and a filter that keeps one order
in ten. Three designs, and the count is of key comparisons. The result is
that the join design and the filter position are not independent choices --
the cheapest pair is not the cheapest join plus the cheapest filter.
"""

CUSTOMERS = 1000
ORDERS = 4000
KEEP_EVERY = 10


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


def orders():
    return [(index, mix(7 + index) % CUSTOMERS) for index in range(ORDERS)]


def customers():
    return [(index, f"customer-{index:04d}") for index in range(CUSTOMERS)]


def nested_then_filter(order_rows, customer_rows):
    """Join everything, then throw nine tenths of it away."""
    comparisons = 0
    kept = 0
    for _order_id, customer_id in order_rows:
        for other_id, _name in customer_rows:
            comparisons += 1
            if other_id == customer_id and customer_id % KEEP_EVERY == 0:
                kept += 1
    return kept, comparisons


def filter_then_nested(order_rows, customer_rows):
    """Throw nine tenths away, then join what is left the same way."""
    comparisons = 0
    survivors = [row for row in order_rows if row[1] % KEEP_EVERY == 0]
    for _order_id, customer_id in survivors:
        for other_id, _name in customer_rows:
            comparisons += 1
            if other_id == customer_id:
                pass
    return len(survivors), comparisons


def filter_then_hash(order_rows, customer_rows):
    """Throw nine tenths away, then probe a table built once."""
    comparisons = 0
    table = {}
    for customer_id, name in customer_rows:
        comparisons += 1
        table[customer_id] = name
    kept = 0
    for _order_id, customer_id in order_rows:
        if customer_id % KEEP_EVERY:
            continue
        comparisons += 1
        if customer_id in table:
            kept += 1
    return kept, comparisons


order_rows = orders()
customer_rows = customers()

DESIGNS = [
    ("join, then filter", nested_then_filter),
    ("filter, then join", filter_then_nested),
    ("filter, then a hash join", filter_then_hash),
]

print(f"{ORDERS:,} orders, {CUSTOMERS:,} customers, one order in {KEEP_EVERY} survives")
print()
print(f"{'design':<26}{'rows joined':>13}{'comparisons':>14}{'per survivor':>14}")
print("-" * 67)
results = []
for name, design in DESIGNS:
    kept, comparisons = design(order_rows, customer_rows)
    results.append((name, kept, comparisons))
    print(f"{name:<26}{kept:>13,}{comparisons:>14,}{comparisons / kept:>14.0f}")

if len({kept for _name, kept, _c in results}) != 1:
    raise SystemExit("the three designs disagreed about the answer")

print()
print("All three produce the same rows, and the first one compares every order")
print("against every customer before discovering that nine tenths of the result")
print("was not wanted. Moving the filter in front of the join removes that work")
print("without changing the join at all.")
print()
print("The third row is the one worth noticing: it is the same filter position")
print("as the second and a different join, and it is the cheapest of the three.")
print("The two decisions are not independent -- a filter that shrinks the outer")
print("side by ten makes a nested loop affordable, and it makes a hash join")
print("better still, and choosing the join first and the filter position second")
print("gets you the second row instead of the third.")
