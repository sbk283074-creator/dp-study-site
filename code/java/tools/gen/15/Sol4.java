import java.util.List;
import java.util.stream.Stream;

public class Sol4 {

    record Order(String id, int units) {
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
            new Order("a", 3), new Order("b", 12), new Order("c", 20));

        List<Order> bulk = orders.stream().filter(order -> order.units() >= 10).toList();

        System.out.println("bulk count: " + bulk.size());
        System.out.println("bulk units: " + bulk.stream().mapToInt(Order::units).sum());
        System.out.println("bulk ids: " + bulk.stream().map(Order::id).toList());

        Stream<Order> once = orders.stream().filter(order -> order.units() >= 10);
        System.out.println("the stream was used once: " + once.count());
        System.out.println("the source list is still usable: "
                + orders.stream().filter(order -> order.units() >= 10).count());
    }
}
