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
