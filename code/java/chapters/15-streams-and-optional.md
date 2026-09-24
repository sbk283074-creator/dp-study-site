---
chapter: 15
part: 2
title: Streams and Optional
summary: Describe the transformation you want instead of the loop that performs it — and use Optional to make absence a fact the caller has to look at.
minutes: 60
tags: [streams, Optional, collectors, laziness, reduce, parallel, functional]
---

A loop says *how*: initialise an accumulator, iterate, test, mutate, return. A stream says *what*:
filter these, map them like this, sum the result. Both are correct, and the second is usually shorter
and harder to get wrong, because there is no accumulator to initialise and no index to mis-manage.

That is the honest case for streams, and it comes with a cost that the syntax hides: a pipeline is
*lazy*, it can be consumed exactly once, and the order of its stages decides how much work happens. All
three are invisible in the source and all three are the subject of this chapter. `Optional` is the
second half — a return type that makes "there is no value" a fact the caller has to handle rather than
a `null` they can forget.

## A pipeline is a description

```java run
import java.util.List;

public class Pipeline {

    record Order(String customer, int units, boolean paid) {
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("ada", 3, true), new Order("grace", 7, false),
            new Order("ada", 2, true), new Order("alan", 5, true));

        System.out.println("paid units: " + orders.stream()
                .filter(Order::paid).mapToInt(Order::units).sum());

        System.out.println("paid customers: " + orders.stream()
                .filter(Order::paid).map(Order::customer).distinct().sorted().toList());

        System.out.println("orders: " + orders.stream().count());
        System.out.println("any unpaid: " + orders.stream().anyMatch(o -> !o.paid()));
        System.out.println("all paid: " + orders.stream().allMatch(Order::paid));
        System.out.println("no unpaid: " + orders.stream().noneMatch(o -> !o.paid()));
    }
}
```

```text
paid units: 10
paid customers: [ada, alan]
orders: 4
any unpaid: true
all paid: false
no unpaid: false
```

Read the first two statements as sentences. *Paid orders, their units, summed* — `filter`, `mapToInt`,
`sum`. *Paid customers, deduplicated, sorted* — `filter`, `map`, `distinct`, `sorted`, `toList`. The
method names are the sentence, and there is no loop variable anywhere.

The last four lines are the **short-circuiting** terminals. `anyMatch`, `allMatch` and `noneMatch` may
stop before reading the whole stream, and they return a `boolean` rather than a collection — which is
what you want when the question is "is there one" rather than "give me all of them".

:::note
A stream is not a collection and does not replace one. It has no storage, no size you can ask for
cheaply, and no way to reach element *n* without walking past the first *n−1*. Use a stream for a
transformation you perform once; use a collection when you need to hold, index or revisit the data.
:::

## Laziness, measured

The intermediate operations do nothing on their own. Work happens only when a **terminal** operation
asks for a result.

```java run
import java.util.List;

public class Lazy {

    static int calls = 0;

    static int doubleIt(int n) {
        calls++;
        return n * 2;
    }

    public static void main(String[] args) {
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);

        calls = 0;
        List<Integer> all = numbers.stream().map(Lazy::doubleIt).toList();
        System.out.println("collecting everything mapped " + calls + " of " + numbers.size());

        calls = 0;
        List<Integer> firstTwo = numbers.stream().map(Lazy::doubleIt)
                .filter(n -> n > 4).limit(2).toList();
        System.out.println("asking for two stopped after " + calls
                + " of " + numbers.size() + ": " + firstTwo);

        calls = 0;
        numbers.stream().map(Lazy::doubleIt);
        System.out.println("no terminal operation ran map " + calls + " times");
    }
}
```

```text
collecting everything mapped 5 of 5
asking for two stopped after 4 of 5: [6, 8]
no terminal operation ran map 0 times
```

The three lines are the whole lesson. Collecting everything mapped all `5` of the elements, because the
result needed all of them. Asking for **two** results stopped after `4` — the fifth element was never
doubled, because `limit` had what it needed. And a pipeline with no terminal operation ran `map` **0**
times, because nothing ever asked for a value.

That last line is worth dwelling on. `numbers.stream().map(Lazy::doubleIt);` compiles, produces no
warning, and does nothing at all. It looks like a statement and is a no-op — one of the very few places
in Java where a whole expression can be silently discarded.

:::pitfall
**A stream pipeline with no terminal operation is dead code that looks like work.** There is no warning
for it, and in a long method it is easy to write `.map(...)` and forget the `.toList()`. If a
transformation seems to have no effect, check for a missing terminal operation before you check
anything else.
:::

## A stream is consumed once

```java throw
import java.util.List;
import java.util.stream.Stream;

public class Consumed {

    public static void main(String[] args) {
        Stream<String> words = List.of("ada", "grace").stream();

        System.out.println("first pass: " + words.count());
        System.out.println("second pass: " + words.count());
    }
}
```

```text
Exception in thread "main" java.lang.IllegalStateException: stream has already been operated upon or closed
```

The first `count()` works and prints `2`. The second throws
`IllegalStateException: stream has already been operated upon or closed`.

A `Stream` is a one-shot pipeline, not a container. It carries the traversal state, so once a terminal
operation has run it, there is nothing left to traverse. This is not a defect — it is what allows a
stream to be built from a file or a socket and read once, without buffering — but it means a `Stream`
variable in a field or a parameter is almost always a mistake.

What you *can* reuse is the source. `orders.stream()` builds a fresh stream each time, so a `List` can
be streamed as many times as you like. The rule is: keep the collection, make the stream where you
need it.

## Collectors: turning a stream back into a structure

A terminal operation has to produce something. `toList` produces a list; `Collectors` produces almost
anything else.

```java run
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Collecting {

    record Sale(String region, int units) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", 3), new Sale("south", 5),
            new Sale("north", 2), new Sale("south", 1), new Sale("north", 4));

        Map<String, Integer> units = sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new, Collectors.summingInt(Sale::units)));
        System.out.println("units by region: " + units);

        Map<String, Long> counts = sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new, Collectors.counting()));
        System.out.println("count by region: " + counts);

        Map<Boolean, List<Sale>> split = sales.stream().collect(
                Collectors.partitioningBy(sale -> sale.units() >= 3));
        System.out.println("big sales: " + split.get(true).size()
                + ", small sales: " + split.get(false).size());

        System.out.println("joined: " + sales.stream().map(Sale::region)
                .distinct().sorted().collect(Collectors.joining(", ")));
    }
}
```

```text
units by region: {north=9, south=6}
count by region: {north=3, south=2}
big sales: 3, small sales: 2
joined: north, south
```

`groupingBy` is the workhorse, and its three-argument form is the one to learn:
`groupingBy(classifier, mapFactory, downstream)`. The classifier picks the key, the map factory decides
*which map* — `TreeMap::new` here, which is why the regions print sorted — and the downstream collector
decides what each value is: `summingInt` for a total, `counting` for a count, `toList` for the elements
themselves. Leave the map factory out and you get a `HashMap`, with all the ordering trouble from
Chapter 12.

`partitioningBy` is `groupingBy` with a `boolean` key, and it is worth using for that reason: it always
produces **both** keys, so `split.get(false)` is a real list even when it is empty, where a `groupingBy`
would simply have no entry for a key that never occurred.

`joining` is the one that stops you writing a loop with a comma flag, which is the most-repeated
five-line snippet in Java.

## `Optional`: absence as a type

`Optional<T>` is a container that either holds a `T` or holds nothing, and it exists so that "there is
no value" is visible in the signature.

```java run
import java.util.List;
import java.util.Optional;

public class Optionals {

    static Optional<String> find(List<String> names, String target) {
        for (String name : names) {
            if (name.equals(target)) {
                return Optional.of(name);
            }
        }
        return Optional.empty();
    }

    public static void main(String[] args) {
        List<String> names = List.of("ada", "grace", "alan");

        System.out.println("found: " + find(names, "grace"));
        System.out.println("missing: " + find(names, "zoe"));
        System.out.println("orElse: " + find(names, "zoe").orElse("nobody"));
        System.out.println("mapped: " + find(names, "grace").map(String::toUpperCase));
        System.out.println("filtered away: " + find(names, "grace").filter(n -> n.length() > 10));
        System.out.println("isEmpty is the real check: " + find(names, "zoe").isEmpty());
        System.out.println("an empty Optional has no elements: " + find(names, "zoe").stream().count());
    }
}
```

```text
found: Optional[grace]
missing: Optional.empty
orElse: nobody
mapped: Optional[GRACE]
filtered away: Optional.empty
isEmpty is the real check: true
an empty Optional has no elements: 0
```

`Optional.of(name)` for a value that exists, `Optional.empty()` for one that does not, and the methods
that let you work with it without ever checking: `orElse` for a default, `map` to transform the value
*if it is there*, `filter` to keep it only if it passes a test.

The shape of `find` is the important part. It returns `Optional<String>` and there is no path through it
that returns `null`, so the caller's obligation is in the type. `orElse("nobody")` cannot be forgotten
the way a `null` check can — the value is inside the container and you must take it out to use it.

The last line is a small convenience worth knowing: `Optional.stream()` gives you a stream of zero or one
element, which lets an optional slot into a pipeline without a branch.

### The one method not to call

`Optional` has a method that undoes everything it is for.

```java throw
import java.util.Optional;

public class OptionalGet {

    public static void main(String[] args) {
        Optional<String> missing = Optional.empty();
        System.out.println("never reached: " + missing.get());
    }
}
```

```text
Exception in thread "main" java.util.NoSuchElementException: No value present
```

`NoSuchElementException: No value present`. `get()` is the `null` dereference with a better exception
name, and it fails in exactly the same place: at the point of use, far from wherever the value went
missing. It is fine inside an `isPresent()` check, and that pattern is a `null` check with extra steps.

Use `orElse`, `orElseThrow` or `map` instead. `orElseThrow(() -> new IllegalStateException("no user"))`
is the honest version of `get()` — it fails deliberately, with a message that says what was expected.

:::pitfall
**`orElse` evaluates its argument eagerly; `orElseGet` does not.** `orElse(expensiveDefault())` calls
`expensiveDefault()` on every path, including the one where the value is present. When the default is a
method call, a query or an allocation, use `orElseGet(() -> expensiveDefault())` and the work only
happens when it is needed.
:::

### Where `Optional` belongs

```java run
import java.util.Optional;

public class OptionalUse {

    record User(String name, String email) {
    }

    static Optional<String> emailOf(Optional<User> user) {
        return user.map(User::email);
    }

    public static void main(String[] args) {
        System.out.println("present user: " + emailOf(Optional.of(new User("ada", "a@x"))));
        System.out.println("no user at all: " + emailOf(Optional.empty()));

        User anonymous = new User("bob", null);
        System.out.println("a nullable field is still null, not empty: "
                + (anonymous.email() == null));
        System.out.println("and nothing in the type said so");
    }
}
```

```text
present user: Optional[a@x]
no user at all: Optional.empty
a nullable field is still null, not empty: true
and nothing in the type said so
```

`emailOf` takes an `Optional<User>` and returns `Optional<String>`, and `map` does the work: if the user
is there, apply `User::email`; if not, stay empty. There is no `if` anywhere, and `Optional.empty()` in
gives `Optional.empty` out.

The last two lines are the argument against `Optional` as a *field*. `User.email` is a `String`, and
`null` is a perfectly legal value for it, so this class has two ways to say "no email": a `null` field
and — if somebody wraps it — an `Optional` field that is itself never `null` but may be empty. Two
representations of one idea is one too many, and the type does not tell you which one this class uses.

The convention that follows is worth adopting wholesale: **`Optional` for return types, plain values
for fields and parameters.** A field should be non-null and set in the constructor; a parameter that
may be absent is better expressed as an overload or a default than as an `Optional`.

## `reduce`, and why the identity matters

`reduce` folds a stream down to a single value, and whether it needs an **identity** decides what it
returns.

```java run
import java.util.List;

public class Reduce {

    public static void main(String[] args) {
        List<Integer> numbers = List.of(3, 1, 4, 1, 5);

        System.out.println("sum with an identity: " + numbers.stream().reduce(0, Integer::sum));
        System.out.println("max without one: " + numbers.stream().reduce(Integer::max));
        System.out.println("empty without an identity: "
                + List.<Integer>of().stream().reduce(Integer::max));
        System.out.println("empty with an identity: "
                + List.<Integer>of().stream().reduce(0, Integer::sum));
        System.out.println("concatenated: "
                + List.of("a", "b", "c").stream().reduce("", (a, b) -> a + b));
    }
}
```

```text
sum with an identity: 14
max without one: Optional[5]
empty without an identity: Optional.empty
empty with an identity: 0
concatenated: abc
```

With an identity — `reduce(0, Integer::sum)` — the result is a plain value, because the identity answers
the question for an empty stream. Without one, `reduce(Integer::max)` returns an `Optional`, because an
empty stream has no maximum and the type has to say so. The two empty-stream lines are the same rule
from both sides: `Optional.empty` with no identity, `0` with one.

The identity must be a genuine identity for the operation — `0` for addition, `1` for multiplication,
`""` for concatenation. Get it wrong and the result is quietly incorrect rather than an error.

## Parallel streams

`parallelStream()` splits the work across threads, and it is much less often a win than it looks.

```java run
import java.util.List;
import java.util.stream.IntStream;

public class Parallel {

    public static void main(String[] args) {
        List<Integer> numbers = IntStream.rangeClosed(1, 20).boxed().toList();

        System.out.println("sequential count: "
                + numbers.stream().filter(n -> n % 3 == 0).count());
        System.out.println("parallel count:   "
                + numbers.parallelStream().filter(n -> n % 3 == 0).count());

        System.out.println("the two agree: "
                + (numbers.stream().mapToInt(Integer::intValue).sum()
                   == numbers.parallelStream().mapToInt(Integer::intValue).sum()));

        System.out.println("an ordered source keeps its order: "
                + numbers.parallelStream().limit(3).toList());
        System.out.println("even when the work is split across threads");
    }
}
```

```text
sequential count: 6
parallel count:   6
the two agree: true
an ordered source keeps its order: [1, 2, 3]
even when the work is split across threads
```

The counts agree, and an ordered source keeps its order even when the work is split — `limit(3)` on a
parallel stream over a `List` still gives `[1, 2, 3]`. That is guaranteed, not luck: the stream is
*ordered* because its source is a list, and parallel execution preserves encounter order for ordered
streams.

What is not shown here is the cost. Splitting, coordinating and merging has overhead that only pays off
for large inputs with expensive per-element work, and any shared mutable state in a lambda turns a
parallel stream into a data race. **Measure before parallelising, and never reach for it by default.**

:::danger
**Never mutate shared state from a stream lambda.** A `forEach` that adds to a plain `ArrayList` is
incorrect even in a sequential stream and corrupts the list under `parallelStream`. Collect with
`Collectors.toList()`, or use a concurrent collection, and keep the lambda free of side effects.
:::

:::scenario The pipeline that does the expensive work before filtering

A report transforms every row, then keeps the ones it wants. The answer is right and the work is
double what it needs to be.

:::solution
The stages run in the order they are written, so `map` before `filter` transforms every row and throws
most of them away. Swapping the two lines gives the same result and calls the expensive step only for
the rows that survive.

```java run
import java.util.List;

public class Scenario {

    static int expensiveCalls = 0;

    static String expensive(String id) {
        expensiveCalls++;
        return id.toUpperCase();
    }

    public static void main(String[] args) {
        List<String> ids = List.of("a1", "b2", "a3", "b4", "a5", "b6");

        expensiveCalls = 0;
        List<String> late = ids.stream()
                .map(Scenario::expensive)
                .filter(id -> id.startsWith("A"))
                .toList();
        int lateCalls = expensiveCalls;

        expensiveCalls = 0;
        List<String> early = ids.stream()
                .filter(id -> id.startsWith("a"))
                .map(Scenario::expensive)
                .toList();
        int earlyCalls = expensiveCalls;

        System.out.println("rows: " + ids.size());
        System.out.println("both give " + early + ": " + late.equals(early));
        System.out.println("map before filter called the work " + lateCalls + " times");
        System.out.println("filter before map called the work " + earlyCalls + " times");
        System.out.println("calls saved: " + (lateCalls - earlyCalls));
    }
}
```

```text
rows: 6
both give [A1, A3, A5]: true
map before filter called the work 6 times
filter before map called the work 3 times
calls saved: 3
```

Six rows, and the same answer either way: `[A1, A3, A5]`. The difference is entirely in the count.
`map` before `filter` called the expensive step **6** times; `filter` before `map` called it **3** times.
Three calls saved, and the only change is the order of two lines.

This is the one place where laziness does *not* rescue you. The pipeline is lazy in the sense that
nothing runs until the terminal operation, but it is not clever: it applies each stage in the order you
wrote it, element by element, and it has no idea that `expensive` is expensive. **A filter is a
promise to do less work, and it only keeps that promise if it comes first.**

The general rule is to order the stages cheapest-first and most-selective-first: `filter` before `map`,
`map` before `sorted`, and `limit` as early as it can legally go. The last of those is the biggest win
available, because `limit` can stop the whole pipeline — as the earlier measurement showed, asking for
two results out of five did four elements' worth of work and not five.
:::

## Solutions

### 1. Filter before you map

```java run
import java.util.List;

public class Sol1 {

    record Order(String id, int units) {
        boolean isBulk() {
            return units >= 10;
        }
    }

    static int lookups = 0;

    static String lookup(Order order) {
        lookups++;
        return order.id();
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("a", 3), new Order("b", 12), new Order("c", 20), new Order("d", 1));

        lookups = 0;
        List<String> bulk = orders.stream()
                .filter(Order::isBulk)
                .map(Sol1::lookup)
                .sorted()
                .toList();

        System.out.println("bulk ids: " + bulk);
        System.out.println("lookups performed: " + lookups + " of " + orders.size());
        System.out.println("nothing was done for the filtered-out orders: "
                + (lookups < orders.size()));
    }
}
```

```text
bulk ids: [b, c]
lookups performed: 2 of 4
nothing was done for the filtered-out orders: true
```

The `filter` moves in front of the `map`, and the lookup runs `2` times out of `4` rows instead of `4`
times. `Order::isBulk` is a method on the record rather than a lambda, which is worth doing on its own:
the rule has a name, it appears in a stack trace, and it can be tested without a stream.

Nothing about the output changed — `bulk ids: [b, c]` either way. That is the point of this class of
fix: it is pure cost, no behaviour, and therefore free to make.

### 2. Build the report with `groupingBy`

```java run
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Sol2 {

    record Sale(String region, String product, int units) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", "pen", 3), new Sale("south", "pen", 5),
            new Sale("north", "ink", 2), new Sale("south", "ink", 1),
            new Sale("north", "pen", 4));

        System.out.println("units by region: " + sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new, Collectors.summingInt(Sale::units))));

        Map<String, Map<String, Integer>> nested = sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new,
                Collectors.groupingBy(Sale::product, TreeMap::new,
                        Collectors.summingInt(Sale::units))));
        nested.forEach((region, products) ->
                System.out.println("  " + region + " -> " + products));

        System.out.println("top product: " + sales.stream()
                .collect(Collectors.groupingBy(Sale::product, Collectors.summingInt(Sale::units)))
                .entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("none"));
    }
}
```

```text
units by region: {north=9, south=6}
  north -> {ink=2, pen=7}
  south -> {ink=1, pen=5}
top product: pen
```

The one-level version and the two-level version are the same shape: a classifier, a `TreeMap::new`, and
a downstream collector. Nesting them — `groupingBy(region, ..., groupingBy(product, ...))` — produces
the two-level map without a single loop, and both levels are sorted because both map factories say so.

`top product` shows the other half of the idiom: collect into a map, take its `entrySet`, stream that,
and `max(Map.Entry.comparingByValue())`. It returns an `Optional`, and the `orElse("none")` is where the
empty case is handled — once, at the end, rather than with a check inside the loop.

### 3. Chain the optional instead of unwrapping it

```java run
import java.util.Map;
import java.util.Optional;

public class Sol3 {

    static final Map<String, String> CONFIG =
            Map.of("host", "example.com", "port", "8080");

    static Optional<String> raw(String key) {
        return Optional.ofNullable(CONFIG.get(key));
    }

    static Optional<Integer> port() {
        return raw("port").map(Integer::parseInt);
    }

    public static void main(String[] args) {
        System.out.println("host: " + raw("host").orElse("localhost"));
        System.out.println("missing key: " + raw("timeout").orElse("30"));
        System.out.println("port: " + port());
        System.out.println("port or default: " + port().orElse(80));
        System.out.println("filtered: " + port().filter(p -> p > 1024).map(p -> "above 1024"));
        System.out.println("a deferred default: " + raw("timeout").orElseGet(() -> "computed-30"));
    }
}
```

```text
host: example.com
missing key: 30
port: Optional[8080]
port or default: 8080
filtered: Optional[above 1024]
a deferred default: computed-30
```

`raw(key)` is `Optional.ofNullable(CONFIG.get(key))`, which is the bridge from a `null`-returning API to
an `Optional` one. Everything after that is chaining: `orElse` for a default, `map` to convert a
`String` to an `Integer`, `filter` to apply a condition, `orElseGet` for a default that costs
something.

Note the last line: `orElseGet(() -> "computed-30")`. The deferred form is the one to reach for
whenever the default is not a literal, because `orElse` would build it on every call including the ones
where the value was present.

:::warning
`Optional.map` does **not** catch exceptions. `Optional.of("abc").map(Integer::parseInt)` throws
`NumberFormatException` straight out — the `Optional` is a container for absence, not a `try` block.
If the transformation can fail, that is a separate decision, and it needs a `try` of its own.
:::

### 4. Keep the collection, make the stream where you need it

```java run
import java.util.List;
import java.util.stream.Stream;

public class Sol4 {

    record Order(String id, int units) {
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("a", 3), new Order("b", 12), new Order("c", 20));

        List<Order> bulk = orders.stream().filter(order -> order.units() >= 10).toList();

        System.out.println("bulk count: " + bulk.size());
        System.out.println("bulk units: " + bulk.stream().mapToInt(Order::units).sum());
        System.out.println("bulk ids: " + bulk.stream().map(Order::id).toList());

        Stream<Order> once = orders.stream().filter(order -> order.units() >= 10);
        System.out.println("the stream was used once: " + once.count());
        System.out.println("the source list is still usable: "
                + orders.stream().filter(order -> order.units() >= 10).count());
    }
}
```

```text
bulk count: 2
bulk units: 32
bulk ids: [b, c]
the stream was used once: 2
the source list is still usable: 2
```

`bulk` is materialised once with `toList()`, and the three lines that follow each build a fresh stream
from it. That is the pattern that avoids the consumed-stream problem entirely: a `List` can be streamed
any number of times, so the stream never needs to outlive the statement it appears in.

The last two lines make the contrast explicit. `once` is used for exactly one terminal operation and
works; the source `orders` is then streamed again successfully. Nothing about `orders` changed — the
stream was the thing that was one-shot, not the data.

The rule to carry: **never store a `Stream` in a field, never accept one as a parameter you keep, and
never return one you have already read.** Make it, use it, and let it go.

## Key takeaways

- A stream describes a transformation: intermediate operations build the description and a terminal
  operation runs it. Nothing happens without a terminal, and a pipeline with none is silent dead code.
- Pipelines are lazy and short-circuit: `limit` can stop the work early, and a pipeline that needs only
  two results does not process the rest.
- A `Stream` is consumed once. Reuse the collection and build a new stream each time; never store or
  pass a stream that may already have been read.
- `Collectors.groupingBy(classifier, mapFactory, downstream)` is the report-building idiom; the map
  factory is what decides whether the output is sorted, and leaving it out gives a `HashMap`.
- `partitioningBy` always produces both keys, unlike `groupingBy`.
- `Optional` makes absence visible in the signature. Use `orElse`, `orElseGet`, `map` and `filter`;
  avoid `get()`, which is a `null` dereference with a better exception name.
- `orElse` evaluates its argument eagerly; `orElseGet` defers it. Use the second whenever the default
  costs anything.
- `Optional` belongs in return types, not in fields or parameters. A field should be non-null and set
  in the constructor.
- `reduce` with an identity returns a plain value; without one it returns an `Optional`, because an
  empty stream has no answer to give.
- Order the stages cheapest and most-selective first: `filter` before `map`, and `limit` as early as it
  can legally go. A parallel stream is a measured decision, never a default.

## Practice

- [ ] Rewrite a loop you have written recently as a pipeline. Count the lines in each version and say
      which is easier to change.
- [ ] Build a `Map<String, List<String>>` from a list of words, grouped by first letter, sorted by key.
      Then do it with `HashMap` and note what changes.
- [ ] Write a pipeline with a `map` that counts its own calls, then add `limit` in three different
      positions and record the count each time.
- [ ] Take a method that returns `null` for "not found" and change it to return `Optional`. List every
      call site the compiler now forces you to look at.
- [ ] Write `Optional.of("abc").map(Integer::parseInt)` and explain what comes out and why.
- [ ] Take a sequential pipeline and a `parallelStream()` version, and find an input where the parallel
      one is slower. Say what made the difference.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The pipeline is usually shorter and has no accumulator to keep consistent; the loop is easier when
   the body needs `break`, `continue`, or more than one result per element.
2. `groupingBy(word -> word.substring(0, 1), TreeMap::new, Collectors.toList())`. With `HashMap` the
   keys come out in an order derived from `hashCode`, so the report stops being reproducible.
3. With `limit` before the `map`, only the limited elements are mapped; after it, all of them are. The
   count is the evidence.
4. Every call site that used the result directly now fails to compile, which is the point — each one is
   a decision that was previously implicit.
5. It throws `NumberFormatException`. `Optional.map` propagates the exception of the mapping function;
   it does not convert a failure into an empty optional.
6. Small inputs, or per-element work that is already cheap, or a lambda that shares mutable state. The
   splitting and merging overhead dominates when the elements are few or the work is small.
