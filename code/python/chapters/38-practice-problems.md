---
chapter: 38
part: 6
title: Practice Problem Bank
summary: Thirty graded problems with worked solutions — the practice you need after the last chapter, and the material interviewers actually draw from.
minutes: 90
tags: [exercises, practice, algorithms, refactoring, testing]
---

Reading about Python makes you able to recognise Python. Writing it makes you able to produce
it. This appendix is thirty problems: six warm-ups, then five themed groups of six, each group
ending with two problems that are genuinely hard. Every problem has a hint that nudges without
spoiling, and a solution at the bottom of its section. Attempt the problem first — a ten-minute
struggle teaches more than a ten-second read. If you get stuck, read the hint, not the solution.
Then write the solution again from memory the next day; that second pass is where it sticks.

## Warm-ups

### 1. Temperature table

A lab notebook needs a printed reference chart. Formatting output into aligned columns is a
skill you will use in every CLI and every report you ever write.

Write `temperature_table(start: int, stop: int, step: int = 10) -> list[str]` that returns the
lines of a table converting Celsius to Fahrenheit, with a header row. Celsius values are
right-aligned in four characters; Fahrenheit values are right-aligned in six characters with one
decimal place. Fahrenheit is `c * 9 / 5 + 32`.

```text
   C      F
 -10   14.0
   0   32.0
  10   50.0
  20   68.0
```

:::tip Hint
The f-string format spec is `{value:>width.precisionf}`. Build the header with the same widths
so the columns line up, and use `range(start, stop + 1, step)` — `range` excludes its stop.
:::

### 2. FizzBuzz

Still the fastest filter for "can this person write a loop and a conditional without panicking".

Write `fizzbuzz(n: int) -> list[str]` returning `n` strings: for each number from 1 to `n`,
`"Fizz"` if divisible by 3, `"Buzz"` if divisible by 5, `"FizzBuzz"` if divisible by both, and
the number as a string otherwise.

```python
>>> fizzbuzz(15)[11:]
['Fizz', '13', '14', 'FizzBuzz']
```

:::tip Hint
The order of your checks decides whether 15 works. Test divisibility by 15 first — or use the
same `if` twice inside one branch.
:::

### 3. Days in a month

Billing code, subscription code, and every date picker need this.

Write `days_in_month(year: int, month: int) -> int`. Raise `ValueError` if `month` is not 1–12.
February has 29 days in a leap year: a year is a leap year if it is divisible by 4, except
centuries, which must be divisible by 400.

```python
>>> days_in_month(2024, 2)
29
>>> days_in_month(2100, 2)
28
```

:::tip Hint
Put the twelve lengths in a tuple and index it with `month - 1`; only February needs the leap
rule. Write `is_leap_year(year)` as a separate function so you can test it on its own.
:::

### 4. Collatz steps

A loop whose trip count you cannot know in advance — the same shape as "retry until the API
answers" or "poll until the job finishes".

Write `collatz_steps(n: int) -> int`. Starting from `n`, if it is even halve it, if it is odd
triple it and add one; count how many steps until you reach 1. Raise `ValueError` for `n < 1`.

```python
>>> collatz_steps(27)
111
>>> collatz_steps(16)
4
```

:::tip Hint
`while n != 1:` and update `n` with a conditional expression. Validate the input before the
loop, otherwise a value like 0 hangs forever.
:::

### 5. Making change

Cash drawers, vending machines, and splitting a payment all reduce to this.

Write `make_change(cents: int, denominations: tuple[int, ...] = (200, 100, 50, 20, 10, 5, 2, 1))
-> dict[int, int]` returning how many of each denomination to hand over, taking the largest coin
first. If the denominations cannot make the amount exactly, raise `ValueError`.

```python
>>> make_change(87, (25, 10, 5, 1))
{25: 3, 10: 1, 1: 2}
>>> make_change(7, (10,))
ValueError: cannot make 7 exactly with (10,)
```

:::tip Hint
`divmod(amount, coin)` gives you both the count and the remainder in one call. Sum
`coin * count` at the end and compare with the input — that check is the difference between a
greedy guess and a correct answer.
:::

### 6. ISBN-10 validation

A catalogue import is rejecting books, and you need to know which records are actually broken.

Write `is_valid_isbn10(isbn: str) -> bool`. Ignore hyphens and surrounding whitespace. The string
must be exactly ten characters: nine digits followed by a digit or `X` (meaning 10). Multiply
each character's value by its weight from 10 down to 1, sum them, and the ISBN is valid if the
sum is divisible by 11.

```python
>>> is_valid_isbn10("0306406152")
True
>>> is_valid_isbn10("080442957X")
True
>>> is_valid_isbn10("0306406153")
False
```

:::tip Hint
`enumerate` gives you both the index and the character, and the weight is `10 - index`.
`X` is only legal in the last position — anywhere else it is invalid, not ten.
:::

:::solution Solution 1
```python
def fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def temperature_table(start: int, stop: int, step: int = 10) -> list[str]:
    lines = [f"{'C':>4} {'F':>6}"]
    for c in range(start, stop + 1, step):
        lines.append(f"{c:>4} {fahrenheit(c):>6.1f}")
    return lines


print("\n".join(temperature_table(-10, 20)))
```
The format spec `>6.1f` means "right-align in six columns, one decimal place", which is why the
decimal points line up. Keeping the header in the same format means the widths can never drift
apart.
:::

:::solution Solution 2
```python
def fizzbuzz(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
```
Checking `% 15` first is the whole trick: if you test `% 3` first, 15 says "Fizz" and the bug
survives every casual glance. This is the canonical example of branch order being a correctness
concern.
:::

:::solution Solution 3
```python
MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError(f"month must be 1-12, got {month}")
    if month == 2 and is_leap_year(year):
        return 29
    return MONTH_LENGTHS[month - 1]
```
The leap rule reads exactly as the English does: divisible by 4, *and* either not a century or a
century divisible by 400. Splitting it out means you can test 1900, 2000, and 2100 in one line
each.
:::

:::solution Solution 4
```python
def collatz_steps(n: int) -> int:
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps
```
Input validation is not decoration here: 0 and negative numbers never reach 1, so the loop would
spin forever. Any loop whose exit condition depends on data needs a guard.
:::

:::solution Solution 5
```python
def make_change(cents: int, denominations: tuple[int, ...] = (200, 100, 50, 20, 10, 5, 2, 1)) -> dict[int, int]:
    if cents < 0:
        raise ValueError("amount must not be negative")
    change: dict[int, int] = {}
    remaining = cents
    for coin in sorted(denominations, reverse=True):
        count, remaining = divmod(remaining, coin)
        if count:
            change[coin] = count
    if remaining:
        raise ValueError(f"cannot make {cents} exactly with {denominations}")
    return change
```
`divmod` replaces a division and a modulo with one call and removes the chance of them
disagreeing. The final `remaining` check is what turns "a greedy attempt" into "a correct
answer" — greedy change-making is only optimal for certain coin systems, so you must verify
rather than assume.
:::

:::solution Solution 6
```python
def is_valid_isbn10(isbn: str) -> bool:
    digits = isbn.replace("-", "").strip()
    if len(digits) != 10:
        return False

    total = 0
    for index, char in enumerate(digits):
        if char.isdigit():
            value = int(char)
        elif char in "xX" and index == 9:
            value = 10
        else:
            return False
        total += (10 - index) * value

    return total % 11 == 0
```
Early returns keep the happy path flat: wrong length, bad character, and finally the checksum.
Note that `str.isdigit()` is not the same as `char in "0123456789"` — it accepts Unicode digits
like `٣`, which would silently pass here, so use the explicit set if you are being strict.
:::

## Strings & text

### 7. Top words

The first step of almost every text analysis you will ever do.

Write `top_words(text: str, n: int = 10) -> list[tuple[str, int]]`. Lower-case the text, count
each word — a word is a run of letters and apostrophes — and return the `n` most common, sorted
by count descending, ties broken alphabetically.

```python
>>> top_words("Hello, hello! World? The world says hello.", 3)
[('hello', 3), ('world', 2), ('says', 1)]
```

:::tip Hint
`re.findall(r"[a-z']+", text.lower())` handles punctuation for you. `collections.Counter` counts,
and `sorted(..., key=lambda kv: (-kv[1], kv[0]))` gives you descending count with alphabetical
tie-breaking in one expression.
:::

### 8. Name normalisation

Imported customer data arrives as `jOHN   o'brien`, `MARY-JANE WATSON`, and `van der BERG`. The
mail merge looks dreadful.

Write `normalise_name(raw: str) -> str`. Collapse runs of whitespace to a single space.
Capitalise the first letter of each part, and also after a hyphen or an apostrophe — except a
trailing `'s`, which is a possessive and stays lower case.

```python
>>> normalise_name("  jOHN   o'brien ")
"John O'Brien"
>>> normalise_name("MARY-JANE WATSON")
'Mary-Jane Watson'
>>> normalise_name("o'brien's")
"O'Brien's"
```

:::tip Hint
`str.title()` gets `O'Brien` right but `John'S` wrong, so it cannot be the whole answer. Split
on whitespace, then split each word on `([-'])` with a capturing group so the separators survive
in the result, and capitalise only the parts that are not separators.
:::

### 9. Template rendering

You need to send `Hi {{ name }}, you have {{ count }} messages` with real values, and the
templates come from a database, not from you.

Write `render(template: str, values: dict, *, strict: bool = True) -> str`. Replace every
`{{ key }}` (optional whitespace inside the braces) with `str(values[key])`. In strict mode an
unknown key raises `KeyError` naming it; with `strict=False` leave the placeholder untouched.

```python
>>> render("Hi {{ name }}, you have {{ count }} messages", {"name": "Ada", "count": 3})
'Hi Ada, you have 3 messages'
>>> render("Hi {{name}}, you have {{ count }} messages", {"name": "Ada"}, strict=False)
'Hi Ada, you have {{ count }} messages'
```

:::tip Hint
Do not reach for `str.format()` — the templates contain literal braces and user-controlled text.
Use `re.sub` with a *function* as the replacement: it receives each match and returns the string
to substitute, which is where your lookup and error handling go.
:::

### 10. Parsing a log line

Two gigabytes of nginx access logs, and somebody wants to know which endpoints 404.

Write `parse_log_line(line: str) -> dict` that parses a combined-format line and returns
`{"ip", "timestamp", "method", "path", "status", "size"}`, with `status` and `size` as integers
and a `-` size as `0`. Raise `ValueError` with the offending line if it does not match.

```python
>>> parse_log_line('127.0.0.1 - - [04/Mar/2025:09:12:03 +0000] "GET /api/orders HTTP/1.1" 200 1234')
{'ip': '127.0.0.1', 'timestamp': '04/Mar/2025:09:12:03 +0000', 'method': 'GET',
 'path': '/api/orders', 'status': 200, 'size': 1234}
```

:::tip Hint
Named groups (`(?P<ip>\S+)`) turn a regex into a dictionary. Build the pattern one field at a
time in the REPL, and remember that `[` and `"` are literal characters that need no escaping but
`[^\]]+` is how you match "anything up to the closing bracket".
:::

### 11. Word wrap

Terminal output, generated emails, and PDF reports all need this, and "split every 72
characters" is not good enough.

Write `wrap(text: str, width: int = 72) -> list[str]`. Fill lines greedily without breaking
words. Preserve paragraphs: a blank line in the input separates them and each paragraph wraps
independently. No trailing whitespace; words longer than `width` go on their own line rather
than being split.

```python
>>> wrap("The quick brown fox jumps over the lazy dog and keeps on running.", 20)
['The quick brown fox', 'jumps over the lazy', 'dog and keeps on', 'running.']
```

:::tip Hint
Split into paragraphs with `re.split(r"\n\s*\n", text.stripped)`, then for each one split on
whitespace (`.split()` with no argument) and append words to a current line while
`len(current) + 1 + len(word) <= width`.
:::

### 12. Breaking a Caesar cipher

Hard. A legacy export encrypted single words with a shifted alphabet and nobody remembers the
shift. Brute force gives you 26 candidates; you need the one that is English.

Write `caesar(text: str, shift: int) -> str` (shift letters, preserve case, leave everything else
alone) and `break_caesar(ciphertext: str) -> tuple[int, str]`, returning the shift and the
recovered plaintext. Score each of the 26 candidates by how closely its letter frequencies match
English, and pick the best.

```python
>>> secret = caesar("We hold these truths to be self evident, that all men are created equal, "
...                 "that they are endowed by their creator with certain unalienable rights, "
...                 "that among these are life, liberty and the pursuit of happiness.", 11)
>>> shift, plain = break_caesar(secret)
>>> shift
11
>>> plain[:46]
'We hold these truths to be self evident, that'
```

:::tip Hint
Chi-squared: for each letter, `((observed% - expected%) ** 2) / expected%`, summed over the
alphabet; the lowest score wins. It needs a few hundred characters to be reliable, and it will
not rescue you if the plaintext is not English.
:::

:::solution Solution 7
```python
import re
from collections import Counter


def top_words(text: str, n: int = 10) -> list[tuple[str, int]]:
    words = re.findall(r"[a-z']+", text.lower())
    counts = Counter(words)
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
```

```python
>>> top_words("Hello, hello! World? The world says hello.", 3)
[('hello', 3), ('world', 2), ('says', 1)]
```
`Counter` is a dict subclass built for exactly this, and the two-part sort key handles both rules
at once: `-count` first (descending), then the word (ascending) to break ties. Never rely on
`Counter.most_common()` alone if you need deterministic output — its tie order is insertion
order, which changes when the input changes.
:::

:::solution Solution 8
```python
import re


def normalise_name(raw: str) -> str:
    words = []
    for word in raw.split():
        parts = re.split(r"([-'])", word.lower())
        out: list[str] = []
        for index, part in enumerate(parts):
            if part in "-'":                                    # separator: keep as-is
                out.append(part)
            elif out and out[-1] == "'" and part == "s" and index == len(parts) - 1:
                out.append(part)                                # possessive: leave lower case
            else:
                out.append(part.capitalize())
        words.append("".join(out))
    return " ".join(words)
```

```python
>>> normalise_name("  jOHN   o'brien ")
"John O'Brien"
>>> normalise_name("o'brien's")
"O'Brien's"
```
`re.split` with a *capturing* group keeps the separators in the output list, so you can rejoin
with `"".join(out)` and lose nothing. `str.split()` with no argument already collapses runs of
whitespace. Real name normalisation is unsolvable in general — `van der Berg` versus
`Van der Berg` depends on the person — so define the rule, write it down, and let the data owner
correct the exceptions.
:::

:::solution Solution 9
```python
import re

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render(template: str, values: dict, *, strict: bool = True) -> str:
    def substitute(match: re.Match) -> str:
        key = match.group(1)
        if key in values:
            return str(values[key])
        if strict:
            raise KeyError(f"no value supplied for placeholder {key!r}")
        return match.group(0)          # leave the placeholder exactly as it was

    return PLACEHOLDER.sub(substitute, template)
```
Passing a function to `re.sub` is the general technique for "replace with something I have to
compute". Rejecting unknown keys is the right default: a template that renders `Hi , you have
messages` in production is worse than a crash in staging.
:::

:::solution Solution 10
```python
import re

LOG_LINE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d{3}) (?P<size>\d+|-)'
)


def parse_log_line(line: str) -> dict:
    match = LOG_LINE.match(line.strip())
    if match is None:
        raise ValueError(f"unparseable log line: {line!r}")
    return {
        "ip": match["ip"],
        "timestamp": match["timestamp"],
        "method": match["method"],
        "path": match["path"],
        "status": int(match["status"]),
        "size": 0 if match["size"] == "-" else int(match["size"]),
    }
```
`\S+` ("run of non-whitespace") parses fixed-layout logs reliably and is far faster than a
greedy `.*`. Always check `match is None` and raise with the offending input — a silent skip
means your totals are quietly wrong, which is worse than a crash you can see.
:::

:::solution Solution 11
```python
import re


def wrap(text: str, width: int = 72) -> list[str]:
    lines: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        current = ""
        for word in paragraph.split():
            if not current:
                current = word                              # always take at least one word
            elif len(current) + 1 + len(word) <= width:
                current += " " + word
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines
```
The `if not current` branch is what makes over-long words safe: a 90-character URL goes on its
own line instead of causing an infinite loop or being chopped. Building lines by concatenation
rather than by slicing means no line ever has trailing whitespace.
:::

:::solution Solution 12
```python
from collections import Counter

ENGLISH_FREQ = {
    "a": 8.2, "b": 1.5, "c": 2.8, "d": 4.3, "e": 12.7, "f": 2.2, "g": 2.0,
    "h": 6.1, "i": 7.0, "j": 0.15, "k": 0.77, "l": 4.0, "m": 2.4, "n": 6.7,
    "o": 7.5, "p": 1.9, "q": 0.095, "r": 6.0, "s": 6.3, "t": 9.1, "u": 2.8,
    "v": 0.98, "w": 2.4, "x": 0.15, "y": 2.0, "z": 0.074,
}


def caesar(text: str, shift: int) -> str:
    out = []
    for char in text:
        if char.islower():
            out.append(chr((ord(char) - 97 + shift) % 26 + 97))
        elif char.isupper():
            out.append(chr((ord(char) - 65 + shift) % 26 + 65))
        else:
            out.append(char)
    return "".join(out)


def chi_squared(text: str) -> float:
    letters = [c for c in text.lower() if c.isalpha()]
    if not letters:
        return float("inf")
    counts = Counter(letters)
    total = len(letters)
    return sum(((counts[ch] / total * 100) - freq) ** 2 / freq
               for ch, freq in ENGLISH_FREQ.items())


def break_caesar(ciphertext: str) -> tuple[int, str]:
    _, shift = min((chi_squared(caesar(ciphertext, -s)), s) for s in range(26))
    return shift, caesar(ciphertext, -shift)
```
Chi-squared measures how far the observed letter distribution sits from English; the correct
shift produces ordinary English and therefore the lowest score. `min()` over a generator of
`(score, shift)` pairs gives you the answer without any bookkeeping. This is also a good lesson
in limits: on a twenty-word sentence the method picks the wrong shift more often than not, so
always eyeball the top few candidates rather than trusting the winner blindly.
:::

## Data structures

### 13. Two-sum

The single most common interview warm-up, and a real pattern: find a complement instead of
comparing everything with everything.

Write `two_sum(nums: list[int], target: int) -> tuple[int, int] | None` returning the indices of
two distinct values that add to `target`, or `None`. It must run in one pass — O(n), not O(n²).

```python
>>> two_sum([2, 7, 11, 15], 9)
(0, 1)
>>> two_sum([1, 2], 9) is None
True
```

:::tip Hint
Walk the list once, storing `value -> index` in a dict. Before you store a value, check whether
`target - value` is already in the dict. Checking backwards means you never pair an element with
itself.
:::

### 14. Inverting a mapping

You have `code -> country` and you need `country -> [codes]`, because several codes share a
country.

Write `invert(mapping: dict) -> dict` where every value maps to the sorted list of keys that had
it. Keys are strings; values are hashable.

```python
>>> invert({"a": 1, "b": 2, "c": 1})
{1: ['a', 'c'], 2: ['b']}
```

:::tip Hint
`collections.defaultdict(list)` lets you `append` without checking whether the key exists. Sort
each list at the end so the output is deterministic.
:::

### 15. Grouping anagrams

A word game, and also how you deduplicate records that differ only by ordering.

Write `group_anagrams(words: list[str]) -> list[list[str]]`. Case-insensitive. Return the groups
with each group sorted, and the groups themselves ordered by their first (alphabetically
smallest) member.

```python
>>> group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
[['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]
```

:::tip Hint
Anagrams share a canonical key: `tuple(sorted(word.lower()))`. Use that as a dict key — lists
cannot be dict keys, tuples can.
:::

### 16. Flattening nested lists

Hard. JSON from third parties nests unpredictably, and sometimes you want to stop at a certain
level.

Write `flatten(nested, max_depth: int | None = None)` as a generator yielding scalar values.
Strings and other non-lists count as scalars and are yielded whole — never iterate a string into
characters. `max_depth` is how many levels to descend: `0` yields the input unchanged, `1`
descends one level, and `None` (the default) flattens completely.

```python
>>> data = [1, [2, [3, [4]]], [[5]]]
>>> list(flatten(data))
[1, 2, 3, 4, 5]
>>> list(flatten(data, max_depth=1))
[1, [2, [3, [4]]], [[5]]]
```

:::tip Hint
`yield from` is recursion for generators. Keep a private `_depth` parameter that you increment
on each recursive call, and yield the list itself when you have reached the limit.
:::

### 17. An LRU cache

Hard. Caches appear in every service you will ever write, and a cache that grows without bound
is a memory leak with good intentions.

Write `LRUCache(capacity: int)` with `get(key) -> int | None` and `put(key, value) -> None`.
`get` returns the value or `None` if absent, and counts as a use. When `put` would exceed
capacity, evict the least recently used entry. Both operations must be O(1). Support `len()`.

```python
>>> c = LRUCache(2)
>>> c.put("a", 1); c.put("b", 2)
>>> c.get("a")          # "a" is now the most recently used
1
>>> c.put("c", 3)       # evicts "b"
>>> c.get("b") is None
True
>>> c.get("a")
1
```

:::tip Hint
`collections.OrderedDict` remembers insertion order and gives you `move_to_end(key)` and
`popitem(last=False)` — eviction of the oldest entry. That is the entire implementation;
anything involving `min()` over timestamps is O(n) and therefore wrong.
:::

:::solution Solution 13
```python
def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    seen: dict[int, int] = {}                 # value -> index
    for index, value in enumerate(nums):
        if (needed := target - value) in seen:
            return seen[needed], index
        seen[value] = index
    return None
```
The walrus operator keeps the complement calculation inline without a second lookup. Because you
check before inserting, `[3]` with target 6 correctly returns `None` instead of pairing the
element with itself.
:::

:::solution Solution 14
```python
from collections import defaultdict


def invert(mapping: dict) -> dict:
    out: defaultdict = defaultdict(list)
    for key, value in mapping.items():
        out[value].append(key)
    return {value: sorted(keys) for value, keys in out.items()}
```
`defaultdict(list)` removes the "does this key exist yet?" branch. Sorting in the final
comprehension makes the result reproducible — unsorted output from a dict is a common source of
tests that pass locally and fail in CI.
:::

:::solution Solution 15
```python
from collections import defaultdict


def group_anagrams(words: list[str]) -> list[list[str]]:
    buckets: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for word in words:
        buckets[tuple(sorted(word.lower()))].append(word)
    groups = [sorted(group) for group in buckets.values()]
    return sorted(groups, key=lambda group: group[0])
```
The canonical key is the whole trick: sorting the letters makes `eat`, `tea`, and `ate` produce
the identical key, so grouping is one dict lookup per word — O(n · m log m) instead of comparing
every pair.
:::

:::solution Solution 16
```python
from collections.abc import Iterator


def flatten(nested, max_depth: int | None = None, _depth: int = 0) -> Iterator:
    if isinstance(nested, list):
        if max_depth is not None and _depth >= max_depth:
            yield nested                       # stop here: hand back the rest untouched
            return
        for item in nested:
            yield from flatten(item, max_depth, _depth + 1)
    else:
        yield nested                           # strings, numbers, None: all scalars
```
`isinstance(nested, list)` rather than "is it iterable" is deliberate — a `str` is iterable, and
the classic bug in hand-written flatteners is recursing into strings and yielding single
characters forever. The leading underscore on `_depth` tells callers it is internal.
:::

:::solution Solution 17
```python
from collections import OrderedDict


class LRUCache:
    """Fixed-capacity cache that evicts the least recently used entry."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._data: OrderedDict[str, int] = OrderedDict()

    def get(self, key: str) -> int | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)            # mark as most recently used
        return self._data[key]

    def put(self, key: str, value: int) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)     # evict the oldest

    def __len__(self) -> int:
        return len(self._data)
```
`OrderedDict` maintains a linked list of keys internally, so both `move_to_end` and
`popitem(last=False)` are O(1) — you get a correct LRU without writing a single pointer. Note
that `put` on an existing key must also move it to the end, otherwise an overwrite does not
count as a use.
:::

### 18. Topological sort

Hard. Build systems, task runners, database migrations, and package managers all need to order
things that depend on each other — and to tell you when the dependencies are impossible.

Write `topo_sort(tasks: dict[str, set[str]]) -> list[str]`, where each key is a task and its
value is the set of tasks it depends on. Return an order in which every task appears after all of
its dependencies. If there is a cycle, raise `ValueError` naming the tasks involved. If a
dependency is not a known task, raise `ValueError` too. The output must be deterministic:
among tasks that are ready at the same time, take them alphabetically.

```python
>>> topo_sort({"deploy": {"build"}, "build": {"test"}, "test": set(), "lint": {"test"}})
['test', 'build', 'deploy', 'lint']
>>> topo_sort({"a": {"b"}, "b": {"a"}})
ValueError: cycle detected among: a, b
```

:::tip Hint
Kahn's algorithm: repeatedly take every task with no remaining dependencies. A `heapq` gives you
the alphabetically smallest ready task in O(log n) and makes the output deterministic. If the
result has fewer entries than the input, whatever is left is inside a cycle.
:::

:::solution Solution 18
```python
import heapq


def topo_sort(tasks: dict[str, set[str]]) -> list[str]:
    remaining = {name: set(deps) for name, deps in tasks.items()}

    for name, deps in remaining.items():
        if unknown := deps - tasks.keys():
            raise ValueError(f"{name} depends on unknown tasks: {sorted(unknown)}")

    ready = [name for name, deps in remaining.items() if not deps]
    heapq.heapify(ready)

    order: list[str] = []
    while ready:
        name = heapq.heappop(ready)
        order.append(name)
        for other, deps in remaining.items():
            if name in deps:
                deps.remove(name)
                if not deps:
                    heapq.heappush(ready, other)

    if len(order) != len(tasks):
        stuck = sorted(set(tasks) - set(order))
        raise ValueError("cycle detected among: " + ", ".join(stuck))
    return order
```
Copying each dependency set (`set(deps)`) is essential — mutating the caller's sets would corrupt
their data. The length check at the end is the cycle detector: if some tasks never became ready,
they were waiting on each other, and the ones missing from `order` are exactly the members of the
cycle.
:::

## Files, data & APIs

### 19. Counting lines in a project

You want to know how big the thing you just built is — and which files are doing the work.

Write `count_lines(root: Path, pattern: str = "*.py", *,
exclude: tuple[str, ...] = (".venv", "__pycache__", ".git")) -> dict[str, int]` returning
`{"files": n, "total": n, "code": n}`, where `total` is every line and `code` excludes blank
lines and lines whose first non-space character is `#`. Skip any path containing an excluded
directory name. Open files with an explicit UTF-8 encoding and replace undecodable bytes rather
than crashing.

```text
$ python3 countlines.py ~/python-mastery
files=42 total=3901 code=2874
```

:::tip Hint
`Path.rglob(pattern)` walks recursively. Filter with `any(part in exclude for part in
path.parts)`, then `path.read_text(encoding="utf-8", errors="replace").splitlines()`.
:::

### 20. CSV in, JSON out

Combines Chapters 8 (files), 11 (dicts), 14 (JSON), and 17 (tests) — the most common shape of
real Python work.

Write `summarise(source: Path, destination: Path) -> dict`. Read a CSV with columns
`order_id,category,amount`, sum the amounts per category with `Decimal`, and write a JSON report
containing the source filename, the number of orders, the categories sorted by total descending
(each with its total and its percentage share of revenue as a string), and the grand total.
Return the same dict you wrote.

```text
order_id,category,amount
1,books,19.99
2,books,5.00
3,toys,12.50
4,books,10.01
5,toys,7.49
```

```json
{
  "source": "orders.csv",
  "orders": 5,
  "categories": [
    {"category": "books", "total": "35.00", "share": "63.6%"},
    {"category": "toys", "total": "19.99", "share": "36.4%"}
  ],
  "grand_total": "54.99"
}
```

:::tip Hint
`csv.DictReader` plus `collections.defaultdict(lambda: Decimal("0.00"))`. Money is `Decimal` in
the calculation and `str(...)` in the JSON — `json` cannot serialise `Decimal`, and you do not
want a float in a financial report.
:::

### 21. A left join on two CSVs

Orders reference customers by ID. Some of those IDs do not exist any more, and silently dropping
those rows is how reports stop reconciling.

Write `left_join(rows: list[dict], lookup: list[dict], key: str, foreign_key: str) ->
tuple[list[dict], list[dict]]`. Every row in `rows` appears at least once, enriched with the
matching record's other fields; if a lookup value has several matches, emit one output row per
match. Rows with no match are returned separately as orphans rather than being dropped.

```python
>>> orders = [{"order_id": "10", "customer_id": "1", "total": "50.00"},
...           {"order_id": "13", "customer_id": "99", "total": "5.00"}]
>>> customers = [{"id": "1", "name": "Ada"}, {"id": "2", "name": "Grace"}]
>>> joined, orphans = left_join(orders, customers, "id", "customer_id")
>>> joined
[{'order_id': '10', 'customer_id': '1', 'total': '50.00', 'name': 'Ada'}]
>>> orphans
[{'order_id': '13', 'customer_id': '99', 'total': '5.00'}]
```

:::tip Hint
Index the lookup side first (`defaultdict(list)` of matches) so the join is O(n + m) rather than
a nested loop. When merging the two dicts, drop the join key from the lookup record so it does
not overwrite the foreign key.
:::

### 22. Fetching an API without hammering it

Every integration you write eventually needs this: a timeout, a retry, and a cache.

Write `fetch_json(url: str, *, cache_dir: Path = Path(".cache"), ttl: float = 300.0) -> dict`.
Return the parsed JSON. Use a `requests.Session` with a connect-and-read timeout. On a timeout or
a 5xx response, retry with exponential backoff and jitter, at most four attempts. Cache
successful responses in `cache_dir` keyed by a hash of the URL, and serve the cached copy while
it is younger than `ttl` — or if the network fails entirely and a cached copy exists at all.

```python
>>> fetch_json("https://api.github.com/repos/python/cpython")["full_name"]
'python/cpython'
>>> fetch_json("https://api.github.com/repos/python/cpython")   # second call: no network
{'full_name': 'python/cpython', ...}
```

:::tip Hint
`hashlib.sha256(url.encode()).hexdigest()` gives you a safe filename. Store `{"fetched_at":
time.time(), "payload": ...}` so you can check freshness, and use `os.replace` for the cache
write so a crashed process never leaves half a cache file behind.
:::

### 23. An incremental pipeline with state

Hard. Combines files, JSON, testing, and the idempotency habit from Chapter 37. Nightly jobs
must not reprocess everything every night.

Write `run_pipeline(source: Path, destination: Path, state: Path) -> dict`. The source CSV has
`id,user,amount`. Read the last processed id from the state file (`{"last_id": n}`, treated as 0
if missing), process only rows with a strictly greater id, add their amounts to the per-user
totals already in `destination`, write both files back, and return
`{"processed": n, "last_id": n, "totals": {...}}`. Running it twice in a row must process zero
rows the second time. Then write two pytest tests using `tmp_path`: one that two consecutive
runs give the same totals as one run, and one that a row added later is picked up.

```text
id,user,amount
1,u1,10
2,u2,20
3,u1,5
```

```python
>>> run_pipeline(src, dest, state)
{'processed': 3, 'last_id': 3, 'totals': {'u1': '15.00', 'u2': '20.00'}}
>>> run_pipeline(src, dest, state)      # nothing new
{'processed': 0, 'last_id': 3, 'totals': {'u1': '15.00', 'u2': '20.00'}}
```

:::tip Hint
Make the state file the source of truth and write it only after the output file is safely
written — if you write state first, a crash between the two loses rows forever. `Decimal` for the
amounts, `str()` for the JSON.
:::

### 24. A searchable index over a folder

Hard. Combines file walking, sets, JSON persistence, and a CLI. This is a tiny version of what
real search does.

Build `Index` with `add(name: str, text: str)`, `build_from(folder: Path)`, and
`search(query: str) -> set[str]`, plus `save(path)` / `load(path)` that persist the postings as
JSON (sets become sorted lists on disk). `search` supports `AND` (default within a group),
`OR` between groups, and `-word` for negation. Then wire it to an `argparse` CLI:
`index.py build <folder>` and `index.py search "cat -dog"`.

```python
>>> index = Index().build_from(Path("docs"))
>>> index.search("cat")
{'a.txt', 'b.txt'}
>>> index.search("cat AND dog")
{'b.txt'}
>>> index.search("dog -cat")
{'c.txt'}
```

:::tip Hint
Split the query on whitespace, then split it into OR-groups; within a group, start with `None`
for "not yet constrained" and intersect each term's posting set. Negation is `all_documents -
postings[word]`, so you need to track the document set as you build.
:::

:::solution Solution 19
```python
from pathlib import Path


def count_lines(root: Path, pattern: str = "*.py", *,
                exclude: tuple[str, ...] = (".venv", "__pycache__", ".git")) -> dict[str, int]:
    files = total = code = 0
    for path in sorted(root.rglob(pattern)):
        if any(part in exclude for part in path.parts):
            continue
        files += 1
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            total += 1
            if line.strip() and not line.lstrip().startswith("#"):
                code += 1
    return {"files": files, "total": total, "code": code}


if __name__ == "__main__":
    import sys
    stats = count_lines(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    print(stats)
```
`errors="replace"` matters more than it looks: one file saved as Latin-1 would otherwise abort
the whole run. `sorted()` around `rglob` gives stable output so you can diff two runs.
:::

:::solution Solution 20
```python
import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

CENT = Decimal("0.01")


def summarise(source: Path, destination: Path) -> dict:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    orders = 0

    with source.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            totals[row["category"]] += Decimal(row["amount"])
            orders += 1

    grand_total = sum(totals.values(), Decimal("0.00"))
    report = {
        "source": source.name,
        "orders": orders,
        "categories": [
            {
                "category": category,
                "total": str(total.quantize(CENT)),
                "share": f"{total / grand_total * 100:.1f}%",
            }
            for category, total in sorted(totals.items(), key=lambda kv: -kv[1])
        ],
        "grand_total": str(grand_total.quantize(CENT)),
    }

    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
```
`Decimal` throughout and `str()` at the JSON boundary: `json` would either refuse to serialise a
`Decimal` or (with a custom encoder) silently turn it into a float, which reintroduces the error
you were avoiding. Writing the file with an explicit encoding is not optional — see Chapter 37.
:::

:::solution Solution 21
```python
from collections import defaultdict


def left_join(rows: list[dict], lookup: list[dict], key: str, foreign_key: str):
    index: dict[str, list[dict]] = defaultdict(list)
    for record in lookup:
        index[record[key]].append(record)

    joined: list[dict] = []
    orphans: list[dict] = []
    for row in rows:
        matches = index.get(row[foreign_key])
        if not matches:
            orphans.append(row)                     # do not lose data silently
            continue
        for match in matches:
            extras = {k: v for k, v in match.items() if k != key}
            joined.append({**row, **extras})
    return joined, orphans
```
Building the index first makes this linear; the naive nested loop is quadratic and will fall over
at a few hundred thousand rows. Returning orphans separately is the point of the exercise — a
join that drops unmatched rows produces totals nobody can reconcile.
:::

:::solution Solution 22
```python
import hashlib
import json
import os
import random
import time
from pathlib import Path

import requests


def _cache_file(cache_dir: Path, url: str) -> Path:
    return cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"


def _atomic_write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    os.replace(tmp, path)


def fetch_json(url: str, *, cache_dir: Path = Path(".cache"), ttl: float = 300.0) -> dict:
    cache_path = _cache_file(cache_dir, url)
    now = time.time()

    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if now - cached["fetched_at"] < ttl:
            return cached["payload"]
    else:
        cached = None

    last_error: Exception | None = None
    with requests.Session() as session:             # connection pooling, one session
        for attempt in range(4):
            try:
                response = session.get(url, timeout=(3.05, 10))
                if response.status_code >= 500:
                    raise requests.HTTPError(f"server error {response.status_code}")
                response.raise_for_status()
                payload = response.json()
                _atomic_write_json(cache_path, {"fetched_at": now, "payload": payload})
                return payload
            except (requests.Timeout, requests.HTTPError) as exc:
                last_error = exc
                time.sleep(random.uniform(0, 0.5 * 2 ** attempt))   # backoff + jitter

    if cached is not None:                          # degraded, but not broken
        return cached["payload"]
    raise RuntimeError(f"{url} unavailable") from last_error
```
Four things are non-negotiable in any HTTP client: a timeout (an unbounded wait is a leak), a
retry policy with jitter (without jitter every worker retries in lockstep), a cache (the cheapest
request is the one you do not make), and a stale-but-usable path when the network is down.
:::

:::solution Solution 23
```python
import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

CENT = Decimal("0.01")


def load_state(path: Path) -> int:
    if not path.exists():
        return 0
    return int(json.loads(path.read_text(encoding="utf-8")).get("last_id", 0))


def run_pipeline(source: Path, destination: Path, state: Path) -> dict:
    last_id = load_state(state)

    deltas: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    new_last = last_id
    with source.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row_id = int(row["id"])
            if row_id <= last_id:                   # already accounted for
                continue
            deltas[row["user"]] += Decimal(row["amount"])
            new_last = max(new_last, row_id)

    previous = json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else {}
    merged = {user: Decimal(amount) for user, amount in previous.items()}
    for user, amount in deltas.items():
        merged[user] = merged.get(user, Decimal("0.00")) + amount

    totals = {user: str(total.quantize(CENT)) for user, total in sorted(merged.items())}
    destination.write_text(json.dumps(totals, indent=2), encoding="utf-8")
    state.write_text(json.dumps({"last_id": new_last}), encoding="utf-8")   # state goes last

    return {"processed": len(deltas), "last_id": new_last, "totals": totals}
```

```python
# test_pipeline.py
from decimal import Decimal
from pathlib import Path


def test_running_twice_is_the_same_as_running_once(tmp_path: Path):
    src = tmp_path / "events.csv"
    src.write_text("id,user,amount\n1,u1,10\n2,u2,20\n", encoding="utf-8")
    dest, state = tmp_path / "totals.json", tmp_path / "state.json"

    first = run_pipeline(src, dest, state)
    second = run_pipeline(src, dest, state)

    assert first["totals"] == {"u1": "10.00", "u2": "20.00"}
    assert second["processed"] == 0                 # idempotent
    assert second["totals"] == first["totals"]


def test_new_rows_are_picked_up(tmp_path: Path):
    src = tmp_path / "events.csv"
    src.write_text("id,user,amount\n1,u1,10\n", encoding="utf-8")
    dest, state = tmp_path / "totals.json", tmp_path / "state.json"

    run_pipeline(src, dest, state)
    src.write_text("id,user,amount\n1,u1,10\n2,u1,5\n", encoding="utf-8")
    result = run_pipeline(src, dest, state)

    assert result["totals"] == {"u1": "15.00"}
```
Ordering is the whole design: output first, state second. If you reverse it, a crash between the
two writes means the rows are skipped for ever. `tmp_path` gives each test its own filesystem, so
the tests cannot contaminate each other — the same principle as the flaky-test fix in Chapter 37.
:::

:::solution Solution 24
```python
import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

WORD = re.compile(r"[a-z]+")


@dataclass
class Index:
    postings: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    documents: set[str] = field(default_factory=set)

    def add(self, name: str, text: str) -> None:
        self.documents.add(name)
        for word in WORD.findall(text.lower()):
            self.postings[word].add(name)

    def build_from(self, folder: Path) -> "Index":
        for path in sorted(folder.glob("*.txt")):
            self.add(path.name, path.read_text(encoding="utf-8"))
        return self

    def search(self, query: str) -> set[str]:
        groups: list[list[str]] = [[]]
        for token in query.split():
            if token == "OR":
                groups.append([])
            elif token == "AND":
                continue
            else:
                groups[-1].append(token.lower())

        found: set[str] = set()
        for group in groups:
            hits: set[str] | None = None
            for token in group:
                negated = token.startswith("-")
                matches = set(self.postings.get(token.lstrip("-"), ()))
                if negated:
                    matches = self.documents - matches
                hits = matches if hits is None else hits & matches
            found |= hits or set()
        return found

    def save(self, path: Path) -> None:
        path.write_text(json.dumps({
            "documents": sorted(self.documents),
            "postings": {w: sorted(d) for w, d in sorted(self.postings.items())},
        }, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Index":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(postings=defaultdict(set, {w: set(d) for w, d in data["postings"].items()}),
                   documents=set(data["documents"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Search a folder of text files.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("folder", type=Path)
    build.add_argument("-o", "--output", type=Path, default=Path("index.json"))

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("-i", "--index", type=Path, default=Path("index.json"))

    args = parser.parse_args()
    if args.command == "build":
        Index().build_from(args.folder).save(args.output)
        print(f"indexed into {args.output}")
    else:
        print("\n".join(sorted(Index.load(args.index).search(args.query))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
Sets are the right structure for postings because search is set algebra: AND is `&`, OR is `|`,
NOT is `-`. JSON has no set type, so persistence converts to sorted lists — sorted so the file is
diffable and reproducible.
:::

## Design & refactoring

### 25. Extracting a long function

The registration endpoint has grown to sixty lines: it reads the payload, validates the email,
looks up a plan price, saves a row, sends an email, and returns a dict. Nothing in it can be
tested without a database and an SMTP server.

Refactor it. Produce: a frozen `Registration` dataclass built by a `from_payload` classmethod
that raises `ValueError` with a specific message on bad input; a pure `price_for(plan, seats)`
using `Decimal`; and a `register(registration, store, mailer)` coordinator that takes its
collaborators as arguments. The point is that the business logic is now testable with no I/O at
all.

```python
>>> reg = Registration.from_payload({"email": " ADA@Example.com ", "plan": "team", "seats": "3"})
>>> reg.email, price_for(reg.plan, reg.seats)
('ada@example.com', Decimal('36.00'))
>>> register(reg, FakeStore(), FakeMailer())
Decimal('36.00')
```

:::tip Hint
Keep `price_for` pure — no I/O, no globals, just arguments in and a value out. Pass `store` and
`mailer` into `register` instead of importing them; that is dependency injection, and it is what
lets the test pass fakes.
:::

### 26. Swapping the storage layer

Hard. Prototypes use a dict, production uses SQLite, and the day you switch should not be a
rewrite.

Define a `TaskStore` Protocol with `add(title) -> int`, `list_open() -> list[tuple[int, str]]`,
and `complete(task_id) -> None`. Write `InMemoryTaskStore` and `SqliteTaskStore` implementing it.
Write `add_two(store)` — a business helper that only knows the Protocol — then write a single
pytest test that runs the same assertions against both implementations using a parametrised
fixture over `[InMemoryTaskStore, lambda: SqliteTaskStore(tmp_path / "t.db")]`.

```python
>>> add_two(InMemoryTaskStore())
[(1, 'write chapter'), (2, 'run tests')]
>>> add_two(SqliteTaskStore(Path("t.db")))
[(1, 'write chapter'), (2, 'run tests')]
```

:::tip Hint
`typing.Protocol` gives you structural typing: a class satisfies it by having the right methods,
without inheriting anything. In the fixture, yield the store and close the SQLite connection
afterwards so the test does not leak file handles.
:::

### 27. Killing flakiness by injection

Hard. A digest job picks "yesterday's highlights" at random and stamps the date on the email.
Its tests pass on your laptop and fail on the build server after 6 p.m.

Refactor `NightlyDigest` so that the current date and the source of randomness are constructor
arguments, not global lookups. Then write three tests that are deterministic: the same seed gives
the same output twice; a fixed clock is reflected in the header; and a Digest built on a Sunday
says "weekend edition".

```python
>>> digest = NightlyDigest(["a@b.c"], clock=lambda: date(2025, 3, 4), rng=random.Random(7))
>>> digest.build() == digest.build()
True
>>> digest.build().splitlines()[0]
'Digest for 2025-03-04'
```

:::tip Hint
Type the clock as `Callable[[], date]` and default it to `date.today` so production code changes
nothing. Seed a `random.Random(7)` instance rather than using the module-level `random` — global
seeding leaks between tests.
:::

### 28. Replacing a dispatch chain with a registry

Every new export format means opening `exporter.py` and adding another `elif`. That file has been
edited eleven times this quarter.

Refactor to a registry: a `REGISTRY: dict[str, Callable[[list[dict]], str]]` and a `register(name)`
decorator that adds a function to it. Write `export(rows, fmt)` that looks the format up and
raises `ValueError` listing the known formats when it is unknown. Provide `csv` and `json`
exporters, then show how a third (`html`) is added without touching `export` or `REGISTRY`
yourself — a plugin, in the literal sense.

```python
>>> export([{"a": 1}], "json")
'[{"a": 1}]'
>>> export([{"a": 1}], "yaml")
ValueError: unknown format 'yaml'; choose from ['csv', 'json']
```

:::tip Hint
A decorator is a function returning a function: `def register(name): ... return decorator`, and
`decorator` stores `fn` and returns it unchanged. Registering at import time means the module
that defines the format is the only file that knows about it.
:::

### 29. A Money value object

Hard. Floats for currency have already cost your company a reconciliation day.

Write `Money` as a value object: `Money(amount, currency="GBP")` stores a `Decimal` quantised to
two decimal places, and `currency` is a three-letter string. Support `+` (same currency only,
otherwise `ValueError`), `* int | Decimal` (quantised), `==`, `hash`, and a useful `repr`.
`allocate(n)` splits the amount into `n` parts that sum exactly to the original, handing the
remainder out a penny at a time. Reject `float` construction loudly.

```python
>>> Money("10.00").allocate(3)
[Money('3.34', 'GBP'), Money('3.33', 'GBP'), Money('3.33', 'GBP')]
>>> Money("19.99") * 3
Money('59.97', 'GBP')
>>> Money("10.00") + Money("5.00", "USD")
ValueError: cannot combine Money('10.00', 'GBP') with Money('5.00', 'USD')
```

:::tip Hint
Work in integer pennies for `allocate`: `base, remainder = divmod(int(amount * 100), n)`, then add
a penny to the first `remainder` parts. That guarantees the parts sum to the original — which
repeated `quantize()` does not.
:::

### 30. An event bus

Hard. Plugins should be able to react to things without the core importing them, and one broken
plugin must not take down the application.

Write `EventBus` with `subscribe(event: str, handler) -> None` and `emit(event: str, **payload)
-> int` returning how many handlers ran successfully. Hold subscribers weakly so a subscriber can
be garbage collected without unsubscribing — use `weakref.WeakMethod` for bound methods and
`weakref.ref` for plain functions, and drop dead references as you discover them. A handler that
raises must be logged with `logger.exception` and must not prevent the remaining handlers from
running.

```python
>>> bus = EventBus()
>>> bus.subscribe("saved", auditor.on_change)     # bound method: held weakly
>>> bus.subscribe("saved", broken_handler)        # raises
>>> bus.emit("saved", name="report.csv")          # the auditor still runs
1
```

:::tip Hint
`weakref.WeakMethod(handler)` returns a callable that gives you the bound method back or `None`
once the object is gone; check `hasattr(handler, "__self__")` to tell bound methods from plain
functions. Wrap each call in `try/except Exception` and log with `logger.exception`, which
captures the traceback for free.
:::

:::solution Solution 25
```python
from dataclasses import dataclass
from decimal import Decimal

PLAN_PRICES = {"free": Decimal("0.00"), "team": Decimal("12.00"), "enterprise": Decimal("29.00")}


@dataclass(frozen=True)
class Registration:
    email: str
    plan: str
    seats: int

    @classmethod
    def from_payload(cls, payload: dict) -> "Registration":
        email = payload.get("email", "").strip().lower()
        if "@" not in email:
            raise ValueError(f"invalid email: {payload.get('email')!r}")
        plan = payload.get("plan", "").strip().lower()
        if plan not in PLAN_PRICES:
            raise ValueError(f"unknown plan {plan!r}; choose from {sorted(PLAN_PRICES)}")
        try:
            seats = int(payload.get("seats", 1))
        except (TypeError, ValueError):
            raise ValueError(f"seats must be a number, got {payload.get('seats')!r}") from None
        if seats < 1:
            raise ValueError("seats must be >= 1")
        return cls(email=email, plan=plan, seats=seats)


def price_for(plan: str, seats: int) -> Decimal:
    """Pure: same input, same output, no I/O, trivially testable."""
    return (PLAN_PRICES[plan] * seats).quantize(Decimal("0.01"))


def register(registration: Registration, store, mailer) -> Decimal:
    total = price_for(registration.plan, registration.seats)
    store.save(registration.email, registration.plan, registration.seats, total)
    mailer.send_welcome(registration.email)
    return total
```
Every piece is now testable in isolation: `from_payload` with a dict, `price_for` with two
arguments, `register` with two fakes. The original function's sixty lines contained all three
concerns tangled together, which is why nobody dared touch it.
:::

:::solution Solution 26
```python
import sqlite3
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest


@runtime_checkable
class TaskStore(Protocol):
    def add(self, title: str) -> int: ...
    def list_open(self) -> list[tuple[int, str]]: ...
    def complete(self, task_id: int) -> None: ...


class InMemoryTaskStore:
    def __init__(self) -> None:
        self._rows: list[dict] = []
        self._next_id = 1

    def add(self, title: str) -> int:
        task_id = self._next_id
        self._next_id += 1
        self._rows.append({"id": task_id, "title": title, "done": False})
        return task_id

    def list_open(self) -> list[tuple[int, str]]:
        return [(r["id"], r["title"]) for r in self._rows if not r["done"]]

    def complete(self, task_id: int) -> None:
        for row in self._rows:
            if row["id"] == task_id:
                row["done"] = True
                return
        raise KeyError(task_id)


class SqliteTaskStore:
    def __init__(self, path: Path) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks "
            "(id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)"
        )

    def add(self, title: str) -> int:
        cursor = self._conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        self._conn.commit()
        return cursor.lastrowid

    def list_open(self) -> list[tuple[int, str]]:
        return self._conn.execute(
            "SELECT id, title FROM tasks WHERE done = 0 ORDER BY id"
        ).fetchall()

    def complete(self, task_id: int) -> None:
        self._conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        self._conn.commit()


def add_two(store: TaskStore) -> list[tuple[int, str]]:
    """Business code that depends only on the Protocol, never on a concrete class."""
    store.add("write chapter")
    store.add("run tests")
    return store.list_open()


@pytest.fixture(params=["memory", "sqlite"])
def store(request, tmp_path: Path):
    if request.param == "memory":
        yield InMemoryTaskStore()
    else:
        sqlite = SqliteTaskStore(tmp_path / "tasks.db")
        yield sqlite
        sqlite._conn.close()      # fixtures clean up after themselves


def test_add_two_lists_both_tasks(store: TaskStore):
    assert add_two(store) == [(1, "write chapter"), (2, "run tests")]


def test_completing_removes_from_open(store: TaskStore):
    task_id = store.add("ship it")
    store.complete(task_id)
    assert store.list_open() == []
```
Protocol-based design inverts the dependency: `add_two` names what it *needs*, not what exists.
The parametrised fixture is the payoff — one test, two storage backends, and the guarantee that
swapping them in production changes nothing.
:::

:::solution Solution 27
```python
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
import random


@dataclass
class NightlyDigest:
    recipients: list[str]
    clock: Callable[[], date] = date.today          # injected, defaulted for production
    rng: random.Random = field(default_factory=random.Random)

    HEADER = "Digest for {:%Y-%m-%d}"

    def build(self) -> str:
        today = self.clock()
        title = "Weekend edition" if today.weekday() >= 5 else self.HEADER.format(today)
        highlights = self.rng.sample(self.HIGHLIGHTS, 3)
        return "\n".join([title, *highlights, f"sent to {len(self.recipients)} recipients"])

    HIGHLIGHTS = [
        "orders up 4%", "3 new signups", "churn flat", "latency down 12ms",
        "invoice #4021 paid", "support backlog cleared",
    ]
```

```python
# test_digest.py
from datetime import date
import random
from digest import NightlyDigest


def build(day: date, seed: int = 7) -> NightlyDigest:
    return NightlyDigest(["a@b.c"], clock=lambda: day, rng=random.Random(seed))


def test_same_seed_is_reproducible():
    assert build(date(2025, 3, 4)).build() == build(date(2025, 3, 4)).build()


def test_header_uses_the_injected_clock():
    assert build(date(2025, 3, 4)).build().splitlines()[0] == "Digest for 2025-03-04"


def test_sunday_is_a_weekend_edition():
    assert build(date(2025, 3, 9)).build().splitlines()[0] == "Weekend edition"
```
The refactor is one line of production code (`clock: Callable[[], date] = date.today`) and it
removes the entire class of failure. Global state — `datetime.now()`, module-level `random`,
"today" — is what makes tests depend on the wall clock; passing it in makes "now" just another
argument.
:::

:::solution Solution 28
```python
import csv
import io
import json
from collections.abc import Callable

Handler = Callable[[list[dict]], str]
REGISTRY: dict[str, Handler] = {}


def register(name: str):
    """Attach a format handler to the registry. Importing the module is enough."""
    def decorator(fn: Handler) -> Handler:
        if name in REGISTRY:
            raise ValueError(f"{name} is already registered by {REGISTRY[name]!r}")
        REGISTRY[name] = fn
        return fn
    return decorator


@register("csv")
def to_csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


@register("json")
def to_json(rows: list[dict]) -> str:
    return json.dumps(rows, indent=2)


def export(rows: list[dict], fmt: str) -> str:
    try:
        handler = REGISTRY[fmt]
    except KeyError:
        raise ValueError(f"unknown format {fmt!r}; choose from {sorted(REGISTRY)}") from None
    return handler(rows)
```

```python
# exporters/html.py — a third format, added without editing exporter.py
from exporter import register

@register("html")
def to_html(rows: list[dict]) -> str:
    header = "".join(f"<th>{key}</th>" for key in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>" for row in rows)
    return f"<table><tr>{header}</tr>{body}</table>"
```
`export` no longer knows how many formats exist, so it never needs editing again — the
open/closed principle in twelve lines. Rejecting duplicate registrations turns a confusing "my
export silently changed" bug into a loud import-time error.
:::

:::solution Solution 29
```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "GBP"

    def __post_init__(self) -> None:
        if isinstance(self.amount, float):
            raise TypeError("Money takes str, int or Decimal — never float")
        if len(self.currency) != 3:
            raise ValueError(f"currency must be a 3-letter code, got {self.currency!r}")
        # frozen dataclasses cannot assign normally; object.__setattr__ is the escape hatch
        object.__setattr__(self, "amount", Decimal(self.amount).quantize(CENT, ROUND_HALF_UP))

    def __add__(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor) -> "Money":
        return Money((self.amount * Decimal(factor)).quantize(CENT, ROUND_HALF_UP), self.currency)

    def _same_currency(self, other: "Money") -> None:
        if not isinstance(other, Money) or other.currency != self.currency:
            raise ValueError(f"cannot combine {self!r} with {other!r}")

    def allocate(self, parts: int) -> list["Money"]:
        """Split into `parts` shares that sum exactly to this amount."""
        if parts < 1:
            raise ValueError("parts must be >= 1")
        pennies = int(self.amount * 100)
        base, remainder = divmod(pennies, parts)
        shares = [Money(Decimal(base) / 100, self.currency) for _ in range(parts)]
        for i in range(remainder):                  # hand out the leftover pennies
            shares[i] = shares[i] + Money("0.01", self.currency)
        return shares

    def __str__(self) -> str:
        return f"{self.currency} {self.amount}"
```
```python
>>> Money("10.00").allocate(3)
[Money(amount=Decimal('3.34'), currency='GBP'), Money(amount=Decimal('3.33'), currency='GBP'),
 Money(amount=Decimal('3.33'), currency='GBP')]
```
`allocate` is the reason this object exists: splitting `10.00` three ways with floats gives you
`3.33 + 3.33 + 3.33 = 9.99` and a missing penny. Working in integer pennies and distributing the
remainder makes the parts sum to the original by construction. `frozen=True` gives you equality,
hashing, and immutability — money should never change under you.
:::

:::solution Solution 30
```python
import logging
import weakref
from collections import defaultdict


class EventBus:
    """Publish/subscribe with weak references and fault isolation."""

    def __init__(self) -> None:
        self._handlers: dict[str, list] = defaultdict(list)
        self._log = logging.getLogger("events")

    def subscribe(self, event: str, handler) -> None:
        ref = (weakref.WeakMethod(handler) if hasattr(handler, "__self__")
               else weakref.ref(handler))
        self._handlers[event].append(ref)

    def emit(self, event: str, **payload) -> int:
        delivered = 0
        for ref in list(self._handlers.get(event, ())):     # copy: handlers may unsubscribe
            handler = ref()                                  # None if the target was collected
            if handler is None:
                self._handlers[event].remove(ref)
                continue
            try:
                handler(event, **payload)
                delivered += 1
            except Exception:
                self._log.exception("handler %r failed for %s", handler, event)
        return delivered
```
```python
>>> bus = EventBus()
>>> bus.subscribe("saved", auditor.on_change)   # bound method: held weakly
>>> bus.subscribe("saved", broken_handler)      # raises every time
>>> bus.emit("saved", name="report.csv")        # auditor runs; failure is logged, not raised
1
```
Weak references are what stop an event bus from becoming a memory leak: a long-lived bus holding
strong references to every subscriber keeps dead objects alive for the life of the process.
Catching `Exception` (never bare `except:`) around each call means one broken plugin degrades to a
log line instead of an outage.
:::

## Key takeaways

- Formatting, loops, and conditionals are not "basic" — branch order and `range` boundaries cause real bugs.
- Reach for `Counter`, `defaultdict`, and `OrderedDict` before writing a manual loop; the standard library versions are correct and fast.
- Any time you need "look something up fast", the answer is a dict (or a set): two-sum, joins, anagram grouping, and inverted indexes are the same idea.
- Recursion plus `yield from` handles nested data; guard it with an explicit type check so strings stay whole.
- Determinism is a feature: sort before you return, seed your randomness, inject your clock — tests that depend on ordering or on "now" will fail when you least want them to.
- Money is `Decimal` end to end, split in integer pennies, and never mixed across currencies.
- Passing collaborators in (a store, a mailer, a clock) instead of importing them is what makes code testable, and it is the habit that separates reusable code from one-off scripts.
- A registry, a Protocol, or an event bus removes the need to edit core code when something new arrives — that is the practical meaning of extensible design.
