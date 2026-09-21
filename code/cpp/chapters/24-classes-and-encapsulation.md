---
chapter: 24
part: 4
title: Classes and Encapsulation
summary: Bind data to the functions that keep it valid, make the compiler run your cleanup code at the end of a scope, and use private members to make an invalid object impossible to construct.
minutes: 55
tags: [class, struct, constructor, destructor, initialiser-list, encapsulation, raii, static, explicit]
---

Look at `handle` from Chapter 21 again. It took a request, produced a response, and closed three
resources on the way out — and it only worked because someone remembered to write the closing code on
every path. In C, the data and the rules for keeping that data valid live in different places: a
`struct Request` in one header, a `request_init` in another, and nothing stops a caller from setting a
field to a value the rest of the code cannot handle. C++ gives you one construct that fixes both
problems at once. A **class** puts the data and the functions together, and its **destructor** runs
automatically when the object's scope ends, so cleanup stops being a thing you remember and becomes a
thing the language does.

## A struct with functions attached

The smallest class is a struct you already know, plus methods:

```cpp run
#include <cstdio>

struct Point {
    int x = 0;
    int y = 0;
};

int main() {
    Point p;
    p.x = 1;
    p.y = 2;
    std::printf("(%d, %d)\n", p.x, p.y);

    Point q{7, 9};
    std::printf("(%d, %d)\n", q.x, q.y);
    return 0;
}
```

```text
(1, 2)
(7, 9)
```

Two things changed from the C structs in Chapter 11. `int x = 0;` is a **default member initialiser** —
`Point p;` now has both fields at zero instead of indeterminate, so the "uninitialised struct" bug
class from Part I cannot happen to this type. And `Point q{7, 9};` initialises both fields in
declaration order, which is the same brace syntax you already use for arrays.

`class` and `struct` are the **same construct**. The only difference is the default access level, and
that one difference is worth a chapter of debugging:

```cpp bad
#include <cstdio>

class Point {
    int x;
    int y;
};

int main() {
    Point p;
    p.x = 1;
    std::printf("%d\n", p.x);
    return 0;
}
```

```text
'x' is a private member of 'Point'
```

The compiler says `implicitly declared private here` and points at the line. In a `struct`, members
are public until you say otherwise; in a `class`, they are private until you say otherwise. That is the
whole difference. The convention the rest of this book follows is the one most C++ codebases use:
**`struct` for plain bundles of data with no invariants, `class` for anything with a constructor that
has to enforce something.**

## The constructor and the destructor

A **constructor** runs when an object is created; a **destructor** runs when it is destroyed. The
destructor is written `~Name`, takes no arguments and has no return type. Watch the order:

```cpp run
#include <cstdio>

struct Tracer {
    const char *name;
    Tracer(const char *n) : name(n) { std::printf("construct %s\n", name); }
    ~Tracer() { std::printf("destroy   %s\n", name); }
};

int main() {
    std::printf("-- entering scope --\n");
    {
        Tracer a("a");
        Tracer b("b");
    }
    std::printf("-- left scope --\n");
    return 0;
}
```

```text
-- entering scope --
construct a
construct b
destroy   b
destroy   a
-- left scope --
```

Destruction is the **exact reverse** of construction. That is not a stylistic choice, it is a
correctness guarantee: if `b` was constructed after `a`, then `b` might hold a pointer into `a`, so
`b` must go first. The compiler guarantees the reverse order everywhere — locals in a block, members
inside an object, objects in an array. You never have to think about it, and you should rely on it.

## Initialising members: the initialiser list

The `: name(n)` after the parameter list is a **member initialiser list**. There are two ways to give a
member its first value and they are not equivalent:

```cpp
// initialiser list — the member is constructed with this value
Widget::Widget(int n) : count_(n) {}

// body assignment — the member is default-constructed, then assigned
Widget::Widget(int n) { count_(n); }   // WRONG: this is not even an assignment
Widget::Widget(int n) { count_ = n; }  // body assignment
```

For an `int` the difference is a wasted write. For anything else it is a difference in behaviour, and
for one case it is a difference between compiling and not compiling:

```cpp bad
#include <cstdio>

struct Id {
    const int value;
    Id(int v) { value = v; }
};

int main() {
    Id id(7);
    std::printf("%d\n", id.value);
    return 0;
}
```

```text
constructor for 'Id' must explicitly initialize the const member 'value'
```

A `const` member has no value to assign to — it is set once, at construction, and never again. The
initialiser list is the only place that can happen. The same applies to a reference member and to a
member of a class that has no default constructor: **if a member cannot be default-constructed and then
assigned, only the initialiser list works.** Make it your default and you will never hit this.

Now the trap that catches everyone once. Members are initialised in **declaration order**, not in the
order you write the list:

```cpp warn
#include <cstdio>

struct Pair {
    int first;
    int second;
    Pair(int a) : second(a), first(a + 1) {}
};

int main() {
    Pair p(10);
    std::printf("first = %d, second = %d\n", p.first, p.second);
    return 0;
}
```

```text
field 'second' will be initialized after field 'first'
```

```text
first = 11, second = 10
```

The list says `second` first. The object does not care: `first` is declared first, so `first` is
initialised first, and the compiler is warning you that your list is a lie about the order. Here it is
harmless because neither initialiser reads the other. Write `Pair(int a) : first(second), second(a)` and
it stops being harmless — `first` would read `second` before `second` exists. **Keep the list in
declaration order** and the warning disappears along with the class of bug it was pointing at.

## Encapsulation: making invalid states impossible

A constructor is where an invariant gets established, and `private` is what stops anyone breaking it
later:

```cpp run
#include <cstdio>

class Range {
public:
    Range(int lo, int hi) : lo_(lo), hi_(hi) {
        if (lo_ > hi_) { int t = lo_; lo_ = hi_; hi_ = t; }
    }
    int lo() const { return lo_; }
    int hi() const { return hi_; }
    int span() const { return hi_ - lo_; }

private:
    int lo_;
    int hi_;
};

int main() {
    Range a(3, 10);
    Range b(10, 3);
    std::printf("a: lo = %d, hi = %d, span = %d\n", a.lo(), a.hi(), a.span());
    std::printf("b: lo = %d, hi = %d, span = %d\n", b.lo(), b.hi(), b.span());
    return 0;
}
```

```text
a: lo = 3, hi = 10, span = 7
b: lo = 3, hi = 10, span = 7
```

Both calls produce the same object, and `span()` can be a one-liner with no defensive check because
`lo_ <= hi_` is true for every `Range` that can ever exist. That is the payoff. A `struct` with public
`lo` and `hi` would need `span()` to handle the reversed case, and every *other* function that touched
it would need the same check, and one of them would forget. **The invariant is established in one place
and enforced by the compiler everywhere else.**

Two conventions worth naming. The trailing underscore (`lo_`) marks a member, so `lo_` and a parameter
named `lo` never collide. And the accessors are marked `const` — as Chapter 23 established, that is what
lets a `const Range` be read. Getters that only read should always be `const`.

## Defining methods out of line

A class declaration is also its interface, so it is normal to declare methods inside the class and
define the bodies somewhere else. The `ClassName::` prefix is the **scope resolution operator** and it
is required:

```cpp run
#include <cstdio>

class Counter {
public:
    Counter(int start);
    void bump();
    int value() const;

private:
    int n_;
};

Counter::Counter(int start) : n_(start) {}
void Counter::bump() { ++n_; }
int Counter::value() const { return n_; }

int main() {
    Counter c(10);
    c.bump();
    c.bump();
    std::printf("value = %d\n", c.value());
    return 0;
}
```

```text
value = 12
```

This is how almost all real C++ is written: a header declares the class, a `.cpp` file defines the
methods. We use the split in Chapter 26 when a class grows past one screen. Note that the `const` on
`value` has to be repeated on the definition — drop it and the compiler reports a definition that does
not match any declaration.

## static members

A member marked `static` belongs to the class, not to any object. That makes it the right tool for
things that are true of the type as a whole — a count of live objects, a shared table, a default value:

```cpp run
#include <cstdio>

class Widget {
public:
    Widget()  { ++live_; }
    ~Widget() { --live_; }
    static int live() { return live_; }

private:
    static int live_;
};

int Widget::live_ = 0;

int main() {
    std::printf("live = %d\n", Widget::live());
    {
        Widget a, b;
        std::printf("live = %d\n", Widget::live());
    }
    std::printf("live = %d\n", Widget::live());
    return 0;
}
```

```text
live = 0
live = 2
live = 0
```

A static data member must be **defined once** outside the class, which is what `int Widget::live_ = 0;`
does. Miss it and you get an `Undefined symbols` **linker** error, not a compiler error — the same
distinction Chapter 14 taught. A static method has no `this`, so it cannot touch non-static members;
`Widget::live()` is called with the class name, not an object.

The compiler will also tell you when a member is dead weight:

```cpp warn
#include <cstdio>

class Cache {
public:
    explicit Cache(int n) : size_(n) {}
    int size() const { return size_; }

private:
    int size_;
    int spare_;
};

int main() {
    Cache c(8);
    std::printf("size = %d\n", c.size());
    return 0;
}
```

```text
private field 'spare_' is not used
```

That is `-Wunused-private-field`, and it is one of the better reasons to compile with `-Wall -Wextra`.
A private member nothing reads is either a bug or a fossil, and the compiler found it without you
reading the whole class.

## explicit

One-argument constructors double as **implicit conversions**, and that is usually not what you want:

```cpp bad
#include <cstdio>

class Meters {
public:
    explicit Meters(double v) : v_(v) {}
    double value() const { return v_; }

private:
    double v_;
};

static void show(Meters m) { std::printf("%.1f m\n", m.value()); }

int main() {
    show(Meters(2.5));
    show(2.5);
    return 0;
}
```

```text
no known conversion from 'double' to 'Meters'
```

Without `explicit`, `show(2.5)` would compile: the compiler would silently construct a `Meters` from
`2.5` and hand it over. With it, `show(Meters(2.5))` is required, and the reader of that call site can
see a `Meters` being made. **Mark every one-argument constructor `explicit`** unless you are
deliberately building a conversion, because the implicit version turns a typo into a silent unit
mismatch. Note that `Meters m = 2.5;` is rejected for the same reason.

## The RAII class

Now the payoff for everything above. A class that acquires a resource in its constructor and releases
it in its destructor is the C++ answer to every cleanup path you wrote by hand in Part III:

```cpp run-san
#include <cstdio>
#include <cstdlib>
#include <cstring>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n), data_(static_cast<char *>(std::malloc(n))) {}

    ~Buffer() {
        std::free(data_);
        std::printf("freed %zu bytes\n", n_);
    }

    char *data() const { return data_; }
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
    char *data_;
};

static void fill(Buffer &b, const char *text) {
    std::size_t len = std::strlen(text);
    if (len + 1 > b.size()) return;
    std::memcpy(b.data(), text, len + 1);
}

int main() {
    Buffer buf(16);
    fill(buf, "hello");
    std::printf("size = %zu, text = %s\n", buf.size(), buf.data());
    return 0;
}
```

```text
size = 16, text = hello
freed 16 bytes
```

Read the order of those two lines. `main` printed its line, then returned, and *then* the destructor
printed. There is no `free` anywhere in `main`. The cleanup happened because a scope ended. That is
what "resource acquisition is initialisation" means — RAII — and it is the single most important idea
in the language. `std::string`, `std::vector`, `std::unique_ptr` and every file and socket wrapper in
the standard library are built on exactly this pattern.

The `static_cast<char *>` is the C++ requirement from Chapter 22: `std::malloc` returns `void *` and
C++ will not convert it silently. The cast is not noise, it is the place where you assert the
allocation size is right.

:::pitfall Your RAII type copies by default, and the copy double-frees

`Buffer` has no copy constructor, so the compiler writes one for you — and the compiler's version
copies the *pointer*, not the memory it points at:

```cpp
Buffer a(16);
Buffer b = a;    // b.data_ == a.data_  — two owners, one allocation
```

Both objects now believe they own the same block, and both destructors will call `free` on it. The
second one is a double free. The compiler will not warn you, because nothing here is a type error.

This is not a corner case: it is *the* reason the "rule of three" exists, and it is why every RAII type
in the standard library either forbids copying or implements it properly. Chapter 25 is entirely about
this — how to detect it, how to write the copy that allocates its own memory, and how to move instead
of copy. Until then, treat any RAII class you write as uncopyable, and do not pass one by value.

:::

:::scenario The log file that was never closed

A service writes a line to a log file every time it finishes a build. After a week in production it
starts failing to open sockets, and the error is `Too many open files` — it has leaked one file
descriptor per failed build. Here is the shape of the bug, reduced to its essentials. Both functions
write a line and both refuse a line that is too long:

```cpp run
#include <cstdio>
#include <cstring>

/* ---- the C version: one early return forgets to close ---- */
static bool record_c(const char *path, const char *line) {
    std::FILE *f = std::fopen(path, "w");
    if (f == nullptr) return false;
    if (std::strlen(line) > 80) return false;      /* BUG: no fclose on this path */
    std::fputs(line, f);
    std::fputs("\n", f);
    std::fclose(f);
    std::printf("C: closed %s\n", path);
    return true;
}

/* ---- the C++ version: the destructor owns the close ---- */
class File {
public:
    File(const char *path, const char *mode)
        : path_(path), f_(std::fopen(path, mode)) {}

    ~File() {
        if (f_ != nullptr) {
            std::fclose(f_);
            std::printf("C++: closed %s\n", path_);
        }
    }

    bool ok() const { return f_ != nullptr; }
    void write(const char *text) const { if (f_ != nullptr) std::fputs(text, f_); }

private:
    const char *path_;
    std::FILE *f_;
};

static bool record_cpp(const char *path, const char *line) {
    File out(path, "w");
    if (!out.ok()) return false;
    if (std::strlen(line) > 80) return false;
    out.write(line);
    out.write("\n");
    return true;
}

int main() {
    const char *short_line = "build 41 finished";
    const char *long_line  = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

    std::printf("--- short line ---\n");
    std::printf("returned %d\n", (int)record_c("c.log", short_line));
    std::printf("returned %d\n", (int)record_cpp("cpp.log", short_line));

    std::printf("--- long line (early return) ---\n");
    std::printf("returned %d\n", (int)record_c("c.log", long_line));
    std::printf("returned %d\n", (int)record_cpp("cpp.log", long_line));
    return 0;
}
```

```text
--- short line ---
C: closed c.log
returned 1
C++: closed cpp.log
returned 1
--- long line (early return) ---
returned 0
C++: closed cpp.log
returned 0
```

Look at the last four lines, which are the whole lesson. `record_c` takes the early return and prints
**no** "closed" line — the handle is gone and nothing can close it now. `record_cpp` takes the same
early return, and `C++: closed cpp.log` appears **before** the outer `returned 0` prints, because the
destructor ran while the callee was still unwinding.

The C fix would be a second `fclose` before the second `return`, and then a third when someone adds a
third early return. The C++ fix is to not write any of them. The rule that follows: **if a function
acquires a resource, wrap it in a type whose destructor releases it, and then the number of exit paths
stops mattering.**

:::

## Key takeaways

- `struct` and `class` are the same construct; `struct` defaults to public members and `class` to
  private ones, and nothing else differs.
- A constructor runs at creation and a destructor at destruction, and destruction is always the exact
  reverse of construction — for locals in a block, for members in an object, and for array elements.
- Members are initialised in **declaration order**, not in the order written in the initialiser list;
  `-Wall -Wextra` warns when the two disagree.
- A `const` member, a reference member, or a member with no default constructor can only be
  initialised through the initialiser list, never by assignment in the constructor body.
- `private` plus a constructor that establishes an invariant makes an invalid object impossible to
  construct, and lets every other method skip its defensive checks.
- A `static` data member needs exactly one definition outside the class, or you get a linker error
  rather than a compiler error.
- Mark one-argument constructors `explicit`, so a value never silently becomes an object at a call site.
- An RAII class acquires in the constructor and releases in the destructor, which makes cleanup
  automatic on every exit path — including early returns and (Chapter 30) exceptions.

## Practice

- [ ] Build a `Rectangle` class holding `int w_` and `int h_`, with a constructor that clamps a
  negative argument to `0`, plus `area()` and `perimeter()` accessors. Show both a normal rectangle and
  one built from a negative width.
- [ ] Build a `Hits` class with an instance method `hit()` and two counters: a per-object `calls()` and
  a `static total()` shared by every object. Two objects, three hits on one and one on the other.
- [ ] Build a `Stack` class wrapping a fixed array of 8 `int`s, with `push`, `pop` and `size`. `push`
  must refuse to overflow and `pop` must refuse to underflow, both by returning `false`. Drive it past
  both limits.
- [ ] A class declares `const int id_;` and its constructor assigns `id_ = v;` in the body. Fix it,
  and say in one sentence why the body cannot work.
- [ ] Build a `Marker` class that prints on construction and on destruction, and use it to prove that
  the destructor runs when a function takes an **early return**.
- [ ] Build a `Temperature` class storing Celsius with a one-argument constructor. Make it `explicit`,
  then show the compiler rejecting `Temperature t = 100.0;` and accepting `Temperature t(100.0);`.

## Solutions

:::solution Exercise 1

```cpp run
#include <cstdio>

class Rectangle {
public:
    Rectangle(int w, int h) : w_(w > 0 ? w : 0), h_(h > 0 ? h : 0) {}
    int area() const { return w_ * h_; }
    int perimeter() const { return 2 * (w_ + h_); }

private:
    int w_;
    int h_;
};

int main() {
    Rectangle a(3, 4);
    Rectangle b(-2, 5);
    std::printf("a: area = %d, perimeter = %d\n", a.area(), a.perimeter());
    std::printf("b: area = %d, perimeter = %d\n", b.area(), b.perimeter());
    return 0;
}
```

```text
a: area = 12, perimeter = 14
b: area = 0, perimeter = 10
```

The clamping happens in the initialiser list, so a `Rectangle` is valid the instant it exists — there
is no window in which `w_` holds `-2` and some other method might read it. `b` has area `0` and
perimeter `10`, which is the arithmetic you get from `w_ = 0, h_ = 5`.

:::

:::solution Exercise 2

```cpp run
#include <cstdio>

class Hits {
public:
    void hit() { ++calls_; ++total_; }
    int calls() const { return calls_; }
    static int total() { return total_; }

private:
    int calls_ = 0;
    static int total_;
};

int Hits::total_ = 0;

int main() {
    Hits a, b;
    a.hit();
    a.hit();
    a.hit();
    b.hit();
    std::printf("a.calls() = %d\n", a.calls());
    std::printf("b.calls() = %d\n", b.calls());
    std::printf("Hits::total() = %d\n", Hits::total());
    return 0;
}
```

```text
a.calls() = 3
b.calls() = 1
Hits::total() = 4
```

`calls_` is per-object and `total_` is per-class, which is exactly the distinction `static` draws. Note
`int Hits::total_ = 0;` at file scope: without that one definition the program compiles and then fails
to link.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>

class Stack {
public:
    bool push(int v) {
        if (n_ == CAP) return false;
        data_[n_++] = v;
        return true;
    }
    bool pop(int &out) {
        if (n_ == 0) return false;
        out = data_[--n_];
        return true;
    }
    int size() const { return n_; }

private:
    static const int CAP = 8;
    int data_[CAP] = {};
    int n_ = 0;
};

int main() {
    Stack s;
    for (int i = 1; i <= 9; i++) {
        if (!s.push(i)) std::printf("push %d rejected, size = %d\n", i, s.size());
    }
    int v = 0;
    while (s.pop(v)) std::printf("popped %d\n", v);
    std::printf("empty? size = %d\n", s.size());
    return 0;
}
```

```text
push 9 rejected, size = 8
popped 8
popped 7
popped 6
popped 5
popped 4
popped 3
popped 2
popped 1
empty? size = 0
```

The two bounds checks are the invariant, and because `n_` is private nothing outside the class can
move it. `pop` takes its result through a reference parameter (Chapter 23) so it can return `bool`
for success and still hand back the value. `int data_[CAP] = {};` zero-initialises the array so no
element is ever indeterminate.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>

class Session {
public:
    explicit Session(int id) : id_(id) {}
    int id() const { return id_; }

private:
    const int id_;
};

int main() {
    Session s(42);
    std::printf("id = %d\n", s.id());
    return 0;
}
```

```text
id = 42
```

A `const` member is set once at construction, so there is no assignment for the constructor body to
perform — the initialiser list is the only place a value can be given. A useful side effect: because
`id_` can never change, this class has no valid assignment operator, so the compiler refuses to
generate one.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>

class Marker {
public:
    explicit Marker(const char *name) : name_(name) { std::printf("  enter %s\n", name_); }
    ~Marker() { std::printf("  leave %s\n", name_); }

private:
    const char *name_;
};

static void validate(int n) {
    Marker m("validate");
    if (n < 0) {
        std::printf("  rejected %d\n", n);
        return;
    }
    std::printf("  accepted %d\n", n);
}

int main() {
    validate(5);
    validate(-1);
    return 0;
}
```

```text
  enter validate
  accepted 5
  leave validate
  enter validate
  rejected -1
  leave validate
```

`leave validate` appears on both calls, including the one that returned early from the middle of the
function. That is the RAII guarantee in its smallest possible form, and it is the reason `Marker` is a
useful thing to keep in your toolbox: dropping one at the top of a function tells you whether every
path out of it is really covered.

:::

:::solution Exercise 6

```cpp run
#include <cstdio>

class Temperature {
public:
    explicit Temperature(double celsius) : c_(celsius) {}
    double celsius() const { return c_; }
    double fahrenheit() const { return c_ * 9.0 / 5.0 + 32.0; }

private:
    double c_;
};

int main() {
    Temperature t(100.0);
    std::printf("%.1f C = %.1f F\n", t.celsius(), t.fahrenheit());
    return 0;
}
```

```text
100.0 C = 212.0 F
```

And the line that `explicit` rejects:

```cpp bad
class Temperature {
public:
    explicit Temperature(double c) : c_(c) {}

private:
    double c_;
};

int main() {
    Temperature t = 100.0;
    return 0;
}
```

```text
no viable conversion from 'double' to 'Temperature'
```

Without `explicit` that line would compile, and the copy-initialisation syntax would hide the fact
that a constructor ran. `Temperature t(100.0);` says what it does.

:::
