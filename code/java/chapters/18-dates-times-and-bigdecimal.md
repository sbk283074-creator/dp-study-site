---
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

```java run
import java.time.LocalDate;
import java.time.Month;
import java.time.Period;
import java.time.temporal.ChronoUnit;

public class LocalDates {
    public static void main(String[] args) {
        LocalDate d = LocalDate.of(2026, Month.MARCH, 14);

        System.out.println("date       = " + d);
        System.out.println("dayOfWeek  = " + d.getDayOfWeek());
        System.out.println("dayOfYear  = " + d.getDayOfYear());
        System.out.println("plusDays   = " + d.plusDays(10));
        System.out.println("minusMonths= " + d.minusMonths(3));
        System.out.println("isLeapYear = " + d.isLeapYear());

        LocalDate e = LocalDate.of(2026, 6, 1);
        System.out.println("period     = " + Period.between(d, e));
        System.out.println("days apart = " + ChronoUnit.DAYS.between(d, e));
        System.out.println("months     = " + ChronoUnit.MONTHS.between(d, e));
        System.out.println("equals     = " + d.equals(LocalDate.of(2026, 3, 14)));
        System.out.println("compareTo  = " + Integer.signum(d.compareTo(e)));
    }
}
```

```text
date       = 2026-03-14
dayOfWeek  = SATURDAY
dayOfYear  = 73
plusDays   = 2026-03-24
minusMonths= 2025-12-14
isLeapYear = false
period     = P2M18D
days apart = 79
months     = 2
equals     = true
compareTo  = -1
```

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

```java run
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.temporal.ChronoUnit;

public class LocalTimes {
    public static void main(String[] args) {
        LocalTime start = LocalTime.of(9, 15);
        LocalTime end = LocalTime.of(17, 45);
        Duration shift = Duration.between(start, end);

        System.out.println("duration   = " + shift);
        System.out.println("minutes    = " + shift.toMinutes());
        System.out.println("parts      = " + shift.toHoursPart() + "h " + shift.toMinutesPart() + "m");
        System.out.println("plus       = " + start.plus(shift));

        Duration overnight = Duration.between(LocalTime.of(23, 0), LocalTime.of(1, 30));
        System.out.println("overnight  = " + overnight);

        LocalDateTime dt = LocalDateTime.of(2026, 3, 14, 9, 15, 30);
        System.out.println("datetime   = " + dt);
        System.out.println("truncated  = " + dt.truncatedTo(ChronoUnit.HOURS));
    }
}
```

```text
duration   = PT8H30M
minutes    = 510
parts      = 8h 30m
plus       = 17:45
overnight  = PT-21H-30M
datetime   = 2026-03-14T09:15:30
truncated  = 2026-03-14T09:00
```

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

```java run
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;

public class InstantsZones {
    public static void main(String[] args) {
        Instant fixed = Instant.parse("2026-03-14T12:00:00Z");
        System.out.println("instant  = " + fixed);
        System.out.println("epochSec = " + fixed.getEpochSecond());

        for (String id : new String[] {"UTC", "Europe/London", "Asia/Shanghai", "America/New_York"}) {
            ZonedDateTime z = fixed.atZone(ZoneId.of(id));
            System.out.printf("%-16s %s  offset=%s%n", id, z.toLocalDateTime(), z.getOffset());
        }
    }
}
```

```text
instant  = 2026-03-14T12:00:00Z
epochSec = 1773489600
UTC              2026-03-14T12:00  offset=Z
Europe/London    2026-03-14T12:00  offset=Z
Asia/Shanghai    2026-03-14T20:00  offset=+08:00
America/New_York 2026-03-14T08:00  offset=-04:00
```

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

```java run
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

public class Formatting {
    public static void main(String[] args) {
        LocalDateTime dt = LocalDateTime.of(2026, 3, 14, 9, 5, 7);

        System.out.println("toString  = " + dt);
        System.out.println("pattern   = "
                + dt.format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")));
        System.out.println("dayNameUS = "
                + dt.format(DateTimeFormatter.ofPattern("EEEE", Locale.US)));
        System.out.println("dayNameDE = "
                + dt.format(DateTimeFormatter.ofPattern("EEEE", Locale.GERMAN)));
        System.out.println("quoted    = "
                + dt.format(DateTimeFormatter.ofPattern("'on' dd 'of' MMMM", Locale.US)));
        System.out.println("isoWeek   = " + dt.format(DateTimeFormatter.ISO_WEEK_DATE));
        System.out.println("quarter   = "
                + dt.format(DateTimeFormatter.ofPattern("QQQ", Locale.US)));
        System.out.println("unpadded  = " + dt.format(DateTimeFormatter.ofPattern("d/M/yyyy")));
    }
}
```

```text
toString  = 2026-03-14T09:05:07
pattern   = 14/03/2026 09:05
dayNameUS = Saturday
dayNameDE = Samstag
quoted    = on 14 of March
isoWeek   = 2026-W11-6
quarter   = Q1
unpadded  = 14/3/2026
```

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

```java run
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

public class Parsing {
    public static void main(String[] args) {
        DateTimeFormatter iso = DateTimeFormatter.ISO_LOCAL_DATE;
        DateTimeFormatter dmy = DateTimeFormatter.ofPattern("dd/MM/yyyy");

        System.out.println("iso       = " + LocalDate.parse("2026-03-14", iso));
        System.out.println("dmy       = " + LocalDate.parse("14/03/2026", dmy));
        System.out.println("roundTrip = " + LocalDate.parse("14/03/2026", dmy).format(dmy));

        try {
            LocalDate.parse("2026-13-01", iso);
        } catch (DateTimeParseException e) {
            System.out.println("rejected  = " + e.getClass().getSimpleName()
                    + " on " + e.getParsedString());
        }
    }
}
```

```text
iso       = 2026-03-14
dmy       = 2026-03-14
roundTrip = 14/03/2026
rejected  = DateTimeParseException on 2026-13-01
```

`LocalDate.parse` takes a formatter, and the round trip works: `14/03/2026` parses and formats back to
itself. Note that `2026-03-14` and `14/03/2026` are the *same* `LocalDate` — the string is a rendering
and the object is the value.

The last block is the important one. `2026-13-01` is not a date, and instead of guessing or returning
`null`, `parse` threw `DateTimeParseException` naming the input. Chapter 13's rule applies: an
exception at the boundary where bad data arrives is far cheaper than a wrong value propagating.

## Money is not a double

A `double` is a binary fraction. `0.1` has no exact binary representation, so the error is present
before any arithmetic happens, and it shows up in the last digit.

```java run
import java.math.BigDecimal;
import java.math.RoundingMode;

public class BigDecimalBasics {
    public static void main(String[] args) {
        double sum = 0.1 + 0.2;
        System.out.println("double sum   = " + sum);
        System.out.println("double == 0.3= " + (sum == 0.3));

        BigDecimal a = new BigDecimal("0.1");
        BigDecimal b = new BigDecimal("0.2");
        System.out.println("decimal sum  = " + a.add(b));
        System.out.println("decimal == .3= " + a.add(b).equals(new BigDecimal("0.3")));

        System.out.println("from double  = " + new BigDecimal(0.1));
        System.out.println("valueOf      = " + BigDecimal.valueOf(0.1));

        System.out.println("scale 0.30   = " + new BigDecimal("0.30").scale());
        System.out.println("equals 2.0   = " + new BigDecimal("2.0").equals(new BigDecimal("2.00")));
        System.out.println("compare 2.0  = " + new BigDecimal("2.0").compareTo(new BigDecimal("2.00")));
        System.out.println("stripped     = " + new BigDecimal("2.00").stripTrailingZeros());

        System.out.println("half up      = " + new BigDecimal("2.345").setScale(2, RoundingMode.HALF_UP));
        System.out.println("half even .5 = " + new BigDecimal("2.345").setScale(2, RoundingMode.HALF_EVEN));
        System.out.println("half even .6 = " + new BigDecimal("2.355").setScale(2, RoundingMode.HALF_EVEN));

        double qty = 12;
        double price = 0.35;
        System.out.println("double line  = " + (qty * price));
        System.out.println("decimal line = "
                + new BigDecimal("0.35").multiply(BigDecimal.valueOf(qty)));
    }
}
```

```text
double sum   = 0.30000000000000004
double == 0.3= false
decimal sum  = 0.3
decimal == .3= true
from double  = 0.1000000000000000055511151231257827021181583404541015625
valueOf      = 0.1
scale 0.30   = 2
equals 2.0   = false
compare 2.0  = 0
stripped     = 2
half up      = 2.35
half even .5 = 2.34
half even .6 = 2.36
double line  = 4.199999999999999
decimal line = 4.200
```

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

```java bad
import java.math.BigDecimal;

public class BadOperator {
    public static void main(String[] args) {
        BigDecimal total = new BigDecimal("10.00");
        System.out.println(total + 1);
    }
}
```

```text
error: bad operand types for binary operator '+'
```

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

```java throw
import java.math.BigDecimal;

public class ThrowDivide {
    public static void main(String[] args) {
        System.out.println(new BigDecimal("10").divide(new BigDecimal("3")));
    }
}
```

```text
Exception in thread "main" java.lang.ArithmeticException: Non-terminating decimal expansion; no exact representable decimal result.
```

`divide` is the one operation with no exact answer in general, so it refuses rather than guessing.
`Non-terminating decimal expansion; no exact representable decimal result.` is the exception, and the
fix is the three-argument overload: `divide(divisor, scale, roundingMode)`.

Choosing the scale *is* choosing where the money goes. The last solution shows `10.00` divided three
ways at scale 2: three parts of `3.33` sum to `9.99`, and a cent has vanished. That is not a bug to
fix — it is a decision you have to make, and the alternatives (carry the remainder, allocate it to one
part, or use a scale of 4 internally and round only at the boundary) are all defensible. What is not
defensible is not noticing.

### An invalid date is not a `null`

```java throw
import java.time.LocalDate;

public class ThrowBadDate {
    public static void main(String[] args) {
        System.out.println(LocalDate.of(2026, 2, 30));
    }
}
```

```text
Exception in thread "main" java.time.DateTimeException: Invalid date 'FEBRUARY 30'
```

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

```java run
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;

public class Scenario {
    record Line(String sku, int qty, BigDecimal unitPrice) {}

    static final BigDecimal TAX = new BigDecimal("0.20");

    public static void main(String[] args) {
        List<Line> lines = List.of(
                new Line("A-1", 3, new BigDecimal("19.99")),
                new Line("B-7", 1, new BigDecimal("4.05")),
                new Line("C-3", 12, new BigDecimal("0.35")));

        BigDecimal net = BigDecimal.ZERO;
        for (Line l : lines) {
            BigDecimal lineTotal = l.unitPrice().multiply(BigDecimal.valueOf(l.qty()));
            net = net.add(lineTotal);
            System.out.printf("%-4s %3d x %6s = %8s%n", l.sku(), l.qty(), l.unitPrice(), lineTotal);
        }

        BigDecimal tax = net.multiply(TAX).setScale(2, RoundingMode.HALF_UP);
        BigDecimal gross = net.add(tax);

        System.out.println("net    = " + net);
        System.out.println("tax    = " + tax);
        System.out.println("gross  = " + gross);

        LocalDate issued = LocalDate.of(2026, 3, 14);
        LocalDate due = issued.plusDays(30);
        System.out.println("issued = " + issued);
        System.out.println("due    = " + due);
        System.out.println("terms  = " + ChronoUnit.DAYS.between(issued, due) + " days");
    }
}
```

```text
A-1    3 x  19.99 =    59.97
B-7    1 x   4.05 =     4.05
C-3   12 x   0.35 =     4.20
net    = 68.22
tax    = 13.64
gross  = 81.86
issued = 2026-03-14
due    = 2026-04-13
terms  = 30 days
```

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

```java run
import java.math.BigDecimal;
import java.math.RoundingMode;

public class Sol1 {
    static BigDecimal money(String amount) {
        return new BigDecimal(amount).setScale(2, RoundingMode.HALF_UP);
    }

    public static void main(String[] args) {
        BigDecimal unit = money("19.995");
        System.out.println("rounded   = " + unit);
        System.out.println("equals    = " + unit.equals(new BigDecimal("20.00")));
        System.out.println("compareTo = " + (unit.compareTo(new BigDecimal("20.00")) == 0));

        BigDecimal total = unit.multiply(BigDecimal.valueOf(3));
        System.out.println("total     = " + total);

        BigDecimal split = total.divide(BigDecimal.valueOf(3), 2, RoundingMode.HALF_UP);
        System.out.println("split     = " + split);
        System.out.println("scale     = " + split.scale());

        BigDecimal ten = new BigDecimal("10.00");
        BigDecimal third = ten.divide(new BigDecimal("3"), 2, RoundingMode.HALF_UP);
        System.out.println("third     = " + third);
        System.out.println("three     = " + third.multiply(BigDecimal.valueOf(3)));
        System.out.println("lost      = " + ten.subtract(third.multiply(BigDecimal.valueOf(3))));
    }
}
```

```text
rounded   = 20.00
equals    = true
compareTo = true
total     = 60.00
split     = 20.00
scale     = 2
third     = 3.33
three     = 9.99
lost      = 0.01
```

`money(String)` is the single place where a scale and a rounding mode are chosen, and every amount in
the program goes through it. `19.995` becomes `20.00`, and `equals` now agrees with `compareTo`
because both operands were normalised by the same function.

The last four lines are the honest part. `10.00` divided three ways at scale 2 is `3.33`, three of
those is `9.99`, and `lost = 0.01`. A money type that hides this is lying; one that reports it lets
the caller decide whether the cent goes to a rounding account, to the largest line, or to the
customer.

### 2. Never call `now()` inside a rule

```java run
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

public class Sol2 {
    static long daysUntil(LocalDate from, LocalDate deadline) {
        return ChronoUnit.DAYS.between(from, deadline);
    }

    static String status(LocalDate from, LocalDate deadline) {
        long days = daysUntil(from, deadline);
        if (days < 0) {
            return "overdue by " + (-days);
        }
        return days == 0 ? "due today" : "due in " + days;
    }

    public static void main(String[] args) {
        LocalDate issued = LocalDate.of(2026, 3, 14);
        LocalDate[] dates = {
            LocalDate.of(2026, 3, 10),
            LocalDate.of(2026, 3, 14),
            LocalDate.of(2026, 3, 20),
        };
        for (LocalDate d : dates) {
            System.out.printf("%s  %s%n", d, status(issued, d));
        }
        System.out.println("acrossFeb = " + daysUntil(LocalDate.of(2026, 1, 31),
                LocalDate.of(2026, 2, 28)));
    }
}
```

```text
2026-03-10  overdue by 4
2026-03-14  due today
2026-03-20  due in 6
acrossFeb = 28
```

`daysUntil` and `status` take both dates as parameters. There is no `LocalDate.now()` anywhere, so
the behaviour is fully determined by the arguments and the method can be tested on any date —
including the awkward ones.

The three printed rows are the three branches: `overdue by 4`, `due today` and `due in 6`. The
`acrossFeb` line answers `28` for 31 January to 28 February 2026, which is the kind of count a
hand-written month-length table gets wrong in a leap year.

### 3. One formatter per purpose, each with an explicit locale

```java run
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

public class Sol3 {
    static final DateTimeFormatter WIRE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd", Locale.ROOT);
    static final DateTimeFormatter HUMAN =
            DateTimeFormatter.ofPattern("d MMMM yyyy", Locale.US);

    public static void main(String[] args) {
        LocalDate d = LocalDate.of(2026, 3, 14);

        System.out.println("wire      = " + d.format(WIRE));
        System.out.println("human     = " + d.format(HUMAN));
        System.out.println("parsed    = " + LocalDate.parse("2026-03-14", WIRE));
        System.out.println("roundTrip = " + LocalDate.parse(d.format(WIRE), WIRE).equals(d));
        System.out.println("german    = "
                + d.format(DateTimeFormatter.ofPattern("d MMMM yyyy", Locale.GERMAN)));
    }
}
```

```text
wire      = 2026-03-14
human     = 14 March 2026
parsed    = 2026-03-14
roundTrip = true
german    = 14 März 2026
```

Two `static final` formatters: `WIRE` for storage and transport, `HUMAN` for display, both with a
named `Locale`. `Locale.ROOT` on the wire formatter is deliberate — a numeric ISO pattern must not
change because a server was started in a different region.

`roundTrip = true` is the property worth having: anything you format with `WIRE` parses back to the
same date. That property is what makes a wire format safe, and it is cheap to assert.

### 4. A `Period` is calendar time; a `Duration` is exact time

```java run
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.time.temporal.ChronoUnit;

public class Sol4 {
    public static void main(String[] args) {
        LocalDate from = LocalDate.of(2025, 1, 31);
        LocalDate to = LocalDate.of(2025, 3, 1);

        System.out.println("period     = " + Period.between(from, to));
        System.out.println("periodDays = " + Period.between(from, to).getDays());
        System.out.println("exactDays  = " + ChronoUnit.DAYS.between(from, to));

        LocalDateTime a = LocalDateTime.of(2025, 3, 8, 12, 0);
        LocalDateTime b = a.plusDays(1);
        System.out.println("duration   = " + Duration.between(a, b));
        System.out.println("plusPeriod = " + a.plus(Period.ofDays(1)));
        System.out.println("normalised = " + from.plus(Period.between(from, to)));
        System.out.println("roundTrip  = " + from.plus(Period.between(from, to)).equals(to));
    }
}
```

```text
period     = P1M1D
periodDays = 1
exactDays  = 29
duration   = PT24H
plusPeriod = 2025-03-09T12:00
normalised = 2025-03-01
roundTrip  = true
```

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
