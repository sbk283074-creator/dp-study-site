#!/usr/bin/env python3
"""Generate chapters/13-exceptions-and-try-with-resources.md.

    python3 tools/gen/13/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "13-exceptions-and-try-with-resources.md")

BLOCKS = {
    "hierarchy": gen.run("Hierarchy.java"),
    "trycatch": gen.run("TryCatch.java"),
    "finallywins": gen.run("FinallyWins.java"),
    "finallywarn": gen.warn("FinallyWarn.java", "[finally]"),
    "unhandled": gen.bad("UnhandledChecked.java", "unreported exception"),
    "swallow": gen.run("Swallow.java"),
    "chaining": gen.run("Chaining.java"),
    "custom": gen.run("Custom.java"),
    "missingserial": gen.warn("MissingSerial.java", "[serial]"),
    "resources": gen.run("Resources.java"),
    "suppressed": gen.run("Suppressed.java"),
    "multicatch": gen.run("MultiCatch.java"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 13
part: 2
title: Exceptions and try-with-resources
summary: Distinguish failures from values, keep the original cause when you wrap, and let the compiler and the language close your resources.
minutes: 60
tags: [exceptions, checked, unchecked, finally, try-with-resources, suppressed, chaining]
---

An exception is a value that says *this call did not produce a result*. That is the whole idea, and the
reason the language gives it a separate channel: a return value has to be a legal value of the return
type, so a method returning `int` has no way to say "I could not". Every alternative to exceptions —
`-1`, `null`, an empty string — is a legal answer that has been overloaded to mean "failed", and every
caller has to remember which.

This chapter is about using that channel properly. Three things go wrong with exceptions and only one of
them is about catching: the failure is collapsed into a value so the caller cannot tell it apart from a
real answer, the original cause is thrown away so the trail is cold, and a resource is leaked because
the `finally` was written by hand. Java has an answer to each, and the compiler enforces a surprising
amount of it.

## The hierarchy, and which branch you can ignore

Everything throwable is a `Throwable`, and it splits in two: `Error` and `Exception`.

@@hierarchy@@

`Error` is for conditions the program cannot recover from — `OutOfMemoryError`,
`StackOverflowError` — and you do not catch it. `Exception` is for everything else.

Under `Exception` there is a third split, and it is the one that matters day to day. A
`RuntimeException` is **unchecked**: nothing forces a caller to handle it. Anything else under
`Exception` is **checked**: the compiler requires the caller to either catch it or declare that it
throws it. `NumberFormatException` is a `RuntimeException` and `IOException` is not, which is why one
can escape `main` and the other cannot.

:::note
The usual guidance is that a checked exception is for a failure the caller can *do something* about —
a missing file, a full disk, a bad port number — and an unchecked one is for a programming mistake the
caller cannot fix at run time, like passing `null` or indexing out of range. The guidance is contested
and plenty of good code disagrees, but the reasoning is worth having: the compiler's insistence is only
useful if the caller has a real choice to make.
:::

## The order of execution

`finally` runs on the way out of the block, whatever happened on the way.

@@trycatch@@

`try catch finally after` — and the interesting part is what is *not* in that order. `finally` runs
after the `catch` block finishes, before the code following the whole statement. It runs whether the
exception was thrown, whether it was caught, and whether it propagated.

That last case is why `finally` exists: it is the only block guaranteed to run when the method is
leaving because of an exception it did not handle.

## The trap in `finally`, and the compiler telling you

`finally` runs so reliably that it can override the control flow of the block it is guarding.

@@finallywins@@

`returnFromFinally` returns **2**, not 1. The `return 1` in the `try` computes its value, then `finally`
runs, and its `return 2` replaces the pending result entirely. The exception that was in flight, if
there had been one, would have been discarded the same way.

`reassignInFinally` returns **1**, and the contrast is the point. Reassigning the local does *not*
change the answer, because the return value was copied out of `result` before `finally` ran. One of
these looks like it should work and does not; the other looks like it should not and does.

The `@SuppressWarnings("finally")` on that method is deliberate — the demo needs the illegal-looking
code to compile. Remove it and the compiler objects:

@@finallywarn@@

`[finally] finally clause cannot complete normally` — javac has a lint category for exactly this
mistake, and under this book's flags `-Werror` makes it fatal. That is a strong hint about how the
language feels about `return` in a `finally` block.

:::danger
**Never `return`, `break`, `continue` or `throw` from a `finally` block.** It silently discards whatever
the `try` or `catch` was doing — including an exception that was propagating, which then vanishes with
no trace. `finally` is for releasing resources, and after this chapter you will not need it for that
either.
:::

## Checked exceptions cannot be ignored

@@unhandled@@

`unreported exception IOException; must be caught or declared to be thrown`. The method `read()` declares
`throws IOException`, so `main` — which does not — cannot call it without handling the failure. This is
the compiler refusing to let a caller pretend the failure does not exist, and it is the entire
difference between a checked and an unchecked exception.

You have two honest options and one dishonest one. Declare `throws IOException` and pass the decision
up; catch it and do something meaningful; or catch it and do nothing, which the compiler allows and
which is the subject of the next section.

## The failure that is turned into a value

The most damaging exception bug is not an unhandled one. It is a handled one that erases the failure.

@@swallow@@

`parse("0")` and `parse("forty")` both return `0`. To the caller they are indistinguishable, and there
is no way to recover the distinction — the `NumberFormatException` was caught and thrown away, and with
it the only evidence that anything went wrong.

This is the defect that makes a `-1` or a `0` or a `null` sentinel so dangerous: the sentinel has to be
a legal value of the return type, so it is always *also* a real answer. A caller that forgets to check
gets a plausible number, and the program continues.

:::pitfall
**A sentinel return value is an exception that has been downgraded to a comment.** The information is
gone, nothing forces the caller to look, and the failure surfaces later as a wrong number rather than an
error. If a method can fail, either let the exception out or return a type that cannot represent "failed"
without saying so.
:::

## Chaining: keeping the original cause

When you do catch a low-level exception and wrap it in something meaningful, keep the original.

@@chaining@@

The message is now `bad port: http` — what the caller of `parsePort` needs. But `getCause()` still
returns the `NumberFormatException`, with its own message (`For input string: "http"`) and its own stack
trace, which is why two frames naming `parseInt` are still there to be found.

That is the difference between a useful wrap and a lost trail. `new IllegalArgumentException("bad port: "
+ text)` — without the second argument — throws away everything about *why*, and the next person to
debug it starts from scratch. **The two-argument constructor is the one you want**, and it costs one
character.

## Your own exception types

A custom exception earns its place when it carries data the caller can act on.

@@custom@@

`InsufficientFundsException` is checked, and it carries `shortfall` as a field with an accessor. A
caller can catch it and make a decision — offer a smaller amount, suggest a transfer — which is exactly
the "the caller can do something about it" test from the start of the chapter.

The `shortfall` in the message is for a human reading a log; the `shortfall()` accessor is for code. Keep
both, and do not make code parse the message.

Adding a custom exception brings one compiler requirement with it, because `Exception` implements
`Serializable`:

@@missingserial@@

`[serial] serializable class ConfigException has no definition of serialVersionUID`. Any class that
extends `Exception` or `RuntimeException` is serializable and needs a `serialVersionUID`, which is why
`Custom` above declares `private static final long serialVersionUID = 1L;`. It is a one-line tax on
every exception type you write, and forgetting it turns a clean build into a `-Werror` failure the
moment somebody adds `-Xlint:all`.

## Resources close themselves

Before `try`-with-resources, every method that opened something had to close it in a `finally`, and
every one of those `finally` blocks was a chance to get it wrong.

@@resources@@

Two resources, declared in one `try` header, and the output shows the whole lifecycle: `open a`,
`open b`, the body, then `close b`, `close a`. **The close order is the reverse of the declaration
order**, which is what you want — the second resource may depend on the first, so it has to go first.

The `close` calls happen before the line after the block, and they happen even if the body throws. That
is the guarantee you were trying to write by hand, now provided by the language.

### When both the body and the close fail

The interesting case is a `close()` that throws while an exception from the body is already on its way
out.

@@suppressed@@

The exception from the body is the one that propagates — `body failed` — because it is the one that
explains what the program was doing. The failure from `close()` is not discarded, though: it is
*attached* to the first one as a **suppressed** exception, and `getSuppressed()` returns it.

This is the case hand-written `finally` blocks get wrong most often. A `close()` that throws inside a
`finally` replaces the original exception, and the real cause disappears from the trace. The
try-with-resources form keeps both, and prints them together when you call `printStackTrace`.

## Multi-catch, when the handling is the same

Two different failures often need the same response, and since Java 7 one block can name both.

@@multicatch@@

`catch (NumberFormatException | ArithmeticException e)` handles both, and the compiler enforces the
important part: **the parameter is implicitly `final`**, because its static type is the common
supertype and you cannot know which one you got. That is a feature, not a restriction — a multi-catch
block that tried to reassign `e` would be relying on information it does not have.

Use it only when the handling really is identical. Two exceptions in one block is a statement that the
caller's response to each is the same, and that statement is worth being sure about.

:::scenario The batch job that counted its own failures

A nightly job parses a column of numbers, doubles each one and adds them up. One row is malformed.

:::solution
The handler returns `-1` to signal a failure, and the caller adds that `-1` into the total along with
every real result. The job even counts the failures correctly — and still reports a total that is wrong
by exactly one sentinel.

@@scenario@@

Four rows, one of them bad. The sentinel detected the failure (`1`) and the total is `23` where the
truth is `24`. **The failure was added to the sum**, because `-1` is a perfectly good `int` and the
accumulator has no way to know it is not data.

Notice how much of this code is correct. The `catch` is present. The failure is detected and counted.
There is no unhandled exception, no crash, and no log line anybody would notice. The bug is a *type*
decision: `-1` was chosen to mean "failed", and `int` cannot say "not a number". The last line makes it
precise — the error is exactly one sentinel, so the fix is not to adjust the arithmetic but to stop
mixing failures into the data.

## Solutions

### 1. Make the failure a value that cannot be mistaken for data

@@sol1@@

`Result` is a record with a `value` and an `error`, and `isOk()` is the only way to get at the value
sensibly. A failure now has a *different shape* from a success, so the accumulator can filter instead
of guessing: `filter(Result::isOk).mapToInt(Result::value).sum()` gives `24`, the correct total.

The `catch` still happens and still turns the failure into a value — that is unavoidable, because the
method has to return something. What changed is that the value is *tagged*. The caller who forgets to
look at `isOk()` gets a `0` that is never summed, because the stream never selects it.

The errors are also collected rather than counted: `failed: 1 -> [oops is not a number]` names the row,
which a bare counter cannot.

### 2. Let the language close things

@@sol2@@

`Counter implements AutoCloseable`, so `try (Counter a = ...; Counter b = ...)` is all it takes. The
output shows both counters closed with their final use counts — `closed b after 1 use(s)` then `closed a
after 2 use(s)` — before the line after the block runs.

`AutoCloseable.close()` declares `throws Exception`, so an implementation may throw anything. If your
`close` cannot fail, `Closeable` is the narrower interface, and it is what `InputStream` and friends
implement.

### 3. An exception that carries the fix

@@sol3@@

`ConfigException` holds the `key` as a field and builds a message from it, and it takes an optional
`cause`. Three inputs produce three useful outcomes: a good port returns `8080`, a non-number wraps the
`NumberFormatException` (`cause: NumberFormatException`), and an out-of-range port throws with
`cause: none`, because there is no lower-level exception to blame.

That last distinction is worth noting. A cause is not required; passing `null` is honest when the
failure was detected here rather than inherited. What is not honest is passing a cause that is
irrelevant just to have one.

### 4. Add context, keep the cause

@@sol4@@

`lookup` catches the `NullPointerException` from `table.get(key).intValue()` and rethrows a
`ServiceException` that names the key. The cause is preserved (`java.lang.NullPointerException`), so
the original trace is still in the chain.

The wrapper is a `RuntimeException`, which is a deliberate choice: adding a checked exception to a
method signature is a breaking change for every caller, and a lookup failure in a service layer is
usually a programming or configuration error rather than something the caller can retry. Wrapping
unchecked exceptions in unchecked exceptions keeps every existing signature valid.

:::tip
Wrap an exception when you can add information the original does not have — which key, which file,
which request. If you cannot name anything new, do not wrap; let the original travel. A layer of
`catch (Exception e) { throw new RuntimeException(e); }` with no added context makes every stack trace
one frame longer and no more useful.
:::

## Key takeaways

- An exception is a value on a separate channel, and its advantage over a sentinel is that it cannot be
  confused with a legal result. A `-1` sentinel is always also a real `-1`.
- `Error` is for unrecoverable conditions and is not caught. Under `Exception`, a `RuntimeException` is
  unchecked and everything else is checked; the compiler requires a caller to catch or declare the
  checked ones.
- `finally` runs on every way out of the block, after the `catch` and before the code that follows. A
  `return` in `finally` overrides the pending result, and javac has `[finally]` to say so.
- Never `return` or `throw` from `finally`: it discards the in-flight exception silently.
- When you wrap an exception, pass the original as the cause. The two-argument constructor is what keeps
  the trail intact.
- A custom exception is worth writing when it carries data the caller can act on. It extends a
  serializable type, so `-Xlint:all` requires a `serialVersionUID`.
- `try`-with-resources closes in reverse declaration order, closes even when the body throws, and
  attaches a failing `close` to the in-flight exception as a **suppressed** exception rather than
  replacing it.
- Multi-catch (`catch (A | B e)`) requires that the handling be identical and makes `e` implicitly
  `final`, because its static type is the common supertype.

## Practice

- [ ] Write a method returning `int` that can fail, three ways: a `-1` sentinel, a checked exception, and
      a `Result` record. Say for each what the caller has to remember.
- [ ] Predict the output of a `try` with `return 1`, a `catch` with `return 2`, and a `finally` with
      `return 3`, then run it and explain the answer.
- [ ] Wrap `Integer.parseInt` in a method that throws a custom exception naming the offending text, and
      make sure the `NumberFormatException` is still reachable from the new exception.
- [ ] Write a resource whose `close()` throws, and a body that also throws. Show that both exceptions
      survive and say which one `getMessage()` returns.
- [ ] Take the `Swallow` program and make the failure impossible to ignore without changing the return
      type to a record or an `Optional`.
- [ ] Compile a class extending `Exception` with `-Xlint:all -Werror` and read the warning. Then fix it
      and confirm the build is clean.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The sentinel requires the caller to remember the convention and to check it; the checked exception
   requires the caller to write a `catch` or a `throws`; the `Result` requires the caller to look at the
   tag before the value. Only the last two are enforced by something other than memory.
2. `3`. The `finally` runs last and its `return` replaces whatever the `try` or `catch` had pending.
3. `throw new ConfigException("port", text, e)` — the third argument is the cause, and
   `e.getCause()` returns the `NumberFormatException` with its original message and trace.
4. Both survive: the body's exception propagates and `getMessage()` returns the body's message; the
   `close` failure is in `getSuppressed()`. A hand-written `finally` would have replaced the first with
   the second.
5. Return an `OptionalInt`, or a `Result` record. Either makes "failed" a shape the caller has to
   acknowledge, rather than a number that looks like data.
6. `[serial] serializable class X has no definition of serialVersionUID`. Add
   `private static final long serialVersionUID = 1L;` and the warning goes.
"""

gen.write(TEMPLATE, BLOCKS)
