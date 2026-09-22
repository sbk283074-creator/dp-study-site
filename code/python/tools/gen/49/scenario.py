#!/usr/bin/env python3
"""Chapter 49 demo -- the scenario: a nightly job that takes forty minutes.

A reporting job joins orders to customers. It works, it has worked for a
year, and it has become slow enough that the team has started scheduling
around it. The task is to find out why and to fix it without changing what
the report says.

The counting takes about a minute. What takes longer is the second half:
the fix that makes it fast also changes its answers, on a case the original
code handled by accident. That is the part a code review is actually for.
"""
import random
from collections import Counter

# ------------------------------------------------------------------ the data

rng = random.Random(49)
CUSTOMERS = [(cid, f"Customer {cid}") for cid in range(1, 401)]
CUSTOMERS.append((137, "Customer 137 (duplicate import)"))   # data-quality artefact

ORDERS = [(oid, rng.randint(1, 400)) for oid in range(1, 1_001)]
# Three orders deliberately reference the duplicated customer, so the
# difference between the two joins is visible rather than theoretical.
DUPLICATE_ID = CUSTOMERS[-1][0]
for oid in (5, 50, 500):
    ORDERS[oid - 1] = (oid, DUPLICATE_ID)


def join_naive(orders, customers):
    """For every order, look at every customer. Returns (rows, comparisons)."""
    comparisons = 0
    rows = []
    for order_id, customer_id in orders:
        for cid, name in customers:
            comparisons += 1
            if cid == customer_id:
                rows.append((order_id, customer_id, name))
    return rows, comparisons


def join_indexed(orders, customers, keep="last"):
    """Build an index once, then one pass. Returns (rows, work)."""
    work = 0
    index = {}
    for cid, name in customers:
        work += 1
        if keep == "last" or cid not in index:
            index[cid] = name
    rows = []
    for order_id, customer_id in orders:
        work += 1
        if customer_id in index:
            rows.append((order_id, customer_id, index[customer_id]))
    return rows, work


def join_indexed_multi(orders, customers):
    """The index that keeps every match, so it agrees with the naive join."""
    work = 0
    index = {}
    for cid, name in customers:
        work += 1
        index.setdefault(cid, []).append(name)
    rows = []
    for order_id, customer_id in orders:
        work += 1
        for name in index.get(customer_id, ()):
            rows.append((order_id, customer_id, name))
    return rows, work


# ------------------------------------------------------------- the code review

print("The job joins 1,000 orders to 400 customers on customer id.\n")
naive_rows, naive_work = join_naive(ORDERS, CUSTOMERS)
index_rows, index_work = join_indexed(ORDERS, CUSTOMERS)
multi_rows, multi_work = join_indexed_multi(ORDERS, CUSTOMERS)

print(f"   nested loop          rows {len(naive_rows):>6,}   "
      f"comparisons {naive_work:>10,}")
print(f"   dict index, last wins rows {len(index_rows):>6,}   "
      f"work        {index_work:>10,}")
print(f"   dict index, all rows  rows {len(multi_rows):>6,}   "
      f"work        {multi_work:>10,}")
print()
print(f"   naive vs index, identical output : "
      f"{naive_rows == index_rows}")
print(f"   naive vs multi, identical output : "
      f"{naive_rows == multi_rows}")

naive_counts = Counter(row[0] for row in naive_rows)
index_counts = Counter(row[0] for row in index_rows)
differing = sorted(oid for oid in naive_counts if naive_counts[oid] != index_counts[oid])
affected = {cid for oid, cid in ORDERS if oid in set(differing)}
all_duplicate = affected == {DUPLICATE_ID}
print()
print(f"   orders whose rows differ between naive and index : {len(differing)}")
print(f"   those orders are {differing}")
print(f"   all of them reference customer {DUPLICATE_ID} : {all_duplicate}")
print(f"   rows the naive join produced   : {len(naive_rows):,}")
print(f"   rows the last-wins index made  : {len(index_rows):,}")
print()
print("This is the finding, and it is not a performance finding. The nested")
print("loop appends a row for *every* customer that matches, so the duplicate")
print("id produces two rows for each order that references it. A dictionary")
print("keyed by customer id holds one name per key, so the index version")
print("silently drops one of them. The report changes, and it changes only on")
print("the orders that touch that customer -- which is why nobody noticed.")

print("\nThe fix is an index of lists, which keeps every match. Verify it:\n")
print(f"   rows in the naive output      : {len(naive_rows):,}")
print(f"   rows in the list-index output : {len(multi_rows):,}")
print(f"   identical, row for row        : {naive_rows == multi_rows}")

# ------------------------------------------------------------- the arithmetic

print("\nNow the arithmetic, which is the part that takes a minute. The nested")
print("loop does one comparison per (order, customer) pair, so its cost is")
print("fixed by the sizes and not by the data. Check that:\n")
print(f"   {'orders':>8}{'customers':>11}{'comparisons':>14}"
      f"{'orders x customers':>21}{'agree':>8}")
print("   " + "-" * 62)
for n_orders, n_customers in ((100, 40), (200, 80), (400, 160)):
    orders = [(i, rng.randint(1, n_customers)) for i in range(n_orders)]
    customers = [(c, f"C{c}") for c in range(1, n_customers + 1)]
    _, work = join_naive(orders, customers)
    print(f"   {n_orders:>8,}{n_customers:>11,}{work:>14,}"
          f"{n_orders * n_customers:>21,}{str(work == n_orders * n_customers):>8}")

print("\nAnd at the sizes the job actually runs at. The nested-loop column is")
print("the formula just verified; the index column is counted.\n")
print(f"   {'orders':>10}{'customers':>11}{'nested loop':>18}"
      f"{'index':>12}{'ratio':>10}")
print("   " + "-" * 61)
for n_orders, n_customers in ((1_000, 400), (50_000, 20_000), (200_000, 120_000)):
    orders = [(i, rng.randint(1, n_customers)) for i in range(n_orders)]
    customers = [(c, f"C{c}") for c in range(1, n_customers + 1)]
    _, work = join_indexed_multi(orders, customers)
    nested = n_orders * n_customers
    print(f"   {n_orders:>10,}{n_customers:>11,}{nested:>18,}{work:>12,}"
          f"{nested / work:>9,.0f}x")

print()
n_orders, n_customers = 200_000, 120_000
nested = n_orders * n_customers
index_ops = n_orders + n_customers
print(f"At {n_orders:,} orders and {n_customers:,} customers the nested loop does")
print(f"{nested:,} comparisons. At a stated 10^7 comparisons per second that")
print(f"is {nested / 1e7:,.0f} seconds, or {nested / 1e7 / 60:,.0f} minutes -- which is")
print("the forty minutes the team has been scheduling around.")
print()
print(f"The index does {index_ops:,} operations instead: "
      f"{nested / index_ops:,.0f}x fewer, and")
print(f"{index_ops / 1e7:.3f} seconds instead of {nested / 1e7:,.0f}.")
print()
print("Two things were needed and only one of them was about speed. The index")
print("fixed the time. Finding the duplicate -- and deciding what the report")
print("should say about it -- fixed the correctness, and it would have been")
print("introduced as a bug if nobody had diffed the two outputs.")
