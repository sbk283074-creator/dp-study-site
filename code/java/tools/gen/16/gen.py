#!/usr/bin/env python3
"""Generate chapters/16-records-enums-and-sealed-types.md.

    python3 tools/gen/16/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "16-records-enums-and-sealed-types.md")

BLOCKS = {
    "basics": gen.run("Basics.java"),
    "badrecord": gen.bad("BadRecord.java", "field declaration must be static"),
    "compact": gen.run("Compact.java"),
    "shallow": gen.run("Shallow.java"),
    "enumbasics": gen.run("EnumBasics.java"),
    "enumswitch": gen.run("EnumSwitch.java"),
    "enumvalues": gen.run("EnumValues.java"),
    "enumsetmap": gen.run("EnumSetMap.java"),
    "sealed": gen.run("Sealed.java"),
    "badsealed": gen.bad("BadSealed.java", "class is not allowed to extend sealed class: Shape"),
    "recordpattern": gen.run("RecordPattern.java"),
    "nonsealed": gen.run("NonSealed.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 16
part: 2
title: Records, Enums and Sealed Types
summary: Let the compiler write the value class, fix the set of constants, and close a hierarchy so a missed case becomes a compile error instead of a runtime surprise.
minutes: 55
tags: [records, enums, sealed, pattern matching, immutability, exhaustive switch]
---

A value class — a point, an order line, a configuration entry — is mostly boilerplate: a constructor,
an accessor per field, and `equals`, `hashCode` and `toString`. You wrote all of that by hand in
Chapter 10, and you saw how easy it is to get one of the three contract methods wrong. Three Java
features remove that work from different directions. `record` writes the class for you, `enum` fixes
the set of instances so no fourth one can appear, and `sealed` closes a hierarchy so the compiler
knows every implementation and can tell you when a case is missing.

## A record is a class the compiler writes for you

@@basics@@

`record Point(int x, int y) {}` is the entire declaration. From those two components the compiler
generates a `private final` field for each, a canonical constructor taking both, an accessor per
component, and `equals`, `hashCode` and `toString` derived from the components.

The last line of the transcript is the one that matters most. A `Point` works as a `HashSet` member
out of the box, because `equals` and `hashCode` were generated consistently. Everything Chapter 10
made you write by hand — and could get wrong — arrives correct.

Two details are worth reading carefully. `components = [x, y]` comes from `getRecordComponents()`, the
reflective view of the component list; it is what lets a library treat a record as *data* rather than
as a class, and it is why a JSON library can serialise one with no configuration at all. And the
accessor is `x()`, not `getX()`. That is the language's chosen convention, so code calling `getX()` on
a record does not compile.

:::note
A record is still a class. It can implement interfaces, declare static fields and static methods, add
instance methods, and be generic. What it cannot do is hold instance state beyond its components, or
extend another class — it already extends `java.lang.Record`.
:::

### What a record cannot do

@@badrecord@@

The rejection is about instance state, and the compiler's wording is worth reading twice:
`field declaration must be static`. A record's instance fields *are* its components, so an extra one
would create state that `equals`, `hashCode` and `toString` know nothing about. The generated methods
would then be wrong in a way nobody could see by reading the declaration, so the compiler refuses to
let you get there.

## The compact constructor is where validation goes

A record's canonical constructor is generated, but you can take it over without repeating the
parameter list.

@@compact@@

`Range { ... }` — no parentheses, no parameter list — is a **compact constructor**. The parameters are
in scope, and the fields are assigned from them *after* the body runs. That ordering is the whole
point: the body is a place to validate, and to adjust values on their way in.

`Name` does both. `first = first.trim()` reassigns the *parameter*; because the field assignment
happens afterwards, the field receives the trimmed value, and `full()` prints `Ada Lovelace`. A caller
who passes blank space gets an exception rather than a `Name` that looks empty and compares unequal to
every other blank one.

`Range` shows the other half — a constructor that refuses. `new Range(9, 2)` throws before any object
exists, so a `Range` in your hand always satisfies `lo <= hi`. That is a stronger guarantee than a
setter that validates, because there is no window in which the object is invalid. The rule generalises:
**validate in the constructor, and make the type's invariants true for every instance that exists.**

## Records are shallowly immutable, and that is not the same as immutable

`final` on a field stops the *reference* from changing. It says nothing about the object the reference
points at.

@@shallow@@

Three lines, three separate surprises.

`caller mutated` shows the record holding the *same array* the caller passed. Writing `marks[0] = 0`
after construction changes what the record reports, because there is only one array and both names
point at it.

`accessor mutated` shows the other direction. `s.marks()` hands out that array, so a caller can write
into the record's state without any setter existing anywhere.

`equals a copy = false` is the consequence, and it is the most dangerous of the three because it is
silent. Two `Scores` with identical contents are not equal, because the generated `equals` compares the
`int[]` components with `Objects.equals`, which for an array is `==`. The next line, `same contents =
true` from `Arrays.equals`, proves the data really is identical — the *comparison* is what is broken.

This is the shape of mistake to carry away: **a record gives you value semantics only for components
that already have value semantics.** `String`, `List`, `Set`, `Map` and other records qualify. If you
must hold an array, copy it in the compact constructor *and* copy it again in the accessor — and notice
that switching the component to `List` fixes both problems at once, because `List.copyOf` copies on
the way in and `List.equals` compares contents. That is the first solution below.

## Enums are classes with a fixed instance set

An `enum` declares a closed set of constants, and each constant is a real object that can carry state
and behaviour.

@@enumbasics@@

`Planet` has two fields, a constructor and two methods. The constants are the only instances that will
ever exist, they are created once when the class is initialised, and the constructor is implicitly
`private` — `new Planet(...)` is not merely discouraged, it does not compile anywhere, including
inside the enum itself.

`ordinal()` is a constant's position, `name()` its identifier, and `values()` the array of all of them
in declaration order. Those two accessors look like conveniences, and one of them is a trap.
`ordinal()` is stable only while nobody reorders or inserts a constant. Persisting an `ordinal()` into
a file or a database column is a bug waiting for the next release; store `name()` and read it back
with `valueOf`.

### Switching on an enum is checked

@@enumswitch@@

`threshold` has no `default` arm and compiles. The compiler knows the complete set of constants, so it
can prove the three arms cover every case, and it will refuse the method the moment a fourth constant
appears. A `default -> 0` would compile too, would look defensive, and would silently swallow exactly
that fourth constant.

`case LOW, MEDIUM ->` shows that arms can group constants when they share a result. That is often the
sign that the two constants want a shared field rather than a shared arm — `Level` could carry a
threshold per constant, and then `threshold` would not need a switch at all. Reach for the switch when
the *behaviour* differs per constant; reach for a field when only the *data* does.

### `values()` hands out a fresh array every time

@@enumvalues@@

The mutation does not stick. `first[0] = Suit.SPADES` changed the array the caller holds, and the very
next call printed the original four constants, because `values()` **clones** its backing array on every
call. `same array = false` says the same thing directly: two consecutive calls do not return the same
object.

This is about cost rather than correctness. Because each call allocates, `for (Suit s : Suit.values())`
is fine — the array is produced once, before the loop begins — while a loop written as
`for (int i = 0; i < Suit.values().length; i++)` allocates on every iteration. The measured fact above
is the entire reason: two calls, two arrays.

## Enum iteration order is declaration order

@@enumsetmap@@

`EnumSet.of(Day.SUN, Day.SAT)` printed `[SAT, SUN]`. That is not insertion order — it is **ordinal**
order, and it is a documented property rather than a coincidence of these values. `EnumMap` behaves
the same way: keys were put in the order FRI, MON, WED and the key set printed `[MON, WED, FRI]`.

The implementation explains it. An `EnumSet` is a bit vector over the ordinals and an `EnumMap` is an
array indexed by ordinal, which is also why both are faster and smaller than the general collections
for this job. The ordering is a side effect you get for free.

The last two lines are the part to be careful about. A `HashSet` and a `HashMap` holding enums compare
**equal** to the `EnumSet` and `EnumMap` — set and map equality is content-based, not order-based — but
their iteration order is derived from `hashCode`, and `Enum` does not override `hashCode`. Every
constant inherits `Object`'s identity hash, so the order is effectively arbitrary and can differ
between two runs of the same program.

:::warning
**An enum's `hashCode` is its identity hash code, so a `HashSet<SomeEnum>` has no stable iteration
order.** Print a sorted view, or use `EnumSet`/`EnumMap`, which iterate by ordinal. This is the hazard
Chapter 12 described for hash collections in general; the difference is that `String.hashCode` is
specified by the language, and an enum's is not.
:::

## Sealed types: closing a hierarchy

An interface is open by default: anyone can implement it, including code written years from now by
someone you have never met. That is usually what you want, and it is exactly what you do not want when
the implementations are a known, fixed set.

@@sealed@@

`sealed interface Shape permits Circle, Rect, Line` names its implementations, and the compiler then
knows the complete set. Two things follow.

`getPermittedSubclasses()` returns the list — `[Circle, Rect, Line]`, in the order they were declared
in the `permits` clause. This is a question that now has a real answer, where an open interface can
only say "somewhere out there".

More useful day to day: `area` has **no `default` arm** and compiles. The compiler can prove the
switch covers every case, because `permits` told it what every case is.

State the payoff as a rule: **a `default` arm in a switch over a sealed type is a missed opportunity.**
It would compile, it would look careful, and it would swallow the next type somebody adds. Leaving it
out means that adding `Pentagon` to the `permits` clause turns every switch in the codebase into a
compile error, at exactly the places a human needs to make a decision.

### The `permits` clause is enforced

@@badsealed@@

`Square` implements `Shape` and is not in the list, so the file does not compile. Note the wording:
javac calls it a **sealed class** even though `Shape` is an interface — a detail of the message, not of
the rule.

The permit list is a closed set in both directions. You cannot implement a sealed type without being
listed, and you cannot list a type without it being in the same package or module — which is what
makes the set knowable at compile time in the first place.

## Pattern matching reads the shape of the value

A `case` arm can name the type *and* take the value apart in the same breath.

@@recordpattern@@

`case Num(double v) -> v` matches a `Num` and binds its component to `v`. `case Add(var l, var r)`
does the same for two components, letting `var` infer each type from the component. This is a **record
pattern**, and because `Expr` is sealed the three arms are exhaustive with no `default`.

The result is a tree interpreter in seven lines: no casts, no `instanceof` chain, no unreachable
fallback. Compare what the same method looks like with only the tools Chapter 09 had — an `instanceof`
test, a cast, then the accessor, repeated once per type, plus a `default` that either throws or returns
something wrong. The nesting in the printed expression shows why this scales: `Mul`'s components are
themselves `Expr`, and the pattern reaches into them without a helper method.

### `non-sealed`: reopening what you closed

@@nonsealed@@

`sealed` is a promise that can be partially withdrawn. `non-sealed interface Wildcard extends Node`
puts `Wildcard` back into the permitted set while removing the restriction *below* it, so `Anything` —
a type `Node` has never heard of — can implement it.

The switch is still exhaustive, because `case Wildcard w` covers everything underneath `Wildcard`,
including types written later. That is the trade in one line: `non-sealed` buys extensibility back and
gives up the compiler's ability to enumerate the leaves. Use it deliberately. A hierarchy that is
sealed at the top and `non-sealed` in one branch is still sealed at the level you usually care about.

:::scenario The discount rule that arrived on a Friday

A pricing service applies a discount per customer tier. The rules sit behind a `sealed interface
Discount`, and the per-tier policy is an `EnumMap<Tier, Discount>`. On Friday somebody asks for a
fourth rule: a percentage that only applies above a minimum order value.

:::solution
Because `Discount` is sealed and every `switch` over it omits `default`, adding
`record PercentOver(int pct, int minCents) implements Discount {}` to the `permits` clause breaks the
build in every place that has to make a decision. The compiler produces a work list instead of a
runtime surprise.

The other half of the design is the `EnumMap`. The policy is keyed by tier, so a tier with no rule is
a missing key, and `policy.get(tier)` returning `null` would blow up inside the switch. Seeding every
tier explicitly makes the policy total — a property you can check by comparing `policy.size()` with
`Tier.values().length`.

@@scenario@@

Four orders, three tiers, one total of `15400` cents. The report prints in ordinal order —
`{BASIC=2000, PRO=5400, ENTERPRISE=8000}` — because the accumulator is an `EnumMap`, which is the
ordering property from earlier in this chapter doing real work. `A2` and `A3` are both `PRO` and are
merged into the same entry by `Map.merge`, which is the idiomatic way to accumulate into a map without
a `containsKey` check.

The one thing this design does *not* protect you from is a rule that is wrong rather than missing. The
sealed hierarchy guarantees every case is handled; it cannot guarantee the handler is correct. That is
what tests are for, and Chapter 19 builds the harness.
:::

## Solutions

### 1. Fix the shallow-immutability trap properly

@@sol1@@

The component changed from `int[]` to `List<Integer>`, and one line in the compact constructor does
the rest: `marks = List.copyOf(marks)`.

Three problems disappear at once. The caller's later mutation does not reach the record, because
`copyOf` took a copy — `defended = [70, 80]` while the caller's list reads `[0, 80]`. The accessor
cannot be used to write into the record, because `copyOf` returns an immutable list and `set` throws
`UnsupportedOperationException`. And `equals` now works, because `List.equals` compares contents, so
`s.equals(new Scores("Ada", List.of(70, 80)))` is `true`.

The general rule: **choose component types that already have value semantics, and the generated
methods are correct for free.** Reach for the defensive-copy version only when an array or another
mutable type is genuinely forced on you.

### 2. Constant-specific behaviour instead of a switch

@@sol2@@

`Op` declares an abstract method and each constant supplies its own body in braces. This is a
**constant-specific class body**: the compiler generates an anonymous subclass per constant, which is
why `apply` can be abstract on the enum itself.

The trade against a switch is worth stating plainly. A switch centralises the behaviour, so one method
shows every case side by side — good when the cases are short and you are comparing them. Constant
bodies distribute the behaviour, so adding an operation means adding one constant and touching nothing
else — good when each case is substantial or carries its own data. Either way the compiler checks
exhaustiveness, because the constant set is closed.

### 3. A sealed event hierarchy with an exhaustive report

@@sol3@@

Two `switch` expressions over the same sealed interface, both without `default`. `kind` maps each event
to a label and `amount` extracts a number, and neither needs a cast or a fallback.

The report is a `TreeMap` so the output is sorted and reproducible — the same determinism discipline
from Chapter 12. `revenue = 3200` is the sum of the two purchases only, because `Login` and `Logout`
return `0` from `amount`. Writing that as two separate exhaustive switches rather than one switch
returning a pair is deliberate: each method answers one question, and the compiler checks each of them.

### 4. Replace a stringly-typed field with an enum

@@sol4@@

`Status.parse` is the pattern for reading an enum from outside data. `valueOf` throws
`IllegalArgumentException` for an unknown name, and the `catch` turns it into a message that names the
offending input instead of just the constant it could not find.

Note the normalisation: `raw.toUpperCase()` is why `"Published"` parses. That is a decision, not a
detail — it means the wire format is case-insensitive while the enum names stay upper-case. Decide
deliberately, and write it in one place, because the alternative is a `toUpperCase()` sprinkled at
every call site and forgotten at one of them.

## Key takeaways

- A `record` generates the fields, canonical constructor, accessors, `equals`, `hashCode` and
  `toString` from its components, so it is correct as a map key with no hand-written code.
- Accessors are named after the component — `x()`, not `getX()`. A record cannot declare extra
  instance fields or extend a class.
- The compact constructor takes over the canonical constructor without repeating the parameter list.
  Fields are assigned *after* the body, so reassigning a parameter changes what is stored.
- A record is **shallowly** immutable. A component of array type breaks both immutability and the
  generated `equals`; prefer `List` and `List.copyOf`.
- An enum's constants are the only instances, created once, with an implicitly private constructor.
  `ordinal()` is position-dependent and must not be persisted; store `name()`.
- A `switch` over an enum needs no `default`, and omitting it makes a new constant a compile error
  rather than a silent fallthrough.
- `values()` clones its array on every call, so hoist it out of a loop condition.
- `EnumSet` and `EnumMap` iterate in ordinal order and are faster than the general collections. A
  `HashSet` or `HashMap` of enums compares equal to them but has no stable iteration order, because an
  enum inherits `Object`'s identity hash.
- A `sealed` type names its implementations, so a `switch` over it is exhaustive without `default`.
  Adding a permitted type then breaks the build at every decision point — which is the feature.
- Record patterns destructure a value inside a `case` arm, replacing an `instanceof` chain and a cast
  with a single line. `non-sealed` reopens a branch of a sealed hierarchy.

## Practice

- [ ] Rewrite a hand-written value class from your own code as a `record`. List every method the
      compiler now generates and check whether any of them differed from yours.
- [ ] Add a compact constructor to a record that normalises a `String` component to trimmed,
      lower-case form, and prove that no instance can hold an untrimmed value.
- [ ] Take a class with a `String` status field and a handful of `if` comparisons, and replace the
      field with an enum. Say what now fails at compile time that used to fail at runtime.
- [ ] Write a record holding an array, demonstrate that two equal contents compare unequal, then fix
      it two ways — a defensive copy and a `List` component — and say which you would ship.
- [ ] Model a small expression language with a sealed interface and three records, then write `eval`
      using record patterns with no `default` arm.
- [ ] Add a fourth type to that sealed hierarchy and count how many places the compiler now refuses to
      build. Compare that with what would have happened had each switch carried a `default`.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The constructor, one accessor per component, `equals`, `hashCode` and `toString`. The generated
   `equals` and `hashCode` are the interesting ones: if your version used only some of the fields, or
   forgot to keep the two consistent, the record version is a bug fix rather than a rewrite.
2. `record Handle(String raw) { Handle { raw = raw.trim().toLowerCase(); } }`. The proof is that the
   accessor returns the normalised value no matter what the caller passed, and that there is no
   setter, so the normalisation cannot be undone afterwards.
3. Every `switch` and every comparison now has to name an enum constant, so a typo becomes a compile
   error instead of a branch that never runs. The `if ("PUBLSHED".equals(status))` that silently never
   matched cannot be written any more.
4. `equals` compares the array components with `Objects.equals`, which is `==` for arrays, so contents
   are never consulted. The defensive-copy fix keeps the array and makes `equals` correct only if you
   also override `equals` and `hashCode` by hand; the `List` fix is one line and needs no overrides.
   Ship the `List`.
5. `sealed interface Expr permits Lit, Add, Mul {}` with `record Lit(double v)`, `record Add(Expr l,
   Expr r)` and `record Mul(Expr l, Expr r)`. `eval` switches on `case Lit(double v) -> v` and
   `case Add(var l, var r) -> eval(l) + eval(r)`, and so on, with no `default`.
6. One place per switch, and the count is the number of `switch` expressions over that type — the
   build stops at each one. With a `default` arm the same change compiles everywhere and the new type
   silently takes the default branch, which is how a missing case reaches production.
"""

gen.write(TEMPLATE, BLOCKS)
