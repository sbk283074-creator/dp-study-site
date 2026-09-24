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

<!--BLOCK:predicted_vs_run-->

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

<!--BLOCK:progress_counts-->

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
