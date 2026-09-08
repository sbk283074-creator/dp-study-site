---
chapter: 3
part: 1
title: Strings & Formatting
summary: Slice, search, and reshape text with confidence, and lay numbers out in readable columns using modern f-string format specs.
minutes: 35
tags: [strings, slicing, methods, f-strings, encoding]
---

Real programs are mostly text wrangling. A user types a name, you read a config line, an API hands
you JSON, you print a report. Numbers matter, but the code around them — parsing, cleaning,
formatting, displaying — is strings. Chapter 2 introduced them; this chapter makes you dangerous
with them, and ends with the tool you will use in every program you ever write: the f-string
format spec.

## String literals and quote choices

A string is any text between quotes. Python treats single and double quotes identically, which
means you can pick whichever avoids escaping:

```python
greeting = "hello"
name = 'ada'
sentence = "It's fine"        # double outside, apostrophe inside
quote = 'She said "go"'       # single outside, double inside
```

For the rare case where you need both, use the other quote or escape with a backslash:

```python
both = "She said \"it's fine\""
```

Quotes only become a real decision with **triple-quoted strings**, which may span lines and
preserve every newline and space:

```python
paragraph = """Line one
Line two
"""
```

:::tip Which quote should I default to?
Double quotes, because English text contains apostrophes more often than quotation marks. Pick one
for your project and let a formatter (Chapter 22) enforce it.
:::

### Escapes and raw strings

A backslash starts an **escape sequence**: `\n` newline, `\t` tab, `\\` a literal backslash,
`\"` a literal quote. That last one is a problem when you write Windows paths or regular
expressions, where backslashes are common. Prefix the string with `r` to make it **raw** —
backslashes stop being special:

```python
path = r"C:\Users\ada\notes.txt"
print(path)
```

```text
C:\Users\ada\notes.txt
```

One restriction: a raw string cannot end with an odd number of backslashes. `r"C:\"` is a syntax
error, because the final backslash escapes the closing quote.

## Indexing and slicing

A string is a sequence of characters, numbered from `0`. Negative indices count from the end:

```python
>>> word = "Python"
>>> word[0], word[5], word[-1]
('P', 'n', 'n')
```

`word[6]` raises `IndexError` — there is no seventh character. Ask for a **slice** instead and
Python is forgiving; out-of-range slice bounds clamp silently:

```python
>>> word[0:2]      # from index 0 up to but NOT including 2
'Py'
>>> word[:2]       # omit start → 0
'Py'
>>> word[2:]       # omit stop → end
'thon'
>>> word[:]        # a copy of the whole string
'Python'
>>> word[0:99]     # no error
'Python'
```

The full form is `s[start:stop:step]`, and the step is where slicing gets powerful:

```python
>>> word[::2]          # every second character
'Pto'
>>> word[::-1]         # step -1 walks backwards
'nohtyP'
>>> word[::-2]
'nhy'
```

`word[::-1]` is the standard palindrome test: `if word == word[::-1]`.

The **stop index is exclusive** — `s[2:4]` gives two characters, indices 2 and 3. Internalise that
now; off-by-one errors in slicing are the most common bug in string code.

## Strings are immutable

You cannot change a character in place:

```python
>>> word = "Python"
>>> word[0] = "J"
TypeError: 'str' object does not support item assignment
```

This is not a limitation to work around, it is the design. Every string method **returns a new
string**; the original never changes:

```python
>>> name = "ada"
>>> name.upper()      # produces a new string
'ADA'
>>> name              # the original is untouched
'ada'
>>> name = name.upper()   # rebind if you want to keep it
```

That last line is the pattern: call the method, rebind the name. Forgetting to rebind — writing
`name.upper()` on its own line and wondering why nothing happened — happens to everyone for about
a week.

## The methods you will actually use

Assume `s = "  Ada Lovelace  "`.

| Method | What it does | Example result |
| --- | --- | --- |
| `s.strip()` | Remove leading/trailing whitespace | `'Ada Lovelace'` |
| `s.strip("ae ")` | Strip any of the given characters | `'Ada Lovelac'` |
| `s.lower()` / `s.upper()` | Change case | `'  ada lovelace  '` |
| `s.title()` | Capitalise each word | `'  Ada Lovelace  '` |
| `s.casefold()` | Aggressive lowercase for comparisons | `'  ada lovelace  '` |
| `s.replace(a, b)` | Replace all occurrences | new string |
| `s.split(sep)` | Split into a list | `['Ada', 'Lovelace']` |
| `sep.join(list)` | Opposite of split | `'Ada Lovelace'` |
| `s.find(sub)` | Index of `sub`, or `-1` | `2` |
| `s.index(sub)` | Index of `sub`, or `ValueError` | `2` |
| `s.count(sub)` | Number of occurrences | `1` |
| `s.startswith(x)` | Prefix test (accepts a tuple) | `False` |
| `s.endswith(x)` | Suffix test (accepts a tuple) | `False` |
| `s.partition(sep)` | Split once into 3 parts | `('  Ada', ' ', 'Lovelace  ')` |
| `s.removeprefix(p)` | Drop prefix if present, else unchanged | new string |
| `s.removesuffix(x)` | Drop suffix if present, else unchanged | new string |

Prefer `find()` over `index()` unless a missing substring is genuinely a bug — `-1` is easier to
handle than an exception, and `index()` forces you into `try`/`except`, which is Chapter 9's
territory.

`startswith()` and `endswith()` accept a tuple of candidates, which beats chaining `or`:

```python
>>> "report.pdf".endswith((".pdf", ".txt", ".md"))
True
```

`partition()` is the right tool for `key = value` lines, because it always returns exactly three
items and never raises:

```python
>>> "timeout=30".partition("=")
('timeout', '=', '30')
>>> "timeout".partition("=")
('timeout', '', '')
```

Membership testing uses `in`, which reads like English and answers with a `bool`:

```python
>>> "love" in "Ada Lovelace"
False
>>> "Love" in "Ada Lovelace"
True
```

Note the case sensitivity. Caseless searching means normalising both sides first:
`"love" in name.casefold()`.

:::pitfall `split()` with no argument is not `split(" ")`
`split()` with no argument splits on **any run of whitespace** and discards empty fields.
`split(" ")` splits on single spaces and keeps the empties. Given messy input:

```python
>>> "  Ada   Lovelace ".split()
['Ada', 'Lovelace']
>>> "  Ada   Lovelace ".split(" ")
['', '', 'Ada', '', '', 'Lovelace', '']
```

That difference is a data-quality bug waiting to happen. Use `split()` for "break into words".
Reach for `split(" ")` only when empty fields are meaningful — a fixed-width format, for example
— and prefer the `csv` module (Chapter 19) for real tabular data. To collapse messy whitespace in
text, combine the two:

```python
>>> " ".join("  Ada   Lovelace  ".split())
'Ada Lovelace'
```
:::

## F-strings in depth

Chapter 2 showed the basics. The power lives after the colon: `f"{value:spec}"`.

```python
amount = 1234.5678
print(f"{amount:.2f}")     # 2 decimal places
print(f"{amount:,.2f}")    # thousands separator + 2 decimals
print(f"{amount:>15,.2f}") # right-aligned in 15 columns
print(f"{amount:08.2f}")   # zero-padded to width 8
```

```text
1234.57
1,234.57
       1,234.57
01234.57
```

The alignment options are `<` (left), `>` (right, the default for numbers), and `^` (centre),
each followed by a width:

```python
print(f"[{'OK':^8}]")
print(f"[{'FAILED':^8}]")
print(f"{'Item':<20}{'Qty':>6}")
print(f"{'Bolt':<20}{240:>6}")
```

```text
[   OK   ]
[ FAILED ]
Item                   Qty
Bolt                  240
```

Percentages use `%`, which multiplies by 100 and adds the sign for you:

```python
>>> f"{0.125:.1%}", f"{0.125:.2%}"
('12.5%', '12.50%')
```

Inside `{}` you can put any expression, including calls and nested format specs:

```python
price, qty = 4.99, 240
print(f"{qty} @ {price:.2f} = {price * qty:,.2f}")
```

```text
240 @ 4.99 = 1,197.60
```

When you want a value with a custom repr, add `!r` (or `!s`, `!a`):

```python
>>> name = "Ada\t"
>>> f"{name!r}"
"'Ada\t'"
```

The extra quotes and the visible `\t` are the point: `!r` shows you what is really in the string,
which is how you spot invisible whitespace.

### The `=` debugger spec

Python 3.8 added `=`, which prints the expression *and* its value. It is the fastest debugging
tool in the language:

```python
total = 1197.6
tax = total * 0.085
print(f"{total=:.2f} {tax=:.2f}")
```

```text
total=1197.60 tax=101.80
```

Use it instead of `print("total:", total)` — you cannot forget to update the label when you rename
the variable, because the label *is* the code.

## Multi-line strings and `textwrap.dedent`

Triple-quoted strings keep your indentation, which is usually not what you want:

```python
report = """
    Monthly Summary
    ---------------
"""
print(report)
```

```text

    Monthly Summary
    ---------------

```

`textwrap.dedent` strips the common leading whitespace:

```python
from textwrap import dedent

report = """
    Monthly Summary
    ---------------
"""
print(dedent(report).strip())
```

```text
Monthly Summary
---------------
```

`dedent` only removes whitespace that *every* line shares, so it is safe even when some lines are
nested deeper. Combined with an f-string you get readable templates:

```python
from textwrap import dedent

store = "Northwind Hardware"
count = 3
print(dedent(f"""
    {store}
    Items counted: {count}
""").strip())
```

## `str` vs `bytes`

Text is an abstraction; files and networks move **bytes**. A `str` is a sequence of Unicode
characters; `bytes` is a sequence of 0–255 integers. Convert with `encode()` and `decode()`, and
always name the encoding:

```python
>>> text = "café"
>>> data = text.encode("utf-8")
>>> data
b'caf\xc3\xa9'
>>> data.decode("utf-8")
'café'
>>> len(text), len(data)
(4, 5)
```

Four characters, five bytes — the é takes two. Bytes literals are prefixed `b`, and `bytes` has
most `str` methods but no formatting and no f-strings.

:::pitfall Mixing `str` and `bytes`
Python will not guess an encoding for you:

```python
>>> "café" + b"!"
TypeError: can't concat str to bytes
>>> b"caf\xc3\xa9".upper()
b'CAF\xc3\xa9'
```

Decode on the way in, encode on the way out, and keep everything in between as `str`. The two
places this bites are file I/O (Chapter 8) and HTTP responses (Chapter 18): open text files with
an explicit `encoding="utf-8"` and let `requests` handle the rest. If you see
`UnicodeDecodeError`, you have bytes being decoded with the wrong codec — never "fix" it by
ignoring errors; find the actual encoding.
:::

## Worked example: a small report generator

Pull it together. This builds a stock report with aligned columns — the kind of thing you email
to a manager:

```python
# report.py
from textwrap import dedent

store = "Northwind Hardware"
period = "2026-08"

name_1, qty_1, price_1 = "Hex bolt M8", 240, 0.45
name_2, qty_2, price_2 = "Washer M8", 1200, 0.08
name_3, qty_3, price_3 = "Torque wrench", 6, 89.90

value_1 = qty_1 * price_1
value_2 = qty_2 * price_2
value_3 = qty_3 * price_3
subtotal = value_1 + value_2 + value_3
shipping = 12.50
total = subtotal + shipping

header = f"{'Item':<20}{'Qty':>6}{'Unit':>10}{'Value':>12}"
rule = "-" * len(header)
rows = [
    f"{name_1:<20}{qty_1:>6,}{price_1:>10.2f}{value_1:>12,.2f}",
    f"{name_2:<20}{qty_2:>6,}{price_2:>10.2f}{value_2:>12,.2f}",
    f"{name_3:<20}{qty_3:>6,}{price_3:>10.2f}{value_3:>12,.2f}",
]

print(dedent(f"""
    {store} — stock valuation {period}
""").strip())
print(header)
print(rule)
print("\n".join(rows))
print(rule)
print(f"{'Subtotal':<20}{'':>6}{'':>10}{subtotal:>12,.2f}")
print(f"{'Shipping':<20}{'':>6}{'':>10}{shipping:>12,.2f}")
print(f"{'TOTAL':<20}{'':>6}{'':>10}{total:>12,.2f}")
```

```bash
python3 report.py
```

```text
Northwind Hardware — stock valuation 2026-08
Item                   Qty      Unit       Value
------------------------------------------------
Hex bolt M8             240      0.45      108.00
Washer M8             1,200      0.08       96.00
Torque wrench             6     89.90      539.40
------------------------------------------------
Subtotal                                   743.40
Shipping                                    12.50
TOTAL                                      755.90
```

Every column is a format spec: `<20` left-aligns the item name in 20 characters, `>6,` right-aligns
the quantity with thousands separators, `>10.2f` right-aligns a two-decimal float. Changing a
number changes the output, not the layout — that is the whole point. The three explicit rows are
deliberately repetitive; Chapter 7 replaces them with a loop over a list of products, and the
formatting logic survives unchanged.

:::scenario Your log parser reports empty usernames
A teammate's script splits each log line on a space and pulls field 2 as the username. On
production data, roughly one in twenty lines yields an empty string, and the dashboard is full of
blank users. The dev environment never showed it.
:::

:::solution The lines have irregular spacing
Logs are usually padded for alignment, so `- - admin - - -` style lines contain runs of spaces.
`split(" ")` treats each space as a delimiter and hands back the empty fields between them:

```python
>>> line = "2026-08-01 09:14:02  admin   login"
>>> parts = line.split(" ")
>>> parts
['2026-08-01', '09:14:02', '', 'admin', '', '', 'login']
>>> parts[2]
''
```

Two fixes, depending on intent. If you want "the words in this line", use `split()` with no
argument — it collapses runs of whitespace:

```python
>>> line.split()
['2026-08-01', '09:14:02', 'admin', 'login']
```

If a field can legitimately contain spaces (a message like `login failed`), limit the split so
the remainder stays intact:

```python
>>> line.split(maxsplit=3)
['2026-08-01', '09:14:02', 'admin', 'login']
>>> "ERROR: disk full on /mnt/data".split(":", maxsplit=1)
['ERROR', ' disk full on /mnt/data']
```

Then `strip()` each field as you consume it. The underlying lesson is general: **do not trust
incoming text to be tidy.** Normalise first (`strip()`, `split()`, `casefold()`), then parse.
Chapter 19 replaces this hand-parsing with the `csv` module, and Chapter 17 with regular
expressions when the structure gets genuinely irregular.
:::

## Key takeaways

- Strings are immutable: every method returns a new string, so rebind the name to keep the result.
- `s[start:stop:step]` slices; `stop` is exclusive, negative indices count from the end, and
  `s[::-1]` reverses.
- `split()` (no argument) splits on any whitespace run; `split(" ")` splits on single spaces and
  keeps empty fields.
- `find()` returns `-1` when a substring is missing; `index()` raises. `partition()` always
  returns three parts.
- F-string format specs control presentation: `:.2f` decimals, `:,` separators, `:>10` / `:<10` /
  `:^10` alignment, `:%` percentages, `{expr=}` for debugging.
- `textwrap.dedent` removes the shared indentation from triple-quoted strings.
- `str` is Unicode text, `bytes` is raw data: `encode()` out, `decode()` in, never concatenate
  them.

## Practice

- [ ] In the REPL with `s = "Python Mastery"`, produce `"Pto"`, `"yretsaM"`, `"Mast"`, and
      `"Python Mastery"` reversed — using only slices.
- [ ] Write `normalize.py`: read a full name (possibly with extra spaces and odd case), then print
      it as `Lovelace, A.` using `strip`, `split`, and `join`.
- [ ] Write `slug.py`: turn a title into a URL slug — lowercase, remove commas/periods/exclamation
      marks, replace spaces with hyphens, strip stray hyphens from the ends.
- [ ] Write `table.py`: print a three-row table of programming languages with a left-aligned name
      column, a right-aligned year column, and a right-aligned user count using `:,`.
- [ ] Write `config.py`: given three `"key=value"` strings, use `partition` to print an aligned
      settings report where the value of the `password` key is masked with asterisks.

## Solutions

:::solution Exercise 2
```python
raw = input("Full name: ")
parts = raw.split()                 # collapses messy whitespace
first, last = parts[0], parts[-1]
print(f"{last.title()}, {first[0].upper()}.")
```
`split()` with no argument handles `"  ada   LOVELACE "` correctly, turning it into
`['ada', 'LOVELACE']`. Indexing `parts[0]` and `parts[-1]` keeps the first and last word even for
three-part names, and `first[0]` grabs the initial.
:::

:::solution Exercise 3
```python
title = input("Title: ").strip().lower()
clean = title.replace(",", "").replace(".", "").replace("!", "")
slug = "-".join(clean.split()).strip("-")
print(slug)
```
The order matters: strip and lowercase first, remove punctuation, then collapse whitespace into
single hyphens with `"-".join(text.split())`. `strip("-")` cleans up any hyphen left at an edge by
trailing punctuation.
:::

:::solution Exercise 4
```python
header = f"{'Language':<14}{'Year':>6}{'Users':>12}"
rows = [
    f"{'Python':<14}{1991:>6}{15_000_000:>12,}",
    f"{'JavaScript':<14}{1995:>6}{20_000_000:>12,}",
    f"{'Rust':<14}{2015:>6}{3_000_000:>12,}",
]

print(header)
print("-" * len(header))
print("\n".join(rows))
```
Widths are chosen once and reused, so every row lines up. `"-" * len(header)` computes the rule
from the header rather than hard-coding it, so it stays correct when you change a column width.
:::

:::solution Exercise 5
```python
lines = ["host=db.internal", "port=5432", "password=hunter2"]

print(f"{'Setting':<12}{'Value':<16}")
print("-" * 28)

key_1, _, val_1 = lines[0].partition("=")
key_2, _, val_2 = lines[1].partition("=")
key_3, _, val_3 = lines[2].partition("=")
val_3 = "*" * len(val_3)

print(f"{key_1:<12}{val_1:<16}")
print(f"{key_2:<12}{val_2:<16}")
print(f"{key_3:<12}{val_3:<16}")
```

```text
Setting     Value
----------------------------
host        db.internal
port        5432
password    *******
```

`partition` always yields exactly three items, so the unpacking into `key, _, val` never raises —
`split` would raise `ValueError` on a line with no `=`. The `_` name is the conventional "I do not
care about this value", and `"*" * len(val)` preserves the shape of the secret without revealing
it.
:::
