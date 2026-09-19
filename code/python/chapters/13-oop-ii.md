---
chapter: 13
part: 2
title: OOP II: Inheritance, Composition & Dataclasses
summary: Share behaviour the right way — composition over inheritance, protocols and ABCs for contracts, and dataclasses for data-heavy classes.
minutes: 45
tags: [inheritance, composition, protocols, abc, dataclasses, MRO]
---

Inheritance gets most of the attention in object-oriented programming and deserves about a tenth
of it. It is genuinely useful for one thing — modelling a real "is-a" relationship — and it is
routinely abused for a different thing: reusing a method you happen to want. That abuse produces
hierarchies six levels deep where changing the base class breaks three teams. This chapter covers
inheritance honestly, then spends most of its time on the two tools that usually beat it:
composition (pass the behaviour in as an object) and dataclasses (stop hand-writing `__init__` for
classes that are mostly data).

## Inheritance basics

```python
class Report:
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows

    def filename(self):
        return self.title.lower().replace(" ", "-") + ".txt"

    def render(self):
        header = self.title.upper()
        lines = [header, "-" * len(header)]
        lines.extend(" | ".join(str(cell) for cell in row) for row in self.rows)
        return "\n".join(lines) + "\n"


class CsvReport(Report):
    def filename(self):
        return self.title.lower().replace(" ", "-") + ".csv"

    def render(self):
        lines = [",".join(str(cell) for cell in row) for row in self.rows]
        return "\n".join(lines) + "\n"
```

```python
rows = [("widget", 3), ("gizmo", 1)]
print(CsvReport("March Sales", rows).render())
print(Report("March Sales", rows).filename())
```

```text
widget,3
gizmo,1
march-sales.txt
```

`CsvReport(Report)` says: a `CsvReport` *is a* `Report`, with two differences. `render` is
**overridden** — completely replaced. `rows` and `title` are inherited unchanged, and so is
anything else `Report` gains later.

### `super()`

Overrides often want to *extend* the parent rather than replace it. `super()` returns the parent's
version of the thing you are in:

```python
from datetime import date


class TimestampedReport(Report):
    def __init__(self, title, rows, created_at=None):
        super().__init__(title, rows)
        self.created_at = created_at or date.today()

    def render(self):
        return f"generated {self.created_at}\n\n" + super().render()
```

```python
print(TimestampedReport("March Sales", rows, date(2026, 3, 1)).render())
```

```text
generated 2026-03-01

MARCH SALES
-----------
widget | 3
gizmo | 1
```

`super().__init__(...)` lets the parent own its own attributes instead of the child re-assigning
them. Skipping it means the parent's setup never runs, which produces the confusing
`AttributeError: 'TimestampedReport' object has no attribute 'title'`.

### `isinstance` and `issubclass`

```python
report = CsvReport("March Sales", rows)

isinstance(report, CsvReport)   # True
isinstance(report, Report)      # True — a subclass instance IS-A parent instance
isinstance(report, object)      # True, always
type(report) is Report          # False — type() is exact, isinstance() is not
issubclass(CsvReport, Report)   # True
```

Reach for `isinstance` before `type(x) == Y`, because the latter breaks the moment someone
subclasses. That said, if your code is full of `isinstance` branches, you probably wanted a method
on each class instead — the branch is a sign the behaviour belongs *in* the objects.

## MRO and multiple inheritance

A class can inherit from several parents. Python decides which method wins using the **MRO**
(Method Resolution Order), and it is visible:

```python
class A:
    def greet(self):
        return "A"

class B:
    def greet(self):
        return "B"

class C(A, B):
    pass
```

```python
print(C().greet())
print([cls.__name__ for cls in C.mro()])
```

```text
A
['C', 'A', 'B', 'object']
```

Left to right, then up. `C` inherits `greet` from `A` because `A` comes first.

Here is the honest part: multiple inheritance is easy for one case and hard for all the others.
The one good case is **mixins** — small classes that add a single capability and are never
instantiated alone:

```python
class DictMixin:
    """Adds as_dict() to any class with ordinary instance attributes."""
    def as_dict(self):
        return {key: value for key, value in vars(self).items()
                if not key.startswith("_")}


class Customer(DictMixin):
    def __init__(self, name, email):
        self.name = name
        self.email = email


print(Customer("Ada", "ada@example.com").as_dict())
```

```text
{'name': 'Ada', 'email': 'ada@example.com'}
```

Multiple inheritance gets genuinely subtle when several parents define the same method and each
calls `super()` — that "cooperative super" pattern requires every class in the chain to cooperate,
and getting it wrong fails in a way that is hard to trace. Rules that keep you out of trouble:

- Keep hierarchies **one or two levels deep**. If you need a third, you probably need composition.
- Name mixins `SomethingMixin` so their role is obvious.
- If you cannot explain your class's MRO from memory, it is too complicated.

## Composition over inheritance

This is the main lesson of the chapter. Consider an order service that needs to notify someone
when an order is placed:

```python
class Notifier:
    def notify(self, message):
        print(f"[notify] {message}")


class OrderService(Notifier):          # an order service is not a notifier
    def __init__(self):
        self.orders = []

    def place(self, item, quantity):
        self.orders.append((item, quantity))
        self.notify(f"placed {quantity} x {item}")

    def cancel(self, item):
        self.orders = [order for order in self.orders if order[0] != item]
        self.notify(f"cancelled {item}")
```

It works, and it is wrong. `OrderService` inherited from `Notifier` because it wanted one method,
not because it *is* a notifier. The bill arrives the first time you need two channels: you now
want `EmailOrderService`, `SmsOrderService`, and `EmailAndSmsOrderService` — a combinatorial
explosion produced entirely by inheritance. Testing is worse: `place()` writes to stdout, so your
test has to capture stdout.

Pass the collaborator in instead:

```python
class ConsoleNotifier:
    def send(self, message):
        print(f"[console] {message}")


class EmailNotifier:
    def __init__(self, address):
        self.address = address

    def send(self, message):
        print(f"[email to {self.address}] {message}")


class OrderService:
    def __init__(self, notifier):
        self.notifier = notifier
        self.orders = []

    def place(self, item, quantity):
        self.orders.append((item, quantity))
        self.notifier.send(f"placed {quantity} x {item}")

    def cancel(self, item):
        self.orders = [order for order in self.orders if order[0] != item]
        self.notifier.send(f"cancelled {item}")
```

Now channels are independent classes, not subclasses, and there is nothing to combine — if you
want two channels, you pass an object that holds two notifiers. And testing is trivial, because you
can pass an object that just remembers what it was told:

```python
class CollectingNotifier:
    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)
```

```python
def test_place_sends_notification():
    notifier = CollectingNotifier()
    service = OrderService(notifier)

    service.place("widget", 3)

    assert notifier.sent == ["placed 3 x widget"]
    assert service.orders == [("widget", 3)]
```

That is Chapter 11's fixture pattern with no mocks required, because the dependency was injected
rather than inherited. **Composition**: an object *has* a collaborator. **Inheritance**: an object
*is* its parent. When you want behaviour, you almost always want "has".

## Duck typing and `Protocol`

`OrderService` never asked what type its notifier was. It called `.send(message)` and moved on.
That is **duck typing**: if it has the method you need, it qualifies. No base class, no import, no
shared ancestor.

Duck typing is excellent at runtime and invisible to tooling, which is what `typing.Protocol`
fixes. A protocol declares the shape you require:

```python
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> None: ...
```

(The annotations are part of the syntax; Chapter 16 covers type hints properly.) Now you can
annotate the parameter, and a type checker will accept *any* class with a matching `send` —
including one from a third-party library that has never heard of your codebase:

```python
class OrderService:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier
```

That is **structural typing**: conformance is determined by shape, not by declaration. Compare it
with a rigid base class, where every collaborator must import and inherit from your base even when
the inheritance makes no sense. Add `@runtime_checkable` if you genuinely need `isinstance(x,
Notifier)` at runtime — but if you do, ask whether a method on the object would be better.

## Abstract base classes

Protocols describe a shape. Sometimes you want the opposite: a real contract that shares
implementation and refuses to be instantiated half-built. That is `abc`:

```python
from abc import ABC, abstractmethod
from pathlib import Path


class Exporter(ABC):
    @abstractmethod
    def render(self): ...

    @abstractmethod
    def filename(self): ...

    def save(self, directory):
        path = Path(directory) / self.filename()
        path.write_text(self.render(), encoding="utf-8")
        return path
```

```python
Exporter()
```

```text
TypeError: Can't instantiate abstract class Exporter without an implementation
for abstract methods 'filename', 'render'
```

A subclass must implement both abstract methods or it cannot be instantiated either — the error
fires at construction time, not at some later call:

```python
class CsvExporter(Exporter):
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows

    def filename(self):
        return self.title.lower().replace(" ", "-") + ".csv"

    def render(self):
        return "\n".join(",".join(str(cell) for cell in row) for row in self.rows) + "\n"


path = CsvExporter("March Sales", [("widget", 3)]).save("/tmp")
print(path.read_text())
```

```text
widget,3
```

`save()` is concrete: every exporter gets it for free, and it is built out of the two abstract
pieces each subclass must supply. That is the template pattern, and it is the best use of an ABC.

Choose between them like this:

| | ABC | Protocol |
| --- | --- | --- |
| Conformance | nominal — must inherit | structural — just have the methods |
| Shares code | yes | no |
| Third-party classes qualify | no | yes |
| Use for | one hierarchy you own, with shared implementation | describing what you need from a collaborator |

## Dataclasses

Most classes you write are mostly data. For those, hand-writing `__init__`, `__repr__`, and
`__eq__` is three screens of boilerplate per class:

```python
from dataclasses import dataclass, field


@dataclass
class Point:
    x: float
    y: float
```

```python
p = Point(1.5, 2.0)
print(p)
print(Point(1.5, 2.0) == Point(1.5, 2.0))
```

```text
Point(x=1.5, y=2.0)
True
```

You get `__init__`, `__repr__`, and `__eq__` for the price of two annotations. Options worth
knowing:

```python
@dataclass(frozen=True)         # immutable: assignment raises FrozenInstanceError,
class Money:                    # and instances become hashable
    currency: str
    cents: int

@dataclass(order=True)          # adds <, <=, >, >= comparing fields in order
class Version:
    major: int
    minor: int
    patch: int

@dataclass(slots=True)          # no per-instance __dict__: less memory, faster
class Reading:                  # attribute access, and typos raise AttributeError
    sensor: str
    value: float
```

A field default that is a mutable object must use `field(default_factory=...)`:

```python
@dataclass
class Basket:
    owner: str
    items: list[str] = field(default_factory=list)
```

```python
a = Basket("Ada")
b = Basket("Grace")
a.items.append("apple")
print(a.items, b.items)
```

```text
['apple'] []
```

Writing `items: list[str] = []` is the pitfall from Chapter 12 wearing a decorator, and Python
refuses it outright:

```text
ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory
```

Validation goes in `__post_init__`, which runs at the end of the generated `__init__`:

```python
@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price_cents: int

    def __post_init__(self):
        if self.price_cents < 0:
            raise ValueError(f"price cannot be negative: {self.price_cents}")


Product("W-1", "Widget", -5)
```

```text
ValueError: price cannot be negative: -5
```

For an immutable record with no behaviour at all, `NamedTuple` is smaller and gives you tuple
semantics for free — indexing, unpacking, and comparison:

```python
from typing import NamedTuple


class Address(NamedTuple):
    line1: str
    city: str
    postcode: str
    country: str = "UK"
```

```python
home = Address("12 Analytic Way", "London", "N1 9GU")
print(home)
print(home.city, home[2])
line1, city, postcode, country = home
```

```text
Address(line1='12 Analytic Way', city='London', postcode='N1 9GU', country='UK')
London N1 9GU
```

## Worked example: an order system

Composition and dataclasses together. Note there is no inheritance anywhere:

```python
from dataclasses import dataclass, field
from typing import NamedTuple, Protocol


class Address(NamedTuple):
    line1: str
    city: str
    postcode: str
    country: str = "UK"


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str
    price_cents: int

    def __post_init__(self):
        if self.price_cents < 0:
            raise ValueError(f"price cannot be negative: {self.price_cents}")


@dataclass
class LineItem:
    product: Product
    quantity: int = 1

    def __post_init__(self):
        if self.quantity < 1:
            raise ValueError(f"quantity must be at least 1, got {self.quantity}")

    @property
    def subtotal_cents(self):
        return self.product.price_cents * self.quantity


@dataclass
class Customer:
    name: str
    email: str
    address: Address | None = None


class Discount(Protocol):
    def apply(self, total_cents: int) -> int: ...


@dataclass
class Order:
    customer: Customer
    items: list[LineItem] = field(default_factory=list)
    discounts: list[Discount] = field(default_factory=list)

    def add(self, product, quantity=1):
        self.items.append(LineItem(product, quantity))

    @property
    def subtotal_cents(self):
        return sum(item.subtotal_cents for item in self.items)

    @property
    def total_cents(self):
        total = self.subtotal_cents
        for discount in self.discounts:
            total = discount.apply(total)
        return total

    def __str__(self):
        lines = [f"Order for {self.customer.name} <{self.customer.email}>"]
        lines.extend(f"  {item.product.name} x{item.quantity}"
                     f"  {format_cents(item.subtotal_cents)}" for item in self.items)
        lines.append(f"  SUBTOTAL {format_cents(self.subtotal_cents)}")
        lines.append(f"  TOTAL    {format_cents(self.total_cents)}")
        return "\n".join(lines)


def format_cents(cents):
    return f"£{cents / 100:.2f}"
```

```python
widget = Product("W-1", "Widget", 250)
gizmo = Product("G-7", "Gizmo", 1299)
ada = Customer("Ada", "ada@example.com", Address("12 Analytic Way", "London", "N1 9GU"))

order = Order(ada)
order.add(widget, 3)
order.add(gizmo)
print(order)
```

```text
Order for Ada <ada@example.com>
  Widget x3  £7.50
  Gizmo x1  £12.99
  SUBTOTAL £20.49
  TOTAL    £20.49
```

Every relationship here is "has a": an `Order` has a `Customer`, has `LineItem`s, and has
`Discount`s. Each piece is independently testable, and `Product` being frozen means nobody can
change a price after an order references it.

Now the payoff. A new discount rule is a new small class, not a subclass of `Order`:

```python
class PercentageDiscount:
    def __init__(self, percent):
        self.percent = percent

    def apply(self, total_cents):
        return round(total_cents * (1 - self.percent / 100))


class LoyaltyDiscount:
    def __init__(self, orders_placed):
        self.orders_placed = orders_placed

    def apply(self, total_cents):
        if self.orders_placed < 5:
            return total_cents
        return round(total_cents * 0.95)


order.discounts.append(PercentageDiscount(10))
print(order)
```

```text
Order for Ada <ada@example.com>
  Widget x3  £7.50
  Gizmo x1  £12.99
  SUBTOTAL £20.49
  TOTAL    £18.44
```

2049 * 0.9 = 1844.1 → 1844 → £18.44. `Order` never changed. That is what composition buys you:
new behaviour arrives as a new object rather than as a new branch in someone else's class, and
this is the shape the Pygame entities in Chapter 33 will use — a `Player` that *has* a
`MovementController` rather than twelve subclasses of `Player`.

:::scenario A five-level hierarchy where changing the base class breaks three teams
The codebase has `Report` → `PdfReport` → `InvoicePdfReport` → `MonthlyInvoicePdfReport` →
`MonthlyInvoicePdfReportV2`. You are asked to add a CSV export. Reading `MonthlyInvoicePdfReportV2`
requires opening four other files, and last time someone touched `PdfReport`, the VAT report broke
because it overrode a method the base class had quietly changed.
:::

:::solution Flatten it: keep one level of inheritance, move everything else to collaborators
A deep hierarchy is almost always two or three unrelated concerns stacked on top of each other.
Separate them:

1. **Keep the genuine "is-a" level.** A `MonthlyInvoiceReport` really is a report. One level, one
   abstract base that defines the contract:
   ```python
   class Report(ABC):
       @abstractmethod
       def rows(self): ...
       @abstractmethod
       def title(self): ...
   ```
2. **Extract the varying parts into collaborators.** Format (PDF vs CSV) is not a subtype — it is
   a strategy you hand the report:
   ```python
   class Report:
       def __init__(self, title, rows, renderer, destination):
           self.title = title
           self.rows = rows
           self.renderer = renderer      # PdfRenderer(), CsvRenderer(), HtmlRenderer()
           self.destination = destination  # EmailDestination(), S3Destination(), LocalDisk()

       def publish(self):
           return self.destination.write(self.renderer.render(self.title, self.rows))
   ```
   Adding CSV is now one new class with no existing file touched — and PDF and CSV can be tested
   against the same fixture data.
3. **Replace the `V2` classes with parameters.** `MonthlyInvoicePdfReportV2` exists because it
   needed one different behaviour. Pass it in: `MonthlyInvoiceReport(..., period="monthly")`.
4. **Do it incrementally and under test.** Write characterisation tests first (Chapter 11) that
   render each existing report and hash the output. Then refactor one leaf at a time, keeping the
   old class as a thin wrapper that constructs the new one, and delete the wrapper once nothing
   imports it.
5. **Add a lint rule** so it cannot come back: any class more than two levels deep needs a comment
   in the review explaining why.

The tell that this was the right call: the CSV export took one new class and zero edits to
existing files. Under the old design it would have needed a parallel five-level hierarchy.
:::

:::pitfall Inheriting to reuse one method
```python
class EmailSender:
    def __init__(self, smtp_host):
        self.smtp_host = smtp_host

    def send(self, to, subject, body):
        print(f"sent {subject} to {to} via {self.smtp_host}")

    def log(self, message):
        print(f"[log] {message}")


class PasswordResetter(EmailSender):
    """Only wanted .log()."""
    def __init__(self):
        super().__init__("smtp.internal")

    def reset(self, email):
        self.log(f"reset requested for {email}")
```

`PasswordResetter` is not an email sender. But it now exposes `.send()`, it is forced to know an
SMTP host, and `isinstance(resetter, EmailSender)` is true — so some future `for sender in
senders: sender.send(...)` loop will hand it a job it cannot do. The coupling is invisible in the
class body and shows up as a bug a year later.

Pass the collaborator in:

```python
class PasswordResetter:
    def __init__(self, logger):
        self.logger = logger

    def reset(self, email):
        self.logger.log(f"reset requested for {email}")
```

```python
class ConsoleLogger:
    def log(self, message):
        print(f"[log] {message}")
```

Now `PasswordResetter` has no opinion about SMTP, tests inject a logger that records messages
instead of printing them, and the two classes can evolve independently.

The question to ask before writing `class X(Y)`: "is every `X` really a `Y`, for all time, in every
sense the rest of the code assumes?" If the honest answer is "I wanted one method", take that
method's object as a constructor argument instead.
:::

## Key takeaways

- Inheritance models a real "is-a" relationship; `super()` extends a parent method instead of
  replacing it.
- Python resolves methods with the MRO, left to right, visible as `SomeClass.mro()`; keep
  hierarchies shallow and use multiple inheritance only for mixins.
- Prefer composition: pass a collaborator object in rather than inheriting for one method.
- Duck typing means any object with the right methods qualifies; `typing.Protocol` documents that
  shape for tooling without forcing a shared base class.
- `abc.ABC` with `@abstractmethod` defines a real contract and refuses to instantiate incomplete
  subclasses; use it when you also share implementation.
- `@dataclass` generates `__init__`, `__repr__`, and `__eq__`; add `frozen=True`, `slots=True`,
  `order=True`, and `field(default_factory=...)` as needed.
- Validate dataclass fields in `__post_init__`; use `NamedTuple` for immutable, tuple-like records.
- A class that is only data is a dataclass; a class with no state is a module.

## Practice

- [ ] Write `Animal` with `__init__(self, name)` and `speak()` returning `""`. Add `Dog` and `Cat`
      overriding `speak`, with `Dog.__init__` calling `super().__init__(name)` and adding a
      `breed`. Confirm `isinstance(dog, Animal)` is `True` and `type(dog) is Animal` is `False`.
- [ ] Build `class A` and `class B` each with a `tag()` method returning their name, then
      `class C(B, A)`. Predict `C().tag()` and `[c.__name__ for c in C.mro()]`, then run it and
      confirm. Swap the parents and explain the new output.
- [ ] Refactor `PasswordResetter(EmailSender)` from the pitfall into the composition version, and
      write two pytest tests: one that a `RecordingLogger` captures the reset message, and one that
      `PasswordResetter` has no `send` attribute.
- [ ] Convert the `Book` class from Chapter 12 into a frozen, slotted dataclass with
      `__post_init__` validation rejecting empty titles and non-positive page counts. Then write a
      `Library` dataclass holding `books: list[Book] = field(default_factory=list)` with `add` and
      `total_pages` methods.
- [ ] Extend the order system: add a `BulkDiscount` class (10% off when the subtotal is £50 or
      more, otherwise no change) that satisfies the `Discount` protocol, wire it into an `Order`,
      and write three pytest tests covering below threshold, above threshold, and combined with
      `PercentageDiscount`.

## Solutions

:::solution Exercise 1
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return ""

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"


class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        return "woof"


class Cat(Animal):
    def speak(self):
        return "meow"


dog = Dog("Rex", "labrador")
print(dog.speak(), dog.name, dog.breed)
print(isinstance(dog, Animal), type(dog) is Animal)
```
```text
woof Rex labrador
True False
```
`super().__init__(name)` sets `name` on the instance via the parent, so `Dog` only has to deal
with what is new — the breed. `type(dog) is Animal` is `False` while `isinstance` is `True`, which
is exactly why `isinstance` is the check you want: it respects the "is-a" relationship.
:::

:::solution Exercise 2
```python
class A:
    def tag(self):
        return "A"

class B:
    def tag(self):
        return "B"

class C(B, A):
    pass


print(C().tag())
print([cls.__name__ for cls in C.mro()])
```
```text
B
['C', 'B', 'A', 'object']
```
The MRO follows the order the bases are listed in, so with `(B, A)` the lookup finds `B.tag` first.
Swap to `class C(A, B)` and both outputs change to `A` and `['C', 'A', 'B', 'object']`. Nothing
about `A` or `B` changed — only the order in which Python is told to search them, which is why
mixin order matters and is easy to get wrong silently.
:::

:::solution Exercise 3
```python
class ConsoleLogger:
    def log(self, message):
        print(f"[log] {message}")


class RecordingLogger:
    def __init__(self):
        self.messages = []

    def log(self, message):
        self.messages.append(message)


class PasswordResetter:
    def __init__(self, logger):
        self.logger = logger

    def reset(self, email):
        self.logger.log(f"reset requested for {email}")
        return True
```
```python
import pytest


def test_reset_records_message():
    logger = RecordingLogger()
    resetter = PasswordResetter(logger)

    assert resetter.reset("ada@example.com") is True
    assert logger.messages == ["reset requested for ada@example.com"]


def test_resetter_has_no_send():
    resetter = PasswordResetter(RecordingLogger())
    assert not hasattr(resetter, "send")
```
Injecting the logger means the test needs no stdout capture and no monkeypatching — the
`RecordingLogger` is a five-line class that happens to satisfy the same duck type as
`ConsoleLogger`. `test_resetter_has_no_send` is a slightly unusual test, but it is worth having
here: it locks in the decoupling, so nobody re-adds the inheritance later.
:::

:::solution Exercise 4
```python
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Book:
    title: str
    author: str
    pages: int

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("title cannot be empty")
        if self.pages <= 0:
            raise ValueError(f"pages must be positive, got {self.pages}")

    @property
    def reading_hours(self):
        return round(self.pages / 40, 1)


@dataclass
class Library:
    name: str
    books: list[Book] = field(default_factory=list)

    def add(self, book):
        self.books.append(book)

    @property
    def total_pages(self):
        return sum(book.pages for book in self.books)
```
```python
library = Library("Bedroom shelf")
library.add(Book("Fluent Python", "Ramalho", 792))
library.add(Book("Dune", "Herbert", 412))
print(library.total_pages, library.books[0].reading_hours)
```
```text
1204 19.8
```
`frozen=True` generates `__hash__` from the fields, so books can go in a set or be dict keys, and
`slots=True` means `book.titel = "x"` raises `AttributeError` instead of silently creating a
misspelled attribute. `__post_init__` runs inside the generated `__init__`, so an invalid `Book`
cannot be constructed at all.
:::

:::solution Exercise 5
```python
class BulkDiscount:
    THRESHOLD_CENTS = 5_000

    def __init__(self, percent=10):
        self.percent = percent

    def apply(self, total_cents):
        if total_cents < self.THRESHOLD_CENTS:
            return total_cents
        return round(total_cents * (1 - self.percent / 100))
```
```python
import pytest


@pytest.fixture
def order():
    customer = Customer("Ada", "ada@example.com")
    cart = Order(customer)
    cart.add(Product("W-1", "Widget", 250), 3)     # £7.50
    return cart


def test_below_threshold_is_unchanged(order):
    order.discounts.append(BulkDiscount())
    assert order.total_cents == 750


def test_above_threshold_gets_ten_percent(order):
    order.add(Product("G-7", "Gizmo", 5_000), 1)    # £50.00, subtotal £57.50
    order.discounts.append(BulkDiscount())
    assert order.subtotal_cents == 5_750
    assert order.total_cents == 5_175                # 5750 * 0.9


def test_discounts_apply_in_order(order):
    order.add(Product("G-7", "Gizmo", 5_000), 1)
    order.discounts.append(BulkDiscount(10))
    order.discounts.append(PercentageDiscount(50))
    assert order.total_cents == round(5_175 * 0.5)   # 2588
```
`BulkDiscount` has no base class and imports nothing from the order module — it has an `apply`
method that takes and returns an integer, which is all `Order.total_cents` requires. That is the
`Discount` protocol doing its job. The third test also pins down something easy to get wrong:
discounts compose in list order, so a 10% bulk discount followed by a 50% promo gives a different
result than the reverse.
:::
