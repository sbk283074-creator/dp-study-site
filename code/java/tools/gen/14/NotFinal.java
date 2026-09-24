import java.util.function.Supplier;

public class NotFinal {

    public static void main(String[] args) {
        int total = 0;
        Supplier<Integer> read = () -> total;
        total = 1;
        System.out.println(read.get());
    }
}
