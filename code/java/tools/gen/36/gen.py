#!/usr/bin/env python3
"""Generate chapters/36-testing-the-service-end-to-end.md.

    python3 tools/gen/36/gen.py

Chapter 19 built a test runner out of annotations and reflection. This one is what
that runner is *for*: the service now has concurrency, a data layer, sessions and
config, and every one of those is the kind of code that works on your machine and
fails under load. Unit tests with a clock the test owns, test doubles, an
end-to-end test over a real socket on port 0, and the flaky test that passes
whether or not the work happened.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "36-testing-the-service-end-to-end.md")

BLOCKS = {
    "core": gen.run_files(["ServiceTests.java", "Suite.java", "Assert.java", "Clock.java",
                           "Escaping.java", "Bounded.java"]),
    "e2e": gen.sh("e2e.sh", "run-project"),
    "doubles": gen.sh("doubles.sh", "run-project"),
    "flaky": gen.sh("flaky.sh", "run-project"),
    "checked": gen.bad("NoIoHandling.java", "unreported exception"),
    "static": gen.warn("StaticCall.java", "static method should be qualified"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
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

@@core@@

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

@@doubles@@

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

@@e2e@@

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

@@flaky@@

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

@@checked@@

`IOException` is checked, so a test client that opens a connection must handle it. The usual temptation
is to declare `throws Exception` on every test method, which is fine in a test and terrible in
production, and worth saying out loud: **a test method that declares `throws Exception` is honest about
what it does not care about**, and that is the right default for a test. The wrong answer is an empty
`catch`, because that is the one that hides a failure.

@@static@@

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
@@scenario@@
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
@@sol1@@

Two tests, three checks. The second one is the valuable one: a single string containing all five
characters means one assertion covers the ordering, which is where a replacement loop usually goes
wrong — replacing `&` last turns every entity you already wrote into `&amp;lt;`.

:::

:::solution Exercise 2
@@sol2@@

`999 ms` alive, `1000 ms` expired. Against the real clock this test would take a second and still be
racy; against a clock the test owns it is exact and instant. The boundary — `>=` or `>` — is now a
deliberate decision with a test on it, rather than an accident nobody noticed.

:::

:::solution Exercise 3
@@sol3@@

Every assertion is a boolean returned by a state machine, so there is no timing anywhere in the test.
That is what makes it safe to run in parallel with everything else — and a suite you can run in
parallel is a suite that gets run.

:::

:::solution Exercise 4
@@sol4@@

The first test passes and proves nothing; the second fails if the exception ever stops being thrown.
Both are in the same suite, and the check count tells you both ran. A suite that contains one test
which is known to be able to fail is a suite whose green means something.

:::
"""

gen.write(TEMPLATE, BLOCKS)
