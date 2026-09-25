public class Dominated {
    sealed interface Shape permits Circle, Square {}

    record Circle(double radius) implements Shape {}

    record Square(double side) implements Shape {}

    static String name(Shape shape) {
        return switch (shape) {
            case Shape any -> "a shape";
            case Circle c -> "circle";
            case Square s -> "square";
        };
    }

    public static void main(String[] args) {
        System.out.println(name(new Circle(1)));
    }
}
