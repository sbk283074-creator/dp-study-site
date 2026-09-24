import java.lang.reflect.Modifier;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Sol2 {

    record Sale(String region, String product) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", "pen"),
            new Sale("north", "pen"),
            new Sale("south", "pen"),
            new Sale("north", "ink")
        );

        Map<Sale, Integer> tally = new LinkedHashMap<>();
        for (Sale sale : sales) {
            tally.merge(sale, 1, Integer::sum);
        }

        System.out.println("sales logged: " + sales.size());
        System.out.println("distinct region/product pairs: " + tally.size());
        tally.forEach((key, count) ->
                System.out.println("  " + key.region() + "/" + key.product() + " -> " + count));
        System.out.println("no component can be reassigned: "
                + java.util.Arrays.stream(Sale.class.getDeclaredFields())
                        .allMatch(f -> Modifier.isFinal(f.getModifiers())));
    }
}
