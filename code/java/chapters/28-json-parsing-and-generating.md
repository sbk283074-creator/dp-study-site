---
chapter: 28
part: 4
title: JSON -- Parsing and Generating
summary: The JDK has no JSON parser, so write one. Eight grammar rules, a sealed value type, escaping measured character by character, numbers that must stay text, and the 10 KB body that kills a thread.
minutes: 75
tags: [json, parsing, recursion, escaping, unicode, security]
---

Chapter 27 ended with a service that speaks HTTP and has no idea what its bodies mean. The next thing
every web service needs is a body format, and the one everybody uses is JSON.

Here is the fact that shapes this chapter: **the JDK has no JSON parser.** Not a deprecated one, not an
internal one — nothing in `java.*` reads or writes JSON. And this track takes no third-party jars, for
the same reason Chapter 19 built its own test runner and Chapter 32 will build its own database: a
format you have to implement is a format you have to understand.

That is not a hardship. JSON's entire grammar is eight rules and a parser for it is about a hundred
lines. By the end of this chapter you will have written one, and you will know exactly which of its
decisions are yours to make.

## JSON is eight rules

```
value   = object | array | string | number | "true" | "false" | "null"
object  = "{" [ member { "," member } ] "}"
member  = string ":" value
array   = "[" [ value { "," value } ] "]"
string  = '"' { character | escape } '"'
escape  = "\" ( '"' | "\" | "/" | "b" | "f" | "n" | "r" | "t" | "u" four-hex-digits )
number  = [ "-" ] ( "0" | digit-1-to-9 { digit } ) [ "." digit { digit } ]
                   [ ( "e" | "E" ) [ "+" | "-" ] digit { digit } ]
```

Two things about that grammar matter more than the rest.

**It never recurses on the left.** A `value` can contain an `array`, which can contain a `value` — so
the parser recurses, but only ever forward, and one character of lookahead is enough to choose. That is
why recursive descent is not merely *a* way to write this parser; it is the shape the grammar already
has.

**`number` is a syntactic definition, not a numeric one.** It says what a number *looks like* and
nothing about what type it is. JSON has exactly one number type, Java has several, and that mismatch is
the source of the most expensive bug in this chapter.

## A value is a sealed interface

```java run-files
// ===== JsonDemo.java =====

import java.util.Map;

public class JsonDemo {
    static final String DOCUMENT =
            "{\"note\":{\"id\":7,\"title\":\"milk\",\"tags\":[\"a\",\"b\"],"
            + "\"done\":false,\"due\":null},\"count\":2}";

    public static void main(String[] args) {
        Json root = JsonParser.parse(DOCUMENT);
        System.out.println("parsed " + DOCUMENT.length() + " character(s)");
        System.out.println();
        print(root, "");
        String back = JsonWriter.write(root);
        System.out.println();
        System.out.println("written back, " + back.length() + " character(s):");
        System.out.println(back);
    }

    static void print(Json value, String indent) {
        switch (value) {
            case Json.Obj o -> {
                System.out.println(indent + "object, " + o.members().size() + " member(s)");
                for (Map.Entry<String, Json> member : o.members().entrySet()) {
                    System.out.println(indent + "  " + member.getKey() + ":");
                    print(member.getValue(), indent + "    ");
                }
            }
            case Json.Arr a -> {
                System.out.println(indent + "array, " + a.items().size() + " item(s)");
                for (Json item : a.items()) {
                    print(item, indent + "  ");
                }
            }
            case Json.Str s -> System.out.println(indent + "string " + s.value());
            case Json.Num n -> System.out.println(indent + "number " + n.raw());
            case Json.Bool b -> System.out.println(indent + "boolean " + b.value());
            case Json.Nil nil -> System.out.println(indent + "null");
        }
    }
}

// ===== Json.java =====

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** A JSON value. Sealed, so a switch over it is checked for exhaustiveness. */
public sealed interface Json
        permits Json.Obj, Json.Arr, Json.Str, Json.Num, Json.Bool, Json.Nil {

    /** An object keeps insertion order, so a parse/write round trip is stable. */
    record Obj(Map<String, Json> members) implements Json {
        public Obj {
            members = new LinkedHashMap<>(members);
        }

        public Json get(String name) {
            return members.get(name);
        }
    }

    record Arr(List<Json> items) implements Json {
        public Arr {
            items = List.copyOf(items);
        }
    }

    record Str(String value) implements Json {}

    /** The raw text is kept: a double cannot hold every number JSON allows. */
    record Num(String raw) implements Json {
        public double asDouble() {
            return Double.parseDouble(raw);
        }

        public long asLong() {
            return Long.parseLong(raw);
        }

        public boolean isIntegral() {
            return raw.indexOf('.') < 0 && raw.indexOf('e') < 0 && raw.indexOf('E') < 0;
        }
    }

    record Bool(boolean value) implements Json {}

    record Nil() implements Json {}
}

// ===== JsonParser.java =====

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * A recursive-descent parser for JSON, over a String, with positions in its errors.
 *
 * <p>The cursor is one int index and every method advances it. There is no lookahead beyond a single
 * character, which is the whole reason the grammar fits on a page.
 */
public final class JsonParser {
    /** What {@code peek()} returns past the end. A raw NUL outside a string is illegal JSON. */
    private static final char END = '\0';

    private final String text;
    private final int maxDepth;
    private int at;

    private JsonParser(String text, int maxDepth) {
        this.text = text;
        this.maxDepth = maxDepth;
    }

    /** No depth limit. Do not use this on input you did not produce. */
    public static Json parse(String text) {
        return parse(text, Integer.MAX_VALUE);
    }

    public static Json parse(String text, int maxDepth) {
        JsonParser parser = new JsonParser(text, maxDepth);
        parser.skip();
        Json value = parser.value(0);
        parser.skip();
        if (parser.at != parser.text.length()) {
            throw parser.error("trailing text after the value");
        }
        return value;
    }

    private Json value(int depth) {
        if (depth > maxDepth) {
            throw error("nested deeper than " + maxDepth + " levels");
        }
        return switch (peek()) {
            case '{' -> object(depth);
            case '[' -> array(depth);
            case '"' -> new Json.Str(string());
            case 't' -> literal("true", new Json.Bool(true));
            case 'f' -> literal("false", new Json.Bool(false));
            case 'n' -> literal("null", new Json.Nil());
            case END -> throw error("the input ended where a value was expected");
            default -> number();
        };
    }

    private Json.Obj object(int depth) {
        expect('{');
        Map<String, Json> members = new LinkedHashMap<>();
        skip();
        if (peek() == '}') {
            at++;
            return new Json.Obj(members);
        }
        while (true) {
            skip();
            if (peek() != '"') {
                throw error("expected a member name");
            }
            String name = string();
            skip();
            expect(':');
            skip();
            members.put(name, value(depth + 1));
            skip();
            if (peek() == ',') {
                at++;
                continue;
            }
            expect('}');
            return new Json.Obj(members);
        }
    }

    private Json.Arr array(int depth) {
        expect('[');
        List<Json> items = new ArrayList<>();
        skip();
        if (peek() == ']') {
            at++;
            return new Json.Arr(items);
        }
        while (true) {
            skip();
            items.add(value(depth + 1));
            skip();
            if (peek() == ',') {
                at++;
                continue;
            }
            expect(']');
            return new Json.Arr(items);
        }
    }

    private String string() {
        expect('"');
        StringBuilder out = new StringBuilder();
        while (true) {
            char c = peek();
            switch (c) {
                case '"' -> {
                    at++;
                    return out.toString();
                }
                case '\\' -> {
                    at++;
                    out.append(escape());
                }
                case END -> throw error("unterminated string");
                default -> {
                    if (c < 0x20) {
                        throw error("a raw control character in a string");
                    }
                    out.append(c);
                    at++;
                }
            }
        }
    }

    private char escape() {
        char c = peek();
        at++;
        return switch (c) {
            case '"' -> '"';
            case '\\' -> '\\';
            case '/' -> '/';
            case 'b' -> '\b';
            case 'f' -> '\f';
            case 'n' -> '\n';
            case 'r' -> '\r';
            case 't' -> '\t';
            case 'u' -> (char) Integer.parseInt(hex4(), 16);
            default -> throw error("unknown escape \\" + c);
        };
    }

    private String hex4() {
        if (at + 4 > text.length()) {
            throw error("a \\u escape needs four hex digits");
        }
        String digits = text.substring(at, at + 4);
        for (int i = 0; i < 4; i++) {
            if (Character.digit(digits.charAt(i), 16) < 0) {
                throw error("not a hex digit: '" + digits.charAt(i) + "'");
            }
        }
        at += 4;
        return digits;
    }

    private Json literal(String word, Json value) {
        if (!text.startsWith(word, at)) {
            throw error("expected '" + word + "'");
        }
        at += word.length();
        return value;
    }

    private Json number() {
        int start = at;
        if (peek() == '-') {
            at++;
        }
        if (!isDigit(peek())) {
            throw error("expected a value");
        }
        if (peek() == '0') {
            at++;
        } else {
            while (isDigit(peek())) {
                at++;
            }
        }
        if (peek() == '.') {
            at++;
            if (!isDigit(peek())) {
                throw error("expected a digit after '.'");
            }
            while (isDigit(peek())) {
                at++;
            }
        }
        if (peek() == 'e' || peek() == 'E') {
            at++;
            if (peek() == '+' || peek() == '-') {
                at++;
            }
            if (!isDigit(peek())) {
                throw error("expected a digit in the exponent");
            }
            while (isDigit(peek())) {
                at++;
            }
        }
        return new Json.Num(text.substring(start, at));
    }

    private void skip() {
        while (at < text.length()) {
            char c = text.charAt(at);
            if (c == ' ' || c == '\t' || c == '\n' || c == '\r') {
                at++;
            } else {
                return;
            }
        }
    }

    private void expect(char c) {
        if (peek() != c) {
            throw error("expected '" + c + "' but found " + describe(peek()));
        }
        at++;
    }

    private char peek() {
        return at < text.length() ? text.charAt(at) : END;
    }

    private static String describe(char c) {
        return c == END ? "the end of the input" : "'" + c + "'";
    }

    private static boolean isDigit(char c) {
        return c >= '0' && c <= '9';
    }

    private IllegalArgumentException error(String message) {
        int line = 1;
        int column = 1;
        int limit = Math.min(at, text.length());
        for (int i = 0; i < limit; i++) {
            if (text.charAt(i) == '\n') {
                line++;
                column = 1;
            } else {
                column++;
            }
        }
        return new IllegalArgumentException(message + " at line " + line + ", column " + column);
    }
}

// ===== JsonWriter.java =====

import java.util.Map;

/** Writes a Json value back out, escaping what JSON requires. */
public final class JsonWriter {
    private JsonWriter() {}

    public static String write(Json value) {
        StringBuilder out = new StringBuilder();
        write(value, out);
        return out.toString();
    }

    /** A compact form, with no whitespace. An indenting writer is a separate decision. */
    private static void write(Json value, StringBuilder out) {
        switch (value) {
            case Json.Nil nil -> out.append("null");
            case Json.Bool b -> out.append(b.value());
            case Json.Num n -> out.append(n.raw());
            case Json.Str s -> quote(s.value(), out);
            case Json.Arr a -> {
                out.append('[');
                for (int i = 0; i < a.items().size(); i++) {
                    if (i > 0) {
                        out.append(',');
                    }
                    write(a.items().get(i), out);
                }
                out.append(']');
            }
            case Json.Obj o -> {
                out.append('{');
                boolean first = true;
                for (Map.Entry<String, Json> member : o.members().entrySet()) {
                    if (!first) {
                        out.append(',');
                    }
                    first = false;
                    quote(member.getKey(), out);
                    out.append(':');
                    write(member.getValue(), out);
                }
                out.append('}');
            }
        }
    }

    /**
     * Escape what JSON requires, and two characters it does not.
     *
     * <p>Required: the quote, the backslash, and every character below 0x20. Everything else may be
     * written raw. {@code U+2028} and {@code U+2029} are legal raw in JSON and terminate a line in
     * JavaScript, which is why a writer that emits JSON for a browser escapes them anyway.
     */
    private static void quote(String text, StringBuilder out) {
        out.append('"');
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            switch (c) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                case '\b' -> out.append("\\b");
                case '\f' -> out.append("\\f");
                case '\u2028' -> out.append("\\u2028");
                case '\u2029' -> out.append("\\u2029");
                default -> {
                    if (c < 0x20) {
                        out.append("\\u").append(hex4(c));
                    } else {
                        out.append(c);
                    }
                }
            }
        }
        out.append('"');
    }

    /** Lower-case hex, padded to four digits, with no locale in sight. */
    private static String hex4(char c) {
        String hex = Integer.toHexString(c);
        return "0000".substring(hex.length()) + hex;
    }
}
```

```text
parsed 83 character(s)

object, 2 member(s)
  note:
    object, 5 member(s)
      id:
        number 7
      title:
        string milk
      tags:
        array, 2 item(s)
          string a
          string b
      done:
        boolean false
      due:
        null
  count:
    number 2

written back, 83 character(s):
{"note":{"id":7,"title":"milk","tags":["a","b"],"done":false,"due":null},"count":2}
```

That listing is the whole library: a sealed interface with six record implementations, a parser, a
writer, and a demo that drives them. It compiles with no dependency, because there is nothing to depend
on.

Start with the type. `Json` is **sealed** (Chapter 16), so the set of implementations is closed and the
compiler knows it. Every `switch` over a `Json` is therefore checked for exhaustiveness: add a seventh
kind of value and every switch that handles the six stops compiling. For a format whose whole job is to
be read by code you have not written yet, that is the most useful property a type can have.

`Obj` holds a `LinkedHashMap`, not a `HashMap`. JSON objects are ordered on the wire, and while the
specification says a reader must not *depend* on that order, a writer that reorders its input makes
every diff, test and log line unstable for no reason at all. Insertion order costs nothing here and
removes an entire class of "it changed but nothing changed".

And `Num` holds a **`String`**. That looks wrong for about five minutes; the section on numbers below is
the argument for it.

## Parsing: a cursor and one character of lookahead

Read `JsonParser` and you will find no cleverness anywhere. There is a `String`, an `int at`, and a
`peek()` that returns the character at `at` or a NUL past the end. Every method advances `at`. There is
no tokenizer, no separate pass, no lookahead buffer.

`value(int depth)` is the whole dispatch, and it is a `switch` on a single character:

```java
return switch (peek()) {
    case '{' -> object(depth);
    case '[' -> array(depth);
    case '"' -> new Json.Str(string());
    case 't' -> literal("true", new Json.Bool(true));
    case 'f' -> literal("false", new Json.Bool(false));
    case 'n' -> literal("null", new Json.Nil());
    case END -> throw error("the input ended where a value was expected");
    default -> number();
};
```

One character decides everything, which is exactly what "no left recursion" buys you. `object` and
`array` recurse into `value(depth + 1)`, and nothing else recurses at all.

Two details are worth noticing before the rest of the chapter uses them.

- **The depth is threaded, not stored.** `value` is told the depth it is being called at, and
  `parse(text, maxDepth)` refuses past a limit. That is the only defence in the file, and "The failure
  that is not an exception" is the reason it is not optional.
- **Errors carry a position.** `error(message)` walks from the start of the input to `at` counting
  newlines, so every failure says *where* it happened. A parser that reports "invalid JSON" and nothing
  else is a parser whose bugs become other people's debugging sessions.

## Strings, and the escapes that are not required

```sh run-project
cat > Escape.java <<'EOF'
public class Escape {
    /** Renders a string so a control character is visible in the transcript. */
    static String visible(String text) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c < 0x20 || c == '\u2028' || c == '\u2029') {
                String hex = Integer.toHexString(c);
                out.append("\\u").append("0000".substring(hex.length())).append(hex);
            } else {
                out.append(c);
            }
        }
        return out.toString();
    }

    public static void main(String[] args) {
        String[] samples = {
            "plain", "a\"b", "a\\b", "line\nbreak", "tab\there",
            "nul\u0001here", "caf\u00e9", "slash/here", "sep\u2028here",
        };

        boolean all = true;
        for (String sample : samples) {
            String written = JsonWriter.write(new Json.Str(sample));
            String back = ((Json.Str) JsonParser.parse(written)).value();
            all = all && back.equals(sample);
            System.out.printf("%-16s -> %s%n", visible(sample), written);
        }

        System.out.println();
        System.out.println("all " + samples.length + " came back unchanged: " + all);
        System.out.println();
        System.out.println("the reader accepts \\/ and the writer never emits it:");
        System.out.println("  a\\/b -> " + ((Json.Str) JsonParser.parse("\"a\\/b\"")).value());
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Escape.java
java -cp out Escape
```

```text
plain            -> "plain"
a"b              -> "a\"b"
a\b              -> "a\\b"
line\u000abreak  -> "line\nbreak"
tab\u0009here    -> "tab\there"
nul\u0001here    -> "nul\u0001here"
café             -> "café"
slash/here       -> "slash/here"
sep\u2028here    -> "sep\u2028here"

all 9 came back unchanged: true

the reader accepts \/ and the writer never emits it:
  a\/b -> a/b
```

Read the two columns and the escaping rules fall out of them. Nine inputs, and what the writer does with
each:

- `"` becomes `\"` and `\` becomes `\\` — required, because each would otherwise end or confuse the
  string literal it sits in.
- A raw newline becomes `\n`, a tab `\t`, and `U+0001` becomes `\u0001` — required, because JSON forbids
  a raw control character, meaning anything below `0x20`, inside a string.
- `café` is written **unchanged**. `é` is above `0x20`, so JSON allows it raw, and escaping it would be
  legal but wasteful: six bytes where two would do, for a character that needs no protection.
- `slash/here` is written unchanged. `/` **may** be escaped as `\/` and need not be; the parser accepts
  both and the writer emits the shorter one. That is the last line of the output — `a\/b -> a/b` — and it
  is the general shape of a format: the reader is the permissive one, and a writer is free to be stricter
  than the grammar requires.
- `sep\u2028here` is escaped even though JSON does not require it. `U+2028` and `U+2029` are legal raw
  in JSON and are **line terminators in JavaScript**, so a document pasted into a `<script>` block or
  handed to `eval` breaks a line that the JSON specification says is one line. Six bytes, one whole
  category of "it works until it does not".

The `all 9 came back unchanged: true` line is the property that matters, and it is worth being precise
about what it does and does not prove. It proves the writer and the reader agree about these nine
strings. It does not prove either is correct — that is what the grammar is for, and it is why this
section is a measurement rather than a proof.

## Numbers are text, because a double is not a JSON number

```sh run-project
cat > Numbers.java <<'EOF'
public class Numbers {
    public static void main(String[] args) {
        String[] texts = {"1", "1.0", "1e3", "-0", "0.1", "9007199254740993",
                          "12345678901234567890"};

        System.out.printf("%-22s %-22s %-22s %s%n", "text", "raw kept", "as a double", "same?");
        for (String text : texts) {
            Json.Num number = (Json.Num) JsonParser.parse(text);
            String asDouble = String.valueOf(number.asDouble());
            System.out.printf("%-22s %-22s %-22s %s%n", text, number.raw(), asDouble,
                    number.raw().equals(asDouble) ? "yes" : "no");
        }

        System.out.println();
        System.out.println("9007199254740993 is 2^53 + 1, the first integer a double cannot hold:");
        Json.Num big = (Json.Num) JsonParser.parse("9007199254740993");
        System.out.println("  as a long    : " + big.asLong());
        System.out.println("  as a double  : " + (long) big.asDouble());
        System.out.println("  written back : " + JsonWriter.write(big));
        System.out.println();
        System.out.println("a parser that stored a double would write 9007199254740992 back,");
        System.out.println("with no error anywhere, so the text is what this parser keeps");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Numbers.java
java -cp out Numbers
```

```text
text                   raw kept               as a double            same?
1                      1                      1.0                    no
1.0                    1.0                    1.0                    yes
1e3                    1e3                    1000.0                 no
-0                     -0                     -0.0                   no
0.1                    0.1                    0.1                    yes
9007199254740993       9007199254740993       9.007199254740992E15   no
12345678901234567890   12345678901234567890   1.2345678901234567E19  no

9007199254740993 is 2^53 + 1, the first integer a double cannot hold:
  as a long    : 9007199254740993
  as a double  : 9007199254740992
  written back : 9007199254740993

a parser that stored a double would write 9007199254740992 back,
with no error anywhere, so the text is what this parser keeps
```

The table is the argument. Read the `same?` column: **five of the seven texts change when they become a
`double`.**

- `1` becomes `1.0`. A document that said "the id is the integer 1" now says "1.0", and a strict reader
  on the other end may reject it or may store a float.
- `1e3` becomes `1000.0` — the same value in different text, and `1e3` was legal input.
- `-0` becomes `-0.0`. Negative zero is a real IEEE value and a real JSON text, and they are not the
  same token.
- `9007199254740993` becomes `9.007199254740992E15`. This is the one that matters.

That number is `2^53 + 1`, and `2^53` is the largest integer a `double` can represent exactly. Above it,
consecutive doubles are more than one apart, so the odd integers simply do not exist. The block makes
the loss concrete:

```
  as a long    : 9007199254740993
  as a double  : 9007199254740992
  written back : 9007199254740993
```

Read that again, because the third line is the point. A parser that stored a `double` would have written
`...992` back — **silently, with no error anywhere, in a document that is still perfectly valid JSON.**
No test that asks "did it parse" can see it. The only defence is to refuse to throw the text away, which
is why `Num` holds a `String` and offers `asDouble()`, `asLong()` and `isIntegral()` as *conversions*
rather than as storage.

The rule generalises, and it is the same rule as Chapter 18's `BigDecimal`: **a number that arrives as
text and leaves as text should never pass through a binary float.** Identifiers, nanosecond timestamps,
currency amounts, and anything that came out of a 64-bit counter all belong in that category.

## Rejecting is most of the job

```sh run-project
cat > Errors.java <<'EOF'
public class Errors {
    static String visible(String text) {
        return text.isEmpty() ? "(empty)" : text;
    }

    public static void main(String[] args) {
        String[] bad = {
            "{\"a\":}", "{\"a\" 1}", "[1,2", "{\"a\":1}x", "\"abc",
            "{\"a\":01}", "[1,]", "tru", "{\"a\":1,}", "",
        };

        for (String text : bad) {
            try {
                JsonParser.parse(text);
                System.out.printf("%-14s -> ACCEPTED, which is wrong%n", visible(text));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-14s -> %s%n", visible(text), e.getMessage());
            }
        }

        System.out.println();
        System.out.println("ten malformed documents, ten rejections, and every message has a position");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Errors.java
java -cp out Errors
```

```text
{"a":}         -> expected a value at line 1, column 6
{"a" 1}        -> expected ':' but found '1' at line 1, column 6
[1,2           -> expected ']' but found the end of the input at line 1, column 5
{"a":1}x       -> trailing text after the value at line 1, column 8
"abc           -> unterminated string at line 1, column 5
{"a":01}       -> expected '}' but found '1' at line 1, column 7
[1,]           -> expected a value at line 1, column 4
tru            -> expected 'true' at line 1, column 1
{"a":1,}       -> expected a member name at line 1, column 8
(empty)        -> the input ended where a value was expected at line 1, column 1

ten malformed documents, ten rejections, and every message has a position
```

Ten malformed documents, ten rejections, and every message carries a position. A parser is judged by
what it refuses, and the interesting thing about this list is how much of it is *nearly* valid:

- `{"a":1}x` — the object is fine; the `x` after it is not. The check is one line at the end of `parse`,
  and without it the parser would silently ignore everything after the first value. Solution 4 is about
  that line.
- `[1,2` — the array is unterminated, and the message says `expected ']' but found the end of the input`,
  which is exactly the sentence a person needs.
- `{"a":01}` — JSON forbids a leading zero and this parser rejects it. Notice *how*: the message is
  `expected '}' but found '1'`, because `number()` consumed the `0` and stopped. The refusal is correct
  and the reason given is not the one you would write down. That is normal for a hand-written parser, and
  it is worth knowing that a correct refusal can carry an imprecise explanation.
- `tru` — `literal()` uses `startsWith`, so a truncated keyword fails at the keyword rather than at some
  later bracket.
- `""`, the empty input — a value was expected and the input ended. An empty body is not an empty
  document, and a service that treats it as one has quietly invented a default.

Nothing here throws a `NullPointerException` and nothing reports a bare index into a string. Every
failure is an `IllegalArgumentException` carrying a line and a column — which is precisely the type the
dispatcher in Chapter 27 catches.

## The failure that is not an exception

```sh run-project
cat > Depth.java <<'EOF'
public class Depth {
    public static void main(String[] args) {
        for (int depth : new int[] {1000, 5000}) {
            String document = "[".repeat(depth) + "]".repeat(depth);
            System.out.printf("%6d levels, %6d characters -> ", depth, document.length());
            try {
                JsonParser.parse(document);
                System.out.println("parsed");
            } catch (StackOverflowError e) {
                System.out.println("StackOverflowError");
            }
        }

        System.out.println();
        System.out.println("a depth limit turns that into an ordinary refusal:");
        String deep = "[".repeat(5000) + "]".repeat(5000);
        try {
            JsonParser.parse(deep, 64);
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }

        System.out.println();
        System.out.println("StackOverflowError is an Error, not a RuntimeException, so Chapter 27's");
        System.out.println("catch (RuntimeException e) in the dispatcher does not catch it:");
        try {
            try {
                JsonParser.parse("[".repeat(100000) + "]".repeat(100000));
            } catch (RuntimeException e) {
                System.out.println("  caught as a RuntimeException");
            }
        } catch (StackOverflowError e) {
            System.out.println("  it escaped that catch and arrived as " + e.getClass().getName());
        }
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Depth.java
java -cp out Depth
```

```text
  1000 levels,   2000 characters -> parsed
  5000 levels,  10000 characters -> StackOverflowError

a depth limit turns that into an ordinary refusal:
  nested deeper than 64 levels at line 1, column 66

StackOverflowError is an Error, not a RuntimeException, so Chapter 27's
catch (RuntimeException e) in the dispatcher does not catch it:
  it escaped that catch and arrived as java.lang.StackOverflowError
```

Now the interesting one, and it is not a bug in the parser. It is a property of recursion.

```
  1000 levels,   2000 characters -> parsed
  5000 levels,  10000 characters -> StackOverflowError
```

Ten kilobytes. Ten thousand characters of `[` and `]` — smaller than one image upload, smaller than most
HTML pages — and the parser dies. Not "returns an error": **dies**, because every nesting level costs a
stack frame and the stack is a fixed size.

Two things make that worse than it looks.

**It is a property of the thread, not of the input.** The exact threshold depends on the stack size and
the frame size, so those numbers are this JVM on this machine, and a different `-Xss` moves them. What
does not move is the shape: some depth kills it, and the depth is small.

**`StackOverflowError` is an `Error`, not a `RuntimeException`.** Chapter 27's dispatcher is

```java
try {
    response = router.route(Requests.from(exchange));
} catch (RuntimeException e) {
    response = Response.text(500, "the service failed: " + e.getMessage());
}
```

and that `catch` does not catch this. The output says so directly:

```
  it escaped that catch and arrived as java.lang.StackOverflowError
```

So the client receives **nothing at all** — the dropped connection Chapter 27 measured, arriving through
a door that chapter did not know existed. A malformed body is a `400`; a deeply nested body is a dead
thread.

:::warning A size limit is not a shape limit

It is tempting to conclude "limit the body to 1 MB and move on". The body in that block is **10 KB**. A
size limit bounds how much memory a request may consume; it says nothing about how deep the document is,
and depth is what kills a recursive parser. They are different limits and you need both.

:::

The fix is the `maxDepth` parameter, and the same block shows it working: `nested deeper than 64 levels
at line 1, column 66` — an ordinary refusal, caught by an ordinary `catch`, turned into an ordinary
response.

## Writing back is not the same as printing

```sh run-project
cat > RoundTrip.java <<'EOF'
public class RoundTrip {
    public static void main(String[] args) {
        String[] documents = {
            "{}", "[]", "{\"a\":[]}", "[1,2,3]", "{\"a\":{\"b\":[true,false,null]}}",
            "{\"esc\":\"a\\nb\"}", "  {  \"spaced\" :  1  }  ",
        };

        for (String document : documents) {
            Json once = JsonParser.parse(document);
            String written = JsonWriter.write(once);
            String twice = JsonWriter.write(JsonParser.parse(written));
            System.out.printf("%-30s -> %-30s stable=%s%n", document, written,
                    written.equals(twice));
        }

        System.out.println();
        System.out.println("whitespace is not part of the value, so the first write normalises it");
        System.out.println("and the second write is byte-for-byte the same as the first");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out RoundTrip.java
java -cp out RoundTrip
```

```text
{}                             -> {}                             stable=true
[]                             -> []                             stable=true
{"a":[]}                       -> {"a":[]}                       stable=true
[1,2,3]                        -> [1,2,3]                        stable=true
{"a":{"b":[true,false,null]}}  -> {"a":{"b":[true,false,null]}}  stable=true
{"esc":"a\nb"}                 -> {"esc":"a\nb"}                 stable=true
  {  "spaced" :  1  }          -> {"spaced":1}                   stable=true

whitespace is not part of the value, so the first write normalises it
and the second write is byte-for-byte the same as the first
```

`JsonWriter` is a `switch` over the sealed interface with no `default`, which is the exhaustiveness
property from the top of the chapter paying off: it is impossible to add a seventh kind of `Json` and
forget to teach the writer about it, because the compiler will not let you.

The measurement is a round trip, and the column that matters is the last one:

```
{"a":[]}                       -> {"a":[]}                       stable=true
  {  "spaced" :  1  }          -> {"spaced":1}                   stable=true
```

**Writing is not printing.** The input `  {  "spaced" :  1  }  ` is a perfectly valid JSON document and
the output is not the same string — the whitespace is gone, because whitespace is not part of the value.
That is why `stable` is the property to test and not `equal`: writing, parsing and writing again has to
produce the same bytes, and it does, for all seven documents.

That property is what makes a JSON body diffable in a test, hashable in a cache, and safe to log. A
writer that emitted a `HashMap`'s iteration order would break all three — which is the other half of the
reason `Obj` holds a `LinkedHashMap`.

:::scenario A 10 KB body that kills the thread

A service accepts `POST /notes` with a JSON body. There is a size limit — 1 MB, checked before the
parser runs — and the dispatcher is Chapter 27's, with `catch (RuntimeException e)` wrapped around the
whole route.

An attacker sends a body of 200,000 characters, all of them `[`.

The body is five times smaller than the limit. What does the client receive, and what is the smallest
change that turns this into a normal error?

:::solution
```sh run-project
cat > Scenario.java <<'EOF'
public class Scenario {
    /** Chapter 27's dispatcher, in miniature: the catch is RuntimeException. */
    static String dispatch(String body) {
        try {
            Json parsed = JsonParser.parse(body);
            return "200 " + JsonWriter.write(parsed);
        } catch (RuntimeException e) {
            return "400 " + e.getMessage();
        }
    }

    public static void main(String[] args) {
        System.out.println("a malformed body:");
        System.out.println("  " + dispatch("{\"a\":}"));

        String deep = "[".repeat(100000) + "]".repeat(100000);
        System.out.println();
        System.out.println("a nested body of " + deep.length() + " character(s):");
        try {
            System.out.println("  " + dispatch(deep));
        } catch (StackOverflowError e) {
            System.out.println("  the dispatcher never returned: " + e.getClass().getName());
        }

        System.out.println();
        System.out.println("the dispatcher catches RuntimeException, and StackOverflowError is an");
        System.out.println("Error -- so it is not caught, and the client gets no response at all");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
```

```text
a malformed body:
  400 expected a value at line 1, column 6

a nested body of 200000 character(s):
  the dispatcher never returned: java.lang.StackOverflowError

the dispatcher catches RuntimeException, and StackOverflowError is an
Error -- so it is not caught, and the client gets no response at all
```

The client receives **nothing at all**. The first line of the output shows the ordinary case working — a
malformed body becomes a clean `400` — and the second shows the nested one:

```
a nested body of 200000 character(s):
  the dispatcher never returned: java.lang.StackOverflowError
```

The dispatcher never returned, so nothing was ever written to the socket, so the connection closed with
an unanswered request. Chapter 27 established that an uncaught *exception* costs the client its
response; this is the same failure with a different cause, and it is worse, because `catch
(RuntimeException)` is not the wrong catch by accident. It is exactly the right catch for exceptions and
no catch at all for errors.

Three things make this a real vulnerability rather than a curiosity:

1. **The size limit does not help.** 200 KB is well under 1 MB, and the parser dies at roughly 5 KB of
   nesting.
2. **It costs the attacker almost nothing.** The body is one repeated character. There is no computation
   to prepare and no state to keep.
3. **It is caught nowhere.** The thread serving the request dies with the error, and if that handler is
   running on a pool thread, the pool is now one thread smaller.

The smallest change that fixes it is a depth limit inside the parser:

```java
if (depth > maxDepth) {
    throw error("nested deeper than " + maxDepth + " levels");
}
```

One `int`, one comparison, in one place — and it converts an `Error` that escapes every catch into an
`IllegalArgumentException` that the existing dispatcher already handles. Solution 1 is that fix,
measured against the same 200 KB body.

The lesson generalises well past JSON: **a limit on input size is not a limit on input shape.** Every
recursive consumer of untrusted input needs a depth bound, and the bound belongs to the consumer rather
than to whoever calls it — because the caller is the one who forgot.
:::
:::

## Solutions

### 1. A depth limit belongs to the parser

The scenario's fix, and the reason it goes in `JsonParser` rather than in the handler.

```sh run-project
cat > Sol1.java <<'EOF'
public class Sol1 {
    public static void main(String[] args) {
        String deep = "[".repeat(100000) + "]".repeat(100000);
        System.out.println("a body of " + deep.length() + " character(s):");

        System.out.println();
        System.out.println("with no limit:");
        try {
            JsonParser.parse(deep);
        } catch (StackOverflowError e) {
            System.out.println("  StackOverflowError, which the dispatcher cannot catch");
        }

        System.out.println();
        System.out.println("with a limit of 64:");
        try {
            JsonParser.parse(deep, 64);
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }

        System.out.println();
        System.out.println("the limit is one int checked in one place, and it belongs to the parser");
        System.out.println("rather than to the caller, so no route can forget to pass it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
```

```text
a body of 200000 character(s):

with no limit:
  StackOverflowError, which the dispatcher cannot catch

with a limit of 64:
  nested deeper than 64 levels at line 1, column 66

the limit is one int checked in one place, and it belongs to the parser
rather than to the caller, so no route can forget to pass it
```

The same 200 KB body, twice. With no limit it is a `StackOverflowError` that nothing can catch; with a
limit of 64 it is a sentence with a position in it.

Putting the limit in the parser rather than in the caller is the whole point. A handler that remembers to
call `parse(body, 64)` is a handler that can forget, and the failure mode of forgetting is not an error
message — it is a dead thread. A default of `Integer.MAX_VALUE` and an explicit opt-in to a bound would
be exactly backwards: the safe choice has to be the one you get by accident, which means the bound
belongs in the API the caller already uses.

### 2. A duplicate name is not a merge

JSON permits an object to contain the same member name twice. The specification does not say what a
reader should do about it, and that silence is the problem.

```sh run-project
cat > Sol2.java <<'EOF'
public class Sol2 {
    static int occurrences(String text, String needle) {
        int count = 0;
        int at = text.indexOf(needle);
        while (at >= 0) {
            count++;
            at = text.indexOf(needle, at + needle.length());
        }
        return count;
    }

    public static void main(String[] args) {
        String body = "{\"role\":\"user\",\"role\":\"admin\"}";
        Json.Obj parsed = (Json.Obj) JsonParser.parse(body);

        System.out.println("the body:                   " + body);
        System.out.println("members named 'role' in it: " + occurrences(body, "\"role\""));
        System.out.println("members named 'role' out:   " + parsed.members().size());
        System.out.println("the value kept:             " + ((Json.Str) parsed.get("role")).value());

        System.out.println();
        System.out.println("two went in and one came out, and nothing said so");
        System.out.println("a proxy that keeps the first and a service that keeps the last disagree");
        System.out.println("about a body they both call valid, so a duplicate name is worth rejecting");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
```

```text
the body:                   {"role":"user","role":"admin"}
members named 'role' in it: 2
members named 'role' out:   1
the value kept:             admin

two went in and one came out, and nothing said so
a proxy that keeps the first and a service that keeps the last disagree
about a body they both call valid, so a duplicate name is worth rejecting
```

Two members named `role` went in and one came out, and nothing said so. This parser keeps the last one,
because `members.put` overwrites — a reasonable choice, and not the only reasonable one. A reader that
keeps the **first** is equally defensible.

That is what makes it a security problem rather than a style question. If a proxy validates the first
`role` and the service acts on the last, then a body that both ends consider valid produces an
authorisation decision the proxy did not make. This is the same shape as Chapter 25's `%2F` smuggling:
two components disagreeing about what a valid input means.

The fix is to reject rather than to choose. `Obj`'s compact constructor is already the right place to
notice, or the parser can check `members.containsKey(name)` before putting — and either way the answer
becomes a `400` instead of a guess.

### 3. Money is not a double

The number section established that a `double` loses large integers. It loses small decimals too, and
money is the case that costs real money.

```sh run-project
cat > Sol3.java <<'EOF'
import java.math.BigDecimal;

public class Sol3 {
    public static void main(String[] args) {
        String body = "{\"price\":0.1,\"tax\":0.2}";
        Json.Obj parsed = (Json.Obj) JsonParser.parse(body);

        BigDecimal price = new BigDecimal(((Json.Num) parsed.get("price")).raw());
        BigDecimal tax = new BigDecimal(((Json.Num) parsed.get("tax")).raw());
        System.out.println("from the raw text: " + price.add(tax));

        double priceAsDouble = ((Json.Num) parsed.get("price")).asDouble();
        double taxAsDouble = ((Json.Num) parsed.get("tax")).asDouble();
        System.out.println("from the doubles:  " + (priceAsDouble + taxAsDouble));

        System.out.println();
        System.out.println("both answers came out of the same body, and only one of them is money");
        System.out.println("BigDecimal can only be built from the text, which is why the parser kept it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
```

```text
from the raw text: 0.3
from the doubles:  0.30000000000000004

both answers came out of the same body, and only one of them is money
BigDecimal can only be built from the text, which is why the parser kept it
```

Both lines came out of the same body, and only one of them is money. `0.1` and `0.2` are exactly
representable in base 10 and not at all in base 2, so the `double` sum carries a rounding error that no
amount of later formatting removes.

`BigDecimal` can only be built from the text — there is no constructor that takes a `double` and gives
you back the value you meant — which is precisely why the parser keeps the raw string. `Num.raw()` is
not a convenience for debugging; it is the only field that can produce a correct `BigDecimal`, and it is
the reason the type is shaped the way it is.

### 4. The input has to end

One line at the end of `parse` decides whether a body is one document or the beginning of one.

```sh run-project
cat > Sol4.java <<'EOF'
public class Sol4 {
    static String verdict(String body) {
        try {
            JsonParser.parse(body);
            return "accepted";
        } catch (IllegalArgumentException e) {
            return e.getMessage();
        }
    }

    public static void main(String[] args) {
        String[] bodies = {"{\"a\":1}", "{\"a\":1}   ", "{\"a\":1}x", "{\"a\":1}{\"b\":2}"};

        for (String body : bodies) {
            System.out.printf("%-24s -> %s%n", "'" + body + "'", verdict(body));
        }

        System.out.println();
        System.out.println("trailing whitespace is fine and a second value is not, because the check is");
        System.out.println("'the input ended', not 'the first value ended'. A parser that stopped at the");
        System.out.println("first value would accept the last body and drop {\"b\":2} without a word");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
```

```text
'{"a":1}'                -> accepted
'{"a":1}   '             -> accepted
'{"a":1}x'               -> trailing text after the value at line 1, column 8
'{"a":1}{"b":2}'         -> trailing text after the value at line 1, column 8

trailing whitespace is fine and a second value is not, because the check is
'the input ended', not 'the first value ended'. A parser that stopped at the
first value would accept the last body and drop {"b":2} without a word
```

Trailing whitespace is accepted and a second value is not, and the distinction is exact: the check is
*"the input ended"*, not *"the first value ended"*. `parse` skips whitespace, parses a value, skips
whitespace again, and then requires `at == text.length()`.

Without that line, `{"a":1}{"b":2}` parses to `{"a":1}` and the second document is left in the buffer
unread and unreported. That matters because a body is not always consumed by one reader: a proxy that
counts the bytes, a logger that records the raw text, and the service that parses it are three readers
of one string, and they must agree on where it ends. A parser that stops early silently hands the next
reader a different document.

## Key takeaways

- **The JDK has no JSON parser**, and this track adds no jars, so the parser is part of the book rather
  than a dependency of it.
- JSON's grammar is eight rules, none of them left-recursive, which is why a cursor, one character of
  lookahead and recursive descent are enough.
- `Json` is a **sealed** interface with six records, so every `switch` over a value is checked for
  exhaustiveness — including `JsonWriter`'s, which has no `default`.
- `Obj` holds a **`LinkedHashMap`**: JSON objects are ordered, and a writer that reorders its input makes
  every diff, hash and log line unstable for nothing.
- `Num` holds a **`String`**. `2^53 + 1` becomes `2^53` as a `double`, silently, in a document that is
  still valid JSON.
- A number that arrives as text and leaves as text must never pass through a binary float. `BigDecimal`
  is built from `Num.raw()` or it is wrong.
- Escaping is **per character**: `"` and `\` and every character below `0x20` are required; `é` and `/`
  are not; `U+2028` and `U+2029` are not required by JSON and are escaped anyway, because they terminate
  a line in JavaScript.
- The reader is the permissive one. `\/` is accepted and never emitted — a writer may be stricter than
  the grammar.
- Every error is an **`IllegalArgumentException` with a line and a column**. A parser that says "invalid
  JSON" is a parser whose bugs become someone else's afternoon.
- A correct refusal can carry an imprecise reason: `{"a":01}` is rejected with a message about `}`
  because the `0` was consumed first.
- **`StackOverflowError` is an `Error`, not a `RuntimeException`**, so Chapter 27's
  `catch (RuntimeException e)` does not catch it and the client gets no response at all.
- A **size** limit is not a **shape** limit. A 10 KB body of `[` kills a recursive parser; the depth
  bound belongs in the parser, where it cannot be forgotten.
- Writing is not printing: whitespace is not part of the value, so the property to test is
  **write → parse → write is byte-identical**, not `equal`.
- A duplicate member name is a **disagreement waiting to happen** between two readers of the same body.
  Reject it rather than choosing a winner.

## Practice

- [ ] Add `Json.Bool` handling to a `switch` you write yourself and then delete one arm. Which error do
      you get, and why does that only work because `Json` is sealed?
- [ ] `Obj` copies its map in the compact constructor. What breaks if it does not, and what does the
      copy cost?
- [ ] Write `Num.asBigDecimal()`. What should it do with `1e3`, and what should `isIntegral()` mean for
      `1.0`?
- [ ] The writer emits compact JSON. Write an indenting variant and make the round-trip property still
      hold — or explain why it cannot.
- [ ] A body arrives with a byte-order mark (`EF BB BF`) before the `{`. What does this parser do, and
      which layer should have removed it?
- [ ] The parser rejects a raw control character inside a string. Which other characters below `0x20`
      are legal *outside* a string in JSON, and what does that tell you about where the check belongs?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Removing an arm gives `the switch expression does not cover all possible input values` — a compile
   error, not a runtime one. It works because `Json` is sealed: the compiler can enumerate the permitted
   subtypes, so exhaustiveness is decidable. With a non-sealed interface it would have to insert a
   synthetic `default` that throws, and you would find out at run time, on the one input you did not
   test. This is the strongest practical argument for sealing a closed set of variants.
2. Without the copy, `Obj` would share the caller's map, so mutating the map after constructing the
   object would change a value that is supposed to be immutable — and `Json` is passed around a service
   precisely because it is safe to share. The cost is one `LinkedHashMap` allocation and a copy of the
   entries, which for a request body is negligible next to the parsing itself. Note that `Arr` uses
   `List.copyOf`, which is even cheaper because it can return the same instance when the list is already
   immutable.
3. `new BigDecimal(raw)` for every case, which is exactly what makes `1e3` interesting: `BigDecimal`
   accepts `1e3` and gives `1E+3`, whose `scale()` is negative. That is correct — the text really does
   have no decimal places — but a caller expecting `scale() == 0` will be surprised. `isIntegral()`
   answers "does the text contain a `.` or an `e`", which is a *syntactic* question and is why it returns
   `false` for `1.0`: the value is an integer and the text is not. Two different questions, and the
   method name should say which one it answers.
4. An indenting writer breaks the round-trip property as stated, because `write(parse(write(v)))` inserts
   whitespace the first output did not have. The property that survives is weaker and more useful: parse
   both outputs and compare the *values*, or define the canonical form as compact and let indentation be
   a separate, explicitly non-canonical view. This is why pretty-printing belongs to a debug command and
   not to the response path.
5. This parser rejects it, with `expected a value`, because the BOM is a character the grammar does not
   allow there. The right place to remove it is the layer that decoded the bytes: a BOM is an encoding
   artefact, not a document feature, so the code that turns `byte[]` into `String` should strip a leading
   `U+FEFF` once. The general rule is that a parser should see text, and the text should already be in
   the encoding the format assumes.
6. The four JSON whitespace characters — space, tab, newline and carriage return — are legal anywhere
   between tokens, so `skip()` is called at every point where a token may be preceded by whitespace, and
   *not* inside `string()`. Inside a string, a raw newline is a control character and is rejected. That
   is the answer to "where does the check belong": a character's legality depends on the state the parser
   is in, which is exactly why the check lives in `string()` and not in a pre-pass over the input.
