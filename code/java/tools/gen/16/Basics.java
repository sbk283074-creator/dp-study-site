import java.lang.reflect.RecordComponent;
import java.util.Arrays;
import java.util.Set;

public class Basics {
    record Point(int x, int y) {}

    public static void main(String[] args) {
        Point p = new Point(3, 4);

        System.out.println("isRecord       = " + Point.class.isRecord());
        System.out.println("components     = " + Arrays.toString(
                Arrays.stream(Point.class.getRecordComponents())
                      .map(RecordComponent::getName)
                      .toArray()));
        System.out.println("accessors      = " + p.x() + ", " + p.y());
        System.out.println("toString       = " + p);
        System.out.println("equals same    = " + p.equals(new Point(3, 4)));
        System.out.println("equals other   = " + p.equals(new Point(3, 5)));
        System.out.println("hashCode match = " + (p.hashCode() == new Point(3, 4).hashCode()));
        System.out.println("works as a key = " + Set.of(p).contains(new Point(3, 4)));
    }
}
