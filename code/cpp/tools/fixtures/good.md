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
