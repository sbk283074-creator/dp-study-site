public sealed interface Commands
        permits Commands.Add, Commands.ListNotes, Commands.Show, Commands.Delete, Commands.Help {

    record Add(String title) implements Commands {}

    record ListNotes() implements Commands {}

    record Show(int id) implements Commands {}

    record Delete(int id) implements Commands {}

    record Help() implements Commands {}

    @SuppressWarnings("serial")
    class UsageException extends IllegalArgumentException {
        UsageException(String message) {
            super(message);
        }
    }

    static Commands parse(String[] args) {
        if (args.length == 0) {
            return new Help();
        }
        return switch (args[0]) {
            case "help" -> new Help();
            case "list" -> new ListNotes();
            case "add" -> {
                if (args.length < 2) {
                    throw new UsageException("add needs a title");
                }
                yield new Add(args[1]);
            }
            case "show" -> new Show(id(args, "show <id>"));
            case "delete" -> new Delete(id(args, "delete <id>"));
            default -> throw new UsageException("unknown command '" + args[0] + "'");
        };
    }

    static String describe(Commands command) {
        return switch (command) {
            case Add a -> "add \"" + a.title() + "\"";
            case ListNotes n -> "list";
            case Show s -> "show #" + s.id();
            case Delete d -> "delete #" + d.id();
            case Help h -> "help";
        };
    }

    private static int id(String[] args, String form) {
        if (args.length < 2) {
            throw new UsageException(form + " needs an id");
        }
        int id;
        try {
            id = Integer.parseInt(args[1]);
        } catch (NumberFormatException e) {
            throw new UsageException("'" + args[1] + "' is not an id");
        }
        if (id <= 0) {
            throw new UsageException("ids start at 1, not " + id);
        }
        return id;
    }
}
