---
chapter: 41
part: 7
title: Memory — Reference Counting and the Cycle Collector
summary: How CPython decides when an object dies, why a cycle survives on its own, what the collector actually does, and how to recognise a leak in a language that has no free().
minutes: 55
tags: [memory, reference counting, gc, weakref, __slots__, leaks]
---

Chapter 40 ended with a rule: the fields that feed `__eq__` and `__hash__` must not change. This chapter
answers the question underneath it — when does an object stop existing at all?

Most languages answer "whenever the runtime feels like it, or never". Python's answer is more precise
and more useful: **CPython frees an object the instant the last reference to it goes away.** No
collector delay, no pause, no ambiguity. That is why `__del__` runs at a predictable moment and why a
file handle closes when you expect it to.

It is also why Python has a second mechanism that most people never learn, and why "Python has a
garbage collector" is a half-truth that leads to real bugs. The collector exists for one specific
shape — the cycle — and for nothing else. Knowing which shape you have tells you whether adding
`gc.collect()` will help or just make the service slower.

## Every object carries a count

CPython stores a reference count in the object header, next to the type pointer. `sys.getrefcount`
lets you read it.

```python run
import sys

a = []
print("a = []      -> getrefcount:", sys.getrefcount(a))
b = a
print("b = a       -> getrefcount:", sys.getrefcount(a))
c = [a, a]
print("c = [a, a]  -> getrefcount:", sys.getrefcount(a))
del b
print("del b       -> getrefcount:", sys.getrefcount(a))
c.clear()
print("c.clear()   -> getrefcount:", sys.getrefcount(a))
print()
print("Every number above is one higher than the count you can see by")
print("reading the code, because passing `a` to getrefcount() creates a")
print("reference for the duration of the call.")
print()
print("`del b` is not what freed the list `b` pointed at. It dropped one")
print("reference; the object goes away when the last one drops.")
```

```text
a = []      -> getrefcount: 2
b = a       -> getrefcount: 3
c = [a, a]  -> getrefcount: 5
del b       -> getrefcount: 4
c.clear()   -> getrefcount: 2

Every number above is one higher than the count you can see by
reading the code, because passing `a` to getrefcount() creates a
reference for the duration of the call.

`del b` is not what freed the list `b` pointed at. It dropped one
reference; the object goes away when the last one drops.
```

Read the numbers as a ledger. One name is one reference. A tuple holding the same list twice is *two*
references, because the tuple stores two pointers. A dict value is one more. `del b` and `c.clear()`
each remove references, and the count falls by exactly what they removed.

Two consequences are worth stating plainly.

**`del` does not delete anything.** It unbinds a name. If two names point at the same list, `del` on one
of them changes nothing about the list. The name `del` is one of the most misleading in the language.

**The count is always at least 1 while you can still reach the object** — and when it reaches zero, the
object is freed immediately, in the same operation that dropped the count. There is no deferred sweep,
no "eventually". This is why CPython reclaims acyclic garbage without ever running a collector, and it
is why a `with` block closes a file at the closing brace rather than at some later moment.

## When the count reaches zero

The `__del__` method is the finaliser, and its timing is the clearest demonstration that reference
counting is immediate.

```python run
import gc


class Tracked:
    def __init__(self, name):
        self.name = name
        print(f"  created   {name}")

    def __del__(self):
        print(f"  finalized {self.name}")


print("1. no cycle -- finalized the moment the last reference goes")
t = Tracked("plain")
del t
print()

print("2. a cycle -- nothing happens until the collector runs")
gc.disable()
a = Tracked("a")
b = Tracked("b")
a.partner = b
b.partner = a
del a
del b
print("   both names are gone, and neither object was finalized")
print("   that is the whole point: their reference counts are not zero")
collected = gc.collect()
print("   gc.collect() collected", collected, "unreachable objects")
gc.enable()
```

```text
1. no cycle -- finalized the moment the last reference goes
  created   plain
  finalized plain

2. a cycle -- nothing happens until the collector runs
  created   a
  created   b
   both names are gone, and neither object was finalized
   that is the whole point: their reference counts are not zero
  finalized a
  finalized b
   gc.collect() collected 2 unreachable objects
```

The first case is immediate: `del t` dropped the last reference and `__del__` ran inside that
operation. The second case is the whole reason the collector exists. `del a` and `del b` removed both
*names*, but each object still has a reference from the other one, so neither count is zero. They are
unreachable from anywhere in your program and they will never be freed by counting.

Note the order in which the finalisers ran — `a` then `b`. Do not rely on that. The order in which the
collector finalises a cycle is an implementation detail, and writing code that depends on it is a bug
waiting for a version upgrade.

:::pitfall `__del__` is not a destructor and must not be your cleanup plan
`__del__` has three properties that make it a poor place for anything important.

**It may never run.** If the interpreter exits while the object is in a cycle that the collector does
not reach, or if the process is killed, `__del__` is simply not called. Any file, socket or lock you
were relying on it to close stays open.

**It runs at a moment you do not control.** In the cycle case above, the finaliser ran during
`gc.collect()` — possibly in the middle of some unrelated code, in a different order than creation.

**An exception inside `__del__` is printed and ignored.** It cannot propagate, so a failure there is a
message on stderr and a silently skipped cleanup.

Use a context manager and a `with` block for cleanup. `__del__` is for diagnostics and for the rare
resource that has no other hook. Chapter 14 covers the `with` protocol; if you remember one rule from
this chapter, make it this one.
:::

## Reference counting cannot see cycles

The cycle is not an edge case. Trees with parent pointers, observers, doubly-linked lists, and any
object graph where a child knows its parent are all cycles, and they are all normal designs.

```python run
import gc, sys


class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

    def __repr__(self):
        return f"Node({self.name!r})"


gc.disable()          # leave only reference counting in play


def make_cycle():
    a = Node("a")
    b = Node("b")
    a.peer = b
    b.peer = a
    print("  inside, getrefcount(a) ->", sys.getrefcount(a),
          "(a, b.peer, and the argument)")
    return None


print("a two-node cycle, built inside a function")
make_cycle()
print("  the function returned, so both local names are gone")
print("  yet neither object was freed: each is kept alive by the other")
print("  their counts are 1, not 0, so reference counting cannot help")
print()
print("  gc.is_tracked is how the collector knows to look at them")
print("  gc.collect() ->", gc.collect(), "unreachable objects freed")
print()
print("reference counting frees acyclic garbage immediately and for free.")
print("The cycle collector exists only for the shapes refcounting cannot see.")
gc.enable()
```

```text
a two-node cycle, built inside a function
  inside, getrefcount(a) -> 3 (a, b.peer, and the argument)
  the function returned, so both local names are gone
  yet neither object was freed: each is kept alive by the other
  their counts are 1, not 0, so reference counting cannot help

  gc.is_tracked is how the collector knows to look at them
  gc.collect() -> 2 unreachable objects freed

reference counting frees acyclic garbage immediately and for free.
The cycle collector exists only for the shapes refcounting cannot see.
```

The mechanism is worth one sentence, because it explains the collector's cost. Every object that *can*
contain references — lists, dicts, instances, frames, tuples — is **tracked**: it is registered in a
linked list. Periodically the collector walks that list, and for each candidate it counts how many
references come from *outside* the candidate set. If a group of objects is only referenced by each
other, the group is unreachable and the whole group is freed. Finding that group requires looking at
every tracked object, which is why collection is expensive and why it is done rarely.

Immutable scalars — `int`, `str`, `bytes`, `float` — cannot contain references and are not tracked. That
is a real optimisation and it is why a list of a million integers is cheaper to manage than a list of a
million small objects.

## The collector, and when it runs

```python run
import gc


class Node:
    def __init__(self):
        self.next = None


print("the collector is generational: young objects are scanned often,")
print("older ones rarely, because most garbage dies young")
print("  gc.get_threshold() ->", gc.get_threshold())
print("  gc.isenabled()     ->", gc.isenabled())
print()

print("an explicit collect always works, even with the collector switched off")
gc.disable()
a, b = Node(), Node()
a.next = b
b.next = a
del a, b
print("  gc.collect() ->", gc.collect(), "objects freed while gc is disabled")
gc.enable()
print()

print("tuning you may actually need:")
print("  gc.set_threshold(...)  -- scan less often, if collection shows up")
print("                            in a profile as the cost")
print("  gc.freeze()            -- exclude existing objects from collection,")
print("                            which is worth knowing before you fork")
print("  gc.set_debug(...)      -- report what the collector collects")
```

```text
the collector is generational: young objects are scanned often,
older ones rarely, because most garbage dies young
  gc.get_threshold() -> (2000, 10, 10)
  gc.isenabled()     -> True

an explicit collect always works, even with the collector switched off
  gc.collect() -> 2 objects freed while gc is disabled

tuning you may actually need:
  gc.set_threshold(...)  -- scan less often, if collection shows up
                            in a profile as the cost
  gc.freeze()            -- exclude existing objects from collection,
                            which is worth knowing before you fork
  gc.set_debug(...)      -- report what the collector collects
```

The threshold triple means: run a generation-0 collection after roughly that many net container
allocations; promote survivors, and collect generation 1 every ten generation-0 passes, generation 2
every ten of those. The exact numbers have changed between versions — `(2000, 10, 10)` is CPython 3.13
— which is why you should read `gc.get_threshold()` rather than remember it.

`gc.freeze()` deserves a sentence because it is the one setting with a production use. After a server
loads a large dataset at startup, that data is in generation 2 and gets scanned on every full
collection for the life of the process, even though it will never be freed. `gc.freeze()` marks
everything currently alive as permanently out of scope, which makes later collections cheaper. If you
have ever seen "gc" in a profile of a long-running service, this is usually the fix.

## A cache that does not keep things alive

The practical tool that comes out of reference counting is the **weak reference**: a pointer that lets
you reach an object without keeping it alive.

```python run
import weakref


class Session:
    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return f"Session({self.user!r})"


print("a weak reference does not keep the object alive")
s = Session("ada")
ref = weakref.ref(s)
print("  ref() while s is alive ->", ref())
del s
print("  after del s            ->", ref())
print()

print("which is what makes a cache that does not leak")
cache = weakref.WeakValueDictionary()
tmp = Session("grace")
cache["grace"] = tmp
print("  cached, tmp alive      ->", dict(cache))
del tmp
print("  after del tmp          ->", dict(cache), " <- the entry went too")
print()

print("a strong cache would have kept it forever")
strong = {}
tmp = Session("alan")
strong["alan"] = tmp
del tmp
print("  strong cache holds     ->", dict(strong))
print("  and holds it until the program ends or the key is deleted")
```

```text
a weak reference does not keep the object alive
  ref() while s is alive -> Session('ada')
  after del s            -> None

which is what makes a cache that does not leak
  cached, tmp alive      -> {'grace': Session('grace')}
  after del tmp          -> {}  <- the entry went too

a strong cache would have kept it forever
  strong cache holds     -> {'alan': Session('alan')}
  and holds it until the program ends or the key is deleted
```

`ref()` returns the object, or `None` if it has been freed — which means every use of a weak reference
must handle `None`, and that is not a nuisance, it is the point. The `WeakValueDictionary` does it for
you: when a value is freed, its entry leaves the dictionary. The dict cannot grow past the set of
objects that something else still cares about.

`WeakKeyDictionary` and `WeakSet` exist for the same purpose with the reference on the other side. They
are the standard answer to "I want a cache, but I do not want it to be the reason memory grows".

One restriction is worth knowing: `int`, `str`, `tuple` and most built-in scalars cannot be weakly
referenced at all — `weakref.ref("x")` raises `TypeError`. They are exactly the types that are not
tracked by the collector, for the same reason: there is nothing inside them to point anywhere.

## `__slots__`: buying memory with flexibility

Every instance of a normal class carries a dictionary. That dictionary is what makes `obj.anything = x`
work, and it is the single largest per-object cost in a program that creates many small objects.

```python run
import tracemalloc


class WithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class WithSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


def footprint(cls, n):
    """Total bytes still allocated for n instances of cls."""
    tracemalloc.start()
    objs = [cls(1, 2) for _ in range(n)]
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del objs
    return current


N = 200_000
d = footprint(WithDict, N)
s = footprint(WithSlots, N)

print(f"  {N:,} objects, measured with tracemalloc")
print(f"  WithDict  -> {d:>10,} bytes   ({d / N:5.1f} per object)")
print(f"  WithSlots -> {s:>10,} bytes   ({s / N:5.1f} per object)")
print(f"  saved     -> {d - s:>10,} bytes")
print()
print("the saving is the per-instance __dict__, which slots removes:")
print("  hasattr(a, '__dict__') ->", hasattr(WithDict(1, 2), "__dict__"))
print("  hasattr(b, '__dict__') ->", hasattr(WithSlots(1, 2), "__dict__"))
print()
print("and what it costs -- the class can no longer gain attributes:")
try:
    WithSlots(1, 2).z = 3
except AttributeError as exc:
    print("  b.z = 3 ->", exc)
print()
print("That is the whole trade: no __dict__ means no room for a new")
print("attribute. At 200,000 objects it is eight megabytes.")
```

```text
  200,000 objects, measured with tracemalloc
  WithDict  -> 19,227,360 bytes   ( 96.1 per object)
  WithSlots -> 11,224,000 bytes   ( 56.1 per object)
  saved     ->  8,003,360 bytes

the saving is the per-instance __dict__, which slots removes:
  hasattr(a, '__dict__') -> True
  hasattr(b, '__dict__') -> False

and what it costs -- the class can no longer gain attributes:
  b.z = 3 -> 'WithSlots' object has no attribute 'z' and no __dict__ for setting new attributes

That is the whole trade: no __dict__ means no room for a new
attribute. At 200,000 objects it is eight megabytes.
```

:::warning Your numbers will not match these
The byte counts come from CPython 3.13.12 on the machine this book was built on. `tracemalloc` measures
what the interpreter actually allocated, and that depends on the version, the build, and the platform.
The *direction* is what matters and it is stable across versions: a class with `__slots__` is smaller
per instance, by roughly the size of one dictionary. Run the block yourself and read your own numbers.
:::

The measurements above are for two fields, so the saving is modest per object and large in aggregate.
Three things are worth knowing before you reach for `__slots__`.

**It is for objects you create in large numbers.** A few hundred config objects do not matter. A million
particles, rows or tokens do.

**It removes the ability to add attributes.** Any code that does `obj.debug_note = ...` breaks. So does
any library that attaches metadata to your instances, and so does `functools.cached_property`, which
needs somewhere to store its result.

**It is not the first thing to try.** A dataclass with `slots=True`, or a `NamedTuple`, or storing rows
in parallel arrays instead of objects, are usually better answers. `__slots__` is the tool you use once
you have measured and know that instance dictionaries are the cost.

## What a leak looks like in Python

Python has no `malloc`, so a leak is never "memory that was never freed". It is always **an object that
is still reachable when you expected it to be dead**. Three shapes cover almost every real case.

```python run
class Node:
    def __init__(self, name):
        self.name = name
        self.children = []


print("shape 1: a container that only ever grows")
root = Node("root")
seen = []
for i in range(1000):
    child = Node(f"c{i}")
    root.children.append(child)
    seen.append(child)
print("  root.children ->", len(root.children), "  seen ->", len(seen))
print("  every child is alive because two containers point at it")
print()

print("shape 2: a closure that keeps everything it ever computed")
def make_counter(seed):
    history = [seed]
    def counter():
        history.append(history[-1] + 1)
        return history[-1]
    return counter


c = make_counter(0)
for _ in range(5):
    c()
print("  c() ->", c())
print("  the closure still holds the whole history ->",
      c.__closure__[0].cell_contents)
print()

print("shape 3: an exception holding a traceback, which holds a frame")
def boom():
    payload = [0] * 1000
    raise ValueError("captured")


held = None
try:
    boom()
except ValueError as exc:
    held = exc
print("  held.__traceback__ ->", type(held.__traceback__).__name__)
print("  the frame it holds still has its locals ->",
      list(held.__traceback__.tb_next.tb_frame.f_locals))
print("  so `payload` -- a thousand elements -- is alive as long as `held` is")
print()
print("none of these is a bug on its own. Each is a reference you did not")
print("notice you were keeping, which is what a leak in Python looks like.")
```

```text
shape 1: a container that only ever grows
  root.children -> 1000   seen -> 1000
  every child is alive because two containers point at it

shape 2: a closure that keeps everything it ever computed
  c() -> 6
  the closure still holds the whole history -> [0, 1, 2, 3, 4, 5, 6]

shape 3: an exception holding a traceback, which holds a frame
  held.__traceback__ -> traceback
  the frame it holds still has its locals -> ['payload']
  so `payload` -- a thousand elements -- is alive as long as `held` is

none of these is a bug on its own. Each is a reference you did not
notice you were keeping, which is what a leak in Python looks like.
```

Shape 3 is the one that surprises people most, and it has a specific fix. A traceback holds the frames
it passed through, and a frame holds its locals. So storing an exception stores everything that was
alive where it was raised. If you keep exceptions in a list for later reporting, you are keeping every
local variable of every frame they passed through. Store `str(exc)` and the traceback text, or `del
exc` after extracting what you need.

The tool for all three is `gc.get_referrers(obj)`, which lists every object that points at yours. When
you cannot work out why something is still alive, that function names the container that is holding it.

:::scenario The service that grows by 40 MB a day
A report generator builds a tree of nodes per request. Each node holds its children, and each child
holds a `parent` pointer back to its parent — a cycle, and a normal design. The tree is rendered,
returned, and dropped.

Memory grows steadily and never comes back. The team's diagnosis was "Python does not release memory",
so they added `gc.collect()` at the end of every handler. The service got measurably slower and memory
kept climbing.

Why did the collector not help, and what is actually holding the memory?
:::

:::solution The objects are not garbage — they are reachable
`gc.collect()` frees **unreachable** cycles. It cannot free anything that something still points at. If
calling it made no difference, the trees are not unreachable, which means the search is for a
reference you did not intend to keep — not for a missing collection.

Here is the same bug in fourteen lines. The registry is the line that gets added "just for debugging":

```python run
import gc, weakref


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.parent = None


print("=== a list registry (the leak)")


def make_tree():
    root = Node("root")
    child = Node("child")
    child.parent = root
    root.children.append(child)
    return root


registry = []
for _ in range(100):
    registry.append(make_tree())

print("  gc.collect() freed   ->", gc.collect(), "objects")
print("  registry holds       ->", len(registry), "roots")
print("  so the trees are NOT garbage: they are reachable from registry")
print()

print("=== a WeakSet registry (the fix)")
weak_registry = weakref.WeakSet()
for _ in range(100):
    weak_registry.add(make_tree())

print("  gc.collect() freed   ->", gc.collect(), "objects")
print("  weak_registry holds  ->", len(weak_registry), "roots")
print("  nothing else referred to the trees, so they were freed and the")
print("  WeakSet dropped them on its own")
```

```text
=== a list registry (the leak)
  gc.collect() freed   -> 0 objects
  registry holds       -> 100 roots
  so the trees are NOT garbage: they are reachable from registry

=== a WeakSet registry (the fix)
  gc.collect() freed   -> 500 objects
  weak_registry holds  -> 0 roots
  nothing else referred to the trees, so they were freed and the
  WeakSet dropped them on its own
```

The first block is the production bug. `gc.collect()` freed **zero** objects, because every tree is
reachable from `registry`, and the registry is a module-level list that lives for the life of the
process. The cycle inside each tree is irrelevant — a cycle only becomes garbage when the *whole* cycle
is unreachable, and one pointer from outside is enough to keep all of it alive.

Notice the shape of the mistake. Each tree is small. The registry grows by one root per request, and
each root holds a subtree. So the leak is proportional to the work done, which is why it looks like
"memory grows with traffic" and why the first instinct — collect more often — cannot possibly help.

**The fix is one word: `WeakSet` instead of `list`.** The registry still lets you look at every tree
that is currently alive, which is what the debugging code wanted. It just does not *keep* them alive.
The second block proves the difference: the collector freed the whole batch, and the registry emptied
itself as the trees died.

Two other fixes are worth knowing, because the situation varies.

**Bound the container.** A `deque(maxlen=1000)` or a list that is truncated on every write gives you
recent history instead of all history. This is the right answer when you genuinely want to keep
something, but not everything.

**Remove the registry.** Debugging scaffolding that survives into production is a common source of
exactly this bug, and the cheapest fix is deletion.

**How to confirm it in a running service**, in order: `gc.get_referrers(suspect)` names the containers
holding an object; `tracemalloc.take_snapshot()` compared against an earlier snapshot shows which
allocation site grew, with line numbers. Do not start by adding `gc.collect()` — start by finding the
reference. The collector is not a fix for reachable objects, and adding it only hides the search behind
a slowdown.
:::

## Key takeaways

- **CPython frees an object the instant its reference count reaches zero**, with no collector delay.
  `del` unbinds a name; it does not delete an object.
- **`sys.getrefcount` always reads one higher than the count you can see**, because the argument itself
  is a reference for the duration of the call.
- **A cycle keeps its members alive at a count of 1 each**, so reference counting can never free it. The
  cycle collector exists for exactly this shape and nothing else.
- **`gc.collect()` frees unreachable cycles, not reachable objects.** If collecting more often does not
  help, the objects are still referenced and the bug is a reference, not a missing collection.
- **The collector is generational** — young objects are scanned often, old ones rarely — and it is
  expensive because it must inspect every tracked container object.
- **`__del__` is a finaliser, not a destructor.** It may never run, it runs at a time you do not
  control, and an exception inside it is printed and swallowed. Use a context manager for cleanup.
- **Weak references let you observe an object without keeping it alive.** `weakref.ref`,
  `WeakValueDictionary`, `WeakKeyDictionary` and `WeakSet` are the standard answer to a cache that must
  not be the reason memory grows.
- **`__slots__` removes the per-instance dictionary**, which is the largest per-object cost for many
  small objects — at the price of not being able to add attributes, and of breaking anything that
  attaches metadata to your instances.
- **A leak in Python is an object that is still reachable when you expected it to be dead.** The three
  usual shapes are a growing container, a closure holding history, and a stored exception holding a
  traceback that holds frames.
- **`gc.get_referrers(obj)` names the container that is holding your object.** It is the first tool to
  reach for, before `tracemalloc`, and long before `gc.collect()`.

## Practice

- [ ] Predict, then verify with `sys.getrefcount`, the count of a list placed in a tuple twice and in a
      dict once. Explain each change by naming the reference that was added.
- [ ] Build a two-object cycle inside a function and show that `__del__` does not run when the function
      returns. Then run `gc.collect()` and show that it does.
- [ ] Put the same object in a `WeakValueDictionary` and a plain `dict`, delete your only other
      reference, and show that the weak entry disappears while the strong one does not.
- [ ] Measure the `__slots__` saving for a class with four fields using `tracemalloc`, and state the
      trade in one sentence.
- [ ] Write a closure that leaks its history, then rewrite it so it does not. Show both return the same
      answer.
- [ ] Explain why `sys.getrefcount(1)` is enormous and `sys.getrefcount([1])` is tiny, and why neither
      is a leak.

## Solutions

:::solution Exercise 1
```python run
import sys

a = []
print("a = []       ->", sys.getrefcount(a))
t = (a, a)
print("t = (a, a)   ->", sys.getrefcount(a))
d = {"k": a}
print("d = {'k': a} ->", sys.getrefcount(a))
del t
print("del t        ->", sys.getrefcount(a))
```

```text
a = []       -> 2
t = (a, a)   -> 4
d = {'k': a} -> 5
del t        -> 3
```

Start from 2, not 1: the name `a` is one reference and the argument to `getrefcount` is the other.

`t = (a, a)` adds **two**, because a tuple stores one pointer per element and there are two elements.
This is the part people get wrong — the count tracks pointers, not "things that point at it". One tuple
can add two references.

`d = {"k": a}` adds one, for the dict's value slot. The key is the string `"k"`, not `a`.

`del t` removes both of the tuple's references at once, because the tuple itself became unreachable and
was freed immediately — which also took its two pointers with it. That is the count falling from 5 to 3
rather than to 4.

The general rule: **count the pointers, not the containers.** A list of one element adds one. A list of
the same element three times adds three.
:::

:::solution Exercise 2
```python run
import gc

events = []


class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

    def __del__(self):
        events.append(self.name)


def build():
    a, b = Node("a"), Node("b")
    a.peer, b.peer = b, a


gc.disable()
build()
print("after build() returned, __del__ has run for:", events)
n = gc.collect()
print("gc.collect() freed", n, "objects")
print("now __del__ has run for:", sorted(events))
gc.enable()
```

```text
after build() returned, __del__ has run for: []
gc.collect() freed 2 objects
now __del__ has run for: ['a', 'b']
```

The empty list is the evidence that reference counting alone cannot handle this. `build()` returned, so
the names `a` and `b` are gone, and every reference that remains is *inside* the pair: `a.peer` holds
`b`, `b.peer` holds `a`. Each object's count is 1, and neither will ever reach 0.

`gc.collect()` freed exactly two objects — the pair — and only then did `__del__` run for each. Note
that the output is sorted: the finalisation order inside a collected cycle is not guaranteed, so a test
that asserted `["a", "b"]` in that order would be relying on an implementation detail.

`gc.disable()` was there to remove the ambiguity. Without it, an automatic collection triggered by
some unrelated allocation might have freed the pair before the `print` — which is precisely why
relying on `__del__` timing is fragile.
:::

:::solution Exercise 3
```python run
import weakref


class Entry:
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return f"Entry({self.key!r})"


weak = weakref.WeakValueDictionary()
strong = {}

w = Entry("weak")
s = Entry("strong")
weak["weak"] = w
strong["strong"] = s

print("both caches, both objects alive ->")
print("  weak   ->", dict(weak))
print("  strong ->", dict(strong))

del w
del s

print("after deleting the only other reference to each ->")
print("  weak   ->", dict(weak), " (the entry vanished)")
print("  strong ->", dict(strong), " (still held, and will be until the dict dies)")
```

```text
both caches, both objects alive ->
  weak   -> {'weak': Entry('weak')}
  strong -> {'strong': Entry('strong')}
after deleting the only other reference to each ->
  weak   -> {}  (the entry vanished)
  strong -> {'strong': Entry('strong')}  (still held, and will be until the dict dies)
```

The weak dictionary emptied itself; the plain one did not. That is the entire difference between a cache
that is bounded by the objects something else still cares about and a cache that becomes the reason
memory grows.

The mistake to avoid while testing this is putting the *same* object in both caches. Then `del w` is not
the last reference, the object stays alive, and the weak entry correctly does not disappear — which
looks like the weak dictionary failing when it is doing exactly the right thing. Use two separate
objects, as above, and the contrast is clean.
:::

:::solution Exercise 4
```python run
import tracemalloc


class Point:
    def __init__(self, x, y, z, label):
        self.x, self.y, self.z, self.label = x, y, z, label


class SlotPoint:
    __slots__ = ("x", "y", "z", "label")

    def __init__(self, x, y, z, label):
        self.x, self.y, self.z, self.label = x, y, z, label


def footprint(cls, n):
    tracemalloc.start()
    objs = [cls(1.0, 2.0, 3.0, "p") for _ in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del objs
    return current


N = 100_000
p = footprint(Point, N)
s = footprint(SlotPoint, N)
print(f"  Point     -> {p:>9,} bytes  ({p / N:5.1f} each)")
print(f"  SlotPoint -> {s:>9,} bytes  ({s / N:5.1f} each)")
print(f"  saved     -> {p - s:>9,} bytes")
```

```text
  Point     -> 11,204,008 bytes  (112.0 each)
  SlotPoint -> 7,200,928 bytes  ( 72.0 each)
  saved     -> 4,003,080 bytes
```

Four fields instead of two, and the saving per object grew with them — because the dictionary is
sized by how much you put in it, while the slots array is exactly one pointer per declared name. That
is the mechanism: you are trading a hash table per object for a fixed array per object.

The trade, in one sentence: **`__slots__` gives up the ability to add attributes to an instance in
exchange for a smaller instance**, which means it breaks any code that sets an attribute the class did
not declare — including `functools.cached_property` and most libraries that attach metadata to objects
they are given.

Note also that the numbers are version-dependent, like every `tracemalloc` measurement. Run it yourself;
the direction is what carries over.
:::

:::solution Exercise 5
```python run
def make_summer():
    seen = []
    def add(n):
        seen.append(n)
        return sum(seen)
    return add


total = make_summer()
for n in range(1000):
    total(n)
print("after 1000 calls the closure is holding 1000 values")


def make_summer_fixed():
    running = 0
    def add(n):
        nonlocal running
        running += n
        return running
    return add


total = make_summer_fixed()
for n in range(1000):
    last = total(n)
print("the fixed version holds one integer and returns", last)
```

```text
after 1000 calls the closure is holding 1000 values
the fixed version holds one integer and returns 499500
```

Both versions return the same running total, and only one of them needs to remember every input. The
first is not wrong — `sum(seen)` is a correct way to compute a running total — but it is a leak in
disguise if the closure is long-lived. A million calls means a million-element list held forever to
answer a question that needs one number.

The fix is the `nonlocal` declaration. A closure cell can hold a mutable binding as easily as a
mutable object, so `running += n` inside the inner function writes to the enclosing scope's variable
rather than creating a new local. That is the mechanism to reach for whenever a closure is accumulating
history you do not actually need.

This is worth contrasting with the previous exercise: `__slots__` reduces what an object costs, and this
reduces *how many objects there are*. The second is usually the bigger win, and it is always the
cheaper one to implement.
:::

:::solution Exercise 6
```python run
import sys

print("sys.getrefcount(1) > 100     ->", sys.getrefcount(1) > 100)
print("sys.getrefcount('a') > 100   ->", sys.getrefcount("a") > 100)
print("sys.getrefcount([1]) > 100   ->", sys.getrefcount([1]) > 100)
```

```text
sys.getrefcount(1) > 100     -> True
sys.getrefcount('a') > 100   -> True
sys.getrefcount([1]) > 100   -> False
```

`1` and `"a"` are cached and interned. Every place in the interpreter that needs the value `1` — and
there are hundreds, in the standard library, in `site`, in the import machinery — points at the same
object. The count is real, and it is a count of *shared users*, not of anything your program is
hoarding.

A fresh list is different: it was created a moment ago for this expression, nothing else has ever seen
it, so its count is 2 — the temporary and the argument. It will be freed as soon as the call returns.

So a large `getrefcount` on a small immutable value means the value is popular, and a small one on a
container means the container is private. Neither says anything about a leak, and neither should be
used as a health check. The number to watch for a leak is the *count of live objects*, or the growth of
`tracemalloc`'s snapshot — not the reference count of a single object.
:::
