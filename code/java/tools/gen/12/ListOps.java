import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

public class ListOps {

    public static void main(String[] args) {
        List<String> queue = new ArrayList<>(List.of("a", "b", "c"));

        System.out.println("start: " + queue);
        queue.add("d");
        System.out.println("add at the end: " + queue);
        queue.add(0, "z");
        System.out.println("add at index 0: " + queue);
        System.out.println("get(1): " + queue.get(1));
        System.out.println("indexOf(\"c\"): " + queue.indexOf("c"));
        System.out.println("remove(\"z\") returned: " + queue.remove("z"));
        System.out.println("remove(0) returned: " + queue.remove(0));
        System.out.println("after removals: " + queue);
        System.out.println("subList(1, 3): " + queue.subList(1, 3));
        System.out.println("size: " + queue.size());

        List<String> linked = new LinkedList<>(queue);
        System.out.println("a LinkedList holds the same: " + linked.equals(queue));
        System.out.println("both implement List: " + (queue instanceof List && linked instanceof List));
        System.out.println("but only one is RandomAccess: "
                + (queue instanceof java.util.RandomAccess) + " and "
                + (linked instanceof java.util.RandomAccess));
    }
}
