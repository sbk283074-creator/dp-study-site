import java.util.HashSet;
import java.util.Set;

public class OverloadEquals {

    static final class Point {
        final int x;
        final int y;

        Point(int x, int y) {
            this.x = x;
            this.y = y;
        }

        public boolean equals(Point other) {
            return other != null && other.x == x && other.y == y;
        }
    }

    public static void main(String[] args) {
        Point p = new Point(1, 2);
        Point q = new Point(1, 2);

        System.out.println("direct call, argument typed Point: " + p.equals(q));
        System.out.println("the same call through an Object reference: "
                + ((Object) p).equals((Object) q));

        Set<Point> seen = new HashSet<>();
        seen.add(p);
        seen.add(q);
        System.out.println("a HashSet holding them: " + seen.size() + " entries");
    }
}
