---
chapter: 9
part: 2
title: Structs, Enums and Unions
summary: Group related values into your own type, pass those groups around without copying more than you meant to, and understand why a struct's size is not the sum of its members.
minutes: 55
tags: [struct, typedef, enum, union, padding, bitfields, member-access]
---

An array is a run of identical things. Real data is not identical: a point has an x and a y, a config
has a width and a height and a flag, a user has a name and an id. A `struct` is how C lets you name that
grouping, and it is the first construct in this book that lets you invent a type rather than borrow one.
Two details make structs more interesting than they look: assignment copies the whole thing, including
any array inside it, and the size the compiler gives a struct is usually larger than the fields you
wrote, because of padding.

## A struct groups values under one name

You declare the shape, then declare variables of it. Members are reached with `.`, and a struct can
hold any types, including other structs:

```c run
#include <stdio.h>
#include <string.h>

struct Point {
    int x;
    int y;
};

int main(void) {
    struct Point origin = {0, 0};
    struct Point corner = {3, 4};

    printf("origin = (%d, %d)\n", origin.x, origin.y);
    printf("corner = (%d, %d)\n", corner.x, corner.y);

    corner.x = 10;
    printf("corner now = (%d, %d)\n", corner.x, corner.y);
    return 0;
}
```

```text
origin = (0, 0)
corner = (3, 4)
corner now = (10, 4)
```

`struct Point` is the type name and `origin` is the variable. C keeps those separate, which is why you
write `struct Point origin` and not `Point origin`. That gets tedious quickly, so the idiom is to wrap
the declaration in a `typedef` and use the alias from then on:

```c run
#include <stdio.h>

typedef struct {
    int width;
    int height;
} Size;

int main(void) {
    Size screen = {1920, 1080};

    printf("area = %d\n", screen.width * screen.height);
    return 0;
}
```

```text
area = 2073600
```

From here on this book writes `Size` rather than `struct Size`, because that is what you will see in
real code. Note the order of initialisers: they are matched to the members in declaration order, so
`{1920, 1080}` sets `width` then `height`. Getting that backwards is a silent bug when both members are
`int`, and there is a syntax that removes the ambiguity — see the designated initialisers below.

## A struct assignment is a copy

This is the property that catches people out. `a = b` on two structs copies every byte of `b` into `a`.
Afterwards the two are completely independent, exactly like assigning two `int`s:

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

int main(void) {
    Point p = {1, 2};
    Point q = p;

    q.x = 99;

    printf("p = (%d, %d)\n", p.x, p.y);
    printf("q = (%d, %d)\n", q.x, q.y);
    return 0;
}
```

```text
p = (1, 2)
q = (99, 2)
```

Arrays do not behave this way — `int a[3]; int b[3]; a = b;` is a compile error, because an array name
decays to a pointer and you cannot assign to one. Structs are the opposite: assignment works, and it
copies. That single difference is why wrapping an array in a struct is a standard trick when you need
an array that can be assigned and passed by value.

## Passing structs to functions

The same copy rule applies to arguments, and this is where the copy stops being convenient. A function
that takes a struct by value receives a copy, so writing to it changes nothing the caller can see:

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

static void move_by_value(Point p) {
    p.x = 99;
}

static void move_by_pointer(Point *p) {
    p->x = 99;
}

int main(void) {
    Point a = {1, 2};
    Point b = {1, 2};

    move_by_value(a);
    move_by_pointer(&b);

    printf("after by_value:   %d\n", a.x);
    printf("after by_pointer: %d\n", b.x);
    return 0;
}
```

```text
after by_value:   1
after by_pointer: 99
```

`p->x` is shorthand for `(*p).x` — follow the pointer, then take the member. The arrow exists purely
because `(*p).x` needs the parentheses, since `.` binds tighter than `*`. You will write `->` far more
often than `(*p).`, and it is the visual signal that a function intends to modify what it was given.

Which one to use is a decision worth making deliberately. **By pointer** when the function modifies the
struct, when the struct is large enough that copying it costs real time, or when the struct contains
something that must not be duplicated. **By value** when the struct is small — a pair of `int`s costs
nothing — and when you want the compiler to guarantee the function cannot change your copy. A `const`
pointer gives you the second guarantee without the copy: `const Point *p`.

## The padding you did not ask for

`sizeof` on a struct is usually not the sum of its members. The compiler is allowed to insert unused
bytes between members so that each one starts at an address the hardware likes to read, and it does:

```c run
#include <stdio.h>
#include <stddef.h>

typedef struct {
    char a;
    int b;
    char c;
} Padded;

typedef struct {
    int b;
    char a;
    char c;
} Packed;

int main(void) {
    printf("Padded = %zu, members sum to %zu\n", sizeof(Padded), sizeof(char) + sizeof(int) + sizeof(char));
    printf("Packed = %zu, members sum to %zu\n", sizeof(Packed), sizeof(char) + sizeof(int) + sizeof(char));
    printf("offset of b in Padded = %zu\n", offsetof(Padded, b));
    printf("offset of c in Padded = %zu\n", offsetof(Padded, c));
    return 0;
}
```

```text
Padded = 12, members sum to 6
Packed = 8, members sum to 6
offset of b in Padded = 4
offset of c in Padded = 8
```

Both structs hold the same three members and one is half again as large. `Padded` puts the `char`
first, so the `int` at offset 4 leaves three unused bytes behind it, and the trailing `char` needs
padding to the struct's own alignment — twelve bytes in total. `Packed` puts the `int` first and the two
`char`s fit in its shadow, giving eight. `offsetof` from `<stddef.h>` reports where a member actually
lands, which is the tool to reach for when the numbers surprise you.

The practical rule: **declare members largest-first** when the struct is going to exist in large
numbers or be written to a file. A record of a million elements shrinks from twelve megabytes to eight
just by reordering three lines. Reordering is always safe in C — member order is not part of a struct's
interface, and nothing in the language depends on it except initialiser order.

## The struct you cannot compare

`==` does not work on structs. There is no member-wise comparison hiding behind the operator, and the
compiler tells you so rather than guessing:

```c bad
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

int main(void) {
    Point p = {1, 2};
    Point q = {1, 2};

    printf("%d\n", p == q);
    return 0;
}
```

```text
invalid operands to binary expression ('Point' and 'Point')
```

The reason is padding again. Two structs can be equal field by field and still differ in the bytes the
compiler inserted, so there is no byte-wise comparison that means "equal" in general. Write the
comparison yourself, and write it as a named function so it exists in exactly one place:

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

static int point_equal(Point left, Point right) {
    return left.x == right.x && left.y == right.y;
}

int main(void) {
    Point p = {1, 2};
    Point q = {1, 2};
    Point r = {1, 3};

    printf("p == q: %d\n", point_equal(p, q));
    printf("p == r: %d\n", point_equal(p, r));
    return 0;
}
```

```text
p == q: 1
p == r: 0
```

## Structs that contain arrays

A struct may contain an array, and the copy rule then applies to the array's *contents*, not to a
pointer to them:

```c run
#include <stdio.h>

typedef struct {
    char text[16];
    int length;
} Name;

int main(void) {
    Name a = {"ada", 3};
    Name b = a;

    b.text[0] = 'A';

    printf("a.text = %s\n", a.text);
    printf("b.text = %s\n", b.text);
    printf("sizeof = %zu\n", sizeof(Name));
    return 0;
}
```

```text
a.text = ada
b.text = Ada
sizeof = 20
```

The two structs have separate sixteen-byte arrays, so changing one leaves the other alone. This is the
one place in C where an array behaves like a value rather than like a pointer, and it is why a struct
holding a fixed-size buffer is a safe thing to return from a function: the bytes travel with the struct.

## Returning structs, and designated initialisers

A function may return a struct by value. Unlike returning a pointer to a local, this is completely
correct — the value is copied out before the frame is popped:

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

static Point make_point(int x, int y) {
    Point p = {.x = x, .y = y};

    return p;
}

int main(void) {
    Point p = make_point(3, 4);
    Point q = {.y = 9, .x = 8};

    printf("p = (%d, %d)\n", p.x, p.y);
    printf("q = (%d, %d)\n", q.x, q.y);
    return 0;
}
```

```text
p = (3, 4)
q = (8, 9)
```

`.x = x` is a *designated initialiser*: it names the member instead of relying on position. The members
in `q` are written in the opposite order to the declaration and still land correctly, which is the whole
point. Any member you do not name is zeroed. Use designated initialisers for any struct with more than
about three members, and always when two members share a type.

## Arrays of structs

Structs and arrays compose, and the result is the shape of almost every real data structure in C:

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

int main(void) {
    Point points[3] = {{1, 2}, {3, 4}, {5, 6}};
    size_t count = sizeof(points) / sizeof(points[0]);
    int sum = 0;

    for (size_t i = 0; i < count; i++) {
        sum += points[i].x + points[i].y;
    }
    printf("count = %zu, sum = %d\n", count, sum);
    return 0;
}
```

```text
count = 3, sum = 21
```

`points[i].x` parses as `(points[i]).x` — subscript first, then member. The array is a contiguous run of
structs, so `points[1]` starts `sizeof(Point)` bytes after `points[0]`, and the whole thing is one
allocation. The `sizeof` idiom from the previous chapter works unchanged.

## Enums: names for a fixed set of values

An `enum` declares a set of named integer constants. It exists so you can write `GREEN` instead of `1`,
and so a reader can see the full set of legal values in one place:

```c run
#include <stdio.h>

typedef enum {
    RED,
    GREEN,
    BLUE
} Colour;

static const char *name_of(Colour c) {
    switch (c) {
        case RED:   return "red";
        case GREEN: return "green";
        case BLUE:  return "blue";
    }
    return "unknown";
}

int main(void) {
    for (Colour c = RED; c <= BLUE; c++) {
        printf("%d -> %s\n", c, name_of(c));
    }
    return 0;
}
```

```text
0 -> red
1 -> green
2 -> blue
```

The first name is `0` and each one after it is one more, so `RED` is `0`, `GREEN` is `1`, `BLUE` is `2`.
You can set the values explicitly (`RED = 1, GREEN = 2`) and they do not have to be consecutive.

An enum is not a distinct type in C the way it looks. It is an integer with a nicer name, and that has
consequences:

```c run
#include <stdio.h>

typedef enum { RED, GREEN, BLUE } Colour;

int main(void) {
    Colour c = GREEN;

    printf("GREEN = %d\n", c);
    printf("sizeof(Colour) = %zu\n", sizeof(Colour));
    printf("BLUE + 1 = %d\n", BLUE + 1);
    return 0;
}
```

```text
GREEN = 1
sizeof(Colour) = 4
BLUE + 1 = 3
```

`sizeof(Colour)` is four, the size of an `int`, because that is what it is. Nothing stops you assigning
`17` to a `Colour` variable, and nothing stops `BLUE + 1` being a valid expression with the value `3`,
which is not a colour at all. C++ fixes this — a scoped enum there really is its own type — but in C
the discipline is yours: always `switch` on an enum with a `case` for every member, so that adding a
fourth colour makes the omission visible.

## Unions: one piece of memory, several readings

A `union` declares members that all start at the same address. Its size is the size of its largest
member, and writing one member overwrites the others:

```c run
#include <stdio.h>

typedef union {
    int i;
    float f;
    unsigned char bytes[4];
} Number;

int main(void) {
    Number n;

    n.f = 1.0f;

    printf("sizeof(Number) = %zu\n", sizeof(Number));
    printf("as int:  %d\n", n.i);
    printf("bytes:   %02x %02x %02x %02x\n", n.bytes[0], n.bytes[1], n.bytes[2], n.bytes[3]);
    return 0;
}
```

```text
sizeof(Number) = 4
as int:  1065353216
bytes:   00 00 80 3f
```

Four bytes, and three ways to read them. `1065353216` is `0x3F800000`, which is exactly how IEEE-754
encodes `1.0f` as a 32-bit integer, and the four bytes in order are that same number written
little-endian — the low byte first. Reading a member you did not last write is *implementation-defined*
in C rather than undefined: the behaviour is the platform's byte reinterpretation, so the value depends
on the machine's byte order and float format. On anything you will meet it is IEEE-754, but the standard
does not promise it. In C++ the same code is undefined behaviour outright, which is why C++ has
`std::bit_cast` instead.

Unions earn their place in two situations: reading the bytes of a larger value, and saving memory when
a record holds one of several alternatives and never more than one at a time. They are not a
type-conversion tool — if you want to turn a `float` into an `int` numerically, write `(int)f`.

## Bitfields

A struct member can declare a width in bits, which is how C describes hardware registers and packed
flag words:

```c run
#include <stdio.h>

typedef struct {
    unsigned ready : 1;
    unsigned error : 1;
    unsigned mode  : 3;
} Flags;

int main(void) {
    Flags f = {0};

    f.ready = 1;
    f.mode = 5;

    printf("sizeof(Flags) = %zu\n", sizeof(Flags));
    printf("ready=%u error=%u mode=%u\n", f.ready, f.error, f.mode);
    return 0;
}
```

```text
sizeof(Flags) = 4
ready=1 error=0 mode=5
```

Five bits of data in a four-byte struct — the compiler packed them into one `unsigned int`. The widths
must not exceed the type's size, and `mode` being three bits means it holds `0`–`7`; assigning `8`
silently keeps the low three bits and gives you `0`. Bitfield layout is also implementation-defined, so
never write one to a file or send one over a network and expect another compiler to read it back the
same way.

:::scenario The defaults that never reached the caller
A developer adds a settings struct and a function to fill in sensible starting values. It compiles, it
runs, and the window comes up at zero by zero:

```c run
#include <stdio.h>

typedef struct {
    int width;
    int height;
    int fullscreen;
} Config;

static void load_defaults(Config config) {
    config.width = 1920;
    config.height = 1080;
    config.fullscreen = 1;
}

int main(void) {
    Config config = {0, 0, 0};

    load_defaults(config);

    printf("width  = %d\n", config.width);
    printf("height = %d\n", config.height);
    return 0;
}
```

```text
width  = 0
height = 0
```

`load_defaults` did its job perfectly — on a copy. The three assignments went into a temporary that was
destroyed the moment the function returned, and the caller's struct was never touched. Nothing warns,
because passing a struct by value is legal and correct C; the function is simply useless as written.
This is the same trap as `swap` in the functions chapter, wearing a larger type.

:::solution Give the function the caller's struct, not a copy
Take a pointer and use `->` for the members. The call site then has to write `&config`, which is a small
piece of friction that makes the mutation visible at the point of the call:

```c run
#include <stdio.h>

typedef struct {
    int width;
    int height;
    int fullscreen;
} Config;

static void load_defaults(Config *config) {
    config->width = 1920;
    config->height = 1080;
    config->fullscreen = 1;
}

int main(void) {
    Config config = {0, 0, 0};

    load_defaults(&config);

    printf("width      = %d\n", config.width);
    printf("height     = %d\n", config.height);
    printf("fullscreen = %d\n", config.fullscreen);
    return 0;
}
```

```text
width      = 1920
height     = 1080
fullscreen = 1
```

The naming convention matters as much as the pointer: a function that takes `Config *` will modify it,
so call it `load_defaults`, not `get_defaults`. In C there is no way to mark a parameter as an output,
so the convention `const Config *` for input and `Config *` for output is the only signal the reader
gets, and every C codebase relies on it. When the struct is small and the function genuinely returns a
new value, prefer returning by value — `Config make_defaults(void)` is clearer still, and the copy rule
makes it safe.
:::

:::pitfall memcmp on a struct compares the padding too
`memcmp` looks like the byte-wise struct comparison the language refuses to give you. It works, and it
is wrong, for a reason that is invisible in the code:

```c run
#include <stdio.h>
#include <string.h>

typedef struct {
    char tag;
    int value;
} Record;

int main(void) {
    Record a;
    Record b;

    memset(&a, 0, sizeof a);
    memset(&b, 0, sizeof b);

    a.tag = 'x';
    a.value = 7;
    b.tag = 'x';
    b.value = 7;

    printf("sizeof = %zu, members = %zu\n", sizeof(Record), sizeof(char) + sizeof(int));
    printf("memcmp after memset = %d\n", memcmp(&a, &b, sizeof a));
    return 0;
}
```

```text
sizeof = 8, members = 5
memcmp after memset = 0
```

The comparison returns zero *because both structs were zeroed first*. Three of the eight bytes being
compared are padding that no assignment ever writes, so without the `memset` their contents are whatever
was on the stack — and `memcmp` will report two field-identical records as different. That is a bug that
appears in a test suite, disappears when you add a `printf`, and reappears in the next build.

Two ways out, and both are fine. Zero the struct before filling it in, which makes `memcmp` deterministic
and is the version shown above; or write a field-by-field comparison function, which is immune to
padding entirely and gives the compiler a chance to optimise it. What you must not do is `memcmp` two
structs you did not initialise, because the result depends on memory you never wrote.
:::

## Key takeaways

- A `struct` groups named members into a new type. `typedef struct { … } Name;` lets you write `Name`
  instead of `struct Name`, and is the idiom real C uses.
- Members are reached with `.` on a struct and `->` on a pointer. `p->x` means `(*p).x`.
- Struct assignment copies every byte, including any array inside the struct. Arrays on their own cannot
  be assigned at all — that difference is why wrapping an array in a struct is a common trick.
- A function taking a struct by value gets a copy, so writes to it are lost. Take `Config *` to modify,
  `const Config *` to read without copying, and return by value when you are producing a new struct.
- `sizeof` on a struct is usually larger than the sum of its members because of alignment padding.
  Declare members largest-first to reduce it. `offsetof` reports where a member really lands.
- `==` does not compile on structs, because padding makes byte-wise equality meaningless. Write a
  field-by-field comparison function.
- A struct may contain an array, and that array is copied with the struct — which makes it safe to
  return such a struct from a function.
- Designated initialisers (`.x = 1`) name members instead of relying on order and zero anything unnamed.
  Use them for any struct with more than a couple of members.
- An `enum` is a set of named `int` constants. `sizeof` is 4, arithmetic on the names is allowed, and
  nothing checks the value — so always `switch` over every member.
- A `union` overlays its members at one address and is the size of the largest. Reading a member you did
  not write is implementation-defined in C and undefined in C++.
- Bitfields pack members into a stated number of bits. Assigning a value wider than the field silently
  truncates, and the layout is implementation-defined, so never use one as a file or wire format.

## Practice

- [ ] Declare a `Point` struct with `x` and `y`, initialise one with a designated initialiser, and print
      both members.
- [ ] Write `static Point add(Point a, Point b)` that returns a new `Point`. Explain why returning the
      struct by value is safe here when returning a pointer to a local would not be.
- [ ] Write `static void scale(Point *p, int factor)` that multiplies both members in place, and call it
      from `main`.
- [ ] Declare `typedef struct { char a; double b; char c; } Awkward;` and print `sizeof`, the sum of the
      members, and the offset of each one. Then reorder the members to make it as small as you can and
      print the new size.
- [ ] Declare an enum for the days of a week and write `name_of` with a `case` for each. Then add a
      fourth enum member to a smaller enum and confirm the compiler warns you that a `switch` no longer
      covers every value.
- [ ] Build a union holding a `double` and an array of eight `unsigned char`, set the `double` to `1.0`,
      and print the bytes. Explain in one sentence why the byte order is what it is.

## Solutions

:::solution Exercise 1
Declare the type, then initialise by naming the members.

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

int main(void) {
    Point p = {.y = 7, .x = 3};

    printf("x = %d\n", p.x);
    printf("y = %d\n", p.y);
    return 0;
}
```

```text
x = 3
y = 7
```

The initialiser names `y` first and `x` second, and the struct still comes out with `x = 3` and `y = 7`.
That is the whole argument for designated initialisers: with `{3, 7}` you would have to check the
declaration to know which member got which number, and here you do not. `p.x` and `p.y` are the member
accesses — the `.` operator applied to a struct variable, which is what you use until you have a pointer.
:::

:::solution Exercise 2
Returning a struct copies the value out, so nothing outlives its frame.

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

static Point add(Point a, Point b) {
    Point result = {.x = a.x + b.x, .y = a.y + b.y};

    return result;
}

int main(void) {
    Point p = {.x = 1, .y = 2};
    Point q = {.x = 10, .y = 20};
    Point sum = add(p, q);

    printf("sum = (%d, %d)\n", sum.x, sum.y);
    return 0;
}
```

```text
sum = (11, 22)
```

`result` is a local, but it is returned *by value*: the compiler copies its bytes into the caller's
`sum` before the frame is destroyed. The broken version of this from the pointers chapter returned
`&local`, an address of memory that was about to be reused — the difference is that an address is not
a value, and a struct is. Designated initialisers make the intent explicit here, and because the two
members share the `int` type, positional initialisers would have been an easy place to swap `x` and `y`
by accident.
:::

:::solution Exercise 3
Take a pointer, use `->`, and pass the address at the call site.

```c run
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

static void scale(Point *p, int factor) {
    p->x *= factor;
    p->y *= factor;
}

int main(void) {
    Point p = {.x = 3, .y = 4};

    scale(&p, 10);

    printf("p = (%d, %d)\n", p.x, p.y);
    return 0;
}
```

```text
p = (30, 40)
```

`p->x *= factor` writes through the pointer into the caller's struct, which is why the change survives.
The parameter must be `Point *` rather than `const Point *` precisely because the function modifies it —
that is the whole purpose of the function, and the type says so. The call site reads `scale(&p, 10)`,
and the `&` is the reader's cue that `p` may come back changed.
:::

:::solution Exercise 4
Declare largest-first and the padding shrinks to the minimum the alignment rules allow.

```c run
#include <stdio.h>
#include <stddef.h>

typedef struct {
    char a;
    double b;
    char c;
} Awkward;

typedef struct {
    double b;
    char a;
    char c;
} Tidy;

int main(void) {
    printf("Awkward = %zu, members sum to %zu\n",
           sizeof(Awkward), sizeof(char) + sizeof(double) + sizeof(char));
    printf("  offset a = %zu, b = %zu, c = %zu\n",
           offsetof(Awkward, a), offsetof(Awkward, b), offsetof(Awkward, c));

    printf("Tidy    = %zu, members sum to %zu\n",
           sizeof(Tidy), sizeof(double) + sizeof(char) + sizeof(char));
    printf("  offset b = %zu, a = %zu, c = %zu\n",
           offsetof(Tidy, b), offsetof(Tidy, a), offsetof(Tidy, c));
    return 0;
}
```

```text
Awkward = 24, members sum to 10
  offset a = 0, b = 8, c = 16
Tidy    = 16, members sum to 10
  offset b = 0, a = 8, c = 9
```

`Awkward` pays twice: seven bytes of padding after `a` to bring `b` to an eight-byte boundary, then
seven more after `c` because the struct as a whole must be a multiple of its largest member's alignment.
`Tidy` moves the `double` to the front, so `b` starts at zero and the two `char`s share the eight bytes
that follow with six to spare. Sixteen bytes against twenty-four, from reordering three lines. The sum
of the members is ten in both cases, and neither struct achieves it — a `double` forces eight-byte
alignment, so ten bytes can never be the answer.
:::

:::solution Exercise 5
An enum with a `case` for every member, then break the coverage and read the warning.

```c run
#include <stdio.h>

typedef enum {
    MONDAY,
    TUESDAY,
    WEDNESDAY,
    THURSDAY,
    FRIDAY,
    SATURDAY,
    SUNDAY
} Day;

static const char *name_of(Day day) {
    switch (day) {
        case MONDAY:    return "Monday";
        case TUESDAY:   return "Tuesday";
        case WEDNESDAY: return "Wednesday";
        case THURSDAY:  return "Thursday";
        case FRIDAY:    return "Friday";
        case SATURDAY:  return "Saturday";
        case SUNDAY:    return "Sunday";
    }
    return "unknown";
}

int main(void) {
    printf("%d -> %s\n", WEDNESDAY, name_of(WEDNESDAY));
    printf("%d -> %s\n", SUNDAY, name_of(SUNDAY));
    return 0;
}
```

```text
2 -> Wednesday
6 -> Sunday
```

The `switch` covers all seven members, which is what makes the `return "unknown";` after it
unreachable in practice — and it is there anyway, because the compiler still requires a return on every
path and because `name_of` accepts any integer a caller cares to pass. Now add a fourth member to the
enum and rebuild: clang reports `enumeration value 'EXTRA' not handled in switch [-Wswitch]`. That
warning is the entire value of using an enum over a set of `#define`s — the compiler cannot check a
`switch` against a `#define`, but it can check one against an enum, and adding a member to an enum is
exactly the moment you want to be told which `switch` statements need updating.
:::

:::solution Exercise 6
Overlay a `double` with eight bytes and read the encoding.

```c run
#include <stdio.h>

typedef union {
    double d;
    unsigned char bytes[8];
} Bits;

int main(void) {
    Bits b;

    b.d = 1.0;

    printf("sizeof = %zu\n", sizeof(Bits));
    for (size_t i = 0; i < sizeof(b.bytes); i++) {
        printf("%s%02x", i == 0 ? "" : " ", b.bytes[i]);
    }
    printf("\n");
    return 0;
}
```

```text
sizeof = 8
00 00 00 00 00 00 f0 3f
```

`f0 3f` is the last two bytes, and it is the tail of `0x3FF0000000000000` — the IEEE-754 encoding of
`1.0`, whose exponent field is `0x3FF` and whose mantissa is all zeroes. The bytes come out
least-significant first because this platform is little-endian, and that is the sentence the exercise
was asking for: the order is a property of the *machine*, not of C. On a big-endian machine the same
program prints `3f f0 00 00 00 00 00 00`, and the standard permits either. That is also why the chapter
called reading a member you did not write implementation-defined rather than undefined: the behaviour
is well specified, it is just specified in terms of the hardware.
:::
