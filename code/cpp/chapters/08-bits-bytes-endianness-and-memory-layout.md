---
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

```cpp run
#include <climits>
#include <cstdio>

static void print_bits(unsigned value, int width) {
    for (int i = width - 1; i >= 0; --i) {
        std::putchar(((value >> (unsigned)i) & 1u) ? '1' : '0');
        if (i % 4 == 0 && i != 0) {
            std::putchar(' ');
        }
    }
}

int main() {
    unsigned char v = 0x9Cu;

    std::printf("CHAR_BIT   = %d\n", CHAR_BIT);
    std::printf("v          = 0x%02X  ", (unsigned)v);
    print_bits(v, 8);
    std::printf("\n");

    std::printf("v & 0x0F   = 0x%02X\n", (unsigned)(v & 0x0Fu));
    std::printf("v | 0x01   = 0x%02X\n", (unsigned)(v | 0x01u));
    std::printf("v ^ 0xFF   = 0x%02X\n", (unsigned)(v ^ 0xFFu));
    std::printf("~v         = 0x%02X\n", (unsigned)(unsigned char)~v);

    std::printf("v << 1     = 0x%02X\n", (unsigned)(unsigned char)(v << 1));
    std::printf("v >> 1     = 0x%02X\n", (unsigned)(unsigned char)(v >> 1));
    std::printf("bit 7 of v = %u\n", (v >> 7) & 1u);
    std::printf("bit 2 of v = %u\n", (v >> 2) & 1u);

    return 0;
}
```

```text
CHAR_BIT   = 8
v          = 0x9C  1001 1100
v & 0x0F   = 0x0C
v | 0x01   = 0x9D
v ^ 0xFF   = 0x63
~v         = 0x63
v << 1     = 0x38
v >> 1     = 0x4E
bit 7 of v = 1
bit 2 of v = 1
```

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

```cpp run
#include <cstdint>
#include <cstdio>

int main() {
    std::uint8_t byte = 0xFFu;
    std::int8_t signed_byte = (std::int8_t)byte;

    std::printf("0xFF as uint8_t = %u\n", (unsigned)byte);
    std::printf("0xFF as int8_t  = %d\n", (int)signed_byte);

    std::uint8_t wrapped = (std::uint8_t)(byte + 1u);
    std::printf("0xFF + 1 in uint8_t = %u\n", (unsigned)wrapped);

    std::int32_t negative = -8;
    std::uint32_t bits = (std::uint32_t)negative;
    std::printf("-8 as uint32_t  = %u\n", bits);

    std::printf("~0u             = %u\n", ~0u);
    std::printf("~0              = %d\n", ~0);
    return 0;
}
```

```text
0xFF as uint8_t = 255
0xFF as int8_t  = -1
0xFF + 1 in uint8_t = 0
-8 as uint32_t  = 4294967288
~0u             = 4294967295
~0              = -1
```

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

```cpp run
#include <climits>
#include <cstdint>
#include <cstdio>

static_assert(CHAR_BIT == 8, "this book assumes a byte is 8 bits");

int main() {
    std::printf("int8_t   %zu\n", sizeof(std::int8_t));
    std::printf("int16_t  %zu\n", sizeof(std::int16_t));
    std::printf("int32_t  %zu\n", sizeof(std::int32_t));
    std::printf("int64_t  %zu\n", sizeof(std::int64_t));
    std::printf("size_t   %zu\n", sizeof(std::size_t));
    std::printf("intptr_t %zu\n", sizeof(std::intptr_t));
    std::printf("float    %zu\n", sizeof(float));
    std::printf("double   %zu\n", sizeof(double));
    std::printf("int      %zu\n", sizeof(int));
    std::printf("long     %zu\n", sizeof(long));
    return 0;
}
```

```text
int8_t   1
int16_t  2
int32_t  4
int64_t  8
size_t   8
intptr_t 8
float    4
double   8
int      4
long     8
```

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

```cpp run-san-catch
#include <cstdio>

int main() {
    unsigned value = 1u;
    int shift = 32;   /* the width of `unsigned` on this target */

    std::printf("%u\n", value << shift);
    return 0;
}
```

```text
shift exponent 32 is too large for 32-bit type 'unsigned int'
```

**Shifting a negative value left.** Left-shifting a negative `int` is undefined:

```cpp run-san-catch
#include <cstdio>

int main() {
    int value = -1;

    std::printf("%d\n", value << 1);
    return 0;
}
```

```text
left shift of negative value -1
```

**Overflowing a signed value.** Not a shift at all, but the same family of bug, and the one you will
meet most often:

```cpp run-san-catch
#include <cstdio>

int main() {
    int value = 2147483647;   /* INT_MAX on a 32-bit int */

    std::printf("%d\n", value + 1);
    return 0;
}
```

```text
signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

None of those three programs crashed. Each printed a number, and each is a program whose behaviour
the standard does not define — which means the compiler is free to do something else entirely,
including at higher optimisation levels something quite different from what you just saw.

When the shift count is a constant, the compiler can see the problem before the program exists:

```cpp warn
#include <cstdio>

int main() {
    int value = 1 << 40;   /* 40 >= the 32 bits of `int` */

    std::printf("%d\n", value);
    return 0;
}
```

```text
shift count >= width of type [-Wshift-count-overflow]
```

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

```cpp run
#include <cstdint>
#include <cstdio>
#include <cstring>

int main() {
    std::uint32_t value = 0x01020304u;

    unsigned char raw[4];
    std::memcpy(raw, &value, sizeof value);
    std::printf("value = 0x%08X\n", value);
    std::printf("raw   = %02X %02X %02X %02X\n",
                (unsigned)raw[0], (unsigned)raw[1], (unsigned)raw[2], (unsigned)raw[3]);

    std::uint16_t one = 1;
    unsigned char probe[2];
    std::memcpy(probe, &one, sizeof one);
    std::printf("order = %s\n", probe[0] ? "little-endian" : "big-endian");

    unsigned char wire[4] = {
        (unsigned char)(value >> 24), (unsigned char)(value >> 16),
        (unsigned char)(value >> 8),  (unsigned char)value,
    };
    std::printf("be    = %02X %02X %02X %02X\n",
                (unsigned)wire[0], (unsigned)wire[1], (unsigned)wire[2], (unsigned)wire[3]);

    std::uint32_t back = ((std::uint32_t)wire[0] << 24) | ((std::uint32_t)wire[1] << 16) |
                         ((std::uint32_t)wire[2] << 8)  |  (std::uint32_t)wire[3];
    std::printf("back  = 0x%08X\n", back);
    return 0;
}
```

```text
value = 0x01020304
raw   = 04 03 02 01
order = little-endian
be    = 01 02 03 04
back  = 0x01020304
```

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

```cpp run
#include <cstdint>
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
```

```text
memcpy into a uint32_t = 738263040
decoded as big-endian  = 300
```

The server allocates 738 MB and blocks waiting for bytes that are never coming. Nothing is corrupt
and nothing crashes, which is what makes this failure mode expensive: the code is *correct on the
machine it was written on*, and the bug only appears when the other end of the wire disagrees about
byte order.

:::solution Decode in the order the format specifies
Never let the machine choose the interpretation. Shift the bytes into place yourself:

```cpp run
#include <cstdint>
#include <cstdio>

static void put_u32_le(std::uint8_t *out, std::uint32_t value) {
    out[0] = (std::uint8_t)value;
    out[1] = (std::uint8_t)(value >> 8);
    out[2] = (std::uint8_t)(value >> 16);
    out[3] = (std::uint8_t)(value >> 24);
}

static std::uint32_t get_u32_le(const std::uint8_t *in) {
    return (std::uint32_t)in[0] | ((std::uint32_t)in[1] << 8) |
           ((std::uint32_t)in[2] << 16) | ((std::uint32_t)in[3] << 24);
}

int main() {
    std::uint32_t value = 0x01020304u;

    std::uint8_t le[4];
    std::uint8_t be[4];
    put_u32_le(le, value);
    be[0] = (std::uint8_t)(value >> 24);
    be[1] = (std::uint8_t)(value >> 16);
    be[2] = (std::uint8_t)(value >> 8);
    be[3] = (std::uint8_t)value;

    std::printf("le = %02X %02X %02X %02X\n",
                (unsigned)le[0], (unsigned)le[1], (unsigned)le[2], (unsigned)le[3]);
    std::printf("be = %02X %02X %02X %02X\n",
                (unsigned)be[0], (unsigned)be[1], (unsigned)be[2], (unsigned)be[3]);
    std::printf("byte-reverse of each other = %d\n",
                le[0] == be[3] && le[1] == be[2] && le[2] == be[1] && le[3] == be[0]);
    std::printf("round trip = 0x%08X\n", get_u32_le(le));
    return 0;
}
```

```text
le = 04 03 02 01
be = 01 02 03 04
byte-reverse of each other = 1
round trip = 0x01020304
```

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

```cpp run
#include <cstddef>
#include <cstdio>

struct Loose {
    char a;
    int  b;
    char c;
};

struct Tight {
    int  b;
    char a;
    char c;
};

int main() {
    std::printf("Loose size=%zu align=%zu  a=%zu b=%zu c=%zu\n",
                sizeof(Loose), alignof(Loose),
                offsetof(Loose, a), offsetof(Loose, b), offsetof(Loose, c));
    std::printf("Tight size=%zu align=%zu  b=%zu a=%zu c=%zu\n",
                sizeof(Tight), alignof(Tight),
                offsetof(Tight, b), offsetof(Tight, a), offsetof(Tight, c));
    std::printf("members alone = %zu bytes\n",
                sizeof(char) + sizeof(int) + sizeof(char));
    return 0;
}
```

```text
Loose size=12 align=4  a=0 b=4 c=8
Tight size=8 align=4  b=0 a=4 c=5
members alone = 6 bytes
```

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

```cpp run
#include <cstdint>
#include <cstdio>

static std::uint32_t set_bit(std::uint32_t reg, unsigned n) {
    return reg | (1u << n);
}

static std::uint32_t clear_bit(std::uint32_t reg, unsigned n) {
    return reg & ~(1u << n);
}

static std::uint32_t toggle_bit(std::uint32_t reg, unsigned n) {
    return reg ^ (1u << n);
}

static unsigned test_bit(std::uint32_t reg, unsigned n) {
    return (reg >> n) & 1u;
}

static unsigned extract(std::uint32_t reg, unsigned hi, unsigned lo) {
    unsigned width = hi - lo + 1;
    return (reg >> lo) & ((1u << width) - 1u);
}

static std::uint32_t insert(std::uint32_t reg, unsigned hi, unsigned lo, std::uint32_t value) {
    unsigned width = hi - lo + 1;
    std::uint32_t mask = ((1u << width) - 1u) << lo;
    return (reg & ~mask) | ((value << lo) & mask);
}

int main() {
    std::uint32_t instr = 0;
    instr = insert(instr, 31, 26, 0x23u);   /* opcode */
    instr = insert(instr, 25, 21, 8u);      /* rs     */
    instr = insert(instr, 20, 16, 9u);      /* rt     */
    instr = insert(instr, 15, 0, 0x0010u);  /* immediate */

    std::printf("instruction = 0x%08X\n", instr);
    std::printf("opcode=%u rs=%u rt=%u imm=%u\n",
                extract(instr, 31, 26), extract(instr, 25, 21),
                extract(instr, 20, 16), extract(instr, 15, 0));

    std::uint32_t reg = 0;
    reg = set_bit(reg, 3);
    reg = set_bit(reg, 7);
    std::printf("after set 3,7 = 0x%02X\n", reg);
    reg = toggle_bit(reg, 3);
    std::printf("after toggle 3 = 0x%02X\n", reg);
    reg = clear_bit(reg, 7);
    std::printf("after clear 7  = 0x%02X\n", reg);
    std::printf("bit 3 = %u, bit 7 = %u\n", test_bit(reg, 3), test_bit(reg, 7));
    return 0;
}
```

```text
instruction = 0x8D090010
opcode=35 rs=8 rt=9 imm=16
after set 3,7 = 0x88
after toggle 3 = 0x80
after clear 7  = 0x00
bit 3 = 0, bit 7 = 0
```

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

```cpp run
#include <cstdint>
#include <cstdio>
#include <cstring>

static std::uint32_t bits_of(float value) {
    std::uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof bits);
    return bits;
}

static void describe(float value) {
    std::uint32_t bits = bits_of(value);
    unsigned sign = (bits >> 31) & 1u;
    unsigned biased = (bits >> 23) & 0xFFu;
    unsigned mantissa = bits & 0x7FFFFFu;

    std::printf("%-5g bits=0x%08X sign=%u exponent=%u (2^%d) mantissa=0x%06X\n",
                (double)value, bits, sign, biased, (int)biased - 127, mantissa);
}

int main() {
    describe(1.0f);
    describe(0.5f);
    describe(-2.0f);
    describe(0.1f);
    return 0;
}
```

```text
1     bits=0x3F800000 sign=0 exponent=127 (2^0) mantissa=0x000000
0.5   bits=0x3F000000 sign=0 exponent=126 (2^-1) mantissa=0x000000
-2    bits=0xC0000000 sign=1 exponent=128 (2^1) mantissa=0x000000
0.1   bits=0x3DCCCCCD sign=0 exponent=123 (2^-4) mantissa=0x4CCCCD
```

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

```cpp bad
#include <cstdio>

struct Flags {
    unsigned readable : 1;
    unsigned writable : 1;
};

int main() {
    Flags flags{1, 0};

    std::printf("%zu\n", sizeof(flags.readable));
    return 0;
}
```

```text
invalid application of 'sizeof' to bit-field
```

Use bit-fields for flags in a struct that never leaves your process, and use explicit shifts and
masks — the `extract` and `insert` pair above — for anything that is written to a file or a socket.

## The project: a big-endian wire codec

Four files: a header of declarations, an implementation, a `main` that exercises them, and a
`Makefile` that builds the lot. The banner lines are listing separators, not file contents — a
`/* ===== Makefile ===== */` line would be a syntax error if you pasted it into a Makefile.

```cpp make-files
/* ===== wire.h ===== */
#ifndef WIRE_H
#define WIRE_H

#include <cstddef>
#include <cstdint>

/* Every integer is written most-significant byte first, the order the network
   uses and the order a hex dump reads naturally. */
void put_u16_be(std::uint8_t *out, std::uint16_t value);
void put_u32_be(std::uint8_t *out, std::uint32_t value);

std::uint16_t get_u16_be(const std::uint8_t *in);
std::uint32_t get_u32_be(const std::uint8_t *in);

unsigned popcount32(std::uint32_t value);

#endif
/* ===== wire.cpp ===== */
#include "wire.h"

void put_u16_be(std::uint8_t *out, std::uint16_t value) {
    out[0] = (std::uint8_t)(value >> 8);
    out[1] = (std::uint8_t)value;
}

void put_u32_be(std::uint8_t *out, std::uint32_t value) {
    out[0] = (std::uint8_t)(value >> 24);
    out[1] = (std::uint8_t)(value >> 16);
    out[2] = (std::uint8_t)(value >> 8);
    out[3] = (std::uint8_t)value;
}

std::uint16_t get_u16_be(const std::uint8_t *in) {
    return (std::uint16_t)(((std::uint16_t)in[0] << 8) | (std::uint16_t)in[1]);
}

std::uint32_t get_u32_be(const std::uint8_t *in) {
    return ((std::uint32_t)in[0] << 24) | ((std::uint32_t)in[1] << 16) |
           ((std::uint32_t)in[2] << 8)  |  (std::uint32_t)in[3];
}

unsigned popcount32(std::uint32_t value) {
    unsigned count = 0;

    while (value != 0u) {
        count += value & 1u;
        value >>= 1;
    }
    return count;
}
/* ===== main.cpp ===== */
#include <cstdio>

#include "wire.h"

int main() {
    /* An 8-byte header: a 2-byte magic, a version, a flag byte, a 4-byte length. */
    std::uint8_t header[8];
    put_u16_be(header + 0, 0xCAFEu);
    header[2] = 2;
    header[3] = 0x05;
    put_u32_be(header + 4, 300u);

    std::printf("header:");
    for (std::size_t i = 0; i < sizeof header; ++i) {
        std::printf(" %02X", (unsigned)header[i]);
    }
    std::printf("\n");

    std::printf("magic  = 0x%04X\n", (unsigned)get_u16_be(header + 0));
    std::printf("length = %u\n", get_u32_be(header + 4));
    std::printf("set bits in length = %u\n", popcount32(get_u32_be(header + 4)));
    return 0;
}
/* ===== Makefile ===== */
CXX      = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: main.o wire.o
	$(CXX) $(CXXFLAGS) -o prog main.o wire.o

main.o: main.cpp wire.h
	$(CXX) $(CXXFLAGS) -c main.cpp

wire.o: wire.cpp wire.h
	$(CXX) $(CXXFLAGS) -c wire.cpp

clean:
	rm -f prog *.o
```

```text
header: CA FE 02 05 00 00 01 2C
magic  = 0xCAFE
length = 300
set bits in length = 4
```

Now the recipe itself, run from a clean directory:

```sh run-project
echo '$ make clean'
make clean
echo '$ make'
make
echo '$ ./prog'
./prog
```

```text
$ make clean
rm -f prog *.o
$ make
clang++ -std=c++17 -Wall -Wextra -Werror -c main.cpp
clang++ -std=c++17 -Wall -Wextra -Werror -c wire.cpp
clang++ -std=c++17 -Wall -Wextra -Werror -o prog main.o wire.o
$ ./prog
header: CA FE 02 05 00 00 01 2C
magic  = 0xCAFE
length = 300
set bits in length = 4
```

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

```cpp run
#include <cstdint>
#include <cstdio>

int main() {
    std::uint8_t byte = 0xB5u;   /* 1011 0101 */

    std::printf("bits:");
    unsigned set = 0;
    for (int i = 7; i >= 0; --i) {
        unsigned bit = ((unsigned)byte >> (unsigned)i) & 1u;
        std::printf(" %u", bit);
        set += bit;
    }
    std::printf("\nset bits = %u\n", set);
    return 0;
}
```

```text
bits: 1 0 1 1 0 1 0 1
set bits = 5
```

The loop counter is an `int` and the value being shifted is `unsigned`, which is why the cast sits
on the value: `(unsigned)byte >> i` does the shift at `unsigned` width, where a shift is well
defined, rather than at `int` width where the sign bit is involved. Five bits are set in `0xB5`,
which is what the count confirms.
:::

:::solution Exercise 2
Flags are a bitmask, and the three operations you need are OR to set, AND to test, and AND with the
complement to clear.

```cpp run
#include <cstdint>
#include <cstdio>

static const std::uint32_t READABLE   = 1u << 0;
static const std::uint32_t WRITABLE   = 1u << 1;
static const std::uint32_t EXECUTABLE = 1u << 2;
static const std::uint32_t HIDDEN     = 1u << 7;

int main() {
    std::uint32_t flags = 0;
    flags |= READABLE | EXECUTABLE;

    std::printf("flags      = 0x%02X\n", flags);
    std::printf("readable   = %s\n", (flags & READABLE)   ? "yes" : "no");
    std::printf("writable   = %s\n", (flags & WRITABLE)   ? "yes" : "no");
    std::printf("executable = %s\n", (flags & EXECUTABLE) ? "yes" : "no");
    std::printf("hidden     = %s\n", (flags & HIDDEN)     ? "yes" : "no");

    flags &= ~EXECUTABLE;
    flags |= HIDDEN;
    std::printf("after changes = 0x%02X\n", flags);
    return 0;
}
```

```text
flags      = 0x05
readable   = yes
writable   = no
executable = yes
hidden     = no
after changes = 0x81
```

`flags &= ~EXECUTABLE` is the idiom worth memorising: `~EXECUTABLE` is every bit *except* the
executable bit, and ANDing with it clears that one bit and leaves the rest alone. Writing
`flags &= ~EXECUTABLE` and writing `flags ^= EXECUTABLE` are not interchangeable — the XOR version
*toggles*, so it would set the bit if it were already clear. Reach for `^` only when you mean
toggle.
:::

:::solution Exercise 3
Same three members, two orders.

```cpp run
#include <cstddef>
#include <cstdio>

struct Loose {
    char   tag;
    double value;
    int    count;
};

struct Tight {
    double value;
    int    count;
    char   tag;
};

int main() {
    std::printf("Loose size=%zu align=%zu  tag=%zu value=%zu count=%zu\n",
                sizeof(Loose), alignof(Loose),
                offsetof(Loose, tag), offsetof(Loose, value), offsetof(Loose, count));
    std::printf("Tight size=%zu align=%zu  value=%zu count=%zu tag=%zu\n",
                sizeof(Tight), alignof(Tight),
                offsetof(Tight, value), offsetof(Tight, count), offsetof(Tight, tag));
    return 0;
}
```

```text
Loose size=24 align=8  tag=0 value=8 count=16
Tight size=16 align=8  value=0 count=8 tag=12
```

`Loose` is 24 bytes: one byte for `tag`, seven bytes of padding so that the `double` starts at
offset 8, eight bytes for `value`, four for `count`, and four more bytes of tail padding so the
struct's size is a multiple of its 8-byte alignment. `Tight` is 16: the `double` first, then the
`int` at offset 8, then the `char` at 12, and three bytes of tail padding. Both structs have
alignment 8 because both contain a `double`, so the largest member sets the alignment. The eight
bytes saved are pure padding — no data was removed.
:::

:::solution Exercise 4
Mask each byte out, move it to its new position, and OR the four together.

```cpp run
#include <cstdint>
#include <cstdio>

static std::uint32_t swap_bytes(std::uint32_t value) {
    return ((value & 0x000000FFu) << 24) | ((value & 0x0000FF00u) << 8) |
           ((value & 0x00FF0000u) >> 8)  | ((value & 0xFF000000u) >> 24);
}

int main() {
    std::uint32_t host = 0x01020304u;
    std::uint32_t swapped = swap_bytes(host);

    std::printf("host    = 0x%08X\n", host);
    std::printf("swapped = 0x%08X\n", swapped);
    std::printf("round trip ok = %d\n", swap_bytes(swapped) == host);
    return 0;
}
```

```text
host    = 0x01020304
swapped = 0x04030201
round trip ok = 1
```

Each of the four terms isolates one byte and slides it across. The masks must be applied *before*
the shift, or neighbouring bytes would come along for the ride — `value << 24` on its own moves the
whole number, not just the low byte. Applying the function twice returns the original, which is the
property that makes it a valid byte-order conversion rather than just a rearrangement.
:::

:::solution Exercise 5
The three fields, then the formula that puts them back together.

```cpp run
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

int main() {
    float value = -6.0f;

    std::uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof bits);

    unsigned sign = (bits >> 31) & 1u;
    unsigned exponent = (bits >> 23) & 0xFFu;
    unsigned mantissa = bits & 0x7FFFFFu;

    /* value = (-1)^sign * (1 + mantissa / 2^23) * 2^(exponent - 127) */
    double fraction = 1.0 + (double)mantissa / 8388608.0;
    double rebuilt = std::ldexp(fraction, (int)exponent - 127);
    if (sign != 0u) {
        rebuilt = -rebuilt;
    }

    std::printf("value   = %g\n", (double)value);
    std::printf("bits    = 0x%08X\n", bits);
    std::printf("rebuilt = %g\n", rebuilt);
    return 0;
}
```

```text
value   = -6
bits    = 0xC0C00000
rebuilt = -6
```

The value is `(-1)^sign × (1 + mantissa / 2^23) × 2^(exponent − 127)`. For `-6.0` the sign bit is
set, the exponent field is 129 so the power is 2, and the mantissa is `0x400000` — half of `2^23` —
so the fraction is 1.5. The result is `-1 × 1.5 × 4`, which is `-6`. `std::ldexp` applies the power
of two without a loop and without pulling in the whole of `<cmath>`'s transcendental machinery.
:::

:::solution Exercise 6
Little-endian writes the least significant byte first, so it is the mirror image of the big-endian
pair.

```cpp run
#include <cstdint>
#include <cstdio>

static void put_u32_le(std::uint8_t *out, std::uint32_t value) {
    out[0] = (std::uint8_t)value;
    out[1] = (std::uint8_t)(value >> 8);
    out[2] = (std::uint8_t)(value >> 16);
    out[3] = (std::uint8_t)(value >> 24);
}

static std::uint32_t get_u32_le(const std::uint8_t *in) {
    return (std::uint32_t)in[0] | ((std::uint32_t)in[1] << 8) |
           ((std::uint32_t)in[2] << 16) | ((std::uint32_t)in[3] << 24);
}

int main() {
    std::uint32_t value = 0x01020304u;

    std::uint8_t le[4];
    std::uint8_t be[4];
    put_u32_le(le, value);
    be[0] = (std::uint8_t)(value >> 24);
    be[1] = (std::uint8_t)(value >> 16);
    be[2] = (std::uint8_t)(value >> 8);
    be[3] = (std::uint8_t)value;

    std::printf("le = %02X %02X %02X %02X\n",
                (unsigned)le[0], (unsigned)le[1], (unsigned)le[2], (unsigned)le[3]);
    std::printf("be = %02X %02X %02X %02X\n",
                (unsigned)be[0], (unsigned)be[1], (unsigned)be[2], (unsigned)be[3]);
    std::printf("byte-reverse of each other = %d\n",
                le[0] == be[3] && le[1] == be[2] && le[2] == be[1] && le[3] == be[0]);
    std::printf("round trip = 0x%08X\n", get_u32_le(le));
    return 0;
}
```

```text
le = 04 03 02 01
be = 01 02 03 04
byte-reverse of each other = 1
round trip = 0x01020304
```

The two four-byte sequences are exact reverses of each other, and the round trip through
`get_u32_le` returns the original. This is the pair to reach for when a format specifies
little-endian — as most on-disk formats and the x86 memory model do. Note that on a little-endian
machine the `le` array happens to be what a `memcpy` of the value would produce, which is exactly
why the `memcpy` shortcut survives code review: it passes locally and fails on the wire.
:::
