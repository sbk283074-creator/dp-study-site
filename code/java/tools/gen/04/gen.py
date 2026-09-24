#!/usr/bin/env python3
"""Generate chapters/04-operators-and-casting.md.

Every `text` fence is captured from a real `javac`/`java` run and every source
block is read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/04/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "04-operators-and-casting.md")

BLOCKS = {
    "division": gen.run("Division.java"),
    "promotion": gen.run("Promotion.java"),
    "casting": gen.run("Casting.java"),
    "badcast": gen.bad("BadCast.java", "possible lossy conversion"),
    "badbyte": gen.bad("BadByte.java", "possible lossy conversion"),
    "lossy": gen.warn("Lossy.java", "[lossy-conversions]"),
    "overflow": gen.run("Overflow.java"),
    "exact": gen.run("Exact.java"),
    "overflowthrow": gen.throw("OverflowThrow.java", "java.lang.ArithmeticException: integer overflow"),
    "mathops": gen.run("MathOps.java"),
    "floating": gen.run("Floating.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
    "sol5": gen.run("Sol5.java"),
}

TEMPLATE = r"""---
chapter: 4
part: 1
title: Operators, Casting and Integer Arithmetic
summary: Predict what an arithmetic expression does before you run it -- integer division, the promotion ladder, narrowing casts, silent overflow, and why 0.1 + 0.2 is not 0.3.
minutes: 55
tags: [operators, casting, promotion, overflow, Math, floating point]
---

An arithmetic expression in Java is a promise about types, and the compiler keeps that promise
whether or not you meant it. `7 / 2` is `3` because both operands are `int`. `Integer.MAX_VALUE + 1`
is negative because there is nowhere else for it to go. `0.1 + 0.2` is not `0.3` because neither of
those numbers exists in binary. None of the three is a warning and none is an error — they are the
arithmetic the language specifies, and a programmer who has not read this chapter meets all three as
bugs, usually in production.

Chapter 2 introduced the primitive types and said `int` is 32 bits. This chapter is about what the
operators *do* with them, and the theme is that every surprise here comes from one of two rules: an
operator promotes its operands before it runs, and a conversion that would lose information is
either refused or silent, never announced.

## Integer division does not round

@@division@@

Two lines there cause most of the arithmetic bugs in Java. `7 / 2` is `3`, not `3.5`, because both
operands are `int` and integer division **truncates toward zero** — which is also why `-7 / 2` is
`-3` and not `-4`. And `double d = 7 / 2` prints `3.0`, because the division happens *before* the
assignment widens the result. Assigning to a `double` does not make the division a floating-point
division; the cast has to reach an operand, as in `(double) 7 / 2`.

`%` is the companion operator and its sign follows the **dividend**: `-7 % 2` is `-1`, not `1`, and
`7 % -2` is `1`. That is the remainder, not the mathematical modulo, and it is the reason an
expression like `index % length` produces a negative index for negative input. `Math.floorMod` is
the version that behaves the way a ring buffer expects, and it appears below.

Division by zero is where the two worlds stop agreeing. `7 / 0` on integers throws
`ArithmeticException`, so it cannot be missed. `7.0 / 0` is `Infinity`, and `0.0 / 0` is `NaN` —
neither of which throws. A floating-point calculation can therefore carry a poisoned value through
a hundred lines and only fail at the point where somebody prints it.

## Every operand is promoted before the operator runs

@@promotion@@

Read that table as a ladder, because that is exactly what it is. A binary operator looks at both
operand types and promotes the narrower one to the wider: `byte`, `short` and `char` all become
`int` first — **even when both operands are already the same small type** — and from there the
ladder runs `int` → `long` → `float` → `double`. Nothing ever narrows on its own.

Two consequences are worth committing to memory. `byte + byte` is an `int`, which is why
`byte c = a + b;` does not compile even when you know the answer fits. And `long + float` is a
`float`, so adding a `long` to a `float` can lose precision *in the long* — the one rung on the
ladder that is not a widening in the everyday sense. If a calculation must stay exact, keep every
operand at `long` or below and never let a `float` into it.

`char` is a 16-bit unsigned number that happens to print as a letter, so `'A' + 1` is `66` and
`(char) ('A' + 1)` is `B`. That is not a curiosity: it is why a `switch` on a `char` and a `switch`
on an `int` are the same construct, and why comparing characters with `<` works.

The last two lines are the concatenation trap. `+` is left-associative, so `1 + 2 + "x"` adds the
numbers first and then concatenates, giving `3x`, while `"x" + 1 + 2` concatenates immediately and
gives `x12`. Once one operand is a `String` the operator means concatenation for the rest of the
expression, which is why `"" + a + b` and `a + b + ""` are different programs.

## Narrowing needs a cast, and a cast is a promise

A conversion from a wider type to a narrower one is where information is lost, so the compiler
refuses to do it silently. When you ask anyway, it truncates or wraps:

@@casting@@

Four of those lines are worth reading twice. `(int) 3.99` is `3` and `(int) -3.99` is `-3` — a cast
to an integer type **truncates toward zero**, it does not round, which is why `Math.round` exists
and gives `4` for the same input. `(byte) 300` is `44`, because 300 does not fit in 8 bits and Java
keeps the low byte: 300 − 256 = 44. `(int) 10^12` is `-727379968`, the same wrap seen from the other
end. And the `float` at the bottom is the subtlest of the four: `16_777_217` is a perfectly good
`int`, but a `float` has 24 bits of mantissa and cannot represent it, so the value is rounded to
`16_777_216` on the way in and the difference of `1` is gone before any arithmetic happens.

Now the two conversions the compiler will not do at all:

@@badcast@@

@@badbyte@@

Both say the same thing in different words. A `double` carries values an `int` cannot hold, and an
`int` carries values a `byte` cannot hold, so Java requires you to write the cast — which is the
language's way of asking whether you have thought about it. The cast is not a fix; it is a promise
that you know the value fits, and it is a promise the compiler will hold you to at run time by
truncating whatever you hand it.

One narrowing conversion escapes that check, and it is the one that hides in real code:

@@lossy@@

A **compound assignment** performs an implicit narrowing cast. `small += big` means
`small = (byte) (small + big)`, so the wrap happens with no cast in sight and no error. That block
is written as a `warn` block rather than a `run` block for exactly that reason: with `-Xlint:all`
the compiler names it, and this book compiles with `-Werror`, so here it is a build failure. In a
project without those flags the program builds and prints `-96`, which is 100,000 wrapped into a
signed byte. Turn the lint on; a silent wrap in a compound assignment is one of the few arithmetic
mistakes a compiler can actually catch for you.

:::warning `-Xlint:lossy-conversions` is not a default
The `lossy-conversions` category is part of `-Xlint:all`, but plain `javac` without any `-Xlint`
flag does not report it, and neither does an IDE that has not been configured. The wrap in the block
above is therefore invisible in the most common setup there is. This is the argument for building
with `-Xlint:all -Werror` from the first day of a project rather than adding it later, when there
are already hundreds of warnings to triage.
:::

## Overflow is silent, and that is the whole problem

An `int` holds 32 bits, so it holds values from `-2147483648` to `2147483647`. Go past either end
and the value wraps around to the other end. There is no exception, no flag, and no warning:

@@overflow@@

The pattern is arithmetic modulo 2³², read as a signed number, and once you see it the outputs stop
being surprising. `MAX_VALUE + 1` is `MIN_VALUE`. `1e6 * 1e6` is `-727379968` as an `int` and
`1000000000000` as a `long`, from the same expression with one `L` added. The running total in the
loop goes *negative* after five additions that each looked fine, and the `long` version does not.

The rule that follows is not "always use `long`" — that wastes memory and reads as superstition. It
is narrower and more useful: **an accumulator's type must be able to hold the largest value the
accumulator can reach, not the largest value any single term can reach.** Each term in that loop is
1.5 billion, which fits an `int` comfortably. Their sum is 7.5 billion, which does not.

## When silence is not acceptable: the exact arithmetic

Java 8 added a set of methods that do the same arithmetic and *check* it. They are slightly slower,
they throw on overflow, and they are the right choice wherever a wrong number is worse than a
crash — money, counters, indices, anything a user will read:

@@exact@@

`Math.addExact` and `Math.multiplyExact` compute the mathematically correct result and compare it
against the range of the type. If it does not fit, they throw `ArithmeticException` with the message
`integer overflow`. `Math.toIntExact` does the same job for a `long` being narrowed to an `int`,
which is the conversion `(int)` would have performed silently.

Uncaught, that exception ends the program — which is the point, and worth seeing once so the failure
is recognisable:

@@overflowthrow@@

Compare that with the `Overflow` block above, where the same arithmetic produced `-727379968` and
carried on. One of these two programs tells you it is broken; the other tells you nothing and lets a
negative byte count reach the dashboard.

## Math, and the three methods that surprise

`Math` holds the operations that have no operator: absolute value, powers, roots, rounding. Most of
it does what the name says. Three of them do not, and all three are in this block:

@@mathops@@

**`Math.abs(Integer.MIN_VALUE)` is negative.** The smallest `int` has no positive counterpart — its
negation is `2147483648`, which does not fit in an `int` — so `abs` returns the input unchanged.
This is not a bug in the JDK; it is the arithmetic, and it means `abs` is not a total function on
`int`. If a value can be `MIN_VALUE`, test for it or widen to `long` first.

**`Math.round(-2.5)` is `-2`, not `-3`.** `round` is defined as "add one half and floor", which
rounds halves toward positive infinity rather than away from zero. `round(2.5)` is `3` and
`round(-2.5)` is `-2`. If you need banker's rounding or rounding away from zero, `round` is not the
method you want and `BigDecimal` has the modes you do.

**`floorDiv` and `floorMod` are not `/` and `%`.** For positive operands they agree; for negative
ones they do not, and the difference is the sign convention. `floorMod(-7, 2)` is `1` where `-7 % 2`
is `-1`, and `floorMod` is the one that keeps a ring buffer's index inside the buffer. `Math.clamp`
is the third, new in Java 21, and it is the method to reach for instead of writing the same
three-line `if` in every class.

## The same trap in floating point

Everything above was about integers. Floating point has the same class of surprise and one extra
one: `double` cannot represent most decimal fractions exactly, so the errors do not wrap, they
accumulate:

@@floating@@

`0.1 + 0.2` is `0.30000000000000004`, and it is not equal to `0.3` — the literal `0.3` is a
different `double` from the sum. `0.1f == 0.1` is `false` for the same reason one rung down the
ladder: the `float` is widened to a `double` that is not the `double` literal. And `1.0 / 3.0` times
`3` happens to come back to exactly `1.0`, which is luck rather than a rule; other fractions do not.

Three habits follow. Never compare `double` values with `==`; compare the absolute difference
against a tolerance, or use `Double.compare` if you want a total order. Use `BigDecimal` for money
and anything else where the *decimal* value is what the user sees — `new BigDecimal("0.1")` from a
string is exact, while `new BigDecimal(0.1)` from the `double` is not, and the difference is a
classic first bug. And remember that `NaN` is not equal to itself, so `x == x` is `false` for a
poisoned value; `Double.isNaN(x)` is the test that works.

:::pitfall The average that is always a whole number

```java
int total = 46, count = 5;
double average = total / count;             // 9.0  -- the division happened first
double correct = (double) total / count;    // 9.2
```

The first line is the one that ships, because it *looks* fixed: the variable is a `double`, so the
author believes the arithmetic is. It is not. The division is an `int` division, it truncates to
`9`, and only then is `9` widened to `9.0`. Every ratio, percentage and rate computed from two
integers has this shape, and so does `done * 100 / total`, which is exact until the multiplication
overflows and is then fixed by writing `done * 100L / total` — the `L` on the *first* operand, since
the promotion happens before the operator runs.
:::

:::scenario The dashboard reports negative traffic

A service tracks the bytes it has served in a field declared `int`. It has been running for six
weeks. The traffic graph now shows a negative number and climbing back toward zero, and the
on-call engineer's first guess is a corrupt database.

:::solution
The database is fine. An `int` holds about 2.1 billion, which is 2 GB, and a service that serves a
few gigabytes a day crosses that in weeks. The addition wraps from `MAX_VALUE` to `MIN_VALUE` and
then counts up toward zero from below — which is why the graph looks like a glitch rather than a
reset, and why it "recovers" without anyone fixing anything.

@@scenario@@

The counter has to be a `long`, and the fix is one word in the declaration. The lesson generalises
past this service: **any accumulator that only ever increases needs a type whose range exceeds the
largest value it can reach in the lifetime of the process.** The `off by exactly 2^32` line is the
part worth keeping. An offset of exactly 2³² is the signature of a 32-bit wrap, and that single
number is what tells you to look at the *type* rather than at concurrency, at the database, or at
whoever last deployed. A lost update looks different; so does a reset.
:::

## Key takeaways

- Integer division truncates toward zero: `7 / 2` is `3`, `-7 / 2` is `-3`. Assigning the result to
  a `double` does not change that — cast an operand instead.
- `%` takes the sign of the dividend, so `-7 % 2` is `-1`. `Math.floorMod` is the ring-buffer
  version and keeps the result non-negative.
- Integer division by zero throws `ArithmeticException`; floating division by zero gives `Infinity`
  or `NaN` and never throws.
- A binary operator promotes to the wider type along `int` → `long` → `float` → `double`, and
  `byte`, `short` and `char` all promote to `int` first — so `byte + byte` is an `int`.
- A narrowing conversion needs a cast, and the cast truncates toward zero or wraps modulo the
  target's width. `(byte) 300` is `44`; `(int) 10^12` is `-727379968`.
- A compound assignment narrows implicitly, so `byte b = 0; b += 100_000;` wraps in silence.
  `-Xlint:all` reports it as `lossy-conversions`.
- `int` overflow wraps silently and is arithmetic modulo 2³². `Math.addExact`, `multiplyExact` and
  `toIntExact` throw `ArithmeticException: integer overflow` instead.
- `Math.abs(Integer.MIN_VALUE)` is still negative, and `Math.round(-2.5)` is `-2`; read the contract
  rather than trusting the name. `Math.floorDiv`, `floorMod` and (in Java 21) `clamp` are the three
  worth knowing.
- Never compare `double` values with `==`. Use a tolerance, `Double.compare`, or `BigDecimal` — and
  build it from a `String`, not from a `double`.
- An accumulator's type must hold the largest value the accumulator can reach, not the largest value
  any single term can reach.

## Practice

- [ ] Print `17 / 5`, `17 % 5`, `-17 / 5`, `-17 % 5` and the `floorDiv`/`floorMod` equivalents side
      by side, and show that `floorDiv * 5 + floorMod` reconstructs the original number.
- [ ] Write `clamp(int value, int min, int max)` by hand, then check it against `Math.clamp` for a
      value below the range, inside it and above it.
- [ ] Find the smallest positive `int` whose square is negative, and print it together with the
      wrapped product and the true product as a `long`.
- [ ] Turn a number of seconds into `H:MM:SS` using nothing but `/` and `%`, and check it on `0`,
      `59`, `60`, `3599`, `3600` and `86399`.
- [ ] Compute the average of five `int`s as a `double` twice — once the naive way and once with a
      cast — and print how much the naive version lost.

## Solutions

:::solution Exercise 1
`/` and `%` truncate toward zero, `floorDiv` and `floorMod` floor. The two pairs reconstruct the
same dividend, which is the identity that shows neither is "wrong" — they are different conventions,
and only one of them keeps an index inside an array:

@@sol1@@

For positive operands the two columns are identical, which is why the bug survives every test that
only uses positive input.
:::

:::solution Exercise 2
The hand-written version and `Math.clamp` agree on every case, including both boundaries — which is
the part worth testing, because an off-by-one in a clamp is invisible until a value lands exactly on
the limit:

@@sol2@@

Note the order of the two comparisons, because it decides which bound wins when a caller passes
`min > max`: this version returns `min` for a value below it and `max` for a value above, which is
not a defined answer so much as an accident of the order it tests in. `Math.clamp` documents that
case as illegal and throws instead, and that is the better contract — a caller who has swapped the
bounds wants to be told, not quietly clamped.
:::

:::solution Exercise 3
The answer is `46341`, and the interesting part is how close the boundary is: `46340` squared still
fits, and the very next integer does not. The `long` column is what the arithmetic meant to produce:

@@sol3@@

The loop condition is the lesson in miniature — `n * n >= 0` is true for every `n` until the square
wraps, so the loop is *looking for* the overflow rather than avoiding it. `Math.sqrt` of the true
square returns `46341.0`, which is how you recover the answer from the wreckage.
:::

:::solution Exercise 4
Two divisions and two remainders, in the order that keeps each result in range — hours first, then
the remainder fed to minutes, then the remainder of that fed to seconds:

@@sol4@@

`3599` becoming `0:59:59` and `3600` becoming `1:00:00` are the two cases that catch an off-by-one,
and `%02d` is what makes `0:01:00` print as `0:01:00` rather than `0:1:0`. The same three lines work
for any base-60 breakdown; only the constants change.

The last two lines are the check worth keeping, because they would catch a real mistake. Computing
the middle field as `totalSeconds / 60` instead of `totalSeconds % 3600 / 60` prints `1666` minutes
for the hundred-thousand-second sample, and `minutes and seconds are always under 60` turns from
`true` to `false` — which is the difference between a formatter and three numbers with colons.
:::

:::solution Exercise 5
The naive version prints `9.0` and the correct one prints `9.2`. The last line is the part people
find unsettling — the difference is not `0.2` but `0.1999999999999993`, because subtracting two
`double`s that are already approximations produces another approximation:

@@sol5@@

That is the whole reason to compare floating-point values with a tolerance rather than with `==`,
and the reason money belongs in `BigDecimal` or in an integer number of cents.
:::
"""

gen.write(TEMPLATE, BLOCKS)
