import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Sol3 {
    sealed interface Event permits Login, Purchase, Logout {}

    record Login(String user) implements Event {}
    record Purchase(String user, int cents) implements Event {}
    record Logout(String user) implements Event {}

    static String kind(Event e) {
        return switch (e) {
            case Login l -> "login";
            case Purchase p -> "purchase";
            case Logout l -> "logout";
        };
    }

    static int amount(Event e) {
        return switch (e) {
            case Login l -> 0;
            case Purchase p -> p.cents();
            case Logout l -> 0;
        };
    }

    public static void main(String[] args) {
        List<Event> events = List.of(
                new Login("ada"),
                new Purchase("ada", 2500),
                new Purchase("bob", 700),
                new Logout("ada"));

        Map<String, Integer> byKind = new TreeMap<>();
        int revenue = 0;
        for (Event e : events) {
            byKind.merge(kind(e), 1, Integer::sum);
            revenue += amount(e);
        }
        System.out.println("by kind = " + byKind);
        System.out.println("revenue = " + revenue);
        System.out.println("events  = " + events.size());
    }
}
