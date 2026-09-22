---
chapter: 50
part: 9
title: Thinking Like an Attacker
summary: A working method for deciding what to protect and what will actually be attacked -- inventory the assets, count the trust boundaries, count the attack surface, model the threats, and then test the two assumptions every design quietly makes: that "internal" means unreachable, and that two defences fail independently. Every number below is counted from a run.
minutes: 100
tags: [security, threat modelling, trust boundaries, attack surface, STRIDE, OWASP, defence in depth, least privilege]
---

Part III and Part IV taught you habits. Chapter 19 showed you parameterised queries, Chapter 25
showed you what `innerHTML` does to a page, Chapter 27 showed you bcrypt and why the response schema
omits the hash, Chapter 28 showed you a CSRF token compared with `compare_digest`. Those habits are
correct and you should keep them.

They are also, every one of them, a fix for a specific thing. What none of them tells you is where to
look next -- in code nobody has written yet, by people who are not you. That is what this Part is
for, and this chapter is the framework the other three rest on.

The framework is not a philosophy. It is five counts and two assumptions. The counts are of assets,
boundaries, inputs, threats and reachable resources, and each one is arithmetic you can do before
writing a line of code. The assumptions are the ones almost every design makes without noticing:
that a service described as internal cannot be reached, and that two defences in a row multiply. Both
are testable, and both turn out to be false in ways that are measurable.

## Start from what you are protecting

An asset is anything whose loss costs somebody something. The mistake is to treat that as a synonym
for "a table of user data", because the set is larger than the design document and the difference is
where the unpleasant surprises live.

<<BLOCK:assets>>

Read the first count before anything else. There are eleven assets and the design document names
five, which means six of them are being protected by whoever happens to remember they exist. Three
have no owner at all: the session table, the settings file, and the cache.

Then look at the distribution at the bottom rather than the total. Exactly one asset out of eleven
passes all four controls, and it is `password_hashes` -- the one everybody thinks about, and the one
that has had the most attention. Four fail exactly one control, and they are the four the team
actually discussed. The interesting rows are the ones at three and four: the two log files and the
settings file fail three, and the session table and the cache fail all four. Nobody is arguing about
those, because nobody has them on a list to argue about.

That is the shape of the problem, and it is not a security problem yet. It is an inventory problem,
and it has an inventory fix: name the assets, then say for each one who owns it, whether it is
encrypted, and how long you keep it. A control with no owner is a control nobody is failing.

The log deserves its own paragraph, because it is the asset people forget hardest and it is the one
that accumulates. The app writes one line per request, and the second half of that block passes a
day's worth of traffic through the actual logger and counts what ends up on disk.

Two hundred of the five hundred lines carry something that is a credential -- a password, a bearer
token, a session value -- and a hundred and one of them carry a credential *and* an email address.
That is forty per cent of the log. And the shapes responsible are only six of the fifteen, which is
the good news, because it means the fix is six handlers rather than a rewrite.

The bad news is the year. At five hundred requests a day that is seventy-three thousand
credential-bearing lines written to a file that is unencrypted, unrotated, in no retention policy,
and owned by nobody. The count is not alarming because seventy-three thousand is a large number. It
is alarming because it grows, and because nothing in the system will ever tell you it grew.

## Trust boundaries, and the count that matters

A trust boundary is a place where the level of trust changes. Inside one zone you can hand a value to
the next component and it is the same value; across a boundary you cannot, and every crossing is a
place where a check either exists or does not.

The reason to draw this rather than keep it in your head is that two counts people conflate turn out
to be different numbers: how many boxes a request touches, and how many boundaries it crosses.

<<BLOCK:boundaries>>

Start with the graph rather than the paths. Thirteen data flows, of which nine cross a zone and four
do not -- and the four that do not are exactly the ones anybody would call internal. That is worth
being precise about, because "internal" is a claim about the four, and the four are not where the
interesting failures are.

Now the table. Read the `components` and `boundaries` columns against each other and notice that they
are not proportional. `admin export` touches four components and crosses one boundary; `webhook in`
touches three and crosses two. The ratio runs from 0.250 to 0.667 depending on which path you pick,
which is the whole point: a diagram with more boxes in it is not a diagram with more risk in it.

The `gap` column is the one to act on. A boundary crossing is guarded when the component that
receives the data checks it, and the gap is the count of crossings where nothing does. The largest
gap in the table belongs to `upload`: five components, three boundaries, one guarded, gap two. The
browser-to-CDN hop has no check because a CDN does not check, which is fine; the app-to-object-store
hop has no check and should not be fine, because that is where the filename becomes a path.

And then the row that is easy to skip over. `fetch image` touches two components -- the fewest in the
table -- crosses one boundary, and guards none of it. It is the only path in the model whose entire
boundary is unguarded, and the reason nobody drew it is that it points *outward*. Every other path is
a request coming in; this one is the app making a request to a URL that arrived in a request. Two
components and one unguarded boundary is the smallest row in the table and it is the one that turns
into a serious finding, which is the argument for counting rather than looking.

## The attack surface is not the endpoint count

The surface is everything an attacker gets to choose, and that is not the number of URLs. It is the
number of *inputs*: every parameter, every body field, every header the handler reads.

<<BLOCK:surface>>

Nineteen routes and forty-seven inputs, so two and a half per route. That ratio is the first thing to
internalise, because it is why "we only have nineteen endpoints" is not a measurement of anything.

The second half of the block is the part worth carrying into your own code. Group the inputs by where
they arrive and look at the unchecked column:

- Seven arrive in the path, and none is unchecked. The framework types them from the decorator and
  rejects the wrong type before the handler runs, so path parameters get a check for free.
- Nineteen arrive in the query string and six are unchecked.
- Nineteen arrive in the body and eight are unchecked.
- One arrives in a header and it is unchecked, and it is the `Authorization` header.

That last line is the one to sit with. The single input that decides who you are is the one input
nothing validates, and it is that way because the framework cannot know what a session token looks
like -- validation of a credential is a lookup, not a type check, and somebody has to write it.

The totals say the same thing from further away: fourteen inputs out of forty-seven have a rule
somebody chose, eighteen have only the framework's type check, and fifteen have nothing at all. So
roughly a third of the surface is protected by a decision, a third by a default, and a third by
nothing.

The block ends with a count that is not about inputs. Five routes read input without an authorization
check; four of them are the endpoints that are *supposed* to run before anybody has logged in, and
the fifth is `POST /upload`. One line, one number, and it is the kind of finding that a route-by-route
review finds only if the reviewer is looking for the right thing.

## A threat model is arithmetic

STRIDE is six questions asked of every element on a data-flow diagram: can this be spoofed, tampered
with, repudiated, disclosed, denied, or elevated? It is a completeness device. It exists so that you
do not forget a question, and it does the job well.

What it does not do is rank, and the reason is arithmetic rather than taste.

<<BLOCK:stride>>

Eighteen elements, six questions, a hundred and eight cells, sixty-eight of which apply -- sixty-three
per cent, because the matrix does not ask a data store whether it can be spoofed. That is the count
people quote, and on its own it is close to useless: sixty-eight threats is not a work queue.

The column underneath it is the one that explains why. Denial of service, information disclosure and
tampering each come out at sixteen, because each applies to four kinds of element and the diagram
happens to have a lot of data stores and flows. Repudiation gets ten, spoofing six, elevation of
privilege four. Sort by that and you would conclude that tampering is four times the risk of
privilege escalation, and the number you sorted by is a property of how many boxes you drew, not of
your system.

The counterfactual at the end of the block makes it undeniable. Take the same system and draw its
four data stores as processes instead -- a change of vocabulary, not of software -- and the applicable
count goes from sixty-eight to seventy-six. Two categories move, and elevation of privilege *doubles*,
from four to eight. Nothing was built. One word under four boxes changed.

So use the matrix for what it is: a way to make sure you have asked. Then rank the results by
something else, because the matrix will not do it and will look like it has.

## What the list of known categories tells you

The OWASP Top Ten is a list somebody else maintains, which is exactly what makes it useful. Left to
your own judgement you will find the things you already worry about; a list maintained by other
people is a way of finding the things you did not think of.

So hold your own code against it. Not your imagined code -- the code you have.

<<BLOCK:owasp>>

Two of the ten are covered by this book, four partly, four not at all. Read the second table rather
than the first, because the split is not random and it is not about difficulty. It is about where the
fix lives.

Three categories have a syntax-level fix: parameterised queries, escaping, hashing. Two of those are
covered and the third is partly covered, and the reason is that a syntax-level fix is a thing you can
learn and then do the same way forever.

Three have a configuration-level fix, and none of the three is covered -- because a book cannot tell
you how your deployment is set up, only what to check.

Four have a design-level fix, and none of them is covered either. Broken access control is not a
missing function call; it is a decision about where authorization lives. Insecure design is not a bug;
it is a missing requirement. Software and data integrity is a decision about what you are willing to
deserialise. Server-side request forgery is a decision about whether a URL from a request is allowed
to become an outbound connection. None of those is a line of code you can copy.

That is the diagnosis this Part exists to treat. And the third table is the uncomfortable one: six
chapters of this book touch any Top Ten category at all, out of fifty-one, and they are all in Part
III and Part IV. A reader who finishes Part II has met none of it. The book has been teaching security
as something that happens in the applied tracks, which is a bit like teaching arithmetic only in the
word problems.

## "It is only reachable from inside"

This sentence is the most expensive one in the field, because it is usually true when it is said and
false when it matters, and nobody re-checks it in between. It is also a claim you can test, with the
breadth-first search from Chapter 47.

<<BLOCK:reachability>>

Nine of the thirteen components are reachable from the internet, and four are not. But the number to
look at is the middle block: of the nine that are reachable, five need no credential at all. The CDN
and the proxy, which is expected. The worker, the object store and the backup, which is not.

Now look at the four that are not reachable. Two of them -- the bastion and the admin CLI -- require a
credential, which is what you would expect from the two components somebody thought about. The other
two, `metadata` and `metrics`, are unreachable and need no credential, and that combination is only
safe for as long as nothing else can reach them.

Which brings the last section of the block. Add one endpoint -- the app's image fetcher, which takes a
URL from the request and requests it -- and the reachable set goes from nine to eleven. The two new
arrivals are `metadata` and `metrics`, both three hops from the internet, neither requiring a
credential.

Read the final two lines together, because the framing matters. The fetch bug added two components.
Nine were already reachable without it. The instinct is to file the SSRF as the incident; the
arithmetic says the flat network was already the finding and the SSRF is what made it visible. Fix the
URL allow-list and you have fixed two of eleven. Fix the network and you have changed the premise.

The reason to say "it is only internal" precisely is that it is a claim about *reachability*, and
reachability is computable. It is not a claim about authentication, which is a different graph. The
two graphs have different edges and the difference between them is your exposure.

## Defence in depth assumes independence

Two checks in front of the same sink are supposed to multiply. If each misses one input in ten, both
missing one should be one in a hundred. That is the arithmetic people quote when they say a control is
"another layer".

The arithmetic has a precondition nobody states: the two checks must fail on *different* inputs.

<<BLOCK:layers>>

Eight payloads in eight encodings, sixty-four inputs, all of them enumerated. Two layers, both of
which match signatures against decoded content.

Independence predicts that the two would catch about 33.6 of the inputs in common, and that between
them they would catch 59.4, leaving 4.6 through. The measured numbers are 43 caught in common, 50
caught between them, and 14 through. The prediction is wrong by a factor of three on the number that
matters, and the direction of the error is the dangerous one: layers you believe are independent
protect you less than you think, never more.

The mechanism is in the per-encoding table, and it is not subtle. Four of the eight encodings defeat
both layers -- double URL encoding, HTML entities, unicode escapes, and a tab where a space was. They
are the same four for both layers, because both layers are asking the same question of the same
decoded string. A second copy of the same check is not a second layer.

And note the containment: the WAF's catch set is a strict subset of the validator's, so the union is
50 and the validator alone is 50. The WAF contributed zero additional catches. That is what happens
when two controls share a signature list, and it is a much more common arrangement than it sounds --
the WAF rule and the application rule are often written from the same advisory by the same person on
the same afternoon.

The last line of the block is the contrast. A parameterised query and context-aware escaping catch all
sixty-four, because they never ask what the input says; they only decide where it goes. A structural
layer does not have a blind spot that scales with an attacker's inventiveness, because it is not
looking for anything.

So when you count layers, count the *kinds*. Two content checks are one layer. A content check and a
structural check are two.

## The check that fails open

Every authorization check can do three things: say yes, say no, or throw. The first two get tests. The
third gets decided by a single word in an `except` clause, usually at two in the morning, usually to
make an error go away.

<<BLOCK:failopen>>

Ten thousand requests, and two hundred and seventy of them take the error path -- the tokens of
accounts that have been deleted but whose tokens are still in the wild. That is 2.70% of traffic.

The failing-open site allows 281 requests; the failing-closed site allows 11. The eleven are the
legitimate owner of the one resource in the model; the other 270 are requests that were authorised
without a check ever being performed. At ten thousand requests a day that is 98,550 a year.

The last block is why this mistake survives review, and it is worth reading as a statement about
testing rather than about security. The two implementations differ on 270 requests out of 10,000. On
the other 9,730 -- 97.30% -- they are the same program, byte for byte, and every test that logs in as
a real user passes against both.

A test that checks a 403 passes against both. A test that exercises the happy path passes against
both. The only test that distinguishes them is one that presents a credential for an account that no
longer exists, and that test is not in the suite because nobody thought a deleted account was an
interesting case.

The general lesson is not "always fail closed", although you usually should. It is that an error path
is a decision, and a decision made by default is still a decision. When you write `except Exception`,
you are choosing a security posture for a case you have not thought about, and you are choosing it in
the one branch that no test is likely to cover.

## The blast radius of one credential

Least privilege is normally argued as a matter of taste, which is why it is normally lost. It is
better argued as a count: if this credential is stolen, how much does the thief reach?

The graph that answers it is not the network graph. It is a credential graph, and an edge means "this
holds something that grants access to that". That is why the traversal crosses layers the network
diagram shows as separate.

<<BLOCK:blast_radius>>

Least privilege reaches three resources. The grant the account actually has -- the same three tables
plus `config`, `sessions` and the request log -- reaches seventeen. Fourteen of the seventeen are
reachable only through those three extra tables, and the factor is 5.7.

None of those three grants would be described as broad by anyone who wrote them. A service account
that can read its own config and its own sessions is not obviously over-privileged; it is the shape
most services have. The number is not in the grant, it is in what the grant *contains*.

Follow the chain: the config table holds an S3 key, the key opens the backup bucket, the bucket holds
the nightly dump, the dump holds the admin password hash, and the hash is a production shell. Six
hops, and there is no network path between the database account and the shell at all. The thing that
connects them is a value stored in a table, and the reason to draw this graph rather than reason about
it is that nobody reasons about six hops.

The audit log at seven hops is the one to notice last. A credential that reaches the audit log can
remove the evidence of everything it did on the way there, which is why the shortest path to the log
is a security property and not an operational detail.

:::pitfall Where you put the rule decides how many rules you have

Everything so far has been about finding things. This is about the mistake that turns a finding into a
recurring one: enforcing a rule where it is easiest to write rather than where it is hardest to
forget.

"Only the owner may read this" is a rule about data. The temptation is to enforce it in the route
handler, because that is where the current user is and it reads well. The cost of that choice is not
paid today. It is paid every time somebody adds a route.

<<BLOCK:pitfall>>

Read the first table as a bill. Twelve routes read owned data at the first release, and under the
route-level design each one is a place the rule has to be right. Five releases later there are
twenty-one, and the nine that arrived in between were nine new opportunities to forget. The
repository-level design ends the same period with one site, and it grew by zero.

The second table is what decides how long a mistake survives. The two designs do not merely differ in
how many sites can be wrong; they differ in what happens when one is. A forgotten check at the route
level returns rows owned by somebody else, with a 200 and a plausible body. A forgotten opt-out at the
repository level raises, on the first request of the first test run.

That asymmetry is the whole argument, and it is not an argument about security. It is an argument
about which mistakes are loud. Given two designs that are equally correct, prefer the one whose
failure mode is a stack trace.

:::

:::scenario The test that was scoped

A penetration test is a purchase. You buy a number of days, pointed at a number of endpoints, and the
report says what was found inside that rectangle. Reading the rectangle before the findings is not
cynicism; it is the only way to know what the report is a statement *about*.

<<BLOCK:scenario>>

The estate has sixty-one endpoints across three services. The engagement covered eighteen of them --
the public API -- which is 29.5%. The other forty-three were not tested, and they produced no findings,
because an endpoint nobody looks at cannot produce one. That is not a criticism of the tester. It is
what a scope means.

The report was four findings: one medium, three low, all of them in the endpoints it was pointed at.
Meanwhile the two services nobody looked at require no session at all, and one of them holds 240,000
records. It is reachable from the VPN, and three of the 340 VPN accounts are shared, so "reachable
from the VPN" is a shorter sentence than it sounds.

The last paragraph is why this scenario belongs in a chapter about thinking rather than in a
post-mortem. One session middleware, applied to the two services that lack it, covers forty-three
endpoints and 240,000 records. The finding was large and the change was small, which is the usual
shape once somebody counts instead of guessing.

:::

## Key takeaways

- **Count the assets before defending them.** Eleven assets in the code, five in the design document.
  An asset in no document has no owner, and a control with no owner is a control nobody is failing.
- **Look at the distribution, not the total.** Exactly one of the eleven assets passes all four
  controls, and it is the one that had the most attention. The two that fail all four had none.
- **The log is an asset.** 200 of 500 request lines carried a credential and 101 carried a credential
  plus an email. Six of the fifteen request shapes were responsible, which makes it a fixable bug.
- **Anything that accumulates needs a retention policy.** 73,000 credential-bearing lines a year, in a
  file that is unencrypted, unrotated and unowned. Nothing in the system will tell you it grew.
- **Count boundaries, not boxes.** The same deployment gives 0.250 to 0.667 boundaries per component
  depending on the path. A diagram with more boxes is not a diagram with more risk.
- **The unguarded path is usually the outbound one.** `fetch image` touches two components, crosses one
  boundary, guards none of it -- and it is the only wholly unguarded path, because nobody drew the
  arrow pointing out.
- **The attack surface is the input count, not the endpoint count.** 19 routes, 47 inputs. Path
  parameters get a type check for free; the query string, the body and the `Authorization` header do
  not.
- **The input that decides who you are is the one nothing validates.** A session token is a lookup,
  not a type check, so no framework can check it for you.
- **STRIDE is a completeness device, not a ranking device.** 68 applicable threats out of 108 cells,
  and the count per category is a property of how many boxes you drew.
- **Redraw the diagram and the threat count moves.** Relabelling four data stores as processes takes
  the total from 68 to 76 and doubles elevation of privilege. Nothing was built.
- **The fix's location predicts whether a book like this has covered it.** Every category with a
  syntax-level fix is covered here; none with a design-level fix is.
- **"Internal" is a reachability claim, and reachability is computable.** Nine of thirteen components
  were reachable from the internet before the SSRF existed; five of the nine needed no credential.
- **Separate the reachability graph from the authentication graph.** They have different edges, and
  the difference between them is the exposure.
- **Two checks that fail on the same inputs are one check.** Independence predicted 4.6 inputs through;
  14 got through. The error is always in the direction that flatters the design.
- **A structural layer has no blind spot that scales.** Parameterisation and context-aware escaping
  caught 64 of 64, because they decide where input goes rather than what it says.
- **An error path is a decision made by default.** The failing-open and failing-closed sites were
  identical on 97.30% of traffic, which is why the 270 requests that distinguished them never came up.
- **Least privilege is a count, not a taste.** Three extra tables took the blast radius from 3
  resources to 17, a factor of 5.7, with no network path between the ends of the chain.
- **Where you enforce a rule decides how many rules you have.** The route-level design needed 21
  correct sites after five releases; the repository-level design needed one, and it grew by zero.

## Practice

- [ ] **Take an inventory.** For a project you have written, list every asset -- tables, config files,
  logs, caches, backups, uploads. For each, record whether it is documented, owned, encrypted and
  retained. Count the assets that fail all four, then count how many credential-bearing lines your
  logs would hold in a year at your real request rate.
- [ ] **Count the boundaries, not the boxes.** Draw the data flows for four request paths through a
  system you know. For each, count the components, the trust boundaries, and how many of those
  boundaries have a check on them. Find the path with the largest gap, then check whether it is also
  the path with the most components.
- [ ] **STRIDE one element.** Pick a single component and answer all six STRIDE questions about it in
  writing. Then run the same component through the applicability matrix. Report how many questions you
  had an answer for, which ones you left blank, and what the matrix says the count should have been.
- [ ] **Compute a blast radius.** Build a credential graph for a project you know: which account reads
  which table, which table holds which key, which key opens which store. Take the least privileged
  account you have and traverse it. Then add back the grants it has but does not obviously need, and
  report the factor by which the radius grows.

## Solutions

:::solution Exercise 1

A smaller inventory over a different application, and the same two counts.

<<BLOCK:sol1>>

:::

:::solution Exercise 2

Four paths, and the check that the two counts are not the same count.

<<BLOCK:sol2>>

:::

:::solution Exercise 3

The six questions answered by hand, and the matrix's opinion of the same component.

<<BLOCK:sol3>>

:::

:::solution Exercise 4

Ten resources, one starting credential, and the factor.

<<BLOCK:sol4>>

:::
