---
chapter: 25
part: 4
title: How the Web Works
summary: Read a real HTTP exchange off a socket and see that the web is text over TCP -- status codes, headers, the blank line that ends the head, and the header that says where the body ends.
minutes: 60
tags: [http, tcp, sockets, status codes, headers, uri, security]
---

Part III built a program that a person drives from a terminal. Part IV builds a service that other
programs drive over a network, and it is called **Bulletin**: a small web service where notes can be
posted and read. Everything in it is built from the JDK, with no third-party jars, and the first step
is to be clear about what is actually going over the wire — because every framework you will ever meet
is a set of decisions about those bytes, and a decision you cannot see is a decision you cannot debug.

So this chapter does not use a framework. It uses `ServerSocket`, `Socket` and the `\r\n` character,
and it prints the bytes.

## A request is text, and you can read it

Here is a complete HTTP exchange: a server on an ephemeral port, a client that sends a request, and
both sides printing exactly what they saw.

```java run
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class RawExchange {
    static final String REQUEST =
            "GET /notes HTTP/1.1\r\n"
            + "Host: localhost\r\n"
            + "Accept: text/plain\r\n"
            + "\r\n";

    static final String RESPONSE =
            "HTTP/1.1 200 OK\r\n"
            + "Content-Type: text/plain; charset=utf-8\r\n"
            + "Content-Length: 12\r\n"
            + "Connection: close\r\n"
            + "\r\n"
            + "hello, world";

    public static void main(String[] args) throws Exception {
        String[] serverSaw = new String[1];

        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    serverSaw[0] = readHead(socket.getInputStream());
                    OutputStream out = socket.getOutputStream();
                    out.write(RESPONSE.getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                } catch (IOException e) {
                    throw new java.io.UncheckedIOException(e);
                }
            });
            server.start();

            String clientSaw;
            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                OutputStream out = socket.getOutputStream();
                out.write(REQUEST.getBytes(StandardCharsets.US_ASCII));
                out.flush();
                clientSaw = readToEnd(socket.getInputStream());
            }
            server.join();

            System.out.println("-- what the server read, byte for byte --");
            System.out.print(show(serverSaw[0]));
            System.out.println();
            System.out.println("-- what the client read, byte for byte --");
            System.out.print(show(clientSaw));
        }
    }

    /** Reads up to and including the blank line that ends the request head. */
    static String readHead(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        int state = 0;
        int b;
        while (state != 4 && (b = in.read()) != -1) {
            bytes.write(b);
            state = switch (state) {
                case 0 -> b == '\r' ? 1 : 0;
                case 1 -> b == '\n' ? 2 : (b == '\r' ? 1 : 0);
                case 2 -> b == '\r' ? 3 : 0;
                default -> b == '\n' ? 4 : 0;
            };
        }
        return bytes.toString(StandardCharsets.US_ASCII);
    }

    /** Reads until the other end closes -- the only signal HTTP/1.0 had. */
    static String readToEnd(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        in.transferTo(bytes);
        return bytes.toString(StandardCharsets.US_ASCII);
    }

    /** Makes the line structure visible instead of letting CRLF act on the terminal. */
    static String show(String text) {
        if (text.endsWith("\r\n")) {
            text = text.substring(0, text.length() - 2);
        }
        StringBuilder out = new StringBuilder();
        for (String line : text.split("\r\n", -1)) {
            out.append(line.isEmpty() ? "|" : "| " + line).append('\n');
        }
        return out.toString();
    }
}
```

```text
-- what the server read, byte for byte --
| GET /notes HTTP/1.1
| Host: localhost
| Accept: text/plain
|

-- what the client read, byte for byte --
| HTTP/1.1 200 OK
| Content-Type: text/plain; charset=utf-8
| Content-Length: 12
| Connection: close
|
| hello, world
```

Read the first block carefully, because it is the whole protocol. The server received **three lines
and then an empty one**. That empty line is the end of the request — it is the only marker in the
message. There is no length prefix, no type tag, no framing beyond `\r\n\r\n`.

The client received a status line, three headers, an empty line, and then twelve bytes of body. The
body is `hello, world` and the header says `Content-Length: 12`. Nothing else needed to be said.

Two details in that code are worth understanding rather than copying.

`readHead` is a four-state machine that reads **one byte at a time** and stops when it has seen
`\r\n\r\n`. Byte-at-a-time looks wasteful and it is deliberate: you cannot ask a stream for "the next
line" without already knowing where the line ends, and — more importantly — you must not read *past*
the blank line, because the body starts immediately after it. A `BufferedReader.readLine()` here would
over-read into the body and you would never get those bytes back.

And the response is a string literal that I typed. That is the point of the block: the server side of
HTTP is text you write. There is no serialization, no schema, no code generation. If you want to send
a header, you write its name, a colon, its value and `\r\n`.

## TCP gives you a byte stream, and nothing else

The reason HTTP has to work this hard is that the layer under it does almost nothing. TCP delivers
**an ordered stream of bytes** and promises that nothing is lost, nothing is reordered and nothing is
duplicated. It promises nothing else. In particular it does not give you messages: if the sender
writes 500 bytes in three calls, the reader may receive them in one, two, three or seventeen chunks.

So framing is HTTP's job, and there are exactly three ways a body can end:

- `Content-Length: n` — exactly `n` bytes follow.
- `Transfer-Encoding: chunked` — the body is a series of sized chunks, ending with a zero-sized one.
- The connection closes — the HTTP/1.0 default, and the only option when the length is not known.

Which means the first thing to understand about a failing HTTP client is that it is usually waiting for
one of those three signals and not getting it.

The failure that is easiest to diagnose is the one where nothing is listening:

```java run
import java.net.ConnectException;
import java.net.ServerSocket;
import java.net.Socket;

public class ConnectRefused {
    public static void main(String[] args) throws Exception {
        int closedPort;
        try (ServerSocket probe = new ServerSocket(0)) {
            closedPort = probe.getLocalPort();
        }

        try (Socket socket = new Socket("127.0.0.1", closedPort)) {
            System.out.println("connected=" + socket.isConnected() + ", which cannot happen");
        } catch (ConnectException e) {
            System.out.println("the port was bound, then closed, then dialled again");
            System.out.println("ConnectException: " + e.getMessage());
            System.out.println("the address is not in the message, which is why this is stable");
        }
    }
}
```

```text
the port was bound, then closed, then dialled again
ConnectException: Connection refused
the address is not in the message, which is why this is stable
```

`Connection refused` is a *fast* failure: the operating system answered the connect attempt with a
reset. Notice that the address is not in the message, which is why a test can assert on it — and
notice how different the other two failure modes are. A connection that is accepted and then goes
silent gives you no error at all until you time out; a connection that closes cleanly looks exactly
like a finished response. **Refused is the only one of the three that tells you what happened**, and
that is why a service that is down is easier to debug than a service that is slow.

## Status codes: the first digit is the contract

Every response begins with a three-digit code and a reason phrase, and the reason phrase is for humans
— the code is what a client switches on. The code's **first digit** is its family, and the family is
what tells a client what to do next:

```java run
public class StatusCodes {
    record Status(int code, String reason) {}

    static String family(int code) {
        return switch (code / 100) {
            case 1 -> "informational";
            case 2 -> "success";
            case 3 -> "redirect";
            case 4 -> "client error";
            case 5 -> "server error";
            default -> "not a status code";
        };
    }

    public static void main(String[] args) {
        Status[] table = {
            new Status(200, "OK"),
            new Status(201, "Created"),
            new Status(204, "No Content"),
            new Status(301, "Moved Permanently"),
            new Status(304, "Not Modified"),
            new Status(400, "Bad Request"),
            new Status(401, "Unauthorized"),
            new Status(404, "Not Found"),
            new Status(405, "Method Not Allowed"),
            new Status(500, "Internal Server Error"),
            new Status(503, "Service Unavailable"),
        };

        System.out.printf("%-5s %-22s %s%n", "code", "reason", "family");
        for (Status status : table) {
            System.out.printf("%-5d %-22s %s%n",
                    status.code(), status.reason(), family(status.code()));
        }
        System.out.println();
        System.out.println("the first digit is the family, and the family is what a client acts on");
    }
}
```

```text
code  reason                 family
200   OK                     success
201   Created                success
204   No Content             success
301   Moved Permanently      redirect
304   Not Modified           redirect
400   Bad Request            client error
401   Unauthorized           client error
404   Not Found              client error
405   Method Not Allowed     client error
500   Internal Server Error  server error
503   Service Unavailable    server error

the first digit is the family, and the family is what a client acts on
```

The reason phrase is decoration. `404` and `Not Found` carry the same information, and a client must
never parse the phrase: a server is allowed to write anything there, in any language. What a client
acts on is the number, and the number's first digit narrows it to one of five behaviours:

- **`1xx` informational** — the request was received and processing continues. You will rarely write
  one by hand; `101 Switching Protocols` is the one you will meet, in websockets.
- **`2xx` success** — it worked. `200` carries a body; `201 Created` says something now exists, and
  usually comes with a `Location` header naming it; `204 No Content` says it worked and there is
  deliberately no body.
- **`3xx` redirect** — the client should look somewhere else. `301` and `302` come with a `Location`
  header; `304 Not Modified` means "use the copy you already have", which is how caching works and is
  the reason a `304` must not carry a body.
- **`4xx` client error** — the request was wrong. `400` is malformed, `401` is "you have not
  identified yourself", `403` is "you have, and you may not", `404` is "no such thing", `405` is "that
  method is not allowed here".
- **`5xx` server error** — the request was fine and *your* code failed. `500` is the catch-all;
  `503 Service Unavailable` means try again later.

The `4xx`/`5xx` split is not cosmetic — it is the difference between "do not retry, the request is
wrong" and "retrying might work". A service that returns `500` for a bad client request will be
retried by every well-behaved client, forever.

:::warning
`204` and `304` are the two statuses that must not have a body, and they are also the two that most
often get one by accident, because the code that writes the body does not know which status was
chosen. If a response has `Content-Length: 0` and a body, the client reads zero bytes and then treats
the body as the beginning of the *next* response on a keep-alive connection. That is how one bad
response poisons a connection.
:::

## Headers are a case-insensitive multimap

A header is a name, a colon and a value, one per line, and the collection has three properties that
each cost somebody a bug:

```java run
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class Headers {
    static final String BLOCK =
            "Content-Type: text/plain; charset=utf-8\r\n"
            + "content-length: 12\r\n"
            + "Set-Cookie: a=1\r\n"
            + "Set-Cookie: b=2\r\n"
            + "Location: http://example.com/notes?page=2\r\n"
            + "X-Note:   padded   \r\n";

    public static void main(String[] args) {
        Map<String, List<String>> headers = new LinkedHashMap<>();
        for (String line : BLOCK.split("\r\n", -1)) {
            if (line.isEmpty()) {
                continue;
            }
            int colon = line.indexOf(':');
            String name = line.substring(0, colon).toLowerCase(Locale.ROOT);
            String value = line.substring(colon + 1).trim();
            headers.computeIfAbsent(name, key -> new ArrayList<>()).add(value);
        }

        for (Map.Entry<String, List<String>> entry : headers.entrySet()) {
            System.out.printf("%-15s %s%n", entry.getKey(), entry.getValue());
        }
        System.out.println();
        System.out.println("Content-Type and content-length became one key: names are case-insensitive");
        System.out.println("a name may appear twice, so a value is a list and never a String");
        System.out.println("Location's value contains a colon, so the split must be on the first one");
    }
}
```

```text
content-type    [text/plain; charset=utf-8]
content-length  [12]
set-cookie      [a=1, b=2]
location        [http://example.com/notes?page=2]
x-note          [padded]

Content-Type and content-length became one key: names are case-insensitive
a name may appear twice, so a value is a list and never a String
Location's value contains a colon, so the split must be on the first one
```

**Names are case-insensitive and values are not.** `Content-Type` and `content-length` became the same
key in the table, which is correct: a client may send `content-length` in any casing and a server must
treat it identically. The *value* is not case-insensitive, and neither is it trimmed beyond the
optional whitespace around it — `X-Note:   padded   ` became `padded`, and that is the only trimming
that is allowed.

**A name may appear more than once.** `Set-Cookie` did, and both values are there, in order. This is
why a header map cannot be `Map<String, String>`: the moment a response sets two cookies, the second
one silently overwrites the first. The type has to be a map to a **list**, and that is a decision to
make before you write the parser, not after.

**The split is on the first colon, not the last.** `Location`'s value is
`http://example.com/notes?page=2`, which contains a colon of its own. Splitting on the last colon gives
you the name `Location: http` and a value that is not a URL at all.

## Methods, and which ones you may retry

The request line's first word is the method, and methods are not interchangeable. They differ along two
axes, and the second one is the one that decides whether a network failure is recoverable:

```java run
public class Methods {
    record Method(String name, boolean safe, boolean idempotent, boolean typicalBody) {}

    public static void main(String[] args) {
        Method[] methods = {
            new Method("GET", true, true, false),
            new Method("HEAD", true, true, false),
            new Method("PUT", false, true, true),
            new Method("DELETE", false, true, false),
            new Method("POST", false, false, true),
            new Method("PATCH", false, false, true),
        };

        System.out.printf("%-8s %-7s %-12s %s%n", "method", "safe", "idempotent", "request body");
        for (Method method : methods) {
            System.out.printf("%-8s %-7b %-12b %b%n", method.name(), method.safe(),
                    method.idempotent(), method.typicalBody());
        }
        System.out.println();
        System.out.println("safe: no side effects. idempotent: doing it twice has the same effect as once");
        System.out.println("POST is neither, and that is why a browser asks before resending one");
    }
}
```

```text
method   safe    idempotent   request body
GET      true    true         false
HEAD     true    true         false
PUT      false   true         true
DELETE   false   true         false
POST     false   false        true
PATCH    false   false        true

safe: no side effects. idempotent: doing it twice has the same effect as once
POST is neither, and that is why a browser asks before resending one
```

**Safe** means the method has no side effects: a client may issue it freely, a crawler may follow it,
and a cache may serve a stored answer. **Idempotent** means issuing it twice has the same effect as
issuing it once — not that it is side-effect-free, but that repeating it does not change the outcome.

`PUT` is the interesting row: it is not safe, because it writes, and it *is* idempotent, because
writing the same value twice leaves the same value. `DELETE` is the same shape: deleting a note that
is already deleted leaves it deleted.

`POST` is neither, and that is why it is the method that gets the special treatment. If a request
times out, a client cannot know whether the server processed it — so a well-behaved client does not
resend a `POST` on its own, and a browser asks the user before doing it. That is not politeness; it is
the only correct behaviour, and it follows directly from `POST` being neither safe nor idempotent.

## The header that says where the body ends

`Content-Length` deserves its own section because it is the header that makes keep-alive possible, and
because getting it wrong produces two failures that look nothing like each other.

```java run
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;

public class ContentLength {
    static final String BODY = "hello, world";

    static final String HEAD =
            "HTTP/1.1 200 OK\r\n"
            + "Content-Type: text/plain; charset=utf-8\r\n"
            + "Content-Length: " + BODY.length() + "\r\n"
            + "\r\n";

    public static void main(String[] args) throws Exception {
        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    readHead(socket.getInputStream());
                    OutputStream out = socket.getOutputStream();
                    out.write((HEAD + BODY).getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                    Thread.sleep(1200);
                } catch (IOException | InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
            server.start();

            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();
                out.write("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
                        .getBytes(StandardCharsets.US_ASCII));
                out.flush();

                String head = readHead(in);
                int declared = Integer.parseInt(
                        head.lines().filter(l -> l.toLowerCase().startsWith("content-length:"))
                                .findFirst().orElseThrow().split(":")[1].trim());

                byte[] body = in.readNBytes(declared);
                System.out.println("Content-Length says " + declared + " byte(s)");
                System.out.println("readNBytes(" + declared + ") returned " + body.length
                        + " byte(s): " + new String(body, StandardCharsets.US_ASCII));

                socket.setSoTimeout(300);
                try {
                    int extra = in.read();
                    System.out.println("one more read returned " + extra);
                } catch (SocketTimeoutException e) {
                    System.out.println("one more read blocked for 300 ms: SocketTimeoutException");
                }
            }
            server.join();
            System.out.println();
            System.out.println("the connection was still open: Content-Length ends the body, not the close");
        }
    }

    static String readHead(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        int state = 0;
        int b;
        while (state != 4 && (b = in.read()) != -1) {
            bytes.write(b);
            state = switch (state) {
                case 0 -> b == '\r' ? 1 : 0;
                case 1 -> b == '\n' ? 2 : (b == '\r' ? 1 : 0);
                case 2 -> b == '\r' ? 3 : 0;
                default -> b == '\n' ? 4 : 0;
            };
        }
        return bytes.toString(StandardCharsets.US_ASCII);
    }
}
```

```text
Content-Length says 12 byte(s)
readNBytes(12) returned 12 byte(s): hello, world
one more read blocked for 300 ms: SocketTimeoutException

the connection was still open: Content-Length ends the body, not the close
```

The client read exactly twelve bytes because the header said twelve, and then tried to read one more
byte with a 300 millisecond timeout. It **timed out**, which proves the connection was still open. The
server had written its response and was sleeping; it had not closed anything.

That is the whole reason `Content-Length` exists. Under HTTP/1.0 a client could read until the
connection closed, because a connection served exactly one request. Under HTTP/1.1 the connection
stays open so it can serve the next one, and a client that reads until close will wait forever for a
close that is not coming. The length is what tells it to stop.

## A target is not a path

The second word of the request line is the request target, and the safest habit to form early is that
it is **not** a file path. It is a string with structure, and `java.net.URI` will take it apart for
you — but you have to know which accessor gives you what:

```java run
import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class Uri {
    public static void main(String[] args) {
        String[] targets = {
            "/",
            "/notes",
            "/notes?tag=work&page=2",
            "/notes?q=hello%20world",
            "/notes?q=hello+world",
        };

        System.out.printf("%-26s %-10s %s%n", "target", "path", "rawQuery");
        for (String target : targets) {
            URI uri = URI.create(target);
            System.out.printf("%-26s %-10s %s%n", target, uri.getPath(), uri.getRawQuery());
        }

        System.out.println();
        System.out.println("q=hello%20world -> '" + decode("hello%20world") + "'");
        System.out.println("q=hello+world   -> '" + decode("hello+world") + "'");
        System.out.println("both spellings decode to the same value: + means space in a query string");

        System.out.println();
        URI smuggled = URI.create("/notes/a%2Fb");
        System.out.println("/notes/a%2Fb -> getPath()    = " + smuggled.getPath());
        System.out.println("             -> getRawPath() = " + smuggled.getRawPath());
        System.out.println("the decoded path contains a separator that was never in the request");
    }

    static String decode(String value) {
        return URLDecoder.decode(value, StandardCharsets.UTF_8);
    }
}
```

```text
target                     path       rawQuery
/                          /          null
/notes                     /notes     null
/notes?tag=work&page=2     /notes     tag=work&page=2
/notes?q=hello%20world     /notes     q=hello%20world
/notes?q=hello+world       /notes     q=hello+world

q=hello%20world -> 'hello world'
q=hello+world   -> 'hello world'
both spellings decode to the same value: + means space in a query string

/notes/a%2Fb -> getPath()    = /notes/a/b
             -> getRawPath() = /notes/a%2Fb
the decoded path contains a separator that was never in the request
```

Two things to notice.

`getRawQuery()` is `null` when there is no query, not the empty string. That is the `null`-vs-`""`
distinction from Chapter 21 arriving again in a new place, and it is why a query parser should be
handed the raw query only after the caller has decided what "no query" means.

And the last three lines are a security lesson, not a formatting one. `/notes/a%2Fb` decodes to
`/notes/a/b`, which contains a separator that was never in the request. `%2F` is an escaped slash, and
a program that decodes the target *before* splitting it on `/` has just been told that a single path
segment is two. That is the whole mechanism behind a large family of path-traversal bugs. **Split the
raw form, then decode the pieces** — never the other way round.

:::tip
`+` means space in a query string and *not* in a path. Both `hello%20world` and `hello+world` decoded
to `hello world` above, which is correct for a query value — that spelling comes from HTML form
encoding — and would be wrong for a path, where a literal `+` is a literal plus. This is why
`URLDecoder` is the wrong tool for a path and `URI` is the right one.
:::

:::scenario The response that was one byte short

A service serves note bodies, and the author writes the response by counting characters:

```java
String head = "HTTP/1.1 200 OK\r\nContent-Length: " + body.length() + "\r\n\r\n";
out.write((head + body).getBytes(StandardCharsets.UTF_8));
```

It passes every test the author writes, because every test uses a body made of ASCII letters. Then a
user saves a note containing an accented character, and the last character of the note never arrives.
Nothing in any log says anything is wrong.

:::solution
The mismatch is silent in both directions, and it is worth seeing both:

```java run
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;

public class Scenario {
    static final String BODY = "hello, world!";
    static final String REQUEST = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";

    public static void main(String[] args) throws Exception {
        System.out.println("the body on the wire is " + BODY.length() + " byte(s): '" + BODY + "'");
        System.out.println();

        System.out.println("-- the header understates the body --");
        exchange(BODY.length() - 1);
        System.out.println();

        System.out.println("-- the header overstates the body --");
        exchange(BODY.length() + 1);
    }

    /** Serves BODY with a Content-Length of `declared` and reports what the client saw. */
    static void exchange(int declared) throws Exception {
        String head = "HTTP/1.1 200 OK\r\nContent-Length: " + declared + "\r\n\r\n";

        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    readHead(socket.getInputStream());
                    OutputStream out = socket.getOutputStream();
                    out.write((head + BODY).getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                    Thread.sleep(800);
                } catch (IOException | InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
            server.start();

            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();
                out.write(REQUEST.getBytes(StandardCharsets.US_ASCII));
                out.flush();
                readHead(in);

                System.out.println("declared " + declared + ", written " + BODY.length());
                socket.setSoTimeout(400);
                try {
                    byte[] body = in.readNBytes(declared);
                    String text = new String(body, StandardCharsets.US_ASCII);
                    System.out.println("  the client read " + body.length + " byte(s): '" + text + "'");
                    if (body.length < BODY.length()) {
                        System.out.println("  the last character never arrived");
                    }
                } catch (SocketTimeoutException e) {
                    System.out.println("  the client waited 400 ms for a byte that was never sent");
                }
            }
            server.join();
        }
        System.out.println("  no status code said so, in either direction");
    }

    static String readHead(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        int state = 0;
        int b;
        while (state != 4 && (b = in.read()) != -1) {
            bytes.write(b);
            state = switch (state) {
                case 0 -> b == '\r' ? 1 : 0;
                case 1 -> b == '\n' ? 2 : (b == '\r' ? 1 : 0);
                case 2 -> b == '\r' ? 3 : 0;
                default -> b == '\n' ? 4 : 0;
            };
        }
        return bytes.toString(StandardCharsets.US_ASCII);
    }
}
```

```text
the body on the wire is 13 byte(s): 'hello, world!'

-- the header understates the body --
declared 12, written 13
  the client read 12 byte(s): 'hello, world'
  the last character never arrived
  no status code said so, in either direction

-- the header overstates the body --
declared 14, written 13
  the client waited 400 ms for a byte that was never sent
  no status code said so, in either direction
```

When the header understates the body, the client reads exactly what it was told to read and stops.
The remaining byte is still sitting in the socket, where it will be read as the beginning of the next
response on a keep-alive connection. When the header overstates the body, the client waits for a byte
that is never sent, and the only thing that ends the wait is a timeout.

**No status code reports either failure.** There is no checksum in HTTP, no length check that the
client can perform, and no error at the transport layer, because as far as TCP is concerned every byte
arrived exactly as it was sent. The header and the body are two independent claims about the same
message, and HTTP never checks that they agree.

The repair is to derive both from one source, which is what the next section's third solution does:
count the **bytes**, not the characters, and build the head and the body from the same array. And the
reason the bug survived the tests is worth naming — every test used an ASCII body, where
`String.length()` and the byte count are the same number. **A test suite that only uses inputs where
two different quantities coincide cannot tell them apart.**
:::
:::

## Solutions

### 1. Make the set of statuses a type

The status codes this service can send are a closed set, and the natural way to express a closed set
is an enum — which is Chapter 16's lesson arriving in a web service:

```java run
public class Sol1 {
    enum Status {
        OK(200, "OK"),
        CREATED(201, "Created"),
        NO_CONTENT(204, "No Content"),
        NOT_MODIFIED(304, "Not Modified"),
        BAD_REQUEST(400, "Bad Request"),
        NOT_FOUND(404, "Not Found"),
        METHOD_NOT_ALLOWED(405, "Method Not Allowed"),
        INTERNAL_ERROR(500, "Internal Server Error");

        final int code;
        final String reason;

        Status(int code, String reason) {
            this.code = code;
            this.reason = reason;
        }

        String family() {
            return switch (code / 100) {
                case 1 -> "informational";
                case 2 -> "success";
                case 3 -> "redirect";
                case 4 -> "client error";
                case 5 -> "server error";
                default -> "not a status code";
            };
        }

        static Status of(int code) {
            for (Status status : values()) {
                if (status.code == code) {
                    return status;
                }
            }
            throw new IllegalArgumentException("no status " + code);
        }
    }

    public static void main(String[] args) {
        for (Status status : Status.values()) {
            System.out.printf("%-18s %d %-20s %s%n",
                    status.name(), status.code, status.reason, status.family());
        }

        System.out.println();
        System.out.println("Status.of(404)     = " + Status.of(404));
        System.out.println("Status.of(418)     = " + caught(418));
        System.out.println("Status.of(404).family() = " + Status.of(404).family());
        System.out.println();
        System.out.println("the enum closes the set: every status this service can send is one of eight");
    }

    static String caught(int code) {
        try {
            return Status.of(code).toString();
        } catch (IllegalArgumentException e) {
            return "IllegalArgumentException: " + e.getMessage();
        }
    }
}
```

```text
OK                 200 OK                   success
CREATED            201 Created              success
NO_CONTENT         204 No Content           success
NOT_MODIFIED       304 Not Modified         redirect
BAD_REQUEST        400 Bad Request          client error
NOT_FOUND          404 Not Found            client error
METHOD_NOT_ALLOWED 405 Method Not Allowed   client error
INTERNAL_ERROR     500 Internal Server Error server error

Status.of(404)     = NOT_FOUND
Status.of(418)     = IllegalArgumentException: no status 418
Status.of(404).family() = client error

the enum closes the set: every status this service can send is one of eight
```

Each constant carries its code and its reason phrase, `family()` derives the family from the code
rather than storing it (so it cannot disagree with the code), and `of(int)` is the lookup for a code
that arrived over the wire.

`Status.of(418)` throwing is the right behaviour and it is worth being explicit about why. A status
code the service does not know is not a value it can respond with — it is a bug in the service or a
misunderstanding in the client, and both want to be loud. Returning `null` would move the failure to
whoever forgot to check, which is a line of code that does not exist yet.

The `family()` method is also where the closed set earns its keep. Because `Status` is an enum, the
switch over the family has an arm for every code the service can send, and adding a `429` without
deciding its family does not compile.

### 2. The request line has three parts

Before any routing, the first line of the request has to be taken apart, and the naive version has a
bug that only shows up on malformed input:

```java run
public class Sol2 {
    record RequestLine(String method, String target, String version) {
        static RequestLine parse(String line) {
            String[] parts = line.split(" ");
            if (parts.length != 3) {
                throw new IllegalArgumentException(
                        "expected three space-separated parts, found " + parts.length);
            }
            return new RequestLine(parts[0], parts[1], parts[2]);
        }
    }

    public static void main(String[] args) {
        String[] lines = {
            "GET /notes HTTP/1.1",
            "POST /notes?tag=work HTTP/1.1",
            "DELETE /notes/7 HTTP/1.1",
            "GET / HTTP/1.0",
            "GET  /two-spaces HTTP/1.1",
            "GET /notes",
        };

        for (String line : lines) {
            try {
                RequestLine request = RequestLine.parse(line);
                System.out.printf("%-28s -> %s%n", line,
                        request.method() + " " + request.target() + " " + request.version());
            } catch (IllegalArgumentException e) {
                System.out.printf("%-28s -> %s%n", line, e.getMessage());
            }
        }

        System.out.println();
        System.out.println("split(\" \") keeps empty parts, so two spaces make four fields, not three");
        System.out.println("the target is still raw here: splitting off the query is the next step");
    }
}
```

```text
GET /notes HTTP/1.1          -> GET /notes HTTP/1.1
POST /notes?tag=work HTTP/1.1 -> POST /notes?tag=work HTTP/1.1
DELETE /notes/7 HTTP/1.1     -> DELETE /notes/7 HTTP/1.1
GET / HTTP/1.0               -> GET / HTTP/1.0
GET  /two-spaces HTTP/1.1    -> expected three space-separated parts, found 4
GET /notes                   -> expected three space-separated parts, found 2

split(" ") keeps empty parts, so two spaces make four fields, not three
the target is still raw here: splitting off the query is the next step
```

`"GET  /two-spaces HTTP/1.1"` has four fields after `split(" ")`, not three, because the two spaces
produce an empty string between them — and the code rejects the request rather than silently
accepting `""` as the target. That is the correct outcome twice over: HTTP requires exactly one space
between the parts, and a parser that accepts what the spec forbids is a parser whose behaviour on
real traffic you cannot predict.

`"GET /notes"` has two fields and is rejected for the same reason. What is *not* done here is
guessing the missing version, or defaulting it to `HTTP/1.0`. A request line that does not parse is a
`400`, and the reason phrase is where you explain that.

Note also what this block deliberately does **not** do: it leaves the target raw. Splitting the query
off is a separate step with its own rules — the ones the previous section measured — and doing both at
once is how `%2F` ends up decoded before the split.

### 3. Content-Length counts bytes

The scenario's bug has a one-line fix, and the fix is to stop having two sources of truth:

```java run
import java.nio.charset.StandardCharsets;

public class Sol3 {
    /** The whole response, as the bytes that go on the wire. */
    static String response(int code, String reason, String contentType, String body) {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        return "HTTP/1.1 " + code + " " + reason + "\r\n"
                + "Content-Type: " + contentType + "\r\n"
                + "Content-Length: " + bytes.length + "\r\n"
                + "\r\n"
                + body;
    }

    static String show(String text) {
        StringBuilder out = new StringBuilder();
        for (String line : text.split("\r\n", -1)) {
            out.append(line.isEmpty() ? "|" : "| " + line).append('\n');
        }
        return out.toString();
    }

    public static void main(String[] args) {
        String body = "caf\u00e9";

        System.out.println("body             = " + body);
        System.out.println("String.length()  = " + body.length());
        System.out.println("UTF-8 byte count = " + body.getBytes(StandardCharsets.UTF_8).length);
        System.out.println();
        System.out.println("the response that writes:");
        System.out.print(show(response(200, "OK", "text/plain; charset=utf-8", body)));
        System.out.println();
        System.out.println("Content-Length counts bytes. String.length() would have said 4, and the");
        System.out.println("client would have stopped one byte early and dropped the second byte of the e.");
    }
}
```

```text
body             = café
String.length()  = 4
UTF-8 byte count = 5

the response that writes:
| HTTP/1.1 200 OK
| Content-Type: text/plain; charset=utf-8
| Content-Length: 5
|
| café

Content-Length counts bytes. String.length() would have said 4, and the
client would have stopped one byte early and dropped the second byte of the e.
```

`café` is four characters and five bytes. The response the block builds says `Content-Length: 5`,
because the byte array is the single thing both the length and the body are taken from. There is no
expression in this method that could disagree with any other, which is the property to want: **a
derived value should be derived, never computed twice.**

The prose above the block is the part worth keeping. `String.length()` and the UTF-8 byte count are
equal for every ASCII string, so a test suite made of ASCII strings cannot distinguish them — and
`Content-Length` is defined in bytes, always, for every encoding. The same mistake in the other
direction is a `Content-Length` that is too small, which truncates the response and leaves the extra
bytes to be misread as the next message.

### 4. Keep-alive reuses the socket

One socket can carry more than one request, and seeing it happen makes the `Content-Length` rule
concrete:

```java run
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class Sol4 {
    static final List<String> REQUESTS = List.of(
            "GET /one HTTP/1.1\r\nHost: localhost\r\n\r\n",
            "GET /two HTTP/1.1\r\nHost: localhost\r\n\r\n");

    public static void main(String[] args) throws Exception {
        List<String> seen = new ArrayList<>();

        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    InputStream in = socket.getInputStream();
                    OutputStream out = socket.getOutputStream();
                    for (int i = 0; i < REQUESTS.size(); i++) {
                        seen.add(readHead(in).split("\r\n")[0]);
                        String body = "reply " + (i + 1);
                        out.write(("HTTP/1.1 200 OK\r\n"
                                + "Content-Length: " + body.length() + "\r\n"
                                + "Connection: keep-alive\r\n"
                                + "\r\n"
                                + body).getBytes(StandardCharsets.US_ASCII));
                        out.flush();
                    }
                } catch (IOException e) {
                    throw new java.io.UncheckedIOException(e);
                }
            });
            server.start();

            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();
                for (String request : REQUESTS) {
                    out.write(request.getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                    String head = readHead(in);
                    int length = Integer.parseInt(head.lines()
                            .filter(l -> l.toLowerCase().startsWith("content-length:"))
                            .findFirst().orElseThrow().split(":")[1].trim());
                    in.readNBytes(length);
                }
            }
            server.join();

            System.out.println("the server handled " + seen.size()
                    + " request(s) on one connection:");
            for (String line : seen) {
                System.out.println("  " + line);
            }
            System.out.println();
            System.out.println("one socket, two request/response pairs. That is keep-alive, and it is");
            System.out.println("the reason a client must know where each body ends.");
        }
    }

    static String readHead(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        int state = 0;
        int b;
        while (state != 4 && (b = in.read()) != -1) {
            bytes.write(b);
            state = switch (state) {
                case 0 -> b == '\r' ? 1 : 0;
                case 1 -> b == '\n' ? 2 : (b == '\r' ? 1 : 0);
                case 2 -> b == '\r' ? 3 : 0;
                default -> b == '\n' ? 4 : 0;
            };
        }
        return bytes.toString(StandardCharsets.US_ASCII);
    }
}
```

```text
the server handled 2 request(s) on one connection:
  GET /one HTTP/1.1
  GET /two HTTP/1.1

one socket, two request/response pairs. That is keep-alive, and it is
the reason a client must know where each body ends.
```

The server looped twice on the same accepted socket, and the client sent its second request on the
same socket it used for the first. The two `GET` lines the server recorded are proof: one connection,
two complete exchanges.

This is the payoff of everything before it. The client could only do this because it knew where each
body ended — it read the `Content-Length`, took exactly that many bytes, and knew the next byte it
read would be the start of a status line. A client that read to end-of-stream could not have sent a
second request at all, and a server that forgot a `Content-Length` would have left its client waiting.

The `Connection` header is how each side says what it expects. `Connection: close` in the first block
of this chapter says "one exchange, then done", and `Connection: keep-alive` here says "I will serve
another". In HTTP/1.1 keep-alive is the default and `close` is the exception — which is precisely why
a missing length is a hang rather than an error.

## Key takeaways

- HTTP is **text over a TCP byte stream**. The head ends at the first `\r\n\r\n`; nothing else marks
  the boundary.
- TCP gives you ordered bytes and no message boundaries, so HTTP frames the body itself: a
  `Content-Length`, a chunked encoding, or a connection close.
- Read the head **byte by byte** and stop at the blank line. A buffered line reader over-reads into
  the body, and those bytes are not recoverable.
- `Connection refused` is the only connection failure that tells you what happened. Silence and a
  clean close both look like something other than what they are.
- A status code's **first digit is its family**, and the family decides what a client does. The reason
  phrase is decoration and must never be parsed.
- `4xx` means the request was wrong and retrying will not help; `5xx` means the server failed and
  retrying might. Returning `500` for a bad request makes every well-behaved client retry forever.
- `204` and `304` must not carry a body. A body on either poisons the next response on a keep-alive
  connection.
- Header **names are case-insensitive, values are not**, a name may appear more than once, and the
  split is on the **first** colon. A header map is a map to a list of values.
- `safe` and `idempotent` are different properties. `PUT` and `DELETE` are idempotent without being
  safe; `POST` is neither, which is why a client will not resend it on its own.
- `Content-Length` counts **bytes**. `String.length()` counts UTF-16 code units, and the two agree for
  every ASCII string — which is exactly why an all-ASCII test suite cannot catch the bug.
- A request target is not a path. Split the **raw** form first and decode the pieces after; decoding
  before splitting lets `%2F` smuggle a separator into a single segment.
- `+` means space in a query string only, never in a path.

## Practice

- [ ] Send a `HEAD` request to the server in the first block and observe that it returns headers with
      a `Content-Length` and no body. What must a client do differently?
- [ ] Reject a request with no `Host` header by returning `400`. Which of the four error statuses in
      the enum is right, and what does the reason phrase say?
- [ ] Parse `/notes?tag=a&tag=b` into a map. Decide what a repeated key means, and write the table
      that pins the decision down.
- [ ] Take a request captured by the first block and find the byte offset of the blank line. Then
      explain what `BufferedReader.readLine()` would have consumed that you cannot get back.
- [ ] Add a `405 Method Not Allowed` for a target that exists but was asked for with the wrong
      method, and include an `Allow` header naming the methods that do work.
- [ ] Change the first block's response to say `Connection: keep-alive` and read a second request on
      the same socket. What breaks first?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `HEAD` returns exactly the headers the equivalent `GET` would return, with the body omitted and the
   `Content-Length` still describing what the body *would* have been. A client must therefore never
   read a body after a `HEAD`, even though the length says there is one — and that is the one place
   where `Content-Length` does not describe the bytes that follow. The reason the method exists is
   caching and link checking: you get the metadata without paying for the body.
2. `400 Bad Request`. `Host` is mandatory in HTTP/1.1, and a request without one is malformed rather
   than unauthorised or missing — `401` would be a lie, and `404` would blame the wrong thing. The
   reason phrase should name the missing header, because the reason phrase is where a human looks and
   it costs nothing to be specific.
3. A repeated key has two defensible meanings: keep the first, or keep all of them. `Map<String,
   List<String>>` is the honest type, and the decision to make is what a *reader* does with the list —
   `tag=a&tag=b` most naturally means "either tag", which is a union and not an intersection. Write
   the table with rows for no key, one key, a repeated key and an empty value, because the empty value
   (`?tag=`) is the case that separates "absent" from "present but blank".
4. The blank line's offset is the index of the first `\r\n\r\n` plus four, and everything before it is
   the head. `readLine()` reads until a line terminator and *discards it*, so you lose both the exact
   bytes of the terminator and any position information — and because it buffers, it may have already
   consumed body bytes into its internal buffer. You cannot un-read them, and you cannot ask a
   `BufferedReader` how many bytes it holds. That is why the first block reads one byte at a time.
5. `405` with `Allow: GET, HEAD` is the right answer, and the `Allow` header is required by the spec
   precisely so a client can discover the supported methods instead of guessing. Note the difference
   from `404`: the target exists, so "not found" would be misleading, and from `403`: the method is
   wrong, not the permissions.
6. The first thing to break is the server: after serving one request it exits the loop, closes the
   socket and stops, so the client's second request goes nowhere and the client sees the connection
   close. The second thing is that the response must now be complete enough to be *parsed* by a client
   looking for the next response — a status line, headers, a blank line, exactly `Content-Length`
   bytes. Keep-alive turns every response into something that has to be correct, not merely readable,
   because a client can no longer fall back on "read until the server stops".
