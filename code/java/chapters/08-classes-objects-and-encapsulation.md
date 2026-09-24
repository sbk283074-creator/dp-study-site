---
chapter: 8
part: 1
title: Classes, Objects and Encapsulation
summary: Define your own types -- fields, constructors, methods -- keep their invariants true with private state, and know when a field belongs to the class rather than the object.
minutes: 60
tags: [classes, objects, constructors, encapsulation, static, final, immutability]
---

Everything so far has used types somebody else defined: `int`, `String`, `int[]`. A class is how you
define one, and the reason it is worth more than a container for fields is that it lets you state a
rule and enforce it. `Account` below promises that a balance is never negative. That promise is not a
comment; it is a consequence of the balance being `private` and the only methods that touch it
checking first.

This is the first chapter where the design of your own types matters, and the theme is that a class
is a *boundary*. Inside it you know what the fields mean and what has to stay true. Outside it,
callers see methods, and the compiler enforces that they cannot reach past them.

## A class is a type you define

```java run
public class Account {
    private long balanceCents;
    private final String owner;

    Account(String owner, long openingCents) {
        this.owner = owner;
        this.balanceCents = openingCents;
    }

    String owner() {
        return owner;
    }

    long balanceCents() {
        return balanceCents;
    }

    void deposit(long cents) {
        if (cents <= 0) {
            throw new IllegalArgumentException("deposit must be positive: " + cents);
        }
        balanceCents += cents;
    }

    boolean withdraw(long cents) {
        if (cents <= 0 || cents > balanceCents) {
            return false;
        }
        balanceCents -= cents;
        return true;
    }

    @Override
    public String toString() {
        return owner + " holds " + balanceCents + " cents";
    }

    public static void main(String[] args) {
        Account account = new Account("ada", 5_000);
        System.out.println(account);

        account.deposit(2_500);
        System.out.println("after deposit:   " + account);

        System.out.println("withdraw 1000    = " + account.withdraw(1_000));
        System.out.println("withdraw 999999  = " + account.withdraw(999_999));
        System.out.println("after attempts:  " + account);

        try {
            account.deposit(-1);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        System.out.println("the balance never went negative: " + (account.balanceCents() >= 0));
    }
}
```

```text
ada holds 5000 cents
after deposit:   ada holds 7500 cents
withdraw 1000    = true
withdraw 999999  = false
after attempts:  ada holds 6500 cents
rejected: deposit must be positive: -1
the balance never went negative: true
```

The pieces are all here and each one has a job. The **fields** hold the state, and they are `private`
so nothing outside the class can read or write them directly. The **constructor** takes the values
that have to be supplied at creation, and it is the only place `owner` is ever written — which is why
`owner` can be `final`. The **methods** are the operations, and two of them enforce the rule:
`deposit` throws on a non-positive amount rather than quietly accepting it, and `withdraw` returns a
boolean rather than allowing an overdraft.

`this.owner = owner` is the idiom for a parameter that shadows a field. `this` is the current object,
so `this.owner` is the field and `owner` is the parameter. Some teams rename the parameter instead;
the convention does not matter, but shadowing a field *without* `this` is a bug the compiler will
happily accept, because you are then assigning the parameter to itself.

The two `withdraw` outcomes are worth comparing. `withdraw(1_000)` returned `true` and the balance
fell; `withdraw(999_999)` returned `false` and the balance did not move. A method that can fail has to
choose between throwing and returning a status, and the choice should follow from whether the failure
is expected. Running out of money is an ordinary outcome of a withdrawal, so it is a `boolean`.
Depositing a negative amount is a programming error, so it throws.

Note also that nothing in the class exposes `balanceCents` as a settable field. There is a
`balanceCents()` reader and no writer at all: the only ways to change the balance are `deposit` and
`withdraw`, and both check. That is encapsulation — not the keyword `private`, but the fact that the
rule lives in one place and cannot be bypassed.

## Constructors, and the one that disappears

A constructor is a method with no return type whose name is the class. Java supplies a **default
constructor** with no arguments — but only while you have written none, which is why the class below
does not get one for free:

```java run
public class Constructors {
    private final String name;
    private final int limit;
    private final boolean active;

    Constructors(String name) {
        this(name, 10);
    }

    Constructors(String name, int limit) {
        this(name, limit, true);
    }

    Constructors(String name, int limit, boolean active) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank");
        }
        if (limit < 0) {
            throw new IllegalArgumentException("limit must not be negative: " + limit);
        }
        this.name = name;
        this.limit = limit;
        this.active = active;
    }

    @Override
    public String toString() {
        return name + "(limit=" + limit + ", active=" + active + ")";
    }

    public static void main(String[] args) {
        System.out.println("one argument   : " + new Constructors("alpha"));
        System.out.println("two arguments  : " + new Constructors("beta", 25));
        System.out.println("three arguments: " + new Constructors("gamma", 0, false));

        try {
            new Constructors("   ");
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        try {
            new Constructors("delta", -5);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
    }
}
```

```text
one argument   : alpha(limit=10, active=true)
two arguments  : beta(limit=25, active=true)
three arguments: gamma(limit=0, active=false)
rejected: name must not be blank
rejected: limit must not be negative: -5
```

The three constructors form a chain. The one-argument constructor calls the two-argument one, which
calls the three-argument one, and **all the real work happens in the last one**. `this(name, 10)` is
how a constructor calls another constructor of the same class, and it must be the first statement —
which is the rule that stops you from half-initialising an object and then chaining.

Putting validation only in the final constructor is deliberate. It is the single place every path
goes through, so a rule added there covers all three entry points; three copies of the check would be
three chances to update two of them. Both rejections in the output come from that one constructor,
which is why they read the same way.

Two rules follow from the output's first three lines. **A constructor's job is to leave the object
valid**, and if it cannot, it throws and no object is created — so there is no state in which a
`Constructors` exists with a blank name. And **the moment you write any constructor, the default one
is gone**: adding `Constructors(String name)` above means `new Constructors()` no longer compiles,
which is a common surprise in a class that previously had no constructors at all.

### final is a promise the compiler keeps

`final` on a field means it is assigned exactly once, and the compiler enforces it:

```java bad
public class FinalAssign {
    public static void main(String[] args) {
        final int limit = 10;
        limit = 20;
        System.out.println(limit);
    }
}
```

```text
error: cannot assign a value to final variable limit
```

On a local variable `final` is a small readability aid. On a **field** it is a design statement: this
value is set during construction and never changes, so no reader of the class has to wonder whether
it can. A field can also be `static final`, which is the idiom for a constant — `static final int
LIMIT = 10;` — and by convention such names are written in capitals.

One caution, because it is the usual mistake: `final` on a reference prevents *reassignment*, not
mutation. `final int[] values` means `values` always points at the same array; `values[0] = 99` is
perfectly legal. Immutability needs more than the keyword, and the last section of this chapter shows
what.

## Encapsulation, measured

The word is usually taught with a diagram, so here is the same rule as two objects that differ in one
keyword:

```java run
public class Encapsulated {
    static final class Open {
        int balanceCents;

        Open(int balanceCents) {
            this.balanceCents = balanceCents;
        }
    }

    static final class Guarded {
        private int balanceCents;

        Guarded(int balanceCents) {
            this.balanceCents = balanceCents;
        }

        int balanceCents() {
            return balanceCents;
        }

        boolean setBalanceCents(int cents) {
            if (cents < 0) {
                return false;
            }
            balanceCents = cents;
            return true;
        }
    }

    public static void main(String[] args) {
        Open open = new Open(100);
        open.balanceCents = -50;
        System.out.println("the open field now holds " + open.balanceCents);

        Guarded guarded = new Guarded(100);
        System.out.println("the guarded setter accepted -50: " + guarded.setBalanceCents(-50));
        System.out.println("the guarded balance is still    " + guarded.balanceCents());
        System.out.println("accepted 250: " + guarded.setBalanceCents(250)
                + ", balance now " + guarded.balanceCents());
    }
}
```

```text
the open field now holds -50
the guarded setter accepted -50: false
the guarded balance is still    100
accepted 250: true, balance now 250
```

`Open` has a public field, so the first thing that happens to it is that it holds `-50` — a value the
class's own name implies is impossible. Nothing in the class was *wrong*; there was simply no place
for a rule to live. `Guarded` has the same field, `private`, and a setter that refuses. The
difference in the output is `false` and `100` against `-50`.

The important part is what did not change: `Guarded` did not get longer by much, and it did not
require the caller to be careful. That is the whole argument for encapsulation, and it is worth
stating in the form that survives contact with real code: **a rule that is enforced in one place is a
rule; a rule that every caller is expected to remember is a comment.**

A caveat in the other direction, because this is the mistake people make after learning the first
one: getters and setters for every field are not encapsulation. A class with `private int x;` and
`public void setX(int x)` has the same lack of invariant as one with a public field, plus more code.
The question is not "is the field private" but "what is true about this object, and where is that
enforced". Some fields should have no setter at all, as `Account.owner` does not.

## static: one copy per class, not per object

An ordinary field gets one copy per object. A `static` field gets **one copy for the class**, shared
by every instance, and a `static` method has no `this` at all:

```java run
public class StaticCount {
    static int created;
    final int serial;

    StaticCount() {
        created++;
        serial = created;
    }

    static int created() {
        return created;
    }

    @Override
    public String toString() {
        return "instance " + serial;
    }

    public static void main(String[] args) {
        System.out.println("before any instance: created = " + StaticCount.created());

        StaticCount first = new StaticCount();
        StaticCount second = new StaticCount();
        StaticCount third = new StaticCount();

        System.out.println(first + ", " + second + ", " + third);
        System.out.println("after three: created = " + StaticCount.created());
        System.out.println("the serials add to " + (first.serial + second.serial + third.serial));
        System.out.println("one field is per class and one is per object");
    }
}
```

```text
before any instance: created = 0
instance 1, instance 2, instance 3
after three: created = 3
the serials add to 6
one field is per class and one is per object
```

`created` counts instances, so it is shared; `serial` is a per-object number, so it is not. The output
shows both: `created` reads `3` from the class, while the three instances kept `1`, `2` and `3`. The
first line, `created = 0` *before* any instance exists, is worth noticing — a `static` field is
initialised when the class is first used, not when the first object is made.

A `static` method cannot read an instance field, because there is no instance to read it from. That is
why `main` is `static`: the JVM calls it before any object of your class exists. It is also why a
`static` method is the right home for a pure function that needs no state, and the wrong home for
anything that does — a `static` mutable field shared by every instance is, in effect, a global
variable, and it is the reason "just make it static" is a fix that spreads.

One habit the compiler will help you keep:

```java warn
public class StaticViaInstance {
    static int created;

    public static void main(String[] args) {
        StaticViaInstance instance = new StaticViaInstance();
        System.out.println(instance.created);
    }
}
```

```text
warning: [static] static variable should be qualified by type name, StaticViaInstance, instead of by an expression
```

Reading a static member through an instance reference compiles but is confusing, because it looks as
if the value belongs to that object. `-Xlint:static` says so, and this book builds with `-Werror`,
so here it is a build failure. Write `StaticViaInstance.created` — the type name — and the reader can
see immediately that there is one copy.

## Immutability, and the defensive copy

An immutable object cannot be changed after construction, which makes it safe to share, safe to use as
a map key, and impossible to break from a distance. `final` fields and no setters get you most of the
way, but not all of it, because a `final` reference to a *mutable* object is still a way in:

```java run
import java.util.Arrays;

public class Immutability {
    static final class Tags {
        private final String[] values;

        Tags(String... values) {
            this.values = values.clone();
        }

        String[] values() {
            return values.clone();
        }

        int count() {
            return values.length;
        }
    }

    public static void main(String[] args) {
        String[] input = {"alpha", "beta"};
        Tags tags = new Tags(input);

        input[0] = "changed";
        System.out.println("mutating the caller's array did not reach the object: "
                + Arrays.toString(tags.values()));

        String[] leaked = tags.values();
        leaked[0] = "leaked";
        System.out.println("mutating the returned array did not either:         "
                + Arrays.toString(tags.values()));

        System.out.println("count is still " + tags.count());
        System.out.println("without the two clone() calls the object would hold "
                + "whatever the caller did next");
    }
}
```

```text
mutating the caller's array did not reach the object: [alpha, beta]
mutating the returned array did not either:         [alpha, beta]
count is still 2
without the two clone() calls the object would hold whatever the caller did next
```

Both `clone()` calls in that class are load-bearing, and the output is the measurement. Without the
copy in the constructor, `input[0] = "changed"` would be visible through `tags.values()` — the object
would have been mutated from outside after construction, and the `final` keyword would not have
prevented it. Without the copy in the accessor, `leaked[0] = "leaked"` would do the same thing.

The rule generalises: **an immutable object must copy any mutable object it receives, and copy any
mutable object it returns.** The copy on the way in is sometimes called a defensive copy and the one
on the way out is the same idea; both exist because handing out a reference to your internals gives
away the ability to change them. The alternative, when the contained object is itself immutable —
a `String`, an `Integer`, a `record` of immutable fields — is that no copy is needed, which is why
`String` and the boxed primitives are so convenient to pass around.

:::pitfall The getter that returns the field

```java
public int[] getValues() {
    return values;              // the caller now owns your array
}
```

A getter written this way hands out a reference to the object's own state, so
`account.getValues()[0] = 0` changes the object — through a method that looks like a reader. The
class still compiles, the fields are still `private`, and the invariant is gone.

The fix is `return values.clone();` for an array, `List.copyOf(...)` for a list (Chapter 12), or a
getter that returns an immutable view. And the same applies to constructors: a constructor that stores
the array it was handed, without copying, has given the caller a permanent handle on the object's
internals.
:::

:::scenario The wallet that spent more than it had

A rewards service has a `Wallet` class with a `balanceCents` field. The balance is checked before
every spend, and the check is correct. Support reports accounts with a negative balance, and the code
that spends money has not changed.

:::solution
The field is public, so the spend method is not the only thing that writes it. Somewhere else — a
batch job, a serialiser, a test helper — assigns to `wallet.balanceCents` directly, and the check in
`spend` never runs. The class has an invariant and no way to enforce it.

```java run
public class Scenario {
    static final class OpenWallet {
        int balanceCents;

        OpenWallet(int balanceCents) {
            this.balanceCents = balanceCents;
        }
    }

    static final class GuardedWallet {
        private int balanceCents;

        GuardedWallet(int balanceCents) {
            this.balanceCents = balanceCents;
        }

        int balanceCents() {
            return balanceCents;
        }

        boolean spend(int cents) {
            if (cents <= 0 || cents > balanceCents) {
                return false;
            }
            balanceCents -= cents;
            return true;
        }
    }

    public static void main(String[] args) {
        OpenWallet open = new OpenWallet(500);
        open.balanceCents -= 800;
        System.out.println("the open wallet holds " + open.balanceCents + " cents");

        GuardedWallet guarded = new GuardedWallet(500);
        System.out.println("spend 800 accepted: " + guarded.spend(800));
        System.out.println("the guarded wallet holds " + guarded.balanceCents() + " cents");

        System.out.println("nothing had to be added to break the first, and nothing can break the second");
    }
}
```

```text
the open wallet holds -300 cents
spend 800 accepted: false
the guarded wallet holds 500 cents
nothing had to be added to break the first, and nothing can break the second
```

`open.balanceCents -= 800;` is a single line that no reviewer would look at twice, and it took the
balance to `-300`. The guarded version refuses the same spend and holds at `500`, and — this is the
part to notice — *nothing was added to it*. No extra validation, no defensive check at the call site:
the rule was already there in `spend`, and making the field private is what made it the only way in.

The generalisation is the one worth carrying out of this chapter. When an invariant is violated in
production, the first question is not "which caller was wrong" but **"how many places can write this
field"**. If the answer is more than one, the invariant was never enforced, and adding a check to each
caller is a race against the next caller.
:::

## Key takeaways

- A class defines a type: `private` fields for state, a constructor that leaves the object valid, and
  methods for the operations. A method that can fail either throws (programming error) or returns a
  status (expected outcome).
- Writing any constructor removes the compiler's default no-argument one, so `new Foo()` stops
  compiling.
- `this(...)` chains one constructor to another and must be the first statement. Put validation in
  the last constructor of the chain so every path goes through it once.
- `final` on a field means assigned exactly once, enforced by the compiler. It prevents reassignment,
  not mutation: `final int[] a` still allows `a[0] = 1`.
- Encapsulation is not "the field is private" — it is that the invariant is enforced in one place.
  Private fields with a setter for each are no safer than public ones.
- A `static` field has one copy per class rather than per object, and is initialised when the class is
  first used. A `static` method has no `this` and cannot read instance state, which is why `main` is
  static.
- Reading a static member through an instance reference compiles but is confusing; `-Xlint:static`
  reports it.
- An immutable object copies every mutable object it receives and every mutable object it returns.
  A getter that returns the internal array hands the caller the ability to change the object.

## Practice

- [ ] Write a `Rectangle` class with `private final` sides, a constructor that rejects a non-positive
      side, and `area`, `perimeter` and `isSquare` methods.
- [ ] Write an immutable `Money` class holding an integer number of cents, with `plus`, `minus` and
      `times` that each return a new instance, and show that the original is unchanged afterwards.
- [ ] Write a `Temperature` class that stores one representation and offers factories and accessors
      for Celsius and Fahrenheit, and check the freezing and boiling points.
- [ ] Write a `Counter` class with a per-object value and a per-class instance count, with an
      `increment` that refuses past a maximum, and print both numbers.

## Solutions

:::solution Exercise 1
The sides are `final`, so there is no setter to write and the validation happens once, in the
constructor:

```java run
public class Sol1 {
    static final class Rectangle {
        private final int width;
        private final int height;

        Rectangle(int width, int height) {
            if (width <= 0 || height <= 0) {
                throw new IllegalArgumentException("sides must be positive: " + width + " x " + height);
            }
            this.width = width;
            this.height = height;
        }

        int width() {
            return width;
        }

        int height() {
            return height;
        }

        int area() {
            return width * height;
        }

        int perimeter() {
            return 2 * (width + height);
        }

        boolean isSquare() {
            return width == height;
        }

        @Override
        public String toString() {
            return width + "x" + height;
        }
    }

    public static void main(String[] args) {
        Rectangle square = new Rectangle(4, 4);
        Rectangle oblong = new Rectangle(4, 6);

        System.out.println(square + " area " + square.area()
                + ", perimeter " + square.perimeter() + ", square: " + square.isSquare());
        System.out.println(oblong + " area " + oblong.area()
                + ", perimeter " + oblong.perimeter() + ", square: " + oblong.isSquare());

        try {
            new Rectangle(0, 5);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        System.out.println("there is no setter, so the sides cannot change after construction");
    }
}
```

```text
4x4 area 16, perimeter 16, square: true
4x6 area 24, perimeter 20, square: false
rejected: sides must be positive: 0 x 5
there is no setter, so the sides cannot change after construction
```

`4x4` has an area and a perimeter of `16`, which is a coincidence of the numbers rather than a
property — `4x6` gives `24` and `20`. The `0 x 5` rejection is the interesting one: without it the
object would exist with a side of zero, every area would be zero, and `isSquare` would still report
`false` for `0x5`, so nothing would look obviously wrong until something divided by the area.
:::

:::solution Exercise 2
Every operation returns a new `Money` and none of them writes a field, which is what makes the class
immutable and safe to share:

```java run
public class Sol2 {
    static final class Money {
        private final long cents;

        private Money(long cents) {
            this.cents = cents;
        }

        static Money of(long cents) {
            return new Money(cents);
        }

        Money plus(Money other) {
            return new Money(cents + other.cents);
        }

        Money minus(Money other) {
            return new Money(cents - other.cents);
        }

        Money times(int factor) {
            return new Money(cents * factor);
        }

        long cents() {
            return cents;
        }

        @Override
        public String toString() {
            return (cents / 100) + "." + String.format("%02d", Math.abs(cents % 100));
        }
    }

    public static void main(String[] args) {
        Money price = Money.of(1_299);
        Money shipping = Money.of(499);

        System.out.println("price         = " + price);
        System.out.println("shipping      = " + shipping);
        System.out.println("plus          = " + price.plus(shipping));
        System.out.println("times 3       = " + price.times(3));
        System.out.println("price after all of that = " + price);
        System.out.println("and a negative amount is representable: "
                + Money.of(100).minus(Money.of(250)));
    }
}
```

```text
price         = 12.99
shipping      = 4.99
plus          = 17.98
times 3       = 38.97
price after all of that = 12.99
and a negative amount is representable: -1.50
```

`price` prints `12.99` before and after `plus` and `times`, which is the assertion that matters — the
operations produced `17.98` and `38.97` and left the original alone. The private constructor plus a
static `of` factory is a small idiom worth knowing: it reads better at the call site than
`new Money(1299)`, and it leaves room to cache or validate later without changing callers.

The last line is the reminder that this is integer arithmetic in cents, so `-1.50` is representable
and `Math.abs` in the formatter is what keeps the sign out of the cents field.
:::

:::solution Exercise 3
One stored field and four conversions around it. Storing both would allow them to disagree:

```java run
import java.util.Locale;

public class Sol3 {
    static final class Temperature {
        private final double celsius;

        private Temperature(double celsius) {
            this.celsius = celsius;
        }

        static Temperature celsius(double value) {
            return new Temperature(value);
        }

        static Temperature fahrenheit(double value) {
            return new Temperature((value - 32) * 5 / 9);
        }

        double celsius() {
            return celsius;
        }

        double fahrenheit() {
            return celsius * 9 / 5 + 32;
        }

        @Override
        public String toString() {
            return String.format(Locale.ROOT, "%.2f C / %.2f F", celsius, fahrenheit());
        }
    }

    public static void main(String[] args) {
        System.out.println("freezing = " + Temperature.celsius(0));
        System.out.println("boiling  = " + Temperature.celsius(100));
        System.out.println("body     = " + Temperature.fahrenheit(98.6));
        System.out.println("37 C in F = " + Temperature.celsius(37).fahrenheit());
        System.out.println("one stored representation, two factories and two accessors");
    }
}
```

```text
freezing = 0.00 C / 32.00 F
boiling  = 100.00 C / 212.00 F
body     = 37.00 C / 98.60 F
37 C in F = 98.6
one stored representation, two factories and two accessors
```

`98.6 F` comes back as `37.00 C`, and `37 C` as `98.6` — the same temperature, and the round trip is
not exactly lossless because `98.6` is not representable in binary (Chapter 4's floating-point
section). `String.format` with `Locale.ROOT` is used for the display so that the decimal separator
does not depend on the machine's locale, which is the kind of thing that turns a passing test into a
failing one on a colleague's laptop.
:::

:::solution Exercise 4
Two counters that look alike and behave differently: `value` is per object, `instances` is per class,
and `max` is per object but never changes:

```java run
public class Sol4 {
    static final class Counter {
        private static int instances;
        private final int max;
        private int value;

        Counter(int max) {
            if (max <= 0) {
                throw new IllegalArgumentException("max must be positive: " + max);
            }
            this.max = max;
            instances++;
        }

        static int instances() {
            return instances;
        }

        boolean increment() {
            if (value == max) {
                return false;
            }
            value++;
            return true;
        }

        int value() {
            return value;
        }

        int max() {
            return max;
        }
    }

    public static void main(String[] args) {
        Counter small = new Counter(3);
        Counter tiny = new Counter(1);

        for (int i = 0; i < 5; i++) {
            System.out.println("increment " + i + " on small: " + small.increment()
                    + " (value " + small.value() + " of " + small.max() + ")");
        }

        System.out.println("tiny increments once: " + tiny.increment()
                + ", then refuses: " + tiny.increment());
        System.out.println("the instance count belongs to the class: " + Counter.instances());
    }
}
```

```text
increment 0 on small: true (value 1 of 3)
increment 1 on small: true (value 2 of 3)
increment 2 on small: true (value 3 of 3)
increment 3 on small: false (value 3 of 3)
increment 4 on small: false (value 3 of 3)
tiny increments once: true, then refuses: false
the instance count belongs to the class: 2
```

`small` accepts three increments and then refuses, `tiny` accepts one and refuses the second, and
`Counter.instances()` reports `2` because both objects share that field. The `static` field is
incremented inside the constructor, which is the only place a new instance can come from — so the
count cannot drift from the number of objects that were actually created, even if a future
constructor is added, as long as it chains to this one.
:::
