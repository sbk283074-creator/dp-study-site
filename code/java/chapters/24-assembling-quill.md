---
chapter: 24
part: 3
title: Assembling Quill
summary: Close Part III by making the program provable and shippable -- an end-to-end test that drives the real run method, the reason main cannot be tested at all, and a jar with a main class.
minutes: 60
tags: [cli, testing, packaging, jar, sealed types, design]
---

Four chapters ago `quill` was a `switch` on `args[0]`. It is now a program with a parser, a sealed
command hierarchy, a versioned file format and an atomic rewrite. None of that is worth much until you
can show that it works and hand it to somebody, and those are the two things this chapter does. It is
also the last chapter of Part III, so it is where the pieces get named and counted.

## Six files, five responsibilities

Here is the whole program, compiled and run with no arguments:

```java run-files
// ===== Main.java =====

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;

public class Main {
    static final int OK = 0;
    static final int USAGE = 2;
    static final int IO_FAILURE = 4;
    static final int NOT_FOUND = 5;

    static final String USAGE_TEXT = """
            quill - a command-line vault

            usage:
              quill [--vault <dir>] <command> [arguments]

            commands:
              help                 show this text
              add <title>          add a note; the body is read from standard input
              list                 list every note
              show <id>            print one note
              delete <id>          remove one note
            """;

    public static void main(String[] args) {
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
        int code = run(args, in, System.out, System.err);
        System.out.flush();
        System.err.flush();
        if (code != OK) {
            System.exit(code);
        }
    }

    static int run(String[] args, BufferedReader in, PrintStream out, PrintStream err) {
        Options.Invocation invocation;
        Commands command;
        try {
            invocation = Options.parse(args);
            command = Commands.parse(invocation.rest());
        } catch (IllegalArgumentException e) {
            err.println("quill: " + e.getMessage());
            err.print(USAGE_TEXT);
            return USAGE;
        }
        try {
            return execute(command, new Vault(invocation.home()), in, out, err);
        } catch (IOException e) {
            err.println("quill: " + e.getMessage());
            return IO_FAILURE;
        }
    }

    static int execute(Commands command, Vault vault, BufferedReader in, PrintStream out,
            PrintStream err) throws IOException {
        return switch (command) {
            case Commands.Help h -> {
                out.print(USAGE_TEXT);
                yield OK;
            }
            case Commands.ListNotes n -> {
                list(vault, out);
                yield OK;
            }
            case Commands.Add a -> add(vault, a.title(), in, out);
            case Commands.Show s -> show(vault, s.id(), out, err);
            case Commands.Delete d -> delete(vault, d.id(), out, err);
        };
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

    private static int show(Vault vault, int id, PrintStream out, PrintStream err)
            throws IOException {
        for (Note note : vault.read()) {
            if (note.id() == id) {
                out.println("#" + note.id() + "  " + note.title());
                out.println(note.body());
                return OK;
            }
        }
        err.println("quill: no note #" + id);
        return NOT_FOUND;
    }

    private static int delete(Vault vault, int id, PrintStream out, PrintStream err)
            throws IOException {
        if (vault.delete(id)) {
            out.println("deleted #" + id);
            return OK;
        }
        err.println("quill: no note #" + id);
        return NOT_FOUND;
    }
}

// ===== Options.java =====

import java.nio.file.Path;
import java.util.Arrays;

public class Options {
    record Invocation(Path home, String[] rest) {}

    static Invocation parse(String[] args) {
        Path home = Path.of("vault");
        int i = 0;
        while (i < args.length) {
            if (args[i].equals("--vault")) {
                if (i + 1 == args.length) {
                    throw new IllegalArgumentException("--vault needs a directory");
                }
                home = Path.of(args[i + 1]);
                i += 2;
            } else if (args[i].equals("--")) {
                i++;
                break;
            } else {
                break;
            }
        }
        return new Invocation(home, Arrays.copyOfRange(args, i, args.length));
    }
}

// ===== Commands.java =====

public sealed interface Commands
        permits Commands.Add, Commands.ListNotes, Commands.Show, Commands.Delete, Commands.Help {

    record Add(String title) implements Commands {}

    record ListNotes() implements Commands {}

    record Show(int id) implements Commands {}

    record Delete(int id) implements Commands {}

    record Help() implements Commands {}

    @SuppressWarnings("serial")
    class UsageException extends IllegalArgumentException {
        UsageException(String message) {
            super(message);
        }
    }

    static Commands parse(String[] args) {
        if (args.length == 0) {
            return new Help();
        }
        return switch (args[0]) {
            case "help" -> new Help();
            case "list" -> new ListNotes();
            case "add" -> {
                if (args.length < 2) {
                    throw new UsageException("add needs a title");
                }
                yield new Add(args[1]);
            }
            case "show" -> new Show(id(args, "show <id>"));
            case "delete" -> new Delete(id(args, "delete <id>"));
            default -> throw new UsageException("unknown command '" + args[0] + "'");
        };
    }

    static String describe(Commands command) {
        return switch (command) {
            case Add a -> "add \"" + a.title() + "\"";
            case ListNotes n -> "list";
            case Show s -> "show #" + s.id();
            case Delete d -> "delete #" + d.id();
            case Help h -> "help";
        };
    }

    private static int id(String[] args, String form) {
        if (args.length < 2) {
            throw new UsageException(form + " needs an id");
        }
        int id;
        try {
            id = Integer.parseInt(args[1]);
        } catch (NumberFormatException e) {
            throw new UsageException("'" + args[1] + "' is not an id");
        }
        if (id <= 0) {
            throw new UsageException("ids start at 1, not " + id);
        }
        return id;
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
import java.nio.file.StandardCopyOption;
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

    boolean delete(int id) throws IOException {
        List<Note> kept = new ArrayList<>();
        boolean removed = false;
        for (Note note : read()) {
            if (note.id() == id) {
                removed = true;
            } else {
                kept.add(note);
            }
        }
        if (!removed) {
            return false;
        }
        rewrite(kept);
        return true;
    }

    private void rewrite(List<Note> notes) throws IOException {
        Files.createDirectories(home);
        StringBuilder out = new StringBuilder(HEADER).append('\n');
        for (Note note : notes) {
            out.append(note.render()).append('\n');
        }
        Path temp = file().resolveSibling(FILE + ".tmp");
        Files.writeString(temp, out.toString(), StandardCharsets.UTF_8);
        Files.move(temp, file(), StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
    }
}

// ===== SelfTest.java =====

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class SelfTest {
    record Case(String label, String[] rest, String stdin, int expected) {}

    public static void main(String[] args) throws Exception {
        Path home = Files.createTempDirectory("quill-selftest");

        List<Case> cases = List.of(
            new Case("(none)", new String[] {}, "", 0),
            new Case("list", new String[] {"list"}, "", 0),
            new Case("add Groceries", new String[] {"add", "Groceries"}, "milk and eggs\n", 0),
            new Case("list", new String[] {"list"}, "", 0),
            new Case("show 1", new String[] {"show", "1"}, "", 0),
            new Case("show 2", new String[] {"show", "2"}, "", 5),
            new Case("delete 1", new String[] {"delete", "1"}, "", 0),
            new Case("delete 1", new String[] {"delete", "1"}, "", 5),
            new Case("show seven", new String[] {"show", "seven"}, "", 2),
            new Case("frobnicate", new String[] {"frobnicate"}, "", 2));

        int passed = 0;
        for (Case c : cases) {
            int actual = Main.run(withHome(home, c.rest()),
                    new BufferedReader(new StringReader(c.stdin())), sink(), sink());
            boolean ok = actual == c.expected();
            if (ok) {
                passed++;
            }
            System.out.printf("%-16s expected %d, got %d  %s%n",
                    c.label(), c.expected(), actual, ok ? "ok" : "FAIL");
        }

        System.out.println();
        System.out.println("passed " + passed + " of " + cases.size());
    }

    static String[] withHome(Path home, String[] rest) {
        String[] full = new String[rest.length + 2];
        full[0] = "--vault";
        full[1] = home.toString();
        System.arraycopy(rest, 0, full, 2, rest.length);
        return full;
    }

    static PrintStream sink() {
        return new PrintStream(new ByteArrayOutputStream());
    }
}
```

```text
quill - a command-line vault

usage:
  quill [--vault <dir>] <command> [arguments]

commands:
  help                 show this text
  add <title>          add a note; the body is read from standard input
  list                 list every note
  show <id>            print one note
  delete <id>          remove one note
```

Five files and one test, and the boundaries are worth reading off the listing:

- `Main` owns the streams, the usage text and the exit codes. It is the only file that knows all the
  others.
- `Options` turns `args` into a home directory and a remainder. It knows nothing about commands.
- `Commands` turns that remainder into a value. It knows nothing about files.
- `Vault` owns the file. It knows nothing about the command line.
- `Note` owns the format — the separator, the escaping, `render` and `parse`. It knows nothing at all.
- `SelfTest` is not part of the program. It is a second `main` that drives the first.

The arrows all point one way. `Main` mentions all four of the others; `Vault` mentions `Note`; nothing
mentions `Main`. **That direction is the reason the next section is possible**: a file that does not
know about `Main` cannot be broken by testing `Main`, and `Main` can be driven by a second entry point
without either one knowing about the other.

Printing the usage text for a bare `quill` is a decision from Chapter 20, and it is worth restating
because it is the kind of decision that gets made by accident. Running the program with no arguments
exits `0`, not `2`. Typing `quill` is not an error; it is a request for help.

## The exit code is the program's public interface

Everything else in this book has been about a program's behaviour toward a *reader*. A command-line
tool has a second audience: the script that called it. That script cannot see your types, your records
or your sealed hierarchies. It sees two things — what came out on which stream, and the number the
process returned.

So the numbers are a contract, and they belong in a table:

| code | meaning | written to |
| --- | --- | --- |
| `0` | success | stdout |
| `2` | the command line was malformed | stderr, then the usage text |
| `4` | an I/O failure | stderr |
| `5` | the note named does not exist | stderr |

The split between `2` and `5` is the one worth defending, and the argument is about the *caller*.
`quill show 9` is a well-formed request for something that is not there: the script asked a sensible
question and got the answer "no". `quill show seven` is not a well-formed request at all — the script
has a bug. A script can act on that difference: `5` means "handle the missing note", `2` means "stop,
the caller is broken". Two malformed-argument codes, which is what Chapters 20 to 22 had, mean nothing
to a caller, because there is no action that distinguishes them. That is why Chapter 23 retired `3`.

:::tip
The exit code is not the only part of the interface. Which stream a message goes to is part of it too.
`quill list` writes notes to stdout; `quill: no note #9` goes to stderr. A script that does
`notes=$(quill list)` gets only the notes, and a script that does `quill list 2>/dev/null` loses only
the errors. Write a diagnostic to stdout and you have corrupted the data stream — which is why every
`err.println` in `Main` is an `err` and not an `out`.
:::

## A test that drives the real program

The test is a `main` of its own, and it drives `Main.run` — the same method the real program calls:

```sh run-project
say() {
  printf '%s\n' "$1"
}

say '$ java -cp out SelfTest'
java -cp out SelfTest 2>&1
echo "  -> exit $?"
```

```text
$ java -cp out SelfTest
(none)           expected 0, got 0  ok
list             expected 0, got 0  ok
add Groceries    expected 0, got 0  ok
list             expected 0, got 0  ok
show 1           expected 0, got 0  ok
show 2           expected 5, got 5  ok
delete 1         expected 0, got 0  ok
delete 1         expected 5, got 5  ok
show seven       expected 2, got 2  ok
frobnicate       expected 2, got 2  ok

passed 10 of 10
  -> exit 0
```

Ten cases, and the first thing to notice is that they are a **sequence**, not ten independent tests.
Case 3 adds a note that case 5 shows and case 7 deletes; case 8 then asks for it again and expects `5`.
Run the cases in a different order and the expected codes are wrong. That is not a flaw in the test —
it is the behaviour a user has, expressed as a table. A user adds a note, lists it, shows it, deletes
it and deletes it again, and the program's answers are `0, 0, 0, 0, 5`.

`show 2` expecting `5` is the row that proves the sequence is real. At that point in the table exactly
one note exists, so asking for the second one is a legitimate question with a "no" for an answer, and
the test pins that down.

The vault is `Files.createTempDirectory("quill-selftest")` — created once, by the test, outside the
source tree. Nothing in the run touches the directory you launched it from.

## Why a test cannot call `main`

Here is the question the previous section skipped. `Main` has a `main`. Why does the test call `run`
instead? The answer is one method call long, and it is the most transferable thing in this chapter:

```sh run-project
say() {
  printf '%s\n' "$1"
}

cat > Driver.java <<'JAVA'
public class Driver {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader in =
                new java.io.BufferedReader(new java.io.StringReader(""));
        java.io.PrintStream sink =
                new java.io.PrintStream(new java.io.ByteArrayOutputStream());
        String[] argv = {"--vault", "demo", "show", "7"};

        if (args[0].equals("main")) {
            Main.main(argv);
            System.out.println("main returned");
        } else {
            int code = Main.run(argv, in, sink, sink);
            System.out.println("run returned " + code);
            System.out.println("so the next case in the table still runs");
        }
    }
}
JAVA

javac -cp out -d out Driver.java

say '$ java -cp out Driver main'
java -cp out Driver main 2>&1
echo "  -> exit $?"
echo
say '$ java -cp out Driver run'
java -cp out Driver run 2>&1
echo "  -> exit $?"
```

```text
$ java -cp out Driver main
quill: no note #7
  -> exit 5

$ java -cp out Driver run
run returned 5
so the next case in the table still runs
  -> exit 0
```

The two runs differ by exactly one call. `Driver main` calls `Main.main(argv)`, which prints
`quill: no note #7` and then calls `System.exit(5)`. The process ends. `main returned` is never
printed, because **`System.exit` does not return** — it terminates the JVM, and no statement after it
in any frame gets to run.

`Driver run` calls `Main.run(argv, in, sink, sink)`, gets `5` back, prints it, and carries on. That
`so the next case in the table still runs` line is not decoration; it is the entire reason the
self-test can report `passed 10 of 10` instead of stopping at the first failure.

Which gives the rule:

> **A method that calls `System.exit` is a method no test can call.**

So the program is split in two, and the split is a boundary between two different things. `main` is
process management: build the streams, call `run`, flush, and translate a non-zero result into a
process exit code. `run` is the program: parse, execute, return a number. The number is a value, and
values can be asserted on.

The streams are arguments for the same reason. `System.out` and `System.err` are process globals;
`run` takes `BufferedReader in, PrintStream out, PrintStream err` and the test passes a `StringReader`
and two `PrintStream`s wrapping a `ByteArrayOutputStream`. A test that captures `System.out` with
`System.setOut` works, and it is global mutable state that two tests cannot share — the same disease
one level up. **A dependency you pass in is a dependency a test can control.**

:::pitfall
Note that `run` is declared with no access modifier, so it is package-private. That is deliberate and
it is a constraint worth understanding: `SelfTest` is in the same (default) package, so it can see
`run`, and nothing outside can. If you ever move the test into its own package you will have to widen
`run` to `public` — and that is a real decision, because `public` on a `run` that returns an exit code
is an invitation for someone to call it from their own program. Test visibility is a design pressure,
not an accident.
:::

## Packaging: a jar with a main class

The program is finished and tested. Shipping it means producing one file that another machine can run
without knowing anything about your source tree:

```sh run-project
say() {
  printf '%s\n' "$1"
}

say '$ javac -Xlint:all -Werror --release 21 -d out *.java'
javac -Xlint:all -Werror --release 21 -d out *.java
echo "  -> exit $?"
echo
say '$ jar --create --file quill.jar --main-class Main -C out .'
jar --create --file quill.jar --main-class Main -C out .
echo "  -> exit $?"
echo
say '$ java -jar quill.jar list'
java -jar quill.jar list 2>&1
echo "  -> exit $?"
echo
say '$ jar --create --file plain.jar -C out .'
jar --create --file plain.jar -C out .
say '$ java -jar plain.jar list'
java -jar plain.jar list 2>&1
echo "  -> exit $?"
```

```text
$ javac -Xlint:all -Werror --release 21 -d out *.java
  -> exit 0

$ jar --create --file quill.jar --main-class Main -C out .
  -> exit 0

$ java -jar quill.jar list
no notes yet
  -> exit 0

$ jar --create --file plain.jar -C out .
$ java -jar plain.jar list
no main manifest attribute, in plain.jar
  -> exit 1
```

Four commands, and the second and third are the pair that matters. `jar --create --file quill.jar
--main-class Main -C out .` builds an archive; `java -jar quill.jar list` runs it. Between them is a
manifest entry that was written for you: `Main-Class: Main`.

A jar is a zip file with a `META-INF/MANIFEST.MF` inside it, and `java -jar` is `java` reading that
manifest to find out which class to start. There is no magic beyond that, which is why the last two
commands fail the way they do. `plain.jar` is built from the same classes with no `--main-class`, and
`java -jar plain.jar list` reports:

```text
no main manifest attribute, in plain.jar
```

and exits `1`. The classes are all there. The archive is a perfectly good jar. What is missing is the
one line that says where to begin — and that is a distinction worth having in your head, because
`no main manifest attribute` and `Could not find or load main class` are different failures with
different fixes, and a classpath problem will not be reported as a manifest problem.

Two details of the `jar` command are easy to get wrong and worth naming:

- `-C out .` means "change to `out`, then add `.`". It exists so that the paths recorded in the
  archive are `Main.class` and `Note.class` — at the top level, where the JVM expects them — rather
  than `out/Main.class`. The archive's internal layout is the classpath.
- `javac -d out` is what created that layout in the first place. `-d` is the mirror image of `-C`:
  one writes the tree, the other reads it.

## A sealed hierarchy is closed

There is one more property of the design that only shows up once other people use the code, and it is
the last thing `sealed` buys:

```java bad
sealed interface Command permits Command.ListNotes {
    record ListNotes() implements Command {}
}

class Intruder implements Command {}
```

```text
error: class is not allowed to extend sealed class: Command (as it is not listed in its 'permits' clause)
class Intruder implements Command {}
```

`Intruder` is in the same file, implements `Command`, and is not in the `permits` clause. javac refuses
it: `class is not allowed to extend sealed class: Command (as it is not listed in its 'permits'
clause)`.

Read the message carefully, because it says *class* about an interface. That is javac reusing the
wording from the class case; the rule is the same either way. What matters is the consequence for the
program in the previous section: because the set of commands is fixed at compile time, `execute` in
`Main` can be written as a `switch` expression with **no `default` arm**, and the compiler checks that
every case is covered.

Those two facts are the same fact. A non-sealed interface would let a third party add a command, and a
`switch` that must tolerate unknown commands needs a `default` arm — and a `default` arm is exactly
what stops the compiler telling you that you forgot to handle the new one. **`sealed` is what buys the
exhaustiveness check.** The price is stated plainly in the same error message: your program is
extensible exactly where you said it is, and nowhere else.

## Driving the shipped artifact

Seven commands against the compiled classes, in one vault, in order:

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
say '$ printf "chapter 23\n" | quill add Reading'
printf 'chapter 23\n' | quill add Reading
echo
say '$ quill list'
quill list
echo
say '$ quill show 2'
quill show 2
echo
say '$ quill delete 1'
quill delete 1
echo
say '$ quill delete 1'
quill delete 1
echo
say '$ quill --vault other list'
quill --vault other list
```

```text
$ printf "milk and eggs\n" | quill add Groceries
added #1 Groceries (13 character(s))
  -> exit 0

$ printf "chapter 23\n" | quill add Reading
added #2 Reading (10 character(s))
  -> exit 0

$ quill list
#1  Groceries  milk and eggs
#2  Reading  chapter 23
  -> exit 0

$ quill show 2
#2  Reading
chapter 23
  -> exit 0

$ quill delete 1
deleted #1
  -> exit 0

$ quill delete 1
quill: no note #1
  -> exit 5

$ quill --vault other list
no notes yet
  -> exit 0
```

Every line here has been earned by an earlier chapter, which is the point of a capstone. `add` reads
its body from standard input, so the pipe is the input — `(13 character(s))` is the length of
`milk and eggs`, not of the title. `list` prints two notes with the ids `nextId` assigned. `show 2`
prints the title line and then the body. The sixth command deletes note 1 a second time and reports
`quill: no note #1` with exit `5` — the code that means "you named something that is not there".
And `quill --vault other list` prints `no notes yet`, which is the `--vault` option doing its job: a
different home directory is a different vault, and this one is empty because nothing was added to it.

:::scenario The suite that passed on one machine

A two-person team has a test suite like the one in this chapter, and it passes on one laptop and fails
on the other. The failing case is `show 1`, which expects `0` and gets `5`.

The difference is not the code. It is that the test's vault directory is `Path.of("vault")` — a
relative path, resolved against whatever directory the test was launched from — and the suite never
removes it. On the machine where it passes, a `vault/` left over from yesterday's manual testing is
sitting in the working directory, with a note in it. On the clean checkout, there is nothing there.

:::solution
The failure is real and the test is wrong, and it is wrong in a specific way: **it depends on the
working directory, so it is testing the machine rather than the program.**

```java run
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class Scenario {
    static List<String> entries(Path dir) throws Exception {
        try (var stream = Files.list(dir)) {
            return stream.map(p -> p.getFileName().toString()).sorted().toList();
        }
    }

    public static void main(String[] args) throws Exception {
        Path work = Path.of("scenario-work");
        Files.createDirectories(work);

        Path leaked = work.resolve("vault");
        Files.createDirectories(leaked);
        System.out.println("after a test with no --vault, " + work.getFileName()
                + " contains " + entries(work));

        Files.delete(leaked);
        System.out.println("after a test with --vault,    " + work.getFileName()
                + " contains " + entries(work));

        System.out.println();
        System.out.println("the first run left state behind that the second run would have found");
    }
}
```

```text
after a test with no --vault, scenario-work contains [vault]
after a test with --vault,    scenario-work contains []

the first run left state behind that the second run would have found
```

The first line is the state a run without `--vault` leaves behind: a `vault` directory inside the
working directory, which the next run will find. The second line is the same measurement with
`--vault` pointed at a directory the test owns, and the working directory is untouched. (The block
removes the directory between the two lines, so the comparison is fair.)

The repair is one line in the test and it is already in `SelfTest`:

```java
Path home = Files.createTempDirectory("quill-selftest");
```

Every run gets a directory of its own, and no run can see another run's notes. Note the second-order
consequence: `createTempDirectory` is called **once** for the whole table, not once per case, and that
is deliberate — the ten cases are a sequence and they must share a vault. Fresh per *run*, shared
within a run, is the rule that makes a sequence test both meaningful and repeatable.

There is a generalisation here worth carrying away. Any test that reads or writes a path it did not
create has a hidden input, and a hidden input is a test that will pass on your machine for a reason
that is not in the code. The `--vault` option exists for the user; the test uses it to stop depending
on the user's directory.
:::

## Solutions

### 1. A self-test you can write in one screen

The smallest version of the previous test has no files in it at all:

```java run
import java.util.List;

public class Sol1 {
    static final int OK = 0;
    static final int USAGE = 2;
    static final int NOT_FOUND = 5;

    record Case(String label, String[] args, int expected) {}

    static int run(String[] args, List<String> notes) {
        if (args.length == 0) {
            return OK;
        }
        return switch (args[0]) {
            case "help", "list" -> OK;
            case "add" -> args.length >= 2 ? OK : USAGE;
            case "show", "delete" -> {
                if (args.length < 2) {
                    yield USAGE;
                }
                int id;
                try {
                    id = Integer.parseInt(args[1]);
                } catch (NumberFormatException e) {
                    yield USAGE;
                }
                yield notes.contains(String.valueOf(id)) ? OK : NOT_FOUND;
            }
            default -> USAGE;
        };
    }

    public static void main(String[] args) {
        List<String> notes = List.of("1", "2");
        Case[] cases = {
            new Case("(none)", new String[] {}, OK),
            new Case("list", new String[] {"list"}, OK),
            new Case("add T", new String[] {"add", "T"}, OK),
            new Case("add", new String[] {"add"}, USAGE),
            new Case("show 1", new String[] {"show", "1"}, OK),
            new Case("show 9", new String[] {"show", "9"}, NOT_FOUND),
            new Case("show seven", new String[] {"show", "seven"}, USAGE),
            new Case("frobnicate", new String[] {"frobnicate"}, USAGE),
        };

        int passed = 0;
        for (Case c : cases) {
            int actual = run(c.args(), notes);
            boolean ok = actual == c.expected();
            if (ok) {
                passed++;
            }
            System.out.printf("%-16s expected %d, got %d  %s%n",
                    c.label(), c.expected(), actual, ok ? "ok" : "FAIL");
        }
        System.out.println("passed " + passed + " of " + cases.length);
    }
}
```

```text
(none)           expected 0, got 0  ok
list             expected 0, got 0  ok
add T            expected 0, got 0  ok
add              expected 2, got 2  ok
show 1           expected 0, got 0  ok
show 9           expected 5, got 5  ok
show seven       expected 2, got 2  ok
frobnicate       expected 2, got 2  ok
passed 8 of 8
```

Eight cases, and `run` here is a pure function of `(args, notes)`: no vault, no I/O, no streams. This
is the version to sketch a design with, because the whole command-line contract fits on one screen and
the test costs nothing to run. `SelfTest` is what you write afterwards, when the question has become
"does the file format actually round-trip".

The two rows to compare are `show 9` and `show seven`. They expect `5` and `2`, and the difference is
the distinction the exit-code table was built on: `9` is a legitimate question about a note that is
not there, `seven` is not a question the program can answer at all. A single "error" code would have
collapsed them, and the test would have been unable to state the difference.

### 2. The help text can be derived from the hierarchy

Chapter 23's practice problems pointed out that the usage text is prose, and prose is not
type-checked — add a command and the help text can go stale without anything failing. Here is the part
of it that can be generated instead:

```java run
import java.util.Arrays;

public class Sol2 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Help {

        record Add(String title) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Help() implements Command {}
    }

    static String commands() {
        return Arrays.stream(Command.class.getPermittedSubclasses())
                .map(Class::getSimpleName)
                .sorted()
                .reduce((a, b) -> a + ", " + b)
                .orElse("");
    }

    public static void main(String[] args) {
        System.out.println(commands());
        System.out.println();
        System.out.println("the list comes from the hierarchy, so a new command cannot be forgotten");
    }
}
```

```text
Add, Delete, Help, ListNotes, Show

the list comes from the hierarchy, so a new command cannot be forgotten
```

`Add, Delete, Help, ListNotes, Show`, straight out of `getPermittedSubclasses()`. A new command appears
in this list because it had to be added to `permits`, which the compiler already enforces. There is no
second place to update, and therefore no way to forget.

Two caveats, both worth having in mind before you replace your usage text with this.

The order is sorted by hand, because `getPermittedSubclasses()` returns the classes in the order the
`PermittedSubclasses` attribute lists them. That happens to be the order you wrote `permits`, and
relying on it across compilers and versions would be relying on something nobody promised. Sorting
costs one call and removes the question.

And this gives you the command *names*, not their syntax. `add <title>` is a fact about how many
arguments `Add` takes and what they mean, and no reflection can recover it. So this replaces the list
of commands in the help text and not the help text. The honest version of the generated help is a line
per command assembled from the hierarchy *plus* a hand-written fragment describing the arguments —
which is a real design, and it is the one most CLI libraries end up at.

### 3. A body with newlines survives the format

The round-trip property Chapter 22 built is worth one explicit test, because it is the assertion that
catches an escaping bug and nothing else does:

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

// ===== Vault.java =====

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
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

    boolean delete(int id) throws IOException {
        List<Note> kept = new ArrayList<>();
        boolean removed = false;
        for (Note note : read()) {
            if (note.id() == id) {
                removed = true;
            } else {
                kept.add(note);
            }
        }
        if (!removed) {
            return false;
        }
        rewrite(kept);
        return true;
    }

    private void rewrite(List<Note> notes) throws IOException {
        Files.createDirectories(home);
        StringBuilder out = new StringBuilder(HEADER).append('\n');
        for (Note note : notes) {
            out.append(note.render()).append('\n');
        }
        Path temp = file().resolveSibling(FILE + ".tmp");
        Files.writeString(temp, out.toString(), StandardCharsets.UTF_8);
        Files.move(temp, file(), StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
    }
}

// ===== Sol3.java =====

import java.nio.file.Files;
import java.nio.file.Path;

public class Sol3 {
    public static void main(String[] args) throws Exception {
        Path home = Path.of("sol3-vault");
        Vault vault = new Vault(home);

        String body = "line one\nline two\nline three";
        Note note = new Note(vault.nextId(), "Multi-line", body);
        vault.append(note);

        System.out.println("in memory  = " + note.body().length() + " character(s), "
                + note.body().split("\n").length + " line(s)");
        System.out.println("on disk    = "
                + Files.readAllLines(vault.file()).size() + " line(s)");
        System.out.println("read back  = " + vault.read().get(0).equals(note));
    }
}
```

```text
in memory  = 28 character(s), 3 line(s)
on disk    = 2 line(s)
read back  = true
```

The body is `line one\nline two\nline three`: 28 characters and three lines in memory. On disk the
vault has **two** lines — the header, and one line for the note — because the newlines inside the body
are escaped. The escaping is not visible in the second number; what it means is that a line count on
disk is not a note count.

`read back = true` is the line that matters. `Note` is a record, so `equals` compares all three
components field by field, and the assertion is "the note that came out of the file is the note that
went in". That is a *property*, and it is the only kind of assertion that would have caught the
escape-order bug from Chapter 22 — where the stored form was wrong and the decoded form was wrong in a
way that happened to cancel out for most inputs. A test that asserted on the file's contents would
have had to restate the escaping rules, and would therefore have agreed with whatever the
implementation did.

### 4. One boolean instead of a scattered dry-run

A `--dry-run` flag is a small feature that is usually implemented badly, and the sealed hierarchy
makes the good version short:

```java run
public class Sol4 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Help {

        record Add(String title) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Help() implements Command {}
    }

    static boolean mutates(Command command) {
        return switch (command) {
            case Command.Add a -> true;
            case Command.Delete d -> true;
            case Command.ListNotes n -> false;
            case Command.Show s -> false;
            case Command.Help h -> false;
        };
    }

    public static void main(String[] args) {
        Command[] commands = {
            new Command.Add("Groceries"),
            new Command.ListNotes(),
            new Command.Show(1),
            new Command.Delete(1),
            new Command.Help(),
        };

        for (Command command : commands) {
            System.out.printf("%-10s mutates=%b%n",
                    command.getClass().getSimpleName(), mutates(command));
        }

        System.out.println();
        System.out.println("--dry-run becomes one boolean on the command, checked in one place");
    }
}
```

```text
Add        mutates=true
ListNotes  mutates=false
Show       mutates=false
Delete     mutates=true
Help       mutates=false

--dry-run becomes one boolean on the command, checked in one place
```

`mutates` is an exhaustive switch with no `default`: `Add` and `Delete` return `true`, the other three
return `false`. With that in hand, `--dry-run` is one check in one place — refuse to execute a command
for which `mutates` is `true` — instead of a flag consulted inside each arm of `execute`.

The scattered version is the one to picture, because it is what most programs do. Five arms, and each
one has to remember to look at the flag. The sixth command will forget, and the bug is a `--dry-run`
that silently writes to the vault. Here, adding a command makes the compiler ask you the question:
a new record in `permits` stops this switch compiling until you have answered `true` or `false`.

**That is the property to look for in a design: the compiler asking you the question you would
otherwise forget.** It is the same property that made `execute` exhaustive in Chapter 20, applied to a
question that has nothing to do with execution.

## Key takeaways

- A command-line tool has two audiences. The reader sees the text; the calling script sees the exit
  code and which stream each line went to. Both are the interface, and both belong in the docs.
- Give each failure its own code only when a caller can act on the difference. `5` (not there) and `2`
  (malformed) are different actions; two flavours of malformed argument are not.
- `System.exit` does not return. **A method that calls `System.exit` is a method no test can call** —
  so keep the program in `run` and the process management in `main`.
- Pass the streams in. `System.out` is a process global and global mutable state is what stops two
  tests sharing a process.
- A test that depends on the working directory is testing the machine. Create the directory you use;
  fresh per run, shared within a run.
- Test the sequence, not the cases. `add`, `list`, `show`, `delete`, `delete` in one vault is the
  behaviour a user has, and the expected codes only make sense in that order.
- `jar --create --main-class Main` writes `Main-Class` into the manifest; `java -jar` reads it. A jar
  without it fails with `no main manifest attribute` while every class inside is fine.
- `-C out .` in a `jar` command is the mirror of `javac -d out`: one writes the class tree, the other
  archives it from the right directory. The archive's internal layout *is* the classpath.
- `sealed` plus `permits` is what lets a `switch` have no `default` arm — and a `default` arm is
  exactly what stops the compiler telling you that a new case is unhandled.
- An outsider cannot implement a sealed interface: `class is not allowed to extend sealed class`. The
  price of the exhaustiveness check is that your program is extensible only where you said it is.
- A round-trip assertion (`read back = true`) is the only kind of test that catches an escaping bug,
  because it does not have to restate the escaping rules to make its claim.

## Practice

- [ ] Add a `quill count` command that prints how many notes there are, and add a case to `SelfTest`.
      Which of the ten existing cases change, and why is the answer "none"?
- [ ] Change `SelfTest` so each case gets its own `Files.createTempDirectory`. Which cases stop being
      meaningful, and what does that tell you about "test independence"?
- [ ] Write a driver that runs the ten cases through `Main.main` in ten separate JVM launches. Compare
      what it can assert with what the current table can assert.
- [ ] Package `quill` as a jar and run `java -jar quill.jar list` from a directory that contains no
      `vault/`. Then add a note and find the file. Decide whether that default location is right.
- [ ] Add `--version`. Is it an option or a command? Justify the choice against `--vault`, which is an
      option because it changes where the program looks.
- [ ] Make `execute` return a value describing what to print instead of printing directly, and have
      `run` do the printing. What does `SelfTest` gain, and what does `execute` cost?

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. None of the ten change, and that is the answer worth having. The table is a sequence of
   *mutations*, and `count` does not mutate, so inserting it anywhere leaves every later id where it
   was. Insert an `add` instead and every later `show 1` and `delete 1` shifts by one. The property
   being demonstrated is that a read-only command is additive to a sequence test and a mutating one is
   not — which is the practical reason to keep the mutating commands in one visible place.
2. Cases 3, 5 and 7 break. `show 1` needs the note that `add Groceries` wrote, and `delete 1` needs
   that same note to exist before it can be deleted; give each case its own vault and both become
   meaningless — `show 1` would expect `5`, and the table would no longer describe a user's session.
   This is the tension worth naming: **per-case isolation and sequence testing are opposites**, and
   you have to choose. Isolation is right for a unit test of `Vault`; a sequence is right for an
   end-to-end test of the command line, and this is the end-to-end one.
3. Ten launches give you the strongest possible isolation — each case is a real process, with a real
   working directory and a real exit code — and they cost a JVM startup each. What they *lose* is the
   sequence: the ten cases can no longer share a vault, so "add then show then delete" cannot be
   expressed at all. What they *gain* is that `System.exit` is now testable, since there is a process
   to observe. The reason `run` exists is that the first version buys almost everything the second one
   does, for none of the cost. Use separate processes to test the wrapper — that `main` turns `5` into
   exit code `5` — and `run` for everything else.
4. The vault is `vault/` **relative to the process working directory**, so `java -jar
   /path/to/quill.jar list` run from `~/tmp` reads and writes `~/tmp/vault/`. Run it from two
   directories and you have two vaults, which is either a feature or the bug report you get first. The
   repair is a default under the user's home — `System.getProperty("user.home")` plus a subdirectory —
   with `--vault` kept as the override. Note that this makes the default depend on an environment
   property, so the test must always pass `--vault`, which is exactly what `SelfTest` does.
5. `--version` should be a command. The rule that keeps `Options` small is that it handles the things
   which change *where the program looks*, and `--vault` is the only one; `version` changes nothing
   about the vault. Making it an option also raises a question with no good answer — what should
   `quill --version list` do? Print the version and exit, or print the version and list? One rule,
   options first and then exactly one command, is easier to document than a special case, and the
   special case is the one users will trip over.
6. `execute` returns something like a `Result` record holding the exit code and the lines to print;
   `run` prints it and returns the code. `SelfTest` gains a much stronger assertion — it can check the
   *message*, not only the number, which is how you would catch a diagnostic that started going to the
   wrong stream. `execute` pays for it by constructing a value in every arm instead of calling
   `out.println`, and `run` gains a printing step. It is the same shape as Chapter 23's parse-then-act
   split, one level down: **a method that computes and a method that prints are easier to test
   separately than a method that does both.**
