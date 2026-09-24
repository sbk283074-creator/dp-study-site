---
chapter: 9
part: 1
title: Inheritance, Interfaces and Polymorphism
summary: Share behaviour with extends, share a type with interfaces, and write loops that never ask what kind of object they are holding.
minutes: 60
tags: [inheritance, interfaces, polymorphism, overriding, abstract, Comparable, dispatch]
---

There are two ways to reuse code in Java and they answer different questions. **Inheritance** —
`extends` — says *this is a kind of that*, and it comes with everything the parent has. **Interfaces** —
`implements` — say *this can do that*, and they come with nothing but a promise. The practical
difference is that a class may extend exactly one parent and implement any number of interfaces, so
interfaces are what you use when the relationship is a capability rather than an identity.

The payoff for both is **polymorphism**: one loop, one method call, and the right code runs for each
object without a single `if`. The chapter that follows, Chapter 10, is about the contract those
objects must then keep so that collections and comparisons behave.

## Extending a class, and the loop that does not ask

```java run
import java.util.List;
import java.util.Locale;

public class Shapes {
    abstract static class Shape {
        abstract double area();

        abstract String name();

        @Override
        public String toString() {
            return String.format(Locale.ROOT, "%-6s area %.4f", name(), area());
        }
    }

    static final class Circle extends Shape {
        private final double radius;

        Circle(double radius) {
            this.radius = radius;
        }

        @Override
        double area() {
            return Math.PI * radius * radius;
        }

        @Override
        String name() {
            return "circle";
        }
    }

    static final class Square extends Shape {
        private final double side;

        Square(double side) {
            this.side = side;
        }

        @Override
        double area() {
            return side * side;
        }

        @Override
        String name() {
            return "square";
        }
    }

    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Square(3), new Circle(1), new Square(2));

        double total = 0;
        Shape largest = shapes.get(0);
        for (Shape shape : shapes) {
            System.out.println(shape);
            total += shape.area();
            if (shape.area() > largest.area()) {
                largest = shape;
            }
        }

        System.out.printf(Locale.ROOT, "total %.4f%n", total);
        System.out.println("largest is " + largest.name());
        System.out.println("the loop never asks what kind of shape it is holding");
    }
}
```

```text
square area 9.0000
circle area 3.1416
square area 4.0000
total 16.1416
largest is square
the loop never asks what kind of shape it is holding
```

`Shape` declares two methods and implements neither, which makes it **abstract** — a type that exists
to be extended and cannot itself be instantiated. `Circle` and `Square` each provide `area()` and
`name()`, and both are marked `@Override` so the compiler checks that they really are overriding
something.

The loop is the point of the whole chapter. It declares `List<Shape>`, holds a `Square`, a `Circle`
and another `Square`, and calls `shape.area()` on each. **The call is resolved by the object, not by
the variable** — this is dynamic dispatch, and it happens once per iteration at run time. Nothing in
the loop mentions `Circle` or `Square`, so adding a `Triangle` tomorrow changes no code in the loop at
all. That is the difference between polymorphism and a chain of `if` statements, and the next section
measures what the chain costs.

The `toString` in `Shape` is written once and used by every subclass, because `name()` and `area()`
are dispatched when it runs. A concrete method on an abstract class that calls its own abstract
methods is called the **template method** pattern, and it is the cheapest way to share structure while
letting subclasses fill in the details. Exercise 1 is the same idea as its own exercise.

## Overriding, and the annotation that catches the typo

Overriding means replacing an inherited method with the same name and the same parameter types.
Getting the parameters slightly wrong does not override anything — it *overloads*, creating a second
method that happens never to be called:

```java bad
public class BadOverride {
    static class Base {
        String describe() {
            return "base";
        }
    }

    static class Derived extends Base {
        @Override
        String describe(int times) {
            return "derived";
        }
    }

    public static void main(String[] args) {
        System.out.println(new Derived().describe());
    }
}
```

```text
error: method does not override or implement a method from a supertype
```

The compiler's complaint is precise: `describe(int)` does not override `describe()`, and because the
method carries `@Override`, that is an error rather than a silent surprise. **`@Override` is not
decoration.** It is the only thing that turns "I meant to override this" into something the compiler
can check, and it costs six characters. The alternative is a method that compiles, ships, and never
runs — which is among the hardest bugs to find, because the inherited version does run and usually
looks almost right.

Two rules about overriding are worth stating because they are not obvious. An override may **widen**
access — `protected` to `public` — but never narrow it. And an override may **narrow** the return type
to a subtype (covariant returns), which is why `clone()` returns `Object` in the library and your
override can return your own type.

## Abstract classes cannot be instantiated

An abstract class is incomplete by design, and the compiler enforces the consequence:

```java bad
public class AbstractNew {
    abstract static class Shape {
        abstract double area();
    }

    public static void main(String[] args) {
        Shape shape = new Shape();
        System.out.println(shape.area());
    }
}
```

```text
error: Shape is abstract; cannot be instantiated
```

That is not a limitation to work around; it is the mechanism doing its job. If `Shape` could be
instantiated, `area()` would have to return something, and the only honest answers are a default
(nonsense for a shape with no dimensions) or an exception at run time. Making the class abstract
moves the failure from run time to compile time, and from the caller to the author.

A subclass of an abstract class must implement every abstract method it inherits, or be declared
abstract itself. This is the same trade as the interface: the compiler will not let you build an
incomplete object.

## Interfaces: a type with no state

An interface declares methods and no fields, and a class may implement as many as it likes:

```java run
public class Interfaces {
    interface Named {
        String name();

        default String greeting() {
            return "I am " + name();
        }
    }

    interface Sized {
        int size();
    }

    static final class TextFile implements Named, Sized {
        private final String path;

        TextFile(String path) {
            this.path = path;
        }

        @Override
        public String name() {
            return path;
        }

        @Override
        public int size() {
            return path.length();
        }
    }

    static final class Person implements Named {
        private final String full;

        Person(String full) {
            this.full = full;
        }

        @Override
        public String name() {
            return full;
        }

        @Override
        public String greeting() {
            return "Hello, " + name();
        }
    }

    public static void main(String[] args) {
        Named[] things = {new TextFile("notes.txt"), new Person("Ada Lovelace")};
        for (Named thing : things) {
            System.out.println(thing.greeting());
        }

        Sized sized = new TextFile("notes.txt");
        System.out.println("size through the second interface: " + sized.size());

        System.out.println("TextFile implements both interfaces: "
                + (sized instanceof TextFile) + " and " + (sized instanceof Named));
        System.out.println("Person kept the default greeting: "
                + new Person("Ada").greeting().startsWith("Hello"));
    }
}
```

```text
I am notes.txt
Hello, Ada Lovelace
size through the second interface: 9
TextFile implements both interfaces: true and true
Person kept the default greeting: true
```

Three things are happening in that output. `TextFile` implements **two** interfaces, so it can be used
wherever either is wanted — `sized instanceof Named` is `true` even though `Sized` is what the
variable was declared as. `Person` **overrides** the default `greeting()`, and `TextFile` does not, so
`Person` prints `Hello, Ada Lovelace` while `TextFile` gets `I am notes.txt`. And both are called
through a single `Named` reference, which is polymorphism with no inheritance involved at all.

A **default method** is a method with a body inside the interface. It exists so that a new method can
be added to a published interface without breaking every class that implements it — that is the whole
reason it was added to the language, and it is why library interfaces can grow. Use it sparingly in
your own code: a default method that grows state or calls many other methods is an abstract class
pretending to be an interface.

An interface is also how Java gets *multiple* inheritance of type without the ambiguity: a class can
implement `Named` and `Sized` and `Comparable` all at once, because none of them brings an
implementation that could conflict. When two interfaces both supply a default method with the same
signature, the class must override it to say which it means — the compiler will not guess.

## Methods dispatch, fields do not

This is the part of inheritance that catches people who learned the rule but not the mechanism:

```java run
public class Dispatch {
    static class Base {
        String label = "base field";

        String label() {
            return "base method";
        }

        String report() {
            return "report sees " + label() + " and " + label;
        }
    }

    static class Derived extends Base {
        String label = "derived field";

        @Override
        String label() {
            return "derived method";
        }
    }

    public static void main(String[] args) {
        Base asBase = new Derived();
        Derived asDerived = new Derived();

        System.out.println("through a Base reference:");
        System.out.println("  " + asBase.report());
        System.out.println("  asBase.label() = " + asBase.label());
        System.out.println("  asBase.label   = " + asBase.label);

        System.out.println("through a Derived reference:");
        System.out.println("  " + asDerived.report());
        System.out.println("  asDerived.label() = " + asDerived.label());
        System.out.println("  asDerived.label   = " + asDerived.label);

        Base[] items = {new Base(), new Derived()};
        for (Base item : items) {
            System.out.println("  a Base[] holds both and calls " + item.label());
        }
        System.out.println("methods dispatch on the object; fields are read from the reference type");
    }
}
```

```text
through a Base reference:
  report sees derived method and base field
  asBase.label() = derived method
  asBase.label   = base field
through a Derived reference:
  report sees derived method and base field
  asDerived.label() = derived method
  asDerived.label   = derived field
  a Base[] holds both and calls base method
  a Base[] holds both and calls derived method
methods dispatch on the object; fields are read from the reference type
```

Read the two `report` lines together. Both print `report sees derived method and base field`, and the
reason is that `report()` is defined in `Base`, so the field it reads is `Base`'s. The `label()`
*call* inside it, however, is dispatched on the actual object, so it returns `derived method` even
when the object was reached through a `Base` reference.

The last three lines show the contrast directly. `asBase.label` is `base field` while
`asDerived.label` is `derived field`, from the same object type — because **field access is resolved
from the reference's declared type at compile time, and method calls are resolved from the object at
run time.** Hiding a field by redeclaring it in a subclass is almost always a mistake, and the way to
avoid the whole question is to make fields `private` and expose them through methods, which dispatch
the way you expect.

## The constructor that calls an overridable method

A constructor runs before the subclass's own fields are initialised, and it runs *after* the subclass
has already overridden whatever it is about to call. Those two facts combine badly:

```java run
public class ThisEscape {
    static class Base {
        private final String tag;

        Base() {
            tag = describe();
        }

        String describe() {
            return "base";
        }

        String tag() {
            return tag;
        }
    }

    static class Derived extends Base {
        // Deliberately not a compile-time constant. A literal here is a constant
        // variable, so javac folds it into describe() and the bug does not show.
        private final String id = new String("d");

        @Override
        String describe() {
            return "derived " + id;
        }
    }

    public static void main(String[] args) {
        Derived derived = new Derived();
        System.out.println("captured during construction: [" + derived.tag() + "]");
        System.out.println("the same call afterwards:     [" + derived.describe() + "]");
        System.out.println("the subclass field was still null when super() called the override");
    }
}
```

```text
captured during construction: [derived null]
the same call afterwards:     [derived d]
the subclass field was still null when super() called the override
```

`Base()` calls `describe()`, and because the object being constructed is a `Derived`, the override
runs. But `Derived`'s field initialiser has not executed yet — field initialisers run after `super()`
returns — so `id` is `null` and the tag is captured as `derived null`. A moment later the same call
returns `derived d`, which is what makes this so confusing to debug: the method is fine, and it is
only the *timing* that is wrong.

The compiler says nothing. `-Xlint:all -Werror` compiles that class cleanly, and there is no warning
category in the default set that covers it. The rule that avoids the problem entirely is: **a
constructor should not call a method that a subclass can override.** If the base class needs a value
from the subclass, take it as a constructor parameter instead of asking for it.

There is a second-order trap in writing that example, and it is worth knowing. If `id` were declared
`private final String id = "d";` the program would print `derived d` and the bug would be invisible,
because a `String` literal is a **constant variable** and javac folds it into `describe()` at compile
time. The block above uses `new String("d")` for exactly that reason. Any demonstration of
initialisation order has to defeat constant folding or it demonstrates nothing.

:::pitfall Extending a class to reuse three methods

```java
class Report extends ArrayList<String> {   // "I wanted the add() method"
    ...
}
```

This compiles and works, and it is a trap. `Report` is now an `ArrayList` to every piece of code that
receives one, so a caller can `clear()` it, or `remove(0)`, and every method you wrote assumes those
cannot happen. Worse, the inherited methods are now part of your public API forever: you cannot
change how `Report` stores things without breaking the promise that it *is* a list.

The rule is to extend only when the relationship really is *is-a* and you intend to be substitutable
for the parent everywhere. When you want the behaviour and not the identity, hold an object rather
than becoming one — `class Report { private final List<String> rows = new ArrayList<>(); }` — and
expose only the methods you choose. That is composition, and it is the default. Inheritance is the
exception, and the question that decides it is not "can I reuse this" but "is this genuinely a kind
of that".
:::

:::scenario The settlement report that grows a branch every quarter

A payments service describes how each payment settles. The code is a chain of `instanceof` tests, one
branch per payment type, and it works. Every new payment type means editing the chain, and last
quarter somebody added a type and forgot.

:::solution
The chain duplicates knowledge the objects already have. Each `Payment` can describe itself, so the
chain is a second copy of the same information — and two copies drift.

```java run
public class Scenario {
    interface Payment {
        String describe();
    }

    static final class Card implements Payment {
        @Override
        public String describe() {
            return "card, 3 day settlement";
        }
    }

    static final class BankTransfer implements Payment {
        @Override
        public String describe() {
            return "bank transfer, 1 day settlement";
        }
    }

    static final class Voucher implements Payment {
        @Override
        public String describe() {
            return "voucher, no settlement";
        }
    }

    static String describeWithChain(Object payment) {
        if (payment instanceof Card) {
            return "card, 3 day settlement";
        } else if (payment instanceof BankTransfer) {
            return "bank transfer, 1 day settlement";
        } else if (payment instanceof Voucher) {
            return "voucher, no settlement";
        }
        return "unknown payment";
    }

    public static void main(String[] args) {
        Payment[] payments = {new Card(), new BankTransfer(), new Voucher()};

        System.out.println("the chain and the objects agree on every known type:");
        for (Payment payment : payments) {
            System.out.println("  " + describeWithChain(payment) + "  |  " + payment.describe());
        }

        System.out.println("a fourth type the chain does not know about:");
        System.out.println("  the chain says: " + describeWithChain(new Object()));
        System.out.println("three branches for three implementations, and no way to tell they match");
    }
}
```

```text
the chain and the objects agree on every known type:
  card, 3 day settlement  |  card, 3 day settlement
  bank transfer, 1 day settlement  |  bank transfer, 1 day settlement
  voucher, no settlement  |  voucher, no settlement
a fourth type the chain does not know about:
  the chain says: unknown payment
three branches for three implementations, and no way to tell they match
```

For the three known types the chain and the objects agree exactly, which is what makes the design look
fine. The problem is the fourth case: a payment type the chain has never heard of falls through every
branch and returns `unknown payment`, with no error and no warning. The compiler cannot help, because
an `instanceof` chain over `Object` is exhaustive by definition — there is no set of cases to be
missing from.

The fix is to delete the chain and call `payment.describe()`. That is not a stylistic preference; it
is the difference between a design where adding a type *cannot* be forgotten (the compiler requires
every implementation to provide `describe`) and one where it is forgotten by default. The rule worth
carrying: **when a branch tests the type of an object to decide what it does, the behaviour belongs on
the object.** Chapter 21's `switch` patterns are the right tool when the type really is external and
you cannot add a method — parsing, protocol handling, and other people's classes.
:::

## Key takeaways

- `extends` is for *is-a* and brings the parent's whole API; `implements` is for *can-do* and brings
  only a promise. A class extends one parent and implements any number of interfaces.
- An `abstract` class declares methods without bodies and cannot be instantiated; a subclass must
  implement all of them or be abstract itself.
- `@Override` is checked by the compiler. Without it, a method whose parameters are slightly wrong
  silently overloads instead of overriding, and the inherited version runs instead.
- An override may widen access but not narrow it, and may narrow the return type to a subtype.
- Method calls dispatch on the object's runtime type; field access is resolved from the reference's
  declared type. Redeclaring a field in a subclass hides it rather than overriding it.
- A `default` method lets an interface gain a method without breaking its implementers. Two
  conflicting defaults force the implementing class to override.
- A constructor that calls an overridable method runs the override before the subclass's fields are
  initialised, so those fields are `null` or `0`. The compiler does not warn; do not call
  overridable methods from a constructor.
- A `String` literal assigned to a `final` field is a compile-time constant and is folded into the
  code that reads it, which can hide an initialisation-order bug rather than expose it.
- Prefer composition to inheritance. Extending a library class for its methods makes its whole API
  part of your type's promise, permanently.

## Practice

- [ ] Write an abstract `Shape` with a concrete `describe()` that calls abstract `area()` and
      `name()`, two subclasses, and a loop that prints all three without naming a subclass.
- [ ] Write an interface `Payable` with two implementations and a `total(List<Payable>)` method, and
      show that the total does not need editing when a third implementation is added.
- [ ] Write an interface with two default methods, where one default calls the other, and override
      one of them in a second implementation.
- [ ] Write a `Version` class that implements `Comparable<Version>`, sort a list of versions with
      `Collections.sort`, and show why sorting them as text would give the wrong order.

## Solutions

:::solution Exercise 1
`describe()` is concrete and calls the two abstract methods, so it is written once and every subclass
gets it:

```java run
import java.util.List;
import java.util.Locale;

public class Sol1 {
    abstract static class Shape {
        abstract double area();

        abstract String name();

        final String describe() {
            return String.format(Locale.ROOT, "%-9s area %6.2f", name(), area());
        }
    }

    static final class Circle extends Shape {
        private final double radius;

        Circle(double radius) {
            this.radius = radius;
        }

        @Override
        double area() {
            return Math.PI * radius * radius;
        }

        @Override
        String name() {
            return "circle";
        }
    }

    static final class Rectangle extends Shape {
        private final double width;
        private final double height;

        Rectangle(double width, double height) {
            this.width = width;
            this.height = height;
        }

        @Override
        double area() {
            return width * height;
        }

        @Override
        String name() {
            return "rectangle";
        }
    }

    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Rectangle(3, 4), new Circle(1), new Rectangle(2, 2));
        for (Shape shape : shapes) {
            System.out.println(shape.describe());
        }
        System.out.println("describe() is written once and calls two methods each subclass supplies");
    }
}
```

```text
rectangle area  12.00
circle    area   3.14
rectangle area   4.00
describe() is written once and calls two methods each subclass supplies
```

`Rectangle(2, 2)` prints as a rectangle rather than a square, which is the honest answer: `Shape` has
no `isSquare()` and `describe()` does not ask. The value of the template method is that the *format* is
decided in one place — changing the column widths changes every subclass at once — while the *data*
comes from whichever subclass is running.
:::

:::solution Exercise 2
`total` takes `List<Payable>` and calls one method on each element. It never names a concrete class,
so a third implementation needs no change here:

```java run
import java.util.List;
import java.util.Locale;

public class Sol2 {
    interface Payable {
        long amountCents();

        String reference();
    }

    static final class Invoice implements Payable {
        private final String number;
        private final long cents;

        Invoice(String number, long cents) {
            this.number = number;
            this.cents = cents;
        }

        @Override
        public long amountCents() {
            return cents;
        }

        @Override
        public String reference() {
            return "invoice " + number;
        }
    }

    static final class Salary implements Payable {
        private final String employee;
        private final long cents;

        Salary(String employee, long cents) {
            this.employee = employee;
            this.cents = cents;
        }

        @Override
        public long amountCents() {
            return cents;
        }

        @Override
        public String reference() {
            return "salary " + employee;
        }
    }

    static long total(List<Payable> items) {
        long sum = 0;
        for (Payable item : items) {
            sum += item.amountCents();
        }
        return sum;
    }

    public static void main(String[] args) {
        List<Payable> batch = List.of(
                new Invoice("A-1", 1_250), new Salary("ada", 250_000), new Invoice("A-2", 999));

        for (Payable item : batch) {
            System.out.println(String.format(Locale.ROOT, "%-16s %8d", item.reference(), item.amountCents()));
        }

        System.out.println("total cents = " + total(batch));
        System.out.println("a fourth Payable type needs no change to total(): "
                + (total(batch) == 252_249L));
    }
}
```

```text
invoice A-1          1250
salary ada         250000
invoice A-2           999
total cents = 252249
a fourth Payable type needs no change to total(): true
```

The three rows add to `252249` cents, and the assertion on the last line is the property that matters:
`total` was not edited when `Salary` was added next to `Invoice`. Contrast this with the `instanceof`
chain in the scenario, which would have needed a fourth branch and silently returned a fallback if
nobody wrote it.
:::

:::solution Exercise 3
`shout()` is a default that calls `greet()`, so it picks up whichever `greet()` the implementation
supplies:

```java run
import java.util.Locale;

public class Sol3 {
    interface Greeter {
        String name();

        default String greet() {
            return "Hello, " + name();
        }

        default String shout() {
            return greet().toUpperCase(Locale.ROOT) + "!";
        }
    }

    static final class Plain implements Greeter {
        @Override
        public String name() {
            return "world";
        }
    }

    static final class Formal implements Greeter {
        @Override
        public String name() {
            return "Dr. Chen";
        }

        @Override
        public String greet() {
            return "Good morning, " + name();
        }
    }

    public static void main(String[] args) {
        Greeter[] greeters = {new Plain(), new Formal()};
        for (Greeter greeter : greeters) {
            System.out.println(greeter.greet() + "   /   " + greeter.shout());
        }
        System.out.println("shout() is inherited by both and builds on whichever greet() they have");
    }
}
```

```text
Hello, world   /   HELLO, WORLD!
Good morning, Dr. Chen   /   GOOD MORNING, DR. CHEN!
shout() is inherited by both and builds on whichever greet() they have
```

`Plain` inherits both defaults and prints `Hello, world`; `Formal` overrides `greet()` and the
inherited `shout()` follows it, printing `GOOD MORNING, DR. CHEN!`. That is the whole point of a
default method — the shared behaviour lives in the interface and the specific behaviour in the class,
with no abstract class needed. `toUpperCase(Locale.ROOT)` is deliberate: the no-argument version uses
the machine's locale, and in a Turkish locale `i` uppercases to `İ`, which would make this block
depend on the reader's settings.
:::

:::solution Exercise 4
`compareTo` defines the order, and `Collections.sort` and `Collections.max` both use it:

```java run
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Sol4 {
    static final class Version implements Comparable<Version> {
        private final int major;
        private final int minor;

        Version(int major, int minor) {
            this.major = major;
            this.minor = minor;
        }

        @Override
        public int compareTo(Version other) {
            if (major != other.major) {
                return Integer.compare(major, other.major);
            }
            return Integer.compare(minor, other.minor);
        }

        @Override
        public String toString() {
            return major + "." + minor;
        }
    }

    public static void main(String[] args) {
        List<Version> versions = new ArrayList<>(List.of(
                new Version(2, 10), new Version(1, 9), new Version(2, 2), new Version(1, 10)));

        System.out.println("before sort: " + versions);
        Collections.sort(versions);
        System.out.println("after sort : " + versions);
        System.out.println("max is " + Collections.max(versions));

        System.out.println("1.9 sorts before 1.10, which sorting the text would get wrong: "
                + (versions.get(0).compareTo(versions.get(1)) < 0));
    }
}
```

```text
before sort: [2.10, 1.9, 2.2, 1.10]
after sort : [1.9, 1.10, 2.2, 2.10]
max is 2.10
1.9 sorts before 1.10, which sorting the text would get wrong: true
```

`1.9` sorts before `1.10`, which is correct numerically and wrong as text — sorting the strings would
put `1.10` first because `'1' < '9'`. That is the whole reason `Comparable` exists rather than a
`sortStrings` helper: the type knows its own order and every generic algorithm can then use it. The
`Integer.compare` calls inside are the safe way to compare two `int`s without the subtraction
overflow from Chapter 4.
:::
