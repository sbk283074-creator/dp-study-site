import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;

public class Sol2 {

    record Entry(String name, int score) {
    }

    static List<String> names(List<Entry> entries) {
        return entries.stream().map(Entry::name).toList();
    }

    public static void main(String[] args) {
        List<Entry> entries = new ArrayList<>(List.of(
            new Entry("eve", 90), new Entry("bob", 75), new Entry("ada", 90),
            new Entry("dee", 75), new Entry("cal", 90)));

        List<Entry> stable = new ArrayList<>(entries);
        stable.sort(Comparator.comparingInt(Entry::score).reversed());
        System.out.println("by score alone, ties keep arrival order: " + names(stable));

        List<Entry> byName = new ArrayList<>(entries);
        byName.sort(Comparator.comparingInt(Entry::score).reversed()
                .thenComparing(Entry::name));
        System.out.println("by score, then name: " + names(byName));

        System.out.println("the tied group is the same three people: "
                + (new HashSet<>(names(stable).subList(0, 3))
                        .equals(new HashSet<>(names(byName).subList(0, 3)))));
        System.out.println("but the order inside it differs: "
                + !names(stable).equals(names(byName)));
    }
}
