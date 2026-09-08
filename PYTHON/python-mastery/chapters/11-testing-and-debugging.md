---
chapter: 11
part: 2
title: Testing & Debugging
summary: Write tests that let you refactor without fear, and track down bugs with pdb, bisection, and a profiler instead of guesswork.
minutes: 45
tags: [pytest, fixtures, mocks, debugging, pdb, profiling]
---

You changed one line and three unrelated things broke. You are now afraid to touch the file. That
fear is the entire reason tests exist — not to prove code is correct, but to let you *change* it.
A test suite is a machine that answers "did I break anything?" in seconds, so you can refactor the
ugly function, upgrade a dependency, or add a feature without holding your breath. This chapter
pairs that with the other half of the job: when something is broken and there is no test to catch
it, finding the cause by method rather than by luck.

## Setting up pytest

`unittest` ships with Python, but `pytest` is what the ecosystem actually uses: plain functions,
plain `assert`, no boilerplate classes. Install it into a virtual environment (Chapter 10):

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pytest
```

Here is the code we will test. Two modules in one folder:

```python
# pricing.py
def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError(f"percent must be between 0 and 100, got {percent}")
    return round(price * (1 - percent / 100), 2)


def format_money(amount):
    return f"${amount:,.2f}"


def bulk_total(unit_price, quantity, percent=0):
    if quantity < 0:
        raise ValueError("quantity cannot be negative")
    return format_money(apply_discount(unit_price * quantity, percent))


def write_report(path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
```

```python
# billing.py
import datetime


def days_overdue(due_date):
    """Return how many days past due `due_date` is, or 0 if it is not overdue."""
    delta = (datetime.date.today() - due_date).days
    return max(0, delta)
```

## Your first test

```python
# test_pricing.py
import pytest

from pricing import apply_discount, bulk_total, format_money


def test_no_discount_returns_original_price():
    assert apply_discount(100, 0) == 100


def test_half_price_discount():
    assert apply_discount(100, 50) == 50


def test_format_money_adds_thousands_separator():
    assert format_money(1234.5) == "$1,234.50"
```

```bash
pytest -v
```

```text
========================= test session starts ==========================
collected 3 items

test_pricing.py::test_no_discount_returns_original_price PASSED    [ 33%]
test_pricing.py::test_half_price_discount PASSED                   [ 67%]
test_pricing.py::test_format_money_adds_thousands_separator PASSED [100%]

========================== 3 passed in 0.03s ===========================
```

Three rules, and pytest found the file by following all three:

1. Files are named `test_*.py` or `*_test.py`.
2. Functions are named `test_*`.
3. Tests use plain `assert`. No `self.assertEqual`.

That is the whole convention. Run `pytest` with no arguments from the project root and it walks
the tree looking for those files.

## Reading a failure

Make one test wrong on purpose — forget that `bulk_total` returns a formatted string and compare
it to a number:

```python
def test_bulk_total_with_discount():
    assert bulk_total(10, 3, 20) == 24.00
```

```text
    def test_bulk_total_with_discount():
>       assert bulk_total(10, 3, 20) == 24.00
E       AssertionError: assert '$24.00' == 24.0
E         +  where '$24.00' = bulk_total(10, 3, 20)
E         -24.0
E         +'$24.00'
```

Three useful things in eight lines: the value the function actually returned, the value you
expected, and the fact that they are different *types*. pytest rewrote the `assert` to show all of
it — you get that for free on any comparison, no message required.

Add a message when the default output is not self-explanatory, for example inside a loop or when
the values are large blobs:

```python
def test_bulk_total_with_discount():
    result = bulk_total(10, 3, 20)
    assert result == "$24.00", f"expected '$24.00', got {result!r}"
```

`{result!r}` uses `repr()`, which shows quotes, trailing spaces, and type. A bare `assert` tells
you something is wrong; a message tells you *what*.

## Arrange, Act, Assert

Structure every test in three moves:

```python
def test_bulk_total_with_discount():
    # Arrange — set up the inputs
    unit_price = 10
    quantity = 3
    percent = 20

    # Act — do the one thing under test
    result = bulk_total(unit_price, quantity, percent)

    # Assert — check the outcome
    assert result == "$24.00"
```

One `Act` per test. If a test has two actions, split it. This is what makes a failing test name
useful: `test_bulk_total_with_discount` failed, therefore bulk totals with discounts are broken,
full stop.

## Parametrize instead of copy-paste

You want `apply_discount` checked against a table of inputs. Do not write eight near-identical
functions:

```python
@pytest.mark.parametrize(
    "price, percent, expected",
    [
        (100, 0, 100),
        (100, 50, 50),
        (80, 25, 60),
        (9.99, 10, 8.99),
        (0, 100, 0),
    ],
)
def test_apply_discount(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

```text
test_pricing.py::test_apply_discount[100-0-100] PASSED   [ 20%]
test_pricing.py::test_apply_discount[100-50-50] PASSED   [ 40%]
test_pricing.py::test_apply_discount[80-25-60] PASSED    [ 60%]
test_pricing.py::test_apply_discount[9.99-10-8.99] PASSED [ 80%]
test_pricing.py::test_apply_discount[0-100-0] PASSED     [100%]
```

Each row becomes an independent test with its own ID. When one fails, the ID tells you exactly
which row: `test_apply_discount[9.99-10-8.99]`. Add a `pytest.param(..., id="name")` when the
auto-generated ID is unreadable.

## Testing that something raises

Validation is behaviour. Test it like behaviour:

```python
def test_negative_percent_raises():
    with pytest.raises(ValueError):
        apply_discount(100, -5)


def test_negative_percent_mentions_the_rule():
    with pytest.raises(ValueError, match="percent must be between"):
        apply_discount(100, 150)
```

`pytest.raises` fails if the exception does *not* happen, which is the point — a validation check
that silently stopped validating is a bug. `match` takes a regular expression (Chapter 17) and
asserts on the message, so you catch "wrong exception, right type".

## Grouping tests with classes

Classes are optional. They are useful for grouping tests that share a fixture, and for readable
IDs:

```python
class TestBulkTotal:
    def test_single_item_no_discount(self):
        assert bulk_total(5, 1) == "$5.00"

    def test_quantity_discount(self):
        assert bulk_total(5, 10, 10) == "$45.00"

    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError, match="negative"):
            bulk_total(5, -1)
```

Name them `Test*` and never give them an `__init__` — pytest instantiates them itself.

## Fixtures

A fixture is a named piece of setup. Ask for it as an argument, and pytest supplies it:

```python
import pytest


@pytest.fixture
def cart():
    return [
        {"sku": "widget", "quantity": 3, "unit_price": 2.50},
        {"sku": "gizmo", "quantity": 1, "unit_price": 10.00},
    ]


def test_empty_cart_has_no_total(cart):
    cart.clear()
    assert cart == []


def test_cart_line_count(cart):
    assert len(cart) == 2
```

The important part: each test gets a **fresh** `cart`. `test_empty_cart_has_no_total` clears its
own copy, so `test_cart_line_count` is unaffected — no matter which order pytest runs them in.
That isolation is why fixtures exist, and it is the opposite of the module-level global you were
about to write.

Fixtures can build on fixtures:

```python
@pytest.fixture
def order(cart):
    return {"customer": "acme", "lines": cart}
```

### Scope

By default a fixture is rebuilt for every test. When setup is expensive — reading a large file,
starting a database — rebuild it once:

```python
@pytest.fixture(scope="module")
def catalog():
    import json
    from pathlib import Path

    return json.loads(Path("tests/data/catalog.json").read_text())
```

Scopes, cheapest to most persistent: `function` (default), `class`, `module`, `package`,
`session`. Wider scope means faster tests and more risk of one test leaking state into another.
Default to `function` and widen only when you have measured that setup is the slow part.

### `tmp_path`

`tmp_path` is a built-in fixture giving each test a private temporary directory as a `pathlib.Path`.
This is how you test code that writes files:

```python
def test_write_report_creates_file(tmp_path):
    out = tmp_path / "report.txt"

    write_report(out, ["alpha", "beta"])

    assert out.exists()
    assert out.read_text(encoding="utf-8") == "alpha\nbeta\n"


def test_write_report_never_touches_the_real_folder(tmp_path):
    out = tmp_path / "nested" / "report.txt"
    out.parent.mkdir(parents=True)

    write_report(out, ["one"])

    assert (tmp_path / "nested" / "report.txt").read_text() == "one\n"
```

No cleanup code, no `finally`, no risk of overwriting something real. Never write test output into
the repository — a test that leaves files behind will eventually fail someone else's build.

## Monkeypatching

`billing.days_overdue` calls `datetime.date.today()`. Left alone, that makes your test correct
today and wrong tomorrow. Replace the dependency at runtime:

```python
import datetime

import billing


class FakeDate(datetime.date):
    @classmethod
    def today(cls):
        return datetime.date(2026, 3, 1)


def test_days_overdue_counts_days(monkeypatch):
    monkeypatch.setattr(billing, "date", FakeDate)

    assert billing.days_overdue(datetime.date(2026, 2, 20)) == 9


def test_days_overdue_is_zero_when_not_due(monkeypatch):
    monkeypatch.setattr(billing, "date", FakeDate)

    assert billing.days_overdue(datetime.date(2026, 4, 1)) == 0
```

`monkeypatch.setattr` replaces the name `date` inside the `billing` module for the duration of the
test, then puts it back — automatically, even if the test fails. We patch the name *where it is
used* (`billing.date`), not where it is defined (`datetime.date`); patching the latter would
change today's date for every module in the process.

`monkeypatch` also handles environment variables (`monkeypatch.setenv`), dict entries
(`monkeypatch.setitem`), and the current directory (`monkeypatch.chdir`).

## Running only what you need

```bash
pytest -k "discount"        # run tests whose name matches the expression
pytest -k "bulk and not raises"
pytest -x                   # stop at the first failure
pytest --lf                 # rerun only the tests that failed last time
pytest -q                   # quiet: dots instead of verbose lines
pytest --lf -x              # the loop you will use all day: fix, rerun failures
pytest tests/test_billing.py::test_days_overdue_counts_days
```

`--lf` (last failed) is the biggest quality-of-life flag in the tool. Fix a bug, run
`pytest --lf -x`, repeat until clean, then run the full suite once.

## Coverage

Coverage tells you which lines your tests *executed*. It does not tell you which lines were
checked.

```bash
python3 -m pip install pytest-cov
pytest --cov=pricing --cov=billing --cov-report=term-missing
```

```text
Name        Stmts   Miss  Cover   Missing
-----------------------------------------
pricing.py     16      2    88%   14, 21
billing.py      5      0   100%
-----------------------------------------
TOTAL          21      2    90%
```

Lines 14 and 21 are the two `raise` statements nobody tested. Coverage found them; it is now your
job to decide whether they matter. Chasing 100% is usually waste — but an untested `raise` and an
untested `except` are exactly the lines that break in production, so they are worth the five
minutes.

## What not to test

- **The standard library.** Do not assert that `sorted()` sorts.
- **Third-party packages.** `requests` has its own tests. Test *your* code around it.
- **Private implementation details.** If `apply_discount` stops calling `round()` internally and
  your test breaks, your test was wrong.
- **Trivial pass-throughs.** A one-line getter, a dataclass field assignment (Chapter 13).
- **Exact strings meant for humans**, unless a contract depends on them — otherwise every copy
  edit breaks the build.
- **Anything that needs the network, the real clock, or a real database.** Isolate them with
  fixtures and `monkeypatch`.

Test the behaviour you promised: the interesting branches, the boundary values (0, negative,
empty, one, huge), and every bug you have ever fixed — a regression test is how that bug stays
fixed.

## Debugging

### `breakpoint()`

Put `breakpoint()` where you want the program to stop, then run it normally. Execution halts and
drops you into **pdb**.

```python
def average(values):
    total = 0
    for value in values:
        breakpoint()
        total += value
    return total / len(values)


print(average([1, 2, "3"]))
```

```text
> /Users/you/demo.py(4)average()
-> total += value
(Pdb) p value
1
(Pdb) p total
0
(Pdb) c
> /Users/you/demo.py(4)average()
-> total += value
(Pdb) p value
2
(Pdb) n
> /Users/you/demo.py(3)average()
-> for value in values:
(Pdb) p value
'3'
```

There is the bug: `value` is the string `'3'`. Commands you will use 95% of the time:

| Command | Meaning |
| --- | --- |
| `n` | next line — execute this line, step *over* function calls |
| `s` | step — execute this line, step *into* a function call |
| `c` | continue running until the next breakpoint or the end |
| `l` | list the source around the current line |
| `p expr` | print the value of an expression (`pp` for pretty-print) |
| `q` | quit immediately and abort the program |

Also worth knowing: `w` prints the call stack (where you are and how you got there), `u`/`d` move
up and down that stack, and `interact` drops you into a normal Python prompt with all local
variables available.

`breakpoint()` is a standard function in Python 3.7+, so you never need `import pdb`. To disable
every breakpoint at once without editing files: `PYTHONBREAKPOINT=0 python3 app.py`.

### The narrow-it-down method

Guessing is the slow way. Do this instead:

1. **Read the traceback bottom-up** (Chapter 1). The last line is the error; the line above is
   where it happened. Do not skip to "what do I think is wrong?".
2. **Get a failing case you can rerun in one keystroke.** If the bug needs eleven clicks to
   reproduce, you will debug it eleven times an hour.
3. **Shrink it.** Delete half the input. Does it still fail? Delete half the code. A bug you can
   reproduce in five lines is a bug you understand.
4. **State your assumption, then check it.** "This list should have three items." `p len(items)`.
   Half of debugging is discovering that the thing you were certain of is false.

### Bisecting with prints

When a debugger is awkward — a loop over a million rows, a failing request in a server — insert a
print at the midpoint of the process and at the two endpoints. If the data is right at the middle
and wrong at the end, the bug is in the second half. Repeat. Ten prints find the fault line in a
million-line run in about twenty passes, and unlike staring, it always terminates.

```python
def process(rows):
    for i, row in enumerate(rows):
        result = transform(row)
        if i % 1000 == 0:
            print(f"[checkpoint {i}] {result!r}")
        save(result)
```

Delete the prints when you are done. Better: turn the failing case into a test (above), and the
print statements become unnecessary next time.

### Rubber-duck debugging

Explain the code out loud, line by line, to someone who does not know the codebase — a colleague,
or an inanimate object. Say what each line is *supposed* to do. You will get two sentences in and
hear yourself say "…and then it writes the total, wait, no, that's the subtotal." The explanation
forces you to read the code instead of your memory of it. It works because your mental model and
the actual code differ somewhere, and speaking is a way to diff them.

## When it is slow rather than wrong

Never guess where the time goes. Measure.

```bash
python3 -m timeit "'-'.join(str(n) for n in range(100))"
python3 -m timeit "'-'.join([str(n) for n in range(100)])"
```

```text
20000 loops, best of 5: 12.4 usec per loop
20000 loops, best of 5: 11.1 usec per loop
```

`timeit` runs the snippet thousands of times and reports the best result, which cancels out noise
from other programs on your machine. Use it for micro-questions: which of these two expressions is
faster?

For "why does my script take 30 seconds?", profile it:

```bash
python3 -m cProfile -s cumtime report.py
```

```text
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.004    0.004   28.412   28.412 report.py:1(<module>)
      500   26.980    0.054   26.980    0.054 report.py:14(fetch_row)
        1    0.002    0.002    1.401    1.401 report.py:41(write_output)
```

Read `tottime` (time spent in the function itself, excluding its calls) to find the hot spot.
Here it is `fetch_row` with 500 calls — a classic sign you should batch the work instead of
calling one at a time. You can also profile a single function from code:

```python
import cProfile

cProfile.run("build_report()", sort="tottime")
```

Optimise only what the profiler points at, and re-measure afterwards. Intuition about performance
is wrong often enough that skipping the measurement is itself a bug.

:::scenario You are asked to add a feature to a 1,800-line module with no tests
The file is `legacy_invoice.py`. It was written by someone who left the company. It has no tests,
and the ticket says "add a 5% loyalty discount for repeat customers, but don't break anything."
Every change you make could quietly break billing for thousands of customers, and you have no way
to know.
:::

:::solution Pin the current behaviour with characterisation tests, then refactor
You do not know what the code is *supposed* to do, but you know exactly what it *does*. Freeze
that before touching anything.

1. **Write characterisation tests.** Feed the module real inputs and record the real outputs,
   including the ones that look wrong. The test asserts current behaviour, not desired behaviour.
   ```python
   def test_invoice_total_for_known_order():
       order = load_fixture("orders/2026-01-14-acme.json")
       assert invoice_total(order) == Decimal("1487.20")
   ```
2. **Cover the branches.** Run `pytest --cov=legacy_invoice --cov-report=term-missing` and write
   tests for the reachable lines you missed, especially the `except` blocks and validation.
3. **Now refactor.** Extract functions, rename variables, split the file into a package
   (Chapter 10). After every small step, run the suite. Green means you changed the shape without
   changing behaviour.
4. **Add the feature last**, with its own tests, including the boundary cases: first order,
   exactly 5%, customer with two currencies.
5. **Leave the tests behind.** They are now the safety net the next person does not have to build
   from scratch.

If a test fails in step 1 and the output looks wrong, do not silently "fix" the expected value.
Find out whether anything depends on that behaviour first. A characterisation test that encodes a
bug is still valuable — it tells you the bug exists and gives you a place to document the fix.
:::

:::pitfall Tests that depend on each other, or on today's date
```python
CURRENT_USER = None

def test_create_user():
    global CURRENT_USER
    CURRENT_USER = create_user("ada")
    assert CURRENT_USER.active

def test_deactivate_user():
    assert deactivate(CURRENT_USER) is True   # depends on the test above
```
This passes on your machine because pytest runs the file top to bottom. It fails the moment
someone runs `pytest -k deactivate`, runs the file in isolation, shards tests across CI workers,
or installs a plugin that randomises order. The second test reports an error that has nothing to
do with what is broken.

The clock is the same bug wearing a hat:
```python
def test_report_is_not_overdue():
    assert days_overdue(date(2026, 9, 20)) == 0     # passes until Sept 20
def test_promo_is_active():
    assert promo_active()                            # fine in Q3, fails in Q4
```
These are *time bombs*: green for months, red on a Monday morning with no related code change. CI
in Chapter 22 will fail and everyone will blame the last commit.

Fix both the same way — make each test set up its own world:

```python
@pytest.fixture
def user():
    return create_user("ada")

def test_create_user(user):
    assert user.active

def test_deactivate_user(user):
    assert deactivate(user) is True
```

and freeze the clock with `monkeypatch` instead of reading the real one. A test that cannot be run
alone, in any order, at any time, is not a test — it is a coincidence.
:::

## Key takeaways

- Tests exist so you can change code without fear; they are a tool for refactoring, not a
  certificate of correctness.
- pytest collects files named `test_*.py` and functions named `test_*`, and uses plain `assert`.
- Structure tests as Arrange, Act, Assert — one action per test.
- Use `@pytest.mark.parametrize` for input tables and `pytest.raises` for expected exceptions.
- Fixtures provide fresh, isolated setup per test; `tmp_path` gives you a private temp directory;
  `monkeypatch` swaps out dependencies like the clock.
- `pytest -k`, `-x`, and `--lf` let you run exactly the tests you care about.
- Coverage shows which lines ran, not which were right — use it to find untested branches.
- Debug with `breakpoint()` and pdb (`n`, `s`, `c`, `l`, `p`, `q`), by shrinking the failing case,
  and by measuring with `timeit`/`cProfile` instead of guessing.

## Practice

- [ ] Install pytest in a venv and run the three `test_pricing.py` tests from this chapter.
      Confirm you can make one fail on purpose.
- [ ] Write tests for `apply_discount` covering 0%, 100%, and the two `ValueError` paths. Use
      `@pytest.mark.parametrize` for the values and `pytest.raises` for the errors.
- [ ] Write a test for `write_report` using `tmp_path` that asserts the file contents, the trailing
      newline, and that an empty list produces a file containing only `"\n"`.
- [ ] Add a fixture that builds a temporary catalog file in `tmp_path`, then write a test that
      reads it back. Give the fixture `scope="module"` and explain in a comment what you trade
      away.
- [ ] `billing.days_overdue` has no tests for a due date far in the future. Add one with
      `monkeypatch`, then remove the patch and confirm the test becomes time-dependent.
- [ ] Debug `moving_average(values, window)` with `breakpoint()` and fix it without rewriting it: the loop is `for i in range(len(values)):` and each result is `sum(values[i:i + window]) / window`. It returns the wrong values at the end of the list. Then write four tests: full windows, `window=1`, `window == len(values)`, and an empty input.

## Solutions

:::solution Exercise 1
```bash
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install pytest
pytest -v
```
Change `assert apply_discount(100, 50) == 50` to `== 51` and rerun; pytest prints the assertion
with both values and a `>` marker on the failing line. Seeing a real failure is important — a test
you have only ever watched pass is a test you do not know works.
:::

:::solution Exercise 2
```python
import pytest

from pricing import apply_discount


@pytest.mark.parametrize(
    "price, percent, expected",
    [
        (100, 0, 100),
        (100, 100, 0),
        (50, 10, 45),
        (19.99, 15, 16.99),
    ],
)
def test_apply_discount(price, percent, expected):
    assert apply_discount(price, percent) == expected


@pytest.mark.parametrize("percent", [-1, 101, 250])
def test_out_of_range_percent_raises(percent):
    with pytest.raises(ValueError, match="percent must be between"):
        apply_discount(100, percent)
```
Check `19.99 * 0.85 = 16.9915`, rounded to `16.99`. Boundary values (0 and 100) are where
off-by-one and division bugs hide, so they earn their own rows rather than being assumed.
:::

:::solution Exercise 3
```python
def test_write_report_content(tmp_path):
    out = tmp_path / "r.txt"
    write_report(out, ["alpha", "beta"])
    assert out.read_text(encoding="utf-8") == "alpha\nbeta\n"


def test_write_report_empty_list(tmp_path):
    out = tmp_path / "r.txt"
    write_report(out, [])
    assert out.read_text(encoding="utf-8") == "\n"


def test_write_report_overwrites(tmp_path):
    out = tmp_path / "r.txt"
    write_report(out, ["one", "two", "three"])
    write_report(out, ["four"])
    assert out.read_text(encoding="utf-8") == "four\n"
```
The empty-list case is genuinely surprising — `"\n".join([]) + "\n"` is `"\n"`, not `""` — and
that is exactly the kind of behaviour a test should pin down so nobody "fixes" it accidentally.
:::

:::solution Exercise 4
```python
import pytest


@pytest.fixture(scope="module")
def catalog_file(tmp_path_factory):
    # scope="module" means one file for every test in this module. Faster, but
    # a test that modifies the file would affect the tests that run after it.
    directory = tmp_path_factory.mktemp("data")
    path = directory / "catalog.csv"
    path.write_text("sku,price\nwidget,2.50\ngizmo,10.00\n", encoding="utf-8")
    return path


def test_catalog_has_header(catalog_file):
    assert catalog_file.read_text(encoding="utf-8").startswith("sku,price")


def test_catalog_row_count(catalog_file):
    lines = catalog_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
```
`tmp_path` is function-scoped, so a module-scoped fixture cannot use it — hence
`tmp_path_factory`, which creates directories at any scope. The tradeoff: fewer file writes, but
shared mutable state across tests in the module.
:::

:::solution Exercise 5
```python
import datetime

import billing


class FakeDate(datetime.date):
    @classmethod
    def today(cls):
        return datetime.date(2026, 3, 1)


def test_far_future_due_date_is_never_overdue(monkeypatch):
    monkeypatch.setattr(billing, "date", FakeDate)
    assert billing.days_overdue(datetime.date(2030, 1, 1)) == 0


def test_without_patch_this_breaks_on_2030_01_01():
    assert billing.days_overdue(datetime.date(2030, 1, 1)) == 0   # time bomb
```
The second test uses the real clock. It passes today and fails on 1 January 2030, with no code
change involved. Patching `billing.date` rather than `datetime.date.today` keeps the change
local to one module and is undone automatically when the test ends.
:::

:::solution Exercise 6
```python
def moving_average(values, window):
    result = []
    for i in range(len(values) - window + 1):
        chunk = values[i:i + window]
        result.append(sum(chunk) / window)
    return result
```
The loop ran over *every* index, including the tail where `values[i:i + window]` is shorter than
`window` — so the last few entries divided a partial sum by the full window size and came out too
small. Stopping at `len(values) - window + 1` keeps every chunk full. You find this in pdb with
`p chunk, window` at the last iteration, or by printing `i` and `len(chunk)`.

```python
def test_full_windows_only():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


def test_window_of_one():
    assert moving_average([5, 10], 1) == [5.0, 10.0]


def test_window_equal_to_length():
    assert moving_average([2, 4, 6], 3) == [4.0]


def test_empty_input():
    assert moving_average([], 3) == []
```
`test_empty_input` is the one worth keeping: `range(len([]) - 3 + 1)` is `range(-2)`, which is
empty — correct by accident, but once it is a test, it stays correct.
:::
