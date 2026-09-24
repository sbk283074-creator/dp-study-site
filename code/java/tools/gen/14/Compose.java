import java.util.function.Function;
import java.util.function.Predicate;

public class Compose {

    public static void main(String[] args) {
        Function<Integer, Integer> doubleIt = n -> n * 2;
        Function<Integer, Integer> addOne = n -> n + 1;

        System.out.println("andThen: " + doubleIt.andThen(addOne).apply(5));
        System.out.println("compose: " + doubleIt.compose(addOne).apply(5));
        System.out.println("they differ: "
                + (doubleIt.andThen(addOne).apply(5) != doubleIt.compose(addOne).apply(5)));

        Predicate<String> shortWord = text -> text.length() < 4;
        Predicate<String> startsA = text -> text.startsWith("a");

        System.out.println("and:    " + shortWord.and(startsA).test("ada"));
        System.out.println("or:     " + shortWord.or(startsA).test("banana"));
        System.out.println("negate: " + shortWord.negate().test("banana"));
    }
}
