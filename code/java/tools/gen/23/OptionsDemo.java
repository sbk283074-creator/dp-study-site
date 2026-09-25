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
