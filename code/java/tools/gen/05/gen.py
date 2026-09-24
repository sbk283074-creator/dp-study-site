#!/usr/bin/env python3
"""Generate chapters/05-control-flow.md.

Every `text` fence is captured from a real `javac`/`java` run and every source
block is read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/05/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "05-control-flow.md")

BLOCKS = {
    "loops": gen.run("Loops.java"),
    "assigninif": gen.bad("AssignInIf.java", "int cannot be converted to boolean"),
    "switchstatement": gen.run("SwitchStatement.java"),
    "fallthrough": gen.warn("Fallthrough.java", "[fallthrough]"),
    "switchexpression": gen.run("SwitchExpression.java"),
    "switchexhaustive": gen.bad("SwitchExhaustive.java",
                                "the switch expression does not cover all possible input values"),
    "switchpattern": gen.run("SwitchPattern.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 5
part: 1
title: Control Flow
summary: Choose between the three loops, write branches the compiler can check, and use switch expressions and Java 21 pattern matching instead of a chain of ifs.
minutes: 55
tags: [if, switch, switch expression, pattern matching, loops, break, continue]
---

Every program is a sequence of decisions and repetitions, and the syntax for both is small enough
to learn in an afternoon. The reason this chapter is worth an hour is that the *shape* of the choice
determines what the compiler can check for you. An `if` chain over a `String` or an `Object` cannot
be checked at all; a `switch` expression over the same value must cover every case or the program
does not build. That difference is the subject here.

Java also changed this area more than any other in the last decade. `switch` became an *expression*
that returns a value, and in Java 21 it gained pattern matching — so a `switch` can now test the
*type* of a value and add a condition to an arm. Everything below is compiled with `--release 21`
and the version each feature needs is named where it appears.

## The three loops

@@loops@@

`for` and `while` are the same loop with different bookkeeping: `for` collects the initialiser, the
test and the update into one line, which is why it is the right choice when you know the count and
the wrong choice when you do not. `while` says only "keep going while this is true", so the update
has to live inside the body where it can be forgotten — an infinite loop is almost always a `while`
whose counter was never incremented.

`do-while` is the one with a behaviour nothing else has: **the body runs before the test**, so it
runs at least once. The block above proves it — `m` starts at `10`, the condition `m < 5` is false
immediately, and the loop still printed `10`. Reach for it when the first iteration is what
*produces* the value the condition tests: a menu that must be shown once, a prompt that must be read
once, a retry that must be attempted once.

`continue` skips to the next iteration and `break` leaves the loop entirely, and both are readable
in moderation. The one form worth knowing and rarely used is the **labelled break**: a bare `break`
inside nested loops leaves only the inner one, and the usual workaround is a boolean flag that every
level has to check. `break outer;` leaves both at once, as the output shows, and the label is a name
you choose rather than syntax you have to remember.

One scoping rule follows from the output's last line. A variable declared *in* the `for` header is
visible only inside the loop; declared outside, it survives and holds the value that failed the
test. That is occasionally what you want and more often the sign that the loop should have been a
method.

## if, and the assignment that is not a comparison

An `if` takes a `boolean` and nothing else. Java will not treat a number as true or false, which is
a deliberate break from C and the reason one of the most famous C bugs cannot happen here:

@@assigninif@@

In C, `if (status = 1)` assigns and then tests the result, so the condition is always true and the
branch always runs. In Java the assignment produces an `int`, an `int` is not a `boolean`, and the
compiler refuses. The `=` that should have been `==` is a compile error rather than a silent
always-true branch, and that is worth a paragraph in a book because it is one of the few places a
language design decision removes a whole bug class.

Two habits around `if` are worth adopting before you write many of them. **Always use braces**, even
for a one-line body: a branch without braces takes exactly one statement, so adding a second line
later puts it outside the `if` and the indentation lies about what runs. And **put the constant
first** when comparing — `if (1 == status)` fails to compile if you write `=` by mistake, whereas
`if (status = 1)` is caught only because Java is strict. The braces habit is not style; it is the
difference between a change that works and a change that appears to.

## The switch statement, and the fall-through it cannot see

The old `switch` is a jump table: it selects a label and then *runs from there onwards* until a
`break` or the end of the block. When every case ends with `break`, that is invisible:

@@switchstatement@@

Grouping labels with no code between them — `case 0: case 6:` — is the one case where falling
through is the intent, and the compiler stays quiet about it because there is nothing to execute in
between. A `switch` also selects on a `String`, an enum and a `char`, not just an integer, and the
comparison is `.equals` rather than `==` — which is why `switch` on a `String` works while `==` on
one does not.

Now remove a `break` and the same construct changes meaning without changing syntax:

@@fallthrough@@

That block is *correct* — it accumulates "admin write read" on purpose, and the warning is the
compiler saying it cannot tell. It fires on **every** fall-through, intentional or not, because a
missing `break` and a deliberate one look identical in the source. So the idiom for intentional
fall-through is an annotation:

```java
@SuppressWarnings("fallthrough")
static String describe(int level) { ... }
```

And that is exactly where the trouble starts. The annotation silences the warning for the whole
method, so the next person who edits it and forgets a `break` gets no diagnostic either. The
`Scenario` section at the end of this chapter is that mistake, in full, with a price attached.

## Switch expressions

Java 14 made `switch` able to produce a value, and the arrow form removes fall-through entirely:
each arm is one expression, there is no `break`, and nothing can run into the next label.

@@switchexpression@@

Four changes are worth naming. The **arrow form** `case 0, 6 ->` accepts several labels separated by
commas, which is how the two weekend days are handled without the empty-case trick. The result is
**assigned**, so a `switch` expression is a value like any other and can be returned directly — no
`String result;` declared above and mutated inside. A **block arm** needs `yield` rather than
`return`, because `return` would leave the enclosing method instead of the switch; the `default` arm
above shows the shape. And a `switch` expression must be **exhaustive**: since it has to produce a
value on every path, the compiler checks that you covered everything.

That last rule is the one that changes what the compiler can do for you, and it is enforced:

@@switchexhaustive@@

The `daysIn` method earlier in this section has a `default` and so is exhaustive. The program above
covers two days out of the `int` range and has no `default`, so there is a value of `day` for which
the expression has no answer — and the compiler says so rather than inventing one. Compare that with
the `switch` *statement*, which is allowed to match nothing at all and simply do nothing. The
expression is stricter because it has to hand back a value; the statement is laxer because it does
not. When a `switch` computes something, prefer the expression.

## Pattern matching, so a branch can test a type

A chain of `if (x instanceof String s)` blocks is what you write when the input can be one of
several types, and Java 21 lets the `switch` do it directly. An arm can name a **type pattern** with
a binding, add a **`when` guard**, and match `null` as a case:

@@switchpattern@@

Read the arms in order, because order is the semantics. `case null` is a case like any other — the
one thing a traditional `switch` can never do, since it throws `NullPointerException` before
matching anything. A `when` guard is part of its arm, so `case Integer i when i < 0` and
`case Integer i` are different arms and the guard has to come first or the general arm swallows
every integer. That ordering requirement is not stylistic: an arm whose pattern is subsumed by an
earlier arm is a compile error, which is the compiler catching a branch that could never run.

Two smaller things in the output. `""` and `"   "` both report `blank text`, because the guard
`isBlank()` is true for an empty string — a guard is an ordinary boolean expression and gets no
special treatment. And `7L` lands in `default` and prints `some other Long`, because a `Long` is not
an `Integer`; the type patterns match the exact class, not a numeric family.

:::pitfall The `break` you did not delete

```java
switch (tier) {
    case 3: percent = 20;
    case 2: percent = 10;
    case 1: percent = 5;
        break;
    default: percent = 0;
}
```

Every case assigns, the last one breaks, and the code reads as if it were a list of separate
branches. It is not: `tier 3` assigns `20`, falls into `case 2` and assigns `10`, falls into
`case 1` and assigns `5`, then breaks. **The last assignment wins, so the highest tier gets the
smallest discount.** If the method carries `@SuppressWarnings("fallthrough")` — and this one has to,
or `-Werror` rejects it — nothing warns you at all. The arrow form cannot express this mistake, and
that is the argument for using it: a whole class of bug stops being writable.
:::

:::scenario The VIP tier gets the smallest discount

A pricing service reads a customer tier and applies a percentage. Finance reports that tier 3
customers are being undercharged, tier 1 customers are billed correctly, and the code "has not
changed in a year".

:::solution
It has not changed — and it never worked. The tier is read correctly and the percentage is looked up
in a `switch` statement whose cases assign and do not break, so every tier above 1 falls through to
`case 1` and ends up with the 5% meant for tier 1. Tier 1 is the one tier that is correct, which is
exactly why nobody noticed: the bug is invisible to whoever tests with the common case.

@@scenario@@

The measured cost is on the last two lines: a tier 3 customer is charged `9500` where the policy
says `8000`, and the `1500` gap is per customer. The fix is to make the lookup a `switch`
expression, which cannot fall through:

```java
static int discountPercent(int tier) {
    return switch (tier) {
        case 3 -> 20;
        case 2 -> 10;
        case 1 -> 5;
        default -> 0;
    };
}
```

Two things are worth taking from this beyond the fix. The first is the *asymmetry of the symptom*:
one tier was right, so a test suite that checked "a discount is applied" would pass, and only a test
that pinned the exact percentage per tier would fail. The second is that the bug was **silenced
rather than hidden** — the fall-through warning was there and an annotation turned it off, which is
the failure mode of every suppression. When you add `@SuppressWarnings`, the annotation covers the
whole method from then on, including the line somebody adds next year.
:::

## Key takeaways

- `for` and `while` differ only in bookkeeping; `do-while` runs its body **before** the test and so
  runs at least once, which is what the `m = 10` example shows.
- A variable declared in the `for` header is scoped to the loop. Declared outside, it holds the
  value that failed the test after the loop ends.
- A bare `break` leaves one loop; a labelled `break outer;` leaves all of them at once, without the
  boolean flag the nested-loop workaround needs.
- `if` requires a `boolean`, so `if (x = 1)` is a compile error rather than an always-true branch.
  Always use braces, even for one statement.
- A `switch` statement runs from the matching label onwards until a `break`, so a missing `break`
  changes the meaning with no syntax error. `-Xlint:fallthrough` warns about every fall-through,
  intentional or not.
- `@SuppressWarnings("fallthrough")` silences that warning for the whole method, including the
  accidental fall-through somebody adds later.
- A `switch` expression (Java 14+) uses the arrow form, has no fall-through, can be assigned, uses
  `yield` to leave a block arm, and must be exhaustive — the compiler rejects one that is not.
- Java 21 pattern matching lets an arm name a type with a binding, add a `when` guard, and match
  `null`. Arms are tried in order, and an arm subsumed by an earlier one is a compile error.

## Practice

- [ ] Print `1` to `20`, replacing multiples of three with `Fizz`, multiples of five with `Buzz` and
      multiples of both with `FizzBuzz`, using a loop and a helper method.
- [ ] Classify a triangle from three side lengths as equilateral, isosceles, scalene, degenerate or
      not a triangle, and check it on a case of each kind.
- [ ] Write a `switch` expression over `Object` that distinguishes `null`, a negative `Integer`, a
      non-negative `Integer`, an empty `String` and a non-empty `String`, and count how many samples
      land in each arm.
- [ ] Take the fall-through discount from the scenario and rewrite it as a `switch` expression, then
      print the price each tier pays and assert that the discount is monotone in the tier.

## Solutions

:::solution Exercise 1
Test the most specific condition first. `n % 15 == 0` has to come before `n % 3 == 0` and
`n % 5 == 0`, or the number is classified as `Fizz` or `Buzz` and never reaches `FizzBuzz`:

@@sol1@@

There are `6` multiples of fifteen up to `100` but `33` of three and `20` of five, so the ordering
is not a detail — the `FizzBuzz` branch is the rarest and has to be tested first. The same shape
appears in any classification where the categories overlap, and the rule is always the same:
**narrowest condition first**.
:::

:::solution Exercise 2
The checks are ordered so that each one can assume the previous ones passed — positivity, then the
triangle inequality, then the equalities. That order is what makes each condition readable on its
own line:

@@sol2@@

`1,2,3` is the case worth looking at: all three sides are positive and it is still not a triangle,
because `1 + 2` is not greater than `3`. A degenerate triangle has zero area, and the inequality is
strict — `<=` rather than `<` is the difference between rejecting it and calling it isosceles.
:::

:::solution Exercise 3
Five arms, and the guard is what separates the two `Integer` arms and the two `String` arms. The
tally is computed from the arm that actually ran, not from the input type:

@@sol3@@

Each counted arm is used exactly once, and the two samples that fall to `default` and to
`Boolean b` are absent from the tally — which is the point of printing both. Note that `""` reaches
the `empty string` arm rather than the `string` arm: a guard is evaluated before the arm is chosen,
so the more specific arm has to be written first and is.
:::

:::solution Exercise 4
The arrow form makes the fall-through impossible to write, and the monotonicity check is what turns
"it looks right" into something a test can fail:

@@sol4@@

The four customers pay `36500` together against `40000` undiscounted, and the last line reports
`true` because each tier pays no more than the tier below it. That is the assertion the original
code would have failed: under the fall-through version every tier from 1 up paid the same `9500`,
so the discount was flat rather than increasing, and no single-price test would have caught it.
:::
"""

gen.write(TEMPLATE, BLOCKS)
