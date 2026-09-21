---
chapter: 33
part: 4
title: C++20 and C++23
summary: Constrain templates with concepts so errors name the requirement, replace pointer-and-length pairs with std::span, compose algorithms with lazy range pipelines, format with std::format instead of printf's width guesses, get all six comparisons from a defaulted operator<=>, and return either a value or a reason with std::expected.
minutes: 80
tags: [c++20, c++23, concepts, requires, ranges, views, span, format, spaceship, three-way-comparison, expected, designated-initialisers, feature-test-macros]
std: c++23
---

Everything in this book so far has been C++17, which is a deliberate choice: it is the oldest
standard still worth targeting, and it is what most build systems default to. This chapter is the
other side of that decision. C++20 and C++23 did not add syntax for its own sake — each feature here
removes a category of mistake that the earlier chapters worked around by hand.

Six things, in increasing order of how much they change how you write code: concepts, `std::span`,
ranges, `std::format`, `operator<=>`, and `std::expected`.

## The standard is a compiler switch

There is no "installing C++20". The standard is selected with a flag, and a feature from a newer
standard compiled under an older one is simply a syntax error:

```sh run
# The same source under two standards. The standard is a compiler switch, not a
# property of the library -- and a C++20 feature under -std=c++17 is just a
# syntax error.
cat > t.cpp <<'EOF'
#include <concepts>
#include <cstdio>

template <typename T>
requires std::integral<T>
T twice(T n) { return n + n; }

int main() { std::printf("%d\n", twice(21)); }
EOF

echo "--- c++17 ---"
if clang++ -std=c++17 -fsyntax-only t.cpp 2>err.txt; then
    echo "compiled"
else
    echo "rejected:"
    grep -E "^t.cpp.*error" err.txt | head -2
fi

echo "--- c++20 ---"
if clang++ -std=c++20 -Wall -Wextra -Werror -o t t.cpp 2>err.txt; then
    ./t
else
    echo "rejected"
fi
```

```text
--- c++17 ---
rejected:
t.cpp:5:1: error: unknown type name 'requires'
t.cpp:5:15: error: no member named 'integral' in namespace 'std'
--- c++20 ---
42
```

That is the whole mechanism. `-std=c++17` does not know the word `requires` and does not have
`std::integral`; `-std=c++20` compiles the same source and it runs.

Which means the practical question is *what does this particular compiler and standard library
support*, and the answer is a **feature-test macro**, not a version number:

```sh run
# Feature-test macros: the honest way to ask "does this compiler have it?"
# instead of guessing from the version number. Language features are
# __cpp_<name>; library features are __cpp_lib_<name>.
cat > t.cpp <<'EOF'
#include <cstdio>
#include <version>

#define REPORT(x) std::printf("%-22s %ld\n", #x, (long)(x))

int main() {
    REPORT(__cplusplus);
    REPORT(__cpp_concepts);
    REPORT(__cpp_lib_ranges);
    REPORT(__cpp_lib_span);
    REPORT(__cpp_lib_format);
    REPORT(__cpp_lib_expected);
    return 0;
}
EOF
clang++ -std=c++23 -Wall -Wextra -Werror -o t t.cpp && ./t
```

```text
__cplusplus            202302
__cpp_concepts         202002
__cpp_lib_ranges       202406
__cpp_lib_span         202002
__cpp_lib_format       202110
__cpp_lib_expected     202211
```

The values are dates in `YYYYMM` form, so bigger is newer, and you can test them with `#if
__cpp_lib_expected >= 202211L`. Language features are spelled `__cpp_<name>`; library features are
`__cpp_lib_<name>`. `<version>` defines all of them in one header.

## Concepts: name the requirement

Chapter 31's `sortrange.cpp` failed *inside `<algorithm>`*, at a `__last - __first` the reader never
wrote. That is the C++17 experience of a violated template requirement: the error is real, and it is
in the wrong place. A concept fixes the report, not just the check.

```cpp run
// A concept is a named requirement, checked at the call site and reported as
// such. Two concepts, one that composes them, and a static_assert.
#include <concepts>
#include <cstdio>

template <typename T>
concept Number = std::integral<T> || std::floating_point<T>;

template <typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

template <typename T>
concept Arithmetic = Number<T> && Addable<T>;

template <Arithmetic T>
T twice(T n) { return n + n; }

static_assert(Arithmetic<int>);
static_assert(Arithmetic<double>);
static_assert(!Arithmetic<const char *>);

int main() {
    std::printf("%d\n", twice(21));
    std::printf("%.1f\n", twice(1.5));
    return 0;
}
```

```text
42
3.0
```

Three ideas in one block. `Number` is a **concept**: a named boolean predicate over types.
`Addable` uses a **`requires` expression** — `{ a + b } -> std::convertible_to<T>` means "the
expression `a + b` must be valid and its result must convert to `T`", which is a requirement you
could not previously write down at all. And `Arithmetic` composes the two with `&&`.

`static_assert(Arithmetic<int>)` turns the requirement into something you can test, which is the
underrated half of the feature: a concept is checkable documentation, not just a constraint.

And when one is not met:

```cpp bad
// The payoff of a concept: the error names the requirement that was not met,
// instead of pointing into the body of the template.
#include <concepts>

template <std::integral T>
T twice(T n) { return n + n; }

int main() { return twice(1.5); }
```

```text
error: no matching function for call to 'twice'
```

The compiler prints three lines under that first one, and they are the right three: which call
failed, which candidate was ignored —

```text
note: candidate template ignored: constraints not satisfied [with T = double]
```

— and then the line C++17 could not produce, naming the requirement itself:

```text
note: because 'double' does not satisfy 'integral'
```

Compare that with the `<algorithm>` error from Chapter 31 and the argument for concepts is settled on
the diagnostic alone. (Only the first line is in the verified fence above, because clang interleaves
echoes of the source between the `note:` lines and a comparison has to be contiguous; the two quoted
here were captured from the same run.)

### Constrained overloads

Because a concept is a predicate, it can select a function:

```cpp run
// Constrained overloads: the concept selects the function, which is the clean
// way to write "this version for integers, that one for everything else".
#include <concepts>
#include <cstdio>
#include <string>

void describe(std::integral auto n) { std::printf("integer %lld\n", (long long)n); }
void describe(std::floating_point auto x) { std::printf("float %.2f\n", (double)x); }
void describe(const std::string &s) { std::printf("string %s\n", s.c_str()); }

int main() {
    describe(42);
    describe(2.5);
    describe(std::string("hi"));
    return 0;
}
```

```text
integer 42
float 2.50
string hi
```

`describe(std::integral auto n)` is shorthand for a template constrained by that concept. The
integer, the floating-point value and the string each reach the right function, and an overload set
that used to need `std::enable_if` and a good deal of squinting now reads as what it means.

## `std::span`: a pointer and a length, with an interface

Every C API you have met takes `const T *data, size_t n` — two parameters that must agree, and
neither of which says what it points at. `std::span` is that pair, as one value, with `size()`,
`begin()`, `end()`, `front()`, `subspan()`, and `operator[]`:

```cpp run
// std::span is a (pointer, length) pair with an interface. It owns nothing --
// which is the point: a function that only reads can take a span and stop
// caring whether the caller used a vector, an array or a malloc'd block.
#include <algorithm>
#include <array>
#include <cstdio>
#include <numeric>
#include <span>
#include <vector>

int sum(std::span<const int> s) {
    return std::accumulate(s.begin(), s.end(), 0);
}

int main() {
    std::vector<int> v{1, 2, 3, 4, 5};
    std::array<int, 3> a{10, 20, 30};

    std::printf("vector: %d\n", sum(v));
    std::printf("array:  %d\n", sum(a));

    std::span<int> s{v};
    std::printf("first=%d last=%d size=%zu\n", s.front(), s.back(), s.size());

    std::span<int> middle = s.subspan(1, 3);        // elements 1,2,3
    std::printf("middle: %d\n", sum(middle));

    std::fill(s.begin(), s.end(), 0);               // writes through the span
    std::printf("after fill: %d\n", sum(v));        // v itself changed
    return 0;
}
```

```text
vector: 15
array:  60
first=1 last=5 size=5
middle: 9
after fill: 0
```

The important line is `sum(v)` and `sum(a)` — a `std::vector` and a `std::array` both convert to
`std::span<const int>` implicitly, so one function serves both. Note the `const` in
`std::span<const int>`: that is what makes it read-only, and it is why `std::fill` later in the block
works on `std::span<int>` but would be rejected on the const version.

A span **owns nothing**. That is its purpose and its danger:

```cpp warn
// A span owns nothing, so it dangles exactly as a pointer would. This one
// refers to a vector that dies when the function returns -- and here the
// compiler can see it, which is the good case.
#include <cstdio>
#include <span>
#include <vector>

std::span<int> dangling() {
    std::vector<int> v{1, 2, 3};
    return std::span<int>(v);          // v's storage dies here
}

int main() {
    std::span<int> s = dangling();
    std::printf("first=%d\n", s[0]);   // reads storage that no longer exists
    return 0;
}
```

```text
warning: address of stack memory associated with local variable 'v' returned [-Wreturn-stack-address]
```

This one the compiler can see — returning a span onto a local's storage is diagnosed at compile time,
and with `-Werror` it does not build. Do not generalise that into a safety guarantee: a span stored
in a member, or returned through two layers of indirection, dangles exactly as a raw pointer would.
The mental model to keep is that a span is a *borrowed view*, and the borrow must not outlive the
storage.

## Ranges: composition instead of temporaries

Chapter 29's algorithms take iterator pairs. Ranges let you compose them instead:

```cpp run
// A range pipeline reads left to right and composes, instead of nesting
// temporary containers. Nothing is copied and nothing is materialised.
#include <algorithm>
#include <cstdio>
#include <numeric>
#include <ranges>
#include <string>
#include <vector>

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    auto evens_doubled = v
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * 10; });

    std::printf("evens doubled:");
    for (int x : evens_doubled) std::printf(" %d", x);
    std::printf("\n");

    std::printf("first three:");
    for (int x : evens_doubled | std::views::take(3)) std::printf(" %d", x);
    std::printf("\n");

    // std::ranges:: algorithms take the range directly -- no begin/end pair.
    std::printf("sum=%d\n", std::ranges::fold_left(v, 0, std::plus<int>{}));
    std::printf("any > 9: %s\n", std::ranges::any_of(v, [](int n) { return n > 9; })
                                 ? "yes" : "no");

    // Projection: sort by a member instead of writing a comparator.
    std::vector<std::string> words{"pear", "fig", "apple"};
    std::ranges::sort(words, {}, [](const std::string &s) { return s.size(); });
    std::printf("by length:");
    for (const auto &w : words) std::printf(" %s", w.c_str());
    std::printf("\n");
    return 0;
}
```

```text
evens doubled: 20 40 60 80 100
first three: 20 40 60
sum=55
any > 9: yes
by length: fig pear apple
```

Three separate things are happening. `v | views::filter(...) | views::transform(...)` composes
left to right, which is the order you think in, instead of nesting. `std::ranges::fold_left(v, 0,
std::plus<int>{})` takes the range itself, so no `begin()`/`end()` pair. And
`std::ranges::sort(words, {}, by_length)` takes a **projection** as its third argument — sort by
`size()` without writing a comparator lambda that compares two things.

Nothing was copied. `evens_doubled` is a view, not a container: it holds a reference to `v` and two
callables.

### Laziness, measured

A view does no work when you build it, and pulls one element at a time when you iterate:

```cpp run
// Views are lazy: building the pipeline does no work, and each element is
// pulled through the whole chain one at a time. A counting predicate proves it.
#include <cstdio>
#include <ranges>
#include <vector>

int main() {
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int filter_calls = 0;
    int transform_calls = 0;

    auto pipeline = v
        | std::views::filter([&](int n) { ++filter_calls; return n % 3 == 0; })
        | std::views::transform([&](int n) { ++transform_calls; return n * 100; });

    std::printf("after building: filter=%d transform=%d\n",
                filter_calls, transform_calls);

    auto first_two = pipeline | std::views::take(2);
    std::printf("result:");
    for (int x : first_two) std::printf(" %d", x);
    std::printf("\n");

    std::printf("after two elements: filter=%d transform=%d\n",
                filter_calls, transform_calls);
    return 0;
}
```

```text
after building: filter=0 transform=0
result: 300 600
after two elements: filter=9 transform=2
```

Read the first line: building the pipeline called **nothing**. Then the loop ran, and the filter was
consulted more times than there were results — it has to look at an element to decide — while the
transform only ran on the three survivors. How far a `take` looks ahead is an implementation detail;
what is guaranteed, and what the block demonstrates, is that no work happens at construction and no
work happens on elements you never consume.

## `std::format`: the type comes from the argument

`printf` asks you to repeat the type in the format string, and gets worse answers than silence when
you get it wrong — `%d` for a `long long` on the wrong platform is undefined behaviour, and no
compiler in this chapter's toolchain will mention it.

```cpp run
// std::format: the type is taken from the argument, not declared in the format
// string -- so there is no %lld to get wrong, and a literal format string is
// checked at compile time.
#include <cstdio>
#include <format>
#include <string>

int main() {
    std::string s = std::format("{} + {} = {}", 1, 2, 3);
    std::printf("%s\n", s.c_str());

    std::printf("%s", std::format("padded |{:>8}| left |{:<8}|\n", "ab", "cd").c_str());
    std::printf("%s", std::format("hex {:#x}  binary {:#b}\n", 255, 5).c_str());
    std::printf("%s", std::format("pi {:.3f}  sci {:.2e}\n", 3.14159, 12345.678).c_str());

    long long big = 9'000'000'000LL;
    std::printf("%s", std::format("no width guesswork: {}\n", big).c_str());
    std::printf("%s", std::format("indexed: {1} before {0}\n", "zero", "one").c_str());
    return 0;
}
```

```text
1 + 2 = 3
padded |      ab| left |cd      |
hex 0xff  binary 0b101
pi 3.142  sci 1.23e+04
no width guesswork: 9000000000
indexed: one before zero
```

No width letters to memorise, no `%lld` to guess, and the format string is a *literal*, so the
library checks it at compile time (the block below shows what that looks like). Indexed arguments
(`{1}` before `{0}`) are the thing `printf` cannot do at all.

```cpp bad
// The format string is checked at compile time when it is a literal, so a
// mismatch is a compile error rather than garbage at run time.
#include <format>

int main() {
    auto s = std::format("{:d}\n", 3.5);   // :d is for integers
    return static_cast<int>(s.size());
}
```

```text
error: call to consteval function 'std::basic_format_string<char, double>::basic_format_string<char[6]>' is not a constant expression
```

The error is a mouthful — it is a `consteval` failure, because the format string is parsed during
compilation — but it is a *compile* error. Compare with `printf("%d", 3.5)`, which compiles, runs,
and prints something meaningless.

:::pitfall std::format needs a literal format string
The compile-time checking only happens because the format string is a compile-time constant. Pass a
`std::string` built at run time and `std::format` throws `std::format_error` instead — you have moved
the failure from compile time to run time. Use `std::vformat` when the format string genuinely is
dynamic, and accept that you are back to a run-time check.
:::

## `operator<=>`: six comparisons from one line

Chapter 31 had you write `==` and `<` and then derive four more by hand, so that they could not
disagree. C++20 makes that the compiler's job:

```cpp run
// Defaulting operator<=> asks the compiler to generate all six comparisons
// from one declaration. Ordering becomes a one-liner instead of six functions
// that can disagree with each other (Chapter 31 wrote them by hand).
#include <compare>
#include <cstdio>
#include <string>
#include <vector>
#include <algorithm>

struct Version {
    int major;
    int minor;
    auto operator<=>(const Version &) const = default;
    bool operator==(const Version &) const = default;
};

int main() {
    Version a{1, 2};
    Version b{1, 3};
    Version c{1, 2};

    std::printf("a < b : %d\n", (int)(a < b));
    std::printf("a == c: %d\n", (int)(a == c));
    std::printf("a >= b: %d\n", (int)(a >= b));

    auto order = a <=> b;
    std::printf("a<=>b is less: %d\n", (int)(order == std::strong_ordering::less));

    std::vector<Version> vs{{2, 0}, {1, 5}, {1, 2}};
    std::sort(vs.begin(), vs.end());
    std::printf("sorted:");
    for (const auto &v : vs) std::printf(" %d.%d", v.major, v.minor);
    std::printf("\n");
    return 0;
}
```

```text
a < b : 1
a == c: 1
a >= b: 0
a<=>b is less: 1
sorted: 1.2 1.5 2.0
```

Two defaulted declarations replace six hand-written functions. `operator<=>` produces the ordering
(`<`, `>`, `<=`, `>=`) and `operator==` produces equality — you need both defaulted, because ordering
does not give you `==` (comparing for order can be cheaper than comparing for equality, so the
language refuses to assume). And because `Version` is now ordered, `std::sort` works on it with no
comparator at all.

The return type of `a <=> b` is a comparison category — `std::strong_ordering`,
`std::weak_ordering` or `std::partial_ordering` — and that category is a statement about your type:
`strong_ordering` means equal values are interchangeable, `partial_ordering` admits "neither less,
nor greater, nor equal" (floating-point `NaN` is the canonical case). Defaulting gives you
`strong_ordering` for a struct of comparable members, which is nearly always what you want.

## `std::expected`: a value, or a reason

Chapter 30 weighed exceptions against error codes. `std::expected<T, E>` is the third option that
became standard in C++23: it is a return value, so no unwinding and no `try` block, but the value and
the reason are in one object and the type system remembers both.

```cpp run
// std::expected<T, E>: either a value or a reason. Unlike an exception it is a
// return value, and unlike an error code the value and the reason are in one
// object and cannot be silently ignored.
#include <cstdio>
#include <expected>
#include <string>
#include <string_view>

std::expected<int, std::string> parse_positive(std::string_view text) {
    if (text.empty()) return std::unexpected("empty input");
    int n = 0;
    for (char c : text) {
        if (c < '0' || c > '9') return std::unexpected("not a number");
        n = n * 10 + (c - '0');
    }
    if (n == 0) return std::unexpected("must be positive");
    return n;
}

int main() {
    for (std::string_view in : {"42", "abc", "", "0", "7"}) {
        std::expected<int, std::string> r = parse_positive(in);
        if (r) std::printf("%s -> %d\n", std::string(in).c_str(), *r);
        else   std::printf("%s -> error: %s\n", std::string(in).c_str(), r.error().c_str());
    }

    int doubled = parse_positive("21").value_or(0) * 2;
    std::printf("value_or fallback: %d\n", doubled);

    auto chained = parse_positive("10").and_then([](int n) -> std::expected<int, std::string> {
        return n * 3;
    });
    std::printf("and_then: %d\n", chained.value_or(-1));
    return 0;
}
```

```text
42 -> 42
abc -> error: not a number
 -> error: empty input
0 -> error: must be positive
7 -> 7
value_or fallback: 42
and_then: 30
```

`if (r)` is the check; `*r` is the value; `r.error()` is the reason. `value_or(0)` supplies a
fallback, and `and_then` chains a computation that only runs on success — so error handling reads as
a sequence rather than as nested `if`s.

The access is checked, not fast:

```cpp run-abort
// Reading .value() on an expected that holds an error is a checked operation:
// it throws, rather than handing back an uninitialised T.
#include <cstdio>
#include <expected>

std::expected<int, const char *> fails() { return std::unexpected("no value"); }

int main() {
    std::expected<int, const char *> r = fails();
    std::printf("%d\n", r.value());
    return 0;
}
```

```text
bad access to std::expected
```

`r.value()` on an `expected` that holds an error throws `std::bad_expected_access<E>`, and the
unhandled exception ends the program. That is the deliberate contrast with a raw error code: reading
the value without checking is not silent.

Use `expected` when a failure is an *expected outcome the caller will handle* — parsing, validation,
a lookup that may miss — and exceptions when the failure has to travel up past frames that cannot
help. The test is the same one Chapter 30 ended on: can the immediate caller do something useful
with this?

## Designated initialisers

Small, and worth the two lines it costs:

```cpp run
// Designated initialisers: name the fields at the call site. The declaration
// order is enforced, so you cannot accidentally swap two members of the same
// type -- which is the bug this feature exists to prevent.
#include <cstdio>

struct Config {
    const char *host;
    int port;
    bool tls;
    int timeout_ms;
};

int main() {
    Config c{.host = "example.com", .port = 443, .tls = true, .timeout_ms = 5000};
    std::printf("%s:%d tls=%d timeout=%d\n",
                c.host, c.port, (int)c.tls, c.timeout_ms);

    Config d{.host = "localhost", .port = 8080};   // the rest are zero
    std::printf("%s:%d tls=%d timeout=%d\n",
                d.host, d.port, (int)d.tls, d.timeout_ms);
    return 0;
}
```

```text
example.com:443 tls=1 timeout=5000
localhost:8080 tls=0 timeout=0
```

`Config{.host = ..., .port = ...}` names each field at the call site. Members you omit are
zero-initialised, and the declaration order is enforced — so `.port = 443, .host = "x"` is rejected,
which is exactly the bug this prevents when two members share a type.

:::scenario A template that fails in the wrong place
You have a C++17 function that formats any container's contents:

```cpp
template <typename Container>
std::string join(const Container &c) {
    std::string out;
    for (const auto &x : c) out += std::format("{}, ", x);
    return out;
}
```

Called with `join(std::list<int>{1, 2, 3})` it works. Called with `join(42)` it produces forty lines
of error pointing into `basic_format_string`, `formatter`, and the internals of `std::string`. The
function is three lines. Rewrite it so the error is one line, and say which two C++20 features you
used.
:::

:::solution
Constrain the parameter with a concept, and decide what "container" means precisely enough to write
down. The requirement you actually need is "iterable", which `std::ranges::range` expresses directly:

```cpp
template <std::ranges::range R>
std::string join(const R &r) {
    std::string out;
    for (const auto &x : r) out += std::format("{}, ", x);
    return out;
}
```

`join(42)` now produces `error: no matching function for call to 'join'` followed by
`note: because 'int' does not satisfy 'range'` — the call site, the candidate, and the requirement.

The two features are **concepts** (a named requirement, reported by name) and **ranges** (the
`std::ranges::range` concept itself, which did not exist in C++17). If you need the elements to be
formattable too, compose them:

```cpp
template <typename R>
requires std::ranges::range<R> && requires(std::ranges::range_value_t<R> v) {
    { std::format("{}", v) };
}
std::string join(const R &r);
```

That is C++17's problem solved properly: the requirement is written down, checked where the mistake
is, and named in the diagnostic.
:::

## Key takeaways

- The standard is a compiler switch. `-std=c++20` is all that "using C++20" means, and a newer feature under an older standard is a syntax error.
- Ask what a toolchain supports with feature-test macros (`__cpp_concepts`, `__cpp_lib_ranges`, …) from `<version>`, not by guessing from the compiler version. Language features are `__cpp_x`; library features are `__cpp_lib_x`.
- A concept is a named requirement over types, composed with `&&`/`||` and testable with `static_assert`. `requires` expressions state what must compile, not just what a type is.
- The payoff is the diagnostic: `note: because 'double' does not satisfy 'integral'` instead of an error forty lines inside `<algorithm>`.
- `std::span<T>` is a borrowed (pointer, length) pair: `sum(v)` and `sum(a)` both work, and `std::span<const T>` is the read-only form. It owns nothing, so it dangles — returning one over a local is caught at compile time, but that is not a general guarantee.
- Range pipelines compose left to right, take the range itself instead of an iterator pair, and accept projections instead of comparators.
- Views are lazy: zero work at construction, one element at a time during iteration, and nothing computed for elements you never reach.
- `std::format` takes the type from the argument, so there is no `%lld` to get wrong — and a literal format string is checked at compile time. A run-time format string throws instead.
- Defaulting `operator<=>` and `operator==` replaces the six hand-written comparisons, and makes the type sortable with no comparator. You need both defaulted: ordering does not imply equality.
- `std::expected<T, E>` is a value or a reason, in one object, with no unwinding. `value_or` and `and_then` chain it; `.value()` on an error throws rather than returning something uninitialised.
- Designated initialisers name fields at the call site and enforce declaration order, which is the guard against swapping two members of the same type.

## Practice

- [ ] 1. Write a concept `Printable` that is satisfied when `std::format("{}", v)` compiles for a value of the type, then constrain a `void show(const T&)` with it. Check that `show(42)` works and that a type with no formatter produces a one-line constraint error.
- [ ] 2. Take the `Ring` iterator from Chapter 31 and make the ring satisfy `std::ranges::range`. What is the minimum you must add, and which concept then accepts it?
- [ ] 3. Replace a `(const int *data, std::size_t n)` function signature with `std::span<const int>` and call it from a `std::vector`, a `std::array` and a C array. Confirm all three call sites compile unchanged in behaviour.
- [ ] 4. Chain three operations with `std::expected`: parse a string to an `int`, reject non-positive values, then double the result. Use `and_then` for the doubling and `or_else` (or a manual check) to report the reason. Show the reason for each of `"abc"`, `"0"` and `"-5"`.
- [ ] 5. Prove the laziness claim differently: build a pipeline over a ten-element vector and iterate only `views::take(1)`. Print how many times the filter ran, and explain why the count is what it is rather than ten.

## Solutions

:::solution Exercise 1
```cpp
template <typename T>
concept Printable = requires(T v) {
    { std::format("{}", v) };
};

template <Printable T>
void show(const T &v) { std::printf("%s\n", std::format("{}", v).c_str()); }
```

The `requires` expression asks one question: does that expression compile? There is no need to name a
result type here, because `std::format` already returns `std::string` for every formattable type.
`show(42)` prints `42`. For a type with no formatter — a plain `struct Point { int x; int y; };` — the
error is `no matching function for call to 'show'` followed by `note: because 'Point' does not
satisfy 'Printable'`, which is the whole point: the reader is told the requirement, not taken into
`__format`'s internals. (To make `Point` formattable you write a `std::formatter<Point>`
specialisation — the library's extension point for user types.)
:::

:::solution Exercise 2
`std::ranges::range` requires `begin(t)` and `end(t)` to be valid on the value — which the ring
already provides as members, and member `begin`/`end` satisfy the concept. The minimum is therefore
**nothing at all**: `static_assert(std::ranges::range<Ring<int, 3>>)` already passes once you have
the member functions from Chapter 31.

What the ring does *not* satisfy is anything stronger. `std::ranges::sized_range` also passes, because
`size()` exists. `std::ranges::random_access_range` does not, and neither does
`bidirectional_range` — the iterator only has `++`, and the concept checks for `--` and for `+ n`.

That is the honest answer, and it is the useful one: a concept is not a badge you apply, it is a
question the library asks your type and gets a truthful answer to. `std::ranges::sort` will still
refuse a ring, and now it will say why by name.
:::

:::solution Exercise 3
```cpp
int sum(std::span<const int> s) {
    return std::accumulate(s.begin(), s.end(), 0);
}

std::vector<int> v{1, 2, 3};
std::array<int, 3> a{4, 5, 6};
int c_array[3] = {7, 8, 9};

std::printf("%d %d %d\n", sum(v), sum(a), sum(c_array));
```

All three convert to `std::span<const int>` implicitly: the vector and array through their `data()`
and `size()`, and the C array through the `std::span(T (&arr)[N])` constructor, which deduces the
extent. That last one is the quiet improvement — the C array case is where a manual `(ptr, n)` pair
was most often wrong, because `sizeof` on a *parameter* silently gives you the pointer's size (the
`-Wsizeof-array-argument` trap from earlier chapters). With a span, the length is computed by the
library, once, correctly.

One call site where the conversion will *not* happen: a `const std::vector<int>` gives
`std::span<const int>` fine, but a `std::vector<int>` passed to `std::span<int>` while the parameter
is declared `const&` will not bind. Match the constness to the intent — read-only functions take
`std::span<const T>`.
:::

:::solution Exercise 4
```cpp
std::expected<int, std::string> parse(std::string_view t);   // from this chapter
std::expected<int, std::string> positive(int n) {
    if (n <= 0) return std::unexpected("must be positive");
    return n;
}

for (std::string_view in : {"abc", "0", "-5", "21"}) {
    auto r = parse(in)
        .and_then(positive)
        .and_then([](int n) -> std::expected<int, std::string> { return n * 2; });
    if (r) std::printf("%s -> %d\n", std::string(in).c_str(), *r);
    else   std::printf("%s -> %s\n", std::string(in).c_str(), r.error().c_str());
}
```

Output: `abc -> not a number`, `0 -> must be positive`, `-5 -> must be positive`, `21 -> 42`.

The shape is the point: each `and_then` receives the *value* and returns an `expected`, so the chain
stops at the first failure and the reason from that failure is the one that comes out. There is no
sentinel (`-1`), no out-parameter, and no way to read the value without having gone through the
check. Compare it with the same logic as nested `if`s and the saving is not lines — it is that the
error path is impossible to forget, because there is no value to read on it.
:::

:::solution Exercise 5
```cpp
int calls = 0;
auto pipeline = v | std::views::filter([&](int n) { ++calls; return n % 3 == 0; });
std::printf("built: calls=%d\n", calls);
for (int x : pipeline | std::views::take(1)) std::printf("got %d\n", x);
std::printf("after: calls=%d\n", calls);
```

The first line prints `built: calls=0`. The last prints a number that is **not ten** — because the
filter stops being consulted as soon as `take` has enough, and `take(1)` needs one element. The exact
count depends on how far the implementation looks ahead before deciding it has enough, which is why
the claim to make in your own code is the general one: **a view does no work at construction and no
work on elements you do not consume.** If you need a precise guarantee about how many times a
callable runs, a view is the wrong tool — write the loop, where the control flow is yours.
:::
