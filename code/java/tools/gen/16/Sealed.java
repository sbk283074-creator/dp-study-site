import java.util.Arrays;

public class Sealed {
    sealed interface Shape permits Circle, Rect, Line {}

    record Circle(double radius) implements Shape {}
    record Rect(double w, double h) implements Shape {}
    record Line(double length) implements Shape {}

    static double area(Shape shape) {
        return switch (shape) {
            case Circle c -> Math.PI * c.radius() * c.radius();
            case Rect r -> r.w() * r.h();
            case Line l -> 0.0;
        };
    }

    public static void main(String[] args) {
        Shape[] shapes = {new Circle(1), new Rect(2, 3), new Line(5)};
        for (Shape s : shapes) {
            System.out.printf("area=%6.2f  %s%n", area(s), s);
        }
        System.out.println("permitted = " + Arrays.toString(
                Arrays.stream(Shape.class.getPermittedSubclasses())
                      .map(Class::getSimpleName)
                      .toArray()));
    }
}
