---
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

```java run
public class Division {
    public static void main(String[] args) {
        int a = 7, b = 2;
        System.out.println("7 / 2          = " + (a / b));
        System.out.println("7 % 2          = " + (a % b));
        System.out.println("7 / 2.0        = " + (7 / 2.0));

        int negative = -7;
        System.out.println("-7 / 2         = " + (negative / 2));
        System.out.println("-7 % 2         = " + (negative % 2));
        System.out.println("7 % -2         = " + (7 % -2));
        System.out.println("-7 % -2        = " + (negative % -2));

        double looksRight = 7 / 2;
        System.out.println("double d = 7/2 = " + looksRight);
        System.out.println("(double) 7 / 2 = " + ((double) 7 / 2));

        int zero = 0;
        try {
            System.out.println("7 / zero       = " + (7 / zero));
        } catch (ArithmeticException e) {
            System.out.println("7 / zero       : " + e.getMessage());
        }
        System.out.println("7.0 / zero     = " + (7.0 / zero));
        System.out.println("0.0 / zero     = " + (0.0 / zero));
        System.out.println("0 / 0.0        = " + (0 / 0.0));
    }
}
```

```text
7 / 2          = 3
7 % 2          = 1
7 / 2.0        = 3.5
-7 / 2         = -3
-7 % 2         = -1
7 % -2         = 1
-7 % -2        = -1
double d = 7/2 = 3.0
(double) 7 / 2 = 3.5
7 / zero       : / by zero
7.0 / zero     = Infinity
0.0 / zero     = NaN
0 / 0.0        = NaN
```

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

```java run
public class Promotion {
    static String type(Object value) {
        return value.getClass().getSimpleName();
    }

    public static void main(String[] args) {
        byte b = 10;
        short s = 20;
        char c = 'A';
        int i = 30;
        long l = 40L;
        float f = 50f;
        double d = 60.0;

        System.out.println("byte  + byte   -> " + type(b + b));
        System.out.println("short + int    -> " + type(s + i));
        System.out.println("char  + char   -> " + type(c + c));
        System.out.println("char  + int    -> " + type(c + i));
        System.out.println("int   + long   -> " + type(i + l));
        System.out.println("long  + float  -> " + type(l + f));
        System.out.println("float + double -> " + type(f + d));

        System.out.println("'A' + 1        = " + (c + 1));
        System.out.println("(char)('A' + 1)= " + (char) (c + 1));

        System.out.println("10 / 4.0       = " + (10 / 4.0));
        System.out.println("1 + 2 + \"x\"    = " + (1 + 2 + "x"));
        System.out.println("\"x\" + 1 + 2    = " + ("x" + 1 + 2));
    }
}
```

```text
byte  + byte   -> Integer
short + int    -> Integer
char  + char   -> Integer
char  + int    -> Integer
int   + long   -> Long
long  + float  -> Float
float + double -> Double
'A' + 1        = 66
(char)('A' + 1)= B
10 / 4.0       = 2.5
1 + 2 + "x"    = 3x
"x" + 1 + 2    = x12
```

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

```java run
public class Casting {
    public static void main(String[] args) {
        double d = 3.99;
        System.out.println("(int) 3.99        = " + (int) d);
        System.out.println("(int) -3.99       = " + (int) -d);
        System.out.println("Math.round(3.99)  = " + Math.round(d));

        int threeHundred = 300;
        System.out.println("(byte) 300        = " + (byte) threeHundred);
        System.out.println("(short) 70000     = " + (short) 70000);
        System.out.println("(int) 4294967296L = " + (int) 4294967296L);

        long trillion = 1_000_000_000_000L;
        System.out.println("(int) 10^12       = " + (int) trillion);

        System.out.println("(char) 65         = " + (char) 65);
        System.out.println("(int) 'A'         = " + (int) 'A');

        float rounded = 16_777_217;
        System.out.println("float 16777217    = " + rounded);
        System.out.println("(int) that float  = " + (int) rounded);
        System.out.println("lost on the way   = " + (16_777_217 - (int) rounded));
    }
}
```

```text
(int) 3.99        = 3
(int) -3.99       = -3
Math.round(3.99)  = 4
(byte) 300        = 44
(short) 70000     = 4464
(int) 4294967296L = 0
(int) 10^12       = -727379968
(char) 65         = A
(int) 'A'         = 65
float 16777217    = 1.6777216E7
(int) that float  = 16777216
lost on the way   = 1
```

Four of those lines are worth reading twice. `(int) 3.99` is `3` and `(int) -3.99` is `-3` — a cast
to an integer type **truncates toward zero**, it does not round, which is why `Math.round` exists
and gives `4` for the same input. `(byte) 300` is `44`, because 300 does not fit in 8 bits and Java
keeps the low byte: 300 − 256 = 44. `(int) 10^12` is `-727379968`, the same wrap seen from the other
end. And the `float` at the bottom is the subtlest of the four: `16_777_217` is a perfectly good
`int`, but a `float` has 24 bits of mantissa and cannot represent it, so the value is rounded to
`16_777_216` on the way in and the difference of `1` is gone before any arithmetic happens.

Now the two conversions the compiler will not do at all:

```java bad
public class BadCast {
    public static void main(String[] args) {
        int truncated = 3.99;
        System.out.println(truncated);
    }
}
```

```text
error: incompatible types: possible lossy conversion from double to int
```

```java bad
public class BadByte {
    public static void main(String[] args) {
        byte b = 200;
        System.out.println(b);
    }
}
```

```text
error: incompatible types: possible lossy conversion from int to byte
```

Both say the same thing in different words. A `double` carries values an `int` cannot hold, and an
`int` carries values a `byte` cannot hold, so Java requires you to write the cast — which is the
language's way of asking whether you have thought about it. The cast is not a fix; it is a promise
that you know the value fits, and it is a promise the compiler will hold you to at run time by
truncating whatever you hand it.

One narrowing conversion escapes that check, and it is the one that hides in real code:

```java warn
public class Lossy {
    public static void main(String[] args) {
        int big = 100_000;
        byte small = 0;
        small += big;
        System.out.println("100000 squeezed into a byte: " + small);
    }
}
```

```text
warning: [lossy-conversions] implicit cast from int to byte in compound assignment is possibly lossy
```

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

```java run
public class Overflow {
    public static void main(String[] args) {
        System.out.println("MAX_VALUE      = " + Integer.MAX_VALUE);
        System.out.println("MAX_VALUE + 1  = " + (Integer.MAX_VALUE + 1));
        System.out.println("MIN_VALUE      = " + Integer.MIN_VALUE);
        System.out.println("MIN_VALUE - 1  = " + (Integer.MIN_VALUE - 1));
        System.out.println("wrapped to the far end: " + (Integer.MAX_VALUE + 1 == Integer.MIN_VALUE));

        int million = 1_000_000;
        System.out.println("1e6 * 1e6 as int  = " + (million * million));
        System.out.println("1e6 * 1e6 as long = " + (1_000_000L * 1_000_000L));

        int total = 0;
        for (int i = 0; i < 5; i++) {
            total += 1_500_000_000;
        }
        System.out.println("5 x 1.5e9 as int  = " + total);
        System.out.println("5 x 1.5e9 as long = " + (5L * 1_500_000_000L));

        long correct = 1_000_000L * 1_000_000L;
        System.out.println("the long answer is right: " + (correct == 1_000_000_000_000L));
    }
}
```

```text
MAX_VALUE      = 2147483647
MAX_VALUE + 1  = -2147483648
MIN_VALUE      = -2147483648
MIN_VALUE - 1  = 2147483647
wrapped to the far end: true
1e6 * 1e6 as int  = -727379968
1e6 * 1e6 as long = 1000000000000
5 x 1.5e9 as int  = -1089934592
5 x 1.5e9 as long = 7500000000
the long answer is right: true
```

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

```java run
public class Exact {
    public static void main(String[] args) {
        System.out.println("addExact(1, 2)      = " + Math.addExact(1, 2));
        System.out.println("multiplyExact(6, 7) = " + Math.multiplyExact(6, 7));

        try {
            int bad = Math.addExact(Integer.MAX_VALUE, 1);
            System.out.println("unreachable: " + bad);
        } catch (ArithmeticException e) {
            System.out.println("addExact overflow       : " + e.getMessage());
        }

        try {
            System.out.println(Math.multiplyExact(1_000_000, 1_000_000));
        } catch (ArithmeticException e) {
            System.out.println("multiplyExact overflow  : " + e.getMessage());
        }

        try {
            System.out.println(Math.toIntExact(5_000_000_000L));
        } catch (ArithmeticException e) {
            System.out.println("toIntExact on a big long: " + e.getMessage());
        }

        System.out.println("and inside the range it just works: " + Math.toIntExact(5_000_000_000L - 4_999_999_999L));
    }
}
```

```text
addExact(1, 2)      = 3
multiplyExact(6, 7) = 42
addExact overflow       : integer overflow
multiplyExact overflow  : integer overflow
toIntExact on a big long: integer overflow
and inside the range it just works: 1
```

`Math.addExact` and `Math.multiplyExact` compute the mathematically correct result and compare it
against the range of the type. If it does not fit, they throw `ArithmeticException` with the message
`integer overflow`. `Math.toIntExact` does the same job for a `long` being narrowed to an `int`,
which is the conversion `(int)` would have performed silently.

Uncaught, that exception ends the program — which is the point, and worth seeing once so the failure
is recognisable:

```java throw
public class OverflowThrow {
    public static void main(String[] args) {
        int half = Integer.MAX_VALUE / 2 + 1;
        int doubled = Math.multiplyExact(half, 2);
        System.out.println("this line is never reached: " + doubled);
    }
}
```

```text
Exception in thread "main" java.lang.ArithmeticException: integer overflow
```

Compare that with the `Overflow` block above, where the same arithmetic produced `-727379968` and
carried on. One of these two programs tells you it is broken; the other tells you nothing and lets a
negative byte count reach the dashboard.

## Math, and the three methods that surprise

`Math` holds the operations that have no operator: absolute value, powers, roots, rounding. Most of
it does what the name says. Three of them do not, and all three are in this block:

```java run
public class MathOps {
    public static void main(String[] args) {
        System.out.println("abs(-5)          = " + Math.abs(-5));
        System.out.println("abs(MIN_VALUE)   = " + Math.abs(Integer.MIN_VALUE));
        System.out.println("min / max        = " + Math.min(3, 9) + " / " + Math.max(3, 9));
        System.out.println("pow(2, 10)       = " + Math.pow(2, 10));
        System.out.println("sqrt(2)          = " + Math.sqrt(2));
        System.out.println("hypot(3, 4)      = " + Math.hypot(3, 4));

        System.out.println("floorDiv(-7, 2)  = " + Math.floorDiv(-7, 2));
        System.out.println("floorMod(-7, 2)  = " + Math.floorMod(-7, 2));
        System.out.println("floorMod(7, -2)  = " + Math.floorMod(7, -2));
        System.out.println("-7 % 2           = " + (-7 % 2));

        System.out.println("round(2.5)       = " + Math.round(2.5));
        System.out.println("round(-2.5)      = " + Math.round(-2.5));
        System.out.println("ceil / floor     = " + Math.ceil(2.1) + " / " + Math.floor(2.9));
        System.out.println("clamp 15 to 10   = " + Math.clamp(15, 0, 10));
    }
}
```

```text
abs(-5)          = 5
abs(MIN_VALUE)   = -2147483648
min / max        = 3 / 9
pow(2, 10)       = 1024.0
sqrt(2)          = 1.4142135623730951
hypot(3, 4)      = 5.0
floorDiv(-7, 2)  = -4
floorMod(-7, 2)  = 1
floorMod(7, -2)  = -1
-7 % 2           = -1
round(2.5)       = 3
round(-2.5)      = -2
ceil / floor     = 3.0 / 2.0
clamp 15 to 10   = 10
```

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

```java run
import java.math.BigDecimal;

public class Floating {
    public static void main(String[] args) {
        double sum = 0.1 + 0.2;
        System.out.println("0.1 + 0.2        = " + sum);
        System.out.println("== 0.3           = " + (sum == 0.3));
        System.out.println("0.1f == 0.1      = " + (0.1f == 0.1));

        double third = 1.0 / 3.0;
        System.out.println("1.0 / 3.0        = " + third);
        System.out.println("(1.0/3.0) * 3.0  = " + (third * 3));

        BigDecimal exact = new BigDecimal("0.1").add(new BigDecimal("0.2"));
        System.out.println("BigDecimal       = " + exact);
        System.out.println("BigDecimal ==0.3 = " + (exact.compareTo(new BigDecimal("0.3")) == 0));

        System.out.println("(float) MAX_VALUE= " + (float) Integer.MAX_VALUE);
        System.out.println("NaN == NaN       = " + (Double.NaN == Double.NaN));
        System.out.println("isNaN(0.0 / 0.0) = " + Double.isNaN(0.0 / 0.0));
        System.out.println("1e308 * 10       = " + (1e308 * 10));
    }
}
```

```text
0.1 + 0.2        = 0.30000000000000004
== 0.3           = false
0.1f == 0.1      = false
1.0 / 3.0        = 0.3333333333333333
(1.0/3.0) * 3.0  = 1.0
BigDecimal       = 0.3
BigDecimal ==0.3 = true
(float) MAX_VALUE= 2.1474836E9
NaN == NaN       = false
isNaN(0.0 / 0.0) = true
1e308 * 10       = Infinity
```

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

```java run
public class Scenario {
    static int totalBytesInt(int[] responses) {
        int total = 0;
        for (int bytes : responses) {
            total += bytes;
        }
        return total;
    }

    static long totalBytesLong(int[] responses) {
        long total = 0;
        for (int bytes : responses) {
            total += bytes;
        }
        return total;
    }

    public static void main(String[] args) {
        int[] responses = {1_500_000_000, 1_000_000_000, 500_000_000};

        int broken = totalBytesInt(responses);
        long correct = totalBytesLong(responses);

        System.out.println("int  total = " + broken + " bytes");
        System.out.println("long total = " + correct + " bytes");
        System.out.println("the int total is negative: " + (broken < 0));

        System.out.println("dashboard shows = " + (broken / 1_073_741_824L) + " GB");
        System.out.println("the truth is    = " + (correct / 1_073_741_824L) + " GB");

        System.out.println("off by exactly 2^32: " + (correct - broken == 4_294_967_296L));
    }
}
```

```text
int  total = -1294967296 bytes
long total = 3000000000 bytes
the int total is negative: true
dashboard shows = -1 GB
the truth is    = 2 GB
off by exactly 2^32: true
```

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

```java run
public class Sol1 {
    public static void main(String[] args) {
        int a = 17, b = 5;
        int negative = -17;

        System.out.println("17 / 5          = " + (a / b));
        System.out.println("17 % 5          = " + (a % b));
        System.out.println("-17 / 5         = " + (negative / b));
        System.out.println("-17 % 5         = " + (negative % b));
        System.out.println("floorDiv(-17, 5)= " + Math.floorDiv(negative, b));
        System.out.println("floorMod(-17, 5)= " + Math.floorMod(negative, b));

        System.out.println("truncating and flooring differ only for negatives:");
        System.out.println("  floorDiv * 5 + floorMod = " + (Math.floorDiv(negative, b) * b + Math.floorMod(negative, b)));
        System.out.println("  /        * 5 + %        = " + ((negative / b) * b + (negative % b)));
    }
}
```

```text
17 / 5          = 3
17 % 5          = 2
-17 / 5         = -3
-17 % 5         = -2
floorDiv(-17, 5)= -4
floorMod(-17, 5)= 3
truncating and flooring differ only for negatives:
  floorDiv * 5 + floorMod = -17
  /        * 5 + %        = -17
```

For positive operands the two columns are identical, which is why the bug survives every test that
only uses positive input.
:::

:::solution Exercise 2
The hand-written version and `Math.clamp` agree on every case, including both boundaries — which is
the part worth testing, because an off-by-one in a clamp is invisible until a value lands exactly on
the limit:

```java run
public class Sol2 {
    static int clamp(int value, int min, int max) {
        if (value < min) {
            return min;
        }
        if (value > max) {
            return max;
        }
        return value;
    }

    public static void main(String[] args) {
        int[] samples = {-5, 0, 7, 10, 15};
        boolean agree = true;
        for (int value : samples) {
            int hand = clamp(value, 0, 10);
            int builtIn = Math.clamp(value, 0, 10);
            agree = agree && hand == builtIn;
            System.out.println("value " + value + " -> hand " + hand + ", Math.clamp " + builtIn);
        }
        System.out.println("the two agree on every case above: " + agree);

        String verdict;
        try {
            verdict = "returned " + Math.clamp(5, 10, 0);
        } catch (IllegalArgumentException e) {
            verdict = "threw " + e.getMessage();
        }
        System.out.println("swapped bounds: hand returned " + clamp(5, 10, 0) + ", Math.clamp " + verdict);
    }
}
```

```text
value -5 -> hand 0, Math.clamp 0
value 0 -> hand 0, Math.clamp 0
value 7 -> hand 7, Math.clamp 7
value 10 -> hand 10, Math.clamp 10
value 15 -> hand 10, Math.clamp 10
the two agree on every case above: true
swapped bounds: hand returned 10, Math.clamp threw 10 > 0
```

Note the order of the two comparisons, because it decides which bound wins when a caller passes
`min > max`: this version returns `min` for a value below it and `max` for a value above, which is
not a defined answer so much as an accident of the order it tests in. `Math.clamp` documents that
case as illegal and throws instead, and that is the better contract — a caller who has swapped the
bounds wants to be told, not quietly clamped.
:::

:::solution Exercise 3
The answer is `46341`, and the interesting part is how close the boundary is: `46340` squared still
fits, and the very next integer does not. The `long` column is what the arithmetic meant to produce:

```java run
public class Sol3 {
    public static void main(String[] args) {
        int n = 1;
        while (n * n >= 0) {
            n++;
        }
        System.out.println("smallest n whose square is negative: " + n);
        System.out.println("n * n                               = " + (n * n));
        System.out.println("(long) n * n                        = " + ((long) n * n));
        System.out.println("previous n still safe: " + ((n - 1) + " * " + (n - 1) + " = " + ((n - 1) * (n - 1))));
        System.out.println("sqrt of the true square             = " + Math.sqrt((long) n * n));
    }
}
```

```text
smallest n whose square is negative: 46341
n * n                               = -2147479015
(long) n * n                        = 2147488281
previous n still safe: 46340 * 46340 = 2147395600
sqrt of the true square             = 46341.0
```

The loop condition is the lesson in miniature — `n * n >= 0` is true for every `n` until the square
wraps, so the loop is *looking for* the overflow rather than avoiding it. `Math.sqrt` of the true
square returns `46341.0`, which is how you recover the answer from the wreckage.
:::

:::solution Exercise 4
Two divisions and two remainders, in the order that keeps each result in range — hours first, then
the remainder fed to minutes, then the remainder of that fed to seconds:

```java run
public class Sol4 {
    static String clock(int totalSeconds) {
        int hours = totalSeconds / 3600;
        int minutes = totalSeconds % 3600 / 60;
        int seconds = totalSeconds % 60;
        return String.format("%d:%02d:%02d", hours, minutes, seconds);
    }

    public static void main(String[] args) {
        int[] samples = {0, 59, 60, 3599, 3600, 86_399, 100_000};
        boolean fieldsInRange = true;
        for (int sample : samples) {
            String rendered = clock(sample);
            System.out.println(sample + " seconds -> " + rendered);
            String[] parts = rendered.split(":");
            fieldsInRange = fieldsInRange
                    && Integer.parseInt(parts[1]) < 60
                    && Integer.parseInt(parts[2]) < 60;
        }
        System.out.println("minutes and seconds are always under 60: " + fieldsInRange);
        System.out.println("the last sample is 27 hours and 40 seconds: " + clock(100_000));
    }
}
```

```text
0 seconds -> 0:00:00
59 seconds -> 0:00:59
60 seconds -> 0:01:00
3599 seconds -> 0:59:59
3600 seconds -> 1:00:00
86399 seconds -> 23:59:59
100000 seconds -> 27:46:40
minutes and seconds are always under 60: true
the last sample is 27 hours and 40 seconds: 27:46:40
```

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

```java run
public class Sol5 {
    public static void main(String[] args) {
        int[] scores = {7, 8, 9, 10, 12};
        int total = 0;
        for (int score : scores) {
            total += score;
        }

        double naive = total / scores.length;
        double correct = (double) total / scores.length;

        System.out.println("total            = " + total);
        System.out.println("count            = " + scores.length);
        System.out.println("total / count    = " + (total / scores.length));
        System.out.println("double naive     = " + naive);
        System.out.println("double correct   = " + correct);
        System.out.println("naive lost       = " + (correct - naive));
    }
}
```

```text
total            = 46
count            = 5
total / count    = 9
double naive     = 9.0
double correct   = 9.2
naive lost       = 0.1999999999999993
```

That is the whole reason to compare floating-point values with a tolerance rather than with `==`,
and the reason money belongs in `BigDecimal` or in an integer number of cents.
:::
