---
chapter: 2
part: 1
title: Primitives, References and the Two Meanings of `==`
summary: Know all eight primitive types and their real ranges, why integer overflow is silent, why `0.1 + 0.2` is not `0.3`, and why `==` compares references rather than values.
minutes: 55
tags: [primitives, references, boxing, overflow, equality]
---

Java has two kinds of value, and almost every confusing thing in the language comes from the
boundary between them. A **primitive** holds a value directly: an `int` *is* a number. A
**reference** holds the address of an object: a `String` variable *points at* text somewhere else.
Because `==` asks a different question for each one, Java has two ways to compare things, and using
the wrong one produces a bug that passes your tests and fails in production. This chapter is about
that boundary.

## Eight primitives

There are exactly eight, and they are part of the language rather than classes — which is why they
are spelled in lower case.

```java run
public class Sizes {
    public static void main(String[] args) {
        System.out.println("byte    " + Byte.SIZE    + " bits  " + Byte.MIN_VALUE    + " .. " + Byte.MAX_VALUE);
        System.out.println("short   " + Short.SIZE   + " bits  " + Short.MIN_VALUE   + " .. " + Short.MAX_VALUE);
        System.out.println("int     " + Integer.SIZE + " bits  " + Integer.MIN_VALUE + " .. " + Integer.MAX_VALUE);
        System.out.println("long    " + Long.SIZE    + " bits  " + Long.MIN_VALUE    + " .. " + Long.MAX_VALUE);
        System.out.println("float   " + Float.SIZE   + " bits");
        System.out.println("double  " + Double.SIZE  + " bits");
        System.out.println("char    " + Character.SIZE + " bits  (unsigned, a UTF-16 code unit)");
        System.out.println("boolean " + true + " — one bit of meaning, no defined size");
    }
}
```

```text
byte    8 bits  -128 .. 127
short   16 bits  -32768 .. 32767
int     32 bits  -2147483648 .. 2147483647
long    64 bits  -9223372036854775808 .. 9223372036854775807
float   32 bits
double  64 bits
char    16 bits  (unsigned, a UTF-16 code unit)
boolean true — one bit of meaning, no defined size
```

Those ranges are fixed by the language specification, not by the machine, which is the whole point:
an `int` is 32 bits on a phone, a server and a mainframe. There is no unsigned `int` in Java — one
genuine gap next to C — and `char` is the closest thing, being an unsigned 16-bit number that
happens to print as a character.

Literals can carry a suffix to say which type they are, and underscores to stay readable:

```java run
public class Literals {
    public static void main(String[] args) {
        var whole   = 10;      // int
        var big     = 10L;     // long
        var precise = 10.0;    // double
        var rough   = 10.0f;   // float
        System.out.println(whole + " " + big + " " + precise + " " + rough);
        System.out.println("1_000_000 = " + 1_000_000);
        System.out.println("0b1010 = " + 0b1010 + ", 0xFF = " + 0xFF + ", 0b1 = " + 0b1);
    }
}
```

```text
10 10 10.0 10.0
1_000_000 = 1000000
0b1010 = 10, 0xFF = 255, 0b1 = 1
```

## Overflow is silent, which is why it is dangerous

```java run
public class Overflow {
    public static void main(String[] args) {
        System.out.println("MAX_VALUE + 1        = " + (Integer.MAX_VALUE + 1));
        System.out.println("1_000_000 * 1_000_000 = " + (1_000_000 * 1_000_000));
        System.out.println("as longs            = " + (1_000_000L * 1_000_000L));
        try {
            Math.addExact(Integer.MAX_VALUE, 1);
        } catch (ArithmeticException e) {
            System.out.println("addExact says       : " + e.getMessage());
        }
    }
}
```

```text
MAX_VALUE + 1        = -2147483648
1_000_000 * 1_000_000 = -727379968
as longs            = 1000000000000
addExact says       : integer overflow
```

Integer arithmetic wraps around and nothing tells you. A quantity that grows — a counter, a byte
count, a price in cents — eventually crosses `Integer.MAX_VALUE` and turns negative, and the bug
appears somewhere else entirely. `Math.addExact` and `Math.multiplyExact` do the same arithmetic and
**throw** instead of wrapping; use them where an overflow means the data is already wrong.

## Floating point: precise enough to be trusted, not exact enough to be compared

```java run
public class Floats {
    public static void main(String[] args) {
        System.out.println("0.1 + 0.2 == 0.3 : " + (0.1 + 0.2 == 0.3));
        System.out.println("0.1 + 0.2        = " + (0.1 + 0.2));
        System.out.println("1.0 / 0          = " + (1.0 / 0));
        System.out.println("0.0 / 0          = " + (0.0 / 0));
        System.out.println("NaN == NaN       : " + (Double.NaN == Double.NaN));
        System.out.println("Double.isNaN(NaN): " + Double.isNaN(Double.NaN));
    }
}
```

```text
0.1 + 0.2 == 0.3 : false
0.1 + 0.2        = 0.30000000000000004
1.0 / 0          = Infinity
0.0 / 0          = NaN
NaN == NaN       : false
Double.isNaN(NaN): true
```

`double` cannot represent `0.1` exactly, for the same reason decimal notation cannot represent 1/3
exactly, so `0.1 + 0.2` is a hair above `0.3`. Two consequences you will use for the rest of your
life: never compare floating-point numbers with `==`, and never store money in a `double`. Floating
division by zero does **not** throw — it produces `Infinity` or `NaN` — and `NaN` is the only value
in Java that is not equal to itself.

Integer division is the other half of the story: it truncates towards zero, and dividing by an
integer zero throws.

```java throw
public class Divide {
    public static void main(String[] args) {
        int items = 12;
        int people = 0;
        System.out.println(items / people);
    }
}
```

```text
ArithmeticException: / by zero
```

## Widening is free; narrowing needs a cast

Java will happily put a small type into a bigger one, because nothing can be lost. The other
direction loses bits, so it refuses unless you say you meant it:

```java bad
public class Narrow {
    public static void main(String[] args) {
        int n = 5L;
        System.out.println(n);
    }
}
```

```text
incompatible types: possible lossy conversion from long to int
```

The same rule catches a literal that does not fit, which is a nicer error than a silent wrap:

```java bad
public class TooBig {
    public static void main(String[] args) {
        byte b = 200;
        System.out.println(b);
    }
}
```

```text
incompatible types: possible lossy conversion from int to byte
```

## Primitives have values; references point at objects

```java run
public class Defaults {
    static int count;
    static boolean flag;
    static String text;
    public static void main(String[] args) {
        System.out.println("int     = " + count);
        System.out.println("boolean = " + flag);
        System.out.println("String  = " + text);
    }
}
```

```text
int     = 0
boolean = false
String  = null
```

A field always has a value, even before you assign one: zero, `false`, or `null`. A **local**
variable gets no such courtesy — the compiler insists you assign it first, precisely because
"uninitialised" is what causes the bugs above:

```java bad
public class Uninitialised {
    public static void main(String[] args) {
        int total;
        System.out.println(total);
    }
}
```

```text
variable total might not have been initialized
```

Each primitive has a **wrapper** class — `Integer`, `Long`, `Double`, `Boolean` and so on — and
Java converts between them automatically. That convenience hides the trap this chapter is named
for:

```java run
public class Boxing {
    public static void main(String[] args) {
        Integer p = 127, q = 127;
        Integer r = 128, s = 128;
        System.out.println("127 == 127     : " + (p == q));
        System.out.println("128 == 128     : " + (r == s));
        System.out.println("128.equals(128): " + r.equals(s));
        Integer boxed = 128;
        int plain = 128;
        System.out.println("Integer == int : " + (boxed == plain));
    }
}
```

```text
127 == 127     : true
128 == 128     : false
128.equals(128): true
Integer == int : true
```

`==` on two objects asks "is this the same object?" — and it answers `true` for 127 by accident,
because the JDK caches the boxed values from −128 to 127 and hands out the same object for both.
At 128 the cache stops, `==` becomes false, and a program that worked all through testing starts
lying. The last line is the useful exception: comparing a wrapper to a primitive **unboxes** the
wrapper, so `==` compares numbers and behaves as you expect.

:::pitfall `==` on boxed numbers, the bug that passes review

```java
Integer a = 127, b = 127;
System.out.println(a == b);   // true  — cached
Integer c = 128, d = 128;
System.out.println(c == d);   // false — not cached
```

Someone changes a constant from 100 to 1000 and a passing check starts failing. Nothing about the
code looks wrong; `==` simply never meant "equal value" for objects. Use `.equals()` for every
object comparison, including boxed numbers, and let `==` mean "same object" or "same primitive" and
nothing else.
:::

## `char` is a number that prints as a letter

```java run
public class Chars {
    public static void main(String[] args) {
        char c = 'A';
        System.out.println("c          = " + c);
        System.out.println("(int) c    = " + (int) c);
        System.out.println("(char)(c+1)= " + (char) (c + 1));
        System.out.println("'a' - 'A'  = " + ('a' - 'A'));
    }
}
```

```text
c          = A
(int) c    = 65
(char)(c+1)= B
'a' - 'A'  = 32
```

Arithmetic on `char` produces an `int`, which is why the cast back to `char` is required. This is
the mechanism behind every letter-counting and Caesar-cipher exercise, and it is the reason a `char`
can hold an emoji only as a pair of code units — a topic Chapter 3 takes up.

:::scenario The billing report is a cent out

A report sums ten thousand prices stored as `double` and the total is wrong by a few cents.
Nobody can reproduce it with three items.

:::solution
Move the decimal point out of the type. Money is a count of the smallest unit, so keep it as a
`long` number of cents and format it only when you print — and format from the integer, never from
a division that reintroduces the error.

```java run-files
// ===== Money.java =====
public class Money {
    /** Cents, always. A long holds about 92 quadrillion cents. */
    public static long of(String text) {
        String clean = text.replace("£", "").replace(",", "");
        int dot = clean.indexOf('.');
        if (dot < 0) return Long.parseLong(clean) * 100;
        long pounds = Long.parseLong(clean.substring(0, dot));
        String pence = clean.substring(dot + 1);
        while (pence.length() < 2) pence = pence + "0";
        return pounds * 100 + Long.parseLong(pence.substring(0, 2));
    }

    public static String show(long cents) {
        long sign = cents < 0 ? -1 : 1;
        long abs = Math.abs(cents);
        return (sign < 0 ? "-£" : "£") + abs / 100 + "." + String.format("%02d", abs % 100);
    }
}

// ===== Main.java =====
public class Main {
    public static void main(String[] args) {
        long total = 0;
        for (String price : new String[] {"19.99", "0.10", "0.20", "5.00"}) {
            total += Money.of(price);
        }
        System.out.println("cents   = " + total);
        System.out.println("display = " + Money.show(total));
        System.out.println("as double = " + (19.99 + 0.10 + 0.20 + 5.00));
        System.out.println("sum of ten 0.10 in double = " + (0.1 + 0.1 + 0.1 + 0.1 + 0.1
                + 0.1 + 0.1 + 0.1 + 0.1 + 0.1));
    }
}
```

```text
cents   = 2529
display = £25.29
as double = 25.29
sum of ten 0.10 in double = 0.9999999999999999
```

The integer total is exact by construction; the `double` column is right here by luck and wrong by
a cent once the list is long enough. If you need decimal arithmetic on non-money values, `BigDecimal`
is the class — but it is slower and its constructor-from-`double` reproduces the same error, so
build it from a `String`.
:::

## Key takeaways

- There are eight primitive types (`byte`, `short`, `int`, `long`, `float`, `double`, `char`,
  `boolean`) with ranges fixed by the language, not by the machine.
- Integer overflow wraps silently; `Math.addExact` and `Math.multiplyExact` throw instead.
- Never compare `double` values with `==`, and never store money in one. `NaN` is not equal to
  itself; floating division by zero gives `Infinity` or `NaN`, integer division by zero throws.
- Widening conversions are implicit; narrowing needs a cast, and a literal that does not fit its
  variable is a compile error rather than a silent wrap.
- Fields get default values (`0`, `false`, `null`); local variables must be assigned before use.
- `==` compares references for objects and values for primitives. Boxed values from −128 to 127 are
  cached, so `==` on `Integer` works for small numbers and fails for larger ones. Use `.equals()`.

## Practice

- [ ] Convert 100 °C to °F and print it. Then change the formula to use integer division and
      explain why the answer changes.
- [ ] Write `Money.show` for a negative amount and check that `-1` cent prints `-£0.01`, not
      `£0.-1`.
- [ ] Print the numbers 100 to 130 twice, once comparing boxed `Integer`s with `==` and once with
      `.equals()`, and count how many answers differ.
- [ ] Multiply two large `long` values with `Math.multiplyExact` and catch the exception; then do
      the same with `*` and print the wrapped result.
- [ ] Print the uppercase alphabet using a `char` loop, and then print the alphabet using
      `'a' + i` without a cast — read the compiler error and fix it.

## Solutions

:::solution Exercise 1
`9.0 / 5.0` is floating division; `9 / 5` is integer division and evaluates to `1`, which loses the
fraction before the multiplication ever happens.

```java run
public class Temperatures {
    public static void main(String[] args) {
        int celsius = 100;
        double correct = celsius * 9.0 / 5.0 + 32;
        double wrong = celsius * 9 / 5 + 32;
        System.out.println("correct = " + correct);
        System.out.println("wrong   = " + wrong);
    }
}
```

```text
correct = 212.0
wrong   = 212.0
```

Both happen to agree here because 100 divides evenly by 5. Try 99 °C and the wrong version reads
210.0 instead of 210.2 — an integer division bug that hides whenever the numbers divide nicely.
:::

:::solution Exercise 2
`Math.abs(Long.MIN_VALUE)` is still negative, but no amount of money reaches it. The safe shape is to
format the sign separately and take the absolute value of the rest.

```java run
public class Negative {
    static String show(long cents) {
        String sign = cents < 0 ? "-" : "";
        long abs = Math.abs(cents);
        return sign + "£" + abs / 100 + "." + String.format("%02d", abs % 100);
    }
    public static void main(String[] args) {
        System.out.println(show(-1));
        System.out.println(show(-250));
        System.out.println(show(0));
    }
}
```

```text
-£0.01
-£2.50
£0.00
```
:::

:::solution Exercise 3
The boundary is at 127: everything up to and including it compares equal, and 128 onwards does not.
That is the whole `IntegerCache` range, and it is why this bug survives code review.

```java run
public class Cache {
    public static void main(String[] args) {
        int same = 0, differs = 0;
        for (int n = 100; n <= 130; n++) {
            Integer a = n, b = n;
            boolean eq = (a == b);
            boolean equals = a.equals(b);
            if (eq != equals) differs++; else same++;
            if (n >= 125 && n <= 129) {
                System.out.println(n + ": == " + eq + ", equals " + equals);
            }
        }
        System.out.println("differing answers = " + differs + " of " + (same + differs));
    }
}
```

```text
125: == true, equals true
126: == true, equals true
127: == true, equals true
128: == false, equals true
129: == false, equals true
differing answers = 3 of 31
```
:::

:::solution Exercise 4
`multiplyExact` throws where `*` silently wraps. In code where an overflow means the data is wrong
anyway, the exception is the feature: it fails at the point of the mistake instead of three reports
later.

```java run
public class Exact {
    public static void main(String[] args) {
        long a = 4_000_000_000L;
        long b = 4_000_000_000L;
        try {
            Math.multiplyExact(a, b);
        } catch (ArithmeticException e) {
            System.out.println("exact: " + e.getMessage());
        }
        System.out.println("plain: " + (a * b));
    }
}
```

```text
exact: long overflow
plain: -2446744073709551616
```
:::

:::solution Exercise 5
`'a' + i` is an `int`, because `char` arithmetic promotes to `int`. The compiler refuses to put an
`int` back into a `char` without a cast, which is the narrowing rule from earlier in this chapter.

```java run
public class Alphabet {
    public static void main(String[] args) {
        StringBuilder upper = new StringBuilder();
        StringBuilder lower = new StringBuilder();
        for (int i = 0; i < 26; i++) {
            upper.append((char) ('A' + i));
            lower.append((char) ('a' + i));
        }
        System.out.println(upper);
        System.out.println(lower);
    }
}
```

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
```
:::
