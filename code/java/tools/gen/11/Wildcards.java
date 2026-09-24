import java.util.ArrayList;
import java.util.List;

public class Wildcards {

    static double sum(List<? extends Number> values) {
        double total = 0;
        for (Number value : values) {
            total += value.doubleValue();
        }
        return total;
    }

    static void addInts(List<? super Integer> target, int count) {
        for (int i = 1; i <= count; i++) {
            target.add(i);
        }
    }

    static <T> void copy(List<? extends T> from, List<? super T> to) {
        for (T item : from) {
            to.add(item);
        }
    }

    public static void main(String[] args) {
        System.out.println("sum of a List<Integer>: " + sum(List.of(1, 2, 3)));
        System.out.println("sum of a List<Double>: " + sum(List.of(1.5, 2.5)));

        List<Number> numbers = new ArrayList<>();
        addInts(numbers, 3);
        System.out.println("List<Number> after addInts: " + numbers);

        List<Object> objects = new ArrayList<>();
        addInts(objects, 2);
        System.out.println("List<Object> after addInts: " + objects);

        List<Number> sink = new ArrayList<>();
        copy(List.of(4, 5), sink);
        System.out.println("copied Integer into List<Number>: " + sink);
    }
}
