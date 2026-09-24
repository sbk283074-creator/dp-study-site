import java.util.ArrayList;
import java.util.List;

public class Varargs {

    @SafeVarargs
    static <T> List<T> listOf(T... items) {
        List<T> result = new ArrayList<>();
        for (T item : items) {
            result.add(item);
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println("listOf(\"a\", \"b\"): " + listOf("a", "b"));
        System.out.println("listOf(1, 2, 3).size(): " + listOf(1, 2, 3).size());
        System.out.println("listOf() with no arguments: " + listOf());
        System.out.println("the array behind the varargs is: "
                + listOf("a", "b").toArray().getClass().getSimpleName());
    }
}
