---
chapter: 0
part: 0
title: How to Use This Book
summary: Know what you are building, why C comes before C++, and the one habit that separates people who learn this from people who bounce off it.
minutes: 12
tags: [orientation, how to read, tooling]
---

C and C++ have a reputation for being hard, and the reputation is half earned and half a
misunderstanding. They are hard the way woodworking is hard: nothing stops you from cutting through
the table, and the saw will not warn you. But that same lack of guard rails is why every operating
system, every browser, every database and every game engine is written in them. This book takes you
from "I have never compiled anything" to shipping three real programs — a systems tool, a web
service and a game — and it does it by making you write code from the first page, not by explaining
syntax at you.

## What you are actually building

Three projects, each larger than the last, each written in the language that suits it:

| Project | What it is | Language | Why that language |
|---|---|---|---|
| **A systems tool** | A real command-line program that does something the standard tools do not | C | C is the language of the operating system. You will use `open`, `read` and `write` directly. |
| **A web service** | An HTTP server that answers real requests over a real socket | C++ | You will do the socket work by hand before reaching for a framework, so the framework is not magic. |
| **A game** | A playable game with a loop, input, collision and enemies | C++ | Games need deterministic memory and predictable timing. This is where C++ earns its keep. |

The order matters. C teaches you what a pointer, a stack frame and a heap allocation actually are,
because in C there is nothing between you and them. C++ then gives you tools — `std::vector`,
`std::string`, `std::unique_ptr` — that make those things safe. If you learn C++ first you will use
those tools without understanding what they protect you from, and the first time one fails you will
have no model to debug with.

## Why C before C++, concretely

Here is the same job — "add three numbers up" — in both languages. In C, the array's length is
written down twice and nothing connects the two copies:

```c run
#include <stdio.h>

int main(void) {
    int values[3] = {10, 20, 30};
    int total = 0;

    for (int i = 0; i < 3; i++) {
        total += values[i];
    }

    printf("total = %d\n", total);
    return 0;
}
```

```text
total = 60
```

The `3` appears in `int values[3]` and again in `i < 3`. The compiler checks that both are integers;
it has no idea they are supposed to describe the same thing. That is not a flaw in the example, it
is the defining property of C: **the length of an array is not part of the array.** Add a fourth
value and forget the loop bound, and you get a program that compiles cleanly, runs, and quietly
gives you the wrong answer — or worse, reads memory that belongs to something else. You will do
exactly that in Exercise 3, and meet the tool that catches it.

In C++ the length is a property of the data, so the two facts cannot drift apart:

```cpp run
#include <iostream>
#include <vector>
#include <numeric>

int main() {
    std::vector<int> values{10, 20, 30};

    int total = std::accumulate(values.begin(), values.end(), 0);

    std::cout << "total = " << total << "\n";
    return 0;
}
```

```text
total = 60
```

The number `3` does not appear anywhere. `values.begin()` and `values.end()` come from the
container, so they always agree with it — including after you add a fourth value. That is the whole
arc of this book: start where the machine is visible, end where the machine is safe.

## The one habit that matters

**Type every example. Do not read it.**

Reading code feels like learning and is not. Your brain accepts `values[i]` as obviously fine; your
fingers, having typed it wrong once, remember it. This is not a motivational slogan — it is the
difference between recognising C++ and being able to write it.

Then break it. Every example here is followed by an explanation of what it does; change a number,
delete a line, swap a type, and see what the compiler says. The compiler is the best teacher you
will ever have, and it is available at 3 a.m. Learning to read its output is a skill in its own
right, and you start on it in Chapter 1.

## Every example in this book has been compiled and run

This matters enough to state plainly. A programming book that teaches a snippet which does not build
is worse than no book at all: you copy it, it fails, and you conclude that *you* are the problem. So
the code here is not written from memory and hoped over. Every program in this book is extracted
automatically and put through a real compiler before the chapter ships, and its printed output is
compared against the output printed in the text. Where an example is *supposed* to fail to compile —
and several are, because a rejected program teaches more than a paragraph about rules — that
rejection is checked too.

:::note What that means for you
If you type a program exactly as printed and it does not work, that is a bug in the book. Assume a
typo of your own first, because it usually is one — but if you have checked carefully, you are right
to be annoyed.
:::

The book is written against **C17 for the C chapters and C++17 for the C++ chapters**, compiled with
`clang++` or `g++` on macOS or Linux. Where a result depends on the machine — the size of a `long`,
for instance — the text says so rather than quoting a number that is only true on the author's
laptop.

## How to read a chapter

Every chapter has the same shape, and the shape is deliberate:

- **Teaching sections first**, each naming the problem before it names the feature. "Here is a
  `struct`" teaches nothing; "you have four fields that must always travel together" does.
- **A real scenario** — a `:::scenario` box — puts the idea in a workplace situation, followed by
  how an experienced developer actually handles it. Read these even when the code looks easy; they
  are where judgement gets transferred.
- **A pitfall** — a `:::pitfall` box — names a mistake people genuinely make. These are not
  hypotheticals. Each one has cost somebody an afternoon.
- **Key takeaways** are checkable statements, not encouragement. If you cannot explain one to
  somebody else, go back to that section.
- **Practice, then Solutions.** Do the exercises before reading the solutions. The solutions are
  complete programs and have been compiled and run like everything else.

Work in order. Chapters assume the previous ones — Chapter 7 on pointers assumes the stack frames
from Chapter 6, and the C++ chapters assume you know what `new` does because you will have done it
by hand in C.

## Key takeaways

- C makes the machine visible and C++ makes it safe; you learn C first so the safety has meaning.
- An array in C does not know how long it is. The length is a separate fact that you maintain.
- Type every example. Reading code and writing code use different attention, and only one transfers.
- Breaking working code on purpose is the fastest way to learn what the rules protect you from.
- Every program in this book is compiled and run before it ships, and its output is checked against
  the printed output.
- The compiler is a tool you are learning to read, not an oracle you are hoping to satisfy.
- The three projects — systems tool, web service, game — are the point. The chapters are how you get
  to them.

## Practice

- [ ] Set up the toolchain by working through Chapter 1, then compile and run the C example above
      and confirm it prints `total = 60`.
- [ ] Add a fourth value, `40`, to the C array and update the loop bound so the program prints `100`.
- [ ] Now add a fourth value but leave the loop bound at `3`, and note what the program prints. Then
      run it under AddressSanitizer with the bound set to `4` on a three-element array and see what
      the tool says. (Chapter 1 shows the exact command.)
- [ ] Run the C++ example, then add `40` to the vector and confirm it prints `100` **without
      touching anything else**.
- [ ] Write down, in one sentence each, why the C version can silently be wrong and the C++ version
      cannot. Keep this note; you will re-read it in Chapter 20.

## Solutions

:::solution Exercise 2
Four values, four in the bound — both copies of the fact updated together.

```c run
#include <stdio.h>

int main(void) {
    int values[4] = {10, 20, 30, 40};
    int total = 0;

    for (int i = 0; i < 4; i++) {
        total += values[i];
    }

    printf("total = %d\n", total);
    return 0;
}
```

```text
total = 100
```

This is correct, and the reason it is correct is entirely social: you remembered to change both
`3`s. Nothing in the language enforced it, and no compiler warning would have fired if you had
changed only one. Compare Exercise 4, where the same edit needs no second change at all.
:::

:::solution Exercise 3
Leaving the bound at `3` gives `60` — a plausible-looking number that is simply missing the fourth
value. Raising the bound to `4` on a three-element array is the interesting failure:

```c run-san-catch
#include <stdio.h>

int main(void) {
    int values[3] = {10, 20, 30};
    int total = 0;

    for (int i = 0; i < 4; i++) {
        total += values[i];
    }

    printf("total = %d\n", total);
    return 0;
}
```

```text
stack-buffer-overflow
```

The first version compiles cleanly and prints a number that looks right, which is why this class of
bug survives code review. The second reads one element past the end of `values` — memory that
belongs to some other variable, or to nothing. That is undefined behaviour, not "getting whatever
happened to be there": the compiler is free to do anything at all with it. AddressSanitizer catches
it immediately and names the line. Chapter 7 explains what the stack looks like and whose bytes the
fourth read actually lands on.
:::

:::solution Exercise 4
Only the data changes; the loop reads the container.

```cpp run
#include <iostream>
#include <vector>
#include <numeric>

int main() {
    std::vector<int> values{10, 20, 30, 40};

    int total = std::accumulate(values.begin(), values.end(), 0);

    std::cout << "total = " << total << "\n";
    return 0;
}
```

```text
total = 100
```

One edit instead of two, and no version of this program can have a bound that disagrees with the
data, because the bound is not written down. This is what people mean when they say C++ is safer
than C — not that it cannot go wrong, but that a whole category of mistake has nowhere to live.
:::
