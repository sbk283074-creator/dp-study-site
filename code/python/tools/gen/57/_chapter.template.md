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

<!--BLOCK:refactor_loop-->

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

<!--BLOCK:divergence-->

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

<!--BLOCK:strangler-->

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

<!--BLOCK:scenario-->

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
