---
chapter: 22
part: 3
title: Persistence — Files, Serialization and a Real Format
summary: Replace Quill's one-line-per-note format with one that can hold any text at all, decide what to do about character encodings and versions, and write the file so that a crash cannot leave it half-finished.
minutes: 60
tags: [persistence, file format, escaping, serialization, encoding, atomic writes]
---

Chapter 20 left Quill with a format that worked and could not hold a newline. Chapter 21 left it
refusing multi-line bodies rather than corrupting them, which was the right call and not a solution.
This chapter fixes the format properly. Along the way it answers three questions every program that
writes a file eventually has to answer — how do I represent text that contains my separator, what do I
do about character encoding, and how do I stop a crash from leaving the file unreadable — and it
answers a fourth that Java poses specifically: the language ships a serialization mechanism, and this
chapter explains why this project does not use it.

## A format has to be able to hold every body

The old rule was "a field may not contain a tab", and it had a hole the size of the user's clipboard.
The new rule is better: **a field may not contain a tab, because a tab in a field is written as the
two characters `\t`.** That is escaping, and it turns a restriction into a representation.

Four characters need it, and the fourth is the one people forget:

| character | written as | why |
|---|---|---|
| `\` | `\\` | or an escape could never be read back unambiguously |
| tab | `\t` | the field separator |
| newline | `\n` | the record separator |
| carriage return | `\r` | the other half of a line ending from Windows |

The backslash has to be escaped first, and *that* is the whole difficulty:

```java run
public class Escaping {
    static String wrongOrder(String field) {
        return field.replace("\n", "\\n").replace("\\", "\\\\");
    }

    static String rightOrder(String field) {
        return field.replace("\\", "\\\\").replace("\n", "\\n");
    }

    static String unescape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            char c = field.charAt(i);
            if (c != '\\') {
                out.append(c);
                continue;
            }
            i++;
            switch (field.charAt(i)) {
                case '\\' -> out.append('\\');
                case 'n' -> out.append('\n');
                case 't' -> out.append('\t');
                default -> throw new IllegalArgumentException("unknown escape");
            }
        }
        return out.toString();
    }

    static String show(String s) {
        return "'" + s.replace("\\", "\\\\").replace("\n", "\\n")
                .replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String[] fields = {"two\nlines", "back\\slash"};

        for (String field : fields) {
            System.out.println("field   = " + show(field));
            for (String name : new String[] {"wrongOrder", "rightOrder"}) {
                String stored = name.equals("wrongOrder")
                        ? wrongOrder(field)
                        : rightOrder(field);
                String back = unescape(stored);
                System.out.printf("  %-10s stored %-20s back %-20s same=%b%n",
                        name, stored, show(back), back.equals(field));
            }
        }
    }
}
```

```text
field   = 'two\nlines'
  wrongOrder stored two\\nlines          back 'two\\nlines'        same=false
  rightOrder stored two\nlines           back 'two\nlines'         same=true
field   = 'back\\slash'
  wrongOrder stored back\\slash          back 'back\\slash'        same=true
  rightOrder stored back\\slash          back 'back\\slash'        same=true
```

Two implementations, the same two inputs, and only one of them is correct.

`wrongOrder` replaces the newline first and the backslash second. On `two\nlines` it turns the newline
into a backslash and an `n` — and then doubles that backslash, because it has not finished escaping
yet. The stored form has two backslashes, and reading it back gives a literal `\n` **as two characters**
rather than a newline. `same=false`.

`rightOrder` escapes the backslash first, so when it later introduces a backslash as part of `\n`,
there is no second pass to double it. `same=true`.

Now look at the second field. `back\slash` has no newline in it, so **both implementations are
correct** — `same=true` twice. That is the trap in its purest form: an escape routine that is wrong
only for newlines passes every test written with backslashes, and the bug ships. This is why the test
suite in the next section is a list of awkward inputs rather than one comfortable example.

## The round-trip property is the test

"Every note survives being written and read" is a property, not an example, so it is tested as one:

```java run-files
// ===== Note.java =====

public record Note(int id, String title, String body) {
    static final String SEP = "\t";

    public Note {
        if (id <= 0) {
            throw new IllegalArgumentException("id must be positive: " + id);
        }
    }

    String render() {
        return id + SEP + escape(title) + SEP + escape(body);
    }

    static Note parse(String line) {
        String[] parts = line.split(SEP, 3);
        if (parts.length != 3) {
            throw new IllegalArgumentException("not a note line: " + line);
        }
        return new Note(Integer.parseInt(parts[0]), unescape(parts[1]), unescape(parts[2]));
    }

    static String escape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            switch (field.charAt(i)) {
                case '\\' -> out.append("\\\\");
                case '\t' -> out.append("\\t");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                default -> out.append(field.charAt(i));
            }
        }
        return out.toString();
    }

    static String unescape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            char c = field.charAt(i);
            if (c != '\\') {
                out.append(c);
                continue;
            }
            i++;
            if (i == field.length()) {
                throw new IllegalArgumentException("trailing backslash in field");
            }
            switch (field.charAt(i)) {
                case '\\' -> out.append('\\');
                case 't' -> out.append('\t');
                case 'n' -> out.append('\n');
                case 'r' -> out.append('\r');
                default -> throw new IllegalArgumentException(
                        "unknown escape: \\" + field.charAt(i));
            }
        }
        return out.toString();
    }
}

// ===== RoundTrip.java =====

public class RoundTrip {
    static String show(String s) {
        return "'" + s.replace("\\", "\\\\").replace("\n", "\\n")
                .replace("\t", "\\t").replace("\r", "\\r") + "'";
    }

    public static void main(String[] args) {
        String[] nasty = {
            "",
            "plain",
            "two\nlines",
            "a\tb",
            "back\\slash",
            "already \\n escaped",
            "\\",
            "\r\n",
            "trailing space ",
        };

        int passed = 0;
        for (String field : nasty) {
            Note note = new Note(1, field, field);
            String stored = note.render();
            Note back = Note.parse(stored);
            boolean same = back.equals(note);
            if (same) {
                passed++;
            }
            System.out.printf("%-24s stored %-34s %s%n",
                    show(field), show(stored), same ? "ok" : "LOST");
        }

        System.out.println();
        System.out.println("round-tripped " + passed + " of " + nasty.length);
    }
}
```

```text
''                       stored '1\t\t'                            ok
'plain'                  stored '1\tplain\tplain'                  ok
'two\nlines'             stored '1\ttwo\\nlines\ttwo\\nlines'      ok
'a\tb'                   stored '1\ta\\tb\ta\\tb'                  ok
'back\\slash'            stored '1\tback\\\\slash\tback\\\\slash'  ok
'already \\n escaped'    stored '1\talready \\\\n escaped\talready \\\\n escaped' ok
'\\'                     stored '1\t\\\\\t\\\\'                    ok
'\r\n'                   stored '1\t\\r\\n\t\\r\\n'                ok
'trailing space '        stored '1\ttrailing space \ttrailing space ' ok

round-tripped 9 of 9
```

Nine inputs, nine `ok`, and the list is chosen rather than typed at random. The empty string. A tab.
A newline. A lone backslash, which is the input that breaks a naive unescaper. The four characters
`already \n escaped`, which is what a user gets if they type the escape sequence literally — the
round trip must keep it as four characters and not turn it into a newline. `\r\n`. And a string with a
**trailing space**, which is the input that breaks a format that trims.

`round-tripped 9 of 9` is the claim, and it is worth noticing what it would take to falsify it: change
`escape` to use `wrongOrder` and the newline case reports `LOST`. The property test is not decoration;
it is the specification of the format, executable.

One detail in `Note` is easy to miss and produces a confusing error. The compact constructor is
declared `public`:

```java
public Note {
    if (id <= 0) {
        throw new IllegalArgumentException("id must be positive: " + id);
    }
}
```

A record's canonical constructor has the same access as the record, so for a `public record` it is
`public`. A compact constructor written without a modifier is package-private, which is *narrower*,
and javac rejects the whole file with `invalid canonical constructor in record Note`. If your record is
public, its compact constructor must say so too.

:::tip
Escape the backslash **first**, then everything else, and write one function that does both directions
next to each other. A format is a pair of functions, and the bug above is a bug about their order — it
is invisible if they live in different files.
:::

## Java will serialize your objects, and you should say no

Java has a built-in way to write an object to bytes: implement `java.io.Serializable` and hand the
object to an `ObjectOutputStream`. It works, and it is a trap.

```java run
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.nio.charset.StandardCharsets;

public class SerialBlob {
    record Person(String name, int age) implements java.io.Serializable {}

    public static void main(String[] args) throws Exception {
        Person before = new Person("Ada", 36);

        ByteArrayOutputStream sink = new ByteArrayOutputStream();
        try (ObjectOutputStream out = new ObjectOutputStream(sink)) {
            out.writeObject(before);
        }
        byte[] blob = sink.toByteArray();

        System.out.println("bytes           = " + blob.length);
        System.out.printf("magic           = %02x%02x%02x%02x%n",
                blob[0] & 0xff, blob[1] & 0xff, blob[2] & 0xff, blob[3] & 0xff);
        System.out.println("names the class = "
                + new String(blob, StandardCharsets.ISO_8859_1).contains("SerialBlob$Person"));

        Person after;
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(blob))) {
            after = (Person) in.readObject();
        }
        System.out.println("round trip      = " + after.equals(before));
    }
}
```

```text
bytes           = 82
magic           = aced0005
names the class = true
round trip      = true
```

`round trip = true` — the mechanism does what it says. Now look at the other three lines.

The bytes start with `aced0005`. That is `STREAM_MAGIC` and `STREAM_VERSION`, and everything after it
is a binary encoding of the class structure, the field names and the values. **It is not text.** You
cannot read it, you cannot fix it with an editor, and `cat` on it is useless. The old format's
advantage was that a human could repair a vault with `vi`; this gives that up.

`names the class = true` is the second problem. The bytes contain the fully-qualified name of the class
that produced them, so the file is coupled to your code. Rename the class, move it to another package,
or change a field and the serialized form no longer matches — Java detects this with a computed
`serialVersionUID` and refuses to read the file with `InvalidClassException`. Your data's lifetime is
now the same as your class's lifetime, which is the opposite of what a persistence format is for.

The third problem is the reason to say no rather than "not yet". **Deserialization of untrusted bytes
is a well-known vulnerability class.** `ObjectInputStream` reconstructs arbitrary objects by running
their constructors and `readObject` methods, so reading a file an attacker can write is close to
executing code an attacker can write. Every security guide that mentions Java serialization says the
same thing: do not use it on data you did not produce.

So Quill writes text, and this chapter writes the escaping by hand. That is more code than
`implements Serializable` — about forty lines — and it buys a file that is readable, repairable,
portable and safe.

:::warning
`Serializable` is not wrong everywhere. It is a reasonable choice for a short-lived cache in a single
program, where the bytes never leave the machine and the class never changes. It is the wrong choice
for anything a user can edit, move between versions, or hand to you.
:::

## Encoding is not optional

A `String` is a sequence of `char` values. A file is a sequence of bytes. `StandardCharsets` is the
bridge, and the bridge is not the identity:

```java run
import java.nio.charset.StandardCharsets;

public class Encoding {
    static int count(byte[] bytes, byte target) {
        int n = 0;
        for (byte b : bytes) {
            if (b == target) {
                n++;
            }
        }
        return n;
    }

    public static void main(String[] args) {
        String body = "café — 咖啡";

        byte[] utf8 = body.getBytes(StandardCharsets.UTF_8);
        byte[] latin1 = body.getBytes(StandardCharsets.ISO_8859_1);

        System.out.println("characters    = " + body.length());
        System.out.println("UTF-8 bytes   = " + utf8.length);
        System.out.println("Latin-1 bytes = " + latin1.length);
        System.out.println("Latin-1 '?'   = " + count(latin1, (byte) '?'));
        System.out.println();
        System.out.println("UTF-8 round trip   = "
                + new String(utf8, StandardCharsets.UTF_8).equals(body));
        System.out.println("Latin-1 round trip = "
                + new String(latin1, StandardCharsets.ISO_8859_1).equals(body));
    }
}
```

```text
characters    = 9
UTF-8 bytes   = 16
Latin-1 bytes = 9
Latin-1 '?'   = 3

UTF-8 round trip   = true
Latin-1 round trip = false
```

`café — 咖啡` is nine characters. In UTF-8 it is sixteen bytes, because `é` takes two and each of the
CJK characters takes three. In Latin-1 it is nine bytes — and `Latin-1 '?' = 3` says why: the em dash
and the two CJK characters **cannot be represented at all**, so `getBytes` replaced each with a
question mark. The bytes are the right length and the text is gone.

That is why `Latin-1 round trip = false` and `UTF-8 round trip = true`. Choosing the wrong charset does
not throw; it silently destroys the characters it cannot represent, and the only way to notice is to
read the data back and compare.

Which is why every file call in Quill names the charset explicitly:

```java
Files.writeString(file, note.render() + "\n", StandardCharsets.UTF_8,
        StandardOpenOption.CREATE, StandardOpenOption.APPEND);
```

`Files.writeString` and `Files.readString` default to UTF-8 and would have been fine without the
argument. The older `FileWriter` and `new PrintWriter(File)` default to **the platform default
charset**, which is UTF-8 on a modern macOS or Linux box and is not on a machine configured otherwise.
Code that relies on the default works on the machine it was written on and corrupts data elsewhere —
and that is the worst kind of bug, because it is invisible until it is expensive. **Name the charset
every time, even when the default happens to be what you want.** The argument is one identifier and it
removes an entire class of environment-dependent failure.

## A file needs a version

The format changed in this chapter, so there are now two kinds of `notes.tsv` in the world: the ones
Chapter 20 wrote, which have no header, and the ones this chapter writes, which do. A reader that
cannot tell them apart will either crash on the first or silently misread the second.

The fix is one line at the top of the file, and a refusal:

```java run
public class Versioned {
    static final String HEADER = "# quill-2";

    static String save(String... bodies) {
        StringBuilder out = new StringBuilder(HEADER).append('\n');
        int id = 1;
        for (String body : bodies) {
            out.append(id++).append('\t').append(body).append('\n');
        }
        return out.toString();
    }

    static int load(String text) {
        String[] lines = text.split("\n", -1);
        if (lines.length == 0 || !lines[0].startsWith("# ")) {
            throw new IllegalArgumentException("not a quill file: no header line");
        }
        String version = lines[0].substring(2);
        if (!version.equals("quill-2")) {
            throw new IllegalArgumentException("unsupported version: " + version);
        }
        int count = 0;
        for (String line : lines) {
            if (!line.isBlank()) {
                count++;
            }
        }
        return count - 1;
    }

    static String show(String s) {
        return "'" + s.replace("\n", "\\n").replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String[] files = {
            save("milk and eggs", "chapter 22"),
            "# quill-1\n1\tmilk\n",
            "1\tmilk\n",
        };

        for (String text : files) {
            try {
                System.out.printf("%-48s -> %d note(s)%n", show(text), load(text));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-48s -> %s%n", show(text), e.getMessage());
            }
        }

        System.out.println();
        System.out.println("a version this build does not understand is refused, not guessed at");
    }
}
```

```text
'# quill-2\n1\tmilk and eggs\n2\tchapter 22\n'   -> 2 note(s)
'# quill-1\n1\tmilk\n'                           -> unsupported version: quill-1
'1\tmilk\n'                                      -> not a quill file: no header line

a version this build does not understand is refused, not guessed at
```

`-> 2 note(s)` for the current format, `-> unsupported version: quill-1` for a file from an older
build, and `-> not a quill file: no header line` for something that is not a vault at all.

The interesting decision is the middle one. `quill-1` is a format this program understands perfectly
well — the escaping is the only difference — and the honest options are to migrate it (Solution 4) or
to refuse it with a message. What is not an option is to guess. **A reader that tries the old format
when the new one fails is a reader that will one day write a file it cannot read back**, because it
will have interpreted some bytes as notes that were never notes.

The header also gives the format somewhere to grow. When Chapter 33 adds a field, the version becomes
`quill-3`, and every build that only understands `quill-2` says so in one sentence instead of
producing a vault with half the fields empty.

## Quill writes the new format

With escaping in place, the restriction from Chapter 21 can go. `Main` no longer counts body lines,
`Vault` writes the header, and `Note` escapes both fields:

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
                        ? add(vault, args[1], in, out)
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

    private static int add(Vault vault, String title, BufferedReader in, PrintStream out)
            throws IOException {
        List<String> lines = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            lines.add(line);
        }
        String body = String.join("\n", lines);
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

    public Note {
        if (id <= 0) {
            throw new IllegalArgumentException("id must be positive: " + id);
        }
    }

    String render() {
        return id + SEP + escape(title) + SEP + escape(body);
    }

    static Note parse(String line) {
        String[] parts = line.split(SEP, 3);
        if (parts.length != 3) {
            throw new IllegalArgumentException("not a note line: " + line);
        }
        return new Note(Integer.parseInt(parts[0]), unescape(parts[1]), unescape(parts[2]));
    }

    static String escape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            switch (field.charAt(i)) {
                case '\\' -> out.append("\\\\");
                case '\t' -> out.append("\\t");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                default -> out.append(field.charAt(i));
            }
        }
        return out.toString();
    }

    static String unescape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            char c = field.charAt(i);
            if (c != '\\') {
                out.append(c);
                continue;
            }
            i++;
            if (i == field.length()) {
                throw new IllegalArgumentException("trailing backslash in field");
            }
            switch (field.charAt(i)) {
                case '\\' -> out.append('\\');
                case 't' -> out.append('\t');
                case 'n' -> out.append('\n');
                case 'r' -> out.append('\r');
                default -> throw new IllegalArgumentException(
                        "unknown escape: \\" + field.charAt(i));
            }
        }
        return out.toString();
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
    static final String HEADER = "# quill-2";

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
        List<String> lines = Files.readAllLines(file(), StandardCharsets.UTF_8);
        if (lines.isEmpty()) {
            return List.of();
        }
        if (!lines.get(0).equals(HEADER)) {
            throw new IOException("unsupported vault header: " + lines.get(0));
        }
        List<Note> notes = new ArrayList<>();
        for (String line : lines.subList(1, lines.size())) {
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
        if (!Files.exists(file())) {
            Files.writeString(file(), HEADER + "\n", StandardCharsets.UTF_8);
        }
        Files.writeString(file(), note.render() + "\n", StandardCharsets.UTF_8,
                StandardOpenOption.APPEND);
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

The `add` method is four lines shorter than it was, because the refusal is gone:

```java
String body = String.join("\n", lines);
```

Joining the lines with a newline and storing that is now correct, because `render` escapes the newline
before it reaches the file. The multi-line body that Chapter 21 had to reject goes in:

```sh run-project
quill() {
  java -cp out Main "$@" 2>&1
  echo "  -> exit $?"
}

say() {
  printf '%s\n' "$1"
}

say '$ printf "milk and eggs\nbread\n" | quill add Groceries'
printf 'milk and eggs\nbread\n' | quill add Groceries
echo
say '$ quill list'
quill list
echo
say '$ cat vault/notes.tsv'
cat vault/notes.tsv
```

```text
$ printf "milk and eggs\nbread\n" | quill add Groceries
added #1 Groceries (19 character(s))
  -> exit 0

$ quill list
#1  Groceries  milk and eggs
bread
  -> exit 0

$ cat vault/notes.tsv
# quill-2
1	Groceries	milk and eggs\nbread
```

Read the three commands in order. `add` reports `19 character(s)` — that is `milk and eggs`, a newline,
and `bread`. `list` prints the note, and the body spans two lines because the newline came back as a
newline. Then `cat` shows the file itself, where the same body is one line containing the two
characters `\` and `n`.

That contrast is the whole idea. The file is line-oriented and always has been; the *fields* are
escaped so that a body can contain anything, and the escaping is what makes the two views agree.

:::scenario The backup that caught the file mid-write

Quill runs on a small server. A nightly job copies `vault/notes.tsv` to a backup directory. One morning
the vault is restored from a backup taken while `quill add` was running, and every note is gone — the
file is zero bytes. The backup job did nothing wrong: it read the file at a moment when the file
really was empty.

:::solution
`Files.writeString(path, text)` does not write the text and then replace the old content. It **truncates
the file to zero bytes first**, and then writes. Between those two moments the file exists and is
empty, and any reader — a backup job, a second copy of `quill`, a text editor — sees an empty vault.

The window is small and it is real, and the size of the window is not the point: the failure is not
proportional to the risk, because a backup that catches it preserves the empty state.

The fix is to never write the live file at all. Write the new content to a temporary file in the same
directory, then **move** it into place:

```java run
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class Scenario {
    static long size(Path p) throws Exception {
        return Files.size(p);
    }

    static long lines(Path p) throws Exception {
        return Files.readAllLines(p, StandardCharsets.UTF_8).size();
    }

    public static void main(String[] args) throws Exception {
        Path dir = Path.of("scenario-vault");
        Path live = dir.resolve("notes.tsv");
        Path temp = dir.resolve("notes.tsv.tmp");
        Files.createDirectories(dir);

        String before = "# quill-2\n1\tGroceries\tmilk and eggs\n";
        String after = before + "2\tReading\tchapter 22\n";
        Files.writeString(live, before, StandardCharsets.UTF_8);

        System.out.println("before the append     : " + size(live) + " bytes, "
                + lines(live) + " line(s)");

        Files.writeString(live, "", StandardCharsets.UTF_8);
        System.out.println("mid-write, truncated  : " + size(live) + " bytes, "
                + lines(live) + " line(s)");

        Files.writeString(temp, after, StandardCharsets.UTF_8);
        Files.move(temp, live, StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
        System.out.println("after the atomic move : " + size(live) + " bytes, "
                + lines(live) + " line(s)");
        System.out.println("temp file left behind : " + Files.exists(temp));
    }
}
```

```text
before the append     : 36 bytes, 2 line(s)
mid-write, truncated  : 0 bytes, 0 line(s)
after the atomic move : 57 bytes, 3 line(s)
temp file left behind : false
```

`mid-write, truncated : 0 bytes, 0 line(s)` is the state the in-place write passes through. The atomic
move has no such state: the live file is either the old content or the new content, and a reader that
opens it always gets one of the two. `temp file left behind : false` because a move does not leave a
copy.

`ATOMIC_MOVE` is the part that matters and it is worth knowing what it promises. It guarantees that the
rename is atomic **on the same filesystem**, so the temporary file must be created in the same
directory as the target — `resolveSibling` rather than `Files.createTempFile`, whose default directory
is somewhere else entirely.

The same reasoning applies to `Vault.append`. Appending is already atomic enough for a single writer,
because `O_APPEND` writes at the end and a reader sees either the line or not. What is not safe is
rewriting the whole file in place, which is what deleting a note will need in Chapter 23.
:::

## Solutions

### 1. The case Chapter 20 had to refuse

Chapter 20's `Note` rejected a tab in the title, and the scenario that motivated it was a title pasted
out of a spreadsheet. With escaping, the ban is unnecessary:

```java run-files
// ===== Note.java =====

public record Note(int id, String title, String body) {
    static final String SEP = "\t";

    public Note {
        if (id <= 0) {
            throw new IllegalArgumentException("id must be positive: " + id);
        }
    }

    String render() {
        return id + SEP + escape(title) + SEP + escape(body);
    }

    static Note parse(String line) {
        String[] parts = line.split(SEP, 3);
        if (parts.length != 3) {
            throw new IllegalArgumentException("not a note line: " + line);
        }
        return new Note(Integer.parseInt(parts[0]), unescape(parts[1]), unescape(parts[2]));
    }

    static String escape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            switch (field.charAt(i)) {
                case '\\' -> out.append("\\\\");
                case '\t' -> out.append("\\t");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                default -> out.append(field.charAt(i));
            }
        }
        return out.toString();
    }

    static String unescape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            char c = field.charAt(i);
            if (c != '\\') {
                out.append(c);
                continue;
            }
            i++;
            if (i == field.length()) {
                throw new IllegalArgumentException("trailing backslash in field");
            }
            switch (field.charAt(i)) {
                case '\\' -> out.append('\\');
                case 't' -> out.append('\t');
                case 'n' -> out.append('\n');
                case 'r' -> out.append('\r');
                default -> throw new IllegalArgumentException(
                        "unknown escape: \\" + field.charAt(i));
            }
        }
        return out.toString();
    }
}

// ===== Sol1.java =====

public class Sol1 {
    static String show(String s) {
        return "'" + s.replace("\\", "\\\\").replace("\n", "\\n")
                .replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String[] titles = {"Groceries", "Groceries\tand more", "Two\nlines", "back\\slash"};

        int ok = 0;
        for (String title : titles) {
            Note note = new Note(1, title, "milk and eggs");
            Note back = Note.parse(note.render());
            boolean same = back.equals(note);
            if (same) {
                ok++;
            }
            System.out.printf("%-24s stored %-32s %s%n",
                    show(title), show(note.render()), same ? "ok" : "LOST");
        }

        System.out.println();
        System.out.println("round-tripped " + ok + " of " + titles.length);
        System.out.println("chapter 20 had to reject the second title; the format now holds it");
    }
}
```

```text
'Groceries'              stored '1\tGroceries\tmilk and eggs'    ok
'Groceries\tand more'    stored '1\tGroceries\\tand more\tmilk and eggs' ok
'Two\nlines'             stored '1\tTwo\\nlines\tmilk and eggs'  ok
'back\\slash'            stored '1\tback\\\\slash\tmilk and eggs' ok

round-tripped 4 of 4
chapter 20 had to reject the second title; the format now holds it
```

`round-tripped 4 of 4`, including `'Groceries\tand more'`, which is the exact input that Chapter 20's
constructor threw an exception on. The stored form shows why: the tab is two characters, `\` and `t`,
so it can no longer be confused with the separator.

This is the difference between validation and representation, and it is worth being able to say out
loud. Validation says *"this value is not allowed"*. Representation says *"this value is allowed and
here is how I write it down"*. A format that can represent everything needs less validation, and every
restriction it does not need is a restriction your users will eventually hit.

### 2. Create the header once, not every time

`Vault.append` needs a header on a new file and must not add a second one to an existing file:

```java run
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class Sol2 {
    static final String HEADER = "# quill-2";

    static void ensureHeader(Path file) throws IOException {
        if (Files.exists(file) && !Files.readString(file, StandardCharsets.UTF_8).isEmpty()) {
            return;
        }
        Files.writeString(file, HEADER + "\n", StandardCharsets.UTF_8);
    }

    static long lines(Path p) throws IOException {
        return Files.readAllLines(p, StandardCharsets.UTF_8).size();
    }

    public static void main(String[] args) throws IOException {
        Path file = Path.of("sol2-vault", "notes.tsv");
        Files.createDirectories(file.getParent());

        ensureHeader(file);
        System.out.println("after the first call  = " + lines(file) + " line(s)");
        ensureHeader(file);
        System.out.println("after the second call = " + lines(file) + " line(s)");
        System.out.println("header                = "
                + Files.readAllLines(file, StandardCharsets.UTF_8).get(0));
    }
}
```

```text
after the first call  = 1 line(s)
after the second call = 1 line(s)
header                = # quill-2
```

`after the first call = 1 line(s)` and `after the second call = 1 line(s)`. The method is **idempotent**
— calling it twice has the same effect as calling it once — and that property is what makes it safe to
call at the top of `append` on every write rather than only on the first.

The check is on the *file*, not on a flag in memory, which is the part that matters. A `boolean
headerWritten` field would be true after a restart that found no file, and false after a restart that
found one. **Ask the file what it contains; do not remember.**

### 3. Replace the file, do not truncate it

The scenario's fix, as a reusable method:

```java run
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;

public class Sol3 {
    static void rewriteAtomically(Path file, List<String> lines) throws IOException {
        Path temp = file.resolveSibling(file.getFileName() + ".tmp");
        Files.writeString(temp, String.join("\n", lines) + "\n", StandardCharsets.UTF_8);
        Files.move(temp, file, StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
    }

    public static void main(String[] args) throws IOException {
        Path dir = Path.of("sol3-vault");
        Path file = dir.resolve("notes.tsv");
        Files.createDirectories(dir);

        Files.writeString(file, "# quill-2\n1\tGroceries\tmilk\n", StandardCharsets.UTF_8);
        System.out.println("before = " + Files.size(file) + " bytes, "
                + Files.readAllLines(file, StandardCharsets.UTF_8).size() + " line(s)");

        rewriteAtomically(file, List.of("# quill-2", "1\tGroceries\tmilk",
                "2\tReading\tchapter 22"));

        System.out.println("after  = " + Files.size(file) + " bytes, "
                + Files.readAllLines(file, StandardCharsets.UTF_8).size() + " line(s)");
        System.out.println("temp   = " + Files.exists(dir.resolve("notes.tsv.tmp")));
        System.out.println();
        System.out.println("the live file is replaced, never truncated in place");
    }
}
```

```text
before = 27 bytes, 2 line(s)
after  = 48 bytes, 3 line(s)
temp   = false

the live file is replaced, never truncated in place
```

`before = 27 bytes, 2 line(s)` and `after = 48 bytes, 3 line(s)`, and `temp = false`. The live file went
from the old content to the new content with no state in between, which is what `ATOMIC_MOVE` buys.

Note the shape: build the whole new content in memory first, write it once, move it once. That is
possible because a vault is small. A file too large to hold in memory needs a different strategy —
write the new file, then stream the unchanged parts across — but the principle is the same, and the
principle is *never modify the live file in place*.

### 4. Migrate, or refuse — but do not guess

A `quill-1` file has no header and no escaping, and both differences are mechanical:

```java run
public class Sol4 {
    static final String HEADER = "# quill-2";

    static String upgrade(String text) {
        StringBuilder out = new StringBuilder(HEADER).append('\n');
        int id = 1;
        for (String line : text.split("\n", -1)) {
            if (line.isBlank() || line.startsWith("# ")) {
                continue;
            }
            String[] parts = line.split("\t", 3);
            if (parts.length != 3) {
                throw new IllegalArgumentException("cannot upgrade: " + line);
            }
            out.append(id++).append('\t')
                    .append(parts[1].replace("\\", "\\\\")).append('\t')
                    .append(parts[2].replace("\\", "\\\\")).append('\n');
        }
        return out.toString();
    }

    static String show(String s) {
        return "'" + s.replace("\n", "\\n").replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String old = "1\tGroceries\tmilk and eggs\n2\tReading\tchapter 22\n";
        String upgraded = upgrade(old);

        System.out.println("before = " + show(old));
        System.out.println("after  = " + show(upgraded));
        System.out.println();
        System.out.println("the header was added and the ids were renumbered from 1");
    }
}
```

```text
before = '1\tGroceries\tmilk and eggs\n2\tReading\tchapter 22\n'
after  = '# quill-2\n1\tGroceries\tmilk and eggs\n2\tReading\tchapter 22\n'

the header was added and the ids were renumbered from 1
```

The header is added and the ids are renumbered from 1. The `.replace("\\", "\\\\")` on each field is a
no-op for this input and is not optional in general: `quill-1` stored fields raw, so a title containing
a backslash would become ambiguous the moment the new unescaper saw it. **Migrating a format means
re-establishing every invariant the new format assumes**, and the ones that are invisible for your test
data are exactly the ones that will bite.

The migration is a one-way door, which is why it is a separate command rather than something `read`
does automatically. `quill migrate` rewrites the file and prints how many notes it converted; `read`
refuses anything that is not `quill-2`. An upgrade the user asked for is a migration. An upgrade that
happens because the reader guessed is a data loss waiting to be discovered.

## Key takeaways

- Escape the backslash **first**. An escaper that adds a backslash before the backslash pass will
  double the escape it just introduced, and it is correct for every input without a newline.
- A format is a pair of functions, `escape` and `unescape`, and the test for it is a round trip over
  awkward inputs: empty, the separator, the terminator, a lone backslash, and a trailing space.
- A `public record` needs a `public` compact constructor. Without the modifier it is package-private,
  which is narrower, and javac rejects the file with `invalid canonical constructor`.
- Java's built-in serialization writes binary that names your class, couples the data to the code's
  lifetime, and is unsafe on untrusted input. Write text instead.
- Always name the charset. `Files.writeString` defaults to UTF-8; `FileWriter` and `PrintWriter` default
  to the platform, which is a bug that only appears on someone else's machine.
- A charset that cannot represent a character replaces it silently. Read the data back and compare, or
  you will not know.
- Put a version in the file. Refuse a version you do not understand, or migrate it deliberately — never
  guess, because a guess writes a file you cannot read.
- `Files.writeString` truncates before it writes. A reader can catch the file at zero bytes. Write to a
  temporary file in the same directory and `ATOMIC_MOVE` it into place.
- A format that can represent everything needs less validation. Prefer representation to restriction.

## Practice

- [ ] Write `escape` and `unescape` for a comma-separated format and prove the round trip over ten
      awkward fields. Include a field that contains a comma, a quote, and the two characters `\n`.
- [ ] Change `Note` to escape the id field too, and explain what has to be true about the id for that
      change to be unnecessary.
- [ ] Make `Vault.append` write the header only when it creates the file, then make it crash between
      creating the file and writing the header, and show that `read` reports a clear error.
- [ ] Write `quill migrate` as a real command that reads a `quill-1` file, writes a `quill-2` file
      atomically, and prints the number of notes converted. It must refuse to run twice.
- [ ] Add a `size` field to `Note`, bump the header to `quill-3`, and write the migration from
      `quill-2`. Decide what `size` means for a note written before it existed.
- [ ] Take the `Scenario` and change `Files.move` to a plain copy followed by a delete. Find the window
      in which the live file is missing, and explain why the window is larger than the truncate window
      it replaced.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. The same structure, with `,` `"` `\n` `\r` and `\` in the escape table. The field containing a
   quote is the one that catches people: if you escape with quotes, the escape character is the quote
   and you need `""` for a literal one, which is why CSV is harder than it looks. Escaping with a
   backslash and quoting only when the field contains a comma is what a real CSV writer does.
2. Escaping the id is unnecessary because `Integer.toString` produces only digits and a leading `-` —
   a set of characters that cannot contain a separator or a backslash. The rule is: escape a field when
   the set of strings it can hold includes the escape character or a separator. For a decimal integer
   that set is closed, so the escaping would be dead code.
3. `Files.createDirectories`, then `Files.createFile` (which fails if it exists), then write the header.
   Crashing between the two leaves an empty file, and `read`'s `lines.isEmpty()` branch returns no
   notes rather than an error — which is wrong, because an empty file is not a valid `quill-2` vault.
   The fix is to treat empty as an error too, or to write the header with `CREATE_NEW` in one call.
4. Read the header, check it is `quill-1`, convert in memory, `rewriteAtomically`, and print the count.
   It refuses to run twice by checking that the header is `quill-1` before doing anything, which is the
   same rule the reader uses: decide from the file, not from a flag.
5. `size` is the length of the body in characters. For a note written before the field existed there is
   no honest value, and the two options are to compute it from the body during the migration — which is
   correct and is what a migration should do — or to leave it `-1` and have every reader treat `-1` as
   "unknown". Computing it is better: the migration has the body, so the information is not lost.
6. A copy-then-delete has two windows: after the copy but before the delete, the live file still exists
   and is stale, and after the delete but before... nothing, because the copy already landed. The real
   problem is that the copy itself is not atomic, so a reader during the copy sees a partially written
   file — the same failure as truncation, with a longer window. `Files.move` on the same filesystem is
   a single rename, so there is no window at all.
