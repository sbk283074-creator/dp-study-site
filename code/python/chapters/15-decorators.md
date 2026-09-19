---
chapter: 15
part: 2
title: Decorators & Closures
summary: Understand closures, then write the decorators real codebases use: timing, retries, caching, and plugin registries.
minutes: 40
tags: [closures, decorators, functools, lru_cache, metaprogramming]
---

Some behaviour does not belong inside a function. "Log every call", "retry on failure", "time
this", "register this as a known report" — none of that is the function's job, and pasting it into
every function body means twenty copies to maintain. Python's answer is the decorator: a function
that takes a function and returns a better one. To write them well you need one idea first — the
closure — because a closure is the mechanism that makes a decorator remember anything at all.

## Functions are objects

You already know functions are called with parentheses. They are also just values: they have
attributes, they can go in lists and dicts, and they can be passed to and returned from other
functions.

```python
def shout(text):
    return text.upper() + "!"

greet = shout          # no parentheses: this is assignment, not a call
print(greet("hi"))
print(shout.__name__)
```

```text
HI!
shout
```

Drop the parentheses and you are holding the function object itself. Add them and you are calling
it. Confusing those two is most of the difficulty in this chapter.

Passing a function to another function is how `sorted(key=...)`, `map()`, and `filter()` worked
back in Chapter 7:

```python
>>> sorted(["bb", "a", "ccc"], key=len)
['a', 'bb', 'ccc']
>>> sorted(["bb", "a", "ccc"], key=lambda s: s[-1])
['ccc', 'a', 'bb']
```

## Inner functions and closures

A `def` inside a `def` is an ordinary function with one extra power: it can see the enclosing
function's variables.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor        # factor comes from the enclosing scope
    return multiply

times3 = make_multiplier(3)
times10 = make_multiplier(10)

print(times3(7), times10(7))
```

```text
21 70
```

Here is the part that surprises people: `make_multiplier(3)` has *finished*. Its local variable
`factor` should be gone. But `times3(7)` still returns 21. The returned `multiply` function
carries a reference to the variable it needs — that pairing of a function with the variables it
captured is a **closure**.

```python
>>> times3.__closure__
(<cell at 0x1041a4b80: int object at 0x1040f4e30>,)
>>> times3.__closure__[0].cell_contents
3
```

Captured variables live in `cell` objects, not in a copy. Two consequences:

1. The captured value survives as long as the function does.
2. It is *shared*, not snapshotted — which produces the classic bug below.

To *rebind* a captured name you need `nonlocal`. Without it, assignment creates a new local and
you get `UnboundLocalError`:

```python
def counter():
    count = 0
    def increment():
        nonlocal count          # without this: UnboundLocalError
        count += 1
        return count
    return increment

tick = counter()
print(tick(), tick(), tick())
```

```text
1 2 3
```

Each call to `counter()` creates a fresh cell, so `tick` and `tock` count independently.

### The late-binding gotcha

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
```

```text
[2, 2, 2]
```

Not `[0, 1, 2]`. The three lambdas captured the *variable* `i`, not its value at creation time,
and by the time you call them the loop has finished with `i == 2`. This is the shared-cell rule,
and it bites hardest in loops that build callbacks, menu handlers, or test cases.

The fix is to bind the value at creation time, either with a default argument or a factory:

```python
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])
```

```text
[0, 1, 2]
```

Default arguments are evaluated once, when the function is created — so `i=i` freezes the current
value.

## Decorators

A decorator is a function that takes a function and returns a function. That is the whole
definition.

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"-> {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} returned {result!r}")
        return result
    return wrapper

def add(a, b):
    return a + b

decorated_add = log_call(add)
print(decorated_add(2, 3))
```

```text
-> add(2, 3)
<- add returned 5
5
```

`log_call(add)` returned `wrapper`, and `wrapper` still has a reference to the original `add` — a
closure. `*args, **kwargs` is what makes this work for any signature: capture everything, pass
everything through.

The `@` syntax is only shorthand for that assignment:

```python
@log_call
def add(a, b):
    return a + b
```

```python
# exactly equivalent
def add(a, b):
    return a + b
add = log_call(add)
```

Nothing more happens at import time than that assignment. `@` is not special syntax to the
interpreter; it is a convenience for a pattern you can always write by hand.

## `functools.wraps`

The version above has a defect. Look at the decorated function's identity:

```python
print(add.__name__, "|", add.__doc__)
```

```text
wrapper | None
```

The name is `wrapper` and the docstring is gone. Anything that inspects your function — `help()`,
auto-generated docs, Sphinx, pytest's test collection, FastAPI's route names, `functools.singledispatch`
— now sees the wrong thing. `functools.wraps` copies the identifying metadata from the original
onto the wrapper:

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"-> {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    """Add two numbers."""
    return a + b

print(add.__name__, "|", add.__doc__)
```

```text
add | Add two numbers.
```

Put `@wraps(func)` on every wrapper. There is no downside and no situation where you want the
wrapper's name leaking out.

## Decorators that take arguments

Want `@retry(times=3)`? Then the outermost thing is not a decorator — it is a factory that
*builds* a decorator. Three layers:

```python
def repeat(times):
    def decorator(func):          # receives the function
        @wraps(func)
        def wrapper(*args, **kwargs):   # receives the arguments
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def ping():
    print("ping", end=" ")
    return "done"

print(ping())
```

```text
ping ping ping done
```

Read the layers outside-in: `repeat(3)` runs first and returns `decorator`; `@decorator` then
wraps `ping`. The mental model is "arguments → function → wrapper".

## Stacking and ordering

```python
@bold
@italic
def hello():
    return "hi"
```

Decorators apply **bottom-up**: this is `bold(italic(hello))`. `italic` wraps first, then `bold`
wraps the result. So at call time the outermost (top) decorator runs first.

Order matters whenever decorators have side effects or transform values. `@timer` above
`@retry` times the whole retry loop; `@retry` above `@timer` times each individual attempt. If
the result looks wrong, reverse the stack before debugging anything else.

## Class-based decorators

A decorator needs to be callable and to remember state. A class with `__call__` does both, and is
cleaner than a closure once there is more than one piece of state:

```python
from functools import wraps

class count_calls:
    def __init__(self, func):
        wraps(func)(self)          # copy __name__/__doc__ onto the instance
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@count_calls
def fetch(url):
    """Fetch a URL."""
    return f"<html from {url}>"

print(fetch("a"), fetch("b"))
print(fetch.calls, fetch.__name__)
```

```text
<html from a> <html from b>
2 fetch
```

The decorated "function" is now an object with a `.calls` attribute. That is legitimate and
sometimes exactly what you want — just remember the trade: callers can no longer introspect it
like a plain function, and it will not work as a method descriptor without extra care.

## Four decorators worth writing

**`@timer`** — the one you will actually use while profiling:

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
    return wrapper

@timer
def slow():
    time.sleep(0.1)
    return sum(range(100_000))

print(slow())
```

```text
slow: 0.1051s
4999950000
```

Wrap the call in `try/finally` so a failing function still gets timed.

**`@retry`** — for flaky network calls (Chapter 18 will give you plenty of those):

```python
import time
from functools import wraps

def retry(times=3, delay=0.5, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last = exc
                    print(f"{func.__name__} attempt {attempt} failed: {exc}")
                    if attempt < times:
                        time.sleep(delay)
            raise last
        return wrapper
    return decorator

attempts = 0

@retry(times=3, delay=0.01, exceptions=(ConnectionError,))
def flaky():
    global attempts
    attempts += 1
    if attempts < 3:
        raise ConnectionError("connection reset")
    return "ok"

print(flaky())
```

```text
flaky attempt 1 failed: connection reset
flaky attempt 2 failed: connection reset
ok
```

Note the `exceptions` argument: retrying a `ValueError` from bad input is pointless and hides real
bugs. Retry only transient failures.

**`@memoize`** — a hand-rolled cache, to show the mechanism:

```python
from functools import wraps

def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(40))
```

```text
102334155
```

Without the cache, `fib(40)` takes minutes. This version only handles hashable positional
arguments and grows without limit — which is why in real code you use:

```python
from functools import cache, lru_cache

@cache                      # unbounded; the fast modern default
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

@lru_cache(maxsize=128)     # bounded, evicts least-recently-used
def parse_config(path):
    return {"path": path}

print(fib.cache_info())
```

```text
CacheInfo(hits=38, misses=41, maxsize=None, currsize=41)
```

`cache_info()` tells you whether the cache is earning its keep. Caching a function with side
effects, or one whose result depends on something other than its arguments, is a bug generator —
only memoize pure functions.

**A registry decorator** — the pattern behind Flask routes, pytest's `@mark`, and plugin systems:

```python
from functools import wraps

REPORTS = {}

def report(name):
    def decorator(func):
        if name in REPORTS:
            raise ValueError(f"duplicate report name: {name!r}")
        REPORTS[name] = func
        return func          # return the original — no wrapping needed
    return decorator

@report("daily-signups")
def signups():
    return "1,204 new users"

@report("revenue")
def revenue():
    return "$12,388"

print(REPORTS)
print(REPORTS["revenue"]())
```

```text
{'daily-signups': <function signups at 0x...>, 'revenue': <function revenue at 0x...>}
$12,388
```

Notice this one returns `func` unchanged. A decorator does not have to modify behaviour —
registration is a perfectly good reason to exist. You will see this same idea in Chapter 26,
where FastAPI's `@app.get("/items")` registers a route rather than changing how the function
works.

:::note `functools.singledispatch`
`singledispatch` overloads a function on the type of its first argument without any `if
isinstance` chains:

```python
from functools import singledispatch

@singledispatch
def render(value):
    return str(value)

@render.register
def _(value):
    return f"{value:,}"

@render.register
def _(value):
    return "[" + ", ".join(render(v) for v in value) + "]"

print(render(1234567), render([1, 22]))
```
```text
1,234,567 [1, 22]
```
It is a decorator-driven alternative to the polymorphism you saw in Chapter 13, most useful when
you cannot modify the classes you are dispatching on.
:::

## When a decorator is the wrong tool

Reach for something else when:

- **The behaviour is configuration, not behaviour.** `@retry(3)` on one function is fine; on sixty
  functions it means your HTTP client should take a retry policy as a constructor argument.
- **You cannot understand the call.** Three stacked decorators that each change the return type is
  harder to debug than one explicit helper function.
- **The logic is genuinely part of the function.** If only one function needs it, write it inline.
  A decorator earns its keep at the second use, not the first.
- **Order bugs keep appearing.** If correctness depends on decorator order, that is a signal the
  composition should be explicit.

:::scenario Your tests vanish after you add a logging decorator
You wrap every handler in a `@log_calls` decorator so the team can trace requests. The next CI
run reports 0 tests collected in a file that clearly has twelve `test_` functions. Separately, the
new FastAPI service starts returning 404s on routes that were working, and the auto-generated docs
label every endpoint "wrapper".
:::

:::solution The decorator erased the functions' identities
Both failures have one cause: the wrapper replaced the original function, and everything
downstream identifies functions by `__name__`. pytest collects functions named `test_*`; the
wrapper is named `wrapper`. FastAPI derives route names and operation IDs from `__name__`, so
every route collided on `wrapper`.

```python
def log_calls(func):
    def wrapper(*args, **kwargs):        # BUG: identity lost
        print(f"call {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def test_addition():
    assert 1 + 1 == 2

print(test_addition.__name__)   # wrapper  -> pytest ignores it
```

Add `@wraps`:

```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"call {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def test_addition():
    assert 1 + 1 == 2

print(test_addition.__name__)   # test_addition -> pytest collects it
```

```text
wrapper
test_addition
```

Two follow-ups worth adopting: use the `logging` module instead of `print` so the decorator can
be turned off, and make pytest itself your check — `pytest --collect-only` lists what pytest
actually sees, which is how you confirm the fix.
:::

:::pitfall Mutable state captured in a closure
This one produces bugs that look like the cache is broken or the counter is wrong:

```python
def collect(func):
    seen = []                    # created ONCE, when the decorator runs
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        seen.append(result)
        return result
    return wrapper

@collect
def double(x):
    return x * 2

print(double(1))
print(double(2))
```

```text
2
4
```

`seen` is not per-call and not per-argument — it is one list shared by every call, forever. That
is sometimes exactly what you want (a memo cache), and sometimes a slow memory leak and a
cross-request data bleed. In a web app, a module-level or closure-level list like this is shared
by all users, which is how one person's data ends up in another person's response.

Two rules: (1) if you want per-call state, create it inside `wrapper`; (2) if you want shared
state, give it a name and an accessor so it is obviously shared (`double.seen`), and consider
whether it should live in an object instead — Chapter 12's classes are the right home for state
with behaviour. And when you need to *rebind* rather than mutate, remember `nonlocal`, or you
will get `UnboundLocalError: cannot access local variable`.
:::

## Key takeaways

- Functions are objects: they can be assigned, stored in containers, passed as arguments, and
  returned from other functions.
- A closure is a function plus the variables it captured from an enclosing scope; those variables
  survive after the outer function returns and are shared, not copied.
- Loop variables captured by lambdas are bound late; use `lambda x=x: ...` to freeze the value.
- `@decorator` above `def f()` is exactly `f = decorator(f)`.
- Always apply `functools.wraps` to the wrapper, or you lose `__name__`, `__doc__`, and
  everything that depends on them.
- A decorator taking arguments has three layers: arguments, then function, then wrapper.
- Stacked decorators apply bottom-up, so the top one runs first at call time.
- `@cache`/`@lru_cache` memoize pure functions; registry decorators can return the function
  unchanged.

## Practice

- [ ] Write `make_adder(n)` that returns a function adding `n` to its argument. Build `add5` and
      `add10` and prove they are independent.
- [ ] Reproduce the late-binding bug with `[lambda: i for i in range(3)]`, print the results, then
      fix it with a default argument.
- [ ] Write `@timer` with `functools.wraps` and `try/finally`, and use it on a function that sleeps
      0.1s and returns a value.
- [ ] Write `@retry(times=3, delay=0.01)` that only retries `ConnectionError`, and test it against
      a function that fails twice then succeeds.
- [ ] Build a `COMMANDS` registry: a `@command("name")` decorator plus a `dispatch(name)` function
      that looks the name up and calls it, raising `KeyError` for unknown names.
- [ ] Compare `fib(35)` with and without `@cache` from `functools`, and print `cache_info()` for
      the cached version.

## Solutions

:::solution Exercise 1
```python
def make_adder(n):
    def adder(x):
        return x + n
    return adder

add5 = make_adder(5)
add10 = make_adder(10)
print(add5(3), add10(3))
print(add5.__closure__[0].cell_contents, add10.__closure__[0].cell_contents)
```
```text
8 13
5 10
```
Each call to `make_adder` creates a new scope with its own `n`, so the two returned functions
hold different cells even though they share the same code.
:::

:::solution Exercise 2
```python
broken = [lambda: i for i in range(3)]
fixed = [lambda i=i: i for i in range(3)]

print([f() for f in broken])
print([f() for f in fixed])
```
```text
[2, 2, 2]
[0, 1, 2]
```
The lambdas capture the variable `i`, not its value, so they all read the final value `2`. The
default argument `i=i` is evaluated when each lambda is created, freezing that iteration's value.
:::

:::solution Exercise 3
```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
    return wrapper

@timer
def slow():
    time.sleep(0.1)
    return "finished"

print(slow(), slow.__name__)
```
```text
slow took 0.1013s
finished slow
```
`try/finally` guarantees the timing prints even if the function raises. `@wraps` is why
`slow.__name__` is still `slow`.
:::

:::solution Exercise 4
```python
import time
from functools import wraps

def retry(times=3, delay=0.01, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last = exc
                    if attempt < times:
                        time.sleep(delay)
            raise last
        return wrapper
    return decorator

attempts = 0

@retry(times=3, delay=0.01, exceptions=(ConnectionError,))
def flaky():
    global attempts
    attempts += 1
    if attempts < 3:
        raise ConnectionError("reset by peer")
    return "connected"

print(flaky())
print(flaky.__name__, attempts)
```
```text
connected
flaky 3
```
Restricting `exceptions` matters: with the default `(Exception,)` this would also swallow
`TypeError` from a genuine bug and turn a one-line fix into a three-second hang.
:::

:::solution Exercise 5
```python
from functools import wraps

COMMANDS = {}

def command(name):
    def decorator(func):
        if name in COMMANDS:
            raise ValueError(f"duplicate command: {name!r}")
        COMMANDS[name] = func
        return func
    return decorator

def dispatch(name, *args, **kwargs):
    if name not in COMMANDS:
        raise KeyError(f"unknown command: {name!r}")
    return COMMANDS[name](*args, **kwargs)

@command("greet")
def greet(who="world"):
    return f"hello, {who}"

@command("quit")
def quit_cmd():
    return "bye"

print(dispatch("greet", "ada"))
print(dispatch("quit"))
print(sorted(COMMANDS))
```
```text
hello, ada
bye
['greet', 'quit']
```
The decorator returns `func` unchanged because it registers rather than wraps — so `greet` is
still an ordinary function you can call directly or test in isolation.
:::

:::solution Exercise 6
```python
import time
from functools import cache

def fib_plain(n):
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)

@cache
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)

start = time.perf_counter()
result_plain = fib_plain(35)
elapsed_plain = time.perf_counter() - start

start = time.perf_counter()
result_cached = fib_cached(35)
elapsed_cached = time.perf_counter() - start

print(result_plain, f"{elapsed_plain:.4f}s")
print(result_cached, f"{elapsed_cached:.6f}s")
print(f"speedup: {elapsed_plain / elapsed_cached:,.0f}x")
print(fib_cached.cache_info())
fib_cached.cache_clear()
print(fib_cached.cache_info())
```
```text
9227465 1.8451s
9227465 0.000041s
speedup: 45,000x
CacheInfo(hits=33, misses=36, maxsize=None, currsize=36)
CacheInfo(hits=0, misses=0, maxsize=None, currsize=0)
```
The plain version recomputes the same sub-problems exponentially many times; the cached version
computes each one once. `cache_clear()` exists because an unbounded cache is a memory decision as
well as a speed one.
:::
