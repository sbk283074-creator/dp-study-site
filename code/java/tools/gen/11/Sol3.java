import java.util.ArrayList;
import java.util.List;

public class Sol3 {

    static <T extends Comparable<T>> T min(List<T> values) {
        T best = values.get(0);
        for (T value : values) {
            if (value.compareTo(best) < 0) {
                best = value;
            }
        }
        return best;
    }

    static <T extends Comparable<T>> T max(List<T> values) {
        T best = values.get(0);
        for (T value : values) {
            if (value.compareTo(best) > 0) {
                best = value;
            }
        }
        return best;
    }

    static double total(List<? extends Number> values) {
        double sum = 0;
        for (Number value : values) {
            sum += value.doubleValue();
        }
        return sum;
    }

    static <T> void copy(List<? extends T> from, List<? super T> to) {
        for (T item : from) {
            to.add(item);
        }
    }

    public static void main(String[] args) {
        List<Integer> numbers = List.of(5, 3, 9, 1);

        System.out.println("min: " + min(numbers) + ", max: " + max(numbers));
        System.out.println("total of ints: " + total(numbers));
        System.out.println("total of doubles: " + total(List.of(1.5, 2.5)));

        List<Number> sink = new ArrayList<>();
        copy(numbers, sink);
        System.out.println("copied into a List<Number>: " + sink);
    }
}
