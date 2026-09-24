import java.util.Optional;

public class OptionalGet {

    public static void main(String[] args) {
        Optional<String> missing = Optional.empty();
        System.out.println("never reached: " + missing.get());
    }
}
