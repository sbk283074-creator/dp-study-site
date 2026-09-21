---
chapter: 42
part: 7
title: Descriptors
summary: One protocol — __get__, __set__ and __delete__ — is the mechanism behind bound methods, property, classmethod, staticmethod, cached_property, __slots__ and dataclass fields. Write it once and four features collapse into one idea.
minutes: 65
tags: [descriptors, protocol, property, classmethod, cached_property, __set_name__]
---

You have used `@property`, `@classmethod`, `@staticmethod` and `@cached_property`. You have called methods
and wondered, briefly, where `self` comes from. You may have written `__slots__` because a blog post said
it saves memory. These look like four features and a keyword.

They are one mechanism. And it is not a large mechanism — it is two methods, one rule about precedence,
and about forty lines to reimplement every one of those features from scratch.

The reason this matters is not elegance. It is that the rule decides which of two things wins when a
name exists in two places, and that decision is the cause of a family of bugs that are hard to find and
trivial to prevent once you can see the rule. By the end of this chapter, `TypeError: 'float' object is
not callable` — from an attribute assignment three files away — will be a diagnosis you make in seconds.

## The protocol

A **descriptor** is an object that defines any of `__get__`, `__set__` or `__delete__`, and that is
stored as a *class attribute* of another class. That is the whole definition.

- `__get__(self, obj, objtype=None)` — called when the attribute is read.
- `__set__(self, obj, value)` — called when the attribute is assigned.
- `__delete__(self, obj)` — called when the attribute is deleted.

Two names follow from that. A **data descriptor** defines `__set__` or `__delete__`. A **non-data
descriptor** defines only `__get__`. The distinction sounds like trivia and is in fact the load-bearing
rule of the entire object model.

```python run
class NonData:
    """Only __get__ -- a NON-data descriptor."""

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return "NonData.__get__ won"


class Data:
    """__get__ and __set__ -- a DATA descriptor."""

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get("_stored", "Data.__get__ won")

    def __set__(self, obj, value):
        obj.__dict__["_stored"] = f"stored by Data.__set__: {value}"


class Demo:
    non_data = NonData()
    data = Data()


d = Demo()

print("1. nothing on the instance yet -- the class is the only source")
print("   d.non_data ->", d.non_data)
print("   d.data     ->", d.data)
print()

print("2. now assign to both")
d.non_data = "plain instance attribute"
d.data = "assignment"
print("   d.__dict__ ->", d.__dict__)
print()

print("3. read them back")
print("   d.non_data ->", d.non_data, " <- the INSTANCE won")
print("   d.data     ->", d.data, " <- the DESCRIPTOR won")
print()
print("The only difference between the two classes is __set__.")
print("A data descriptor takes precedence over the instance dict.")
print("A non-data descriptor does not.")
```

```text
1. nothing on the instance yet -- the class is the only source
   d.non_data -> NonData.__get__ won
   d.data     -> Data.__get__ won

2. now assign to both
   d.__dict__ -> {'non_data': 'plain instance attribute', '_stored': 'stored by Data.__set__: assignment'}

3. read them back
   d.non_data -> plain instance attribute  <- the INSTANCE won
   d.data     -> stored by Data.__set__: assignment  <- the DESCRIPTOR won

The only difference between the two classes is __set__.
A data descriptor takes precedence over the instance dict.
A non-data descriptor does not.
```

Look carefully at the `d.__dict__` line, because it shows both behaviours at once. `non_data` landed in
the instance dictionary as an ordinary attribute. `data` did not — the assignment was intercepted by
`Data.__set__`, which stored the value under a *different* name (`_stored`) and left the public name
free for the descriptor to keep answering for.

## The lookup order, written out

This is the rule the whole chapter rests on. When Python evaluates `obj.name`, it does this, in order:

1. **`type(obj)` is searched for `name` in the MRO.** If it finds a **data descriptor**, its `__get__`
   is called and the result is returned. **Stop here — the instance dictionary is never consulted.**
2. **`obj.__dict__` is searched for `name`.** If found, that value is returned.
3. **`type(obj)` is searched again.** If it finds a **non-data descriptor**, its `__get__` is called and
   the result is returned. If it finds a plain class attribute, that is returned.
4. **`__getattr__` is called**, if the class defines it. Otherwise, `AttributeError`.

The asymmetry between steps 1 and 3 is the entire reason `__set__` exists. A non-data descriptor is a
*default* that the instance may override. A data descriptor is a *gatekeeper* that the instance cannot
override.

Assignment is simpler, and worth stating separately because it is not the mirror image you might expect.
`obj.name = value`:

1. **`type(obj)` is searched for `name`.** If it finds a **data descriptor**, its `__set__` is called.
2. Otherwise the value goes into `obj.__dict__`.

There is no step that consults a non-data descriptor, and there is no step that consults the instance
dictionary first. **Reading walks a chain of four places; writing consults at most one descriptor and
then falls through to the instance dictionary.** That difference is why a `property` with no setter
raises on assignment instead of silently creating a shadowing attribute.

## A method is a descriptor

The first payoff is that `self` stops being magic.

```python run
class Counter:
    def __init__(self):
        self.n = 0

    def bump(self):
        self.n += 1
        return self.n


c = Counter()

print("a function has __get__ ->", hasattr(Counter.bump, "__get__"))
print("a function has __set__ ->", hasattr(Counter.bump, "__set__"))
print("so a function is a NON-data descriptor, and that is all a method is.")
print()

bound = Counter.bump.__get__(c, Counter)
print("calling __get__ by hand builds the bound method:")
print("  type(bound).__name__   ->", type(bound).__name__)
print("  bound.__self__ is c    ->", bound.__self__ is c)
print("  bound.__func__.__name__->", bound.__func__.__name__)
print("  bound()                ->", bound())
print()

print("accessed on the CLASS, __get__ receives obj=None and hands back")
print("the plain function:")
print("  Counter.bump.__name__        ->", Counter.bump.__name__)
print("  Counter.bump is bound.__func__ ->", Counter.bump is bound.__func__)
print()

print("So `self` is not a keyword and not an argument you pass. It is")
print("whatever __get__ was given when the attribute was looked up.")
```

```text
a function has __get__ -> True
a function has __set__ -> False
so a function is a NON-data descriptor, and that is all a method is.

calling __get__ by hand builds the bound method:
  type(bound).__name__   -> method
  bound.__self__ is c    -> True
  bound.__func__.__name__-> bump
  bound()                -> 1

accessed on the CLASS, __get__ receives obj=None and hands back
the plain function:
  Counter.bump.__name__        -> bump
  Counter.bump is bound.__func__ -> True

So `self` is not a keyword and not an argument you pass. It is
whatever __get__ was given when the attribute was looked up.
```

Three things follow immediately.

**`Counter.bump(c)` and `c.bump()` do different things.** The first gets the plain function from the
class and passes `c` explicitly. The second goes through the descriptor protocol and gets a method that
already remembers `c`. Exercise 6 makes this concrete by showing why `Counter.bump()` on its own fails.

**A function is a *non-data* descriptor, so an instance attribute can shadow a method.** This is not a
footnote. It is the cause of one of the most confusing errors in the language, and the last section of
this chapter is about it.

**Every callable attribute is this same mechanism.** A `lambda` assigned in a class body is a function
and therefore a descriptor. A callable object that is not a function is *not* a descriptor, so assigning
it in a class body gives you the object itself with no binding — which is why `functools.partial` in a
class body behaves differently from a `def`.

## `property` from scratch

The built-in `property` is a data descriptor. Here is a working one, and then the reason it needs
`__set__`.

```python run
class computed:
    """A minimal property: __get__ only, so a NON-data descriptor."""

    def __init__(self, fget):
        self.fget = fget
        self.__doc__ = fget.__doc__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @computed
    def area(self):
        return round(3.141592653589793 * self.radius ** 2, 4)


c = Circle(2)
print("a working computed attribute: c.area ->", c.area)
print()
print("but it can be overwritten, because a non-data descriptor loses to")
print("the instance dict:")
c.area = 999
print("  after c.area = 999 ->", c.area)
print("  c.__dict__ ->", c.__dict__)
print()

print("the real property closes that hole with __set__:")


class readonly:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)

    def __set__(self, obj, value):
        raise AttributeError("property has no setter")


class Circle2:
    def __init__(self, radius):
        self.radius = radius

    @readonly
    def area(self):
        return round(3.141592653589793 * self.radius ** 2, 4)


c2 = Circle2(2)
print("  c2.area ->", c2.area)
try:
    c2.area = 999
except AttributeError as exc:
    print("  c2.area = 999 ->", exc)
print()
print("and the built-in property is the same object, in C:")


class Circle3:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return round(3.141592653589793 * self.radius ** 2, 4)


c3 = Circle3(2)
print("  c3.area ->", c3.area)
try:
    c3.area = 999
except AttributeError as exc:
    print("  c3.area = 999 ->", exc)
```

```text
a working computed attribute: c.area -> 12.5664

but it can be overwritten, because a non-data descriptor loses to
the instance dict:
  after c.area = 999 -> 999
  c.__dict__ -> {'radius': 2, 'area': 999}

the real property closes that hole with __set__:
  c2.area -> 12.5664
  c2.area = 999 -> property has no setter

and the built-in property is the same object, in C:
  c3.area -> 12.5664
  c3.area = 999 -> property 'area' of 'Circle3' object has no setter
```

`computed` worked perfectly until someone assigned to it — and then it stopped working *silently*. That
is the danger of a non-data descriptor: it is a default, not a guarantee. `c.area = 999` did not raise,
did not warn, and did not run the getter again. It created an instance attribute that now shadows the
descriptor forever, and the object quietly started lying.

`readonly` fixes that with four lines, and the four lines are the whole difference. Because it defines
`__set__`, it is a data descriptor, so step 1 of the read order finds it before the instance dictionary
is ever consulted. The stale value can be written — but it can never be *read*, because the descriptor
wins every time.

The real `property` is this object in C. The only visible difference is the error message, which names
the class and the attribute. That difference is worth having, and it is why you should use the built-in
unless you need behaviour it does not offer.

:::tip `@property` for computation, not for storage
A `property` is right when reading an attribute should *compute* something — a derived value, a
validated read, a value assembled from several fields. It is the wrong tool for hiding a plain attribute
behind a getter and setter pair, which is a Java habit that costs you a lookup on every access and buys
nothing in Python.

The sign that you have gone wrong: a property whose getter is `return self._x` and whose setter is
`self._x = value` with no logic in between. Delete both and use the attribute.
:::

## `classmethod` and `staticmethod` from scratch

Both are small, and the contrast between them is the clearest way to see what binding means.

```python run
from types import MethodType


class my_classmethod:
    """Binds the CLASS instead of the instance."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        return MethodType(self.func, objtype)


class my_staticmethod:
    """Binds nothing at all -- returns the function unchanged."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        return self.func


class Temperature:
    unit = "C"

    def __init__(self, celsius):
        self.celsius = celsius

    @my_classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @my_staticmethod
    def is_freezing(kelvin):
        return kelvin <= 273.15


t = Temperature.from_fahrenheit(212)
print("Temperature.from_fahrenheit(212) ->", round(t.celsius, 6), "degrees C")
print("it built a", type(t).__name__, "with no instance involved")
print()

print("my_classmethod bound the class, so `cls` is Temperature:")
print("  Temperature.unit ->", Temperature.unit)
print("  a subclass would be passed instead:")


class Fahrenheit(Temperature):
    unit = "F"


print("  Fahrenheit.from_fahrenheit(212).unit ->",
      Fahrenheit.from_fahrenheit(212).unit)
print()

print("my_staticmethod bound nothing, so there is no first argument:")
print("  Temperature.is_freezing(273.0) ->", Temperature.is_freezing(273.0))
print("  Temperature.is_freezing(300.0) ->", Temperature.is_freezing(300.0))
print("  Temperature(20).is_freezing(273.0) ->",
      Temperature(20).is_freezing(273.0))
print("  the last call went through an instance, and it made no difference")
print()

print("the built-ins behave identically:")


class Real:
    @classmethod
    def cm(cls):
        return cls.__name__

    @staticmethod
    def sm():
        return "no self, no cls"


print("  Real.cm()    ->", Real.cm(), "   Real().cm() ->", Real().cm())
print("  Real.sm()    ->", Real.sm())
```

```text
Temperature.from_fahrenheit(212) -> 100.0 degrees C
it built a Temperature with no instance involved

my_classmethod bound the class, so `cls` is Temperature:
  Temperature.unit -> C
  a subclass would be passed instead:
  Fahrenheit.from_fahrenheit(212).unit -> F

my_staticmethod bound nothing, so there is no first argument:
  Temperature.is_freezing(273.0) -> True
  Temperature.is_freezing(300.0) -> False
  Temperature(20).is_freezing(273.0) -> True
  the last call went through an instance, and it made no difference

the built-ins behave identically:
  Real.cm()    -> Real    Real().cm() -> Real
  Real.sm()    -> no self, no cls
```

`my_classmethod.__get__` builds `MethodType(self.func, objtype)` — a method bound to the *class*. That is
the whole implementation. The reason `cls` is the subclass when you call
`Fahrenheit.from_fahrenheit(...)` is not special-casing; it is that `objtype` was `Fahrenheit` when the
lookup happened. An inherited classmethod knows which class you reached it through, and that is what
makes the "alternative constructor" pattern work with subclasses.

`my_staticmethod.__get__` returns `self.func` and does nothing else. No binding happens, so the function
is called with exactly the arguments you gave it. It is the one descriptor in the standard library whose
`__get__` is a no-op, and that is the entire difference between it and a plain function assigned in a
class body — a plain function would get bound and would receive a spurious first argument.

Neither of these defines `__set__`, so both are non-data descriptors. You can shadow
`Temperature.from_fahrenheit` on an instance, and that is occasionally useful for stubbing in tests.

## `cached_property`: a descriptor that deletes itself

This is the most elegant use of the rule in the standard library, and it only works because of the
non-data descriptor precedence.

```python run
from functools import cached_property


class my_cached_property:
    def __init__(self, func):
        self.func = func
        self.attrname = None

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.attrname] = value
        return value


class Dataset:
    def __init__(self, rows):
        self.rows = rows
        self.computations = 0

    @my_cached_property
    def summary(self):
        self.computations += 1
        return f"n={len(self.rows)} sum={sum(self.rows)}"


d = Dataset([1, 2, 3, 4])
print("first  access ->", d.summary)
print("second access ->", d.summary)
print("third  access ->", d.summary)
print("the expensive function ran", d.computations, "time(s)")
print()
print("d.__dict__ ->", d.__dict__)
print()
print("From the second access on, the descriptor is never consulted:")
print("the value is in the instance dict, and a NON-data descriptor")
print("loses to the instance dict. The cache IS the shadowing rule.")
print()


class Same:
    def __init__(self, rows):
        self.rows = rows
        self.computations = 0

    @cached_property
    def summary(self):
        self.computations += 1
        return f"n={len(self.rows)} sum={sum(self.rows)}"


s = Same([1, 2, 3, 4])
s.summary
s.summary
s.summary
print("functools.cached_property behaves the same: ran",
      s.computations, "time(s)")
print("  s.__dict__ ->", s.__dict__)
```

```text
first  access -> n=4 sum=10
second access -> n=4 sum=10
third  access -> n=4 sum=10
the expensive function ran 1 time(s)

d.__dict__ -> {'rows': [1, 2, 3, 4], 'computations': 1, 'summary': 'n=4 sum=10'}

From the second access on, the descriptor is never consulted:
the value is in the instance dict, and a NON-data descriptor
loses to the instance dict. The cache IS the shadowing rule.

functools.cached_property behaves the same: ran 1 time(s)
  s.__dict__ -> {'rows': [1, 2, 3, 4], 'computations': 1, 'summary': 'n=4 sum=10'}
```

Read what `__get__` does: it computes the value, **writes it into the instance dictionary under its own
name**, and returns it. On the next access, the read order reaches step 2 — the instance dictionary —
finds the value, and returns it. Step 3 is never reached, so `__get__` never runs again.

The descriptor does not implement a cache. It implements a *self-erasing* descriptor, and it gets the
cache for free from the precedence rule. `cached_property` is one of the few places in the standard
library where a design is this much cleverer than it needs to be, and it is worth understanding rather
than merely using.

Two consequences follow, and both are real traps.

**Invalidating the cache means deleting the attribute.** `del d.summary` removes the instance entry, and
the descriptor starts answering again. There is no `d.summary.invalidate()`, because the cache is not an
object — it is a dictionary key.

**`cached_property` needs an instance `__dict__`,** so it breaks on a class with `__slots__`. That is the
next section.

## `__set_name__`: a descriptor that learns its own name

`cached_property` above used `__set_name__` to find out what it was called. This is a separate hook the
class machinery calls during class creation.

```python run
class Field:
    def __set_name__(self, owner, name):
        self.name = name
        print(f"  __set_name__: {owner.__name__}.{name}")

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value

    def __repr__(self):
        return f"Field({self.name!r})"


print("the class body runs, and each Field is told its own name:")


class Config:
    host = Field()
    port = Field()


print()
print("so a descriptor can store under its own name without the user")
print("ever repeating it:")
print("  Config.host ->", Config.host)
print("  Config.port ->", Config.port)
print()
c = Config()
c.host = "localhost"
c.port = 8080
print("  c.host ->", c.host)
print("  c.port ->", c.port)
print("  c.__dict__ ->", c.__dict__)
print()
print("Note the storage name and the attribute name are the same, and the")
print("descriptor worked that out on its own. That is what __set_name__ is")
print("for, and it is how dataclasses and Django-style models work.")
```

```text
the class body runs, and each Field is told its own name:
  __set_name__: Config.host
  __set_name__: Config.port

so a descriptor can store under its own name without the user
ever repeating it:
  Config.host -> Field('host')
  Config.port -> Field('port')

  c.host -> localhost
  c.port -> 8080
  c.__dict__ -> {'host': 'localhost', 'port': 8080}

Note the storage name and the attribute name are the same, and the
descriptor worked that out on its own. That is what __set_name__ is
for, and it is how dataclasses and Django-style models work.
```

`__set_name__(self, owner, name)` is called once per descriptor, during class creation, after the class
body has run. Before it existed (Python 3.6), a reusable descriptor had to be told its name explicitly —
`host = Field("host")` — which is redundant and easy to get wrong when you rename the attribute. Now the
descriptor discovers its own name, which is why the pattern is usable in a library.

The sequence at class creation is worth knowing: the class body executes, then `__set_name__` is called
on every value in the namespace that defines it, then the class is bound. `owner` is the class being
created, and `name` is the attribute name it was assigned to.

## Where this rule bites

Three interactions cause most of the real bugs, and all three are consequences of the read and write
orders rather than of anything specific to descriptors.

```python run
from functools import cached_property


print("1. cached_property caches by writing into the instance __dict__")
print("   a class with __slots__ and no __dict__ has nowhere to put it:")


class WithSlots:
    __slots__ = ("rows",)

    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def summary(self):
        return sum(self.rows)


try:
    WithSlots([1, 2, 3]).summary
except TypeError as exc:
    print("   TypeError:", exc)
print()


print("2. adding __dict__ to __slots__ fixes it, and gives back the memory")
print("   you were trying to save:")


class WithBoth:
    __slots__ = ("rows", "__dict__")

    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def summary(self):
        return sum(self.rows)


w = WithBoth([1, 2, 3])
print("   summary  ->", w.summary)
print("   __dict__ ->", w.__dict__)
print()


print("3. the expensive version of the same rule: an instance attribute")
print("   that shadows a method, because a function is a NON-data")
print("   descriptor and loses to the instance dict")


class Cart:
    def __init__(self, items):
        self.items = items

    def total(self):
        return sum(self.items)


c = Cart([1, 2, 3])
print("   c.total() ->", c.total())

c.total = 6.0
print("   after c.total = 6.0, c.total ->", c.total)
try:
    c.total()
except TypeError as exc:
    print("   c.total() ->", exc)
print()

print("4. a property cannot be shadowed, because it is a DATA descriptor")


class SafeCart:
    def __init__(self, items):
        self.items = items

    @property
    def total(self):
        return sum(self.items)


s = SafeCart([1, 2, 3])
print("   s.total ->", s.total)
try:
    s.total = 6.0
except AttributeError as exc:
    print("   s.total = 6.0 ->", exc)
print("   the mistake is impossible rather than merely discouraged")
```

```text
1. cached_property caches by writing into the instance __dict__
   a class with __slots__ and no __dict__ has nowhere to put it:
   TypeError: No '__dict__' attribute on 'WithSlots' instance to cache 'summary' property.

2. adding __dict__ to __slots__ fixes it, and gives back the memory
   you were trying to save:
   summary  -> 6
   __dict__ -> {'summary': 6}

3. the expensive version of the same rule: an instance attribute
   that shadows a method, because a function is a NON-data
   descriptor and loses to the instance dict
   c.total() -> 6
   after c.total = 6.0, c.total -> 6.0
   c.total() -> 'float' object is not callable

4. a property cannot be shadowed, because it is a DATA descriptor
   s.total -> 6
   s.total = 6.0 -> property 'total' of 'SafeCart' object has no setter
   the mistake is impossible rather than merely discouraged
```

Each of these is worth one sentence of explanation.

**`__slots__` is itself implemented with descriptors.** Declaring `__slots__ = ("rows",)` creates a
`member_descriptor` named `rows` on the class, which is a *data* descriptor. That is why a slot can be
read and written but not added, and why a slot always wins over the instance dictionary — the instance
has none. It is also why `cached_property` fails there: `cached_property.__get__` writes to
`obj.__dict__`, and there is no such dictionary.

**Adding `"__dict__"` to `__slots__` is legal, and cancels the benefit.** You get the smaller fixed part
of the object plus a dictionary allocated on first use, which is exactly what you had before. If you
need `cached_property` and `__slots__` together, the honest answer is that you do not need `__slots__`.

**The shadowing bug is the expensive one**, and section 3 shows why. `c.total` stopped being a method
and became a float. The failure surfaces later, at a call site that looks correct, with a message about
a float not being callable — and nothing in that message mentions `Cart`, the assignment, or the fact
that a method was replaced.

:::scenario Only some carts crash
A checkout service has a `Cart` with a method `total()` that sums the items. It has worked for two
years.

A performance change adds a `refresh()` that computes the total once and stores it, so the template can
read it without recomputing:

```python
def refresh(self):
    self.total = sum(self.items)
```

Everything looks right. `cart.total` returns the correct number in every test. Then the order-confirmation
page starts raising `TypeError: 'float' object is not callable` — but only for carts that were refreshed.
Carts that were never refreshed work fine.

What is happening, and what is the fix that prevents it from coming back?
:::

:::solution A method is a non-data descriptor, so the attribute won
`cart.total` is not calling a method any more. It is reading a float that was written into the instance
dictionary, and the instance dictionary wins over a non-data descriptor. The method is still on the
class; it has simply become unreachable through that instance.

The reason only refreshed carts fail is the reason the bug is hard to find. Before `refresh()` runs, the
instance dictionary has no `total` key, so the lookup falls through to the class and finds the function,
which is bound into a method. After `refresh()` runs, step 2 of the read order finds the float and
returns it. Same class, same attribute name, two different behaviours depending on which code path ran.

The minimal reproduction is four lines:

```python run
class Cart:
    def __init__(self, items):
        self.items = items

    def total(self):
        return sum(self.items)

    def refresh(self):
        self.total = sum(self.items)


c = Cart([1, 2, 3])
print("before refresh: type(c.total).__name__ ->", type(c.total).__name__)
c.refresh()
print("after refresh:  type(c.total).__name__ ->", type(c.total).__name__)
print("                c.total ->", c.total)
try:
    c.total()
except TypeError as exc:
    print("and c.total() ->", exc)
```

```text
before refresh: type(c.total).__name__ -> method
after refresh:  type(c.total).__name__ -> int
                c.total -> 6
and c.total() -> 'int' object is not callable
```

The type changing from `method` to `int` is the first clue worth noticing: the name did not stop
working, it started meaning something else. The `TypeError` then names `int` and never mentions `Cart`,
which is why the message reads as unrelated to the change that caused it.

**Three fixes, in order of how much they buy.**

**Rename the attribute.** `self._total = ...` or `self.cached_total = ...`. This is the smallest change,
it costs nothing at runtime, and it removes the collision permanently. The leading underscore also
signals that it is state rather than an operation, which is a convention worth keeping.

**Make the method a `property`.** A property is a *data* descriptor, so it takes precedence over the
instance dictionary and cannot be shadowed. Assigning to it would call the setter, or raise if there is
none — the mistake becomes an immediate, loud error at the line that makes it, instead of a `TypeError`
three files away at the line that notices.

**Give the class a `__slots__` that omits `total`.** A slot is a data descriptor too, so the same
protection applies, plus you get the memory saving. But this only works if the class can afford
`__slots__` at all, which the next section shows is not always true.

The rule to carry: **never assign to an instance attribute whose name matches a method on the class.**
When you want a computed value to be readable like an attribute, write a `property` — that is exactly
what `property` is for, and it makes the collision impossible rather than merely unlikely.
:::

:::pitfall The three ways this rule surprises people
**A non-data descriptor is a default, not a guarantee.** If your descriptor only defines `__get__`, any
code anywhere can replace it with `obj.name = ...` and your descriptor will never run again. Add a
`__set__` that raises if that must not happen. `computed` earlier in this chapter is the cautionary
example: it worked until the first assignment, then silently stopped.

**`__set__` is not called when the attribute is set on the class.** `Demo.data = something` replaces the
descriptor for every instance, because class-level assignment is an ordinary namespace operation and the
descriptor protocol does not apply. This is how monkey-patching works, and it is also how a stray class
attribute assignment breaks every instance at once.

**Reading a descriptor on the class passes `obj=None`.** That is why every descriptor in this chapter
begins with `if obj is None: return self`. Forget it and `Config.host` raises an `AttributeError` inside
your getter — during class creation, in some cases, which produces an error message that names the wrong
line entirely.
:::

## Key takeaways

- **A descriptor is an object with `__get__`, `__set__` or `__delete__`, stored as a class attribute.**
  That is the entire protocol, and it is the mechanism behind methods, `property`, `classmethod`,
  `staticmethod`, `cached_property`, `__slots__` and dataclass fields.
- **A data descriptor defines `__set__` or `__delete__`; a non-data descriptor defines only `__get__`.**
  The distinction decides which of two values wins, and it is the load-bearing rule of the object model.
- **The read order is: data descriptor on the type, then the instance dictionary, then a non-data
  descriptor or class attribute, then `__getattr__`.** The instance dictionary sits *between* the two
  kinds of descriptor, and that position is why `__set__` matters.
- **The write order is shorter: a data descriptor's `__set__` if one exists, otherwise the instance
  dictionary.** A non-data descriptor is never consulted on assignment.
- **A function is a non-data descriptor,** which is what a method is: `__get__` binds the instance and
  returns an object that remembers it. `self` is not a keyword — it is whatever `__get__` was given.
- **`classmethod` binds the class, `staticmethod` binds nothing,** and both are about ten lines. The
  subclass-aware behaviour of a classmethod comes from `objtype` being the class you reached it through.
- **`cached_property` is a self-erasing descriptor.** It writes its result into the instance dictionary,
  which then shadows it — so the cache is the precedence rule, and invalidating it means `del obj.name`.
- **`__set_name__(self, owner, name)` runs once during class creation,** letting a descriptor discover
  its own attribute name. Without it, every reusable descriptor would have to be told its name twice.
- **`__slots__` is implemented with data descriptors,** which is why a slot beats the instance dictionary
  and why `cached_property` raises `TypeError` on a slotted class: there is no `__dict__` to cache into.
- **Never assign to an instance attribute whose name matches a method.** It shadows the method silently,
  and the failure surfaces later and elsewhere. Use a `property` when a computed value should read like
  an attribute — a property is a data descriptor, so the collision is impossible.

## Practice

- [ ] Write a descriptor that logs every read and every write, attach two of them to a class, and show
      the log. Use `__set_name__` so it stores under a private name.
- [ ] Implement `property` with a setter, so that `@x.setter` works and the setter validates its input.
      Show a rejected assignment.
- [ ] Write your own non-data and data descriptors, and demonstrate the precedence rule with a value
      placed in the instance dictionary directly.
- [ ] Use `__set_name__` to build a descriptor whose public name is `name` and whose storage name is
      `_name`, and show that the public name never appears in the instance dictionary.
- [ ] Reproduce the `cached_property` plus `__slots__` `TypeError`, then fix it two ways and say which
      you would ship.
- [ ] Explain why `Counter.bump.__get__(Counter(), Counter)()` works while `Counter.bump()` raises, and
      relate the answer to where `self` comes from.

## Solutions

:::solution Exercise 1
```python run
class Logged:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        print(f"    read  {self.name[1:]}")
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        print(f"    write {self.name[1:]} = {value!r}")
        setattr(obj, self.name, value)


class Config:
    host = Logged()
    port = Logged()


c = Config()
c.host = "localhost"
c.port = 8080
print("  c.host ->", c.host)
print("  c.port ->", c.port)
print("  c.__dict__ ->", c.__dict__)
```

```text
    write host = 'localhost'
    write port = 8080
    read  host
  c.host -> localhost
    read  port
  c.port -> 8080
  c.__dict__ -> {'_host': 'localhost', '_port': 8080}
```

The log shows the interception working exactly as the protocol describes. The two assignments printed
`write` lines and no `read` lines, because assignment never consults a getter. The two reads printed
`read` lines, and the values came back from `_host` and `_port` rather than from the public names.

`__set_name__` is doing the useful work here: the descriptor stores under `"_" + name`, so it knows both
names from a single declaration. `Config.host` and `c.host` both resolve to the same descriptor object,
and neither the class nor the caller had to say `"host"` twice.

The `if obj is None: return self` guard is not optional. Without it, `Config.host` — a read on the class
rather than on an instance — would call `getattr(None, "_host")` and raise `AttributeError` during
class-body evaluation, producing an error that points at the class definition rather than at the guard.
:::

:::solution Exercise 2
```python run
class validated:
    def __init__(self, fget):
        self.fget = fget
        self.fset = None

    def setter(self, fset):
        self.fset = fset
        return self

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)


class Person:
    def __init__(self, age):
        self.age = age

    @validated
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if not isinstance(value, int):
            raise TypeError("age must be an int")
        if value < 0:
            raise ValueError("age cannot be negative")
        self._age = value


p = Person(30)
print("  p.age ->", p.age)
p.age = 31
print("  after p.age = 31 ->", p.age)
for bad in (-1, "old"):
    try:
        p.age = bad
    except (TypeError, ValueError) as exc:
        print(f"  p.age = {bad!r} -> {type(exc).__name__}: {exc}")
print("  p.__dict__ ->", p.__dict__)
```

```text
  p.age -> 30
  after p.age = 31 -> 31
  p.age = -1 -> ValueError: age cannot be negative
  p.age = 'old' -> TypeError: age must be an int
  p.__dict__ -> {'_age': 31}
```

The trick is in the decorator ordering. `@validated` replaces `age` in the class namespace with the
descriptor object. The second `@age.setter` then calls `.setter(...)` on *that descriptor* — not on the
function — because by then the name `age` refers to the descriptor. `setter` returns `self`, so the name
ends up back at the same descriptor, now with both halves filled in.

That is exactly how the built-in `property.setter` works, and it is why the standard idiom is to reuse
the same name three times. Nothing is being overwritten: the descriptor is being configured in place.

The validation lives in `__set__`, which is why `Person(30)` in `__init__` was validated too — the
constructor assigns through the same gate as any later assignment. And `p.__dict__` shows `_age` only:
the public name never appears in the instance dictionary, because a data descriptor is always consulted
first.
:::

:::solution Exercise 3
```python run
class NonData:
    def __get__(self, obj, objtype=None):
        return "descriptor"


class Data:
    def __get__(self, obj, objtype=None):
        return "descriptor"

    def __set__(self, obj, value):
        obj.__dict__["_d"] = value


class C:
    a = NonData()
    b = Data()


c = C()
c.__dict__["a"] = "instance"
c.__dict__["b"] = "instance"
print("  c.a ->", c.a, " <- the instance dict wins")
print("  c.b ->", c.b, " <- the data descriptor wins")
```

```text
  c.a -> instance  <- the instance dict wins
  c.b -> descriptor  <- the data descriptor wins
```

Both attributes were given a value in the instance dictionary, by the same line of code, and they came
back differently. The only difference is `__set__` on `Data`.

Writing `c.__dict__["b"] = "instance"` directly is the point of the exercise: it bypasses `Data.__set__`,
so it demonstrates that the precedence comes from the *read* order rather than from assignment being
intercepted. Even with a value sitting in the instance dictionary, the data descriptor wins the read.

If you used `c.b = "instance"` instead, `Data.__set__` would have run and stored `"instance"` under
`_d` — a different outcome, and worth trying to see that assignment and reading follow different rules.
:::

:::solution Exercise 4
```python run
class Private:
    def __set_name__(self, owner, name):
        self.public = name
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        setattr(obj, self.private, value)


class Settings:
    theme = Private()
    language = Private()


s = Settings()
s.theme = "dark"
s.language = "en"
print("  s.theme ->", s.theme, "  s.language ->", s.language)
print("  s.__dict__ ->", s.__dict__)
```

```text
  s.theme -> dark   s.language -> en
  s.__dict__ -> {'_theme': 'dark', '_language': 'en'}
```

The instance dictionary contains only the private names, which is the property that makes this pattern
useful: the public attribute is a pure interface with no storage of its own, so every read and write goes
through the descriptor and can be validated, logged or converted.

This is the shape of Django's model fields, SQLAlchemy's columns, and `dataclasses.field`. In each case
the descriptor holds the metadata, the instance holds a plain value under a different name, and the
class-level name is the only thing user code touches.

`getattr(obj, self.private, None)` returns `None` for an unset field rather than raising, which is a
deliberate choice: an unset setting is a normal state. Returning `None` rather than raising is the right
default for configuration and the wrong one for a required field — in that case, raise, and raise with a
message that names the field.
:::

:::solution Exercise 5
```python run
from functools import cached_property


class Broken:
    __slots__ = ("rows",)

    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def total(self):
        return sum(self.rows)


try:
    Broken([1, 2]).total
except TypeError as exc:
    print("  with __slots__ only   ->", exc)


class FixDict:
    __slots__ = ("rows", "__dict__")

    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def total(self):
        return sum(self.rows)


print("  fix 1: add __dict__   ->", FixDict([1, 2]).total)


class FixPlain:
    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def total(self):
        return sum(self.rows)


print("  fix 2: drop __slots__ ->", FixPlain([1, 2]).total)
```

```text
  with __slots__ only   -> No '__dict__' attribute on 'Broken' instance to cache 'total' property.
  fix 1: add __dict__   -> 3
  fix 2: drop __slots__ -> 3
```

Both fixes work, and I would ship neither of them as the first move. Fix 1 adds `__dict__` back, which
allocates a dictionary per instance on first use — the exact cost `__slots__` was added to avoid. Fix 2
throws away the memory saving entirely. In both cases you have `__slots__` and you do not have what it
was for.

The question to ask is *why* the class has `__slots__`. If it is a class with a handful of instances,
`__slots__` was a mistake and fix 2 is correct. If it is a class with a million instances, then the right
answer is usually the third one: **do not cache on the instance at all.** Compute the value where it is
needed, or cache it in a separate structure keyed by whatever identifies the object, or make the value a
plain attribute computed once at construction.

A `cached_property` is an optimisation for a class that is constructed rarely and read often. A class
with `__slots__` is one that exists in enormous numbers. Those two descriptions rarely apply to the same
class, and the `TypeError` is Python telling you that you have asked for both.
:::

:::solution Exercise 6
```python run
class Counter:
    def bump(self):
        return "bumped"


print("  Counter.bump.__get__(Counter(), Counter)() ->",
      Counter.bump.__get__(Counter(), Counter)())
try:
    Counter.bump()
except TypeError as exc:
    print("  Counter.bump() ->", exc)
```

```text
  Counter.bump.__get__(Counter(), Counter)() -> bumped
  Counter.bump() -> Counter.bump() missing 1 required positional argument: 'self'
```

`Counter.bump` is the plain function, reached by reading an attribute on the class. Reading it there
passes `obj=None` to `__get__`, and a function's `__get__` returns itself when there is no instance to
bind. So `Counter.bump` is a function with one required parameter, `self`.

Calling it with no arguments therefore raises — and the error message names `self`, which is the clue.
Nothing is wrong with the function; it is simply waiting for an argument that the descriptor protocol
would normally have supplied.

`Counter.bump.__get__(Counter(), Counter)` calls the protocol by hand. `__get__` receives an instance,
builds a bound method, and returns it. Calling *that* supplies the instance as the first argument, so
`self` is filled in.

The lesson is that the binding is an *attribute access* step, not a *call* step. `c.bump` performs the
binding; `c.bump()` performs the binding and then calls the result. That is why
`m = c.bump; m()` works, why `m.__self__` is `c`, and why storing `c.bump` keeps the instance alive —
a bound method is a strong reference to its instance, which is exactly the kind of unnoticed reference
Chapter 41 warned about.
:::
