---
chapter: 16
part: 2
title: Records, Enums and Sealed Types
summary: Let the compiler write the value class, fix the set of constants, and close a hierarchy so a missed case becomes a compile error instead of a runtime surprise.
minutes: 55
tags: [records, enums, sealed, pattern matching, immutability, exhaustive switch]
---

A value class — a point, an order line, a configuration entry — is mostly boilerplate: a constructor,
an accessor per field, and `equals`, `hashCode` and `toString`. You wrote all of that by hand in
Chapter 10, and you saw how easy it is to get one of the three contract methods wrong. Three Java
features remove that work from different directions. `record` writes the class for you, `enum` fixes
the set of instances so no fourth one can appear, and `sealed` closes a hierarchy so the compiler
knows every implementation and can tell you when a case is missing.

## A record is a class the compiler writes for you

```java run
import java.lang.reflect.RecordComponent;
import java.util.Arrays;
import java.util.Set;

public class Basics {
    record Point(int x, int y) {}

    public static void main(String[] args) {
        Point p = new Point(3, 4);

        System.out.println("isRecord       = " + Point.class.isRecord());
        System.out.println("components     = " + Arrays.toString(
                Arrays.stream(Point.class.getRecordComponents())
                      .map(RecordComponent::getName)
                      .toArray()));
        System.out.println("accessors      = " + p.x() + ", " + p.y());
        System.out.println("toString       = " + p);
        System.out.println("equals same    = " + p.equals(new Point(3, 4)));
        System.out.println("equals other   = " + p.equals(new Point(3, 5)));
        System.out.println("hashCode match = " + (p.hashCode() == new Point(3, 4).hashCode()));
        System.out.println("works as a key = " + Set.of(p).contains(new Point(3, 4)));
    }
}
```

```text
isRecord       = true
components     = [x, y]
accessors      = 3, 4
toString       = Point[x=3, y=4]
equals same    = true
equals other   = false
hashCode match = true
works as a key = true
```

`record Point(int x, int y) {}` is the entire declaration. From those two components the compiler
generates a `private final` field for each, a canonical constructor taking both, an accessor per
component, and `equals`, `hashCode` and `toString` derived from the components.

The last line of the transcript is the one that matters most. A `Point` works as a `HashSet` member
out of the box, because `equals` and `hashCode` were generated consistently. Everything Chapter 10
made you write by hand — and could get wrong — arrives correct.

Two details are worth reading carefully. `components = [x, y]` comes from `getRecordComponents()`, the
reflective view of the component list; it is what lets a library treat a record as *data* rather than
as a class, and it is why a JSON library can serialise one with no configuration at all. And the
accessor is `x()`, not `getX()`. That is the language's chosen convention, so code calling `getX()` on
a record does not compile.

:::note
A record is still a class. It can implement interfaces, declare static fields and static methods, add
instance methods, and be generic. What it cannot do is hold instance state beyond its components, or
extend another class — it already extends `java.lang.Record`.
:::

### What a record cannot do

```java bad
public class BadRecord {
    record Bad(int x) {
        private int cache;
    }

    public static void main(String[] args) {
        System.out.println(new Bad(1));
    }
}
```

```text
error: field declaration must be static
```

The rejection is about instance state, and the compiler's wording is worth reading twice:
`field declaration must be static`. A record's instance fields *are* its components, so an extra one
would create state that `equals`, `hashCode` and `toString` know nothing about. The generated methods
would then be wrong in a way nobody could see by reading the declaration, so the compiler refuses to
let you get there.

## The compact constructor is where validation goes

A record's canonical constructor is generated, but you can take it over without repeating the
parameter list.

```java run
public class Compact {
    record Range(int lo, int hi) {
        Range {
            if (lo > hi) {
                throw new IllegalArgumentException("lo " + lo + " is above hi " + hi);
            }
        }
    }

    record Name(String first, String last) {
        Name {
            first = first.trim();
            last = last.trim();
            if (first.isEmpty()) {
                throw new IllegalArgumentException("first name is blank");
            }
        }

        String full() {
            return first + " " + last;
        }
    }

    public static void main(String[] args) {
        System.out.println("range      = " + new Range(2, 9));
        System.out.println("normalised = " + new Name("  Ada ", "  Lovelace ").full());

        try {
            new Range(9, 2);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected   = " + e.getMessage());
        }
    }
}
```

```text
range      = Range[lo=2, hi=9]
normalised = Ada Lovelace
rejected   = lo 9 is above hi 2
```

`Range { ... }` — no parentheses, no parameter list — is a **compact constructor**. The parameters are
in scope, and the fields are assigned from them *after* the body runs. That ordering is the whole
point: the body is a place to validate, and to adjust values on their way in.

`Name` does both. `first = first.trim()` reassigns the *parameter*; because the field assignment
happens afterwards, the field receives the trimmed value, and `full()` prints `Ada Lovelace`. A caller
who passes blank space gets an exception rather than a `Name` that looks empty and compares unequal to
every other blank one.

`Range` shows the other half — a constructor that refuses. `new Range(9, 2)` throws before any object
exists, so a `Range` in your hand always satisfies `lo <= hi`. That is a stronger guarantee than a
setter that validates, because there is no window in which the object is invalid. The rule generalises:
**validate in the constructor, and make the type's invariants true for every instance that exists.**

## Records are shallowly immutable, and that is not the same as immutable

`final` on a field stops the *reference* from changing. It says nothing about the object the reference
points at.

```java run
import java.util.Arrays;

public class Shallow {
    record Scores(String student, int[] marks) {}

    public static void main(String[] args) {
        int[] marks = {70, 80};
        Scores s = new Scores("Ada", marks);
        System.out.println("stored          = " + Arrays.toString(s.marks()));

        marks[0] = 0;
        System.out.println("caller mutated  = " + Arrays.toString(s.marks()));

        s.marks()[1] = 0;
        System.out.println("accessor mutated= " + Arrays.toString(s.marks()));

        System.out.println("equals a copy   = " + s.equals(new Scores("Ada", new int[] {0, 0})));
        System.out.println("same contents   = " + Arrays.equals(s.marks(), new int[] {0, 0}));
    }
}
```

```text
stored          = [70, 80]
caller mutated  = [0, 80]
accessor mutated= [0, 0]
equals a copy   = false
same contents   = true
```

Three lines, three separate surprises.

`caller mutated` shows the record holding the *same array* the caller passed. Writing `marks[0] = 0`
after construction changes what the record reports, because there is only one array and both names
point at it.

`accessor mutated` shows the other direction. `s.marks()` hands out that array, so a caller can write
into the record's state without any setter existing anywhere.

`equals a copy = false` is the consequence, and it is the most dangerous of the three because it is
silent. Two `Scores` with identical contents are not equal, because the generated `equals` compares the
`int[]` components with `Objects.equals`, which for an array is `==`. The next line, `same contents =
true` from `Arrays.equals`, proves the data really is identical — the *comparison* is what is broken.

This is the shape of mistake to carry away: **a record gives you value semantics only for components
that already have value semantics.** `String`, `List`, `Set`, `Map` and other records qualify. If you
must hold an array, copy it in the compact constructor *and* copy it again in the accessor — and notice
that switching the component to `List` fixes both problems at once, because `List.copyOf` copies on
the way in and `List.equals` compares contents. That is the first solution below.

## Enums are classes with a fixed instance set

An `enum` declares a closed set of constants, and each constant is a real object that can carry state
and behaviour.

```java run
public class EnumBasics {
    enum Planet {
        MERCURY(3.303e+23, 2.4397e6),
        EARTH(5.976e+24, 6.37814e6),
        MARS(6.421e+23, 3.3972e6);

        private final double mass;    // kilograms
        private final double radius;  // metres

        Planet(double mass, double radius) {
            this.mass = mass;
            this.radius = radius;
        }

        double surfaceGravity() {
            return 6.67300E-11 * mass / (radius * radius);
        }

        double surfaceWeight(double otherMass) {
            return otherMass * surfaceGravity();
        }
    }

    public static void main(String[] args) {
        System.out.printf("count   = %d%n", Planet.values().length);
        for (Planet p : Planet.values()) {
            System.out.printf("%-8s ordinal=%d gravity=%.2f%n", p, p.ordinal(), p.surfaceGravity());
        }
        System.out.println("valueOf = " + Planet.valueOf("MARS"));
        System.out.println("name    = " + Planet.EARTH.name());
        System.out.printf("75kg on MARS = %.2f%n", Planet.MARS.surfaceWeight(75));
    }
}
```

```text
count   = 3
MERCURY  ordinal=0 gravity=3.70
EARTH    ordinal=1 gravity=9.80
MARS     ordinal=2 gravity=3.71
valueOf = MARS
name    = EARTH
75kg on MARS = 278.45
```

`Planet` has two fields, a constructor and two methods. The constants are the only instances that will
ever exist, they are created once when the class is initialised, and the constructor is implicitly
`private` — `new Planet(...)` is not merely discouraged, it does not compile anywhere, including
inside the enum itself.

`ordinal()` is a constant's position, `name()` its identifier, and `values()` the array of all of them
in declaration order. Those two accessors look like conveniences, and one of them is a trap.
`ordinal()` is stable only while nobody reorders or inserts a constant. Persisting an `ordinal()` into
a file or a database column is a bug waiting for the next release; store `name()` and read it back
with `valueOf`.

### Switching on an enum is checked

```java run
public class EnumSwitch {
    enum Level { LOW, MEDIUM, HIGH }

    static int threshold(Level level) {
        return switch (level) {
            case LOW -> 10;
            case MEDIUM -> 50;
            case HIGH -> 90;
        };
    }

    static String note(Level level) {
        return switch (level) {
            case LOW, MEDIUM -> "routine";
            case HIGH -> "escalate";
        };
    }

    public static void main(String[] args) {
        for (Level level : Level.values()) {
            System.out.printf("%-7s threshold=%-3d note=%s%n",
                    level, threshold(level), note(level));
        }
    }
}
```

```text
LOW     threshold=10  note=routine
MEDIUM  threshold=50  note=routine
HIGH    threshold=90  note=escalate
```

`threshold` has no `default` arm and compiles. The compiler knows the complete set of constants, so it
can prove the three arms cover every case, and it will refuse the method the moment a fourth constant
appears. A `default -> 0` would compile too, would look defensive, and would silently swallow exactly
that fourth constant.

`case LOW, MEDIUM ->` shows that arms can group constants when they share a result. That is often the
sign that the two constants want a shared field rather than a shared arm — `Level` could carry a
threshold per constant, and then `threshold` would not need a switch at all. Reach for the switch when
the *behaviour* differs per constant; reach for a field when only the *data* does.

### `values()` hands out a fresh array every time

```java run
import java.util.Arrays;

public class EnumValues {
    enum Suit { CLUBS, DIAMONDS, HEARTS, SPADES }

    public static void main(String[] args) {
        Suit[] first = Suit.values();
        System.out.println("first        = " + Arrays.toString(first));

        first[0] = Suit.SPADES;
        System.out.println("after write  = " + Arrays.toString(first));
        System.out.println("fresh call   = " + Arrays.toString(Suit.values()));
        System.out.println("constants ok = " + (Suit.values()[0] == Suit.CLUBS));
        System.out.println("same array   = " + (Suit.values() == Suit.values()));
    }
}
```

```text
first        = [CLUBS, DIAMONDS, HEARTS, SPADES]
after write  = [SPADES, DIAMONDS, HEARTS, SPADES]
fresh call   = [CLUBS, DIAMONDS, HEARTS, SPADES]
constants ok = true
same array   = false
```

The mutation does not stick. `first[0] = Suit.SPADES` changed the array the caller holds, and the very
next call printed the original four constants, because `values()` **clones** its backing array on every
call. `same array = false` says the same thing directly: two consecutive calls do not return the same
object.

This is about cost rather than correctness. Because each call allocates, `for (Suit s : Suit.values())`
is fine — the array is produced once, before the loop begins — while a loop written as
`for (int i = 0; i < Suit.values().length; i++)` allocates on every iteration. The measured fact above
is the entire reason: two calls, two arrays.

## Enum iteration order is declaration order

```java run
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class EnumSetMap {
    enum Day { MON, TUE, WED, THU, FRI, SAT, SUN }

    public static void main(String[] args) {
        Set<Day> weekend = EnumSet.of(Day.SUN, Day.SAT);
        System.out.println("EnumSet order  = " + weekend);

        EnumSet<Day> weekdays = EnumSet.complementOf(EnumSet.of(Day.SAT, Day.SUN));
        System.out.println("complement     = " + weekdays);

        Map<Day, Integer> counts = new EnumMap<>(Day.class);
        counts.put(Day.FRI, 3);
        counts.put(Day.MON, 1);
        counts.put(Day.WED, 2);
        System.out.println("EnumMap keys   = " + counts.keySet());
        System.out.println("EnumMap values = " + counts.values());

        Set<Day> hashSet = new HashSet<>(weekend);
        Map<Day, Integer> hashMap = new HashMap<>(counts);
        System.out.println("HashSet equal  = " + hashSet.equals(weekend));
        System.out.println("HashMap equal  = " + hashMap.equals(counts));
    }
}
```

```text
EnumSet order  = [SAT, SUN]
complement     = [MON, TUE, WED, THU, FRI]
EnumMap keys   = [MON, WED, FRI]
EnumMap values = [1, 2, 3]
HashSet equal  = true
HashMap equal  = true
```

`EnumSet.of(Day.SUN, Day.SAT)` printed `[SAT, SUN]`. That is not insertion order — it is **ordinal**
order, and it is a documented property rather than a coincidence of these values. `EnumMap` behaves
the same way: keys were put in the order FRI, MON, WED and the key set printed `[MON, WED, FRI]`.

The implementation explains it. An `EnumSet` is a bit vector over the ordinals and an `EnumMap` is an
array indexed by ordinal, which is also why both are faster and smaller than the general collections
for this job. The ordering is a side effect you get for free.

The last two lines are the part to be careful about. A `HashSet` and a `HashMap` holding enums compare
**equal** to the `EnumSet` and `EnumMap` — set and map equality is content-based, not order-based — but
their iteration order is derived from `hashCode`, and `Enum` does not override `hashCode`. Every
constant inherits `Object`'s identity hash, so the order is effectively arbitrary and can differ
between two runs of the same program.

:::warning
**An enum's `hashCode` is its identity hash code, so a `HashSet<SomeEnum>` has no stable iteration
order.** Print a sorted view, or use `EnumSet`/`EnumMap`, which iterate by ordinal. This is the hazard
Chapter 12 described for hash collections in general; the difference is that `String.hashCode` is
specified by the language, and an enum's is not.
:::

## Sealed types: closing a hierarchy

An interface is open by default: anyone can implement it, including code written years from now by
someone you have never met. That is usually what you want, and it is exactly what you do not want when
the implementations are a known, fixed set.

```java run
import java.util.Arrays;

public class Sealed {
    sealed interface Shape permits Circle, Rect, Line {}

    record Circle(double radius) implements Shape {}
    record Rect(double w, double h) implements Shape {}
    record Line(double length) implements Shape {}

    static double area(Shape shape) {
        return switch (shape) {
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Rect r -> r.w() * r.h();
            case Line l -> 0.0;
        };
    }

    public static void main(String[] args) {
        Shape[] shapes = {new Circle(1), new Rect(2, 3), new Line(5)};
        for (Shape s : shapes) {
            System.out.printf("area=%6.2f  %s%n", area(s), s);
        }
        System.out.println("permitted = " + Arrays.toString(
                Arrays.stream(Shape.class.getPermittedSubclasses())
                      .map(Class::getSimpleName)
                      .toArray()));
    }
}
```

```text
area=  3.14  Circle[radius=1.0]
area=  6.00  Rect[w=2.0, h=3.0]
area=  0.00  Line[length=5.0]
permitted = [Circle, Rect, Line]
```

`sealed interface Shape permits Circle, Rect, Line` names its implementations, and the compiler then
knows the complete set. Two things follow.

`getPermittedSubclasses()` returns the list — `[Circle, Rect, Line]`, in the order they were declared
in the `permits` clause. This is a question that now has a real answer, where an open interface can
only say "somewhere out there".

More useful day to day: `area` has **no `default` arm** and compiles. The compiler can prove the
switch covers every case, because `permits` told it what every case is.

State the payoff as a rule: **a `default` arm in a switch over a sealed type is a missed opportunity.**
It would compile, it would look careful, and it would swallow the next type somebody adds. Leaving it
out means that adding `Pentagon` to the `permits` clause turns every switch in the codebase into a
compile error, at exactly the places a human needs to make a decision.

### The `permits` clause is enforced

```java bad
public class BadSealed {
    sealed interface Shape permits Circle {}

    record Circle(double r) implements Shape {}
    record Square(double side) implements Shape {}

    public static void main(String[] args) {
        System.out.println(new Square(2));
    }
}
```

```text
error: class is not allowed to extend sealed class: Shape (as it is not listed in its 'permits' clause)
```

`Square` implements `Shape` and is not in the list, so the file does not compile. Note the wording:
javac calls it a **sealed class** even though `Shape` is an interface — a detail of the message, not of
the rule.

The permit list is a closed set in both directions. You cannot implement a sealed type without being
listed, and you cannot list a type without it being in the same package or module — which is what
makes the set knowable at compile time in the first place.

## Pattern matching reads the shape of the value

A `case` arm can name the type *and* take the value apart in the same breath.

```java run
public class RecordPattern {
    sealed interface Expr permits Num, Add, Mul {}

    record Num(double value) implements Expr {}
    record Add(Expr left, Expr right) implements Expr {}
    record Mul(Expr left, Expr right) implements Expr {}

    static double eval(Expr e) {
        return switch (e) {
            case Num(double v) -> v;
            case Add(var l, var r) -> eval(l) + eval(r);
            case Mul(var l, var r) -> eval(l) * eval(r);
        };
    }

    public static void main(String[] args) {
        Expr e = new Add(new Num(2), new Mul(new Num(3), new Num(4)));
        System.out.println("expr = " + e);
        System.out.printf("eval = %.1f%n", eval(e));
    }
}
```

```text
expr = Add[left=Num[value=2.0], right=Mul[left=Num[value=3.0], right=Num[value=4.0]]]
eval = 14.0
```

`case Num(double v) -> v` matches a `Num` and binds its component to `v`. `case Add(var l, var r)`
does the same for two components, letting `var` infer each type from the component. This is a **record
pattern**, and because `Expr` is sealed the three arms are exhaustive with no `default`.

The result is a tree interpreter in seven lines: no casts, no `instanceof` chain, no unreachable
fallback. Compare what the same method looks like with only the tools Chapter 09 had — an `instanceof`
test, a cast, then the accessor, repeated once per type, plus a `default` that either throws or returns
something wrong. The nesting in the printed expression shows why this scales: `Mul`'s components are
themselves `Expr`, and the pattern reaches into them without a helper method.

### `non-sealed`: reopening what you closed

```java run
public class NonSealed {
    sealed interface Node permits Leaf, Branch, Wildcard {}

    record Leaf(int value) implements Node {}
    record Branch(Node left, Node right) implements Node {}
    non-sealed interface Wildcard extends Node {}

    record Anything(String tag) implements Wildcard {}

    static String describe(Node n) {
        return switch (n) {
            case Leaf l -> "leaf " + l.value();
            case Branch b -> "branch of " + b.left() + " and " + b.right();
            case Wildcard w -> "wildcard " + w;
        };
    }

    public static void main(String[] args) {
        Node[] nodes = {
            new Leaf(1),
            new Branch(new Leaf(1), new Leaf(2)),
            new Anything("x"),
        };
        for (Node n : nodes) {
            System.out.println(describe(n));
        }
        System.out.println("permitted = " + java.util.Arrays.toString(
                java.util.Arrays.stream(Node.class.getPermittedSubclasses())
                      .map(Class::getSimpleName)
                      .toArray()));
    }
}
```

```text
leaf 1
branch of Leaf[value=1] and Leaf[value=2]
wildcard Anything[tag=x]
permitted = [Leaf, Branch, Wildcard]
```

`sealed` is a promise that can be partially withdrawn. `non-sealed interface Wildcard extends Node`
puts `Wildcard` back into the permitted set while removing the restriction *below* it, so `Anything` —
a type `Node` has never heard of — can implement it.

The switch is still exhaustive, because `case Wildcard w` covers everything underneath `Wildcard`,
including types written later. That is the trade in one line: `non-sealed` buys extensibility back and
gives up the compiler's ability to enumerate the leaves. Use it deliberately. A hierarchy that is
sealed at the top and `non-sealed` in one branch is still sealed at the level you usually care about.

:::scenario The discount rule that arrived on a Friday

A pricing service applies a discount per customer tier. The rules sit behind a `sealed interface
Discount`, and the per-tier policy is an `EnumMap<Tier, Discount>`. On Friday somebody asks for a
fourth rule: a percentage that only applies above a minimum order value.

:::solution
Because `Discount` is sealed and every `switch` over it omits `default`, adding
`record PercentOver(int pct, int minCents) implements Discount {}` to the `permits` clause breaks the
build in every place that has to make a decision. The compiler produces a work list instead of a
runtime surprise.

The other half of the design is the `EnumMap`. The policy is keyed by tier, so a tier with no rule is
a missing key, and `policy.get(tier)` returning `null` would blow up inside the switch. Seeding every
tier explicitly makes the policy total — a property you can check by comparing `policy.size()` with
`Tier.values().length`.

```java run
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public class Scenario {
    enum Tier { BASIC, PRO, ENTERPRISE }

    sealed interface Discount permits Percent, Flat, None {}
    record Percent(int pct) implements Discount {}
    record Flat(int cents) implements Discount {}
    record None() implements Discount {}

    record Order(String id, Tier tier, int units) {}

    static int priceCents(Order order, Discount discount) {
        int gross = order.units() * 1000;
        return switch (discount) {
            case Percent(int pct) -> gross - gross * pct / 100;
            case Flat(int cents) -> Math.max(0, gross - cents);
            case None() -> gross;
        };
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
                new Order("A1", Tier.BASIC, 2),
                new Order("A2", Tier.PRO, 5),
                new Order("A3", Tier.PRO, 1),
                new Order("A4", Tier.ENTERPRISE, 10));

        Map<Tier, Discount> policy = new EnumMap<>(Tier.class);
        policy.put(Tier.BASIC, new None());
        policy.put(Tier.PRO, new Percent(10));
        policy.put(Tier.ENTERPRISE, new Flat(2000));

        Map<Tier, Integer> byTier = new EnumMap<>(Tier.class);
        int total = 0;
        for (Order o : orders) {
            int cents = priceCents(o, policy.get(o.tier()));
            total += cents;
            byTier.merge(o.tier(), cents, Integer::sum);
            System.out.printf("%-3s %-11s %6d%n", o.id(), o.tier(), cents);
        }
        System.out.println("by tier = " + byTier);
        System.out.println("total   = " + total);
    }
}
```

```text
A1  BASIC         2000
A2  PRO           4500
A3  PRO            900
A4  ENTERPRISE    8000
by tier = {BASIC=2000, PRO=5400, ENTERPRISE=8000}
total   = 15400
```

Four orders, three tiers, one total of `15400` cents. The report prints in ordinal order —
`{BASIC=2000, PRO=5400, ENTERPRISE=8000}` — because the accumulator is an `EnumMap`, which is the
ordering property from earlier in this chapter doing real work. `A2` and `A3` are both `PRO` and are
merged into the same entry by `Map.merge`, which is the idiomatic way to accumulate into a map without
a `containsKey` check.

The one thing this design does *not* protect you from is a rule that is wrong rather than missing. The
sealed hierarchy guarantees every case is handled; it cannot guarantee the handler is correct. That is
what tests are for, and Chapter 19 builds the harness.
:::

## Solutions

### 1. Fix the shallow-immutability trap properly

```java run
import java.util.ArrayList;
import java.util.List;

public class Sol1 {
    record Scores(String student, List<Integer> marks) {
        Scores {
            marks = List.copyOf(marks);
        }
    }

    public static void main(String[] args) {
        List<Integer> marks = new ArrayList<>(List.of(70, 80));
        Scores s = new Scores("Ada", marks);

        marks.set(0, 0);
        System.out.println("caller mutated = " + marks);
        System.out.println("defended       = " + s.marks());
        System.out.println("value kept     = " + (s.marks().get(0) == 70));
        System.out.println("equals works   = " + s.equals(new Scores("Ada", List.of(70, 80))));

        try {
            s.marks().set(0, 1);
        } catch (UnsupportedOperationException e) {
            System.out.println("immutable      = " + e.getClass().getSimpleName());
        }
    }
}
```

```text
caller mutated = [0, 80]
defended       = [70, 80]
value kept     = true
equals works   = true
immutable      = UnsupportedOperationException
```

The component changed from `int[]` to `List<Integer>`, and one line in the compact constructor does
the rest: `marks = List.copyOf(marks)`.

Three problems disappear at once. The caller's later mutation does not reach the record, because
`copyOf` took a copy — `defended = [70, 80]` while the caller's list reads `[0, 80]`. The accessor
cannot be used to write into the record, because `copyOf` returns an immutable list and `set` throws
`UnsupportedOperationException`. And `equals` now works, because `List.equals` compares contents, so
`s.equals(new Scores("Ada", List.of(70, 80)))` is `true`.

The general rule: **choose component types that already have value semantics, and the generated
methods are correct for free.** Reach for the defensive-copy version only when an array or another
mutable type is genuinely forced on you.

### 2. Constant-specific behaviour instead of a switch

```java run
public class Sol2 {
    enum Op {
        PLUS("+") {
            int apply(int a, int b) {
                return a + b;
            }
        },
        MINUS("-") {
            int apply(int a, int b) {
                return a - b;
            }
        },
        TIMES("*") {
            int apply(int a, int b) {
                return a * b;
            }
        };

        private final String symbol;

        Op(String symbol) {
            this.symbol = symbol;
        }

        abstract int apply(int a, int b);

        String symbol() {
            return symbol;
        }
    }

    public static void main(String[] args) {
        for (Op op : Op.values()) {
            System.out.printf("3 %s 4 = %d%n", op.symbol(), op.apply(3, 4));
        }
        System.out.println("count  = " + Op.values().length);
    }
}
```

```text
3 + 4 = 7
3 - 4 = -1
3 * 4 = 12
count  = 3
```

`Op` declares an abstract method and each constant supplies its own body in braces. This is a
**constant-specific class body**: the compiler generates an anonymous subclass per constant, which is
why `apply` can be abstract on the enum itself.

The trade against a switch is worth stating plainly. A switch centralises the behaviour, so one method
shows every case side by side — good when the cases are short and you are comparing them. Constant
bodies distribute the behaviour, so adding an operation means adding one constant and touching nothing
else — good when each case is substantial or carries its own data. Either way the compiler checks
exhaustiveness, because the constant set is closed.

### 3. A sealed event hierarchy with an exhaustive report

```java run
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Sol3 {
    sealed interface Event permits Login, Purchase, Logout {}

    record Login(String user) implements Event {}
    record Purchase(String user, int cents) implements Event {}
    record Logout(String user) implements Event {}

    static String kind(Event e) {
        return switch (e) {
            case Login l -> "login";
            case Purchase p -> "purchase";
            case Logout l -> "logout";
        };
    }

    static int amount(Event e) {
        return switch (e) {
            case Login l -> 0;
            case Purchase p -> p.cents();
            case Logout l -> 0;
        };
    }

    public static void main(String[] args) {
        List<Event> events = List.of(
                new Login("ada"),
                new Purchase("ada", 2500),
                new Purchase("bob", 700),
                new Logout("ada"));

        Map<String, Integer> byKind = new TreeMap<>();
        int revenue = 0;
        for (Event e : events) {
            byKind.merge(kind(e), 1, Integer::sum);
            revenue += amount(e);
        }
        System.out.println("by kind = " + byKind);
        System.out.println("revenue = " + revenue);
        System.out.println("events  = " + events.size());
    }
}
```

```text
by kind = {login=1, logout=1, purchase=2}
revenue = 3200
events  = 4
```

Two `switch` expressions over the same sealed interface, both without `default`. `kind` maps each event
to a label and `amount` extracts a number, and neither needs a cast or a fallback.

The report is a `TreeMap` so the output is sorted and reproducible — the same determinism discipline
from Chapter 12. `revenue = 3200` is the sum of the two purchases only, because `Login` and `Logout`
return `0` from `amount`. Writing that as two separate exhaustive switches rather than one switch
returning a pair is deliberate: each method answers one question, and the compiler checks each of them.

### 4. Replace a stringly-typed field with an enum

```java run
public class Sol4 {
    enum Status {
        DRAFT, PUBLISHED, ARCHIVED;

        static Status parse(String raw) {
            try {
                return valueOf(raw.toUpperCase());
            } catch (IllegalArgumentException e) {
                throw new IllegalArgumentException("unknown status: " + raw);
            }
        }
    }

    public static void main(String[] args) {
        for (String raw : new String[] {"draft", "Published", "ARCHIVED"}) {
            System.out.printf("%-10s -> %s%n", raw, Status.parse(raw));
        }
        try {
            Status.parse("publishd");
        } catch (IllegalArgumentException e) {
            System.out.println("rejected   -> " + e.getMessage());
        }
        System.out.println("states     = " + Status.values().length);
    }
}
```

```text
draft      -> DRAFT
Published  -> PUBLISHED
ARCHIVED   -> ARCHIVED
rejected   -> unknown status: publishd
states     = 3
```

`Status.parse` is the pattern for reading an enum from outside data. `valueOf` throws
`IllegalArgumentException` for an unknown name, and the `catch` turns it into a message that names the
offending input instead of just the constant it could not find.

Note the normalisation: `raw.toUpperCase()` is why `"Published"` parses. That is a decision, not a
detail — it means the wire format is case-insensitive while the enum names stay upper-case. Decide
deliberately, and write it in one place, because the alternative is a `toUpperCase()` sprinkled at
every call site and forgotten at one of them.

## Key takeaways

- A `record` generates the fields, canonical constructor, accessors, `equals`, `hashCode` and
  `toString` from its components, so it is correct as a map key with no hand-written code.
- Accessors are named after the component — `x()`, not `getX()`. A record cannot declare extra
  instance fields or extend a class.
- The compact constructor takes over the canonical constructor without repeating the parameter list.
  Fields are assigned *after* the body, so reassigning a parameter changes what is stored.
- A record is **shallowly** immutable. A component of array type breaks both immutability and the
  generated `equals`; prefer `List` and `List.copyOf`.
- An enum's constants are the only instances, created once, with an implicitly private constructor.
  `ordinal()` is position-dependent and must not be persisted; store `name()`.
- A `switch` over an enum needs no `default`, and omitting it makes a new constant a compile error
  rather than a silent fallthrough.
- `values()` clones its array on every call, so hoist it out of a loop condition.
- `EnumSet` and `EnumMap` iterate in ordinal order and are faster than the general collections. A
  `HashSet` or `HashMap` of enums compares equal to them but has no stable iteration order, because an
  enum inherits `Object`'s identity hash.
- A `sealed` type names its implementations, so a `switch` over it is exhaustive without `default`.
  Adding a permitted type then breaks the build at every decision point — which is the feature.
- Record patterns destructure a value inside a `case` arm, replacing an `instanceof` chain and a cast
  with a single line. `non-sealed` reopens a branch of a sealed hierarchy.

## Practice

- [ ] Rewrite a hand-written value class from your own code as a `record`. List every method the
      compiler now generates and check whether any of them differed from yours.
- [ ] Add a compact constructor to a record that normalises a `String` component to trimmed,
      lower-case form, and prove that no instance can hold an untrimmed value.
- [ ] Take a class with a `String` status field and a handful of `if` comparisons, and replace the
      field with an enum. Say what now fails at compile time that used to fail at runtime.
- [ ] Write a record holding an array, demonstrate that two equal contents compare unequal, then fix
      it two ways — a defensive copy and a `List` component — and say which you would ship.
- [ ] Model a small expression language with a sealed interface and three records, then write `eval`
      using record patterns with no `default` arm.
- [ ] Add a fourth type to that sealed hierarchy and count how many places the compiler now refuses to
      build. Compare that with what would have happened had each switch carried a `default`.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The constructor, one accessor per component, `equals`, `hashCode` and `toString`. The generated
   `equals` and `hashCode` are the interesting ones: if your version used only some of the fields, or
   forgot to keep the two consistent, the record version is a bug fix rather than a rewrite.
2. `record Handle(String raw) { Handle { raw = raw.trim().toLowerCase(); } }`. The proof is that the
   accessor returns the normalised value no matter what the caller passed, and that there is no
   setter, so the normalisation cannot be undone afterwards.
3. Every `switch` and every comparison now has to name an enum constant, so a typo becomes a compile
   error instead of a branch that never runs. The `if ("PUBLSHED".equals(status))` that silently never
   matched cannot be written any more.
4. `equals` compares the array components with `Objects.equals`, which is `==` for arrays, so contents
   are never consulted. The defensive-copy fix keeps the array and makes `equals` correct only if you
   also override `equals` and `hashCode` by hand; the `List` fix is one line and needs no overrides.
   Ship the `List`.
5. `sealed interface Expr permits Lit, Add, Mul {}` with `record Lit(double v)`, `record Add(Expr l,
   Expr r)` and `record Mul(Expr l, Expr r)`. `eval` switches on `case Lit(double v) -> v` and
   `case Add(var l, var r) -> eval(l) + eval(r)`, and so on, with no `default`.
6. One place per switch, and the count is the number of `switch` expressions over that type — the
   build stops at each one. With a `default` arm the same change compiles everywhere and the new type
   silently takes the default branch, which is how a missing case reaches production.
