---
chapter: 10
part: 1
title: "Object: equals, hashCode, toString"
summary: The methods every object inherits, and the contract that every set, map and comparison quietly depends on.
minutes: 60
tags: [equals, hashCode, toString, records, contracts, collections, Objects]
---

Every class you write extends `Object`, whether you say so or not, and the three methods you will
override all come from it: `equals`, `hashCode` and `toString`. Each has a default that is *correct*
and almost never what you want. The defaults are not broken — they answer a narrower question than
you think they do — and the gap between the narrow answer and the useful one is where most of the
bugs in this chapter live.

This is the chapter that decides whether Chapter 12 works. A `HashSet` that refuses to find the
element you just put in it, a `HashMap` that reports two identical customers as two customers, a
`List.contains` that returns `false` for a value you are looking at — all three are the same bug, and
it is this contract. The compiler will catch exactly one of the ways to break it, so the rest is on
you.

## The four methods you inherit

Start by watching the defaults do their job honestly.

```java run
public class DefaultObject {

    static final class Tag {
        final String label;

        Tag(String label) {
            this.label = label;
        }
    }

    public static void main(String[] args) {
        Tag a = new Tag("invoice");
        Tag b = new Tag("invoice");
        Tag c = a;

        String rendered = a.toString();

        System.out.println("the same reference equals itself: " + a.equals(c));
        System.out.println("a different object with the same label: " + a.equals(b));
        System.out.println("Object.equals is identity, nothing more: " + (a.equals(c) && !a.equals(b)));
        System.out.println("toString begins with the class name: "
                + rendered.startsWith("DefaultObject$Tag@"));
        System.out.println("toString ends with hex digits: "
                + rendered.substring(rendered.indexOf('@') + 1).matches("[0-9a-f]+"));
        System.out.println("printing an object calls toString: " + a.equals(a));
    }
}
```

```text
the same reference equals itself: true
a different object with the same label: false
Object.equals is identity, nothing more: true
toString begins with the class name: true
toString ends with hex digits: true
printing an object calls toString: true
```

Nothing here is a bug. `a.equals(c)` is `true` because `a` and `c` are the *same object* — one
reference, copied. `a.equals(b)` is `false` because `b`, despite carrying the same label, is a
different object at a different address. `Object.equals` is **identity**: it is the `==` test, wrapped
in a method so subclasses can replace it.

The `toString` default is built from the class name and the identity hash code, joined by `@`. The
program never prints those hex digits — it prints a *shape*, because the actual value changes from
run to run and a book that printed it would be wrong by the next run. That is worth noticing as a
habit: when a value is not reproducible, assert a property of it instead of the value.

The `@` form is not meant to be read by users. It is a debugging aid that tells you the type and lets
you tell two instances apart. As soon as a human reads your output — a log line, an error message, a
report — you owe them a `toString` that says something.

## equals is identity until you say otherwise

A **value class** is one where two instances with the same data are interchangeable. `Money` is the
example: two amounts of 1250 pence in the same currency are the same amount, and no caller should
have to care which object they were handed.

```java run
import java.util.Objects;

public class ValueEquals {

    static final class Money {
        private final long cents;
        private final String currency;

        Money(long cents, String currency) {
            this.cents = cents;
            this.currency = Objects.requireNonNull(currency, "currency");
        }

        @Override
        public boolean equals(Object other) {
            if (this == other) {
                return true;
            }
            if (!(other instanceof Money money)) {
                return false;
            }
            return cents == money.cents && currency.equals(money.currency);
        }

        @Override
        public int hashCode() {
            return Objects.hash(cents, currency);
        }

        @Override
        public String toString() {
            return String.format("%s %.2f", currency, cents / 100.0);
        }
    }

    public static void main(String[] args) {
        Money a = new Money(1250, "GBP");
        Money b = new Money(1250, "GBP");
        Money c = new Money(1250, "USD");

        System.out.println("a prints as: " + a);
        System.out.println("a.equals(b), same value: " + a.equals(b));
        System.out.println("hashCodes agree: " + (a.hashCode() == b.hashCode()));
        System.out.println("a.equals(c), different currency: " + a.equals(c));
        System.out.println("a.equals(null): " + a.equals(null));
        System.out.println("a.equals(a String): " + a.equals("1250 GBP"));
    }
}
```

```text
a prints as: GBP 12.50
a.equals(b), same value: true
hashCodes agree: true
a.equals(c), different currency: false
a.equals(null): false
a.equals(a String): false
```

Four things are happening in that `equals`, and each is a rule rather than a preference.

`this == other` is checked first and returns `true` immediately. It is a cheap shortcut that also
guarantees the reflexive rule — `x.equals(x)` — for every object, including one holding a `NaN` field
where a field-by-field comparison would return `false`.

`!(other instanceof Money money)` handles two cases at once. If `other` is `null`, `instanceof` is
`false`, so a null argument returns `false` instead of throwing — the contract requires `false` for
`null`, not an exception. If `other` is some unrelated type, it also returns `false`, which is what
lets you compare a `Money` to a `String` without a cast blowing up. The **pattern variable** `money`
is bound only inside the branch that succeeded, so there is no cast and no way to get it wrong.

The field comparison uses `currency.equals(...)` for the `String` and `==` for the `long`. That
distinction is Chapter 3 and Chapter 2 arriving at once: `==` compares values for a primitive and
identities for a reference. Comparing two `String` fields with `==` is the single most common
`equals` bug in Java.

`hashCode` is `Objects.hash(cents, currency)` — the same two fields, in the same order. That is the
entire contract, and the next section is about what happens when you break it.

### The signature is `equals(Object)`, and `@Override` is how you find out

The parameter type is the whole method. `equals(Object)` overrides; `equals(Money)` is a different
method that happens to share a name, and it will never be called by a collection.

```java bad
public class BadEquals {

    static final class Point {
        final int x;
        final int y;

        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        @Override
        public boolean equals(Point other) {
            return other != null && other.x == x && other.y == y;
        }
    }

    public static void main(String[] args) {
        System.out.println(new Point(1, 2).equals(new Point(1, 2)));
    }
}
```

```text
error: method does not override or implement a method from a supertype
```

The author's intent is clear and the code is reasonable-looking, and javac rejects it:
`method does not override or implement a method from a supertype`. The `@Override` annotation is what
turns a silent, invisible bug into a compile error.

Now delete that one annotation and watch what the trap looks like when nothing stops it.

```java run
import java.util.HashSet;
import java.util.Set;

public class OverloadEquals {

    static final class Point {
        final int x;
        final int y;

        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public boolean equals(Point other) {
            return other != null && other.x == x && other.y == y;
        }
    }

    public static void main(String[] args) {
        Point p = new Point(1, 2);
        Point q = new Point(1, 2);

        System.out.println("direct call, argument typed Point: " + p.equals(q));
        System.out.println("the same call through an Object reference: "
                + ((Object) p).equals((Object) q));

        Set<Point> seen = new HashSet<>();
        seen.add(p);
        seen.add(q);
        System.out.println("a HashSet holding them: " + seen.size() + " entries");
    }
}
```

```text
direct call, argument typed Point: true
the same call through an Object reference: false
a HashSet holding them: 2 entries
```

This compiles with no warning at all, and the first line says `true`. The `equals` that ran is the
*overload* `equals(Point)`, because the argument's static type is `Point` and javac picks the most
specific applicable method. The code looks like it works.

The second line is the same comparison with both sides widened to `Object`. Now the only `equals` in
scope is `Object`'s, so the answer is `false`. And the third line is what a collection does — `HashSet`
calls `equals(Object)`, because that is the signature `Object` declares — so two points that compare
equal hold `2 entries` in a set.

That is why the annotation matters more here than almost anywhere else. `@Override` is not a comment;
it is an assertion the compiler checks, and it is the only thing standing between a working-looking
`equals` and a class that every collection silently mishandles.

:::tip
An IDE's *generate `equals` and `hashCode`* command is worth using once to see the shape, and worth
not using afterwards. The generated version is correct and includes a `getClass()` test that is often
not what you want, and reading it teaches you the contract faster than writing it from memory.
:::

:::note
`Objects.hash` boxes its arguments into an array and calls `Arrays.hashCode`, so it allocates on every
call. For a class used as a map key in a hot loop that is measurable. The hand-written form
`Long.hashCode(cents) * 31 + currency.hashCode()` allocates nothing and is what a profiler will
eventually push you toward. Write the readable one first; this is a chapter about correctness.
:::

## The two rules, and which one the compiler can see

The contract has two halves, and they are not equally well defended.

**Rule one — equal objects must have equal hash codes.** If `a.equals(b)` is `true`, then
`a.hashCode() == b.hashCode()` must also be `true`. This is the rule collections depend on.

**Rule two — `equals` must be an equivalence relation.** Reflexive (`x.equals(x)`), symmetric
(`x.equals(y)` implies `y.equals(x)`), transitive, and consistent: the same comparison must keep
returning the same answer as long as nothing relevant changed.

Break rule one and the compiler may help you. Watch.

```java warn
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class NoHashCode {

    static final class Badge {
        final String code;

        Badge(String code) {
            this.code = code;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Badge badge && badge.code.equals(code);
        }
    }

    public static void main(String[] args) {
        Badge issued = new Badge("A-17");
        Badge lookedUp = new Badge("A-17");

        System.out.println("equals says they are the same: " + issued.equals(lookedUp));

        Set<Badge> seen = new HashSet<>();
        seen.add(issued);
        seen.add(lookedUp);
        System.out.println("a set of equal values holds: " + seen.size() + " entries");

        Map<Badge, String> owner = new HashMap<>();
        owner.put(issued, "Ada");
        System.out.println("map.get with an equal key: " + owner.get(lookedUp));
        System.out.println("the map still holds: " + owner.size() + " entry");
    }
}
```

```text
warning: [overrides] Class Badge overrides equals, but neither it nor any superclass overrides hashCode method
```

`Badge` overrides `equals` and forgets `hashCode`, and `-Xlint:all` names the mistake exactly:
`[overrides] Class Badge overrides equals, but neither it nor any superclass overrides hashCode
method`. This is a `warn` block, not a `run` block, because under this book's flags `-Werror` turns
that warning into a build failure — which is the right setting for a project and the reason the
diagnosis is worth quoting rather than paraphrasing.

Now the part the compiler cannot see.

```java run
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class BadHashCode {

    static final class Badge {
        final String code;
        final String holder;

        Badge(String code, String holder) {
            this.code = code;
            this.holder = holder;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Badge badge && badge.code.equals(code);
        }

        @Override
        public int hashCode() {
            return holder.hashCode();
        }
    }

    public static void main(String[] args) {
        Badge issued = new Badge("A-17", "Ada");
        Badge lookedUp = new Badge("A-17", "Grace");

        System.out.println("equals says they are the same: " + issued.equals(lookedUp));
        System.out.println("their hashCodes agree: " + (issued.hashCode() == lookedUp.hashCode()));

        Set<Badge> seen = new HashSet<>();
        seen.add(issued);
        seen.add(lookedUp);
        System.out.println("a set of equal values holds: " + seen.size() + " entries");

        Map<Badge, String> owner = new HashMap<>();
        owner.put(issued, "Ada");
        System.out.println("map.get with an equal key: " + owner.get(lookedUp));
        System.out.println("the map still holds: " + owner.size() + " entry");
    }
}
```

```text
equals says they are the same: true
their hashCodes agree: false
a set of equal values holds: 2 entries
map.get with an equal key: null
the map still holds: 1 entry
```

`BadHashCode` *does* override `hashCode`. It just bases it on `holder` while `equals` compares
`code`. There is no warning, because no warning is possible: `holder.hashCode()` is a perfectly valid
`hashCode` in isolation, and only the relationship between it and `equals` makes it wrong. The
compiler cannot check that relationship, so the failure surfaces at run time as arithmetic that does
not add up — the two badges are equal, their hash codes are not, and every hash-based collection
believes them to be different values.

Look at what the set reports: `2 entries` for what `equals` insists is one value. And the map is
worse than wrong, because it is *silently* wrong. `owner.get(lookedUp)` returns `null` even though an
equal key is in the map, and `owner.size()` still says `1`. The entry is there. You cannot reach it.

:::pitfall
**`equals` without `hashCode` is the bug everyone knows about; `equals` and `hashCode` disagreeing
about which fields matter is the one that ships.** The first is a lint warning. The second is
silence, and it passes every unit test that does not put the object in a `HashSet` or a `HashMap`.
When you write one of the pair, write the other on the next line and use the same fields in the same
order.
:::

### Why a bucket cares

`HashMap` stores entries in an array of buckets and picks the bucket with `hashCode`. A lookup
therefore happens in two stages: `hashCode` narrows to a bucket, and `equals` finds the entry inside
it. If two equal objects hash differently, the second stage never runs — the lookup is looking in a
bucket the entry was never put in.

This also explains the shape of a hash collision, which is *not* a bug. Two different objects are
allowed to share a hash code; the bucket simply holds both and `equals` separates them. A hash
function that returns `0` for everything is correct and useless — every lookup degrades to a linear
scan of the whole map. Correctness comes from rule one; speed comes from spreading the values out.

:::note
A `HashMap` bucket holding many entries converts from a linked list to a red-black tree once it passes
eight entries, which turns the worst case for that bucket from O(n) to O(log n). It does not rescue a
constant `hashCode` — the entries are still in one bucket — it only makes the collapse less
catastrophic. The defence is a real hash function, not the tree.
:::

## Records: the contract, written for you

A `record` is a class whose entire purpose is to hold data, and the compiler writes the three methods
we have been hand-writing.

```java run
import java.lang.reflect.Modifier;
import java.util.HashSet;
import java.util.Set;

public class RecordKey {

    record Point(int x, int y) {
    }

    public static void main(String[] args) {
        Point p = new Point(3, 4);
        Point q = new Point(3, 4);

        System.out.println("printed: " + p);
        System.out.println("equals: " + p.equals(q));
        System.out.println("hashCodes agree: " + (p.hashCode() == q.hashCode()));

        Set<Point> distinct = new HashSet<>();
        distinct.add(p);
        distinct.add(q);
        System.out.println("a set of equal records holds: " + distinct.size() + " entry");

        System.out.println("components are readable: " + p.x() + "," + p.y());
        System.out.println("the class is final: " + Modifier.isFinal(Point.class.getModifiers()));
        String methods = java.util.Arrays.stream(Point.class.getDeclaredMethods())
                .map(java.lang.reflect.Method::getName)
                .sorted()
                .reduce((left, right) -> left + ", " + right)
                .orElse("");
        System.out.println("the methods it was given: " + methods);
    }
}
```

```text
printed: Point[x=3, y=4]
equals: true
hashCodes agree: true
a set of equal records holds: 1 entry
components are readable: 3,4
the class is final: true
the methods it was given: equals, hashCode, toString, x, y
```

`Point[x=3, y=4]` is the generated `toString` — the class name and each component with its accessor
name. `equals` and `hashCode` are derived from all components, which is why the two `Point`s are
equal, agree on their hash code, and collapse to `1 entry` in a `HashSet`. The reflection at the end
confirms the whole generated surface: `equals, hashCode, toString, x, y`.

The class is `final`, and that matters more than it looks. Rule two's hardest case is a subclass that
wants to be "equal but extra", and the language removes it here by forbidding subclasses altogether.

:::tip
Reach for a `record` whenever the answer to *"what is this class?"* is a list of fields. You get the
three methods, immutability, and a readable `toString` for one line of code. Hand-write `equals` and
`hashCode` only when the class is not a plain data holder — when identity is meaningful, or when only
some fields participate in equality.
:::

## Why the key must not move

Immutability is not a style preference in a map key. It is what keeps rule one true over time.

```java run
import java.util.HashMap;
import java.util.Map;

public class MutableKey {

    static final class Session {
        String user;

        Session(String user) {
            this.user = user;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Session s && s.user.equals(user);
        }

        @Override
        public int hashCode() {
            return user.hashCode();
        }

        @Override
        public String toString() {
            return "Session[" + user + "]";
        }
    }

    public static void main(String[] args) {
        Map<Session, Integer> visits = new HashMap<>();
        Session s = new Session("ada");
        visits.put(s, 1);
        System.out.println("lookup before the change: " + visits.get(s));

        s.user = "grace";
        System.out.println("the key now prints as: " + s);
        System.out.println("lookup after the change: " + visits.get(s));
        System.out.println("a fresh equal key finds it: " + visits.get(new Session("grace")));
        System.out.println("the map still holds: " + visits.size() + " entry");
        System.out.println("the value is still in there: " + visits.containsValue(1));
    }
}
```

```text
lookup before the change: 1
the key now prints as: Session[grace]
lookup after the change: null
a fresh equal key finds it: null
the map still holds: 1 entry
the value is still in there: true
```

The sequence is worth following slowly. `visits.put(s, 1)` computes `s.hashCode()` from
`"ada".hashCode()` and files the entry in that bucket. Then `s.user = "grace"` changes the hash code
of the key *while it is sitting in the map* — and the map has no idea. It is still in the `"ada"`
bucket.

Now every lookup is computed against the new hash code. `visits.get(s)` asks for the `"grace"` bucket,
which does not contain the entry. A brand-new `Session("grace")` hashes to the same place as `s` does
now, and it still does not find it, because the entry is somewhere else entirely. And yet
`containsValue(1)` is `true` and `size()` is `1`: the data is present, reachable by iteration, and
unreachable by key.

This is the failure that makes people distrust `HashMap` when the real problem is a mutable key. The
fix is not in the map. It is `final` on the fields that `equals` and `hashCode` read.

:::danger
**Never let a field used by `hashCode` be reassignable.** The damage is not a wrong answer at the
moment of mutation — it is that the map becomes permanently inconsistent with no exception, no
warning, and no way to detect it except by iterating and comparing. If a key must change, remove it
from the map, change it, and put it back.
:::

## toString is for humans

`toString` has no contract at all, which is exactly why it needs a decision. It is called by string
concatenation, by `print` and `println`, by debuggers, and by `List.toString` on every element.

```java run
import java.util.List;
import java.util.Objects;

public class ToString {

    static final class Order {
        final String id;
        final List<String> items;

        Order(String id, List<String> items) {
            this.id = id;
            this.items = List.copyOf(items);
        }

        @Override
        public String toString() {
            return "Order " + id + " (" + items.size() + " item(s)) " + items;
        }
    }

    public static void main(String[] args) {
        Order order = new Order("A-17", List.of("pen", "ink"));

        System.out.println(order);
        System.out.println("concatenation calls toString: " + ("sending " + order));
        System.out.println("a list prints its elements: " + List.of(order));
        System.out.println("a null in a concatenation becomes: " + (Object) null);
        System.out.println("String.valueOf(null): " + String.valueOf((Object) null));
        System.out.println("Objects.toString with a fallback: "
                + Objects.toString(null, "<none>"));
        System.out.println("the log never sees the word null: "
                + !(order + " " + Objects.toString(null, "<none>")).contains("null"));
    }
}
```

```text
Order A-17 (2 item(s)) [pen, ink]
concatenation calls toString: sending Order A-17 (2 item(s)) [pen, ink]
a list prints its elements: [Order A-17 (2 item(s)) [pen, ink]]
a null in a concatenation becomes: null
String.valueOf(null): null
Objects.toString with a fallback: <none>
the log never sees the word null: true
```

The first three lines are three callers that never name `toString`: `println`, the `+` operator, and
a `List` rendering its elements. That is why a useful `toString` on one class makes every containing
collection readable for free.

The last four lines are the `null` trap. A `null` inside a concatenation becomes the four letters
`null` rather than an exception, so a log line can read `customer null` and look like data.
`Objects.toString(value, fallback)` is the explicit form: pass a fallback and the word `null` never
reaches the log. The final line asserts the property rather than the string — the composed message
genuinely contains no `null` substring.

:::note
`toString` is for a human reading a log or a debugger, and it is not a serialization format. Do not
parse it, do not assert on it in a test that matters, and do not let another program's correctness
depend on its exact wording. Change it freely; that is what it is for.
:::

:::scenario The customer report that counts everyone once

A nightly job counts orders per customer, and it does not work.

:::solution
The map is doing exactly what it was told. `Customer` has no `equals`, so it inherits identity from
`Object` and every `new Customer(email)` is a distinct key — however many times the same address
appears.

```java run
import java.util.HashMap;
import java.util.Map;

public class Scenario {

    static final class Customer {
        final String email;

        Customer(String email) {
            this.email = email;
        }
    }

    static Map<Customer, Integer> countOrders(String[] emails) {
        Map<Customer, Integer> counts = new HashMap<>();
        for (String email : emails) {
            Customer key = new Customer(email);
            counts.put(key, counts.getOrDefault(key, 0) + 1);
        }
        return counts;
    }

    public static void main(String[] args) {
        String[] emails = {
            "ada@example.com", "grace@example.com", "ada@example.com",
            "ada@example.com", "grace@example.com"
        };

        Map<Customer, Integer> counts = countOrders(emails);
        int largest = counts.values().stream().mapToInt(Integer::intValue).max().orElse(0);
        long distinctEmails = java.util.Arrays.stream(emails).distinct().count();

        System.out.println("orders received: " + emails.length);
        System.out.println("distinct customers reported: " + counts.size());
        System.out.println("customers actually present: " + distinctEmails);
        System.out.println("the largest count in the report: " + largest);
        System.out.println("every row in the report reads 1: " + (largest == 1));
    }
}
```

```text
orders received: 5
distinct customers reported: 5
customers actually present: 2
the largest count in the report: 1
every row in the report reads 1: true
```

Five orders arrived. The report says **five distinct customers** and the largest count is **1**. The
input plainly contains two customers, and one of them ordered three times.

The code is not wrong in any way a reader would notice. `countOrders` creates a `Customer` key per
email, and calls `counts.getOrDefault(key, 0) + 1`. That line is correct — for any key type that has
an `equals`. `Customer` does not have one, so every `new Customer(email)` is a distinct key no matter
how many times the same email appears. The map is doing precisely what it was told.

The interesting part is *how* it fails. There is no exception. There is no warning. The report is
well-formed, the counts are all present, and the total still adds to five. It is wrong only in the
one number a human would check by hand, and it would go unnoticed for as long as nobody checked.
:::

## Solutions

### 1. Give the key an `equals` and a `hashCode`

```java run
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Sol1 {

    static final class Customer {
        final String email;

        Customer(String email) {
            this.email = Objects.requireNonNull(email, "email");
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Customer c && c.email.equals(email);
        }

        @Override
        public int hashCode() {
            return email.hashCode();
        }

        @Override
        public String toString() {
            return email;
        }
    }

    public static void main(String[] args) {
        String[] emails = {
            "ada@example.com", "grace@example.com", "ada@example.com",
            "ada@example.com", "grace@example.com"
        };

        Map<Customer, Integer> counts = new HashMap<>();
        for (String email : emails) {
            counts.merge(new Customer(email), 1, Integer::sum);
        }

        System.out.println("orders received: " + emails.length);
        System.out.println("distinct customers reported: " + counts.size());
        System.out.println("ada's count: " + counts.get(new Customer("ada@example.com")));
        System.out.println("grace's count: " + counts.get(new Customer("grace@example.com")));
        System.out.println("the counts add back to the input: "
                + (counts.values().stream().mapToInt(Integer::intValue).sum() == emails.length));
    }
}
```

```text
orders received: 5
distinct customers reported: 2
ada's count: 3
grace's count: 2
the counts add back to the input: true
```

Two lines of code fix it: `equals` comparing `email`, and `hashCode` returning `email.hashCode()`.
The report now reads `2` distinct customers, `ada` at `3` and `grace` at `2`, and the counts add back
to the five orders received. Note the deliberate consistency: both methods read the same single
field, which is the only way rule one can hold. The `merge(key, 1, Integer::sum)` is a smaller
improvement — it replaces `getOrDefault` plus `put` with one call, so the counting logic appears once.

`Objects.requireNonNull(email, "email")` in the constructor is the third line of defence: a `null`
email would make `email.hashCode()` throw at an unpredictable later moment, and it is far better to
refuse the value at the point where you still know who passed it.

### 2. Use a record and let the compiler write the pair

```java run
import java.lang.reflect.Modifier;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Sol2 {

    record Sale(String region, String product) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", "pen"),
            new Sale("north", "pen"),
            new Sale("south", "pen"),
            new Sale("north", "ink")
        );

        Map<Sale, Integer> tally = new LinkedHashMap<>();
        for (Sale sale : sales) {
            tally.merge(sale, 1, Integer::sum);
        }

        System.out.println("sales logged: " + sales.size());
        System.out.println("distinct region/product pairs: " + tally.size());
        tally.forEach((key, count) ->
                System.out.println("  " + key.region() + "/" + key.product() + " -> " + count));
        System.out.println("no component can be reassigned: "
                + java.util.Arrays.stream(Sale.class.getDeclaredFields())
                        .allMatch(f -> Modifier.isFinal(f.getModifiers())));
    }
}
```

```text
sales logged: 4
distinct region/product pairs: 3
  north/pen -> 2
  south/pen -> 1
  north/ink -> 1
no component can be reassigned: true
```

`Sale` is a `record`, so `equals`, `hashCode` and `toString` are derived from `region` and `product`
with no source at all. The two identical `north/pen` sales collapse to a count of `2`, the three
distinct pairs are all present, and the reflection at the end confirms what makes the key safe:
every component is `final`, so the hash code cannot change underneath the map.

`LinkedHashMap` is used so the output order is the insertion order rather than a hash order. That is
a real choice and not decoration: a `HashMap` would print the same three rows in an order that varies
with the hash codes, and a book that printed them would be a book that fails its own test. **When you
print a map, choose a map whose order you can state.**

### 3. Make `equals` symmetric

```java run
public class Sol3 {

    static class Colour {
        final String name;

        Colour(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Colour c && name.equals(c.name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static final class Rgb extends Colour {
        final int rgb;

        Rgb(String name, int rgb) {
            super(name);
            this.rgb = rgb;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Rgb r && r.rgb == rgb && name.equals(r.name);
        }

        @Override
        public int hashCode() {
            return name.hashCode() * 31 + rgb;
        }
    }

    static class StrictColour {
        final String name;

        StrictColour(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other != null && other.getClass() == getClass()
                    && name.equals(((StrictColour) other).name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static final class StrictRgb extends StrictColour {
        final int rgb;

        StrictRgb(String name, int rgb) {
            super(name);
            this.rgb = rgb;
        }

        @Override
        public boolean equals(Object other) {
            return other != null && other.getClass() == getClass()
                    && ((StrictRgb) other).rgb == rgb && name.equals(((StrictRgb) other).name);
        }

        @Override
        public int hashCode() {
            return name.hashCode() * 31 + rgb;
        }
    }

    static void report(String title, Object parent, Object child) {
        boolean up = parent.equals(child);
        boolean down = child.equals(parent);
        System.out.println(title);
        System.out.println("  parent.equals(child): " + up);
        System.out.println("  child.equals(parent): " + down);
        System.out.println("  symmetric: " + (up == down));
    }

    public static void main(String[] args) {
        report("instanceof, which lets a subclass in:",
                new Colour("teal"), new Rgb("teal", 0x008080));
        report("getClass(), which does not:",
                new StrictColour("teal"), new StrictRgb("teal", 0x008080));
    }
}
```

```text
instanceof, which lets a subclass in:
  parent.equals(child): true
  child.equals(parent): false
  symmetric: false
getClass(), which does not:
  parent.equals(child): false
  child.equals(parent): false
  symmetric: true
```

`instanceof` is the convenient test and it has a cost. `named.equals(exact)` is `true` because an
`Rgb` *is a* `Colour` and the names match. `exact.equals(named)` is `false` because a plain `Colour`
is not an `Rgb` and has no `rgb` to compare. Two objects, two answers to the same question — rule two
is broken.

`getClass() == getClass()` closes it: a `Colour` and an `Rgb` are never equal in either direction.
The pair is now symmetric, and the price is that a subclass instance can never equal a superclass
instance even when every inherited field agrees. That is a deliberate trade — the language gives you
`instanceof` for *"is this the same value"* and `getClass` for *"is this exactly the same type"*, and
you pick per hierarchy.

### What asymmetry does to a set

The pair above is not merely untidy. A `HashSet` decides whether an element is already present by
calling `equals` on the **argument**, so an asymmetric relation makes the set's behaviour depend on
the order things arrived in.

```java run
import java.util.HashSet;
import java.util.Set;

public class SymmetrySet {

    static class Parent {
        final String name;

        Parent(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Parent p && name.equals(p.name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static final class Child extends Parent {
        final int extra;

        Child(String name, int extra) {
            super(name);
            this.extra = extra;
        }

        @Override
        public boolean equals(Object other) {
            return other != null && other.getClass() == getClass()
                    && ((Child) other).extra == extra && name.equals(((Child) other).name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static Set<Parent> inOrder(Parent first, Parent second) {
        Set<Parent> seen = new HashSet<>();
        seen.add(first);
        seen.add(second);
        return seen;
    }

    public static void main(String[] args) {
        Parent p = new Parent("x");
        Child c = new Child("x", 1);

        System.out.println("parent.equals(child): " + p.equals(c));
        System.out.println("child.equals(parent): " + c.equals(p));

        Set<Parent> parentFirst = inOrder(p, c);
        Set<Parent> childFirst = inOrder(c, p);

        System.out.println("size after parent then child: " + parentFirst.size());
        System.out.println("size after child then parent: " + childFirst.size());
        System.out.println("the one-entry set reports contains(parent): " + childFirst.contains(p));
        System.out.println("the one-entry set reports contains(child): " + childFirst.contains(c));
    }
}
```

```text
parent.equals(child): true
child.equals(parent): false
size after parent then child: 2
size after child then parent: 1
the one-entry set reports contains(parent): true
the one-entry set reports contains(child): true
```

Two objects. Insert them in one order and the set holds two entries; insert them in the other order
and it holds one. The hash codes agree, so both land in the same bucket and `equals` is genuinely
consulted — which is what exposes the asymmetry. `Parent.equals(Child)` is `true`, so the second
insertion is treated as a duplicate; `Child.equals(Parent)` is `false`, so it is not. Same two
values, different set, decided by history.

Then look at what the one-entry set reports: `contains(parent)` is `true` *and* `contains(child)` is
`true`, for two values it cannot both be holding. A set that says yes to two things and stores one
is not a set in any sense a caller can rely on.

:::pitfall
**Never mix the two tests across a hierarchy.** If the parent's `equals` uses `instanceof` and the
child's uses `getClass`, the relation is asymmetric in a way that neither class reveals on its own.
Whichever test you choose, every class in the hierarchy must choose the same one — and if you cannot
promise that, `record` or `final` is the safer design.
:::

### 4. Null-safe comparison with `Objects`

```java run
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Sol4 {

    static final class Ticket {
        final String id;
        final String assignee;

        Ticket(String id, String assignee) {
            this.id = Objects.requireNonNull(id, "id");
            this.assignee = assignee;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Ticket t
                    && id.equals(t.id)
                    && Objects.equals(assignee, t.assignee);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, assignee);
        }

        @Override
        public String toString() {
            return "Ticket[" + id + (assignee == null ? ", unassigned" : ", " + assignee) + "]";
        }
    }

    public static void main(String[] args) {
        Ticket open = new Ticket("T-1", null);
        Ticket alsoOpen = new Ticket("T-1", null);
        Ticket taken = new Ticket("T-1", "ada");

        boolean survived;
        try {
            survived = open.equals(alsoOpen);
        } catch (NullPointerException e) {
            survived = false;
        }

        System.out.println("two unassigned tickets are equal: " + open.equals(alsoOpen));
        System.out.println("their hashCodes agree: " + (open.hashCode() == alsoOpen.hashCode()));
        System.out.println("an assigned ticket differs: " + open.equals(taken));
        System.out.println("no NullPointerException from the null field: " + survived);

        Map<Ticket, String> log = new HashMap<>();
        log.put(open, "opened");
        System.out.println("lookup with an equal key holding a null: " + log.get(alsoOpen));
        System.out.println("printed: " + open);
        System.out.println("requireNonNull names the argument it rejected:");
        try {
            new Ticket(null, "ada");
        } catch (NullPointerException e) {
            System.out.println("  " + e.getMessage());
        }
    }
}
```

```text
two unassigned tickets are equal: true
their hashCodes agree: true
an assigned ticket differs: false
no NullPointerException from the null field: true
lookup with an equal key holding a null: opened
printed: Ticket[T-1, unassigned]
requireNonNull names the argument it rejected:
  id
```

A `null` field is where a hand-written `equals` throws instead of answering. `assignee` is optional,
so it is `null` for an unassigned ticket, and `assignee.equals(t.assignee)` would throw a
`NullPointerException` the moment it is reached. `Objects.equals(assignee, t.assignee)` is null-safe
in both directions, and `Objects.hash(id, assignee)` treats `null` as a value rather than an error.

The two unassigned tickets are equal, they agree on their hash code, and the map lookup with an equal
key succeeds — the `null` field participated correctly in both halves of the contract. The `try`
around `new Ticket(null, "ada")` prints `id`, which is the string passed to `Objects.requireNonNull`:
a failure that names the argument it rejected rather than a bare `NullPointerException` pointing at
a line number.

## Key takeaways

- `Object.equals` is identity, not content. Two objects with identical data are unequal until you
  override `equals` — and a `HashMap` key without one is a different key every time.
- Override `equals` and `hashCode` together, from the same fields, in the same order. Equal objects
  must produce equal hash codes; the compiler warns about a missing `hashCode` but is silent about a
  wrong one.
- The signature is `equals(Object)`. Write `equals(Point)` and you have written an overload that a
  direct call still finds and no collection ever calls — put `@Override` on it so javac says so.
- `instanceof` makes `equals` convenient across a hierarchy and asymmetric if a subclass compares
  more fields. `getClass()` makes it symmetric and forbids cross-type equality. Choose per hierarchy
  and use the same test in every class of it.
- An asymmetric `equals` makes a `HashSet`'s size depend on insertion order, and lets `contains`
  answer `true` for two values the set cannot both be holding. Rule two is not politeness — it is
  what makes a collection's behaviour a function of its contents.
- A field read by `hashCode` must not be reassignable. Mutating a key already in a map loses the
  entry without an exception: the value is still there, iterable, and unreachable by key.
- A `record` generates `equals`, `hashCode`, `toString` and accessors from its components, and is
  `final` — which removes the subclass problem before you can create it.
- `Objects.equals` and `Objects.hash` are null-safe in both directions; `Objects.requireNonNull`
  fails early with the argument's name. Hand-written comparisons throw on `null` where the contract
  says `false`.
- `toString` is called by `+`, by `println`, and by every collection that contains the object. A
  `null` renders as the word `null`; `Objects.toString(value, fallback)` is how you stop that.

## Practice

- [ ] Write a `Book` class with an `isbn` and a `title`. Decide which fields belong in `equals` and
      justify it in one sentence — then make the other choice and describe what breaks.
- [ ] Take the `Session` from this chapter and make the key safe by construction rather than by
      discipline. Which field do you make `final`, and what does the class lose?
- [ ] Build a `HashSet<String>` and a `HashSet<Customer>` from the same five emails. Explain the two
      sizes using the bucket mechanism rather than "one has `equals`".
- [ ] Write a `record Money(long cents, String currency)` and a `Map<Money, Integer>` of
      transactions. Print a total per currency, sorted, without a `TreeMap`.
- [ ] Deliberately break symmetry with a parent using `instanceof` and a child using `getClass()`.
      Find an input where a `HashSet` holds two elements it considers equal.
- [ ] Write a `toString` for a class with a nullable field that never emits the word `null`, and
      prove it with an assertion rather than by reading the output.

## Solutions to the practice problems

The practice problems are open-ended by design — several have more than one defensible answer, and the
justification is the point. Sketch answers, in order:

1. `isbn` alone makes two copies of the same edition equal, which is usually what a library wants —
   a second copy of a book is the same book. Adding `title` makes equality stricter and quietly
   breaks the moment a publisher corrects a typo in the title of an edition already catalogued.
2. `final String user` plus a constructor is the answer. The class loses the ability to rename a user
   in place, which forces the map's owner to remove-and-reinsert — which is the correct, visible
   operation.
3. Five emails give a `HashSet<String>` of size 2 and a `HashSet<Customer>` of size 5. `String` has a
   real `equals` and `hashCode`, so the five insertions hash into two buckets and the second stage
   collapses the duplicates.
4. A `TreeMap<String, Long>` accumulates by currency and gives sorted output for free; the `record`
   makes the key immutable so the accumulation is safe.
5. A parent using `instanceof` and a child using `getClass()` gives `parent.equals(child) == true`
   and `child.equals(parent) == false` — and the set that follows depends on insertion order, as
   `SymmetrySet` showed. The asymmetry is the defect; the order-dependence is the symptom.
6. Assert the property: `!rendered.contains("null")`. Asserting the exact string couples the test to
   the wording, which is the thing `toString` is free to change.
