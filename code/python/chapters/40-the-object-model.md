---
chapter: 40
part: 7
title: The Object Model
summary: Every value in Python is an object with an identity, a type and a value — and almost every feature you already use is one of the protocols that object model defines.
minutes: 60
tags: [objects, identity, dunder methods, __eq__, __hash__, __repr__, protocols]
---

Chapter 39 opened the interpreter and showed you the instructions. This chapter opens the values those
instructions move around.

You have been using objects since chapter 2, and you have probably noticed that Python is unusually
willing to let you define behaviour by naming a method with two underscores around it. `__init__` you
know. `__repr__` you have written. `__eq__` you have written because a test needed it. What you may
not have noticed is that these are not a grab-bag of features. They are the surface of a single model,
and that model is small enough to hold in your head:

**Every value in Python is an object, and every object has an identity, a type, and a value. The
interpreter reaches all of its behaviour through a fixed set of protocols, and you join a protocol by
defining a method with the right name.**

That is the whole chapter. Everything below is either a consequence of it or an exception to it that
you need to know about. The payoff is not academic: the `__eq__`/`__hash__` contract is the reason a
dict lookup can silently fail, and the mutability rule is the reason a default argument can poison a
function across every call in a long-running process.

## Three questions you can ask about any value

Identity, type and value. Python gives you one operator or function for each.

```python run
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print("three questions you can ask about any value")
print("  identity : a is c      ->", a is c)
print("  identity : a is b      ->", a is b)
print("  type     : type(a) is type(b) ->", type(a) is type(b))
print("  value    : a == b      ->", a == b)
print()
print("a and b are equal values that are different objects.")
print("a and c are the same object, so they cannot help being equal.")
```

```text
three questions you can ask about any value
  identity : a is c      -> True
  identity : a is b      -> False
  type     : type(a) is type(b) -> True
  value    : a == b      -> True

a and b are equal values that are different objects.
a and c are the same object, so they cannot help being equal.
```

Read the last line again, because it is a one-way implication and the direction matters. **Same
object implies equal value. Equal value does not imply same object.** `a == c` is `True` because `a is
c`, and no work is done to establish it — the interpreter does not compare three integers, it sees two
names for one list and stops. `a == b` is `True` after comparing element by element.

That asymmetry is why `is` and `==` are different operators rather than a fast and slow version of the
same thing. `is` asks a question that is always answerable in one step: are these two references
pointing at the same object? `==` asks a question that may require walking an entire data structure,
and that a class is allowed to redefine.

Identity is reported as an integer by `id()`, and in CPython that integer happens to be the object's
address. Do not build anything on that. The language only promises that `id()` is unique among live
objects and constant for an object's lifetime. In a future version it could be a counter, and your
program would still be correct if you used `is`.

## Identity is not value

Two equal objects are usually two objects. Sometimes they are not, and the exceptions are worth
knowing because they are exactly where a program that confuses `is` with `==` starts working by
accident and then stops.

```python run
print("identity is not value -- three ways they diverge")
print()

print("1. CPython caches small integers, so equal ones are the same object")
print("   int('256') is int('256') ->", int("256") is int("256"))
print("   int('257') is int('257') ->", int("257") is int("257"))
print("   (the cache covers -5..256, and that range is an implementation detail)")
print()

print("2. equal constants in ONE code object are folded into one object")
x = 257
y = 257
print("   257 and 257, reached through two names in one scope ->", x is y)
print()

print("3. strings are only interned when they look like identifiers")
same = "hello"
built = "".join(["hel", "lo"])
print("   'hello' == 'hello' ->", same == built)
print("   'hello' is 'hello' ->", same is built)
print()

print("conclusion: `is` answers a question about identity, and identity is not")
print("something a program may rely on for numbers or for text.")
```

```text
identity is not value -- three ways they diverge

1. CPython caches small integers, so equal ones are the same object
   int('256') is int('256') -> True
   int('257') is int('257') -> False
   (the cache covers -5..256, and that range is an implementation detail)

2. equal constants in ONE code object are folded into one object
   257 and 257, reached through two names in one scope -> True

3. strings are only interned when they look like identifiers
   'hello' == 'hello' -> True
   'hello' is 'hello' -> False

conclusion: `is` answers a question about identity, and identity is not
something a program may rely on for numbers or for text.
```

All three of these are optimisations. The small-integer cache exists because programs create millions
of small integers and most of them are the same few values. Interning exists because dictionary keys
are usually identifiers, and comparing two strings that are the same object is free while comparing
two that are not requires reading both. Constant folding happens in the compiler, which is why case 2
behaves differently from case 1: those two `257` literals never became two objects in the first place.

The trap is that case 2 makes `257 is 257` print `True` in a quick experiment, and someone concludes
that `is` compares numbers. It does not. It compared two references to one object that the compiler
happened to share. Write the same comparison where the compiler cannot fold it and the answer flips.

:::warning `is` with a literal is a mistake the interpreter will point out
Python 3.13 notices this specific pattern and warns about it at compile time. The program still runs —
which is what makes it dangerous — but the warning is proof that the compiler regards the comparison as
almost certainly a bug.

```python run
import os, subprocess, sys, tempfile

SOURCE = "print(257 is 257)\n"

with tempfile.TemporaryDirectory() as td:
    path = os.path.join(td, "demo.py")
    with open(path, "w") as fh:
        fh.write(SOURCE)

    proc = subprocess.run([sys.executable, path], capture_output=True, text=True)

print("the program  : print(257 is 257)")
print("its stdout   :", proc.stdout.strip())
print("its stderr   :", proc.stderr.strip().splitlines()[0].split(": ", 1)[1])
print()
print("The interpreter rejected nothing -- the program ran and printed True.")
print("But the compiler noticed the mistake, and said so, before running it.")
```

```text
the program  : print(257 is 257)
its stdout   : True
its stderr   : SyntaxWarning: "is" with 'int' literal. Did you mean "=="?

The interpreter rejected nothing -- the program ran and printed True.
But the compiler noticed the mistake, and said so, before running it.
```

Note where the warning came from. It is on stderr, and it appeared *before* the program's own output —
because it was produced by the compiler in stage two, and the program only reached stage three
afterwards. Chapter 39's three stages are not a diagram; they are observable.

The two uses of `is` that are correct, and that you should keep using, are `x is None` and
`x is not None`. Both work because `None` is a singleton: there is exactly one `None` object in a
running interpreter, so identity and equality agree, and identity is the faster and clearer question.
`isinstance` and `is` with a sentinel object you created yourself are the other legitimate cases.
:::

## `__new__` builds the object; `__init__` configures it

Everyone learns that `__init__` "constructs" an object. It does not. By the time `__init__` runs, the
object already exists and is empty. Something else made it.

That something is `__new__`, and the call sequence is worth seeing once.

```python run
class Probe:
    def __new__(cls, *args, **kwargs):
        print("  __new__     called, args =", args)
        instance = super().__new__(cls)
        print("  __new__     built an empty", type(instance).__name__)
        return instance

    def __init__(self, value):
        print("  __init__    called, value =", value)
        self.value = value


print("Probe(1):")
p = Probe(1)
print("  result: p.value =", p.value)
print()

print("Now a class whose __new__ returns something that is NOT an instance")
print("of the class:")


class Factory:
    def __new__(cls):
        print("  __new__  returning a list instead of a Factory")
        return [1, 2, 3]

    def __init__(self):
        print("  __init__ ran -- you should NOT see this line")


f = Factory()
print("  result:", f, type(f).__name__)
print()

print("And the case that forces you to use __new__: an immutable base.")


class Frozen(tuple):
    def __new__(cls, *values):
        return super().__new__(cls, values)


fz = Frozen(1, 2, 3)
print("  Frozen(1, 2, 3) ->", fz, " type:", type(fz).__name__)
print("  isinstance(fz, tuple) ->", isinstance(fz, tuple))
print("  a tuple subclass cannot set attributes in __init__: the value is")
print("  already fixed by the time __new__ returns, which is the whole point.")
```

```text
Probe(1):
  __new__     called, args = (1,)
  __new__     built an empty Probe
  __init__    called, value = 1
  result: p.value = 1

Now a class whose __new__ returns something that is NOT an instance
of the class:
  __new__  returning a list instead of a Factory
  result: [1, 2, 3] list

And the case that forces you to use __new__: an immutable base.
  Frozen(1, 2, 3) -> (1, 2, 3)  type: Frozen
  isinstance(fz, tuple) -> True
  a tuple subclass cannot set attributes in __init__: the value is
  already fixed by the time __new__ returns, which is the whole point.
```

Three facts are visible in that output, and each one has a practical consequence.

**`__new__` runs first and receives the same arguments.** It is a static method even though you write
it as `def __new__(cls, ...)` — Python passes the class in, which is why you call
`super().__new__(cls)` and not `super().__new__()`.

**If `__new__` returns an object that is not an instance of the class, `__init__` is skipped.** The
list came back from `Factory()` and the `__init__` line never printed. This is not a curiosity; it is
the mechanism behind several idioms, including the one in Exercise 2 where a class returns an existing
instance instead of a new one — and it is why a singleton that returns a cached instance still has
`__init__` run on it every time.

**Immutable types must be built in `__new__`, because you cannot change them afterwards.** A tuple's
contents are fixed when the object is created, so a `tuple` subclass has no `__init__` step in which to
set anything. All of its construction is in `__new__`. The same is true of `str`, `int`, `bytes` and
`frozenset`. This is the first place where immutability is not a style preference but a structural
constraint on how you write the class.

:::tip You will almost never write `__new__`
For ordinary classes, `object.__new__` does the right thing and you override `__init__`. Reach for
`__new__` when you need to control *which object is returned* — a cache, a singleton, a subclass
chosen at runtime — or when you are subclassing an immutable type. If you are writing `__new__` to set
attributes on a normal class, you have taken a wrong turn.
:::

## Where attributes actually live

`self.value = value` looks like it stores something on the object. `Counter.step = 1` looks like it
stores something on the class. Both are true, and the difference between them explains a surprising
amount of behaviour.

```python run
class Counter:
    step = 1                      # lives on the class

    def __init__(self):
        self.value = 0            # lives on the instance

    def bump(self):
        self.value += self.step


c = Counter()
d = Counter()

print("where attributes live")
print("  c.__dict__            ->", c.__dict__)
print("  'step' in Counter.__dict__ ->", "step" in Counter.__dict__)
print("  'bump' in Counter.__dict__ ->", "bump" in Counter.__dict__)
print("  'bump' in c.__dict__       ->", "bump" in c.__dict__)
print()

print("reading c.step finds it on the class:")
print("  c.step ->", c.step)
print()

c.step = 10
print("after `c.step = 10` -- this creates an INSTANCE attribute:")
print("  c.__dict__     ->", c.__dict__)
print("  c.step         ->", c.step)
print("  d.step         ->", d.step, " (untouched)")
print("  Counter.step   ->", Counter.step, " (untouched)")
print()

print("the lookup order is: instance dict, then type, then the MRO")
print("  c.bump() ->", end=" ")
c.bump()
print(c.value)
print("  ...and `bump` was found on the type, not on c. That is why a bound")
print("  method knows which instance to pass as `self`.")
```

```text
where attributes live
  c.__dict__            -> {'value': 0}
  'step' in Counter.__dict__ -> True
  'bump' in Counter.__dict__ -> True
  'bump' in c.__dict__       -> False

reading c.step finds it on the class:
  c.step -> 1

after `c.step = 10` -- this creates an INSTANCE attribute:
  c.__dict__     -> {'value': 0, 'step': 10}
  c.step         -> 10
  d.step         -> 1  (untouched)
  Counter.step   -> 1  (untouched)

the lookup order is: instance dict, then type, then the MRO
  c.bump() -> 10
  ...and `bump` was found on the type, not on c. That is why a bound
  method knows which instance to pass as `self`.
```

`bump` is not in `c.__dict__`. It never will be. **A method is a class attribute.** When you write
`c.bump()`, the interpreter looks up `bump` on the instance dict (miss), then on `type(c)` (hit),
finds a function, and *binds* it to `c` before calling it. Binding is the step that produces the `self`
argument. You are not calling a function that magically knows about `c`; you are calling a small
adapter object that was created on the spot and that remembers `c`.

Chapter 42 takes that adapter apart and shows that `@property`, `@classmethod`, `@staticmethod` and
`functools.cached_property` are all the same mechanism wearing different names. For now, the fact to
keep is that **reading an attribute walks a chain, and writing an attribute does not.**

`c.step = 10` did not change `Counter.step`. It created a new entry in `c.__dict__` that now shadows
the class attribute for `c` alone. `d` and `Counter` were untouched — but `c.bump()` then used the
shadowed value, because `self.step` goes through the same lookup chain and finds the instance entry
first. Shadowing is not a cosmetic change to a name; it changes what the object's own methods compute.

That is the same rule that makes `self.value += 1` work. `+=` on an attribute reads through the chain
and then writes to the instance dict, which is why the first `bump()` creates `value`'s new entry
rather than modifying the class.

## `__repr__` for developers, `__str__` for users

`print(x)` and `repr(x)` are different operations, and a class that defines only one of them behaves
in a way worth knowing precisely.

```python run
class Money:
    def __init__(self, amount, currency="GBP"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self):
        return f"{self.amount:.2f} {self.currency}"


m = Money(3.5)
print("repr(m)       ->", repr(m))
print("str(m)        ->", str(m))
print("f'{m}'        ->", f"{m}")
print("f'{m!r}'      ->", f"{m!r}")
print("inside a list ->", [m, m])
print("as a dict key ->", {m: "value"})
print()

print("a class with only __repr__:")


class OnlyRepr:
    def __repr__(self):
        return "OnlyRepr()"


o = OnlyRepr()
print("  str(o) ->", str(o), " <- __str__ falls back to __repr__")
print()

print("a class with neither:")


class Bare:
    pass


b = Bare()

import re

# The real repr contains an address, which differs on every run. Masking it
# keeps this listing honest and reproducible: the SHAPE is the lesson.
def masked(obj):
    return re.sub(r"0x[0-9a-f]+", "0x...", repr(obj))


print("  repr(b) ->", masked(b))
print("  str(b)  ->", masked(b))
print()
print("The default shows the class and an address. That is the cost of not")
print("writing __repr__: every debugging session pays it, every time.")
```

```text
repr(m)       -> Money(3.5, 'GBP')
str(m)        -> 3.50 GBP
f'{m}'        -> 3.50 GBP
f'{m!r}'      -> Money(3.5, 'GBP')
inside a list -> [Money(3.5, 'GBP'), Money(3.5, 'GBP')]
as a dict key -> {Money(3.5, 'GBP'): 'value'}

a class with only __repr__:
  str(o) -> OnlyRepr()  <- __str__ falls back to __repr__

a class with neither:
  repr(b) -> <__main__.Bare object at 0x...>
  str(b)  -> <__main__.Bare object at 0x...>

The default shows the class and an address. That is the cost of not
writing __repr__: every debugging session pays it, every time.
```

Four rules fall out of this, and they are the reason the pair is worth writing deliberately.

**`repr` is for you; `str` is for the user.** `Money(3.5, 'GBP')` tells a developer the class and the
exact arguments. `3.50 GBP` tells a customer the amount. Neither is a better version of the other.

**Containers call `repr` on their contents, not `str`.** Look at the list and the dict: both show
`Money(3.5, 'GBP')`. This is deliberate — if a list called `str` on its elements, `[money1, money2]`
would print as `[3.50 GBP, 3.50 GBP]` and you would have lost the information that distinguishes the
two entries. That rule is why a class without `__repr__` makes debugging a list of them so unpleasant.

**`__str__` falls back to `__repr__`, never the reverse.** Define only `__repr__` and both work. Define
only `__str__` and `repr(x)` still shows the address — so your `print` statements look fine while your
debugger output does not. **If you only have time for one, write `__repr__`.**

**The `!r` conversion in an f-string calls `repr`,** which is what you want when building a `__repr__`
out of your own fields. `f"Money({self.amount!r}, ...)"` is why the currency shows as `'GBP'` with
quotes — the same doubled-representation rule you met in chapter 3, applied on purpose this time.

:::pitfall `repr` must not have side effects, and must not lie
Two rules, both learned by people who broke them.

`repr` is called by things you do not control: the debugger, the traceback printer, the error reporter,
a log formatter. If `__repr__` queries a database or takes a lock, then merely *looking* at an object
in a debugger can hang your program. Keep it cheap and side-effect free.

The second rule is subtler: a `__repr__` that shows a stale field is worse than no `__repr__` at all,
because you will trust it. If you cache a computed value, show the cache's state, not a field that
might not have been updated. A misleading debugger is more expensive than a missing one.
:::

## `__eq__` and `__hash__` are one contract, not two methods

This is the part of the object model that causes real bugs in real systems, so it is worth doing
slowly.

Define `__eq__` on a class and something else happens that you did not ask for:

```python run
class Money:
    def __init__(self, amount, currency="GBP"):
        self.amount = amount
        self.currency = currency

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"


print("define __eq__ and nothing else:")
print("  Money.__hash__ is None ->", Money.__hash__ is None)
try:
    {Money(1)}
except TypeError as exc:
    print("  putting one in a set raises:", exc)
print()

print("so add __hash__ over the SAME fields __eq__ compares:")


class Hashable(Money):
    def __hash__(self):
        return hash((self.amount, self.currency))


print("  equal values hash equal  ->", hash(Hashable(1)) == hash(Hashable(1)))
print("  a set collapses the pair ->", {Hashable(1), Hashable(1)})
print("  a dict finds by value    ->", {Hashable(1): "found"}[Hashable(1)])
print()

print("returning NotImplemented hands the comparison back to the other side:")
print("  Money(1) == 1 ->", Money(1) == 1)
print("  Money(1) != 1 ->", Money(1) != 1)
print()

print("the contract: a == b must imply hash(a) == hash(b)")
print("  1 == 1.0  ->", 1 == 1.0, "  hash equal ->", hash(1) == hash(1.0))
print("  True == 1 ->", True == 1, "  hash equal ->", hash(True) == hash(1))
d = {1: "one"}
print("  so one dict entry answers to all three:")
print("    d[1] ->", d[1], "   d[1.0] ->", d[1.0], "   d[True] ->", d[True])
print()

print("and the failure mode -- a hash key that can change:")


class Bad:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return hash(self.n)

    def __eq__(self, other):
        return isinstance(other, Bad) and self.n == other.n

    def __repr__(self):
        return f"Bad(n={self.n})"


k = Bad(1)
cache = {k: "computed"}
print("  stored while n == 1: cache[Bad(1)] ->", cache[Bad(1)])
k.n = 2
print("  after k.n = 2:       cache[Bad(1)] ->",
      cache.get(Bad(1), "NOT FOUND"))
print("  the entry is still in the dict:", list(cache))
print("  it sits in the bucket for hash(1); nothing can reach it by value now.")
```

```text
define __eq__ and nothing else:
  Money.__hash__ is None -> True
  putting one in a set raises: unhashable type: 'Money'

so add __hash__ over the SAME fields __eq__ compares:
  equal values hash equal  -> True
  a set collapses the pair -> {Money(1, 'GBP')}
  a dict finds by value    -> found

returning NotImplemented hands the comparison back to the other side:
  Money(1) == 1 -> False
  Money(1) != 1 -> True

the contract: a == b must imply hash(a) == hash(b)
  1 == 1.0  -> True   hash equal -> True
  True == 1 -> True   hash equal -> True
  so one dict entry answers to all three:
    d[1] -> one    d[1.0] -> one    d[True] -> one

and the failure mode -- a hash key that can change:
  stored while n == 1: cache[Bad(1)] -> computed
  after k.n = 2:       cache[Bad(1)] -> NOT FOUND
  the entry is still in the dict: [Bad(n=2)]
  it sits in the bucket for hash(1); nothing can reach it by value now.
```

**Defining `__eq__` silently sets `__hash__` to `None`.** This is not an accident. It is Python
protecting the contract: a class whose equality is defined by value, but whose hash is still
identity-based, would break every dict and set in the program. Rather than let you do that quietly, the
language makes the class unhashable and tells you at the point of use — which is, unfortunately, far
from the class definition. If you have ever seen `TypeError: unhashable type` and not understood why,
this is why.

**The contract is one-directional: `a == b` implies `hash(a) == hash(b)`.** Not the reverse — many
unequal objects may share a hash, and a dict handles that by comparing with `==` after it finds the
bucket. `1`, `1.0` and `True` are all equal to each other and all hash the same, which is why one dict
entry answers to all three names. That is the numeric tower doing exactly what the contract requires.

**`NotImplemented` is not `False`.** Returning it says "I do not know how to compare myself with this
type; ask the other operand." Python then tries the reflected operation, and if nobody knows, falls
back to identity. Returning `False` instead would claim a definite answer and would break comparisons
against types that *do* know how to compare with you. This is a one-word difference with a real
consequence, and it is the reason `Money(1) == 1` is `False` rather than an error.

**A hash key must not change.** The `Bad` class is the minimal reproduction of an entire family of
production bugs. The entry was inserted into the bucket for `hash(1)`. Then `n` changed, so the
object's hash changed, so the lookup for `Bad(1)` computes `hash(1)`, finds the right bucket, compares
`Bad(1) == k` — and `k.n` is now 2, so they are not equal. The dict probes onward and finds nothing.
**The value is still in the dict and is unreachable by value.** It will only come out if you iterate
the dict, or if it is ever garbage collected.

The fix is a rule, not a technique: **the fields that participate in `__eq__` and `__hash__` must be
immutable for the object's lifetime.** Either freeze them, or key the container on something stable
like an id.

:::danger The three ways this ships
This bug reaches production in three shapes, and all three pass tests.

**Mutable keys.** A dataclass used as a cache key gets a field that the code updates in place. Tests
construct a fresh instance for every case, so the mutation never happens in a test.

**`__hash__` over all fields.** Someone writes `def __hash__(self): return hash(tuple(vars(self)))`.
That is convenient, it works, and it silently includes every mutable field — including ones added
later by someone who has not read this chapter.

**`__eq__` that returns `False` instead of `NotImplemented`.** Comparisons against a foreign type start
returning a definite `False` where they should have deferred, and the failure appears in a library that
is comparing your object to its own.
:::

## Truthiness is a protocol too

`if x:` does not ask whether `x` is `True`. It asks the object, and the object answers.

```python run
print("__bool__ is consulted first; __len__ is the fallback")


class ByBool:
    def __bool__(self):
        return False


class ByLen:
    def __len__(self):
        return 0


class Both:
    def __bool__(self):
        return True

    def __len__(self):
        return 0


print("  bool(ByBool()) ->", bool(ByBool()))
print("  bool(ByLen())  ->", bool(ByLen()))
print("  bool(Both())   ->", bool(Both()), " <- __bool__ wins over len == 0")
print()

print("the falsy family:")
for v in (False, None, 0, 0.0, 0j, "", b"", [], (), {}, set(), frozenset()):
    print(f"  {type(v).__name__:9s} {v!r:13s} -> {bool(v)}")
print()

print("and the truthy values that surprise people:")
for v in (0.1, -1, "0", "False", [0], (0,), {0: 0}, float("nan")):
    print(f"  {type(v).__name__:9s} {v!r:13s} -> {bool(v)}")
print()

print("the trap: 0 and None are both falsy, and they mean different things")
for v in (0, None, 3):
    print(f"  v = {str(v):5s}  bool(v) = {str(bool(v)):5s}  v is None = {v is None}")
print()
print("  `if not v:` collapses 0 and None into one branch.")
print("  `if v is None:` keeps them apart. Pick one deliberately, because")
print("  'the count is zero' and 'there is no count' are different facts.")
```

```text
__bool__ is consulted first; __len__ is the fallback
  bool(ByBool()) -> False
  bool(ByLen())  -> False
  bool(Both())   -> True  <- __bool__ wins over len == 0

the falsy family:
  bool      False         -> False
  NoneType  None          -> False
  int       0             -> False
  float     0.0           -> False
  complex   0j            -> False
  str       ''            -> False
  bytes     b''           -> False
  list      []            -> False
  tuple     ()            -> False
  dict      {}            -> False
  set       set()         -> False
  frozenset frozenset()   -> False

and the truthy values that surprise people:
  float     0.1           -> True
  int       -1            -> True
  str       '0'           -> True
  str       'False'       -> True
  list      [0]           -> True
  tuple     (0,)          -> True
  dict      {0: 0}        -> True
  float     nan           -> True

the trap: 0 and None are both falsy, and they mean different things
  v = 0      bool(v) = False  v is None = False
  v = None   bool(v) = False  v is None = True
  v = 3      bool(v) = True   v is None = False

  `if not v:` collapses 0 and None into one branch.
  `if v is None:` keeps them apart. Pick one deliberately, because
  'the count is zero' and 'there is no count' are different facts.
```

The lookup order is `__bool__`, then `__len__`, then "true". A container is falsy when it is empty,
which is why every empty container in the list is falsy without anyone writing `__bool__` for it — the
`list` type defines `__len__` and the protocol uses it. `Both` proves the precedence: `__bool__` says
`True` and `len` is 0, and the object is truthy.

The `nan` row is worth a second look. `float("nan")` is not zero, so it is truthy — even though
`nan != nan` and `nan == nan` is `False`. Truthiness and equality are different protocols, and a value
can be unequal to itself while being perfectly truthy. That single fact is the reason "check for NaN"
is `math.isnan(x)` and not any comparison.

And the trap at the end is the one that costs money. `if not count:` reads naturally and means "there
is nothing here", but it also fires when the count is a genuine zero. `if count is None:` separates
"no data" from "the data says zero". Both are legitimate; writing one while meaning the other is how a
dashboard reports "no readings" for a sensor that is reading zero.

## Mutability decides what is safe to share

The last piece of the model is the one that catches people earliest: what happens when you assign one
object to two names.

```python run
print("assignment never copies")
a = [1, 2, 3]
b = a
b.append(4)
print("  a ->", a, "   b ->", b)
print("  a is b ->", a is b)
print()

print("rebinding is not mutating")
c = [1, 2, 3]
d = c
d = d + [4]
print("  c ->", c, "   d ->", d)
print("  the + built a NEW list and pointed d at it; c never moved")
print()

print("the default-argument trap")


def collect(item, into=[]):
    into.append(item)
    return into


print("  collect(1) ->", collect(1))
print("  collect(2) ->", collect(2))
print("  collect(3) ->", collect(3))
print("  the default object itself ->", collect.__defaults__[0])
print()

print("the fix")


def collect_safe(item, into=None):
    if into is None:
        into = []
    into.append(item)
    return into


print("  collect_safe(1) ->", collect_safe(1))
print("  collect_safe(2) ->", collect_safe(2))
print()

print("immutables can be shared, because sharing is invisible")
x = (1, 2, 3)
y = x
print("  x is y ->", x is y, "  and mutating is impossible, so nobody notices")
print()

print("but a tuple can still hold something mutable")
t = ([],)
t[0].append("oops")
print("  t ->", t)
print("  the tuple never changed; the list inside it did")
```

```text
assignment never copies
  a -> [1, 2, 3, 4]    b -> [1, 2, 3, 4]
  a is b -> True

rebinding is not mutating
  c -> [1, 2, 3]    d -> [1, 2, 3, 4]
  the + built a NEW list and pointed d at it; c never moved

the default-argument trap
  collect(1) -> [1]
  collect(2) -> [1, 2]
  collect(3) -> [1, 2, 3]
  the default object itself -> [1, 2, 3]

the fix
  collect_safe(1) -> [1]
  collect_safe(2) -> [2]

immutables can be shared, because sharing is invisible
  x is y -> True   and mutating is impossible, so nobody notices

but a tuple can still hold something mutable
  t -> (['oops'],)
  the tuple never changed; the list inside it did
```

`b = a` binds a second name to one list. `b.append(4)` changes that list, so `a` sees it too — not
because assignment copied anything, but because there was only ever one list. `d = d + [4]` is a
different operation: `+` builds a new list, and `d` is rebound to point at the new one. **Mutating
changes an object; rebinding changes a name.** Confusing the two is the source of most "Python
assignment is weird" complaints.

The default argument is the sharpest edge of this. **A default value is evaluated once, when the `def`
statement runs — not on each call.** So the empty list literal creates exactly one list, it is stored
on the function object in `__defaults__`, and every call that omits the argument appends to that same
list. `collect(2)` returning `[1, 2]` is the accumulated state of every previous call. The
`__defaults__` line is the evidence: the shared object now contains all three items.

The `None` sentinel is the standard fix, and it works because `None` is immutable and there is only one
of it. If `None` is a legal value for the parameter, use a module-level sentinel object instead —
Exercise 5 does both.

Immutability is what makes sharing safe. Two names for one tuple cannot diverge, because neither name
can change the tuple. That is why immutable objects are cheaper to pass around, safe to use as dict
keys, and safe to intern. But **immutability is shallow.** `t = ([],)` is an immutable tuple holding a
mutable list, and the list changed. The tuple did not — `t[0]` is still the same list object. A frozen
dataclass containing a list has exactly the same hole, which is why `frozen=True` gives you a
guarantee about the fields' *bindings* and not about the objects they point to.

:::scenario The cache that only misses in production
A team memoises an expensive pricing calculation. `Order` is a dataclass, so it has `__eq__` and
`__hash__` generated over all of its fields, `status` included:

```python
_cache = {}


def price_for(order):
    if order not in _cache:
        _cache[order] = compute_price(order)      # slow: calls a pricing service
    return _cache[order]
```

It worked for a year. Then a colleague added `order.status = "shipped"` to a fulfilment step that runs
*after* pricing.

Now the pricing service is called repeatedly for the same order, memory climbs slowly, and occasionally
a stale price is returned. The test suite is green — and every test constructs a fresh `Order`.

Why does the cache stop working, and what is the smallest fix that does not slow anything down?
:::

:::solution The key moved out of its own bucket
The cache is keyed on the object, and the object's hash changed after it was inserted. Here is the
whole failure in twelve lines:

```python run
class Order:
    def __init__(self, oid, status):
        self.oid = oid
        self.status = status

    def __hash__(self):
        return hash((self.oid, self.status))

    def __eq__(self, other):
        return (isinstance(other, Order)
                and (self.oid, self.status) == (other.oid, other.status))

    def __repr__(self):
        return f"Order({self.oid!r}, {self.status!r})"


_cache = {}
calls = []


def price_for(order):
    if order not in _cache:
        calls.append(order.oid)          # stands in for the pricing service
        _cache[order] = 100
    return _cache[order]


o = Order(7, "pending")
print("first call  ->", price_for(o), "  service calls:", len(calls))
print("second call ->", price_for(o), "  service calls:", len(calls), " (cache hit)")
o.status = "shipped"
print("after the fulfilment step sets status:")
print("  third call ->", price_for(o), "  service calls:", len(calls), " (cache MISS)")
print("  the cache now holds", len(_cache), "entries, and only one is reachable")
```

```text
first call  -> 100   service calls: 1
second call -> 100   service calls: 1  (cache hit)
after the fulfilment step sets status:
  third call -> 100   service calls: 2  (cache MISS)
  the cache now holds 2 entries, and only one is reachable
```

The first call inserted the order into the bucket for `hash((7, "pending"))`. The second call computed
the same hash, found the entry, and hit. Then `status` changed, so `hash(o)` became
`hash((7, "shipped"))` — a different bucket. The third lookup computed the *new* hash, looked in a
bucket the entry is not in, and missed. It inserted a second entry.

Three consequences, and they are all present in the report:

- **The service is called again.** Every post-fulfilment lookup is a miss, because the object's hash
  never goes back.
- **Memory climbs.** The first entry is unreachable by value forever. It is not a leak in the sense of
  a lost reference — the dict still holds it — but nothing can ever retrieve or evict it, so the dict
  grows by one entry per order and never shrinks.
- **Stale prices appear.** If two objects hash into the same bucket, the dict compares them with `==`
  to confirm. With `status` in the comparison, an order that has shipped never equals the order that
  was priced while pending — so a lookup can also land on a *different* order's entry in the same
  bucket and compare as equal if the other fields happen to match.

**Why the tests pass.** Each test builds a fresh `Order`, prices it, and asserts on the result. The
mutation happens between insertion and lookup, and no test does that. The bug needs *a mutation after
insertion*, which is exactly the thing a unit test with fresh fixtures never produces.

**The smallest fix: key on a stable value.**

```python run
class Order:
    def __init__(self, oid, status):
        self.oid = oid
        self.status = status

    def __repr__(self):
        return f"Order({self.oid!r}, {self.status!r})"


_cache = {}
calls = []


def price_for(order):
    key = order.oid                      # a stable, immutable value
    if key not in _cache:
        calls.append(key)                # stands in for the pricing service
        _cache[key] = 100
    return _cache[key]


o = Order(7, "pending")
print("first call  ->", price_for(o), "  service calls:", len(calls))
o.status = "shipped"
print("after the fulfilment step sets status:")
print("  second call ->", price_for(o), "  service calls:", len(calls), " (still a hit)")
print("  the cache still holds", len(_cache), "entry")
```

```text
first call  -> 100   service calls: 1
after the fulfilment step sets status:
  second call -> 100   service calls: 1  (still a hit)
  the cache still holds 1 entry
```

`order.oid` is an integer, so it is immutable and its hash cannot move. The cache now keys on identity
in the domain sense — "this order" — rather than on the current state of the object. Nothing got
slower, and the object is free to change as much as it likes.

Two other fixes are legitimate and worth knowing, because they apply when the situation differs.

**Exclude the mutable field from equality** — in a dataclass, `status: str = field(compare=False)`.
This works, and it says something real: *an order's identity does not include its status*. But it is
only correct if that is genuinely true. If two orders with different statuses should compare unequal,
you have just told the language a lie to make a cache work.

**Make the object immutable** — `@dataclass(frozen=True)`. This is the strongest fix, because it makes
the whole class of bug impossible rather than this instance of it. The cost is that the fulfilment step
can no longer mutate in place; it must build a new `Order` with the new status. That is often the right
change, and it is a much larger one than editing one line.

The rule that covers all three: **anything used as a hash key must be immutable for as long as it is in
the container.** The reason to prefer keying on `oid` is that it satisfies the rule without imposing a
constraint on the rest of the design — and it makes the cache's intent explicit in one line, which is
worth more than the two characters it costs.
:::

## The model in one page

Every protocol in this chapter is the same shape: the interpreter reaches a specific operation, and if
your class defines a method with the right name, yours runs instead of the default.

| You write | The interpreter uses it for | Default if absent |
|---|---|---|
| `__new__` | making the instance, before it has attributes | allocate a blank object |
| `__init__` | configuring the instance, if `__new__` returned one of ours | do nothing |
| `__repr__` | debugger, tracebacks, and containers showing their contents | class name and address |
| `__str__` | `print`, `str()`, f-strings without `!r` | fall back to `__repr__` |
| `__eq__` | `==`, `!=`, `in` on a list, dict lookups | identity |
| `__hash__` | `set`, `dict` keys, `in` on a set | identity — **but `None` if you defined `__eq__`** |
| `__bool__` | `if`, `while`, `and`, `or`, `not` | `__len__`, then true |
| `__len__` | `len()`, and truthiness when `__bool__` is absent | not supported |

The `__hash__` row is the only one with a conditional default, and it is the one that causes the most
trouble. Everything else in the table is a straightforward "define it and it runs".

## Key takeaways

- **Every value has an identity, a type and a value**, and `is`, `type()` and `==` ask about exactly
  one of them each. Same object implies equal value; equal value does not imply same object.
- **`is` is correct for `None` and for sentinels, and wrong for numbers and text.** Small-integer
  caching, interning and constant folding all make `is` *appear* to work on values, and all three are
  optimisations you are not allowed to depend on.
- **`__new__` creates, `__init__` configures, and `__init__` is skipped if `__new__` returns an object
  of a different type.** Immutable types must do all their work in `__new__`, because there is nothing
  to configure afterwards.
- **Methods are class attributes, not instance attributes.** Reading an attribute walks the instance
  dict, then the type, then the MRO; writing always lands on the instance. That chain is why a bound
  method knows its `self`, and why `obj.attr = x` shadows a class attribute without touching it.
- **Write `__repr__` even if you never write `__str__`.** Containers call `repr` on their contents, and
  `__str__` falls back to `__repr__` but not the other way round.
- **`__eq__` and `__hash__` are one contract.** Defining `__eq__` sets `__hash__` to `None`; the fields
  that feed both must be immutable for the object's lifetime, or dict and set lookups will fail in a way
  that looks like the container is broken.
- **Return `NotImplemented`, never `False`, from `__eq__` for a type you do not understand.** It hands
  the comparison to the other operand instead of claiming an answer.
- **Truthiness is a protocol:** `__bool__`, then `__len__`, then true. `0` and `None` are both falsy and
  mean different things, so choose between `if not v` and `if v is None` deliberately.
- **Mutating changes an object; rebinding changes a name.** Default arguments are evaluated once at
  `def` time, so a mutable default is shared state across every call — use a `None` sentinel.
- **Immutability is shallow.** A frozen container of mutable objects is not frozen, and `frozen=True`
  on a dataclass guarantees the bindings, not the values they point at.

## Practice

- [ ] Predict, then verify, `a == b`, `a is b` and `id(a) == id(b)` for `a = [1, 2, 3]` and
      `b = list(a)`. Explain why `list()` cannot return `a`.
- [ ] Write a class whose `__new__` returns a cached instance, so that `Config() is Config()`. Show that
      `__init__` still runs on every call, then show two ways to stop it running twice.
- [ ] Put an instance of a class that defines `__eq__` and no `__hash__` into a set, and read the exact
      error. Add `__hash__` and show the set collapsing two equal instances into one.
- [ ] Write a `__repr__` for a class such that `eval(repr(obj)) == obj`. Verify the round trip, and say
      in one sentence why `eval` on a `repr` is still not safe on untrusted input.
- [ ] Show the default-argument bug using `f.__defaults__`, then fix it two ways: with a `None`
      sentinel, and with a module-level sentinel object for when `None` is a legal value.
- [ ] Build a class that is truthy when non-empty, hashable, and equal by value. Demonstrate that two
      equal instances are interchangeable as dict keys.

## Solutions

:::solution Exercise 1
```python run
a = [1, 2, 3]
b = list(a)

print("a == b         ->", a == b)
print("a is b         ->", a is b)
print("id(a) == id(b) ->", id(a) == id(b))
print()
print("list() always builds a new list and copies the elements in.")
print("It has no way to know that its argument was already a list of")
print("the same shape, and it is not allowed to return its argument:")
print("callers mutate the result and expect the original to be untouched.")
```

```text
a == b         -> True
a is b         -> False
id(a) == id(b) -> False

list() always builds a new list and copies the elements in.
It has no way to know that its argument was already a list of
the same shape, and it is not allowed to return its argument:
callers mutate the result and expect the original to be untouched.
```

The third line is the one people expect to be `True`. It is not: `list(a)` allocated a fresh object, so
the two ids differ. If `list()` returned its argument, then `b = list(a); b.append(4)` would append to
`a`, which is precisely what every caller of `list()` is trying to avoid.

Note also that the copy is shallow. The *elements* are shared, not copied — which is invisible here
because integers are immutable, and becomes visible the moment the elements are lists.
:::

:::solution Exercise 2
```python run
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("  __new__: creating the one instance")
            cls._instance = super().__new__(cls)
        else:
            print("  __new__: handing back the existing instance")
        return cls._instance

    def __init__(self):
        print("  __init__: runs on EVERY call")
        self.loaded = True


a = Config()
b = Config()
print("a is b ->", a is b)
```

```text
  __new__: creating the one instance
  __init__: runs on EVERY call
  __new__: handing back the existing instance
  __init__: runs on EVERY call
a is b -> True
```

`a is b` is `True`, so there is one object — and `__init__` ran twice anyway. That is the rule from
this chapter in its purest form: **`__init__` is called whenever `__new__` returns an instance of the
class**, whether that instance is brand new or one that has been sitting in a cache for an hour.

Two fixes, and they suit different situations.

```python run
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_ready", False):
            return
        print("  __init__: doing the work once")
        self._ready = True


a = Config()
b = Config()
print("a is b ->", a is b, "  __init__ ran once")
```

```text
  __init__: doing the work once
a is b -> True   __init__ ran once
```

The first fix is a flag checked at the top of `__init__`: cheap, obvious, and it keeps the work inside
the method that is supposed to do it. The second is to move the construction out of `__init__`
altogether and build the object in `__new__` when it is created, leaving `__init__` empty — which is
tidier but means the instance is fully built before `__init__` ever sees it.

The reason to prefer the flag is testability. A module-level singleton is global state, and global state
that is expensive to build is global state nobody resets between tests. Whichever fix you choose, give
the class a way to be reset — a `_reset()` classmethod that clears `_instance` — or your test suite will
eventually run in an order that matters.
:::

:::solution Exercise 3
```python run
class NoHash:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if not isinstance(other, NoHash):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"{type(self).__name__}({self.x!r}, {self.y!r})"


class WithHash(NoHash):
    def __hash__(self):
        return hash((self.x, self.y))


try:
    {NoHash(1, 2)}
except TypeError as exc:
    print("__eq__ alone      ->", exc)

print("__eq__ + __hash__ ->", {WithHash(1, 2), WithHash(1, 2)})
print("hash agrees with eq ->", hash(WithHash(1, 2)) == hash(WithHash(1, 2)))
```

```text
__eq__ alone      -> unhashable type: 'NoHash'
__eq__ + __hash__ -> {WithHash(1, 2)}
hash agrees with eq -> True
```

Two equal instances went into the set and one came out, which is the whole point of hashing by value.
Note that `__hash__` is built from exactly the two fields `__eq__` compares. That is not a coincidence
to be admired; it is the contract, and a `__hash__` that reads a different set of fields is a bug that
will only show up when two equal objects land in different buckets.
:::

:::solution Exercise 4
```python run
class Matrix:
    def __init__(self, rows):
        self.rows = [list(row) for row in rows]

    def __repr__(self):
        return f"Matrix({self.rows!r})"

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.rows == other.rows


m = Matrix([[1, 2], [3, 4]])
text = repr(m)
rebuilt = eval(text)

print("repr(m)            ->", text)
print("eval(repr(m))      ->", rebuilt)
print("eval(repr(m)) == m ->", rebuilt == m)
print("rebuilt is not m   ->", rebuilt is not m)
```

```text
repr(m)            -> Matrix([[1, 2], [3, 4]])
eval(repr(m))      -> Matrix([[1, 2], [3, 4]])
eval(repr(m)) == m -> True
rebuilt is not m   -> True
```

A `repr` that survives `eval` is a useful discipline because it forces the output to be *complete* — it
must name the class and carry every field that participates in equality, with enough precision to
rebuild the object. `Matrix([[1, 2], [3, 4]])` does. A `repr` like `<Matrix 2x2>` does not, and could
not.

It is still not safe on untrusted input, because `eval` executes whatever it is given. `repr` is
trusted only because *you* wrote it; a `repr` that arrives from a log file, a network message or a
user's saved file is code, and running it is the same mistake as running any other untrusted string.
Chapter 51 takes that idea seriously; for now, the rule is that the round-trip property is a
correctness check you run in a test, not a serialisation format you ship.
:::

:::solution Exercise 5
```python run
def collect(item, acc=[]):
    acc.append(item)
    return acc


print("collect(1) ->", collect(1))
print("collect(2) ->", collect(2))
print("the shared default object:", collect.__defaults__)
print()

print("fix 1: a None sentinel, so the default itself is immutable")


def collect_none(item, acc=None):
    if acc is None:
        acc = []
    acc.append(item)
    return acc


print("  collect_none(1) ->", collect_none(1))
print("  collect_none(2) ->", collect_none(2))
print()

print("fix 2: a sentinel object, for when None is a legal value")
_SENTINEL = object()


def collect_sentinel(item, acc=_SENTINEL):
    if acc is _SENTINEL:
        acc = []
    acc.append(item)
    return acc


print("  collect_sentinel(1) ->", collect_sentinel(1))
print("  collect_sentinel(2) ->", collect_sentinel(2))
```

```text
collect(1) -> [1]
collect(2) -> [1, 2]
the shared default object: ([1, 2],)

fix 1: a None sentinel, so the default itself is immutable
  collect_none(1) -> [1]
  collect_none(2) -> [2]

fix 2: a sentinel object, for when None is a legal value
  collect_sentinel(1) -> [1]
  collect_sentinel(2) -> [2]
```

The `__defaults__` line is the proof, and it is worth reading carefully: the default is a tuple
containing one list, and that list already holds both items. The default was evaluated once, at `def`
time, and it accumulated across calls. Nothing in the function is doing anything wrong — the mistake is
that a mutable object was chosen as a default.

Between the two fixes, `None` is the right choice almost every time: it is idiomatic, it reads clearly,
and `acc is None` is unambiguous. Reach for the sentinel object only when `None` is a meaningful value
the caller might legitimately pass — collecting into a list that is deliberately `None` is unusual, but
passing `None` to mean "not supplied" versus "explicitly nothing" is a real distinction in APIs that
merge configurations.
:::

:::solution Exercise 6
```python run
class Sorted:
    def __init__(self, items=()):
        self.items = tuple(sorted(items))

    def __bool__(self):
        return bool(self.items)

    def __eq__(self, other):
        if not isinstance(other, Sorted):
            return NotImplemented
        return self.items == other.items

    def __hash__(self):
        return hash(self.items)

    def __repr__(self):
        return f"Sorted({list(self.items)!r})"


first, second = [3, 1, 2], [2, 3, 1]
a, b = Sorted(first), Sorted(second)

print("built from   ->", first, "and", second)
print("a            ->", a)
print("b            ->", b)
print("a == b       ->", a == b, " (same elements, so the same value)")
print("a is b       ->", a is b)
print("hash equal   ->", hash(a) == hash(b))
print("bool(a)      ->", bool(a), "  bool(Sorted()) ->", bool(Sorted()))
cache = {a: "computed"}
print("cache[b]     ->", cache[b], " (b found a's entry)")
```

```text
built from   -> [3, 1, 2] and [2, 3, 1]
a            -> Sorted([1, 2, 3])
b            -> Sorted([1, 2, 3])
a == b       -> True  (same elements, so the same value)
a is b       -> False
hash equal   -> True
bool(a)      -> True   bool(Sorted()) -> False
cache[b]     -> computed  (b found a's entry)
```

The class is only four methods, and the design decision that makes it work is that `items` is a
**tuple**. That single choice is what lets `__hash__` exist at all: hashing a list would raise, and
hashing a tuple of the sorted elements is stable for the object's lifetime because the tuple cannot be
mutated.

The first line of output is the one to look at. `a` and `b` were built from `[3, 1, 2]` and
`[2, 3, 1]` — different orders — and both print as `Sorted([1, 2, 3])`, because the constructor sorts.
If you compared the two `repr`s and stopped there you would have learned nothing; the interesting claim
is the next line, that objects built from differently-ordered input are *equal and hash the same*.

That is the property that makes them usable as dictionary keys. `cache[b]` found the entry `a` had
stored, and it could only do that because `a == b` and `hash(a) == hash(b)`. Had `__hash__` been left
out, `cache[b]` would raise instead — and had `__hash__` been built from the *input* list rather than
the sorted tuple, `a` and `b` would hash differently and the lookup would miss.

`__repr__` converts back to a list so the output reads as `Sorted([1, 2, 3])` — the same text you would
type to build it. `__bool__` is not strictly necessary, since `__len__` would be inferred from nothing
here and the default would be "always true" — which is exactly the bug it is preventing: an empty
`Sorted` would be truthy without it.
:::
