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
