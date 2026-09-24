import java.util.List;
import java.util.stream.Stream;

public class Consumed {

    public static void main(String[] args) {
        Stream<String> words = List.of("ada", "grace").stream();

        System.out.println("first pass: " + words.count());
        System.out.println("second pass: " + words.count());
    }
}
