import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class Bridge {

    static class Named implements Comparable<Named> {
        final String name;

        Named(String name) {
            this.name = name;
        }

        @Override
        public int compareTo(Named other) {
            return name.compareTo(other.name);
        }
    }

    static String describe(Class<?>[] types) {
        return Arrays.stream(types).map(Class::getSimpleName)
                .reduce((left, right) -> left + ", " + right).orElse("");
    }

    public static void main(String[] args) {
        Method[] methods = Named.class.getDeclaredMethods();

        Arrays.stream(methods)
                .map(m -> "  " + m.getName() + "(" + describe(m.getParameterTypes())
                        + ") -> " + m.getReturnType().getSimpleName())
                .sorted()
                .forEach(System.out::println);

        System.out.println("declared methods: " + methods.length);
        System.out.println("of which bridges: "
                + Arrays.stream(methods).filter(Method::isBridge).count());

        List<Named> people = new ArrayList<>(List.of(new Named("grace"), new Named("ada")));
        Collections.sort(people);
        System.out.println("sorted through the erased path: "
                + people.stream().map(p -> p.name).toList());
    }
}
