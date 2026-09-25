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
