#!/usr/bin/env python3
"""Generate chapters/34-sessions-cookies-and-authentication.md.

    python3 tools/gen/34/gen.py

HTTP is stateless, so a service has to invent a session -- and every part of that
is a security decision: where the id comes from, what the Set-Cookie attributes
promise, how the password is stored, and how the comparison is made. The key
derivation is checked against published test vectors rather than asserted, because
a hash you cannot check is a hash you cannot trust.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from javagen import Gen  # noqa: E402

CHAPTERS = HERE.parent.parent.parent / "chapters"
gen = Gen(HERE, CHAPTERS, "34-sessions-cookies-and-authentication.md")

BLOCKS = {
    "core": gen.run_files(["AuthDemo.java", "Cookies.java", "Ids.java", "Secrets.java"]),
    "headers": gen.sh("headers.sh", "run-project"),
    "fixation": gen.sh("fixation.sh", "run-project"),
    "checked": gen.bad("NoAlgorithm.java", "unreported exception NoSuchAlgorithmException"),
    "serial": gen.warn("Stateful.java", "serialVersionUID"),
    "scenario": gen.sh("scenario.sh", "run-project"),
    "sol1": gen.sh("sol1.sh", "run-project"),
    "sol2": gen.sh("sol2.sh", "run-project"),
    "sol3": gen.sh("sol3.sh", "run-project"),
    "sol4": gen.sh("sol4.sh", "run-project"),
}

TEMPLATE = r"""---
chapter: 34
part: 5
title: Sessions, Cookies and Authentication
summary: HTTP forgets everything between requests, so a service has to invent a session — and every piece of that is a security decision. Where session ids come from, the five Set-Cookie attributes and the one attack each prevents, password storage with a salt and a slow KDF checked against published test vectors, session fixation, and why String.equals leaks a secret.
minutes: 85
tags: [sessions, cookies, authentication, pbkdf2, timing, security, http]
---

HTTP has no memory. Every request arrives knowing nothing about the one before it, which is a large
part of why the protocol scales — and it means that anything that looks like "being logged in" is
something your service has to invent. It invents it with a cookie carrying a session id, and every
decision in that sentence is a security decision: where the id comes from, what the browser is told to
do with it, what is stored against it, and how a presented secret is compared.

The claim that organises this chapter is that **authentication is not a feature you add, it is a set of
defaults you can get wrong silently.** Every mistake below produces a service that works perfectly for
years and is broken the whole time.

## What a session actually is

@@core@@

Three of those blocks are worth reading slowly.

**The test vectors.** `PBKDF2-HMAC-SHA256("password", "salt", 1)` producing
`120fb6cf...70be17b` is a published value, not a claim from this book — and it matters that it is
checkable, because a key-derivation function that is subtly wrong produces output that looks exactly
like output that is right. If you ever wire up password storage, print one published vector once and
compare it. It takes a minute and it is the only check that proves the algorithm, the encoding and the
iteration count are all what you think they are.

**The salts.** One password, two users, two different records. That is what a salt buys, and it is not
secrecy — the salt is stored next to the hash in plain text. It buys two things: two users with the
same password do not get the same record, so one stolen hash does not reveal who shared a password; and
a precomputed table of hashes for common passwords is useless, because the table would have to be
computed per salt.

**The comparison.** `String.equals` compared **1** character when the guess was wrong at the first
position and **17** when it was wrong at the last. That difference is the vulnerability. It is
observable — in a loop over a network, statistically, by an attacker who can measure microseconds — and
it turns a 2<sup>128</sup> search into sixteen sequential searches over 256 values each. The
equal-time version compared 17 in both cases, because it reads every character whether or not it has
already found a difference.

### Slowness is the point

A password hash has to be *slow*, and that is the opposite of every other hashing instinct.
`SHA-256("abc")` is one pass and costs nanoseconds, which is why it is right for checksums and wrong
for passwords: an attacker with a GPU computes billions of them per second. PBKDF2 with 4096 iterations
costs 4096 times as much — trivial for one login, expensive for a billion guesses. That is why the
iteration count is a configuration value you raise over time, and why the record has to store it: to
verify an old password you need to know how many iterations it was hashed with.

Modern practice is `bcrypt`, `scrypt` or `Argon2` rather than PBKDF2, because those are also
memory-hard and therefore expensive on the GPUs attackers actually use. PBKDF2 is used here because it
is in the JDK, which means it is verifiable on your machine with no jars. The shape of the code is
identical either way.

## The two cookie headers are not the same shape

@@headers@@

`Cookie:` and `Set-Cookie:` look similar and are not. A request's `Cookie` header is a list of
name=value pairs — that is all it can be, because the client is only ever sending pairs. A response's
`Set-Cookie` is **one pair followed by attributes**, and the attributes are instructions to the
browser, not data. The transcript shows what happens when you parse one with the other's parser: five
entries, three of which are not cookies at all.

That bug is worse than it looks. A server that accepts a cookie named `Path` or `HttpOnly` from a
request has let a client define its own attributes, and it is the same class of mistake as trusting a
`X-Forwarded-For` header — reading attacker-controlled data into a field you thought you owned.

Each attribute is a promise about exactly one attack:

| Attribute | What it stops | What happens without it |
|---|---|---|
| `HttpOnly` | theft via XSS | `document.cookie` reads the session id, and any injected script mails it away |
| `Secure` | interception | the cookie is sent over plain HTTP if the user ever lands on one |
| `SameSite=Lax` | CSRF | the cookie rides along on requests other sites initiate |
| `Path=/` | over-sending | the cookie is sent to every path, including static assets |
| `Max-Age` | indefinite sessions | a stolen cookie works forever |

`SameSite` deserves the note that it has largely replaced CSRF tokens for the common case. `Lax` means
"send it on top-level navigation but not on cross-site subrequests", so a link to your site still works
while an `<img>` on someone else's page cannot trigger a state-changing request. `Strict` is stronger
and breaks inbound links. `None` requires `Secure` and should be rare.

:::danger A session id must come from SecureRandom
`new Random()` is a deterministic algorithm with a 48-bit seed, and `new Random(seed)` produces the
same sequence every time — which the transcript demonstrates. Worse, a `Random` seeded from
`System.currentTimeMillis()` has a seed an attacker can guess to within a few million values, and
"a few million" is not a search space. Session ids, password-reset tokens, CSRF tokens and anything
else an attacker must not predict come from `SecureRandom`, which is seeded from the operating system's
entropy pool. Sixteen bytes — 128 bits — is the floor; the transcript's thousand draws produced a
thousand distinct ids and no collisions, which is what 128 bits is for.
:::

## Session fixation

@@fixation@@

Here is the attack the name describes. An attacker visits your site, gets a session id, and then
persuades the victim to use it — a link with `?sid=...` that your service accepts, or a cookie planted
on a domain the victim shares. The victim logs in. If the service keeps the same id after
authentication, the attacker now holds the id of an authenticated session, and no credential was ever
stolen.

The fix is one line and it is easy to forget: **issue a fresh session id at every change in privilege**,
and invalidate the old one rather than merely overwriting it. Login is the obvious place; password
change and permission elevation are the ones that get missed.

## The crypto APIs throw, and javac will not let you forget

@@checked@@

Every `MessageDigest.getInstance`, `KeyGenerator.getInstance` and `Cipher.getInstance` takes the
algorithm as a **string** and throws `NoSuchAlgorithmException`. That is a checked exception for a
reason: the algorithm name is resolved at runtime, so "does this JVM have it" is not a question the
compiler can answer. The practical consequence is that every crypto helper either declares `throws
Exception` or wraps in an unchecked type — and the wrong answer is `catch (Exception e) { return null; }`,
which turns a misconfiguration into a null hash and a login that accepts anything.

### Sessions that get serialised

@@serial@@

A session object that is stored in a session store, replicated between nodes, or written to disk is
serialised, and javac's warning is about versioning: without an explicit `serialVersionUID`, the
compiler derives one from the class's shape, so adding a field changes it and every stored session from
before the change fails to deserialise. In a service that means every user is logged out by a deploy.
Declare it once — `private static final long serialVersionUID = 1L;` — and the class can grow without
invalidating what is already stored.

:::pitfall Rolling your own session store when you did not mean to
The default in most frameworks is an in-memory `Map<String, Session>`. That works perfectly on one
machine and is broken the moment there are two: a request that lands on the other node has no session,
so the user is logged out seemingly at random, and the bug is invisible in every test that runs one
instance. Three options, in order of how much they cost: sticky sessions at the load balancer (cheap,
and a deploy logs everyone out), a shared store such as Redis (normal), or stateless signed tokens
(no store, but no server-side logout either). What matters is choosing — an in-memory map with two
nodes behind a round-robin balancer is not a choice, it is an accident.
:::

:::scenario The login that stored the password
A small service stores users in a table with the columns `email` and `password`, and the registration
handler inserts the password it was given. It works. The team ships. Eighteen months later the database
is in a backup that leaks, and every user's password is in it — and because people reuse passwords,
the damage is not confined to this service.

```sh run-project
@@scenario@@
```

:::solution
Store a derived value, never the password, and make the derivation slow and salted:

1. **Per-user salt, 16 random bytes**, stored in plain text beside the hash. Not one global salt, which
   defeats the point, and not a hash of the email, which is guessable.
2. **A slow KDF** — PBKDF2 at 210,000 iterations is OWASP's current floor for HMAC-SHA256, `bcrypt` or
   `Argon2id` preferred — with the iteration count stored in the record so it can be raised later.
3. **Compare in equal time.** `MessageDigest.isEqual` does this for byte arrays and is one call; use it
   rather than `Arrays.equals`, which short-circuits exactly like `String.equals`.
4. **Set every cookie attribute.** The transcript's `HttpOnly; Secure; SameSite=Lax; Max-Age=3600` is
   the minimum, not the maximum.
5. **Rotate the session id at login**, and delete the old one server-side.
6. **Rate-limit the login endpoint**, because a slow KDF only helps if the attacker cannot simply ask
   your service a million times.

What none of this replaces: multi-factor authentication, and a breach-notification plan. Password
storage determines how much damage a leak does, not whether one happens.
:::

## Key takeaways

- HTTP is stateless; "logged in" is a session id in a cookie, and every part of that is a security decision.
- A `Cookie` request header is pairs; a `Set-Cookie` response is one pair plus attributes — never parse one with the other's parser.
- `HttpOnly` stops XSS theft, `Secure` stops plain-HTTP leakage, `SameSite=Lax` stops CSRF, `Max-Age` bounds the session.
- Session ids come from `SecureRandom`, never `Random`: a `Random` with a known seed reproduces its whole sequence.
- Store a salted, slow derivation of a password, never the password; PBKDF2 with 210,000 iterations, bcrypt or Argon2id.
- The salt is not secret; it makes identical passwords produce different records and defeats precomputed tables.
- Slowness is the point: a hash that costs nanoseconds lets an attacker try billions.
- `String.equals` short-circuits, and the number of characters it compares leaks the secret — compare in equal time.
- Rotate the session id at every change of privilege and invalidate the old one, or session fixation wins.
- Crypto algorithm names are strings resolved at runtime, which is why those APIs throw checked exceptions.

## Practice

- [ ] Parse `sid=abc123; theme=dark; lang=en` and print the three values plus what a missing key returns.
- [ ] Build the same cookie twice — once with no attributes, once with all of them — and print both.
- [ ] Derive the same password twice with the same salt and once with a different one, and print which records match.
- [ ] Compare two guesses that differ at the first and last character, and print how many characters each comparison reads.

## Solutions

:::solution Exercise 1
@@sol1@@

`null` for a missing key. The dangerous version of this bug is `if (cookies.get("sid") != "")`, which
is true when the cookie is absent — so "not logged in" reads as "logged in as the empty user", and the
handler proceeds with a session that does not exist.

:::

:::solution Exercise 2
@@sol2@@

The weak cookie is one string; the strong one is the same string plus five attributes. That is the
entire cost of the three mitigations, which is why there is no argument for shipping the weak one —
it is not a trade-off, it is an omission.

:::

:::solution Exercise 3
@@sol3@@

Same salt and same password give the same record; a different salt does not. Note that the salt is 16
bytes and the record is 64 hex characters — the stored value is the derived key, and the salt sits
beside it in the row.

:::

:::solution Exercise 4
@@sol4@@

`String.equals` read 1 character for the early mismatch and 16 for the late one. That gap is the whole
timing side channel, and it is why `MessageDigest.isEqual` exists: the equal-time version reads 16 for
both, so the response time carries no information about where the guess went wrong.

:::
"""

gen.write(TEMPLATE, BLOCKS)
