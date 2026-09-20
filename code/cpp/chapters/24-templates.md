---
chapter: 24
part: 4
title: Templates
summary: Write one function or class for many types, understand what the compiler deduces and when it gives up, keep templates in headers, and use static_assert to turn an unreadable error into a sentence.
minutes: 60
tags: [templates, generics, type-deduction, class-template, non-type-parameter, static-assert, header-only, instantiation]
---

Every function written so far has been one function for one type. Chapter 23's `Exporter` had three
virtual functions because three formats behaved differently — but if the bodies had been *identical* and
only the type had differed, three functions would have been pure duplication. That situation is common:
`larger(int, int)`, `larger(double, double)` and `larger(std::string, std::string)` would have the same
body. A **template** is how you write that body once and let the compiler produce one function per type
it is actually called with. It is the mechanism the entire standard library is built on, which is why
Chapter 25 can be a tour of containers and algorithms rather than a list of hundreds of functions.

## One function, many types

```cpp run
#include <cstdio>

template <typename T>
static T larger(T a, T b) {
    return a > b ? a : b;
}

int main() {
    std::printf("int    %d\n", larger(3, 7));
    std::printf("double %.1f\n", larger(2.5, 1.5));
    std::printf("char   %c\n", larger('a', 'z'));
    return 0;
}
```

```text
int    7
double 2.5
char   z
```

`template <typename T>` declares that `T` is a placeholder for a type. Nothing is compiled at that
point. When the compiler sees `larger(3, 7)` it **deduces** `T = int`, generates a function called an
**instantiation**, and calls it. `larger(2.5, 1.5)` generates a second, separate function with `T = double`.
The two have nothing in common at run time; they are as separate as if you had written them by hand,
which is the point — templates are a code-generation feature, not a run-time one. There is no
performance cost and no indirection.

`typename` and `class` mean the same thing here. `template <class T>` is identical and appears often in
older code; this book uses `typename` because it says what it means.

## Deduction, and where it stops

`T` is deduced from the arguments, and the deduction must produce **one** type:

```cpp bad
#include <cstdio>

template <typename T>
static T larger(T a, T b) { return a > b ? a : b; }

int main() {
    std::printf("%d\n", larger(3, 2.5));
    return 0;
}
```

```text
deduced conflicting types for parameter 'T' ('int' vs. 'double')
```

The compiler cannot pick: `int` would truncate `2.5`, and `double` would change the return type. Rather
than guess, it refuses. You have two ways out, and the difference matters:

```cpp run
#include <cstdio>

template <typename T>
static T larger(T a, T b) { return a > b ? a : b; }

int main() {
    std::printf("%.1f\n", larger<double>(3, 2.5));
    return 0;
}
```

```text
3.0
```

`larger<double>(3, 2.5)` names the type explicitly, so no deduction happens and `3` is converted to
`3.0`. The answer is `3.0` rather than `2.5`, because after the conversion the comparison is between
`3.0` and `2.5`. That is correct but easy to misread, and it is a good argument for taking the
parameters as `const T &` so at least no copies happen, or for making the two parameter types
independent when the function genuinely accepts mixed input.

## Class templates

Classes are templated the same way, and you must name the arguments when you use one:

```cpp run
#include <cstdio>

template <typename T>
class Box {
public:
    explicit Box(T value) : value_(value) {}
    const T &get() const { return value_; }
    void set(T value) { value_ = value; }

private:
    T value_;
};

int main() {
    Box<int> n(5);
    Box<double> d(2.5);
    n.set(9);
    std::printf("n = %d\n", n.get());
    std::printf("d = %.1f\n", d.get());
    std::printf("sizeof Box<int> = %zu, sizeof Box<double> = %zu\n",
                sizeof(Box<int>), sizeof(Box<double>));
    return 0;
}
```

```text
n = 9
d = 2.5
sizeof Box<int> = 4, sizeof Box<double> = 8
```

`Box<int>` and `Box<double>` are two unrelated classes that happen to have been generated from the same
text. The `sizeof` line is the proof: `4` and `8`, exactly the size of the member each holds, with no
per-object overhead. Unlike the virtual functions in Chapter 23, a template costs nothing at run time —
it moves the work to compile time.

A class template can take more than one parameter, and they need not be related:

```cpp run
#include <cstdio>
#include <string>

template <typename A, typename B>
class Pair {
public:
    Pair(A a, B b) : first_(a), second_(b) {}
    const A &first() const { return first_; }
    const B &second() const { return second_; }

private:
    A first_;
    B second_;
};

int main() {
    Pair<int, std::string> p(1, "one");
    Pair<std::string, double> q("pi", 3.14159);
    std::printf("p = %d / %s\n", p.first(), p.second().c_str());
    std::printf("q = %s / %.2f\n", q.first().c_str(), q.second());
    return 0;
}
```

```text
p = 1 / one
q = pi / 3.14
```

## Non-type parameters

A template parameter does not have to be a type. It can be a **value**, which lets you put a size into
the type itself:

```cpp run
#include <cstdio>

template <typename T, std::size_t N>
class Fixed {
public:
    std::size_t capacity() const { return N; }
    T &at(std::size_t i) { return data_[i]; }
    const T &at(std::size_t i) const { return data_[i]; }

private:
    T data_[N] = {};
};

int main() {
    Fixed<int, 4> a;
    a.at(0) = 11;
    a.at(3) = 44;
    std::printf("capacity = %zu, first = %d, last = %d\n", a.capacity(), a.at(0), a.at(3));
    std::printf("sizeof = %zu\n", sizeof(a));
    return 0;
}
```

```text
capacity = 4, first = 11, last = 44
sizeof = 16
```

`Fixed<int, 4>` holds its data inline — `sizeof` is `16`, four `int`s, with no pointer and no
allocation. This is how `std::array` works. Because `N` is part of the type, `Fixed<int, 4>` and
`Fixed<int, 8>` are different types, and the compiler can check bounds against a constant. `capacity()`
returns `N` without reading anything, because `N` is known at compile time.

## Templates live in headers

A template is not compiled until it is instantiated, and instantiation happens where it is *used*. That
means the compiler needs the full definition, not just a declaration, at every point of use — so a
template cannot be split into a header and a `.cpp` the way Chapter 12's functions were:

```cpp bad-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

template <typename T>
T larger(T a, T b);

#endif

/* ===== util.cpp ===== */
#include "util.h"

template <typename T>
T larger(T a, T b) { return a > b ? a : b; }

/* ===== main.cpp ===== */
#include <cstdio>
#include "util.h"

int main() {
    std::printf("%d\n", larger(3, 7));
    return 0;
}
```

```text
Undefined symbols for architecture arm64
```

Note that this is a **linker** error, not a compiler error. `main.cpp` compiled perfectly: it saw the
declaration, trusted it, and emitted a call to `larger<int>(int, int)`. `util.cpp` compiled perfectly
too, and emitted nothing at all — a template definition with no instantiation is not code, so the
compiler threw it away. The linker then looked for `larger<int>` and found no definition anywhere. This
is the same class of failure as Chapter 12's missing definition, arriving through a new route.

The fix is to put the whole definition in the header:

```cpp run-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

template <typename T>
T larger(T a, T b) {
    return a > b ? a : b;
}

#endif

/* ===== main.cpp ===== */
#include <cstdio>
#include "util.h"

int main() {
    std::printf("%d\n", larger(3, 7));
    return 0;
}
```

```text
7
```

The banner lines (`/* ===== util.h ===== */`) are listing separators, not file contents — do not paste
them into a file. The rule to remember: **a template's definition goes in a header**, and if the header
gets large you split it into several headers rather than into a header and a source file. The standard
library does exactly this, which is why `<vector>` is thousands of lines of code you compile every time
you include it.

## When instantiation fails, the error is unreadable

Because the compiler generates the function from your template, an error inside the body is reported at
the *template*, not at your call, and the message is about a type you never wrote:

```cpp bad
#include <cstdio>

template <typename T>
static T larger(T a, T b) { return a > b ? a : b; }

struct Opaque {
    int id;
};

int main() {
    Opaque x{1}, y{2};
    std::printf("%d\n", larger(x, y).id);
    return 0;
}
```

```text
invalid operands to binary expression ('Opaque' and 'Opaque')
```

The message is about `Opaque` and `Opaque`, which is the `a > b` inside a function you did not write for
`Opaque`. The note that follows is the useful half — `in instantiation of function template
specialization 'larger<Opaque>' requested here` — because it points at your call. With one template
parameter the error is survivable; with the four or five that `std::vector`'s internals have, the
message can run to a hundred lines, and this is the real cost of templates.

You can put the error back under control by asserting what you need at the top of the body:

```cpp run
#include <cstdio>
#include <type_traits>

template <typename T>
static T halve(T v) {
    static_assert(std::is_arithmetic<T>::value, "halve needs a number");
    return v / 2;
}

int main() {
    std::printf("int    %d\n", halve(9));
    std::printf("double %.2f\n", halve(7.0));
    return 0;
}
```

```text
int    4
double 3.50
```

`static_assert` is checked at compile time and costs nothing at run time. When the requirement fails, the
message is the sentence you wrote:

```cpp bad
#include <type_traits>

template <typename T>
static T halve(T v) {
    static_assert(std::is_arithmetic<T>::value, "halve needs a number");
    return v / 2;
}

struct Opaque {
    int id;
};

int main() {
    Opaque o{1};
    Opaque h = halve(o);
    return h.id;
}
```

```text
static assertion failed due to requirement 'std::is_arithmetic<Opaque>::value': halve needs a number
```

Compare that to the `invalid operands to binary expression` above. Same mistake, two very different
messages, and the difference is one line you wrote on purpose. **Put a `static_assert` in any template
whose requirements are not obvious from its signature** — it is the cheapest documentation you will ever
write, and the only kind the compiler reads.

:::scenario The three functions that were the same function

A codebase has three helpers for "give me the larger of these two", accumulated over two years:

```cpp
int         max_int(int a, int b)             { return a > b ? a : b; }
double      max_double(double a, double b)    { return a > b ? a : b; }
std::string max_string(const std::string &a, const std::string &b) { return a > b ? a : b; }
```

Someone notices they have identical bodies, replaces all three with one template, and deletes the
originals:

```cpp run
#include <cstdio>
#include <string>

template <typename T>
static T max_of(const T &a, const T &b) { return a > b ? a : b; }

int main() {
    std::printf("%d\n", max_of(3, 7));
    std::printf("%.1f\n", max_of(2.5, 1.5));
    std::printf("%s\n", max_of(std::string("apple"), std::string("pear")).c_str());
    return 0;
}
```

```text
7
2.5
pear
```

Three call sites, three types, one function — and `std::string` works without the template knowing
anything about strings, because `std::string` has `operator>`. That is what makes templates worth the
trouble: they work for types that did not exist when the template was written, including types in other
people's libraries.

Two things changed for the worse, and both are worth naming before you delete the originals. The first
is that the parameters are now `const T &` rather than the specific types, so a caller passing `int` and
`double` gets the deduction error from earlier instead of an implicit conversion — usually an
improvement, but it is a change in behaviour, not just in style. The second is the error message: a
future caller who passes a type without `operator>` now gets `invalid operands to binary expression`
pointing at a function they did not write.

The professional version of this change therefore keeps the template **and** adds the guard:

```cpp
template <typename T>
static T max_of(const T &a, const T &b) {
    static_assert(std::is_copy_constructible<T>::value,
                  "max_of returns a T by value, so T must be copyable");
    return a > b ? a : b;
}
```

Now the failure mode is a sentence. This is the trade you are making every time you generalise a
function: **fewer definitions, weaker signatures, better coverage** — and the price is paid in error
messages, which is why the `static_assert` is not optional decoration but the thing that makes the
generalisation safe to ship.

:::

:::pitfall A template parameter deduced from an array decays to a pointer

Chapter 8 taught that an array passed to a function becomes a pointer to its first element, losing its
size. Templates do not change that, and the symptom is a `sizeof` that looks impossible:

```cpp run
#include <cstdio>

template <typename T>
static std::size_t size_of(T) { return sizeof(T); }

int main() {
    int a[5] = {1, 2, 3, 4, 5};
    std::printf("size_of(a) = %zu\n", size_of(a));
    std::printf("sizeof a   = %zu\n", sizeof(a));
    return 0;
}
```

```text
size_of(a) = 8
sizeof a   = 20
```

Twenty bytes of array, and the template reported eight. It deduced `T = int *`, because the parameter
is `T` **by value** and an array passed by value decays to a pointer — so `sizeof(T)` is the size of a
pointer on this 64-bit target, not of the array. The template is not wrong; it answered the question it
was asked, which was about the type after decay.

If you actually want the size, take the array by reference so no decay happens:

```cpp run
#include <cstdio>

template <typename T, std::size_t N>
static std::size_t count_of(const T (&)[N]) { return N; }

int main() {
    int a[5] = {1, 2, 3, 4, 5};
    double b[3] = {1.0, 2.0, 3.0};
    std::printf("count_of(a) = %zu\n", count_of(a));
    std::printf("count_of(b) = %zu\n", count_of(b));
    return 0;
}
```

```text
count_of(a) = 5
count_of(b) = 3
```

`const T (&)[N]` says "a reference to an array of `N` `T`s", so the array does not decay and the compiler
deduces both `T` and `N` from the argument. This is how `std::size` and range-based `for` work. The
lesson generalises past arrays: **a template parameter is deduced from the argument's type as passed**,
so how you declare the parameter — by value, by reference, by const reference — decides what the
template sees, and a by-value parameter always sees the decayed type.

:::

## Key takeaways

- `template <typename T>` makes `T` a placeholder; the compiler generates a separate function or class
  per type it is actually used with, so templates cost nothing at run time.
- `typename` and `class` are interchangeable as template parameter keywords.
- Deduction must produce one type, so `larger(3, 2.5)` fails with `deduced conflicting types`; name the
  type explicitly (`larger<double>(3, 2.5)`) or make the parameters independent.
- A class template's arguments must be written out (`Box<int>`), and different arguments produce
  unrelated types — `sizeof Box<int>` is `4` and `sizeof Box<double>` is `8`.
- A non-type parameter such as `std::size_t N` puts a value into the type, so `Fixed<int, 4>` stores its
  data inline and can be bounds-checked against a compile-time constant.
- A template's definition must be visible where it is used, so templates go in headers; splitting one
  into a header and a `.cpp` produces an `Undefined symbols` **linker** error, not a compiler error.
- An error inside a template body is reported at the template with the caller's type substituted in, so
  the message is long and names types you did not write; the `in instantiation of ...` note points at
  your call.
- Use `static_assert` to state a template's requirements so failures produce a sentence instead of a
  hundred lines — C++20's `concepts` are the language's built-in version of the same idea, but they need
  `-std=c++20` and this book stays on C++17.

## Practice

- [ ] Write a `clamp(value, lo, hi)` function template and use it for `int` and `double`, including a
  value below the low bound, one above the high bound, and one in the middle.
- [ ] Write a `Pair<A, B>` class template with `first()` and `second()`, and instantiate it as
  `Pair<int, std::string>` and `Pair<std::string, double>`.
- [ ] Show the compiler rejecting `larger(3, 2.5)`, quote the note that names the two deduced types, then
  fix the call by naming the template argument.
- [ ] Write a `Fixed<T, N>` array wrapper with `capacity()` and `at()`, and show that
  `Fixed<int, 4>` reports `4` and occupies `16` bytes.
- [ ] Add a `static_assert` to a template requiring an arithmetic type, show the clear message it
  produces for a struct, and compare it with the raw `invalid operands` message you get without it.
- [ ] Split a template across a header and a `.cpp` file, show the linker error, then move the definition
  into the header and show the program building.

## Solutions

:::solution Exercise 1

```cpp run
#include <cstdio>

template <typename T>
static T clamp(T value, T lo, T hi) {
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

int main() {
    std::printf("%d\n", clamp(15, 0, 10));
    std::printf("%d\n", clamp(-3, 0, 10));
    std::printf("%d\n", clamp(7, 0, 10));
    std::printf("%.2f\n", clamp(2.75, 0.0, 1.0));
    return 0;
}
```

```text
10
0
7
1.00
```

All four calls deduce one type, so no conflict arises: `clamp(15, 0, 10)` gives `T = int` and
`clamp(2.75, 0.0, 1.0)` gives `T = double`. The `%.2f` line is the interesting one — the value is clamped
down to `1.0` and the format prints it as `1.00`. Mixing the types, as in `clamp(2.75, 0, 1)`, would fail
to deduce and is the reason this signature takes three of the same type.

:::

:::solution Exercise 2

```cpp run
#include <cstdio>
#include <string>

template <typename A, typename B>
class Pair {
public:
    Pair(A a, B b) : first_(a), second_(b) {}
    const A &first() const { return first_; }
    const B &second() const { return second_; }

private:
    A first_;
    B second_;
};

int main() {
    Pair<int, std::string> p(1, "one");
    Pair<std::string, double> q("pi", 3.14159);
    std::printf("p = %d / %s\n", p.first(), p.second().c_str());
    std::printf("q = %s / %.2f\n", q.first().c_str(), q.second());
    return 0;
}
```

```text
p = 1 / one
q = pi / 3.14
```

The two parameters are independent, so `Pair<int, std::string>` and `Pair<std::string, double>` are
completely different types generated from the same text. The accessors return `const A &` and `const B &`
rather than values, so reading through them copies nothing — with a `std::string` member that matters.

:::

:::solution Exercise 3

```cpp bad
#include <cstdio>

template <typename T>
static T larger(T a, T b) { return a > b ? a : b; }

int main() {
    std::printf("%d\n", larger(3, 2.5));
    return 0;
}
```

```text
candidate template ignored: deduced conflicting types for parameter 'T' ('int' vs. 'double')
```

The note names both deduced types, which is the compiler telling you exactly why it gave up. Naming the
argument removes the deduction and therefore the conflict:

```cpp run
#include <cstdio>

template <typename T>
static T larger(T a, T b) { return a > b ? a : b; }

int main() {
    std::printf("%.1f\n", larger<double>(3, 2.5));
    return 0;
}
```

```text
3.0
```

With `T` fixed to `double`, the `3` is converted and the comparison is `3.0 > 2.5`, so the answer is
`3.0`. The result is correct, and it is also a good illustration of why naming a template argument is
sometimes a decision worth pausing over: the conversion happened silently, and `larger<int>(3, 2.5)`
would have been the wrong answer rather than an error.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>

template <typename T, std::size_t N>
class Fixed {
public:
    std::size_t capacity() const { return N; }
    T &at(std::size_t i) { return data_[i]; }
    const T &at(std::size_t i) const { return data_[i]; }

private:
    T data_[N] = {};
};

int main() {
    Fixed<int, 4> a;
    a.at(0) = 11;
    a.at(3) = 44;
    std::printf("capacity = %zu, first = %d, last = %d\n", a.capacity(), a.at(0), a.at(3));
    std::printf("sizeof = %zu\n", sizeof(a));
    return 0;
}
```

```text
capacity = 4, first = 11, last = 44
sizeof = 16
```

`sizeof = 16` is four `int`s and nothing else: the size is in the type, so no pointer and no heap
allocation are needed. `capacity()` returns the constant `N`, so it compiles to a number rather than a
memory read. `Fixed<int, 4>` and `Fixed<int, 8>` are different types, so a function taking one will not
accept the other — the size is part of the contract, checked at compile time.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>
#include <type_traits>

template <typename T>
static T halve(T v) {
    static_assert(std::is_arithmetic<T>::value, "halve needs a number");
    return v / 2;
}

int main() {
    std::printf("int    %d\n", halve(9));
    std::printf("double %.2f\n", halve(7.0));
    return 0;
}
```

```text
int    4
double 3.50
```

And the failure, which is one readable sentence:

```cpp bad
#include <type_traits>

template <typename T>
static T halve(T v) {
    static_assert(std::is_arithmetic<T>::value, "halve needs a number");
    return v / 2;
}

struct Opaque {
    int id;
};

int main() {
    Opaque o{1};
    Opaque h = halve(o);
    return h.id;
}
```

```text
static assertion failed due to requirement 'std::is_arithmetic<Opaque>::value': halve needs a number
```

Compare that with what the same mistake produces without the assertion — `invalid operands to binary
expression ('Opaque' and 'int')`, pointing at the `v / 2` inside a function the caller never wrote. The
assertion does not change whether the program compiles; it changes who has to work out why it did not.
`int 4` in the passing run is `9 / 2` with integer division, which is worth noticing: the template
performs the same operation the types imply, and `halve(9.0)` would print `4.50`.

:::

:::solution Exercise 6

The template declared in the header and defined in a `.cpp`:

```cpp bad-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

template <typename T>
T larger(T a, T b);

#endif

/* ===== util.cpp ===== */
#include "util.h"

template <typename T>
T larger(T a, T b) { return a > b ? a : b; }

/* ===== main.cpp ===== */
#include <cstdio>
#include "util.h"

int main() {
    std::printf("%d\n", larger(3, 7));
    return 0;
}
```

```text
Undefined symbols for architecture arm64
```

Both translation units compile; the failure is at link time. `main.cpp` emitted a call to
`larger<int>(int, int)` based on the declaration, and `util.cpp` produced no code at all, because a
template definition that is never instantiated in that translation unit generates nothing. Moving the
definition into the header gives the compiler the body at the point of use:

```cpp run-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

template <typename T>
T larger(T a, T b) {
    return a > b ? a : b;
}

#endif

/* ===== main.cpp ===== */
#include <cstdio>
#include "util.h"

int main() {
    std::printf("%d\n", larger(3, 7));
    return 0;
}
```

```text
7
```

The banner lines are listing separators rather than file contents. Note that only one translation unit
remains: with the definition in the header there is nothing left for `util.cpp` to contain, which is the
normal shape for a header-only utility. The general rule is that a template's definition and its
declaration belong in the same file — the language has an `export` keyword for the other arrangement,
and essentially no compiler implements it.

:::
