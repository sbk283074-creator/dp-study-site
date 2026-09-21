---
chapter: 1
part: 0
title: Your Workbench
summary: Install a compiler, understand the four stages that turn a .cpp file into a running program, memorise the flags that catch real bugs, and learn to read a diagnostic instead of fearing it.
minutes: 45
tags: [toolchain, clang, gcc, flags, sanitizers, make, gdb]
---

Before you can learn a language you need a loop you can trust: write something, build it, run it,
see what happened. Most people who give up on C or C++ never had that loop working properly — they
fought the toolchain, blamed the language, and stopped. This chapter builds the loop and, more
importantly, teaches you to use the compiler as an advisor rather than an obstacle. By the end you
will have a command you can type from muscle memory, a set of flags that catch whole categories of
bug before the program ever runs, and the habit of reading an error message rather than skimming it.

## What the compiler actually is

"Compiler" is shorthand for four programs that run in sequence. Knowing which one is complaining is
most of what makes error messages readable.

| Stage | What it does | What it complains about |
|---|---|---|
| **Preprocessor** | Handles `#include`, `#define`, `#if`. Pure text substitution. | A missing file (`file not found`), a malformed macro. |
| **Compiler** | Turns your source into assembly for the target CPU. | Almost everything you will meet: type errors, missing semicolons, wrong argument counts. |
| **Assembler** | Turns that assembly into machine code — an **object file** (`.o`). | Rarely; only if the compiler emitted something odd. |
| **Linker** | Joins your object files and libraries into one executable. | *"I told you this function exists but I cannot find it"* — the classic `undefined symbol`. |

The distinction that will save you the most time is compiler versus linker. If the message names a
line of *your* code, it is the compiler. If it says something like `undefined reference to 'foo'`,
the compiler was happy and the linker cannot find `foo`'s body — usually because you forgot to
compile the file that defines it, or misspelled it in a declaration. Chapter 13 is entirely about
that distinction.

## Hello, world, and the command that builds it

Save this as `hello.cpp`:

```cpp run
#include <iostream>

int main() {
    std::cout << "Hello, world!\n";
    return 0;
}
```

```text
Hello, world!
```

Now build and run it. This is the command you will type several thousand times:

```bash
clang++ -std=c++17 -Wall -Wextra -Werror -o hello hello.cpp
./hello
```

`-o hello` names the output. Without it you get a file called `a.out`, which is fine for ten minutes
and confusing for ten years. `./hello` runs it — the `./` is required because on Unix your current
directory is not searched for programs, deliberately.

If you prefer GCC, `g++` takes the same flags. Everything in this book works with either.

You can stop after compiling, which is useful when you want to build several files separately:

```bash
clang++ -std=c++17 -c -o hello.o hello.cpp
```

`-c` means "compile only, do not link". On this machine that produces a 9,808-byte object file,
and the finished executable is 38,376 bytes — the difference is the C++ runtime that the linker
adds. That gap is the linker's job made visible.

## The flags worth memorising

| Flag | What it does | Why you want it |
|---|---|---|
| `-std=c++17` | Selects the language version. | Without it you get the compiler's default, which changes between versions. Pin it. |
| `-Wall` | Turns on a large set of warnings. | The name means "all", and it is a lie — but it is still the single highest-value flag. |
| `-Wextra` | Turns on the ones `-Wall` left out. | Catches unused parameters, suspicious comparisons, and similar. |
| `-Werror` | Promotes every warning to an error. | Turns "I'll look at that later" into "you cannot build this until you fix it". |
| `-g` | Keeps debug information. | Required for a debugger to show you variable names and line numbers. |
| `-O2` | Optimises. | For release builds. **Do not debug optimised code** — the compiler rearranges it, and your breakpoints land in strange places. |
| `-fsanitize=address,undefined` | Instruments the program to catch memory and UB errors at runtime. | The subject of a section below. |

For learning, this is the line to use:

```bash
clang++ -std=c++17 -Wall -Wextra -Werror -g -o prog prog.cpp
```

## Reading an error message

Here is a program with a missing semicolon. Compile it and the compiler tells you exactly where and
exactly what:

```cpp bad
#include <iostream>

int main() {
    int x = 5
    std::cout << x << "\n";
    return 0;
}
```

The real diagnostic is:

```text
missingsemi.cpp:4:14: error: expected ';' at end of declaration
    4 |     int x = 5
      |              ^
      |              ;
1 error generated.
```

Read it in four pieces:

1. `missingsemi.cpp:4:14` — file, **line 4, column 14**. The `:` separators are file, line, column.
2. `error:` — the severity. `warning:` means it built; `error:` means it did not.
3. `expected ';' at end of declaration` — what the compiler wanted.
4. The caret and the `;` underneath — a picture of the fix, printed at the position it belongs.

A second, more interesting example. This one has a typo, and the compiler guesses what you meant:

```cpp bad
#include <iostream>

int main() {
    int count = 3;
    std::cout << cont << "\n";
    return 0;
}
```

```text
typo.cpp:5:18: error: use of undeclared identifier 'cont'; did you mean 'count'?
    5 |     std::cout << cont << "\n";
      |                  ^~~~
      |                  count
typo.cpp:4:9: note: 'count' declared here
    4 |     int count = 3;
      |         ^
1 error generated.
```

Two things to take from this. First, `note:` lines are part of the same report — the compiler is
telling you where the name it thinks you meant was declared. Second, the *first* error is usually
the only one worth reading: one missing `}` can produce two hundred follow-on errors, and fixing the
first often clears all of them. Scroll to the top, fix, rebuild, repeat.

:::pitfall Fixing errors from the bottom up
A single stray brace or a missing semicolon at the top of a file can generate a wall of errors on
every line after it. If you start at the bottom you will "fix" code that was never broken, and
introduce real bugs while doing it. **Always start at the first error.** Rebuild after each fix
rather than working through the whole list — most of the list is usually one mistake wearing many
hats.
:::

## Make the compiler strict, on purpose

Warnings are things the compiler noticed but was not required to stop for. Here is a variable that
is assigned and never used:

```bash
clang++ -std=c++17 -Wall -Wextra unused.cpp -o unused
```

```text
unused.cpp:4:9: warning: unused variable 'unused' [-Wunused-variable]
    4 |     int unused = 42;
      |         ^~~~~~
1 warning generated.
```

The build succeeded. Add `-Werror` and the same message becomes fatal:

```text
    4 |     int unused = 42;
      |         ^~~~~~
1 error generated.
```

That is the entire point of `-Werror`: it removes your ability to ignore the compiler. An unused
variable is harmless. An unused variable *of a type with a constructor that does something* is not,
and the compiler has no way to tell you which you have. Getting into the habit of a warning-free
build means the one warning that matters never gets lost in the noise of fifty that do not.

The `[-Wunused-variable]` in brackets is the warning's name. That matters: when you meet a warning
you disagree with, you can silence exactly that one with `-Wno-unused-variable` instead of turning
off `-Wall` and losing everything else. Silence the specific, never the general.

## Sanitizers: for the mistakes that compile

The compiler checks that your program is *well-formed*. It cannot check that it is *correct* —
whether the memory you are reading is memory you own. That is what sanitizers are for. They are a
second compiler mode that inserts checks around memory accesses and arithmetic, then reports
violations at runtime.

Here is a program that compiles cleanly under `-Wall -Wextra -Werror`, prints a number, and is
broken:

```cpp run-san-catch
#include <iostream>

int main() {
    int *numbers = new int[3];
    numbers[7] = 1;
    std::cout << numbers[7] << "\n";
    delete[] numbers;
    return 0;
}
```

```text
heap-buffer-overflow
```

Build it with the sanitizer and the same program refuses to lie to you:

```bash
clang++ -std=c++17 -Wall -Wextra -g -fsanitize=address,undefined -o prog prog.cpp
./prog
```

You get a report naming the exact line, the size of the allocation (`3` ints) and the size of the
access, plus the stack trace that led there. `AddressSanitizer` catches buffer overflows, reads and
writes after `free`, and double frees. `UndefinedBehaviorSanitizer`, switched on by the same flag,
catches signed integer overflow, null dereferences and out-of-range shifts.

Add these two flags to every build while you are learning. The cost is roughly a factor of two in
speed, and the benefit is that the bug you would otherwise spend three hours on tells you its own
line number.

:::warning Leak detection is not available everywhere
`AddressSanitizer` can also report memory you allocated and never freed. That part is **not
available on macOS** — Apple's clang ships no LeakSanitizer, and asking for it is ignored. So a
leaking program can exit cleanly here. If you want leak checking on a Mac, install `valgrind` or
run the same build on Linux. Chapter 11 covers leaks properly, and says which tool catches them on
which platform.
:::

## make: stop retyping the command

The command is long and you will type it hundreds of times. `make` reads a file called `Makefile`
and runs the recipe you name.

```makefile
CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -g

hello: hello.cpp
	$(CXX) $(CXXFLAGS) -o hello hello.cpp

clean:
	rm -f hello
```

The indentation before `$(CXX)` **must be a tab**, not spaces. This is the single most common
Makefile error and the message (`missing separator`) does not mention tabs.

Now `make` builds, and `make clean` tidies up. Make also earns its keep through *incremental*
builds: it compares timestamps and only rebuilds what changed. On a one-file project that is
invisible; on the 40-file project in Chapter 22 it is the difference between a two-second and a
two-minute edit-build-test loop.

## The debugger, briefly

Printing things is a fine debugging technique and you should not apologise for it. But when you need
to know *why* a value is wrong, a debugger answers questions printing cannot: what is in this
variable at this moment, and how did execution get here.

```bash
clang++ -std=c++17 -g -O0 -o prog prog.cpp
lldb ./prog          # or: gdb ./prog
```

Inside, the four commands that carry most of the weight:

```text
break main      stop when main is reached
run             start the program
next            step over the current line
print x         show the value of x
```

`-O0` means "do not optimise". Debugging optimised code is possible and miserable: variables get
reused, lines get reordered, and the value you ask for may not exist any more. Compile with `-g
-O0` when debugging, `-O2` when shipping.

:::scenario A build that works on your machine and fails in CI
You push a change. It builds locally. CI fails with `undefined reference to 'parse_config()'`. You
re-read your code — the function is right there, spelled correctly, and your local build is clean.

The temptation is to blame CI. The useful move is to read the linker's complaint literally: the
linker does not know about source files, only about object files and libraries it has been *given*.
If `parse_config` lives in `config.cpp` and you have been building with `clang++ -o app main.cpp`
locally, your local build should have failed too. It did not, which means the two builds are not
compiling the same set of files.

:::solution Find the difference in inputs before touching the code
Compare the two command lines rather than the two outputs. In practice this is almost always one of
three things: the new file is not listed in the build (a `Makefile`, a `CMakeLists.txt`, or a CI
script), it is listed but with a typo, or it is listed in the local build and not the CI one. Here
the fix is one line in the `Makefile`:

```makefile
CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -g

app: main.cpp config.cpp
	$(CXX) $(CXXFLAGS) -o app main.cpp config.cpp
```

The general lesson: **a linker error is a statement about your build's inputs, not about your
source.** Once you believe that, the fix is usually a one-line diff in a build file.
:::

## Key takeaways

- "Compiler" is four stages; a message naming a line of your code is the compiler, and
  `undefined reference` is the linker saying it was never given the body.
- `-o name` controls the output filename; without it you get `a.out`.
- Use `-std=c++17 -Wall -Wextra -Werror -g` while learning, and add
  `-fsanitize=address,undefined` to catch what compiles but is still wrong.
- Read a diagnostic as file, line, column, severity, message — then read the `note:` lines.
- Fix the **first** error and rebuild; a single mistake often produces a hundred messages.
- Silence a specific warning with `-Wno-name`, never by dropping `-Wall`.
- `make` compares timestamps, so it only rebuilds what changed; the recipe line must start with a
  tab.
- Debug with `-g -O0`; ship with `-O2`.

## Practice

- [ ] Build and run the `hello.cpp` above, then delete the `#include <iostream>` line and read the
      error. Put it back.
- [ ] Compile it without `-o` and confirm you get `a.out`, then run it.
- [ ] Remove a semicolon on purpose and compare your error to the one quoted in this chapter. Then
      add a `}` at the end of the file and notice how many extra errors appear.
- [ ] Take the `-Wall -Wextra unused.cpp` example, build it with and without `-Werror`, and confirm
      the warning becomes fatal.
- [ ] Write the `Makefile` for `hello.cpp`, run `make`, then `make clean`. Confirm the recipe line
      breaks if you replace its tab with spaces, and read the message you get.
- [ ] Write a program that allocates an array of 3 and writes to index 5. Build it once with the
      sanitizer and once without, and run both. Write down what each does.

## Solutions

:::solution Exercise 1
Deleting the include gives:

```text
hello.cpp:3:5: error: use of undeclared identifier 'std'
```

`std::cout` is declared in `<iostream>`. Remove the include and the name `std::cout` no longer
exists. This is the preprocessor stage's whole job: `#include <iostream>` pastes the contents of
that file in at that point, and with nothing pasted in, the compiler has never heard of `std`.
:::

:::solution Exercise 3
One missing semicolon produces one error. Now add an extra `}` at the end of the file:

```cpp bad
#include <iostream>

int main() {
    int x = 5
    std::cout << x << "\n";
    return 0;
}
}
```

```text
error: expected ';' at end of declaration
```

The extra brace turns one error into several, and the later ones point at code that is perfectly
correct. This is why you fix from the top: after repairing the semicolon the trailing-brace error
becomes the only one, and it is then obvious.
:::

:::solution Exercise 6
Writing past the end of an allocation. The unsanitized build first — it compiles clean:

```cpp compile
#include <iostream>

int main() {
    int *numbers = new int[3];
    numbers[5] = 99;
    std::cout << "wrote and read " << numbers[5] << "\n";
    delete[] numbers;
    return 0;
}
```

`-Wall -Wextra -Werror` accepts it without a murmur, because the compiler has no idea how long the
allocation is — `new int[3]` hands back a bare `int *`, and the `3` is gone by the time the subscript
is checked. Run it and, on this machine, it dies with a segmentation fault: **exit code 139, every
single time.**

Now change the `5` to a `3` — one element past the end instead of two — and it prints
`wrote and read 99` and exits **0**. Same bug, two utterly different outcomes. Neither is a promise:
that is what "undefined behaviour" means, and it is why "it worked when I ran it" is not evidence.

With the sanitizer, the ambiguity disappears:

```cpp run-san-catch
#include <iostream>

int main() {
    int *numbers = new int[3];
    numbers[5] = 99;
    std::cout << "wrote and read " << numbers[5] << "\n";
    delete[] numbers;
    return 0;
}
```

```text
heap-buffer-overflow
```

The report names the line, tells you the allocation was 12 bytes and the write was 4 bytes past its
end, and shows the call stack. That is the argument for the flag in one paragraph: without it, a
program that is definitely broken either lies to you or dies somewhere unhelpful, and you have no way
to tell which bug you have.
:::
