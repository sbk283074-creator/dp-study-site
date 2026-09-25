---
chapter: 21
part: 3
title: Reading and Parsing Input
summary: Read text from a file, a string or standard input without losing a line or a character, and turn the strings a user types into values your program can trust.
minutes: 55
tags: [io, bufferedreader, scanner, parsing, stdin, validation]
---

Chapter 20 gave Quill its shape: a `run` method that returns an exit code, a `Note` that knows how to
turn itself into a line, and a `Vault` that owns a file. What it did not have is a way to *get text
in*. Every value so far was a literal typed into a `main` method. This chapter is about the boundary
where the outside world — a file, a terminal, a pipe — hands your program a sequence of characters,
and the two things that go wrong there: you lose data you did not mean to lose, and you accept data you
should not have. Both failures are quiet, and both are cheap to prevent once you know the shape of the
tool.

## A reader is a stream, and a stream ends

The interface for reading text is `Reader`, and the one you will use is `BufferedReader`, because it
reads in blocks and hands you one line at a time:

```java run
import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

public class ReaderLines {
    public static void main(String[] args) throws IOException {
        String text = "first\n\nthird\n";

        int count = 0;
        try (BufferedReader reader = new BufferedReader(new StringReader(text))) {
            String line;
            while ((line = reader.readLine()) != null) {
                count++;
                System.out.printf("%d: '%s' (length %d)%n", count, line, line.length());
            }
        }

        System.out.println("lines = " + count);
        System.out.println("the blank line was a line; the trailing newline was not");
    }
}
```

```text
1: 'first' (length 5)
2: '' (length 0)
3: 'third' (length 5)
lines = 3
the blank line was a line; the trailing newline was not
```

Three lines of output from a four-line string, and the count is the lesson. The input was
`"first\n\nthird\n"`, which is three lines of text and a terminator. `readLine` produced:

- `first` for the first line;
- `''`, an empty string, for the blank line in the middle;
- `third` for the last line;
- and then **`null`**, which is how a stream says "there is nothing more".

The trailing `\n` did not create a fourth line, and the blank line did create one. That distinction is
the whole contract: **a line is terminated by a newline, not made of one**, so a file ending in a
newline has exactly as many lines as it has newlines, and a blank line in the middle is a real line
with zero characters in it.

`readLine` also accepts more than one terminator. It treats `\n`, `\r` and the pair `\r\n` as ending a
line and strips whichever it found. That is why the loop above never sees a `\r`, and it is worth
remembering, because it is the reason one particular bug appears in one place and not another — the
scenario later in this chapter turns on exactly this.

The `try (...)` is a **try-with-resources**, from Chapter 13. `BufferedReader` is `Closeable`, so it is
closed when the block ends, including when the block ends because something threw. You will see a
reader closed by hand later in this chapter, and what happens when you keep reading after that.

## Scanner is convenient, and it has one sharp edge

`Scanner` reads *tokens* rather than lines. You tell it what you expect and it skips whitespace and
parses it for you, which makes it the fastest way to read a few numbers from a terminal:

```java run
import java.util.Scanner;

public class ScannerBasics {
    public static void main(String[] args) {
        String input = "42\nAda Lovelace\n";

        Scanner scanner = new Scanner(input);
        int number = scanner.nextInt();
        String afterInt = scanner.nextLine();
        String name = scanner.nextLine();

        System.out.println("number      = " + number);
        System.out.println("afterInt    = '" + afterInt + "' (length " + afterInt.length() + ")");
        System.out.println("name        = '" + name + "'");

        System.out.println();

        Scanner fixed = new Scanner(input);
        int parsed = Integer.parseInt(fixed.nextLine());
        String rest = fixed.nextLine();
        System.out.println("parsed      = " + parsed);
        System.out.println("rest        = '" + rest + "'");
    }
}
```

```text
number      = 42
afterInt    = '' (length 0)
name        = 'Ada Lovelace'

parsed      = 42
rest        = 'Ada Lovelace'
```

Look at the first three lines. The input was `"42\nAda Lovelace\n"`. `nextInt()` returned `42`. Then
`nextLine()` returned `''` — the empty string — and only the *second* `nextLine()` returned
`Ada Lovelace`.

The explanation is in the name. `nextInt()` reads the characters that make up an integer and stops at
the first character that cannot be part of one, which is the `\n`. It does **not** consume that `\n`.
So the newline is still sitting in the stream, and the very next `nextLine()` finds a line terminator
immediately and returns everything before it — nothing.

This is the single most common `Scanner` bug, and there are two ways out. You can call `nextLine()`
once to throw away the rest of the line the number was on, or you can read whole lines and parse them
yourself, which is what the second half of the transcript does and what Quill does everywhere. Solution
1 measures all three approaches side by side.

:::tip
`Scanner` skips whitespace between tokens, so it is genuinely convenient when the input is a sequence
of numbers separated by spaces. It is a poor fit for line-oriented formats, because every format where
a line means something needs `nextLine()`, and `nextLine()` and `nextInt()` disagree about where a
token ends. Use `BufferedReader` for line formats and `Scanner` for token streams.
:::

## A reader is not a collection

The for-each loop from Chapter 7 works on arrays and on anything that implements `Iterable`. A
`BufferedReader` is neither, and the compiler says so in a way worth reading once:

```java bad
import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

public class BadForeach {
    public static void main(String[] args) throws IOException {
        try (BufferedReader reader = new BufferedReader(new StringReader("a\nb\n"))) {
            for (String line : reader) {
                System.out.println(line);
            }
        }
    }
}
```

```text
error: for-each not applicable to expression type
            for (String line : reader) {
                               ^
```

`required: array or java.lang.Iterable` and `found: BufferedReader` — the diagnostic names both sides,
which makes it one of the more helpful ones javac produces. The fix is not to find a way to iterate;
it is to write the `while` loop, because the loop *is* the iteration. The reason `BufferedReader` is
not `Iterable` is that reading is destructive: each call consumes from the stream, so a for-each would
be a lie about what is happening.

This is the difference between a stream and a collection, and it is worth stating plainly. A `List` you
can traverse as many times as you like. A stream you can traverse **once**, and then it is exhausted.
The `lines` block above reads to `null`; if you called the same method again on the same reader it
would return an empty list immediately, because the stream is at its end and stays there.

## Parsing turns text into a decision

The user types characters. Your program needs an `int`. `Integer.parseInt` is the bridge, and it is
strict about what it will accept:

```java throw
public class ThrowParse {
    public static void main(String[] args) {
        System.out.println("about to parse");
        int id = Integer.parseInt("abc");
        System.out.println("never printed: " + id);
    }
}
```

```text
Exception in thread "main" java.lang.NumberFormatException: For input string: "abc"
```

The first line of output proves the program started. The second line of the transcript is missing
because the exception happened before it, and the exception names the input it could not use:
`For input string: "abc"`. That message is worth quoting in your own error handling, because "the id
was not a number" and `the id was "abc"` are different amounts of help.

`NumberFormatException` is a subclass of `IllegalArgumentException`, which is a subclass of
`RuntimeException`, so the compiler does not force you to handle it. It should not: a `parseInt` that
fails means the program was handed something it has no sensible interpretation for, and the right
answer is usually to turn it into a message for the user rather than to continue.

What `parseInt` accepts is narrower than people expect, and Solution 2 measures it:

```text
'7'              -> 7
'+7'             -> 7
'007'            -> 7
' 7'             -> rejected: not a note id: ' 7'
'7 '             -> rejected: not a note id: '7 '
''               -> rejected: not a note id: ''
'abc'            -> rejected: not a note id: 'abc'
'999999999999'   -> rejected: not a note id: '999999999999'
```

`+7` and `007` are accepted. ` 7` — with a leading space — is not, and neither is `7 ` with a trailing
one. A string of digits too large for an `int` is rejected too, rather than wrapping. **So a value that
came from a text field must be trimmed and then parsed, and the parse must be allowed to fail with a
message that names the input.** Doing the trim without the parse check is how `NumberFormatException`
reaches a user as a stack trace.

## A closed reader is a runtime error

Resources and exceptions interact, and the interaction is easy to get wrong in a way no compiler
catches:

```java throw
import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

public class ThrowClosed {
    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new StringReader("a\nb\n"));
        reader.close();
        System.out.println("closed the reader, now reading from it");
        System.out.println(reader.readLine());
    }
}
```

```text
Exception in thread "main" java.io.IOException: Stream closed
```

Nothing here is a compile error. `reader.close()` is legal, `reader.readLine()` is legal, and the
mistake only appears when the second one runs: `java.io.IOException: Stream closed`. That is a
checked exception, so it had to be declared, but nothing about the *order* of those two statements is
checked — and a `BufferedReader` wrapping a `StringReader` is a particularly good demonstration,
because the underlying `StringReader` would happily have kept going. It is the wrapper that remembers
it was closed.

This is the argument for try-with-resources rather than calling `close()` by hand. The block form ties
the lifetime of the reader to the scope in which it is used, so there is no window in which the reader
is closed and still in reach.

## Reading a body from standard input

Files have an end and so do pipes, and for a program that reads a note body from a terminal the two
behave the same way: the reader returns `null` when the input stops. That makes "read the body" a loop
with no length in it:

```sh run
cat > ReadBody.java <<'JAVA'
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class ReadBody {
    static List<String> readAll(BufferedReader in) throws IOException {
        List<String> lines = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            lines.add(line);
        }
        return lines;
    }

    public static void main(String[] args) throws IOException {
        List<String> lines = readAll(new BufferedReader(new InputStreamReader(System.in)));
        System.out.println("title     = " + args[0]);
        System.out.println("lines     = " + lines.size());
        for (String line : lines) {
            System.out.println("  | '" + line + "'");
        }
        System.out.println("body      = " + String.join("\n", lines).length() + " character(s)");
    }
}
JAVA

javac -Xlint:all -Werror --release 21 ReadBody.java
printf 'milk and eggs\nbread\n\n' | java -cp . ReadBody Groceries
echo "  -> exit $?"
```

```text
title     = Groceries
lines     = 3
  | 'milk and eggs'
  | 'bread'
  | ''
body      = 20 character(s)
  -> exit 0
```

The shell block feeds the program with `printf` and reads what it printed. The three lines of the body
arrived as three lines — including the third, which is empty — and the character count is `20`, because
the body is `milk and eggs` plus `bread` plus the empty line, joined by newlines.

Note what the program does **not** do: it does not ask how long the input is, and it does not read
twice. It reads until `null` and keeps what it got. That is the only shape that works for a pipe,
because a pipe has no length until it is over.

:::pitfall
**`line.isEmpty()` is not how you detect the end of a stream.** Look again at the `lines` block: the
second line of that input was `''`. A loop written as `while (!(line = reader.readLine()).isEmpty())`
would have stopped there and silently discarded everything after the blank line — one line of output
instead of three, no exception, no warning. The end of a stream is `null` and nothing else. A blank
line is data.
:::

## Quill reads its body from standard input

Chapter 20's `add` took the body as a third argument, which meant a body could never contain a space
without quoting it, and could never be longer than one shell argument. Reading from standard input
fixes both, and it is the change this chapter makes to the project:

```java run-files
// ===== Main.java =====

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class Main {
    static final int OK = 0;
    static final int UNKNOWN = 2;
    static final int MISSING_ARG = 3;
    static final int IO_FAILURE = 4;
    static final int TOO_MANY_LINES = 5;

    static final String USAGE = """
            quill - a command-line vault

            usage:
              quill                        show this help
              quill add <title>            add a note; the body is read from standard input
              quill list                   list every note
            """;

    public static void main(String[] args) {
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        int code = run(args, Path.of("vault"), in, System.out, System.err);
        System.out.flush();
        System.err.flush();
        if (code != OK) {
            System.exit(code);
        }
    }

    static int run(String[] args, Path home, BufferedReader in, PrintStream out, PrintStream err) {
        if (args.length == 0) {
            out.print(USAGE);
            return OK;
        }
        Vault vault = new Vault(home);
        try {
            return switch (args[0]) {
                case "help" -> {
                    out.print(USAGE);
                    yield OK;
                }
                case "list" -> {
                    list(vault, out);
                    yield OK;
                }
                case "add" -> args.length >= 2
                        ? add(vault, args[1], in, out, err)
                        : missing(err, "add <title>");
                default -> unknown(err, args[0]);
            };
        } catch (IOException e) {
            err.println("quill: " + e.getMessage());
            return IO_FAILURE;
        }
    }

    private static void list(Vault vault, PrintStream out) throws IOException {
        List<Note> notes = vault.read();
        if (notes.isEmpty()) {
            out.println("no notes yet");
            return;
        }
        for (Note note : notes) {
            out.println("#" + note.id() + "  " + note.title() + "  " + note.body());
        }
    }

    private static int add(Vault vault, String title, BufferedReader in, PrintStream out,
            PrintStream err) throws IOException {
        List<String> lines = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            lines.add(line);
        }
        if (lines.size() > 1) {
            err.println("quill: the body must be a single line (" + lines.size() + " lines read)");
            return TOO_MANY_LINES;
        }
        String body = lines.isEmpty() ? "" : lines.get(0);
        Note note = new Note(vault.nextId(), title, body);
        vault.append(note);
        out.println("added #" + note.id() + " " + note.title()
                + " (" + body.length() + " character(s))");
        return OK;
    }

    private static int missing(PrintStream err, String form) {
        err.println("quill: missing argument; usage: quill " + form);
        return MISSING_ARG;
    }

    private static int unknown(PrintStream err, String command) {
        err.println("quill: unknown command '" + command + "'");
        return UNKNOWN;
    }
}

// ===== Note.java =====

public record Note(int id, String title, String body) {
    static final String SEP = "\t";

    String render() {
        return id + SEP + title + SEP + body;
    }

    static Note parse(String line) {
        String[] parts = line.split(SEP, 3);
        if (parts.length != 3) {
            throw new IllegalArgumentException("not a note line: " + line);
        }
        return new Note(Integer.parseInt(parts[0]), parts[1], parts[2]);
    }
}

// ===== Vault.java =====

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

public class Vault {
    static final String FILE = "notes.tsv";

    private final Path home;

    Vault(Path home) {
        this.home = home;
    }

    Path file() {
        return home.resolve(FILE);
    }

    List<Note> read() throws IOException {
        if (!Files.exists(file())) {
            return List.of();
        }
        List<Note> notes = new ArrayList<>();
        for (String line : Files.readAllLines(file(), StandardCharsets.UTF_8)) {
            if (!line.isBlank()) {
                notes.add(Note.parse(line));
            }
        }
        return notes;
    }

    int nextId() throws IOException {
        int highest = 0;
        for (Note note : read()) {
            highest = Math.max(highest, note.id());
        }
        return highest + 1;
    }

    void append(Note note) throws IOException {
        Files.createDirectories(home);
        Files.writeString(file(), note.render() + "\n", StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }
}
```

```text
quill - a command-line vault

usage:
  quill                        show this help
  quill add <title>            add a note; the body is read from standard input
  quill list                   list every note
```

The `add` arm now takes a reader instead of a body, and the `add` method reads to `null` and decides
what to do with what it got. There is a new exit code, `5`, for a body it cannot represent: the
format from Chapter 20 is one note per line, so a body containing a newline would break the file. For
now the program refuses rather than corrupts, and Chapter 22 replaces the format so the refusal can go
away.

Running it shows the whole thing working, including the refusal:

```sh run-project
quill() {
  java -cp out Main "$@" 2>&1
  echo "  -> exit $?"
}

say() {
  printf '%s\n' "$1"
}

say '$ printf "milk and eggs\n" | quill add Groceries'
printf 'milk and eggs\n' | quill add Groceries
echo
say '$ printf "bread\nand cheese\n" | quill add Shopping'
printf 'bread\nand cheese\n' | quill add Shopping
echo
say '$ quill list'
quill list
```

```text
$ printf "milk and eggs\n" | quill add Groceries
added #1 Groceries (13 character(s))
  -> exit 0

$ printf "bread\nand cheese\n" | quill add Shopping
quill: the body must be a single line (2 lines read)
  -> exit 5

$ quill list
#1  Groceries  milk and eggs
  -> exit 0
```

Three invocations, and each one is a claim the program makes about itself. A one-line body is stored
and the confirmation says how many characters were kept. A two-line body is refused with the count of
lines it read — `2 lines read` is more useful than `invalid body`, because it tells the user what the
program saw. And `list` prints the one note that survived.

The `|` in the transcript is a shell pipe: the output of `printf` becomes the standard input of
`quill`, which is exactly the situation `readLine` returning `null` at the end is designed for.

:::scenario The export that arrived with an invisible character

A user moves their vault to a new machine and exports it from a tool that writes Windows line endings
— every line ends `\r\n` instead of `\n`. On the new machine, `quill list` prints the notes with a
stray character at the end of every body, and `quill show 2` prints a body that does not compare equal
to the one the user typed.

:::solution
The first question is *where* the `\r` got in, and the answer is the interesting part, because the same
program handles the same file correctly or incorrectly depending on which method it uses:

```java run
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class Scenario {
    static void show(String line) {
        String body = line.split("\t", 3)[2];
        System.out.printf("body='%s' length=%d endsWithCR=%b%n",
                body.replace("\r", "\\r"), body.length(), body.endsWith("\r"));
    }

    public static void main(String[] args) throws Exception {
        Path file = Path.of("exported.tsv");
        Files.writeString(file, "1\tGroceries\tmilk and eggs\r\n2\tReading\tchapter 21\r\n",
                StandardCharsets.UTF_8);

        System.out.println("-- Files.readAllLines --");
        for (String line : Files.readAllLines(file, StandardCharsets.UTF_8)) {
            show(line);
        }

        System.out.println();
        System.out.println("-- Files.readString and split --");
        for (String line : Files.readString(file, StandardCharsets.UTF_8).split("\n")) {
            if (!line.isEmpty()) {
                show(line);
            }
        }
    }
}
```

```text
-- Files.readAllLines --
body='milk and eggs' length=13 endsWithCR=false
body='chapter 21' length=10 endsWithCR=false

-- Files.readString and split --
body='milk and eggs\r' length=14 endsWithCR=true
body='chapter 21\r' length=11 endsWithCR=true
```

`Files.readAllLines` strips the line terminator, whatever it is, so it returns `milk and eggs` and the
carriage return never reaches the note. `Files.readString` followed by `split("\n")` splits on one
specific character and returns `milk and eggs\r` — length 14 instead of 13 — because the `\r` is not
part of the `\n` it was told to split on.

Both methods read the same bytes. One of them leaves an invisible character inside a field, and the
result is a body that looks right in a terminal and fails an equality check, because `\r` is a
character like any other and `equals` does not ignore it.

The fix belongs at the boundary, in `Note.parse`, and it is the same shape as the tab fix from Chapter
20: normalise the input before you split it. Solution 4 writes it, and it strips *every* trailing
carriage return rather than one, because a file that has been through two tools can have two.

**The general rule: whichever method you use to split lines, know whether it strips the terminator.**
`readLine` and `readAllLines` do; `split("\n")` does not. A file that came from another operating
system is the case that finds out which one you used.
:::

## Solutions

### 1. Three ways past the `nextInt` trap

The trap is that `nextInt()` leaves the line terminator behind. There are three fixes and they are not
equally good:

```java run
import java.util.Scanner;

public class Sol1 {
    static final String INPUT = "42\nAda Lovelace\n";

    public static void main(String[] args) {
        System.out.println("-- nextInt() then nextLine() --");
        Scanner a = new Scanner(INPUT);
        int n1 = a.nextInt();
        String s1 = a.nextLine();
        System.out.println("int  = " + n1);
        System.out.println("line = '" + s1 + "'");

        System.out.println();
        System.out.println("-- nextInt() then a second nextLine() --");
        Scanner b = new Scanner(INPUT);
        int n2 = b.nextInt();
        b.nextLine();
        String s2 = b.nextLine();
        System.out.println("int  = " + n2);
        System.out.println("line = '" + s2 + "'");

        System.out.println();
        System.out.println("-- nextLine() and parse --");
        Scanner c = new Scanner(INPUT);
        int n3 = Integer.parseInt(c.nextLine());
        String s3 = c.nextLine();
        System.out.println("int  = " + n3);
        System.out.println("line = '" + s3 + "'");
    }
}
```

```text
-- nextInt() then nextLine() --
int  = 42
line = ''

-- nextInt() then a second nextLine() --
int  = 42
line = 'Ada Lovelace'

-- nextLine() and parse --
int  = 42
line = 'Ada Lovelace'
```

The first is the bug, and it is in the transcript: `line = ''`. The second consumes the remainder of
the line the number was on, and then `nextLine()` returns the name. The third never calls `nextInt()`
at all — it reads a line and parses it, so there is no leftover to be confused by.

Prefer the third. It has one rule instead of two, and the rule is "a line is a line". The second
approach works and is what you will see in older code; it fails the moment the input has two numbers
on one line, because you then have to know how many `nextLine()` calls to make, and that number
depends on the data.

### 2. Parse, and say what you could not parse

`parseId` is four lines and it changes the failure from a stack trace into a message:

```java run
public class Sol2 {
    static int parseId(String raw) {
        try {
            return Integer.parseInt(raw);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("not a note id: '" + raw + "'");
        }
    }

    public static void main(String[] args) {
        String[] inputs = {"7", "+7", "007", " 7", "7 ", "", "abc", "999999999999"};

        int accepted = 0;
        for (String raw : inputs) {
            try {
                int id = parseId(raw);
                accepted++;
                System.out.printf("%-16s -> %d%n", "'" + raw + "'", id);
            } catch (IllegalArgumentException e) {
                System.out.printf("%-16s -> rejected: %s%n", "'" + raw + "'", e.getMessage());
            }
        }

        System.out.println();
        System.out.println("accepted " + accepted + " of " + inputs.length);
    }
}
```

```text
'7'              -> 7
'+7'             -> 7
'007'            -> 7
' 7'             -> rejected: not a note id: ' 7'
'7 '             -> rejected: not a note id: '7 '
''               -> rejected: not a note id: ''
'abc'            -> rejected: not a note id: 'abc'
'999999999999'   -> rejected: not a note id: '999999999999'

accepted 3 of 8
```

`accepted 3 of 8`. The three accepted inputs are the ones a user would actually type for a note id.
The five rejections are more interesting: `' 7'` and `'7 '` are rejected because `parseInt` does not
trim, `''` is rejected because an empty string is not a number, and `'999999999999'` is rejected
because it does not fit in an `int` — the exception for that case is the same `NumberFormatException`,
which is why the message has to name the input rather than the reason.

The message names the offending text, `' 7'`, with the space visible between the quotes. That matters
more than it sounds: the user's first reaction to "not a note id" is to look at their input and see
`7`, which is a valid id. Showing the whitespace is what ends the conversation.

### 3. Bound a read you did not write

Reading to `null` is correct and it is also unbounded. If the input is a pipe from another program
that never ends, the loop never ends, and the list grows until memory runs out:

```java run
import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.List;

public class Sol3 {
    static final int MAX_LINES = 3;

    static BufferedReader reader(String text) {
        return new BufferedReader(new StringReader(text));
    }

    static List<String> readAtMost(BufferedReader in, int limit) throws IOException {
        List<String> lines = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            if (lines.size() == limit) {
                throw new IllegalStateException("more than " + limit + " lines");
            }
            lines.add(line);
        }
        return lines;
    }

    public static void main(String[] args) throws IOException {
        try {
            System.out.println("three lines: " + readAtMost(reader("a\nb\nc\n"), MAX_LINES));
        } catch (IllegalStateException e) {
            System.out.println("three lines: " + e.getMessage());
        }

        try {
            System.out.println("four lines:  " + readAtMost(reader("a\nb\nc\nd\n"), MAX_LINES));
        } catch (IllegalStateException e) {
            System.out.println("four lines:  " + e.getMessage());
        }

        System.out.println();
        System.out.println("the limit is checked before the line is added, so at most 3 means 3");
    }
}
```

```text
three lines: [a, b, c]
four lines:  more than 3 lines

the limit is checked before the line is added, so at most 3 means 3
```

`three lines: [a, b, c]` and `four lines:  more than 3 lines`. The check is placed *before* the line is
added, so "at most three" means three rather than four — an off-by-one that a test written from the
happy path would not catch, because the happy path has three lines.

The point is not the number. It is that a read loop has no natural bound, so if you want one you have
to write it, and the place to write it is the loop. The same shape defends against a body that is one
line but ten megabytes.

### 4. Strip the terminator your splitter left behind

`readLine` strips it, `split("\n")` does not, so if any path through the program uses `split`, the
normalisation has to happen anyway:

```java run
public class Sol4 {
    static String stripCarriageReturn(String line) {
        int end = line.length();
        while (end > 0 && line.charAt(end - 1) == '\r') {
            end--;
        }
        return line.substring(0, end);
    }

    public static void main(String[] args) {
        String[] lines = {
            "1\tGroceries\tmilk and eggs\r",
            "2\tReading\tchapter 21",
            "3\tOdd\ttwo\r\r",
        };

        for (String raw : lines) {
            String clean = stripCarriageReturn(raw);
            String body = clean.split("\t", 3)[2];
            System.out.printf("%-40s body='%s' length=%d%n",
                    "'" + raw.replace("\t", "\\t").replace("\r", "\\r") + "'",
                    body, body.length());
        }

        System.out.println();
        System.out.println("every body is now free of a carriage return");
    }
}
```

```text
'1\tGroceries\tmilk and eggs\r'          body='milk and eggs' length=13
'2\tReading\tchapter 21'                 body='chapter 21' length=10
'3\tOdd\ttwo\r\r'                        body='two' length=3

every body is now free of a carriage return
```

Every body is free of a carriage return, including the third case, which had two of them. The loop
strips from the end rather than replacing every `\r` in the string, because a carriage return in the
*middle* of a body is legitimate data — it is only the ones at the end that came from the line
terminator.

That distinction is the difference between normalising and mangling. `replace("\r", "")` would have
passed the same three test cases and quietly destroyed any body that genuinely contained one, which is
why the test cases include a body with two trailing returns and the implementation is written to
count from the end.

## Key takeaways

- `readLine()` returns `null` at the end of a stream and `""` for a blank line. `null` is the only
  end-of-stream signal; a blank line is data.
- A stream is consumed once. Reading to `null` exhausts it, and a second pass gets nothing. A reader
  is not a collection and is deliberately not `Iterable`.
- `readLine` strips `\n`, `\r` and `\r\n`. `split("\n")` strips only the `\n`, which is why a file
  from Windows can leave a `\r` inside a field.
- `Scanner.nextInt()` does not consume the rest of the line. Either discard the remainder with a
  `nextLine()`, or read lines and parse them yourself.
- `Integer.parseInt` accepts `+7` and `007`, rejects `' 7'`, `'7 '`, `''` and anything too large for an
  `int`. Trim first, then parse, and let the failure carry a message naming the input.
- A closed reader throws `IOException: Stream closed` when you read from it — a runtime error with no
  compile-time warning. Try-with-resources removes the window in which it can happen.
- Read to `null` for a pipe or a terminal; there is no length to ask for. Put a bound in the loop if
  the input is not yours.
- Normalise at the boundary. Strip the terminator a splitter left behind *before* the value reaches
  your format, and strip only the trailing ones.

## Practice

- [ ] Write a method that reads a file two ways — `Files.readAllLines` and
      `Files.readString(...).split("\n")` — on the same CRLF file, and print the length of every line
      from each. Explain the difference in one sentence.
- [ ] Write `readAtMost` with a limit, then feed it a stream that exceeds the limit and confirm it
      refuses rather than truncates. Then decide which of those two behaviours a note body should have
      and write down why.
- [ ] Take the `Scanner` example and rewrite it to read two integers and a name from one line of
      input, using only `nextLine()`. Then rewrite it with `nextInt()` and count how many `nextLine()`
      calls you need.
- [ ] Add a `quill import <file>` command that reads a TSV file and appends every valid line, reporting
      the number it added and the number it rejected. Decide what to do with a line that has two fields
      instead of three.
- [ ] Make `parseId` reject an id of `0` and a negative id with a message that says which rule was
      broken, and write the four cases that prove it.
- [ ] Change the `add` command so a body longer than 200 characters is refused with a message naming
      the limit and the actual length. Then decide whether the limit belongs in `Main` or in `Note`.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `readAllLines` returns 13 and 10 characters; `split("\n")` returns 14 and 11. The extra character is
   the `\r`, which `split` keeps because it was told to split on `\n` and the `\r` is not a `\n`. One
   sentence: *the two methods disagree about whether the line terminator is part of the line.*
2. The check goes before `lines.add(line)`, as in Solution 3. Refusing is right for a note body: a
   truncated body is a body the user did not write, and silently storing half of what someone typed is
   worse than telling them it is too long. Truncation is the right answer only when the data is
   genuinely disposable, such as a log line.
3. With `nextLine()` only: read one line, `split("\\s+", 3)`, parse the first two fields. With
   `nextInt()` you need **three** `nextLine()` calls in the right places — one to consume the remainder
   of the line the second integer was on, and one to read the name — and the exact count changes if the
   input puts the name on a different line. That fragility is the argument for the first version.
4. Read the file with `Files.readAllLines`, loop, and count `added` and `rejected` separately. A line
   with two fields is rejected and reported, because a two-field line means the file was written by
   something that does not agree with your format, and guessing which field is missing would invent
   data. Print both counts and exit non-zero if `rejected` is not zero, so a script can tell.
5. `if (id <= 0) throw new IllegalArgumentException("id must be positive: " + id);` before the
   `parseInt`, or after it on the parsed value — after is better, because `"-3"` parses and then fails
   the range check with the number visible. The four cases are `"0"`, `"-3"`, `"abc"` and `"4"`.
6. `Main`, not `Note`. The format's job is to say which strings it can represent, and a 200-character
   limit is not a fact about TSV — it is a policy about this command. Putting it in `Note` would make
   the format lie about what it can hold, and the next thing to store a note (an importer, a test)
   would inherit a limit it does not have.
