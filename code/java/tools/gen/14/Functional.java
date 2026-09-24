import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;

public class Functional {

    public static void main(String[] args) {
        Function<String, Integer> length = String::length;
        Predicate<String> longerThanThree = text -> text.length() > 3;
        Consumer<String> print = text -> System.out.println("  consumed " + text);
        Supplier<String> greeting = () -> "hello";
        BiFunction<Integer, Integer, Integer> add = Integer::sum;

        System.out.println("Function: " + length.apply("ada"));
        System.out.println("Predicate: " + longerThanThree.test("ada")
                + " and " + longerThanThree.test("grace"));
        print.accept("a line");
        System.out.println("Supplier: " + greeting.get());
        System.out.println("BiFunction: " + add.apply(3, 4));
        System.out.println("they all live in: " + Function.class.getPackageName());
    }
}
