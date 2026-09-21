#!/usr/bin/env python3
"""Generate chapters/33-cpp20-and-cpp23.md.

Every `text` fence is captured from a real clang++ run and every source block is
read off disk, so nothing in the chapter is retyped. The chapter sets
`std: c++23` in its frontmatter, which the harness honours per chapter.

    python3 tools/gen/33/gen.py
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/33 -> gen -> tools -> cpp
OUT = CHAPTERS / "33-cpp20-and-cpp23.md"

CXX = "clang++"
STD = "c++23"
BASE = ["-std=" + STD, "-Wall", "-Wextra"]
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 90


def build_and_run(name: str, sanitize: bool = False):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror"] + (SAN if sanitize else []) + \
              ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        env = dict(os.environ)
        env["ASAN_OPTIONS"] = "detect_leaks=0"
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td,
                           timeout=TIMEOUT, env=env)
        return r.stdout, r.stderr, r.returncode


def diagnostic(name: str, marker: str):
    """Compile with -Wall -Wextra and NO -Werror. `bad` must fail, `warn` must build."""
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if marker == "error:" and b.returncode == 0:
            raise SystemExit(f"{name} was supposed to be rejected, but it built cleanly")
        if marker == "warning:" and b.returncode != 0:
            raise SystemExit(f"{name} must still build for a `warn` block:\n{b.stderr}")
        return b.stderr


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def msg(blob: str, marker: str, needle: str) -> str:
    """Return `<marker> <message>` for the first diagnostic containing `needle`.

    The raw line carries this machine's absolute path, which must never reach
    the book, so only the part after the marker is published.
    """
    for line in blob.splitlines():
        if needle in line and marker in line:
            return marker + " " + line.split(marker, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{blob}")


CONCEPT_NOTE_1 = "note: candidate template ignored: constraints not satisfied [with T = double]"
CONCEPT_NOTE_2 = "note: because 'double' does not satisfy 'integral'"


def assert_notes(blob: str, lines: list[str]) -> None:
    """Prove the concept-satisfaction notes really are emitted.

    The harness can only compare one contiguous phrase -- clang interleaves the
    source-echo lines between the `note:` lines -- so the first line goes in the
    verified fence and these two are quoted in prose. They are still asserted
    here, so the prose cannot claim a diagnostic that was never produced.
    """
    sq = squash(blob)
    for line in lines:
        if squash(line) not in sq:
            raise SystemExit(f"diagnostic line not actually produced:\n  {line}\nin:\n{blob}")


def shell(name: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(["sh", str(HERE / name)], text=True, capture_output=True,
                           cwd=td, timeout=TIMEOUT)
        if r.returncode != 0:
            raise SystemExit(f"{name} exited {r.returncode}:\n{r.stderr}")
        return r.stdout


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").rstrip("\n")


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# capture
# --------------------------------------------------------------------------
print("capturing evidence ...")

stdcheck_out = shell("stdcheck.sh")
features_out = shell("features.sh")

concept_out, _, _ = build_and_run("concept.cpp")
overload_out, _, _ = build_and_run("overload.cpp")
span_out, _, _ = build_and_run("span.cpp")
ranges_out, _, _ = build_and_run("ranges.cpp")
lazy_out, _, _ = build_and_run("lazy.cpp")
format_out, _, _ = build_and_run("format.cpp")
spaceship_out, _, _ = build_and_run("spaceship.cpp")
expected_out, _, _ = build_and_run("expected.cpp")
designated_out, _, _ = build_and_run("designated.cpp")

_, throw_err, throw_rc = build_and_run("expected_throw.cpp")
if throw_rc == 0:
    raise SystemExit("expected_throw.cpp must die on the bad access")
THROW_NEEDLE = "bad access to std::expected"
if THROW_NEEDLE not in throw_err:
    raise SystemExit(f"expected {THROW_NEEDLE!r} in:\n{throw_err}")

concept_err = diagnostic("concept_violation.cpp", "error:")
assert_notes(concept_err, [CONCEPT_NOTE_1, CONCEPT_NOTE_2])
format_err = diagnostic("format_bad.cpp", "error:")
span_err = diagnostic("span_dangle.cpp", "warning:")

print("all evidence captured")

BLOCKS = {
    "stdcheck":   fence("sh", "run", read("stdcheck.sh"), stdcheck_out),
    "features":   fence("sh", "run", read("features.sh"), features_out),
    "concept":    fence("cpp", "run", read("concept.cpp"), concept_out),
    "violation":  fence("cpp", "bad", read("concept_violation.cpp"),
                        msg(concept_err, "error:", "no matching function")),
    "overload":   fence("cpp", "run", read("overload.cpp"), overload_out),
    "span":       fence("cpp", "run", read("span.cpp"), span_out),
    "span_dangle": fence("cpp", "warn", read("span_dangle.cpp"),
                         msg(span_err, "warning:", "address of stack memory")),
    "ranges":     fence("cpp", "run", read("ranges.cpp"), ranges_out),
    "lazy":       fence("cpp", "run", read("lazy.cpp"), lazy_out),
    "format":     fence("cpp", "run", read("format.cpp"), format_out),
    "format_bad": fence("cpp", "bad", read("format_bad.cpp"),
                        msg(format_err, "error:", "is not a constant expression")),
    "spaceship":  fence("cpp", "run", read("spaceship.cpp"), spaceship_out),
    "expected":   fence("cpp", "run", read("expected.cpp"), expected_out),
    "throw":      fence("cpp", "run-abort", read("expected_throw.cpp"), THROW_NEEDLE),
    "designated": fence("cpp", "run", read("designated.cpp"), designated_out),
}

# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------
DOC = """---
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

@@stdcheck@@
That is the whole mechanism. `-std=c++17` does not know the word `requires` and does not have
`std::integral`; `-std=c++20` compiles the same source and it runs.

Which means the practical question is *what does this particular compiler and standard library
support*, and the answer is a **feature-test macro**, not a version number:

@@features@@
The values are dates in `YYYYMM` form, so bigger is newer, and you can test them with `#if
__cpp_lib_expected >= 202211L`. Language features are spelled `__cpp_<name>`; library features are
`__cpp_lib_<name>`. `<version>` defines all of them in one header.

## Concepts: name the requirement

Chapter 31's `sortrange.cpp` failed *inside `<algorithm>`*, at a `__last - __first` the reader never
wrote. That is the C++17 experience of a violated template requirement: the error is real, and it is
in the wrong place. A concept fixes the report, not just the check.

@@concept@@
Three ideas in one block. `Number` is a **concept**: a named boolean predicate over types.
`Addable` uses a **`requires` expression** — `{ a + b } -> std::convertible_to<T>` means "the
expression `a + b` must be valid and its result must convert to `T`", which is a requirement you
could not previously write down at all. And `Arithmetic` composes the two with `&&`.

`static_assert(Arithmetic<int>)` turns the requirement into something you can test, which is the
underrated half of the feature: a concept is checkable documentation, not just a constraint.

And when one is not met:

@@violation@@
The compiler prints three lines under that first one, and they are the right three: which call
failed, which candidate was ignored —

```text
""" + CONCEPT_NOTE_1 + """
```

— and then the line C++17 could not produce, naming the requirement itself:

```text
""" + CONCEPT_NOTE_2 + """
```

Compare that with the `<algorithm>` error from Chapter 31 and the argument for concepts is settled on
the diagnostic alone. (Only the first line is in the verified fence above, because clang interleaves
echoes of the source between the `note:` lines and a comparison has to be contiguous; the two quoted
here were captured from the same run.)

### Constrained overloads

Because a concept is a predicate, it can select a function:

@@overload@@
`describe(std::integral auto n)` is shorthand for a template constrained by that concept. The
integer, the floating-point value and the string each reach the right function, and an overload set
that used to need `std::enable_if` and a good deal of squinting now reads as what it means.

## `std::span`: a pointer and a length, with an interface

Every C API you have met takes `const T *data, size_t n` — two parameters that must agree, and
neither of which says what it points at. `std::span` is that pair, as one value, with `size()`,
`begin()`, `end()`, `front()`, `subspan()`, and `operator[]`:

@@span@@
The important line is `sum(v)` and `sum(a)` — a `std::vector` and a `std::array` both convert to
`std::span<const int>` implicitly, so one function serves both. Note the `const` in
`std::span<const int>`: that is what makes it read-only, and it is why `std::fill` later in the block
works on `std::span<int>` but would be rejected on the const version.

A span **owns nothing**. That is its purpose and its danger:

@@span_dangle@@
This one the compiler can see — returning a span onto a local's storage is diagnosed at compile time,
and with `-Werror` it does not build. Do not generalise that into a safety guarantee: a span stored
in a member, or returned through two layers of indirection, dangles exactly as a raw pointer would.
The mental model to keep is that a span is a *borrowed view*, and the borrow must not outlive the
storage.

## Ranges: composition instead of temporaries

Chapter 29's algorithms take iterator pairs. Ranges let you compose them instead:

@@ranges@@
Three separate things are happening. `v | views::filter(...) | views::transform(...)` composes
left to right, which is the order you think in, instead of nesting. `std::ranges::fold_left(v, 0,
std::plus<int>{})` takes the range itself, so no `begin()`/`end()` pair. And
`std::ranges::sort(words, {}, by_length)` takes a **projection** as its third argument — sort by
`size()` without writing a comparator lambda that compares two things.

Nothing was copied. `evens_doubled` is a view, not a container: it holds a reference to `v` and two
callables.

### Laziness, measured

A view does no work when you build it, and pulls one element at a time when you iterate:

@@lazy@@
Read the first line: building the pipeline called **nothing**. Then the loop ran, and the filter was
consulted more times than there were results — it has to look at an element to decide — while the
transform only ran on the three survivors. How far a `take` looks ahead is an implementation detail;
what is guaranteed, and what the block demonstrates, is that no work happens at construction and no
work happens on elements you never consume.

## `std::format`: the type comes from the argument

`printf` asks you to repeat the type in the format string, and gets worse answers than silence when
you get it wrong — `%d` for a `long long` on the wrong platform is undefined behaviour, and no
compiler in this chapter's toolchain will mention it.

@@format@@
No width letters to memorise, no `%lld` to guess, and the format string is a *literal*, so the
library checks it at compile time (the block below shows what that looks like). Indexed arguments
(`{1}` before `{0}`) are the thing `printf` cannot do at all.

@@format_bad@@
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

@@spaceship@@
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

@@expected@@
`if (r)` is the check; `*r` is the value; `r.error()` is the reason. `value_or(0)` supplies a
fallback, and `and_then` chains a computation that only runs on success — so error handling reads as
a sequence rather than as nested `if`s.

The access is checked, not fast:

@@throw@@
`r.value()` on an `expected` that holds an error throws `std::bad_expected_access<E>`, and the
unhandled exception ends the program. That is the deliberate contrast with a raw error code: reading
the value without checking is not silent.

Use `expected` when a failure is an *expected outcome the caller will handle* — parsing, validation,
a lookup that may miss — and exceptions when the failure has to travel up past frames that cannot
help. The test is the same one Chapter 30 ended on: can the immediate caller do something useful
with this?

## Designated initialisers

Small, and worth the two lines it costs:

@@designated@@
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
void show(const T &v) { std::printf("%s\\n", std::format("{}", v).c_str()); }
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

std::printf("%d %d %d\\n", sum(v), sum(a), sum(c_array));
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
    if (r) std::printf("%s -> %d\\n", std::string(in).c_str(), *r);
    else   std::printf("%s -> %s\\n", std::string(in).c_str(), r.error().c_str());
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
std::printf("built: calls=%d\\n", calls);
for (int x : pipeline | std::views::take(1)) std::printf("got %d\\n", x);
std::printf("after: calls=%d\\n", calls);
```

The first line prints `built: calls=0`. The last prints a number that is **not ten** — because the
filter stops being consulted as soon as `take` has enough, and `take(1)` needs one element. The exact
count depends on how far the implementation looks ahead before deciding it has enough, which is why
the claim to make in your own code is the general one: **a view does no work at construction and no
work on elements you do not consume.** If you need a precise guarantee about how many times a
callable runs, a view is the wrong tool — write the loop, where the control flow is yours.
:::
"""

for key, block in BLOCKS.items():
    marker = "@@" + key + "@@"
    if marker not in DOC:
        raise SystemExit(f"marker {marker} is not used in the chapter")
    DOC = DOC.replace(marker, block)

OUT.write_text(DOC.lstrip("\n"), encoding="utf-8")
print(f"wrote {OUT.relative_to(CHAPTERS.parent.parent)}  "
      f"({len(DOC.split())} words, {DOC.count(chr(10)) + 1} lines)")
