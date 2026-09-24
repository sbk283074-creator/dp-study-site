import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class Immutable {

    public static void main(String[] args) {
        List<String> fixed = List.of("a", "b");
        Set<String> unique = Set.of("a", "b");
        Map<String, Integer> counts = Map.of("a", 1, "b", 2);

        System.out.println("List.of: " + fixed);
        System.out.println("Set.of, printed in sorted order: " + new TreeSet<>(unique));
        System.out.println("Map.of: " + new TreeMap<>(counts));

        List<String> copy = new ArrayList<>(fixed);
        copy.add("c");
        System.out.println("a defensive copy can grow: " + copy);
        System.out.println("the original is untouched: " + fixed);

        List<String> alsoCopy = List.copyOf(fixed);
        System.out.println("List.copyOf is also immutable: " + alsoCopy);
        System.out.println("it is a different object from the source: " + (alsoCopy != fixed));
        System.out.println("but equal to it: " + alsoCopy.equals(fixed));
    }
}
