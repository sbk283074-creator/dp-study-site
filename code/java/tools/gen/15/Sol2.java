import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

public class Sol2 {

    record Sale(String region, String product, int units) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", "pen", 3), new Sale("south", "pen", 5),
            new Sale("north", "ink", 2), new Sale("south", "ink", 1),
            new Sale("north", "pen", 4));

        System.out.println("units by region: " + sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new, Collectors.summingInt(Sale::units))));

        Map<String, Map<String, Integer>> nested = sales.stream().collect(Collectors.groupingBy(
                Sale::region, TreeMap::new,
                Collectors.groupingBy(Sale::product, TreeMap::new,
                        Collectors.summingInt(Sale::units))));
        nested.forEach((region, products) ->
                System.out.println("  " + region + " -> " + products));

        System.out.println("top product: " + sales.stream()
                .collect(Collectors.groupingBy(Sale::product, Collectors.summingInt(Sale::units)))
                .entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("none"));
    }
}
