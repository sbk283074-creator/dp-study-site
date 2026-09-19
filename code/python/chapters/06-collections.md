---
chapter: 6
part: 1
title: Lists, Tuples, Dicts & Sets
summary: Store and reshape real collections of data, pick the right container for the job, and avoid the aliasing and sorting traps that cost beginners hours.
minutes: 45
tags: [list, tuple, dict, set, collections]
---

Four chapters in you can hold one value in a variable. Real programs never do. A to-do app holds
many tasks, an API response is a bag of named fields, a game holds hundreds of sprites. Python
gives you four built-in containers for that, and choosing correctly between them is the
difference between ten lines of clear code and fifty lines of fighting your own data structure.
This chapter covers all four, plus the `collections` module that finishes the job.

## Lists: the ordered workhorse

You need a sequence of things that can grow, shrink, and change. That's a list.

```python
tasks = ["write chapter", "review PR", "ship build"]
numbers = [4, 8, 15, 16, 23, 42]
mixed = ["ada", 36, True]          # legal, rarely wise
empty = []
```

Indexing starts at zero, and negative indices count from the end. Slicing takes
`[start:stop:step]` where `stop` is **exclusive** — the same half-open rule you met with `range()`
in Chapter 4.

```python
>>> tasks[0]
'write chapter'
>>> tasks[-1]
'ship build'
>>> numbers[1:4]
[8, 15, 16]
>>> numbers[:3]
[4, 8, 15]
>>> numbers[::2]
[4, 15, 23]
>>> numbers[::-1]
[42, 23, 16, 15, 8, 4]
```

### The methods that matter

```python
>>> tasks = ["write chapter", "review PR"]
>>> tasks.append("ship build")          # add one item to the end
>>> tasks.extend(["clean up", "rest"])  # add every item from another iterable
>>> tasks.insert(1, "urgent: coffee")   # insert at a position
>>> tasks.remove("clean up")            # delete the first matching *value*
>>> last = tasks.pop()                  # remove and return the last item
>>> tasks.pop(0)                        # remove and return item at index 0
>>> tasks.index("review PR")
1
>>> len(tasks)
3
```

The distinction beginners blur: `append` adds **one element**, `extend` adds **several**.
`append([1, 2])` puts a list *inside* your list; `extend([1, 2])` puts two numbers in it.

### `sort()` versus `sorted()`

`sort()` mutates the list and returns `None`. `sorted()` leaves the original alone and returns a
new sorted list. Both accept `key=` (a function applied to each item to decide its ranking) and
`reverse=True`.

```python
>>> names = ["ada", "Grace", "linus", "Barbara"]
>>> sorted(names)                          # default: by character code, so capitals first
['Barbara', 'Grace', 'ada', 'linus']
>>> sorted(names, key=str.lower)           # case-insensitive
['ada', 'Barbara', 'Grace', 'linus']
>>> sorted(names, key=len)                 # shortest first
['ada', 'Grace', 'linus', 'Barbara']
>>> names
['ada', 'Grace', 'linus', 'Barbara']      # untouched

>>> numbers = [4, 8, 15, 16, 23, 42]
>>> numbers.sort(reverse=True)
>>> numbers
[42, 23, 16, 15, 8, 4]
```

`key=` is the power move. Sorting a list of dicts is `key=lambda row: row["created_at"]`, and
sorting by two criteria is `key=lambda r: (r["team"], r["score"])`.

:::pitfall `x = x.sort()` destroys your data
`list.sort()` returns `None` because it modifies in place. So `x = x.sort()` sets `x` to `None`
and your list is gone — silently, with no error. The same trap exists for `append`, `insert`,
`remove`, `reverse`, and `clear`. If you want a sorted *copy*, write `x = sorted(x)`. Rule of
thumb: if a list method returns `None`, it changed the list; if it returns something, it gave you
a new value.
:::

### The aliasing trap

Assignment never copies. It binds a second name to the same object.

```python
>>> a = [1, 2, 3]
>>> b = a          # b is another name for the SAME list
>>> b.append(4)
>>> a
[1, 2, 3, 4]       # a changed too
```

This bites hard when you pass a list into a function and the function mutates it — the caller's
list changes. To actually copy:

```python
>>> b = list(a)      # or a.copy(), or a[:] — all make a shallow copy
>>> b.append(99)
>>> a
[1, 2, 3, 4]
```

:::pitfall Shallow copies do not copy the inside
`list(a)`, `a.copy()`, and `a[:]` copy only the outer container. If the list holds other lists or
dicts, those inner objects are still shared:

```python
>>> matrix = [[1, 2], [3, 4]]
>>> copy = matrix.copy()
>>> copy[0].append(99)
>>> matrix
[[1, 2, 99], [3, 4]]       # the original changed
```

Use `copy.deepcopy()` when the structure is nested. It is slower, so only reach for it when you
genuinely have nested mutables.
:::

## Tuples: frozen sequences and lightweight records

A tuple is a list you promise not to change. Write it with parentheses (or with no brackets at
all — the comma makes the tuple, not the parens).

```python
>>> point = (3, 4)
>>> point[0] = 99
TypeError: 'tuple' object does not support item assignment
```

That immutability buys you three things:

1. **Packing and unpacking.** Multiple assignment is tuple packing and unpacking wearing a
   disguise.
   ```python
   >>> name, age = ("ada", 36)        # unpack
   >>> name, age = age, name          # swap, no temp variable
   >>> first, *rest = [1, 2, 3, 4]    # starred unpacking
   >>> rest
   [2, 3, 4]
   ```
2. **Records without a class.** `("ada", 36, "London")` is a cheap three-field row. Chapter 13
   replaces these with dataclasses when the shape gets complicated; until then, tuples are fine.
3. **Dict keys.** Only *hashable* objects can be keys, and hashable means immutable. A tuple of
   coordinates is a perfect key: `grid[(x, y)] = "wall"`. A list cannot be a key.

:::note Single-element tuples need the comma
`(1)` is just the integer `1`. `(1,)` is a one-element tuple. The comma is not optional, and
forgetting it is a classic source of "why is this an int?" bugs.
:::

## Dicts: look up by name, not by position

You need to find a value by a label — a username, an ID, a config key — rather than by index.
That's a dict: unordered-in-principle pairs of key and value, with O(1) lookup.

```python
>>> user = {"name": "ada", "age": 36, "active": True}
>>> user["name"]
'ada'
>>> user["country"]                 # missing key
KeyError: 'country'
>>> user.get("country", "unknown")  # missing key, with a default
'unknown'
>>> user["country"] = "UK"          # insert or overwrite
```

Use `[]` when a missing key is a bug you want to hear about. Use `get()` when absence is a normal,
expected outcome. That single distinction makes your intentions readable.

### The methods worth memorising

```python
>>> counts = {}
>>> for word in ["red", "blue", "red", "green"]:
...     counts[word] = counts.get(word, 0) + 1
...
>>> counts
{'red': 2, 'blue': 1, 'green': 1}

>>> counts.setdefault("yellow", 0)   # set if absent, return the value either way
0
>>> counts.update({"blue": 5, "black": 1})
>>> counts.pop("green")
1
```

`setdefault` is the idiom for building a dict of lists:
`buckets.setdefault(team, []).append(player)`.

### Iteration and ordering

```python
>>> for key in user:              # keys, the default
...     print(key)
>>> for value in user.values():
...     print(value)
>>> for key, value in user.items():   # the one you will use most
...     print(f"{key} = {value}")
```

Since Python 3.7 dicts **guarantee insertion order** — items come out in the order you put them
in. Treat it as guaranteed, not accidental; JSON round-trips and config files depend on it.

A dict comprehension builds one in a single expression (Chapter 7 goes deep on comprehensions):

```python
>>> {name: len(name) for name in ["ada", "grace", "linus"]}
{'ada': 3, 'grace': 5, 'linus': 5}
```

What can be a key? Anything **hashable**: strings, numbers, booleans (careful — `1`, `1.0`, and
`True` all hash equal), tuples of hashables, `frozenset`. Not lists, dicts, or sets.

## Sets: uniqueness and instant membership

You need to throw away duplicates, or ask "have I seen this before?" a million times. That's a
set: unordered, unique, and blindingly fast at `in` — a set membership check is roughly constant
time no matter how big it gets, while a list check scans every element.

```python
>>> tags = {"python", "web", "python", "game"}
>>> sorted(tags)
['game', 'python', 'web']
>>> "sql" in tags
False
>>> sorted(set([1, 2, 2, 3, 3, 3]))
[1, 2, 3]
```

Set algebra maps directly onto real questions:

```python
>>> python_devs = {"ada", "grace", "linus"}
>>> game_devs = {"linus", "margaret"}
>>> sorted(python_devs | game_devs)          # union — everyone
['ada', 'grace', 'linus', 'margaret']
>>> python_devs & game_devs                  # intersection — both
{'linus'}
>>> sorted(python_devs - game_devs)          # difference — in the first only
['ada', 'grace']
>>> sorted(python_devs ^ game_devs)          # symmetric difference — exactly one
['ada', 'grace', 'margaret']
>>> python_devs <= {"ada", "grace", "linus", "alan"}   # subset
True
```

:::note Set display order is arbitrary
A set has no order, and the order you see when you print one depends on hash values — which Python
randomises per process for strings. Run the same snippet twice and you may get two different
printouts. Never rely on it: wrap the result in `sorted()` whenever you need stable, readable
output, and remember that a set is the wrong tool if order is part of your answer.
:::

Each has a named method too: `.union()`, `.intersection()`, `.difference()`,
`.symmetric_difference()`. The operators require sets on both sides; the methods accept any
iterable and convert it for you.

Use `set()` for an empty set — `{}` is an empty dict. A `frozenset` is an immutable set, which
means it is hashable and can be used as a dict key or stored inside another set.

## Which collection should I use?

| I need to... | Use | Why |
| --- | --- | --- |
| Keep items in order, change them later | `list` | Indexed, mutable, ordered |
| Keep a fixed group / use as a dict key | `tuple` | Immutable and hashable |
| Look up a value by a label | `dict` | O(1) lookup by key |
| Remove duplicates, test membership fast | `set` | O(1) `in`, no duplicates |
| Count occurrences | `Counter` | Built for exactly that |
| Group items under a key that may not exist | `defaultdict(list)` | No `if key not in d` boilerplate |
| Add/remove at both ends | `deque` | O(1) at the front, unlike a list |
| A tiny named record | `namedtuple` | Readable fields, tuple behaviour |

## The `collections` module

```python
from collections import Counter, defaultdict, deque, namedtuple

# Counter — tally anything
>>> Counter("mississippi").most_common(2)
[('i', 4), ('s', 4)]

# defaultdict — a factory for missing keys
>>> by_team = defaultdict(list)
>>> for name, team in [("ada", "red"), ("bob", "blue"), ("cy", "red")]:
...     by_team[team].append(name)
...
>>> dict(by_team)
{'red': ['ada', 'cy'], 'blue': ['bob']}

# deque — a queue or stack that does not slow down at the front
>>> q = deque(["a", "b"], maxlen=3)
>>> q.append("c"); q.append("d")
>>> q
deque(['b', 'c', 'd'], maxlen=3)     # the oldest fell off the left
>>> q.popleft()
'b'

# namedtuple — a tuple with names
>>> Point = namedtuple("Point", ["x", "y"])
>>> p = Point(3, 4)
>>> p.x, p.y
(3, 4)
>>> p._replace(x=10)
Point(x=10, y=4)
```

`deque.popleft()` is the one to remember: `list.pop(0)` forces Python to shift every remaining
element left, which is slow in a loop.

## Nested structures

Real data is stacked: a list of dicts from an API, a dict of lists grouped by category, a dict of
dicts for configuration.

```python
users = [
    {"name": "ada", "team": "platform", "commits": 142},
    {"name": "grace", "team": "platform", "commits": 88},
    {"name": "linus", "team": "tools", "commits": 231},
]

total = sum(u["commits"] for u in users)
top = max(users, key=lambda u: u["commits"])
names_by_team = {}
for u in users:
    names_by_team.setdefault(u["team"], []).append(u["name"])

print(total, top["name"], names_by_team)
```

```text
461 linus {'platform': ['ada', 'grace'], 'tools': ['linus']}
```

Read nested access left to right: `users[0]["name"]` means "the first user, then their name".
When a nested structure gets three levels deep, that is the signal to reach for a dataclass in
Chapter 13.

:::scenario A deployment report is wrong and nobody knows why
Your team's release script builds a summary of which services deployed, kept in a dict of lists
keyed by environment. Someone adds a "retry" step and suddenly the staging list contains services
that were never deployed to staging. The bug survived two code reviews.
:::

:::solution It is the aliasing trap one level down
The original code created the per-environment lists like this:

```python
envs = ["dev", "staging", "prod"]
report = dict.fromkeys(envs, [])     # every key shares ONE list
report["dev"].append("api")
print(report)
# {'dev': ['api'], 'staging': ['api'], 'prod': ['api']}
```

`dict.fromkeys` evaluated `[]` once and gave every key the same list. The retry step appended to
"dev" and silently appended to all three. There are two correct fixes:

```python
# 1. Build the lists independently
report = {env: [] for env in envs}

# 2. Let defaultdict create them on demand
from collections import defaultdict
report = defaultdict(list)
report["dev"].append("api")
```

The general lesson: whenever you see a mutable value (`[]`, `{}`, a set) being reused across
several keys or loop iterations, ask whether it is one object or many. `[] `inside a comprehension
runs once per iteration; `[]` passed as an argument runs once, period. It is the same rule behind
mutable default arguments in Chapter 5, and behind most bug reports you will ever file about
shared state.
:::

## Key takeaways

- Lists are ordered and mutable; `append` adds one item, `extend` adds many, `pop` removes and
  returns.
- `list.sort()` sorts in place and returns `None`; `sorted(x)` returns a new sorted list. Both
  take `key=` and `reverse=`.
- `b = a` copies a reference, not data — use `list(a)`, `a.copy()`, or `copy.deepcopy()`.
- Tuples are immutable and hashable, which is why they can be dict keys and can be unpacked into
  several variables at once.
- Dicts map keys to values with O(1) lookup; `[]` raises `KeyError`, `get()` returns a default,
  `setdefault` inserts when absent.
- Sets remove duplicates and test membership in constant time; `|`, `&`, `-`, `^` are union,
  intersection, difference, and symmetric difference.
- Only hashable (immutable) objects can be dict keys or set members.
- `Counter`, `defaultdict`, `deque`, and `namedtuple` from `collections` cover the cases the
  built-ins handle awkwardly.

## Practice

- [ ] Build `shopping.py`: start with a list of three items, `append` two more, `insert` one at
      the front, `remove` one by name, then print the list and its length.
- [ ] Write `wordcount.py` that counts how often each word appears in the string
      `"the cat sat on the mat with the other cat"` and prints the three most common with their
      counts.
- [ ] Create a small `inventory` dict mapping three product names to prices. Add a product with
      `update`, look one up with `get()` using a default of `0.0`, and print every
      `name -> price` pair with an f-string.
- [ ] Write `dedupe.py`: given `["a", "b", "a", "c", "b", "a"]`, print the unique values in their
      original first-seen order (a set alone will not preserve order — you need a loop).
- [ ] Write `matrix.py` with a 3x3 list of lists of numbers. Print the sum of each row, then
      create a genuinely independent deep copy, change one inner value in the copy, and prove the
      original is unchanged.
- [ ] Build `roster.py`: a list of dicts, each with `name`, `team`, and `score`. Print the average
      score, the name of the top scorer, and a dict mapping each team to a sorted list of its
      members' names.

## Solutions

:::solution Exercise 1
```python
# shopping.py
items = ["milk", "bread", "eggs"]
items.append("coffee")
items.append("butter")
items.insert(0, "apples")
items.remove("bread")
print(items)
print(len(items))
```
```text
['apples', 'milk', 'eggs', 'coffee', 'butter']
5
```
`insert(0, ...)` puts the item at the front and pushes the rest right; `remove()` deletes the first
matching *value*, not an index. `len()` gives the current count after the mutations, not the
original.
:::

:::solution Exercise 2
```python
# wordcount.py
from collections import Counter

sentence = "the cat sat on the mat with the other cat"
counts = Counter(sentence.split())
print(counts.most_common(3))
```
```text
[('the', 3), ('cat', 2), ('sat', 1)]
```
`str.split()` with no argument splits on any whitespace and returns a list, which `Counter` counts
directly. `most_common(n)` returns `(item, count)` tuples in descending order; ties keep
first-seen order.
:::

:::solution Exercise 3
```python
# inventory.py
inventory = {"keyboard": 79.99, "mouse": 24.50, "monitor": 199.00}
inventory.update({"headset": 59.95})
print(inventory.get("webcam", 0.0))
for name, price in inventory.items():
    print(f"{name:>10} -> ${price:.2f}")
```
`get()` with a default keeps a missing product from crashing the program. Iterating `.items()`
gives you both halves at once, which is almost always what you want.
:::

:::solution Exercise 4
```python
# dedupe.py
items = ["a", "b", "a", "c", "b", "a"]
seen = set()
unique = []
for item in items:
    if item not in seen:
        seen.add(item)
        unique.append(item)
print(unique)
```
```text
['a', 'b', 'c']
```
The set answers "have I seen this?" in constant time; the list preserves the order. This
see-and-collect pair is a standard pattern — memorise it.
:::

:::solution Exercise 5
```python
# matrix.py
import copy

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
for row in matrix:
    print(sum(row))

clone = copy.deepcopy(matrix)
clone[0][0] = 999
print(clone[0])    # [999, 2, 3]
print(matrix[0])   # [1, 2, 3]  — unchanged
```
A shallow `.copy()` would have left the inner row lists shared, so mutating `clone[0][0]` would
have changed `matrix[0][0]` too. `deepcopy` walks the whole structure.
:::

:::solution Exercise 6
```python
# roster.py
from collections import defaultdict

players = [
    {"name": "ada", "team": "red", "score": 42},
    {"name": "grace", "team": "blue", "score": 91},
    {"name": "linus", "team": "red", "score": 77},
    {"name": "alan", "team": "blue", "score": 61},
]

average = sum(p["score"] for p in players) / len(players)
top = max(players, key=lambda p: p["score"])
teams = defaultdict(list)
for p in players:
    teams[p["team"]].append(p["name"])

print(f"average: {average:.1f}")
print(f"top scorer: {top['name']}")
for team in teams:
    print(team, sorted(teams[team]))
```
`defaultdict(list)` removes the "does this key exist yet?" check inside the loop. `max(..., key=)`
returns the whole dict, not just the score, so you can then read `top["name"]`. This shape — a
list of records — is exactly what Chapter 18 turns into JSON from an API and Chapter 19 turns
into a database table.
:::
