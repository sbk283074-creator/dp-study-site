import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class Ordering {
    static class Suite {
        void testCharlie() {}

        void testAlpha() {}

        void testBravo() {}
    }

    static List<String> declaredOrder() {
        List<String> names = new ArrayList<>();
        for (Method m : Suite.class.getDeclaredMethods()) {
            names.add(m.getName());
        }
        return names;
    }

    static List<String> sortedOrder() {
        List<String> names = declaredOrder();
        names.sort(Comparator.naturalOrder());
        return names;
    }

    public static void main(String[] args) {
        System.out.println("sorted  = " + sortedOrder());
        System.out.println("again   = " + sortedOrder());
        System.out.println("stable  = " + sortedOrder().equals(sortedOrder()));
        System.out.println("count   = " + sortedOrder().size());
    }
}
