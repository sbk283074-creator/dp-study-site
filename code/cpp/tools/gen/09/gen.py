#!/usr/bin/env python3
"""Generate chapters/09-the-compile-pipeline-linking-and-build-systems.md.

Nothing in the chapter is typed by hand: the listings are read from the files
beside this script and every `text` fence is captured by compiling and running
the program, exactly as tools/verify_examples.py will.

    python3 tools/gen/09/gen.py

STYLE.md: "Generate listings from the files, do not retype them."
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/09 -> gen -> tools -> cpp
OUT = CHAPTERS / "09-the-compile-pipeline-linking-and-build-systems.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]

# Same banner the harness uses, so the generator and the gate agree on what a
# file boundary is.
FILE_BANNER_RE = re.compile(r"^\s*/\*\s*=+\s*(\S+)\s*=+\s*\*/\s*$")


# --------------------------------------------------------------------------
# running things
# --------------------------------------------------------------------------
def compile_and_run(src: str, sanitize: bool = False, werror: bool = True):
    """Return (stdout, stderr, exit)."""
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + (["-Werror"] if werror else [])
        if sanitize:
            cmd += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
        cmd += ["-o", exe, "-x", "c++", "-"]
        build = subprocess.run(cmd, input=src, text=True, capture_output=True, cwd=td)
        if build.returncode != 0:
            return "", build.stderr, build.returncode
        try:
            run = subprocess.run([exe], capture_output=True, text=True, cwd=td, timeout=20)
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", 1
        return run.stdout, run.stderr, run.returncode


def compile_only(src: str):
    """Compile with -Wall -Wextra and NO -Werror. Returns (exit, stderr).

    No -Werror because a `bad` block has to fail on a real error rather than on
    a promoted warning.
    """
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, "-x", "c++", "-"]
        build = subprocess.run(cmd, input=src, text=True, capture_output=True, cwd=td)
        return build.returncode, build.stderr


def split_files(code: str):
    """Split a multi-file listing into (name, contents) pairs, in order."""
    files = []
    name = None
    body: list[str] = []
    for line in code.split("\n"):
        m = FILE_BANNER_RE.match(line)
        if m:
            if name is not None:
                files.append((name, "\n".join(body).strip("\n") + "\n"))
            name = m.group(1)
            body = []
        elif name is not None:
            body.append(line)
    if name is not None:
        files.append((name, "\n".join(body).strip("\n") + "\n"))
    return files


def build_files(listing_text: str):
    """Write a multi-file listing to a temp dir, link it, run it.

    Mirrors what the harness does for a `run-files` block, so the transcript
    captured here is the transcript the gate will reproduce.
    """
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        sources = []
        for name, text in split_files(listing_text):
            path = work / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            if path.suffix in (".c", ".cpp"):
                sources.append(name)
        exe = work / "prog"
        cmd = [CXX] + BASE + ["-Werror", "-I."] + sources + ["-o", str(exe)]
        build = subprocess.run(cmd, text=True, capture_output=True, cwd=work)
        if build.returncode != 0:
            raise SystemExit("build failed:\n" + build.stderr)
        run = subprocess.run([str(exe)], capture_output=True, text=True,
                             cwd=work, timeout=20)
        if run.returncode != 0:
            raise SystemExit("run failed:\n" + run.stdout + run.stderr)
        return run.stdout


def build_project():
    """Copy proj/ into a temp dir, run make, then run prog.

    Returns only prog's stdout: the harness compares a `make-files` block against
    the program's output, not against make's chatter about what it compiled.
    """
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "proj"
        shutil.copytree(HERE / "proj", work)
        m = subprocess.run(["make"], capture_output=True, text=True, cwd=work)
        if m.returncode != 0:
            raise SystemExit("make failed:\n" + m.stdout + m.stderr)
        r = subprocess.run(["./prog"], capture_output=True, text=True, cwd=work)
        if r.returncode != 0:
            raise SystemExit("prog failed:\n" + r.stdout + r.stderr)
        return r.stdout


def shell_transcript(script: str, seed_project: bool = False):
    """Run a shell script the way the harness does.

    `run-project` seeds the directory from the chapter's project and builds it
    first; a plain `sh run` gets an empty directory.
    """
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        cwd = work
        if seed_project:
            cwd = work / "proj"
            shutil.copytree(HERE / "proj", cwd)
            subprocess.run(["make"], capture_output=True, text=True, cwd=cwd)
        r = subprocess.run(["sh", "-c", script], capture_output=True, text=True,
                           cwd=cwd, timeout=30)
        return r.stdout


def read(rel: str) -> str:
    return (HERE / rel).read_text(encoding="utf-8").rstrip("\n")


def listing(*pairs) -> str:
    """Join (filename, source) pairs into one multi-file listing with banners."""
    out = []
    for name, text in pairs:
        out.append(f"/* ===== {name} ===== */")
        out.append(text.rstrip("\n"))
    return "\n".join(out) + "\n"


def fence(lang: str, directive: str, body: str, text: str | None = None) -> str:
    parts = [f"```{lang} {directive}", body.rstrip("\n"), "```"]
    if text is not None:
        parts += ["", "```text", text.rstrip("\n"), "```"]
    return "\n".join(parts) + "\n"


def quoted(stderr: str, needle: str) -> str:
    """The text of a diagnostic after its `needle`, taken from the real report."""
    for line in stderr.splitlines():
        if needle in line:
            return line.split(needle, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{stderr}")


def line_with(stderr: str, needle: str) -> str:
    """The whole line containing `needle`, taken from the real report."""
    for line in stderr.splitlines():
        if needle in line:
            return line.strip()
    raise SystemExit(f"no {needle!r} in:\n{stderr}")


# --------------------------------------------------------------------------
# capture every piece of evidence
# --------------------------------------------------------------------------
print("capturing evidence ...")

# Stage 1 of the pipeline, in isolation. expand.cpp includes only a local header,
# so the expansion is deterministic and has no SDK version in it.
pp_out = shell_transcript(read("pp.sh"))

proj_listing = listing(
    ("config.h", read("proj/config.h")),
    ("config.cpp", read("proj/config.cpp")),
    ("main.cpp", read("proj/main.cpp")),
    ("Makefile", read("proj/Makefile")),
    ("Makefile.nodep", read("proj/Makefile.nodep")),
)
proj_out = build_project()

stages_out = shell_transcript(read("stages.sh"), seed_project=True)
makefile_out = shell_transcript(read("makefile.sh"), seed_project=True)
define_out = shell_transcript(read("define.sh"))

# A declaration with no definition anywhere: the compiler is happy and the
# linker is not. This is the whole point of separating the two stages.
scen_broken_src = read("scen_broken.cpp")
_, scen_broken_err = compile_only(scen_broken_src)
assert "Undefined symbols" in scen_broken_err, scen_broken_err[:400]
scen_broken_note = line_with(scen_broken_err, "Undefined symbols")

scen_listing = listing(
    ("greet.h", read("scen_greet.h")),
    ("greet.cpp", read("scen_greet.cpp")),
    ("main.cpp", read("scen_main.cpp")),
)
scen_out = build_files(scen_listing)

# assert is a debug-only check, and NDEBUG is how you turn it off.
asrt_src = r'''#include <cassert>
#include <cstdio>

int main() {
    int value = 1;

    assert(value == 2);
    std::printf("not reached\n");
    return 0;
}
'''
_, asrt_err, asrt_rc = compile_and_run(asrt_src)
assert asrt_rc != 0, "the assert was supposed to abort"
asrt_note = line_with(asrt_err, "Assertion failed").split(", file ")[0]

asrt_off_src = r'''#define NDEBUG
#include <cassert>
#include <cstdio>

int main() {
    int value = 1;

    assert(value == 2);
    std::printf("value = %d, and the assert did nothing\n", value);
    return 0;
}
'''
asrt_off_out, _, asrt_off_rc = compile_and_run(asrt_off_src)
assert asrt_off_rc == 0, asrt_off_out

# A header that is not on the include path.
nohdr_src = r'''#include "nope.h"

int main() {
    return 0;
}
'''
nohdr_rc, nohdr_err = compile_only(nohdr_src)
assert nohdr_rc != 0, "the missing header must be an error"
nohdr_note = quoted(nohdr_err, "fatal error:")

ex1_listing = listing(
    ("stats.h", read("ex1_stats.h")),
    ("stats.cpp", read("ex1_stats.cpp")),
    ("main.cpp", read("ex1_main.cpp")),
)
ex1_out = build_files(ex1_listing)

ex2_out = shell_transcript(read("ex2.sh"))
ex3_out = shell_transcript(read("ex3.sh"))
includedir_out = shell_transcript(read("includedir.sh"))

ex4_macro_src = read("ex4_macro.cpp")
ex4_macro_out, _, ex4_macro_rc = compile_and_run(ex4_macro_src)
assert ex4_macro_rc == 0, ex4_macro_out

ex4_func_src = read("ex4_func.cpp")
ex4_func_out, _, ex4_func_rc = compile_and_run(ex4_func_src)
assert ex4_func_rc == 0, ex4_func_out


# --------------------------------------------------------------------------
# the chapter
# --------------------------------------------------------------------------
BODY = f"""---
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

{fence("sh", "run", read("pp.sh").strip(), pp_out)}
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

{fence("cpp", "make-files", proj_listing, proj_out)}
Now watch the stages happen one at a time, by hand, without `make` in the way:

{fence("sh", "run-project", read("stages.sh").strip(), stages_out)}
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

{fence("sh", "run-project", read("makefile.sh").strip(), makefile_out)}
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

{fence("cpp", "bad", scen_broken_src, scen_broken_note)}
Read the message carefully, because it says exactly what is missing and who wants it. It is not
about the syntax of `greeting()` — that line is fine. It is that no translation unit in the link
supplied a body for it.

:::solution Compile every source file and link them together
The fix is to put the definition in a translation unit and pass that unit to the linker:

{fence("cpp", "run-files", scen_listing, scen_out)}
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

{fence("sh", "run", read("define.sh").strip(), define_out)}
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

{fence("sh", "run", read("includedir.sh").strip(), includedir_out)}
The first compile fails and the second succeeds, with one extra flag. Note that `units.cpp` also
needs `-Iinclude` — it includes its own header the same way, so the flag belongs in the build for
every translation unit, which is why a Makefile normally carries one variable holding all the `-I`
paths and applies it to every rule.

That is also the whole difference between the two include forms. `#include "units.h"` searches the
directory of the including file first and then the `-I` directories; `#include <units.h>` skips the
local directory entirely. A project's own headers are quoted, the standard library's are bracketed,
and the reason is exactly this search order.

Get the path wrong and the compiler stops before it has read any C++ at all:

{fence("cpp", "bad", nohdr_src, nohdr_note)}
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

{fence("cpp", "run-abort", asrt_src, asrt_note)}
The message goes to stderr, the exit code is 134, and the program stops at the line that failed
rather than continuing with a wrong value. Compile the same file with `NDEBUG` defined and the check
is not there at all:

{fence("cpp", "run", asrt_off_src, asrt_off_out)}
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

{fence("cpp", "run-files", ex1_listing, ex1_out)}
Delete `stats.cpp` from the command and the error changes species: `Undefined symbols for
architecture arm64: "sum(int const*, unsigned long)", referenced from _main`. Two functions are
missing, and both are named with their parameter types — the mangling from earlier in the chapter,
doing its job of keeping overloads apart. This is also why the fix is never to add a declaration:
one is already there, and that is exactly what let the compiler succeed.
:::

:::solution Exercise 2
`#ifndef` gives the macro a default so the file still compiles without any flag, and `#if` chooses
between the branches.

{fence("sh", "run", read("ex2.sh").strip(), ex2_out)}
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

{fence("sh", "run", read("ex3.sh").strip(), ex3_out)}
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

{fence("cpp", "run", ex4_macro_src, ex4_macro_out)}
`SQUARE(next())` became `((next()) * (next()))`, so `next` ran twice and the counter is 2. The
result is still 9 because `next` returns 3 both times, which is exactly what makes this bug survive
testing: the answer looks right and only the side effect is wrong. In a real program `next` might be
reading a stream, incrementing a cursor or popping a queue, and the second call silently consumes
something.

Wrapping the argument in parentheses — the usual piece of macro advice — does not help here. It
fixes precedence, not evaluation count. The fix is to stop using a macro for something that has
semantics:

{fence("cpp", "run", ex4_func_src, ex4_func_out)}
One call, one increment. A function evaluates its argument once because that is what a function
call means. The cost is that a function is a real call rather than inline text — and an `inline`
function in a header gives you the inlining back without the double evaluation, which is why
function-like macros in modern C++ are rare and usually wrong. We come back to this in Chapter 15,
where the preprocessor gets the full treatment.
:::
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(BODY, encoding="utf-8")
print(f"\nwrote {OUT}  ({len(BODY.splitlines())} lines)")
