#!/usr/bin/env python3
"""Generate chapters/09-inheritance-interfaces-and-polymorphism.md.

    python3 tools/gen/09/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "09-inheritance-interfaces-and-polymorphism.md")

BLOCKS = {
    "shapes": gen.run("Shapes.java"),
    "badoverride": gen.bad("BadOverride.java",
                           "method does not override or implement a method from a supertype"),
    "abstractnew": gen.bad("AbstractNew.java", "is abstract; cannot be instantiated"),
    "interfaces": gen.run("Interfaces.java"),
    "dispatch": gen.run("Dispatch.java"),
    "thisescape": gen.run("ThisEscape.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 9
part: 1
title: Inheritance, Interfaces and Polymorphism
summary: Share behaviour with extends, share a type with interfaces, and write loops that never ask what kind of object they are holding.
minutes: 60
tags: [inheritance, interfaces, polymorphism, overriding, abstract, Comparable, dispatch]
---

There are two ways to reuse code in Java and they answer different questions. **Inheritance** —
`extends` — says *this is a kind of that*, and it comes with everything the parent has. **Interfaces** —
`implements` — say *this can do that*, and they come with nothing but a promise. The practical
difference is that a class may extend exactly one parent and implement any number of interfaces, so
interfaces are what you use when the relationship is a capability rather than an identity.

The payoff for both is **polymorphism**: one loop, one method call, and the right code runs for each
object without a single `if`. The chapter that follows, Chapter 10, is about the contract those
objects must then keep so that collections and comparisons behave.

## Extending a class, and the loop that does not ask

@@shapes@@

`Shape` declares two methods and implements neither, which makes it **abstract** — a type that exists
to be extended and cannot itself be instantiated. `Circle` and `Square` each provide `area()` and
`name()`, and both are marked `@Override` so the compiler checks that they really are overriding
something.

The loop is the point of the whole chapter. It declares `List<Shape>`, holds a `Square`, a `Circle`
and another `Square`, and calls `shape.area()` on each. **The call is resolved by the object, not by
the variable** — this is dynamic dispatch, and it happens once per iteration at run time. Nothing in
the loop mentions `Circle` or `Square`, so adding a `Triangle` tomorrow changes no code in the loop at
all. That is the difference between polymorphism and a chain of `if` statements, and the next section
measures what the chain costs.

The `toString` in `Shape` is written once and used by every subclass, because `name()` and `area()`
are dispatched when it runs. A concrete method on an abstract class that calls its own abstract
methods is called the **template method** pattern, and it is the cheapest way to share structure while
letting subclasses fill in the details. Exercise 1 is the same idea as its own exercise.

## Overriding, and the annotation that catches the typo

Overriding means replacing an inherited method with the same name and the same parameter types.
Getting the parameters slightly wrong does not override anything — it *overloads*, creating a second
method that happens never to be called:

@@badoverride@@

The compiler's complaint is precise: `describe(int)` does not override `describe()`, and because the
method carries `@Override`, that is an error rather than a silent surprise. **`@Override` is not
decoration.** It is the only thing that turns "I meant to override this" into something the compiler
can check, and it costs six characters. The alternative is a method that compiles, ships, and never
runs — which is among the hardest bugs to find, because the inherited version does run and usually
looks almost right.

Two rules about overriding are worth stating because they are not obvious. An override may **widen**
access — `protected` to `public` — but never narrow it. And an override may **narrow** the return type
to a subtype (covariant returns), which is why `clone()` returns `Object` in the library and your
override can return your own type.

## Abstract classes cannot be instantiated

An abstract class is incomplete by design, and the compiler enforces the consequence:

@@abstractnew@@

That is not a limitation to work around; it is the mechanism doing its job. If `Shape` could be
instantiated, `area()` would have to return something, and the only honest answers are a default
(nonsense for a shape with no dimensions) or an exception at run time. Making the class abstract
moves the failure from run time to compile time, and from the caller to the author.

A subclass of an abstract class must implement every abstract method it inherits, or be declared
abstract itself. This is the same trade as the interface: the compiler will not let you build an
incomplete object.

## Interfaces: a type with no state

An interface declares methods and no fields, and a class may implement as many as it likes:

@@interfaces@@

Three things are happening in that output. `TextFile` implements **two** interfaces, so it can be used
wherever either is wanted — `sized instanceof Named` is `true` even though `Sized` is what the
variable was declared as. `Person` **overrides** the default `greeting()`, and `TextFile` does not, so
`Person` prints `Hello, Ada Lovelace` while `TextFile` gets `I am notes.txt`. And both are called
through a single `Named` reference, which is polymorphism with no inheritance involved at all.

A **default method** is a method with a body inside the interface. It exists so that a new method can
be added to a published interface without breaking every class that implements it — that is the whole
reason it was added to the language, and it is why library interfaces can grow. Use it sparingly in
your own code: a default method that grows state or calls many other methods is an abstract class
pretending to be an interface.

An interface is also how Java gets *multiple* inheritance of type without the ambiguity: a class can
implement `Named` and `Sized` and `Comparable` all at once, because none of them brings an
implementation that could conflict. When two interfaces both supply a default method with the same
signature, the class must override it to say which it means — the compiler will not guess.

## Methods dispatch, fields do not

This is the part of inheritance that catches people who learned the rule but not the mechanism:

@@dispatch@@

Read the two `report` lines together. Both print `report sees derived method and base field`, and the
reason is that `report()` is defined in `Base`, so the field it reads is `Base`'s. The `label()`
*call* inside it, however, is dispatched on the actual object, so it returns `derived method` even
when the object was reached through a `Base` reference.

The last three lines show the contrast directly. `asBase.label` is `base field` while
`asDerived.label` is `derived field`, from the same object type — because **field access is resolved
from the reference's declared type at compile time, and method calls are resolved from the object at
run time.** Hiding a field by redeclaring it in a subclass is almost always a mistake, and the way to
avoid the whole question is to make fields `private` and expose them through methods, which dispatch
the way you expect.

## The constructor that calls an overridable method

A constructor runs before the subclass's own fields are initialised, and it runs *after* the subclass
has already overridden whatever it is about to call. Those two facts combine badly:

@@thisescape@@

`Base()` calls `describe()`, and because the object being constructed is a `Derived`, the override
runs. But `Derived`'s field initialiser has not executed yet — field initialisers run after `super()`
returns — so `id` is `null` and the tag is captured as `derived null`. A moment later the same call
returns `derived d`, which is what makes this so confusing to debug: the method is fine, and it is
only the *timing* that is wrong.

The compiler says nothing. `-Xlint:all -Werror` compiles that class cleanly, and there is no warning
category in the default set that covers it. The rule that avoids the problem entirely is: **a
constructor should not call a method that a subclass can override.** If the base class needs a value
from the subclass, take it as a constructor parameter instead of asking for it.

There is a second-order trap in writing that example, and it is worth knowing. If `id` were declared
`private final String id = "d";` the program would print `derived d` and the bug would be invisible,
because a `String` literal is a **constant variable** and javac folds it into `describe()` at compile
time. The block above uses `new String("d")` for exactly that reason. Any demonstration of
initialisation order has to defeat constant folding or it demonstrates nothing.

:::pitfall Extending a class to reuse three methods

```java
class Report extends ArrayList<String> {   // "I wanted the add() method"
    ...
}
```

This compiles and works, and it is a trap. `Report` is now an `ArrayList` to every piece of code that
receives one, so a caller can `clear()` it, or `remove(0)`, and every method you wrote assumes those
cannot happen. Worse, the inherited methods are now part of your public API forever: you cannot
change how `Report` stores things without breaking the promise that it *is* a list.

The rule is to extend only when the relationship really is *is-a* and you intend to be substitutable
for the parent everywhere. When you want the behaviour and not the identity, hold an object rather
than becoming one — `class Report { private final List<String> rows = new ArrayList<>(); }` — and
expose only the methods you choose. That is composition, and it is the default. Inheritance is the
exception, and the question that decides it is not "can I reuse this" but "is this genuinely a kind
of that".
:::

:::scenario The settlement report that grows a branch every quarter

A payments service describes how each payment settles. The code is a chain of `instanceof` tests, one
branch per payment type, and it works. Every new payment type means editing the chain, and last
quarter somebody added a type and forgot.

:::solution
The chain duplicates knowledge the objects already have. Each `Payment` can describe itself, so the
chain is a second copy of the same information — and two copies drift.

@@scenario@@

For the three known types the chain and the objects agree exactly, which is what makes the design look
fine. The problem is the fourth case: a payment type the chain has never heard of falls through every
branch and returns `unknown payment`, with no error and no warning. The compiler cannot help, because
an `instanceof` chain over `Object` is exhaustive by definition — there is no set of cases to be
missing from.

The fix is to delete the chain and call `payment.describe()`. That is not a stylistic preference; it
is the difference between a design where adding a type *cannot* be forgotten (the compiler requires
every implementation to provide `describe`) and one where it is forgotten by default. The rule worth
carrying: **when a branch tests the type of an object to decide what it does, the behaviour belongs on
the object.** Chapter 21's `switch` patterns are the right tool when the type really is external and
you cannot add a method — parsing, protocol handling, and other people's classes.
:::

## Key takeaways

- `extends` is for *is-a* and brings the parent's whole API; `implements` is for *can-do* and brings
  only a promise. A class extends one parent and implements any number of interfaces.
- An `abstract` class declares methods without bodies and cannot be instantiated; a subclass must
  implement all of them or be abstract itself.
- `@Override` is checked by the compiler. Without it, a method whose parameters are slightly wrong
  silently overloads instead of overriding, and the inherited version runs instead.
- An override may widen access but not narrow it, and may narrow the return type to a subtype.
- Method calls dispatch on the object's runtime type; field access is resolved from the reference's
  declared type. Redeclaring a field in a subclass hides it rather than overriding it.
- A `default` method lets an interface gain a method without breaking its implementers. Two
  conflicting defaults force the implementing class to override.
- A constructor that calls an overridable method runs the override before the subclass's fields are
  initialised, so those fields are `null` or `0`. The compiler does not warn; do not call
  overridable methods from a constructor.
- A `String` literal assigned to a `final` field is a compile-time constant and is folded into the
  code that reads it, which can hide an initialisation-order bug rather than expose it.
- Prefer composition to inheritance. Extending a library class for its methods makes its whole API
  part of your type's promise, permanently.

## Practice

- [ ] Write an abstract `Shape` with a concrete `describe()` that calls abstract `area()` and
      `name()`, two subclasses, and a loop that prints all three without naming a subclass.
- [ ] Write an interface `Payable` with two implementations and a `total(List<Payable>)` method, and
      show that the total does not need editing when a third implementation is added.
- [ ] Write an interface with two default methods, where one default calls the other, and override
      one of them in a second implementation.
- [ ] Write a `Version` class that implements `Comparable<Version>`, sort a list of versions with
      `Collections.sort`, and show why sorting them as text would give the wrong order.

## Solutions

:::solution Exercise 1
`describe()` is concrete and calls the two abstract methods, so it is written once and every subclass
gets it:

```java run
@@sol1@@
```

`Rectangle(2, 2)` prints as a rectangle rather than a square, which is the honest answer: `Shape` has
no `isSquare()` and `describe()` does not ask. The value of the template method is that the *format* is
decided in one place — changing the column widths changes every subclass at once — while the *data*
comes from whichever subclass is running.
:::

:::solution Exercise 2
`total` takes `List<Payable>` and calls one method on each element. It never names a concrete class,
so a third implementation needs no change here:

```java run
@@sol2@@
```

The three rows add to `252249` cents, and the assertion on the last line is the property that matters:
`total` was not edited when `Salary` was added next to `Invoice`. Contrast this with the `instanceof`
chain in the scenario, which would have needed a fourth branch and silently returned a fallback if
nobody wrote it.
:::

:::solution Exercise 3
`shout()` is a default that calls `greet()`, so it picks up whichever `greet()` the implementation
supplies:

```java run
@@sol3@@
```

`Plain` inherits both defaults and prints `Hello, world`; `Formal` overrides `greet()` and the
inherited `shout()` follows it, printing `GOOD MORNING, DR. CHEN!`. That is the whole point of a
default method — the shared behaviour lives in the interface and the specific behaviour in the class,
with no abstract class needed. `toUpperCase(Locale.ROOT)` is deliberate: the no-argument version uses
the machine's locale, and in a Turkish locale `i` uppercases to `İ`, which would make this block
depend on the reader's settings.
:::

:::solution Exercise 4
`compareTo` defines the order, and `Collections.sort` and `Collections.max` both use it:

```java run
@@sol4@@
```

`1.9` sorts before `1.10`, which is correct numerically and wrong as text — sorting the strings would
put `1.10` first because `'1' < '9'`. That is the whole reason `Comparable` exists rather than a
`sortStrings` helper: the type knows its own order and every generic algorithm can then use it. The
`Integer.compare` calls inside are the safe way to compare two `int`s without the subtraction
overflow from Chapter 4.
:::
"""

gen.write(TEMPLATE, BLOCKS)
