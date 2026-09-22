---
chapter: 53
part: 9
title: Web Security
summary: The same mistakes as the last two chapters, in the one place where you control neither end -- a browser, a session, and a set of services you did not write. Eleven blocks counting what each defence actually covers, including three checks that are enforced and measuring the wrong quantity, and one feature that makes six of the mistakes at once.
minutes: 100
tags: [security, XSS, escaping contexts, CSRF, SameSite, SSRF, open redirect, IDOR, sessions, timing attacks, secrets, supply chain, logging, OWASP]
---

The last two chapters were about a value that arrives where something parses it, and about formats
that rebuild an object, a path or a length from their content. Both of them assumed you were the one
holding both ends: you wrote the query, you wrote the reader, and the question was what you did with
what arrived.

This chapter is the same set of mistakes in the place where you hold neither end. There is a browser
that runs the page and does not tell you what it did with it. There is a session that is a promise
about the future. There are services you call and services you install, and a log that is read by
somebody who was not there.

Nothing here is a new mechanism. Everything here is one of the two mechanisms you already have --
something parsed a value as syntax, or something reconstructed an object from a value -- with the
difference that the parser is not yours, or the value came from a party who has an interest in what
happens next.

## The parser you do not run

A page is built by concatenating strings, and the browser then parses the result. The escaping
question is therefore not "which characters are dangerous" but "which parser is about to read this
value", and there is more than one parser in a single document.

<<BLOCK:html_parse>>

Four contexts, six payloads, and the same escaper applied to all of them. Raw, it broke out of 8 of
the 24 renders. Escaped, it broke out of 2 -- and both of the two are in the same context.

That context is an unquoted attribute, and the reason is worth stating precisely rather than as a
rule of thumb. `html.escape` turns `<`, `>`, `&` and the quote characters into entities. In an
element body and in a quoted attribute, those are exactly the characters that would end the string
the value is sitting inside. In an unquoted attribute there is no string to end, so the payload does
not need a quote at all: it needs a space, and a space is not one of the four characters an HTML
escaper escapes.

The fix for that context is not a stronger encoder. It is a pair of quotes, and the encoder on top of
them -- which is the general shape. The escaper is the second decision. The first one is where the
value goes, and a value that goes into an unquoted attribute has no escaper that would have saved it.

## A request your server cannot tell from any other

An HTTP request arrives with a cookie attached, and the server has no way to know which page caused
the browser to send it. That is the whole of the cross-site request forgery problem, and the modern
answer is a cookie attribute rather than a token.

<<BLOCK:same_site>>

Eight request shapes against three settings. `None` sent the cookie on all eight, `Lax` on three, and
`Strict` on two. The interesting column is `Lax`, and the interesting number inside it is one.

`Lax` held the cookie on five of the six cross-site shapes and sent it on one: a top-level navigation
with a safe method. That exception is not a gap in the setting, it is the reason the setting exists --
following a link to a page you are already logged in to has to work, or the web stops working. What
it means for your code is that "state changes must not be GETs" stops being a matter of taste and
becomes the rule that keeps the exception from being reachable by an attacker.

`None` is worth reading correctly too, because it is the setting you end up with the moment a cookie
has to work inside an iframe or across origins. It sent on all eight. It is not a weaker `Lax`; it is
the absence of the protection, and the thing doing the work is whatever else you built.

## The server that fetches what you tell it

The next three sections are about a value that becomes a *destination* rather than an argument, and
the check that is supposed to bound it. The first one is the server making an outbound request to a
URL a user supplied.

<<BLOCK:ssrf_allowlist>>

Sixteen URLs, fourteen of which should be refused, against an allow-list holding one hostname. The
four validators accept 3, 3, 2 and 0 of the hostile ones, and the useful reading is that the three
accepted lists are not three attempts at the same thing. Each one removes a class the one above it
missed, and the classes are different in kind.

`startswith` accepts three, and all three are the string beginning with the allowed host without the
host being that host: a longer name that starts with it, a userinfo section that is it, and a
trailing dot that makes it a different name. `endswith` accepts three as well, and they are not the
same three -- it drops the userinfo and the trailing dot, and picks up a domain that ends with the
allowed one without a dot in front of it, plus two URLs whose scheme is not https at all. A hostname
check is not a scheme check.

Comparing the hostname drops the suffix case and still accepts the two wrong schemes, which is what
the fourth validator is for. It checks the scheme and the hostname, and then asks what the hostname
is if it happens to be an address. Nothing in this block resolves anything, so it is the shape of the
check rather than the whole of it. But the shape is the point: a check on the name is not a check on
where the connection goes.

## The redirect that leaves your site

A redirect is a second URL, and it is usually built from something the request supplied -- a `next`
parameter, a return-to path, a language code. If the value is a URL and the code only checks that it
starts with a slash, the check has a set of members and the set has members you did not intend.

<<BLOCK:open_redirect>>

Twelve targets, nine of which should be refused, against three checks. The first accepts 4, the second
accepts 7, and the third accepts 1.

The second is the one to look at, because it is the check that looks correct and is not. It parses
the URL and asks whether the netloc is empty. `urlparse` leaves the netloc empty for anything it does
not recognise as a host -- a backslash, a scheme with no slashes, a triple slash -- and an empty
netloc is exactly what the check is looking for. It accepts more than the check it replaced.

The third accepts one, and the one it accepts is the percent-encoded target. Nothing here decodes,
and the browser does before it follows, which turns it back into a protocol-relative URL. That is the
same lesson as the first section one layer down: the check has to know which characters the consumer
treats as separators, and the consumer is the browser rather than the parser you happened to use.

## Two questions, and only one of them gets asked

Authentication is whether you are who you say. Authorization is whether you are allowed to do this,
to *this thing*. Almost every access-control bug is the first question being answered and the second
one not being asked, and the shape of the mistake is that the check is on the route while the data is
in the row.

<<BLOCK:idor>>

Four endpoints, three callers, twelve pairs. Four pairs end with a caller holding data that is not
theirs, and one of the four endpoints is not among them.

That endpoint is the one somebody wrote while looking at it. The other three ask whether there is a
session, which is a real question and a different one. The most useful row is the list endpoint,
because its guard is *correct* -- it does require a session -- and it still leaks. The question is
not only whether you may call this, it is also which rows the answer may contain, and those are two
checks in two different places.

The last count is what the fix costs. One guard, applied where the rows are read rather than where
the route is declared, takes four leaking pairs to none, and it is the same move as putting the rule
at the repository instead of at the handler.

## A session is a claim about the future

A session cookie is a promise that whoever holds this string is that user, for as long as the server
honours it. Everything that makes the promise wrong is a moment when the server's answer should
change and does not.

<<BLOCK:session_fixation>>

Five attacks against four settings, and the count of attacks that still work goes 5, 4, 3, 1. Each
column removes one, and the row that survives every column is the one worth finding.

It is a password change. Nothing in the settings list is about it, because it is not a session event
at all -- it is a different route, and no amount of care in the session code reaches it. The fix is
to invalidate every session for the account when the credential changes, which is a line in the
password route and not in this one.

The token generator underneath is the other half. Every row that can be measured is 1000 distinct out
of 1000, and the first two rows are an attacker reproducing every id without ever having seen one,
because the id is a function of something smaller than the id. Uniqueness is the property people test
for, and it is not the property that matters.

## The comparison that answers more than yes

The last of the destination-shaped problems is a comparison that leaks how far it got.

<<BLOCK:timing_compare>>

A 28-byte secret, 256 candidates per position, 7168 probes per attack, run against two comparisons.
Both were probed the same number of times. The difference is not the cost of the attack; it is what a
probe tells you. The early-exit comparison produced a number that varies with the position, and the
constant one produced the same number for all of them.

The early-exit comparison recovered 27 of the 28 bytes, and the byte it missed is the last one,
because there is no byte after it to differ at. A wrong guess at the final position examines the same
number of bytes as a right one, so nothing ranks them. That is a property of the method rather than
of the comparison -- append a byte to the guess and the last position becomes recoverable like the
others.

The second count is the one that matters. The constant comparison recovered zero bytes, not because
it is hard to break, but because every wrong guess looks exactly like every other wrong guess. The
standard library's version is `hmac.compare_digest`, written in C so that no interpreter detail can
reintroduce the early exit. Reach for it rather than writing one.

## The file that must not be in the repository

Everything so far has been about a value arriving. This is about a value that should never have been
there, and about the fact that finding it is a detection problem rather than a design one.

<<BLOCK:secret_scan>>

Twelve config lines, six of which really carry a credential, against three detectors. The prefix
detector found 2 of the 6 and raised 0 false alarms. The keyword detector found 3 and raised 1. The
entropy detector found 5 and raised 3. The union found all 6 and cost 4.

The three are not three attempts at the same thing; they read different parts of the line. The prefix
detector reads the value and knows a handful of formats, which is why its precision is perfect and
its recall is the worst of the three -- a format it does not have written down is invisible to it,
and the formats are issued by whoever runs the service.

The keyword detector reads the name and not the value at all. One of the three it misses is
`WEBHOOK_URL`, a credential whose name describes what it is for rather than what it is, and the name
is chosen by whoever wrote the config. The other two have "key" in the name: the list holds `api key`
and not `key`, because a bare `key` flags every config file that has one. The detector is exactly as
wide as the words somebody chose.

The entropy detector reads the value and knows nothing about formats or names. It found 5 of the 6
and flagged 3 of the 6 that are not credentials, because a build hash is a random string and so is a
key. It is the only one that finds a credential nobody has seen before, and the only one that cannot
tell one from a checksum. The one it misses is a password whose value is a word, which is what a
password a person chose looks like.

The union finds all six and costs four false alarms, and what all three depend on is the same thing:
a corpus somebody chose. That is the blocklist argument from the injection chapter, and it ends the
same way. Detection is a backstop for a credential that has already leaked. The fix is that it was
never in the file.

## What runs when you install

The last section before the callouts is the one where the code you are responsible for is not the
code you wrote.

<<BLOCK:supply_chain>>

The first table is the size of the surface you did not choose. Five published versions of three
packages is 125 distinct sets of versions a fresh install can land on. A major-version constraint
takes it to 27, pinning one package to 25, and pinning all three to 1.

The last two rows have the same number and are not the same thing. A version is a name the publisher
chooses and can move; a hash is the bytes. Pinning every version narrows the surface to one and still
installs whatever is served under that version, which is why the row above it is the same number with
a different answer in the last column.

The second table is what happens at install. Four of the six steps run code the package author wrote,
and none of them ask. The two that do not are the two that install a built artefact or check a
checksum, and that is the only reason they are different.

The third is a name check, and it is the part that generalises. A check that flags anything within
one edit of a name you already use caught 7 of 11. The misses are two kinds: names that keep the name
you know and change the part after it, which are the more convincing ones because they look like an
edition of something already in your file; and a transposition, which is two edits rather than one,
so the check misses the single most common typo there is. A blocklist of known-bad names would catch
none of them, because every one of them was fine on the day it was written.

:::pitfall The log that is a copy of the request

Every section so far has had a defence. This one is the category where the defence is a decision
rather than a mechanism, and it is the last of the OWASP top ten for that reason.

A service logging ten event types over sixty requests.

<<BLOCK:a09_logging>>

Two numbers, and they are opposite problems in the same file. 32 of the 54 lines written carry a
credential, because the line is built from the request body and the request body is where the
password is. And 6 of the 29 requests an incident review would need produced no line at all.

The log is the most copied artefact in an incident and the least protected one in most systems, which
is why the first number is the one that gets fixed. The second is the one that matters more. The
events with no line are a refusal, a role change and a lockout -- the events that describe an attack
-- and they are missing because nobody decided they should be there. A successful request is what the
log was built to record, and an attack is made of the ones that failed.

The fix for the first is a field allow-list rather than a body dump. The fix for the second is a list
of events that must always produce a line, written down and tested like any other requirement. That
second list is the whole of the category, and it is also why the category has no syntax-level fix:
nothing in the code is wrong, and the thing that is missing is missing from the output you would
check it against.

:::

:::scenario The password reset link

A reset link is the feature to end on, because it is small, it is in every application, and it walks
through most of this chapter on its own. It takes an address, mails a token, accepts the token back,
lets the holder set a new password, and redirects them somewhere afterwards.

Six mistakes are available to it, and they are in six different places.

<<BLOCK:scenario>>

Four designs. The first makes all six. Adding a constant-time comparison takes it to five; adding a
single-use token and invalidating the sessions takes it to three; and the last one, which also makes
the reply uniform, restricts the redirect target and allow-lists the logged fields, reaches zero.

Read the columns as places rather than as strengths. The comparison is in the comparison, the
single-use token is in the token store, the invalidation is in the session store, the uniform reply
is in the handler, the redirect target is in the redirect, and the logged fields are in the logger. A
review that reads one file finds the mistakes that happen to be in that file, and a feature is the
unit that reaches all of them.

The comparison evidence underneath is the part that is measured rather than counted. Sixteen
single-byte-wrong guesses, and the early-exit comparison takes sixteen different numbers of bytes to
answer them while the constant one takes one. The reply is still only yes or no. What leaked was the
work behind it, which is the same shape as the timing section and the same shape as the blocklist:
the thing that is observable is not the thing you were thinking about.

:::

## Key takeaways

- **The escaping question is which parser reads the value, not which characters are dangerous.** Four
  contexts, one escaper, 8 of 24 renders broken raw and 2 of 24 broken after escaping.
- **`html.escape` escapes the four characters that end a string.** In an unquoted attribute there is
  no string to end, so the payload needs a space, and a space is not one of the four.
- **The fix for an unquoted attribute is a pair of quotes, not a stronger encoder.** Where the value
  goes is the first decision; the escaper is the second one.
- **`SameSite=Lax` sends on exactly one cross-site shape: a top-level navigation with a safe method.**
  That exception is why state changes must not be GETs.
- **`SameSite=None` is not a weaker `Lax`.** It sent on all eight shapes. It is the absence of the
  protection, and something else is doing the work.
- **A check on the name is not a check on where the connection goes.** Three string checks accepted 3,
  3 and 2 of fourteen hostile URLs, and each removed a class of a different kind.
- **A hostname check is not a scheme check.** Two of the URLs the hostname comparisons accepted used
  schemes that were not https at all.
- **The check that looks correct is the one to test.** Asking whether `urlparse` found a netloc
  accepted 7 of 9 hostile targets -- more than the check it replaced, because an unrecognised URL
  leaves the netloc empty.
- **A validator has to know what the consumer treats as a separator.** The percent-encoded target was
  accepted by every check here and decoded by the browser.
- **Authentication and authorization are two questions, and only one of them is usually asked.** Four
  of twelve endpoint-and-caller pairs leaked, and one leaking endpoint had a correct guard.
- **A correct guard can still leak.** A list endpoint that requires a session and returns every row is
  a leak; the question is which rows the answer may contain, and that check lives where the rows are
  read.
- **A password change is not a session event, and it has to be.** Five attacks, four settings, and the
  one that survives all four settings is the one that is not in the session code.
- **Uniqueness is not unpredictability.** Every token generator measured was 1000 distinct out of
  1000, and a counter and a seeded PRNG were both reproduced in full by an attacker who never saw one.
- **An early-exit comparison recovered 27 of 28 bytes.** It misses the last one because there is no
  byte after it to differ at -- a property of the method, and appending a byte makes it recoverable.
- **A constant comparison recovered zero, and that is the point.** Every wrong guess looks like every
  other wrong guess, so there is nothing to rank them by. Use `hmac.compare_digest`.
- **Detection is not prevention, and it is still worth measuring.** Three secret detectors found 2, 3
  and 5 of six real credentials, at a cost of 0, 1 and 3 false alarms.
- **A detector is exactly as wide as the words somebody chose.** The keyword list held `api key` and
  not `key`, and the name of a credential is chosen by whoever wrote the config.
- **125 sets of versions become 27, then 25, then 1, and the last two rows are not the same thing.** A
  version is a name the publisher can move; a hash is the bytes.
- **Four of six install steps run code the package author wrote, and none of them ask.** The two that
  do not are the two that install a built artefact or check a checksum.
- **A log built from the request body is a copy of the request.** 32 of 54 lines carried a credential,
  and 6 of the 29 requests an incident would need produced no line at all -- including every refusal.

## Practice

- [ ] **Test an escaper by context rather than by character.** Take a page in a project of yours and
  find every place a user-supplied value is rendered. Classify each one by the parser that reads it:
  element body, quoted attribute, unquoted attribute, URL, JavaScript string, CSS, a header. Then
  write six payloads per context and record which of them break out. Report the number of contexts
  your current escaper covers, and the ones it does not -- the answer is usually that it covers the
  two you thought of.
- [ ] **Walk a redirect parameter to the end.** Find a `next`, `return_to` or `redirect_uri`
  parameter in a project of yours. Collect twelve values it should refuse, including a
  protocol-relative URL, a backslash form, a percent-encoded form, a scheme with no slashes and a
  value that is a valid URL to a host that merely starts with yours. Run them through the check, then
  through the check after decoding the value the way the consumer will. Report how many each version
  accepts, and name the consumer you assumed.
- [ ] **Count the places one feature asks about identity.** Take the feature with the most endpoints
  in a project of yours -- a resource with a list, a detail, a nested child and a bulk read. For each
  endpoint, write down the question its guard asks and the question its query answers. Then write a
  test that calls each endpoint as a second user and as an anonymous caller, and report the number of
  pairs where a caller receives data that is not theirs. Fix one endpoint by moving the rule from the
  route to the query and report the number again.
- [ ] **Write the list of events that must leave a trace.** For a project of yours, list every event
  that an incident review would ask about: every refusal, every privilege change, every credential
  change, every lockout, every export. Then list every event that currently writes a line. Report the
  events in the first list and not the second -- that number is the gap, and it is invisible in the
  output because the output is what you would check it against. Then add the missing lines and
  confirm each one carries a named field rather than a request body.

## Solutions

:::solution Exercise 1

Three rendering contexts, four escapers, and the two questions that are not the same question.

<<BLOCK:sol1>>

:::

:::solution Exercise 2

Five ways to reach an address inside, and four validators whose only difference is when the question
is asked.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

A route guard and a row scope, and the endpoint whose guard is correct and still leaks.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

A field allow-list and a list of events that must produce a line, checked against each other.

<<BLOCK:sol4>>

:::
