import java.util.List;
import java.util.function.Function;

public class Sol2 {

    static final Function<String, String> TRIM = String::trim;
    static final Function<String, String> UPPER = String::toUpperCase;
    static final Function<String, String> EXCLAIM = text -> text + "!";

    public static void main(String[] args) {
        Function<String, String> pipeline = TRIM.andThen(UPPER).andThen(EXCLAIM);

        System.out.println(pipeline.apply("  ada  "));
        System.out.println("applied to a list: "
                + List.of("  ada ", " grace", "alan ").stream().map(pipeline).toList());
        System.out.println("compose gives the same pipeline here: "
                + UPPER.compose(TRIM).andThen(EXCLAIM).apply("  ada  ")
                        .equals(pipeline.apply("  ada  ")));
    }
}
