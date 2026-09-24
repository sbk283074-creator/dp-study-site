import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class Sol4 {

    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("ada", "bob", "cal", "ben"));

        List<String> byRemoveIf = new ArrayList<>(names);
        byRemoveIf.removeIf(name -> name.startsWith("b"));
        System.out.println("removeIf: " + byRemoveIf);

        List<String> byIterator = new ArrayList<>(names);
        Iterator<String> iterator = byIterator.iterator();
        while (iterator.hasNext()) {
            if (iterator.next().startsWith("b")) {
                iterator.remove();
            }
        }
        System.out.println("iterator.remove: " + byIterator);

        System.out.println("the two agree: " + byRemoveIf.equals(byIterator));

        List<String> byFilter = names.stream().filter(name -> !name.startsWith("b")).toList();
        System.out.println("filter into a new list: " + byFilter);
        System.out.println("the original is untouched: " + names);
    }
}
