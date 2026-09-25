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
