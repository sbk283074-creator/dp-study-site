import java.util.List;

public class Bounds {

    static <T extends Comparable<T>> T largest(List<T> values) {
        T best = values.get(0);
        for (T value : values) {
            if (value.compareTo(best) > 0) {
                best = value;
            }
        }
        return best;
    }

    static <T extends Number & Comparable<T>> double total(List<T> values) {
        double sum = 0;
        for (T value : values) {
            sum += value.doubleValue();
        }
        return sum;
    }

    public static void main(String[] args) {
        System.out.println("largest word: " + largest(List.of("pear", "apple", "plum")));
        System.out.println("largest number: " + largest(List.of(3, 9, 4)));
        System.out.println("total: " + total(List.of(1, 2, 3, 4)));
        System.out.println("the bound is what lets compareTo be called: "
                + largest(List.of(3, 9, 4)).getClass().getSimpleName());
    }
}
