import java.util.List;

public class Pipeline {

    record Order(String customer, int units, boolean paid) {
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("ada", 3, true), new Order("grace", 7, false),
            new Order("ada", 2, true), new Order("alan", 5, true));

        System.out.println("paid units: " + orders.stream()
                .filter(Order::paid).mapToInt(Order::units).sum());

        System.out.println("paid customers: " + orders.stream()
                .filter(Order::paid).map(Order::customer).distinct().sorted().toList());

        System.out.println("orders: " + orders.stream().count());
        System.out.println("any unpaid: " + orders.stream().anyMatch(o -> !o.paid()));
        System.out.println("all paid: " + orders.stream().allMatch(Order::paid));
        System.out.println("no unpaid: " + orders.stream().noneMatch(o -> !o.paid()));
    }
}
