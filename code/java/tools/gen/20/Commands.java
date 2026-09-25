public sealed interface Commands
        permits Commands.Add, Commands.ListNotes, Commands.Show, Commands.Help {

    record Add(String title, String body) implements Commands {}

    record ListNotes() implements Commands {}

    record Show(int id) implements Commands {}

    record Help() implements Commands {}

    static String describe(Commands command) {
        return switch (command) {
            case Add a -> "add \"" + a.title() + "\"";
            case ListNotes n -> "list";
            case Show s -> "show #" + s.id();
            case Help h -> "help";
        };
    }
}
