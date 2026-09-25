---
chapter: 20
part: 3
title: The Project — Quill, a Command-Line Vault
summary: Start the project this part builds — a note vault driven from the command line — and settle its two contracts, the exit codes and the file format, before writing any of its features.
minutes: 55
tags: [cli, project, records, sealed types, exit codes, files]
---

Everything in Part II was a technique. This part is a program: **Quill**, a vault of short notes that
you drive from a terminal. It is small on purpose — four commands and one file — and it is the right
first project because everything it does is checkable. A command-line program reads arguments, writes
a file and prints text, and all three can be verified by a machine, which is why every transcript in
this part is a real one. By the end of Chapter 24 Quill will be a program you would not be embarrassed
to use. This chapter builds its skeleton and, more importantly, settles the two contracts that every
later chapter will have to honour.

## A program's exit code is part of its interface

A command-line program talks to the world in three ways: its arguments, its standard output, and its
**exit code**. The first two are visible when you run it by hand. The third is invisible, and that is
exactly why it is the one that gets neglected — and the one that a shell script depends on, because
`if quill list; then` is testing nothing else.

So the exit codes are decided first, before any feature exists, and they are written down as constants:

```text
0   success
2   unknown command
3   a required argument is missing
```

The numbers are not arbitrary. `0` for success is the one universal convention. `2` and `3` are above
`1` because `1` is reserved for "something went wrong that we did not anticipate" — a file that could
not be read, a disk that is full. A caller can then tell "you typed the command wrong" (my fault, do
not retry) from "the vault is unreadable" (not my fault, maybe retry) without parsing English.

```java run
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

public class Skeleton {
    static final int OK = 0;
    static final int UNKNOWN = 2;
    static final int MISSING_ARG = 3;

    static final String USAGE = """
            quill - a command-line vault

            usage:
              quill                        show this help
              quill add <title> <body>     add a note
              quill list                   list every note
            """;

    static int run(String[] args, PrintStream out) {
        if (args.length == 0) {
            out.print(USAGE);
            return OK;
        }
        return switch (args[0]) {
            case "help" -> {
                out.print(USAGE);
                yield OK;
            }
            case "list" -> OK;
            case "add" -> args.length >= 3 ? OK : MISSING_ARG;
            default -> UNKNOWN;
        };
    }

    public static void main(String[] args) {
        String[][] invocations = {
            {},
            {"list"},
            {"add"},
            {"add", "Groceries", "milk and eggs"},
            {"frobnicate"},
        };
        for (String[] invocation : invocations) {
            ByteArrayOutputStream sink = new ByteArrayOutputStream();
            int code = run(invocation, new PrintStream(sink));
            String label = invocation.length == 0
                    ? "(no arguments)"
                    : String.join(" ", invocation);
            System.out.printf("%-30s exit %d, %3d byte(s) written%n",
                    label, code, sink.size());
        }
    }
}
```

```text
(no arguments)                 exit 0, 172 byte(s) written
list                           exit 0,   0 byte(s) written
add                            exit 3,   0 byte(s) written
add Groceries milk and eggs    exit 0,   0 byte(s) written
frobnicate                     exit 2,   0 byte(s) written
```

Read the shape of that `run` method, because it is the shape of the whole project.

It takes the arguments **and a `PrintStream`**. It does not touch `System.out`. That one decision is
what makes the contract testable: the demo `main` above hands `run` a `ByteArrayOutputStream` for each
invocation, which is why it can print `0 byte(s) written` for `list` without a single character
reaching the terminal. This is the dependency injection of Chapter 19 again, applied to output rather
than to a clock, and it will pay for itself every time a chapter needs to assert on what a command
printed.

The `switch` is an expression, so every arm has to produce a value and the compiler will not let one
fall through. `add` needs three arguments — the command, a title and a body — and the whole arm is the
ternary that checks it.

The measured table is the contract:

```text
(no arguments)                 exit 0, 172 byte(s) written
list                           exit 0,   0 byte(s) written
add                            exit 3,   0 byte(s) written
add Groceries milk and eggs    exit 0,   0 byte(s) written
frobnicate                     exit 2,   0 byte(s) written
```

The bare invocation writes 172 bytes — the help text — and exits **0**. That is a choice worth stating
plainly, because `git` does the opposite: running `git` with no arguments prints the usage and exits 1.
The argument for `0` is that the user asked for something reasonable and got it; nothing failed. The
argument for `1` is that a script which runs `quill` to check the tool exists should not see a success.
Pick one and write it down — what you must not do is leave it to whichever branch happens to be first.

:::warning
`System.exit` does not flush your output streams. A program that prints a result and then exits can
lose the last buffer, and the bug appears only when the output is large enough to fill it. Flush
before you exit, or avoid `System.exit` on the success path altogether. Quill does the second: `main`
returns normally when the code is `0`, and only calls `System.exit` when it must report a failure.
:::

## The unit of the vault is a record

A note has an id, a title and a body, and nothing else. Chapter 16 introduced records as classes the
compiler writes for you; here is one doing real work:

```java run-files
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

// ===== NoteDemo.java =====

public class NoteDemo {
    static String show(String s) {
        return s.replace("\t", "\\t");
    }

    public static void main(String[] args) {
        Note original = new Note(1, "Groceries", "milk\teggs");
        String line = original.render();
        Note reread = Note.parse(line);

        System.out.println("line        = " + show(line));
        System.out.println("round trip  = " + reread.equals(original));
        System.out.println("body        = " + show(reread.body()));

        System.out.println();

        Note awkward = new Note(2, "A\tB", "x");
        Note damaged = Note.parse(awkward.render());
        System.out.println("title in    = " + show(awkward.title()));
        System.out.println("title out   = " + damaged.title());
        System.out.println("body out    = " + show(damaged.body()));
    }
}
```

```text
line        = 1\tGroceries\tmilk\teggs
round trip  = true
body        = milk\teggs

title in    = A\tB
title out   = A
body out    = B\tx
```

Two methods and one constant, and between them they define the file format. `render` turns a note into
a line; `parse` turns a line back into a note. **A format is the pair of them, and they are only
correct together.** Writing one without the other is how formats drift.

The interesting detail is the `3` in `line.split(SEP, 3)`. Without it, `split` would break the line
into as many pieces as there are tabs, and a note whose body contains a tab would come back in
fragments. The limit says *"split into at most three fields"*, so everything after the second tab is
the body — and the demo proves it:

```text
line        = 1\tGroceries\tmilk\teggs
round trip  = true
body        = milk\teggs
```

The body survived a tab. `round trip = true` means `parse(render(note)).equals(note)`, which is the
property that makes a format usable: what you write is what you read.

Now look at the second half of the same transcript, and watch the same format fail:

```text
title in    = A\tB
title out   = A
body out    = B\tx
```

A tab in the **title** does not survive, and the reason is that `split` works from the left. The first
field is the id, the second ends at the next tab — so `A` becomes the title, and the rest of what was
the title is now the head of the body. Nothing threw. Nothing warned. The note was silently rewritten.

That is not a bug in `parse`; `parse` did exactly what the format says. It is a hole in the format, and
it can only be closed by refusing the input — a title may not contain a tab, enforced where the note is
constructed. Chapter 16 showed where that goes (a compact constructor) and Chapter 22 will show what
happens when you decide instead to escape the separator rather than forbid it.

## A command is a sealed type, so the compiler can check the switch

The dispatcher in `Skeleton` switches on a `String`. That works, and it has a weakness: the compiler
knows nothing about the set of commands. Misspell `"lisst"` in a `case` label and you get a command
that can never be reached, with no complaint from anyone.

Chapter 16's sealed types fix exactly this. A command becomes a value, and the set of commands becomes
a closed hierarchy the compiler can see:

```java run-files
// ===== Commands.java =====

public sealed interface Commands
        permits Commands.Add, Commands.ListNotes, Commands.Show, Commands.Help {

    record Add(String title, String body) implements Commands {}

    record ListNotes() implements Commands {}

    record Show(int id) implements Commands {}

    record Help() implements Commands {}

    static String describe(Commands command) {
        return switch (command) {
            case Add a -> "add \"" + a.title() + "\"";
            case ListNotes n -> "list";
            case Show s -> "show #" + s.id();
            case Help h -> "help";
        };
    }
}

// ===== CommandsDemo.java =====

public class CommandsDemo {
    public static void main(String[] args) {
        Commands[] commands = {
            new Commands.Add("Groceries", "milk and eggs"),
            new Commands.ListNotes(),
            new Commands.Show(7),
            new Commands.Help(),
        };
        for (Commands command : commands) {
            System.out.printf("%-12s %s%n",
                    command.getClass().getSimpleName(), Commands.describe(command));
        }
    }
}
```

```text
Add          add "Groceries"
ListNotes    list
Show         show #7
Help         help
```

`Commands` is sealed and `permits` exactly four records, so the compiler knows the complete list. The
`describe` switch has **no `default` arm**, and that is the point: javac can prove the arms cover every
permitted type, so it does not ask for one. A `default` here would not be defensive; it would throw
away the only guarantee the sealed keyword bought you.

The four lines of output are the proof that each command is a distinct value carrying its own data:

```text
Add          add "Groceries"
ListNotes    list
Show         show #7
Help         help
```

Note that `ListNotes` and `Help` are records with no components. They are still distinct types, which
is what lets them appear as separate arms — a fact an `enum` could not express, because `Add` carries a
title and a body while `Help` carries nothing.

## What the compiler does when you forget one

The guarantee is worth seeing fail, because the failure is the feature:

```java bad
public class BadSwitch {
    sealed interface Shape permits BadSwitch.Circle, BadSwitch.Square {}

    record Circle(double radius) implements Shape {}

    record Square(double side) implements Shape {}

    static double area(Shape shape) {
        return switch (shape) {
            case Circle c -> Math.PI * c.radius() * c.radius();
        };
    }

    public static void main(String[] args) {
        System.out.println(area(new Circle(1)));
    }
}
```

```text
error: the switch expression does not cover all possible input values
```

`Shape` permits two records. The switch handles `Circle` and stops. javac refuses the file, and the
sentence it produces — **the switch expression does not cover all possible input values** — is the
entire reason to prefer a sealed hierarchy over a `String` and a `default`.

This is what Chapter 16 meant by closing a hierarchy. Adding a fifth command to Quill in Chapter 23
will break every switch that describes a command, at compile time, in the file that needs the new arm.
The alternative is a `default` arm that quietly does something wrong at runtime, and you find out from
a user.

:::pitfall
**A `default` arm in a switch over a sealed type is a silent downgrade.** It compiles, it looks
prudent, and it converts a compile error into a runtime surprise: add a permitted subtype and the new
case falls into `default` instead of stopping the build. If the switch is meant to be exhaustive, say
so by leaving the `default` out and let javac hold you to it.
:::

## The vault is a file, and the file is the state

There is no database in this project and no in-memory index. The state of a vault is one text file,
and every read goes to disk. That sounds slow and it is, by a few milliseconds; it is also the reason
the whole thing can be inspected, copied and repaired with `cat` and a text editor, which is worth far
more at this size.

```java run-files
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

// ===== VaultDemo.java =====

import java.nio.file.Files;
import java.nio.file.Path;

public class VaultDemo {
    public static void main(String[] args) throws Exception {
        Path home = Path.of("demo-vault");
        Vault vault = new Vault(home);

        System.out.println("empty        = " + vault.read());

        vault.append(new Note(vault.nextId(), "Groceries", "milk and eggs"));
        vault.append(new Note(vault.nextId(), "Reading", "chapter 20"));

        System.out.println("after two    = " + vault.read().size() + " note(s)");
        System.out.println("next id      = " + vault.nextId());
        System.out.println();
        System.out.println("notes.tsv, tabs shown as \\t:");
        System.out.print(Files.readString(home.resolve("notes.tsv")).replace("\t", "\\t"));
        System.out.println();
        System.out.println("lines on disk= "
                + Files.readAllLines(home.resolve("notes.tsv")).size());
    }
}
```

```text
empty        = []
after two    = 2 note(s)
next id      = 3

notes.tsv, tabs shown as \t:
1\tGroceries\tmilk and eggs
2\tReading\tchapter 20

lines on disk= 2
```

`read` is the only place that knows how to turn the file into notes, and it is careful about the two
cases that bite: the file may not exist yet, and it may contain a blank line. A missing file returns an
empty list rather than throwing, because "I have no notes" and "I have no vault" are the same thing to
a reader.

`append` uses `StandardOpenOption.APPEND`, so writing note number four hundred does not rewrite the
first three hundred and ninety-nine. It also calls `Files.createDirectories(home)` first, so the very
first `add` on a fresh machine creates `vault/` without a separate setup step.

The demo shows the file as it really is — tabs and all — and the count on disk:

```text
empty        = []
after two    = 2 note(s)
next id      = 3

notes.tsv, tabs shown as \t:
1\tGroceries\tmilk and eggs
2\tReading\tchapter 20

lines on disk= 2
```

`nextId` is the method to look at twice. It returns the **highest existing id plus one**, not the
number of notes plus one. Those agree until something is deleted, and then they disagree in the worst
possible way: after deleting a middle note, `size + 1` names a note that already exists. Solution 4
measures it.

## The three files, wired together

Here is the whole program as it stands. `Main.java` is the entry point, `Note.java` is the value and
`Vault.java` is the storage, and the arrows only point one way: `Main` knows about `Vault`, `Vault`
knows about `Note`, and `Note` knows about nothing.

```java run-files
// ===== Main.java =====

import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Path;
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
              quill add <title> <body>     add a note
              quill list                   list every note
            """;

    public static void main(String[] args) {
        int code = run(args, Path.of("vault"), System.out, System.err);
        System.out.flush();
        System.err.flush();
        if (code != OK) {
            System.exit(code);
        }
    }

    static int run(String[] args, Path home, PrintStream out, PrintStream err) {
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
                case "add" -> args.length >= 3
                        ? add(vault, args[1], args[2], out)
                        : missing(err, "add <title> <body>");
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

    private static int add(Vault vault, String title, String body, PrintStream out)
            throws IOException {
        Note note = new Note(vault.nextId(), title, body);
        vault.append(note);
        out.println("added #" + note.id() + " " + note.title());
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
  quill add <title> <body>     add a note
  quill list                   list every note
```

Read the `main` method as three lines of policy. It resolves where the vault lives, it delegates every
decision to `run`, and it converts the returned code into a process exit. Everything interesting is in
`run`, which takes the home directory and both streams as parameters — so a test, or the next chapter,
can point it at a temporary directory and capture what it printed.

When this listing is compiled and run with no arguments it prints the help and exits 0, which is why
the transcript under it is the usage text and nothing else.

## Driving it

Arguments are the last piece, and the only honest way to show them is to run the program. The block
below compiles the listing above into `out/` and then calls it six times. The shell function folds the
error stream into the output with `2>&1` — without it, every diagnostic would be invisible here — and
prints `$?`, the exit code of the command that just ran:

```sh run-project
quill() {
  java -cp out Main "$@" 2>&1
  echo "  -> exit $?"
}

echo '$ quill list'
quill list
echo
echo '$ quill add Groceries "milk and eggs"'
quill add Groceries "milk and eggs"
echo
echo '$ quill add Reading "chapter 20"'
quill add Reading "chapter 20"
echo
echo '$ quill list'
quill list
echo
echo '$ quill frobnicate'
quill frobnicate
echo
echo '$ quill add Untitled'
quill add Untitled
```

```text
$ quill list
no notes yet
  -> exit 0

$ quill add Groceries "milk and eggs"
added #1 Groceries
  -> exit 0

$ quill add Reading "chapter 20"
added #2 Reading
  -> exit 0

$ quill list
#1  Groceries  milk and eggs
#2  Reading  chapter 20
  -> exit 0

$ quill frobnicate
quill: unknown command 'frobnicate'
  -> exit 2

$ quill add Untitled
quill: missing argument; usage: quill add <title> <body>
  -> exit 3
```

Six invocations, and the transcript is the specification:

- `list` on an empty vault prints `no notes yet` and exits `0`. An empty vault is not an error.
- Two `add` calls each print a confirmation naming the id they assigned, and `list` then shows both.
- `frobnicate` prints `quill: unknown command 'frobnicate'` and exits `2`.
- `add Untitled` prints the usage for that command and exits `3`.

That last line is the difference between a usable tool and an annoying one. `quill: missing argument;
usage: quill add <title> <body>` tells the user what was wrong *and* what to type instead. The
message is on the error stream, so a script that captures output does not have to filter it out.

:::scenario A note that came back with the wrong title

Quill is in use. A user copies a title out of a spreadsheet — the cell reads `Groceries` and a second
column, and what the clipboard actually contains is `Groceries\tand more`, because the spreadsheet puts
a tab between the columns. The note is added, and a week later the user reports that the vault has
split their note in two: the title is `Groceries` and the body begins `and more`.

:::solution
The format is `title` + tab + `body`, and the title arrived containing a tab. Everything downstream
behaved correctly: `render` wrote the tab, `parse` split on the first tab it found, and the title it
returned was genuinely the text before that tab.

The fix is not in `parse`. It is at the boundary, where the note is constructed, and it is the compact
constructor from Chapter 16:

```java run
public class Scenario {
    record Loose(String title, String body) {
        String render() {
            return title + "\t" + body;
        }
    }

    record Guarded(String title, String body) {
        Guarded {
            if (title.indexOf('\t') >= 0 || title.indexOf('\n') >= 0) {
                throw new IllegalArgumentException("title may not contain a tab or newline");
            }
        }

        String render() {
            return title + "\t" + body;
        }
    }

    static String show(String s) {
        return "'" + s.replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String pasted = "Groceries\tand more";

        String[] parts = new Loose(pasted, "milk").render().split("\t", 2);
        System.out.println("pasted title     = " + show(pasted));
        System.out.println("title read back  = " + show(parts[0]));
        System.out.println("body read back   = " + show(parts[1]));

        System.out.println();

        try {
            new Guarded(pasted, "milk");
            System.out.println("guarded          = accepted, which would be wrong");
        } catch (IllegalArgumentException e) {
            System.out.println("guarded          = rejected at the boundary");
            System.out.println("message          = " + e.getMessage());
        }
    }
}
```

```text
pasted title     = 'Groceries\tand more'
title read back  = 'Groceries'
body read back   = 'and more\tmilk'

guarded          = rejected at the boundary
message          = title may not contain a tab or newline
```

The unguarded record demonstrates the corruption — the title read back is `Groceries` and the body
read back is `and more\tmilk` — and the guarded one refuses the same input with a message naming the
problem. The value of doing it in the constructor rather than in `main` is that there is no way to
build a bad note: every path that constructs one goes through the same check, including paths that do
not exist yet.

**The general rule: a format has a set of strings it can represent, and the strings it cannot represent
must be rejected where they enter the system, not discovered where they leave it.** The tab is this
format's example. Every format has one — a comma in a CSV field, a quote in a JSON string, a newline in
an HTTP header.
:::

## Solutions

### 1. The exit-code contract, written as a table

The contract in this chapter was three constants and a promise. A promise is not a test. Here it is as
data, checked by a loop:

```java run
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

public class Sol1 {
    static final int OK = 0;
    static final int UNKNOWN = 2;
    static final int MISSING_ARG = 3;

    record Case(String[] args, int expected) {}

    static int run(String[] args, PrintStream out) {
        if (args.length == 0) {
            out.print("usage");
            return OK;
        }
        return switch (args[0]) {
            case "help" -> {
                out.print("usage");
                yield OK;
            }
            case "list" -> OK;
            case "add" -> args.length >= 3 ? OK : MISSING_ARG;
            default -> UNKNOWN;
        };
    }

    public static void main(String[] args) {
        Case[] cases = {
            new Case(new String[] {}, OK),
            new Case(new String[] {"help"}, OK),
            new Case(new String[] {"list"}, OK),
            new Case(new String[] {"add", "Groceries", "milk"}, OK),
            new Case(new String[] {"add"}, MISSING_ARG),
            new Case(new String[] {"add", "Groceries"}, MISSING_ARG),
            new Case(new String[] {"frobnicate"}, UNKNOWN),
            new Case(new String[] {"--help"}, UNKNOWN),
        };

        int passed = 0;
        for (Case c : cases) {
            int actual = run(c.args(), new PrintStream(new ByteArrayOutputStream()));
            boolean ok = actual == c.expected();
            if (ok) {
                passed++;
            }
            String label = c.args().length == 0 ? "(none)" : String.join(" ", c.args());
            System.out.printf("%-22s expected %d, got %d  %s%n",
                    label, c.expected(), actual, ok ? "ok" : "FAIL");
        }
        System.out.println("passed " + passed + " of " + cases.length);
    }
}
```

```text
(none)                 expected 0, got 0  ok
help                   expected 0, got 0  ok
list                   expected 0, got 0  ok
add Groceries milk     expected 0, got 0  ok
add                    expected 3, got 3  ok
add Groceries          expected 3, got 3  ok
frobnicate             expected 2, got 2  ok
--help                 expected 2, got 2  ok
passed 8 of 8
```

`passed 8 of 8`. The value of writing it this way is that the contract is now *in* the test: eight
`Case` records, each with the arguments and the code the chapter claims. Adding a command to Quill
means adding its rows, and a row that disagrees with the implementation fails the build.

Note the last two rows. `add` with no title and `add` with a title but no body are both `MISSING_ARG`
— the argument count is checked once, not per-argument. And `--help`, which a user will certainly try,
is an unknown command, not help. If you want it to be help, that is a decision, and it belongs in this
table before it belongs in the code.

### 2. Reject the separator at the boundary

The scenario fixed the title. This is the same fix with the round-trip property made explicit, because
"the constructor rejects a tab" and "every note that exists survives a round trip" are different
claims:

```java run
public class Sol2 {
    record SafeNote(int id, String title, String body) {
        SafeNote {
            if (title.indexOf('\t') >= 0 || title.indexOf('\n') >= 0) {
                throw new IllegalArgumentException("tab or newline in title");
            }
        }

        String render() {
            return id + "\t" + title + "\t" + body;
        }

        static SafeNote parse(String line) {
            String[] parts = line.split("\t", 3);
            if (parts.length != 3) {
                throw new IllegalArgumentException("not a note line");
            }
            return new SafeNote(Integer.parseInt(parts[0]), parts[1], parts[2]);
        }
    }

    static String show(String s) {
        return "'" + s.replace("\t", "\\t").replace("\n", "\\n") + "'";
    }

    public static void main(String[] args) {
        String[] titles = {"Groceries", "Groceries\tand more", "Two\nlines", "", "Ünïcode"};

        int accepted = 0;
        int lossless = 0;
        for (String title : titles) {
            try {
                SafeNote note = new SafeNote(1, title, "milk\tand eggs");
                accepted++;
                if (SafeNote.parse(note.render()).equals(note)) {
                    lossless++;
                }
                System.out.printf("%-22s accepted%n", show(title));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-22s rejected%n", show(title));
            }
        }

        System.out.println();
        System.out.println("accepted " + accepted + " of " + titles.length);
        System.out.println("round-tripped losslessly " + lossless + " of " + accepted);
    }
}
```

```text
'Groceries'            accepted
'Groceries\tand more'  rejected
'Two\nlines'           rejected
''                     accepted
'Ünïcode'              accepted

accepted 3 of 5
round-tripped losslessly 3 of 3
```

`accepted 3 of 5` and `round-tripped losslessly 3 of 3`. The two rejected titles are the ones
containing a tab and a newline. The three accepted ones include the empty string and `Ünïcode`, and the
second number is the one that matters: **every note the constructor allowed came back identical.**

The empty string is accepted deliberately. It is not the same as a missing title — the command layer
decides that `quill add` with no title at all is a usage error, and the format layer decides that a
note may have an empty title. Two layers, two questions, and keeping them separate is what stops one
of them from making the other's decisions.

### 3. Adding a command proves the switch

Chapter 16 promised that a sealed hierarchy catches a missed case at compile time. Here is the promise
kept, with a `delete` command added to the four:

```java run
public class Sol3 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Help {

        record Add(String title, String body) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Help() implements Command {}
    }

    static String describe(Command command) {
        return switch (command) {
            case Command.Add a -> "add \"" + a.title() + "\"";
            case Command.ListNotes n -> "list";
            case Command.Show s -> "show #" + s.id();
            case Command.Delete d -> "delete #" + d.id();
            case Command.Help h -> "help";
        };
    }

    public static void main(String[] args) {
        Command[] commands = {
            new Command.Add("Groceries", "milk and eggs"),
            new Command.ListNotes(),
            new Command.Show(3),
            new Command.Delete(3),
            new Command.Help(),
        };
        for (Command command : commands) {
            System.out.printf("%-12s %s%n",
                    command.getClass().getSimpleName(), describe(command));
        }
        System.out.println();
        System.out.println("5 permitted types, 5 arms, and no default arm");
    }
}
```

```text
Add          add "Groceries"
ListNotes    list
Show         show #3
Delete       delete #3
Help         help

5 permitted types, 5 arms, and no default arm
```

`5 permitted types, 5 arms, and no default arm`. The `describe` method grew by exactly one arm and
nothing else had to change, which is the property to look for in a design: the cost of a new case is
proportional to the case, not to the number of places that must be told about it.

The proof that the switch is exhaustive is the absence of `default`. Delete the `Command.Delete` arm
and the file stops compiling with the same diagnostic `BadSwitch.java` produced earlier in the
chapter. You do not have to trust that you remembered — javac tells you.

### 4. `max + 1`, not `size + 1`

This is the one that looks like a style preference and is not:

```java run
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

public class Sol4 {
    static final Path FILE = Path.of("sol4-vault", "notes.tsv");

    static List<String> read() throws IOException {
        return Files.exists(FILE)
                ? Files.readAllLines(FILE, StandardCharsets.UTF_8)
                : List.of();
    }

    static void write(List<String> lines) throws IOException {
        Files.createDirectories(FILE.getParent());
        Files.writeString(FILE, String.join("\n", lines) + "\n", StandardCharsets.UTF_8);
    }

    static void append(String line) throws IOException {
        Files.createDirectories(FILE.getParent());
        Files.writeString(FILE, line + "\n", StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }

    static int idByMax() throws IOException {
        int highest = 0;
        for (String line : read()) {
            highest = Math.max(highest, Integer.parseInt(line.split("\t", 2)[0]));
        }
        return highest + 1;
    }

    static int idBySize() throws IOException {
        return read().size() + 1;
    }

    public static void main(String[] args) throws IOException {
        append("1\tGroceries\tmilk and eggs");
        append("2\tReading\tchapter 20");
        append("3\tDraft\tdelete me");
        System.out.println("after three       max+1 = " + idByMax()
                + "   size+1 = " + idBySize());

        List<String> kept = new ArrayList<>();
        for (String line : read()) {
            if (!line.startsWith("2\t")) {
                kept.add(line);
            }
        }
        write(kept);
        System.out.println("after deleting #2 max+1 = " + idByMax()
                + "   size+1 = " + idBySize());
        System.out.println();
        System.out.println("size+1 now names #3, a note that already exists");
    }
}
```

```text
after three       max+1 = 4   size+1 = 4
after deleting #2 max+1 = 4   size+1 = 3

size+1 now names #3, a note that already exists
```

Three notes, then the middle one deleted. `max + 1` returns `4` both times, because the highest id in
the file is still `3`. `size + 1` returns `4` and then `3` — and `3` is already taken. The next `add`
would create a second note numbered 3, `list` would print two notes with the same id, and `show 3`
would have to pick one.

An id is an identifier, not an index. An index is a position in a sequence and it is expected to
change when the sequence changes; an identifier is a name and it must never be reused, or every
reference to it becomes ambiguous. The same reasoning is why databases have sequences that never go
backwards, and why deleting a row does not renumber the others.

## Key takeaways

- A command-line program's interface is its arguments, its output **and its exit code**. Decide the
  codes before the features, write them as constants, and let `0` mean success.
- Take the output stream as a parameter instead of using `System.out` directly. It costs one argument
  and makes every command testable.
- `System.exit` does not flush. Flush first, or stay off the success path.
- A file format is `render` and `parse` together. `split(SEP, 3)` keeps the body intact when it contains
  the separator; the same limit is what lets a separator in the *title* corrupt the note silently.
- A format's illegal inputs must be rejected where the value is constructed. The compact constructor is
  where that goes.
- A sealed hierarchy plus a switch with no `default` arm turns "did you handle every case?" into a
  compile error, with the message `the switch expression does not cover all possible input values`.
- A `default` arm over a sealed type throws that guarantee away. It is not defensive; it is a silent
  downgrade to a runtime bug.
- Append to a file with `StandardOpenOption.APPEND`. Rewriting the whole file to add one line is a
  correctness bug waiting for a crash, not just a performance one.
- An id is a name, not an index. Use the highest existing id plus one, never the count plus one —
  they differ the moment anything is deleted.

## Practice

- [ ] Add a `count` command that prints the number of notes and exits 0. Add its rows to the
      exit-code table from Solution 1 and check that the table still passes.
- [ ] Give `Note` a compact constructor that rejects a tab or newline in the title, then write a loop
      that tries twenty titles — including `""`, a title of only spaces, and one with an emoji — and
      reports how many were accepted and how many of those round-tripped.
- [ ] Change `nextId` to `size + 1` and write the sequence of commands that makes two notes share an
      id. Then change it back and show that the same sequence cannot.
- [ ] Add a `--vault <dir>` option that makes the vault live somewhere other than `./vault`. Prove
      that two vaults in two directories do not see each other's notes.
- [ ] Make `list` print a column-aligned table, then add a note whose title is longer than the column
      width and fix the output so it does not shift.
- [ ] Write a `show <id>` command that exits 4 when the id does not exist. Decide whether an empty
      vault should exit 4 or 0 for `show 1`, and write down why.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `case "count" -> { out.println(vault.read().size()); yield OK; }`. The table gains one row,
   `new Case(new String[] {"count"}, OK)`, and `passed 9 of 9` is the evidence. If you also add a row
   for a missing vault, you have discovered that `count` on an empty directory is not an error.
2. The constructor is the one from Solution 2. The interesting results are the edges: `""` and a title
   of only spaces are accepted, and the emoji is accepted because a tab is not a character class —
   the check is for two specific characters, not for "unusual" ones. A title of only spaces is
   arguably a mistake, but it is the *command layer's* mistake to catch, not the format's.
3. `add A`, `add B`, `add C`, delete `B`, then `add D`. With `size + 1` the new note is numbered 3,
   which `C` already has; `list` shows two notes numbered 3. With `max + 1` it is numbered 4. The
   sequence is the test — write it down before you change the code, or you will pick a sequence where
   the two happen to agree.
4. Parse the option before dispatching and pass the resolved `Path` into `run`, which already takes
   one. Two vaults in two directories are two `Vault` objects over two files; they cannot see each
   other because neither ever looks outside its own `home`. That is the whole benefit of `Vault` taking
   a `Path` rather than deciding for itself.
5. Compute the widest title first, then use `printf("%-" + width + "s", title)`. The trap is that a
   fixed width like `%-20s` does not truncate and does not push the next column along — it just butts
   the long value against whatever follows. Either measure the data or put the variable-length field
   last.
6. `show` reads the vault, finds the note with that id, and prints it; if there is none it writes
   `quill: no note #4` to the error stream and returns 4. For an empty vault the honest answer is 4:
   the user named a note that does not exist, and "the vault is empty" is the reason, not an excuse.
   Returning 0 would tell a script the note was found.
