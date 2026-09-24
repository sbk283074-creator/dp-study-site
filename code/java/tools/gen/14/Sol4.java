import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;

public class Sol4 {

    @FunctionalInterface
    interface Rule {
        boolean test(String value);

        default Rule and(Rule other) {
            return value -> test(value) && other.test(value);
        }

        default Rule negate() {
            return value -> !test(value);
        }
    }

    static Rule minLength(int length) {
        return value -> value.length() >= length;
    }

    static Rule startsWith(String prefix) {
        return value -> value.startsWith(prefix);
    }

    public static void main(String[] args) {
        Rule valid = minLength(3).and(startsWith("a"));

        System.out.println("ada:    " + valid.test("ada"));
        System.out.println("alan:   " + valid.test("alan"));
        System.out.println("bo:     " + valid.test("bo"));
        System.out.println("banana: " + valid.test("banana"));
        System.out.println("negated: " + valid.negate().test("banana"));

        long abstractMethods = Arrays.stream(Rule.class.getDeclaredMethods())
                .filter(m -> Modifier.isAbstract(m.getModifiers()))
                .count();
        System.out.println("abstract methods: " + abstractMethods);
        System.out.println("so it is a functional interface: " + (abstractMethods == 1));
    }
}
