"""Chapter 61 -- a join, counted three ways.

Orders and customers, joined on the customer key. Three designs: a nested
loop, which is what a join is if you write it yourself; a sort of both sides
followed by a merge; and a hash table built on one side. The count is of key
comparisons, and the three sit in three different growth classes.
"""

CUSTOMERS = 1000
ORDER_COUNTS = [1000, 2000, 4000]


def mix(state):
    """A deterministic value in [0, 2**32)."""
    state = (state * 2654435761) % 4294967296
    state = (state ^ (state >> 16)) * 2246822519 % 4294967296
    state = (state ^ (state >> 13)) * 3266489917 % 4294967296
    return (state ^ (state >> 16)) % 4294967296


def orders(count):
    return [(index, mix(7 + index) % CUSTOMERS) for index in range(count)]


def customers():
    return [(index, f"customer-{index:04d}") for index in range(CUSTOMERS)]


def nested_loop(order_rows, customer_rows):
    """Every order against every customer. The inner scan cannot stop early,
    because a key on the inner side may match more than one row."""
    comparisons = 0
    matched = 0
    for _order_id, customer_id in order_rows:
        for other_id, _name in customer_rows:
            comparisons += 1
            if other_id == customer_id:
                matched += 1
    return matched, comparisons


def hash_join(order_rows, customer_rows):
    """One hash per customer, one probe per order."""
    probes = 0
    table = {}
    for customer_id, name in customer_rows:
        probes += 1
        table[customer_id] = name
    matched = 0
    for _order_id, customer_id in order_rows:
        probes += 1
        if customer_id in table:
            matched += 1
    return matched, probes


def sort_merge(order_rows, customer_rows):
    """Put both sides in key order, then walk them together."""
    comparisons = [0]

    def merge_sort(items, key):
        if len(items) <= 1:
            return list(items)
        middle = len(items) // 2
        left = merge_sort(items[:middle], key)
        right = merge_sort(items[middle:], key)
        out = []
        i = 0
        j = 0
        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if key(left[i]) <= key(right[j]):
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    left = merge_sort(order_rows, lambda row: row[1])
    right = merge_sort(customer_rows, lambda row: row[0])
    i = 0
    j = 0
    matched = 0
    while i < len(left) and j < len(right):
        comparisons[0] += 1
        if left[i][1] < right[j][0]:
            i += 1
        elif left[i][1] > right[j][0]:
            j += 1
        else:
            matched += 1
            i += 1
    return matched, comparisons[0]


customer_rows = customers()

print(f"{CUSTOMERS:,} customers, orders from {ORDER_COUNTS[0]:,} to {ORDER_COUNTS[-1]:,}")
print()
print(f"{'orders':>8}{'nested loop':>14}{'sort and merge':>16}{'hash table':>12}"
      f"{'nested/hash':>13}")
print("-" * 63)
for count in ORDER_COUNTS:
    order_rows = orders(count)
    matched_nested, nested = nested_loop(order_rows, customer_rows)
    matched_merge, merge = sort_merge(order_rows, customer_rows)
    matched_hash, hashed = hash_join(order_rows, customer_rows)
    if not matched_nested == matched_merge == matched_hash:
        raise SystemExit("the three designs disagreed about the answer")
    print(f"{count:>8,}{nested:>14,}{merge:>16,}{hashed:>12,}"
          f"{nested / hashed:>13.1f}")

print()
print("All three produce the same answer and the same match count, so nothing")
print("in the result distinguishes them.")
print()
print("The nested loop is the product of the two sizes: doubling the orders")
print("doubles it, and doubling the customers would double it again. The hash")
print("table is the sum of the two sizes, so it is linear in each. Sort and")
print("merge is n log n in each side, which is why it sits between them -- and")
print("it is the design that wins when one side is already in key order,")
print("because then there is nothing to sort and the merge is a single walk.")
print()
print("The column that matters is the last one. At a thousand orders the")
print("nested loop is five hundred times the hash table, and the ratio grows")
print("with the table, because one design is a product and the other is a sum.")
