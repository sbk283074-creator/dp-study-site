---
chapter: 31
part: 4
title: Operator Overloading and Iterators
summary: Teach your own types to work with +, ==, [], << and the range-for loop, learn which operators you may not touch and why symmetry decides member versus non-member, and write an iterator that presents a logical sequence over storage that does not match it.
minutes: 75
tags: [operator-overloading, iterators, range-for, iterator_traits, functor, non-member-operator, compound-assignment, iterator-invalidation, forward-iterator]
---

Everything you have written so far has been called by name. That is fine for a program, and it is
miserable for a *type*. If a `Vec2` has to be combined with `add(a, scale(b, 2.0))`, every reader of
every line has to re-derive what that expression means. If it can be written `a + b * 2.0`, the
reader already knows: multiplication binds tighter, addition combines, and the result is a `Vec2`.
That is the entire argument for overloading operators — not shorter code, but code whose meaning is
already in the reader's head.

The second half of this chapter is the other half of the same idea. An iterator is what lets a
container you invented be used by `for (auto x : c)` and by every algorithm in `<algorithm>` that
applies to it. Together they are the difference between a class that *has* data and a type that
*participates* in the language.

## What you are buying

Here is the named-function version.

```cpp run
// The same arithmetic, written with named functions. Nothing here is wrong --
// the point is what the reader has to hold in their head to read it.
#include <cstdio>

struct Vec2 { double x; double y; };

Vec2 add(Vec2 a, Vec2 b)   { return Vec2{a.x + b.x, a.y + b.y}; }
Vec2 scale(Vec2 a, double k) { return Vec2{a.x * k, a.y * k}; }

void print(Vec2 v) { std::printf("(%.1f, %.1f)\n", v.x, v.y); }

int main() {
    Vec2 a{1.0, 2.0};
    Vec2 b{3.0, 4.0};
    print(add(a, scale(b, 2.0)));
    return 0;
}
```

```text
(7.0, 10.0)
```

Now the same thing with operators.

```cpp run
#include <cstdio>

struct Vec2 { double x; double y; };

// Non-member: neither operand is privileged, which is what lets `2.0 * b`
// work later on.
Vec2 operator+(Vec2 a, Vec2 b)    { return Vec2{a.x + b.x, a.y + b.y}; }
Vec2 operator*(Vec2 a, double k)  { return Vec2{a.x * k, a.y * k}; }
Vec2 operator*(double k, Vec2 a)  { return a * k; }

void print(Vec2 v) { std::printf("(%.1f, %.1f)\n", v.x, v.y); }

int main() {
    Vec2 a{1.0, 2.0};
    Vec2 b{3.0, 4.0};
    print(a + b * 2.0);   // * still binds tighter than +: a + (b * 2)
    print(2.0 * a + b);
    return 0;
}
```

```text
(7.0, 10.0)
(5.0, 8.0)
```

Neither program is more correct than the other. The second one is *readable* by someone who has not
seen `Vec2` before, because the operators carry rules — precedence, associativity, and a rough
expectation that `+` combines and `*` scales — that a function name has to establish from scratch
every single time.

## The rules that are not negotiable

Overloading is not extension. You do not get to add symbols, and you do not get to change what the
existing ones mean structurally. Four limits matter in practice:

- **The set of operators is fixed.** `+ - * / % ^ & | ~ ! = < > += -= *= /= %= ^= &= |= << >> >>= <<= == != <= >= && || ++ -- , ->* -> ( ) [ ] new delete` and nothing else.
- **Arity and precedence are fixed.** `!` is unary and `%` binds tighter than `+`, whatever your type does. You may change what an operator *does* but never how it *parses*.
- **At least one operand must be a user-defined type.** You cannot redefine `int + int`.
- **Four operators must be members:** `=`, `[]`, `()`, and `->`.

The first two are enforced at compile time. Attempting to give `!` two parameters:

```cpp bad
// Arity is fixed by the language. `!` is unary, so an operator! taking two
// parameters is not an overload of anything -- it is a syntax error.
struct Vec2 { double x; double y; };

bool operator!(Vec2 a, int extra) { return a.x == 0.0 && a.y == 0.0 && extra == 0; }

int main() { return 0; }
```

```text
error: overloaded 'operator!' must be a unary operator (has 2 parameters)
```

Note that the complaint is about the *shape* of the declaration, not about the body. The compiler
never got as far as what your operator was going to do.

And `operator=` as a free function:

```cpp bad
// Four operators must be members, because they act on an object that already
// exists. operator= is one of them; a free function cannot be it.
struct Vec2 { double x; double y; };

Vec2 &operator=(Vec2 &a, const Vec2 &b) {
    a.x = b.x;
    a.y = b.y;
    return a;
}

int main() { return 0; }
```

```text
error: overloaded 'operator=' must be a non-static member function
```

`=` acts on an object that already exists, so it has to be a member of the type it assigns to. The
same reasoning applies to `[]`, `()` and `->`: all four take "the object" as their starting point in
a way a free function cannot express.

## Member or non-member: let symmetry decide

An operator declared as a member has the left operand as `this`. That is the whole rule, and it has
one consequence you will hit immediately: a member `operator*` makes `v * 2.0` work and `2.0 * v`
fail.

```cpp bad
// operator* as a MEMBER: the left operand must be a Vec2, because a member
// operator is a call with the left operand as `this`.
#include <cstdio>

struct Vec2 {
    double x;
    double y;
    Vec2 operator*(double k) const { return Vec2{x * k, y * k}; }
};

int main() {
    Vec2 a{1.0, 2.0};
    Vec2 b = 2.0 * a;                 // scalar on the left
    std::printf("%.1f %.1f\n", b.x, b.y);
    return 0;
}
```

```text
error: invalid operands to binary expression ('double' and 'Vec2')
```

The left operand is a `double`, and a `double` has no member `operator*`. Nothing is wrong with the
declaration — it is simply the wrong shape for an operation that ought to be symmetric.

When the operation should work in both orders, write it as a non-member (a hidden friend if it needs
access to private members):

```cpp
struct Vec2 { double x; double y; };
Vec2 operator*(Vec2 a, double k) { return Vec2{a.x * k, a.y * k}; }
Vec2 operator*(double k, Vec2 a) { return a * k; }   // the mirror image
```

Two rules of thumb that follow: **if the operator modifies its left operand** (`+=`, `++`, `=`) or
**must be a member** (`[]`, `()`, `->`), make it a member. Otherwise prefer a non-member, because
non-members cannot accidentally depend on `this` and because they accept conversions on *both*
sides.

### `operator<<` has to be a non-member

This is the case people get wrong most often, and it is the same asymmetry one more time: the stream
is on the left, and you do not own `std::ostream`.

```cpp bad
// The same operator written as a member. It compiles -- and it is unusable,
// because `os << v` has the stream on the left, where `this` is not.
#include <sstream>

struct Vec2 {
    double x;
    double y;
    std::ostream &operator<<(std::ostream &os) const { return os << x; }
};

int main() {
    std::ostringstream out;
    out << Vec2{1.5, 2.5};
    return 0;
}
```

```text
error: invalid operands to binary expression ('std::ostringstream' (aka 'basic_ostringstream<char>') and 'Vec2')
```

Written as a non-member, with the stream as the first parameter, it works — and because it returns
the stream by reference, calls chain:

```cpp run
// operator<< has to be a non-member: the stream is the LEFT operand, and you do
// not own std::ostream.
#include <cstdio>
#include <sstream>

struct Vec2 { double x; double y; };

std::ostream &operator<<(std::ostream &os, Vec2 v) {
    return os << "(" << v.x << ", " << v.y << ")";
}

int main() {
    std::ostringstream out;
    out << Vec2{1.5, 2.5} << " and " << Vec2{-1.0, 0.0};
    std::printf("%s\n", out.str().c_str());
    return 0;
}
```

```text
(1.5, 2.5) and (-1, 0)
```

The `return os << ...;` shape is not decoration. Returning the same stream is what makes
`out << a << " and " << b` one expression, and it is why the return type is
`std::ostream &` rather than `void`.

## Compound first, then the plain operator

There are two operators to write for addition — `+` and `+=` — and one of them is the real one.
Implement `+=` once, correctly, and then express `+` in terms of it:

```cpp run
// Implement += once, then express + in terms of it. One place to get the
// arithmetic right; the copy semantics come for free.
#include <cstdio>

struct Counter {
    int n = 0;
    Counter &operator+=(int k) { n += k; return *this; }   // mutates, returns *this
};

Counter operator+(Counter c, int k) { c += k; return c; }  // takes a copy

int main() {
    Counter a{10};
    a += 5;                       // a is modified in place
    Counter b = a + 3;            // a is untouched; b is a new object
    std::printf("a=%d b=%d\n", a.n, b.n);

    (b += 1) += 2;                // chains, because += returns a reference
    std::printf("b=%d\n", b.n);
    return 0;
}
```

```text
a=15 b=18
b=21
```

`+=` mutates and returns `Counter &`, a reference to the object it modified, which is what makes
`(b += 1) += 2` legal and meaningful. `+` takes its argument **by value** — so it is already working
on a copy — applies `+=` to that copy, and returns it. One definition holds the arithmetic; the other
is three lines that cannot disagree with it.

The payoff is visible in what the copy buys. Here is the same type, and an attempt to chain onto the
result of `+`:

```cpp run
// `+` returns a temporary. Calling += on it is legal -- member functions may be
// called on rvalues -- so this compiles, runs, and quietly achieves nothing.
#include <cstdio>

struct Counter {
    int n = 0;
    Counter &operator+=(int k) { n += k; return *this; }
};

Counter operator+(Counter c, int k) { c += k; return c; }

int main() {
    Counter a{10};
    (a + 3) += 5;                 // modifies the temporary, then drops it
    std::printf("a=%d\n", a.n);   // a never changed
    return 0;
}
```

```text
a=10
```

**This compiles.** A member function may be called on an rvalue, so `+=` runs on the temporary that
`a + 3` produced, increments it to 18, and then the temporary is destroyed. `a` is still 10, and no
compiler diagnostic mentions the problem.

:::danger The expensive operators are the quiet ones
A failed compile costs you a minute. This one costs you an afternoon: the code reads as though it
does something, it runs, and the value you expected to change did not. The general form of the bug is
"an operation that returns by value was used as though it returned a reference". If an expression
that looks like it mutates something is followed by no change, check the return type before you check
the arithmetic.
:::

## Comparison: one does not give you the others

Defining `==` says nothing about `!=`:

```cpp bad
// C++17 does NOT derive != from ==. Defining one says nothing about the other.
#include <cstdio>

struct Point { int x; int y; };

bool operator==(Point a, Point b) { return a.x == b.x && a.y == b.y; }

int main() {
    Point p{1, 2};
    Point q{1, 2};
    std::printf("%s\n", (p != q) ? "different" : "same");
    return 0;
}
```

```text
error: invalid operands to binary expression ('Point' and 'Point')
```

In C++17 you write both. The usual arrangement is to define `==` and `<`, then derive the rest so
that they cannot drift apart:

```cpp
bool operator==(const Point &a, const Point &b) { return a.x == b.x && a.y == b.y; }
bool operator< (const Point &a, const Point &b) {
    return a.x < b.x || (a.x == b.x && a.y < b.y);
}
bool operator!=(const Point &a, const Point &b) { return !(a == b); }
bool operator<=(const Point &a, const Point &b) { return !(b < a); }
bool operator> (const Point &a, const Point &b) { return b < a; }
bool operator>=(const Point &a, const Point &b) { return !(a < b); }
```

Six lines derived from two, and they stay consistent because there is only one place where "equal"
is defined and one place where "less" is. C++20 replaces all six with a single `operator<=>` — see
Chapter 33, where the language does the deriving for you.

## `[]`, `()`, and `->`

Subscripting comes in two flavours, and you usually need both: the non-const overload returns a
reference you can assign through, and the const overload returns a reference you can only read.

```cpp run
// operator[] in const and non-const flavours. The const overload is what lets a
// read-only caller still index -- without it, `const Row` would be unusable.
#include <cstdio>

struct Row {
    int cells[3] = {0, 0, 0};
    int       &operator[](int i)       { return cells[i]; }
    const int &operator[](int i) const { return cells[i]; }
};

int main() {
    Row r;
    r[1] = 7;                 // writes through the non-const overload
    const Row &cr = r;
    std::printf("%d %d\n", r[1], cr[1]);
    return 0;
}
```

```text
7 7
```

Without the const overload, `const Row` could not be indexed at all, which would make every
read-only function that takes one by reference unusable.

`operator()` makes an object callable. A *functor* differs from a free function in one way that
matters: it can carry state.

```cpp run
// operator() makes an object callable. A "functor" carries state a free
// function cannot, which is why algorithms take one.
#include <algorithm>
#include <cstdio>
#include <vector>

struct DivisibleBy {
    int d;
    bool operator()(int n) const { return n % d == 0; }
};

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    int threes = 0;
    for (int n : v) if (DivisibleBy{3}(n)) ++threes;
    std::printf("multiples of 3: %d\n", threes);

    long twos = std::count_if(v.begin(), v.end(), DivisibleBy{2});
    std::printf("multiples of 2: %ld\n", twos);
    return 0;
}
```

```text
multiples of 3: 3
multiples of 2: 5
```

`DivisibleBy{3}` is an object holding `d = 3`, and `DivisibleBy{3}(n)` is a call. The same object
works with `std::count_if` because the algorithm only requires that its predicate be callable with
one argument — it does not care whether that callable is a function pointer, a lambda, or a struct
with `operator()`.

`operator->` must return a pointer, or something that itself has `operator->`. The language then
applies `->` again to the result:

```cpp run
// operator-> must return something that itself has -> (or is a pointer).
// The language then applies -> again, which is what makes the chain work.
#include <cstdio>

struct Point {
    int x;
    int y;
    void show() const { std::printf("(%d, %d)\n", x, y); }
};

struct Handle {
    Point *p;
    Point *operator->() { return p; }
};

int main() {
    Point pt{3, 4};
    Handle h{&pt};
    h->show();
    std::printf("x=%d\n", h->x);
    return 0;
}
```

```text
(3, 4)
x=3
```

This is what makes smart pointers work at all: `p->member()` has to reach `member` through the
wrapper, and `operator->` returning the raw pointer is the mechanism.

## What not to overload

The short answer is: stop when the operator's meaning would surprise the reader. Three cases are
worth stating precisely, because the first one is a real trap rather than a style opinion.

```cpp run
// Overloaded && and || are ordinary function calls, and a function call
// evaluates all of its arguments. Short-circuit evaluation is gone.
#include <cstdio>

struct Bool { bool v; };

Bool operator&&(Bool a, Bool b) { return Bool{a.v && b.v}; }

Bool note(const char *name, bool v) {
    std::printf("evaluated %s\n", name);
    return Bool{v};
}

int main() {
    Bool r = note("left", false) && note("right", true);
    std::printf("result=%d\n", static_cast<int>(r.v));
    return 0;
}
```

```text
evaluated left
evaluated right
result=0
```

**Overloaded `&&` and `||` lose short-circuit evaluation.** `note("left", false) && note("right",
true)` evaluated *both* sides — the right one printed, and the program only got the right answer by
accident, because a function call evaluates all of its arguments before the body runs. With the
built-in operators, `false && f()` never calls `f`, and an entire category of guards
(`p != nullptr && p->field == 3`) depends on that. Do not overload these two.

The other two are smaller: `operator&`, `operator,` and `operator<<` for anything other than shifting
or streaming will be misread by every person who sees the call site, and an `operator+` that mutates
its left operand will be misread by every person who sees *that*. An overloaded operator is a promise
about behaviour; keep them.

:::pitfall An overload that lies is worse than no overload
`operator+` that appends to the left operand, `operator==` that is not transitive, `operator<` that
is not a strict weak ordering — each of these compiles and passes a quick test, then breaks inside
`std::sort` or `std::map` in a way that looks like a library bug. If you cannot honour the
convention the operator implies, use a named function. The reader will thank you, and so will every
algorithm that makes assumptions about the operator.
:::

## Iterators: what a range-for actually requires

`for (int x : range)` is not magic, and it is not restricted to `std::vector`. It expands into
something close to:

```cpp
auto &&__r = range;
auto __it  = begin(__r);      // or __r.begin()
auto __end = end(__r);        // or __r.end()
for (; __it != __end; ++__it) {
    int x = *__it;
    ...
}
```

So a type is a *range* if `begin`/`end` give you something with `!=`, prefix `++`, and unary `*`.
Those three requirements are real. Here is a type that has two of them:

```cpp bad
// A range-for needs begin/end, and it needs ++, * and != on what they return.
// This iterator has the first two but not the comparison, so the loop cannot be
// written -- the requirement is real, not a convention.
#include <cstdio>

struct Iter {
    int i;
    int  operator*() const { return i; }
    Iter &operator++() { ++i; return *this; }
};

struct Range {
    Iter begin() { return Iter{0}; }
    Iter end()   { return Iter{3}; }
};

int main() {
    for (int x : Range{}) std::printf("%d\n", x);
    return 0;
}
```

```text
error: invalid operands to binary expression ('Iter' and 'Iter')
```

`Iter` has `*` and `++`, but no `!=`, so the loop cannot even be written. Note where the error
points: at the `for`, not at the missing operator — and note the second line, which names the
implicit `operator!=` call the expansion needs. When a range-for fails to compile on your own type,
this is the diagnostic to expect.

## The easiest iterator is one you already have

For contiguous storage, a raw pointer satisfies every requirement of a random access iterator, so
`begin` and `end` are two typedefs and two one-line functions:

```cpp run
// The easiest iterator is one you already had: for contiguous storage, a
// pointer satisfies every requirement, so the container just hands one out.
#include <algorithm>
#include <cstdio>

template <typename T, int N>
struct FixedVec {
    T data[N];
    int n = 0;

    void push(const T &t) { data[n++] = t; }

    using iterator       = T *;
    using const_iterator = const T *;

    iterator       begin()       { return data; }
    iterator       end()         { return data + n; }
    const_iterator begin() const { return data; }
    const_iterator end()   const { return data + n; }
};

int main() {
    FixedVec<int, 8> f;
    for (int i : {5, 3, 9, 1}) f.push(i);

    for (int x : f) std::printf("%d ", x);
    std::printf("\n");

    auto it = std::find(f.begin(), f.end(), 9);
    std::printf("9 is at index %ld\n", it - f.begin());
    std::printf("count of 3: %ld\n",
                std::count(f.begin(), f.end(), 3));
    return 0;
}
```

```text
5 3 9 1 
9 is at index 2
count of 3: 1
```

`std::find` and `std::count` work on it with no further effort, because they are templates over
iterators and never mention the container. This is the single most important consequence of the
iterator design: **an algorithm you did not write, written years before your type existed, works on
your type** as long as your iterator answers the questions the algorithm asks.

## An iterator that has to do work

A ring buffer is the interesting case. Its elements are *not* in storage order once it has wrapped
around, so the iterator has to convert a logical position into a storage index on every dereference:

```cpp run
// A ring buffer: the elements are NOT in storage order once it has wrapped, so
// the iterator has to do arithmetic. That is the whole job of an iterator --
// present a logical sequence over whatever layout you actually chose.
#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <iterator>
#include <numeric>

template <typename T, std::size_t N>
class Ring {
    T buf[N];
    std::size_t head = 0;    // next slot to write
    std::size_t count = 0;   // how many are live

public:
    void push(T v) {
        buf[head] = v;
        head = (head + 1) % N;
        if (count < N) ++count;
    }
    std::size_t size() const { return count; }

    class iterator {
        Ring *owner;
        std::size_t index;                 // logical position, 0 .. count
    public:
        // The five typedefs are how the standard library asks what this is.
        using iterator_category = std::forward_iterator_tag;
        using value_type        = T;
        using difference_type   = std::ptrdiff_t;
        using pointer           = T *;
        using reference         = T &;

        iterator(Ring *o, std::size_t i) : owner(o), index(i) {}

        reference operator*() const {
            std::size_t start = (owner->head + N - owner->count) % N;
            return owner->buf[(start + index) % N];
        }
        iterator &operator++() { ++index; return *this; }
        iterator  operator++(int) { iterator tmp = *this; ++index; return tmp; }
        bool operator==(const iterator &o) const {
            return owner == o.owner && index == o.index;
        }
        bool operator!=(const iterator &o) const { return !(*this == o); }
    };

    iterator begin() { return iterator(this, 0); }
    iterator end()   { return iterator(this, count); }
};

int main() {
    Ring<int, 3> r;
    for (int i = 1; i <= 5; ++i) r.push(i);   // 1 and 2 are overwritten

    std::printf("size=%zu contents:", r.size());
    for (int x : r) std::printf(" %d", x);
    std::printf("\n");

    auto it = std::find(r.begin(), r.end(), 4);
    std::printf("found 4: %s\n", it != r.end() ? "yes" : "no");
    std::printf("sum=%d\n", std::accumulate(r.begin(), r.end(), 0));
    return 0;
}
```

```text
size=3 contents: 3 4 5
found 4: yes
sum=12
```

Four things in there are worth isolating.

- **The five typedefs** (`iterator_category`, `value_type`, `difference_type`, `pointer`,
  `reference`) are how `std::iterator_traits` asks what this is. Algorithms read them; if you omit
  them, `std::iterator_traits<It>` cannot answer and the algorithms stop compiling.
- **`operator*` does the wrap-around arithmetic**, which is exactly the freedom an iterator buys
  you: the caller sees `3 4 5` in logical order while the storage holds `4 5 3`.
- **`operator++(int)`** — the postfix form, distinguished by the dummy `int` parameter — must return
  a copy of the *old* iterator. That is why it is three lines and the prefix form is two.
- **`end()` returns `iterator(this, count)`**, a one-past-the-end position that is never
  dereferenced. Every iterator range in the standard library is half-open: `[begin, end)`.

## Categories, and what they buy you

An iterator category is a promise about which operations are cheap. `std::iterator_traits` publishes
it, and you can read it back:

```cpp run
// iterator_traits is where a container declares what its iterator can do. The
// algorithms read that answer and refuse the ones they cannot honour.
#include <cstdio>
#include <iterator>
#include <list>
#include <type_traits>
#include <vector>

template <typename It>
const char *category() {
    using Cat = typename std::iterator_traits<It>::iterator_category;
    if      constexpr (std::is_same_v<Cat, std::random_access_iterator_tag>) return "random access";
    else if constexpr (std::is_same_v<Cat, std::bidirectional_iterator_tag>) return "bidirectional";
    else if constexpr (std::is_same_v<Cat, std::forward_iterator_tag>)       return "forward";
    else if constexpr (std::is_same_v<Cat, std::input_iterator_tag>)         return "input";
    else return "other";
}

int main() {
    std::printf("vector<int>::iterator : %s\n", category<std::vector<int>::iterator>());
    std::printf("list<int>::iterator   : %s\n", category<std::list<int>::iterator>());
    std::printf("int*                  : %s\n", category<int *>());
    return 0;
}
```

```text
vector<int>::iterator : random access
list<int>::iterator   : bidirectional
int*                  : random access
```

- **input / output** — single pass, read or write once. Stream iterators live here.
- **forward** — multi-pass, only `++`. `std::forward_list`, and the `Ring::iterator` above.
- **bidirectional** — also `--`. `std::list`, `std::map`, `std::set`.
- **random access** — also `+ n`, `- n`, `[]`, and `<`. `std::vector`, `std::deque`, and pointers.

The category is not documentation; it is enforced. `std::sort` needs to jump around, so it computes
`last - first` — and a list iterator has no subtraction:

```cpp bad
// std::sort needs to jump around (it computes `it + n`), so it demands random
// access. A list iterator is bidirectional, and the refusal happens at compile
// time rather than by producing a wrong answer at run time.
#include <algorithm>
#include <list>

int main() {
    std::list<int> l{3, 1, 2};
    std::sort(l.begin(), l.end());
    return 0;
}
```

```text
error: invalid operands to binary expression ('std::__list_iterator<int, void *>' and 'std::__list_iterator<int, void *>')
```

The error points into `<algorithm>` internals rather than at your call, which is the signature of a
requirement violation: the mistake is at `std::sort(l.begin(), l.end())`, but the diagnostic is
wherever the subtraction physically appears. (C++20 concepts turn this into an error that names the
requirement — Chapter 33.) The fix is not to make the code compile but to ask for the right thing:
`l.sort()` is a member because a list knows how to sort itself by relinking.

## Invalidation: an iterator is a position, not a value

The last thing to know about iterators is how they die.

```cpp run-san-catch
// An iterator is a position, not a value. Growing a vector past its capacity
// moves the elements, and every iterator into the old storage dies with it.
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> v;
    v.reserve(4);                       // exactly four slots
    for (int i = 0; i < 4; ++i) v.push_back(i);

    auto it = v.begin();                // points into the current storage
    v.push_back(4);                     // fifth element: must reallocate
    std::printf("first = %d\n", *it);   // that storage has been freed
    return 0;
}
```

```text
ERROR: AddressSanitizer: heap-use-after-free
```

`reserve(4)` allocates exactly four slots. Four `push_back` calls fill them, `v.begin()` points at
the first, and the fifth `push_back` has to allocate a bigger block, move the elements, and free the
old one. The iterator still holds the old address — and reading through it is a use-after-free that
ASan names on the spot.

This is why every standard container documents which operations invalidate iterators. For
`std::vector`: anything that reallocates (`push_back` past capacity, `reserve`, `insert`,
`resize`) invalidates *all* of them; `erase` invalidates the erased position and everything after
it. For `std::list` and `std::map`, insertion never invalidates and only erasing the element you are
holding does. The rule is not "iterators stay valid" — it is "check which operations you used".

:::scenario A loop that skips an element and then crashes
You are removing every even number from a `std::vector<int>` and the loop looks right:

```cpp
for (auto it = v.begin(); it != v.end(); ++it) {
    if (*it % 2 == 0) v.erase(it);
}
```

It compiles, it skips elements it should have removed, and on some inputs it crashes. Two separate
facts from this chapter are in play. Which, and what is the fix?
:::

:::solution
**`erase` invalidates the iterator you passed**, so `++it` on the next iteration advances an iterator
that no longer refers into the vector — undefined behaviour, which is why the crash is intermittent
and input-dependent. And because `erase` shifts everything after the erased element down by one, the
iterator's new position is *already* the next element, so `++it` additionally skips it. That is the
"skips elements" half, and it would happen even if invalidation were harmless.

`erase` returns an iterator to the element after the one removed, which is precisely the value the
loop needs next — so use it, and do not increment in the advancing case:

```cpp
for (auto it = v.begin(); it != v.end(); ) {
    if (*it % 2 == 0) it = v.erase(it);   // erase hands back the next position
    else              ++it;
}
```

Better still, let the library do it. `std::erase_if(v, pred)` (C++20) or the erase-remove idiom
before that exists because this loop is easy to get wrong:

```cpp
v.erase(std::remove_if(v.begin(), v.end(),
                       [](int n) { return n % 2 == 0; }),
        v.end());
```

`remove_if` does not erase; it partitions, moving the survivors forward and returning the new
logical end. `erase` then truncates in one call. No iterator is used after an operation that
invalidates it, which is the actual lesson.
:::

## Key takeaways

- Overload an operator to make a type readable, not to make code shorter — the payoff is that the reader already knows the precedence and the rough meaning.
- You cannot add operator symbols, change arity or precedence, or redefine operators for two built-in types. `=`, `[]`, `()` and `->` must be members.
- Make an operator a member when it modifies the left operand or must be one; otherwise make it a non-member, so both operands may be converted.
- A member `operator*` makes `v * 2` work and `2 * v` fail. Symmetric operations need a non-member (usually a hidden friend), and `operator<<` always does, because the stream is on the left.
- Implement `+=` once, then write `+` as a copy plus `+=`. `+=` returns `Counter &`; `+` returns by value — which is why `(a + 3) += 5` compiles, runs, and does nothing.
- In C++17 `==` does not give you `!=`. Define `==` and `<`, then derive the other four so they cannot disagree.
- Overloaded `&&` and `||` lose short-circuit evaluation, because a function call evaluates all of its arguments. Never overload them.
- An iterator is the answer to "what is the next element", not "where is the memory". A range is anything with `begin`/`end` whose iterator has `!=`, `++` and `*`.
- The five `iterator_traits` typedefs are what let algorithms you did not write work on a container you did. Omit them and `std::find` stops compiling.
- Categories are enforced, not documented: `std::sort` needs random access, and a list iterator fails inside `<algorithm>` rather than at your call site.
- Iterators are positions, and positions die. `push_back` past capacity, `erase`, `insert` and `resize` invalidate them; `erase` returns the next valid one.

## Practice

- [ ] 1. `Vec2` above has `+` and `*` but no `-` or unary `-`. Add `operator-` (binary) and `operator-()` (unary negation, no parameters as a member) as non-members, and check that `a - b * 2.0` parses as `a - (b * 2.0)`.
- [ ] 2. Write `operator+=` for `Vec2` and then rewrite `operator+` in terms of it, exactly as `Counter` does. Print the result of `(a += b) += b` to confirm `+=` still returns a reference.
- [ ] 3. Give the ring buffer a `const_iterator` so that a `const Ring<int, 3> &` can be walked with a range-for. (What has to change in `begin`/`end`, and what does `operator*` return?)
- [ ] 4. `std::find` needs `operator==` on the elements, not on the iterators — but `std::find_if` takes a predicate. Use `std::find_if` on the `Ring` to locate the first element greater than 3, and report its logical index.
- [ ] 5. The invalidation block dereferences `v.begin()` after a reallocating `push_back`. Fix it by capturing the *index* of the element you care about instead of an iterator, and confirm the fixed program runs clean under the sanitizers.

## Solutions

:::solution Exercise 1
Two different operators share a name and are told apart by their parameter count:

```cpp
Vec2 operator-(Vec2 a, Vec2 b) { return Vec2{a.x - b.x, a.y - b.y}; }
Vec2 operator-(Vec2 a)         { return Vec2{-a.x, -a.y}; }
```

Both are non-members, which is what lets `-v` work without a member and keeps `a - b` symmetric.
Precedence you cannot change, and do not need to: `a - b * 2.0` is `a - (b * 2.0)`, because `*` has
always bound tighter than `-`. If you want to *see* that rather than assume it, print
`a - b * 2.0` and `(a - b) * 2.0` and compare — the two lines will differ.
:::

:::solution Exercise 2
```cpp
struct Vec2 {
    double x;
    double y;
    Vec2 &operator+=(const Vec2 &o) { x += o.x; y += o.y; return *this; }
};

Vec2 operator+(Vec2 a, const Vec2 &b) { a += b; return a; }
```

`+=` is a member because it modifies the left operand; `+` is a non-member that takes `a` **by
value** — that copy *is* the result — applies `+=` to it and returns it. `(a += b) += b` adds `b`
twice to `a`: each call returns `Vec2 &` to the same object, so the second call operates on the
already-updated `a`. If `+=` returned `Vec2` by value instead, the second `+=` would modify a
temporary and the result would be wrong in exactly the silent way the `chain.cpp` block is.
:::

:::solution Exercise 3
Add a second class that stores `const Ring *` and returns `const T &`:

```cpp
class const_iterator {
    const Ring *owner;
    std::size_t index;
public:
    using iterator_category = std::forward_iterator_tag;
    using value_type        = T;
    using difference_type   = std::ptrdiff_t;
    using pointer           = const T *;
    using reference         = const T &;

    const_iterator(const Ring *o, std::size_t i) : owner(o), index(i) {}
    reference operator*() const {
        std::size_t start = (owner->head + N - owner->count) % N;
        return owner->buf[(start + index) % N];
    }
    const_iterator &operator++() { ++index; return *this; }
    const_iterator  operator++(int) { const_iterator t = *this; ++index; return t; }
    bool operator==(const const_iterator &o) const {
        return owner == o.owner && index == o.index;
    }
    bool operator!=(const const_iterator &o) const { return !(*this == o); }
};

const_iterator begin() const { return const_iterator(this, 0); }
const_iterator end()   const { return const_iterator(this, count); }
```

Three details: `owner` is `const Ring *`, so `operator*` must be const and must return
`const T &`; `begin`/`end` get **const overloads**, which is what the `const Ring &` uses; and
`pointer` changes to `const T *` so the traits stay honest. The duplicated arithmetic is the real
cost here — in production code you would template the iterator on its constness instead of writing
it twice.
:::

:::solution Exercise 4
```cpp
auto it = std::find_if(r.begin(), r.end(), [](int x) { return x > 3; });
if (it != r.end()) {
    std::printf("first > 3 is %d at index %ld\n", *it,
                std::distance(r.begin(), it));
} else {
    std::printf("none\n");
}
```

`std::distance` walks the range with `++` and counts, so it works on a forward iterator like the
ring's — it does not need subtraction, which a forward iterator does not have. On a random access
iterator the same call is O(1) because `distance` detects the category and subtracts; on the ring it
is O(n). Same call, different cost, decided entirely by `iterator_category`.
:::

:::solution Exercise 5
The bug is holding a position across an operation that moves the storage. An index survives a
reallocation; an iterator does not:

```cpp
std::vector<int> v;
v.reserve(4);
for (int i = 0; i < 4; ++i) v.push_back(i);

std::size_t first_index = 0;      // a position expressed independently of storage
v.push_back(4);                   // may reallocate
std::printf("first = %d\n", v[first_index]);
```

If you must keep an iterator, then keep it *after* the growth instead of across it — reserve enough
capacity up front (`v.reserve(5)` before any `push_back`) and re-take `v.begin()` after the last
insertion. Both fixes are the same principle: an iterator is a claim about memory, and a claim you
made before a reallocation is a claim about memory you no longer own.
:::
