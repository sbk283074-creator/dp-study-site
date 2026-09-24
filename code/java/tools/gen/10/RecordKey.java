import java.lang.reflect.Modifier;
import java.util.HashSet;
import java.util.Set;

public class RecordKey {

    record Point(int x, int y) {
    }

    public static void main(String[] args) {
        Point p = new Point(3, 4);
        Point q = new Point(3, 4);

        System.out.println("printed: " + p);
        System.out.println("equals: " + p.equals(q));
        System.out.println("hashCodes agree: " + (p.hashCode() == q.hashCode()));

        Set<Point> distinct = new HashSet<>();
        distinct.add(p);
        distinct.add(q);
        System.out.println("a set of equal records holds: " + distinct.size() + " entry");

        System.out.println("components are readable: " + p.x() + "," + p.y());
        System.out.println("the class is final: " + Modifier.isFinal(Point.class.getModifiers()));
        String methods = java.util.Arrays.stream(Point.class.getDeclaredMethods())
                .map(java.lang.reflect.Method::getName)
                .sorted()
                .reduce((left, right) -> left + ", " + right)
                .orElse("");
        System.out.println("the methods it was given: " + methods);
    }
}
