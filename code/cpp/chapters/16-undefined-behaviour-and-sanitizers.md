---
chapter: 16
part: 2
title: Undefined Behaviour and Sanitizers
summary: Learn the difference between "wrong", "won't compile" and "undefined" — signed overflow, out-of-bounds access, use-after-free, bad shifts and null writes — and how to make ASan and UBSan prove each one instead of guessing.
minutes: 80
tags: [undefined-behaviour, UB, sanitizer, ASan, UBSan, AddressSanitizer, signed-overflow, use-after-free, double-free, strict-aliasing, integer-overflow]
---

Up to now every mistake in this book has been one of two kinds: the compiler refused the program, or
the program ran and did something you can reason about. C has a third kind, and it is the one that
costs people days. The program compiles. It runs. It prints a number. And the language standard
places **no requirements at all** on what that number is — not "wrong", not "unpredictable", but
outside the contract entirely. This chapter is about that third kind, and about the tools that turn
it from a mystery into a line of output naming the file and the line.

## "Undefined" is permission, not randomness

The standard uses *undefined behaviour* to mean: it imposes no requirements. That sentence is a
licence granted to the compiler, and compilers use it. Here is a program whose behaviour changes
with the optimisation level:

```sh run
cat > opt.c <<'EOF'
#include <stdio.h>
#include <limits.h>
int main(void) {
    volatile int v = INT_MAX;
    int x = v;
    if (x + 1 > x) printf("overflow assumed impossible\n");
    else printf("no overflow\n");
    return 0;
}
EOF
clang -std=c17 -O0 -o o0 opt.c && printf "at -O0: " && ./o0
clang -std=c17 -O2 -o o2 opt.c && printf "at -O2: " && ./o2
```

```text
at -O0: no overflow
at -O2: overflow assumed impossible
```

The expression is `x + 1 > x`, and `x` is `INT_MAX`. Unoptimised, `x + 1` wraps to `INT_MIN`, which
is not greater than `INT_MAX`, so the program prints `no overflow`. At `-O2` the compiler reasons
that signed overflow **cannot happen**, and from a premise that is false it proves anything: if
`x + 1` cannot overflow then `x + 1 > x` is true for every `x`, so the test is folded away and the
branch that should be unreachable is taken.

Nothing here is a compiler bug. Saying "overflow is undefined" is exactly saying "you may assume it
does not happen", and one wrong assumption can delete a check, remove a loop's exit condition, or
make two different pieces of code disagree about the same value.

:::danger UB is not "produces a garbage value"
The habit that costs the most time is treating UB as *unspecified but bounded* — "it'll be some
number, probably `INT_MIN`". It is not. The licence is unbounded, and the optimiser is the thing
that collects it. A program with UB can work perfectly in a debug build and misbehave only in the
build you ship, which is the worst possible place for a defect to appear.
:::

## Signed overflow, and the unsigned exception

```c run-san-catch
#include <stdio.h>
#include <limits.h>

int main(void) {
    int x = INT_MAX;
    printf("x      = %d\n", x);
    int y = x + 1;                /* undefined behaviour: signed overflow */
    printf("x + 1  = %d\n", y);
    return 0;
}
```

```text
runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

The program printed a plausible answer — `-2147483648` — and was still wrong in the only sense that
matters: the standard does not guarantee that answer, and the compiler is free to act as though the
line never executes. UBSan names the operation, both operands and the type.

Unsigned arithmetic has no such rule. It is defined to wrap modulo 2^N:

```c run-san
#include <stdio.h>
#include <limits.h>

int main(void) {
    unsigned int u = UINT_MAX;
    printf("UINT_MAX     = %u\n", u);
    u = u + 1;                     /* defined: wraps modulo 2^32 */
    printf("UINT_MAX + 1 = %u\n", u);

    unsigned int z = 0;
    printf("0 - 1        = %u\n", z - 1);
    return 0;
}
```

```text
UINT_MAX     = 4294967295
UINT_MAX + 1 = 0
0 - 1        = 4294967295
```

This block is `run-san`, not `run-san-catch`: the sanitizers must stay **silent**, and they do,
because wrapping is required behaviour for `unsigned int`. That is the reason a size, a count or an
index should be unsigned — and the reason `for (unsigned i = n; i-- > 0;)` works while the signed
version of the same loop is a trap.

### Why the block says `run-san-catch`

```sh run
cat > ub.c <<'EOF'
#include <limits.h>
#include <stdio.h>
int main(void) {
    int x = INT_MAX;
    int y = x + 1;
    printf("x + 1 = %d\n", y);
    return 0;
}
EOF
clang -std=c17 -fsanitize=undefined -o ub ub.c
./ub 2>/dev/null
echo "exit=$?"
```

```text
x + 1 = -2147483648
exit=0
```

Read the last line: **the process exited 0.** UBSan printed its report to stderr and let the program
continue. Measured on this platform, that is what happens, and it is why every UB demonstration in
this chapter is `run-san-catch` rather than `run` — a plain `run` block asserts only the exit code,
so a block with UB in it would "pass" while teaching the reader to expect a crash that never comes.

## Memory: past the end, after the end, and twice

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(4 * sizeof(int));
    if (!p) return 1;
    p[0] = 10;
    p[1] = 20;
    p[2] = 30;
    p[3] = 40;
    printf("p[3] = %d\n", p[3]);
    printf("p[4] = %d\n", p[4]);   /* one past the end of the block */
    free(p);
    return 0;
}
```

```text
ERROR: AddressSanitizer: heap-buffer-overflow
```

`malloc(4 * sizeof(int))` is 16 bytes; `p[4]` is byte 16, the first one you do not own. ASan reports
the region and the offset, and — unlike the sanitizer-free build, which prints whatever happens to
live there — it reports it *every time*, including the runs where the neighbouring bytes happen to
hold a plausible value.

```c run-san-catch
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));
    if (!p) return 1;
    *p = 7;
    printf("before free: %d\n", *p);
    free(p);
    printf("after free:  %d\n", *p);   /* use after free */
    return 0;
}
```

```text
ERROR: AddressSanitizer: heap-use-after-free
```

After `free(p)`, the pointer still holds the address; what changed is that you no longer own it.
Reading through it is UB even when the value looks intact, because the allocator may have reused
those bytes already. ASan quarantines freed memory precisely so that this reads as an error rather
than as a stale `7`.

```c run-san-catch
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));
    if (!p) return 1;
    *p = 1;
    free(p);
    free(p);       /* double free */
    return 0;
}
```

```text
ERROR: AddressSanitizer: attempting double-free
```

A second `free` of the same pointer corrupts the allocator's own bookkeeping, which is why a
double free often crashes somewhere with no visible connection to the line that caused it. ASan
names it at the second `free`.

## Writing through a null pointer

```c run-san-catch
#include <stdio.h>

int main(void) {
    int *p = NULL;
    printf("about to write through a null pointer\n");
    *p = 1;
    printf("wrote %d\n", *p);
    return 0;
}
```

```text
runtime error: store to null pointer of type 'int'
```

UBSan reports the store first, and the process then dies on the signal ASan reports as a `SEGV` on
the zero page. The lesson is not "null checks are good" — it is that the failure is *detected*
rather than silently accepted, and that a null write is UB rather than a guaranteed crash. On a
platform with a writable zero page, or with the write optimised into something else, it may not
crash at all.

## Shifts: one the compiler sees, one it cannot

A shift by a constant the compiler can evaluate is caught before the program exists:

```c warn
#include <stdio.h>

int main(void) {
    unsigned int u = 1u;
    printf("1u << 31 = %u\n", u << 31);
    printf("1u << 32 = %u\n", u << 32);   /* undefined: exponent == width */
    return 0;
}
```

```text
warning: shift count >= width of type [-Wshift-count-overflow]
```

That is a warning and not an error, which is worth noticing: **this program is still wrong, and it
still compiles** unless you add `-Werror`. The warning is the compiler telling you it can already see
the mistake.

Make the shift count a variable and the compiler cannot see it any more, so the job falls to UBSan:

```c run-san-catch
#include <stdio.h>

int main(void) {
    unsigned int u = 1u;
    int n = 32;                    /* a variable: invisible to the compiler */
    printf("1u << %d = %u\n", n, u << n);
    return 0;
}
```

```text
runtime error: shift exponent 32 is too large for 32-bit type 'unsigned int'
```

Note what the program printed: `1u << 32 = 1`. On this machine the shift instruction uses only the
low bits of the count, so shifting by 32 behaves like shifting by 0 — a perfectly plausible answer
that is wrong, produced by hardware rather than by the language. This is the shape of most UB bugs:
not a crash, but a number that looks reasonable enough to be believed.

## What the sanitizers cannot see

Two classes of mistake in this chapter are **not** caught by ASan or UBSan, and knowing the limits
matters as much as knowing the coverage.

```c warn
#include <stdio.h>

int main(void) {
    int x;
    printf("x = %d\n", x);
    return 0;
}
```

```text
warning: variable 'x' is uninitialized when used here [-Wuninitialized]
```

Reading an uninitialised variable is caught here by a *compiler* warning, not by a sanitizer. ASan
does not instrument uninitialised reads — that is the job of MemorySanitizer, which is not available
on this platform. The practical consequence: **`-Wall -Wextra -Werror` and the sanitizers are not
substitutes, they are different nets**, and you need both.

Reinterpreting an object's bytes through an incompatible pointer type violates the strict aliasing
rule, and no tool in this chapter reports it. The defined way to do it is `memcpy`, which the
compiler understands as a byte copy:

```c run
#include <stdio.h>
#include <string.h>

int main(void) {
    float f = 1.0f;
    unsigned int bits;
    memcpy(&bits, &f, sizeof bits);      /* the defined way to reinterpret bytes */
    printf("1.0f as bits = 0x%08x\n", bits);

    float g;
    memcpy(&g, &bits, sizeof g);
    printf("back to float = %.1f\n", g);
    return 0;
}
```

```text
1.0f as bits = 0x3f800000
back to float = 1.0
```

`0x3f800000` is the IEEE-754 bit pattern for `1.0f`, so the round trip is exact. Use `memcpy` for
type punning; a `*(unsigned int *)&f` cast may appear to work and may be broken by the optimiser.

## Running them, and what each one covers

Add both sanitizers to any build you are testing:

```bash
clang -std=c17 -Wall -Wextra -Werror -g -fno-omit-frame-pointer \
      -fsanitize=address,undefined -o prog prog.c
```

| Tool | Catches | Not available here |
|---|---|---|
| `-Wall -Wextra -Werror` | mistakes the compiler can see: uninitialised reads, constant shift overflow, format mismatches | — |
| AddressSanitizer | out-of-bounds (heap and stack), use-after-free, double free, invalid `free` | **leak detection** — macOS ships no LeakSanitizer, so a leak is reported only on Linux or under `valgrind` |
| UndefinedBehaviorSanitizer | signed overflow, invalid shifts, null pointer use, misaligned access | **does not change the exit code** — a report alone will not fail a script |
| ThreadSanitizer | data races | not exercised in this chapter; concurrency arrives in Chapter 40 |

`-g` and `-fno-omit-frame-pointer` are what make the stack traces readable; without them ASan still
catches the bug but its report is a list of addresses.

:::scenario A crash in a function that has no bugs in it
A service dies once a night inside `free()`, in a module nobody has touched in months. The core dump
points at a line that is obviously correct. Adding ASan makes the failure appear immediately, and
now it points at a completely different function — one that frees a buffer and then keeps a pointer
to it in a struct that another request reads later.
:::

:::solution Run the test suite under ASan before trying to reason about it. The crash was in `free()` because that is where the allocator finally noticed corruption; the *defect* was a use-after-free in a different function, perhaps minutes earlier. ASan quarantines freed memory and reports the read at the moment it happens, which moves the diagnostic from "where it finally broke" to "where you made the mistake". Then fix the ownership: either the struct owns the buffer and frees it when it is done, or the buffer outlives every reader — but not both, and not neither. A sanitizer run in CI converts this class of bug from a nightly mystery into a failing build.
:::

:::pitfall A sanitizer build is not a release build
ASan and UBSan change the program: allocations move, red zones appear between objects, and timing
shifts. Do not compare timings measured under a sanitizer with timings from a normal build, and do
not ship the binary. More subtly, a bug that ASan reports may be *invisible* without it, so "it
passed in production for a year" is not evidence the code is correct — only that nothing has
detected the defect yet.
:::

## Key takeaways

- Undefined behaviour means the standard imposes no requirements; it is permission for the compiler to assume the case never happens, not a guarantee of a wrong-but-usable value.
- Signed integer overflow is UB; unsigned arithmetic is defined to wrap modulo 2^N, which is why counts and indices should be unsigned.
- UBSan prints its report to stderr and **leaves the exit code at 0**, so a UB demonstration must be `run-san-catch` — a `run` block would pass on the exit code alone.
- Reading past the end of an allocation, reading after `free`, and freeing twice are all caught by ASan, which names the region and the operation.
- A shift count that is a constant is caught by a compiler *warning*; make it a variable and only UBSan can see it.
- Uninitialised reads are a `-Wall` warning, not a sanitizer finding — ASan and UBSan are different nets from the compiler's, and you need both.
- Use `memcpy` to reinterpret bytes; a pointer cast between incompatible types violates strict aliasing and no tool here reports it.
- macOS has no leak detection, so a leak must be checked on Linux or with `valgrind`; never promise a reader a leak report this platform cannot produce.
- A sanitizer build is a diagnostic build: do not measure performance under it and do not ship it.

## Practice

- [ ] Compile a program that reads `p[4]` from a 4-`int` allocation **without** sanitizers and record what it prints. Then add `-fsanitize=address` and record the difference.
- [ ] Write a loop `for (unsigned i = 5; i-- > 0; )` and the signed equivalent. Explain why the unsigned one terminates and what makes the signed one different.
- [ ] Take a program that frees a pointer and then reads it. Confirm ASan names the read, then fix it by moving the `free` after the last use.
- [ ] Shift `1u` by a constant `32` and by a variable holding `32`. Show which one the compiler catches and which one needs UBSan.
- [ ] Add `-fsanitize=address,undefined` to a Makefile target called `san` and confirm `make san` builds and runs a correct program cleanly.

## Solutions

:::solution Exercise 1
Without sanitizers the read usually returns whatever integer happens to sit in the byte after your
block — often `0`, which is why it survives testing. Under ASan you get
`ERROR: AddressSanitizer: heap-buffer-overflow` naming the region and the offset, deterministically,
on every run. The unsanitised answer is not "a wrong value", it is an accident of layout.
:::

:::solution Exercise 2
`for (unsigned i = 5; i-- > 0; )` decrements `i` and compares against `0`; when `i` reaches `0` the
comparison fails and the loop stops, and because unsigned arithmetic wraps by definition there is no
undefined transition at the bottom. The signed version relies on `i` going negative to exit, which
is fine — until someone changes the bound or the type, at which point the last decrement can
overflow, and signed overflow is UB rather than a wrap. Prefer the unsigned form for a countdown.
:::

:::solution Exercise 3
Move the `free` below the last read, or copy the value out before freeing. ASan reports
`ERROR: AddressSanitizer: heap-use-after-free` at the read, which is the line that is actually wrong;
without it the read often succeeds and the bug surfaces later as corruption in unrelated code. The
rule to apply is that a pointer's *lifetime* must cover every use of it, not merely the allocation.
:::

:::solution Exercise 4
`1u << 32` with a literal is caught at compile time: `warning: shift count >= width of type`. That is
only a warning, so it needs `-Werror` to stop the build. With the count in a variable the compiler
cannot evaluate it, so the program builds and UBSan reports
`shift exponent 32 is too large for 32-bit type 'unsigned int'` at run time — after the program has
already printed a wrong answer.
:::

:::solution Exercise 5
Give the target its own binary and flags so the normal build stays clean:
`san: prog.c` with `$(CC) -std=c17 -Wall -Wextra -Werror -g -fno-omit-frame-pointer -fsanitize=address,undefined -o prog-san prog.c` (recipes need a tab). A correct program then builds and runs
with no output beyond its own `printf` — which is the signal you want: silence means the sanitizers
found nothing. Verify it by temporarily introducing an out-of-bounds read and watching `make san`
fail.
:::
