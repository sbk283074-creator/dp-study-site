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
