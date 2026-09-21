#!/usr/bin/env python3
"""Generate chapters/08-bits-bytes-endianness-and-memory-layout.md.

Nothing in the chapter is typed by hand: the listings are read from the files
beside this script and every `text` fence is captured by compiling and running
the program, exactly as tools/verify_examples.py will.

    python3 tools/gen/08/gen.py

STYLE.md: "Generate listings from the files, do not retype them."
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAPTERS = HERE.parent.parent.parent / "chapters"   # gen/08 -> gen -> tools -> cpp
OUT = CHAPTERS / "08-bits-bytes-endianness-and-memory-layout.md"

CXX = "clang++"
BASE = ["-std=c++17", "-Wall", "-Wextra"]


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
        env = dict(os.environ)
        if sanitize:
            env["ASAN_OPTIONS"] = "detect_leaks=0"
        try:
            run = subprocess.run([exe], capture_output=True, text=True,
                                 cwd=td, timeout=20, env=env)
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT", 1
        return run.stdout, run.stderr, run.returncode


def compile_only(src: str):
    """Compile with -Wall -Wextra and NO -Werror. Returns (exit, stderr).

    No -Werror because a `warn` block is exactly the case where the compiler
    complains and still builds, and a `bad` block has to fail on a real error
    rather than on a promoted warning.
    """
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "prog")
        cmd = [CXX] + BASE + ["-o", exe, "-x", "c++", "-"]
        build = subprocess.run(cmd, input=src, text=True, capture_output=True, cwd=td)
        return build.returncode, build.stderr


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


def shell_transcript(script: str):
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "proj"
        shutil.copytree(HERE / "proj", work)
        subprocess.run(["make"], capture_output=True, text=True, cwd=work)
        r = subprocess.run(["sh", "-c", script], capture_output=True, text=True,
                           cwd=work, timeout=20)
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
    """Pull the measured diagnostic out of a compiler or sanitizer report.

    The chapter must quote what the tool actually printed, so the diagnostic is
    lifted from the run rather than paraphrased.
    """
    for line in stderr.splitlines():
        if needle in line:
            return line.split(needle, 1)[1].strip()
    raise SystemExit(f"no {needle!r} in:\n{stderr}")


# --------------------------------------------------------------------------
# capture every piece of evidence
# --------------------------------------------------------------------------
print("capturing evidence ...")

bits_src = read("bits.cpp")
bits_out, _, bits_rc = compile_and_run(bits_src)
assert bits_rc == 0, bits_out

twos_src = read("twos.cpp")
twos_out, _, twos_rc = compile_and_run(twos_src)
assert twos_rc == 0, twos_out

sizes_src = read("sizes.cpp")
sizes_out, _, sizes_rc = compile_and_run(sizes_src)
assert sizes_rc == 0, sizes_out

endian_src = read("endian.cpp")
endian_out, _, endian_rc = compile_and_run(endian_src)
assert endian_rc == 0, endian_out

layout_src = read("layout.cpp")
layout_out, _, layout_rc = compile_and_run(layout_src)
assert layout_rc == 0, layout_out

fields_src = read("fields.cpp")
fields_out, _, fields_rc = compile_and_run(fields_src)
assert fields_rc == 0, fields_out

pun_src = read("pun.cpp")
pun_out, _, pun_rc = compile_and_run(pun_src)
assert pun_rc == 0, pun_out

# Three separate undefined behaviours, each caught by UBSan.
#
# UBSan prints its report and carries on: the exit code stays 0 unless
# -fno-sanitize-recover is passed. So the assertion has to be about the report,
# not about the exit status -- and the `run-san-catch` block is still correct,
# because the harness accepts "runtime error" in stderr as the catch.
shiftexp_src = read("shiftexp.cpp")
_, shiftexp_err, _ = compile_and_run(shiftexp_src, sanitize=True)
assert "runtime error" in shiftexp_err, "shift by 32 was supposed to be caught"
shiftexp_note = quoted(shiftexp_err, "runtime error:")

shiftneg_src = read("shiftneg.cpp")
_, shiftneg_err, _ = compile_and_run(shiftneg_src, sanitize=True)
assert "runtime error" in shiftneg_err, "left shift of a negative was supposed to be caught"
shiftneg_note = quoted(shiftneg_err, "runtime error:")

overflow_src = read("overflow.cpp")
_, overflow_err, _ = compile_and_run(overflow_src, sanitize=True)
assert "runtime error" in overflow_err, "signed overflow was supposed to be caught"
overflow_note = quoted(overflow_err, "runtime error:")

# A constant shift count is caught before the program exists.
warnshift_src = read("warnshift.cpp")
warnshift_rc, warnshift_err = compile_only(warnshift_src)
assert warnshift_rc == 0, "the shift-count warning must not stop the build"
warnshift_note = quoted(warnshift_err, "warning:")

# A bit-field has no address, so it has no size either.
badbitfield_src = read("badbitfield.cpp")
badbitfield_rc, badbitfield_err = compile_only(badbitfield_src)
assert badbitfield_rc != 0, "sizeof on a bit-field must be rejected"
badbitfield_note = quoted(badbitfield_err, "error:")

# The scenario: reading a length field with memcpy instead of decoding it.
naive_src = r'''#include <cstdint>
#include <cstdio>
#include <cstring>

int main() {
    /* What arrived on the wire: the big-endian encoding of 300. */
    unsigned char wire[4] = {0x00, 0x00, 0x01, 0x2C};

    std::uint32_t host_order = 0;
    std::memcpy(&host_order, wire, sizeof host_order);

    std::uint32_t wire_order = ((std::uint32_t)wire[0] << 24) |
                               ((std::uint32_t)wire[1] << 16) |
                               ((std::uint32_t)wire[2] << 8)  |
                                (std::uint32_t)wire[3];

    std::printf("memcpy into a uint32_t = %u\n", host_order);
    std::printf("decoded as big-endian  = %u\n", wire_order);
    return 0;
}
'''
naive_out, _, naive_rc = compile_and_run(naive_src)
assert naive_rc == 0, naive_out

proj_listing = listing(
    ("wire.h", read("proj/wire.h")),
    ("wire.cpp", read("proj/wire.cpp")),
    ("main.cpp", read("proj/main.cpp")),
    ("Makefile", read("proj/Makefile")),
)
proj_out = build_project()

SHELL = r'''
echo '$ make clean'
make clean
echo '$ make'
make
echo '$ ./prog'
./prog
'''
shell_out = shell_transcript(SHELL)

EX = {}
for n in range(1, 7):
    src = read(f"ex{n}.cpp")
    out, _, rc = compile_and_run(src)
    assert rc == 0, out
    EX[n] = (src, out)


# --------------------------------------------------------------------------
# the chapter
# --------------------------------------------------------------------------
BODY = f"""---
chapter: 8
part: 1
title: Bits, Bytes, Endianness and Memory Layout
summary: Open up the bytes underneath the types — binary and hex, two's complement, bitwise operators and the shifts that are undefined, byte order, struct padding and offsetof, and how to read a float's bits.
minutes: 75
tags: [bits, bytes, hex, bitwise, two's-complement, endianness, padding, alignment, offsetof, ieee754, memcpy]
---

Chapter 3 told you an `int` is four bytes and a `double` is eight, and left it there. This chapter
opens those bytes. Once you can see the individual bits you can pack eight flags into one byte, read
and write a binary format that another program also reads, understand why `0.1` is not exactly
representable, and recognise the specific bug where a program reads the *right* memory in the
*wrong* order. Every file, socket and protocol in Parts III and V sits on top of this, so it is
worth slowing down for.

## Bits, bytes and the systems we write them in

A **byte** is the smallest unit of memory you can address. You cannot ask a machine for the third
bit of a byte — only for the byte — so bit manipulation always means the same three steps: read the
byte, change the bits you care about, write it back. A **nibble** is four bits, which is why one hex
digit is exactly one nibble: hex is a compact way to write bits, not a different kind of number.

`CHAR_BIT` is the number of bits in a byte, and the standard only promises it is at least eight.
Every platform you will meet uses eight.

{fence("cpp", "run", bits_src, bits_out)}
Read that against the code. `0x9C` is `1001 1100`. `& 0x0F` keeps the low nibble and clears
everything above it — that is the mask idiom, and it is the single most useful pattern in this
chapter. `|` sets bits, `^` flips them.

`~v` prints `0x63`, the same as `v ^ 0xFF`, and that is not a coincidence: complementing is XOR with
all ones. The cast is what makes it work. `~v` promotes the `unsigned char` to `int`, so `~` produces
`0xFFFFFF63`; casting back to `unsigned char` truncates to `0x63`. Leaving that cast out is one of
the most common surprises in bit code.

`v << 1` deserves a second look. `0x9C` shifted left is `0x138`, which does not fit in a byte, and
the cast drops the top bit to leave `0x38`. The shift happened at `int` width and the truncation
happened at the cast, and nothing warned you — because an explicit cast is you telling the compiler
you meant it.

## Two's complement, and why `0xFF` is two numbers

Signed integers are stored in **two's complement**: the top bit is worth `-2^(n-1)` rather than
`+2^(n-1)`. The practical consequence is that the same eight bits mean different numbers depending
on the type you read them through.

{fence("cpp", "run", twos_src, twos_out)}
`0xFF` is `255` as a `uint8_t` and `-1` as an `int8_t` — one pattern, two readings. `-1` is all ones
in two's complement, which is why `~0` is `-1` while `~0u` is `4294967295`: the same operation at two
different widths and types. Writing `~0` where you meant "every bit set" is a classic bug, because
what you get depends on the type the expression is converted to. Say `~0u` or `0xFFFFFFFFu`.

Unsigned arithmetic **wraps**, and the standard defines it as arithmetic modulo `2^N`, so `0xFF + 1`
in a `uint8_t` is `0` with no undefined behaviour. Signed overflow is the opposite: `INT_MAX + 1` is
undefined and the compiler may assume it never happens. That asymmetry is the subject of the next
section but one.

Converting an out-of-range value between signed and unsigned is the remaining wrinkle. Unsigned to
signed was implementation-defined before C++20 and is defined as wrapping since; every platform you
will use wraps either way. Signed to unsigned has always been defined as wrapping.

## Fixed-width types, so the width stops being a guess

`int` is four bytes on every platform this book targets, but the standard only guarantees two. When
the width is part of your contract — a file format, a protocol header, a hash — say so with the
types from `<cstdint>`.

{fence("cpp", "run", sizes_src, sizes_out)}
Every line but the last two prints a number the standard fixes. `int` is four here, on 64-bit Linux
and on 64-bit Windows. `long` is eight here and on Linux, but **four on 64-bit Windows** — that
single disagreement is the reason a file format should never contain a `long`. Use `std::int32_t`
and the question disappears.

`static_assert` is where an assumption like this belongs. It is checked when the file is compiled,
costs nothing at runtime, and fails loudly on a platform that does not match instead of producing a
program that quietly reads the wrong number of bytes.

## Shifts, and the three ways to make them undefined

The bitwise operators `&`, `|`, `^` and `~` are defined for every value. The shifts are not. Three
separate things can go wrong, and the sanitizer catches all three.

**Shifting by an amount that is too large.** The behaviour is undefined for a shift count greater
than or equal to the width of the promoted left operand:

{fence("cpp", "run-san-catch", shiftexp_src, shiftexp_note)}
**Shifting a negative value left.** Left-shifting a negative `int` is undefined:

{fence("cpp", "run-san-catch", shiftneg_src, shiftneg_note)}
**Overflowing a signed value.** Not a shift at all, but the same family of bug, and the one you will
meet most often:

{fence("cpp", "run-san-catch", overflow_src, overflow_note)}
None of those three programs crashed. Each printed a number, and each is a program whose behaviour
the standard does not define — which means the compiler is free to do something else entirely,
including at higher optimisation levels something quite different from what you just saw.

When the shift count is a constant, the compiler can see the problem before the program exists:

{fence("cpp", "warn", warnshift_src, warnshift_note)}
That block is a `warn`, not a `bad`, and the distinction is deliberate: the compiler complains and
still builds the program. `-Werror` is what turns this class of diagnostic into a build failure, and
it is the reason every project in this book compiles with it.

:::pitfall Unsigned is not a safety net for shifts
`unsigned` saves you from *overflow* — `0xFF + 1` wraps, and wrapping is defined. It does not save
you from *shift* errors. `1u << 32` is undefined even though the type is unsigned, because the
count is out of range, and `-1 << 1` is undefined because the value is negative. The two rules are
independent: unsigned arithmetic wraps, and shifts by an out-of-range or negative count are
undefined whatever the type.

Reaching for `unsigned` to silence an arithmetic warning is a habit worth having; assuming it also
made your shifts safe is a bug waiting for a 64-bit port, where the same code suddenly shifts by a
count that is now legal and produces a number you never expected.
:::

## Byte order: the same bytes, two meanings

A multi-byte integer is a sequence of bytes in memory, and there are two sensible orders for that
sequence. **Little-endian** puts the least significant byte first; **big-endian** puts the most
significant byte first. The choice belongs to the CPU, not to the language, and both are in
widespread use — which is why every file format and network protocol has to name one.

{fence("cpp", "run", endian_src, endian_out)}
Read `raw` against `value`. `0x01020304` is stored as `04 03 02 01` on this machine, least
significant byte first. The `probe` array is the two-line way to ask a machine which order it uses.
The `be` array is the same number written out by hand, most significant byte first, and `back` proves
the hand-written decode inverts the hand-written encode.

The rule to carry away is that **the order of bytes in memory is not part of the value**.
`0x01020304` is a number; `04 03 02 01` is one representation of it. The moment you write that number
to a file or a socket, the representation escapes your program and becomes part of a contract with
whoever reads it. That is why the network order is big-endian, and why `put_u32_be` below is named
after the format rather than the machine.

:::scenario The length field that was read backwards
A C server reads a binary message: a four-byte length, then that many bytes of payload. The
developer copies the four bytes into a `std::uint32_t` with `memcpy`, which is the obvious way to do
it and passes every test, because their machine and the sender are both little-endian.

The format specifies big-endian. A message arrives claiming a length of 300:

{fence("cpp", "run", naive_src, naive_out)}
The server allocates 738 MB and blocks waiting for bytes that are never coming. Nothing is corrupt
and nothing crashes, which is what makes this failure mode expensive: the code is *correct on the
machine it was written on*, and the bug only appears when the other end of the wire disagrees about
byte order.

:::solution Decode in the order the format specifies
Never let the machine choose the interpretation. Shift the bytes into place yourself:

{fence("cpp", "run", EX[6][0], EX[6][1])}
That is `put_u32_le` and `get_u32_le` from the practice exercises, shown next to the big-endian
encoding of the same value. The two byte sequences are exact reverses, which is the property that
makes a byte-order bug so hard to see by eye: both are four bytes, both are plausible, and only one
of them is what the format says.

The same argument rules out casting a byte buffer to `std::uint32_t *` and dereferencing it. That
reads the bytes in whatever order the machine uses — the bug above — and it also breaks the
compiler's aliasing rules, so an optimiser is entitled to reorder or delete the access. The
hand-written shift version is correct on every platform and compiles to a single load.
:::

## Memory layout: padding, alignment and `offsetof`

A struct's members are not necessarily laid out end to end.

{fence("cpp", "run", layout_src, layout_out)}
`Loose` holds a `char`, an `int` and a `char` — six bytes of data in twelve bytes of struct. The
compiler inserts **padding** so that each member begins at an address that is a multiple of its
alignment, and then pads the struct as a whole to a multiple of its own alignment so that an array
of them keeps every element aligned. `offsetof` is the only portable way to ask where a member
actually landed; it is a macro from `<cstddef>` that the compiler answers, not a guess you make.

`Tight` holds the same three values in eight bytes. Moving the `int` to the front removes the
padding that followed `a` and shrinks the struct by a third. With a million of them, 12 MB becomes
8 MB and the cache has more room to work with. The rule of thumb is to declare members in decreasing
order of alignment.

Before you reorder anything in a real codebase, know that layout is a property of the target rather
than the language. These numbers are for arm64 macOS with clang and the LP64 data model. The
relationships hold on x86-64 Linux too, because it is also LP64 — but change the target and you
should re-measure rather than assume. This is the same rule as `sizeof(long)`: name the platform or
do not claim the number.

## Bit manipulation in practice

Fields narrower than a byte are what every protocol header, colour value and hardware register is
made of. Two functions cover almost all of it.

{fence("cpp", "run", fields_src, fields_out)}
`extract` shifts the field down to bit zero and masks off everything above it. `insert` is the more
interesting of the two: it builds a mask covering the field's bits, clears them in the destination
with `& ~mask`, and ORs in the new value already shifted into place. The `& mask` applied to the
incoming value is not decoration — it truncates a value too large for the field, so
`insert(reg, 15, 0, 0x12345)` stores `0x2345` instead of corrupting the neighbouring bits.

Two traps live in that pair. `(1u << width) - 1u` needs the `u`: with a plain `1` the shift happens
at `int` width and a 32-bit field would be undefined behaviour, which is the first failure mode from
the previous section arriving through the back door. And `width = hi - lo + 1` counts the field
*inclusively*, which is where off-by-one errors breed — bits 31 down to 26 hold six bits, not five.

## Reading a float's bits

A `float` is not a different kind of number, it is the same bits read under a different agreement.
`memcpy` is how you look at them legally:

{fence("cpp", "run", pun_src, pun_out)}
IEEE 754 single precision is one sign bit, eight exponent bits biased by 127, and 23 mantissa bits
holding the fraction after an implicit leading one. Read the four lines. `1.0` has exponent 127 —
that is `2^0` — and a zero mantissa. `0.5` halves the exponent to 126. `-2` sets the sign bit and
raises the exponent to 128.

`0.1` is the one to study. Its mantissa is `0x4CCCCD`, not zero, because `0.1` is not a binary
fraction — it cannot be written as a finite sum of powers of two, any more than `1/3` can be written
as a finite decimal. The stored value is the nearest representable one, and every arithmetic
operation on it carries that small error forward. That is the whole of the `0.1 + 0.2` story: it is
a representation problem, not a language flaw, and the same thing happens in every language that
uses IEEE 754.

Use `memcpy` rather than a cast. `*(std::uint32_t *)&value` is undefined behaviour under the
aliasing rules, and **no sanitizer will catch it** — which makes it more dangerous than the shift
bugs above, not less. `memcpy` between two objects of the same size is defined, and the compiler
turns it into a register move.

## Bit-fields, and why not to put them on the wire

A bit-field declares a member with a width in bits and lets the compiler pack them together. It is
tempting for binary formats and it is the wrong tool, for three reasons: the layout is
implementation-defined, so the standard does not say whether `readable` occupies the low bit or the
high one, nor how a field that straddles a storage unit is arranged; a bit-field has no address, so
you cannot pass it to anything that takes a pointer; and the underlying type is `int`, so a field is
signed unless you write `unsigned`.

The missing address is why this does not compile:

{fence("cpp", "bad", badbitfield_src, badbitfield_note)}
Use bit-fields for flags in a struct that never leaves your process, and use explicit shifts and
masks — the `extract` and `insert` pair above — for anything that is written to a file or a socket.

## The project: a big-endian wire codec

Four files: a header of declarations, an implementation, a `main` that exercises them, and a
`Makefile` that builds the lot. The banner lines are listing separators, not file contents — a
`/* ===== Makefile ===== */` line would be a syntax error if you pasted it into a Makefile.

{fence("cpp", "make-files", proj_listing, proj_out)}
Now the recipe itself, run from a clean directory:

{fence("sh", "run-project", SHELL.strip(), shell_out)}
The transcript is the recipe being executed, not a description of it. Three things in the
`Makefile` are worth naming. `prog` depends on the two object files, and each object file depends on
its source *and* the header — that header dependency is what makes `make` rebuild both objects when
`wire.h` changes, and leaving it out is the classic Makefile bug where a header edit appears to do
nothing. The `clean` target exists so a rebuild can be tested honestly rather than hoped for. And
`CXX = clang++` is written with `=` rather than `?=` on purpose: `make` has a built-in default for
`CXX`, and `?=` only assigns to variables that are not already set, so `CXX ?= clang++` is silently
ignored and you get whatever `make` was built with. If you need a different compiler, override it on
the command line with `make CXX=g++`.

## Key takeaways

- A byte is the smallest addressable unit; `CHAR_BIT` is at least 8 by the standard and is 8
  everywhere you will work.
- `&` masks, `|` sets, `^` flips, `~` complements. Complementing is XOR with all ones, which is why
  `~v` and `v ^ 0xFF` agree.
- `~0` is `-1` and `~0u` is `4294967295`. Never write `~0` when you mean every bit set.
- Two's complement means the same bits read as different numbers through different types: `0xFF` is
  `255` as `uint8_t` and `-1` as `int8_t`.
- Unsigned arithmetic wraps and is defined. Signed overflow is undefined. The two rules are
  independent.
- Use `<cstdint>` types whenever the width is part of a contract, and `static_assert` to record an
  assumption the platform has to satisfy.
- Shifting by a count that is too large, shifting a negative value left, and overflowing a signed
  value are all undefined. UBSan catches all three; the compiler catches only the constant cases.
- A constant shift count that is out of range is a compile-time warning, not an error, unless you
  build with `-Werror`.
- Byte order is a property of the CPU. Little-endian stores the least significant byte first.
- Byte order is not part of a value, so every file format and protocol must name one. The network
  order is big-endian.
- Never cast a byte buffer to an integer pointer. Decode with shifts and masks; the compiler
  optimises it to a single load.
- Struct members are padded to their alignment, and the struct is padded to its own. `offsetof` is
  the portable way to find a member; declaring members in decreasing order of alignment usually
  shrinks the struct.
- `memcpy` is the legal way to reinterpret bits. A pointer cast is undefined behaviour under the
  aliasing rules and no sanitizer will tell you.
- A bit-field has no address, so `sizeof` on one is an error and it cannot be passed by pointer.

## Practice

- [ ] Print the bits of a byte most-significant first, and count how many are set.
- [ ] Build a permission flag word: set two flags with `|`, test them with `&`, and clear one with
      `&= ~`.
- [ ] Declare a struct with a `char`, a `double` and an `int`. Print `sizeof` and every `offsetof`,
      then reorder the members and print them again.
- [ ] Convert a `std::uint32_t` between little-endian and big-endian byte order and prove the round
      trip returns the original value.
- [ ] Decode a `float` into its sign, exponent and mantissa, then rebuild the value from those three
      fields.
- [ ] Write `put_u32_le` and `get_u32_le` and show they are the exact byte-reverse of the big-endian
      pair.

## Solutions

:::solution Exercise 1
Shift each bit down to position zero in turn and mask it off. Going from bit 7 to bit 0 prints the
byte the way you read it rather than the way the machine stores it.

{fence("cpp", "run", EX[1][0], EX[1][1])}
The loop counter is an `int` and the value being shifted is `unsigned`, which is why the cast sits
on the value: `(unsigned)byte >> i` does the shift at `unsigned` width, where a shift is well
defined, rather than at `int` width where the sign bit is involved. Five bits are set in `0xB5`,
which is what the count confirms.
:::

:::solution Exercise 2
Flags are a bitmask, and the three operations you need are OR to set, AND to test, and AND with the
complement to clear.

{fence("cpp", "run", EX[2][0], EX[2][1])}
`flags &= ~EXECUTABLE` is the idiom worth memorising: `~EXECUTABLE` is every bit *except* the
executable bit, and ANDing with it clears that one bit and leaves the rest alone. Writing
`flags &= ~EXECUTABLE` and writing `flags ^= EXECUTABLE` are not interchangeable — the XOR version
*toggles*, so it would set the bit if it were already clear. Reach for `^` only when you mean
toggle.
:::

:::solution Exercise 3
Same three members, two orders.

{fence("cpp", "run", EX[3][0], EX[3][1])}
`Loose` is 24 bytes: one byte for `tag`, seven bytes of padding so that the `double` starts at
offset 8, eight bytes for `value`, four for `count`, and four more bytes of tail padding so the
struct's size is a multiple of its 8-byte alignment. `Tight` is 16: the `double` first, then the
`int` at offset 8, then the `char` at 12, and three bytes of tail padding. Both structs have
alignment 8 because both contain a `double`, so the largest member sets the alignment. The eight
bytes saved are pure padding — no data was removed.
:::

:::solution Exercise 4
Mask each byte out, move it to its new position, and OR the four together.

{fence("cpp", "run", EX[4][0], EX[4][1])}
Each of the four terms isolates one byte and slides it across. The masks must be applied *before*
the shift, or neighbouring bytes would come along for the ride — `value << 24` on its own moves the
whole number, not just the low byte. Applying the function twice returns the original, which is the
property that makes it a valid byte-order conversion rather than just a rearrangement.
:::

:::solution Exercise 5
The three fields, then the formula that puts them back together.

{fence("cpp", "run", EX[5][0], EX[5][1])}
The value is `(-1)^sign × (1 + mantissa / 2^23) × 2^(exponent − 127)`. For `-6.0` the sign bit is
set, the exponent field is 129 so the power is 2, and the mantissa is `0x400000` — half of `2^23` —
so the fraction is 1.5. The result is `-1 × 1.5 × 4`, which is `-6`. `std::ldexp` applies the power
of two without a loop and without pulling in the whole of `<cmath>`'s transcendental machinery.
:::

:::solution Exercise 6
Little-endian writes the least significant byte first, so it is the mirror image of the big-endian
pair.

{fence("cpp", "run", EX[6][0], EX[6][1])}
The two four-byte sequences are exact reverses of each other, and the round trip through
`get_u32_le` returns the original. This is the pair to reach for when a format specifies
little-endian — as most on-disk formats and the x86 memory model do. Note that on a little-endian
machine the `le` array happens to be what a `memcpy` of the value would produce, which is exactly
why the `memcpy` shortcut survives code review: it passes locally and fails on the wire.
:::
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(BODY, encoding="utf-8")
print(f"\nwrote {OUT}  ({len(BODY.splitlines())} lines)")
