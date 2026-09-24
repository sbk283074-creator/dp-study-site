---
chapter: 0
part: 0
title: How to Use This Book
summary: The map, the rules, and the habit that decides whether you finish this book.
minutes: 8
tags: [study plan, setup, expectations]
---

Most programming books get abandoned around chapter four, right when the reader stops typing
along and starts only reading. This book is built to make that harder. Every chapter gives you
something to run, break, and fix. Here is how to use it so it actually works.

## The three rules

**Rule 1 — Type every example. Do not copy-paste.** Your fingers build muscle memory your eyes
cannot. When you copy-paste, you get the illusion of understanding without the skill. Type it,
run it, then change one thing and predict what happens before you run it again.

**Rule 2 — Break things on purpose.** After an example works, delete a line, pass the wrong type,
rename a variable. Read the error. Python's tracebacks are unusually good teachers, and learning
to read them is a skill you will use every single day of your career.

**Rule 3 — Do the exercises before reading the solutions.** The solution is at the bottom of each
chapter for a reason. Struggling for ten minutes builds a mental hook that reading for ten
seconds never will. If you are truly stuck after a real attempt, read the solution, then close
it and write it again from memory.

## The shape of the book

| Part | Chapters | What you become able to do |
|---|---|---|
| I · Foundations | 01–09 | Write real scripts: read files, transform data, handle mistakes |
| II · Leveling Up | 10–17 | Write code other people can maintain: classes, tests, type hints |
| III · Real-World Python | 18–23 | Consume APIs, query databases, automate work, ship a CLI product |
| IV · Track A | 24–30 | Build and deploy a full-stack web application with FastAPI |
| V · Track B | 31–36 | Build and package a complete game with Pygame |
| VI · Appendices | 37–38 | Recipes and a bank of practice problems |
| VII · How Python Actually Works | 39–43 | See the interpreter, the object model, the memory rules and the descriptor protocol under the features you already use |
| VIII · Algorithms & Complexity | 44–49 | Reason about what code costs before you run it, and choose a data structure on evidence |
| XII · Where Next | 62 | Turn the skills into evidence, and choose what to learn next |

Parts IX–XI are being written now: Security, Architecture & Patterns, and Performance & Data at
Scale. They fill chapters 50–61, and they sit deliberately *after* the applied tracks — they are what
turns "I can build things" into "I can choose what to build". Each one appears in this table once its
first chapter ships.

Parts I–III are mandatory and linear. After that the book forks: Track A is web development,
Track B is game development. You can do either one, or do both — Track A and Track B do not
depend on each other, only on Parts I–III.

:::tip How long this takes
At one chapter per session, roughly an hour each including exercises, this is a two-to-three
month journey if you go steadily. Going slower is completely fine. Going faster by skipping
exercises is not — it just moves the wall later.
:::

## What you need

- A computer running macOS, Windows, or Linux (Chapter 1 walks through the setup).
- About an hour per chapter, and the discipline to keep a single folder for your work.
- No prior programming experience for Part I. If you already know another language, skim
  Chapters 1–7 but still do the exercises — Python's idioms are different enough that
  assumptions will bite you.

## How to organise your work

Make one folder now and use it for the entire book:

```bash
mkdir -p ~/python-mastery
cd ~/python-mastery
```

Inside it, create one subfolder per chapter (`01`, `02`, …). Every snippet you type goes into
that folder as a real file with a real name. At the end of the book this folder is your
portfolio, and it is also the fastest way to find that thing you wrote three weeks ago.

:::scenario You have 20 minutes, not an hour
Real life rarely hands you a clean hour. You open the book, and you only have time for a
fraction of a chapter.
:::

:::solution Read-then-type beats read-only
Use the 20 minutes like this: read one section (5 min), type and run its examples (10 min),
then write yourself a one-line note about what surprised you (5 min). Do not start a new
section you cannot finish — a half-read section evaporates, but a finished one compounds. The
book is designed with small sections precisely so that a 20-minute session always lands on a
clean boundary.
:::

## Progress tracking

This site remembers which chapters you have completed (the "Mark chapter complete" button at
the bottom of every page, stored in your browser). Exercise checkboxes are saved too. Use it —
visible progress is a real motivator, and on the days you feel stuck it is evidence that you
are not.

Keyboard shortcuts: `←` and `→` move between chapters, `/` jumps to search.

:::pitfall Collecting resources instead of finishing one
The failure mode that ends most self-taught attempts is not difficulty. It is opening a second
book, a third course, and a fourth video series the first time a topic feels hard — because
starting something new feels like progress and being confused does not. It is not progress. You
now have four half-finished introductions and no working programs.

When a chapter here is hard, the fix is to slow down inside it, not to leave it: re-read the
section, type the example again from scratch, and break it deliberately to see what happens. If
you still cannot make it work, ask about that specific line and move on — a chapter you finished
badly is worth more than three you abandoned cleanly.
:::

## Counted: predictions against runs, and a tracker against the book

Two claims in this chapter are the ones that decide how you should read the rest
of it: that a prediction is not evidence, and that a progress list is not a
record of the book.

### Six of eight

Eight things a reader might predict about Python, each one checked by running it.
The count is of predictions that turn out to be wrong.

```python run
"""Chapter 00 -- the reason this book runs every example.

Eight things a reader might predict about Python, checked rather than argued.
The count is of predictions that turn out to be wrong.
"""

# (what you would guess, the topic, and the expression that decides it)
CLAIMS = [
    ("0.1 + 0.2 == 0.3", True, "floating point", lambda: 0.1 + 0.2 == 0.3),
    ("sum([0.1] * 10) == 1.0", True, "floating point", lambda: sum([0.1] * 10) == 1.0),
    ("bool('False')", False, "truthiness", lambda: bool("False")),
    ("bool([])", False, "truthiness", lambda: bool([])),
    ("round(2.5) == 3", True, "rounding", lambda: round(2.5) == 3),
    ("-7 // 2 == -3", True, "integer division", lambda: -7 // 2 == -3),
    ("'abc'.find('d') == 0", True, "lookup", lambda: "abc".find("d") == 0),
    ("[1, 2] == (1, 2)", True, "equality", lambda: [1, 2] == (1, 2)),
]

rows = []
for expression, predicted, topic, run in CLAIMS:
    actual = run()
    rows.append((expression, predicted, actual, topic,
                 "right" if actual == predicted else "wrong"))

right = sum(1 for _, _, _, _, verdict in rows if verdict == "right")
wrong = len(rows) - right

topics = sorted({topic for _, _, _, topic, _ in rows})
per_topic = [(topic, sum(1 for _, _, _, t, v in rows if t == topic and v == "wrong"),
              sum(1 for _, _, _, t, _ in rows if t == topic))
             for topic in topics]

print(f"{len(CLAIMS)} predictions about Python, checked by running them")
print()
print(f"{'expression':<26}{'guessed':>9}{'actual':>8}{'topic':>18}{'verdict':>9}")
print("-" * 70)
for expression, predicted, actual, topic, verdict in rows:
    print(f"{expression:<26}{str(predicted):>9}{str(actual):>8}{topic:>18}"
          f"{verdict:>9}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'predictions made':<46}{len(rows):>8}")
print(f"{'predictions that were right':<46}{right:>8}")
print(f"{'predictions that were wrong':<46}{wrong:>8}")
print(f"{'topics covered':<46}{len(topics):>8}")
for topic, bad, total in per_topic:
    print(f"{'wrong in ' + topic:<46}{bad:>8}")
print(f"{'topics where every prediction was wrong':<46}"
      f"{sum(1 for _, bad, total in per_topic if bad == total):>8}")

print()
print(f"Six of these eight are wrong, and the two that are right are not the two")
print("that look safe. `bool([])` is false, which everyone knows, and")
print("`sum([0.1] * 10) == 1.0` is *true* -- the rounding errors happen to cancel")
print("over ten additions, so the one prediction here that looks like a trap is")
print("the one that is fine, and `0.1 + 0.2 == 0.3` two rows above it is not.")
print()
print("That is the whole argument for this book's one rule, and it is stronger")
print("than 'people are bad at floating point'. A prediction is not a fact about")
print("Python; it is a fact about you, and the two agree often enough that the")
print("difference stays invisible until something breaks. Reading the output of a")
print("program you ran takes a second. Believing you know what it prints costs an")
print("afternoon, and the afternoon arrives months later in code you no longer")
print("remember writing.")
print()
print("So every example in this book carries its real output, and the output is")
print("produced by running the example rather than by writing down what it ought")
print("to be. The habit to take from here is smaller than the book: when a result")
print("surprises you, run the four-line version before you argue with it.")
```

```text
8 predictions about Python, checked by running them

expression                  guessed  actual             topic  verdict
----------------------------------------------------------------------
0.1 + 0.2 == 0.3               True   False    floating point    wrong
sum([0.1] * 10) == 1.0         True    True    floating point    right
bool('False')                 False    True        truthiness    wrong
bool([])                      False   False        truthiness    right
round(2.5) == 3                True   False          rounding    wrong
-7 // 2 == -3                  True   False  integer division    wrong
'abc'.find('d') == 0           True   False            lookup    wrong
[1, 2] == (1, 2)               True   False          equality    wrong

what is counted                                  count
------------------------------------------------------
predictions made                                     8
predictions that were right                          2
predictions that were wrong                          6
topics covered                                       6
wrong in equality                                    1
wrong in floating point                              1
wrong in integer division                            1
wrong in lookup                                      1
wrong in rounding                                    1
wrong in truthiness                                  1
topics where every prediction was wrong              4

Six of these eight are wrong, and the two that are right are not the two
that look safe. `bool([])` is false, which everyone knows, and
`sum([0.1] * 10) == 1.0` is *true* -- the rounding errors happen to cancel
over ten additions, so the one prediction here that looks like a trap is
the one that is fine, and `0.1 + 0.2 == 0.3` two rows above it is not.

That is the whole argument for this book's one rule, and it is stronger
than 'people are bad at floating point'. A prediction is not a fact about
Python; it is a fact about you, and the two agree often enough that the
difference stays invisible until something breaks. Reading the output of a
program you ran takes a second. Believing you know what it prints costs an
afternoon, and the afternoon arrives months later in code you no longer
remember writing.

So every example in this book carries its real output, and the output is
produced by running the example rather than by writing down what it ought
to be. The habit to take from here is smaller than the book: when a result
surprises you, run the four-line version before you argue with it.
```

Six of the eight are wrong, and the two that are right are not the two that look
safe. `bool([])` is false, which everyone knows. And `sum([0.1] * 10) == 1.0` is
*true* — the rounding errors happen to cancel over ten additions — so the
prediction that looks most like a trap is the one that is fine, while
`0.1 + 0.2 == 0.3` two rows above it is not.

That is the argument for this book's rule, and it is stronger than "people are
bad at floating point". A prediction is not a fact about Python; it is a fact
about you, and the two agree often enough that the difference stays invisible
until something breaks. Reading the output of a program you ran takes a second.
Believing you know what it prints costs an afternoon, and the afternoon arrives
months later in code you no longer remember writing.

So every example in this book carries its real output, produced by running the
example rather than by writing down what it ought to be. The habit to take from
here is smaller than the book: when a result surprises you, run the four-line
version before you argue with it.

### The chapters with no state

A tracker for the first twelve chapters, kept by hand. The count is of chapters
in each state, and of the chapters that have no state at all.

```python run
"""Chapter 00 -- a progress list is only useful if you count what is missing.

A tracker for the first twelve chapters, kept by hand. The count is of chapters
in each state, and of the chapters that have no state at all.
"""

CHAPTERS = [
    "01-getting-started", "02-variables-and-types", "03-strings-and-formatting",
    "04-control-flow", "05-collections", "06-functions", "07-comprehensions",
    "08-files-and-paths", "09-errors-and-exceptions", "10-modules-and-venv",
    "11-testing-and-debugging", "12-oop-i",
]

# The state of each chapter, as it was written down after each session. Three
# chapters are missing because they were added to the book after the list was
# started and nobody went back to it.
STATUS = {
    "01-getting-started": "done",
    "02-variables-and-types": "done",
    "03-strings-and-formatting": "done",
    "04-control-flow": "done",
    "05-collections": "in progress",
    "06-functions": "in progress",
    "07-comprehensions": "in progress",
    "08-files-and-paths": "untouched",
    "09-errors-and-exceptions": "untouched",
}

STATES = ["done", "in progress", "untouched"]

missing = [name for name in CHAPTERS if name not in STATUS]
unknown = sorted({state for state in STATUS.values()} - set(STATES))

print(f"{len(CHAPTERS)} chapters, {len(STATUS)} of them written down")
print()
print(f"{'state':<20}{'chapters':>10}")
print("-" * 30)
for state in STATES:
    print(f"{state:<20}{sum(1 for v in STATUS.values() if v == state):>10}")
print(f"{'(no state)':<20}{len(missing):>10}")

print()
print(f"{'what is counted':<46}{'count':>8}")
print("-" * 54)
print(f"{'chapters in the book':<46}{len(CHAPTERS):>8}")
print(f"{'chapters with a state':<46}{len(STATUS):>8}")
print(f"{'chapters with no state':<46}{len(missing):>8}")
print(f"{'distinct states used':<46}{len(set(STATUS.values())):>8}")
print(f"{'states the tracker defines':<46}{len(STATES):>8}")
print(f"{'states used but not defined':<46}{len(unknown):>8}")
for state in STATES:
    print(f"{'chapters marked ' + state:<46}"
          f"{sum(1 for v in STATUS.values() if v == state):>8}")
print(f"{'share of the book with a state':<46}"
      f"{round(100 * len(STATUS) / len(CHAPTERS)):>7}%")

print()
print("The last line of the table is the one a hand-kept tracker never shows you,")
print("and it is the only number that matters. Three chapters have no state at")
print("all -- not 'untouched', which is a decision, but absent, which is not.")
print("They were added to the book after the list was started, and a list cannot")
print("tell you about a row that was never written.")
print()
print("So the useful measurement is not how many chapters are done. It is the")
print("difference between the number of chapters that exist and the number the")
print("tracker knows about, and it only works if both numbers come from somewhere")
print("other than the tracker. A list that counts itself is always complete.")
print()
print("That is the same discipline as the examples in this book, applied to your")
print("own work. Keep the list next to the thing it describes rather than in place")
print("of it, count the gap in both directions, and treat a chapter that is")
print("missing as more interesting than one that is late -- being late is a")
print("schedule, and being missing is a blind spot.")
```

```text
12 chapters, 9 of them written down

state                 chapters
------------------------------
done                         4
in progress                  3
untouched                    2
(no state)                   3

what is counted                                  count
------------------------------------------------------
chapters in the book                                12
chapters with a state                                9
chapters with no state                               3
distinct states used                                 3
states the tracker defines                           3
states used but not defined                          0
chapters marked done                                 4
chapters marked in progress                          3
chapters marked untouched                            2
share of the book with a state                     75%

The last line of the table is the one a hand-kept tracker never shows you,
and it is the only number that matters. Three chapters have no state at
all -- not 'untouched', which is a decision, but absent, which is not.
They were added to the book after the list was started, and a list cannot
tell you about a row that was never written.

So the useful measurement is not how many chapters are done. It is the
difference between the number of chapters that exist and the number the
tracker knows about, and it only works if both numbers come from somewhere
other than the tracker. A list that counts itself is always complete.

That is the same discipline as the examples in this book, applied to your
own work. Keep the list next to the thing it describes rather than in place
of it, count the gap in both directions, and treat a chapter that is
missing as more interesting than one that is late -- being late is a
schedule, and being missing is a blind spot.
```

The third row of the counts is the one a hand-kept tracker never shows you, and
it is the only number that matters. Three chapters have no state — not
"untouched", which is a decision, but absent, which is not. They were added to
the book after the list was started, and a list cannot tell you about a row that
was never written.

So the useful measurement is not how many chapters are done. It is the
difference between the number of chapters that exist and the number the tracker
knows about, and it only works if both numbers come from somewhere other than
the tracker. A list that counts itself is always complete.

That is the same discipline as the examples in this book, applied to your own
work. Keep the list next to the thing it describes rather than in place of it,
count the gap in both directions, and treat a chapter that is missing as more
interesting than one that is late — being late is a schedule, and being missing
is a blind spot.

## Key takeaways

- Type the code; never copy-paste it. Muscle memory is the point.
- Break working code on purpose and read the traceback. Errors are the curriculum.
- Attempt every exercise before opening the solutions section.
- Parts I–III are linear; Tracks A and B are independent choices afterwards.
- Keep one `~/python-mastery` folder with one subfolder per chapter.
- Finishing a chapter badly beats abandoning three cleanly — the cost is the topic you skipped, not the time you spent.

## Practice

- [ ] Create `~/python-mastery` and a subfolder named `00` inside it.
- [ ] Write a file called `notes.md` where you will record, after each chapter, the one thing
      that surprised you most.
- [ ] Decide right now which track you want first: Track A (web) or Track B (games). Write it
      at the top of `notes.md`.
- [ ] Schedule your next three sessions in a calendar. Vague intentions lose to booked time.

## Solutions

:::solution Exercise 1
```bash
mkdir -p ~/python-mastery/00
cd ~/python-mastery/00
```
`mkdir -p` creates the parent directories if they are missing and does nothing (no error) if
they already exist, which makes it safe to run repeatedly.
:::

:::solution Exercise 2
There is no code for this one — the point is the habit. Keep `notes.md` at the root of
`~/python-mastery`, not inside a chapter folder, so it is always easy to find:

```
~/python-mastery/
├── notes.md
├── 00/
├── 01/
└── 02/
```
:::

:::solution Exercise 3
Either answer is correct. If you want to build things people use over a network, pick Track A.
If you want to build things that are fun to play and run locally, pick Track B. You can always
do the other one afterwards — they share the same Parts I–III foundation.
:::

:::solution Exercise 4
Pick recurring slots rather than random ones. Three fixed 45-minute blocks beat one mythical
four-hour Sunday. Put the chapter number in the event title so you never waste time deciding
what to work on.
:::
