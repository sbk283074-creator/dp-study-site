---
chapter: 54
part: 10
title: Patterns You Will Actually Use
summary: Six shapes that get written again and again, and what each one costs rather than what it is called. Every block measures the pattern against the thing it replaced -- comparisons, lines, frames, functions that must change -- and the measurements keep disagreeing with the usual argument for the pattern.
minutes: 100
tags: [architecture, strategy, dispatch, observer, adapter, factory, registry, composite, decorator, protocol, interfaces, layers, abstraction]
---

A pattern is a name for a shape somebody already wrote. That is the whole of what the catalogue is,
and it is worth saying plainly because the usual way the subject is taught turns the names into
targets: you learn twenty-three of them and then go looking for somewhere to put one.

The useful question about any shape is not which pattern it is. It is what the shape costs, what it
buys, and whether the thing it buys is something this program needs. All three of those are
countable, and this chapter counts them. Every block compares a pattern against the thing it
replaced, and several of the comparisons come out against the pattern.

There is a second theme, and it is specific to Python. Several of the catalogue's patterns exist
because the languages it was written for had no first-class functions. This one does. A dispatch
table is a dictionary, `@` is the decorator pattern, `with` is the template method, and
`functools.singledispatch` is the strategy pattern with the selection already written. Recognising
the pattern is still worth doing -- a name is how you talk about a design -- but recognising it is
not the same as needing to build it.

## The conditional that selects behaviour

Start with the shape everybody writes first, because the measurement is the easiest to take and the
result is not the one the pattern's advocates claim.

```python run
"""Chapter 54 -- the strategy pattern, and what adding a case costs.

The same five shipping methods, written twice: as a chain of comparisons
and as a table. Both are measured, and the measurement of "how many
places mention this name" is taken from the source of the file you are
reading rather than asserted.
"""

import pathlib

CHAIN_ORDER = ["standard", "express", "overnight", "pickup", "freight"]


# --- chain
def cost_chain(order, method, count):
    count[0] = 0

    count[0] += 1
    if method == "standard":
        return order * 1.0

    count[0] += 1
    if method == "express":
        return order * 1.4 + 2.0

    count[0] += 1
    if method == "overnight":
        return order * 2.0 + 8.0

    count[0] += 1
    if method == "pickup":
        return 0.0

    count[0] += 1
    if method == "freight":
        return order * 0.8 + 12.0

    raise ValueError("unknown method: " + method)


# --- default
def cost_chain_default(order, method, count):
    """The same chain with the last branch written as a default, which is
    the version that ships."""
    count[0] = 0

    count[0] += 1
    if method == "express":
        return order * 1.4 + 2.0

    count[0] += 1
    if method == "overnight":
        return order * 2.0 + 8.0

    count[0] += 1
    if method == "pickup":
        return 0.0

    count[0] += 1
    if method == "freight":
        return order * 0.8 + 12.0

    return order * 1.0


# --- table
def rate_standard(order):
    return order * 1.0


def rate_express(order):
    return order * 1.4 + 2.0


def rate_overnight(order):
    return order * 2.0 + 8.0


def rate_pickup(order):
    return 0.0


def rate_freight(order):
    return order * 0.8 + 12.0


RATES = {
    "standard": rate_standard,
    "express": rate_express,
    "overnight": rate_overnight,
    "pickup": rate_pickup,
    "freight": rate_freight,
}


def cost_table(order, method, count):
    count[0] = 1
    try:
        return RATES[method](order)
    except KeyError:
        raise ValueError("unknown method: " + method) from None
# --- end


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
# The chain region stops at the second chain, so that the line count below
# compares one chain against one table. `cost_chain_default` is a variant
# used only by the last table, and counting it here would compare two
# implementations against one.
CHAIN_SRC = SOURCE.split("# --- chain")[1].split("# --- default")[0]
TABLE_SRC = SOURCE.split("# --- table")[1].split("# --- end")[0]

UNKNOWN = ["sameday", "drone", "barge"]


def mentions(source, name):
    return sum(1 for line in source.splitlines() if name in line)


def main():
    print(f"  methods                             {len(CHAIN_ORDER)}")
    print(f"  lines in the chain region           "
          f"{len(CHAIN_SRC.strip().splitlines())}")
    print(f"  lines in the table region           "
          f"{len(TABLE_SRC.strip().splitlines())}")
    print()

    print("    method       comparisons    lines mentioning the name")
    print("                 chain table      chain table")
    total_chain = 0
    for method in CHAIN_ORDER:
        count = [0]
        cost_chain(10.0, method, count)
        total_chain += count[0]
        print("    {:<12}{:>6}{:>6}{:>11}{:>6}".format(
            method, count[0], 1, mentions(CHAIN_SRC, method),
            mentions(TABLE_SRC, method)))
    print()
    print("    {:<12}{:>6}{:>6}".format("total", total_chain, len(CHAIN_ORDER)))
    print()

    print(f"  the chain compares the name {total_chain} times to resolve "
          f"{len(CHAIN_ORDER)} calls,")
    print("  and the table compares it once per call. the chain's cost grows")
    print("  with the number of cases and the table's does not.")
    print()
    print("  the table is also the longer of the two, and it mentions every")
    print("  name twice: once as a function and once as a key. so the usual")
    print("  argument for the pattern -- that it is tidier -- is not what the")
    print("  numbers say. it is more code.")
    print()
    print("  what it buys is in the last table.")
    print()

    print("    an unknown method                the charge it produced")
    for method in UNKNOWN:
        count = [0]
        try:
            cost_chain(10.0, method, count)
            chain = "charged"
        except ValueError:
            chain = "refused"
        default = cost_chain_default(10.0, method, [0])
        count = [0]
        try:
            cost_table(10.0, method, count)
            table = "charged"
        except ValueError:
            table = "refused"
        print("    {:<32}{:<10}{:<13}{}".format(
            method, chain, "charged %.1f" % default, table))
    print()
    print("  both the chain and the table refuse an unknown method. the chain")
    print("  with a default branch charges it the standard rate instead, and")
    print("  nothing anywhere says so -- the request succeeds, the customer is")
    print("  billed, and the only signal is a number that is plausible.")
    print()
    print("  that is the actual difference between the two shapes. it is not")
    print("  line count and it is not speed. a chain has a place where a case")
    print("  can be forgotten, and forgetting it is a *fall-through* to")
    print("  whichever branch happens to be last. a table has no such place,")
    print("  because a missing key is a `KeyError` on the first call.")


main()
```

```text
  methods                             5
  lines in the chain region           24
  lines in the table region           35

    method       comparisons    lines mentioning the name
                 chain table      chain table
    standard         1     1          1     2
    express          2     1          1     2
    overnight        3     1          1     2
    pickup           4     1          1     2
    freight          5     1          1     2

    total           15     5

  the chain compares the name 15 times to resolve 5 calls,
  and the table compares it once per call. the chain's cost grows
  with the number of cases and the table's does not.

  the table is also the longer of the two, and it mentions every
  name twice: once as a function and once as a key. so the usual
  argument for the pattern -- that it is tidier -- is not what the
  numbers say. it is more code.

  what it buys is in the last table.

    an unknown method                the charge it produced
    sameday                         refused   charged 10.0 refused
    drone                           refused   charged 10.0 refused
    barge                           refused   charged 10.0 refused

  both the chain and the table refuse an unknown method. the chain
  with a default branch charges it the standard rate instead, and
  nothing anywhere says so -- the request succeeds, the customer is
  billed, and the only signal is a number that is plausible.

  that is the actual difference between the two shapes. it is not
  line count and it is not speed. a chain has a place where a case
  can be forgotten, and forgetting it is a *fall-through* to
  whichever branch happens to be last. a table has no such place,
  because a missing key is a `KeyError` on the first call.
```

Five shipping methods. The chain compares the method name 15 times to resolve five calls and the
table compares it once per call, which is the argument everybody makes and it is true.

The line count goes the other way. The chain region is 24 lines and the table region is 35, and the
third column says the same thing from a different angle: the table mentions every name twice -- once
as a function and once as a key -- where the chain mentions each of them once. So the table is more
code, not less, and "tidier" is not what was bought.

What was bought is in the last table. An unknown method is refused by both, and the chain whose last
branch is a default charges it the standard rate instead. The request succeeds, the customer is
billed, and the only signal is a number that looks plausible. That is the difference: a chain has a
place where a case can be forgotten, and forgetting it is a fall-through to whichever branch happens
to be last. A table has no such place, because a missing key is a `KeyError` on the first call.

## Dispatch that is already in the language

`functools.singledispatch` is the strategy pattern as a library function, and the two things worth
knowing about it are which argument it looks at and what it does with a subclass.

```python run
"""Chapter 54 -- dispatch, which Python already has.

`functools.singledispatch` is the strategy pattern as a language
feature. It dispatches on the type of one argument, and the two things
worth knowing are which argument and what it does with a subclass.
"""

from functools import singledispatch


@singledispatch
def render(value):
    return "the default"


@render.register
def _(value: int):
    return "int"


@render.register
def _(value: str):
    return "str"


@render.register
def _(value: list):
    return "list"


class Money(int):
    """A subclass of a registered type, which is the case that decides
    whether the dispatch is on the class or on the name."""


@singledispatch
def combine(first, second):
    return "the default"


@combine.register
def _(first: int, second):
    return "int first"


@combine.register
def _(first: str, second):
    return "str first"


VALUES = [1, True, 1.0, "a", [1], {"a": 1}, (1,), None, Money(707)]

CALLS = [
    (1, "a"),
    ("a", 1),
    (1.0, 1),
    ([1], 1),
    (True, "a"),
]


def main():
    print(f"  handlers registered                 {len(render.registry)}")
    print(f"  values                              {len(VALUES)}")
    print()

    print("    value                type        handler reached")
    for value in VALUES:
        print("    {:<21}{:<12}{}".format(
            repr(value), type(value).__name__, render(value)))
    print()

    reached = {}
    for value in VALUES:
        reached.setdefault(render(value), []).append(repr(value))
    default = reached.get("the default", [])
    print(f"  {len(default)} of the {len(VALUES)} reached the default, and the one")
    print("  worth reading is `True`. `bool` is a subclass of `int`, so it")
    print("  reached the int handler -- and so did `Money(7)`, which is a")
    print("  subclass you wrote. the dispatch walks the mro rather than")
    print("  matching the class name, which is why registering `int` is not")
    print("  the same as registering `int` and only `int`.")
    print()

    print("  the second argument decides nothing")
    print()
    print("    call                 first arg type   handler")
    for first, second in CALLS:
        print("    {:<21}{:<16}{}".format(
            "combine({}, {})".format(repr(first), repr(second)),
            type(first).__name__, combine(first, second)))
    print()
    print("  `combine(1, 'a')` and `combine(1, 1)` reach the same handler,")
    print("  and `combine('a', 1)` and `combine('a', 1.0)` reach another. the")
    print("  type of the second argument is never consulted, which is the")
    print("  limit of the mechanism and also its documentation: the function")
    print("  is dispatched on one value and every other argument is data.")
    print()
    print("  so this is the strategy pattern with the selection already")
    print("  written, and the trade is the same one as the table: the")
    print("  dispatch is a registration rather than a branch, and a type")
    print("  nobody registered is a default rather than a silent")
    print("  fall-through -- as long as you decide what the default is.")
    print("  the default here returns a string, which is the wrong answer")
    print("  that looks like the right one; raising would have been better.")


main()
```

```text
  handlers registered                 4
  values                              9

    value                type        handler reached
    1                    int         int
    True                 bool        int
    1.0                  float       the default
    'a'                  str         str
    [1]                  list        list
    {'a': 1}             dict        the default
    (1,)                 tuple       the default
    None                 NoneType    the default
    707                  Money       int

  4 of the 9 reached the default, and the one
  worth reading is `True`. `bool` is a subclass of `int`, so it
  reached the int handler -- and so did `Money(7)`, which is a
  subclass you wrote. the dispatch walks the mro rather than
  matching the class name, which is why registering `int` is not
  the same as registering `int` and only `int`.

  the second argument decides nothing

    call                 first arg type   handler
    combine(1, 'a')      int             int first
    combine('a', 1)      str             str first
    combine(1.0, 1)      float           the default
    combine([1], 1)      list            the default
    combine(True, 'a')   bool            int first

  `combine(1, 'a')` and `combine(1, 1)` reach the same handler,
  and `combine('a', 1)` and `combine('a', 1.0)` reach another. the
  type of the second argument is never consulted, which is the
  limit of the mechanism and also its documentation: the function
  is dispatched on one value and every other argument is data.

  so this is the strategy pattern with the selection already
  written, and the trade is the same one as the table: the
  dispatch is a registration rather than a branch, and a type
  nobody registered is a default rather than a silent
  fall-through -- as long as you decide what the default is.
  the default here returns a string, which is the wrong answer
  that looks like the right one; raising would have been better.
```

Nine values, four handlers registered, and four of the nine reach the default. The one to read twice
is `True`: `bool` is a subclass of `int`, so it reached the int handler, and so did a `Money` class
defined a few lines above. The dispatch walks the mro rather than matching the class, which is the
behaviour you want and also the behaviour that makes "register `int`" mean something wider than it
looks.

The second table is the limit. `combine(1, "a")` and `combine(1, 1)` reach the same handler and
`combine("a", 1)` reaches another, because the type of the second argument is never consulted. That
is the mechanism's boundary and also its documentation: the function is dispatched on one value and
every other argument is data.

The trade is the same as the table's. The dispatch is a registration rather than a branch, and a type
nobody registered is a default rather than a silent fall-through -- as long as you decide what the
default is. The default here returns a string, which is the wrong answer that looks like the right
one. Raising would have been better, and that decision is the one the pattern does not make for you.

## The list of callbacks

A subscriber list is the observer pattern and it is three lines. What it does not answer is what
happens when one of them raises, and whether the order they run in is part of the contract.

```python run
"""Chapter 54 -- the observer pattern, and the two questions it raises.

A list of callbacks is the whole pattern. What it does not answer is
what happens when one of them raises, and whether the order they run in
is part of the contract.
"""

import itertools


def make_subscribers():
    """Six subscribers, the third of which raises."""
    ran = []

    def first(event):
        ran.append("first")

    def second(event):
        ran.append("second")

    def third(event):
        raise RuntimeError("third")

    def fourth(event):
        ran.append("fourth")

    def fifth(event):
        ran.append("fifth")

    def sixth(event):
        ran.append("sixth")

    return ran, [first, second, third, fourth, fifth, sixth]


def notify_naive(subscribers, event):
    """What the first version of this always looks like."""
    for subscriber in subscribers:
        subscriber(event)


def notify_isolated(subscribers, event):
    """The same loop, with each subscriber's failure kept to itself."""
    failures = []
    for subscriber in subscribers:
        try:
            subscriber(event)
        except Exception as exc:
            failures.append((subscriber.__name__, type(exc).__name__))
    return failures


FACTORS = [2, 3, 5]


def run_order(order):
    """Three subscribers that each fold the shared value, so the result
    is a function of the order they run in."""
    state = [0]
    for factor in order:
        state[0] = state[0] * factor + 1
    return state[0]


def main():
    print(f"  subscribers                         {len(make_subscribers()[1])}")
    print()

    ran, subscribers = make_subscribers()
    try:
        notify_naive(subscribers, "order placed")
        outcome = "no failure"
    except RuntimeError:
        outcome = "raised"
    print(f"  the loop that does not isolate failures: {outcome} after "
          f"{len(ran)} of the")
    print(f"  {len(subscribers)} subscribers ran. the three after the failure never")
    print("  hear about the event, and the caller never gets a return value,")
    print("  so the list of who did run is not available either.")
    print()

    ran, subscribers = make_subscribers()
    failures = notify_isolated(subscribers, "order placed")
    print(f"  the loop that isolates failures: {len(ran)} of the "
          f"{len(subscribers)} ran, and")
    print("  the failures are returned:")
    for name, kind in failures:
        print(f"    {name}  {kind}")
    print()
    print("  both loops are three lines. the difference is that the second")
    print("  one treats a subscriber as something that can be wrong, which is")
    print("  the only assumption a list of callbacks needs and the one the")
    print("  first version does not make.")
    print()

    orders = list(itertools.permutations(FACTORS))
    outcomes = {}
    for order in orders:
        outcomes.setdefault(run_order(order), []).append(order)
    print(f"  the order the subscribers run in")
    print()
    print("    order        the value it leaves")
    for order in orders:
        print("    {:<12}{}".format(
            ",".join(str(f) for f in order), run_order(order)))
    print()
    print(f"  {len(outcomes)} of the {len(orders)} orderings leave a different value.")
    print("  three subscribers that each fold a shared value commute with")
    print("  nothing, so the order is not an implementation detail -- it is")
    print("  part of the result, and nothing in the pattern says what it is.")
    print()
    print("  that is the question a subscriber list raises and does not")
    print("  answer. if the subscribers only report, any order will do and the")
    print("  isolation is the whole fix. if any of them can change the value")
    print("  the others see, the order is a contract, and a contract that is")
    print("  not written down is one that a later refactor will change.")


main()
```

```text
  subscribers                         6

  the loop that does not isolate failures: raised after 2 of the
  6 subscribers ran. the three after the failure never
  hear about the event, and the caller never gets a return value,
  so the list of who did run is not available either.

  the loop that isolates failures: 5 of the 6 ran, and
  the failures are returned:
    third  RuntimeError

  both loops are three lines. the difference is that the second
  one treats a subscriber as something that can be wrong, which is
  the only assumption a list of callbacks needs and the one the
  first version does not make.

  the order the subscribers run in

    order        the value it leaves
    2,3,5       21
    2,5,3       19
    3,2,5       16
    3,5,2       13
    5,2,3       10
    5,3,2       9

  6 of the 6 orderings leave a different value.
  three subscribers that each fold a shared value commute with
  nothing, so the order is not an implementation detail -- it is
  part of the result, and nothing in the pattern says what it is.

  that is the question a subscriber list raises and does not
  answer. if the subscribers only report, any order will do and the
  isolation is the whole fix. if any of them can change the value
  the others see, the order is a contract, and a contract that is
  not written down is one that a later refactor will change.
```

Six subscribers, the third of which raises. The loop that does not isolate failures raised after 2 of
the 6 had run, so the last three never hear about the event -- and because the exception left the
loop, the caller does not get the list of who did run either. The loop that isolates failures ran 5
of the 6 and returned the failure as data.

Both loops are three lines. The difference is that the second treats a subscriber as something that
can be wrong, which is the only assumption a list of callbacks needs.

The second half is the question nobody writes down. Three subscribers that each fold a shared value
leave a different result in every one of the 6 orderings. So the order is not an implementation
detail, it is part of the result -- and nothing in the pattern says what it is. If the subscribers
only report, any order will do and isolation is the whole fix. If any of them can change the value
the others see, the order is a contract, and a contract that is not written down is one a later
refactor will change.

## The dependency whose names are everywhere

An adapter is the answer to a question you can ask before writing it, and the question is a count.

```python run
"""Chapter 54 -- the adapter pattern, measured as a count of places.

A vendor library whose records are dictionaries with the vendor's own
field names. Two consumers read them: one that reads the vendor's names
directly, and one that reads them behind a single translation. Then the
vendor renames a field, which is the only event the pattern is for.
"""

# what each consumer needs, and the vendor field it comes from
DIRECT_READS = [
    ("name", "user_name"),
    ("joined", "created"),
    ("tier", "plan_code"),
    ("active", "is_enabled"),
]


class VendorV1:
    def fetch(self):
        return [{"user_name": "ada", "created": 1,
                 "plan_code": "pro", "is_enabled": True}]


class VendorV2:
    """The same vendor, one release later."""

    def fetch(self):
        return [{"username": "ada", "created_at": 1,
                 "plan": "pro", "enabled": True}]


def direct(record):
    """Every field read is a place the vendor's names appear."""
    out = {}
    for label, field in DIRECT_READS:
        try:
            out[label] = record[field]
        except KeyError:
            out[label] = "MISSING"
    return out


def translate(record):
    """The one place the vendor's names appear."""
    return {
        "name": record["user_name"],
        "joined": record["created"],
        "tier": record["plan_code"],
        "active": record["is_enabled"],
    }


def adapted(record):
    try:
        return translate(record)
    except KeyError as exc:
        return {"translation failed": "MISSING " + str(exc)}


def survey(consumer, vendor):
    rows = []
    for record in vendor.fetch():
        rows.append(consumer(record))
    return rows


def main():
    print(f"  fields the consumer needs           {len(DIRECT_READS)}")
    print(f"  places the direct version reads one  {len(DIRECT_READS)}")
    print("  places the adapted version reads one 1")
    print()

    for label, vendor in (("vendor v1", VendorV1()), ("vendor v2", VendorV2())):
        print(f"    {label}")
        for name, consumer in (("direct", direct), ("adapted", adapted)):
            rows = survey(consumer, vendor)
            broken = sum(1 for row in rows
                         for value in row.values()
                         if isinstance(value, str) and value.startswith("MISSING"))
            print("      {:<9}{} of {} reads missing".format(
                name, broken, len(rows[0])))
        print()

    print("  under v1 both versions work, and that is the whole reason the")
    print("  pattern gets skipped. the two look identical in the output and")
    print("  the direct one is shorter, so the direct one ships.")
    print()
    print("  under v2 the direct version has four places to change and the")
    print("  adapted version has one. the number that matters is not four; it")
    print("  is that the four are spread across the consumer, wherever a field")
    print("  happened to be needed, and the one is a single function whose")
    print("  whole job is that translation.")
    print()
    print("  the adapter is not an extra layer for its own sake. it is the")
    print("  answer to a question you can ask before writing it: when this")
    print("  dependency changes, how many places will I be looking at? if the")
    print("  answer is one, the adapter is already there and you should keep")
    print("  it. if the answer is one, and it is one because there is only one")
    print("  call site, then the adapter is a layer with nothing to do.")


main()
```

```text
  fields the consumer needs           4
  places the direct version reads one  4
  places the adapted version reads one 1

    vendor v1
      direct   0 of 4 reads missing
      adapted  0 of 4 reads missing

    vendor v2
      direct   4 of 4 reads missing
      adapted  1 of 1 reads missing

  under v1 both versions work, and that is the whole reason the
  pattern gets skipped. the two look identical in the output and
  the direct one is shorter, so the direct one ships.

  under v2 the direct version has four places to change and the
  adapted version has one. the number that matters is not four; it
  is that the four are spread across the consumer, wherever a field
  happened to be needed, and the one is a single function whose
  whole job is that translation.

  the adapter is not an extra layer for its own sake. it is the
  answer to a question you can ask before writing it: when this
  dependency changes, how many places will I be looking at? if the
  answer is one, the adapter is already there and you should keep
  it. if the answer is one, and it is one because there is only one
  call site, then the adapter is a layer with nothing to do.
```

Four fields, four places in the direct version and one in the adapted one. Under v1 both work, which
is exactly why the pattern gets skipped -- the two are indistinguishable in the output and the
direct one is shorter. Under v2 the direct version has four reads to fix and the adapted one has one,
in a function whose only job is that translation.

The number that matters is not four. It is that the four are spread across the consumer, wherever a
field happened to be needed, and the one is adjacent to itself. And the honest version of the
argument is that with a single call site there is no difference at all: the adapter only divides a
number that is greater than one.

## The registry, and what builds it

The factory pattern in Python is a dictionary with a decorator in front of it. Two things go wrong
with it and neither of them is in the decorator.

```python run
"""Chapter 54 -- the factory pattern, as a registry.

A decorator that files a function under its own name, which is the
whole of the pattern. Two things go wrong with it, and neither is in the
decorator: a handler that lives in a module nobody imported, and a
lookup that goes through `globals()` instead of through the registry.
"""

REGISTRY = {}


def handles(fn):
    REGISTRY[fn.__name__] = fn
    return fn


@handles
def read_csv(source):
    return "csv from " + source


@handles
def read_json(source):
    return "json from " + source


@handles
def read_tsv(source):
    return "tsv from " + source


# two more handlers, in a module that nothing has imported yet
LAZY = [("read_xml", lambda source: "xml from " + source),
        ("read_yaml", lambda source: "yaml from " + source)]


def import_lazy_module():
    """What importing the module would do, as a side effect of the
    decorator running at import time."""
    for name, fn in LAZY:
        REGISTRY[name] = fn


REQUESTED = ["read_csv", "read_json", "read_tsv", "read_xml", "read_yaml",
             "handles", "main", "REGISTRY"]


def resolve(name):
    return REGISTRY.get(name)


def main():
    print(f"  handlers the service defines        {len(REGISTRY) + len(LAZY)}")
    print(f"  handlers in the registry at import  {len(REGISTRY)}")
    print()

    print("    request             before the import   after")
    before = {name: resolve(name) for name in REQUESTED}
    import_lazy_module()
    after = {name: resolve(name) for name in REQUESTED}
    for name in REQUESTED:
        print("    {:<20}{:<21}{}".format(
            name,
            "found" if before[name] else "not in the registry",
            "found" if after[name] else "not in the registry"))
    print()
    print(f"  importing the other module took the registry from "
          f"{sum(1 for n in REQUESTED if before[n])} to "
          f"{sum(1 for n in REQUESTED if after[n])} of the "
          f"{len(REQUESTED)} requests.")
    print("  the registration happened as a side effect of an import that")
    print("  nobody wrote for that reason, so which handlers exist depends on")
    print("  which modules the process happened to touch -- and the failure")
    print("  is a missing key at request time, in a different file from the")
    print("  handler that was never registered.")
    print()

    print("    how a name becomes a handler")
    for label, lookup in (("the registry", resolve),
                          ("globals()", lambda n: globals().get(n))):
        found = [n for n in REQUESTED if lookup(n)]
        print("      {:<14}{} of {} requests resolved".format(
            label, len(found), len(REQUESTED)))
    via_globals = [n for n in REQUESTED if globals().get(n)]
    extra = [n for n in via_globals if n not in REGISTRY]
    print()
    print(f"  `globals()` resolved {len(extra)} names the registry does not have, and")
    print(f"  they are {', '.join('`' + n + '`' for n in extra)}. none of them is a")
    print("  format handler, and a lookup that goes through the module's own")
    print("  namespace cannot tell the difference -- it answers with whatever")
    print("  the name happens to be bound to, which is the same failure as")
    print("  the resolver in the untrusted-data chapter, one layer up.")
    print()
    print("  the registry is worth having for that reason rather than for the")
    print("  decorator. it is a list of the things that are allowed to answer,")
    print("  written where you can read it, and the import-order problem is")
    print("  the price: the list is built by side effects, so it is only")
    print("  complete once everything that contributes to it has been")
    print("  imported. importing the handler modules explicitly, for that")
    print("  reason, is the fix.")


main()
```

```text
  handlers the service defines        5
  handlers in the registry at import  3

    request             before the import   after
    read_csv            found                found
    read_json           found                found
    read_tsv            found                found
    read_xml            not in the registry  found
    read_yaml           not in the registry  found
    handles             not in the registry  not in the registry
    main                not in the registry  not in the registry
    REGISTRY            not in the registry  not in the registry

  importing the other module took the registry from 3 to 5 of the 8 requests.
  the registration happened as a side effect of an import that
  nobody wrote for that reason, so which handlers exist depends on
  which modules the process happened to touch -- and the failure
  is a missing key at request time, in a different file from the
  handler that was never registered.

    how a name becomes a handler
      the registry  5 of 8 requests resolved
      globals()     6 of 8 requests resolved

  `globals()` resolved 3 names the registry does not have, and
  they are `handles`, `main`, `REGISTRY`. none of them is a
  format handler, and a lookup that goes through the module's own
  namespace cannot tell the difference -- it answers with whatever
  the name happens to be bound to, which is the same failure as
  the resolver in the untrusted-data chapter, one layer up.

  the registry is worth having for that reason rather than for the
  decorator. it is a list of the things that are allowed to answer,
  written where you can read it, and the import-order problem is
  the price: the list is built by side effects, so it is only
  complete once everything that contributes to it has been
  imported. importing the handler modules explicitly, for that
  reason, is the fix.
```

Five handlers are defined and three are in the registry, because the other two live in a module
nothing has imported. The registration is a side effect of an import that nobody wrote for that
reason, so which handlers exist depends on which modules the process happened to touch -- and the
failure is a missing key at request time, in a different file from the handler that was never
registered. Importing the handler modules explicitly, for that reason, is the fix.

The second table is the reason to prefer the registry over a lookup that goes through the module's
own namespace. The registry resolved 5 of 8 requests and `globals()` resolved 6, and they are not
the same five. `globals()` answers for `handles`, `main` and `REGISTRY`, none of which is a format
handler, and it has no answer for `read_xml` or `read_yaml`, which are handlers defined inside a list
rather than at module level. So the two lookups disagree in both directions, and the direction that
matters is the first one: a lookup that goes through `globals()` cannot tell a handler from anything
else the module happens to define, which is the same failure as the resolver in the untrusted-data
chapter, one layer up.

## The tree that answers the same question

The composite pattern gives a leaf and a branch the same interface. The claim is that a new kind of
node is one new class, and that is measurable: count the implementations against the number of
nodes.

```python run
"""Chapter 54 -- the composite pattern.

A tree whose leaves and whose branches answer the same questions. The
pattern's claim is that a new kind of node is one new class, and that is
measurable: count the implementations against the number of nodes.
"""


class Node:
    kind = "node"

    def size(self, visits):
        raise NotImplementedError

    def count(self):
        raise NotImplementedError


class File(Node):
    kind = "file"

    def __init__(self, name, size):
        self.name = name
        self._size = size

    def size(self, visits):
        visits[0] += 1
        return self._size

    def count(self):
        return 1


class Dir(Node):
    kind = "dir"

    def __init__(self, name, children):
        self.name = name
        self.children = children

    def size(self, visits):
        visits[0] += 1
        return sum(child.size(visits) for child in self.children)

    def count(self):
        return 1 + sum(child.count() for child in self.children)


class Cached(Node):
    """The same interface again, with the answer remembered. This is the
    node that makes the pattern pay, and it is also the node that has to
    know about invalidation."""

    def __init__(self, child):
        self.child = child
        self._cached = None

    def size(self, visits):
        visits[0] += 1
        if self._cached is None:
            self._cached = self.child.size(visits)
        return self._cached

    def count(self):
        return self.child.count()


TREE = Dir("root", [
    File("readme.md", 12),
    Dir("src", [
        File("main.py", 40),
        File("util.py", 15),
        Dir("lib", [File("a.py", 8), File("b.py", 9)]),
    ]),
    Dir("docs", [File("index.md", 30), File("api.md", 22)]),
    File("setup.py", 6),
])


def nodes(node):
    yield node
    for child in getattr(node, "children", []):
        yield from nodes(child)


def main():
    kinds = {}
    for node in nodes(TREE):
        kinds[node.kind] = kinds.get(node.kind, 0) + 1
    implementations = [File, Dir, Cached]
    print(f"  nodes in the tree                   {sum(kinds.values())}")
    for kind in ("file", "dir"):
        print("    {:<34}{}".format(kind, kinds[kind]))
    print(f"  implementations of the interface    {len(implementations)}")
    print("    {:<34}{}".format(
        "and the node types the tree uses", len(set(type(n) for n in nodes(TREE)))))
    print()

    print(f"  the whole tree is {TREE.count()} entries and "
          f"{TREE.size([0])} bytes.")
    print()

    print("    query on the root          nodes visited")
    for label in ("the first", "the second", "the third"):
        visits = [0]
        TREE.size(visits)
        print("    {:<27}{}".format(label, visits[0]))
    print()
    print("  every query walks every node. the pattern gives the leaf and the")
    print("  branch the same interface, and it does not give them the same")
    print("  cost -- a branch is a fold over its children, so asking the root")
    print("  a question is asking the whole tree that question.")
    print()

    cached = Cached(TREE)
    print("    the same, with one caching node at the root")
    for label in ("the first", "the second", "the third"):
        visits = [0]
        cached.size(visits)
        print("    {:<27}{}".format(label, visits[0]))
    print()
    print("  the caching node implements the same interface, so nothing above")
    print("  it changed and nothing above it can tell. that is the pattern")
    print("  working exactly as advertised.")
    print()
    print("  it is also the node that has to be told when the answer stops")
    print("  being true, and nothing in the interface has a method for that.")
    print("  the pattern made the tree uniform and left invalidation as the")
    print("  thing the uniform interface cannot express.")


main()
```

```text
  nodes in the tree                   12
    file                              8
    dir                               4
  implementations of the interface    3
    and the node types the tree uses  2

  the whole tree is 12 entries and 142 bytes.

    query on the root          nodes visited
    the first                  12
    the second                 12
    the third                  12

  every query walks every node. the pattern gives the leaf and the
  branch the same interface, and it does not give them the same
  cost -- a branch is a fold over its children, so asking the root
  a question is asking the whole tree that question.

    the same, with one caching node at the root
    the first                  13
    the second                 1
    the third                  1

  the caching node implements the same interface, so nothing above
  it changed and nothing above it can tell. that is the pattern
  working exactly as advertised.

  it is also the node that has to be told when the answer stops
  being true, and nothing in the interface has a method for that.
  the pattern made the tree uniform and left invalidation as the
  thing the uniform interface cannot express.
```

Twelve nodes, two node types in the tree, three implementations of the interface. A leaf answers
`size` and a directory answers `size`, and the directory's answer is a fold over its children -- so
asking the root a question is asking the whole tree that question, every time. Every query visited
all twelve nodes.

The caching node is the pattern working exactly as advertised: it implements the same interface,
nothing above it changed, and nothing above it can tell. It is also the node that has to be told when
the answer stops being true, and the interface has no method for that. The pattern made the tree
uniform and left invalidation as the thing the uniform interface cannot express.

## Punctuation that is a pattern

`@` is the decorator pattern, and what it does not do by itself is preserve anything about the
function it wraps.

```python run
"""Chapter 54 -- the decorator pattern, which in Python is punctuation.

`@` is the pattern. What it does not do by itself is preserve anything
about the function it wraps, and the list of what is lost is short
enough to check.
"""

import functools
import inspect


def original(a, b=2, *rest, **named):
    """Add two numbers.

    A docstring, which is one of the things at stake.
    """
    return a + b


def bare(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def keeping(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


def logging_around(fn):
    """A decorator with arguments is a factory: one more layer, and the
    one that is usually written wrong."""
    def decorate(inner):
        @functools.wraps(inner)
        def wrapper(*args, **kwargs):
            return inner(*args, **kwargs)
        return wrapper
    return decorate


CHECKS = [
    ("__name__", lambda f: f.__name__),
    ("__doc__", lambda f: (f.__doc__ or "").strip().split("\n")[0]),
    ("__qualname__", lambda f: f.__qualname__),
    ("__module__", lambda f: f.__module__),
    ("signature", lambda f: str(inspect.signature(f))),
]


def main():
    variants = [
        ("the original", original),
        ("after a bare decorator", bare(original)),
        ("after functools.wraps", keeping(original)),
        ("after a decorator factory", logging_around("why")(original)),
    ]
    print(f"  things a function carries           {len(CHECKS)}")
    print()

    print("    what                    the original          after a bare decorator")
    for label, read in CHECKS:
        print("    {:<24}{:<22}{}".format(
            label, read(original), read(bare(original))))
    print()
    print("    what                    after functools.wraps")
    for label, read in CHECKS:
        print("    {:<24}{}".format(label, read(keeping(original))))
    print()

    lost = [label for label, read in CHECKS
            if read(bare(original)) != read(original)]
    kept = [label for label, read in CHECKS
            if read(keeping(original)) == read(original)]
    print(f"  the bare decorator loses {len(lost)} of the {len(CHECKS)}: "
          f"{', '.join(lost)}.")
    print(f"  `functools.wraps` restores {len(kept)} of the {len(CHECKS)}.")
    print()
    print("  the one that matters most in practice is the signature, and it")
    print("  matters because nothing in the code fails. a wrapped function")
    print("  still runs, and a caller who passes the wrong argument still gets")
    print("  the original's own error. what breaks is every tool that reads")
    print("  the function rather than calls it -- a help page, an editor, a")
    print("  schema generator -- and those all report the wrapper.")
    print()
    print("  the fourth variant is there because the factory is the shape")
    print("  that gets it wrong: `@logging_around(\"why\")` is three nested")
    print("  functions, and putting `functools.wraps` on the outer one instead")
    print("  of the inner one is the mistake that looks like a fix. the")
    print("  measurement above is the inner one, which is the right one.")


main()
```

```text
  things a function carries           5

    what                    the original          after a bare decorator
    __name__                original              wrapper
    __doc__                 Add two numbers.      
    __qualname__            original              bare.<locals>.wrapper
    __module__              __main__              __main__
    signature               (a, b=2, *rest, **named)(*args, **kwargs)

    what                    after functools.wraps
    __name__                original
    __doc__                 Add two numbers.
    __qualname__            original
    __module__              __main__
    signature               (a, b=2, *rest, **named)

  the bare decorator loses 4 of the 5: __name__, __doc__, __qualname__, signature.
  `functools.wraps` restores 5 of the 5.

  the one that matters most in practice is the signature, and it
  matters because nothing in the code fails. a wrapped function
  still runs, and a caller who passes the wrong argument still gets
  the original's own error. what breaks is every tool that reads
  the function rather than calls it -- a help page, an editor, a
  schema generator -- and those all report the wrapper.

  the fourth variant is there because the factory is the shape
  that gets it wrong: `@logging_around("why")` is three nested
  functions, and putting `functools.wraps` on the outer one instead
  of the inner one is the mistake that looks like a fix. the
  measurement above is the inner one, which is the right one.
```

Five things a function carries, and a bare decorator loses four of them: the name, the docstring, the
qualified name and the signature. The module is the one that survives, and it survives by accident
rather than by design -- the decorator was defined in the same module as the function it wraps, so the
wrapper's `__module__` happens to be the right answer. It is the one entry in that column that the
decorator is not responsible for. `functools.wraps` restores all five.

The one that matters most in practice is the signature, and it matters because nothing in the code
fails. A wrapped function still runs and a caller who passes the wrong argument still gets the
original's own error. What breaks is every tool that reads the function rather than calls it -- a
help page, an editor, a schema generator -- and all of them report the wrapper.

The fourth variant in the table is there because the factory is the shape that gets it wrong. A
decorator that takes arguments is three nested functions, and putting `functools.wraps` on the outer
one instead of the inner one is the mistake that looks like a fix.

## What a check on an interface is worth

An interface is a name for a set of methods. What `isinstance` does with that name depends on which
kind of interface it is, and the difference is what the word "structural" costs.

```python run
"""Chapter 54 -- interfaces, and what a check on one is worth.

A `Protocol` and an `ABC` both name an interface. What they do with
`isinstance` is different, and the difference is what the word
"structural" costs.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Store(Protocol):
    def get(self, key):
        ...


@runtime_checkable
class Checkable(Protocol):
    def get(self, key):
        ...


class BaseStore(ABC):
    @abstractmethod
    def get(self, key):
        ...


class Real:
    def get(self, key):
        return "the value for " + key


class WrongArity:
    """The right name and the wrong signature."""

    def get(self):
        return "no key taken"


class NotCallable:
    """The right name bound to something that is not a method."""

    get = 5


class Subclass(BaseStore):
    def get(self, key):
        return "subclassed"


OBJECTS = [
    ("a class with the method", Real()),
    ("the right name, wrong signature", WrongArity()),
    ("the right name, not callable", NotCallable()),
    ("a subclass of the ABC", Subclass()),
]


def check(obj, cls):
    try:
        return "True" if isinstance(obj, cls) else "False"
    except TypeError as exc:
        return type(exc).__name__


def main():
    print(f"  objects                             {len(OBJECTS)}")
    print(f"  interfaces named                    {3}")
    print()

    print("    object                           Store      Checkable  BaseStore")
    for label, obj in OBJECTS:
        print("    {:<33}{:<11}{:<11}{}".format(
            label, check(obj, Store), check(obj, Checkable),
            check(obj, BaseStore)))
    print()

    plain = set(check(obj, Store) for _, obj in OBJECTS)
    structural = [label for label, obj in OBJECTS if check(obj, Checkable) == "True"]
    nominal = [label for label, obj in OBJECTS if check(obj, BaseStore) == "True"]
    print(f"  the plain Protocol raises {', '.join(sorted(plain))} for all "
          f"{len(OBJECTS)} objects,")
    print("  which is a decision rather than an oversight: a structural check")
    print("  costs a walk over the attributes on every call, and the default")
    print("  is to not pay it.")
    print()
    print(f"  `runtime_checkable` accepts {len(structural)} of the {len(OBJECTS)}:")
    for label in structural:
        print("    " + label)
    print()
    print(f"  the ABC accepts {len(nominal)}: {', '.join(nominal)}. it is the strictest")
    print("  of the three, and it is strict in the way that costs the most --")
    print("  a class that already does the right thing has to be edited to say")
    print("  so, which is a change to code that was not wrong.")
    print()
    print("  the row to read twice is the second one. an object whose method")
    print("  takes no arguments passed a check for an interface whose method")
    print("  takes a key, because the runtime check looks at whether the")
    print("  attribute exists and not at what it accepts. so the one check")
    print("  that is available at runtime is a check on names.")
    print()
    print("  that is the trade the whole idea rests on. the interface is for")
    print("  the reader and the type checker, both of which can see the")
    print("  signature. the runtime check is for the code path you cannot")
    print("  prove, and it is weaker than it looks -- which is fine, as long")
    print("  as it is not the only thing standing between a request and a")
    print("  call.")


main()
```

```text
  objects                             4
  interfaces named                    3

    object                           Store      Checkable  BaseStore
    a class with the method          TypeError  True       False
    the right name, wrong signature  TypeError  True       False
    the right name, not callable     TypeError  True       False
    a subclass of the ABC            TypeError  True       True

  the plain Protocol raises TypeError for all 4 objects,
  which is a decision rather than an oversight: a structural check
  costs a walk over the attributes on every call, and the default
  is to not pay it.

  `runtime_checkable` accepts 4 of the 4:
    a class with the method
    the right name, wrong signature
    the right name, not callable
    a subclass of the ABC

  the ABC accepts 1: a subclass of the ABC. it is the strictest
  of the three, and it is strict in the way that costs the most --
  a class that already does the right thing has to be edited to say
  so, which is a change to code that was not wrong.

  the row to read twice is the second one. an object whose method
  takes no arguments passed a check for an interface whose method
  takes a key, because the runtime check looks at whether the
  attribute exists and not at what it accepts. so the one check
  that is available at runtime is a check on names.

  that is the trade the whole idea rests on. the interface is for
  the reader and the type checker, both of which can see the
  signature. the runtime check is for the code path you cannot
  prove, and it is weaker than it looks -- which is fine, as long
  as it is not the only thing standing between a request and a
  call.
```

Four objects and three ways of naming the interface. A plain `Protocol` raises `TypeError` for all
four, which is a decision rather than an oversight: a structural check walks the attributes on every
call and the default is not to pay for it.

`runtime_checkable` accepted all four, including the object whose method takes no arguments and the
object whose `get` is the number five. The ABC accepted one -- the subclass written to satisfy it
-- and it is the strictest of the three in the way that costs the most, because a class that already
does the right thing has to be edited to say so.

So the one check available at runtime is a check on names. The interface is for the reader and the
type checker, both of which can see the signature. The runtime check catches the collaborator that
is missing the attribute entirely, which is the mistake that actually happens when a dependency is
swapped -- and it is not strong enough to be the only thing standing between a request and a call.

## What a layer costs

The last teaching block is the one that turns the chapter's method on the chapter's subject. A layer
is a claim about a change that might happen, and the claim can be checked.

```python run
"""Chapter 54 -- the cost of a layer, measured in frames.

One rule, wrapped in four layers that each do nothing but forward. The
count is of frames, and of the implementations each layer actually has.
"""

TRACE = []


def core(order):
    TRACE.append("core")
    return order * 1.2


def repository(order):
    TRACE.append("repository")
    return core(order)


def service(order):
    TRACE.append("service")
    return repository(order)


def controller(order):
    TRACE.append("controller")
    return service(order)


def handler(order):
    TRACE.append("handler")
    return controller(order)


def frames_between(outer, inner, argument):
    """How many of our own frames sit between the call and the rule."""
    global TRACE
    TRACE = []
    outer(argument)
    return list(TRACE)


def main():
    direct = frames_between(core, core, 10.0)
    layered = frames_between(handler, core, 10.0)
    print(f"  frames for the rule called directly  {len(direct)}")
    print(f"  frames for the rule behind a handler {len(layered)}")
    print("    " + " -> ".join(layered))
    print()

    print(f"  the rule is one expression, and a call from the outside reaches")
    print(f"  it through {len(layered)} frames, {len(layered) - len(direct)} of which only")
    print("  forward their argument to the next one.")
    print()
    print("  that is not an argument against layers. it is the number to put")
    print("  next to them, because a layer is a claim about a change that")
    print("  might happen, and the claim can be checked.")
    print()

    layers = ["handler", "controller", "service", "repository", "core"]
    print("    layer            implementations")
    for name in layers:
        print("    {:<17}{}".format(name, 1))
    print()
    print(f"  {len(layers)} layers and {len(layers)} implementations, so the seam each")
    print("  one creates is a seam with one thing on each side. swapping the")
    print("  rule changes one line with the layers and one line without them,")
    print("  and adding a second implementation to any layer is what would")
    print("  make the count go up.")
    print()
    print("  the honest way to read the frame count is as a question rather")
    print("  than a verdict: how many implementations does each of these")
    print("  layers have, and how many does it have in six months? a layer")
    print("  that keeps one implementation is a layer that has been paying")
    print("  rent without a tenant, and the four frames are what the rent")
    print("  looks like at the call site.")
    print()
    print("  what makes it worth paying is the direction, and the direction is")
    print("  not visible in the frames. if the rule is at the bottom and the")
    print("  layers point down at it, then the thing at the top can be")
    print("  replaced without touching it. if the rule ever imports the")
    print("  handler, the stack has become a cycle and the layers are no")
    print("  longer a boundary -- they are a detour.")


main()
```

```text
  frames for the rule called directly  1
  frames for the rule behind a handler 5
    handler -> controller -> service -> repository -> core

  the rule is one expression, and a call from the outside reaches
  it through 5 frames, 4 of which only
  forward their argument to the next one.

  that is not an argument against layers. it is the number to put
  next to them, because a layer is a claim about a change that
  might happen, and the claim can be checked.

    layer            implementations
    handler          1
    controller       1
    service          1
    repository       1
    core             1

  5 layers and 5 implementations, so the seam each
  one creates is a seam with one thing on each side. swapping the
  rule changes one line with the layers and one line without them,
  and adding a second implementation to any layer is what would
  make the count go up.

  the honest way to read the frame count is as a question rather
  than a verdict: how many implementations does each of these
  layers have, and how many does it have in six months? a layer
  that keeps one implementation is a layer that has been paying
  rent without a tenant, and the four frames are what the rent
  looks like at the call site.

  what makes it worth paying is the direction, and the direction is
  not visible in the frames. if the rule is at the bottom and the
  layers point down at it, then the thing at the top can be
  replaced without touching it. if the rule ever imports the
  handler, the stack has become a cycle and the layers are no
  longer a boundary -- they are a detour.
```

One expression, reached through five frames from the outside. Four of those frames only forward
their argument to the next one, and each layer has exactly one implementation, so every seam has one
thing on each side.

That is not an argument against layers. It is the number to put next to them, because the number is
the rent and the implementations are the tenant. Swapping the rule changes one line with the layers
and one line without them; what would make the count go up is a second implementation at some layer,
and not one of the five here has one. The seam each layer creates is a seam with one thing on each
side of it, which is the definition of a seam that is not being used.

The direction is the part the frames cannot show. If the rule is at the bottom and the layers point
down at it, the thing at the top can be replaced without touching it. If the rule ever imports the
handler, the stack has become a cycle and the layers are no longer a boundary -- they are a detour.

:::pitfall The pattern where a function would do

Every block so far has compared a pattern against something simpler and found the pattern paying for
itself somewhere. This one is the case where it does not.

Three notification channels, built twice: once as a hierarchy with a factory, once as a dictionary of
functions.

```python run
"""Chapter 54 -- the pattern where a function would do.

The same three notification channels, built twice: once as a hierarchy
with a factory, and once as a dictionary of functions. The two are
compared on what they cost and on what each one changes when a fourth
channel arrives.
"""

import pathlib

# --- pattern
class Notifier:
    def send(self, message):
        raise NotImplementedError


class EmailNotifier(Notifier):
    def send(self, message):
        return "email: " + message


class SmsNotifier(Notifier):
    def send(self, message):
        return "sms: " + message


class WebhookNotifier(Notifier):
    def send(self, message):
        return "webhook: " + message


NOTIFIER_TYPES = {
    "email": EmailNotifier,
    "sms": SmsNotifier,
    "webhook": WebhookNotifier,
}


def make_notifier(channel):
    return NOTIFIER_TYPES[channel]()


def notify_pattern(channel, message):
    return make_notifier(channel).send(message)


# --- function
def notify_function(channel, message):
    return CHANNELS[channel](message)


CHANNELS = {
    "email": lambda m: "email: " + m,
    "sms": lambda m: "sms: " + m,
    "webhook": lambda m: "webhook: " + m,
}
# --- end


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
PATTERN_SRC = SOURCE.split("# --- pattern")[1].split("# --- function")[0]
FUNC_SRC = SOURCE.split("# --- function")[1].split("# --- end")[0]

CHANNELS_TESTED = ["email", "sms", "webhook"]
UNKNOWN = ["slack", "pagerduty"]


def count(source, word):
    return sum(1 for line in source.splitlines() if word in line)


def main():
    print(f"  channels                            {len(CHANNELS_TESTED)}")
    print()
    print("    what                          the hierarchy   the dictionary")
    print("    {:<30}{:>13}{:>16}".format(
        "classes", count(PATTERN_SRC, "class "), count(FUNC_SRC, "class ")))
    print("    {:<30}{:>13}{:>16}".format(
        "functions and methods", count(PATTERN_SRC, "def "),
        count(FUNC_SRC, "def ")))
    print("    {:<30}{:>13}{:>16}".format(
        "lines", len(PATTERN_SRC.strip().splitlines()),
        len(FUNC_SRC.strip().splitlines())))
    print()

    for channel in CHANNELS_TESTED:
        same = (notify_pattern(channel, "hi") == notify_function(channel, "hi"))
        if not same:
            print("    the two disagree on " + channel)
    print("  all three channels produce the same string through both, so the")
    print("  two are interchangeable for the behaviour they exist to produce.")
    print()

    print("    an unknown channel                the hierarchy   the dictionary")
    for channel in UNKNOWN:
        outcomes = []
        for fn in (notify_pattern, notify_function):
            try:
                fn(channel, "hi")
                outcomes.append("raised nothing")
            except KeyError:
                outcomes.append("KeyError")
        print("    {:<34}{:<16}{}".format(channel, outcomes[0], outcomes[1]))
    print()
    print("  both refuse an unknown channel, and both refuse it the same way,")
    print("  because both of them end in a dictionary lookup. the hierarchy is")
    print("  a dictionary with four extra names in front of it.")
    print()

    print("    what a fourth channel changes")
    print("    {:<34}{:>10}   {}".format("the hierarchy", "2", "a class and a key"))
    print("    {:<34}{:>10}   {}".format("the dictionary", "1", "a key"))
    print()
    print("  the hierarchy needs a class and a registry entry; the dictionary")
    print("  needs a key. the class is not doing anything the function does not")
    print("  do -- it holds no state, it has one method, and it is constructed")
    print("  and thrown away on every call.")
    print()
    print("  the hierarchy starts paying on the day a notifier needs to")
    print("  remember something: a retry count, a client handle, a rate limit.")
    print("  a function can hold that too, in a closure or in a default")
    print("  argument, and the moment it does, the difference between the two")
    print("  is that one of them is a class and the other is not. that is the")
    print("  whole of what was bought, and it is worth naming before paying")
    print("  for it.")


main()
```

```text
  channels                            3

    what                          the hierarchy   the dictionary
    classes                                   4               0
    functions and methods                     6               1
    lines                                    33               9

  all three channels produce the same string through both, so the
  two are interchangeable for the behaviour they exist to produce.

    an unknown channel                the hierarchy   the dictionary
    slack                             KeyError        KeyError
    pagerduty                         KeyError        KeyError

  both refuse an unknown channel, and both refuse it the same way,
  because both of them end in a dictionary lookup. the hierarchy is
  a dictionary with four extra names in front of it.

    what a fourth channel changes
    the hierarchy                              2   a class and a key
    the dictionary                             1   a key

  the hierarchy needs a class and a registry entry; the dictionary
  needs a key. the class is not doing anything the function does not
  do -- it holds no state, it has one method, and it is constructed
  and thrown away on every call.

  the hierarchy starts paying on the day a notifier needs to
  remember something: a retry count, a client handle, a rate limit.
  a function can hold that too, in a closure or in a default
  argument, and the moment it does, the difference between the two
  is that one of them is a class and the other is not. that is the
  whole of what was bought, and it is worth naming before paying
  for it.
```

Four classes, six functions and 33 lines against no classes, one function and 9 lines. Both produce
the same string for all three channels, and both refuse an unknown channel the same way -- because
both of them end in a dictionary lookup. The hierarchy is a dictionary with four extra names in front
of it.

A fourth channel costs a class and a registry entry against a key. And the class is not doing
anything the function does not do: it holds no state, it has one method, and it is constructed and
thrown away on every call.

The hierarchy starts paying on the day a notifier needs to remember something -- a retry count, a
client handle, a rate limit. A function can hold that too, in a closure or a default argument, and
the moment it does, the difference between the two is that one of them is a class and the other is
not. That is the whole of what was bought, and it is worth naming before paying for it.

The rule to carry away is not "do not use patterns". It is that the class was introduced to hold
behaviour, and behaviour in this language is a value. Introduce the class when it holds something
else -- state, a configuration, an identity that matters -- and not before.

:::

:::scenario The plugin host

A plugin host is where this chapter's patterns all turn up at once, because it is the feature whose
entire job is to let code you did not write run inside your process. Eight plugins, four of which are
broken in four different ways.

```python run
"""Chapter 54 -- the scenario. A plugin host.

Eight plugins, four of which are broken in four different ways, and five
hosts that differ in what they do about it. The count is of requests
answered, and the column that matters is when the broken ones are found.
"""


class Plugin:
    name = "plugin"

    def handle(self, request):
        raise NotImplementedError


class Good(Plugin):
    def __init__(self, name, answer):
        self.name = name
        self._answer = answer

    def handle(self, request):
        return self._answer


class Raiser(Plugin):
    def __init__(self, name, error):
        self.name = name
        self._error = error

    def handle(self, request):
        raise self._error


class OldSignature(Plugin):
    """Written against the first version of the interface, which took no
    request."""

    name = "old"

    def handle(self):
        return "old answer"


class NotCallable(Plugin):
    name = "not-callable"
    handle = 5


def build():
    return [
        Good("alpha", "alpha ok"),
        Good("beta", "beta ok"),
        Good("gamma", "gamma ok"),
        Good("delta", "delta ok"),
        Raiser("epsilon", RuntimeError("epsilon failed")),
        Raiser("zeta", KeyError("zeta failed")),
        OldSignature(),
        NotCallable(),
    ]


def try_call(plugin, request):
    """Returns (answered, the answer or the error name)."""
    try:
        return True, plugin.handle(request)
    except Exception as exc:
        return False, type(exc).__name__


def adapt(plugin):
    """The adapter for the old signature, which is one place that knows
    the old shape."""
    if isinstance(plugin, OldSignature):
        return _Adapted(plugin)
    return plugin


class _Adapted(Plugin):
    def __init__(self, inner):
        self.inner = inner
        self.name = inner.name

    def handle(self, request):
        return self.inner.handle()


def probe(plugins):
    """What a startup check would find, and it is the same call the
    request path makes."""
    ok, broken = [], []
    for plugin in plugins:
        answered, _ = try_call(plugin, "probe")
        (ok if answered else broken).append(plugin.name)
    return ok, broken


def main():
    plugins = build()
    print(f"  plugins                             {len(plugins)}")
    print(f"  good                                "
          f"{sum(1 for p in plugins if type(p) is Good)}")
    print(f"  broken                              "
          f"{sum(1 for p in plugins if type(p) is not Good)}")
    print()

    rows = []

    # A: call each plugin directly and let it fail
    answered, crashed = 0, False
    for plugin in plugins:
        ok, _ = try_call(plugin, "request")
        if ok:
            answered += 1
        else:
            crashed = True
            break
    rows.append(("call it and let it fail", answered, crashed, "at the first request"))

    # B: isolate each call
    answered = 0
    for plugin in plugins:
        ok, _ = try_call(plugin, "request")
        answered += 1 if ok else 0
    rows.append(("isolate each call", answered, False, "at the first request"))

    # C: isolate, and check the interface first
    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class Handles(Protocol):
        def handle(self, request):
            ...

    answered, accepted = 0, 0
    for plugin in plugins:
        if isinstance(plugin, Handles):
            accepted += 1
        ok, _ = try_call(plugin, "request")
        answered += 1 if ok else 0
    rows.append(("isolate, and check the interface", answered, False,
                 "at the first request"))

    # D: plus the adapter
    adapted = [adapt(p) for p in plugins]
    answered = 0
    for plugin in adapted:
        ok, _ = try_call(plugin, "request")
        answered += 1 if ok else 0
    rows.append(("and adapt the old signature", answered, False,
                 "at the first request"))

    # E: plus a startup probe
    ok, broken = probe(adapted)
    answered = 0
    for plugin in adapted:
        if plugin.name in ok:
            good, _ = try_call(plugin, "request")
            answered += 1 if good else 0
    rows.append(("and probe every plugin at startup", answered, False,
                 "before the first request"))

    print("    host                              answered  survived   found")
    for label, answered, crashed, when in rows:
        print("    {:<34}{:>8}  {:<9}{}".format(
            label, "%d of %d" % (answered, len(plugins)),
            "no" if crashed else "yes", when))
    print()

    print(f"  the interface check accepted {accepted} of the {len(plugins)} plugins and")
    print("  changed nothing, because a runtime protocol check asks whether")
    print("  the name is there -- and for the plugin whose `handle` is the")
    print("  number five, it is.")
    print()
    print("  isolation is what keeps the host up, and the adapter is what")
    print("  gets one more plugin answering. neither of them tells you which")
    print("  plugin is broken.")
    print()
    print("  the last row does not answer more requests than the one above it.")
    print("  it answers the same number and it finds the broken ones *before*")
    print("  the first request, which is the only difference and the whole of")
    print("  it. a plugin host is a place where the patterns give you the")
    print("  shape -- a registry, an interface, a dispatch, an adapter -- and")
    print("  the shape is not the part that decides whether the system works.")
    print("  the part that decides is the one line nobody writes: the probe")
    print("  that calls every plugin once, at startup, and names the ones that")
    print("  did not answer.")


main()
```

```text
  plugins                             8
  good                                4
  broken                              4

    host                              answered  survived   found
    call it and let it fail             4 of 8  no       at the first request
    isolate each call                   4 of 8  yes      at the first request
    isolate, and check the interface    4 of 8  yes      at the first request
    and adapt the old signature         5 of 8  yes      at the first request
    and probe every plugin at startup   5 of 8  yes      before the first request

  the interface check accepted 8 of the 8 plugins and
  changed nothing, because a runtime protocol check asks whether
  the name is there -- and for the plugin whose `handle` is the
  number five, it is.

  isolation is what keeps the host up, and the adapter is what
  gets one more plugin answering. neither of them tells you which
  plugin is broken.

  the last row does not answer more requests than the one above it.
  it answers the same number and it finds the broken ones *before*
  the first request, which is the only difference and the whole of
  it. a plugin host is a place where the patterns give you the
  shape -- a registry, an interface, a dispatch, an adapter -- and
  the shape is not the part that decides whether the system works.
  the part that decides is the one line nobody writes: the probe
  that calls every plugin once, at startup, and names the ones that
  did not answer.
```

Five hosts. The first calls each plugin and lets it fail, and it answered four of the eight requests
before the host came down. Isolation keeps the host up and still answers four. Adding the interface
check changes nothing at all -- it accepted all eight, including the plugin whose `handle` is the
number five, because a runtime protocol check asks whether the name is there and it is. The adapter
gets one more plugin answering, which is what an adapter is for.

The last row answers the same number as the one above it, and the difference is *when* the broken
plugins are found: before the first request rather than during it. That is the whole gain and it is
the largest single gain in the table.

So a plugin host is a place where the patterns give you the shape -- a registry, an interface, a
dispatch, an adapter -- and the shape is not the part that decides whether the system works. The
part that decides is the one line nobody writes: the probe that calls every plugin once, at startup,
and names the ones that did not answer.

:::

## Key takeaways

- **A pattern is a name for a shape, not a target to aim at.** The question is what the shape costs,
  what it buys, and whether this program needs the thing it buys.
- **The table is the longer of the two.** 24 lines of chain against 35 lines of table, and every
  method name appears twice in the table -- once as a function and once as a key.
- **What a table buys is not brevity, it is that a missing case cannot be forgotten.** A chain whose
  last branch is a default charged an unknown method the standard rate, silently and plausibly.
- **A chain compares 15 times over 5 calls; a table compares once per call.** That is the argument
  everybody makes and it is true, and it is not the one that matters.
- **`functools.singledispatch` dispatches on one argument and walks the mro.** `True` reached the int
  handler, and so did a subclass of `int` written in the same file.
- **The second argument of a singledispatch function decides nothing.** The type of every argument
  after the first is never consulted, which is the mechanism's limit and its documentation.
- **A default that returns a plausible value is worse than one that raises.** The default here
  returns a string, which is the wrong answer that looks like the right one.
- **A subscriber list is three lines, and the second version of it treats a subscriber as something
  that can be wrong.** The first raised after 2 of 6 had run, and the three after the failing one
  never heard about the event at all.
- **Order is part of the result when subscribers share state.** All 6 orderings of three folding
  subscribers left a different value, and nothing in the pattern says what the order is.
- **An adapter divides a number, so it does nothing when the number is one.** Four reads in four
  places against four reads in one, and with a single call site there is no difference at all.
- **A registry is built by import side effects.** Five handlers defined, three registered, and the
  missing two are missing because a module was not imported -- reported as a missing key at request
  time, in a different file.
- **A lookup through `globals()` cannot tell a handler from anything else.** It resolved 6 of 8
  requests where the registry resolved 5, and they were not the same five: three of the names it
  answered for were not handlers, and two of the registry's handlers were not module-level names.
- **A composite gives a leaf and a branch the same interface and not the same cost.** Every query on
  the root visited all twelve nodes.
- **A caching node implements the same interface, so nothing above it can tell.** It is also the node
  that has to be invalidated, and the interface has no method for that.
- **A bare decorator loses four of the five things a function carries.** The module survives, by
  accident rather than by design, because the decorator was defined in the same module. `functools.wraps`
  restores all five, and the one that matters is the signature, because nothing in the code fails
  without it.
- **A decorator with arguments is three nested functions.** Putting `functools.wraps` on the outer
  one instead of the inner one is the mistake that looks like a fix.
- **A plain `Protocol` raises on `isinstance` for every object.** That is a decision about cost, not
  an oversight, and `runtime_checkable` is the switch that pays it.
- **The runtime check is a check on names.** It accepted an object whose method takes no arguments
  and an object whose method name is bound to the number five, because it does not call anything.
- **An ABC is the strictest and costs the most.** One of the four objects accepted, and every class
  that already satisfied the interface had to be edited to say so.
- **Five frames for one expression, and four of them only forward.** A layer is rent and the
  implementations are the tenant; a layer whose implementation count stays at one has been paying
  rent without a tenant.

## Practice

- [ ] **Replace one conditional with a table, and check the last branch first.** Find an `if`/`elif`
  chain of four or more branches in a project of yours that selects behaviour. Before rewriting it,
  look at what the final branch does with a value it does not recognise -- if it returns a default
  rather than raising, write down how many inputs would be silently accepted. Then write the table
  version, count the comparisons per call in both, and count the lines in both. Report all three
  numbers.
- [ ] **Count the places a dependency's names appear.** Pick a third-party library or a service
  client. List the field or method names it defines that your code reads. Then count the *functions*
  in your code that mention any of them. If the number is more than one, write the adapter and count
  again. Report the two numbers and say whether the adapter earned its place.
- [ ] **Survey the layers on one call path.** Take a request handler or a command entry point in a
  project of yours. List every function between it and the rule that decides the answer. For each
  one, record how many implementations it has. Report the number of frames in the path and the number
  of functions with exactly one implementation -- and then say which of those you would delete, and
  what you would have to be sure of first.
- [ ] **Audit the interface you rely on.** Take a collaborator your code is duck-typed against. Write
  five stand-ins: one correct, one with the right method name and the wrong signature, one with the
  name bound to something that is not callable, one missing the name entirely, and one that subclasses
  an ABC you write. Run all five through `hasattr`, a plain `Protocol`, a `runtime_checkable`
  `Protocol`, and the ABC. Report how many each check accepts, and name the one check that catches
  the mistake you would actually make.

## Solutions

:::solution Exercise 1

A field-validation chain and the table that replaces it, and the three fields the chain accepts
because it has never heard of them.

```python run
"""Chapter 54 -- practice 1.

A field-validation chain and the table that replaces it. The chain's
last branch is a default, and the default is what an unknown field gets.
"""

import pathlib

KNOWN = ["email", "age", "postcode", "phone", "name"]
UNKNOWN = ["nickname", "tax_id", "referrer"]


# --- chain
def validate_chain(field, value, count):
    count[0] = 0

    count[0] += 1
    if field == "email":
        return "@" in value

    count[0] += 1
    if field == "age":
        return value.isdigit() and 0 <= int(value) < 130

    count[0] += 1
    if field == "postcode":
        return len(value) == 6

    count[0] += 1
    if field == "phone":
        return value.startswith("+")

    count[0] += 1
    if field == "name":
        return len(value) > 0

    return True


# --- table
def check_email(value):
    return "@" in value


def check_age(value):
    return value.isdigit() and 0 <= int(value) < 130


def check_postcode(value):
    return len(value) == 6


def check_phone(value):
    return value.startswith("+")


def check_name(value):
    return len(value) > 0


CHECKS = {
    "email": check_email,
    "age": check_age,
    "postcode": check_postcode,
    "phone": check_phone,
    "name": check_name,
}


def validate_table(field, value, count):
    count[0] = 1
    try:
        return CHECKS[field](value)
    except KeyError:
        raise ValueError("unknown field: " + field) from None
# --- end


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
CHAIN_SRC = SOURCE.split("# --- chain")[1].split("# --- table")[0]
TABLE_SRC = SOURCE.split("# --- table")[1].split("# --- end")[0]

SAMPLES = {
    "email": "ada@example.com",
    "age": "36",
    "postcode": "123456",
    "phone": "+441234",
    "name": "Ada",
    "nickname": "!! not a name",
    "tax_id": "",
    "referrer": "",
}


def main():
    print(f"  fields the chain knows              {len(KNOWN)}")
    print(f"  fields it does not                  {len(UNKNOWN)}")
    print(f"  lines in the chain region           "
          f"{len(CHAIN_SRC.strip().splitlines())}")
    print(f"  lines in the table region           "
          f"{len(TABLE_SRC.strip().splitlines())}")
    print()

    print("    field          value              chain   table")
    chain_total = 0
    for field in KNOWN + UNKNOWN:
        count = [0]
        chain = validate_chain(field, SAMPLES[field], count)
        chain_total += count[0]
        count = [0]
        try:
            table = validate_table(field, SAMPLES[field], count)
        except ValueError:
            table = "refused"
        print("    {:<15}{:<19}{:<8}{}".format(
            field, repr(SAMPLES[field])[:18], str(chain), str(table)))
    print()
    print(f"  the chain compares the field name {chain_total} times over "
          f"{len(KNOWN) + len(UNKNOWN)} calls")
    print(f"  and the table compares it once per call, which is the column")
    print("  everybody looks at.")
    print()
    accepted = [f for f in UNKNOWN if validate_chain(f, SAMPLES[f], [0])]
    print(f"  the column that matters is the three fields the chain does not")
    print(f"  know, and the chain accepted {len(accepted)} of them: "
          f"{', '.join(accepted)}.")
    print("  a validator that returns `True` for a field it has never heard of")
    print("  is a validator that will accept any field a later release adds to")
    print("  the form, and nothing anywhere reports it -- the value is")
    print("  validated, the request succeeds, and the only signal is that no")
    print("  error appeared.")
    print()
    print("  the table refuses all three, because a missing key is a")
    print("  `KeyError` and the code turns it into a `ValueError`. the")
    print("  difference between the two shapes is not the comparison count")
    print("  and it is not the line count -- the table region is the longer of")
    print("  the two. it is that a chain has a last branch and whatever it")
    print("  returns is the answer for everything not listed above it.")


main()
```

```text
  fields the chain knows              5
  fields it does not                  3
  lines in the chain region           24
  lines in the table region           35

    field          value              chain   table
    email          'ada@example.com'  True    True
    age            '36'               True    True
    postcode       '123456'           True    True
    phone          '+441234'          True    True
    name           'Ada'              True    True
    nickname       '!! not a name'    True    refused
    tax_id         ''                 True    refused
    referrer       ''                 True    refused

  the chain compares the field name 30 times over 8 calls
  and the table compares it once per call, which is the column
  everybody looks at.

  the column that matters is the three fields the chain does not
  know, and the chain accepted 3 of them: nickname, tax_id, referrer.
  a validator that returns `True` for a field it has never heard of
  is a validator that will accept any field a later release adds to
  the form, and nothing anywhere reports it -- the value is
  validated, the request succeeds, and the only signal is that no
  error appeared.

  the table refuses all three, because a missing key is a
  `KeyError` and the code turns it into a `ValueError`. the
  difference between the two shapes is not the comparison count
  and it is not the line count -- the table region is the longer of
  the two. it is that a chain has a last branch and whatever it
  returns is the answer for everything not listed above it.
```

:::

:::solution Exercise 2

Three consumers reading a vendor's names, written twice, with the count taken from the source of the
file.

```python run
"""Chapter 54 -- practice 2.

Where a dependency's names appear. Three consumers written twice: once
reading the vendor's field names wherever they are needed, and once
behind a single translation. The count is of functions that mention a
vendor name, taken from the source of the file you are reading.
"""

import pathlib

VENDOR_FIELDS = ["customer_name", "amount_cents", "currency_code",
                 "captured_at", "refundable"]


class Gateway:
    """A stand-in for a payment library. Its records are dictionaries
    with its own names, and it renames them in v2."""

    def __init__(self, version):
        self.version = version

    def charges(self):
        if self.version == 1:
            return [{"customer_name": "Ada", "amount_cents": 1200,
                     "currency_code": "GBP", "captured_at": 1,
                     "refundable": True}]
        return [{"customer": "Ada", "amount_minor": 1200,
                 "currency": "GBP", "captured": 1, "refundable": True}]


# --- direct
def direct_summary(charge):
    return {"who": charge["customer_name"],
            "amount": charge["amount_cents"] / 100}


def direct_receipt(charge):
    return {"total": charge["amount_cents"],
            "in": charge["currency_code"]}


def direct_audit(charge):
    return {"when": charge["captured_at"],
            "refundable": charge["refundable"]}


DIRECT_CONSUMERS = [direct_summary, direct_receipt, direct_audit]
# --- direct


# --- adapted
def translate(charge):
    """The one place the vendor's names appear."""
    return {"who": charge["customer_name"],
            "minor": charge["amount_cents"],
            "currency": charge["currency_code"],
            "when": charge["captured_at"],
            "can_refund": charge["refundable"]}


def summary(charge):
    row = translate(charge)
    return {"who": row["who"], "amount": row["minor"] / 100}


def receipt(charge):
    row = translate(charge)
    return {"total": row["minor"], "in": row["currency"]}


def audit(charge):
    row = translate(charge)
    return {"when": row["when"], "can_refund": row["can_refund"]}


ADAPTED_CONSUMERS = [summary, receipt, audit]
ADAPTED_FUNCTIONS = [translate, summary, receipt, audit]
# --- adapted


SOURCE = pathlib.Path(__file__).read_text(encoding="utf-8")
DIRECT_SRC = SOURCE.split("# --- direct")[1].split("# --- direct")[0]
ADAPTED_SRC = SOURCE.split("# --- adapted")[1].split("# --- adapted")[0]


def body_of(source, name):
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("def " + name):
            out = []
            for line in lines[i + 1:]:
                if line.startswith("def ") or line.startswith("# ---"):
                    break
                out.append(line)
            return out
    return []


def mentions(source, name):
    return sum(1 for line in body_of(source, name)
               for field in VENDOR_FIELDS if field in line)


def main():
    print(f"  vendor fields                       {len(VENDOR_FIELDS)}")
    print(f"  consumers                           {len(DIRECT_CONSUMERS)}")
    print()

    print("    consumer           vendor names read   functions that read one")
    SUMMARY = {}
    for label, names in (("direct", DIRECT_CONSUMERS),
                         ("adapted", ADAPTED_FUNCTIONS)):
        source = DIRECT_SRC if label == "direct" else ADAPTED_SRC
        per = {fn.__name__: mentions(source, fn.__name__) for fn in names}
        total = sum(per.values())
        touched = sum(1 for n in per.values() if n)
        SUMMARY[label] = (total, touched, len(names))
        print("    {:<19}{:>11}   {} of {}".format(
            label, total, touched, len(names)))
    print()

    print("    function                       vendor names in its body")
    for label, source, names in (("direct", DIRECT_SRC, DIRECT_CONSUMERS),
                                 ("adapted", ADAPTED_SRC, ADAPTED_FUNCTIONS)):
        for fn in names:
            print("    {:<31}{}".format(
                fn.__name__, mentions(source, fn.__name__)))
    print()

    for version in (1, 2):
        gateway = Gateway(version)
        print("    gateway v%d" % version)
        for label, consumers in (("direct", DIRECT_CONSUMERS),
                                 ("adapted", ADAPTED_CONSUMERS)):
            outcomes = []
            for fn in consumers:
                for charge in gateway.charges():
                    try:
                        fn(charge)
                        outcomes.append("ok")
                    except KeyError as exc:
                        outcomes.append("KeyError " + str(exc))
            broken = sum(1 for o in outcomes if o != "ok")
            print("      {:<9}{} of {} consumers broken".format(
                label, broken, len(consumers)))
    print()
    d_reads, d_funcs, _ = SUMMARY["direct"]
    a_reads, a_funcs, _ = SUMMARY["adapted"]
    print(f"  the direct version reads {d_reads} vendor fields across "
          f"{d_funcs} functions. the")
    print(f"  adapted one reads {a_reads} in {a_funcs}. the second number is the one to")
    print("  write down, because it is the number of places a rename touches,")
    print("  and it is the number the adapter divides.")
    print()
    print("  so the count to write down is the number of functions that")
    print("  mention a vendor name, because that is the number of places a")
    print("  rename touches. with one consumer the two are equal and the")
    print("  adapter is a layer with nothing to do. with three it is the")
    print("  difference between one edit and three, and the three are in")
    print("  functions whose job is something else.")
    print()
    print("  the question to ask before writing the adapter is therefore not")
    print("  whether the dependency might change. it is how many consumers")
    print("  read it, because that is the number the adapter divides.")


main()
```

```text
  vendor fields                       5
  consumers                           3

    consumer           vendor names read   functions that read one
    direct                       6   3 of 3
    adapted                      5   1 of 4

    function                       vendor names in its body
    direct_summary                 2
    direct_receipt                 2
    direct_audit                   2
    translate                      5
    summary                        0
    receipt                        0
    audit                          0

    gateway v1
      direct   0 of 3 consumers broken
      adapted  0 of 3 consumers broken
    gateway v2
      direct   3 of 3 consumers broken
      adapted  3 of 3 consumers broken

  the direct version reads 6 vendor fields across 3 functions. the
  adapted one reads 5 in 1. the second number is the one to
  write down, because it is the number of places a rename touches,
  and it is the number the adapter divides.

  so the count to write down is the number of functions that
  mention a vendor name, because that is the number of places a
  rename touches. with one consumer the two are equal and the
  adapter is a layer with nothing to do. with three it is the
  difference between one edit and three, and the three are in
  functions whose job is something else.

  the question to ask before writing the adapter is therefore not
  whether the dependency might change. it is how many consumers
  read it, because that is the number the adapter divides.
```

:::

:::solution Exercise 3

A five-frame call path, and the two layers that have more than one implementation behind them.

```python run
"""Chapter 54 -- practice 3.

Implementations per layer. A call path is walked from the entry point to
the rule, and each function on the way is asked how many things
implement it.
"""

import pathlib

CALL_PATH = ["handler", "controller", "service", "repository", "core"]

# what each layer has behind it, counted rather than assumed
IMPLEMENTATIONS = {
    "handler": ["http", "cli"],
    "controller": ["orders"],
    "service": ["orders"],
    "repository": ["sql", "in-memory", "fake"],
    "core": ["standard"],
}

TRACE = []


def core(order):
    TRACE.append("core")
    return order * 1.2


def repository(order):
    TRACE.append("repository")
    return core(order)


def service(order):
    TRACE.append("service")
    return repository(order)


def controller(order):
    TRACE.append("controller")
    return service(order)


def handler(order):
    TRACE.append("handler")
    return controller(order)


def walk(entry, argument):
    global TRACE
    TRACE = []
    entry(argument)
    return list(TRACE)


def main():
    frames = walk(handler, 10.0)
    print(f"  frames from the entry point to the rule  {len(frames)}")
    print("    " + " -> ".join(frames))
    print(f"  frames when the rule is called directly  {len(walk(core, 10.0))}")
    print()

    print("    layer            implementations   what they are")
    for name in CALL_PATH:
        impls = IMPLEMENTATIONS[name]
        print("    {:<17}{:>15}   {}".format(name, len(impls), ", ".join(impls)))
    print()

    forwarding = [n for n in CALL_PATH
                  if len(IMPLEMENTATIONS[n]) == 1 and n != "core"]
    with_choice = [n for n in CALL_PATH if len(IMPLEMENTATIONS[n]) > 1]
    print(f"  {len(with_choice)} of the {len(CALL_PATH)} layers have more than one")
    print("  implementation, and those are the layers that are earning their")
    print("  frames. the other "
          f"{len(forwarding)} have exactly one, so every call through them")
    print("  reaches the same code it would have reached without them.")
    print()
    print("  that is not the same as saying they are wrong. a layer with one")
    print("  implementation is a seam that has been cut and not yet used, and")
    print("  the repository here shows what using it looks like: three")
    print("  implementations, one of which is a fake, and the fake is what")
    print("  makes the service testable without a database.")
    print()
    print("  the count to carry away is the one for the layers with a single")
    print("  implementation. each of them is a place a reader has to open to")
    print("  find the rule, and the rule is at the bottom. if the number of")
    print("  those layers grows while the number of implementations stays at")
    print("  one, the call path is getting longer and nothing is getting")
    print("  easier -- and that is the whole diagnosis, available by counting")
    print("  two columns instead of reading the code.")


main()
```

```text
  frames from the entry point to the rule  5
    handler -> controller -> service -> repository -> core
  frames when the rule is called directly  1

    layer            implementations   what they are
    handler                        2   http, cli
    controller                     1   orders
    service                        1   orders
    repository                     3   sql, in-memory, fake
    core                           1   standard

  2 of the 5 layers have more than one
  implementation, and those are the layers that are earning their
  frames. the other 2 have exactly one, so every call through them
  reaches the same code it would have reached without them.

  that is not the same as saying they are wrong. a layer with one
  implementation is a seam that has been cut and not yet used, and
  the repository here shows what using it looks like: three
  implementations, one of which is a fake, and the fake is what
  makes the service testable without a database.

  the count to carry away is the one for the layers with a single
  implementation. each of them is a place a reader has to open to
  find the rule, and the rule is at the bottom. if the number of
  those layers grows while the number of implementations stays at
  one, the call path is getting longer and nothing is getting
  easier -- and that is the whole diagnosis, available by counting
  two columns instead of reading the code.
```

:::

:::solution Exercise 4

Five collaborators and four ways of asking whether each of them satisfies the interface.

```python run
"""Chapter 54 -- practice 4.

An audit of one interface. Five collaborators and four ways of asking
whether each of them satisfies it, so that the question "which check
should I use" can be answered with a table instead of an opinion.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class Fetches(Protocol):
    """The interface the code relies on. One method, one argument."""

    def fetch(self, key):
        ...


@runtime_checkable
class FetchesChecked(Protocol):
    def fetch(self, key):
        ...


class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, key):
        ...


class Correct:
    def fetch(self, key):
        return "the value for " + key


class WrongArity:
    def fetch(self):
        return "no key"


class NotCallable:
    fetch = "a string"


class Missing:
    def get(self, key):
        return "the wrong name"


class Subclass(BaseFetcher):
    def fetch(self, key):
        return "subclassed"


COLLABORATORS = [
    ("the method, with the right signature", Correct()),
    ("the name, with no argument", WrongArity()),
    ("the name, bound to a string", NotCallable()),
    ("the wrong name entirely", Missing()),
    ("a subclass of the abc", Subclass()),
]

CHECKS = [
    ("hasattr", lambda obj: hasattr(obj, "fetch")),
    ("Protocol", lambda obj: _safe(obj, Fetches)),
    ("runtime", lambda obj: _safe(obj, FetchesChecked)),
    ("ABC", lambda obj: _safe(obj, BaseFetcher)),
]


def _safe(obj, cls):
    try:
        return isinstance(obj, cls)
    except TypeError:
        return "TypeError"


def main():
    print(f"  collaborators                       {len(COLLABORATORS)}")
    print(f"  ways of asking                      {len(CHECKS)}")
    print()

    print("    collaborator                        " +
          "".join("{:>10}".format(name) for name, _ in CHECKS))
    for label, obj in COLLABORATORS:
        row = "    {:<36}".format(label)
        for _, check in CHECKS:
            row += "{:>10}".format(str(check(obj)))
        print(row)
    print()

    for name, check in CHECKS:
        accepted = [label for label, obj in COLLABORATORS if check(obj) is True]
        print("    {:<32}{} of {} accepted".format(
            name, len(accepted), len(COLLABORATORS)))
    print()

    print(f"  the strictest check is the ABC, and it accepts "
          f"{len([1 for _, o in COLLABORATORS if _safe(o, BaseFetcher) is True])} of")
    print("  the five: only the collaborator that was written to satisfy it.")
    print("  it costs the most, because every class that already satisfies the")
    print("  interface has to be edited to say so, and that is a change to")
    print("  code that was not wrong.")
    print()
    print("  `hasattr` and the runtime protocol check accept the same four,")
    print("  and the third of those is the one worth looking at: `fetch` is")
    print("  bound to a string, so the attribute is there and calling it will")
    print("  fail. a runtime check on a name cannot tell that from a method,")
    print("  because it does not call anything.")
    print()
    print("  so the answer to which check to use is not one check. the")
    print("  interface is for the reader and the type checker, both of which")
    print("  can see the signature. the runtime check is a cheap guard that")
    print("  catches the collaborator that is missing the name entirely, which")
    print("  is the mistake that actually happens when a dependency is")
    print("  swapped. and the thing that catches the other two is a test that")
    print("  calls `fetch` and looks at what comes back -- which is the only")
    print("  one of the four that is asking about behaviour rather than about")
    print("  names.")


main()
```

```text
  collaborators                       5
  ways of asking                      4

    collaborator                           hasattr  Protocol   runtime       ABC
    the method, with the right signature      True TypeError      True     False
    the name, with no argument                True TypeError      True     False
    the name, bound to a string               True TypeError      True     False
    the wrong name entirely                  False TypeError     False     False
    a subclass of the abc                     True TypeError      True      True

    hasattr                         4 of 5 accepted
    Protocol                        0 of 5 accepted
    runtime                         4 of 5 accepted
    ABC                             1 of 5 accepted

  the strictest check is the ABC, and it accepts 1 of
  the five: only the collaborator that was written to satisfy it.
  it costs the most, because every class that already satisfies the
  interface has to be edited to say so, and that is a change to
  code that was not wrong.

  `hasattr` and the runtime protocol check accept the same four,
  and the third of those is the one worth looking at: `fetch` is
  bound to a string, so the attribute is there and calling it will
  fail. a runtime check on a name cannot tell that from a method,
  because it does not call anything.

  so the answer to which check to use is not one check. the
  interface is for the reader and the type checker, both of which
  can see the signature. the runtime check is a cheap guard that
  catches the collaborator that is missing the name entirely, which
  is the mistake that actually happens when a dependency is
  swapped. and the thing that catches the other two is a test that
  calls `fetch` and looks at what comes back -- which is the only
  one of the four that is asking about behaviour rather than about
  names.
```

:::
