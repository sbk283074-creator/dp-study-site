---
chapter: 6
part: 1
title: Functions and the Stack
summary: Give a computation a name and a contract — how arguments actually travel, why C's pass-by-value surprises everyone once, what a stack frame is, and when recursion is the right answer.
minutes: 55
tags: [functions, prototypes, pass by value, stack, recursion, static, linker]
---

A function is two things at once: a way to name a computation so you can call it from ten places, and
a contract about what goes in and what comes out. C takes that contract more literally than most
languages, and the mechanism it uses to honour it — copying values onto a stack of frames — explains
most of the surprising behaviour you will meet for the rest of this book. Understanding the frame is
not academic. It is why a `swap` function does nothing, why a large local array can crash a program,
and why a recursive function that works on small inputs dies on large ones.

## Declare before you call

C compiles each file top to bottom, so a function must be *known* before it is called. A **prototype**
declares the contract without providing the body:

```c run
#include <stdio.h>

static int double_it(int value);   /* prototype: name, arguments, return type */

int main(void) {
    printf("%d\n", double_it(21));
    return 0;
}

static int double_it(int value) {  /* definition: the body */
    return value * 2;
}
```

```text
42
```

The prototype is the contract and the definition is the implementation, and they can live far apart —
in different files, in fact, which is what a header file is for (Chapter 13). The compiler checks
every call against the prototype, which is why the argument types and the return type are worth
getting right before you write the body.

In C99 and later, calling a function that has never been declared is an error rather than a warning,
because the old behaviour — assuming it returns `int` and guessing the arguments — was a rich source
of crashes:

```c bad
#include <stdio.h>

int main(void) {
    printf("%d\n", helper(3));
    return 0;
}

static int helper(int value) {
    return value * 2;
}
```

```text
error: call to undeclared function 'helper'; ISO C99 and later do not support implicit function declarations [-Wimplicit-function-declaration]
```

The compiler is telling you the order is wrong, not the code. Move the definition above `main`, or add
a prototype above it. A prototype is usually the better choice, because it puts the contract where a
reader will see it first.

There is a second, subtler failure waiting in the same place. A prototype promises that the function
exists *somewhere*; the compiler takes that promise and moves on. If nothing ever defines it, the
compiler is satisfied and the **linker** is not:

```c bad
#include <stdio.h>

int helper(int value);

int main(void) {
    printf("%d\n", helper(3));
    return 0;
}
```

```text
Undefined symbols for architecture arm64
```

The build failed, but notice where. The source compiled with no complaints at all — the prototype made
the call legal — and the failure came from `ld`, the linker, when it went looking for a function named
`helper` and found none. This is the distinction from Chapter 1's scenario: compiling turns one file
into an object file, and linking joins the object files into a program. An `undefined reference` or
`Undefined symbols` error means your declarations and your definitions disagree about what exists, and
no amount of staring at the line the linker names will show you why — the problem is a *missing* file
or a name that does not match. The wording differs by platform: clang on macOS says `Undefined symbols
for architecture arm64`, GCC on Linux says `undefined reference to 'helper'`. Both are linker errors,
and both mean the same thing.

## Everything is passed by value

This is the single most important sentence in the chapter: **C passes every argument by copying its
value.** The function gets its own variable, initialised with a copy of the caller's. Writing to it
changes the copy and nothing else.

```c run
#include <stdio.h>

static void swap(int a, int b) {
    int temporary = a;
    a = b;
    b = temporary;
}

int main(void) {
    int x = 1;
    int y = 2;

    swap(x, y);
    printf("x=%d y=%d\n", x, y);
    return 0;
}
```

```text
x=1 y=2
```

`swap` works perfectly — on its own copies. `x` and `y` in `main` are untouched, because `a` and `b`
were never `x` and `y`; they were two integers that started with the same values. This is not a bug
in `swap`, it is the definition of a call.

To let a function change the caller's variable, you pass the *address* of the variable. The copy that
travels is then a copy of the address, and the function can follow it back:

```c run
#include <stdio.h>

static void swap(int *a, int *b) {
    int temporary = *a;
    *a = *b;
    *b = temporary;
}

int main(void) {
    int x = 1;
    int y = 2;

    swap(&x, &y);
    printf("x=%d y=%d\n", x, y);
    return 0;
}
```

```text
x=2 y=1
```

The `&` at the call site is the whole difference, and it is deliberate: C makes you write `&x` so that
a reader can see that this call may modify `x`. Languages that hide this are not doing you a favour;
they are moving the surprise somewhere you will find it later. Chapter 7 takes pointers apart
properly.

:::note Why arrays seem to be the exception
They are not. When you pass an array, the *array* is not copied — but that is not a special rule for
arguments, it is what an array name means in any expression. `values` in an expression is converted to
a pointer to its first element, so what gets copied is a pointer. This is why a function can modify
the caller's array, and why `sizeof` inside the function does not tell you the array's length. The
scenario below is that bug.
:::

## Returning a value, and void

A function declares its return type, and `return` converts the value to that type on the way out — so
a mismatch is a conversion, not an error. Returning `double` from a function declared `int` silently
truncates. A function that returns nothing is declared `void`, and a `void` function may use a bare
`return;` to leave early.

`main` is special in one way only: reaching its closing brace without a `return` is defined to exit
with status `0`. Every other function that falls off the end without returning a value is undefined
behaviour, and the compiler will warn about it (see the pitfall below).

## The call stack

Every call gets a **stack frame**: a block of memory holding the arguments, the function's local
variables, and the return address — the place in the caller to resume at. Frames are pushed on call
and popped on return, so the most recent call is always at the top. That is why you see this:

```c run
#include <stdio.h>

static void frame(int depth) {
    int local = depth * 10;

    if (depth < 3) {
        frame(depth + 1);
    }

    printf("depth %d: local = %d\n", depth, local);
}

int main(void) {
    frame(1);
    return 0;
}
```

```text
depth 3: local = 30
depth 2: local = 20
depth 1: local = 10
```

The prints come out backwards. `frame(1)` calls `frame(2)`, which calls `frame(3)`, which prints first
— and then each frame returns to the line after its call and prints on the way back down. Three
separate `local` variables existed at the same time, one per frame, each holding its own value. That
is the stack, made visible.

The stack has a fixed size — commonly 8 MB on the main thread — and each frame consumes some of it. A
function with a large local array uses a lot per call; deep recursion uses a little per call, many
times. Either way, running out is a hard crash, not an error you can catch.

## Recursion

A recursive function calls itself. It is the natural way to express anything defined in terms of a
smaller version of itself, and it costs a frame per level.

```c run
#include <stdio.h>

static long calls = 0;

static long fib(int n) {
    calls++;
    if (n < 2) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

int main(void) {
    printf("fib(20) = %ld\n", fib(20));
    printf("calls   = %ld\n", calls);
    return 0;
}
```

```text
fib(20) = 6765
calls   = 21891
```

The answer is right and the call count is the lesson. Twenty-one thousand calls to compute the
twenty-first Fibonacci number, because `fib(n - 1)` and `fib(n - 2)` recompute the same subtrees over
and over. Each extra input value roughly multiplies the work by 1.6, so `fib(40)` would be about
two hundred million calls. **A correct recursive function can still be the wrong program.** When the
recursion tree has overlapping branches, you either add a cache (Chapter 23) or you write it as a
loop.

The failure mode when the base case is wrong is worse than slow:

```c run-san-catch
#include <stdio.h>

static int countdown(int n) {
    if (n == 0) {
        return 0;
    }
    return countdown(n - 1) + 1;
}

int main(void) {
    printf("%d\n", countdown(-1));
    return 0;
}
```

```text
stack-overflow
```

The base case exists and is correct — for `n == 0`. Called with `-1`, the function counts downwards
forever, never reaches zero, and each call consumes a frame until the stack runs out. The sanitizer
names it exactly: `AddressSanitizer: stack-overflow`. Note that this is a *logic* bug, not a memory
bug; the sanitizer catches it because it is watching the stack, not because you wrote anything
illegal.

## static: two different meanings

`static` at file scope means "this name is private to this file" — internal linkage. A `static`
function cannot be called from another file, which lets you have two files with a `helper` in each
without a clash. That is why every function in this book's examples is `static`: they are all in one
file, and it documents the intent.

`static` on a **local variable** means something else entirely: the variable keeps its value between
calls. It is allocated once, not on each call.

```c run
#include <stdio.h>

static int next_id(void) {
    static int counter = 0;

    counter++;
    return counter;
}

int main(void) {
    printf("%d\n", next_id());
    printf("%d\n", next_id());
    printf("%d\n", next_id());
    return 0;
}
```

```text
1
2
3
```

Without the `static` keyword, the same function returns `1` every time:

```c run
#include <stdio.h>

static int next_id(void) {
    int counter = 0;

    counter++;
    return counter;
}

int main(void) {
    printf("%d\n", next_id());
    printf("%d\n", next_id());
    printf("%d\n", next_id());
    return 0;
}
```

```text
1
1
1
```

The initialiser on a `static` local runs once, not on every call. That makes it a hidden piece of
state — useful for a counter or a lazily-built cache, and dangerous for anything that needs to be
thread-safe or resettable. Prefer passing state in as an argument, and reach for `static` locals only
when the persistence really is a property of the function.

:::scenario The array length that vanished inside the function
A developer writes a helper that returns the sum of an array. To avoid making callers pass the length,
they compute it inside the function with the idiom they know:

```c warn
#include <stdio.h>

static void report(int values[]) {
    printf("sizeof(values) == sizeof(int *): %d\n",
           (int)(sizeof(values) == sizeof(int *)));
}

int main(void) {
    int values[10] = {0};

    report(values);
    return 0;
}
```

```text
sizeof on array function parameter will return size of 'int *' instead of 'int[]' [-Wsizeof-array-argument]
```

The compiler tells them exactly what is wrong: inside `report`, `values` is an `int *`, so
`sizeof(values) / sizeof(values[0])` is `8 / 4`, which is `2`. The function would sum the first two
elements of a ten-element array and return a plausible number. Nothing crashes, no test that uses a
two-element array fails, and the bug only appears on real data.

:::solution Pass the length, and make the parameter const
The length of an array is not part of the array, so it has to travel separately:

```c run
#include <stdio.h>

static int sum(const int *values, size_t count) {
    int total = 0;

    for (size_t i = 0; i < count; i++) {
        total += values[i];
    }
    return total;
}

int main(void) {
    int values[5] = {1, 2, 3, 4, 5};
    size_t count = sizeof(values) / sizeof(values[0]);

    printf("sum of %zu values = %d\n", count, sum(values, count));
    return 0;
}
```

```text
sum of 5 values = 15
```

Note where the `sizeof` idiom lives now: in `main`, where `values` is still a real array and
`sizeof(values)` really is 20. It is correct there and wrong one function away, which is precisely why
it is a trap — it works in every example you write until the day you move it.

The `const` on the parameter is not decoration. It is the function telling every caller, and every
future reader, that it does not modify the array. It also lets the function accept `const` data, which
a non-const parameter cannot. And the `size_t` for the count matches what `sizeof` produces, so the
comparison in the loop has no signed/unsigned mismatch to warn about.
:::

:::pitfall Forgetting to return a value
If a non-`void` function can reach its closing brace without returning, the caller receives whatever
happened to be in the register that was supposed to hold the answer. There is no default and no error
— the behaviour is undefined.

```c warn
#include <stdio.h>

static int classify(int value) {
    if (value > 0) {
        return 1;
    }
    if (value < 0) {
        return -1;
    }
}

int main(void) {
    printf("%d\n", classify(0));
    return 0;
}
```

```text
non-void function does not return a value in all control paths [-Wreturn-type]
```

The two `if`s cover every value except zero, and zero is exactly what the program passes in. The
compiler sees the gap and says so — this warning is on by default, not something you have to opt into,
so a build with `-Werror` will not let it through. The fix is a final `return 0;` after the second
`if`, which is also the clearest way to say "zero is neither positive nor negative".
:::

## Key takeaways

- A prototype declares a function's contract; the definition provides the body. C needs the contract
  before the call.
- Calling an undeclared function is an error in C99 and later, because the old implicit-declaration
  rule assumed the wrong return type and argument list.
- **C passes every argument by value.** A function writing to a parameter changes only its own copy.
- To let a function modify the caller's variable, pass its address with `&` and accept a pointer.
- Arrays are not an exception: an array name in an expression becomes a pointer to its first element,
  so what is copied is the pointer. `sizeof` inside the function therefore reports a pointer's size.
- A non-`void` function that can reach its closing brace without returning is undefined behaviour;
  `-Wreturn-type` warns about it by default.
- Each call gets a stack frame holding its arguments, locals and return address; frames are pushed on
  call and popped on return, which is why locals in a recursive function are independent.
- Recursion costs a frame per level. A wrong base case exhausts the stack, and AddressSanitizer
  reports it as `stack-overflow`.
- A correct recursive function can still be too slow: naive `fib(20)` makes 21 891 calls because the
  subtrees repeat.
- `static` at file scope means private to the file; `static` on a local means the variable survives
  between calls, and its initialiser runs once.

## Practice

- [ ] Write `int max_of_three(int a, int b, int c)` and call it with a positive set, a negative set,
      and three equal values.
- [ ] Write `swap` twice — once taking `int`, once taking `int *` — and show in one program that only
      the second one changes the caller's variables.
- [ ] Write a function that takes an array and its length and returns the largest element. Explain in
      one sentence why the length parameter cannot be avoided.
- [ ] Write `factorial` iteratively and recursively, and print both for 1 to 6. Which would you ship
      for `n = 20`, and why?
- [ ] Write a recursive function that prints a countdown from `n` to 0. Call it with a negative number
      and run it under the sanitizer.
- [ ] Write a function that returns a new id each time it is called, using a `static` local. Then
      remove `static` and explain the difference in one sentence.

## Solutions

:::solution Exercise 1
Start with the first value and improve it.

```c run
#include <stdio.h>

static int max_of_three(int a, int b, int c) {
    int best = a;

    if (b > best) {
        best = b;
    }
    if (c > best) {
        best = c;
    }
    return best;
}

int main(void) {
    printf("%d\n", max_of_three(3, 9, 5));
    printf("%d\n", max_of_three(-1, -7, -3));
    printf("%d\n", max_of_three(4, 4, 4));
    return 0;
}
```

```text
9
-1
4
```

Seeding `best` with `a` rather than `0` is the important detail. Initialising to `0` would give the
wrong answer for the all-negative case — `max_of_three(-1, -7, -3)` would return `0`, which is not one
of its arguments. The comparisons are strict `>`, so equal values keep the earlier one, which is why
the third call returns `4` rather than a copy.
:::

:::solution Exercise 3
The length cannot be recovered inside the function, so it has to be passed.

```c run
#include <stdio.h>

static int largest(const int *values, size_t count) {
    int best = values[0];

    for (size_t i = 1; i < count; i++) {
        if (values[i] > best) {
            best = values[i];
        }
    }
    return best;
}

int main(void) {
    int readings[6] = {14, 3, 27, 9, 27, 5};
    size_t count = sizeof(readings) / sizeof(readings[0]);

    printf("largest of %zu = %d\n", count, largest(readings, count));
    return 0;
}
```

```text
largest of 6 = 27
```

The reason the length is unavoidable is the rule from Chapter 3: an array's length is not part of the
array. By the time the pointer arrives in `largest`, the only thing known is where the data starts —
how many elements follow is information that existed at the call site and nowhere else. The
`sizeof(readings) / sizeof(readings[0])` idiom recovers it in `main`, where `readings` is still an
array. Note the loop starts at `i = 1` because `values[0]` seeded `best`; starting at 0 would compare
the first element with itself, which is harmless but says you were not thinking about it.
:::

:::solution Exercise 4
Both are correct; only one is shippable for large inputs.

```c run
#include <stdio.h>

static int factorial_iterative(int n) {
    int result = 1;

    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

static int factorial_recursive(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial_recursive(n - 1);
}

int main(void) {
    for (int i = 1; i <= 6; i++) {
        printf("%d! = %d (iterative), %d (recursive)\n",
               i, factorial_iterative(i), factorial_recursive(i));
    }
    return 0;
}
```

```text
1! = 1 (iterative), 1 (recursive)
2! = 2 (iterative), 2 (recursive)
3! = 6 (iterative), 6 (recursive)
4! = 24 (iterative), 24 (recursive)
5! = 120 (iterative), 120 (recursive)
6! = 720 (iterative), 720 (recursive)
```

Ship the iterative one. The recursive version makes `n` nested calls, so it needs `n` frames — fine for
6, and a stack overflow for a few hundred thousand. The iterative version uses one frame no matter
how large `n` gets. Unlike `fib`, the recursive form here is not even doing anything clever: there is
no branching, so the recursion buys you nothing and costs you the stack.

The other thing to notice is that `int` overflows at `13!` — 6 227 020 800 does not fit in a 32-bit
signed integer. That is the Chapter 3 lesson arriving on schedule: pick the width from the data's
range, and check where the range ends.
:::

:::solution Exercise 6
A `static` local is allocated once and keeps its value; an automatic one is rebuilt on every call.

```c run
#include <stdio.h>

static int next_id(void) {
    static int counter = 0;

    counter++;
    return counter;
}

int main(void) {
    printf("%d\n", next_id());
    printf("%d\n", next_id());
    printf("%d\n", next_id());
    return 0;
}
```

```text
1
2
3
```

Without `static`, `counter` is a fresh variable initialised to `0` on every call, so the function
returns `1` forever — the version shown earlier in the chapter. The `static` keyword moves the variable
out of the frame and into a fixed location that persists for the life of the program, and the
initialiser runs once at startup rather than on each call. The cost is that the function now has
hidden state: two callers interleave, and they share the counter. For a real id generator you would
pass the counter in, or use an atomic, because a `static` local is not thread-safe.
:::
