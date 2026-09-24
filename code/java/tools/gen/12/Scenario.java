import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Scenario {

    public static void main(String[] args) {
        List<String> regions = List.of("west", "east", "north", "south", "east", "west", "west");

        Map<String, Integer> hash = new HashMap<>();
        Map<String, Integer> linked = new LinkedHashMap<>();
        Map<String, Integer> tree = new TreeMap<>();
        for (String region : regions) {
            for (Map<String, Integer> target : List.of(hash, linked, tree)) {
                target.merge(region, 1, Integer::sum);
            }
        }

        List<String> hashOrder = new ArrayList<>(hash.keySet());
        List<String> linkedOrder = new ArrayList<>(linked.keySet());
        List<String> treeOrder = new ArrayList<>(tree.keySet());
        List<String> sortedOrder = new ArrayList<>(linkedOrder);
        Collections.sort(sortedOrder);

        System.out.println("rows: " + regions.size() + ", distinct regions: " + hash.size());
        System.out.println("HashMap order:       " + hashOrder);
        System.out.println("LinkedHashMap order: " + linkedOrder);
        System.out.println("TreeMap order:       " + treeOrder);
        System.out.println("LinkedHashMap is the arrival order: "
                + linkedOrder.equals(List.of("west", "east", "north", "south")));
        System.out.println("TreeMap is sorted: " + treeOrder.equals(sortedOrder));
        System.out.println("HashMap is sorted: " + hashOrder.equals(sortedOrder));
        System.out.println("all three agree on the counts: "
                + (hash.equals(tree) && tree.equals(linked)));
    }
}
