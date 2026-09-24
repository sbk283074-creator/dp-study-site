import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;

public class Capture {

    public static void main(String[] args) {
        String prefix = "id-";
        int count = 3;
        List<String> names = new ArrayList<>(List.of("a", "b"));

        Function<String, String> tag = name -> prefix + name;
        Supplier<Integer> size = () -> count + names.size();

        System.out.println("captured a String: " + tag.apply("x"));
        System.out.println("captured an int and a reference: " + size.get());

        names.add("c");
        System.out.println("a captured reference sees later changes: " + size.get());
        System.out.println("the local itself was never reassigned: " + (count == 3));
        System.out.println("so the lambda is legal without being final");
    }
}
