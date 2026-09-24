import java.util.List;
import java.util.Objects;

public class ToString {

    static final class Order {
        final String id;
        final List<String> items;

        Order(String id, List<String> items) {
            this.id = id;
            this.items = List.copyOf(items);
        }

        @Override
        public String toString() {
            return "Order " + id + " (" + items.size() + " item(s)) " + items;
        }
    }

    public static void main(String[] args) {
        Order order = new Order("A-17", List.of("pen", "ink"));

        System.out.println(order);
        System.out.println("concatenation calls toString: " + ("sending " + order));
        System.out.println("a list prints its elements: " + List.of(order));
        System.out.println("a null in a concatenation becomes: " + (Object) null);
        System.out.println("String.valueOf(null): " + String.valueOf((Object) null));
        System.out.println("Objects.toString with a fallback: "
                + Objects.toString(null, "<none>"));
        System.out.println("the log never sees the word null: "
                + !(order + " " + Objects.toString(null, "<none>")).contains("null"));
    }
}
