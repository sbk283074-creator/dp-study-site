public class BadSwitch {
    sealed interface Shape permits BadSwitch.Circle, BadSwitch.Square {}

    record Circle(double radius) implements Shape {}

    record Square(double side) implements Shape {}

    static double area(Shape shape) {
        return switch (shape) {
            case Circle c -> Math.PI * c.radius() * c.radius();
        };
    }

    public static void main(String[] args) {
        System.out.println(area(new Circle(1)));
    }
}
