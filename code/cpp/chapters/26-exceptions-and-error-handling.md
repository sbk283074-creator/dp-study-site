---
chapter: 26
part: 4
title: Exceptions and Error Handling
summary: Let a failure travel to the one place that can handle it, keep the destructors running on the way out, and know when an error code is the better answer.
minutes: 60
tags: [exceptions, try-catch, raii, exception-safety, noexcept, terminate, custom-exception, error-codes]
---

Chapter 17's `handle` owned three resources and had five ways out of it. Chapter 20's RAII made the
cleanup automatic on every one of them, which solved half the problem. The other half is that in C, a
failure discovered six calls deep has to be *returned* six calls up: every intermediate function has to
check the error code, and every one of them can forget. Exceptions are how C++ lets a failure travel
straight to the one frame that knows what to do with it, unwinding the stack on the way and running the
destructors of everything it passes. That combination — a failure that skips the frames that cannot help,
and cleanup that happens anyway — is why modern C++ code contains so little error-handling boilerplate.

## throw, try, catch

`throw` starts a failure; `try` marks the code that might produce one; `catch` receives it:

```cpp run
#include <cstdio>
#include <stdexcept>
#include <string>

static int parse_port(const std::string &s) {
    if (s.empty()) throw std::invalid_argument("empty port");
    int port = 0;
    for (char c : s) {
        if (c < '0' || c > '9') throw std::invalid_argument("port is not numeric: " + s);
        port = port * 10 + (c - '0');
    }
    if (port < 1 || port > 65535) throw std::out_of_range("port out of range: " + s);
    return port;
}

int main() {
    const char *inputs[] = {"8080", "abc", "", "70000"};
    for (const char *in : inputs) {
        try {
            std::printf("parse(%s) = %d\n", in, parse_port(in));
        } catch (const std::exception &e) {
            std::printf("parse(%s) failed: %s\n", in, e.what());
        }
    }
    return 0;
}
```

```text
parse(8080) = 8080
parse(abc) failed: port is not numeric: abc
parse() failed: empty port
parse(70000) failed: port out of range: 70000
```

Three failure modes, one `catch`, and the loop continues after each one. `parse_port` has one `return`
and three `throw`s, and the caller has one handler rather than three checks. Compare that to the C
version, where the function would return a code and every caller would need an `if` — and where the
*fourth* caller someone adds next month would probably forget.

Two mechanics are worth naming. `throw` takes a value and copies it into a runtime-managed region, which
is why the exception survives the stack frames being destroyed. And the `catch` clause's type is matched
against that value, so `catch (const std::exception &e)` catches anything derived from `std::exception`.

## The destructor runs on the way out

This is the part that makes exceptions usable rather than merely convenient. When an exception unwinds
the stack, every fully-constructed object in the frames being left is destroyed:

```cpp run
#include <cstdio>
#include <stdexcept>

class Guard {
public:
    explicit Guard(const char *name) : name_(name) { std::printf("acquire %s\n", name_); }
    ~Guard() { std::printf("release %s\n", name_); }

private:
    const char *name_;
};

static void work(int n) {
    Guard g("lock");
    std::printf("working\n");
    if (n < 0) throw std::runtime_error("bad input");
    std::printf("finished\n");
}

int main() {
    try {
        work(1);
        work(-1);
    } catch (const std::exception &e) {
        std::printf("caught: %s\n", e.what());
    }
    std::printf("after the try block\n");
    return 0;
}
```

```text
acquire lock
working
finished
release lock
acquire lock
working
release lock
caught: bad input
after the try block
```

Read the last four lines. The second call to `work` printed `working`, threw, and `release lock` appeared
**before** `caught:` — the guard's destructor ran while the stack was unwinding, before the handler
received the exception. There is no `catch` inside `work` and no cleanup code anywhere. `Guard` does not
know exceptions exist; it only knows that its destructor releases the lock.

That is the whole argument for RAII in one transcript. **If your cleanup lives in a destructor, it
happens on the exception path for free.** If it lives in a `goto cleanup` block or at the end of the
function body, it does not — and the exception path is exactly the path that gets tested least. This is
also why `std::unique_ptr`, `std::vector` and `std::string` are safe to use in code that throws: they
release on unwinding because their destructors do.

## The exception hierarchy

`<stdexcept>` gives you a small set of standard types, all derived from `std::exception`:

| Type | Meaning | Typical cause |
|---|---|---|
| `std::logic_error` | a bug in the program | the caller passed something impossible |
| `std::invalid_argument` | bad argument | unparseable input |
| `std::out_of_range` | value outside the valid range | a port above 65535 |
| `std::length_error` | exceeds a maximum size | a string longer than allowed |
| `std::runtime_error` | something failed at run time | a failed operation |
| `std::bad_alloc` | allocation failed | `new` or a container ran out of memory |

`std::exception::what()` returns a `const char *` description, and it is what you print. The type matters
as much as the message, though, because `catch` matches on type: `catch (const std::out_of_range &)` lets
you handle a range problem differently from an unparseable argument. Catch by **`const &`** — the reason
is the pitfall below.

## Custom exception types

When the standard types do not carry enough information, derive your own:

```cpp run
#include <cstdio>
#include <exception>
#include <string>
#include <utility>

class ConfigError : public std::exception {
public:
    ConfigError(std::string key, std::string what)
        : key_(std::move(key)), what_(std::move(what)) {}

    const char *what() const noexcept override { return what_.c_str(); }
    const std::string &key() const { return key_; }

private:
    std::string key_;
    std::string what_;
};

static int require_port(const std::string &value, const std::string &key) {
    if (value.empty()) throw ConfigError(key, "value is missing");
    int port = 0;
    for (char c : value) {
        if (c < '0' || c > '9') throw ConfigError(key, "value is not numeric");
        port = port * 10 + (c - '0');
    }
    return port;
}

int main() {
    try {
        std::printf("port = %d\n", require_port("8080", "server.port"));
    } catch (const ConfigError &e) {
        std::printf("config error on %s: %s\n", e.key().c_str(), e.what());
    }

    try {
        std::printf("port = %d\n", require_port("", "server.port"));
    } catch (const ConfigError &e) {
        std::printf("config error on %s: %s\n", e.key().c_str(), e.what());
    }
    return 0;
}
```

```text
port = 8080
config error on server.port: value is missing
```

Three requirements for a well-behaved exception type. It derives from `std::exception` (so a generic
handler can still catch it), it overrides `what()`, and — the one that is easy to miss — it marks
`what()` as **`noexcept`**. `what()` is called *during* exception handling, so if it could throw you
would have an exception while handling an exception, which is `std::terminate`. Overriding `what()`
without `noexcept` does not compile, which is the compiler saving you from that.

`ConfigError` carries a `key` as well as a message, which is the reason to write a custom type at all:
the handler can report *which* setting was wrong, and the `catch` can distinguish this failure from
every other `std::runtime_error` in the program.

## noexcept, and why a destructor must not throw

A function marked `noexcept` promises not to let an exception escape. If one does, the program does not
catch it — it calls `std::terminate` immediately, with no unwinding and no handler:

```cpp run-abort
#include <cstdio>
#include <stdexcept>

class Bad {
public:
    ~Bad() noexcept(false) {
        std::printf("~Bad is about to throw\n");
        throw std::runtime_error("from destructor");
    }
};

int main() {
    try {
        Bad b;
        throw std::runtime_error("from the body");
    } catch (const std::exception &e) {
        std::printf("caught: %s\n", e.what());
    }
    std::printf("done\n");
    return 0;
}
```

```text
terminating due to uncaught exception
```

The program prints `~Bad is about to throw` and then dies — the `catch` never runs, `done` is never
printed, and the process exits with a signal. There are already two exceptions in flight (one from the
body, one from the destructor) and C++ has no way to report the second, so it gives up.

Destructors are **implicitly `noexcept`**, which is why the example had to write `noexcept(false)` to
demonstrate the failure — and why in normal code you cannot even write this bug by accident. The rule
follows: **a destructor must not throw.** If cleanup can fail, catch it inside the destructor, log it,
and let the destructor finish. A destructor that swallows an error is a design smell worth investigating,
but it is vastly better than a destructor that terminates the process.

This is also where `noexcept` earns its keep elsewhere. Chapter 21 marked the move constructor `noexcept`
because `std::vector` reallocates by moving, and it will only move if it is guaranteed the move cannot
throw — a throw mid-reallocation would leave the container unrecoverable. `noexcept` is not decoration;
it is information the library uses to choose between a fast path and a safe one.

## Error codes are sometimes the right answer

Exceptions are for failures the immediate caller cannot fix. For failures that are a *normal part of the
function's contract*, an error code or an `std::optional` is better:

```cpp run
#include <cstdio>
#include <string>

enum class ParseResult { ok, empty, not_numeric, out_of_range };

static ParseResult parse_port(const std::string &s, int &out) {
    if (s.empty()) return ParseResult::empty;
    int port = 0;
    for (char c : s) {
        if (c < '0' || c > '9') return ParseResult::not_numeric;
        port = port * 10 + (c - '0');
    }
    if (port < 1 || port > 65535) return ParseResult::out_of_range;
    out = port;
    return ParseResult::ok;
}

static const char *describe(ParseResult r) {
    switch (r) {
        case ParseResult::ok:           return "ok";
        case ParseResult::empty:        return "empty";
        case ParseResult::not_numeric:  return "not numeric";
        case ParseResult::out_of_range: return "out of range";
    }
    return "unknown";
}

int main() {
    const char *inputs[] = {"8080", "abc", ""};
    for (const char *in : inputs) {
        int port = 0;
        ParseResult r = parse_port(in, port);
        if (r == ParseResult::ok) std::printf("parse(%s) = %d\n", in, port);
        else std::printf("parse(%s) failed: %s\n", in, describe(r));
    }
    return 0;
}
```

```text
parse(8080) = 8080
parse(abc) failed: not numeric
parse() failed: empty
```

The same parse, with the same four outcomes, expressed as a return value. The trade is explicit:

| | Exceptions | Error codes |
|---|---|---|
| Caller that ignores it | cannot — it must `catch` or propagate | gets a default value and no warning |
| Cost when nothing fails | effectively zero on the happy path | a branch per call |
| Cost of forgetting to check | none | a bug |
| Can be caught far from the failure | yes | only by every intermediate frame |
| Type information | the exception's type and fields | whatever the enum carries |

The rule of thumb that follows: **use exceptions for failures the caller cannot be expected to handle
locally** — a missing config file, a failed allocation, a violated invariant — and error codes or
`std::optional` for outcomes that are part of the function's normal contract, like "this string is not a
number". A parser that returns "not a number" for "not a number" is not failing; it is answering.

:::scenario The handler that had to clean up on five paths

Chapter 17's `handle` had three resources and five exits, and the only reason it was correct was that
every exit went through one cleanup block. That discipline does not survive contact with a growing
function — a `throw` from anywhere inside it, or a new early `return` added by someone in a hurry, and
the cleanup is skipped. The version that survives puts the cleanup in a destructor and lets the failure
travel:

```cpp run-san
#include <cstdio>
#include <stdexcept>
#include <string>
#include <utility>

class Connection {
public:
    explicit Connection(int fd) : fd_(fd) { std::printf("open  %d\n", fd_); }
    ~Connection() { std::printf("close %d\n", fd_); }
    int fd() const { return fd_; }

private:
    int fd_;
};

class Request {
public:
    explicit Request(std::string body) : body_(std::move(body)) {}
    const std::string &body() const { return body_; }

private:
    std::string body_;
};

static Request parse(const std::string &raw) {
    if (raw.size() > 12) {
        throw std::length_error("request too long: " + std::to_string(raw.size()));
    }
    return Request(raw);
}

static void handle(const std::string &raw) {
    Connection c(7);
    Request r = parse(raw);
    std::printf("handled %s\n", r.body().c_str());
}

int main() {
    try {
        handle("GET /");
    } catch (const std::exception &e) {
        std::printf("error: %s\n", e.what());
    }
    try {
        handle("GET /a-very-long-path");
    } catch (const std::exception &e) {
        std::printf("error: %s\n", e.what());
    }
    std::printf("server still running\n");
    return 0;
}
```

```text
open  7
handled GET /
close 7
open  7
close 7
error: request too long: 21
server still running
```

Look at what `handle` does not contain: no `try`, no `catch`, no `return false`, no cleanup. It opens a
connection, parses, prints, and returns. On the second call the parse threw, and `close 7` still appeared
— before the `error:` line, because the connection's destructor ran during unwinding.

Now count the exit paths. There are two today and there will be more tomorrow, and **none of them needs
any code**. The `throw` in `parse` does not know it is unwinding through `handle`; `Connection` does not
know exceptions exist. That separation is the point: the function that detects the problem reports it,
the type that owns the resource releases it, and the frame that can decide what to do — `main` here —
catches it. The `server still running` line is the proof that a failed request did not take the server
down, which is what the error-code version had to achieve by checking and forwarding at every level.

:::

:::pitfall Catching by value slices the exception

`catch (std::exception e)` looks harmless and compiles. It is the Chapter 23 slicing problem applied to
exceptions, and the symptom is that your message disappears:

```cpp run
#include <cstdio>
#include <exception>
#include <string>
#include <utility>

class ConfigError : public std::exception {
public:
    explicit ConfigError(std::string what) : what_(std::move(what)) {}
    const char *what() const noexcept override { return what_.c_str(); }

private:
    std::string what_;
};

int main() {
    try {
        throw ConfigError("missing key: port");
    } catch (std::exception e) {
        std::printf("by value: %s\n", e.what());
    }

    try {
        throw ConfigError("missing key: port");
    } catch (const std::exception &e) {
        std::printf("by ref:   %s\n", e.what());
    }
    return 0;
}
```

```text
by value: std::exception
by ref:   missing key: port
```

The `catch` parameter is an object, so catching by value **copy-constructs a `std::exception`** from the
`ConfigError` that was thrown — slicing off the derived part, including the `what_` string, and leaving
the base's generic message. The fix is one character: catch by `const &`.

Always write `catch (const std::exception &e)`. The reference binds to the thrown object without copying,
so the derived type survives, `what()` dispatches to the override, and any custom fields like
`ConfigError::key()` are still reachable. Catching by value also copies the exception object a second
time, which is a real cost in a handler that may run often.

:::

:::warning catch (...) swallows your bug reports

`catch (...)` catches everything, including the exceptions you did not think about, and it gives you no
way to find out what happened — you cannot name the object or call `what()` on it. It has exactly two
legitimate uses: a destructor that must not let anything escape, and the outermost boundary of a thread
or an event loop, where the alternative is terminating the process. Anywhere else it converts a crash you
would have debugged in five minutes into silence you will debug for a week.

If you must catch everything, at least make it visible:

```cpp
try {
    do_the_work();
} catch (const std::exception &e) {
    log_error(e.what());          // the case you can describe
    throw;                        // re-throw: do not pretend it was handled
} catch (...) {
    log_error("unknown exception");
    throw;
}
```

A bare `throw;` with no argument re-throws the exception currently being handled, preserving its type.
That is how a frame adds context and passes the problem on instead of absorbing it.

:::

## Key takeaways

- `throw` starts a failure, `try` marks the code that might produce one, and `catch` matches on the
  thrown object's **type** — so the type carries meaning beyond the message.
- When an exception unwinds the stack, every fully-constructed object in the frames being left is
  destroyed, which is why cleanup in a destructor happens on the exception path automatically.
- Catch by `const &`; catching by value slices the exception and loses `what()` and any custom fields.
- `std::exception::what()` returns the description; the standard hierarchy is `logic_error` /
  `invalid_argument` / `out_of_range` / `length_error` / `runtime_error` / `bad_alloc`.
- A custom exception should derive from `std::exception` and override `what()` as `noexcept` — the
  compiler requires the `noexcept`, because `what()` runs while an exception is already being handled.
- Destructors are implicitly `noexcept` and **must not throw**; a throw during unwinding calls
  `std::terminate` immediately, with no handler and no further cleanup.
- `noexcept` on a move constructor is not decoration: `std::vector` will only move elements on
  reallocation if the move is guaranteed not to throw.
- Use error codes or `std::optional` for outcomes that are part of a function's normal contract ("this
  string is not a number") and exceptions for failures the local caller cannot fix.

## Practice

- [ ] Write a `parse_port` that throws `std::invalid_argument` for a non-numeric string and
  `std::out_of_range` above 65535, and a caller that catches `const std::exception &` and prints
  `what()`.
- [ ] Write a `ConfigError` deriving from `std::exception` that carries both a message and a key, and
  catch it to report which key was wrong.
- [ ] Show that `catch (std::exception e)` prints the base message while `catch (const std::exception &e)`
  prints yours, and explain the difference in one sentence.
- [ ] Write a class that prints on construction and destruction, throw from inside a function that has
  one, and show that the destructor runs before the handler receives the exception.
- [ ] Write a destructor that throws during unwinding, and show what the runtime does instead of running
  your handler.
- [ ] Express the same parse as an `enum class` return value with an out-parameter, and say in one
  sentence which of the two designs you would ship for a config file and why.

## Solutions

:::solution Exercise 1

```cpp run
#include <cstdio>
#include <stdexcept>
#include <string>

static int parse_port(const std::string &s) {
    if (s.empty()) throw std::invalid_argument("empty port");
    int port = 0;
    for (char c : s) {
        if (c < '0' || c > '9') throw std::invalid_argument("port is not numeric: " + s);
        port = port * 10 + (c - '0');
    }
    if (port < 1 || port > 65535) throw std::out_of_range("port out of range: " + s);
    return port;
}

int main() {
    const char *inputs[] = {"8080", "abc", "", "70000"};
    for (const char *in : inputs) {
        try {
            std::printf("parse(%s) = %d\n", in, parse_port(in));
        } catch (const std::exception &e) {
            std::printf("parse(%s) failed: %s\n", in, e.what());
        }
    }
    return 0;
}
```

```text
parse(8080) = 8080
parse(abc) failed: port is not numeric: abc
parse() failed: empty port
parse(70000) failed: port out of range: 70000
```

Four inputs, three failures, and the loop keeps going after each one — the handler is inside the loop,
so a failed parse does not end the program. The single `catch (const std::exception &)` covers both the
`invalid_argument` and the `out_of_range` because both derive from `std::exception`. If the two needed
different treatment, a `catch (const std::out_of_range &)` clause placed **before** the general one would
receive the range failures, because `catch` clauses are tried in order and the first match wins.

:::

:::solution Exercise 2

```cpp run
#include <cstdio>
#include <exception>
#include <string>
#include <utility>

class ConfigError : public std::exception {
public:
    ConfigError(std::string key, std::string what)
        : key_(std::move(key)), what_(std::move(what)) {}

    const char *what() const noexcept override { return what_.c_str(); }
    const std::string &key() const { return key_; }

private:
    std::string key_;
    std::string what_;
};

static int require_port(const std::string &value, const std::string &key) {
    if (value.empty()) throw ConfigError(key, "value is missing");
    int port = 0;
    for (char c : value) {
        if (c < '0' || c > '9') throw ConfigError(key, "value is not numeric");
        port = port * 10 + (c - '0');
    }
    return port;
}

int main() {
    try {
        std::printf("port = %d\n", require_port("8080", "server.port"));
    } catch (const ConfigError &e) {
        std::printf("config error on %s: %s\n", e.key().c_str(), e.what());
    }

    try {
        std::printf("port = %d\n", require_port("", "server.port"));
    } catch (const ConfigError &e) {
        std::printf("config error on %s: %s\n", e.key().c_str(), e.what());
    }
    return 0;
}
```

```text
port = 8080
config error on server.port: value is missing
```

`what()` is marked `noexcept` because the compiler requires it — it is an override of
`std::exception::what()`, which is `noexcept`, and a looser override would not compile. The `key_` member
is what makes the custom type worth writing: the handler prints `server.port`, which is the name the user
of the program can act on. `key()` returns `const std::string &` rather than a copy, and the handler uses
`c_str()` because `%s` needs a `const char *`.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>
#include <exception>
#include <string>
#include <utility>

class ConfigError : public std::exception {
public:
    explicit ConfigError(std::string what) : what_(std::move(what)) {}
    const char *what() const noexcept override { return what_.c_str(); }

private:
    std::string what_;
};

int main() {
    try {
        throw ConfigError("missing key: port");
    } catch (std::exception e) {
        std::printf("by value: %s\n", e.what());
    }

    try {
        throw ConfigError("missing key: port");
    } catch (const std::exception &e) {
        std::printf("by ref:   %s\n", e.what());
    }
    return 0;
}
```

```text
by value: std::exception
by ref:   missing key: port
```

The `catch` parameter is an object, so `catch (std::exception e)` **copy-constructs a `std::exception`**
from the thrown `ConfigError`. That copy is a plain base object — the derived part, including the
`what_` string, is sliced away — so `what()` returns the base's generic text. Catching by `const &` binds
a reference to the exception that was actually thrown, so the dynamic type survives and `what()`
dispatches to the override. It is the Chapter 23 rule applied to handlers: **a polymorphic type is never
caught by value.**

:::

:::solution Exercise 4

```cpp run
#include <cstdio>
#include <stdexcept>

class Guard {
public:
    explicit Guard(const char *name) : name_(name) { std::printf("acquire %s\n", name_); }
    ~Guard() { std::printf("release %s\n", name_); }

private:
    const char *name_;
};

static void work(int n) {
    Guard g("lock");
    std::printf("working\n");
    if (n < 0) throw std::runtime_error("bad input");
    std::printf("finished\n");
}

int main() {
    try {
        work(1);
        work(-1);
    } catch (const std::exception &e) {
        std::printf("caught: %s\n", e.what());
    }
    std::printf("after the try block\n");
    return 0;
}
```

```text
acquire lock
working
finished
release lock
acquire lock
working
release lock
caught: bad input
after the try block
```

The second `work` call printed `working`, threw, and `release lock` came **before** `caught:` — the guard
was destroyed while the stack unwound, before the handler ran. `work` contains no `try` and no cleanup
code, and `Guard` contains no reference to exceptions at all. This is the property that makes RAII the
right place for cleanup: the destructor runs on the return path and on the exception path, and you wrote
it once.

:::

:::solution Exercise 5

```cpp run-abort
#include <cstdio>
#include <stdexcept>

class Bad {
public:
    ~Bad() noexcept(false) {
        std::printf("~Bad is about to throw\n");
        throw std::runtime_error("from destructor");
    }
};

int main() {
    try {
        Bad b;
        throw std::runtime_error("from the body");
    } catch (const std::exception &e) {
        std::printf("caught: %s\n", e.what());
    }
    std::printf("done\n");
    return 0;
}
```

```text
terminating due to uncaught exception
```

The program printed `~Bad is about to throw` and then died: the `catch` never ran, `done` was never
printed, and the process exited on a signal rather than with a status. The reason is that two exceptions
are in flight at once — the one from the body, which is unwinding the stack, and the one from the
destructor — and C++ has no mechanism for reporting the second. `std::terminate` is called directly, with
no further unwinding, so the handler that was waiting for the first exception never gets control.

`noexcept(false)` was needed to write the example at all, because destructors are implicitly `noexcept`
and a throwing destructor inside a `noexcept` function would terminate even sooner. That implicitness is
the language protecting you: in normal code this bug cannot be typed by accident. The rule to carry away
is that **cleanup that can fail must handle its own failure inside the destructor** — log it, swallow it,
but let the destructor finish.

:::

:::solution Exercise 6

```cpp run
#include <cstdio>
#include <string>

enum class ParseResult { ok, empty, not_numeric, out_of_range };

static ParseResult parse_port(const std::string &s, int &out) {
    if (s.empty()) return ParseResult::empty;
    int port = 0;
    for (char c : s) {
        if (c < '0' || c > '9') return ParseResult::not_numeric;
        port = port * 10 + (c - '0');
    }
    if (port < 1 || port > 65535) return ParseResult::out_of_range;
    out = port;
    return ParseResult::ok;
}

static const char *describe(ParseResult r) {
    switch (r) {
        case ParseResult::ok:           return "ok";
        case ParseResult::empty:        return "empty";
        case ParseResult::not_numeric:  return "not numeric";
        case ParseResult::out_of_range: return "out of range";
    }
    return "unknown";
}

int main() {
    const char *inputs[] = {"8080", "abc", ""};
    for (const char *in : inputs) {
        int port = 0;
        ParseResult r = parse_port(in, port);
        if (r == ParseResult::ok) std::printf("parse(%s) = %d\n", in, port);
        else std::printf("parse(%s) failed: %s\n", in, describe(r));
    }
    return 0;
}
```

```text
parse(8080) = 8080
parse(abc) failed: not numeric
parse() failed: empty
```

The same four outcomes as the throwing version, expressed as a value. `enum class` is used rather than a
plain `enum` so the enumerators cannot be compared against integers by accident, and the `switch` in
`describe` is exhaustive, which is what `-Wswitch` (part of `-Wall`) enforces — add a fifth enumerator and
the compiler points at this function rather than letting it fall through to `"unknown"`.

For a **config file**, this is the design to ship. A malformed value in a config file is an expected
outcome, not an exception: the caller is going to report it to the user and exit, so there is nothing to
unwind past and no benefit to the exception machinery. Exceptions earn their place when the failure is
discovered deep inside a call chain whose intermediate frames cannot help — which is precisely the
`handle` scenario earlier in this chapter, where the parse happens six calls below the frame that knows
how to respond. The distinguishing question is not "how bad is this?" but **"can the immediate caller do
anything useful with it?"**

:::
