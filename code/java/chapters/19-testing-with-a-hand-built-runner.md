---
chapter: 19
part: 2
title: Testing with a Hand-Built Test Runner
summary: Build the smallest test framework that works — annotations, reflection, a runner and assertions — and use it to find a bug that a passing run would have hidden.
minutes: 60
tags: [testing, annotations, reflection, assertions, test doubles, regression]
---

A test is a claim about your code that a machine checks for you. Everything else — the framework, the
reporters, the IDE integration — is packaging around that idea. This chapter builds the packaging from
nothing, on purpose. A real project uses JUnit, and you should too; but JUnit is not magic, it is
annotations plus reflection plus a runner, and building a forty-line version teaches you what the real
one is doing when a test passes for a reason you did not expect. It also happens to be the only
testing library this track can use, because the book takes no third-party jars.

## What a test framework actually is

```java run
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;

public class MiniTest {
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface Test {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface BeforeEach {}

    public static class AssertionFailure extends RuntimeException {
        private static final long serialVersionUID = 1L;

        AssertionFailure(String message) {
            super(message);
        }
    }

    public record Result(String name, boolean passed, String detail) {}

    static void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionFailure("expected <" + expected + "> but was <" + actual + ">");
        }
    }

    public static List<Result> run(Class<?> suite) throws ReflectiveOperationException {
        List<Method> tests = new ArrayList<>();
        List<Method> befores = new ArrayList<>();
        for (Method m : suite.getDeclaredMethods()) {
            if (m.isAnnotationPresent(Test.class)) {
                tests.add(m);
            } else if (m.isAnnotationPresent(BeforeEach.class)) {
                befores.add(m);
            }
        }
        tests.sort(Comparator.comparing(Method::getName));
        befores.sort(Comparator.comparing(Method::getName));

        List<Result> results = new ArrayList<>();
        for (Method test : tests) {
            Object instance = suite.getDeclaredConstructor().newInstance();
            try {
                for (Method before : befores) {
                    before.invoke(instance);
                }
                test.invoke(instance);
                results.add(new Result(test.getName(), true, ""));
            } catch (InvocationTargetException e) {
                Throwable cause = e.getCause();
                results.add(new Result(test.getName(), false,
                        cause.getClass().getSimpleName() + ": " + cause.getMessage()));
            }
        }
        return results;
    }

    public static void report(Class<?> suite, List<Result> results) {
        int passed = 0;
        for (Result r : results) {
            if (r.passed()) {
                passed++;
                System.out.printf("PASS  %s%n", r.name());
            } else {
                System.out.printf("FAIL  %s  <- %s%n", r.name(), r.detail());
            }
        }
        System.out.printf("%s: %d of %d passed%n", suite.getSimpleName(), passed, results.size());
    }

    static class Suite {
        private int calls;

        @BeforeEach
        void freshState() {
            calls = 0;
        }

        @Test
        void adds() {
            calls++;
            assertEquals(4, 2 + 2);
            assertEquals(1, calls);
        }

        @Test
        void counts() {
            calls += 2;
            assertEquals(2, calls);
        }

        @Test
        void fails() {
            assertEquals(5, 2 + 2);
        }
    }

    public static void main(String[] args) throws ReflectiveOperationException {
        report(Suite.class, run(Suite.class));
    }
}
```

```text
PASS  adds
PASS  counts
FAIL  fails  <- AssertionFailure: expected <5> but was <4>
Suite: 2 of 3 passed
```

That is the whole framework. Read it in four parts.

`@Test` and `@BeforeEach` are **annotations**, declared with `@Retention(RUNTIME)` so they survive into
the class file where reflection can see them, and `@Target(METHOD)` so the compiler stops you putting
one in the wrong place. An annotation with `SOURCE` retention would be gone by the time the runner
looked, which is the single most common reason a hand-written framework finds no tests at all.

`run` does the work: it asks the class for its declared methods, collects the ones carrying each
annotation, and sorts them. Then, for every test, it **constructs a fresh instance** of the suite,
invokes every `@BeforeEach`, and invokes the test.

`report` turns the results into lines a human reads, and the last line is the one that matters — a
count, not a verdict.

The output is the point of the whole chapter:

```
PASS  adds
PASS  counts
FAIL  fails  <- AssertionFailure: expected <5> but was <4>
Suite: 2 of 3 passed
```

`fails` is a test that is *supposed* to fail, and it does — with a message naming the expected value,
the actual value, and the test. That is a usable failure. A bare `false` or a stack trace into the
framework would tell you far less.

## Discovery is reflection

The runner never mentions `adds` or `counts` by name. It finds them.

```java run
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class Ordering {
    static class Suite {
        void testCharlie() {}

        void testAlpha() {}

        void testBravo() {}
    }

    static List<String> declaredOrder() {
        List<String> names = new ArrayList<>();
        for (Method m : Suite.class.getDeclaredMethods()) {
            names.add(m.getName());
        }
        return names;
    }

    static List<String> sortedOrder() {
        List<String> names = declaredOrder();
        names.sort(Comparator.naturalOrder());
        return names;
    }

    public static void main(String[] args) {
        System.out.println("sorted  = " + sortedOrder());
        System.out.println("again   = " + sortedOrder());
        System.out.println("stable  = " + sortedOrder().equals(sortedOrder()));
        System.out.println("count   = " + sortedOrder().size());
    }
}
```

```text
sorted  = [testAlpha, testBravo, testCharlie]
again   = [testAlpha, testBravo, testCharlie]
stable  = true
count   = 3
```

`getDeclaredMethods()` returns the methods of a class with no **order guarantee whatsoever** — not
declaration order, not alphabetical, nothing the specification promises. It happens to come back in a
consistent order on this JVM today, and that is not something to build on: a test suite whose
execution order is unspecified is a suite whose failures move around between machines.

So the runner sorts, and `stable = true` is the assertion that matters. The three tests run in
`testAlpha`, `testBravo`, `testCharlie` order every time, on every JVM. The `count = 3` is there
because a runner that silently discovers nothing also reports zero failures, and a green suite that
ran nothing is worse than a red one.

:::pitfall
**A test runner that finds no tests reports success.** If you rename `@Test` or forget
`@Retention(RUNTIME)`, `run` collects an empty list and prints `0 of 0 passed`. Guard against it: assert
that the number of tests discovered equals the number you expect, and treat zero as a failure. The
same trap exists in real frameworks, where a missing annotation or a class the runner cannot see
produces a cheerful empty report.
:::

## A test must not depend on the order

The fresh instance per test is not a formality. It is what stops one test from changing the world the
next one runs in.

```java run
public class Isolation {
    static int sharedCalls;

    static class Shared {
        boolean check() {
            sharedCalls++;
            return sharedCalls == 1;
        }
    }

    static class Fresh {
        private int calls;

        boolean check() {
            calls++;
            return calls == 1;
        }
    }

    public static void main(String[] args) {
        Shared shared = new Shared();
        System.out.println("shared first  = " + shared.check());
        System.out.println("shared second = " + shared.check());

        System.out.println("fresh first   = " + new Fresh().check());
        System.out.println("fresh second  = " + new Fresh().check());
        System.out.println("total shared  = " + sharedCalls);
    }
}
```

```text
shared first  = true
shared second = false
fresh first   = true
fresh second  = true
total shared  = 2
```

`Shared` keeps its counter in a `static` field, so the value survives from one call to the next. The
first call sees `1` and passes; the second sees `2` and **fails** — and it would have passed if it had
run alone. A test whose result depends on what ran before it is worse than no test, because it will
pass on your machine and fail in CI, or the reverse.

`Fresh` puts the counter in an instance field, and a new instance per call means each call starts from
zero. Both calls pass, in either order, forever.

This is the reason the runner does `suite.getDeclaredConstructor().newInstance()` inside the loop
rather than once outside it. It costs an allocation per test and it buys order-independence, which is
the property that makes a suite trustworthy. **If a test needs shared setup that cannot be an
instance field, it is a signal that the code under test is holding state it should not.**

## An assertion is a throw

`assertEquals` compares two values and, when they differ, throws. Everything else follows from that.

```java throw
public class ThrowAssertion {
    static class AssertionFailure extends RuntimeException {
        private static final long serialVersionUID = 1L;

        AssertionFailure(String message) {
            super(message);
        }
    }

    static void assertEquals(int expected, int actual) {
        if (expected != actual) {
            throw new AssertionFailure("expected <" + expected + "> but was <" + actual + ">");
        }
    }

    public static void main(String[] args) {
        assertEquals(4, 2 + 2);
        System.out.println("first assertion held");
        assertEquals(5, 2 + 2);
        System.out.println("this line is never reached");
    }
}
```

```text
Exception in thread "main" ThrowAssertion$AssertionFailure: expected <5> but was <4>
```

The first assertion held, so `first assertion held` was printed. The second threw, so the line after
it never ran — `this line is never reached` is absent from the output, and that absence is the
evidence.

The exception carries the message, the runner catches it at the boundary, and the suite keeps going
with the next test. That is the entire control flow of a test framework: **an assertion failure is an
exception, and a runner is a loop with a `catch` in it.** Note that the JVM prints the exception with
its full class name, `ThrowAssertion$AssertionFailure`, which is why the runner uses
`cause.getClass().getSimpleName()` for the report — `AssertionFailure` is what a reader wants.

## Testing that something fails

Some of the most valuable tests assert that bad input is *rejected*. That needs an assertion whose
success condition is an exception.

```java run
public class ExpectsThrow {
    static int divide(int a, int b) {
        return a / b;
    }

    static String assertThrows(Class<? extends Throwable> expected, Runnable body) {
        try {
            body.run();
        } catch (Throwable actual) {
            if (expected.isInstance(actual)) {
                return "threw " + actual.getClass().getSimpleName() + ": " + actual.getMessage();
            }
            return "wrong type: " + actual.getClass().getSimpleName();
        }
        return "nothing thrown";
    }

    public static void main(String[] args) {
        int numerator = 1;
        int denominator = 0;

        System.out.println("divide   = " + assertThrows(ArithmeticException.class,
                () -> divide(numerator, denominator)));
        System.out.println("parse    = " + assertThrows(NumberFormatException.class,
                () -> Integer.parseInt("nope")));
        System.out.println("mismatch = " + assertThrows(IllegalStateException.class,
                () -> divide(numerator, denominator)));
        System.out.println("silent   = " + assertThrows(ArithmeticException.class,
                () -> divide(numerator, numerator)));
    }
}
```

```text
divide   = threw ArithmeticException: / by zero
parse    = threw NumberFormatException: For input string: "nope"
mismatch = wrong type: ArithmeticException
silent   = nothing thrown
```

`assertThrows` takes the expected exception type and a `Runnable`, runs the body, and returns a string
describing what happened. It deliberately **does not** return a boolean, so a failure cannot be
silently discarded — the report line carries the reason.

Four outcomes, and the last two are the ones people forget to write. `divide` and `parse` are the
expected failures, each named with its real message. `mismatch` shows the wrong exception type being
caught — a test that only checked "something threw" would pass here, and the code would be wrong.
`silent` is the case where nothing threw at all, which is the failure a naive `try`/`catch` hides
completely.

:::warning
**A test that catches `Exception` and does nothing always passes.** If the body of a `try` block
throws, an empty `catch` swallows it and the test is green. Every `assertThrows` must name the
exception it expects and must fail when a *different* one arrives — which is exactly what the
`mismatch` line above is checking.
:::

## A seam you can substitute

Code that reads the clock, the network or the filesystem is hard to test because its output depends on
something you do not control. The fix is not a mocking library; it is a small interface.

```java run
import java.util.ArrayList;
import java.util.List;

public class TestDouble {
    interface Clock {
        int hour();
    }

    static class RealClock implements Clock {
        @Override
        public int hour() {
            return 9;
        }
    }

    static class FakeClock implements Clock {
        private final int hour;

        FakeClock(int hour) {
            this.hour = hour;
        }

        @Override
        public int hour() {
            return hour;
        }
    }

    static String greeting(Clock clock) {
        int hour = clock.hour();
        if (hour < 12) {
            return "Good morning";
        }
        return hour < 18 ? "Good afternoon" : "Good evening";
    }

    public static void main(String[] args) {
        List<String> seen = new ArrayList<>();
        for (int hour : new int[] {6, 13, 21}) {
            seen.add(greeting(new FakeClock(hour)));
        }
        System.out.println("fake = " + seen);
        System.out.println("real = " + greeting(new RealClock()));
    }
}
```

```text
fake = [Good morning, Good afternoon, Good evening]
real = Good morning
```

`greeting` takes a `Clock` and calls `hour()`. It has no idea whether that is a real clock or a fake,
and it does not need to. `FakeClock` returns whatever it was constructed with, so the three branches
of the rule can be exercised at `6`, `13` and `21` — including the two boundaries that a test driven by
the real clock would only hit twice a day, if you happened to run it at the right moment.

`RealClock` is the production implementation, and `greeting(new RealClock())` is the real path. The
fake is not a lie about the system; it is the same rule with one input made controllable.

The name for this is **dependency injection**, and it is the reason to write `greeting(Clock)` rather
than calling `LocalTime.now()` inside. Chapter 18 said never to call `now()` inside a rule; this is
what you do instead. A **test double** is the stand-in, and the smallest useful double is a class with
one field and one method.

## An annotation declares where it may go

```java bad
import java.lang.annotation.ElementType;
import java.lang.annotation.Target;

public class BadTarget {
    @Target(ElementType.METHOD)
    @interface OnlyOnMethods {}

    @OnlyOnMethods
    record Point(int x, int y) {}

    public static void main(String[] args) {
        System.out.println(new Point(1, 2));
    }
}
```

```text
error: annotation interface not applicable to this kind of declaration
```

`@OnlyOnMethods` was declared `@Target(ElementType.METHOD)` and applied to a record, so javac refused
the file. The wording is worth noting — the compiler says **annotation interface**, which is what an
annotation actually is.

This is why `@Test` on a class is a compile error rather than a silently undiscovered test, and it is
the cheapest possible version of the empty-suite trap. `@Target` turns a runtime mystery into a build
failure, and it costs one line.

:::scenario The cent that only appeared on one input

A payments service converts an amount to cents with `Math.round(amount * 100)`. It has been in
production for two years. A test is written that compares it against exact decimal arithmetic across a
handful of representative amounts.

:::solution
The test is table-driven: a list of input strings, both conversions computed, and a count of how many
disagree. `centsFromDouble` is the code under test; `centsExact` is the oracle, and it uses
`BigDecimal` — the type from Chapter 18 — so it has no representation error of its own.

The point is not that the production code is wrong on most inputs. It is right on three of the four
here. The point is *which* input it is wrong on, and that you cannot tell by looking.

```java run
import java.math.BigDecimal;
import java.math.RoundingMode;

public class Scenario {
    static long centsFromDouble(String amount) {
        return Math.round(Double.parseDouble(amount) * 100);
    }

    static long centsExact(String amount) {
        return new BigDecimal(amount)
                .movePointRight(2)
                .setScale(0, RoundingMode.HALF_UP)
                .longValueExact();
    }

    public static void main(String[] args) {
        String[] amounts = {"19.99", "0.35", "1.005", "2.675"};
        int differences = 0;
        for (String amount : amounts) {
            long viaDouble = centsFromDouble(amount);
            long exact = centsExact(amount);
            boolean same = viaDouble == exact;
            if (!same) {
                differences++;
            }
            String note = same ? "" : "  <- differs";
            System.out.printf("%-6s double=%4d exact=%4d%s%n", amount, viaDouble, exact, note);
        }
        System.out.println("differed on " + differences + " of " + amounts.length);
    }
}
```

```text
19.99  double=1999 exact=1999
0.35   double=  35 exact=  35
1.005  double= 100 exact= 101  <- differs
2.675  double= 268 exact= 268
differed on 1 of 4
```

`differed on 1 of 4`. `1.005` gives `100` through the `double` path and `101` through the exact one,
because `1.005` is not representable in binary and lands just below the half-cent boundary. The other
three amounts agree.

That is the shape of a bug that survives two years in production: it is correct on nearly everything,
the failures depend on the exact input, and no amount of reading the code reveals which inputs those
are. `19.99` and `0.35` and `2.675` all agree; `1.005` does not. **A test that enumerates the
boundaries is how you find it, and a test that checks one comfortable example is how you miss it.**

The oracle matters as much as the test. If `centsExact` had also used a `double`, both sides would
agree and the test would pass while the bug remained.
:::

## Solutions

### 1. Table-driven tests

```java run
public class Sol1 {
    static String slug(String title) {
        return title.toLowerCase()
                .replaceAll("[^a-z0-9]+", "-")
                .replaceAll("(^-|-$)", "");
    }

    public static void main(String[] args) {
        String[][] cases = {
            {"Hello World", "hello-world"},
            {"  Spaced  Out  ", "spaced-out"},
            {"Already-slugged", "already-slugged"},
            {"Punctuation! Here?", "punctuation-here"},
            {"", ""},
        };

        int passed = 0;
        for (String[] c : cases) {
            String actual = slug(c[0]);
            boolean ok = actual.equals(c[1]);
            if (ok) {
                passed++;
            }
            System.out.printf("%-4s %s%n", ok ? "PASS" : "FAIL",
                    "'" + c[0] + "' -> '" + actual + "'");
        }
        System.out.println("passed " + passed + " of " + cases.length);
    }
}
```

```text
PASS 'Hello World' -> 'hello-world'
PASS '  Spaced  Out  ' -> 'spaced-out'
PASS 'Already-slugged' -> 'already-slugged'
PASS 'Punctuation! Here?' -> 'punctuation-here'
PASS '' -> ''
passed 5 of 5
```

One function, one table of input/expected pairs, one loop. `passed 5 of 5` is the result, and adding a
sixth case is one line.

Note the cases: an empty string, a string of only spaces, and a string that is already slugged. Those
are the inputs a single happy-path example never covers, and the empty string in particular is where
`replaceAll` chains usually produce something surprising. The table is also documentation — a reader
learns the rule from the cases faster than from the regex.

### 2. Assert the failure, and assert which failure

```java run
public class Sol2 {
    static int parsePort(String raw) {
        int port = Integer.parseInt(raw);
        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("port out of range: " + port);
        }
        return port;
    }

    static String expectFailure(String raw) {
        try {
            parsePort(raw);
            return "no exception";
        } catch (RuntimeException e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
    }

    public static void main(String[] args) {
        System.out.println("ok        = " + parsePort("8080"));
        for (String raw : new String[] {"0", "70000", "http", "-1"}) {
            System.out.printf("%-8s-> %s%n", raw, expectFailure(raw));
        }
    }
}
```

```text
ok        = 8080
0       -> IllegalArgumentException: port out of range: 0
70000   -> IllegalArgumentException: port out of range: 70000
http    -> NumberFormatException: For input string: "http"
-1      -> IllegalArgumentException: port out of range: -1
```

`parsePort` has two distinct failure modes and the table shows both.
`NumberFormatException: For input string: "http"` comes from `Integer.parseInt`, and
`IllegalArgumentException: port out of range: 0` comes from the range check.

A test that only asserted "an exception is thrown" would pass for both and would not notice if the
range check were deleted — `parsePort("0")` would then return `0` and the test would still see an
exception from a different input. **Name the exception type and the message.** The message is the part
that tells the next person what the code believed.

### 3. Test the boundaries, not the middle

```java run
public class Sol3 {
    static int clamp(int value, int low, int high) {
        return Math.max(low, Math.min(high, value));
    }

    public static void main(String[] args) {
        int[][] cases = {
            {5, 1, 10, 5},
            {0, 1, 10, 1},
            {11, 1, 10, 10},
            {1, 1, 10, 1},
            {10, 1, 10, 10},
        };

        int failed = 0;
        for (int[] c : cases) {
            int actual = clamp(c[0], c[1], c[2]);
            boolean ok = actual == c[3];
            if (!ok) {
                failed++;
            }
            System.out.printf("%-4s clamp(%2d, %2d, %2d) = %2d%n",
                    ok ? "PASS" : "FAIL", c[0], c[1], c[2], actual);
        }
        System.out.println("failed " + failed + " of " + cases.length);
    }
}
```

```text
PASS clamp( 5,  1, 10) =  5
PASS clamp( 0,  1, 10) =  1
PASS clamp(11,  1, 10) = 10
PASS clamp( 1,  1, 10) =  1
PASS clamp(10,  1, 10) = 10
failed 0 of 5
```

`clamp` is `Math.max(low, Math.min(high, value))`, and the five cases are the whole truth about it:
one interior value and the two ends of the range, twice each. `failed 0 of 5`.

The interior case, `5`, would pass under almost any implementation. The cases that matter are `0` and
`11` — outside the range — and `1` and `10`, which are *on* the boundary. An off-by-one in a clamp
always shows up at the boundary and never in the middle, so a suite of interior values is a suite that
cannot fail. **For any function with a range, the interesting inputs are the two ends and the two
just-outsides.**

### 4. A regression test names the bug it prevents

```java run
public class Sol4 {
    static int lastIndex(String haystack, String needle) {
        return haystack.lastIndexOf(needle);
    }

    static boolean has(String haystack, String needle) {
        return lastIndex(haystack, needle) >= 0;
    }

    public static void main(String[] args) {
        System.out.println("found     = " + lastIndex("banana", "an"));
        System.out.println("missing   = " + lastIndex("banana", "zz"));
        System.out.println("empty     = " + lastIndex("banana", ""));
        System.out.println("whole     = " + lastIndex("banana", "banana"));
        System.out.println("has an    = " + has("banana", "an"));
        System.out.println("has zz    = " + has("banana", "zz"));
    }
}
```

```text
found     = 3
missing   = -1
empty     = 6
whole     = 0
has an    = true
has zz    = false
```

`lastIndexOf` returns `-1` for "not found" and `6` for an empty needle — the length of the haystack.
Both are real, both are documented, and both are surprising, which is why they are worth a test.

`has` wraps the index in `>= 0`, and the last two lines are the regression: `has zz = false` where a
naive implementation using `!= 0` would say `true`, and `has an = true` where one treating `-1` as an
index would throw.

The rule: **a regression test should fail on the old code and pass on the new one.** `missing = -1`
and `empty = 6` are the values that make it a regression test rather than a demonstration — they
record the two edges the bug lived on.

## Key takeaways

- A test framework is annotations plus reflection plus a loop with a `catch`. JUnit is the same idea
  with more packaging, and a real project should use it.
- An annotation must be `@Retention(RUNTIME)` to be visible to reflection. `SOURCE` retention is the
  usual reason a hand-written runner discovers nothing.
- `getDeclaredMethods()` promises no order. Sort the tests, or the suite's behaviour varies between
  JVMs.
- A runner that discovers zero tests reports zero failures. Assert the discovered count.
- Construct a fresh instance of the suite per test. Shared `static` state makes a test's result depend
  on what ran before it.
- An assertion failure is an exception; that is the whole control flow. Give it a message that names
  the expected and actual values.
- `assertThrows` must check the exception *type* and fail when nothing is thrown. A `catch` that
  swallows everything makes a test that can never fail.
- Replace a clock, a socket or a filesystem with a small interface you can substitute. That is
  dependency injection, and the test double is the class that implements it.
- `@Target` turns a misapplied annotation into a compile error. `@Target(ElementType.METHOD)` on
  `@Test` is why `@Test` on a class does not silently do nothing.
- Test the boundaries and the failure modes. A suite of comfortable examples cannot fail, and a bug
  that depends on the input is exactly what such a suite misses.

## Practice

- [ ] Add an `@AfterEach` annotation to the runner in this chapter, and a test that proves it runs
      after a test that throws.
- [ ] Write a test that asserts `Math.round` and exact decimal conversion agree for ten amounts you
      choose, then find the one where they do not.
- [ ] Take a method that calls `LocalDate.now()` and change it to take the date as a parameter. Write
      the test that was impossible before the change.
- [ ] Write a test that is order-dependent — two tests sharing a `static` field — and watch it pass
      alone and fail in the suite. Then fix it.
- [ ] Build a `FakeClock` for a method that decides whether a shop is open, and test every boundary
      hour including midnight.
- [ ] Write a regression test for a bug you have actually fixed. It must fail on the old code.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Collect methods annotated `@AfterEach` alongside `@BeforeEach` and invoke them in a `finally`
   block, so they run whether the test passed, failed or threw. The test that proves it uses a static
   list and asserts the order `before, test, after`.
2. `Math.round(Double.parseDouble(s) * 100)` against
   `new BigDecimal(s).movePointRight(2).setScale(0, RoundingMode.HALF_UP)`. Amounts ending in `5` at
   the third decimal are where they diverge, and the divergence depends on the binary representation
   rather than on anything visible in the decimal.
3. `daysUntil(LocalDate, LocalDate)` and a test that passes `LocalDate.of(2026, 3, 14)`. Before the
   change the method's answer depended on the day the test ran, so no assertion could be written.
4. Both tests pass in isolation and the second fails in the suite, because the first incremented the
   shared field. The fix is an instance field and a fresh instance per test.
5. A `Clock` interface with `int hour()`, a `FakeClock(int)`, and a table of hours covering `0`, the
   opening hour, the closing hour, and the hours either side of each. The boundaries are where the
   comparison operators are wrong.
6. Revert to the old code, run the test, and watch it fail — then restore the fix and watch it pass.
   A regression test that passes on both versions is not a regression test.
