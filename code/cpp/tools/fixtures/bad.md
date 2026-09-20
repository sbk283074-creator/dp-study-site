---
chapter: 0
part: 0
title: Harness self-test — nine failures it MUST report
summary: This file must FAIL, with exactly nine failures. If it passes, the harness is blind.
minutes: 1
tags: [selftest, must-fail]
---

1. A `run` block whose documented output is wrong. Must be caught as a mismatch.

```cpp run
#include <iostream>

int main() {
    std::cout << "actual\n";
    return 0;
}
```

```text
documented-but-wrong
```

2. A `bad` block that is not actually bad — it compiles. Must be refused.

```cpp bad
int main() {
    int x = 5;
    return x - 5;
}
```

3. A `run` block that exits non-zero. Must be reported, not ignored.

```cpp run
#include <iostream>

int main() {
    std::cout << "before the crash\n";
    return 3;
}
```

```text
before the crash
```

4. A `run-san-catch` block that is actually fine — nothing for the sanitizer to find.

```cpp run-san-catch
#include <iostream>

int main() {
    std::cout << "all good\n";
    return 0;
}
```

5. A `run-san` block with undefined behaviour. UBSan reports it but the exit code stays 0,
   so a harness that only checked the exit code would pass this. It must not.

```cpp run-san
#include <iostream>
#include <climits>

int main() {
    int x = INT_MAX;
    x = x + 1;
    std::cout << x << "\n";
    return 0;
}
```

```text
-2147483648
```

6. A `bad` block that IS correctly rejected, but whose quoted diagnostic is invented. The
   block is genuinely bad and the build genuinely fails, so an exit-code-only check would
   wave it through — and the chapter would teach the reader to expect an error message that
   does not exist. Must be caught.

```cpp bad
int main() {
    int x = 5
    return 0;
}
```

```text
error: missing semicolon before 'return'
```

7. A `run-files` block whose files compile but do not LINK. Each translation unit is
   valid on its own, so a harness that compiled the files separately would see two
   successes; the missing definition only shows up at link time. Must be caught.

```c run-files
/* ===== helper.c ===== */
int helper(void) {
    return 1;
}

/* ===== main.c ===== */
int helper(void);
int missing(void);

int main(void) {
    return helper() + missing();
}
```

8. A `run-files` block with no banner, so there is no way to tell which file is which.
   Silently treating the whole block as one file would run the wrong experiment. Must be
   caught rather than guessed at.

```c run-files
#include <stdio.h>

int main(void) {
    printf("this is not a multi-file listing\n");
    return 0;
}
```

9. A `make-files` block whose Makefile builds something that does not link. Every file
   in the listing is correct C; the *recipe* is wrong. A harness that compiled the
   files itself would never see this, which is exactly why the Makefile has to be part
   of the example. Must be caught, and with the linker's message rather than a guess.

```c make-files
/* ===== util.h ===== */
int twice(int value);

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
prog: main.c
	clang -std=c17 -o prog main.c
```

```text
Undefined symbols
```

10. A shell block whose transcript is wrong. `sh run` compares stdout with the `text`
    fence, so a hand-written transcript that does not match the real output is caught.
    This is the case that motivated the directive: a quoted `make` message that the
    machine has never printed is exactly the sort of error prose hides.

```sh run
printf 'two\n'
```

```text
one
```
