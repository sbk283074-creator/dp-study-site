import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

public class SetOrders {

    public static void main(String[] args) {
        List<String> input = List.of("pear", "apple", "plum", "apple");

        Set<String> hash = new HashSet<>(input);
        Set<String> linked = new LinkedHashSet<>(input);
        Set<String> tree = new TreeSet<>(input);

        System.out.println("input: " + input);
        System.out.println("LinkedHashSet keeps arrival order: " + linked);
        System.out.println("TreeSet sorts: " + tree);
        System.out.println("all three hold the same elements: "
                + (hash.equals(linked) && linked.equals(tree)));
        System.out.println("the duplicates are gone: " + hash.size() + " of " + input.size());
        System.out.println("HashSet membership, not order: " + hash.contains("apple"));
    }
}
