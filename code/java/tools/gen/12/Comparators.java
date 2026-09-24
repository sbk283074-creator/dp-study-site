import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

public class Comparators {

    record Person(String name, int age) {
    }

    static List<String> names(List<Person> people) {
        return people.stream().map(Person::name).toList();
    }

    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
            new Person("grace", 45), new Person("ada", 36),
            new Person("alan", 41), new Person("bob", 36)));

        people.sort(Comparator.comparing(Person::age));
        System.out.println("by age:                " + names(people));

        people.sort(Comparator.comparing(Person::age).thenComparing(Person::name));
        System.out.println("by age, then name:     " + names(people));

        people.sort(Comparator.comparing(Person::name).reversed());
        System.out.println("by name, reversed:     " + names(people));

        people.sort(Comparator.comparingInt(Person::age).reversed()
                .thenComparing(Person::name));
        System.out.println("oldest first, ties by name: " + names(people));

        List<String> words = new ArrayList<>(Arrays.asList("pear", null, "apple"));
        words.sort(Comparator.nullsLast(Comparator.naturalOrder()));
        System.out.println("nulls last:            " + words);

        Comparator<Person> byAge = Comparator.comparingInt(Person::age);
        System.out.println("reversing twice returns the original: "
                + (byAge.reversed().reversed().compare(people.get(0), people.get(1))
                   == byAge.compare(people.get(0), people.get(1))));
    }
}
