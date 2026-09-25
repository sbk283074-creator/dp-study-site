---
chapter: 23
part: 3
title: A Command Layer and Argument Parsing
summary: Turn the strings a user typed into a value your program can switch on, so that every malformed command is rejected in one place and every valid one is handled somewhere the compiler can check.
minutes: 55
tags: [cli, argument parsing, sealed types, exceptions, design]
---

Chapter 20 sketched a sealed command hierarchy and then did not use it: `Main` switched on
`args[0]`, a `String`. This chapter makes the sketch real. The change is small in code and large in
consequence — arguments are parsed into a value *once*, before anything is executed, and from that
point the rest of the program works with a type that cannot be malformed. It is the difference between
a program that checks its input in five places and one that checks it in one.

## A string array is a poor thing to switch on

`String[] args` is what the JVM hands you, and it has no structure at all. `args[0]` might be a
command, might be an option, might be a typo. `args[1]` means a title for `add`, an id for `show`, and
nothing for `list`. Every one of those facts lives in the head of whoever wrote the dispatcher.

That is survivable for four commands. It stops being survivable the moment the rules are worth
writing down, because a `switch` on a `String` cannot express them:

- Nothing connects the label `"list"` to the fact that `list` takes no arguments.
- Nothing stops `args[1]` being read when `args.length` is 1.
- Nothing tells you, when you add a fifth command, that you forgot to handle it somewhere.

The fix is to spend the first few lines of the program turning the strings into a **value**, and then
never look at the strings again.

## Parse into a value, then act on the value

The command layer is a sealed interface with one record per command, and a `parse` that returns one of
them:

```java run-files
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

// ===== ParseDemo.java =====

public class ParseDemo {
    public static void main(String[] args) {
        String[][] cases = {
            {},
            {"help"},
            {"list"},
            {"add", "Groceries"},
            {"add"},
            {"show", "7"},
            {"show"},
            {"show", "seven"},
            {"show", "0"},
            {"delete", "3"},
            {"frobnicate"},
        };

        for (String[] c : cases) {
            String label = c.length == 0 ? "(none)" : String.join(" ", c);
            try {
                Commands command = Commands.parse(c);
                System.out.printf("%-20s -> %s%n", label, Commands.describe(command));
            } catch (Commands.UsageException e) {
                System.out.printf("%-20s -> usage: %s%n", label, e.getMessage());
            }
        }
    }
}
```

```text
(none)               -> help
help                 -> help
list                 -> list
add Groceries        -> add "Groceries"
add                  -> usage: add needs a title
show 7               -> show #7
show                 -> usage: show <id> needs an id
show seven           -> usage: 'seven' is not an id
show 0               -> usage: ids start at 1, not 0
delete 3             -> delete #3
frobnicate           -> usage: unknown command 'frobnicate'
```

Eleven inputs, and every one of them is answered. The first block is worth reading carefully because
it contains the whole design in miniature.

`parse` takes the array and returns a `Commands`. It does not execute anything, it does not print
anything, and it does not touch a file. `new Help()` for an empty array is a decision — a bare `quill`
is a request for help, not an error — and because it is a decision it is visible here rather than
buried in a branch.

Then the errors. `add` with no title, `show` with no id, `show seven`, `show 0`, and `frobnicate` all
produce a `UsageException` carrying a message a user can act on. `usage: show <id> needs an id` and
`usage: 'seven' is not an id` are different failures and they say so; `usage: ids start at 1, not 0` is
the range check from Chapter 22's format surfacing at the command line, where it belongs.

The `describe` method is the same exhaustive switch from Chapter 20, and it exists because a transcript
is easier to read than a `toString`. In the real program the second switch *executes*.

:::tip
Keep `parse` and the executor apart, and notice what each one is allowed to know. `parse` knows about
strings and about what a well-formed command looks like. The executor knows about vaults and notes and
streams. Neither knows what the other knows, and the seam between them is one method call.
:::

## The parse throws, and that is the design

`UsageException` extends `IllegalArgumentException`, and it is thrown rather than returned. That is a
choice worth defending, because returning `null` or an `Either` is fashionable.

A usage error is exceptional in the literal sense: it happens once, at startup, and it ends the
program. It is not a value the program goes on to compute with. Making it an exception means the happy
path — `parse`, then execute — reads as two statements with no error plumbing between them, and the
single `catch` in `Main` turns it into an exit code:

```java
try {
    invocation = Options.parse(args);
    command = Commands.parse(invocation.rest());
} catch (IllegalArgumentException e) {
    err.println("quill: " + e.getMessage());
    err.print(USAGE_TEXT);
    return USAGE;
}
```

The one thing that must not happen is for the exception to escape as a stack trace. A user who types
`quill show seven` should not see twenty lines of `at Main.run(Main.java:41)`. **Catch it at the
boundary, print the message, print the usage, return `2`.** The stack trace is for the developer; the
message is for the user; they are different audiences and the boundary is where you choose.

**This retires exit code `3`.** Chapters 20 to 22 returned `3` for `add` with no title and `2` for an
unknown command — two codes for two failures a user cannot tell apart, since both mean "the command
line was malformed" and both print the same usage text. Now that every malformed command goes through
one parser, there is one code for it, and it is `2`. A published contract that changes should say so
out loud: a script that tested for `3` will see `2` from this chapter on, and the exit-code table is
exactly where a reader would go looking for the difference.

## An arm that can never be reached is a compile error

The sealed hierarchy is not only a way to make the executor exhaustive. It also lets javac find arms
that are *dead*, which is the same guarantee from the other direction:

```java bad
public class Dominated {
    sealed interface Shape permits Circle, Square {}

    record Circle(double radius) implements Shape {}

    record Square(double side) implements Shape {}

    static String name(Shape shape) {
        return switch (shape) {
            case Shape any -> "a shape";
            case Circle c -> "circle";
            case Square s -> "square";
        };
    }

    public static void main(String[] args) {
        System.out.println(name(new Circle(1)));
    }
}
```

```text
error: this case label is dominated by a preceding case label
```

`case Shape any` matches every `Shape`, so the two arms after it can never run. javac says so:
`this case label is dominated by a preceding case label`. The file does not compile, and the reason is
worth pausing on — a type pattern for the sealed interface itself is a valid arm, and writing it first
silently disables everything below it.

In a `String` switch the equivalent mistake is unreachable in a different way: `case "list"` written
twice is a duplicate-label error, but a `default` placed first is perfectly legal and swallows
everything. The sealed version refuses the broad arm in front of the narrow ones, which is the more
useful check.

## A serializable exception wants a `serialVersionUID`

`UsageException` extends `IllegalArgumentException`, and `Throwable` implements `java.io.Serializable`.
That inheritance has a consequence that `-Xlint:all` will point out:

```java warn
public class WarnSerial {
    static class UsageException extends RuntimeException {
        UsageException(String message) {
            super(message);
        }
    }

    public static void main(String[] args) {
        System.out.println(new UsageException("missing argument").getMessage());
    }
}
```

```text
warning: [serial] serializable class UsageException has no definition of serialVersionUID
```

`warning: [serial] serializable class UsageException has no definition of serialVersionUID`.

This is the one place in the book where the answer to a warning is *suppress it*, and it is worth
understanding why rather than reaching for the annotation out of habit. Java's serialization machinery
computes a version number for a class so that it can refuse to read bytes written by an incompatible
version. For a value type that gets persisted, that check is doing real work. For an exception that is
thrown, caught and discarded inside one process, nothing is ever serialized, so the number is dead
weight — and computing it costs a warning every time you add a method.

So the class says so:

```java
@SuppressWarnings("serial")
class UsageException extends IllegalArgumentException {
    UsageException(String message) {
        super(message);
    }
}
```

Note the shape of the argument, because it is the argument for every suppression. **You are not
silencing a warning; you are recording that the warning does not apply, at the one place a reader will
look.** A `@SuppressWarnings` on a method that swallows a real problem is a bug; this one is
documentation.

## Options come before the command

`--vault <dir>` has to be understood before the command is parsed, because it changes where the
command will look. That makes it a separate concern from `Commands.parse`, and it gets its own type:

```java run-files
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

// ===== OptionsDemo.java =====

import java.util.Arrays;

public class OptionsDemo {
    public static void main(String[] args) {
        String[][] cases = {
            {"list"},
            {"--vault", "/tmp/notes", "list"},
            {"--vault", "/tmp/notes", "add", "Groceries"},
            {"--vault"},
            {"--", "--vault", "list"},
        };

        for (String[] c : cases) {
            String label = String.join(" ", c);
            try {
                Options.Invocation invocation = Options.parse(c);
                System.out.printf("%-36s -> home %s, command %s%n",
                        label, invocation.home(), Arrays.toString(invocation.rest()));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-36s -> %s%n", label, e.getMessage());
            }
        }
    }
}
```

```text
list                                 -> home vault, command [list]
--vault /tmp/notes list              -> home /tmp/notes, command [list]
--vault /tmp/notes add Groceries     -> home /tmp/notes, command [add, Groceries]
--vault                              -> --vault needs a directory
-- --vault list                      -> home vault, command [--vault, list]
```

The loop consumes options from the front and stops at the first thing that is not one. Four cases and
one subtlety:

- `list` — no options, so the whole array is the command.
- `--vault /tmp/notes list` — the option is consumed, `[list]` is what the command layer sees.
- `--vault` with nothing after it — an error naming the option, not a crash on an array index.
- `--` — the terminator. Everything after it is a command argument even if it starts with a dash,
  which is what `-- --vault list` demonstrates: `--vault` is now a *command name*, and the command
  layer will reject it as unknown.

The last one is the reason `--` exists at all. Without it, there is no way to pass a value that looks
like an option, and a program that cannot represent a valid input is a program with a hole in it. You
have used this every time you typed `git checkout -- .`.

## Quill parses, then executes

The project now has five files, and the arrows between them are worth following. `Main` owns the
streams and the exit codes. `Options` turns `args` into a home directory and a remainder. `Commands`
turns the remainder into a value. `Vault` owns the file. `Note` owns the format.

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

`run` is three phases in ten lines. Parse — and if that fails, report and return. Then construct the
vault from the parsed home directory. Then hand both the command and the vault to `execute`, whose
switch is the only place in the program that knows what a command *does*.

Look at how little `execute` needs. It takes a `Commands`, a `Vault` and the streams. It does not take
`args`, and it could not read them if it wanted to, because by the time it is called they have been
consumed. **That is the whole point of parsing into a value: the malformed inputs are gone.** There is
no `args.length >= 3` check inside `add`, because `Add` cannot be constructed without a title.

Running it exercises every arm of that switch:

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

Two notes added, both listed, one shown, one deleted. Then the sixth command deletes note 1 a second
time and prints `quill: no note #1` with exit `5` — the code this chapter added for "you named
something that is not there". And the last line, `quill --vault other list`, prints `no notes yet`,
which is the option working: a different home directory is a different vault, and it is empty because
nothing has been added to it.

:::pitfall
**Parsing inside the executor is how the checks get duplicated.** The tempting version of `execute`
takes `String[] args` and does `Integer.parseInt(args[1])` in the `show` arm and again in the `delete`
arm — and now the range check, the error message and the exit code are written twice, and a third time
when `rename` arrives. The symptom is that `show abc` and `delete abc` report *slightly* different
errors, because they were written on different days. Parse once, in one place, into one type.
:::

:::scenario The delete that took two other notes with it

A teammate implements `quill delete <id>`. The implementation finds the line whose id matches, then
writes back everything **before** that line — a natural thing to reach for, because the file is
line-oriented and truncating is one call. A user deletes note 1 out of three and reports that notes 2
and 3 have vanished as well.

:::solution
The bug is not in the id matching. It is in the assumption that "remove an item from a sequence" means
"cut the sequence at that point". It means **keep everything that is not the item**, and those are the
same thing only when the item is last.

```java run
import java.util.ArrayList;
import java.util.List;

public class Scenario {
    static List<String> lines() {
        return new ArrayList<>(List.of(
                "# quill-2",
                "1\tGroceries\tmilk and eggs",
                "2\tReading\tchapter 23",
                "3\tDraft\tdelete me"));
    }

    static List<String> truncateAt(List<String> lines, int id) {
        for (int i = 0; i < lines.size(); i++) {
            if (lines.get(i).startsWith(id + "\t")) {
                return new ArrayList<>(lines.subList(0, i));
            }
        }
        return lines;
    }

    static List<String> filterOut(List<String> lines, int id) {
        List<String> kept = new ArrayList<>();
        for (String line : lines) {
            if (!line.startsWith(id + "\t")) {
                kept.add(line);
            }
        }
        return kept;
    }

    public static void main(String[] args) {
        System.out.println("before          = " + lines().size() + " line(s)");
        System.out.println("truncate at #1  = " + truncateAt(lines(), 1).size() + " line(s)");
        System.out.println("filter out #1   = " + filterOut(lines(), 1).size() + " line(s)");
        System.out.println();
        System.out.println("truncating keeps what came before the note and loses what came after");
    }
}
```

```text
before          = 4 line(s)
truncate at #1  = 1 line(s)
filter out #1   = 3 line(s)

truncating keeps what came before the note and loses what came after
```

Deleting note 1 by truncation leaves 1 line — the header, and nothing else. Deleting it by filtering
leaves 3: the header and the two notes that were never the target. The second number is the correct
one and the difference is not subtle, which is exactly why it is worth a test rather than a reading.

Two things made this bug possible, and both are worth naming.

The first is that the vault is a *list of lines* rather than a list of notes. `Vault.delete` in this
chapter reads every note, builds a new list containing the ones whose id differs, and rewrites — so
"remove one" is expressed as "keep the others" and there is no index to get wrong.

The second is that the rewrite is atomic. `delete` is the first operation that has to replace the
whole file, and Chapter 22's `rewrite` writes to a temporary file and moves it into place, so a crash
halfway through leaves the old vault rather than a truncated one. **A destructive command is exactly
where the atomic-write discipline earns its keep**, and it is not a coincidence that the first
destructive command is the first one that needs it.
:::

## Solutions

### 1. Adding a command, and what it costs

`rename` is the sixth command. Here it is, fully wired, in a hierarchy of its own:

```java run
public class Sol1 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Rename, Command.Help {

        record Add(String title) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Rename(int id, String title) implements Command {}

        record Help() implements Command {}
    }

    static String describe(Command command) {
        return switch (command) {
            case Command.Add a -> "add \"" + a.title() + "\"";
            case Command.ListNotes n -> "list";
            case Command.Show s -> "show #" + s.id();
            case Command.Delete d -> "delete #" + d.id();
            case Command.Rename r -> "rename #" + r.id() + " to \"" + r.title() + "\"";
            case Command.Help h -> "help";
        };
    }

    public static void main(String[] args) {
        Command[] commands = {
            new Command.Add("Groceries"),
            new Command.ListNotes(),
            new Command.Show(7),
            new Command.Delete(3),
            new Command.Rename(3, "Shopping"),
            new Command.Help(),
        };

        for (Command command : commands) {
            System.out.printf("%-10s %s%n",
                    command.getClass().getSimpleName(), describe(command));
        }

        System.out.println();
        System.out.println("6 permitted types, 6 arms, no default: one new case, one new arm");
    }
}
```

```text
Add        add "Groceries"
ListNotes  list
Show       show #7
Delete     delete #3
Rename     rename #3 to "Shopping"
Help       help

6 permitted types, 6 arms, no default: one new case, one new arm
```

`6 permitted types, 6 arms, no default: one new case, one new arm`. That is the claim worth checking
against the alternative. In the `String`-switch version of Chapter 20, adding a command meant editing
the dispatcher and *remembering* to edit the help text, the `describe` method if there was one, and
any test that enumerated the commands. Here the compiler enumerates them for you: add `Rename` to the
`permits` clause and every switch over `Command` in the program stops compiling until it has an arm.

The cost is proportional to the case, not to the number of places that must be told about it. That is
the property to look for in a design, and it is the reason the sealed hierarchy is worth the extra
type rather than a `String` and a `default`.

### 2. "Not found" is an exit code, not an exception

`delete` on an id that is not there is not a bug in the program. It is an answer, and it needs a code:

```java run
import java.util.ArrayList;
import java.util.List;

public class Sol2 {
    static final int OK = 0;
    static final int NOT_FOUND = 5;

    static int delete(List<Integer> ids, int id) {
        if (ids.remove(Integer.valueOf(id))) {
            return OK;
        }
        return NOT_FOUND;
    }

    public static void main(String[] args) {
        List<Integer> ids = new ArrayList<>(List.of(1, 2, 3));
        int[] attempts = {2, 2, 1, 3, 3};

        for (int id : attempts) {
            int code = delete(ids, id);
            System.out.printf("delete #%d -> exit %d, %d left %s%n",
                    id, code, ids.size(), ids);
        }

        System.out.println();
        System.out.println("the second attempt on the same id is not a failure of the vault");
    }
}
```

```text
delete #2 -> exit 0, 2 left [1, 3]
delete #2 -> exit 5, 2 left [1, 3]
delete #1 -> exit 0, 1 left [3]
delete #3 -> exit 0, 0 left []
delete #3 -> exit 5, 0 left []

the second attempt on the same id is not a failure of the vault
```

`delete #2 -> exit 0, 2 left [1, 3]` and then `delete #2 -> exit 5, 2 left [1, 3]`. The second attempt
removed nothing and reported `5`, and the vault is unchanged either way.

The design question is whether that second attempt should be an error at all. Two defensible answers:
`5` says "the thing you named is not here", which lets a script tell a typo from a success; `0` says
"the note you asked to be gone is gone", which makes the operation idempotent and a retry safe. What is
not defensible is throwing an exception — nothing went wrong, the user asked about a note that does not
exist, and the program knows the answer.

This chapter chose `5`, and the choice is visible in the exit-code table rather than hidden in a
branch. Whichever you pick, write it down, because a script author will build on it.

### 3. The id is validated once

`show`, `delete` and `rename` all take an id, and all three go through one function:

```java run
public class Sol3 {
    static int parseId(String raw) {
        int id;
        try {
            id = Integer.parseInt(raw);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("'" + raw + "' is not an id");
        }
        if (id <= 0) {
            throw new IllegalArgumentException("ids start at 1, not " + id);
        }
        return id;
    }

    public static void main(String[] args) {
        String[] inputs = {"3", "007", "+3", "0", "-1", " 3", "3 ", "", "abc", "2147483648"};

        for (String raw : inputs) {
            try {
                System.out.printf("%-14s -> %d%n", "'" + raw + "'", parseId(raw));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-14s -> %s%n", "'" + raw + "'", e.getMessage());
            }
        }
    }
}
```

```text
'3'            -> 3
'007'          -> 7
'+3'           -> 3
'0'            -> ids start at 1, not 0
'-1'           -> ids start at 1, not -1
' 3'           -> ' 3' is not an id
'3 '           -> '3 ' is not an id
''             -> '' is not an id
'abc'          -> 'abc' is not an id
'2147483648'   -> '2147483648' is not an id
```

Ten inputs, and the split between accepted and rejected is the useful part. `'3'`, `'007'` and `'+3'`
all become `3` — `Integer.parseInt` accepts a leading `+` and any number of leading zeros, so the three
spellings a user might type all work. `'0'` and `'-1'` parse fine and are then rejected by the range
check, with a message that names the rule. `' 3'` and `'3 '` are rejected by `parseInt` itself, because
it does not trim.

That last pair is the one to remember. A value that came from a text field or a copy-paste routinely
carries whitespace, and `parseInt` will not forgive it. Trim at the boundary where the string arrives,
not inside the parser — the parser is the wrong place to guess what the user meant.

One function, one message per failure, called from three commands. When the rules change — when ids
become `String` identifiers, say — there is one place to change them.

### 4. An unknown option is an error, not something to ignore

A parser that skips what it does not understand is worse than one that refuses, because the user gets
a program that silently did something other than what they asked:

```java run
public class Sol4 {
    static String firstCommand(String[] args) {
        int i = 0;
        while (i < args.length && args[i].startsWith("-")) {
            if (args[i].equals("--")) {
                i++;
                break;
            }
            if (args[i].equals("--vault")) {
                i += 2;
                continue;
            }
            return "unknown option '" + args[i] + "'";
        }
        return i < args.length ? "command '" + args[i] + "'" : "no command";
    }

    public static void main(String[] args) {
        String[][] cases = {
            {"list"},
            {"--vault", "/tmp/n", "list"},
            {"--vault", "/tmp/n", "--", "list"},
            {"-x", "list"},
            {"--vault=/tmp/n", "list"},
            {"--help"},
            {"--"},
        };

        for (String[] c : cases) {
            System.out.printf("%-32s -> %s%n", String.join(" ", c), firstCommand(c));
        }
    }
}
```

```text
list                             -> command 'list'
--vault /tmp/n list              -> command 'list'
--vault /tmp/n -- list           -> command 'list'
-x list                          -> unknown option '-x'
--vault=/tmp/n list              -> unknown option '--vault=/tmp/n'
--help                           -> unknown option '--help'
--                               -> no command
```

Seven inputs and the two that matter are the failures. `-x list` reports `unknown option '-x'` rather
than treating `-x` as a command name and reporting `unknown command`. And `--vault=/tmp/n list` is
rejected, because this parser only understands the two-token form — `--vault` followed by its value.

That second one is a real limitation and it is stated rather than hidden. Many programs accept both
`--vault /tmp/n` and `--vault=/tmp/n`; supporting the second means checking for the `=` and splitting
on the first one, which is four lines. What must not happen is accepting `--vault=/tmp/n` and then
ignoring it, because the user's vault is now somewhere they did not choose.

`--help` being an unknown option is also deliberate. There is one spelling for a command in this
program — a word with no dashes — and adding a second one for `help` alone would mean every future
command has to decide whether it wants a `--` spelling too.

## Key takeaways

- Turn `String[] args` into a value **once**, before executing anything. After that, the rest of the
  program cannot see a malformed command.
- One record per command in a sealed interface, and `permits` listing all of them. The compiler then
  knows the complete set.
- Parse in one place and execute in another. `parse` knows strings; the executor knows vaults and
  streams. Neither needs the other's knowledge.
- A usage error is an exception thrown at startup and caught at the boundary. Catch it, print the
  message, print the usage, return `2` — never let a stack trace reach the user.
- A type pattern for the sealed interface itself, written before the specific arms, makes them
  unreachable: `this case label is dominated by a preceding case label`.
- `[serial]` fires on every class extending `Exception`. For an exception that is never serialized,
  `@SuppressWarnings("serial")` is documentation, not a silencing.
- Consume options from the front and stop at the first non-option. Support `--` so that a value which
  looks like an option can still be passed.
- An option you do not understand is an error. Silently ignoring it means the user gets a program that
  did something other than what they asked.
- "Not found" is an exit code, not an exception. Pick a number, write it in the table, and make the
  choice visible.
- Remove an item by keeping the ones that differ, never by truncating at its position.

## Practice

- [ ] Add a `count` command and add its arm to `execute`. Before you compile, predict which files
      change; then check. The answer should be two.
- [ ] Make `Commands.parse` reject a command that takes arguments when it is given extra ones —
      `quill list extra` should fail — and add the rows to a table that proves it.
- [ ] Implement `--vault=<dir>` as well as `--vault <dir>`, and decide what `--vault= list` should do.
- [ ] Change `delete` to exit `0` when the note was already gone, and write the two-command sequence
      that tells the two designs apart.
- [ ] Add a `search <word>` command that prints every note whose title or body contains the word, and
      make it exit `5` when nothing matches.
- [ ] Move the id parsing out of `Commands` into a `parseId` in its own class, then add a second caller
      that needs a different message. Decide whether the message belongs to the parser or the caller.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. Two files: `Commands.java` gets a `record Count() implements Commands {}`, a `permits` entry, a
   `parse` arm and a `describe` arm; `Main.java` gets an `execute` arm. Nothing else changes, and if
   you predicted three you probably expected the help text to need editing — which it does, and which
   is the one thing the compiler cannot check. That is worth noticing: a `Usage` constant is prose, and
   prose is not type-checked.
2. `case "list" -> { if (args.length > 1) throw new UsageException("list takes no arguments"); yield
   new ListNotes(); }`. The table gains `{"list", "extra"}` expecting a usage error. The reason to do
   this is that a user who types `quill list extra` has almost certainly made a mistake, and the
   program should say so rather than ignore the extra word.
3. Check `args[i].startsWith("--vault=")` and take `substring(8)`. `--vault= list` should be an error:
   the value is empty, and an empty directory name is not a vault. The general rule is that an option
   which requires a value must reject an empty one, because the empty string is the value users get
   when a shell variable was unset.
4. `delete #2` then `delete #2`. With exit `5` on the second the script stops; with exit `0` it
   continues. If your scripts retry, choose `0`; if they distinguish a typo from a success, choose `5`.
   The sequence is the test either way.
5. `search` filters `vault.read()` on `note.title().contains(word) || note.body().contains(word)` and
   returns `NOT_FOUND` when the list is empty. Notice that this is the same "is empty a failure?" question
   as `show`, answered the same way for the same reason.
6. The message belongs to the caller, because the same failure is useful at different levels of detail:
   `Commands` wants `'seven' is not an id` for a user, and a test wants to know which of the two rules
   was broken. Have `parseId` throw a typed exception with a code, and let each caller format it — which
   is the same separation as `parse` versus `execute`.
