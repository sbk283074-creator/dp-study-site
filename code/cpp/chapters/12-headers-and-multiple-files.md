---
chapter: 12
part: 2
title: Headers and Multiple Files
summary: Split a program across several files, declare in headers and define in sources, guard against double inclusion, control what other files can see, and let make do the rebuilding.
minutes: 60
tags: [header, include-guard, static, extern, linkage, make, preprocessor, macro]
---

Every program in this book has been one file, and that stops working somewhere around a thousand
lines. The reason is not tidiness — it is that a single file must be recompiled in full for every
change, and that everything in it can see everything else. Splitting a program fixes both: each `.c`
file is compiled on its own into an object file, and only the ones that changed are rebuilt. The cost
is a new set of rules about what a *declaration* is versus a *definition*, and those rules are where
multi-file C projects go wrong. The compiler and the linker enforce them for you, which is why this
chapter's examples are mostly failures — the interesting ones.

## Declaration versus definition

A **declaration** says a name exists and what its type is. A **definition** creates it. For a function
the difference is the body:

```c
int twice(int value);              /* declaration: a promise */
int twice(int value) { return value * 2; }   /* definition: the promise kept */
```

A program may declare the same function as many times as it likes, in as many files as it likes, but it
must define it **exactly once** in the whole program. That is the one-definition rule, and it is what
makes headers possible: a header holds declarations, so every `.c` file that includes it learns the
function's signature without defining anything.

A variable declaration is subtler, because `int counter;` at file scope is a *definition* — it creates
the variable and allocates space. To declare a variable without defining it you need `extern`, and the
pattern that makes it useful is a header that says the name exists plus one source file that creates it:

```c run-files
/* ===== state.h ===== */
#ifndef STATE_H
#define STATE_H

extern int request_count;

void record_request(void);

#endif

/* ===== state.c ===== */
#include "state.h"

int request_count = 0;

void record_request(void) {
    request_count++;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "state.h"

int main(void) {
    record_request();
    record_request();
    record_request();

    printf("requests = %d\n", request_count);
    return 0;
}
```

```text
requests = 3
```

`extern int request_count;` appears in the header and in every file that includes it, and it defines
nothing — it is a promise that a variable of that name and type exists somewhere. The promise is kept
exactly once, by `int request_count = 0;` in `state.c`. Remove the `extern` and the header would define
the variable in every including file, giving the same `duplicate symbol` you are about to meet. This is
the mechanism behind every C library that keeps a global counter, cache or configuration block, and it
is also the mechanism most responsible for the phrase "global state is a bug" — a variable that any of
twenty files can change is a variable whose value you cannot reason about from any one of them.

## The three-file program

Here is the shape everything else in this chapter is a variation on. `point.h` declares, `point.c`
defines, `main.c` uses.

```c run-files
/* ===== point.h ===== */
#ifndef POINT_H
#define POINT_H

typedef struct {
    int x;
    int y;
} Point;

Point point_add(Point a, Point b);

#endif

/* ===== point.c ===== */
#include "point.h"

Point point_add(Point a, Point b) {
    Point result = {a.x + b.x, a.y + b.y};
    return result;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "point.h"

int main(void) {
    Point a = {1, 2};
    Point b = {10, 20};
    Point sum = point_add(a, b);

    printf("sum = (%d, %d)\n", sum.x, sum.y);
    return 0;
}
```

```text
sum = (11, 22)
```

Three files, one program. `main.c` can call `point_add` because it has seen the declaration in
`point.h`; it does not know or care that the definition is somewhere else. That separation is the whole
point of the arrangement — you could rewrite `point.c` completely, keeping the same signatures, and
`main.c` would not need to change a character.

:::note How multi-file listings are written in this book
The `/* ===== point.h ===== */` lines are **listing separators**, not part of any file. Each one names
the file that follows it, so a single code block can show a whole project in the order you would read
it. When you type the example out, the separator line is the file name you save under, and nothing else.

This matters most for the Makefile examples later in the chapter, where the banner looks like a comment
but is not one — a Makefile has its own comment syntax (`#`), and pasting a `/* ... */` line into one
would be a syntax error.
:::

The `#ifndef POINT_H` at the top is an **include guard**, and it is not optional. Headers get included
more than once in a real project — `main.c` includes `config.h`, `config.h` includes `limits.h`, and
something else includes `limits.h` too. Without a guard, the second inclusion re-processes the file:

```c bad-files
/* ===== config.h ===== */
int max_connections = 100;

/* ===== main.c ===== */
#include "config.h"
#include "config.h"

int main(void) {
    return max_connections - 100;
}
```

```text
error: redefinition of 'max_connections'
```

The guard works by defining a macro the first time the file is read, so the second read skips everything
between `#ifndef` and `#endif`:

```c
#ifndef POINT_H
#define POINT_H
/* ... contents, processed once ... */
#endif
```

The macro name is conventionally the file name in capitals with the dots turned into underscores —
`POINT_H` for `point.h`, `NET_HTTP_CLIENT_H` for `net/http_client.h`. It has to be unique across the
whole project, because the preprocessor has one flat namespace. Some compilers accept `#pragma once`
instead, which is shorter and does the same thing by file identity; it is not in the C standard, but
every compiler you will meet supports it. This book uses guards, because they are portable and because
seeing the mechanism is worth more than saving three lines.

## What belongs in a header

The rule is one sentence: **a header declares, a source file defines.** So a header holds function
prototypes, `typedef`s, `struct` and `enum` definitions, macro constants, and `extern` variable
declarations. It must not hold function bodies or variable definitions, because it will be included by
more than one file and every inclusion would be another definition.

There is a genuine exception worth knowing. A `struct` *definition* is fine in a header — it is a type,
not an object, so including it twice in one file is harmless once the guard is in place, and including
it in ten files creates ten types with one name, which is what you want.

`static` is how you make a function or variable private to its file. Two translation units can each have
their own `static` helper with the same name, and the linker never sees a conflict:

```c run-files
/* ===== counters.h ===== */
#ifndef COUNTERS_H
#define COUNTERS_H

void bump_a(void);
void bump_b(void);
int get_a(void);
int get_b(void);

#endif

/* ===== counter_a.c ===== */
#include "counters.h"

static int total = 0;

void bump_a(void) {
    total += 1;
}

int get_a(void) {
    return total;
}

/* ===== counter_b.c ===== */
#include "counters.h"

static int total = 0;

void bump_b(void) {
    total += 10;
}

int get_b(void) {
    return total;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "counters.h"

int main(void) {
    bump_a();
    bump_a();
    bump_b();

    printf("a = %d, b = %d\n", get_a(), get_b());
    return 0;
}
```

```text
a = 2, b = 10
```

Two variables named `total`, in two files, with no conflict — because `static` at file scope means
*internal linkage*: the name is not exported and cannot be seen from another translation unit. Each file
has its own. Drop the `static` and the same program does not link:

```c bad-files
/* ===== counters.h ===== */
void bump_a(void);
void bump_b(void);
int get_a(void);
int get_b(void);

/* ===== counter_a.c ===== */
#include "counters.h"

int total = 0;

void bump_a(void) {
    total += 1;
}

int get_a(void) {
    return total;
}

/* ===== counter_b.c ===== */
#include "counters.h"

int total = 0;

void bump_b(void) {
    total += 10;
}

int get_b(void) {
    return total;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "counters.h"

int main(void) {
    bump_a();
    bump_b();
    printf("a = %d, b = %d\n", get_a(), get_b());
    return 0;
}
```

```text
duplicate symbol
```

That message comes from the **linker**, not the compiler, and the distinction matters when you are
reading a build log. Each `.c` file compiles cleanly on its own — the compiler has no way to know that
another object file defines the same name. It is only when the linker tries to assemble one program out
of all the object files that the collision appears. When you see a linker error rather than a compiler
error, the fix is almost always in the declarations and definitions across files, not inside any one
function.

## Compiling and linking

Building the three-file program is two steps per source file, then one link:

```bash
clang -std=c17 -Wall -Wextra -Werror -c point.c    # produces point.o
clang -std=c17 -Wall -Wextra -Werror -c main.c     # produces main.o
clang -std=c17 -Wall -Wextra -Werror -o prog main.o point.o
```

`-c` means "compile to an object file, do not link". The link step has no `-c` and names every object
file. Once `point.o` exists, editing `main.c` only needs `main.o` rebuilt — the compile step for
`point.c` is skipped, which is the whole benefit and the reason a large C project can rebuild in seconds
where a single-file program of the same size would take minutes.

Doing that by hand is fine for three files and hopeless for three hundred, which is what `make` is for.
A Makefile states each output, its inputs, and the command that turns one into the other:

```c make-files
/* ===== point.h ===== */
#ifndef POINT_H
#define POINT_H

typedef struct {
    int x;
    int y;
} Point;

Point point_add(Point a, Point b);
int point_dot(Point a, Point b);

#endif

/* ===== point.c ===== */
#include "point.h"

Point point_add(Point a, Point b) {
    Point result = {a.x + b.x, a.y + b.y};
    return result;
}

int point_dot(Point a, Point b) {
    return a.x * b.x + a.y * b.y;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "point.h"

int main(void) {
    Point a = {1, 2};
    Point b = {3, 4};
    Point sum = point_add(a, b);

    printf("sum = (%d, %d), dot = %d\n", sum.x, sum.y, point_dot(a, b));
    return 0;
}

/* ===== Makefile ===== */
CC = clang
CFLAGS = -std=c17 -Wall -Wextra -Werror

prog: main.o point.o
	$(CC) $(CFLAGS) -o prog main.o point.o

main.o: main.c point.h
	$(CC) $(CFLAGS) -c main.c

point.o: point.c point.h
	$(CC) $(CFLAGS) -c point.c

clean:
	rm -f prog main.o point.o
```

```text
sum = (4, 6), dot = 11
```

Three things about that Makefile are load-bearing. The indentation on the recipe lines is a **tab**, not
spaces — make is old enough to care, and a spaces-indented recipe produces
`missing separator. Stop.` rather than a build. `$(CC)` and `$(CFLAGS)` are make variables, not shell
ones, expanded by make before the command runs. And `main.o: main.c point.h` lists the header as a
dependency, so editing `point.h` rebuilds both object files — a rule that omits headers is the classic
Makefile bug, and it produces builds that are silently stale.

This book's verification harness runs `make` in the listing above and then runs the `prog` it produced,
so the recipe is checked rather than trusted. A Makefile that forgets to link `point.o` fails the check
with the linker's own message, which is exactly the failure you would hit.

## The preprocessor

Everything starting with `#` is handled before the compiler sees the code, by a program that knows
nothing about C types. `#include` pastes a file in. `#define` does text substitution:

```c run
#include <stdio.h>

#define SQUARE(x) x * x

int main(void) {
    printf("SQUARE(1 + 2) = %d\n", SQUARE(1 + 2));
    return 0;
}
```

```text
SQUARE(1 + 2) = 5
```

`SQUARE(1 + 2)` expands to `1 + 2 * 1 + 2`, and multiplication binds tighter than addition, so the
answer is `1 + 2 + 2` — five, not nine. The fix is to parenthesise both the parameter and the whole
expansion, so the result is correct whatever the argument looks like:

```c
#define SQUARE(x) ((x) * (x))
```

That fixes precedence. It does not fix the second problem, which is that the macro expands its argument
as many times as the argument appears:

```c run
#include <stdio.h>

#define SQUARE(x) ((x) * (x))

static int calls = 0;

static int next_value(void) {
    calls++;
    return 3;
}

int main(void) {
    int result = SQUARE(next_value());

    printf("result = %d, calls = %d\n", result, calls);
    return 0;
}
```

```text
result = 9, calls = 2
```

One call in the source, two calls at runtime. `next_value()` was substituted into both slots, so it ran
twice. This is why macros with side-effecting arguments are dangerous in a way that functions never are:
a function evaluates its argument once, before the call, and no amount of rewriting the function can
change that. The version with `i++` instead of a function call is worse still — it is undefined
behaviour, and the compiler catches it with
`multiple unsequenced modifications to 'i' [-Wunsequenced]`, which is one of the few macro bugs you get
for free.

A macro redefined is a warning rather than an error, which is worth knowing because it usually means two
headers disagree:

```c warn-files
/* ===== main.c ===== */
#include <stdio.h>

#define LIMIT 10
#define LIMIT 20

int main(void) {
    printf("%d\n", LIMIT);
    return 0;
}
```

```text
'LIMIT' macro redefined
```

For constants, `#define` is the wrong tool when a real declaration will do. A macro has no type, cannot
be seen by the debugger, cannot be scoped, and takes over the name everywhere in the file. A
`static const int max_connections = 100;` in a header gives you a typed object with a name you can look
up.

The `static` is doing real work there, and leaving it off is a trap — see the pitfall below.

`#ifdef` is the other half of the preprocessor's job: compiling different code from the same source,
which is how debug logging and platform differences are handled.

```c run
#include <stdio.h>

#define DEBUG 1

int main(void) {
#ifdef DEBUG
    printf("debug build\n");
#else
    printf("release build\n");
#endif
    return 0;
}
```

```text
debug build
```

In real code the macro comes from the build system rather than the source — `make CFLAGS=-DDEBUG` or
`clang -DDEBUG` defines it on the command line, so the same files produce a debug build or a release
build without being edited. `#ifndef` around a whole file is the same mechanism, which is why include
guards are not a special feature: they are just conditional compilation, used carefully.

:::scenario The helper that was defined in the header
A developer needs a small `clamp` function in two places. Putting it in the header is the obvious move,
and it works — for a while:

```c bad-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

int clamp(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

#endif

/* ===== reader.c ===== */
#include "util.h"

int read_level(void) {
    return clamp(500, 0, 100);
}

/* ===== writer.c ===== */
#include "util.h"

int write_level(int level) {
    return clamp(level, 0, 100);
}

/* ===== main.c ===== */
#include <stdio.h>
#include "util.h"

int read_level(void);
int write_level(int level);

int main(void) {
    printf("%d %d\n", read_level(), write_level(42));
    return 0;
}
```

```text
duplicate symbol
```

The header is guarded, so each file includes it once and there is no compiler error at all — four
translation units, four clean compilations. The problem is at the link step: `reader.c`, `writer.c` and
`main.c` each got a full copy of `clamp`, so the program defines it three times. The one-definition rule
was violated by a file that looks perfectly well written, and the include guard — which everyone reaches
for first — cannot help, because the guard only stops the file being processed twice *within one
translation unit*.

This is the mistake that makes the "declaration versus definition" rule worth learning rather than
memorising. The header is not a place to put code; it is a place to put the *shape* of code.

:::solution Declare in the header, define in one source file
Move the body into a `.c` file and leave only the prototype behind:

```c run-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

int clamp(int value, int low, int high);

#endif

/* ===== util.c ===== */
#include "util.h"

int clamp(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

/* ===== reader.c ===== */
#include "util.h"

int read_level(void) {
    return clamp(500, 0, 100);
}

/* ===== writer.c ===== */
#include "util.h"

int write_level(int level) {
    return clamp(level, 0, 100);
}

/* ===== main.c ===== */
#include <stdio.h>
#include "util.h"

int read_level(void);
int write_level(int level);

int main(void) {
    printf("%d %d\n", read_level(), write_level(42));
    return 0;
}
```

```text
100 42
```

Now `clamp` is defined once in `util.c` and declared three times, which is exactly what the
one-definition rule permits. Every other file still compiles without seeing the body, so changing the
implementation of `clamp` recompiles one file instead of three — the build-time benefit that made
splitting the program worthwhile in the first place.

There is a legitimate reason to want code in a header, and the language has a name for it: `static
inline` on the function, which gives each translation unit its own copy and tells the compiler to
inline it. That is what C++ does automatically for functions defined in a class body, and it is the
mechanism behind header-only libraries. The plain non-`static` version above has neither the type
safety of one definition nor the intent of the other.
:::

:::pitfall a const in a header is not the same as a macro
`static const int` in a header works. Plain `const int` in a header included by two files does not, and
the error arrives at link time with no compiler warning beforehand:

```c bad-files
/* ===== limits.h ===== */
#ifndef LIMITS_H
#define LIMITS_H

const int max_connections = 100;

#endif

/* ===== report.c ===== */
#include "limits.h"

int report_limit(void) {
    return max_connections;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "limits.h"

int report_limit(void);

int main(void) {
    printf("%d\n", report_limit());
    return 0;
}
```

```text
duplicate symbol
```

The reason is that in C, `const` on a file-scope variable does **not** give it internal linkage — unlike
C++, where it does. `const int max_connections = 100;` in a header is a definition with external linkage,
so every translation unit that includes the header defines it, and the linker sees the collision. In C++
the identical code compiles and links, which is why this trap is so easy to carry across from one
language to the other.

Three ways out, in order of preference. Use `#define MAX_CONNECTIONS 100` and accept that it is untyped
— fine for an integer constant, and the conventional choice. Use `static const int` and accept that each
translation unit gets its own copy — fine for a small value, wasteful for a large table, and it silently
defeats any address comparison. Or declare it `extern` in the header and define it once in a `.c` file,
which is the correct answer when the object is large or must have one identity. What you must not do is
write `const int` in a header and expect it to work because it does in C++.
:::

## Key takeaways

- A declaration says a name exists; a definition creates it. A function may be declared many times but
  defined exactly once in the whole program — the one-definition rule.
- A header holds declarations: prototypes, `typedef`s, `struct`/`enum` definitions, macro constants and
  `extern` variable declarations. It must not hold function bodies or variable definitions.
- Every header needs an include guard: `#ifndef NAME_H` / `#define NAME_H` / `#endif`, with a name unique
  across the project. `#pragma once` works on every real compiler but is not standard.
- `static` at file scope gives internal linkage. Two files may each have their own `static` helper of the
  same name; without `static` the linker reports `duplicate symbol`.
- A `duplicate symbol` error comes from the linker, so every file compiled cleanly. Look at what is
  defined in more than one place, not inside any one function.
- `-c` compiles to an object file without linking. The link step names every object file and has no `-c`.
- A Makefile recipe line must be indented with a **tab**. List every header a source file depends on, or
  the build will be silently stale.
- `#define` is text substitution with no types and no scoping. Parenthesise both the parameter and the
  whole expansion: `#define SQUARE(x) ((x) * (x))`.
- A macro expands its argument once per appearance in the body, so a side-effecting argument runs more
  than once. A function evaluates its argument exactly once.
- Redefining a macro is a warning (`'LIMIT' macro redefined`), not an error, and usually means two
  headers disagree.
- In C, `const` at file scope does **not** imply internal linkage. `const int` in a header included twice
  is a `duplicate symbol`; use `#define`, `static const`, or `extern` plus one definition. C++ differs.
- `#ifdef` / `#ifndef` compile different code from the same source. Include guards are just this
  mechanism, and `-DDEBUG` on the command line is how the build system sets it.

## Practice

- [ ] Split a program into `math_utils.h`, `math_utils.c` and `main.c`. The header declares `int
      gcd(int a, int b);` and `int lcm(int a, int b);`, the source defines them, and `main` prints
      `gcd(48, 18)` and `lcm(4, 6)`.
- [ ] Take the program above and remove the include guard from the header. Add a second header that also
      includes it, and have `main.c` include both. Confirm the error, then put the guard back and confirm
      it goes away.
- [ ] Write a header holding `static const double PI = 3.14159265358979;` and include it from two
      translation units. Confirm it links, then change `static const` to plain `const` and explain the
      new error in one sentence.
- [ ] Write `#define MAX(a, b) a > b ? a : b`, then work out `2 * MAX(3, 4)` by hand before running it.
      Fix the macro and confirm the answer changes.
- [ ] Write a Makefile for a three-file program with a `clean` target, then deliberately change a header
      and confirm that `make` rebuilds the object files that depend on it.
- [ ] Write a `static` helper function in two translation units with the same name and different
      behaviour, call both from `main`, and confirm there is no link error. Then remove `static` and read
      the linker's message.

## Solutions

:::solution Exercise 1
Declare both functions in the header, define both in the source, and let the Makefile-free link do the
rest.

```c run-files
/* ===== math_utils.h ===== */
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int gcd(int a, int b);
int lcm(int a, int b);

#endif

/* ===== math_utils.c ===== */
#include "math_utils.h"

int gcd(int a, int b) {
    while (b != 0) {
        int remainder = a % b;
        a = b;
        b = remainder;
    }
    return a < 0 ? -a : a;
}

int lcm(int a, int b) {
    int divisor = gcd(a, b);

    if (divisor == 0) {
        return 0;
    }
    return (a / divisor) * b;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "math_utils.h"

int main(void) {
    printf("gcd(48, 18) = %d\n", gcd(48, 18));
    printf("lcm(4, 6) = %d\n", lcm(4, 6));
    return 0;
}
```

```text
gcd(48, 18) = 6
lcm(4, 6) = 12
```

Euclid's algorithm is the loop: replace `(a, b)` with `(b, a % b)` until `b` is zero, and the answer is
what is left in `a`. It terminates because the remainder is strictly smaller than `b`. The header guard
is `MATH_UTILS_H`, derived from the file name — not `MATH_H`, which would collide with a header of that
name in any larger project. Note that `lcm` divides *before* multiplying: `(a / divisor) * b` rather
than `(a * b) / divisor`, because the intermediate product can overflow even when the final answer fits,
which is the wrap-around trap from the dynamic memory chapter. The `divisor == 0` guard exists because
`lcm(0, 0)` would otherwise divide by zero, and `a / divisor` truncates exactly, so no precision is lost.
:::

:::solution Exercise 2
Two headers including the same unguarded file, then the same project with guards in place.

```c bad-files
/* ===== limits.h ===== */
int max_rows = 128;

/* ===== config.h ===== */
#include "limits.h"

int max_columns = 64;

/* ===== main.c ===== */
#include <stdio.h>
#include "limits.h"
#include "config.h"

int main(void) {
    printf("%d %d\n", max_rows, max_columns);
    return 0;
}
```

```text
error: redefinition of 'max_rows'
```

`main.c` includes `limits.h` directly and again through `config.h`, so `int max_rows = 128;` is processed
twice in one translation unit and the second one redefines the first. This is a *compiler* error, not a
linker one, which is the useful signal: the duplicate is inside a single file's preprocessing, so the
fix is a guard rather than a change to what is defined where. Adding the guard makes the second inclusion
a no-op, and the same project links:

```c run-files
/* ===== limits.h ===== */
#ifndef LIMITS_H
#define LIMITS_H

int max_rows = 128;

#endif

/* ===== config.h ===== */
#ifndef CONFIG_H
#define CONFIG_H

#include "limits.h"

int max_columns = 64;

#endif

/* ===== main.c ===== */
#include <stdio.h>
#include "limits.h"
#include "config.h"

int main(void) {
    printf("%d %d\n", max_rows, max_columns);
    return 0;
}
```

```text
128 64
```

Note that `config.h` needs its own guard for the same reason, even though it includes nothing twice in
this program — the moment a third file includes `config.h` as well, its contents would be processed twice
and the same error would come back. Guards are not about the file that has the problem; they are about
every file that might ever include it.
:::

:::solution Exercise 3
`static const` links; plain `const` does not.

```c run-files
/* ===== constants.h ===== */
#ifndef CONSTANTS_H
#define CONSTANTS_H

static const double PI = 3.14159265358979;

#endif

/* ===== circle.c ===== */
#include "constants.h"

double circle_area(double radius) {
    return PI * radius * radius;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "constants.h"

double circle_area(double radius);

int main(void) {
    printf("%.4f\n", circle_area(2.0));
    return 0;
}
```

```text
12.5664
```

`static const` gives each translation unit its own private copy of `PI`, so `circle.c` and `main.c` each
have one and the linker never sees a duplicate. The cost is that the two copies are different objects at
different addresses, which matters if you ever compare `&PI` across files — it is one of the few places
where "the same constant" is not the same object. Change `static const` to plain `const` and the error
becomes `duplicate symbol`, because in C a file-scope `const` has external linkage: the header defines
the object once per including file. The one-sentence answer to the exercise is that in C, `const` says
the value cannot be modified and says nothing at all about linkage — the two ideas are independent, and
C++ is the language where they happen to coincide.
:::

:::solution Exercise 4
Work out the expansion by hand first, then add the parentheses.

```c run
#include <stdio.h>

#define MAX_BROKEN(a, b) a > b ? a : b
#define MAX(a, b) (((a) > (b)) ? (a) : (b))

int main(void) {
    printf("broken 2 * MAX(3, 4) = %d\n", 2 * MAX_BROKEN(3, 4));
    printf("fixed  2 * MAX(3, 4) = %d\n", 2 * MAX(3, 4));
    return 0;
}
```

```text
broken 2 * MAX(3, 4) = 3
fixed  2 * MAX(3, 4) = 8
```

By hand: `2 * MAX_BROKEN(3, 4)` expands to `2 * 3 > 4 ? 3 : 4`. The multiplication binds tighter than
the comparison, so this is `(2 * 3) > 4`, which is `6 > 4` — true — and the conditional picks `3`. The
answer is three times too small, and nothing warns you, because every operator in the expansion is doing
exactly what it says; the mistake is that the macro's `?:` was never protected from the `2 *` that got
pasted in front of it. The fixed version expands to `2 * (((3) > (4)) ? (3) : (4))`, where the outer
parentheses mean the multiplication applies to the conditional's *result* rather than to its first
branch, and the answer is `8`.

Both parenthesisation rules are doing work here. Around each parameter, so an argument's own operators
cannot leak into the surrounding expression; and around the whole expansion, so the macro's operators
cannot leak into whatever it is embedded in. This example needs the second rule, and the `SQUARE(1 + 2)`
example earlier in the chapter needs the first. Note that the fixed macro still evaluates its chosen
argument twice, so `MAX(i++, j++)` remains a bug no amount of parenthesising will fix — for that you
need a function, or `static inline`.
:::

:::solution Exercise 5
Three source files, a header, and a Makefile with a `clean` target.

```c make-files
/* ===== stats.h ===== */
#ifndef STATS_H
#define STATS_H

int stats_sum(const int *values, int count);
int stats_max(const int *values, int count);

#endif

/* ===== stats.c ===== */
#include "stats.h"

int stats_sum(const int *values, int count) {
    int total = 0;

    for (int i = 0; i < count; i++) {
        total += values[i];
    }
    return total;
}

int stats_max(const int *values, int count) {
    int best = values[0];

    for (int i = 1; i < count; i++) {
        if (values[i] > best) {
            best = values[i];
        }
    }
    return best;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "stats.h"

int main(void) {
    const int values[5] = {4, 8, 15, 16, 23};

    printf("sum = %d, max = %d\n", stats_sum(values, 5), stats_max(values, 5));
    return 0;
}

/* ===== Makefile ===== */
CC = clang
CFLAGS = -std=c17 -Wall -Wextra -Werror

prog: main.o stats.o
	$(CC) $(CFLAGS) -o prog main.o stats.o

main.o: main.c stats.h
	$(CC) $(CFLAGS) -c main.c

stats.o: stats.c stats.h
	$(CC) $(CFLAGS) -c stats.c

clean:
	rm -f prog main.o stats.o
```

```text
sum = 66, max = 23
```

The rebuild rule is the part of this exercise worth doing by hand. Run `make` once and it compiles both
object files; run it again and it says `make: Nothing to be done for 'prog'.`, because both objects are
newer than their sources. Touch `stats.h` — `touch stats.h`, or just edit a comment in it — and `make`
rebuilds *both* object files, because both rules list the header as a dependency. That is the behaviour
that a rule omitting `stats.h` would silently break: the objects would still be newer than the `.c` files
they came from, so make would skip them, and the program would link against a stale definition of the
struct or macro the header changed. Stale builds are the worst class of bug in a Makefile precisely
because nothing fails — the code is right and the binary is old.

`clean` is the other convention worth having from the start. `make clean` removes every generated file so
the next `make` is a full rebuild, which is the first thing to try when a build behaves impossibly.
Listing the generated files explicitly (`prog main.o stats.o`) rather than using a wildcard means
`make clean` can never delete a source file by accident.
:::

:::solution Exercise 6
Two translation units, two `static` functions with the same name and different behaviour.

```c run-files
/* ===== helper.h ===== */
#ifndef HELPER_H
#define HELPER_H

int describe_a(void);
int describe_b(void);

#endif

/* ===== helper_a.c ===== */
#include "helper.h"

static int value(void) {
    return 1;
}

int describe_a(void) {
    return value() * 10;
}

/* ===== helper_b.c ===== */
#include "helper.h"

static int value(void) {
    return 2;
}

int describe_b(void) {
    return value() * 10;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "helper.h"

int main(void) {
    printf("%d %d\n", describe_a(), describe_b());
    return 0;
}
```

```text
10 20
```

There is no link error, and there would not be even if a hundred files each declared their own `static
int value(void)` — internal linkage means the name never reaches the linker's symbol table, so there is
nothing for it to collide with. Each `describe_*` function calls *its own file's* `value`, which is why
the two answers differ despite the identical name and signature. Remove `static` and the linker reports
`duplicate symbol: _value`, because both functions become external and the program defines one name
twice.

This is the mechanism that makes it possible for two libraries to coexist in one program while both
containing an internal helper called `init` or `parse`. It is also why `static` at file scope is not the
same keyword as `static` inside a function: there it means "this variable survives between calls"; at
file scope it means "this name is private to this file". Same word, two unrelated jobs — one of C's
older naming decisions, and worth reading as two different keywords whenever you meet it.
:::
