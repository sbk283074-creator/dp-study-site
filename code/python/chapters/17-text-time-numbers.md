---
chapter: 17
part: 2
title: Regex, Dates & Numbers
summary: Parse and clean real text with regular expressions, handle dates and timezones correctly, and stop losing cents to floating point.
minutes: 45
tags: [regex, datetime, zoneinfo, decimal, random, secrets]
---

Three things break programs in the field more often than anything else: text that is not quite the
shape you expected, timestamps that are in the wrong timezone, and money that is off by a cent.
None of them are hard, and all of them are embarrassing in production. Python ships solid tools
for each — the `re` module, `datetime` with `zoneinfo`, and `decimal` — and knowing where their
edges are is the difference between code that works on your sample data and code that works on
everyone's.

## Regular expressions: the right tool, and the wrong one

A regular expression is a pattern describing a set of strings. It earns its place when the shape
of your text is variable but rule-based.

Reach for regex when you need to: extract a field from loosely structured text (log lines,
filenames, user input), validate a format, or rewrite many strings with one rule.

Do **not** reach for regex when a simpler tool exists:

| Need | Use instead |
|---|---|
| Split on a fixed separator | `str.split(",")`, `str.partition("=")` |
| Check prefix, suffix, or substring | `str.startswith()`, `in` |
| Work with file paths | `pathlib` (Chapter 8) |
| Parse CSV | the `csv` module (Chapter 19) |
| Parse JSON, HTML, XML | `json`, an HTML parser — never regex |

The HTML point deserves emphasis: HTML is not a regular language, and every regex that parses it
breaks on the first nested tag. Use a parser.

### Raw strings

Regexes are full of backslashes, and backslashes in normal Python strings start escape sequences.
`"\b"` is a backspace character, not a word boundary. A **raw string** — prefix `r` — passes
backslashes through untouched:

```python
>>> len("\b")        # one character: backspace
1
>>> len(r"\b")       # two characters: backslash, b
2
>>> r"\d+\s\w+"
'\\d+\\s\\w+'
```

Always write patterns as `r"..."`. It is not optional in practice, and the bugs you get otherwise
are silent — `r"\1"` and `"\1"` are completely different strings.

### `search` vs `match` vs `fullmatch`

Every beginner trip is here, so get it straight:

```python
import re

text = "order 42 shipped"

print(re.search(r"\d+", text))        # found anywhere
print(re.match(r"\d+", text))         # anchored at position 0 only
print(re.fullmatch(r"\d+", text))     # must match the ENTIRE string
print(re.search(r"\d+", text).group())
```

```text
<re.Match object; span=(6, 8), match='42'>
None
None
42
```

- `search` — scans for the first match anywhere. Your default.
- `match` — only at the very start. Rarely what you want; `re.match(p, s)` is roughly
  `re.search(r"\A" + p, s)`.
- `fullmatch` — the whole string must match. This is the one for **validation**, because
  `search` will happily find a valid-looking substring inside garbage:
  `re.search(r"\d{5}", "abc12345xyz")` matches. `re.fullmatch(r"\d{5}", "abc12345xyz")` does not.

All three return `None` on failure. Check before you use the result:

```python
m = re.search(r"\d+", text)
if m:
    print(f"found {m.group()} at {m.start()}-{m.end()}")
```

### `findall` and `finditer`

```python
>>> re.findall(r"\d+", "a1 b22 c333")
['1', '22', '333']
>>> re.findall(r"(\w+)=(\d+)", "x=1 y=22")
[('x', '1'), ('y', '22')]
```

`findall` with groups returns tuples of groups, not whole matches. When you need positions, named
parts, or a lot of matches, use `finditer` — it yields `Match` objects lazily instead of building
a list:

```python
for m in re.finditer(r"(?P<key>\w+)=(?P<value>\d+)", "x=1 y=22"):
    print(m.group("key"), int(m.group("value")), m.span())
```

```text
x 1 (0, 3)
y 22 (4, 9)
```

### Groups and named groups

Parentheses capture. `m.group(1)` is the first, `m.group(0)` is the whole match. Numbering breaks
when someone adds a group in the middle, so name anything you will refer to more than once:
`(?P<name>...)` to define, `m.group("name")` to read.

```python
LOG = r"^(?P<ts>\S+) (?P<level>\w+) (?P<service>\S+) (?P<msg>.*)$"
m = re.match(LOG, "2026-09-07T09:02:45Z ERROR api.auth invalid token")
print(m.groupdict())
```

```text
{'ts': '2026-09-07T09:02:45Z', 'level': 'ERROR', 'service': 'api.auth', 'msg': 'invalid token'}
```

`\S+` means "one or more non-whitespace characters" and `.*` means "anything". That combination —
concrete anchors around greedy filler — is how most practical patterns are built.

### `sub`: rewriting text

```python
>>> re.sub(r"\s+", " ", "too    many     spaces")      # collapse whitespace
'too many spaces'
>>> re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2026-09-07")
'07/09/2026'
>>> re.sub(r"\b(\w+) \1\b", r"\1", "the the cat sat sat")   # \1 backreference
'the cat sat'
>>> re.sub(r"\d+", lambda m: f"[{m.group()}]", "a1 bb22")
'a[1] bb[22]'
```

The replacement can be a string (where `\1` refers to group 1) or a function — and a function is
how you do anything non-trivial, like transforming each match on the way through.

### Compiling and `re.VERBOSE`

Python caches compiled patterns, so `re.compile` is about readability and reuse, not speed. Use it
when a pattern is named and used more than once, and always with `re.VERBOSE` for anything longer
than about thirty characters:

```python
LOG_LINE = re.compile(r"""
    ^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)  # ISO-ish timestamp
    \s+(?P<level>DEBUG|INFO|WARN|ERROR)             # severity
    \s+(?P<service>[\w.]+)                          # e.g. api.auth
    \s+(?P<message>.*)$                             # the rest
""", re.VERBOSE)

line = "2026-09-07T09:02:45Z ERROR api.auth invalid token for user 42"
print(LOG_LINE.match(line).group("service", "message"))
```

```text
('api.auth', 'invalid token for user 42')
```

`re.VERBOSE` ignores whitespace and `#` comments inside the pattern, so a regex stops being a
puzzle. Other flags worth knowing: `re.IGNORECASE` (`re.I`), `re.MULTILINE` (`re.M`, makes `^`
and `$` match at line boundaries), and `re.DOTALL` (`re.S`, makes `.` match newlines).

### A pattern cookbook

| Pattern | Catches | Notes |
|---|---|---|
| `[\w.+-]+@[\w-]+\.[\w.]+` | email-shaped text | Validation only; deliverability needs a real email |
| `\d{4}-\d{2}-\d{2}` | ISO date | `fullmatch` it, then let `date.fromisoformat` verify |
| `\s+` | any run of whitespace | Replace with `" "` to normalise |
| `-?\d+(?:\.\d+)?` | an integer or decimal number | `(?:...)` is a non-capturing group |
| `\b[A-Z]{2,}\b` | ALL-CAPS words | Handy for finding acronyms in prose |
| `https?://\S+` | URLs | Stops at the first space |
| `^\s*#` | comment lines | With `re.MULTILINE`, per line |
| `\d+` | digits | `\b\d+\b` avoids matching digits inside words |
| `<[^>]+>` | an HTML tag | Fine for stripping tags; never for parsing documents |
| `\b(\w+)\s+\1\b` | accidentally repeated word | Backreference: the word appears twice |

Test every pattern against a "should not match" case as well as a "should match" one. Most broken
regexes are not too strict, they are too loose.

## Dates and times

Three types, and picking the right one saves you conversions later:

```python
from datetime import date, datetime, timedelta, timezone

launch = date(2026, 12, 1)            # a calendar day, no time
meeting = datetime(2026, 9, 7, 14, 30)   # a date plus a time
print(launch, meeting)
print(f"{(launch - date(2026, 1, 1)).days} days from New Year to launch")
```

```text
2026-12-01 2026-09-07 14:30:00
334 days from New Year to launch
```

- `date` — birthdays, deadlines, invoice dates. Use it when the time of day is meaningless.
- `datetime` — timestamps, scheduled events, anything with an hour.
- `timedelta` — a duration, the result of subtracting two dates.

Arithmetic and comparison work the way you would hope:

```python
print(meeting + timedelta(hours=1, minutes=15))
print(meeting - timedelta(days=7))
print(meeting > datetime(2026, 9, 1))
print(timedelta(hours=2, minutes=30).total_seconds())
```

```text
2026-09-07 15:45:00
2026-08-31 14:30:00
True
9000.0
```

### `strftime` and `strptime`

`strftime` formats a datetime into a string; `strptime` parses a string into a datetime. The `f`
is for *format*, the `p` for *parse*. Both use the same `%` codes:

| Code | Meaning | Example |
|---|---|---|
| `%Y` | 4-digit year | `2026` |
| `%y` | 2-digit year | `26` |
| `%m` | zero-padded month | `09` |
| `%d` | zero-padded day | `07` |
| `%H` | hour, 00–23 | `14` |
| `%I` | hour, 01–12 | `02` |
| `%p` | AM/PM | `PM` |
| `%M` | minute | `30` |
| `%S` | second | `05` |
| `%A` | full weekday | `Monday` |
| `%a` | short weekday | `Mon` |
| `%B` | full month | `September` |
| `%b` | short month | `Sep` |
| `%z` | UTC offset | `+0000` |
| `%Z` | timezone name | `UTC` |
| `%%` | a literal `%` | `%` |

```python
print(meeting.strftime("%A %d %B %Y at %H:%M"))
print(datetime.strptime("07/09/2026 14:30", "%d/%m/%Y %H:%M"))
print(meeting.isoformat())
print(datetime.fromisoformat("2026-09-07T14:30:00"))
```

```text
Monday 07 September 2026 at 14:30
2026-09-07 14:30:00
2026-09-07T14:30:00
2026-09-07 14:30:00
```

Prefer ISO 8601 (`isoformat()` / `fromisoformat()`) for anything machine-to-machine: it is
unambiguous, sorts lexicographically, and needs no format string. Note that `%d/%m/%Y` and
`%m/%d/%Y` are both plausible readings of `07/09/2026` — one of them is wrong for your users.

`strptime` raises `ValueError` when the string does not match the format, so wrap it when the
input is untrusted:

```python
try:
    when = datetime.strptime(user_input, "%Y-%m-%d")
except ValueError:
    print("expected a date like 2026-09-07")
```

### Naive vs aware, and `zoneinfo`

A datetime is **naive** if it has no timezone, and **aware** if it does. Naive means "this is
whatever wall clock the reader happens to be in", which is almost never what you want on a server.

```python
print(datetime.now())                    # naive: local wall clock — avoid in servers
print(datetime.now(timezone.utc))        # aware: the correct default
print(date.today())                      # naive is fine for a calendar date
```

```text
2026-09-07 14:30:12.881234
2026-09-07 12:30:12.881234+00:00
2026-09-07
```

:::warning `datetime.utcnow()` is deprecated
It returned a *naive* UTC datetime, which silently confused everyone who compared it to an aware
one. Use `datetime.now(timezone.utc)` and always attach the `tzinfo`.
:::

Mixing naive and aware raises rather than guessing:

```python
datetime(2026, 9, 7, 9) > datetime(2026, 9, 7, 9, tzinfo=timezone.utc)
```

```text
TypeError: can't compare offset-naive and offset-aware datetimes
```

That `TypeError` is a feature. For real timezones use `zoneinfo` (standard library since 3.9):

```python
from zoneinfo import ZoneInfo

berlin = datetime(2026, 9, 7, 9, 0, tzinfo=ZoneInfo("Europe/Berlin"))
print(berlin, "| offset:", berlin.utcoffset())
print("as UTC:", berlin.astimezone(timezone.utc))
print("as NY :", berlin.astimezone(ZoneInfo("America/New_York")))
```

```text
2026-09-07 09:00:00+02:00 | offset: 2:00:00
as UTC: 2026-09-07 07:00:00+00:00
as NY : 2026-09-07 03:00:00-04:00
```

Two rules that prevent nearly every timezone bug:

1. **Store and compute in UTC.** Convert to a local zone only for display.
2. **Use `astimezone()` to convert, never `replace(tzinfo=...)`.** `replace` re-labels the same
   wall clock ("9:00 Berlin" becomes "9:00 UTC"), which silently shifts the instant by hours.
   `astimezone` keeps the instant and changes the label.

## Numbers

### Floats are binary, and binary cannot hold `0.1`

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
>>> f"{0.1:.30f}"
'0.100000000000000005551115123125782'
```

Floats are stored in base 2, and just as `1/3` has no exact decimal representation, `0.1` has no
exact binary one — so the stored value is the nearest approximation and the error accumulates.
This is not a Python bug; it is IEEE 754, and it is identical in JavaScript, C, and every SQL
`FLOAT` column.

Two consequences. Never compare floats with `==`; use `math.isclose`:

```python
import math
print(math.isclose(0.1 + 0.2, 0.3))
print(math.isclose(1_000_000.1, 1_000_000.2, rel_tol=1e-9))
```

And `round()` uses **banker's rounding** — ties go to the even digit, which is deliberately
different from what you were taught in school:

```python
print(round(2.5), round(3.5), round(0.125, 2))
```

```text
2 4 0.12
```

For money, none of this is acceptable.

### `Decimal` for money

```python
from decimal import Decimal

print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Decimal(0.1))
```

```text
True
0.1000000000000000055511151231257827021181583404541015625
```

The first line is why `Decimal` exists. The second is the trap: **always construct `Decimal` from
a string**, never from a float — otherwise you bake the float error in permanently.

`quantize` rounds to a fixed number of decimal places, and it defaults to the same
round-half-to-even behaviour:

```python
from decimal import ROUND_HALF_UP, Decimal

cents = Decimal("0.01")
print(Decimal("10.005").quantize(cents))                          # default: half-even
print(Decimal("10.005").quantize(cents, rounding=ROUND_HALF_UP))  # what finance expects
```

```text
10.00
10.01
```

A real invoice, end to end:

```python
from decimal import ROUND_HALF_UP, Decimal

TAX_RATE = Decimal("0.0825")          # 8.25%
CENTS = Decimal("0.01")

def money(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)

items = [("Widget", Decimal("19.99"), 3), ("Gadget", Decimal("4.50"), 2)]
subtotal = sum((price * qty for _, price, qty in items), Decimal("0"))
tax = money(subtotal * TAX_RATE)
total = money(subtotal + tax)

for name, price, qty in items:
    print(f"{name:<8} {qty:>2} x {price:>7} = {money(price * qty):>8}")
print(f"{'subtotal':<8} {'':>13} {money(subtotal):>8}")
print(f"{'tax':<8} {'':>13} {tax:>8}")
print(f"{'total':<8} {'':>13} {total:>8}")
```

```text
Widget    3 x   19.99 =    59.97
Gadget    2 x    4.50 =     9.00
subtotal                   68.97
tax                         5.69
total                      74.66
```

Subtotal 68.97, tax 5.69 (68.97 × 0.0825 = 5.6900…), total 74.66. Every intermediate value is
exact, and each one is rounded exactly once, at the point the business says it should be.

The other approach, and the one payment APIs like Stripe use: **store integer minor units** (cents)
and divide by 100 only for display. It has the same exactness with no dependency.

:::note `Fraction`
When you need exact rational arithmetic rather than exact decimal arithmetic — `1/3` and friends —
`fractions.Fraction` does it exactly:

```python
from fractions import Fraction
print(Fraction(1, 3) * 3 == 1)
print(Fraction("0.1") + Fraction("0.2") == Fraction("0.3"))
```
```text
True
True
```
Slower than floats, and rarely needed outside scientific and symbolic work.
:::

### Formatting numbers

f-strings take a format spec after a colon — `[fill][align][sign][width][,][.precision][type]`:

```python
value = 1234567.891
print(f"{value:,.2f}")     # thousands separator, 2 decimals
print(f"{value:>15,.2f}")  # right-aligned in 15 columns
print(f"{0.4237:.1%}")     # percentage
print(f"{-42:+d}")         # always show the sign
print(f"{255:#06x}")       # hex, zero-padded, with prefix
```

```text
1,234,567.89
   1,234,567.89
42.4%
-42
0x00ff
```

`{value:,.2f}` is the one you will type most. For money, pass the `Decimal` — it formats
identically and you never round-trip through a float.

### `random` for simulation, `secrets` for anything security-relevant

```python
import random

random.seed(42)                        # reproducible runs — essential for tests
print(random.random())                 # float in [0.0, 1.0)
print(random.randint(1, 6))            # inclusive both ends
print(random.choice(["rock", "paper", "scissors"]))
print(random.sample(range(100), 5))    # 5 distinct values
print(round(random.gauss(100, 15), 1)) # normal distribution
```

`random` is a **pseudo-random number generator**: deterministic given a seed, and designed for
speed, not unpredictability. That is exactly what you want for simulations, game AI (Chapter 35),
and test fixtures — and exactly what you must never use for tokens, passwords, password resets,
session IDs, or API keys, because an attacker who observes enough output can predict the rest.

```python
import secrets

token = secrets.token_urlsafe(32)                     # URL-safe random string
hex_id = secrets.token_hex(16)                        # 32 hex characters
otp = "".join(secrets.choice("0123456789") for _ in range(6))
print(token)
print(hex_id, otp)
print(secrets.compare_digest("secret-a", "secret-a"))  # constant-time comparison
```

`secrets` draws from the operating system's cryptographic random source. It has no `seed()`
because there is nothing to seed. Use `compare_digest` rather than `==` when comparing secrets,
so the comparison cannot be timed to leak how many characters matched.

:::scenario The monthly revenue report is off by four dollars
Finance sends you a spreadsheet and a question: why does your revenue report say $84,102.19 when
the payment processor says $84,106.36? The difference is $4.17 across 31,000 orders — tiny per
order, and completely invisible in every test you have, because your tests use round numbers.
:::

:::solution Floats accumulated. Switch to exact arithmetic at the boundary.
The bug is a float pipeline: prices parsed as `float`, summed, multiplied by a tax rate, rounded
with `round()` (banker's rounding, so ties drift downward), and summed again. Each step adds a
rounding error of about a billionth, and 31,000 of them add up to real money.

```python
# before — three sources of drift per order
subtotal = 19.99 * 3 + 4.50 * 2           # 68.97000000000001
tax = round(subtotal * 0.0825, 2)         # banker's rounding, float multiply
total = round(subtotal + tax, 2)
```

Fix it by making the *representation* exact, not by rounding harder:

```python
from decimal import ROUND_HALF_UP, Decimal

def to_cents(raw) -> Decimal:
    return Decimal(str(raw)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def order_total(lines) -> Decimal:
    subtotal = sum((to_cents(p) * qty for _, p, qty in lines), Decimal("0"))
    tax = (subtotal * Decimal("0.0825")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return subtotal + tax
```

`Decimal(str(raw))` instead of `Decimal(raw)` matters when `raw` is already a float — `str()`
takes the shortest representation a human meant, rather than the full binary expansion.

Three follow-ups that stop this recurring:

1. Parse external money into `Decimal` at the **edge** of your program (the JSON/CSV/DB read), not
   in the middle of the calculation. Everything downstream is then exact.
2. Store money as integer cents in the database, or as `NUMERIC`/`DECIMAL` — never `FLOAT`. SQL
   floats have exactly the same problem (Chapter 19).
3. Add a test with awkward values — `0.1`, `0.2`, `19.99`, `1.005` — and assert the exact expected
   total. Round numbers hide this bug forever.
:::

:::pitfall `0.1 + 0.2` is not `0.3`
```python
>>> 0.1 + 0.2 == 0.3
False
>>> 0.1 + 0.2
0.30000000000000004
>>> sum([0.1] * 10) == 1.0
False
```

Computers store floats in binary, and `0.1` has no exact binary representation — the stored value
is the closest approximation, so arithmetic on it carries a tiny error that sometimes becomes
visible and sometimes cancels out. That unpredictability is what makes it dangerous: your test
passes, and the customer's invoice does not.

Three responses, and which to use when:

- **Comparing floats:** `math.isclose(a, b)` (or `math.isclose(a, b, abs_tol=1e-9)` when the values
  are near zero). Never `==`.
- **Money or anything that must be exact:** `Decimal`, constructed from strings, rounded once with
  `quantize`.
- **Displaying:** format with an f-string (`f"{value:,.2f}"`). Rounding for display is fine;
  rounding to fix a calculation is not — it hides the error and moves it somewhere else.

And watch for the same problem in disguise: `round()` uses half-to-even, so `round(2.5)` is `2`
and `round(1.005, 2)` is `1.0`. If your users expect schoolbook rounding, say so explicitly with
`Decimal` and `ROUND_HALF_UP`.
:::

## Key takeaways

- Write every pattern as a raw string (`r"\d+"`); use `re.VERBOSE` for anything non-trivial.
- `search` finds anywhere, `match` anchors at the start, `fullmatch` requires the whole string —
  use `fullmatch` for validation.
- Names capture groups (`(?P<name>...)`) and read them with `m.group("name")` or `m.groupdict()`.
- Reach for a parser, not regex, when the format is nested (HTML, XML) or already has a module
  (CSV, JSON, paths).
- Use `date` for calendar days, `datetime` for instants, `timedelta` for durations; prefer ISO
  8601 for anything machine-readable.
- Store and compute in UTC with `datetime.now(timezone.utc)`; convert for display with
  `astimezone()`, never `replace(tzinfo=...)`.
- Floats cannot represent `0.1` exactly: compare with `math.isclose`, and use `Decimal` for money.
- `random` is for simulation and is seeded; `secrets` is for tokens, passwords, and anything an
  attacker might try to predict.

## Practice

- [ ] For the string `"order 42 shipped"`, print the results of `re.search(r"\d+", s)`,
      `re.match(r"\d+", s)`, and `re.fullmatch(r"\d+", s)`. Explain in a comment why two are
      `None`.
- [ ] Write `normalise(text)` that collapses all whitespace runs to a single space and strips the
      ends. Then write `numbers(text)` that returns every number in a string as a `float`.
- [ ] Compile a `re.VERBOSE` pattern with named groups for
      `2026-09-07T09:02:45Z ERROR api.auth invalid token`, then use `finditer` over a multi-line
      log to print only the `ERROR` lines' service and message.
- [ ] Compute the number of days from `date(2026, 1, 1)` to a date parsed from the string
      `"2026-12-31"`. Then convert `datetime(2026, 9, 7, 9, 0, tzinfo=ZoneInfo("Europe/Berlin"))`
      to UTC and print both.
- [ ] Build the invoice program from this chapter as a function
      `invoice(lines, tax_rate="0.0825") -> Decimal` using `Decimal` throughout, and verify that
      three items priced `0.10`, `0.20`, and `0.30` total exactly `0.60`.
- [ ] Write `make_api_key()` using `secrets` that returns a key like `sk_live_a1b2c3...` (32 hex
      chars after the prefix), plus `is_valid_key(key)` using `re.fullmatch`. Then write
      `redact(text)` that replaces every email with `a***@domain.com` using `sub` and a function.

## Solutions

:::solution Exercise 1
```python
import re

s = "order 42 shipped"
print(re.search(r"\d+", s))
print(re.match(r"\d+", s))
print(re.fullmatch(r"\d+", s))
```
```text
<re.Match object; span=(6, 8), match='42'>
None
None
```
`search` scans the whole string and finds `42` at index 6. `match` only tries position 0, where
the text is `order` — no digits, so `None`. `fullmatch` requires the entire string to be digits,
and `"order 42 shipped"` is not.
:::

:::solution Exercise 2
```python
import re

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def numbers(text: str) -> list[float]:
    return [float(m.group()) for m in re.finditer(r"-?\d+(?:\.\d+)?", text)]

raw = "  too    many\n  spaces   and 12 or -3.5 numbers "
print(repr(normalise(raw)))
print(numbers(raw))
```
```text
'too many spaces and 12 or -3.5 numbers'
[12.0, -3.5]
```
`-?` makes the minus optional and `(?:...)` groups the decimal part without capturing it, so
`m.group()` is always the whole number. Convert to `float` after matching, never inside the
pattern.
:::

:::solution Exercise 3
```python
import re

LOG_LINE = re.compile(r"""
    ^(?P<ts>\S+)                  # timestamp
    \s+(?P<level>\w+)             # severity
    \s+(?P<service>[\w.]+)        # service name
    \s+(?P<message>.*)$           # everything else
""", re.VERBOSE)

LOG = """2026-09-07T09:01:12Z INFO api.gateway path=/login
2026-09-07T09:02:45Z ERROR api.auth invalid token for user 42
2026-09-07T09:03:10Z WARN api.gateway slow response 1.9s
2026-09-07T09:04:02Z ERROR api.billing card declined
"""

for m in LOG_LINE.finditer(LOG):
    if m.group("level") == "ERROR":
        print(f"{m.group('service'):<14} {m.group('message')}")
```
```text
api.auth       invalid token for user 42
api.billing    card declined
```
`finditer` needs `re.MULTILINE` only if you use `^`/`$` with `re.match`-style anchoring across
lines — here the pattern is applied per line because `.` does not cross newlines, so each match
stays on one line. `re.VERBOSE` strips the indentation from the pattern, so layout it for humans.
:::

:::solution Exercise 4
```python
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

start = date(2026, 1, 1)
end = datetime.strptime("2026-12-31", "%Y-%m-%d").date()
print(f"{start} -> {end}: {(end - start).days} days")

berlin = datetime(2026, 9, 7, 9, 0, tzinfo=ZoneInfo("Europe/Berlin"))
utc = berlin.astimezone(timezone.utc)
print(berlin, "=", utc)
print(utc.isoformat())
```
```text
2026-01-01 -> 2026-12-31: 364 days
2026-09-07 09:00:00+02:00 = 2026-09-07 07:00:00+00:00
2026-09-07T07:00:00+00:00
```
`strptime` returns a `datetime`, so `.date()` converts it to a `date` before subtracting —
subtracting a `datetime` from a `date` is a `TypeError`. Note 364 days, not 365: 2026 is not a
leap year and the interval is exclusive of the end day.
:::

:::solution Exercise 5
```python
from decimal import ROUND_HALF_UP, Decimal

def invoice(lines, tax_rate="0.0825") -> Decimal:
    cents = Decimal("0.01")
    subtotal = sum(
        (Decimal(str(price)) * qty for _, price, qty in lines),
        Decimal("0"),
    )
    tax = (subtotal * Decimal(tax_rate)).quantize(cents, rounding=ROUND_HALF_UP)
    return (subtotal + tax).quantize(cents, rounding=ROUND_HALF_UP)

print(invoice([("A", "0.10", 1), ("B", "0.20", 1), ("C", "0.30", 1)], tax_rate="0"))
print(invoice([("Widget", "19.99", 3), ("Gadget", "4.50", 2)]))
```
```text
0.60
74.66
```
With a zero tax rate the three items total exactly `0.60` — the float version gives
`0.6000000000000001`. `Decimal(str(price))` accepts a string or a float safely, because `str()`
of a float gives the shortest representation a human would have typed.
:::

:::solution Exercise 6
```python
import re
import secrets

KEY = re.compile(r"sk_live_[0-9a-f]{32}")

def make_api_key() -> str:
    return f"sk_live_{secrets.token_hex(16)}"

def is_valid_key(key: str) -> bool:
    return KEY.fullmatch(key) is not None

EMAIL = re.compile(r"(?P<user>[\w.+-]+)@(?P<domain>[\w-]+\.[\w.]+)")

def redact(text: str) -> str:
    return EMAIL.sub(lambda m: f"{m.group('user')[0]}***@{m.group('domain')}", text)

key = make_api_key()
print(key, is_valid_key(key), is_valid_key("sk_live_tooshort"))
print(redact("mail ada@example.com or bob.smith@corp.co.uk now"))
```
```text
sk_live_9f3c... True False
mail a***@example.com or b***@corp.co.uk now
```
`token_hex(16)` gives 32 hex characters. `fullmatch` is essential for validation — `search` would
accept `password: sk_live_abc...` as a valid key. And the key comes from `secrets`, not `random`,
because anyone who can predict a key can forge a request.
:::
