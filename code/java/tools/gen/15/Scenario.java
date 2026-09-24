import java.util.List;

public class Scenario {

    static int expensiveCalls = 0;

    static String expensive(String id) {
        expensiveCalls++;
        return id.toUpperCase();
    }

    public static void main(String[] args) {
        List<String> ids = List.of("a1", "b2", "a3", "b4", "a5", "b6");

        expensiveCalls = 0;
        List<String> late = ids.stream()
                .map(Scenario::expensive)
                .filter(id -> id.startsWith("A"))
                .toList();
        int lateCalls = expensiveCalls;

        expensiveCalls = 0;
        List<String> early = ids.stream()
                .filter(id -> id.startsWith("a"))
                .map(Scenario::expensive)
                .toList();
        int earlyCalls = expensiveCalls;

        System.out.println("rows: " + ids.size());
        System.out.println("both give " + early + ": " + late.equals(early));
        System.out.println("map before filter called the work " + lateCalls + " times");
        System.out.println("filter before map called the work " + earlyCalls + " times");
        System.out.println("calls saved: " + (lateCalls - earlyCalls));
    }
}
