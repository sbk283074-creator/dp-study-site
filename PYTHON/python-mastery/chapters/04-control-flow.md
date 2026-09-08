---
chapter: 4
part: 1
title: Control Flow
summary: Make decisions, dispatch on values, and write loops that terminate — including the input-validation loop you will use in every script from here to Chapter 39.
minutes: 35
tags: [if/else, boolean logic, match, while loops, validation]
---

A program that executes top to bottom with no branches is a calculator. Everything interesting —
validating a form, retrying a failed request, running a game loop, routing an HTTP request in
Chapter 27 — is control flow: choosing a path, repeating work, and bailing out when something is
wrong. This chapter covers the decisions, Chapter 7 covers iteration over collections, and the two
together are most of what programming *is*.

## Comparisons

Six operators produce a `bool`:

| Operator | Meaning | Example |
| --- | --- | --- |
| `==` | equal by value | `3 == 3.0` → `True` |
| `!=` | not equal | `"a" != "b"` → `True` |
| `<` `<=` | less than (or equal) | `2 <= 2` → `True` |
| `>` `>=` | greater than (or equal) | `10 > 9` → `True` |
| `is` | same object | `x is None` |
| `in` | membership | `"py" in "python"` → `True` |

Note `3 == 3.0` is `True` — Python compares numeric values across types rather than refusing.

Python also lets you **chain** comparisons the way you would write them in maths:

```python
>>> age = 30
>>> 18 <= age < 65
True
```

That is two comparisons with an implicit `and`, evaluated left to right. Write `0 <= x <= 100`,
not `x >= 0 and x <= 100`.

## `if`, `elif`, `else`

The shape is fixed: one `if`, any number of `elif` ("else if"), at most one `else`. Python runs
the first block whose condition is true and skips the rest.

```python
weight = float(input("Package weight (kg): "))

if weight <= 0:
    print("Weight must be positive.")
elif weight <= 1:
    print("Post: 3.50")
elif weight <= 5:
    print("Parcel: 7.90")
elif weight <= 20:
    print("Freight: 18.00")
else:
    print("Too heavy — call for a quote.")
```

Order matters: the conditions are tested top to bottom, so `weight <= 1` is only reached when
`weight > 0`. Get the order wrong and the cheap branch swallows everything.

Indentation is not style, it is syntax. Four spaces per level, and a block ends when the
indentation returns to the previous level. Tabs and spaces mixed in one file is a `TabError`.

## Truthiness in conditions

You almost never need a comparison to make a `bool`. Python evaluates the value directly (Chapter 2's
truthiness table), so write what you mean:

```python
name = input("Name: ")

if name:                       # good
    print(f"Hello, {name}")

if len(name) > 0:              # noisy, equivalent
    print(f"Hello, {name}")
```

The same applies to `if not items:` for an empty collection and `if result is None:` when `None`
specifically means "missing" rather than "empty" — those are different states, and conflating them
is a real bug.

## `and`, `or`, `not`

```python
if age >= 18 and has_ticket:
    print("Come in")

if day == "saturday" or day == "sunday":
    print("Weekend")

if not logged_in:
    print("Please sign in")
```

Both `and` and `or` **short-circuit**: they stop evaluating as soon as the answer is known. `and`
stops at the first falsey operand; `or` stops at the first truthy one. That is not a curiosity —
it is how you write safe guards:

```python
>>> total, count = 10, 0
>>> if count != 0 and total / count > 2:
...     print("above target")
... else:
...     print("cannot average zero items")
cannot average zero items
```

Without short-circuiting the second line would raise `ZeroDivisionError`. The same trick protects
indexing: `if items and items[0] == "admin"`.

`or` has a second life as a default-value operator, because it returns the *value* that decided the
outcome, not a `bool`:

```python
>>> name = input("Name (blank for Anonymous): ").strip() or "Anonymous"
```

If the input is empty, `or` yields `"Anonymous"`. Neat, but it also swallows `0` and `0.0`; when
`0` is legitimate, use an explicit `if` instead.

## Guard clauses beat nesting

Deeply nested `if`s are hard to read and harder to change. Handle the exceptional cases first and
return early; the happy path ends up flat at the bottom. Here is the nested version:

```python
def shipping_cost_nested(weight, express):
    if weight > 0:
        if weight <= 20:
            cost = 4.99 + weight * 0.5
            if express:
                cost += 9.99
            return cost
        else:
            return None
    else:
        return 0.0
```

And the same logic with guard clauses (functions are Chapter 5's subject; you already met `def`
in Chapter 1's traceback):

```python
def shipping_cost(weight, express):
    if weight <= 0:
        return 0.0
    if weight > 20:
        return None          # cannot ship: caller must handle this

    cost = 4.99 + weight * 0.5
    if express:
        cost += 9.99
    return cost
```

Same behaviour, three fewer indentation levels, and each rule reads as a statement about the
world: "nothing weighs nothing", "over 20 kg is unshippable". When you find yourself four levels
deep, you are missing a guard clause.

## Conditional expressions

When a whole `if`/`else` only picks between two values, use the one-line form:

```python
status = "adult" if age >= 18 else "minor"
label = f"{count} item" + ("" if count == 1 else "s")
```

Read it as `value_if_true if condition else value_if_false`. Use it for simple choices; if the
expression needs parentheses to be understood, use a real `if`. Never nest two of them on one
line.

## `match` / `case`

Python 3.10 added structural pattern matching. When you are dispatching on the *shape* of a value
rather than a range of numbers, it beats a long `elif` chain:

```python
command = input("> ").strip().lower()
parts = command.split()

match parts:
    case []:
        print("Type a command, or 'help'.")
    case ["quit" | "exit" | "q"]:
        print("Bye.")
    case ["add", *items] if items:
        print(f"Adding {len(items)} item(s): {', '.join(items)}")
    case ["add"]:
        print("Usage: add <item>...")
    case [verb, *args]:
        print(f"Unknown command {verb!r}.")
```

```text
> add milk eggs bread
Adding 3 item(s): milk, eggs, bread
```

The pattern forms, in the order you will use them:

| Pattern | Matches |
| --- | --- |
| `case 42:` | A literal value |
| `case "quit" \| "exit":` | Either literal (`\|` = or-pattern) |
| `case [verb, *args]:` | A sequence; `*` captures the rest |
| `case name:` | Anything — and binds it to `name` |
| `case _:` | Anything — wildcard, no binding (must be last) |
| `case [verb] if verb.isalpha():` | Only when the guard is true |

Two rules: `_` must come last or nothing below it runs, and a bare name like `case status:` is a
*capture*, not a variable read — it matches everything and assigns to it. That trips people who
expect `case ERROR_CODE:` to compare against a constant; use a dotted name like
`case Status.ERROR:` if you need that (Chapter 13).

Guards (`if` after the pattern) handle the cases patterns cannot express, like ranges or
cross-field checks:

```python
match command.split():
    case ["delay", minutes] if minutes.isdigit() and int(minutes) > 0:
        print(f"Delaying {minutes} minutes.")
    case ["delay", _]:
        print("Usage: delay <positive minutes>")
```

**When to prefer `elif`:** numeric ranges. `case int() if score >= 90:` is worse than
`if score >= 90:`. Reach for `match` when you are branching on discrete values, tags, or the
structure of parsed data — the command dispatchers in Chapter 20 and the message routers in
Chapter 28 are exactly this.

## `while` loops

`while` repeats as long as its condition stays true:

```python
countdown = 5
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Liftoff")
```

Three things must be true of every `while` loop: the condition starts true (or the body never
runs), something inside the body eventually makes it false, and the thing that changes it is
actually reached.

`break` exits the loop immediately; `continue` skips to the next iteration:

```python
while True:
    line = input("log line (blank to stop): ")
    if not line:
        break                      # exit
    if line.startswith("#"):
        continue                   # skip comments
    print(f"stored: {line}")
print("done")
```

`while True:` with a `break` is idiomatic Python for "loop until something happens" — the
condition is in the middle of the body where it belongs, rather than duplicated at the top. It is
also the shape of every game loop in Chapters 31–36.

### The `else` clause on loops

`while` and `for` accept an `else` block that runs **only if the loop finished without hitting
`break`**. It is the clean way to express "searched and found nothing":

```python
attempts = 3
while attempts > 0:
    if input("Password: ") == "hunter2":
        print("Welcome back.")
        break
    attempts -= 1
    print(f"{attempts} attempts left")
else:
    print("Account locked.")
```

### Infinite loops

A loop whose condition never changes will run forever. Press `Ctrl-C` (`Ctrl-Break` on some
Windows terminals) to interrupt it — Python raises `KeyboardInterrupt` and shows you the line it
was stuck on, which is usually enough to spot the missing `attempts -= 1`. If `Ctrl-C` is not
enough, close the terminal. There is no shame in this; it happens to everyone.

### The input-validation loop

This pattern appears in nearly every script that talks to a human, so learn it now:

```python
while True:
    raw = input("How many seats? (1-8): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= 8:
        seats = int(raw)
        break
    print("Please enter a whole number from 1 to 8.")
```

The shape is always the same: ask, validate, `break` on success, explain the failure and loop.
`isdigit()` guards the `int()` call so it cannot raise, and the range check happens after
conversion. Chapter 9 replaces this with `try`/`except`, which handles decimals and signs too.

## `pass` as a placeholder

`pass` does nothing. It exists because Python needs a statement inside a block, and "nothing" is
not allowed:

```python
if command == "skip":
    pass        # TODO: implement skipping in the next sprint
else:
    run(command)
```

Use it to sketch structure or to explicitly ignore a case you have considered. Unlike a comment
alone, `pass` is a real statement, so the block is syntactically valid.

## EAFP vs LBYL, briefly

Two philosophies for handling "might not work":

```python
# LBYL — Look Before You Leap
if "email" in record and record["email"]:
    send(record["email"])

# EAFP — Easier to Ask Forgiveness than Permission
try:
    send(record["email"])
except KeyError:
    print("no email on record")
```

Python culture leans EAFP: it avoids race conditions and reads better when the happy path is the
common one. Chapter 9 gives both the full treatment.

:::scenario The weekend-only maintenance job ran on a Wednesday
A cron job is supposed to run heavy maintenance only at the weekend. Someone writes
`if day == "Sat" or "Sun":` to guard it. It runs every single day, deletes three days of data
before anyone notices, and the post-mortem is uncomfortable.
:::

:::solution `"Sun"` is a truthy value, so the condition is always true
The expression does not say what its author meant. `or` takes two complete conditions, and a
non-empty string on its own is truthy:

```python
>>> day = "Wed"
>>> day == "Sat" or "Sun"          # parsed as (day == "Sat") or ("Sun")
'Sun'
>>> bool(day == "Sat" or "Sun")
True
```

It does not even return a `bool` — it returns the string `"Sun"`, which `if` then treats as true.
Three correct spellings:

```python
if day == "Sat" or day == "Sun":        # correct but repetitive
    ...
if day in ("Sat", "Sun"):               # idiomatic
    ...
if day in {"Sat", "Sun"}:               # set: fastest membership test (Chapter 6)
    ...
```

Prefer the membership form; it scales to ten values without turning into a wall of `or`.

The deeper lesson is about defensive habits: **a condition you cannot read is a condition you
cannot verify.** Test the guard before you deploy the thing it guards, with at least one value
that should pass and one that should fail. Chapter 11 turns that instinct into automated tests, and
this is exactly the class of bug a single `assert shipping_runs_on("Wed") is False` would have
caught in a second.
:::

:::pitfall Conditions that say nothing, and loops that never end
Three mistakes show up constantly in code review.

**1. Comparing against `True` or `False`.**

```python
if flag == True:      # no
    ...
if flag:              # yes
    ...
if flag is True:      # only if you must reject 1 and "yes"
    ...
```

`== True` is redundant at best and wrong at worst: it is false for `1`, `"yes"`, and other
truthy values you probably wanted to accept.

**2. Measuring emptiness instead of testing it.**

```python
if len(name) > 0:     # no
    ...
if name:              # yes
    ...
if items != []:       # no
    ...
if items:             # yes
    ...
```

One exception: when `None` and empty mean different things, say so explicitly with
`if name is not None:`.

**3. A `while` loop that never advances its condition.**

```python
n = 0
while n < 5:
    print(n)
    # n += 1  <-- commented out during debugging
```

Or worse, the increment exists but `continue` jumps over it:

```python
n = 0
while n < 5:
    if n == 2:
        continue          # n never changes → hangs forever
    n += 1
```

When a `while` loop hangs, look for the variable in the condition and trace every path through
the body. If a `continue` can skip the update, move the update above it or restructure as
`while True:` with an explicit `break`.
:::

## Key takeaways

- Comparison operators return `bool`; chain them (`18 <= age < 65`) instead of using `and`.
- `and` and `or` short-circuit, which makes guards like `if count and total / count > 2` safe.
- Test truthiness directly (`if name:`) rather than comparing to `True` or checking `len() > 0`.
- Guard clauses — handle the edge cases and return early — flatten nested conditionals.
- `match`/`case` dispatches on discrete values and structure with `|`, `*`, `_`, and `if` guards;
  keep `elif` for numeric ranges.
- `while True:` plus `break` is the standard "loop until it works" shape, and the `else` clause on
  a loop runs only when no `break` happened.
- Every `while` loop needs a reachable path that makes its condition false.
- The validation loop — ask, check, `break`, explain, repeat — is a pattern you will write for the
  rest of your Python life.

## Practice

- [ ] In the REPL, predict then check: `bool("")`, `bool("0")`, `bool([])`, `0 == False`,
      `3 == 3.0`, `18 <= 25 < 30`, and `""` or `"fallback"`.
- [ ] Write `grade.py`: read a score from 0–100 and print a letter grade (A ≥ 90, B ≥ 80, C ≥ 70,
      D ≥ 60, else F). Reject anything outside 0–100 with a message instead of a grade.
- [ ] Write `dispatch.py`: a `match`/`case` command loop that handles `help`, `add <item...>`,
      `remove <item>`, `list`, and `quit` — with a wildcard branch for unknown commands.
- [ ] Write `guess.py`: pick a random number from 1 to 100, then loop until the user guesses it,
      printing "higher" or "lower". Cap it at seven attempts and print the answer if they run out.
- [ ] Write `calc.py`: a calculator that keeps running until the user types `quit`. Each round it
      reads two numbers (validated with the input-validation loop) and an operator
      (`+ - * /`), refuses division by zero, and prints the result.

## Solutions

:::solution Exercise 2
```python
raw = input("Score (0-100): ").strip()

if not (raw.isdigit() and 0 <= int(raw) <= 100):
    print("Enter a whole number from 0 to 100.")
else:
    score = int(raw)
    if score >= 90:
        print("A")
    elif score >= 80:
        print("B")
    elif score >= 70:
        print("C")
    elif score >= 60:
        print("D")
    else:
        print("F")
```
Validate first with a guard clause, then the grade chain can assume sane input and skip its own
`else`. Because the `elif` chain is ordered, `score >= 90` must come first — reversing it would
assign every passing score an F.
:::

:::solution Exercise 3
```python
items = []

while True:
    parts = input("> ").strip().lower().split()

    match parts:
        case []:
            continue
        case ["quit" | "exit" | "q"]:
            print("Bye.")
            break
        case ["help"]:
            print("commands: add <item>, remove <item>, list, quit")
        case ["add", *new_items] if new_items:
            items.extend(new_items)
            print(f"added: {', '.join(new_items)}")
        case ["remove", name] if name in items:
            items.remove(name)
            print(f"removed: {name}")
        case ["remove", name]:
            print(f"not in list: {name}")
        case ["list"]:
            print(", ".join(items) if items else "(empty)")
        case [verb, *rest]:
            print(f"unknown command: {verb}")

    print(f"[{len(items)} items]")
```
`match` reads top to bottom and takes the first pattern that fits, so the specific
`["remove", name] if name in items` case must precede the generic `["remove", name]`. The
`case []:` guard handles a bare Enter without crashing on an empty list.
:::

:::solution Exercise 4
```python
import random

secret = random.randint(1, 100)
attempts_left = 7

while attempts_left > 0:
    raw = input(f"Guess (1-100), {attempts_left} left: ").strip()
    if not raw.isdigit():
        print("Numbers only.")
        continue

    guess = int(raw)
    if guess == secret:
        print("Correct!")
        break
    elif guess < secret:
        print("Higher.")
    else:
        print("Lower.")

    attempts_left -= 1
else:
    print(f"Out of attempts. It was {secret}.")
```
The decrement sits at the *end* of the body so a bad guess costs an attempt but a malformed input
does not — `continue` skips back to the top before reaching it. The `else` on the `while` runs
only when the loop exhausts `attempts_left` without `break`, which is exactly the "gave up" case.
:::

:::solution Exercise 5
```python
print("tiny calculator — 'quit' to exit")

while True:
    raw = input("> ").strip().lower()
    if raw in ("quit", "exit", "q"):
        print("Bye.")
        break

    left_raw = input("first number: ").strip()
    operator = input("operator (+ - * /): ").strip()
    right_raw = input("second number: ").strip()

    if not (left_raw.isdigit() and right_raw.isdigit()):
        print("Both operands must be numbers.")
        continue

    left, right = int(left_raw), int(right_raw)

    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            print("Cannot divide by zero.")
            continue
        result = left / right
    else:
        print(f"Unknown operator: {operator}")
        continue

    print(f"= {result}")
```

Reading input as strings and converting once, at the top of each round, keeps the arithmetic
branch simple. The two `continue` statements handle the invalid cases where they happen, so the
success path stays flat at the bottom — the same guard-clause idea applied to a loop. Chapter 5
turns the operator dispatch into a dict of functions, and Chapter 9 replaces `isdigit()` with a
proper `try`/`except` so negative and decimal numbers work.
:::
