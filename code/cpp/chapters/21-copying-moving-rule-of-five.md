---
chapter: 21
part: 4
title: Copying, Moving and the Rule of Five
summary: Stop the compiler's default copy from freeing the same pointer twice, write the deep copy and the move that make an owning type safe, and learn the rule of zero that means writing none of them.
minutes: 60
tags: [copy-constructor, copy-assignment, move-semantics, rvalue-reference, rule-of-three, rule-of-five, rule-of-zero, std-move, delete]
---

Chapter 20 ended with a warning: the `Buffer` class it taught would double-free if you ever copied it,
and the compiler would not say a word. This chapter is that bill coming due. It is also where C++ does
something no other mainstream language did at the time — it lets you say "this value is about to die,
so take its guts instead of duplicating them" — and that single idea is why `std::vector` can grow to a
million elements without copying a million elements. The mechanics are small: two constructors, two
assignment operators, and one cast. Getting the *rules* right is the part that takes practice.

## The compiler's copy is a member-wise copy

When you do not write a copy constructor, the compiler writes one for you, and it copies **each member**.
For an `int` that is exactly right. For a pointer it is catastrophic:

```cpp run-san-catch
#include <cstdio>
#include <cstdlib>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n), data_(static_cast<char *>(std::malloc(n))) {}
    ~Buffer() { std::free(data_); }

    char *data() const { return data_; }
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
    char *data_;
};

int main() {
    Buffer a(16);
    Buffer b = a;
    std::printf("two owners, one allocation\n");
    return 0;
}
```

```text
attempting double-free
```

The compiler's copy constructor copied `data_`, which is a pointer, so `a.data_` and `b.data_` hold the
**same address**. Nothing about that is a type error, which is why the compiler cannot warn you. The
program prints its line, `b` is destroyed and frees the block, then `a` is destroyed and frees the same
block again. AddressSanitizer catches it at the second `free` and shows you both destructor frames.

The general statement, which is worth memorising: **the compiler's default copy is correct exactly when
"copy every member" is the right meaning.** It is right for plain data. It is wrong for every type that
owns a resource — a pointer, a file handle, a socket, a lock.

## The rule of three

If a class needs a destructor, it almost certainly needs a copy constructor and a copy assignment
operator too, and if you write one of the three you should write all three. That is the **rule of
three**, and here is the complete version for `Buffer`:

```cpp run-san
#include <cstdio>
#include <cstdlib>
#include <cstring>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n), data_(static_cast<char *>(std::malloc(n))) {}

    Buffer(const Buffer &other)
        : n_(other.n_), data_(static_cast<char *>(std::malloc(other.n_))) {
        std::memcpy(data_, other.data_, n_);
    }

    Buffer &operator=(const Buffer &other) {
        if (this == &other) return *this;
        char *fresh = static_cast<char *>(std::malloc(other.n_));
        std::memcpy(fresh, other.data_, other.n_);
        std::free(data_);
        data_ = fresh;
        n_ = other.n_;
        return *this;
    }

    ~Buffer() { std::free(data_); }

    char *data() const { return data_; }
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
    char *data_;
};

int main() {
    Buffer a(16);
    std::memcpy(a.data(), "hello", 6);
    Buffer b = a;
    b.data()[0] = 'H';
    std::printf("a = %s\n", a.data());
    std::printf("b = %s\n", b.data());
    return 0;
}
```

```text
a = hello
b = Hello
```

That output *is* the proof. Changing `b` did not change `a`, so `b` owns its own block. Three details in
the code are load-bearing:

- **The copy constructor allocates before it copies.** It must give the new object its own memory; there
  is nothing to copy *into* otherwise.
- **`operator=` frees the old block only after the new one exists.** Allocate and copy first, then free,
  then swap in. Free first and an allocation failure would leave a dangling pointer behind.
- **The self-assignment guard `if (this == &other) return *this;`** handles `a = a`. Without it, that
  line frees `a`'s block and then copies from the freed memory — a use-after-free that only appears when
  someone writes a self-assignment, which they will.

Note the return type: `Buffer &`, returning `*this`. That is what makes `x = y = z;` work.

## Lvalues, rvalues, and what `std::move` really is

Every expression in C++ is either an **lvalue** (it names something with an address, like a variable) or
an **rvalue** (a temporary, or something about to expire). A function parameter declared `T &&` is an
**rvalue reference** and will only bind to an rvalue:

```cpp bad
class Traced {
public:
    Traced() = default;
    Traced(const Traced &) {}
    Traced(Traced &&) noexcept {}
};

static void take(Traced &&) {}

int main() {
    Traced a;
    take(a);
    return 0;
}
```

```text
expects an rvalue for 1st argument
```

`a` is a named variable, so it is an lvalue, and an rvalue reference refuses it. That is the entire
mechanism: **`T &&` means "the caller promises this object is disposable".**

`std::move` is how you make that promise, and despite the name it **moves nothing**. It is a cast — it
turns an lvalue into an rvalue reference and nothing else. Whether a move actually happens is decided by
which constructor or assignment operator the compiler then picks:

```cpp run
#include <cstdio>
#include <utility>

class Traced {
public:
    Traced() { std::printf("default\n"); }
    Traced(const Traced &) { std::printf("copy\n"); }
    Traced(Traced &&) noexcept { std::printf("move\n"); }
};

static void by_value(Traced) {}

int main() {
    Traced a;
    std::printf("-- by_value(a) --\n");
    by_value(a);
    std::printf("-- by_value(std::move(a)) --\n");
    by_value(std::move(a));
    return 0;
}
```

```text
default
-- by_value(a) --
copy
-- by_value(std::move(a)) --
move
```

The same call, the same parameter list, two different functions. `Traced` now has a **move
constructor** — a constructor taking `Traced &&` — and it is preferred over the copy constructor
whenever the argument is an rvalue.

## The move constructor, and the moved-from state

A move constructor does not copy anything. It **steals the pointer** and then puts the source into a
state where its destructor is harmless:

```cpp
Buffer(Buffer &&other) noexcept
    : n_(other.n_), data_(other.data_) {   // take the pointer, do not duplicate it
    other.n_ = 0;
    other.data_ = nullptr;                 // so other's destructor frees nothing
}
```

Those two lines in the body are the whole trick. After the move, `other` still exists — it is a valid
object with `size() == 0` — and it is only its *destructor* that would be a disaster if `data_` still
pointed at the block the new object now owns. Setting it to `nullptr` makes `std::free(nullptr)` the
no-op the C standard guarantees it to be.

`noexcept` on the move is not decoration. `std::vector` reallocates by moving its elements, but it will
only use the move constructor if it is guaranteed not to throw — because a throw halfway through a
reallocation would leave the container in a state it cannot repair. **Mark your move constructor and
move assignment `noexcept`, or the standard library will quietly copy instead.**

## The rule of five

Adding the two move operations to the rule of three gives the **rule of five**: destructor, copy
constructor, copy assignment, move constructor, move assignment. Here is the complete type, with each
operation announcing itself so you can watch which one runs:

```cpp run-san
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <utility>

class Buffer {
public:
    explicit Buffer(std::size_t n)
        : n_(n), data_(static_cast<char *>(std::malloc(n))) {
        std::printf("construct %zu\n", n_);
    }

    ~Buffer() {
        std::free(data_);
        std::printf("destroy   %zu\n", n_);
    }

    Buffer(const Buffer &other)
        : n_(other.n_), data_(static_cast<char *>(std::malloc(other.n_))) {
        std::memcpy(data_, other.data_, n_);
        std::printf("copy      %zu\n", n_);
    }

    Buffer &operator=(const Buffer &other) {
        if (this == &other) return *this;
        char *fresh = static_cast<char *>(std::malloc(other.n_));
        std::memcpy(fresh, other.data_, other.n_);
        std::free(data_);
        data_ = fresh;
        n_ = other.n_;
        std::printf("copy=     %zu\n", n_);
        return *this;
    }

    Buffer(Buffer &&other) noexcept
        : n_(other.n_), data_(other.data_) {
        other.n_ = 0;
        other.data_ = nullptr;
        std::printf("move      %zu\n", n_);
    }

    Buffer &operator=(Buffer &&other) noexcept {
        if (this == &other) return *this;
        std::free(data_);
        n_ = other.n_;
        data_ = other.data_;
        other.n_ = 0;
        other.data_ = nullptr;
        std::printf("move=     %zu\n", n_);
        return *this;
    }

    std::size_t size() const { return n_; }

private:
    std::size_t n_;
    char *data_;
};

int main() {
    Buffer a(16);
    std::printf("-- copy construction --\n");
    Buffer b = a;
    std::printf("-- move construction --\n");
    Buffer c = std::move(a);
    std::printf("-- after the move, a.size() = %zu --\n", a.size());
    std::printf("-- copy assignment --\n");
    b = c;
    std::printf("-- move assignment --\n");
    b = std::move(c);
    std::printf("-- after the move, c.size() = %zu --\n", c.size());
    return 0;
}
```

```text
construct 16
-- copy construction --
copy      16
-- move construction --
move      16
-- after the move, a.size() = 0 --
-- copy assignment --
copy=     16
-- move assignment --
move=     16
-- after the move, c.size() = 0 --
destroy   0
destroy   16
destroy   0
```

Read the three `destroy` lines at the end. They are `c`, `b` and `a` in reverse declaration order, and
two of them print `0` — those are the moved-from objects, whose `data_` is `nullptr` and whose `free`
does nothing. No leak, no double free, and the sanitized build agrees.

## The rule of zero

Everything above is a lot of code to write, and most of the time **you should not write any of it**:

```cpp run
#include <cstdio>
#include <string>
#include <utility>
#include <vector>

class Report {
public:
    Report(std::string title, std::vector<std::string> lines)
        : title_(std::move(title)), lines_(std::move(lines)) {}

    std::size_t size() const { return lines_.size(); }
    const std::string &title() const { return title_; }

private:
    std::string title_;
    std::vector<std::string> lines_;
};

int main() {
    Report a("build", {"one", "two", "three"});
    std::printf("a: %s, %zu lines\n", a.title().c_str(), a.size());

    Report b = a;
    std::printf("b: %s, %zu lines\n", b.title().c_str(), b.size());

    Report c = std::move(a);
    std::printf("c: %s, %zu lines\n", c.title().c_str(), c.size());
    std::printf("a after the move: %zu lines\n", a.size());
    return 0;
}
```

```text
a: build, 3 lines
b: build, 3 lines
c: build, 3 lines
a after the move: 0 lines
```

`Report` declares no destructor, no copy constructor, no copy assignment, no move constructor and no
move assignment. And yet: `Report b = a;` produced a genuinely independent copy, `std::move` emptied the
source, and there is no leak anywhere, because `std::string` and `std::vector` are themselves
rule-of-five types. The compiler generated `Report`'s copy by copying `std::string` and `std::vector`,
and both of those know how to copy and move themselves.

That is the **rule of zero**: **write no destructor, no copy and no move if you can put the ownership
inside a member that already handles it.** `Report` owns memory — through a `std::string` and a
`std::vector` — and it did not write a line of ownership code. Compare it to `Buffer`, which had to
write five functions because it held a raw `char *`. The lesson is not "the rule of five is hard"; it is
**"avoid holding a raw owning pointer and the rule of five never applies to you."**

## Forbidding copying

Sometimes the right answer is neither copy nor move: a class that owns a unique resource, like a socket
or a file lock, must not be copyable at all. Say so explicitly with `= delete`:

```cpp bad
#include <cstddef>
#include <cstdio>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n) {}
    Buffer(const Buffer &) = delete;
    Buffer &operator=(const Buffer &) = delete;
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
};

int main() {
    Buffer a(16);
    std::printf("%zu\n", a.size());
    Buffer b = a;
    (void)b;
    return 0;
}
```

```text
call to deleted constructor of 'Buffer'
```

The compiler's message is precise: `'Buffer' has been explicitly marked deleted here`. `= delete` is
better than "just don't write a copy constructor", because the default one would otherwise be generated
and would compile. Deleting it makes the mistake a compile error at the call site, which is where you
want to hear about it.

:::scenario I wrote no copy or move code and it still works

A new engineer is asked to review a class that accumulates build results. They open the file expecting
to check five special member functions and find this:

```cpp
class BuildLog {
public:
    BuildLog(std::string name, std::vector<std::string> entries)
        : name_(std::move(name)), entries_(std::move(entries)) {}

    void add(std::string entry) { entries_.push_back(std::move(entry)); }

    std::size_t count() const { return entries_.size(); }
    const std::string &name() const { return name_; }

private:
    std::string name_;
    std::vector<std::string> entries_;
};
```

Their first instinct is that the class is incomplete — where is the destructor? Where is the copy
constructor? The answer is that both are correct *by construction*:

- The **destructor** is generated and destroys `name_` then `entries_`, each of which frees whatever it
  owns. Nothing else in the class owns anything.
- The **copy constructor** is generated and copies `name_` and `entries_`. `std::string`'s copy
  allocates its own buffer; `std::vector`'s copy allocates its own array and copies each element. So the
  copy is deep, which is what a reviewer would have had to verify line by line if the class held a
  `char *`.
- The **move constructor** is generated and moves both members, which is a pointer swap per member. It
  is also generated `noexcept`, because `std::string` and `std::vector` have `noexcept` moves — which
  means `std::vector<BuildLog>` will reallocate by moving, not copying.

The one thing the reviewer *should* check is that no raw pointer or raw handle sneaked in. Add a
`std::FILE *` member and every guarantee above evaporates: the generated copy would duplicate the
handle and the generated destructor would close it twice. The review question is not "are the five
special members right?" but **"does this class own anything that is not already an owning member?"** If
the answer is no, the compiler's generated set is the right set, and writing your own can only make it
worse.

:::

:::pitfall The destructor you wrote silently deleted the move constructor

The compiler only generates a move constructor if you have not declared a destructor, a copy
constructor, or a copy assignment operator. Write any one of them and the implicit move **disappears**,
with no warning. Your type silently goes back to copying:

```cpp run
#include <cstdio>
#include <utility>

class Traced {
public:
    Traced() { std::printf("default\n"); }
    ~Traced() { std::printf("destroy\n"); }
    Traced(const Traced &) { std::printf("copy\n"); }
};

static void by_value(Traced) {}

int main() {
    Traced a;
    std::printf("-- by_value(std::move(a)) --\n");
    by_value(std::move(a));
    return 0;
}
```

```text
default
-- by_value(std::move(a)) --
copy
destroy
destroy
```

`std::move` was called, and the output says `copy`. The destructor is the only difference from the
earlier `Traced`, and its presence is what suppressed the move constructor. Adding one line brings the
move back:

```cpp
Traced(Traced &&) noexcept { std::printf("move\n"); }
```

This is the most common reason a type is slower than its author expects, and it is invisible unless you
are looking for it. If you must write a destructor, write the move too — or better, hold the resource in
a member that already handles it and write neither. Also note that `std::move` on a **`const`** object
cannot move anything either, because the move constructor takes a non-const `Traced &&`: the compiler
silently falls back to the copy constructor. `const` and moving are mutually exclusive.

:::

## Key takeaways

- The compiler's default copy copies each member; that is correct for plain data and wrong for any type
  that owns a resource, where it produces two owners of one allocation.
- The rule of three: if you write a destructor, write the copy constructor and copy assignment too.
- A copy constructor allocates its own memory before copying, and `operator=` allocates the new block
  before freeing the old one, with a `if (this == &other) return *this;` guard for self-assignment.
- An rvalue reference (`T &&`) only binds to a disposable value, which is why `take(a)` on a named
  variable is an error and `take(std::move(a))` is not.
- `std::move` moves nothing — it is a cast to an rvalue reference. The move constructor and move
  assignment operator are what actually transfer ownership.
- A move leaves the source valid but empty; setting the stolen pointer to `nullptr` is what makes the
  source's destructor harmless.
- Mark move operations `noexcept`, or `std::vector` will copy instead of move when it reallocates.
- The rule of zero: put ownership in a member that already handles it (`std::string`, `std::vector`, and
  in Chapter 22 `std::unique_ptr`) and write no destructor, no copy and no move at all.
- Declaring a destructor, a copy constructor or a copy assignment operator **suppresses** the implicit
  move constructor — a silent performance bug with no diagnostic.

## Practice

- [ ] Fix the double-free from the start of the chapter by writing a deep copy constructor for
  `Buffer`, and prove the copy is independent by modifying one buffer and printing both.
- [ ] Take the `Buffer` from Exercise 1 and add `Buffer(const Buffer &) = delete;` plus a matching
  deleted assignment. Show the compiler rejecting `Buffer b = a;`.
- [ ] Write a move constructor for `Buffer` that leaves the source empty, and print the source's
  `size()` before and after the move.
- [ ] Write a class with a copy constructor and a move constructor that each print which one ran. Move
  a **`const`** instance of it and explain the output in one sentence.
- [ ] Write a class holding a `std::string` and a `std::vector<int>` with **no** destructor, copy or
  move operations. Show that it copies deeply and that moving it empties the source.
- [ ] Write a class with a destructor and a copy constructor, show that `std::move` on it still copies,
  then add the move constructor and show the output change.

## Solutions

:::solution Exercise 1

```cpp run-san
#include <cstdio>
#include <cstdlib>
#include <cstring>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n), data_(static_cast<char *>(std::malloc(n))) {}

    Buffer(const Buffer &other)
        : n_(other.n_), data_(static_cast<char *>(std::malloc(other.n_))) {
        std::memcpy(data_, other.data_, n_);
    }

    ~Buffer() { std::free(data_); }

    char *data() const { return data_; }
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
    char *data_;
};

int main() {
    Buffer a(16);
    std::memcpy(a.data(), "hello", 6);
    Buffer b = a;
    b.data()[0] = 'H';
    std::printf("a = %s\n", a.data());
    std::printf("b = %s\n", b.data());
    return 0;
}
```

```text
a = hello
b = Hello
```

The copy constructor allocates `other.n_` bytes of its own before copying into them, so `b` never shares
`a`'s block. The proof is the output: writing `'H'` into `b` left `a` untouched, and the sanitized build
reports no double free. Note that this class still has no assignment operator — `b = a;` would use the
generated one and reintroduce the bug, which is the reason the rule of three insists on all three.

:::

:::solution Exercise 2

```cpp bad
#include <cstddef>
#include <cstdio>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n) {}
    Buffer(const Buffer &) = delete;
    Buffer &operator=(const Buffer &) = delete;
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
};

int main() {
    Buffer a(16);
    std::printf("%zu\n", a.size());
    Buffer b = a;
    (void)b;
    return 0;
}
```

```text
call to deleted constructor of 'Buffer'
```

The error arrives at the *call site* rather than inside the class, which is what you want: the person who
wrote `Buffer b = a;` gets told immediately. Deleting the assignment operator as well matters, because
deleting only the constructor would leave `b = a;` compiling through the generated assignment.

:::

:::solution Exercise 3

```cpp run-san
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <utility>

class Buffer {
public:
    explicit Buffer(std::size_t n) : n_(n), data_(static_cast<char *>(std::malloc(n))) {
        std::memcpy(data_, "payload", 8);
    }

    Buffer(Buffer &&other) noexcept : n_(other.n_), data_(other.data_) {
        other.n_ = 0;
        other.data_ = nullptr;
    }

    ~Buffer() { std::free(data_); }

    char *data() const { return data_; }
    std::size_t size() const { return n_; }

private:
    std::size_t n_;
    char *data_;
};

int main() {
    Buffer a(16);
    std::printf("before: a.size() = %zu, a.data() = %s\n", a.size(), a.data());
    Buffer b = std::move(a);
    std::printf("after:  a.size() = %zu, b.size() = %zu, b.data() = %s\n",
                a.size(), b.size(), b.data());
    return 0;
}
```

```text
before: a.size() = 16, a.data() = payload
after:  a.size() = 0, b.size() = 16, b.data() = payload
```

`b` took the pointer, so it owns the payload without any allocation happening. `a` reports size `0` and
its `data_` is `nullptr` — a valid, empty object whose destructor will call `free(nullptr)`, which does
nothing. The sanitized build confirms there is no leak and no double free.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>
#include <utility>

class Traced {
public:
    Traced() = default;
    Traced(const Traced &) { std::printf("copy\n"); }
    Traced(Traced &&) noexcept { std::printf("move\n"); }
};

int main() {
    const Traced c;
    Traced x = std::move(c);
    (void)x;
    return 0;
}
```

```text
copy
```

`std::move(c)` produces a `const Traced &&`, and the move constructor takes a non-const `Traced &&`, so
it cannot bind. The copy constructor takes `const Traced &`, which accepts anything, so that is the one
the compiler picks. A `const` object is never movable, and no diagnostic is issued — the cast succeeded
and the overload resolution just chose differently than you intended.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>
#include <string>
#include <utility>
#include <vector>

class Shelf {
public:
    Shelf(std::string label, std::vector<int> items)
        : label_(std::move(label)), items_(std::move(items)) {}

    std::size_t count() const { return items_.size(); }
    const std::string &label() const { return label_; }
    int first() const { return items_.front(); }

private:
    std::string label_;
    std::vector<int> items_;
};

int main() {
    Shelf a("bolts", {4, 8, 15});
    std::printf("a: %s, %zu items, first = %d\n", a.label().c_str(), a.count(), a.first());

    Shelf b = a;
    std::printf("b: %s, %zu items, first = %d\n", b.label().c_str(), b.count(), b.first());

    Shelf c = std::move(a);
    std::printf("c: %s, %zu items\n", c.label().c_str(), c.count());
    std::printf("a after the move: %zu items\n", a.count());
    return 0;
}
```

```text
a: bolts, 3 items, first = 4
b: bolts, 3 items, first = 4
c: bolts, 3 items
a after the move: 0 items
```

`Shelf` writes no special member functions, and the compiler's generated ones are all correct because
`std::string` and `std::vector` own their own memory. `b` is a real copy — `std::vector`'s copy
constructor allocated a new array — and `c` is a real move, which is why `a` is left empty. This is the
rule of zero, and it is the shape most of your classes should have.

:::

:::solution Exercise 6

```cpp run
#include <cstdio>
#include <utility>

class Traced {
public:
    Traced() { std::printf("default\n"); }
    ~Traced() { std::printf("destroy\n"); }
    Traced(const Traced &) { std::printf("copy\n"); }
};

static void by_value(Traced) {}

int main() {
    Traced a;
    std::printf("-- by_value(std::move(a)) --\n");
    by_value(std::move(a));
    return 0;
}
```

```text
default
-- by_value(std::move(a)) --
copy
destroy
destroy
```

Declaring the destructor (and the copy constructor) suppressed the implicit move constructor, so the
only candidate left for `std::move(a)` was the copy. Adding `Traced(Traced &&) noexcept { ... }` restores
it and the same program prints `move` instead — which is the one-line change that fixes the performance
bug, and the reason the rule of five exists as a rule rather than as a set of unrelated guidelines.

:::
