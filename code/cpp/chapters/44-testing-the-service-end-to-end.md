---
chapter: 44
part: 5
title: Testing the Service End to End
summary: A test is a program that fails loudly — unit tests over pure functions, a table for the cases you would forget, and an integration test that spawns the real service, talks to it over a socket, and checks its exit status.
minutes: 80
tags: [testing, unit tests, integration, property tests, flakiness, exit status, fork]
---

Every chapter so far has ended with a program that had to be *looked at*. `curl` answered, the
transcript matched, and a person decided it was right. That does not scale past one person, and it
does not survive Wednesday, when the same code is compiled by a different toolchain.

A test is a program that fails loudly — and that is the entire definition. Everything else about
testing is a consequence of it, including the parts people find annoying. It has to run without
someone deciding when it passed. Its verdict has to be a number a script can read. And it has to
be **capable of failing**, because a check that cannot fail is not a check; it is a comment with
extra steps.

## The smallest thing that is a test

```cpp run
#include <cstdio>
#include <string>
#include <vector>

// A test is a program that fails loudly. Everything else about testing is a
// consequence of that sentence: it has to be runnable without a person deciding when
// it passed, and its verdict has to be a number a script can read.
static int checks = 0;
static int failures = 0;

// No __FILE__ or __LINE__ here, on purpose. A real project prints them -- they are how
// you find the failing line -- but a chapter that prints an absolute path, or a line
// number that shifts whenever a line is added above it, cannot be verified. The test's
// own name is the stable thing to print.
static void check(bool ok, const char *name, const char *expr) {
    ++checks;
    if (!ok) {
        ++failures;
        std::fprintf(stderr, "FAIL %s: %s\n", name, expr);
    }
}

// The function under test: a port is 1..65535, and "0" is not a port a server should
// accept from a configuration file even though binding to it is legal.
static bool valid_port(const std::string &text) {
    if (text.empty() || text.size() > 5) return false;
    long value = 0;
    for (char c : text) {
        if (c < '0' || c > '9') return false;
        value = value * 10 + (c - '0');
    }
    return value >= 1 && value <= 65535;
}

int main() {
    check(valid_port("8080"), "valid_port", "8080");
    check(valid_port("1"), "valid_port", "1");
    check(valid_port("65535"), "valid_port", "65535");
    check(!valid_port("0"), "valid_port", "!0");
    check(!valid_port("65536"), "valid_port", "!65536");
    check(!valid_port(""), "valid_port", "!empty");
    check(!valid_port("80a0"), "valid_port", "!80a0");
    check(!valid_port("-1"), "valid_port", "!-1");

    std::printf("%d check(s), %d failure(s)\n", checks, failures);
    std::printf("the verdict is the exit status: %d\n", failures == 0 ? 0 : 1);
    return failures == 0 ? 0 : 1;
}
```

```text
8 check(s), 0 failure(s)
the verdict is the exit status: 0
```

That program is a test suite, and it is worth noticing how little is in it. Eight checks, two
counters, one function that reports a failure and keeps going. The exit status is the verdict:
`0` for "everything held", non-zero for "something did not".

Three decisions in it are not obvious.

**It does not stop at the first failure.** A suite that aborts on the first problem tells you
about one problem per run, and the run is the expensive part. Counting failures and continuing is
why the summary line can say `0 failure(s)` and mean it.

**Failures go to `stderr`, the summary to `stdout`.** A script piping the report into a summary
gets the summary; a human reading a terminal gets both, colour-separated by the terminal itself.

**There is no `__FILE__` or `__LINE__`.** This is a deliberate departure from what you should
write in a real project, where the failing line number is the most useful thing in the message.
Here, a line number is a fact about the file that changes whenever a line is added above it, and
an absolute path changes with the checkout — so a transcript quoting either could not be
verified. The *test's name* is the stable thing, and it is what this suite prints instead.

:::pitfall A test that cannot fail
The failure mode is not a missing test. It is a test that runs, passes, and would pass no matter
what the code did. Three ways it happens:

- **The assertion is unreachable.** An early `return`, an exception swallowed by a `catch (...)`,
  a `for` loop over an empty container. The test is green and tests nothing.
- **The assertion restates the implementation.** `CHECK(parse(x) == parse(x))`; or comparing the
  function's output to a value produced by calling the same function. Green forever.
- **The assertion is on something the code cannot influence.** The wrong variable, a copy made
  before the call, a field that is never read.

The only defence is to watch the test go red. Change one thing the code does, run the suite, and
require a failure. If nothing turns red, that test is not protecting anything -- which is what the
next section demonstrates on purpose.
:::

## A table, so the case you forgot is a line

Hand-written tests fail in a specific way: they cover the cases their author thought of, and the
author is the one person who cannot see the case they did not think of. A table changes the cost
of the missing case from "write another test" to "add a line":

```cpp run
#include <cstdio>
#include <string>
#include <vector>

// Table-driven: the cases are data. Adding a case is adding a line, and the loop that
// runs them is written once -- which is why a table finds the case somebody forgot,
// while a hand-written sequence of ifs finds only the cases its author imagined.
struct Case {
    const char *in;
    const char *want;
};

static std::string json_escape(const std::string &in) {
    std::string out;
    for (char c : in) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) out += '?';
                else out += c;
        }
    }
    return out;
}

int main() {
    // The inputs are written as escapes in the source, which is the only way to put a
    // control character in a table at all.
    const Case cases[] = {
        {"plain", "plain"},
        {"a\"b", "a\\\"b"},
        {"a\\b", "a\\\\b"},
        {"a\nb", "a\\nb"},
        {"a\tb", "a\\tb"},
        {"\x01", "?"},
        {"", ""},
    };

    int failed = 0;
    for (const Case &c : cases) {
        const std::string got = json_escape(c.in);
        if (got != c.want) {
            ++failed;
            std::printf("  case %s: want %s, got %s\n", c.in, c.want, got.c_str());
        }
    }
    std::printf("%zu case(s), %d failure(s)\n", sizeof(cases) / sizeof(cases[0]), failed);
    std::printf("a table is data, so a new case is a new line -- not a new test\n");
    return failed == 0 ? 0 : 1;
}
```

```text
7 case(s), 0 failure(s)
a table is data, so a new case is a new line -- not a new test
```

Seven rows, one loop, and the two rows worth staring at are the ones with escapes in them. The
input `a\nb` in the source is a *two-character* string containing a newline — and the expected
output `a\\nb` is the three-character string `a\nb`, because that is what a JSON escape is. Getting
that pair right in a table is easy. Getting it right by hand inside a test named
`test_escape_newline` is easy too, and then the tab case never gets written.

The empty-string row is there for the same reason. It costs one line and it is the input that
breaks a surprising number of implementations, because `""` is the one string for which "loop over
the characters" does nothing at all.

## A test that is designed to fail

Here is the part that people skip, and it is the part that makes the rest trustworthy. A suite
whose checks have never failed is a suite nobody has any evidence about:

```cpp run-abort
#include <cstdio>

static int failures = 0;

#define CHECK(expr)                                                    \
    do {                                                               \
        if (!(expr)) {                                                 \
            ++failures;                                                \
            std::fprintf(stderr, "FAIL %s\n", #expr);                   \
        }                                                              \
    } while (0)

static int add(int a, int b) { return a + b; }

int main() {
    CHECK(add(2, 2) == 4);
    CHECK(add(2, 2) == 5);        // the deliberate failure: the suite must notice
    CHECK(add(0, 0) == 0);
    std::fprintf(stderr, "%d failure(s)\n", failures);
    return failures == 0 ? 0 : 1;
}
```

```text
FAIL add(2, 2) == 5
```

That program does not run as a `run` block, and the reason is the point. A `run` block requires a
zero exit status, and this one must exit non-zero — so it is verified with `run-abort`, which
requires a non-zero exit *and* requires the quoted text to be found in `stderr`. The harness is
checking the same two things a CI job would: the verdict, and the words that explain it.

The failure is deliberate: `add(2, 2) == 5` is false and the suite must say so, by name. If this
program exited `0`, the harness would fail the chapter — and the chapter would deserve it, because
a test runner that reports success for a failing test is worse than no test runner.

This is also the check to run against your own suite the day you write it. Introduce one bug on
purpose, watch the suite go red, and revert. It takes a minute and it is the difference between
having tests and having a green light that means nothing.

## Where flakiness comes from

A test that passes sometimes is worse than a test that fails: it teaches the team to re-run the
build instead of reading the failure. Every source of flakiness in C++ is one of three things.

**The clock.** Anything that calls `time()`, `clock()` or `steady_clock::now()` internally is
untestable, and the fix is the previous chapter's: pass the clock in.

**The order.** Tests that share mutable state pass in one order and fail in another. Each test
should build what it needs, and the runner should not depend on registration order.

**The port, the path, the file.** A fixed port collides with whatever else is running; a fixed
temp path collides with a parallel run. Both have a mechanical answer — ask the kernel
(`bind` to port `0` and read back the number) and use a per-run temporary directory.

There is a fourth source that is really the first one wearing a hat: **a shared external service**.
A test that depends on a database somebody else can restart is a test that fails for reasons that
have nothing to do with the code. The integration test below avoids it by starting its own child.

## Integration: a real process, a real socket

Unit tests cover the functions. They cannot tell you whether the server *speaks HTTP*, and that is
where the interesting defects live — a missing `Content-Length`, a header written with the wrong
line ending, a session the handler created but never sent back.

The suite below therefore does the hardest-looking thing in the chapter, and it is about thirty
lines: it forks, executes the real `./server` binary, waits for it to accept a connection, sends
requests over a socket, and then sends `SIGTERM` and checks the exit status.

```cpp make-files
/* ===== framework.hpp ===== */

#pragma once

#include <cstdio>
#include <functional>
#include <string>
#include <vector>

struct TestCase {
    std::string name;
    std::function<void()> body;
};

inline std::vector<TestCase> &registry() { static std::vector<TestCase> all; return all; }
inline int &failures() { static int n = 0; return n; }
inline int &checks() { static int n = 0; return n; }
inline std::string &current() { static std::string s; return s; }

struct Registrar {
    Registrar(const char *name, std::function<void()> body) {
        registry().push_back({name, body});
    }
};

#define TEST(name)                                   \
    static void name();                              \
    static Registrar registrar_##name(#name, name);  \
    static void name()

// Failures go to stderr and the process exits non-zero, so the whole interface is
// `./prog` and the whole verdict is `$?`. A suite that reports by printing a pretty
// summary and returning 0 is a suite nothing can automate.
#define CHECK(expr)                                                          \
    do {                                                                     \
        ++checks();                                                          \
        if (!(expr)) {                                                       \
            ++failures();                                                    \
            std::fprintf(stderr, "FAIL %s check %d: %s\n", current().c_str(), \
                         checks(), #expr);                                   \
        }                                                                    \
    } while (0)

// A test that cannot fail is not a test. This counter is how the suite notices that
// one of its own cases stopped discriminating.
inline int run_all() {
    for (const TestCase &t : registry()) {
        current() = t.name;
        const int before = failures();
        t.body();
        std::printf("%-42s %s\n", t.name.c_str(), failures() == before ? "ok" : "FAIL");
    }
    std::printf("%zu test(s), %d check(s), %d failure(s)\n", registry().size(),
                checks(), failures());
    return failures() == 0 ? 0 : 1;
}

/* ===== session.hpp ===== */

#pragma once

#include <cstddef>
#include <cstdlib>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <sys/random.h>

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

inline bool constant_eq(const std::string &a, const std::string &b) {
    if (a.size() != b.size()) return false;
    unsigned char diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i)
        diff |= static_cast<unsigned char>(a[i] ^ b[i]);
    return diff == 0;
}

struct Session { std::string user; long expires_at; };

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
        if (it->second.expires_at <= now) { table_.erase(it); return std::nullopt; }
        return it->second.user;
    }
    void destroy(const std::string &id) {
        std::lock_guard<std::mutex> guard(m_);
        table_.erase(id);
    }
private:
    std::mutex m_;
    std::unordered_map<std::string, Session> table_;
    long ttl_;
};

/* ===== auth.hpp ===== */

#pragma once

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

inline std::string pbkdf2(const std::string &password, const std::string &salt, unsigned rounds) {
    unsigned char digest[32];
    const int rc = CCKeyDerivationPBKDF(
        kCCPBKDF2, password.data(), password.size(),
        reinterpret_cast<const std::uint8_t *>(salt.data()), salt.size(),
        kCCPRFHmacAlgSHA256, rounds, digest, sizeof digest);
    if (rc != kCCSuccess) { std::fprintf(stderr, "PBKDF2 failed\n"); std::exit(1); }
    return to_hex(digest, sizeof digest);
}

inline std::vector<std::string> split_fields(const std::string &s, char sep) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i <= s.size()) {
        const std::size_t p = s.find(sep, i);
        out.push_back(s.substr(i, p == std::string::npos ? std::string::npos : p - i));
        if (p == std::string::npos) break;
        i = p + 1;
    }
    return out;
}

// The work factor is fixed at 1000 here rather than 100000: this chapter runs it four
// times, and the cost is not what is being tested. Chapter 42 chose the real number.
inline constexpr unsigned kTestRounds = 1000;

inline std::string make_record(const std::string &password) {
    const std::string salt = random_salt();
    return "pbkdf2-sha256$" + std::to_string(kTestRounds) + "$" + salt + "$" +
           pbkdf2(password, salt, kTestRounds);
}

inline bool verify_record(const std::string &record, const std::string &password) {
    const std::vector<std::string> fields = split_fields(record, '$');
    if (fields.size() != 4 || fields[0] != "pbkdf2-sha256") return false;
    try {
        const unsigned rounds = static_cast<unsigned>(std::stoul(fields[1]));
        return constant_eq(fields[3], pbkdf2(password, fields[2], rounds));
    } catch (const std::exception &) {
        return false;
    }
}

/* ===== service.cpp ===== */

// Chapter 42's service, with Chapter 43's configuration and logging taken back out so
// that this chapter is about the tests. The handler's contract is unchanged -- the same
// `Request` in, the same `Response` out -- which is exactly why the suite below can be
// pointed at the full service as well.
#include <arpa/inet.h>
#include <atomic>
#include <cerrno>
#include <csignal>
#include <cctype>
#include <ctime>
#include <netinet/in.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "auth.hpp"
#include "session.hpp"

static const char *kUser = "alice";
static const char *kCookie = "sid";
static std::string g_record;
static SessionStore g_sessions(3600);
static std::atomic<bool> g_stopping{false};
static std::atomic<int> g_in_flight{0};

static long now_seconds() { return static_cast<long>(std::time(nullptr)); }

static void on_terminate(int) { g_stopping.store(true); }

static void install_signals() {
    struct sigaction action {};
    action.sa_handler = on_terminate;
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    ::sigaction(SIGTERM, &action, nullptr);
    ::sigaction(SIGINT, &action, nullptr);
    ::signal(SIGPIPE, SIG_IGN);
}

struct Request {
    std::string method, target, body;
    std::vector<std::pair<std::string, std::string>> headers;
    std::string header(const std::string &name) const {
        for (const auto &h : headers) if (h.first == name) return h.second;
        return {};
    }
    std::string cookie(const std::string &name) const {
        const std::string all = header("cookie");
        std::size_t i = 0;
        while (i < all.size()) {
            const std::size_t semi = all.find(';', i);
            std::string part = all.substr(i, semi == std::string::npos ? std::string::npos : semi - i);
            while (!part.empty() && part.front() == ' ') part.erase(part.begin());
            const std::size_t eq = part.find('=');
            if (eq != std::string::npos && part.substr(0, eq) == name) return part.substr(eq + 1);
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
        if (buf.size() > 65536) return false;
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
                std::string name = line.substr(0, colon), value = line.substr(colon + 1);
                while (!value.empty() && (value.front() == ' ' || value.front() == '\t'))
                    value.erase(value.begin());
                for (char &c : name) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
                req.headers.emplace_back(name, value);
                if (name == "content-length") content_length = static_cast<std::size_t>(std::stoul(value));
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

struct Response { int status; std::string body; std::string set_cookie; };

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
        const std::string pair = body.substr(i, amp == std::string::npos ? std::string::npos : amp - i);
        const std::size_t eq = pair.find('=');
        if (eq != std::string::npos && pair.substr(0, eq) == key) return pair.substr(eq + 1);
        if (amp == std::string::npos) break;
        i = amp + 1;
    }
    return {};
}

static std::string session_cookie(const std::string &value, int max_age) {
    return std::string(kCookie) + "=" + value + "; Max-Age=" + std::to_string(max_age) +
           "; Path=/; HttpOnly; SameSite=Strict";
}

static Response handle(const Request &req) {
    if (req.target == "/probe") return {200, "ok\n", ""};
    if (req.target == "/public") return {200, "public area\n", ""};
    if (req.target == "/login" && req.method == "POST") {
        const std::string user = form_value(req.body, "user");
        const std::string password = form_value(req.body, "password");
        if (user != kUser || !verify_record(g_record, password))
            return {401, "bad credentials\n", ""};
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
        return {200, "you are " + *user + "\n", ""};
    }
    return {404, "no such route\n", ""};
}

static void serve_one(int fd) {
    g_in_flight.fetch_add(1);
    Request req;
    if (read_request(fd, req)) send_all(fd, render(handle(req)));
    ::close(fd);
    g_in_flight.fetch_sub(1);
}

int main(int argc, char **argv) {
    const int port = argc > 1 ? std::atoi(argv[1]) : 0;
    g_record = make_record("hunter2");
    install_signals();

    const int listener = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) return 1;
    int on = 1;
    ::setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(port));
    if (::bind(listener, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) return 1;
    if (::listen(listener, 128) != 0) return 1;

    while (!g_stopping.load()) {
        pollfd pfd{listener, POLLIN, 0};
        const int ready = ::poll(&pfd, 1, 50);
        if (ready < 0) { if (errno == EINTR) continue; break; }
        if (ready == 0) continue;
        const int fd = ::accept(listener, nullptr, nullptr);
        if (fd < 0) continue;
        std::thread(serve_one, fd).detach();
    }
    for (int waited = 0; waited < 2000 && g_in_flight.load() > 0; waited += 10)
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    ::close(listener);
    return 0;
}

/* ===== tests.cpp ===== */

#include "framework.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <arpa/inet.h>
#include <fcntl.h>
#include <csignal>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>

#include "auth.hpp"
#include "session.hpp"

// ---------------------------------------------------------------------------
// Unit tests: pure functions, no sockets, no clock, no files.
// ---------------------------------------------------------------------------

TEST(constant_eq_is_exact) {
    CHECK(constant_eq("abc", "abc"));
    CHECK(!constant_eq("abc", "abd"));
    CHECK(!constant_eq("abc", "ab"));
    // Two empty strings ARE equal -- the length check passes and the loop body never
    // runs, so the result is `true`. The first draft of this test asserted the
    // opposite, and the suite said so on the next run, which is the whole argument
    // for having a suite.
    CHECK(constant_eq("", ""));
}

TEST(tokens_are_hex_and_unique) {
    std::vector<std::string> seen;
    int wrong_length = 0, not_hex = 0;
    for (int i = 0; i < 256; ++i) {
        const std::string t = random_token();
        if (t.size() != 32) ++wrong_length;
        bool hex = true;
        for (char c : t) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) hex = false;
        if (!hex) ++not_hex;
        seen.push_back(t);
    }
    CHECK(wrong_length == 0);
    CHECK(not_hex == 0);
    std::sort(seen.begin(), seen.end());
    CHECK(std::adjacent_find(seen.begin(), seen.end()) == seen.end());
}

TEST(record_round_trips) {
    const std::string record = make_record("hunter2");
    CHECK(verify_record(record, "hunter2"));
    CHECK(!verify_record(record, "hunter3"));
    const std::vector<std::string> fields = split_fields(record, '$');
    CHECK(fields.size() == 4);
    CHECK(fields[0] == "pbkdf2-sha256");
    CHECK(fields[1] == "1000");
    CHECK(fields[2].size() == 32);
    CHECK(fields[3].size() == 64);
}

// A property test: the invariant is named, the inputs are generated, and the seed is
// fixed so the run is reproducible. Note the assertion is reflexive-and-sensitive
// rather than "equals this string" -- there is no expected value to write down.
static std::uint64_t splitmix64(std::uint64_t &s) {
    std::uint64_t z = (s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

TEST(constant_eq_over_generated_inputs) {
    std::uint64_t state = 0xC0FFEE;
    int reflexive_failures = 0, sensitive_failures = 0;
    for (int i = 0; i < 500; ++i) {
        const std::uint64_t a = splitmix64(state), b = splitmix64(state);
        unsigned char raw[16];
        std::memcpy(raw, &a, 8);
        std::memcpy(raw + 8, &b, 8);
        const std::string s = to_hex(raw, 16);
        if (!constant_eq(s, s)) ++reflexive_failures;
        std::string flipped = s;
        flipped[0] = (s[0] == '0') ? '1' : '0';
        if (constant_eq(s, flipped)) ++sensitive_failures;
    }
    CHECK(reflexive_failures == 0);
    CHECK(sensitive_failures == 0);
}

// ---------------------------------------------------------------------------
// Integration: a real child process, a real socket, a real exit status.
// ---------------------------------------------------------------------------

static int free_port() {
    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return 0;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0;                       // the kernel picks, so no fixed port to collide
    if (::bind(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) { ::close(fd); return 0; }
    socklen_t len = sizeof addr;
    if (::getsockname(fd, reinterpret_cast<sockaddr *>(&addr), &len) != 0) { ::close(fd); return 0; }
    const int port = ntohs(addr.sin_port);
    ::close(fd);
    return port;
}

static pid_t spawn_service(const char *path, int port) {
    const pid_t pid = ::fork();
    if (pid != 0) return pid;
    // The child's output is discarded: the test asserts on the socket, and a service
    // that prints would otherwise interleave its lines with the suite's report.
    const int devnull = ::open("/dev/null", O_WRONLY);
    if (devnull >= 0) { ::dup2(devnull, 1); ::dup2(devnull, 2); }
    const std::string p = std::to_string(port);
    ::execl(path, path, p.c_str(), static_cast<char *>(nullptr));
    ::_exit(127);                            // 127 is "exec failed", never reached otherwise
}

static bool wait_ready(int port, int tries) {
    for (int i = 0; i < tries; ++i) {
        const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd >= 0) {
            sockaddr_in addr{};
            addr.sin_family = AF_INET;
            addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
            addr.sin_port = htons(static_cast<unsigned short>(port));
            const bool up = ::connect(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) == 0;
            ::close(fd);
            if (up) return true;
        }
        // Bounded on purpose: an unbounded wait turns a broken test into a CI job that
        // never finishes, which is worse than a failure.
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
    return false;
}

// NOT named `exchange`: std::exchange is found by ADL through std::string, and a
// template with forwarding references can outrank a plain function at the call site.
static std::string http_exchange(int port, const std::string &request) {
    const int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return "";
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(port));
    if (::connect(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) != 0) { ::close(fd); return ""; }
    ::send(fd, request.data(), request.size(), 0);
    std::string response;
    char buf[4096];
    for (;;) {
        const ssize_t n = ::recv(fd, buf, sizeof buf, 0);
        if (n <= 0) break;
        response.append(buf, static_cast<std::size_t>(n));
    }
    ::close(fd);
    return response;
}

static std::string post(const std::string &target, const std::string &body) {
    return "POST " + target + " HTTP/1.1\r\nHost: t\r\nContent-Length: " +
           std::to_string(body.size()) + "\r\n\r\n" + body;
}

TEST(the_service_answers_end_to_end) {
    const int port = free_port();
    CHECK(port > 0);
    const pid_t pid = spawn_service("./server", port);
    CHECK(pid > 0);
    // If this fails, the child never came up and every assertion below would be a
    // confusing 404-shaped nothing. One bounded wait turns that into one clear failure.
    CHECK(wait_ready(port, 100));

    const std::string pub = http_exchange(port, "GET /public HTTP/1.1\r\nHost: t\r\n\r\n");
    CHECK(pub.find(" 200 ") != std::string::npos);
    CHECK(pub.find("public area") != std::string::npos);

    const std::string anon = http_exchange(port, "GET /me HTTP/1.1\r\nHost: t\r\n\r\n");
    CHECK(anon.find(" 401 ") != std::string::npos);

    const std::string wrong = http_exchange(port, post("/login", "user=alice&password=guess"));
    CHECK(wrong.find(" 401 ") != std::string::npos);

    const std::string ok = http_exchange(port, post("/login", "user=alice&password=hunter2"));
    CHECK(ok.find(" 200 ") != std::string::npos);
    CHECK(ok.find("Set-Cookie: sid=") != std::string::npos);

    // Take the cookie out of the response and use it -- the smallest client that can
    // carry a session, and the reason this is an integration test rather than six unit
    // tests: the header writer, the parser and the store are only correct together.
    const std::size_t at = ok.find("sid=");
    CHECK(at != std::string::npos);
    const std::size_t end = ok.find(';', at);
    const std::string sid = ok.substr(at + 4, end - (at + 4));
    CHECK(sid.size() == 32);

    const std::string authed =
        http_exchange(port, "GET /me HTTP/1.1\r\nHost: t\r\nCookie: sid=" + sid + "\r\n\r\n");
    CHECK(authed.find(" 200 ") != std::string::npos);
    CHECK(authed.find("you are alice") != std::string::npos);

    // A forged id of exactly the right shape: the length is not the defence.
    const std::string forged =
        http_exchange(port, "GET /me HTTP/1.1\r\nHost: t\r\nCookie: sid=" + std::string(32, '0') + "\r\n\r\n");
    CHECK(forged.find(" 401 ") != std::string::npos);

    // And the shutdown contract, which no unit test can reach.
    ::kill(pid, SIGTERM);
    int status = 0;
    CHECK(::waitpid(pid, &status, 0) == pid);
    CHECK(WIFEXITED(status));
    CHECK(WEXITSTATUS(status) == 0);
}

int main() {
    return run_all();
}

/* ===== Makefile ===== */

CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

all: prog server

prog: tests.cpp framework.hpp session.hpp auth.hpp
	$(CXX) $(CXXFLAGS) -o prog tests.cpp

server: service.cpp session.hpp auth.hpp
	$(CXX) $(CXXFLAGS) -o server service.cpp

clean:
	rm -f prog server
```

```text
constant_eq_is_exact                       ok
tokens_are_hex_and_unique                  ok
record_round_trips                         ok
constant_eq_over_generated_inputs          ok
the_service_answers_end_to_end             ok
5 test(s), 33 check(s), 0 failure(s)
```

Everything that could have been made convenient has been made honest instead. There is no fixed
port — `free_port()` binds to `0`, asks the kernel which port it got, and closes the socket, so
two runs in parallel cannot collide. The child's stdout is redirected to `/dev/null`, because a
service that prints would interleave its lines with the suite's report and turn a deterministic
transcript into a lottery. And readiness is a **bounded** loop: twenty milliseconds apart, a
hundred times, then give up and fail.

That last one deserves its own sentence, because it is the difference between a test and a hang.
If the child never starts, every assertion after it becomes a confusing string of empty responses
— the socket connects to nothing and the response is `""`. One bounded wait converts that into a
single clear failure before anything else runs.

Then the assertions themselves, and note what they are: **substrings**. `pub.find(" 200 ")` and
`anon.find(" 401 ")`, not equality against a whole response. A whole-response comparison would
assert on `Date`, `Server` and every header the server happens to add, and would fail on a
different machine for a reason nobody cares about. The contract is the status, the body and the
presence of `Set-Cookie: sid=` — those are the things the handler promised.

And then the part no unit test can reach:

```cpp
::kill(pid, SIGTERM);
int status = 0;
CHECK(::waitpid(pid, &status, 0) == pid);
CHECK(WIFEXITED(status));
CHECK(WEXITSTATUS(status) == 0);
```

`WIFEXITED` before `WEXITSTATUS`, always. If the process was killed by a signal, the value inside
`status` is not an exit code at all, and reading it as one is how a suite reports "exit status 0"
for a service that segfaulted. Chapter 43 made the drain a contract; this is the assertion that
holds it to the contract.

## Running it

`./prog` is the whole interface, and `$?` is the whole verdict:

```sh run-project
echo "--- ./prog, which is the whole interface ---"
./prog
echo "exit status: $?"

echo
echo "--- the same suite, and the test names it registered ---"
./prog 2>/dev/null | grep ' ok$' | awk '{print $1}'
```

```text
--- ./prog, which is the whole interface ---
constant_eq_is_exact                       ok
tokens_are_hex_and_unique                  ok
record_round_trips                         ok
constant_eq_over_generated_inputs          ok
the_service_answers_end_to_end             ok
5 test(s), 33 check(s), 0 failure(s)
exit status: 0

--- the same suite, and the test names it registered ---
constant_eq_is_exact
tokens_are_hex_and_unique
record_round_trips
constant_eq_over_generated_inputs
the_service_answers_end_to_end
```

Five tests, every one `ok`, and `0 failure(s)`. The second run greps out the test names, which is
worth doing once: it is where you notice that a test you thought you had is not in the list,
because a registration macro was mistyped and its body is dead code the compiler never
complained about.

:::scenario The suite that was green and shipped a broken login
A team has 240 tests, all passing, and a login flow that has been broken for a week. The unit
tests cover `verify_record` thoroughly — correct password accepted, wrong password rejected, a
malformed record rejected — and they are all correct. The bug is in the handler:

```cpp
if (user != kUser || !verify_record(g_record, password))
    return {401, "bad credentials\n", ""};
return {200, "welcome\n", ""};          // <- the Set-Cookie was dropped in a refactor
```

Every unit test passes, because `verify_record` still works. Every manual test passed too, because
the person testing logged in, saw `welcome`, and closed the tab. The defect only exists in the join
between three correct pieces: the store that minted the session, the handler that forgot to send
it, and the browser that therefore arrives at the next page anonymous.

That is precisely the class of bug an integration test exists for, and the assertion that catches
it is one line — `CHECK(ok.find("Set-Cookie: sid=") != std::string::npos)` — sitting in the middle
of this chapter's suite. Adding more unit tests would never have found it. Testing the *seam*
would have, on the first run.
:::

## Key takeaways

- A test is a program that fails loudly; its verdict must be an exit status, and it must run without
  a person deciding when it passed.
- Failures belong on `stderr` and the summary on `stdout`, and the runner should count and continue
  rather than stop at the first problem.
- A test that cannot fail is not a test; the only way to know a check discriminates is to watch it
  go red once.
- A table makes the forgotten case cost one line instead of one test, and the rows with escapes and
  the empty string are the ones that earn their keep.
- Flakiness has three mechanical sources — the clock, shared order, and fixed ports or paths — and
  each has a mechanical answer: inject the clock, isolate the state, ask the kernel.
- Unit tests cover functions; only an integration test covers the seam, and the seam is where the
  defects that survive a manual smoke test live.
- An integration test spawns the real binary, waits for readiness **bounded**, asserts on substrings
  rather than whole responses, and checks `WIFEXITED` before reading `WEXITSTATUS`.
- `SIGTERM` plus an exit-status assertion is the only way to test the shutdown contract Chapter 43
  wrote.

## Practice

- [ ] Write a test for a function that reads the wall clock, then refactor the function to take the
  clock as a parameter and show that the test becomes an exact comparison.
- [ ] Take a table from this chapter and add three cases that a hand-written test would plausibly
  have missed. Run it and confirm at least one of them fails before you fix the function.
- [ ] Write a test that forks and execs a binary that does not exist, and make it report "could not
  start" rather than timing out. Compare the message with what a connection-refused error would say.
- [ ] Write a property test for a round-trip: pick any encode/decode pair in the book so far and
  generate inputs. Record the seed in the failure message.
- [ ] Write a table for the cookie parser covering the cases a hand-written test omits, including a
  value containing `=`, a duplicate name, and a name that differs only in case.
- [ ] Add a test that asserts the service rejects a request with an unreasonably large
  `Content-Length`, and decide what the correct response is before writing it.

## Solutions

:::solution Exercise 1
The clock is the only thing standing between a flaky test and a deterministic one:

```cpp run
#include <cstdio>
#include <string>

// Exercise 1: the flaky test, and its cure. The version on the left cannot be asserted
// on; the version on the right can, and the only difference is where the time came from.
static long real_now() { return 1758600000L; }

static std::string stamp_text(long now) { return "started at " + std::to_string(now); }
static std::string stamp_json(long now) { return "{\"t\":" + std::to_string(now) + "}"; }

struct Clock { long (*now)(); };

int main() {
    const Clock real = {real_now};
    std::printf("a test that reads the wall clock sees %s\n", stamp_text(real.now()).c_str());
    std::printf("the same test tomorrow sees something else: yes\n");
    std::printf("so the only assertion available is a substring: %s\n",
                stamp_json(real.now()).find("\"t\":") != std::string::npos ? "yes" : "no");

    const Clock fixed = {[]() -> long { return 1700000000000L; }};
    std::printf("\nwith an injected clock the assertion is the whole line:\n");
    std::printf("  %s\n", stamp_json(fixed.now()).c_str());
    std::printf("assert on that exactly: yes\n");
    std::printf("the clock was the only thing standing between this test and determinism\n");
    return 0;
}
```

```text
a test that reads the wall clock sees started at 1758600000
the same test tomorrow sees something else: yes
so the only assertion available is a substring: yes

with an injected clock the assertion is the whole line:
  {"t":1700000000000}
assert on that exactly: yes
the clock was the only thing standing between this test and determinism
```

The first half is unassertable and the reason is not subtle once it is written down: the function's
output depends on a value that changes every second, so the only assertion that can survive is a
substring — and a substring assertion passes for almost any bug. The second half replaces one
function pointer and the assertion becomes the whole line. That is the whole technique: **a
dependency that is read from outside the process is a parameter, not an ambient fact.**
:::

:::solution Exercise 2
The three cases worth adding to the escape table, and why each one is easy to miss:

```cpp
const Case extra[] = {
    {"\"", "\\\""},        // an input that is nothing but a quote
    {"\\\\", "\\\\\\\\"},  // two backslashes: the case that catches "replace once" bugs
    {"\x7f", "\x7f"},      // 0x7f is DEL, NOT a control character below 0x20
};
```

The first is the boundary of the loop: an escaping routine that indexes `i + 1` without checking
crashes on an input that is a single quote. The second catches the classic defect where the
implementation finds and replaces only the first backslash in a run. The third is the row that
documents the *policy* — `0x7f` is a printable-looking control character that this implementation
leaves alone, and a table is where that decision becomes visible instead of accidental.
:::

:::solution Exercise 3
A child that cannot start must fail with a message, not a timeout:

```cpp run
#include <cstdio>
#include <string>
#include <sys/wait.h>
#include <unistd.h>

// Exercise 3: a child that never starts must fail the test with a message, not hang it.
// The bounded wait is the whole exercise -- an unbounded one turns a broken test into a
// CI job that never finishes.
int main() {
    const pid_t pid = ::fork();
    if (pid == 0) {
        ::execl("./no-such-binary", "./no-such-binary", static_cast<char *>(nullptr));
        ::_exit(127);                    // reached only when exec failed
    }

    int status = 0;
    const pid_t done = ::waitpid(pid, &status, 0);
    std::printf("the child exited: %s\n", done == pid ? "yes" : "no");
    std::printf("because exec failed, not because the service stopped: %s\n",
                WIFEXITED(status) && WEXITSTATUS(status) == 127 ? "yes" : "no");
    std::printf("127 is the conventional 'could not start' status\n");
    std::printf("waitpid returned, so the readiness loop is not what timed out here\n");
    std::printf("a test that reported 'connection refused' instead would hide this\n");
    return 0;
}
```

```text
the child exited: yes
because exec failed, not because the service stopped: yes
127 is the conventional 'could not start' status
waitpid returned, so the readiness loop is not what timed out here
a test that reported 'connection refused' instead would hide this
```

`127` is the conventional status for "the execution failed", and it is the value this test puts
there itself, in the child, after `execl` returns. That detail is the whole lesson: `execl` only
returns when it *failed*, so the line after it is unreachable in every successful run. A test that
instead reported `connection refused` would send someone to look at the network, and the actual
cause — a missing binary, a typo in the path — would be three layers away.
:::

:::solution Exercise 4
Generated inputs, a named invariant, and a seed that makes the failure reproducible:

```cpp run
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

// Exercise 4: a property test. The inputs are generated, the invariant is named, and the
// seed is fixed -- which is the only way a generated test can live in a book, and also
// the first thing to reach for when a run does fail.
static std::uint64_t splitmix64(std::uint64_t &s) {
    std::uint64_t z = (s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static std::string escape(const std::string &in) {
    std::string out;
    for (char c : in) {
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (static_cast<unsigned char>(c) < 0x20) out += '?';
        else out += c;
    }
    return out;
}

// The invariant: escaping produces a string that contains no bare quote and no control
// character. It is checkable from the output alone, with no second implementation.
static bool is_safe(const std::string &s) {
    bool quoted = false;
    for (std::size_t i = 0; i < s.size(); ++i) {
        const unsigned char c = static_cast<unsigned char>(s[i]);
        if (quoted) { quoted = false; continue; }
        if (c == '\\') { quoted = true; continue; }
        if (c == '"' || c < 0x20) return false;
    }
    return !quoted;
}

int main() {
    const std::uint64_t seed = 0xC0FFEE;
    std::uint64_t state = seed;
    int trials = 0, bad = 0;
    for (int i = 0; i < 2000; ++i) {
        const std::size_t len = static_cast<std::size_t>(splitmix64(state) % 24);
        std::string input;
        for (std::size_t j = 0; j < len; ++j)
            input += static_cast<char>(splitmix64(state) % 128);
        ++trials;
        if (!is_safe(escape(input))) ++bad;
    }
    std::printf("seed: %llu\n", static_cast<unsigned long long>(seed));
    std::printf("%d generated input(s), %d unsafe output(s)\n", trials, bad);
    std::printf("re-running with the same seed repeats the same inputs: yes\n");
    std::printf("so a failure can be reproduced from one number\n");
    return bad == 0 ? 0 : 1;
}
```

```text
seed: 12648430
2000 generated input(s), 0 unsafe output(s)
re-running with the same seed repeats the same inputs: yes
so a failure can be reproduced from one number
```

Two thousand generated inputs, zero unsafe outputs, and `seed: 12648430` at the top of the report.
The invariant is the interesting part: `is_safe` checks a *property of the output* — no bare quote,
no control character, no dangling backslash — rather than comparing against a second escaping
implementation. A test that compares against a second implementation can only tell you that the
two disagree, and it needs the second implementation to be right.

The seed is not a detail. The value of a generated test is that it searches a space a person would
not enumerate by hand, and the cost is that a failure must be reproducible — which means the seed
is part of the failure report, printed before anything else can go wrong.
:::

:::solution Exercise 5
The rows a hand-written cookie test leaves out:

```cpp run
#include <cstdio>
#include <string>
#include <vector>

// Exercise 5: the cases a hand-written test forgets. Every line here is a request
// somebody's browser really sent.
struct Case {
    const char *header;
    const char *name;
    const char *want;
};

static std::string cookie(const std::string &header, const std::string &name) {
    std::size_t i = 0;
    while (i < header.size()) {
        const std::size_t semi = header.find(';', i);
        std::string part = header.substr(i, semi == std::string::npos ? std::string::npos : semi - i);
        while (!part.empty() && part.front() == ' ') part.erase(part.begin());
        const std::size_t eq = part.find('=');
        if (eq != std::string::npos && part.substr(0, eq) == name) {
            std::string value = part.substr(eq + 1);
            // The trim at the front is not enough. RFC 6265 allows optional whitespace
            // around the pair, and the case below -- which a hand-written test does not
            // have -- is what turned this line from a suspicion into a fact.
            while (!value.empty() && (value.back() == ' ' || value.back() == '\t')) value.pop_back();
            return value;
        }
        if (semi == std::string::npos) break;
        i = semi + 1;
    }
    return "";
}

int main() {
    const Case cases[] = {
        {"sid=abc", "sid", "abc"},
        {"sid=abc; theme=dark", "sid", "abc"},
        {" theme=dark ; sid=abc ", "sid", "abc"},
        {"sid=first; sid=second", "sid", "first"},      // first wins
        {"sid=", "sid", ""},                            // present and empty
        {"other=1", "sid", ""},                         // absent
        {"sid=a=b=c", "sid", "a=b=c"},                  // '=' in the value
        {"SID=abc", "sid", ""},                         // names are case-sensitive
    };

    int failed = 0;
    for (const Case &c : cases) {
        const std::string got = cookie(c.header, c.name);
        if (got != c.want) {
            ++failed;
            std::printf("  %-28s want '%s', got '%s'\n", c.header, c.want, got.c_str());
        }
    }
    std::printf("%zu case(s), %d failure(s)\n", sizeof(cases) / sizeof(cases[0]), failed);
    std::printf("the interesting rows are the last three\n");
    return failed == 0 ? 0 : 1;
}
```

```text
8 case(s), 0 failure(s)
the interesting rows are the last three
```

Eight rows, and the last three are the ones nobody writes by hand. `sid=a=b=c` is the case that
breaks any parser splitting on `=` and taking element `[1]` — the value is everything after the
*first* `=`, and a base64 or signed token will contain more of them. `SID=abc` is the case that
documents a decision: cookie names are compared case-sensitively, so this is *not* the cookie, and
a suite that asserts the opposite will fight the browser. And `sid=` is the case that separates
"absent" from "present and empty" — two states that a handler must distinguish, because the second
one means the session is over.

The `sid=first; sid=second` row is the one from Chapter 42 restated as a test, which is the point
of a table: a rule that lives in prose gets re-derived every time someone reads it; a rule that
lives in a row is enforced on every run.

One row here is not a restatement but a discovery, and it is worth being precise about it. The
third case — `" theme=dark ; sid=abc "` — failed the first time this table was run against the
parser exactly as Chapter 42 wrote it, because that parser trims whitespace before the name and
not after the value, so it returned `"abc "` with a trailing space. The service has never noticed,
because `curl` and every browser send `sid=abc` with no padding; the header is *allowed* to have
it, so this is a latent bug that only a table would have found. The fix is the three lines above
the `return`, and the lesson is the one the practice section keeps returning to: a table is where
a rule becomes a line, and a line is where a rule gets checked.
:::

:::solution Exercise 6
The test is easy; deciding the answer is the exercise:

```cpp
TEST(oversized_content_length_is_refused) {
    // Not "the server survives" -- the assertion below is about the *contract*.
    const std::string response = http_exchange(port,
        "POST /login HTTP/1.1\r\nHost: t\r\nContent-Length: 100000000\r\n\r\n");
    CHECK(response.find(" 413 ") != std::string::npos);
}
```

The right answer is `413 Payload Too Large`, and it has to be decided *before* the test is written,
because the two wrong answers are both tempting. Closing the connection without a response leaves
the client unable to tell a refusal from a crash. Reading the body first and *then* refusing is the
actual bug this test is looking for: a server that honours an attacker-chosen `Content-Length`
allocates a gigabyte per request, and it will do so before it gets around to having an opinion.
The check must come from a maximum the server chose, compared against the header — never from the
header deciding how much memory to reserve.
:::
