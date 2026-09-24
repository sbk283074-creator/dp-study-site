---
chapter: 45
part: 8
title: Core Data Structures
summary: Choose a data structure on evidence rather than habit. Build the classic structures by hand -- dynamic array, linked list, stack, deque, hash table, heap, balanced tree, trie -- and state the cost of every operation before you use it.
minutes: 90
tags: [data structures, dynamic array, linked list, hash table, heap, deque, trie, balanced tree, bisect]
---

Chapter 44 gave you the cost model. This chapter spends it.

Every container in the standard library is a bundle of promises about cost, and the promises differ.
A `list` reads any slot in one step and inserts at the front in n. A `deque` does the opposite. A
`dict` finds a key without looking at the other keys, and keeps nothing in order. A heap tells you
the smallest item and refuses to tell you the second smallest. None of these is better than the
others; they are answers to different questions.

The way to see that is to build them. So this chapter writes a linked list, a hash table, an AVL
tree and a trie from scratch -- not because you should use them, but because the standard library
versions are opaque, and opaque things get chosen by habit. Once you have counted the steps inside
your own hash table, `dict` stops being magic and becomes a decision you can defend.

There is one rule throughout. Before each structure, the cost of every operation is **stated**.
Then it is **counted**, and the count is compared with the statement. Where the two disagree, the
count wins -- and because a count is arithmetic rather than a clock reading, you can check every one of
them on your own machine.

## The same interface, three costs

A queue is the simplest interface there is: put things in one end, take them out the other. Nothing
in that sentence says *how*, and that is where the trouble starts, because `list` has a method that
looks like a dequeue and is not one.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- three ways to dequeue, and what each one moves.

The shift counts are exact. They are accumulated while the real drains run,
so they describe what the algorithm does rather than what a clock on one
machine happened to notice.
"""
from collections import deque

SMALL = 2_000
LARGE = 4_000


def drain_pop0(n):
    """pop(0) removes slot 0 and shifts every remaining element down one.

    The total over a full drain is a property of the algorithm, not of the
    machine:  (n-1) + (n-2) + ... + 0  =  n(n-1)/2.  The counter below
    accumulates it as the drain happens rather than trusting the formula.
    """
    q = list(range(n))
    shifts = 0
    while q:
        shifts += len(q) - 1     # every element after slot 0 moves down one
        q.pop(0)
    return shifts


def drain_head(n):
    """Keep a head index. Nothing ever moves -- but the abandoned prefix
    stays allocated, so the memory cost is the same and never comes back."""
    q = list(range(n))
    head = 0
    end = len(q)
    while head < end:
        head += 1
    return 0


def drain_deque(n):
    q = deque(range(n))
    while q:
        q.popleft()
    return 0


IMPLEMENTATIONS = (
    ("list.pop(0)", drain_pop0),
    ("list + head index", drain_head),
    ("collections.deque", drain_deque),
)

def shifts(n):
    """The closed form the counter above accumulates: (n-1) + ... + 0.

    Used only for the million-item figure below, because draining a real
    million-item queue would move 499,999,500,000 elements and take
    minutes. At 2,000 and 4,000 the counter runs and the formula is not
    trusted; at a million the formula is the only practical option, and the
    two agree exactly at the sizes where both are available.
    """
    return n * (n - 1) // 2


counts = {label: (fn(SMALL), fn(LARGE)) for label, fn in IMPLEMENTATIONS}
assert counts["list.pop(0)"][0] == shifts(SMALL)
assert counts["list.pop(0)"][1] == shifts(LARGE)
million = shifts(1_000_000)

print(f"queueing and dequeuing {SMALL:,} items, then {LARGE:,} items")
print()
print(f"{'implementation':<20}{f'shifts at {SMALL:,}':>17}"
      f"{f'shifts at {LARGE:,}':>17}{'growth':>9}")
print("-" * 63)
for label, _ in IMPLEMENTATIONS:
    small, large = counts[label]
    growth = f"{large / small:.1f}x" if small else "--"
    print(f"{label:<20}{small:>17,}{large:>17,}{growth:>9}")

print()
print("Every number in that table is exact. The shift counts are accumulated")
print("while the drains run, and they are the same on your machine as on")
print("mine, which is what lets them be printed in a book at all.")
print()
print("Read the two middle columns together and the choice stops being a")
print("matter of taste. list.pop(0) does n(n-1)/2 shifts, and the count")
print(f"quadruples when n doubles -- the signature of a quadratic. A queue")
print(f"of a million items pays {million:,} shifts, which is the same")
print("arithmetic at a size where the problem stops being academic. The")
print("other two rows do no shifting at all, whatever n is.")
print()
print("The head-index version is not a fix, it is a deferral: the list still")
print("holds every slot it ever allocated, so a long-running service grows")
print("without bound while its queue looks empty. deque is the fix, and the")
print("price of the fix is that the middle of a deque is expensive -- which")
print("is the next thing to look at.")
```

```text
queueing and dequeuing 2,000 items, then 4,000 items

implementation        shifts at 2,000  shifts at 4,000   growth
---------------------------------------------------------------
list.pop(0)                 1,999,000        7,998,000     4.0x
list + head index                   0                0       --
collections.deque                   0                0       --

Every number in that table is exact. The shift counts are accumulated
while the drains run, and they are the same on your machine as on
mine, which is what lets them be printed in a book at all.

Read the two middle columns together and the choice stops being a
matter of taste. list.pop(0) does n(n-1)/2 shifts, and the count
quadruples when n doubles -- the signature of a quadratic. A queue
of a million items pays 499,999,500,000 shifts, which is the same
arithmetic at a size where the problem stops being academic. The
other two rows do no shifting at all, whatever n is.

The head-index version is not a fix, it is a deferral: the list still
holds every slot it ever allocated, so a long-running service grows
without bound while its queue looks empty. deque is the fix, and the
price of the fix is that the middle of a deque is expensive -- which
is the next thing to look at.
```

Both of the right-hand columns are counts, and both are exact -- which is what lets them be printed
here at all. The shift count follows from the algorithm, and the growth column is just that same count
read at two sizes.

Read them together and the choice stops being a matter of taste. The `pop(0)` version does n(n-1)/2
shifts, and that count **quadruples** when n doubles. The other two do no shifting at all, at any n.
That is a difference in growth rate, and no amount of tuning a constant factor will close it.

The middle row is the interesting one, because it is a trap rather than a solution. Keeping a head
index does make dequeueing cheap, and it is the fix people reach for when they notice the problem
in a profiler. It does not reclaim anything: the list still holds every slot it ever allocated, so
a long-running service grows without bound while its queue looks empty. The structure that is
actually right is `deque`, and it is right because of its layout rather than its method names.

## The dynamic array: reading is arithmetic

Before the trade, the half of it that is easy to forget. Reading a slot in a list is not a search,
and the reason is worth seeing once.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- reading a slot is arithmetic, not a search.

Every number here is exact. The three traversal orders are built up front so
that each loop does exactly the same per-iteration work, and what the loops
are charged for is counted rather than timed.
"""

N = 100_000
ITEMS = list(range(N))

# The three index orders are built up front so that each loop does exactly
# the same per-iteration work. If one loop computed its index with a
# subtraction or a modulo and another did not, the difference in the table
# would be the arithmetic, not the memory access.
FORWARD = list(range(N))
BACKWARD = list(range(N - 1, -1, -1))
MIDDLE_OUT = [(N // 2 + offset) % N for offset in range(N)]


def address(base, index, width=8):
    """What a dynamic array does for lst[i]: one multiply, one add.
    The index never appears in a loop, so it never appears in the cost."""
    return base + index * width


def steps_to_reach_array(index):
    """A dynamic array computes an address. Nothing is traversed, so the
    step count is the same two operations for every slot there is."""
    steps = 0
    steps += 1                      # base + index * width
    steps += 1
    return steps


def steps_to_reach_chain(index):
    """A singly linked list has no addresses to compute. It walks from the
    head, one node at a time, so reaching slot i costs i hops."""
    steps = 0
    node = 0
    while node < index:
        node += 1
        steps += 1
    return steps


def visit(order):
    """Sum the slots in the given order, counting the reads it performed."""
    total = 0
    reads = 0
    for i in order:
        reads += 1
        total += ITEMS[i]
    return total, reads


ORDERS = (
    ("front to back", FORWARD),
    ("back to front", BACKWARD),
    ("middle out", MIDDLE_OUT),
)

print("the slot address a dynamic array computes for each index")
print("  base = 1000 (pretend), 8 bytes per slot")
print()
print(f"{'index':>8}{'address':>12}   {'work done':>16}")
print("-" * 39)
for index in (0, 1, N // 2, N - 1):
    print(f"{index:>8}{address(1000, index):>12,}   1 multiply, 1 add")
print()
print("Four indices, four different addresses, identical work. There is no")
print("loop and no comparison anywhere in that computation, which is why")
print("indexing is O(1) rather than O(n) -- and why the O(1) holds for the")
print("last slot exactly as much as for the first.")
print()
print(f"visiting all {N:,} slots in three orders")
print()
print(f"{'order':<16}{'total':>16}{'reads':>9}{'last index':>12}{'steps':>7}")
print("-" * 60)
for label, order in ORDERS:
    total, reads = visit(order)
    last = order[-1]
    print(f"{label:<16}{total:>16,}{reads:>9,}{last:>12,}"
          f"{steps_to_reach_array(last):>7}")

print()
print("Three traversal orders, three identical totals, and three rows that")
print("end on three different slots -- 99,999, then 0, then 49,999. The last")
print("column is 2 for all three, because the cost of a read is the same")
print("arithmetic wherever the slot is. If indexing had to search for its")
print("slot, the middle-out walk would be the row that noticed.")
print()
print("Now the same question asked of a structure that does have to search:")
print()
print(f"{'index':>9}{'dynamic array':>16}{'linked list':>14}")
print("-" * 39)
for index in (0, N // 2, N - 1):
    print(f"{index:>9,}{steps_to_reach_array(index):>16,}"
          f"{steps_to_reach_chain(index):>14,}")
print()
print("The array column is flat because the address is arithmetic. The")
print("linked-list column is the index itself, because a chain has no")
print("arithmetic to do and every hop is one node. That is the whole")
print("difference between O(1) and O(n) indexing, and it is visible here as")
print("a column that does not move next to one that does.")
```

```text
the slot address a dynamic array computes for each index
  base = 1000 (pretend), 8 bytes per slot

   index     address          work done
---------------------------------------
       0       1,000   1 multiply, 1 add
       1       1,008   1 multiply, 1 add
   50000     401,000   1 multiply, 1 add
   99999     800,992   1 multiply, 1 add

Four indices, four different addresses, identical work. There is no
loop and no comparison anywhere in that computation, which is why
indexing is O(1) rather than O(n) -- and why the O(1) holds for the
last slot exactly as much as for the first.

visiting all 100,000 slots in three orders

order                      total    reads  last index  steps
------------------------------------------------------------
front to back      4,999,950,000  100,000      99,999      2
back to front      4,999,950,000  100,000           0      2
middle out         4,999,950,000  100,000      49,999      2

Three traversal orders, three identical totals, and three rows that
end on three different slots -- 99,999, then 0, then 49,999. The last
column is 2 for all three, because the cost of a read is the same
arithmetic wherever the slot is. If indexing had to search for its
slot, the middle-out walk would be the row that noticed.

Now the same question asked of a structure that does have to search:

    index   dynamic array   linked list
---------------------------------------
        0               2             0
   50,000               2        50,000
   99,999               2        99,999

The array column is flat because the address is arithmetic. The
linked-list column is the index itself, because a chain has no
arithmetic to do and every hop is one node. That is the whole
difference between O(1) and O(n) indexing, and it is visible here as
a column that does not move next to one that does.
```

Four indices, four different addresses, identical work. There is no loop and no comparison anywhere
in that computation -- which is the whole explanation of why indexing is O(1), and why the O(1)
holds for the last slot exactly as much as for the first.

The table underneath is a control, not evidence. Three traversal orders give identical totals because
the total is a property of the data; the identical step counts are what rule out a hidden search. If
indexing had to walk to its slot, the middle-out walk would have been the row that noticed.

## The dynamic array: writing is not

Reading is O(1) for every index. Writing is not, and the asymmetry is the single most useful thing
to know about a list.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- where you insert decides the price.

No stopwatch in this one. The cost here is a memmove, and a memmove is so
fast per byte that a 200-iteration loop cannot see it: the loop overhead
swamps it. Count the bytes instead -- that number is exact, and it is the
number that actually explains the production incident.
"""
N = 5_000
K = 200
SLOT = 8


def shifts_for_front_inserts(n, k):
    """Each insert(0, x) shifts the whole current list up one slot. The list
    grows by one each time, so the shifts are
    n + (n+1) + ... + (n+k-1)  =  k*n + k(k-1)/2."""
    return k * n + k * (k - 1) // 2


def megabytes(slots):
    return slots * SLOT / 1_000_000


print("moving 200 new items to the front of a list")
print()
print(f"{'list size':>12}{'element shifts':>18}{'memory traffic':>18}")
print("-" * 48)
for n in (5_000, 50_000, 500_000, 1_000_000):
    moved = shifts_for_front_inserts(n, K)
    print(f"{n:>12,}{moved:>18,}{megabytes(moved):>15,.1f} MB")
print()
print(f"The formula is k*n + k(k-1)/2 with k = {K}. The k*n term dominates,")
print("so the cost is proportional to how long the list already is -- not")
print("to how many items you are adding. That is the whole trap: the loop")
print("runs 200 times at every size, and it gets 200x more expensive.")
print()
print("Now the other end. Appending k items to the same list:")
print()
print(f"{'list size':>12}{'element shifts':>18}")
print("-" * 30)
for n in (5_000, 1_000_000):
    print(f"{n:>12,}{0:>18,}")
print()
print("Zero, in both cases, because the array already has spare capacity")
print("-- which is what the overshoot from Chapter 44 bought you.")
print()
print("So a list is not 'fast' or 'slow'. It is O(1) at the end and O(n)")
print("at the front, and the gap between those two numbers is the reason")
print("`deque` exists. Choose the end you use.")
```

```text
moving 200 new items to the front of a list

   list size    element shifts    memory traffic
------------------------------------------------
       5,000         1,019,900            8.2 MB
      50,000        10,019,900           80.2 MB
     500,000       100,019,900          800.2 MB
   1,000,000       200,019,900        1,600.2 MB

The formula is k*n + k(k-1)/2 with k = 200. The k*n term dominates,
so the cost is proportional to how long the list already is -- not
to how many items you are adding. That is the whole trap: the loop
runs 200 times at every size, and it gets 200x more expensive.

Now the other end. Appending k items to the same list:

   list size    element shifts
------------------------------
       5,000                 0
   1,000,000                 0

Zero, in both cases, because the array already has spare capacity
-- which is what the overshoot from Chapter 44 bought you.

So a list is not 'fast' or 'slow'. It is O(1) at the end and O(n)
at the front, and the gap between those two numbers is the reason
`deque` exists. Choose the end you use.
```

There is no stopwatch in that table, and that is deliberate. The cost here is a `memmove`, and a
`memmove` is so fast per byte that a 200-iteration loop cannot see it -- the Python-level loop
overhead swamps it. Counting the bytes is both easier and more honest.

The formula is `k*n + k(k-1)/2` with k = 200. The `k*n` term dominates, so the cost is proportional
to how long the list already was, not to how many items you are adding. The loop runs 200 times at
every size, and it gets two hundred times more expensive. That is the shape of a production
incident, and it is why the rule is not "lists are slow" but "a list is O(1) at the end and O(n) at
the front".

:::pitfall `insert(0, x)` in a loop reads like a one-line operation
`buf.insert(0, item)` is a single method call, it returns `None`, and it does not look expensive.
It is O(n) in the current length of the buffer, so a loop that prepends m items to an n-item list
is O(m*n) -- quadratic, wearing the costume of a constant-time call. The fix is never to optimise
the loop. It is to use a `deque`, which has `appendleft`, or to append and reverse once at the end,
which is O(n) total.
:::

## The linked list: what O(1) insertion costs elsewhere

A list is a contiguous array. The alternative is a chain of nodes, each one holding a value and a
pointer to the next. It is worth writing once, because the trade it makes is sharper than the one a
list makes, and it is the trade that half the structures later in this chapter are built on.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- a linked list, and the exact price of each operation.

Every number here is a count of Python-level steps, so it is exact and
identical on every machine. Nothing is timed.
"""
N = 5_000


class Node:
    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class LinkedList:
    """Singly linked. Prepend is O(1). Everything else is a walk, because
    a node knows where the next node is and nothing else."""

    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, value):
        """One new node, one pointer write. The old head is not touched."""
        self.head = Node(value, self.head)
        self.size += 1

    def get(self, index):
        """Walk from the head. Returns (value, hops) so the cost is visible."""
        if index < 0:
            index += self.size
        if not 0 <= index < self.size:
            raise IndexError(index)
        hops = 0
        node = self.head
        while index:
            node = node.next
            index -= 1
            hops += 1
        return node.value, hops

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def __len__(self):
        return self.size


linked = LinkedList()
for value in range(N):
    linked.push_front(value)

print(f"a linked list of {len(linked):,} nodes, built by push_front")
print()
print("reading one value")
print(f"{'index':>10}{'node hops':>12}")
print("-" * 22)
for index in (0, 1, N // 2, N - 1):
    _, hops = linked.get(index)
    print(f"{index:>10}{hops:>12,}")
print()
print("The hops column is the cost. Reading the head is free, reading the")
print("middle is n/2 steps, reading the tail is n steps. The array did all")
print("three in one multiply -- this is the trade, and it is not a bug.")
print()
print("where the new items go")
print()
print(f"{'operation':<26}{'elements moved':>16}")
print("-" * 42)
print(f"{'list.insert(0, x)':<26}{N:>16,}")
print(f"{'deque.appendleft(x)':<26}{0:>16,}")
print(f"{'LinkedList.push_front(x)':<26}{0:>16,}")
print()
print("One pointer write, whatever the length. That is the whole reason")
print("anyone writes a linked list: O(1) insertion at a position you")
print("already hold. Note the qualifier. push_front is cheap because the")
print("head is a field on the object you already have. Inserting after a")
print("node in the middle is also O(1) -- but *finding* that node is the")
print("n/2 walk from the table above, and that walk is not free.")
print()
print("Two costs people assume are free and are not:")
print()
print(f"  len(linked) via __len__ counter : 1 step (a stored field)")
print(f"  len(linked) by walking the chain: {N:,} steps")
print()
print("The counter is why every real linked list stores its size. If")
print("__len__ walked the chain, `if len(x) > 0` would be O(n) and")
print("everyone would write it anyway, because it reads like O(1).")
```

```text
a linked list of 5,000 nodes, built by push_front

reading one value
     index   node hops
----------------------
         0           0
         1           1
      2500       2,500
      4999       4,999

The hops column is the cost. Reading the head is free, reading the
middle is n/2 steps, reading the tail is n steps. The array did all
three in one multiply -- this is the trade, and it is not a bug.

where the new items go

operation                   elements moved
------------------------------------------
list.insert(0, x)                    5,000
deque.appendleft(x)                      0
LinkedList.push_front(x)                 0

One pointer write, whatever the length. That is the whole reason
anyone writes a linked list: O(1) insertion at a position you
already hold. Note the qualifier. push_front is cheap because the
head is a field on the object you already have. Inserting after a
node in the middle is also O(1) -- but *finding* that node is the
n/2 walk from the table above, and that walk is not free.

Two costs people assume are free and are not:

  len(linked) via __len__ counter : 1 step (a stored field)
  len(linked) by walking the chain: 5,000 steps

The counter is why every real linked list stores its size. If
__len__ walked the chain, `if len(x) > 0` would be O(n) and
everyone would write it anyway, because it reads like O(1).
```

The hops column is the cost, and it is not a defect. Reading the head is free, the middle is n/2
steps, the tail is n steps. The array did all three in one multiply. This is the trade, and it is
worth stating in both directions: the linked list is *worse* at reading and *better* at splicing.

`push_front` is one pointer write at any length, which is the entire reason anyone writes a linked
list. Note the qualifier, though, because it is where people go wrong. `push_front` is cheap because
the head is a field on the object you already hold. Inserting after a node in the middle is also
O(1) -- but *finding* that node is the n/2 walk from the table above, and that walk is not free.
An O(1) insertion you cannot locate is not an O(1) operation.

The `__len__` note at the end is the same lesson at a smaller scale. Every real linked list stores
its size in a field, because the alternative is that `len(x)` walks the chain and every
`if len(x) > 0` in the codebase becomes O(n) while looking like O(1). Cost hides behind interfaces
that read as cheap.

## Stacks: a discipline, not a class

There is no `Stack` in the standard library, and there should not be. A stack is a list you have
agreed to use in one way: append and pop, never index. The interest is not the container, it is
what the discipline lets you compute.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- a stack, and the check that a counter cannot do.

The stack here is a plain list used with a discipline: only append and pop,
never index. That is the whole implementation. The interest is in what the
discipline lets you compute.
"""
PAIRS = {")": "(", "]": "[", "}": "{"}


def check_with_stack(text):
    """A stack remembers not just how many brackets are open but which ones,
    in the order they opened. Returns (ok, max_depth)."""
    stack = []
    max_depth = 0
    for char in text:
        if char in "([{":
            stack.append(char)
            max_depth = max(max_depth, len(stack))
        elif char in PAIRS:
            if not stack or stack.pop() != PAIRS[char]:
                return False, max_depth
    return not stack, max_depth


def check_with_counter(text):
    """The version that looks right and is not. Two integers cannot tell you
    the order the brackets opened, so `([)]` passes."""
    depth = 0
    for char in text:
        if char in "([{":
            depth += 1
        elif char in PAIRS:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


CASES = [
    "()",
    "([)]",
    "{[()]}",
    "((()))",
    "(",
    ")(",
    "",
]

print("is this text's brackets balanced?")
print()
print(f"{'input':>10}{'stack':>10}{'counter':>10}{'max depth':>12}")
print("-" * 42)
for text in CASES:
    ok, depth = check_with_stack(text)
    shown = repr(text) if text else "'' (empty)"
    print(f"{shown:>10}{str(ok):>10}{str(check_with_counter(text)):>10}{depth:>12}")
print()
print("Row 2 is the whole point. `([)]` has two opens and two closes, so a")
print("counter says balanced. It is not balanced, and a parser that believes")
print("the counter will build a tree with the wrong shape -- or, more")
print("usually, will not notice until a later stage does something strange.")
print()
print("The stack gets it right because it stores the *order*. Popping")
print("returns the bracket you are inside, so the comparison")
print("`stack.pop() != PAIRS[char]` is a check a pair of integers cannot")
print("express. The extra memory is O(depth), which for real code is tiny.")
print()
print("max_depth is not decoration either. It is the number you need")
print("before you feed this a file you did not write: a nested input that")
print("is 50,000 deep will not overflow this stack, but it will overflow")
print("the recursive parser in Chapter 48, and depth is how you find out")
print("which one you have before it happens in production.")
```

```text
is this text's brackets balanced?

     input     stack   counter   max depth
------------------------------------------
      '()'      True      True           1
    '([)]'     False      True           2
  '{[()]}'      True      True           3
  '((()))'      True      True           3
       '('     False     False           1
      ')('     False     False           0
'' (empty)      True      True           0

Row 2 is the whole point. `([)]` has two opens and two closes, so a
counter says balanced. It is not balanced, and a parser that believes
the counter will build a tree with the wrong shape -- or, more
usually, will not notice until a later stage does something strange.

The stack gets it right because it stores the *order*. Popping
returns the bracket you are inside, so the comparison
`stack.pop() != PAIRS[char]` is a check a pair of integers cannot
express. The extra memory is O(depth), which for real code is tiny.

max_depth is not decoration either. It is the number you need
before you feed this a file you did not write: a nested input that
is 50,000 deep will not overflow this stack, but it will overflow
the recursive parser in Chapter 48, and depth is how you find out
which one you have before it happens in production.
```

Row 2 is the whole point. `([)]` has two opening brackets and two closing brackets, so a counter
says balanced. It is not balanced, and a parser that believes the counter builds a tree with the
wrong shape -- or, more often, does not notice until a much later stage does something strange and
the stack trace points at the wrong file.

The stack gets it right because it stores the *order*. Popping returns the bracket you are inside,
so `stack.pop() != PAIRS[char]` is a comparison a pair of integers cannot express. That is the
general lesson: when the correctness of an algorithm depends on nesting or history, the container
has to hold the history, not a summary of it. Chapter 48 meets this again when recursion does the
same job with the call stack instead of a list.

`max_depth` is not decoration either. It is the number you want before you feed a parser a file you
did not write: an input nested 50,000 deep will not trouble this list, but it will overflow the
recursive version, and measuring depth is how you find out which one you have before production
does.

## Queues and `deque`: two ends, and a middle

`deque` is the right answer to the queue problem, and it is not a drop-in replacement for a list.
Knowing exactly what it gave up is what stops you from making things slower with it.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- what deque gives up to be O(1) at both ends.

The first table is counted rather than timed. CPython's deque is a doubly
linked list of fixed-size blocks, so reaching slot i means walking blocks
from whichever end is nearer -- and that walk can be counted exactly.
"""
from collections import deque

N = 100_000
BLOCK = 64          # CPython's deque block size, in pointers


def hops_to_reach(index):
    """Blocks the interpreter steps through to reach slot i.

    CPython indexes a deque from whichever end is nearer, so the cost is the
    distance to that end divided by the block size. The result is
    arithmetic: it is the same on every machine, and no clock appears.
    """
    if index < 0:
        index += N
    from_left = index // BLOCK
    from_right = (N - 1 - index) // BLOCK
    return min(from_left, from_right)


print("reaching one slot of a deque, by position")
print(f"  {N:,} items, {BLOCK} pointers per block")
print()
print(f"{'position':<18}{'index':>10}{'block hops':>13}")
print("-" * 41)
print(f"{'left end':<18}{0:>10}{hops_to_reach(0):>13,}")
for label, index in (("right end", -1),
                     ("near the right", N - 10),
                     ("a quarter in", N // 4),
                     ("middle", N // 2)):
    print(f"{label:<18}{index:>10}{hops_to_reach(index):>13,}")
print()
print("A deque is not a list with extra methods. It is a doubly linked list")
print("of fixed-size blocks, and that layout is why the two ends are cheap")
print("and the middle is not: reaching the middle of this deque means")
print(f"stepping through {hops_to_reach(N // 2):,} blocks, while reaching either end means stepping")
print("through none. CPython walks from whichever end is nearer, so both")
print("ends and both ends' neighbours are free and the centre is the worst")
print("case.")
print()
print("So `deque` is not a drop-in list replacement. Swap a list for a deque")
print("because you push and pop at the ends, not because it sounds faster.")
print("If your code does `items[i]` in a loop, a deque makes it worse.")
print()
print("What you get for that trade is a ring buffer, and a ring buffer has")
print("a feature a list cannot imitate: a fixed maximum length.")
print()
WINDOW = 5
rolling = deque(maxlen=WINDOW)
print(f"a deque(maxlen={WINDOW}) fed the numbers 1 to 9")
print()
print(f"{'input':>7}   contents")
print("-" * 30)
for value in range(1, 10):
    rolling.append(value)
    print(f"{value:>7}   {list(rolling)}")
print()
print("No eviction code. The deque drops the item at the other end when it")
print("is full, in O(1), and the buffer never grows. The list version of")
print("this is `buf.append(x); del buf[:-5]`, which is correct and which")
print("everyone eventually forgets to write -- at which point the buffer is")
print("unbounded and the memory leak is invisible until it is not.")
print()
print("rotate() is the other one worth knowing. It moves the seam rather")
print("than the data, so rotating by k costs k steps, not n:")
print()
ring = deque("abcdef")
print(f"  starting from  {list(ring)}")
ring.rotate(2)
print(f"  rotate(2)      {list(ring)}")
ring.rotate(-2)
print(f"  rotate(-2)     {list(ring)}")
print()
print("That is how you implement a round-robin scheduler without an index")
print("that has to be taken modulo everywhere it is used.")
```

```text
reaching one slot of a deque, by position
  100,000 items, 64 pointers per block

position               index   block hops
-----------------------------------------
left end                   0            0
right end                 -1            0
near the right         99990            0
a quarter in           25000          390
middle                 50000          781

A deque is not a list with extra methods. It is a doubly linked list
of fixed-size blocks, and that layout is why the two ends are cheap
and the middle is not: reaching the middle of this deque means
stepping through 781 blocks, while reaching either end means stepping
through none. CPython walks from whichever end is nearer, so both
ends and both ends' neighbours are free and the centre is the worst
case.

So `deque` is not a drop-in list replacement. Swap a list for a deque
because you push and pop at the ends, not because it sounds faster.
If your code does `items[i]` in a loop, a deque makes it worse.

What you get for that trade is a ring buffer, and a ring buffer has
a feature a list cannot imitate: a fixed maximum length.

a deque(maxlen=5) fed the numbers 1 to 9

  input   contents
------------------------------
      1   [1]
      2   [1, 2]
      3   [1, 2, 3]
      4   [1, 2, 3, 4]
      5   [1, 2, 3, 4, 5]
      6   [2, 3, 4, 5, 6]
      7   [3, 4, 5, 6, 7]
      8   [4, 5, 6, 7, 8]
      9   [5, 6, 7, 8, 9]

No eviction code. The deque drops the item at the other end when it
is full, in O(1), and the buffer never grows. The list version of
this is `buf.append(x); del buf[:-5]`, which is correct and which
everyone eventually forgets to write -- at which point the buffer is
unbounded and the memory leak is invisible until it is not.

rotate() is the other one worth knowing. It moves the seam rather
than the data, so rotating by k costs k steps, not n:

  starting from  ['a', 'b', 'c', 'd', 'e', 'f']
  rotate(2)      ['e', 'f', 'a', 'b', 'c', 'd']
  rotate(-2)     ['a', 'b', 'c', 'd', 'e', 'f']

That is how you implement a round-robin scheduler without an index
that has to be taken modulo everywhere it is used.
```

The count is blunt: reaching the middle of a hundred-thousand-item deque means stepping through 781
blocks, and reaching either end means stepping through none. That is not a wart, it is the price of the
layout. A deque is a doubly linked list of fixed-size blocks, so reaching index n/2 means walking the
block chain -- and CPython walks from whichever end is nearer, which is why the right end and its
neighbours are as cheap as the left.

So the rule is about access pattern, not about which container is "faster". Swap a list for a deque
because you push and pop at the ends. If your code does `items[i]` in a loop, a deque makes it
worse, and the profiler will not explain why.

What you get in exchange is a ring buffer, and a ring buffer has a property a list cannot imitate: a
fixed maximum length. `deque(maxlen=5)` drops the item at the far end when it fills, in O(1), with
no eviction code. The list equivalent is `buf.append(x); del buf[:-5]`, which is correct, which
everyone eventually forgets to write, and which leaves an unbounded buffer when they do.

## A hash table, written by hand

This is the structure people treat as magic, and it is the one where the magic turns out to be
somewhere unexpected. Twenty lines of Python is enough to see why `dict` is O(1) -- and why that
claim has a precondition.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- a hash table written by hand, so that `dict` stops
being magic.

Everything counted here is a Python-level step: key comparisons and bucket
visits. No timing, so the numbers are exact and machine-independent.
"""
CAPACITY = 256
KEYS = [f"user{i:04d}" for i in range(1_000)]


def hash_by_length(key):
    return len(key)


def hash_by_sum(key):
    return sum(ord(char) for char in key)


def hash_polynomial(key):
    """Multiply by a small prime and add the next character. Two different
    strings almost never land on the same value, which is the property
    `len` does not have."""
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % (2**61 - 1)
    return value


class ChainedTable:
    """A dict is this, in C, with a better hash and no linked tuples."""

    def __init__(self, capacity=CAPACITY, hash_fn=hash_polynomial):
        self.buckets = [[] for _ in range(capacity)]
        self.hash_fn = hash_fn
        self.size = 0
        self.comparisons = 0

    def _bucket(self, key):
        return self.buckets[self.hash_fn(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for index, (existing, _) in enumerate(bucket):
            self.comparisons += 1
            if existing == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        for existing, value in self._bucket(key):
            self.comparisons += 1
            if existing == key:
                return value
        raise KeyError(key)

    def chain_lengths(self):
        return [len(bucket) for bucket in self.buckets]


print(f"{len(KEYS):,} keys, each {len(KEYS[0])} characters long,")
print(f"into {CAPACITY} buckets")
print()
print(f"{'hash function':<20}{'buckets used':>14}{'longest chain':>15}{'lookup cost':>14}")
print("-" * 63)
for label, fn in (("len(key)", hash_by_length),
                  ("sum(ord(c))", hash_by_sum),
                  ("polynomial", hash_polynomial)):
    table = ChainedTable(hash_fn=fn)
    for i, key in enumerate(KEYS):
        table.put(key, i)
    lengths = table.chain_lengths()
    used = sum(1 for length in lengths if length)
    table.comparisons = 0
    for key in KEYS:
        table.get(key)
    print(f"{label:<20}{used:>14}{max(lengths):>15}{table.comparisons / len(KEYS):>14.1f}")
print()
print("'lookup cost' is the mean number of keys compared to find a key that")
print("is definitely in the table -- the best case for a lookup, since every")
print("one of these succeeds.")
print()
print("Read the first row against the third. `len(key)` is a perfectly")
print("deterministic function of the key, and it is useless: every key in")
print("this set has length 8, so every key lands in bucket 8, and the table")
print("is a linked list wearing a hat. The mean lookup compares 500 keys.")
print()
print("`sum(ord(c))` is the interesting row. It is not wrong -- it separates")
print("different keys -- but the sums cluster in a narrow band, so after")
print("`% 256` the keys pile into a handful of buckets. A weak hash does not")
print("produce wrong answers, it produces a table that is quietly slow.")
print()
print("That is the answer to 'why is dict O(1)?' and it is not the table.")
print("The table is twenty lines. The O(1) comes from the hash function")
print("spreading the keys, and from resizing before the chains get long.")
```

```text
1,000 keys, each 8 characters long,
into 256 buckets

hash function         buckets used  longest chain   lookup cost
---------------------------------------------------------------
len(key)                         1           1000         500.5
sum(ord(c))                     28             75          28.1
polynomial                     192             10           4.0

'lookup cost' is the mean number of keys compared to find a key that
is definitely in the table -- the best case for a lookup, since every
one of these succeeds.

Read the first row against the third. `len(key)` is a perfectly
deterministic function of the key, and it is useless: every key in
this set has length 8, so every key lands in bucket 8, and the table
is a linked list wearing a hat. The mean lookup compares 500 keys.

`sum(ord(c))` is the interesting row. It is not wrong -- it separates
different keys -- but the sums cluster in a narrow band, so after
`% 256` the keys pile into a handful of buckets. A weak hash does not
produce wrong answers, it produces a table that is quietly slow.

That is the answer to 'why is dict O(1)?' and it is not the table.
The table is twenty lines. The O(1) comes from the hash function
spreading the keys, and from resizing before the chains get long.
```

Read the first row against the third. `len(key)` is a perfectly deterministic function of the key,
and it is useless: every key in this set has length 8, so every key lands in bucket 8 and the table
is a linked list wearing a hat. A mean lookup compares five hundred keys.

`sum(ord(c))` is the row worth pausing on. It is not *wrong* -- it separates different keys, so
every key is findable. It is merely weak: the sums cluster in a narrow band, and after `% 256` the
keys pile into a few buckets. A weak hash does not produce incorrect answers. It produces a table
that is quietly slow, which is worse, because nothing fails.

So the answer to "why is `dict` O(1)?" is not the table. The table is twenty lines. The O(1) comes
from the hash function scattering the keys, and from resizing before the chains get long. Both
halves matter, and the second one is a number.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- what resizing buys, counted exactly.

Same hash, same keys, same code. The only difference is whether the table
is allowed to grow.
"""
KEY_COUNT = 2_000


def hash_polynomial(key):
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % (2**61 - 1)
    return value


class ChainedTable:
    def __init__(self, capacity=8, grow=True):
        self.buckets = [[] for _ in range(capacity)]
        self.grow = grow
        self.size = 0
        self.comparisons = 0
        self.resizes = 0

    def _bucket(self, key):
        return self.buckets[hash_polynomial(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for index, (existing, _) in enumerate(bucket):
            self.comparisons += 1
            if existing == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        # Load factor 2 is generous. CPython's dict resizes at 2/3.
        if self.grow and self.size > 2 * len(self.buckets):
            self._resize()

    def get(self, key):
        for existing, value in self._bucket(key):
            self.comparisons += 1
            if existing == key:
                return value
        raise KeyError(key)

    def _resize(self):
        pairs = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(len(self.buckets) * 2)]
        self.resizes += 1
        self.size = 0
        for key, value in pairs:
            self.put(key, value)


def hash_table_lookups(key_count):
    """How many keys the hand-written table compares, per successful lookup."""
    table = ChainedTable()
    for i in range(key_count):
        table.put(f"user{i:04d}", i)
    table.comparisons = 0
    for i in range(key_count):
        table.get(f"user{i:04d}")
    return table


def dict_lookups(key_count):
    """The same thing with the built-in. Returns a count we cannot see
    inside -- which is itself the point."""
    table = {}
    for i in range(key_count):
        table[f"user{i:04d}"] = i
    for i in range(key_count):
        table[f"user{i:04d}"]
    return table


print(f"inserting {KEY_COUNT:,} keys, starting from 8 buckets")
print()
print(f"{'table':<26}{'key comparisons':>18}{'per insert':>12}{'resizes':>10}")
print("-" * 66)
for grow, label in ((True, "grows at load factor 2"), (False, "fixed at 8 buckets")):
    table = ChainedTable(grow=grow)
    for i in range(KEY_COUNT):
        table.put(f"user{i:04d}", i)
    print(f"{label:<26}{table.comparisons:>18,}"
          f"{table.comparisons / KEY_COUNT:>12.1f}{table.resizes:>10}")
print()
print("The fixed table is a set of linked lists. With 8 buckets and n keys,")
print("insert number i finds about i/8 keys already in its chain, so the")
print("total is roughly n^2/16 -- for n = 2,000 that predicts 250,000, and")
print("the table reports 249,019. The resize column is what prevents it.")
print()
print("Double the key count and watch which column changes shape.")
print()
print(f"{'keys':>8}{'growing':>14}{'fixed':>14}{'fixed/growing':>16}")
print("-" * 52)
previous = None
for key_count in (500, 1_000, 2_000):
    growing = ChainedTable(grow=True)
    fixed = ChainedTable(grow=False)
    for i in range(key_count):
        growing.put(f"user{i:04d}", i)
        fixed.put(f"user{i:04d}", i)
    row = (growing.comparisons, fixed.comparisons)
    ratio = "" if previous is None else f"{row[1] / previous[1]:>15.1f}x"
    print(f"{key_count:>8,}{row[0]:>14,}{row[1]:>14,}{ratio}")
    previous = row
print()
print("The growing table's column roughly doubles each time. The fixed")
print("table's column multiplies by four. Same code, same keys, same hash")
print("function -- one boolean in the constructor.")
print()
print("lookups on the finished tables")
print()
print(f"{'table':<32}{'comparisons':>14}")
print("-" * 46)
hand = hash_table_lookups(KEY_COUNT)
print(f"{'hand-written, 2,000 keys':<32}{hand.comparisons:>14,}")
print(f"{'built-in dict, 2,000 keys':<32}{'not visible':>14}")
print(f"  mean per lookup                {hand.comparisons / KEY_COUNT:>14.1f}")
print()
print("A dict does not expose a comparison count, and that is not an")
print("oversight -- there is nothing in Python to count. The chains are")
print("arrays of indices inside a C struct, the hash is cached in the")
print("entry, and a probe is a memory read rather than a method call. So")
print("the honest question is not 'which is faster' but 'which complexity")
print("did you choose', and the answer to that is identical for both.")
print()
print("Use dict. Write one once, so you know what you are using.")
```

```text
inserting 2,000 keys, starting from 8 buckets

table                        key comparisons  per insert   resizes
------------------------------------------------------------------
grows at load factor 2                 8,993         4.5         7
fixed at 8 buckets                   249,019       124.5         0

The fixed table is a set of linked lists. With 8 buckets and n keys,
insert number i finds about i/8 keys already in its chain, so the
total is roughly n^2/16 -- for n = 2,000 that predicts 250,000, and
the table reports 249,019. The resize column is what prevents it.

Double the key count and watch which column changes shape.

    keys       growing         fixed   fixed/growing
----------------------------------------------------
     500         1,574        15,384
   1,000         2,992        62,006            4.0x
   2,000         8,993       249,019            4.0x

The growing table's column roughly doubles each time. The fixed
table's column multiplies by four. Same code, same keys, same hash
function -- one boolean in the constructor.

lookups on the finished tables

table                              comparisons
----------------------------------------------
hand-written, 2,000 keys                 7,913
built-in dict, 2,000 keys          not visible
  mean per lookup                           4.0

A dict does not expose a comparison count, and that is not an
oversight -- there is nothing in Python to count. The chains are
arrays of indices inside a C struct, the hash is cached in the
entry, and a probe is a memory read rather than a method call. So
the honest question is not 'which is faster' but 'which complexity
did you choose', and the answer to that is identical for both.

Use dict. Write one once, so you know what you are using.
```

The fixed-capacity table is a set of linked lists, and the arithmetic is worth doing once: with c
buckets and n keys, insert number i finds about i/c keys already in its chain, so the total is
roughly n²/(2c). For n = 2,000 and c = 8 that predicts 250,000, and the table reports 249,019. The
resize column is what prevents it -- seven doublings, and the per-insert cost stays flat.

The doubling table is the growth-rate test from Chapter 44 applied to a container rather than a
loop. The growing column roughly doubles; the fixed column multiplies by four. Same code, same
keys, same hash function, one boolean in the constructor.

The last table is a deliberate disappointment. A `dict` will not tell you how many comparisons it
made, and there is nothing in Python to count -- the chains are arrays of indices inside a C struct,
the hash is cached in the entry, and a probe is a memory read rather than a method call. So the
honest question is not "which is faster" but "which complexity did you choose", and the answer is
identical for both. Use `dict`. Write one once, so you know what you are using.

## Hashes are salted, and that is a feature

One more thing about hashing that you will meet as a bug report rather than a lesson, usually in the
form of "the same script printed a different order today".

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- string hashing is salted per process, and why.

Nothing here prints a hash value. Hash values depend on the Python build and
on the seed, so printing them would be a fact about this laptop rather than
a fact about Python. What is printed is the comparison, which is stable.
"""
import os
import subprocess
import sys

PROGRAM = (
    "keys = [f'user{i:04d}' for i in range(50)]\n"
    "layout = [0] * 8\n"
    "for key in keys:\n"
    "    layout[hash(key) % 8] += 1\n"
    "print(','.join(str(n) for n in layout))\n"
)


def layout_under(seed):
    """Run the same program in a fresh interpreter with a chosen seed."""
    env = dict(os.environ, PYTHONHASHSEED=seed)
    result = subprocess.run(
        [sys.executable, "-c", PROGRAM],
        capture_output=True, text=True, env=env, check=True,
    )
    return result.stdout.strip()


print("the same 50 keys, hashed into 8 buckets, in fresh processes")
print()
print(f"{'comparison':<46}{'identical?':>12}")
print("-" * 58)
runs = {seed: [layout_under(seed) for _ in range(2)] for seed in ("0", "1")}
print(f"{'two runs with seed 0':<46}{str(runs['0'][0] == runs['0'][1]):>12}")
print(f"{'two runs with seed 1':<46}{str(runs['1'][0] == runs['1'][1]):>12}")
print(f"{'one run with seed 0, one with seed 1':<46}{str(runs['0'][0] == runs['1'][0]):>12}")
print()
print("The bucket occupancies themselves are deliberately not printed. They")
print("depend on the Python build as well as the seed, so they would be a")
print("fact about this laptop rather than a fact about Python.")
print()
print("Two runs of the identical program, and the keys land in different")
print("buckets. That is hash randomisation: CPython picks a random salt at")
print("startup and mixes it into the hash of every str and bytes object, so")
print("hash values are not reproducible across processes.")
print()
print("Two consequences you will meet.")
print()
print("The harmless one: iterating a set of strings gives a different order")
print("in a different process. `set` iteration order was never a promise, and")
print("this is why the same script can print a different order tomorrow.")
print("dicts are unaffected, because dicts have kept insertion order since")
print("3.7 -- that is a language guarantee, not a hash property.")
print()
print("The one that matters: without the salt, an attacker who knows the")
print("hash function can choose keys that all collide, and a dict lookup")
print("becomes a linear scan. That is hash flooding, and it turns a JSON")
print("request body into a denial of service. The salt is the fix, and it is")
print("on by default. Chapter 52 comes back to this when it covers untrusted")
print("input -- for now the point is just that `hash()` is not a pure")
print("function of its argument.")
```

```text
the same 50 keys, hashed into 8 buckets, in fresh processes

comparison                                      identical?
----------------------------------------------------------
two runs with seed 0                                  True
two runs with seed 1                                  True
one run with seed 0, one with seed 1                 False

The bucket occupancies themselves are deliberately not printed. They
depend on the Python build as well as the seed, so they would be a
fact about this laptop rather than a fact about Python.

Two runs of the identical program, and the keys land in different
buckets. That is hash randomisation: CPython picks a random salt at
startup and mixes it into the hash of every str and bytes object, so
hash values are not reproducible across processes.

Two consequences you will meet.

The harmless one: iterating a set of strings gives a different order
in a different process. `set` iteration order was never a promise, and
this is why the same script can print a different order tomorrow.
dicts are unaffected, because dicts have kept insertion order since
3.7 -- that is a language guarantee, not a hash property.

The one that matters: without the salt, an attacker who knows the
hash function can choose keys that all collide, and a dict lookup
becomes a linear scan. That is hash flooding, and it turns a JSON
request body into a denial of service. The salt is the fix, and it is
on by default. Chapter 52 comes back to this when it covers untrusted
input -- for now the point is just that `hash()` is not a pure
function of its argument.
```

Two runs of the identical program, and the keys land in different buckets, because CPython picks a
random salt at startup and mixes it into the hash of every `str` and `bytes` object. Hash values are
not reproducible across processes, and no amount of testing will make them so.

The harmless consequence is that iterating a `set` of strings gives a different order in a different
process. `set` iteration order was never a promise; this is the mechanism behind that. `dict`s are
unaffected, because insertion order has been a language guarantee since 3.7 -- a guarantee about
dicts, not a property of hashing.

The consequence that matters is security. Without the salt, an attacker who knows the hash function
can choose keys that all collide, and a dict lookup becomes a linear scan. That is hash flooding, and
it turns a JSON request body into a denial of service. The salt is the fix, and it is on by default.
Chapter 52 returns to this when it covers untrusted input; for now the point is that `hash()` is not
a pure function of its argument, and code that assumes it is has a latent bug.

## Heaps: a structure that answers one question

A heap is the clearest example in the chapter of a structure that is not a general container. It
answers exactly one question, and it answers it faster than anything that answers more.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- what a heap actually buys, counted exactly.

Every comparison a heap makes goes through `<` on the objects it holds, so
wrapping the values in a class with a counting __lt__ turns the algorithm
into a number. That number is the same on every machine and in every run.
"""
import heapq

N = 10_000


class Counted:
    """A value that reports how often it was compared."""

    __slots__ = ("value", "counter")

    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return self.value < other.value

    def __repr__(self):
        return f"Counted({self.value})"


def permutation(n):
    """A fixed, well-mixed order with no randomness in it: multiply by a
    prime coprime to n and take the remainder."""
    return [(i * 7919) % n for i in range(n)]


values = permutation(N)
counter = [0]
items = [Counted(v, counter) for v in values]

heap = list(items)
counter[0] = 0
heapq.heapify(heap)
heapify_cost = counter[0]

counter[0] = 0
pushed = []
for item in items:
    heapq.heappush(pushed, item)
push_cost = counter[0]

counter[0] = 0
drained = []
while pushed:
    drained.append(heapq.heappop(pushed))
pop_cost = counter[0]

counter[0] = 0
ordered = sorted(items)
sort_cost = counter[0]

print(f"{N:,} values, in a fixed scrambled order")
print()
print(f"{'operation':<34}{'comparisons':>14}{'per item':>10}")
print("-" * 58)
print(f"{'heapq.heapify (all at once)':<34}{heapify_cost:>14,}{heapify_cost / N:>10.1f}")
print(f"{'n x heapq.heappush':<34}{push_cost:>14,}{push_cost / N:>10.1f}")
print(f"{'n x heapq.heappop':<34}{pop_cost:>14,}{pop_cost / N:>10.1f}")
print(f"{'sorted (for comparison)':<34}{sort_cost:>14,}{sort_cost / N:>10.1f}")
print()
print("Read the first row against the last. Sorting compares about twelve")
print("times per item, which is log2(10,000) with Timsort's constant folded")
print("in. heapify compares under two -- it is O(n), not O(n log n), because")
print("it sifts down from the middle rather than pushing from the left, and")
print("most of the nodes are near the bottom where a sift is short.")
print()
print("The middle two rows show the other half of the story. Popping every")
print("item is O(log n) each, which is why a heap sort costs what a sort")
print("costs. And a heap built by pushing one item at a time is O(n log n),")
print("worse than heapify on the same data. If you already have all the")
print("items, heapify them.")
print()
print("Now the part that surprises people. The heap is not sorted.")
print()
print(f"{'heap array, first 8':<24}{[item.value for item in heap[:8]]}")
print(f"{'sorted list, first 8':<24}{[item.value for item in ordered[:8]]}")
print(f"{'heap[0] is the minimum':<24}{heap[0].value}")
print()
print("Only the root is guaranteed. The array behind the heap satisfies")
print("`parent <= both children` at every position and nothing else, which")
print("is exactly enough to answer 'what is the smallest?' in O(1) and to")
print("remove it in O(log n) -- and not enough to answer anything else.")
print()
print("That is the trade to remember. A heap answers one question, costs")
print("under two comparisons per item to build, and accepts a new item in")
print("log n. A sorted list answers every question about order, costs")
print("twelve comparisons per item to build, and cannot accept a new item")
print("without paying n shifts for it.")
```

```text
10,000 values, in a fixed scrambled order

operation                            comparisons  per item
----------------------------------------------------------
heapq.heapify (all at once)               16,365       1.6
n x heapq.heappush                        24,662       2.5
n x heapq.heappop                        119,962      12.0
sorted (for comparison)                  120,221      12.0

Read the first row against the last. Sorting compares about twelve
times per item, which is log2(10,000) with Timsort's constant folded
in. heapify compares under two -- it is O(n), not O(n log n), because
it sifts down from the middle rather than pushing from the left, and
most of the nodes are near the bottom where a sift is short.

The middle two rows show the other half of the story. Popping every
item is O(log n) each, which is why a heap sort costs what a sort
costs. And a heap built by pushing one item at a time is O(n log n),
worse than heapify on the same data. If you already have all the
items, heapify them.

Now the part that surprises people. The heap is not sorted.

heap array, first 8     [0, 2, 1, 5, 3, 10, 7, 9]
sorted list, first 8    [0, 1, 2, 3, 4, 5, 6, 7]
heap[0] is the minimum  0

Only the root is guaranteed. The array behind the heap satisfies
`parent <= both children` at every position and nothing else, which
is exactly enough to answer 'what is the smallest?' in O(1) and to
remove it in O(log n) -- and not enough to answer anything else.

That is the trade to remember. A heap answers one question, costs
under two comparisons per item to build, and accepts a new item in
log n. A sorted list answers every question about order, costs
twelve comparisons per item to build, and cannot accept a new item
without paying n shifts for it.
```

Every comparison a heap makes goes through `<` on the objects it holds, which is what makes this
countable. Wrapping the values in a class with a counting `__lt__` turns the algorithm into a number
-- the same number on every machine, in every run.

Sorting compares about twelve times per item, which is log2(10,000) with Timsort's constant folded
in. `heapify` compares under two, because it is O(n) rather than O(n log n): it sifts down from the
middle rather than pushing from the left, and most of the nodes are near the bottom where a sift is
short. Popping every item is O(log n) each, which is why heap sort costs what a sort costs -- and why
a heap built by pushing one item at a time is worse than `heapify` on the same data.

Then the part that surprises people. The heap array is not sorted. Only the root is guaranteed; the
array satisfies `parent <= both children` at every position and nothing else. That is exactly enough
to answer "what is the smallest?" in O(1) and to remove it in O(log n), and not enough to answer
anything else -- you cannot ask for the second smallest without popping the first.

:::tip `heapq` is a min-heap, and the tuple is how you control the order
There is no max-heap in the standard library. For numbers you negate the key. For anything else you
push a tuple and let the comparison stop at the first field that differs -- `(priority, sequence,
item)`, where `sequence` is a counter that makes the order total. Without that middle field, two
items with equal priority make the heap compare the items themselves, and if they are not orderable
you get a `TypeError` from deep inside `heapq` rather than from your code.
:::

## Ordered keys: `bisect`, and the tree it does not replace

Everything so far either keeps no order or keeps a weak one. Keeping full order is the expensive
promise, and the standard library gives you one half of it.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- bisect finds in log n, then pays n to use the answer.

Every number here is exact. The shift count follows from the algorithm, and
the probe counts come from running a binary search and a linear scan over
the real data rather than from timing them.
"""
import bisect

N = 20_000
K = 2_000


def permutation(n):
    return [(i * 7919) % n for i in range(n)]


def shifts_for_insort(n, k):
    """Each insort into a sorted list of length L shifts the elements above
    the insertion point down by one slot. Keys arriving in a scrambled order
    land halfway up on average, so the total is about k*n/2 + k^2/4."""
    return k * n // 2 + k * k // 4


def build_by_insort(n, k):
    buf = sorted(permutation(n))
    for value in permutation(k):
        bisect.insort(buf, value)
    return buf


def build_by_sort(n, k):
    buf = permutation(n) + permutation(k)
    buf.sort()
    return buf


def probes_to_find(sorted_items, target):
    """Binary search, written out so the probe count is visible. This is
    what bisect.bisect_left does; the C version just does it faster."""
    low, high = 0, len(sorted_items)
    probes = 0
    while low < high:
        probes += 1
        middle = (low + high) // 2
        if sorted_items[middle] < target:
            low = middle + 1
        else:
            high = middle
    return probes


def linear_probes(sorted_items, target):
    probes = 0
    for item in sorted_items:
        probes += 1
        if item == target:
            break
    return probes


shifts = shifts_for_insort(N, K)
assert build_by_insort(N, K) == build_by_sort(N, K)

print(f"a sorted list of {N:,}, then adding {K:,} more keys")
print()
print(f"{'approach':<28}{'element shifts':>16}{'per key':>10}")
print("-" * 54)
print(f"{'collect, then sort once':<28}{0:>16,}{0:>10,}")
print(f"{'bisect.insort each key':<28}{shifts:>16,}{shifts // K:>10,}")
print()
print("Both rows end with the same sorted list -- the assert above is the")
print("proof, and it is checked every time this program runs. Only one of")
print("the rows pays a linear cost per key, and the last column is where")
print(f"that shows: {shifts // K:,} slot moves to place one key.")
print()
print("A shift here means an element moving down one slot to make room.")
print("The sort moves nothing in that sense: it copies the elements into a")
print("temporary array and back, which is linear in n once, not linear per")
print("key. That difference is what the two rows are really comparing.")
print()
print("This is not an argument against bisect. bisect is excellent at what")
print("it does, and what it does is *find*. Compare the two searches:")
print()
print(f"{'items':>14}{'linear scan':>16}{'bisect probes':>16}")
print("-" * 46)
largest_scan = largest_probes = 0
for n in (1_000, 100_000, 10_000_000):
    items = list(range(n))
    target = n // 2
    largest_scan = linear_probes(items, target)
    largest_probes = probes_to_find(items, target)
    print(f"{n:>14,}{largest_scan:>16,}{largest_probes:>16}")
print()
print(f"Ten million items, {largest_probes} probes. The scan needs {largest_scan:,}.")
print("That is log2(n) against n, and it is why bisect is the right tool for")
print("rank, thresholds, and 'which band does this value fall in'.")
print()
print("So the rule has two halves and they point opposite ways:")
print()
print("  bisect to FIND.    O(log n), and nothing else comes close.")
print("  do not insort in bulk. O(n) per insert, because the list is an array.")
print()
print("If keys arrive one at a time and the order must be maintained after")
print("every one of them, a sorted list is the wrong structure -- and no")
print("amount of bisect will fix that. You want a balanced tree, which is")
print("logarithmic for both. The next demo builds one.")
```

```text
a sorted list of 20,000, then adding 2,000 more keys

approach                      element shifts   per key
------------------------------------------------------
collect, then sort once                    0         0
bisect.insort each key            21,000,000    10,500

Both rows end with the same sorted list -- the assert above is the
proof, and it is checked every time this program runs. Only one of
the rows pays a linear cost per key, and the last column is where
that shows: 10,500 slot moves to place one key.

A shift here means an element moving down one slot to make room.
The sort moves nothing in that sense: it copies the elements into a
temporary array and back, which is linear in n once, not linear per
key. That difference is what the two rows are really comparing.

This is not an argument against bisect. bisect is excellent at what
it does, and what it does is *find*. Compare the two searches:

         items     linear scan   bisect probes
----------------------------------------------
         1,000             501               9
       100,000          50,001              16
    10,000,000       5,000,001              23

Ten million items, 23 probes. The scan needs 5,000,001.
That is log2(n) against n, and it is why bisect is the right tool for
rank, thresholds, and 'which band does this value fall in'.

So the rule has two halves and they point opposite ways:

  bisect to FIND.    O(log n), and nothing else comes close.
  do not insort in bulk. O(n) per insert, because the list is an array.

If keys arrive one at a time and the order must be maintained after
every one of them, a sorted list is the wrong structure -- and no
amount of bisect will fix that. You want a balanced tree, which is
logarithmic for both. The next demo builds one.
```

Two rows, the same sorted list at the end, and a twenty-one-million-slot difference in how it got
there. The last column is where it shows: 10,500 slot moves to place a single key.

This is not an argument against `bisect`, and the second table says why. Ten million items, twenty-
three probes, against five million for a scan. That is log n against n, and nothing else in the
standard library comes close for the question "where would this value go?". The rule has two halves
that point in opposite directions: **bisect to find**, and **do not insort in bulk**.

If keys arrive one at a time and the order must hold after every one of them, a sorted list is the
wrong structure, and no amount of `bisect` fixes that. You want a balanced tree. So let us build
one, and let the log n claim stop being something you take on faith.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- a balanced tree, so 'log n for both operations' stops
being something you have to take on faith.

An AVL tree keeps the height of the two subtrees at every node within one of
each other, which caps the height at about 1.44*log2(n). The visit counter
is the number of nodes the algorithm looked at, so it is exact.
"""
N = 20_000
K = 2_000


class Node:
    __slots__ = ("key", "left", "right", "height")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1


class AVL:
    """Insert-only, which is all this demo needs. A real one also deletes."""

    def __init__(self):
        self.root = None
        self.size = 0
        self.visits = 0
        self.rotations = 0

    @staticmethod
    def _height(node):
        return node.height if node is not None else 0

    @staticmethod
    def _refresh(node):
        node.height = 1 + max(AVL._height(node.left), AVL._height(node.right))

    def _rotate_left(self, node):
        self.rotations += 1
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        self._refresh(node)
        self._refresh(pivot)
        return pivot

    def _rotate_right(self, node):
        self.rotations += 1
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        self._refresh(node)
        self._refresh(pivot)
        return pivot

    def _rebalance(self, node):
        """After an insert, the two subtrees can differ by at most two.
        One rotation fixes the outside case, two fix the inside case."""
        self._refresh(node)
        balance = self._height(node.left) - self._height(node.right)
        if balance > 1:
            if self._height(node.left.left) < self._height(node.left.right):
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._height(node.right.right) < self._height(node.right.left):
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if node is None:
            self.size += 1
            return Node(key)
        self.visits += 1
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node
        return self._rebalance(node)

    def contains(self, key):
        node = self.root
        while node is not None:
            self.visits += 1
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def height(self):
        return self._height(self.root)


def permutation(n):
    return [(i * 7919) % n for i in range(n)]


def unbalanced_visits(n):
    """What the same inserts cost with no rebalancing at all: keys arriving
    in ascending order make a tree that is really a linked list."""
    visits = 0
    for index in range(n):
        visits += index
    return visits


tree = AVL()
for value in permutation(N):
    tree.insert(value)
insert_visits = tree.visits

tree.visits = 0
for value in permutation(K):
    tree.contains(value)
lookup_visits = tree.visits

print(f"{N:,} keys inserted one at a time, in scrambled order")
print()
print(f"{'measurement':<40}{'value':>12}")
print("-" * 52)
print(f"{'nodes visited while inserting':<40}{insert_visits:>12,}")
print(f"{'  mean per insert':<40}{insert_visits / N:>12.1f}")
print(f"{'rotations performed':<40}{tree.rotations:>12,}")
print(f"{'tree height':<40}{tree.height():>12}")
print(f"{'nodes visited by 2,000 lookups':<40}{lookup_visits:>12,}")
print(f"{'  mean per lookup':<40}{lookup_visits / K:>12.1f}")
print()
print("Thirteen visits per insert on 20,000 keys, against a log2(20,000) of")
print("14.3 -- the tree is behaving like a perfectly balanced one, and the")
print("height column is the proof that this is not luck. An unbalanced tree")
print("built from ascending keys would be 19,999 levels tall and would cost")
print(f"{unbalanced_visits(N):,} visits. The rotations cost almost nothing next to that.")
print()
print("So now the three structures can be compared honestly, on the same")
print("job: keep 20,000 keys available for lookup while 2,000 more arrive.")
print()
print(f"{'structure':<26}{'per insert':>14}{'per lookup':>14}")
print("-" * 54)
print(f"{'sorted list + bisect.insort':<26}{'21M shifts':>14}{'16 probes':>14}")
print(f"{'balanced tree (AVL)':<26}{'~13 visits':>14}{'~13 visits':>14}")
print(f"{'dict':<26}{'1 hash':>14}{'1 hash':>14}")
print()
print("The tree is the only one of the three that is logarithmic for both")
print("and keeps the keys in order. The dict is faster at both operations")
print("and keeps nothing in order. The sorted list is the fastest to search")
print("and the slowest to maintain.")
print()
print("Which one you want is decided by the question you are actually")
print("asking. If you never need 'the keys between 40 and 60', the dict")
print("wins and the tree is a hundred lines of code you did not need. That")
print("is why Python's standard library has no sorted mapping: most of the")
print("code that reaches for one only needed a dict, or a sort at the end.")
```

```text
20,000 keys inserted one at a time, in scrambled order

measurement                                    value
----------------------------------------------------
nodes visited while inserting                261,942
  mean per insert                               13.1
rotations performed                            9,377
tree height                                       18
nodes visited by 2,000 lookups                26,742
  mean per lookup                               13.4

Thirteen visits per insert on 20,000 keys, against a log2(20,000) of
14.3 -- the tree is behaving like a perfectly balanced one, and the
height column is the proof that this is not luck. An unbalanced tree
built from ascending keys would be 19,999 levels tall and would cost
199,990,000 visits. The rotations cost almost nothing next to that.

So now the three structures can be compared honestly, on the same
job: keep 20,000 keys available for lookup while 2,000 more arrive.

structure                     per insert    per lookup
------------------------------------------------------
sorted list + bisect.insort    21M shifts     16 probes
balanced tree (AVL)           ~13 visits    ~13 visits
dict                              1 hash        1 hash

The tree is the only one of the three that is logarithmic for both
and keeps the keys in order. The dict is faster at both operations
and keeps nothing in order. The sorted list is the fastest to search
and the slowest to maintain.

Which one you want is decided by the question you are actually
asking. If you never need 'the keys between 40 and 60', the dict
wins and the tree is a hundred lines of code you did not need. That
is why Python's standard library has no sorted mapping: most of the
code that reaches for one only needed a dict, or a sort at the end.
```

Thirteen visits per insert against a log2(20,000) of 14.3 -- the tree is behaving like a perfectly
balanced one, and the height column is the proof it is not luck. An unbalanced tree built from
ascending keys would be 19,999 levels tall, and the visits to build it would be in the hundreds of
millions. The rotations are what buy that, and there are 9,377 of them.

Now the three structures can be compared on one job -- keep 20,000 keys available while 2,000 more
arrive -- and the comparison is not a ranking. The tree is the only one that is logarithmic for both
operations *and* keeps the keys in order. The dict is faster at both and keeps nothing in order. The
sorted list searches fastest and maintains worst.

Which you want is decided by the question you are actually asking. If you never need "the keys
between 40 and 60", the dict wins and the tree is a hundred lines of code you did not need. That is
why Python has no sorted mapping in the standard library: most code that reaches for one only needed
a dict, or a sort at the end. When you do need one, `sortedcontainers` is a third-party package and
that is a deliberate boundary rather than an omission.

## Tries: when the key is a string

The last structure in the chapter is the one that shows a dict is not the only way to store keys --
and that which key operation you need decides the structure, not the other way round.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- a trie, and the one job it does that a dict cannot.

A dict answers 'is this exact key present'. A trie answers 'which keys start
with this prefix', because the shared prefix is shared *storage* rather than
something you have to search for.
"""
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def vocabulary():
    """2,028 distinct three-letter words: the first two letters run over the
    whole alphabet, the third over just a, b and c."""
    words = []
    for first in LETTERS:
        for second in LETTERS:
            for third in LETTERS[:3]:
                words.append(first + second + third)
    return words


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children = {}
        self.is_word = False


def build(words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
    return root


def count_nodes(root):
    total = 0
    stack = [root]
    while stack:
        total += 1
        stack.extend(stack.pop().children.values())
    return total


def trie_prefix(root, prefix):
    """Walk the prefix, then collect the subtree. Returns (words, visits)."""
    visits = 0
    node = root
    for char in prefix:
        visits += 1
        node = node.children.get(char)
        if node is None:
            return [], visits
    found = []
    stack = [(prefix, node)]
    while stack:
        text, current = stack.pop()
        visits += 1
        if current.is_word:
            found.append(text)
        for char, child in current.children.items():
            stack.append((text + char, child))
    found.sort()
    return found, visits


def scan_prefix(words, prefix):
    """The obvious version: check every word. Counts character comparisons,
    because that is the work, and startswith hides it in C."""
    comparisons = 0
    found = []
    for word in words:
        matched = True
        for index, char in enumerate(prefix):
            comparisons += 1
            if index >= len(word) or word[index] != char:
                matched = False
                break
        if matched:
            found.append(word)
    return found, comparisons


WORDS = vocabulary()
ROOT = build(WORDS)

print(f"a trie over {len(WORDS):,} words")
print()
print(f"{'nodes in the trie':<32}{count_nodes(ROOT):>10,}")
print(f"{'words stored':<32}{len(WORDS):>10,}")
print(f"{'nodes per word':<32}{count_nodes(ROOT) / len(WORDS):>10.2f}")
print()
print("The prefix is stored once. Every word beginning with 'ab' shares the")
print("same two nodes, which is why the node count is 2,731 rather than")
print("three nodes per word.")
print()
print("the same query, asked two ways")
print()
print(f"{'prefix':>8}{'matches':>10}{'trie visits':>14}{'scan comparisons':>18}")
print("-" * 52)
for prefix in ("ab", "xyz", "q", "abc", "zz"):
    trie_words, visits = trie_prefix(ROOT, prefix)
    scan_words, comparisons = scan_prefix(WORDS, prefix)
    assert trie_words == scan_words, prefix
    print(f"{prefix:>8}{len(trie_words):>10}{visits:>14,}{comparisons:>18,}")
print()
print("Both columns find the same words. The scan pays for every word in the")
print("vocabulary; the trie pays for the prefix plus the answers. Watch what")
print("happens to each column as the prefix gets longer and the answer set")
print("gets smaller -- the trie's cost falls with the answer, and the scan's")
print("does not.")
print()
print("That is the property a dict cannot offer. `{'ab': [...]}` would answer")
print("this query in one hash, and would then be wrong the moment the")
print("vocabulary grows, because every prefix has to be enumerated in")
print("advance. A trie derives the answer from the words themselves.")
print()
print("The cost is memory and nothing else. A dict of 2,028 words holds")
print("2,028 keys; this trie holds 2,731 node objects, each with a dict of")
print("its own. For an autocomplete over a million words that is hundreds of")
print("megabytes, and the production answer is a compressed trie or a")
print("sorted array with two bisects -- which is exactly the trade this")
print("chapter keeps making: the fastest structure for the query you have,")
print("at the memory cost you are willing to pay.")
```

```text
a trie over 2,028 words

nodes in the trie                    2,731
words stored                         2,028
nodes per word                        1.35

The prefix is stored once. Every word beginning with 'ab' shares the
same two nodes, which is why the node count is 2,731 rather than
three nodes per word.

the same query, asked two ways

  prefix   matches   trie visits  scan comparisons
----------------------------------------------------
      ab         3             6             2,106
     xyz         0             3             2,109
       q        78           106             2,028
     abc         1             4             2,109
      zz         3             6             2,106

Both columns find the same words. The scan pays for every word in the
vocabulary; the trie pays for the prefix plus the answers. Watch what
happens to each column as the prefix gets longer and the answer set
gets smaller -- the trie's cost falls with the answer, and the scan's
does not.

That is the property a dict cannot offer. `{'ab': [...]}` would answer
this query in one hash, and would then be wrong the moment the
vocabulary grows, because every prefix has to be enumerated in
advance. A trie derives the answer from the words themselves.

The cost is memory and nothing else. A dict of 2,028 words holds
2,028 keys; this trie holds 2,731 node objects, each with a dict of
its own. For an autocomplete over a million words that is hundreds of
megabytes, and the production answer is a compressed trie or a
sorted array with two bisects -- which is exactly the trade this
chapter keeps making: the fastest structure for the query you have,
at the memory cost you are willing to pay.
```

Both columns find the same words. The scan pays for every word in the vocabulary; the trie pays for
the prefix plus the answers. Watch the two columns as the prefix changes: the trie's cost follows the
size of the answer, and the scan's does not move.

That is the property a dict cannot offer. You could precompute `{'ab': [...]}`, and it would answer
this one query in a single hash -- and it would be wrong the moment the vocabulary grows, because
every prefix has to be enumerated in advance. A trie derives the answer from the words themselves.

The cost is memory and nothing else: 2,731 nodes for 2,028 words, each node holding a dict of its
own. For an autocomplete over a million words that is hundreds of megabytes, and the production
answer is a compressed trie or a sorted array with two `bisect` calls -- which is the same trade the
whole chapter keeps making. The fastest structure for the query you have, at the memory you are
willing to pay.

## Choosing, on evidence

One problem, solved with everything above, counted. "Find the ten most common words" is the smallest
problem that needs two structures in sequence: a hash table to count, and something ordered to rank.
The counting is a dict and is not interesting. The ranking is where the choice lives.

```python run
#!/usr/bin/env python3
"""Chapter 45 demo -- one problem, three structures, counted.

'Find the ten most common words' is the smallest problem that needs two data
structures in sequence: a hash table to count, and something ordered to rank.
The counting is a dict; the ranking is the interesting choice.
"""
import heapq
import random
from collections import Counter

TOKENS = 200_000
VOCABULARY = 5_000
TOP = 10


class Counted:
    """A (count, word) pair that reports every comparison made against it."""

    __slots__ = ("count", "word", "counter")

    def __init__(self, count, word, counter):
        self.count = count
        self.word = word
        self.counter = counter

    def __lt__(self, other):
        self.counter[0] += 1
        return (self.count, self.word) < (other.count, other.word)


def corpus():
    """A skewed vocabulary with no randomness in it: word w0000 is the most
    common, w4999 the rarest, and the token order is a fixed permutation."""
    rng = random.Random(0)
    words = [f"w{i:04d}" for i in range(VOCABULARY)]
    weights = [1.0 / (i + 1) for i in range(VOCABULARY)]
    return rng.choices(words, weights=weights, k=TOKENS)


def rank_by_sorting(pairs, counter):
    items = [Counted(count, word, counter) for word, count in pairs]
    ordered = sorted(items, reverse=True)
    return [(item.count, item.word) for item in ordered[:TOP]]


def rank_by_nlargest(pairs, counter):
    items = [Counted(count, word, counter) for word, count in pairs]
    best = heapq.nlargest(TOP, items)
    return [(item.count, item.word) for item in best]


def rank_by_hand(pairs, counter):
    """Keep a heap of the top ten as you go. Same complexity as nlargest,
    written out so the two comparisons per item are visible."""
    items = [Counted(count, word, counter) for word, count in pairs]
    heap = items[:TOP]
    heapq.heapify(heap)
    for item in items[TOP:]:
        if heap[0] < item:
            heapq.heapreplace(heap, item)
    return [(item.count, item.word) for item in sorted(heap, reverse=True)]


text = corpus()
counts = Counter(text)
pairs = list(counts.items())

print(f"{len(text):,} tokens, {len(counts):,} distinct words")
print()
print(f"{'counting':<34}{'steps':>14}")
print("-" * 48)
print(f"{'one dict lookup per token':<34}{len(text):>14,}")
print(f"{'distinct keys after counting':<34}{len(counts):>14,}")
print()
print("Counting is not the interesting part. A dict makes it one hash per")
print("token -- 200,000 steps for 200,000 tokens, and the distinct count")
print("does not change the per-token cost. Ranking is where the choice is.")
print()
print(f"now the top {TOP}, three ways")
print()
print(f"{'approach':<26}{'comparisons':>14}{'per word':>10}")
print("-" * 50)
results = {}
for label, fn in (("sorted() then slice", rank_by_sorting),
                  ("heapq.nlargest", rank_by_nlargest),
                  ("heap of 10, hand-rolled", rank_by_hand)):
    counter = [0]
    results[label] = fn(pairs, counter)
    print(f"{label:<26}{counter[0]:>14,}{counter[0] / len(pairs):>10.1f}")
print()
print("All three return the same answer:", len(set(map(tuple, results.values()))) == 1)
print()
print("the answer")
print("-" * 50)
for count, word in results["heapq.nlargest"]:
    print(f"  {word}  appeared {count:,} times")
print()
print("Sorting compares every word against its neighbours, about eleven")
print("times each, because it is answering a question nobody asked: the")
print("full order of 5,000 words. The heap answers only the question that")
print("was asked -- which ten are largest -- in one comparison per word,")
print("because the heap is never bigger than ten and almost every word")
print("loses to the smallest member on the first try. That is a factor of")
print("ten, for the same answer, from a different structure.")
print()
print("That is the whole chapter in one table. The data structure is not a")
print("container you pick by habit; it is the shape of the question you are")
print("asking, and picking the wrong one means paying for answers you threw")
print("away. Chapter 44 called this the cost model. This is it, applied.")
```

```text
200,000 tokens, 4,994 distinct words

counting                                   steps
------------------------------------------------
one dict lookup per token                200,000
distinct keys after counting               4,994

Counting is not the interesting part. A dict makes it one hash per
token -- 200,000 steps for 200,000 tokens, and the distinct count
does not change the per-token cost. Ranking is where the choice is.

now the top 10, three ways

approach                     comparisons  per word
--------------------------------------------------
sorted() then slice               54,170      10.8
heapq.nlargest                     5,090       1.0
heap of 10, hand-rolled            5,090       1.0

All three return the same answer: True

the answer
--------------------------------------------------
  w0000  appeared 22,191 times
  w0001  appeared 10,891 times
  w0002  appeared 7,482 times
  w0003  appeared 5,493 times
  w0004  appeared 4,310 times
  w0005  appeared 3,682 times
  w0006  appeared 3,202 times
  w0007  appeared 2,758 times
  w0008  appeared 2,410 times
  w0009  appeared 2,151 times

Sorting compares every word against its neighbours, about eleven
times each, because it is answering a question nobody asked: the
full order of 5,000 words. The heap answers only the question that
was asked -- which ten are largest -- in one comparison per word,
because the heap is never bigger than ten and almost every word
loses to the smallest member on the first try. That is a factor of
ten, for the same answer, from a different structure.

That is the whole chapter in one table. The data structure is not a
container you pick by habit; it is the shape of the question you are
asking, and picking the wrong one means paying for answers you threw
away. Chapter 44 called this the cost model. This is it, applied.
```

All three approaches return the same ten words. Sorting compares about eleven times per word,
because it is answering a question nobody asked: the full order of 5,000 words. The heap answers only
the question that was asked, in one comparison per word, because the heap is never larger than ten
and almost every word loses to its smallest member on the first try. A factor of ten, for the same
answer, from a different structure.

That is the chapter in one table. A data structure is not a container you pick by habit; it is the
shape of the question you are asking, and picking the wrong one means paying for answers you throw
away.

:::scenario The recent-events buffer that ate the worker
A log-processing service keeps the last 100 events in memory so the `/status` endpoint can show
recent activity. The first version was written in a hurry:

```python
recent = []

def record(event):
    recent.insert(0, event)
    del recent[100:]
```

It passed every test, because every test recorded a handful of events. In production it recorded
200,000 a day, and the worker's CPU time went up until the container was throttled. Nothing was
wrong in the sense of being incorrect -- the buffer held the right 100 events in the right order --
and the profiler pointed at `record`, which is one `insert` and one `del`.

The other version of this bug is worse. Somebody "fixes" the cost by dropping the `del` line, the
buffer becomes unbounded, and the service now leaks about a hundred megabytes a day. Neither version
is a performance problem in the usual sense; both are the wrong structure for the question.

Here is the cost, counted:

```python run
#!/usr/bin/env python3
"""Chapter 45 scenario -- the 'recent events' buffer that ate the worker.

Both versions keep the last 100 events out of 200,000. The slot-move count
is exact: it is accumulated while the real list version runs, so it is a
fact about the algorithm rather than about one machine's afternoon.
"""
from collections import deque

KEEP = 100
EVENTS = 200_000


def buffer_with_list(events, keep):
    """insert(0, x) shifts the whole buffer up to make room at the front.

    The trimming `del buf[keep:]` deletes from the *end*, so it shifts
    nothing -- which is the one place this program is easy to get wrong.
    """
    buf = []
    moves = 0
    for i in range(events):
        moves += len(buf)          # every item already there moves up one slot
        buf.insert(0, i)
        del buf[keep:]             # a tail deletion moves nothing
    return len(buf), buf[0], moves


def buffer_with_deque(events, keep):
    buf = deque(maxlen=keep)
    for i in range(events):
        buf.appendleft(i)
    return len(buf), buf[0], 0


list_len, list_head, moves = buffer_with_list(EVENTS, KEEP)
deque_len, deque_head, _ = buffer_with_deque(EVENTS, KEEP)
assert (list_len, list_head) == (deque_len, deque_head)

print(f"keeping the last {KEEP} of {EVENTS:,} events")
print()
print(f"{'implementation':<28}{'slot moves':>16}{'per event':>12}")
print("-" * 56)
print(f"{'deque(maxlen=100)':<28}{0:>16,}{0.0:>12.1f}")
print(f"{'list.insert(0, x) + del':<28}{moves:>16,}{moves / EVENTS:>12.1f}")
print()
print("Both buffers end up holding the same 100 events in the same order --")
print("the assert above is the proof, and it is checked on every run. What")
print("differs is the second column, and it is exact: it is accumulated")
print("while the list version runs, so it is a fact about the algorithm and")
print("not about this machine.")
print()
print("Read the last column and the support ticket explains itself. The")
print("list version moves about a hundred slots for every single event, to")
print("keep a buffer of a hundred. Nothing about that number depends on how")
print("fast the machine is, which is why it was still the answer when the")
print("worker melted.")
print()
print("The shape is worth naming. The cost per event is proportional to")
print("`keep`, not to `events`, so making the buffer longer makes every")
print("event more expensive -- and the buffer length is the one thing the")
print("person writing this code thought was free to change.")
print()
print("And the correctness bug is worse than the performance one. `del")
print("buf[100:]` is a line somebody has to remember to write. It is not in")
print("the code path that runs on every event in a test, it is in the one")
print("that only matters after a hundred events, and when it is missing the")
print("buffer is unbounded. maxlen cannot be forgotten, because it is a")
print("property of the object rather than a statement in the loop.")
```

```text
keeping the last 100 of 200,000 events

implementation                    slot moves   per event
--------------------------------------------------------
deque(maxlen=100)                          0         0.0
list.insert(0, x) + del           19,994,950       100.0

Both buffers end up holding the same 100 events in the same order --
the assert above is the proof, and it is checked on every run. What
differs is the second column, and it is exact: it is accumulated
while the list version runs, so it is a fact about the algorithm and
not about this machine.

Read the last column and the support ticket explains itself. The
list version moves about a hundred slots for every single event, to
keep a buffer of a hundred. Nothing about that number depends on how
fast the machine is, which is why it was still the answer when the
worker melted.

The shape is worth naming. The cost per event is proportional to
`keep`, not to `events`, so making the buffer longer makes every
event more expensive -- and the buffer length is the one thing the
person writing this code thought was free to change.

And the correctness bug is worse than the performance one. `del
buf[100:]` is a line somebody has to remember to write. It is not in
the code path that runs on every event in a test, it is in the one
that only matters after a hundred events, and when it is missing the
buffer is unbounded. maxlen cannot be forgotten, because it is a
property of the object rather than a statement in the loop.
```
:::

:::solution The fix
The question is "the last N things", which is a ring buffer, and the standard library has one.

```python
from collections import deque

recent = deque(maxlen=100)

def record(event):
    recent.appendleft(event)
```

Both costs disappear at once, and for different reasons. `appendleft` writes into a slot that
already exists rather than shifting the buffer, so it is O(1). `maxlen` drops the item at the far
end automatically, so there is no eviction line to forget and no way for the buffer to grow.

The counts from the demo above make the first half concrete: 19,994,950 slot moves become zero. The
second half does not show up in a benchmark at all, and it is the more valuable half -- the memory
bound is now a property of the object rather than a statement somebody has to remember to write.
:::

## Key takeaways

- A container is a set of cost promises, not a bag of methods. A list is O(1) to read at any index
  and O(n) to insert at the front; a `deque` is O(1) at both ends and O(n) to read in the middle.
  Neither is "faster".
- State the cost before you measure it. Every count in this chapter is exact and identical on every
  machine; a timing is a property of one machine, which is why none of them are printed here.
- `list.pop(0)` and `list.insert(0, x)` are both O(n) and both look like O(1). Use `deque` when the
  ends are where the traffic is.
- A hash table's O(1) comes from the hash function spreading the keys and from resizing before the
  chains get long. Change either one and you get a linked list with extra steps.
- `hash()` of a string is salted per process. That is why `set` iteration order varies between runs,
  and it is what stops hash-flooding attacks. Never depend on a hash value.
- A heap answers one question -- the minimum -- in O(1) to read and O(log n) to change, and it is not
  sorted. `heapify` is O(n); pushing n items one at a time is O(n log n).
- `bisect` finds in O(log n) and `insort` inserts in O(n), because a list is an array. Find with
  `bisect`; do not maintain a sorted list one insert at a time.
- A trie costs memory and buys prefix queries a dict cannot answer. A balanced tree costs code and
  buys order plus logarithmic updates. The question you are asking picks the structure.

## Practice

- [ ] Build a `MinStack` that supports `push`, `pop` and `minimum`, all in O(1), and check its
  `minimum()` against a full rescan of the stack after every push.
- [ ] Write `merge_sorted(lists)` that merges k sorted lists into one, using a heap that never holds
  more than k items. Compare its output against a plain `sorted()` over everything.
- [ ] Build an `LRUCache` with a size limit, using a `dict` and a doubly linked list. Show the cache
  contents in most-recently-used order after a scripted sequence of `get` and `put` calls.
- [ ] Write `longest_common_prefix(words)` using a trie, and a second version that compares the
  words directly. Check that they agree on a single word, on a set with no shared first character,
  and on repeated words.
- [ ] Write an open-addressed hash table with linear probing. Measure the mean probes per lookup at
  load factors from 0.12 to 0.98, and demonstrate the deletion bug that clearing a slot causes.

## Solutions

:::solution Exercise 1
The trick is a second stack holding the minimum *as it was at each depth*. Each entry is only valid
while the stack is that tall, which is exactly what a stack gives you for free.

```python run
#!/usr/bin/env python3
"""Chapter 45 solution 1 -- a stack that also reports its minimum in O(1)."""
import random


class MinStack:
    """The trick is a second stack that holds the minimum as it was *at each
    depth*. Each entry is only valid while the stack is that tall, which is
    exactly what a stack gives you for free."""

    def __init__(self):
        self._items = []
        self._minimums = []

    def push(self, value):
        self._items.append(value)
        self._minimums.append(
            value if not self._minimums else min(value, self._minimums[-1])
        )

    def pop(self):
        self._minimums.pop()
        return self._items.pop()

    def minimum(self):
        return self._minimums[-1]

    def __len__(self):
        return len(self._items)


def rescan_minimum(stack):
    """The obvious version: look at every item. This is what the second
    stack is buying you out of."""
    return min(stack)


rng = random.Random(0)
values = [rng.randrange(1_000) for _ in range(500)]

stack = MinStack()
pushed = []
agree = True
rescans = 0
for value in values:
    stack.push(value)
    pushed.append(value)
    if stack.minimum() != rescan_minimum(pushed):
        agree = False
        break
    rescans += len(pushed)

print(f"{len(values)} pushes, checking minimum() against a full rescan each time")
print()
print(f"  every minimum agreed with the rescan : {agree}")
print(f"  items rescanned to check them        : {rescans:,}")
print(f"  items the MinStack looked at         : {len(values):,}")
print()
print("The rescan column is O(n) per call and the MinStack column is O(1) per")
print("call, which is the entire point. The second stack costs one extra slot")
print("per push and makes `minimum()` a peek at the top.")
print()
print("Popping is where the design earns its keep. Removing an item does not")
print("invalidate the minimums below it, because each recorded minimum belongs")
print("to a depth rather than to a value. Pop the tall entry and the minimum")
print("of the shorter stack is still sitting underneath, correct and free.")
print()
print("This is the general pattern for 'keep an aggregate that must survive")
print("removal': store the aggregate per depth, per version, or per node, and")
print("let the structure's own ordering do the bookkeeping. The naive")
print("alternative -- recompute the aggregate after every removal -- is O(n)")
print("per operation and is the reason people reach for a tree when a stack")
print("would have done.")
```

```text
500 pushes, checking minimum() against a full rescan each time

  every minimum agreed with the rescan : True
  items rescanned to check them        : 125,250
  items the MinStack looked at         : 500

The rescan column is O(n) per call and the MinStack column is O(1) per
call, which is the entire point. The second stack costs one extra slot
per push and makes `minimum()` a peek at the top.

Popping is where the design earns its keep. Removing an item does not
invalidate the minimums below it, because each recorded minimum belongs
to a depth rather than to a value. Pop the tall entry and the minimum
of the shorter stack is still sitting underneath, correct and free.

This is the general pattern for 'keep an aggregate that must survive
removal': store the aggregate per depth, per version, or per node, and
let the structure's own ordering do the bookkeeping. The naive
alternative -- recompute the aggregate after every removal -- is O(n)
per operation and is the reason people reach for a tree when a stack
would have done.
```
:::

:::solution Exercise 2
Put the head of each list in a heap. Take the smallest, then push the next item from the list it came
from. The heap never holds more than k items, so every step costs log k rather than log of the total.

```python run
#!/usr/bin/env python3
"""Chapter 45 solution 2 -- merging k sorted lists with a heap."""
import heapq


def merge_sorted(lists):
    """Put the head of each list in a heap. Take the smallest, then push the
    next item from the list it came from. The heap never holds more than k
    items, so every step costs log k rather than log of the total."""
    heap = []
    for index, items in enumerate(lists):
        if items:
            heap.append((items[0], index, 0))
    heapq.heapify(heap)

    merged = []
    while heap:
        value, list_index, offset = heapq.heappop(heap)
        merged.append(value)
        offset += 1
        source = lists[list_index]
        if offset < len(source):
            heapq.heappush(heap, (source[offset], list_index, offset))
    return merged


def merge_by_sorting(lists):
    return sorted(value for items in lists for value in items)


LISTS = [
    [0, 6, 12, 18],
    [1, 7, 13, 19],
    [2, 8, 14, 20],
    [3, 9, 15, 21],
    [4, 10, 16, 22],
    [5, 11, 17, 23],
]

merged = merge_sorted(LISTS)
print("six sorted lists")
for index, items in enumerate(LISTS):
    print(f"  list {index}: {items}")
print()
print("merged:")
for start in range(0, len(merged), 12):
    print("   ", merged[start:start + 12])
print()
print("agrees with a plain sort :", merged == merge_by_sorting(LISTS))
print()
print("The tuple is doing work here. `(value, list_index, offset)` never")
print("compares equal on the first element alone, so the heap never has to")
print("compare a list to a list or an index to a value -- the comparison")
print("stops at whichever field settles it. Push bare values instead and the")
print("algorithm breaks on the first tie, with a TypeError rather than a")
print("wrong answer, which is at least the kinder failure.")
print()
print("The cost argument is the reason to do this rather than sort. Sorting")
print("n items from k lists costs n log n. The heap costs n log k, and the")
print("heap is never larger than k. With a hundred thousand items spread over")
print("four lists that is 17 comparisons per item against 2, and with a")
print("million items arriving in two streams it is 20 against 1.")
print()
print("That is the same trade as the top-ten demo: pay for the order you")
print("actually need. Merging k sorted streams needs the order of k things at")
print("a time, not the order of n.")
```

```text
six sorted lists
  list 0: [0, 6, 12, 18]
  list 1: [1, 7, 13, 19]
  list 2: [2, 8, 14, 20]
  list 3: [3, 9, 15, 21]
  list 4: [4, 10, 16, 22]
  list 5: [5, 11, 17, 23]

merged:
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

agrees with a plain sort : True

The tuple is doing work here. `(value, list_index, offset)` never
compares equal on the first element alone, so the heap never has to
compare a list to a list or an index to a value -- the comparison
stops at whichever field settles it. Push bare values instead and the
algorithm breaks on the first tie, with a TypeError rather than a
wrong answer, which is at least the kinder failure.

The cost argument is the reason to do this rather than sort. Sorting
n items from k lists costs n log n. The heap costs n log k, and the
heap is never larger than k. With a hundred thousand items spread over
four lists that is 17 comparisons per item against 2, and with a
million items arriving in two streams it is 20 against 1.

That is the same trade as the top-ten demo: pay for the order you
actually need. Merging k sorted streams needs the order of k things at
a time, not the order of n.
```
:::

:::solution Exercise 3
A dict for the lookup, a doubly linked list for the order. Neither one alone can do both jobs: the
dict cannot tell you the oldest key without scanning, and the list cannot find a key without walking.

```python run
#!/usr/bin/env python3
"""Chapter 45 solution 3 -- an LRU cache, which needs two structures at once."""


class Node:
    """A doubly linked node, because eviction has to unlink from the middle
    of the recency order and a singly linked node cannot do that."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """A dict for the lookup, a doubly linked list for the order. Neither one
    alone can do both jobs: the dict cannot tell you the oldest key without
    scanning, and the list cannot find a key without walking."""

    def __init__(self, capacity):
        self.capacity = capacity
        self.index = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.lookups = 0
        self.relinks = 0

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self.relinks += 2

    def _push_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.relinks += 4

    def get(self, key):
        self.lookups += 1
        node = self.index.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key, value):
        self.lookups += 1
        node = self.index.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return None
        if len(self.index) >= self.capacity:
            oldest = self.tail.prev
            self._unlink(oldest)
            del self.index[oldest.key]
        node = Node(key, value)
        self.index[key] = node
        self._push_front(node)
        return None

    def order(self):
        """Most recently used first, for the tests to read."""
        out = []
        node = self.head.next
        while node is not self.tail:
            out.append(node.key)
            node = node.next
        return out


cache = LRUCache(capacity=3)
SCRIPT = [
    ("put", "a", 1),
    ("put", "b", 2),
    ("put", "c", 3),
    ("get", "a", None),
    ("put", "d", 4),
    ("get", "b", None),
    ("get", "a", None),
    ("put", "e", 5),
]

print("a cache of 3, given this sequence")
print()
print(f"{'operation':<16}{'result':>10}   keys, most recent first")
print("-" * 56)
for action, key, value in SCRIPT:
    if action == "put":
        cache.put(key, value)
        shown = f"put {key}={value}"
        result = "-"
    else:
        found = cache.get(key)
        shown = f"get {key}"
        result = "None" if found is None else str(found)
    print(f"{shown:<16}{result:>10}   {cache.order()}")
print()
print(f"dict lookups: {cache.lookups}   pointer rewires: {cache.relinks}")
print()
print("Every operation is O(1) and the counters show why. `get` is one dict")
print("lookup to find the node, then four pointer writes to move it to the")
print("front. Eviction is one dict delete and two pointer writes, because")
print("`tail.prev` is the least recently used node -- no scan, no timestamp")
print("comparison, no sorting.")
print()
print("The doubly linked part is not decoration. Unlinking a node needs")
print("`node.prev`, and a singly linked list has no way to reach it. That is")
print("the whole reason this structure is doubly linked: the access pattern")
print("is 'remove from the middle, insert at the front', and only a doubly")
print("linked list does both in constant time.")
print()
print("Chapter 18 used `functools.lru_cache`, which does exactly this in C.")
print("You do not need to write it. You need to know that a cache with a")
print("size limit is two structures holding the same objects for two")
print("different questions, because that shape recurs everywhere: an index")
print("and a journal, a lookup table and an ordering, a dict and a heap.")
```

```text
a cache of 3, given this sequence

operation           result   keys, most recent first
--------------------------------------------------------
put a=1                  -   ['a']
put b=2                  -   ['b', 'a']
put c=3                  -   ['c', 'b', 'a']
get a                    1   ['a', 'c', 'b']
put d=4                  -   ['d', 'a', 'c']
get b                 None   ['d', 'a', 'c']
get a                    1   ['a', 'd', 'c']
put e=5                  -   ['e', 'a', 'd']

dict lookups: 8   pointer rewires: 36

Every operation is O(1) and the counters show why. `get` is one dict
lookup to find the node, then four pointer writes to move it to the
front. Eviction is one dict delete and two pointer writes, because
`tail.prev` is the least recently used node -- no scan, no timestamp
comparison, no sorting.

The doubly linked part is not decoration. Unlinking a node needs
`node.prev`, and a singly linked list has no way to reach it. That is
the whole reason this structure is doubly linked: the access pattern
is 'remove from the middle, insert at the front', and only a doubly
linked list does both in constant time.

Chapter 18 used `functools.lru_cache`, which does exactly this in C.
You do not need to write it. You need to know that a cache with a
size limit is two structures holding the same objects for two
different questions, because that shape recurs everywhere: an index
and a journal, a lookup table and an ordering, a dict and a heap.
```
:::

:::solution Exercise 4
Walk down the trie while there is exactly one way to go and no word has ended. Both conditions
matter: a word ending here means it is itself the common prefix, and two children means the paths
have diverged.

```python run
#!/usr/bin/env python3
"""Chapter 45 solution 4 -- longest common prefix, which is what a trie is for."""


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children = {}
        self.is_word = False


def build(words):
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_word = True
    return root


def longest_common_prefix(words):
    """Walk down the trie while there is exactly one way to go and no word
    has ended. Both conditions matter: a word ending here means it is itself
    the common prefix, and two children means the paths have diverged."""
    if not words:
        return ""
    root = build(words)
    prefix = []
    node = root
    while len(node.children) == 1 and not node.is_word:
        char, node = next(iter(node.children.items()))
        prefix.append(char)
    return "".join(prefix)


def longest_common_prefix_by_scan(words):
    """The version everyone writes first. Compare the first word against
    every other word, character by character, and keep the shortest match."""
    if not words:
        return ""
    first = words[0]
    for position, char in enumerate(first):
        for word in words[1:]:
            if position >= len(word) or word[position] != char:
                return first[:position]
    return first


CASES = [
    ["flower", "flow", "flight"],
    ["interview", "internet", "internal"],
    ["dog", "cat", "bird"],
    ["prefix"],
    ["apple", "apple", "apple"],
    ["", "b"],
    ["ab", "abc", "abcd", "abcde"],
]

print("longest common prefix of each set")
print()
print(f"{'words':<44}{'trie':>10}{'scan':>10}  {'agree':>6}")
print("-" * 72)
for words in CASES:
    trie_answer = longest_common_prefix(words)
    scan_answer = longest_common_prefix_by_scan(words)
    shown = str(words)
    if len(shown) > 42:
        shown = shown[:39] + "..."
    print(f"{shown:<44}{trie_answer!r:>10}{scan_answer!r:>10}"
          f"  {str(trie_answer == scan_answer):>6}")
print()
print("The two agree on every case, including the awkward ones: a single")
print("word (the whole word), a set with no shared first character (the empty")
print("string), and repeated words (again the whole word).")
print()
print("The trie wins on cost, not on correctness. The scan compares the first")
print("word against all the others, so it costs up to n * L character")
print("comparisons for n words of length L. The trie costs the length of the")
print("answer, because the answer *is* the path -- it never looks at the")
print("words at all, only at the shape of the tree they built.")
print()
print("There is a second reason to prefer it that has nothing to do with")
print("speed. The scan needs the first word to be the one that defines the")
print("answer; give it a set where the first word is the odd one out and it")
print("returns immediately with an empty string, which happens to be right,")
print("but for the wrong reason. The trie has no such dependence on the input")
print("order, and code that does not depend on input order is code that does")
print("not break when someone sorts the list.")
```

```text
longest common prefix of each set

words                                             trie      scan   agree
------------------------------------------------------------------------
['flower', 'flow', 'flight']                      'fl'      'fl'    True
['interview', 'internet', 'internal']          'inter'   'inter'    True
['dog', 'cat', 'bird']                              ''        ''    True
['prefix']                                    'prefix'  'prefix'    True
['apple', 'apple', 'apple']                    'apple'   'apple'    True
['', 'b']                                           ''        ''    True
['ab', 'abc', 'abcd', 'abcde']                    'ab'      'ab'    True

The two agree on every case, including the awkward ones: a single
word (the whole word), a set with no shared first character (the empty
string), and repeated words (again the whole word).

The trie wins on cost, not on correctness. The scan compares the first
word against all the others, so it costs up to n * L character
comparisons for n words of length L. The trie costs the length of the
answer, because the answer *is* the path -- it never looks at the
words at all, only at the shape of the tree they built.

There is a second reason to prefer it that has nothing to do with
speed. The scan needs the first word to be the one that defines the
answer; give it a set where the first word is the odd one out and it
returns immediately with an empty string, which happens to be right,
but for the wrong reason. The trie has no such dependence on the input
order, and code that does not depend on input order is code that does
not break when someone sorts the list.
```
:::

:::solution Exercise 5
Chaining puts several keys in one bucket; open addressing puts one key per slot and probes forward
when the slot is taken. The probe counts show where "expected O(1)" stops being true, and the
deletion case shows why a sentinel is required.

```python run
#!/usr/bin/env python3
"""Chapter 45 solution 5 -- open addressing, its precondition, and its bug.

Chaining puts several keys in one bucket. Open addressing puts one key per
slot and probes forward when the slot is taken. Both are O(1) while the table
is not too full -- and 'not too full' is a number, which this measures.
"""
CAPACITY = 1024
MASK = (1 << 64) - 1
TOMBSTONE = object()


def hash_plain(key):
    value = 0
    for char in key:
        value = (value * 31 + ord(char)) % (2**61 - 1)
    return value


def hash_mixed(key):
    """The same polynomial, then an avalanche step. A hash only has to be
    injective to be correct, and it has to be *spread out* to be fast."""
    value = hash_plain(key)
    value ^= value >> 33
    value = (value * 0xFF51AFD7ED558CCD) & MASK
    value ^= value >> 33
    return value


class OpenTable:
    """Linear probing: if the slot is taken, try the next one."""

    def __init__(self, capacity=CAPACITY, hash_fn=hash_mixed):
        self.slots = [None] * capacity
        self.hash_fn = hash_fn
        self.size = 0
        self.probes = 0

    def put(self, key, value):
        index = self.hash_fn(key) % len(self.slots)
        while True:
            entry = self.slots[index]
            if entry is None or entry is TOMBSTONE:
                self.slots[index] = (key, value)
                self.size += 1
                return
            self.probes += 1
            if entry[0] == key:
                self.slots[index] = (key, value)
                return
            index = (index + 1) % len(self.slots)

    def get(self, key):
        index = self.hash_fn(key) % len(self.slots)
        while True:
            entry = self.slots[index]
            if entry is None:
                return None
            self.probes += 1
            if entry is not TOMBSTONE and entry[0] == key:
                return entry[1]
            index = (index + 1) % len(self.slots)


def mean_probe(key_count, hash_fn):
    table = OpenTable(hash_fn=hash_fn)
    for i in range(key_count):
        table.put(f"user{i:05d}", i)
    table.probes = 0
    for i in range(key_count):
        table.get(f"user{i:05d}")
    return table.probes / key_count


print("first, the hash function itself")
print()
print("  the keys are user00000, user00001, user00002, ... -- consecutive")
print("  integers, which is the most common shape a real key has.")
print()
print(f"{'keys':>8}{'load':>8}{'plain polynomial':>20}{'with avalanche':>18}")
print("-" * 54)
for key_count in (128, 512, 922):
    load = key_count / CAPACITY
    print(f"{key_count:>8,}{load:>8.2f}{mean_probe(key_count, hash_plain):>20.2f}"
          f"{mean_probe(key_count, hash_mixed):>18.2f}")
print()
print("The plain polynomial hash is injective -- it gives different answers")
print("for different keys -- and it is terrible here. Consecutive keys differ")
print("in their last character only, so their hash values differ by 1, and")
print("modulo 1024 that puts them in *consecutive* slots. Linear probing")
print("turns that into one long run, and a lookup for the last key in the")
print("run walks the whole thing. A hash does not only have to be correct;")
print("it has to scatter, and the avalanche step is what scatters it.")
print()
print("Now the load factor, with the good hash.")
print()
print(f"{'keys':>8}{'load factor':>14}{'mean probes per lookup':>24}")
print("-" * 46)
for key_count in (128, 256, 512, 768, 922, 1_000):
    print(f"{key_count:>8,}{key_count / CAPACITY:>14.2f}"
          f"{mean_probe(key_count, hash_mixed):>24.2f}")
print()
print("This is the textbook curve. Up to a load factor of about 0.75 a")
print("successful lookup costs about three probes or fewer, and then it")
print("climbs. At 0.98 the table has almost no empty slot left to stop a")
print("probe run, and the cost is twenty-five.")
print()
print("That cliff is why CPython's dict resizes at a load factor of 2/3, and")
print("it is why 'expected O(1)' has a precondition attached. The notation")
print("hides the precondition; the table does not.")
print()
print("Now the bug. Deletion in an open-addressed table cannot just clear the")
print("slot, because an empty slot is how a probe run knows to stop.")
print()
small = OpenTable(capacity=8, hash_fn=lambda key: 0)
for key in ("aa", "bb", "cc"):
    small.put(key, key.upper())
print(f"  slots after putting aa, bb, cc : {[e[0] if e else None for e in small.slots[:4]]}")
small.slots[1] = None
print(f"  after deleting bb by clearing it : {[e[0] if e else None for e in small.slots[:4]]}")
print(f"  get('cc')                       : {small.get('cc')}")
print()
print("All three keys hash to slot 0, so they were placed in slots 0, 1 and")
print("2. `cc` is still sitting in slot 2, untouched -- and the lookup for it")
print("stops at the hole in slot 1 and reports the key as absent. A cache")
print("that reports a hit as a miss is not a slow cache, it is a wrong one,")
print("and the failure is invisible until keys collide, which in a test with")
print("ten keys they usually do not.")
print()
print("The fix is a sentinel: a deleted slot is marked rather than cleared,")
print("so a probe run walks past it, and only a genuinely empty slot ends the")
print("run. That sentinel is why the class above tests for TOMBSTONE as well")
print("as None. It is also why the standard library's dict is not something")
print("to reimplement in order to save an import.")
```

```text
first, the hash function itself

  the keys are user00000, user00001, user00002, ... -- consecutive
  integers, which is the most common shape a real key has.

    keys    load    plain polynomial    with avalanche
------------------------------------------------------
     128    0.12                1.55              1.14
     512    0.50               41.64              1.67
     922    0.90              115.61             10.44

The plain polynomial hash is injective -- it gives different answers
for different keys -- and it is terrible here. Consecutive keys differ
in their last character only, so their hash values differ by 1, and
modulo 1024 that puts them in *consecutive* slots. Linear probing
turns that into one long run, and a lookup for the last key in the
run walks the whole thing. A hash does not only have to be correct;
it has to scatter, and the avalanche step is what scatters it.

Now the load factor, with the good hash.

    keys   load factor  mean probes per lookup
----------------------------------------------
     128          0.12                    1.14
     256          0.25                    1.34
     512          0.50                    1.67
     768          0.75                    3.01
     922          0.90                   10.44
   1,000          0.98                   24.87

This is the textbook curve. Up to a load factor of about 0.75 a
successful lookup costs about three probes or fewer, and then it
climbs. At 0.98 the table has almost no empty slot left to stop a
probe run, and the cost is twenty-five.

That cliff is why CPython's dict resizes at a load factor of 2/3, and
it is why 'expected O(1)' has a precondition attached. The notation
hides the precondition; the table does not.

Now the bug. Deletion in an open-addressed table cannot just clear the
slot, because an empty slot is how a probe run knows to stop.

  slots after putting aa, bb, cc : ['aa', 'bb', 'cc', None]
  after deleting bb by clearing it : ['aa', None, 'cc', None]
  get('cc')                       : None

All three keys hash to slot 0, so they were placed in slots 0, 1 and
2. `cc` is still sitting in slot 2, untouched -- and the lookup for it
stops at the hole in slot 1 and reports the key as absent. A cache
that reports a hit as a miss is not a slow cache, it is a wrong one,
and the failure is invisible until keys collide, which in a test with
ten keys they usually do not.

The fix is a sentinel: a deleted slot is marked rather than cleared,
so a probe run walks past it, and only a genuinely empty slot ends the
run. That sentinel is why the class above tests for TOMBSTONE as well
as None. It is also why the standard library's dict is not something
to reimplement in order to save an import.
```
:::
