---
chapter: 3
part: 1
title: Types and Numbers
summary: Choose integer and floating-point types deliberately — know what each can hold, what happens when it overflows, and why a size you measured on your own machine is not a fact about the language.
minutes: 50
tags: [types, sizeof, integers, overflow, floating point, limits]
---

A type in C is two facts welded together: how many bytes the value occupies, and how those bytes
should be read. Nothing about that is automatic. The language gives you a menu of sizes and lets you
pick, and when you pick wrong it does not stop you — it converts your value to whatever fits and
carries on. That is why the same program can be correct for a year and then produce a negative
download counter on the one day somebody transfers two gigabytes. This chapter is about picking the
size on purpose, knowing what the numbers mean, and recognising the two failure modes that matter:
silent conversion and overflow.

## A type is a size and an interpretation

`sizeof` is an operator, not a function, and it answers the size question in bytes.

```c run
#include <stdio.h>

int main(void) {
    printf("sizeof(char) == 1: %d\n", (int)(sizeof(char) == 1));
    printf("sizeof(short) <= sizeof(int): %d\n", (int)(sizeof(short) <= sizeof(int)));
    printf("sizeof(int) <= sizeof(long): %d\n", (int)(sizeof(int) <= sizeof(long)));
    printf("sizeof(long) <= sizeof(long long): %d\n", (int)(sizeof(long) <= sizeof(long long)));
    printf("sizeof(int) >= 2: %d\n", (int)(sizeof(int) >= 2));
    printf("sizeof(float) <= sizeof(double): %d\n", (int)(sizeof(float) <= sizeof(double)));
    return 0;
}
```

```text
sizeof(char) == 1: 1
sizeof(short) <= sizeof(int): 1
sizeof(int) <= sizeof(long): 1
sizeof(long) <= sizeof(long long): 1
sizeof(int) >= 2: 1
sizeof(float) <= sizeof(double): 1
```

Those six lines are the *entire* set of guarantees the C standard makes about type sizes. A `char` is
exactly one byte — and a byte is `CHAR_BIT` bits, which is 8 on every platform you will meet. Every
other type is at least as large as the one before it, and an `int` is at least 16 bits. That is all.
Nothing in the language says an `int` is four bytes.

Which means the only honest way to talk about the actual numbers is to print them:

```c run
#include <stdio.h>

int main(void) {
    printf("char        %zu\n", sizeof(char));
    printf("short       %zu\n", sizeof(short));
    printf("int         %zu\n", sizeof(int));
    printf("long        %zu\n", sizeof(long));
    printf("long long   %zu\n", sizeof(long long));
    printf("void *      %zu\n", sizeof(void *));
    printf("float       %zu\n", sizeof(float));
    printf("double      %zu\n", sizeof(double));
    printf("long double %zu\n", sizeof(long double));
    return 0;
}
```

Run it and write the numbers down. On the machine this book was written on — Apple clang 21,
arm64 macOS — it prints:

| Type | Bytes | On 64-bit Windows | On x86-64 Linux |
|---|---|---|---|
| `char` | 1 | 1 | 1 |
| `short` | 2 | 2 | 2 |
| `int` | 4 | 4 | 4 |
| `long` | 8 | **4** | 8 |
| `long long` | 8 | 8 | 8 |
| `void *` | 8 | 8 | 8 |
| `float` | 4 | 4 | 4 |
| `double` | 8 | 8 | 8 |
| `long double` | **8** | 8 | **16** |

Look at the two bold entries. `long` is eight bytes on macOS and Linux and four on 64-bit Windows —
the one type whose width genuinely differs between the three platforms you will actually use. And
`long double` is eight bytes here, which is to say it is a `double` with a longer name, because
Apple's arm64 ABI declines to provide anything wider. On x86-64 Linux it is sixteen. This is why the
book prints sizes inside a program instead of writing them into prose as rules: **a size is a fact
about a platform, not about C.**

## The integer family

Six signed integer types, each with an unsigned counterpart:

| Type | Typical width | Holds (signed) |
|---|---|---|
| `char` | 8 bits | −128 … 127 |
| `short` | 16 bits | −32 768 … 32 767 |
| `int` | 32 bits | −2 147 483 648 … 2 147 483 647 |
| `long` | 32 or 64 bits | platform-dependent |
| `long long` | 64 bits | ±9.2 × 10¹⁸ |
| `unsigned` versions | same | 0 … 2ⁿ − 1 |

Do not type those limits. Ask for them:

```c run
#include <stdio.h>
#include <limits.h>

int main(void) {
    printf("INT_MAX   %d\n", INT_MAX);
    printf("INT_MIN   %d\n", INT_MIN);
    printf("UINT_MAX  %u\n", UINT_MAX);
    printf("LLONG_MAX %lld\n", LLONG_MAX);
    return 0;
}
```

```text
INT_MAX   2147483647
INT_MIN   -2147483648
UINT_MAX  4294967295
LLONG_MAX 9223372036854775807
```

`<limits.h>` is the only place these numbers should come from. If your code needs to know the
largest `int`, it needs `INT_MAX`, not `2147483647` — because on a platform where `int` is 16 bits,
the literal is wrong and the macro is right.

When the exact width is part of the data format — a binary file header, a network packet, a hardware
register — use `<stdint.h>` instead and say the width out loud:

```c run
#include <stdio.h>
#include <stdint.h>

int main(void) {
    uint8_t  flags = 0x0F;
    int32_t  sample_count = -1;
    uint64_t bytes_served = 0;

    printf("flags  0x%02X\n", (unsigned int)flags);
    printf("count  %d\n", (int)sample_count);
    printf("served %llu\n", (unsigned long long)bytes_served);
    return 0;
}
```

```text
flags  0x0F
count  -1
served 0
```

The casts in those three `printf` calls are the price of portability, and they are worth paying. On
this platform `int32_t` is an `int`, so `%d` would work without the cast; on a platform where `int` is
16 bits it would be a `long` and the format string would be wrong. `uint64_t` has the same problem —
it is `unsigned long` on macOS and Linux and `unsigned long long` on 64-bit Windows. Casting to a type
with a guaranteed specifier makes the call correct everywhere.

`int32_t` is exactly 32 bits or the header refuses to compile, which is a much better failure than a
program that reads a file wrong. Reach for these whenever the width is a requirement rather than a
convenience.

## Signed overflow is not a wrap

Here is the mistake that costs the most money. An `int` counter, incremented one too many times:

```c run-san-catch
#include <stdio.h>
#include <limits.h>

int main(void) {
    int served = INT_MAX;
    served = served + 1;
    printf("%d\n", served);
    return 0;
}
```

```text
runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

Note what did *not* happen. The build succeeded — no compiler error, no warning. The run exited `0`.
The program printed `-2147483648`, a perfectly ordinary-looking number. The only reason you know
anything is wrong is that UndefinedBehaviorSanitizer was watching, and this is exactly why the flag
from Chapter 1 belongs in your test suite rather than in your drawer.

Signed overflow is **undefined behaviour**, which is a stronger statement than "it wraps around". The
standard does not say the result is `−2147483648`. It says the program has no defined meaning at all,
and the compiler is entitled to assume it never happens — which makes the obvious after-the-fact check
useless, because "this addition never overflows" is precisely the assumption the optimiser uses to
delete the condition. You cannot detect signed overflow afterwards. You have to check *before* you add:

```c run
#include <stdio.h>
#include <limits.h>

int main(void) {
    int total = INT_MAX - 5;
    int incoming = 10;

    if (incoming > INT_MAX - total) {
        printf("refusing %d bytes: would overflow\n", incoming);
    } else {
        total += incoming;
        printf("total is now %d\n", total);
    }
    return 0;
}
```

```text
refusing 10 bytes: would overflow
```

The check is a subtraction, not an addition, and that is the whole trick: `INT_MAX - total` cannot
itself overflow while `total` is non-negative, so it is safe to compute, and comparing the incoming
value against the remaining headroom is a question the optimiser cannot reason away.

Unsigned types are different, and deliberately so:

```c run
#include <stdio.h>
#include <limits.h>

int main(void) {
    unsigned int served = UINT_MAX;
    served = served + 1u;
    printf("%u\n", served);
    return 0;
}
```

```text
0
```

Unsigned arithmetic wraps modulo 2ⁿ and that behaviour is **guaranteed by the standard**. It is still
usually a bug — a counter that resets to zero is no more useful than one that goes negative — but it
is a *predictable* bug, and it is the reason a hash function or a checksum can use unsigned arithmetic
freely.

:::pitfall Reading a size as a signed number
`sizeof` does not return an `int`. It returns `size_t`, an unsigned type, and any arithmetic mixing
it with a signed value converts the signed value to unsigned first. A negative number becomes
enormous.

```c warn
#include <stdio.h>

int main(void) {
    int remaining = -1;
    if (remaining < sizeof(int)) {
        printf("there is room\n");
    } else {
        printf("no room\n");
    }
    return 0;
}
```

```text
comparison of integers of different signs: 'int' and 'unsigned long' [-Wsign-compare]
```

`remaining` is `−1`. Converting it to `unsigned long` yields 18446744073709551615, which is not less
than 4, so the program takes the `else` branch and reports that a negative amount of remaining space
means there is no room. The comparison is not just unhelpful — it is backwards. The compiler catches
this one for you, but only because the warning is enabled; under `-Werror` it stops the build. The
habit that avoids it entirely is to keep counts unsigned: if a value can never be negative, do not
give it a signed type in the first place.
:::

## Floating point is not exact

A `double` stores a value as a sign, a mantissa and a power of two. Most decimal fractions are not
exactly representable in binary — `0.1` is the canonical example — so every floating-point number you
write is really the nearest representable value. The errors are tiny, and they accumulate.

```c run
#include <stdio.h>

int main(void) {
    double tenth = 0.1;
    double fifth = 0.2;

    printf("0.1 + 0.2 = %.17f\n", tenth + fifth);
    printf("equal to 0.3? %d\n", (int)(tenth + fifth == 0.3));
    return 0;
}
```

```text
0.1 + 0.2 = 0.30000000000000004
equal to 0.3? 0
```

Seventeen decimal places is enough to show every bit of a `double`, which is why the default six
places hide this. The lesson is not "floating point is broken" — it is that **`==` is the wrong tool
for comparing floating-point values**. Compare with a tolerance, or better, avoid the comparison:
work in integer units (cents, not pounds; milliseconds, not seconds) whenever the value has a fixed
precision.

`float` and `double` differ in precision rather than in kind. `<float.h>` gives you `FLT_DIG` (6) and
`DBL_DIG` (15) — the number of decimal digits each can round-trip — which is the honest way to
describe how much a float is worth. A `float` has about seven significant digits; a `double` about
sixteen. Money and physics simulations use `double` for that reason.

## Conversions happen whether you ask or not

C converts between numeric types automatically, and the conversion does not have to be lossless. This
is where a value silently becomes a different value:

```c warn
#include <stdio.h>

int main(void) {
    char letter = 300;
    printf("%d\n", letter);
    return 0;
}
```

```text
implicit conversion from 'int' to 'char' changes value from 300 to 44 [-Wconstant-conversion]
```

`char` holds −128…127 on this platform, so 300 does not fit. The compiler keeps the low eight bits and
you get 44. The warning is a gift — it tells you the value changed *at compile time*, which is only
possible because `300` is a constant. When the value arrives from a file or a user, there is nothing
to warn about, and the truncation happens in silence.

That is the general shape of the hazard: **the compiler can only warn about conversions it can see.**
Two more conversions worth knowing:

- Comparing a signed value with an unsigned one promotes the signed one — the `remaining < sizeof(int)`
  trap above.
- Whether plain `char` is signed or unsigned is the platform's choice, not the standard's. On arm64
  and x86-64 macOS and Linux it is signed, so `(char)200` is −56. Never rely on either behaviour: if
  the sign matters, write `signed char` or `unsigned char` and say what you mean.

## The type of a literal

Every literal has a type before you put it anywhere, and the type decides what the expression does.

| Literal | Type | Note |
|---|---|---|
| `42` | `int` | the default for whole numbers |
| `42u` | `unsigned int` | |
| `42L` | `long` | |
| `42LL` | `long long` | |
| `42.0` | `double` | the default for fractional numbers |
| `42.0f` | `float` | |
| `'A'` | **`int`** | a character constant, not a `char` |
| `"A"` | `char[2]` | a string: `'A'` and `'\0'` |

The last two rows are the ones that bite. A character constant in C has type `int`, which is why
`printf("%c", 'A')` works and why `sizeof('A')` is 4 on this platform rather than 1. And `"A"` is not
a character at all — it is an array of two bytes, and the second byte is a null terminator. Mixing
them up is common enough that the compiler rejects it outright:

```c bad
#include <stdio.h>

int main(void) {
    char letter = "A";
    printf("%c\n", letter);
    return 0;
}
```

```text
error: incompatible pointer to integer conversion initializing 'char' with an expression of type 'char[2]' [-Wint-conversion]
```

Read the type the compiler inferred: `char[2]`. Double quotes always mean an array, single quotes
always mean a single value. The error message is telling you exactly that.

:::scenario The counter that went negative after two gigabytes
A file-sharing service tracks how many bytes it has served today in an `int`. It works in every test,
because the fixtures serve a few megabytes. In production a single large transfer pushes the running
total past `INT_MAX` — 2 147 483 647 bytes, about 2.1 GB. The dashboard shows a negative number, and
the daily quota check starts refusing uploads, because the comparison against the limit now goes the
wrong way.

:::solution Choose the width from the data, and make the tests reach the boundary
Two fixes, and the second is the one people skip.

The type first. A byte count has no business in a signed 32-bit integer — bytes are never negative,
and 2.1 GB is not a large file. `uint64_t` from `<stdint.h>` says both facts in the declaration:

```c run
#include <stdio.h>
#include <stdint.h>

int main(void) {
    uint64_t served = 2147483647u;
    served += 1000000000u;

    printf("served %llu bytes\n", (unsigned long long)served);
    printf("fits in an int? %d\n", (int)(served <= (uint64_t)INT32_MAX));
    return 0;
}
```

```text
served 3147483647 bytes
fits in an int? 0
```

The cast to `unsigned long long` in the `printf` is not decoration. `uint64_t` is `unsigned long` on
this platform and `unsigned long long` on others, so the portable spelling of "print this 64-bit
unsigned value" is to cast to a type with a guaranteed specifier. Chapter 2's rule — the format
string is a promise — applies to every type in this chapter.

Now the part that matters more. Changing the type fixes *this* overflow, not the next one. The
reason it reached production is that no test ever drove the counter anywhere near its limit, so the
bug was invisible. Running the test suite with `-fsanitize=undefined` turns that class of bug into a
failing test the first time a boundary case appears, instead of a dashboard anomaly weeks later.
Pick the type deliberately, then prove the boundary behaves.
:::

## Key takeaways

- A type is a size plus an interpretation; `sizeof` reports the size in bytes.
- `sizeof(char) == 1` and the ordering relations are the only size guarantees the standard gives.
  Every actual number is a fact about the platform — `long` is 4 bytes on 64-bit Windows and 8 on
  macOS and Linux, and `long double` is 8 bytes on arm64 macOS.
- `sizeof` returns `size_t`, an unsigned type. Print it with `%zu`, or cast it deliberately.
- Signed overflow is undefined behaviour, not a wrap: the compiler may assume it never happens and
  may delete your overflow check. Unsigned overflow wraps, and that is guaranteed.
- Floating-point values are approximations in binary. `0.1 + 0.2` is not `0.3`, and `==` is the wrong
  way to compare them. Work in integer units when the precision is fixed.
- Conversions between numeric types happen implicitly and may lose information; the compiler warns
  only about conversions it can see.
- A literal has a type: `'A'` is an `int`, `"A"` is a `char[2]`, `42` is an `int` and `42.0` is a
  `double`.
- Get the limits from `<limits.h>` and the exact widths from `<stdint.h>`. Never type either.

## Practice

- [ ] Run the size-printing program and write down all nine numbers. Which ones differ from the table
      in this chapter, and on which platform?
- [ ] Print `INT_MAX`, `INT_MIN`, `UINT_MAX` and `LLONG_MAX` by including `<limits.h>` and using the
      correct specifier for each. Do not type any of the numbers yourself.
- [ ] This loop never terminates. Work out why before you run it, then confirm it.
      `for (unsigned char c = 0; c <= 255; c++) { ... }`
- [ ] Add `0.1` to itself ten times in a `double` and print the sum with `%.17f`. Then compute
      `0.1 * 10` and print that. Explain why the two answers differ.
- [ ] Deliberately overflow a signed `int`, then run it under the sanitizer and paste the report. Now
      do the same with an `unsigned int` and note that the sanitizer says nothing.
- [ ] Choose a type for each of these and justify it in one sentence: the number of bytes in a file;
      the number of students in a class; a temperature in kelvin to two decimal places; a running
      total of money in cents that can exceed two billion.

## Solutions

:::solution Exercise 2
Ask the header, never the keyboard.

```c run
#include <stdio.h>
#include <limits.h>

int main(void) {
    printf("INT_MAX   %d\n", INT_MAX);
    printf("INT_MIN   %d\n", INT_MIN);
    printf("UINT_MAX  %u\n", UINT_MAX);
    printf("LLONG_MAX %lld\n", LLONG_MAX);
    return 0;
}
```

```text
INT_MAX   2147483647
INT_MIN   -2147483648
UINT_MAX  4294967295
LLONG_MAX 9223372036854775807
```

Note that `UINT_MAX` needs `%u` and `LLONG_MAX` needs `%lld` — a mismatch here is the `-Wformat`
warning from Chapter 2, and with `-Werror` it will not build at all. These four values are the same on
every mainstream 64-bit platform, but `LONG_MAX` is not, which is exactly why you print it rather than
memorise it.
:::

:::solution Exercise 3
Because `255 + 1` is not 256.

```c run
#include <stdio.h>

int main(void) {
    unsigned char c = 255;
    c++;
    printf("after 255 comes %d\n", (int)c);
    printf("so the bound c <= 255 is never false\n");
    return 0;
}
```

```text
after 255 comes 0
so the bound c <= 255 is never false
```

An `unsigned char` holds 0…255. Incrementing 255 wraps to 0, which is defined behaviour for unsigned
types — the same modulo arithmetic from the counter example, at eight bits instead of thirty-two. The
loop condition is checked *before* the increment, so when `c` is 255 the condition is true, then `c`
becomes 0 and the cycle repeats forever.

The subtlety is that `c <= 255` does not compare two `unsigned char` values. `c` is promoted to `int`
first, because C performs arithmetic at `int` width or wider, so the comparison is `255 <= 255` —
true. The promotion is what makes the bound look safe. If you want to iterate over every value of an
unsigned type, use a wider loop variable and cast at the point of use.
:::

:::solution Exercise 4
Ten additions are not one multiplication, because each addition rounds.

```c run
#include <stdio.h>

int main(void) {
    double sum = 0.0;
    for (int i = 0; i < 10; i++) {
        sum += 0.1;
    }

    printf("ten times 0.1 = %.17f\n", sum);
    printf("0.1 * 10      = %.17f\n", 0.1 * 10);
    printf("either equals 1.0? %d\n", (int)(sum == 1.0));
    return 0;
}
```

```text
ten times 0.1 = 0.99999999999999989
0.1 * 10      = 1.00000000000000000
either equals 1.0? 0
```

`0.1` is not representable in binary, so each stored value is a hair below one tenth. Adding ten of
those accumulates ten tiny errors in the same direction and lands at `0.99999999999999989` — one unit
in the last place away from 1.0, which is why `sum == 1.0` is false. The multiplication rounds once
and happens to land exactly on 1.0. Neither result is more "correct"; both are the nearest `double` to
the true answer of their own sequence of operations. The lesson is that `==` on floating-point values
asks a question about bit patterns, not about arithmetic.
:::

:::solution Exercise 5
The sanitizer catches the signed case and correctly ignores the unsigned one.

```c run-san-catch
#include <stdio.h>
#include <limits.h>

int main(void) {
    int value = INT_MAX;
    value = value + 1;
    printf("%d\n", value);
    return 0;
}
```

```text
runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

Change `int` to `unsigned int` and `INT_MAX` to `UINT_MAX` and the report disappears, because wrapping
is defined for unsigned types — the sanitizer is not being lenient, it is correctly reporting that
nothing undefined happened. This is the practical test for which kind of arithmetic you are doing: if
the sanitizer complains, the standard makes no promise about your result; if it stays quiet on an
unsigned wrap, the standard does.

Note that the build succeeded and the exit status was `0` in both cases. That is the trap recorded in
Chapter 1: UBSan *reports*, it does not fail the process, so a test suite that only checks exit codes
will not notice.
:::
