public class Sol4 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Help {

        record Add(String title) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Help() implements Command {}
    }

    static boolean mutates(Command command) {
        return switch (command) {
            case Command.Add a -> true;
            case Command.Delete d -> true;
            case Command.ListNotes n -> false;
            case Command.Show s -> false;
            case Command.Help h -> false;
        };
    }

    public static void main(String[] args) {
        Command[] commands = {
            new Command.Add("Groceries"),
            new Command.ListNotes(),
            new Command.Show(1),
            new Command.Delete(1),
            new Command.Help(),
        };

        for (Command command : commands) {
            System.out.printf("%-10s mutates=%b%n",
                    command.getClass().getSimpleName(), mutates(command));
        }

        System.out.println();
        System.out.println("--dry-run becomes one boolean on the command, checked in one place");
    }
}
