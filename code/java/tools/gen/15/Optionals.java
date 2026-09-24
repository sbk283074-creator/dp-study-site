import java.util.List;
import java.util.Optional;

public class Optionals {

    static Optional<String> find(List<String> names, String target) {
        for (String name : names) {
            if (name.equals(target)) {
                return Optional.of(name);
            }
        }
        return Optional.empty();
    }

    public static void main(String[] args) {
        List<String> names = List.of("ada", "grace", "alan");

        System.out.println("found: " + find(names, "grace"));
        System.out.println("missing: " + find(names, "zoe"));
        System.out.println("orElse: " + find(names, "zoe").orElse("nobody"));
        System.out.println("mapped: " + find(names, "grace").map(String::toUpperCase));
        System.out.println("filtered away: " + find(names, "grace").filter(n -> n.length() > 10));
        System.out.println("isEmpty is the real check: " + find(names, "zoe").isEmpty());
        System.out.println("an empty Optional has no elements: " + find(names, "zoe").stream().count());
    }
}
