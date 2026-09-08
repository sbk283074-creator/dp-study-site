---
chapter: 9
part: 1
title: Errors, Exceptions & Defensive Programming
summary: Handle failures deliberately with try/except/finally, raise exceptions that explain themselves, and stop hiding real bugs behind bare except blocks.
minutes: 40
tags: [exceptions, try/except, raise, logging, EAFP]
---

Code that never fails is code that never runs. Files go missing, users type letters where you
expected digits, networks time out, and APIs change shape overnight. The question is never "will
this break?" but "when it breaks, does it break loudly, explain itself, and leave the system in a
sane state?" This chapter is about making that answer yes — and about the single worst habit in
Python, the bare `except:` that turns a real bug into a mystery.

## Three kinds of wrong

Distinguish them, because each has a different fix:

1. **Syntax errors** — Python cannot parse your code. Nothing runs. `SyntaxError: expected ':'`.
   Your editor catches these before you save.
2. **Exceptions** — the code is valid, but something failed while running: a missing key, a
   missing file, a division by zero. These are *recoverable* and are what this chapter is about.
3. **Logic errors** — the program runs and produces the wrong answer. No traceback, no warning.
   Chapter 11's testing section is the defence here.

Chapter 1 taught you to read a traceback bottom-up. Now you need to predict which one you will get.

## The exception hierarchy

Every exception is an object in a family tree rooted at `BaseException`. You almost always catch
`Exception`, which is the parent of everything a program is expected to survive:

```text
BaseException
 +-- SystemExit, KeyboardInterrupt, GeneratorExit   <- do NOT catch casually
 +-- Exception
      +-- ValueError          right type, bad value: int("abc")
      +-- TypeError           wrong type: "2" + 2
      +-- KeyError            missing dict key
      +-- IndexError          index past the end of a sequence
      +-- AttributeError      object has no such attribute
      +-- FileNotFoundError   (subclass of OSError) path does not exist
      +-- PermissionError     (subclass of OSError) no access
      +-- ZeroDivisionError   1 / 0
      +-- ImportError         module or name could not be imported
```

Notice `FileNotFoundError` and `PermissionError` are both `OSError`s. Catching `OSError` handles
the whole family of filesystem and OS problems, which is often what you want when the only sensible
response is "tell the user and give up".

## `try` / `except` / `else` / `finally`

Four clauses, four distinct jobs:

```python
try:
    value = int(input("Enter a number: "))
except ValueError:
    print("That was not a whole number.")
else:
    print(f"Thanks, {value * 2} is double that.")
finally:
    print("(this always runs)")
```

- `try` — the code that might fail. Keep it **narrow**: one risky operation, not twenty lines.
- `except` — what to do about a specific failure.
- `else` — runs only if `try` succeeded. It keeps "the happy path" out of the `try` block so you
  cannot accidentally catch an exception raised by your own success-handling code.
- `finally` — runs no matter what, even on `return` or an uncaught exception. Use it for cleanup:
  closing files, releasing locks, stopping timers.

`finally` is why `with open(...)` works — Chapter 14 shows you how to write your own context
managers, but `with` already covers the file case, so prefer it over `try`/`finally`.

### Catch what you mean, in order

```python
try:
    result = compute(data)
except ValueError as e:
    print(f"bad value: {e}")
except (TypeError, KeyError) as e:
    print(f"malformed data: {e!r}")
except Exception:
    print("unexpected failure")
    raise
```

Three rules are visible here. Catch the **most specific first** — Python checks `except` blocks top
to bottom and stops at the first match, so a broad `Exception` at the top makes everything below it
dead code. Use `as e` to get the exception object, and put it in your message; `"bad value"` alone
tells you nothing at 3 a.m. And re-`raise` in a catch-all so the program still fails loudly after
you have logged something useful.

:::danger `except:` swallows bugs
A bare `except:` catches `BaseException` — including `KeyboardInterrupt` (Ctrl-C) and
`SystemExit`. `except Exception: pass` is only slightly better: it catches every genuine bug in
your code, discards it, and lets the program continue with corrupt state.

```python
# catastrophic
try:
    process(order)
except Exception:
    pass
```

Every typo, every `None` you forgot to check, every wrong variable name vanishes. If you must
ignore an error, name the exact type and say why:

```python
try:
    os.remove(temp_file)
except FileNotFoundError:
    pass          # already gone; that is the outcome we wanted
```

That is a decision. The other one is a landmine.
:::

## `raise`: making failure explicit

`raise` throws an exception on purpose. Use it when a function cannot do its job and silence would
be worse.

```python
def percentage(part, whole):
    if whole == 0:
        raise ValueError("percentage() needs a non-zero whole")
    return 100 * part / whole
```

Validate at the **boundary** — where data enters your program from `input()`, a file, an HTTP
request, or a user form — and let the interior assume the data is already good. Half the defensive
code in a badly written codebase exists because every function re-checks what the first one already
verified.

### Exception chaining with `raise ... from`

When you catch one exception and raise a different, more meaningful one, chain them:

```python
def load_config(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ValueError(f"{path} is not valid JSON") from err
```

The traceback then shows both:

```text
ValueError: config.json is not valid JSON
  ...
The above exception was the direct cause of the following exception:
  ...
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

Use `raise ... from err` when you are translating an error, and `raise ... from None` when the
original traceback is noise you deliberately want to hide. Without either, Python still chains
implicitly with "During handling of the above exception...", which is noisier and less clear.

## Custom exceptions

Once your program has more than one failure mode, define your own. It costs three lines and lets
callers react to *your* errors without string-matching messages.

```python
class AppError(Exception):
    """Base class for errors raised by this application."""

class ValidationError(AppError):
    pass

class PaymentDeclined(AppError):
    pass
```

Now a caller can write `except AppError:` to catch anything your code raises deliberately, while
`TypeError`s from real bugs still crash normally. Derive from `Exception`, never `BaseException`.
Chapter 12 revisits this once you are writing classes of your own.

## `assert` is for developers, not users

```python
def apply_discount(price, percent):
    assert 0 <= percent <= 100, f"discount out of range: {percent}"
    return price * (1 - percent / 100)
```

`assert` states an **internal invariant**: something you believe is impossible if your own code is
correct. It is documentation that executes. It is *not* input validation, for one hard reason:
running Python with `python3 -O` strips every `assert` out of the program. Your validation would
silently disappear in production. Validate user input with `if` and `raise ValueError`; reserve
`assert` for "this should never happen" — and Chapter 11 will show you how tests lean on it
heavily.

## EAFP versus LBYL

Python culture prefers **EAFP** — *Easier to Ask Forgiveness than Permission*: just try it and
handle the failure.

```python
# EAFP — Pythonic
try:
    user = users[key]
except KeyError:
    user = default_user()

# LBYL — Look Before You Leap
if key in users:
    user = users[key]
else:
    user = default_user()
```

EAFP wins when failures are rare: one lookup instead of two, and no race condition if the dict
changes between the check and the use. That last point is the one that matters — the LBYL version
has a gap where another thread, another request, or another process can change the state. Chapter
21 makes that concrete with concurrency.

LBYL is still correct when failure is *expected and common*, or when the check is cheap and the
failure expensive to unwind. Checking `if path.is_file()` before reading is perfectly fine — it
gives a better error message than a bare `FileNotFoundError`. The rule: use EAFP when the operation
usually succeeds; check first when you need to fail fast with a clear message.

## Retrying transient failures

Network calls and file locks fail temporarily. Retry, but with limits and increasing delay, or you
will hammer a struggling service and get yourself blocked.

```python
import time


def fetch_with_retry(fetch, attempts=3, delay=1.0):
    """Call fetch() up to `attempts` times, waiting longer between tries."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return fetch()
        except (TimeoutError, ConnectionError) as err:
            last_error = err
            print(f"attempt {attempt} failed ({err}); retrying...")
            time.sleep(delay * attempt)
    raise RuntimeError(f"gave up after {attempts} attempts") from last_error
```

Note what this does not do: it does not retry `ValueError` or `KeyError`, because those will fail
the same way forever, and it always ends by raising rather than returning `None`. A function that
returns `None` on failure just moves the crash somewhere harder to debug.

## Logging instead of `print`

`print()` goes to stdout, has no severity, no timestamp, and cannot be turned off. The `logging`
module fixes all of that and is in the standard library.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

log.debug("parsed %d rows", 42)
log.info("server starting on port %d", 8000)
log.warning("config missing 'timeout', using default 30s")
log.error("could not reach payment API")
```

```text
2026-09-07 14:03:11 INFO     __main__: server starting on port 8000
2026-09-07 14:03:11 WARNING  __main__: config missing 'timeout', using default 30s
2026-09-07 14:03:11 ERROR    __main__: could not reach payment API
```

Levels, in order: `DEBUG` (developer detail) < `INFO` (normal progress) < `WARNING` (something odd,
still working) < `ERROR` (an operation failed) < `CRITICAL` (the program is dying). Set `level` to
filter: `level=logging.WARNING` hides debug and info without deleting a single line of code.

Use `%s`-style placeholders rather than f-strings (`log.info("user %s", name)`) so the string is
only formatted if the message is actually emitted. And inside an `except` block, use
`log.exception(...)` — it logs at ERROR level **and** includes the full traceback:

```python
try:
    process(order)
except Exception:
    log.exception("failed to process order %s", order.id)
    raise
```

Chapter 29 will wire this into a deployed app where logs are the only way to see what happened.

:::scenario A background sync job keeps "succeeding" while syncing nothing
A nightly job imports partner data into your database. The dashboard says "Success" every night.
A customer complains that their record is three weeks stale. Investigation shows the job's main
loop is wrapped in a broad exception handler written by someone who wanted the job to be
"resilient".
:::

:::solution Delete the blanket handler; fail per record, loudly and specifically
The code was:

```python
for record in payload:
    try:
        save(record)
    except Exception:
        continue        # "keep going if one record is bad"
```

`save()` had started raising `IntegrityError` for *every* record after a schema change. The
handler hid it, the loop skipped everything, and the job reported success. The fix splits the
failure modes:

```python
import logging

log = logging.getLogger(__name__)
failed = []

for record in payload:
    try:
        save(record)
    except ValidationError as err:
        log.warning("skipping record %s: %s", record.get("id"), err)
        failed.append(record.get("id"))
    except Exception:
        log.exception("unexpected failure on record %s", record.get("id"))
        raise          # a real bug — stop the job

if failed:
    log.error("%d of %d records failed", len(failed), len(payload))
    raise RuntimeError(f"sync incomplete, failures: {failed}")
```

Three changes do the work. Expected, per-record problems (`ValidationError`) are caught narrowly,
counted, and reported. Unexpected problems are logged with a full traceback and re-raised, so the
job fails instead of lying. And the job now checks its own results — a run that processed zero
records or lost more than a few is treated as a failure, not a success.

The principle: **catch the errors you know how to handle, and let everything else stop the
program.** A crashed job that pages someone at 02:00 is fixed that week. A job that silently
succeeds while doing nothing can run broken for a month. Chapter 11 turns this into tests, and
Chapter 29 into monitoring and alerts for the deployed app.
:::

## Key takeaways

- Syntax errors stop parsing, exceptions happen at runtime, logic errors produce wrong answers
  with no error at all.
- All normal exceptions inherit from `Exception`; `FileNotFoundError` and `PermissionError` are
  both `OSError`s.
- `try` guards risky code, `except` handles a specific failure, `else` runs only on success, and
  `finally` always runs for cleanup.
- Order `except` blocks from most specific to least; a broad `Exception` first makes the rest dead
  code.
- `raise ... from err` chains exceptions so the traceback shows the original cause.
- `assert` documents internal invariants and is stripped by `python3 -O` — validate user input with
  `if` and `raise` instead.
- EAFP (try and handle) is the Pythonic default; check first when failure is common or you need a
  better error message.
- Use `logging`, not `print`: levels, timestamps, and `log.exception()` for tracebacks.

## Practice

- [ ] Write `safe_div.py`: read two numbers with `input()`, divide them, and print a friendly
      message on `ZeroDivisionError` and on `ValueError` without crashing.
- [ ] Write `read_maybe.py`: try to open a filename given by the user; print its contents if it
      exists, and a clear message if not. Use `try`/`except FileNotFoundError`, not an `if`.
- [ ] Write `retry.py`: a function that calls another function up to three times, catching
      `ValueError`, printing each attempt, and raising `RuntimeError` with `from` if all three
      fail.
- [ ] Write `validate.py`: define a `ConfigError(Exception)` class and a `load_port(value)`
      function that raises it (chained from the original `ValueError`) when the value is not an
      integer between 1 and 65535. Demonstrate both a failing and a passing call.
- [ ] Write `rollback.py`: simulate a two-step operation (write a file, then "commit" a message to
      a list) where the second step fails; use `try`/`except`/`finally` so the file is always
      deleted afterwards, and print what happened at each stage.
- [ ] Write `importer.py`: parse a list of strings like `"ada:42"`, `"bad"`, `"grace:91"` into a
      dict, using `logging` to record a warning for each malformed entry, skipping it, and
      printing the successful results. Include `logging.basicConfig` at the top.

## Solutions

:::solution Exercise 1
```python
# safe_div.py
try:
    a = int(input("First number: "))
    b = int(input("Second number: "))
    print(f"{a} / {b} = {a / b}")
except ValueError:
    print("That was not a whole number.")
except ZeroDivisionError:
    print("You cannot divide by zero.")
```
Both failures come from different lines but land in the same `try` — that is fine here because the
block is short. `int("abc")` raises `ValueError`, division by zero raises `ZeroDivisionError`, and
each gets its own message instead of a traceback.
:::

:::solution Exercise 2
```python
# read_maybe.py
from pathlib import Path

name = input("Filename: ")
try:
    print(Path(name).read_text(encoding="utf-8"))
except FileNotFoundError:
    print(f"No such file: {name}")
except OSError as err:
    print(f"Could not read {name}: {err}")
```
This is EAFP: attempt the read and handle the failure. `FileNotFoundError` is a subclass of
`OSError`, so it must come first — otherwise the broader block would swallow it and give a vaguer
message.
:::

:::solution Exercise 3
```python
# retry.py
from itertools import count

counter = count(1)


def flaky():
    """Fails twice, then succeeds."""
    attempt = next(counter)
    if attempt < 3:
        raise ValueError(f"not ready (call {attempt})")
    return "ok"


def call_with_retry(func, attempts=3):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except ValueError as err:
            print(f"attempt {attempt} failed: {err}")
            last_error = err
    raise RuntimeError(f"{func.__name__} failed after {attempts} attempts") from last_error


print(call_with_retry(flaky))
```
Catching only `ValueError` means a `TypeError` — a genuine bug — is not retried three times before
being reported. The final `raise ... from last_error` preserves the original failure in the
traceback instead of replacing it.
:::

:::solution Exercise 4
```python
# validate.py
class ConfigError(Exception):
    """Raised when configuration is invalid."""


def load_port(value):
    try:
        port = int(value)
    except ValueError as err:
        raise ConfigError(f"port must be an integer, got {value!r}") from err
    if not 1 <= port <= 65535:
        raise ConfigError(f"port {port} out of range 1-65535")
    return port


print(load_port("8080"))
try:
    load_port("http")
except ConfigError as err:
    print(f"config error: {err}")
```
Deriving from `Exception` gives you a class callers can catch by name. Chaining from the original
`ValueError` means the traceback still shows the real cause underneath your clearer message.
:::

:::solution Exercise 5
```python
# rollback.py
from pathlib import Path

temp = Path("pending.txt")
committed = []

try:
    temp.write_text("half-finished work", encoding="utf-8")
    print("step 1: wrote temp file")
    raise RuntimeError("commit failed: database unavailable")
    committed.append("work")          # never reached
except RuntimeError as err:
    print(f"step 2 failed: {err}")
finally:
    temp.unlink(missing_ok=True)
    print(f"cleanup: temp removed (exists={temp.exists()}), committed={committed}")
```
`finally` runs whether the `try` succeeded or the `except` handled an error, which is exactly what
cleanup needs. `unlink(missing_ok=True)` makes the cleanup itself safe if the file was never
created.
:::

:::solution Exercise 6
```python
# importer.py
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

raw = ["ada:42", "bad", "grace:91", "", "linus:abc"]
scores = {}

for entry in raw:
    try:
        name, value = entry.split(":")
        scores[name] = int(value)
    except ValueError as err:
        log.warning("skipping malformed entry %r (%s)", entry, err)

print(scores)
```
```text
WARNING: skipping malformed entry 'bad' (not enough values to unpack (expected 2, got 1))
WARNING: skipping malformed entry '' (not enough values to unpack (expected 2, got 1))
WARNING: skipping malformed entry 'linus:abc' (invalid literal for int() with base 10: 'abc')
{'ada': 42, 'grace': 91}
```
Both failure modes — wrong number of fields and a non-numeric value — raise `ValueError`, so one
`except` covers them. Logging with `%r`/`%s` placeholders keeps the record machine-readable, and
the bad rows are reported rather than silently dropped.
:::
