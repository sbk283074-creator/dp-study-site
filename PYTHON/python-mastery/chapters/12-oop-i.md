---
chapter: 12
part: 2
title: OOP I: Classes & Objects
summary: Bundle data with the behaviour that belongs to it, write classes that are pleasant to use, and know when a plain function is the better call.
minutes: 45
tags: [classes, objects, self, dunder methods, properties, encapsulation]
---

You have been writing programs as functions that operate on data: a list of dicts goes in, a
formatted total comes out. That works until the data has rules. A bank balance must never go
negative. An order total must be the sum of its lines, recalculated every time a line changes. With
dicts, every one of those rules lives in the head of every programmer who touches the data, and it
breaks the first time someone writes `account["balance"] = -500`. A class lets you put the data and
the rules that govern it in one place, so the rules cannot be forgotten. That is the whole pitch.

## The problem classes solve

Here is the dict approach to a bank account:

```python
def create_account(owner, balance=0):
    return {"owner": owner, "balance": balance}

def deposit(account, amount):
    account["balance"] += amount
    return account["balance"]

def withdraw(account, amount):
    if amount > account["balance"]:
        raise ValueError("insufficient funds")
    account["balance"] -= amount
    return account["balance"]
```

Three problems, and they get worse as the code grows. The shape of the data exists only in
`create_account`, so a typo in a key (`account["ballance"]`) fails at runtime, far from the cause.
Nothing stops `account["balance"] = -500` from any file in the project — the validation is
advisory. And every function takes `account` as its first argument, which is a strong hint that
the data and the behaviour want to be together.

Here is the same thing as a class:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance
```

```python
account = BankAccount("Ada", 100)
account.deposit(50)
print(account.balance)
```

```text
150
```

Now the rules have a home. Anything that wants to change a balance goes through `deposit` or
`withdraw`, and later we will make that the *only* way.

## Classes, instances, and `self`

A class is the blueprint; an object is the thing built from it. A cookie cutter and the cookies —
that is the analogy, and now we can drop it, because the mechanical truth is more useful.

A class is an object that knows how to create instances. Calling it builds one:

```python
a = BankAccount("Ada", 100)
b = BankAccount("Grace", 50)
print(type(a))
print(a is b)
```

```text
<class '__main__.BankAccount'>
False
```

`a` and `b` are independent: same behaviour, separate data. Change `a.balance` and `b` is
untouched.

### What `self` really is

`self` is the instance. That is all it is. When you write:

```python
account.deposit(50)
```

Python translates it to:

```python
BankAccount.deposit(account, 50)
```

The instance is passed as the first argument, automatically. `self` is just the name we give that
first parameter — the name is a convention, not a keyword, but treat it as mandatory. Prove the
equivalence:

```python
account = BankAccount("Ada", 100)
BankAccount.deposit(account, 25)
print(account.balance)
```

```text
125
```

Two consequences worth internalising:

- `self` is why methods can see the instance's data without any globals. `self.balance` means
  "the balance attribute of this particular object".
- Forgetting `self` in a method signature produces `TypeError: deposit() takes 1 positional
  argument but 2 were given`. The two arguments it saw were `account` and `50`; you only declared
  `amount`. This error means "you forgot `self`".

Inside `__init__`, `self.owner = owner` reads as: take the value passed in as `owner` and store it
on this instance under the name `owner`. The parameter and the attribute are different things that
happen to share a name.

## Instance attributes vs class attributes

Attributes assigned on `self` belong to the instance. Attributes assigned directly in the class
body belong to the class and are shared by every instance:

```python
class Dog:
    species = "Canis familiaris"      # class attribute — shared

    def __init__(self, name):
        self.name = name              # instance attribute — per dog
```

```python
rex = Dog("Rex")
bella = Dog("Bella")
print(rex.name, bella.name)
print(rex.species, bella.species)
```

```text
Rex Bella
Canis familiaris Canis familiaris
```

Reading `rex.species` finds nothing on the instance, so Python falls back to the class. Use class
attributes for constants genuinely shared by every instance — a tax rate, a default page size, a
regex pattern — and instance attributes for everything else.

Assignment is where the two diverge: `rex.species = "wolf"` creates an instance attribute that
*shadows* the class one for that object only. The class attribute is unchanged. Nothing was
shared-mutated; you just gave one dog its own value.

## Methods that Python calls for you

Names with two underscores on each side are **dunder** (double underscore) methods. You rarely call
them directly; Python calls them in specific situations. You have already met `__init__` and
`len()` quietly uses `__len__`.

### `__repr__` and `__str__`

Without them, printing an object is useless:

```python
print(BankAccount("Ada", 100))
```

```text
<__main__.BankAccount object at 0x104b3c1d0>
```

- `__str__` is for humans: what `print()` and f-strings call.
- `__repr__` is for developers: what the REPL shows, what appears in tracebacks and inside
  containers. Aim for something you could paste back into Python to recreate the object.

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance!r})"

    def __str__(self):
        return f"{self.owner}'s account: ${self.balance:.2f}"
```

```python
account = BankAccount("Ada", 100)
print(str(account))
print(repr(account))
print([account])
```

```text
Ada's account: $100.00
BankAccount(owner='Ada', balance=100)
[BankAccount(owner='Ada', balance=100)]
```

**Always write `__repr__`.** It costs one line and it improves every debugging session you will
ever have with that class, including the ones inside lists and dicts where `__str__` is not used.
If you only write one, write `__repr__`. If `__str__` is missing, Python falls back to `__repr__`.

### `__eq__`

By default `==` between two objects compares identity — the same rule as `is`. Two accounts with
identical data are not equal:

```python
BankAccount("Ada", 100) == BankAccount("Ada", 100)   # False
```

Define `__eq__` when equal *data* should mean equal objects:

```python
class BankAccount:
    # ... __init__ and the other methods ...

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self.owner == other.owner and self.balance == other.balance
```

```python
BankAccount("Ada", 100) == BankAccount("Ada", 100)   # True
BankAccount("Ada", 100) == "not an account"          # False
```

Returning `NotImplemented` (not `False`, not an exception) for unknown types lets Python try the
comparison the other way around before giving up. `isinstance` is the correct check — testing
`type(other) == BankAccount` would break subclasses, which we meet in Chapter 13.

:::note Defining `__eq__` makes instances unhashable
Python sets `__hash__ = None` on any class that defines `__eq__` without `__hash__`, so:

```python
{BankAccount("Ada", 100)}   # TypeError: unhashable type: 'BankAccount'
```

For a mutable object that is arguably correct — if you can change the balance, the object should
not be a dict key. If you need hashability, define `__hash__` over the same fields:
`return hash((self.owner, self.balance))`. Chapter 13's frozen dataclasses do this for you.
:::

## Encapsulation and the underscore convention

Python has no `private`. The convention is a single leading underscore: `_balance` means "internal,
do not touch, I will not help you if it breaks". It is a signal to humans and to documentation
tools, not a lock — `account._balance` still works, and that is deliberate. Adults-only rules beat
enforcement here.

The practical use is separating the *interface* (methods you promise to maintain) from the
*implementation* (attributes you want to be free to change). Expose behaviour, keep the storage
private.

## `@property`: validate without breaking callers

Say `owner` must never be empty. You could add a `set_owner()` method — but now every caller must
remember to use it, and any code that assigns directly bypasses the check. A property keeps the
plain assignment syntax while routing it through your code:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner          # goes through the setter below
        self.balance = balance

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("owner name cannot be empty")
        self._owner = value.strip()

    def __repr__(self):
        return f"BankAccount(owner={self._owner!r}, balance={self.balance!r})"
```

```python
account = BankAccount("Ada")
account.owner = "  Grace  "       # setter runs, strips whitespace
print(account.owner)              # 'Grace'
account.owner = ""                # ValueError: owner name cannot be empty
```

`account.owner` looks like an attribute access and behaves like a method call. That is the point:
you started with a plain attribute, and when you needed validation you added a property without
changing a single line of calling code. In most languages you would have had to change every
caller to `get_owner()`.

Properties are also the right tool for **computed** values — things that are derived from other
attributes and must never drift out of sync:

```python
class BankAccount:
    # ...
    @property
    def is_empty(self):
        return self.balance == 0

    @property
    def statement(self):
        return f"{self._owner}: {len(self._transactions)} transactions, balance {self.balance}"
```

A computed property is recalculated on every access, so it cannot go stale. If a computation is
expensive, a method (`get_statement()`) is more honest than a property — readers assume property
access is cheap.

## `@classmethod` and `@staticmethod`

Three kinds of method, and the difference is what gets passed in:

| Decorator | First argument | Use it for |
| --- | --- | --- |
| *(none)* | `self` — the instance | normal behaviour |
| `@classmethod` | `cls` — the class | alternative constructors |
| `@staticmethod` | nothing | a helper that belongs to the class conceptually |

**`@classmethod`** is almost always an alternative constructor: a second way to build the object
that is more convenient than the main one.

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    @classmethod
    def from_row(cls, row):
        """Build from a database row: (owner, balance_cents)."""
        owner, cents = row
        return cls(owner, cents / 100)

    @classmethod
    def empty(cls, owner):
        return cls(owner, 0)
```

```python
account = BankAccount.from_row(("Ada", 12500))
print(account.balance)
```

```text
125.0
```

Using `cls(...)` instead of hardcoding `BankAccount(...)` means a subclass gets an instance of
itself, not of the parent. That is the entire reason `@classmethod` exists; if you never subclass,
a module-level function would do.

**`@staticmethod`** is just a function living inside the class namespace because that is where
readers will look for it. It touches neither `self` nor `cls`:

```python
class BankAccount:
    # ...
    @staticmethod
    def is_valid_owner(name):
        return isinstance(name, str) and bool(name.strip())
```

```python
BankAccount.is_valid_owner("Ada")     # True
```

If a static method is not called through the class, it probably wants to be a module-level
function instead. Most static methods are a sign of a function that has not found its home yet.

## Worked example: BankAccount

Everything together, including transfer between accounts:

```python
class BankAccount:
    MAX_WITHDRAWAL = 10_000

    def __init__(self, owner, balance=0):
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner = owner
        self.balance = balance
        self._transactions = []

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if not self.is_valid_owner(value):
            raise ValueError("owner name cannot be empty")
        self._owner = value.strip()

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError(f"deposit must be positive, got {amount}")
        self.balance += amount
        self._transactions.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError(f"withdrawal must be positive, got {amount}")
        if amount > self.MAX_WITHDRAWAL:
            raise ValueError(f"withdrawal exceeds limit of {self.MAX_WITHDRAWAL}")
        if amount > self.balance:
            raise ValueError(f"insufficient funds: balance {self.balance}, requested {amount}")
        self.balance -= amount
        self._transactions.append(("withdraw", amount))
        return self.balance

    def transfer(self, target, amount):
        """Move money to another account. Both halves succeed or neither does."""
        if not isinstance(target, BankAccount):
            raise TypeError("target must be a BankAccount")
        self.withdraw(amount)
        try:
            target.deposit(amount)
        except Exception:
            self.balance += amount          # roll back
            self._transactions.pop()
            raise
        return self.balance

    @property
    def transaction_count(self):
        return len(self._transactions)

    @staticmethod
    def is_valid_owner(name):
        return isinstance(name, str) and bool(name.strip())

    def __repr__(self):
        return f"BankAccount(owner={self._owner!r}, balance={self.balance!r})"

    def __str__(self):
        return f"{self._owner}'s account: ${self.balance:.2f}"
```

```python
ada = BankAccount("Ada", 1000)
grace = BankAccount("Grace", 250)

ada.transfer(grace, 400)
print(ada, "|", grace)
print(ada.transaction_count)

ada.withdraw(20_000)
```

```text
Ada's account: $600.00 | Grace's account: $650.00
1
ValueError: withdrawal exceeds limit of 10000
```

`transfer` is the interesting one: it delegates to `withdraw` and `deposit`, so the validation
rules are written once and apply everywhere. Objects calling methods on other objects is what
object-oriented code actually looks like. And it is directly testable — Chapter 11's pytest
fixtures build these two accounts in three lines, no mocking required.

## When not to use a class

Classes are not a maturity signal. Reach for a function first:

- **One operation on data.** `def area(width, height): return width * height` does not need a
  `Rectangle` class.
- **Two methods, one of which is `__init__`.** That is a function wearing a costume.
- **Behaviour with no state.** A class whose methods never touch `self` is a module.
- **Pure records.** A bundle of fields with no behaviour of its own is a dataclass (Chapter 13) or
  a dict, not a hand-written class.
- **A namespace for constants.** Use a module: `config.py` with `TAX_RATE = 0.2`.

The test: does this data have *rules* or *several* operations that always travel together? A
rectangle needs `area`, `perimeter`, `scale`, `rotate`, and `contains_point` — now a class earns
its keep. Until then, a function is shorter, easier to test, and easier to delete.

:::scenario A customer's balance went negative even though `withdraw()` checks for it
Support escalates: one account shows -£320. You read `withdraw()`. It validates. You read
`deposit()`. It validates. Nobody can find the bug, and it has happened three times this quarter.
:::

:::solution The check was bypassed, not broken — make the balance read-only
Somewhere in a batch job, someone wrote the obvious thing:

```python
account.balance -= fee          # no validation, no transaction log
```

or worse, acted on a cached dict: `row["balance"] -= fee`. Every rule in `withdraw()` is advisory
if the attribute is public and writable. The bug is not in the method; it is in the fact that the
method can be skipped.

Fix it by making the attribute private and exposing only validated behaviour:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        return self._balance
```

Now `account.balance -= fee` raises `AttributeError: property 'balance' of 'BankAccount' object
has no setter`, at the exact line that broke the rule. Which is precisely what you want: a loud
failure at the bad line beats a silent negative balance discovered by a customer.

Then do the two follow-ups, because the class fix alone is not enough:

1. Grep the codebase for `.balance` assignments (`rg "\.balance\s*[-+*/]?="`) — every hit is a
   latent bug. Replace them with a named operation: `account.apply_fee(fee)`.
2. Add a regression test that asserts the property has no setter:
   ```python
   def test_balance_is_read_only():
       account = BankAccount("Ada", 100)
       with pytest.raises(AttributeError):
           account.balance = -320
   ```
   Now the invariant is enforced by the test suite, and the next person who tries to bypass it
   finds out in CI rather than from support.
:::

:::pitfall A mutable class attribute is shared by every instance
```python
class ShoppingCart:
    items = []                    # one list, shared by ALL carts

    def add(self, item):
        self.items.append(item)
```

```python
a = ShoppingCart()
b = ShoppingCart()
a.add("apple")
print(b.items)
```

```text
['apple']
```

Nothing was added to `b`, yet `b.items` contains the apple. `items` was created once, when the
class body executed; every instance reads that same list object. `self.items.append(...)` mutates
it rather than rebinding, so the change is visible everywhere.

The same trap catches default arguments (`def add(self, item, log=[])`) for the same reason: the
default object is created once at definition time.

The fix is to create per-instance state in `__init__`:

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
```

Now each cart gets a fresh list. Keep mutable containers out of the class body entirely; put
immutable constants there (`MAX_WITHDRAWAL = 10_000`, `SPECIES = "Canis familiaris"`) and
everything mutable behind `self`.
:::

## Key takeaways

- A class bundles data with the rules and behaviour that belong to it, so those rules cannot be
  forgotten by callers.
- `self` is the instance, passed automatically as the first argument; `obj.method(x)` is
  `Class.method(obj, x)`.
- Instance attributes are assigned on `self` in `__init__`; class attributes are shared constants
  defined in the class body.
- Always define `__repr__` — it is what you see in the REPL, in tracebacks, and inside containers.
- `__eq__` makes `==` compare data instead of identity, and makes instances unhashable unless you
  also define `__hash__`.
- `_name` marks an attribute as internal; `@property` lets you add validation or computation
  without changing how callers write the code.
- `@classmethod` takes `cls` and is used for alternative constructors; `@staticmethod` takes
  neither and is usually a function that belongs in a module.
- Do not use a class for a single operation on data — a function is shorter, easier to test, and
  easier to delete.

## Practice

- [ ] Write a `Book` class with `title`, `author`, and `pages`. Add `__repr__` and `__str__`, then
      put two books in a list and print it to see which one Python uses.
- [ ] Add `__eq__` to `Book` so two books with the same title and author are equal. Confirm that
      comparing a `Book` to a string returns `False` rather than raising.
- [ ] Add a `@property` called `reading_hours` that returns `pages / 40` rounded to one decimal,
      and a validated `pages` setter that rejects zero or negative values.
- [ ] Extend `BankAccount` with an `@classmethod` called `from_dict` that accepts
      `{"owner": "Ada", "balance": 100}` and builds an account, raising `KeyError`-free errors for
      missing fields.
- [ ] Write a `ShoppingCart` class with `add`, `remove`, `total`, and `__len__`, storing items as a
      list of `(name, price)` tuples created fresh in `__init__`. Then write five pytest tests for
      it, including removing an item that is not there.
- [ ] Refactor a dict-based program from Chapter 9 into a class: pick something with at least one
      validation rule, make the data private, and expose behaviour instead.

## Solutions

:::solution Exercise 1
```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __repr__(self):
        return f"Book(title={self.title!r}, author={self.author!r}, pages={self.pages!r})"

    def __str__(self):
        return f"{self.title} by {self.author}"


books = [Book("The Pragmatic Programmer", "Hunt & Thomas", 352),
         Book("Fluent Python", "Ramalho", 792)]
print(books)
print(books[0])
```
```text
[Book(title='The Pragmatic Programmer', author='Hunt & Thomas', pages=352), Book(title='Fluent Python', author='Ramalho', pages=792)]
The Pragmatic Programmer by Hunt & Thomas
```
Printing the *list* used `__repr__` for each element, while `print(books[0])` used `__str__`.
Containers always use `__repr__`, which is why a good `__repr__` matters more than a pretty
`__str__`.
:::

:::solution Exercise 2
```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.title == other.title and self.author == other.author

    def __repr__(self):
        return f"Book(title={self.title!r}, author={self.author!r}, pages={self.pages!r})"


print(Book("Dune", "Herbert", 412) == Book("Dune", "Herbert", 688))   # True
print(Book("Dune", "Herbert", 412) == "Dune")                          # False
```
`NotImplemented` tells Python "I do not know how to compare to that", so it falls back to identity
comparison and yields `False` instead of raising. Note that `pages` is deliberately excluded from
the comparison — two editions of the same book are the same book. Equality is a design decision,
not a mechanical one.
:::

:::solution Exercise 3
```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages          # routed through the setter

    @property
    def pages(self):
        return self._pages

    @pages.setter
    def pages(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"pages must be a positive integer, got {value!r}")
        self._pages = value

    @property
    def reading_hours(self):
        return round(self.pages / 40, 1)


book = Book("Dune", "Herbert", 412)
print(book.reading_hours)     # 10.3
book.pages = 0                # ValueError: pages must be a positive integer, got 0
```
Because `self.pages = pages` in `__init__` goes through the setter, an invalid page count fails at
construction time. `reading_hours` is computed on access, so it can never disagree with `pages`.
:::

:::solution Exercise 4
```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    @classmethod
    def from_dict(cls, data):
        try:
            owner = data["owner"]
        except KeyError:
            raise ValueError("account data is missing 'owner'") from None
        balance = data.get("balance", 0)
        if balance < 0:
            raise ValueError(f"opening balance cannot be negative, got {balance}")
        return cls(owner, balance)

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance!r})"


print(BankAccount.from_dict({"owner": "Ada", "balance": 100}))
print(BankAccount.from_dict({"owner": "Grace"}))
BankAccount.from_dict({"balance": 5})
```
```text
BankAccount(owner='Ada', balance=100)
BankAccount(owner='Grace', balance=0)
ValueError: account data is missing 'owner'
```
Using `cls(owner, balance)` rather than `BankAccount(...)` means a subclass such as
`SavingsAccount.from_dict(...)` returns a `SavingsAccount`. Translating `KeyError` into a
`ValueError` with a useful message is worth the three lines: the caller sees what is actually
wrong instead of a bare key name.
:::

:::solution Exercise 5
```python
class ShoppingCart:
    def __init__(self):
        self._items = []

    def add(self, name, price):
        self._items.append((name, price))

    def remove(self, name):
        for index, (item_name, _) in enumerate(self._items):
            if item_name == name:
                del self._items[index]
                return
        raise ValueError(f"{name!r} is not in the cart")

    @property
    def total(self):
        return sum(price for _, price in self._items)

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"ShoppingCart({self._items!r})"
```
```python
import pytest


@pytest.fixture
def cart():
    cart = ShoppingCart()
    cart.add("apple", 0.50)
    cart.add("book", 12.00)
    return cart


def test_total(cart):
    assert cart.total == 12.50

def test_len(cart):
    assert len(cart) == 2

def test_remove_existing(cart):
    cart.remove("apple")
    assert cart.total == 12.00

def test_remove_missing_raises(cart):
    with pytest.raises(ValueError, match="not in the cart"):
        cart.remove("kumquat")

def test_new_cart_is_empty():
    assert len(ShoppingCart()) == 0
```
`self._items = []` inside `__init__` is what prevents the shared-mutable-state bug from the
pitfall — each `ShoppingCart()` gets its own list. Defining `__len__` also makes `if not cart`
work, because an object with `__len__` is falsy when its length is zero.
:::

:::solution Exercise 6
Take the user-registration validation from Chapter 9 — a dict plus three free functions:

```python
# before: the rules live outside the data
def validate(user):
    if len(user["password"]) < 12:
        raise ValueError("password too short")
    if "@" not in user["email"]:
        raise ValueError("bad email")

user = {"email": "ada@example.com", "password": "hunter2"}
validate(user)
user["password"] = "x"          # nothing stops this
```

```python
# after: the rules live with the data
class User:
    MIN_PASSWORD = 12

    def __init__(self, email, password):
        self.email = email
        self.password = password

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError(f"invalid email: {value!r}")
        self._email = value

    @property
    def password(self):
        return "***"

    @password.setter
    def password(self, value):
        if len(value) < self.MIN_PASSWORD:
            raise ValueError(f"password must be at least {self.MIN_PASSWORD} characters")
        self._password = value

    def check_password(self, candidate):
        return candidate == self._password

    def __repr__(self):
        return f"User(email={self._email!r})"


user = User("ada@example.com", "correct-horse-battery")
user.password = "x"             # ValueError: password must be at least 12 characters
```
The win is not shorter code — it is longer. The win is that an invalid `User` cannot exist: the
rules run in `__init__` and on every assignment, so no code path, batch job, or future teammate
can produce a bad one. The password getter returns a placeholder so a stray `print(user.password)`
never leaks a real credential into a log, and `__repr__` omits it for the same reason.
:::
