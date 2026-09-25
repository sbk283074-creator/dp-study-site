import java.util.Arrays;

public class Sol2 {
    sealed interface Command permits Command.Add, Command.ListNotes, Command.Show,
            Command.Delete, Command.Help {

        record Add(String title) implements Command {}

        record ListNotes() implements Command {}

        record Show(int id) implements Command {}

        record Delete(int id) implements Command {}

        record Help() implements Command {}
    }

    static String commands() {
        return Arrays.stream(Command.class.getPermittedSubclasses())
                .map(Class::getSimpleName)
                .sorted()
                .reduce((a, b) -> a + ", " + b)
                .orElse("");
    }

    public static void main(String[] args) {
        System.out.println(commands());
        System.out.println();
        System.out.println("the list comes from the hierarchy, so a new command cannot be forgotten");
    }
}
