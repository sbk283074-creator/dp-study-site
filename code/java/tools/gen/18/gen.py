#!/usr/bin/env python3
"""Generate chapters/18-dates-times-and-bigdecimal.md.

    python3 tools/gen/18/gen.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "18-dates-times-and-bigdecimal.md")

BLOCKS = {
    "localdates": gen.run("LocalDates.java"),
    "localtimes": gen.run("LocalTimes.java"),
    "instantszones": gen.run("InstantsZones.java"),
    "formatting": gen.run("Formatting.java"),
    "parsing": gen.run("Parsing.java"),
    "bigdecimal": gen.run("BigDecimalBasics.java"),
    "badoperator": gen.bad("BadOperator.java", "bad operand types for binary operator"),
    "throwdivide": gen.throw("ThrowDivide.java", "Non-terminating decimal expansion"),
    "throwbaddate": gen.throw("ThrowBadDate.java", "Invalid date 'FEBRUARY 30'"),
    "scenario": gen.run("Scenario.java"),
    "sol1": gen.run("Sol1.java"),
    "sol2": gen.run("Sol2.java"),
    "sol3": gen.run("Sol3.java"),
    "sol4": gen.run("Sol4.java"),
}

TEMPLATE = r"""---
chapter: 18
part: 2
title: Dates, Times, BigDecimal and Formatting
summary: Model a date as a date rather than a string, a moment as a moment rather than a date, and money as a decimal rather than a double — and know which of the java.time types answers which question.
minutes: 55
tags: [java.time, LocalDate, Instant, Duration, Period, BigDecimal, formatting, rounding]
---

Two of the most expensive classes of bug in business software come from the same mistake: using a
type that is *convenient* for one that is *correct*. A date stored as a `String` cannot be compared,
sorted or advanced. An amount stored as a `double` cannot be added without losing a fraction of a
cent, and a system that does it a million times a day loses real money. This chapter is about the two
libraries that fix both: `java.time`, which separates a date, a time, a moment and a duration because
they answer different questions, and `java.math.BigDecimal`, which represents a decimal exactly.

## A date is not a moment

`LocalDate` is a date with no time and no zone: a birthday, an invoice date, the day a report covers.

@@localdates@@

Every value here came from arithmetic on a fixed input, which is the habit to build. `LocalDate.now()`
would have made this transcript a fact about the day it was captured; `LocalDate.of(2026, 3, 14)` makes
it a fact about the calendar. **Dates in tests and examples are literals.** The only place `now()`
belongs is inside the application code that genuinely means "today".

The first six lines are accessors and arithmetic. `2026-03-14` is a `SATURDAY` and day `73` of the
year, and `minusMonths(3)` gives `2025-12-14` — the 14th, because the day of month is preserved when
it exists.

`Period.between` is the interesting call. It returned `P2M18D` — two months and eighteen days — while
`ChronoUnit.DAYS.between` returned `79` for the same pair of dates. Both are correct and they answer
different questions. `Period` is *calendar* arithmetic: two months and eighteen days is what a human
would say, and it is what you want for "the contract runs for two months". `ChronoUnit.DAYS` is exact
elapsed time, and it is what you want for "how many days until the deadline". Mixing them up is how a
billing period comes out one day short.

`compareTo` returned `-1`, which is the sign convention from Chapter 12: negative means the receiver
sorts first. `LocalDate` implements `Comparable`, so dates sort correctly in a `TreeMap` with no
comparator at all.

## A time, and a date and time together

@@localtimes@@

`Duration.between(9:15, 17:45)` is `PT8H30M`, `510` minutes, and `8h 30m` when split into parts.
`start.plus(shift)` returns `17:45`, so a `Duration` can be added to a `LocalTime` — it is a quantity
of exact time, and a `LocalTime` is a point on a clock face.

The `overnight` line is the trap. `Duration.between(LocalTime.of(23, 0), LocalTime.of(1, 30))` is
`PT-21H-30M` — **negative**, because on a clock face 01:30 comes before 23:00. A `LocalTime` has no
date, so it cannot know that you meant the next morning. Shift work, overnight jobs and anything that
crosses midnight needs a `LocalDateTime`, not two `LocalTime`s.

`truncatedTo(ChronoUnit.HOURS)` gave `2026-03-14T09:00`, which is the clean way to drop precision
without string surgery.

## An instant is a moment; a zone is how it is displayed

`Instant` is a point on the timeline, counted from 1970-01-01T00:00:00Z. It has no zone, because a
moment does not need one — `1773489600` seconds is the same instant everywhere.

@@instantszones@@

One instant, four renderings. `Asia/Shanghai` shows `20:00` with offset `+08:00`;
`America/New_York` shows `08:00` with offset `-04:00`, because by 14 March 2026 daylight saving is in
effect there; `Europe/London` shows `12:00` with offset `Z`, because it is not — British Summer Time
does not begin until the last Sunday in March. None of those numbers was computed by the program.
They came from the zone rules the JDK ships, which is precisely why you must not hand-roll them.

This is the rule to carry: **store and transmit an `Instant`; convert to a `ZoneId` only for display
or for a business rule that genuinely depends on a local calendar.** An offset is not a zone. `+08:00`
tells you where a clock was set; `Asia/Shanghai` also knows that the offset has never changed, which
matters the moment you deal with a zone that has daylight saving.

:::warning
**`Instant.now()` and every `now()` are non-deterministic, so they must not appear in a transcript
that is checked against a run.** The same is true of a default `LocalDate.now()` inside a method.
Inject the clock — take a `LocalDate` or a `Clock` as a parameter — and the method becomes both
testable and reproducible. Chapter 19 builds the harness that needs this.
:::

## Formatting is a choice, and the locale is part of it

@@formatting@@

`toString()` gave `2026-03-14T09:05:07`, which is ISO-8601 and is what you want for a log line or a
wire format. `ofPattern("dd/MM/yyyy HH:mm")` gave `14/03/2026 09:05` for humans.

The two day-name lines are the point of this section. The same instant is `Saturday` in
`Locale.US` and `Samstag` in `Locale.GERMAN`. A pattern containing `EEEE`, `MMMM` or `QQQ` produces
text, and text depends on a locale — so **a formatter that produces text must be given one
explicitly.** `QQQ` gave `Q1`, and `ISO_WEEK_DATE` gave `2026-W11-6`, the ISO week-based year, week
and day-of-week.

`'on' dd 'of' MMMM` shows the quoting rule: letters are pattern symbols, so literal words are wrapped
in single quotes. Without them, `o`, `n` and `f` would be read as (invalid) pattern letters and
`ofPattern` would throw.

## Parsing is the inverse, and it fails loudly

@@parsing@@

`LocalDate.parse` takes a formatter, and the round trip works: `14/03/2026` parses and formats back to
itself. Note that `2026-03-14` and `14/03/2026` are the *same* `LocalDate` — the string is a rendering
and the object is the value.

The last block is the important one. `2026-13-01` is not a date, and instead of guessing or returning
`null`, `parse` threw `DateTimeParseException` naming the input. Chapter 13's rule applies: an
exception at the boundary where bad data arrives is far cheaper than a wrong value propagating.

## Money is not a double

A `double` is a binary fraction. `0.1` has no exact binary representation, so the error is present
before any arithmetic happens, and it shows up in the last digit.

@@bigdecimal@@

`0.1 + 0.2` is `0.30000000000000004`, so `sum == 0.3` is `false`. That is not a rounding quirk you can
tune away — it is what the type is. The `BigDecimal` version adds `0.1` and `0.2` and gets exactly
`0.3`, and the comparison against a literal `0.3` is `true`.

The `from double` line is the one that catches people out. `new BigDecimal(0.1)` gives
`0.1000000000000000055511151231257827021181583404541015625`, because it faithfully represents the
`double` it was handed, error included. **Construct from a `String`**, or use
`BigDecimal.valueOf(double)`, which goes through `Double.toString` and gives `0.1`. Never
`new BigDecimal(double)`.

Scale is not the only thing `double` gets wrong in a total. The last two lines of that transcript are
one invoice line computed twice: `0.35 × 12` is `4.199999999999999` as a `double` and `4.200` as a
`BigDecimal`. The difference is not academic — the `double` version is the one that makes a
reconciliation report disagree with itself.

### `equals` and `compareTo` disagree, and both are right

`new BigDecimal("2.0").equals(new BigDecimal("2.00"))` is `false`, and
`compareTo` returns `0`. `equals` compares the value *and* the scale, so `2.0` and `2.00` are different
numbers in the same way that `2.0` and `2.00` are different strings of digits; `compareTo` compares
numeric value only.

The practical rule: **use `compareTo` for money.** A map keyed on `BigDecimal`, or a `Set`, or an
`equals` check after two different code paths produced the same amount with different scales, will
disagree with your intent. `stripTrailingZeros()` normalised `2.00` to `2`, which is one way to make
`equals` behave — and it introduces a scale of its own, so `compareTo` is still the safer habit.

### Rounding is a policy

`setScale(2, RoundingMode.HALF_UP)` gave `2.35` for `2.345`. `HALF_EVEN` gave `2.34` for the same
input and `2.36` for `2.355` — it rounds a tie to the *even* digit. That is banker's rounding, and it
is not a curiosity: it is what accounting systems use, because rounding every half up biases a long
series of amounts upward. **Pick a rounding mode deliberately and name it at the call site** — the
overload without one throws rather than choosing for you.

### There is no operator overloading

@@badoperator@@

`total + 1` does not compile, and the message names the two types. Java has no operator overloading,
so every `BigDecimal` operation is a method call: `add`, `subtract`, `multiply`, `divide`,
`compareTo`. It reads more heavily than `+` and it is the reason `BigDecimal` code is verbose — that
verbosity is the price of exactness.

:::pitfall
**`BigDecimal` is immutable, so every operation returns a new object.** `total.add(x);` as a statement
does nothing at all, because the result is discarded — the same silent no-op as the terminal-less
stream from Chapter 15. Write `total = total.add(x);`. The compiler cannot help you here, because the
statement is perfectly legal.
:::

### Division needs a scale

@@throwdivide@@

`divide` is the one operation with no exact answer in general, so it refuses rather than guessing.
`Non-terminating decimal expansion; no exact representable decimal result.` is the exception, and the
fix is the three-argument overload: `divide(divisor, scale, roundingMode)`.

Choosing the scale *is* choosing where the money goes. The last solution shows `10.00` divided three
ways at scale 2: three parts of `3.33` sum to `9.99`, and a cent has vanished. That is not a bug to
fix — it is a decision you have to make, and the alternatives (carry the remainder, allocate it to one
part, or use a scale of 4 internally and round only at the boundary) are all defensible. What is not
defensible is not noticing.

### An invalid date is not a `null`

@@throwbaddate@@

`LocalDate.of(2026, 2, 30)` throws `Invalid date 'FEBRUARY 30'` rather than rolling over into March.
That is the behaviour you want at a system boundary: a date that does not exist is a data error, and
silently normalising it hides a corrupt upstream.

:::scenario The invoice that was a cent out

An invoicing service totals order lines, applies 20% tax, and stores the result. A customer disputes
the total by one cent on a specific invoice.

:::solution
Two things have to be true for the total to be explainable, and the code has to make both explicit.

First, every intermediate amount carries a scale. `unitPrice.multiply(BigDecimal.valueOf(qty))` gives
an exact product at the scale of the price, so the running `net` never accumulates error. Second, tax
is computed once on the net and rounded **once**, at the boundary where it becomes money:
`net.multiply(TAX).setScale(2, RoundingMode.HALF_UP)`. Rounding per line and then summing gives a
different total from summing and then rounding, and the customer will eventually find the difference.

The dates are the other half of an invoice. `issued.plusDays(30)` gives the due date, and
`ChronoUnit.DAYS.between` reports the term as a number rather than as a string to be re-parsed.

@@scenario@@

Three lines of `19.99 × 3`, `4.05 × 1` and `0.35 × 12` give `59.97`, `4.05` and `4.20`, and the net is
`68.22`. Tax at 20% is `13.644`, which rounds to `13.64`, so the gross is `81.86`. Every one of those
figures is exact decimal arithmetic — the `0.35 × 12 = 4.20` line in particular has no
floating-point residue at all, where a `double` version of the same multiplication gives
`4.199999999999999` and a report that will not reconcile.

`issued = 2026-03-14` and `due = 2026-04-13` are 30 days apart, and the transcript prints that count
from `ChronoUnit.DAYS` rather than stating it. The month boundary is crossed, which is exactly where a
hand-rolled "add one month" would have produced `2026-04-14`.
:::

## Solutions

### 1. A money type with one rounding policy

@@sol1@@

`money(String)` is the single place where a scale and a rounding mode are chosen, and every amount in
the program goes through it. `19.995` becomes `20.00`, and `equals` now agrees with `compareTo`
because both operands were normalised by the same function.

The last four lines are the honest part. `10.00` divided three ways at scale 2 is `3.33`, three of
those is `9.99`, and `lost = 0.01`. A money type that hides this is lying; one that reports it lets
the caller decide whether the cent goes to a rounding account, to the largest line, or to the
customer.

### 2. Never call `now()` inside a rule

@@sol2@@

`daysUntil` and `status` take both dates as parameters. There is no `LocalDate.now()` anywhere, so
the behaviour is fully determined by the arguments and the method can be tested on any date —
including the awkward ones.

The three printed rows are the three branches: `overdue by 4`, `due today` and `due in 6`. The
`acrossFeb` line answers `28` for 31 January to 28 February 2026, which is the kind of count a
hand-written month-length table gets wrong in a leap year.

### 3. One formatter per purpose, each with an explicit locale

@@sol3@@

Two `static final` formatters: `WIRE` for storage and transport, `HUMAN` for display, both with a
named `Locale`. `Locale.ROOT` on the wire formatter is deliberate — a numeric ISO pattern must not
change because a server was started in a different region.

`roundTrip = true` is the property worth having: anything you format with `WIRE` parses back to the
same date. That property is what makes a wire format safe, and it is cheap to assert.

### 4. A `Period` is calendar time; a `Duration` is exact time

@@sol4@@

31 January to 1 March 2025 is `P1M1D` as a `Period` — one month and one day, which is what a person
would say — and `29` days as `ChronoUnit.DAYS`, which is what a clock would say. Neither is wrong.

`from.plus(Period.between(from, to))` returns exactly `to`, which is the property that makes `Period`
useful for calendar work: it round-trips through date arithmetic. `Duration.between` on two
`LocalDateTime`s one day apart gives `PT24H`, exact time with no calendar involved.

The rule: **`Period` for calendar rules, `Duration` for elapsed time.** A subscription that runs "one
month" is a `Period`; a timeout is a `Duration`. And note that `Period.between` returned `getDays() ==
1`, not `29` — the days component is a remainder, not a total, which is why `ChronoUnit.DAYS` exists.

## Key takeaways

- `LocalDate` is a date, `LocalTime` a time, `LocalDateTime` both, `Instant` a moment on the timeline,
  and `ZonedDateTime` a moment rendered in a zone. Pick the one that matches the question.
- Never call `now()` inside a rule. Take the date as a parameter and the method becomes testable and
  reproducible; a transcript that contains `now()` cannot be verified.
- `Period` is calendar arithmetic (`P2M18D`) and `ChronoUnit.DAYS` is exact elapsed time (`79`) for
  the same pair of dates. Use `Period` for "one month" and days for "how long until".
- A `Duration` between two `LocalTime`s can be negative, because a clock face has no date. Anything
  crossing midnight needs a `LocalDateTime`.
- Store and transmit an `Instant`; convert to a `ZoneId` for display. An offset is not a zone, and
  daylight saving is why the difference matters.
- A formatter that produces text needs an explicit `Locale`, or the same instant renders differently
  on a differently configured machine. Literal text in a pattern must be single-quoted.
- `new BigDecimal(double)` reproduces the `double`'s error. Construct from a `String`, or use
  `BigDecimal.valueOf`.
- `BigDecimal.equals` compares scale as well as value, so `2.0` is not `2.00`; use `compareTo` for
  money.
- `setScale` needs a `RoundingMode`. `HALF_UP` and `HALF_EVEN` differ on ties, and `HALF_EVEN` is the
  accounting convention.
- `divide` without a scale throws, because most divisions have no exact decimal answer. Choosing the
  scale is choosing where the remainder goes.

## Practice

- [ ] Write a method that takes an invoice date and a term in days and returns the due date, then
      test it across a month boundary, a year boundary and a leap day.
- [ ] Take a program that computes a price with `double` and rewrite it with `BigDecimal`. List the
      places where the answer changed in the last digit.
- [ ] Format the same `Instant` in three zones and in two locales, and say which of the five
      renderings you would put in a log line and why.
- [ ] Compute a total by rounding each line and then summing, and again by summing and then rounding
      once. Find an input where the two differ and say which you would ship.
- [ ] Write a `Period`-based subscription renewal that adds one month to 31 January, and check what
      the JDK does with a month that has no 31st.
- [ ] Explain why `LocalDate.parse("2026-13-01")` throws rather than returning `null`, and write the
      `try`/`catch` you would put at a system boundary.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `issued.plusDays(term)`. Test 31 January plus 30 days, 31 December plus 1 day, and
   28 February 2028 plus 1 day — `LocalDate` handles the leap year and the month lengths, which is
   exactly why you do not write the arithmetic yourself.
2. `BigDecimal` throughout, with `money()` normalising scale and rounding mode. The changed answers
   are the ones that were only wrong in the last digit — a `double` total of `0.30000000000000004`
   becomes `0.3` — and the reason to list them is that each is a place a reconciliation report
   previously disagreed with itself.
3. One zone and `Locale.ROOT`: a log line should be unambiguous and sortable, so `Instant.toString()`
   or an ISO-8601 rendering with an explicit offset. The other renderings are for people, not files.
4. Rounding per line can differ by a cent from rounding the total, because each line's discarded
   fraction is independent. Round once, at the boundary where the number becomes money, and keep full
   precision internally.
5. `LocalDate.of(2026, 1, 31).plusMonths(1)` gives `2026-02-28` — the day is clamped to the last valid
   day rather than rolling into March. That is the documented behaviour and it is why "one month" is
   a policy decision, not an arithmetic one.
6. Because a parse failure is a data error at a boundary, and `null` would push the failure to a later
   line with less context. Catch `DateTimeParseException`, and either reject the input with a message
   naming it or convert to a domain-specific exception.
"""

gen.write(TEMPLATE, BLOCKS)
