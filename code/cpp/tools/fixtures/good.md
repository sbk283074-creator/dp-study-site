---
chapter: 0
part: 0
title: Harness self-test — every directive used correctly
summary: This file must pass. It exercises all six directives.
minutes: 1
tags: [selftest, must-pass]
---

A complete C++ program, compiled and run, output compared.

```cpp run
#include <iostream>

int main() {
    std::cout << "hello\n";
    return 0;
}
```

```text
hello
```

The same for C, with a computed value.

```c run
#include <stdio.h>

int main(void) {
    printf("%d\n", 2 + 3);
    return 0;
}
```

```text
5
```

Compile-only: a complete program that needs stdin, so it must not be run.

```cpp compile
#include <iostream>
#include <string>

int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
        std::cout << line << "\n";
    }
    return 0;
}
```

Intentionally wrong: the missing semicolon must be rejected.

```cpp bad
int main() {
    int x = 5
    return 0;
}
```

The same rejection, this time with the diagnostic quoted. `bad` now treats a following
`text` fence as a claim: the quoted words must appear in the real error.

```cpp bad
int main() {
    int x = 5
    return 0;
}
```

```text
expected ';' at end of declaration
```

A memory bug that the sanitizer must catch. The text fence names the report.

```cpp run-san-catch
#include <iostream>

int main() {
    int *a = new int[3];
    a[7] = 1;
    std::cout << a[7] << "\n";
    delete[] a;
    return 0;
}
```

```text
heap-buffer-overflow
```

A clean run under the sanitizers.

```cpp run-san
#include <iostream>
#include <memory>

int main() {
    auto p = std::make_unique<int>(41);
    std::cout << *p + 1 << "\n";
    return 0;
}
```

```text
42
```

A leak. On a platform with LeakSanitizer this must be caught; on macOS it is reported
SKIPPED rather than passed, because Apple clang ships no LeakSanitizer.

```cpp run-san-leak
#include <iostream>

int main() {
    int *leak = new int[100];
    leak[0] = 1;
    std::cout << leak[0] << "\n";
    return 0;
}
```

```text
leak
```

A warning the compiler emits but does not treat as fatal. The documented phrase must
appear in the diagnostic.

```cpp warn
#include <iostream>

int main() {
    int unused = 5;
    std::cout << "hi\n";
    return 0;
}
```

```text
unused variable 'unused'
```

A fragment, deliberately not compiled.

```cpp
struct Point { int x; int y; };
```

A multi-file listing. Every file is written out, headers resolve through `-I.`, and
all translation units are linked in one command — so this only passes if the header
guard works and `point_add` really is defined somewhere.

```c run-files
/* ===== point.h ===== */
#ifndef POINT_H
#define POINT_H

typedef struct {
    int x;
    int y;
} Point;

Point point_add(Point a, Point b);

#endif

/* ===== point.c ===== */
#include "point.h"

Point point_add(Point a, Point b) {
    Point result = {a.x + b.x, a.y + b.y};
    return result;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "point.h"

int main(void) {
    Point a = {1, 2};
    Point b = {10, 20};
    Point sum = point_add(a, b);

    printf("sum = (%d, %d)\n", sum.x, sum.y);
    return 0;
}
```

```text
sum = (11, 22)
```

A multi-file listing whose `main` is the second translation unit, and which uses
`static` for internal linkage.

```c run-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

int double_it(int value);

#endif

/* ===== util.c ===== */
#include "util.h"

static int secret_base(void) {
    return 21;
}

int double_it(int value) {
    return value * 2 + secret_base() - 21;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "util.h"

int main(void) {
    printf("%d\n", double_it(4));
    return 0;
}
```

```text
8
```

Shell blocks. `sh run` executes the script and compares stdout with the `text` fence,
so a command transcript is a claim rather than prose.

```sh run
printf 'one\n'
printf '%s\n' "$((6 * 7))"
```

```text
one
42
```

`sh run-project` runs in a directory seeded with the multi-file listing above and
already built, so the shell can drive the program that listing produced.

```sh run-project
./prog
```

```text
8
```

A listing that carries its own Makefile. The harness runs `make` and then the `prog` it
produced, so the recipe itself is under test — a Makefile that forgets to link a
translation unit fails here with the linker's own message.

```c make-files
/* ===== util.h ===== */
#ifndef UTIL_H
#define UTIL_H

int twice(int value);

#endif

/* ===== util.c ===== */
#include "util.h"

int twice(int value) {
    return value * 2;
}

/* ===== main.c ===== */
#include <stdio.h>
#include "util.h"

int main(void) {
    printf("%d\n", twice(21));
    return 0;
}

/* ===== Makefile ===== */
CC = clang
CFLAGS = -std=c17 -Wall -Wextra -Werror

prog: main.o util.o
	$(CC) $(CFLAGS) -o prog main.o util.o

main.o: main.c util.h
	$(CC) $(CFLAGS) -c main.c

util.o: util.c util.h
	$(CC) $(CFLAGS) -c util.c

clean:
	rm -f prog main.o util.o
```

```text
42
```
