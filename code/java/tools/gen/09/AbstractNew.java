public class AbstractNew {
    abstract static class Shape {
        abstract double area();
    }

    public static void main(String[] args) {
        Shape shape = new Shape();
        System.out.println(shape.area());
    }
}
