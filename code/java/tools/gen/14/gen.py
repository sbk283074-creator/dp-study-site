#!/usr/bin/env python3
"""Generate chapters/14-lambdas-and-method-references.md.

    python3 tools/gen/14/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "14-lambdas-and-method-references.md")

BLOCKS = {
    "lambdas": gen.run("Lambdas.java"),
    "functional": gen.run("Functional.java"),
    "capture": gen.run("Capture.java"),
    "notfinal": gen.bad("NotFinal.java", "must be final or effectively final"),
    "methodrefs": gen.run("MethodRefs.java"),
    "compose": gen.run("Compose.java"),
    "thisinlambda": gen.run("ThisInLambda.java"),
    "checkedlambda": gen.bad("CheckedLambda.java", "unreported exception"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 14
part: 2
title: Lambdas and Method References
summary: Pass behaviour as a value — write the body and nothing else, capture only what is safe to capture, and reach for a method reference when a name already exists.
minutes: 60
tags: [lambdas, functional-interfaces, method-references, closures, capture, composition]
---

Until Java 8, passing behaviour meant writing a class. A single-line comparison became a file, or an
anonymous class with six lines of ceremony around the one line that mattered. Lambdas removed the
ceremony, and the language paid for it with a rule: a lambda needs a **functional interface** — a type
with exactly one abstract method — to be the target.

That constraint is the whole design. A lambda is not an object with a type of its own; it is a
*body* that the compiler attaches to whichever functional interface the surrounding context requires.
Everything in this chapter follows from it: why a lambda cannot be its own type, why `this` behaves
the way it does, and why the rules about what a lambda may capture are stricter than they first look.

## A lambda is an interface implementation with the ceremony removed

@@lambdas@@

The lambda and the anonymous class do the same job, and the difference is what you had to type. The
anonymous class repeats the interface name, the method name, the parameter type and the return type;
the lambda writes `text -> text.toUpperCase()` and lets the compiler read the rest from `Transform`.

`upper instanceof Transform` is `true`, because the lambda *is* a `Transform` — the compiler has made
one for you. But `upper.getClass() != anonymous.getClass()`, and the lambda's class is not one you can
name. That is deliberate: the class is an implementation detail, so nothing you write should depend on
it. A lambda has no identity of its own to depend on.

:::note
A lambda is not a way to make a new type. It is a way to supply the one method a type already requires.
When you find yourself wanting the lambda to carry state or expose more than one method, the answer is
a class — or, more often, a `record` with a method.
:::

## The interfaces you will actually use

`java.util.function` holds the standard shapes, and almost everything you write is one of five.

@@functional@@

`Function<T, R>` takes one argument and returns a value. `Predicate<T>` takes one and returns a
`boolean` — which is why `test` reads oddly at first, since `Predicate` predates the convention of
naming the method after the thing. `Consumer<T>` takes one and returns nothing. `Supplier<T>` takes
nothing and returns one. `BiFunction<T, U, R>` takes two and returns one.

The `Bi` prefix is the pattern for arity, and there is no `TriFunction` because almost nobody needs
one. When you do, you write it — a three-parameter interface with one method is four lines.

`String::length` used as a `Function<String, Integer>` is a method reference, which the next section
covers. What matters here is that it is *shaped* like a function, so it fits.

## What a lambda may capture

A lambda can read local variables from the enclosing method, but only ones that are **final or
effectively final** — never reassigned after they are initialised.

@@capture@@

Both `prefix` and `count` are read by the lambdas, and neither is declared `final`. They are
*effectively* final: the compiler checks that they are never assigned after their initialiser, and that
is enough.

`names` is different in an important way. The lambda captured the **reference**, so when `names.add("c")`
runs later, `size.get()` returns `6` rather than `5`. The variable could not be reassigned; the object
it points at can change freely. That distinction — the variable is frozen, the object is not — is the
thing to hold on to.

The restriction is not arbitrary. A lambda may run later, on another thread, after the method that
created it has returned. If it captured a mutable local by reference, the value it read would depend on
when it ran, and there would be no way for the compiler to reason about the method at all.

What happens when you break the rule is worth seeing once.

@@notfinal@@

`local variables referenced from a lambda expression must be final or effectively final` — javac names
the variable's role rather than its name, so the message is about the *rule* rather than the offender.
The fix is almost always to introduce a new local that is not reassigned, which is also clearer to read.

## Method references: when the body is just a call

If the whole lambda is a call to a method, name the method instead.

@@methodrefs@@

The five forms, and the `::` syntax is the same in all of them — the difference is what is on the left:

- **Static** — `MethodRefs::shout`. The lambda would be `text -> shout(text)`.
- **Bound to an instance** — `"hello"::indexOf`. The receiver is fixed; the argument supplies the
  parameter.
- **Unbound, on the argument** — `String::trim`. The lambda would be `text -> text.trim()`, so the
  first argument becomes the receiver.
- **Constructor** — `ArrayList::new`. A `Supplier` because it takes no arguments.
- **Instance method on an argument** — `Name::full`. Same shape as the unbound form, and the reason
  `Name::full` needs no instance.

The rule for choosing is mechanical: **write the lambda first, then see if it is only a call.** A
method reference is shorter and names an existing thing, which is usually better. But when the lambda
does anything at all — a null check, an extra argument, a transformation — it must stay a lambda, and
forcing a method reference with a helper method can be less readable than the lambda was.

## Composing functions instead of nesting calls

`Function` and `Predicate` have default methods that build new functions out of old ones.

@@compose@@

`andThen` runs this function first, then the argument; `compose` runs the argument first. On `5` with
`doubleIt` and `addOne` they give `11` and `12`, and the difference is only the order.

Read them as a pipeline rather than a nest. `TRIM.andThen(UPPER)` says what happens, in the order it
happens, and a long chain stays readable where `upper(trim(x))` becomes a puzzle of parentheses. The
`Predicate` versions — `and`, `or`, `negate` — are the same idea for conditions, and they let you name
each rule separately and combine them at the call site.

:::tip
Build predicates as small named constants and combine them where they are used. A rule named
`startsWith("a")` is testable on its own, appears in a stack trace with a useful name, and can be
reused. The same logic inlined into a `filter` call can be neither.
:::

## `this` in a lambda is the enclosing `this`

An anonymous class is a class, so it has its own `this` and its own fields. A lambda is not, and this
catches people who are used to the older form.

@@thisinlambda@@

The lambda prints the **outer** field. `this` inside a lambda refers to the instance of the enclosing
method's class, not to the lambda, because the lambda is not an object with a scope of its own.

The anonymous class prints its own field, because it genuinely is a separate class with a field of that
name. If you are converting an anonymous class to a lambda and it reads a field through `this`, the
meaning changes — and the compiler will not warn you, because both versions are legal.

## The checked exception a lambda cannot throw

A functional interface declares one abstract method with a fixed `throws` clause, and most of the
standard ones declare nothing.

@@checkedlambda@@

`unreported exception IOException; must be caught or declared to be thrown`. `Files.readString` throws a
checked `IOException`, and `Function.apply` does not declare it — so the lambda body is a method body
that may not throw what it throws.

This is not a limitation of lambdas so much as a consequence of the interface. `Function` was designed
for transformations that cannot fail. When yours can, you have three options: catch inside the lambda
and handle it there, write a functional interface of your own whose method declares `throws`, or wrap
the throwing call in a helper that converts the checked exception into an unchecked one. `Sol3` is the
third, which is the one that keeps the pipeline readable.

:::pitfall
**Do not swallow a checked exception to make a lambda compile.** The quickest fix is a `try` block that
logs and returns `null`, and it turns a failure into a `NullPointerException` three frames later. If the
call can fail, the failure has to go somewhere — up as an unchecked exception, or into a value the
caller must inspect.
:::

:::scenario The list of lambdas that all print the same number

A list of `Supplier<Integer>` is built in a loop, one supplier per iteration, and every one of them
returns the same value.

:::solution
The loop variable is not captured by value; the *variable* is captured, and a mutable holder is the same
variable every round. Java prevents this for a plain `for` loop by requiring the loop variable to be
effectively final — which is why the bug needs a mutable holder to reproduce at all.

@@scenario@@

Three lines, three different outcomes, and the middle one is the surprise for anyone arriving from a
language where the loop variable is shared.

The **for-each** case is correct: `[ada, grace, alan]`. Each iteration gets a fresh `name`, and each
lambda captures its own. This is a language guarantee, not luck.

The **classic `for`** case needs `int copy = i;` inside the body. Without it the code does not compile,
because `i` is reassigned by the increment. The copy is a new variable per iteration, so each lambda
captures a different one.

The **mutable holder** case is the bug: `[3, 3, 3]`. The lambda captured `holder` — one array, shared by
all three suppliers — and reads `holder[0]` when it is *called*, by which time the loop has finished and
the value is `3`. Nothing was captured by value except the reference.

So Java's capture rules remove the most common form of this bug and leave the form that requires a
mutable holder. If you need a per-iteration value, make it a local; if you deliberately want shared
state, a holder is how you say so — and now you know you said it.
:::

## Solutions

### 1. Build the comparator instead of writing it

@@sol1@@

`Comparator.comparingLong(Entry::size).thenComparing(Entry::name)` replaces what would have been a
multi-line `compare` with two method references and a tie-break. The tie-break is not optional: two
entries of `200` bytes sort in arrival order without it, and that order is not reproducible from the
data.

`Comparator.comparing(Entry::name)` is a value, and the last line proves it — a comparator can be
stored, passed and tested in isolation. That is the practical difference between `Comparator` and
`Comparable` from Chapter 12: an order expressed as an object can be varied, combined and unit-tested.

### 2. A pipeline of method references

@@sol2@@

Three `Function` constants, combined once into a `pipeline`, then applied to a single value and to a
list. The pipeline is a value: it can be named, reused and passed to `map`, and the list version needs
no change to work on any number of elements.

`TRIM.andThen(UPPER).andThen(EXCLAIM)` and `UPPER.compose(TRIM).andThen(EXCLAIM)` produce the same
function here, which the last line confirms. That is a property of this particular pipeline, not a
general rule — `andThen` and `compose` differ whenever the order matters, and the earlier example with
`doubleIt` and `addOne` is the proof.

### 3. Wrap the checked exception once

@@sol3@@

`CheckedFunction` is a functional interface whose one method declares `throws Exception`. `unchecked`
takes one of those and returns a plain `Function` that catches and rethrows as a `RuntimeException`,
preserving the original as the cause.

That helper is written once and then every throwing call in the codebase can be adapted with one line:
`unchecked(Integer::parseInt)` is a `Function<String, Integer>` that fits a stream. The alternative —
a `try` block inside every lambda — spreads the same six lines everywhere and buries the actual
transformation.

The failure still surfaces, wrapped, with `NumberFormatException` reachable through `getCause()`. That
is the difference between adapting a checked exception and discarding it.

### 4. A functional interface of your own

@@sol4@@

`Rule` declares one abstract method and two `default` methods, and `@FunctionalInterface` documents
that. The last two lines verify it by reflection: one abstract method, which is exactly the requirement
for a lambda target. A second abstract method would make `value -> ...` illegal and the annotation a
compile error.

The `and` and `negate` defaults are what make it pleasant to use: `minLength(3).and(startsWith("a"))`
reads as the rule it is, and each half is a separate named function you can test alone.

:::tip
Write your own functional interface when the standard ones do not say what you mean. A `Rule` that
reads `minLength(3).and(startsWith("a"))` documents itself in a way that
`Predicate<String> p = s -> s.length() >= 3 && s.startsWith("a")` does not — and the second version has
no name to appear in a stack trace or a test report.
:::

## Key takeaways

- A lambda is a body attached to a **functional interface** — a type with exactly one abstract method.
  It has no type of its own, and you cannot name its class.
- The five standard shapes are `Function`, `Predicate`, `Consumer`, `Supplier` and `BiFunction`, all in
  `java.util.function`.
- A lambda may capture a local only if it is final or effectively final. The *variable* is frozen; the
  object it points at is not, so a captured list sees later changes.
- Write the lambda first and convert it to a method reference only when the body is nothing but a call.
  The five forms are static, bound, unbound, constructor, and instance-on-an-argument.
- `andThen` and `compose` differ in order: `f.andThen(g)` is `g(f(x))` and `f.compose(g)` is `f(g(x))`.
  `Predicate` adds `and`, `or` and `negate`.
- `this` inside a lambda is the enclosing instance. An anonymous class has its own `this` and its own
  fields, so converting one to a lambda can change what a field read means.
- A lambda cannot throw a checked exception the interface does not declare. Adapt it with a helper that
  preserves the cause, or write your own interface that declares `throws`.
- A for-each loop gives each iteration a fresh variable, so a list of lambdas built in one is correct.
  A classic `for` needs a local copy, and a mutable holder is genuinely shared — all three suppliers
  then read the same final value.

## Practice

- [ ] Write the same operation as an anonymous class, a lambda and a method reference. Say for each what
      the reader has to hold in their head.
- [ ] Build a `Function<String, String>` that trims, lowercases and replaces spaces with hyphens, then
      apply it to a list. Use method references where the body is only a call.
- [ ] Write a lambda that captures a `List` and a lambda that captures an `int`. Mutate both after
      capture and explain the two different outcomes.
- [ ] Write a `@FunctionalInterface` with a `default` method that returns a new instance, and confirm by
      reflection that it still has exactly one abstract method.
- [ ] Take a call that throws a checked exception and adapt it three ways: catch inside the lambda, a
      custom interface declaring `throws`, and a wrapping helper. Say which you would ship.
- [ ] Convert an anonymous class that reads a field through `this` into a lambda and find the case where
      the behaviour changes.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The anonymous class repeats the type and the signature; the lambda states the parameter and the body;
   the method reference names an existing method and says nothing else. The method reference is shortest
   but requires the reader to know what the method does.
2. `String::trim` then `.andThen(String::toLowerCase)` then a lambda for the replacement, because that
   step is not a single call. Applied with `.map(pipeline)` over the list.
3. The `int` must be effectively final or the code does not compile, so a mutation after capture is
   impossible. The `List` is captured by reference, so a later `add` is visible to the lambda.
4. `default` methods are not abstract, so a `default` that returns a new instance leaves the abstract
   count at one and the interface remains a lambda target.
5. Catching inside the lambda buries the handling at every call site. A custom interface is cleanest
   when the exception is expected. The wrapping helper is best when the checked exception is incidental
   to the pipeline.
6. The behaviour changes when the anonymous class declares a field of the same name the lambda would
   read from the outer class — the lambda reads the outer one, the anonymous class reads its own.
"""

gen.write(TEMPLATE, BLOCKS)
