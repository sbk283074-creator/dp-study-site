import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class MapOps {

    public static void main(String[] args) {
        Map<String, Integer> counts = new HashMap<>();
        for (String word : List.of("a", "b", "a", "c", "a")) {
            counts.merge(word, 1, Integer::sum);
        }
        System.out.println("merged: " + new TreeMap<>(counts));

        Map<String, List<String>> grouped = new HashMap<>();
        for (String word : List.of("apple", "avocado", "banana")) {
            grouped.computeIfAbsent(word.substring(0, 1), key -> new ArrayList<>()).add(word);
        }
        System.out.println("grouped: " + new TreeMap<>(grouped));

        System.out.println("getOrDefault on a missing key: " + counts.getOrDefault("zzz", 0));
        System.out.println("putIfAbsent returns the value already there: "
                + counts.putIfAbsent("a", 99));
        System.out.println("so a is still: " + counts.get("a"));
        System.out.println("get on a missing key is: " + counts.get("zzz"));
        System.out.println("keys: " + new TreeMap<>(counts).keySet());
        System.out.println("values total: " + counts.values().stream().mapToInt(Integer::intValue).sum());
    }
}
