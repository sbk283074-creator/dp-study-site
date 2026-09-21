---
chapter: 43
part: 7
title: Metaclasses and Class Creation
summary: A class is an object made by a callable, and that callable is the metaclass. See the whole creation sequence, build a registry and a validator, and learn the four-step ladder that tells you when the answer is "do not".
minutes: 60
tags: [metaclasses, type, __init_subclass__, __prepare__, class creation, abc]
---

Chapter 42 showed that a class attribute can intercept access. This chapter takes the step before that:
what happens when the class itself is created.

There is a fact in here that rearranges how the language looks. **A class is an object, and it was
produced by calling something.** That something is the class's *metaclass*, and by default it is `type`.
Every `class` statement you have ever written is a call in disguise.

Metaclasses have a reputation for being advanced and dangerous, and half of that reputation is earned.
The other half comes from people reaching for a metaclass when a decorator or `__init_subclass__` would
have been clearer. So this chapter does two things: it shows you the whole mechanism, and it gives you a
ladder to climb before you use it — with the honest answer that step three is where most real problems
stop.

## `type` is a class, and a class is an instance of it

`type(x)` normally answers "what kind of thing is this". It has a second job.

```python run
class Statement:
    """Built with the class statement."""
    kind = "statement"

    def describe(self):
        return f"I am a {self.kind}"


def describe(self):
    return f"I am a {self.kind}"


Built = type("Built", (), {"kind": "type()", "describe": describe})

print("type(Statement) ->", type(Statement).__name__)
print("type(Built)     ->", type(Built).__name__)
print("type(3)         ->", type(3).__name__)
print()
print("so a class is an instance of type, and `type` is itself a class:")
print("  isinstance(Statement, type) ->", isinstance(Statement, type))
print("  isinstance(Built, type)     ->", isinstance(Built, type))
print("  isinstance(Statement, object) ->", isinstance(Statement, object))
print()
print("and both classes behave identically:")
print("  Statement().describe() ->", Statement().describe())
print("  Built().describe()     ->", Built().describe())
print()
print("`class Foo(Base): ...` is sugar for three arguments -- a name, a")
print("tuple of bases, and a namespace dict -- handed to a callable that")
print("produces the class. That callable is the metaclass, and by default")
print("it is `type` itself.")
```

```text
type(Statement) -> type
type(Built)     -> type
type(3)         -> int

so a class is an instance of type, and `type` is itself a class:
  isinstance(Statement, type) -> True
  isinstance(Built, type)     -> True
  isinstance(Statement, object) -> True

and both classes behave identically:
  Statement().describe() -> I am a statement
  Built().describe()     -> I am a type()

`class Foo(Base): ...` is sugar for three arguments -- a name, a
tuple of bases, and a namespace dict -- handed to a callable that
produces the class. That callable is the metaclass, and by default
it is `type` itself.
```

`type("Built", (), {...})` is the same operation the compiler performs for a `class` statement. The
statement form exists because writing the namespace as a dict literal would be miserable for anything
larger than a toy — but the two produce equivalent objects, and the second line of output is the proof.

Two consequences follow, and they are the reason metaclasses are possible at all.

**A class is a value, not a declaration.** You can build one in a function, pass it around, store it in a
list, return it from another function. Every framework that generates classes at runtime — ORMs, schema
libraries, test fixtures — is doing exactly this.

**Because a class is created by calling a callable, that callable can be replaced.** That is the whole
of what a metaclass is: a class whose instances are classes, which the `class` statement calls instead of
`type`.

## The creation sequence

Rather than describe the order, here it is printed.

```python run
def log(msg):
    print("  " + msg)


class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        log(f"1. __prepare__({name}) -> builds the namespace mapping")
        return {}

    def __new__(mcls, name, bases, namespace, **kwargs):
        log(f"2. Meta.__new__({name}) -> the class body has already run")
        public = sorted(k for k in namespace if not k.startswith("_"))
        log(f"   names the class body defined: {public}")
        log(f"   '__init__' is in the namespace: {'__init__' in namespace}")
        cls = super().__new__(mcls, name, bases, namespace)
        log("   (type.__new__ has now called __set_name__ on every descriptor)")
        return cls

    def __init__(cls, name, bases, namespace, **kwargs):
        log(f"3. Meta.__init__({name})")
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        log(f"4. Meta.__call__({cls.__name__}) -- this is what Widget() hits")
        return super().__call__(*args, **kwargs)


class Tracker:
    def __set_name__(self, owner, name):
        log(f"   __set_name__: {owner.__name__}.{name}")


log("about to execute the class statement")


class Widget(metaclass=Meta):
    log("   the class body is running")
    field = Tracker()
    kind = "widget"

    def __init__(self):
        log("   5. the instance __init__ runs")


log("the class statement is finished")
w = Widget()
```

```text
  about to execute the class statement
  1. __prepare__(Widget) -> builds the namespace mapping
     the class body is running
  2. Meta.__new__(Widget) -> the class body has already run
     names the class body defined: ['field', 'kind']
     '__init__' is in the namespace: True
     __set_name__: Widget.field
     (type.__new__ has now called __set_name__ on every descriptor)
  3. Meta.__init__(Widget)
  the class statement is finished
  4. Meta.__call__(Widget) -- this is what Widget() hits
     5. the instance __init__ runs
```

Read the order carefully, because two lines in it are counter-intuitive.

**`__prepare__` runs before the class body.** It is the only hook that gets to influence what the body
sees, because it supplies the mapping the body writes into. Everything else happens afterwards.

**The class body runs before `__new__`.** This is the fact that surprises people. By the time the
metaclass's `__new__` is called, every assignment, every `def`, and every decorator inside the class
body has already executed. `__new__` receives the finished namespace as a dict. You are not watching the
class being built; you are inspecting the result.

**`__set_name__` is called from inside `type.__new__`,** which is why it appears between steps 2 and 3.
Chapter 42 introduced it as the hook that tells a descriptor its own name; this is where it fires.

**`Meta.__call__` is a separate event entirely.** It runs when you instantiate the class, not when you
define it. Defining `__call__` on a metaclass is how you intercept `Widget(...)` — and it is the
mechanism behind `abc.ABCMeta` refusing to instantiate an abstract class.

## A registry, with no metaclass at all

Here is the job people most often reach for a metaclass to do — "register every subclass" — done with the
hook that was added for exactly this purpose.

```python run
registry = {}


class Handler:
    def __init_subclass__(cls, *, command=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if command is not None:
            registry[command] = cls
            print(f"  registered {cls.__name__} for command {command!r}")

    def run(self):
        raise NotImplementedError


print("subclassing registers -- no metaclass anywhere in this file:")


class Add(Handler, command="add"):
    def run(self):
        return "adding"


class Remove(Handler, command="remove"):
    def run(self):
        return "removing"


print()
print("registry ->", {k: v.__name__ for k, v in registry.items()})
print()
print("and the classes are ordinary classes:")
print("  Add().run()    ->", Add().run())
print("  Remove().run() ->", Remove().run())
print()
print("a subclass that omits the keyword is simply not registered:")
class Plain(Handler):
    def run(self):
        return "plain"


print("  registry after Plain ->", {k: v.__name__ for k, v in registry.items()})
print()
print("`command` is keyword-only and the hook receives it because it was")
print("declared with `**kwargs` in the class statement. That is how a base")
print("class accepts options from a subclass it has never seen.")
```

```text
subclassing registers -- no metaclass anywhere in this file:
  registered Add for command 'add'
  registered Remove for command 'remove'

registry -> {'add': 'Add', 'remove': 'Remove'}

and the classes are ordinary classes:
  Add().run()    -> adding
  Remove().run() -> removing

a subclass that omits the keyword is simply not registered:
  registry after Plain -> {'add': 'Add', 'remove': 'Remove'}

`command` is keyword-only and the hook receives it because it was
declared with `**kwargs` in the class statement. That is how a base
class accepts options from a subclass it has never seen.
```

`__init_subclass__` is an implicit classmethod on the base class, called once for every subclass that is
created — including subclasses created years later in other files. It is inherited, which is the property
a decorator cannot provide, and it needs no metaclass.

The keyword arguments are the second half of the trick. `class Add(Handler, command="add")` looks like
inheritance with a stray argument; the class statement collects any keywords it does not recognise and
passes them to the metaclass, which forwards them to `__init_subclass__`. Because the hook declares
`**kwargs` and calls `super().__init_subclass__(**kwargs)`, a class can cooperate with another base class
that also wants keywords — which is exactly why you must not swallow `**kwargs` silently.

## A validator that runs at class-creation time

Now the case that genuinely needs a metaclass: a rule that must apply to the class *object* itself, and
must be inherited.

```python run
class Validated(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        for attr, value in namespace.items():
            if attr.startswith("_") or not callable(value):
                continue
            if not value.__doc__:
                raise TypeError(
                    f"{name}.{attr}() has no docstring: every public method "
                    f"must document itself")
        return super().__new__(mcls, name, bases, namespace)


print("the metaclass inspects the class at creation time:")


class Service(metaclass=Validated):
    def connect(self):
        """Open the connection."""

    def close(self):
        """Close the connection."""


print("  Service was created, so both methods had docstrings")
print("  public methods ->",
      sorted(n for n, v in vars(Service).items()
             if callable(v) and not n.startswith("_")))
print()

print("and now one method that does not:")
try:
    class Broken(metaclass=Validated):
        def connect(self):
            """Open the connection."""

        def close(self):
            pass
except TypeError as exc:
    print("  TypeError:", exc)
print()
print("The failure happened when the class was DEFINED, not when it was")
print("used, not in a test, and not in production. That is the entire")
print("argument for validating at class-creation time.")
print()
print("and the check is inherited, because the metaclass is:")
try:
    class SubService(Service):
        def reset(self):
            pass
except TypeError as exc:
    print("  TypeError:", exc)
```

```text
the metaclass inspects the class at creation time:
  Service was created, so both methods had docstrings
  public methods -> ['close', 'connect']

and now one method that does not:
  TypeError: Broken.close() has no docstring: every public method must document itself

The failure happened when the class was DEFINED, not when it was
used, not in a test, and not in production. That is the entire
argument for validating at class-creation time.

and the check is inherited, because the metaclass is:
  TypeError: SubService.reset() has no docstring: every public method must document itself
```

The last block is the important one. `SubService` never mentions `Validated` — it just inherits from
`Service`. But `SubService`'s metaclass is `Validated`, because a class inherits its metaclass from its
bases, so the check ran on it too. **A rule enforced by a metaclass reaches code that has not been written
yet,** in files you will never see, written by people who have not read your validation code. That is the
capability, and it is worth a metaclass when you need it.

## `__prepare__`, and being honest about it

`__prepare__` supplies the mapping the class body writes into. Here is the one thing it can do that no
other hook can.

```python run
class Strict(dict):
    """A namespace that refuses to let a name be defined twice."""

    def __setitem__(self, key, value):
        if key in self and not key.startswith("_"):
            raise TypeError(f"{key!r} defined twice in the class body")
        super().__setitem__(key, value)


class StrictMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return Strict()


print("a class body that defines each name once is fine:")


class Dup(metaclass=StrictMeta):
    a = 1
    b = 2


print("  Dup created: a =", Dup.a, " b =", Dup.b)
print()
print("but a class body that defines a name twice is caught:")


try:
    class Dup2(metaclass=StrictMeta):
        a = 1
        a = 2
except TypeError as exc:
    print("  TypeError:", exc)
print()
print("A plain dict would have silently kept the second value. Rejecting")
print("a duplicate is something a dict cannot do, and it is only possible")
print("BEFORE the class body runs -- which is what __prepare__ is for.")
```

```text
a class body that defines each name once is fine:
  Dup created: a = 1  b = 2

but a class body that defines a name twice is caught:
  TypeError: 'a' defined twice in the class body

A plain dict would have silently kept the second value. Rejecting
a duplicate is something a dict cannot do, and it is only possible
BEFORE the class body runs -- which is what __prepare__ is for.
```

An honest note, because the internet oversells this hook: **`__prepare__` returning a plain dict is
pointless today.** Dictionaries have preserved insertion order since Python 3.7, so the classic example —
"use `__prepare__` to remember field order" — needs no custom mapping any more. `__prepare__` earns its
place only when you need a mapping that behaves unlike a dict: rejecting a name, resolving a name through
a lookup instead of storing it, or counting duplicates. That is a narrow set of problems, and if yours is
not in it, you do not need this hook.

## The ladder: four steps before you write a metaclass

The same rule — "every subclass must define `handle()`" — written three ways, with the trade-off of each.

```python run
def require_docstrings(cls):
    """The same validation as the metaclass, as a decorator."""
    for attr, value in vars(cls).items():
        if attr.startswith("_") or not callable(value):
            continue
        if not value.__doc__:
            raise TypeError(f"{cls.__name__}.{attr}() has no docstring")
    return cls


print("the same rule, enforced by a decorator -- no metaclass:")


@require_docstrings
class Good:
    def go(self):
        """Go."""


print("  Good was created; its docstring is present")
try:
    @require_docstrings
    class Bad:
        def go(self):
            pass
except TypeError as exc:
    print("  TypeError:", exc)
print()
print("but a decorator runs AFTER the class body, and it is not inherited:")


class SubGood(Good):
    def also(self):
        pass


print("  SubGood was created with no complaint")
print("  SubGood.also.__doc__ ->", SubGood.also.__doc__)
print()
print("A metaclass is inherited, so the rule reaches subclasses written")
print("years later in another file. That is the one thing a decorator")
print("cannot do, and it is usually the only reason to reach for a")
print("metaclass at all.")
print()
print("So the order to try is:")
print("  1. a plain function or __init__ check   -- simplest")
print("  2. a decorator                          -- one class, one rule")
print("  3. __init_subclass__                    -- the rule must be inherited")
print("  4. a metaclass                          -- you must change the")
print("                                             NAMESPACE before the")
print("                                             class body runs, or")
print("                                             replace the class object")
```

```text
the same rule, enforced by a decorator -- no metaclass:
  Good was created; its docstring is present
  TypeError: Bad.go() has no docstring

but a decorator runs AFTER the class body, and it is not inherited:
  SubGood was created with no complaint
  SubGood.also.__doc__ -> None

A metaclass is inherited, so the rule reaches subclasses written
years later in another file. That is the one thing a decorator
cannot do, and it is usually the only reason to reach for a
metaclass at all.

So the order to try is:
  1. a plain function or __init__ check   -- simplest
  2. a decorator                          -- one class, one rule
  3. __init_subclass__                    -- the rule must be inherited
  4. a metaclass                          -- you must change the
                                             NAMESPACE before the
                                             class body runs, or
                                             replace the class object
```

Step 3 is where most real problems stop. `__init_subclass__` is inherited, it is a plain method you can
read and test, it composes with other base classes, and it does not consume the one metaclass slot a
class has.

That last point is the practical reason to prefer it. **A class has exactly one metaclass.** If your
library claims it, every user of your library is locked out of using a second one — and a metaclass
conflict produces `TypeError: metaclass conflict`, which is a genuinely difficult error to work around
when both metaclasses come from libraries you do not control.

:::pitfall The four things that go wrong with metaclasses
**A metaclass conflict you cannot resolve.** Two base classes with different metaclasses, neither a
subclass of the other, and the class statement cannot proceed. The error arrives at the class statement
and names two classes from two libraries. If either library had used `__init_subclass__`, this could not
happen.

**The check runs at import time, so it breaks the whole program.** A metaclass that validates raises
during import, which means one bad class takes down every module that imports it. A decorator has the
same problem, but at least it is attached to one class. Test a metaclass's validation against your own
package before shipping it, and make the failure message name the class and the attribute.

**`__prepare__` returning a non-dict breaks assumptions.** `namespace.items()`, `namespace[name]` and
`dict(namespace)` are not guaranteed to work on a custom mapping unless it subclasses `dict` or implements
the full mapping protocol. Subclass `dict` unless you have a reason not to.

**`__call__` on a metaclass intercepts every instantiation, forever.** If it is slow or it logs, it is
slow or logs on every object creation in the program. If it returns a cached object, `__init__` still
runs — the rule from chapter 40. Keep it minimal.
:::

## Where metaclasses actually appear

You will read far more metaclass code than you write. Knowing the four places they earn their keep makes
that code legible.

**`abc.ABCMeta`** gives you `@abstractmethod` and makes instantiating an incomplete subclass an error. The
check is on the class object, and it is inherited, so it is a metaclass job.

**`enum.EnumMeta`** builds a class whose members are instances of itself, and resolves names through a
lookup rather than plain storage. That is a `__prepare__` job plus a `__new__` job.

**`typing.Protocol`** needs to inspect the class body to collect the protocol's members and check them
against implementations.

**ORM model bases** — Django's `ModelBase`, SQLAlchemy's declarative base — collect fields, generate
column metadata, and attach a manager. They need to see the namespace before it is turned into a class,
which no decorator can do.

Notice what all four have in common: they must **change the class object or the namespace**, not merely
check it. Checking is a decorator's job, and inheritance of a check is `__init_subclass__`'s. Everything
else is either a metaclass or a mistake.

:::scenario The framework that locked out every other framework
A team writes an internal ORM. To collect fields they use a metaclass:

```python
class ModelMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._fields = {k: v for k, v in namespace.items()
                       if isinstance(v, Column)}
        return cls


class Model(metaclass=ModelMeta):
    pass
```

It works. A year later they need `abc.ABC` for an abstract base in the same hierarchy, and this happens:

```text
TypeError: metaclass conflict: the metaclass of a derived class must be a
(non-strict) subclass of the metaclasses of all its bases
```

Nobody can explain it, and the workaround people start using — dropping the abstract base — quietly
removes the abstraction they needed.

What is the conflict, and what should the ORM have done instead?
:::

:::solution Two metaclasses, neither one a subclass of the other
`Model` has metaclass `ModelMeta`. `abc.ABC` has metaclass `abc.ABCMeta`. A class inheriting from both
would need a metaclass that is a subclass of *both*, and none exists. Python refuses rather than guess
which behaviour to use.

The error is not about your class. It is about two libraries each having claimed the single metaclass
slot on their own base class, with no way to combine them.

```python run
import abc


class ModelMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._fields = {k: v for k, v in namespace.items() if k == "column"}
        return cls


class Model(metaclass=ModelMeta):
    pass


try:
    class Mixed(Model, abc.ABC):
        pass
except TypeError as exc:
    print("  TypeError:", exc)
print()
print("  the two metaclasses are unrelated:")
print("    ModelMeta.__mro__    ->", [c.__name__ for c in ModelMeta.__mro__])
print("    ABCMeta is a subclass of type, not of ModelMeta ->",
      issubclass(abc.ABCMeta, ModelMeta))
```

```text
  TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases

  the two metaclasses are unrelated:
    ModelMeta.__mro__    -> ['ModelMeta', 'type', 'object']
    ABCMeta is a subclass of type, not of ModelMeta -> False
```

**What the ORM should have done.** The `_fields` collection above does not need a metaclass at all. It
reads the finished namespace, and a class body's namespace is available to any hook that runs after it —
including `__init_subclass__`:

```python
class Model:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._fields = {k: v for k, v in cls.__dict__.items()
                       if isinstance(v, Column)}
```

That version registers subclasses, sees the fields, and leaves the metaclass slot free — so
`class Mixed(Model, abc.ABC)` works, and so does any other library's metaclass.

**The escape hatch, when you do not control the library.** Define a combined metaclass:

```python
class CombinedMeta(ModelMeta, abc.ABCMeta):
    pass

class Mixed(Model, abc.ABC, metaclass=CombinedMeta):
    pass
```

This works because `CombinedMeta` is a subclass of both. It is the standard workaround, and it is worth
recognising — but needing it is a sign that a library took a slot it did not need.

**The rule to carry:** a metaclass is a scarce, exclusive resource. Claim it only when nothing else can
do the job, and prefer `__init_subclass__` whenever the job is "observe or check the finished class",
which is most jobs.
:::

## Key takeaways

- **A class is an object, created by calling its metaclass.** `class Foo(Base): ...` is a call with a
  name, a tuple of bases and a namespace dict, and by default the callable is `type`.
- **`type(name, bases, namespace)` builds a class directly.** Use it when a class must be generated at
  runtime; the result is equivalent to the class statement in every way that matters.
- **The creation order is `__prepare__`, then the class body, then `__new__`, then `__init__`, with
  `__set_name__` called from inside `type.__new__`.** The class body has *already finished* by the time
  your metaclass sees the namespace.
- **`__prepare__` is the only hook that runs before the class body,** so it is the only one that can
  change what the body sees. Returning a plain dict buys nothing since Python 3.7.
- **`__init_subclass__` handles the common case: a rule that must be inherited.** It is a plain method, it
  composes with other base classes, and it does not claim the metaclass slot.
- **A metaclass is inherited from the bases,** which is what makes a metaclass-enforced rule reach
  subclasses written years later by other people.
- **A class has exactly one metaclass.** If your library claims it, users are locked out of every other
  metaclass-based library, and the failure is a `metaclass conflict` they cannot easily work around.
- **A decorator is not inherited.** It enforces a rule on one class and nothing else, which is either
  exactly what you want or a silent hole, depending on the rule.
- **Use the ladder: plain function, then decorator, then `__init_subclass__`, then metaclass.** The fourth
  step is for changing the namespace or replacing the class object, and for little else.
- **The real metaclasses you will meet — `ABCMeta`, `EnumMeta`, `Protocol`, ORM bases — all change the
  class rather than merely checking it.** That is the signature of a legitimate use.

## Practice

- [ ] Build a class with `type()`, add a method to it after creation, and show it works. Then say why a
      `class` statement is only sugar.
- [ ] Write an `__init_subclass__` that requires a `label` keyword and raises if it is missing. Show a
      subclass that passes and one that fails.
- [ ] Write a metaclass that rejects any class name not starting with a capital letter.
- [ ] Demonstrate that a metaclass is inherited and a decorator is not, by recording which classes each
      one ran for.
- [ ] Use `__prepare__` to build a namespace that rejects a name defined twice, and show the `TypeError`.
      Explain why no other hook could do this.
- [ ] Enforce "every subclass must define `handle()`" with `__init_subclass__` and with a metaclass, and
      say which you would ship and why.

## Solutions

:::solution Exercise 1
```python run
Point = type("Point", (), {"kind": "point"})
Point.describe = lambda self: f"I am a {self.kind}"

p = Point()
print("  Point.__name__       ->", Point.__name__)
print("  Point.__bases__      ->", Point.__bases__)
print("  p.describe()         ->", p.describe())
print("  isinstance(p, Point) ->", isinstance(p, Point))
```

```text
  Point.__name__       -> Point
  Point.__bases__      -> (<class 'object'>,)
  p.describe()         -> I am a point
  isinstance(p, Point) -> True
```

The class was created by a call, and then *modified* by an ordinary attribute assignment — which is only
possible because a class is a mutable object like any other. `Point.describe = ...` put a function into
the class namespace, and because a function is a descriptor (chapter 42) it became a method the moment it
was read through an instance.

The empty tuple for bases gives `object` as the base, which is why `isinstance(p, Point)` is `True` and
`Point.__bases__` shows `object`.

The reason a `class` statement is sugar: everything it does is available as a call plus assignments. The
statement is easier to read and it is what the compiler emits, but there is no capability inside it that
`type()` does not have. That is what makes runtime class generation possible — and it is why a metaclass
can exist at all, since a metaclass is simply what the statement calls instead of `type`.
:::

:::solution Exercise 2
```python run
class Labelled:
    def __init_subclass__(cls, *, label=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if label is None:
            raise TypeError(f"{cls.__name__} must declare a label")
        cls.label = label


class Good(Labelled, label="g"):
    pass


print("  Good.label ->", Good.label)
try:
    class Bad(Labelled):
        pass
except TypeError as exc:
    print("  TypeError:", exc)
```

```text
  Good.label -> g
  TypeError: Bad must declare a label
```

`label` is declared keyword-only with `*`, which means a subclass cannot pass it positionally — and that
matters, because the class statement forwards unrecognised keywords and a positional argument there would
be a `TypeError` with a much less helpful message.

The `**kwargs` and the `super().__init_subclass__(**kwargs)` call are both required for cooperation. If
you accept `**kwargs` and do not forward it, a class inheriting from your base *and* from another base
that also uses `__init_subclass__` will fail — and the failure will point at the other library, not at
yours.

The failure message names the subclass, which is the part worth copying. A validation error that says
"Bad must declare a label" is actionable; one that says "missing keyword argument" is a puzzle.
:::

:::solution Exercise 3
```python run
class Capitalised(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        if not name[0].isupper():
            raise TypeError(f"class name {name!r} must start with a capital")
        return super().__new__(mcls, name, bases, namespace)


class Fine(metaclass=Capitalised):
    pass


print("  Fine ->", Fine.__name__)
try:
    class lower(metaclass=Capitalised):
        pass
except TypeError as exc:
    print("  TypeError:", exc)
```

```text
  Fine -> Fine
  TypeError: class name 'lower' must start with a capital
```

The check runs on `name`, before `super().__new__` is called — so the invalid class is never created at
all. Raising before delegating is the pattern for a validation-only metaclass: there is no half-built
class left behind, and no cleanup to write.

Two limitations worth knowing. `name[0]` raises `IndexError` on an empty name, which `type("", (), {})`
permits — a real check would use `name[:1].isupper()`. And this cannot see the class statement's *text*,
only the name it was given, so `lower = type("lower", (), {})` is caught but a class defined in a string
and `exec`'d with a valid name is not. Metaclasses validate objects, not source code.

Note also that `Capitalised` itself is created by `type`, not by `Capitalised` — a metaclass is an
instance of `type`, and making a metaclass's metaclass a metaclass is possible and almost never wanted.
:::

:::solution Exercise 4
```python run
ran = []


class Enforced(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        ran.append(name)
        return super().__new__(mcls, name, bases, namespace)


class Base(metaclass=Enforced):
    pass


class Sub(Base):
    pass


print("  the metaclass ran for:", ran)
print()

decorated = []


def decorate(cls):
    decorated.append(cls.__name__)
    return cls


@decorate
class Decorated:
    pass


class SubDecorated(Decorated):
    pass


print("  the decorator ran for:", decorated)
print("  SubDecorated is missing from that list, and nothing warned")
```

```text
  the metaclass ran for: ['Base', 'Sub']

  the decorator ran for: ['Decorated']
  SubDecorated is missing from that list, and nothing warned
```

Both hooks are recorded, and the difference is stark. `Enforced` ran for `Base` **and** for `Sub`, because
`Sub` inherits its metaclass from `Base` and therefore its creation goes through `Enforced.__new__`.
`decorate` ran once, for `Decorated`, and `SubDecorated` was created by `type` with no decoration at all.

That is the whole argument for step 4 of the ladder. A rule enforced by a metaclass reaches code written
later by someone who has never heard of your rule. A rule enforced by a decorator reaches exactly one
class, and the hole is silent — there is no warning, no error, and no indication that `SubDecorated`
skipped anything.

The comparison to carry away: if the rule is "this class must be well-formed", a decorator is enough and
clearer. If the rule is "everything in this hierarchy, forever, must be well-formed", only the metaclass
(or `__init_subclass__`, which is inherited too and is usually the better choice) will do it.
:::

:::solution Exercise 5
```python run
class Strict(dict):
    def __setitem__(self, key, value):
        if key in self and not key.startswith("_"):
            raise TypeError(f"{key!r} defined twice in the class body")
        super().__setitem__(key, value)


class StrictMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return Strict()


class Dup(metaclass=StrictMeta):
    a = 1
    b = 2


print("  Dup created: a =", Dup.a, " b =", Dup.b)
try:
    class Dup2(metaclass=StrictMeta):
        a = 1
        a = 2
except TypeError as exc:
    print("  TypeError:", exc)
```

```text
  Dup created: a = 1  b = 2
  TypeError: 'a' defined twice in the class body
```

No other hook could do this, and the reason is about *when* each one runs. By the time `__new__` or
`__init_subclass__` sees the namespace, it is a finished dict and `a` appears exactly once — the second
assignment overwrote the first, and the information that there were two is gone. `__prepare__` is the
only hook that runs before the body, so it is the only one that can observe the writes as they happen.

`Strict` subclasses `dict` rather than implementing the mapping protocol from scratch, which is the
practical choice: the class body calls `__setitem__` on it, but `type.__new__` will later treat it as a
mapping and will call `items()`, `keys()` and `__getitem__`. Subclassing `dict` gets all of that for free.

The `not key.startswith("_")` exemption is deliberate. The compiler writes `__module__`, `__qualname__`
and a few other dunders into the namespace, and some of them are written more than once; a check that did
not exempt them would reject every class in the program.
:::

:::solution Exercise 6
```python run
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "handle" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define handle()")


class Good(Base):
    def handle(self):
        return "handled"


print("  Good created; handle() ->", Good().handle())
try:
    class Bad(Base):
        pass
except TypeError as exc:
    print("  TypeError:", exc)
```

```text
  Good created; handle() -> handled
  TypeError: Bad must define handle()
```

**I would ship this version.** It is six lines, it is a plain method that can be read and tested in
isolation, it is inherited so it reaches every subclass, and — the deciding factor — it does not consume
the class's single metaclass slot.

The check uses `cls.__dict__` rather than `hasattr(cls, "handle")`. That is the difference between
"must define" and "must have", and it is deliberate: `hasattr` would be satisfied by an inherited
implementation, so a subclass could pass the check without implementing anything. If inheriting a default
implementation is acceptable, `hasattr` is the right call — but then the rule is weaker than the one
stated, and it is better to notice that while writing it than after.

The metaclass version of the same rule would be about fifteen lines, would run at the same moment, and
would produce the same error — at the cost of preventing anyone from combining your base with
`abc.ABC`, a Protocol, or any other metaclass-based base. That is the whole trade, and it is why the
ladder puts `__init_subclass__` above the metaclass.
:::
