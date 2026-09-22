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

<<BLOCK:sql_injection>>

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

<<BLOCK:order_by>>

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

<<BLOCK:command_injection>>

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

<<BLOCK:format_ssti>>

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

<<BLOCK:eval_literal>>

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

<<BLOCK:normalise_order>>

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

<<BLOCK:sink_encoding>>

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

<<BLOCK:payload_space>>

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

<<BLOCK:log_injection>>

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

<<BLOCK:pitfall>>

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

<<BLOCK:scenario>>

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

<<BLOCK:sol1>>

:::

:::solution Exercise 2

The deny-list, the ten payloads written to defeat it, and the six that did.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

Six sinks, three loaders, and the count of hostile strings each one runs.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

Forty requests, a forged line count, and what escaping the separator does and does not change.

<<BLOCK:sol4>>

:::
