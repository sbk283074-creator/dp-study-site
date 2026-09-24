import java.util.List;
import java.util.function.Function;

public class Sol3 {

    interface CheckedFunction<T, R> {
        R apply(T value) throws Exception;
    }

    static <T, R> Function<T, R> unchecked(CheckedFunction<T, R> function) {
        return value -> {
            try {
                return function.apply(value);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        };
    }

    public static void main(String[] args) {
        List<String> words = List.of("ada", "grace", "alan");
        System.out.println("lengths: " + words.stream().map(String::length).toList());

        Function<String, Integer> parse = unchecked(Integer::parseInt);
        System.out.println("parsing a good value: " + parse.apply("42"));

        try {
            parse.apply("forty");
        } catch (RuntimeException e) {
            System.out.println("a bad value arrives wrapped: "
                    + e.getCause().getClass().getSimpleName());
        }
    }
}
