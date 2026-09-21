---
chapter: 9
part: 1
title: The Compile Pipeline, Linking and Build Systems
summary: Follow a source file through preprocessing, compilation, assembly and linking, read a symbol table, tell a link error from a compile error, and drive the whole thing with make.
minutes: 75
tags: [compiler, linker, preprocessor, object-files, symbols, make, makefile, static-library, cmake, flags]
---

You have been typing a compiler command and getting a working program out, which is a small miracle
you have so far taken on trust. This chapter takes the trust away and replaces it with a model. Once
you know that one command is really four stages, several classes of error stop being mysterious: the
difference between "does not compile" and "does not link", why editing a header sometimes does
nothing, why a declaration is enough for the compiler and not enough for the program, and what a
build system is actually doing when it decides to rebuild something.

## Four stages, not one command

A compiler driver is a program that runs other programs. `clang++ main.cpp -o prog` runs four
distinct stages, and you can stop it after any of them:

| Stage | What it does | Flag to stop there | Output |
|---|---|---|---|
| Preprocess | expands `#include`, `#define` and `#if` | `-E` | text |
| Compile | turns C++ into assembly for the target | `-S` | `.s` |
| Assemble | turns assembly into machine code | `-c` | `.o` |
| Link | joins objects and libraries into a program | (default) | executable |

The first stage is the one people find most surprising, because it is pure text manipulation and it
happens before any C++ is understood. A macro is not a function and a `#include` is not an import;
both are string operations that run first.

```sh run
cat > config.h <<'EOF'
#ifndef CONFIG_H
#define CONFIG_H

#define MAX_ITEMS 3
#define SQUARE(x) ((x) * (x))

#endif
EOF
cat > expand.cpp <<'EOF'
#include "config.h"

int value = SQUARE(MAX_ITEMS);
EOF
echo '$ clang++ -E -P expand.cpp'
clang++ -E -P expand.cpp
```

```text
$ clang++ -E -P expand.cpp

int value = ((3) * (3));
```

That is the entire preprocessor. `#include "config.h"` pasted the header's text in, `#ifndef` and
`#define` did nothing visible, and `SQUARE(MAX_ITEMS)` was replaced by `((3) * (3))` — not by a call
to anything, just by text. The parentheses around the parameter in the macro body are load-bearing:
without them `SQUARE(a + b)` would expand to `a + b * a + b`, which is a different number.

Note the blank first line: the header's own leading newline came along with it. That is what "the
preprocessor is textual" means in practice.

## Translation units, objects and symbols

The unit of compilation is the **translation unit**: one `.cpp` file after preprocessing, with all
its headers pasted in. Each becomes one object file. Here is a two-file program, the way it is
normally laid out — a header for the declarations, a source for the definitions, and a `main` that
uses them.

```cpp make-files
/* ===== config.h ===== */
#ifndef CONFIG_H
#define CONFIG_H

#define MAX_ITEMS 3
#define SQUARE(x) ((x) * (x))

int clamp_to_max(int value);

#endif
/* ===== config.cpp ===== */
#include "config.h"

int clamp_to_max(int value) {
    if (value > MAX_ITEMS) {
        return MAX_ITEMS;
    }
    return value;
}
/* ===== main.cpp ===== */
#include <cstdio>

#include "config.h"

int main() {
    std::printf("clamped 1 -> %d\n", clamp_to_max(1));
    std::printf("clamped 5 -> %d\n", clamp_to_max(5));
    std::printf("SQUARE(MAX_ITEMS) = %d\n", SQUARE(MAX_ITEMS));
    return 0;
}
/* ===== Makefile ===== */
CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

OBJECTS  = main.o config.o

prog: $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJECTS)

main.o: main.cpp config.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

config.o: config.cpp config.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f prog *.o

.PHONY: clean
/* ===== Makefile.nodep ===== */
CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

OBJECTS  = main.o config.o

prog: $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJECTS)

main.o: main.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

config.o: config.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f prog *.o

.PHONY: clean
```

```text
clamped 1 -> 1
clamped 5 -> 3
SQUARE(MAX_ITEMS) = 9
```

Now watch the stages happen one at a time, by hand, without `make` in the way:

```sh run-project
echo '$ clang++ -c -std=c++17 config.cpp -o config.o'
clang++ -c -std=c++17 config.cpp -o config.o
echo '$ clang++ -c -std=c++17 main.cpp -o main.o'
clang++ -c -std=c++17 main.cpp -o main.o
echo '$ ls *.o'
ls *.o
echo '$ nm -g config.o | c++filt'
nm -g config.o | c++filt
echo '$ nm -g main.o | c++filt'
nm -g main.o | c++filt
echo '$ clang++ -o prog main.o config.o'
clang++ -o prog main.o config.o
echo '$ ./prog'
./prog
```

```text
$ clang++ -c -std=c++17 config.cpp -o config.o
$ clang++ -c -std=c++17 main.cpp -o main.o
$ ls *.o
config.o
main.o
$ nm -g config.o | c++filt
0000000000000000 T clamp_to_max(int)
$ nm -g main.o | c++filt
                 U clamp_to_max(int)
0000000000000000 T _main
                 U _printf
$ clang++ -o prog main.o config.o
$ ./prog
clamped 1 -> 1
clamped 5 -> 3
SQUARE(MAX_ITEMS) = 9
```

Three things are worth stopping on. `clang++ -c` produced an object file and did **not** produce a
program — an object file is machine code with holes in it. The `nm` output is the symbol table:
`T` marks a symbol the object *defines*, and `U` marks one it *needs and does not have*. And the
mangled name is not a mistake. The compiler encodes the parameter types into the symbol, which is
how two functions with the same name and different parameters can coexist — and it is also why a C
library has to be declared `extern "C"` before C++ can call it, so the name is left alone.

`main.o` has `U clamp_to_max(int)` and `config.o` has `T clamp_to_max(int)`. Nothing has run yet.
The linker's job is to match every `U` with a `T`, and the program exists only when it has.

## Build systems: make

Typing four commands per file does not scale, and neither does recompiling everything after a
one-line edit. `make` solves both: you describe the *dependency graph* and the command for each
edge, and it works out what is out of date.

```sh run-project
echo '$ make clean'
make clean
echo '$ make'
make
echo '$ ./prog'
./prog
sleep 1
echo '$ touch config.h && make'
touch config.h && make
echo '$ make clean > /dev/null && make -f Makefile.nodep'
make clean > /dev/null && make -f Makefile.nodep
sleep 1
echo '$ touch config.h && make -f Makefile.nodep'
touch config.h && make -f Makefile.nodep
```

```text
$ make clean
rm -f prog *.o
$ make
clang++ -std=c++17 -Wall -Wextra -Werror -c main.cpp -o main.o
clang++ -std=c++17 -Wall -Wextra -Werror -c config.cpp -o config.o
clang++ -std=c++17 -Wall -Wextra -Werror -o prog main.o config.o
$ ./prog
clamped 1 -> 1
clamped 5 -> 3
SQUARE(MAX_ITEMS) = 9
$ touch config.h && make
clang++ -std=c++17 -Wall -Wextra -Werror -c main.cpp -o main.o
clang++ -std=c++17 -Wall -Wextra -Werror -c config.cpp -o config.o
clang++ -std=c++17 -Wall -Wextra -Werror -o prog main.o config.o
$ make clean > /dev/null && make -f Makefile.nodep
clang++ -std=c++17 -Wall -Wextra -Werror -c main.cpp -o main.o
clang++ -std=c++17 -Wall -Wextra -Werror -c config.cpp -o config.o
clang++ -std=c++17 -Wall -Wextra -Werror -o prog main.o config.o
$ touch config.h && make -f Makefile.nodep
make: `prog' is up to date.
```

The transcript is the lesson, so read it in order. `make` compiled both sources and linked. Then
`touch config.h` — which changes nothing about the program — and `make` rebuilt **both** object
files and relinked, because both objects list `config.h` as a prerequisite. That is the whole point
of a build system: it is not a list of commands, it is a graph.

The second half runs the same experiment against `Makefile.nodep`, which is identical except that
the header is not listed as a prerequisite. After `touch config.h`, `make` reports the target is up
to date and rebuilds nothing. Nothing is wrong with the program yet — it just runs yesterday's
machine code while you look at today's header, and the symptoms are baffling precisely because the
source on screen does not match the binary in memory.

:::pitfall The header you forgot to list as a prerequisite
That stale rebuild is the single most common Makefile bug, and the reason it is dangerous is that
it produces no error. You edit a struct in a header, rebuild, run, and see the old behaviour. You
re-read the header, doubt your own edit, and rebuild again — still the old behaviour, because the
object file is newer than the header and `make` is being perfectly consistent.

The measured transcript above is the evidence: same files, same `touch`, two Makefiles, two
different outcomes. `Makefile.nodep` is not broken; it is a correct description of a graph that is
missing an edge.

Two ways to avoid it. List the header in every object's prerequisites, which is what the real
`Makefile` does, and which is exactly what `g++ -MM` exists to generate for you. Or let the compiler
do it: `-MMD -MP` writes a `.d` file per object listing the headers it actually read, and a
`-include $(OBJECTS:.o=.d)` line pulls them in. The second scales to a project with fifty headers;
the first is fine while you can still count them.
:::

## A link error is a different species

Because the compiler and the linker are separate programs with separate jobs, they fail differently,
and the distinction tells you where to look. The compiler knows about syntax and types. The linker
knows about names and addresses, and it never sees your types at all.

:::scenario The code that compiled and then would not build
A developer splits a growing file in two, moving a helper into its own source file and declaring it
in a header. They check their work the fast way — compile the one file they edited — and the
compiler reports nothing wrong. So they hand it to a colleague, whose build fails with a message
about symbols rather than about code.

The compiler was right both times. A declaration is a promise that a definition exists *somewhere*,
and the compiler cannot check that promise; only the linker can, and only when it has been given
every object file.

```cpp bad
#include <cstdio>

/* Declared, never defined in this translation unit. */
const char *greeting();

int main() {
    std::printf("%s\n", greeting());
    return 0;
}
```

```text
Undefined symbols for architecture arm64:
```

Read the message carefully, because it says exactly what is missing and who wants it. It is not
about the syntax of `greeting()` — that line is fine. It is that no translation unit in the link
supplied a body for it.

:::solution Compile every source file and link them together
The fix is to put the definition in a translation unit and pass that unit to the linker:

```cpp run-files
/* ===== greet.h ===== */
#ifndef GREET_H
#define GREET_H

const char *greeting();

#endif
/* ===== greet.cpp ===== */
#include "greet.h"

const char *greeting() {
    return "linked, not merely compiled";
}
/* ===== main.cpp ===== */
#include <cstdio>

#include "greet.h"

int main() {
    std::printf("%s\n", greeting());
    return 0;
}
```

```text
linked, not merely compiled
```

Three files, one link command. The header is included by both `.cpp` files, which is what keeps the
declaration and the definition in agreement — if the signature in `greet.h` and the one in
`greet.cpp` ever drift apart, the linker reports an undefined symbol for the header's version, and
that error is the compiler telling you the two files disagree.

A useful habit falls out of this: when a link error appears, the question is never "what is wrong
with this line", it is "which translation unit was supposed to define this, and did I actually give
it to the linker". Most often the answer is that a new `.cpp` file was created and never added to
the build.
:::
:::

## What the flags do

Flags are not incantations. Each one names a stage or a decision within a stage.

`-D` defines a macro before the first line of the file, which is how one source can be built several
ways without being edited:

```sh run
cat > greet.cpp <<'EOF'
#include <cstdio>

int main() {
#ifdef VERBOSE
    std::printf("verbose: hello\n");
#else
    std::printf("hello\n");
#endif
    return 0;
}
EOF
echo '$ clang++ -std=c++17 -o greet greet.cpp && ./greet'
clang++ -std=c++17 -o greet greet.cpp && ./greet
echo '$ clang++ -std=c++17 -DVERBOSE -o greet greet.cpp && ./greet'
clang++ -std=c++17 -DVERBOSE -o greet greet.cpp && ./greet
```

```text
$ clang++ -std=c++17 -o greet greet.cpp && ./greet
hello
$ clang++ -std=c++17 -DVERBOSE -o greet greet.cpp && ./greet
verbose: hello
```

The same source, compiled twice, with different behaviour, and the difference is entirely in the
preprocessor. This is how feature flags, debug logging and platform branches are usually built. It
is also a habit worth being suspicious of: code that changes shape depending on how it was compiled
is code that cannot be tested in all its shapes at once, and the configuration nobody builds is the
configuration that rots.

The rest of the flags worth knowing fall into four groups:

- **Which language and dialect.** `-std=c++17` sets the standard. This book uses C++17 as its floor
  and says so whenever a feature needs more.
- **How loud the compiler is.** `-Wall -Wextra` turn on the useful diagnostics; `-Werror` makes them
  fatal. Every block in this book is compiled with all three, which is why a warning you would
  otherwise scroll past becomes a build failure here.
- **What to optimise for.** `-O0` is the default and the fastest to compile; `-O2` is the usual
  release setting; `-g` adds debug information. They are independent — `-O2 -g` is a legitimate
  release-with-symbols build, and shipping `-g` is how you get usable crash reports.
- **Where to look for things.** `-I` adds a directory to the include search path, `-L` adds one to
  the library search path, and `-l` names a library to link. `-I` is the one you will need first:

```sh run
mkdir -p include
cat > include/units.h <<'EOF'
#ifndef UNITS_H
#define UNITS_H

int metres_to_centimetres(int metres);

#endif
EOF
cat > units.cpp <<'EOF'
#include "units.h"

int metres_to_centimetres(int metres) {
    return metres * 100;
}
EOF
cat > report.cpp <<'EOF'
#include <cstdio>

#include "units.h"

int main() {
    std::printf("%d\n", metres_to_centimetres(3));
    return 0;
}
EOF
echo '$ clang++ -c -std=c++17 report.cpp'
clang++ -c -std=c++17 report.cpp 2>&1 | head -1
echo '$ clang++ -c -std=c++17 -Iinclude report.cpp'
clang++ -c -std=c++17 -Iinclude report.cpp
echo '$ clang++ -c -std=c++17 -Iinclude units.cpp'
clang++ -c -std=c++17 -Iinclude units.cpp
echo '$ clang++ -o prog report.o units.o'
clang++ -o prog report.o units.o
echo '$ ./prog'
./prog
```

```text
$ clang++ -c -std=c++17 report.cpp
report.cpp:3:10: fatal error: 'units.h' file not found
$ clang++ -c -std=c++17 -Iinclude report.cpp
$ clang++ -c -std=c++17 -Iinclude units.cpp
$ clang++ -o prog report.o units.o
$ ./prog
300
```

The first compile fails and the second succeeds, with one extra flag. Note that `units.cpp` also
needs `-Iinclude` — it includes its own header the same way, so the flag belongs in the build for
every translation unit, which is why a Makefile normally carries one variable holding all the `-I`
paths and applies it to every rule.

That is also the whole difference between the two include forms. `#include "units.h"` searches the
directory of the including file first and then the `-I` directories; `#include <units.h>` skips the
local directory entirely. A project's own headers are quoted, the standard library's are bracketed,
and the reason is exactly this search order.

Get the path wrong and the compiler stops before it has read any C++ at all:

```cpp bad
#include "nope.h"

int main() {
    return 0;
}
```

```text
'nope.h' file not found
```

`fatal error` rather than plain `error` is the compiler saying it could not get far enough to compile
anything. Nothing about your code has been examined, so there is no point reading the line it points
at — the problem is in the build configuration, and the fix is a flag or a moved file rather than an
edit.

### Libraries, static and dynamic

A library is a bundle of object files. A **static** library (`.a` on Unix, `.lib` on Windows) is
literally that bundle, and the linker copies in the object files it needs. A **dynamic** or
**shared** library (`.so`, `.dylib`, `.dll`) is loaded at run time, and the executable keeps only a
reference to it.

The trade-off is the usual one. Static linking makes a bigger executable that has no dependencies
and cannot be broken by a library update. Dynamic linking shares one copy between programs and lets
you fix a library without rebuilding everything that uses it — at the cost of a program that may not
start because a file it never mentioned is missing or is the wrong version.

### Assertions, and what a "debug build" actually means

`assert` is a check that exists only in a debug build. It is not a general error-handling tool — it
is a statement about what must be true, and it vanishes entirely when `NDEBUG` is defined:

```cpp run-abort
#include <cassert>
#include <cstdio>

int main() {
    int value = 1;

    assert(value == 2);
    std::printf("not reached\n");
    return 0;
}
```

```text
Assertion failed: (value == 2), function main
```

The message goes to stderr, the exit code is 134, and the program stops at the line that failed
rather than continuing with a wrong value. Compile the same file with `NDEBUG` defined and the check
is not there at all:

```cpp run
#define NDEBUG
#include <cassert>
#include <cstdio>

int main() {
    int value = 1;

    assert(value == 2);
    std::printf("value = %d, and the assert did nothing\n", value);
    return 0;
}
```

```text
value = 1, and the assert did nothing
```

Nothing between those two blocks changed except a macro. This is why release builds are normally
compiled with `-DNDEBUG`, and it is why an assert must never have a side effect: `assert(consume())`
does its work in a debug build and silently does nothing in a release one, so the two builds behave
differently. An assert may check a condition, never change the program's state.

## CMake, and why this book starts with make

`make` is thirty years old, has no notion of what a compiler is, and is available everywhere. That
last property is why it is worth understanding: whatever else a project uses, something underneath
it is probably running `make`.

For anything larger than a handful of files, though, most C++ projects use **CMake**, which
generates the Makefiles (or Ninja files, or an Xcode project) from a higher-level description:

```cmake
cmake_minimum_required(VERSION 3.16)
project(units CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(prog report.cpp units.cpp)
target_include_directories(prog PRIVATE include)
```

That describes the same program with no compiler flags spelled out, and CMake supplies the right
ones per platform. The reason it wins on real projects is that it knows about compilers, so
`-std=c++17` becomes the correct spelling for whichever compiler it finds.

**This chapter does not verify the CMake listing, and you should not treat it as tested.** `cmake`
is not installed on the machine this book was built on, and a build file that has never been run is
a claim rather than a fact — the same standard the rest of this book holds its code to. Learn `make`
here, where every recipe is executed before it is printed, and pick up CMake when you have a project
big enough to need it and a machine that can run it.

## Key takeaways

- One compiler command is four stages: preprocess, compile, assemble, link. `-E`, `-S` and `-c` stop
  after the first three.
- The preprocessor is textual. `#include` pastes text and `#define` substitutes text, before any C++
  is understood.
- Parenthesise every parameter in a function-like macro. `#define SQUARE(x) ((x) * (x))` is the
  minimum, and it still evaluates its argument twice.
- A translation unit is one source file after preprocessing. Each becomes one object file.
- A declaration is a promise; a definition is the fulfilment. The compiler checks the promise, the
  linker checks the fulfilment, and only the linker can fail to find it.
- A link error says `Undefined symbols`. A compile error names a file, a line and a column. The
  shape of the message tells you which stage to look at.
- `nm` shows a symbol table: `T` is defined in this object, `U` is needed and missing. C++ mangles
  names to encode parameter types, which is why `extern "C"` is needed to call C.
- A Makefile is a dependency graph, not a list of commands. A header that is not a prerequisite
  produces a stale binary and no error at all.
- `-D` defines a macro from the command line, so one source can be built several ways.
- `-Wall -Wextra -Werror` is the setting this book uses everywhere. `-g` and `-O2` are independent
  choices, not opposites.
- `assert` is a debug-only check. Defining `NDEBUG` removes it from the build entirely, which is why
  an assert must never have a side effect.
- `-I` adds an include directory, `-L` a library directory, `-l` a library. The convention is objects
  first and libraries after them; GNU `ld` requires that order, and Apple's linker happens to accept
  either.
- A static library is copied into the executable; a shared library is resolved at run time.

## Practice

- [ ] Split a program into two translation units and a header, and link them. Then delete one
      definition and read the link error.
- [ ] Compile one source file three times with different `-D` values and show the behaviour change.
- [ ] Build a static library with `ar` and link a program against it using `-L` and `-l`.
- [ ] Show a function-like macro evaluating its argument twice, then fix it with a function.

## Solutions

:::solution Exercise 1
A header for the declarations, one source for the definitions, one for `main`, and a single link
command that names both objects.

```cpp run-files
/* ===== stats.h ===== */
#ifndef STATS_H
#define STATS_H

#include <cstddef>

int sum(const int *values, std::size_t count);
int maximum(const int *values, std::size_t count);

#endif
/* ===== stats.cpp ===== */
#include "stats.h"

int sum(const int *values, std::size_t count) {
    int total = 0;

    for (std::size_t i = 0; i < count; ++i) {
        total += values[i];
    }
    return total;
}

int maximum(const int *values, std::size_t count) {
    int best = values[0];

    for (std::size_t i = 1; i < count; ++i) {
        if (values[i] > best) {
            best = values[i];
        }
    }
    return best;
}
/* ===== main.cpp ===== */
#include <cstdio>

#include "stats.h"

int main() {
    const int readings[5] = {4, 9, 2, 7, 5};
    const std::size_t count = sizeof(readings) / sizeof(readings[0]);

    std::printf("sum     = %d\n", sum(readings, count));
    std::printf("maximum = %d\n", maximum(readings, count));
    return 0;
}
```

```text
sum     = 27
maximum = 9
```

Delete `stats.cpp` from the command and the error changes species: `Undefined symbols for
architecture arm64: "sum(int const*, unsigned long)", referenced from _main`. Two functions are
missing, and both are named with their parameter types — the mangling from earlier in the chapter,
doing its job of keeping overloads apart. This is also why the fix is never to add a declaration:
one is already there, and that is exactly what let the compiler succeed.
:::

:::solution Exercise 2
`#ifndef` gives the macro a default so the file still compiles without any flag, and `#if` chooses
between the branches.

```sh run
cat > level.cpp <<'EOF'
#include <cstdio>

#ifndef LEVEL
#define LEVEL 1
#endif

int main() {
#if LEVEL >= 2
    std::printf("level %d: detailed\n", LEVEL);
#else
    std::printf("level %d: quiet\n", LEVEL);
#endif
    return 0;
}
EOF
echo '$ clang++ -std=c++17 -o level level.cpp && ./level'
clang++ -std=c++17 -o level level.cpp && ./level
echo '$ clang++ -std=c++17 -DLEVEL=2 -o level level.cpp && ./level'
clang++ -std=c++17 -DLEVEL=2 -o level level.cpp && ./level
echo '$ clang++ -std=c++17 -DLEVEL=9 -o level level.cpp && ./level'
clang++ -std=c++17 -DLEVEL=9 -o level level.cpp && ./level
```

```text
$ clang++ -std=c++17 -o level level.cpp && ./level
level 1: quiet
$ clang++ -std=c++17 -DLEVEL=2 -o level level.cpp && ./level
level 2: detailed
$ clang++ -std=c++17 -DLEVEL=9 -o level level.cpp && ./level
level 9: detailed
```

`-DLEVEL=9` takes the same branch as `-DLEVEL=2`, because the condition is `LEVEL >= 2` and not an
equality. That is the usual shape for a log level: the comparison is ordered, so raising the level
enables everything below it. The `#ifndef` block matters more than it looks — without it, building
the file with no `-D` at all would leave `LEVEL` undefined, and `#if LEVEL >= 2` would silently
evaluate the undefined identifier as `0` rather than failing. A macro that must have a value should
either be defaulted here or checked with `#ifndef` and an `#error`.
:::

:::solution Exercise 3
`ar` packs object files into an archive, and `-L` plus `-l` tell the linker where to find it and
what it is called.

```sh run
mkdir -p include
cat > include/units.h <<'EOF'
#ifndef UNITS_H
#define UNITS_H

int metres_to_centimetres(int metres);

#endif
EOF
cat > units.cpp <<'EOF'
#include "units.h"

int metres_to_centimetres(int metres) {
    return metres * 100;
}
EOF
cat > report.cpp <<'EOF'
#include <cstdio>

#include "units.h"

int main() {
    std::printf("%d\n", metres_to_centimetres(3));
    return 0;
}
EOF
echo '$ clang++ -c -std=c++17 -Iinclude units.cpp'
clang++ -c -std=c++17 -Iinclude units.cpp
echo '$ ar rcs libunits.a units.o'
ar rcs libunits.a units.o
echo '$ clang++ -c -std=c++17 -Iinclude report.cpp'
clang++ -c -std=c++17 -Iinclude report.cpp
echo '$ clang++ -o prog -L. -lunits report.o'
clang++ -o prog -L. -lunits report.o 2>&1 | head -1
echo '$ clang++ -o prog report.o -L. -lunits'
clang++ -o prog report.o -L. -lunits
echo '$ ./prog'
./prog
```

```text
$ clang++ -c -std=c++17 -Iinclude units.cpp
$ ar rcs libunits.a units.o
$ clang++ -c -std=c++17 -Iinclude report.cpp
$ clang++ -o prog -L. -lunits report.o
$ clang++ -o prog report.o -L. -lunits
$ ./prog
300
```

Two details in that script are worth naming. `ar rcs` means *replace, create, write a symbol index*
— that last letter is the one that matters, because without an index the linker cannot look anything
up in the archive. And `-lunits` does not name a file: the linker expands it to `libunits.a` by
adding the `lib` prefix and the `.a` suffix, which is why the archive had to be named that way in the
first place.

The script also links the same program in the other order — `-lunits` before `report.o` — and here
is the part worth being careful about. **Both orders linked successfully on the machine this book
was built on.** The rule you will read everywhere is that the linker resolves left to right and an
archive only satisfies symbols that are already needed, so objects must come first; that rule is
real and GNU `ld` on Linux enforces it, which is where the familiar `undefined reference` errors come
from. Apple's linker, which is what ran above, was more forgiving. So treat the ordering rule as
advice worth following unconditionally rather than as something this chapter has demonstrated — the
command that fails on your Linux CI is the first one, and nothing in this transcript warns you.
:::

:::solution Exercise 4
The macro is textual, so the argument is pasted in wherever the parameter appears — twice.

```cpp run
#include <cstdio>

#define SQUARE(x) ((x) * (x))

static int calls = 0;

static int next(void) {
    ++calls;
    return 3;
}

int main() {
    std::printf("result = %d\n", SQUARE(next()));
    std::printf("calls  = %d\n", calls);
    return 0;
}
```

```text
result = 9
calls  = 2
```

`SQUARE(next())` became `((next()) * (next()))`, so `next` ran twice and the counter is 2. The
result is still 9 because `next` returns 3 both times, which is exactly what makes this bug survive
testing: the answer looks right and only the side effect is wrong. In a real program `next` might be
reading a stream, incrementing a cursor or popping a queue, and the second call silently consumes
something.

Wrapping the argument in parentheses — the usual piece of macro advice — does not help here. It
fixes precedence, not evaluation count. The fix is to stop using a macro for something that has
semantics:

```cpp run
#include <cstdio>

static int calls = 0;

static int next(void) {
    ++calls;
    return 3;
}

static int square(int value) {
    return value * value;
}

int main() {
    std::printf("result = %d\n", square(next()));
    std::printf("calls  = %d\n", calls);
    return 0;
}
```

```text
result = 9
calls  = 1
```

One call, one increment. A function evaluates its argument once because that is what a function
call means. The cost is that a function is a real call rather than inline text — and an `inline`
function in a header gives you the inlining back without the double evaluation, which is why
function-like macros in modern C++ are rare and usually wrong. We come back to this in Chapter 15,
where the preprocessor gets the full treatment.
:::
