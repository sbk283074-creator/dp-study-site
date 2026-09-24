import java.util.List;
import java.util.Locale;

public class Sol1 {
    abstract static class Shape {
        abstract double area();

        abstract String name();

        final String describe() {
            return String.format(Locale.ROOT, "%-9s area %6.2f", name(), area());
        }
    }

    static final class Circle extends Shape {
        private final double radius;

        Circle(double radius) {
            this.radius = radius;
        }

        @Override
        double area() {
            return Math.PI * radius * radius;
        }

        @Override
        String name() {
            return "circle";
        }
    }

    static final class Rectangle extends Shape {
        private final double width;
        private final double height;

        Rectangle(double width, double height) {
            this.width = width;
            this.height = height;
        }

        @Override
        double area() {
            return width * height;
        }

        @Override
        String name() {
            return "rectangle";
        }
    }

    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Rectangle(3, 4), new Circle(1), new Rectangle(2, 2));
        for (Shape shape : shapes) {
            System.out.println(shape.describe());
        }
        System.out.println("describe() is written once and calls two methods each subclass supplies");
    }
}
