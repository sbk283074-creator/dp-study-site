#!/usr/bin/env python3
"""Generate chapters/31-operator-overloading-and-iterators.md.

Every `text` fence in this chapter is captured from a real clang++ run, and
every source block is read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/31/gen.py

STYLE.md: "The `bad` directive exists to keep that honest."
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/31 -> gen -> tools -> cpp
OUT = CHAPTERS / "31-operator-overloading-and-iterators.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
SAN = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 60


def build_and_run(name: str, sanitize: bool = False):
    """Build with -Werror and run. Returns (stdout, stderr, returncode)."""
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


def diagnostic(name: str):
    """Compile with -Wall -Wextra and NO -Werror. Returns (rc, stderr)."""
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode == 0:
            raise SystemExit(f"{name} was supposed to be rejected, but it built cleanly")
        return b.returncode, b.stderr


def err_msg(blob: str, needle: str) -> str:
    """Return `error: <message>` for the first diagnostic containing `needle`.

    The raw line carries this machine's absolute path, which must never reach
    the book, so only the part after `error:` is published.
    """
    for line in blob.splitlines():
        if needle in line and "error:" in line:
            return "error: " + line.split("error:", 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{blob}")


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").rstrip("\n")


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    """A fence plus, for `bad`/`warn`/`run`, the `text` fence it is checked against.

    The `{{`/`}}` in the DOC below are C++ braces; this function returns the
    literal text, so nothing here needs escaping.
    """
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# capture the evidence
# --------------------------------------------------------------------------
print("capturing evidence ...")

noops_out, _, _ = build_and_run("noops.cpp")
vec2_out, _, _ = build_and_run("vec2.cpp")
stream_out, _, _ = build_and_run("stream.cpp")
compound_out, _, _ = build_and_run("compound.cpp")
chain_out, _, _ = build_and_run("chain.cpp")
subscript_out, _, _ = build_and_run("subscript.cpp")
functor_out, _, _ = build_and_run("functor.cpp")
arrow_out, _, _ = build_and_run("arrow.cpp")
shortcircuit_out, _, _ = build_and_run("shortcircuit.cpp")
fixedvec_out, _, _ = build_and_run("fixedvec.cpp")
ring_out, _, _ = build_and_run("ring.cpp")
traits_out, _, _ = build_and_run("traits.cpp")

_, member_err = diagnostic("member_only.cpp")
_, arity_err = diagnostic("arity.cpp")
_, assign_err = diagnostic("assign_nm.cpp")
_, stream_member_err = diagnostic("stream_member.cpp")
_, eqonly_err = diagnostic("eqonly.cpp")
_, sort_err = diagnostic("sortrange.cpp")
_, notiter_err = diagnostic("notiter.cpp")

invalid_out, invalid_err, invalid_rc = build_and_run("invalidate.cpp", sanitize=True)
if "heap-use-after-free" not in invalid_err:
    raise SystemExit("invalidate.cpp must be caught as a use-after-free by ASan")

print("all evidence captured")

BLOCKS = {
    "noops":        fence("cpp", "run", read("noops.cpp"), noops_out),
    "vec2":         fence("cpp", "run", read("vec2.cpp"), vec2_out),
    "stream":       fence("cpp", "run", read("stream.cpp"), stream_out),
    "compound":     fence("cpp", "run", read("compound.cpp"), compound_out),
    "chain":        fence("cpp", "run", read("chain.cpp"), chain_out),
    "subscript":    fence("cpp", "run", read("subscript.cpp"), subscript_out),
    "functor":      fence("cpp", "run", read("functor.cpp"), functor_out),
    "arrow":        fence("cpp", "run", read("arrow.cpp"), arrow_out),
    "shortcircuit": fence("cpp", "run", read("shortcircuit.cpp"), shortcircuit_out),
    "fixedvec":     fence("cpp", "run", read("fixedvec.cpp"), fixedvec_out),
    "ring":         fence("cpp", "run", read("ring.cpp"), ring_out),
    "traits":       fence("cpp", "run", read("traits.cpp"), traits_out),
    "invalidate":   fence("cpp", "run-san-catch", read("invalidate.cpp"),
                          "ERROR: AddressSanitizer: heap-use-after-free"),
    "member_only":  fence("cpp", "bad", read("member_only.cpp"),
                          err_msg(member_err, "invalid operands to binary expression")),
    "arity":        fence("cpp", "bad", read("arity.cpp"),
                          err_msg(arity_err, "must be a unary operator")),
    "assign_nm":    fence("cpp", "bad", read("assign_nm.cpp"),
                          err_msg(assign_err, "must be a non-static member function")),
    "stream_member": fence("cpp", "bad", read("stream_member.cpp"),
                           err_msg(stream_member_err, "invalid operands to binary expression")),
    "eqonly":       fence("cpp", "bad", read("eqonly.cpp"),
                          err_msg(eqonly_err, "invalid operands to binary expression")),
    "sortrange":    fence("cpp", "bad", read("sortrange.cpp"),
                          err_msg(sort_err, "invalid operands to binary expression")),
    "notiter":      fence("cpp", "bad", read("notiter.cpp"),
                          err_msg(notiter_err, "invalid operands to binary expression")),
}

# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------
DOC = """---
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

@@noops@@
Now the same thing with operators.

@@vec2@@
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

@@arity@@
Note that the complaint is about the *shape* of the declaration, not about the body. The compiler
never got as far as what your operator was going to do.

And `operator=` as a free function:

@@assign_nm@@
`=` acts on an object that already exists, so it has to be a member of the type it assigns to. The
same reasoning applies to `[]`, `()` and `->`: all four take "the object" as their starting point in
a way a free function cannot express.

## Member or non-member: let symmetry decide

An operator declared as a member has the left operand as `this`. That is the whole rule, and it has
one consequence you will hit immediately: a member `operator*` makes `v * 2.0` work and `2.0 * v`
fail.

@@member_only@@
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

@@stream_member@@
Written as a non-member, with the stream as the first parameter, it works — and because it returns
the stream by reference, calls chain:

@@stream@@
The `return os << ...;` shape is not decoration. Returning the same stream is what makes
`out << a << " and " << b` one expression, and it is why the return type is
`std::ostream &` rather than `void`.

## Compound first, then the plain operator

There are two operators to write for addition — `+` and `+=` — and one of them is the real one.
Implement `+=` once, correctly, and then express `+` in terms of it:

@@compound@@
`+=` mutates and returns `Counter &`, a reference to the object it modified, which is what makes
`(b += 1) += 2` legal and meaningful. `+` takes its argument **by value** — so it is already working
on a copy — applies `+=` to that copy, and returns it. One definition holds the arithmetic; the other
is three lines that cannot disagree with it.

The payoff is visible in what the copy buys. Here is the same type, and an attempt to chain onto the
result of `+`:

@@chain@@
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

@@eqonly@@
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

@@subscript@@
Without the const overload, `const Row` could not be indexed at all, which would make every
read-only function that takes one by reference unusable.

`operator()` makes an object callable. A *functor* differs from a free function in one way that
matters: it can carry state.

@@functor@@
`DivisibleBy{3}` is an object holding `d = 3`, and `DivisibleBy{3}(n)` is a call. The same object
works with `std::count_if` because the algorithm only requires that its predicate be callable with
one argument — it does not care whether that callable is a function pointer, a lambda, or a struct
with `operator()`.

`operator->` must return a pointer, or something that itself has `operator->`. The language then
applies `->` again to the result:

@@arrow@@
This is what makes smart pointers work at all: `p->member()` has to reach `member` through the
wrapper, and `operator->` returning the raw pointer is the mechanism.

## What not to overload

The short answer is: stop when the operator's meaning would surprise the reader. Three cases are
worth stating precisely, because the first one is a real trap rather than a style opinion.

@@shortcircuit@@
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

@@notiter@@
`Iter` has `*` and `++`, but no `!=`, so the loop cannot even be written. Note where the error
points: at the `for`, not at the missing operator — and note the second line, which names the
implicit `operator!=` call the expansion needs. When a range-for fails to compile on your own type,
this is the diagnostic to expect.

## The easiest iterator is one you already have

For contiguous storage, a raw pointer satisfies every requirement of a random access iterator, so
`begin` and `end` are two typedefs and two one-line functions:

@@fixedvec@@
`std::find` and `std::count` work on it with no further effort, because they are templates over
iterators and never mention the container. This is the single most important consequence of the
iterator design: **an algorithm you did not write, written years before your type existed, works on
your type** as long as your iterator answers the questions the algorithm asks.

## An iterator that has to do work

A ring buffer is the interesting case. Its elements are *not* in storage order once it has wrapped
around, so the iterator has to convert a logical position into a storage index on every dereference:

@@ring@@
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

@@traits@@
- **input / output** — single pass, read or write once. Stream iterators live here.
- **forward** — multi-pass, only `++`. `std::forward_list`, and the `Ring::iterator` above.
- **bidirectional** — also `--`. `std::list`, `std::map`, `std::set`.
- **random access** — also `+ n`, `- n`, `[]`, and `<`. `std::vector`, `std::deque`, and pointers.

The category is not documentation; it is enforced. `std::sort` needs to jump around, so it computes
`last - first` — and a list iterator has no subtraction:

@@sortrange@@
The error points into `<algorithm>` internals rather than at your call, which is the signature of a
requirement violation: the mistake is at `std::sort(l.begin(), l.end())`, but the diagnostic is
wherever the subtraction physically appears. (C++20 concepts turn this into an error that names the
requirement — Chapter 33.) The fix is not to make the code compile but to ask for the right thing:
`l.sort()` is a member because a list knows how to sort itself by relinking.

## Invalidation: an iterator is a position, not a value

The last thing to know about iterators is how they die.

@@invalidate@@
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
    std::printf("first > 3 is %d at index %ld\\n", *it,
                std::distance(r.begin(), it));
} else {
    std::printf("none\\n");
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
std::printf("first = %d\\n", v[first_index]);
```

If you must keep an iterator, then keep it *after* the growth instead of across it — reserve enough
capacity up front (`v.reserve(5)` before any `push_back`) and re-take `v.begin()` after the last
insertion. Both fixes are the same principle: an iterator is a claim about memory, and a claim you
made before a reallocation is a claim about memory you no longer own.
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
