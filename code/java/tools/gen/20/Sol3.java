public class Sol3 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Help {

        record Add(String title, String body) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Help() implements Command {}
    }

    static String describe(Command command) {
        return switch (command) {
            case Command.Add a -> "add \"" + a.title() + "\"";
            case Command.ListNotes n -> "list";
            case Command.Show s -> "show #" + s.id();
            case Command.Delete d -> "delete #" + d.id();
            case Command.Help h -> "help";
        };
    }

    public static void main(String[] args) {
        Command[] commands = {
            new Command.Add("Groceries", "milk and eggs"),
            new Command.ListNotes(),
            new Command.Show(3),
            new Command.Delete(3),
            new Command.Help(),
        };
        for (Command command : commands) {
            System.out.printf("%-12s %s%n",
                    command.getClass().getSimpleName(), describe(command));
        }
        System.out.println();
        System.out.println("5 permitted types, 5 arms, and no default arm");
    }
}
