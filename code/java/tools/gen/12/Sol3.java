import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Sol3 {

    record Sale(String region, String product, int units) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", "pen", 3), new Sale("south", "pen", 5),
            new Sale("north", "ink", 2), new Sale("south", "ink", 1),
            new Sale("north", "pen", 4));

        Map<String, Integer> byRegion = new TreeMap<>();
        for (Sale sale : sales) {
            byRegion.merge(sale.region(), sale.units(), Integer::sum);
        }
        System.out.println("units by region: " + byRegion);

        Map<String, Map<String, Integer>> nested = new TreeMap<>();
        for (Sale sale : sales) {
            nested.computeIfAbsent(sale.region(), key -> new TreeMap<>())
                  .merge(sale.product(), sale.units(), Integer::sum);
        }
        nested.forEach((region, products) ->
                System.out.println("  " + region + " -> " + products));

        int total = sales.stream().mapToInt(Sale::units).sum();
        System.out.println("total units: " + total);
        System.out.println("the regions sum to the total: "
                + (byRegion.values().stream().mapToInt(Integer::intValue).sum() == total));
    }
}
