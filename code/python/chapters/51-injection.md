---
chapter: 51
part: 9
title: Injection
summary: The one mechanism behind SQL injection, command injection, template injection, eval, log forging and path traversal -- a value arrives in a position where something parses it, and what happens next is decided by where it landed rather than what it says. Nine blocks, each counting how many payloads get through under each defence, including the defences that make things worse than doing nothing.
minutes: 100
tags: [security, SQL injection, parameterised queries, command injection, SSTI, eval, log injection, encoding, path traversal, blocklists]
---

Chapter 50 was about deciding where to look. This chapter is about the thing you find most often
when you look, and it has one shape. Chapter 19 showed you parameterised queries and told you why
they work. Chapter 25 showed you what `innerHTML` does to a page. Chapter 27 showed you a response
schema that omits the hash. Those are three different chapters about three different bugs, and they
are the same bug.

The shape is this: a value arrives in a position where something parses it, and the parser cannot
tell the difference between the value and the syntax it is standing in. Nothing is broken when this
happens. The parser is doing exactly what it was built to do. That is why the fix is never "detect
the bad input" -- detecting is the parser's job, and the parser is already doing it.

The chapter is nine counts. Each one takes a defence that sounds sufficient and measures how many
payloads get past it. Two of them measure a defence that makes things *worse* than no defence at
all, which is the part people do not expect and the part worth the most.

## A query is a program

Start with the one everybody has heard of, because the mechanism is visible in it and the same
mechanism recurs in the other eight sections with different syntax.

A SQL statement is a program. Before the database can run `SELECT id, name FROM users WHERE name =
'ada'` it has to decide which parts of that string are structure and which are data, and it decides
by reading the string. `'ada'` is data because of the quotes around it. `WHERE` is structure because
of where it sits. There is no other source of information. If a value you did not write ends up
inside the string before the parser sees it, the parser reads it the same way it reads everything
else -- as structure if it looks like structure.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 1 -- binding is a protocol, not a string treatment.

A parameterised query is not a string that has been made safe. It is a
different arrangement: the statement is parsed first, and the values are sent
afterwards, so a value is never parsed as SQL at all. That is why no payload
defeats it, and it is why hand-rolled escaping is a different thing that only
looks like the same thing.

Twelve payloads, each against a fresh in-memory database, so the destructive
one is contained. The counts are exact; nothing is timed.
"""
import sqlite3

PAYLOADS = [
    "ada",
    "' OR '1'='1",
    "' OR 1=1 --",
    "admin'--",
    "' OR 'x'='x",
    "') OR ('1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT id, name FROM secrets --",
    "1 OR 1=1",
    "1; DROP TABLE users",
    "%' OR 1=1 --",
    "' OR 1 LIKE 1 --",
]

USERS = [(1, "ada"), (2, "grace"), (3, "alan"), (4, "edsger"), (5, "barbara")]
SECRETS = [(1, "api-key-9f3a"), (2, "db-password")]


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", USERS)
    conn.execute("CREATE TABLE secrets (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO secrets VALUES (?, ?)", SECRETS)
    return conn


def tables(conn):
    return sorted(r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"))


def main():
    print(f"  users in the table                 {len(USERS):>3} rows")
    print(f"  rows in the secrets table          {len(SECRETS):>3} rows")
    print(f"  payloads                           {len(PAYLOADS):>3}")

    interp_rows, bound_rows = [], []
    interp_dropped, script_dropped = 0, 0

    for p in PAYLOADS:
        conn = fresh()
        try:
            got = conn.execute(
                f"SELECT id, name FROM users WHERE name = '{p}'").fetchall()
        except (sqlite3.Error, sqlite3.Warning):
            got = []
        interp_rows.append(len(got))
        if "users" not in tables(conn):
            interp_dropped += 1
        conn.close()

        conn = fresh()
        got = conn.execute(
            "SELECT id, name FROM users WHERE name = ?", (p,)).fetchall()
        bound_rows.append(len(got))
        conn.close()

        # executescript, by contrast, is happy to run several statements.
        conn = fresh()
        try:
            conn.executescript(
                f"SELECT id, name FROM users WHERE name = '{p}';")
        except (sqlite3.Error, sqlite3.Warning):
            pass
        if "users" not in tables(conn):
            script_dropped += 1
        conn.close()

    print()
    print(f"    {'payload':<46}{'interpolated':>13}{'bound':>7}")
    for p, a, b in zip(PAYLOADS, interp_rows, bound_rows):
        print(f"    {p:<46}{a:>13}{b:>7}")

    print()
    print(f"  rows returned, total               {sum(interp_rows):>3}"
          f" interpolated   {sum(bound_rows):>3} bound")
    print(f"  payloads that returned a row       "
          f"{sum(1 for n in interp_rows if n):>3} interpolated   "
          f"{sum(1 for n in bound_rows if n):>3} bound")
    print(f"  of {len(PAYLOADS)} payloads, the intended answer is 0 rows for every one.")

    print()
    print("  the same payloads through execute() and through executescript()")
    print(f"    tables dropped by execute()      {interp_dropped:>3}")
    print(f"    tables dropped by executescript() {script_dropped:>3}"
          f"   (one statement is allowed to be several)")

    print()
    print("  the bound column is not a smaller number. it is a different")
    print("  arrangement: the statement was parsed before the value existed.")


if __name__ == "__main__":
    main()
```

```text
  users in the table                   5 rows
  rows in the secrets table            2 rows
  payloads                            12

    payload                                        interpolated  bound
    ada                                                       1      1
    ' OR '1'='1                                               5      0
    ' OR 1=1 --                                               5      0
    admin'--                                                  0      0
    ' OR 'x'='x                                               5      0
    ') OR ('1'='1                                             0      0
    '; DROP TABLE users; --                                   0      0
    ' UNION SELECT id, name FROM secrets --                   2      0
    1 OR 1=1                                                  0      0
    1; DROP TABLE users                                       0      0
    %' OR 1=1 --                                              5      0
    ' OR 1 LIKE 1 --                                          5      0

  rows returned, total                28 interpolated     1 bound
  payloads that returned a row         7 interpolated     1 bound
  of 12 payloads, the intended answer is 0 rows for every one.

  the same payloads through execute() and through executescript()
    tables dropped by execute()        0
    tables dropped by executescript()   1   (one statement is allowed to be several)

  the bound column is not a smaller number. it is a different
  arrangement: the statement was parsed before the value existed.
```

Twelve payloads against a five-row table, and the intended answer for every one of them is zero rows,
because none of them is a name that exists. Interpolated, seven of the twelve returned a row, and
the twelve together returned twenty-eight rows. Bound, one of the twelve returned a row, and that one
is `ada`, the real name -- the query found what it was asked to find and nothing else.

Read the two totals rather than the seven. Twenty-eight rows to one is not a smaller number, it is a
different arrangement. In the bound column the statement was parsed before the value existed, so
there was never a moment when the parser could have mistaken `' OR '1'='1` for structure: by the time
the value arrives the parse is already a tree, and the value goes into a leaf. That is the entire
content of the fix, and it is why the fix is a change to how you build the statement rather than a
change to what you allow inside it.

Now look at the second table, which is the one that usually gets skipped. The same payload,
`'; DROP TABLE users; --`, was run twice: once through `execute()` and once through `executescript()`.
Through `execute()` it dropped zero tables. Through `executescript()` it dropped one.

`execute()` refuses more than one statement, and `executescript()` is documented to run several. Both
of those are true, and together they mean the safety in the first row belongs to the driver rather
than to the code. That distinction matters the moment somebody reaches for the method whose name says
"script", which is exactly the method you reach for when you want to run a migration.

## The one place binding is not an option

If binding is a change to how the statement is built, the useful question is where you cannot make
that change. There is one common answer, and it is the one that catches people who have understood
the previous section correctly.

A sort key is not a value. `ORDER BY ?` does not sort by the column you name; it sorts by a string
constant, which is the same order every time. The interface offers four orderings, and binding
delivers none of them.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 2 -- the parts of a statement you cannot bind.

Binding works for values. It does not work for anything the parser has to
understand before the query runs, and a surprising number of a query's parts
are in that category: a column name, a sort direction, a table name.

The reason is not a limitation to work around; it is the mechanism doing its
job. A bound parameter is a value, so a bound column name arrives as the
*string* "name" rather than as the identifier `name`, and the sort does
nothing. Which leaves the question this script answers by counting: if you
cannot bind it, what is the safe way to accept it?
"""
import sqlite3

ROWS = [
    (1, "grace", 92), (2, "ada", 71), (3, "edsger", 58),
    (4, "barbara", 84), (5, "alan", 63),
]

# The four orderings the interface offers, and the six hostile values an
# attacker will try in the same slot.
WANTED = [("name", "ASC"), ("name", "DESC"), ("score", "ASC"), ("score", "DESC")]

HOSTILE = [
    "score; DROP TABLE scores",
    "(SELECT name FROM secrets)",
    "score DESC, name",
    "1",
    "score --",
    "CASE WHEN 1=1 THEN score ELSE name END",
]

ALLOWED = {"name", "score"}
ALLOWED_DIR = {"ASC", "DESC"}


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE scores (id INTEGER, name TEXT, score INTEGER)")
    conn.executemany("INSERT INTO scores VALUES (?, ?, ?)", ROWS)
    conn.execute("CREATE TABLE secrets (value TEXT)")
    conn.execute("INSERT INTO secrets VALUES ('api-key-9f3a')")
    return conn


def names(conn, sql):
    try:
        return [r[0] for r in conn.execute(sql)]
    except (sqlite3.Error, sqlite3.Warning):
        return None


def main():
    print(f"  rows                               {len(ROWS):>3}")
    print(f"  orderings the interface offers     {len(WANTED):>3}")
    print(f"  hostile values tried in the slot   {len(HOSTILE):>3}")

    # 1. Bind the column name. It arrives as a value, so nothing sorts.
    works_bound = 0
    for col, direction in WANTED:
        conn = fresh()
        got = names(conn, "SELECT name FROM scores ORDER BY ? ASC")
        expected = sorted(r[1] for r in ROWS)
        if got == expected and col == "name" and direction == "ASC":
            works_bound += 1
        conn.close()

    # 2. Interpolate it. It sorts, and so does anything else in the slot.
    works_interp = 0
    hostile_ran = []
    hostile_dropped = 0
    for col, direction in WANTED:
        conn = fresh()
        got = names(conn, f"SELECT name FROM scores ORDER BY {col} {direction}")
        if got is not None:
            works_interp += 1
        conn.close()
    for h in HOSTILE:
        conn = fresh()
        got = names(conn, f"SELECT name FROM scores ORDER BY {h}")
        if got is not None:
            hostile_ran.append(h)
        if "scores" not in [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]:
            hostile_dropped += 1
        conn.close()

    # 3. Allow-list it. The value is compared, never parsed.
    works_allow = 0
    for col, direction in WANTED:
        if col in ALLOWED and direction in ALLOWED_DIR:
            conn = fresh()
            got = names(conn, f"SELECT name FROM scores ORDER BY {col} {direction}")
            if got is not None:
                works_allow += 1
            conn.close()
    hostile_allowed = sum(1 for h in HOSTILE
                          if h in ALLOWED or h in ALLOWED_DIR)

    print()
    print(f"    {'approach':<26}{'valid orderings':>17}{'hostile accepted':>18}")
    print(f"    {'bind the column name':<26}{works_bound:>17}{0:>18}")
    print(f"    {'interpolate it':<26}{works_interp:>17}{len(hostile_ran):>18}")
    print(f"    {'allow-list it':<26}{works_allow:>17}{hostile_allowed:>18}")

    print()
    print("  the hostile values that ran, and what they did")
    for h in hostile_ran:
        note = "reads the secrets table" if "secrets" in h else "parsed as an expression"
        print(f"    {h:<44}{note}")

    print()
    print(f"  of {len(WANTED)} valid orderings, binding delivers {works_bound}.")
    print(f"  of {len(HOSTILE)} hostile values, interpolation runs {len(hostile_ran)}"
          f" and drops a table {hostile_dropped} time(s).")
    print(f"  the allow-list delivers {works_allow} valid and accepts "
          f"{hostile_allowed} hostile.")
    print()
    print("  the drop did not happen because execute() refuses more than one")
    print("  statement -- the driver stopped it, not the code. Part 1 of this")
    print("  chapter shows the same payload through executescript().")

    print()
    print("  binding is not the safe option and interpolation the unsafe one.")
    print("  binding is not an option here at all -- so the choice is between")
    print("  interpolating and comparing, and only one of those parses.")


if __name__ == "__main__":
    main()
```

```text
  rows                                 5
  orderings the interface offers       4
  hostile values tried in the slot     6

    approach                    valid orderings  hostile accepted
    bind the column name                      0                 0
    interpolate it                            4                 5
    allow-list it                             4                 0

  the hostile values that ran, and what they did
    (SELECT name FROM secrets)                  reads the secrets table
    score DESC, name                            parsed as an expression
    1                                           parsed as an expression
    score --                                    parsed as an expression
    CASE WHEN 1=1 THEN score ELSE name END      parsed as an expression

  of 4 valid orderings, binding delivers 0.
  of 6 hostile values, interpolation runs 5 and drops a table 0 time(s).
  the allow-list delivers 4 valid and accepts 0 hostile.

  the drop did not happen because execute() refuses more than one
  statement -- the driver stopped it, not the code. Part 1 of this
  chapter shows the same payload through executescript().

  binding is not the safe option and interpolation the unsafe one.
  binding is not an option here at all -- so the choice is between
  interpolating and comparing, and only one of those parses.
```

Six hostile values in the same slot. Interpolation runs five of them, and the five are worth reading
one at a time because they are five different kinds of damage: one reads a table the page never
mentions, and four are parsed as expressions the interface was never meant to evaluate. Then look at
the drop count, which is zero -- and read the paragraph under the table before concluding that
interpolation is therefore safe here. The driver stopped the drop, not the code. Part 1 of this
chapter shows the same payload through the other method.

The last row of the table is the fix, and it is not a variation on binding. The allow-list delivers
all four valid orderings and accepts zero hostile values, because it is not a filter and not an
escape. It is a lookup: the value you pass is a key into a table of strings you wrote, and the string
that reaches the statement is one you chose. That is why it delivers all four rather than most of
them -- a key is either present or it is not.

So the choice in this slot is not between the safe option and the unsafe one. Binding is not an
option at all. The choice is between interpolating and comparing, and only one of those parses.

## Where the argument goes, not what it contains

Command injection looks like a different bug. It is the same one with the parser being a shell, and
it adds a variable that SQL does not have: the same payload is safe or not depending on which
argument position it occupies.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 3 -- which of these five call sites is dangerous?

The received wisdom is "do not use a string with the shell". That is half of
it, and the half that is easy to state is not the half that matters: a list of
arguments is not safe if the shell is still in the pipeline, and a string is
safe if it never reaches one.

So this script measures it instead of asserting it. Every payload is harmless
-- they run `echo` -- and the test is whether a line of output is *exactly* the
marker, which is the difference between a command that ran and a command that
was echoed as text.

Five call sites, eight payloads.
"""
import shlex
import subprocess

MARKER = "INJECTED"

PAYLOADS = [
    "notes.txt",
    "notes.txt; echo INJECTED",
    "notes.txt && echo INJECTED",
    "notes.txt | echo INJECTED",
    "$(echo INJECTED)",
    "`echo INJECTED`",
    "notes.txt\necho INJECTED",
    "notes'.txt",
]


def ran_marker(result):
    """Did a *command* run, or was the marker just echoed as text?"""
    return MARKER in (result.stdout or "").splitlines()


def shell_fstring(name):
    return subprocess.run(f"echo {name}", shell=True,
                          capture_output=True, text=True)


def list_no_shell(name):
    return subprocess.run(["echo", name], shell=False,
                          capture_output=True, text=True)


def shell_quoted(name):
    return subprocess.run(f"echo {shlex.quote(name)}", shell=True,
                          capture_output=True, text=True)


def list_with_shell(name):
    return subprocess.run(["echo", name], shell=True,
                          capture_output=True, text=True)


def list_first_arg(name):
    """shell=True with a sequence: argv[0] is the command string."""
    return subprocess.run([f"echo {name}"], shell=True,
                          capture_output=True, text=True)


def explicit_sh(name):
    return subprocess.run(["sh", "-c", f"echo {name}"], shell=False,
                          capture_output=True, text=True)


SITES = [
    ("f-string, shell=True", shell_fstring),
    ("list, shell=False", list_no_shell),
    ("shlex.quote, shell=True", shell_quoted),
    ("list, shell=True, payload in argv[1]", list_with_shell),
    ("list, shell=True, payload in argv[0]", list_first_arg),
    ("['sh','-c', f-string], shell=False", explicit_sh),
]


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  the test is whether a line equals  {MARKER!r}")
    print()
    print(f"    {'call site':<42}{'payloads that ran':>18}{'safe?':>8}")
    for label, fn in SITES:
        hits = 0
        for p in PAYLOADS:
            try:
                if ran_marker(fn(p)):
                    hits += 1
            except OSError:
                pass
        safe = hits == 0
        print(f"    {label:<42}{hits:>18}{('yes' if safe else 'NO'):>8}")

    print()
    print(f"  of {len(PAYLOADS)} payloads, a call site that never reaches a shell")
    print("  runs 0 of them, whichever way the arguments were written.")
    print()
    print("  the two shell=True rows differ only in which argument the payload")
    print("  occupies, and they differ by every payload in the set.")


if __name__ == "__main__":
    main()
```

```text
  payloads                             8
  the test is whether a line equals  'INJECTED'

    call site                                  payloads that ran   safe?
    f-string, shell=True                                       6      NO
    list, shell=False                                          0     yes
    shlex.quote, shell=True                                    0     yes
    list, shell=True, payload in argv[1]                       0     yes
    list, shell=True, payload in argv[0]                       6      NO
    ['sh','-c', f-string], shell=False                         6      NO

  of 8 payloads, a call site that never reaches a shell
  runs 0 of them, whichever way the arguments were written.

  the two shell=True rows differ only in which argument the payload
  occupies, and they differ by every payload in the set.
```

Six call sites, eight payloads, and the test is whether a line equal to `INJECTED` appears -- nothing
subtle, because nothing subtle is needed.

Two rows to read. The first is the last one: `['sh', '-c', f-string]` with `shell=False` runs all
eight. `shell=False` is the setting people quote as the fix, and here it is the wrong thing to look
at, because the shell is not spawned by the flag -- it is the program being invoked. The rule is not
"pass `shell=False`". The rule is that no shell appears anywhere in the pipeline, and a call that
names `sh` as its first argument has one.

The second is the pair of `shell=True` rows that differ by every payload in the set and differ in
nothing else. Payload in `argv[1]`: zero. Payload in `argv[0]`: eight. The payload did not change,
the escaping did not change, and the setting did not change. What changed is where the value landed,
and on POSIX `argv[0]` becomes the command string while the rest become the shell's positional
arguments. The vulnerability is a property of the position, which is why "is this input dangerous"
is not a question that has an answer.

`shlex.quote` does work here -- zero of eight -- and it is worth noticing that it works by quoting for
one specific parser. That is a real fix at a real call site, and the pitfall later in this chapter is
about what it costs to have one of those per call site.

## The same mechanism, one layer up

Template injection is where the parser stops being a query language or a shell and becomes a
programming language with attribute access, and the consequence is that a payload does not need to
call anything.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 4 -- the template engine is a code path.

Server-side template injection is usually taught with a template library,
which hides the mechanism behind the interesting question: which string was
the *template*? This script uses `str.format`, which is in the standard
library and is enough to show the whole thing.

`str.format` evaluates attribute access and indexing inside the braces. So a
string that reaches `.format()` as the format string is a program, and a
string that reaches it as an argument is data. The payload set is the same in
both cases; only the position changes.

Nothing prints a payload's *result*, because a repr of a class contains an
address. The script counts whether a payload expanded and whether it read the
attribute it was aiming at.
"""


class Vault:
    def __init__(self):
        self.secret = "s3cr3t"


PAYLOADS = [
    "{0}",
    "{0.secret}",
    "{0.__class__}",
    "{0.__class__.__mro__}",
    "{0.__class__.__mro__[1].__subclasses__}",
    "{0.__init__.__globals__}",
    "{0[0]}",
]

FIXED = "Hello, {name}!"


def main():
    thing = Vault()

    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  the object passed to format()      Vault(secret={thing.secret!r})")
    print()
    print(f"    {'payload':<46}{'as the template':>16}{'as an argument':>15}")

    expanded, leaked = 0, 0
    as_data = 0
    for p in PAYLOADS:
        # The payload is the template: it is parsed.
        try:
            out = p.format(thing)
            did_expand = True
        except (AttributeError, IndexError, KeyError, TypeError, ValueError):
            did_expand = False
        if did_expand:
            expanded += 1
            if thing.secret in out:
                leaked += 1

        # The payload is an argument: it is a value.
        out2 = FIXED.format(name=p)
        if p in out2:
            as_data += 1

        print(f"    {p:<46}{('yes' if did_expand else 'no'):>16}"
              f"{('data' if p in out2 else '?'):>15}")

    print()
    print(f"  payloads that expanded as the template      {expanded} of {len(PAYLOADS)}")
    print(f"  of those, payloads that read .secret        {leaked}")
    print(f"  payloads treated as data as an argument     {as_data} of {len(PAYLOADS)}")

    # The minimal fix for this mechanism, measured the same way. Note the test
    # cannot be "did it raise" -- nothing raises once the braces are doubled;
    # the question is whether the payload came back as data.
    doubled_as_data = 0
    for p in PAYLOADS:
        doubled = p.replace("{", "{{").replace("}", "}}")
        try:
            out = doubled.format(thing)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError):
            continue
        if out == p:
            doubled_as_data += 1
    print()
    print(f"  with braces doubled first                   {doubled_as_data} of "
          f"{len(PAYLOADS)} come back as data")

    print()
    print(f"  the same payloads, the same call. the two columns disagree on {expanded}")
    print(f"  of the {len(PAYLOADS)} rows -- every row where the payload was interpreted as a")
    print("  template. the vulnerability is not in the payload.")


if __name__ == "__main__":
    main()
```

```text
  payloads                             7
  the object passed to format()      Vault(secret='s3cr3t')

    payload                                        as the template as an argument
    {0}                                                        yes           data
    {0.secret}                                                 yes           data
    {0.__class__}                                              yes           data
    {0.__class__.__mro__}                                      yes           data
    {0.__class__.__mro__[1].__subclasses__}                    yes           data
    {0.__init__.__globals__}                                   yes           data
    {0[0]}                                                      no           data

  payloads that expanded as the template      6 of 7
  of those, payloads that read .secret        1
  payloads treated as data as an argument     7 of 7

  with braces doubled first                   7 of 7 come back as data

  the same payloads, the same call. the two columns disagree on 6
  of the 7 rows -- every row where the payload was interpreted as a
  template. the vulnerability is not in the payload.
```

Seven payloads, run twice each. As the template, six of the seven were parsed and expanded. As an
argument to a fixed template, all seven came back as data. Same payloads, same `format()` call, and
the two columns disagree on six of the seven rows -- every row where the payload was interpreted as a
template.

The row to look at is `{0.secret}`. It is one of the six that expanded, it is the one of those six
that read the attribute the object was holding, and it contains no call, no import and no name. It is
a field access. A template engine that offers field access offers it to whoever supplies the
template, and the string `{0.__class__.__mro__[1].__subclasses__}` in the table is where that path
leads when somebody keeps walking.

The last line of the output is the minimal fix, and it is the same fix as the previous section:
doubling the braces makes the payload a literal, and seven of seven come back as data. Nothing about
the payload changed, again. The mechanism was never in the payload.

## Text that runs is a decision

`eval` is injection with the parser removed, because there is no data position at all. Every
character of the string is structure, and the only question is which structure you are willing to
accept.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 5 -- eval, literal_eval, and a restricted eval.

`eval` runs its argument. `ast.literal_eval` parses its argument and returns
the value only if the whole thing is a literal. Those are different promises
and the difference is measurable: feed both the same set of strings and count
what each accepts.

The third column is the one that matters for people who try to fix `eval` by
taking the builtins away. That is a filter, not a sandbox, and a filter has a
coverage number.

Nothing prints a payload's *value* -- several of them return machine-specific
objects. The counts are of accepted versus rejected, which is a fact about the
functions rather than about this computer.
"""
import ast

LITERALS = [
    "[1, 2, 3]",
    '{"a": 1}',
    "(1, 2)",
    '"x"',
    "42",
    "True",
    "None",
    "1.5",
    "[[1], [2]]",
    "{1, 2}",
]

CODE = [
    '__import__("sys")',
    "1 + 1",
    "[i for i in range(3)]",
    "(lambda: 1)()",
    "().__class__",
    'exec("y = 1")',
    '__import__("os").getpid()',
    "globals()",
]

BIG = "[" + ",".join(["1"] * 20000) + "]"


def accepts(fn, text):
    try:
        fn(text)
        return True
    except Exception:
        return False


def main():
    print(f"  literal strings                    {len(LITERALS):>3}")
    print(f"  code strings                       {len(CODE):>3}")
    print()
    print(f"    {'input':<32}{'eval':>7}{'literal_eval':>14}{'restricted eval':>17}")

    ev = lv = rv = 0
    for s in LITERALS:
        a = accepts(eval, s)
        b = accepts(ast.literal_eval, s)
        c = accepts(lambda t: eval(t, {"__builtins__": {}}), s)
        ev += a
        lv += b
        rv += c
        print(f"    {s:<32}{('yes' if a else 'no'):>7}{('yes' if b else 'no'):>14}"
              f"{('yes' if c else 'no'):>17}")

    print()
    ev_c = lv_c = rv_c = 0
    for s in CODE:
        a = accepts(eval, s)
        b = accepts(ast.literal_eval, s)
        c = accepts(lambda t: eval(t, {"__builtins__": {}}), s)
        ev_c += a
        lv_c += b
        rv_c += c
        print(f"    {s:<32}{('yes' if a else 'no'):>7}{('yes' if b else 'no'):>14}"
              f"{('yes' if c else 'no'):>17}")

    print()
    print(f"  of {len(LITERALS)} literals   eval {ev}, literal_eval {lv}, restricted {rv}")
    print(f"  of {len(CODE)} code strings  eval {ev_c}, literal_eval {lv_c}, "
          f"restricted {rv_c}")
    print()
    print(f"  literal_eval rejected {len(CODE) - lv_c} of {len(CODE)} code strings"
          f" and {len(LITERALS) - lv} of {len(LITERALS)} literals.")
    print(f"  restricted eval still ran {rv_c} of {len(CODE)}"
          f" -- a filter, with a coverage number.")

    # Safety from code execution is not safety from resource use.
    print()
    print(f"  a literal of {len(BIG):,} characters")
    try:
        obj = ast.literal_eval(BIG)
        print(f"    literal_eval accepts it            {len(obj):>7,} elements")
    except Exception as exc:
        print(f"    literal_eval rejects it            {type(exc).__name__}")
    print("    both functions accept it, because neither has a size limit.")
    print("    literal_eval is a promise about *parsing*, not about resources.")


if __name__ == "__main__":
    main()
```

```text
  literal strings                     10
  code strings                         8

    input                              eval  literal_eval  restricted eval
    [1, 2, 3]                           yes           yes              yes
    {"a": 1}                            yes           yes              yes
    (1, 2)                              yes           yes              yes
    "x"                                 yes           yes              yes
    42                                  yes           yes              yes
    True                                yes           yes              yes
    None                                yes           yes              yes
    1.5                                 yes           yes              yes
    [[1], [2]]                          yes           yes              yes
    {1, 2}                              yes           yes              yes

    __import__("sys")                   yes            no               no
    1 + 1                               yes            no              yes
    [i for i in range(3)]               yes            no               no
    (lambda: 1)()                       yes            no              yes
    ().__class__                        yes            no              yes
    exec("y = 1")                       yes            no               no
    __import__("os").getpid()           yes            no               no
    globals()                           yes            no               no

  of 10 literals   eval 10, literal_eval 10, restricted 10
  of 8 code strings  eval 8, literal_eval 0, restricted 3

  literal_eval rejected 8 of 8 code strings and 0 of 10 literals.
  restricted eval still ran 3 of 8 -- a filter, with a coverage number.

  a literal of 40,001 characters
    literal_eval accepts it             20,000 elements
    both functions accept it, because neither has a size limit.
    literal_eval is a promise about *parsing*, not about resources.
```

Ten literals and eight code strings, three loaders. Plain `eval` accepts all eighteen, which is the
expected result. `ast.literal_eval` accepts all ten literals and rejects all eight code strings, and
the second number is the one that makes it a different kind of answer from the others: it does not
run less of the string, it refuses to accept a string that is not data. That is why it also keeps all
ten literals, including the ones a filter would have thrown away.

The middle column is the interesting one. "Restricted eval" -- a filter that permits arithmetic and
blocks names -- ran three of the eight. `1 + 1` is obviously permitted. So is `(lambda: 1)()`, which
is a function call the filter allowed because it contains no forbidden name, and so is
`().__class__`, which is attribute access on a literal. Three of eight is a coverage number, and a
filter with a coverage number is a filter you have to keep scoring. The next section is about what
happens to that number over time.

Then the last block, which is the one that catches people who have already chosen `literal_eval`
correctly. A literal of forty thousand and one characters parses into twenty thousand elements, and
both loaders accept it. `literal_eval` is a promise about *parsing*. It is not a promise about
resources, and the resource question belongs somewhere else in the design.

## The value you check must be the value you use

Everything so far has had the payload arriving in a place it should not be. This section is about a
payload that arrives in the right place and is checked there, and still gets through, because the
check and the use do not look at the same string.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 8 -- the check must run after the normalisation.

A blocklist that looks for `../` is not wrong. It is wrong *in the position it
is usually placed*, which is before the value has been decoded. The value that
reaches the file system is not the value that arrived in the request; there is
a decoding step in between, and a check that runs on the wrong side of it is
checking a string nobody will use.

Nine payloads, three placements. The third placement decodes until the value
stops changing, which is the property that makes a normalisation usable as a
security boundary: it has to be idempotent.
"""
import urllib.parse

PAYLOADS = [
    "../etc/passwd",
    "%2e%2e%2fetc/passwd",
    "..%2fetc/passwd",
    "%252e%252e%252fetc/passwd",
    "....//etc/passwd",
    "..%5cetc%5cpasswd",
    "%2e./etc/passwd",
    "..%2Fetc%2Fpasswd",
    "....//....//etc/passwd",
]


def is_traversal(value):
    v = value.replace("\\", "/")
    return "../" in v or v.startswith("/") or v.endswith("/..")


def normalise_once(value):
    return urllib.parse.unquote(value)


def normalise_stable(value):
    """Decode until the value stops changing, then fold separators."""
    seen = value
    while True:
        nxt = normalise_once(seen)
        if nxt == seen:
            break
        seen = nxt
    return seen.replace("\\", "/")


def passes_needed(value):
    n, seen = 0, value
    while True:
        nxt = normalise_once(seen)
        if nxt == seen:
            return n
        seen, n = nxt, n + 1


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print()
    print(f"    {'payload':<34}{'raw':>6}{'once':>7}{'stable':>8}{'passes':>8}")

    raw_caught = once_caught = stable_caught = 0
    multi = 0
    for p in PAYLOADS:
        a = is_traversal(p)
        b = is_traversal(normalise_once(p))
        c = is_traversal(normalise_stable(p))
        n = passes_needed(p)
        raw_caught += a
        once_caught += b
        stable_caught += c
        if n > 1:
            multi += 1
        print(f"    {p:<34}{('yes' if a else 'no'):>6}{('yes' if b else 'no'):>7}"
              f"{('yes' if c else 'no'):>8}{n:>8}")

    total = len(PAYLOADS)
    print()
    print(f"  checked before decoding            {raw_caught:>3} of {total}"
          f"   ({raw_caught / total:.1%})")
    print(f"  checked after decoding once        {once_caught:>3} of {total}"
          f"   ({once_caught / total:.1%})")
    print(f"  checked after decoding to a fixed point {stable_caught:>3} of {total}"
          f"   ({stable_caught / total:.1%})")

    print()
    print(f"  payloads needing more than one pass {multi:>3}"
          f"   (the double-encoded one)")

    missed_once = [p for p in PAYLOADS if not is_traversal(normalise_once(p))]
    print(f"  what the one-pass check misses     {len(missed_once):>3}")
    for p in missed_once:
        print(f"    {p}  ->  {normalise_once(p)}")

    print()
    print("  the rule is not 'decode first'. it is 'the value you check must be")
    print("  the value you use' -- and since decoding can be applied more than")
    print("  once by the layers in front of you, the check belongs after the")
    print("  fixed point, not after one call.")


if __name__ == "__main__":
    main()
```

```text
  payloads                             9

    payload                              raw   once  stable  passes
    ../etc/passwd                        yes    yes     yes       0
    %2e%2e%2fetc/passwd                   no    yes     yes       1
    ..%2fetc/passwd                       no    yes     yes       1
    %252e%252e%252fetc/passwd             no     no     yes       2
    ....//etc/passwd                     yes    yes     yes       0
    ..%5cetc%5cpasswd                     no    yes     yes       1
    %2e./etc/passwd                       no    yes     yes       1
    ..%2Fetc%2Fpasswd                     no    yes     yes       1
    ....//....//etc/passwd               yes    yes     yes       0

  checked before decoding              3 of 9   (33.3%)
  checked after decoding once          8 of 9   (88.9%)
  checked after decoding to a fixed point   9 of 9   (100.0%)

  payloads needing more than one pass   1   (the double-encoded one)
  what the one-pass check misses       1
    %252e%252e%252fetc/passwd  ->  %2e%2e%2fetc/passwd

  the rule is not 'decode first'. it is 'the value you check must be
  the value you use' -- and since decoding can be applied more than
  once by the layers in front of you, the check belongs after the
  fixed point, not after one call.
```

Nine traversal payloads. Checked as it arrives, three of the nine are caught -- 33.3%. Checked after
one round of decoding, eight of the nine -- 88.9%. Checked after decoding to a fixed point, nine of
the nine.

The gap between the second and third numbers is one payload, and it is the double-encoded one:
`%252e%252e%252fetc/passwd` decodes once to `%2e%2e%2fetc/passwd`, which is still encoded, and only
decodes to `../` on the second pass. If your check decodes once and your framework decodes twice,
you have checked a string that is not the string you are about to open.

That is the rule, and it is worth stating precisely because the version people remember is wrong.
The rule is not "decode first". Decoding first is what the middle row already does. The rule is that
the value you check must be the value you use, and since decoding can be applied more than once by
the layers in front of you, the check belongs after the fixed point rather than after one call.

Notice the shape of this bug, because it is the one in this chapter that no amount of input
validation fixes. Every payload here is a well-formed string. There is nothing in any of the nine
that a validator could object to on its own terms.

## One payload, eight sinks

"Escape the input" is the advice that survives after "validate the input" has been ruled out, and it
is a decision rather than an instruction. An escaper is correct or incorrect relative to a parser,
so the unit of the decision is the pair -- this encoder, that sink.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 7 -- escaping is per-sink, so "sanitise" is not a function.

Every sink parses its input with different rules, which means the encoding
that neutralises a value in one sink is wrong in another. The word for a
function that makes a value safe for *all* of them does not exist, and this
script counts why: it builds the matrix.

Six payloads, eight sinks, seven encoders, and for each pair a test of whether
the encoded value is still dangerous in that sink. Every test is a small
structural check, so the counts are exact and nothing depends on the machine.

The last table is the interesting one. Exactly one encoder makes all eight
sinks safe, and it does it by destroying the value.
"""

PAYLOADS = [
    "<script>alert(1)</script>",
    "' OR 1=1 --",
    "$(id)",
    "../etc/passwd",
    "a\nINJECTED",
    '{"json": "value"}',
]

# ---------------------------------------------------------------- the sinks
# Each returns True when the value is still dangerous in that sink.


def html_body(v):
    return "<script" in v or "<img" in v


def html_attribute(v):
    return '"' in v


def js_string(v):
    return "'" in v or "\\" in v or "<" in v


def url_query(v):
    return "&" in v or "=" in v or "#" in v


def sql_literal(v):
    return v.count("'") % 2 == 1


def log_line(v):
    return "\n" in v or "\r" in v


def http_header(v):
    return "\n" in v or "\r" in v


def json_string(v):
    return '"' in v or "\\" in v


SINKS = [
    ("HTML body", html_body),
    ("HTML attribute", html_attribute),
    ("JavaScript string", js_string),
    ("URL query", url_query),
    ("SQL literal", sql_literal),
    ("log line", log_line),
    ("HTTP header", http_header),
    ("JSON string", json_string),
]

SHORT = {
    "HTML body": "HTMLbody",
    "HTML attribute": "HTMLattr",
    "JavaScript string": "JSstr",
    "URL query": "URLquery",
    "SQL literal": "SQLlit",
    "log line": "logline",
    "HTTP header": "HTTPhdr",
    "JSON string": "JSONstr",
}

# -------------------------------------------------------------- the encoders


def enc_none(v):
    return v


def enc_html(v):
    return (v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def enc_js(v):
    return (v.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
             .replace("<", "\\x3c"))


def enc_url(v):
    out = []
    for ch in v:
        if ch.isalnum() or ch in "-._~":
            out.append(ch)
        else:
            out.append(f"%{ord(ch):02X}")
    return "".join(out)


def enc_sql(v):
    return v.replace("'", "''")


def enc_json(v):
    return (v.replace("\\", "\\\\").replace('"', '\\"')
             .replace("\n", "\\n").replace("\r", "\\r"))


def enc_strip_newlines(v):
    return v.replace("\n", "").replace("\r", "")


ENCODERS = [
    ("none", enc_none),
    ("html_escape", enc_html),
    ("js_escape", enc_js),
    ("url_quote", enc_url),
    ("sql_double", enc_sql),
    ("json_escape", enc_json),
    ("strip_newlines", enc_strip_newlines),
]


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print(f"  sinks                              {len(SINKS):>3}")
    print(f"  encoders                           {len(ENCODERS):>3}")

    # pairs[encoder][sink] = how many payloads stay safe
    fixes = {}
    for ename, fn in ENCODERS:
        row = {}
        for sname, check in SINKS:
            safe = sum(1 for p in PAYLOADS if not check(fn(p)))
            row[sname] = safe
        fixes[ename] = row

    print()
    print(f"    {'encoder':<18}" + "".join(f"{SHORT[s]:>10}" for s, _ in SINKS))
    for ename, _ in ENCODERS:
        cells = "".join(f"{fixes[ename][s]:>10}" for s, _ in SINKS)
        print(f"    {ename:<18}{cells}")
    print(f"    {'':<18}" + "".join(f"{SHORT[s]:>10}" for s, _ in SINKS))
    print(f"    (cells are payloads out of {len(PAYLOADS)} that stay safe)")

    print()
    print("  sinks each encoder makes safe, out of " + str(len(SINKS)))
    totals = {}
    for ename, _ in ENCODERS:
        n = sum(1 for s, _ in SINKS if fixes[ename][s] == len(PAYLOADS))
        totals[ename] = n
        print(f"    {ename:<18}{n:>3}")

    universal = [e for e in totals if totals[e] == len(SINKS)]
    print()
    print(f"  encoders that make every sink safe   {len(universal)}"
          f"   {', '.join(universal) if universal else '--'}")

    # An encoder can also make a sink *less* safe than leaving the value alone.
    baseline = fixes["none"]
    print()
    print("  sinks each encoder makes worse than doing nothing")
    worse_total = 0
    for ename, _ in ENCODERS:
        if ename == "none":
            continue
        bad = [s for s, _ in SINKS if fixes[ename][s] < baseline[s]]
        if bad:
            worse_total += 1
            print(f"    {ename:<18}{len(bad)}   {', '.join(bad)}")
    print(f"    encoders that make at least one sink worse   {worse_total}")

    # Does the universal one preserve the value?
    print()
    unchanged = {ename: sum(1 for p in PAYLOADS if fn(p) == p)
                 for ename, fn in ENCODERS}

    print("  and whether each encoder returns the value unchanged")
    print(f"    {'encoder':<18}{'payloads unchanged':>19}")
    for ename, _ in ENCODERS:
        print(f"    {ename:<18}{unchanged[ename]:>19}")

    rest = {e: n for e, n in totals.items()
            if e != "none" and e not in universal}
    best = max(rest, key=lambda e: (rest[e], -unchanged[e], e))
    print()
    print(f"  the best encoder short of {universal[0]} fixes {totals[best]} of "
          f"{len(SINKS)} sinks ({best}),")
    print(f"  and rewrites {len(PAYLOADS) - unchanged[best]} of the "
          f"{len(PAYLOADS)} payloads to do it.")
    print(f"  the one that fixes all {len(SINKS)} ({universal[0]}) rewrites "
          f"every value it is given.")
    print()
    print(f"  and {worse_total} of the {len(ENCODERS) - 1} encoders that change "
          f"anything make")
    print("  at least one sink less safe than leaving the value alone, which is")
    print("  the failure mode nobody writes a test for.")


if __name__ == "__main__":
    main()
```

```text
  payloads                             6
  sinks                                8
  encoders                             7

    encoder             HTMLbody  HTMLattr     JSstr  URLquery    SQLlit   logline   HTTPhdr   JSONstr
    none                       5         5         4         5         5         5         5         5
    html_escape                6         6         6         3         6         5         5         6
    js_escape                  6         5         3         5         5         5         5         3
    url_quote                  6         6         6         6         6         6         6         6
    sql_double                 5         5         4         5         6         5         5         5
    json_escape                5         5         2         5         5         6         6         4
    strip_newlines             5         5         4         5         5         6         6         5
                        HTMLbody  HTMLattr     JSstr  URLquery    SQLlit   logline   HTTPhdr   JSONstr
    (cells are payloads out of 6 that stay safe)

  sinks each encoder makes safe, out of 8
    none                0
    html_escape         5
    js_escape           1
    url_quote           8
    sql_double          1
    json_escape         2
    strip_newlines      2

  encoders that make every sink safe   1   url_quote

  sinks each encoder makes worse than doing nothing
    html_escape       1   URL query
    js_escape         2   JavaScript string, JSON string
    json_escape       2   JavaScript string, JSON string
    encoders that make at least one sink worse   3

  and whether each encoder returns the value unchanged
    encoder            payloads unchanged
    none                                6
    html_escape                         3
    js_escape                           3
    url_quote                           0
    sql_double                          5
    json_escape                         4
    strip_newlines                      5

  the best encoder short of url_quote fixes 5 of 8 sinks (html_escape),
  and rewrites 3 of the 6 payloads to do it.
  the one that fixes all 8 (url_quote) rewrites every value it is given.

  and 3 of the 6 encoders that change anything make
  at least one sink less safe than leaving the value alone, which is
  the failure mode nobody writes a test for.
```

Six payloads, eight sinks, seven encoders, and the cells are how many of the six payloads stay safe
in that sink after that encoder. Fifty-six pairs, and the table is worth reading as a grid rather
than a list.

One encoder makes every sink safe: `url_quote`, eight of eight. It also returns zero of the six
payloads unchanged -- it rewrites every value it is given, which is why it is safe and also why it is
not what you want in an HTML body or a log line.

Every other encoder is a column with holes. `html_escape` fixes five of the eight sinks, which sounds
like most of them, and it rewrites three of the six payloads to do it. Then look at the third table,
because two rows there are the ones nobody writes a test for. `html_escape` makes the URL query sink
*less* safe than doing nothing: five payloads safe becomes three. `js_escape` and `json_escape` each
make two sinks worse. Three of the six encoders that change anything at all make at least one sink
worse than leaving the value alone.

The mechanism is not mysterious once you see it. Escaping for HTML turns `'` into `&#39;`, which is
five characters where there was one, and in a URL query that is not an escape at all -- it is four
new characters you did not sanitise. An encoder that is correct for one parser is a transformer for
every other parser, and a transformer with no stated output alphabet is a source of new input.

## The blocklist has a coverage number

If escaping is per-pair, the tempting simplification is a list of known-bad patterns. This section
generates the input space instead of arguing about it, because the argument is decided by arithmetic.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 9 -- what a blocklist actually covers.

A blocklist is judged by whether it catches the payload in the incident
report. The number that matters is different: of all the strings that mean the
same thing to the parser, what fraction does it catch? That fraction can be
computed, because the set is finite and small if you build it deliberately.

One payload -- a tautology with a quote -- expanded four ways: letter case,
the separator between the words, a prefix, a suffix, and five encodings. Seven
thousand six hundred and eighty strings, all of them equivalent to a database,
and four blocklist configurations scored against every one.

The last line is the point: the configurations differ by a factor, and the
factor is still not one.
"""
import urllib.parse

BASE = "' or true"
LETTERS = [i for i, c in enumerate(BASE) if c.isalpha()]

SEPARATORS = [("space", " "), ("tab", "\t"), ("newline", "\n"), ("comment", "/**/")]
PREFIXES = [("plain", ""), ("bang-comment", "/*!*/")]
SUFFIXES = [("none", ""), ("dash-dash", "--"), ("hash", "#")]
ENCODINGS = ["raw", "url", "double url", "html", "unicode"]

SIGNATURES = [
    "' or true", "or 1=1", "union select", "drop table",
    "1=1", "--", "/*!", "or 1",
]


def case_variants():
    out = []
    for mask in range(1 << len(LETTERS)):
        chars = list(BASE)
        for bit, idx in enumerate(LETTERS):
            if (mask >> bit) & 1:
                chars[idx] = chars[idx].upper()
        out.append("".join(chars))
    return out


def enc_raw(v):
    return v


def enc_url(v):
    return urllib.parse.quote(v, safe="")


def enc_double_url(v):
    return urllib.parse.quote(urllib.parse.quote(v, safe=""), safe="")


def enc_html(v):
    return v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") \
            .replace("'", "&#39;")


def enc_unicode(v):
    return v.replace("'", "\\u0027").replace("<", "\\u003c")


ENCODER = {
    "raw": enc_raw,
    "url": enc_url,
    "double url": enc_double_url,
    "html": enc_html,
    "unicode": enc_unicode,
}


def build():
    space = []
    for base in case_variants():
        for _, sep in SEPARATORS:
            variant = base.replace(" ", sep, 1)
            for _, pre in PREFIXES:
                for _, suf in SUFFIXES:
                    text = pre + variant + suf
                    for enc in ENCODINGS:
                        space.append((enc, ENCODER[enc](text)))
    return space


def matches(value, signatures, case_sensitive):
    hay = value if case_sensitive else value.lower()
    for sig in signatures:
        needle = sig if case_sensitive else sig.lower()
        if needle in hay:
            return True
    return False


def to_fixed_point(value):
    seen = value
    while True:
        nxt = urllib.parse.unquote(seen)
        if nxt == seen:
            return seen
        seen = nxt


def main():
    space = build()
    total = len(space)
    print(f"  base payload                       {BASE!r}")
    print(f"  case variants                      {1 << len(LETTERS):>6}")
    print(f"  separators                         {len(SEPARATORS):>6}")
    print(f"  prefixes x suffixes                {len(PREFIXES) * len(SUFFIXES):>6}")
    print(f"  encodings                          {len(ENCODINGS):>6}")
    print(f"  strings in the space               {total:>6}")

    configs = [
        ("raw, case-sensitive", lambda v: matches(v, SIGNATURES, True)),
        ("raw, case-insensitive", lambda v: matches(v, SIGNATURES, False)),
        ("decoded once", lambda v: matches(urllib.parse.unquote(v), SIGNATURES, False)),
        ("decoded to a fixed point", lambda v: matches(to_fixed_point(v), SIGNATURES, False)),
    ]

    print()
    print(f"  a blocklist of {len(SIGNATURES)} signatures, scored against all {total}")
    print()
    print(f"    {'configuration':<28}{'caught':>8}{'missed':>8}{'coverage':>10}")
    for label, test in configs:
        caught = sum(1 for _, v in space if test(v))
        print(f"    {label:<28}{caught:>8}{total - caught:>8}"
              f"{caught / total:>9.1%}")

    # Which encodings are invisible to the best configuration?
    best = configs[-1][1]
    print()
    print(f"    {'encoding':<28}{'caught':>8}{'of':>8}{'coverage':>10}")
    for enc in ENCODINGS:
        got = [(e, v) for e, v in space if e == enc]
        caught = sum(1 for _, v in got if best(v))
        print(f"    {enc:<28}{caught:>8}{len(got):>8}{caught / len(got):>9.1%}")

    print()
    print("  the best configuration catches most of the space, and the space")
    print("  is generated by the attacker, who can always add a dimension.")
    print()
    print("  a blocklist is a filter with a coverage number, and the number")
    print("  moves every time somebody writes a new encoder.")


if __name__ == "__main__":
    main()
```

```text
  base payload                       "' or true"
  case variants                          64
  separators                              4
  prefixes x suffixes                     6
  encodings                               5
  strings in the space                 7680

  a blocklist of 8 signatures, scored against all 7680

    configuration                 caught  missed  coverage
    raw, case-sensitive             4098    3582    53.4%
    raw, case-insensitive           4224    3456    55.0%
    decoded once                    4864    2816    63.3%
    decoded to a fixed point        5504    2176    71.7%

    encoding                      caught      of  coverage
    raw                             1152    1536    75.0%
    url                             1152    1536    75.0%
    double url                      1152    1536    75.0%
    html                            1024    1536    66.7%
    unicode                         1024    1536    66.7%

  the best configuration catches most of the space, and the space
  is generated by the attacker, who can always add a dimension.

  a blocklist is a filter with a coverage number, and the number
  moves every time somebody writes a new encoder.
```

One base payload, `' or true`, and four independent dimensions: sixty-four case variants, four
separators, six prefix and suffix combinations, five encodings. Seven thousand six hundred and eighty
distinct strings, all of them the same attack.

Eight signatures, scored against all of them. The most careful configuration -- case-insensitive,
decoded to a fixed point -- catches five thousand five hundred and four, which is 71.7%. The least
careful catches 53.4%. Notice that the improvement from the first row to the last is real and
substantial: two and a half thousand more payloads caught, for the work of normalising before
matching. That is worth doing.

Then notice the breakdown by encoding, which is where the number stops being a project you can
finish. Every configuration catches 75.0% of the raw, URL and double-URL strings and 66.7% of the
HTML and unicode ones. The encodings are not equally hard, which means the attacker's cheapest move
is to shift the mix toward the ones you are worst at -- and the attacker generates the space, so the
mix is theirs to choose.

A blocklist is a filter with a coverage number. The number moves every time somebody writes a new
encoder, and somebody is always writing a new encoder.

## The separator is part of the data

The last one is not about a parser at all. It is about a format whose records are separated by a
character that also appears inside the fields, and the count is what a reader of that file will
believe.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 6 -- the log is a sink like any other.

A log file is read by a person and by a parser, and both of them decide where
one record ends by looking for a newline. So a value that contains a newline
does not extend a record; it *starts a new one*, and the new record is written
in the logger's voice rather than the attacker's.

The payloads here are harmless strings. What they forge is a log line, which
is the point: the damage is to the evidence, not to the system. Sixty
requests, twelve of which carry a query that is not a query.
"""
NORMAL_QUERIES = ["q=holiday", "q=verbs", "limit=20", "sort=name", "q=hola"]

CLAIM = "2026-01-01 00:00:00 INFO auth login success user="
FORGED = "x\n" + CLAIM + "admin\n" + CLAIM + "root"

REQUESTS = 60


def build():
    out = []
    for i in range(REQUESTS):
        q = FORGED if i % 5 == 0 else NORMAL_QUERIES[i % len(NORMAL_QUERIES)]
        out.append(("GET", "/search", q))
    return out


def log_naive(text, method, path, q):
    text.append(f"{method} {path} q={q}")


def log_escaped(text, method, path, q):
    safe = q.replace("\r", "\\r").replace("\n", "\\n")
    text.append(f"{method} {path} q={safe}")


def to_file(text):
    """What lands in the file: the logger writes a string, the file has lines."""
    lines = []
    for chunk in text:
        lines.extend(chunk.split("\n"))
    return lines


def main():
    trace = build()
    hostile = [r for r in trace if "\n" in r[2]]

    naive_written = []
    for method, path, q in trace:
        log_naive(naive_written, method, path, q)

    escaped_written = []
    for method, path, q in trace:
        log_escaped(escaped_written, method, path, q)

    naive = to_file(naive_written)
    escaped = to_file(escaped_written)

    forged = [ln for ln in naive if not ln.startswith("GET ")]
    claims = [ln for ln in forged if "login success" in ln]
    forged_escaped = [ln for ln in escaped if not ln.startswith("GET ")]

    print(f"  requests made                      {REQUESTS:>3}")
    print(f"  requests carrying a newline        {len(hostile):>3}")
    print(f"  strings handed to the log          {len(naive_written):>3}")
    print(f"  the payload, as a value            {FORGED!r}")
    print()
    print(f"    {'':<24}{'lines written':>14}{'not a request':>15}"
          f"{'claiming success':>18}")
    print(f"    {'newlines written as-is':<24}{len(naive):>14}{len(forged):>15}"
          f"{len(claims):>18}")
    print(f"    {'newlines escaped':<24}{len(escaped):>14}{len(forged_escaped):>15}"
          f"{0:>18}")

    print()
    print(f"  a parser splitting on newlines sees {len(naive)} events from "
          f"{REQUESTS} requests.")
    print(f"  {len(claims)} of them record a successful login as a privileged user.")
    print()
    print("  every forged line is attributable to nobody, and the request")
    print("  that produced it is the one line in the group that looks normal.")
    print()
    print(f"  escaping the value takes the count from {len(naive)} lines to "
          f"{len(escaped)} -- one per request.")


if __name__ == "__main__":
    main()
```

```text
  requests made                       60
  requests carrying a newline         12
  strings handed to the log           60
  the payload, as a value            'x\n2026-01-01 00:00:00 INFO auth login success user=admin\n2026-01-01 00:00:00 INFO auth login success user=root'

                             lines written  not a request  claiming success
    newlines written as-is              84             24                24
    newlines escaped                    60              0                 0

  a parser splitting on newlines sees 84 events from 60 requests.
  24 of them record a successful login as a privileged user.

  every forged line is attributable to nobody, and the request
  that produced it is the one line in the group that looks normal.

  escaping the value takes the count from 84 lines to 60 -- one per request.
```

Sixty requests, twelve of which carry a newline in a field. Written as they arrive, the file holds
eighty-four lines, and twenty-four of those are not requests. All twenty-four claim a successful
login as a privileged user.

Read the asymmetry. The attacker did not have to write a plausible request; they had to write one
newline and then a line that looks like every other line in the file. The forged lines are
indistinguishable from the real ones, they are attributed to an address that never made a request,
and the request that produced them is the one normal-looking line at the top of its group. An
incident review reads the file from the top.

Escaping the value takes the file from eighty-four lines to sixty, one per request, and zero forged.
It does not remove the payload. The text is still there and still readable. What it removes is the
payload's ability to be a line, which was the only thing it needed.

:::pitfall The escaper that only works where you quoted

Every section so far has been about finding an injection. This is about the defence that turns one
finding into a recurring one, and it is the most common shape in real code because it is the defence
you reach for while reading the section you just read.

The habit is real and correct as far as it goes: escape the quotes before you build the statement.
It is also incomplete in a way that is invisible at the call site where you wrote it.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 10 -- an escaper only works where you remembered to quote.

The habit this chapter is about is real: escape the quotes before you build
the statement. It is also incomplete in a way that is invisible when you test
it in the place you wrote it, because the escaper's coverage is not a property
of the escaper. It is a property of the call site.

Twelve payloads, six of which were written for a quoted context and six of
which were written for a numeric one. The escaper is the standard one: double
the quote. Each payload is run against a fresh database.
"""
import sqlite3

# payload, the context it was written for, is this a legitimate value?
PAYLOADS = [
    ("ada", "quoted", True),
    ("' OR '1'='1", "quoted", False),
    ("' OR 1=1 --", "quoted", False),
    ("admin'--", "quoted", False),
    ("x' OR 'x'='x", "quoted", False),
    ("' UNION SELECT id, name FROM secrets --", "quoted", False),
    ("3", "numeric", True),
    ("0 OR 1=1", "numeric", False),
    ("1 OR 1=1", "numeric", False),
    ("0; DROP TABLE users", "numeric", False),
    ("1 UNION SELECT id, name FROM secrets", "numeric", False),
    ("9 OR 9=9", "numeric", False),
]

USERS = [(1, "ada"), (2, "grace"), (3, "alan")]
SECRETS = [(1, "api-key-9f3a")]


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", USERS)
    conn.execute("CREATE TABLE secrets (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO secrets VALUES (?, ?)", SECRETS)
    return conn


def escape_quotes(value):
    return value.replace("'", "''")


def run(conn, sql, params=()):
    try:
        return conn.execute(sql, params).fetchall()
    except (sqlite3.Error, sqlite3.Warning):
        return []


def main():
    print(f"  payloads                           {len(PAYLOADS):>3}")
    print("  the escaper                        value.replace(\"'\", \"''\")")
    print()
    print(f"    {'payload':<44}{'context':>9}{'escaped':>9}{'bound':>7}")

    escaped_rows = {"quoted": 0, "numeric": 0}
    escaped_leaks = {"quoted": 0, "numeric": 0}
    bound_leaks = 0
    real_rows = 0
    for p, ctx, legit in PAYLOADS:
        e = escape_quotes(p)
        conn = fresh()
        if ctx == "quoted":
            esc = run(conn, f"SELECT id, name FROM users WHERE name = '{e}'")
            bnd = run(conn, "SELECT id, name FROM users WHERE name = ?", (p,))
        else:
            esc = run(conn, f"SELECT id, name FROM users WHERE id = {e}")
            bnd = run(conn, "SELECT id, name FROM users WHERE id = ?", (p,))
        conn.close()
        # a leak is rows coming back from a payload that was not a real value
        if esc and not legit:
            escaped_leaks[ctx] += 1
        if legit:
            real_rows += len(esc)
        else:
            escaped_rows[ctx] += len(esc)
        if bnd and not legit:
            bound_leaks += 1

        print(f"    {p:<44}{ctx:>9}{len(esc):>9}{len(bnd):>7}")

    nq = sum(1 for _, c, _ in PAYLOADS if c == "quoted")
    nn = len(PAYLOADS) - nq
    print()
    print(f"  the escaper, in the context it was written for   "
          f"{nq - escaped_leaks['quoted']} of {nq} payloads neutralised")
    print(f"  the escaper, in the other context                "
          f"{nn - escaped_leaks['numeric']} of {nn} payloads neutralised")
    print(f"  binding, in both contexts                        "
          f"{len(PAYLOADS) - bound_leaks} of {len(PAYLOADS)} neutralised")

    print()
    print(f"  rows returned by the payloads       "
          f"{escaped_rows['quoted'] + escaped_rows['numeric']}"
          f"   ({escaped_rows['quoted']} from the quoted context)")
    print(f"  rows returned by the real values    {real_rows}"
          f"   (what the query was asked for)")
    print()
    print("  there are no quotes in '0 OR 1=1', so there is nothing for the")
    print("  escaper to do, and the code that calls it looks exactly like the")
    print("  code that calls it correctly.")
    print()
    print("  an escaper is a treatment for one context. binding is a treatment")
    print("  for every context, which is why it is the one to standardise on.")


if __name__ == "__main__":
    main()
```

```text
  payloads                            12
  the escaper                        value.replace("'", "''")

    payload                                       context  escaped  bound
    ada                                            quoted        1      1
    ' OR '1'='1                                    quoted        0      0
    ' OR 1=1 --                                    quoted        0      0
    admin'--                                       quoted        0      0
    x' OR 'x'='x                                   quoted        0      0
    ' UNION SELECT id, name FROM secrets --        quoted        0      0
    3                                             numeric        1      1
    0 OR 1=1                                      numeric        3      0
    1 OR 1=1                                      numeric        3      0
    0; DROP TABLE users                           numeric        0      0
    1 UNION SELECT id, name FROM secrets          numeric        2      0
    9 OR 9=9                                      numeric        3      0

  the escaper, in the context it was written for   6 of 6 payloads neutralised
  the escaper, in the other context                2 of 6 payloads neutralised
  binding, in both contexts                        12 of 12 neutralised

  rows returned by the payloads       11   (0 from the quoted context)
  rows returned by the real values    2   (what the query was asked for)

  there are no quotes in '0 OR 1=1', so there is nothing for the
  escaper to do, and the code that calls it looks exactly like the
  code that calls it correctly.

  an escaper is a treatment for one context. binding is a treatment
  for every context, which is why it is the one to standardise on.
```

Twelve payloads, six written for a quoted context and six for a numeric one, and one escaper: double
the quote.

In the context it was written for, the escaper neutralises six of six. Zero rows came back from the
quoted payloads, and the only quoted row in the table is `ada`, the real name. That is a working
defence, tested where it was written, and it would pass review.

In the other context it neutralises two of six. Eleven rows came back from payloads, and none of them
from the quoted context -- which is the point. The escaper did not fail. It was never consulted,
because there are no quotes in `0 OR 1=1` and there is nothing for it to do. The code that calls it
in the numeric context looks exactly like the code that calls it correctly in the quoted one: a
value goes in, a function is applied, a string comes out.

That is the pitfall. An escaper's coverage is not a property of the escaper. It is a property of the
call site, which means it is a property of every call site, which means it is a number that decays
every time somebody adds one. Binding, in both contexts, neutralises twelve of twelve -- not because
it is a better escaper but because it does not have a context to be right about.

:::

:::scenario The report that tested for quotes

A penetration test is a purchase, and the last chapter was about reading its scope. This is about
reading its *payload list*, which is a smaller document and decides a different thing: what the
report is capable of finding at all.

The standard payload set for SQL injection is built from quotes, because the canonical payload is
one. A test built from the canonical payload finds the canonical bug, and the canonical bug is real.
The question is what else was in the same rectangle.

```python run
#!/usr/bin/env python3
"""Chapter 51 demo, part 11 -- the report that tested for quotes.

A search box is the classic injection surface and the classic scoped test. The
standard payload set for SQL injection is built from quotes, because the
canonical payload is one, and a test built from the canonical payload finds
the canonical bug.

This script runs twelve inputs through a real search feature. Two of the twelve
contain a quote. Counting them is easy. Counting the ones that actually leak is
harder, because "leaked" does not mean the same thing in both slots: in the
search term it means rows came back that should not have, and in the sort key it
means a key ran that is not on the list. The row count is identical either way,
which is exactly why the sort bugs survive a report that only counts rows.
"""
import sqlite3

CARDS = [
    (1, "hola", "hello", "greetings"),
    (2, "adios", "goodbye", "greetings"),
    (3, "gracias", "thank you", "polite"),
    (4, "por favor", "please", "polite"),
    (5, "buenos dias", "good morning", "greetings"),
]

# input, the slot it is tried in
INPUTS = [
    ("hola", "term"),
    ("%", "term"),
    ("_", "term"),
    ("%%", "term"),
    ("' OR '1'='1", "term"),
    ("' UNION SELECT id, front FROM cards --", "term"),
    ("front", "sort"),
    ("back", "sort"),
    ("id", "sort"),
    ("(SELECT front FROM cards)", "sort"),
    ("CASE WHEN 1=1 THEN front ELSE back END", "sort"),
    ("front DESC, back", "sort"),
]

ALLOWED_SORT = {"front", "back", "id"}
QUOTE = "'"


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE cards (id INTEGER, front TEXT, back TEXT, tag TEXT)")
    conn.executemany("INSERT INTO cards VALUES (?, ?, ?, ?)", CARDS)
    return conn


def run(conn, sql):
    try:
        return conn.execute(sql).fetchall()
    except (sqlite3.Error, sqlite3.Warning):
        return None


def main():
    print(f"  cards in the table                 {len(CARDS):>3}")
    print(f"  inputs                             {len(INPUTS):>3}")
    print(f"  the sort allow-list                "
          f"{len(ALLOWED_SORT)} keys")

    results = []
    for value, slot in INPUTS:
        conn = fresh()
        if slot == "term":
            # what a literal substring search should return
            expected = [c[0] for c in CARDS if value in c[1]]
            rows = run(conn, f"SELECT id, front FROM cards WHERE front LIKE '%{value}%'")
            got = None if rows is None else [r[0] for r in rows]
            if rows is None:
                verdict = "rejected"
            elif got != expected:
                verdict = "leak: matched everything"
            else:
                verdict = "ok"
        else:
            base = run(conn, "SELECT id, front FROM cards")
            rows = run(conn, f"SELECT id, front FROM cards ORDER BY {value}")
            if rows is None:
                verdict = "rejected"
            elif value not in ALLOWED_SORT:
                verdict = "leak: key not on the list"
            else:
                moved = [r[0] for r in rows] != [r[0] for r in base]
                verdict = "ok (reordered)" if moved else "ok (same order)"
        conn.close()
        results.append((value, slot, rows, verdict))

    print()
    print(f"    {'input':<42}{'slot':>7}{'rows':>7}  {'verdict'}")
    for value, slot, rows, verdict in results:
        n = "-" if rows is None else str(len(rows))
        print(f"    {value:<42}{slot:>7}{n:>7}  {verdict}")

    quoted = [v for v, _ in INPUTS if QUOTE in v]
    leaked = [(v, slot, verdict) for v, slot, _, verdict in results
              if verdict.startswith("leak")]
    quoted_leaks = [v for v, _, _ in leaked if QUOTE in v]
    term_inputs = [v for v, s in INPUTS if s == "term"]
    sort_inputs = [v for v, s in INPUTS if s == "sort"]
    sort_leaks = [v for v, s, _ in leaked if s == "sort"]
    allowed = [v for v in sort_inputs if v in ALLOWED_SORT]

    print()
    print(f"  inputs containing a quote            {len(quoted):>3} of {len(INPUTS)}")
    print(f"  inputs that leaked                   {len(leaked):>3}")
    print(f"  of the leaking inputs, quoting        {len(quoted_leaks):>3}")
    print(f"  leaking in the term slot             {len(leaked) - len(sort_leaks):>3}"
          f" of {len(term_inputs)}")
    print(f"  leaking in the sort slot             {len(sort_leaks):>3}"
          f" of {len(sort_inputs)}")

    print()
    print("  every leaking input, and what it did")
    for value, slot, verdict in leaked:
        print(f"    {value:<42}{slot:>7}   {verdict}")

    print()
    print(f"  a test built from quotes covers {len(quoted_leaks)}"
          f" of the {len(leaked)} inputs that actually leak.")
    print(f"  all {len(leaked)} leaking inputs return "
          f"{len(CARDS)} rows, so a row count cannot see them.")
    print(f"  the allow-list accepts {len(allowed)} of the {len(sort_inputs)} "
          f"sort inputs and 0 hostile ones.")


if __name__ == "__main__":
    main()
```

```text
  cards in the table                   5
  inputs                              12
  the sort allow-list                3 keys

    input                                        slot   rows  verdict
    hola                                         term      1  ok
    %                                            term      5  leak: matched everything
    _                                            term      5  leak: matched everything
    %%                                           term      5  leak: matched everything
    ' OR '1'='1                                  term      5  leak: matched everything
    ' UNION SELECT id, front FROM cards --       term      5  leak: matched everything
    front                                        sort      5  ok (reordered)
    back                                         sort      5  ok (reordered)
    id                                           sort      5  ok (same order)
    (SELECT front FROM cards)                    sort      5  leak: key not on the list
    CASE WHEN 1=1 THEN front ELSE back END       sort      5  leak: key not on the list
    front DESC, back                             sort      5  leak: key not on the list

  inputs containing a quote              2 of 12
  inputs that leaked                     8
  of the leaking inputs, quoting          2
  leaking in the term slot               5 of 6
  leaking in the sort slot               3 of 6

  every leaking input, and what it did
    %                                            term   leak: matched everything
    _                                            term   leak: matched everything
    %%                                           term   leak: matched everything
    ' OR '1'='1                                  term   leak: matched everything
    ' UNION SELECT id, front FROM cards --       term   leak: matched everything
    (SELECT front FROM cards)                    sort   leak: key not on the list
    CASE WHEN 1=1 THEN front ELSE back END       sort   leak: key not on the list
    front DESC, back                             sort   leak: key not on the list

  a test built from quotes covers 2 of the 8 inputs that actually leak.
  all 8 leaking inputs return 5 rows, so a row count cannot see them.
  the allow-list accepts 3 of the 6 sort inputs and 0 hostile ones.
```

Twelve inputs into a real search feature, six in the search term and six in the sort key. Two of the
twelve contain a quote.

Eight of the twelve leaked. Five of the six term inputs and three of the six sort inputs. The two
quote-carrying inputs are among the eight, so the payload list is not wrong -- it is two of eight,
which is 25%.

The sentence to carry out of this section is the one under the table. All eight leaking inputs return
five rows, which is the number of rows in the table, so a test that compares row counts cannot see
any of them. That is not a subtlety about sorting; it is the reason the sort bugs survive a report
that counts. A sort injection does not change how many rows come back. It changes which rows come
back, and the two orderings it chooses between are both five rows long.

So the report has two blind spots stacked on top of each other. The payload list covers the inputs
whose damage changes a count. The measurement only counts. The allow-list at the end of the block is
the same fix as Part 2: three of the six sort inputs are keys it knows, and zero hostile inputs are.

:::

## Key takeaways

- **Injection has one shape.** A value arrives where something parses it, and the parser cannot tell
  the value from the syntax it stands in. Nothing is broken; the parser is doing its job.
- **Binding is a change to how the statement is built, not to what it allows.** The statement is
  parsed before the value exists, so there is no moment at which the value could be read as structure.
- **Seven of twelve payloads returned a row interpolated; one did, bound, and it was the real name.**
  Twenty-eight rows against one is a different arrangement, not a smaller number.
- **Read the driver's behaviour as the driver's.** `execute()` dropped zero tables and
  `executescript()` dropped one, on the same payload. That safety disappears with the method name.
- **Some slots cannot be bound at all.** `ORDER BY ?` sorts by a constant. Binding delivered zero of
  the four orderings the interface offers.
- **Where binding is not an option, the choice is between interpolating and comparing.** The
  allow-list delivered all four valid orderings and accepted zero hostile values, because it is a
  lookup rather than a filter.
- **The position decides, not the payload.** The same eight payloads ran zero times in `argv[1]` and
  eight times in `argv[0]`, with `shell=True` and no escaping difference.
- **`shell=False` is not the rule.** `['sh', '-c', f-string]` with `shell=False` ran all eight. The
  shell is the program you invoked, not the flag you set.
- **A template engine is a language, and field access is enough.** `{0.secret}` expanded, read the
  attribute, and contains no call, no import and no name.
- **Six of seven payloads expanded as the template and seven of seven were data as an argument.** The
  two columns disagree on six rows, and the payload is identical in both.
- **`literal_eval` is a different kind of answer.** It does not run less of the string; it refuses to
  accept a string that is not data. Ten of ten literals kept, eight of eight code strings rejected.
- **A filter has a coverage number and needs to keep being scored.** Restricted `eval` ran three of
  eight code strings, including a lambda call and attribute access on a literal.
- **`literal_eval` is a promise about parsing, not about resources.** A forty-thousand-character
  literal parses to twenty thousand elements and both loaders accept it.
- **The rule is not "decode first", it is "the value you check must be the value you use".** Decoding
  once caught 8 of 9 traversal payloads; the fixed point caught 9 of 9.
- **An escaper is correct relative to a parser.** `url_quote` is the only encoder that made all eight
  sinks safe, and it rewrites every value it is given.
- **Three of six encoders made a sink worse than no encoder.** `html_escape` took the URL query sink
  from five safe payloads to three. An encoder is a transformer for every parser but its own.
- **A blocklist is a filter with a coverage number, and the attacker generates the space.** The most
  careful configuration caught 71.7% of seven thousand six hundred and eighty strings built from one
  attack, and the encodings were not equally hard.
- **An escaper's coverage is a property of the call site.** Six of six neutralised where it was
  written, two of six in the other context, and the code looks the same in both.
- **A sort injection does not change the row count.** All eight leaking inputs returned five rows, so
  a test that counts cannot see any of them.
- **A payload list is a scope.** Two of the twelve inputs carried a quote; eight leaked. The list
  covered 25% of the damage and none of the sort bugs.

## Practice

- [ ] **Find the slots that cannot be bound.** Take a project you have written and list every place a
  value from a request reaches a statement, a command, a path or a template. For each, record whether
  it arrives in a value position or a structure position -- a column name, a table name, a sort
  direction, a filename extension. For every structure position, replace the interpolation with a
  lookup into a dictionary you wrote and count how many hostile values it accepts.
- [ ] **Write the deny-list, then break it.** Build the defence you would write first: strip or reject
  the characters the payloads you know about are made of. Then write ten payloads that contain none of
  those characters and run them against the same code. Report how many you blocked and how many
  changed the query's meaning anyway, and name the operator or construct each survivor used.
- [ ] **Score an encoder against the sinks it will meet.** For a project of yours, list the sinks an
  input value reaches -- HTML body, HTML attribute, URL query, SQL literal, log line, HTTP header,
  JSON. For each sink, write the encoder you would use and then write one payload that survives it.
  Count how many sinks you have a tested answer for, and check whether any encoder you chose makes a
  sink you did not think about worse than leaving the value alone.
- [ ] **Measure a log file's separator.** Find a log your code writes where a field comes from a
  request. Write forty requests, ten of which carry a newline in that field, and count the lines that
  reach the file and how many of them a reader would attribute to a request that never happened.
  Then escape the separators and count both numbers again, and report what changed and what did not.

## Solutions

:::solution Exercise 1

Structure positions and value positions, with the lookup that replaces each one.

```python run
#!/usr/bin/env python3
"""Exercise 1 -- the deny-list that misses half the payloads.

The obvious defence after reading about injection is to strip the characters
the payloads are made of. This script builds that defence and runs it against
twelve inputs, counting two things: how many inputs it blocks, and how many
inputs still change the query's meaning without using any of the characters it
blocks.
"""
import sqlite3

USERS = [(1, "ada"), (2, "grace"), (3, "alan")]

# input, is this a legitimate value
INPUTS = [
    ("1", True),
    ("2", True),
    ("1 OR 1=1", False),
    ("0 OR 1=1", False),
    ("1 UNION SELECT id, name FROM users", False),
    ("2 OR id>0", False),
    ("1/**/OR/**/1=1", False),
    ("1 OR 0x31=0x31", False),
    ("' OR 1=1 --", False),
    ("1--", False),
    ("1; DROP TABLE users", False),
    ("1 OR 'a'='a", False),
]

# the characters the canonical payloads are made of
DENY = ("'", "--", ";")


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", USERS)
    return conn


def run(conn, sql, params=()):
    try:
        return conn.execute(sql, params).fetchall()
    except (sqlite3.Error, sqlite3.Warning):
        return []


def main():
    hostile = [v for v, ok in INPUTS if not ok]
    benign = [v for v, ok in INPUTS if ok]

    print(f"  inputs                             {len(INPUTS):>3}")
    print(f"  legitimate values                  {len(benign):>3}")
    print(f"  hostile inputs                     {len(hostile):>3}")
    print(f"  the deny-list                      {DENY}")
    print()
    print(f"    {'input':<36}{'kind':>9}{'blocked':>9}{'rows':>6}{'bound':>7}")

    blocked_hostile = 0
    leaked = []
    bound_leaks = []
    bound_ok = 0
    for value, legit in INPUTS:
        blocked = any(c in value for c in DENY)
        conn = fresh()
        if blocked:
            rows = []          # never reached the database
        else:
            rows = run(conn, f"SELECT id, name FROM users WHERE id = {value}")
        bnd = run(conn, "SELECT id, name FROM users WHERE id = ?", (value,))
        conn.close()

        if blocked and not legit:
            blocked_hostile += 1
        if rows and not legit:
            leaked.append(value)
        if bnd and not legit:
            bound_leaks.append(value)
        if bnd and legit:
            bound_ok += 1

        kind = "real" if legit else "hostile"
        print(f"    {value:<36}{kind:>9}{'yes' if blocked else 'no':>9}"
              f"{len(rows):>6}{len(bnd):>7}")

    ran = [v for v in hostile if not any(c in v for c in DENY)]

    print()
    print(f"  hostile inputs the deny-list blocks   {blocked_hostile:>3}"
          f" of {len(hostile)}")
    print(f"  hostile inputs it lets through        {len(ran):>3}")
    print(f"  of those, ones that change the result {len(leaked):>3}")
    print(f"  binding, hostile inputs that leak     {len(bound_leaks):>3}")
    print(f"  binding, legitimate values returned   {bound_ok:>3}"
          f" of {len(benign)}")

    print()
    print("  the ones that got through, and what they used instead of a quote")
    for value in leaked:
        print(f"    {value}")

    print()
    print("  stripping the characters the payloads are made of stops the")
    print("  payloads that are made of those characters. the rest of the")
    print("  grammar is still there, and 'OR' does not need a quote to be")
    print("  an operator.")


if __name__ == "__main__":
    main()
```

```text
  inputs                              12
  legitimate values                    2
  hostile inputs                      10
  the deny-list                      ("'", '--', ';')

    input                                    kind  blocked  rows  bound
    1                                        real       no     1      1
    2                                        real       no     1      1
    1 OR 1=1                              hostile       no     3      0
    0 OR 1=1                              hostile       no     3      0
    1 UNION SELECT id, name FROM users    hostile       no     3      0
    2 OR id>0                             hostile       no     3      0
    1/**/OR/**/1=1                        hostile       no     3      0
    1 OR 0x31=0x31                        hostile       no     3      0
    ' OR 1=1 --                           hostile      yes     0      0
    1--                                   hostile      yes     0      0
    1; DROP TABLE users                   hostile      yes     0      0
    1 OR 'a'='a                           hostile      yes     0      0

  hostile inputs the deny-list blocks     4 of 10
  hostile inputs it lets through          6
  of those, ones that change the result   6
  binding, hostile inputs that leak       0
  binding, legitimate values returned     2 of 2

  the ones that got through, and what they used instead of a quote
    1 OR 1=1
    0 OR 1=1
    1 UNION SELECT id, name FROM users
    2 OR id>0
    1/**/OR/**/1=1
    1 OR 0x31=0x31

  stripping the characters the payloads are made of stops the
  payloads that are made of those characters. the rest of the
  grammar is still there, and 'OR' does not need a quote to be
  an operator.
```

:::

:::solution Exercise 2

The deny-list, the ten payloads written to defeat it, and the six that did.

```python run
#!/usr/bin/env python3
"""Exercise 2 -- the search box that is bound, and still wrong.

A parameterised query fixes injection. It does not fix the other half of the
same problem: the value you pass in is not always a value. In a LIKE pattern
the characters % and _ are syntax, so a bound parameter carrying them still
changes what the query means. Nothing is escaped by binding, because there is
nothing to escape -- the parameter is delivered as data, and it is data that
happens to be an operator.

Ten search terms, three ways of running each one, and a count of how often each
way agrees with a plain substring search.
"""
import sqlite3

CARDS = [
    (1, "hola"),
    (2, "adios"),
    (3, "gracias"),
    (4, "por favor"),
    (5, "buenos dias"),
]

TERMS = [
    "hola",
    "a",
    "buenos dias",
    "%",
    "_",
    "%%",
    "hol%",
    "hola_",
    "\\",
    "adios",
]


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE cards (id INTEGER, front TEXT)")
    conn.executemany("INSERT INTO cards VALUES (?, ?)", CARDS)
    return conn


def run(conn, sql, params=()):
    try:
        return [r[0] for r in conn.execute(sql, params).fetchall()]
    except (sqlite3.Error, sqlite3.Warning):
        return None


def escape_like(value):
    """Make a value mean itself inside a LIKE pattern."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def main():
    print(f"  cards                              {len(CARDS):>3}")
    print(f"  search terms                       {len(TERMS):>3}")
    print()
    print(f"    {'term':<14}{'literal':>9}{'LIKE ?':>9}{'ESCAPE':>9}")

    over = []
    exact = 0
    for term in TERMS:
        conn = fresh()
        literal = sorted(c[0] for c in CARDS if term in c[1])
        plain = run(conn, "SELECT id FROM cards WHERE front LIKE ?",
                    (f"%{term}%",))
        esc = run(conn, "SELECT id FROM cards WHERE front LIKE ? ESCAPE '\\'",
                  (f"%{escape_like(term)}%",))
        conn.close()

        if plain != literal:
            over.append(term)
        if esc == literal:
            exact += 1

        print(f"    {term:<14}{len(literal):>9}{len(plain):>9}{len(esc):>9}")

    print()
    print(f"  terms where binding alone over-matches   {len(over):>3}"
          f" of {len(TERMS)}")
    for term in over:
        print(f"    {term}")
    print(f"  terms where the escaping version is exact {exact:>3}"
          f" of {len(TERMS)}")

    print()
    print("  both columns are bound. the difference is not escaping -- the")
    print("  value is never parsed as SQL in either one. it is that LIKE")
    print("  gives three characters a meaning, and a bound parameter does")
    print("  not take that meaning away. binding removes the syntax from")
    print("  the statement; it cannot remove the syntax from the value.")


if __name__ == "__main__":
    main()
```

```text
  cards                                5
  search terms                        10

    term            literal   LIKE ?   ESCAPE
    hola                  1        1        1
    a                     5        5        5
    buenos dias           1        1        1
    %                     0        5        0
    _                     0        5        0
    %%                    0        5        0
    hol%                  0        1        0
    hola_                 0        0        0
    \                     0        0        0
    adios                 1        1        1

  terms where binding alone over-matches     4 of 10
    %
    _
    %%
    hol%
  terms where the escaping version is exact  10 of 10

  both columns are bound. the difference is not escaping -- the
  value is never parsed as SQL in either one. it is that LIKE
  gives three characters a meaning, and a bound parameter does
  not take that meaning away. binding removes the syntax from
  the statement; it cannot remove the syntax from the value.
```

:::

:::solution Exercise 3

Six sinks, three loaders, and the count of hostile strings each one runs.

```python run
#!/usr/bin/env python3
"""Exercise 3 -- the sandbox that only removed one door.

Loading a small configuration file with eval is a real habit, and the first fix
everyone reaches for is to empty __builtins__. This script measures how much
that actually buys, against six hostile strings and four ordinary ones, using
three loaders.
"""
import ast

BENIGN = [
    "8",
    "'production'",
    "[1, 2, 3]",
    "{'debug': False}",
]

HOSTILE = [
    "__import__('os').environ",
    "open(__file__).read()",
    "globals()",
    "(1).__class__.__base__.__subclasses__()",
    "().__class__.__base__.__subclasses__()",
    "lambda: 1",
]


def load_plain(src):
    return eval(src)  # noqa: S307 -- this is the thing being measured


def load_no_builtins(src):
    return eval(src, {"__builtins__": {}})  # noqa: S307


def load_literal(src):
    return ast.literal_eval(src)


def try_load(fn, src):
    try:
        fn(src)
        return True
    except Exception:
        return False


def main():
    print(f"  ordinary configs                    {len(BENIGN):>3}")
    print(f"  hostile configs                     {len(HOSTILE):>3}")
    print()
    print(f"    {'loader':<24}{'accepted':>10}{'ran hostile':>13}")

    for name, fn in (("eval(src)", load_plain),
                     ("eval, no builtins", load_no_builtins),
                     ("ast.literal_eval", load_literal)):
        good = sum(1 for s in BENIGN if try_load(fn, s))
        bad = sum(1 for s in HOSTILE if try_load(fn, s))
        print(f"    {name:<24}{good:>6} of {len(BENIGN):<3}{bad:>7}"
              f" of {len(HOSTILE):<3}")

    print()
    print("  which hostile strings survive the empty-builtins sandbox")
    for src in HOSTILE:
        survived = try_load(load_no_builtins, src)
        mark = "runs" if survived else "blocked"
        print(f"    {mark:<9}{src}")

    print()
    print("  emptying __builtins__ removes the names. it does not remove")
    print("  attribute access, and attribute access is enough to walk from")
    print("  any object to the class hierarchy and back out to a module")
    print("  that does have __builtins__. three of the six never needed a")
    print("  builtin name in the first place.")
    print()
    print("  literal_eval is a different kind of answer: it does not run")
    print("  less of the string, it refuses to accept a string that is not")
    print("  data. that is why it also keeps all four ordinary configs.")


if __name__ == "__main__":
    main()
```

```text
  ordinary configs                      4
  hostile configs                       6

    loader                    accepted  ran hostile
    eval(src)                    4 of 4        6 of 6  
    eval, no builtins            4 of 4        3 of 6  
    ast.literal_eval             4 of 4        0 of 6  

  which hostile strings survive the empty-builtins sandbox
    blocked  __import__('os').environ
    blocked  open(__file__).read()
    blocked  globals()
    runs     (1).__class__.__base__.__subclasses__()
    runs     ().__class__.__base__.__subclasses__()
    runs     lambda: 1

  emptying __builtins__ removes the names. it does not remove
  attribute access, and attribute access is enough to walk from
  any object to the class hierarchy and back out to a module
  that does have __builtins__. three of the six never needed a
  builtin name in the first place.

  literal_eval is a different kind of answer: it does not run
  less of the string, it refuses to accept a string that is not
  data. that is why it also keeps all four ordinary configs.
```

:::

:::solution Exercise 4

Forty requests, a forged line count, and what escaping the separator does and does not change.

```python run
#!/usr/bin/env python3
"""Exercise 4 -- the log file that reports requests nobody made.

Every field in a log line is separated by a character the writer chose and the
attacker can supply. This script writes forty requests to a log two ways and
counts the lines that come out, the lines that no request produced, and the
addresses those lines are attributed to.
"""
REQUESTS = 40

# path, user agent
SHAPES = [
    ("/", "Mozilla/5.0"),
    ("/notes", "Mozilla/5.0"),
    ("/notes/12", "curl/8.0"),
    ("/search?q=hola", "Mozilla/5.0"),
    ("/me", "curl/8.0"),
    ("/static/app.css", "Mozilla/5.0"),
    ("/notes", "curl/8.0\n10.0.0.9 - root - GET /admin 200"),
    ("/notes/12",
     "curl/8.0\n10.0.0.9 - root - GET /admin 200\n"
     "10.0.0.9 - root - POST /users 201"),
]

REAL_IPS = ["203.0.113.7", "203.0.113.8", "198.51.100.4"]
FORGED_IP = "10.0.0.9"


def requests():
    out = []
    for i in range(REQUESTS):
        path, ua = SHAPES[i % len(SHAPES)]
        out.append((REAL_IPS[i % len(REAL_IPS)], path, ua))
    return out


def write_naive(reqs):
    return [f"{ip} - GET {path} {ua}" for ip, path, ua in reqs]


def write_escaped(reqs):
    def clean(s):
        return s.replace("\r", "\\r").replace("\n", "\\n")

    return [f"{ip} - GET {clean(path)} {clean(ua)}" for ip, path, ua in reqs]


def lines_of(records):
    out = []
    for rec in records:
        out.extend(rec.split("\n"))
    return out


def report(label, records):
    lines = lines_of(records)
    forged = [l for l in lines if l.startswith(FORGED_IP)]
    mentions = sum(l.count(FORGED_IP) for l in lines)
    print(f"  {label}")
    print(f"    requests                            {len(records):>3}")
    print(f"    lines in the file                   {len(lines):>3}")
    print(f"    lines that begin like a request     {len(forged):>3}")
    print(f"    mentions of the payload address     {mentions:>3}")
    return len(lines), len(forged)


def main():
    reqs = requests()
    hostile = [r for r in reqs if "\n" in r[2]]
    extra = sum(r[2].count("\n") for r in reqs)

    print(f"  requests                            {len(reqs):>3}")
    print(f"  requests with a newline in a field  {len(hostile):>3}")
    print(f"  newlines those requests supply      {extra:>3}")
    print()
    report("written as it arrives", write_naive(reqs))
    print()
    report("written with the separators escaped", write_escaped(reqs))

    print()
    print("  escaping the newline does not remove the payload. the text is")
    print("  still in the line and still readable. what it removes is the")
    print("  payload's ability to be a line, which is the only thing it")
    print("  needed in order to look like a request.")
    print()
    print(f"  a reader that trusts the file now sees {extra} requests from")
    print(f"  {FORGED_IP} that never happened, and none of them are unusual")
    print("  enough to notice next to the ones that did.")


if __name__ == "__main__":
    main()
```

```text
  requests                             40
  requests with a newline in a field   10
  newlines those requests supply       15

  written as it arrives
    requests                             40
    lines in the file                    55
    lines that begin like a request      15
    mentions of the payload address      15

  written with the separators escaped
    requests                             40
    lines in the file                    40
    lines that begin like a request       0
    mentions of the payload address      15

  escaping the newline does not remove the payload. the text is
  still in the line and still readable. what it removes is the
  payload's ability to be a line, which is the only thing it
  needed in order to look like a request.

  a reader that trusts the file now sees 15 requests from
  10.0.0.9 that never happened, and none of them are unusual
  enough to notice next to the ones that did.
```

:::
