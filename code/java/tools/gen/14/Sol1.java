import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class Sol1 {

    record Entry(String name, long size, long modified) {
    }

    public static void main(String[] args) {
        List<Entry> entries = new ArrayList<>(List.of(
            new Entry("b.txt", 200, 5), new Entry("a.txt", 200, 9),
            new Entry("c.txt", 100, 7)));

        entries.sort(Comparator.comparingLong(Entry::size).thenComparing(Entry::name));
        System.out.println("by size then name: "
                + entries.stream().map(Entry::name).toList());

        entries.sort(Comparator.comparingLong(Entry::modified).reversed());
        System.out.println("newest first: " + entries.stream().map(Entry::name).toList());

        Comparator<Entry> byName = Comparator.comparing(Entry::name);
        System.out.println("a comparator is a value you can pass around: "
                + (byName.compare(new Entry("a", 0, 0), new Entry("b", 0, 0)) < 0));
    }
}
