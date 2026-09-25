---
chapter: 27
part: 4
title: Requests, Responses and Routing
summary: Move the service off HttpExchange. A request and a response become plain values, one adapter file touches the socket, and the router keeps 404 and 405 apart.
minutes: 70
tags: [http, routing, records, design, adapters, status-codes]
---

Chapter 26 left you with a working server and a handler that takes an `HttpExchange`. That handler is
holding a live socket. It can read the network and write the network, and there is no way to call it
with a path and see what it answers — testing it means starting a server, opening a connection, and
reading bytes back. Every routing rule you write lives inside a running process.

This chapter moves the service off that type. The move is small, it is mechanical, and it is the single
change that makes the rest of this Part possible: **a request and a response become plain values**, and
one file — exactly one — still knows what a socket is. Everything after that file is ordinary Java that
runs in a `main` method with no server anywhere.

## A handler that is holding a socket

Here is the shape Chapter 26 ended with:

```java
server.createContext("/notes", exchange -> {
    String id = exchange.getRequestURI().getPath().substring("/notes/".length());
    byte[] body = ("note " + id).getBytes(StandardCharsets.UTF_8);
    exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
    exchange.sendResponseHeaders(200, body.length);
    try (OutputStream out = exchange.getResponseBody()) {
        out.write(body);
    }
});
```

Count what this handler knows. It knows the path format (`/notes/` plus an id, sliced by character
offset). It knows the content type and the encoding. It knows that `sendResponseHeaders` takes a length
in bytes. It knows the response body is an `OutputStream` that has to be closed. It knows `200`.

Now ask a smaller question: **which of those things is the answer to "what should `GET /notes/7`
return?"** Only the last two lines. The rest is protocol plumbing that has nothing to do with notes.

:::tip Separate the decision from the transport

The test for this separation is a sentence: *"the handler decides what the answer is; something else
decides how an answer becomes bytes."* When a handler contains `\r\n`, a `byte[]`, or the word
`Content-Type`, the two jobs have been mixed, and the mixing is what forces a server into every test.

:::

So the service gets two new types. A `Request` is what a handler is allowed to know. A `Response` is
what a handler is allowed to produce.

## A request as a value

```java run-files
// ===== RequestDemo.java =====

import java.util.List;
import java.util.Map;

public class RequestDemo {
    public static void main(String[] args) {
        Request request = new Request("GET", "/notes/7", Map.of("q", List.of("milk")),
                Map.of("accept", "text/plain"), "", Map.of("id", "7"));

        System.out.println("method  " + request.method());
        System.out.println("path    " + request.path());
        System.out.println("var id  " + request.var("id"));
        System.out.println("query q " + request.query("q"));
        System.out.println("accept  " + request.header("Accept"));

        System.out.println();
        System.out.println("asking for a variable the pattern never declared:");
        try {
            request.var("nope");
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }

        System.out.println();
        Request other = request.withVars(Map.of("id", "9"));
        System.out.println("after withVars, the original still says id = " + request.var("id"));
        System.out.println("and the copy says id = " + other.var("id"));
        System.out.println("a record cannot be edited in place, so a handler cannot corrupt another's request");
    }
}

// ===== Request.java =====

import java.util.List;
import java.util.Map;

/** Everything a handler is allowed to know about the request. No socket, no exchange. */
public record Request(String method, String path, Map<String, List<String>> query,
                      Map<String, String> headers, String body, Map<String, String> vars) {

    /** The shape a test or a demo uses, with no query, no headers and no path variables. */
    public Request(String method, String path, String body) {
        this(method, path, Map.of(), Map.of(), body, Map.of());
    }

    /** The same request, with the path variables the router pulled out of the pattern. */
    public Request withVars(Map<String, String> vars) {
        return new Request(method, path, query, headers, body, vars);
    }

    public String var(String name) {
        String value = vars.get(name);
        if (value == null) {
            throw new IllegalArgumentException("no path variable " + name + " on " + path);
        }
        return value;
    }

    public String header(String name) {
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            if (entry.getKey().equalsIgnoreCase(name)) {
                return entry.getValue();
            }
        }
        return null;
    }

    public String query(String name) {
        List<String> values = query.get(name);
        return values == null || values.isEmpty() ? null : values.get(0);
    }
}
```

```text
method  GET
path    /notes/7
var id  7
query q milk
accept  text/plain

asking for a variable the pattern never declared:
  no path variable nope on /notes/7

after withVars, the original still says id = 7
and the copy says id = 9
a record cannot be edited in place, so a handler cannot corrupt another's request
```

Six components, and none of them is a socket: the method, the path, the query parameters, the headers,
the body, and the path variables the router pulled out of the pattern.

Three details in that output are the whole point of the type.

**Asking for a variable that is not there throws.** `no path variable nope on /notes/7` — not `null`.
That is a deliberate choice. A handler that reads `var("id")` on a route whose pattern has no `{id}` has
a bug in the *pattern*, and the pattern is written somewhere else, in the table the router was built
from. Returning `null` would move that bug into the handler's body, where it becomes a
`NullPointerException` two frames later with no mention of routing. Throwing names the mistake where it
was made. This is the same instinct as Chapter 24's exit codes: a failure should be reported as itself.

**Header lookup ignores case.** The record stores `accept` and the call asked for `Accept`. Chapter 25
measured on the wire that header names are case-insensitive; this is that rule implemented, once, in one
method, so that no handler has to remember it.

**`withVars` returns a copy.** After `request.withVars(Map.of("id", "9"))`, the original still says `7`.
A record cannot be edited in place, so a router can attach variables to a request without any possibility
of a handler seeing another request's variables. The compiler enforces it, not discipline.

## A response as a value

```java run-files
// ===== ResponseDemo.java =====

import java.nio.charset.StandardCharsets;

public class ResponseDemo {
    public static void main(String[] args) {
        Response[] responses = {
            Response.ok("every note"),
            Response.text(201, "added buy milk"),
            Response.notFound("/notes/9"),
            Response.methodNotAllowed("PUT", "GET, POST"),
        };

        for (Response response : responses) {
            System.out.printf("%d  %-26s %2d byte(s)  %s%n", response.status(),
                    response.contentType(), response.length(), response.body());
        }

        System.out.println();
        String ascii = "hello";
        String accented = "h\u00e9llo";
        System.out.println("'" + ascii + "' is " + ascii.length() + " char(s) and "
                + ascii.getBytes(StandardCharsets.UTF_8).length + " byte(s)");
        System.out.println("'" + accented + "' is " + accented.length() + " char(s) and "
                + accented.getBytes(StandardCharsets.UTF_8).length + " byte(s)");

        Response tall = Response.ok(accented);
        System.out.println();
        System.out.println("Response.ok(\"" + accented + "\").length() = " + tall.length());
        System.out.println("length() counts bytes, because bytes are what the header promises");
        System.out.println("a writer that used String.length() would promise 5 and send 6");
    }
}

// ===== Response.java =====

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/** A response as a value: nothing is written until something asks for the bytes. */
public record Response(int status, String contentType, String body) {

    static final String TEXT = "text/plain; charset=utf-8";

    public static Response text(int status, String body) {
        return new Response(status, TEXT, body);
    }

    public static Response ok(String body) {
        return text(200, body);
    }

    public static Response notFound(String path) {
        return text(404, "no route for " + path);
    }

    public static Response methodNotAllowed(String method, String allow) {
        return text(405, method + " is not allowed; try " + allow);
    }

    /** The length of the body as bytes, which is what the wire needs. */
    public int length() {
        return body.getBytes(StandardCharsets.UTF_8).length;
    }

    /** The one place that turns a response value into a framed HTTP response. */
    public void writeTo(com.sun.net.httpserver.HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", contentType);
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }
}
```

```text
200  text/plain; charset=utf-8  10 byte(s)  every note
201  text/plain; charset=utf-8  14 byte(s)  added buy milk
404  text/plain; charset=utf-8  21 byte(s)  no route for /notes/9
405  text/plain; charset=utf-8  33 byte(s)  PUT is not allowed; try GET, POST

'hello' is 5 char(s) and 5 byte(s)
'héllo' is 5 char(s) and 6 byte(s)

Response.ok("héllo").length() = 6
length() counts bytes, because bytes are what the header promises
a writer that used String.length() would promise 5 and send 6
```

The record has three components — status, content type, body — and the factories exist so that a handler
never spells out `200` or `text/plain; charset=utf-8` by hand. `Response.notFound(path)` is the one that
pays for itself, because it makes the service's 404 format a single decision instead of one decision per
handler.

The interesting method is `length()`, and the measurement above is why:

```
'hello' is 5 char(s) and 5 byte(s)
'héllo' is 5 char(s) and 6 byte(s)
```

Five characters either way. Six bytes for the second one, because `é` is two bytes in UTF-8. So
`Response.ok("héllo").length()` is `6`, and a writer that promised `body.length()` would promise 5 and
send 6 — which is precisely the understated-header failure Chapter 25 measured, where the client read
five bytes, dropped the last character, and no status code said anything was wrong.

`writeTo` is where that gets fixed, and it is worth reading closely. It converts the body to a `byte[]`
**once**, then uses that one array for both the header and the write:

```java
byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
exchange.sendResponseHeaders(status, bytes.length);
```

One array, one length, one place. The two numbers cannot disagree, because there is only one number. That
is the structural answer to Chapter 26's scenario — the response that declared 100 bytes and wrote 14 —
and it is a better answer than care, because care is not checkable.

:::warning One writer, or none

The moment a second place writes a response, the guarantee is gone. The rule is not "remember to count
bytes"; the rule is "`Response` is the only type that calls `sendResponseHeaders`". Everything else
returns a `Response` and lets this method frame it.

:::

## The one file that still knows about the socket

```java run-files
// ===== AdapterDemo.java =====

import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/** What the adapter saw, printed from inside the handler. */
public class AdapterDemo {
    public static void main(String[] args) throws Exception {
        List<String> seen = new ArrayList<>();
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            Request request = Requests.from(exchange);
            seen.add("method  " + request.method());
            seen.add("path    " + request.path());
            seen.add("q       " + request.query("q"));
            seen.add("tag     " + request.query("tag") + "  (the record keeps "
                    + request.query().get("tag") + ")");
            seen.add("accept  " + request.header("Accept"));
            seen.add("body    " + request.body());
            Response.ok("ok").writeTo(exchange);
        });
        server.start();

        String raw = "POST /notes?q=hot%20milk&tag=a&tag=b HTTP/1.1\r\n"
                + "Host: localhost\r\n"
                + "Accept: application/json\r\n"
                + "Content-Length: 8\r\n"
                + "Connection: close\r\n"
                + "\r\n"
                + "buy milk";
        call(server, raw);
        server.stop(0);

        for (String line : seen) {
            System.out.println(line);
        }
        System.out.println();
        System.out.println("one file read the exchange; everything above is a plain value");
    }

    static void call(HttpServer server, String raw) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(raw.getBytes(StandardCharsets.UTF_8));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
        }
    }
}

// ===== Requests.java =====

import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * The adapter. This is the only file in the service that knows about both an HttpExchange and a
 * Request, and it is deliberately the only one: nothing downstream can reach the socket.
 */
public final class Requests {
    private Requests() {}

    public static Request from(HttpExchange exchange) throws IOException {
        Map<String, String> headers = new LinkedHashMap<>();
        exchange.getRequestHeaders()
                .forEach((name, values) -> headers.put(name, String.join(", ", values)));
        return new Request(
                exchange.getRequestMethod(),
                exchange.getRequestURI().getPath(),
                Query.parse(exchange.getRequestURI().getRawQuery()),
                headers,
                new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8),
                Map.of());
    }
}

// ===== Query.java =====

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Query {
    private Query() {}

    /** A name with no `=` is present with an empty value; a repeated name keeps every value. */
    public static Map<String, List<String>> parse(String raw) {
        Map<String, List<String>> params = new LinkedHashMap<>();
        if (raw == null || raw.isEmpty()) {
            return params;
        }
        for (String pair : raw.split("&")) {
            int equals = pair.indexOf('=');
            String name = equals < 0 ? pair : pair.substring(0, equals);
            String value = equals < 0
                    ? ""
                    : URLDecoder.decode(pair.substring(equals + 1), StandardCharsets.UTF_8);
            params.computeIfAbsent(name, key -> new ArrayList<>()).add(value);
        }
        return params;
    }
}

// ===== Request.java =====

import java.util.List;
import java.util.Map;

/** Everything a handler is allowed to know about the request. No socket, no exchange. */
public record Request(String method, String path, Map<String, List<String>> query,
                      Map<String, String> headers, String body, Map<String, String> vars) {

    /** The shape a test or a demo uses, with no query, no headers and no path variables. */
    public Request(String method, String path, String body) {
        this(method, path, Map.of(), Map.of(), body, Map.of());
    }

    /** The same request, with the path variables the router pulled out of the pattern. */
    public Request withVars(Map<String, String> vars) {
        return new Request(method, path, query, headers, body, vars);
    }

    public String var(String name) {
        String value = vars.get(name);
        if (value == null) {
            throw new IllegalArgumentException("no path variable " + name + " on " + path);
        }
        return value;
    }

    public String header(String name) {
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            if (entry.getKey().equalsIgnoreCase(name)) {
                return entry.getValue();
            }
        }
        return null;
    }

    public String query(String name) {
        List<String> values = query.get(name);
        return values == null || values.isEmpty() ? null : values.get(0);
    }
}

// ===== Response.java =====

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/** A response as a value: nothing is written until something asks for the bytes. */
public record Response(int status, String contentType, String body) {

    static final String TEXT = "text/plain; charset=utf-8";

    public static Response text(int status, String body) {
        return new Response(status, TEXT, body);
    }

    public static Response ok(String body) {
        return text(200, body);
    }

    public static Response notFound(String path) {
        return text(404, "no route for " + path);
    }

    public static Response methodNotAllowed(String method, String allow) {
        return text(405, method + " is not allowed; try " + allow);
    }

    /** The length of the body as bytes, which is what the wire needs. */
    public int length() {
        return body.getBytes(StandardCharsets.UTF_8).length;
    }

    /** The one place that turns a response value into a framed HTTP response. */
    public void writeTo(com.sun.net.httpserver.HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", contentType);
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }
}
```

```text
method  POST
path    /notes
q       hot milk
tag     a  (the record keeps [a, b])
accept  application/json
body    buy milk

one file read the exchange; everything above is a plain value
```

`Requests.from(exchange)` is the only code in the service that names both `HttpExchange` and `Request`.
That is the whole design in one sentence: the socket is read in exactly one place, converted to a value,
and never mentioned again. Nothing downstream can reach the network, which means nothing downstream needs
a network to be tested.

The request above was sent as

```
POST /notes?q=hot%20milk&tag=a&tag=b
```

and the handler saw `q` as `hot milk` — decoded, because `%20` is a space — and `tag` as `a`, while the
record still holds `[a, b]`. Two rules are visible in that pair of lines:

- **A name is a map to a *list*.** `?tag=a&tag=b` is legal, common, and means both values. The record
  keeps the list; `query(name)` is a convenience that returns the first one. Know which of the two you
  are calling. Chapter 26's practice problem about `null` and `""` is the same warning from the other
  direction: a query string is not a map to a string.
- **Decoding happens once, at the edge.** The handler never sees `%20`, because `URLDecoder` ran in the
  adapter. If a handler decoded again, `a%2520b` would become a space when it should have stayed
  `a%20b` — the double-decoding bug, which is a security bug when the value is a path or a filename.

And the body arrives as a `String`. That is not free — the adapter reads the whole thing with
`readAllBytes()` before the handler runs — but it is *correct*, because Chapter 26 established that the
body must be read before the response is sent, and the adapter is the one place that can guarantee the
order. A streaming design would return a stream instead; this service returns a `String`, and that is a
size limit the chapter's practice questions come back to.

## The router, and the two probes that drive it

Everything so far has been types. Here is the router, and with it the complete library — five types and
the two probes that drive them. `RouteDemo` comes first and is what the run below prints; `ServiceDemo`
is the end-to-end probe the last section of this chapter runs, and it is in this listing because it is
the program that uses every one of these files.

```java run-files
// ===== RouteDemo.java =====

import java.util.Map;

public class RouteDemo {
    static Router router() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("every note"));
        router.get("/notes/{id}", request -> Response.ok("note " + request.var("id")));
        router.post("/notes", request -> Response.ok("created from '" + request.body() + "'"));
        router.delete("/notes/{id}", request -> Response.ok("deleted " + request.var("id")));
        return router;
    }

    record Call(String method, String path, String body) {}

    public static void main(String[] args) {
        Router router = router();
        System.out.println("routes: " + router.size());
        System.out.println();

        Call[] calls = {
            new Call("GET", "/notes", ""),
            new Call("GET", "/notes/7", ""),
            new Call("POST", "/notes", "milk"),
            new Call("DELETE", "/notes/7", ""),
            new Call("GET", "/notes/7/edit", ""),
            new Call("PUT", "/notes", ""),
            new Call("DELETE", "/notes", ""),
            new Call("GET", "/other", ""),
        };

        for (Call call : calls) {
            Request request = new Request(call.method(), call.path(), call.body());
            Response response = router.route(request);
            System.out.printf("%-7s %-16s -> %d  %s%n",
                    call.method(), call.path(), response.status(), response.body());
        }
        System.out.println();
        System.out.println("405 and 404 are different answers: PUT /notes found a route and rejected the method");
    }
}

// ===== ServiceDemo.java =====

import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class ServiceDemo {
    static List<String> notes = new ArrayList<>(List.of("groceries", "reading"));

    static Router routes() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok(String.join(", ", notes)));
        router.get("/notes/{id}", request -> {
            int id = Integer.parseInt(request.var("id"));
            return Response.ok(notes.get(id));
        });
        router.post("/notes", request -> {
            notes.add(request.body());
            return Response.text(201, "added " + request.body());
        });
        router.get("/boom", request -> {
            throw new IllegalStateException("the note store is on fire");
        });
        return router;
    }

    public static void main(String[] args) throws Exception {
        Router router = routes();
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            Response response;
            try {
                response = router.route(Requests.from(exchange));
            } catch (RuntimeException e) {
                response = Response.text(500, "the service failed: " + e.getMessage());
            }
            response.writeTo(exchange);
        });
        server.start();

        String[][] calls = {
            {"GET", "/notes", null},
            {"GET", "/notes/1", null},
            {"POST", "/notes", "buy milk"},
            {"GET", "/notes", null},
            {"PUT", "/notes", null},
            {"GET", "/nowhere", null},
            {"GET", "/boom", null},
        };

        for (String[] call : calls) {
            String response = call(server, call[0], call[1], call[2]);
            System.out.printf("%-6s %-12s -> %s%n", call[0], call[1], statusLine(response));
            System.out.println("        " + bodyOf(response));
        }
        server.stop(0);

        System.out.println();
        System.out.println("one handler threw and the client still got a complete 500 response");
    }

    static String call(HttpServer server, String method, String path, String body) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            StringBuilder request = new StringBuilder(method).append(' ').append(path)
                    .append(" HTTP/1.1\r\nHost: localhost\r\n");
            if (body != null) {
                request.append("Content-Length: ")
                        .append(body.getBytes(StandardCharsets.UTF_8).length).append("\r\n");
            }
            request.append("Connection: close\r\n\r\n");
            if (body != null) {
                request.append(body);
            }
            OutputStream out = socket.getOutputStream();
            out.write(request.toString().getBytes(StandardCharsets.UTF_8));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
            return bytes.toString(StandardCharsets.UTF_8);
        }
    }

    static String statusLine(String response) {
        return response.split("\r\n", 2)[0];
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "" : response.substring(end + 4).trim();
    }
}

// ===== Router.java =====

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Method plus path pattern to handler, with the two failure answers kept apart. */
public final class Router {
    public interface Handler {
        Response handle(Request request);
    }

    record Route(String method, String[] pattern, Handler handler) {}

    private final List<Route> routes = new ArrayList<>();

    public Router get(String pattern, Handler handler) {
        return add("GET", pattern, handler);
    }

    public Router post(String pattern, Handler handler) {
        return add("POST", pattern, handler);
    }

    public Router delete(String pattern, Handler handler) {
        return add("DELETE", pattern, handler);
    }

    private Router add(String method, String pattern, Handler handler) {
        routes.add(new Route(method, pattern.split("/"), handler));
        return this;
    }

    public int size() {
        return routes.size();
    }

    public Response route(Request request) {
        List<String> allowed = new ArrayList<>();
        for (Route route : routes) {
            Map<String, String> vars = match(route.pattern(), request.path());
            if (vars == null) {
                continue;
            }
            if (!route.method().equals(request.method())) {
                if (!allowed.contains(route.method())) {
                    allowed.add(route.method());
                }
                continue;
            }
            return route.handler().handle(request.withVars(vars));
        }
        if (!allowed.isEmpty()) {
            return Response.methodNotAllowed(request.method(), String.join(", ", allowed));
        }
        return Response.notFound(request.path());
    }

    /** The path variables, or null when the pattern does not match. */
    static Map<String, String> match(String[] pattern, String path) {
        String[] parts = path.split("/");
        if (parts.length != pattern.length) {
            return null;
        }
        Map<String, String> vars = new LinkedHashMap<>();
        for (int i = 0; i < pattern.length; i++) {
            if (pattern[i].startsWith("{")) {
                vars.put(pattern[i].substring(1, pattern[i].length() - 1), parts[i]);
            } else if (!pattern[i].equals(parts[i])) {
                return null;
            }
        }
        return vars;
    }
}

// ===== Request.java =====

import java.util.List;
import java.util.Map;

/** Everything a handler is allowed to know about the request. No socket, no exchange. */
public record Request(String method, String path, Map<String, List<String>> query,
                      Map<String, String> headers, String body, Map<String, String> vars) {

    /** The shape a test or a demo uses, with no query, no headers and no path variables. */
    public Request(String method, String path, String body) {
        this(method, path, Map.of(), Map.of(), body, Map.of());
    }

    /** The same request, with the path variables the router pulled out of the pattern. */
    public Request withVars(Map<String, String> vars) {
        return new Request(method, path, query, headers, body, vars);
    }

    public String var(String name) {
        String value = vars.get(name);
        if (value == null) {
            throw new IllegalArgumentException("no path variable " + name + " on " + path);
        }
        return value;
    }

    public String header(String name) {
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            if (entry.getKey().equalsIgnoreCase(name)) {
                return entry.getValue();
            }
        }
        return null;
    }

    public String query(String name) {
        List<String> values = query.get(name);
        return values == null || values.isEmpty() ? null : values.get(0);
    }
}

// ===== Response.java =====

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/** A response as a value: nothing is written until something asks for the bytes. */
public record Response(int status, String contentType, String body) {

    static final String TEXT = "text/plain; charset=utf-8";

    public static Response text(int status, String body) {
        return new Response(status, TEXT, body);
    }

    public static Response ok(String body) {
        return text(200, body);
    }

    public static Response notFound(String path) {
        return text(404, "no route for " + path);
    }

    public static Response methodNotAllowed(String method, String allow) {
        return text(405, method + " is not allowed; try " + allow);
    }

    /** The length of the body as bytes, which is what the wire needs. */
    public int length() {
        return body.getBytes(StandardCharsets.UTF_8).length;
    }

    /** The one place that turns a response value into a framed HTTP response. */
    public void writeTo(com.sun.net.httpserver.HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", contentType);
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }
}

// ===== Requests.java =====

import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * The adapter. This is the only file in the service that knows about both an HttpExchange and a
 * Request, and it is deliberately the only one: nothing downstream can reach the socket.
 */
public final class Requests {
    private Requests() {}

    public static Request from(HttpExchange exchange) throws IOException {
        Map<String, String> headers = new LinkedHashMap<>();
        exchange.getRequestHeaders()
                .forEach((name, values) -> headers.put(name, String.join(", ", values)));
        return new Request(
                exchange.getRequestMethod(),
                exchange.getRequestURI().getPath(),
                Query.parse(exchange.getRequestURI().getRawQuery()),
                headers,
                new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8),
                Map.of());
    }
}

// ===== Query.java =====

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Query {
    private Query() {}

    /** A name with no `=` is present with an empty value; a repeated name keeps every value. */
    public static Map<String, List<String>> parse(String raw) {
        Map<String, List<String>> params = new LinkedHashMap<>();
        if (raw == null || raw.isEmpty()) {
            return params;
        }
        for (String pair : raw.split("&")) {
            int equals = pair.indexOf('=');
            String name = equals < 0 ? pair : pair.substring(0, equals);
            String value = equals < 0
                    ? ""
                    : URLDecoder.decode(pair.substring(equals + 1), StandardCharsets.UTF_8);
            params.computeIfAbsent(name, key -> new ArrayList<>()).add(value);
        }
        return params;
    }
}
```

```text
routes: 4

GET     /notes           -> 200  every note
GET     /notes/7         -> 200  note 7
POST    /notes           -> 200  created from 'milk'
DELETE  /notes/7         -> 200  deleted 7
GET     /notes/7/edit    -> 404  no route for /notes/7/edit
PUT     /notes           -> 405  PUT is not allowed; try GET, POST
DELETE  /notes           -> 405  DELETE is not allowed; try GET, POST
GET     /other           -> 404  no route for /other

405 and 404 are different answers: PUT /notes found a route and rejected the method
```

The table has four routes and the eight calls above land on all of them plus both failure modes. Read the
last four lines carefully, because they are the reason this router is not three lines long:

```
PUT     /notes           -> 405  PUT is not allowed; try GET, POST
DELETE  /notes           -> 405  DELETE is not allowed; try GET, POST
GET     /notes/7/edit    -> 404  no route for /notes/7/edit
GET     /other           -> 404  no route for /other
```

`PUT /notes` and `GET /other` are both refusals, and they are not the same refusal. `/notes` **exists** —
there are two methods registered at that path — and `PUT` is not one of them. `/other` does not exist at
all. `405` says "this path means something, and you asked the wrong way". `404` says "this path means
nothing here". A client that gets `404` for `PUT /notes` will conclude the resource is missing, and may
try to create it, or report a broken link to a user. Neither is what happened.

So `route` cannot answer as soon as a pattern fails to match. It has to walk the **entire** table,
collecting the methods that did match the path, and only then decide:

- at least one method matched the path, but not this one → `405`, with the collected methods
- nothing matched the path at all → `404`

That is why the method is written with an accumulator and no early return. The list it builds is not
decoration either: it becomes the `Allow` header, which is what lets a client retry correctly instead of
guessing. The router hands the list to `Response.methodNotAllowed`, and the response carries it.

From here on the blocks are shell scripts. Each one drops a single driver into the project this listing
built and compiles it against the already-compiled `out/`, which is why no source above is printed twice.

## Registration order decides

```sh run-project
cat > Specificity.java <<'EOF'
import java.util.List;

public class Specificity {
    static Router idFirst() {
        Router router = new Router();
        router.get("/notes/{id}", request -> Response.ok("a note with id=" + request.var("id")));
        router.get("/notes/latest", request -> Response.ok("the latest note"));
        return router;
    }

    static Router literalFirst() {
        Router router = new Router();
        router.get("/notes/latest", request -> Response.ok("the latest note"));
        router.get("/notes/{id}", request -> Response.ok("a note with id=" + request.var("id")));
        return router;
    }

    public static void main(String[] args) {
        List<Router> routers = List.of(idFirst(), literalFirst());
        String[] labels = {"{id} registered first", "literal registered first"};

        for (int i = 0; i < routers.size(); i++) {
            System.out.println(labels[i] + ":");
            for (String path : List.of("/notes/7", "/notes/latest")) {
                Request request = new Request("GET", path, "");
                Response response = routers.get(i).route(request);
                System.out.printf("  %-16s -> %d  %s%n", path, response.status(), response.body());
            }
        }

        System.out.println();
        System.out.println("both patterns match /notes/latest, and the first one registered wins");
        System.out.println("so a literal path has to be registered before the variable that would swallow it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Specificity.java
java -cp out Specificity
```

```text
{id} registered first:
  /notes/7         -> 200  a note with id=7
  /notes/latest    -> 200  a note with id=latest
literal registered first:
  /notes/7         -> 200  a note with id=7
  /notes/latest    -> 200  the latest note

both patterns match /notes/latest, and the first one registered wins
so a literal path has to be registered before the variable that would swallow it
```

Both routers above contain the same two routes. They differ only in the order they were added, and the
second line of each block is a different answer:

```
{id} registered first:
  /notes/latest    -> 200  a note with id=latest
literal registered first:
  /notes/latest    -> 200  the latest note
```

`/notes/{id}` matches `/notes/latest` — `latest` is a perfectly good `id`. `/notes/latest` also matches
`/notes/latest`. Two routes match, so *something* has to break the tie, and this router breaks it by
registration order: **first match wins**.

That is a deliberate choice, and it is worth being explicit about what it buys and what it costs. It buys
predictability — the table is a list, it is read top to bottom, and there is no hidden scoring function to
learn. It costs an ordering obligation on whoever writes the table: a literal path must be registered
**before** the variable that would swallow it, and nothing in the router will tell you when you get it
wrong. The symptom is not an error; it is a handler that quietly never runs.

:::tip The order rule, stated once

Register the specific before the general. `/notes/latest` before `/notes/{id}`, `/notes/{id}/edit` before
`/notes/{id}`. If you find yourself wanting a scoring function, ask first whether the table can simply be
written in the right order.

:::

## What a thrown exception looks like from the client

```sh run-project
cat > Errors.java <<'EOF'
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Errors {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/uncaught", exchange -> {
            throw new IllegalStateException("nobody caught this");
        });
        server.createContext("/caught", exchange -> {
            Response response;
            try {
                throw new IllegalStateException("somebody caught this");
            } catch (RuntimeException e) {
                response = Response.text(500, "the service failed: " + e.getMessage());
            }
            response.writeTo(exchange);
        });
        server.start();

        for (String path : new String[] {"/uncaught", "/caught"}) {
            String response = call(server, path);
            System.out.println("GET " + path + " ->");
            if (response.isEmpty()) {
                System.out.println("  the client received nothing at all");
            } else {
                System.out.println("  " + response.split("\r\n", 2)[0]);
                System.out.println("  " + bodyOf(response));
            }
        }
        server.stop(0);

        System.out.println();
        System.out.println("an uncaught handler exception closes the connection with no response");
        System.out.println("the catch-all in the dispatcher is the only thing that can turn it into a 500");
    }

    static String call(HttpServer server, String path) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(("GET " + path + " HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                    .getBytes(StandardCharsets.US_ASCII));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
            return bytes.toString(StandardCharsets.UTF_8);
        }
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "(no body)" : response.substring(end + 4).trim();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Errors.java
java -cp out Errors
```

```text
GET /uncaught ->
  the client received nothing at all
GET /caught ->
  HTTP/1.1 500 Internal Server Error
  the service failed: somebody caught this

an uncaught handler exception closes the connection with no response
the catch-all in the dispatcher is the only thing that can turn it into a 500
```

A handler that throws is not a handler that returns `500`. Those are two different events, and the
measurement is blunt about the difference:

```
GET /uncaught ->
  the client received nothing at all
GET /caught ->
  HTTP/1.1 500 Internal Server Error
  the service failed: somebody caught this
```

The first handler threw and the connection closed with no response at all. Not a `500` — nothing. The
client is left holding a half-open socket and an unanswered request. The second handler caught its own
exception and produced a complete response.

So the catch-all in the dispatcher is not defensive programming; it is the only thing that can turn an
unexpected failure into an answer. Without it, every bug in every handler becomes a dropped connection,
and a dropped connection is the hardest kind of failure to diagnose: the server's log and the client's
error do not agree on what happened, because the client never heard anything.

## The whole service, end to end

`ServiceDemo.java` — the last file in the listing above — is the whole service in one program, and this
is what it prints:

```sh run-project
java -cp out ServiceDemo
```

```text
GET    /notes       -> HTTP/1.1 200 OK
        groceries, reading
GET    /notes/1     -> HTTP/1.1 200 OK
        reading
POST   /notes       -> HTTP/1.1 201 Created
        added buy milk
GET    /notes       -> HTTP/1.1 200 OK
        groceries, reading, buy milk
PUT    /notes       -> HTTP/1.1 405 Method Not Allowed
        PUT is not allowed; try GET, POST
GET    /nowhere     -> HTTP/1.1 404 Not Found
        no route for /nowhere
GET    /boom        -> HTTP/1.1 500 Internal Server Error
        the service failed: the note store is on fire

one handler threw and the client still got a complete 500 response
```

The dispatcher it drives is three statements inside one context:

```java
server.createContext("/", exchange -> {
    Response response;
    try {
        response = router.route(Requests.from(exchange));
    } catch (RuntimeException e) {
        response = Response.text(500, "the service failed: " + e.getMessage());
    }
    response.writeTo(exchange);
});
```

Adapt, route, write. One context, registered at `/`, so that no path can reach Chapter 26's built-in HTML
404 — every request lands here and gets a `Response` in the service's own format.

The run makes seven calls and every one of them got a complete response: two reads, a `POST` that changed
the state (note that the third `GET` sees `buy milk`, so the handler really did mutate the list), a
`405`, a `404`, and a `500` from a handler that threw. That is the payoff. The failure modes are all
still failures, but they are now *answers*, and every one of them came from the same three lines.

:::scenario The router that answered 404 for a path it knew

A colleague writes the router the obvious way — search the table for the pair `(method, path)` and return
`404` when the pair is not there:

```java
for (Pair pair : PAIRS) {
    if (pair.method().equals(method) && match(pair.pattern().split("/"), path) != null) {
        return Response.ok("handled");
    }
}
return Response.notFound(path);
```

The table has `GET /notes`, `POST /notes` and `DELETE /notes/{id}`. A client sends `DELETE /notes`.

What does it receive, what will it conclude, and what does the correct router answer instead?

:::solution
```sh run-project
cat > Scenario.java <<'EOF'
import java.util.List;

public class Scenario {
    record Pair(String method, String pattern) {}

    static final List<Pair> PAIRS = List.of(
            new Pair("GET", "/notes"),
            new Pair("POST", "/notes"),
            new Pair("DELETE", "/notes/{id}"));

    /** The version that looks for the pair (method, path) and gives up when it is not there. */
    static Response naiveRoute(String method, String path) {
        for (Pair pair : PAIRS) {
            if (pair.method().equals(method)
                    && Router.match(pair.pattern().split("/"), path) != null) {
                return Response.ok("handled");
            }
        }
        return Response.notFound(path);
    }

    static Router realRouter() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("handled"));
        router.post("/notes", request -> Response.ok("handled"));
        router.delete("/notes/{id}", request -> Response.ok("handled"));
        return router;
    }

    public static void main(String[] args) {
        Router router = realRouter();

        for (String method : List.of("GET", "DELETE")) {
            String path = "/notes";
            Response naive = naiveRoute(method, path);
            Response real = router.route(new Request(method, path, ""));
            System.out.printf("%-7s %-10s naive -> %d  %s%n", method, path, naive.status(), naive.body());
            System.out.printf("%-7s %-10s real  -> %d  %s%n", method, path, real.status(), real.body());
        }

        System.out.println();
        System.out.println("the naive router collapsed two different failures into one answer");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
GET     /notes     naive -> 200  handled
GET     /notes     real  -> 200  handled
DELETE  /notes     naive -> 404  no route for /notes
DELETE  /notes     real  -> 405  DELETE is not allowed; try GET, POST

the naive router collapsed two different failures into one answer
```

The naive router answers `404  no route for /notes`. The correct one answers
`405  DELETE is not allowed; try GET, POST`.

The path `/notes` is in the table twice. The naive router compares the **pair**, so a method that is
absent makes the pair absent, and a missing pair is indistinguishable from a missing path. It collapses
two different failures into one answer — and it collapses them in the direction that lies, because the
`404` says the resource does not exist when the resource is right there with two methods on it.

The consequences are concrete. A client that gets `404` on a `DELETE` may reasonably decide the item is
already gone and report success to the user. An API explorer will mark the endpoint as nonexistent and
stop offering it. A retry loop will keep retrying, because `404` reads like a routing mistake rather than
a method mistake.

The real router scans the whole table and accumulates the methods that matched the path. It only reaches
`405` after the scan, and the accumulator becomes the `Allow` header — so the client is not merely told
"no", it is told `try GET, POST`, which is a fact it can act on. That is the difference between a refusal
and a dead end.
:::
:::

## Solutions

### 1. A 405 has to say what is allowed

The status code says the method was refused. It does not say which methods would have worked, and without
that the client is guessing. `Allow` is the header that carries the answer.

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Sol1 {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            exchange.getResponseHeaders().set("Allow", "GET, POST");
            byte[] body = "PUT is not allowed; try GET, POST".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(405, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.print(show(headOf(get(server, "/notes"))));
        server.stop(0);

        System.out.println();
        System.out.println("Allow is not decoration: a client that reads it can retry correctly");
        System.out.println("without it, 405 says only that the request was refused");
    }

    static String get(HttpServer server, String path) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(("PUT " + path + " HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                    .getBytes(StandardCharsets.US_ASCII));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
            return bytes.toString(StandardCharsets.UTF_8);
        }
    }

    static String headOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(0, end + 4);
    }

    static String show(String text) {
        if (text.endsWith("\r\n")) {
            text = text.substring(0, text.length() - 2);
        }
        StringBuilder out = new StringBuilder();
        for (String line : text.split("\r\n", -1)) {
            if (line.startsWith("Date:")) {
                line = "Date: <masked>";
            }
            out.append(line.isEmpty() ? "|" : "| " + line).append('\n');
        }
        return out.toString();
    }
}
```

```text
| HTTP/1.1 405 Method Not Allowed
| Date: <masked>
| Allow: GET, POST
| Content-length: 33
|

Allow is not decoration: a client that reads it can retry correctly
without it, 405 says only that the request was refused
```

The head shows the whole story: `405`, then `Allow: GET, POST`, then a body the service wrote itself.
Compare this with Chapter 26's built-in 404 — `Content-Type: text/html`, `<h1>404 Not Found</h1>` — and
the difference is the same in both cases. A response the service wrote is a response the service
controls, and the parts a client actually reads are the ones you chose.

Note the casing: `Content-length`, not `Content-Length`, and `Allow` exactly as set. Chapter 26 measured
that the JDK re-cases header names on the way out; the `Allow` you set is the `Allow` the client sees
only because it happened to already be in that case. Header names are case-insensitive, so this is legal
— but a client that does a string comparison against `"Allow"` is relying on the JDK's casing, not on
the protocol.

### 2. A route that exists and an id that is wrong are not the same failure

The first `405`-versus-`404` split was about the method. This is the same discipline applied one level
down, to the value inside the path.

```sh run-project
cat > Sol2.java <<'EOF'
import java.util.List;

public class Sol2 {
    static Router routes() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("every note"));
        router.get("/notes/{id}", request -> {
            String raw = request.var("id");
            try {
                return Response.ok("note " + Integer.parseInt(raw));
            } catch (NumberFormatException e) {
                return Response.text(400, "'" + raw + "' is not an id");
            }
        });
        return router;
    }

    public static void main(String[] args) {
        Router router = routes();
        for (String path : List.of("/notes", "/notes/7", "/notes/seven", "/notes/7/edit", "/other")) {
            Response response = router.route(new Request("GET", path, ""));
            System.out.printf("%-16s -> %d  %s%n", path, response.status(), response.body());
        }
        System.out.println();
        System.out.println("three different answers: 200 found it, 400 the id is malformed, 404 no such route");
        System.out.println("a route that exists and an id that is wrong are not the same failure");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
/notes           -> 200  every note
/notes/7         -> 200  note 7
/notes/seven     -> 400  'seven' is not an id
/notes/7/edit    -> 404  no route for /notes/7/edit
/other           -> 404  no route for /other

three different answers: 200 found it, 400 the id is malformed, 404 no such route
a route that exists and an id that is wrong are not the same failure
```

Five paths, four outcomes, and each one is a different sentence:

- `/notes` → `200`, the collection
- `/notes/7` → `200`, the item, because `7` parses
- `/notes/seven` → `400`, because the route matched and the *argument* is malformed
- `/notes/7/edit` → `404`, because no pattern has three segments after the root
- `/other` → `404`, because no pattern starts with `other`

The `400` is the one that gets skipped in a hurry. `Integer.parseInt` throws `NumberFormatException`, and
the lazy version lets it escape — which, per the previous section, means the client receives nothing at
all. Catching it and returning `400` costs three lines and turns a dropped connection into a sentence the
client can act on. `400` is also the honest code: the request is syntactically fine and the *value* is
not acceptable, which is exactly what `400 Bad Request` means.

### 3. A path matches exactly, segment for segment

What counts as the same path is a question with a surprising answer, so it is worth measuring rather than
assuming.

```sh run-project
cat > Sol3.java <<'EOF'
import java.util.List;

public class Sol3 {
    public static void main(String[] args) {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("every note"));

        for (String path : List.of("/notes", "/notes/", "//notes", "/NOTES", "/notes/ ")) {
            Response response = router.route(new Request("GET", path, ""));
            System.out.printf("%-12s -> %d  '%s'%n", "'" + path + "'", response.status(),
                    response.body());
        }

        System.out.println();
        System.out.println("'/notes/' matched, because split() drops a trailing empty segment");
        System.out.println("'//notes' did not, because only the trailing one is dropped");
        System.out.println("and matching is case-sensitive, so '/NOTES' is a different path");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
'/notes'     -> 200  'every note'
'/notes/'    -> 200  'every note'
'//notes'    -> 404  'no route for //notes'
'/NOTES'     -> 404  'no route for /NOTES'
'/notes/ '   -> 404  'no route for /notes/ '

'/notes/' matched, because split() drops a trailing empty segment
'//notes' did not, because only the trailing one is dropped
and matching is case-sensitive, so '/NOTES' is a different path
```

`'/notes/'` matched. That is not the rule anyone writes down — it is an accident of `String.split`, which
**discards trailing empty segments**. `"/notes/".split("/")` is `["", "notes"]`, not
`["", "notes", ""]`, so it produces the same two segments as `/notes` and the two paths are
indistinguishable to this router.

`'//notes'` did not match, and the reason is the same call: `["", "", "notes"]` has three segments, and
only the *trailing* empties are dropped. So the trailing-slash tolerance is not a rule you designed, it
is a side effect you inherited — and it is the kind of side effect that should be written down, because
the day someone "fixes" the split the behaviour changes silently.

The other two lines are not accidents. `'/NOTES'` is a different path because matching is case-sensitive,
and `'/notes/ '` is a different path because a space is a character like any other — it is not padding to
be trimmed. A client that sends either one gets a `404`, and the `404` is correct.

### 4. The `Allow` list comes from the same table

`405` needs an `Allow` list. `OPTIONS` needs an `Allow` list. It would be easy to write the list twice —
once in the router and once in an `OPTIONS` handler — and it would be wrong the first time a route is
added.

```sh run-project
cat > Sol4.java <<'EOF'
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Sol4 {
    record Route(String method, String[] pattern) {}

    static final List<Route> ROUTES = List.of(
            new Route("GET", "/notes".split("/")),
            new Route("POST", "/notes".split("/")),
            new Route("GET", "/notes/{id}".split("/")),
            new Route("DELETE", "/notes/{id}".split("/")));

    /** Every method that would be accepted at this path, in registration order. */
    static List<String> methodsFor(String path) {
        Map<String, Boolean> seen = new LinkedHashMap<>();
        for (Route route : ROUTES) {
            if (Router.match(route.pattern(), path) != null) {
                seen.putIfAbsent(route.method(), Boolean.TRUE);
            }
        }
        return new ArrayList<>(seen.keySet());
    }

    public static void main(String[] args) {
        for (String path : new String[] {"/notes", "/notes/7", "/other"}) {
            List<String> methods = methodsFor(path);
            System.out.printf("%-12s -> %s%n", path,
                    methods.isEmpty() ? "(no methods; a 404)" : String.join(", ", methods));
        }
        System.out.println();
        System.out.println("this is what an Allow header is made of, and what OPTIONS would answer");
        System.out.println("it comes from the same table the router already has, so it cannot go stale");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
/notes       -> GET, POST
/notes/7     -> GET, DELETE
/other       -> (no methods; a 404)

this is what an Allow header is made of, and what OPTIONS would answer
it comes from the same table the router already has, so it cannot go stale
```

The list is computed by running every route's pattern against the path and collecting the methods that
matched, which is the *same* test the router performs, on the *same* table. So it cannot go stale: add a
`PATCH` route and both `405` and `OPTIONS` report it, with no second list to remember.

`match` is `static` for exactly this reason. The router needs it, and so does any code that wants to ask
"which methods are allowed here" without performing a route — which is what `OPTIONS` is for. Making it
package-private and static keeps one implementation of the matching rule and lets the answer be computed
from outside the router.

## Key takeaways

- A handler should decide **what the answer is**; something else decides how an answer becomes bytes. A
  handler containing `\r\n`, a `byte[]` or `Content-Type` has mixed the two jobs.
- `Request` and `Response` are **records**, so they are immutable: a router can attach path variables
  without any risk of a handler mutating another request's data.
- A missing path variable **throws** rather than returning `null`, so the bug is reported where it was
  made — in the pattern — instead of two frames later as a `NullPointerException`.
- `header(name)` is **case-insensitive**, because header names are. Chapter 25 measured it on the wire;
  this implements it once.
- `Response.length()` counts **bytes**, not characters. `"héllo"` is 5 characters and 6 bytes, and the
  header must promise 6.
- `writeTo` converts the body to a `byte[]` **once** and uses that one array for the header and the
  write, so the two numbers cannot disagree. One writer, or the guarantee is gone.
- `Requests.from` is the **only** file that names both `HttpExchange` and `Request`. Nothing downstream
  can reach the network, so nothing downstream needs a network to be tested.
- A query string is a map to a **list**. `query(name)` returns the first value; the record keeps them all.
  Decode once, at the edge — double-decoding turns `%2520` into a space and is a security bug.
- `404` and `405` are different answers. `404` says the path means nothing; `405` says the path exists and
  the method is wrong, and it carries `Allow` so the client can retry correctly.
- Answering `405` requires scanning the **whole** table first, because `Allow` is built from the routes
  that matched the path. An early return cannot produce it.
- The router is **first match wins**. A literal must be registered before the variable that would swallow
  it, and getting the order wrong fails silently — a handler that never runs.
- An uncaught handler exception gives the client **nothing at all**, not a `500`. The dispatcher's
  catch-all is the only thing that turns a bug into an answer.
- `String.split("/")` discards **trailing** empty segments, so `/notes/` and `/notes` are the same route
  by accident, while `//notes` is not.

## Practice

- [ ] Add a `PATCH /notes/{id}` route and make `Allow` report it. What has to change — the table, the
      matching rule, or both?
- [ ] `Requests.from` reads the body with `readAllBytes()`. What does that cost for a 100 MB upload, and
      what would you change if the service had to accept one?
- [ ] `query(name)` returns the *first* value for a repeated name. Write a version that returns the last,
      and explain why "first" is the conventional choice.
- [ ] `Requests.from` joins multi-valued headers with `", "`. Why is that correct for `Accept` and wrong
      for `Set-Cookie`?
- [ ] The router returns `405` with an `Allow` list. What should `OPTIONS` return, and how much of that
      can be computed from the same table?
- [ ] `Response.writeTo` takes an `HttpExchange`. What would it take to make it write to an
      `OutputStream` instead, and what would that buy you?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Only the table. Add `router.patch(pattern, handler)` as a one-line wrapper around `add`, register the
   route, and both `405` and `OPTIONS` report it — because `Allow` is computed by scanning the table, not
   by a second list. The matching rule does not change at all: `match` compares segments and treats
   `{...}` as a variable, and it has no idea which method it is serving. That is the payoff of keeping
   the method out of the matcher.
2. `readAllBytes()` holds the whole body in memory, and it holds it as a `String`, which for UTF-8 is
   roughly the byte count again. A 100 MB upload becomes 100 MB of byte array plus a `String`, and
   several concurrent uploads become an out-of-memory error. The fix is to stop returning a `String`:
   give `Request` a body that is either a `byte[]` for small bodies or an `InputStream` the handler
   consumes, and decide the limit by the route. Note that the eager read is *deliberate* for the ordinary
   case — Chapter 26 established that the body must be read before the response is sent, and doing it in
   the adapter makes that impossible to get wrong. The change is to bound it, not to remove it.
3. The last value is `values.get(values.size() - 1)`, or a `LinkedHashMap` overwrite if you do not need
   the earlier ones. "First" is conventional because a query string is a *list* in order, and a client
   that sends `?tag=a&tag=b` has expressed a preference that reads left to right — the same convention as
   `Accept`, where the first media type is the preferred one. Both are defensible; what matters is that
   the choice is documented, because a caller cannot tell the difference from the outside.
4. Because HTTP defines a comma-separated list as the meaning of a repeated header for *most* headers, so
   `Accept: text/html, application/json` and two `Accept` lines mean the same thing. `Set-Cookie` is the
   famous exception: a cookie value may itself contain a comma — `Expires=Wed, 21 Oct 2026 07:28:00 GMT`
   is a single value with a comma in it — so joining two cookies with `", "` produces one unparseable
   header. Chapter 26 measured the rule from the other side: `set` replaces and `add` appends, and two
   cookies need two `Set-Cookie` headers. The general lesson is that "join with a comma" is a decision
   per header, not a default.
5. `OPTIONS` should return `204 No Content` with an `Allow` header listing the methods for that path —
   and `204` means no body, which per Chapter 26 means a negative length, not `0`. All of the list comes
   from the same scan: run every route's pattern against the path and collect the methods that matched,
   exactly as `Allow` is built for `405`. The one thing that cannot come from that scan is whether the
   *path itself* exists, so an `OPTIONS` for a path with no routes should be a `404` — the same rule as
   `route`, applied without a method.
6. `writeTo` needs to stop naming `HttpExchange` and take an `OutputStream` plus a way to say the status
   and the content type — in practice a small `Head` record, or just the two values as arguments. What it
   buys is that the writer no longer depends on the JDK server: it can write into a `ByteArrayOutputStream`
   in a test, or into a file, and the framing can be asserted without a socket. That is the same trade
   this chapter made one level up, applied to the last file that still touched the framework. The cost is
   that the caller now has to remember to call `sendResponseHeaders`, so the split only pays if a thin
   adapter does it once.
