---
chapter: 26
part: 4
title: Smart Pointers
summary: Use unique_ptr, shared_ptr and weak_ptr to get the rule of five for free, decide who owns what on purpose, and stop writing delete entirely.
minutes: 60
tags: [unique_ptr, shared_ptr, weak_ptr, make_unique, make_shared, ownership, custom-deleter, raii]
---

Chapter 25 ended with the most useful piece of advice in this part of the book: put ownership in a
member that already handles it, and the rule of five never applies to you. That advice is only worth
anything if such members exist — and for dynamically allocated objects they are `std::unique_ptr` and
`std::shared_ptr`. Between them they cover almost every case where C code would call `malloc` and
`free`. The interesting part is not the syntax, which is small; it is the **ownership question** they
force you to answer: for each pointer in your program, who is responsible for destroying the thing it
points at, and is that exactly one party, many parties, or nobody?

## The question that raw pointers do not ask

A raw pointer `T *` says nothing about ownership. In Chapter 24's `Buffer` the member `char *data_` was
an owner — the destructor had to free it. In the `Server` below, a member will be a raw pointer that
must **not** be freed. Both look identical at the type level, and that is the whole problem: the
compiler cannot tell them apart, so it cannot help you. Smart pointers put the answer in the type.

There are three answers, and they map onto the three standard pointer types:

| Question | Answer | Type |
|---|---|---|
| Does exactly one thing own this, and destroy it at scope end? | yes | `std::unique_ptr<T>` |
| Do several things share ownership, destroyed when the last one goes? | yes | `std::shared_ptr<T>` |
| Does this only *observe* something owned elsewhere? | no | `T *` or `std::weak_ptr<T>` |

## unique_ptr: exactly one owner

```cpp run-san
#include <cstdio>
#include <memory>

int main() {
    auto p = std::make_unique<int>(42);
    std::printf("*p = %d\n", *p);
    *p = 7;
    std::printf("*p = %d\n", *p);
    return 0;
}
```

```text
*p = 42
*p = 7
```

There is no `delete` in that program, and the sanitized build reports nothing, which means the `int`
was freed. `std::make_unique<int>(42)` allocates an `int` and hands you an object whose destructor
calls `delete`. It behaves like a pointer — `*p` dereferences it, `p.get()` gives the raw address — but
it is a value with a destructor, so it obeys the same rules as `Buffer`.

Prefer `make_unique` to writing `new` yourself. `std::unique_ptr<int> p(new int(42));` means the same
thing, but it names the type twice and it creates a window in which the `new` has happened and no owner
exists yet. `make_unique` cannot be got wrong.

The defining property of `unique_ptr` is that it is **move-only**, and the compiler enforces it:

```cpp bad
#include <memory>

int main() {
    auto a = std::make_unique<int>(1);
    auto b = a;
    (void)b;
    return 0;
}
```

```text
call to implicitly-deleted copy constructor of 'unique_ptr<int>'
```

That message is the type doing its job. If `unique_ptr` were copyable you would get exactly the double
free from Chapter 25 — two owners, one allocation. Instead, the only way to hand the object to someone
else is to give up your claim to it:

```cpp run
#include <cstdio>
#include <memory>
#include <utility>

int main() {
    auto a = std::make_unique<int>(5);
    auto b = std::move(a);
    std::printf("a is %s\n", a ? "set" : "empty");
    std::printf("b is %s, *b = %d\n", b ? "set" : "empty", *b);
    return 0;
}
```

```text
a is empty
b is set, *b = 5
```

`std::move(a)` transfers the pointer and sets `a` to null, so `a` tests false. This is the same
moved-from convention from Chapter 25, and it is why a `unique_ptr` in a boolean context tells you
whether it still owns anything. **Moving a `unique_ptr` is how you express "ownership passes to you".**
A function returning a `unique_ptr` is a function saying "I made this; it is yours now" — a sentence C
can only express in a comment.

`unique_ptr` also handles arrays, using `delete[]` instead of `delete` for you:

```cpp run
#include <cstdio>
#include <memory>

int main() {
    auto buf = std::make_unique<char[]>(16);
    for (int i = 0; i < 15; i++) buf[i] = (char)('a' + (i % 26));
    buf[15] = '\0';
    std::printf("buf = %s\n", buf.get());
    return 0;
}
```

```text
buf = abcdefghijklmno
```

Note `std::make_unique<char[]>(16)` — the `[]` in the type is what selects the array form, and it is the
reason this cannot be the `new[]`/`delete` mismatch from Chapter 22's pitfall.

## shared_ptr: several owners, one object

When ownership genuinely is shared — a cache and a worker both holding a connection, say — the last one
to let go must destroy it, and only the last one. That is what `std::shared_ptr` does, with a reference
count stored in a **control block** next to the object:

```cpp run
#include <cstdio>
#include <memory>

int main() {
    auto a = std::make_shared<int>(9);
    std::printf("count = %ld\n", a.use_count());
    {
        auto b = a;
        std::printf("count = %ld\n", a.use_count());
        auto c = b;
        std::printf("count = %ld\n", a.use_count());
    }
    std::printf("count = %ld\n", a.use_count());
    return 0;
}
```

```text
count = 1
count = 2
count = 3
count = 1
```

Copying a `shared_ptr` increments the count; the three copies in the inner block are released together
at the closing brace and the count falls back to `1`. When it reaches `0` — which the last line shows
has not happened yet, because `a` is still alive — the object is destroyed. `use_count()` is a
diagnostic, not something to branch on in real code; it is here so you can see the mechanism.

Two things follow from the control block existing. `shared_ptr` is **bigger than a raw pointer** (two
pointers, in practice — the object and the control block), so passing it by value copies and bumps a
count. Pass it as `const std::shared_ptr<T> &` when you only need to read through it, or as a raw `T *`
or `T &` when the callee does not need to keep it alive.

## The cycle that never frees

Reference counting has one failure mode, and it is a common one: two objects that hold `shared_ptr`s to
each other keep each other's count at `1` forever, so neither is ever destroyed.

```cpp run
#include <cstdio>
#include <memory>

struct Node {
    int id;
    std::shared_ptr<Node> partner;
    explicit Node(int i) : id(i) { std::printf("make %d\n", id); }
    ~Node() { std::printf("free %d\n", id); }
};

int main() {
    auto a = std::make_shared<Node>(1);
    auto b = std::make_shared<Node>(2);
    a->partner = b;
    b->partner = a;
    std::printf("a count = %ld, b count = %ld\n", a.use_count(), b.use_count());
    a.reset();
    b.reset();
    std::printf("both handles released, nothing was freed\n");
    return 0;
}
```

```text
make 1
make 2
a count = 2, b count = 2
both handles released, nothing was freed
```

The evidence is what is **missing**: no `free 1` and no `free 2`, even though both handles were
released. Each node is still held by the other's `partner` member, so both counts are `2` at the point
where you would expect `1`, and neither ever reaches zero. This is a leak, and it is worth noticing that
you can see it here **without** a leak detector — the destructors that should have printed never did.
That habit is more useful than any tool, because it works on the platform you are on.

The fix is to decide that one direction of the relationship does not own the other. A `std::weak_ptr` is
a reference that observes without contributing to the count:

```cpp run
#include <cstdio>
#include <memory>

struct Node {
    int id;
    std::weak_ptr<Node> partner;
    explicit Node(int i) : id(i) { std::printf("make %d\n", id); }
    ~Node() { std::printf("free %d\n", id); }
};

int main() {
    auto a = std::make_shared<Node>(1);
    auto b = std::make_shared<Node>(2);
    a->partner = b;
    b->partner = a;
    std::printf("a count = %ld, b count = %ld\n", a.use_count(), b.use_count());
    if (auto locked = a->partner.lock()) {
        std::printf("a's partner is still %d\n", locked->id);
    }
    a.reset();
    b.reset();
    std::printf("done\n");
    return 0;
}
```

```text
make 1
make 2
a count = 1, b count = 1
a's partner is still 2
free 1
free 2
done
```

Two changes, both visible in the output. The counts are now `1` and `1`, because a `weak_ptr` does not
hold anything. And `free 1` and `free 2` appear, so the nodes were really destroyed.

A `weak_ptr` cannot be dereferenced directly, and that is deliberate: the object it observes might
already be gone. To use it you must call `lock()`, which either returns a `shared_ptr` that keeps the
object alive for as long as you hold it, or a null `shared_ptr` if it has already been destroyed. **The
`if (auto locked = ...)` pattern is the whole reason `weak_ptr` is safe** — you cannot accidentally
read freed memory, because the act of getting a usable pointer also guarantees the object survives.

:::scenario Who owns the connection?

A server accepts connections and needs to keep them alive for the lifetime of the server. The
straightforward translation from C is a list of `Connection *` and a `delete` in the server's
destructor — which is the bug Chapter 24 was about, only now spread across two classes. The C++ version
puts the ownership in the type, and the type system then answers the question for every future
maintainer:

```cpp run-san
#include <cstdio>
#include <memory>
#include <vector>

class Server;

class Connection {
public:
    Connection(int fd, Server *owner) : fd_(fd), owner_(owner) {
        std::printf("open  fd %d\n", fd_);
    }
    ~Connection() { std::printf("close fd %d\n", fd_); }

    int fd() const { return fd_; }
    bool attached() const { return owner_ != nullptr; }

private:
    int fd_;
    Server *owner_;          // non-owning: the Server outlives its connections
};

class Server {
public:
    Connection *add(int fd) {
        conns_.push_back(std::make_unique<Connection>(fd, this));
        return conns_.back().get();
    }
    std::size_t count() const { return conns_.size(); }

private:
    std::vector<std::unique_ptr<Connection>> conns_;
};

int main() {
    Server s;
    Connection *first = s.add(3);
    s.add(4);
    std::printf("server holds %zu connections\n", s.count());
    std::printf("first connection is attached: %s\n", first->attached() ? "yes" : "no");
    return 0;
}
```

```text
open  fd 3
open  fd 4
server holds 2 connections
first connection is attached: yes
close fd 4
close fd 3
```

Four things are worth pulling out of that.

- **The `Server` owns its connections** because it holds `std::vector<std::unique_ptr<Connection>>`.
  Nobody wrote a destructor, and yet both connections closed — in reverse order, `4` then `3`, as
  Chapter 24 guaranteed.
- **`Connection` does not own its `Server`**, and that is expressed by a plain `Server *`. A
  `shared_ptr` here would be wrong twice over: it would be a cycle if `Server` also held the
  connections by `shared_ptr`, and it would claim an ownership that does not exist.
- **`add` returns a raw `Connection *`**, not a `unique_ptr`. The caller is not being given ownership; it
  is being given a way to look at something the server owns. Returning a `unique_ptr` would hand over
  the only owner and leave the vector holding nothing.
- **The pointer stays valid across `push_back`.** The vector may reallocate and move the `unique_ptr`s,
  but a `unique_ptr`'s move moves the *pointer*, not the `Connection` — so `first` still points at the
  same heap object. With a `std::vector<Connection>` instead, `push_back` would have moved the
  `Connection` itself and `first` would have dangled.

The review question from Chapter 25 becomes answerable at a glance: every member is either a value, a
`unique_ptr`, or a raw pointer that is documented as non-owning. There is no fourth case.

:::

## Custom deleters: owning things that are not `new`ed

Not everything is allocated with `new`. A `std::FILE *` comes from `std::fopen` and must be released
with `std::fclose`, and a `unique_ptr` can carry that instruction:

```cpp run
#include <cstdio>
#include <memory>

int main() {
    auto closer = [](std::FILE *f) { std::fclose(f); };
    std::unique_ptr<std::FILE, decltype(closer)> log(std::fopen("out.log", "w"), closer);

    if (!log) {
        std::printf("could not open out.log\n");
        return 1;
    }
    std::fputs("line one\n", log.get());
    std::printf("wrote a line, handle is %s\n", log ? "open" : "closed");
    return 0;
}
```

```text
wrote a line, handle is open
```

The second template argument is the deleter type, and `decltype(closer)` names it because the lambda has
no nameable type. This is a `unique_ptr` that calls `std::fclose` instead of `delete`, so the whole of
Chapter 24's `File` class collapses into one line at the point of use. `log.get()` is how you reach the
raw `std::FILE *` for `std::fputs`, which needs one.

The lambda is a preview of Chapter 29. For now, read `[](std::FILE *f) { std::fclose(f); }` as "an
anonymous function taking a `std::FILE *`", and `decltype(closer)` as "whatever type that is".

## When a raw pointer is still right

Smart pointers are not a replacement for pointers. They are a way of recording ownership, and a
non-owning pointer is still a non-owning pointer — that is what `Server *owner_` was in the scenario,
and what a parameter should be when the function only reads through it:

```cpp
void log_request(const Request &r);      // reference: not null, not owned
void log_request(const Request *r);      // pointer: may be null, not owned
std::unique_ptr<Request> parse(...);     // unique_ptr: ownership passes to the caller
std::shared_ptr<Cache> shared_cache();   // shared_ptr: ownership is shared
```

Use `unique_ptr` and `shared_ptr` for **members and return values** — the places where ownership is
decided. Use `T *` and `T &` for **parameters and non-owning members** — the places where ownership is
merely observed. A function that takes a `shared_ptr` by value is making a claim about the caller's
design that it usually should not be making.

:::pitfall Two shared_ptrs built from the same raw pointer

`shared_ptr` counts owners, but the count lives in the control block, and **each `shared_ptr` you
construct from a bare pointer creates its own control block**. Two of them, one allocation, and both
will delete:

```cpp run-san-catch
#include <cstdio>
#include <memory>

int main() {
    int *raw = new int(5);
    std::shared_ptr<int> a(raw);
    std::shared_ptr<int> b(raw);
    std::printf("a count = %ld, b count = %ld\n", a.use_count(), b.use_count());
    return 0;
}
```

```text
attempting double-free
```

Notice what the counts would have said: `1` and `1`. Each `shared_ptr` believes it is the only owner,
because neither knows the other exists. This is the Chapter 25 double free wearing a safety feature's
clothes, and the compiler cannot see it either.

The rule that prevents it: **create the object through `make_shared`, or through exactly one
`shared_ptr` constructor, and then copy the `shared_ptr`.** `auto a = std::make_shared<int>(5); auto b = a;`
is correct and gives a count of `2`. If you are handed a raw pointer by a C API, wrap it once, and pass
the `shared_ptr` around — never the raw pointer.

:::

## Key takeaways

- A raw pointer does not say whether it owns; smart pointers put the answer in the type, which is the
  only way the compiler can enforce it.
- `std::unique_ptr<T>` is a single owner and is move-only, so the double free is impossible; use
  `std::make_unique` rather than `new`, and the array form `std::make_unique<T[]>(n)` for buffers.
- Moving a `unique_ptr` transfers ownership and leaves the source null, which is how a function says
  "this is yours now".
- `std::shared_ptr<T>` shares ownership through a reference count in a control block; copying increments
  it and the object dies when the last owner goes. It is larger than a raw pointer, so pass it by
  reference when you only read through it.
- Two objects holding `shared_ptr`s to each other keep both counts at `1` forever and leak; the missing
  destructor output is the evidence, and no leak detector is needed to see it.
- `std::weak_ptr<T>` observes without owning and must be `lock()`ed before use, which is what makes it
  safe: a successful `lock()` also guarantees the object is still alive.
- A custom deleter makes `unique_ptr` own anything with a matching release function — `std::fclose`, a
  socket close, a mutex unlock — collapsing a hand-written RAII class into one declaration.
- Keep raw pointers for **parameters and non-owning members**, and smart pointers for **members and
  return values**; never build two `shared_ptr`s from one raw pointer.

## Practice

- [ ] Replace a `new`/`delete` pair with `std::make_unique`, and use a class that prints in its
  constructor and destructor to prove the object dies at the end of the scope with no `delete` in sight.
- [ ] Show the compiler rejecting a copy of a `unique_ptr`, then fix it with `std::move` and print
  whether each pointer is still set.
- [ ] Create one `shared_ptr` and print `use_count()` at four points: alone, with one copy, with two
  copies, and after the copies go out of scope.
- [ ] Build a struct holding a `shared_ptr` to itself, show that the count is `2` and that nothing is
  freed when the handle is released, then change the member to `weak_ptr` and show the destructor
  running.
- [ ] Wrap a `std::FILE *` in a `unique_ptr` with a `std::fclose` deleter, write a line through it, and
  confirm the file was written.
- [ ] Write a factory function that returns a `std::unique_ptr` to a class that announces itself, and
  show the caller's pointer owning the object and destroying it.

## Solutions

:::solution Exercise 1

```cpp run
#include <cstdio>
#include <memory>

class Job {
public:
    explicit Job(int n) : id(n) { std::printf("start %d\n", id); }
    ~Job() { std::printf("done  %d\n", id); }
    int id;
};

int main() {
    auto j = std::make_unique<Job>(7);
    std::printf("working on %d\n", j->id);
    return 0;
}
```

```text
start 7
working on 7
done  7
```

`done  7` prints after `main`'s last statement and there is no `delete` anywhere. `make_unique`
allocates and constructs in one expression, so there is no window in which a `Job` exists with no owner.
Note `j->id` — `unique_ptr` overloads `->` so it reads like a raw pointer.

:::

:::solution Exercise 2

```cpp run
#include <cstdio>
#include <memory>
#include <utility>

int main() {
    auto a = std::make_unique<int>(5);
    auto b = std::move(a);
    std::printf("a is %s\n", a ? "set" : "empty");
    std::printf("b is %s, *b = %d\n", b ? "set" : "empty", *b);
    return 0;
}
```

```text
a is empty
b is set, *b = 5
```

And the copy that `unique_ptr` refuses, which is the reason the move is necessary:

```cpp bad
#include <memory>

int main() {
    auto a = std::make_unique<int>(1);
    auto b = a;
    (void)b;
    return 0;
}
```

```text
call to implicitly-deleted copy constructor of 'unique_ptr<int>'
```

The message is more informative than it looks: the copy constructor is deleted *because* the type has a
user-declared move constructor. That is the language saying a `unique_ptr` is defined by being
transferable rather than duplicable, and the same mechanism gives you a single owner for free.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>
#include <memory>

int main() {
    auto a = std::make_shared<int>(9);
    std::printf("count = %ld\n", a.use_count());
    {
        auto b = a;
        std::printf("count = %ld\n", a.use_count());
        auto c = b;
        std::printf("count = %ld\n", a.use_count());
    }
    std::printf("count = %ld\n", a.use_count());
    return 0;
}
```

```text
count = 1
count = 2
count = 3
count = 1
```

Each copy bumps the count and the two copies in the inner block are released together at its closing
brace, which is why the count drops by two in one step. The count never reaches `0` in this program
because `a` is still alive, so nothing is destroyed — a `shared_ptr` frees its object on the transition
*to* zero, not on every release.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>
#include <memory>

struct Parent {
    std::shared_ptr<Parent> child;
    ~Parent() { std::printf("freed\n"); }
};

int main() {
    auto p = std::make_shared<Parent>();
    p->child = p;
    std::printf("count = %ld\n", p.use_count());
    p.reset();
    std::printf("handle released, nothing was freed\n");
    return 0;
}
```

```text
count = 2
handle released, nothing was freed
```

The count is `2` before `reset()` because the object holds a `shared_ptr` to itself, so releasing the
external handle only takes it from `2` to `1`. No `freed` line appears — the object is still alive and
will never be freed. Changing the member to `std::weak_ptr<Parent>` makes the count `1`, so `reset()`
takes it to `0` and prints `freed` immediately.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>
#include <memory>

int main() {
    auto closer = [](std::FILE *f) { std::fclose(f); };
    std::unique_ptr<std::FILE, decltype(closer)> log(std::fopen("out.log", "w"), closer);

    if (!log) {
        std::printf("could not open out.log\n");
        return 1;
    }
    std::fputs("line one\n", log.get());
    std::printf("wrote a line, handle is %s\n", log ? "open" : "closed");
    return 0;
}
```

```text
wrote a line, handle is open
```

`log` tests true because `unique_ptr` converts to `bool` by checking its pointer, so the same check you
would write for a raw `std::FILE *` still works. The `std::fclose` happens when `log` goes out of scope
at the end of `main`, which is why the program never calls it. This is the whole of Chapter 24's `File`
class replaced by one declaration.

:::

:::solution Exercise 6

```cpp run
#include <cstdio>
#include <memory>

class Parser {
public:
    explicit Parser(int n) : depth_(n) { std::printf("parser at depth %d\n", depth_); }
    ~Parser() { std::printf("parser closed\n"); }
    int depth() const { return depth_; }

private:
    int depth_;
};

static std::unique_ptr<Parser> make_parser(int n) {
    return std::make_unique<Parser>(n);
}

int main() {
    auto p = make_parser(3);
    std::printf("caller owns depth %d\n", p->depth());
    return 0;
}
```

```text
parser at depth 3
caller owns depth 3
parser closed
```

`make_parser` returns by value, and `unique_ptr` has a move constructor, so the ownership leaves the
function and arrives in `p` with no copy and no leak. `parser closed` printing after `main`'s output is
the proof that `p` is the owner. This is the shape to reach for whenever a function creates something
whose lifetime outlasts the call — the alternative in C is returning a pointer plus a documented
obligation to free it, which is a comment the compiler cannot check.

:::
