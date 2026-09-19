---
chapter: 5
part: 1
title: Functions
summary: Package code into reusable, testable units — arguments, scope, recursion, lambdas — and break a long script into functions you can actually reason about.
minutes: 40
tags: [functions, arguments, scope, recursion, refactoring]
---

Copy-paste is the enemy. The moment you write the same six lines twice, a future change has two
places to happen and one of them will be forgotten. Functions are the fix: a named block of code
that takes inputs, does work, and hands back a result. They are also the unit of *thinking* — a
program made of well-named functions can be read top-down like a table of contents, which is why
every chapter after this one assumes you are organising code this way.

## Defining and calling

```python
def area(width, height):
    """Return the area of a rectangle."""
    return width * height

print(area(3, 4))
```

```text
12
```

Three parts: `def`, the name, and the parameter list in parentheses. The indented block is the
**body**. Calling `area(3, 4)` binds `3` to `width` and `4` to `height`, runs the body, and
replaces the call expression with whatever `return` produced.

The `return` on line 3 is the point of the whole exercise. Compare:

```python
def area_print(width, height):
    print(width * height)

result = area_print(3, 4)
print(f"result is {result}")
```

```text
12
result is None
```

### `return`, not `print`

`print()` writes to the screen — a **side effect** that nobody else can use. `return` hands a
value back to the caller, which can then print it, store it, add it to something, or pass it to
another function. Beginners `print` inside functions because they want to *see* the answer; the
habit makes the function useless in every other context.

Rule of thumb: **compute and return at the bottom, print at the top.** One place in your program
talks to the user — usually `main()` or the module level — and every function below it returns
values.

### Functions that fall off the end return `None`

If a function has no `return`, or a `return` with no value, it returns `None`:

```python
>>> def nothing():
...     pass
>>> print(nothing())
None
```

That is why `result` above was `None`. It is also the source of a classic bug:

```python
>>> numbers = [3, 1, 2]
>>> numbers = numbers.sort()      # sort() returns None!
```
`list.sort()` sorts in place and returns `None` (Chapter 6 covers this in detail). The method
either *returns* a new value or *mutates* the existing one — never assume which, and never assign
the result of a method you have not checked.

## Arguments

### Defaults

```python
def connect(host, port=5432, timeout=5.0):
    return f"connecting to {host}:{port} (timeout {timeout}s)"

print(connect("db.internal"))
print(connect("db.internal", 3306))
print(connect("db.internal", timeout=30))
```

```text
connecting to db.internal:5432 (timeout 5.0s)
connecting to db.internal:3306 (timeout 5.0s)
connecting to db.internal:5432 (timeout 30s)
```

Parameters with defaults must come after parameters without them, otherwise Python cannot tell
which argument fills which slot. Use defaults for the "usually fine" values so callers only
mention what is unusual — that is why the third call above is so readable.

### Keyword arguments

Any argument can be passed by name (`timeout=30`), which makes call sites self-documenting and
lets you skip over parameters you do not care about. Prefer keywords for booleans especially:
`send(retries=3)` beats `send(3)`, and `render(caching=True)` beats `render(True)`.

### `*args` and `**kwargs`

When you do not know how many arguments will arrive, collect them:

```python
def total(*amounts):
    """Sum any number of amounts."""
    result = 0.0
    index = 0
    while index < len(amounts):
        result += amounts[index]
        index += 1
    return result

print(total(1.5, 2.25, 9.99))
```

```text
13.74
```

Inside the function, `amounts` is a tuple. `**kwargs` does the same for keyword arguments,
collecting them into a dict (Chapter 6 covers both types properly):

```python
def log(level, message, **context):
    extra = " ".join(f"{key}={value}" for key, value in context.items())
    print(f"[{level}] {message} {extra}".rstrip())

log("INFO", "user signed in", user="ada", ip="10.0.0.4")
```

The names `args` and `kwargs` are convention; the `*` and `**` are the syntax.

### Positional-only and keyword-only parameters

Two markers give you control over *how* callers may pass things:

- Everything before `/` is **positional-only** — it cannot be passed by keyword.
- Everything after `*` is **keyword-only** — it must be passed by name.

```python
def power(base, exponent, /, *, modulo=None):
    result = base ** exponent
    if modulo is not None:
        result %= modulo
    return result

print(power(2, 10))
print(power(2, 10, modulo=1000))
```

```text
1024
24
```

```python
>>> power(base=2, exponent=10)
TypeError: power() got some positional-only arguments passed as keyword arguments
```

The standard library uses these constantly: `len()` rejects `len(obj=...)` because the parameter
name is an implementation detail, and `print(*values, sep="", end="\n")` makes `sep` and `end`
keyword-only so they cannot be confused with the values being printed. Use `/` when you want the
freedom to rename a parameter later, and `*` when a call site would otherwise be unreadable
(`power(2, 10, 1000)` means nothing; `power(2, 10, modulo=1000)` is obvious).

Full parameter order: positional-only → normal → `*args` → keyword-only → `**kwargs`.

## Scope: where a name is visible

Python resolves a name using **LEGB**: **L**ocal, **E**nclosing, **G**lobal, **B**uilt-in.

```python
discount = 0.10          # global

def price_for(amount):
    tax = 0.085          # local: created and destroyed with the call
    return amount * (1 + tax) * (1 - discount)
```

`tax` is local — it does not exist outside `price_for`. `discount` is global: readable inside any
function, but **writing** to it from inside a function is a different story:

```python
counter = 0

def bump():
    counter += 1         # UnboundLocalError!
```

```text
UnboundLocalError: cannot access local variable 'counter' where it is not
associated with a value
```

Assigning to `counter` anywhere in the body makes it local for the whole function, so the
`counter += 1` read fails before any local value exists. Python is telling you the truth: the name
is local, and you have not given it a value.

You *can* opt out:

```python
counter = 0

def bump():
    global counter
    counter += 1
```

:::warning `global` and `nonlocal` are last resorts
`global` makes state changes invisible at the call site and makes functions impossible to test in
isolation — Chapter 11 will show you why. Nearly always, the better answer is to pass the value in
and return the new one:

```python
def bump(counter):
    return counter + 1

counter = bump(counter)
```

`nonlocal` does the same for a variable in an enclosing function's scope. It exists for closures,
which Chapter 15 covers properly. If you reach for either keyword in ordinary code, treat it as a
design smell and ask whether a class (Chapter 12) or a return value would be cleaner.
:::

## Docstrings

A string literal as the first statement in a function is its **docstring**. It is not a comment —
Python stores it, and tools read it:

```python
def celsius(fahrenheit):
    """Convert a Fahrenheit temperature to Celsius."""
    return (fahrenheit - 32) * 5 / 9

print(celsius.__doc__)
help(celsius)
```

```text
Convert a Fahrenheit temperature to Celsius.
```

One line for the summary, a blank line, then details if the function is non-obvious. Write what the
function *does* and what it *returns*, not how it does it — the code already says how. Chapter 22
adds the conventions that turn docstrings into generated documentation.

## Functions are values

`def` binds a name to a function object, and function objects are ordinary values. You can pass
them around like numbers:

```python
def double(x):
    return x * 2

def apply_twice(fn, value):
    return fn(fn(value))

print(apply_twice(double, 5))
```

```text
20
```

Pass `double`, not `double()` — the parentheses *call* the function, and without them you are
handing over the function itself. This is how the standard library stays flexible:
`sorted(words, key=len)` passes the `len` function to be called later.

The same idea gives you a dispatch table, which is a cleaner alternative to a long `if`/`elif`
chain:

```python
OPERATIONS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}

print(OPERATIONS["*"](6, 7))
```

Chapter 20 builds real CLI tools on this pattern, and Chapter 15 shows decorators — functions that
take a function and return a better one.

## `lambda`, and when it is a mistake

`lambda` is a one-expression anonymous function: `lambda a, b: a + b` is `def(a, b): return a + b`
with no name allowed. It earns its place when a function is needed for exactly one moment and is
trivial:

```python
>>> names = ["ada", "grace", "alan"]
>>> sorted(names, key=lambda name: name[-1])
['ada', 'alan', 'grace']
```

It stops being a good idea the moment the expression grows. This is bad:

```python
key=lambda record: (record.split(":")[1].strip().lower(), -len(record))
```

Nobody can read it, nobody can test it in isolation, and the traceback will point at a line with no
name. Give it a `def` and a docstring instead. If you cannot fit a `lambda` on one line and still
understand it at a glance, it wants a name.

## Recursion

A function may call itself. Every recursive function needs **a base case** — an input it answers
directly — and a **recursive case** that moves closer to it:

```python
def factorial(n):
    """Return n! for a non-negative integer n."""
    if n < 0:
        raise ValueError("factorial needs a non-negative integer")
    if n <= 1:          # base case
        return 1
    return n * factorial(n - 1)   # recursive case, nearer the base

print(factorial(5))
```

```text
120
```

Remove the base case and you get `RecursionError: maximum recursion depth exceeded`, which is
Python's safety net at roughly 1000 nested calls.

Fibonacci is the classic second example — and the classic warning:

```python
def fib(n):
    """Return the nth Fibonacci number (0, 1, 1, 2, 3, ...)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10))
```

```text
55
```

Correct, and catastrophically slow: `fib(35)` recomputes the same sub-problems millions of times.
Recursion is the right tool for tree-shaped problems (directory walks, nested JSON, parsers); for
linear sequences, a loop or an iterative accumulator is faster and cannot blow the stack. Chapter 15
fixes `fib` properly with caching.

## Pure functions

A **pure** function depends only on its arguments and changes nothing outside itself: same inputs,
same output, no side effects. `area()` and `celsius()` are pure. `print()`, `input()`, anything
that writes a file or mutates a global, is not.

Pure functions are trivially testable — no setup, no teardown, no mocks — which is why the
decomposition below pushes all the printing into `main()` and keeps everything else pure. Chapter 11
builds on exactly this property.

## Decomposition: forty lines into five functions

Here is a realistic monolith. It works, but it is four concerns tangled together — parsing,
arithmetic, formatting, and output:

```python
# orders_monolith.py
raw = """bolt,240,0.45
washer,1200,0.08
wrench,6,89.90"""

TAX_RATE = 0.085

lines = raw.strip().splitlines()
subtotal = 0.0
rows = []
index = 0

while index < len(lines):
    parts = lines[index].split(",")
    name = parts[0].strip()
    qty = int(parts[1])
    price = float(parts[2])
    line_total = qty * price
    subtotal += line_total
    rows.append(f"{name:<12}{qty:>6,}{price:>10.2f}{line_total:>12,.2f}")
    index += 1

tax = subtotal * TAX_RATE
header = f"{'Item':<12}{'Qty':>6}{'Unit':>10}{'Value':>12}"
rule = "-" * len(header)
print(header)
print(rule)
print("\n".join(rows))
print(rule)
print(f"{'Subtotal':<12}{'':>6}{'':>10}{subtotal:>12,.2f}")
print(f"{'Tax':<12}{'':>6}{'':>10}{tax:>12,.2f}")
print(f"{'TOTAL':<12}{'':>6}{'':>10}{subtotal + tax:>12,.2f}")
```

Now the same program, decomposed:

```python
# orders.py
DATA = """bolt,240,0.45
washer,1200,0.08
wrench,6,89.90"""

TAX_RATE = 0.085


def parse_order(line):
    """Split one 'name,qty,price' line into typed values."""
    name, qty, price = line.split(",")
    return name.strip(), int(qty), float(price)


def row_total(qty, price):
    """Extended price for one order line."""
    return qty * price


def format_row(name, qty, price, total):
    """Return one fixed-width report line."""
    return f"{name:<12}{qty:>6,}{price:>10.2f}{total:>12,.2f}"


def build_report(lines, tax_rate=TAX_RATE):
    """Return the complete report as a single string."""
    rows = []
    subtotal = 0.0
    index = 0

    while index < len(lines):
        name, qty, price = parse_order(lines[index])
        total = row_total(qty, price)
        subtotal += total
        rows.append(format_row(name, qty, price, total))
        index += 1

    tax = subtotal * tax_rate
    header = f"{'Item':<12}{'Qty':>6}{'Unit':>10}{'Value':>12}"
    rule = "-" * len(header)
    footer = (
        f"{'Subtotal':<12}{'':>6}{'':>10}{subtotal:>12,.2f}\n"
        f"{'Tax':<12}{'':>6}{'':>10}{tax:>12,.2f}\n"
        f"{'TOTAL':<12}{'':>6}{'':>10}{subtotal + tax:>12,.2f}"
    )
    return "\n".join([header, rule, *rows, rule, footer])


def main():
    print(build_report(DATA.strip().splitlines()))


main()
```

```bash
python3 orders.py
```

```text
Item              Qty      Unit       Value
-------------------------------------------
bolt             240      0.45      108.00
washer         1,200      0.08       96.00
wrench             6     89.90      539.40
-------------------------------------------
Subtotal                                743.40
Tax                                      63.19
TOTAL                                   806.59
```

What changed: every function does one thing and has a name that says it. `build_report` is pure —
feed it lines, get a string — so you can test it without capturing stdout. `main()` is the only
part that talks to the outside world. Chapter 10 explains why `main()` is normally behind an
`if __name__ == "__main__":` guard: it stops the report printing when another file imports this
module to reuse `build_report`.

Decomposition is not about line count; the second version is barely shorter. It is about being able
to change the tax logic without reading the formatting code.

:::pitfall The mutable default argument
A default value is evaluated **once**, when the function is defined — not each time it is called.
With an immutable default (`0.085`, `"USD"`, `None`) you never notice. With a mutable one you get a
bug that survives code review:

```python
def add_item(item, cart=[]):
    cart.append(item)
    return cart

print(add_item("apple"))
print(add_item("banana"))
print(add_item("pear"))
```

```text
['apple']
['apple', 'banana']
['apple', 'banana', 'pear']
```

Every call appends to *the same list*, created the moment `def` ran. The cart is never empty after
the first order, and in a web app that means one customer's items appear in another customer's.

The fix is a `None` sentinel with the real default created inside the body:

```python
def add_item(item, cart=None):
    if cart is None:
        cart = []
    cart = [*cart, item]      # new list, caller's list untouched
    return cart
```

Two details matter. `cart is None` (not `== None`) is the identity test for the sentinel. And
building a *new* list instead of calling `.append()` means a caller who passes their own list does
not have it mutated underneath them — the function returns a value rather than reaching out and
changing someone else's data. If you genuinely want to accumulate into a caller's list, say so in
the docstring and return `None`. Chapter 6 covers list copying properly, and Chapter 16 shows how
type hints make the `None` sentinel explicit.
:::

:::scenario "It works alone, but crashes when I call it twice"
A teammate adds a retry counter to a download helper:

```python
retries = 0

def download(url):
    response = fetch(url)
    if not response.ok:
        retries += 1
    return response
```

The very first call dies with `UnboundLocalError: cannot access local variable 'retries'`, which
is baffling because `retries` is plainly defined at the top of the file.
:::

:::solution Assignment makes the name local for the whole function
Python decides a name's scope at compile time, per function: any name you *assign* to anywhere in
the body is local everywhere in that body. The `retries += 1` makes `retries` local, so the read on
its right-hand side looks for a local that does not exist yet. The global `retries = 0` is shadowed
and unreachable.

You can force it with `global retries`, and that will make the error go away. Do not stop there.
Global mutable state means the function's behaviour depends on what happened before it was called,
so it cannot be tested in isolation, cannot be run twice cleanly, and breaks the moment two threads
call it (Chapter 21).

Return the state instead:

```python
def download(url, retries=0):
    """Fetch a URL; return (response, updated retry count)."""
    response = fetch(url)
    if not response.ok:
        retries += 1
    return response, retries

response, retries = download(url, retries)
```

Now the caller owns the counter, the function is pure, and `download(url, 0)` is a complete,
repeatable experiment. When the state genuinely belongs with the behaviour — several functions
sharing it — that is the signal to reach for a class, which is Chapter 12.

The debugging habit worth keeping: `UnboundLocalError` almost never means "the variable is
missing". It means "you assigned to this name somewhere in this function", and the fix is to decide
who should own the value.
:::

## Key takeaways

- `def` creates a function; `return` hands a value back to the caller, and a function with no
  `return` hands back `None`.
- Compute and return inside functions; print at the top level.
- Default arguments come last; call with keywords when the meaning is not obvious from position.
- `*args` collects extra positional arguments into a tuple, `**kwargs` extra keyword arguments into
  a dict.
- `/` marks positional-only parameters, `*` marks keyword-only ones.
- Names resolve Local → Enclosing → Global → Built-in; assigning to a global inside a function
  requires `global`, which is usually a design smell — return the new value instead.
- Recursion needs a base case; use it for nested data, not for long linear sequences.
- Prefer small, pure functions: they are testable, reusable, and readable top-down.

## Practice

- [ ] Write `double(n)`, `area(width, height)`, and `initials(first, last)`. Call each one and
      print the result. Then delete the `return` from `double` and predict what
      `print(double(3))` shows — check the prediction in the REPL.
- [ ] Write `make_email(first, last, domain="example.com")` and call it three ways: positionally,
      with the default domain, and with `domain=` as a keyword.
- [ ] Write `average(*numbers)` returning the mean of any number of values, and
      `log_event(level, message, **context)` that prints `[LEVEL] message key=value ...`. Then
      write `power(base, exponent, /, *, modulo=None)` and confirm that
      `power(base=2, exponent=10)` raises `TypeError`.
- [ ] Write `factorial(n)` and `fib(n)` recursively, each with a non-negative guard, plus
      `sum_digits(n)` that returns the sum of a number's digits (`sum_digits(472)` is `13`)
      without converting to a string.
- [ ] Refactor a gradebook script into four functions: `letter(score)`, `average(*scores)`,
      `format_student(name, *scores)`, and a pure `build_gradebook(records)` that returns the
      whole report as one string. Add a `main()` that prints it.

## Solutions

:::solution Exercise 1
```python
def double(n):
    return n * 2

def area(width, height):
    return width * height

def initials(first, last):
    return f"{first[0].upper()}.{last[0].upper()}."

print(double(21))
print(area(3, 4))
print(initials("ada", "lovelace"))
```

```text
42
12
A.L.
```

With `return` deleted, `double(3)` returns `None`, so `print(double(3))` prints `None` — no error,
which is exactly why this bug survives. The function did the work and threw the answer away.
:::

:::solution Exercise 2
```python
def make_email(first, last, domain="example.com"):
    """Build a lower-cased email address from a person's name."""
    return f"{first.strip().lower()}.{last.strip().lower()}@{domain}"

print(make_email("Ada", "Lovelace"))
print(make_email("Ada", "Lovelace", "python.org"))
print(make_email(first="Grace", last="Hopper", domain="navy.mil"))
```

```text
ada.lovelace@example.com
ada.lovelace@python.org
grace.hopper@navy.mil
```

Defaults belong on the value that changes least often. Once a third caller needs a different
domain, the keyword form keeps it obvious which value is which.
:::

:::solution Exercise 3
```python
def average(*numbers):
    """Return the mean of the given numbers."""
    total = 0.0
    index = 0
    while index < len(numbers):
        total += numbers[index]
        index += 1
    return total / len(numbers)

def log_event(level, message, **context):
    """Print a structured log line with optional key=value context."""
    extra = " ".join(f"{key}={value}" for key, value in context.items())
    print(f"[{level.upper()}] {message} {extra}".rstrip())

def power(base, exponent, /, *, modulo=None):
    """Raise base to exponent, optionally reduced modulo a number."""
    result = base ** exponent
    if modulo is not None:
        result %= modulo
    return result

print(average(1, 2, 3, 4))
log_event("warn", "disk almost full", used="91%", mount="/data")
print(power(2, 10), power(2, 10, modulo=1000))
print(power(base=2, exponent=10))   # TypeError: positional-only arguments
```

```text
2.5
[WARN] disk almost full used=91% mount=/data
1024 24
```

`average()` with no arguments raises `ZeroDivisionError` — a real edge case, and one that
`max(len(numbers), 1)` or an explicit guard would handle. `power` rejects keyword passing for
`base` and `exponent` because of the `/`, and requires `modulo` to be named because of the `*`.
:::

:::solution Exercise 4
```python
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fib(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

def sum_digits(n):
    """Return the sum of the decimal digits of a non-negative integer."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 10:          # base case: a single digit
        return n
    return n % 10 + sum_digits(n // 10)

print(factorial(5), fib(10), sum_digits(472))
```

```text
120 55 13
```

`sum_digits` peels off the last digit with `% 10` and recurses on the rest with `// 10`, so every
call is strictly smaller and must reach the single-digit base case. Raising `ValueError` for
negative input is better than returning a wrong number silently — Chapter 9 makes this the
standard pattern.
:::

:::solution Exercise 5
```python
GRADEBOOK = [
    ("Ada Lovelace", (95, 88, 92)),
    ("Alan Turing", (78, 85, 80)),
    ("Grace Hopper", (100, 97, 99)),
]


def letter(score):
    """Return the letter grade for a numeric score."""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def average(*scores):
    """Return the mean of the given scores."""
    total = 0.0
    index = 0
    while index < len(scores):
        total += scores[index]
        index += 1
    return total / len(scores)


def format_student(name, *scores):
    """Return one formatted gradebook row."""
    mean = average(*scores)
    return f"{name:<14}{mean:>7.1f}  {letter(mean)}"


def build_gradebook(records):
    """Return the whole gradebook as a single formatted string."""
    header = f"{'Student':<14}{'Avg':>7}  Grade"
    rows = []
    index = 0
    while index < len(records):
        name, scores = records[index]
        rows.append(format_student(name, *scores))
        index += 1
    return "\n".join([header, "-" * len(header), *rows])


def main():
    print(build_gradebook(GRADEBOOK))


main()
```

```text
Student            Avg  Grade
-----------------------------
Ada Lovelace      91.7  A
Alan Turing       81.0  B
Grace Hopper      98.7  A
```

`build_gradebook` never prints anything — it returns a string, so a test can call it and compare
the result directly (Chapter 11). The `while` index loop is the same shape as Chapter 4; Chapter 7
replaces it with `for name, scores in records:`, which is why keeping the iteration isolated in one
function pays off immediately.
:::
