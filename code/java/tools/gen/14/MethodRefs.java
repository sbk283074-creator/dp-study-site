import java.util.ArrayList;
import java.util.function.Function;
import java.util.function.Supplier;

public class MethodRefs {

    static String shout(String text) {
        return text.toUpperCase() + "!";
    }

    record Name(String first, String last) {
        String full() {
            return first + " " + last;
        }
    }

    public static void main(String[] args) {
        Function<String, String> staticRef = MethodRefs::shout;
        Function<String, Integer> boundRef = "hello"::indexOf;
        Function<String, String> unboundRef = String::trim;
        Supplier<ArrayList<String>> constructorRef = ArrayList::new;
        Function<Name, String> argumentRef = Name::full;

        System.out.println("static:                " + staticRef.apply("ada"));
        System.out.println("bound to an instance:  " + boundRef.apply("l"));
        System.out.println("unbound, on the arg:   " + unboundRef.apply("  spaced  ") + "|");
        System.out.println("constructor:           " + constructorRef.get().getClass().getSimpleName());
        System.out.println("instance on the arg:   " + argumentRef.apply(new Name("ada", "lovelace")));
    }
}
