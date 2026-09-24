import java.util.function.Function;

public class Sol2 {

    record Pair<A, B>(A first, B second) {

        <C> Pair<B, C> then(Function<A, C> step) {
            return new Pair<>(second, step.apply(first));
        }

        static <A, B> Pair<B, A> swap(Pair<A, B> pair) {
            return new Pair<>(pair.second(), pair.first());
        }
    }

    public static void main(String[] args) {
        Pair<String, Integer> counted = new Pair<>("ada", 3);

        System.out.println("printed: " + counted);
        System.out.println("swapped: " + Pair.swap(counted));
        System.out.println("then(String::length): " + counted.then(String::length));
        System.out.println("first with no cast: " + counted.first().toUpperCase());
        System.out.println("second with no cast: " + (counted.second() + 1));
    }
}
