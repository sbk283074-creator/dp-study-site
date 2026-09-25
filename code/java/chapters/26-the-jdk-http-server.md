---
chapter: 26
part: 4
title: The JDK HTTP Server
summary: Use the HTTP server that ships with the JDK -- see which of Chapter 25's decisions it makes for you, which it leaves to you, and the three ways to say how long a body is.
minutes: 65
tags: [http, httpserver, handlers, executors, routing, security]
---

Chapter 25 read HTTP off a socket and found three decisions in every message: where the head ends,
where the body ends, and what the status code means. This chapter uses the server that ships with the
JDK — `com.sun.net.httpserver` — and the interesting question is not what it does but **which of those
decisions it takes away from you**. That set is smaller than most people expect, and knowing its
boundary is what makes the rest of this Part possible without a framework.

There is no dependency to add. `com.sun.net.httpserver` is a module in the JDK, so it compiles and
runs with exactly the flags every other chapter has used.

## The smallest server that works

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Minimal {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            byte[] body = "hello from HttpServer".getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write("GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                    .getBytes(StandardCharsets.US_ASCII));
            out.flush();
            String response = readToEnd(socket.getInputStream());
            System.out.print(show(response));
        } finally {
            server.stop(0);
        }
    }

    static String readToEnd(InputStream in) throws Exception {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        in.transferTo(bytes);
        return bytes.toString(StandardCharsets.UTF_8);
    }

    /** Prints the response with the CRLF structure visible, and masks the clock. */
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
| HTTP/1.1 200 OK
| Date: <masked>
| Content-type: text/plain; charset=utf-8
| Content-length: 21
|
| hello from HttpServer
```

That is the whole server: a listener, a context, a handler. Compare it with Chapter 25's
`ServerSocket` version and the split is clear.

**The server wrote for you:** the status line, the `Date` header, and the `Content-length`. It also
read the request head, split the request line, parsed every header, and handed the handler an object.
There is no `\r\n` anywhere in that code, and no byte counting.

**It did not write for you:** the content type (you set that), the body, and — this is the part that
matters — anything at all about what a path *means*. A context is a path prefix and a handler. There is
no router, no JSON, no templating, no sessions, no static files, no logging. Everything this Part adds
from here is a decision the JDK deliberately left open.

Note the header names the server sent: `Content-type` and `Content-length`, not `Content-Type` and
`Content-Length`. The JDK re-cases names on the way out. That is legal — Chapter 25 measured that
header names are case-insensitive — and it is the first of several places where this server's choices
are visible only if you look at the bytes.

## The three ways to say how long the body is

`sendResponseHeaders(int code, long length)` is the method that writes the status line and the headers,
and its second argument is doing more than it looks like it is:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class Lengths {
    static final String BODY = "hello, world";

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/exact", exchange -> {
            exchange.sendResponseHeaders(200, BODY.length());
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(BODY.getBytes(StandardCharsets.UTF_8));
            }
        });
        server.createContext("/unknown", exchange -> {
            exchange.sendResponseHeaders(200, 0);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(BODY.getBytes(StandardCharsets.UTF_8));
            }
        });
        server.createContext("/none", exchange -> {
            exchange.sendResponseHeaders(204, -1);
            exchange.close();
        });
        server.start();

        for (String path : List.of("/exact", "/unknown", "/none")) {
            System.out.println(path + " ->");
            System.out.print(show(headOf(get(server, path))));
            System.out.println();
        }
        server.stop(0);

        System.out.println("12 is the body, 0 asked for chunked, -1 said there is no body at all");
    }

    static String get(HttpServer server, String path) throws Exception {
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

    /** Everything up to and including the blank line that ends the head. */
    static String headOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(0, end + 4);
    }

    /** Renders CRLF visibly, and masks the clock the server adds. */
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
/exact ->
| HTTP/1.1 200 OK
| Date: <masked>
| Content-length: 12
|

/unknown ->
| HTTP/1.1 200 OK
| Date: <masked>
| Transfer-encoding: chunked
|

/none ->
| HTTP/1.1 204 No Content
| Date: <masked>
|

12 is the body, 0 asked for chunked, -1 said there is no body at all
```

Three calls, three different protocols:

- **`length` greater than zero** — that many bytes follow, and the response carries
  `Content-length: 12`. This is the one to use whenever you know the size.
- **`length` exactly zero** — the size is *not* known, so the server switches to
  `Transfer-encoding: chunked` and writes no `Content-length` at all. The body is a series of
  sized chunks, ending with a zero-sized one.
- **`length` less than zero** — there is no body, and the server omits `Content-length` entirely. With
  `204 No Content` that is exactly right.

The trap is the middle one, and it is a trap because `0` reads like "an empty body". It means the
opposite: an unknown-length body, framed the expensive way. An empty response is `-1`; a response whose
length you know is that length. Writing `sendResponseHeaders(200, 0)` and then a body gets you chunked
encoding, which is correct but not what you meant — and it is one of the few places where a wrong
number still produces a working response, which is why it survives testing.

:::warning
`204 No Content` and `304 Not Modified` must not have a body, and the JDK will let you try. If you call
`sendResponseHeaders(204, 5)` and write five bytes, the framing is wrong in a way a client cannot
recover from: the five bytes become the start of the next response on a keep-alive connection. Use
`-1` for both, and let the status code say what happened.
:::

## What the handler is handed

A handler receives an `HttpExchange`, and everything Chapter 25 did by hand is already done:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class Introspect {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/notes", exchange -> {
            String body = new String(exchange.getRequestBody().readAllBytes(),
                    StandardCharsets.UTF_8);
            String report = line("method", exchange.getRequestMethod())
                    + line("path", exchange.getRequestURI().getPath())
                    + line("rawQuery", String.valueOf(exchange.getRequestURI().getRawQuery()))
                    + line("Host", header(exchange, "Host"))
                    + line("Content-Type", header(exchange, "Content-Type"))
                    + line("X-Note", header(exchange, "x-note"))
                    + line("body", "'" + body + "' (" + body.length() + " character(s))");
            byte[] bytes = report.getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(bytes);
            }
        });
        server.start();

        System.out.print(bodyOf(post(server)));
        server.stop(0);

        System.out.println();
        System.out.println("the handler was handed a parsed request: no framing, no socket, no CRLF");
        System.out.println("header lookup ignores case, so 'x-note' found 'X-Note'");
    }

    static String line(String label, String value) {
        return String.format("%-13s%s%n", label, value);
    }

    static String header(com.sun.net.httpserver.HttpExchange exchange, String name) {
        List<String> values = exchange.getRequestHeaders().get(name);
        return values == null ? "(absent)" : String.join(", ", values);
    }

    static String post(HttpServer server) throws Exception {
        String body = "remember the milk";
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(("POST /notes?tag=work HTTP/1.1\r\n"
                    + "Host: localhost\r\n"
                    + "Content-Type: text/plain; charset=utf-8\r\n"
                    + "X-Note: kept\r\n"
                    + "Content-Length: " + body.length() + "\r\n"
                    + "Connection: close\r\n"
                    + "\r\n"
                    + body).getBytes(StandardCharsets.US_ASCII));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
            return bytes.toString(StandardCharsets.UTF_8);
        }
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(end + 4);
    }
}
```

```text
method       POST
path         /notes
rawQuery     tag=work
Host         localhost
Content-Type text/plain; charset=utf-8
X-Note       kept
body         'remember the milk' (17 character(s))

the handler was handed a parsed request: no framing, no socket, no CRLF
header lookup ignores case, so 'x-note' found 'X-Note'
```

The method, the path, the raw query, the headers and the body — all parsed. `getRequestURI()` returns a
`java.net.URI`, which means every measurement from Chapter 25 applies directly: `getPath()` is decoded
and `getRawPath()` is not, and `getRawQuery()` returns `null` when there is no query. The escaping trap
does not go away because a framework is holding the string.

Two things about the body are worth naming.

`getRequestBody()` returns an `InputStream`, and `readAllBytes()` reads it into memory. For a note
service that is the right call — a note body is small and you want the whole thing before you parse it.
For an upload endpoint it is the wrong call, because the memory you use is the size of the request, and
the client controls the size. Chapter 34 comes back to that with a limit.

And the body must be read **before** the response is sent. On a keep-alive connection, unread request
bytes are still in the socket when the next request arrives, and the server will read them as the
beginning of the next request line. That is the same failure as Chapter 25's short response, seen from
the other side.

:::tip
`header(exchange, "x-note")` found a header the client sent as `X-Note`. That is Chapter 25's
case-insensitivity rule being enforced *for* you by the server's header map, and it is worth relying on
rather than reimplementing — a lookup helper that lowercases the name and then looks in a case-sensitive
map is a bug that only appears when a client's casing differs from your test's.
:::

## Contexts are path prefixes, matched by segment

`createContext(path, handler)` is the entire routing mechanism, and it has exactly two rules:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class Contexts {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/notes", exchange -> {
            byte[] body = ("the /notes handler saw "
                    + exchange.getRequestURI().getPath()).getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.createContext("/", exchange -> {
            byte[] body = "the / handler".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        for (String path : List.of("/notes", "/notes/7", "/notes/7/edit", "/noteworthy", "/other")) {
            String response = get(server, path);
            System.out.printf("%-16s %-24s %s%n", path, statusLine(response), bodyOf(response));
        }
        server.stop(0);

        System.out.println();
        System.out.println("/noteworthy is not /notes: a match stops at a path boundary");
        System.out.println("and where two contexts both match, the longest one wins");
    }

    static String get(HttpServer server, String path) throws Exception {
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

    static String statusLine(String response) {
        return response.split("\r\n", 2)[0];
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "" : response.substring(end + 4).trim();
    }
}
```

```text
/notes           HTTP/1.1 200 OK          the /notes handler saw /notes
/notes/7         HTTP/1.1 200 OK          the /notes handler saw /notes/7
/notes/7/edit    HTTP/1.1 200 OK          the /notes handler saw /notes/7/edit
/noteworthy      HTTP/1.1 200 OK          the / handler
/other           HTTP/1.1 200 OK          the / handler

/noteworthy is not /notes: a match stops at a path boundary
and where two contexts both match, the longest one wins
```

**A context matches whole path segments.** `/notes` matched `/notes`, `/notes/7` and `/notes/7/edit`,
because each of those begins with the segment `notes`. It did **not** match `/noteworthy`, even though
`/noteworthy` starts with the five characters `/note`. The match is on segments, so `notes` and
`noteworthy` are different words and not a prefix and a continuation.

**Where two contexts both match, the longest one wins.** `/notes/7` matched both `/notes` and `/`; the
handler that ran was `/notes`. That is the rule that lets a root context exist as a catch-all without
shadowing everything else.

Which makes the root context the design decision to make consciously. Registering `/` gives you a
handler that sees every request the more specific contexts did not take, and *not* registering it hands
those requests to the server — which brings us to the next section.

## An unmatched path is answered by the server, not by you

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class NotFound {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/notes", exchange -> {
            byte[] body = "a note".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.createContext("/missing", exchange -> {
            byte[] body = "no such note".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(404, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        for (String path : List.of("/notes", "/missing", "/no-such-context")) {
            System.out.println("GET " + path + " ->");
            System.out.print(show(get(server, path)));
            System.out.println();
        }
        server.stop(0);

        System.out.println("the third response was written by the server, not by any handler");
    }

    static String get(HttpServer server, String path) throws Exception {
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
GET /notes ->
| HTTP/1.1 200 OK
| Date: <masked>
| Content-length: 6
|
| a note

GET /missing ->
| HTTP/1.1 404 Not Found
| Date: <masked>
| Content-length: 12
|
| no such note

GET /no-such-context ->
| HTTP/1.1 404 Not Found
| Content-Length: 50
| Content-Type: text/html
| Connection: close
|
| <h1>404 Not Found</h1>No context found for request

the third response was written by the server, not by any handler
```

Three requests, and the third one is the interesting one. `/notes` and `/missing` were answered by
handlers, which set their own content type and their own status. `/no-such-context` was answered by
**the server itself**, and look at how different its response is:

- `Content-Length` — capital `L`, where every handler-written response said `Content-length`.
- `Content-Type: text/html` — and a body that is HTML, `<h1>404 Not Found</h1>No context found for
  request`.
- `Connection: close`, and **no `Date` header at all**.

So a service that registers only its own paths has two different 404 responses with two different
content types, and a client that asked for JSON gets a fragment of HTML. That is not a bug in the JDK;
it is the JDK declining to guess what your service's error format is. The repair is to register `/`
and return your own 404 in your own format, which is what Solution 1's router is for.

## One thread, unless you say otherwise

The last thing the server leaves to you is the most consequential, and it is a one-line omission with a
measurable effect. `HttpServer` uses an executor, and the default executor is **the single thread that
accepts connections**:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Threads {
    public static void main(String[] args) throws Exception {
        System.out.println("no executor set:");
        System.out.println("  " + measure(false));
        System.out.println();
        System.out.println("a fixed pool of two:");
        System.out.println("  " + measure(true));
        System.out.println();
        System.out.println("the default executor is one thread, and the documentation leaves that to you");
    }

    /** Fires two requests at once and reports what the handlers actually observed. */
    static String measure(boolean pooled) throws Exception {
        Set<String> threads = ConcurrentHashMap.newKeySet();
        CountDownLatch bothArrived = new CountDownLatch(2);
        int[] sawBoth = {0};

        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            threads.add(Thread.currentThread().getName());
            bothArrived.countDown();
            try {
                if (bothArrived.await(3, TimeUnit.SECONDS)) {
                    sawBoth[0]++;
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            byte[] body = "ok".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });

        ExecutorService pool = null;
        if (pooled) {
            pool = Executors.newFixedThreadPool(2);
            server.setExecutor(pool);
        }
        server.start();

        Thread first = new Thread(() -> quietlyGet(server));
        Thread second = new Thread(() -> quietlyGet(server));
        first.start();
        second.start();
        first.join();
        second.join();
        server.stop(0);
        if (pool != null) {
            pool.shutdown();
        }

        return threads.size() + " thread(s) answered; handler(s) that saw both requests in flight: "
                + sawBoth[0];
    }

    static void quietlyGet(HttpServer server) {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write("GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                    .getBytes(StandardCharsets.US_ASCII));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

```text
no executor set:
  1 thread(s) answered; handler(s) that saw both requests in flight: 1

a fixed pool of two:
  2 thread(s) answered; handler(s) that saw both requests in flight: 2

the default executor is one thread, and the documentation leaves that to you
```

Both runs fire two requests at the same moment, and both count two things: how many distinct threads
answered, and how many handlers saw *both* requests in flight before either replied.

With no executor set, **one** thread answered both requests, and only one handler ever saw both in
flight — because the second request could not even be accepted until the first handler returned. The
accept loop and the handler are the same thread, so a handler that waits is a server that stops
accepting. A handler that waits for *another request* — a lock, a cache warm-up, a call to the same
service — deadlocks a single-threaded server permanently.

With a fixed pool of two, two threads answered, and both handlers saw both requests in flight. The
accept loop was free to accept the second connection while the first handler was still running.

`server.setExecutor(Executors.newFixedThreadPool(4))` is the fix, and there are two details in it worth
noticing now because Chapter 30 is about them. The pool's threads are non-daemon by default, so the JVM
will not exit while the pool is alive — the block above calls `pool.shutdown()` for that reason. And
"four threads" is a *bound* on concurrency, not a guarantee of it; it says how many handlers may run at
once, and nothing about how quickly they finish.

:::scenario The response that declared 100 bytes and wrote 14

A handler is written in two steps that look independent:

```java
exchange.sendResponseHeaders(200, 100);
try (OutputStream out = exchange.getResponseBody()) {
    out.write("only fourteen!".getBytes(StandardCharsets.UTF_8));
}
```

The number 100 is a placeholder that was never replaced, and the body is fourteen bytes.

:::solution
The JDK does catch it — this is not one of the silent failures Chapter 25 measured:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Scenario {
    static final String BODY = "only fourteen!";
    static volatile String failure = "(the handler did not fail)";

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/short", exchange -> {
            exchange.sendResponseHeaders(200, 100);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(BODY.getBytes(StandardCharsets.UTF_8));
            } catch (IOException e) {
                failure = e.getClass().getName() + ": " + e.getMessage();
                throw e;
            }
        });
        server.createContext("/report", exchange -> {
            byte[] body = failure.getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.println("the handler declared 100 byte(s) and wrote " + BODY.length());
        System.out.println();
        String response = get(server, "/short");
        System.out.println("what the client received:");
        System.out.print(show(headOf(response)));
        System.out.println("  ...then " + bodyLength(response) + " byte(s) of body, with 100 promised");
        System.out.println();
        System.out.println("what the handler caught:");
        System.out.println("  " + bodyOf(get(server, "/report")));
        server.stop(0);
    }

    static int bodyLength(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? 0 : response.length() - (end + 4);
    }

    static String get(HttpServer server, String path) throws Exception {
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

    static String headOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(0, end + 4);
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "" : response.substring(end + 4).trim();
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
the handler declared 100 byte(s) and wrote 14

what the client received:
| HTTP/1.1 200 OK
| Date: <masked>
| Content-length: 100
|
  ...then 14 byte(s) of body, with 100 promised

what the handler caught:
  java.io.IOException: insufficient bytes written to stream
```

The client received `HTTP/1.1 200 OK` with `Content-length: 100`, and then fourteen bytes. The handler
caught `java.io.IOException: insufficient bytes written to stream`, thrown when the response body was
closed with eighty-six bytes still owed.

The exception is better than silence, and it arrives **too late**. By the time it is thrown the status
line and the headers are already on the wire; a status code cannot be revised. The client is now
waiting for eighty-six bytes that will never arrive, and on a keep-alive connection those bytes would
be the next response's status line. So the handler's exception is a *log* entry, not a recovery — and
the repair has to be upstream of the response, which is Chapter 25's rule restated: derive the length
from the same byte array that produces the body.

There is one more thing to take from the shape of this bug. The two numbers were written on two
different lines, and nothing tied them together. `sendResponseHeaders(200, 100)` followed by a write is
the pattern to avoid; the pattern to want is a single value — a byte array, or a small record holding
the status, the content type and the bytes — that the writer consumes. Then there is no second number
to get wrong.
:::
:::

## Solutions

### 1. Routing is a pure function

Chapter 25's lesson was that a request is data. Here is the routing decision as data too, with no
server anywhere:

```java run
public class Sol1 {
    record Response(int status, String contentType, String body) {
        static Response text(String body) {
            return new Response(200, "text/plain; charset=utf-8", body);
        }

        static Response notFound(String path) {
            return new Response(404, "text/plain; charset=utf-8", "no such path: " + path);
        }
    }

    static Response route(String method, String path) {
        if (!method.equals("GET")) {
            return new Response(405, "text/plain; charset=utf-8", method + " is not allowed here");
        }
        if (path.startsWith("/notes/")) {
            return Response.text("note " + path.substring("/notes/".length()));
        }
        return switch (path) {
            case "/" -> Response.text("bulletin");
            case "/health" -> Response.text("ok");
            default -> Response.notFound(path);
        };
    }

    public static void main(String[] args) {
        String[][] requests = {
            {"GET", "/"},
            {"GET", "/health"},
            {"GET", "/notes/7"},
            {"POST", "/notes/7"},
            {"GET", "/other"},
        };

        for (String[] request : requests) {
            Response response = route(request[0], request[1]);
            System.out.printf("%-6s %-12s -> %d  %s%n",
                    request[0], request[1], response.status(), response.body());
        }
        System.out.println();
        System.out.println("route is a pure function of (method, path): no socket, no server, no port");
        System.out.println("that is what makes the routing table testable on its own");
    }
}
```

```text
GET    /            -> 200  bulletin
GET    /health      -> 200  ok
GET    /notes/7     -> 200  note 7
POST   /notes/7     -> 405  POST is not allowed here
GET    /other       -> 404  no such path: /other

route is a pure function of (method, path): no socket, no server, no port
that is what makes the routing table testable on its own
```

`route` takes a method and a path and returns a `Response`. There is no socket, no port, no server, no
thread — and therefore no flakiness, no timeout and no teardown. Every routing rule the service has is
visible in one function and testable in one loop.

Look at what the switch expresses. `405` is produced when the method is wrong, before the path is even
considered, because "this path exists but not for that method" is a different answer from "no such
path". `/notes/` is handled by a `startsWith` **outside** the switch, because it is a family of paths
rather than a fixed one. And the `default` arm returns the service's own 404 with its own content type —
which is the repair for the previous section, expressed as one line.

The server-side version of this is three lines: a context, a call to `route`, and a call to
`sendResponseHeaders` with the length of `response.body()`. **The router does not need to know it is on
a network**, and that separation is the difference between a service whose rules are testable and one
whose rules can only be exercised by making requests.

### 2. The query string is a map to a list

`getRawQuery()` gives you the raw text after the `?`, and it is still raw — no splitting, no decoding,
and `null` when there is nothing after the `?`:

```java run
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Sol2 {
    static Map<String, List<String>> parse(String raw) {
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

    public static void main(String[] args) {
        String[] queries = {
            null,
            "",
            "tag=work",
            "tag=a&tag=b",
            "q=",
            "flag",
            "q=hello+world&q=a%20b",
        };

        for (String query : queries) {
            System.out.printf("%-24s -> %s%n",
                    query == null ? "(no query at all)" : "'" + query + "'", render(parse(query)));
        }
        System.out.println();
        System.out.println("null and \"\" both give an empty map, and that is the first decision");
        System.out.println("'flag' has no equals sign: present, with an empty value, not absent");
        System.out.println("a repeated name keeps both values, in the order they were written");
    }

    /** Quotes every value, so an empty one is visible rather than an empty pair of brackets. */
    static String render(Map<String, List<String>> params) {
        StringBuilder out = new StringBuilder("{");
        params.forEach((name, values) -> {
            if (out.length() > 1) {
                out.append(", ");
            }
            out.append(name).append("=[");
            for (int i = 0; i < values.size(); i++) {
                out.append(i == 0 ? "" : ", ").append('\'').append(values.get(i)).append('\'');
            }
            out.append(']');
        });
        return out.append('}').toString();
    }
}
```

```text
(no query at all)        -> {}
''                       -> {}
'tag=work'               -> {tag=['work']}
'tag=a&tag=b'            -> {tag=['a', 'b']}
'q='                     -> {q=['']}
'flag'                   -> {flag=['']}
'q=hello+world&q=a%20b'  -> {q=['hello world', 'a b']}

null and "" both give an empty map, and that is the first decision
'flag' has no equals sign: present, with an empty value, not absent
a repeated name keeps both values, in the order they were written
```

Four decisions are packed into that small function, and each one is a decision because the spec does not
make it for you.

`null` and the empty string both produce an empty map. They are different inputs — one means there was
no `?` at all — and collapsing them is a choice, made here because every caller would otherwise have to
test for both.

A name with no `=` is **present with an empty value**, not absent. `?flag` and `?flag=` produce the same
map, and `flag` is a key in both. That matters for a filter: "the caller asked for the flag" and "the
caller did not mention the flag" are different intentions and a map that cannot tell them apart cannot
serve them.

A repeated name keeps every value, in the order written, which is why the type is a map to a list.
`?tag=a&tag=b` most naturally means "either tag" — a union — and a `Map<String, String>` would silently
keep only `b`.

And the values are decoded with `URLDecoder`, which is the right tool *here* and the wrong tool for a
path: it turns `+` into a space, which is correct in a query string and wrong in a path segment. Chapter
25 measured both spellings; this is where the measurement becomes a line of code.

### 3. The length argument wins over a header

Here is a small experiment with a surprising outcome. Set `Content-Length` by hand, then tell
`sendResponseHeaders` a different number:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Sol3 {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
            exchange.getResponseHeaders().set("Cache-Control", "no-store");
            exchange.getResponseHeaders().set("Content-Length", "999");
            byte[] body = "{\"ok\":true}".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.print(show(headOf(get(server, "/"))));
        server.stop(0);

        System.out.println();
        System.out.println("Content-Length was set to 999 and the response says 11");
        System.out.println("the argument to sendResponseHeaders is the length; a header cannot override it");
        System.out.println("the server also re-cased Content-Type to Content-type, which is legal");
    }

    static String get(HttpServer server, String path) throws Exception {
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
| HTTP/1.1 200 OK
| Date: <masked>
| Content-type: application/json; charset=utf-8
| Content-length: 11
| Cache-control: no-store
|

Content-Length was set to 999 and the response says 11
the argument to sendResponseHeaders is the length; a header cannot override it
the server also re-cased Content-Type to Content-type, which is legal
```

The response says `Content-length: 11`, which is the length of the JSON body. The `999` that was set on
the header map is simply gone.

That is the right behaviour and the reason for it is the design of the API: the length is an argument
to `sendResponseHeaders` precisely so that it cannot drift from the body. A header map is for headers
whose value *is* the value you set — `Content-Type`, `Cache-Control`, `Location`. A header the server
must compute to keep the framing consistent is not yours to set, and the API takes it away from you.

The same experiment also shows the re-casing again: `Content-Type` went out as `Content-type`. If you
have ever wondered whether header names are really case-insensitive, this server normalises them on
every response, and every client that works with it is proof.

### 4. `set` replaces, `add` appends

A response header map is the same shape as a request header map — a name to a list — and the API gives
you two methods that differ only in which of those they do:

```java run
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Sol4 {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            exchange.getResponseHeaders().set("X-Tag", "first");
            exchange.getResponseHeaders().set("X-Tag", "second");
            exchange.getResponseHeaders().set("Set-Cookie", "a=1");
            exchange.getResponseHeaders().add("Set-Cookie", "b=2");
            byte[] body = "ok".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.print(show(headOf(get(server, "/"))));
        server.stop(0);

        System.out.println();
        System.out.println("set replaced 'first' with 'second'; add appended a second Set-Cookie");
        System.out.println("the server re-cased Set-Cookie to Set-cookie on the way out, which is legal");
        System.out.println("a response header map is a map to a list, exactly as on the way in");
    }

    static String get(HttpServer server, String path) throws Exception {
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
| HTTP/1.1 200 OK
| X-tag: second
| Date: <masked>
| Content-length: 2
| Set-cookie: a=1
| Set-cookie: b=2
|

set replaced 'first' with 'second'; add appended a second Set-Cookie
the server re-cased Set-Cookie to Set-cookie on the way out, which is legal
a response header map is a map to a list, exactly as on the way in
```

`set("X-Tag", "first")` followed by `set("X-Tag", "second")` left one header with the value `second`.
`set("Set-Cookie", "a=1")` followed by `add("Set-Cookie", "b=2")` left **two** `Set-cookie` headers, in
the order written.

The distinction is exactly Chapter 25's "a name may appear more than once", and it is the reason
cookies work at all: a response that sets two cookies must send two `Set-Cookie` headers, because a
single comma-separated header is not equivalent — cookie values are allowed to contain commas. Using
`set` for the second cookie silently drops the first, and the user's session disappears with it.

Notice too that the names went out as `Set-cookie` and `X-tag`. Same normalisation as before, and the
same conclusion: the wire spelling of a header name is not something to depend on in either direction.

## Key takeaways

- `com.sun.net.httpserver` is a **JDK module**: no dependency, and it compiles with the same flags as
  every other chapter.
- The server writes the status line, `Date`, `Content-length` and the framing. It does **not** write your
  content type, your body, or any opinion about what a path means.
- `sendResponseHeaders(code, length)`: **positive** = exactly that many bytes, **zero** = unknown length
  and chunked encoding, **negative** = no body. `0` does not mean "empty".
- `204` and `304` must have no body. Use a negative length, or the body poisons the next response on a
  keep-alive connection.
- A handler gets a parsed request — method, `URI`, headers, body stream. The `URI` rules from Chapter 25
  still apply: `getPath()` is decoded, `getRawPath()` is not, `getRawQuery()` may be `null`.
- Read the request body **before** sending the response, or its unread bytes are the next request's
  first line.
- A context matches **whole path segments** — `/notes` does not match `/noteworthy` — and the longest
  matching context wins.
- An unmatched path is answered by the **server**, with `Content-Type: text/html`, different header
  casing and no `Date`. Register `/` and return your own 404 in your own format.
- The default executor is the accepting thread. **One thread, one request at a time**, and a handler
  that waits stops the server accepting.
- `setExecutor` with a pool is the fix; the pool's threads are non-daemon, so shut it down or the JVM
  will not exit.
- Routing is a pure function of `(method, path)` returning a response value. Keep it out of the handler
  and it needs no server to test.
- A query string is a map to a **list**; a name with no `=` is present with an empty value; `null` and
  `""` are different inputs and only you can decide whether they mean the same thing.
- `Content-Length` is an argument to `sendResponseHeaders`, not a header you set — and if you set one
  anyway, the argument wins.
- `set` replaces, `add` appends. Two cookies need two `Set-Cookie` headers.

## Practice

- [ ] Register only `/notes` and request `/notes/7/edit`. Add a handler that pulls `7` out of the path.
      Where does that parsing belong — in the handler, or in the router from Solution 1?
- [ ] Make every response in the service go through one method that takes the `Response` record and
      writes it. What does that buy you for the 404 case, and what does it cost?
- [ ] Register `/` so nothing reaches the built-in 404, then prove with a raw client that the service
      never returns HTML.
- [ ] Change `Threads` to use a pool of four and re-measure. Which number changes, which does not, and
      why?
- [ ] Read `getRequestBody()` twice in one handler and report what the second read returns. Then explain
      why that is the same rule as "read the body before responding".
- [ ] Send a request with `Expect: 100-continue` and see what the server does with it. Which of the five
      status-code families is `100`, and what is the client supposed to do next?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The parsing belongs in the router, for the same reason `route` takes a `String` path rather than an
   `HttpExchange`: the moment a handler starts slicing paths it needs a request to be tested, and the
   rule "the third segment after `/notes/` is the id" becomes a fact that only exists inside a running
   server. Have `route` return either a `Response` or a value describing which handler and which
   argument, and the server-side code stays three lines.
2. Every response goes through one writer, which means the status line, the content type and the length
   are decided in **one** place — and the length comes from the byte array, so the scenario above cannot
   happen. The 404 case is the payoff: the built-in HTML 404 disappears entirely, because there is no
   path left that does not reach the writer. The cost is a little indirection: a handler can no longer
   stream a large body, because it has to produce the whole thing first. That is a real trade and it is
   the right one for small JSON responses.
3. Register `/` and return a 404 in the service's format. Prove it with a raw `Socket` rather than a
   client library, because the claim is about bytes: read the head, assert the status is `404`, assert
   the content type is the service's, and assert no `<h1>` appears anywhere in the body. A library would
   hide exactly the difference you are testing for.
4. The distinct-thread count changes only if there are more concurrent requests than the pool has
   threads; with two requests, a pool of two and a pool of four both answer on two threads. What does
   *not* change is the number of handlers that saw both requests in flight — it stays at two, because
   the constraint was never the pool size but whether the accept loop was free. The lesson is that a
   pool bounds concurrency without creating it.
5. The second read returns `-1`, immediately — the stream is at its end, and `-1` is the same value it
   would return for an empty body, which is why a double read is silent rather than an error. It is the
   same rule as reading before responding: the body is a stream with a position, it is consumed once,
   and any code that assumes otherwise is relying on a body it cannot see. If you need the bytes twice,
   read them once into a byte array.
6. `Expect: 100-continue` asks the server to send an interim `100 Continue` before the client commits to
   uploading the body, so that a request which is going to be rejected can be rejected without the
   upload. `100` is the **informational** family — the request was received and processing continues —
   and the client's next move is to send the body it was holding back. The reason it exists is worth
   carrying: a body can be expensive to send, and a protocol that lets the receiver say "don't bother"
   before the cost is paid is a protocol designed by people who had paid it.
