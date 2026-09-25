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
