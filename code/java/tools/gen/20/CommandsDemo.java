public class CommandsDemo {
    public static void main(String[] args) {
        Commands[] commands = {
            new Commands.Add("Groceries", "milk and eggs"),
            new Commands.ListNotes(),
            new Commands.Show(7),
            new Commands.Help(),
        };
        for (Commands command : commands) {
            System.out.printf("%-12s %s%n",
                    command.getClass().getSimpleName(), Commands.describe(command));
        }
    }
}
