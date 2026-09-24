---
chapter: 11
part: 2
title: Generics and Type Erasure
summary: Write one class that works for every type, understand what the compiler keeps and what it throws away, and learn why the throws-away part decides most of the limits.
minutes: 60
tags: [generics, type-erasure, bounds, wildcards, PECS, bridge-methods, raw-types]
---

A type parameter is a promise you make to the compiler and it makes back. You promise that every use of
`T` in a class is the *same* type; the compiler promises to check every use, everywhere, at compile
time, and to insert the casts you would otherwise write by hand. Chapter 10 was about a contract that
collections depend on at run time. This is the contract they depend on at compile time, and it is the
one that catches the mistake before the program runs.

The chapter has two halves and they pull in opposite directions. The first half is what generics *give*
you — a `Holder<T>` that returns a `String` with no cast, and a compiler that refuses to let you put an
`Integer` in it. The second half is what generics *cannot* give you, and the reason is a single design
decision made in 2004: the type parameter is erased. `List<String>` and `List<Integer>` are, at run
time, the same class. Almost every confusing generics error message follows from that one fact.

## A type parameter is a checked promise

```java run
import java.util.function.Function;

public class Box {

    static final class Holder<T> {
        private final T value;

        Holder(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }

        <R> Holder<R> map(Function<T, R> step) {
            return new Holder<>(step.apply(value));
        }

        @Override
        public String toString() {
            return "Holder[" + value + "]";
        }
    }

    public static void main(String[] args) throws Exception {
        Holder<String> name = new Holder<>("Ada");
        Holder<Integer> count = new Holder<>(3);

        System.out.println("name: " + name);
        System.out.println("count: " + count);
        System.out.println("a String with no cast: " + name.get().toUpperCase());
        System.out.println("an Integer with no cast: " + (count.get() + 1));

        Holder<Integer> length = name.map(String::length);
        System.out.println("mapped: " + length);
        System.out.println("the erased return type of get(): "
                + Holder.class.getDeclaredMethod("get").getReturnType());
    }
}
```

```text
name: Holder[Ada]
count: Holder[3]
a String with no cast: ADA
an Integer with no cast: 4
mapped: Holder[3]
the erased return type of get(): class java.lang.Object
```

`Holder<T>` declares one type parameter and uses it in two places: the field and the return of `get()`.
The two call sites then pick different arguments, and neither needs a cast. `name.get()` is a `String`
as far as the compiler is concerned, so `.toUpperCase()` compiles; `count.get()` is an `Integer`, so
`+ 1` compiles. The `<R> Holder<R> map(...)` is a second type parameter on a *method* rather than the
class, and it is what lets a `Holder<String>` become a `Holder<Integer>` without the caller naming
either type.

Now the last line, which is the hinge of the whole chapter. `Holder.class.getDeclaredMethod("get")`
reports a return type of `class java.lang.Object`. The source says `T get()`. The compiled class says
`Object get()`. Both are true, and the difference is **erasure**: `T` exists while javac is reading your
source and does not exist in the bytecode.

The compiler does not lose anything by this. It checks every use of `T` while it still knows what `T`
is, and then it inserts the casts at the points where a value flows out. `name.get().toUpperCase()`
compiles to a `checkcast String` followed by the call. **The cast is still there — you just did not have
to write it, and, crucially, you cannot get it wrong.**

## What erasure actually removes

```java run
import java.util.ArrayList;
import java.util.List;

public class Erasure {

    static final class Holder<T> {
        private final T value;

        Holder(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }
    }

    public static void main(String[] args) throws Exception {
        List<String> words = new ArrayList<>();
        List<Integer> numbers = new ArrayList<>();

        System.out.println("words.getClass(): " + words.getClass().getName());
        System.out.println("numbers.getClass(): " + numbers.getClass().getName());
        System.out.println("one class object for both: "
                + (words.getClass() == numbers.getClass()));

        System.out.println("List.get returns: "
                + List.class.getMethod("get", int.class).getReturnType().getName());
        System.out.println("Holder.get returns: "
                + Holder.class.getDeclaredMethod("get").getReturnType().getName());
        System.out.println("Holder's field is a: "
                + Holder.class.getDeclaredFields()[0].getType().getName());
    }
}
```

```text
words.getClass(): java.util.ArrayList
numbers.getClass(): java.util.ArrayList
one class object for both: true
List.get returns: java.lang.Object
Holder.get returns: java.lang.Object
Holder's field is a: java.lang.Object
```

This is the fact that explains the rest of the chapter. `List<String>` and `List<Integer>` are both
`java.util.ArrayList` at run time, and the reflection API agrees: `List.get` returns `Object`,
`Holder.get` returns `Object`, and the private field that holds the value is an `Object`.

So the type argument is *not* available at run time. There is no way, from an object, to ask what it
holds. The information was used to type-check the program and then discarded — a deliberate choice that
let generics arrive in Java 5 without changing the JVM, at the cost of every limitation in the second
half of this chapter.

:::note
The type parameter is not erased *everywhere* — only from the running program. `Holder.class.getTypeParameters()`
still reports `T`, because the compiler writes it into the class file's metadata as a *signature*
attribute. That is how reflection libraries and `List.of` know what to check. What is gone is the
ability to recover the argument from an **instance**: the class file records the shape of the type, and
each object records only its erased class.
:::

## Raw types: the escape hatch that switches the checks off

Before generics there was only `List`. That type still exists, and using it is called a **raw type**.

```java warn
import java.util.ArrayList;
import java.util.List;

public class RawTypes {

    public static void main(String[] args) {
        List<String> typed = new ArrayList<>();
        typed.add("one");

        List raw = typed;
        raw.add(42);

        System.out.println("the raw list is the typed list: " + (raw == typed));
        System.out.println("the typed view now holds: " + typed);
        System.out.println("and its size is: " + typed.size());
    }
}
```

```text
warning: [rawtypes] found raw type: List
```

This compiles — with two warnings, which is why it is a `warn` block rather than a `run` block. Under
this book's flags `-Werror` turns them into a build failure, which is exactly what you want in a
project: `[rawtypes] found raw type: List`, and then `[unchecked] unchecked call to add(E) as a member
of the raw type List`.

The first warning is the cause and the second is the consequence. `List raw = typed` throws the type
argument away, so `raw.add(42)` has nothing left to check against. If the block did run, it would print
a `List<String>` whose first element is the integer `42` — a heap that has been told one thing and
contains another. Every read from it would then throw a `ClassCastException` somewhere far from the
line that caused it.

Raw types exist for one reason: code written before 2004 had to keep compiling. There is no reason to
write one today, and every reason not to. If you see `[rawtypes]`, the fix is to add the type argument,
not to reach for `@SuppressWarnings`.

## The cast the compiler cannot check

```java warn
import java.util.ArrayList;
import java.util.List;

public class UncheckedCast {

    static List<String> asStrings(Object value) {
        return (List<String>) value;
    }

    public static void main(String[] args) {
        List<Integer> numbers = new ArrayList<>(List.of(1, 2, 3));
        List<String> strings = asStrings(numbers);

        System.out.println("the cast succeeded at run time: "
                + ((Object) strings == (Object) numbers));
        System.out.println("element 0 is really a: " + strings.get(0).getClass().getName());

        try {
            String first = strings.get(0);
            System.out.println("assigned without complaint: " + first);
        } catch (ClassCastException e) {
            System.out.println("it fails only when used: " + e.getClass().getSimpleName());
        }
    }
}
```

```text
warning: [unchecked] unchecked cast
```

This is a `warn` block for a reason, and the warning — `[unchecked] unchecked cast` — is the compiler
telling you precisely what it cannot do. The cast `(List<String>) value` is a cast to `List`, because
the argument is erased. The compiler can see that much. What it *cannot* see is whether the elements
inside are `String`s, and it will not look, because looking would mean checking every element of every
list at every cast.

The second line is the evidence. The cast succeeded — there was nothing to fail — and element 0 is
really a `java.lang.Integer`. The program only breaks on the third line, where the value is finally used
as a `String` and the compiler's inserted `checkcast String` runs.

:::pitfall
**An unchecked cast moves the failure, it does not remove it.** The exception is thrown at the point of
*use*, not the point of the cast, so the stack trace names a line that looks innocent and is nowhere
near the mistake. That is why `@SuppressWarnings("unchecked")` should be treated as a confession: it is
correct only when you can prove the elements really are the right type, and the proof has to live in a
comment next to it.
:::

## Bounds: telling the compiler what `T` can do

An unbounded `T` is only known to be an `Object`, so the only methods you can call on it are the ones
every object has. A **bound** says more.

```java run
import java.util.List;

public class Bounds {

    static <T extends Comparable<T>> T largest(List<T> values) {
        T best = values.get(0);
        for (T value : values) {
            if (value.compareTo(best) > 0) {
                best = value;
            }
        }
        return best;
    }

    static <T extends Number & Comparable<T>> double total(List<T> values) {
        double sum = 0;
        for (T value : values) {
            sum += value.doubleValue();
        }
        return sum;
    }

    public static void main(String[] args) {
        System.out.println("largest word: " + largest(List.of("pear", "apple", "plum")));
        System.out.println("largest number: " + largest(List.of(3, 9, 4)));
        System.out.println("total: " + total(List.of(1, 2, 3, 4)));
        System.out.println("the bound is what lets compareTo be called: "
                + largest(List.of(3, 9, 4)).getClass().getSimpleName());
    }
}
```

```text
largest word: plum
largest number: 9
total: 10.0
the bound is what lets compareTo be called: Integer
```

`<T extends Comparable<T>>` does two things at once. Inside the method, `T` is now known to have a
`compareTo`, so `value.compareTo(best)` compiles — the bound is what makes the method body legal. And at
the call site, the bound *rejects* anything that is not `Comparable`: a `List<Object>` or a `List<int[]>`
will not compile, which is the promise being enforced.

`<T extends Number & Comparable<T>>` shows that a bound may be a list. The first entry may be a class
and the rest must be interfaces, which is a rule about the single-inheritance language underneath:
`Number` is a class and `Comparable` is an interface, and they are joined with `&`.

Note that a bound does not change erasure. `T extends Comparable<T>` erases to `Comparable`, not to
`Object`, because the bound is the most specific thing the compiler knows. That is why the erased
signature of a bounded method is more useful than an unbounded one, and why a raw `Comparable` bound is
sometimes the right tool for interoperating with old code.

## Wildcards, and the two directions of a container

Here is the rule that surprises everyone: `List<Integer>` is **not** a `List<Number>`, even though
`Integer` is a `Number`. Generics are **invariant** — the type argument must match exactly.

The reason is that the other choice is unsound. If `List<Integer>` were a `List<Number>`, you could pass
it to a method that added a `Double`, and the `List<Integer>` you still hold would contain a `Double`.
The compiler would have to insert a cast at every read, and every read could fail. Java rejects the
assignment instead, and wildcards are how you say what you actually meant.

```java run
import java.util.ArrayList;
import java.util.List;

public class Wildcards {

    static double sum(List<? extends Number> values) {
        double total = 0;
        for (Number value : values) {
            total += value.doubleValue();
        }
        return total;
    }

    static void addInts(List<? super Integer> target, int count) {
        for (int i = 1; i <= count; i++) {
            target.add(i);
        }
    }

    static <T> void copy(List<? extends T> from, List<? super T> to) {
        for (T item : from) {
            to.add(item);
        }
    }

    public static void main(String[] args) {
        System.out.println("sum of a List<Integer>: " + sum(List.of(1, 2, 3)));
        System.out.println("sum of a List<Double>: " + sum(List.of(1.5, 2.5)));

        List<Number> numbers = new ArrayList<>();
        addInts(numbers, 3);
        System.out.println("List<Number> after addInts: " + numbers);

        List<Object> objects = new ArrayList<>();
        addInts(objects, 2);
        System.out.println("List<Object> after addInts: " + objects);

        List<Number> sink = new ArrayList<>();
        copy(List.of(4, 5), sink);
        System.out.println("copied Integer into List<Number>: " + sink);
    }
}
```

```text
sum of a List<Integer>: 6.0
sum of a List<Double>: 4.0
List<Number> after addInts: [1, 2, 3]
List<Object> after addInts: [1, 2]
copied Integer into List<Number>: [4, 5]
```

`List<? extends Number>` is a *producer*: you can read `Number`s out of it and you cannot put anything
in, because the compiler does not know the real argument. `List<? super Integer>` is a *consumer*: you
can put `Integer`s in and reading gives you an `Object`, because the compiler does not know how
specific the real argument is.

That is **PECS** — *Producer Extends, Consumer Super* — and `copy` is the pattern in one line:
`List<? extends T>` is read from, `List<? super T>` is written to, and the method works for a
`List<Integer>` source and a `List<Number>` sink. Try to write that signature with a plain `T` and you
will find you cannot: `List<T>` is invariant, and the call would be rejected.

## The three things generics cannot do

Erasure is not a footnote. It is the reason for a set of errors you will meet in your first week.

### You cannot create a generic array

```java bad
public class GenericArray<T> {

    private final T[] items = new T[10];
}
```

```text
error: generic array creation
```

`new T[10]` is rejected with `generic array creation`. An array knows its component type at run time —
`String[]` and `Object[]` are genuinely different classes, and storing a `Double` into a `String[]`
throws `ArrayStoreException`. `T` is erased, so there is no component type to build the array from.
Arrays are reified and generics are not, and the language refuses to pretend otherwise.

The workaround is to keep an `Object[]` internally and cast on the way out, which is what
`ArrayList` does, or to take a `Class<T>` argument and use `Array.newInstance`.

### You cannot widen the argument

```java bad
import java.util.ArrayList;
import java.util.List;

public class Invariance {

    public static void main(String[] args) {
        List<Number> numbers = new ArrayList<Integer>();
        numbers.add(1.5);
        System.out.println(numbers);
    }
}
```

```text
error: incompatible types: ArrayList<Integer> cannot be converted to List<Number>
```

`incompatible types: ArrayList<Integer> cannot be converted to List<Number>` — the invariance rule,
stated as a compile error. This is the error to remember, because it is the one that makes people
conclude generics are broken. They are not; they are refusing to let you create a list that claims to
hold `Number`s and actually holds `Integer`s, because the very next line would add a `Double`.

The fix is `List<? extends Number>` on the *variable*, if you only need to read.

### You cannot ask what a container holds

```java bad
import java.util.List;

public class InstanceOfGeneric {

    static boolean isStringList(Object value) {
        return value instanceof List<String>;
    }

    public static void main(String[] args) {
        System.out.println(isStringList(List.of("a")));
    }
}
```

```text
error: Object cannot be safely cast to List<String>
```

`value instanceof List<String>` is rejected: `Object cannot be safely cast to List<String>`. At run time
there is no such thing as a `List<String>` to test against, so the test would be a lie — it would have
to mean "is a `List`", which is not what you wrote.

Test the erased type (`value instanceof List`) and, if you truly need the element type, test the first
element or carry a `Class<T>` token alongside the list.

:::danger
**`instanceof` with a type argument is not a stricter check that the compiler optimises away — it is a
check that cannot exist.** If you find yourself wanting it, the design is usually asking you to pass a
`Class<T>` token, or to make the type an interface with a method on it. Both are better than a cast you
cannot verify.
:::

## Bridge methods: how erasure still dispatches

If the type argument is gone, how does `Collections.sort` — written against raw `Comparable` — call the
`compareTo(Named)` you wrote?

```java run
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class Bridge {

    static class Named implements Comparable<Named> {
        final String name;

        Named(String name) {
            this.name = name;
        }

        @Override
        public int compareTo(Named other) {
            return name.compareTo(other.name);
        }
    }

    static String describe(Class<?>[] types) {
        return Arrays.stream(types).map(Class::getSimpleName)
                .reduce((left, right) -> left + ", " + right).orElse("");
    }

    public static void main(String[] args) {
        Method[] methods = Named.class.getDeclaredMethods();

        Arrays.stream(methods)
                .map(m -> "  " + m.getName() + "(" + describe(m.getParameterTypes())
                        + ") -> " + m.getReturnType().getSimpleName())
                .sorted()
                .forEach(System.out::println);

        System.out.println("declared methods: " + methods.length);
        System.out.println("of which bridges: "
                + Arrays.stream(methods).filter(Method::isBridge).count());

        List<Named> people = new ArrayList<>(List.of(new Named("grace"), new Named("ada")));
        Collections.sort(people);
        System.out.println("sorted through the erased path: "
                + people.stream().map(p -> p.name).toList());
    }
}
```

```text
  compareTo(Named) -> int
  compareTo(Object) -> int
declared methods: 2
of which bridges: 1
sorted through the erased path: [ada, grace]
```

Two `compareTo` methods exist, and you wrote one. The one you wrote takes a `Named`; the one the
compiler added takes an `Object` and is marked **synthetic** and **bridge**. Its body is a cast and a
call: cast the argument to `Named` and delegate to your method.

It has to exist because of the erased world. `Collections.sort` was compiled against
`Comparable.compareTo(Object)` and knows nothing about your class. The bridge is the adapter that keeps
the old signature working while the typed method stays callable and checked. It appears for overrides
that narrow a parameter type and for covariant return types, and you never write one — but if you ever
read a stack trace naming a method you cannot find in the source, a bridge is why.

## Varargs and the generic array

A varargs parameter is an array, and an array of `T` is exactly what erasure forbids. So a generic
varargs method is *always* creating an array whose component type the compiler cannot verify.

```java run
import java.util.ArrayList;
import java.util.List;

public class Varargs {

    @SafeVarargs
    static <T> List<T> listOf(T... items) {
        List<T> result = new ArrayList<>();
        for (T item : items) {
            result.add(item);
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println("listOf(\"a\", \"b\"): " + listOf("a", "b"));
        System.out.println("listOf(1, 2, 3).size(): " + listOf(1, 2, 3).size());
        System.out.println("listOf() with no arguments: " + listOf());
        System.out.println("the array behind the varargs is: "
                + listOf("a", "b").toArray().getClass().getSimpleName());
    }
}
```

```text
listOf("a", "b"): [a, b]
listOf(1, 2, 3).size(): 3
listOf() with no arguments: []
the array behind the varargs is: Object[]
```

The method works and `listOf()` with no arguments is fine — a zero-length array of the erased type. The
last line shows the array's real class: `Object[]`, not `String[]`, because `T` erased to `Object`.

`@SafeVarargs` is the promise that the method does not do anything unsafe with the array: it does not
store into it, and it does not let the array escape to a caller who might. In exchange the compiler
stops warning. **The annotation is a claim you make, and the compiler cannot check it** — which is why
it is only allowed on `static`, `final` or `private` methods, the ones that cannot be overridden with a
different erasure.

:::pitfall
**`@SafeVarargs` on a method that stores into the array is a lie that corrupts the heap.** A method that
writes to `items[0]` can put a value of the wrong type into the caller's array — the caller built it
with the *concrete* type, and the method only knows the erased one. Annotate only after reading the body
and confirming the array never escapes and is never written to.
:::

:::scenario The registry that stores everything and checks nothing

The `Registry` takes an `Object` and returns an `Object`, so the type of a value is known only to the
caller who stored it — and it has to be re-supplied, by hand, at every read.

:::solution
Every read needs a cast the compiler cannot check, and the cast fails at run time on a value that was
stored perfectly legally. The mistake is at the `put` and the exception is at the `get`, so the two are
in different places — and the type information is not in the code at all.

```java run
import java.util.HashMap;
import java.util.Map;

public class Scenario {

    static final class Registry {
        private final Map<String, Object> values = new HashMap<>();

        void put(String key, Object value) {
            values.put(key, value);
        }

        Object get(String key) {
            return values.get(key);
        }

        int size() {
            return values.size();
        }
    }

    public static void main(String[] args) {
        Registry registry = new Registry();
        registry.put("timeout", 30);
        registry.put("host", "example.com");

        System.out.println("host: " + (String) registry.get("host"));
        System.out.println("host length: " + ((String) registry.get("host")).length());

        try {
            int timeout = (Integer) registry.get("host");
            System.out.println("never reached: " + timeout);
        } catch (ClassCastException e) {
            System.out.println("the cast fails where it is read, not where it was written");
        }

        System.out.println("keys stored: " + registry.size());
    }
}
```

```text
host: example.com
host length: 11
the cast fails where it is read, not where it was written
keys stored: 2
```

The `Registry` works, and it is exactly what Java looked like before 2004 — and it is what a great deal
of code still looks like when somebody wants "a map of anything".

The first two lines look fine, because the caller remembered the types. The third is where it goes
wrong: `(Integer) registry.get("host")` is a cast the compiler cannot check, and it fails at run time
on a value that was stored perfectly legally. **The mistake is at the `put`, and the exception is at the
`get`** — and if the two are in different files, written months apart, the trail is cold.

The deeper problem is that the type information is not in the code at all. It is in the head of whoever
called `put`, and it has to be re-supplied at every `get`. `Sol1` moves that information into the key,
where the compiler can see it.
:::

## Solutions

### 1. Put the type in the key

```java run
import java.util.HashMap;
import java.util.Map;

public class Sol1 {

    static final class Key<T> {
        private final String name;

        Key(String name) {
            this.name = name;
        }

        @Override
        public String toString() {
            return name;
        }
    }

    static final class Registry {
        private final Map<Key<?>, Object> values = new HashMap<>();

        <T> void put(Key<T> key, T value) {
            values.put(key, value);
        }

        @SuppressWarnings("unchecked")
        <T> T get(Key<T> key) {
            return (T) values.get(key);
        }
    }

    static final Key<Integer> TIMEOUT = new Key<>("timeout");
    static final Key<String> HOST = new Key<>("host");

    public static void main(String[] args) {
        Registry registry = new Registry();
        registry.put(TIMEOUT, 30);
        registry.put(HOST, "example.com");

        System.out.println("host: " + registry.get(HOST));
        System.out.println("timeout plus one: " + (registry.get(TIMEOUT) + 1));
        System.out.println("no cast at the call site: " + registry.get(HOST).length());
        System.out.println("the key carries the type, not the caller: " + HOST);
    }
}
```

```text
host: example.com
timeout plus one: 31
no cast at the call site: 11
the key carries the type, not the caller: host
```

`Key<T>` is a key that carries its value's type, and the method signatures do the rest:
`<T> void put(Key<T> key, T value)` and `<T> T get(Key<T> key)`. A `Key<String>` can only be used with a
`String`, and the compiler enforces it at both ends — `registry.put(HOST, 42)` does not compile.

The whole point is where the unchecked cast ended up. It is on **one line inside `get`**, guarded by
`@SuppressWarnings("unchecked")`, and it is correct for a reason you can state: the only way to put a
value in is through `put`, which requires the key's type to match. The suppression is safe because the
API makes it unreachable to do otherwise — which is the standard you should hold every suppression to.

### 2. A pair that knows its halves

```java run
import java.util.function.Function;

public class Sol2 {

    record Pair<A, B>(A first, B second) {

        <C> Pair<B, C> then(Function<A, C> step) {
            return new Pair<>(second, step.apply(first));
        }

        static <A, B> Pair<B, A> swap(Pair<A, B> pair) {
            return new Pair<>(pair.second(), pair.first());
        }
    }

    public static void main(String[] args) {
        Pair<String, Integer> counted = new Pair<>("ada", 3);

        System.out.println("printed: " + counted);
        System.out.println("swapped: " + Pair.swap(counted));
        System.out.println("then(String::length): " + counted.then(String::length));
        System.out.println("first with no cast: " + counted.first().toUpperCase());
        System.out.println("second with no cast: " + (counted.second() + 1));
    }
}
```

```text
printed: Pair[first=ada, second=3]
swapped: Pair[first=3, second=ada]
then(String::length): Pair[first=3, second=3]
first with no cast: ADA
second with no cast: 4
```

`Pair<A, B>` is a record with two type parameters, and every use is checked. `counted.first()` is a
`String` so `.toUpperCase()` compiles, `counted.second()` is an `Integer` so `+ 1` compiles, and
`Pair.swap` exchanges them with the types following along.

`then` is the interesting one, because it introduces a *third* type parameter on the method:
`<C> Pair<B, C> then(Function<A, C> step)`. The result's first component is the old `B`, and its second
is whatever `step` produces. `counted.then(String::length)` therefore gives `Pair[first=3, second=3]` —
the original `second` is `3`, and `"ada".length()` is also `3`. Two `3`s that mean completely different
things is a good reminder that a `Pair` is not self-describing; when the components are not obvious from
the call site, a record with named components is the better shape.

### 3. Bounds and wildcards in one place

```java run
import java.util.ArrayList;
import java.util.List;

public class Sol3 {

    static <T extends Comparable<T>> T min(List<T> values) {
        T best = values.get(0);
        for (T value : values) {
            if (value.compareTo(best) < 0) {
                best = value;
            }
        }
        return best;
    }

    static <T extends Comparable<T>> T max(List<T> values) {
        T best = values.get(0);
        for (T value : values) {
            if (value.compareTo(best) > 0) {
                best = value;
            }
        }
        return best;
    }

    static double total(List<? extends Number> values) {
        double sum = 0;
        for (Number value : values) {
            sum += value.doubleValue();
        }
        return sum;
    }

    static <T> void copy(List<? extends T> from, List<? super T> to) {
        for (T item : from) {
            to.add(item);
        }
    }

    public static void main(String[] args) {
        List<Integer> numbers = List.of(5, 3, 9, 1);

        System.out.println("min: " + min(numbers) + ", max: " + max(numbers));
        System.out.println("total of ints: " + total(numbers));
        System.out.println("total of doubles: " + total(List.of(1.5, 2.5)));

        List<Number> sink = new ArrayList<>();
        copy(numbers, sink);
        System.out.println("copied into a List<Number>: " + sink);
    }
}
```

```text
min: 1, max: 9
total of ints: 18.0
total of doubles: 4.0
copied into a List<Number>: [5, 3, 9, 1]
```

`min` and `max` show the bound doing its job: `<T extends Comparable<T>>` is what makes `compareTo`
callable, and `List<Integer>` satisfies it because `Integer implements Comparable<Integer>`.

`total` shows the *wildcard* instead — `List<? extends Number>` — and the difference matters. A bound
(`<T extends Number>`) would work here too, but it forces the caller to name a type variable and it
pins the whole method to one `T`. The wildcard says "any list whose elements are `Number`s" and is
happy with a `List<Integer>` and a `List<Double>` at the same call site, which the bound cannot be.

`copy` is PECS written out: `List<? extends T>` is read, `List<? super T>` is written. That signature
accepts `copy(numbers, sink)` with a `List<Integer>` source and a `List<Number>` sink, which the
invariance rule would otherwise reject in both directions.

### 4. A bound on the container, not the method

```java run
import java.util.ArrayList;
import java.util.List;

public class Sol4 {

    interface Entity {
        long id();
    }

    record User(long id, String name) implements Entity {
    }

    record Order(long id, int units) implements Entity {
    }

    static final class Repo<T extends Entity> {
        private final List<T> rows = new ArrayList<>();

        void add(T row) {
            rows.add(row);
        }

        T byId(long id) {
            for (T row : rows) {
                if (row.id() == id) {
                    return row;
                }
            }
            return null;
        }

        long highestId() {
            long best = 0;
            for (T row : rows) {
                best = Math.max(best, row.id());
            }
            return best;
        }
    }

    public static void main(String[] args) {
        Repo<User> users = new Repo<>();
        users.add(new User(1, "ada"));
        users.add(new User(7, "grace"));
        System.out.println("user 7: " + users.byId(7));
        System.out.println("highest user id: " + users.highestId());

        Repo<Order> orders = new Repo<>();
        orders.add(new Order(10, 3));
        System.out.println("order 10: " + orders.byId(10));
        System.out.println("the bound lets id() be called on any T: " + users.byId(1).name());
    }
}
```

```text
user 7: User[id=7, name=grace]
highest user id: 7
order 10: Order[id=10, units=3]
the bound lets id() be called on any T: ada
```

`Repo<T extends Entity>` is a bound on the *class*, and it buys something a method bound cannot: every
method in the body can call `row.id()`, because every `T` this repo will ever hold is an `Entity`. That
is what makes `highestId` writable at all — comparing `long` ids requires knowing they exist.

The `Repo<User>` and `Repo<Order>` are separate types as far as the compiler is concerned, and
`users.byId(7)` returns a `User` with no cast. The erasure is still there — `Repo` is one class at run
time, and `byId` returns `Entity` — but every call site is checked, which is the trade generics makes
everywhere.

:::tip
Prefer a bound on the class when *most* methods need it, and a bound on the method when only one does.
A class-wide bound is a real constraint on users of the type; a method bound is local and easier to
relax later.
:::

## Key takeaways

- A type parameter is a compile-time promise in both directions: every use of `T` is the same type, and
  the compiler checks every use and inserts the casts for you.
- Erasure means the type argument is gone at run time. `List<String>` and `List<Integer>` are the same
  class, `T get()` compiles to `Object get()`, and no object can be asked what it holds.
- A raw type switches the checking off. `[rawtypes]` names the cause and `[unchecked]` names the
  consequence, and under `-Werror` both stop the build — which is the right outcome.
- An unchecked cast is a promise you make. It moves the failure from the cast to the first *use*, so the
  stack trace points at an innocent line. Confine every `@SuppressWarnings("unchecked")` to one line and
  state the reason next to it.
- A bound (`<T extends Comparable<T>>`) tells the compiler what `T` can do and rejects call sites that
  do not qualify. A bound may be a class plus any number of interfaces, joined with `&`.
- Generics are invariant: `List<Integer>` is not a `List<Number>`. Wildcards are how you say what you
  meant — **PECS**: `? extends` to read, `? super` to write.
- Erasure forbids `new T[]`, forbids widening a type argument, and forbids `instanceof List<String>`.
  Each has a workaround that costs one `Class<T>` token or one `Object[]`.
- Bridge methods are synthetic adapters the compiler writes so that erased code still dispatches to your
  typed override. If a stack trace names a method you cannot find, that is why.

## Practice

- [ ] Write `Pair<A, B>` twice — once as a class with `equals`/`hashCode`, once as a record — and find
      one thing the record does that the class cannot.
- [ ] Take `Registry` from the scenario and add a `remove` method that keeps the type safety. Which
      signature makes that possible?
- [ ] Write `swap` for a `List<T>` that reverses it in place, then a `copy` that is safe for a
      `List<Integer>` source and a `List<Number>` sink. Say which needs a wildcard and why.
- [ ] Write a method that takes a `List<? extends Number>` and returns the largest element. Explain why
      the return type has to be `Number` rather than `T`.
- [ ] Deliberately write a raw `List`, compile with `-Xlint:all`, and read both warnings. Then fix it
      without `@SuppressWarnings`.
- [ ] Write a class with a covariant return type (`Object get()` in the parent, `String get()` in the
      child) and use reflection to show the bridge method that appears.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. A record is `final` and generates `equals`, `hashCode` and a readable `toString` from its components;
   the hand-written class can be subclassed and can choose which fields participate. A `Pair` almost
   always wants the record.
2. `boolean remove(Key<T> key)` — the key carries `T`, so the signature stays checked even though the
   stored value is only an `Object`.
3. Reversal needs no wildcard (`List<T>` is read and written at the same type). The copy needs
   `List<? extends T>` and `List<? super T>`, because the source and the sink are different types and
   invariance rejects both plain forms.
4. The return type must be `Number`, because the method cannot name the list's element type. `T` is not
   in scope unless you write the method with a bound, which then pins the call site to one type.
5. Adding the type argument fixes both warnings at once; the raw type was the cause and the unchecked
   call was the symptom.
6. `Child.class.getDeclaredMethods()` reports two `get` methods, one of which has
   `isBridge() == true` and returns `Object`. It casts and delegates to the `String` version.
