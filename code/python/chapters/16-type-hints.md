---
chapter: 16
part: 2
title: Type Hints & Static Analysis
summary: Annotate real code, express generics and protocols, and let mypy catch the mistakes your tests never think to make.
minutes: 40
tags: [type hints, mypy, generics, Protocol, TypedDict, pydantic]
---

`def total(prices):` tells you nothing. Is `prices` a list of floats, a dict of sku to quantity, or
a filename? Six months from now you will open that file, squint at the call sites, and guess. Type
hints move that answer into the signature where your editor and a checker can see it, and — the
part that actually pays — they turn a whole class of bug from a 3 a.m. production incident into a
red squiggle. Hints are optional, incremental, and ignored by the interpreter at runtime. Used at
the boundaries of your code, they cost almost nothing and catch the mistakes tests rarely think
to make.

## Annotating the basics

Three places take annotations, and the syntax differs slightly in each:

```python
def total(prices: list[float]) -> float:      # parameter and return
    return sum(prices)

discount: float = 0.1                          # variable
names: list[str] = []                          # variable, with no value yet if you like
```

```python
counts: dict[str, int] = {}                    # declaration + assignment
counts["widget"] = 3
```

A bare annotation with no value is legal and useful: `cache: dict[str, int]` declares the name
for a type checker without creating anything. Parameters use `name: type`, returns use `-> type`
after the closing paren, and everything is available on the function object:

```python
>>> def double(x: int) -> int: ...
>>> double.__annotations__
{'x': <class 'int'>, 'return': <class 'int'>}
```

Annotate **parameters and returns on every public function** first. That is where the payoff is
highest: it is the contract other modules rely on, and it is what your editor shows you in the
autocomplete popup when you call the function from somewhere else.

## Built-in generics

Since Python 3.9 the built-in containers are generic, so you write `list[str]` directly rather
than importing `List` from `typing`:

| Annotation | Means |
|---|---|
| `list[str]` | list of strings |
| `dict[str, int]` | string keys, integer values |
| `tuple[float, float]` | exactly two floats |
| `tuple[int, ...]` | any number of ints (note the `...`) |
| `set[str]` | set of strings |
| `list[dict[str, int]]` | list of string→int dicts |

The `tuple` distinction matters and has no equivalent for lists: `tuple[int, str]` is a
*two*-element tuple of int then str, while `tuple[int, ...]` is a homogeneous tuple of any length.
For heterogeneous fixed-size data, prefer a dataclass (Chapter 13) — it has names.

## Unions, `None`, `Any`, and `Callable`

Since 3.10, `X | Y` is the union operator and it works in annotations:

```python
def find_user(user_id: int) -> dict[str, str] | None:
    ...
```

Write `str | None`, not `Optional[str]`. They mean the same thing; the `|` form is shorter, needs
no import, and reads like English. You will still see `Optional` in older code — know it, do not
write it.

Three more you need:

```python
from typing import Any
from collections.abc import Callable, Iterable, Iterator, Sequence

def load_config(path: str) -> Any:                 # Any: no checking, use sparingly
    ...

Handler = Callable[[str, int], None]               # callable taking (str, int), returning None

def notify(handler: Handler, message: str, code: int) -> None:
    handler(message, code)

def total(values: Iterable[float]) -> float:       # prefers Iterable over list[float]
    return sum(values)
```

`Any` is the escape hatch and it is contagious: a value typed `Any` silently passes every check,
so one `Any` in the middle of a pipeline can hide a real error downstream. Reach for
`object` (which you must narrow before use) or a precise type first, and reserve `Any` for
genuinely dynamic data like parsed JSON.

`Callable[[ArgType, ...], ReturnType]` describes a function value — exactly the functions-as-objects
idea from Chapter 15. `Iterable`, `Iterator`, and `Sequence` come from `collections.abc` and
compose with the iterator protocol from Chapter 14: `Iterable[T]` means "I can loop over it",
`Iterator[T]` means "I can `next()` it", `Sequence[T]` means "indexable and sized". Accepting
`Iterable[float]` instead of `list[float]` makes your function work with generators too, which is
nearly always what you want.

## Type aliases

When an annotation gets long, name it:

```python
from typing import TypeAlias

UserId: TypeAlias = int
Row: TypeAlias = dict[str, str | int | float]
JSON: TypeAlias = "dict[str, JSON] | list[JSON] | str | int | float | bool | None"

def fetch(user_id: UserId) -> Row: ...
```

`TypeAlias` makes the intent explicit to mypy (this is a type, not a variable), and the recursive
`JSON` alias shows the one place you still need quotes: a name that refers to itself.

## `TypeVar`: generic functions and classes

`Any` says "I do not care what this is". A `TypeVar` says "I do not care what this is, **but it is
the same thing on both sides**". That difference is the whole point.

```python
from typing import TypeVar
from collections.abc import Sequence

T = TypeVar("T")

def first(items: Sequence[T]) -> T:
    return items[0]

reveal_type(first([1, 2, 3]))       # int
reveal_type(first(["a", "b"]))      # str
```

`first` does not return `Any` — it returns whatever type went in. Compare with the `Any` version,
where mypy would happily let you write `first([1, 2]) + "oops"`.

Constrain a `TypeVar` when the body needs specific behaviour:

```python
class Animal:
    def speak(self) -> str:
        return "..."

TAnimal = TypeVar("TAnimal", bound=Animal)     # any Animal subclass

def loudest(animals: list[TAnimal]) -> TAnimal:
    return max(animals, key=lambda a: len(a.speak()))
```

A generic class works the same way, via `Generic[T]`:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

stack: Stack[int] = Stack()
stack.push(1)
stack.push("two")        # mypy: Argument 1 has incompatible type "str"; expected "int"
stack.pop() + 1          # fine: pop() is int
```

`Stack[int]` is a *parameterised* type: one class, checked at each use site.

## `Protocol`: structural typing

Chapter 13's inheritance is **nominal** — a class is a subtype because it says so. `Protocol`
gives you **structural** typing: a class satisfies the protocol because it has the right methods,
whether or not it ever heard of it.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:                      # note: does not inherit from Drawable
    def draw(self) -> str:
        return "  ( o )  "

class BarChart:
    def draw(self) -> str:
        return "▁▃▅▇"

def render(shape: Drawable) -> str:
    return shape.draw()

for shape in (Circle(), BarChart()):
    print(render(shape))
```

```text
  ( o )
▁▃▅▇
```

This is duck typing that a machine can verify. Use a `Protocol` when you want to accept "anything
with `.read()`" or "anything with `.draw()`" without forcing unrelated classes into a shared
hierarchy — which is exactly the situation you hit when a class already inherits from something
else. Chapter 33's game architecture leans on this.

## `Literal`, `Final`, `TypedDict`, `NewType`

Four small tools that remove a surprising amount of ambiguity:

```python
from typing import Final, Literal, NewType, TypedDict

LogLevel = Literal["DEBUG", "INFO", "WARN", "ERROR"]   # exactly these strings
MAX_RETRIES: Final = 3                                  # constant; reassignment is an error

class User(TypedDict):                                  # shape of a JSON-ish dict
    id: int
    email: str
    is_admin: bool

UserId = NewType("UserId", int)                         # distinct type, same runtime value

def log(message: str, level: LogLevel = "INFO") -> None:
    print(f"[{level}] {message}")

def get_user(user_id: UserId) -> User: ...

log("started")
log("oops", "TRACE")     # mypy: not a valid LogLevel
get_user(42)             # mypy: int is not UserId
get_user(UserId(42))     # fine
```

- **`Literal`** turns a set of strings into a type. mypy flags typos in what used to be free-form
  arguments, which is a real bug class in config and logging code.
- **`Final`** marks a constant. `MAX_RETRIES = 4` elsewhere becomes an error.
- **`TypedDict`** describes the shape of a dict — usually one that came from JSON. Plain
  `dict[str, Any]` tells you nothing about the keys; `User` tells you all of them.
- **`NewType`** creates a distinct type from an existing one with zero runtime cost. It stops you
  passing a raw `int` where a `UserId` is expected — the classic "arguments in the wrong order"
  bug.

## `from __future__ import annotations`

By default, annotations are evaluated when the `def` statement runs. That breaks forward
references — a method annotated with a class defined later in the file. This line at the top of
the module makes annotations *strings* that are only resolved when something asks:

```python
from __future__ import annotations

class Node:
    def __init__(self, value: int) -> None:
        self.value = value
        self.next: Node | None = None      # refers to Node, which is not finished yet
```

It must be the first statement in the file (comments and the docstring excepted). It also speeds
up imports slightly and lets you use `X | Y` syntax on 3.9.

The trade-off: because annotations are strings, anything that reads them at runtime must resolve
them, usually with `typing.get_type_hints()`. Pydantic and FastAPI do exactly that — which is why
a Pydantic model in a module using `from __future__ import annotations` needs every referenced
type importable at module scope.

## Running mypy

```bash
python3 -m pip install mypy
```

Given this file:

```python
# orders.py
def total(prices: list[float]) -> float:
    return sum(prices)

def label(name: str, qty: int) -> str:
    return f"{name}: {qty}"

print(total([1.5, 2.5]))
print(label("widget", "3"))
print(total(["1.50", "2.50"]))
```

Run the checker:

```bash
python3 -m mypy orders.py
```

```text
orders.py:8: error: Argument 2 to "label" has incompatible type "str"; expected "int"  [arg-type]
orders.py:9: error: List item 0 has incompatible type "str"; expected "float"  [list-item]
Found 2 errors in 1 file (checked 1 source file)
```

Read each line as `file:line: error: message [error-code]`. The message tells you what mypy
inferred and what it wanted; the bracketed code (`arg-type`, `list-item`, `return-value`,
`attr-defined`) is what you use to silence that specific error. Both errors above are real: `"3"`
is a string, and `total` will concatenate rather than add.

`reveal_type(expression)` is the debugging tool — mypy prints its inferred type. It is a mypy
special form with no runtime meaning, so delete the line before running the file.

### Stricter, and how to silence it properly

```bash
python3 -m mypy --strict orders.py
```

`--strict` turns on roughly a dozen flags, the painful ones being `disallow_untyped_defs` (every
function must be annotated) and `disallow_any_generics` (`list`, not `list[Any]`). Good for new
code; brutal for legacy code. Rather than typing flags every time, put them in `pyproject.toml`:

```text
[tool.mypy]
python_version = "3.12"
strict = true
warn_unreachable = true

[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true
```

To ignore one line, always name the code:

```python
value = untyped_library_call()  # type: ignore[arg-type]
```

A bare `# type: ignore` suppresses everything on that line, including the `attr-defined` error you
did not know about. Under `--strict`, `warn_unused_ignores` flags ignores that no longer match
anything, so they cannot rot.

mypy is not the only checker. **pyright** (which powers the Pylance extension in VS Code) is
faster, has excellent inference, and needs no configuration to be useful. If you use VS Code you
are probably already running it. Pick one for CI — mypy is the conventional choice — and let the
other be your editor's opinion.

:::scenario You add mypy to a codebase and get 812 errors
You have inherited a 20,000-line service with no annotations. You install mypy expecting a
reassuring summary and instead get 812 errors across 140 files. Nobody will approve a week-long
typing sprint, and half the errors are in third-party libraries you do not control.
:::

:::solution Do not fix 812 errors. Move the boundary.
Typing is *gradual* — every file can be checked to a different depth, and mypy is designed for
exactly this rollout. Turn the firehose into a ratchet:

1. **Start permissive.** Add config that checks only what you have already annotated:

   ```text
   [tool.mypy]
   python_version = "3.12"
   ignore_missing_imports = true
   check_untyped_defs = false
   ```

   `ignore_missing_imports` silences the "no stubs for library X" noise from untyped third-party
   packages; if a library ships type hints or has a `-stubs` package, install it instead.

2. **Annotate the boundaries first.** Public function signatures, data models, and anything that
   parses external input. That is where a wrong type becomes a runtime crash. Private helpers can
   wait.

3. **Lock in progress with overrides.** Once a module is clean, opt it into strict mode so it
   cannot regress:

   ```text
   [[tool.mypy.overrides]]
   module = ["orders.*", "billing.*"]
   strict = true
   ```

4. **Make it a gate, not a report.** Run mypy in CI on the files it currently checks and fail the
   build on new errors. `git diff --name-only main | grep '\.py$' | xargs mypy` checks only what
   changed, which keeps the signal useful on day one.

The errors you find first will be the interesting ones: functions returning `None` on one path and
a value on another, dict lookups that can raise `KeyError`, and `if user:` where the intention was
`if user is not None:`. Those are latent bugs, and mypy just handed you the list.
:::

## Narrowing

A checker follows your control flow. Inside a branch where you have tested the type, the type is
narrower — so `str | None` becomes `str` and `.title()` is allowed:

```python
def greet(name: str | None) -> str:
    if name is None:
        return "Hello, stranger"
    return f"Hello, {name.title()}"      # name is str here

def double(value: int | str) -> int | str:
    if isinstance(value, str):
        return value * 2                 # "ab" -> "abab"
    return value * 2                     # 3 -> 6

def first_user(users: list[str]) -> str:
    assert users, "users must not be empty"
    return users[0].upper()              # assert narrows away the empty case
```

`is None`, `isinstance`, `in`, `==`, truthiness, and `assert` all narrow. When your annotation is
right but mypy still complains, you are usually missing a guard — add the `if`, do not reach for
`cast` or `# type: ignore`.

## Annotations at runtime: Pydantic and FastAPI

Annotations are ordinary Python objects sitting in `__annotations__`, so libraries can read them
and act. **Pydantic** does exactly that:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    tags: list[str] = []

print(Item(name="Cup", price="3.50"))
```

```text
name='Cup' price=3.5 tags=[]
```

The string `"3.50"` became `3.5` because the annotation said `float`. Give it something it cannot
coerce and you get a real error, with the field named:

```python
Item(name="Cup", price="free")
```

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for Item
price
  Input should be a valid number, unable to parse string as a number [type=float_parsing, ...]
```

This is the pattern FastAPI is built on: you declare a Pydantic model, use it as a parameter
annotation, and the framework validates the request body, generates the JSON schema, and writes
the API docs from the same source of truth. Chapter 26 opens with exactly that. It is also the
clearest argument for annotating carefully — one annotation ends up doing three jobs.

:::pitfall Annotations are not validated at runtime
The interpreter records annotations and then ignores them:

```python
def double(x: int) -> int:
    return x * 2

print(double("ha"))
```

```text
haha
```

No `TypeError`, no warning. The same is true of variable annotations:

```python
counts: dict[str, int] = {}
counts["a"] = "not a number"      # runs fine
```

Hints are documentation for humans and input for static checkers — never a runtime guard. So when
data comes from outside your program (HTTP request, JSON file, CSV, user input, database row), you
must validate it yourself. Two options, in order of preference:

1. **Pydantic** (or similar) — declare a model and let it parse and coerce. Best when you already
   have it as a dependency, and built into FastAPI.
2. **Manual validation** — explicit `isinstance` checks that raise `ValueError` with a message
   naming the offending field.

```python
def parse_quantity(raw: object) -> int:
    if not isinstance(raw, int) or isinstance(raw, bool):   # bool is a subclass of int
        raise ValueError(f"quantity must be an int, got {type(raw).__name__}")
    return raw
```

Note the `isinstance(raw, bool)` clause: `isinstance(True, int)` is `True`, so without it a JSON
`true` sails through as the number 1.
:::

## Key takeaways

- Annotate parameters (`x: int`) and returns (`-> str`) on every public function; annotate
  variables when the type is not obvious from the assignment.
- Use built-in generics (`list[str]`, `dict[str, int]`), `tuple[int, ...]` for variable-length
  tuples, and `X | None` instead of `Optional[X]`.
- `TypeVar` says "same type in and out"; `Protocol` says "any object with these methods" without
  requiring inheritance.
- `Literal`, `Final`, `TypedDict`, and `NewType` eliminate whole categories of typo and
  wrong-argument bugs.
- `from __future__ import annotations` makes annotations lazy strings, enabling forward
  references.
- `mypy file.py` reports `file:line: error: message [code]`; use `--strict` for new code and
  `# type: ignore[code]` with an explicit code, never a bare ignore.
- Type hints are not runtime validation — validate external data with Pydantic or explicit
  `isinstance` checks.

## Practice

- [ ] Annotate this function and its variables, then run mypy and confirm it is clean:
      `def average(values): total = 0; for v in values: total += v; return total / len(values)`.
- [ ] Write a generic `first(items: Sequence[T]) -> T` and a `Stack(Generic[T])` class. Use them
      with `int` and with `str`, and confirm mypy infers the right type for `first(["a"])`.
- [ ] Define a `Serializable(Protocol)` with a `to_json(self) -> str` method, then write two
      unrelated classes that satisfy it and a `dump(obj: Serializable) -> str` that calls it.
- [ ] Model a `Movie` with `TypedDict`, a `Rating = Literal["G", "PG", "PG-13", "R"]`, and a
      `DEFAULT_RATING: Final = "PG"`. Write `by_rating(movies: list[Movie], rating: Rating)`.
- [ ] Write a file with three deliberate type errors, run mypy, and fix all three without using
      `# type: ignore`. Use `reveal_type` on one expression first.
- [ ] Write `parse_order(raw: dict[str, Any]) -> Order` where `Order` is a `TypedDict`. It must
      raise `ValueError` naming the field when a key is missing or has the wrong type.

## Solutions

:::solution Exercise 1
```python
from collections.abc import Iterable

def average(values: Iterable[float]) -> float:
    total: float = 0.0
    count: int = 0
    for value in values:
        total += value
        count += 1
    return total / count

print(average([1.0, 2.0, 4.0]))
```
`Iterable[float]` accepts lists, tuples, and generators — stricter than `Any`, more flexible than
`list[float]`. `count` is tracked separately because `len()` does not exist on an arbitrary
iterable. Run `python3 -m mypy average.py` and it reports `Success: no issues found`.
:::

:::solution Exercise 2
```python
from typing import Generic, TypeVar
from collections.abc import Sequence

T = TypeVar("T")

def first(items: Sequence[T]) -> T:
    return items[0]

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

numbers: Stack[int] = Stack()
numbers.push(10)
print(numbers.pop() + 1)

words: Stack[str] = Stack()
words.push("hi")
print(first(["a", "b"]).upper())
print(first([1, 2]).upper())      # mypy: "int" has no attribute "upper"
```
```text
11
A
```
The last line is the point: because `first` is generic rather than `Any`-returning, mypy knows
`first([1, 2])` is an `int` and rejects `.upper()` before you run anything.
:::

:::solution Exercise 3
```python
from typing import Protocol

class Serializable(Protocol):
    def to_json(self) -> str: ...

class User:
    def __init__(self, name: str) -> None:
        self.name = name

    def to_json(self) -> str:
        return f'{{"name": "{self.name}"}}'

class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def to_json(self) -> str:
        return f'{{"x": {self.x}, "y": {self.y}}}'

def dump(obj: Serializable) -> str:
    return obj.to_json()

print(dump(User("ada")))
print(dump(Point(1, 2)))
```
```text
{"name": "ada"}
{"x": 1, "y": 2}
```
Neither class inherits from `Serializable` — having a matching `to_json` method is enough. That
is structural typing, and it is why you can add a new serialisable class anywhere in the codebase
without touching a base class.
:::

:::solution Exercise 4
```python
from typing import Final, Literal, TypedDict

Rating = Literal["G", "PG", "PG-13", "R"]
DEFAULT_RATING: Final = "PG"

class Movie(TypedDict):
    title: str
    year: int
    rating: Rating

def by_rating(movies: list[Movie], rating: Rating = DEFAULT_RATING) -> list[Movie]:
    return [m for m in movies if m["rating"] == rating]

LIBRARY: list[Movie] = [
    {"title": "Arrival", "year": 2016, "rating": "PG-13"},
    {"title": "Inside Out", "year": 2015, "rating": "PG"},
]

print(by_rating(LIBRARY))
print(by_rating(LIBRARY, "PG"))
```
```text
[{'title': 'Inside Out', 'year': 2015, 'rating': 'PG'}]
[{'title': 'Inside Out', 'year': 2015, 'rating': 'PG'}]
```
`TypedDict` turns an untyped dict into a record with known keys, so mypy catches
`m["rating"] = "M"` and `by_rating(LIBRARY, "M")` at check time instead of at 3 a.m.
:::

:::solution Exercise 5
```python
# broken.py
def shout(text: str) -> str:
    return text.upper()

def add(a: int, b: int) -> int:
    return a + b

print(shout(42))
print(add("2", 3))
print(shout("ok").appending("!"))
```
```bash
python3 -m mypy broken.py
```
```text
broken.py:7: error: Argument 1 to "shout" has incompatible type "int"; expected "str"  [arg-type]
broken.py:8: error: Argument 1 to "add" has incompatible type "str"; expected "int"  [arg-type]
broken.py:9: error: "str" has no attribute "appending"  [attr-defined]
Found 3 errors in 1 file (checked 1 source file)
```
Fixed:

```python
# fixed.py
def shout(text: str) -> str:
    return text.upper()

def add(a: int, b: int) -> int:
    return a + b

print(shout("42"))
print(add(2, 3))
print(shout("ok") + "!")
```
```text
Success: no issues found in 1 source file
```
`reveal_type(shout("ok"))` prints `note: Revealed type is "builtins.str"` — it is the fastest way
to check what mypy actually thinks when an error message surprises you.
:::

:::solution Exercise 6
```python
from typing import Any, TypedDict

class Order(TypedDict):
    id: int
    item: str
    quantity: int

FIELDS: dict[str, type] = {"id": int, "item": str, "quantity": int}

def parse_order(raw: dict[str, Any]) -> Order:
    for field, expected in FIELDS.items():
        if field not in raw:
            raise ValueError(f"missing field: {field!r}")
        value = raw[field]
        if not isinstance(value, expected) or isinstance(value, bool):
            raise ValueError(
                f"{field!r} must be {expected.__name__}, got {type(value).__name__}"
            )
    return Order(id=raw["id"], item=raw["item"], quantity=raw["quantity"])

print(parse_order({"id": 1, "item": "Cup", "quantity": 2}))
print(parse_order({"id": "1", "item": "Cup", "quantity": 2}))
```
```text
{'id': 1, 'item': 'Cup', 'quantity': 2}
Traceback (most recent call last):
  ...
ValueError: 'id' must be int, got str
```
This is manual validation, the fallback for when Pydantic is not available. Two details matter:
the `isinstance(value, bool)` guard (booleans are ints in Python, so `True` would otherwise pass
as a quantity), and error messages that name the field — "must be int, got str" is debuggable at
2 a.m., "bad input" is not.
:::
