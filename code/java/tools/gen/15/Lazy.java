import java.util.List;

public class Lazy {

    static int calls = 0;

    static int doubleIt(int n) {
        calls++;
        return n * 2;
    }

    public static void main(String[] args) {
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);

        calls = 0;
        List<Integer> all = numbers.stream().map(Lazy::doubleIt).toList();
        System.out.println("collecting everything mapped " + calls + " of " + numbers.size());

        calls = 0;
        List<Integer> firstTwo = numbers.stream().map(Lazy::doubleIt)
                .filter(n -> n > 4).limit(2).toList();
        System.out.println("asking for two stopped after " + calls
                + " of " + numbers.size() + ": " + firstTwo);

        calls = 0;
        numbers.stream().map(Lazy::doubleIt);
        System.out.println("no terminal operation ran map " + calls + " times");
    }
}
