public class BadSealed {
    sealed interface Shape permits Circle {}

    record Circle(double r) implements Shape {}
    record Square(double side) implements Shape {}

    public static void main(String[] args) {
        System.out.println(new Square(2));
    }
}
