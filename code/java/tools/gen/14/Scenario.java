import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public class Scenario {

    public static void main(String[] args) {
        List<Supplier<String>> fromForEach = new ArrayList<>();
        for (String name : List.of("ada", "grace", "alan")) {
            fromForEach.add(() -> name);
        }
        System.out.println("for-each captures a fresh variable each round: "
                + fromForEach.stream().map(Supplier::get).toList());

        List<Supplier<Integer>> fromForLoop = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            int copy = i;
            fromForLoop.add(() -> copy);
        }
        System.out.println("a classic for needs the copy: "
                + fromForLoop.stream().map(Supplier::get).toList());

        List<Supplier<Integer>> shared = new ArrayList<>();
        int[] holder = {0};
        for (holder[0] = 0; holder[0] < 3; holder[0]++) {
            shared.add(() -> holder[0]);
        }
        System.out.println("a mutable holder is shared, not captured: "
                + shared.stream().map(Supplier::get).toList());
    }
}
