---
chapter: 14
part: 2
title: Lambdas and Method References
summary: Pass behaviour as a value — write the body and nothing else, capture only what is safe to capture, and reach for a method reference when a name already exists.
minutes: 60
tags: [lambdas, functional-interfaces, method-references, closures, capture, composition]
---

Until Java 8, passing behaviour meant writing a class. A single-line comparison became a file, or an
anonymous class with six lines of ceremony around the one line that mattered. Lambdas removed the
ceremony, and the language paid for it with a rule: a lambda needs a **functional interface** — a type
with exactly one abstract method — to be the target.

That constraint is the whole design. A lambda is not an object with a type of its own; it is a
*body* that the compiler attaches to whichever functional interface the surrounding context requires.
Everything in this chapter follows from it: why a lambda cannot be its own type, why `this` behaves
the way it does, and why the rules about what a lambda may capture are stricter than they first look.

## A lambda is an interface implementation with the ceremony removed

```java run
public class Lambdas {

    interface Transform {
        String apply(String text);
    }

    public static void main(String[] args) {
        Transform upper = text -> text.toUpperCase();
        Transform exclaim = text -> text + "!";
        Transform anonymous = new Transform() {
            @Override
            public String apply(String text) {
                return text.toUpperCase();
            }
        };

        System.out.println("lambda: " + upper.apply("ada"));
        System.out.println("chained: " + exclaim.apply(upper.apply("ada")));
        System.out.println("anonymous class: " + anonymous.apply("ada"));
        System.out.println("both are Transform instances: "
                + (upper instanceof Transform) + " and " + (anonymous instanceof Transform));
        System.out.println("they are different classes: "
                + (upper.getClass() != anonymous.getClass()));
        System.out.println("the lambda body is the only thing you had to write");
    }
}
```

```text
lambda: ADA
chained: ADA!
anonymous class: ADA
both are Transform instances: true and true
they are different classes: true
the lambda body is the only thing you had to write
```

The lambda and the anonymous class do the same job, and the difference is what you had to type. The
anonymous class repeats the interface name, the method name, the parameter type and the return type;
the lambda writes `text -> text.toUpperCase()` and lets the compiler read the rest from `Transform`.

`upper instanceof Transform` is `true`, because the lambda *is* a `Transform` — the compiler has made
one for you. But `upper.getClass() != anonymous.getClass()`, and the lambda's class is not one you can
name. That is deliberate: the class is an implementation detail, so nothing you write should depend on
it. A lambda has no identity of its own to depend on.

:::note
A lambda is not a way to make a new type. It is a way to supply the one method a type already requires.
When you find yourself wanting the lambda to carry state or expose more than one method, the answer is
a class — or, more often, a `record` with a method.
:::

## The interfaces you will actually use

`java.util.function` holds the standard shapes, and almost everything you write is one of five.

```java run
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;

public class Functional {

    public static void main(String[] args) {
        Function<String, Integer> length = String::length;
        Predicate<String> longerThanThree = text -> text.length() > 3;
        Consumer<String> print = text -> System.out.println("  consumed " + text);
        Supplier<String> greeting = () -> "hello";
        BiFunction<Integer, Integer, Integer> add = Integer::sum;

        System.out.println("Function: " + length.apply("ada"));
        System.out.println("Predicate: " + longerThanThree.test("ada")
                + " and " + longerThanThree.test("grace"));
        print.accept("a line");
        System.out.println("Supplier: " + greeting.get());
        System.out.println("BiFunction: " + add.apply(3, 4));
        System.out.println("they all live in: " + Function.class.getPackageName());
    }
}
```

```text
Function: 3
Predicate: false and true
  consumed a line
Supplier: hello
BiFunction: 7
they all live in: java.util.function
```

`Function<T, R>` takes one argument and returns a value. `Predicate<T>` takes one and returns a
`boolean` — which is why `test` reads oddly at first, since `Predicate` predates the convention of
naming the method after the thing. `Consumer<T>` takes one and returns nothing. `Supplier<T>` takes
nothing and returns one. `BiFunction<T, U, R>` takes two and returns one.

The `Bi` prefix is the pattern for arity, and there is no `TriFunction` because almost nobody needs
one. When you do, you write it — a three-parameter interface with one method is four lines.

`String::length` used as a `Function<String, Integer>` is a method reference, which the next section
covers. What matters here is that it is *shaped* like a function, so it fits.

## What a lambda may capture

A lambda can read local variables from the enclosing method, but only ones that are **final or
effectively final** — never reassigned after they are initialised.

```java run
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;

public class Capture {

    public static void main(String[] args) {
        String prefix = "id-";
        int count = 3;
        List<String> names = new ArrayList<>(List.of("a", "b"));

        Function<String, String> tag = name -> prefix + name;
        Supplier<Integer> size = () -> count + names.size();

        System.out.println("captured a String: " + tag.apply("x"));
        System.out.println("captured an int and a reference: " + size.get());

        names.add("c");
        System.out.println("a captured reference sees later changes: " + size.get());
        System.out.println("the local itself was never reassigned: " + (count == 3));
        System.out.println("so the lambda is legal without being final");
    }
}
```

```text
captured a String: id-x
captured an int and a reference: 5
a captured reference sees later changes: 6
the local itself was never reassigned: true
so the lambda is legal without being final
```

Both `prefix` and `count` are read by the lambdas, and neither is declared `final`. They are
*effectively* final: the compiler checks that they are never assigned after their initialiser, and that
is enough.

`names` is different in an important way. The lambda captured the **reference**, so when `names.add("c")`
runs later, `size.get()` returns `6` rather than `5`. The variable could not be reassigned; the object
it points at can change freely. That distinction — the variable is frozen, the object is not — is the
thing to hold on to.

The restriction is not arbitrary. A lambda may run later, on another thread, after the method that
created it has returned. If it captured a mutable local by reference, the value it read would depend on
when it ran, and there would be no way for the compiler to reason about the method at all.

What happens when you break the rule is worth seeing once.

```java bad
import java.util.function.Supplier;

public class NotFinal {

    public static void main(String[] args) {
        int total = 0;
        Supplier<Integer> read = () -> total;
        total = 1;
        System.out.println(read.get());
    }
}
```

```text
error: local variables referenced from a lambda expression must be final or effectively final
```

`local variables referenced from a lambda expression must be final or effectively final` — javac names
the variable's role rather than its name, so the message is about the *rule* rather than the offender.
The fix is almost always to introduce a new local that is not reassigned, which is also clearer to read.

## Method references: when the body is just a call

If the whole lambda is a call to a method, name the method instead.

```java run
import java.util.ArrayList;
import java.util.function.Function;
import java.util.function.Supplier;

public class MethodRefs {

    static String shout(String text) {
        return text.toUpperCase() + "!";
    }

    record Name(String first, String last) {
        String full() {
            return first + " " + last;
        }
    }

    public static void main(String[] args) {
        Function<String, String> staticRef = MethodRefs::shout;
        Function<String, Integer> boundRef = "hello"::indexOf;
        Function<String, String> unboundRef = String::trim;
        Supplier<ArrayList<String>> constructorRef = ArrayList::new;
        Function<Name, String> argumentRef = Name::full;

        System.out.println("static:                " + staticRef.apply("ada"));
        System.out.println("bound to an instance:  " + boundRef.apply("l"));
        System.out.println("unbound, on the arg:   " + unboundRef.apply("  spaced  ") + "|");
        System.out.println("constructor:           " + constructorRef.get().getClass().getSimpleName());
        System.out.println("instance on the arg:   " + argumentRef.apply(new Name("ada", "lovelace")));
    }
}
```

```text
static:                ADA!
bound to an instance:  2
unbound, on the arg:   spaced|
constructor:           ArrayList
instance on the arg:   ada lovelace
```

The five forms, and the `::` syntax is the same in all of them — the difference is what is on the left:

- **Static** — `MethodRefs::shout`. The lambda would be `text -> shout(text)`.
- **Bound to an instance** — `"hello"::indexOf`. The receiver is fixed; the argument supplies the
  parameter.
- **Unbound, on the argument** — `String::trim`. The lambda would be `text -> text.trim()`, so the
  first argument becomes the receiver.
- **Constructor** — `ArrayList::new`. A `Supplier` because it takes no arguments.
- **Instance method on an argument** — `Name::full`. Same shape as the unbound form, and the reason
  `Name::full` needs no instance.

The rule for choosing is mechanical: **write the lambda first, then see if it is only a call.** A
method reference is shorter and names an existing thing, which is usually better. But when the lambda
does anything at all — a null check, an extra argument, a transformation — it must stay a lambda, and
forcing a method reference with a helper method can be less readable than the lambda was.

## Composing functions instead of nesting calls

`Function` and `Predicate` have default methods that build new functions out of old ones.

```java run
import java.util.function.Function;
import java.util.function.Predicate;

public class Compose {

    public static void main(String[] args) {
        Function<Integer, Integer> doubleIt = n -> n * 2;
        Function<Integer, Integer> addOne = n -> n + 1;

        System.out.println("andThen: " + doubleIt.andThen(addOne).apply(5));
        System.out.println("compose: " + doubleIt.compose(addOne).apply(5));
        System.out.println("they differ: "
                + (doubleIt.andThen(addOne).apply(5) != doubleIt.compose(addOne).apply(5)));

        Predicate<String> shortWord = text -> text.length() < 4;
        Predicate<String> startsA = text -> text.startsWith("a");

        System.out.println("and:    " + shortWord.and(startsA).test("ada"));
        System.out.println("or:     " + shortWord.or(startsA).test("banana"));
        System.out.println("negate: " + shortWord.negate().test("banana"));
    }
}
```

```text
andThen: 11
compose: 12
they differ: true
and:    true
or:     false
negate: true
```

`andThen` runs this function first, then the argument; `compose` runs the argument first. On `5` with
`doubleIt` and `addOne` they give `11` and `12`, and the difference is only the order.

Read them as a pipeline rather than a nest. `TRIM.andThen(UPPER)` says what happens, in the order it
happens, and a long chain stays readable where `upper(trim(x))` becomes a puzzle of parentheses. The
`Predicate` versions — `and`, `or`, `negate` — are the same idea for conditions, and they let you name
each rule separately and combine them at the call site.

:::tip
Build predicates as small named constants and combine them where they are used. A rule named
`startsWith("a")` is testable on its own, appears in a stack trace with a useful name, and can be
reused. The same logic inlined into a `filter` call can be neither.
:::

## `this` in a lambda is the enclosing `this`

An anonymous class is a class, so it has its own `this` and its own fields. A lambda is not, and this
catches people who are used to the older form.

```java run
public class ThisInLambda {

    String label = "outer field";

    Runnable viaLambda() {
        return () -> System.out.println("lambda sees this.label = " + this.label);
    }

    Runnable viaAnonymous() {
        return new Runnable() {
            String label = "anonymous field";

            @Override
            public void run() {
                System.out.println("anonymous sees this.label = " + this.label);
            }
        };
    }

    public static void main(String[] args) {
        ThisInLambda outer = new ThisInLambda();
        outer.viaLambda().run();
        outer.viaAnonymous().run();
        System.out.println("a lambda does not introduce a new this");
    }
}
```

```text
lambda sees this.label = outer field
anonymous sees this.label = anonymous field
a lambda does not introduce a new this
```

The lambda prints the **outer** field. `this` inside a lambda refers to the instance of the enclosing
method's class, not to the lambda, because the lambda is not an object with a scope of its own.

The anonymous class prints its own field, because it genuinely is a separate class with a field of that
name. If you are converting an anonymous class to a lambda and it reads a field through `this`, the
meaning changes — and the compiler will not warn you, because both versions are legal.

## The checked exception a lambda cannot throw

A functional interface declares one abstract method with a fixed `throws` clause, and most of the
standard ones declare nothing.

```java bad
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Function;

public class CheckedLambda {

    public static void main(String[] args) {
        Function<Path, String> read = path -> Files.readString(path);
        System.out.println(read.apply(Path.of("missing.txt")));
    }
}
```

```text
error: unreported exception IOException; must be caught or declared to be thrown
```

`unreported exception IOException; must be caught or declared to be thrown`. `Files.readString` throws a
checked `IOException`, and `Function.apply` does not declare it — so the lambda body is a method body
that may not throw what it throws.

This is not a limitation of lambdas so much as a consequence of the interface. `Function` was designed
for transformations that cannot fail. When yours can, you have three options: catch inside the lambda
and handle it there, write a functional interface of your own whose method declares `throws`, or wrap
the throwing call in a helper that converts the checked exception into an unchecked one. `Sol3` is the
third, which is the one that keeps the pipeline readable.

:::pitfall
**Do not swallow a checked exception to make a lambda compile.** The quickest fix is a `try` block that
logs and returns `null`, and it turns a failure into a `NullPointerException` three frames later. If the
call can fail, the failure has to go somewhere — up as an unchecked exception, or into a value the
caller must inspect.
:::

:::scenario The list of lambdas that all print the same number

A list of `Supplier<Integer>` is built in a loop, one supplier per iteration, and every one of them
returns the same value.

:::solution
The loop variable is not captured by value; the *variable* is captured, and a mutable holder is the same
variable every round. Java prevents this for a plain `for` loop by requiring the loop variable to be
effectively final — which is why the bug needs a mutable holder to reproduce at all.

```java run
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public class Scenario {

    public static void main(String[] args) {
        List<Supplier<String>> fromForEach = new ArrayList<>();
        for (String name : List.of("ada", "grace", "alan")) {
            fromForEach.add(() -> name);
        }
        System.out.println("for-each captures a fresh variable each round: "
                + fromForEach.stream().map(Supplier::get).toList());

        List<Supplier<Integer>> fromForLoop = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            int copy = i;
            fromForLoop.add(() -> copy);
        }
        System.out.println("a classic for needs the copy: "
                + fromForLoop.stream().map(Supplier::get).toList());

        List<Supplier<Integer>> shared = new ArrayList<>();
        int[] holder = {0};
        for (holder[0] = 0; holder[0] < 3; holder[0]++) {
            shared.add(() -> holder[0]);
        }
        System.out.println("a mutable holder is shared, not captured: "
                + shared.stream().map(Supplier::get).toList());
    }
}
```

```text
for-each captures a fresh variable each round: [ada, grace, alan]
a classic for needs the copy: [0, 1, 2]
a mutable holder is shared, not captured: [3, 3, 3]
```

Three lines, three different outcomes, and the middle one is the surprise for anyone arriving from a
language where the loop variable is shared.

The **for-each** case is correct: `[ada, grace, alan]`. Each iteration gets a fresh `name`, and each
lambda captures its own. This is a language guarantee, not luck.

The **classic `for`** case needs `int copy = i;` inside the body. Without it the code does not compile,
because `i` is reassigned by the increment. The copy is a new variable per iteration, so each lambda
captures a different one.

The **mutable holder** case is the bug: `[3, 3, 3]`. The lambda captured `holder` — one array, shared by
all three suppliers — and reads `holder[0]` when it is *called*, by which time the loop has finished and
the value is `3`. Nothing was captured by value except the reference.

So Java's capture rules remove the most common form of this bug and leave the form that requires a
mutable holder. If you need a per-iteration value, make it a local; if you deliberately want shared
state, a holder is how you say so — and now you know you said it.
:::

## Solutions

### 1. Build the comparator instead of writing it

```java run
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class Sol1 {

    record Entry(String name, long size, long modified) {
    }

    public static void main(String[] args) {
        List<Entry> entries = new ArrayList<>(List.of(
            new Entry("b.txt", 200, 5), new Entry("a.txt", 200, 9),
            new Entry("c.txt", 100, 7)));

        entries.sort(Comparator.comparingLong(Entry::size).thenComparing(Entry::name));
        System.out.println("by size then name: "
                + entries.stream().map(Entry::name).toList());

        entries.sort(Comparator.comparingLong(Entry::modified).reversed());
        System.out.println("newest first: " + entries.stream().map(Entry::name).toList());

        Comparator<Entry> byName = Comparator.comparing(Entry::name);
        System.out.println("a comparator is a value you can pass around: "
                + (byName.compare(new Entry("a", 0, 0), new Entry("b", 0, 0)) < 0));
    }
}
```

```text
by size then name: [c.txt, a.txt, b.txt]
newest first: [a.txt, c.txt, b.txt]
a comparator is a value you can pass around: true
```

`Comparator.comparingLong(Entry::size).thenComparing(Entry::name)` replaces what would have been a
multi-line `compare` with two method references and a tie-break. The tie-break is not optional: two
entries of `200` bytes sort in arrival order without it, and that order is not reproducible from the
data.

`Comparator.comparing(Entry::name)` is a value, and the last line proves it — a comparator can be
stored, passed and tested in isolation. That is the practical difference between `Comparator` and
`Comparable` from Chapter 12: an order expressed as an object can be varied, combined and unit-tested.

### 2. A pipeline of method references

```java run
import java.util.List;
import java.util.function.Function;

public class Sol2 {

    static final Function<String, String> TRIM = String::trim;
    static final Function<String, String> UPPER = String::toUpperCase;
    static final Function<String, String> EXCLAIM = text -> text + "!";

    public static void main(String[] args) {
        Function<String, String> pipeline = TRIM.andThen(UPPER).andThen(EXCLAIM);

        System.out.println(pipeline.apply("  ada  "));
        System.out.println("applied to a list: "
                + List.of("  ada ", " grace", "alan ").stream().map(pipeline).toList());
        System.out.println("compose gives the same pipeline here: "
                + UPPER.compose(TRIM).andThen(EXCLAIM).apply("  ada  ")
                        .equals(pipeline.apply("  ada  ")));
    }
}
```

```text
ADA!
applied to a list: [ADA!, GRACE!, ALAN!]
compose gives the same pipeline here: true
```

Three `Function` constants, combined once into a `pipeline`, then applied to a single value and to a
list. The pipeline is a value: it can be named, reused and passed to `map`, and the list version needs
no change to work on any number of elements.

`TRIM.andThen(UPPER).andThen(EXCLAIM)` and `UPPER.compose(TRIM).andThen(EXCLAIM)` produce the same
function here, which the last line confirms. That is a property of this particular pipeline, not a
general rule — `andThen` and `compose` differ whenever the order matters, and the earlier example with
`doubleIt` and `addOne` is the proof.

### 3. Wrap the checked exception once

```java run
import java.util.List;
import java.util.function.Function;

public class Sol3 {

    interface CheckedFunction<T, R> {
        R apply(T value) throws Exception;
    }

    static <T, R> Function<T, R> unchecked(CheckedFunction<T, R> function) {
        return value -> {
            try {
                return function.apply(value);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };
    }

    public static void main(String[] args) {
        List<String> words = List.of("ada", "grace", "alan");
        System.out.println("lengths: " + words.stream().map(String::length).toList());

        Function<String, Integer> parse = unchecked(Integer::parseInt);
        System.out.println("parsing a good value: " + parse.apply("42"));

        try {
            parse.apply("forty");
        } catch (RuntimeException e) {
            System.out.println("a bad value arrives wrapped: "
                    + e.getCause().getClass().getSimpleName());
        }
    }
}
```

```text
lengths: [3, 5, 4]
parsing a good value: 42
a bad value arrives wrapped: NumberFormatException
```

`CheckedFunction` is a functional interface whose one method declares `throws Exception`. `unchecked`
takes one of those and returns a plain `Function` that catches and rethrows as a `RuntimeException`,
preserving the original as the cause.

That helper is written once and then every throwing call in the codebase can be adapted with one line:
`unchecked(Integer::parseInt)` is a `Function<String, Integer>` that fits a stream. The alternative —
a `try` block inside every lambda — spreads the same six lines everywhere and buries the actual
transformation.

The failure still surfaces, wrapped, with `NumberFormatException` reachable through `getCause()`. That
is the difference between adapting a checked exception and discarding it.

### 4. A functional interface of your own

```java run
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;

public class Sol4 {

    @FunctionalInterface
    interface Rule {
        boolean test(String value);

        default Rule and(Rule other) {
            return value -> test(value) && other.test(value);
        }

        default Rule negate() {
            return value -> !test(value);
        }
    }

    static Rule minLength(int length) {
        return value -> value.length() >= length;
    }

    static Rule startsWith(String prefix) {
        return value -> value.startsWith(prefix);
    }

    public static void main(String[] args) {
        Rule valid = minLength(3).and(startsWith("a"));

        System.out.println("ada:    " + valid.test("ada"));
        System.out.println("alan:   " + valid.test("alan"));
        System.out.println("bo:     " + valid.test("bo"));
        System.out.println("banana: " + valid.test("banana"));
        System.out.println("negated: " + valid.negate().test("banana"));

        long abstractMethods = Arrays.stream(Rule.class.getDeclaredMethods())
                .filter(m -> Modifier.isAbstract(m.getModifiers()))
                .count();
        System.out.println("abstract methods: " + abstractMethods);
        System.out.println("so it is a functional interface: " + (abstractMethods == 1));
    }
}
```

```text
ada:    true
alan:   true
bo:     false
banana: false
negated: true
abstract methods: 1
so it is a functional interface: true
```

`Rule` declares one abstract method and two `default` methods, and `@FunctionalInterface` documents
that. The last two lines verify it by reflection: one abstract method, which is exactly the requirement
for a lambda target. A second abstract method would make `value -> ...` illegal and the annotation a
compile error.

The `and` and `negate` defaults are what make it pleasant to use: `minLength(3).and(startsWith("a"))`
reads as the rule it is, and each half is a separate named function you can test alone.

:::tip
Write your own functional interface when the standard ones do not say what you mean. A `Rule` that
reads `minLength(3).and(startsWith("a"))` documents itself in a way that
`Predicate<String> p = s -> s.length() >= 3 && s.startsWith("a")` does not — and the second version has
no name to appear in a stack trace or a test report.
:::

## Key takeaways

- A lambda is a body attached to a **functional interface** — a type with exactly one abstract method.
  It has no type of its own, and you cannot name its class.
- The five standard shapes are `Function`, `Predicate`, `Consumer`, `Supplier` and `BiFunction`, all in
  `java.util.function`.
- A lambda may capture a local only if it is final or effectively final. The *variable* is frozen; the
  object it points at is not, so a captured list sees later changes.
- Write the lambda first and convert it to a method reference only when the body is nothing but a call.
  The five forms are static, bound, unbound, constructor, and instance-on-an-argument.
- `andThen` and `compose` differ in order: `f.andThen(g)` is `g(f(x))` and `f.compose(g)` is `f(g(x))`.
  `Predicate` adds `and`, `or` and `negate`.
- `this` inside a lambda is the enclosing instance. An anonymous class has its own `this` and its own
  fields, so converting one to a lambda can change what a field read means.
- A lambda cannot throw a checked exception the interface does not declare. Adapt it with a helper that
  preserves the cause, or write your own interface that declares `throws`.
- A for-each loop gives each iteration a fresh variable, so a list of lambdas built in one is correct.
  A classic `for` needs a local copy, and a mutable holder is genuinely shared — all three suppliers
  then read the same final value.

## Practice

- [ ] Write the same operation as an anonymous class, a lambda and a method reference. Say for each what
      the reader has to hold in their head.
- [ ] Build a `Function<String, String>` that trims, lowercases and replaces spaces with hyphens, then
      apply it to a list. Use method references where the body is only a call.
- [ ] Write a lambda that captures a `List` and a lambda that captures an `int`. Mutate both after
      capture and explain the two different outcomes.
- [ ] Write a `@FunctionalInterface` with a `default` method that returns a new instance, and confirm by
      reflection that it still has exactly one abstract method.
- [ ] Take a call that throws a checked exception and adapt it three ways: catch inside the lambda, a
      custom interface declaring `throws`, and a wrapping helper. Say which you would ship.
- [ ] Convert an anonymous class that reads a field through `this` into a lambda and find the case where
      the behaviour changes.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The anonymous class repeats the type and the signature; the lambda states the parameter and the body;
   the method reference names an existing method and says nothing else. The method reference is shortest
   but requires the reader to know what the method does.
2. `String::trim` then `.andThen(String::toLowerCase)` then a lambda for the replacement, because that
   step is not a single call. Applied with `.map(pipeline)` over the list.
3. The `int` must be effectively final or the code does not compile, so a mutation after capture is
   impossible. The `List` is captured by reference, so a later `add` is visible to the lambda.
4. `default` methods are not abstract, so a `default` that returns a new instance leaves the abstract
   count at one and the interface remains a lambda target.
5. Catching inside the lambda buries the handling at every call site. A custom interface is cleanest
   when the exception is expected. The wrapping helper is best when the checked exception is incidental
   to the pipeline.
6. The behaviour changes when the anonymous class declares a field of the same name the lambda would
   read from the outer class — the lambda reads the outer one, the anonymous class reads its own.
