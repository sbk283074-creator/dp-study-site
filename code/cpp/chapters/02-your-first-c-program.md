---
chapter: 2
part: 1
title: Your First C Program
summary: Read and write the smallest real C program — what main returns, how printf actually formats, why the exit code matters, and how to get a number in and out of a program.
minutes: 40
tags: [c, main, printf, format specifiers, exit codes]
---

Every C program you will ever write is the same program with more in the middle: something runs
`main`, `main` does work, and `main` returns a number to whoever started it. That number is not a
formality — it is how the program tells the operating system and every shell script on the machine
whether it succeeded. This chapter gets that skeleton exactly right, then fills it in with the two
things every program does: printing values and computing with them. Get comfortable here and the
rest of C is detail; get sloppy here and you will spend your life confused about why a build script
ignored a failure.

## The smallest program that is not a toy

```c run
#include <stdio.h>

int main(void) {
    printf("Hello from C.\n");
    return 0;
}
```

```text
Hello from C.
```

Four lines do real work, and each one is worth naming.

**`#include <stdio.h>`** is a preprocessor instruction, not C. It pastes the contents of the
standard input/output header in at that point, which is where the compiler learns that `printf`
exists and what arguments it takes. Without it, `printf` is an unknown name and the build fails.
The angle brackets mean "look in the system include directories"; `"myfile.h"` with quotes means
"look next to this file first" (Chapter 13).

**`int main(void)`** is the entry point. `int` is the return type — `main` gives a number back.
`(void)` means "takes no arguments", which in C is not the same as `()`: an empty pair of
parentheses says "takes unspecified arguments" and switches off argument checking. Always write
`(void)`.

**`printf("Hello from C.\n")`** prints. The `\n` is a newline character — two characters in the
source, one byte in the output.

**`return 0`** hands `0` back to the operating system. Zero means success. This is a convention, not
a rule of the language, and it is a convention that everything on Unix follows.

## The exit code is a real channel

`main`'s return value becomes the program's **exit status**, and any shell can read it. Try it:

```bash
./hello
echo $?
```

```text
0
```

`$?` is the exit status of the last command. Now change `return 0;` to `return 1;`, rebuild, and run
the same two commands. You get `1`. That single number is how `make`, CI systems, package managers
and shell scripts decide whether your program worked. A program that prints an error message but
returns `0` is a program that **lies**, and it will break somebody's automation.

:::pitfall Falling off the end of main
In C, reaching the closing `}` of `main` without a `return` is a special case: the standard says the
program exits with status `0`. So `return 0;` is technically optional in `main` and nowhere else.
Do not use that as a style: every other function that promises to return a value and does not is
undefined behaviour, and a reader cannot tell from a missing `return 0;` whether you meant it or
forgot it. Write it.
:::

## printf: the format string is a promise

`printf`'s first argument is a **format string**, and it is not just text. Every `%` in it is a slot
that consumes the next argument. The letter after the `%` says what type that argument is, and the
compiler trusts you.

| Specifier | Consumes | Example output |
|---|---|---|
| `%d` | `int` | `42` |
| `%ld` | `long` | `42` |
| `%u` | `unsigned int` | `42` |
| `%f` | `double` | `3.140000` |
| `%.2f` | `double`, 2 decimal places | `3.14` |
| `%c` | a character (`int` holding a char code) | `A` |
| `%s` | a string (`char *`) | `hello` |
| `%%` | nothing — prints a literal `%` | `%` |

```c run
#include <stdio.h>

int main(void) {
    int apples = 12;
    double price = 0.75;
    double total = apples * price;
    char grade = 'A';

    printf("apples:  %d\n", apples);
    printf("price:   %.2f\n", price);
    printf("total:   %.2f\n", total);
    printf("grade:   %c\n", grade);
    printf("percent: 100%%\n");
    return 0;
}
```

```text
apples:  12
price:   0.75
total:   9.00
grade:   A
percent: 100%
```

Two things to notice. `%f` prints six decimal places by default, which is why `%.2f` exists — the
`.2` is a precision, and it rounds. And `%%` is how you print a percent sign, because a lone `%`
would start a conversion.

:::danger A format specifier that disagrees with its argument
`%f` tells `printf` to read a `double` from the argument list. Give it an `int` and `printf` — which
has no type information beyond the format string — reads your integer's bits and reinterprets them
as a floating-point number. The result is not an error message; it is whatever those bits happen to
mean.

```c warn
#include <stdio.h>

int main(void) {
    int count = 7;
    printf("count as a double: %f\n", count);
    return 0;
}
```

The real diagnostic, which you get because you are building with `-Wall`:

```text
fmt.c:5:39: warning: format specifies type 'double' but the argument has type 'int' [-Wformat]
    5 |     printf("count as a double: %f\n", count);
      |                                ~~     ^~~~~
      |                                %d
1 warning generated.
```

Read the word after the column number: **warning**, not error. Without `-Werror` this program builds
and runs, and prints `0.000000`. That is precisely why the flag from Chapter 1 earns its place — it
promotes this warning into a build failure, so the mistake never reaches a running program. The
compiler even prints the fix (`%d`) under the caret.

It cannot save you in every case. Here the format string is passed *through* a function:

```c run
#include <stdio.h>
#include <stdarg.h>

static void log_value(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
}

int main(void) {
    int count = 7;
    log_value("count as a double: %f\n", count);
    return 0;
}
```

```text
count as a double: 0.000000
```

This one builds cleanly under `-Wall -Wextra -Werror` and prints nonsense, because by the time the
format string meets the argument the compiler has lost the connection between them — the argument's
type was erased at the `...`. Wrapper functions that forward a format string are exactly where this
bug lives in real code. Chapter 19 shows how to hand the compiler back enough information to check
through the wrapper.
:::

## A program that computes something

Printing constants teaches syntax. Here is a program with an actual job: convert a temperature.

```c run
#include <stdio.h>

int main(void) {
    double celsius = 37.0;
    double fahrenheit = celsius * 9.0 / 5.0 + 32.0;

    printf("%.1f C = %.1f F\n", celsius, fahrenheit);
    return 0;
}
```

```text
37.0 C = 98.6 F
```

The expression `celsius * 9.0 / 5.0 + 32.0` is worth reading slowly, because it contains a trap you
will meet in Chapter 4.

Why `9.0 / 5.0` and not `9 / 5`? Because `9 / 5` is **integer division**, and it equals `1`, not
`1.8`. The `.0` on either side makes it a floating-point operation. This one character is the
difference between `98.6` and `98.0`, and it is one of the most common bugs in beginner C.

Order matters too: `celsius * 9.0 / 5.0` and `celsius * (9.0 / 5.0)` give the same answer here
because both are floating-point, but `celsius * 9 / 5` does not — it truncates at the division.
Multiplication and division have the same precedence and associate left to right, so
`celsius * 9.0 / 5.0` means `(celsius * 9.0) / 5.0`.

## Getting a value in

A program that cannot take input is a demonstration. `scanf` is the mirror of `printf` and shares its
format-string rules.

```c compile
#include <stdio.h>

int main(void) {
    int width = 0;
    int height = 0;

    printf("Enter width and height: ");
    if (scanf("%d %d", &width, &height) != 2) {
        fprintf(stderr, "expected two whole numbers\n");
        return 1;
    }

    printf("area = %d\n", width * height);
    return 0;
}
```

Build it, then feed it input without typing anything:

```bash
printf '3 4\n' | ./area
```

```text
Enter width and height: area = 12
```

The prompt and the answer land on the same line, because the input was already waiting — the program
never paused. Type the numbers yourself instead and you will see the prompt, then your keystrokes,
then the answer on the next line. Same program, same output, different presentation: a terminal
echoes what you type, and a pipe does not.

Two things there are not optional. The `&` in `&width` passes the **address** of the variable, not
its value — `scanf` needs to know where to write. Forgetting the `&` is the single most common
`scanf` mistake and it usually crashes. And checking `scanf`'s return value, which is the number of
items it successfully converted, is how you find out that the user typed `three` instead of `3`.
Chapter 14 makes that check systematic.

:::scenario The script that "worked" and then deleted the wrong files
A build script runs `make clean`, then `rm -rf build/`, then copies artifacts. One day `make clean`
fails — a permission problem — and the script cheerfully continues and wipes a directory it should
never have touched. The cause is that the script never looked at `$?`.

:::solution Check the exit status, and make the shell do it for you
The direct fix is to test after every command:

```bash
make clean || exit 1
```

But the better fix is to stop relying on remembering. `set -e` makes the shell abort on the first
command that returns non-zero:

```bash
set -euo pipefail
make clean
rm -rf build/
cp -r out/ build/
```

`-e` exits on failure, `-u` treats an unset variable as an error, `-o pipefail` makes a pipeline
fail if any stage fails rather than only the last. Every serious shell script starts with that line.
And the C half of the lesson: this only works because well-behaved programs **return non-zero on
failure**. Your own programs must do the same — which is why `return 0` at the end of `main` is a
statement about correctness, not a ritual.
:::

## Key takeaways

- A C program is `main`, work, and a return value; `int main(void)` is the correct signature.
- `main`'s return value becomes the exit status. `0` means success, non-zero means failure, and
  scripts depend on it.
- `#include <stdio.h>` is a preprocessor paste, and it is why `printf` is a known name.
- `printf`'s format string is the only type information it has; a specifier that disagrees with its
  argument is not caught at runtime and produces garbage.
- `%d` is `int`, `%f` is `double`, `%s` is a string, `%c` is a character, `%%` is a literal percent.
- `%.2f` sets precision and rounds; bare `%f` prints six decimal places.
- Integer division truncates: `9 / 5` is `1`, and `9.0 / 5.0` is `1.8`.
- `scanf` needs the address of the variable (`&x`) and its return value tells you how many items it
  actually read.

## Practice

- [ ] Write a program that prints your name, then returns `0`. Run it and check `echo $?`.
- [ ] Change it to return `3`, rebuild, and confirm `echo $?` prints `3`.
- [ ] Print a small receipt: three items with prices, aligned in a column, with the total. Use
      `%.2f` throughout.
- [ ] Write a program that converts a distance in miles to kilometres (`1 mile = 1.60934 km`) and
      prints both with two decimal places.
- [ ] Deliberately print a `double` with `%d` and an `int` with `%f`. Note that both build and run.
      Write down what each printed.
- [ ] Write a program that reads two integers and prints their sum, difference, product and quotient.
      Check its return value handling by running it with no input at all.

## Solutions

:::solution Exercise 3
Three items, a column, and a total computed from the values rather than typed in.

```c run
#include <stdio.h>

int main(void) {
    int pencils = 3;
    int notebooks = 2;
    int erasers = 1;

    double pencil_price = 0.75;
    double notebook_price = 2.50;
    double eraser_price = 0.40;

    double total = pencils * pencil_price
                 + notebooks * notebook_price
                 + erasers * eraser_price;

    printf("%-12s %3d x %6.2f\n", "Pencils", pencils, pencil_price);
    printf("%-12s %3d x %6.2f\n", "Notebooks", notebooks, notebook_price);
    printf("%-12s %3d x %6.2f\n", "Erasers", erasers, eraser_price);
    printf("%-12s %11s\n", "", "------");
    printf("%-12s %11.2f\n", "TOTAL", total);
    return 0;
}
```

```text
Pencils        3 x   0.75
Notebooks      2 x   2.50
Erasers        1 x   0.40
                  ------
TOTAL               7.65
```

The `%-12s` means "a string in a field at least 12 wide, left-aligned" — the minus is what makes it
left-aligned, and without it the text would be pushed right. `%3d` right-aligns a number in three
columns, and `%6.2f` right-aligns a two-decimal number in six. Field widths are how you line up
columns without counting spaces by hand, and they are worth learning now: the alternative is a
table that breaks the moment a number gains a digit.
:::

:::solution Exercise 4
Miles to kilometres, both values printed with two decimals.

```c run
#include <stdio.h>

int main(void) {
    double miles = 26.2;
    double km = miles * 1.60934;

    printf("%.2f miles = %.2f km\n", miles, km);
    return 0;
}
```

```text
26.20 miles = 42.16 km
```

`26.2` is a marathon, and the conversion factor is exact enough for the exercise. Note that both
`%.2f` slots take `double` arguments and both are correctly supplied — a mismatch here would print
garbage rather than failing, which is the lesson from the `%f`-with-an-`int` example above.
:::

:::solution Exercise 6
Two integers in, four results out, with the failure path handled.

```c compile
#include <stdio.h>

int main(void) {
    int a = 0;
    int b = 0;

    if (scanf("%d %d", &a, &b) != 2) {
        fprintf(stderr, "expected two whole numbers\n");
        return 1;
    }

    printf("sum        %d\n", a + b);
    printf("difference %d\n", a - b);
    printf("product    %d\n", a * b);

    if (b == 0) {
        fprintf(stderr, "cannot divide by zero\n");
        return 1;
    }

    printf("quotient   %d\n", a / b);
    return 0;
}
```

Run it with `printf '3 4\n' | ./calc` and it prints:

```text
sum        7
difference -1
product    12
quotient   0
```

Run with `3 4` piped in, the quotient is `0` — not `0.75` — because `a` and `b` are `int`s and
integer division truncates. That is the same rule from the temperature example, now biting in the
opposite direction: there, adding `.0` fixed it; here, you would have to decide whether you *want* a
fractional answer and use `double` if you do.

The divide-by-zero check is not decoration. Integer division by zero is undefined behaviour, and on
most machines it terminates the program with `SIGFPE` — a signal whose name suggests a floating-point
error and whose most common cause is integer division by zero. Checking first and returning `1` is
how a program fails *politely*.
:::
