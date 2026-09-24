import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Collecting {

    record Sale(String region, int units) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", 3), new Sale("south", 5),
            new Sale("north", 2), new Sale("south", 1), new Sale("north", 4));

        Map<String, Integer> units = sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new, Collectors.summingInt(Sale::units)));
        System.out.println("units by region: " + units);

        Map<String, Long> counts = sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new, Collectors.counting()));
        System.out.println("count by region: " + counts);

        Map<Boolean, List<Sale>> split = sales.stream().collect(
                Collectors.partitioningBy(sale -> sale.units() >= 3));
        System.out.println("big sales: " + split.get(true).size()
                + ", small sales: " + split.get(false).size());

        System.out.println("joined: " + sales.stream().map(Sale::region)
                .distinct().sorted().collect(Collectors.joining(", ")));
    }
}
