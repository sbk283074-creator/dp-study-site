import java.util.List;

public class Sol1 {

    record Order(String id, int units) {
        boolean isBulk() {
            return units >= 10;
        }
    }

    static int lookups = 0;

    static String lookup(Order order) {
        lookups++;
        return order.id();
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("a", 3), new Order("b", 12), new Order("c", 20), new Order("d", 1));

        lookups = 0;
        List<String> bulk = orders.stream()
                .filter(Order::isBulk)
                .map(Sol1::lookup)
                .sorted()
                .toList();

        System.out.println("bulk ids: " + bulk);
        System.out.println("lookups performed: " + lookups + " of " + orders.size());
        System.out.println("nothing was done for the filtered-out orders: "
                + (lookups < orders.size()));
    }
}
