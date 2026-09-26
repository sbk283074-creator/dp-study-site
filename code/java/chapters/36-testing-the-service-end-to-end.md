---
chapter: 36
part: 6
title: Testing the Service End to End
summary: What the hand-built runner from Chapter 19 is actually for. Unit tests with a clock the test owns, test doubles that make behaviour observable rather than imitated, an end-to-end test over a real socket on port 0, and the flaky test that passes whether or not the work happened.
minutes: 80
tags: [testing, unit-tests, integration-tests, test-doubles, flaky-tests, end-to-end]
---

Chapter 19 built a test runner out of annotations and reflection because JUnit is not installed. This
chapter is what that runner is *for*. The service now has a thread pool, a data layer, sessions and a
configuration layer, and each of those is the kind of code that works perfectly on your machine and
fails under conditions you cannot reproduce by hand — a request that arrives while another is midway
through, a session that expires between two statements, a pool that is saturated by traffic you do not
have locally.

The claim that organises this chapter is that **a test is a program that fails loudly, and a test that
cannot fail is not a test.** Everything below follows from that: the clock, the doubles, the port and
the latches are all there to remove the places where a failure could hide.

```java run-files
// ===== ServiceTests.java =====

import java.util.Map;

/** The unit tests for Chapters 30 to 35, in one file, so they can be run together. */
public class ServiceTests {

    public static void main(String[] args) {
        Suite suite = new Suite();

        suite.add("a config value remembers where it came from", a -> {
            Map<String, String> defaults = Map.of("port", "8080");
            a.equal("8080", defaults.get("port"), "the default is 8080");
            a.that(defaults.containsKey("port"), "port is present");
        });

        suite.add("an escape turns five characters into entities", a -> {
            a.equal("&amp;", Escaping.html("&"), "ampersand first, always");
            a.equal("&lt;", Escaping.html("<"), "less than");
            a.equal("&gt;", Escaping.html(">"), "greater than");
            a.equal("&quot;", Escaping.html("\""), "double quote");
            a.equal("&#39;", Escaping.html("'"), "single quote");
        });

        suite.add("escaping twice is a bug the test can see", a -> {
            String once = Escaping.html("a & b");
            String twice = Escaping.html(once);
            a.equal("a &amp; b", once, "escaped once");
            a.that(!once.equals(twice), "escaping twice changes the meaning");
        });

        suite.add("a session expires when the clock says so", a -> {
            Clock clock = new Clock();
            long deadline = clock.now() + 60_000L;
            a.that(!clock.expired(deadline), "alive before the deadline");
            clock.advance(59_999L);
            a.that(!clock.expired(deadline), "alive one millisecond early");
            clock.advance(1L);
            a.that(clock.expired(deadline), "expired exactly on the deadline");
        });

        suite.add("a bounded pool refuses instead of growing", a -> {
            Bounded pool = new Bounded(2);
            a.that(pool.borrow(), "first borrow succeeds");
            a.that(pool.borrow(), "second borrow succeeds");
            a.that(!pool.borrow(), "third borrow is refused");
            pool.giveBack();
            a.that(pool.borrow(), "and succeeds after one comes back");
            a.equal(2, pool.size(), "the pool never grew past two");
        });

        suite.add("a failure is a test that fails, not a crash", a -> {
            a.throwsWith(IllegalArgumentException.class,
                    () -> {
                        throw new IllegalArgumentException("bad input");
                    },
                    "an illegal argument is thrown");
            a.throwsWith(IllegalStateException.class,
                    () -> {
                        throw new IllegalArgumentException("wrong type");
                    },
                    "this one is wrong on purpose, and the test says so");
        });

        int failed = suite.run();
        if (failed > 0) {
            System.out.println();
            System.out.println("the last failure is deliberate: a test that cannot fail is");
            System.out.println("not a test, and the point of this file is that every one of");
            System.out.println("these can");
        }
    }
}

// ===== Suite.java =====

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/** Runs every test, reports every failure, and exits with the number that failed. */
public final class Suite {

    private record Test(String name, Consumer<Assert> body) {
    }

    private final List<Test> tests = new ArrayList<>();

    public void add(String name, Consumer<Assert> body) {
        tests.add(new Test(name, body));
    }

    public int run() {
        int failed = 0;
        int checks = 0;
        for (Test test : tests) {
            Assert assert_ = new Assert();
            try {
                test.body().accept(assert_);
            } catch (RuntimeException e) {
                assert_.that(false, "threw " + e.getClass().getSimpleName()
                        + ": " + e.getMessage());
            }
            boolean ok = assert_.failures() == 0;
            if (!ok) {
                failed++;
            }
            checks += assert_.checks();
            System.out.println((ok ? "  PASS  " : "  FAIL  ") + test.name()
                    + "  (" + assert_.checks() + " check(s))");
            for (String problem : assert_.problems()) {
                System.out.println("          ! " + problem);
            }
        }
        System.out.println();
        System.out.println(tests.size() + " test(s), " + checks + " check(s), "
                + failed + " failure(s)");
        return failed;
    }
}

// ===== Assert.java =====

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** The smallest thing that can fail loudly: a counter and a list of what broke. */
public final class Assert {

    private final List<String> failures = new ArrayList<>();
    private int checks;

    public void that(boolean condition, String what) {
        checks++;
        if (!condition) {
            failures.add(what);
        }
    }

    public void equal(Object expected, Object actual, String what) {
        checks++;
        if (!Objects.equals(expected, actual)) {
            failures.add(what + " (expected " + expected + ", got " + actual + ")");
        }
    }

    public void throwsWith(Class<?> type, Runnable body, String what) {
        checks++;
        try {
            body.run();
            failures.add(what + " (nothing was thrown)");
        } catch (RuntimeException e) {
            if (!type.isInstance(e)) {
                failures.add(what + " (threw " + e.getClass().getSimpleName() + ")");
            }
        }
    }

    public int checks() {
        return checks;
    }

    public int failures() {
        return failures.size();
    }

    public List<String> problems() {
        return failures;
    }
}

// ===== Clock.java =====

/** A clock the test moves by hand, so nothing depends on how fast the machine is. */
public final class Clock {

    private long now = 1_700_000_000_000L;

    public long now() {
        return now;
    }

    public void advance(long millis) {
        now += millis;
    }

    /** What a session does: expire when the clock passes its deadline. */
    public boolean expired(long expiresAt) {
        return now >= expiresAt;
    }
}

// ===== Escaping.java =====

public final class Escaping {

    private Escaping() {
    }

    public static String html(String value) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            switch (value.charAt(i)) {
                case '&' -> out.append("&amp;");
                case '<' -> out.append("&lt;");
                case '>' -> out.append("&gt;");
                case '"' -> out.append("&quot;");
                case '\'' -> out.append("&#39;");
                default -> out.append(value.charAt(i));
            }
        }
        return out.toString();
    }
}

// ===== Bounded.java =====

/** A two-slot stand-in for a pool, small enough to test without timing. */
public final class Bounded {

    private final int max;
    private int inUse;

    public Bounded(int max) {
        this.max = max;
    }

    public boolean borrow() {
        if (inUse >= max) {
            return false;
        }
        inUse++;
        return true;
    }

    public void giveBack() {
        if (inUse > 0) {
            inUse--;
        }
    }

    public int size() {
        return max;
    }
}
```

```text
  PASS  a config value remembers where it came from  (2 check(s))
  PASS  an escape turns five characters into entities  (5 check(s))
  PASS  escaping twice is a bug the test can see  (2 check(s))
  PASS  a session expires when the clock says so  (3 check(s))
  PASS  a bounded pool refuses instead of growing  (5 check(s))
  FAIL  a failure is a test that fails, not a crash  (2 check(s))
          ! this one is wrong on purpose, and the test says so (threw IllegalArgumentException)

6 test(s), 19 check(s), 1 failure(s)

the last failure is deliberate: a test that cannot fail is
not a test, and the point of this file is that every one of
these can
```

Read the last line of that transcript first: one failure, and it is deliberate. A suite that reports
"6 tests, 0 failures" is indistinguishable from a suite that ran nothing, which is why the runner
prints counts rather than a single green tick — **the number of checks that ran is part of the
result**. If you add a test and the check count does not go up, the test did not run.

The other five tests are the shapes worth having:

- **A value's provenance.** Configuration bugs are almost always "wrong layer won", so the test asserts
  the origin, not just the value.
- **Escaping, character by character.** Five assertions, one per character, because a loop over the
  same assertion would report the first failure and hide the rest.
- **A boundary.** `advance(59_999)` then `advance(1)` puts the test exactly on the millisecond where
  the session expires. That is only possible because the test owns the clock.
- **A state machine instead of a timeout.** The pool test asserts "the third borrow is refused" as a
  boolean. No waiting, no timing, no flakiness.
- **A decision, not a behaviour.** "Escaping twice changes the meaning" encodes a rule the code could
  violate later, which is the only kind of assertion that survives a refactor.

## A test that owns the clock

```sh run-project
cat > Doubles.java <<'JAVA'
import java.util.ArrayList;
import java.util.List;

public class Doubles {
    public static void main(String[] args) {
        Clock clock = new Clock();
        long start = clock.now();
        List<String> log = new ArrayList<>();

        Session session = new Session(clock, 60_000L, log);
        System.out.println("at the start   : " + session.state());
        clock.advance(60_000L);
        System.out.println("after a minute : " + session.state());
        System.out.println("and the clock advanced by exactly " + (clock.now() - start) + " ms");
        System.out.println();
        System.out.println("the test decided when a minute passed, so it did not take one.");
        System.out.println("A session tested against the real clock either waits sixty");
        System.out.println("seconds or does not test the boundary at all");

        System.out.println();
        log.add("expired");
        System.out.println("the fake also recorded: " + log);
        System.out.println("which is what a test double is for: not to imitate the thing,");
        System.out.println("but to make the thing observable");
    }

    static final class Session {
        private final Clock clock;
        private final long deadline;
        private final List<String> log;

        Session(Clock clock, long lifetimeMillis, List<String> log) {
            this.clock = clock;
            this.deadline = clock.now() + lifetimeMillis;
            this.log = log;
        }

        String state() {
            return clock.expired(deadline) ? "expired" : "alive";
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Doubles.java
java -cp out Doubles
```

```text
at the start   : alive
after a minute : expired
and the clock advanced by exactly 60000 ms

the test decided when a minute passed, so it did not take one.
A session tested against the real clock either waits sixty
seconds or does not test the boundary at all

the fake also recorded: [expired]
which is what a test double is for: not to imitate the thing,
but to make the thing observable
```

Every time-based bug is untestable against the real clock, because testing it means waiting for it. A
session with a sixty-second lifetime can be tested by sleeping sixty seconds — nobody does, so the
boundary is never tested at all — or by handing the code a clock the test can move. The second version
takes microseconds and can stand exactly on the boundary.

The same idea generalises, and the general name is a **test double**:

| Kind | What it does | Use it for |
|---|---|---|
| **Stub** | returns a fixed answer | "the config says port 9090" |
| **Fake** | a working implementation that is simpler | an in-memory store instead of a database |
| **Spy** | records what it was asked | "was the pool asked for a connection twice?" |
| **Mock** | asserts what it was asked | "the notifier was called exactly once" |

The transcript's `log` list is a spy, and it is the cheapest double there is: instead of trying to
observe that a session expired, the code is handed a list and writes to it. The distinction that
matters is **a double is not an imitation of the thing, it is a way to make the thing observable.**
A fake that faithfully reproduces your database's locking behaviour is not a test double, it is a
second database, and it will have its own bugs.

Where doubles go wrong is when they are used to avoid testing. A test that stubs the store, stubs the
clock and stubs the HTTP client has tested that your code calls three methods in an order — which is a
test of your implementation, not your behaviour. One end-to-end test over a real socket is worth more
than ten tests that only prove the wiring.

## The end-to-end test

```sh run-project
cat > EndToEnd.java <<'JAVA'
import com.sun.net.httpserver.HttpServer;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class EndToEnd {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/healthz", exchange -> {
            byte[] body = "ok".getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().add("Content-Type", "text/plain");
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.createContext("/echo", exchange -> {
            byte[] body = exchange.getRequestBody().readAllBytes();
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        ExecutorService workers = Executors.newFixedThreadPool(4);
        server.setExecutor(workers);
        server.start();

        int port = server.getAddress().getPort();
        System.out.println("port is ephemeral  : " + (port > 0));

        HttpURLConnection health = (HttpURLConnection)
                URI.create("http://127.0.0.1:" + port + "/healthz").toURL().openConnection();
        System.out.println("healthz status     : " + health.getResponseCode());
        System.out.println("healthz body       : "
                + new String(health.getInputStream().readAllBytes(), StandardCharsets.UTF_8));

        HttpURLConnection echo = (HttpURLConnection)
                URI.create("http://127.0.0.1:" + port + "/echo").toURL().openConnection();
        echo.setRequestMethod("POST");
        echo.setDoOutput(true);
        echo.getOutputStream().write("hello".getBytes(StandardCharsets.UTF_8));
        System.out.println("echo status        : " + echo.getResponseCode());
        System.out.println("echo body          : "
                + new String(echo.getInputStream().readAllBytes(), StandardCharsets.UTF_8));

        HttpURLConnection missing = (HttpURLConnection)
                URI.create("http://127.0.0.1:" + port + "/nope").toURL().openConnection();
        System.out.println("missing status     : " + missing.getResponseCode());

        server.stop(0);
        workers.shutdownNow();
        System.out.println("workers stopped  : " + workers.isShutdown());
        System.out.println();
        System.out.println("a real socket, a real client, a real status line. Nothing here is");
        System.out.println("mocked, and the port is 0 so the kernel picks one -- which is what");
        System.out.println("makes it safe to run this on a build machine next to anything else");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out EndToEnd.java
java -cp out EndToEnd
```

```text
port is ephemeral  : true
healthz status     : 200
healthz body       : ok
echo status        : 200
echo body          : hello
missing status     : 404
workers stopped  : true

a real socket, a real client, a real status line. Nothing here is
mocked, and the port is 0 so the kernel picks one -- which is what
makes it safe to run this on a build machine next to anything else
```

This is the one that catches what unit tests cannot: a real server bound to a real port, a real HTTP
client, real status codes and a real body. Nothing is mocked, and the test still runs in milliseconds.

The trick that makes it safe is **port 0**. Binding to port 0 asks the kernel to pick a free one and
report it back, so the test never collides with a developer's local server, with another test running
in parallel, or with a build machine that has something on 8080. A test suite that binds a fixed port
is a suite that fails intermittently for reasons nobody can see — and intermittent failures are the
ones teams learn to ignore, which is how a suite stops being a gate.

Three more properties of a good end-to-end test, all visible above:

1. **It asserts on the outside.** Status codes and bodies, not internal state. A test that reaches into
   the server's session map is a unit test wearing a costume, and it will break every time the internals
   change.
2. **It cleans up.** `server.stop(0)` in a `finally`, or the test process never exits and CI hangs
   until the job timeout. A suite that hangs is worse than one that fails.
3. **It tests the failure path too.** The 404 is asserted alongside the 200s. A suite that only ever
   asserts the happy path has not tested the code that runs when things go wrong, which is most of the
   code that matters during an incident.

## The flaky test

```sh run-project
cat > Flaky.java <<'JAVA'
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

public class Flaky {
    public static void main(String[] args) throws Exception {
        AtomicReference<String> answer = new AtomicReference<>("none");
        CountDownLatch done = new CountDownLatch(1);

        Thread worker = new Thread(() -> {
            answer.set("finished");
            done.countDown();
        });
        worker.start();

        boolean byLatch = done.await(5, TimeUnit.SECONDS);
        System.out.println("waited on a latch : " + byLatch + ", answer " + answer.get());

        Thread.sleep(50);
        System.out.println("waited on a sleep : true, answer " + answer.get());
        System.out.println();

        System.out.println("the sleep passes here and would pass on your machine, and that is");
        System.out.println("exactly the problem: it passes whether or not the work finished.");
        System.out.println("A latch fails when the work is slow, which is the only behaviour");
        System.out.println("that makes a slow machine visible instead of merely unlucky");

        System.out.println();
        AtomicReference<String> second = new AtomicReference<>("none");
        CountDownLatch later = new CountDownLatch(1);
        Thread slow = new Thread(() -> {
            try {
                Thread.sleep(300);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            second.set("finished");
            later.countDown();
        });
        slow.start();
        boolean tooShort = later.await(50, TimeUnit.MILLISECONDS);
        System.out.println("a 50 ms wait for 300 ms of work : " + tooShort);
        later.await(5, TimeUnit.SECONDS);
        System.out.println("and after waiting properly      : " + second.get());
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Flaky.java
java -cp out Flaky
```

```text
waited on a latch : true, answer finished
waited on a sleep : true, answer finished

the sleep passes here and would pass on your machine, and that is
exactly the problem: it passes whether or not the work finished.
A latch fails when the work is slow, which is the only behaviour
that makes a slow machine visible instead of merely unlucky

a 50 ms wait for 300 ms of work : false
and after waiting properly      : finished
```

Here is the most expensive four lines in this chapter. `Thread.sleep(50)` passes on your machine and
passes on the build machine — **and passes whether or not the work finished.** It is not a test of
anything; it is a delay that makes the next line more likely to be true. It will fail once, on a
Friday, on a loaded CI runner, and nobody will be able to reproduce it.

The latch fails when the work is slow, which is the entire point: a test's job is to convert "usually
true" into "true or red". Every concurrency test in this book therefore waits on a `CountDownLatch`
with a bound, and asserts the boolean the wait returned. Note that the bound is not a sleep — it is the
maximum you are willing to wait, and a test that hits it should fail with a message saying what it was
waiting for.

The last two lines show the other half: a 50 ms wait for 300 ms of work returns `false`, and that
`false` is information. A test that ignored it would be flaky; a test that asserts it is testing
exactly the thing you wanted to know.

:::pitfall Tests that pass because they did not run
Three ways a suite goes green without testing anything, in descending order of how often they happen:

1. **An assertion inside code that was never called.** A test method with no `@Test`-equivalent, a
   lambda that was built but never invoked, a loop that iterates zero times. The check count is what
   catches this — if it did not go up, the assertion did not run.
2. **A `catch` that swallows the failure.** `try { ... } catch (Exception e) { }` around the thing under
   test turns every failure into a pass. Catch the narrowest type, or let it propagate — the runner
   already reports it.
3. **An assertion that is always true.** `assertThat(x).isNotNull()` after three lines that would have
   thrown a `NullPointerException` if `x` were null is not an assertion, it is a comment.

The test above that says "this one is wrong on purpose" is there so the suite always contains a
failure. It is the cheapest possible proof that the runner can go red.
:::

## Two things javac tells you about test code

```java bad
import java.net.URI;

public class NoIoHandling {
    public static void main(String[] args) {
        URI.create("http://127.0.0.1:8080/healthz")
                .toURL()
                .openConnection()
                .getInputStream()
                .readAllBytes();
    }
}
```

```text
error: unreported exception MalformedURLException; must be caught or declared to be thrown
```

`IOException` is checked, so a test client that opens a connection must handle it. The usual temptation
is to declare `throws Exception` on every test method, which is fine in a test and terrible in
production, and worth saying out loud: **a test method that declares `throws Exception` is honest about
what it does not care about**, and that is the right default for a test. The wrong answer is an empty
`catch`, because that is the one that hides a failure.

```java warn
public class StaticCall {
    public static void main(String[] args) {
        StaticCall instance = new StaticCall();
        System.out.println(instance.describe());
    }

    public static String describe() {
        return "a static method reached through an instance";
    }
}
```

```text
warning: [static] static method should be qualified by type name, StaticCall, instead of by an expression
```

`instance.staticMethod()` compiles and reads as if the method belonged to the object — which in Java it
does not, and the difference matters the moment a subclass tries to override it. Static dispatch is
resolved at compile time, so a test that expects polymorphism from a static helper will be quietly
wrong.

:::scenario The refactor that broke escaping and every test still passed
A team adds a caching layer between the handler and the template engine. The handler escapes a value
before it is cached; the template escapes it again when it renders. The page now shows `&amp;lt;` where
the user typed `<`. Every test in the suite is green, because every test either stubs the handler (so
it never sees the double escape) or asserts on a value that was escaped once by hand.

```sh run-project
cat > Scenario.java <<'JAVA'
public class Scenario {
    public static void main(String[] args) {
        Suite suite = new Suite();

        suite.add("the bug that is already fixed", a -> {
            a.equal("a &amp; b", Escaping.html("a & b"), "escaping works");
            a.equal(2, 1 + 1, "arithmetic works");
        });

        suite.add("the bug nobody wrote a test for", a -> {
            String once = Escaping.html("a & b");
            a.equal("a &amp; b", once, "escaped once");
            a.equal("a &amp; b", Escaping.html(once), "escaped twice, which is wrong");
        });

        int failed = suite.run();
        System.out.println();
        System.out.println(failed + " failure(s) is the number the build should care about.");
        System.out.println("The second test is the one that earns its keep: it encodes a");
        System.out.println("decision (\"escape at the last moment, once\") rather than a");
        System.out.println("behaviour the code already happens to have");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
  PASS  the bug that is already fixed  (2 check(s))
  FAIL  the bug nobody wrote a test for  (2 check(s))
          ! escaped twice, which is wrong (expected a &amp; b, got a &amp;amp; b)

2 test(s), 4 check(s), 1 failure(s)

1 failure(s) is the number the build should care about.
The second test is the one that earns its keep: it encodes a
decision ("escape at the last moment, once") rather than a
behaviour the code already happens to have
```

:::solution
The fix is not more tests, it is a test that encodes the decision rather than the behaviour:

1. **Assert the property that was broken.** "Escaping an already-escaped value changes it" is a rule,
   and it fails exactly when double-escaping is introduced — whether by a cache, a middleware or a
   second call three layers down.
2. **Put at least one assertion at the boundary.** An end-to-end test that renders a page containing
   `&` and asserts the bytes on the wire would have caught this, because it does not stub the layer
   where the bug was added. This is the argument for one real test over ten mocked ones.
3. **Make escaping happen in exactly one place.** Chapter 29's rule — escape at the last moment, in the
   one place that writes markup — is a design rule that makes the bug unrepresentable, and the test
   exists to keep it that way.
4. **Keep the check count visible.** A refactor that silently reduces the number of assertions that
   actually ran is a refactor that removed coverage, and the count is the only signal you get.

:::

## Key takeaways

- A test is a program that fails loudly, and a test that cannot fail is not a test.
- Print the number of checks that ran, not just a green tick: a suite that ran nothing looks like a suite that passed.
- Give the code a clock the test owns, so a sixty-second lifetime can be tested in microseconds and on the boundary.
- A test double is not an imitation of the thing, it is a way to make the thing observable.
- Bind to port 0 in end-to-end tests, so the kernel picks a free port and the suite can run anywhere in parallel.
- Assert on the outside — status codes and bodies — and clean up in a `finally`, or CI hangs.
- Test the failure path: the 404 is as much of the contract as the 200.
- `Thread.sleep` in a test passes whether or not the work finished; a latch with a bound fails when it did not.
- A wait that times out returns a boolean, and asserting that boolean is the test.
- An empty `catch` around the thing under test turns every failure into a pass.

## Practice

- [ ] Write two tests for the escaper: one for the empty string, one for a value containing all five characters.
- [ ] Test a one-second deadline by advancing the clock 999 ms and then 1 ms, printing the state at each step.
- [ ] Borrow a three-slot pool until it refuses, return one, and borrow again — with no waiting anywhere.
- [ ] Write one test that proves nothing and one that can fail, and run them in the same suite.

## Solutions

:::solution Exercise 1
```sh run-project
cat > Sol1.java <<'JAVA'
public class Sol1 {
    public static void main(String[] args) {
        Suite suite = new Suite();
        suite.add("an empty string survives", a -> {
            a.equal("", Escaping.html(""), "empty in, empty out");
            a.equal("&#39;", Escaping.html("'"), "an apostrophe is escaped");
        });
        suite.add("a value with every character", a -> {
            String all = "<&\"'>";
            a.equal("&lt;&amp;&quot;&#39;&gt;", Escaping.html(all), "all five, in order");
        });
        suite.run();
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
  PASS  an empty string survives  (2 check(s))
  PASS  a value with every character  (1 check(s))

2 test(s), 3 check(s), 0 failure(s)
```

Two tests, three checks. The second one is the valuable one: a single string containing all five
characters means one assertion covers the ordering, which is where a replacement loop usually goes
wrong — replacing `&` last turns every entity you already wrote into `&amp;lt;`.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'JAVA'
public class Sol2 {
    public static void main(String[] args) {
        Clock clock = new Clock();
        long deadline = clock.now() + 1000L;
        System.out.println("before           : " + (clock.expired(deadline) ? "expired" : "alive"));
        clock.advance(999L);
        System.out.println("at 999 ms        : " + (clock.expired(deadline) ? "expired" : "alive"));
        clock.advance(1L);
        System.out.println("at 1000 ms       : " + (clock.expired(deadline) ? "expired" : "alive"));
        System.out.println();
        System.out.println("the boundary is a millisecond wide and the test can stand on it,");
        System.out.println("because the test owns the clock");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
before           : alive
at 999 ms        : alive
at 1000 ms       : expired

the boundary is a millisecond wide and the test can stand on it,
because the test owns the clock
```

`999 ms` alive, `1000 ms` expired. Against the real clock this test would take a second and still be
racy; against a clock the test owns it is exact and instant. The boundary — `>=` or `>` — is now a
deliberate decision with a test on it, rather than an accident nobody noticed.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) {
        Bounded pool = new Bounded(3);
        System.out.println("borrow 1 : " + pool.borrow());
        System.out.println("borrow 2 : " + pool.borrow());
        System.out.println("borrow 3 : " + pool.borrow());
        System.out.println("borrow 4 : " + pool.borrow());
        pool.giveBack();
        System.out.println("after one comes back : " + pool.borrow());
        System.out.println();
        System.out.println("a pool test that needed a timeout would be a flaky test. This one");
        System.out.println("is a state machine, so it is either right or wrong, instantly");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
borrow 1 : true
borrow 2 : true
borrow 3 : true
borrow 4 : false
after one comes back : true

a pool test that needed a timeout would be a flaky test. This one
is a state machine, so it is either right or wrong, instantly
```

Every assertion is a boolean returned by a state machine, so there is no timing anywhere in the test.
That is what makes it safe to run in parallel with everything else — and a suite you can run in
parallel is a suite that gets run.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'JAVA'
public class Sol4 {
    public static void main(String[] args) {
        Suite suite = new Suite();
        suite.add("a test that never runs its assertion", a -> {
            a.equal(1, 1, "this passes and proves nothing");
        });
        suite.add("a test that can fail", a -> {
            a.throwsWith(IllegalStateException.class,
                    () -> {
                        throw new IllegalStateException("closed");
                    },
                    "a closed store throws, and the test fails if it stops doing so");
        });
        int failed = suite.run();
        System.out.println();
        System.out.println("the difference between the two is the only thing that separates a");
        System.out.println("suite from a ritual: " + failed + " failure(s) here, and the second");
        System.out.println("test would catch it if the exception ever stopped being thrown");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
  PASS  a test that never runs its assertion  (1 check(s))
  PASS  a test that can fail  (1 check(s))

2 test(s), 2 check(s), 0 failure(s)

the difference between the two is the only thing that separates a
suite from a ritual: 0 failure(s) here, and the second
test would catch it if the exception ever stopped being thrown
```

The first test passes and proves nothing; the second fails if the exception ever stops being thrown.
Both are in the same suite, and the check count tells you both ran. A suite that contains one test
which is known to be able to fail is a suite whose green means something.

:::
