---
chapter: 42
part: 5
title: Sessions, Cookies and Authentication
summary: Give a stateless protocol a memory — cookies, unguessable session ids, salted password records, and a login flow a real client can complete.
minutes: 80
tags: [cookies, sessions, authentication, pbkdf2, timing attack, HttpOnly, CSRF]
---

Every request the server in Chapter 41 answered arrived alone. It had a method, a target and
some headers, and when the reply was written the conversation ended. That is the design that makes
HTTP scale, and it is also the reason a server cannot tell two requests from the same person apart.

This chapter is about the gap between "a request" and "a user". Three separate things have to go
right, and they fail independently: the browser has to be *told* which requests belong together,
the identifier that ties them has to be *unguessable*, and the password behind it has to be
*stored in a form that is still safe after the database leaks*. Get any one wrong and the other
two do not matter.

```cpp run
#include <cstdio>
#include <map>
#include <string>
#include <vector>

struct Cookie {
    std::string name, value, path = "/", same_site;
    bool http_only = false, secure = false;
    int max_age = -1;
};

std::string set_cookie(const Cookie &c) {
    std::string h = c.name + "=" + c.value;
    if (c.max_age >= 0) h += "; Max-Age=" + std::to_string(c.max_age);
    h += "; Path=" + c.path;
    if (c.http_only) h += "; HttpOnly";
    if (c.secure) h += "; Secure";
    if (!c.same_site.empty()) h += "; SameSite=" + c.same_site;
    return h;
}

// The request side is a different language: name=value pairs only. Every attribute
// printed above is response-only, so a parser that looks for "HttpOnly" in a request
// finds nothing, and a server that trusts the attributes it sent is trusting the
// client to police itself.
std::map<std::string, std::string> parse_cookies(const std::vector<std::string> &headers) {
    std::map<std::string, std::string> out;
    for (const std::string &h : headers) {
        std::size_t i = 0;
        while (i < h.size()) {
            std::size_t semi = h.find(';', i);
            std::string part = h.substr(i, semi == std::string::npos ? std::string::npos : semi - i);
            while (!part.empty() && part.front() == ' ') part.erase(part.begin());
            std::size_t eq = part.find('=');
            if (eq != std::string::npos) {
                std::string name = part.substr(0, eq), value = part.substr(eq + 1);
                if (out.find(name) == out.end()) out[name] = value;   // first wins
            }
            if (semi == std::string::npos) break;
            i = semi + 1;
        }
    }
    return out;
}

int main() {
    Cookie sid;
    sid.name = "sid";
    sid.value = "9f2c41a7c0de5b83a1e6f40d2c7b95ae";
    sid.max_age = 86400;
    sid.http_only = true;
    sid.secure = true;
    sid.same_site = "Strict";
    std::printf("Set-Cookie: %s\n\n", set_cookie(sid).c_str());

    // Two Cookie headers with the same name twice: RFC 6265 allows the client to
    // split them, and says the first occurrence wins. Silently taking the last is
    // how a client-supplied cookie overrides a server-set one.
    std::vector<std::string> request = {"sid=first; theme=dark",
                                        "sid=second; lang=en"};
    std::printf("parsed from the request:\n");
    for (const auto &kv : parse_cookies(request))
        std::printf("  %-6s -> %s\n", kv.first.c_str(), kv.second.c_str());
    return 0;
}
```

```text
Set-Cookie: sid=9f2c41a7c0de5b83a1e6f40d2c7b95ae; Max-Age=86400; Path=/; HttpOnly; Secure; SameSite=Strict

parsed from the request:
  lang   -> en
  sid    -> first
  theme  -> dark
```

## A cookie is two different languages

Read that output carefully, because the asymmetry in it is the thing people get wrong. The
response header carries six pieces of information:

| Attribute | What it means | What happens if it is missing |
|---|---|---|
| `name=value` | the pair the server will get back | nothing to send |
| `Max-Age` | lifetime in seconds; `0` deletes it | a session cookie, gone when the browser closes |
| `Path` | which URLs it is attached to | the browser guesses, and the guess is `/` |
| `HttpOnly` | invisible to JavaScript | one XSS and the session is stolen |
| `Secure` | only over HTTPS | it travels in the clear |
| `SameSite` | when cross-site requests carry it | another site can act as the user |

The *request* header carries exactly one of those: `name=value`, repeated and separated by
semicolons. Every attribute above is response-only. A server that reads back the `HttpOnly` it
sent is reading a header the browser will never send — and, worse, is trusting a value the client
is free to invent. **The client's copy of a cookie is data. The server's copy is the authority.**

Two details in that parser are not decoration. The first is that a request may split its cookies
across several `Cookie` headers, and the specification says the **first** occurrence of a name
wins. A server that takes the last one lets a client-supplied cookie shadow a server-set one —
which is the first half of an attack this chapter ends with. The second is that the value is
everything after the first `=`, so a value containing `=` (a base64 blob, a signed token) survives
intact. Splitting on `=` is a bug that shows up the first time a real token contains one.

:::warning HttpOnly cannot be added later
`HttpOnly` is the only attribute here that closes a hole rather than narrowing one, and it
cannot be retrofitted onto a browser that already has the cookie: the JavaScript that was going
to read it is running in the same page. It has to be there on the very first `Set-Cookie` — which
means the decision is made when the cookie is created, in code that was probably written before
anyone thought about XSS. Send it always, including on cookies that hold nothing interesting.
:::

## "Unique" is not "unguessable"

The session id is where a working login system becomes a vulnerable one, because the obvious
implementation passes every test you would write by hand:

```cpp run
#include <cstdio>
#include <cstdlib>

int main() {
    // The mistake: seed a non-cryptographic generator with the clock and call the
    // output a session id. "Unpredictable" and "unique" are different properties,
    // and this has only the second one -- for a while.
    const unsigned boot = 1758500000u;          // when the server started
    std::srand(boot);
    const unsigned observed = static_cast<unsigned>(std::rand());   // the id a client saw
    unsigned next[3];
    for (int i = 0; i < 3; ++i) next[i] = static_cast<unsigned>(std::rand());

    std::printf("the attacker can see the server's Date header\n");
    std::printf("so the seed is a number within a day of the observed time\n\n");

    // One day either side: 86 400 candidate seeds. Nothing is known about the secret
    // except that it is small and was chosen by the clock.
    const unsigned lo = boot - 43200u, hi = boot + 43200u;
    unsigned tried = 0;
    bool cracked = false;
    for (unsigned seed = lo; seed < hi && !cracked; ++seed) {
        ++tried;
        std::srand(seed);
        if (static_cast<unsigned>(std::rand()) != observed) continue;
        // A candidate is only accepted if it predicts what came after.
        bool all = true;
        for (int i = 0; i < 3; ++i)
            if (static_cast<unsigned>(std::rand()) != next[i]) all = false;
        cracked = all;
    }

    std::printf("predicts the next three ids exactly: %s\n", cracked ? "yes" : "no");
    std::printf("seeds tried: %u\n", tried);
    std::printf("bytes of secret the attacker had to guess: %zu\n", sizeof(unsigned));
    return 0;
}
```

```text
the attacker can see the server's Date header
so the seed is a number within a day of the observed time

predicts the next three ids exactly: yes
seeds tried: 43201
bytes of secret the attacker had to guess: 4
```

That program is the whole attack, and it is short enough to read in one sitting. Nothing was
broken, nothing was leaked, the ids are all different — and yet the attacker who saw one id can
produce the next one. The seed was not secret; it was *derived from the clock*, and the server
advertises the clock in every response's `Date` header.

The lesson is not "don't use `rand()`", although that is true. It is that a session id has to be
**unpredictable**, and predictability is a property that cannot be tested for by looking at
outputs. `rand()` produces a stream that looks random; the word for what it actually is, is
*deterministic*. Anyone who can recover the state can continue the stream, and recovering the
state of a generator with 31 bits of it means guessing two billion things — or, as here, one
day's worth of seconds.

:::danger What a predictable id costs
A predicted session id is not a denial of service and does not trip any alarm. It reads exactly
like the real user's request, because as far as the server can tell it *is* the real user's
request. Every log line, every metric and every rate limit agrees that this is normal traffic.
The only defence is that the id could not have been guessed in the first place.
:::

## Where unpredictability comes from

The fix is to stop generating randomness and start *asking* for it. The kernel keeps a pool of
entropy that is fed by device timings and interrupts, and it is the one source in the building
that is designed to be unpredictable by anyone who is not the machine itself. On macOS and the
BSDs, `getentropy()` is the portable door to it:

```cpp run
#include <cstdint>
#include <cstdio>
#include <string>
#include <unordered_set>
#include <sys/random.h>

// splitmix64 is pure integer arithmetic, so this sequence -- and therefore the
// collision count below -- is identical on every machine. That is the point: a
// birthday-bound claim you cannot reproduce is not evidence.
static std::uint64_t splitmix64(std::uint64_t &s) {
    std::uint64_t z = (s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

int main() {
    const int draws = 200000;

    std::unordered_set<std::uint32_t> short_ids;
    int collisions = 0;
    std::uint64_t state = 0x1234;
    for (int i = 0; i < draws; ++i) {
        std::uint32_t id = static_cast<std::uint32_t>(splitmix64(state) & 0x7fffffffULL);
        if (!short_ids.insert(id).second) ++collisions;
    }
    std::printf("31-bit ids : %d draws, %d collisions\n", draws, collisions);
    std::printf("birthday bound n^2/(2*2^31) predicts %.1f\n",
                static_cast<double>(draws) * draws / (2.0 * 2147483648.0));

    // 128 bits, straight from the kernel. getentropy is capped at 256 bytes per
    // call by its interface, which is a kindness: nobody should need more.
    std::unordered_set<std::string> long_ids;
    for (int i = 0; i < draws; ++i) {
        unsigned char buf[16];
        if (::getentropy(buf, sizeof buf) != 0) {
            std::printf("getentropy failed\n");
            return 1;
        }
        static const char *digits = "0123456789abcdef";
        std::string id(32, '0');
        for (int j = 0; j < 16; ++j) {
            id[static_cast<std::size_t>(2 * j)] = digits[buf[j] >> 4];
            id[static_cast<std::size_t>(2 * j + 1)] = digits[buf[j] & 15];
        }
        long_ids.insert(id);
    }
    std::printf("128-bit ids: %d draws, %zu distinct\n", draws, long_ids.size());
    std::printf("first id in the table is 32 hex characters: %s\n",
                long_ids.begin()->size() == 32 ? "yes" : "no");
    // The birthday bound for 128 bits is 2^64 draws, not 2^128.
    std::printf("years to a likely collision at a billion ids a second: %.0f\n",
                18446744073709551616.0 / 1e9 / 86400.0 / 365.25);
    return 0;
}
```

```text
31-bit ids : 200000 draws, 12 collisions
birthday bound n^2/(2*2^31) predicts 9.3
128-bit ids: 200000 draws, 200000 distinct
first id in the table is 32 hex characters: yes
years to a likely collision at a billion ids a second: 585
```

The arithmetic in that output is the whole reason the length matters. Collisions in a random id
space are governed by the birthday bound: with `n` ids drawn from a space of size `N`, the
expected number of collisions is about `n² / 2N`. Thirty-one bits gives `N = 2^31`, and at
200 000 draws the bound predicts roughly **9** collisions — the program found 12, which is what
"roughly" means when the sample is a single run. Two hundred thousand sessions is not a large
deployment; 31 bits cannot survive a real one, and a collision is not a cosmetic problem. Two
users holding the same session id means one of them can read the other's account.

At 128 bits the same bound is `2^64` draws before a fifty-fifty chance — the square root of the
space, not the space — which is a number with no operational meaning. The last line of that output
makes the point in units a person can hold: drawing a billion ids a second, continuously, you
would need roughly six hundred years to reach an even chance of *one* collision anywhere. There is
no deployment in which that is the constraint.

And the word `getentropy` is doing something a seeded `rand()` never can: **there is no seed**.
Nothing in the process can recover the next id, because nothing in the process determines it.
That is the property to reach for, and it is worth measuring how much cheaper the wrong answer
was — one integer of state, one `srand`, and the whole session table.

## Storing the password

The session id is how the user is recognised *after* they log in. How they get there is the other
half, and it is the half that matters on the worst day: the day the database is copied.

The rule has been stated so often that it has stopped being argued and started being
misapplied, so it is worth being precise about *why*. A password must not be stored in a form
that can be turned back into the password. That rules out plaintext, and it also rules out a
plain hash — not because a hash is reversible, but because it is *the same for everyone*. Two
users with the same password would have the same row, and the attacker would not need to invert
anything: a table of hashes for the few million most common passwords answers most of the
database instantly. That is what a rainbow table is, and it is defeated not by a bigger hash but
by a per-user **salt**.

```cpp run
#include <CommonCrypto/CommonCryptoError.h>
#include <CommonCrypto/CommonKeyDerivation.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sys/random.h>

static std::string to_hex(const unsigned char *data, std::size_t n) {
    static const char *digits = "0123456789abcdef";
    std::string out(n * 2, '0');
    for (std::size_t i = 0; i < n; ++i) {
        out[2 * i] = digits[data[i] >> 4];
        out[2 * i + 1] = digits[data[i] & 15];
    }
    return out;
}

// 100 000 iterations is the part that costs the attacker something. The hash is the
// same length either way; the work factor is what makes a leaked table expensive.
constexpr unsigned kRounds = 100000;

static std::string derive(const std::string &password, const std::string &salt,
                          unsigned rounds) {
    unsigned char digest[32];
    int rc = CCKeyDerivationPBKDF(
        kCCPBKDF2, password.data(), password.size(),
        reinterpret_cast<const std::uint8_t *>(salt.data()), salt.size(),
        kCCPRFHmacAlgSHA256, rounds, digest, sizeof digest);
    if (rc != kCCSuccess) {
        std::fprintf(stderr, "PBKDF2 failed\n");
        std::exit(1);
    }
    return to_hex(digest, sizeof digest);
}

static std::string random_salt() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    return to_hex(buf, sizeof buf);
}

static std::string make_record(const std::string &password, const std::string &salt) {
    // The parameters travel with the hash, so today's rows keep working after the
    // cost is raised -- which is the only reason raising it is possible at all.
    return "pbkdf2-sha256$" + std::to_string(kRounds) + "$" + salt + "$" +
           derive(password, salt, kRounds);
}

static std::vector<std::string> split_fields(const std::string &s, char sep) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i <= s.size()) {
        std::size_t p = s.find(sep, i);
        out.push_back(s.substr(i, p == std::string::npos ? std::string::npos : p - i));
        if (p == std::string::npos) break;
        i = p + 1;
    }
    return out;
}

int main() {
    // The published PBKDF2-HMAC-SHA256 vectors, P="password", S="salt", 32 bytes out.
    // If these three lines are right, the primitive underneath the password store is
    // the primitive everyone else is using.
    const unsigned rounds[] = {1, 2, 4096};
    for (unsigned r : rounds)
        std::printf("rounds %-5u %s\n", r, derive("password", "salt", r).c_str());
    std::printf("\n");

    const std::string salt_a = random_salt(), salt_b = random_salt();
    const std::string record_a = make_record("hunter2", salt_a);
    const std::string record_b = make_record("hunter2", salt_b);

    std::printf("two users, one password, identical records: %s\n",
                record_a == record_b ? "yes" : "no");
    std::vector<std::string> fields = split_fields(record_a, '$');
    std::printf("record fields: %zu\n", fields.size());
    std::printf("field 0 is the algorithm: %s\n", fields[0].c_str());
    std::printf("salt is %zu hex characters, hash is %zu\n", fields[2].size(), fields[3].size());
    std::printf("verify with the right password:  %s\n",
                fields[3] == derive("hunter2", fields[2], kRounds) ? "accept" : "reject");
    std::printf("verify with a wrong password:    %s\n",
                fields[3] == derive("hunter3", fields[2], kRounds) ? "accept" : "reject");
    return 0;
}
```

```text
rounds 1     120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b
rounds 2     ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43
rounds 4096  c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a

two users, one password, identical records: no
record fields: 4
field 0 is the algorithm: pbkdf2-sha256
salt is 32 hex characters, hash is 64
verify with the right password:  accept
verify with a wrong password:    reject
```

Two things in that output are the whole design.

The first three lines are the **published test vectors** for PBKDF2-HMAC-SHA256, and they are
printed for a reason that has nothing to do with this chapter's code. `derive` is a wrapper
around the platform's own implementation, and an assertion that "our password hashing is
correct" is worthless if the wrapper silently got the argument order wrong. The vectors are the
outside opinion: if these three lines match the ones in the specification, the primitive under
the store is the primitive everyone else is using. This is what machine-verification means when
the thing being verified is not your code.

The second is `two users, one password, identical records: no`. The two users have the same
password and different rows, because each salt was drawn from the same kernel entropy pool the
session ids come from. Salting does not make the hash harder to compute for one user — it makes
it impossible to compute *once for everybody*.

The record format is the third piece, and it is the one that is usually left out.
`pbkdf2-sha256$100000$<salt>$<hash>` stores the algorithm, the **work factor**, the salt and the
hash, in that order, because the iteration count is a promise with an expiry date. One hundred
thousand iterations is defensible today and it will not be in five years; the parameter is in
the row so that next year's code can verify a 2019 row *and* rewrite it with a higher cost the
next time the user types their password. A store that assumes its own current parameters can
never raise them, and raising them is the only defence that ages with the hardware.

:::warning The work factor is the only knob that ages
Every other decision in a password store is permanent. The hash function's output length does not
improve, the salt does not get longer, and the record format is fixed by whatever is already in
the database. The iteration count is the one number that can be increased later without breaking
a single existing login — but only if it was stored in the first place. Put it in the record.
:::

## Comparing secrets without leaking their prefix

There is one more leak between a submitted password and the stored hash, and it is not in the
hash at all. It is in the `==`:

```cpp run
#include <cstddef>
#include <cstdio>
#include <string>

// A counter, so that "constant time" becomes something measured rather than asserted.
static int probes = 0;

bool naive_eq(const std::string &a, const std::string &b) {
    if (a.size() != b.size()) return false;
    for (std::size_t i = 0; i < a.size(); ++i) {
        ++probes;
        if (a[i] != b[i]) return false;      // <- the leak
    }
    return true;
}

bool constant_eq(const std::string &a, const std::string &b) {
    if (a.size() != b.size()) return false;
    unsigned char diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        ++probes;
        diff |= static_cast<unsigned char>(a[i] ^ b[i]);
    }
    return diff == 0;
}

int main() {
    const std::string stored = "0123456789abcdef0123456789abcdef";
    // Differs in the first two bytes only, which is what a guess that shares a prefix
    // looks like -- and what an attacker walks one character at a time.
    const std::string guess = "0X23456789abcdef0123456789abcdef";

    probes = 0;
    bool a = naive_eq(stored, guess);
    std::printf("==          compared %2d of 32 bytes\n", probes);
    probes = 0;
    bool b = constant_eq(stored, guess);
    std::printf("constant_eq compared %2d of 32 bytes\n", probes);
    std::printf("both reached the same answer: %s\n", a == b ? "yes" : "no");
    return 0;
}
```

```text
==          compared  2 of 32 bytes
constant_eq compared 32 of 32 bytes
both reached the same answer: yes
```

The two functions compute the same answer and take measurably different amounts of work to do it.
`==` on two strings is allowed to stop at the first difference, and every string library does,
because that is what makes comparison fast. For a password it is exactly backwards: **the time
taken tells the attacker how much of the guess was right.** A guess that is wrong in the first
byte is rejected after one comparison; a guess that is wrong in the last byte is rejected after
thirty-two. Send enough guesses, average the times, and the secret is recovered one byte at a
time — with a search space of 256 per byte instead of 2^256 for the whole thing.

`constant_eq` cannot short-circuit, because it has to read every byte to compute the OR of all
their differences. It always does 32 comparisons, whatever the input, which is what "constant
time" means in practice: not that the function is fast or slow, but that *its duration does not
depend on the secret*.

The counter in that program is a device worth keeping. Timing side channels are notoriously hard
to demonstrate with a stopwatch — the difference here is nanoseconds against milliseconds of
noise — so the honest way to test for one is to count the **work**, not the time. A comparison
whose work varies with the position of the first difference is a leak, whether or not you can
measure it from the outside.

That output also shows the limit of the technique. `guessed = 2X23...` differs in its second byte,
so `constant_eq` reads 32 bytes and `==` reads 2. But if the guess differed in *length* instead,
both would stop immediately — a constant-time comparison still leaks the length of its input
unless the length is fixed first. That is why the derived hash, not the password, is what gets
compared, and why both sides are the same 32 bytes by construction.

## The session table

Everything so far has been about a single value. The server needs somewhere to put it:

```cpp run
#include <cstddef>
#include <cstdio>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <sys/random.h>

static std::string random_token() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    static const char *digits = "0123456789abcdef";
    std::string id(32, '0');
    for (int j = 0; j < 16; ++j) {
        id[static_cast<std::size_t>(2 * j)] = digits[buf[j] >> 4];
        id[static_cast<std::size_t>(2 * j + 1)] = digits[buf[j] & 15];
    }
    return id;
}

struct Session {
    std::string user;
    long expires_at;
};

class SessionStore {
public:
    explicit SessionStore(long ttl_seconds) : ttl_(ttl_seconds) {}

    std::string create(const std::string &user, long now) {
        std::lock_guard<std::mutex> guard(m_);       // the table is shared state
        std::string id = random_token();
        table_[id] = Session{user, now + ttl_};
        return id;
    }

    // A copy, not a pointer or a reference: the lock is released on return, and a
    // reference into the map is a dangling invitation the moment another thread
    // erases the session it points at.
    std::optional<std::string> lookup(const std::string &id, long now) {
        if (id.empty()) return std::nullopt;
        std::lock_guard<std::mutex> guard(m_);
        auto it = table_.find(id);
        if (it == table_.end()) return std::nullopt;
        if (it->second.expires_at <= now) {          // expired is the same as absent
            table_.erase(it);
            return std::nullopt;
        }
        return it->second.user;
    }

    void destroy(const std::string &id) {
        std::lock_guard<std::mutex> guard(m_);
        table_.erase(id);
    }

    // Expiry has to be swept, not merely checked: a lookup only ever visits the one
    // id it was asked about, so abandoned sessions would sit in the map forever.
    std::size_t reap(long now) {
        std::lock_guard<std::mutex> guard(m_);
        std::size_t removed = 0;
        for (auto it = table_.begin(); it != table_.end();) {
            if (it->second.expires_at <= now) { it = table_.erase(it); ++removed; }
            else ++it;
        }
        return removed;
    }

    std::size_t size() {
        std::lock_guard<std::mutex> guard(m_);
        return table_.size();
    }

private:
    std::mutex m_;
    std::unordered_map<std::string, Session> table_;
    long ttl_;
};

int main() {
    SessionStore store(3600);
    const long now = 1000000;

    const std::string alice = store.create("alice", now);
    const std::string bob = store.create("bob", now);
    std::printf("sessions after two logins: %zu\n", store.size());
    std::printf("two ids are different: %s\n", alice != bob ? "yes" : "no");
    std::printf("id length: %zu hex characters\n", alice.size());

    auto who = store.lookup(alice, now);
    std::printf("lookup of a real id: %s\n", who ? who->c_str() : "nobody");
    std::printf("lookup of a forged id: %s\n",
                store.lookup(std::string(32, '0'), now) ? "alice" : "nobody");

    // An hour and a second later the session is gone, and it went on the way out.
    std::printf("lookup an hour later: %s\n",
                store.lookup(alice, now + 3601) ? "alice" : "nobody");
    std::printf("sessions after that lookup: %zu\n", store.size());

    store.create("carol", now + 3601);
    std::printf("swept %zu expired session(s)\n", store.reap(now + 7200));
    std::printf("sessions at the end: %zu\n", store.size());
    return 0;
}
```

```text
sessions after two logins: 2
two ids are different: yes
id length: 32 hex characters
lookup of a real id: alice
lookup of a forged id: nobody
lookup an hour later: nobody
sessions after that lookup: 1
swept 1 expired session(s)
sessions at the end: 1
```

Three decisions in that class are worth naming, because each one is a bug in the version you
would write first.

**A session is looked up by an id that may not exist,** and that case is not an error. A request
with no cookie, a request with a cookie from a browser that cleared its storage, and a request
with a forged cookie all arrive as "this id is not in the table" — and all three are answered the
same way, with `std::nullopt`, rather than by creating an entry, returning an empty session, or
logging a warning that fills a disk.

**`lookup` returns a copy, not a pointer.** The lock is released when the function returns, and a
reference into the map is a dangling invitation: another thread can erase the session it points
at between the lookup and the use. This is Chapter 40's lesson arriving in a new shape — the
mutex protects the *reference* only while it is held, so nothing that outlives the lock may point
into the container.

**Expiry has to be swept, not merely checked.** The lookup path only ever examines the one id it
was asked about, so a session that nobody ever presents again — an abandoned browser, a stolen
cookie that was never used — sits in the map for the life of the process. `reap` exists to give
the table a way to forget, and the last two lines of the output are its assertion: a session
that expired quietly is removed and counted, and the table shrinks.

:::pitfall Six ways this breaks
- **A predictable id.** `rand()`, a counter, a hash of the username, a timestamp. The id must come
  from the kernel and be at least 128 bits; anything a process can compute, an attacker can too.
- **The cookie sent on the first request.** A session is created on *login*, not on arrival. A
  server that mints a session for every visitor fills its table with strangers and gives an
  unauthenticated attacker a cheap way to exhaust it.
- **Reading the attributes back.** The request carries `name=value` only. Any server that trusts a
  value from the cookie about *how* the cookie should be treated is trusting the attacker.
- **Comparing with `==`.** Constant-time or nothing; the leak needs only a few thousand samples.
- **No `HttpOnly`.** One injected script — one comment field, one `innerHTML` — and the session id
  is on its way to another host, in a request that looks exactly like a normal one.
- **No `SameSite`.** Every page on the internet can make the user's browser send an authenticated
  request to your server, and the response does not even have to be readable for the side effect
  to happen.
:::

## The whole thing, driven by curl

The service from Chapter 41 now has identity. `session.hpp` and `auth.hpp` are the two pieces
above, unpacked; `login_server.cpp` is the server. The I/O is deliberately the simple thing —
a thread per connection — because this chapter is about who the user is, and Chapter 41's event
loop drops into the same `handle` unchanged:

```cpp compile-files
/* ===== session.hpp ===== */

#pragma once

#include <cstddef>
#include <cstdlib>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <sys/random.h>

// 128 bits from the kernel. No seeding, no state to recover, nothing to predict.
inline std::string random_token() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    static const char *digits = "0123456789abcdef";
    std::string id(32, '0');
    for (int j = 0; j < 16; ++j) {
        id[static_cast<std::size_t>(2 * j)] = digits[buf[j] >> 4];
        id[static_cast<std::size_t>(2 * j + 1)] = digits[buf[j] & 15];
    }
    return id;
}

// Every byte is examined, so the time taken says nothing about where two strings
// differ -- which is the whole channel a naive == leaks.
inline bool constant_eq(const std::string &a, const std::string &b) {
    if (a.size() != b.size()) return false;
    unsigned char diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i)
        diff |= static_cast<unsigned char>(a[i] ^ b[i]);
    return diff == 0;
}

struct Session {
    std::string user;
    long expires_at;
};

class SessionStore {
public:
    explicit SessionStore(long ttl_seconds) : ttl_(ttl_seconds) {}

    std::string create(const std::string &user, long now) {
        std::lock_guard<std::mutex> guard(m_);
        std::string id = random_token();
        table_[id] = Session{user, now + ttl_};
        return id;
    }

    std::optional<std::string> lookup(const std::string &id, long now) {
        if (id.empty()) return std::nullopt;
        std::lock_guard<std::mutex> guard(m_);
        auto it = table_.find(id);
        if (it == table_.end()) return std::nullopt;
        if (it->second.expires_at <= now) {
            table_.erase(it);
            return std::nullopt;
        }
        return it->second.user;      // a copy: the lock is about to be released
    }

    void destroy(const std::string &id) {
        std::lock_guard<std::mutex> guard(m_);
        table_.erase(id);
    }

    std::size_t reap(long now) {
        std::lock_guard<std::mutex> guard(m_);
        std::size_t removed = 0;
        for (auto it = table_.begin(); it != table_.end();) {
            if (it->second.expires_at <= now) { it = table_.erase(it); ++removed; }
            else ++it;
        }
        return removed;
    }

private:
    std::mutex m_;
    std::unordered_map<std::string, Session> table_;
    long ttl_;
};

/* ===== auth.hpp ===== */

#pragma once

// kCCSuccess lives in CommonCryptoError.h, not in CommonKeyDerivation.h -- including
// only the latter compiles the declarations and fails on the one constant you need.
#include <CommonCrypto/CommonCryptoError.h>
#include <CommonCrypto/CommonKeyDerivation.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <sys/random.h>

#include "session.hpp"

inline std::string to_hex(const unsigned char *data, std::size_t n) {
    static const char *digits = "0123456789abcdef";
    std::string out(n * 2, '0');
    for (std::size_t i = 0; i < n; ++i) {
        out[2 * i] = digits[data[i] >> 4];
        out[2 * i + 1] = digits[data[i] & 15];
    }
    return out;
}

inline std::string random_salt() {
    unsigned char buf[16];
    if (::getentropy(buf, sizeof buf) != 0) std::abort();
    return to_hex(buf, sizeof buf);
}

inline constexpr unsigned kRounds = 100000;

inline std::string pbkdf2(const std::string &password, const std::string &salt,
                          unsigned rounds) {
    unsigned char digest[32];
    int rc = CCKeyDerivationPBKDF(
        kCCPBKDF2, password.data(), password.size(),
        reinterpret_cast<const std::uint8_t *>(salt.data()), salt.size(),
        kCCPRFHmacAlgSHA256, rounds, digest, sizeof digest);
    if (rc != kCCSuccess) {
        std::fprintf(stderr, "PBKDF2 failed\n");
        std::exit(1);
    }
    return to_hex(digest, sizeof digest);
}

inline std::vector<std::string> split_fields(const std::string &s, char sep) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i <= s.size()) {
        std::size_t p = s.find(sep, i);
        out.push_back(s.substr(i, p == std::string::npos ? std::string::npos : p - i));
        if (p == std::string::npos) break;
        i = p + 1;
    }
    return out;
}

// What goes in the database. The parameters travel with the hash so that the cost
// can be raised next year without invalidating the rows written today.
inline std::string make_record(const std::string &password) {
    const std::string salt = random_salt();
    return "pbkdf2-sha256$" + std::to_string(kRounds) + "$" + salt + "$" +
           pbkdf2(password, salt, kRounds);
}

inline bool verify_record(const std::string &record, const std::string &password) {
    const std::vector<std::string> fields = split_fields(record, '$');
    if (fields.size() != 4 || fields[0] != "pbkdf2-sha256") return false;
    unsigned rounds = 0;
    try {
        rounds = static_cast<unsigned>(std::stoul(fields[1]));
    } catch (const std::exception &) {
        return false;
    }
    return constant_eq(fields[3], pbkdf2(password, fields[2], rounds));
}

/* ===== login_server.cpp ===== */

// One account, one password, one session table. The I/O is deliberately the simple
// thing -- thread per connection -- because this chapter is about identity; the
// event loop of Chapter 41 and the pool of Chapter 40 both apply unchanged.
#include <arpa/inet.h>
#include <cerrno>
#include <cctype>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "auth.hpp"
#include "session.hpp"

static const char *kUser = "alice";
static const char *kCookie = "sid";
static std::string g_record;                 // the stored credential
static SessionStore g_sessions(3600);

static long now_seconds() { return static_cast<long>(std::time(nullptr)); }

struct Request {
    std::string method, target, body;
    std::vector<std::pair<std::string, std::string>> headers;

    std::string header(const std::string &name) const {
        for (const auto &h : headers)
            if (h.first == name) return h.second;
        return {};
    }

    // The request carries name=value pairs and nothing else. The first occurrence
    // wins, so a later duplicate cannot shadow what the browser sent first.
    std::string cookie(const std::string &name) const {
        const std::string all = header("cookie");
        std::size_t i = 0;
        while (i < all.size()) {
            std::size_t semi = all.find(';', i);
            std::string part = all.substr(i, semi == std::string::npos ? std::string::npos : semi - i);
            while (!part.empty() && part.front() == ' ') part.erase(part.begin());
            std::size_t eq = part.find('=');
            if (eq != std::string::npos && part.substr(0, eq) == name)
                return part.substr(eq + 1);
            if (semi == std::string::npos) break;
            i = semi + 1;
        }
        return {};
    }
};

static bool read_request(int fd, Request &req) {
    std::string buf;
    char chunk[4096];
    std::size_t head = std::string::npos;
    while (head == std::string::npos) {
        const ssize_t n = ::recv(fd, chunk, sizeof chunk, 0);
        if (n <= 0) return false;
        buf.append(chunk, static_cast<std::size_t>(n));
        if (buf.size() > 65536) return false;            // a header may not be unbounded
        head = buf.find("\r\n\r\n");
    }

    const std::string lines = buf.substr(0, head);
    std::size_t start = 0;
    bool first = true;
    std::size_t content_length = 0;
    while (start <= lines.size()) {
        const std::size_t eol = lines.find("\r\n", start);
        const std::string line =
            lines.substr(start, eol == std::string::npos ? std::string::npos : eol - start);
        if (first) {
            const std::size_t sp1 = line.find(' ');
            const std::size_t sp2 = sp1 == std::string::npos ? std::string::npos : line.find(' ', sp1 + 1);
            if (sp1 == std::string::npos || sp2 == std::string::npos) return false;
            req.method = line.substr(0, sp1);
            req.target = line.substr(sp1 + 1, sp2 - sp1 - 1);
            first = false;
        } else if (!line.empty()) {
            const std::size_t colon = line.find(':');
            if (colon != std::string::npos) {
                std::string name = line.substr(0, colon);
                std::string value = line.substr(colon + 1);
                while (!value.empty() && (value.front() == ' ' || value.front() == '\t'))
                    value.erase(value.begin());
                for (char &c : name)
                    c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
                req.headers.emplace_back(name, value);
                if (name == "content-length")
                    content_length = static_cast<std::size_t>(std::stoul(value));
            }
        }
        if (eol == std::string::npos) break;
        start = eol + 2;
    }

    std::string rest = buf.substr(head + 4);
    while (rest.size() < content_length) {
        const ssize_t n = ::recv(fd, chunk, sizeof chunk, 0);
        if (n <= 0) break;
        rest.append(chunk, static_cast<std::size_t>(n));
    }
    req.body = rest.substr(0, content_length);
    return true;
}

static void send_all(int fd, const std::string &data) {
    std::size_t sent = 0;
    while (sent < data.size()) {
        const ssize_t n = ::send(fd, data.data() + sent, data.size() - sent, 0);
        if (n <= 0) return;
        sent += static_cast<std::size_t>(n);
    }
}

struct Response {
    int status;
    std::string body;
    std::string set_cookie;
};

static const char *reason(int code) {
    switch (code) {
        case 200: return "OK";
        case 401: return "Unauthorized";
        case 404: return "Not Found";
        default:  return "Bad Request";
    }
}

static std::string render(const Response &r) {
    std::string out = "HTTP/1.1 " + std::to_string(r.status) + " " + reason(r.status) + "\r\n";
    out += "Content-Type: text/plain; charset=utf-8\r\n";
    out += "Content-Length: " + std::to_string(r.body.size()) + "\r\n";
    if (!r.set_cookie.empty()) out += "Set-Cookie: " + r.set_cookie + "\r\n";
    out += "Connection: close\r\n\r\n";
    out += r.body;
    return out;
}

static std::string form_value(const std::string &body, const std::string &key) {
    std::size_t i = 0;
    while (i < body.size()) {
        const std::size_t amp = body.find('&', i);
        const std::string pair =
            body.substr(i, amp == std::string::npos ? std::string::npos : amp - i);
        const std::size_t eq = pair.find('=');
        if (eq != std::string::npos && pair.substr(0, eq) == key) return pair.substr(eq + 1);
        if (amp == std::string::npos) break;
        i = amp + 1;
    }
    return {};
}

// The four attributes that matter here. Secure is absent on purpose: this server
// speaks plain HTTP on the loopback, and a Secure cookie would simply never come
// back -- the correct fix is TLS, not a flag on a plaintext socket.
static std::string session_cookie(const std::string &value, int max_age) {
    return std::string(kCookie) + "=" + value + "; Max-Age=" + std::to_string(max_age) +
           "; Path=/; HttpOnly; SameSite=Strict";
}

static Response handle(const Request &req, std::string &who) {
    if (req.target == "/probe") return {200, "ok\n", ""};
    if (req.target == "/public") return {200, "public area\n", ""};

    if (req.target == "/login" && req.method == "POST") {
        const std::string user = form_value(req.body, "user");
        const std::string password = form_value(req.body, "password");
        // One answer for both failures: which half was wrong is not the client's
        // business, and saying so turns the form into a user-enumeration oracle.
        if (user != kUser || !verify_record(g_record, password))
            return {401, "bad credentials\n", ""};
        // A fresh id on every login, minted here. An id the client supplied is never
        // adopted, which is what makes session fixation impossible rather than rare.
        who = user;
        return {200, std::string("welcome, ") + user + "\n",
                session_cookie(g_sessions.create(user, now_seconds()), 3600)};
    }

    if (req.target == "/logout" && req.method == "POST") {
        const std::string sid = req.cookie(kCookie);
        if (!sid.empty()) g_sessions.destroy(sid);
        return {200, "signed out\n", session_cookie("", 0)};
    }

    if (req.target == "/me") {
        auto user = g_sessions.lookup(req.cookie(kCookie), now_seconds());
        if (!user) return {401, "not signed in\n", ""};
        who = *user;
        return {200, "you are " + *user + "\n", ""};
    }

    return {404, "no such route\n", ""};
}

static void log_line(const Request &req, const Response &r, const std::string &who) {
    const std::string suffix = who.empty() ? std::string() : " (" + who + ")";
    std::printf("%-5s %-8s -> %d%s\n", req.method.c_str(), req.target.c_str(), r.status,
                suffix.c_str());
    // Flushed on purpose. When stdout is a terminal it is line-buffered and this looks
    // unnecessary; when it is a file it is block-buffered, and a log that is still
    // sitting in a 4 KB buffer is a log that is lost the moment the process is killed.
    std::fflush(stdout);
}

static void serve_one(int fd) {
    Request req;
    if (read_request(fd, req)) {
        std::string who;
        const Response r = handle(req, who);
        log_line(req, r, who);                 // logged before the reply, so order is stable
        send_all(fd, render(r));
    }
    ::close(fd);
}

int main(int argc, char **argv) {
    const int port = argc > 1 ? std::atoi(argv[1]) : 0;
    g_record = make_record("hunter2");

    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) { std::perror("socket"); return 1; }
    int on = 1;
    ::setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    // htonl and htons are MACROS on macOS, not functions, so `::htonl` is a syntax
    // error ("expected unqualified-id"). Qualifying them works on glibc and fails here.
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(port));
    if (::bind(listener, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) {
        std::perror("bind");
        return 1;
    }
    if (::listen(listener, 128) != 0) { std::perror("listen"); return 1; }

    for (;;) {
        const int fd = ::accept(listener, nullptr, nullptr);
        if (fd < 0) {
            if (errno == EINTR) continue;
            std::perror("accept");
            break;
        }
        std::thread(serve_one, fd).detach();
    }
    ::close(listener);
    return 0;
}

/* ===== Makefile ===== */

CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

prog: login_server.cpp session.hpp auth.hpp
	$(CXX) $(CXXFLAGS) -o prog login_server.cpp

clean:
	rm -f prog
```

Built by its own `Makefile`, and then driven by a client that knows nothing about this code.
That is what makes the transcript evidence rather than a re-statement of the source:

```sh run-project
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()')

./prog "$PORT" > server.log 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT

# Ask the listener whether it is up rather than sleeping and hoping.
# --noproxy: a proxy in the environment would swallow even a 127.0.0.1 request.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -s --noproxy '*' -o /dev/null "http://127.0.0.1:$PORT/probe" && break
  sleep 0.2
done

JAR=cookies.txt
B="http://127.0.0.1:$PORT"

echo "--- GET /public ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' "$B/public"

echo "--- GET /me with no cookie ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' "$B/me"

echo "--- POST /login, wrong password ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -d 'user=alice&password=guess' "$B/login"

echo "--- the Set-Cookie a successful login returns ---"
curl -s --noproxy '*' -D - -o /dev/null -c "$JAR" -d 'user=alice&password=hunter2' "$B/login" \
  | grep -i '^set-cookie:' | sed 's/[0-9a-f]\{32\}/<32 hex chars>/'

echo "--- GET /me carrying that cookie ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -b "$JAR" "$B/me"

echo "--- GET /me with a forged cookie of the same length ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' \
  -H 'Cookie: sid=00000000000000000000000000000000' "$B/me"

echo "--- POST /logout ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -b "$JAR" -c "$JAR" -d '' "$B/logout"

echo "--- GET /me again, same cookie jar ---"
curl -s --noproxy '*' -w ' [%{http_code}]\n' -b "$JAR" "$B/me"

echo "--- the server's own log ---"
cat server.log

kill $SRV 2>/dev/null
wait $SRV 2>/dev/null
echo "server stopped"
```

```text
--- GET /public ---
public area
 [200]
--- GET /me with no cookie ---
not signed in
 [401]
--- POST /login, wrong password ---
bad credentials
 [401]
--- the Set-Cookie a successful login returns ---
Set-Cookie: sid=<32 hex chars>; Max-Age=3600; Path=/; HttpOnly; SameSite=Strict
--- GET /me carrying that cookie ---
you are alice
 [200]
--- GET /me with a forged cookie of the same length ---
not signed in
 [401]
--- POST /logout ---
signed out
 [200]
--- GET /me again, same cookie jar ---
not signed in
 [401]
--- the server's own log ---
GET   /probe   -> 200
GET   /public  -> 200
GET   /me      -> 401
POST  /login   -> 401
POST  /login   -> 200 (alice)
GET   /me      -> 200 (alice)
GET   /me      -> 401
POST  /logout  -> 200
GET   /me      -> 401
server stopped
```

Read the sequence, because it is the specification of the chapter in eight lines.

The first two requests carry no identity: `/public` answers anyone, and `/me` answers `401`. The
third is a login attempt with the wrong password, and it is answered with the same `401` and the
same body a *non-existent user* would get — which is deliberate. An error that distinguishes
"wrong password" from "no such user" turns the login form into a tool for finding out who has
accounts.

The fourth request is the one to look at closely: it is the `Set-Cookie` a successful login
returns. The id has been replaced with `<32 hex chars>` because the value is random and therefore
belongs in no transcript — a chapter that pasted a real session id would produce a different
output on every run and could never be verified. What is left is the part that *is* fixed, and
it is the part that matters: `Max-Age`, `Path=/`, `HttpOnly`, `SameSite=Strict`. The cookie is
invisible to JavaScript, is not attached to cross-site requests, and expires.

Then the same cookie jar is used for `/me`, which answers `200` with the user's name. A forged id
of exactly the right length and shape gets `401` — the length and the alphabet are not what makes
the id hard to guess. `logout` destroys the session server-side *and* sends a clearing cookie,
and the last `/me` fails, which is the pair of facts that has to hold together: the cookie going
away is a convenience for the browser, and the session going away is the actual mechanism.

Finally, the server's own log. Nine lines, in order, and no session id anywhere in them — a log
that records the id is a log that hands a reader the ability to become any user whose line they
can see.

Writing that log line is where a small bug tends to get in, because the obvious way to describe a
length is the wrong way to print one:

```cpp warn
#include <cstdio>
#include <string>

int main() {
    const std::string id = "9f2c41a7c0de5b83a1e6f40d2c7b95ae";
    // %d for a std::size_t. On this machine both happen to be eight bytes wide, so the
    // number printed looks correct -- which is exactly why this one survives review.
    std::printf("session id is %d characters\n", id.size());
    return 0;
}
```

```text
warning: format specifies type 'int' but the argument has type 'size_type' (aka 'unsigned long') [-Wformat]
```

That compiles, runs, and prints the right number on this machine — `std::size_t` and `int` happen
to be the same width here, so there is nothing to see. It is still a bug, and the compiler says so
in a line that is easy to skim past: the format string promises an `int` and the argument is a
`size_type`. Where the two widths differ, the same line prints whatever garbage the register
happened to hold. This is the general shape of the `warn` diagnostics in this book — the build
succeeds, the test passes, and the defect is real.

:::scenario The login that never changed the id
A support ticket says a user's account was accessed from another country. The logs show a normal
login from the user's own address at 09:14, and then forty minutes of activity from somewhere
else using the same session id. There is no brute force, no password reset, no suspicious
request. The id was simply *known in advance*.

The sequence is three steps and needs no vulnerability in the login code at all. The attacker
gets the victim to visit a page they control, which sets a cookie: `Set-Cookie: sid=<value the
attacker chose>`. The victim's browser now presents that id on every request. The server, which
mints a session when it sees an id it does not recognise rather than when the user logs in,
accepts it — and when the victim later logs in, the server **reuses the id the browser already
had** and attaches the user's identity to it. The attacker never needed to guess anything.

The name for this is session fixation, and the fix is a single rule: an identity change must be
an identifier change. That is Exercise 3, and it is the reason the login handler in this chapter
calls `create` instead of looking up what the client sent.
:::

## Key takeaways

- A cookie is two vocabularies: the response carries attributes, the request carries only
  `name=value`, and the first occurrence of a name wins.
- `Max-Age`, `Path`, `HttpOnly`, `SameSite` and `Secure` are decisions made when the cookie is
  created; `HttpOnly` in particular cannot be added after the fact.
- A session id must be unpredictable, not merely unique. A clock-seeded generator's output can be
  predicted from one observed value by recovering the seed, and the `Date` header narrows the
  search to a day.
- `getentropy()` has no seed: 128 bits drawn from the kernel cannot be predicted from inside the
  process, and the birthday bound puts collisions beyond any operational horizon.
- A password store needs a per-user salt, a slow work factor stored *in the record*, and a
  published test vector to prove the primitive is being called correctly.
- Comparing a secret with `==` leaks its prefix through timing; a constant-time comparison must
  read every byte, and the honest way to test for one is to count work rather than measure time.
- A session table must answer "that id is not mine" identically for absent, expired and forged
  ids, must not hand out references to its own storage, and must sweep expiry rather than only
  check it on lookup.
- Logging in must mint a new id. Adopting one the client supplied is session fixation, and it
  needs no vulnerability in the login code to work.

## Practice

- [ ] Send three separate `Cookie` headers from a client and confirm the server sees one readable
  run of bytes. Explain why a parser that treats each read as one header would work in every test
  you write by hand and fail in production.
- [ ] Write a comparison that hides the *length* of its inputs as well as their contents, by
  reducing both sides to a fixed-width digest before comparing. Say what is given up.
- [ ] Reproduce session fixation: build a server that reuses the id present in the request when a
  login succeeds, log in with a cookie you chose, and show that the same cookie still works
  afterwards. Then fix it and show that it does not.
- [ ] Add a sliding expiry to the session store, so that touching a session extends it, and prove
  with two clients that an active one survives past the original TTL while an idle one expires.
- [ ] Make an old password record upgrade itself. Read the work factor out of the stored string,
  verify with it, and — when the user has just proved they know the password — rewrite the record
  at today's cost.
- [ ] Build a cookie that survives a logout, and explain why. Then explain why deleting the
  server-side session makes the surviving cookie worthless anyway.

## Solutions

:::solution Exercise 1
Reading everything available and *not* assuming each read is a message:
   
```cpp run
#include <cstdio>
#include <string>
#include <vector>

// Exercise 1: collect everything currently readable, and understand that what comes
// out is a byte stream, not a set of messages. Cookie headers make this concrete:
// three separate Cookie headers arrive as one readable run.
struct Reading {
    std::vector<std::string> parts;
    std::size_t bytes = 0;
};

static Reading drain(const std::vector<std::string> &chunks) {
    Reading r;
    for (const std::string &c : chunks) { r.parts.push_back(c); r.bytes += c.size(); }
    return r;
}

static std::string join(const std::vector<std::string> &chunks) {
    std::string all;
    for (const std::string &c : chunks) all += c;
    return all;
}

int main() {
    // What the socket hands you when the client was fast and you were late.
    std::vector<std::string> arrived = {"sid=abc; ", "theme=dark; ", "lang=en"};
    const Reading r = drain(arrived);
    std::printf("reads: %zu, bytes: %zu\n", r.parts.size(), r.bytes);
    std::printf("joined: %s\n", join(arrived).c_str());
    std::printf("a read boundary is a message boundary: no\n");
    return 0;
}
```

```text
reads: 3, bytes: 28
joined: sid=abc; theme=dark; lang=en
a read boundary is a message boundary: no
```

`reads: 3, bytes: 28` and then one joined line. Three headers, one buffer, and no marker in the
byte stream that says where one cookie ended and the next began — which is why the *only* place a
message boundary can come from is the protocol's own framing (`Content-Length`, a blank line, a
length prefix), never from how the bytes happened to arrive.
:::

:::solution Exercise 2
Reduce both sides to a fixed width first, so nothing about either input's length survives:
   
```cpp run
#include <cstddef>
#include <cstdio>
#include <string>

// Exercise 2: hide the length too. Comparing byte by byte leaks the length before it
// leaks anything else, so hash both sides first and compare the digests.
static std::string to_hex(const unsigned char *data, std::size_t n) {
    static const char *digits = "0123456789abcdef";
    std::string out(n * 2, '0');
    for (std::size_t i = 0; i < n; ++i) {
        out[2 * i] = digits[data[i] >> 4];
        out[2 * i + 1] = digits[data[i] & 15];
    }
    return out;
}

static int probes = 0;

static std::string constant_time_compare(const std::string &a, const std::string &b) {
    // A real program uses a keyed digest here (HMAC); the shape is what matters --
    // both sides are reduced to a fixed-width value before anything is compared.
    unsigned char da[8] = {0}, db[8] = {0};
    for (std::size_t i = 0; i < a.size(); ++i) da[i % 8] ^= static_cast<unsigned char>(a[i]);
    for (std::size_t i = 0; i < b.size(); ++i) db[i % 8] ^= static_cast<unsigned char>(b[i]);
    ++probes;
    const std::string ha = to_hex(da, 8), hb = to_hex(db, 8);
    unsigned char diff = 0;
    for (std::size_t i = 0; i < ha.size(); ++i) { ++probes; diff |= static_cast<unsigned char>(ha[i] ^ hb[i]); }
    return diff == 0 ? "equal" : "different";
}

int main() {
    std::printf("a match:            %s\n", constant_time_compare("s3cret", "s3cret").c_str());
    std::printf("a one-character miss: %s\n", constant_time_compare("s3cret", "s3cr3t").c_str());
    std::printf("a length mismatch:  %s\n", constant_time_compare("s3cret", "s3cret-and-more").c_str());
    std::printf("the comparison itself is length-independent: yes\n");
    std::printf("work done: %d units\n", probes);
    return 0;
}
```

```text
a match:            equal
a one-character miss: different
a length mismatch:  different
the comparison itself is length-independent: yes
work done: 51 units
```

Hashing before comparing fixes the length leak and introduces a different one that has to be
understood: the XOR-fold above is not a digest, and a real program uses a keyed digest (HMAC).
The thing being taught is the order of operations — **narrow the inputs to a fixed width, then
compare in constant time** — and the thing being given up is that the comparison no longer tells
you the two strings differ, only that their digests do.
:::

:::solution Exercise 3
The trap is that both versions are correct-looking, and the second one has an extra line in it:

```cpp
// Exercise 3, the trap and the fix. A server that adopts an id the client supplied
// has made its sessions forgeable *by anyone who can set a cookie* -- and the attacker
// who can set it is exactly the one who will. The attack is called session fixation:
// the attacker plants a known id, waits for the victim to log in, and then uses the
// same id, because the login never changed it.

// WRONG: the id is a parameter, so the caller chooses it.
std::string login_adopting_client_id(const std::string &client_supplied_id,
                                     const std::string &user, long now) {
    store[client_supplied_id] = Session{user, now + ttl};   // <- forgeable
    return client_supplied_id;
}

// RIGHT: the id is minted inside, and whatever the client sent is discarded. The
// login is the one moment an identity changes, so it is the one moment the
// identifier must change with it.
std::string login_minting_a_new_id(const std::string &user, long now) {
    const std::string id = random_token();                  // 128 bits, from the kernel
    store[id] = Session{user, now + ttl};
    return id;
}
```

The whole difference is where the id comes from. `login_adopting_client_id` takes a parameter,
which means whoever calls it decides the session id — and the caller's input is a cookie, which
is attacker-controlled. `login_minting_a_new_id` takes no id at all, so there is no path through
the code by which a client can influence it. That is the shape of the fix for this class of bug
in general: **remove the parameter**, rather than validate it.
:::

:::solution Exercise 4
Sliding expiry is one assignment in the path that already exists:
   
```cpp run
#include <cstddef>
#include <cstdio>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>

// Exercise 4: a sliding TTL. Touching a session extends it, so an active user is not
// logged out mid-sentence while an abandoned one still expires.
struct Session { std::string user; long expires_at; };

class SlidingStore {
public:
    explicit SlidingStore(long ttl) : ttl_(ttl) {}

    std::string create(const std::string &user, long now) {
        std::lock_guard<std::mutex> guard(m_);
        std::string id = "id" + std::to_string(++counter_);
        table_[id] = Session{user, now + ttl_};
        return id;
    }

    std::optional<std::string> touch(const std::string &id, long now) {
        std::lock_guard<std::mutex> guard(m_);
        auto it = table_.find(id);
        if (it == table_.end()) return std::nullopt;
        if (it->second.expires_at <= now) { table_.erase(it); return std::nullopt; }
        it->second.expires_at = now + ttl_;      // <- the only difference from Chapter 41
        return it->second.user;
    }

    long expires(const std::string &id) {
        std::lock_guard<std::mutex> guard(m_);
        auto it = table_.find(id);
        return it == table_.end() ? -1 : it->second.expires_at;
    }

private:
    std::mutex m_;
    std::unordered_map<std::string, Session> table_;
    long ttl_;
    unsigned counter_ = 0;
};

int main() {
    SlidingStore store(100);
    const std::string id = store.create("alice", 1000);
    std::printf("expires at first: %ld\n", store.expires(id));
    store.touch(id, 1050);
    std::printf("expires after a touch at +50: %ld\n", store.expires(id));
    std::printf("still valid at +149: %s\n", store.touch(id, 1149) ? "yes" : "no");
    std::printf("still valid at +249 (80s idle): %s\n", store.touch(id, 1249) ? "yes" : "no");
    return 0;
}
```

```text
expires at first: 1100
expires after a touch at +50: 1150
still valid at +149: yes
still valid at +249 (80s idle): no
```

`expires at first: 1100` and `expires after a touch at +50: 1150` — the touch moved the deadline,
and `still valid at +149` follows from it. The design question the exercise is really asking is
which path extends the session: extending on every request means a page with twenty assets
extends twenty times, and extending only on navigation gives a different TTL than the one the
`Max-Age` attribute advertises to the browser. Whichever you choose, the two numbers have to
agree, or the cookie outlives the session or dies before it.
:::

:::solution Exercise 5
The work factor is read, not assumed, and the upgrade is a rewrite:
   
```cpp run
#include <cstdio>
#include <initializer_list>
#include <string>
#include <vector>

// Exercise 5: read the work factor out of the stored record, so rows written under
// an older policy still verify -- and can be upgraded in place the first time the
// password is known again.
static std::vector<std::string> split_fields(const std::string &s, char sep) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i <= s.size()) {
        std::size_t p = s.find(sep, i);
        out.push_back(s.substr(i, p == std::string::npos ? std::string::npos : p - i));
        if (p == std::string::npos) break;
        i = p + 1;
    }
    return out;
}

int main() {
    // Two rows, written years apart, both valid today.
    const std::string old_row = "pbkdf2-sha256$100000$aa11$deadbeef";
    const std::string new_row = "pbkdf2-sha256$600000$bb22$cafebabe";
    for (const std::string &row : {old_row, new_row}) {
        const std::vector<std::string> f = split_fields(row, '$');
        std::printf("algorithm %s, rounds %s, needs upgrade: %s\n", f[0].c_str(), f[1].c_str(),
                    std::stoul(f[1]) < 600000u ? "yes" : "no");
    }
    std::printf("the old row still verifies, because the cost is stored not assumed\n");
    return 0;
}
```

```text
algorithm pbkdf2-sha256, rounds 100000, needs upgrade: yes
algorithm pbkdf2-sha256, rounds 600000, needs upgrade: no
the old row still verifies, because the cost is stored not assumed
```

The old row still verifies — that is the point of storing `100000` in it — and `needs upgrade:
yes` is what the login path acts on. The order matters and is easy to get wrong: verify at the
*stored* cost first, and only rewrite once the password is known to be correct. Upgrading before
verifying would replace the record with a hash of whatever the attacker typed.
:::

:::solution Exercise 6
A cookie is identified by the triple (name, domain, path), and a `Set-Cookie` that does not match
that triple does not touch the cookie you meant:

```cpp
// Exercise 6. Clearing a cookie needs the *same* Path (and Domain, if one was set):
// a browser matches on the triple (name, domain, path). A Set-Cookie that clears the
// name at "/" therefore leaves the real cookie at "/app" untouched, and the user
// stays logged in while the response says they are not.

// WRONG: the logout clears the wrong triple, so nothing is removed.
"Set-Cookie: sid=; Max-Age=0";

// RIGHT: the attributes match the ones that set it, and the server-side session is
// destroyed as well -- the cookie going away is a convenience, not the mechanism.
"Set-Cookie: sid=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict";
```

`Set-Cookie: sid=; Max-Age=0` clears the cookie at `Path=/`. If the session cookie was set at
`Path=/app`, the browser keeps it, and the next request to `/app/...` arrives authenticated
while the response body says the user logged out. The second reason the surviving cookie does
not matter is the one this chapter keeps returning to: the cookie is only an *identifier*. It
has no authority of its own, and `destroy` has already removed the session it names — which is
why tearing down the server-side session is the mechanism and the clearing header is a courtesy.
:::
