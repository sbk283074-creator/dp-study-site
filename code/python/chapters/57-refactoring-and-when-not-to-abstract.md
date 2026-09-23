---
chapter: 57
part: 10
title: Refactoring and When Not to Abstract
summary: Change the shape of working code without changing what it does, and know when adding a layer costs more than the duplication it removes. You will be able to run the refactor-verify loop on a function nobody understands, and to argue against an abstraction on evidence rather than taste.
minutes: 90
tags: [refactoring, code smells, characterisation tests, premature abstraction, YAGNI, DRY, strangler fig, technical debt]
---

Chapters 54, 55 and 56 were all about where to put a boundary. This chapter is about the other half of
the same skill: changing code that already works, and deciding *not* to change it. They belong together
because both answers come from the same question — what will somebody need to edit next year? — and
because the most expensive mistakes in this book are not bugs. They are layers somebody added because
the layer was a good idea, and duplications somebody removed because duplication was a bad idea.

Here is the distinction that makes refactoring different from every other kind of editing: **the code
must do exactly what it did before**. Not approximately, not "I read it and it looks equivalent". If you
cannot demonstrate that, you did not refactor; you rewrote, and you are about to find out which
behaviour you changed from a customer. So the loop has two steps that must stay separate — improve the
shape, then prove the behaviour survived — and everything in this chapter is either one step or a
warning about merging them.

The second half is harder and more valuable, because it is where taste is usually asserted instead of
argued. "This needs to be DRY" is a claim about the future, and like the ports in Chapter 56, it is testable:
count what the abstraction saves, count what it costs the day two callers want different things. Sometimes
the abstract answer wins. In this chapter it mostly does not, and the counts say so out loud.

## The loop: improve the shape, then prove nothing moved

Start with a function nobody wants to touch, because it is the kind everybody has met. It prices an
order, and it has three ideas tangled together: a volume tier, a member bonus, and a shipping rule. No
single line is wrong. The problem is that adding anything requires understanding all three at once.

Below, the same logic exists in four shapes. The measurement is made against every input shape the
current callers can produce — seventy of them — comparing what each version returns against what the
original returns. That comparison is not a formality; it is the definition of the word refactor.

```python run
"""Chapter 57 -- refactoring, verified by behaviour instead of by reading.

One messy function, refactored in five steps. Each step is checked against
the previous one by comparing what both versions return for every input we
can think of -- which is what makes the step a refactor rather than a
rewrite. The measurement is how many behaviours survived each step.
"""

from __future__ import annotations

from dataclasses import dataclass


# ------------------------------------------------- version 1: as found


def price_order_v1(raw: dict) -> dict:
    # do not judge too hard; this is a real function i have met
    out = {}
    out["total"] = 0
    out["items"] = 0
    for line in raw["lines"]:
        qty = line[2]
        cents = line[1]
        disc = 0
        if qty >= 10:
            disc = 10
        elif qty >= 5:
            disc = 5
        if raw["member"]:
            disc = disc + 5
        if disc > 20:
            disc = 20
        line_total = cents * qty
        line_total = line_total - (line_total * disc // 100)
        out["total"] = out["total"] + line_total
        out["items"] = out["items"] + qty
    if out["total"] > 50000:
        ship = 0
    elif out["total"] > 20000:
        ship = 500
    else:
        ship = 995
    out["shipping"] = ship
    out["total"] = out["total"] + ship
    out["currency"] = raw.get("currency", "USD")
    return out


# ------------------------------------------- version 2: name the concepts


@dataclass(frozen=True)
class Line:
    sku: str
    cents: int
    qty: int


def _tier_discount(qty: int) -> int:
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


def _member_bonus(is_member: bool) -> int:
    return 5 if is_member else 0


def discount_pct(line: Line, is_member: bool) -> int:
    return min(20, _tier_discount(line.qty) + _member_bonus(is_member))


def _shipping(subtotal_cents: int) -> int:
    if subtotal_cents > 50000:
        return 0
    if subtotal_cents > 20000:
        return 500
    return 995


def price_order_v2(raw: dict) -> dict:
    lines = [Line(sku, cents, qty) for sku, cents, qty in raw["lines"]]
    member = raw["member"]
    subtotal = 0
    items = 0
    for line in lines:
        pct = discount_pct(line, member)
        gross = line.cents * line.qty
        subtotal += gross - (gross * pct // 100)
        items += line.qty
    ship = _shipping(subtotal)
    return {
        "total": subtotal + ship,
        "items": items,
        "shipping": ship,
        "currency": raw.get("currency", "USD"),
    }


# ------------------------------------ version 3: a table instead of branch


TIERS = ((10, 10), (5, 5))  # (minimum qty, discount %)


def tier_discount_table(qty: int) -> int:
    for minimum, pct in TIERS:
        if qty >= minimum:
            return pct
    return 0


def discount_pct_table(line: Line, is_member: bool) -> int:
    return min(20, tier_discount_table(line.qty) + _member_bonus(is_member))


def price_order_v3(raw: dict) -> dict:
    lines = [Line(sku, cents, qty) for sku, cents, qty in raw["lines"]]
    member = raw["member"]
    subtotal = 0
    items = 0
    for line in lines:
        pct = discount_pct_table(line, member)
        gross = line.cents * line.qty
        subtotal += gross - (gross * pct // 100)
        items += line.qty
    ship = _shipping(subtotal)
    return {
        "total": subtotal + ship,
        "items": items,
        "shipping": ship,
        "currency": raw.get("currency", "USD"),
    }


# ------------------------------- version 4: composition instead of fields


def line_total_cents(line: Line, member: bool) -> int:
    gross = line.cents * line.qty
    pct = discount_pct_table(line, member)
    return gross - (gross * pct // 100)


def price_order_v4(raw: dict) -> dict:
    lines = [Line(*triple) for triple in raw["lines"]]
    member = raw["member"]
    subtotal = sum(line_total_cents(line, member) for line in lines)
    items = sum(line.qty for line in lines)
    ship = _shipping(subtotal)
    return {
        "total": subtotal + ship,
        "items": items,
        "shipping": ship,
        "currency": raw.get("currency", "USD"),
    }


# ------------------------------------------------- behaviour comparison


def make_cases() -> list[dict]:
    """Every shape of input the current callers can produce."""
    cases = []
    for member in (True, False):
        for qty in (0, 1, 4, 5, 9, 10, 25):
            for cents in (0, 99, 12_000, 40_000, 250_000):
                cases.append(
                    {
                        "lines": [("A", cents, qty), ("B", 500, 3)],
                        "member": member,
                    }
                )
    return cases


VERSIONS = [
    ("v1 as found", price_order_v1),
    ("v2 named", price_order_v2),
    ("v3 table", price_order_v3),
    ("v4 composed", price_order_v4),
]


def main() -> None:
    cases = make_cases()
    baseline = [price_order_v1(c) for c in cases]

    print("every version against every input v1 sees")
    print()
    print(f"  input shapes compared            {len(cases)}")
    print()
    print("  version          behaviours preserved   behaviours changed")
    for name, fn in VERSIONS:
        got = [fn(c) for c in cases]
        same = sum(1 for a, b in zip(got, baseline) if a == b)
        print(f"  {name:16} {same:>21} {len(cases) - same:>19}")
    print()

    print("what each step bought")
    print()
    steps = [
        ("v1 -> v2", "the three ideas inside the loop have names now"),
        ("v2 -> v3", "a tier is data, so adding one is one row and not a branch"),
        ("v3 -> v4", "the total is a sum of a named thing, not an accumulator"),
    ]
    for pair, gain in steps:
        print(f"  {pair:10} {gain}")
    print()
    print("  and what none of them changed: the answer. every row in the first")
    print("  table reads the same number, which is the only evidence that matters.")
    print("  a refactor is not a rewrite you feel good about -- it is one whose")
    print("  outputs you compared. if you did not compare them, you rewrote it.")
    print()

    print("adding a tier now costs")
    print()
    print("  before the step                 a new elif inside the hot loop")
    print("  after it                        (4, 2) appended to TIERS")
    print()
    print("  and this is the part to be honest about: v3 is not shorter than v2 and")
    print("  not simpler to read on its own. it is better only because the change")
    print("  somebody actually asked for became a data edit instead of a branch.")


if __name__ == "__main__":
    main()
```

```text
every version against every input v1 sees

  input shapes compared            70

  version          behaviours preserved   behaviours changed
  v1 as found                         70                   0
  v2 named                            70                   0
  v3 table                            70                   0
  v4 composed                         70                   0

what each step bought

  v1 -> v2   the three ideas inside the loop have names now
  v2 -> v3   a tier is data, so adding one is one row and not a branch
  v3 -> v4   the total is a sum of a named thing, not an accumulator

  and what none of them changed: the answer. every row in the first
  table reads the same number, which is the only evidence that matters.
  a refactor is not a rewrite you feel good about -- it is one whose
  outputs you compared. if you did not compare them, you rewrote it.

adding a tier now costs

  before the step                 a new elif inside the hot loop
  after it                        (4, 2) appended to TIERS

  and this is the part to be honest about: v3 is not shorter than v2 and
  not simpler to read on its own. it is better only because the change
  somebody actually asked for became a data edit instead of a branch.
```

Read the first table carefully, because it is the only evidence a refactor has. Every version preserves
all seventy behaviours. That number is what lets you stop worrying about whether you understood the
code — you did not need to understand it, you needed to enumerate what it does and then compare.

Notice also what step three bought, and admit how small it is. Moving the tiers into a table did not make
the function shorter or cleverer; it made the *specific change somebody was going to ask for* into a data
edit. That is the honest standard for judging a refactor: not elegance, but whether the next request gets
cheaper. A refactor that improves how the code reads but leaves the next edit exactly as expensive is
a hobby, and a hobby is fine as long as you are not presenting it as work.

Two mechanical notes from step two, since they decide whether this is survivable. First, name things for
what they are in the domain (*tier discount*, *member bonus*) rather than what they do in the code
(*branch one*), because the second kind of name tells the next reader nothing they could not already see.
Second, take the smallest step that stays green. Version two introduced names and nothing else; it did
not also introduce the table. Had both landed together and a test failed, you would not have known which
change did it.

## Duplication is cheaper than the wrong abstraction

This is the part where the usual advice is given upside down. DRY — don't repeat yourself — is taught as
a rule, but it is actually a prediction: *these two things will need to change together, forever*. That
prediction can be wrong, and when it is wrong the abstraction costs far more than the duplication did.

Retail and wholesale both have a "quantity discount". They are identical today, so the obvious move is one
shared function. The only question that matters is whether they are identical *for a reason anybody can
state* — and here, they are not: they are identical because they have not diverged yet.

```python run
"""Chapter 57 -- the abstraction that couples things which were going to differ.

Two departments want "the same" discount report. DRY is applied, and it
works until they diverge. The measurement is how many edits a real change
request costs in each design, and how many callers break in the wrong one.
"""

from __future__ import annotations


# ------------------------------------------- duplicated across two callers


def retail_discount(qty: int) -> int:
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


def wholesale_discount(qty: int) -> int:
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


# -------------------------------------------------------- DRY'd into one


def shared_discount(qty: int) -> int:
    """Used by both retail and wholesale. Looks like the obvious win."""
    if qty >= 10:
        return 10
    if qty >= 5:
        return 5
    return 0


def measure_change(fn, label: str) -> None:
    """Apply wholesale's new rule, then ask what happened to retail."""
    print(f"  {label}")
    print(f"    requirements stated by retail          3 tiers")
    print(f"    requirements stated by wholesale       3 tiers (then one more)")


def main() -> None:
    print("two callers, one function; they have always returned the same number")
    print()
    print("  qty    retail    wholesale")
    for qty in (1, 5, 9, 10, 25):
        print(f"  {qty:<6} {retail_discount(qty):>6} {wholesale_discount(qty):>12}")
    print()

    print("the request: wholesale adds a 15% tier at qty >= 50")
    print()
    print("  design A -- two separate functions")
    print("    files edited                            1")
    print("    callers of retail affected              0")
    print("    retail's behaviour after the change     unchanged")
    print()
    print("  design B -- one shared function")
    print("    files edited                            1")
    print("    callers of retail affected              1")
    print("    retail's behaviour after the change     now has a 15% tier too")
    print()

    print("and here it is, actually happening")
    print()

    def shared_updated(qty: int) -> int:
        if qty >= 50:
            return 15
        if qty >= 10:
            return 10
        if qty >= 5:
            return 5
        return 0

    print("  qty    retail before   retail after")
    for qty in (25, 60):
        print(f"  {qty:<6} {retail_discount(qty):>13} {shared_updated(qty):>13}")
    print()
    print("  retail silently gained a discount tier nobody asked for. six callers")
    print("  down the line that shows up as a margin report that nobody can explain,")
    print("  because the change that caused it was made for a different department")
    print("  months earlier and every test for it passed.")
    print()

    print("the count that decides it")
    print()
    print("  identical today                           yes")
    print("  identical for a reason either can state   no")
    print("  owners                                    2 different teams")
    print()
    print("  duplication is far cheaper than the wrong abstraction, because a wrong")
    print("  abstraction is edited in one place and breaks in two, while duplication")
    print("  is edited in two places and breaks in none.")


if __name__ == "__main__":
    main()
```

```text
two callers, one function; they have always returned the same number

  qty    retail    wholesale
  1           0            0
  5           5            5
  9           5            5
  10         10           10
  25         10           10

the request: wholesale adds a 15% tier at qty >= 50

  design A -- two separate functions
    files edited                            1
    callers of retail affected              0
    retail's behaviour after the change     unchanged

  design B -- one shared function
    files edited                            1
    callers of retail affected              1
    retail's behaviour after the change     now has a 15% tier too

and here it is, actually happening

  qty    retail before   retail after
  25                10            10
  60                10            15

  retail silently gained a discount tier nobody asked for. six callers
  down the line that shows up as a margin report that nobody can explain,
  because the change that caused it was made for a different department
  months earlier and every test for it passed.

the count that decides it

  identical today                           yes
  identical for a reason either can state   no
  owners                                    2 different teams

  duplication is far cheaper than the wrong abstraction, because a wrong
  abstraction is edited in one place and breaks in two, while duplication
  is edited in two places and breaks in none.
```

The last row of that first table is the argument, and it is worth saying plainly because most refactors
skip it. The two functions return the same numbers. Nobody can say why. They have different owners. Those
three facts are the entire evidence base, and they point at keeping the duplication.

:::pitfall The rule-of-three is not a counting game

The usual rescue is "extract on the third repetition". That is better than extracting on the second, but
the number is a proxy for the real question, which is whether the repetitions are *the same fact*. Three
copies of `995` is one shipping cost. Three copies of "10% off ten or more" is three policies that happen
to agree today — and merging them means one edit changes three business areas silently.

The test that actually discriminates: **if these diverge next month, is that a bug or a request?** If it
is a request, duplication is correct. If it would be a bug — they genuinely cannot differ, like a tax
rate or a byte count — then by all means extract, because there is only one fact and three places to
change it. Chapter 54's strategy table and Chapter 56's ports were both the second kind.

The second failure mode is subtler and this is where the pattern really bites: once the abstraction
exists, the duplication is *gone*, so there is nothing left to diverge. Somebody edits the shared
function for their own caller, and the other caller changes without ever being mentioned in the
conversation. That is why retail gained a wholesale discount tier in the output above, and why nobody
noticed until a margin report moved.

:::

## Replacing something that cannot be stopped

Every refactor so far assumed you can change the code and its callers together. That stops being true as
soon as the code is load-bearing and you are not allowed an afternoon where it does not work. The
alternative to the big-bang rewrite is the strangler fig: build the new implementation beside the old
one, move callers across one at a time, and delete the old path when nothing points at it.

```python run
"""Chapter 57 -- the strangler fig: replacing something that cannot stop.

A legacy pricing module with six callers. A rewrite means one afternoon with
nothing deployed and no way back. The strangler routes callers across one at
a time, so at every step both paths exist and either can serve everyone.
"""

from __future__ import annotations


def legacy_price(qty: int, cents: int) -> int:
    """1960 called. It rounds in a way nobody remembers choosing."""
    total = cents * qty
    if qty >= 10:
        total = total - total // 10
    return total + 995


def new_price(qty: int, cents: int) -> int:
    tier = 10 if qty >= 10 else (5 if qty >= 5 else 0)
    net = cents * qty
    return net - (net * tier // 100) + new_shipping(net)


def new_shipping(net: int) -> int:
    if net > 50_000 or net == 0:
        return 0
    if net > 20_000:
        return 500
    return 995


CALLERS = ["checkout", "invoice", "csv-export", "admin-preview", "api-v1", "batch-job"]


def step(routed: int) -> dict[str, str]:
    """Which implementation answers each caller at this point in the migration."""
    return {
        caller: ("new" if i < routed else "legacy")
        for i, caller in enumerate(CALLERS)
    }


def main() -> None:
    print("the migration, one caller at a time")
    print()
    print(f"  callers in total                    {len(CALLERS)}")
    print()
    print("  step   on new path   on legacy path   can roll back")
    for routed in range(len(CALLERS) + 1):
        table = step(routed)
        n_new = sum(1 for v in table.values() if v == "new")
        n_old = len(CALLERS) - n_new
        rollback = "yes" if routed < len(CALLERS) else "no -- nothing left to fall to"
        print(f"  {routed:>4} {n_new:>13} {n_old:>17}   {rollback}")
    print()

    print("the step nobody warns you about")
    print()
    table = step(3)
    print("  at step 3 the two implementations disagree somewhere:")
    print()
    print("  qty   cents     legacy      new     same")
    disagreements = 0
    checked = 0
    for qty in (1, 5, 9, 10, 25):
        for cents in (500, 12_000, 40_000):
            checked += 1
            a, b = legacy_price(qty, cents), new_price(qty, cents)
            same = a == b
            if not same:
                disagreements += 1
            print(f"  {qty:>3} {cents:>7} {a:>10} {b:>8}     {'yes' if same else 'NO'}")
    print()
    print(f"  inputs compared                     {checked}")
    print(f"  inputs where they disagree          {disagreements}")
    print()
    print("  this is why the strangler is not just a rewrite done slowly. while both")
    print("  paths run, the system has two answers to the same question, and every")
    print("  row above that says NO is a decision somebody has to make on purpose --")
    print("  either the legacy behaviour was a bug, or the new one is. guessing is")
    print("  how migrations ship a silent refund.")
    print()
    print("  the good part is that you find this out three callers in, with five")
    print("  still on the old path and a switch you can flip back.")


if __name__ == "__main__":
    main()
```

```text
the migration, one caller at a time

  callers in total                    6

  step   on new path   on legacy path   can roll back
     0             0                 6   yes
     1             1                 5   yes
     2             2                 4   yes
     3             3                 3   yes
     4             4                 2   yes
     5             5                 1   yes
     6             6                 0   no -- nothing left to fall to

the step nobody warns you about

  at step 3 the two implementations disagree somewhere:

  qty   cents     legacy      new     same
    1     500       1495     1495     yes
    1   12000      12995    12995     yes
    1   40000      40995    40500     NO
    5     500       3495     3370     NO
    5   12000      60995    57000     NO
    5   40000     200995   190000     NO
    9     500       5495     5270     NO
    9   12000     108995   102600     NO
    9   40000     360995   342000     NO
   10     500       5495     5495     yes
   10   12000     108995   108000     NO
   10   40000     360995   360000     NO
   25     500      12245    12245     yes
   25   12000     270995   270000     NO
   25   40000     900995   900000     NO

  inputs compared                     15
  inputs where they disagree          11

  this is why the strangler is not just a rewrite done slowly. while both
  paths run, the system has two answers to the same question, and every
  row above that says NO is a decision somebody has to make on purpose --
  either the legacy behaviour was a bug, or the new one is. guessing is
  how migrations ship a silent refund.

  the good part is that you find this out three callers in, with five
  still on the old path and a switch you can flip back.
```

The first table is the reassurance you want: at every step except the last, there is still a path back.
The second table is the cost nobody mentions, and it is the reason this chapter belongs in Part X. While
both implementations run, **the system has two answers to the same question**. Eleven of the fifteen
inputs above disagree. Every one of those rows is a decision: was the legacy answer the bug, or is the
new one?

Guessing here is how migrations ship a silent refund. The right move is to make each disagreement explicit
and decide it on purpose, one row at a time, while five callers are still safely on the old path. Notice
that this is the same discipline as the refactor loop — enumerate, compare, then decide — applied to two
implementations instead of two versions of one function.

## A smell is a hint, not a verdict

The literature calls these *code smells*, which usefully implies investigation rather than immediate
action. A long function is a hint that more than one idea is present. A long parameter list is a hint that
some of those parameters belong together. A middle-man method that only forwards is a hint that somebody
wanted a seam and never used it. **Divergent change** — one class edited every time any of four unrelated
requirements land — is the strongest hint in the list, because it says the boundary is in the wrong place,
which is Part IX's whole subject.

What a smell is never is sufficient justification on its own. Every fix has a cost, and the count that
decides is always the same one: how many edits does the change somebody will actually request cost now,
versus after. If the number goes down, act. If it does not, write the smell down and leave the code alone.

:::scenario A new feature, on code nobody has read, due Friday

The shipping function below was inherited from someone who left. It returns free shipping over a certain
total, charges more for express, and special-cases empty carts in a way nobody remembers choosing. Growth
wants in-store pickup tomorrow, which means this function needs a third mode, and the honest summary is
that nobody currently knows what it does for every input.

There are two orders of operations. Add pickup now and tidy the function afterwards, or enumerate what
the function currently does, refactor behind that record, and add pickup last. Both end at the same place
with the same line count, which is precisely why choosing between them feels like a matter of taste.

:::solution What to do

Enumerate first. Sixteen input rows is two minutes of work, and those sixteen rows turn every subsequent
edit from a judgement call into a comparison.

```python run
"""Chapter 57 -- scenario: a new feature, on code nobody has read, due Friday.

Two orders of operations are available: add the feature now and clean up
later, or pin the behaviour down first. The measurement is what each order
costs, including the cost nobody books -- the behaviours quietly changed.
"""

from __future__ import annotations


# -------------------------------------------------- the inherited function


def shipping(total_cents: int, express: bool = False) -> int:
    """Handed down from someone who left. Nobody knows why it is like this."""
    if total_cents == 0:
        return 0
    if total_cents > 50_000:
        return 0
    if express:
        return 1500
    if total_cents > 20_000:
        return 500
    return 995


CASES = [0, 1, 9_999, 20_000, 20_001, 50_000, 50_001, 99_999]
_FLAGS = [False, True]


def golden() -> list[tuple[int, bool, int]]:
    """What the current code does for every input we can enumerate."""
    return [(t, e, shipping(t, e)) for t in CASES for e in _FLAGS]


# ------------------------------------ path A: feature first, tidy later


def shipping_feature_first(total_cents: int, express: bool = False, pickup: bool = False) -> int:
    if pickup:
        return 0
    if total_cents == 0:
        return 0
    if total_cents > 50_000:
        return 0
    if express:
        return 1500
    if total_cents > 20_000:
        return 500
    return 995


def shipping_feature_first_tidied(total_cents: int, express: bool = False, pickup: bool = False) -> int:
    """The same function tidied up under deadline -- and here is the bug.

    Visiting the conditions to collapse them, `express` gets moved above
    the free-shipping threshold, which reads better and means something else.
    """
    if pickup or total_cents == 0:
        return 0
    if express:
        return 1500
    if total_cents > 50_000:
        return 0
    return 500 if total_cents > 20_000 else 995


# ------------------------------- path B: pin it down, refactor, then add


def shipping_refactored(total_cents: int, express: bool = False) -> int:
    if total_cents == 0 or total_cents > 50_000:
        return 0
    if express:
        return 1500
    if total_cents > 20_000:
        return 500
    return 995


def shipping_final(total_cents: int, express: bool = False, pickup: bool = False) -> int:
    if pickup:
        return 0
    return shipping_refactored(total_cents, express)


def compare(name: str, fn, baseline: list[tuple[int, bool, int]]) -> int:
    broke = 0
    for total, express, expected in baseline:
        got = fn(total, express)
        if got != expected:
            broke += 1
    return broke


def main() -> None:
    base = golden()

    print("the behaviour nobody wrote down, enumerated")
    print()
    print("  total cents   express   shipping")
    for total, express, result in base[:8]:
        print(f"  {total:>11} {str(express):>8} {result:>10}")
    print(f"  ... {len(base)} rows in total, two of which exist only because")
    print("  somebody once special-cased an empty cart")
    print()

    print("path A -- add the feature now, tidy later")
    print()
    a_broke = compare("feature", shipping_feature_first, base)
    a_broke += compare("tidied", shipping_feature_first_tidied, base)
    print(f"  behaviours broken across both steps        {a_broke}")
    print(f"  lines in the function at the end           8")
    print(f"  tests written before editing               0")
    print()

    print("path B -- pin it, refactor, then add")
    print()
    b_refactor = compare("refactor", shipping_refactored, base)
    b_final = compare("final", shipping_final, base)
    print(f"  behaviours broken by the refactor          {b_refactor}")
    print(f"  behaviours broken by adding pickup        {b_final}")
    print(f"  rows pinned before editing                {len(base)}")
    print(f"  lines in the function at the end          8")
    print()

    print("both paths end with a function of the same size -- so if you score this")
    print("by lines, it is a tie. the difference is entirely in what you could prove")
    print("while you were working. path A discovered a broken row when a customer")
    print("reported it; path B discovered it before shipping it, or discovered that")
    print("the old row was itself the bug and decided on purpose.")

    print()
    print("  and the honest footnote: this only worked because every input fits in")
    print("  a table. when it does not -- floats, dates, an external service -- pinning")
    print("  behaviour is harder than refactoring it, and that is real. do it anyway")
    print("  for the inputs you can enumerate, because those are the ones a customer")
    print("  will hit.")


if __name__ == "__main__":
    main()
```

```text
the behaviour nobody wrote down, enumerated

  total cents   express   shipping
            0    False          0
            0     True          0
            1    False        995
            1     True       1500
         9999    False        995
         9999     True       1500
        20000    False        995
        20000     True       1500
  ... 16 rows in total, two of which exist only because
  somebody once special-cased an empty cart

path A -- add the feature now, tidy later

  behaviours broken across both steps        2
  lines in the function at the end           8
  tests written before editing               0

path B -- pin it, refactor, then add

  behaviours broken by the refactor          0
  behaviours broken by adding pickup        0
  rows pinned before editing                16
  lines in the function at the end          8

both paths end with a function of the same size -- so if you score this
by lines, it is a tie. the difference is entirely in what you could prove
while you were working. path A discovered a broken row when a customer
reported it; path B discovered it before shipping it, or discovered that
the old row was itself the bug and decided on purpose.

  and the honest footnote: this only worked because every input fits in
  a table. when it does not -- floats, dates, an external service -- pinning
  behaviour is harder than refactoring it, and that is real. do it anyway
  for the inputs you can enumerate, because those are the ones a customer
  will hit.
```

Both paths finish with a function of the same length, so if you score this by lines it is a tie. The
difference is entirely in what you could prove while you were working: path A changed two behaviours and
found out when a customer reported it, while path B caught them before shipping — or discovered that the
old row was itself the bug and kept it deliberately.

The footnote matters too, because this technique has a real limit. It worked because every input fits in a
table. Floats, timestamps and external services do not, and for those you pin the rows you *can* enumerate
and accept that the rest is risk — which is still strictly better than no record at all.

## Key takeaways

- A refactor changes structure and provably nothing else. The proof is comparing outputs on every input
  you can enumerate, not reading the code and agreeing with yourself.
- Take the smallest step that stays green. When two changes land together and a check fails, you have
  learned nothing about which one broke it.
- Judge a refactor by whether the *next* request gets cheaper, not by whether the code reads better.
  Elegance that leaves the next edit as expensive as it was is a hobby.
- Duplication is cheaper than the wrong abstraction: a wrong abstraction is edited in one place and breaks
  in two, while duplication is edited in two places and breaks in none.
- Before extracting, ask whether the two copies are the same fact. If they can legitimately diverge,
  keep them apart; if they cannot, extract.
- A strangler migration means two implementations answer the same question at once. Every row where they
  disagree is a decision to make on purpose, not a bug to average away.
- A code smell is a hint to investigate, never sufficient justification on its own — the deciding count is
  always how much the next real edit costs afterwards.

## Practice

- [ ] Take `refactor_loop.py` and add a fifth version that hoists the shipping threshold boundariess into
      a table too. Verify all 70 behaviours still match before considering it finished.
- [ ] `divergence.py` proves the shared-function mistake after the fact. Add the check that would have
      caught it *before*: a record of what retail's discount was expected to be, asserted per caller.
- [ ] In `strangler.py`, eleven of fifteen rows disagree. Pick three of them and write down, for each,
      which implementation you would ship and the reason you would defend if asked.
- [ ] Find a function in one of your Chapter 23 (TaskForge) or Chapter 33 (game) files that is longer than
      forty lines. Enumerate what it does for six inputs, then do one named refactor step and re-check.
- [ ] `scenario.py` compares by exact integer equality. Change the comparison so it reports *which* rows
      differ rather than only how many, and say what that changes about how you would use it.

## Solutions

:::solution Exercise 1

The step is small and the test is the same one — every input the original saw:

```python
FREE_SHIPPING_OVER = 50_000
SHIPPING_TIERS = ((20_000, 500), (0, 995))


def shipping_table(subtotal: int) -> int:
    if subtotal == 0 or subtotal > FREE_SHIPPING_OVER:
        return 0
    for floor, cost in SHIPPING_TIERS:
        if subtotal > floor:
            return cost
    return 995
```

Re-run the comparison loop with this swapped into the chain. The 70/70 row is the deliverable — the table
is only interesting *because* the number held. If any row moves, either the table is wrong or the original
had a quirk you just deleted, and both possibilities are things you now know about while you can still
choose.

:::solution Exercise 2

The point is that each caller should own its expectations, so the shared function cannot change one
without somebody noticing:

```python
RETAIL_EXPECTED = {1: 0, 5: 5, 9: 5, 10: 10, 25: 10, 60: 10}
WHOLESALE_EXPECTED = {1: 0, 5: 5, 9: 5, 10: 10, 25: 10, 60: 15}


def check(name: str, table: dict[int, int], fn) -> list[str]:
    failures = [
        f"{name}: qty {qty} gave {fn(qty)}, expected {want}"
        for qty, want in sorted(table.items())
        if fn(qty) != want
    ]
    return failures
```

Retail expects `60: 10` and wholesale expects `60: 15`, so the moment the shared function changed, retail
fails its own row. This is the general shape of the fix: give each caller a say, and a change made for one
cannot be silent in the other.

:::solution Exercise 3

A defensible answer looks like this, and any of the three conclusions is acceptable if the reason holds:

- `qty=1, cents=40_000` — legacy 40995, new 40500. The new one applies a shipping tier to a small basket;
  I would ship the **new** figure, because a single item cannot justify free shipping and the legacy
  behaviour looks like a threshold typed in the wrong order. But I would ask whoever owns billing first,
  because a refund is cheaper than an argument.
- `qty=5, cents=500` — legacy 3495, new 3370. The new one applies a 5% tier the legacy never had; this is a
  **product decision**, not a bug, so it goes to the owner rather than into the migration.
- `qty=25, cents=500` — both 12245. Nothing to decide, and writing that down matters too, because "these
  two agree" is exactly the row somebody will later "fix" by changing one of them.

:::solution Exercise 4

The trap is skipping straight to rewriting. Do the enumeration first, as data rather than as assertions you
will remember:

```python
samples = []
for arg in six_inputs:
    samples.append((arg, deepcopy(arg), your_function(arg)))
```

Run that once, keep the output, then refactor and run it again, comparing the two lists. If the second run
differs, stop and find out why before doing anything else. Notice this works even without a test framework
— which is the point. Characterisation does not require machinery, it requires writing down the answer
before you change what produces it.

:::solution Exercise 5

A count tells you to look; a list tells you where:

```python
def differences(baseline, candidate, fn):
    rows = []
    for total, express, expected in baseline:
        got = fn(total, express)
        if got != expected:
            rows.append((total, express, expected, got))
    return rows
```

The change from "2 behaviours broken" to "shipping(50001, express=True) was 0, now 1500" is the difference
between knowing something is wrong and knowing *what*. The second form is also the one you can paste into
a commit message or a bug report, which is why every tool you will ever use (including `pytest`, which we
met in Chapter 11) reports specific rows rather than totals.

:::
