---
chapter: 7
part: 1
title: Pointers and Memory
summary: Work with addresses directly — what a pointer is, why the type matters, how to reach the heap with malloc and free, and the four memory bugs every C programmer writes at least once.
minutes: 60
tags: [pointers, addresses, dereference, malloc, free, use-after-free, nullptr]
---

Everything so far has kept memory at arm's length: you name a variable, the compiler finds it a
place to live, and the value arrives where you expect. Pointers remove that cushion. A pointer is a
value that names a location, and once you can name a location you can read and write it, walk along
it, hand it to a function, or keep it after the memory it named has gone away. This is the chapter
that makes C worth learning and the chapter that makes it dangerous, because the compiler will let you
do all four of those things and only one of them is usually correct.

## An address is a value

`&` takes the address of a variable. `*` reads or writes the value at an address. A pointer variable
is just a variable that holds an address, and its type says what kind of thing lives there.

```c run
#include <stdio.h>

int main(void) {
    int value = 42;
    int *pointer = &value;

    printf("value              = %d\n", value);
    printf("*pointer           = %d\n", *pointer);
    printf("pointer == &value  : %d\n", (int)(pointer == &value));
    printf("pointer is not NULL: %d\n", (int)(pointer != NULL));
    return 0;
}
```

```text
value              = 42
*pointer           = 42
pointer == &value  : 1
pointer is not NULL: 1
```

Three separate ideas are on display. `&value` produces the address, and it is a value like any other —
you can compare two of them, as line three does. `*pointer` follows the address and gives you the `int`
that lives there, and because it is an lvalue you could also assign through it. And `pointer` is not
magically connected to `value`: it holds a copy of the address, so if you reassign `pointer` to point
somewhere else, `value` is unaffected.

Reading `*` correctly is most of the battle. In a *declaration* it means "this variable is a pointer
to"; in an *expression* it means "the thing at this address". `int *pointer` declares a pointer;
`*pointer` dereferences one. Same character, two jobs, decided by position.

## Why the pointer's type matters

Every object pointer is the same size on mainstream platforms:

```c run
#include <stdio.h>

int main(void) {
    printf("sizeof(int *) == sizeof(char *): %d\n",
           (int)(sizeof(int *) == sizeof(char *)));
    printf("sizeof(void *) == sizeof(int *): %d\n",
           (int)(sizeof(void *) == sizeof(int *)));
    return 0;
}
```

```text
sizeof(int *) == sizeof(char *): 1
sizeof(void *) == sizeof(int *): 1
```

If they are all the same size, why does the type exist at all? Because the type is what tells the
compiler how to interpret the bytes and how far to move. `pointer + 1` on an `int *` advances four
bytes; on a `char *` it advances one. `*pointer` reads four bytes as an integer, or one byte as a
character. The type is not about the address, it is about what you find when you get there.

The standard guarantees that `void *` and `char *` share a representation and that any object pointer
can round-trip through a `void *`. It does not guarantee that `int *` and `char *` are the same size —
every platform you will use makes them so, but that is a fact about the platforms, not about C.

Because the type matters so much, getting it wrong is a real bug. In C it is only a warning:

```c warn
#include <stdio.h>

int main(void) {
    int count = 5;
    double *pointer = &count;

    printf("%f\n", *pointer);
    return 0;
}
```

```text
incompatible pointer types initializing 'double *' with an expression of type 'int *' [-Wincompatible-pointer-types]
```

The program builds and runs. It reads eight bytes as a `double` when only four were allocated, so it
consumes four bytes of whatever happens to sit next to `count`, and prints a number that is not 5 and
never was. This is the case that makes C++ worth the extra ceremony: the identical code is a hard
error there (Chapter 24), and you will not miss the warning-as-error once you have spent an afternoon
chasing a number that was never 5.

## Pointer arithmetic walks in elements

`pointer + n` moves by `n` *elements*, not `n` bytes, and subtracting two pointers gives a count of
elements. An array name in an expression becomes a pointer to its first element, which is why the two
notations are interchangeable.

```c run
#include <stdio.h>

int main(void) {
    int values[3] = {10, 20, 30};
    int *pointer = values;

    printf("*pointer       = %d\n", *pointer);
    printf("*(pointer + 2) = %d\n", *(pointer + 2));
    printf("pointer[1]     = %d\n", pointer[1]);
    printf("distance       = %d\n", (int)((pointer + 2) - pointer));
    return 0;
}
```

```text
*pointer       = 10
*(pointer + 2) = 30
pointer[1]     = 20
distance       = 2
```

`pointer + 2` adds eight bytes, not two, because the pointer is an `int *` and an `int` is four bytes.
And `pointer[1]` is defined as `*(pointer + 1)` — the subscript is not a different mechanism, it is
shorthand for the same arithmetic. That definition is why `2[pointer]` compiles and means the same
thing (it is `*(2 + pointer)`), and why you should never write it.

The distance is `2`, not `8`: subtracting two `int *` values gives the number of `int`s between them.
Arithmetic on pointers is only meaningful within one array — comparing or subtracting pointers into
different objects is undefined behaviour, though every platform will happily produce a number for you.

## const, and the two places it can go

`const` can protect either the value being pointed at or the pointer itself, and the two are written
differently:

```c run
#include <stdio.h>

int main(void) {
    int x = 1;
    int y = 2;

    const int *can_read = &x;   /* the pointed-to value is read-only */
    int *const fixed = &x;      /* the pointer itself is read-only */

    can_read = &y;              /* fine: the pointer may change */
    *fixed = 9;                 /* fine: the value may change */

    printf("x=%d y=%d *can_read=%d\n", x, y, *can_read);
    return 0;
}
```

```text
x=9 y=2 *can_read=2
```

Read the declarations from the name outwards. `const int *can_read` means "`can_read` is a pointer to
an `int` that is const", so you cannot write through it. `int *const fixed` means "`fixed` is a const
pointer to an `int`", so you cannot reseat it. Both compiled here, and the two assignments prove
which restriction each one carries. Writing through the first one is the error:

```c bad
#include <stdio.h>

int main(void) {
    int x = 1;
    const int *pointer = &x;

    *pointer = 5;
    return 0;
}
```

```text
error: read-only variable is not assignable
```

`const` on a pointer parameter is how a function promises not to modify your data, and it is worth
writing every time. A reader who sees `const int *values` knows the function will not touch the array;
a reader who sees `int *values` has to go and check.

## The stack and the heap

There are two places your data can live, and they behave differently.

**The stack** holds local variables and function frames. It is fast, it is automatic — memory is
reclaimed when the function returns — and it is small, typically 8 MB. You never call anything to get
stack memory and you never free it.

**The heap** is a large pool you request from explicitly with `malloc` and give back with `free`. It
survives the function that allocated it, which is exactly what you need when the size is not known
until runtime or the data must outlive the call. In exchange, you are responsible for every byte.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int on_stack = 1;
    int *on_heap = malloc(sizeof(int));

    if (on_heap == NULL) {
        return 1;
    }
    *on_heap = 2;

    printf("stack value %d, heap value %d\n", on_stack, *on_heap);
    printf("different locations: %d\n", (int)((void *)&on_stack != (void *)on_heap));

    free(on_heap);
    return 0;
}
```

```text
stack value 1, heap value 2
different locations: 1
```

The comparison needs the cast to `void *` because comparing an `int *` with an `int *` is fine but
printing the result of a pointer comparison is not — `%d` wants an `int`, and the `(int)` makes the
boolean explicit. Note also that the two values are genuinely in different places; the stack and the
heap are different regions of the address space, which is why a dangling pointer into the stack
usually still "works" for a while and a dangling heap pointer often does not.

## malloc and free

`malloc` takes a number of bytes and returns a `void *` to a fresh block, or `NULL` if it cannot
satisfy the request. `free` takes a pointer that came from `malloc` and releases it. Neither knows
about types, which is why you cast and why the size is written as a product.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int count = 5;
    int *values = malloc(sizeof(int) * (size_t)count);

    if (values == NULL) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    for (int i = 0; i < count; i++) {
        values[i] = i * i;
    }
    for (int i = 0; i < count; i++) {
        printf("%d ", values[i]);
    }
    printf("\n");

    free(values);
    return 0;
}
```

```text
0 1 4 9 16
```

Four habits are in that program, and each one is load-bearing. **Check for `NULL`** — allocation can
fail, and dereferencing `NULL` is the crash below. **Write the size as `sizeof(type) * count`** so the
count and the element size cannot drift apart, and cast the count to `size_t` so the multiplication is
done at a width that cannot overflow. **Free exactly once**, at the point where the data is no longer
needed. And note that `free` takes no size: the allocator remembers how big the block was, which is
why `free` on a pointer that did not come from `malloc` is undefined behaviour.

## The four ways to get it wrong

The compiler catches almost none of these. The sanitizer catches all four, which is why it is worth
running your tests with it on.

**One: dereferencing NULL.** A pointer that is `NULL` names no location, and reading it is undefined:

```c run-san-catch
#include <stdio.h>

int main(void) {
    int *pointer = NULL;

    printf("%d\n", *pointer);
    return 0;
}
```

```text
load of null pointer of type 'int'
```

On this platform UBSan reports the load and AddressSanitizer then reports a `SEGV`, because the null
page is deliberately unmapped. That crash is the *good* outcome — the bad outcome is a wild pointer
into a mapped page, which silently reads or overwrites unrelated data and corrupts something you will
not notice for a week.

**Two: using memory after freeing it.** `free` returns the block to the allocator; the pointer you
still hold is now dangling, and the allocator may have already handed that memory to somebody else:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = malloc(sizeof(int) * 4);

    if (values == NULL) {
        return 1;
    }
    values[0] = 42;
    free(values);

    printf("%d\n", values[0]);
    return 0;
}
```

```text
heap-use-after-free
```

AddressSanitizer reports exactly what happened, including the line that freed it and the line that
allocated it. That trace is the reason to use the tool: without it, this is a program that prints `42`
and looks correct.

**Three: freeing the same block twice.** The second `free` corrupts the allocator's bookkeeping:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = malloc(sizeof(int));

    if (values == NULL) {
        return 1;
    }
    free(values);
    free(values);
    return 0;
}
```

```text
attempting double-free
```

This one is nastier than use-after-free, because the damage is to the allocator rather than to your
data — the crash often happens much later, inside an unrelated allocation.

**Four: writing past the end of a block.** The allocator gave you exactly the bytes you asked for:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = malloc(sizeof(int) * 3);

    if (values == NULL) {
        return 1;
    }
    values[3] = 1;
    free(values);
    return 0;
}
```

```text
heap-buffer-overflow
```

Note that the program writes to `values[3]` on a three-element array and never reads it back, so
nothing about the output looks wrong. The sanitizer knows the block's real size and reports the write
immediately.

The fifth failure mode is the quiet one: **forgetting to free at all**. A leak does not crash and does
not corrupt anything; it just means the program's memory grows until it is killed.

```c run-san-leak
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = malloc(sizeof(int) * 100);

    if (values == NULL) {
        return 1;
    }
    values[0] = 1;
    printf("%d\n", values[0]);
    return 0;
}
```

```text
leak
```

**On macOS this block is not verified.** Apple's clang ships no LeakSanitizer, so the sanitizer here
detects heap overflows, use-after-free and double frees but not leaks. To see this one caught you need
Linux with `-fsanitize=address`, or Valgrind, which is not installed on the machine this book was
written on. This book's verification harness reports the block as **skipped** on macOS rather than
pretending it passed — a leak demonstration that nobody can reproduce is worse than no demonstration.

When the index is a constant, the compiler can catch an out-of-bounds access before you run anything:

```c warn
#include <stdio.h>

int main(void) {
    int values[3] = {1, 2, 3};

    printf("%d\n", values[5]);
    return 0;
}
```

```text
array index 5 is past the end of the array (that has type 'int[3]') [-Warray-bounds]
```

This works only because `5` is a literal. The moment the index comes from a loop variable, a file or
a user, the compiler cannot know and says nothing — which is why the sanitizer, not the compiler, is
the tool that catches array bugs in practice.

:::scenario The helper that returned a pointer into a dead frame
A developer needs a function that builds a short description string. Returning a pointer is the
convenient signature, so they write:

```c warn
#include <stdio.h>

static int *make_pointer(void) {
    int local = 5;
    return &local;
}

int main(void) {
    printf("%d\n", *make_pointer());
    return 0;
}
```

```text
address of stack memory associated with local variable 'local' returned [-Wreturn-stack-address]
```

`local` lives in `make_pointer`'s stack frame. The frame is popped the instant the function returns,
so the address being handed back names memory that is already free to be reused — by the next call,
by `printf`, by anything. In testing it often prints `5` anyway, because nothing has overwritten that
slot yet. In production it prints whatever the next function put there, and the value changes between
builds.

:::solution Let the caller own the memory
The function does not own a place to put the result, so it must not pretend to. Either return the
value itself, or take a buffer from the caller and fill it:

```c run
#include <stdio.h>

static void describe(char *buffer, size_t size) {
    snprintf(buffer, size, "reading %d", 42);
}

int main(void) {
    char buffer[32];

    describe(buffer, sizeof(buffer));
    printf("%s\n", buffer);
    return 0;
}
```

```text
reading 42
```

The caller owns `buffer`, so its lifetime is obvious and correct: it lives as long as `main`'s frame,
which is longer than any use of it. The function writes into it and returns nothing, so there is no
question about who frees what — nobody does, because nothing was allocated. `snprintf` takes the size
and refuses to write past it, which is the same contract `strcpy` does not offer.

The third option, when the result genuinely must outlive the call, is for the function to `malloc` and
for the caller to `free`. That works, but it splits the ownership across two functions and the rule
"whoever allocates, frees" is the first thing to get lost in a codebase. Chapter 28 replaces the whole
arrangement with `std::string` and `std::unique_ptr`, where the type carries the ownership and the
compiler enforces it. Until then, the caller-owns-the-buffer shape is the one to reach for.
:::

:::pitfall free does not clear your pointer
`free(pointer)` releases the memory. It does not change `pointer`, which still holds the old address
and is now dangling. Setting it to `NULL` yourself is the discipline that makes an accidental
re-dereference impossible — the `if` below would crash if the pointer were still live.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *pointer = malloc(sizeof(int));

    if (pointer == NULL) {
        return 1;
    }
    *pointer = 7;

    free(pointer);
    pointer = NULL;   /* free does NOT do this for you */

    if (pointer != NULL) {
        printf("%d\n", *pointer);
    }
    printf("done\n");
    return 0;
}
```

```text
done
```

The pair `free(p); p = NULL;` is the manual version of what a smart pointer does automatically. It is
two lines and easy to forget, which is exactly why every serious C codebase has a convention for it —
either always null after free, or never free outside a designated cleanup function. What you must not
do is free a pointer and leave it looking valid, because the next reader has no way to tell.

One warning about this pattern: nulling your copy does not null anybody else's. If three places hold
the same pointer, freeing it and nulling one leaves two dangling pointers that look fine. Ownership
has to be a decision you make once, not a habit you apply locally.
:::

## Key takeaways

- `&x` produces the address of `x`; `*p` reads or writes the value at the address in `p`. In a
  declaration `*` means "pointer to"; in an expression it means "the thing at".
- A pointer holds a copy of an address, so reassigning the pointer does not affect the variable it
  used to name.
- The pointer's type determines how far `p + 1` moves and how many bytes `*p` reads. All object
  pointers are the same width on mainstream platforms, but the type is not optional.
- In C, initialising a pointer of one type from a pointer of another is a warning, not an error, and
  the program will build and misread memory. In C++ it is an error.
- `p + n` moves by `n` elements; subtracting two pointers gives a count of elements, not bytes. Both
  are only defined within a single array.
- `const int *p` protects the value; `int *const p` protects the pointer. Writing through the first is
  a compile error.
- The stack is automatic, fast and small; the heap is explicit, survives the call, and is your
  responsibility.
- `malloc` returns `NULL` on failure and must be checked. Write the size as `sizeof(type) * count`,
  with the count cast to `size_t`.
- `free` takes no size, and only accepts pointers that came from `malloc`. `free(p); p = NULL;` is the
  safe pairing.
- The four memory bugs — null dereference, use-after-free, double free, out-of-bounds write — all
  build cleanly. AddressSanitizer and UBSan catch them; the compiler usually cannot.
- Leak detection does not exist in Apple's clang. On macOS you need Linux or Valgrind to see a leak
  reported, and this book's harness marks those blocks skipped rather than verified.
- A pointer to a local variable must never escape the function that owns the frame.

## Practice

- [ ] Declare an `int`, take its address, and print the value three ways: directly, through the
      pointer with `*`, and by comparing the pointer with `&value`.
- [ ] Declare `int values[5]`, take a pointer to the first element, and print every element using only
      `*(pointer + i)` — no subscript notation.
- [ ] Write a function `void double_all(int *values, size_t count)` that multiplies every element by
      two in place. Explain why the caller's array changes.
- [ ] Allocate an array of ten `int`s with `malloc`, fill it with squares, print it, and free it.
      Compile and run it with the sanitizers on.
- [ ] Deliberately write past the end of a `malloc`ed block and confirm the sanitizer names it. Then
      free the block twice and confirm the second report.
- [ ] Write a function that takes a buffer and its size and fills it with a message, the way
      `describe` does in this chapter. Then write the broken version that returns a pointer to a local
      and note the compiler's warning.

## Solutions

:::solution Exercise 3
The caller's array changes because the function is given its address, not a copy.

```c run
#include <stdio.h>

static void double_all(int *values, size_t count) {
    for (size_t i = 0; i < count; i++) {
        values[i] *= 2;
    }
}

int main(void) {
    int values[5] = {1, 2, 3, 4, 5};
    size_t count = sizeof(values) / sizeof(values[0]);

    double_all(values, count);

    for (size_t i = 0; i < count; i++) {
        printf("%d ", values[i]);
    }
    printf("\n");
    return 0;
}
```

```text
2 4 6 8 10
```

From Chapter 6, arguments are passed by value — but the value being copied here is a *pointer*, and a
copy of an address still names the same memory. So `values[i] *= 2` writes to the caller's array, and
the change survives the return. This is the mechanism behind every function in the standard library
that modifies its input, and it is also why the parameter should be `const int *` on any function that
only reads.
:::

:::solution Exercise 4
Allocate, fill, print, free — with the sanitizers watching.

```c run-san
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 10;
    int *squares = malloc(sizeof(int) * count);

    if (squares == NULL) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    for (size_t i = 0; i < count; i++) {
        squares[i] = (int)(i * i);
    }
    for (size_t i = 0; i < count; i++) {
        printf("%d ", squares[i]);
    }
    printf("\n");

    free(squares);
    return 0;
}
```

```text
0 1 4 9 16 25 36 49 64 81
```

This block carries the `run-san` directive, so the harness compiles it with AddressSanitizer and
UndefinedBehaviorSanitizer and requires the run to be *clean* — no overflow, no use-after-free, no
leak of the wrong kind. The `size_t` loop variable matters: `sizeof(int) * count` is a `size_t`
expression, and indexing with an `int` would introduce the signed/unsigned mismatch from Chapter 3.
Note that `i * i` is computed in `size_t` and cast down to `int` at the assignment; for values this
small the cast is exact, and for larger ones it would be the overflow trap from Chapter 3.
:::

:::solution Exercise 6
Give the caller's buffer to the function, and let the compiler warn you about the other shape.

```c run
#include <stdio.h>

static void format_status(char *buffer, size_t size, int code) {
    snprintf(buffer, size, "status %d", code);
}

int main(void) {
    char buffer[64];

    format_status(buffer, sizeof(buffer), 404);
    printf("%s\n", buffer);
    return 0;
}
```

```text
status 404
```

The function writes into memory it did not allocate and does not own, and it takes the size so it can
refuse to overrun it — `snprintf` returns the number of characters it *would* have written, which is
how you detect truncation when it matters. The broken version from the scenario is worth comparing
directly: change the return type to `char *` and return a local array, and the compiler says
`address of stack memory associated with local variable ... returned [-Wreturn-stack-address]`. That
warning is on by default, so `-Werror` turns it into a build failure — one of the few memory bugs you
get for free.
:::
