import java.util.List;

public class Reduce {

    public static void main(String[] args) {
        List<Integer> numbers = List.of(3, 1, 4, 1, 5);

        System.out.println("sum with an identity: " + numbers.stream().reduce(0, Integer::sum));
        System.out.println("max without one: " + numbers.stream().reduce(Integer::max));
        System.out.println("empty without an identity: "
                + List.<Integer>of().stream().reduce(Integer::max));
        System.out.println("empty with an identity: "
                + List.<Integer>of().stream().reduce(0, Integer::sum));
        System.out.println("concatenated: "
                + List.of("a", "b", "c").stream().reduce("", (a, b) -> a + b));
    }
}
