---
chapter: 23
part: 4
title: References, const, and Overloading
summary: Use references instead of pointers for the common case, make const part of a type rather than a comment, and give several functions one name.
minutes: 55
tags: [reference, const, const-correctness, overloading, auto, default-arguments, dangling-reference]
---

In C, avoiding a copy meant passing a pointer, and letting a function change your variable meant
passing a pointer, and both meant the caller writing `&` and the callee wondering whether the pointer
could be null. C++ separates those two ideas. A **reference** means "this is the same object, not a
copy" and can do neither of the things that make pointers awkward: it cannot be null, and it cannot be
made to point somewhere else later. **`const`** then means "I promise not to modify it", and unlike a
comment in C, the compiler enforces it. Between them they take most pointers out of ordinary code, and
they are the reason the rest of Part IV can talk about ownership without constantly talking about
addresses.

## A reference is the object

A reference is declared with `&` and bound at the moment it is created. From then on it is a second
name for the same object, with no dereferencing and no separate existence:

```cpp run
#include <cstdio>

int main() {
    int value = 10;

    int &ref = value;          /* an alias, not a copy */
    ref = 20;
    std::printf("value = %d\n", value);

    int *ptr = &value;         /* a pointer must be dereferenced */
    *ptr = 30;
    std::printf("value = %d\n", value);

    std::printf("sizeof ref = %zu, sizeof ptr = %zu\n", sizeof ref, sizeof ptr);
    return 0;
}
```

```text
value = 20
value = 30
sizeof ref = 4, sizeof ptr = 8
```

The last line is the one to remember. `sizeof ref` is **4** — the size of an `int`, not the size of an
address — because `ref` is not a separate thing that refers to `value`; it *is* `value`, under another
name. `sizeof ptr` is 8, an address on this 64-bit target. A reference is not a pointer with nicer
syntax; it is a compile-time alias that costs nothing at run time.

Three rules follow from that, and they are all enforced by the compiler rather than by discipline:

- A reference **must** be initialised. `int &r;` does not compile, because there is no object to name.
- A reference **cannot** be reseated. `ref = other;` assigns to the object, it does not rebind the
  reference. If you need "can point somewhere else later", that is a pointer.
- A reference **cannot be null**. There is no null reference, which means a function that takes one
  never needs the `if (p == NULL) return;` guard that every C function taking a pointer needs.

## Passing by reference

The most common use is a parameter. C passes everything by value, so a function that takes a
`std::string` by value copies it — and in Chapter 22 the copy would have been invisible. This struct
prints when it is copied, which makes the cost visible:

```cpp run
#include <cstdio>
#include <string>

struct Tracked {
    std::string payload;
    explicit Tracked(const char *p) : payload(p) { std::printf("built\n"); }
    Tracked(const Tracked &other) : payload(other.payload) { std::printf("copied\n"); }
};

static void by_value(Tracked t)      { std::printf("by_value %zu\n", t.payload.size()); }
static void by_ref(const Tracked &t) { std::printf("by_ref   %zu\n", t.payload.size()); }

int main() {
    Tracked t("hello");
    by_value(t);
    by_ref(t);
    return 0;
}
```

```text
built
copied
by_value 5
by_ref   5
```

`copied` appears exactly once, and it belongs to `by_value`. The `&` in `by_ref` avoided it. For a
string of five characters that is irrelevant; for a vector of a million records it is the difference
between a fast function and a slow one, and the call site looks identical either way — which is why
the rule is worth learning as a habit rather than as an optimisation:

- **`const T &`** to read something without copying it. This is the default for any parameter bigger
  than a couple of machine words.
- **`T &`** to modify the caller's object. The call site does not change; the callee can write to it.
- **`T`** only for small types — `int`, `double`, a pointer — where a copy is cheaper than the
  indirection a reference introduces.

`const T &` also binds to a temporary, which is how `by_ref(std::string("hi"))` works even though there
is no named object to refer to. A plain `T &` will not accept a temporary, and that is deliberate: a
function that promises to modify its argument has no business being handed something about to vanish.

## const is part of the type

In C, `const` is easy to ignore — you can drop it through a pointer and the compiler will only
sometimes object. In C++ it is part of the type, so the compiler tracks it through every call. Two
declarations that look similar mean different things:

```cpp run
#include <cstdio>

int main() {
    int a = 1, b = 2;

    const int *p = &a;   /* cannot write through p ... */
    p = &b;              /* ... but p itself can move */
    std::printf("p -> %d\n", *p);

    int *const q = &a;   /* q cannot move ... */
    *q = 99;             /* ... but the value it points at can change */
    std::printf("a = %d\n", a);
    return 0;
}
```

```text
p -> 2
a = 99
```

Read the declarations right to left: `const int *p` is "p is a pointer to a const int", so the
*pointee* is protected; `int *const q` is "q is a const pointer to an int", so the *pointer* is. The
one you will write most often is neither: it is `const` on a reference parameter, and on a member
function.

A member function marked `const` promises not to modify the object it is called on, which is what makes
it callable on a `const` object. Without the marking, this does not compile:

```cpp bad
struct Counter {
    int n = 0;
    int get() { return n; }
};

int main() {
    const Counter c;
    return c.get();
}
```

```text
'this' argument to member function 'get' has type 'const Counter', but function is not marked const
```

The fix is to write `int get() const { return n; }`. The error message names the real problem: every
non-static member function has a hidden first parameter — `this` — and marking the function `const`
marks that parameter. The compiler is telling you that `get` wants a mutable `Counter` and you gave it
a const one. **Mark every member function `const` unless it actually modifies the object**, and your
types become usable in places you have not thought of yet — like being passed to a function that takes
`const Counter &`.

## Overloading

C has one global namespace for function names, which is why it is full of `abs`, `labs`, `fabs`,
`strtol`, `strtod`. C++ lets several functions share a name as long as their parameter lists differ,
and picks one from the argument types at compile time:

```cpp run
#include <cstdio>

static void show(int v)         { std::printf("int    %d\n", v); }
static void show(double v)      { std::printf("double %.1f\n", v); }
static void show(const char *v) { std::printf("text   %s\n", v); }

int main() {
    show(7);
    show(2.5);
    show("seven");
    return 0;
}
```

```text
int    7
double 2.5
text   seven
```

This is not a run-time decision. `show(7)` is resolved when the program is compiled, and the three
functions get three different mangled symbols — which is exactly the mechanism Chapter 22 showed you
in a linker error. Overloading is what name mangling is *for*.

Because the choice is made at compile time, it can also fail at compile time. Given two candidates that
each require a conversion, the compiler refuses to guess:

```cpp bad
int twice(long v)   { return (int)(v * 2); }
int twice(double v) { return (int)(v * 2); }

int main() {
    return twice(3);
}
```

```text
call to 'twice' is ambiguous
```

An `int` argument is not an exact match for either, so the conversion from `int` to `long` and the
conversion from `int` to `double` are equally good and the call is ambiguous. Adding `twice(int)` fixes
it, and that is the useful lesson: when an overload set becomes ambiguous, the answer is almost always
an exact-match overload, not a cast at every call site.

## Default arguments, and auto

Two smaller conveniences that come with the same territory:

```cpp run
#include <cstdio>

static int add(int a, int b = 10) { return a + b; }

int main() {
    auto total = add(5);
    auto other = add(5, 1);
    std::printf("%d %d\n", total, other);
    return 0;
}
```

```text
15 6
```

A default argument must be the last one, so `add(int a = 10, int b)` is not allowed — otherwise
`add(5)` would be ambiguous about which parameter it filled. `auto` asks the compiler to take the type
from the initialiser, which is a genuine convenience when the type is long (`std::vector<std::string>::iterator`)
and a hazard when it is not what you assumed. `auto` is not "no type"; it is "the type of the right-hand
side", deduced once, at compile time.

:::scenario The pointer that became a reference, and the one that must not

A C function fills a caller-provided buffer and reports success through its return value:

```c
int read_name(char *out, size_t outsz, const char *path);
```

Porting it to C++ the obvious way replaces the buffer with a `std::string`, and the `const char *path`
becomes a reference, because a path is always present:

```cpp
bool read_name(std::string &out, const std::string &path);
```

The `outsz` parameter is gone — the string knows its own size and grows itself — and `const` on `path`
tells every caller at the call site that the function will not modify it. The `&` on `out` tells them
that it will. Neither is a pointer, so neither needs a null check, and the two calls now read:

```cpp
std::string name;
if (!read_name(name, "/etc/hostname")) return -1;
```

The rule this illustrates: **a parameter that can legitimately be absent stays a pointer.** If the
function had to accept "no output wanted", `std::string *out` would be correct and `std::string &out`
would be a lie. Choosing a reference asserts "this is always there", and the compiler will hold you to
it — you cannot pass `nullptr`, and you cannot pass nothing.

:::

:::pitfall Returning a reference to a local

A function that returns `T &` must return a reference to something that outlives the call. Returning a
local is the mistake, and it is worth seeing how it is caught:

```cpp warn
#include <cstdio>

const int &pick() {
    int local = 42;
    return local;
}

int main() {
    std::printf("%d\n", pick());
    return 0;
}
```

```text
reference to stack memory associated with local variable 'local' returned
```

Two things about this. First, the compiler catches it — `-Wreturn-stack-address` is on by default and
is a warning, not an error, so the program above still builds and still prints `42`. It is undefined
behaviour that happens to look correct. Second, **the sanitizer does not catch it here**: under
`-fsanitize=address` this runs clean and exits `0`, because ASan's stack-use-after-return detection is
off by default. A run that reports nothing has not proved the code is correct.

What is safe to return a reference to: a static, a member of an object that outlives the call, an
element of a container that is still alive, or an object the caller owns and passed in. What is never
safe: a local, or a temporary you constructed in the function.

:::

## Key takeaways

- A **reference** is an alias for an object: it must be initialised, cannot be reseated, cannot be
  null, and `sizeof` on it gives the size of the *object*, not of an address.
- Use **`const T &`** to read a parameter without copying, **`T &`** to modify the caller's object, and
  plain **`T`** only for small types.
- `const T &` binds to temporaries; `T &` does not, because modifying something about to vanish is
  never what you meant.
- Read pointer declarations right to left: `const int *p` protects the pointee, `int *const q`
  protects the pointer.
- Mark every member function **`const`** unless it modifies the object. `this` is a hidden parameter,
  and `const` on the function is `const` on that parameter.
- **Overloading** is resolved at compile time from the argument types, and it is what name mangling
  exists to support. An ambiguous call is a compile error, not a run-time choice.
- A **default argument** must be last. **`auto`** takes its type from the initialiser at compile time;
  it is deduction, not absence of a type.
- Never return a reference to a local or a temporary. The compiler warns; the sanitizer does not.

## Practice

- [ ] Write `void bump(int &n)` that adds one to its argument, and call it on a local. Then write
      `void bump(int *n)` that does the same, and compare what the two call sites look like.
- [ ] Write a function `size_t total_length(const std::vector<std::string> &words)` and call it with
      a vector of five strings. Add a second version taking the vector by value and explain, from the
      printed output of a copy-tracking struct, which one you would ship.
- [ ] Take the `Counter` struct from this chapter and add a `const` member function `int doubled()
      const`. Show that a `const Counter` can call `doubled` but not the original `get`.
- [ ] Write an overload set `describe` for `int`, `double` and `bool`, and show which one `describe(0)`
      picks. Then explain why `describe('x')` might pick the `int` version.
- [ ] Write a function that returns a reference to a `static` counter, incrementing it each call. Run
      it three times and explain why this is safe when returning a local reference is not.
- [ ] Write two overloads that make a call ambiguous, run the compiler, and quote the error. Then fix
      it by adding an exact-match overload rather than by casting the argument.

## Solutions

:::solution Exercise 1

```cpp run
#include <cstdio>

static void bump_ref(int &n) { n += 1; }
static void bump_ptr(int *n) { *n += 1; }

int main() {
    int a = 10, b = 10;

    bump_ref(a);            /* no & at the call site, no * in the body */
    bump_ptr(&b);           /* both, at both ends */

    std::printf("%d %d\n", a, b);
    return 0;
}
```

```text
11 11
```

The bodies are a wash — `n += 1` against `*n += 1`. The difference is the call site and the contract.
`bump_ref(a)` cannot be called wrongly, and `bump_ref` cannot be handed a null. `bump_ptr(&b)` requires
the caller to remember the `&`, and `bump_ptr(nullptr)` compiles, so the body ought to have a null
check that `bump_ref` does not need.

:::

:::solution Exercise 2

```cpp run
#include <cstdio>
#include <string>
#include <vector>

static size_t total_length(const std::vector<std::string> &words) {
    size_t n = 0;
    for (const std::string &w : words) n += w.size();
    return n;
}

static void clear_copy(std::vector<std::string> words) {
    words.clear();
    std::printf("inside:  %zu\n", words.size());
}

int main() {
    std::vector<std::string> words = {"one", "two", "three"};
    std::printf("total = %zu\n", total_length(words));

    clear_copy(words);
    std::printf("outside: %zu\n", words.size());
    return 0;
}
```

```text
total = 11
inside:  0
outside: 3
```

Both functions "work". The difference is what the second one is allowed to do. `clear_copy` takes its
parameter by value, so it gets a private copy, empties that, and the caller's vector is untouched —
which is exactly what you want when modifying a copy *is* the point, and exactly the wrong thing when
it is not. `total_length` takes `const std::vector<std::string> &`, so it copies neither the vector nor
the three strings inside it, and the `const` guarantees it cannot touch them.

Passing a container by value copies **every element**, not once for the container. The reference
version is the one to ship by default; by-value is for when you intend to consume or mutate a private
copy.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>

struct Counter {
    int n = 0;
    int get() { return n; }
    int doubled() const { return n * 2; }
};

int main() {
    const Counter c;
    std::printf("doubled = %d\n", c.doubled());
    return 0;
}
```

```text
doubled = 0
```

`c.doubled()` compiles because `doubled` is marked `const`, so its hidden `this` parameter is
`const Counter *`. `c.get()` would still be the error from earlier in the chapter — `get` is not
marked, so it asks for a mutable `Counter`. Note that `n = 0` is initialised by the member initialiser
in the declaration, so a `const Counter` can be constructed at all.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>

static void describe(int v)    { std::printf("int    %d\n", v); }
static void describe(double v) { std::printf("double %.1f\n", v); }
static void describe(bool v)   { std::printf("bool   %s\n", v ? "true" : "false"); }

int main() {
    describe(0);
    describe(2.5);
    describe(true);
    describe('x');
    return 0;
}
```

```text
int    0
double 2.5
bool   true
int    120
```

Read the four lines against the argument that produced each one, because two of them are not the
overload a reader would guess:

| Call | Argument type | Overload chosen | Why |
| --- | --- | --- | --- |
| `describe(0)` | `int` | `int` | exact match |
| `describe(2.5)` | `double` | `double` | exact match |
| `describe(true)` | `bool` | `bool` | exact match |
| `describe('x')` | `char` | **`int`** | promotion beats every conversion |

The first three are unremarkable: an exact match always wins, and `2.5` is a `double` literal and
`true` is a `bool` literal, so no conversion happens at all. `describe('x')` is the interesting one. A
`char` is an integer type, and the promotion from `char` to `int` is ranked *better* than the
conversion from `char` to `bool` or to `double`, so the `int` overload wins and you get `120` — the
character code, not the character. That is the hazard of overload sets over arithmetic types: it
compiles, it runs, and it is not what the reader of the call site expects. Prefer distinct names, or a
type that says what you meant.

Notice also that each of these functions is `static` and every one of them is called. That is not
decoration: under `-Wall -Wextra -Werror` an overload that is defined but never called in the
translation unit is a hard error (`-Wunused-function`), so an exercise that adds an overload has to
call it or the build fails.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>

static int &counter() {
    static int n = 0;
    return n;
}

int main() {
    counter() += 1;
    counter() += 1;
    counter() += 1;
    std::printf("%d\n", counter());
    return 0;
}
```

```text
3
```

This is safe because a `static` local lives for the whole program, not for the call: its lifetime
starts on first execution and ends when the program does. A local without `static` is destroyed when
the function returns, so the reference the caller receives names memory that is about to be reused —
which is the warning from the pitfall. The distinction is **storage duration**, and it is the thing to
check before returning any reference.

:::

:::solution Exercise 6

```cpp bad
int twice(long v)   { return (int)(v * 2); }
int twice(double v) { return (int)(v * 2); }

int main() {
    return twice(3);
}
```

```text
call to 'twice' is ambiguous
```

The fix is an exact match for `int`, which then wins outright with no conversion at all:

```cpp run
#include <cstdio>

static int twice(int v)    { return v * 2; }
static int twice(long v)   { return (int)(v * 2); }
static int twice(double v) { return (int)(v * 2); }

int main() {
    std::printf("%d\n", twice(3));
    std::printf("%d\n", twice(3L));
    std::printf("%d\n", twice(3.5));
    return 0;
}
```

```text
6
6
7
```

`twice(3)` now picks the `int` overload — an exact match, so no conversion is needed and there is
nothing left to be ambiguous about. `twice(3L)` and `twice(3.5)` still reach the `long` and `double`
overloads as before, which is what shows the new overload was *added* rather than substituted. Note
`twice(3.5)` printing `7`: the argument is `double` and the return is `int`, so `3.5 * 2` is `7.0` and
the cast truncates to `7`. All three overloads are called here, so all three survive
`-Wunused-function`.

Casting at the call site would also have silenced the error, and it would have been the wrong fix: it
puts the burden on every caller and leaves the overload set ambiguous for the next person. An exact
overload solves it once, at the definition.

:::
