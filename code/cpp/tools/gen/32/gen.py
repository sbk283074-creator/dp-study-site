#!/usr/bin/env python3
"""Generate chapters/32-value-categories-and-perfect-forwarding.md.

Every `text` fence is captured from a real clang++ run and every source block is
read off disk, so nothing in the chapter is retyped.

    python3 tools/gen/32/gen.py
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/32 -> gen -> tools -> cpp
OUT = CHAPTERS / "32-value-categories-and-perfect-forwarding.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]
TIMEOUT = 60


def build_and_run(name: str):
    src = HERE / name
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-Werror", "-o", exe, str(src)]
        b = subprocess.run(cmd, text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        if b.returncode != 0:
            raise SystemExit(f"{name} failed to build:\n{b.stderr}")
        r = subprocess.run([exe], text=True, capture_output=True, cwd=td, timeout=TIMEOUT)
        return r.stdout, r.stderr, r.returncode


def diagnostic(name: str, marker: str):
    """Compile with -Wall -Wextra and NO -Werror; return the first `marker` line.

    `bad` must be rejected; `warn` must still build. Both are checked.
    """
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


def msg(blob: str, marker: str, needle: str) -> str:
    """Return `<marker> <message>` for the first diagnostic containing `needle`.

    The raw line carries this machine's absolute path, which must never reach
    the book, so only the part after the marker is published.
    """
    for line in blob.splitlines():
        if needle in line and marker in line:
            return marker + " " + line.split(marker, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{blob}")


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

categories_out, _, _ = build_and_run("categories.cpp")
tracked_out, _, _ = build_and_run("tracked.cpp")
constmove_out, _, _ = build_and_run("constmove.cpp")
nrvo_out, _, _ = build_and_run("nrvo.cpp")
collapse_out, _, _ = build_and_run("collapse.cpp")
universal_out, _, _ = build_and_run("universal.cpp")
forward_out, _, _ = build_and_run("forward.cpp")
mymove_out, _, _ = build_and_run("mymove.cpp")
moveonly_out, _, _ = build_and_run("moveonly.cpp")
autorr_out, _, _ = build_and_run("autorr.cpp")
vecgrowth_out, _, _ = build_and_run("vecgrowth.cpp")

bind_err = diagnostic("bindrvalue.cpp", "error:")
movefail_err = diagnostic("movefail.cpp", "error:")
pess_err = diagnostic("pessimizing.cpp", "warning:")

print("all evidence captured")

BLOCKS = {
    "categories": fence("cpp", "run", read("categories.cpp"), categories_out),
    "bindrvalue": fence("cpp", "bad", read("bindrvalue.cpp"),
                        msg(bind_err, "error:", "cannot bind to lvalue")),
    "tracked":    fence("cpp", "run", read("tracked.cpp"), tracked_out),
    "constmove":  fence("cpp", "run", read("constmove.cpp"), constmove_out),
    "nrvo":       fence("cpp", "run", read("nrvo.cpp"), nrvo_out),
    "pessimizing": fence("cpp", "warn", read("pessimizing.cpp"),
                         msg(pess_err, "warning:", "prevents copy elision")),
    "collapse":   fence("cpp", "run", read("collapse.cpp"), collapse_out),
    "universal":  fence("cpp", "run", read("universal.cpp"), universal_out),
    "forward":    fence("cpp", "run", read("forward.cpp"), forward_out),
    "mymove":     fence("cpp", "run", read("mymove.cpp"), mymove_out),
    "moveonly":   fence("cpp", "run", read("moveonly.cpp"), moveonly_out),
    "movefail":   fence("cpp", "bad", read("movefail.cpp"),
                        msg(movefail_err, "error:", "implicitly-deleted copy constructor")),
    "autorr":     fence("cpp", "run", read("autorr.cpp"), autorr_out),
    "vecgrowth":  fence("cpp", "run", read("vecgrowth.cpp"), vecgrowth_out),
}

# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------
DOC = """---
chapter: 32
part: 4
title: Value Categories and Perfect Forwarding
summary: Understand lvalues, xvalues and prvalues as the thing overload resolution actually reads, learn that std::move is a cast that can silently do nothing, and use reference collapsing and std::forward to hand an argument through a wrapper without changing what it was.
minutes: 75
tags: [value-categories, lvalue, rvalue, xvalue, prvalue, std-move, std-forward, perfect-forwarding, forwarding-reference, reference-collapsing, nrvo, copy-elision, universal-reference]
---

Chapter 25 introduced move semantics as a way to avoid copying. This chapter is about the machinery
that decides *whether a move is even possible*, and about the second problem it solves: passing an
argument through a function without changing what it was.

There are two questions the type system asks about every expression, and they are not the same
question:

1. **Can I take resources from this thing?** Answered by the value category: an lvalue is something
   with a name that other code can still reach, so stealing from it is dangerous; an rvalue is a
   temporary or an explicit "I am finished with this", so taking from it is safe.
2. **What did the caller actually pass?** Answered by `std::forward`, which recovers that answer from
   the template parameter after ordinary naming has thrown it away.

The first is why move constructors exist. The second is why `std::forward` exists, and it is the one
nobody believes until they see an overload set pick the wrong function.

## Categories: what overload resolution reads

Every expression in C++ has a type and a value category. The categories are:

| Category | What it is | Example |
|---|---|---|
| **lvalue** | has a name (or an address you can take); outlives this expression | `i`, `v[0]`, `*p`, a function returning `T&` |
| **xvalue** | an lvalue you have declared finished — "expiring" | `std::move(i)`, a function returning `T&&` |
| **prvalue** | a pure result, not yet an object with a location | `3`, `i + 1`, a function returning `T` |

Grouped the other way: **glvalue** = lvalue ∪ xvalue (has identity), and **rvalue** = xvalue ∪
prvalue (can be moved from). The grouping is what the rules are written against: an rvalue reference
binds to rvalues, and a move constructor takes `T&&`.

None of this is visible in a program unless something distinguishes it. Three overloads do:

@@categories@@
`f(i)` picks `int&` because `i` is an lvalue. `f(3)` and `f(i + 1)` pick `int&&` because a literal and
the result of `+` are prvalues. And `f(std::move(i))` picks `int&&` too — which is the entire
definition of what `std::move` does: **it does not move, it changes the category of the expression so
that the rvalue overload is the one that gets selected.**

An rvalue reference is a reference that *binds* to rvalues. It will not bind to an lvalue, and the
error is worth reading once:

@@bindrvalue@@
The corollary is the fact that trips everyone: inside the function, a *named* rvalue reference is an
lvalue. `void g(int &&x)` gives you a variable named `x`, and a variable is an lvalue, so
`h(x)` calls `h(int&)`. The reference type says what it bound to; it does not change what the name
is.

## std::move is a cast

Watch the constructors instead of trusting the name. This type logs every one:

@@tracked@@
Three things to read out of that output. `Tracked b{a}` ran the copy constructor. `Tracked
c{std::move(a)}` ran the move constructor — and the move constructor sets `o.id = -1`, which is why
`a.id` is `-1` afterwards: the resource really was transferred. And the destruction order confirms
it: `c` and `b` still hold `1`, while `a` holds the sentinel `-1`.

A moved-from object is not destroyed and not poisoned. It is in **a valid but unspecified state**,
which is a promise you make in your own move constructors: the destructor must still work, and so
must assignment. `-1` here is a deliberate marker; a real type would leave it empty or zero.

### The const trap

@@constmove@@
`std::move(a)` on a `const Tracked` produces `const Tracked&&`. The move constructor takes
`Tracked&&` and cannot bind to something const, so it is not viable; the copy constructor takes
`const Tracked&` and can. **The copy runs, silently** — `a.id` is still `1`, exactly as the output
says.

This is the single most common way a "move" fails to happen, and there is no diagnostic for it,
because nothing is wrong: you asked for a conversion the type system could not grant, and the next
best overload took the call. If a move is not happening, check the constness of the source before you
check anything else.

## Returning: the language already knows

A named local is about to die, so the language already treats `return local;` as an rvalue — and,
better than that, allows the object to be constructed directly in the caller's storage:

@@nrvo@@
One `construct`, no copy, no move. That is named return value optimisation (NRVO), and it is better
than a move: zero work. Adding `std::move` cannot improve on zero, and in fact removes the
possibility:

@@pessimizing@@
That is a real compiler verdict, not a style preference. `return std::move(local)` forces the object
to exist in the callee's frame and then be moved out, and it makes the elision impossible. The rule
is simple: **never write `std::move` on a `return` of a local object.** (It is fine, and sometimes
necessary, when returning something that is not a local — a member, or a parameter — where no elision
is possible anyway.)

## Where moves happen in ordinary code

You rarely write `std::move` at all. The place it matters is containers:

@@vecgrowth@@
`reserve(2)` makes the first two `emplace_back` calls pure constructions. The third exceeds capacity,
so the vector allocates a bigger block and relocates the existing elements — and it *moves* them,
because `Tracked` has a `noexcept` move constructor. The two `destroy id=-1` lines are the
moved-from shells being destroyed right after.

That `noexcept` is load-bearing. `std::vector` only uses move during reallocation if the move
constructor cannot throw; otherwise it must fall back to copying, because a half-finished relocation
that threw would leave the vector unrecoverable. Declaring a move constructor that cannot throw as
`noexcept` is not a micro-optimisation — it is what selects the entire strategy.

## Reference collapsing

Forwarding rests on four rules you cannot write down directly, because `int & &` is not something
you are allowed to spell. Collapse happens only through a template parameter or a typedef:

@@collapse@@
Three of the four collapse to `T&`. The summary people remember is **an lvalue reference anywhere
wins**: only `T&& &&` stays an rvalue reference.

## `T&&` is not always an rvalue reference

This is the distinction that unlocks the rest. In `void g(int &&x)` the type is concrete, so `int&&`
is an rvalue reference and nothing is deduced. But in a template where `T` is deduced, `T&&` is a
**forwarding reference** (historically "universal reference"), and what it becomes depends entirely
on what `T` deduced to:

@@universal@@
Pass an rvalue and `T` deduces to `int`, so the parameter is `int&&`. Pass an lvalue and `T` deduces
to `int&`, so the parameter is `int& &&`, which collapses to `int&`. That is the whole trick: **the
lvalue-ness of the argument is recorded in `T`**, and it is available later.

## Perfect forwarding

So here is the problem. Inside the wrapper, the parameter has a name — and a named variable is an
lvalue, whatever its type. The information about the caller's argument is still in `T`, but using the
name directly throws it away:

@@forward@@
Read the last line. `unforwarded(5)` passed a literal, and `sink(int&)` was called — an rvalue
arrived as an lvalue. `std::forward<T>(x)` restores it: `forwarded(5)` reaches `sink(int&&)`, while
`forwarded(i)` still reaches `sink(int&)` and `forwarded(c)` still reaches `sink(const int&)`. The
category the caller passed is the category the callee sees. That is what "perfect" means here — not
fast, but lossless.

The two functions differ by exactly one token, and that token is doing all the work.

### Both of them are one line each

It is worth seeing that there is no magic, because the moment you see the definitions the rule stops
being arbitrary:

@@mymove@@
`std::move` is a `static_cast` to `T&&` — an unconditional conversion to an rvalue reference.
`std::forward<T>` is a `static_cast` to `T&&` where `T` may itself be an lvalue reference, and
collapsing is what turns that back into `T&` when it is. So:

- **`std::move(t)`** — "I am done with this; let it be taken from." Use it when you *know* you want a move.
- **`std::forward<T>(t)`** — "pass on whatever the caller gave me." Use it inside a forwarding reference, and only there.

The `static_assert`s in that block are the specification: `my_forward<int>(i)` yields `int&&` while
`my_forward<int &>(i)` yields `int&`. One function, two return types, decided by the template
argument.

## Move-only types: where forwarding stops being academic

A `std::unique_ptr` cannot be copied at all. Hand one to a wrapper and there is exactly one way
through:

@@moveonly@@
And if you forget the `std::move` at the call site, `T` deduces to `unique_ptr<Task>&`, `forward`
faithfully produces an lvalue, and the copy constructor — the one that does not exist — is selected:

@@movefail@@
Note where the error points: at `std::forward<T>(t)`, one frame away from the actual mistake, which
is `relay(p)` passing an lvalue. The rule for move-only types is therefore worth stating plainly:
**ownership is transferred at the call site with `std::move`, and preserved through the wrapper with
`std::forward`.** One is about the value, the other is about the shape.

## `auto &&` in a range-for

The same deduction happens in a loop, and it is the reason `auto &&` is the safe default when you do
not know what a range yields:

@@autorr@@
`auto x` copies each element, so doubling `x` leaves the vector alone. `auto &&x` deduces to `int&`
and binds to the element itself, so the write lands in the vector. For a range that yields *proxy*
objects rather than real references — a `std::vector<bool>` is the famous case — `auto &&` is the
only form that binds cleanly, which is why it is the habit worth forming.

:::pitfall Forwarding references are greedy
`template <typename T> void f(T &&)` matches almost anything, including things you did not mean to
catch: it will beat an overload taking `const std::string&` for a `const char *` argument, because the
deduced `T = const char (&)[N]` is an exact match. If a wrapper template starts stealing calls from a
more specific overload, constrain it — with `std::enable_if` in C++17, or with a concept in C++20
(Chapter 33). A forwarding reference is a very wide net, and "perfect" only describes how it passes
things along, not whether it should have caught them.
:::

:::scenario A factory that copies when it should move
```cpp
template <typename T, typename Arg>
T make(Arg &&arg) {
    return T(std::forward<Arg>(arg));
}
```

You call `make<Widget>(std::move(w))` and profiling shows a copy of `w` where you expected a move.
The `std::forward` is there and `Widget` has a move constructor. What is left to check?
:::

:::solution
Two candidates, and the first one is the one from earlier in this chapter: **is the parameter
`const`?** If the call site is `const Widget w; ... make<Widget>(std::move(w))`, then `Arg` deduces to
`const Widget&`, `forward` yields a const lvalue, and `Widget(const Widget&)` is the only viable
constructor. `std::move` on a const object asks for a conversion the type system cannot grant, and
the copy silently takes the call. The fix is at the call site: the source has to be non-const.

The second candidate is subtler and worth knowing even though it is not the bug here: if `T`'s
constructor is a template itself, or if `Widget` has no move constructor at all (say it has a
user-declared destructor and you never wrote one, so the implicit move was suppressed), then no move
is available and the copy is correct behaviour.

Confirm which one you have by making it observable — temporarily give `Widget` logging constructors
exactly as `Tracked` does in this chapter, and read the output instead of reasoning about it. A move
that does not happen never announces itself; you have to make it print.
:::

## Key takeaways

- Every expression has a type and a value category. lvalues can be reached again later; rvalues (xvalues and prvalues) can be moved from. Grouped: glvalue = lvalue ∪ xvalue, rvalue = xvalue ∪ prvalue.
- `std::move` does not move. It is a cast to `T&&` that changes the *category*, so the rvalue overload is selected. Whether anything moves is then decided by overload resolution.
- A named rvalue reference is an lvalue. Inside `void g(int &&x)`, passing `x` onward calls the `int&` overload.
- `std::move` on a `const` object produces `const T&&`, which cannot bind to `T&&`, so the copy constructor runs — silently, with no diagnostic.
- Never `return std::move(local);`. The language already treats a returned local as an rvalue, and NRVO can elide the transfer entirely; the explicit move forbids the elision and `-Wpessimizing-move` says so.
- Reference collapsing has four rules and one summary: an lvalue reference anywhere wins. Only `T&& &&` stays an rvalue reference.
- `T&&` with a deduced `T` is a *forwarding* reference: the argument's lvalue-ness is recorded in `T` (`int&` for lvalues, `int` for rvalues).
- `std::forward<T>(x)` recovers that recorded category; using `x` directly loses it, and an rvalue arrives as an lvalue. Move-only types make the difference unmissable.
- `noexcept` on a move constructor is what lets `std::vector` move instead of copy during reallocation. It selects a strategy, not just a fast path.
- `auto &&` in a range-for binds to whatever the range yields, which is why it mutates in place and why it is the safe default for ranges returning proxies.

## Practice

- [ ] 1. Predict which of `f(int&)`, `f(const int&)` and `f(int&&)` is chosen for `f(i++)`, `f(++i)`, `f(i + 0)` and `f(std::move(i))`, then check by adding the lines. (`i++` and `++i` are the interesting pair.)
- [ ] 2. Write `void g(int &&x)` that calls `f(x)` and then `f(std::move(x))`, where `f` is the three-overload set from this chapter. Explain the two lines of output.
- [ ] 3. Give `Tracked` a move-assignment operator and assign a moved-from object to a fresh one. What does the log show, and what does that tell you about the "valid but unspecified" state?
- [ ] 4. Write a `wrapper` template that takes `T&&` and stores the argument in a `std::decay_t<T>` member, initialising it in the constructor's init-list with `std::forward<T>`. Show that it stores a copy for an lvalue and a move for an rvalue.
- [ ] 5. `relay(p)` on a `unique_ptr` failed to compile. Fix the call site so ownership is transferred, and then show that `relay(std::move(p))` leaves `p` null — i.e. that the move really happened through the wrapper.

## Solutions

:::solution Exercise 1
`i++` yields a prvalue (the old value, materialised as a temporary), so it selects `f(int&&)`.
`++i` yields an **lvalue** — it returns a reference to `i` itself — so it selects `f(int&)`.
`i + 0` is a prvalue, `f(int&&)`. `std::move(i)` is an xvalue, `f(int&&)`.

The `++/++i` pair is the reason this is worth doing: they differ by one character in the source and
by an entire value category in the type system. If you ever need the postfix form to be an lvalue,
you cannot have it — that is the whole reason `++i` is the recommended form in loops over iterators
(Chapter 31): the prefix form hands back the object, the postfix form hands back a temporary.
:::

:::solution Exercise 2
```cpp
void g(int &&x) {
    f(x);              // sink(int&)   -- x has a name, so it is an lvalue
    f(std::move(x));   // sink(int&&)  -- the cast restores the category
}
```

The type of `x` is `int&&` in both lines. What changes is the *expression*: a named variable is an
lvalue, and `std::move(x)` is an xvalue. This is the compact form of the whole forwarding problem —
and the reason a wrapper needs `std::forward<T>` rather than a plain `std::move`: `std::move` would
always say "rvalue", and the caller's lvalue would be stolen from unexpectedly.
:::

:::solution Exercise 3
```cpp
Tracked &operator=(Tracked &&o) noexcept {
    if (this != &o) { id = o.id; o.id = -1; std::printf("move-assign id=%d\\n", id); }
    return *this;
}
```

Assigning from a moved-from object (`a.id == -1`) copies `-1` across and sets the source to `-1`
again. It works, and the result is useless — which is precisely what "valid but unspecified"
promises: **the object is safe to destroy and safe to assign to, but you may not read it expecting a
meaningful value.** A real type would satisfy that by leaving the moved-from object empty: a moved-from
`std::vector` is empty, a moved-from `std::string` is typically empty, a moved-from `unique_ptr` is
null. Note the self-assignment guard: `a = std::move(a)` is legal, and without the check it would set
`id` to `-1` and then read it back.
:::

:::solution Exercise 4
```cpp
template <typename T>
class Wrapper {
    std::decay_t<T> value;
public:
    explicit Wrapper(T &&v) : value(std::forward<T>(v)) {}
    const std::decay_t<T> &get() const { return value; }
};
```

`std::decay_t<T>` is what turns the deduced type into something storable: for `T = int&` it is `int`,
for `T = int` it is `int`, for `T = const char (&)[6]` it is `const char *`. Without it the member
would be a reference to the caller's object for lvalues and a value for rvalues — a type that cannot
even be declared uniformly. The constructor's parameter is `T&&` (a forwarding reference, because `T`
is the class's parameter), so `Wrapper<Tracked> w{t}` with an lvalue `t` logs a `copy`, and
`Wrapper<Tracked> w{std::move(t)}` logs a `move`. One class, two behaviours, selected by the caller —
which is exactly what `std::pair`, `std::tuple` and every factory in the standard library do.
:::

:::solution Exercise 5
```cpp
auto p = std::make_unique<Task>(Task{7});
relay(std::move(p));                       // transfer ownership at the call site
std::printf("p is now %s\\n", p ? "alive" : "null");
```

The output is `p is now null`, and that null is the proof: `take` received ownership, and the move
happened *through* the wrapper rather than being copied or blocked. `std::move` at the call site
makes the argument an xvalue, so `T` deduces to `unique_ptr<Task>`; `std::forward<T>` inside `relay`
preserves the rvalue-ness, so `take`'s by-value parameter is initialised by the move constructor; and
the move constructor nulls the source. If you drop either half — no `move` at the call, or no
`forward` in the wrapper — you get a compile error about a deleted copy constructor, and the error
points inside the wrapper rather than at the line you actually need to change.
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
