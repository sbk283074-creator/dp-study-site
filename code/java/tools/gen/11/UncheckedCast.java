import java.util.ArrayList;
import java.util.List;

public class UncheckedCast {

    static List<String> asStrings(Object value) {
        return (List<String>) value;
    }

    public static void main(String[] args) {
        List<Integer> numbers = new ArrayList<>(List.of(1, 2, 3));
        List<String> strings = asStrings(numbers);

        System.out.println("the cast succeeded at run time: "
                + ((Object) strings == (Object) numbers));
        System.out.println("element 0 is really a: " + strings.get(0).getClass().getName());

        try {
            String first = strings.get(0);
            System.out.println("assigned without complaint: " + first);
        } catch (ClassCastException e) {
            System.out.println("it fails only when used: " + e.getClass().getSimpleName());
        }
    }
}
