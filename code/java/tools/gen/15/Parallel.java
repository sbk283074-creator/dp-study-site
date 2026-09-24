import java.util.List;
import java.util.stream.IntStream;

public class Parallel {

    public static void main(String[] args) {
        List<Integer> numbers = IntStream.rangeClosed(1, 20).boxed().toList();

        System.out.println("sequential count: "
                + numbers.stream().filter(n -> n % 3 == 0).count());
        System.out.println("parallel count:   "
                + numbers.parallelStream().filter(n -> n % 3 == 0).count());

        System.out.println("the two agree: "
                + (numbers.stream().mapToInt(Integer::intValue).sum()
                   == numbers.parallelStream().mapToInt(Integer::intValue).sum()));

        System.out.println("an ordered source keeps its order: "
                + numbers.parallelStream().limit(3).toList());
        System.out.println("even when the work is split across threads");
    }
}
