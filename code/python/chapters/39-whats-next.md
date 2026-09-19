---
chapter: 39
part: 6
title: "What to Learn Next"
summary: Take an honest inventory of what you can now actually build, then pick one specialisation and one deep project to carry into the next ninety days. A roadmap for direction, portfolio, open source, interviews, and the month right after the last page.
minutes: 25
tags: [roadmap, portfolio, open source, career]
---

Finishing a book creates a strange gap: you have more ability than you can feel, and less than
you can now see. Both halves of that sentence are normal, and the second half is the useful one —
you can finally tell the difference between "I don't know how to do this" and "I don't know how
to do this *yet*". This last chapter is not a pep talk. It is an inventory, a set of forks in the
road, and a plan for the next thirty days that turns the skills you have into evidence someone
else can look at.

## What you can now claim

Be precise here, because vague claims collapse under the first technical question. These are
things you can honestly say you can do, having finished Parts I–III and at least one track:

- Write Python scripts that read real files with `pathlib`, parse CSV and JSON, and fail loudly
  instead of silently corrupting data.
- Model a problem with dataclasses and classes, and choose between them on purpose.
- Use dicts and sets deliberately — membership tests, grouping, deduplication, counting — and
  explain why a dict lookup is O(1) and what that costs you in memory.
- Reach for generators and comprehensions where they make code clearer, and know when a plain
  `for` loop is the honest answer.
- Handle errors with `try`/`except`/`finally`, define your own exception types, and log instead
  of `print` when the code outlives your terminal.
- Write unit tests with `pytest`, including fixtures and parametrized cases, and run them before
  you ship anything.
- Consume an HTTP API with `httpx`, handle timeouts, retries, and pagination without guessing.
- Model and query a relational database with SQL, then do the same through SQLAlchemy 2.x, and
  explain what the ORM generated and why it sometimes generated something slow.
- Build a command-line tool that takes arguments, reads config, and does one job well (TaskForge).
- Package a project, pin its dependencies in a virtual environment, and put it under Git with a
  history a colleague could read.
- Either: build, test, and deploy a multi-user web application with FastAPI, Jinja2 and HTMX,
  running in Docker against Postgres (StudyHub) — or: build, profile, package, and hand to a
  friend a complete game with input, state, collision, and procedural content (Neon Dungeon).

What you cannot yet claim: architecture at scale, performance work under real load, mentoring,
or on-call judgement. Nobody expects those from someone at your stage. The order in which you
acquire the next layer matters more than the speed.

## Pick a direction

| Direction | What the day-to-day is really like | Core libraries to learn next | Time to useful / employable |
|---|---|---|---|
| Backend & web | Reading other people's endpoints, writing new ones, arguing about schema migrations, fixing things that broke in staging | FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, Celery or RQ, pytest, Docker | 2–4 months to be genuinely useful; 6–9 to be hired with no hand-holding |
| Data engineering & analytics | Moving data between systems that disagree, writing jobs that must be idempotent, debugging yesterday's 3 a.m. failure | pandas, Polars, PyArrow, DuckDB, SQLAlchemy, Prefect or Dagster, dbt | 3–5 months; SQL depth matters more than Python cleverness here |
| ML & AI | Less modelling than you imagine; mostly data cleaning, evaluation, and pipeline plumbing | numpy, pandas, scikit-learn, PyTorch, Hugging Face `transformers`, MLflow | 6–12 months, and you will lean on maths you may need to backfill |
| Automation & DevOps/SRE | Replacing manual steps with scripts, then owning the alert when the script is wrong | subprocess, Fabric, Ansible, Docker, Kubernetes client, `boto3`, pytest | 2–4 months if you already like systems work |
| Testing & quality | Reading code you did not write, finding its seams, and defending users from regressions | pytest (deep), Hypothesis, Playwright, tox/nox, coverage, mocking | 1–3 months to add value; a genuinely under-served niche |
| Game development | Long stretches of refactoring engine code, short bursts of visible fun, constant profiling | Pygame, Pyglet or Arcade, numpy for grids, `pymunk`, Pydantic for save data | 3–6 months to a shippable small game; portfolio-driven, not interview-driven |
| Security | Reading protocols and code side by side, writing tools that prove a weakness, writing reports people act on | `requests`/`httpx`, Scapy, `cryptography`, `bandit`, `sqlmap` internals, pytest | 6–12 months; usually entered after a year or two elsewhere |

Choose the one whose *daily work* you would do on a Saturday, unpaid. Not the one with the best
salary chart, and not the one your feed says is hot. Every row above contains weeks of tedious
maintenance for every week of visible progress; the only thing that carries you through the
tedious part is liking the subject. If two rows tie, pick the one where you already have a
problem of your own you want to solve — an itch beats a plan.

:::pitfall Collecting roadmaps instead of walking one
Reading five "2026 Python roadmap" posts feels like progress and produces nothing. Roadmaps are
written for everyone, so they are written for no one. Pick a row today, write it at the top of
your notes, and do not revisit the decision for ninety days.
:::

## Build a portfolio that gets read

A portfolio is not a list of repositories; it is a small number of artefacts someone can run.
Here are six, each with the twist that makes it worth a second look:

1. **TaskForge, plus a public REST API and a generated OpenAPI client SDK.** The CLI is the
   product; the SDK is the proof you understand contract-first design. Ship the generated client
   to a package index.
2. **StudyHub, plus a real deployment with a URL, a database migration history, and a public
   status page.** Anyone can run an app locally. Very few juniors can show a thing that survived
   contact with the internet.
3. **Neon Dungeon, plus a seeded daily run and a public leaderboard.** A daily seed turns a game
   into a shared event, and the leaderboard forces you to handle untrusted input, validation,
   and cheating.
4. **A data pipeline: fetch a public dataset nightly, land it in DuckDB or Postgres, and publish
   one chart.** Include the failure case — what happens when the upstream API is down — because
   that is the part interviewers actually ask about.
5. **A test-quality project: take a small open source library with weak coverage and raise it,
   using Hypothesis to find at least one real bug.** A pull request that deletes a bug beats any
   demo app.
6. **A tool you personally use every week.** Smallest scope, strongest signal. It proves you can
   notice friction and remove it.

### A README that isn't filler

Four sections, in this order, and nothing else at the top:

- **The problem.** Two or three sentences, in the words of the person who has it. Not "a
  task manager built with FastAPI" but "my team's standup notes were scattered across three
  tools, so I built one place to paste them and get a digest".
- **The decisions.** Three to five bullet points: why this database, why this framework, what
  you rejected and why. This is the section that separates you from a tutorial clone.
- **How to run it.** Copy-pasteable commands from a clean clone, including the environment
  variable names. If it takes more than `git clone`, one `make` target, and one `docker compose
  up`, simplify the project.
- **What I'd do differently.** Honest, specific, and technical: "I put business logic in the
  routers; I'd move it into a service layer and test it without HTTP". Nobody expects a perfect
  project. Everybody trusts someone who can see their own seams.

One deep project beats ten todo apps. A single repository with migrations, tests, CI, a
deployment, and a written record of hard decisions tells a reader how you work under pressure.
Ten half-finished demos tell them how you start.

## Contributing to open source

First, stop looking for "good first issues" as a category and start looking for a *maintainer
behaviour* signal. A genuinely good first issue has: a maintainer who replied to someone in the
last two weeks, a description that names the expected behaviour, and a scope you can finish in
one sitting. If the last activity is eight months old or the thread contains a volunteer who
submitted a PR that was never reviewed, move on — you will be waiting, not learning.

To read a foreign codebase efficiently, do not start at `main.py`. Start at the tests: they show
you the public surface, the intended edge cases, and the naming conventions faster than any
README. Then pick one request — one HTTP call, one click, one command — and follow it end to end,
writing down each file you pass through. Two hours of that teaches you the architecture; two days
of reading files alphabetically teaches you nothing.

What makes a PR easy to merge: it does one thing, it includes a test that fails before your fix,
it matches the surrounding style even when you would have written it differently, and the
description explains the *why* in three sentences. Also: fix the boring thing nobody wants —
docs, error messages, type hints, a flaky test. Maintainers remember the person who made their
week quieter.

## Reading other people's code

The method, done weekly for an hour:

1. Pick one module of 300 lines or fewer. Not a whole framework.
2. Read it twice without running anything: once for structure, once for the data flow.
3. Then run it under a debugger or add `breakpoint()` at one interesting line and step through.
4. Write a 100-word summary in your notes, including one thing you would have done differently.
5. Optional, and highly effective: reimplement one function from memory the next day.

Good targets, roughly in order of approachability: the standard library's `pathlib` (a master
class in making an awkward API pleasant) and `dataclasses` (metaprogramming that reads like
plain code); [httpx](https://github.com/encode/httpx) for clean, typed, modern Python; and
[Rich](https://github.com/Textualize/rich) for how to build a large library out of small,
testable pieces. Flask's early releases are worth a look too — a few hundred lines that explain
what a framework actually *is*.

## Interview preparation

At junior and mid level, interviews are mostly a search for three things: can you write working
code while someone watches, do you understand what your code does to memory and time, and are
you tolerable to work with. Expect:

- One or two small live-coding exercises (strings, dicts, two-pointer, "make this test pass").
- Conceptual questions, usually five minutes each: `dict`/`set` internals and hashability,
  mutability and why `list.sort()` returns `None`, generators versus lists, the GIL and what it
  does and does not affect, decorators and closures, `*args`/`**kwargs`, and SQL versus ORM —
  including "show me the query you think this ORM call produced".
- One debugging or refactoring round: here is ugly code, improve it and explain your changes.
- One behavioural conversation. Have two real stories ready: a time you were wrong, and a time
  you disagreed with someone.

Practise out loud. Say your reasoning while you type, in complete sentences, to an empty room or
a rubber duck. The gap between "I can do this" and "I can do this while narrating it" is where
most failed interviews happen. Record yourself once; it is uncomfortable and it works.

From this book, the topics that come up most often are dicts and sets, mutability, generators and
iteration, the GIL, decorators, and the SQL-versus-ORM boundary. If you revise only five things,
revise those.

## Staying sharp

Deliberate practice means working at the edge of what you can currently do, not repeating what
you can already do well. Concretely: pick the task you would normally avoid, do it badly, then do
it again after reading how someone else did it. Ten hours of that beats a hundred hours of
comfortable repetition.

Write about what you learn. A 200-word note published anywhere — a repo README, a blog, a gist —
forces you to find out whether you actually understand it, and it becomes the artefact a hiring
manager finds at 11 p.m. Teaching is a debugging tool for your own mental model.

Reading list, in order. Start with the official docs, which are unusually good: the
[Python Tutorial](https://docs.python.org/3/tutorial/) end to end, then the
[Standard Library Reference](https://docs.python.org/3/library/) as a reference you skim weekly,
then the [HOWTOs](https://docs.python.org/3/howto/) — the logging, sorting, and descriptor guides
repay an hour each. Then books: *Fluent Python* (Luciano Ramalho) for the language's real depth,
*Effective Python* (Brett Slatkin) for 90 specific habits, *Python Distilled* (David Beazley) if
you prefer concise, and *Architecture Patterns with Python* (Percival & Gregory) once you are
writing services that are getting hard to change.

## A 30-day plan

Week 1 — Close the loop:

- [ ] Re-read your chapter notes and write a one-page list of the ten things you can now do.
- [ ] Pick one direction from the table above and write it at the top of `notes.md`.
- [ ] Choose one portfolio project and write its problem statement in a README before any code.

Week 2 — Depth:

- [ ] Implement the smallest end-to-end slice of that project (one feature, real data, no mocks).
- [ ] Add `pytest` tests for the core logic, including one failure case you actually hit.
- [ ] Push it to a public repository with a real commit history and a `.gitignore`.

Week 3 — Contact with reality:

- [ ] Deploy it, or package it so a friend can run it, and have that friend run it.
- [ ] Write the "what I'd do differently" section of the README honestly.
- [ ] Read one module of `pathlib` or `httpx` and write your 100-word summary.

Week 4 — Outward:

- [ ] Find one open source issue that is small, recent, and has an active maintainer.
- [ ] Comment, then submit a PR that does one thing and includes a test.
- [ ] Do two live-coding problems out loud, recorded.
- [ ] Book your next thirty days: one project, one contribution, one public write-up.

:::scenario Two weeks in, you feel like you still know nothing
You finished the book, started a project of your own, and now everything takes four times longer
than it did when you were following along. You Google constantly. You look at your own code from
last week and it looks like someone else wrote it — badly. The obvious conclusion is that the
book did not work and you are not cut out for this.
:::

:::solution Name it: the competence dip
This is a well-documented phase, and it has a cause. While you were following a book, the
problem, the structure, and the "done" condition were all supplied. Now you supply all three, and
you are doing two hard things at once: building the thing and deciding what the thing should be.
On top of that, your standards rose faster than your skills — you can now see the gap, which is
exactly what you could not do at chapter one. Seeing more of the mountain is not evidence that
you are lower down it.

What to do about it:

- Shrink the unit of work until it is embarrassing. Not "build the API", but "make `GET /health`
  return 200". Finish something today.
- Keep a log of things that confused you and cost more than thirty minutes. Review it monthly —
  most entries will look trivial in six weeks, and that list is your real progress bar.
- Compare against your own past work, never against someone with five years of context. Open an
  early chapter folder and read what you wrote.
- Separate the two skills. Spend one session on writing new code and a different session on
  deciding what to build. Mixing them is what makes you feel slow.
- Ask for a review earlier than feels comfortable. Twenty minutes of someone else's eyes saves a
  week of private doubt.

The dip ends, and it ends from finishing small things, not from reading more.
:::

## Key takeaways

- Inventory your skills in specific, checkable claims: files, tests, HTTP, SQL and ORM, packaging,
  and either a deployed web app or a shipped game.
- Choose a specialisation by the daily work you would do unpaid, and commit to it for ninety days.
- One deep project with migrations, tests, CI, a deployment, and honest README decisions beats ten
  demo apps.
- A good first open source issue is small, recent, and has a maintainer who answered someone
  within the last two weeks.
- Read foreign code by starting at the tests and following one request end to end.
- Interviews at your level test dicts and sets, mutability, generators, the GIL, decorators,
  SQL versus ORM, and your ability to think out loud while typing.
- Practise at the edge of your ability, write down what you learn, and treat the official docs as
  the first book, not the last resort.
- The competence dip two weeks after finishing is the expected cost of having better taste. Finish
  something small today; that is the way out.
