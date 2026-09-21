---
chapter: 15
part: 2
title: The Preprocessor
summary: Understand the text-substitution phase that runs before the compiler — includes, object-like and function-like macros, stringify and paste, conditional compilation and include guards — and why nearly every macro has a safer modern replacement.
minutes: 70
tags: [preprocessor, macro, include, include-guard, conditional-compilation, stringify, token-paste, NDEBUG, assert, pragma-once]
---

Every program you have compiled so far was not compiled. It was edited first. A separate program
called the **preprocessor** read your source as *text*, spliced other files into it, replaced
identifiers with other text, deleted whole blocks, and handed the result to the compiler proper.
The compiler never saw your `#define`. This chapter makes that invisible phase visible, because
the bugs it produces are unlike any other bug in C: the code that fails to compile is not the code
you wrote, and the error message points at a line that does not exist in your file.

## The preprocessor is a text editor, not a compiler

The clearest way to see this is to stop before compiling. `clang -E` runs only the preprocessor and
prints what it produced; `-P` suppresses the `# 1 "file.c"` line markers that debuggers use, so the
output is just C:

```sh run
cat > demo.c <<'EOF'
#define GREET "hi"
#define DBL(x) ((x) * 2)
int main(void) { return DBL(3); }
EOF
clang -E -P demo.c
```

```text
int main(void) { return ((3) * 2); }
```

Two things happened. `DBL(3)` became `((3) * 2)` — the macro's parameters were substituted as
*text*, and the parentheses you wrote in the definition survived into the output. And `GREET`
vanished entirely, because an unused macro expands to nothing at all. Nothing here has been parsed,
type-checked or even understood as C. The preprocessor does not know what a function is.

That is the whole model, and every macro bug in this chapter is a consequence of it.

## Object-like and function-like macros

A macro has one of two shapes. An **object-like** macro is a name replaced by a token sequence; a
**function-like** macro takes arguments and substitutes them into its body.

```c run
#include <stdio.h>

#define GREET  "hello"
#define PI     3.14159
#define DBL(x) ((x) * 2)

int main(void) {
    printf("GREET        = %s\n", GREET);
    printf("PI           = %.5f\n", PI);
    printf("DBL(21)      = %d\n", DBL(21));
    printf("this is line %d\n", __LINE__);
    return 0;
}
```

```text
GREET        = hello
PI           = 3.14159
DBL(21)      = 42
this is line 11
```

`__LINE__` is not defined by you — it is one of the macros the implementation provides, and the
preprocessor rewrites it at every use to the line number it was expanded on. The value in the output
is the line of the `printf`, not the line of any `#define`.

The rule the standard actually states is worth internalising: after substitution, the result must be
a valid sequence of *tokens*. Not a valid expression, not a valid statement — tokens. A macro can
expand to half an expression, which is exactly how the next two bugs happen.

## Trap 1: a macro without parentheses is a precedence bug

```c run
#include <stdio.h>

#define SQUARE_NAIVE(x) x * x
#define SQUARE_SAFE(x)  ((x) * (x))

int main(void) {
    printf("SQUARE_NAIVE(1 + 2) = %d\n", SQUARE_NAIVE(1 + 2));
    printf("SQUARE_SAFE(1 + 2)  = %d\n", SQUARE_SAFE(1 + 2));

    int n = 1 + 2;
    printf("SQUARE_NAIVE(n)     = %d   (n = %d)\n", SQUARE_NAIVE(n), n);
    return 0;
}
```

```text
SQUARE_NAIVE(1 + 2) = 5
SQUARE_SAFE(1 + 2)  = 9
SQUARE_NAIVE(n)     = 9   (n = 3)
```

`SQUARE_NAIVE(1 + 2)` expanded to `1 + 2 * 1 + 2`, and `*` binds tighter than `+`, so the answer is
`5` instead of `9`. Note the third line: with a plain variable `n` the naive macro gives the right
answer. **This bug is invisible until someone passes an expression**, which is why it survives code
review and then appears years later.

The fix is on the second line: parenthesise the whole body *and* every parameter. The outer
parentheses keep the result atomic in a larger expression; the inner ones keep an argument's own
precedence from leaking.

## Trap 2: an argument can be evaluated twice

Parentheses do not fix everything. A function-like macro copies its argument text into the body, so
an argument with a side effect is evaluated once per occurrence.

```c run
#include <stdio.h>

#define MAX_NAIVE(a, b) ((a) > (b) ? (a) : (b))

static int max_fn(int a, int b) { return a > b ? a : b; }

int main(void) {
    int i = 3;
    int r1 = MAX_NAIVE(i++, 2);
    printf("MAX_NAIVE(i++, 2) = %d   i is now %d\n", r1, i);

    int j = 3;
    int r2 = max_fn(j++, 2);
    printf("max_fn(j++, 2)    = %d   j is now %d\n", r2, j);
    return 0;
}
```

```text
MAX_NAIVE(i++, 2) = 4   i is now 5
max_fn(j++, 2)    = 3   j is now 4
```

`MAX_NAIVE(i++, 2)` should be `max(3, 2)`, which is `3`. It printed `4`, and `i` ended at `5` —
incremented **twice**, once by the comparison and once by the branch that was taken. The static
function did the sane thing: one increment, `j` at `4`, the right answer. A macro is not a function
and cannot be made to behave like one in this respect; the only fix is not to pass an argument with
a side effect, or to use a function.

:::danger The macro that looks like a function
`MAX_NAIVE` above has both parentheses *and* a ternary, and it is still wrong, because the defect is
duplication, not precedence. A macro whose body mentions an argument twice is broken for any
argument that is not a pure expression. When you review a macro, count how many times each parameter
appears in the body.
:::

## Making a macro behave like one statement

A macro that expands to several statements cannot be used where the language expects one, and this
is the failure that produces the most confusing diagnostic in the whole language.

```c run
#include <stdio.h>

#define BUMP(a) do { (a) += 1; printf("bumped to %d\n", (a)); } while (0)

int main(void) {
    int x = 0;
    if (x == 0)
        BUMP(x);
    else
        printf("skipped\n");
    printf("x = %d\n", x);
    return 0;
}
```

```text
bumped to 1
x = 1
```

The `do { ... } while (0)` wrapper is the idiom. It is one statement, so it sits correctly under an
`if`, and the trailing `while (0)` means it runs exactly once. The `0` is a constant, so the
compiler folds the loop away entirely.

Remove the wrapper and the same call site stops compiling:

```c bad
#include <stdio.h>

#define BUMP_BAD(a) (a) += 1; printf("bumped to %d\n", (a))

int main(void) {
    int x = 0;
    if (x == 0)
        BUMP_BAD(x);
    else
        printf("skipped\n");
    printf("x = %d\n", x);
    return 0;
}
```

```text
error: expected expression
```

Read that carefully, because the error is not where you would look. `BUMP_BAD(x)` expanded to two
statements; the `;` you typed after the call ended the `if`, so `else` arrived with no `if` to
attach to and the parser reported `expected expression` — pointing at `else`, not at the macro. This
is the cost of a phase the compiler cannot see: **the diagnostic describes the expanded text, not
your source.**

## Turning tokens into text: `#` and `##`

Two operators work only inside a macro body. `#` stringifies its argument; `##` pastes two tokens
into one.

```c run
#include <stdio.h>

#define STRINGIFY(x) #x
#define CONCAT(a, b) a##b

int main(void) {
    printf("STRINGIFY(1 + 2)    = %s\n", STRINGIFY(1 + 2));
    printf("STRINGIFY(\"text\")   = %s\n", STRINGIFY("text"));

    int CONCAT(wa, ter) = 42;
    printf("water               = %d\n", water);
    return 0;
}
```

```text
STRINGIFY(1 + 2)    = 1 + 2
STRINGIFY("text")   = "text"
water               = 42
```

`STRINGIFY(1 + 2)` produced the string `1 + 2` — the tokens were turned into text before any
arithmetic happened, which is what makes this useful for logging the expression itself. `##` built
the identifier `water` out of `wa` and `ter` in `int CONCAT(wa, ter) = 42;`. Both operators run on
tokens, so `##` will happily produce something that is not a valid identifier, and you will find out
from the compiler rather than from the preprocessor.

## Conditional compilation

The preprocessor can delete code before the compiler sees it, which is how one source tree serves
several builds.

```c run
#include <stdio.h>

#define LEVEL 2

int main(void) {
#if !defined(LEVEL)
#error "LEVEL must be defined"
#endif

#if LEVEL >= 3
    printf("level 3: verbose diagnostics\n");
#elif LEVEL == 2
    printf("level 2: normal diagnostics\n");
#else
    printf("level 1: quiet\n");
#endif

#ifdef __clang__
    printf("built with clang\n");
#else
    printf("built with something else\n");
#endif
    return 0;
}
```

```text
level 2: normal diagnostics
built with clang
```

`#if` is evaluated by the preprocessor, so its expression must be made of integer constants and
`defined(...)` — it cannot call a function or read a variable. `#ifdef NAME` is shorthand for
`#if defined(NAME)`. Branches not taken are removed from the translation unit completely: they are
never type-checked, which is how platform-specific code for an OS you do not target can contain
calls that do not exist on your machine.

When no branch is acceptable, say so and stop the build:

```c bad
#if !defined(ENABLED)
#error "ENABLED must be defined before this file is used"
#endif

int main(void) { return 0; }
```

```text
error: "ENABLED must be defined before this file is used"
```

`#error` is the preprocessor's way of failing the build with your own message. Use it for a
configuration the project cannot work without; a build that stops with a sentence is far better than
one that compiles something wrong.

### The macros you did not write

```c run
#include <stdio.h>

int main(void) {
    printf("__LINE__         = %d\n", __LINE__);
    printf("__STDC__         = %d\n", __STDC__);
    printf("__STDC_VERSION__ = %ldL\n", (long)__STDC_VERSION__);
    printf("__func__         = %s\n", __func__);
    return 0;
}
```

```text
__LINE__         = 4
__STDC__         = 1
__STDC_VERSION__ = 201710L
__func__         = main
```

`__STDC_VERSION__` is `201710L` under `-std=c17`, so you can gate a feature on the standard rather
than on the compiler. `__func__` is the odd one out: it is **not** a macro. It is a predefined
identifier the compiler provides inside every function, so it has a value at run time and cannot be
used in `#if`. Confusing the two is a common first mistake — `#if defined(__func__)` is always
false.

## Headers need a guard

A header is text, and `#include` is a copy. Include the same header twice in one translation unit
and its declarations appear twice. For a `struct`, that is an error:

```c bad-files
/* ===== cfg.h ===== */
struct Config { int port; };
/* ===== main.c ===== */
#include "cfg.h"
#include "cfg.h"
int main(void) { return 0; }
```

```text
error: redefinition of 'Config'
```

The fix is an **include guard**: a macro that records that the header has already been spliced in.

```c run-files
/* ===== settings.h ===== */
#ifndef SETTINGS_H
#define SETTINGS_H

#define APP_NAME "serve"

int max_connections(void);

#endif
/* ===== settings.c ===== */
#include "settings.h"

int max_connections(void) { return 8; }
/* ===== guardmain.c ===== */
#include <stdio.h>

#include "settings.h"
#include "settings.h"   /* deliberately twice: the guard makes this a no-op */

int main(void) {
    printf("app = %s\n", APP_NAME);
    printf("max = %d\n", max_connections());
    return 0;
}
```

```text
app = serve
max = 8
```

`guardmain.c` includes `settings.h` twice on purpose, and the second include is a no-op: the guard's
`#ifndef` is false, so the whole body is skipped. The guard also makes the header safe to include
from **two different translation units** — `settings.c` and `guardmain.c` both include it, and the
declaration of `max_connections` is seen once per file, which is correct. The guard protects against
double inclusion per file, not against the symbol being defined twice; that second problem is why a
header should *declare* a function and a `.c` file should *define* it.

`#pragma once` does the same job and is supported by every compiler you will meet, but it is not in
the standard and it identifies a file by path, which is ambiguous when the same header is reachable
under two names through symlinks or copies. Guards are portable and explicit; the pragma is
convenient. Pick one and use it everywhere.

## Two things that go wrong at definition time

Redefining a macro is a warning, not an error, so the compiler tells you and carries on:

```c warn
#define BUFFER 64
#define BUFFER 128

int main(void) { return BUFFER; }
```

```text
warning: 'BUFFER' macro redefined [-Wmacro-redefined]
```

The second value wins, and every use after that line silently means something different from every
use before it. This is what makes a macro a poor way to hold a constant: there is no scope, no type,
and no protection against a later `#define` in a header you did not read.

A function-like macro with the wrong number of arguments is a hard error:

```c bad
#define ADD(a, b) ((a) + (b))

int main(void) { return ADD(1); }
```

```text
error: too few arguments provided to function-like macro invocation
```

Note that the compiler also reported `use of undeclared identifier 'ADD'` — after the macro failed to
expand, the name reached the compiler as an ordinary identifier it had never heard of. One mistake,
two diagnostics, neither mentioning your actual error.

## Assertions are macros, and `NDEBUG` removes them

`assert` is a macro, which is what lets it be compiled out entirely.

```sh run
cat > a.c <<'EOF'
#include <assert.h>
#include <stdio.h>
int main(void) {
    int x = 0;
    assert(x != 0);
    printf("survived\n");
    return 0;
}
EOF
clang -std=c17 -o with_assert a.c
./with_assert 2>&1
echo "exit=$?"
clang -std=c17 -DNDEBUG -o no_assert a.c
./no_assert 2>&1
echo "exit=$?"
```

```text
Assertion failed: (x != 0), function main, file a.c, line 5.
exit=134
survived
exit=0
```

With `assert` active the program dies with a message naming the expression, the function, the file
and the line, and exits `134` (`128 + SIGABRT`). With `-DNDEBUG` the macro expands to nothing, the
check is gone, and the program runs on. Because `NDEBUG` deletes the expression itself, **an
assertion must never contain a side effect** — `assert(advance() != 0)` is a call that exists in
debug builds and does not exist in release ones.

:::scenario A constant that changed value halfway through a file
A teammate reports that a buffer allocated with `BUFFER` is sometimes 64 bytes and sometimes 128, in
the same binary. You find `#define BUFFER 64` at the top of a header and `#define BUFFER 128` in a
`.c` file that includes it — a redefinition the compiler warned about and nobody read. The code that
ran before the second `#define` used 64; the code after it used 128.
:::

:::solution Replace the macro with a real constant, so redefinition becomes a compile error instead of a warning. In C, `static const int buffer_size = 64;` in the header gives it a type and a scope, and a second definition is an error rather than a note. In C++, `constexpr int kBufferSize = 64;`. Then delete both `#define` lines and let the compiler find every use that no longer compiles. The warning was free information about a real bug; treating warnings as noise is what let it ship.
:::

:::pitfall `__DATE__` and `__TIME__` in a build
`__DATE__` and `__TIME__` expand to when the *preprocessor ran*, not when the file was written.
Embed them in a version string and every rebuild produces a different binary, which defeats
reproducible builds and any caching you have. Worse, they make two builds of identical source
unequal, so a "no change" release still looks changed. If a build needs a timestamp, pass it in from
the build system as a `-D` so that it is explicit and can be pinned.
:::

## What C++ does instead

Almost every macro in this chapter has a replacement that is typed, scoped and visible to the
debugger.

```cpp run
#include <iostream>

constexpr int kMax = 64;                                  // replaces #define kMax 64
inline int square(int x) { return x * x; }                // replaces #define SQUARE(x) ((x)*(x))
template <typename T> T max_of(T a, T b) { return a > b ? a : b; }

int main() {
    std::cout << "kMax         = " << kMax << "\n";
    std::cout << "square(1+2)  = " << square(1 + 2) << "\n";
    std::cout << "max_of(3, 2) = " << max_of(3, 2) << "\n";
    return 0;
}
```

```text
kMax         = 64
square(1+2)  = 9
max_of(3, 2) = 3
```

`square(1 + 2)` is `9`, not `5`: `square` is a function, so its argument is evaluated once, in the
caller, before the body runs. That single property removes Trap 1 and Trap 2 at once.

| You want | Macro | Modern replacement |
|---|---|---|
| A constant | `#define N 64` | `constexpr int N = 64;` (C++), `static const int N = 64;` (C) |
| A small function | `#define SQ(x) ((x)*(x))` | `inline` function, or `constexpr` |
| A generic function | `#define MAX(a,b) ...` | `template` — typed, and arguments evaluated once |
| Conditional code | `#ifdef DEBUG` | still `#ifdef`; there is no replacement |
| A header guard | `#ifndef H` / `#pragma once` | `## once` is idiomatic; C++20 modules are the intended answer |

Two entries have no replacement, and that is the honest boundary of this chapter: **conditional
compilation and `#include` are still preprocessor jobs.** C++20 modules were designed to replace
headers, but Apple clang does not implement them, so this book cannot compile an example of one.
Every other row in that table should be a macro only when you can say why the replacement does not
work.

## Key takeaways

- The preprocessor edits text before the compiler parses anything; it has no idea what a type, a function or a statement is.
- Parenthesise a function-like macro's whole body **and** every parameter, or an argument containing an operator will re-order your arithmetic.
- An argument that appears twice in a macro body is evaluated twice, so `MAX(i++, 2)` increments `i` twice; parentheses cannot fix this.
- Wrap a multi-statement macro in `do { ... } while (0)` so it is one statement and works under `if` / `else`.
- A header must be guarded, because `#include` is a copy and an unguarded struct definition included twice is a redefinition error.
- `#if` is evaluated by the preprocessor, so it only understands integer constants and `defined(...)`; it cannot read a variable or call a function.
- `__func__` is a predefined identifier, not a macro, so it has no value at preprocessing time and cannot appear in `#if`.
- `NDEBUG` deletes `assert` expressions entirely, so an assertion must never contain a side effect.
- Prefer `constexpr`, `inline` and templates over macros; they are typed, scoped, evaluated once and visible to a debugger.

## Practice

- [ ] Write `#define AREA(w, h) w * h` and call `AREA(2 + 1, 4)`. Predict the answer, then fix the macro and confirm it prints `12`.
- [ ] Write a `SWAP_BAD(a, b)` macro with three statements and no wrapper, use it under `if (...) ... else ...`, and record the exact diagnostic. Then wrap it in `do { } while (0)` and show it compile and run.
- [ ] Build a two-file program where a header declares `int version(void);` and is included by both translation units. Prove the guard works by including it twice in one file.
- [ ] Use `#` to write `LOG_EXPR(x)` that prints both the expression text and its value, so `LOG_EXPR(2 * 21)` prints `2 * 21 = 42`.
- [ ] Gate a debug block on `#ifdef VERBOSE` and show the binary's output change without editing any C — by adding a `#define VERBOSE` line only.
- [ ] Add `assert` to a function that must not receive `0`, run it with and without `-DNDEBUG`, and explain why the release build does not crash.

## Solutions

:::solution Exercise 1
`#define AREA(w, h) w * h` expands `AREA(2 + 1, 4)` to `2 + 1 * 4`, which is `2 + 4 = 6` — not `12`.
Parenthesise both the body and each parameter: `#define AREA(w, h) ((w) * (h))`. The outer
parentheses also matter: without them, `AREA(2, 3) + 1` would expand to `2 * 3 + 1`.
:::

:::solution Exercise 2
The unwrapped macro expands to three statements, so the `;` you type after the call terminates the
`if` and the following `else` has nothing to attach to. clang reports `error: expected expression`
pointing at `else`, which is why the message is so hard to connect to the macro. `do { ... } while (0)`
makes the expansion a single statement, so the `if` / `else` parses; the `0` is a constant and the
compiler removes the loop.
:::

:::solution Exercise 3
Put `#ifndef MY_H` / `#define MY_H` around the header body and `#endif` at the bottom. Including it
twice in one translation unit is then a no-op because the guard macro is already defined. Including
it from two translation units is fine because each file gets its own copy of the *declaration*; only
the single definition in one `.c` file produces a symbol. Without the guard, a `struct` in the
header gives `error: redefinition of 'Config'`; a plain function declaration would only warn, which
is why the failure is easy to miss until the header grows a type.
:::

:::solution Exercise 4
`#` works only on a macro parameter, so you need one level of indirection when the parameter is
itself a macro: `#define LOG_EXPR(x) printf("%s = %d\n", #x, (x))`. `#x` produces the string
`"2 * 21"` and `(x)` produces `42`. The indirection matters for the general case:
`#define STR(x) #x` used as `STR(SOME_MACRO)` yields `"SOME_MACRO"`, not the expanded value, because
`#` suppresses expansion of its operand.
:::

:::solution Exercise 5
Add `#define VERBOSE` as the first line of the file (or pass `-DVERBOSE`), and wrap the extra
printing in `#ifdef VERBOSE` / `#endif`. Because the preprocessor deletes the block when the macro is
absent, the release build contains no branch and no string — the check costs nothing at run time.
This is the one job macros still do better than any alternative.
:::

:::solution Exercise 6
`assert` is a macro from `<assert.h>`. Without `-DNDEBUG` it tests the expression and, on failure,
writes the expression, file and line to stderr and calls `abort`, so the process dies with `SIGABRT`
(exit `134`). With `-DNDEBUG` the macro expands to nothing at all, so the check is absent from the
binary and the program continues — which is why the assertion must not contain a side effect such as
`assert(advance() != 0)`, since that call would exist in debug builds only.
:::
