---
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

```java run-files
// ===== AuthDemo.java =====

import java.util.Map;

public class AuthDemo {
    public static void main(String[] args) throws Exception {
        System.out.println("--- published test vectors, so this is checkable ---");
        System.out.println();
        System.out.println("  PBKDF2-HMAC-SHA256, password/salt, c=1:");
        System.out.println("    " + Secrets.derive("password", "salt".getBytes("UTF-8"), 1));
        System.out.println("  PBKDF2-HMAC-SHA256, password/salt, c=4096:");
        System.out.println("    " + Secrets.derive("password", "salt".getBytes("UTF-8"), 4096));
        System.out.println("  SHA-256(\"abc\"):");
        System.out.println("    " + Secrets.sha256("abc"));

        System.out.println();
        System.out.println("--- one password, two users, two salts ---");
        byte[] alice = Secrets.salt();
        byte[] bob = Secrets.salt();
        String forAlice = Secrets.derive("correct horse", alice, 4096);
        String forBob = Secrets.derive("correct horse", bob, 4096);
        System.out.println("  same password, different salt, same record : "
                + forAlice.equals(forBob));
        System.out.println("  both verify against their own salt         : "
                + (forAlice.equals(Secrets.derive("correct horse", alice, 4096))
                && forBob.equals(Secrets.derive("correct horse", bob, 4096))));
        System.out.println("  a wrong password verifies                  : "
                + forAlice.equals(Secrets.derive("correct hoarse", alice, 4096)));

        System.out.println();
        System.out.println("--- comparing a secret, and how much that leaks ---");
        String stored = "s3cr3t-session-id";
        String early = "aaaaaaaaaaaaaaaaa";
        String late = "s3cr3t-session-iX";
        System.out.println("  String.equals, differs at index 0   : compared "
                + Secrets.countEquals(stored, early));
        System.out.println("  String.equals, differs at the end   : compared "
                + Secrets.countEquals(stored, late));
        Secrets.equalsAlways(stored, early);
        System.out.println("  equal-time,   differs at index 0    : compared "
                + Secrets.compared);
        Secrets.equalsAlways(stored, late);
        System.out.println("  equal-time,   differs at the end    : compared "
                + Secrets.compared);

        System.out.println();
        System.out.println("--- session ids ---");
        System.out.println("  bytes of entropy : 16");
        System.out.println("  hex characters   : " + Ids.newId().length());
        System.out.println("  distinct in 1000 : " + Ids.distinctIn(1000));
        System.out.println("  new Random, same seed, same value : "
                + Ids.seededPredictably(42));

        System.out.println();
        System.out.println("--- the two headers are not the same shape ---");
        String response = Cookies.setCookie("sid", "abc123", "/", true, true, "Lax", 3600);
        System.out.println("  Set-Cookie : " + response);
        Map<String, String> parsed = Cookies.parse(response);
        System.out.println("  parsed as cookies      : " + parsed.size() + " entries");
        System.out.println("  a request would send   : "
                + Cookies.parse("sid=abc123; theme=dark"));
    }
}

// ===== Cookies.java =====

import java.util.LinkedHashMap;
import java.util.Map;

/** The Cookie and Set-Cookie headers, and the fact that they are not the same shape. */
public final class Cookies {

    private Cookies() {
    }

    /** A request's Cookie header: name=value pairs, and nothing else. */
    public static Map<String, String> parse(String header) {
        Map<String, String> out = new LinkedHashMap<>();
        if (header == null || header.isEmpty()) {
            return out;
        }
        for (String part : header.split(";")) {
            int at = part.indexOf('=');
            if (at <= 0) {
                continue;
            }
            out.put(part.substring(0, at).trim(), part.substring(at + 1).trim());
        }
        return out;
    }

    /** A response's Set-Cookie: one pair, then attributes. */
    public static String setCookie(String name, String value, String path, boolean httpOnly,
                                   boolean secure, String sameSite, long maxAgeSeconds) {
        StringBuilder out = new StringBuilder();
        out.append(name).append('=').append(value);
        if (path != null) {
            out.append("; Path=").append(path);
        }
        if (maxAgeSeconds >= 0) {
            out.append("; Max-Age=").append(maxAgeSeconds);
        }
        if (httpOnly) {
            out.append("; HttpOnly");
        }
        if (secure) {
            out.append("; Secure");
        }
        if (sameSite != null) {
            out.append("; SameSite=").append(sameSite);
        }
        return out.toString();
    }
}

// ===== Ids.java =====

import java.security.SecureRandom;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;

/** Where session ids come from, and why `new Random()` is the wrong answer. */
public final class Ids {

    private static final SecureRandom RANDOM = new SecureRandom();

    private Ids() {
    }

    public static String newId() {
        byte[] bytes = new byte[16];
        RANDOM.nextBytes(bytes);
        StringBuilder out = new StringBuilder();
        for (byte b : bytes) {
            out.append(Character.forDigit((b >> 4) & 0xf, 16));
            out.append(Character.forDigit(b & 0xf, 16));
        }
        return out.toString();
    }

    public static int distinctIn(int draws) {
        Set<String> seen = new HashSet<>();
        for (int i = 0; i < draws; i++) {
            seen.add(newId());
        }
        return seen.size();
    }

    /** Two `Random`s built from the same seed produce the same sequence. Always. */
    public static boolean seededPredictably(long seed) {
        Random a = new Random(seed);
        Random b = new Random(seed);
        return a.nextLong() == b.nextLong();
    }
}

// ===== Secrets.java =====

import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.HexFormat;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/** Passwords: a per-user salt, a slow key-derivation function, and an equal-time compare. */
public final class Secrets {

    private static final SecureRandom RANDOM = new SecureRandom();
    public static int compared;

    private Secrets() {
    }

    public static byte[] salt() {
        byte[] bytes = new byte[16];
        RANDOM.nextBytes(bytes);
        return bytes;
    }

    public static String derive(String password, byte[] salt, int iterations) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, 256);
        byte[] key = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                .generateSecret(spec).getEncoded();
        return HexFormat.of().formatHex(key);
    }

    public static String sha256(String text) throws Exception {
        return HexFormat.of().formatHex(
                MessageDigest.getInstance("SHA-256").digest(text.getBytes("UTF-8")));
    }

    /** `String.equals` stops at the first difference, and the count is observable. */
    public static int countEquals(String a, String b) {
        int seen = 0;
        int limit = Math.min(a.length(), b.length());
        for (int i = 0; i < limit; i++) {
            seen++;
            if (a.charAt(i) != b.charAt(i)) {
                return seen;
            }
        }
        return seen;
    }

    /** Reads every character whether or not it has already found a difference. */
    public static boolean equalsAlways(String a, String b) {
        compared = 0;
        if (a.length() != b.length()) {
            return false;
        }
        int difference = 0;
        for (int i = 0; i < a.length(); i++) {
            compared++;
            difference |= a.charAt(i) ^ b.charAt(i);
        }
        return difference == 0;
    }
}
```

```text
--- published test vectors, so this is checkable ---

  PBKDF2-HMAC-SHA256, password/salt, c=1:
    120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b
  PBKDF2-HMAC-SHA256, password/salt, c=4096:
    c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a
  SHA-256("abc"):
    ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad

--- one password, two users, two salts ---
  same password, different salt, same record : false
  both verify against their own salt         : true
  a wrong password verifies                  : false

--- comparing a secret, and how much that leaks ---
  String.equals, differs at index 0   : compared 1
  String.equals, differs at the end   : compared 17
  equal-time,   differs at index 0    : compared 17
  equal-time,   differs at the end    : compared 17

--- session ids ---
  bytes of entropy : 16
  hex characters   : 32
  distinct in 1000 : 1000
  new Random, same seed, same value : true

--- the two headers are not the same shape ---
  Set-Cookie : sid=abc123; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Lax
  parsed as cookies      : 4 entries
  a request would send   : {sid=abc123, theme=dark}
```

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

```sh run-project
cat > Headers.java <<'JAVA'
import java.util.Map;

public class Headers {
    public static void main(String[] args) {
        String response = Cookies.setCookie("sid", "abc123", "/", true, true, "Lax", 3600);
        System.out.println("Set-Cookie             : " + response);
        System.out.println();
        System.out.println("read back with the request parser:");
        for (Map.Entry<String, String> entry : Cookies.parse(response).entrySet()) {
            System.out.println("  cookie " + entry.getKey() + " = " + entry.getValue());
        }
        System.out.println();
        System.out.println("three of those are not cookies. HttpOnly, Secure and SameSite are");
        System.out.println("attributes that tell the browser what to do with the cookie, and a");
        System.out.println("naive parser stores them as if a client had sent them -- which is");
        System.out.println("how a server ends up believing it was sent a cookie named Path");

        System.out.println();
        System.out.println("each attribute is a promise about one attack:");
        System.out.println("  HttpOnly  : document.cookie cannot read it, so XSS cannot steal it");
        System.out.println("  Secure    : the browser will not send it over plain HTTP");
        System.out.println("  SameSite  : it is not sent on cross-site requests, which is what");
        System.out.println("              stops CSRF without a token");
        System.out.println("  Path      : the cookie is only sent under this prefix");
        System.out.println("  Max-Age   : it expires, in seconds, from now");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Headers.java
java -cp out Headers
```

```text
Set-Cookie             : sid=abc123; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Lax

read back with the request parser:
  cookie sid = abc123
  cookie Path = /
  cookie Max-Age = 3600
  cookie SameSite = Lax

three of those are not cookies. HttpOnly, Secure and SameSite are
attributes that tell the browser what to do with the cookie, and a
naive parser stores them as if a client had sent them -- which is
how a server ends up believing it was sent a cookie named Path

each attribute is a promise about one attack:
  HttpOnly  : document.cookie cannot read it, so XSS cannot steal it
  Secure    : the browser will not send it over plain HTTP
  SameSite  : it is not sent on cross-site requests, which is what
              stops CSRF without a token
  Path      : the cookie is only sent under this prefix
  Max-Age   : it expires, in seconds, from now
```

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

```sh run-project
cat > Fixation.java <<'JAVA'
public class Fixation {
    public static void main(String[] args) {
        String planted = "attacker-knows-this-id";
        System.out.println("--- a session id the attacker chose ---");
        System.out.println("  planted before login : " + planted);

        String afterLogin = Ids.newId();
        System.out.println("  issued at login      : <32 hex chars, never sent before>");
        System.out.println("  rotated              : " + !afterLogin.equals(planted));
        System.out.println("  length               : " + afterLogin.length());
        System.out.println();
        System.out.println("a server that keeps the pre-login id after authentication has");
        System.out.println("handed the attacker a session it already knows. The fix is one");
        System.out.println("line: issue a fresh id at every privilege change, and invalidate");
        System.out.println("the old one rather than merely overwriting it");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Fixation.java
java -cp out Fixation
```

```text
--- a session id the attacker chose ---
  planted before login : attacker-knows-this-id
  issued at login      : <32 hex chars, never sent before>
  rotated              : true
  length               : 32

a server that keeps the pre-login id after authentication has
handed the attacker a session it already knows. The fix is one
line: issue a fresh id at every privilege change, and invalidate
the old one rather than merely overwriting it
```

Here is the attack the name describes. An attacker visits your site, gets a session id, and then
persuades the victim to use it — a link with `?sid=...` that your service accepts, or a cookie planted
on a domain the victim shares. The victim logs in. If the service keeps the same id after
authentication, the attacker now holds the id of an authenticated session, and no credential was ever
stolen.

The fix is one line and it is easy to forget: **issue a fresh session id at every change in privilege**,
and invalidate the old one rather than merely overwriting it. Login is the obvious place; password
change and permission elevation are the ones that get missed.

## The crypto APIs throw, and javac will not let you forget

```java bad
import java.security.MessageDigest;

public class NoAlgorithm {
    public static void main(String[] args) {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        System.out.println(digest.getDigestLength());
    }
}
```

```text
error: unreported exception NoSuchAlgorithmException; must be caught or declared to be thrown
```

Every `MessageDigest.getInstance`, `KeyGenerator.getInstance` and `Cipher.getInstance` takes the
algorithm as a **string** and throws `NoSuchAlgorithmException`. That is a checked exception for a
reason: the algorithm name is resolved at runtime, so "does this JVM have it" is not a question the
compiler can answer. The practical consequence is that every crypto helper either declares `throws
Exception` or wraps in an unchecked type — and the wrong answer is `catch (Exception e) { return null; }`,
which turns a misconfiguration into a null hash and a login that accepts anything.

### Sessions that get serialised

```java warn
import java.io.Serializable;

public class Stateful implements Serializable {
    private String user;
    private long expiresAt;

    public static void main(String[] args) {
        System.out.println("a session object that gets serialised into a store");
    }
}
```

```text
warning: [serial] serializable class Stateful has no definition of serialVersionUID
```

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
cat > Scenario.java <<'JAVA'
import java.util.LinkedHashMap;
import java.util.Map;

public class Scenario {
    public static void main(String[] args) throws Exception {
        Map<String, String> users = new LinkedHashMap<>();
        byte[] salt = Secrets.salt();
        users.put("bob", Secrets.derive("hunter2", salt, 4096));

        System.out.println("--- a login that stores a hash, not a password ---");
        System.out.println("  stored for bob : <" + users.get("bob").length()
                + " hex chars, and none of them is the password>");
        System.out.println("  correct        : "
                + users.get("bob").equals(Secrets.derive("hunter2", salt, 4096)));
        System.out.println("  wrong          : "
                + users.get("bob").equals(Secrets.derive("hunter3", salt, 4096)));
        System.out.println("  length         : " + users.get("bob").length() + " hex chars");

        System.out.println();
        System.out.println("--- and a cookie the browser will actually protect ---");
        String cookie = Cookies.setCookie("sid", Ids.newId(), "/", true, true, "Lax", 3600);
        String shown = cookie.substring(0, cookie.indexOf('=') + 1) + "<32 hex chars>"
                + cookie.substring(cookie.indexOf(';'));
        System.out.println("  " + shown);
        System.out.println();
        System.out.println("  HttpOnly is present : " + cookie.contains("HttpOnly"));
        System.out.println("  Secure is present   : " + cookie.contains("Secure"));
        System.out.println("  SameSite=Lax        : " + cookie.contains("SameSite=Lax"));
        System.out.println("  expires in seconds  : 3600");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
--- a login that stores a hash, not a password ---
  stored for bob : <64 hex chars, and none of them is the password>
  correct        : true
  wrong          : false
  length         : 64 hex chars

--- and a cookie the browser will actually protect ---
  sid=<32 hex chars>; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Lax

  HttpOnly is present : true
  Secure is present   : true
  SameSite=Lax        : true
  expires in seconds  : 3600
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
```sh run-project
cat > Sol1.java <<'JAVA'
import java.util.Map;

public class Sol1 {
    public static void main(String[] args) {
        Map<String, String> cookies = Cookies.parse("sid=abc123; theme=dark; lang=en");
        System.out.println("pairs   : " + cookies.size());
        System.out.println("sid     : " + cookies.get("sid"));
        System.out.println("theme   : " + cookies.get("theme"));
        System.out.println("missing : " + cookies.get("nope"));
        System.out.println();
        System.out.println("a missing cookie is null, not \"\", and code that treats the two");
        System.out.println("the same will treat \"logged out\" as \"logged in as \"''");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
pairs   : 3
sid     : abc123
theme   : dark
missing : null

a missing cookie is null, not "", and code that treats the two
the same will treat "logged out" as "logged in as "''
```

`null` for a missing key. The dangerous version of this bug is `if (cookies.get("sid") != "")`, which
is true when the cookie is absent — so "not logged in" reads as "logged in as the empty user", and the
handler proceeds with a session that does not exist.

:::

:::solution Exercise 2
```sh run-project
cat > Sol2.java <<'JAVA'
public class Sol2 {
    public static void main(String[] args) {
        String weak = Cookies.setCookie("sid", "abc123", null, false, false, null, -1);
        String strong = Cookies.setCookie("sid", "abc123", "/", true, true, "Lax", 3600);
        System.out.println("weak   : " + weak);
        System.out.println("strong : " + strong);
        System.out.println();
        System.out.println("the weak one is readable by any script on the page, is sent over");
        System.out.println("plain HTTP, and is attached to requests other sites initiate. The");
        System.out.println("strong one is none of those things, and it costs one more string");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
weak   : sid=abc123
strong : sid=abc123; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Lax

the weak one is readable by any script on the page, is sent over
plain HTTP, and is attached to requests other sites initiate. The
strong one is none of those things, and it costs one more string
```

The weak cookie is one string; the strong one is the same string plus five attributes. That is the
entire cost of the three mitigations, which is why there is no argument for shipping the weak one —
it is not a trade-off, it is an omission.

:::

:::solution Exercise 3
```sh run-project
cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) throws Exception {
        byte[] salt = Secrets.salt();
        String one = Secrets.derive("same-password", salt, 4096);
        String two = Secrets.derive("same-password", salt, 4096);
        byte[] other = Secrets.salt();
        String three = Secrets.derive("same-password", other, 4096);

        System.out.println("same salt, same password : " + one.equals(two));
        System.out.println("different salt           : " + one.equals(three));
        System.out.println("salt length in bytes     : " + salt.length);
        System.out.println("record length in hex     : " + one.length());
        System.out.println();
        System.out.println("the salt is stored next to the hash and is not a secret. What it");
        System.out.println("buys is that two users with one password get two different records,");
        System.out.println("so one stolen hash does not reveal who shared a password");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
same salt, same password : true
different salt           : false
salt length in bytes     : 16
record length in hex     : 64

the salt is stored next to the hash and is not a secret. What it
buys is that two users with one password get two different records,
so one stolen hash does not reveal who shared a password
```

Same salt and same password give the same record; a different salt does not. Note that the salt is 16
bytes and the record is 64 hex characters — the stored value is the derived key, and the salt sits
beside it in the row.

:::

:::solution Exercise 4
```sh run-project
cat > Sol4.java <<'JAVA'
public class Sol4 {
    public static void main(String[] args) {
        String stored = "0123456789abcdef";
        String guessEarly = "x123456789abcdef";
        String guessLate = "0123456789abcdex";

        System.out.println("String.equals, first char wrong : compared "
                + Secrets.countEquals(stored, guessEarly));
        System.out.println("String.equals, last char wrong  : compared "
                + Secrets.countEquals(stored, guessLate));

        Secrets.equalsAlways(stored, guessEarly);
        int early = Secrets.compared;
        Secrets.equalsAlways(stored, guessLate);
        int late = Secrets.compared;
        System.out.println("equal-time, first char wrong    : compared " + early);
        System.out.println("equal-time, last char wrong     : compared " + late);
        System.out.println();
        System.out.println("the first two numbers differ, and that difference is measurable");
        System.out.println("from across a network. The second two are the same, so there is");
        System.out.println("nothing to measure");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
String.equals, first char wrong : compared 1
String.equals, last char wrong  : compared 16
equal-time, first char wrong    : compared 16
equal-time, last char wrong     : compared 16

the first two numbers differ, and that difference is measurable
from across a network. The second two are the same, so there is
nothing to measure
```

`String.equals` read 1 character for the early mismatch and 16 for the late one. That gap is the whole
timing side channel, and it is why `MessageDigest.isEqual` exists: the equal-time version reads 16 for
both, so the response time carries no information about where the guess went wrong.

:::
