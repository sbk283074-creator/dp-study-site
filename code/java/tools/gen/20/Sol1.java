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
