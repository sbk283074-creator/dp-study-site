---
chapter: 23
part: 4
title: Inheritance and Polymorphism
summary: Derive one type from another, let the compiler pick a function at run time with virtual, and learn the four silent failures that make C++ inheritance dangerous.
minutes: 65
tags: [inheritance, virtual, override, abstract-class, pure-virtual, virtual-destructor, object-slicing, vtable, polymorphism]
---

Everything so far has been about one type owning something. This chapter is about types that relate to
each other, and about the one mechanism in C++ that lets a decision be made while the program runs
rather than when it is compiled. That mechanism — the `virtual` function — is what turns a list of
different things into a list you can loop over without asking what each one is. It is also where C++'s
sharpest footguns live, and unlike the double free from Chapter 21, every one of them is **silent**: the
code compiles, runs, and does the wrong thing.

## Deriving one type from another

A class can be declared to derive from another. `Square` **is a** `Shape`, and everything `Shape` can do,
`Square` can do:

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual const char *name() const { return "shape"; }
    virtual double area() const { return 0.0; }
};

class Square : public Shape {
public:
    explicit Square(double side) : side_(side) {}
    const char *name() const override { return "square"; }
    double area() const override { return side_ * side_; }

private:
    double side_;
};
```

Construction order is the mirror image of the destructor order from Chapter 20: **base first, then
members, then the derived constructor's body**, and destruction in exactly the reverse. So by the time
`Square`'s constructor body runs, the `Shape` part of the object already exists and is valid. This is
why a derived constructor can pass arguments up to a base constructor in its initialiser list, and why
you should never call a virtual function from a constructor: at that moment the object is a `Shape`, not
yet a `Square`, so the base version is what runs.

Use `public` inheritance. C++ also allows `private` and `protected` inheritance, which are almost never
what you want and which the rest of this book does not use. When you write `: public Base`, read it as
"is a".

## virtual: deciding at run time

The word `virtual` on a member function means "do not decide which function this call is at compile
time; look it up on the object instead." Here is what that buys you:

```cpp run-san
#include <cstdio>
#include <memory>
#include <vector>

class Shape {
public:
    virtual ~Shape() = default;
    virtual const char *name() const { return "shape"; }
    virtual double area() const { return 0.0; }
};

class Square : public Shape {
public:
    explicit Square(double side) : side_(side) {}
    const char *name() const override { return "square"; }
    double area() const override { return side_ * side_; }

private:
    double side_;
};

class Circle : public Shape {
public:
    explicit Circle(double r) : r_(r) {}
    const char *name() const override { return "circle"; }
    double area() const override { return 3.14159265358979 * r_ * r_; }

private:
    double r_;
};

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Square>(3.0));
    shapes.push_back(std::make_unique<Circle>(1.0));

    for (const auto &s : shapes) {
        std::printf("%s: area = %.2f\n", s->name(), s->area());
    }
    return 0;
}
```

```text
square: area = 9.00
circle: area = 3.14
```

That loop contains no test. It does not ask what kind of shape it is holding. It calls `name()` and
`area()` on a `Shape` and gets the right answer for a square and for a circle, because the call goes
through the object's **vtable** — a per-class table of function addresses that every object with virtual
functions carries a pointer to. The pointer is usually called `vptr`, and it is a hidden member you did
not declare.

That hidden member is the cost of the feature, and it is worth knowing the size of it:

```cpp run
#include <cstdio>

struct Plain {
    int a;
    int b;
};

class HasVirtual {
public:
    int a;
    int b;
    virtual ~HasVirtual() = default;
};

int main() {
    std::printf("sizeof Plain      = %zu\n", sizeof(Plain));
    std::printf("sizeof HasVirtual = %zu\n", sizeof(HasVirtual));
    return 0;
}
```

```text
sizeof Plain      = 8
sizeof HasVirtual = 16
```

Two `int`s and a pointer, so 16 bytes on this 64-bit target: **8 bytes of data plus 8 bytes of `vptr`.**
One pointer per object, one table per class. The call itself is also indirect, so it cannot be inlined
the way a normal call can. That is the price. For most code it is the right trade — one branch and eight
bytes for a loop with no type tests in it — but it is a real cost, and a design that makes every object
in a hot loop polymorphic is paying it whether it needs to or not.

## override: making the compiler check your intent

The `override` keyword asserts "this function overrides a virtual in a base class." Without it, a typo
in the signature silently creates a **new** function instead of overriding, and the call goes to the
base version:

```cpp bad
class Base {
public:
    virtual int value() const { return 1; }
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    int value() override { return 2; }
};

int main() {
    Derived d;
    return d.value();
}
```

```text
non-virtual member function marked 'override' hides virtual member function
```

The note underneath is the part worth reading: `different qualifiers ('const' vs unqualified)`. The
author forgot the `const` that `Base::value` has, so this is a different function with the same name —
and `override` caught it. Drop the `override` and the program compiles, and every call through a
`Base *` quietly returns `1`. **Write `override` on every overriding function**, always. It costs five
characters and converts a silent wrong answer into a compiler error.

## Abstract classes and pure virtual

A function declared with `= 0` instead of a body is **pure virtual**, and a class with any pure virtual
function is **abstract**: it describes an interface that cannot itself be instantiated.

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;      // no body: subclasses must provide one
};
```

```cpp bad
#include <cstdio>

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
};

int main() {
    Shape s;
    std::printf("%.2f\n", s.area());
    return 0;
}
```

```text
variable type 'Shape' is an abstract class
```

The note is `unimplemented pure virtual method 'area' in 'Shape'`, which names exactly what is missing.
An abstract class is how you express "every shape has an area, and I refuse to guess what it is". The
compiler will not let you have a `Shape` object, so the question "what does `Shape::area` return?" never
comes up. Note that the destructor is still defined (`= default`) even though the class is abstract —
an abstract class needs a virtual destructor for exactly the reason below.

## The virtual destructor

This is the footgun that produces leaks with no diagnostic. Deleting a derived object through a base
pointer is undefined behaviour **unless the base destructor is virtual**:

```cpp warn
#include <cstdio>

class Base {
public:
    ~Base() { std::printf("~Base\n"); }
    virtual void speak() { std::printf("base\n"); }
};

class Derived : public Base {
public:
    ~Derived() { std::printf("~Derived\n"); }
    void speak() override { std::printf("derived\n"); }
};

int main() {
    Base *p = new Derived();
    p->speak();
    delete p;
    return 0;
}
```

```text
delete called on non-final 'Base' that has virtual functions but non-virtual destructor
```

That is `-Wdelete-non-abstract-non-virtual-dtor`, and it is worth knowing that this warning exists
because the failure it describes is invisible at run time: the program prints `derived`, then `~Base`,
and **never prints `~Derived`**. The `Derived` part of the object is never destroyed, so anything it
owned leaks. One keyword fixes it:

```cpp run
#include <cstdio>

class Base {
public:
    virtual ~Base() { std::printf("~Base\n"); }
    virtual void speak() { std::printf("base\n"); }
};

class Derived : public Base {
public:
    ~Derived() { std::printf("~Derived\n"); }
    void speak() override { std::printf("derived\n"); }
};

int main() {
    Base *p = new Derived();
    p->speak();
    delete p;
    return 0;
}
```

```text
derived
~Derived
~Base
```

Now `~Derived` runs, in the correct order, and then the base. **If a class has any virtual function, give
it a virtual destructor.** The idiom `virtual ~Base() = default;` costs nothing and removes the whole
category. Chapter 22's `unique_ptr<Shape>` in the first example works only because `Shape` has one.

## Object slicing

When you copy a derived object into a base **by value**, the base copy constructor runs and the derived
part is discarded. The result is a genuine `Base` object — this is called **slicing**, and it is not an
error or a warning:

```cpp run
#include <cstdio>
#include <string>
#include <vector>

class Animal {
public:
    virtual ~Animal() = default;
    virtual std::string speak() const { return "..."; }
};

class Dog : public Animal {
public:
    std::string speak() const override { return "woof"; }
};

static void listen(Animal a) {
    std::printf("by value: %s\n", a.speak().c_str());
}

static void listen_ref(const Animal &a) {
    std::printf("by reference: %s\n", a.speak().c_str());
}

int main() {
    Dog d;
    listen(d);
    listen_ref(d);
    return 0;
}
```

```text
by value: ...
by reference: woof
```

The same `Dog` passed to two functions gives two different answers. `listen` took it by value, so what
arrived was an `Animal` — the `Dog` part, including its `speak`, was cut off at the copy. `listen_ref`
took a reference, so it is looking at the real `Dog` and the vtable is the dog's.

The rule that follows is short: **pass polymorphic types by reference or by pointer, never by value.**
A `const Animal &` parameter accepts anything derived from `Animal` without slicing, and it is also
cheaper, because no copy happens at all.

:::scenario The exporter that needed a new format

A build dashboard writes a table of results. It started as CSV, then someone asked for Markdown for the
PR comment, then someone else asked for JSON. The first implementation had a `format` string and an
`if` chain in the middle of the writing loop, and every new format meant editing that loop and hoping
not to break the others. The version that survived puts the format behind an interface:

```cpp run
#include <cstdio>
#include <string>
#include <vector>

class Exporter {
public:
    virtual ~Exporter() = default;
    virtual const char *name() const = 0;
    virtual void header(const std::vector<std::string> &cols) = 0;
    virtual void row(const std::vector<std::string> &cells) = 0;
};

class CsvExporter : public Exporter {
public:
    const char *name() const override { return "csv"; }
    void header(const std::vector<std::string> &cols) override { line(cols); }
    void row(const std::vector<std::string> &cells) override { line(cells); }

private:
    static void line(const std::vector<std::string> &cells) {
        for (std::size_t i = 0; i < cells.size(); i++) {
            if (i > 0) std::printf(",");
            std::printf("%s", cells[i].c_str());
        }
        std::printf("\n");
    }
};

class MarkdownExporter : public Exporter {
public:
    const char *name() const override { return "markdown"; }
    void header(const std::vector<std::string> &cols) override { line(cols); }
    void row(const std::vector<std::string> &cells) override { line(cells); }

private:
    static void line(const std::vector<std::string> &cells) {
        std::printf("|");
        for (const std::string &c : cells) std::printf(" %s |", c.c_str());
        std::printf("\n");
    }
};

static void export_table(Exporter &e,
                         const std::vector<std::string> &cols,
                         const std::vector<std::vector<std::string>> &rows) {
    std::printf("--- %s ---\n", e.name());
    e.header(cols);
    for (const std::vector<std::string> &r : rows) e.row(r);
}

int main() {
    std::vector<std::string> cols = {"build", "status"};
    std::vector<std::vector<std::string>> rows = {{"41", "ok"}, {"42", "failed"}};

    CsvExporter csv;
    MarkdownExporter md;
    export_table(csv, cols, rows);
    export_table(md, cols, rows);
    return 0;
}
```

```text
--- csv ---
build,status
41,ok
42,failed
--- markdown ---
| build | status |
| 41 | ok |
| 42 | failed |
```

The design decision that matters is what `export_table` does **not** know. It has no idea that CSV or
Markdown exist; it knows that an `Exporter` can print a header and a row, and it loops. Adding a JSON
exporter is a new class and one line in `main` — the loop, and every other format, are untouched. The
`if` chain version would have required editing the one function that all three formats share, which is
exactly where a change breaks something unrelated.

Three details in the code are deliberate. `name()`, `header()` and `row()` are pure virtual, so
`Exporter` cannot be instantiated and every subclass is forced to answer all three. `export_table` takes
`Exporter &`, not `Exporter` by value — that is the slicing rule, and taking it by value would have
compiled and printed the base versions. And the destructor is `virtual`, which is what makes
`std::unique_ptr<Exporter>` safe, and what the next chapter's factory will need.

The pattern is worth naming, because you will use it constantly: **an abstract base class defining the
operations, concrete subclasses implementing them, and code that depends only on the base.** It is the
C++ form of a plugin interface, and it is what makes it possible to add behaviour without editing the
code that uses it.

:::

:::pitfall Slicing into a container, silently

The by-value parameter is the obvious form of slicing. The one that ships to production is a container
of base objects, because the loop looks completely reasonable:

```cpp run
#include <cstdio>
#include <string>
#include <vector>

class Animal {
public:
    virtual ~Animal() = default;
    virtual std::string speak() const { return "..."; }
};

class Dog : public Animal {
public:
    std::string speak() const override { return "woof"; }
};

int main() {
    std::vector<Animal> zoo;
    zoo.push_back(Dog{});
    std::printf("zoo says: %s\n", zoo[0].speak().c_str());
    return 0;
}
```

```text
zoo says: ...
```

The dog barked as a generic animal, and nothing warned — not `-Wall`, not `-Wextra`, not the sanitizer.
`std::vector<Animal>` can only store `Animal`s, so `push_back(Dog{})` copied the `Animal` part and threw
the rest away. The fix is to store pointers or references, and since Chapter 22 we know which pointer:

```cpp
std::vector<std::unique_ptr<Animal>> zoo;
zoo.push_back(std::make_unique<Dog>());
std::printf("zoo says: %s\n", zoo[0]->speak().c_str());   // woof
```

`std::vector<std::unique_ptr<Animal>>` stores pointers to real `Dog`s, so the vtable survives and the
loop dispatches correctly. The general rule: **whenever a type has virtual functions, containers of it
hold `unique_ptr` or `shared_ptr`, not values.** A container of base values is a container of sliced
bases, and it will compile every time.

:::

## Key takeaways

- `class Derived : public Base` means "is a"; construction runs base, then members, then the derived
  body, and destruction is the exact reverse.
- A `virtual` function is looked up on the object at run time through a vtable, which costs one hidden
  pointer per object (8 bytes here) plus one table per class, and prevents inlining.
- Write `override` on every overriding function; without it a signature typo creates a new function
  instead of overriding, and calls silently go to the base version.
- A pure virtual function (`= 0`) makes the class abstract, so it cannot be instantiated and every
  subclass must implement it — this is how you express an interface.
- **Any class with a virtual function needs a virtual destructor**, or deleting through a base pointer
  runs only the base destructor and leaks everything the derived part owned; the compiler warns, and the
  run-time symptom is a missing destructor message.
- Copying a derived object into a base **by value** slices it: the derived part is discarded and the
  base version of every virtual function runs.
- Pass polymorphic types by reference or pointer, and store them in containers as `unique_ptr` or
  `shared_ptr` — never as base values.
- Prefer composition to inheritance when the relationship is "has a" rather than "is a": a class that
  holds a `std::vector<std::unique_ptr<Connection>>` (Chapter 22) is doing the same job as inheritance
  without the coupling.

## Practice

- [ ] Write an abstract `Notifier` with pure virtual `channel()` and `send()`, and two subclasses that
  print differently. Call both through a `Notifier &` parameter and show the dispatch.
- [ ] Write a base class with `virtual int value() const` and a subclass that forgets the `const`. Show
  the compiler error that `override` produces, and quote the note that names the qualifier difference.
- [ ] Pass a `Dog` to two functions, one taking `Animal` by value and one taking `const Animal &`, and
  show that only the reference one barks.
- [ ] Write a base with a non-virtual destructor and a derived with one. Show the compiler warning, then
  add `virtual` and show both destructors running in the right order.
- [ ] Write a pure virtual `Task` with a `cost()`, two implementations, and a function that sums the cost
  of an array of `Task *`.
- [ ] Store two different subclasses of an abstract `Shape` in a
  `std::vector<std::unique_ptr<Shape>>`, print each one's name and area, and print the total.

## Solutions

:::solution Exercise 1

```cpp run
#include <cstdio>
#include <string>

class Notifier {
public:
    virtual ~Notifier() = default;
    virtual std::string channel() const = 0;
    virtual void send(const std::string &msg) = 0;
};

class Email : public Notifier {
public:
    std::string channel() const override { return "email"; }
    void send(const std::string &msg) override { std::printf("email: %s\n", msg.c_str()); }
};

class Sms : public Notifier {
public:
    std::string channel() const override { return "sms"; }
    void send(const std::string &msg) override { std::printf("sms:   %s\n", msg.c_str()); }
};

static void notify(Notifier &n, const std::string &msg) {
    std::printf("via %s -> ", n.channel().c_str());
    n.send(msg);
}

int main() {
    Email e;
    Sms s;
    notify(e, "build 41 finished");
    notify(s, "build 41 finished");
    return 0;
}
```

```text
via email -> email: build 41 finished
via sms -> sms:   build 41 finished
```

`notify` takes a `Notifier &`, so both calls reach the same function and the vtable picks the
implementation. Taking `Notifier` by value would have sliced both objects into bare `Notifier`s — except
that `Notifier` is abstract, so that version would not compile at all. An abstract base class cannot be
sliced into, which is one of the quieter advantages of making the interface pure virtual.

:::

:::solution Exercise 2

```cpp bad
class Base {
public:
    virtual int value() const { return 1; }
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    int value() override { return 2; }
};

int main() {
    Derived d;
    return d.value();
}
```

```text
non-virtual member function marked 'override' hides virtual member function
```

And the note that identifies the actual mistake:

```text
different qualifiers ('const' vs unqualified)
```

`Base::value` is `const` and `Derived::value` is not, so they are different functions with the same
name. Without `override` this compiles, `Derived::value` is called through a `Derived` object, and every
call through a `Base *` or `const Base &` gets `1`. The fix is to write `int value() const override`.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>
#include <string>

class Animal {
public:
    virtual ~Animal() = default;
    virtual std::string speak() const { return "..."; }
};

class Dog : public Animal {
public:
    std::string speak() const override { return "woof"; }
};

static void listen_value(Animal a) {
    std::printf("by value:     %s\n", a.speak().c_str());
}

static void listen_ref(const Animal &a) {
    std::printf("by reference: %s\n", a.speak().c_str());
}

int main() {
    Dog d;
    listen_value(d);
    listen_ref(d);
    return 0;
}
```

```text
by value:     ...
by reference: woof
```

`listen_value`'s parameter is an `Animal`, so the argument is copy-constructed as an `Animal` and the
`Dog` half never arrives — the object inside the function is genuinely not a dog, and its vtable is the
base one. `listen_ref` binds directly to the caller's `Dog`, so the vtable is the dog's. The reference
form is also faster, since nothing is copied.

:::

:::solution Exercise 4

```cpp warn
#include <cstdio>

class Base {
public:
    ~Base() { std::printf("~Base\n"); }
    virtual void speak() { std::printf("base\n"); }
};

class Derived : public Base {
public:
    ~Derived() { std::printf("~Derived\n"); }
    void speak() override { std::printf("derived\n"); }
};

int main() {
    Base *p = new Derived();
    p->speak();
    delete p;
    return 0;
}
```

```text
delete called on non-final 'Base' that has virtual functions but non-virtual destructor
```

Adding `virtual` to the destructor is the entire fix:

```cpp run
#include <cstdio>

class Base {
public:
    virtual ~Base() { std::printf("~Base\n"); }
    virtual void speak() { std::printf("base\n"); }
};

class Derived : public Base {
public:
    ~Derived() { std::printf("~Derived\n"); }
    void speak() override { std::printf("derived\n"); }
};

int main() {
    Base *p = new Derived();
    p->speak();
    delete p;
    return 0;
}
```

```text
derived
~Derived
~Base
```

`speak()` dispatched correctly in both versions, which is the trap: the polymorphic call worked, so the
code looked right. Only the destructor failed, and its failure is a missing line of output. In the fixed
version `~Derived` runs first and then `~Base`, which is the correct order and the proof that the whole
object was destroyed. Note that the warning fires because `delete p` names a `Base *` — the compiler is
looking at the static type, which is exactly the information the run-time behaviour depends on.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>

class Task {
public:
    virtual ~Task() = default;
    virtual const char *kind() const = 0;
    virtual int cost() const = 0;
};

class Build : public Task {
public:
    const char *kind() const override { return "build"; }
    int cost() const override { return 10; }
};

class Test : public Task {
public:
    const char *kind() const override { return "test"; }
    int cost() const override { return 4; }
};

static int total(Task **tasks, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) sum += tasks[i]->cost();
    return sum;
}

int main() {
    Build b;
    Test t;
    Task *all[] = {&b, &t};
    std::printf("total cost = %d\n", total(all, 2));
    std::printf("first is a %s\n", all[0]->kind());
    return 0;
}
```

```text
total cost = 14
first is a build
```

The array is `Task *`, so it holds two different types without slicing, and `total` adds them up without
knowing either type. `Task *all[] = {&b, &t};` points at objects that live on the stack and outlive the
array, so no ownership question arises — the array observes, it does not own. If these were created with
`new`, the array would be `std::unique_ptr<Task> all[]` or a vector of them, and the virtual destructor
would be what makes that safe.

:::

:::solution Exercise 6

```cpp run
#include <cstdio>
#include <memory>
#include <string>
#include <vector>

class Shape {
public:
    virtual ~Shape() = default;
    virtual const char *name() const = 0;
    virtual double area() const = 0;
};

class Square : public Shape {
public:
    explicit Square(double s) : s_(s) {}
    const char *name() const override { return "square"; }
    double area() const override { return s_ * s_; }

private:
    double s_;
};

class Rectangle : public Shape {
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    const char *name() const override { return "rectangle"; }
    double area() const override { return w_ * h_; }

private:
    double w_;
    double h_;
};

static std::unique_ptr<Shape> make(const std::string &kind) {
    if (kind == "square") return std::make_unique<Square>(3.0);
    return std::make_unique<Rectangle>(2.0, 5.0);
}

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(make("square"));
    shapes.push_back(make("rectangle"));

    double sum = 0.0;
    for (const auto &s : shapes) {
        std::printf("%-10s area = %.2f\n", s->name(), s->area());
        sum += s->area();
    }
    std::printf("total = %.2f\n", sum);
    return 0;
}
```

```text
square     area = 9.00
rectangle  area = 10.00
total = 19.00
```

`make` returns a `unique_ptr<Shape>` — a `Square` or a `Rectangle` depending on the string — and the
caller never learns which. This is a **factory function**, and it is the standard way to hand back a
polymorphic object without exposing the concrete types. Three pieces have to be right for it to work:
the base destructor must be virtual, or the `unique_ptr` deletes only the `Shape` part; `make` must
return by value, which moves the `unique_ptr` and transfers ownership; and the container must hold
pointers rather than `Shape` values, or every element would be sliced. The loop then needs no type test
at all, which is the point.

:::
