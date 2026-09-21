---
chapter: 22
part: 4
title: Why C++
summary: See what C++ adds on top of C — code that runs automatically when a scope ends, strings and vectors that manage their own memory — and the three places the compiler stops accepting what C allowed.
minutes: 50
tags: [c++, raii, destructor, string, vector, namespace, name-mangling, vtable]
---

Every function in Part III had a cleanup path. `handle` in Chapter 21 had to free the body, close the
file and close the connection on the way out, and the only reason it was correct is that every route
out of it went through one place. That is the problem C++ was invented to solve, and almost everything
else in the language follows from the answer: **a destructor runs when an object goes out of scope**,
so releasing a resource stops being something you have to remember and becomes something the compiler
does for you. This chapter is the transition. The syntax is the syntax you already know, the C library
is still underneath, and the interesting part is the short list of things C++ refuses to let you do.

## The same source, two compilers

`clang++` takes the same flags as `clang`: the same `-c`, the same `-o`, the same headers, the same
linker, the same object files. A lot of what you wrote in Parts I and II compiles as C++ unchanged —
the C library is still there, moved under `std::`:

```cpp run
#include <cstdio>

int main() {
    int total = 0;
    for (int i = 1; i <= 5; i++) total += i;
    std::printf("%d\n", total);
    return 0;
}
```

```text
15
```

The differences are not in what C++ accepts but in what it refuses. C converts `void *` to any pointer
type silently, which is why `malloc` needs no cast — and why a mismatched allocation can go unnoticed:

```c run
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    void *raw = malloc(4);
    int *p = raw;              /* C converts for you, silently */
    *p = 7;
    printf("%d\n", *p);
    free(raw);
    return 0;
}
```

```text
7
```

C++ refuses the same line. Nothing else about the program changes:

```cpp bad
#include <cstdlib>

int main() {
    void *raw = std::malloc(4);
    int *p = raw;              /* no implicit conversion in C++ */
    *p = 7;
    std::free(raw);
    return 0;
}
```

```text
cannot initialize a variable of type 'int *' with an lvalue of type 'void *'
```

That is not pedantry. The silent conversion is exactly what hides a wrong-sized allocation: if that
`malloc(4)` had been `malloc(2)`, C would have compiled it without a murmur and you would have written
two bytes past the end. In C++ you write `static_cast<int *>(raw)`, and the cast is a place a reviewer
can see. **C++ makes you say what you mean at the points where getting it wrong is expensive.**

## Where C is silent and C++ is not

The same pattern shows up with string literals, and here the contrast is sharper because C says
nothing at all:

```c run
#include <stdio.h>

int main(void) {
    char *p = "hello";         /* C: no diagnostic at all */
    printf("%s\n", p);
    return 0;
}
```

```text
hello
```

```cpp warn
#include <cstdio>

int main() {
    char *p = "hello";         /* C++: you are warned, but it still builds */
    std::printf("%s\n", p);
    return 0;
}
```

```text
ISO C++11 does not allow conversion from string literal to 'char *'
```

Note what the warning is *not*: it is not an error, and the program still builds and runs. The literal
lives in read-only memory, so writing through `p` is undefined behaviour that C++ is warning you
about and C is not. The habit to take away is `const char *`, which is correct in both languages and
silences this entirely.

## The linker tells you which language you are in

Compiling is the same; linking is where C++ stops looking like C. Define the same function twice in
two files and the linker complains — but read the name it complains about:

```cpp bad-files
/* ===== first.cpp ===== */
int twice(int value) { return value * 2; }

/* ===== second.cpp ===== */
int twice(int value) { return value + value; }

int main() { return twice(3) == 6 ? 0 : 1; }
```

```text
duplicate symbol 'twice(int)'
```

In C that same mistake reads `duplicate symbol '_twice'` — a leading underscore and nothing else.
C++ **mangles** names: the symbol the linker sees encodes the parameter types, so `twice(int)` and
`twice(double)` are different symbols and can coexist. That is not a curiosity, it is the mechanism
that makes overloading work in Chapter 23. What you see above is the linker demangling the name back
for you, which is a small kindness you will be grateful for the first time you meet a page of them.

## Strings that grow

Now the part that actually saves you work. In C, a string that can grow is a `malloc`, a `realloc`, a
length variable, an error check after each, and a `free` on every path out. In C++ it is a type:

```cpp run
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> names = {"ana", "bo", "cy"};
    names.push_back("di");

    std::string joined;
    for (const std::string &name : names) {
        if (!joined.empty()) joined += ", ";
        joined += name;
    }
    std::cout << joined << "\n";
    std::cout << "length = " << joined.size() << "\n";
    return 0;
}
```

```text
ana, bo, cy, di
length = 15
```

There is no length to track, no capacity to check, no `free`. `joined` grows as many times as it needs
to and releases its buffer when it goes out of scope at the end of `main`. `names` does the same for
its array of strings. The `&` in `const std::string &name` is a **reference** — Chapter 23's subject —
and for now the useful reading is "do not copy this element just to look at it".

## Cleanup that cannot be forgotten

Here is the idea the whole language is built around. A `struct` in C++ can have a **destructor**: a
function the compiler calls when the object's lifetime ends, whatever ends it.

```cpp run
#include <cstdio>

struct Connection {
    int fd;
    Connection(int f) : fd(f) { std::printf("open %d\n", fd); }
    ~Connection()            { std::printf("close %d\n", fd); }
};

static int handle(int ok) {
    Connection c(7);
    if (!ok) {
        std::printf("failing early\n");
        return -1;
    }
    std::printf("doing work\n");
    return 0;
}

int main() {
    handle(1);
    handle(0);
    return 0;
}
```

```text
open 7
doing work
close 7
open 7
failing early
close 7
```

`close 7` appears on **both** paths, including the one that returned early from the middle of the
function. Nobody wrote a `goto cleanup`, nobody duplicated a `close`, and nobody could forget one —
the second `handle(0)` call demonstrates the case that breaks C code, and it is correct here for free.

This is **RAII**: resource acquisition is initialisation. The constructor acquires, the destructor
releases, and the language guarantees the second one runs. Chapter 21's `handle` had to free the body,
`fclose` the file and `close` the connection on every return; written this way, all three become
objects whose destructors run on the way out, and the cleanup path stops existing as a thing you can
get wrong. Part IV is largely the study of what that idea does to the rest of the language.

## What it costs

C++'s reputation for being heavy is partly deserved and mostly about specific features you opt into.
Sizes on this target, `arm64` macOS with Apple clang:

```cpp run
#include <cstdio>
#include <string>
#include <vector>

struct Empty      { };
struct Plain      { int a; int b; };
struct HasVirtual { int a; int b; virtual ~HasVirtual() {} };

int main() {
    std::printf("Empty            = %zu\n", sizeof(Empty));
    std::printf("Plain            = %zu\n", sizeof(Plain));
    std::printf("HasVirtual       = %zu\n", sizeof(HasVirtual));
    std::printf("std::string      = %zu\n", sizeof(std::string));
    std::printf("std::vector<int> = %zu\n", sizeof(std::vector<int>));
    return 0;
}
```

```text
Empty            = 1
Plain            = 8
HasVirtual       = 16
std::string      = 24
std::vector<int> = 24
```

Three things to read off that. An empty struct is **1** byte, not 0, because two distinct objects must
have distinct addresses. Adding one `virtual` function grew the struct from 8 bytes to 16 — every
object carries a hidden pointer to its table of virtual functions, and that is the price of Chapter
23's polymorphism, paid per object. And `std::string` is 24 bytes: not a pointer to a heap buffer but
a small struct that can hold short strings inline. The container itself is cheap; what it *owns* is
elsewhere.

## C++ does not make memory errors go away

It is worth being clear about this early, because "modern C++" gets sold as if it were. `new` and
`delete` are manual, and the sanitizer from Part II still applies:

```cpp run-san-catch
int main() {
    int *p = new int(1);
    delete p;
    delete p;                  /* undefined behaviour */
    return 0;
}
```

```text
attempting double-free
```

Nothing about C++ prevents that. What C++ adds is the ability to write code where you never type
`new` at all — Chapter 26's `std::unique_ptr` is the standard answer, and it is the reason the rest of
this part pushes you away from raw owning pointers rather than toward them.

## Namespaces, and one habit to avoid

Everything in the standard library lives in a namespace called `std`, which is why every example above
says `std::cout` and not `cout`. Namespaces exist so that two libraries can both define `distance`
without colliding. You will see `using namespace std;` at the top of a lot of teaching code, and the
reason to avoid it is not style:

```cpp bad
#include <cstddef>

using namespace std;

typedef unsigned char byte;

int main() {
    byte flags = 0;
    return flags;
}
```

```text
reference to 'byte' is ambiguous
```

`byte` used to be a name nobody had. C++17 put `std::byte` in the standard library, and this program —
which compiled fine before — stopped compiling, with an error that points at a `typedef` you wrote
years ago. `using namespace std;` at file scope means every name the standard library gains in future
becomes a potential collision in your code. Write `std::` and the question never arises.

:::scenario The port that leaked on the error path

A team is moving a C service to C++ a file at a time, and the first candidate is a function shaped
exactly like Chapter 21's `handle`: it opens a file, allocates a buffer, and has four `return`
statements. The first translation is mechanical — `malloc` becomes `new`, `free` becomes `delete`, and
each of the four returns keeps its own cleanup:

```cpp
int handle(const char *path) {
    FILE *f = std::fopen(path, "rb");
    if (!f) return -1;

    char *buf = new char[4096];
    if (!read_into(f, buf)) {
        std::fclose(f);
        delete[] buf;
        return -2;
    }
    if (!validate(buf)) {
        std::fclose(f);
        delete[] buf;
        return -3;
    }

    std::fclose(f);
    delete[] buf;
    return 0;
}
```

It works, and it is worse than the C it replaced: there are now three copies of the cleanup and four
places to add a fifth. The code review should reject it on exactly that ground.

:::solution Give each resource an owner

Introduce one small type per resource, with the release in the destructor. Neither type knows anything
about `handle`; they only know how to release themselves.

```cpp
struct File {
    FILE *f;
    explicit File(const char *path) : f(std::fopen(path, "rb")) {}
    ~File() { if (f) std::fclose(f); }
    bool ok() const { return f != nullptr; }
};

struct Buffer {
    char *data;
    explicit Buffer(std::size_t n) : data(new char[n]) {}
    ~Buffer() { delete[] data; }
};

int handle(const char *path) {
    File file(path);
    if (!file.ok()) return -1;

    Buffer buf(4096);
    if (!read_into(file.f, buf.data)) return -2;
    if (!validate(buf.data))          return -3;
    return 0;
}
```

Every early return now releases both resources, and the two lines of cleanup that were repeated three
times are gone. The next resource added to this function costs one line at the top and nothing
anywhere else — which is the property that makes the rewrite worth doing at all.

:::

:::pitfall `new[]` and `delete` are not interchangeable

`new int[3]` allocates an array and must be released with `delete[]`. Using plain `delete` is undefined
behaviour. You do not have to remember this, because the compiler tells you:

```cpp warn
int main() {
    int *a = new int[3];
    a[0] = 1;
    delete a;
    return 0;
}
```

```text
did you mean 'delete[]'?
```

Read that warning and take the second lesson with it: **the compiler is the only thing that will catch
this here.** AddressSanitizer's `alloc-dealloc-mismatch` check is disabled by default on this platform,
so the same program under `-fsanitize=address` runs silently and exits `0`. A sanitizer that reports
nothing has not proved anything — it has only failed to notice. Compiler warnings and sanitizers catch
different mistakes, and this one is a compiler-warning mistake.

:::

## Key takeaways

- A **destructor** runs when an object's lifetime ends, including on an early `return`, and that is
  the mechanism the rest of C++ is built on.
- **RAII** means one object owns one resource: the constructor acquires it, the destructor releases
  it, and cleanup stops being a path you can get wrong.
- C++ **refuses** implicit `void *` conversions and warns about `char *p = "literal"`; C accepts both
  silently. The refusals mark the places where a mistake is expensive.
- C++ **mangles** names, so the linker reports `duplicate symbol 'twice(int)'` where C reports
  `_twice`. The parameter types are part of the symbol, which is what makes overloading possible.
- `std::string` and `std::vector` manage their own memory: no length variable, no `realloc`, no `free`.
- `sizeof(Empty) == 1`; one `virtual` function adds a hidden pointer to every object; `std::string` is
  24 bytes on this target and owns a buffer somewhere else.
- `using namespace std;` at file scope makes your code depend on names the standard library has not
  invented yet. Write `std::`.
- C++ does not remove memory errors. It gives you the tools to avoid typing `new` — Chapter 26 is
  where those tools arrive.

## Practice

- [ ] Compile the `void *` example from this chapter as C and as C++. Add `static_cast<int *>` and
      confirm the C++ version now builds, then explain in one sentence what the cast changed.
- [ ] Write a C++ program that reads a line with `std::getline` into a `std::string`, prints its
      length, and appends it to a `std::vector<std::string>` in a loop. Run it twice with different
      input and check that no cleanup code was needed.
- [ ] Give the `Connection` struct a second constructor that takes no argument and opens a
      fixed descriptor, then add a member function `bool is_open() const`. Print the result on both
      paths of `handle`.
- [ ] Make a struct with a destructor that prints its name, create three of them in one scope, and
      predict the order the destructors run in before you run it. Then explain the order.
- [ ] Write a program that leaks a `new int[100]` and run it under `-fsanitize=address`. Note what
      the sanitizer does *not* tell you on this platform, and say which tool would have.
- [ ] Take the `File` and `Buffer` types from the scenario and add a `Buffer` member function
      `std::size_t size() const`. Then add a third resource of your own and confirm no existing
      `return` statement needed changing.

## Solutions

:::solution Exercise 1

Adding the cast makes the conversion explicit, which is the only thing C++ objected to:

```cpp bad
int main() {
    void *raw = nullptr;
    int *p = raw;
    return p == nullptr ? 0 : 1;
}
```

```text
cannot initialize a variable of type 'int *' with an lvalue of type 'void *'
```

```cpp run
#include <cstdlib>

int main() {
    void *raw = std::malloc(4);
    int *p = static_cast<int *>(raw);
    *p = 7;
    std::free(raw);
    return 0;
}
```

The cast changed nothing at run time — it is the same bytes. What it changed is that the conversion is
now written down at one place, so a reader can see that a `void *` became an `int *` and ask whether
the size was right. That question is the whole point.

:::

:::solution Exercise 2

Reading from `std::cin` is the real version, but it cannot be shown with a fixed output — so this
block feeds the same loop from a string instead, which is the same code with the source of the lines
changed:

```cpp run
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main() {
    std::istringstream input("hello\nworld\n");
    std::vector<std::string> lines;
    std::string line;

    while (std::getline(input, line)) {
        std::cout << line.size() << "\n";
        lines.push_back(line);
    }
    std::cout << "lines = " << lines.size() << "\n";
    return 0;
}
```

```text
5
5
lines = 2
```

Swap `input` for `std::cin` and it reads the terminal instead; nothing else changes, because both are
input streams. Note what is absent either way: no buffer to size, no `strlen`, no capacity to check
before the second `push_back`, and no `free`. `line` and `lines` release their buffers when `main`
returns.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>

struct Connection {
    int fd;
    explicit Connection(int f) : fd(f) {}
    Connection() : fd(3) {}
    ~Connection() { std::printf("close %d\n", fd); }
    bool is_open() const { return fd >= 0; }
};

int main() {
    Connection a;
    Connection b(7);
    std::printf("a open: %d\n", a.is_open());
    std::printf("b open: %d\n", b.is_open());
    return 0;
}
```

```text
a open: 1
b open: 1
close 7
close 3
```

Two constructors with different parameter lists is **overloading**, which Chapter 23 covers properly.
The destructors run in reverse order of construction, which is the answer to Exercise 4 as well.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>

struct Tracer {
    const char *name;
    explicit Tracer(const char *n) : name(n) { std::printf("construct %s\n", name); }
    ~Tracer() { std::printf("destroy %s\n", name); }
};

int main() {
    Tracer first("first");
    Tracer second("second");
    Tracer third("third");
    std::printf("end of scope\n");
    return 0;
}
```

```text
construct first
construct second
construct third
end of scope
destroy third
destroy second
destroy first
```

Destructors run in **reverse order of construction** — last in, first out. The reason is that a later
object may depend on an earlier one, so the reverse order is the one that is always safe: the thing
built on top is destroyed first.

:::

:::solution Exercise 5

```cpp run-san-leak
int main() {
    int *leaked = new int[100];
    leaked[0] = 1;
    return leaked[0] - 1;
}
```

```text
leak
```

On this platform the sanitizer reports nothing at all: Apple's clang ships no LeakSanitizer, so leak
detection is unavailable rather than merely quiet. The tool that would have found it is `valgrind`
(absent here) or an ASan build on Linux. The honest conclusion is the same as the pitfall's: **a clean
sanitizer run is not evidence that there is no leak.**

:::

:::solution Exercise 6

```cpp run
#include <cstdio>
#include <cstring>

struct File {
    FILE *f;
    explicit File(const char *path) : f(std::fopen(path, "rb")) {}
    ~File() { if (f) std::fclose(f); }
    bool ok() const { return f != nullptr; }
};

struct Buffer {
    char *data;
    std::size_t len;
    explicit Buffer(std::size_t n) : data(new char[n]), len(n) {}
    ~Buffer() { delete[] data; }
    std::size_t size() const { return len; }
};

int main() {
    Buffer buf(4096);
    std::printf("size = %zu\n", buf.size());
    return 0;
}
```

```text
size = 4096
```

The third resource would be one more type with a destructor and one more line in the function that
uses it. No `return` statement changes, because none of them ever named the resources being released —
that is the property the rewrite was for.

:::
