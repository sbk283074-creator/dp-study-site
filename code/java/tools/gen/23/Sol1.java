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
