---
chapter: 0
part: 0
title: Harness self-test — five failures it MUST report
summary: This file must FAIL, with exactly five failures. If it passes, the harness is blind.
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
