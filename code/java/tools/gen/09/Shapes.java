import java.util.List;
import java.util.Locale;

public class Shapes {
    abstract static class Shape {
        abstract double area();

        abstract String name();

        @Override
        public String toString() {
            return String.format(Locale.ROOT, "%-6s area %.4f", name(), area());
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

    static final class Square extends Shape {
        private final double side;

        Square(double side) {
            this.side = side;
        }

        @Override
        double area() {
            return side * side;
        }

        @Override
        String name() {
            return "square";
        }
    }

    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Square(3), new Circle(1), new Square(2));

        double total = 0;
        Shape largest = shapes.get(0);
        for (Shape shape : shapes) {
            System.out.println(shape);
            total += shape.area();
            if (shape.area() > largest.area()) {
                largest = shape;
            }
        }

        System.out.printf(Locale.ROOT, "total %.4f%n", total);
        System.out.println("largest is " + largest.name());
        System.out.println("the loop never asks what kind of shape it is holding");
    }
}
