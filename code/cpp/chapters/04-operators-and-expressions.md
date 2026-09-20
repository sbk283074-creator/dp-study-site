---
chapter: 4
part: 1
title: Operators and Expressions
summary: Read an expression as a tree — know which operator binds tighter, what happens when two operators are equally tight, and which expressions have no defined answer at all.
minutes: 50
tags: [operators, precedence, associativity, bitwise, short-circuit, undefined behaviour]
---

An expression is not a sentence read left to right. It is a tree, and the operators' precedence and
associativity decide its shape before the compiler looks at anything else. Almost every operator bug
in real code comes from the same place: the tree in your head is not the tree the language builds.
`flags & MASK == 0` looks like "is the mask bit clear" and actually means "`flags` AND zero", which is
always zero. This chapter teaches you to see the tree, and then it teaches you the handful of
expressions where the tree is irrelevant because the language refuses to define an answer at all.

## Arithmetic: two division traps

Integer division truncates toward zero, and the remainder takes the sign of the dividend. That single
sentence is worth memorising, because the results look wrong until you know it.

```c run
#include <stdio.h>

int main(void) {
    printf(" 9 /  5 = %d,  9 %%  5 = %d\n", 9 / 5, 9 % 5);
    printf("-9 /  5 = %d, -9 %%  5 = %d\n", -9 / 5, -9 % 5);
    printf(" 9 / -5 = %d,  9 %% -5 = %d\n", 9 / -5, 9 % -5);
    return 0;
}
```

```text
 9 /  5 = 1,  9 %  5 = 4
-9 /  5 = -1, -9 %  5 = -4
 9 / -5 = -1,  9 % -5 = 4
```

Three things to take from that. Division discards the fraction rather than rounding, so `9 / 5` is
`1` and not `2`. Truncation is toward zero, so `-9 / 5` is `-1` — not `-2`, which is what rounding
down would give. And the remainder follows the dividend's sign, so `-9 % 5` is `-4`, which means
`a % b` is **not** a way to get a non-negative value. If you need one — for a hash table index, a
clock wrap, a colour channel — write it explicitly:

```c
int index = ((value % size) + size) % size;
```

The `%` operator also requires integers. This is a compile error, not a warning, because there is no
sensible way to define a remainder for real numbers:

```c bad
#include <stdio.h>

int main(void) {
    double half = 2.0;
    printf("%d\n", (int)(7 % half));
    return 0;
}
```

```text
error: invalid operands to binary expression ('int' and 'double')
```

For floating point you want `fmod` from `<math.h>`, and you should think about whether you want it at
all — a remainder is usually a sign that you are working in the wrong units.

## Precedence and associativity

Precedence decides which operator groups first; associativity decides how equal operators group.

```c run
#include <stdio.h>

int main(void) {
    printf("2 + 3 * 4   = %d\n", 2 + 3 * 4);
    printf("(2 + 3) * 4 = %d\n", (2 + 3) * 4);
    printf("10 - 3 - 2  = %d\n", 10 - 3 - 2);
    printf("10 / 4 * 4  = %d\n", 10 / 4 * 4);
    printf("2 * 3 %% 4   = %d\n", 2 * 3 % 4);
    return 0;
}
```

```text
2 + 3 * 4   = 14
(2 + 3) * 4 = 20
10 - 3 - 2  = 5
10 / 4 * 4  = 8
2 * 3 % 4   = 2
```

The fourth line is the interesting one. `*` and `/` have the same precedence and associate left to
right, so `10 / 4 * 4` is `(10 / 4) * 4`, which is `2 * 4` — and `2` is what integer division gave
you. The result is `8`, not `10`. Left-to-right associativity is doing something visible here, and
`-` behaves the same way: `10 - 3 - 2` is `5`, not `9`.

You do not need the whole precedence table in your head. You need the four groups that actually
catch people, and you need to know that when in doubt you write parentheses:

| Binds tightest | Operators |
|---|---|
| 1 | `()` `[]` `.` `->` — postfix `++` `--` |
| 2 | unary `!` `~` `+` `-` `*` `&` prefix `++` `--` |
| 3 | `*` `/` `%` |
| 4 | `+` `-` |
| 5 | `<<` `>>` |
| 6 | `<` `<=` `>` `>=` |
| 7 | `==` `!=` |
| 8 | `&` then `^` then `\|` |
| 9 | `&&` then `\|\|` |
| 10 | `?:` |
| 11 | `=` `+=` `-=` … |
| loosest | `,` |

Read rows 5 to 8 slowly, because that is where the damage is. **Shifts bind looser than arithmetic,
and bitwise operators bind looser than comparisons.** Both facts are counter-intuitive, and both
produce code that compiles and is silently wrong.

```c warn
#include <stdio.h>

#define MASK 1

int main(void) {
    int flags = 1;

    if (flags & MASK == 0) {
        printf("no flag\n");
    } else {
        printf("flag set\n");
    }
    return 0;
}
```

```text
& has lower precedence than ==; == will be evaluated first [-Wparentheses]
```

The condition is `flags & (MASK == 0)`, which is `flags & 0`, which is always `0`. The branch that
runs is the `else`, and it runs for every possible value of `flags`. The fix is one pair of
parentheses: `(flags & MASK) == 0`. The compiler tells you, and `-Werror` makes it stop the build —
which is the only reason this bug does not reach production in a codebase that has the flag on.

## Increment and decrement

`i++` yields the old value and then increments; `++i` increments and then yields the new value. When
the result is discarded, they are identical — and in a `for` loop's third clause that is always true,
so `i++` and `++i` are interchangeable there.

```c run
#include <stdio.h>

int main(void) {
    int x = 5;
    int y = 5;

    int from_post = x++;
    int from_pre = ++y;

    printf("from_post = %d, x = %d\n", from_post, x);
    printf("from_pre  = %d, y = %d\n", from_pre, y);
    return 0;
}
```

```text
from_post = 5, x = 6
from_pre  = 6, y = 6
```

The difference only matters when the value is used, which is exactly when it is worth pausing over.
Two side effects in one expression is where this stops being a style question and becomes undefined
behaviour.

## Short-circuit evaluation

`&&` and `||` are **guaranteed** to stop as soon as the answer is known. This is not an optimisation
you may rely on by accident — it is a rule of the language, and it is why `if (p != NULL && p->value)`
is safe.

```c run
#include <stdio.h>

static int calls = 0;

static int positive(int value) {
    calls++;
    return value > 0;
}

int main(void) {
    int zero = 0;

    calls = 0;
    if (zero != 0 && positive(zero)) {
        printf("branch A taken\n");
    }
    printf("after &&: %d call(s)\n", calls);

    calls = 0;
    if (zero != 0 || positive(zero)) {
        printf("branch B taken\n");
    }
    printf("after ||: %d call(s)\n", calls);

    return 0;
}
```

```text
after &&: 0 call(s)
after ||: 1 call(s)
```

With `&&`, the left side was false, so the right side was never evaluated and `positive` was never
called. With `||`, the left side was false, so the right side *had* to be evaluated to know the
answer — and it ran once. Neither branch was taken, because both conditions turned out false. This is
the mechanism that makes the null-pointer guard idiom work, and it is also the reason you must never
put a needed side effect on the right of an `&&`: it may simply not happen.

## Bitwise operators are not logical operators

`&`, `|` and `^` operate on every bit independently. `&&`, `||` and `!` treat their operands as
"zero or non-zero" and produce `0` or `1`. They are different operators for different jobs.

```c run
#include <stdio.h>

int main(void) {
    unsigned int a = 0xCu;
    unsigned int b = 0xAu;

    printf("a & b  = %u\n", a & b);
    printf("a | b  = %u\n", a | b);
    printf("a ^ b  = %u\n", a ^ b);
    printf("~a     = %u\n", ~a & 0xFu);
    printf("a && b = %d\n", (int)(a && b));
    return 0;
}
```

```text
a & b  = 8
a | b  = 14
a ^ b  = 6
~a     = 3
a && b = 1
```

`0xC` is `1100` and `0xA` is `1010` in binary, so the AND keeps the shared bit, the OR keeps both,
and the XOR keeps the bits that differ. The `& 0xFu` on the `~` line masks the result back down to
four bits, because `~a` flips all thirty-two bits of the `unsigned int` and the interesting ones are
the low four.

Bitwise operators are how you pack several yes/no facts into one integer — file permissions, hardware
registers, feature flags. The idiom is `(flags & MASK) == MASK` for "is this flag set", and the
parentheses are not optional, as the warning above showed.

## Shifts: three ways to get undefined behaviour

`x << n` shifts left by `n` places. It is defined when `n` is less than the width of the type and the
result is representable; otherwise it is undefined behaviour, and the sanitizer will tell you.

```c run-san-catch
#include <stdio.h>

int main(void) {
    int one = 1;
    int shift = 31;

    printf("%d\n", one << shift);
    return 0;
}
```

```text
runtime error: left shift of 1 by 31 places cannot be represented in type 'int'
```

Shifting a `1` into the sign bit of a signed `int` is not a clever way to write `INT_MIN`. It is
undefined. Note again that the build succeeded, the program ran, and it printed `-2147483648` — a
plausible number. Only the sanitizer knew.

The second way is a shift count that is too large. Here the shift amount is a variable, so the
compiler cannot check it and says nothing at all:

```c run-san-catch
#include <stdio.h>

int main(void) {
    unsigned int value = 1u;
    int shift = 32;

    printf("%u\n", value << shift);
    return 0;
}
```

```text
runtime error: shift exponent 32 is too large for 32-bit type 'unsigned int'
```

A `1u` shifted by 32 on a 32-bit type is undefined, and it printed `1` — which is the *wrong* answer
for anyone expecting zero. The third way is a negative shift count, which is undefined for the same
reason. The safe habit is to keep shift counts unsigned and assert that they are in range, or to use
a `uint64_t` when you genuinely need bit 32 or above.

:::pitfall Using = where you meant ==
An assignment is an expression with a value, so it can go anywhere a value can — including inside an
`if`. `if (x = 5)` assigns 5 to `x` and then tests `5`, which is true, so the branch always runs. The
variable is silently corrupted as a side effect.

```c warn
#include <stdio.h>

int main(void) {
    int remaining = 3;

    if (remaining = 0) {
        printf("still have work\n");
    } else {
        printf("done\n");
    }
    printf("remaining is now %d\n", remaining);
    return 0;
}
```

```text
using the result of an assignment as a condition without parentheses [-Wparentheses]
```

The program prints `done`, and it prints it for every value you could have put in `remaining`, because
the assignment overwrote it with `0` first. The compiler spots the pattern and says so, and `-Werror`
refuses the build. If the assignment really is intended — `while ((c = getchar()) != EOF)` is the
standard idiom — you say so with the extra parentheses, and the warning goes away because you have
demonstrated that you meant it.
:::

## Evaluation order is not left to right

Precedence tells you how the tree is shaped. It does **not** tell you the order the branches are
evaluated in. C leaves that unspecified for most operators, and when two unsequenced operations
modify the same variable, the behaviour is undefined:

```c warn
#include <stdio.h>

int main(void) {
    int i = 1;
    int j = i++ + i++;

    printf("i = %d, j = %d\n", i, j);
    return 0;
}
```

```text
multiple unsequenced modifications to 'i' [-Wunsequenced]
```

There is no correct answer to "what is `j`" — the standard permits several, and the compiler is free
to pick differently on a Tuesday. The compiler warns, which is the only reliable defence. The rule
that keeps you safe is mechanical: **one side effect per variable per expression.** If you want to
increment `i` twice, do it on two lines.

:::scenario The permission check that let the wrong people in
A request handler gates an admin action on a bitmask. The original line was
`if (user->flags & PERM_ADMIN != 0) { allow(); }`. Because `!=` binds tighter than `&`, the condition
is really `user->flags & (PERM_ADMIN != 0)` — that is, `user->flags & 1`. `PERM_ADMIN` happens to be
bit 2, so the test has nothing to do with admin at all; it tests bit 0, which is `PERM_READ`, and
every user who can read anything gets admin access.

:::solution Name the test, and let the compiler enforce the parentheses
The fix is not "add parentheses and remember next time". Parentheses are easy to forget and there is
no signal when you do. Wrap the test in a function whose name states the question, so the operator
precedence lives in exactly one place that you have already verified:

```c run
#include <stdio.h>
#include <stdbool.h>

#define PERM_READ  (1u << 0)
#define PERM_WRITE (1u << 1)
#define PERM_ADMIN (1u << 2)

static bool has_permission(unsigned int flags, unsigned int permission) {
    return (flags & permission) == permission;
}

int main(void) {
    unsigned int user = PERM_READ | PERM_WRITE;

    printf("read?  %d\n", (int)has_permission(user, PERM_READ));
    printf("admin? %d\n", (int)has_permission(user, PERM_ADMIN));

    user |= PERM_ADMIN;
    printf("after grant, admin? %d\n", (int)has_permission(user, PERM_ADMIN));
    return 0;
}
```

```text
read?  1
admin? 0
after grant, admin? 1
```

Three things are doing work here. The parentheses are inside one function, so there is one place to
get right instead of a dozen. `(flags & permission) == permission` tests that *all* the bits in the
mask are present, which is what "has this permission" means — `!= 0` would be the wrong test the
moment a permission is defined as more than one bit. And the caller now reads as a question rather
than as bit arithmetic, so the next person to touch it cannot mis-parse it.

The second half of the fix is the compiler flag. `-Wparentheses` catches the original mistake, and
`-Werror` turns it into a build failure. A permission bug that reaches production is not a
precedence problem; it is a missing `-Werror`.
:::

## Key takeaways

- Integer division truncates toward zero and the remainder takes the dividend's sign, so `-9 % 5` is
  `-4` and `a % b` is not guaranteed non-negative.
- `%` requires integers; for floating point you need `fmod`, and usually you want different units
  instead.
- `*` `/` `%` share a precedence level and associate left to right, which is why `10 / 4 * 4` is `8`.
- Shifts bind looser than `+` and `-`, and bitwise `&` `^` `|` bind looser than `==`. Both are
  counter-intuitive and both are caught by `-Wparentheses` or `-Wshift-op-parentheses`.
- `i++` yields the old value, `++i` the new one; the difference is invisible where the value is
  discarded.
- `&&` and `||` are guaranteed to short-circuit, which is what makes null checks safe and what makes
  side effects on the right-hand side unreliable.
- `&` `|` `^` `~` work bit by bit; `&&` `||` `!` work on truth values. They are not interchangeable.
- Shifting into the sign bit, shifting by a count at least the width of the type, and shifting by a
  negative count are all undefined behaviour. UBSan reports them without failing the process.
- `if (x = 5)` assigns and then tests, and always takes the true branch. Use `==`, or double
  parentheses if the assignment is deliberate.
- Two unsequenced modifications to the same variable in one expression have no defined result.

## Practice

- [ ] Write an expression that computes `-7 / 2` and `-7 % 2`, print both, and check them against the
      truncation-toward-zero rule.
- [ ] Rewrite `a % b` so the result is always in `[0, b)` for any `a`, including negative `a`, and
      test it with `a = -1`, `b = 5`.
- [ ] Add the missing parentheses to `flags & MASK == 0` and confirm the program prints the branch you
      expect. Then explain in one sentence what the original expression computed.
- [ ] Predict the output of each of these before running them: `1 << 4`, `~0u >> 4`, `7 & 3`,
      `7 | 3`, `7 ^ 3`. Then check.
- [ ] Write a `while` loop that reads characters with `getchar()` and stops at `EOF`, using the
      assignment-in-condition idiom with the extra parentheses. Compile with `-Wall -Wextra -Werror`
      and confirm it is accepted.
- [ ] Take the short-circuit program and change `&&` to `&`. Predict what `calls` will be, then run
      it. Explain the difference in terms of what each operator promises.

## Solutions

:::solution Exercise 2
Add the modulus, take the modulus again.

```c run
#include <stdio.h>

static int positive_mod(int a, int b) {
    return ((a % b) + b) % b;
}

int main(void) {
    int cases[4][2] = {{7, 5}, {-7, 5}, {-1, 5}, {-11, 5}};

    for (int i = 0; i < 4; i++) {
        int a = cases[i][0];
        int b = cases[i][1];
        printf("positive_mod(%3d, %d) = %d\n", a, b, positive_mod(a, b));
    }
    return 0;
}
```

```text
positive_mod(  7, 5) = 2
positive_mod( -7, 5) = 3
positive_mod( -1, 5) = 4
positive_mod(-11, 5) = 4
```

`a % b` is in `(-b, b)`, so adding `b` makes it positive, and the outer `% b` brings it back into
range when the inner value was already positive and the addition pushed it to `b` or beyond. Note
that `-7 % 5` is `-2`, and `-2 + 5` is `3` — which is `-7` mod `5` in the mathematical sense. This is
the version you want for array indices and for wrapping angles into a range.
:::

:::solution Exercise 4
Predict, then check.

```c run
#include <stdio.h>

int main(void) {
    printf("1 << 4   = %d\n", 1 << 4);
    printf("~0u >> 4 = %u\n", ~0u >> 4);
    printf("7 & 3    = %d\n", 7 & 3);
    printf("7 | 3    = %d\n", 7 | 3);
    printf("7 ^ 3    = %d\n", 7 ^ 3);
    return 0;
}
```

```text
1 << 4   = 16
~0u >> 4 = 268435455
7 & 3    = 3
7 | 3    = 7
7 ^ 3    = 4
```

`1 << 4` is sixteen, the obvious case. `~0u` is all thirty-two bits set, and shifting right by four
clears the top four, leaving `0x0FFFFFFF` — 268435455. This is the standard way to build a mask of a
given width. For the last three, `7` is `111` and `3` is `011`: AND keeps `011` (3), OR keeps `111`
(7), and XOR keeps the bits that differ (100, which is 4). Note that `~0u >> 4` uses an *unsigned*
zero: with a signed `0`, `~0` is `-1` and right-shifting a negative value is implementation-defined,
which is another of the traps this chapter is about.
:::

:::solution Exercise 6
`&` does not short-circuit, so the call happens.

```c run
#include <stdio.h>

static int calls = 0;

static int positive(int value) {
    calls++;
    return value > 0;
}

int main(void) {
    int zero = 0;

    calls = 0;
    if ((zero != 0) & positive(zero)) {
        printf("branch taken\n");
    }
    printf("with &: %d call(s)\n", calls);

    calls = 0;
    if (zero != 0 && positive(zero)) {
        printf("branch taken\n");
    }
    printf("with &&: %d call(s)\n", calls);

    return 0;
}
```

```text
with &: 1 call(s)
with &&: 0 call(s)
```

`&` is a bitwise operator: it must have both operands before it can compute anything, so it evaluates
both sides unconditionally. `&&` is a logical operator: once the left side is false the answer is
known, and the standard requires it to stop. That is why `&&` protects a dereference and `&` does
not. The two lines also happen to produce the same branch here, because `1 & 0` and `1 && 0` are both
falsy — but the *side effect* differs, and that is the whole lesson.

Note the parentheses around `zero != 0`. Without them this line does not compile: `&` binds looser
than `!=`, so the compiler sees `zero != (0 & positive(zero))` and refuses with
`& has lower precedence than !=; != will be evaluated first [-Wparentheses]`. That the compiler
forces you to write the parentheses is itself a hint — mixing a bitwise operator with a comparison is
almost never what you meant, and the one place it is deliberate should be spelled out.
:::
