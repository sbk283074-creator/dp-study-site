---
chapter: 10
part: 2
title: Arrays and Strings
summary: Store many values under one name, pass them to functions without losing their length, and handle text — which in C is just an array of characters with a zero on the end, and the single richest source of bugs in the language.
minutes: 60
tags: [arrays, strings, strlen, strcmp, strncpy, snprintf, buffer-overflow]
---

A pointer names one place. An array names a run of places, and C gives you the arithmetic to walk
along it and nothing else — no length, no bounds check, no growth. Text is built on top of that same
mechanism: a string is an array of `char` with a zero byte marking the end, and every string function
in the standard library is a loop that trusts you to have put that zero in the right place. This is
the chapter where C's compactness stops being charming, because the mistakes here do not produce
wrong numbers, they produce programs that read and write memory they do not own.

## An array is a fixed run of elements

An array declaration states a type and a count. The count is fixed at compile time, and the elements
sit next to each other in memory with no gaps.

```c run
#include <stdio.h>

int main(void) {
    int values[5] = {10, 20, 30, 40, 50};
    size_t count = sizeof(values) / sizeof(values[0]);
    int total = 0;

    for (size_t i = 0; i < count; i++) {
        total += values[i];
    }
    printf("count = %zu\n", count);
    printf("total = %d\n", total);
    return 0;
}
```

```text
count = 5
total = 150
```

`sizeof(values)` is the size of the whole array in bytes — twenty, not five. Dividing by the size of
one element gives the element count, and writing it as `sizeof(values) / sizeof(values[0])` rather
than the literal `5` means the loop bound cannot drift when you add a sixth value. That idiom is
everywhere in real C, and it is worth typing out every time.

If you supply fewer initialisers than the array has room for, C fills the rest with zeros. That is
guaranteed, and it is the reason `= {0}` is the standard way to zero a whole array:

```c run
#include <stdio.h>

int main(void) {
    int partial[5] = {1, 2};
    int zeroed[5] = {0};
    size_t count = sizeof(partial) / sizeof(partial[0]);

    for (size_t i = 0; i < count; i++) {
        printf("[%d]", partial[i]);
    }
    printf("\n");
    for (size_t i = 0; i < count; i++) {
        printf("[%d]", zeroed[i]);
    }
    printf("\n");
    return 0;
}
```

```text
[1][2][0][0][0]
[0][0][0][0][0]
```

## An array name is not a pointer

The two are close enough to be confusing and different enough to matter. In most expressions an array
name *decays* to a pointer to its first element. But `sizeof` is not most expressions — it sees the
array itself, and that is the whole reason the count idiom works.

The decay happens when you pass the array to a function. The function receives a pointer, and the
length is gone:

```c warn
#include <stdio.h>

static void show_count(int values[]) {
    printf("inside:  %zu\n", sizeof(values) / sizeof(values[0]));
}

int main(void) {
    int values[5] = {1, 2, 3, 4, 5};

    printf("outside: %zu\n", sizeof(values) / sizeof(values[0]));
    show_count(values);
    return 0;
}
```

```text
sizeof on array function parameter will return size of 'int *' instead of 'int[]' [-Wsizeof-array-argument]
```

`int values[]` in a parameter list means `int *values`. There is no array there, only an address, so
`sizeof` reports the size of a pointer — eight bytes here, which divided by four gives the `2` that
the program would have printed had the compiler let it build. This warning is one of the most valuable
in the language, because the code it describes looks completely correct.

The fix is not to find a cleverer way to recover the length. The fix is to pass it:

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
    int values[5] = {10, 20, 30, 40, 50};

    printf("sum = %d\n", sum(values, sizeof(values) / sizeof(values[0])));
    return 0;
}
```

```text
sum = 150
```

`const int *values` and `size_t count` together are the standard C function signature for "a run of
integers I will not modify". Every function in the standard library that takes an array takes a length
beside it for exactly this reason.

## There is no bounds check

`values[i]` compiles to "take the address of `values`, add `i` elements, use what is there". Nothing
verifies that `i` is in range, and the compiler only complains when it can see the answer for itself:

```c warn
#include <stdio.h>

int main(void) {
    int values[3] = {1, 2, 3};

    values[5] = 1;
    return 0;
}
```

```text
array index 5 is past the end of the array (that has type 'int[3]') [-Warray-bounds]
```

That works because `5` is a literal and the array has a known size. The moment the index comes from a
loop variable, a file or a user, the compiler cannot know, says nothing, and the write lands wherever
the arithmetic points:

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int values[3] = {1, 2, 3};
    int index = (argc > 1) ? atoi(argv[1]) : 5;

    values[index] = 99;
    printf("wrote values[%d]\n", index);
    return 0;
}
```

```text
index 5 out of bounds for type 'int[3]'
```

Two sanitizers report this and both are worth knowing. UndefinedBehaviorSanitizer's bounds check names
the index and the type, which is the message above; AddressSanitizer then names the memory itself with
`stack-buffer-overflow`, which is the message you will see for out-of-bounds writes that UBSan cannot
reason about. In C the compiler is a weak ally against array bugs and the sanitizer is a strong one —
which is why the previous chapters kept telling you to run your tests with `-fsanitize=address,undefined`
switched on.

## A C string is a char array that ends in a zero

C has no string type. It has `char` arrays, and a convention: the last meaningful byte is followed by a
byte whose value is `0`, written `'\0'` and called the *null terminator*. Every string function walks
until it finds that byte.

```c run
#include <stdio.h>

int main(void) {
    char word[] = "hi";

    printf("bytes: %zu\n", sizeof(word));
    for (size_t i = 0; i < sizeof(word); i++) {
        printf("word[%zu] = %d\n", i, word[i]);
    }
    return 0;
}
```

```text
bytes: 3
word[0] = 104
word[1] = 105
word[2] = 0
```

`"hi"` is two characters plus a terminator, so the array is three bytes. `104` and `105` are `h` and
`i`; the third byte is the zero that makes it a string rather than a two-element character array. This
is also why `sizeof` and `strlen` disagree, and mixing them up is one of the most common C bugs:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *s = "hello";
    char arr[] = "hello";

    printf("strlen(s)   = %zu\n", strlen(s));
    printf("sizeof(s)   = %zu\n", sizeof(s));
    printf("sizeof(arr) = %zu\n", sizeof(arr));
    return 0;
}
```

```text
strlen(s)   = 5
sizeof(s)   = 8
sizeof(arr) = 6
```

`strlen` counts characters up to the terminator and is a runtime function — it walks the memory. `sizeof`
is a compile-time operator that reports the size of the *thing*, and `s` is a pointer, so it reports
eight. `arr` really is an array, so `sizeof` sees six bytes: five letters plus the terminator. Whenever
you find yourself writing `sizeof` where you meant "how long is this text", stop.

## String literals are read-only

`"hello"` in your source is stored once in the read-only part of the program. A `char *` pointing at it
can be read but must never be written — and in C, the compiler says nothing about that:

```c run-san-catch
#include <stdio.h>

int main(void) {
    char *s = "hi";

    s[0] = 'H';
    printf("%s\n", s);
    return 0;
}
```

```text
AddressSanitizer:DEADLYSIGNAL
```

The program dies on the write, because the page holding the literal is not writable. The exact signal
depends on the platform — a `SEGV` on Linux and x86, a `BUS` here on arm64 macOS — and ASan prints the
same `DEADLYSIGNAL` banner for both, which is why that is the phrase worth remembering. What matters is
that the compiler was silent: `char *s = "hi";` produces no warning at all in C, and the mistake only
surfaces when the program runs.

The discipline that avoids this entirely is to write `const char *` for anything that points at text
you did not allocate. Then the compiler does catch the write, and the type documents the intent:

```c bad
#include <stdio.h>

int main(void) {
    const char *s = "hi";

    s[0] = 'H';
    return 0;
}
```

```text
error: read-only variable is not assignable
```

## Comparing strings

Because a string is an array, comparing two of them with `==` compares addresses. Clang catches the
commonest version of this mistake, comparing against a literal:

```c warn
#include <stdio.h>

static const char *current_user(void) {
    return "admin";
}

int main(void) {
    if (current_user() == "admin") {
        printf("match\n");
    }
    return 0;
}
```

```text
result of comparison against a string literal is unspecified (use an explicit string comparison function instead) [-Wstring-compare]
```

Read that carefully, because it is stronger than it looks: the standard does not merely say the result
is unhelpful, it says the result is *unspecified*. Two identical literals in one program may or may not
be the same object, and a compiler is free to merge them or not. `strcmp` is the function that compares
contents, and it answers a different question from `==`:

```c run
#include <stdio.h>
#include <string.h>

static const char *pick(int flag) {
    return flag ? "left" : "right";
}

int main(void) {
    const char *a = pick(1);
    const char *b = pick(0);

    printf("a == b      : %d\n", a == b);
    printf("strcmp == 0 : %d\n", strcmp(a, b) == 0);
    printf("sign        : %d\n", strcmp(a, b) < 0 ? -1 : 1);
    return 0;
}
```

```text
a == b      : 0
strcmp == 0 : 0
sign        : -1
```

`strcmp` returns zero when the strings are equal, a negative number when the first sorts before the
second, and a positive number when it sorts after. Only the *sign* is specified — never compare the
result to `-1` or `1`, always to zero or with `< 0` and `> 0`, which is what the third line does.
`==` on two pointers is a perfectly good operation, it just answers "is this the same object", and
almost every time you write it on strings you meant "is this the same text".

## Copying strings without overrunning

`strcpy` copies until it finds a terminator, writing into the destination as it goes, with no idea how
much room there is. When the compiler can see both sides it refuses to let you:

```c warn
#include <stdio.h>
#include <string.h>

int main(void) {
    char small[5];

    strcpy(small, "this is far too long");
    printf("%s\n", small);
    return 0;
}
```

```text
'strcpy' will always overflow; destination buffer has size 5, but the source string has length 21 (including NUL byte) [-Wfortify-source]
```

That is clang's fortified-source check, and it is excellent — but it only fires when the source is
visible at the call site. The realistic version of this bug has the source coming from somewhere else,
and then nothing warns you and the sanitizer is the only thing between you and corrupted memory:

```c run-san-catch
#include <stdio.h>
#include <string.h>

int main(void) {
    char source[16];
    char destination[8];

    snprintf(source, sizeof(source), "%s", "a-long-name-here");
    strcpy(destination, source);
    printf("%s\n", destination);
    return 0;
}
```

```text
stack-buffer-overflow
```

`strncpy` is the traditional answer and it is a trap of its own. It copies *at most* `n` bytes and stops
— including the terminator only if it fits. When it truncates, it does not terminate:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    char buffer[8];

    memset(buffer, 'X', sizeof(buffer));
    strncpy(buffer, "abcdef", 3);

    for (size_t i = 0; i < sizeof(buffer); i++) {
        printf("%c", buffer[i]);
    }
    printf("\n");
    printf("buffer[3] is NUL: %d\n", buffer[3] == '\0');
    return 0;
}
```

```text
abcXXXXX
buffer[3] is NUL: 0
```

Three bytes were copied and no terminator was written, so the buffer is not a string — it is three
characters followed by whatever was there before. The `memset` in this program is there only to make
that visible; without it the leftover bytes are unpredictable, and printing the buffer with `%s` walks
off the end of the array until it happens to find a zero. That is the exact bug in the `run-san-catch`
block above, in the other direction.

The tool that gets this right is `snprintf`. It takes the destination size, never writes past it, and
returns the length it *would* have written — so you can detect truncation instead of guessing:

```c run
#include <stdio.h>

int main(void) {
    char line[64];

    snprintf(line, sizeof(line), "id=%d name=%s", 7, "ada");
    printf("%s\n", line);
    printf("would-be length: %d\n", snprintf(NULL, 0, "%s", "hello"));

    char tiny[5];
    int would = snprintf(tiny, sizeof(tiny), "%s", "hello world");

    printf("tiny=[%s] would=%d\n", tiny, would);
    return 0;
}
```

```text
id=7 name=ada
would-be length: 5
tiny=[hell] would=11
```

`tiny` holds four characters and a terminator, and `would` is `11` — the length the full string needed.
The test `would >= (int)sizeof(tiny)` is how you tell the caller "I truncated this", which is a decision
your program should make deliberately rather than discover later. Calling `snprintf` with `NULL` and a
size of zero to measure a string is a standard trick and is the only place a null pointer is legal here.

## Splitting and searching

`strchr` finds the first occurrence of a character and `strstr` the first occurrence of a substring;
both return a pointer into the original string, or `NULL`. Subtracting the original gives the offset:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *haystack = "hello world";
    const char *found = strstr(haystack, "wor");

    if (found != NULL) {
        printf("found at offset %d\n", (int)(found - haystack));
    }
    printf("first space at %d\n", (int)(strchr(haystack, ' ') - haystack));
    return 0;
}
```

```text
found at offset 6
first space at 5
```

For splitting on a delimiter, `strtok` walks a buffer and hands you one field at a time:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    char csv[] = "ada,grace,alan";
    char *field = strtok(csv, ",");
    int count = 0;

    while (field != NULL) {
        printf("%d: %s\n", ++count, field);
        field = strtok(NULL, ",");
    }
    printf("fields = %d\n", count);
    return 0;
}
```

```text
1: ada
2: grace
3: alan
fields = 3
```

Two things about `strtok` are worth carrying away. The first call takes the buffer; every later call
takes `NULL` and continues where the last one stopped, which is why it is not safe to use in two loops
at once or in anything threaded. And it works by *writing* `'\0'` over each delimiter — it modifies the
buffer you hand it. That is why the declaration above is `char csv[]` and not `const char *`: passing a
literal would be a compile error, and passing a literal you had cast would be the crash from earlier in
this chapter.

## Arrays of strings and two-dimensional arrays

An array of strings is an array of pointers, and each element is a pointer to text stored elsewhere:

```c run
#include <stdio.h>

int main(void) {
    const char *names[3] = {"ada", "grace", "alan"};

    for (int i = 0; i < 3; i++) {
        printf("%s (%zu)\n", names[i], sizeof(names[i]));
    }
    return 0;
}
```

```text
ada (8)
grace (8)
alan (8)
```

Note what `sizeof(names[i])` reports: eight, the size of a pointer, because `names[i]` is a `const char *`.
`sizeof(names)` would be twenty-four — three pointers. The text itself lives in the read-only segment,
which is why this form is preferred for fixed tables: it stores three pointers and shares nothing else.

A genuine two-dimensional array is a single block of memory with the rows laid end to end, which is why
the row count and column count can both be recovered with `sizeof`:

```c run
#include <stdio.h>

int main(void) {
    int grid[2][3] = {{1, 2, 3}, {4, 5, 6}};

    printf("total %zu, row %zu, cell %zu\n", sizeof(grid), sizeof(grid[0]), sizeof(grid[0][0]));
    printf("rows %zu, cols %zu\n",
           sizeof(grid) / sizeof(grid[0]), sizeof(grid[0]) / sizeof(grid[0][0]));
    printf("flat %d %d\n", grid[1][2], *(*(grid + 1) + 2));
    return 0;
}
```

```text
total 24, row 12, cell 4
rows 2, cols 3
flat 6 6
```

`grid` is twenty-four bytes: two rows of three four-byte integers. `grid[0]` is an array of three, so
`sizeof` sees twelve. That last line is there to make the layout concrete — `grid[1][2]` and
`*(*(grid + 1) + 2)` are the same expression written two ways, and neither knows where the row ends.
Passing a two-dimensional array to a function means passing a pointer to its first row, so the column
count must appear in the parameter type: `void f(int grid[][3], size_t rows)`.

:::scenario The login check that compared addresses
A developer is fixing a bug where a login always fails even though the stored name and the typed name
are obviously the same. The debug print proves the contents match, so the comparison itself must be at
fault:

```c run
#include <stdio.h>
#include <string.h>

static const char *stored_name(void) {
    return "admin";
}

int main(void) {
    char typed[16];

    snprintf(typed, sizeof(typed), "%s", "admin");

    if (stored_name() == typed) {
        printf("match\n");
    } else {
        printf("no match\n");
    }
    printf("strcmp says: %d\n", strcmp(stored_name(), typed));
    return 0;
}
```

```text
no match
strcmp says: 0
```

The two lines disagree, and that is the whole lesson: `strcmp` says the contents are identical while
`==` says they are different, because `==` is comparing two addresses. One string is a literal in the
read-only segment; the other is a local buffer that was filled by `snprintf`. Different objects,
different addresses, and no warning from the compiler — `-Wstring-compare` only fires when one side is
literally spelled out at the comparison, which is exactly the case that is easy to spot by eye.

:::solution Compare contents, and let the type say what you mean
`strcmp` against zero is the correct test, and the parameters should be `const char *` so the intent is
visible at the signature:

```c run
#include <stdio.h>
#include <string.h>

static const char *stored_name(void) {
    return "admin";
}

static int same_name(const char *left, const char *right) {
    return strcmp(left, right) == 0;
}

int main(void) {
    char typed[16];

    snprintf(typed, sizeof(typed), "%s", "admin");

    if (same_name(stored_name(), typed)) {
        printf("match\n");
    } else {
        printf("no match\n");
    }
    return 0;
}
```

```text
match
```

Wrapping the comparison in a named function is not ceremony. It puts the `== 0` in one place, so the
next person cannot write `strcmp(a, b)` and use the result as a boolean — which compiles, and is wrong
for exactly the case where the strings are equal, because `strcmp` returns zero and zero is false. The
function also gives the comparison a name that says what it means, and `const char *` on both
parameters tells the caller neither string will be touched.
:::

:::pitfall strlen returns an unsigned length, and the loop recomputes it
`strlen` returns `size_t`, which is unsigned. Comparing it against an `int` loop counter is a
signed/unsigned mismatch, and calling it in the loop condition walks the whole string on every
iteration:

```c warn
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *name = "grace";
    int length = strlen(name);

    for (int i = 0; i < strlen(name); i++) {
        printf("%c", name[i]);
    }
    printf("\nlength = %d\n", length);
    return 0;
}
```

```text
comparison of integers of different signs: 'int' and 'unsigned long' [-Wsign-compare]
```

Two fixes, and you want both. Declare the counter as `size_t` so the comparison is between like types,
and take the length once into a variable so the loop is not quadratic in the length of the string. On a
short name neither matters; in a loop over a million rows of text, the second one is the difference
between a fast program and a slow one, and the first one is the difference between a warning and a
silent bug the day someone's name is longer than `INT_MAX` characters.
:::

## Key takeaways

- `int values[5]` is a fixed run of five elements. `sizeof(values) / sizeof(values[0])` gives the count
  and keeps working when the array grows.
- A partial initialiser zero-fills the rest, so `= {0}` zeroes a whole array.
- An array name decays to a pointer to its first element in most expressions, but not in `sizeof`.
  As a function parameter, `int values[]` *is* `int *values` and the length is gone —
  `-Wsizeof-array-argument` warns about exactly this.
- There is no bounds check. The compiler catches only constant indices (`-Warray-bounds`); a runtime
  index is caught by UBSan's bounds check or ASan's `stack-buffer-overflow`.
- A C string is a `char` array whose last byte is `0`. `strlen` counts up to it at runtime; `sizeof`
  reports the array's size at compile time. They are not interchangeable.
- String literals are read-only. `char *s = "hi"; s[0] = 'H';` produces no warning in C and dies at
  runtime; write `const char *` and the compiler rejects it.
- `==` on strings compares addresses. Use `strcmp`, test only against zero or its sign, and never
  against `-1` or `1`.
- `strcpy` has no bound. `-Wfortify-source` catches it when both sides are visible; otherwise the
  overflow is only caught at runtime. `strncpy` does not terminate on truncation. `snprintf` takes the
  size, never overruns, and returns the length it would have written so you can detect truncation.
- `strchr` and `strstr` return a pointer into the original string, or `NULL`. `strtok` walks a
  `char[]` in place, writes terminators over the delimiters, and is not reentrant.
- `const char *names[3]` is three pointers to text stored elsewhere; `int grid[2][3]` is one block of
  twenty-four bytes with the rows laid end to end.

## Practice

- [ ] Declare `double readings[6]`, fill it with values, and print the count and the average using the
      `sizeof` idiom rather than a literal.
- [ ] Write `size_t count_char(const char *text, char target)` that returns how many times `target`
      appears. Test it on `"mississippi"` with `'s'` and with `'p'`.
- [ ] Write `void copy_limited(char *destination, size_t size, const char *source)` using `snprintf`,
      and prove it truncates safely when the source is longer than the destination.
- [ ] Write `void reverse(char *text)` that reverses a string in place. It must not allocate.
- [ ] Declare `const char *names[4]`, then write a loop that finds a given name with `strcmp` and
      prints its index, or `-1` if it is absent.
- [ ] Take the `run-san-catch` program from the bounds-check section and change the default index from
      `5` to `2`. Predict the output before you run it, then explain why the sanitizer is silent.

## Solutions

:::solution Exercise 2
Count with an index that stops at the terminator, and use `size_t` throughout.

```c run
#include <stdio.h>

static size_t count_char(const char *text, char target) {
    size_t count = 0;

    for (size_t i = 0; text[i] != '\0'; i++) {
        if (text[i] == target) {
            count++;
        }
    }
    return count;
}

int main(void) {
    printf("'s' in mississippi: %zu\n", count_char("mississippi", 's'));
    printf("'p' in mississippi: %zu\n", count_char("mississippi", 'p'));
    return 0;
}
```

```text
's' in mississippi: 4
'p' in mississippi: 2
```

The loop condition is `text[i] != '\0'` rather than a call to `strlen`, which is the difference between
one pass over the string and one pass to count plus another to walk — the same point as the pitfall
above. `size_t` for the counter and the return type keeps the signed/unsigned warning away, and the
parameter is `const char *` because the function reads the text and has no business changing it.
:::

:::solution Exercise 3
`snprintf` is the safe copy, and its return value is how you detect that it truncated.

```c run
#include <stdio.h>

static int copy_limited(char *destination, size_t size, const char *source) {
    int written = snprintf(destination, size, "%s", source);

    return written >= 0 && (size_t)written < size;
}

int main(void) {
    char buffer[8];

    printf("fits:    %d [%s]\n", copy_limited(buffer, sizeof(buffer), "short"), buffer);
    printf("truncated: %d [%s]\n", copy_limited(buffer, sizeof(buffer), "far too long"), buffer);
    return 0;
}
```

```text
fits:    1 [short]
truncated: 0 [far too]
```

`snprintf` returns the number of characters the full string needed, not the number it managed to write,
so comparing that against `size` tells you whether anything was lost. Note that `written` is an `int`,
because `snprintf` returns `int` and can return a negative value on an encoding error — the cast to
`size_t` has to wait until after the sign is known good, which is why the check reads `written >= 0 &&
(size_t)written < size` and not the other way round. The buffer is still a valid, terminated string
either way: `snprintf` always terminates when `size` is greater than zero, which is the guarantee
`strncpy` does not give.
:::

:::solution Exercise 4
Two indices walking towards each other, swapping as they go.

```c run
#include <stdio.h>
#include <string.h>

static void reverse(char *text) {
    size_t left = 0;
    size_t right = strlen(text);

    if (right == 0) {
        return;
    }
    right--;

    while (left < right) {
        char swap = text[left];
        text[left] = text[right];
        text[right] = swap;
        left++;
        right--;
    }
}

int main(void) {
    char word[] = "physics";

    reverse(word);
    printf("%s\n", word);
    return 0;
}
```

```text
scisyhp
```

`strlen` gives a count, so the last valid index is `strlen(text) - 1`; getting that wrong is the classic
off-by-one, and it writes one byte past the terminator. The `right == 0` guard is there because
decrementing zero on a `size_t` wraps to the largest possible value, which would turn an empty string
into a crash rather than a no-op. The swap uses a temporary `char` rather than any pointer trick, and
the loop condition is `left < right` so the middle character of an odd-length string is left alone —
swapping it with itself would be harmless, but stopping there is clearer about what the loop means.
:::

:::solution Exercise 5
`strcmp` inside a loop, with a sentinel for "not found".

```c run
#include <stdio.h>
#include <string.h>

static int find_name(const char *names[], size_t count, const char *target) {
    for (size_t i = 0; i < count; i++) {
        if (strcmp(names[i], target) == 0) {
            return (int)i;
        }
    }
    return -1;
}

int main(void) {
    const char *names[4] = {"ada", "grace", "alan", "edsger"};

    printf("alan   -> %d\n", find_name(names, 4, "alan"));
    printf("edsger -> %d\n", find_name(names, 4, "edsger"));
    printf("barbara-> %d\n", find_name(names, 4, "barbara"));
    return 0;
}
```

```text
alan   -> 2
edsger -> 3
barbara-> -1
```

The parameter is `const char *names[]`, which is a pointer to a pointer — an array of strings decaying
into a pointer to its first element, each of which is itself a `const char *`. The count comes in
separately for the same reason as every other array in this chapter. `-1` as the "not found" sentinel
works because index `0` is a legitimate result and a boolean would lose the distinction; this is the
convention `strchr` and `strstr` follow by returning `NULL`, and it is why the return type is `int`
rather than `size_t` — an unsigned type has no way to spell "no index".
:::
