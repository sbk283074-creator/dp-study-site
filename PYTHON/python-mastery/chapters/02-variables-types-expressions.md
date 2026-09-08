---
chapter: 2
part: 1
title: Variables, Types & Expressions
summary: Store data under names, convert between types deliberately, do arithmetic that means what you think it means, and understand what assignment actually does.
minutes: 30
tags: [variables, types, operators, input, f-strings]
---

Every program you will ever write does the same three things: it holds onto data, it gives that
data names, and it computes new data from it. Before you can read a file, query an API, or draw a
sprite, you need to be completely fluent in those three moves — and you need to know what Python
is doing behind the `=`, because the mental model most beginners bring to it is wrong in a way
that causes bugs for years.

## Values have types

A **value** is a piece of data: `42`, `3.14`, `"hello"`, `True`. Every value has a **type**, and
the type decides what you are allowed to do with it. Ask any value its type with `type()`:

```python
>>> type(42)
<class 'int'>
>>> type(3.14)
<class 'float'>
>>> type("hello")
<class 'str'>
>>> type(True)
<class 'bool'>
```

Four types cover most of what you touch daily:

| Type | Meaning | Examples | What it's for |
| --- | --- | --- | --- |
| `int` | Whole number, unlimited size | `0`, `-7`, `1_000_000` | Counting, indexing, IDs |
| `float` | Number with a decimal point | `3.14`, `-0.5`, `2.0` | Measurement, money-ish, ratios |
| `str` | Text (a sequence of characters) | `"ada"`, `'42'`, `""` | Names, messages, file content |
| `bool` | Truth value | `True`, `False` | Decisions — Chapter 4 runs on these |

Note `1_000_000`: underscores in numeric literals are ignored by Python and exist purely so you
can read large numbers. `1_000_000 == 1000000` is `True`.

`bool` is worth pausing on because it is a subtype of `int` under the hood — `True + True` is `2`.
That is occasionally handy and usually a sign you should be writing clearer code.

## Names are labels, not boxes

Here is the model to delete from your head: a variable is a box, and assignment puts a value into
the box. The accurate model: **a value exists somewhere in memory, and a name is a label stuck to
it.** Assignment sticks a label on a value. Reassignment moves the label to a different value.

```python
>>> x = 10
>>> y = x          # y now labels the same value 10
>>> x = 20         # x moves to a new value
>>> y
10
```

Moving `x` did not touch `y`. They were labels on the same value, and then `x` was peeled off and
stuck somewhere else. For numbers this is invisible, because numbers can never change. It becomes
visible with values that *can* change — lists and dicts, which arrive in Chapter 6:

```python
>>> a = [1, 2, 3]
>>> b = a          # b labels the SAME list — no copy is made
>>> b.append(4)
>>> a
[1, 2, 3, 4]
```

Nothing copied anything; `a` and `b` are two labels on one list, so a change seen through one is
seen through the other. This is **aliasing**, and it explains a huge family of "why did my data
change?" bugs. When you genuinely want a second, independent copy, ask for one explicitly
(`list(a)`, `a.copy()`), which is a Chapter 6 conversation.

## What you're allowed to call a name

The rules are short:

- Letters, digits, and underscores. Cannot start with a digit (`2fast` is illegal).
- Case-sensitive: `total`, `Total`, and `TOTAL` are three different names.
- Cannot be a reserved keyword (`if`, `for`, `class`, `return`, `None`, `True`...).

```python
>>> import keyword
>>> keyword.iskeyword("for")
True
>>> keyword.iskeyword("total")
False
```

Style is the part that matters more than the rules, because nobody reads code alone:

- `snake_case` for variables and functions: `user_name`, `total_price`.
- `UPPER_SNAKE_CASE` for constants: `TAX_RATE`, `MAX_RETRIES`.
- `PascalCase` for classes: `Player`, `Order` (Chapter 12).
- Names describe *what the value is*, not its type: `user_count`, not `int_users`.

These are PEP 8, Python's official style guide. Every formatter and linter you meet later assumes
them, and following them means your code looks like everyone else's on day one of a job.

## Assignment, rebinding, and unpacking

You can assign several names at once, which is how you write initial values compactly:

```python
>>> width, height = 1920, 1080
>>> x = y = 0
```

The first line is **tuple unpacking**: the values on the right are packed into a tuple and pulled
apart into the names on the left. The classic use is a swap, which needs no temporary variable:

```python
>>> a, b = 1, 2
>>> a, b = b, a
>>> a, b
(2, 1)
```

Unpacking also unpacks sequences, which is how you split a `"city, country"` string (Chapter 3
covers a cleaner way with `partition`):

```python
>>> first, rest = "Ada Lovelace".split(maxsplit=1)
>>> first, rest
('Ada', 'Lovelace')
```

The number of names must match the number of values, or Python raises `ValueError`.

**Augmented assignment** shortens "take the current value, change it, put it back":

```python
count = 0
count += 1        # count = count + 1
total *= 1.085    # apply 8.5% tax
text += "!"       # strings support + and * too
```

Every operator has an augmented form: `-=`, `*=`, `/=`, `//=`, `%=`, `**=`.

## Arithmetic

| Operator | Meaning | Example | Result |
| --- | --- | --- | --- |
| `+` | Addition | `7 + 2` | `9` |
| `-` | Subtraction | `7 - 2` | `5` |
| `*` | Multiplication | `7 * 2` | `14` |
| `/` | Division (always float) | `7 / 2` | `3.5` |
| `//` | Floor division | `7 // 2` | `3` |
| `%` | Modulo (remainder) | `7 % 2` | `1` |
| `**` | Exponent | `2 ** 10` | `1024` |

`/` always returns a `float`, even when the result is whole: `4 / 2` is `2.0`, not `2`. If you
want an integer answer, use `//`.

### Floor division and modulo

`//` rounds **down** (toward negative infinity, not toward zero), and `%` returns a remainder
whose sign matches the divisor. This surprises people exactly once:

```python
>>> 7 // 2, -7 // 2
(3, -4)
>>> 7 % 3, -7 % 3
(1, 2)
```

Modulo is the workhorse for "wrap around" logic: `minutes % 60` gives you the minute of the hour,
`(hour + 9) % 24` gives you a time nine hours from now. `divmod(a, b)` hands you both at once:

```python
>>> divmod(200, 60)
(3, 20)          # 200 seconds is 3 minutes 20 seconds
```

### Operator precedence

When an expression has several operators, Python applies this order (highest first):

| Level | Operators |
| --- | --- |
| 1 | `**` (right-associative: `2 ** 3 ** 2` is `2 ** 9` = 512) |
| 2 | unary `-`, `+` |
| 3 | `*`, `/`, `//`, `%` |
| 4 | `+`, `-` |
| 5 | comparisons (`<`, `<=`, `>`, `>=`, `==`, `!=`) |
| 6 | `not` |
| 7 | `and` |
| 8 | `or` |

Parentheses override everything and cost nothing. `-3 ** 2` is `-9` because `**` binds tighter
than unary minus — if you meant `(-3) ** 2`, write the parentheses, and so will every reader
after you.

## Converting between types

Data rarely arrives in the type you want. `input()` gives you strings; files give you strings;
APIs give you whatever the server felt like. Convert explicitly:

```python
>>> int("42")           # 42
>>> int(3.9)            # 3   — truncates toward zero, does not round
>>> int(-3.9)           # -3
>>> float("3.5")        # 3.5
>>> str(42)             # '42'
>>> bool("")            # False
>>> bool("False")       # True  — any non-empty string is true!
```

Two rules that will save you:

1. `int("3.9")` raises `ValueError` — `int()` will not parse a decimal string. Go through
   `float` first: `int(float("3.9"))`.
2. `str` → number conversions raise on garbage, so validate before converting (Chapter 4 builds
   the loop that does this, and Chapter 9 makes it bulletproof).

## Truthiness

Conditions do not require a `bool`; Python evaluates every value for truth. The rule is short:
**empty things and zero are falsey, everything else is truthy.**

| Falsey | Truthy |
| --- | --- |
| `False` | `True` |
| `0`, `0.0` | any other number (`-1` is truthy) |
| `""` | any non-empty string (`"0"` is truthy) |
| `None` | most objects |
| empty collections (`[]`, `{}`, `set()`) | non-empty collections |

`bool(value)` tells you which side a value falls on. Chapter 4 turns this into `if name:` instead
of `if len(name) > 0:`.

## None

`None` is Python's "no value here" marker, and it is what a function returns when it has nothing
to return (Chapter 5). It is falsey, it prints as `None`, and there is exactly one of them — which
is why you test for it with `is`, never `==`:

```python
result = None
if result is None:
    print("nothing to report")
```

## Constants, by convention

Python has no real constants. The signal is naming: `TAX_RATE` in caps tells every reader "do not
reassign this." Nothing stops you; that is the deal in a language that trusts adults. Chapter 13
introduces constructs that actually enforce immutability when you need it.

## `input()` always hands you a string

This is the single most common beginner bug in real scripts, so let's build the thing that trips
on it. A small order calculator:

```python
# receipt.py
TAX_RATE = 0.085

item = input("Item name: ")
price = float(input("Unit price: "))
quantity = int(input("Quantity: "))

subtotal = price * quantity
tax = subtotal * TAX_RATE
total = subtotal + tax

print(f"{quantity} x {item} @ {price}")
print(f"Subtotal: {subtotal}")
print(f"Tax:      {round(tax, 2)}")
print(f"Total:    {round(total, 2)}")
print(type(price), type(quantity), type(total))
```

```bash
python3 receipt.py
```

```text
Item name: bolt
Unit price: 1.10
Quantity: 3
3 x bolt @ 1.1
Subtotal: 3.3000000000000003
Tax:      0.28
Total:    3.58
<class 'float'> <class 'int'> <class 'float'>
```

Three things to notice. First, the conversions on lines 6–7 are mandatory: delete them and
`price * quantity` either explodes or silently repeats the string. Second, `3.3000000000000003` is
not a bug in your code — binary floating point cannot represent `1.10` exactly, and the error
shows up in arithmetic. Round for *display* (`round(x, 2)`), and reach for `decimal` when the
numbers are money that must balance (Chapter 17). Third, `f"..."` — an f-string — drops the value
of anything inside `{}` straight into the text.

## F-strings, first look

Put `f` before the quote, and every `{}` becomes an expression slot:

```python
name = "Ada"
age = 36
print(f"{name} is {age} next year: {age + 1}.")
```

```text
Ada is 36 next year: 37.
```

The slots hold expressions, not just names, and the result is always a string. Chapter 3 goes deep
on alignment, decimal places, and thousands separators — the stuff that turns `"Total: 3.58"` into
a properly aligned report column.

:::pitfall `is` is not `==`
`==` asks "are these values equal?" `is` asks "are these labels on the very same object?" They are
different questions, and Python will let you confuse them:

```python
>>> a = 500
>>> b = 500
>>> a == b          # True  — same value
True
>>> a is b          # False — two separate objects
False
>>> x = 100
>>> y = 100
>>> x is y          # True  — ???
True
```

That last result is the trap. CPython pre-creates and reuses the integers from `-5` to `256`, so
small numbers are shared objects and larger ones are not. The behaviour is an implementation
detail, not a language rule, which is why `is` gives different answers for `100` and `500`.

Use `==` for every value comparison. Use `is` only for identity against singletons: `x is None`,
`x is True`, `x is False`. Modern Python even emits a `SyntaxWarning` when you write `x is 500`,
because there is never a good reason to.
:::

:::scenario The nightly report prints `151515` instead of `45`
A batch job reads order quantities from a CSV export and multiplies each by a unit price. One row
prints `151515` where the total should be `45`, and another crashes with
`TypeError: can't multiply sequence by non-int of type 'float'`. Nobody changed the code.
:::

:::solution The data was never a number
The CSV reader hands you strings (Chapter 19 shows it doing exactly this), so `quantity` is `"3"`
and `price` is `15`. Watch what each combination does:

```python
>>> "3" * 15          # string repetition, not multiplication
'333333333333333333333333333333'
>>> "3" * 15.0        # float repeats are rejected outright
TypeError: can't multiply sequence by non-int of type 'float'
```

String `*` means "repeat me", which is why the first row produced a wall of digits, and it refuses
to repeat by a non-whole number, which is why the second row crashed. Converting at the boundary
fixes both:

```python
quantity = int(row["quantity"])
price = float(row["price"])
total = quantity * price
```

The general fix is a habit: **convert at the edges, compute in the middle.** As soon as data
enters your program — from `input()`, a file, an HTTP response, a database — turn it into the type
you actually want, once. Everything downstream then deals in real numbers, and this entire class
of bug disappears. Chapter 9 adds the validation that rejects `"abc"` before `int()` sees it.
:::

## Key takeaways

- Every value has a type (`int`, `float`, `str`, `bool`); `type(value)` tells you which.
- A name is a label on a value, not a box containing it — `b = a` creates a second label, not a
  copy.
- Use `snake_case` for names, `UPPER_SNAKE_CASE` for values you intend never to reassign.
- `a, b = b, a` swaps two names; `+=` and friends modify and rebind in one step.
- `/` always returns a `float`; `//` floors and `%` wraps.
- `int()`, `float()`, `str()`, and `bool()` convert explicitly; `input()` never converts for you.
- Empty and zero are falsey; everything else is truthy.
- Compare values with `==`; use `is` only for `None` and other singletons.

## Practice

- [ ] In the REPL, run `type()` on `7`, `7.0`, `"7"`, `True`, and `None`. Then run `bool()` on
      `0`, `""`, `"0"`, and `"False"`, and write down which are truthy.
- [ ] Ask the user for two numbers with `input()`, swap them with tuple unpacking, and print them
      before and after.
- [ ] Write `celsius.py`: read a Fahrenheit temperature, convert to Celsius
      (`(f - 32) * 5 / 9`), and print it rounded to one decimal with `round(c, 1)`.
- [ ] Write `clock.py`: ask for a start hour (0–23) and a number of hours to add, then print the
      resulting hour on a 24-hour clock using `%`.
- [ ] Write `receipt2.py`: ask for an item name, a unit price, and a quantity, then print an
      itemised receipt with subtotal, tax at 8.5%, and total — all rounded to two decimals.

## Solutions

:::solution Exercise 2
```python
a = input("First number: ")
b = input("Second number: ")

print(f"before: a={a}, b={b}")
a, b = b, a
print(f"after:  a={a}, b={b}")
```
The right side `b, a` is fully evaluated *before* any assignment happens, which is why no
temporary variable is needed and why this works on any number of names at once.
:::

:::solution Exercise 3
```python
fahrenheit = float(input("Temperature in Fahrenheit: "))
celsius = (fahrenheit - 32) * 5 / 9
print(f"{fahrenheit} F is {round(celsius, 1)} C")
```
`float(input(...))` is required — without it, subtracting `32` from a string raises `TypeError`.
Note that `5 / 9` is `0.555...`, a float; writing `5 // 9` would give `0` and zero out every
result.
:::

:::solution Exercise 4
```python
start = int(input("Start hour (0-23): "))
add = int(input("Hours to add: "))

end = (start + add) % 24
print(f"{start}:00 plus {add} hours is {end}:00")
```
`%` wraps the value back into `0..23`, so `22 + 5` gives `3` rather than `27`. The same trick
handles negative durations: `22 - 25` becomes `21`.
:::

:::solution Exercise 5
```python
TAX_RATE = 0.085

item = input("Item: ")
price = float(input("Unit price: "))
quantity = int(input("Quantity: "))

subtotal = price * quantity
tax = subtotal * TAX_RATE
total = subtotal + tax

print(f"{quantity} x {item}")
print(f"  subtotal {round(subtotal, 2)}")
print(f"  tax      {round(tax, 2)}")
print(f"  total    {round(total, 2)}")
```
Keeping `TAX_RATE` as a single named value in caps means a rate change is one edit, not a hunt
through the file. If you round each line independently the printed numbers may not add up exactly;
real invoices round once, at the end, which Chapter 17 revisits with `decimal`.
:::
