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
