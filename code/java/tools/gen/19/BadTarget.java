import java.lang.annotation.ElementType;
import java.lang.annotation.Target;

public class BadTarget {
    @Target(ElementType.METHOD)
    @interface OnlyOnMethods {}

    @OnlyOnMethods
    record Point(int x, int y) {}

    public static void main(String[] args) {
        System.out.println(new Point(1, 2));
    }
}
