---
chapter: 12
part: 2
title: Dynamic Memory
summary: Grow a buffer while the program runs, understand what realloc does to your pointers, and learn the ownership rules that decide who frees what — including the multiplication bug that turns a size check into a heap overflow.
minutes: 65
tags: [malloc, calloc, realloc, free, ownership, dynamic-array, heap-overflow]
---

Chapter 7 introduced `malloc` and `free` as a way to get memory that outlives a function. That is only
half of why the heap exists. The other half is *size*: an array's length is fixed when you write the
declaration, and almost every real program learns how much data it has at runtime — a file's line count,
a user's input, the number of records in a response. This chapter is about buffers that grow, which is
where `realloc` earns its reputation as the most misunderstood function in C: it can move your data to
a new address, it can fail and leave you holding a pointer you must still free, and both of those facts
have produced bugs in every C codebase that has ever been written.

## The size you do not know until it runs

You already know the shape: ask for bytes, check the answer, use it, give it back.

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 6;
    int *values = malloc(sizeof(int) * count);

    if (values == NULL) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    int total = 0;

    for (size_t i = 0; i < count; i++) {
        values[i] = (int)(i * i);
        total += values[i];
    }
    for (size_t i = 0; i < count; i++) {
        printf("[%d]", values[i]);
    }
    printf("\nsum = %d\n", total);

    free(values);
    return 0;
}
```

```text
[0][1][4][9][16][25]
sum = 55
```

In this program `count` is a literal, so an array would have done. The point is that nothing in the code
above would change if `count` came from `argc`, from a file, or from a `scanf` — that is the property
you are buying. The three habits from Chapter 7 still apply and still matter: check for `NULL`, write the
size as `sizeof(type) * count`, and free exactly once.

## calloc, and what malloc does not promise

`calloc` takes a count and an element size rather than a byte count, and it zeroes the memory it returns.
`malloc` does not:

```c run
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(void) {
    int *raw = malloc(sizeof(int) * 4);
    int *zeroed = calloc(4, sizeof(int));

    if (raw == NULL || zeroed == NULL) {
        free(raw);
        free(zeroed);
        return 1;
    }

    printf("aligned to 16: %d\n", ((uintptr_t)raw % 16) == 0);
    printf("calloc zeroed: %d %d %d %d\n", zeroed[0], zeroed[1], zeroed[2], zeroed[3]);

    free(raw);
    free(zeroed);
    return 0;
}
```

```text
aligned to 16: 1
calloc zeroed: 0 0 0 0
```

The first line is worth knowing: `malloc` guarantees the block is aligned suitably for any type, which
on this 64-bit platform means a sixteen-byte boundary. That is why a `malloc`ed block can hold a
`double` or a struct without complaint, and why you never need to align anything yourself.

The second line is `calloc`'s whole reason to exist. `malloc` returns memory containing whatever was
there before, and reading it is not a crash — it is just a value that means nothing:

```c run-san
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *raw = malloc(sizeof(int) * 4);
    int *zeroed = calloc(4, sizeof(int));

    if (raw == NULL || zeroed == NULL) {
        free(raw);
        free(zeroed);
        return 1;
    }

    printf("malloc[0] as hex = %08x\n", (unsigned)raw[0]);
    printf("calloc[0]        = %d\n", zeroed[0]);

    free(raw);
    free(zeroed);
    return 0;
}
```

```text
malloc[0] as hex = bebebebe
calloc[0]        = 0
```

**That `bebebebe` is AddressSanitizer's doing, not C's.** With the sanitizer on, freshly allocated heap
memory is filled with the byte `0xBE` precisely so that a program which reads uninitialised memory gets
an obviously wrong answer instead of a plausible one. Without the sanitizer you would see whatever the
allocator last had at that address — often zeros, which is the worst possible outcome, because the
program appears to work and then stops working when the allocation pattern changes. If you need zeros,
ask for them with `calloc`; do not rely on getting them for free.

## realloc, and the two things it does

`realloc(pointer, new_size)` returns a block of at least `new_size` bytes containing the old contents up
to the smaller of the two sizes. The old block is freed if it moved. It also accepts `NULL` as a
pointer, which makes it a `malloc`, and `free(NULL)` is always safe:

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = realloc(NULL, sizeof(int) * 4);

    if (values == NULL) {
        return 1;
    }
    for (int i = 0; i < 4; i++) {
        values[i] = (i + 1) * 10;
    }
    printf("realloc(NULL, n): [%d][%d][%d][%d]\n", values[0], values[1], values[2], values[3]);

    free(values);
    free(NULL);
    printf("free(NULL) is safe\n");
    return 0;
}
```

```text
realloc(NULL, n): [10][20][30][40]
free(NULL) is safe
```

Those two behaviours mean you can write one function that handles "create" and "grow" without a special
case for the first call — which is exactly what the growable array below does.

Growing preserves the contents, and shrinking keeps the prefix:

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 4;
    int *values = malloc(sizeof(int) * count);

    if (values == NULL) {
        return 1;
    }
    for (size_t i = 0; i < count; i++) {
        values[i] = (int)(i + 1);
    }

    size_t bigger = 8;
    int *grown = realloc(values, sizeof(int) * bigger);

    if (grown == NULL) {
        free(values);
        return 1;
    }
    values = grown;
    for (size_t i = count; i < bigger; i++) {
        values[i] = (int)(i + 1);
    }
    for (size_t i = 0; i < bigger; i++) {
        printf("[%d]", values[i]);
    }
    printf("\n");

    int *smaller = realloc(values, sizeof(int) * 3);

    if (smaller == NULL) {
        free(values);
        return 1;
    }
    values = smaller;
    for (size_t i = 0; i < 3; i++) {
        printf("[%d]", values[i]);
    }
    printf("\n");

    free(values);
    return 0;
}
```

```text
[1][2][3][4][5][6][7][8]
[1][2][3]
```

The assignment `values = grown` on the line after the check is the pattern to memorise. The reason is
the second thing `realloc` does: **it may return a different address**. When the block cannot be extended
where it is, the allocator copies your data somewhere else and frees the original. Any pointer you kept
to the old block is now dangling, and the compiler will not warn you:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = malloc(sizeof(int) * 4);

    if (values == NULL) {
        return 1;
    }
    int *before = values;

    for (int i = 0; i < 4; i++) {
        values[i] = i;
    }

    int *grown = realloc(values, sizeof(int) * 100000);

    if (grown == NULL) {
        free(values);
        return 1;
    }

    printf("moved: %d\n", grown != before);
    printf("before[0] = %d\n", before[0]);
    free(grown);
    return 0;
}
```

```text
heap-use-after-free
```

The program printed `moved: 1` — the block really did relocate — and then read through `before`, which
now names freed memory. AddressSanitizer catches it immediately and prints the allocation and free sites.
The lesson generalises further than `realloc`: **any address you stored into a buffer is invalidated by
a reallocation of that buffer**, including pointers you handed to other parts of your program. That is
the strongest practical argument for growing a buffer rarely and in large steps rather than often and in
small ones.

## The multiplication that wraps

The size you pass to `malloc` is a `size_t`, and `size_t` arithmetic wraps silently. When both the count
and the element size come from outside your program, the product can overflow and give you a small number:

```c run
#include <stdio.h>

int main(void) {
    size_t count = (size_t)1 << 62;

    printf("count * sizeof(int) = %zu\n", count * sizeof(int));
    printf("SIZE_MAX            = %zu\n", (size_t)-1);
    return 0;
}
```

```text
count * sizeof(int) = 0
SIZE_MAX            = 18446744073709551615
```

`2^62` times four is `2^64`, which does not fit in a 64-bit `size_t`, so the product wraps to exactly
zero. `malloc(0)` is legal and returns a pointer to a zero-byte block — a *valid* pointer, not `NULL` —
so a `NULL` check does not save you, and the first write lands outside the allocation:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = (size_t)1 << 62;
    int *values = malloc(count * sizeof(int));

    if (values == NULL) {
        fprintf(stderr, "allocation failed\n");
        return 1;
    }
    values[0] = 1;
    printf("wrote %d\n", values[0]);
    free(values);
    return 0;
}
```

```text
heap-buffer-overflow
```

This is the shape of a large family of real security bugs: an attacker supplies a large count, the
multiplication wraps, a small buffer is allocated, and a loop writes past the end of it. The defence is
to check the multiplication itself, before it happens:

```c run
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int *allocate_ints(size_t count) {
    if (count > SIZE_MAX / sizeof(int)) {
        return NULL;
    }
    return malloc(sizeof(int) * count);
}

int main(void) {
    size_t huge = (size_t)1 << 62;

    printf("huge rejected: %d\n", allocate_ints(huge) == NULL);
    printf("small allowed: %d\n", allocate_ints(10) != NULL);
    return 0;
}
```

```text
huge rejected: 1
small allowed: 1
```

`count > SIZE_MAX / sizeof(int)` is the division form of `count * sizeof(int) > SIZE_MAX`, and it is the
version to write because the multiplication in the original expression is the thing that overflows. It
costs one comparison per allocation. Note that `allocate_ints(10)` leaks the block it returns — in real
code the caller owns it, which brings us to the part of this chapter that has nothing to do with
pointers and everything to do with design.

## Ownership: who frees what

Every `malloc` must be matched by exactly one `free`, and the hard part is not remembering to free — it
is deciding *which function* is responsible. Three rules cover almost every case.

**Whoever allocates, frees** — unless the allocation is explicitly handed over. A function that
allocates and returns a pointer is saying "you own this now", and the caller must free it. A function
that fills a buffer it was given does not own anything and frees nothing. Both are fine; mixing them in
one codebase without a convention is not.

**Free in the reverse order of allocation.** For a two-dimensional array that means rows first, then the
array of row pointers:

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t rows = 3;
    size_t cols = 4;
    int **grid = malloc(rows * sizeof(int *));

    if (grid == NULL) {
        return 1;
    }
    for (size_t r = 0; r < rows; r++) {
        grid[r] = malloc(cols * sizeof(int));
        if (grid[r] == NULL) {
            return 1;
        }
        for (size_t c = 0; c < cols; c++) {
            grid[r][c] = (int)(r * cols + c);
        }
    }

    for (size_t r = 0; r < rows; r++) {
        for (size_t c = 0; c < cols; c++) {
            printf("%3d", grid[r][c]);
        }
        printf("\n");
    }

    for (size_t r = 0; r < rows; r++) {
        free(grid[r]);
    }
    free(grid);
    return 0;
}
```

```text
  0  1  2  3
  4  5  6  7
  8  9 10 11
```

Four allocations and four frees. Freeing `grid` first would lose the row pointers before you could free
them — a leak of three blocks — and then reading `grid[r]` to free them anyway would be a use-after-free.
The `%3d` in the format string is there so the columns line up whatever the numbers are.

**Null after free, and free through a helper.** The pair `free(p); p = NULL;` from Chapter 7 is the
manual version of what a smart pointer does automatically, and it is what makes a second `free` harmless
rather than fatal.

## A buffer that grows

Put `realloc` and the ownership rules together and you get the data structure the C++ standard library
calls `std::vector`: a pointer, a count, and a capacity, where the capacity doubles when it runs out.

```c run
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;
    size_t count;
    size_t capacity;
} IntList;

static int list_push(IntList *list, int value) {
    if (list->count == list->capacity) {
        size_t next = (list->capacity == 0) ? 1 : list->capacity * 2;
        int *grown = realloc(list->data, next * sizeof(int));

        if (grown == NULL) {
            return 0;
        }
        list->data = grown;
        list->capacity = next;
    }
    list->data[list->count] = value;
    list->count++;
    return 1;
}

static void list_free(IntList *list) {
    free(list->data);
    list->data = NULL;
    list->count = 0;
    list->capacity = 0;
}

int main(void) {
    IntList list = {NULL, 0, 0};

    for (int i = 1; i <= 9; i++) {
        if (!list_push(&list, i * 10)) {
            list_free(&list);
            return 1;
        }
        printf("after %d: count=%zu capacity=%zu\n", i, list.count, list.capacity);
    }

    for (size_t i = 0; i < list.count; i++) {
        printf("%d ", list.data[i]);
    }
    printf("\n");

    list_free(&list);
    return 0;
}
```

```text
after 1: count=1 capacity=1
after 2: count=2 capacity=2
after 3: count=3 capacity=4
after 4: count=4 capacity=4
after 5: count=5 capacity=8
after 6: count=6 capacity=8
after 7: count=7 capacity=8
after 8: count=8 capacity=8
after 9: count=9 capacity=16
10 20 30 40 50 60 70 80 90
```

Four details make this correct rather than nearly correct. `realloc(NULL, n)` is a `malloc`, so the first
push needs no special case. The result goes into a temporary `grown` and only then into `list->data`, so
a failed `realloc` leaves the original pointer intact and freeable. `next` is computed from `capacity`,
never from `count`, so the array never grows by one and never reallocates on every push — doubling gives
amortised constant time per push, which is why `std::vector` does the same thing. And `list_free` nulls
the fields, so a second call is harmless.

The `count` and `capacity` being separate is the whole trick: `count` is what the caller sees, `capacity`
is what has been paid for. Chapter 28 replaces this struct with `std::vector<int>` and deletes the file,
but the doubling strategy survives unchanged — it is a fact about arrays, not about C.

## Duplicating a string

A function that returns a copy of a string is the smallest complete example of the allocate-and-hand-over
pattern:

```c run
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *duplicate(const char *source) {
    size_t size = strlen(source) + 1;
    char *copy = malloc(size);

    if (copy == NULL) {
        return NULL;
    }
    memcpy(copy, source, size);
    return copy;
}

int main(void) {
    char *copy = duplicate("hello");

    if (copy == NULL) {
        return 1;
    }
    printf("%s (%zu bytes)\n", copy, strlen(copy) + 1);

    free(copy);
    return 0;
}
```

```text
hello (6 bytes)
```

The `+ 1` is the terminator, and it is the single most commonly forgotten byte in C. `memcpy` is used
rather than `strcpy` because the length is already known, so there is no reason to walk the string twice
— and because passing a length means the function cannot overrun, which is the property the previous
chapter spent so long on. POSIX systems also provide `strdup`, which does exactly this; it is not part of
the C standard, so a program that needs to be portable should write the six lines above instead.

## The leak

The failure mode that does not crash. A function allocates, returns the pointer, the caller uses it and
drops it, and the block stays allocated until the process exits:

```c run-san-leak
#include <stdio.h>
#include <stdlib.h>

static int *make_buffer(void) {
    int *buffer = malloc(sizeof(int) * 1024);

    if (buffer != NULL) {
        buffer[0] = 1;
    }
    return buffer;
}

int main(void) {
    for (int i = 0; i < 3; i++) {
        int *buffer = make_buffer();

        if (buffer == NULL) {
            return 1;
        }
        printf("request %d: %d\n", i + 1, buffer[0]);
    }
    return 0;
}
```

```text
leak
```

**On macOS this block is not verified.** Apple's clang ships no LeakSanitizer, so the sanitizer used
throughout this book detects heap overflows, use-after-free and double frees but not leaks. To see this
one reported you need Linux with `-fsanitize=address`, or Valgrind, which is not installed on the machine
this book was written on. This book's verification harness reports the block as **skipped** here rather
than pretending it passed.

The reason a leak is worth a section despite being invisible is that it is the memory bug that survives
testing and reaches production. Three iterations leak twelve kilobytes and nobody notices. A server that
handles a million requests with the same twelve-kilobyte leak exhausts its memory and is killed by the
kernel, and the stack trace tells you nothing. Every allocation needs an owner, and the owner needs to
be a decision you made on purpose.

:::scenario The struct copy that made two owners of one buffer
A developer adds a small string type, fills one in, and takes a copy so it can be modified independently.
The program prints both strings correctly and then dies inside `free`:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char *text;
} Str;

int main(void) {
    Str a;

    a.text = malloc(16);
    if (a.text == NULL) {
        return 1;
    }
    snprintf(a.text, 16, "%s", "hello");

    Str b = a;
    printf("a = %s, b = %s\n", a.text, b.text);

    free(a.text);
    free(b.text);
    return 0;
}
```

```text
attempting double-free
```

Chapter 11 said a struct assignment copies every byte. For a struct containing an *array* that is exactly
what you want. For a struct containing a *pointer*, copying the bytes copies the address — so `a` and `b`
now point at one buffer, and the two `free` calls are the same `free` twice. The output line proves the
bug is invisible from the outside: both names print correctly, and there is nothing in `a = hello, b =
hello` to suggest that `b` is not a separate object.

This is the distinction between a **shallow copy**, which duplicates the pointer, and a **deep copy**,
which duplicates what it points at. C does shallow copies for struct assignment and gives you no way to
change that, so a struct with a pointer member needs its own copy function — and, by the ownership rule,
its own free function.

:::solution Give the type its own init, copy and free
Three functions, named so the ownership is obvious at every call site:

```c run
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *text;
    size_t capacity;
} Str;

static int str_init(Str *s, const char *source) {
    s->capacity = strlen(source) + 1;
    s->text = malloc(s->capacity);

    if (s->text == NULL) {
        s->capacity = 0;
        return 0;
    }
    memcpy(s->text, source, s->capacity);
    return 1;
}

static int str_copy(Str *destination, const Str *source) {
    return str_init(destination, source->text);
}

static void str_free(Str *s) {
    free(s->text);
    s->text = NULL;
    s->capacity = 0;
}

int main(void) {
    Str a;

    if (!str_init(&a, "hello")) {
        return 1;
    }

    Str b;

    if (!str_copy(&b, &a)) {
        str_free(&a);
        return 1;
    }

    b.text[0] = 'H';
    printf("a = %s\n", a.text);
    printf("b = %s\n", b.text);

    str_free(&a);
    str_free(&b);
    return 0;
}
```

```text
a = hello
b = Hello
```

Now the two structs own two buffers, changing one leaves the other alone, and each `free` is matched to
its own allocation. `str_copy` is one line because it delegates to `str_init` — a copy is just an
initialise from an existing string, and writing it that way means the `+ 1` and the `memcpy` exist in
exactly one place. `str_free` nulls the pointer and zeroes the capacity, so a double free is harmless
and a use after free reads through a `NULL` rather than into recycled memory.

The naming carries the contract: `str_init` and `str_copy` return an `int` because they can fail, and
every failure path in `main` frees what it has already taken. That last part is easy to skip and is the
difference between a program that leaks under memory pressure and one that does not.
:::

:::pitfall free only accepts the exact pointer malloc returned
Passing an interior pointer — an address into the middle of a block — is not a near miss that happens to
work. The allocator keeps bookkeeping immediately before the block, and it looks there for the size:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *values = malloc(sizeof(int) * 4);

    if (values == NULL) {
        return 1;
    }
    free(values + 1);
    return 0;
}
```

```text
attempting free on address which was not malloc()-ed
```

The mistake is easy to make when a loop advances a pointer rather than an index. `for (p = values; p <
values + n; p++)` moves `p`, and if you then write `free(p)` after the loop you are freeing one past the
end. The fix is to keep the original: either iterate with an index, or keep a second pointer that never
moves and free that one. The same rule applies to `realloc` — it also requires a pointer that came from
`malloc`, `calloc` or `realloc` and was never advanced.
:::

## Key takeaways

- The heap exists for sizes you learn at runtime. `malloc(sizeof(type) * count)` plus a `NULL` check
  plus one `free` is the shape.
- `malloc` does not zero its memory and the alignment it returns is suitable for any type. Use `calloc`
  when you need zeros; never rely on getting them by accident.
- `realloc(NULL, n)` is `malloc(n)`, and `free(NULL)` is safe, so one code path can handle both create
  and grow.
- `realloc` may return a different address and frees the old block when it moves. Always assign the
  result to a temporary, check it, then assign to your pointer. Any other pointer into the old block is
  now dangling.
- `size_t` arithmetic wraps silently. Check `count > SIZE_MAX / sizeof(type)` before multiplying, because
  `malloc(0)` returns a valid pointer and a `NULL` check will not catch the wrap.
- Growing preserves contents; shrinking keeps the prefix.
- Whoever allocates frees, unless the allocation is handed over by a documented contract. Free in the
  reverse order of allocation — rows before the array of row pointers.
- `free` accepts only the exact pointer `malloc` returned. An interior pointer is a hard error, so keep
  the original when a loop advances a pointer.
- A growable array is a pointer, a count and a capacity, with the capacity doubling. Compute the next
  capacity from the capacity, not the count.
- Struct assignment is a shallow copy. A struct with a pointer member needs its own init, copy and free
  functions, because two structs holding one pointer is two owners of one buffer.
- A leak does not crash. Leak detection does not exist in Apple's clang, so on macOS this book's harness
  marks leak blocks skipped rather than verified.

## Practice

- [ ] Allocate an array of twenty `int`s with `calloc`, fill it with the first twenty squares, print it,
      and free it. Compile with `-fsanitize=address,undefined` and confirm the run is clean.
- [ ] Write `static int *resize_ints(int *old, size_t old_count, size_t new_count)` that grows or shrinks
      a block with `realloc`, zero-filling any new elements. It must not leak `old` if the `realloc`
      fails.
- [ ] Write `static size_t count_lines(const char *text)` and a `duplicate` function, then build a
      program that duplicates a string, uppercases the copy, and prints both — freeing both.
- [ ] Extend `IntList` with a `list_at(const IntList *list, size_t index)` that returns a pointer to an
      element or `NULL` when the index is out of range. Explain why returning a pointer is safe here but
      would not be if the function returned a pointer to a local.
- [ ] Deliberately write past the end of a `malloc`ed block of ten `int`s and confirm the sanitizer names
      it. Then fix the loop bound and confirm the run is clean.
- [ ] Write a `Matrix` type that owns `rows * cols` `int`s in a single allocation, with `matrix_init`,
      `matrix_at` and `matrix_free`. Explain why one allocation is better than an array of row pointers
      when the row count is fixed.

## Solutions

:::solution Exercise 1
`calloc` takes the count and the element size, and hands back zeros.

```c run-san
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 20;
    int *squares = calloc(count, sizeof(int));

    if (squares == NULL) {
        return 1;
    }

    for (size_t i = 0; i < count; i++) {
        squares[i] = (int)(i * i);
    }
    for (size_t i = 0; i < count; i++) {
        printf("%s%d", i == 0 ? "" : " ", squares[i]);
    }
    printf("\n");

    free(squares);
    return 0;
}
```

```text
0 1 4 9 16 25 36 49 64 81 100 121 144 169 196 225 256 289 324 361
```

The block carries `run-san`, so the harness compiles it with AddressSanitizer and UndefinedBehaviorSanitizer
and requires a clean run — no overflow, no use-after-free, no invalid free. `calloc(count, sizeof(int))`
says the same thing as `malloc(sizeof(int) * count)` and additionally guarantees zeros, which is the right
choice when the array is going to be read before it is fully written. The `%s` trick in the print loop
avoids a trailing space in the output: the first element is prefixed with nothing and every later one with
a space. Printing that space unconditionally would leave one at the end of the line, which is the kind of
detail that makes an output fence in a book disagree with the program.
:::

:::solution Exercise 2
Take the old pointer and both sizes, and never lose the original on failure.

```c run
#include <stdio.h>
#include <stdlib.h>

static int *resize_ints(int *old, size_t old_count, size_t new_count) {
    int *resized = realloc(old, new_count * sizeof(int));

    if (resized == NULL) {
        return NULL;
    }
    for (size_t i = old_count; i < new_count; i++) {
        resized[i] = 0;
    }
    return resized;
}

int main(void) {
    size_t count = 3;
    int *values = malloc(count * sizeof(int));

    if (values == NULL) {
        return 1;
    }
    for (size_t i = 0; i < count; i++) {
        values[i] = (int)(i + 1);
    }

    size_t bigger = 6;
    int *grown = resize_ints(values, count, bigger);

    if (grown == NULL) {
        free(values);
        return 1;
    }
    values = grown;

    for (size_t i = 0; i < bigger; i++) {
        printf("[%d]", values[i]);
    }
    printf("\n");

    free(values);
    return 0;
}
```

```text
[1][2][3][0][0][0]
```

The function returns `NULL` and does **not** free `old` when `realloc` fails, because it cannot know
whether the caller has another use for it — ownership stays with the caller until the new pointer is in
their hands. `main` then does the free itself on the failure path, which is why the `if (grown == NULL)`
branch calls `free(values)` before returning. Zero-filling from `old_count` upward is what makes the new
elements well-defined: `realloc` leaves the extra space uninitialised exactly like `malloc` does, and the
`for` loop is the `calloc` behaviour applied only to the part that needs it.
:::

:::solution Exercise 3
Duplicate first, modify the copy, and free it when both are done being used.

```c run
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *duplicate(const char *source) {
    size_t size = strlen(source) + 1;
    char *copy = malloc(size);

    if (copy == NULL) {
        return NULL;
    }
    memcpy(copy, source, size);
    return copy;
}

static size_t count_lines(const char *text) {
    size_t lines = 0;

    for (size_t i = 0; text[i] != '\0'; i++) {
        if (text[i] == '\n') {
            lines++;
        }
    }
    return lines;
}

int main(void) {
    const char *source = "first\nsecond\nthird";
    char *copy = duplicate(source);

    if (copy == NULL) {
        return 1;
    }

    for (size_t i = 0; copy[i] != '\0'; i++) {
        if (copy[i] >= 'a' && copy[i] <= 'z') {
            copy[i] = (char)(copy[i] - 'a' + 'A');
        }
    }

    printf("original: %s\n", source);
    printf("copy:     %s\n", copy);
    printf("lines:    %zu\n", count_lines(source));

    free(copy);
    return 0;
}
```

```text
original: first
second
third
copy:     FIRST
SECOND
THIRD
lines:    2
```

The `source` pointer points at a string literal, which lives in read-only memory — writing to it directly
would be the `DEADLYSIGNAL` crash from Chapter 10. Duplicating onto the heap is what makes the uppercase
loop legal, and it is the reason the function exists at all. Note that `source` is printed unchanged after
the loop, which is the proof that the copy is a real copy. `count_lines` returns `2` rather than `3`
because it counts *separators*: three lines separated by two newlines. If you want the number of lines
with no trailing newline, that is `count + 1` when the text is non-empty, and getting this distinction
wrong is the classic off-by-one in every log-processing script ever written.
:::

:::solution Exercise 4
Bounds-check, then hand back the address of the element.

```c run
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;
    size_t count;
    size_t capacity;
} IntList;

static int list_push(IntList *list, int value) {
    if (list->count == list->capacity) {
        size_t next = (list->capacity == 0) ? 1 : list->capacity * 2;
        int *grown = realloc(list->data, next * sizeof(int));

        if (grown == NULL) {
            return 0;
        }
        list->data = grown;
        list->capacity = next;
    }
    list->data[list->count] = value;
    list->count++;
    return 1;
}

static int *list_at(const IntList *list, size_t index) {
    if (index >= list->count) {
        return NULL;
    }
    return &list->data[index];
}

int main(void) {
    IntList list = {NULL, 0, 0};

    for (int i = 1; i <= 5; i++) {
        if (!list_push(&list, i * i)) {
            free(list.data);
            return 1;
        }
    }

    int *third = list_at(&list, 2);

    if (third != NULL) {
        printf("index 2 = %d\n", *third);
    }
    printf("index 9 is null: %d\n", list_at(&list, 9) == NULL);

    free(list.data);
    return 0;
}
```

```text
index 2 = 9
index 9 is null: 1
```

Returning `&list->data[index]` is safe because the element lives in the heap block, which outlives the
function — the pointer names memory the caller already owns through `list`. Contrast the broken version
from Chapter 7, where a function returned the address of a *local*: that memory belonged to a frame that
was destroyed on return, so the pointer named nothing. The difference is ownership, not syntax. Note
that the pointer is invalidated by the next `list_push` that triggers a reallocation, which is the
`realloc` hazard from earlier in this chapter, and is why `list_at` should be used rather than the
pointer being stored.
:::

:::solution Exercise 5
The wrong bound first, so the sanitizer can name it, then the fix.

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 10;
    int *values = malloc(sizeof(int) * count);

    if (values == NULL) {
        return 1;
    }
    for (size_t i = 0; i <= count; i++) {
        values[i] = (int)i;
    }
    printf("last = %d\n", values[count - 1]);
    free(values);
    return 0;
}
```

```text
heap-buffer-overflow
```

`i <= count` runs eleven times over a ten-element block. Note that nothing about the program looks wrong
and nothing crashes on its own: the eleventh write lands in the allocator's bookkeeping, the `printf`
reads a value that is in range, and without a sanitizer this would appear to work. That is the point of
the exercise — the bug is a one-character difference in a loop condition, and the only reliable way to
find it is to run with the sanitizer on. The fix is `<` instead of `<=`:

```c run-san
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t count = 10;
    int *values = malloc(sizeof(int) * count);

    if (values == NULL) {
        return 1;
    }
    for (size_t i = 0; i < count; i++) {
        values[i] = (int)i;
    }
    printf("last = %d\n", values[count - 1]);
    free(values);
    return 0;
}
```

```text
last = 9
```

The two blocks differ by one character, and the harness verifies both: the first must be *caught* by the
sanitizer and the second must run *clean*. That pairing is the whole argument for putting the sanitizer in
your build rather than reaching for it after a crash — the buggy version and the fixed version produce
identical output on a machine without one.
:::

:::solution Exercise 6
One allocation, one free, and an index computed from the row and column.

```c run
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;
    size_t rows;
    size_t cols;
} Matrix;

static int matrix_init(Matrix *m, size_t rows, size_t cols) {
    if (rows == 0 || cols == 0 || rows > SIZE_MAX / cols / sizeof(int)) {
        return 0;
    }
    m->data = malloc(rows * cols * sizeof(int));
    if (m->data == NULL) {
        m->rows = 0;
        m->cols = 0;
        return 0;
    }
    m->rows = rows;
    m->cols = cols;
    return 1;
}

static int *matrix_at(Matrix *m, size_t row, size_t col) {
    if (row >= m->rows || col >= m->cols) {
        return NULL;
    }
    return &m->data[row * m->cols + col];
}

static void matrix_free(Matrix *m) {
    free(m->data);
    m->data = NULL;
    m->rows = 0;
    m->cols = 0;
}

int main(void) {
    Matrix m;

    if (!matrix_init(&m, 2, 3)) {
        return 1;
    }

    for (size_t r = 0; r < m.rows; r++) {
        for (size_t c = 0; c < m.cols; c++) {
            *matrix_at(&m, r, c) = (int)(r * m.cols + c);
        }
    }

    for (size_t r = 0; r < m.rows; r++) {
        for (size_t c = 0; c < m.cols; c++) {
            printf("%3d", *matrix_at(&m, r, c));
        }
        printf("\n");
    }

    printf("out of range is null: %d\n", matrix_at(&m, 5, 0) == NULL);
    matrix_free(&m);
    return 0;
}
```

```text
  0  1  2
  3  4  5
out of range is null: 1
```

One allocation means one `free`, and that is the argument. The array-of-rows version needs `rows + 1`
allocations and `rows + 1` frees in the right order, and every one of them is a chance to get the order
wrong or to forget one. The cost is that the index has to be computed by hand — `row * cols + col` —
rather than written as `m[row][col]`, and the type has to carry `cols` so the arithmetic is possible.
The overflow check multiplies nothing until it has divided first: `rows > SIZE_MAX / cols / sizeof(int)`
rejects a pair of dimensions whose product would wrap, which is the same defence as `allocate_ints` in
the chapter, applied to two unknowns instead of one. The `rows == 0 || cols == 0` guard is there because
a zero-sized matrix has no useful interpretation and `malloc(0)` would hand back a valid pointer to
nothing.
:::
