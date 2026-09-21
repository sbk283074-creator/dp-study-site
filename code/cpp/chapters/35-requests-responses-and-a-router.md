---
chapter: 35
part: 5
title: Requests, responses and a router
summary: Turn a raw request into a Request you can read fields off, answer with a Response that knows how to put itself on the wire, and match paths with a router that tells 404 apart from 405.
minutes: 70
tags: [http, router, enum-class, headers, string-view, functional, project, 404, 405]
---

Chapter 34's server reads one line and compares it:

```cpp
const std::string line = raw.substr(0, raw.find("\r\n"));
std::istringstream in(line);
std::string method, target, version;
if (!(in >> method >> target >> version)) return error_response("400 Bad Request", ...);
if (method != "GET" && method != "HEAD") return error_response("405 Method Not Allowed", ...);
```

That is honest code for a server with exactly one route shape. It stops being honest the moment there
is a second one. `/health` and `/items` and `/items/:id` are three different answers to the same
question — "which handler?" — and a `target` you only ever `substr` cannot express "and the id was
42". It also cannot tell a caller who used the wrong method from a caller who asked for something that
does not exist, which is the difference between `405` and `404` and the difference between a client
retrying forever and a client giving up.

This chapter builds the two types the rest of the part is written against — `Request` and `Response` —
and the `Router` that chooses between them. The socket layer from Chapter 34 is unchanged. What
changes is everything between accepting a connection and writing the response back.

## Headers are case-insensitive, and `std::map` is not

The request parser has to look headers up by name, and the first thing to know about HTTP header names
is that `Content-Length`, `content-length` and `CONTENT-LENGTH` are the same header. A `std::map`
disagrees:

```cpp run
#include <cctype>
#include <cstdio>
#include <map>
#include <optional>
#include <string>

static std::string lower(std::string s) {
    for (char &c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

int main() {
    /* The obvious version: a map keyed by the name exactly as it arrived. */
    std::map<std::string, std::string> naive;
    naive["Content-Length"] = "42";
    const auto found = naive.find("content-length");
    std::printf("raw map, lowercased lookup:  %s\n",
                found == naive.end() ? "(not found)" : found->second.c_str());

    /* The version HTTP needs: keys are normalised on the way in. */
    std::map<std::string, std::string> normalised;
    normalised[lower("Content-Length")] = "42";

    for (const char *name : {"content-length", "CONTENT-LENGTH", "Content-Length"}) {
        const auto it = normalised.find(lower(name));
        std::printf("normalised, lookup %-16s -> %s\n", name,
                    it == normalised.end() ? "(not found)" : it->second.c_str());
    }
    return 0;
}
```

```text
raw map, lowercased lookup:  (not found)
normalised, lookup content-length   -> 42
normalised, lookup CONTENT-LENGTH   -> 42
normalised, lookup Content-Length   -> 42
```

The fix is not to remember to write the right case at every call site — that is the same class of
problem as the `close(conn)` Chapter 34 opened with. The fix is to make the wrong case *impossible* by
normalising the key once, on the way in, in a `set` that every write goes through:

```cpp
void Headers::set(std::string name, std::string value) {
    data_[lower(std::move(name))] = std::move(value);
}

std::optional<std::string> Headers::get(const std::string &name) const {
    const auto it = data_.find(lower(name));
    if (it == data_.end()) return std::nullopt;
    return it->second;
}
```

`get` returns `std::optional<std::string>`, not `std::string` with an empty string for "absent". A
header can legitimately be empty, so an empty return would be ambiguous; `nullopt` is not. That is the
distinction Chapter 29 drew, and here it decides whether `if (headers.get("content-length"))` means
what you think.

The `lower` helper takes its argument **by value** and mutates it. That is deliberate: the caller
passes either a `std::string` it does not need any more (moved in) or a `const std::string &` that must
not be touched, and by-value handles both without a second overload.

:::note The headers go out lowercase

Because the keys are normalised on the way in, they come back out lowercase — the wire shows
`content-type: text/plain`, not `Content-Type: text/plain`. Both are correct: RFC 7230 says header
field names are case-insensitive, so a client must accept either. Lowercase is the convention HTTP/2
made mandatory, and sending it in HTTP/1.1 means the two protocols' wire formats agree. If you are
looking at a transcript and wondering why the case changed, this is why.

:::

## Status codes that cannot be mixed up

A status code is a number on the wire and a small set of named things in your program. Writing it as a
bare `int` means `respond(404)` and `respond(Status::Ok)` and `respond(3)` all compile, and only one of
them is what you meant. `enum class` is the fix, and the first thing it does is refuse the conversion:

```cpp bad
enum class Status { Ok = 200, NotFound = 404 };

int main() {
    int code = Status::Ok;
    return code;
}
```

```text
error: cannot initialize a variable of type 'int' with an rvalue of type 'Status'
```

Two things to notice. The names are *scoped* — you write `Status::Ok`, never a bare `Ok`, so adding a
second enum with an `Ok` in it cannot collide. And there is no implicit conversion in either direction,
so the only way to get the number 200 out is to ask for it:

```cpp
std::string status_line(Status s) {
    return "HTTP/1.1 " + std::to_string(static_cast<int>(s)) + " " + reason(s);
}
```

The `static_cast<int>(s)` is the single place where the enum becomes a number. Everywhere else in the
program a status is a `Status`, which means a function that takes a status cannot be handed a port
number, a file descriptor or an index.

The reason phrase needs a `switch`, and that is where the compiler turns out to be more useful than
you might expect:

```cpp warn
#include <cstdio>

enum class Status { Ok = 200, Created = 201, NotFound = 404 };

static const char *reason(Status s) {
    switch (s) {
        case Status::Ok:       return "OK";
        case Status::NotFound: return "Not Found";
    }
    return "?";
}

int main() {
    std::printf("%s\n", reason(Status::Created));
    return 0;
}
```

```text
warning: enumeration value 'Created' not handled in switch
```

`-Wswitch` fires on a `switch` over an enum whenever a value is missing, and it is enabled by `-Wall`.
So the moment someone adds `Status::Created` to the enum, every `switch` that has not been updated
starts warning — which is exactly the reminder you want, at compile time, in the right place. This is
the payoff for `enum class` over `int` constants: **the compiler knows the complete set of values and
will tell you when your code does not.** The project compiles with `-Werror`, so a missing case is not
a warning there; it is a build failure.

The `return "?";` after the switch is what satisfies the compiler that the function always returns a
value. Once every case is handled it is unreachable, and it is the only line in the function that is
allowed to be wrong without a diagnostic — so when you add a status, fix the `switch`, not the
fallback.

## Parsing a request

`Request::parse` is the bridge between the bytes and the structure, and it has one job: turn a string
into a `Request`, or say it cannot.

```cpp
static std::optional<Request> parse(const std::string &raw);
```

`std::optional<Request>` rather than a thrown exception, and the choice is the one Chapter 30 drew: a
malformed request is an *expected* outcome that the caller has a specific answer for (`400 Bad
Request`), so it belongs in the return type. A missing configuration file at startup is the opposite —
there is no reasonable way to continue — and that is what exceptions are for.

The parser works in four passes over the same string:

1. **The request line.** `METHOD SP TARGET SP VERSION`, split on the first two spaces. The version is
   checked against `HTTP/1.1` and `HTTP/1.0` because anything else means the client is speaking
   something this server does not implement, and guessing is worse than refusing.
2. **The target.** Split at `?` into `path` and `query`. The path is what the router matches; the query
   is data for the handler.
3. **The headers.** One per line until the blank line, each split at its first `:` and trimmed.
4. **The body.** Exactly as many bytes as `Content-Length` promised — and if fewer are available, the
   request is not complete and `parse` says so.

The target is percent-decoded **once, here**, and a bad escape fails the whole request. That ordering
matters more than it looks: Chapter 34's lesson was that a security check must run on the value you
actually use, and the same applies to validation. If `parse` guarantees the target is well-formed, then
the router can decode path parameters without re-checking, and there is one place to audit instead of
two.

## A response that knows how to put itself on the wire

`Response` is three fields and one method:

```cpp
struct Response {
    Status status = Status::Ok;
    Headers headers;
    std::string body;

    std::string to_string() const;
};
```

`to_string` is where the defaults live, and defaults are what make a handler short:

```cpp
std::string Response::to_string() const {
    Headers out = headers;
    if (!out.get("content-length")) out.set("Content-Length", std::to_string(body.size()));
    if (!out.get("connection")) out.set("Connection", "close");
    return status_line(status) + "\r\n" + out.to_string() + "\r\n" + body;
}
```

Note the `Headers out = headers;` — a copy, so a `const` method can fill in what the handler left out
without mutating the response the caller still holds. Chapter 25's copy semantics, used for exactly
what they are for.

`Content-Length` comes from `body.size()`, never from a parameter. That was Chapter 34's lesson and it
holds here for the same reason: one source of truth cannot disagree with itself. A handler that wants a
different `Content-Type` sets one; a handler that does not gets `text/plain` from the helper it called.

## Matching a path

A route is a method, a pattern, and something to run. The pattern is split into segments, and a segment
starting with `:` captures whatever is in that position:

```cpp
void Router::add(const std::string &method, const std::string &pattern, Handler handler);
```

A handler is a `std::function<Response(const Request &, const Params &)>`, which means all of these are
acceptable:

```cpp
router.add("GET", "/health", health_handler);                        // a function
router.add("GET", "/items",  [](const Request &, const Params &) {   // a lambda
    return text(Status::Ok, "[]\n");
});
router.add("GET", "/items/:id", [&repo](const Request &, const Params &p) {  // capturing a local
    return text(Status::Ok, repo.find(p.at("id")));
});
```

`std::function` is type erasure: it holds any callable with that signature and calls it through an
indirection. The cost is one virtual-ish call per request, which for a route table of a few dozen
entries is nothing next to reading a file or opening a socket. The alternative from Chapter 27 is an
abstract base class with a `virtual Response handle(...)`, and it is the better choice when handlers
are big, when you want to add data members, or when you want the compiler to check that you implemented
everything — an abstract class cannot be instantiated until it is complete, while a `std::function`
just has to be callable.

The `dispatch` that uses these routes is two passes, and the order of the passes is the whole point:

```cpp
Response Router::dispatch(const Request &req) const {
    const std::vector<std::string> path = split(req.path);

    /* First: does any route have this shape at all? */
    std::vector<const Route *> shape_matches;
    for (const Route &route : routes_) {
        Params ignored;
        if (match(route, path, &ignored)) shape_matches.push_back(&route);
    }

    if (shape_matches.empty()) {
        /* ... 404 ... */
    }

    /* Second: among those, is there one that accepts this method? */
    for (const Route *route : shape_matches) {
        if (route->method != req.method) continue;
        Params captured;
        match(*route, path, &captured);
        return route->handler(req, captured);
    }

    /* ... 405, with an Allow header ... */
}
```

Pass one asks only about *shape*. If nothing has that shape, the answer is `404 Not Found` and the
method never enters into it. Pass two asks about the method among the routes that did match. The
distinction is not pedantry: `404` means "there is nothing here", and a client that gets it stops.
`405` means "this exists, but not like that", and a client that gets it is being told its request was
understood. Answering `405` for a path that does not exist tells every client and every crawler that
something is there when it is not.

The `Allow` header on a `405` has to list the methods that *would* work, which means collecting them
from the routes that matched — and the project uses a `std::set<std::string>` to do it, because the
same method can appear more than once (two routes can share a path and differ only by method) and
because a set comes out sorted. `Allow: GET, POST` is a contract; `Allow: POST, GET, POST` is a
sentence a client has to parse around.

## Borrowing without copying

`std::string_view`, new in C++17, is a pointer and a length: a view of characters somebody else owns.
Passing one costs nothing, which makes it the right type for a parser that reads a big string and hands
back pieces of it:

```cpp run
#include <cstdio>
#include <cstdlib>
#include <string>
#include <string_view>

/* Split "Name: value" without copying either half. */
static void split_header(std::string_view line, std::string_view *name,
                         std::string_view *value) {
    const std::size_t colon = line.find(':');
    *name = line.substr(0, colon);
    std::size_t start = colon + 1;
    while (start < line.size() && line[start] == ' ') start++;
    *value = line.substr(start);
}

int main() {
    /* The string outlives every view taken from it. */
    const std::string header = "Content-Length: 4096";

    std::string_view name, value;
    split_header(header, &name, &value);

    std::printf("name  = %.*s (%zu bytes, no copy yet)\n",
                static_cast<int>(name.size()), name.data(), name.size());
    std::printf("value = %.*s (%zu bytes, no copy yet)\n",
                static_cast<int>(value.size()), value.data(), value.size());

    /* Copy at the boundary: this is the only allocation in the program. */
    const int length = std::atoi(std::string(value).c_str());
    std::printf("as a number: %d\n", length);
    return 0;
}
```

```text
name  = Content-Length (14 bytes, no copy yet)
value = 4096 (4 bytes, no copy yet)
as a number: 4096
```

Splitting a header line into its name and value allocates nothing, because a `string_view` is two
numbers and `substr` on one is arithmetic. The single allocation is at the boundary, where the value
stops being characters and becomes an `int`.

A `string_view` is a **non-owning** view, and that is the entire hazard. It is Chapter 23's reference
rule with a longer reach: the view is valid exactly as long as the buffer it points at is, and nothing
in the type system enforces it. The mistake is easy to make and invisible when you make it:

```cpp run-san-catch
#include <cstdio>
#include <string>
#include <string_view>

static std::string header_line() { return "Content-Type: text/html"; }

static std::string_view value_of(const std::string &line) {
    return std::string_view(line).substr(line.find(':') + 1);
}

int main() {
    /* header_line() returns a temporary std::string. It dies at the end of
       this statement, and `value` is a view into its buffer. */
    const std::string_view value = value_of(header_line());
    std::printf("value: %.*s\n", static_cast<int>(value.size()), value.data());
    return 0;
}
```

```text
ERROR: AddressSanitizer: heap-use-after-free
```

`header_line()` returns a `std::string` by value. That temporary is destroyed at the end of the
statement, and `value` is left pointing at a buffer that has been freed. The program does not crash —
it reads whatever is in that memory now, which is why this bug reaches production.

The rules that keep you out of it:

- **A `string_view` parameter is safe** as long as the caller's string outlives the call. Use it for
  read-only arguments you will not store.
- **A `string_view` return is a promise** that the buffer outlives the caller's use. Return one from a
  function that takes a reference to a string that will still be alive, and never from a function that
  built a temporary.
- **Store a `std::string`.** A member that holds a view into something else is a member whose validity
  depends on something the class does not control — the same trap Chapter 26 described for raw
  pointers, and the same fix applies.

The project's `Headers::get` returns `std::optional<std::string>` rather than a view, and that is the
conservative choice on purpose: it copies a few bytes and in exchange the caller can keep the result
for as long as it likes.

## The project

`http.h` and `http.cpp` hold `Status`, `Headers`, `Request` and `Response`; `router.h` and `router.cpp`
hold `Router`; `main.cpp` registers five routes and dispatches nine requests through them.

```cpp make-files
/* ===== http.h ===== */
#ifndef HTTP_H
#define HTTP_H

#include <cstddef>
#include <map>
#include <optional>
#include <string>

/* The status codes this service can produce. `enum class` means none of them
   converts to an int by accident. */
enum class Status {
    Ok               = 200,
    Created          = 201,
    NoContent        = 204,
    BadRequest       = 400,
    NotFound         = 404,
    MethodNotAllowed = 405,
    UriTooLong       = 414,
    ServerError      = 500,
};

const char *reason(Status s);
std::string status_line(Status s);

/* HTTP header names are case-insensitive; std::map is not. Keys are lowercased
   on the way in, so every lookup can be written in any case. */
class Headers {
public:
    void set(std::string name, std::string value);
    std::optional<std::string> get(const std::string &name) const;
    std::size_t size() const { return data_.size(); }
    std::string to_string() const;          /* one "Name: value\r\n" per header */

private:
    std::map<std::string, std::string> data_;
};

struct Request {
    std::string method;
    std::string target;                     /* the raw request target */
    std::string path;                       /* target with the query removed */
    std::string query;
    Headers headers;
    std::string body;

    /* Nothing if the request is malformed, or if the target has a bad escape. */
    static std::optional<Request> parse(const std::string &raw);
};

struct Response {
    Status status = Status::Ok;
    Headers headers;
    std::string body;

    /* Status line, headers, blank line, body - exactly what goes on the wire.
       Content-Length and Connection are filled in if the handler left them out. */
    std::string to_string() const;
};

std::optional<std::string> percent_decode(const std::string &in);

#endif
/* ===== http.cpp ===== */
#include "http.h"

#include <cctype>

namespace {

std::string lower(std::string s) {
    for (char &c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return s;
}

std::string trim(const std::string &s) {
    const std::size_t begin = s.find_first_not_of(" \t");
    if (begin == std::string::npos) return "";
    const std::size_t end = s.find_last_not_of(" \t");
    return s.substr(begin, end - begin + 1);
}

int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

}  // namespace

const char *reason(Status s) {
    switch (s) {
        case Status::Ok:               return "OK";
        case Status::Created:          return "Created";
        case Status::NoContent:        return "No Content";
        case Status::BadRequest:       return "Bad Request";
        case Status::NotFound:         return "Not Found";
        case Status::MethodNotAllowed: return "Method Not Allowed";
        case Status::UriTooLong:       return "URI Too Long";
        case Status::ServerError:      return "Internal Server Error";
    }
    return "Unknown";            /* unreachable: every value is handled above */
}

std::string status_line(Status s) {
    return "HTTP/1.1 " + std::to_string(static_cast<int>(s)) + " " + reason(s);
}

void Headers::set(std::string name, std::string value) {
    data_[lower(std::move(name))] = std::move(value);
}

std::optional<std::string> Headers::get(const std::string &name) const {
    const auto it = data_.find(lower(name));
    if (it == data_.end()) return std::nullopt;
    return it->second;
}

std::string Headers::to_string() const {
    std::string out;
    for (const auto &pair : data_) out += pair.first + ": " + pair.second + "\r\n";
    return out;
}

std::string Response::to_string() const {
    Headers out = headers;
    if (!out.get("content-length")) out.set("Content-Length", std::to_string(body.size()));
    if (!out.get("connection")) out.set("Connection", "close");
    return status_line(status) + "\r\n" + out.to_string() + "\r\n" + body;
}

std::optional<std::string> percent_decode(const std::string &in) {
    std::string out;
    out.reserve(in.size());
    for (std::size_t i = 0; i < in.size(); i++) {
        unsigned char c = static_cast<unsigned char>(in[i]);
        if (c == '%') {
            if (i + 2 >= in.size()) return std::nullopt;
            const int hi = hex_value(in[i + 1]);
            const int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return std::nullopt;
            c = static_cast<unsigned char>(hi * 16 + lo);
            if (c == 0) return std::nullopt;
            i += 2;
        }
        out.push_back(static_cast<char>(c));
    }
    return out;
}

std::optional<Request> Request::parse(const std::string &raw) {
    Request req;

    const std::size_t head_end = raw.find("\r\n\r\n");
    const std::string head = head_end == std::string::npos ? raw : raw.substr(0, head_end);

    /* The request line: METHOD SP TARGET SP VERSION. */
    const std::size_t first_eol = head.find("\r\n");
    const std::string line = head.substr(0, first_eol);

    const std::size_t sp1 = line.find(' ');
    if (sp1 == std::string::npos) return std::nullopt;
    const std::size_t sp2 = line.find(' ', sp1 + 1);
    if (sp2 == std::string::npos) return std::nullopt;

    req.method = line.substr(0, sp1);
    req.target = line.substr(sp1 + 1, sp2 - sp1 - 1);
    const std::string version = line.substr(sp2 + 1);
    if (version != "HTTP/1.1" && version != "HTTP/1.0") return std::nullopt;
    if (req.method.empty() || req.target.empty()) return std::nullopt;

    /* A malformed escape is caught here, once, so nothing downstream has to
       worry about it - including the router, which decodes path parameters. */
    if (!percent_decode(req.target)) return std::nullopt;

    const std::size_t question = req.target.find('?');
    if (question == std::string::npos) {
        req.path = req.target;
    } else {
        req.path = req.target.substr(0, question);
        req.query = req.target.substr(question + 1);
    }

    /* Headers, one per line, until the blank line. */
    std::size_t pos = first_eol == std::string::npos ? head.size() : first_eol + 2;
    while (pos < head.size()) {
        const std::size_t eol = head.find("\r\n", pos);
        const std::size_t end = eol == std::string::npos ? head.size() : eol;
        const std::string header = head.substr(pos, end - pos);
        const std::size_t colon = header.find(':');
        if (colon == std::string::npos) return std::nullopt;
        req.headers.set(header.substr(0, colon), trim(header.substr(colon + 1)));
        pos = end + 2;
    }

    /* The body is exactly as long as Content-Length says, or it is not there. */
    if (head_end != std::string::npos) {
        const auto declared = req.headers.get("content-length");
        if (declared) {
            const unsigned long want = std::stoul(*declared);
            const std::string rest = raw.substr(head_end + 4);
            if (rest.size() < want) return std::nullopt;
            req.body = rest.substr(0, want);
        }
    }
    return req;
}
/* ===== router.h ===== */
#ifndef ROUTER_H
#define ROUTER_H

#include <cstddef>
#include <functional>
#include <map>
#include <string>
#include <vector>

#include "http.h"

/* A path parameter, already percent-decoded. */
using Params = std::map<std::string, std::string>;

/* A handler is anything callable with this signature: a lambda, a function
   pointer, or a std::function someone stored earlier. */
using Handler = std::function<Response(const Request &, const Params &)>;

class Router {
public:
    /* ":name" in a pattern captures one segment. */
    void add(const std::string &method, const std::string &pattern, Handler handler);

    Response dispatch(const Request &req) const;
    std::size_t size() const { return routes_.size(); }

private:
    struct Route {
        std::string method;
        std::vector<std::string> segments;
        Handler handler;
    };

    static std::vector<std::string> split(const std::string &path);
    static bool match(const Route &route, const std::vector<std::string> &path,
                      Params *captured);

    std::vector<Route> routes_;
};

#endif
/* ===== router.cpp ===== */
#include "router.h"

#include <set>
#include <utility>

std::vector<std::string> Router::split(const std::string &path) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i < path.size()) {
        while (i < path.size() && path[i] == '/') i++;
        if (i >= path.size()) break;
        const std::size_t start = i;
        while (i < path.size() && path[i] != '/') i++;
        out.push_back(path.substr(start, i - start));
    }
    return out;
}

bool Router::match(const Route &route, const std::vector<std::string> &path,
                   Params *captured) {
    if (route.segments.size() != path.size()) return false;

    Params found;
    for (std::size_t i = 0; i < route.segments.size(); i++) {
        const std::string &piece = route.segments[i];
        if (piece.size() > 1 && piece[0] == ':') {
            /* The request target was validated when it was parsed, so a bad
               escape cannot reach here - but a segment can still fail to
               decode if it was split after decoding, which it was not. */
            const auto decoded = percent_decode(path[i]);
            if (!decoded) return false;
            found[piece.substr(1)] = *decoded;
        } else if (piece != path[i]) {
            return false;
        }
    }
    *captured = std::move(found);
    return true;
}

void Router::add(const std::string &method, const std::string &pattern, Handler handler) {
    routes_.push_back(Route{method, split(pattern), std::move(handler)});
}

Response Router::dispatch(const Request &req) const {
    const std::vector<std::string> path = split(req.path);

    /* First: does any route have this shape at all? */
    std::vector<const Route *> shape_matches;
    for (const Route &route : routes_) {
        Params ignored;
        if (match(route, path, &ignored)) shape_matches.push_back(&route);
    }

    if (shape_matches.empty()) {
        Response res;
        res.status = Status::NotFound;
        res.headers.set("Content-Type", "text/plain");
        res.body = "no route for " + req.path + "\n";
        return res;
    }

    /* Second: among those, is there one that accepts this method? */
    for (const Route *route : shape_matches) {
        if (route->method != req.method) continue;
        Params captured;
        match(*route, path, &captured);
        return route->handler(req, captured);
    }

    /* The path exists, the method does not. Say which ones do. */
    std::set<std::string> allowed;
    for (const Route *route : shape_matches) allowed.insert(route->method);

    std::string list;
    for (const std::string &method : allowed) {
        if (!list.empty()) list += ", ";
        list += method;
    }

    Response res;
    res.status = Status::MethodNotAllowed;
    res.headers.set("Allow", list);
    res.headers.set("Content-Type", "text/plain");
    res.body = "allowed: " + list + "\n";
    return res;
}
/* ===== main.cpp ===== */
#include "router.h"

#include <cstdio>
#include <cstring>
#include <string>

namespace {

Response text(Status status, const std::string &body) {
    Response res;
    res.status = status;
    res.headers.set("Content-Type", "text/plain");
    res.body = body;
    return res;
}

/* One line per request, so the table fits on a screen. */
std::string one_line(std::string s) {
    for (char &c : s) if (c == '\n' || c == '\r') c = ' ';
    while (!s.empty() && s.back() == ' ') s.pop_back();
    return s;
}

void dump(const std::string &label, const std::string &data) {
    std::printf("=== %s ===\n", label.c_str());
    for (char ch : data) {
        if (ch == '\r')      std::fputs("\\r", stdout);
        else if (ch == '\n') std::fputs("\\n\n", stdout);
        else                 std::putchar(ch);
    }
    if (data.empty() || data.back() != '\n') std::putchar('\n');
}

Router build_router() {
    Router router;

    router.add("GET", "/", [](const Request &, const Params &) {
        Response res;
        res.headers.set("Content-Type", "text/html");
        res.body = "<h1>hello</h1>\n";
        return res;
    });
    router.add("GET", "/health", [](const Request &, const Params &) {
        return text(Status::Ok, "{\"status\":\"ok\"}\n");
    });
    router.add("GET", "/items", [](const Request &, const Params &) {
        return text(Status::Ok, "[{\"id\":1},{\"id\":2}]\n");
    });
    router.add("GET", "/items/:id", [](const Request &, const Params &params) {
        return text(Status::Ok, "{\"id\":\"" + params.at("id") + "\"}\n");
    });
    router.add("POST", "/items", [](const Request &req, const Params &) {
        return text(Status::Created,
                    "received " + std::to_string(req.body.size()) + " bytes\n");
    });
    return router;
}

}  // namespace

int main(int argc, char **argv) {
    const Router router = build_router();

    if (argc == 2 && std::strcmp(argv[1], "--help") == 0) {
        std::printf("usage: %s                  run the built-in self-test\n", argv[0]);
        std::printf("       %s METHOD TARGET    dispatch one request and dump it\n", argv[0]);
        return 0;
    }

    /* One request from the command line, dumped exactly as it would be sent. */
    if (argc >= 3) {
        const std::string raw =
            std::string(argv[1]) + " " + argv[2] + " HTTP/1.1\r\nHost: x\r\n\r\n";
        const auto req = Request::parse(raw);
        if (!req) {
            std::fprintf(stderr, "malformed request: %s %s\n", argv[1], argv[2]);
            return 2;
        }
        dump(std::string(argv[1]) + " " + argv[2], router.dispatch(*req).to_string());
        return 0;
    }

    std::printf("%zu route(s) registered\n\n", router.size());

    const std::string requests[] = {
        "GET / HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /health HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /items/42 HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /items/a%20b HTTP/1.1\r\nHost: x\r\n\r\n",
        "POST /items HTTP/1.1\r\nHost: x\r\nContent-Length: 7\r\n\r\n{\"a\":1}",
        "DELETE /items HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /nope HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /items/42/extra HTTP/1.1\r\nHost: x\r\n\r\n",
        "GET /items/%zz HTTP/1.1\r\nHost: x\r\n\r\n",
    };

    for (const std::string &raw : requests) {
        const auto req = Request::parse(raw);
        if (!req) {
            std::printf("%-6s %-18s %-3d %s\n", "?", "?", 400, "Bad Request (unparseable)");
            continue;
        }
        const Response res = router.dispatch(*req);
        std::printf("%-6s %-18s %-3d %-18s %s\n",
                    req->method.c_str(), req->path.c_str(),
                    static_cast<int>(res.status), reason(res.status),
                    one_line(res.body).c_str());
    }

    std::printf("\n");
    const auto first = Request::parse(requests[0]);
    dump("GET / on the wire", router.dispatch(*first).to_string());
    return 0;
}
/* ===== Makefile ===== */
CXX      = c++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -O2

OBJS     = main.o http.o router.o

prog: $(OBJS)
	$(CXX) $(CXXFLAGS) -o prog $(OBJS)

main.o: main.cpp router.h http.h
	$(CXX) $(CXXFLAGS) -c main.cpp

http.o: http.cpp http.h
	$(CXX) $(CXXFLAGS) -c http.cpp

router.o: router.cpp router.h http.h
	$(CXX) $(CXXFLAGS) -c router.cpp

clean:
	rm -f prog $(OBJS)

.PHONY: clean
```

```text
5 route(s) registered

GET    /                  200 OK                 <h1>hello</h1>
GET    /health            200 OK                 {"status":"ok"}
GET    /items/42          200 OK                 {"id":"42"}
GET    /items/a%20b       200 OK                 {"id":"a b"}
POST   /items             201 Created            received 7 bytes
DELETE /items             405 Method Not Allowed allowed: GET, POST
GET    /nope              404 Not Found          no route for /nope
GET    /items/42/extra    404 Not Found          no route for /items/42/extra
?      ?                  400 Bad Request (unparseable)

=== GET / on the wire ===
HTTP/1.1 200 OK\r\n
connection: close\r\n
content-length: 15\r\n
content-type: text/html\r\n
\r\n
<h1>hello</h1>\n
```

Read the middle of that table, where the interesting answers are. `GET /items/42` finds the `:id` route
and the handler sees `"42"`; `GET /items/a%20b` finds the same route and the handler sees `"a b"`,
because the parameter was percent-decoded after the path was split — so a `%2f` in a parameter would
be a literal slash in the value rather than a path separator. `POST /items` reaches a different handler
for the same path and answers `201`, which is why the router cannot simply key routes by path.
`DELETE /items` gets `405` with `Allow: GET, POST`, and `GET /nope` and `GET /items/42/extra` both get
`404` — including `/items/42/extra`, which has a *longer* path than any registered route. A router that
matched by prefix would have sent that one to the `/items` handler. That mistake has its own section
below, because it is the most common way a hand-written router goes wrong.

The last request, `GET /items/%zz`, never reaches the router at all: `Request::parse` refuses it, and
`main` reports `400 Bad Request`. One place decides what a well-formed target is, and it decides before
anything else looks at it.

## Driving it from the shell

The self-test exercises the model directly. The command line makes the same model visible one request
at a time, and prints exactly the bytes the socket would carry:

```sh run-project
./prog --help
echo "---"
./prog GET /health
./prog GET /items/7
./prog DELETE /items
./prog GET /nope
exit 0
```

```text
usage: ./prog                  run the built-in self-test
       ./prog METHOD TARGET    dispatch one request and dump it
---
=== GET /health ===
HTTP/1.1 200 OK\r\n
connection: close\r\n
content-length: 16\r\n
content-type: text/plain\r\n
\r\n
{"status":"ok"}\n
=== GET /items/7 ===
HTTP/1.1 200 OK\r\n
connection: close\r\n
content-length: 11\r\n
content-type: text/plain\r\n
\r\n
{"id":"7"}\n
=== DELETE /items ===
HTTP/1.1 405 Method Not Allowed\r\n
allow: GET, POST\r\n
connection: close\r\n
content-length: 19\r\n
content-type: text/plain\r\n
\r\n
allowed: GET, POST\n
=== GET /nope ===
HTTP/1.1 404 Not Found\r\n
connection: close\r\n
content-length: 19\r\n
content-type: text/plain\r\n
\r\n
no route for /nope\n
```

That is the whole reason to build `Response::to_string`: the response is a value you can print, compare
and test without a socket in sight. Chapter 34's server had the same property and used it for the
self-test; here it is the primary interface, and the socket layer is the thin part on top.

:::scenario The body that was never read

A `POST` endpoint is added. It reads `req.body`, parses the JSON, stores the record. The self-test
passes — it builds a request string in memory and parses it, so the body is right there. In production
every request fails with "empty body", and the client is sending valid JSON.

The bug is in Chapter 34's socket code, and it has been there all along:

```cpp
const std::string raw = conn.read_until("\r\n\r\n", kRequestCap);
conn.write_all(handle(raw));
```

`read_until` stops **at the blank line** — the end of the headers. For a static file server that is
correct and it is all you need, because a `GET` has no body. For anything that reads `req.body` it is
wrong: the body bytes are still in the socket buffer, unread, and `Request::parse` sees a
`Content-Length: 7` with nothing after it.

It gets worse before it gets better. A client that sends the headers and the body in two writes is the
easy case; a client that sends them together can have both arrive in the same `read`, so sometimes
`raw` *does* contain the body and the endpoint works. That is the shape of a bug that survives a demo
and fails under load.

```cpp run
#include <cstdio>
#include <cstdlib>
#include <string>
#include <unistd.h>
#include <sys/socket.h>

/* Chapter 34's read_until: stop as soon as the blank line arrives. */
static std::string read_until(int fd, const std::string &marker, std::size_t cap) {
    std::string got;
    char buf[1024];
    while (got.size() < cap) {
        const ssize_t n = ::read(fd, buf, sizeof buf);
        if (n <= 0) break;
        got.append(buf, static_cast<std::size_t>(n));
        if (got.find(marker) != std::string::npos) break;
    }
    return got;
}

/* The number Request::parse would take from the headers. */
static unsigned long content_length(const std::string &head) {
    const std::size_t at = head.find("Content-Length:");
    if (at == std::string::npos) return 0;
    return std::strtoul(head.c_str() + at + 15, nullptr, 10);
}

int main() {
    int fds[2] = {-1, -1};
    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, fds) != 0) return 1;

    const std::string head = "POST /items HTTP/1.1\r\nHost: x\r\nContent-Length: 7\r\n\r\n";
    const std::string payload = "{\"a\":1}";

    /* The client writes the headers first, and the body after - which is what
       any client does when the two are produced separately. */
    if (::write(fds[1], head.data(), head.size()) < 0) return 1;

    const std::string got = read_until(fds[0], "\r\n\r\n", 8192);
    const std::size_t blank = got.find("\r\n\r\n");
    const std::size_t body_bytes = blank == std::string::npos ? 0 : got.size() - (blank + 4);

    std::printf("read_until gave %zu bytes, ending at the blank line\n", got.size());
    std::printf("Content-Length says %lu\n", content_length(got));
    std::printf("body the handler would see: %zu bytes\n", body_bytes);

    /* The fix: once the headers are parsed, read exactly what they promised. */
    if (::write(fds[1], payload.data(), payload.size()) < 0) return 1;

    const unsigned long want = content_length(got);
    std::string body(want, '\0');
    const ssize_t n = ::read(fds[0], body.data(), body.size());
    body.resize(n > 0 ? static_cast<std::size_t>(n) : 0);

    std::printf("after reading Content-Length more: %zu bytes -> %s\n", body.size(), body.c_str());

    ::close(fds[0]);
    ::close(fds[1]);
    return 0;
}
```

```text
read_until gave 52 bytes, ending at the blank line
Content-Length says 7
body the handler would see: 0 bytes
after reading Content-Length more: 7 bytes -> {"a":1}
```

:::solution Read the headers, then read what they promised

The socket layer keeps its shape and gains one step: after the headers arrive, ask them how much body
to expect and read that much.

```cpp
Socket conn = listener_.accept_one();

/* Headers first, because that is where the length is. */
std::string raw = conn.read_until("\r\n\r\n", kRequestCap);

/* Then exactly as many more bytes as the headers declared. */
if (const auto declared = content_length_of(raw)) {
    const std::string more = conn.read_exactly(*declared);
    raw += more;
}

conn.write_all(handle(raw).to_string());
```

`read_exactly` is a loop, not one `read`: a stream socket is allowed to return fewer bytes than you
asked for, and on a real network it often will. One `read` of 100000 bytes that returns 4096 is normal,
and a server that treats it as the whole body truncates large uploads on exactly the connections that
are slowest.

The general lesson is the one the whole chapter is about: **the layer that owns the bytes has to hand
the layer above a complete message.** Chapter 34's `read_until` stopped at the first boundary it found
because the boundary was all it needed. Once a layer above depends on the rest of the message, the
boundary is not the end of the work — and nothing warns you, because the headers were complete and
correct and the parse succeeded.

:::

:::

:::pitfall The route that matched too much

A router written with `find` instead of a segment comparison is the most common way this goes wrong.
`path.rfind(pattern, 0) == 0` asks "does the path start with the pattern", which is a different question
from "are these the same path":

```cpp run
#include <cstdio>
#include <string>
#include <vector>

struct Route { std::string pattern; };

/* WRONG: "does the path start with the pattern". */
static const char *prefix_match(const std::vector<Route> &routes, const std::string &path) {
    for (const Route &r : routes) {
        if (path.rfind(r.pattern, 0) == 0) return r.pattern.c_str();
    }
    return "(no match)";
}

/* RIGHT: compare segment by segment, so the shapes must be the same length. */
static std::vector<std::string> split(const std::string &path) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i < path.size()) {
        while (i < path.size() && path[i] == '/') i++;
        if (i >= path.size()) break;
        const std::size_t start = i;
        while (i < path.size() && path[i] != '/') i++;
        out.push_back(path.substr(start, i - start));
    }
    return out;
}

static const char *segment_match(const std::vector<Route> &routes, const std::string &path) {
    const std::vector<std::string> parts = split(path);
    for (const Route &r : routes) {
        const std::vector<std::string> pattern = split(r.pattern);
        if (pattern.size() != parts.size()) continue;
        bool same = true;
        for (std::size_t i = 0; i < pattern.size() && same; i++) {
            if (pattern[i].size() > 1 && pattern[i][0] == ':') continue;
            if (pattern[i] != parts[i]) same = false;
        }
        if (same) return r.pattern.c_str();
    }
    return "(no match)";
}

int main() {
    const std::vector<Route> routes = {{"/items"}, {"/items/:id"}, {"/"}};

    const char *paths[] = {"/items", "/items/42", "/items/42/extra", "/itemsX"};
    for (const char *path : paths) {
        std::printf("%-18s prefix -> %-12s segments -> %s\n", path,
                    prefix_match(routes, path), segment_match(routes, path));
    }
    return 0;
}
```

```text
/items             prefix -> /items       segments -> /items
/items/42          prefix -> /items       segments -> /items/:id
/items/42/extra    prefix -> /items       segments -> (no match)
/itemsX            prefix -> /items       segments -> (no match)
```

Three failures in one table. `/items/42` goes to the `/items` handler, so `GET /items/42` returns the
list instead of the item — and if that handler is a `DELETE`, it deletes the wrong thing. `/itemsX`
matches `/items` even though there is no slash, so a typo in a client is answered with real data.
`/items/42/extra` is served by `/items` rather than refused, which means every unmatched path under a
registered prefix is answered by that prefix's handler. In a file server that is a directory traversal;
in an API it is an endpoint that answers for paths it was never given.

The fix is to compare *shapes*, which means splitting both the pattern and the path and requiring the
same number of segments. The `pattern.size() != parts.size()` line is the one that stops all three
failures, and it is easy to leave out — a loop over `pattern` alone silently ignores extra path
segments, which is the third bug in the table.

:::

## Key takeaways

- Header names are case-insensitive; `std::map` is not. Normalise the key in the one function every
  write goes through, so no call site can get the case wrong.
- Return `std::optional` for "absent" and never an empty string, because an empty header is a valid
  header and the two must be distinguishable.
- `enum class` gives scoped names, no implicit conversion in either direction, and — with `-Wswitch` —
  a compiler that tells you when a `switch` has missed a value you just added.
- Return `std::optional<Request>` from a parser: a malformed request is an expected outcome the caller
  has a specific answer for. Reserve exceptions for "cannot continue".
- Validate the target once, in `parse`, and let everything downstream assume it is well-formed. One
  place to audit beats two.
- `Response::to_string` fills in `Content-Length` from `body.size()`, so the header cannot disagree with
  the payload. A `const` method can still do this, because it copies the headers it amends.
- `std::function` erases the handler's type, so a function, a lambda and a capturing lambda all fit the
  same route table. Use an abstract base instead when handlers are big or you want the compiler to
  enforce that they are complete.
- **Ask about shape before method.** No route with that shape means `404`; the right shape with the
  wrong method means `405` plus an `Allow` header. Answering `405` for a path that does not exist tells
  clients something is there when it is not.
- `Allow` comes from a `std::set`, so it is deduplicated and sorted. A header listing is a contract.
- A `string_view` is a pointer and a length. A view parameter is safe; a view *returned* from a function
  that built a temporary is a use-after-free, and ASan catches it only because the buffer was on the
  heap.
- Match paths by **shape**, not by prefix. Prefix matching sends `/items/42` to the `/items` handler and
  answers for `/itemsX`.
- The layer that owns the bytes must hand the layer above a complete message. Headers that arrive
  complete are not the same as a request that arrived complete.

## Practice

- [ ] Write `parse_query` so `?q=hello%20world&page=2&flag` becomes a map with three entries, one of
      them empty. Explain what should happen to a pair whose value fails to percent-decode.
- [ ] `reason()` handles every value of `Status`. Write a program that prints the status line for all of
      them, and explain why listing the values in an array is a better test than calling `reason` eight
      times by hand.
- [ ] Show what `Router::split` does with `/items/`, `//items` and `/items//`. Explain why a route
      registered as `/items` matches all three, and whether that is a bug.
- [ ] `Allow` is built from a `std::set`. Show what it would look like built from the `std::vector` the
      router already has, and say which of the two you would want a client to receive.
- [ ] A handler throws `std::runtime_error`. Wrap the call in `dispatch` so the caller gets `500` and a
      body, and explain why catching inside `dispatch` is better than catching in `serve_one`.
- [ ] Add a `HEAD` route for `/items/:id` that returns the headers with an empty body. Which part of
      `Response` has to change, and why can a `const` method not do it?

## Solutions

:::solution Exercise 1

Split on `&`, then on the first `=`, and percent-decode both halves:

```cpp run
#include <cstdio>
#include <map>
#include <optional>
#include <string>

static int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

std::optional<std::string> percent_decode(const std::string &in) {
    std::string out;
    for (std::size_t i = 0; i < in.size(); i++) {
        unsigned char c = static_cast<unsigned char>(in[i]);
        if (c == '%') {
            if (i + 2 >= in.size()) return std::nullopt;
            const int hi = hex_value(in[i + 1]);
            const int lo = hex_value(in[i + 2]);
            if (hi < 0 || lo < 0) return std::nullopt;
            c = static_cast<unsigned char>(hi * 16 + lo);
            if (c == 0) return std::nullopt;
            i += 2;
        }
        out.push_back(static_cast<char>(c));
    }
    return out;
}

/* "q=hello%20world&page=2&flag" -> {q: hello world, page: 2, flag: ""} */
std::map<std::string, std::string> parse_query(const std::string &query) {
    std::map<std::string, std::string> out;
    std::size_t i = 0;
    while (i <= query.size() && !query.empty()) {
        const std::size_t amp = query.find('&', i);
        const std::string pair = query.substr(
            i, amp == std::string::npos ? std::string::npos : amp - i);

        const std::size_t eq = pair.find('=');
        if (eq == std::string::npos) {
            const auto key = percent_decode(pair);
            if (key) out[*key] = "";
        } else {
            const auto key = percent_decode(pair.substr(0, eq));
            const auto value = percent_decode(pair.substr(eq + 1));
            if (key && value) out[*key] = *value;
        }

        if (amp == std::string::npos) break;
        i = amp + 1;
    }
    return out;
}

int main() {
    const auto query = parse_query("q=hello%20world&page=2&flag");
    for (const auto &pair : query) {
        std::printf("%-6s = %s\n", pair.first.c_str(),
                    pair.second.empty() ? "(empty)" : pair.second.c_str());
    }
    return 0;
}
```

```text
flag   = (empty)
page   = 2
q      = hello world
```

The iteration is sorted because the container is a `std::map`, not because the query was in that order.
Three entries from three different shapes: `k=v`, a bare `k` with no `=`, and a value that needed
decoding.

A pair whose value fails to decode should be **dropped**, not turned into an empty string. `?q=%zz`
is a client error, and silently reading it as `q=""` gives the handler a value the client never sent —
the same mistake as treating a missing header as an empty one. If you want the client to know, make
`parse_query` return `std::optional` and let the caller answer `400`; either way, "could not decode" and
"decoded to nothing" must not be the same value.

:::

:::solution Exercise 2

```cpp run
#include <cstdio>
#include <string>

enum class Status {
    Ok               = 200,
    Created          = 201,
    NoContent        = 204,
    BadRequest       = 400,
    NotFound         = 404,
    MethodNotAllowed = 405,
    UriTooLong       = 414,
    ServerError      = 500,
};

const char *reason(Status s) {
    switch (s) {
        case Status::Ok:               return "OK";
        case Status::Created:          return "Created";
        case Status::NoContent:        return "No Content";
        case Status::BadRequest:       return "Bad Request";
        case Status::NotFound:         return "Not Found";
        case Status::MethodNotAllowed: return "Method Not Allowed";
        case Status::UriTooLong:       return "URI Too Long";
        case Status::ServerError:      return "Internal Server Error";
    }
    return "Unknown";
}

std::string status_line(Status s) {
    return "HTTP/1.1 " + std::to_string(static_cast<int>(s)) + " " + reason(s);
}

int main() {
    /* Listing every value is what keeps the switch honest: add one to the enum
       and this array no longer compiles, which is the reminder you want. */
    const Status all[] = {
        Status::Ok,        Status::Created,          Status::NoContent,
        Status::BadRequest, Status::NotFound,        Status::MethodNotAllowed,
        Status::UriTooLong, Status::ServerError,
    };
    for (Status s : all) std::printf("%s\n", status_line(s).c_str());
    return 0;
}
```

```text
HTTP/1.1 200 OK
HTTP/1.1 201 Created
HTTP/1.1 204 No Content
HTTP/1.1 400 Bad Request
HTTP/1.1 404 Not Found
HTTP/1.1 405 Method Not Allowed
HTTP/1.1 414 URI Too Long
HTTP/1.1 500 Internal Server Error
```

An array of every value is a better test than eight calls for two reasons. It prints the whole set in
one place, so a wrong reason phrase or a wrong number is visible against its neighbours. And it is a
*compile-time* check on the enum: `Status::Created` cannot be removed without breaking this array, and
a new value cannot be added without someone noticing that this list does not have it. Eight separate
calls would keep compiling through both.

Notice that `static_cast<int>(s)` is the only conversion in the program, and it is in `status_line`,
where the number is genuinely needed. `reason` never sees an `int`, and neither does anything that
calls `status_line`.

:::

:::solution Exercise 3

```cpp run
#include <cstdio>
#include <string>
#include <vector>

/* The splitter that skips runs of slashes, so an empty segment never exists. */
static std::vector<std::string> split(const std::string &path) {
    std::vector<std::string> out;
    std::size_t i = 0;
    while (i < path.size()) {
        while (i < path.size() && path[i] == '/') i++;
        if (i >= path.size()) break;
        const std::size_t start = i;
        while (i < path.size() && path[i] != '/') i++;
        out.push_back(path.substr(start, i - start));
    }
    return out;
}

static std::string show(const std::vector<std::string> &parts) {
    std::string out = "{";
    for (std::size_t i = 0; i < parts.size(); i++) {
        if (i != 0) out += ", ";
        out += '"' + parts[i] + '"';
    }
    return out + "}";
}

int main() {
    for (const char *path : {"/items", "/items/", "//items", "/items//", "/"}) {
        std::printf("%-10s -> %s\n", path, show(split(path)).c_str());
    }
    return 0;
}
```

```text
/items     -> {"items"}
/items/    -> {"items"}
//items    -> {"items"}
/items//   -> {"items"}
/          -> {}
```

All four spellings of `/items` produce the same one-element vector, so they all match a route
registered as `/items`. That falls out of the `while (path[i] == '/') i++;` at the top of the loop,
which consumes a *run* of slashes rather than one — so an empty segment is never produced in the first
place.

Is that a bug? For a public API, treating `/items/` and `/items` as the same resource is what every
framework does and what users expect; a trailing slash is a typographic habit, not a different
resource. What it costs is the ability to *distinguish* them, so if you ever need `/items/` to mean
something else — a collection with a trailing-slash convention, say — this splitter cannot express it
and you would need to keep empty segments and handle the `{}` case for the root.

The last line is the one worth staring at. `/` splits to the empty vector, which is why the route
pattern `/` also splits to the empty vector and the two match. If you had instead kept empty segments,
`/` would be `{"", ""}` and the root route would need a special case. Skipping them makes the root fall
out of the same rule as everything else.

:::

:::solution Exercise 4

```cpp run
#include <cstdio>
#include <set>
#include <string>
#include <vector>

static std::string join(const std::vector<std::string> &methods) {
    std::string list;
    for (const std::string &method : methods) {
        if (!list.empty()) list += ", ";
        list += method;
    }
    return list;
}

static std::string join_sorted(const std::vector<std::string> &methods) {
    const std::set<std::string> unique(methods.begin(), methods.end());
    std::string list;
    for (const std::string &method : unique) {
        if (!list.empty()) list += ", ";
        list += method;
    }
    return list;
}

int main() {
    /* Two routes can share a path and differ only by method, so the same
       method turns up more than once. */
    const std::vector<std::string> found = {"POST", "GET", "POST"};

    std::printf("as found:   %s\n", join(found).c_str());
    std::printf("as a set:   %s\n", join_sorted(found).c_str());
    return 0;
}
```

```text
as found:   POST, GET, POST
as a set:   GET, POST
```

The vector version is the router's own order, which is registration order — so it repeats `POST`
because two routes matched the same shape with that method, and it puts `POST` before `GET` because
that is the order they were added. The set version is deduplicated and sorted.

Send the set version. `Allow` is a list a client is entitled to read literally, and RFC 7231 specifies
that its members are comma-separated and that a client may compare them as a set — but a human reading
a log, or a test asserting on the header, is much better served by a canonical order than by whatever
the registration sequence happened to be. Sorted and deduplicated is the version that does not change
when someone reorders two lines in `main`.

The cost is that the set loses the registration order, which matters only if you wanted to say
"try these in order". `Allow` does not.

:::

:::solution Exercise 5

```cpp run
#include <cstdio>
#include <functional>
#include <stdexcept>
#include <string>

using Handler = std::function<std::string()>;

/* A handler that throws must not take the server down. It becomes a status and
   a body, like any other outcome. */
static std::string run_handler(const Handler &handler, int *status) {
    try {
        *status = 200;
        return handler();
    } catch (const std::exception &e) {
        *status = 500;
        return e.what();
    }
}

int main() {
    int status = 0;

    const Handler good = [] { return std::string("{\"items\":2}"); };
    std::string body = run_handler(good, &status);
    std::printf("good handler: status %d, body %s\n", status, body.c_str());

    const Handler bad = []() -> std::string { throw std::runtime_error("no database"); };
    body = run_handler(bad, &status);
    std::printf("bad handler:  status %d, body %s\n", status, body.c_str());

    return 0;
}
```

```text
good handler: status 200, body {"items":2}
bad handler:  status 500, body no database
```

Catching inside `dispatch` — rather than in `serve_one` — is better for three reasons. The response
still gets sent: a `try` in `serve_one` around `conn.write_all(...)` would have to catch *before* the
write, so it would have to build the error response itself and the `Response` type would have two
producers. The handler's own context is still available: `dispatch` knows which route ran, so it can
log the method and path, which `serve_one` no longer has in scope. And the status code belongs to the
HTTP layer: `500` is a statement about a request, and the layer that understands requests is the one
that should say it.

Do not catch `...`. Chapter 30's warning applies: a bare catch swallows the bugs you most need to see,
including the ones that are not exceptions you can describe. `catch (const std::exception &e)` handles
everything the standard library and your own types throw, and lets anything else — a thrown `int`, a
failed `static_assert`-style abort — behave as the failure it is.

One thing to add when you do this for real: the body should not be `e.what()` verbatim. It leaks
internal detail to the client. Log `e.what()` and send a generic message, which is a security decision
rather than a C++ one, and it is the kind of thing that is easy to get wrong when the error path is
three lines long.

:::

:::solution Exercise 6

`HEAD` needs a response whose headers describe the body that *would* have been sent, with no body
bytes. `Response::to_string` is where that has to change, because it is the only place that knows both
the body and the headers:

```cpp
std::string Response::to_string(bool include_body = true) const {
    Headers out = headers;
    if (!out.get("content-length")) out.set("Content-Length", std::to_string(body.size()));
    if (!out.get("connection")) out.set("Connection", "close");
    const std::string head = status_line(status) + "\r\n" + out.to_string() + "\r\n";
    return include_body ? head + body : head;
}
```

A `const` method cannot do this on its own, because there are two different things it could mean and
only the caller knows which. If `to_string` cleared `body` and returned the headers, it would be
mutating — or, if it copied the whole `Response` first, allocating a copy of the body just to throw it
away. Passing a flag says what you want without changing what the object is. `Content-Length` still
comes from `body.size()`, which is the part that matters: a client asking `HEAD` to find out how big a
resource is must be told the real size, not zero.

The other half is in the router, and it is the reason `HEAD` is worth thinking about at all. A `HEAD`
request should reach the same handler a `GET` would, with the body suppressed at the last moment — so
either you register every route twice, once per method, or `dispatch` treats `HEAD` as `GET` and passes
the difference down. Registering twice doubles the route table and makes it possible to have a `HEAD`
that answers differently from its `GET`, which is exactly the bug the two-method design was supposed to
prevent.

:::
